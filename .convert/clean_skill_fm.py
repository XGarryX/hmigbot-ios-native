#!/usr/bin/env python
# Remove Codex-incompatible frontmatter keys from every skill's SKILL.md.
# Only edits the YAML frontmatter block (between the first two '---' lines);
# the body is preserved verbatim. Keys removed: allowed-tools, compatible.
import os
import re
import glob

ROOT = r"C:\AI\migbot\migbot-codex\skills"
DROP = ("allowed-tools", "compatible")
changed = []

for md in glob.glob(os.path.join(ROOT, "*", "SKILL.md")):
    with open(md, encoding="utf-8") as f:
        text = f.read()
    m = re.match(r"^---\n(.*?)\n---\n?(.*)$", text, re.S)
    if not m:
        continue
    fm, body = m.group(1), m.group(2)
    lines = fm.split("\n")
    kept = []
    skip_cont = False
    for ln in lines:
        key = re.match(r"^([A-Za-z_-]+):", ln)
        if key and key.group(1) in DROP:
            skip_cont = True
            continue
        if skip_cont:
            # drop YAML list/map continuation lines (indented under the dropped key)
            if re.match(r"^\s", ln):
                continue
            skip_cont = False
        kept.append(ln)
    new_fm = "\n".join(kept).rstrip()
    new_text = "---\n" + new_fm + "\n---\n" + body
    if new_text != text:
        with open(md, "w", encoding="utf-8", newline="\n") as f:
            f.write(new_text)
        changed.append(os.path.relpath(md, ROOT))

print("cleaned %d skill frontmatter(s):" % len(changed))
for c in changed:
    print("  -", c)
