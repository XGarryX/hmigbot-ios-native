"""Archived-trip protocol fixtures; synthetic files are not device evidence."""
import copy
import io
import json
import os
from pathlib import Path
import plistlib
import shutil
import sys
import tempfile
import types
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from hmigbot_ios.core import MigrationError, read_json, write_json
from hmigbot_ios152 import native_canonical as C
from hmigbot_ios152.native_source_build import app_build_identity
from hmigbot_ios152.native_visual import identities_from_tree, arrival
from evaluations.test_native_canonical import Fixture, capture


class ArchivedTrip46(unittest.TestCase):
    def setUp(self):
        temporary=tempfile.TemporaryDirectory(prefix='native-archive46-test-');self.addCleanup(temporary.cleanup)
        self.root=Path(temporary.name).resolve();self.f=Fixture(self.root,names=('HomeView',));self.trip='trip_1_logged_out'
        plan=read_json(self.f.ew/'walk_plan.json');first=copy.deepcopy(plan['walks'][0])
        first.update(walk_id='synthetic_first',trip_id=self.trip);plan['walks'].append(first);write_json(self.f.ew/'walk_plan.json',plan)
        # Deliberately synthetic build-record protocol, not a claimed Xcode build.
        self.app=self.root/'SYNTHETIC.app';self.app.mkdir()
        (self.app/'Info.plist').write_bytes(plistlib.dumps({'CFBundleIdentifier':'org.hmigbot.neutral','CFBundleExecutable':'SYNTHETIC'}))
        (self.app/'SYNTHETIC').write_bytes(b'SYNTHETIC protocol bytes, not a Mach-O app')
        self.build={'app':str(self.app),'exit_code':0,'app_binary_sha256':C.sha(self.app/'SYNTHETIC'),
                    'source_sha256':'SYNTHETIC-CONTEXT','simulator_entitlements':{'validation':'passed'},'signing_mode':'SYNTHETIC'}
        write_json(self.root/'build.json',self.build)
        tree=read_json(self.f.tree);tree['native_context']={'source_sha256':'SYNTHETIC-CONTEXT'}
        tree['pages'][0]['native_identity']={'required':[{'label':'HomeView title','element_type':48}]}
        write_json(self.f.tree,tree)
        meta=capture(self.f.ew/'shots/_bytrip'/self.trip,'HomeView',trip=self.trip)
        meta['source_app_build']=app_build_identity(self.app)
        obs=read_json(Path(meta['native_json']));selector=tree['pages'][0]['native_identity']['required'][0]
        query={'required':[{'selector':selector,'visible_unique':True,'response':{'ok':True,'session':obs['session']}}],'excluded':[]}
        meta['arrival']=arrival(obs,'HomeView',identities_from_tree(tree),{'HomeView':query})
        self.history={'via':'SYNTHETIC archived-trip fixture','trip':self.trip,'capture':'verified','capture_meta':meta}
        ledger=read_json(self.f.ew/'ledger.json');ledger['settled_by_trip']={self.trip:{'HomeView':self.history}}
        write_json(self.f.ew/'ledger.json',ledger)
    def ledger(self):return read_json(self.f.ew/'ledger.json')
    def save(self,value):write_json(self.f.ew/'ledger.json',value)
    def place(self):return C.place_baselines(self.f.tree,self.f.ew,self.root,self.trip,source_app=self.app)
    def test_archived_capture_places_its_own_trip_and_reports_source(self):
        result=self.place();self.assertEqual(['HomeView'],result['placed'])
        self.assertEqual({'HomeView':'settled_by_trip'},result['placement_sources'])
        self.assertEqual(self.history['capture_meta']['raw_sha256']['png'],
                         C.sha(self.root/'spec/visual-verify/screenshots/ios'/self.trip/'HomeView.png'))
    def test_matching_global_has_priority_over_conflicting_history(self):
        ledger=self.ledger();ledger['settled_by_trip'][self.f.trip]={'HomeView':{'trip':'wrong'}};self.save(ledger)
        result=C.place_baselines(self.f.tree,self.f.ew,self.root,self.f.trip)
        self.assertEqual(['HomeView'],result['placed']);self.assertNotIn('placement_sources',result)
    def test_missing_history_preserves_skip_and_unreached(self):
        ledger=self.ledger();ledger.pop('settled_by_trip');self.save(ledger)
        result=self.place();self.assertEqual(['HomeView'],result['skipped_other_trip']);self.assertEqual([],result['placed'])
        ledger['settled']={};self.save(ledger);result=self.place();self.assertEqual(['HomeView'],result['unreached'])
    def test_history_also_works_when_global_row_missing(self):
        ledger=self.ledger();ledger['settled']={};self.save(ledger)
        self.assertEqual(['HomeView'],self.place()['placed'])
    def test_conflicting_trip_is_not_relabelled(self):
        ledger=self.ledger();ledger['settled_by_trip'][self.trip]['HomeView']['capture_meta']['trip']=self.f.trip;self.save(ledger)
        with self.assertRaisesRegex(MigrationError,'trip conflicts'):self.place()
    def test_archive_copy_must_equal_immutable_raw_even_if_copy_hash_updated(self):
        ledger=self.ledger();meta=ledger['settled_by_trip'][self.trip]['HomeView']['capture_meta']
        png=Path(meta['shot_path']);png.write_bytes(png.read_bytes()+b'SYNTHETIC altered archive')
        meta['sha256']['png']=C.sha(png);self.save(ledger)
        with self.assertRaisesRegex(MigrationError,'immutable raw png'):self.place()
    def test_different_source_context_cannot_reuse_history(self):
        tree=read_json(self.f.tree);tree['native_context']['source_sha256']='CHANGED-SYNTHETIC-CONTEXT';write_json(self.f.tree,tree)
        with self.assertRaisesRegex(MigrationError,'Source/build differs'):self.place()
    def test_changed_current_build_cannot_reuse_history(self):
        (self.app/'SYNTHETIC').write_bytes(b'SYNTHETIC changed product')
        self.build['app_binary_sha256']=C.sha(self.app/'SYNTHETIC');write_json(self.root/'build.json',self.build)
        with self.assertRaisesRegex(MigrationError,'Source/build differs'):self.place()
    def test_changed_page_selectors_do_not_reuse_old_live_query(self):
        tree=read_json(self.f.tree);tree['pages'][0]['native_identity']['required'][0]['label']='Different title';write_json(self.f.tree,tree)
        with self.assertRaisesRegex(MigrationError,'identity selectors changed'):self.place()
    def test_current_source_app_is_required_for_history(self):
        with self.assertRaisesRegex(MigrationError,'needs --source-app'):
            C.place_baselines(self.f.tree,self.f.ew,self.root,self.trip)
    def test_original_trip_assignment_still_excludes_history(self):
        write_json(self.root/'spec/visual-verify/_trip_assignment.json',{'pages':{'HomeView':{'trips':[self.f.trip]}}})
        result=self.place();self.assertEqual([],result['placed']);self.assertEqual(['HomeView'],result['skipped_other_trip'])
    @unittest.skipUnless(os.environ.get('HMIGBOT_TEST_PREVIOUS_CANONICAL'),'frozen previous implementation required')
    def test_default_global_output_matches_frozen45_exactly(self):
        path=Path(os.environ['HMIGBOT_TEST_PREVIOUS_CANONICAL']);old=types.ModuleType('hmigbot_ios152._archive46_old45')
        old.__package__='hmigbot_ios152';old.__file__=str(path);sys.modules[old.__name__]=old
        self.addCleanup(sys.modules.pop,old.__name__,None);exec(compile(path.read_text(),str(path),'exec'),old.__dict__)
        before=self.f.tree.read_bytes();result45=old.place_baselines(self.f.tree,self.f.ew,self.root,self.f.trip)
        tree45=self.f.tree.read_bytes();images45={p.name:C.sha(p) for p in self.f.baseline.iterdir()}
        shutil.rmtree(self.f.baseline);self.f.tree.write_bytes(before)
        result46=C.place_baselines(self.f.tree,self.f.ew,self.root,self.f.trip)
        self.assertEqual(result45,result46);self.assertEqual(tree45,self.f.tree.read_bytes())
        self.assertEqual(images45,{p.name:C.sha(p) for p in self.f.baseline.iterdir()})
    def test_finalize_step5_accepts_history_placement_result(self):
        calls=[]
        def consume(name,args,*a,**kw):
            calls.append(name)
            self.assertTrue((self.root/'spec/visual-verify/screenshots/ios'/self.trip/'HomeView.png').is_file())
            return 0
        # Orchestration only: original core commands are represented explicitly;
        # real original gates and a real project are exercised separately.
        args=['--trip',self.trip,'--tree',str(self.f.tree),'--dir',str(self.f.ew),
              '--project-root',str(self.root),'--walk-id','synthetic_history','--source-app',str(self.app)]
        with patch.object(C,'inherit_cli',return_value=0),patch.object(C,'tree_write_cli',return_value=0),\
             patch.object(C,'data_cli',side_effect=consume),redirect_stdout(io.StringIO()) as output:
            result=C.finalize_cli(args,ROOT/'skills/arkts-visual-verify/scripts')
        self.assertEqual(0,result);self.assertIn('placement_sources',output.getvalue())
        self.assertEqual(['phase2_needs','check_android_screenshot','check_blackbox_evidence'],calls)


if __name__=='__main__':unittest.main()
