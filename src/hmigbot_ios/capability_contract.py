"""Optional plan-time capability references; no runtime or lifecycle proof."""
from __future__ import annotations

import re
from pathlib import PurePosixPath

from .artifact_contract import _json
from .core import MigrationError, safe_child

FIELDS = {'key', 'kind', 'symbol', 'path', 'slot', 'lifecycle', 'provider', 'provenance'}
KINDS = {'runtime-slot', 'scoped', 'artifact-only'}


def _blocks(text):
    # Same fence boundary rules as artifact_contract.json_blocks. Its public
    # iterator only yields action fences, so keep this optional kind separate.
    fence, body = None, []
    for number, line in enumerate(text.splitlines(), 1):
        if fence:
            if re.match(r'^ {0,3}' + re.escape(fence['char']) + '{' + str(fence['size']) + r',}\s*$', line):
                if fence['kind'] == 'capability-declarations':
                    yield '\n'.join(body)
                fence, body = None, []
            else:
                body.append(line)
            continue
        opening = re.match(r'^ {0,3}(`{3,}|~{3,})(.*?)\s*$', line)
        if opening:
            fence = {'char': opening[1][0], 'size': len(opening[1]),
                     'kind': opening[2], 'line': number}
    if fence and fence['kind'] == 'capability-declarations':
        raise MigrationError('capability-declaration-invalid: unclosed fence at line ' + str(fence['line']))


def _relative(project, value):
    if value != value.strip() or any(char in value for char in '*?['):
        raise MigrationError('capability-declaration-invalid: expected exact relative POSIX path: ' + value)
    safe_child(project, value)
    return value


def load_contract(project, plans, units, required=False):
    """Strict versioned declaration data bound to the shared plan authority."""
    blocks = [block for path in plans for block in _blocks(path.read_text(encoding='utf-8-sig'))]
    if not blocks:
        if required:
            raise MigrationError('capability-declarations-missing')
        return None
    if len(blocks) != 1:
        raise MigrationError('capability-declaration-ambiguous: expected exactly one fence across validated plans')
    try:
        value = _json(blocks[0])
    except MigrationError as exc:
        raise MigrationError("capability-declaration-invalid: " + str(exc)) from exc
    modern = isinstance(value, dict) and 'capability_schema' in value
    top = {'capability_schema', 'declarations', 'initialization', 'seams', 'absence'} if modern else {'declarations', 'seams'}
    if not isinstance(value, dict) or set(value) != top:
        raise MigrationError('capability-declaration-invalid: unknown or missing top-level fields')
    if value['seams'] != 'none':
        raise MigrationError('capability-declaration-invalid: only seams="none" is supported')
    if modern and value['absence'] != 'none':
        raise MigrationError('capability-absence-unsupported: only none is supported')
    if modern and (type(value['capability_schema']) is not int or value['capability_schema'] != 2):
        raise MigrationError('capability-declaration-invalid: capability_schema must be 2')
    if modern:
        init = value['initialization']
        if not isinstance(init, dict) or set(init) != {'hosts', 'chains', 'injections'} or any(not isinstance(v, list) for v in init.values()):
            raise MigrationError('capability-init-invalid: expected hosts/chains/injections arrays')
        if not init['hosts'] or not init['chains']:
            raise MigrationError('capability-init-invalid: hosts and chains must be nonempty')
        from .capability_runtime import validate_initialization
        validate_initialization(init)
        owned={path for item in units.values() if item['scope']=='product' for path in item['ownership']}
        for role in ('hosts','chains'):
            for rule in init[role]:
                _relative(project,rule['path'])
                if rule['path'] not in owned:
                    raise MigrationError('capability-init-host-not-owned: '+rule['path'])
    declarations = value['declarations']
    if not isinstance(declarations, list) or not declarations:
        raise MigrationError('capability-declaration-invalid: declarations must be a nonempty array')
    files = {item['path'] for item in units.values()}
    seen, identities = set(), set()
    for entry in declarations:
        expected = FIELDS | {'materialization'} if modern else FIELDS
        if not isinstance(entry, dict) or set(entry) != expected:
            raise MigrationError('capability-declaration-invalid: unknown or missing declaration fields')
        string_fields = expected - {'lifecycle'} if modern else expected
        if any(not isinstance(entry[key], str) for key in string_fields):
            raise MigrationError('capability-declaration-invalid: declaration fields must be strings')
        allowed_kinds = KINDS | {'framework-created'} if modern else KINDS
        if entry['kind'] not in allowed_kinds or any(not entry[key].strip() for key in string_fields - {'slot'}):
            raise MigrationError('capability-declaration-invalid: unknown kind or empty field')
        if modern:
            life = entry['lifecycle']
            if not isinstance(life, list) or any(not isinstance(v, str) or not v.strip() for v in life) or len(set(life)) != len(life):
                raise MigrationError('capability-declaration-invalid: lifecycle must list unique method names')
            if entry['materialization'] not in {'pending', 'materialized'}:
                raise MigrationError('capability-declaration-invalid: unknown materialization')
        if entry['kind'] == 'runtime-slot' and not entry['slot'].strip() or modern and entry['kind'] != 'runtime-slot' and entry['slot']:
            raise MigrationError('capability-declaration-invalid: only runtime-slot uses a nonempty slot')
        if entry['key'] in seen:
            raise MigrationError('capability-declaration-invalid: duplicate key: ' + entry['key'])
        seen.add(entry['key'])
        output = _relative(project, entry['path'])
        if entry['provider'].count('#') != 1:
            raise MigrationError('capability-provider-unknown: expected file#full-item_id')
        source, ident = entry['provider'].split('#'); _relative(project, source)
        if '/' not in source:
            matches = [path for path in files if PurePosixPath(path).name == source]
            if len(matches) > 1:
                raise MigrationError('capability-provider-ambiguous: ' + source)
            source = matches[0] if matches else source
        unit = units.get(ident)
        if unit is None or unit['path'] != source or unit['scope'] != 'product':
            raise MigrationError('capability-provider-unknown: ' + entry['provider'])
        if output not in unit['ownership']:
            raise MigrationError('capability-provider-owner-mismatch: ' + entry['key'])
        identity = (output, entry['symbol'])
        if modern and identity in identities:
            raise MigrationError('capability-declaration-invalid: duplicate path+symbol')
        identities.add(identity)
    return value


def validate_declarations(project, plans, units):
    value = load_contract(project, plans, units)
    if value is None:
        return None
    return {'status': 'static_references_validated', 'declarations': len(value['declarations']),
            'capability_schema': value.get('capability_schema', 1), 'runtime_verified': False}
