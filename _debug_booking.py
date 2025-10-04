import requests
from datetime import datetime, timedelta
s = requests.Session()
# login
s.post('http://127.0.0.1:5000/login', data={'username':'debuguser','password':'validpass123'})
# Attempt booking with invalid email
resp = s.post('http://127.0.0.1:5000/booking/1', data={
    'name':'Test User','email':'invalid-email','phone':'1234567890','travelers':'2','date':(datetime.now()+timedelta(days=10)).strftime('%Y-%m-%d'),'bus_id':'1'
}, allow_redirects=False)
print('Status:', resp.status_code)
print('Headers:', resp.headers)
print('Body:\n', resp.text[:4000])
