"""Task-owned resource deltas and one recoverable indexed-stage merge.

Only this adapter's submit/merge protocol is coordinated by the project lock.
It does not authorize arbitrary writers or replace compilation/acceptance.
"""
from __future__ import annotations

import argparse
import base64
from contextlib import contextmanager
import hashlib
import json
import math
import os
from pathlib import Path, PurePosixPath
import re
import stat
import sys
import uuid

from .core import MigrationError, digest, json_bytes, source_snapshot

ROOT = 'spec/execution/resource-deltas'
CONTRACT = 'spec/execution/execution-contract.json'
KINDS = {'string', 'color', 'float', 'boolean', 'integer', 'strarray', 'intarray', 'plural'}
MAX_BYTES = 16 * 1024 * 1024


def _require(value, message):
    if not value:
        raise MigrationError(message)


def _object(value, fields, label, required=None):
    _require(isinstance(value, dict) and not set(value) - set(fields), label + ': unsupported object fields')
    _require(set(fields if required is None else required) <= set(value), label + ': required fields missing')
    return value


def _identifier(value, label, *, portable=False):
    _require(isinstance(value, str) and 0 < len(value) <= 256 and
             not any(ord(c) < 32 for c in value), label + ': invalid identity')
    if portable:
        _require(bool(re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,100}', value)), label + ': use a portable scope identifier')
    return value


def _project(value):
    path = Path(value).expanduser().absolute()
    for part in (path, *path.parents):
        _require(not part.is_symlink(), 'Project path cannot traverse symbolic links')
    _require(path.is_dir(), 'Project directory does not exist')
    return path


def _path(project, relative):
    _require(isinstance(relative, str) and relative and '\\' not in relative and ':' not in relative,
             'Unsafe project-relative path')
    parts = PurePosixPath(relative)
    _require(not parts.is_absolute() and '..' not in parts.parts and parts.as_posix() == relative,
             'Noncanonical or escaping project-relative path: ' + relative)
    _require(all(p not in {'.', ''} and not p.endswith((' ', '.')) for p in parts.parts), 'Unsafe path component')
    path = project
    for component in parts.parts:
        if path.is_dir():
            aliases = [p.name for p in path.iterdir() if p.name.casefold() == component.casefold()]
            _require(not aliases or aliases == [component], 'Case-colliding resource protocol path: ' + relative)
        path = path/component
        _require(not path.is_symlink(), 'Path traverses a symbolic link: ' + relative)
    return path


def _raw(project, relative, *, missing=False):
    path = _path(project, relative)
    if not path.exists() and missing:
        return None
    flags = os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0) | getattr(os, 'O_NONBLOCK', 0)
    try:
        fd = os.open(path, flags)
        with os.fdopen(fd, 'rb') as stream:
            info = os.fstat(stream.fileno())
            _require(stat.S_ISREG(info.st_mode) and info.st_size <= MAX_BYTES, 'Expected bounded ordinary file: ' + relative)
            result = stream.read(MAX_BYTES + 1)
            _require(len(result) <= MAX_BYTES, 'File exceeds resource protocol limit: ' + relative)
            after = path.lstat()
            _require((info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns) ==
                     (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns), 'File changed while reading: ' + relative)
            return result
    except OSError as exc:
        raise MigrationError('Cannot read resource protocol file: ' + relative + ': ' + str(exc)) from exc


def _json(raw, label):
    _require(isinstance(raw, bytes) and len(raw) <= MAX_BYTES, label + ': JSON exceeds protocol limit')
    def pairs(items):
        result = {}
        for key, value in items:
            _require(key not in result, label + ': duplicate JSON key ' + key)
            result[key] = value
        return result
    def constant(value):
        raise MigrationError(label + ': non-finite JSON number ' + value)
    def finite(value):
        number = float(value)
        _require(math.isfinite(number), label + ': non-finite JSON number ' + value)
        return number
    try:
        return json.loads(raw.decode('utf-8-sig'), object_pairs_hook=pairs,
                          parse_constant=constant, parse_float=finite)
    except (UnicodeError, ValueError) as exc:
        raise MigrationError(label + ': invalid JSON: ' + str(exc)) from exc


def _read(project, relative):
    return _json(_raw(project, relative), relative)


def _mkdir(project, relative):
    path = _path(project, relative)
    path.mkdir(parents=True, exist_ok=True)
    _path(project, relative)
    _require(path.is_dir(), 'Expected directory: ' + relative)
    return path


def _atomic(project, relative, raw):
    _require(len(raw) <= MAX_BYTES, 'Resource protocol output exceeds bounded file limit')
    path = _path(project, relative)
    _mkdir(project, PurePosixPath(relative).parent.as_posix())
    temporary = path.parent / ('.resource-delta-' + uuid.uuid4().hex)
    fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, 'O_NOFOLLOW', 0), 0o600)
    try:
        with os.fdopen(fd, 'wb') as stream:
            mode = stat.S_IMODE(path.stat().st_mode) if path.exists() else (
                0o644 if '/src/main/resources/' in relative else 0o600)
            os.fchmod(stream.fileno(),mode)
            stream.write(raw);stream.flush();os.fsync(stream.fileno())
        _path(project, relative)
        os.replace(temporary, path)
        parent_fd = os.open(path.parent, os.O_RDONLY | getattr(os, 'O_DIRECTORY', 0))
        try:
            os.fsync(parent_fd)
        finally:
            os.close(parent_fd)
    finally:
        temporary.unlink(missing_ok=True)


@contextmanager
def _lock(project, *, readonly=False):
    try:
        import fcntl
    except ImportError as exc:
        raise MigrationError('Resource merge locking is unavailable on this host') from exc
    if not readonly:
        _mkdir(project, ROOT)
    path = _path(project, ROOT + '/.lock')
    flags = os.O_RDONLY if readonly else os.O_RDWR | os.O_CREAT
    try:
        fd = os.open(path, flags | getattr(os, 'O_NOFOLLOW', 0), 0o600)
    except OSError as exc:
        raise MigrationError('Resource scope is not initialized or its lock is unavailable') from exc
    try:
        _require(stat.S_ISREG(os.fstat(fd).st_mode), 'Resource lock must be an ordinary file')
        fcntl.flock(fd, fcntl.LOCK_SH if readonly else fcntl.LOCK_EX)
        yield
    finally:
        os.close(fd)


def _scope(scope):
    return ROOT + '/' + _identifier(scope, 'scope', portable=True)


def _resource_path(path):
    _require(isinstance(path, str) and re.fullmatch(
        r'[A-Za-z0-9_-]+/src/main/resources/[A-Za-z0-9_-]+/element/[A-Za-z0-9_-]+\.json', path),
        'Resource destination must be a module/src/main/resources/<qualifier>/element/*.json path')
    return path


def _entries(value, kind, label):
    _require(isinstance(value, list), label + ': expected resource array')
    result = {}
    for item in value:
        _object(item, {'name', 'value', 'translatable'}, label, {'name', 'value'})
        name = item['name']
        _require(isinstance(name, str) and re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*', name), label + ': invalid resource name')
        _require(name not in result, label + ': duplicate resource name ' + name)
        if 'translatable' in item:
            _require(kind == 'string' and type(item['translatable']) is bool, label + ': invalid translatable flag')
        val = item['value']
        if kind in {'string', 'color'}:
            _require(isinstance(val, str), label + ': expected string value')
        elif kind == 'float':
            _require(isinstance(val, str) or type(val) in (int, float) and math.isfinite(val), label + ': invalid float value')
        elif kind == 'boolean':
            _require(type(val) is bool or val in ('true', 'false'), label + ': invalid boolean value')
        elif kind == 'integer':
            _require(type(val) is int or isinstance(val, str) and re.fullmatch(r'-?\d+', val), label + ': invalid integer value')
        elif kind in {'strarray', 'intarray'}:
            _require(isinstance(val, list) and all(isinstance(v, str) if kind == 'strarray' else type(v) is int for v in val), label + ': invalid array value')
        else:
            _require(isinstance(val, list), label + ': invalid plural value')
            quantities = set()
            for v in val:
                _object(v, {'quantity', 'value'}, label)
                _require(v['quantity'] in {'zero','one','two','few','many','other'} and
                         v['quantity'] not in quantities and isinstance(v['value'], str), label + ': invalid plural entry')
                quantities.add(v['quantity'])
        result[name] = item
    return result


def _context(project):
    from .plan_contract import contract_revision, structural_digest
    cfg_raw = _raw(project, '.migbot/config.json')
    cfg = _json(cfg_raw, 'config')
    _require(isinstance(cfg,dict) and cfg.get('source_platform') == 'ios' and isinstance(cfg.get('ios'), str), 'Configured iOS source is required')
    source = Path(cfg['ios'])
    source = source if source.is_absolute() else project / source
    _require(source.is_dir(), 'Configured source is unavailable')
    raw = _raw(project, CONTRACT);contract = _json(raw, CONTRACT)
    _require(isinstance(contract,dict) and type(contract.get('schema_version')) is int and
             contract.get('schema_version') == 1 and contract.get('execution_model') == 'indexed-stages-v1',
             'Current indexed execution contract is required')
    _require(contract.get('resource_protocol') == 'task-deltas-v1', 'Execution contract must enable task-deltas-v1; review and replan old contracts')
    _require(contract.get('source_sha256') == source_snapshot(source)['sha256'], 'Execution source changed; review and replan')
    _require(contract.get('contract_revision') == contract_revision(project), 'Execution tool rules changed; reviewed replan is required')
    _require(isinstance(contract.get('plan_items'), dict) and contract['plan_items'], 'Execution contract has no indexed plan items')
    inputs = contract.get('plan_inputs')
    _require(isinstance(inputs, dict) and inputs, 'Execution contract has no frozen plan inputs')
    for relative, expected in inputs.items():
        content = _raw(project, relative)
        actual = (structural_digest(content.decode('utf-8-sig'), artifact=relative)
                  if relative.endswith('.md') else digest(content))
        _require(actual == expected, 'Frozen plan input changed: ' + relative)
    return {'execution_contract_sha256': digest(raw), 'source_sha256': contract['source_sha256'],
            'config_sha256': digest(cfg_raw), 'contract_revision': contract['contract_revision'],
            'plan_inputs': inputs}, contract


def _manifest(value, contract):
    _object(value, {'schema_version','scope_id','closer_id','tasks','resources'}, 'resource scope')
    _require(type(value['schema_version']) is int and value['schema_version'] == 1, 'Unsupported resource scope schema')
    _identifier(value['scope_id'], 'scope_id', portable=True)
    _identifier(value['closer_id'], 'closer_id')
    _require(isinstance(value['tasks'], list) and value['tasks'], 'Expected tasks must be declared before dispatch')
    seen = set()
    for task in value['tasks']:
        _object(task, {'task_id','attempt','plan_item_ids'}, 'expected task')
        _identifier(task['task_id'], 'task_id')
        _require(task['task_id'] not in seen, 'Duplicate task identity')
        seen.add(task['task_id'])
        _require(type(task['attempt']) is int and task['attempt'] > 0, 'Task attempt must be positive')
        refs = task['plan_item_ids']
        _require(isinstance(refs, list) and refs and all(isinstance(r,str) for r in refs) and
                 len(refs) == len(set(refs)) and set(refs) <= contract['plan_items'].keys(),
                 'Task must map to actual current indexed plan items')
    _require(isinstance(value['resources'], list), 'Resource destinations must be an array; [] means no resource outputs')
    paths = set()
    for item in value['resources']:
        _object(item, {'path','type'}, 'resource destination')
        _resource_path(item['path'])
        _require(item['type'] in KINDS, 'Unsupported resource type')
        _require(item['path'].casefold() not in paths, 'Duplicate/case-colliding resource path')
        paths.add(item['path'].casefold())
    return value


def _snapshot(project, manifest):
    paths = {str(PurePosixPath(r['path']).parent) for r in manifest['resources']}
    result = {}
    for relative in sorted(paths):
        folder = _path(project, relative)
        if not folder.exists():
            continue
        _require(folder.is_dir(), 'Resource element path is not a directory')
        for path in sorted(folder.iterdir()):
            _require(not path.is_symlink(), 'Resource directory contains symbolic link: ' + str(path))
            if path.suffix == '.json':
                name = path.relative_to(project).as_posix()
                result[name] = digest(_raw(project, name))
    return result


def _state(project, scope):
    relative = _scope(scope) + '/scope.json'
    state = _read(project, relative)
    _object(state, {'schema_version','manifest','binding','resource_preimages'}, 'frozen resource scope')
    binding, contract = _context(project)
    _require(type(state['schema_version']) is int and state['schema_version'] == 1 and
             state['binding'] == binding, 'Resource scope inputs changed; do not refresh old evidence')
    _manifest(state['manifest'], contract)
    _require(state['manifest']['scope_id'] == scope, 'Resource scope identity mismatch')
    return state, digest(_raw(project, relative))


def initialize(project, manifest):
    project = _project(project)
    with _lock(project):
        _require(_raw(project, ROOT + '/pending.json', missing=True) is None, 'Pending resource transaction requires recover first')
        binding, contract = _context(project)
        manifest = _manifest(manifest, contract)
        relative = _scope(manifest['scope_id']) + '/scope.json'
        frozen = _raw(project, relative, missing=True)
        if frozen is not None:
            state, _ = _state(project, manifest['scope_id'])
            _require(state['manifest'] == manifest, 'Existing scope is immutable; use a new reviewed scope for changed tasks/attempts')
            if _raw(project,_scope(manifest['scope_id'])+'/merge-receipt.json',missing=True) is not None:
                _receipt(project,manifest['scope_id'],manifest['closer_id'])
            else:
                _require(_snapshot(project,manifest)==state['resource_preimages'],'Resource preimages changed before repeated initialization')
            return {'status':'initialized','scope':manifest['scope_id'],'existing':True,'scope_sha256':digest(frozen)}
        state = {'schema_version':1,'manifest':manifest,'binding':binding,
                 'resource_preimages':_snapshot(project, manifest)}
        # Validate all declared/current resource formats before admitting workers.
        _resource_index(project, state)
        raw = json_bytes(state);_atomic(project, relative, raw)
        return {'status':'initialized','scope':manifest['scope_id'],'existing':False,'scope_sha256':digest(raw)}


def _delta_path(scope, task_id):
    return _scope(scope) + '/tasks/' + digest(task_id.encode()) + '.json'


def _delta(payload, manifest):
    _object(payload, {'resources'}, 'task delta')
    _require(isinstance(payload['resources'], list), 'Task delta resources must be an array; [] means no additions')
    allowed = {r['path']: r['type'] for r in manifest['resources']}
    seen = set()
    for resource in payload['resources']:
        _object(resource, {'path','type','entries'}, 'task delta resource')
        path = resource['path']
        _require(isinstance(path, str) and path in allowed and allowed[path] == resource['type'] and path not in seen,
                 'Task delta destination missing, duplicated or outside frozen resource scope')
        seen.add(path);_entries(resource['entries'], resource['type'], path)
    return payload


def submit(project, scope, task_id, attempt, payload):
    project = _project(project)
    with _lock(project):
        _require(_raw(project, ROOT+'/pending.json', missing=True) is None, 'Recover pending resource merge before submitting more')
        state, identity = _state(project, scope);manifest = state['manifest']
        matching = [t for t in manifest['tasks'] if t['task_id'] == task_id and t['attempt'] == attempt]
        _require(len(matching) == 1, 'Task/attempt is not declared in this frozen scope')
        _delta(payload, manifest)
        value = {'schema_version':1,'scope_sha256':identity,'task':matching[0],'payload':payload}
        raw = json_bytes(value);relative = _delta_path(scope, task_id)
        prior = _raw(project, relative, missing=True)
        if prior is not None:
            _require(prior == raw, 'Task delta is immutable; changed output requires a new reviewed scope')
            if _raw(project,_scope(scope)+'/merge-receipt.json',missing=True) is not None:
                _receipt(project,scope,manifest['closer_id'])
            else:
                _require(_snapshot(project,manifest)==state['resource_preimages'],'Shared resources changed before merge')
        else:
            _require(_snapshot(project,manifest)==state['resource_preimages'],'Shared resources changed before merge')
            _atomic(project, relative, raw)
        return {'status':'submitted','scope':scope,'task_id':task_id,'attempt':attempt,
                'delta_path':relative,'delta_sha256':digest(raw),'existing':prior is not None}


def _resource_index(project, state):
    manifest = state['manifest'];resources = {r['path']:r['type'] for r in manifest['resources']}
    # Validate every destination even when it does not exist yet. Comparing
    # only the directory snapshot misses a case alias of an existing filename.
    for path in resources:
        _path(project, path)
    kinds = {str(PurePosixPath(p).parent):set() for p in resources}
    for p,kind in resources.items():kinds[str(PurePosixPath(p).parent)].add(kind)
    documents, index = {}, {}
    for path in sorted(state['resource_preimages']):
        raw = _raw(project,path)
        _require(digest(raw)==state['resource_preimages'][path],'Resource changed while preparing merge: '+path)
        value = _json(raw,path)
        _require(isinstance(value,dict), 'Resource file must contain an object: '+path)
        selected = set(value) & kinds[str(PurePosixPath(path).parent)]
        if not selected:
            continue
        _require(len(value) == 1 and len(selected) == 1, 'Resource file must contain one resource type: '+path)
        kind = next(iter(selected));rows = _entries(value[kind], kind, path)
        if path in resources:_require(resources[path] == kind, 'Declared resource type mismatch: '+path)
        documents[path] = value
        for name,item in rows.items():
            key = (str(PurePosixPath(path).parent), kind, name)
            _require(key not in index, 'Existing resource is defined in multiple files: '+kind+'.'+name)
            index[key] = {'path':path,'entry':item,'origins':[{'existing_file':path}]}
    for path,kind in resources.items():
        if path in state['resource_preimages']:
            _require(path in documents, 'Declared resource has wrong type: '+path)
        else:
            documents[path] = {kind:[]}
    return documents, index


def _plan(project, scope, closer):
    state, identity = _state(project, scope);manifest=state['manifest']
    _require(closer == manifest['closer_id'], 'Only the declared closer may merge this scope')
    _require(_snapshot(project, manifest) == state['resource_preimages'], 'Resource preimages changed; reject stale merge')
    documents, index = _resource_index(project, state)
    delta_hashes, conflicts = {}, []
    for task in sorted(manifest['tasks'], key=lambda t:t['task_id']):
        path = _delta_path(scope, task['task_id']);raw = _raw(project, path,missing=True)
        _require(raw is not None,'Expected task has not submitted its delta: '+task['task_id'])
        value = _json(raw, path)
        _object(value, {'schema_version','scope_sha256','task','payload'}, 'submitted task delta')
        _require(type(value['schema_version']) is int and value['schema_version'] == 1 and
                 value['scope_sha256'] == identity and value['task'] == task,
                 'Submitted delta task/scope/attempt mismatch: '+task['task_id'])
        _delta(value['payload'], manifest);delta_hashes[path] = digest(raw)
        for resource in value['payload']['resources']:
            target=resource['path'];kind=resource['type']
            for row in resource['entries']:
                key=(str(PurePosixPath(target).parent),kind,row['name'])
                origin={'task_id':task['task_id'],'attempt':task['attempt'],'declared_path':target}
                if key in index:
                    if json_bytes(index[key]['entry']) != json_bytes(row):
                        conflicts.append({'resource':kind+'.'+row['name'],'qualifier_path':key[0],
                                          'prior_sources':index[key]['origins'],'incoming_source':origin})
                    else:index[key]['origins'].append(origin)
                else:
                    documents[target][kind].append(row)
                    index[key]={'path':target,'entry':row,'origins':[origin]}
    _require(not conflicts, 'Conflicting resource values/metadata; no shared files changed: '+json.dumps(conflicts,ensure_ascii=False))
    writes=[];after=dict(state['resource_preimages'])
    for path in sorted(documents):
        if path not in {r['path'] for r in manifest['resources']}:continue
        before_raw=_raw(project,path,missing=True)
        _require((digest(before_raw) if before_raw is not None else None)==state['resource_preimages'].get(path),
                 'Resource changed while rendering merge: '+path)
        raw=json_bytes(documents[path])
        # Preserve original bytes for files with no additions.
        if before_raw is not None and _json(before_raw,path)==documents[path]:continue
        if before_raw is None and not any(documents[path].values()):continue
        writes.append({'path':path,'before_sha256':digest(before_raw) if before_raw is not None else None,
                       'after_sha256':digest(raw),'after_base64':base64.b64encode(raw).decode('ascii')})
        after[path]=digest(raw)
    return {'schema_version':1,'scope':scope,'closer_id':closer,'scope_sha256':identity,
            'binding':state['binding'],'delta_hashes':delta_hashes,'before':state['resource_preimages'],
            'after':after,'writes':writes,
            'provenance':[{'path':value['path'],'type':key[1],'name':key[2],'sources':value['origins']}
                          for key,value in sorted(index.items())]}


def _receipt(project, scope, closer):
    state, identity = _state(project, scope)
    _require(closer == state['manifest']['closer_id'], 'Closer identity mismatch')
    receipt = _read(project, _scope(scope)+'/merge-receipt.json')
    _object(receipt, {'schema_version','scope','closer_id','scope_sha256','binding','delta_hashes',
                      'before','after','provenance','status','written_files'}, 'resource merge receipt')
    _require(type(receipt['schema_version']) is int and receipt['schema_version'] == 1 and
             receipt.get('status') == 'merged' and receipt.get('scope') == scope and receipt.get('closer_id') == closer
             and receipt.get('scope_sha256') == identity and receipt.get('binding') == state['binding'], 'Invalid or stale merge receipt')
    _require(isinstance(receipt['delta_hashes'],dict) and
             set(receipt['delta_hashes']) == {_delta_path(scope,t['task_id']) for t in state['manifest']['tasks']},
             'Merge receipt omitted expected tasks')
    for path,expected in receipt['delta_hashes'].items():
        _require(digest(_raw(project,path)) == expected, 'Submitted delta changed after merge')
    _require(_snapshot(project,state['manifest']) == receipt['after'], 'Resources changed after merge; receipt is not current')
    return receipt


def verify_merged(project, scope, closer_id):
    """Read-only gate for the caller immediately before original writeback."""
    project=_project(project)
    with _lock(project,readonly=True):
        _require(_raw(project,ROOT+'/pending.json',missing=True) is None, 'Pending resource transaction requires recovery')
        return _receipt(project,scope,closer_id)


def check(project, scope, closer_id, *, require_merged=False):
    project=_project(project)
    with _lock(project,readonly=True):
        _require(_raw(project,ROOT+'/pending.json',missing=True) is None,'Pending resource transaction requires recovery')
        if _raw(project,_scope(scope)+'/merge-receipt.json',missing=True) is not None:
            return _receipt(project,scope,closer_id)
        _require(not require_merged,'Resource scope has not been merged')
        plan=_plan(project,scope,closer_id)
        return {'status':'ready','scope':scope,'writes':len(plan['writes']),'tasks':len(plan['delta_hashes']),
                'scope_sha256':plan['scope_sha256']}


def _finish(project, transaction):
    _object(transaction, {'schema_version','scope','closer_id','scope_sha256','binding','delta_hashes',
                          'before','after','writes','provenance'}, 'pending resource transaction')
    scope=transaction['scope'];state,identity=_state(project,scope)
    _require(type(transaction['schema_version']) is int and transaction['schema_version'] == 1 and
             transaction.get('scope_sha256') == identity and
             transaction.get('binding') == state['binding'] and transaction.get('closer_id') == state['manifest']['closer_id'],
             'Transaction no longer matches frozen scope')
    _require(transaction.get('before')==state['resource_preimages'],'Transaction preimages differ from frozen scope')
    _require(isinstance(transaction['delta_hashes'],dict) and
             set(transaction['delta_hashes'])=={_delta_path(scope,t['task_id']) for t in state['manifest']['tasks']},
             'Transaction omits expected delta')
    for path,expected in transaction['delta_hashes'].items():
        _require(digest(_raw(project,path))==expected,'Transaction delta changed; recovery refused')
    allowed={r['path'] for r in state['manifest']['resources']}
    _require(isinstance(transaction['writes'],list) and isinstance(transaction['after'],dict), 'Invalid transaction output shape')
    for row in transaction['writes']:
        _object(row, {'path','before_sha256','after_sha256','after_base64'}, 'pending resource write')
    writes={row['path']:row for row in transaction['writes']}
    _require(len(writes)==len(transaction['writes']) and set(writes)<=allowed,'Transaction resource writes are invalid')
    observed=_snapshot(project,state['manifest'])
    _require(set(transaction['after'])==set(transaction['before'])|set(writes),'Transaction result paths differ from its declared writes')
    _require(all(transaction['after'][path] == sha for path,sha in transaction['before'].items() if path not in writes),
             'Transaction altered a resource outside its write set')
    _require(set(observed)<=set(transaction['after']) and set(transaction['before'])<=set(observed), 'Resource file set changed during transaction')
    for path in set(transaction['before'])|set(transaction['after']):
        _require(observed.get(path) in {transaction['before'].get(path),transaction['after'].get(path)},
                 'Resource changed outside pending transaction: '+path)
    for path,row in writes.items():
        _require(row['before_sha256']==transaction['before'].get(path) and row['after_sha256']==transaction['after'].get(path),
                 'Transaction hashes do not match file set')
        raw=base64.b64decode(row['after_base64'],validate=True)
        _require(digest(raw)==row['after_sha256'],'Transaction content hash mismatch')
        declared=next(r['type'] for r in state['manifest']['resources'] if r['path']==path)
        value=_json(raw,path);_object(value,{declared},'pending resource');_entries(value[declared],declared,path)
    for path,row in writes.items():
        current_raw=_raw(project,path,missing=True)
        current=digest(current_raw) if current_raw is not None else None
        _require(current in {row['before_sha256'],row['after_sha256']},'Resource changed before replace: '+path)
        if current != row['after_sha256']:
            _atomic(project,path,base64.b64decode(row['after_base64'],validate=True))
    _require(_snapshot(project,state['manifest'])==transaction['after'],'Merged resource readback failed')
    receipt={k:v for k,v in transaction.items() if k!='writes'}
    receipt.update(status='merged',written_files=sorted(writes))
    _atomic(project,_scope(scope)+'/merge-receipt.json',json_bytes(receipt))
    _path(project,ROOT+'/pending.json').unlink()
    return receipt


def merge(project, scope, closer_id, *, recover=False):
    project=_project(project)
    with _lock(project):
        pending=_raw(project,ROOT+'/pending.json',missing=True)
        if pending is not None:
            _require(recover,'Pending resource merge; run recover with its declared scope/closer')
            transaction=_json(pending,'pending resource transaction')
            _require(transaction.get('scope')==scope and transaction.get('closer_id')==closer_id,'Pending transaction belongs to another scope/closer')
            return _finish(project,transaction)
        if _raw(project,_scope(scope)+'/merge-receipt.json',missing=True) is not None:
            return _receipt(project,scope,closer_id)
        _require(not recover,'No pending transaction to recover')
        transaction=_plan(project,scope,closer_id)
        # Intent is durable before the first shared file changes. An interrupted
        # multi-file commit blocks all new merges until explicit roll-forward.
        _atomic(project,ROOT+'/pending.json',json_bytes(transaction))
        return _finish(project,transaction)


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    commands=parser.add_subparsers(dest='action',required=True)
    init=commands.add_parser('init');init.add_argument('--project',type=Path,required=True);init.add_argument('--manifest',type=Path,required=True)
    sub=commands.add_parser('submit');sub.add_argument('--project',type=Path,required=True)
    sub.add_argument('--scope',required=True);sub.add_argument('--task',required=True);sub.add_argument('--attempt',type=int,required=True);sub.add_argument('--input',type=Path,required=True)
    for name in ['check','merge','recover']:
        command=commands.add_parser(name);command.add_argument('--project',type=Path,required=True)
        command.add_argument('--scope',required=True);command.add_argument('--closer',required=True)
        if name=='check':command.add_argument('--require-merged',action='store_true')
    args=parser.parse_args(argv)
    args.command = 'resource-delta-' + args.action
    progress_note = None
    try:
        # Reject an escaping/symlinked project before progress can write there.
        args.project = _project(args.project)
        if args.action != 'check':
            from .project_progress import ProjectProgress
            progress_note = ProjectProgress(args)
            progress_note.record('running')
        def payload(path,label):
            _require(not path.is_symlink() and path.is_file() and path.stat().st_size<=MAX_BYTES, label+': expected bounded ordinary file')
            return _json(path.read_bytes(),label)
        if args.action=='init':result=initialize(args.project,payload(args.manifest,'scope manifest'))
        elif args.action=='submit':result=submit(args.project,args.scope,args.task,args.attempt,payload(args.input,'task payload'))
        elif args.action=='check':result=check(args.project,args.scope,args.closer,require_merged=args.require_merged)
        else:result=merge(args.project,args.scope,args.closer,recover=args.action=='recover')
        if progress_note is not None:
            progress_note.record(result.get('status','returned'),result,exit_code=0)
        # Keep the terminal small; detailed provenance remains in the receipt.
        print(json.dumps({k:v for k,v in result.items() if k not in {'provenance','binding','before','after','delta_hashes'}},ensure_ascii=False,indent=2))
        return 0
    except (MigrationError,OSError,ValueError,KeyError,TypeError,AttributeError) as exc:
        error = {'status':'blocked','error':str(exc),'recovery':'Keep scope/deltas and original failure; repair the input or explicitly recover the pending transaction.'}
        if progress_note is not None:
            progress_note.record('blocked',error,exit_code=2)
        print(json.dumps(error,ensure_ascii=False))
        return 2


if __name__=='__main__':
    raise SystemExit(main())
