import re

with open('frontend/js/ui/draft.js', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(
    '<img src="${photoUrl}" class="fut-card-large-face" onerror="this.src=\\\'https://cdn.sofifa.net/players/notfound_0_120.png\\\'" alt="Face">',
    '<img src="${photoUrl}" class="fut-card-large-face" referrerpolicy="no-referrer" onerror="this.onerror=null; this.src=\\\'../img/placeholder_player.png\\\';" alt="Face">'
)

content = content.replace(
    '<img src="${photoUrl}" class="fut-card-face" onerror="this.src=\\\'https://cdn.sofifa.net/players/notfound_0_120.png\\\'">',
    '<img src="${photoUrl}" class="fut-card-face" referrerpolicy="no-referrer" onerror="this.onerror=null; this.src=\\\'../img/placeholder_player.png\\\';">'
)

with open('frontend/js/ui/draft.js', 'w', encoding='utf-8') as f:
    f.write(content)
print("Fixed images in ui/draft.js")
