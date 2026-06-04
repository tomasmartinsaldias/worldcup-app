
with open('/Users/franmonti/Documents/Austral/worldcup-app/frontend/js/draft.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace <img src="${imgUrl}" alt="${p.NAME}" loading="lazy">
# with <img src="${imgUrl}" alt="${p.NAME}" loading="lazy" referrerpolicy="no-referrer" onerror="this.src='../img/placeholder_player.png'">
content = content.replace(
    'loading="lazy">',
    'loading="lazy" referrerpolicy="no-referrer" onerror="this.onerror=null; this.src=\\\'../img/placeholder_player.png\\\';">'
)

with open('/Users/franmonti/Documents/Austral/worldcup-app/frontend/js/draft.js', 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated draft.js to include referrerpolicy")
