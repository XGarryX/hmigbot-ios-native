"""Read the authoritative Git facts/SwiftSyntax evidence for downstream consumers.

This is a wire adapter for Garry's audited target-side checks. It never invokes a
second source parser, selects another build configuration, or rewrites baseline.
"""
from pathlib import Path
import re

from .core import source_snapshot
from .core import MigrationError, digest, read_json, safe_child, snapshot

CODE = {'.swift', '.m', '.mm', '.h', '.c', '.cpp'}


class Source:
    def __init__(self, root, project=None):
        from .native_pipeline import context
        from .ios_facts import validate_graph
        from .swift_native import project_syntax
        if project is None:
            raise MigrationError('Downstream source reads require the configured project root')
        self.root, self.project = Path(root).resolve(), Path(project).resolve()
        configured, _ = context(self.project)
        if configured != self.root:
            raise MigrationError('Downstream source differs from the configured Git source')
        self.graph, _ = validate_graph(self.root, self.project)
        snap = source_snapshot(self.root)
        self.fingerprint = snap['sha256']
        if self.fingerprint != self.graph['source_sha256']:
            raise MigrationError('Source changed between Git graph validation and downstream read')
        self.records = {f['path']: f for f in snap['files']}
        self.config = read_json(self.project / '.migbot/config.json')
        variant = self.graph['variant']
        self.selection = variant if variant.get('scope') == 'project-targets' else None
        allowed = set(variant.get('source_files', self.records))
        self.files = {p for p in allowed if p in self.records and Path(p).suffix in CODE
                      and Path(p).name != 'Package.swift'}
        self._syntax = project_syntax(self.project, self.root, self.graph)
        self._texts, self._tokens = {}, {}
        self.view = None
        self._active = {}
        if self.graph.get('conditional_evidence'):
            from .conditional_evidence import validate
            evidence = validate(self.root, Path(self.graph['conditional_evidence']['path']), project=self.project)
            self.files.update(name for name in evidence.get('analysis_files', [])
                              if name in self.records and Path(name).suffix in CODE)
            for name, views in evidence['observed'].items():
                groups = {tuple(v['active_lines']) for v in views}
                if len(groups) == 1:
                    self._active[name] = set(next(iter(groups)))
                else:
                    self._active[name] = None

    def text(self, name):
        if name not in self.files:
            raise MigrationError('Source outside the reviewed product scope: ' + name)
        raw = safe_child(self.root, name).read_bytes()
        if digest(raw) != self.records[name]['sha256']:
            raise MigrationError('Downstream source changed: ' + name)
        text = raw.decode('utf-8' if name.endswith('.swift') else 'utf-8-sig')
        if name in self._active:
            if self._active[name] is None:
                raise MigrationError('Multiple compiled source views require an explicit context: ' + name)
            text = ''.join(line if n in self._active[name] else
                           ''.join(c if c in '\r\n' else ' ' for c in line)
                           for n, line in enumerate(text.splitlines(keepends=True), 1))
        else:
            if name.endswith('.swift') and self._syntax is not None and name in self._syntax:
                has_condition = any(node['kind'] == 'conditional_compilation' for node in self._syntax[name]['nodes'])
            else:
                from .swiftui import tokenize
                directive_lines = {token.line for token in tokenize(text, skip_pragma_marks=not name.endswith('.swift'))
                                   if token.kind != 'string' and token.value == '#'}
                has_condition = any(number in directive_lines and re.match(r'^\s*#\s*(?:if|ifdef|ifndef)\b', line)
                                    for number, line in enumerate(text.splitlines(), 1))
            if has_condition:
                raise MigrationError('Active conditional source evidence is unresolved: ' + name)
        self._texts[name] = text
        return text

    def syntax(self, name):
        self.text(name)
        if not name.endswith('.swift'):
            return None
        if self._syntax is None or name not in self._syntax:
            raise MigrationError('Reviewed Git SwiftSyntax evidence is required: ' + name)
        return self._syntax[name]

    def tokens(self, name):
        text = self.text(name)
        if name.endswith('.swift'):
            from .swift_native import tokens_for
            original = safe_child(self.root, name).read_bytes().decode('utf-8')
            result = tokens_for(self.syntax(name), original)
            if name in self._active:
                result = [t for t in result if t.line in self._active[name]]
        else:
            from .swiftui import tokenize
            result = tokenize(text, skip_pragma_marks=True)
        return result

    def code(self, name, strings=False):
        text = self.text(name)
        result = [c if c in '\r\n' else ' ' for c in text]
        for token in self.tokens(name):
            if token.kind == 'regex' or token.kind == 'string' and not strings:
                continue
            result[token.start:token.end] = text[token.start:token.end]
        return ''.join(result)


def anchors(md, source):
    from .native_pipeline import source_paths
    return [p for p in source_paths(Path(md).read_text(encoding='utf-8-sig')) if p in source.files]


def declarations(source, name):
    if name.endswith('.swift'):
        return {n['value']['name'].strip('`') for n in source.syntax(name)['nodes']
                if n['kind'] in {'type', 'function'}}
    return set(re.findall(r'\b(?:interface|implementation|class|struct|enum|protocol)\s+(\w+)', source.code(name)))


def entrypoints(source):
    """Use the reviewed page anchors, preserving stable page identity from Git."""
    result = []
    for path in sorted((source.project / 'spec/baseline/ui').glob('page_*.md')):
        symbol=re.sub(r'^page_\d{4}_','',path.stem)
        for name in anchors(path, source):
            if symbol in declarations(source, name):
                result.append({'short':symbol, 'file':name, 'page_spec':path.name})
    return result


def module_inventory(source):
    return {'modules': sorted(set(source.selection['targets'])) if source.selection else [source.root.name]}
