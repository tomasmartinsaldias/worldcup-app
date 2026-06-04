import re

with open('/Users/franmonti/Documents/Austral/worldcup-app/frontend/js/draft.js', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace("\\`", "`").replace("\\$", "$")

with open('/Users/franmonti/Documents/Austral/worldcup-app/frontend/js/draft.js', 'w', encoding='utf-8') as f:
    f.write(content)
print("Fixed draft.js syntax")
