import re

with open('frontend/js/landing-main.js', 'r', encoding='utf-8') as f:
    content = f.read()

if "const futDraft = document.getElementById('draft-template');" not in content:
    content = content.replace(
        "      const draft = document.getElementById('draft-overlay');",
        "      const futDraft = document.getElementById('draft-template');\n      if (futDraft) {\n        futDraft.classList.remove('visible');\n        futDraft.classList.add('hidden');\n      }\n\n      const draft = document.getElementById('draft-overlay');"
    )

with open('frontend/js/landing-main.js', 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated landing-main.js")
