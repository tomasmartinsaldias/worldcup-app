import io

with io.open('frontend/js/ui/draft.js', 'r', encoding='utf-8') as f:
    text = f.read()

old_err = "container.innerHTML = 'Error: Datos de clusters no cargados.';"
new_err = "container.innerHTML = 'Error: Datos de clusters no cargados. Debug: appData=' + (state.appData ? Object.keys(state.appData).join(',') : 'null') + ' clusters=' + (state.appData && state.appData.clusters ? Object.keys(state.appData.clusters).join(',') : 'null');"

text = text.replace(old_err, new_err)

with io.open('frontend/js/ui/draft.js', 'w', encoding='utf-8') as f:
    f.write(text)

with io.open('frontend/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

import time
v = str(int(time.time()))
import re
html = re.sub(r'\?v=\d+(\?v=\d+)?', '?v=' + v, html)

with io.open('frontend/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
