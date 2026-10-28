"""Neutral real-core and source-boundary regressions; no device evidence."""
from contextlib import redirect_stdout,redirect_stderr
import copy
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from hmigbot_ios.core import read_json,write_json,MigrationError
from hmigbot_ios152 import native_functional as F
from hmigbot_ios152 import visual_prerequisites as P


def fixture(root):
    project=Path(root);tree=project/'spec/toolkit-fact-tree.json'
    page={'id':'NeutralHome','type':'Activity','purpose':'Neutral source fixture',
        'ios_file':'Neutral.swift','reach_path':['launch'],'reach_paths':[{'display':'launch','depth':0}],
        'navigation_contract':{'trigger_actions':[{'type':'launch'}],'contract_uncertain':False,
                               'verify_signal':{'text_contains':['Neutral']}},'components':[
            {'id':'dynamic','type':'Button','text':None,'is_interactive':True,'triggers':['click'],
             'source_anchor':{'file':'Neutral.swift','line':8},'native_source_span':{'start':5,'end':20},
             'native_identifier':'actual-identifier','native_text_expression':'model.title',
             'behaviors':[{'event':'click','method':'open()','file':'Neutral.swift','line':8}],
             'action':'open detail'},
            {'id':'static','type':'Button','text':'Preferences','is_interactive':True,'triggers':['click'],
             'source_anchor':{'file':'Neutral.swift','line':12},
             'behaviors':[{'event':'click','method':'showPrefs()','file':'Neutral.swift','line':12}],
             'navigation':{'to_page':'PreferencesView'}}], 'functional_checks':[]}
    value={'schema_version':'1.0','source':{'platform':'ios','generator':'neutral-unit-fixture'},
        'app':{'package':'org.hmigbot.neutral'},'features':[],
        'pages':[page],'fragments':[],'dialogs':[],'flow_graph':{'nodes':[],'edges':[]},'stats':{}}
    write_json(tree,value);return project,tree,value


class Contracts(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='native-prereqs36-test-')
        self.addCleanup(self.temp.cleanup)
        self.project,self.tree,self.value=fixture(self.temp.name)

    def cli(self,skill,stem,*argv):
        return subprocess.run([sys.executable,'-B',str(ROOT/'skills'/skill/'scripts'/(stem+'.py')),*map(str,argv)],
            cwd=self.project,capture_output=True,text=True,timeout=180)

    def test_freshness_original_success_and_zero_reach_failure(self):
        receipt=self.project/'gate.json'
        result=self.cli('arkts-visual-verify','check_prereq_freshness',self.tree,'--receipt',receipt)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        self.assertEqual(result.stdout.strip(),'PASS')
        before=self.tree.read_bytes()
        self.assertEqual(read_json(receipt)['exit_code'],0)
        self.assertEqual(self.tree.read_bytes(),before)
        self.value['pages'][0]['reach_path']=[];self.value['pages'][0]['reach_paths']=[];write_json(self.tree,self.value)
        result=self.cli('arkts-visual-verify','check_prereq_freshness',self.tree)
        self.assertEqual(result.returncode,2,result.stdout+result.stderr)
        self.assertIn('NEED:',result.stdout)

    def test_functional_core_reads_project_registry_and_missing_tree(self):
        write_json(self.project/'spec/a2h/functional_registry.json',{'entries':[{'name':'A'}]})
        result=self.cli('arkts-visual-verify','check_functional_dimension',self.tree,self.project)
        self.assertEqual(result.returncode,2,result.stdout+result.stderr)
        self.assertIn('functional-not-injected',result.stdout)
        self.value['pages'][0]['functional_checks']=[{'name':'A'}];write_json(self.tree,self.value)
        result=self.cli('arkts-visual-verify','check_functional_dimension',self.tree,self.project)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        self.tree.unlink()
        # Dispatch still resolves iOS from the project configuration.
        write_json(self.project/'.migbot/config.json',{'source_platform':'ios'})
        result=self.cli('arkts-visual-verify','check_functional_dimension',self.tree,self.project)
        self.assertEqual(result.returncode,2,result.stdout+result.stderr)
        self.assertIn('tree-missing',result.stdout)

    def test_real_projection_merge_fold_preserve_denominator_and_native_fields(self):
        with tempfile.TemporaryDirectory(prefix='functional36-original-oracle-') as raw:
            raw=Path(raw);source=raw/'spec/toolkit-fact-tree.json';write_json(source,self.value)
            engine=ROOT/'skills/a2h-functional-registry/scripts/bin/macos-arm64/_entry.dist/_entry.bin'
            original=subprocess.run([str(engine),'compose_registry_from_tree',str(source)],
                cwd=raw,capture_output=True,text=True,timeout=180)
            self.assertEqual(original.returncode,0,original.stdout+original.stderr)
            original_registry=read_json(raw/'spec/a2h/functional_registry.json')
            original_hosts=read_json(raw/'spec/a2h/compose_host_map.json')
            original_intents=read_json(raw/'spec/a2h/test_intents.json')
        result=self.cli('a2h-functional-registry','compose_registry_from_tree',self.tree)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        registry=read_json(self.project/'spec/a2h/functional_registry.json')
        self.assertEqual(len(registry['entries']),2)
        self.assertEqual(registry,original_registry)
        hosts=read_json(self.project/'spec/a2h/compose_host_map.json')
        self.assertEqual(set(hosts),set(original_hosts))
        for key,host in hosts.items():
            for field in ('host_id','component_id','expected','to_page','precondition','code_anchor'):
                self.assertEqual(host[field],original_hosts[key][field])
        dynamic=next(x for x in hosts.values() if x['component_id']=='dynamic')
        self.assertIsNone(dynamic['tap_text'])
        self.assertEqual(dynamic['tap_by'],'native_observation_required')
        self.assertNotIn('source_native_selector',dynamic) # unproved declared name
        intents=read_json(self.project/'spec/a2h/test_intents.json')
        self.assertEqual(intents['statistics'],original_intents['statistics'])
        for group,items in intents['groups'].items():
            self.assertEqual([x['feature_path'] for x in items],
                             [x['feature_path'] for x in original_intents['groups'][group]])
            for new,old in zip(items,original_intents['groups'][group]):
                self.assertEqual([s.split('，预期结果：')[-1] for s in new['steps']],
                                 [s.split('，预期结果：')[-1] for s in old['steps']])
        self.assertNotIn('点击「Button#dynamic」',json.dumps(intents,ensure_ascii=False))
        result=self.cli('a2h-functional-merge','compose_merge_into_facttree','--write')
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        merged=read_json(self.tree);items=merged['pages'][0]['functional_checks']
        self.assertEqual(len(items),2)
        self.assertTrue(all('expected_ios' in x and 'ios_anchor' in x for x in items))
        self.assertTrue(all('expected_android' not in x for x in items))
        keys=[F.check_key(x) for x in items]
        items[0].update(expected_ios='Actually observed neutral result',ios_trusted=False,
                        ios_anchor={'evidence_file':'neutral-observation.json'},precondition=None)
        write_json(self.tree,merged)
        for stem,argv in [('compose_merge_into_facttree',['--write']),('fold_enum_groups',[str(self.tree),'--write'])]:
            result=self.cli('a2h-functional-merge',stem,*argv)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            now=read_json(self.tree)['pages'][0]['functional_checks']
            self.assertEqual([F.check_key(x) for x in now],keys)
            self.assertEqual(now[0]['expected_ios'],'Actually observed neutral result')
            self.assertIs(now[0]['ios_trusted'],False)
            self.assertEqual(now[0]['ios_anchor'],{'evidence_file':'neutral-observation.json'})

    def test_source_identifier_requires_exact_parser_proof_and_stays_source_only(self):
        host={'NeutralHome>Button#dynamic':{'host_id':'NeutralHome','component_id':'dynamic',
            'tap_text':'Button#dynamic','tap_by':'text'}}
        proof={'dynamic':{'id':'dynamic','accessibility_identifier':'actual-identifier',
            'file':'Neutral.swift','line':8,'start':5,'end':20}}
        F.project_locators(self.value,host,{'groups':{}},proof)
        item=next(iter(host.values()))
        self.assertEqual(item['source_native_selector']['value'],'actual-identifier')
        self.assertEqual(item['tap_by'],'native_observation_required')
        self.assertIsNone(item['tap_text'])
        snapshot=copy.deepcopy(host)
        F.project_locators(self.value,host,{'groups':{}},proof)
        self.assertEqual(host,snapshot)
        F.project_locators(self.value,host,{'groups':{}},{})
        self.assertNotIn('source_native_selector',next(iter(host.values())))

    def test_reordered_checks_preserve_whole_gt_block_and_loss_fails(self):
        before=copy.deepcopy(self.value)
        before['pages'][0]['functional_checks']=[{'fp_id':'one','expected_ios':None,'ios_trusted':False,
            'ios_anchor':None},{'fp_id':'two','expected_ios':'Observed','ios_trusted':True,'ios_anchor':{'capture':'x'}}]
        wire=copy.deepcopy(before)
        wire['pages'][0]['functional_checks']=[{'fp_id':'two','expected_android':'BAD','android_trusted':False,
            'android_anchor':{'capture':'BAD'}},{'fp_id':'one','expected_android':'BAD','android_trusted':True}]
        result=F.restore_checks(before,wire,{})['pages'][0]['functional_checks']
        self.assertEqual(result[0]['expected_ios'],'Observed');self.assertIs(result[1]['ios_trusted'],False)
        self.assertIsNone(result[1]['ios_anchor']);self.assertIsNone(result[1]['expected_ios'])
        wire['pages'][0]['functional_checks'].pop()
        with self.assertRaises(MigrationError):F.restore_checks(before,wire,{})

    def test_original_null_enum_fold_keeps_report_and_source_roundtrip(self):
        value=copy.deepcopy(self.value)
        value['native_source_root']='neutral provenance string'
        value['source']['ios_root']='neutral provenance string'
        # No filesystem freshness declaration: these values exercise the pure
        # conversion roundtrip rather than pretend to describe a source build.
        from hmigbot_ios152 import native_canonical as C
        self.assertEqual(C.native_writeback(value,C.legacy_wire(value)),value)
        value.pop('native_source_root');value['source'].pop('ios_root')
        value['pages'][0]['functional_checks']=[{'fp_id':name,'name':'Color-'+name,
            'feature_path':'Color>'+name,'source_section':'enum_options','expected_llm':'Select '+name,
            'expected_ios':None,'ios_trusted':None,'ios_anchor':{'decl_file':'Color.swift','raw_identifier':name},
            'precondition':None} for name in ('Red','Green','Blue','All')]
        write_json(self.tree,value)
        result=self.cli('a2h-functional-merge','fold_enum_groups',self.tree,'--write')
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        folded=read_json(self.tree)
        self.assertEqual(len(folded['pages'][0]['functional_checks']),2)
        report=read_json(self.project/'spec/a2h/_work/fold_enum_report.json')
        self.assertEqual(len(report['folded_groups'][0]['original_members']),4)
        self.assertTrue(all('ios_anchor' in member for member in report['folded_groups'][0]['original_members']))
        F.validate_fold_lineage(value,folded,C.legacy_wire(report))
        corrupt=copy.deepcopy(folded)
        corrupt['pages'][0]['functional_checks'][0]['members'].pop()
        with self.assertRaises(MigrationError):F.validate_fold_lineage(value,corrupt,C.legacy_wire(report))

    def test_old_feature_path_matches_new_fp_id_without_restoring_deleted_original_fields(self):
        before=copy.deepcopy(self.value)
        before['pages'][0]['functional_checks']=[{'feature_path':'Neutral>Action','expected_ios':'Observed',
            'ios_trusted':False,'ios_anchor':None,'old_original_marker':'stale','native_extra':'retained'}]
        wire=copy.deepcopy(before)
        wire['pages'][0]['functional_checks']=[{'fp_id':'new-id','feature_path':'Neutral>Action',
            'expected_android':None,'android_trusted':None,'android_anchor':{'decl_file':'New'}}]
        result=F.restore_checks(before,wire,{})['pages'][0]['functional_checks'][0]
        self.assertEqual(result['expected_ios'],'Observed');self.assertIs(result['ios_trusted'],False)
        self.assertNotIn('old_original_marker',result);self.assertEqual(result['native_extra'],'retained')

    def test_unproved_new_anchor_cannot_turn_into_ground_truth_on_second_merge(self):
        wire=copy.deepcopy(self.value)
        wire['pages'][0]['functional_checks']=[{'fp_id':'A','expected_android':'UNPROVED','android_trusted':True,
            'android_anchor':{'decl_file':'Current.swift','capture':'UNPROVED'},'evidence':'UNPROVED'}]
        first=F.restore_checks(self.value,wire,{})
        check=first['pages'][0]['functional_checks'][0]
        self.assertIsNone(check['expected_ios']);self.assertIsNone(check['ios_trusted'])
        self.assertEqual(check['ios_anchor'],{'decl_file':'Current.swift'})
        self.assertFalse(F.has_grounding(check))
        second=F.restore_checks(first,wire,{})
        self.assertFalse(F.has_grounding(second['pages'][0]['functional_checks'][0]))
        clean=copy.deepcopy(wire)
        clean['pages'][0]['functional_checks']=[{'fp_id':'A','expected_android':None,'android_trusted':None,
                                               'android_anchor':{'decl_file':'Current.swift'}}]
        third=F.restore_checks(second,clean,{})
        self.assertNotIn('native_unproved_original_oracle',third['pages'][0]['functional_checks'][0])

    def test_native_unknown_path_cannot_escape_mirror_and_android_argv_stays_original(self):
        result=self.cli('a2h-functional-merge','compose_merge_into_facttree','--write','--unknown-output',self.tree)
        self.assertEqual(result.returncode,2,result.stdout+result.stderr)
        self.assertEqual(read_json(self.tree),self.value)
        android=copy.deepcopy(self.value);android['source']={'platform':'android'};write_json(self.tree,android)
        result=self.cli('a2h-functional-registry','compose_registry_from_tree',self.tree,'--unknown-original-arg')
        engine=ROOT/'skills/a2h-functional-registry/scripts/bin/macos-arm64/_entry.dist/_entry.bin'
        original=subprocess.run([str(engine),'compose_registry_from_tree',str(self.tree),'--unknown-original-arg'],
            cwd=self.project,capture_output=True,text=True,timeout=180)
        self.assertEqual(result.returncode,original.returncode)
        self.assertEqual(result.stdout,original.stdout)

    def test_functional_original_canonical_wire_and_empty_projection_contracts(self):
        from hmigbot_ios152.compiled_runtime import execute
        from hmigbot_ios152 import native_canonical as C
        scripts=ROOT/'skills/arkts-visual-verify/scripts'
        (self.project/'p/spec/a2h').mkdir(parents=True)
        write_json(self.project/'p/spec/a2h/functional_registry.json',{'entries':[{'name':'A'}]})
        for truth in (None,False,True):
            value=copy.deepcopy(self.value)
            value['pages'][0]['functional_checks']=[{'name':'A','expected_ios':'Outcome','ios_trusted':truth}]
            write_json(self.project/'t',value)
            native=execute('check_functional_dimension',['xtp'],scripts,cwd=self.project,capture_output=True)
            write_json(self.project/'t',C.legacy_wire(value))
            legacy=execute('check_functional_dimension',['xtp'],scripts,cwd=self.project,capture_output=True)
            self.assertEqual((native.returncode,native.stdout,native.stderr),(legacy.returncode,legacy.stdout,legacy.stderr))
        self.value['pages'][0]['components']=[];write_json(self.tree,self.value)
        result=self.cli('a2h-functional-registry','compose_registry_from_tree',self.tree)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        for name in F.FILES:self.assertTrue((self.project/'spec/a2h'/name).is_file())
        result=self.cli('a2h-functional-registry','compose_registry_from_tree')
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        self.assertIn('Native functional receipt',result.stderr)

    def test_documented_member_probe_fails_missing_unit_and_downgrades_missing_specs(self):
        scripts=ROOT/'skills/arkts-visual-verify/scripts'
        with redirect_stdout(io.StringIO()):self.assertEqual(P.dimensions(['--project-root',str(self.project)],scripts),2)
        for name in ('visual-fixer','visual-fixer-reviewer'):
            p=self.project/'.codex/agents'/(name+'.toml');p.parent.mkdir(parents=True,exist_ok=True);p.write_text('name="'+name+'"')
        with redirect_stdout(io.StringIO()):self.assertEqual(P.dimensions(['--project-root',str(self.project)],scripts),3)
        p=self.project/'spec/baseline/ui/page_Neutral.md';p.parent.mkdir(parents=True);p.write_text('Neutral page')
        with redirect_stdout(io.StringIO()):self.assertEqual(P.dimensions(['--project-root',str(self.project)],scripts),0)

    def test_original_duplicate_display_ids_keep_distinct_paths_and_grounding(self):
        before=copy.deepcopy(self.value)
        before['pages'][0]['functional_checks']=[
            {'fp_id':'FP_Unknown','feature_path':'Form>Unknown','expected_ios':'First observation','ios_trusted':False,'ios_anchor':None},
            {'fp_id':'FP_Unknown','feature_path':'Form>Unknown#2','expected_ios':None,'ios_trusted':True,'ios_anchor':{'capture':'second'}}]
        from hmigbot_ios152 import native_canonical as C
        wire=C.legacy_wire(before);wire['pages'][0]['functional_checks'].reverse()
        result=F.restore_checks(before,wire,{})['pages'][0]['functional_checks']
        self.assertEqual(result[0]['feature_path'],'Form>Unknown#2');self.assertIs(result[0]['ios_trusted'],True)
        self.assertEqual(result[0]['ios_anchor'],{'capture':'second'})
        self.assertEqual(result[1]['expected_ios'],'First observation');self.assertIs(result[1]['ios_trusted'],False)
        wire['pages'][0]['functional_checks'][0]['fp_id']='FP_Named'
        changed=F.restore_checks(before,wire,{})
        matching,removed=F.match_checks(F.checks(before),F.checks(changed))
        self.assertFalse(removed);self.assertEqual(len(matching),2)
        self.assertIs(changed['pages'][0]['functional_checks'][0]['ios_trusted'],True)
        duplicate=copy.deepcopy(before)
        duplicate['pages'][0]['functional_checks'][1]['feature_path']='Form>Unknown'
        with self.assertRaises(MigrationError):F.checks(duplicate)

    def test_identity_namespaces_and_unique_legacy_id_fallback(self):
        before=copy.deepcopy(self.value)
        before['pages'][0]['functional_checks']=[{'fp_id':'same','expected_ios':'Legacy GT','ios_trusted':False},
            {'fp_id':'other','feature_path':'same','expected_ios':'Distinct GT','ios_trusted':True}]
        self.assertEqual(len(F.checks(before)),2)
        from hmigbot_ios152 import native_canonical as C
        wire=C.legacy_wire(before);wire['pages'][0]['functional_checks'][0]['feature_path']='Form>AddedPath'
        result=F.restore_checks(before,wire,{})
        self.assertEqual(result['pages'][0]['functional_checks'][0]['expected_ios'],'Legacy GT')
        self.assertEqual(result['pages'][0]['functional_checks'][1]['expected_ios'],'Distinct GT')
        _,removed=F.match_checks(F.checks(before),F.checks(result));self.assertFalse(removed)
        ambiguous=copy.deepcopy(wire)
        ambiguous['pages'][0]['functional_checks'].append({'fp_id':'same','feature_path':'Form>Other'})
        with self.assertRaises(MigrationError):F.restore_checks(before,ambiguous,{})

    def test_fold_prefix_collision_cannot_inherit_an_ordinary_check_grounding(self):
        before=copy.deepcopy(self.value)
        before['pages'][0]['functional_checks']=[{'fp_id':'parent','feature_path':'Color',
            'expected_ios':'Observed parent control','ios_trusted':True,'check_kind':'functional'}]
        wire=copy.deepcopy(before)
        wire['pages'][0]['functional_checks']=[{'fp_id':'group','feature_path':'Color',
            'check_kind':'enum_group_presence','expected_android':None,'android_trusted':None}]
        with self.assertRaises(MigrationError):F.restore_checks(before,wire,{})
        # Missing discriminator is the historical ordinary-functional default.
        wire['pages'][0]['functional_checks'][0]['check_kind']=None
        result=F.restore_checks(before,wire,{})
        self.assertEqual(result['pages'][0]['functional_checks'][0]['expected_ios'],'Observed parent control')


if __name__=='__main__':unittest.main()
