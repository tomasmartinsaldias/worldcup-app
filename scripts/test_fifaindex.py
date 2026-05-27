import requests
from bs4 import BeautifulSoup
import urllib.parse

def test_fifaindex(name):
    url = f"https://www.fifaindex.com/players/?name={urllib.parse.quote(name)}"
    headers = {"User-Agent": "Mozilla/5.0"}
    resp = requests.get(url, headers=headers)
    soup = BeautifulSoup(resp.text, 'html.parser')
    
    # FifaIndex uses <span class="link-position">RW</span>
    pos_span = soup.find('span', class_='link-position')
    if pos_span:
        print(f"Found {name}: {pos_span.text.strip()}")
    else:
        print(f"Not found {name}")

test_fifaindex('Lamine Yamal')
test_fifaindex('Kylian Mbappé')
test_fifaindex('Dani Olmo')
