
with open('frontend/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

close_btn = """<button id="close-draft-modal-btn" style="position: absolute; top: 1rem; right: 1rem; background: transparent; color: white; border: none; font-size: 1.5rem; cursor: pointer; z-index: 10;"><i class="fa-solid fa-xmark"></i></button>
          <h2 id="draft-modal-title" """

content = content.replace('<h2 id="draft-modal-title" ', close_btn)

with open('frontend/index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print("Added close button to draft modal")
