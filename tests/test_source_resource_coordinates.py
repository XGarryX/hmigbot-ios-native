"""Resource decoding is format-aware; coordinates never erase obligations."""
from pathlib import Path
import plistlib

import pytest

from hmigbot_ios.core import MigrationError, digest
from hmigbot_ios.ios_facts import extract, obligations


@pytest.mark.parametrize('suffix', ['.plist', '.entitlements', '.xcprivacy', '.stringsdict'])
def test_valid_binary_property_list_has_verified_document_coordinates(tmp_path, suffix):
    from hmigbot_ios.source_scope import source_anchor_info
    path = tmp_path / ('Metadata' + suffix)
    path.write_bytes(plistlib.dumps({'CFBundleName': '真实资源 #Preview 不排除', 'Enabled': False}, fmt=plistlib.FMT_BINARY))
    info = source_anchor_info(path)
    assert info['coordinate_kind'] == 'resource_document'
    assert info['source_sha256'] == digest(path.read_bytes())
    assert info['format'] == 'plist' and info['content_validation'] == 'parsed'
    assert info['line_count'] == 1
    graph = extract(tmp_path)
    fact, = [f for f in graph['facts'] if f['kind'] == 'resource']
    assert fact['value']['content_validation'] == 'parsed'
    assert fact['value']['source_sha256'] == digest(path.read_bytes())
    assert fact['value']['coordinate_kind'] == 'resource_document'
    assert any(o['fact_id'] == fact['id'] for o in obligations(graph)['obligations'])
    assert graph['issues'] == []


def test_valid_xml_uses_real_text_lines_and_is_parsed(tmp_path):
    from hmigbot_ios.source_scope import source_anchor_info
    path = tmp_path / 'Metadata.plist'
    path.write_bytes(plistlib.dumps({'CFBundleName': 'XML'}))
    info = source_anchor_info(path)
    assert info['coordinate_kind'] == 'text_line'
    assert info['line_count'] == len(path.read_text().splitlines())
    assert info['content_validation'] == 'parsed'


@pytest.mark.parametrize('payload', [b'bplist00\x80\xff', b'<plist><dict><key>x</key></plist>', b'ordinary text is not plist'])
def test_malformed_resource_blocks_extraction_instead_of_disappearing(tmp_path, payload):
    from hmigbot_ios.source_scope import source_anchor_info
    path = tmp_path / 'Broken.plist'
    path.write_bytes(payload)
    with pytest.raises(MigrationError, match='Invalid property-list resource'):
        source_anchor_info(path)
    graph = extract(tmp_path)
    assert any(i['rule'] == 'IOS.RESOURCE_PARSE' and i['path'] == 'Broken.plist' for i in graph['issues'])


@pytest.mark.parametrize('suffix', ['.swift', '.m', '.mm', '.h'])
def test_code_remains_strict_text_including_objective_c(tmp_path, suffix):
    from hmigbot_ios.source_scope import source_anchor_info
    path = tmp_path / ('App' + suffix)
    path.write_text('// 中文\nvoid open(void);\n')
    assert source_anchor_info(path) == {'line_count': 2, 'coordinate_kind': 'text_line'}
    path.write_bytes(b'\xff\xfe\x80')
    with pytest.raises(UnicodeError):
        source_anchor_info(path)
