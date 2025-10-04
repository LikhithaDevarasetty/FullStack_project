import requests
r=requests.get('http://127.0.0.1:5000/destination_detail/2')
print('/destination_detail/2', r.status_code, 'len', len(r.text))
needle='id="carousel-caption"'
print('has caption id?', needle in r.text)
i=r.text.find(needle)
print(r.text[i-120:i+120].replace('\n',' '))
