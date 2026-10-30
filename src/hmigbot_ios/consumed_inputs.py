"""Freeze formal contracts and the evidence they actually reference.

This controls tool inputs, not iOS semantics. Native source/build interpretation
remains owned by the compiler providers and their replay validators.
"""
from pathlib import Path
import json
import re

from .core import MigrationError, digest, json_bytes, read_json, safe_child

SOURCE_RECORDS = {'ios-source-index.json', 'ios-facts.json', 'ios-obligations.json'}
PRODUCT_RECORDS = SOURCE_RECORDS | {'ios-semantics.json', 'ios-coverage.json',
    'ios-source-disposition.json', 'literal-ledger.json', 'ios-responsibility.json'}


def baseline_inputs(project, wave):
    from .artifact_contract import catalog, contract_version, _artifact_paths, json_blocks
    from .spec_contract import COMMON, references
    project = Path(project).resolve()
    inputs, documents, values, capture_ids = {}, [], [], set()

    def record(path):
        path = Path(path).resolve()
        if not path.is_relative_to(project) or path == project:
            raise MigrationError('Consumed evidence escapes project: ' + str(path))
        relative = path.relative_to(project).as_posix()
        safe_child(project, relative)
        if not path.is_file():
            raise MigrationError('Consumed input is missing: ' + relative)
        inputs[relative] = digest(path.read_bytes())
        return path

    def bundle(value):
        path = Path(value)
        path = path.resolve() if path.is_absolute() else safe_child(project, value)
        path = path / 'manifest.json' if path.is_dir() else path
        record(path)
        data = read_json(path)
        for name, expected in data.get('artifacts', {}).items():
            item = record(safe_child(path.parent, name))
            if digest(item.read_bytes()) != expected:
                raise MigrationError('Consumed evidence was modified: ' + item.relative_to(project).as_posix())
        return data

    def provider(ref):
        path = record(safe_child(project, ref['path']))
        if ref.get('sha256') != inputs[path.relative_to(project).as_posix()]:
            raise MigrationError('Consumed provider evidence was modified: ' + ref['path'])
        data = read_json(path)
        for name, expected in data.get('outputs', {}).items():
            item = record(safe_child(path.parent, name))
            if digest(item.read_bytes()) != expected:
                raise MigrationError('Consumed provider output was modified: ' + name)
        run = path.parent / 'run.json'
        if run.is_file():
            record(run)
            for failure in read_json(run).get('prior_failures', []):
                item = record(safe_child(path.parent.parent, failure['path']))
                if digest(item.read_bytes()) != failure['sha256']:
                    raise MigrationError('Consumed provider failure evidence changed')

    base = project / 'spec/baseline'
    names = SOURCE_RECORDS if wave == 'understand' else PRODUCT_RECORDS
    for name in sorted(names):
        path = base / name
        if path.is_file():
            record(path)
            values.append(read_json(path))
    graph_path = base / 'ios-facts.json'
    if graph_path.is_file():
        graph = read_json(graph_path)
        for ref in graph.get('provider_artifacts', []):
            provider(ref)
        if graph.get('manifest_evidence'):
            bundle(graph['manifest_evidence']['path'])
        for key in ('evidence_path', 'compilation_evidence_path'):
            if graph.get('variant', {}).get(key):
                bundle(graph['variant'][key])
        if graph.get('conditional_evidence'):
            # The service owns Clang/Swift/mixed component and actual compiler
            # dependencies. Do not replace this with an entire run-directory scan.
            from .conditional_evidence import frozen_inputs
            inputs.update(frozen_inputs(project, graph))

    if wave == 'domains':
        from .source_ui_capture import frozen_inputs as ui_inputs
        inputs.update(ui_inputs(project))
        documents.extend(base / name for name in COMMON if (base / name).is_file())
        for folder, pattern in (('features', 'F*.md'), ('ui', 'page_*.md')):
            documents.extend(sorted((base / folder).glob(pattern)))
        decision = project / 'spec/decision-ledger.md'
        if decision.is_file():
            documents.append(decision)
        if contract_version(project) == 2:
            for entry in catalog()['spec']:
                for path in _artifact_paths(project, entry):
                    if not path.is_file():
                        continue
                    if path.suffix == '.md':
                        documents.append(path)
                    else:
                        record(path); values.append(read_json(path))
            pages = {re.match(r'page_\d+', p.name)[0] for p in (base / 'ui').glob('page_*.md')
                     if re.match(r'page_\d+', p.name)}
            for ident in pages:
                meta = base / 'ui-snapshots' / ident / 'meta.json'
                if meta.is_file():
                    record(meta); values.append(read_json(meta))

    # Follow only formal contract links. A scratch Markdown/JSON file is not a
    # semantic dependency just because it sits beside the reviewed contracts.
    pending, seen = list(documents), set()
    while pending:
        path = pending.pop().resolve()
        if path in seen:
            continue
        seen.add(path); record(path)
        text = path.read_text(encoding='utf-8-sig')
        pending.extend(target for target, _, _ in references(project, path, text))
        for block in json_blocks(text):
            try:
                values.append(json.loads(block['body']))
            except (ValueError, UnicodeError):
                pass  # The formal authoring validator owns malformed typed content.

    def inspect(value):
        if isinstance(value, dict):
            if isinstance(value.get('tool_evidence_ids'), list):
                capture_ids.update(v for v in value['tool_evidence_ids'] if isinstance(v, str))
            if isinstance(value.get('contract_ref'), str):
                text = 'contract_refs: ' + json.dumps([value['contract_ref']])
                for target, _, _ in references(project, project, text):
                    collect_reference(target)
            for child in value.values():
                inspect(child)
        elif isinstance(value, list):
            for child in value:
                inspect(child)

    def collect_reference(path):
        path = path.resolve()
        if path in seen:
            return
        seen.add(path); record(path)
        text = path.read_text(encoding='utf-8-sig')
        for target, _, _ in references(project, path, text):
            collect_reference(target)
        for block in json_blocks(text):
            try:
                inspect(json.loads(block['body']))
            except (ValueError, UnicodeError):
                pass

    for value in values:
        inspect(value)
    if capture_ids:
        index = read_json(project / 'spec/ref/ios-mcp-index.json')
        captures = {}
        for item in index.get('captures', []):
            if isinstance(item, dict) and item.get('id') in capture_ids:
                selected = {key: item.get(key) for key in ('id', 'path', 'sha256', 'transcript_sha256')}
                if item['id'] in captures and captures[item['id']] != selected:
                    raise MigrationError('Conflicting consumed MCP evidence ID: ' + item['id'])
                captures[item['id']] = selected
        for ident in sorted(capture_ids):
            if ident not in captures:
                raise MigrationError('Unknown consumed MCP evidence ID: ' + ident)
            entry = captures[ident]
            # Pin the selected index record, not unrelated historical entries.
            inputs['@mcp-capture/' + ident] = digest(json_bytes(entry))
            path = record(safe_child(project, entry['path']))
            if digest(path.read_bytes()) != entry['sha256']:
                raise MigrationError('Consumed MCP evidence changed: ' + ident)
            transcript = record(path.parent / 'transcript.json')
            if digest(transcript.read_bytes()) != entry['transcript_sha256']:
                raise MigrationError('Consumed MCP transcript changed: ' + ident)
    return inputs
