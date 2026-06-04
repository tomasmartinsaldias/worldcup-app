import io

# Fix ui/draft.js
with io.open('frontend/js/ui/draft.js', 'r', encoding='utf-8') as f:
    text = f.read()

# Fix cosine similarity mapping in draft.js
old_map = """  // Map normalized feature values (~0.15) to [-1, 1] range.
  let ritmo = (avgPace - 0.15) * 15;
  let posesion = (avgPassing - 0.15) * 15;
  let defensa = (avgDefending - 0.15) * 15;"""

new_map = """  // Map standardized feature values (mean 0, std 1) to approximately [-1, 1] range.
  let ritmo = avgPace / 3;
  let posesion = avgPassing / 3;
  let defensa = avgDefending / 3;"""

text = text.replace(old_map, new_map)

with io.open('frontend/js/ui/draft.js', 'w', encoding='utf-8') as f:
    f.write(text)

print("Updates applied to ui/draft.js")
