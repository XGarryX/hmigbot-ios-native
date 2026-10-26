"""HarmonyOS build log diagnostics: classify real compiler output read from log files.

Design constraints (task contract):
- Read-only over the provided stdout/stderr log files: they are hashed (SHA-256)
  for audit and never modified. Reports go only to an explicit output path.
- ``returncode`` is the real process exit code. A non-zero or missing returncode
  is NEVER reported as a pass: without parseable errors the status is
  ``fail_unparsed``. A zero returncode only means the build command exited zero;
  functionality and UI are explicitly marked not verified.
- ``error_code`` is reported only when the code string is literally present in
  the log (ArkTS lint rule ids such as ``arkts-no-standalone-this`` or numeric
  codes such as ohpm's ``Error code:404``). Codes are never invented.
- file/line/column/target are reported only when the log actually contains them;
  ``log_ref`` always pins the exact original log line(s).
- Suggestions are advisory text anchored to the finding's source location and
  derived from local DevEco skill data (arkts-error-fixes, deveco-studio-hvigor)
  or an explicit heuristic marker. This API never edits source code, signing
  configuration or devices and never calls model APIs.
- Credential-like log lines (passwords, tokens, private keys) are never copied
  into reports; secret values are redacted before inclusion.
- Unmatched errors stay ``unknown`` with low confidence.
"""
from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .core import SCHEMA, MigrationError, atomic_write, digest, io_path, json_bytes

_REPORT_KIND = "harmony_build_diagnostics"
_MAX_FINDINGS = 200
_MAX_MESSAGE_LINES = 8
_SKILL_ARKTS = "deveco skill: arkts-error-fixes"
_SKILL_HVIGOR = "deveco skill: deveco-studio-hvigor"
_HEURISTIC = "hmigbot heuristic (no exact skill section)"

_LIMITATIONS = [
    "Parsing rules were validated against synthetic logs modeled on DevEco/hvigor output; no real-device or real-project HarmonyOS build capture was used.",
    "returncode=0 means only that the build command exited 0; functionality and UI are not verified.",
    "error_code is reported only when the code string is literally present in the log.",
    "Suggestions are advisory; this API never edits source, signing configuration or devices and never calls model APIs.",
]

_REDACTED_LINE = "[REDACTED:credential-like line]"
_REDACTED_KEY_BLOCK = "[REDACTED:private-key-block]"
_REDACTED_VALUE = "[REDACTED]"
_REDACTED_TOKEN = "[REDACTED:token]"

_ARKTS_FILE_HEADER = re.compile(
    r"^\s*(?:(?P<sev>ERROR|WARNING|WARN)\s*:?\s*)?"
    r"(?:ArkTS|ets_checker|ets_loader|tsc)\s*:?\s*(?:ERROR|WARNING)?\s*:?\s*"
    r"File\s*:\s*(?P<file>.+?):(?P<line>\d+):(?P<col>\d+)\s*$",
    re.IGNORECASE)

_ARKTS_PLAIN_HEADER = re.compile(
    r"^\s*(?:(?P<sev>ERROR|WARNING|WARN)\s*:?\s*)?"
    r"(?:ArkTS|ets_checker|ets_loader|tsc)\s*:?\s*(?:ERROR|WARNING)\s*:?\s*(?P<msg>.*)$",
    re.IGNORECASE)

_GENERIC_HEADER = re.compile(
    r"^\s*(?P<sev>ERROR|WARNING|WARN)(?:\s+Message)?\s*:\s*(?P<msg>.*)$",
    re.IGNORECASE)

_BUILD_SUCCESS = re.compile(r"BUILD SUCCESSFUL", re.IGNORECASE)
_BUILD_FAILED = re.compile(r"BUILD FAILED", re.IGNORECASE)
_LOG_ERROR = re.compile(r"^\s*(?:(?:>\s*)?hvigor\s+)?(?:ERROR|FATAL)\b\s*[:\[]", re.IGNORECASE)

_BARE_ERROR = re.compile(
    r"hvigorw[^\n]{0,40}is not recognized|is not recognized[^\n]{0,40}hvigorw|hvigorw: command not found",
    re.IGNORECASE)

_ARKTS_CODE = re.compile(
    r"(?<![A-Za-z0-9-])(arkts-no-[a-z0-9-]+|arkts-limited-stdlib|arkts-strict-typing)(?![a-z0-9-])",
    re.IGNORECASE)

_NUMERIC_CODE = re.compile(
    r"(?:[Ee]rror(?:\s+[Mm]essage)?\s*[Cc]ode|[Rr]esponse\s+[Cc]ode)\s*[:=]?\s*(\d{3,7})")

_MODULE_TARGET = re.compile(
    r"(?<![\w@.\-/])([A-Za-z][A-Za-z0-9_-]{0,63})@([A-Za-z][A-Za-z0-9_-]{0,63})(?![\w@.\-])")

_KEY_BEGIN = re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")
_KEY_END = re.compile(r"-----END [A-Z ]*PRIVATE KEY-----")

_CREDENTIAL_LINE = re.compile(
    r"(?i)(?<![\w])(?:password|passwd|pwd|store[ _-]?password|key[ _-]?password|token|access[ _-]?token|"
    r"refresh[ _-]?token|api[ _-]?key|apikey|client[ _-]?secret|secret|authorization|cookie)"
    r"\b[\"']?(?:\s*[:=]|\s+|$)|"
    r"-----BEGIN [A-Z ]*PRIVATE KEY-----")

_BEARER = re.compile(r"(?i)\bbearer\s+[A-Za-z0-9._\-]+")

_TOKEN_LITERAL = re.compile(
    r"ghp_[A-Za-z0-9]{16,}|gho_[A-Za-z0-9]{16,}|github_pat_[A-Za-z0-9_]{16,}|"
    r"sk-[A-Za-z0-9]{16,}|AKIA[0-9A-Z]{16}|xox[baprs]-[A-Za-z0-9-]{10,}")


def _rule(pattern: str, category: str, suggestion: str, confidence: str,
          basis: str, tool: str) -> tuple[re.Pattern[str], dict[str, Any]]:
    return re.compile(pattern, re.IGNORECASE), {
        "category": category, "suggestion": suggestion,
        "confidence": confidence, "basis": basis, "tool": tool}


_CODE_RULES: dict[str, dict[str, Any]] = {
    "arkts-no-standalone-this": {
        "category": "arkts_syntax", "confidence": "high", "tool": "arkts",
        "suggestion": "Pass the context explicitly as a function parameter (e.g. function foo(context: Context)) instead of using `this` in a standalone function.",
        "basis": _SKILL_ARKTS + " > Standalone Function `this` Errors"},
    "arkts-no-obj-literals-as-types": {
        "category": "arkts_type", "confidence": "high", "tool": "arkts",
        "suggestion": "Do not use object-literal types in annotations; declare an interface/class and use it as the type.",
        "basis": _SKILL_ARKTS + " > Object Literal Type Errors"},
    "arkts-no-untyped-obj-literals": {
        "category": "arkts_type", "confidence": "high", "tool": "arkts",
        "suggestion": "Declare an explicit class/interface before using the object literal and give the literal that type.",
        "basis": _SKILL_ARKTS + " > Object Literal Interface Errors"},
    "arkts-no-any-unknown": {
        "category": "arkts_type", "confidence": "medium", "tool": "arkts",
        "suggestion": "Replace `any`/`unknown` with concrete types; ArkTS restricts them.",
        "basis": _HEURISTIC},
    "arkts-limited-stdlib": {
        "category": "arkts_syntax", "confidence": "medium", "tool": "arkts",
        "suggestion": "Use an ArkTS-supported standard library API instead of the disallowed one.",
        "basis": _HEURISTIC},
    "arkts-strict-typing": {
        "category": "arkts_type", "confidence": "medium", "tool": "arkts",
        "suggestion": "Add explicit type annotations; ArkTS strict typing rejects implicit `any`.",
        "basis": _HEURISTIC},
}

_MESSAGE_RULES: list[tuple[re.Pattern[str], dict[str, Any]]] = [
    _rule(r"hvigorw['\w ]* is not recognized|hvigorw: command not found|cannot find module.*hvigorw",
          "hvigor",
          "Invoke the wrapper through Node: node \"<DevEco Studio>/tools/hvigor/bin/hvigorw.js\" <task> --no-daemon (Windows) or fix PATH.",
          "high", _SKILL_HVIGOR + " > Common Problems > hvigorw command not found", "hvigor"),
    _rule(r"unsupported modelversion", "sdk_api",
          "Unify modelVersion in hvigor/hvigor-config.json5 and oh-package.json5, and targetSdkVersion/compatibleSdkVersion in build-profile.json5.",
          "high", _SKILL_HVIGOR + " > Common Problems > Version compatibility issues", "hvigor"),
    _rule(r"init keystore failed|parsealgparameters failed", "signing",
          "Inspect the referenced signing configuration and certificate/profile validity read-only. Ask the project owner to supply a valid authorized signing configuration; preserve existing signingConfigs and credentials.",
          "high", _SKILL_HVIGOR + " > Common Problems > Signing configuration errors", "signing"),
    _rule(r"\bsigningconfigs?\b|\bkeystore\b|\.p12\b|\.cer\b|\.p7b\b|provisioning profile", "signing",
          "Verify the signing configuration in build-profile.json5: file paths, alias, passwords and certificate/profile validity.",
          "medium", _SKILL_HVIGOR + " > Common Problems > Signing configuration errors", "signing"),
    _rule(r"install failed", "module_dependency",
          "Check the failing package name/version in the module's oh-package.json5 and registry reachability, then rerun ohpm install or hvigor --sync.",
          "medium", _HEURISTIC, "ohpm"),
    _rule(r"cannot find module ['\"]?@(?:ohos|kit)\.", "sdk_api",
          "Verify the @ohos/@kit import path spelling and that the API is available in the project's compatibleSdkVersion.",
          "medium", _HEURISTIC, "arkts"),
    _rule(r"cannot find module|unable to resolve (?:module|package|dependency)", "module_dependency",
          "Add the missing dependency to the matching oh-package.json5 and run ohpm install (or hvigor --sync).",
          "medium", _HEURISTIC, "ohpm"),
    _rule(r"resource (?:id )?(?:was )?not found|resource [\w ']*invalid|invalid resource", "resource",
          "Ensure the resource exists under the module's resources/base/element (and qualifier dirs) and that $r('app.type.name') matches it exactly.",
          "medium", _HEURISTIC, "hvigor"),
    _rule(r"no (?:connected )?devices?|device (?:not found|offline|unauthorized)|\[Empty\]|failed to communicate with (?:the )?daemon", "device",
          "Check `hdc list targets`, reconnect/authorize the device, then retry the install or hdc command.",
          "medium", _HEURISTIC, "device"),
    _rule(r"object literal must correspond to some explicitly declared class or interface", "arkts_type",
          "Declare an explicit class/interface for the object literal and annotate the literal with it.",
          "high", _SKILL_ARKTS + " > Object Literal Interface Errors", "arkts"),
    _rule(r"object literal", "arkts_type",
          "Object literals need explicit class/interface types in ArkTS; declare the type and annotate the literal (also for return types).",
          "medium", _SKILL_ARKTS + " > Object Literal Type Errors", "arkts"),
    _rule(r"catch clause variable cannot have (?:a |an )?type annotation", "arkts_syntax",
          "Remove the type annotation from the catch clause variable; ArkTS does not allow typed catch parameters.",
          "high", _SKILL_ARKTS + " > Catch Clause Type Errors", "arkts"),
    _rule(r"standalone[^\n]{0,40}\bthis\b|\bthis\b[^\n]{0,40}standalone", "arkts_syntax",
          "Pass the context explicitly as a function parameter (e.g. function foo(context: Context)) instead of using `this` in a standalone function.",
          "high", _SKILL_ARKTS + " > Standalone Function `this` Errors", "arkts"),
    _rule(r"is possibly (?:'|\")?(?:null|undefined)", "arkts_type",
          "Guard the access with an explicit null/undefined check or optional chaining before use.",
          "medium", _SKILL_ARKTS + " > Possibly Null Errors", "arkts"),
    _rule(r"property '[^']+' does not exist on type 'color'", "arkts_type",
          "Use a hex color value (e.g. '#FF0000') or an existing Color member; the referenced Color property does not exist.",
          "medium", _SKILL_ARKTS + " > Color Property Errors", "arkts"),
    _rule(r"property '[^']+' does not exist on type", "arkts_type",
          "Check the object's declared type: add the property to the type, or correct the property name/type.",
          "medium", _HEURISTIC, "arkts"),
    _rule(r"type '[^']+' is not assignable to type|argument of type", "arkts_type",
          "Align the value with the declared type (explicit annotation or explicit conversion); ArkTS rejects implicit structural typing.",
          "medium", _HEURISTIC, "arkts"),
    _rule(r"cannot find name", "arkts_type",
          "Declare the identifier, fix its spelling, or add the missing import.",
          "medium", _HEURISTIC, "arkts"),
    _rule(r"@storagelink", "arkts_type",
          "Give the @StorageLink property a default value (`= undefined` or a concrete value).",
          "medium", _SKILL_ARKTS + " > @StorageLink Default Value Errors", "arkts"),
    _rule(r"\besobject\b", "arkts_type",
          "Avoid ESObject; use ESModule or concrete types instead.",
          "medium", _SKILL_ARKTS + " > ESObject Type Errors", "arkts"),
    _rule(r"getlastwindow", "arkts_type",
          "Use the callback pattern for window.getLastWindow; its Promise type inference trips ArkTS checks.",
          "medium", _SKILL_ARKTS + " > Window API Type Errors", "arkts"),
    _rule(r"appstorage", "arkts_type",
          "Prefer @StorageLink with LocalStorage or AppStorage.setAndLink instead of AppStorage.get()/setOrCreate() type inference.",
          "medium", _SKILL_ARKTS + " > AppStorage Type Errors", "arkts"),
    _rule(r"idatasource", "arkts_type",
          "Implement the IDataSource interface for the LazyForEach data source.",
          "medium", _SKILL_ARKTS + " > IDataSource Type Errors", "arkts"),
    _rule(r"duplicate[^\n]{0,30}@entry|@entry[^\n]{0,30}(?:once|duplicate)|only one @entry", "arkts_syntax",
          "Keep a single @Entry per page; use plain @Component for child components and remove the extra @Entry.",
          "medium", _SKILL_ARKTS + " > Duplicate Entry Errors", "arkts"),
    _rule(r"avoidarea", "arkts_type",
          "Add the missing `visible: false` property to the AvoidArea object literal.",
          "medium", _SKILL_ARKTS + " > AvoidArea Type Errors", "arkts"),
    _rule(r"titlebuttonrect", "arkts_type",
          "Use window.TitleButtonRect; only width and height exist (no left/top).",
          "medium", _SKILL_ARKTS + " > TitleButtonRect Type Errors", "arkts"),
    _rule(r"is declared but (?:its value )?(?:is )?never read|declared but never used", "arkts_lint",
          "Remove the unused variable or consume it (e.g. console.info/hilog) if it was meant for logging.",
          "medium", _SKILL_ARKTS + " > Unused Variable Warnings", "arkts"),
    _rule(r"(?:convert|instead of|only)[^\n]{0,40}arrow function|arrow function[^\n]{0,40}(?:instead of|convert)", "arkts_syntax",
          "Convert the function expression to an arrow function (`=>`).",
          "medium", _SKILL_ARKTS + " > Arrow Function Conversion Errors", "arkts"),
    _rule(r"function lacks ending return statement|not all code paths return", "arkts_type",
          "Add an explicit return type annotation and return a value on every code path.",
          "medium", _SKILL_ARKTS + " > Function Return Type Errors", "arkts"),
    _rule(r"unsupported[^\n]{0,20}node(?:\.js)?|node(?:\.js)? v?ersion[^\n]{0,40}(?:required|unsupported|incompatible)", "hvigor",
          "Use Node.js v14.18.3+ (DevEco Studio ships one under tools/node).",
          "medium", _SKILL_HVIGOR + " > Environment requirements", "hvigor"),
    _rule(r"api (?:level|version)|requires api level|compatible(?:d)?sdkversion", "sdk_api",
          "Check compatibleSdkVersion/targetSdkVersion in build-profile.json5 and guard APIs with canIUse/version checks.",
          "medium", _HEURISTIC, "hvigor"),
]

_API_CONTRACT = {
    "reads_logs_only": True,
    "edits_source": False,
    "edits_signing": False,
    "device_operations": False,
    "network_access": False,
    "model_api_calls": False,
}


def _redact_line(line: str, counters: dict[str, int]) -> str:
    if _CREDENTIAL_LINE.search(line):
        counters["redacted"] += 1
        return _REDACTED_LINE
    text = _TOKEN_LITERAL.sub(_REDACTED_TOKEN, line)
    text = _BEARER.sub("Bearer " + _REDACTED_VALUE, text)
    if text != line:
        counters["redacted"] += 1
    return text


def _new_finding(sev: str | None, start: int, tool: str | None = None,
                 file: str | None = None, line: int | None = None,
                 column: int | None = None) -> dict[str, Any]:
    severity = "warning" if sev and sev.upper().startswith("WARN") else "error"
    return {"severity": severity, "tool": tool, "start": start, "end_line": start,
            "file": file, "line": line, "column": column, "message_lines": []}


def _append_message_line(current: dict[str, Any], text: str, lineno: int) -> None:
    if len(current["message_lines"]) >= _MAX_MESSAGE_LINES:
        return
    current["message_lines"].append(text)
    current["end_line"] = lineno


def _infer_tool(text: str) -> str:
    low = text.lower()
    if ".ets" in low or "arkts" in low:
        return "arkts"
    if "ohpm" in low or "oh-package" in low or "oh_modules" in low:
        return "ohpm"
    if "hvigor" in low:
        return "hvigor"
    if "keystore" in low or "signing" in low or "certificate" in low:
        return "signing"
    if "hdc" in low or "device" in low:
        return "device"
    return "unknown"


def _classify(text: str, code: str | None) -> dict[str, Any]:
    matched: dict[str, Any] | None = None
    for pattern, rule in _MESSAGE_RULES:
        if pattern.search(text):
            if matched is None or rule["confidence"] == "high":
                matched = rule
            if rule["confidence"] == "high":
                break
    code_rule = _CODE_RULES.get(code) if code else None
    if matched and matched["confidence"] == "high":
        return matched
    if code_rule:
        return code_rule
    if matched:
        return matched
    if code and code.startswith('arkts-'):
        return {"category": "arkts_lint",
                "suggestion": "Apply the rule text for '%s' from the ArkTS type specification; no local fix mapping exists." % code,
                "confidence": "medium",
                "basis": "ArkTS lint rule literal from log; no local rule mapping",
                "tool": "arkts"}
    return {"category": "unknown", "suggestion": None, "confidence": "low",
            "basis": _HEURISTIC, "tool": None}


def _finalize_finding(current: dict[str, Any], stream: str) -> dict[str, Any]:
    message = "\n".join(current["message_lines"])
    text = " ".join(current["message_lines"])
    code: str | None = None
    m = _ARKTS_CODE.search(text)
    if m:
        code = m.group(1).lower()
    else:
        m = _NUMERIC_CODE.search(text)
        if m:
            code = m.group(1)
    target = None
    m = _MODULE_TARGET.search(text)
    if m:
        target = "%s@%s" % (m.group(1), m.group(2))
    chosen = _classify(text, code)
    tool = current["tool"] or chosen.get("tool") or _infer_tool(text)
    suggestion = chosen["suggestion"]
    if suggestion and current["file"]:
        suggestion = "%s:%s:%s: %s" % (current["file"], current["line"], current["column"], suggestion)
    return {"severity": current["severity"], "tool": tool, "error_code": code,
            "message": message, "file": current["file"], "line": current["line"],
            "column": current["column"], "target": target,
            "log_ref": {"stream": stream, "line": current["start"], "end_line": current["end_line"]},
            "category": chosen["category"], "suggestion": suggestion,
            "basis": chosen["basis"], "confidence": chosen["confidence"]}


def _flush(current: dict[str, Any] | None, findings: list[dict[str, Any]],
           stream: str, counters: dict[str, Any]) -> None:
    if current is None:
        return
    if counters.get('findings', 0) >= _MAX_FINDINGS:
        counters["truncated"] = True
        return
    findings.append(_finalize_finding(current, stream))
    counters['findings'] = counters.get('findings', 0) + 1


def _scan_stream(lines: list[str], stream: str,
                 counters: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, bool]]:
    findings: list[dict[str, Any]] = []
    markers = {"build_successful": False, "build_failed": False}
    current: dict[str, Any] | None = None
    in_key_block = False
    for lineno, line in enumerate(lines, 1):
        if _LOG_ERROR.search(line):
            counters["error_marker"] = True
        if in_key_block:
            if _KEY_END.search(line):
                in_key_block = False
            continue
        if _KEY_BEGIN.search(line):
            if current is not None:
                _append_message_line(current, _REDACTED_KEY_BLOCK, lineno)
                counters["redacted"] += 1
            in_key_block = True
            continue
        if _BUILD_SUCCESS.search(line):
            markers["build_successful"] = True
            _flush(current, findings, stream, counters)
            current = None
            continue
        if _BUILD_FAILED.search(line):
            markers["build_failed"] = True
            _flush(current, findings, stream, counters)
            current = None
            continue
        m = _ARKTS_FILE_HEADER.match(line)
        if m:
            _flush(current, findings, stream, counters)
            safe_file = _redact_line(m.group("file"), counters)
            current = _new_finding(m.group("sev"), lineno, tool="arkts",
                                   file=safe_file if safe_file == m.group("file") else None, line=int(m.group("line")),
                                   column=int(m.group("col")))
            continue
        m = _ARKTS_PLAIN_HEADER.match(line)
        if m:
            _flush(current, findings, stream, counters)
            current = _new_finding(m.group("sev"), lineno, tool="arkts")
            _append_message_line(current, _redact_line(m.group("msg"), counters), lineno)
            continue
        m = _GENERIC_HEADER.match(line)
        if m:
            _flush(current, findings, stream, counters)
            current = _new_finding(m.group("sev"), lineno)
            _append_message_line(current, _redact_line(m.group("msg"), counters), lineno)
            continue
        if _BARE_ERROR.search(line):
            _flush(current, findings, stream, counters)
            current = _new_finding("ERROR", lineno)
            _append_message_line(current, _redact_line(line, counters), lineno)
            continue
        if line.strip() == "":
            _flush(current, findings, stream, counters)
            current = None
            continue
        if current is not None:
            _append_message_line(current, _redact_line(line, counters), lineno)
    _flush(current, findings, stream, counters)
    return findings, markers


def analyze(stdout_path, stderr_path=None, returncode=None, target=None,
            log_encoding: str = "utf-8", decode_errors: str = "replace") -> dict[str, Any]:
    """Analyze real build logs plus the real process returncode.

    ``stdout_path``/``stderr_path`` are paths to captured logs (at least one is
    required); both files are read once, hashed and never modified. ``returncode``
    must be the actual exit code (int) or None (e.g. timeout). ``target`` is an
    optional bounded module/module_target/product identity dict. Returns a JSON-safe
    report dict; see docs/harmony-build-diagnostics.md.
    """
    if stdout_path is None and stderr_path is None:
        raise MigrationError("Provide at least one of stdout_path or stderr_path")
    if isinstance(returncode, bool) or not (returncode is None or isinstance(returncode, int)):
        raise MigrationError("returncode must be an int or None")
    if target is not None:
        if not isinstance(target, dict):
            raise MigrationError("target must be a dict of identity fields or None")
        if set(target) - {"module", "module_target", "product"}:
            raise MigrationError("target permits only module, module_target and product identity fields")
        for value in target.values():
            if (not isinstance(value, str) or re.fullmatch(r"[A-Za-z0-9_-]{1,128}", value) is None
                    or _TOKEN_LITERAL.search(value)):
                raise MigrationError("target identity values must be bounded identifiers without credential patterns")
    if not isinstance(log_encoding, str) or not isinstance(decode_errors, str):
        raise MigrationError("log_encoding and decode_errors must be strings")
    logs: dict[str, dict[str, Any]] = {}
    findings: list[dict[str, Any]] = []
    markers = {"build_successful": False, "build_failed": False}
    counters = {"truncated": False, "redacted": 0, "error_marker": False}
    for stream, path in (("stdout", stdout_path), ("stderr", stderr_path)):
        if path is None:
            continue
        file = Path(path)
        if not file.is_file():
            raise MigrationError("Log file not found: %s: %s" % (stream, file))
        raw = io_path(file).read_bytes()
        try:
            text = raw.decode(log_encoding, errors=decode_errors)
        except (LookupError, UnicodeError) as exc:
            raise MigrationError("Cannot decode %s log with %s: %s" % (stream, log_encoding, exc)) from exc
        stream_findings, stream_markers = _scan_stream(text.lstrip("\ufeff").splitlines(), stream, counters)
        findings.extend(stream_findings)
        markers["build_successful"] = markers["build_successful"] or stream_markers["build_successful"]
        markers["build_failed"] = markers["build_failed"] or stream_markers["build_failed"]
        logs[stream] = {"path": str(file.resolve()), "sha256": digest(raw), "bytes": len(raw)}
    errors = [f for f in findings if f["severity"] == "error"]
    if returncode == 0:
        conflict = bool(errors or markers["build_failed"] or counters["error_marker"])
        build_passed = not conflict
        status = "conflicting_build_evidence" if conflict else "build_command_passed"
    else:
        build_passed = False
        status = "fail_with_errors" if errors else "fail_unparsed"
    notes: list[str] = []
    if returncode == 0:
        notes.append("returncode=0 only indicates the build command exited 0; functionality, UI and device behavior are NOT verified by this report.")
        if not build_passed:
            notes.append("Zero process exit conflicts with ERROR/FATAL or BUILD FAILED evidence; no build acceptance is inferred.")
    else:
        rc_text = "None" if returncode is None else str(returncode)
        if status == "fail_unparsed":
            notes.append("returncode=%s with no parseable compiler error in the logs; treated as failed with unknown cause and never reported as PASS." % rc_text)
        else:
            notes.append("returncode=%s; parsed compiler errors are listed in findings." % rc_text)
    if markers["build_successful"]:
        notes.append("Log contains a BUILD SUCCESSFUL marker.")
    if markers["build_failed"]:
        notes.append("Log contains a BUILD FAILED marker.")
    if counters["redacted"]:
        notes.append("%d credential-like log line(s) were redacted and not copied into this report." % counters["redacted"])
    if counters["truncated"]:
        notes.append("Findings truncated at %d; inspect the original logs for more errors." % _MAX_FINDINGS)
    categories: dict[str, int] = {}
    tools: dict[str, int] = {}
    for finding in findings:
        categories[finding["category"]] = categories.get(finding["category"], 0) + 1
        tools[finding["tool"]] = tools.get(finding["tool"], 0) + 1
    return {
        "schema_version": SCHEMA,
        "report_kind": _REPORT_KIND,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "target": dict(target) if target else None,
        "returncode": returncode,
        "process_exit_zero": returncode == 0,
        "logs": logs,
        "log_encoding": log_encoding,
        "decode_errors": decode_errors,
        "markers": markers,
        "status": status,
        "overall_status": "conflict" if status == "conflicting_build_evidence" else "unknown" if returncode == 0 else "fail",
        "build_command_passed": build_passed,
        "functional_verified": False,
        "ui_verified": False,
        "status_notes": notes,
        "findings": findings,
        "summary": {"errors": len(errors), "warnings": len(findings) - len(errors),
                    "categories": categories, "tools": tools,
                    "truncated": counters["truncated"]},
        "redacted_lines": counters["redacted"],
        "api_contract": dict(_API_CONTRACT),
        "limitations": list(_LIMITATIONS),
    }


def save_report(report: dict[str, Any], path) -> Path:
    """Persist a report as deterministic UTF-8 JSON; returns the output path."""
    _validate_report_logs(report)
    out = Path(path)
    actual = io_path(out).resolve()
    for entry in report["logs"].values():
        source = io_path(Path(entry["path"]))
        if actual == source.resolve() or (actual.exists() and source.exists() and actual.samefile(source)):
            raise MigrationError("Report output must not overwrite an input log or its alias")
    atomic_write(out, json_bytes(report))
    return out


def _validate_report_logs(report: dict[str, Any]) -> None:
    if not isinstance(report, dict) or report.get("report_kind") != _REPORT_KIND:
        raise MigrationError("Not a harmony build diagnostics report")
    logs = report.get("logs")
    if not isinstance(logs, dict) or not logs or set(logs) - {"stdout", "stderr"}:
        raise MigrationError("Diagnostics report must identify its input logs")
    if any(not isinstance(entry, dict) or not isinstance(entry.get("path"), str) or not entry["path"]
           or not isinstance(entry.get("sha256"), str) or re.fullmatch(r"[0-9a-f]{64}", entry["sha256"]) is None
           for entry in logs.values()):
        raise MigrationError("Invalid diagnostics input log identity")


def verify(report: dict[str, Any]) -> bool:
    """True iff every recorded log file still exists with its original SHA-256.

    Raises MigrationError for payloads that are not harmony build diagnostics
    reports. Returns False when any log changed, moved or disappeared, so saved
    reports can be re-validated against the source logs at any time.
    """
    _validate_report_logs(report)
    logs = report.get("logs") or {}
    if not logs:
        return False
    for entry in logs.values():
        path = entry.get("path") if isinstance(entry, dict) else None
        if not path:
            return False
        file = Path(path)
        if not file.is_file():
            return False
        if digest(io_path(file).read_bytes()) != entry.get("sha256"):
            return False
    return True
