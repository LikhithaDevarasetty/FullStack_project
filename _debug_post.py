import requests
s = requests.Session()
resp = s.post('http://127.0.0.1:5000/register', data={'username':'debuguser','email':'debuguser@example.com','password':'validpass123'}, allow_redirects=False)
print('Status:', resp.status_code)
print('Location header:', resp.headers.get('Location'))
print('Body snippet:\n', resp.text[:1200])
                   