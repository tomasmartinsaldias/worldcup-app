import re

with open('/Users/franmonti/Documents/Austral/worldcup-app/frontend/js/landing-quiz.js', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace("    }\n    }\n\n    // --- LÓGICA FANÁTICO ---", "    }\n\n    // --- LÓGICA FANÁTICO ---")

with open('/Users/franmonti/Documents/Austral/worldcup-app/frontend/js/landing-quiz.js', 'w', encoding='utf-8') as f:
    f.write(content)
print("Syntax fixed")
