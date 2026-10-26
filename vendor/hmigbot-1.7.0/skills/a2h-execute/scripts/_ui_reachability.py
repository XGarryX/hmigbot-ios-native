"""Static UI declaration reachability, with no product or report writes."""
import re
from pathlib import Path

TOKENS = re.compile(r"/\*.*?\*/|//[^\n]*|'(?:[^'\\]|\\.)*'|\"(?:[^\"\\]|\\.)*\"|`(?:[^`\\]|\\.)*`", re.S)
IMPORT = re.compile(r"\bimport\s+(type\s+)?([^;]*?)\s+from\s*['\"]([^'\"]+)['\"]\s*;?")
REEXPORT = re.compile(r"\bexport\s*\{([^}]+)\}\s*from\s*['\"]([^'\"]+)['\"]")
DECL = re.compile(r"\b(class|struct|function)\s+([A-Za-z_]\w*)")


def mask(text, strings=True):
    return TOKENS.sub(lambda m: ''.join('\n' if c == '\n' else ' ' for c in m[0])
                     if strings or m[0].startswith(('//', '/*')) else m[0], text)


def balanced(code, start, opening='{', closing='}'):
    depth = 0
    for index in range(start, len(code)):
        if code[index] == opening:
            depth += 1
        elif code[index] == closing:
            depth -= 1
            if depth == 0:
                return index + 1
    return len(code)


def declarations(text):
    code = mask(text)
    depth, depths = 0, []
    for char in code:
        depths.append(depth)
        depth += (char == '{') - (char == '}')
    result = {}
    for match in DECL.finditer(code):
        if depths[match.start()] != 0:
            continue
        start = match.end()
        if match[1] == 'function':
            paren = code.find('(', start)
            if paren < 0:
                continue
            start = balanced(code, paren, '(', ')')
        brace = code.find('{', start)
        if brace < 0:
            continue
        result[match[2]] = text[match.start():balanced(code, brace)]
        if re.search(r'export\s+default\s*$', code[max(0, match.start()-40):match.start()]):
            result['default'] = result[match[2]]
    return result


def bindings(declaration):
    """Import/export pairs (local name, provider name); ignore type-only names."""
    brace = re.search(r'\{([^}]+)\}', declaration)
    pairs = []
    if brace:
        for entry in brace[1].split(','):
            entry = entry.strip()
            if not entry or entry.startswith('type '):
                continue
            parts = re.split(r'\s+as\s+', entry)
            pairs.append((parts[-1].strip(), parts[0].strip()))
    star = re.search(r'\*\s+as\s+(\w+)', declaration)
    if star:
        pairs.append((star[1], '*'))
    default = declaration.split('{')[0].split(',')[0].strip()
    if re.fullmatch(r'[A-Za-z_]\w*', default):
        pairs.append((default, 'default'))
    return pairs


def used(code, name):
    return bool(re.search(r'\b' + re.escape(name) +
        r'\s*(?:\(|\.|<[^;{}]*>\s*\()', code) or
        re.search(r'\b(?:wrapBuilder\s*\(|extends\s+)' + re.escape(name) + r'\b', code))


def transparent_forward(body):
    """Only an empty onReady adapter removing its own captured path is delegation.

    Ordinary outgoing navigation never contributes the destination's UI depth.
    """
    text = mask(body, strings=False)
    if not re.search(r'NavDestination\(\)\s*\{\s*Stack\(\)\.[^{}]*\}', text):
        return None
    ready = re.search(r'\.onReady\s*\(', text)
    if not ready:
        return None
    callback = text[ready.end():balanced(mask(text), ready.end()-1, '(', ')')]
    call = re.search(r'\bthis\.(\w+)\s*\(', callback)
    if not call:
        return None
    method = re.search(r'\b' + re.escape(call[1]) + r'\s*\([^;{}]*\)\s*(?::\s*void)?\s*\{', text)
    if not method:
        return None
    core = text[method.start():balanced(mask(text), method.end()-1)]
    own = re.search(r'const\s+(\w+)\s*:\s*number\[\]\s*=\s*([\w.]+)\.getIndexByName\(\s*\w+\.pathInfo\.name\s*\)', core)
    if not own:
        return None
    index = re.search(r'const\s+(\w+)\s*:\s*number\s*=[^;]*\b' + re.escape(own[1]) + r'\[', core)
    if not index or not re.search(re.escape(own[2]) + r'\.removeByIndexes\(\s*\[\s*' + re.escape(index[1]) + r'\s*\]\s*\)', core):
        return None
    pushes = re.findall(re.escape(own[2]) + r"\.pushPathByName\(\s*['\"]([A-Za-z_]\w*)['\"]", core)
    return pushes[0] if len(pushes) == 1 else None


def ui_sources(page, ets_root):
    """Follow only used local declarations; exclude unrelated exports and dead files.

    UI struct/class bodies include event builders as potential page states.
    Runtime classes may carry native ComponentContent builders through callbacks.
    Cycles and repeated component declarations count once per page.
    """
    root = Path(ets_root).resolve()
    queue = [(Path(page).resolve(), None)]
    seen, counted, selected, files = set(), set(), [], set()
    cache = {}
    while queue:
        path, symbol = queue.pop(0)
        if (path, symbol) in seen or path.is_symlink() or not path.is_file() or not path.is_relative_to(root):
            continue
        seen.add((path, symbol))
        if path not in cache:
            text = path.read_text(encoding='utf-8', errors='ignore')
            cache[path] = (text, declarations(text))
        text, decls = cache[path]
        if symbol is None:
            if path.stem in decls:
                symbol = path.stem
            elif path.stem + 'Builder' in decls:
                symbol = path.stem + 'Builder'
            else:
                structs = [m[2] for m in DECL.finditer(mask(text)) if m[1] == 'struct' and m[2] in decls]
                if structs:
                    queue.append((path, structs[0]))
                    continue
        body = decls.get(symbol) if symbol else text
        if body is None:
            # Barrel export: follow the named symbol, never all sibling exports.
            for match in REEXPORT.finditer(mask(text, strings=False)):
                for local, provider in bindings('{' + match[1] + '}'):
                    if local == symbol:
                        target = (path.parent / match[2]).resolve()
                        queue.append((target if target.suffix == '.ets' else target.with_suffix('.ets'), provider))
            continue
        if (path, body) in counted:
            continue
        counted.add((path, body))
        clean = mask(IMPORT.sub('', body))
        selected.append((path, symbol, clean))
        files.add(path)
        forwarded = transparent_forward(body)
        if forwarded:
            queue.append((root / 'pages' / (forwarded + '.ets'), forwarded))
        for name in decls if symbol is not None else []:
            if name != symbol and name != 'default' and used(clean, name):
                queue.append((path, name))
        for match in IMPORT.finditer(mask(text, strings=False)):
            if match[1] or not match[3].startswith('.'):
                continue
            target = (path.parent / match[3]).resolve()
            targets = [target] if target.suffix == '.ets' else [target.with_suffix('.ets'), target / 'Index.ets', target / 'index.ets']
            for local, provider in bindings(match[2]):
                if provider == '*':
                    providers = re.findall(r'\b' + re.escape(local) + r'\.(\w+)\s*(?:\(|\.)', clean)
                else:
                    providers = [provider] if used(clean, local) else []
                for candidate in targets:
                    for name in providers:
                        queue.append((candidate, name))
    return selected, files
