import re

with open('frontend/js/ui/draft.js', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(
    "modal.classList.remove('hidden');",
    "modal.classList.remove('hidden');\n  modal.classList.add('visible');"
)

content = content.replace(
    "document.getElementById('draft-modal').classList.add('hidden');",
    "document.getElementById('draft-modal').classList.add('hidden');\n      document.getElementById('draft-modal').classList.remove('visible');"
)

with open('frontend/js/ui/draft.js', 'w', encoding='utf-8') as f:
    f.write(content)
print("Fixed modal visible class")
