import io
import re

# 1. Fix draft.css
with io.open('frontend/draft.css', 'r', encoding='utf-8') as f:
    css_text = f.read()

# Replace .pitch-container to include width: 100%;
css_text = re.sub(
    r'(\.pitch-container\s*\{\s*)(background:)',
    r'\1width: 100%;\n    \2',
    css_text
)
with io.open('frontend/draft.css', 'w', encoding='utf-8') as f:
    f.write(css_text)
print("Fixed draft.css")


# 2. Fix state.js parseJSON function
with io.open('frontend/js/state.js', 'r', encoding='utf-8') as f:
    state_text = f.read()

old_parseJSON = """    const parseJSON = async (res) => {
      try {
        if (res.ok) return await res.json();
        console.error('parseJSON error', e, res.url); return null;
      } catch (e) {
        console.error('parseJSON error', e, res.url); return null;
      }
    };"""

new_parseJSON = """    const parseJSON = async (res) => {
      try {
        if (res.ok) return await res.json();
        console.error('parseJSON not ok', res.url); return null;
      } catch (e) {
        console.error('parseJSON error', e, res ? res.url : 'unknown'); return null;
      }
    };"""

state_text = state_text.replace(old_parseJSON, new_parseJSON)

with io.open('frontend/js/state.js', 'w', encoding='utf-8') as f:
    f.write(state_text)
print("Fixed state.js")


# 3. Fix ui/draft.js robustNormalise scope
with io.open('frontend/js/ui/draft.js', 'r', encoding='utf-8') as f:
    draft_ui_text = f.read()

# Move robustNormalise to the top level
old_getPlayerPhoto = """  function getPlayerPhoto(name) {
    if (!state.appData || !state.appData.photoIndex) return 'https://cdn.sofifa.net/players/notfound_0_120.png';
  
    const robustNormalise = str => {
      if (!str) return '';
      return str
        .normalize('NFD')
        .replace(/[\\u0300-\\u036f]/g, '')
        .replace(/\\u00d8/g, 'O')
        .replace(/\\u00f8/g, 'o')
        .replace(/\\u0111/g, 'd')
        .replace(/\\u0110/g, 'D')
        .toLowerCase().trim();
    };"""

new_getPlayerPhoto = """  const robustNormalise = str => {
    if (!str) return '';
    return str
      .normalize('NFD')
      .replace(/[\\u0300-\\u036f]/g, '')
      .replace(/\\u00d8/g, 'O')
      .replace(/\\u00f8/g, 'o')
      .replace(/\\u0111/g, 'd')
      .replace(/\\u0110/g, 'D')
      .toLowerCase().trim();
  };

  function getPlayerPhoto(name) {
    if (!state.appData || !state.appData.photoIndex) return 'https://cdn.sofifa.net/players/notfound_0_120.png';
  """

draft_ui_text = draft_ui_text.replace(old_getPlayerPhoto, new_getPlayerPhoto)

with io.open('frontend/js/ui/draft.js', 'w', encoding='utf-8') as f:
    f.write(draft_ui_text)
print("Fixed ui/draft.js")
