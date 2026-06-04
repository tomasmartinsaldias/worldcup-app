import re

with open('frontend/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

import_state_pattern = re.compile(r"import \{ loadData \} from '\./js/state\.js.*';")
import_draft_pattern = re.compile(r"import \{ initDraft, startDraft \} from '\./js/ui/draft\.js.*';")

import_time = "import { loadData } from './js/state.js?v=3';"
import_draft_time = "import { initDraft, startDraft } from './js/ui/draft.js?v=3';"

content = import_state_pattern.sub(import_time, content)
content = import_draft_pattern.sub(import_draft_time, content)

with open('frontend/index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print("Added cache busting to module imports")
