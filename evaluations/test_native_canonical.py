"""Neutral iOS canonical contracts; synthetic fixtures are not device evidence.

Set HMIGBOT_TEST_ORIGINAL_VISUAL_ENGINE to an isolated original engine for the
optional real-core differential tests. No test calls a device command.
"""
from __future__ import annotations
from contextlib import redirect_stdout,redirect_stderr
import copy
from datetime import datetime,timedelta
import io
import json
import os
from pathlib import Path
import random
import shutil
import struct
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch
import uuid
import zlib

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from hmigbot_ios.core import MigrationError,read_json,write_json
from hmigbot_ios152 import native_canonical as C
from hmigbot_ios152 import visual_dispatch as D
from hmigbot_ios152.native_visual import observation_xml


def png(path,width=400,height=800,seed=7):
    rng=random.Random(seed)
    raw=b''.join(b'\0'+rng.randbytes(width*3) for _ in range(height))
    def chunk(kind,data):
        return struct.pack('>I',len(data))+kind+data+struct.pack('>I',zlib.crc32(kind+data)&0xffffffff)
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',width,height,8,2,0,0,0))+
                     chunk(b'IDAT',zlib.compress(raw))+chunk(b'IEND',b''))


def capture(folder,page,*,size=(400,800),seed=7,trip='trip_2_logged_in_vip'):
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=True)
    request=uuid.uuid4().hex;original=folder/'native-observations';original.mkdir(exist_ok=True)
    native=original/(request+'.native.json');raw_png=original/(request+'.png')
    image=folder/(page+'.png');xml=folder/(page+'.ios.xml')
    width,height=size
    def element(kind,label,frame,identifier='',children=None):
        return {'element_type':kind,'identifier':identifier,'label':label,'title':'','value':None,
                'placeholder_value':'','enabled':True,'selected':False,'exists':True,'hittable':kind==9,
                'frame':frame,'coordinate_space':'screen_points','children':children or []}
    tree=element(2,'Neutral app',{'x':0,'y':0,'width':width/2,'height':height/2},children=[
        element(48,page+' title',{'x':10,'y':30,'width':100,'height':25}),
        element(9,'Toggle favorite' if page=='LibraryView' else 'Open library' if page=='HomeView' else 'Cancel sheet',
                {'x':10,'y':80,'width':120,'height':30},'favorite' if page=='LibraryView' else '')])
    observation={'schema_version':1,'platform':'ios','session':'synthetic-contract-fixture',
        'request_id':request,'bundle_id':'org.hmigbot.neutral','collection_method':'synthetic-fixture',
        'started_at':'2026-10-26T00:00:00Z','finished_at':'2026-10-26T00:00:01Z',
        'app_state_before':4,'app_state_after':4,'system_tree_status':'observed',
        'system_overlay':{'alert_count':0},'tree':tree,
        'screenshot':{'pixel_size':{'width':width,'height':height},
            'point_size':{'width':width/2,'height':height/2},'image_scale':2,
            'pixel_per_point_x':2,'pixel_per_point_y':2,'origin_screen_points':{'x':0,'y':0}}}
    write_json(native,observation);png(raw_png,width,height,seed);shutil.copy2(raw_png,image)
    xml.write_text(observation_xml(observation,native_sha256=C.sha(native)))
    raw_xml=native.with_suffix('.ios.xml');shutil.copy2(xml,raw_xml)
    meta={'status':'ok','source_platform':'ios','page_id':page,'trip':trip,
        'shot_path':str(image),'dump_path':str(xml),'native_json':str(native),
        'raw_png':str(raw_png),'raw_xml':str(raw_xml),
        'captured_at':'2026-10-26T00:00:01Z','reach_path':['Synthetic contract fixture '+page],
        'arrival':{'arrived':True,'expected_page':page,'matched_pages':[page],'request_id':request},
        'observed_signature':[page+' title'],'nav_by':'synthetic-fixture','verify_by':'synthetic-fixture',
        'notes':['SYNTHETIC CONTRACT FIXTURE, NOT DEVICE VERIFICATION'],
        'sha256':{'png':C.sha(image),'xml':C.sha(xml),'native_json':C.sha(native)}}
    meta['raw_sha256']={'png':C.sha(raw_png),'xml':C.sha(raw_xml),'native_json':C.sha(native)}
    write_json(folder/(page+'.capture.json'),meta)
    return meta


class Fixture:
    def __init__(self,root,names=('HomeView','LibraryView','ConfirmSheet'),size=(400,800)):
        self.root=Path(root);self.ew=self.root/'spec/visual-verify/edgewalk'
        self.ew.mkdir(parents=True);self.tree=self.root/'spec/toolkit-fact-tree.json'
        self.trip='trip_2_logged_in_vip';self.names=names
        records=[{'id':name,'type':'Activity','fq_class':name,'purpose':'Neutral fixture',
                  'inbound_triggers':[],'functional_checks':[]} for name in names]
        if 'LibraryView' in names:
            record=next(x for x in records if x['id']=='LibraryView')
            record['inbound_triggers']=[{'from_page':'HomeView','trigger_label':'Open library',
                'trigger_view_id':None,'source':'synthetic-fixture','evidence_file':'Neutral.swift','evidence_line':8}]
            record['functional_checks']=[{'name':'Toggle favorite','expected_ios':'Favorite becomes selected',
                'ios_trusted':True,'ios_anchor':{'raw_identifier':'favorite'},'source_section':'click_handlers'}]
        if 'ConfirmSheet' in names:
            records[-1]['inbound_triggers']=[{'from_page':'LibraryView','trigger_label':'Show sheet',
                'trigger_view_id':None,'source':'synthetic-fixture','evidence_file':'Neutral.swift','evidence_line':13}]
        tree={'$schema_version':1,'source_platform':'ios','source':{'platform':'ios','generator':'synthetic-contract-fixture'},
              'app':{'launcher_short':'HomeView','launcher_activity':'HomeView','package':'org.hmigbot.neutral'},
              'pages':[r for r in records if r['id']!='ConfirmSheet'],'fragments':[],
              'dialogs':[{**r,'type':'Dialog'} for r in records if r['id']=='ConfirmSheet'],
              'flow_graph':{'nodes':[],'edges':[]}}
        write_json(self.tree,tree)
        steps=[{'step':1,'action':'coldstart','to':names[0],'settles_capture':names[0]}]
        for i,name in enumerate(names[1:],2):
            steps.append({'step':i,'action':'tap','from':names[i-2],'to':name,
                'trigger':'Open library' if i==2 else 'Show sheet','kind':'tab_switch' if i==2 else 'dialog',
                'safety':'normal','needs_discovery':False,'settles_capture':name})
        plan={'tree':str(self.tree),'targets':list(names),'target_count':len(names),
              'derived_config':{'launcher':names[0],'main_root':names[0]},
              'walks':[{'walk_id':'neutral_walk','trip_id':self.trip,'root':names[0],
                        'steps':steps,'settles':list(names)}],'orphans':[]}
        write_json(self.ew/'walk_plan.json',plan)
        ledger={'t0':0,'coldstarts':[],'targets':list(names),'settled':{}}
        for index,name in enumerate(names):
            meta=capture(self.ew/'shots',name,size=size,seed=index+7,trip=self.trip)
            ledger['settled'][name]={'via':'Synthetic fixture '+name,'capture':'verified',
                                      'trip':self.trip,'capture_meta':meta}
        write_json(self.ew/'ledger.json',ledger)
        self.baseline=self.root/'spec/visual-verify/screenshots/ios'/self.trip
    def place(self):return C.place_baselines(self.tree,self.ew,self.root,self.trip)


def trigger_source(root):
    """Official-parser input; declaration evidence, not a built/device app."""
    source=Path(root)/'source';source.mkdir(parents=True,exist_ok=True)
    (source/'Neutral.swift').write_text(r'''import SwiftUI
struct HomeView: View {
 var name: String = "World"
 var body: some View {
  VStack {
   Button("Open static") {}.accessibilityIdentifier("static-control")
   Button("Open \u{4e16}界") {}
   Text(#"Raw \ plain"#)
   Text("Hello \(name)").accessibilityIdentifier("dynamic-control")
   Text("Other").id("swiftui-id")
   if false { Text("Dead literal"); deadHelper() }
   helper()
  }
 }
 func helper() -> some View { Text("Reached helper") }
 func unused() -> some View { Text("Uncalled helper") }
 func deadHelper() -> some View { Text("False-branch helper") }
 // Comment only
}
''',encoding='utf-8')
    (source/'Neutral.storyboard').write_text('<document><label text="IB &amp; entity"/></document>')
    write_json(source/'Localizable.xcstrings',{'strings':{'catalog.key':{'localizations':{'en':{'stringUnit':{'value':'Catalog only'}}}}}})
    (source/'Localizable.strings').write_text('"Key only" = "Localized coffee";')
    write_json(source/'bundled.json',{'caption':'Resource only'})
    tree={'source_platform':'ios','source':{'platform':'ios','ios_root':str(source)},
          'pages':[{'id':'HomeView','fq_class':'HomeView'}],'fragments':[],'dialogs':[]}
    from hmigbot_ios152.source import Source
    from hmigbot_ios152.native_routes import analyze
    tree['source']['source_sha256']=analyze(Source(source))['source_sha']
    return source,tree


class CanonicalTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='native-canonical-test-');self.root=Path(self.temp.name)
    def tearDown(self):self.temp.cleanup()
    def test_wire_is_one_way_and_cannot_use_stale_android_alias(self):
        value={'source_platform':'ios','pages':[{'expected_ios':'current','ios_trusted':False,
                                               'expected_android':'STALE','android_trusted':True}]}
        wire=C.legacy_wire(value)
        self.assertEqual(wire['pages'][0]['expected_android'],'current')
        self.assertIs(wire['pages'][0]['android_trusted'],False)
        wire['pages'][0]['expected_android']='observed';wire['pages'][0]['android_trusted']=True
        native=C.native_writeback(value,wire)
        self.assertEqual(native['pages'][0]['expected_ios'],'observed')
        self.assertIs(native['pages'][0]['ios_trusted'],True)
        self.assertNotIn('expected_android',native['pages'][0])
    def test_wire_hash_tampering_fails(self):
        file=self.root/'tree.json';write_json(file,{'source_platform':'ios','source':{'platform':'ios'},'pages':[]})
        with C.wire_copy(file,self.root) as (wire,manifest,guard):
            C.verify_projection(file,wire,manifest)
            wire.write_text('{}')
            with self.assertRaises(MigrationError):C.verify_projection(file,wire,manifest)
    def test_old_string_source_is_explicitly_incompatible(self):
        with self.assertRaisesRegex(MigrationError,'regenerate'):
            C._source_current({'source_platform':'ios','source':'ios','pages':[]},self.root)
    def test_official_native_trigger_three_states_and_selected_text_resources(self):
        source,tree=trigger_source(self.root);guard=C.InputGuard();index=C.NativeTriggerIndex(tree,self.root,guard)
        for text in ('Open static','Open 世界','Raw \\ plain','IB & entity','Catalog only','Resource only','Key only','Reached helper'):
            with self.subTest(text=text):
                value=index.classify({'trigger_text':text})
                self.assertEqual(value['classification'],'static',value);self.assertTrue(value['evidence'])
        for text in ('Comment only','Dead literal','Uncalled helper','Unseen unknown','False-branch helper'):
            with self.subTest(text=text):self.assertEqual(index.classify({'trigger_text':text})['classification'],'unknown')
        self.assertEqual(index.classify({'trigger_text':'Hello Sam','trigger_native_identifier':'dynamic-control'})['classification'],'dynamic')
        self.assertEqual(index.classify({'trigger_text':'','trigger_native_identifier':'static-control'})['classification'],'static')
        self.assertEqual(index.classify({'trigger_text':'','trigger_native_identifier':'swiftui-id'})['classification'],'unknown')
        with self.assertRaisesRegex(MigrationError,'resource-id'):
            index.classify({'trigger_text':'Open static','trigger_resource_id':'fake.android:id/button'})
        (source/'bundled.json').write_text('{}')
        with self.assertRaises(MigrationError):guard.verify()
    def test_observed_native_ax_requires_real_three_way_capture(self):
        _,tree=trigger_source(self.root);index=C.NativeTriggerIndex(tree,self.root,C.InputGuard())
        meta=capture(self.root/'trigger','LibraryView')
        meta['native_blackbox_source_inputs_sha256']=index.source_inputs_sha256
        value=index.classify({'trigger_text':'','trigger_native_identifier':'favorite','trigger_capture_meta':meta})
        self.assertEqual(value['classification'],'static');self.assertEqual(value['evidence'][0]['kind'],'observed accessibilityIdentifier')
        meta['sha256']['native_json']='wrong'
        with self.assertRaises(MigrationError):index.classify({'trigger_text':'','trigger_native_identifier':'favorite','trigger_capture_meta':meta})
    def test_undecodable_selected_resource_stays_unknown_instead_of_dynamic(self):
        source,tree=trigger_source(self.root);(source/'bundled.json').write_text('{ broken JSON Resource only')
        index=C.NativeTriggerIndex(tree,self.root,C.InputGuard());value=index.classify({'trigger_text':'Resource only'})
        self.assertEqual(value['classification'],'unknown')
        self.assertTrue(any(v.get('reason')=='resource_text_not_decoded' for v in value['issues']))
    def test_discovery_missing_source_is_not_unsafe_static_fallback(self):
        with self.assertRaisesRegex(MigrationError,'require.*source'):
            C.NativeTriggerIndex({'source_platform':'ios','source':{'platform':'ios'},'pages':[]},self.root,C.InputGuard())
    def test_new_receipt_resource_scope_excludes_other_product_and_preserves_original_snapshot_guard(self):
        source=self.root/'source';source.mkdir();project=self.root/'target';(project/'.migbot').mkdir(parents=True)
        objects={'P':{'isa':'PBXProject','mainGroup':'G','projectDirPath':'','targets':['T1','T2'],'buildConfigurationList':'CL'},
            'G':{'isa':'PBXGroup','sourceTree':'<group>','children':['F1','F2','J1','J2']},
            'CL':{'isa':'XCConfigurationList','buildConfigurations':['C']},'C':{'isa':'XCBuildConfiguration','name':'Release','buildSettings':{}}}
        for n in ('1','2'):
            objects['T'+n]={'isa':'PBXNativeTarget','name':'App'+n,'productType':'com.apple.product-type.application',
                'buildConfigurationList':'CL','buildPhases':['S'+n,'R'+n],'dependencies':[]}
            objects['S'+n]={'isa':'PBXSourcesBuildPhase','files':['B'+n]};objects['B'+n]={'isa':'PBXBuildFile','fileRef':'F'+n}
            objects['F'+n]={'isa':'PBXFileReference','sourceTree':'<group>','path':'App'+n+'.swift'}
            objects['R'+n]={'isa':'PBXResourcesBuildPhase','files':['RB'+n]};objects['RB'+n]={'isa':'PBXBuildFile','fileRef':'J'+n}
            objects['J'+n]={'isa':'PBXFileReference','sourceTree':'<group>','path':'App'+n+'.json'}
            (source/('App'+n+'.swift')).write_text('import SwiftUI\nstruct Screen'+n+': View {var body:some View{Text("Screen")}}')
            write_json(source/('App'+n+'.json'),{'label':'Resource '+n})
        write_json(source/'Neutral.xcodeproj/project.pbxproj',{'objects':objects,'rootObject':'P'})
        variant={'scope':'project-targets','project_path':'Neutral.xcodeproj/project.pbxproj','targets':['App1'],'configuration':'Release'}
        write_json(project/'.migbot/config.json',{'source_platform':'ios','ios':{'source_root':str(source),'variant':variant}})
        tree={'source_platform':'ios','source':{'platform':'ios','ios_root':str(source)},'pages':[]}
        before=C._blackbox_source_inputs(tree,project)
        self.assertNotIn('App2.json',before['text_resources'])
        write_json(source/'App2.json',{'label':'Changed unselected product'})
        after=C._blackbox_source_inputs(tree,project)
        self.assertEqual(after['text_resources'],before['text_resources'])
        # Existing selection/source identity intentionally hashes the whole
        # source snapshot. The receipt must not bypass that original guard.
        self.assertNotEqual(after['route_source_sha256'],before['route_source_sha256'])
        write_json(source/'App1.json',{'label':'Changed selected product'})
        self.assertNotEqual(C._blackbox_source_inputs(tree,project)['text_resources'],before['text_resources'])
    def test_guard_detects_source_input_change(self):
        file=self.root/'source.swift';file.write_text('struct Neutral {}')
        guard=C.InputGuard();guard.add(file);file.write_text('struct Changed {}')
        with self.assertRaises(MigrationError):guard.verify()
    def test_three_way_pair_rejects_missing_dump_and_wrong_capture_id(self):
        meta=capture(self.root/'capture','HomeView')
        C.capture_pair(meta)
        not_arrived=copy.deepcopy(meta);not_arrived['arrival']['arrived']=False
        with self.assertRaisesRegex(MigrationError,'arrival'):C.capture_pair(not_arrived)
        wrong=copy.deepcopy(meta);value=read_json(Path(meta['native_json']));value['request_id']='wrong'
        write_json(Path(meta['native_json']),value);wrong['sha256']['native_json']=C.sha(meta['native_json'])
        wrong['raw_sha256']['native_json']=wrong['sha256']['native_json']
        with self.assertRaises(MigrationError):C.capture_pair(wrong)
        Path(meta['dump_path']).unlink()
        with self.assertRaises(MigrationError):C.capture_pair(meta)
    def test_native_source_placement_freezes_and_preserves_three_part_pair(self):
        fixture=Fixture(self.root);result=fixture.place()
        self.assertEqual(set(result['placed']),set(fixture.names))
        tree=read_json(fixture.tree)
        for page in tree['pages']:
            record=page['screenshots'][fixture.trip];C.capture_pair(record)
            self.assertEqual(record['capture_id'],record['arrival']['request_id'])
            self.assertTrue(Path(record['raw_capture']['shot_path']).is_file())
        before={p.name:C.sha(p) for p in fixture.baseline.iterdir()}
        again=fixture.place()
        self.assertEqual(set(again['skipped_exist']),set(fixture.names))
        self.assertEqual(before,{p.name:C.sha(p) for p in fixture.baseline.iterdir()})
    def test_official_resize_keeps_bounds_and_png_geometry_paired(self):
        fixture=Fixture(self.root,names=('HomeView',),size=(1900,2100));fixture.place()
        record=read_json(fixture.tree)['pages'][0]['screenshots'][fixture.trip]
        self.assertLessEqual(max(C._png_size(record['shot_path'])),1800)
        self.assertEqual(C._png_size(record['raw_capture']['shot_path']),(1900,2100))
        doc=C.ET.fromstring(Path(record['dump_path']).read_bytes())
        transform=record['canonical_transform'];self.assertAlmostEqual(float(doc.get('pixel_per_point_x')),2*transform['scale_x'])
        app=doc.find('node');self.assertEqual(app.get('bounds'),f'[0,0][{C._png_size(record["shot_path"])[0]},{C._png_size(record["shot_path"])[1]}]')
        self.assertEqual(json.loads(app.get('frame_points'))['width'],950)
        C.capture_pair(record)
    def test_native_mirror_ignores_residual_android_dump_and_detects_mirror_tampering(self):
        fixture=Fixture(self.root,names=('HomeView',));fixture.place()
        (fixture.baseline/'HomeView.android.xml').write_text('STALE INVALID ANDROID')
        destination=self.root/'internal';guard=C.InputGuard();mapping=C._mirror_baseline(read_json(fixture.tree),fixture.baseline,destination,guard)
        self.assertTrue((destination/'HomeView.xml').is_file())
        self.assertNotIn('STALE',(destination/'HomeView.xml').read_text())
        self.assertFalse((destination/'HomeView.android.xml').exists())
        (destination/'HomeView.xml').chmod(0o644);(destination/'HomeView.xml').write_text('tampered')
        with self.assertRaises(MigrationError):C._verify_mirror(mapping,destination,guard)
    def test_pending_and_unapplied_binding_are_original_red(self):
        fixture=Fixture(self.root,names=('HomeView',));write_json(fixture.ew/'pending_bindings.json',[{'node':'HomeView','verdict':'bind_as','applied':False}])
        with redirect_stdout(io.StringIO()),patch.object(C,'_core',side_effect=AssertionError('No backend step before pending gate')):
            self.assertEqual(C.finalize_cli(['--tree',str(fixture.tree),'--dir',str(fixture.ew),'--project-root',str(self.root),'--trip',fixture.trip,'--dry-run'],ROOT/'skills/arkts-visual-verify/scripts'),20)
    def test_mirror_preserves_file_and_round_directory_mtime_ns_after_all_writes(self):
        fixture=Fixture(self.root,names=('HomeView',));fixture.place()
        round_dir=self.root/'spec/fix/round-1';round_dir.mkdir(parents=True)
        proof=round_dir/'proof.json';write_json(proof,{'trip':fixture.trip,'path':str(fixture.tree)})
        file_ns=time.time_ns()-120_000_000_000+12345;directory_ns=file_ns-53
        os.utime(proof,ns=(file_ns,file_ns));os.utime(round_dir,ns=(directory_ns,directory_ns))
        with C.ProjectMirror(self.root,round_number=1,short_trips=True) as mirror:
            self.assertEqual((mirror.root/'spec/fix/round-1').stat().st_mtime_ns,directory_ns)
            self.assertEqual((mirror.root/'spec/fix/round-1/proof.json').stat().st_mtime_ns,file_ns)
    def test_observed_unjudged_and_duplicate_names_require_real_judgements(self):
        ew=self.root/'ew';write_json(ew/'grounding/Home/run_meta.json',{'node':'Home','checks':[{'idx':1,'name':'Same','status':'ok'},{'idx':2,'name':'Same','status':'ok'}]})
        write_json(ew/'grounding_results.json',[{'node':'Home','check_name':'Same','expected_ios':'a'}])
        self.assertIn('unjudged',C._judgement_debt(ew))
        write_json(ew/'grounding_results.json',[{'node':'Home','check_idx':i,'check_name':'Same','expected_ios':'a'} for i in [1,2]])
        self.assertIsNone(C._judgement_debt(ew))
    def test_unsupported_ios_source_entry_never_calls_original_device_backend(self):
        tree=self.root/'tree.json';write_json(tree,{'source_platform':'ios','pages':[]})
        with patch('hmigbot_ios152.compiled_runtime.run',side_effect=AssertionError('ADB backend reached')),redirect_stderr(io.StringIO()):
            self.assertEqual(D.run('node_sweep',['--tree',str(tree)],ROOT/'skills/arkts-visual-verify/scripts'),2)
    def test_anonymous_native_controls_remain_distinct(self):
        meta=capture(self.root/'capture','HomeView');observation=read_json(Path(meta['native_json']))
        button=copy.deepcopy(observation['tree']['children'][1]);button['identifier']='';button['label']='Anonymous'
        second=copy.deepcopy(button);second['frame']['y']=130
        observation['tree']['children']=[button,second]
        class Session:
            def capture(self,output,**kwargs):return {'observation':observation,'native_json':meta['native_json'],'png':meta['shot_path']}
        out=io.StringIO()
        with patch.object(D,'_session',return_value=Session()),redirect_stdout(out):self.assertEqual(D.native_clickables(['--all']),0)
        result=json.loads(out.getvalue());self.assertEqual(result['count'],2)
        self.assertNotEqual(result['elements'][0]['frame_points'],result['elements'][1]['frame_points'])
    def test_public_wrapper_inventory_all_bootstrap_and_deny_unknown_source(self):
        scripts=ROOT/'skills/arkts-visual-verify/scripts'
        for file in scripts.glob('*.py'):
            text=file.read_text();self.assertIn('visual_dispatch import run',text,file.name)
            self.assertNotIn('os.execv',text,file.name)
    def test_documented_ios_public_alias_retains_gate_and_survey_is_explicit(self):
        tree=self.root/'tree.json';write_json(tree,{'source_platform':'ios','source':{'platform':'ios'},'pages':[]})
        scripts=ROOT/'skills/arkts-visual-verify/scripts'
        with patch.object(C,'data_cli',return_value=43) as gate:
            self.assertEqual(D.run('check_ios_screenshot',[str(tree)],scripts),43)
            gate.assert_called_once_with('check_android_screenshot',[str(tree)],scripts)
        with patch('hmigbot_ios152.compiled_runtime.run',side_effect=AssertionError('opaque survey called')):
            with redirect_stdout(io.StringIO()),redirect_stderr(io.StringIO()):
                self.assertEqual(D.run('run_phase2_ios_survey',['--help'],scripts),0)
                self.assertEqual(D.run('run_phase2_ios_survey',[str(tree)],scripts),2)


@unittest.skipUnless(os.environ.get('HMIGBOT_TEST_ORIGINAL_VISUAL_ENGINE'),'Optional isolated original-core differential')
class OriginalCoreTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='native-original-core-test-');self.root=Path(self.temp.name)
        self.engine=Path(os.environ['HMIGBOT_TEST_ORIGINAL_VISUAL_ENGINE']).resolve()
        def execute(command,args,scripts,*,cwd=None,env=None):
            return subprocess.run([str(self.engine),command,*map(str,args)],cwd=cwd,
                capture_output=True,text=True,timeout=60,env={**os.environ,**(env or {}),'ARKTS_SKILL_DIR':str(self.engine.parents[3]),'PYTHONDONTWRITEBYTECODE':'1'})
        self.mock=patch.object(C,'_core',side_effect=execute);self.mock.start()
    def tearDown(self):self.mock.stop();self.temp.cleanup()
    def native_blackbox_fixture(self,text='Resource only'):
        fixture=Fixture(self.root,names=('HomeView',));source,source_tree=trigger_source(self.root)
        tree=read_json(fixture.tree);tree['source']=source_tree['source'];write_json(fixture.tree,tree)
        discovery={'key':'resource-trigger','trigger_text':text,'trigger_resource_id':'','landing_ability':'DetailView',
            'trigger_class':'XCUIElementTypeButton','landing_signature':'fixture detail'}
        variant,_,_=C._native_variant(tree['pages'][0],discovery)
        meta=capture(self.root/'variant-observations',variant['id'],trip=fixture.trip)
        meta['native_blackbox_source_inputs_sha256']=C._json_digest(C._blackbox_source_inputs(tree,self.root))
        discovery.update(capture_meta=meta,screenshot=meta['shot_path'],dump=meta['dump_path'])
        directory=self.root/'spec/visual-verify/blackbox_discoveries';manifest=directory/'round-0/HomeView/HomeView__manifest.json'
        data={'parent_page_id':'HomeView','trip_id':fixture.trip,'discoveries':[discovery],
            'behavior_ledger':[{'trigger_text':text,'outcome':'page_change'}]}
        write_json(manifest,data);args=['--factree',str(fixture.tree),'--discoveries-dir',str(directory)]
        with redirect_stdout(io.StringIO()),redirect_stderr(io.StringIO()):self.assertEqual(C.materialize_native_cli(args,ROOT/'skills/arkts-visual-verify/scripts'),0)
        return fixture,source,manifest,data,args
    def test_native_blackbox_receipt_covers_resource_set_and_tamper_but_not_new_unrun_requirement(self):
        fixture,source,manifest,data,args=self.native_blackbox_fixture();tree=read_json(fixture.tree)
        receipt=tree['native_blackbox_input_identity'];C._source_current(tree,self.root)
        file=self.root/receipt['receipt'];original=file.read_bytes();file.write_text('{}')
        with self.assertRaises(C.BindingError):C._source_current(tree,self.root)
        file.write_bytes(original);tampered=copy.deepcopy(tree);tampered['native_blackbox_input_identity']['sha256']='bad'
        with self.assertRaises(C.BindingError):C._source_current(tampered,self.root)
        no_receipt=copy.deepcopy(tree);no_receipt.pop('native_blackbox_input_identity')
        with self.assertRaisesRegex(C.BindingError,'without.*receipt'):C._source_current(no_receipt,self.root)
        ordinary=copy.deepcopy(tree);ordinary.pop('native_blackbox_input_identity');ordinary['pages']=[ordinary['pages'][0]];ordinary['pages'][0].pop('blackbox_behavior')
        C._source_current(ordinary,self.root)  # No executed blackbox: no extra requirement.
        added=source/'added.json';write_json(added,{'caption':'New selected root resource'})
        with self.assertRaises(C.BindingError):C._source_current(tree,self.root)
        added.unlink();C._source_current(tree,self.root)
        write_json(source/'bundled.json',{'caption':'Changed bundled value'})
        with self.assertRaises(C.BindingError):C._source_current(tree,self.root,allow_manifest_collection=True)
        # Refresh permits only the receipt to be stale; current native source
        # facts still pass, and the resource now has an unknown trigger debt.
        with redirect_stdout(io.StringIO()),redirect_stderr(io.StringIO()):self.assertEqual(C.materialize_native_cli(args,ROOT/'skills/arkts-visual-verify/scripts'),20)
        fresh=read_json(fixture.tree);self.assertNotEqual(fresh['native_blackbox_input_identity']['sha256'],receipt['sha256'])
        self.assertTrue(C._judgement_debt(fixture.ew))
        with self.assertRaises(C.BindingError):C._baseline_record(fresh,'DetailView#via=Resource_only',fixture.baseline)
    def test_native_collection_only_appends_and_consumers_cannot_open_exception(self):
        fixture,source,manifest,data,args=self.native_blackbox_fixture();tree=read_json(fixture.tree)
        data['behavior_ledger'].append({'trigger_text':'New observation','outcome':'noop'});write_json(manifest,data)
        state=C._source_current(tree,self.root,allow_manifest_collection=True)
        self.assertEqual(state['native_classification_status'],'pending_rematerialization')
        with self.assertRaises(C.BindingError):C._source_current(tree,self.root)
        scripts=ROOT/'skills/arkts-visual-verify/scripts'
        with redirect_stdout(io.StringIO()),redirect_stderr(io.StringIO()):
            self.assertEqual(D.run('compile_replay_plan',['--tree',str(fixture.tree),'--baseline-dir',str(fixture.baseline),
                '--out',str(self.root/'plan.json'),'--allow-manifest-collection'],scripts),22)
        data['behavior_ledger'][0]['outcome']='edited';write_json(manifest,data)
        with self.assertRaises(C.BindingError):C._source_current(tree,self.root,allow_manifest_collection=True)
        data['behavior_ledger'].pop(0);write_json(manifest,data)
        with self.assertRaises(C.BindingError):C._source_current(tree,self.root,allow_manifest_collection=True)
    def test_native_receipt_transaction_failure_leaves_prior_pair_recoverable(self):
        fixture,source,manifest,data,args=self.native_blackbox_fixture();old=fixture.tree.read_bytes();tree=read_json(fixture.tree)
        receipt=self.root/tree['native_blackbox_input_identity']['receipt'];receipt_bytes=receipt.read_bytes()
        write_json(source/'bundled.json',{'caption':'Changed selected resource'})
        writer=C.write_json
        def fail_tree(path,value):
            if Path(path).resolve()==fixture.tree.resolve():raise OSError('Synthetic tree commit failure')
            return writer(path,value)
        with patch.object(C,'write_json',side_effect=fail_tree),redirect_stdout(io.StringIO()),redirect_stderr(io.StringIO()):
            with self.assertRaises(OSError):C.materialize_native_cli(args,ROOT/'skills/arkts-visual-verify/scripts')
        self.assertEqual(fixture.tree.read_bytes(),old);self.assertEqual(receipt.read_bytes(),receipt_bytes)
        with redirect_stdout(io.StringIO()),redirect_stderr(io.StringIO()):self.assertEqual(C.materialize_native_cli(args,ROOT/'skills/arkts-visual-verify/scripts'),20)
        self.assertNotEqual(read_json(fixture.tree)['native_blackbox_input_identity']['sha256'],tree['native_blackbox_input_identity']['sha256'])
    def test_selected_resource_change_during_capture_stops_before_ledger_settle(self):
        fixture,source,manifest,data,args=self.native_blackbox_fixture();tree=read_json(fixture.tree)
        stable=C._source_current(tree,self.root,allow_manifest_collection=True)['native_blackbox_source_inputs_sha256']
        before=C.sha(fixture.ew/'ledger.json')
        def observer_capture(argv):
            meta=capture(Path(C._option(argv,'--shots-dir')),'HomeView',trip=fixture.trip)
            meta['native_blackbox_source_inputs_sha256']=stable
            write_json(source/'bundled.json',{'caption':'Changed during native observer request'})
            print(json.dumps(meta));return 0
        command=['--dir',str(fixture.ew),'settle','--node','HomeView','--via','actual raw fixture arrival',
            '--tree',str(fixture.tree),'--trip',fixture.trip,'--pkg','org.hmigbot.neutral','--launcher','HomeView','--project-root',str(self.root)]
        with patch('hmigbot_ios152.native_visual.capture_cli',side_effect=observer_capture):
            with self.assertRaises(C.BindingError):D.native_settle(command,ROOT/'skills/arkts-visual-verify/scripts')
        self.assertEqual(C.sha(fixture.ew/'ledger.json'),before)
    def test_original_writeback_updates_true_ios_fields(self):
        fixture=Fixture(self.root,names=('HomeView',));tree=read_json(fixture.tree);tree['pages'][0]['functional_checks']=[{'name':'Observe','expected_ios':None,'ios_trusted':None}];write_json(fixture.tree,tree)
        ground=self.root/'ground.json';write_json(ground,[{'node':'HomeView','check_name':'Observe','expected_ios':'Seen','ios_trusted':True,'precondition':'neutral'}])
        with redirect_stdout(io.StringIO()):self.assertEqual(C.tree_write_cli('writeback_walk',['--tree',str(fixture.tree),'--grounding',str(ground)],ROOT/'skills/arkts-visual-verify/scripts'),0)
        row=read_json(fixture.tree)['pages'][0]['functional_checks'][0]
        self.assertEqual(row['expected_ios'],'Seen');self.assertIs(row['ios_trusted'],True)
        self.assertNotIn('expected_android',row)
    def test_native_discovery_three_states_keep_complete_original_behavior(self):
        fixture=Fixture(self.root,names=('HomeView',));source,source_tree=trigger_source(self.root)
        tree=read_json(fixture.tree);tree['source']=source_tree['source'];write_json(fixture.tree,tree)
        parent=tree['pages'][0];directory=self.root/'spec/visual-verify/blackbox_discoveries'
        manifest_path=directory/'round-0/HomeView/HomeView__manifest.json'
        def discovery(text,identifier=''):
            value={'key':text,'trigger_text':text,'trigger_native_identifier':identifier,'trigger_resource_id':'',
                   'trigger_content_desc':text,'trigger_class':'XCUIElementTypeButton','trigger_center':[10,20],
                   'landing_ability':'DetailView','landing_signature':'detail fixture'}
            variant,_,_=C._native_variant(parent,value)
            value['capture_meta']=capture(self.root/'discovery-shots',variant['id'],trip=fixture.trip)
            value['capture_meta']['native_blackbox_source_inputs_sha256']=C._json_digest(C._blackbox_source_inputs(tree,self.root))
            value['screenshot']=value['capture_meta']['shot_path'];value['dump']=value['capture_meta']['dump_path']
            return value
        discoveries=[discovery('Open static'),discovery('Hello Sam','dynamic-control'),discovery('Unknown initially')]
        entries=[{'trigger_text':d['trigger_text'],'trigger_resource_id':'','native_identifier':d['trigger_native_identifier'],
                  'outcome':'page_change','landing_ability':d['landing_ability']} for d in discoveries]
        value={'parent_page_id':'HomeView','trip_id':fixture.trip,'discoveries':discoveries,'behavior_ledger':entries}
        write_json(manifest_path,value);scripts=ROOT/'skills/arkts-visual-verify/scripts'
        argv=['--factree',str(fixture.tree),'--discoveries-dir',str(directory)]
        with redirect_stdout(io.StringIO()),redirect_stderr(io.StringIO()):self.assertEqual(C.materialize_native_cli(argv,scripts),20)
        report=read_json(fixture.ew/'native_blackbox_materialization.json')
        self.assertEqual(report['summary']['classifications'],{'static':1,'dynamic':1,'unknown':1})
        result=read_json(fixture.tree);self.assertEqual(result['pages'][0]['blackbox_behavior'][fixture.trip],entries)
        first_result=copy.deepcopy(result)
        self.assertEqual([p['id'] for p in result['pages'] if p['type']=='PageVariant'],['DetailView#via=Open_static'])
        self.assertTrue((fixture.baseline/'DetailView#via=Open_static.ios.xml').is_file())
        self.assertIsNotNone(C._judgement_debt(fixture.ew))
        # Deleting the discovery list cannot erase an unresolved binding debt.
        empty=copy.deepcopy(value);empty['discoveries']=[];write_json(manifest_path,empty)
        with redirect_stdout(io.StringIO()),redirect_stderr(io.StringIO()):self.assertEqual(C.materialize_native_cli(argv,scripts),20)
        self.assertIsNotNone(C._judgement_debt(fixture.ew))
        write_json(fixture.tree,first_result);write_json(manifest_path,value)
        path=source/'Neutral.swift';path.write_text(path.read_text().replace('   helper()','   Text("Unknown initially")\n   helper()'))
        with self.assertRaisesRegex(MigrationError,'Native source changed'):C.materialize_native_cli(argv,scripts)
        # Actual source-fact regeneration and affected-baseline invalidation,
        # followed by fresh observations, is required for changed code.
        from hmigbot_ios152.native_routes import analyze
        from hmigbot_ios152.source import Source
        refreshed=read_json(fixture.tree);refreshed['source']['source_sha256']=analyze(Source(source))['source_sha']
        for page in refreshed['pages']:page.pop('screenshots',None)
        write_json(fixture.tree,refreshed);shutil.move(fixture.baseline,self.root/'archived-baseline')
        stable=C._json_digest(C._blackbox_source_inputs(refreshed,self.root))
        for d in discoveries:
            variant,_,_=C._native_variant(parent,d);d['capture_meta']=capture(self.root/'fresh-discovery-shots',variant['id'],trip=fixture.trip)
            d['capture_meta']['native_blackbox_source_inputs_sha256']=stable
            d['screenshot']=d['capture_meta']['shot_path'];d['dump']=d['capture_meta']['dump_path']
        write_json(manifest_path,value)
        with redirect_stdout(io.StringIO()),redirect_stderr(io.StringIO()):self.assertEqual(C.materialize_native_cli(argv,scripts),0)
        self.assertIsNone(C._judgement_debt(fixture.ew))
        final=read_json(fixture.tree);self.assertEqual(len([p for p in final['pages'] if p['type']=='PageVariant']),2)
        self.assertEqual(final['pages'][0]['blackbox_behavior'][fixture.trip],entries)
    def test_native_static_variant_without_arrived_pair_cannot_enter_baseline(self):
        fixture=Fixture(self.root,names=('HomeView',));_,source_tree=trigger_source(self.root)
        tree=read_json(fixture.tree);tree['source']=source_tree['source'];write_json(fixture.tree,tree)
        directory=self.root/'spec/visual-verify/blackbox_discoveries'
        value={'parent_page_id':'HomeView','trip_id':fixture.trip,'discoveries':[{'trigger_text':'Open static',
            'trigger_resource_id':'','landing_ability':'DetailView','screenshot':str(fixture.ew/'shots/HomeView.png')}],
            'behavior_ledger':[{'trigger_text':'Open static','outcome':'page_change'}]}
        write_json(directory/'HomeView__manifest.json',value)
        with redirect_stdout(io.StringIO()),redirect_stderr(io.StringIO()):self.assertEqual(C.materialize_native_cli([
            '--factree',str(fixture.tree),'--discoveries-dir',str(directory)],ROOT/'skills/arkts-visual-verify/scripts'),20)
        result=read_json(fixture.tree)
        self.assertEqual(result['pages'][-1]['id'],'DetailView#via=Open_static')
        self.assertFalse((fixture.baseline/'DetailView#via=Open_static.png').exists())
        self.assertIsNotNone(C._judgement_debt(fixture.ew))
    def test_native_variant_projection_matches_actual_original_fields_and_slug(self):
        scripts=ROOT/'skills/arkts-visual-verify/scripts'
        for index,label in enumerate(('Open static','  A !!! B ','!!!','X'*120,'中文（测试）','')):
            with self.subTest(label=label):
                case=self.root/str(index);android=case/'android/app/src/main';android.mkdir(parents=True)
                (android/'N.kt').write_text(label);tree=case/'tree.json';parent={'id':'HomeView'}
                write_json(tree,{'source':{'android_root':str(case/'android')},'pages':[parent]})
                discovery={'trigger_text':label,'trigger_resource_id':'control-id','trigger_content_desc':label,
                    'trigger_class':'XCUIElementTypeButton','trigger_center':[10,20],'landing_ability':'DetailView',
                    'landing_signature':'detail fixture','screenshot':None,'dump':None}
                directory=case/'dis';write_json(directory/'HomeView__manifest.json',{'parent_page_id':'HomeView',
                    'trip_id':'trip_2_logged_in_vip','discoveries':[discovery],'behavior_ledger':[]})
                process=C._core('materialize_blackbox_to_factree',['--factree',tree,'--discoveries-dir',directory],scripts)
                self.assertEqual(process.returncode,0,process.stdout+process.stderr)
                original=read_json(tree)['pages'][-1]
                native_input={**discovery,'trigger_resource_id':'','trigger_native_identifier':'control-id'}
                native,edge,extra=C._native_variant(parent,native_input)
                normalized=copy.deepcopy(native);normalized['android_file']=normalized.pop('ios_file')
                normalized['via_trigger']['resource_id']=normalized['via_trigger'].pop('native_identifier')
                action=normalized['navigation_contract']['trigger_actions'][0];action['resource_id']=action.pop('native_identifier')
                self.assertEqual(normalized,original)
                self.assertEqual(native['via_trigger']['resource_id'],'');self.assertEqual(edge['trigger_resource_id'],'')
    def test_original_compiler_keeps_multiscreen_tab_modal_and_behavior_gates(self):
        fixture=Fixture(self.root);fixture.place()
        out=self.root/'plan.json';annotations=self.root/'annotations.json'
        write_json(annotations,{'app':{'bundle':'org.hmigbot.neutral','ability':'EntryAbility'},'extra_blacklist':['Delete'],'state_signatures':{fixture.trip:['HomeView title']}})
        args=['--tree',str(fixture.tree),'--walk-plan',str(fixture.ew/'walk_plan.json'),
              '--baseline-dir',str(fixture.baseline),'--annotations',str(annotations),'--out',str(out)]
        with redirect_stdout(io.StringIO()):self.assertEqual(C.compile_replay_cli(args,ROOT/'skills/arkts-visual-verify/scripts'),0)
        plan=read_json(out)
        self.assertIn('LibraryView',plan['node_sentinels'])
        self.assertTrue(plan['node_sentinels']['LibraryView'])
        self.assertEqual(len(plan['functional_denominator']),1)
        self.assertEqual(plan['functional_not_planned'],[])
        self.assertNotIn('.ios"',json.dumps(plan['node_sentinels']))
        self.assertNotIn('hmigbot-ios-replay-',out.read_text())

    def target_fixture(self,*,native=False,trips=('trip_1_logged_out','trip_2_logged_in_vip'),pages=('HomeView','LibraryView','ConfirmSheet')):
        family='ios' if native else 'android';outs={};plans={}
        if native:
            fixture=Fixture(self.root,names=pages);fixture.place();tree=read_json(fixture.tree)
            for trip in trips:
                if trip==fixture.trip:continue
                base=self.root/f'spec/visual-verify/screenshots/ios'/trip;base.mkdir(parents=True)
                for index,page in enumerate(C.page_records(tree)):
                    meta=capture(fixture.ew/'prior_trip',page['id'],seed=index+30,trip=trip)
                    for key,suffix in [('shot_path','.png'),('dump_path','.ios.xml')]:
                        target=base/(page['id']+suffix);shutil.copy2(meta[key],target);meta[key]=str(target)
                    page.setdefault('screenshots',{})[trip]=meta
            write_json(fixture.tree,tree)
        for trip in trips:
            base=self.root/f'spec/visual-verify/screenshots/{family}'/trip;base.mkdir(parents=True,exist_ok=True)
            for index,page in enumerate(pages):
                if not (base/(page+'.png')).exists():png(base/(page+'.png'),120,240,index+2)
            capture_dir=self.root/'spec/visual-verify/replay'/trip
            (capture_dir/'shots').mkdir(parents=True);(capture_dir/'dumps').mkdir()
            for page in pages:
                image=capture_dir/f'shots/{page}.jpeg'
                subprocess.run(['/usr/bin/sips','-s','format','jpeg',str(base/(page+'.png')),'--out',str(image)],capture_output=True,check=True)
                write_json(capture_dir/f'dumps/{page}.hmos.json',{'attributes':{'type':'Root','bounds':'[0,0][120,240]'},
                    'children':[{'attributes':{'type':'Text','text':page+' title','bounds':'[10,30][100,50]'},'children':[]}]})
            manifest={'role':'capture','started_at':(datetime.now()-timedelta(minutes=1)).strftime('%Y-%m-%dT%H:%M:%S'),
                'finished_at':datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
                'pages_status':{page:{'status':'captured'} for page in pages},
                'per_page':{page:{'screenshot':str(capture_dir/f'shots/{page}.jpeg'),
                    'dump':str(capture_dir/f'dumps/{page}.hmos.json'),
                    'behavior_observations':[{'trigger_text':'Toggle favorite','rid':'favorite','outcome':'changed'}] if page=='LibraryView' else [],
                    'observation_notes':['Synthetic schema fixture, not target device verification']} for page in pages},
                'functional_coverage':{'gt_total':1,'effective_denominator':1,'observed':1,'gap_items':[]},
                'reconcile_unsettled':[]}
            write_json(capture_dir/'capture_manifest.json',manifest)
            plan_path=self.root/'spec/visual-verify/edgewalk'/('plan_'+trip+'.json')
            if native:
                annotations=self.root/'annotations.json';write_json(annotations,{'app':{'bundle':'org.hmigbot.neutral','ability':'EntryAbility'},'extra_blacklist':['Delete']})
                with redirect_stdout(io.StringIO()):self.assertEqual(C.compile_replay_cli(['--tree',str(fixture.tree),
                    '--walk-plan',str(fixture.ew/'walk_plan.json'),'--baseline-dir',str(base),
                    '--annotations',str(annotations),'--out',str(plan_path)],ROOT/'skills/arkts-visual-verify/scripts'),0)
                plan=read_json(plan_path);manifest['native_input_provenance']={
                    'source_platform':'ios','plan_path':str(plan_path),'plan_sha256':C.sha(plan_path),
                    'canonical_tree_sha256':plan['native_input_provenance']['canonical_tree_sha256'],
                    'baseline':plan['native_input_provenance']['baseline'],
                    'note':'SYNTHETIC CONTRACT FIXTURE; not an actual executor receipt'}
                write_json(capture_dir/'capture_manifest.json',manifest)
            else:
                write_json(plan_path,{'coverage_targets':list(pages),'functional_denominator':[{'node':'LibraryView','name':'Toggle favorite','rid':'favorite'}],
                    'functional_deferred':[],'same_screen_aliases':{},'steps':[]})
            process=C._core('replay_place_artifacts',['--capture-dir',str(capture_dir),'--round','1','--trip',trip,
                '--project-root',str(self.root),'--android-baseline-dir',str(base),'--no-resize'],ROOT/'skills/arkts-visual-verify/scripts')
            self.assertEqual(process.returncode,0,process.stdout+process.stderr)
            sbs=self.root/'spec/visual-verify/screenshots/sbs/round-1'/trip;sbs.mkdir(parents=True)
            for page in pages:shutil.copy2(capture_dir/f'shots/{page}.jpeg',sbs/(page+'.jpeg'))
            if native:
                placement=self.root/'spec/visual-verify/screenshots/harmony/round-1'/trip/'_placement.json'
                C._record_target_provenance('replay_place_artifacts',self.root,1,trip,capture_dir,placement)
                packet=capture_dir/'judge_input_round1.json';write_json(packet,{'role':'judge_input','notes':['Synthetic contract fixture']})
                C._record_target_provenance('build_judge_input',self.root,1,trip,capture_dir,packet)
            outs[trip]=str(capture_dir);plans[trip]=str(plan_path)
        return outs,plans

    def test_original_single_trip_alias_adapter_is_differentially_identical(self):
        outs,plans=self.target_fixture(trips=('trip_1_logged_out',))
        trip=next(iter(outs));scripts=ROOT/'skills/arkts-visual-verify/scripts'
        # The same original core runs first in a direct short-name harness,
        # then via the production alias adapter. Only path/trip labels differ.
        direct=self.root/'direct';direct.mkdir();root_alias=direct/'r';shutil.copytree(self.root/'spec',root_alias/'spec')
        baseline=root_alias/'spec/visual-verify/screenshots/android';(baseline/trip).rename(baseline/'t')
        for family in ('harmony','sbs'):
            base=root_alias/f'spec/visual-verify/screenshots/{family}/round-1';(base/trip).rename(base/'t')
        shutil.copytree(outs[trip],direct/'c');shutil.copy2(plans[trip],direct/'p')
        raw=C._core('assert_replay_artifacts',['xr1tcp'],scripts,cwd=direct)
        self.assertEqual(raw.returncode,0,raw.stdout+raw.stderr)
        out=io.StringIO()
        with redirect_stdout(out):code=C.target_gate_cli('assert_replay_artifacts',[str(self.root),'1',trip,outs[trip],plans[trip]],scripts)
        self.assertEqual(code,raw.returncode,out.getvalue())
        self.assertEqual(C._artifact_conditions(raw),[])
        self.assertIn('cond 4',out.getvalue())
        self.assertNotIn('hmigbot-ios-canonical-',out.getvalue())

    def test_original_cores_aggregate_two_trips_and_detect_functional_and_evidence_failures(self):
        outs,plans=self.target_fixture();scripts=ROOT/'skills/arkts-visual-verify/scripts'
        args=[str(self.root),'1']
        for trip in outs:args+=['--trip-out',trip+'='+outs[trip],'--plan',trip+'='+plans[trip]]
        with redirect_stdout(io.StringIO()):code=C.round_aggregate_cli(args,scripts)
        self.assertEqual(code,0)
        state=read_json(self.root/'spec/fix/round-1/_run_state.json')
        self.assertEqual(state['expected_trips'],sorted(outs));self.assertEqual(state['verdict'],'ALIGNMENT_CLEAN')
        self.assertTrue(all(row['android_denominator']==3 and row['delivered']==3 for row in state['trips'].values()))
        first=next(iter(outs));manifest=Path(outs[first])/'capture_manifest.json';value=read_json(manifest)
        value['functional_coverage']['observed']=0;value['functional_coverage']['gap_items']=[{'node':'LibraryView','name':'Toggle favorite'}];write_json(manifest,value)
        with redirect_stdout(io.StringIO()):self.assertEqual(C.round_aggregate_cli(args,scripts),20)
        bad=read_json(self.root/'spec/fix/round-1/_run_state.json');self.assertNotEqual(bad['verdict'],'ALIGNMENT_CLEAN')
        self.assertIn('4',bad['trips'][first]['artifact_failed_conditions'])
        # No trip-out means no execution, even with leftover canonical images.
        with redirect_stdout(io.StringIO()):self.assertEqual(C.round_aggregate_cli([str(self.root),'1'],scripts),20)

    def test_original_evidence_bypass_is_first_failure_and_preserves_other_findings(self):
        outs,plans=self.target_fixture(trips=('trip_1_logged_out',));trip=next(iter(outs));scripts=ROOT/'skills/arkts-visual-verify/scripts'
        canonical=self.root/'spec/visual-verify/screenshots/harmony/round-1'/trip
        for file in canonical.glob('*.jpeg'):file.unlink()
        round_dir=self.root/'spec/fix/round-1';round_dir.mkdir(parents=True)
        old_ns=time.time_ns()-120_000_000_000;os.utime(round_dir,ns=(old_ns,old_ns))
        adhoc=self.root/'spec/visual-verify/screenshots/adhoc';adhoc.mkdir(parents=True)
        for i in range(4):(adhoc/('probe_'+str(i)+'.jpeg')).write_bytes(b'synthetic evidence bypass counterfactual')
        with redirect_stdout(io.StringIO()):code=C.round_aggregate_cli([str(self.root),'1',
            '--trip-out',trip+'='+outs[trip],'--plan',trip+'='+plans[trip]],scripts)
        self.assertEqual(code,30)
        state=read_json(self.root/'spec/fix/round-1/_run_state.json')
        self.assertEqual(state['verdict'],'EVIDENCE_BYPASSED')
        self.assertTrue(any(f['gate']=='replay_artifacts' for f in state['findings']))

    def test_standalone_evidence_preserves_existing_round_window_and_state_on_two_runs(self):
        outs,plans=self.target_fixture(trips=('trip_1_logged_out',));trip=next(iter(outs));scripts=ROOT/'skills/arkts-visual-verify/scripts'
        for file in (self.root/'spec/visual-verify/screenshots/harmony/round-1'/trip).glob('*.jpeg'):file.unlink()
        rd=self.root/'spec/fix/round-1';rd.mkdir(parents=True);state=rd/'_run_state.json'
        write_json(state,{'round':1,'probe':'existing round state must remain byte-identical'})
        adhoc=self.root/'spec/visual-verify/screenshots/adhoc';adhoc.mkdir(parents=True);image=adhoc/'within_round.jpeg';image.write_bytes(b'fixture')
        now=time.time_ns();os.utime(state,ns=(now-10_000_000_000,)*2);os.utime(image,ns=(now-30_000_000_000,)*2)
        os.utime(rd,ns=(now-120_000_000_000,)*2)
        before=(C.sha(state),state.stat().st_mtime_ns,rd.stat().st_mtime_ns)
        for _ in range(2):
            with redirect_stdout(io.StringIO()),redirect_stderr(io.StringIO()):
                self.assertEqual(C.target_gate_cli('assert_evidence_channel',[str(self.root),'1'],scripts),30)
            self.assertEqual((C.sha(state),state.stat().st_mtime_ns,rd.stat().st_mtime_ns),before)
        # The original existing-state mtime also closes the round. Preserve its
        # observed exclusion of post-close adhoc rather than inventing a rule.
        os.utime(image,ns=(now,now))
        with redirect_stdout(io.StringIO()),redirect_stderr(io.StringIO()):
            self.assertEqual(C.target_gate_cli('assert_evidence_channel',[str(self.root),'1'],scripts),0)
        self.assertEqual((C.sha(state),state.stat().st_mtime_ns,rd.stat().st_mtime_ns),before)

    def test_existing_state_artifact_and_gap_adapters_match_pure_original_checks(self):
        outs,plans=self.target_fixture(trips=('trip_1_logged_out',));trip=next(iter(outs));scripts=ROOT/'skills/arkts-visual-verify/scripts'
        rd=self.root/'spec/fix/round-1';rd.mkdir(parents=True);state=rd/'_run_state.json'
        write_json(state,{'round':1,'probe':'pure per-trip gates do not publish a round state'})
        old=time.time_ns()-120_000_000_000;os.utime(state,ns=(old,old));os.utime(rd,ns=(old-1,old-1))
        before=(C.sha(state),state.stat().st_mtime_ns,rd.stat().st_mtime_ns)
        for command in ('assert_replay_artifacts','assert_gap_ticket_coverage'):
            with C.ProjectMirror(self.root,round_number=1,short_trips=True,source_family='android') as mirror:
                arg='x'+mirror.root_alias+'1'+mirror.trip_alias[trip]+mirror.add_capture(outs[trip])
                if command=='assert_replay_artifacts':arg+=mirror.add_plan(plans[trip])
                raw=C._core(command,[arg],scripts,cwd=mirror.work)
                expected=mirror.normalize(raw.stdout+raw.stderr)
                self.assertEqual(raw.returncode,0,expected)
            args=[str(self.root),'1',trip,outs[trip]]+([plans[trip]] if command=='assert_replay_artifacts' else [])
            for _ in range(2):
                output=io.StringIO()
                with redirect_stdout(output),redirect_stderr(output):code=C.target_gate_cli(command,args,scripts)
                self.assertEqual(code,raw.returncode);self.assertEqual(output.getvalue(),expected)
                self.assertEqual((C.sha(state),state.stat().st_mtime_ns,rd.stat().st_mtime_ns),before)

    def test_old_variant_collection_rejection_uses_stale22_without_crediting_settle(self):
        fixture,source,manifest,data,args=self.native_blackbox_fixture();tree=read_json(fixture.tree)
        variant=next(p['id'] for p in tree['pages'] if p.get('type')=='PageVariant')
        plan=read_json(fixture.ew/'walk_plan.json');plan['targets'].append(variant);write_json(fixture.ew/'walk_plan.json',plan)
        data['behavior_ledger'].append({'trigger_text':'new observation','outcome':'noop'});write_json(manifest,data)
        inputs=C._source_current(tree,self.root,allow_manifest_collection=True)
        before=C.sha(fixture.ew/'ledger.json')
        def observer_capture(argv):
            meta=capture(Path(C._option(argv,'--shots-dir')),variant,trip=fixture.trip);meta.update(inputs)
            print(json.dumps(meta));return 0
        command=['--dir',str(fixture.ew),'settle','--node',variant,'--via','actual raw fixture arrival',
            '--tree',str(fixture.tree),'--trip',fixture.trip,'--pkg','org.hmigbot.neutral','--launcher','HomeView','--project-root',str(self.root)]
        output=io.StringIO()
        with patch('hmigbot_ios152.native_visual.capture_cli',side_effect=observer_capture),redirect_stdout(output):
            self.assertEqual(D.native_settle(command,ROOT/'skills/arkts-visual-verify/scripts'),22)
        self.assertEqual(json.loads(output.getvalue())['status'],'stale_classification')
        self.assertEqual(C.sha(fixture.ew/'ledger.json'),before)

    def test_original_budget_keeps_default_three_rounds_and_requires_round_ledger(self):
        scripts=ROOT/'skills/arkts-visual-verify/scripts';state=self.root/'spec/fix/_state.yaml';state.parent.mkdir(parents=True)
        def run(action):return C._core('round_budget',[action,'--state',state],scripts,cwd=self.root)
        self.assertEqual(run('begin').returncode,0)
        self.assertEqual(run('next').returncode,2)  # Original missing aggregate ledger gate.
        for n in range(3):
            write_json(self.root/f'spec/fix/round-{n}/_run_state.json',{'round':n,'expected_trips':['t'],
                'trips':{'t':{'android_denominator':1,'delivered':1,'replay_assert_exit':0,'gap_ticket_exit':0}},
                'verdict':'ALIGNMENT_CLEAN','evidence_channel_exit':0,'open_findings':0,'product_findings':0,'exit_code':0})
            result=run('next');self.assertEqual(result.returncode,0 if n<2 else 10,result.stdout+result.stderr)
        self.assertIn('BUDGET_EXHAUSTED',result.stdout+result.stderr)

    def test_missing_pair_and_unticketed_gap_stay_red_in_original_cores(self):
        outs,plans=self.target_fixture(trips=('trip_1_logged_out',));trip=next(iter(outs));scripts=ROOT/'skills/arkts-visual-verify/scripts'
        base=self.root/'spec/visual-verify/screenshots/harmony/round-1'/trip
        (base/'ConfirmSheet.jpeg').unlink()
        with redirect_stdout(io.StringIO()),redirect_stderr(io.StringIO()):
            self.assertEqual(C.target_gate_cli('assert_gap_ticket_coverage',[str(self.root),'1',trip,outs[trip]],scripts),21)
        (base/'LibraryView.hmos.json').unlink()
        with redirect_stdout(io.StringIO()),redirect_stderr(io.StringIO()):
            self.assertNotEqual(C.target_gate_cli('assert_replay_artifacts',[str(self.root),'1',trip,outs[trip],plans[trip]],scripts),0)

    def test_ios_double_trip_hash_bindings_and_stale_sbs_counterfactual(self):
        outs,plans=self.target_fixture(native=True);scripts=ROOT/'skills/arkts-visual-verify/scripts'
        args=[str(self.root),'1']
        for trip in outs:args+=['--trip-out',trip+'='+outs[trip],'--plan',trip+'='+plans[trip]]
        with redirect_stdout(io.StringIO()):code=C.round_aggregate_cli(args,scripts)
        self.assertEqual(code,0)
        state=read_json(self.root/'spec/fix/round-1/_run_state.json')
        self.assertEqual(state['native_input_provenance']['source_family'],'ios')
        first=next(iter(outs));sbs=self.root/'spec/visual-verify/screenshots/sbs/round-1'/first/'HomeView.jpeg'
        sbs.write_bytes(b'stale replacement')
        with redirect_stdout(io.StringIO()):self.assertEqual(C.round_aggregate_cli(args,scripts),22)
        stale=read_json(self.root/'spec/fix/round-1/_run_state.json')
        self.assertEqual(stale['verdict'],'STALE_ARTIFACTS')

    def test_nonempty_inheritance_and_behavior_ledger_reach_true_ios_tree(self):
        fixture=Fixture(self.root,names=('HomeView','LibraryView'));tree=read_json(fixture.tree)
        _,source_tree=trigger_source(self.root);tree['source']=source_tree['source']
        tree['pages'][0]['functional_checks']=[{'name':'Open library','expected_ios':None,'ios_trusted':None}]
        write_json(fixture.tree,tree)
        write_json(fixture.ew/'grounding/HomeView/run_meta.json',{'node':'HomeView','checks':[
            {'idx':0,'name':'Open library','status':'deferred_same_destination','anchor_rid':'open_library',
             'inherit_from_edge':{'from':'HomeView','to':'LibraryView','trigger':'Open library'}}]})
        write_json(fixture.ew/'grounding_results.json',[])
        write_json(fixture.ew/'edge_results.json',[{'from':'HomeView','to':'LibraryView','status':'confirmed',
            'device_state':fixture.trip,'control':{'rid':'','text':'Open library'},'landed':'LibraryView',
            'back_returns_to_parent':True,'evidence':'Synthetic contract fixture, not device observation'}])
        scripts=ROOT/'skills/arkts-visual-verify/scripts'
        with redirect_stdout(io.StringIO()):self.assertEqual(C.inherit_cli(['--dir',str(fixture.ew),'--device-state',fixture.trip],scripts),0)
        ground=read_json(fixture.ew/'grounding_results.json')
        self.assertEqual(len(ground),1);self.assertIs(ground[0]['ios_trusted'],True)
        self.assertIn('LibraryView',ground[0]['expected_ios']);self.assertNotIn('expected_android',ground[0])
        with redirect_stdout(io.StringIO()):self.assertEqual(C.tree_write_cli('writeback_walk',['--tree',str(fixture.tree),
            '--grounding',str(fixture.ew/'grounding_results.json'),'--edges',str(fixture.ew/'edge_results.json')],scripts),0)
        path=self.root/'spec/visual-verify/blackbox_discoveries/round-0/HomeView/HomeView__manifest.json'
        entries=[{'trigger_text':'Unclaimed button','trigger_resource_id':'','native_identifier':'unclaimed',
                  'outcome':'noop','note':'Synthetic native observation ledger fixture'}]
        write_json(path,{'parent_page_id':'HomeView','trip_id':fixture.trip,'discoveries':[],'behavior_ledger':entries})
        with redirect_stdout(io.StringIO()),redirect_stderr(io.StringIO()):self.assertEqual(C.tree_write_cli('materialize_blackbox_to_factree',[
            '--factree',str(fixture.tree),'--discoveries-dir',str(path.parents[2])],scripts),0)
        tree=read_json(fixture.tree)
        self.assertEqual(tree['pages'][0]['blackbox_behavior'][fixture.trip],entries)
        self.assertIs(tree['pages'][0]['functional_checks'][0]['ios_trusted'],True)
        self.assertEqual(len(tree['pages'][1]['inbound_triggers']),1)

    def test_full_finalize_keeps_nonempty_ledgers_and_original_source_gates(self):
        fixture=Fixture(self.root,names=('HomeView','LibraryView'));tree=read_json(fixture.tree)
        _,source_tree=trigger_source(self.root);tree['source']=source_tree['source']
        tree['pages'][0]['functional_checks']=[{'name':'Open library','expected_ios':None,'ios_trusted':None}]
        # First-trip baseline is a separate paired fixture, already frozen.
        first='trip_1_logged_out';base=self.root/'spec/visual-verify/screenshots/ios'/first;base.mkdir(parents=True)
        for index,page in enumerate(tree['pages']):
            meta=capture(fixture.ew/'prior_trip',page['id'],seed=index+40,trip=first)
            for key,suffix in [('shot_path','.png'),('dump_path','.ios.xml')]:
                target=base/(page['id']+suffix);shutil.copy2(meta[key],target);meta[key]=str(target)
            page.setdefault('screenshots',{})[first]=meta
        write_json(fixture.tree,tree)
        write_json(fixture.ew/'grounding/HomeView/run_meta.json',{'node':'HomeView','checks':[
            {'idx':0,'name':'Open library','status':'deferred_same_destination',
             'inherit_from_edge':{'from':'HomeView','to':'LibraryView','trigger':'Open library'}}]})
        write_json(fixture.ew/'grounding_results.json',[])
        write_json(fixture.ew/'edge_results.json',[{'from':'HomeView','to':'LibraryView','status':'confirmed',
            'device_state':fixture.trip,'control':{'rid':'','text':'Open library'},'landed':'LibraryView',
            'back_returns_to_parent':True,'evidence':'Synthetic source ledger fixture'}])
        for page in fixture.names:
            path=self.root/'spec/visual-verify/blackbox_discoveries/round-0'/page/(page+'__manifest.json')
            write_json(path,{'parent_page_id':page,'trip_id':fixture.trip,'parent_signature':'synthetic-'+page,
                'bucket_total':1,'probe_valid':True,'discoveries':[],
                'behavior_ledger':[{'trigger_text':'Observed '+page,'trigger_resource_id':'','outcome':'noop',
                                    'note':'Synthetic contract fixture, not a device result'}]})
        stdout=io.StringIO();stderr=io.StringIO()
        with redirect_stdout(stdout),redirect_stderr(stderr):
            code=C.finalize_cli(['--tree',str(fixture.tree),'--dir',str(fixture.ew),
                '--project-root',str(self.root),'--trip',fixture.trip,'--walk-id','neutral_full_finalize'],ROOT/'skills/arkts-visual-verify/scripts')
        self.assertEqual(code,0,stdout.getvalue()+stderr.getvalue())
        result=read_json(fixture.tree)
        self.assertIs(result['pages'][0]['functional_checks'][0]['ios_trusted'],True)
        self.assertTrue(result['pages'][0]['blackbox_behavior'][fixture.trip])
        self.assertEqual(len(result['pages'][1]['inbound_triggers']),1)
        self.assertEqual(set(p.name for p in fixture.baseline.iterdir()),
                         {page+suffix for page in fixture.names for suffix in ['.png','.ios.xml']})

    def test_append_discovery_then_ordinary_raw_settle_then_one_finalize_does_not_self_lock(self):
        original=C.finalize_cli;events=[]
        def collect_then_finalize(argv,scripts):
            tree_path=Path(C._option(argv,'--tree'));ew=Path(C._option(argv,'--dir'));trip=C._option(argv,'--trip')
            directory=self.root/'spec/visual-verify/blackbox_discoveries'
            with redirect_stdout(io.StringIO()),redirect_stderr(io.StringIO()):self.assertEqual(C.materialize_native_cli([
                '--factree',str(tree_path),'--discoveries-dir',str(directory)],scripts),0)
            tree=read_json(tree_path);file=directory/'round-0/HomeView/HomeView__manifest.json';data=read_json(file)
            meta=capture(self.root/'new-discovery','DetailView#via=Hello_Sam',trip=trip)
            stable=C._source_current(tree,self.root,allow_manifest_collection=True)['native_blackbox_source_inputs_sha256']
            meta['native_blackbox_source_inputs_sha256']=stable
            data['discoveries'].append({'key':'new-dynamic','trigger_text':'Hello Sam','trigger_native_identifier':'dynamic-control',
                'trigger_resource_id':'','landing_ability':'DetailView','capture_meta':meta,
                'screenshot':meta['shot_path'],'dump':meta['dump_path']})
            data['behavior_ledger'].append({'trigger_text':'Hello Sam','trigger_resource_id':'','outcome':'page_change'})
            write_json(file,data)
            state=C._source_current(tree,self.root,allow_manifest_collection=True)
            self.assertEqual(state['native_classification_status'],'pending_rematerialization')
            events.append('new discovery collected; normal navigation remains raw')
            def observer_capture(args):
                page=C._option(args,'--page');result=capture(Path(C._option(args,'--shots-dir')),page,trip=trip)
                result.update(state);print(json.dumps(result));return 0
            command=['--dir',str(ew),'settle','--node','LibraryView','--via','HomeView --[Open library]--> LibraryView',
                '--tree',str(tree_path),'--trip',trip,'--pkg','org.hmigbot.neutral','--launcher','HomeView','--project-root',str(self.root)]
            with patch('hmigbot_ios152.native_visual.capture_cli',side_effect=observer_capture),redirect_stdout(io.StringIO()):
                self.assertEqual(D.native_settle(command,scripts),0)
            row=read_json(ew/'ledger.json')['settled']['LibraryView']
            self.assertEqual(row['capture'],'verified');self.assertEqual(row['native_classification_status'],'pending_rematerialization')
            self.assertFalse(row['coverage_credited']);self.assertFalse((self.root/'spec/visual-verify/screenshots/ios'/trip/'LibraryView.png').exists())
            events.append('ordinary page arrived/capture paired; no canonical baseline yet')
            code=original(argv,scripts);self.assertEqual(code,0)
            C._source_current(read_json(tree_path),self.root)
            events.append('one original-order finalize materialized then placed and passed original readiness cores')
            return code
        with patch.object(C,'finalize_cli',side_effect=collect_then_finalize):self.test_full_finalize_keeps_nonempty_ledgers_and_original_source_gates()
        self.assertEqual(len(events),3)


if __name__=='__main__':unittest.main()
