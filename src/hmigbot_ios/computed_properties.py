"""Conservative computed-property token locators, not a Swift semantic parser.

The caller must establish member/owner scope. A match only locates an explicit
type and implementation braces; it never evaluates a derived value or proves
that the declaration compiles. Unsupported forms return None for provider review.
"""
from __future__ import annotations


_DECLARATION_BOUNDARIES = {
    "var", "let", "func", "init", "deinit", "subscript", "class", "struct",
    "enum", "extension", "protocol", "import", "where", "return", "if",
    "guard", "switch", "for", "while", "case", "get", "set", "didSet", "willSet",
}
_TYPE_SYMBOLS = {".", "?", "!", "&", "->", ",", ":"}
_PAIRS = {"(": ")", "[": "]", "<": ">"}


def _brace_end(tokens, start):
    depth = 0
    for index in range(start, len(tokens)):
        token = tokens[index]
        if token.kind == "string":
            continue
        depth += token.value == "{"
        depth -= token.value == "}"
        if depth == 0:
            return index
    return None


def _accessors(tokens, start, end):
    """Locate explicit accessor implementations; requirements have no body."""
    result = []
    cursor = start
    while cursor < end:
        head = cursor
        modifiers = []
        while cursor < end and tokens[cursor].value in {"mutating", "nonmutating"}:
            modifiers.append(tokens[cursor].value)
            cursor += 1
        if cursor >= end or tokens[cursor].kind == "string" or tokens[cursor].value not in {"get", "set"}:
            return None
        kind = tokens[cursor].value
        cursor += 1
        parameter = None
        if kind == "set" and cursor < end and tokens[cursor].value == "(":
            if (cursor + 2 >= end or tokens[cursor + 1].kind != "identifier"
                    or tokens[cursor + 2].value != ")"):
                return None
            parameter = tokens[cursor + 1].value
            cursor += 3
        effects = []
        while cursor < end and tokens[cursor].value in {"async", "throws", "rethrows"}:
            effects.append(tokens[cursor].value)
            cursor += 1
        if cursor >= end or tokens[cursor].value != "{":
            return None  # e.g. protocol { get set }, or unsupported typed throws.
        close = _brace_end(tokens, cursor)
        if close is None or close >= end:
            return None
        result.append({"kind": kind, "line": tokens[head].line,
                       "end_line": tokens[close].line, "modifiers": modifiers,
                       "effects": effects, "parameter": parameter,
                       "body_start_token": cursor, "body_end_token": close})
        cursor = close + 1
    kinds = [item["kind"] for item in result]
    if "get" not in kinds or len(kinds) != len(set(kinds)):
        return None
    return result


def computed_property(tokens, index):
    """Return unresolved evidence for simple ``var name: Type { body }``.

    Token indices in accessor_evidence are inclusive, with source line bounds.
    Comments must already be removed by swiftui.tokenize; string tokens remain
    opaque. Local declarations may match: ownership is solely the caller's job.
    Initializers, observers, requirements, destructuring, attributes within the
    type and incomplete/unbalanced declarations are deliberately not classified.
    """
    if (index < 0 or index + 3 >= len(tokens) or tokens[index].kind != "identifier"
            or tokens[index].value != "var" or tokens[index + 1].kind != "identifier"
            or tokens[index + 1].value in _DECLARATION_BOUNDARIES | {"_"}
            or tokens[index + 2].value != ":"):
        return None
    type_start = index + 3
    cursor, stack = type_start, []
    while cursor < len(tokens):
        token = tokens[cursor]
        value = token.value
        if token.kind == "string" or value in _DECLARATION_BOUNDARIES or value in {"=", ";", "}"}:
            return None
        if value == "{":
            if stack or cursor == type_start:
                return None
            break
        if value in _PAIRS:
            stack.append(_PAIRS[value])
        elif value in _PAIRS.values():
            if not stack or stack.pop() != value:
                return None
        elif token.kind != "identifier" and value not in _TYPE_SYMBOLS:
            return None
        cursor += 1
    else:
        return None
    close = _brace_end(tokens, cursor)
    if close is None or close == cursor + 1:
        return None
    first = tokens[cursor + 1]
    if first.kind != "string" and first.value in {"didSet", "willSet", "@", "_read", "_modify"}:
        return None  # Observers and unsupported accessor forms need provider review.
    explicit = first.kind != "string" and first.value in {"get", "set", "mutating", "nonmutating"}
    if explicit:
        accessors = _accessors(tokens, cursor + 1, close)
        if accessors is None:
            return None
    else:
        accessors = [{"kind": "implicit_get", "line": first.line,
                      "end_line": tokens[close - 1].end_line or tokens[close - 1].line,
                      "body_start_token": cursor + 1, "body_end_token": close - 1,
                      "effects": []}]
    type_tokens = [token.value for token in tokens[type_start:cursor]]
    symbol = tokens[index + 1].value
    return {"symbol": symbol, "type": " ".join(type_tokens),
            "line": tokens[index].line, "end_line": tokens[close].line,
            "storage": "computed_property", "initializer": None,
            "resolution": "token_signal", "semantics": "unresolved",
            "property_role": "rendering_property" if symbol == "body" and type_tokens == ["some", "View"] else "derived_property",
            "accessor_evidence": {"kind": "explicit_accessors" if explicit else "implicit_getter",
                                  "body_start_token": cursor, "body_end_token": close,
                                  "accessors": accessors, "semantics": "unresolved"}}
