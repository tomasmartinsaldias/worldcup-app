import io
with io.open('frontend/js/state.js', 'r', encoding='utf-8') as f:
    text = f.read()

new_func = """    const robustNormalise = str => {
      if (!str) return '';
      return str
        .normalize('NFD')
        .replace(/[\\u0300-\\u036f]/g, '')
        .replace(/ø/gi, 'o').replace(/ð/gi, 'd').replace(/þ/gi, 'th')
        .replace(/æ/gi, 'ae').replace(/ł/gi, 'l').replace(/ß/gi, 'ss').replace(/œ/gi, 'oe')
        .replace(/[^\\x00-\\x7F]/g, '')
        .toLowerCase().trim();
    };"""

text = text.replace('const normalise = str => str ? str.normalize("NFD").replace(/[\\u0300-\\u036f]/g, "").toLowerCase().trim() : "";', new_func)

text = text.replace('normalise(p.n)', 'robustNormalise(p.n)')
text = text.replace('normalise(p.fn)', 'robustNormalise(p.fn)')
text = text.replace('normalise(`${parts[0][0]}. ${parts[parts.length - 1]}`)', 'robustNormalise(`${parts[0][0]}. ${parts[parts.length - 1]}`)')

with io.open('frontend/js/state.js', 'w', encoding='utf-8') as f:
    f.write(text)
print("Done")
