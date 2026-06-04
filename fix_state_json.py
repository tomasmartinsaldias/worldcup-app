import re

with open('frontend/js/state.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the Promise.all logic with one that gracefully handles .json() parsing
replacement = """
    const parseJSON = async (res) => {
      try {
        if (res.ok) return await res.json();
        return null;
      } catch (e) {
        return null;
      }
    };
    
    state.appData = await parseJSON(mainRes) || {};
    state.appData.clubLogos = await parseJSON(logosRes) || {};

    const estiloData = await parseJSON(estiloRes) || { response: [] };
    const arquetiposData = await parseJSON(arquetiposRes) || { archetypes: [] };
    state.appData.estilos = estiloData.response;
    state.appData.arquetipos = arquetiposData.archetypes;

    const clusters = await Promise.all([gkRes, cbRes, fbRes, midRes, wingRes, stRes].map(parseJSON));
"""

# Let's use a regex to replace from "state.appData = await mainRes.json();" 
# to "const clusters = await Promise.all([...]);"
pattern = re.compile(
    r"state\.appData = await mainRes\.json\(\);.*?const clusters = await Promise\.all\(\[.*?\]\);", 
    re.DOTALL
)

content = pattern.sub(replacement, content)

with open('frontend/js/state.js', 'w', encoding='utf-8') as f:
    f.write(content)
print("Fixed json parsing in state.js")
