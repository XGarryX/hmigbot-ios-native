"""Migration inputs and repository audit are different identities.

This is a conservative file relevance filter, not compiler membership. Unknown
files remain inputs. A support file referenced by a retained source/build input
is promoted (including resource directories and transitive build scripts).
"""
from pathlib import Path
import re

from .core import digest, json_bytes, snapshot

SUPPORT_NAMES = {'.gitignore', '.gitattributes', '.gitmodules', '.editorconfig',
                 '.mailmap', 'license', 'copying', 'authors', 'contributors',
                 'codeowners', 'changelog', 'readme', 'contributing', 'code_of_conduct',
                 'agents.md', 'source-manifest.json', 'source-origin.json',
                 'source-preservation-check.json'}
SUPPORT_FOLDERS = {'.github', '.gitlab', 'docs', 'documentation'}
SUPPORT_SUFFIXES = {'.md', '.rst', '.adoc', '.py', '.sh', '.bash', '.zsh', '.example'}
REFERENCE_SUFFIXES = {'.swift', '.m', '.mm', '.h', '.c', '.cpp', '.cc', '.cxx', '.hpp',
                      '.pbxproj', '.xcconfig', '.xcscheme', '.xctestplan', '.xcworkspacedata',
                      '.yml', '.yaml', '.py', '.sh', '.bash', '.zsh', '.rb'}


def support_candidate(relative):
    path = Path(relative)
    return (path.name.lower() in SUPPORT_NAMES or path.stem.lower() in SUPPORT_NAMES
            or path.suffix.lower() in SUPPORT_SUFFIXES
            or any(part.lower() in SUPPORT_FOLDERS for part in path.parts[:-1]))


def classify(source, entries=None):
    """Return file roles with a replayable reason, without guessing product scope.

    All unknown files are retained. References only promote, never exclude;
    they do not establish that a target actually compiles a file. Both exact
    names and directory references count, avoiding a suffix-only allowlist.
    """
    source = Path(source)
    entries = snapshot(source)['files'] if entries is None else entries
    candidates = {item['path'] for item in entries if support_candidate(item['path'])}
    retained = {item['path'] for item in entries} - candidates
    reasons = {path: 'source/resource/build input or unclassified file' for path in retained}
    by_spelling = {}
    for path in candidates:
        item = Path(path)
        spellings = {path, item.name}
        spellings.update(p.as_posix() for p in item.parents if p.as_posix() != '.')
        if item.suffix.lower() in {'.md', '.rst', '.adoc'}:
            spellings.add(item.stem)
        for spelling in spellings:
            by_spelling.setdefault(spelling, set()).add(path)
    pending = sorted(retained)
    while pending and candidates:
        parent = pending.pop()
        origin = Path(parent)
        if origin.suffix.lower() not in REFERENCE_SUFFIXES and origin.name not in {'Podfile', 'Makefile'}:
            # An audit JSON listing every repository path is not a build edge.
            # Unknown resources remain fingerprinted, but cannot manufacture
            # product duties merely by mentioning a support filename.
            continue
        if not (source / parent).is_file():
            continue  # A referenced but missing input stays relevant and fails its owning check.
        raw = (source / parent).read_bytes()
        # Binary resources cannot carry portable textual build references.
        if b'\x00' in raw[:4096]:
            continue
        try:
            text = raw.decode('utf-8-sig')
        except UnicodeError:
            continue
        # Tokens in code, PBX, XML, YAML and shell syntax. Matching is only a
        # conservative promotion; unresolved macros keep their unknown inputs.
        tokens = set(re.findall(r'[\w.\-/]+', text))
        tokens |= {Path(token).name for token in tokens}
        promoted = set().union(*(by_spelling[token] for token in tokens & by_spelling.keys())) & candidates
        for path in sorted(promoted):
            candidates.remove(path)
            retained.add(path)
            pending.append(path)
            reasons[path] = 'referenced by retained input: ' + parent
    return {item['path']: {'role': 'migration_input' if item['path'] in retained else 'repository_support',
                           'reason': reasons.get(item['path'], 'unreferenced repository/support material')}
            for item in entries}


def inventory_roles(source, paths):
    """Include stale inventory paths, so deleting an unrelated note cannot block.

    Missing build-referenced material is still promoted and must be repaired.
    Paths are validated before using authored inventory text as file addresses.
    """
    from .core import safe_child
    entries = snapshot(source)['files']
    known = {item['path'] for item in entries}
    for path in paths:
        safe_child(source, path)
        if path not in known:
            entries.append({'path': path})
            known.add(path)
    return classify(source, entries)


def migration_snapshot(source):
    full = snapshot(source)
    roles = classify(source, full['files'])
    files = [item for item in full['files'] if roles[item['path']]['role'] == 'migration_input']
    return {**full, 'files': files, 'sha256': digest(json_bytes(files))}


def audit(source):
    full = snapshot(source)
    roles = classify(source, full['files'])
    migration = [item for item in full['files'] if roles[item['path']]['role'] == 'migration_input']
    return {'schema_version': 1, 'policy': 'migration-relevance/1',
            'repository_sha256': full['sha256'], 'source_sha256': digest(json_bytes(migration)),
            'files': [{**item, **roles[item['path']]} for item in full['files']]}
