"""Canonical lexical source candidates; never compiler binding or approved scope."""
from pathlib import Path
import re
from .core import MigrationError, safe_child
from .swiftui import tokenize
CODE = {".swift", ".m", ".mm", ".h", ".c", ".cpp"}
DECL_KEYWORDS = {'struct', 'class', 'enum', 'actor', 'extension'}
BRIDGE_SYMBOLS = ('UIViewRepresentable', 'UIViewControllerRepresentable', 'UIHostingController')
UIKIT_BASE = ('UIViewController', 'UINavigationController', 'UITableViewController',
              'UICollectionViewController', 'UISplitViewController', 'UITabBarController', 'UITableViewCell', 'UICollectionViewCell', 'UIView')
SCAFFOLD_BANNER = (
    "脚手架候选（scaffold candidate）。非已验收规格：spec_complete=false，"
    "behavior_verified=false，needs_review=true。"
    "未经独立源码/内容审查与 source-check --harness 不得进入 plan。"
)
UNKNOWN_BANNER = (
    "未知模板(Unknown template)：未识别为 UI 页面，不列入可进入 plan 的页面，"
    "需审查者确认其 UI 语义后再决定是否成页。"
)


# --------------------------------------------------------------------------- #
# Source discovery (header-scoped, comment/string immune)
# --------------------------------------------------------------------------- #
def _header_values(tokens, start, end):
    """Non-string token values of a declaration header (keyword .. opening brace)."""
    return [t.value for t in tokens[start:end] if t.kind != 'string']


def _top_level_types(text, *, language='swift'):
    """Compatibility entry; Swift declarations come exclusively from SwiftParser."""
    if language != 'swift':
        return _top_level_c_types(tokenize(text, language='c', skip_pragma_marks=True))
    from .swift_native import parse_sources, tokens_for
    file = parse_sources({'Types.swift': text})['Types.swift']
    tokens_for(file, text)
    result = []
    for node in file['nodes']:
        value = node['value']
        if node['kind'] not in {'type', 'extension'} or value.get('top_level') is not True:
            continue
        kind, name = value.get('kind', 'extension'), value.get('name', value.get('type'))
        header = [kind, name]
        for i, inherited in enumerate(value.get('inherits', [])):
            header.extend([':' if i == 0 else ',', inherited])
        result.append((name, kind, node['line'], header))
    return result


def _top_level_c_types(tokens):
    """Return ``(name, decl_kind, line, header_values)`` for each top-level type.

    Uses the token stack discipline from ``ios_facts``: a declaration only becomes a
    candidate when its opening brace lifts the depth 0 -> 1, so nested types are
    ignored. ``header_values`` carries only the declaration's own signature tokens,
    excluding comments and string literals.
    """
    found, pending_owner, decl_kind, decl_start, depth = [], None, None, None, 0
    for i, tok in enumerate(tokens):
        v = tok.value
        if v in DECL_KEYWORDS and i + 1 < len(tokens) and tokens[i + 1].kind != 'string':
            name = None
            for nxt in tokens[i + 1:i + 4]:
                if nxt.kind == 'string' or nxt.value in {':', 'where'}:
                    break
                if re.match(r'^[A-Za-z_]\w*$', nxt.value):
                    name = nxt.value
                    break
            if name:
                pending_owner, decl_kind, decl_start = name, v, i
        if v == '{':
            depth += 1
            if pending_owner is not None and depth == 1:
                found.append((pending_owner, decl_kind, tok.line, _header_values(tokens, decl_start, i)))
            pending_owner = None
        elif v == '}':
            if depth > 0:
                depth -= 1
    return found


def _has_conformance(header_values, name):
    """True only if ``name`` is an inherited type in THIS declaration's header.

    Conformances appear as ``: Name`` or ``, Name`` in the inheritance list, so the
    preceding token must be ``:`` or ``,``. Comments/strings are already excluded.
    """
    for i, v in enumerate(header_values):
        if v == name and i > 0 and header_values[i - 1] in (':', ','):
            return True
    return False


def classify_type(name, decl_kind, header_values, imports_swiftui, imports_uikit):
    """Classify a single declaration from its OWN header evidence.

    Returns ``(candidate_type, framework, confidence, is_ui, is_extension, is_bridge,
    unknown_template)``. A declaration with no UI conformance / UIKit subclass / bridge
    symbol is ``unknown`` even when the file imports SwiftUI/UIKit -- a model struct in
    a UI file stays ``unknown`` and is never turned into a page.
    """
    is_view = imports_swiftui and _has_conformance(header_values, 'View')
    subclass_uikit = any(_has_conformance(header_values, base) for base in UIKIT_BASE)
    is_bridge = any(symbol in header_values for symbol in BRIDGE_SYMBOLS)

    if decl_kind == 'extension':
        return ('extension', 'unknown', 'low', False, True, False, False)
    if is_bridge:
        framework = 'uikit' if (imports_uikit or subclass_uikit) else ('swiftui' if imports_swiftui else 'unknown')
        return ('bridge', framework, 'low', True, False, True, False)
    if subclass_uikit:
        return ('page', 'uikit', 'low', True, False, False, False)
    if is_view:
        screenish = bool(re.search(r'(Screen|Page|ViewController|Root|Main|Home|Detail|Scene|Flow)$', name))
        if screenish:
            return ('page', 'swiftui', 'low', True, False, False, False)
        return ('component', 'swiftui', 'low', True, False, False, False)
    return ('unknown', 'unknown', 'none', False, False, False, True)


def discover_candidates(source, index, *, swift_syntax=None, conditional=None):
    """Discover candidate types from the reviewed source index, deterministically."""
    known = {f['path']: f for f in index.get('files', [])}
    if swift_syntax is None:
        from .swift_native import parse_sources
        inputs = {path: safe_child(source, path).read_bytes().decode('utf-8')
                  for path in known if Path(path).suffix == '.swift' and safe_child(source, path).is_file()}
        if inputs:
            swift_syntax = parse_sources(inputs)
    candidates = []
    for path, meta in known.items():
        if Path(path).suffix.lower() not in CODE:
            continue
        if conditional is not None:
            selected = set(conditional['members']) | set(conditional.get('analysis_files', []))
            if path not in selected:
                continue
            if path in {item['path'] for item in conditional.get('unknowns', [])}:
                raise MigrationError('Candidate source has unresolved compiler context: ' + path)
            views = conditional['observed'].get(path, [])
            active = {line for view in views for line in view['active_lines']} if views else None
        else:
            active = None
        file = safe_child(source, path)
        if not file.is_file():
            continue
        text = file.read_text(encoding='utf-8-sig')
        if Path(path).suffix == '.swift':
            from .swift_native import source_tokens
            source_tokens(source, path, swift_syntax)  # Reject missing/error/stale coordinates.
            view = swift_syntax[path]
            if view.get('selected_for_build') is False:
                continue
            if 'active_lines' in view:
                configured = set(view['active_lines'])
                active = configured if active is None else active & configured
            nodes = [node for node in view['nodes'] if active is None or node['line'] in active]
            imports = {n['value'].get('module') for n in nodes if n['kind'] == 'import'}
            imports_swiftui, imports_uikit = 'SwiftUI' in imports, 'UIKit' in imports
            declarations = []
            for node in nodes:
                value = node['value']
                if node['kind'] not in {'type', 'extension'} or value.get('top_level') is not True:
                    continue
                kind = value.get('kind', 'extension')
                name = value.get('name', value.get('type'))
                header = [kind, name]
                for index, inherited in enumerate(value.get('inherits', [])):
                    header.extend([':' if index == 0 else ',', inherited])
                declarations.append((name, kind, node['line'], header))
        else:
            tokens = tokenize(text, language='c', skip_pragma_marks=True)
            if active is not None:
                tokens = [token for token in tokens if token.line in active]
            imports = {tokens[i+1].value for i, token in enumerate(tokens[:-1])
                       if token.value == 'import' and tokens[i+1].kind != 'string'}
            imports_swiftui, imports_uikit = 'SwiftUI' in imports, 'UIKit' in imports
            declarations = _top_level_c_types(tokens)
        if Path(path).suffix in {'.m', '.mm', '.h'}:
            for i, token in enumerate(tokens[:-4]):
                if token.value == '@' and tokens[i+1].value == 'interface' and tokens[i+3].value == ':':
                    declarations.append((tokens[i+2].value, 'class', token.line,
                                         ['class', tokens[i+2].value, ':', tokens[i+4].value]))
        for name, decl_kind, line, header in declarations:
            (ctype, framework, confidence, is_ui, is_ext, is_bridge, unknown) = classify_type(
                name, decl_kind, header, imports_swiftui, imports_uikit)
            candidates.append({
                'name': name, 'decl_kind': decl_kind,
                'anchor': {'path': path, 'line': line, 'sha256': meta['sha256']},
                'candidate_type': ctype, 'framework': framework, 'confidence': confidence,
                'is_ui': is_ui, 'is_extension': is_ext, 'is_bridge': is_bridge, 'unknown_template': unknown,
            })
    # Stable ordering: same source -> same IDs. Source change detection is separate.
    candidates.sort(key=lambda c: (c['anchor']['path'], c['anchor']['line'], c['name']))
    return candidates

