import io

with io.open('frontend/js/ui/draft.js', 'r', encoding='utf-8') as f:
    text = f.read()

# Fix the corrupted robustNormalise replacement lines
# Old (corrupted) function body - we'll do it by locating the pattern
old_replace_lines = "        .replace(/\u00f8/gi, 'o').replace(/\u00f0/gi, 'd').replace(/\u00fe/gi, 'th')\n        .replace(/\u00e6/gi, 'ae').replace(/\u0142/gi, 'l').replace(/\u00df/gi, 'ss').replace(/\u0153/gi, 'oe')"

new_replace_lines = r"        .replace(/\u00f8/gi, 'o').replace(/\u00f0/gi, 'd').replace(/\u00fe/gi, 'th')" + "\n" + r"        .replace(/\u00e6/gi, 'ae').replace(/\u0142/gi, 'l').replace(/\u00df/gi, 'ss').replace(/\u0153/gi, 'oe')"

# The replace call in the file has corrupted chars, we need to find and fix them
# Find the function block first
start_marker = "    const robustNormalise = str => {\n      if (!str) return '';\n      return str\n        .normalize('NFD')\n        .replace(/[\\u0300-\\u036f]/g, '')\n"
end_marker = "\n        .replace(/[^\\x00-\\x7F]/g, '')\n        .toLowerCase().trim();"

start_idx = text.find(start_marker)
if start_idx == -1:
    print("Could not find robustNormalise function")
else:
    end_idx = text.find(end_marker, start_idx)
    middle_section = text[start_idx + len(start_marker):end_idx]
    print("Middle section found:")
    print(repr(middle_section))
    
    fixed_middle = r"        .replace(/\u00f8/gi, 'o').replace(/\u00f0/gi, 'd').replace(/\u00fe/gi, 'th')" + "\n" + r"        .replace(/\u00e6/gi, 'ae').replace(/\u0142/gi, 'l').replace(/\u00df/gi, 'ss').replace(/\u0153/gi, 'oe')"
    
    new_text = text[:start_idx + len(start_marker)] + fixed_middle + text[end_idx:]
    
    with io.open('frontend/js/ui/draft.js', 'w', encoding='utf-8') as f:
        f.write(new_text)
    print("Done!")
