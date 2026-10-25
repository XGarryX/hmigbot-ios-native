"""Lossless asset packaging and literal localization conversion with explicit gaps."""
from collections import defaultdict
import json
from pathlib import Path
import re
import struct

from .core import MigrationError, digest, json_bytes, read_json, safe_child
from .xcode import OpenStep


def resource_name(namespace, key):
    slug = re.sub('[^a-z0-9_]', '_', key.lower()).strip('_')[:40] or 'value'
    return 'ios_' + slug + '_' + digest((namespace + '\0' + key).encode('utf-8'))[:10]


def asset_inventory(root, files):
    assets, issues = [], []
    for item in files:
        path = root / item['path']
        if path.name != 'Contents.json' or not any(part.endswith('.xcassets') for part in path.parts):
            continue
        try:
            contents = read_json(path)
            if not isinstance(contents, dict):
                raise MigrationError('Asset Contents.json must be an object')
            assets.append({'name': path.parent.stem, 'type': path.parent.suffix[1:], 'path': item['path'],
                           'sha256': item['sha256'], 'contents': contents})
        except MigrationError as exc:
            issues.append({'code': 'asset_parse_failed', 'path': item['path'], 'message': str(exc)})
    return {'assets': assets}, issues


def convert_assets(root, inventory):
    payload, mappings, issues = {}, [], []
    for asset in inventory['assets']:
        if asset['type'] == 'xcassets':
            continue
        contents = asset['contents']
        if asset['type'] != 'imageset':
            issues.append({'code': 'asset_type_unmapped', 'path': asset['path'], 'type': asset['type']})
            continue
        images = contents.get('images', [])
        if not images or contents.get('properties'):
            issues.append({'code': 'asset_properties_need_mapping', 'path': asset['path']})
            continue
        present = [image for image in images if image.get('filename')]
        if any(set(i) - {'idiom', 'filename', 'scale'} or i.get('idiom') != 'universal' or
               i.get('scale') not in {'1x', '2x', '3x'} for i in present):
            issues.append({'code': 'asset_variant_unmapped', 'path': asset['path']})
            continue
        if not present or len({i['scale'] for i in present}) != len(present):
            issues.append({'code': 'asset_variants_missing_or_duplicate', 'path': asset['path']})
            continue
        try:
            variants = []
            logical_sizes = set()
            for image in present:
                source = safe_child((root / asset['path']).parent, image['filename'])
                data = source.read_bytes()
                # PNG metadata can be inspected without a decoder or pixel transformation.
                if source.suffix.lower() != '.png' or data[:8] != b'\x89PNG\r\n\x1a\n' or data[12:16] != b'IHDR' or len(data) < 33:
                    raise MigrationError('Only PNG image sets are covered by the lossless rule')
                width, height = struct.unpack('>II', data[16:24])
                scale = int(image['scale'][0])
                if not width or not height:
                    raise MigrationError('Invalid PNG dimensions')
                logical_sizes.add((width / scale, height / scale))
                variants.append((scale, source, data, width, height))
            if len(logical_sizes) != 1:
                raise MigrationError('Image scales disagree on logical dimensions')
            scale, source, data, width, height = max(variants, key=lambda x: x[0])
            name = resource_name(asset['path'], asset['name'])
            target = f'entry/src/main/resources/base/media/{name}.png'
            payload[target] = data
            mappings.append({'source_name': asset['name'], 'source_catalog': asset['path'], 'source_file': source.relative_to(root).as_posix(),
                             'source_sha256': digest(data), 'target': target, 'resource': f'app.media.{name}',
                             'logical_width': width / scale, 'logical_height': height / scale,
                             'selected_scale': scale, 'operation': 'lossless_copy',
                             'layout_requirement': 'Use explicit source logical dimensions; intrinsic size equivalence is unverified'})
        except (MigrationError, OSError, struct.error) as exc:
            issues.append({'code': 'asset_conversion_blocked', 'path': asset['path'], 'message': str(exc)})
    return {'mappings': mappings, 'pixel_transformation': False}, issues, payload


def locale_qualifier(locale):
    parts = re.split('[-_]', locale)
    if not re.fullmatch('[a-z]{2,3}', parts[0]):
        raise MigrationError(f'Unsupported locale: {locale}')
    rest = parts[1:]
    if rest and re.fullmatch('[A-Z][a-z]{3}', rest[0]):
        rest = rest[1:]
    if rest and re.fullmatch('[A-Z]{2,3}|[0-9]{3}', rest[0]):
        rest = rest[1:]
    if rest:
        raise MigrationError(f'Unsupported locale extension: {locale}')
    return '_'.join(parts)


def localization_inventory(root, files):
    entries, issues = [], []
    for item in files:
        path = root / item['path']
        try:
            if path.suffix == '.xcstrings':
                catalog = read_json(path)
                language = catalog.get('sourceLanguage')
                namespace = Path(item['path']).with_suffix('').as_posix()
                for key, value in catalog.get('strings', {}).items():
                    if value.get('shouldTranslate') is False:
                        issues.append({'code': 'nonlocalized_key', 'path': item['path'], 'key': key})
                        continue
                    localized = dict(value.get('localizations', {}))
                    if language and language not in localized:
                        localized[language] = {'stringUnit': {'state': 'source_key_fallback', 'value': key}}
                    for locale, unit in localized.items():
                        if set(unit) != {'stringUnit'} or not isinstance(unit.get('stringUnit'), dict):
                            issues.append({'code': 'localization_variations_unmapped', 'path': item['path'], 'key': key, 'locale': locale})
                            continue
                        entries.append({'namespace': namespace, 'key': key, 'locale': locale,
                            'value': unit['stringUnit'].get('value'), 'state': unit['stringUnit'].get('state'),
                            'path': item['path'], 'sha256': item['sha256']})
            elif path.suffix == '.strings':
                raw = path.read_bytes()
                text = raw.decode('utf-16') if raw.startswith((b'\xff\xfe', b'\xfe\xff')) else raw.decode('utf-8-sig')
                values = OpenStep('{' + text + '}').parse()
                locale_parts = [p[:-6] for p in Path(item['path']).parts if p.endswith('.lproj')]
                if len(locale_parts) != 1 or locale_parts[0] == 'Base':
                    issues.append({'code': 'strings_locale_unresolved', 'path': item['path']})
                    continue
                namespace = '/'.join(p for p in Path(item['path']).with_suffix('').parts if not p.endswith('.lproj'))
                for key, value in values.items():
                    entries.append({'namespace': namespace, 'key': key, 'value': value, 'locale': locale_parts[0],
                                    'state': 'literal_file', 'path': item['path'], 'sha256': item['sha256']})
            elif path.suffix == '.stringsdict':
                issues.append({'code': 'stringsdict_plural_rule_unmapped', 'path': item['path']})
        except (MigrationError, UnicodeError, AttributeError, TypeError) as exc:
            issues.append({'code': 'localization_parse_failed', 'path': item['path'], 'message': str(exc)})
    return {'entries': entries}, issues


def convert_localization(inventory, default_locale):
    default = locale_qualifier(default_locale)
    groups, issues = defaultdict(dict), []
    mappings, seen = {}, set()
    for entry in inventory['entries']:
        try:
            locale = locale_qualifier(entry['locale'])
            value = entry['value']
            if not isinstance(value, str) or '%' in value:
                raise MigrationError('Format placeholders require a typed formatting rule')
            if entry['state'] not in {'translated', 'source_key_fallback', 'literal_file'}:
                raise MigrationError('Unapproved/untranslated localization state')
            name = resource_name(entry['namespace'], entry['key'])
            identity = (locale, name)
            if identity in seen:
                raise MigrationError('Duplicate localization key in the same locale')
            seen.add(identity)
            groups[locale][name] = value
            mappings[name] = {'namespace': entry['namespace'], 'key': entry['key'], 'resource': 'app.string.' + name}
        except MigrationError as exc:
            issues.append({'code': 'localization_conversion_blocked', 'path': entry['path'], 'key': entry['key'], 'message': str(exc)})
    base = groups.get(default, {})
    valid = set(base)
    for locale, values in groups.items():
        for name in set(values) - valid:
            issues.append({'code': 'default_locale_value_missing', 'locale': locale, 'resource': name})
    payload = {}
    for locale, values in groups.items():
        allowed = {name: value for name, value in values.items() if name in valid}
        if allowed:
            qualifier = 'base' if locale == default else locale
            payload[f'entry/src/main/resources/{qualifier}/element/ios_strings.json'] = json_bytes({
                'string': [{'name': name, 'value': allowed[name]} for name in sorted(allowed)]})
    return {'mappings': [mappings[name] for name in sorted(valid)], 'default_locale': default_locale,
            'callsite_rewriting': 'not_performed'}, issues, payload
