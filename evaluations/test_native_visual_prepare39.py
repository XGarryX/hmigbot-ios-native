"""Official-parser and original-core neutral preparation regressions; no UI evidence."""
from contextlib import redirect_stdout
import copy
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from hmigbot_ios.core import MigrationError,read_json,write_json
from hmigbot_ios152 import native_visual_prepare as P
from hmigbot_ios152.compiled_runtime import execute

SWIFT='''import SwiftUI
@main struct NeutralApp: App { var body: some Scene { WindowGroup { NeutralView() } } }
struct NeutralView:View {
 @State var show=false
 var body:some View {
  Button("Open") {show=true}.sheet(isPresented:$show){Editor()}
   .fullScreenCover(isPresented:$show){Editor()}
   .alert("Title",isPresented:$show){
    Button("cancel.key",role:.cancel) {show=false}.accessibilityIdentifier("cancel.real")
    Button("Delete",role:.destructive) {}
    Button("Confirm") {}
   }
 }
}
struct Editor:View { var body:some View { Button("Close"){} } }
'''


class NativePreparation(unittest.TestCase):
 maxDiff=None
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory(prefix='native39-preparation-');self.addCleanup(self.temp.cleanup)
  self.root=Path(self.temp.name);self.src=self.root/'source';self.src.mkdir()
  (self.src/'Main.swift').write_text(SWIFT);self.project=self.root/'target';self.project.mkdir()
  write_json(self.project/'.migbot/config.json',{'source_platform':'ios','ios':{'source_root':str(self.src)}})
 def source(self):return P.checked_source(self.src,self.project)
 def anchor_inputs(self):
  tree={'source':{'platform':'ios','ios_root':str(self.src)},'pages':[
    {'id':'NeutralView','fq_class':'NeutralView'},
    {'id':'Unmatched','fq_class':'Unmatched','ios_source_refs':[str((self.src/'Main.swift').resolve())]}],
    'fragments':[],'dialogs':[]}
  path=self.project/'spec/toolkit-fact-tree.json';write_json(path,tree)
  draft=self.project/'spec/.cache/fact-tree/draft.json';write_json(draft,tree)
  md=self.project/'spec/baseline/ui';md.mkdir(parents=True)
  doc='# page_0000_NeutralView: Neutral\n\n```yaml\nsource_anchors:\n  Alias0: "Main.swift"\n```\n'
  (md/'page_0000_NeutralView.md').write_text(doc,encoding='utf-8')
  return path,draft,md,doc
 def enrich(self,path,draft,md):
  with redirect_stdout(io.StringIO()):return P.enrich_cli(['--fact-tree',str(path),'--page-spec-dir',str(md),
    '--also-draft',str(draft),'--receipt',str(self.root/'receipt.json')],ROOT/'skills/arkts-visual-verify/scripts')
 def test_old_refs_are_removed_and_legacy_draft_does_not_gain_source_provenance(self):
  path,draft,md,_=self.anchor_inputs();value=read_json(draft);value.pop('source');write_json(draft,value)
  self.assertEqual(self.enrich(path,draft,md),0)
  for file in (path,draft):self.assertNotIn('ios_source_refs',read_json(file)['pages'][1])
  self.assertNotIn('source',read_json(draft))
 def test_document_body_and_utf8_text_survive_non_utf8_locale(self):
  path,draft,md,doc=self.anchor_inputs();file=md/'page_0000_NeutralView.md'
  payload=(doc+'\n## 正文示例\n```yaml\nsource_anchors:\n  BodyExample: "NotDeclared.swift"\n```\n').replace('\n','\r\n').encode('utf-8')
  file.write_bytes(payload)
  result=subprocess.run([sys.executable,'-B',str(ROOT/'skills/arkts-visual-verify/scripts/enrich_factree_anchors.py'),
    '--fact-tree',str(path),'--page-spec-dir',str(md),'--also-draft',str(draft),'--project-root',str(self.project)],
    cwd=self.project,env={**os.environ,'LC_ALL':'C','PYTHONUTF8':'0','PYTHONCOERCECLOCALE':'0'},capture_output=True)
  self.assertEqual(result.returncode,0,result.stderr.decode('utf-8','replace'))
  self.assertEqual(file.read_bytes(),payload);self.assertEqual(len(read_json(path)['pages'][0]['ios_source_refs']),1)
 def test_multiple_spec_claims_fail_without_publishing(self):
  path,draft,md,doc=self.anchor_inputs();(md/'page_0001_NeutralView.md').write_text(doc,encoding='utf-8')
  before={p:p.read_bytes() for p in (path,draft)}
  with self.assertRaisesRegex(MigrationError,'Multiple page specifications'):self.enrich(path,draft,md)
  for p,data in before.items():self.assertEqual(p.read_bytes(),data)
 def test_ib_presentations_are_preserved_and_unowned_segue_is_unknown(self):
  (self.src/'Main.storyboard').write_text('''<document><scenes><scene>
<viewController id="host" customClass="HostController"><connections>
<segue id="modal" kind="presentation" destination="detail"/>
</connections></viewController>
<viewController id="detail" customClass="ModalController"><view id="view"><button id="close" title="Close"/></view></viewController>
</scene></scenes>
<segue id="orphan" kind="popoverPresentation" destination="detail"/>
</document>''',encoding='utf-8')
  source,facts=self.source();catalog=P.native_catalog(source,facts,'org.hmigbot.neutral')
  modal=catalog['dialogs']['ModalController'];self.assertEqual(modal['api'],'storyboard.segue')
  self.assertTrue(modal['controls']);self.assertEqual(modal['presentation_sites'][0]['via'],'storyboard.segue')
  self.assertTrue(any(x.get('file')=='Main.storyboard' and x.get('kind')=='popoverPresentation' for x in catalog['unsupported_constructs']))
  self.assertEqual(catalog['status'],'partial_unknowns')
 def test_resource_scope_and_bad_ib_cannot_become_empty_success(self):
  xml=self.src/'Main.storyboard';xml.write_text('<document/>',encoding='utf-8')
  source,facts=self.source();missing=copy.deepcopy(facts);missing.pop('resource_scope')
  with self.assertRaisesRegex(MigrationError,'computed resource scope'):P.native_catalog(source,missing,'org.hmigbot.neutral')
  xml.write_text('<document><broken>',encoding='utf-8')
  with self.assertRaisesRegex(MigrationError,'Main.storyboard'):P.native_catalog(source,facts,'org.hmigbot.neutral')
 def test_catalog_retains_all_static_roles_and_shared_presentations_without_runtime_claims(self):
  source,facts=self.source();catalog=P.native_catalog(source,facts,'org.hmigbot.neutral')
  self.assertEqual(catalog['schema_version'],'native-dialog-catalog/1')
  self.assertEqual(catalog['status'],'complete');self.assertFalse(catalog['runtime_verified'])
  self.assertEqual(len(catalog['dialogs']['Editor']['presentation_sites']),2)
  alert=next(d for k,d in catalog['dialogs'].items() if '.alert@' in k)
  by_text={c['declared_text_literal_or_key']:c for c in alert['controls']}
  self.assertEqual(by_text['cancel.key']['source_role'],'cancel')
  self.assertEqual(by_text['cancel.key']['selector_candidate'],{'identifier':'cancel.real'})
  self.assertEqual(by_text['Delete']['source_role'],'destructive')
  self.assertIsNone(by_text['Confirm']['source_role']);self.assertIsNone(by_text['Confirm']['selector_candidate'])
  for d in catalog['dialogs'].values():
   self.assertFalse(d['automatic_dismiss_allowed'])
   for c in d['controls']:
    self.assertIn('analysis_key',c);self.assertNotIn('id',c);self.assertNotIn('all_ids',c)
    self.assertTrue(c['requires_live_uniqueness']);self.assertFalse(c['runtime_verified'])
 def test_unmodeled_uikit_and_dynamic_modal_are_explicit_unknowns(self):
  with (self.src/'Main.swift').open('a') as f:f.write('''
import UIKit
class Controller:UIViewController {func open(){present(UIAlertController(title:"Q",message:nil,preferredStyle:.alert),animated:true)}}
struct Dynamic:View {var target:AnyView;@State var show=false;var body:some View {Text("X").sheet(isPresented:$show){target}}}
''')
  source,facts=self.source();catalog=P.native_catalog(source,facts,'org.hmigbot.neutral')
  self.assertEqual(catalog['status'],'partial_unknowns');self.assertTrue(catalog['unsupported_constructs'])
  self.assertTrue(all(r.get('file') and r.get('line') for r in catalog['unsupported_constructs']))
 def test_malformed_source_cannot_produce_a_catalog(self):
  (self.src/'Main.swift').write_text('struct Incomplete { func broken( {')
  with self.assertRaises(MigrationError):self.source()
 def test_cli_help_and_legacy_filename_are_explicit(self):
  script=ROOT/'skills/arkts-visual-verify/scripts/extract_dialog_ids.py'
  help_result=subprocess.run([sys.executable,'-B',str(script),'--help'],cwd=self.project,capture_output=True,text=True)
  self.assertEqual(help_result.returncode,0,help_result.stderr);self.assertIn('--ios-root',help_result.stdout)
  with self.assertRaises(MigrationError):P.catalog_cli(['--ios-root',str(self.src),'--package','org.hmigbot.neutral',
    '--out',str(self.root/'dialog_id_catalog.json'),'--project-root',str(self.project)])
  with self.assertRaises(MigrationError):P.catalog_cli(['--ios-root',str(self.src),'--package','org.hmigbot.neutral',
    '--out',str(self.root/'native_dialog_catalog.json'),'--layout-pattern','*'])
  output=self.root/'native_dialog_catalog.json'
  with redirect_stdout(io.StringIO()):code=P.catalog_cli(['--ios-root',str(self.src),'--package','org.hmigbot.neutral',
    '--out',str(output),'--project-root',str(self.project)])
  self.assertEqual(code,0);self.assertFalse(read_json(output)['runtime_verified'])
 def test_original_anchor_algorithm_diff_and_canonical_field_conservation(self):
  tree={'source':{'platform':'ios','ios_root':str(self.src)},'pages':[
    {'id':'NeutralView','fq_class':'NeutralView','functional_checks':[{'name':'A','ios_trusted':False,'expected_ios':None}]},
    {'id':'Unmatched','fq_class':'Unmatched'}],'fragments':[],'dialogs':[]}
  path=self.project/'spec/toolkit-fact-tree.json';write_json(path,tree)
  draft=self.project/'spec/.cache/fact-tree/draft.json';write_json(draft,tree)
  md=self.project/'spec/baseline/ui';md.mkdir(parents=True)
  doc='# page_0000_NeutralView: Neutral\n\n```yaml\nsource_anchors:\n  Alias0: "Main.swift"\n```\n'
  (md/'page_0000_NeutralView.md').write_text(doc)
  with redirect_stdout(io.StringIO()):code=P.enrich_cli(['--fact-tree',str(path),'--page-spec-dir',str(md),
    '--also-draft',str(draft),'--receipt',str(self.root/'receipt.json')],ROOT/'skills/arkts-visual-verify/scripts')
  self.assertEqual(code,0)
  result=read_json(path);expected=copy.deepcopy(tree)
  expected['pages'][0]['ios_source_refs']=[str((self.src/'Main.swift').resolve())]
  self.assertEqual(result,expected);self.assertEqual(read_json(draft),expected)
  self.assertEqual((md/'page_0000_NeutralView.md').read_text(),doc)
  # Independently call the original producer with its native Android-named inputs.
  original=copy.deepcopy(tree);original['source']['android_root']=str(self.src)
  raw=self.root/'raw.json';write_json(raw,original);legacy=self.root/'legacy';legacy.mkdir()
  (legacy/'page_0000_NeutralView.md').write_text(doc.replace('source_anchors:','android_source_anchors:'))
  oracle=execute('enrich_factree_anchors',['--fact-tree',str(raw),'--page-spec-dir',str(legacy),
      '--also-draft',str(self.root/'absent')],ROOT/'skills/arkts-visual-verify/scripts',cwd=self.root,capture_output=True)
  self.assertEqual(oracle.returncode,0,oracle.stderr)
  self.assertEqual(read_json(raw)['pages'][0]['android_source_refs'],result['pages'][0]['ios_source_refs'])
  before=copy.deepcopy(original);after=read_json(raw);after['pages'][0]['purpose']='Unpermitted mutation'
  source,_=self.source()
  with self.assertRaises(MigrationError):P.refs_result(before,after,source)
  after=read_json(raw);after['pages'][0]['android_source_refs']=['/outside/Unknown.swift']
  with self.assertRaises(MigrationError):P.refs_result(before,after,source)


if __name__=='__main__':unittest.main()
