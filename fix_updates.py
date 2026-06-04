import io

# 1. Fix draft.css (pitch width)
with io.open('frontend/draft.css', 'r', encoding='utf-8') as f:
    css_text = f.read()

if '.pitch-container {\n    background' in css_text:
    css_text = css_text.replace(
        '.pitch-container {\n    background',
        '.pitch-container {\n    width: 100%;\n    background'
    )
    with io.open('frontend/draft.css', 'w', encoding='utf-8') as f:
        f.write(css_text)
    print("Fixed draft.css width")


# 2. Fix state.js (clusters Promise mapping & finalPhotosData saving)
with io.open('frontend/js/state.js', 'r', encoding='utf-8') as f:
    state_text = f.read()

old_clusters = "const clusters = await Promise.all([gkRes, cbRes, fbRes, midRes, wingRes, stRes].map(parseJSON));"
new_clusters = "const clusters = await Promise.all([gkRes, cbRes, fbRes, midRes, wingRes, stRes].map(async p => await parseJSON(await p)));"
state_text = state_text.replace(old_clusters, new_clusters)

old_save_photos = "    state.appData.photoIndex = {};"
new_save_photos = "    state.appData.playersFinal = finalPhotosData;\n    state.appData.photoIndex = {};"
state_text = state_text.replace(old_save_photos, new_save_photos)

with io.open('frontend/js/state.js', 'w', encoding='utf-8') as f:
    f.write(state_text)
print("Fixed state.js promises and playersFinal")


# 3. Fix ui/draft.js (Sort players by Overall and get photo from players_final.json)
with io.open('frontend/js/ui/draft.js', 'r', encoding='utf-8') as f:
    draft_ui_text = f.read()

old_show = """  const players = state.appData.clusters[groupName].filter(p => p.cluster_id == clusterId);
  const shuffled = players.sort(() => 0.5 - Math.random());
  const selected = shuffled.slice(0, 3);

  selected.forEach((player, index) => {
    const photoUrl = getPlayerPhoto(player.long_name);"""

new_show = """  let players = state.appData.clusters[groupName].filter(p => p.cluster_id == clusterId);
  
  // Enrich with playersFinal data (Overall and photo)
  if (state.appData.playersFinal) {
    players.forEach(p => {
      const pName = robustNormalise(p.long_name);
      const finalPlayer = state.appData.playersFinal.find(fp => robustNormalise(fp.NAME) === pName || (fp.NAME && fp.NAME.includes(p.long_name)));
      if (finalPlayer) {
        if (finalPlayer.Overall) p.overall = finalPlayer.Overall;
        if (finalPlayer._URL) p.photoUrl = finalPlayer._URL;
      }
    });
  }

  // Sort by overall descending
  players.sort((a, b) => (b.overall || 0) - (a.overall || 0));
  const selected = players.slice(0, 3);

  selected.forEach((player, index) => {
    const photoUrl = player.photoUrl || getPlayerPhoto(player.long_name);"""

draft_ui_text = draft_ui_text.replace(old_show, new_show)

# Also need to use the photoUrl when selecting the player in selectPlayer
old_select = """function selectPlayer(player) {
  draftedPlayers[currentActiveSlot] = player;
  const photoUrl = getPlayerPhoto(player.long_name);"""

new_select = """function selectPlayer(player) {
  draftedPlayers[currentActiveSlot] = player;
  const photoUrl = player.photoUrl || getPlayerPhoto(player.long_name);"""

draft_ui_text = draft_ui_text.replace(old_select, new_select)

with io.open('frontend/js/ui/draft.js', 'w', encoding='utf-8') as f:
    f.write(draft_ui_text)
print("Fixed ui/draft.js sorting and photos")
