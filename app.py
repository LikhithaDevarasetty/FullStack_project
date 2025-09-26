from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import joinedload
import os

app = Flask(__name__)

@app.context_processor
def inject_user():
    if 'user_id' in session:
        return {
            'is_authenticated': True,
            'current_user': {
                'is_admin': session.get('is_admin', False)
            }
        }
    return {
        'is_authenticated': False,
        'current_user': None
    }
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///travel.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

class Package(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(150), nullable=False)
    location = db.Column(db.String(150))
    duration = db.Column(db.String(50))
    best_time = db.Column(db.String(50))
    activities = db.Column(db.Text)
    bookings = db.relationship('Booking', backref='package', lazy=True)

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    package_id = db.Column(db.Integer, db.ForeignKey('package.id'), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    travelers = db.Column(db.Integer, nullable=False)
    date = db.Column(db.String(50), nullable=False)
    user = db.relationship('User', backref='bookings', lazy=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['is_admin'] = user.is_admin
            return redirect(url_for('index'))
        flash('Invalid credentials')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        email = request.form['email'].strip()
        password = request.form['password']
        is_admin = 'is_admin' in request.form

        if not username or not email or not password:
            flash('All fields are required.')
            return render_template('register.html')

        if len(password) < 8:
            flash('Password must be at least 8 characters long.')
            return render_template('register.html')

        import re
        if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
            flash('Invalid email format.')
            return render_template('register.html')

        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            flash('Username or email already exists.')
            return render_template('register.html')

        password_hash = generate_password_hash(password)
        user = User(username=username, email=email, password=password_hash, is_admin=is_admin)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/packages')
def packages():
    packages = Package.query.all()
    return render_template('packages.html', packages=packages)

@app.route('/maps')
def maps():
    return render_template('maps.html')

@app.route('/destination_detail/<int:package_id>')
def destination_detail(package_id):
    package = Package.query.get_or_404(package_id)
    return render_template('destination_detail.html', package=package)

@app.route('/gallery/<int:package_id>')
def gallery(package_id):
    package = Package.query.get_or_404(package_id)
    return render_template('gallery.html', package=package)

@app.route('/booking/<int:package_id>', methods=['GET', 'POST'])
def booking(package_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    package = Package.query.get_or_404(package_id)
    if request.method == 'POST':
        name = request.form['name'].strip()
        email = request.form['email'].strip()
        phone = request.form['phone'].strip()
        travelers = request.form['travelers']
        date = request.form['date']

        if not name or not email or not phone or not travelers or not date:
            flash('All fields are required.')
            return render_template('booking.html', package=package)

        import re
        if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
            flash('Invalid email format.')
            return render_template('booking.html', package=package)

        try:
            from datetime import datetime
            booking_date = datetime.strptime(date, '%Y-%m-%d')
            if booking_date <= datetime.now():
                flash('Travel date must be in the future.')
                return render_template('booking.html', package=package)
        except ValueError:
            flash('Invalid date format. Please use YYYY-MM-DD.')
            return render_template('booking.html', package=package)

        try:
            travelers = int(travelers)
            if travelers < 1:
                flash('Number of travelers must be at least 1.')
                return render_template('booking.html', package=package)
        except ValueError:
            flash('Number of travelers must be a valid number.')
            return render_template('booking.html', package=package)

        booking = Booking(
            user_id=session['user_id'],
            package_id=package_id,
            name=name,
            email=email,
            phone=phone,
            travelers=travelers,
            date=date
        )
        db.session.add(booking)
        db.session.commit()
        return render_template('booking_confirmation.html', booking=booking, package=package)
    return render_template('booking.html', package=package)

@app.route('/mybookings')
def mybookings():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    bookings = Booking.query.filter_by(user_id=session['user_id']).options(joinedload(Booking.package)).all()
    return render_template('mybookings.html', bookings=bookings)

@app.route('/cancel_booking/<int:booking_id>')
def cancel_booking(booking_id):
    if 'user_id' not in session:
        flash('Please log in to cancel bookings.')
        return redirect(url_for('login'))
    
    booking = Booking.query.get_or_404(booking_id)
    if booking.user_id != session['user_id']:
        flash('You can only cancel your own bookings.')
        return redirect(url_for('mybookings'))
    
    db.session.delete(booking)
    db.session.commit()
    flash('Booking cancelled successfully.')
    return redirect(url_for('mybookings'))

@app.route('/admin')
def admin():
    if 'is_admin' not in session or not session['is_admin']:
        return redirect(url_for('login'))
    bookings = Booking.query.options(joinedload(Booking.package), joinedload(Booking.user)).all()
    return render_template('admin.html', bookings=bookings)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.drop_all()
        db.create_all()
        # Seed sample packages if not exist
        packages_data = [
            {'name': 'GOA', 'description': 'Goa, located on the western coast of India, is a vibrant and enchanting destination known for its beautiful beaches, rich cultural heritage, and lively atmosphere. With a unique blend of Indian and Portuguese influences, Goa offers a diverse and captivating experience to its visitors.\n\nCalangute Beach: Known as the "Queen of Beaches," Calangute Beach is one of the most famous and busiest beaches in Goa. It offers a wide stretch of golden sand, water sports activities, beach shacks, and vibrant nightlife.\n\nOld Goa: Explore the historical charm of Old Goa, a UNESCO World Heritage Site. Visit the Basilica of Bom Jesus, which houses the mortal remains of St. Francis Xavier, and the Se Cathedral, one of the largest churches in Asia. Don\'t miss the Church of St. Cajetan and the Archaeological Museum.\n\nDudhsagar Falls: Located on the Mandovi River, Dudhsagar Falls is one of India\'s tallest waterfalls. Its milky white cascades amidst lush green surroundings make for a breathtaking sight. You can reach the falls by a trek, jeep safari, or a train ride.\n\nPanaji: The capital city of Goa, Panaji, or Panjim, is known for its charming Portuguese architecture and scenic beauty. Explore the narrow streets of Fontainhas, the Latin Quarter of Panaji, and visit the iconic Our Lady of the Immaculate Conception Church. Enjoy a leisurely stroll along the Mandovi River promenade and indulge in local cuisine.\n\nAnjuna Flea Market: Visit the famous Anjuna Flea Market, held every Wednesday, to experience the vibrant and bohemian side of Goa. It offers a variety of items like clothing, jewelry, handicrafts, and souvenirs. Enjoy live music performances and indulge in delicious street food.\n\nFort Aguada: Explore the historic Fort Aguada, built by the Portuguese in the 17th century. It offers panoramic views of the Arabian Sea and the Mandovi River. The fort also houses a lighthouse and a jail, which is now a part of the Central Jail Aguada.\n\nRemember, Goa has numerous beaches, each with its unique charm and character. It\'s worth exploring different parts of the coastline to discover hidden gems and enjoy the coastal beauty that the state has to offer.', 'image': 'destination1.jpg', 'location': 'India, South-West', 'duration': '4-7 days', 'best_time': 'November-February', 'activities': 'Water Sports: Goa is known for its thrilling water sports activities. You can indulge in a variety of options like parasailing, jet skiing, banana boat rides, kayaking, snorkeling, and scuba diving.||River Cruises: Goa is blessed with several scenic rivers, and taking a river cruise is a fantastic way to explore the backwaters and enjoy the natural beauty of the region.'},
            {'name': 'MANALI', 'description': 'Manali, nestled in the picturesque mountains of Himachal Pradesh in northern India, is a popular hill station and a haven for nature lovers and adventure enthusiasts. Known for its breathtaking landscapes, snow-capped peaks, and serene valleys, Manali offers a refreshing escape from the bustling city life.\n\nRohtang Pass: Situated at an altitude of 3,978 meters (13,050 feet), Rohtang Pass is a must-visit destination near Manali. It offers stunning panoramic views of the surrounding mountains, glaciers, and valleys. The pass is also famous for adventure activities like snowboarding and skiing (available during the winter months).\n\nSolang Valley: Located about 13 kilometers from Manali, Solang Valley is a picturesque destination known for its adventure sports. Enjoy activities like paragliding, zorbing, cable car rides, and skiing (during winter). The valley\'s scenic beauty and snow-capped peaks make it a popular spot for nature lovers and thrill-seekers alike.\n\nHadimba Devi Temple: Dedicated to Goddess Hadimba, this ancient wooden temple is a significant religious site in Manali. Surrounded by lush greenery, the temple showcases unique architecture and is a peaceful place to visit.\n\nOld Manali: Take a stroll through the narrow lanes of Old Manali to experience its bohemian charm. The area is dotted with quaint cafes, shops selling handicrafts and local products, and guesthouses. Enjoy the laid-back vibe and soak in the beautiful surroundings.\n\nManikaran: Located about 80 kilometers from Manali, Manikaran is famous for its hot springs and religious significance. Visit the Gurudwara Manikaran Sahib and the Ram Temple, and take a dip in the hot springs believed to have therapeutic properties.\n\nNaggar Castle: Visit the historic Naggar Castle, situated on a hilltop overlooking the Kullu Valley. This ancient castle has now been converted into a heritage hotel and museum. Explore its architectural beauty, art galleries, and enjoy the panoramic views of the surrounding mountains.\n\nThe region is also blessed with beautiful valleys, waterfalls, and trekking trails, making it a paradise for nature lovers and adventure seekers.', 'image': 'destination2.jpg', 'location': 'India, North', 'duration': '5-7 days', 'best_time': 'April-June', 'activities': 'Trekking: Some popular treks in Manali include the Beas Kund Trek, Hampta Pass Trek, Bhrigu Lake Trek, and Chandrakhani Pass Trek.||River Rafting: The river has stretches suitable for both beginners and experts, making it a popular activity for adventure seekers.'},
            {'name': 'OOTY', 'description': 'Ooty, also known as Udhagamandalam, is a picturesque hill station located in the Nilgiri Hills of Tamil Nadu, India. With its pleasant climate, lush greenery, and scenic landscapes, Ooty has become a popular tourist destination.\n\nOoty Lake: The Ooty Lake is a popular tourist spot where you can enjoy boating and take a leisurely walk around the lake. It offers serene surroundings and scenic views, making it a perfect place to unwind.\n\nBotanical Gardens: The Government Botanical Gardens in Ooty is a must-visit attraction. Spread over 55 acres, it features a wide variety of exotic plants, flowers, and trees. Don\'t miss the fossilized tree trunk that is estimated to be over 20 million years old.\n\nDoddabetta Peak: Located at an altitude of 2,637 meters (8,650 feet), Doddabetta Peak is the highest point in the Nilgiri Hills. Enjoy panoramic views of the surrounding hills, valleys, and tea estates from the observation tower at the top.\n\nTea Gardens: Ooty is famous for its sprawling tea estates. Take a stroll through the tea gardens, learn about the tea-making process, and enjoy the scenic beauty. Many estates also offer guided tours and tea tasting experiences.\n\nRose Garden: Ooty\'s Rose Garden is home to thousands of varieties of roses. With beautifully landscaped gardens and a vast collection of roses, it is a treat for nature lovers and photography enthusiasts.\n\nPykara Falls and Lake: Located about 20 kilometers from Ooty, Pykara offers scenic beauty with its cascading waterfalls and a serene lake. Enjoy a boat ride on the Pykara Lake and visit the Pykara Falls for a refreshing experience.\n\nNilgiri Mountain Railway: Experience the charm of the Nilgiri Mountain Railway, a UNESCO World Heritage Site. Take a toy train ride from Ooty to Coonoor, passing through tunnels, bridges, and breathtaking landscapes.\n\nThese attractions offer a mix of natural beauty, cultural experiences, and historical significance, allowing you to explore and enjoy the best of what Ooty and its surroundings have to offer.', 'image': 'destination3.jpg', 'location': 'India, Tamil Nadu', 'duration': '3-4 days', 'best_time': 'October - June', 'activities': 'Toy Train Ride: Experience the scenic beauty of the Nilgiri Mountains by taking a ride on the Nilgiri Mountain Railway, also known as the Toy Train.||Trekking and Nature Walks: You can embark on trails that take you through tea estates, forests, and hillsides, offering stunning views and a chance to connect with nature.'},
            {'name': 'KERALA', 'description': 'Kerala, often referred to as "God\'s Own Country," offers a diverse range of experiences from backwaters to hill stations. It is famous for its serene backwaters, lush green landscapes, and Ayurvedic treatments.\n\nAlleppey Backwaters: Cruise through the tranquil backwaters on a houseboat, surrounded by palm-fringed canals.\n\nMunnar Hill Station: Explore tea plantations and misty hills in this picturesque destination.\n\nPeriyar Wildlife Sanctuary: Spot elephants and tigers in this biodiversity hotspot.\n\nKovalam Beach: Relax on golden sands with lighthouse views.\n\nFort Kochi: Discover colonial architecture and Chinese fishing nets.', 'image': 'destination4.jpg', 'location': 'India, South', 'duration': '7-10 days', 'best_time': 'September-March', 'activities': 'Houseboat Cruise: Relax on a houseboat in the backwaters of Alleppey.||Ayurveda: Experience traditional Kerala Ayurveda treatments.'},
            {'name': 'JAIPUR', 'description': 'Jaipur, the Pink City, is renowned for its forts, palaces, and vibrant culture.\n\nAmber Fort: Ride an elephant to this majestic hilltop fort.\n\nCity Palace: Explore the royal residence with museums and courtyards.\n\nHawa Mahal: Admire the Palace of Winds with its honeycomb windows.\n\nJantar Mantar: Visit the astronomical observatory.\n\nJal Mahal: View the Water Palace from the lakeside.', 'image': 'destination5.jpg', 'location': 'India, North', 'duration': '3-5 days', 'best_time': 'October-March', 'activities': 'Elephant Ride: Take an elephant ride to Amber Fort.||Shopping: Explore the vibrant markets for traditional Rajasthani crafts.'},
            {'name': 'LADAKH', 'description': 'Ladakh, the Land of High Passes, offers stunning Himalayan views and adventure.\n\nPangong Lake: Witness the color-changing lake at 4,350m altitude.\n\nNubra Valley: Camel safari in the cold desert.\n\nLeh Palace: Explore the royal residence overlooking the town.\n\nMagnetic Hill: Experience the optical illusion of uphill pull.\n\nThiksey Monastery: Admire the Gompa resembling Potala Palace.', 'image': 'destination6.jpg', 'location': 'India, North', 'duration': '7-10 days', 'best_time': 'June-September', 'activities': 'Motorcycle Tour: Embark on a thrilling motorcycle tour across the rugged terrain.||Monastery Visit: Visit ancient Buddhist monasteries.'},
            {'name': 'ANDAMAN', 'description': 'The Andaman Islands boast pristine beaches, coral reefs, and colonial history.\n\nRadhanagar Beach: Voted Asia\'s best beach for its white sands.\n\nCellular Jail: Tour the historic prison of India\'s freedom struggle.\n\nRoss Island: Explore the ruins of British settlement.\n\nElephant Beach: Snorkel in shallow waters.\n\nBaratang Island: See limestone caves and mud volcanoes.', 'image': 'destination7.jpg', 'location': 'India, East', 'duration': '5-7 days', 'best_time': 'October-May', 'activities': 'Scuba Diving: Explore the underwater world around the islands.||Beach Hopping: Visit Havelock and Neil Islands.'},
            {'name': 'LAKSHADWEEP', 'description': 'Literally meaning a \'hundred thousand islands\', Lakshadweep has few of the most beautiful and exotic islands and beaches of India.\n\nKavaratti Island: Relax on white sandy beaches and visit mosques.\n\nMinicoy Island: Experience lighthouse views and tuna fishing.\n\nAgatti Island: Enjoy water sports and airport access.\n\nBangaram Island: Uninhabited paradise for snorkeling.\n\nKadmat Island: Dive in coral reefs and lagoons.', 'image': 'destination8.jpg', 'location': 'India, South', 'duration': '4-6 days', 'best_time': 'October-May', 'activities': 'Snorkeling: Snorkel in the clear lagoons.||Island Hopping: Visit different atolls.'},
            {'name': 'COORG', 'description': 'Located amidst imposing mountains in Karnataka with a perpetually misty landscape, Coorg is the place to be for all nature lovers. This popular coffee producing hill station is not only popular for its beautiful green hills and the streams cutting right through them.\n\nAbbey Falls: Admire the cascading waterfall amidst coffee plantations.\n\nRaja\'s Seat: Enjoy sunset views from this garden viewpoint.\n\nNisargadhama: Walk through bamboo forests on a river island.\n\nIruppu Falls: Trek to this sacred waterfall in Brahmagiri hills.\n\nDubare Elephant Camp: Interact with elephants and raft on the river.', 'image': 'destination9.jpg', 'location': 'India, South', 'duration': '3-5 days', 'best_time': 'October-March', 'activities': 'Coffee Plantation Tour: Tour the famous coffee estates.||Waterfalls: Visit Abbey Falls and Iruppu Falls.'},
            {'name': 'NEPAL', 'description': 'A hub for the adventure-lovers and home to Mt. Everest, the world\'s tallest peak, Nepal is a Himalayan country sandwiched between India and China. The mighty snow-capped mountains here such as Annapurna, Mount Everest, Manaslu, and Kanchenjunga.\n\nKathmandu: Explore ancient temples and Durbar Square.\n\nPokhara: Boating on Phewa Lake with Annapurna views.\n\nChitwan National Park: Safari for rhinos and tigers.\n\nBhaktapur: Medieval city with pottery and architecture.\n\nLumbini: Birthplace of Buddha, a UNESCO site.', 'image': 'destination10.jpg', 'location': 'Nepal', 'duration': '7-14 days', 'best_time': 'March-May, September-November', 'activities': 'Trekking: Trek to Everest Base Camp.||Rafting: White water rafting in the rivers.'},
            {'name': 'BHUTAN', 'description': 'The ‘Land of the Thunder Dragon’ – Bhutan nestles in the mountainous regions of the Eastern Himalayas and is one of the cleanest countries in the South Asian region.\n\nParo Taktsang (Tiger\'s Nest): Hike to this iconic cliffside monastery.\n\nPunakha Dzong: Visit the beautiful fortress at river confluence.\n\nThimphu: Explore the capital with Buddha Dordenma statue.\n\nWangdue Phodrang: See the reconstructed dzong and local crafts.\n\nTrongsa Dzong: Admire the largest fortress in Bhutan.', 'image': 'destination11.jpg', 'location': 'Bhutan', 'duration': '5-7 days', 'best_time': 'March-May, September-November', 'activities': 'Hiking: Hike to Tiger\'s Nest Monastery.||Cultural Tour: Explore ancient dzongs.'},
            {'name': 'AMRITSAR', 'description': 'Home of the glorious Golden Temple, the iconic city of Amritsar, portrays the heroic character of the Punjab. A day in this peaceful city starts with the spiritual prayers from Gurudwaras.\n\nGolden Temple: Visit the holiest Sikh shrine at dawn.\n\nJallianwala Bagh: Memorial for the 1919 massacre victims.\n\nWagah Border: Witness the Indo-Pak border ceremony.\n\nPartition Museum: Learn about the 1947 partition history.\n\nDurgiana Temple: Explore this Hindu temple resembling Golden Temple.', 'image': 'destination12.jpeg', 'location': 'India, North', 'duration': '2-3 days', 'best_time': 'October-March', 'activities': 'Wagah Border Ceremony: Attend the Beating Retreat ceremony.||Langar: Participate in the community kitchen at Golden Temple.'}
        ]
        for p in packages_data:
            if not Package.query.filter_by(name=p['name']).first():
                package = Package(**p)
                db.session.add(package)
        db.session.commit()
    app.run(debug=True)
