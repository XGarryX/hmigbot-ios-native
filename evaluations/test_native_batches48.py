"""Actual original v4 schema plus neutral overlay cases; no device evidence."""
import contextlib
import copy
import io
import os
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

from evaluations import test_native_batches47 as B47
from evaluations.test_native_batches47 import SCRIPTS,batch_args
from hmigbot_ios.core import read_json,write_json
from hmigbot_ios152 import native_file_mapping as M
from hmigbot_ios152 import native_canonical as C


def entry(name,state):
    value={'name':name}
    if state=='resolved':value['file_resolved']='entry/pages/'+name+'.ets'
    if state=='via_parent':value.update(parent_file_resolved='entry/pages/Host.ets',parent_used='Host')
    if state=='ambiguous':value['file_candidates']=['entry/a/Index.ets','entry/b/Index.ets']
    return value


class V4Overlay48(unittest.TestCase):
    def setUp(self):
        temp=tempfile.TemporaryDirectory(prefix='native-batches48-test-');self.addCleanup(temp.cleanup)
        self.root=Path(temp.name).resolve();self.tree=self.root/'spec/tree.json';write_json(self.tree,{'synthetic':True})
        self.output=self.root/'spec/batches.json'
        self.queue={'entries':[entry(n,s) for n,s in [('Home','resolved'),('Inline','via_parent'),('Ambig','ambiguous'),('Missing','unfound'),('Existing','resolved')]]}
    def run_overlay(self,value,queue=None):
        def produce(*a,**kw):write_json(self.output,value);return 0
        with patch.object(C,'data_cli',side_effect=produce),patch.object(M,'mapped_queue',return_value=(queue or self.queue,{})),contextlib.redirect_stdout(io.StringIO()):
            return M.batches_cli(['--fact-tree',str(self.tree),'--out',str(self.output)],SCRIPTS)
    def v4(self,pages):
        return {'schema_version':'v4-batches/1','stats':{'total_records':len(pages)},'trips':[
            {'trip_id':'first','scenario_chain':[],'batches':[{'batch_id':'first-1','pages':pages}]}]}
    def test_v4_preserves_all_original_fields_and_repeated_trip_identities(self):
        value=self.v4([{'page_id':n,'android_file':'Source/'+n+'.swift','edges_to_test':[{'keep':True}]} for n in ['Home','Inline','Ambig','Missing','Existing','Unknown']])
        value['trips'][0]['batches'][0]['pages'][4]['file_resolved']='native/Keep.ets'
        value['trips'].append({'trip_id':'second','scenario_chain':['original-state'],'batches':[{'batch_id':'second-1','pages':[copy.deepcopy(value['trips'][0]['batches'][0]['pages'][0])]}]})
        self.assertEqual(0,self.run_overlay(value));after=read_json(self.output)
        rows=list(M.batch_rows(after));self.assertEqual('entry/pages/Home.ets',rows[0][1]['file_resolved'])
        self.assertEqual('entry/pages/Host.ets',rows[1][1]['parent_file_resolved'])
        self.assertNotIn('file_resolved',rows[2][1]);self.assertEqual(2,len(rows[2][1]['file_candidates']))
        self.assertNotIn('file_resolved',rows[3][1]);self.assertEqual('native/Keep.ets',rows[4][1]['file_resolved'])
        self.assertEqual(rows[0][1]['file_resolved'],rows[-1][1]['file_resolved'])
        for (_,old),(_,new) in zip(M.batch_rows(value),M.batch_rows(after),strict=True):
            for field in M.LOCATORS:
                if field in old:new[field]=old[field]
                else:new.pop(field,None)
        self.assertEqual(value,after)
        receipt=read_json(self.output.with_name(self.output.name+'.native-mapping.json'))
        self.assertEqual(['Unknown'],receipt['batch_rows_by_trip']['first']['unmatched'])
        self.assertEqual(1,receipt['batch_rows_by_trip']['second']['matched'])
    def test_known_unfound_subset_is_not_blocked_by_other_resolved_queue_entries(self):
        value=self.v4([{'page_id':'Missing','android_file':None}])
        self.assertEqual(0,self.run_overlay(value));self.assertEqual(value,read_json(self.output))
    def test_no_identity_matches_is_reported_instead_of_silent_success(self):
        with self.assertRaisesRegex(C.MigrationError,'no queue identity matches'):
            self.run_overlay(self.v4([{'page_id':'Wrong'}]))
    def test_conflicting_name_and_page_id_are_rejected(self):
        with self.assertRaisesRegex(C.MigrationError,'Conflicting'):
            self.run_overlay(self.v4([{'page_id':'Home','name':'Other'}]))
    def test_unknown_mixed_and_malformed_layouts_are_rejected(self):
        values=[{}, {'trips':[]}, {'schema_version':'other','trips':[]},
            {'schema_version':'v4-batches/1','trips':[],'batches':[]},
            {'schema_version':'v4-batches/1','trips':[{'trip_id':'first','batches':{}}]}]
        for value in values:
            with self.subTest(value=value),self.assertRaises(C.MigrationError):self.run_overlay(value)
    def test_empty_valid_v4_remains_a_valid_noop(self):
        value={'schema_version':'v4-batches/1','stats':{'total_records':0},'trips':[]}
        self.assertEqual(0,self.run_overlay(value));self.assertEqual(value,read_json(self.output))


@unittest.skipUnless(os.environ.get('HMIGBOT_TEST_ORIGINAL_VISUAL_ENGINE'),'isolated original core required')
class ActualOriginalV4_48(unittest.TestCase):
    setUp=B47.NestedOriginal47.setUp
    def test_actual_original_v4_output_receives_overlay_without_other_changes(self):
        original_data=C.data_cli;before={}
        def produced(command,argv,scripts):
            code=original_data(command,argv,scripts)
            if not code:before.update(read_json(self.root/'batches.json'))
            return code
        queue={'entries':[entry(n,'resolved' if n=='HomeView' else 'via_parent' if n=='LibraryView' else 'ambiguous' if n=='DetailView' else 'unfound') for n in self.f.names]}
        with patch.object(C,'data_cli',side_effect=produced),patch.object(M,'mapped_queue',return_value=(queue,{})),contextlib.redirect_stdout(io.StringIO()),contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(0,M.batches_cli(batch_args(self.f),SCRIPTS))
        self.assertEqual('v4-batches/1',before['schema_version']);after=read_json(self.root/'batches.json')
        self.assertTrue(any(r.get('file_resolved')=='entry/pages/HomeView.ets' for _,r in M.batch_rows(after)))
        for (_,old),(_,new) in zip(M.batch_rows(before),M.batch_rows(after),strict=True):
            for field in M.LOCATORS:
                if field in old:new[field]=old[field]
                else:new.pop(field,None)
        self.assertEqual(before,after)
    def test_original_ui_failure_never_runs_overlay(self):
        shutil.rmtree(self.root/'spec/visual-verify/screenshots/ios')
        with (patch.object(M,'mapped_queue',side_effect=AssertionError('overlay before gate')),
             contextlib.redirect_stdout(io.StringIO()),contextlib.redirect_stderr(io.StringIO())):
            self.assertEqual(40,M.batches_cli(batch_args(self.f),SCRIPTS))
        self.assertFalse((self.root/'batches.json').exists())


if __name__=='__main__':unittest.main()
