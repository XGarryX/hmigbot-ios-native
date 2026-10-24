"""Package and compare the source directory without rebuilding its layout."""
import hashlib
import json
from pathlib import Path, PurePosixPath
import stat
import zipfile

EXCLUDED_DIRS = {'.git', '__pycache__', '.pytest_cache', '.venv', 'node_modules',
                 '.build', '.swiftpm', 'build', 'dist', 'work', '.hmigbot-ios',
                 '.migbot', '.agents', '.codex'}


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def excluded(path):
    if path.is_dir() and path.name in EXCLUDED_DIRS:
        return 'local state/build/cache directory'
    if path.name == '.DS_Store' or path.name.startswith('._') or path.suffix in {'.pyc', '.pyo'}:
        return 'system/cache file'
    return None


def inventory(root):
    root = Path(root).resolve()
    files, directories, exclusions = [], [], []

    def visit(directory):
        for path in sorted(directory.iterdir()):
            relative = path.relative_to(root).as_posix()
            reason = excluded(path)
            if reason:
                exclusions.append({'path': relative, 'reason': reason})
                continue
            if path.is_symlink():
                raise ValueError('Source link cannot be packaged: ' + relative)
            info = zipfile.ZipInfo.from_file(path, strict_timestamps=False)
            # ZIP timestamps have two-second resolution.
            stamp = list(info.date_time)
            stamp[-1] &= ~1
            record = {'path': relative, 'mode': oct(stat.S_IMODE(path.stat().st_mode)),
                      'zip_date_time': stamp}
            if path.is_dir():
                directories.append(record)
                visit(path)
            elif path.is_file():
                files.append({**record, 'size': path.stat().st_size, 'sha256': sha(path)})
            else:
                raise ValueError('Unsupported source file: ' + relative)

    visit(root)
    root_info = zipfile.ZipInfo.from_file(root, strict_timestamps=False)
    stamp = list(root_info.date_time)
    stamp[-1] &= ~1
    root_record = {'mode': oct(stat.S_IMODE(root.stat().st_mode)), 'zip_date_time': stamp}
    return {'source_root_name': root.name, 'root_metadata': root_record, 'files': files, 'directories': directories,
            'excluded': exclusions}


def sidecars(package):
    return package.with_suffix(package.suffix + '.sha256'), package.with_suffix(package.suffix + '.manifest.json')


def build_package(root, output):
    root, output = Path(root).resolve(), Path(output).resolve()
    if output.is_relative_to(root):
        raise ValueError('Package output must be outside the source directory')
    sums, manifest_path = sidecars(output)
    if any(path.exists() for path in (output, sums, manifest_path)):
        raise ValueError('Output or sidecar already exists')
    before = inventory(root)
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, 'x', compression=zipfile.ZIP_DEFLATED) as archive:
        # from_file retains source modes and modification times, including dirs.
        archive.write(root, root.name + '/')
        for record in before['directories']:
            archive.write(root / record['path'], root.name + '/' + record['path'] + '/')
        for record in before['files']:
            archive.write(root / record['path'], root.name + '/' + record['path'])
    after = inventory(root)
    if any(before[key] != after[key] for key in ('root_metadata', 'files', 'directories')):
        raise ValueError('Source changed during packaging; archive has no completion sidecars')
    checksum = sha(output)
    manifest = {'schema_version': 1, **before, 'archive_sha256': checksum,
                'scope': 'Source files, directories, modes and ZIP-resolution mtimes. Local state/cache exclusions are listed. Filesystem ownership and extended attributes are outside ZIP scope.'}
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    sums.write_text(checksum + '  ' + output.name + '\n', encoding='utf-8')
    report = verify_package(output, root)
    if report['status'] != 'passed':
        raise ValueError('Source/archive verification failed: ' + json.dumps(report['differences']))
    return report


def verify_package(package, source=None):
    package = Path(package).resolve()
    sums, manifest_path = sidecars(package)
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    prefix = manifest['source_root_name']
    if not prefix or PurePosixPath(prefix).name != prefix or '\\' in prefix or ':' in prefix or prefix in {'.', '..'}:
        raise ValueError('Invalid source root in package manifest')
    differences = []
    checksum = sha(package)
    if checksum != manifest['archive_sha256'] or checksum != sums.read_text(encoding='utf-8').split()[0]:
        differences.append({'rule': 'archive-checksum'})
    expected = {record['path']: {**record, 'kind': 'file'} for record in manifest['files']}
    for record in manifest['directories']:
        if record['path'] in expected:
            raise ValueError('Duplicate manifest path')
        expected[record['path']] = {**record, 'kind': 'directory'}
    if len(expected) != len(manifest['files']) + len(manifest['directories']):
        raise ValueError('Duplicate manifest path')
    observed, seen, roots = {}, set(), []
    with zipfile.ZipFile(package) as archive:
        for info in archive.infolist():
            path = PurePosixPath(info.filename)
            if path.is_absolute() or '..' in path.parts or '\\' in info.filename or ':' in info.filename or path.parts[0] != prefix:
                raise ValueError('Unsafe or unexpected archive path')
            if info.filename in seen or stat.S_ISLNK(info.external_attr >> 16):
                raise ValueError('Archive contains a duplicate or link')
            seen.add(info.filename)
            if info.filename == prefix + '/' and info.is_dir():
                roots.append(info)
                continue
            relative = path.relative_to(prefix).as_posix()
            if relative in observed:
                raise ValueError('Conflicting file/directory archive path')
            item = {'path': relative, 'kind': 'directory' if info.is_dir() else 'file',
                    'mode': oct(stat.S_IMODE(info.external_attr >> 16)), 'zip_date_time': list(info.date_time)}
            if not info.is_dir():
                with archive.open(info) as stream:
                    item.update(size=info.file_size, sha256=hashlib.file_digest(stream, 'sha256').hexdigest())
            observed[relative] = item
    if len(roots) != 1:
        differences.append({'rule': 'archive-root'})
    elif {'mode': oct(stat.S_IMODE(roots[0].external_attr >> 16)), 'zip_date_time': list(roots[0].date_time)} != manifest['root_metadata']:
        differences.append({'rule': 'archive-root-metadata'})
    for path in sorted(expected.keys() | observed.keys()):
        if expected.get(path) != observed.get(path):
            differences.append({'rule': 'archive-manifest-mismatch', 'path': path})
    if source is not None:
        current = inventory(source)
        if current['source_root_name'] != prefix:
            differences.append({'rule': 'source-root-name'})
        if current['root_metadata'] != manifest['root_metadata']:
            differences.append({'rule': 'source-root-metadata'})
        for kind in ('files', 'directories'):
            old = {record['path']: record for record in manifest[kind]}
            new = {record['path']: record for record in current[kind]}
            for path in sorted(old.keys() | new.keys()):
                if old.get(path) != new.get(path):
                    differences.append({'rule': 'source-mismatch', 'path': path})
    return {'status': 'failed' if differences else 'passed', 'archive_sha256': checksum,
            'source_root_name': prefix, 'files': len(manifest['files']),
            'directories': len(manifest['directories']), 'excluded': manifest['excluded'],
            'source_compared': source is not None, 'differences': differences}
