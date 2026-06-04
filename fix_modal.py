import re

with open('frontend/js/ui/draft.js', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(
    "modal.classList.add('active');",
    "modal.classList.add('active');\n  modal.classList.remove('hidden');"
)

content = content.replace(
    "document.getElementById('draft-modal').classList.remove('active');",
    "document.getElementById('draft-modal').classList.remove('active');\n      document.getElementById('draft-modal').classList.add('hidden');"
)

with open('frontend/js/ui/draft.js', 'w', encoding='utf-8') as f:
    f.write(content)
print("Fixed modal visibility")
