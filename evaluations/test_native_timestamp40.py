"""Exact JSON-number/XML-text pairing, with no timestamp approximation."""
import copy
from pathlib import Path
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from hmigbot_ios.core import MigrationError,read_json,write_json
from hmigbot_ios152 import native_canonical as C
from hmigbot_ios152.native_visual import observation_xml
from evaluations.test_native_canonical import capture


class NativeTimestampPairing(unittest.TestCase):
 def test_numeric_and_legacy_text_timestamps_remain_exact(self):
  with tempfile.TemporaryDirectory(prefix='native40-timestamp-') as directory:
   for start,finish in [(1793057663,1793057663.933986),(1793057663.686528,1793057663.933986),
                        ('2026-10-27T00:00:00Z','2026-10-27T00:00:01Z')]:
    meta=capture(Path(directory)/str(type(start).__name__),'Neutral')
    self.retime(meta,start,finish);C.capture_pair(meta)
    paths,xml,_=C.capture_pair(meta)
    xml.set('capture_finished_at',str(finish)+'0')
    self.write_xml(meta,xml)
    with self.assertRaisesRegex(MigrationError,'timestamp mismatch'):C.capture_pair(meta)
 def test_invalid_json_timestamp_types_cannot_match_their_string_spelling(self):
  with tempfile.TemporaryDirectory(prefix='native40-invalid-') as directory:
   for index,value in enumerate([True,False,None,'',0,{},[],float('nan'),float('inf'),float('-inf')]):
    meta=capture(Path(directory)/str(index),'Neutral');self.retime(meta,value,value)
    with self.subTest(value=value),self.assertRaisesRegex(MigrationError,'timestamp mismatch|Non-finite JSON number'):C.capture_pair(meta)
 def test_pairing_still_rejects_wrong_hash_or_capture_identity(self):
  with tempfile.TemporaryDirectory(prefix='native40-binding-') as directory:
   meta=capture(Path(directory),'Neutral');self.retime(meta,1793057663.686528,1793057663.933986)
   changed=copy.deepcopy(meta);changed['sha256']['native_json']='wrong'
   with self.assertRaises(MigrationError):C.capture_pair(changed)
   paths,xml,_=C.capture_pair(meta);xml.set('request_id','another-request');self.write_xml(meta,xml)
   with self.assertRaisesRegex(MigrationError,'capture ID or hash'):C.capture_pair(meta)
 @staticmethod
 def write_xml(meta,xml):
  import xml.etree.ElementTree as ET
  data=ET.tostring(xml,encoding='unicode');Path(meta['dump_path']).write_text(data,encoding='utf-8')
  Path(meta['raw_xml']).write_text(data,encoding='utf-8')
  meta['sha256']['xml']=C.sha(meta['dump_path']);meta['raw_sha256']['xml']=C.sha(meta['raw_xml'])
 @staticmethod
 def retime(meta,start,finish):
  path=Path(meta['native_json']);native=read_json(path);native.update(started_at=start,finished_at=finish);write_json(path,native)
  meta['sha256']['native_json']=C.sha(path);meta['raw_sha256']['native_json']=C.sha(path)
  data=observation_xml(native,native_sha256=C.sha(path),png_sha256=C.sha(meta['shot_path']))
  Path(meta['dump_path']).write_text(data,encoding='utf-8');Path(meta['raw_xml']).write_text(data,encoding='utf-8')
  meta['sha256']['xml']=C.sha(meta['dump_path']);meta['raw_sha256']['xml']=C.sha(meta['raw_xml'])


if __name__=='__main__':unittest.main()
