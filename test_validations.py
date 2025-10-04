import requests
from datetime import datetime, timedelta

# Base URL
base_url = 'http://localhost:5000'

# Session to maintain cookies
session = requests.Session()

# Test 1: Register with short password (should fail server-side, but client blocks; here we test direct POST)
def test_register_short_password():
    data = {
        'username': 'testshort',
        'email': 'testshort@example.com',
        'password': 'short'  # 5 chars <8
    }
    r = session.post(f'{base_url}/register', data=data)
    print(f"Register short password: Status {r.status_code}")
    if r.status_code == 200 and 'Password must be at least 8 characters long.' in r.text:
        print("PASS: Server-side password validation works")
    else:
        print("FAIL: Expected flash error for short password")

# Test 2: Register with invalid email (client blocks, but test server)
def test_register_invalid_email():
    data = {
        'username': 'testinvalidemail',
        'email': 'invalid-email',  # No @
        'password': 'validpass123'
    }
    r = session.post(f'{base_url}/register', data=data)
    print(f"Register invalid email: Status {r.status_code}")
    if r.status_code == 200 and 'Invalid email format.' in r.text:
        print("PASS: Server-side email validation works")
    else:
        print("FAIL: Expected flash error for invalid email")

# Test 3: Register duplicate (after successful register)
def test_register_duplicate():
    # First, register a valid user
    data_valid = {
        'username': 'testdup',
        'email': 'testdup@example.com',
        'password': 'validpass123'
    }
    r_valid = session.post(f'{base_url}/register', data=data_valid, allow_redirects=False)
    # Registration endpoint redirects to /login on success (302)
    if r_valid.status_code == 302:
        # Now try duplicate
        r_dup = session.post(f'{base_url}/register', data=data_valid)
        print(f"Register duplicate: Status {r_dup.status_code}")
        if r_dup.status_code == 200 and 'Username or email already exists.' in r_dup.text:
            print("PASS: Duplicate validation works")
        else:
            print("FAIL: Expected duplicate error")
    else:
        print("FAIL: Could not register valid user for duplicate test")

# Test 4: Login with valid user
def test_login():
    data = {
        'username': 'testdup',
        'password': 'validpass123'
    }
    # Login endpoint redirects to index on success; don't follow redirects so we can assert 302
    r = session.post(f'{base_url}/login', data=data, allow_redirects=False)
    print(f"Login: Status {r.status_code}")
    if r.status_code == 302 and r.headers.get('Location') in ('/', ''):
        print("PASS: Login successful")
        return True
    else:
        print("FAIL: Login failed")
        return False

# Test 5: Booking with invalid email
def test_booking_invalid_email(logged_in):
    if not logged_in:
        return
    data = {
        'name': 'Test User',
        'email': 'invalid-email',
        'phone': '1234567890',
        'travelers': '2',
        'date': '2025-10-01'
    }
    r = session.post(f'{base_url}/booking/1', data=data)
    print(f"Booking invalid email: Status {r.status_code}")
    if r.status_code == 200 and 'Invalid email format.' in r.text:
        print("PASS: Server-side booking email validation works")
    else:
        print("FAIL: Expected flash error for invalid email in booking")

# Test 6: Booking with past date
def test_booking_past_date(logged_in):
    if not logged_in:
        return
    past_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    data = {
        'name': 'Test User',
        'email': 'test@example.com',
        'phone': '1234567890',
        'travelers': '2',
        'date': past_date
    }
    r = session.post(f'{base_url}/booking/1', data=data)
    print(f"Booking past date ({past_date}): Status {r.status_code}")
    if r.status_code == 200 and 'Travel date must be in the future.' in r.text:
        print("PASS: Server-side past date validation works")
    else:
        print("FAIL: Expected flash error for past date")

# Test 7: Booking with invalid date format
def test_booking_invalid_date(logged_in):
    if not logged_in:
        return
    data = {
        'name': 'Test User',
        'email': 'test@example.com',
        'phone': '1234567890',
        'travelers': '2',
        'date': 'invalid-date'
    }
    r = session.post(f'{base_url}/booking/1', data=data)
    print(f"Booking invalid date: Status {r.status_code}")
    if r.status_code == 200 and 'Invalid date format. Please use YYYY-MM-DD.' in r.text:
        print("PASS: Server-side invalid date format works")
    else:
        print("FAIL: Expected flash error for invalid date")

# Test 8: Booking with invalid travelers
def test_booking_invalid_travelers(logged_in):
    if not logged_in:
        return
    # Non-integer
    data_nonint = {
        'name': 'Test User',
        'email': 'test@example.com',
        'phone': '1234567890',
        'travelers': 'abc',
        'date': '2025-10-01'
    }
    r_nonint = session.post(f'{base_url}/booking/1', data=data_nonint)
    print(f"Booking non-int travelers: Status {r_nonint.status_code}")
    if r_nonint.status_code == 200 and 'Number of travelers must be a valid number.' in r_nonint.text:
        print("PASS: Non-integer travelers validation works")

    # Zero travelers
    data_zero = {
        'name': 'Test User',
        'email': 'test@example.com',
        'phone': '1234567890',
        'travelers': '0',
        'date': '2025-10-01'
    }
    r_zero = session.post(f'{base_url}/booking/1', data=data_zero)
    print(f"Booking zero travelers: Status {r_zero.status_code}")
    if r_zero.status_code == 200 and 'Number of travelers must be at least 1.' in r_zero.text:
        print("PASS: Zero travelers validation works")
    else:
        print("FAIL: Expected error for zero travelers")

# Test 9: Successful booking (integration)
def test_successful_booking(logged_in):
    if not logged_in:
        return
    data = {
        'name': 'Valid Test User',
        'email': 'valid@example.com',
        'phone': '1234567890',
        'travelers': '2',
        'date': (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')  # Future
    }
    r = session.post(f'{base_url}/booking/1', data=data)
    print(f"Successful booking: Status {r.status_code}")
    if r.status_code == 200 and 'booking_confirmation' in r.url or 'booking_confirmation.html' in r.text:
        print("PASS: Successful booking creates entry")
    else:
        print("FAIL: Expected success for valid booking")

# Run tests
if __name__ == '__main__':
    print("Running validation tests...")
    test_register_short_password()
    test_register_invalid_email()
    test_register_duplicate()
    logged_in = test_login()
    test_booking_invalid_email(logged_in)
    test_booking_past_date(logged_in)
    test_booking_invalid_date(logged_in)
    test_booking_invalid_travelers(logged_in)
    test_successful_booking(logged_in)
    print("Tests completed.")
