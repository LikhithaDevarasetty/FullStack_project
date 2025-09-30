import requests
import time
import random
import string

BASE='http://127.0.0.1:5000'
s = requests.Session()
# helper to make unique strings
def uid(n=6):
    return ''.join(random.choices(string.ascii_lowercase+string.digits,k=n))

username = 'smoke_'+uid()
email = username+'@example.com'
password = 'smokepass123'

print('Registering', username, email)
r = s.post(BASE+'/register', data={'username':username,'email':email,'password':password})
print('register status', r.status_code)
if r.status_code not in (200,302):
    print('Register failed')
    raise SystemExit(1)

# login (the app redirects to / after login)
r = s.post(BASE+'/login', data={'username':email,'password':password})
print('login status', r.status_code)
if r.status_code not in (200,302):
    print('Login failed')
    raise SystemExit(1)

# find a package with at least one bus by visiting /packages then the booking page
r = s.get(BASE+'/packages')
print('/packages', r.status_code)
if r.status_code!=200:
    raise SystemExit(1)
html = r.text
# find first occurrence of /destination_detail/<id> in hrefs
import re
match = re.search(r'href=["\']([^"\']*/destination_detail/(\d+))', html)
if not match:
    # fallback: search for the path fragment and extract digits after it
    match2 = re.search(r'/destination_detail/(\d+)', html)
    if not match2:
        print('No destination_detail link found on /packages')
        raise SystemExit(1)
    pid = int(match2.group(1))
else:
    pid = int(match.group(2))
print('Using package id', pid)

# visit booking page to fetch bus selection
r = s.get(BASE+f'/booking/{pid}')
print('/booking page', r.status_code)
if r.status_code!=200:
    raise SystemExit(1)

html = r.text
# extract first <option value="..."> from the booking page
opt = re.search(r'<select[^>]*name=["\']bus_id["\'][^>]*>(.*?)</select>', html, re.S)
if not opt:
    print('No bus select on booking page; cannot proceed')
    raise SystemExit(1)
opts_html = opt.group(1)
optval = re.search(r'<option[^>]*value=["\'](\d+)["\']', opts_html)
if not optval:
    print('No bus option available')
    raise SystemExit(1)
bus_id = optval.group(1)
print('Found bus_id', bus_id)

# prepare booking data
from datetime import datetime, timedelta
future = (datetime.now()+timedelta(days=10)).strftime('%Y-%m-%d')
booking_data = {
    'name': 'Smoke Tester',
    'email': email,
    'phone': '9999999999',
    'travelers': '2',
    'date': future,
    'bus_id': bus_id
}

r = s.post(BASE+f'/booking/{pid}', data=booking_data)
print('booking POST', r.status_code)
if r.status_code not in (200,302):
    print('booking failed')
    print(r.text[:1000])
    raise SystemExit(1)

# check mybookings
r = s.get(BASE+'/mybookings')
print('/mybookings', r.status_code)
if r.status_code!=200:
    raise SystemExit(1)

if email in r.text or 'Smoke Tester' in r.text:
    print('Booking appears in mybookings — smoke test passed')
else:
    print('Booking not found in mybookings — check server output')
    print(r.text[:1000])
    raise SystemExit(1)
