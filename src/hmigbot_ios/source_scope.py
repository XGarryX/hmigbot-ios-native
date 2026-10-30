"""Conservative lexical scope locators; never a compiler membership claim."""
from pathlib import Path
import plistlib
from xml.parsers.expat import ExpatError

from .swiftui import tokenize
from .core import MigrationError, digest

PLIST_SUFFIXES = {'.plist', '.entitlements', '.xcprivacy', '.stringsdict'}


def source_anchor_info(path: Path, *, raw: bytes | None = None):
    """Read source coordinates using the file's real format.

    A binary property list is one resource document, never a pretend UTF-8
    line. Its coordinate must be bound to the original bytes by SHA-256.
    XML property lists retain line coordinates when they are UTF-8. Other
    source text is decoded strictly; corrupt code must still block review.
    """
    path = Path(path)
    raw = path.read_bytes() if raw is None else raw
    info = {}
    if path.suffix.lower() in PLIST_SUFFIXES:
        try:
            value = plistlib.loads(raw)
        except (ValueError, OverflowError, ExpatError) as exc:
            raise MigrationError('Invalid property-list resource: ' + str(path) + ': ' + str(exc)) from exc
        info.update(format='plist', root_type=type(value).__name__, content_validation='parsed')
        binary = raw.startswith(b'bplist00')
        try:
            text = raw.decode('utf-8-sig') if not binary else None
        except UnicodeError:
            text = None  # Valid XML may declare another encoding; plistlib parsed it above.
        if text is None:
            return {**info, 'line_count': 1, 'coordinate_kind': 'resource_document',
                    'source_sha256': digest(raw), 'encoding': 'binary' if binary else 'xml'}
    else:
        text = raw.decode('utf-8-sig')
    return {**info, 'line_count': max(1, len(text.splitlines())), 'coordinate_kind': 'text_line'}


def import_token_lines(tokens):
    """Locate dependency directives, including attributed imports, without string scans."""
    return {token.line for token in tokens if token.kind != 'string' and token.value == 'import'}


def preview_source_lines(path: Path, *, tokens=None, project=None, source=None):
    """Only Swift source can carry the supported SwiftUI Preview scopes.

    Resources retain their ordinary obligations. In particular, plist metadata
    is not UTF-8 source text; its format parser owns content interpretation.
    Decode errors in actual Swift remain errors rather than exclusions.
    """
    if path.suffix != '.swift':
        return set()
    if tokens is None and project is not None:
        from .swift_native import project_syntax, source_tokens
        tokens = source_tokens(source, path.relative_to(source).as_posix(), project_syntax(project, source))
    return preview_lines(path.read_text(encoding='utf-8-sig'), tokens=tokens)


def preview_lines(text, *, tokens=None):
    tokens = tokenize(text) if tokens is None else tokens
    result = set()
    for i, token in enumerate(tokens):
        if token.kind == 'string':
            continue
        macro = token.value == '#' and i + 1 < len(tokens) and tokens[i + 1].value == 'Preview'
        header = []
        if token.value == 'struct':
            for item in tokens[i + 1:]:
                if item.value == '{':
                    break
                header.append(item.value)
        provider = ':' in header and 'PreviewProvider' in header
        if not (macro or provider):
            continue
        start = next((j for j in range(i + 1, len(tokens)) if tokens[j].kind != 'string' and tokens[j].value == '{'), None)
        if start is None:
            continue
        depth = 0
        for j in range(start, len(tokens)):
            if tokens[j].kind == 'string':
                continue
            depth += tokens[j].value == '{'
            depth -= tokens[j].value == '}'
            if depth == 0:
                result.update(range(token.line, tokens[j].line + 1))
                break
    return result
