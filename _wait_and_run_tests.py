import requests
import time

url = 'http://127.0.0.1:5000/'
for i in range(20):
    try:
        r = requests.get(url, timeout=2)
        print('Server up, status:', r.status_code)
        break
    except Exception as e:
        print('Waiting for server...', i)
        time.sleep(1)
else:
    print('Server did not start in time')
    raise SystemExit(1)


import subprocess
subprocess.run(['python', 'test_validations.py'])
