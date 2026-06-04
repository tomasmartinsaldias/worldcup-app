import io

with io.open('frontend/js/state.js', 'r', encoding='utf-8') as f:
    text = f.read()

old_catch = """  } catch (err) {
    console.error('Error loading data:', err);
  }"""

new_catch = """  } catch (err) {
    console.error('Error loading data:', err);
    state.appData = { _error_caught: err.toString() };
  }"""

if old_catch in text:
    text = text.replace(old_catch, new_catch)
    with io.open('frontend/js/state.js', 'w', encoding='utf-8') as f:
        f.write(text)
    print('Updated catch')
else:
    print('Could not find catch')

import time, re
with io.open('frontend/index.html', 'r', encoding='utf-8') as f:
    html = f.read()
v = str(int(time.time()))
html = re.sub(r'\?v=\d+(\?v=\d+)?', '?v=' + v, html)
with io.open('frontend/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
