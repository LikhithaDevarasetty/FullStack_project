import requests
s = requests.Session()
resp = s.post('http://127.0.0.1:5000/login', data={'username':'debuguser','password':'validpass123'}, allow_redirects=True)
print('Status:', resp.status_code)
print('Final URL:', resp.url)
print('Body snippet:\n', resp.text[:1200])
