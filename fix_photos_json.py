
with open('frontend/js/state.js', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(
    "const photosData = await photosRes.json();",
    "const photosData = await parseJSON(photosRes) || [];"
)

with open('frontend/js/state.js', 'w', encoding='utf-8') as f:
    f.write(content)
print("Fixed photos JSON parsing")
