import requests
resp = requests.get('https://restcountries.com/v3.1/name/Argentina')
print(resp.json()[0]['flags']['png'])
