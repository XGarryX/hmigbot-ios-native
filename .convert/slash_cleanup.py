#!/usr/bin/env python
# Codex has no slash commands: rewrite every `/a2h-*` and `/migbot-increment-*`
# slash-command reference to the `$`-mention form across all skill docs.
# Path-safe: a slash preceded by '/' or an alnum (e.g. `.migbot/bin/a2h-tool`,
# `.agents/skills/a2h-run/`) is NOT a command reference and is left alone.
# Also rewrites residual `Skill({skill:"<n>"})` tool calls -> `$<n>` mention, and
# `.claude/skills/` textual self-references -> `.agents/skills/`.
import os
import re
import glob

ROOT = r"C:\AI\migbot\migbot-codex\skills"

NAMES = [
    "a2h-init-zh", "a2h-init", "a2h-run-zh", "a2h-run", "a2h-build-zh", "a2h-build",
    "a2h-privacy-zh", "a2h-privacy", "a2h-spec", "a2h-plan", "a2h-execute",
    "a2h-verify", "a2h-retrospect",
    "migbot-increment-init", "migbot-increment-workflow", "migbot-increment-review",
    "migbot-increment-archive", "migbot-increment-planning", "migbot-increment-implementing",
    "migbot-increment-applying", "migbot-increment-reviewing", "migbot-increment-archiving",
]
SLASH = re.compile(r"(?<![A-Za-z0-9/_$])/(?:" + "|".join(re.escape(n) for n in NAMES) + r")")
# Skill({skill:"<name>"}) / Skill(skill="..." / Skill{...}  ->  $<name>
SKILL_CALL = re.compile(r'Skill\(\s*\{?\s*skill\s*[:=]\s*["\']([a-z0-9-]+)["\']')

changed = 0
for md in glob.glob(os.path.join(ROOT, "**", "*.md"), recursive=True):
    with open(md, encoding="utf-8") as f:
        orig = f.read()
    new = SLASH.sub(lambda m: "$" + m.group(0)[1:], orig)
    new = SKILL_CALL.sub(lambda m: "$" + m.group(1), new)
    new = new.replace(".claude/skills/", ".agents/skills/")
    if new != orig:
        with open(md, "w", encoding="utf-8", newline="\n") as f:
            f.write(new)
        changed += 1

print("slash/Skill-call/claude-path cleanup touched %d skill doc(s)" % changed)
