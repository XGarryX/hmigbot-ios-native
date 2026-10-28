import copy
import json
from pathlib import Path
import struct
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
import zlib

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from hmigbot_ios152.native_visual import arrival, observation_xml, signature_strings, live_page_queries


def observation(scale=2):
    def node(kind, identifier, label, frame, children=None):
        return {'element_type':kind,'identifier':identifier,'label':label,'value':None,
                'exists':True,'enabled':True,'selected':False,'hittable':None,
                'frame':dict(zip(('x','y','width','height'),frame)),'children':children or []}
    button = node(9,'go.detail','Open detail',(10,20,80,30))
    second = node(9,'go.other','Open detail',(110,20,80,30))
    tree = node(2,'','Neutral',(0,0,200,400),[button,second])
    return {'platform':'ios','session':'fixture','request_id':'capture-1','bundle_id':'org.neutral.app',
            'collection_method':'public_snapshot','started_at':1,'finished_at':2,
            'app_state_before':4,'app_state_after':4,'tree':tree,
            'system_tree_status':'observed','system_overlay':{'alert_count':0},
            'screenshot':{'pixel_per_point_x':scale,'pixel_per_point_y':scale,
                          'origin_screen_points':{'x':0,'y':0},
                          'pixel_size':{'width':200*scale,'height':400*scale}}}


class NativeVisualTests(unittest.TestCase):
    def test_native_types_identifiers_and_live_hittability(self):
        tree = ET.fromstring(observation_xml(observation(),{'0/0':True,'0/1':True},native_sha256='abc'))
        buttons = [n for n in tree.iter('node') if n.get('class') == 'XCUIElementTypeButton']
        self.assertEqual(2,len(buttons))
        self.assertEqual({'go.detail','go.other'},{n.get('identifier') for n in buttons})
        self.assertTrue(all(n.get('resource-id') == '' and n.get('clickable') == 'true' for n in buttons))
        self.assertEqual('abc',tree.get('native_snapshot_sha256'))
        self.assertNotIn('android.',ET.tostring(tree,encoding='unicode'))

    def test_unknown_hittability_retains_candidates_without_claiming_hittable(self):
        tree = ET.fromstring(observation_xml(observation()))
        buttons=[n for n in tree.iter('node') if n.get('class')=='XCUIElementTypeButton']
        self.assertEqual(2,len(buttons))
        self.assertTrue(all(n.get('clickable')=='true' and n.get('native_hittable')=='unknown' for n in buttons))

    def test_unidentified_and_duplicate_label_candidates_are_not_dropped(self):
        data=observation()
        data['tree']['children'][0].update(identifier='',label='',hittable=None)
        other=copy.deepcopy(data['tree']['children'][1]);other.update(identifier='',hittable=False)
        data['tree']['children'].append(other)
        tree=ET.fromstring(observation_xml(data))
        buttons=[n for n in tree.iter('node') if n.get('class')=='XCUIElementTypeButton']
        self.assertEqual(3,len(buttons))
        self.assertTrue(all(n.get('clickable')=='true' for n in buttons))
        self.assertEqual(['unknown','unknown','false'],[n.get('native_hittable') for n in buttons])

    def test_real_scale_and_nonzero_screen_origin(self):
        for scale in (2,3):
            data = observation(scale)
            data['screenshot']['origin_screen_points'] = {'x':2,'y':3}
            tree = ET.fromstring(observation_xml(data))
            button = next(n for n in tree.iter('node') if n.get('identifier') == 'go.detail')
            self.assertEqual('[%d,%d][%d,%d]' % (8*scale,17*scale,88*scale,47*scale),button.get('bounds'))

    def test_page_identity_is_unique_not_application_state(self):
        data = observation()
        identities = {'Home':{'required':[{'identifier':'go.detail','type':'Button'}]},
                      'Detail':{'required':[{'label':'Detail title'}]}}
        self.assertTrue(arrival(data,'Home',identities)['arrived'])
        self.assertFalse(arrival(data,'Detail',identities)['arrived'])
        identities['Other'] = copy.deepcopy(identities['Home'])
        self.assertFalse(arrival(data,'Home',identities)['arrived'])

    def test_screenshot_projection_clips_legacy_fields_and_keeps_native_facts(self):
        for scale in (2,3):
            data=observation(scale); original=copy.deepcopy(data)
            base=data['tree']['children'][0]
            off=copy.deepcopy(base);off.update(identifier='offscreen',label='Offscreen',hittable=True)
            off['frame'].update(y=450)
            partial=copy.deepcopy(base);partial.update(identifier='partial',label='Partial',hittable=True)
            partial['frame'].update(y=390,height=30)
            absent=copy.deepcopy(base);absent.update(identifier='absent',exists=False,hittable=True)
            disabled=copy.deepcopy(base);disabled.update(identifier='disabled',enabled=False,hittable=False,label='Disabled text')
            data['tree']['children'] += [off,partial,absent,disabled]
            snapshot=copy.deepcopy(data)
            raw=observation_xml(data,native_sha256='json-hash',png_sha256='png-hash')
            self.assertEqual(raw,observation_xml(data,native_sha256='json-hash',png_sha256='png-hash'))
            tree=ET.fromstring(raw);byid={n.get('identifier'):n for n in tree.iter('node')}
            self.assertEqual(snapshot,data)
            self.assertEqual('',byid[''].get('text'))
            self.assertEqual(original['tree']['label'],byid[''].get('native_label'))
            self.assertEqual('png-hash',tree.get('screenshot_sha256'))
            self.assertEqual('screenshot-viewport-v1',tree.get('comparison_projection'))
            for key in ('offscreen','absent'):
                n=byid[key]
                self.assertEqual(('', '', 'false', '[0,0][0,0]'),tuple(n.get(k) for k in ('text','content-desc','clickable','bounds')))
                self.assertTrue(n.get('native_label'))
            self.assertEqual('[%d,%d][%d,%d]'%(10*scale,390*scale,90*scale,400*scale),byid['partial'].get('bounds'))
            self.assertEqual('Partial',byid['partial'].get('text'))
            self.assertEqual('Disabled text',byid['disabled'].get('text'))
            self.assertEqual('false',byid['disabled'].get('clickable'))
            for n in tree.iter('node'):
                import re
                x1,y1,x2,y2=map(int,re.findall(r'-?\d+',n.get('bounds')))
                self.assertTrue(0<=x1<=x2<=200*scale and 0<=y1<=y2<=400*scale)

    def test_screenshot_projection_rejects_inconsistent_geometry(self):
        from hmigbot_ios.core import MigrationError
        data=observation();data['screenshot']['point_size']={'width':400,'height':200}
        with self.assertRaises(MigrationError):observation_xml(data)
        data=observation();data['screenshot']['pixel_per_point_y']=3
        with self.assertRaises(MigrationError):observation_xml(data)

    def test_failed_overwrite_cannot_leave_previous_success_eligible(self):
        from hmigbot_ios152.native_visual import capture
        from hmigbot_ios152.xcode_ui import XcodeUIError
        class FailedSession:
            def capture(self,*args,**kwargs):raise XcodeUIError('owned fixture collection failed')
        with tempfile.TemporaryDirectory() as tmp:
            directory=Path(tmp);png=directory/'Home.png';xml=directory/'Home.ios.xml';meta=directory/'Home.capture.json'
            png.write_bytes(b'preserved diagnostic png');xml.write_text('<preserved/>')
            previous={'status':'ok','page_id':'Home'};meta.write_text(json.dumps(previous))
            code,result=capture(FailedSession(),'Home',{},directory,overwrite=True,trip='trip_1')
            self.assertEqual(13,code);self.assertEqual('dump_unavailable',result['status'])
            self.assertEqual(b'preserved diagnostic png',png.read_bytes())
            self.assertEqual('<preserved/>',xml.read_text())
            invalidated=json.loads(meta.read_text())
            self.assertEqual('capture_pending',invalidated['status'])
            self.assertEqual(previous,invalidated['previous_capture'])

    def test_duplicate_labels_are_ambiguous(self):
        identities = {'Home':{'required':[{'label':'Open detail'}]}}
        self.assertFalse(arrival(observation(),'Home',identities)['arrived'])

    def test_public_query_rejects_background_and_resolves_snapshot_layer_duplication(self):
        data=observation();data['tree']['children'].append(copy.deepcopy(data['tree']['children'][0]))
        ids={'Home':{'required':[{'identifier':'go.detail','element_type':9}]}}
        self.assertFalse(arrival(data,'Home',ids)['arrived'])
        class Live:
            visible=True
            def command(self,*args):
                node=copy.deepcopy(data['tree']['children'][0]);node['hittable']=self.visible
                return {'ok':True,'result':node}
        live=Live();queries=live_page_queries(live,data,ids)
        self.assertTrue(arrival(data,'Home',ids,queries)['arrived'])
        live.visible=False
        self.assertFalse(arrival(data,'Home',ids,live_page_queries(live,data,ids))['arrived'])

    def test_system_permission_and_unknown_system_tree_block_arrival(self):
        data = observation(); ids = {'Home':{'required':[{'identifier':'go.detail'}]}}
        data['system_overlay']['alert_count'] = 1
        self.assertIn('system_alert_present',arrival(data,'Home',ids)['blockers'])
        data['system_overlay']['alert_count'] = 0; data.pop('system_tree_status')
        self.assertIn('system_overlay_unknown',arrival(data,'Home',ids)['blockers'])

    def test_ambiguous_exclusion_query_never_becomes_proven_absence(self):
        data=observation();ids={'Home':{'required':[{'identifier':'go.detail'}],
                                      'excluded':[{'label':'Open detail'}]}}
        class Live:
            def command(self,operation,args):
                if 'label' in args['selector']:
                    return {'ok':False,'error':{'code':'ambiguous'}}
                n=copy.deepcopy(data['tree']['children'][0]);n['hittable']=True
                return {'ok':True,'result':n}
        queries=live_page_queries(Live(),data,ids)
        self.assertFalse(arrival(data,'Home',ids,queries)['arrived'])

    def test_not_found_with_invalidated_session_is_tool_error_not_absence(self):
        from hmigbot_ios152.xcode_ui import XcodeUIError
        data=observation();ids={'Home':{'required':[{'identifier':'go.detail'}],
                                      'excluded':[{'label':'Missing'}]}}
        class Live:
            def command(self,operation,args):
                if 'label' in args['selector']:
                    return {'ok':False,'error':{'code':'not_found'},'session_invalidated':True,'evidence_status':'timeout'}
                n=copy.deepcopy(data['tree']['children'][0]);n['hittable']=True
                return {'ok':True,'result':n}
        with self.assertRaises(XcodeUIError):live_page_queries(Live(),data,ids)

    def test_signatures_keep_stable_string_contract(self):
        signatures = signature_strings(observation())
        self.assertIn('identifier:go.detail',signatures)
        self.assertIn('text:Open detail',signatures)
        self.assertEqual(1,signatures.count('text:Open detail'))

    def test_observer_build_snapshot_is_checked_when_known(self):
        from hmigbot_ios152.native_visual import observer_build
        from hmigbot_ios.core import MigrationError
        from types import SimpleNamespace
        state={'source_app_build':{'build_record_binding':True,'source_sha256':'old'}}
        session=SimpleNamespace(state=state)
        with self.assertRaisesRegex(MigrationError,'earlier source snapshot'):
            observer_build({'native_context':{'source_sha256':'current'}},session)
        self.assertEqual(state['source_app_build'],observer_build({'native_context':{'source_sha256':'old'}},session))
        self.assertEqual(state['source_app_build'],observer_build({},session))

    def test_imageio_decodes_black_and_nonblack_png(self):
        from hmigbot_ios152.apple_image import inspect
        def png(rgb):
            def chunk(name,data):
                return struct.pack('>I',len(data))+name+data+struct.pack('>I',zlib.crc32(name+data)&0xffffffff)
            return b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',8,8,8,2,0,0,0))+chunk(b'IDAT',zlib.compress((b'\0'+bytes(rgb)*8)*8))+chunk(b'IEND',b'')
        with tempfile.TemporaryDirectory() as tmp:
            dark = Path(tmp)/'black.png';dark.write_bytes(png((0,0,0)))
            light = Path(tmp)/'light.png';light.write_bytes(png((255,255,255)))
            self.assertTrue(inspect(dark)['black_sample'])
            self.assertFalse(inspect(light)['black_sample'])
            corrupt = Path(tmp)/'invalid.png';corrupt.write_text('not PNG')
            with self.assertRaises(ValueError): inspect(corrupt)


if __name__ == '__main__': unittest.main()
