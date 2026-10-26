"""
Lightweight Kotlin/Java function symbol and call graph extractor.

This intentionally uses conservative source scanning so the pipeline can emit
stable evidence without adding parser dependencies. The schema is designed so a
future Tree-sitter/Kotlin PSI/JVM implementation can replace the internals while
keeping the same JSON contract.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

try:
    from extractors import ast_index
except Exception:  # pragma: no cover - fallback when imported standalone
    ast_index = None  # type: ignore[assignment]

from extractors import android_project


_PACKAGE_RE = re.compile(r"^\s*package\s+([\w.]+)", re.MULTILINE)
_CLASS_RE = re.compile(r"\b(?:class|object|interface|enum\s+class)\s+([A-Za-z_]\w*)")
_KT_FUN_RE = re.compile(
    r"(?m)^\s*(?:@\w+(?:\([^)]*\))?\s*)*"
    r"(?:(?:public|private|protected|internal|override|open|final|abstract|suspend|inline|tailrec|operator|infix)\s+)*"
    r"fun\s+(?:<[^>\n]+>\s*)?(?:[A-Za-z_]\w*\s*\.\s*)?([A-Za-z_]\w*)\s*\(([^)]*)\)"
)
_JAVA_METHOD_RE = re.compile(
    r"(?m)^\s*(?:@\w+(?:\([^)]*\))?\s*)*"
    r"(?:(?:public|private|protected|static|final|abstract|synchronized|native|override)\s+)*"
    r"(?:[\w$<>\[\].?,]+\s+)+([A-Za-z_]\w*)\s*\(([^)]*)\)\s*(?:throws\s+[\w$.,\s]+)?\s*\{"
)
_CALL_RE = re.compile(r"\b([A-Za-z_]\w*)\s*\(")

_SKIP_CALLS = {
    "if",
    "for",
    "while",
    "when",
    "switch",
    "catch",
    "return",
    "throw",
    "super",
    "this",
    "class",
    "fun",
}


def _line_of(source: str, pos: int) -> int:
    return source[:pos].count("\n") + 1


def _pos_of_line(source: str, line: int) -> int:
    if line <= 1:
        return 0
    pos = 0
    for _ in range(line - 1):
        nxt = source.find("\n", pos)
        if nxt == -1:
            return len(source)
        pos = nxt + 1
    return pos


def _package_name(source: str) -> str:
    m = _PACKAGE_RE.search(source)
    return m.group(1) if m else ""


def _nearest_class(source: str, pos: int, fallback: str) -> str:
    cls = fallback
    for m in _CLASS_RE.finditer(source, 0, pos):
        cls = m.group(1)
    return cls


def _find_block_end(source: str, start_pos: int) -> int:
    open_pos = source.find("{", start_pos)
    if open_pos == -1:
        line_end = source.find("\n", start_pos)
        return len(source) if line_end == -1 else line_end
    depth = 0
    for i in range(open_pos, len(source)):
        ch = source[i]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return i + 1
    return len(source)


def _lang_for(path: Path) -> str:
    if path.suffix == ".kt":
        return "kotlin"
    if path.suffix == ".java":
        return "java"
    return path.suffix.lstrip(".")


def _symbol_id(package: str, class_name: str, function_name: str, signature: str) -> str:
    owner = ".".join(x for x in (package, class_name) if x)
    arity = 0 if not signature.strip() else len([p for p in signature.split(",") if p.strip()])
    return f"fn:{owner}.{function_name}/{arity}" if owner else f"fn:{function_name}/{arity}"


def _source_files(root: Path) -> list[Path]:
    return android_project.source_files(root)


def _rel_path(path: Path, root: Path, file_prefix: str = "") -> str:
    rel = path.relative_to(root).as_posix()
    return f"{file_prefix}/{rel}" if file_prefix else rel


def extract_symbols(project_root: str, file_prefix: str = "") -> dict[str, Any]:
    if ast_index is not None:
        try:
            index = ast_index.build_project_index(project_root, file_prefix=file_prefix)
            if index.ast_available:
                return ast_index.symbols_payload(index)
        except Exception:
            pass

    root = Path(project_root)
    symbols: list[dict[str, Any]] = []
    for src_path in _source_files(root):
        try:
            source = src_path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        package = _package_name(source)
        fallback_class = src_path.stem
        rel = _rel_path(src_path, root, file_prefix)
        fun_re = _KT_FUN_RE if src_path.suffix == ".kt" else _JAVA_METHOD_RE
        for m in fun_re.finditer(source):
            function_name = m.group(1)
            signature = " ".join((m.group(2) or "").split())
            class_name = _nearest_class(source, m.start(), fallback_class)
            end_pos = _find_block_end(source, m.end())
            start_line = _line_of(source, m.start())
            end_line = _line_of(source, end_pos)
            symbol_id = _symbol_id(package, class_name, function_name, signature)
            symbols.append(
                {
                    "symbol_id": symbol_id,
                    "kind": "function",
                    "language": _lang_for(src_path),
                    "package": package,
                    "class_name": class_name,
                    "function_name": function_name,
                    "signature": signature,
                    "file": rel,
                    "start_line": start_line,
                    "end_line": end_line,
                    "confidence": "regex",
                }
            )
    symbols.sort(key=lambda s: (s["file"], s["start_line"], s["symbol_id"]))
    return {
        "schema_version": "1.0",
        "symbols": symbols,
        "stats": {
            "source_files_scanned": len(_source_files(root)),
            "symbol_count": len(symbols),
        },
    }


def _symbol_for_call(caller: dict[str, Any], name: str, by_name: dict[str, list[dict[str, Any]]]) -> tuple[str, str]:
    candidates = by_name.get(name) or []
    if not candidates:
        return "", "unresolved"
    same_class = [s for s in candidates if s.get("class_name") == caller.get("class_name")]
    if len(same_class) == 1:
        return str(same_class[0]["symbol_id"]), "regex_same_class"
    if len(candidates) == 1:
        return str(candidates[0]["symbol_id"]), "regex_unique_name"
    return "", "ambiguous"


def build_call_graph(project_root: str, symbols_payload: dict[str, Any] | None = None, file_prefix: str = "") -> dict[str, Any]:
    if ast_index is not None:
        try:
            index = ast_index.build_project_index(project_root, file_prefix=file_prefix)
            if index.ast_available:
                return ast_index.call_graph_payload(index)
        except Exception:
            pass

    root = Path(project_root)
    payload = symbols_payload or extract_symbols(project_root, file_prefix=file_prefix)
    symbols = list(payload.get("symbols") or [])
    by_name: dict[str, list[dict[str, Any]]] = {}
    by_file: dict[str, list[dict[str, Any]]] = {}
    for sym in symbols:
        by_name.setdefault(str(sym.get("function_name")), []).append(sym)
        by_file.setdefault(str(sym.get("file")), []).append(sym)

    calls: list[dict[str, Any]] = []
    unresolved: list[dict[str, Any]] = []
    seen_calls: set[tuple[str, str, int, str]] = set()
    for src_path in _source_files(root):
        try:
            source = src_path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        rel = _rel_path(src_path, root, file_prefix)
        for caller in by_file.get(rel, []):
            start_pos = _pos_of_line(source, int(caller.get("start_line", 1)))
            end_pos = _pos_of_line(source, int(caller.get("end_line", caller.get("start_line", 1))) + 1)
            body = source[start_pos:end_pos]
            first_newline = body.find("\n")
            search_offset = start_pos + (first_newline + 1 if first_newline != -1 else 0)
            search_body = source[search_offset:end_pos]
            for m in _CALL_RE.finditer(search_body):
                callee_name = m.group(1)
                if callee_name in _SKIP_CALLS or callee_name == caller.get("function_name"):
                    continue
                call_pos = search_offset + m.start()
                call_line = _line_of(source, call_pos)
                to_symbol, confidence = _symbol_for_call(caller, callee_name, by_name)
                if to_symbol:
                    key = (str(caller["symbol_id"]), to_symbol, call_line, callee_name)
                    if key not in seen_calls:
                        seen_calls.add(key)
                        calls.append(
                            {
                                "from_symbol_id": caller["symbol_id"],
                                "to_symbol_id": to_symbol,
                                "callee_name": callee_name,
                                "callsite_file": rel,
                                "callsite_line": call_line,
                                "confidence": confidence,
                            }
                        )
                else:
                    unresolved.append(
                        {
                            "from_symbol_id": caller["symbol_id"],
                            "callee_name": callee_name,
                            "callsite_file": rel,
                            "callsite_line": call_line,
                            "reason": confidence,
                        }
                    )

    calls.sort(key=lambda c: (c["callsite_file"], c["callsite_line"], c["from_symbol_id"], c["callee_name"]))
    unresolved.sort(key=lambda c: (c["callsite_file"], c["callsite_line"], c["from_symbol_id"], c["callee_name"]))
    return {
        "schema_version": "1.0",
        "symbols": symbols,
        "calls": calls,
        "unresolved_calls": unresolved,
        "stats": {
            "symbol_count": len(symbols),
            "call_count": len(calls),
            "unresolved_call_count": len(unresolved),
        },
    }


def run(project_root: str, file_prefix: str = "") -> tuple[dict[str, Any], dict[str, Any]]:
    symbols = extract_symbols(project_root, file_prefix=file_prefix)
    call_graph = build_call_graph(project_root, symbols, file_prefix=file_prefix)
    return symbols, call_graph
