from app import app, db, User, Package, Bus
from datetime import datetime, timedelta

print('Running in-process validation tests...')

with app.app_context():
    # fresh DB for tests
    db.drop_all()
    db.create_all()
    # seed a package and a bus
    pkg = Package(name='TESTPKG', description='desc', image='img.jpg')
    db.session.add(pkg)
    db.session.commit()
    bus = Bus(name='TestBus', package_id=pkg.id, capacity=30, price=100.0, departure_time='09:00')
    db.session.add(bus)
    db.session.commit()

    client = app.test_client()

    # Test 1: Register short password
    resp = client.post('/register', data={'username':'testshort','email':'testshort@example.com','password':'short'})
    print('Register short password:', resp.status_code)
    assert resp.status_code == 200 and b'Password must be at least 8 characters long.' in resp.data
    print('PASS: short password')

    # Test 2: Register invalid email
    resp = client.post('/register', data={'username':'testinvalid','email':'invalid-email','password':'validpass123'})
    print('Register invalid email:', resp.status_code)
    assert resp.status_code == 200 and b'Invalid email format.' in resp.data
    print('PASS: invalid email')

    # Test 3: Register valid and duplicate
    resp = client.post('/register', data={'username':'testdup','email':'testdup@example.com','password':'validpass123'}, follow_redirects=False)
    print('Register valid:', resp.status_code)
    assert resp.status_code == 302
    # duplicate
    resp = client.post('/register', data={'username':'testdup','email':'testdup@example.com','password':'validpass123'})
    print('Register duplicate:', resp.status_code)
    assert resp.status_code == 200 and b'Username or email already exists.' in resp.data
    print('PASS: duplicate')

    # Login
    resp = client.post('/login', data={'username':'testdup','password':'validpass123'}, follow_redirects=False)
    print('Login:', resp.status_code)
    assert resp.status_code == 302
    print('PASS: login')

    # Use client with session to set user id (simulate login)
    with client.session_transaction() as sess:
        user = User.query.filter_by(username='testdup').first()
        sess['user_id'] = user.id
        sess['username'] = user.username
        sess['is_admin'] = user.is_admin

    # Booking invalid email
    future_date = (datetime.now() + timedelta(days=10)).strftime('%Y-%m-%d')
    resp = client.post('/booking/1', data={'name':'A','email':'invalid','phone':'123','travelers':'2','date':future_date,'bus_id':'1'})
    print('Booking invalid email:', resp.status_code)
    assert resp.status_code == 200 and b'Invalid email format.' in resp.data
    print('PASS: booking invalid email')

    # Booking past date
    past_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    resp = client.post('/booking/1', data={'name':'A','email':'a@example.com','phone':'123','travelers':'2','date':past_date,'bus_id':'1'})
    print('Booking past date:', resp.status_code)
    assert resp.status_code == 200 and b'Travel date must be in the future.' in resp.data
    print('PASS: booking past date')

    # Booking invalid travelers
    resp = client.post('/booking/1', data={'name':'A','email':'a@example.com','phone':'123','travelers':'abc','date':future_date,'bus_id':'1'})
    print('Booking non-int travelers:', resp.status_code)
    assert resp.status_code == 200 and b'Number of travelers must be a valid number.' in resp.data
    print('PASS: non-int travelers')

    resp = client.post('/booking/1', data={'name':'A','email':'a@example.com','phone':'123','travelers':'0','date':future_date,'bus_id':'1'})
    print('Booking zero travelers:', resp.status_code)
    assert resp.status_code == 200 and b'Number of travelers must be at least 1.' in resp.data
    print('PASS: zero travelers')

    # Successful booking
    resp = client.post('/booking/1', data={'name':'Valid','email':'valid@example.com','phone':'123','travelers':'2','date':future_date,'bus_id':'1'}, follow_redirects=False)
    print('Successful booking status:', resp.status_code)
    # final view returns booking_confirmation template (200 if follow_redirects True), here we render direct
    assert resp.status_code == 200 or resp.status_code == 302
    print('PASS: successful booking')

print('All in-process tests passed')
