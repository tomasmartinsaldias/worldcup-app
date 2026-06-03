import re

html = open('spain.html', encoding='utf-8').read()

# Try a very loose regex to capture images
matches = re.findall(r'<img\s+src="(https://images\.football-logos\.cc/[^"]+\.svg)"', html)
print("Found SVG images:", len(matches))
print(matches[:5])

# Also let's try to capture the team name
# Look for: "name":"FC Barcelona" or alt="FC Barcelona"
matches_alt = re.findall(r'<img\s+src="(https://images\.football-logos\.cc/[^"]+\.svg)"[^>]*alt="([^"]+)"', html)
print("Found SVG with alt:", len(matches_alt))
print(matches_alt[:5])

# The site uses structured JSON-LD or something. 
# "name":"FC Barcelona"
names = re.findall(r'"name":"([^"]+)"', html)
print("Names found:", len(names))
print(names[:20])
