#!/usr/bin/env python
# Convert Claude agents/<n>.md -> Codex agents-codex/<n>.toml.
#
# Rules (spec-v2 sec 3.2):
#  - name: hyphen -> underscore
#  - description: verbatim (single-line basic string, escaped)
#  - developer_instructions: full markdown body verbatim, in a TOML multi-line
#    LITERAL string (triple-single-quote) so regex backslashes and embedded
#    triple-double-quotes survive unchanged. Verified no body contains '''.
#  - 'via the Skill tool' / 'the Skill tool' -> explicit backtick-dollar skill
#    mention (Codex has no Skill tool; skills are mentioned by $name).
#  - tools:/skills:/model:/color: dropped; sandbox_mode replaces tools.
#  - model omitted (inherit user default, sec 8.2 #5).
import os
import re

SRC = r"C:\AI\migbot\migbot\agents"
DST = r"C:\AI\migbot\migbot-codex\agents-codex"
os.makedirs(DST, exist_ok=True)

# (sandbox_mode, nickname_candidates)
CLASSIFY = {
    "a2h-ios-converter": ("workspace-write", ["Converter-1", "Converter-2"]),
    # analyzer writes spec/ref docs, so it needs workspace-write despite being
    # an analysis role (Codex read-only would block the doc writes).
    "a2h-ios-analyzer": ("workspace-write", ["Analyzer-1"]),
    "a2h-fixer": ("workspace-write", ["Fixer-1", "Fixer-2"]),
    "a2h-migration-worker": ("workspace-write", ["Worker-1", "Worker-2"]),
    "hmos-builder": ("workspace-write", ["Builder-1", "Builder-2"]),
    "visual-fixer": ("workspace-write", ["VFixer-1", "VFixer-2"]),
    # reviewer only returns review flags to the main agent; no file writes.
    "visual-fixer-reviewer": ("read-only", ["Reviewer-1"]),
}


def parse_frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---\n?(.*)$", text, re.S)
    if not m:
        return {}, text
    fm_raw, body = m.group(1), m.group(2)
    fm = {}
    for line in fm_raw.splitlines():
        m2 = re.match(r"^([a-zA-Z_-]+):\s*(.*)$", line)
        if m2:
            fm[m2.group(1)] = m2.group(2).strip()
    return fm, body


def transform_body(body):
    body = body.replace("via the Skill tool", "via an explicit `$<skill-name>` mention")
    body = body.replace("the Skill tool", "an explicit `$<skill-name>` mention")
    # The only Claude `Skill(...)` tool dispatch (hmos-builder) -> $ mention.
    # Must run BEFORE the underscore rename below (the call string embeds the name).
    body = body.replace(
        'Skill("hmos_fix_build_errors", args="<PROJECT_PATH> <DEVECO_PATH>" + (SIGNED ? " --signed" : ""))',
        '`$hmos-fix-build-errors <PROJECT_PATH> <DEVECO_PATH>`   (append `--signed` when SIGNED is set)',
    )
    # Renamed skills: underscore -> hyphen (opencode port renamed these dirs; codex keeps it).
    body = body.replace("hmos_fix_build_errors", "hmos-fix-build-errors")
    body = body.replace("android2hmos_resources_convert", "ios-resources-convert")
    return body


def toml_desc(desc):
    esc = desc.replace("\\", "\\\\").replace('"', '\\"')
    return '"' + esc + '"'


for fname in sorted(os.listdir(SRC)):
    if not fname.endswith(".md"):
        continue
    base = fname[:-3]
    with open(os.path.join(SRC, fname), encoding="utf-8") as f:
        text = f.read()
    fm, body = parse_frontmatter(text)
    name = fm.get("name", base).replace("-", "_")
    desc = fm.get("description", "")
    sandbox, nicks = CLASSIFY.get(base, ("workspace-write", []))
    body = transform_body(body).rstrip("\n")

    nick_line = ""
    if nicks:
        nick_line = "nickname_candidates = [" + ", ".join('"%s"' % n for n in nicks) + "]"

    note = ""
    if base == "a2h-ios-analyzer":
        note = "  # workspace-write (not read-only): writes spec/ref docs"

    parts = []
    parts.append("# .codex/agents/%s.toml" % name)
    parts.append("# Converted from agents/%s.md (Claude) -> Codex subagent TOML." % base)
    parts.append("# See spec-v2.md §3.2 for the field mapping.")
    parts.append('name = "%s"' % name)
    parts.append("description = %s" % toml_desc(desc))
    parts.append("# model intentionally omitted - inherits the user default (spec §8.2#5).")
    parts.append('sandbox_mode = "%s"%s' % (sandbox, note))
    if nick_line:
        parts.append(nick_line)
    parts.append("")
    parts.append("developer_instructions = '''")
    parts.append(body)
    parts.append("'''")
    parts.append("")
    with open(os.path.join(DST, name + ".toml"), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(parts))

print("converted %d agents -> %s" % (len([x for x in os.listdir(SRC) if x.endswith('.md')]), DST))
