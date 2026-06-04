import re

with open('/Users/franmonti/Documents/Austral/worldcup-app/frontend/js/particles.js', 'r', encoding='utf-8') as f:
    content = f.read()

animate_func = """function animateParticles() {
  requestAnimationFrame(animateParticles);

  // PAUSE RENDER LOOP IF NOT ON HOMEPAGE TO SAVE CPU/GPU
  if (window.appState && window.appState !== 'homepage' && window.appState !== 'transition') {
      return;
  }

  ctx.clearRect(0, 0, canvas.width, canvas.height);"""

content = re.sub(r'function animateParticles\(\) \{\n  requestAnimationFrame\(animateParticles\);\n  ctx\.clearRect\(0, 0, canvas\.width, canvas\.height\);', animate_func, content)

with open('/Users/franmonti/Documents/Austral/worldcup-app/frontend/js/particles.js', 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated particles.js animate loop")
