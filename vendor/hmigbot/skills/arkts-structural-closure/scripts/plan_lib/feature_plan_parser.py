"""Parser for feature-plan.md (indexed layout).

Indexed layout (the only supported layout): feature-plan.md is a pure index
whose `## Slice N:` entries carry `detail:` pointers to
plans/slices/slice-NN-<fid>.md; each slice file holds the same `## Slice N:`
header + blocks parsed below. Slice files are read-only scheduling ledgers —
no checkbox / evidence fields (integration_points entries are plain
structured pairs); anchors live in the feature spec, the slice file only
carries `android_source_anchors_ref: {count, source}`.

Old monolith plans (slice sections without `detail:` pointers) are rejected
with an upgrade hint — regenerate via a2h-plan; execution state lives in
ui-manifest / feature-index / briefs and survives re-planning.

The plan file is markdown with YAML-flavored fields embedded under each
Slice section. We don't use yaml.safe_load because the file mixes prose and
loosely-indented YAML; a tolerant line-based parser is more reliable.

Each Slice block:

    ## Slice 7: F005 Filters Overlay (priority: P1, parallel_group: 4)
    complexity: complex
    depends_on: [Slice 3]

    android_source_anchors:
      - role: util
        path: "..."

    placeholders_planned: []

    integration_points:
      - [ ] <handler> ← <target>
        evidence: <text>

    wires:                          # 统一接线账本：VM 实例化 + 组件@Builder嵌入
      - page: <path>                # VM 入边 → C1
        viewmodel: <path>
      - page: <parent path>         # 组件嵌入入边 → C4
        slot: <@Builder名/Tab槽位>
        embed: <ChildPage()>
        resolve_by: Slice N Step 3X

    modifies_files:
      - <path>
      cross_slice_edits:
        - file: <path>
          handler: <name>
          slot: <可选>
          resolve_by: Slice N Step 3X

(Back-compat only: a legacy `parent_placeholder_replacement:` block is still parsed
and folded into the wires embed list; new plans put embeds directly under `wires:`.)
"""
from __future__ import annotations
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


# ─── Public data classes ──────────────────────────────────────────────────────
@dataclass
class IntegrationPoint:
    description: str
    handler_text: str
    target_text: str
    handler_local: Optional[str]
    target_class: Optional[str]
    evidence_raw: str
    checked: bool          # True if `- [x]`, False if `- [ ]`


@dataclass
class WireEntry:
    page: str
    viewmodel: str


@dataclass
class CrossSliceEdit:
    file: str
    handler: str
    resolve_by: str
    slot: str = ""          # P2: 同 (file,handler) 不同槽位的区分键（builder名/Tab槽位），可选


@dataclass
class ParentReplacement:
    parent_file: str
    builder_name: str
    replace_with: str
    resolve_by: str


@dataclass
class SliceSpec:
    slice_id: int
    title: str
    priority: Optional[str] = None
    parallel_group: Optional[int] = None
    complexity: Optional[str] = None
    depends_on: list[str] = field(default_factory=list)
    android_source_anchors: list[dict] = field(default_factory=list)
    placeholders_planned: list[dict] = field(default_factory=list)
    integration_points: list[IntegrationPoint] = field(default_factory=list)
    wires: list[WireEntry] = field(default_factory=list)
    modifies_files: list[str] = field(default_factory=list)
    cross_slice_edits: list[CrossSliceEdit] = field(default_factory=list)
    parent_placeholder_replacement: list[ParentReplacement] = field(default_factory=list)
    detail: str = ""                                   # indexed 布局：索引条目指向的 slice 文件
    anchors_ref: dict = field(default_factory=dict)    # {count, source} —— anchors 权威在 feature spec


@dataclass
class FeaturePlan:
    slices: dict[int, SliceSpec] = field(default_factory=dict)

    def get(self, slice_id: int) -> Optional[SliceSpec]:
        return self.slices.get(slice_id)

    @classmethod
    def parse_file(cls, path: Path) -> "FeaturePlan":
        """Parse feature-plan.md（indexed 布局，唯一支持形态）。

        索引 slice 条目须含 `detail:` 指针 → 逐 slice 文件解析；检测到旧
        monolith（slice 段无 detail 指针）→ SystemExit 提示重跑 a2h-plan。
        """
        text = path.read_text(encoding="utf-8", errors="replace").lstrip("﻿")
        sections = list(_iter_slice_sections(text))
        if not sections:
            return cls.parse(text)
        has_detail = any(
            re.search(r"^detail\s*[:：]", s, re.MULTILINE) for s, _ in sections
        )
        if not has_detail:
            raise SystemExit(
                "error: 检测到旧 monolith feature-plan 格式（slice 段无 detail: 指针）。\n"
                "请重跑 a2h-plan 升级为 indexed 布局（plan_format: indexed-v1）；"
                "执行进度存于 ui-manifest / feature-index / briefs，重排零损失。"
            )
        plan = cls()
        plans_dir = path.parent
        for slice_text, header_groups in sections:
            dm = re.search(r"^detail\s*[:：]\s*(?P<d>\S+)", slice_text, re.MULTILINE)
            if not dm:
                raise SystemExit(
                    f"error: 索引中 Slice {header_groups['sid']} 缺少 detail: 指针"
                    "（indexed 布局必填）。"
                )
            detail_rel = dm.group("d").strip()
            # detail 惯例写作 plans/slices/...（相对 spec/baseline/），此处相对索引所在目录解析
            rel = detail_rel[len("plans/"):] if detail_rel.startswith("plans/") else detail_rel
            slice_path = plans_dir / rel
            if not slice_path.exists():
                raise SystemExit(
                    f"error: slice 文件不存在: {slice_path}（索引 detail: {detail_rel}）"
                )
            s_text = slice_path.read_text(encoding="utf-8", errors="replace").lstrip("﻿")
            parsed_any = False
            for s_section, s_header in _iter_slice_sections(s_text):
                spec = _parse_slice(s_section, s_header)
                spec.detail = detail_rel
                plan.slices[spec.slice_id] = spec
                parsed_any = True
            if not parsed_any:
                raise SystemExit(f"error: slice 文件缺少 `## Slice N:` 头: {slice_path}")
        return plan

    @classmethod
    def parse(cls, text: str) -> "FeaturePlan":
        plan = cls()
        for slice_text, header_groups in _iter_slice_sections(text):
            spec = _parse_slice(slice_text, header_groups)
            plan.slices[spec.slice_id] = spec
        return plan


# ─── Section splitting ────────────────────────────────────────────────────────
_SLICE_HEADER = re.compile(
    r"^##\s+Slice\s+(?P<sid>\d+)\s*[:：]\s*(?P<title>.+?)\s*(?:\((?P<meta>[^)]+)\))?\s*$",
    re.MULTILINE,
)
_META_PRIORITY = re.compile(r"priority\s*[:：]\s*(?P<p>[A-Z]\d)")
_META_GROUP = re.compile(r"parallel_group\s*[:：]\s*(?P<g>\d+)")


def _iter_slice_sections(text: str):
    matches = list(_SLICE_HEADER.finditer(text))
    for i, m in enumerate(matches):
        start = m.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        yield text[start:end], m.groupdict()


# ─── Field-level extraction ──────────────────────────────────────────────────
def _parse_slice(slice_text: str, header: dict) -> SliceSpec:
    spec = SliceSpec(
        slice_id=int(header["sid"]),
        title=header["title"].strip(),
    )
    meta = header.get("meta") or ""
    pm = _META_PRIORITY.search(meta)
    if pm:
        spec.priority = pm.group("p")
    gm = _META_GROUP.search(meta)
    if gm:
        spec.parallel_group = int(gm.group("g"))

    # New-style one-line header fields. Two accepted anchors (priority was dropped 2026-08):
    #   `parallel_group: 5 | complexity: complex`                     (current; oversized 字段 2026-08 废除, 旧产物含之亦容忍)
    #   `priority: P0 | parallel_group: 5 | complexity: complex | ...` (legacy)
    if hl_m := re.search(r"^(?:priority|parallel_group)\s*[:：][^\n]*$", slice_text, re.MULTILINE):
        hl = hl_m.group(0)
        if m := re.search(r"priority\s*[:：]\s*([A-Z]\d)", hl):
            spec.priority = m.group(1)
        if m := re.search(r"parallel_group\s*[:：]\s*(\d+)", hl):
            spec.parallel_group = int(m.group(1))
        if m := re.search(r"complexity\s*[:：]\s*(\w+)", hl):
            spec.complexity = m.group(1)

    # Simple top-of-section fields
    if m := re.search(r"^complexity\s*[:：]\s*(\w+)", slice_text, re.MULTILINE):
        spec.complexity = m.group(1).strip()
    if m := re.search(r"^depends_on\s*[:：]\s*\[(.+?)\]", slice_text, re.MULTILINE):
        spec.depends_on = [x.strip() for x in m.group(1).split(",") if x.strip()]
    if m := re.search(r"^detail\s*[:：]\s*(\S+)", slice_text, re.MULTILINE):
        spec.detail = m.group(1).strip()
    if m := re.search(
        r"^(?:source_anchors_ref|android_source_anchors_ref)\s*[:：]\s*\{(?P<body>[^}]*)\}",
        slice_text, re.MULTILINE,
    ):
        ref: dict = {}
        for part in m.group("body").split(","):
            if ":" in part:
                k, v = part.split(":", 1)
                ref[k.strip()] = v.strip().strip('"')
        spec.anchors_ref = ref

    spec.android_source_anchors = _parse_anchors(slice_text)
    spec.placeholders_planned = _parse_placeholders_planned(slice_text)
    spec.integration_points = _parse_integration_points(slice_text)
    spec.wires, _embed_wires = _parse_wires(slice_text)
    spec.modifies_files, spec.cross_slice_edits = _parse_modifies_files(slice_text)
    # Unified ledger: embed wires (from `wires:`) + legacy `parent_placeholder_replacement:` block.
    # Both feed C4; WireEntry/ParentReplacement/C1/C4 are unchanged.
    spec.parent_placeholder_replacement = _parse_parent_replacement(slice_text) + _embed_wires

    return spec


def _parse_anchors(slice_text: str) -> list[dict]:
    block = _yaml_block(slice_text, "source_anchors") or _yaml_block(slice_text, "android_source_anchors")
    if not block:
        return []
    anchors: list[dict] = []
    current: dict = {}
    for line in block.splitlines():
        s = line.strip()
        if s.startswith("- role:"):
            if current:
                anchors.append(current)
            current = {"role": s.split(":", 1)[1].strip()}
        elif s.startswith("path:"):
            current["path"] = s.split(":", 1)[1].strip().strip('"')
        elif s.startswith("role:") and "role" not in current:
            current["role"] = s.split(":", 1)[1].strip()
    if current:
        anchors.append(current)
    return anchors


def _parse_placeholders_planned(slice_text: str) -> list[dict]:
    # Quick path: `placeholders_planned: []`
    if re.search(r"^placeholders_planned\s*[:：]\s*\[\s*\]", slice_text, re.MULTILINE):
        return []
    block = _yaml_block(slice_text, "placeholders_planned")
    if not block:
        return []
    out = []
    current: dict = {}
    for line in block.splitlines():
        s = line.strip()
        if s.startswith("- id:"):
            if current:
                out.append(current)
            current = {"id": s.split(":", 1)[1].strip()}
        elif ":" in s and not s.startswith("#"):
            k, v = s.split(":", 1)
            current[k.strip()] = v.strip()
    if current:
        out.append(current)
    return out


_IP_ENTRY = re.compile(
    r"^\s{2,}-\s+(?:\[(?P<check>[ xX])\]\s+)?(?P<desc>.+?)\s*\n"
    r"(?P<extras>(?:\s{4,}.+\n?)*)",
    re.MULTILINE,
)
_EVIDENCE_LINE = re.compile(r"^\s{4,}evidence\s*[:：]\s*(?P<text>.+?)\s*$", re.MULTILINE)
_LOCAL_TOKEN = re.compile(r"\.(?P<token>[A-Za-z_][A-Za-z0-9_]*)")
_TARGET_CLASS = re.compile(r"\b(?P<cls>[A-Z][A-Za-z0-9_]*)(?:\.\w+|\.|$|\s)")


def _parse_integration_points(slice_text: str) -> list[IntegrationPoint]:
    block = _yaml_block(slice_text, "integration_points")
    if not block:
        return []
    out: list[IntegrationPoint] = []
    for em in _IP_ENTRY.finditer("integration_points:\n" + block):
        desc = em.group("desc").strip()
        extras = em.group("extras") or ""
        handler, target = _split_arrow(desc)
        ev_m = _EVIDENCE_LINE.search(extras)
        evidence = ev_m.group("text").strip() if ev_m else ""

        ht = _LOCAL_TOKEN.findall(handler)
        target_class_m = _TARGET_CLASS.search(target) if target else None

        out.append(IntegrationPoint(
            description=desc,
            handler_text=handler,
            target_text=target,
            handler_local=ht[-1] if ht else None,
            target_class=target_class_m.group("cls") if target_class_m else None,
            evidence_raw=evidence,
            checked=(em.group("check") or "").lower() == "x",
        ))
    return out


def _split_arrow(s: str) -> tuple[str, str]:
    for arrow in ("←", "→", " <- ", " -> "):
        if arrow in s:
            parts = s.split(arrow, 1)
            return parts[0].strip(), parts[1].strip()
    return s.strip(), ""


def _parse_wires(slice_text: str) -> tuple[list[WireEntry], list[ParentReplacement]]:
    """Unified wiring ledger. Each `wires:` entry is one of:
      - VM wire   : `- page: X` + `viewmodel: Y`                 → WireEntry      (C1)
      - embed wire: `- page: X` + `slot:` + `embed:`/`replace_with:` [+ `resolve_by:`]
                                                                  → ParentReplacement (C4)
    Kind is inferred from which target field is present (viewmodel vs slot/embed);
    no manual `kind` is written. Embed wires are returned separately so the caller
    can merge them with any legacy `parent_placeholder_replacement:` block.
    """
    block = _yaml_block(slice_text, "wires")
    if not block or block.strip() in ("", "[]"):
        return [], []
    vm_wires: list[WireEntry] = []
    embeds: list[ParentReplacement] = []
    current: dict = {}

    def _flush() -> None:
        if current.get("page") and current.get("viewmodel"):
            vm_wires.append(WireEntry(page=current["page"], viewmodel=current["viewmodel"]))
        elif current.get("page") and (current.get("slot") or current.get("replace_with")):
            embeds.append(ParentReplacement(
                parent_file=current["page"],
                builder_name=current.get("slot", ""),
                replace_with=current.get("replace_with", ""),
                resolve_by=current.get("resolve_by", ""),
            ))

    for line in block.splitlines():
        s = line.strip()
        if s.startswith("- page:"):
            _flush()
            current = {"page": s.split(":", 1)[1].strip()}
        elif s.startswith("viewmodel:"):
            current["viewmodel"] = s.split(":", 1)[1].strip()
        elif s.startswith("page:"):
            current["page"] = s.split(":", 1)[1].strip()
        elif s.startswith("slot:") or s.startswith("builder:") or s.startswith("builder_name:"):
            current["slot"] = s.split(":", 1)[1].strip()
        elif s.startswith("embed:") or s.startswith("replace_with:"):
            current["replace_with"] = s.split(":", 1)[1].strip()
        elif s.startswith("resolve_by:"):
            current["resolve_by"] = s.split(":", 1)[1].strip()
    _flush()
    return vm_wires, embeds


_CROSS_SLICE_FILE = re.compile(r"^\s+-\s+file\s*[:：]\s*(?P<f>.+)$", re.MULTILINE)
_CROSS_SLICE_HANDLER = re.compile(r"^\s+handler\s*[:：]\s*(?P<h>.+)$", re.MULTILINE)
_CROSS_SLICE_RESOLVE = re.compile(r"^\s+resolve_by\s*[:：]\s*(?P<r>.+)$", re.MULTILINE)


def _parse_modifies_files(slice_text: str) -> tuple[list[str], list[CrossSliceEdit]]:
    block = _yaml_block(slice_text, "modifies_files")
    files: list[str] = []
    cross: list[CrossSliceEdit] = []
    if not block:
        return files, cross

    if block.strip() == "[]":
        return files, cross

    # Files appear as `  - <path>` lines; cross_slice_edits as nested block
    in_cross = False
    cross_acc: dict = {}
    for line in block.splitlines():
        s_raw = line.rstrip()
        s = s_raw.strip()
        if s.startswith("cross_slice_edits"):
            in_cross = True
            continue
        if in_cross:
            if s.startswith("- file:"):
                if cross_acc:
                    cross.append(CrossSliceEdit(**cross_acc))
                cross_acc = {"file": s.split(":", 1)[1].strip(), "handler": "", "resolve_by": "", "slot": ""}
            elif s.startswith("handler:"):
                cross_acc["handler"] = s.split(":", 1)[1].strip()
            elif s.startswith("resolve_by:"):
                cross_acc["resolve_by"] = s.split(":", 1)[1].strip()
            elif s.startswith("slot:"):
                cross_acc["slot"] = s.split(":", 1)[1].strip()
        else:
            if s.startswith("- "):
                files.append(s[2:].strip().split("#", 1)[0].strip())

    if cross_acc:
        cross.append(CrossSliceEdit(**cross_acc))
    return files, cross


def _parse_parent_replacement(slice_text: str) -> list[ParentReplacement]:
    block = _yaml_block(slice_text, "parent_placeholder_replacement")
    if not block or block.strip() in ("", "[]"):
        return []
    out: list[ParentReplacement] = []
    current = {}
    for line in block.splitlines():
        s = line.strip()
        if s.startswith("- parent_file:"):
            if current:
                out.append(ParentReplacement(**current))
            current = {
                "parent_file": s.split(":", 1)[1].strip(),
                "builder_name": "",
                "replace_with": "",
                "resolve_by": "",
            }
        elif s.startswith("builder_name:"):
            current["builder_name"] = s.split(":", 1)[1].strip()
        elif s.startswith("replace_with:"):
            current["replace_with"] = s.split(":", 1)[1].strip()
        elif s.startswith("resolve_by:"):
            current["resolve_by"] = s.split(":", 1)[1].strip()
    if current:
        out.append(ParentReplacement(**current))
    return out


# ─── Generic YAML-block extractor ─────────────────────────────────────────────
def _yaml_block(text: str, field_name: str) -> Optional[str]:
    """Extract the text under a top-level field name until the next blank-line
    boundary that returns to column-0 content (or a markdown heading/list).

    Important: use `[ \\t]*` (not `\\s*`) around the colon to avoid consuming
    newlines — `\\s*` would let the regex eat the line break and absorb the
    first body line as part of the inline value.
    """
    pattern = (
        rf"^{re.escape(field_name)}[ \t]*[:：][ \t]*(?P<inline>[^\n]*)\n"
        rf"(?P<body>(?:[ \t]+[^\n]*\n?)*)"
    )
    m = re.search(pattern, text, re.MULTILINE)
    if not m:
        return None
    inline = (m.group("inline") or "").strip()
    body = m.group("body") or ""
    # Trailing-comment-only inline (e.g. `placeholders_planned: []     # comment`)
    # → strip the comment so the caller sees the actual scalar.
    if inline:
        # remove trailing markdown-style comment
        inline = re.sub(r"\s+#.*$", "", inline).rstrip()
    if inline and not body.strip():
        # field has inline value like `[]` — caller handles it
        return inline
    if inline and inline not in ("[]", "{}"):
        # mixed: inline + body (rare) — caller will see body; we prepend inline
        return inline + "\n" + body
    return body
