import re
with open('frontend/index.html', 'r') as f:
    lines = f.readlines()

new_lines = []
for i, line in enumerate(lines):
    # lines are 0-indexed, so line 597 is i=596
    if 596 <= i <= 723: 
        continue
    new_lines.append(line)

with open('frontend/index.html', 'w') as f:
    f.writelines(new_lines)
