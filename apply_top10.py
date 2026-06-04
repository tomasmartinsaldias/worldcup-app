import io

with io.open('frontend/js/ui/draft.js', 'r', encoding='utf-8') as f:
    text = f.read()

old_logic = """    const players = state.appData.clusters[groupName].filter(p => p.cluster_id == clusterId);
    const shuffled = players.sort(() => 0.5 - Math.random());
    const selected = shuffled.slice(0, 3);"""

new_logic = """    const players = state.appData.clusters[groupName].filter(p => p.cluster_id == clusterId);
    
    // Sort descending by overall (handling missing overalls as 0)
    const sorted = players.sort((a, b) => (b.overall || 0) - (a.overall || 0));
    
    // Take top 10 players
    const top10 = sorted.slice(0, 10);
    
    // Shuffle the top 10
    const shuffled = top10.sort(() => 0.5 - Math.random());
    
    // Select 3 to display
    const selected = shuffled.slice(0, 3);"""

if old_logic in text:
    text = text.replace(old_logic, new_logic)
    with io.open('frontend/js/ui/draft.js', 'w', encoding='utf-8') as f:
        f.write(text)
    print('Successfully applied top 10 logic!')
else:
    print('old_logic not found!')
