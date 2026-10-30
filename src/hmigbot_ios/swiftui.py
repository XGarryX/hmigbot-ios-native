"""ArkUI emission plus the explicit static compatibility lexer.

SwiftUI lowering prefers SwiftParser AST. Standalone inventory may explicitly
use weak_swiftui after native failure, producing marked, unverified drafts.
The static lexer never certifies Swift syntax.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
import re

from .core import MigrationError

# Closed-grammar supported bounds. Swift itself permits deeper nesting, but the
# deterministic lexer refuses to resolve beyond these bounds and reports a stable
# "requires syntax provider" diagnostic instead of crashing (RecursionError) or
# emitting a misleading "Unterminated ..." error. Deep nesting is legal Swift but
# outside this grammar's resolve set, so it is reported, not silently accepted.
SUPPORTED_INTERPOLATION_DEPTH = 64
SUPPORTED_STRING_NESTING_DEPTH = 64


@dataclass(frozen=True)
class Token:
    value: str
    line: int
    kind: str = "symbol"
    hash_count: int = 0
    quote_count: int = 0
    end_line: int = 0
    start: int = 0
    end: int = 0


def _string_opening(text, pos):
    """Recognize Swift string delimiters without consuming a standalone macro #."""
    quote = pos
    while quote < len(text) and text[quote] == '#':
        quote += 1
    if quote >= len(text) or text[quote] != '"':
        return None
    return quote - pos, 3 if text.startswith('"""', quote) else 1


def _block_comment_end(text, start):
    depth, pos = 1, start + 2
    while depth and pos < len(text):
        if text.startswith('/*', pos):
            depth += 1
            pos += 2
        elif text.startswith('*/', pos):
            depth -= 1
            pos += 2
        else:
            pos += 1
    if depth:
        raise MigrationError(f"Unterminated comment at line {text.count(chr(10), 0, start) + 1}")
    return pos


def _interpolation_end(text, start, depth):
    """Skip a complete interpolation; its expressions stay inside the string token.

    This only preserves lexical boundaries. It does not bind/evaluate Swift
    expressions or claim their runtime value is known.

    ``depth`` counts surrounding nested strings; interpolation parentheses have
    their own bound. Both limits protect the closed grammar before Python's
    recursion limit, without declaring deeply nested Swift invalid.
    """
    nest_depth, pos = 1, start
    while pos < len(text):
        if text.startswith('//', pos):
            end = text.find('\n', pos)
            pos = len(text) if end == -1 else end
        elif text.startswith('/*', pos):
            pos = _block_comment_end(text, pos)
        elif text[pos] == '#' and re.match(r'#+/', text[pos:]):
            # Regex contents can contain parentheses, quotes and comment-like
            # text. This lexer cannot assign their expression boundaries.
            raise RequiresSyntaxProvider(
                f"Regex literal requires syntax provider at line "
                f"{text.count(chr(10), 0, pos) + 1}")
        elif _string_opening(text, pos) is not None:
            pos, _, _ = _string_end(text, pos, depth + 1)
        elif text[pos] == '(':
            nest_depth += 1
            if nest_depth > SUPPORTED_INTERPOLATION_DEPTH:
                raise RequiresSyntaxProvider(
                    f"interpolation nesting exceeds supported bound of "
                    f"{SUPPORTED_INTERPOLATION_DEPTH}; requires syntax provider at line "
                    f"{text.count(chr(10), 0, start) + 1}")
            pos += 1
        elif text[pos] == ')':
            nest_depth -= 1
            pos += 1
            if not nest_depth:
                return pos
        else:
            pos += 1
    raise MigrationError(f"Unterminated interpolation at line {text.count(chr(10), 0, start) + 1}")


def _string_end(text, start, depth=0, *, swift=True):
    hashes, quotes = _string_opening(text, start)
    closing = '"' * quotes + '#' * hashes
    escape = '\\' + '#' * hashes
    pos = start + hashes + quotes
    in_interpolation = depth > 0
    while pos < len(text):
        if text.startswith(closing, pos):
            return pos + len(closing), hashes, quotes
        if text.startswith(escape, pos):
            following = pos + len(escape)
            if swift and quotes == 1 and following < len(text) and text[following] in '\r\n':
                # Swift's escaped-newline production belongs only to multiline
                # strings; an escape cannot continue a single-line literal.
                raise MigrationError(
                    f"Unterminated string at line {text.count(chr(10), 0, start) + 1}")
            if swift and following < len(text) and text[following] == '(':
                if depth + 1 > SUPPORTED_STRING_NESTING_DEPTH:
                    raise RequiresSyntaxProvider(
                        f"Deep string interpolation nesting exceeds supported bound of "
                        f"{SUPPORTED_STRING_NESTING_DEPTH}; requires syntax provider at line "
                        f"{text.count(chr(10), 0, start) + 1}")
                pos = _interpolation_end(text, following + 1, depth)
            else:
                pos = following + 1
        else:
            if swift and quotes == 1 and text[pos] in '\r\n':
                # A raw newline inside a single-line string means the closing
                # quote is missing on this line: genuinely unterminated.
                raise MigrationError(
                    f"Unterminated string at line {text.count(chr(10), 0, start) + 1}")
            pos += 1
    # Reached end of text while still scanning this string.
    if in_interpolation:
        # An open interpolation was never closed: the interpolation error is the
        # specific, stable diagnostic (not the phantom nested string's error).
        raise MigrationError(
            f"Unterminated string interpolation at line {text.count(chr(10), 0, start) + 1}")
    raise MigrationError(f"Unterminated string at line {text.count(chr(10), 0, start) + 1}")


def tokenize(text: str, *, skip_pragma_marks: bool = False, language: str = "swift") -> list[Token]:
    result, pos, line = [], 0, 1
    while pos < len(text):
        char = text[pos]
        if char.isspace():
            line += char == "\n"
            pos += 1
        elif text.startswith("//", pos):
            end = text.find("\n", pos)
            pos = len(text) if end == -1 else end
        elif text.startswith("/*", pos):
            start = pos
            pos = _block_comment_end(text, pos)
            line += text[start:pos].count("\n")
        elif _string_opening(text, pos) is not None:
            start, start_line = pos, line
            pos, hashes, quotes = _string_end(text, pos, 0, swift=language == "swift" and not skip_pragma_marks)
            value = text[start:pos]
            line += value.count("\n")
            result.append(Token(value, start_line, "string", hashes, quotes, line, start, pos))
        elif (skip_pragma_marks and char == "#"
              and not text[text.rfind("\n", 0, pos) + 1:pos].strip()
              and re.match(r"#[ \t]*pragma[ \t]+mark\b", text[pos:])):
            # C/Objective-C section headings are metadata, not executable tokens.
            # Recognize them only outside comments/strings and preserve source lines.
            while pos < len(text):
                end = text.find("\n", pos)
                if end == -1:
                    pos = len(text)
                    break
                continued = text[pos:end].removesuffix("\r").endswith("\\")
                pos = end + 1
                line += 1
                if not continued:
                    break
        else:
            match = re.match(r"[A-Za-z_][A-Za-z_0-9]*|[0-9]+(?:\.[0-9]+)?|\+=|-=|==|->", text[pos:])
            value = match.group() if match else char
            kind = "identifier" if re.fullmatch(r"[A-Za-z_][A-Za-z_0-9]*", value) else "symbol"
            result.append(Token(value, line, kind))
            pos += len(value)
    return result


class Unsupported(MigrationError):
    pass


class RequiresSyntaxProvider(MigrationError):
    """A Swift construct that is legal but outside this closed grammar's resolve set.

    It must be handled by the official SwiftSyntax provider, not by this lexer.
    """


def parse_view(text, *, syntax=None):
    """Map the actual SwiftParser AST through the bounded ArkUI target rule.

    The former Python SwiftUI parser has been removed. No static lexer fallback
    can certify that a page is covered by the conversion rule.
    """
    from .swift_native import parse_sources, SwiftEvidenceError
    from .core import digest
    syntax = parse_sources({'View.swift': text})['View.swift'] if syntax is None else syntax
    if syntax.get('sha256') != digest(text.encode('utf-8')):
        raise SwiftEvidenceError('SwiftSyntax lowering source changed')
    lowering = syntax.get('arkui_rule', {})
    if lowering.get('status') != 'mapped':
        raise Unsupported(lowering.get('reason', 'SwiftSyntax provider has no ArkUI AST rule output'))
    if syntax.get('parse_has_error') is not False:
        raise Unsupported('SwiftParser rejected source syntax')
    return lowering['view']


def emit_expression(pieces):
    values = [f"this.{p['state']}.toString()" if "state" in p else json.dumps(p["literal"], ensure_ascii=False)
              for p in pieces if "state" in p or p.get("literal")]
    return " + ".join(values) or '""'


def emit_view(view, entry=False):
    names = {"VStack": "Column", "HStack": "Row", "ZStack": "Stack", "Spacer": "Blank"}
    lines = ["// Generated by hmigbot-ios. Draft; build and behavior validation required."]
    if entry:
        lines.append("@Entry")
    lines += ["@Component", f"struct {view['name']} {{"]
    for name, initial in view["states"].items():
        lines.append(f"  @State {name}: number = {initial}")
    lines.append("  build() {")
    def emit(node, indent):
        pad = " " * indent
        kind = names.get(node["kind"], node["kind"])
        arguments = emit_expression(node["text"]) if "text" in node else ""
        if "resource" in node:
            arguments = '$r(' + json.dumps(node['resource']) + ')'
        if node['kind'] == 'Image' and 'resource' not in node:
            raise MigrationError('Image requires a validated asset-convert bundle: ' + node['asset_name'])
        if "spacing" in node:
            arguments = "{ space: " + str(node["spacing"]) + " }"
        if node["kind"] in {"VStack", "HStack", "ZStack"}:
            lines.append(f"{pad}{kind}({arguments}) {{")
            for child in node["children"]:
                emit(child, indent + 2)
            lines.append(f"{pad}}}")
        else:
            lines.append(f"{pad}{kind}({arguments})")
        for modifier in node["modifiers"]:
            lines.append(f"{pad}  .{modifier['name']}({modifier['value']})")
        if "action" in node:
            action = node["action"]
            lines.append(f"{pad}  .onClick(() => {{ this.{action['state']} {action['operator']} {action['value']} }})")
    emit(view["root"], 4)
    lines += ["  }", "}", ""]
    return "\n".join(lines)
