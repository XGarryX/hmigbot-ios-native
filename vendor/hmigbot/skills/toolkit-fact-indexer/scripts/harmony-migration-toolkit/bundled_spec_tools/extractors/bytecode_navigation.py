"""
bytecode_navigation.py
从编译后的 .class 文件字节码中提取导航关系。

通用方案 — 不依赖正则匹配源码格式，直接分析 JVM 字节码中的：
  - new Intent → startActivity / startActivityForResult  (Activity 跳转)
  - new XxxDialog → <init>                               (Dialog 弹出)
  - adapter 字段赋值                                      (Adapter-Host 绑定)
  - R$id 字段引用                                         (菜单/CAB 项)

用法（被 navigation_extractor.py 调用）：
  from extractors.bytecode_navigation import extract_edges_from_classes
  edges = extract_edges_from_classes(class_dir)
"""

import re
from pathlib import Path
from extractors.class_parser import parse_class, extract_invocations


def _short_class(full_name: str) -> str:
    """com.simplemobiletools.gallery.pro.activities.MainActivity → MainActivity"""
    return full_name.rsplit(".", 1)[-1] if "." in full_name else full_name


def _is_activity(name: str) -> bool:
    return "Activity" in name


def _is_dialog(name: str) -> bool:
    return "Dialog" in name or "BottomSheet" in name


def _extract_intent_targets_in_code(pool, code: bytes) -> list[str]:
    """从字节码中提取 Intent 目标 Activity class。

    模式 1: new Intent(this, XxxActivity.class) → startActivity
      字节码: new Intent → ldc XxxActivity.class → invokespecial Intent.<init> → ... → startActivity

    模式 2: new Intent → addAction → startActivity (隐式)
    """
    targets = []
    if not code:
        return targets

    invocs = extract_invocations(pool, code)
    has_start = any(
        i.get("name") in ("startActivity", "startActivityForResult")
        for i in invocs
    )
    if not has_start:
        return targets

    # 收集 ldc_class 加载的 Activity/Fragment class
    for i in invocs:
        if i.get("opcode") == "ldc_class":
            short = _short_class(i.get("class", ""))
            if "$" in short:
                continue
            if _is_activity(short) or "Fragment" in short:
                targets.append(short)

    # 收集 new XxxActivity (less common but possible)
    for i in invocs:
        if i.get("opcode") == "new":
            short = _short_class(i.get("class", ""))
            if "$" in short:
                continue
            if _is_activity(short) or "Fragment" in short:
                targets.append(short)

    return targets


def _extract_dialog_creations(pool, code: bytes) -> list[str]:
    """提取 new XxxDialog(...) 调用。"""
    dialogs = []
    if not code:
        return dialogs

    invocs = extract_invocations(pool, code)
    for i in invocs:
        if i["opcode"] == "new":
            short = _short_class(i.get("class", ""))
            if _is_dialog(short):
                dialogs.append(short)
    return dialogs


def _extract_method_calls(pool, code: bytes) -> list[dict]:
    """提取所有方法调用（invokevirtual/invokestatic/invokespecial）。"""
    if not code:
        return []
    invocs = extract_invocations(pool, code)
    return [
        {"class": _short_class(i.get("class", "")), "name": i["name"]}
        for i in invocs
        if i["opcode"] in ("0xb6", "0xb7", "0xb8")
    ]


def _get_host_class(class_name: str) -> str:
    """EditActivity$setupAspectRatioButtons$5$1 → EditActivity"""
    return class_name.split("$")[0]


def _scan_adapter_bindings(all_classes: dict) -> dict[str, list[str]]:
    """扫描所有 class 文件，找到 XxxAdapter 构造调用，绑定到 host class。

    字节码中体现为：
      new com.simplemobiletools.gallery.pro.adapters.MediaAdapter
      invokespecial MediaAdapter.<init>
    出现在某个 Activity/Fragment 的方法中。
    """
    adapter_to_hosts: dict[str, list[str]] = {}

    for class_file, cls_info in all_classes.items():
        host = _short_class(_get_host_class(cls_info["class"]))
        for m in cls_info["methods"]:
            if not m["code"]:
                continue
            invocs = extract_invocations(cls_info["pool"], m["code"])
            for i in invocs:
                if i["opcode"] == "new":
                    short = _short_class(i.get("class", ""))
                    if short.endswith("Adapter"):
                        adapter_to_hosts.setdefault(short, []).append(host)

    for k in adapter_to_hosts:
        adapter_to_hosts[k] = list(set(adapter_to_hosts[k]))

    return adapter_to_hosts


def _trace_method_chain(
    all_classes: dict,
    host_class: str,
    method_name: str,
    depth: int = 3,
) -> list[dict]:
    """追踪方法调用链，找到间接的 startActivity / Dialog 调用。

    例：MainActivity.itemClicked() → handleLockedFolderOpening(lambda) → Intent(MediaActivity)
    字节码中 lambda 调用生成了内部类 MainActivity$itemClicked$1。
    """
    results = []
    if depth <= 0:
        return results

    host_short = _short_class(host_class)

    # 先在 host class 中找方法
    cls_info = None
    for cf, ci in all_classes.items():
        if _short_class(_get_host_class(ci["class"])) == host_short:
            if ci["class"] == host_class or ci["class"].startswith(host_class + "$"):
                cls_info = ci
                break

    if not cls_info:
        # 尝试找主 class
        for cf, ci in all_classes.items():
            if _short_class(ci["class"]) == host_short and "$" not in ci["class"]:
                cls_info = ci
                break

    if not cls_info:
        return results

    for m in cls_info["methods"]:
        if m["name"] != method_name:
            continue
        if not m["code"]:
            continue

        targets = _extract_intent_targets_in_code(cls_info["pool"], m["code"])
        for t in targets:
            results.append({"target": t, "type": "activity", "via": method_name})

        dialogs = _extract_dialog_creations(cls_info["pool"], m["code"])
        for d in dialogs:
            results.append({"target": d, "type": "dialog", "via": method_name})

    # 追踪 lambda / 内部类
    lambda_pattern = re.compile(
        re.escape(host_short) + r"\$" + re.escape(method_name) + r"\$\d+$"
    )
    for cf, ci in all_classes.items():
        inner_name = _short_class(ci["class"])
        inner_host = _get_host_class(ci["class"])
        if _short_class(inner_host) != host_short:
            continue

        # 匹配 MainActivity$itemClicked$1 这种模式
        if method_name not in inner_name:
            continue

        for m in ci["methods"]:
            if m["name"].startswith("access$"):
                continue
            if not m["code"]:
                continue

            targets = _extract_intent_targets_in_code(ci["pool"], m["code"])
            for t in targets:
                results.append({"target": t, "type": "activity", "via": f"{method_name}→lambda"})

            dialogs = _extract_dialog_creations(ci["pool"], m["code"])
            for d in dialogs:
                results.append({"target": d, "type": "dialog", "via": f"{method_name}→lambda"})

            # 继续追踪间接调用
            calls = _extract_method_calls(ci["pool"], m["code"])
            for c in calls:
                if c["name"] in ("startActivity", "startActivityForResult"):
                    continue
                if c["class"] == host_short:
                    sub = _trace_method_chain(all_classes, c["class"], c["name"], depth - 1)
                    results.extend(sub)

    return results


def extract_edges_from_classes(class_dir: str) -> list[dict]:
    """主入口：从 build class 目录提取所有导航边。"""
    root = Path(class_dir)
    if not root.exists():
        return []

    # 1. 解析所有 .class 文件
    all_classes: dict[str, dict] = {}
    for cf in root.rglob("*.class"):
        try:
            cls = parse_class(cf)
            all_classes[str(cf)] = cls
        except Exception:
            continue

    # 2. 提取直接导航边（startActivity + Dialog）
    edges = []
    seen = set()

    for cf, cls_info in all_classes.items():
        full_class = cls_info["class"]
        if "$" in _short_class(full_class):
            continue  # 跳过内部类（会在 trace_method_chain 中处理）

        host = _short_class(full_class)
        if not (_is_activity(host) or "Fragment" in host):
            continue

        for m in cls_info["methods"]:
            if not m["code"]:
                continue
            method_name = m["name"]

            targets = _extract_intent_targets_in_code(cls_info["pool"], m["code"])
            for t in targets:
                key = (host, t, method_name)
                if key not in seen:
                    seen.add(key)
                    edges.append({
                        "from": host,
                        "to": t,
                        "type": "activity",
                        "via": "startActivity",
                        "trigger": f"fn: {method_name}",
                        "source": "bytecode",
                    })

            dialogs = _extract_dialog_creations(cls_info["pool"], m["code"])
            for d in dialogs:
                key = (host, d, method_name)
                if key not in seen:
                    seen.add(key)
                    edges.append({
                        "from": host,
                        "to": d,
                        "type": "dialog",
                        "via": "Dialog()",
                        "trigger": f"fn: {method_name}",
                        "source": "bytecode",
                    })

    # 3. 追踪间接调用（lambda / 内部类中的导航）
    for cf, cls_info in all_classes.items():
        full_class = cls_info["class"]
        if "$" in _short_class(full_class):
            continue
        host = _short_class(full_class)
        if not (_is_activity(host) or "Fragment" in host):
            continue

        for m in cls_info["methods"]:
            if not m["code"]:
                continue
            calls = _extract_method_calls(cls_info["pool"], m["code"])
            for c in calls:
                if c["class"] == host and c["name"] not in (
                    "startActivity", "startActivityForResult", "finish", "<init>"
                ):
                    chain = _trace_method_chain(all_classes, full_class, c["name"], depth=2)
                    for r in chain:
                        key = (host, r["target"], m["name"])
                        if key not in seen:
                            seen.add(key)
                            edges.append({
                                "from": host,
                                "to": r["target"],
                                "type": r["type"],
                                "via": f"fn: {m['name']}→{c['name']}",
                                "trigger": f"fn: {m['name']}",
                                "source": "bytecode_indirect",
                            })

    # 4. Adapter-Host 绑定
    adapter_bindings = _scan_adapter_bindings(all_classes)
    adapter_classes = set()
    for cf, cls_info in all_classes.items():
        short = _short_class(cls_info["class"])
        if short.endswith("Adapter"):
            adapter_classes.add(short)

    # 找 adapter 的出边（adapter 方法中的导航调用）
    adapter_edges: dict[str, list[dict]] = {}
    for cf, cls_info in all_classes.items():
        short = _short_class(cls_info["class"])
        if short not in adapter_classes:
            continue

        for m in cls_info["methods"]:
            if not m["code"]:
                continue
            targets = _extract_intent_targets_in_code(cls_info["pool"], m["code"])
            for t in targets:
                adapter_edges.setdefault(short, []).append({
                    "target": t, "type": "activity", "method": m["name"]
                })

            dialogs = _extract_dialog_creations(cls_info["pool"], m["code"])
            for d in dialogs:
                adapter_edges.setdefault(short, []).append({
                    "target": d, "type": "dialog", "method": m["name"]
                })

    # 将 adapter 的边绑定到 host
    for adapter_name, hosts in adapter_bindings.items():
        for host in hosts:
            for ae in adapter_edges.get(adapter_name, []):
                key = (host, ae["target"], f"adapter:{adapter_name}")
                if key not in seen:
                    seen.add(key)
                    edges.append({
                        "from": host,
                        "to": ae["target"],
                        "type": ae["type"],
                        "via": f"adapter:{adapter_name}",
                        "trigger": f"adapter:{adapter_name}:{ae['method']}",
                        "source": "bytecode_adapter",
                    })

    return edges


def find_class_dir(project_root: str) -> str | None:
    """在 Android 项目中定位 build class 目录。"""
    root = Path(project_root)
    candidates = [
        root / "app" / "build" / "tmp" / "kotlin-classes",
        root / "app" / "build" / "intermediates" / "javac",
    ]
    for c in candidates:
        if c.exists():
            for variant in c.iterdir():
                if variant.is_dir():
                    return str(variant)
    # fallback: search for any directory containing .class files under build/
    build_dirs = list(root.rglob("build"))
    for bd in build_dirs:
        class_files = list(bd.rglob("*.class"))
        if class_files:
            return str(bd)
    return None
