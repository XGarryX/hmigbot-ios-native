"""Neutral Source/contract/original-resolver tests, never device evidence."""
import copy
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from hmigbot_ios.core import read_json,write_json
from hmigbot_ios152 import native_file_mapping as M
from hmigbot_ios152 import native_canonical as C
from hmigbot_ios152.source import Source
from hmigbot_ios152.native_routes import analyze


@unittest.skipUnless(os.environ.get('HMIGBOT_TEST_ORIGINAL_VISUAL_ENGINE'),'isolated original core required')
class NativeMappingTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='native-map45-test-')
        self.root=Path(self.temp.name).resolve();self.project=self.root/'target';self.project.mkdir()
        self.src=self.root/'Source';self.src.mkdir()
        (self.src/'Neutral.swift').write_text('import SwiftUI\nstruct AlphaView: View { var body: some View { Text("Neutral") } }\n')
        self.source=Source(self.src);self.facts=analyze(self.source)
        self.tree=self.project/'spec/toolkit-fact-tree.json'
        self.value={'$schema_version':1,'source_platform':'ios','source':{'platform':'ios','ios_root':str(self.src)},
            'app':{'launcher_short':'AlphaView','launcher_activity':'AlphaView','package':'org.hmigbot.neutral'},
            'pages':[{'id':'AlphaView','fq_class':'AlphaView','type':'Activity','purpose':'Synthetic contract',
                      'functional_checks':[],'navigation':{'inbound':[],'outbound':[]}}],
            'fragments':[],'dialogs':[],'flow_graph':{'nodes':[],'edges':[]}}
        self.save();self.ets('entry/src/main/ets/pages/TargetPage.ets');self.spec()
        self.engine=Path(os.environ['HMIGBOT_TEST_ORIGINAL_VISUAL_ENGINE']).resolve()
        self.calls=[]
        def execute(command,args,scripts,**kw):
            self.calls.append((command,args))
            return subprocess.run([str(self.engine),command,*map(str,args)],cwd=kw.get('cwd'),
                env={**os.environ,'ARKTS_SKILL_DIR':str(self.engine.parents[3])},capture_output=True,text=True,timeout=60)
        self.patcher=patch.object(C,'_core',side_effect=execute);self.patcher.start()

    def tearDown(self):self.patcher.stop();self.temp.cleanup()
    def save(self):write_json(self.tree,self.value)
    def ets(self,name):
        p=self.project/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('@Component struct Target { build() {} }\n')
    def spec(self,owner='AlphaView',output='entry/src/main/ets/pages/TargetPage.ets',anchors='Neutral.swift',suffix='one'):
        p=self.project/('spec/baseline/ui/page_'+suffix+'.md');p.parent.mkdir(parents=True,exist_ok=True)
        surface='' if owner is None else '- iOS 页面/系统表面: '+owner+'；explanation is not a type\n'
        p.write_text('# Neutral\n```yaml\nsource_anchors:\n  deliberately_wrong_key: "'+anchors+'"\n```\n\n## 溯源\n'+surface+'- 输出文件: `'+output+'`\n');return p
    def mapped(self):return M.mapped_queue(self.tree,self.project,ROOT/'skills/arkts-visual-verify/scripts',source=self.source)

    def test_contract_values_and_real_source_resolve_without_changing_input(self):
        before=self.tree.read_bytes();queue,proof=self.mapped()
        self.assertEqual(queue['entries'][0]['file_resolved'],'entry/src/main/ets/pages/TargetPage.ets')
        self.assertEqual(queue['entries'][0]['name'],'AlphaView');self.assertEqual(queue['total'],1)
        self.assertEqual(self.tree.read_bytes(),before)
        self.assertEqual(proof['native_path_resolution']['unfound'],1)
        self.assertEqual(proof['final_path_resolution']['resolved'],1)
        self.assertTrue(proof['core_runs']);self.assertTrue(proof['target_ets'])

    def test_duplicate_output_stems_remain_ambiguous(self):
        self.ets('feature/src/main/ets/pages/TargetPage.ets');q,p=self.mapped()
        self.assertIsNone(q['entries'][0]['file_resolved'])
        self.assertEqual(len(q['entries'][0]['file_candidates']),2)
        self.assertEqual(q['path_resolution']['ambiguous'],1)

    def test_ambiguous_probe_cannot_hide_a_nonexistent_contract_path(self):
        self.ets('feature/src/main/ets/pages/TargetPage.ets')
        self.spec(output='missing/src/main/ets/pages/TargetPage.ets')
        q,proof=self.mapped()
        self.assertEqual(q['path_resolution']['unfound'],1)
        self.assertTrue(any(p.get('state')=='ambiguous' and not p['accepted'] for p in proof['contracts']))

    def test_bundled_page_template_plain_surface_and_unquoted_output(self):
        p=self.spec();p.write_text(p.read_text().replace('iOS 页面/系统表面:','iOS 页面:').replace('`entry/src/main/ets/pages/TargetPage.ets`','entry/src/main/ets/pages/TargetPage.ets'))
        q,proof=self.mapped();self.assertEqual(q['path_resolution']['resolved'],1)

    def test_native_direct_and_ambiguity_are_never_replaced_by_contract(self):
        self.ets('entry/src/main/ets/pages/AlphaView.ets')
        q,p=self.mapped();self.assertEqual(q['entries'][0]['file_resolved'],'entry/src/main/ets/pages/AlphaView.ets')
        self.assertFalse(p['contracts'])
        self.ets('feature/src/main/ets/pages/AlphaView.ets');q,p=self.mapped()
        self.assertEqual(q['path_resolution']['ambiguous'],1);self.assertFalse(p['contracts'])

    def test_false_surface_does_not_fall_back_to_file_owner_or_prose(self):
        for owner in ['MissingView','AlphaView plus prose','Other.AlphaView']:
            with self.subTest(owner=owner):
                self.spec(owner);q,p=self.mapped();self.assertEqual(q['path_resolution']['unfound'],1)

    def test_file_only_requires_unique_current_page_declaration(self):
        self.spec(None);q,p=self.mapped();self.assertEqual(q['path_resolution']['resolved'],1)
        (self.src/'Other.swift').write_text('import SwiftUI\nstruct OtherView: View { var body: some View { Text("Other") } }\n')
        self.source=Source(self.src);self.facts=analyze(self.source)
        s=self.spec(None);s.write_text(s.read_text().replace('  deliberately_wrong_key:', '  extra: "Other.swift"\n  deliberately_wrong_key:'))
        q,p=self.mapped();self.assertEqual(q['path_resolution']['unfound'],1)

    def test_surface_must_belong_to_an_anchor_value_and_output_must_match_exactly(self):
        (self.src/'Other.swift').write_text('struct Other {}\n');self.source=Source(self.src);self.facts=analyze(self.source)
        self.spec(anchors='Other.swift');q,p=self.mapped();self.assertEqual(q['path_resolution']['unfound'],1)
        self.spec(output='missing/src/main/ets/pages/TargetPage.ets');q,p=self.mapped()
        self.assertEqual(q['path_resolution']['unfound'],1)

    def test_parent_projection_uses_original_via_parent_and_keeps_dialog_identity(self):
        child={'id':'InlineNotice','fq_class':'InlineNotice','type':'Dialog','purpose':'Synthetic child',
               'functional_checks':[],'navigation':{'inbound':[{'from':'AlphaView'}],'outbound':[]}}
        self.value['dialogs']=[child];self.save();q,p=self.mapped()
        row=next(e for e in q['entries'] if e['name']=='InlineNotice')
        self.assertIsNone(row['file_resolved']);self.assertEqual(row['parent_file_resolved'],'entry/src/main/ets/pages/TargetPage.ets')
        self.assertEqual(row['parent_used'],'AlphaView');self.assertEqual(row['triggered_by'],['AlphaView'])
        self.assertEqual(q['path_resolution']['via_parent'],1)

    def test_projection_id_collision_does_not_change_other_page(self):
        other=copy.deepcopy(self.value['pages'][0]);other.update(id='TargetPage',fq_class='UnmappedType')
        self.value['pages'].append(other);self.save();q,p=self.mapped()
        self.assertEqual(q['total'],2)
        self.assertIsNone(next(e for e in q['entries'] if e['name']=='AlphaView')['file_resolved'])
        self.assertTrue(any('collides' in e.get('reason','') for e in p['contracts']))

    def test_inline_owner_fq_class_does_not_claim_the_parent_contract_directly(self):
        self.value['dialogs']=[{'id':'InlineNotice','fq_class':'AlphaView','type':'Dialog',
            'native_declared_type':False,'functional_checks':[],'navigation':{'inbound':[{'from':'AlphaView'}]}}]
        self.save();q,p=self.mapped();row=next(e for e in q['entries'] if e['name']=='InlineNotice')
        self.assertIsNone(row['file_resolved']);self.assertEqual(row['parent_used'],'AlphaView')
        self.assertEqual(q['path_resolution']['via_parent'],1)

    def test_explicit_multiple_source_types_can_share_one_output_contract(self):
        with (self.src/'Neutral.swift').open('a') as f:f.write('struct BetaView: View { var body: some View { Text("Beta") } }\n')
        self.source=Source(self.src);self.facts=analyze(self.source)
        other=copy.deepcopy(self.value['pages'][0]);other.update(id='BetaView',fq_class='BetaView')
        self.value['pages'].append(other);self.save();self.spec('AlphaView, BetaView')
        q,p=self.mapped();self.assertEqual(q['total'],2);self.assertEqual(q['path_resolution']['resolved'],2)

    def test_module_qualification_and_unqualified_duplicate_owner(self):
        # Official parser facts are real; target membership is a synthetic
        # contract fixture, not an Xcode build or runtime claim.
        (self.src/'Other.swift').write_text((self.src/'Neutral.swift').read_text())
        self.source=Source(self.src);analyze(self.source)
        self.source.selection={'source_membership':[{'path':'Neutral.swift','targets':['A']},
                                                    {'path':'Other.swift','targets':['B']}]}
        self.source.view=SimpleNamespace(artifact={'settings_targets':{'A':{'PRODUCT_MODULE_NAME':'ModuleA'},'B':{'PRODUCT_MODULE_NAME':'ModuleB'}}})
        self.value['pages'][0]['fq_class']='ModuleA.AlphaView';self.save()
        self.spec('AlphaView');q,p=self.mapped();self.assertEqual(q['path_resolution']['unfound'],1)
        self.spec('ModuleA.AlphaView');q,p=self.mapped();self.assertEqual(q['path_resolution']['resolved'],1)
        # A contract exists only for ModuleA, but a bare tree name must still
        # account for ModuleB's real declaration with no contract of its own.
        self.value['pages'][0]['fq_class']='AlphaView';self.save()
        q,p=self.mapped();self.assertEqual(q['path_resolution']['unfound'],1)

    def test_batch_file_overlay_does_not_change_membership_or_native_file(self):
        output=self.project/'spec/batches.json'
        original={'batches':[{'batch_id':'one','pages':[{'name':'AlphaView','file_resolved':None,'kind':'page'},
                   {'name':'AlphaView','file_resolved':'native/Already.ets','kind':'page'}]}], 'coverage':{'planned':2},'sentinel':'preserve'}
        def produced(*a,**kw):write_json(output,original);return 0
        argv=['--fact-tree',str(self.tree),'--out',str(output)]
        with patch.object(C,'data_cli',side_effect=produced),redirect_stdout(io.StringIO()):
            self.assertEqual(M.batches_cli(argv,ROOT/'skills/arkts-visual-verify/scripts'),0)
        result=read_json(output);self.assertEqual(result['batches'][0]['pages'][0]['file_resolved'],'entry/src/main/ets/pages/TargetPage.ets')
        self.assertEqual(result['batches'][0]['pages'][1],original['batches'][0]['pages'][1])
        result['batches'][0]['pages'][0]=original['batches'][0]['pages'][0]
        self.assertEqual(result,original)


if __name__=='__main__':unittest.main()
