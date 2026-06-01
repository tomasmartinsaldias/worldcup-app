import urllib.request
import re
import json
import os
import time

countries = [
    'england', 'spain', 'italy', 'germany', 'france', 
    'argentina', 'brazil', 'portugal', 'netherlands', 'belgium',
    'scotland', 'turkey', 'mexico', 'usa', 'greece', 'saudi-arabia', 'qatar', 'uae', 'japan', 'south-korea'
]

logos = {}

for country in countries:
    try:
        req = urllib.request.Request(f'https://football-logos.cc/{country}/', headers={'User-Agent': 'Mozilla/5.0'})
        html = urllib.request.urlopen(req).read().decode('utf-8')
        
        matches = re.findall(r'<img\s+src="(https://images\.football-logos\.cc/[^"]+\.svg)"\s+alt="([^"]+) vector logo"', html)
        for src, name in matches:
            clean_name = name.strip()
            logos[clean_name] = src
            logos[clean_name.lower().replace(' ', '')] = src
            # Add some variations
            logos[clean_name + ' FC'] = src
            logos['FC ' + clean_name] = src
        print(f"Scraped {country}: {len(matches)} logos")
        time.sleep(0.5)
    except Exception as e:
        print(f"Error scraping {country}: {e}")

out_path = os.path.join('frontend', 'data', 'club_logos.json')
os.makedirs(os.path.dirname(out_path), exist_ok=True)
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(logos, f, ensure_ascii=False, indent=2)
print(f"Total extracted: {len(logos)} logos. Saved to {out_path}.")
