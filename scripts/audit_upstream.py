"""Verify the complete imported HMigBot payload and record transparent derivative edits."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
from manage_install import filesystem_path
from hmigbot_ios.payload_layout import exclusion, release_profile

ROOT = filesystem_path(Path(__file__).resolve().parents[1])


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def safe_relative(relative):
    path = PurePosixPath(relative)
    if (path.is_absolute() or '..' in path.parts or '\\' in relative or ':' in relative or
            not path.parts or path.as_posix() != relative):
        raise ValueError('Unsafe upstream manifest path')
    return path


def release_selection(relative):
    safe_relative(relative)
    return exclusion('vendor/hmigbot/' + relative)


def macho_library_modes(directory):
    """Dylibs/bundles are loadable data, never candidate Python interpreters."""
    checked, errors = 0, []
    for path in directory.rglob('*'):
        if not path.is_file() or '/scripts/bin/macos-' not in path.as_posix():
            continue
        if release_selection(path.relative_to(directory).as_posix()):
            continue
        with path.open('rb') as stream:
            header = stream.read(16)
        endian = {b'\xcf\xfa\xed\xfe': 'little', b'\xce\xfa\xed\xfe': 'little',
                  b'\xfe\xed\xfa\xcf': 'big', b'\xfe\xed\xfa\xce': 'big'}.get(header[:4])
        if endian and len(header) == 16 and int.from_bytes(header[12:16], endian) in {6, 8}:
            checked += 1
            if path.stat().st_mode & 0o111:
                errors.append(path.relative_to(directory).as_posix())
    return checked, errors


def audit():
    baseline = json.loads((ROOT / 'docs/upstream/import-manifest.json').read_text(encoding='utf-8'))
    selection_path=ROOT/'docs/upstream/stage-import-manifest.json'
    selection=json.loads(selection_path.read_text(encoding='utf-8')) if selection_path.exists() else {'files':[]}
    selected={entry['path']:entry for entry in selection['files']}
    if len(selected)!=len(selection['files']):
        raise ValueError('Duplicate stage-import manifest path')
    changed, missing, binaries_changed, excluded = [], [], [], []
    replacements=[]
    for entry in baseline['files']:
        reason = release_selection(entry['path'])
        if reason:
            excluded.append({'path': entry['path'], 'reason': reason})
            continue
        path = ROOT / 'vendor/hmigbot' / entry['path']
        if not path.is_file():
            missing.append(entry['path'])
            continue
        current = digest(path)
        if current != entry['sha256']:
            changed.append({'path': entry['path'], 'upstream_sha256': entry['sha256'], 'current_sha256': current})
            if '/scripts/bin/' in entry['path'] or path.suffix in {'.exe', '.dll', '.bin', '.so', '.dylib'}:
                approved=selected.get(entry['path'],{})
                if (approved.get('predecessor_sha256')==entry['sha256'] and
                        approved.get('sha256')==current==approved.get('source_sha256') and
                        approved.get('authority')=='garry'):
                    replacements.append(entry['path'])
                else:
                    binaries_changed.append(entry['path'])
    selection_errors=[]
    stage_excluded = []
    for relative,entry in selected.items():
        reason = release_selection(relative)
        if reason:
            stage_excluded.append({'path': relative, 'reason': reason})
            continue
        path=ROOT/'vendor/hmigbot'/relative
        if (not path.is_file() or digest(path)!=entry['sha256'] or
                ('mode' in entry and path.stat().st_mode & 0o777 != entry['mode'])):
            selection_errors.append(relative)
    library_count, library_mode_errors = macho_library_modes(ROOT / 'vendor/hmigbot')
    return {'upstream_version': baseline['version'], 'imported_files': len(baseline['files']),
            'release_profile': release_profile(),
            'source_manifest_sha256': digest(ROOT / 'docs/upstream/import-manifest.json'),
            'release_files': len(baseline['files']) - len(excluded),
            'excluded_source_files': excluded, 'excluded_stage_import_files': stage_excluded,
            'unchanged_files': len(baseline['files']) - len(excluded) - len(changed) - len(missing),
            'changes': changed, 'missing': missing, 'binaries_changed': binaries_changed,
            'reviewed_binary_replacements':replacements,'stage_import_errors':selection_errors,
            'macho_libraries_checked':library_count,'macho_library_mode_errors':library_mode_errors,
            'stage_import_manifest_sha256':digest(selection_path) if selection_path.exists() else None,
            'status': 'passed' if not missing and not binaries_changed and not selection_errors and not library_mode_errors else 'failed',
            'scope': 'Unmodified full source manifest retained as provenance; every selected release file is checked, and intentional exclusions are disclosed. This is runtime integrity, not application acceptance.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true', help='Refresh reviewed derivative manifest after edits')
    args = parser.parse_args()
    result = audit()
    path = ROOT / 'docs/upstream/derivative-manifest.json'
    if args.write:
        path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    else:
        expected = json.loads(path.read_text(encoding='utf-8')) if path.exists() else None
        # The original reviewed derivative manifest may cover more platforms
        # and developer tests than this release. Never require those files to
        # be installed; still bind every selected derivative to reviewed bytes.
        reviewed = [entry for entry in (expected or {}).get('changes', [])
                    if not release_selection(entry['path'])]
        result['manifest_matches'] = expected is not None and reviewed == result['changes']
        if not result['manifest_matches']:
            result['status'] = 'failed'
    print(json.dumps({key: value for key, value in result.items() if key != 'changes'}, ensure_ascii=False, indent=2))
    return 0 if result['status'] == 'passed' else 1


if __name__ == '__main__':
    raise SystemExit(main())
