
with open('frontend/js/state.js', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace("fetch(`data/", "fetch(`../data/")

with open('frontend/js/state.js', 'w', encoding='utf-8') as f:
    f.write(content)
print("Fixed fetch paths in state.js")
