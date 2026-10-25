"""Actual device-build source membership, derived only from captured compiler inputs.

Every member comes from a real compiler input record: a Swift compiler file list
written by the device build, or a compiler invocation printed by that build. The
project directory layout is never used as a proxy for membership, so a missing
file list can never turn into a plausible-looking complete list.

Inputs that are not source members keep explicit, reviewable states instead of
disappearing: generated build-tree inputs, inputs outside the source tree,
inputs excluded from the source fingerprint, unsupported compiler inputs and
mismatched invocation records. Insufficient evidence yields
``membership_status == 'unresolved'``; a recorded but incomplete picture yields
``'incomplete'``. Only ``'complete'`` claims that every captured compiler input
was accounted for.

An evidence bundle around this document proves package integrity only. It is
not build authenticity, IPA authorship, runtime behavior or test evidence.
"""
from __future__ import annotations

from pathlib import Path
import re

from .contracts import require
from .core import MigrationError, digest, json_bytes, read_json, safe_child, snapshot

KIND = "source_build_membership"
SCHEMA_VERSION = 1
SCOPE = "selected-build"
STATUSES = ("complete", "incomplete", "unresolved")

ORIGIN_SWIFT_FILE_LIST = "swift_file_list"
ORIGIN_BUILD_LOG_SWIFT = "build_log_swift_invocation"
ORIGIN_BUILD_LOG_CLANG = "build_log_clang_invocation"
ORIGIN_BUILD_LOG_OTHER = "build_log_other_invocation"
ORIGINS = (ORIGIN_SWIFT_FILE_LIST, ORIGIN_BUILD_LOG_SWIFT, ORIGIN_BUILD_LOG_CLANG, ORIGIN_BUILD_LOG_OTHER)

SWIFT_SUFFIXES = {".swift"}
CLANG_SUFFIXES = {".m", ".mm", ".c", ".cc", ".cpp", ".cxx", ".s"}
COMPILE_SUFFIXES = SWIFT_SUFFIXES | CLANG_SUFFIXES | {".metal", ".swiftinterface"}

EXCLUDED_GENERATED = "generated_build_tree_input"
EXCLUDED_OUTSIDE = "outside_source_tree"
EXCLUDED_SNAPSHOT = "outside_source_fingerprint_scope"
EXCLUDED_TARGET = "outside_selected_targets"
BLOCKING_EXCLUSIONS = {EXCLUDED_SNAPSHOT}

MEMBER_KINDS = ("swift_source", "clang_source", "other_compiler_input")

_SWIFT_LOG_HEADS = ("SwiftCompile", "SwiftEmitModule", "SwiftDriver", "CompileSwift")
_OTHER_LOG_HEADS = ("Metal", "CompileMetalFile", "MetalCompile", "CompileMetal")
_IN_TARGET = re.compile(r"\(in target '([^']*)' from project '([^']*)'\)")
_BUILD_SUFFIX = ".SwiftFileList"


def _norm(value: str) -> str:
    """Compare compiler paths in one textual form; no filesystem case folding."""
    return value.replace("\\", "/")


def _absolute(value: str) -> bool:
    return value.startswith("/") or re.fullmatch(r"[A-Za-z]:[\\/].*", value) is not None


def _suffix(value: str) -> str:
    name = _norm(value).rsplit("/", 1)[-1]
    index = name.rfind(".")
    return name[index:].lower() if index > 0 else ""


def _member_kind(value: str) -> tuple[str, str]:
    suffix = _suffix(value)
    if suffix in SWIFT_SUFFIXES:
        return "swift_source", "compiled_input"
    if suffix in CLANG_SUFFIXES:
        return "clang_source", "compiled_input"
    return "other_compiler_input", "not_analyzed"


def _safe(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", value).strip("._")
    return cleaned[:48] or "unnamed"


def _tokens(line: str) -> list[str]:
    """Split one compiler line, re-joining xcodebuild's backslash-escaped spaces."""
    merged: list[str] = []
    for raw in line.split():
        if merged and merged[-1].endswith("\\"):
            merged[-1] = merged[-1][:-1] + " " + raw
        else:
            merged.append(raw)
    quoted: list[str] = []
    for token in merged:
        if quoted and quoted[-1].startswith('"') and not quoted[-1].endswith('"'):
            quoted[-1] += " " + token
        else:
            quoted.append(token)
    result = []
    for token in quoted:
        token = token.strip().rstrip(",;")
        if len(token) > 1 and token.startswith('"') and token.endswith('"'):
            token = token[1:-1]
        if token:
            result.append(token)
    return result


def parse_file_list(raw: bytes) -> list[str]:
    """Parse one captured Swift compiler file list: one absolute path per line.

    Entries are returned verbatim (paths may contain spaces and non-ASCII text);
    nothing is expanded, globbed or resolved against the source tree.
    """
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeError as exc:
        raise MigrationError(f"Swift compiler file list is not UTF-8: {exc}") from exc
    if "\x00" in text:
        raise MigrationError("Swift compiler file list contains NUL bytes")
    entries = []
    for line in text.splitlines():
        value = line.strip()
        if not value:
            continue
        if len(value) > 1 and value.startswith('"') and value.endswith('"'):
            value = value[1:-1]
        entries.append(_norm(value))
    return entries


def _architecture(tokens: list[str], start: int) -> str | None:
    """Read the architecture from '<task> normal <arch> ...' when it is printed."""
    for index in range(start, min(start + 3, len(tokens) - 1)):
        if tokens[index].lower() == "normal":
            candidate = tokens[index + 1]
            return candidate if candidate and not candidate.startswith("-") else None
    return None


def _path_like(token: str) -> bool:
    """A token that tries to name a location, not a bare file name.

    ``SwiftDriver``/``SwiftEmitModule`` lines and the ``Compiling\\ A.swift,\\ B.swift``
    short form name tasks or bare files, never an input location: they cannot be
    read as an input, but they also do not claim one is missing.
    """
    return "/" in token and _suffix(token) in COMPILE_SUFFIXES


def parse_compile_invocations(text: str) -> dict:
    """Extract compiler inputs printed by the captured device build.

    Only lines whose first token names a compiler task are read, and only
    absolute paths that carry a compile-input suffix count as inputs. Anything
    that cannot be read that way is reported as ambiguous instead of guessed.
    """
    entries, ambiguous = [], []
    for number, line in enumerate(text.splitlines(), 1):
        stripped = line.strip()
        if not stripped:
            continue
        tokens = _tokens(stripped)
        if not tokens:
            continue
        head = tokens[0]
        if head == "CompileC":
            origin = ORIGIN_BUILD_LOG_CLANG
        elif head.startswith(_SWIFT_LOG_HEADS):
            origin = ORIGIN_BUILD_LOG_SWIFT
        elif head.startswith(_OTHER_LOG_HEADS):
            origin = ORIGIN_BUILD_LOG_OTHER
        else:
            continue
        match = _IN_TARGET.search(stripped)
        target = match.group(1) if match else None
        architecture = _architecture(tokens, 1)
        if head == "CompileC":
            # CompileC <object> <source> normal <arch> ... : the second path is the input.
            if len(tokens) >= 3 and _absolute(tokens[2]) and _suffix(tokens[2]) in COMPILE_SUFFIXES:
                entries.append({"path": _norm(tokens[2]), "origin": origin, "target": target,
                                "architecture": architecture, "line": number})
            else:
                ambiguous.append({"line": number, "detail": stripped[:240]})
            continue
        candidates = [token for token in tokens[1:] if _absolute(token) and _suffix(token) in COMPILE_SUFFIXES]
        if not candidates:
            # Only a line that points at a location we could not read is ambiguous;
            # driver, module-emission and bare-name lines name no input at all.
            if origin == ORIGIN_BUILD_LOG_SWIFT and any(_path_like(token) for token in tokens[1:]):
                ambiguous.append({"line": number, "detail": stripped[:240]})
            continue
        for candidate in candidates:
            entries.append({"path": _norm(candidate), "origin": origin, "target": target,
                            "architecture": architecture, "line": number})
    unique, seen = [], set()
    for entry in entries:
        key = (entry["path"], entry["origin"], entry["target"], entry["architecture"])
        if key not in seen:
            seen.add(key)
            unique.append(entry)
    return {"entries": unique, "ambiguous": ambiguous}


def _swift_file_lists(derived_data: Path, unresolved: list) -> list[Path]:
    if not derived_data.is_dir():
        unresolved.append({"reason": "build_tree_missing", "path": str(derived_data),
                           "detail": "DerivedData is unavailable before cleanup"})
        return []
    found: dict[str, Path] = {}
    try:
        for pattern in ("*" + _BUILD_SUFFIX, "*.swiftfilelist"):
            for path in derived_data.rglob(pattern):
                if path.is_file():
                    found[path.as_posix().casefold()] = path
    except OSError as exc:
        unresolved.append({"reason": "build_tree_unreadable", "path": str(derived_data), "detail": str(exc)})
        return []
    return [found[key] for key in sorted(found)]


def _location(path: Path) -> tuple[str | None, str | None]:
    """Read target and architecture from the compiler's own output directory name."""
    parts = path.as_posix().split("/")
    if "Objects-normal" not in parts:
        return None, None
    index = len(parts) - 1 - parts[::-1].index("Objects-normal")
    architecture = parts[index + 1] if index + 1 < len(parts) - 1 else None
    target = None
    for part in reversed(parts[:index]):
        if part.endswith(".build"):
            target = part[: -len(".build")]
            break
    return target, architecture


def _classify(value: str, source_posix: str, derived_posix: str, source: Path, snap: dict) -> tuple[str, str | None, str | None]:
    if not _absolute(value):
        return "relative", None, "Compiler input is not an absolute path"
    prefix = source_posix.rstrip("/") + "/"
    if not value.startswith(prefix):
        if derived_posix and value.startswith(derived_posix.rstrip("/") + "/"):
            return "generated", None, "Compiler input lives in the build tree, not in source"
        return "outside", None, "Compiler input is outside both the source and build trees"
    relative = value[len(prefix):]
    if not relative or relative.startswith("/") or ".." in relative.split("/"):
        return "escaping", None, "Compiler input escapes the source root"
    if relative not in snap:
        if (source / relative).is_file():
            return "excluded", relative, "Compiler input is outside the source fingerprint scope"
        return "missing", relative, "Compiler input is listed but absent from the source tree"
    return "member", relative, None


def _object_files(derived_data: Path, selected: set) -> dict:
    """Count compiled object files per selected target/architecture directory.

    Object files are the compiler's own output per input, so a directory with more
    objects than captured inputs means something compiled that was not captured.
    """
    counts: dict = {}
    try:
        objects = [path for path in derived_data.rglob("*.o") if path.is_file()]
    except OSError:
        return counts
    for path in objects:
        target, architecture = _location(path)
        if not target or not architecture or target.casefold() not in selected:
            continue
        counts.setdefault((target, architecture), set()).add(path.name)
    return counts


def _selection(value, declared_architectures: set) -> dict:
    """Validate the selected build settings that scope this membership."""
    require(isinstance(value, dict), "Membership selection must be an object")
    allowed = {"scheme", "configuration", "sdk", "xcode_version", "targets", "product", "architectures", "toolchain"}
    require(not set(value) - allowed, "Unknown membership selection fields")
    selection = {}
    for key in ("scheme", "configuration", "sdk", "xcode_version"):
        item = value.get(key)
        require(isinstance(item, str) and bool(item.strip()), f"Membership selection requires {key}")
        selection[key] = item.strip()
    product = value.get("product")
    require(product is None or (isinstance(product, str) and bool(product.strip())),
            "Membership selection product must be a bundle identifier string")
    if product is not None:
        selection["product"] = product.strip()
    targets = value.get("targets")
    require(isinstance(targets, list) and bool(targets), "Membership selection requires the built targets")
    require(all(isinstance(item, str) and bool(item.strip()) for item in targets), "Target names must be strings")
    require(len({item.casefold() for item in targets}) == len(targets), "Duplicate target names")
    selection["targets"] = sorted(item.strip() for item in targets)
    architectures = value.get("architectures", [])
    require(isinstance(architectures, list) and all(isinstance(item, str) and item.strip() for item in architectures),
            "Selection architectures must be strings")
    selection["architectures"] = sorted({item.strip() for item in architectures})
    declared_architectures.update(selection["architectures"])
    toolchain = value.get("toolchain", {})
    require(isinstance(toolchain, dict), "Selection toolchain must be an object")
    require(all(isinstance(key, str) and isinstance(item, str) for key, item in toolchain.items()),
            "Selection toolchain values must be strings")
    selection["toolchain"] = {key: toolchain[key] for key in sorted(toolchain)}
    return selection


def collect(source: Path, derived_data: Path, capture: Path, selection: dict,
            *, build_log: Path | None = None) -> dict:
    """Write ``source-files.json`` for one real device build into ``capture``.

    The document is produced even when evidence is insufficient, so reviewers
    can see what was captured; its status is then ``incomplete``/``unresolved``.
    """
    source, derived_data, capture = Path(source).resolve(), Path(derived_data).resolve(), Path(capture).resolve()
    require(source.is_dir(), f"Source directory does not exist: {source}")
    require(capture.is_dir(), f"Capture directory must already exist: {capture}")
    require(not capture.is_relative_to(source) and not source.is_relative_to(capture),
            "Membership capture must not overlap the source tree")
    require(not derived_data.is_relative_to(source), "Build tree must not live inside the source tree")
    declared_architectures: set = set()
    selection = _selection(selection, declared_architectures)
    selected_targets = {item.casefold() for item in selection["targets"]}
    current = snapshot(source)
    snap = {item["path"]: item for item in current["files"]}
    source_posix, derived_posix = source.as_posix(), derived_data.as_posix()

    files: dict[str, bytes] = {}
    sources: list[dict] = []
    unresolved: list[dict] = []
    captured: list[dict] = []

    for index, path in enumerate(_swift_file_lists(derived_data, unresolved)):
        target, architecture = _location(path)
        try:
            raw = path.read_bytes()
            entries = parse_file_list(raw)
        except (OSError, MigrationError) as exc:
            unresolved.append({"reason": "swift_file_list_unreadable", "path": path.as_posix(), "detail": str(exc)})
            continue
        name = f"filelists/{index:04d}-{_safe(target or 'target')}-{_safe(architecture or 'arch')}.list"
        files[name] = raw
        sources.append({"kind": ORIGIN_SWIFT_FILE_LIST, "artifact": name, "sha256": digest(raw),
                        "bytes": len(raw), "entries": len(entries), "target": target,
                        "architecture": architecture, "module": path.name.rsplit(".", 1)[0]})
        for entry in entries:
            captured.append({"path": entry, "origin": ORIGIN_SWIFT_FILE_LIST, "target": target,
                             "architecture": architecture})
        if not entries:
            unresolved.append({"reason": "empty_swift_file_list", "path": name,
                               "detail": "Captured Swift file list lists no compiled input"})

    build_log_record = None
    invocations = {"entries": [], "ambiguous": []}
    if build_log is not None:
        build_log = Path(build_log)
        raw_log = b""
        try:
            raw_log = build_log.read_bytes()
        except OSError as exc:
            unresolved.append({"reason": "build_log_unreadable", "path": str(build_log), "detail": str(exc)})
        else:
            try:
                text = raw_log.decode("utf-8")
            except UnicodeError:
                text = raw_log.decode("utf-8", "replace")
                unresolved.append({"reason": "build_log_not_utf8", "path": str(build_log),
                                   "detail": "Decoded with replacement characters"})
            invocations = parse_compile_invocations(text)
            for item in invocations["entries"]:
                captured.append({"path": item["path"], "origin": item["origin"], "target": item["target"],
                                 "architecture": item.get("architecture")})
            if invocations["ambiguous"]:
                unresolved.append({"reason": "ambiguous_compile_invocation", "path": str(build_log),
                                   "detail": f"{len(invocations['ambiguous'])} compiler line(s) could not be read "
                                             "as an input path; inspect compile-invocations.json"})
            artifact = None
            if build_log.is_relative_to(capture):
                artifact = build_log.relative_to(capture).as_posix()
            build_log_record = {"artifact": artifact, "sha256": digest(raw_log), "bytes": len(raw_log),
                                "swift_entries": sum(1 for item in invocations["entries"]
                                                     if item["origin"] == ORIGIN_BUILD_LOG_SWIFT),
                                "clang_entries": sum(1 for item in invocations["entries"]
                                                     if item["origin"] == ORIGIN_BUILD_LOG_CLANG),
                                "other_entries": sum(1 for item in invocations["entries"]
                                                     if item["origin"] == ORIGIN_BUILD_LOG_OTHER),
                                "ambiguous_lines": len(invocations["ambiguous"])}
    # A missing build log is a gap in the cross-check, not an unaccounted input.

    has_file_list = any(item["kind"] == ORIGIN_SWIFT_FILE_LIST for item in sources)
    if build_log_record and build_log_record["swift_entries"] and not has_file_list:
        unresolved.append({"reason": "swift_file_list_absent", "path": None,
                           "detail": "The build log compiles Swift but no Swift file list was captured"})

    members: dict[str, dict] = {}
    excluded: dict[str, dict] = {}
    for item in captured:
        target = item.get("target")
        if target and target.casefold() not in selected_targets:
            # Dependency, package and test targets compile inside the same build but
            # are not members of the selected product's source.
            record = excluded.get(item["path"])
            if record is None:
                record = excluded[item["path"]] = {"path": item["path"], "relative_path": None,
                                                   "reason": EXCLUDED_TARGET,
                                                   "detail": "Compiler input belongs to an unselected target",
                                                   "origins": set(), "targets": set()}
            record["origins"].add(item["origin"])
            record["targets"].add(target)
            continue
        category, relative, detail = _classify(item["path"], source_posix, derived_posix, source, snap)
        if category == "member":
            entry = snap[relative]
            kind, analysis = _member_kind(relative)
            record = members.get(relative)
            if record is None:
                record = members[relative] = {"path": relative, "sha256": entry["sha256"], "bytes": entry["bytes"],
                                              "kind": kind, "analysis": analysis, "origins": set(),
                                              "targets": set(), "architectures": set()}
            record["origins"].add(item["origin"])
            if item.get("target"):
                record["targets"].add(item["target"])
            if item.get("architecture"):
                record["architectures"].add(item["architecture"])
            continue
        if category == "relative" or category == "escaping" or category == "missing":
            reason = {"relative": "relative_compile_input", "escaping": "escaping_compile_input",
                      "missing": "missing_compile_input"}[category]
            unresolved.append({"reason": reason, "path": item["path"], "detail": detail})
            continue
        reason = {"generated": EXCLUDED_GENERATED, "outside": EXCLUDED_OUTSIDE,
                  "excluded": EXCLUDED_SNAPSHOT}[category]
        key = item["path"]
        record = excluded.get(key)
        if record is None:
            record = excluded[key] = {"path": key, "relative_path": relative, "reason": reason,
                                      "detail": detail, "origins": set(), "targets": set()}
        record["origins"].add(item["origin"])
        if item.get("target"):
            record["targets"].add(item["target"])

    case_keys = {path.casefold() for path in members}
    if len(case_keys) != len(members):
        unresolved.append({"reason": "case_colliding_member_paths", "path": None,
                           "detail": "Two compiled inputs differ only by letter case"})

    # A path attributed to a selected target cannot stay excluded by target scope.
    member_paths = {source_posix.rstrip("/") + "/" + path for path in members}
    for key in [key for key in excluded if key in member_paths]:
        excluded.pop(key)

    expected_by_directory: dict = {}
    for item in captured:
        target, architecture = item.get("target"), item.get("architecture")
        if target and architecture and target.casefold() in selected_targets:
            expected_by_directory.setdefault((target, architecture), set()).add(item["path"])
    object_counts = _object_files(derived_data, selected_targets)
    directories, unmatched = [], []
    for (target, architecture), names in sorted(object_counts.items()):
        captured_inputs = len(expected_by_directory.get((target, architecture), set()))
        directories.append({"target": target, "architecture": architecture,
                            "objects": len(names), "captured_inputs": captured_inputs})
        if len(names) > captured_inputs:
            unmatched.append({"target": target, "architecture": architecture, "objects": len(names),
                              "captured_inputs": captured_inputs, "sample_objects": sorted(names)[:5]})
    if unmatched:
        first = unmatched[0]
        unresolved.append({"reason": "object_count_exceeds_membership", "path": None,
                           "detail": f"{first['target']}/{first['architecture']} has {first['objects']} object "
                                     f"files but only {first['captured_inputs']} captured compiler inputs; "
                                     "compiled inputs may be missing from the capture"})
    build_tree_objects = {"directories": directories, "unmatched": unmatched}

    observed = set()
    for record in members.values():
        observed.update(record["architectures"])
    for item in sources:
        if item.get("architecture"):
            observed.add(item["architecture"])

    blocking = list(unresolved)
    if not members and not excluded:
        unresolved.append({"reason": "no_compile_evidence", "path": None,
                           "detail": "No Swift file list or compiler invocation was captured for this build"})
        status = "unresolved"
    elif blocking:
        status = "incomplete"
    elif any(item["reason"] in BLOCKING_EXCLUSIONS for item in excluded.values()):
        status = "incomplete"
    elif not members:
        unresolved.append({"reason": "no_source_tree_members", "path": None,
                           "detail": "Every captured compiler input lives outside the source tree"})
        status = "unresolved"
    else:
        status = "complete"

    limitations = ["membership_from_one_selected_device_build",
                   "headers_are_not_compile_inputs",
                   "build_authenticity_not_verified",
                   "behavior_equivalence_not_verified",
                   "ipa_authentication_not_performed"]
    if any(item["reason"] == EXCLUDED_GENERATED for item in excluded.values()):
        limitations.append("generated_build_tree_inputs_recorded_not_members")
    if any(item["reason"] == EXCLUDED_OUTSIDE for item in excluded.values()):
        limitations.append("out_of_tree_inputs_recorded_not_members")
    if any(item["reason"] == EXCLUDED_SNAPSHOT for item in excluded.values()):
        limitations.append("inputs_outside_source_fingerprint_scope")
    if any(item["reason"] == EXCLUDED_TARGET for item in excluded.values()):
        limitations.append("unselected_target_inputs_recorded_not_members")
    if any(record["kind"] == "other_compiler_input" for record in members.values()):
        limitations.append("non_swift_inputs_recorded_not_analyzed")
    if declared_architectures and not declared_architectures <= observed:
        limitations.append("declared_architectures_not_all_observed")
    if build_log_record is None:
        limitations.append("build_log_cross_check_unavailable")

    document = {
        "schema_version": SCHEMA_VERSION,
        "kind": KIND,
        "scope": SCOPE,
        "membership_status": status,
        "selection": selection,
        "capture_roots": {"source": source_posix, "derived_data": derived_posix},
        "source_sha256": current["sha256"],
        "architectures": sorted(observed),
        "source_files": sorted(members),
        "members": [{**record, "origins": sorted(record["origins"]), "targets": sorted(record["targets"]),
                     "architectures": sorted(record["architectures"])}
                    for _, record in sorted(members.items())],
        "excluded_inputs": [{**record, "origins": sorted(record["origins"]), "targets": sorted(record["targets"])}
                            for _, record in sorted(excluded.items())],
        "unresolved": unresolved,
        "evidence": {"captured_build_log": build_log_record, "sources": sources,
                     "build_tree_objects": build_tree_objects},
        "limitations": sorted(set(limitations)),
        "claims": {"package_integrity": "evidence_bundle_only", "build_authenticity": "not_verified",
                   "behavior_equivalence": "not_verified", "ipa_authentication": "not_performed",
                   "capture_host": "macos_xcode_required"},
        "counts": {"source_files": len(members),
                   "non_member_inputs": sum(1 for item in excluded.values()
                                            if item["reason"] != EXCLUDED_SNAPSHOT),
                   "unsupported_inputs": sum(1 for item in members.values()
                                             if item["kind"] == "other_compiler_input"),
                   "unresolved_inputs": len(unresolved)},
    }
    files["compile-invocations.json"] = json_bytes(
        {"schema_version": SCHEMA_VERSION, "kind": "source_build_compile_invocations",
         "captured_build_log": build_log_record, "entries": invocations["entries"],
         "ambiguous": invocations["ambiguous"][:20], "ambiguous_total": len(invocations["ambiguous"])})
    files["source-files.json"] = json_bytes(document)
    for name, data in files.items():
        target = capture / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    return document


def _names(value, label):
    require(isinstance(value, list) and all(isinstance(item, str) and item and item == item.strip()
                                         for item in value), label + " must contain names")
    require(value == sorted(set(value)), label + " must be unique and sorted")
    return set(value)


def _count(value, expected, label):
    require(type(value) is int and value == expected, label + " disagrees with replayed evidence")


def _capture_roots(document, source):
    """Use recorded textual prefixes only; never open the capturing host's paths."""
    if "capture_roots" not in document:
        return source.as_posix(), ""  # Legacy v1 can only replay against the original source root.
    roots = document["capture_roots"]
    require(isinstance(roots, dict) and set(roots) == {"source", "derived_data"}, "Invalid capture_roots")
    for key, value in roots.items():
        require(isinstance(value, str) and _absolute(value) and "\\" not in value and "\x00" not in value
                and all(part not in {".", ".."} for part in value.split("/")) and "//" not in value
                and (not value.endswith("/") or value == "/" or re.fullmatch(r"[A-Za-z]:/", value)),
                "Capture root must be a normalized absolute path without traversal: " + key)
    source_root, derived_root = roots["source"], roots["derived_data"]
    require(derived_root != source_root and not derived_root.startswith(source_root.rstrip("/") + "/"),
            "Captured build tree must not live inside the captured source tree")
    return source_root, derived_root


def _replay_membership(source, capture, document, snap, selected):
    """Replay raw compiler records, never the derived invocation summary alone."""
    evidence = document.get("evidence")
    require(isinstance(evidence, dict), "Membership evidence block is missing")
    sources = evidence.get("sources")
    require(isinstance(sources, list), "Membership evidence sources must be a list")
    source_root, derived_root = _capture_roots(document, source)
    captured, observed, required_unresolved, artifacts = [], set(), set(), set()
    for item in sources:
        require(isinstance(item, dict) and item.get("kind") == ORIGIN_SWIFT_FILE_LIST,
                "Unknown evidence source kind")
        artifact = item.get("artifact")
        require(isinstance(artifact, str) and artifact.startswith("filelists/"),
                "Evidence source must reference a captured file list")
        path = safe_child(capture, artifact)
        require(artifact not in artifacts, "Duplicate captured file list")
        artifacts.add(artifact)
        require(path.is_file(), f"Missing captured file list: {artifact}")
        raw = path.read_bytes()
        require(digest(raw) == item.get("sha256"), f"Captured file list was modified: {artifact}")
        _count(item.get("bytes"), len(raw), "Captured file list bytes")
        entries = parse_file_list(raw)
        _count(item.get("entries"), len(entries), "Captured file list entry count")
        for key in ("target", "architecture"):
            value = item.get(key)
            require(value is None or isinstance(value, str) and bool(value.strip()),
                    "Invalid file list " + key)
        require(re.fullmatch(r"filelists/\d{4,}-" + re.escape(_safe(item.get("target") or "target"))
                             + "-" + re.escape(_safe(item.get("architecture") or "arch")) + r"\.list", artifact),
                "Captured file list target/architecture disagree with its artifact name")
        if item.get("architecture"):
            observed.add(item["architecture"])
        if not entries:
            required_unresolved.add(("empty_swift_file_list", artifact))
        captured.extend({"path": entry, "origin": ORIGIN_SWIFT_FILE_LIST,
                         "target": item.get("target"), "architecture": item.get("architecture")}
                        for entry in entries)

    logged = evidence.get("captured_build_log")
    invocations = {"entries": [], "ambiguous": []}
    require(logged is None or isinstance(logged, dict), "Invalid captured build log record")
    if logged is not None:
        artifact = logged.get("artifact")
        require(isinstance(artifact, str) and bool(artifact), "Captured build log needs its raw artifact")
        path = safe_child(capture, artifact)
        require(path.is_file(), f"Missing captured build log: {artifact}")
        raw = path.read_bytes()
        require(digest(raw) == logged.get("sha256"), f"Captured build log was modified: {artifact}")
        _count(logged.get("bytes"), len(raw), "Captured build log bytes")
        try:
            text = raw.decode("utf-8")
        except UnicodeError:
            text = raw.decode("utf-8", "replace")
            required_unresolved.add(("build_log_not_utf8", None))
        invocations = parse_compile_invocations(text)
        for key, origin in (("swift_entries", ORIGIN_BUILD_LOG_SWIFT),
                            ("clang_entries", ORIGIN_BUILD_LOG_CLANG),
                            ("other_entries", ORIGIN_BUILD_LOG_OTHER)):
            _count(logged.get(key), sum(item["origin"] == origin for item in invocations["entries"]),
                   "Captured build log " + key)
        _count(logged.get("ambiguous_lines"), len(invocations["ambiguous"]), "Ambiguous build log lines")
        if invocations["ambiguous"]:
            required_unresolved.add(("ambiguous_compile_invocation", None))
        if logged["swift_entries"] and not sources:
            required_unresolved.add(("swift_file_list_absent", None))
        captured.extend(invocations["entries"])
    summary_path = safe_child(capture, "compile-invocations.json")
    if summary_path.is_file():
        require(read_json(summary_path) == {
            "schema_version": SCHEMA_VERSION, "kind": "source_build_compile_invocations",
            "captured_build_log": logged, "entries": invocations["entries"],
            "ambiguous": invocations["ambiguous"][:20], "ambiguous_total": len(invocations["ambiguous"])},
            "Compile invocation summary disagrees with the raw build log")

    members, excluded, directories = {}, {}, {}
    claimed_excluded = {item["path"]: item for item in document["excluded_inputs"]}
    complete = document["membership_status"] == "complete"
    for item in captured:
        target, architecture, value = item.get("target"), item.get("architecture"), item["path"]
        require(not complete or target and architecture,
                "Complete membership cannot hide unknown compiler target or architecture")
        if target and architecture and target.casefold() in selected:
            directories.setdefault((target, architecture), set()).add(value)
        if target and target.casefold() not in selected:
            category, relative, reason = "excluded", None, EXCLUDED_TARGET
        else:
            category, relative, _ = _classify(value, source_root, derived_root, source, snap)
            if category in {"relative", "escaping", "missing"}:
                required_unresolved.add(({"relative": "relative_compile_input", "escaping": "escaping_compile_input",
                                          "missing": "missing_compile_input"}[category], value))
                continue
            reason = {"excluded": EXCLUDED_SNAPSHOT, "generated": EXCLUDED_GENERATED}.get(category, EXCLUDED_OUTSIDE)
            # Old v1 did not record the build-tree root. It cannot establish a
            # relocation, but its explicit non-member classification stays usable.
            if not derived_root and category == "outside" and claimed_excluded.get(value, {}).get("reason") == EXCLUDED_GENERATED:
                reason = EXCLUDED_GENERATED
        if category == "member":
            record = members.setdefault(relative, {"origins": set(), "targets": set(), "architectures": set()})
            if architecture:
                record["architectures"].add(architecture)
                observed.add(architecture)
        else:
            record = excluded.setdefault(value, {"reason": reason, "relative_path": relative,
                                                  "origins": set(), "targets": set()})
        record["origins"].add(item["origin"])
        if target:
            record["targets"].add(target)
    member_paths = {source_root.rstrip("/") + "/" + path for path in members}
    for value in [value for value in excluded if value in member_paths]:
        excluded.pop(value)
    require(set(members) == set(document["source_files"]),
            "Membership members lack raw compiler evidence or omit captured source inputs")
    for member in document["members"]:
        for field in ("origins", "targets", "architectures"):
            require(set(member[field]) == members[member["path"]][field],
                    "Member " + field + " disagree with raw compiler evidence: " + member["path"])
    require(set(excluded) == set(claimed_excluded), "Excluded inputs disagree with raw compiler evidence")
    for value, replayed in excluded.items():
        claimed = claimed_excluded[value]
        require(all(claimed[field] == replayed[field] for field in ("reason", "relative_path"))
                and all(set(claimed[field]) == replayed[field] for field in ("origins", "targets")),
                "Excluded input metadata disagrees with raw compiler evidence: " + value)
    require(set(document["architectures"]) == observed, "Membership architectures disagree with raw compiler evidence")
    unresolved = document["unresolved"]
    for reason, path in required_unresolved:
        require(any(item["reason"] == reason and (path is None or item.get("path") == path) for item in unresolved),
                "Raw compiler evidence has an unreported unresolved input: " + reason)
    objects = evidence.get("build_tree_objects")
    require(isinstance(objects, dict) and isinstance(objects.get("directories"), list)
            and isinstance(objects.get("unmatched"), list), "Invalid build object evidence")
    expected_unmatched, seen = set(), set()
    for item in objects["directories"]:
        require(isinstance(item, dict), "Invalid build object directory")
        key = (item.get("target"), item.get("architecture"))
        require(all(isinstance(value, str) and value for value in key) and key not in seen,
                "Unknown or duplicate build object directory")
        seen.add(key)
        require(key[0].casefold() in selected, "Build object target is outside selection")
        count = len(directories.get(key, set()))
        _count(item.get("captured_inputs"), count, "Build object captured_inputs")
        require(type(item.get("objects")) is int and item["objects"] >= 0, "Invalid build object count")
        if item["objects"] > count:
            expected_unmatched.add((key[0], key[1], item["objects"], count))
    actual_unmatched = set()
    for item in objects["unmatched"]:
        require(isinstance(item, dict), "Invalid unmatched build object record")
        values = tuple(item.get(key) for key in ("target", "architecture", "objects", "captured_inputs"))
        require(all(isinstance(value, str) for value in values[:2]) and all(type(value) is int for value in values[2:]),
                "Invalid unmatched build object fields")
        require(values not in actual_unmatched, "Duplicate unmatched build object record")
        actual_unmatched.add(values)
    require(actual_unmatched == expected_unmatched, "Unmatched object records disagree with captured input counts")
    if expected_unmatched:
        require(any(item["reason"] == "object_count_exceeds_membership" for item in unresolved),
                "Unmatched build objects must remain unresolved")


def validate(source: Path, document, *, capture: Path | None = None) -> dict:
    """Replay a membership document against the current source tree.

    Complete membership requires raw compiler records in capture. Without those
    records only incomplete/unresolved document structure can be checked.
    """
    source = Path(source).resolve()
    if isinstance(document, (str, Path)):
        document = read_json(Path(document))
    require(isinstance(document, dict), "Membership document must be an object")
    require(type(document.get("schema_version")) is int and document["schema_version"] == SCHEMA_VERSION
            and document.get("kind") == KIND and document.get("scope") == SCOPE,
            "Unsupported source build membership contract")
    status = document.get("membership_status")
    require(status in STATUSES, "Membership status is missing or unknown")
    selection = _selection(document.get("selection"), set())
    require(document["selection"] == selection, "Membership selection must be normalized")
    selected = {item.casefold() for item in selection["targets"]}
    _capture_roots(document, source)
    _names(document.get("architectures"), "Membership architectures")
    current = snapshot(source)
    require(document.get("source_sha256") == current["sha256"],
            "Membership source fingerprint is stale or modified")
    snap = {item["path"]: item for item in current["files"]}
    paths = document.get("source_files")
    require(isinstance(paths, list) and all(isinstance(item, str) and item for item in paths),
            "Membership source_files must be a list of relative paths")
    require(paths == sorted(set(paths)), "Membership source_files must be unique and sorted")
    members = document.get("members")
    require(isinstance(members, list) and all(isinstance(item, dict) for item in members),
            "Membership members must be a list of objects")
    require([item.get("path") for item in members] == paths,
            "Membership member records disagree with source_files")
    for member in members:
        require(isinstance(member, dict), "Membership member must be an object")
        entry = snap.get(member.get("path"))
        require(entry is not None, f"Member is outside the source fingerprint scope: {member.get('path')}")
        require(member.get("sha256") == entry["sha256"] and type(member.get("bytes")) is int
                and member["bytes"] == entry["bytes"],
                f"Member fingerprint differs from current source: {member.get('path')}")
        require((member.get("kind"), member.get("analysis")) == _member_kind(member["path"]),
                "Member kind/analysis disagree with its source suffix")
        origins = _names(member.get("origins"), "Member origins")
        require(bool(origins) and origins <= set(ORIGINS),
                "Member origin must name a captured compiler input record")
        targets = _names(member.get("targets"), "Member targets")
        require({target.casefold() for target in targets} <= selected, "Member targets are outside selection")
        architectures = _names(member.get("architectures"), "Member architectures")
        require(architectures <= set(document["architectures"]), "Member architectures are not observed")
    excluded = document.get("excluded_inputs")
    require(isinstance(excluded, list), "Membership excluded_inputs must be a list")
    for item in excluded:
        require(isinstance(item, dict) and isinstance(item.get("reason"), str) and item["reason"] in
                {EXCLUDED_GENERATED, EXCLUDED_OUTSIDE, EXCLUDED_SNAPSHOT, EXCLUDED_TARGET},
                "Unknown excluded input reason")
        require(isinstance(item.get("path"), str) and bool(item["path"]), "Invalid excluded input path")
        require(item.get("relative_path") is None or isinstance(item["relative_path"], str), "Invalid excluded relative path")
        require(bool(_names(item.get("origins"), "Excluded origins"))
                and set(item["origins"]) <= set(ORIGINS), "Unknown excluded origin")
        _names(item.get("targets"), "Excluded targets")
    require(not (set(paths) & {item.get("relative_path") for item in excluded}),
            "An input cannot be both member and excluded")
    require(len({item["path"] for item in excluded}) == len(excluded), "Duplicate excluded input")
    unresolved = document.get("unresolved")
    require(isinstance(unresolved, list), "Membership unresolved list must be present")
    require(all(isinstance(item, dict) and isinstance(item.get("reason"), str) and item["reason"]
                and (item.get("path") is None or isinstance(item["path"], str)) for item in unresolved),
            "Invalid unresolved input record")
    if status == "complete":
        require(not unresolved, "A complete membership must not carry unresolved inputs")
        require(not any(item.get("reason") in BLOCKING_EXCLUSIONS for item in excluded),
                "A complete membership must not exclude compiled inputs from the source fingerprint")
        require(bool(paths), "A complete membership must name at least one compiled source file")
        require(capture is not None, "Complete membership requires captured raw compiler evidence")
    counts = document.get("counts")
    require(isinstance(counts, dict), "Membership counts must be present")
    for key, expected in {"source_files": len(paths), "unresolved_inputs": len(unresolved),
                          "non_member_inputs": sum(item["reason"] != EXCLUDED_SNAPSHOT for item in excluded),
                          "unsupported_inputs": sum(item["kind"] == "other_compiler_input" for item in members)}.items():
        _count(counts.get(key), expected, "Membership count " + key)
    if capture is not None:
        _replay_membership(source, Path(capture).resolve(), document, snap, selected)
    return {"schema_version": SCHEMA_VERSION, "kind": KIND, "integrity_passed": True,
            "membership_status": status, "source_sha256": current["sha256"],
            "source_files": paths, "claim_validation": "not_performed",
            "build_authenticity": "not_verified", "behavior_equivalence": "not_verified"}
