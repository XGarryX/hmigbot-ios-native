"""Read-only IPA inspection; presence of signing material is not signature validation."""
from pathlib import PurePosixPath
import plistlib
import struct
import zipfile

from .core import MigrationError, digest


def macho(data):
    if len(data) < 32 or data[:4] not in (b'\xcf\xfa\xed\xfe', b'\xfe\xed\xfa\xcf'):
        raise MigrationError('Expected a thin 64-bit device Mach-O executable')
    endian = '<' if data[:4] == b'\xcf\xfa\xed\xfe' else '>'
    cpu, _, _, ncmds, size, _, _ = struct.unpack(endian + '7I', data[4:32])
    if cpu != 0x0100000c:
        raise MigrationError('Expected arm64 device architecture')
    if ncmds > 10000 or size > len(data) - 32:
        raise MigrationError('Malformed Mach-O load commands')
    pos, platforms = 32, []
    for _ in range(ncmds):
        if pos + 8 > 32 + size:
            raise MigrationError('Truncated Mach-O load command')
        kind, length = struct.unpack(endian + '2I', data[pos:pos + 8])
        if length < 8 or pos + length > 32 + size:
            raise MigrationError('Invalid Mach-O load command length')
        if kind == 0x32 and length >= 24:
            platforms.append(struct.unpack(endian + 'I', data[pos + 8:pos + 12])[0])
        elif kind == 0x25:
            platforms.append(2)  # LC_VERSION_MIN_IPHONEOS, for older device toolchains.
        pos += length
    if not platforms or any(value != 2 for value in platforms):
        raise MigrationError('Mach-O is not an iPhoneOS device executable')
    return {'architecture': 'arm64', 'platform': 'iPhoneOS'}


def inspect_ipa(path):
    if not path.is_file():
        raise MigrationError('IPA file does not exist')
    try:
        with zipfile.ZipFile(path) as archive:
            names = set()
            if sum(i.file_size for i in archive.infolist()) > 2 * 1024**3:
                raise MigrationError('IPA exceeds the 2 GiB uncompressed inspection limit')
            for info in archive.infolist():
                name = info.filename
                parts = PurePosixPath(name).parts
                if name in names or name.startswith('/') or '\\' in name or ':' in name or '..' in parts:
                    raise MigrationError('Unsafe or duplicate IPA member')
                names.add(name)
            bad = archive.testzip()
            if bad:
                raise MigrationError('IPA CRC mismatch: ' + bad)
            roots = [n[:-len('/Info.plist')] for n in names if n.startswith('Payload/') and n.count('/') == 2 and n.endswith('.app/Info.plist')]
            if len(roots) != 1:
                raise MigrationError('IPA must contain exactly one top-level Payload/*.app')
            app = roots[0]
            bundles = [app] + sorted(n[:-len('/Info.plist')] for n in names if n.startswith(app + '/PlugIns/') and n.endswith('.appex/Info.plist'))
            results = []
            for bundle in bundles:
                info = plistlib.loads(archive.read(bundle + '/Info.plist'))
                if info.get('CFBundleSupportedPlatforms') != ['iPhoneOS']:
                    raise MigrationError('Bundle is not built for physical iPhoneOS')
                executable = info.get('CFBundleExecutable')
                if not isinstance(executable, str) or '/' in executable or '\\' in executable or executable in {'.', '..'}:
                    raise MigrationError('Invalid bundle executable')
                binary = macho(archive.read(bundle + '/' + executable))
                results.append({'path': bundle, 'bundle_id': info.get('CFBundleIdentifier'), 'minimum_os': info.get('MinimumOSVersion'),
                    **binary, 'provisioning_profile_present': bundle + '/embedded.mobileprovision' in names})
            return {'status': 'device_ipa_structure_valid', 'sha256': digest(path.read_bytes()), 'bytes': path.stat().st_size,
                'bundles': results, 'signature_validity': 'not_verified', 'installation': 'not_performed',
                'next': 'Use local Apple-account signing before installation; validate extension entitlements separately'}
    except (zipfile.BadZipFile, KeyError, plistlib.InvalidFileException, ValueError, struct.error) as exc:
        if isinstance(exc, MigrationError):
            raise
        raise MigrationError('Invalid IPA: ' + str(exc)) from exc
