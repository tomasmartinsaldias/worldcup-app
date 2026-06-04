import re

with open('/Users/franmonti/Documents/Austral/worldcup-app/frontend/js/scene3D.js', 'r', encoding='utf-8') as f:
    content = f.read()

animate_func = """    function animate() {
      requestAnimationFrame(animate);

      // PAUSE RENDER LOOP IF NOT ON HOMEPAGE TO SAVE CPU/GPU
      if (window.appState && window.appState !== 'homepage' && window.appState !== 'transition') {
          return;
      }

      const elapsedTime = clock.getElapsedTime();"""

content = re.sub(r'    function animate\(\) \{\n      requestAnimationFrame\(animate\);\n      const elapsedTime = clock\.getElapsedTime\(\);', animate_func, content)

with open('/Users/franmonti/Documents/Austral/worldcup-app/frontend/js/scene3D.js', 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated scene3D.js animate loop")
