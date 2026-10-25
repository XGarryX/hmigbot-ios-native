"""A deliberately closed SwiftUI grammar, not a general Swift compiler.

No unrecognized statement or modifier is dropped during lowering. The lexer is
also used for *lexical* inventory, never advertised as compiler-resolved facts.
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
EXTENDED_REGEX_LITERAL = re.compile(r"#+/")


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
        elif text[pos] == '#' and EXTENDED_REGEX_LITERAL.match(text, pos):
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


def _string_end(text, start, depth=0):
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
            if quotes == 1 and following < len(text) and text[following] in '\r\n':
                # Swift's escaped-newline production belongs only to multiline
                # strings; an escape cannot continue a single-line literal.
                raise MigrationError(
                    f"Unterminated string at line {text.count(chr(10), 0, start) + 1}")
            if following < len(text) and text[following] == '(':
                if depth + 1 > SUPPORTED_STRING_NESTING_DEPTH:
                    raise RequiresSyntaxProvider(
                        f"Deep string interpolation nesting exceeds supported bound of "
                        f"{SUPPORTED_STRING_NESTING_DEPTH}; requires syntax provider at line "
                        f"{text.count(chr(10), 0, start) + 1}")
                pos = _interpolation_end(text, following + 1, depth)
            else:
                pos = following + 1
        else:
            if quotes == 1 and text[pos] in '\r\n':
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


def tokenize(text: str) -> list[Token]:
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
        elif char == '#' and EXTENDED_REGEX_LITERAL.match(text, pos):
            # Reject at the opener, before a #// pattern can be mistaken for a
            # line comment and erase valid declarations later on the same line.
            raise RequiresSyntaxProvider(
                f"Regex literal requires syntax provider at line {line}")
        elif _string_opening(text, pos) is not None:
            start, start_line = pos, line
            pos, hashes, quotes = _string_end(text, pos, 0)
            value = text[start:pos]
            line += value.count("\n")
            result.append(Token(value, start_line, "string", hashes, quotes, line, start, pos))
        else:
            match = re.match(r"[A-Za-z_][A-Za-z_0-9]*|[0-9]+(?:\.[0-9]+)?|\+=|-=|==|->", text[pos:])
            value = match.group() if match else char
            kind = "identifier" if re.fullmatch(r"[A-Za-z_][A-Za-z_0-9]*", value) else "symbol"
            result.append(Token(value, line, kind, end_line=line, start=pos, end=pos + len(value)))
            pos += len(value)
    return result


class Unsupported(MigrationError):
    pass


class RequiresSyntaxProvider(MigrationError):
    """A Swift construct that is legal but outside this closed grammar's resolve set.

    It must be handled by the official SwiftSyntax provider, not by this lexer.
    """


class Parser:
    def __init__(self, text):
        self.tokens = tokenize(text)
        self.pos = 0
        self.states = {}

    def peek(self):
        return self.tokens[self.pos].value if self.pos < len(self.tokens) else "<eof>"

    def error(self, message):
        line = self.tokens[min(self.pos, len(self.tokens) - 1)].line if self.tokens else 1
        raise Unsupported(f"line {line}: {message}; found {self.peek()}")

    def take(self, expected=None):
        if self.pos == len(self.tokens) or (expected is not None and self.peek() != expected):
            self.error(f"expected {expected}")
        result = self.tokens[self.pos]
        self.pos += 1
        return result

    def accept(self, value):
        if self.peek() == value:
            self.pos += 1
            return True
        return False

    def identifier(self):
        token = self.take()
        if token.kind != "identifier":
            self.error("expected identifier")
        # Preserve exact names in facts; reject ArkTS special member names in codegen.
        if token.value in {"build", "constructor", "aboutToAppear", "aboutToDisappear", "Index",
                           "Text", "Button", "VStack", "HStack", "ZStack", "Spacer", "Divider",
                           "class", "struct", "interface", "function", "private", "public", "this", "var", "let"}:
            self.error("identifier collides with target component lifecycle")
        return token.value

    def number(self, integer=False):
        sign = -1 if self.accept("-") else 1
        raw = self.take().value
        if not re.fullmatch(r"\d+" if integer else r"\d+(?:\.\d+)?", raw):
            self.error("expected numeric literal")
        number = sign * (int(raw) if "." not in raw else float(raw))
        if abs(number) > 2**53 - 1:
            self.error("number exceeds exact ArkTS integer range")
        return number

    def text_literal(self, interpolate=False):
        token = self.take()
        if token.kind == "string" and token.hash_count:
            self.error("extended-delimiter string literals require a Swift semantic adapter")
        if token.kind != "string" or token.quote_count == 3:
            self.error("only single-line string literals are supported")
        raw = token.value[1:-1]
        pieces, start = [], 0
        # Interpolation is parsed before JSON escapes, allowing only a state identifier.
        for match in re.finditer(r"\\\(([^)]*)\)", raw):
            if not interpolate or match.group(1) not in self.states:
                self.error("only declared integer-state interpolation is supported")
            try:
                prefix = json.loads('"' + raw[start:match.start()] + '"')
            except json.JSONDecodeError:
                self.error("unsupported Swift string escape")
            pieces.append({"literal": prefix})
            pieces.append({"state": match.group(1)})
            start = match.end()
        try:
            pieces.append({"literal": json.loads('"' + raw[start:] + '"')})
        except json.JSONDecodeError:
            self.error("unsupported Swift string escape")
        return pieces

    def parse(self):
        while self.accept("import"):
            if self.take().value != "SwiftUI":
                self.error("only import SwiftUI is permitted by this conversion rule")
        self.take("struct")
        name = self.identifier()
        self.take(":")
        self.take("View")
        self.take("{")
        while self.accept("@"):
            self.take("State")
            self.accept("private")
            self.take("var")
            state = self.identifier()
            if self.accept(":"):
                self.take("Int")
            self.take("=")
            initial = self.number(integer=True)
            if state in self.states:
                self.error("duplicate state")
            self.states[state] = initial
        self.take("var")
        self.take("body")
        self.take(":")
        self.take("some")
        self.take("View")
        self.take("{")
        root = self.node()
        self.take("}")
        self.take("}")
        if self.peek() != "<eof>":
            self.error("additional declarations require a semantic adapter")
        return {"name": name, "states": self.states, "root": root,
                "rule": "swiftui-literal-and-int-state/1",
                "limitations": ["Layout units, typography and default spacing need visual validation",
                                "String localization requires a separate localization mapping",
                                "Swift Int overflow and large integer behavior are not equivalent",
                                "Navigation, lifecycle and app entry are outside this page rule"]}

    def node(self):
        start = self.take()
        kind = start.value
        node = {"kind": kind, "line": start.line, "modifiers": [], "children": []}
        if kind in {"VStack", "HStack", "ZStack"}:
            if self.accept("("):
                if not self.accept(")"):
                    self.take("spacing")
                    self.take(":")
                    if kind == "ZStack":
                        self.error("ZStack spacing is not valid")
                    node["spacing"] = self.number()
                    self.take(")")
            self.take("{")
            while self.peek() not in {"}", "<eof>"}:
                node["children"].append(self.node())
            self.take("}")
        elif kind == "Text":
            self.take("(")
            if self.accept("verbatim"):
                self.take(":")
                node["verbatim"] = True
            node["text"] = self.text_literal(interpolate=True)
            self.take(")")
        elif kind == "Image":
            self.take("(")
            pieces = self.text_literal()
            node["asset_name"] = ''.join(p['literal'] for p in pieces)
            self.take(")")
        elif kind == "Button":
            self.take("(")
            node["text"] = self.text_literal()
            self.take(")")
            self.take("{")
            state = self.identifier()
            if state not in self.states:
                self.error("button can only modify a declared integer state")
            operation = self.take().value
            if operation not in {"+=", "-=", "="}:
                self.error("only integer assignment/add/subtract actions are supported")
            node["action"] = {"state": state, "operator": operation, "value": self.number(integer=True)}
            self.take("}")
        elif kind in {"Spacer", "Divider"}:
            self.take("(")
            self.take(")")
        else:
            self.error(f"unsupported view {kind}")
        while self.accept("."):
            modifier = self.take().value
            self.take("(")
            if modifier == "padding":
                value = self.number()
                if value < 0:
                    self.error("negative padding needs a layout rule")
                node["modifiers"].append({"name": "padding", "value": value})
            elif modifier == "frame":
                seen = set()
                while True:
                    axis = self.take().value
                    if axis not in {"width", "height"} or axis in seen:
                        self.error("frame accepts unique width/height literals only")
                    seen.add(axis)
                    self.take(":")
                    value = self.number()
                    if value < 0:
                        self.error("negative dimensions are not supported")
                    node["modifiers"].append({"name": axis, "value": value})
                    if not self.accept(","):
                        break
            else:
                self.error(f"unsupported modifier {modifier}")
            self.take(")")
        attributes = [m["name"] for m in node["modifiers"]]
        if len(attributes) != len(set(attributes)):
            self.error("repeated layout modifiers need composition-aware lowering")
        return node


def parse_view(text):
    return Parser(text).parse()


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
