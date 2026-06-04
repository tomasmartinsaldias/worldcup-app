import re

with open('frontend/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Wrap hero-ui and scroll-indicator in page-hero
# Find the start of hero-ui and the end of scroll-indicator
start_idx = content.find('<div class="hero-ui">')
end_idx = content.find('<!-- OVERLAYS UI -->')

if start_idx != -1 and end_idx != -1:
    hero_content = content[start_idx:end_idx]
    wrapped_hero = '<div id="page-hero" class="ui-page page-active">\n  ' + hero_content.replace('\n', '\n  ').rstrip(' ') + '\n</div>\n\n'
    content = content[:start_idx] + wrapped_hero + content[end_idx:]

# Modify spectator-selection
# Change <div id="spectator-selection" class="ui-overlay hidden">
# to <div id="spectator-selection" class="ui-page page-below">
content = content.replace('<div id="spectator-selection" class="ui-overlay hidden">', '<div id="spectator-selection" class="ui-page page-below">')

# Modify titles inside spectator-selection to match hero text style
# <h2 class="overlay-title">ELIGE TU NIVEL</h2> -> <h2 class="epic-title text-center">ELIGE TU DESTINO</h2>
content = content.replace('<h2 class="overlay-title">ELIGE TU NIVEL</h2>', '<h2 class="epic-title text-center">ELIGE TU DESTINO</h2>')
content = content.replace('<p class="overlay-title">', '<p class="epic-subtitle text-center">')
content = content.replace('Elige cómo vas a vivir el mundial para personalizar tu experiencia.', 'Define cómo vivirás la gloria de la Copa del Mundo.')

with open('frontend/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated index.html")
