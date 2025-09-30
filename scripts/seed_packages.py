import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app, db, Package, Bus

packages_data = [
    {'name': 'GOA', 'description': 'Goa, located on the western coast of India, is a vibrant and enchanting destination known for its beautiful beaches, rich cultural heritage, and lively atmosphere.', 'image': 'destination1.jpg', 'location': 'India, South-West', 'duration': '4-7 days', 'best_time': 'November-February', 'activities': 'Water Sports: Enjoy water sports||River Cruises: River cruises available'},
    {'name': 'MANALI', 'description': 'Manali, nestled in the picturesque mountains of Himachal Pradesh.', 'image': 'destination2.jpg', 'location': 'India, North', 'duration': '5-7 days', 'best_time': 'April-June', 'activities': 'Trekking: Several treks available||River Rafting: For thrill seekers'},
    {'name': 'OOTY', 'description': 'Ooty, also known as Udhagamandalam, is a picturesque hill station.', 'image': 'destination3.jpg', 'location': 'India, Tamil Nadu', 'duration': '3-4 days', 'best_time': 'October - June', 'activities': 'Toy Train Ride: Scenic ride||Gardens: Botanical Gardens'},
    {'name': 'KERALA', 'description': 'Kerala, often referred to as "God\'s Own Country".', 'image': 'destination4.jpg', 'location': 'India, South', 'duration': '7-10 days', 'best_time': 'September-March', 'activities': 'Houseboat Cruise: Relax on a houseboat||Ayurveda: Experience treatments'},
    {'name': 'JAIPUR', 'description': 'Jaipur, the Pink City, is renowned for its forts and palaces.', 'image': 'destination5.jpg', 'location': 'India, North', 'duration': '3-5 days', 'best_time': 'October-March', 'activities': 'Fort Visits: Historic forts||Shopping: Traditional crafts'},
    {'name': 'LADAKH', 'description': 'Ladakh, the Land of High Passes.', 'image': 'destination6.jpg', 'location': 'India, North', 'duration': '7-10 days', 'best_time': 'June-September', 'activities': 'Monasteries: Visit Gompas||High Passes: Scenic drives'},
    {'name': 'ANDAMAN', 'description': 'Andaman & Nicobar Islands with pristine beaches and coral reefs.', 'image': 'destination7.jpg', 'location': 'India, East', 'duration': '5-7 days', 'best_time': 'October-May', 'activities': 'Scuba Diving: World-class diving||Island Hopping: Visit islands'},
    {'name': 'LAKSHADWEEP', 'description': 'Lakshadweep has beautiful islands and beaches.', 'image': 'destination8.jpg', 'location': 'India, South', 'duration': '4-6 days', 'best_time': 'October-May', 'activities': 'Snorkeling: Explore reefs||Island Hopping: Visit atolls'},
    {'name': 'COORG', 'description': 'Coorg is a nature lover\'s paradise.', 'image': 'destination9.jpg', 'location': 'India, South', 'duration': '3-5 days', 'best_time': 'October-March', 'activities': 'Coffee Tours: Plantation tours||Waterfalls: Visit Abbey Falls'},
    {'name': 'NEPAL', 'description': 'Nepal, a hub for adventure and trekking.', 'image': 'destination10.jpg', 'location': 'Nepal', 'duration': '7-14 days', 'best_time': 'March-May, September-November', 'activities': 'Trekking: Everest region||Rafting: White water rafting'},
    {'name': 'BHUTAN', 'description': 'Bhutan, the Land of the Thunder Dragon.', 'image': 'destination11.jpg', 'location': 'Bhutan', 'duration': '5-7 days', 'best_time': 'March-May, September-November', 'activities': 'Hiking: Tiger\'s Nest||Cultural Tours: Dzongs and monasteries'},
    {'name': 'AMRITSAR', 'description': 'Amritsar, home of the Golden Temple.', 'image': 'destination12.jpeg', 'location': 'India, North', 'duration': '2-3 days', 'best_time': 'October-March', 'activities': 'Temple Visits: Golden Temple||History: Jallianwala Bagh'}
]

with app.app_context():
    created = 0
    for p in packages_data:
        if not Package.query.filter_by(name=p['name']).first():
            package = Package(**p)
            db.session.add(package)
            db.session.commit()
            created += 1
            # seed a few buses for the package
            buses_data = [
                {'name': f"{package.name} Express 1", 'capacity': 50, 'price': 1000.0, 'departure_time': '08:00 AM'},
                {'name': f"{package.name} Deluxe 2", 'capacity': 40, 'price': 1200.0, 'departure_time': '10:00 AM'}
            ]
            for b in buses_data:
                bus = Bus(package_id=package.id, **b)
                db.session.add(bus)
            db.session.commit()
    print(f"Created {created} new packages")
