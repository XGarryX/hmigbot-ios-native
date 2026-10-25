#!/usr/bin/env python
# Align subagent dispatch with Codex (spec sec 3.2):
#  1. rename the field `subagent_type` -> `agent_type` everywhere in skill docs
#     (Codex's spawn_agent uses `agent_type`; the token is unambiguous).
#  2. inject a dispatch-convention note into the two pipeline orchestrators
#     (a2h-execute, a2h-spec) that maps the hyphen agent labels to the underscore
#     `.codex/agents/` role names and names spawn_agent as the tool.
# We do NOT globally rename hyphen role labels (they also appear in prose / paths);
# the convention note tells the model the mapping instead.
import os
import re
import glob

ROOT = r"C:\AI\migbot\migbot-codex\skills"

NOTE = (
    "> **Codex subagent dispatch convention.** This skill dispatches subagents. In Codex, "
    "spawn them with the `spawn_agent` tool, `agent_type` = the role's underscore name. The "
    "hyphen labels below map to the registered `.codex/agents/` roles: "
    "`a2h-ios-converter`->`a2h_activity_converter`, "
    "`a2h-migration-worker`->`a2h_migration_worker`, "
    "`a2h-ios-analyzer`->`a2h_android_analyzer`, "
    "`hmos-builder`->`hmos_builder`, `visual-fixer`->`visual_fixer`, "
    "`visual-fixer-reviewer`->`visual_fixer_reviewer`, `a2h-fixer`->`a2h_fixer`. "
    "The built-in `general-purpose` agent_type is unchanged. "
    "(Claude's `subagent_type` field is written `agent_type` for Codex; "
    "`Agent(...)` dispatch calls are `spawn_agent(...)`.)\n\n"
)

renamed = 0
for md in glob.glob(os.path.join(ROOT, "**", "*.md"), recursive=True):
    with open(md, encoding="utf-8") as f:
        orig = f.read()
    new = orig.replace("subagent_type", "agent_type")
    if new != orig:
        with open(md, "w", encoding="utf-8", newline="\n") as f:
            f.write(new)
        renamed += 1

injected = []
for skill in ("a2h-execute", "a2h-spec"):
    md = os.path.join(ROOT, skill, "SKILL.md")
    with open(md, encoding="utf-8") as f:
        text = f.read()
    if "Codex subagent dispatch convention" in text:
        continue
    # insert right after the frontmatter block (after the second '---' line)
    m = re.match(r"^---\n.*?\n---\n", text, re.S)
    if not m:
        continue
    pos = m.end()
    text = text[:pos] + "\n" + NOTE + text[pos:]
    with open(md, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    injected.append(skill)

print("renamed subagent_type->agent_type in %d doc(s)" % renamed)
print("injected dispatch convention into: %s" % (", ".join(injected) or "none"))
