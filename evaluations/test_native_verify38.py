"""Neutral legacy-input/collector contracts; fixtures are not device evidence."""
import copy
from contextlib import redirect_stdout
import hashlib
import io
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from hmigbot_ios.core import MigrationError,write_json,read_json
from hmigbot_ios152 import native_functional as F,native_visual as V,native_canonical as C


def legacy_fixture():
    check={'name':'Same','feature_path':'Form>Same','code_anchor':'Neutral.swift:3',
        'android_anchor':{'decl_file':'Neutral.swift','impl_file':None,'raw_identifier':'Same'},
        'expected_android':None,'android_trusted':None}
    component={'id':'button','source_anchor':{'file':'Neutral.swift','line':3,'sha256':'source-hash'}}
    tree={'source':{'platform':'ios'},'pages':[{'id':'Form','components':[component],'functional_checks':[check]}],
          'fragments':[],'dialogs':[]}
    contracts={'functional_registry.json':{'entries':[{'feature_path':'Form>Same','source_file':'Neutral.swift','raw_identifier':'Same'}]},
        'compose_host_map.json':{'Form>Same':{'host_id':'Form','component_id':'button','code_anchor':'Neutral.swift:3'}}}
    source=SimpleNamespace(files={'Neutral.swift'},records={'Neutral.swift':{'sha256':'source-hash'}})
    return tree,contracts,source


class LegacySeeds(unittest.TestCase):
    def test_static_anchor_migrates_without_upgrading_old_runtime_aliases(self):
        tree,contracts,source=legacy_fixture();original=copy.deepcopy(tree)
        check=tree['pages'][0]['functional_checks'][0]
        check.update(expected_android='OLD UNPROVED',android_trusted=False)
        check['android_anchor']['capture']='OLD UNPROVED CAPTURE'
        seeded,count=F.legacy_static_seeds(tree,contracts,source)
        row=seeded['pages'][0]['functional_checks'][0]
        self.assertEqual(count,1);self.assertEqual(row['ios_anchor'],original['pages'][0]['functional_checks'][0]['android_anchor'])
        self.assertIsNone(row['expected_ios']);self.assertIsNone(row['ios_trusted']);self.assertFalse(F.has_grounding(row))
        self.assertIn('android_anchor_runtime_fields',row['native_unproved_original_oracle'])
        self.assertIs(row['native_unproved_original_oracle']['android_trusted'],False)
        native=C.native_writeback({},C.legacy_wire(seeded))
        self.assertEqual(native['pages'][0]['functional_checks'][0]['ios_anchor'],row['ios_anchor'])
        self.assertNotIn('ios_anchor',tree['pages'][0]['functional_checks'][0])

    def test_explicit_native_null_and_false_are_never_overwritten(self):
        tree,contracts,source=legacy_fixture()
        tree['pages'][0]['functional_checks'][0].update(ios_anchor=None,expected_ios='Native observation',ios_trusted=False)
        result,count=F.legacy_static_seeds(tree,contracts,source)
        row=result['pages'][0]['functional_checks'][0]
        self.assertEqual(count,0);self.assertIsNone(row['ios_anchor']);self.assertIs(row['ios_trusted'],False)
        self.assertEqual(row['expected_ios'],'Native observation')

    def test_anchor_component_registry_and_selected_file_must_all_agree(self):
        tree,contracts,source=legacy_fixture()
        for change in ('raw','line','file','hash','duplicate'):
            value=copy.deepcopy(tree);c=copy.deepcopy(contracts);s=copy.deepcopy(source)
            if change=='raw':value['pages'][0]['functional_checks'][0]['android_anchor']['raw_identifier']='Different'
            if change=='line':value['pages'][0]['components'][0]['source_anchor']['line']=4
            if change=='file':s.files=set()
            if change=='hash':s.records['Neutral.swift']['sha256']='changed'
            if change=='duplicate':c['functional_registry.json']['entries']*=2
            with self.subTest(change=change),self.assertRaises(MigrationError):F.legacy_static_seeds(value,c,s)


def source_tree():
    return {'source':{'platform':'ios','generator':'neutral-fixture'},'app':{'package':'org.hmigbot.neutral'},
        'pages':[{'id':'Neutral','inbound_triggers':[],
            'native_identity':{'required':[{'label':'Neutral title','element_type':48}]},
            'functional_checks':[{'name':'Same','feature_path':'Form>A','expected_ios':None,'ios_trusted':None},
                                 {'name':'Same','feature_path':'Form>B','expected_ios':None,'ios_trusted':None}]}],
        'fragments':[],'dialogs':[]}


class FixtureObserver:
    def __init__(self):self.state={'bundle_id':'org.hmigbot.neutral'};self.values={'A':0,'B':0};self.sequence=0
    def node(self,kind,label,identifier=''):
        return {'element_type':kind,'label':label,'identifier':identifier,'exists':True,'hittable':True,'enabled':True,
                'frame':{'x':0,'y':0,'width':100,'height':30},'children':[]}
    def capture(self,directory):
        directory=Path(directory);directory.mkdir(parents=True,exist_ok=True);self.sequence+=1
        native=directory/(str(self.sequence)+'.native.json')
        tree=self.node(2,'Neutral app');tree['children']=[self.node(48,'Neutral title'),self.node(9,'Same','A'),self.node(9,'Same','B')]
        observation={'tree':tree,'request_id':str(self.sequence),'session':'SYNTHETIC-FIXTURE','bundle_id':self.state['bundle_id'],
            'app_state_before':4,'app_state_after':4,'system_tree_status':'observed','system_overlay':{'alert_count':0},
            'fixture_values':dict(self.values)}
        write_json(native,observation)
        return {'observation':observation,'native_json':str(native),'png':str(directory/'SYNTHETIC-NO-DEVICE.png'),
                'sha256':{'native_json':C.sha(native),'png':'SYNTHETIC-NO-DEVICE'}}
    def command(self,operation,arguments):
        selector=arguments.get('selector',{})
        if operation=='find':return {'ok':True,'result':self.node(48,selector.get('label','Neutral title'))}
        if operation=='tap':self.values[selector['identifier']]+=1;return {'ok':True,'result':{}}
        raise AssertionError(operation)


class CollectorContracts(unittest.TestCase):
    def setUp(self):
        self.temporary=tempfile.TemporaryDirectory(prefix='native38-collector-');self.addCleanup(self.temporary.cleanup)
        self.root=Path(self.temporary.name);self.tree=source_tree();self.page=self.tree['pages'][0]
    def plan(self):
        return {'functional_checks_sha256':V.functional_snapshot(self.page),'checks':[
            {'check_idx':i,'feature_path':c['feature_path'],'check_name':c['name'],
             'actions':[{'operation':'tap','arguments':{'selector':{'identifier':identifier}},'safety':'normal'}]}
            for i,(c,identifier) in enumerate(zip(self.page['functional_checks'],('A','B')))]}
    def test_collector_emits_original_idx_schema_and_distinct_actual_before_states(self):
        observer=FixtureObserver();output=self.root/'grounding/Neutral'
        result=V.sweep(observer,self.tree,'Neutral',self.plan(),output,project=self.root)
        meta=read_json(output/'run_meta.json')
        self.assertEqual(result['records'],2);self.assertNotIn('records',meta)
        self.assertEqual([(c['idx'],c['name'],c['status']) for c in meta['checks']],[(0,'Same','ok'),(1,'Same','ok')])
        first=read_json(Path(meta['checks'][0]['before_capture']['native_json']))
        second=read_json(Path(meta['checks'][1]['before_capture']['native_json']))
        self.assertEqual(first['fixture_values'],{'A':0,'B':0});self.assertEqual(second['fixture_values'],{'A':1,'B':0})
        # Metadata directory names need not equal the logical node id.
        renamed=output.parent/'Encoded Node Folder';renamed.mkdir()
        (output/'run_meta.json').replace(renamed/'run_meta.json')
        judgments=[{'node':'Neutral','check_idx':i,'check_name':'Same','feature_path':c['feature_path'],
                    'functional_checks_sha256':meta['functional_checks_sha256'],'expected_ios':str(i),'ios_trusted':bool(i)}
                   for i,c in enumerate(self.page['functional_checks'])]
        write_json(self.root/'grounding_results.json',judgments)
        self.assertIsNone(C._judgement_debt(self.root,self.tree))
        incomplete=copy.deepcopy(judgments);incomplete[0].pop('functional_checks_sha256')
        write_json(self.root/'grounding_results.json',incomplete)
        self.assertIn('lost its collector snapshot',C._judgement_debt(self.root,self.tree))
        write_json(self.root/'grounding_results.json',judgments)
        changed=copy.deepcopy(self.tree);changed['pages'][0]['functional_checks'].reverse()
        self.assertIn('snapshot is stale',C._judgement_debt(self.root,changed))
        tree=self.root/'spec/toolkit-fact-tree.json';write_json(tree,self.tree)
        with redirect_stdout(io.StringIO()):code=C.tree_write_cli('writeback_walk',['--tree',str(tree),
            '--grounding',str(self.root/'grounding_results.json')],ROOT/'skills/arkts-visual-verify/scripts')
        self.assertEqual(code,0)
        checks=read_json(tree)['pages'][0]['functional_checks']
        self.assertEqual([(c['expected_ios'],c['ios_trusted'],c['grounded_match']) for c in checks],[('0',False,'idx'),('1',True,'idx')])
        for change in ('missing','wrong-index'):
            rows=copy.deepcopy(judgments)
            if change=='missing':rows[0].pop('functional_checks_sha256')
            else:rows[0]['check_idx']=1
            write_json(self.root/'grounding_results.json',rows);write_json(tree,self.tree);before=tree.read_bytes()
            with self.subTest(change=change),self.assertRaises(MigrationError):C.tree_write_cli('writeback_walk',['--tree',str(tree),
                '--grounding',str(self.root/'grounding_results.json')],ROOT/'skills/arkts-visual-verify/scripts')
            self.assertEqual(tree.read_bytes(),before)
        write_json(self.root/'grounding_results.json',judgments)
        write_json(tree,changed);before=tree.read_bytes()
        with self.assertRaises(MigrationError):C.tree_write_cli('writeback_walk',['--tree',str(tree),
            '--grounding',str(self.root/'grounding_results.json')],ROOT/'skills/arkts-visual-verify/scripts')
        self.assertEqual(tree.read_bytes(),before)

    def test_list_binding_duplicate_indices_and_legacy_ambiguous_names_fail(self):
        for change in ('fingerprint','path','bool','duplicate','name'):
            plan=self.plan()
            if change=='fingerprint':plan['functional_checks_sha256']='stale'
            if change=='path':plan['checks'][0]['feature_path']='Wrong'
            if change=='bool':plan['checks'][0]['check_idx']=True
            if change=='duplicate':plan['checks'][1]['check_idx']=0
            if change=='name':plan['checks'][0]['check_name']='Wrong'
            with self.subTest(change=change),self.assertRaises(MigrationError):V.sweep_plans(self.page,plan)
        with self.assertRaises(MigrationError):V.sweep_plans(self.page,{'checks':{'Same':{'actions':[]}}})
        result=V.sweep(FixtureObserver(),self.tree,'Neutral',{'checks':{}},self.root/'not-found',project=self.root)
        self.assertEqual(result['records'],2)
        self.assertEqual([c['status'] for c in read_json(self.root/'not-found/run_meta.json')['checks']],['not_found','not_found'])

    def test_template_reference_is_portable_with_spaces_and_script_symlink(self):
        template=(ROOT/'skills/arkts-visual-verify/references/phase2-chunk-dispatch-template.md').read_text()
        self.assertNotIn('/Users/ventiu/',template);self.assertIn('$SCRIPTS/../references/phase2-edge-walk.md',template)
        scripts=ROOT/'skills/arkts-visual-verify/scripts';alias=self.root/'Path With Spaces'/'Scripts Alias'
        alias.parent.mkdir();alias.symlink_to(scripts,target_is_directory=True)
        self.assertEqual(C.sha((alias/'../references/phase2-edge-walk.md').resolve()),
                         C.sha(ROOT/'skills/arkts-visual-verify/references/phase2-edge-walk.md'))


class HostIdentityContracts(unittest.TestCase):
    def tree(self):
        host={'id':'Host','fq_class':'Host','ios_file':'Host.swift','is_container':True,'parent_in_nav':None,
            'contains':['Leaf','Other'],'navigation_contract':{'relationship_kind':'activity_root'},
            'native_identity':{'required':[{'element_type':22,'label':'Tab Bar'}]}}
        leaves=[{'id':name,'fq_class':name,'parent_in_nav':'Host','navigation_contract':{'relationship_kind':'tab'},'native_identity':{
            'required':[{'element_type':48,'label':label}]}} for name,label in [('Leaf','Main title'),('Other','Other title')]]
        return {'pages':[host],'fragments':leaves,'dialogs':[],
            'native_tab_groups':[{'host':'Host','file':'Host.swift','items':[{'target':'Leaf'},{'target':'Other'}]}]}
    def observation(self,other=False,hidden_other=False):
        def node(kind,label,hittable=True):return {'element_type':kind,'label':label,'exists':True,'hittable':hittable,'children':[]}
        children=[node(22,'Tab Bar'),node(48,'Main title')]
        if other or hidden_other:children.append(node(48,'Other title',not hidden_other))
        return {'tree':{'children':children},'request_id':'SYNTHETIC-HOST','app_state_before':4,'app_state_after':4,
            'system_tree_status':'observed','system_overlay':{'alert_count':0}}
    def live(self,observation,identities):
        return {name:{'required':[{'visible_unique':sum(V.selector_matches(n,s) and n.get('hittable') is True
            for n in V.nodes(observation['tree']))==1} for s in c.get('required',[])],'excluded':[]}
            for name,c in identities.items()}
    def result(self,tree,page,observation=None):
        identities=V.identities_from_tree(tree);observation=observation or self.observation()
        return V.arrival(observation,page,identities,self.live(observation,identities))
    def test_host_and_selected_leaf_both_keep_their_own_unique_identity(self):
        tree=self.tree()
        for page,level in [('Host','host'),('Leaf','leaf')]:
            row=self.result(tree,page)
            self.assertTrue(row['verified'],row);self.assertEqual(row['matched_pages'],[page])
            self.assertEqual(row['all_matched_pages'],['Host','Leaf']);self.assertEqual(row['identity_level'],level)
    def test_two_visible_leaves_fail_even_for_unique_host(self):
        for page in ('Host','Leaf'):self.assertFalse(self.result(self.tree(),page,self.observation(other=True))['arrived'])
    def test_unresolved_parent_only_blocks_when_a_host_relationship_is_used(self):
        value=self.tree();value['fragments'][0]['parent_in_nav']='Missing'
        # An unrelated but valid host still exists in the inventory.
        value['pages'][0]['contains']=['Other'];value['native_tab_groups'][0]['items']=[{'target':'Other'}]
        observed=self.observation();observed['tree']['children'].pop(0)
        self.assertTrue(self.result(value,'Leaf',observed)['verified'])
        row=self.result(value,'Leaf')
        self.assertFalse(row['arrived']);self.assertIn('identity_relationship_unavailable',row['blockers'])
    def test_standalone_annotation_cli_cannot_claim_internal_host_roles(self):
        with tempfile.TemporaryDirectory(prefix='native38-flat-cli-') as temporary:
            root=Path(temporary);identities=V.identities_from_tree(self.tree())
            write_json(root/'identities.json',identities);write_json(root/'observation.json',self.observation())
            with redirect_stdout(io.StringIO()):code=V.main(['arrival','--observation',str(root/'observation.json'),
                '--identities',str(root/'identities.json'),'--page','Leaf','--out',str(root/'result.json')])
            result=read_json(root/'result.json')
            self.assertEqual(code,15);self.assertFalse(result['snapshot_match'])
            self.assertEqual(result['matched_host_pages'],[]);self.assertEqual(result['matched_pages'],['Host','Leaf'])
    def test_unselected_accessibility_content_is_not_a_visible_leaf(self):
        row=self.result(self.tree(),'Leaf',self.observation(hidden_other=True))
        self.assertTrue(row['arrived']);self.assertEqual(row['all_matched_pages'],['Host','Leaf'])
    def test_empty_or_invalid_host_declaration_cannot_be_substituted_by_leaf(self):
        value=self.tree();value['pages'][0]['native_identity']['required']=[]
        self.assertFalse(self.result(value,'Host')['arrived'])
        for change in ('parent','contains','group','container'):
            value=self.tree()
            if change=='parent':value['fragments'][0]['parent_in_nav']=None
            if change=='contains':value['pages'][0]['contains']=[]
            if change=='group':value['native_tab_groups'][0]['items'].pop()
            if change=='container':value['pages'][0]['is_container']=False
            with self.subTest(change=change):self.assertFalse(self.result(value,'Leaf')['arrived'])
    def test_fake_role_metadata_is_not_accepted_and_parent_cycles_fail(self):
        value=self.tree();value['native_tab_groups']=[]
        value['pages'][0]['native_identity']['_native_identity_host_members']=['Leaf','Other']
        self.assertFalse(self.result(value,'Leaf')['arrived'])
        value=self.tree();value['pages'][0]['parent_in_nav']='Leaf'
        self.assertFalse(self.result(value,'Leaf')['arrived'])
    def test_unrelated_host_with_visible_leaf_is_rejected(self):
        value=self.tree()
        second=copy.deepcopy(value['pages'][0]);second.update(id='HostB',fq_class='HostB',ios_file='HostB.swift',contains=['ChildB'])
        second['native_identity']={'required':[{'element_type':22,'label':'Other Bar'}]};value['pages'].append(second)
        value['fragments'].append({'id':'ChildB','fq_class':'ChildB','parent_in_nav':'HostB','navigation_contract':{'relationship_kind':'tab'},'native_identity':{'required':[{'label':'Child B'}]}})
        value['native_tab_groups'].append({'host':'HostB','file':'HostB.swift','items':[{'target':'ChildB'}]})
        observed=self.observation();observed['tree']['children'][0]['label']='Other Bar'
        row=self.result(value,'Leaf',observed)
        self.assertFalse(row['arrived']);self.assertIn('unrelated_or_ambiguous_native_host',row['blockers'])
    def test_multiple_host_matches_are_not_silently_disambiguated(self):
        value=self.tree();second=copy.deepcopy(value['pages'][0]);second.update(id='HostB',fq_class='HostB',ios_file='HostB.swift',contains=['ChildB'])
        value['pages'].append(second);value['fragments'].append({'id':'ChildB','fq_class':'ChildB','parent_in_nav':'HostB','navigation_contract':{'relationship_kind':'tab'},'native_identity':{'required':[{'label':'Child B'}]}})
        value['native_tab_groups'].append({'host':'HostB','file':'HostB.swift','items':[{'target':'ChildB'}]})
        self.assertFalse(self.result(value,'Leaf')['arrived']);self.assertFalse(self.result(value,'Host')['arrived'])


if __name__=='__main__':unittest.main()
