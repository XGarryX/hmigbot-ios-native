#!/usr/bin/env python3
"""Multica PR 机器校验（MC-01 ~ MC-16）。

实现 docs/Multica_Submission_Spec.md §3 机器校验契约：
- error 级不通过 → exit 1（配合 branch protection 阻断 merge）
- warning 级 → 仅提示（GitHub annotation + job summary）

输入：
- 环境变量 PR_BODY（workflow 注入）或 --body-file <path>（本地调试）
- 环境变量 GITHUB_REPOSITORY（owner/repo，MC-05 用；缺失时跳过触发仓配对检查）

输出：逐条 [MC-xx][LEVEL] 结果；写入 GITHUB_STEP_SUMMARY（若存在）。
"""

import argparse
import os
import re
import sys

try:
    import yaml
except ImportError:  # pragma: no cover
    print("::error::PyYAML not installed (pip install pyyaml)")
    sys.exit(2)

KNOWN_STAGES = [
    "a2h-init", "a2h-build", "a2h-spec", "a2h-plan",
    "a2h-execute", "a2h-verify", "a2h-retrospect",
]
REQUIRED_GROUPS = [
    "validation", "test_app",
    "deveco_project", "migration", "runtime",
]
# 路径类字段（local_workspace / test_app.local_path / migration.decisions_path）
# 不再要求渲染：由 Instruction 路径规则在执行侧自动派生；
# 显式给出时仍校验格式（MC-10 / MC-11）。
REQUIRED_FIELDS = {
    "validation": ["profile", "platform", "test_date"],
    "test_app": ["url", "app_name"],
    "deveco_project": ["project_name", "sdk", "created_by"],
    "migration": ["stages"],
    "runtime": ["launch_mode", "model", "effort"],
}
PROFILE_ABBREV = {"migbot": "cc", "migbot_codex": "codex"}
REPO_PROFILE = {
    "hmigbot": "migbot",
    "migbot": "migbot",              # renamed 2026-08; kept for replays on old slug
    "migbot-runtime-src": "migbot",
    "hmigbot-codex": "migbot_codex",
    "migbot-codex": "migbot_codex",  # renamed 2026-08; kept for replays on old slug
    "migbot-codex-runtime-src": "migbot_codex",
}
FORBIDDEN_TOP_GROUPS = {"candidate", "mode"}
# 已注册评测包的 App（规范名/简称小写；与 migbot-utils AutoEval/gt_eval_registry.json 同步维护）
EVAL_REGISTRY_APPS = {"antennapod", "aippt"}
FORBIDDEN_KEYS = {"sha", "commit", "validation_run_id", "migbot_version"}
GITHUB_URL_RE = re.compile(
    r"^https://github\.com/[^/\s]+/[^/\s]+(?:/tree/[^/\s]+(?:/\S+)?)?/?$"
)
# 非 github.com 的内网 git 托管（如 AIPPT 内网仓）：宽松要求 https + 至少 /owner/repo
GENERIC_URL_RE = re.compile(r"^https://[^/\s]+/[^/\s]+/\S+$")
# 执行机本地路径：~/、POSIX 绝对路径、Windows 盘符（D:\ 或 D:/）、UNC（\\host\share）
LOCAL_PATH_RE = re.compile(r"^(~/|/|[A-Za-z]:[/\\]|\\\\)")
PREAMBLE_IDENTIFIERS = [
    "hmigbot-CodeX", "migbot-CodeX", "migbot_codex", "migbot-codex-runtime-src",
    "migbot-runtime-src", "Validation-Profile",
]

results = []  # (mc_id, level, ok, message)


def report(mc_id, level, ok, message):
    results.append((mc_id, level, ok, message))


def find_multica_blocks(body):
    """返回所有首行为 `# multica` 的 fenced 代码块内容列表。

    fence 的 info string 任意（容忍被渲染改写成 yaml_xxx 等）。
    """
    blocks = []
    lines = body.replace("\r\n", "\n").split("\n")
    i = 0
    while i < len(lines):
        stripped = lines[i].strip()
        m = re.match(r"^(`{3,}|~{3,})", stripped)
        if m:
            fence = m.group(1)[0] * len(m.group(1))
            content = []
            i += 1
            while i < len(lines):
                inner = lines[i].strip()
                if re.match(r"^%s+\s*$" % re.escape(fence[0] * 3), inner) and \
                        inner.count(fence[0]) >= len(fence):
                    break
                content.append(lines[i])
                i += 1
            body_lines = [l for l in content if l.strip()]
            if body_lines and body_lines[0].strip() == "# multica":
                blocks.append("\n".join(content))
        i += 1
    return blocks


def iter_scalars(node, path="$"):
    if isinstance(node, dict):
        for k, v in node.items():
            yield from iter_scalars(v, f"{path}.{k}")
    elif isinstance(node, list):
        for idx, v in enumerate(node):
            yield from iter_scalars(v, f"{path}[{idx}]")
    else:
        yield path, node


def iter_keys(node, path="$"):
    if isinstance(node, dict):
        for k, v in node.items():
            yield f"{path}.{k}", str(k)
            yield from iter_keys(v, f"{path}.{k}")
    elif isinstance(node, list):
        for idx, v in enumerate(node):
            yield from iter_keys(v, f"{path}[{idx}]")


def get(data, group, field):
    g = data.get(group)
    if isinstance(g, dict):
        return g.get(field)
    return None


def as_str(v):
    return "" if v is None else str(v).strip()


def check(body, repo_name):
    # ---- MC-01 块存在且唯一、可解析 ----
    blocks = find_multica_blocks(body or "")
    if len(blocks) != 1:
        report("MC-01", "error", False,
               f"需要恰好一个 `# multica` yaml 块，实际 {len(blocks)} 个")
        return None
    try:
        data = yaml.safe_load(blocks[0])
    except yaml.YAMLError as e:
        report("MC-01", "error", False, f"YAML 解析失败：{e}")
        return None
    if not isinstance(data, dict):
        report("MC-01", "error", False, "块内容不是 YAML mapping")
        return None
    report("MC-01", "error", True, "multica 块存在且可解析")

    # ---- MC-02 六组齐全 ----
    missing = [g for g in REQUIRED_GROUPS
               if not isinstance(data.get(g), dict)]
    report("MC-02", "error", not missing,
           "五个语义组齐全" if not missing else f"缺组：{missing}")

    # ---- MC-03 必填字段非空 ----
    empty = []
    for grp, fields in REQUIRED_FIELDS.items():
        for f in fields:
            v = get(data, grp, f)
            if v is None or (isinstance(v, str) and not v.strip()) or \
                    (isinstance(v, list) and not v):
                empty.append(f"{grp}.{f}")
    report("MC-03", "error", not empty,
           "必填字段齐全" if not empty else f"缺失/为空：{empty}")

    profile = as_str(get(data, "validation", "profile"))
    platform = as_str(get(data, "validation", "platform"))
    test_date = as_str(get(data, "validation", "test_date"))
    release_tag = as_str(get(data, "validation", "release_tag"))
    app_name = as_str(get(data, "test_app", "app_name"))
    url = as_str(get(data, "test_app", "url"))
    local_path = as_str(get(data, "test_app", "local_path"))
    project_name = as_str(get(data, "deveco_project", "project_name"))
    stages = get(data, "migration", "stages") or []
    decisions_path = as_str(get(data, "migration", "decisions_path"))
    policy = as_str(get(data, "migration", "unanswered_policy"))
    launch_mode = as_str(get(data, "runtime", "launch_mode"))
    effort = as_str(get(data, "runtime", "effort"))

    # ---- MC-04 枚举 ----
    enum_errs = []
    if profile not in ("migbot", "migbot_codex"):
        enum_errs.append(f"profile={profile!r}")
    if platform not in ("mac", "windows", "dual"):
        enum_errs.append(f"platform={platform!r}")
    if policy and policy not in ("blocked", "wait_human"):
        enum_errs.append(f"unanswered_policy={policy!r}")  # 可选字段，出现时才校验
    if launch_mode not in ("codex_cli", "codex_app", "claude_code"):
        enum_errs.append(f"launch_mode={launch_mode!r}")
    if effort.lower() == "extrahigh":
        enum_errs.append("effort=extraHigh（非法拼写；合法如 high / xhigh）")
    report("MC-04", "error", not enum_errs,
           "枚举取值合法" if not enum_errs else f"非法枚举：{enum_errs}")

    # ---- MC-05 Profile 一致性 ----
    errs = []
    if repo_name:
        expected = REPO_PROFILE.get(repo_name.lower())
        if expected and profile and profile != expected:
            errs.append(f"触发仓 {repo_name} 要求 profile={expected}，实际 {profile}")
    if profile == "migbot_codex" and launch_mode not in ("codex_cli", "codex_app"):
        errs.append(f"migbot_codex 要求 launch_mode ∈ codex_cli/codex_app，实际 {launch_mode}")
    if profile == "migbot" and launch_mode != "claude_code":
        errs.append(f"migbot 要求 launch_mode=claude_code，实际 {launch_mode}")
    report("MC-05", "error", not errs,
           "Profile/触发仓/launch_mode 一致" if not errs else "；".join(errs))

    # ---- MC-06 占位符残留 ----
    bad = [p for p, v in iter_scalars(data)
           if isinstance(v, str) and any(c in v for c in "{}<>")]
    report("MC-06", "error", not bad,
           "无占位符残留" if not bad else f"含 {{}}/<> 占位符：{bad}")

    # ---- MC-07 test_date ----
    ok = bool(re.fullmatch(r"\d{3,4}", test_date))
    if ok:
        mm, dd = (int(test_date[:-2]), int(test_date[-2:]))
        ok = 1 <= mm <= 12 and 1 <= dd <= 31
    report("MC-07", "error", ok,
           f"test_date={test_date} 合法" if ok else f"test_date={test_date!r} 不是合法 MMDD")

    # ---- MC-08 app_name ----
    ok = bool(re.fullmatch(r"[a-z0-9]+", app_name))
    report("MC-08", "error", ok,
           f"app_name={app_name} 合规" if ok else f"app_name={app_name!r} 须匹配 ^[a-z0-9]+$")

    # ---- MC-09 project_name 公式 ----
    abbrev = PROFILE_ABBREV.get(profile, "?")
    base = f"{app_name}_v{test_date}_{abbrev}"
    ok = project_name == base or project_name.startswith(base + "_")
    report("MC-09", "error", ok,
           f"project_name={project_name} 符合公式" if ok
           else f"project_name={project_name!r} 应为 {base}[_<后缀>]")

    # ---- MC-10 url / local_path ----
    errs = []
    if url.startswith("https://github.com/"):
        if not GITHUB_URL_RE.match(url):
            errs.append(f"url={url!r} 不符合 github.com repo/tree 形式")
    elif not GENERIC_URL_RE.match(url):
        errs.append(f"url={url!r} 须为 https://<host>/<owner>/<repo> 形式")
    if local_path and not LOCAL_PATH_RE.match(local_path):
        errs.append(f"local_path={local_path!r} 须为 ~/、/、盘符或 UNC 开头的本地路径")
    report("MC-10", "error", not errs,
           "test_app 路径格式合法" if not errs else "；".join(errs))

    # ---- MC-11 stages / decisions_path ----
    errs = []
    if not isinstance(stages, list) or not stages:
        errs.append("migration.stages 须为非空列表")
    if decisions_path and not LOCAL_PATH_RE.match(decisions_path):
        errs.append(f"decisions_path={decisions_path!r} 须为 ~/、/、盘符或 UNC 开头的本地路径")  # 可选，出现时才校验
    report("MC-11", "error", not errs,
           "stages/decisions_path 合法" if not errs else "；".join(errs))

    # ---- MC-12 禁用键 ----
    bad = [g for g in FORBIDDEN_TOP_GROUPS if g in data]
    for path, key in iter_keys(data):
        kl = key.lower()
        if kl in FORBIDDEN_KEYS or kl.startswith("mock"):
            bad.append(path)
    report("MC-12", "error", not bad,
           "无禁用键" if not bad else f"出现禁用键：{bad}")

    # ---- MC-13 未知 stage（warning）----
    unknown = [s for s in stages if s not in KNOWN_STAGES] \
        if isinstance(stages, list) else []
    report("MC-13", "warning", not unknown,
           "stages 均为已知 skill" if not unknown
           else f"未知 stage {unknown}：执行侧可能无法识别，将导致 blocked")

    # ---- MC-14 a2h-verify 模拟器（notice：固定提醒，不计入告警）----
    has_verify = isinstance(stages, list) and "a2h-verify" in stages
    report("MC-14", "notice", True,
           "含 a2h-verify：请确认执行机已开启 Android 与 HarmonyOS 模拟器"
           if has_verify else "不含 a2h-verify")

    # ---- MC-15 导语（warning）----
    pre = (body or "").split("```", 1)[0]
    has_id = any(t in pre for t in PREAMBLE_IDENTIFIERS)
    has_real = "真实迁移" in pre
    ok = has_id and has_real
    report("MC-15", "warning", ok,
           "导语含标识与真实迁移声明" if ok
           else "导语缺失或不完整（推荐在块前声明 Profile 标识与'真实迁移非 Mock'）")

    # ---- MC-16 release_tag（warning）----
    ok = (not release_tag) or release_tag.startswith("v")
    report("MC-16", "warning", ok,
           "release_tag 未渲染或格式正常" if ok
           else f"release_tag={release_tag!r} 不以 v 开头，请核对 Tag 拼写")

    # ---- MC-17 evaluation.gt_eval 枚举（error；组可选，未渲染即 off）----
    evaluation = data.get("evaluation") if isinstance(data.get("evaluation"), dict) else {}
    raw_gt = evaluation.get("gt_eval")
    # YAML 1.1 把裸 off/on/yes/no 解析成布尔（off → False）——归一回字符串，
    # 否则 skill 的默认渲染值 `gt_eval: off` 会被误判非法。生成器渲染带引号，此处兜底手写块。
    if isinstance(raw_gt, bool):
        gt_eval = "off" if raw_gt is False else "on"
    else:
        gt_eval = as_str(raw_gt) or "off"
    ok = gt_eval in ("off", "smoke", "full")
    report("MC-17", "error", ok,
           (f"evaluation.gt_eval={gt_eval}" if "evaluation" in data
            else "evaluation 组未渲染，缺省 off") if ok
           else f"evaluation.gt_eval={gt_eval!r} 非法，应为 off | smoke | full")
    if not ok:
        gt_eval = "off"

    # ---- MC-18 评测包注册（warning）----
    url_seg = url.rstrip("/").split("/")[-1].lower() if url else ""
    registered = bool({url_seg, (app_name or "").lower()} & EVAL_REGISTRY_APPS)
    ok = gt_eval == "off" or registered
    report("MC-18", "warning", ok,
           "未开启评测或 App 已注册评测包" if ok
           else f"gt_eval={gt_eval} 但 App 未注册评测包：执行侧判 not_applicable 跳过"
                "（提示级，不阻断 merge 与本轮任何环节）；改 off 或先补评测 kit 即可消除")

    # ---- MC-19 自动评测就绪提醒（notice：固定提醒，不计入告警）----
    report("MC-19", "notice", True,
           "开启自动评测：请确认执行机鸿蒙模拟器可用、签名 profile 在有效期内"
           if gt_eval != "off" else "未开启自动评测")
    return data


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--body-file", help="本地调试：从文件读 PR body")
    args = ap.parse_args()

    if args.body_file:
        with open(args.body_file, encoding="utf-8") as f:
            body = f.read()
    else:
        body = os.environ.get("PR_BODY", "")

    repo_full = os.environ.get("GITHUB_REPOSITORY", "")
    repo_name = repo_full.split("/")[-1] if repo_full else ""

    check(body, repo_name)

    errors = [r for r in results if r[1] == "error" and not r[2]]
    warnings = [r for r in results if r[1] == "warning" and not r[2]]

    lines = []
    for mc_id, level, ok, msg in results:
        tag = "OK" if ok and level != "notice" else level.upper()
        line = f"[{mc_id}][{tag}] {msg}"
        lines.append(line)
        print(line)
        if level == "notice":
            if "请确认" in msg:
                print(f"::notice title={mc_id}::{msg}")
        elif not ok:
            gh_cmd = "error" if level == "error" else "warning"
            print(f"::{gh_cmd} title={mc_id}::{msg}")

    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_path:
        with open(summary_path, "a", encoding="utf-8") as f:
            f.write("## Multica PR Check\n\n")
            f.write(f"- errors: **{len(errors)}** / warnings: **{len(warnings)}**\n\n")
            f.write("| ID | 级别 | 结果 | 说明 |\n|---|---|---|---|\n")
            for mc_id, level, ok, msg in results:
                esc = msg.replace("|", "\\|")
                mark = "✅" if ok else "❌"
                f.write(f"| {mc_id} | {level} | {mark} | {esc} |\n")

    print(f"\nresult: {len(errors)} error(s), {len(warnings)} warning(s)")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
