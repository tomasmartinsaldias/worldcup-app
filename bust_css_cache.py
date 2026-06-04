import io
import time

with io.open('frontend/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

v = str(int(time.time()))

html = html.replace('href="draft.css"', 'href="draft.css?v=' + v + '"')
html = html.replace('href="css/styles.css"', 'href="css/styles.css?v=' + v + '"')

with io.open('frontend/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print('Cache busted CSS in index.html')
