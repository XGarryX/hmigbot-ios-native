"""Ownership evidence for observed system presentations, not runtime success."""
from __future__ import annotations

import hashlib
from pathlib import Path
import re

from hmigbot_ios.core import read_json


def _unknown(reason):
    return {'classification': 'unknown', 'evidence': [], 'reason': reason}


def _anchor(value):
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        match = re.fullmatch(r'([^\n]+\.swift):([1-9][0-9]*)(?:\s.*)?', value)
        if match:
            return {'file': match[1], 'line': int(match[2])}
    return {}


def share_presentation(index, parent, discovery, manifest):
    """A caller's system flag is only a clue; current Source must prove it.

    This version supports directly anchored SwiftUI.ShareLink in its declaring
    parent. UIKit present chains and unresolved imports remain existing debt.
    """
    if discovery.get('external_system_ui') is not True:
        return None
    anchor = _anchor(discovery.get('source_anchor'))
    name, line = anchor.get('file'), anchor.get('line')
    if not isinstance(name, str) or type(line) is not int or line < 1:
        return _unknown('System presentation claim needs a current selected Source anchor')
    source = index.source
    path = (source.root / name).resolve()
    if not path.is_relative_to(source.root):
        return _unknown('System presentation anchor escapes the selected Source')
    name = path.relative_to(source.root).as_posix()
    file = index.swift_files.get(name)
    if file is None:
        return _unknown('System presentation anchor is not selected Swift Source')
    current_sha = hashlib.sha256(path.read_bytes()).hexdigest()
    if anchor.get('sha256') is not None and anchor['sha256'] != current_sha:
        return _unknown('System presentation anchor file fingerprint is stale')
    if parent.get('ios_file') != name:
        return _unknown('System presentation is not directly anchored in its parent Source file')
    owner = parent.get('fq_class') or parent.get('id')
    text = discovery.get('trigger_text')
    if not isinstance(owner, str) or not isinstance(text, str) or not text:
        return _unknown('System presentation has no parent type or observed trigger text')
    candidates = []
    for call in index.live_calls.get(name, []):
        callee = call['value'].get('callee', '')
        if callee not in {'ShareLink', 'SwiftUI.ShareLink'}:
            continue
        declared_owner = file.owner(call)
        if owner != declared_owner and not re.fullmatch(r'\w+\.' + re.escape(declared_owner), owner):
            continue
        literals = [t.literal_value for t in file.toks(call) if t.kind == 'string'
                    and getattr(t, 'literal_is_static', False)]
        if text not in literals:
            continue
        candidates.append(call)
    if not candidates:
        # A false flag on an ordinary app control must not suppress its variant.
        return None
    anchored = [c for c in candidates if c['line'] <= line <= file.text[:c['end']].count('\n') + 1]
    choices = anchored or candidates  # Old line numbers are hints, never authority.
    if len(choices) != 1:
        return _unknown('System presentation Source call cannot be uniquely relocated')
    call = choices[0]
    imports = {n['value'].get('module', '') for n in file.nodes if n['kind'] == 'import'}
    for other in index.live_calls.get(name, []):
        if (other is not call and call['start'] <= other['start'] and other['end'] <= call['end']
                and other['value'].get('callee_name') in {'Button', 'NavigationLink', 'Link', 'Menu', 'ShareLink'}):
            return _unknown('Nested interactive content makes the system trigger ambiguous')
    meta_path = manifest.get('native_run_meta') if isinstance(manifest, dict) else None
    if not isinstance(meta_path, str) or not Path(meta_path).is_file():
        return _unknown('System presentation needs its real parent collection context')
    index.guard.add(Path(meta_path))
    if hashlib.sha256(Path(meta_path).read_bytes()).hexdigest() != manifest.get('native_run_meta_sha256'):
        return _unknown('System presentation parent collection fingerprint changed')
    meta = read_json(Path(meta_path))
    if meta.get('node') != parent['id'] or meta.get('source_sha256') != index.facts['source_sha']:
        return _unknown('System presentation parent observation belongs to different Source')
    from .native_semantics import resolved_call
    from hmigbot_ios.core import MigrationError
    import subprocess
    try:
        binding = resolved_call(index, file, call)
    except (MigrationError, OSError, ValueError, KeyError, subprocess.TimeoutExpired) as exc:
        return _unknown('Current real Source semantic binding unresolved: ' + str(exc))
    if not re.match(r'^SwiftUI(?:Core)?\.\(file\)\.ShareLink(?: extension)?\.init\(', binding['declaration']):
        return _unknown('Current real Source call does not resolve to Apple SwiftUI.ShareLink')
    return {'classification': 'static', 'destination_ownership': 'system',
            'runtime_verified': False,
            'evidence': [{'kind': 'current SwiftParser system presentation API',
                'api': 'SwiftUI.ShareLink', 'file': name, 'sha256': current_sha,
                'line': call['line'], 'start': call['start'], 'end': call['end'],
                'parent': parent['id'], 'owner': file.owner(call),
                'anchor_relocated': not bool(anchored), 'imports': sorted(imports),
                'parent_collection': str(meta_path),
                'parent_collection_sha256': manifest['native_run_meta_sha256']}, binding],
            'note': 'Static trigger and system-owned presentation; behavior remains unmodified, no app baseline or sharing-success verdict'}
