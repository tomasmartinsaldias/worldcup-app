import re

with open('frontend/css/styles.css', 'r', encoding='utf-8') as f:
    content = f.read()

new_styles = """
    /* --- PAGE SLIDE SYSTEM --- */
    .ui-page {
      position: absolute;
      top: 0; left: 0; width: 100vw; height: 100vh;
      transition: transform 1.2s cubic-bezier(0.77, 0, 0.175, 1), opacity 0.8s ease;
      z-index: 5;
      display: flex;
      flex-direction: column;
      justify-content: center;
      align-items: center;
    }
    
    #page-hero {
      /* Keep hero UI structure from inside it */
      display: block; 
    }

    .page-active {
      transform: translateY(0);
      opacity: 1;
      pointer-events: auto;
    }

    .page-above {
      transform: translateY(-100vh);
      opacity: 0.2;
      pointer-events: none;
    }

    .page-below {
      transform: translateY(100vh);
      opacity: 0;
      pointer-events: none;
    }

    /* Epic Title for the spectator selection */
    .epic-title {
      font-family: 'Outfit', sans-serif;
      font-size: 4rem;
      font-weight: 300;
      letter-spacing: 4px;
      margin-bottom: 0.5rem;
      text-transform: uppercase;
      background: linear-gradient(135deg, #f5d061 0%, #8a7330 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      text-shadow: 0 4px 20px rgba(245, 208, 97, 0.2);
    }
    
    .epic-subtitle {
      font-family: 'Inter', sans-serif;
      font-size: 1.2rem;
      color: #aaa;
      margin-bottom: 4rem;
      letter-spacing: 2px;
      text-transform: uppercase;
    }
    
    .text-center { text-align: center; }
"""

if "/* --- PAGE SLIDE SYSTEM --- */" not in content:
    with open('frontend/css/styles.css', 'a', encoding='utf-8') as f:
        f.write(new_styles)
    print("Added page slide styles to styles.css")
