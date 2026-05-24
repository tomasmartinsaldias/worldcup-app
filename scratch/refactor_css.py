import re

css_path = r"c:\Users\user\Downloads\app_mundial\worldcup-app\frontend\style.css"
with open(css_path, "r", encoding="utf-8") as f:
    css = f.read()

# 1. Replace :root
root_old = re.search(r":root \{.*?\n\}", css, re.DOTALL).group(0)
root_new = """:root {
  --bg-primary: #f4f6f9;
  --bg-secondary: #ffffff;
  --bg-tertiary: #e2e8f0;
  --bg-card: #ffffff;
  --bg-glass: rgba(255, 255, 255, 0.9);
  
  --border-glass: rgba(26, 43, 76, 0.08);
  --border-glow: rgba(211, 32, 42, 0.15);
  
  --accent-navy: #1a2b4c;
  --accent-red: #d3202a;
  --accent-green: #007749;
  --accent-gold: #d3202a;
  --accent-teal: #007749;
  --accent-cyan: #1a2b4c;
  --accent-purple: #6b21a8;
  
  --text-primary: #111827;
  --text-secondary: #4b5563;
  --text-muted: #6b7280;
  
  --font-primary: 'Outfit', sans-serif;
  --font-secondary: 'Inter', sans-serif;
  
  --transition-fast: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  --transition-smooth: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
  --shadow-neon: 0 0 15px rgba(211, 32, 42, 0.15);
  --shadow-card: 0 10px 25px -5px rgba(26, 43, 76, 0.05);
}"""
css = css.replace(root_old, root_new)

# 2. Update body gradient
body_old = re.search(r"body \{.*?\n\}", css, re.DOTALL).group(0)
body_new = """body {
  background-color: var(--bg-primary);
  color: var(--text-primary);
  font-family: var(--font-secondary);
  overflow-x: hidden;
  background-image: radial-gradient(circle at 10% 20%, rgba(211, 32, 42, 0.03) 0%, transparent 50%), radial-gradient(circle at 90% 80%, rgba(0, 119, 73, 0.03) 0%, transparent 50%);
  background-attachment: fixed;
  min-height: 100vh;
}"""
css = css.replace(body_old, body_new)

# 3. Update header
css = re.sub(r"header \{[^\}]*\}", """header {
  position: sticky;
  top: 0;
  z-index: 100;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--border-glass);
  box-shadow: 0 4px 6px -1px rgba(26, 43, 76, 0.05);
}""", css, count=1)

# Update logo
css = re.sub(r"\.logo \{.*?-webkit-text-fill-color: transparent;\s*\}", """.logo {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 1.5rem;
  font-family: var(--font-primary);
  font-weight: 800;
  color: var(--accent-navy);
}""", css, flags=re.DOTALL)
css = re.sub(r"\.logo i \{.*?-webkit-text-fill-color: transparent;\s*\}", """.logo i {
  color: var(--accent-red);
}""", css, flags=re.DOTALL)

# Update nav-btn.active
css = re.sub(r"\.nav-btn\.active \{.*?\}", """.nav-btn.active {
  color: #ffffff;
  background: var(--accent-navy);
  box-shadow: var(--shadow-card);
}""", css, flags=re.DOTALL)

# Update hero section
css = re.sub(r"\.hero-section \{.*?\}", """.hero-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  margin-bottom: 3rem;
  padding: 2.5rem;
  border-radius: 24px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-glass);
  box-shadow: var(--shadow-card);
  position: relative;
  overflow: hidden;
}""", css, flags=re.DOTALL, count=1)

css = re.sub(r"\.hero-title \{.*?\}", """.hero-title {
  font-size: 2.75rem;
  font-weight: 800;
  margin-bottom: 1rem;
  color: var(--accent-navy);
}""", css, flags=re.DOTALL)

css = re.sub(r"\.hero-tag \{.*?\}", """.hero-tag {
  font-family: var(--font-primary);
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.15em;
  color: var(--accent-red);
  font-size: 0.85rem;
  margin-bottom: 0.75rem;
}""", css, flags=re.DOTALL)

# 4. Automate general fixes for light theme
# Reemplazar transparencias de blanco (usadas en dark theme para dar luz)
# por transparencias del navy (para dar sombra en light theme)
css = css.replace("rgba(255, 255, 255, 0.05)", "rgba(26, 43, 76, 0.05)")
css = css.replace("rgba(255, 255, 255, 0.02)", "rgba(26, 43, 76, 0.02)")
css = css.replace("rgba(255, 255, 255, 0.03)", "rgba(26, 43, 76, 0.03)")
css = css.replace("rgba(255, 255, 255, 0.06)", "rgba(26, 43, 76, 0.06)")
css = css.replace("rgba(255, 255, 255, 0.08)", "rgba(26, 43, 76, 0.08)")
css = css.replace("rgba(255, 255, 255, 0.1)", "rgba(26, 43, 76, 0.1)")
css = css.replace("rgba(255,255,255,0.05)", "rgba(26,43,76,0.05)")
css = css.replace("rgba(255,255,255,0.08)", "rgba(26,43,76,0.08)")

# Cambiar fondos semitransparentes oscuros a blancos
css = css.replace("rgba(8, 12, 20, 0.4)", "rgba(255, 255, 255, 0.6)")
css = css.replace("rgba(8, 12, 20, 0.5)", "rgba(255, 255, 255, 0.7)")
css = css.replace("rgba(8, 12, 20, 0.75)", "rgba(255, 255, 255, 0.95)")
css = css.replace("rgba(8, 12, 20, 0.7)", "rgba(26, 43, 76, 0.5)") # Modal backdrop

# Reemplazar los colores hardcodeados de teal y gold a los nuevos verde y rojo (en rgba)
css = css.replace("rgba(6, 182, 212,", "rgba(0, 119, 73,") # Teal -> Green
css = css.replace("rgba(251, 191, 36,", "rgba(211, 32, 42,") # Gold -> Red

# Suavizar sombras que en dark mode eran negro intenso
css = css.replace("rgba(0, 0, 0, 0.7)", "rgba(26, 43, 76, 0.08)")
css = css.replace("rgba(0, 0, 0, 0.8)", "rgba(26, 43, 76, 0.1)")
css = css.replace("rgba(0, 0, 0, 0.5)", "rgba(26, 43, 76, 0.1)")
css = css.replace("rgba(0, 0, 0, 0.3)", "rgba(26, 43, 76, 0.08)")
css = css.replace("rgba(0,0,0,0.3)", "rgba(26,43,76,0.08)")
css = css.replace("rgba(0,0,0,0.5)", "rgba(26,43,76,0.1)")

# Quitar gradientes de colores para usar sólidos o colores limpios
css = re.sub(r"linear-gradient\(.*?, var\(--accent-gold\) 0%, var\(--accent-teal\) 100%\)", "var(--accent-red)", css)
css = re.sub(r"linear-gradient\(.*?, rgba\(30, 41, 59, 0\.4\) 0%, rgba\(15, 23, 42, 0\.6\) 100%\)", "var(--bg-secondary)", css)

with open(css_path, "w", encoding="utf-8") as f:
    f.write(css)

print("Refactor de CSS completado exitosamente.")
