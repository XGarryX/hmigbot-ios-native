"""Pin consumed contract logic, without making comments or optional CLI modules gates."""
import ast
from pathlib import Path

from .core import digest


def rule_digest(path):
    path = Path(path)
    raw = path.read_bytes()
    if path.suffix != '.py':
        return digest(raw)
    tree = ast.parse(raw)
    for node in ast.walk(tree):
        body = getattr(node, 'body', None)
        if isinstance(body, list) and body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant) and isinstance(body[0].value.value, str):
            del body[0]
    return digest(ast.dump(tree, include_attributes=False).encode())


def consumed_modules(root, paths):
    """Follow local imports of contract readers, excluding optional CLI routers.

    The caller's explicit resource list remains authoritative for schemas,
    templates and native payloads. This never imports or executes project code.
    """
    root = Path(root)
    pending = [Path(p) for p in paths if Path(p).suffix == '.py']
    seen = set()
    while pending:
        path = pending.pop()
        if path in seen or not path.is_file():
            continue
        seen.add(path)
        tree = ast.parse(path.read_bytes())
        def imports(node):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == 'main':
                return
            if isinstance(node, ast.ImportFrom) and node.level == 1 and node.module:
                candidate = root / 'src/hmigbot_ios' / (node.module.replace('.', '/') + '.py')
                if candidate.is_file():
                    pending.append(candidate)
            for child in ast.iter_child_nodes(node):
                imports(child)
        imports(tree)
    return seen
