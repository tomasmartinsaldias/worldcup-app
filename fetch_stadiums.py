import json
import urllib.request
import urllib.parse
import time

stadiums = ['BC Place', 'AT&T Stadium', 'Estadio BBVA', 'Hard Rock Stadium', 'SoFi Stadium', 'MetLife Stadium', 'Lumen Field', 'Arrowhead Stadium', 'Estadio Azteca', 'Lincoln Financial Field', 'Estadio Akron', 'BMO Field', 'NRG Stadium', 'Mercedes-Benz Stadium', 'Gillette Stadium', "Levi's Stadium"]

mapping = {}
headers = {'User-Agent': 'WorldCupApp/1.0 (test@example.com)'}

for st in stadiums:
    query = urllib.parse.quote(st)
    url = f"https://en.wikipedia.org/w/api.php?action=query&titles={query}&prop=pageimages&format=json&pithumbsize=800"
    
    req = urllib.request.Request(url, headers=headers)
    try:
        res = urllib.request.urlopen(req)
        data = json.loads(res.read())
        pages = data['query']['pages']
        page_id = list(pages.keys())[0]
        if page_id != '-1' and 'thumbnail' in pages[page_id]:
            mapping[st] = pages[page_id]['thumbnail']['source']
        else:
            mapping[st] = 'https://images.unsplash.com/photo-1522778119026-d647f0596c20?q=80&w=600&auto=format&fit=crop'
    except Exception as e:
        print(f"Failed for {st}: {e}")
        mapping[st] = 'https://images.unsplash.com/photo-1522778119026-d647f0596c20?q=80&w=600&auto=format&fit=crop'
    time.sleep(0.5)

print("const STADIUM_IMAGES = {")
for k, v in mapping.items():
    print(f'  "{k}": "{v}",')
print("};")
