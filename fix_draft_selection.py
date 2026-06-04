import re

with open('/Users/franmonti/Documents/Austral/worldcup-app/frontend/js/draft.js', 'r', encoding='utf-8') as f:
    content = f.read()

# For teams
teams_func = """
  paginated.forEach((t) => {
    const originalIndex = draftData.teams.indexOf(t);
    const isSelected = draftState.team === originalIndex ? 'selected' : '';
    html += `
      <div class="draft-card ${isSelected}" data-type="team" data-id="${originalIndex}">
"""
content = re.sub(r'\s*paginated\.forEach\(\(t\) => \{[\s\S]*?html \+= `[\s\S]*?<div class="draft-card" data-type="team" data-id="\$\{originalIndex\}">', teams_func, content)

# For countries
countries_func = """
  paginated.forEach((c) => {
    const originalIndex = draftData.countries.indexOf(c);
    const isSelected = draftState.countries.includes(originalIndex) ? 'selected' : '';
    html += `
      <div class="draft-card ${isSelected}" data-type="country" data-id="${originalIndex}">
"""
content = re.sub(r'\s*paginated\.forEach\(\(c\) => \{[\s\S]*?html \+= `[\s\S]*?<div class="draft-card" data-type="country" data-id="\$\{originalIndex\}">', countries_func, content)

# For players
players_func = """
  paginated.forEach((p) => {
    const originalIndex = draftData.players.indexOf(p);
    const isSelected = draftState.players.includes(originalIndex) ? 'selected' : '';
    const imgUrl = p._URL || '../img/placeholder_player.png';
    html += `
      <div class="draft-card ${isSelected}" data-type="player" data-id="${originalIndex}">
"""
content = re.sub(r'\s*paginated\.forEach\(\(p\) => \{[\s\S]*?const imgUrl = p\._URL \|\| \'\.\./img/placeholder_player\.png\';[\s\S]*?html \+= `[\s\S]*?<div class="draft-card" data-type="player" data-id="\$\{originalIndex\}">', players_func, content)

with open('/Users/franmonti/Documents/Austral/worldcup-app/frontend/js/draft.js', 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated draft.js selection states")
