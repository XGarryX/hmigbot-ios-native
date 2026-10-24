# OPTIMIZED_FOR_MACOS_XCODE_NATIVE: retains Python orchestration only; compiler/build facts come from Xcode CLI.
"""Small independently callable source operations with common provenance."""
import xml.etree.ElementTree as ET
from pathlib import Path

from . import __version__
from .core import SCHEMA, MigrationError, digest, json_bytes, read_json, snapshot, write_new_tree
from .xcode import project_inventory, dependency_inventory
from .resources import asset_inventory, localization_inventory, convert_assets, convert_localization
from .providers import swift_syntax, normalize_build_settings, xcodebuild_settings, clang_ast

OPERATIONS = {
    'project-inventory': ['A02', 'A03', 'A06'],
    'dependency-inventory': ['A04'],
    'swift-syntax': ['A05', 'B01', 'B02', 'B04', 'B06', 'B07'],
    'clang-ast': ['A05', 'B01', 'B02', 'B12'],
    'interface-builder': ['B04', 'B05', 'B07', 'B08'],
    'asset-inventory': ['B13'],
    'localization-inventory': ['B14'],
    'asset-convert': ['D06', 'E09'],
    'localization-convert': ['D06', 'E09'],
    'build-settings': ['A02'],
}


def interface_builder(root, files):
    documents, issues = [], []
    for file in files:
        if Path(file['path']).suffix not in {'.xib', '.storyboard'}:
            continue
        try:
            raw = (root / file['path']).read_bytes()
            if b'<!DOCTYPE' in raw.upper() or b'<!ENTITY' in raw.upper():
                raise MigrationError('DTD/entities are not supported')
            tree = ET.fromstring(raw)
            nodes, edges, identifiers = [], [], set()
            def visit(element, owner=None):
                node_id = element.get('id')
                if node_id:
                    if node_id in identifiers:
                        raise MigrationError('Duplicate Interface Builder object ID')
                    identifiers.add(node_id)
                    nodes.append({'id': node_id, 'tag': element.tag, 'attributes': dict(element.attrib), 'parent': owner})
                if element.tag in {'outlet', 'action', 'segue', 'constraint'}:
                    edges.append({'kind': element.tag, 'owner': owner, **element.attrib})
                for child in element:
                    visit(child, node_id or owner)
            visit(tree)
            for edge in edges:
                for field in ('destination', 'firstItem', 'secondItem'):
                    if edge.get(field) and edge[field] not in identifiers:
                        issues.append({'code': 'unresolved_ib_reference', 'path': file['path'], 'id': edge[field]})
            documents.append({'path': file['path'], 'sha256': file['sha256'], 'initial_view_controller': tree.get('initialViewController'),
                              'nodes': nodes, 'connections': edges, 'layout_solution': 'not_computed'})
        except (MigrationError, ET.ParseError) as exc:
            issues.append({'code': 'ib_parse_failed', 'path': file['path'], 'message': str(exc)})
    return {'documents': documents}, issues


def run_atom(operation, root, output, *, provider_config=None, input_path=None, default_locale=None):
    if operation not in OPERATIONS:
        raise MigrationError('Unknown atomic operation')
    root, output = root.resolve(), output.resolve()
    if output.is_relative_to(root) or root.is_relative_to(output):
        raise MigrationError('Atom output must not overlap its source')
    before = snapshot(root)
    files = before['files']
    payload, extra = {}, {}
    if operation == 'project-inventory':
        value, issues = project_inventory(root, files)
    elif operation == 'dependency-inventory':
        value, issues = dependency_inventory(root, files)
    elif operation == 'swift-syntax':
        if not provider_config:
            raise MigrationError('swift-syntax requires --provider-config with explicit executable argument arrays')
        value, issues = swift_syntax(root, files, provider_config)
    elif operation == 'clang-ast':
        if not provider_config:
            raise MigrationError('clang-ast requires an explicit provider configuration')
        value, issues, payload = clang_ast(root, files, provider_config)
    elif operation == 'interface-builder':
        value, issues = interface_builder(root, files)
    elif operation.startswith('asset-'):
        value, issues = asset_inventory(root, files)
        if operation == 'asset-convert':
            value, gaps, payload = convert_assets(root, value)
            issues.extend(gaps)
    elif operation.startswith('localization-'):
        value, issues = localization_inventory(root, files)
        if operation == 'localization-convert':
            if not default_locale:
                raise MigrationError('localization-convert requires --default-locale')
            value, gaps, payload = convert_localization(value, default_locale)
            issues.extend(gaps)
    elif operation == 'build-settings':
        if provider_config:
            value = xcodebuild_settings(root, read_json(provider_config))
            issues = []
            extra = {'input_mode': 'direct_xcodebuild'}
        else:
            if not input_path:
                raise MigrationError('build-settings requires --provider-config for direct Xcode or --input for frozen evidence')

            from .evidence import validate
            evidence = validate(root, input_path)
            if evidence['kind'] != 'source_build':
                raise MigrationError('Build settings require source_build evidence')
            manifest = read_json(input_path / 'manifest.json')
            if 'artifacts/build-settings.json' not in manifest['artifacts']:
                raise MigrationError('Bundle must contain hashed artifacts/build-settings.json')
            value = normalize_build_settings(read_json(input_path / 'artifacts/build-settings.json'))
            issues = []
            extra = {'input_manifest_sha256': digest((input_path / 'manifest.json').read_bytes()), 'input_mode': 'frozen_evidence'}
    if snapshot(root)['sha256'] != before['sha256']:
        raise MigrationError('Source changed during atomic operation; retry with a stable snapshot')
    report = {'schema_version': SCHEMA, 'tool_version': __version__, 'operation': operation,
              'atom_ids': OPERATIONS[operation], 'source_sha256': before['sha256'], 'source_snapshot': before,
              'status': 'partial' if issues else 'operation_completed', 'data': value, 'issues': issues,
              'outputs': {name: digest(data) for name, data in payload.items()},
              'application_migration': 'not_verified', **extra}
    payload['artifact.json'] = json_bytes(report)
    write_new_tree(output, payload)
    return report
