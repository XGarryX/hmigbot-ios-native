"""Neutral SwiftSyntax facts, native verdicts and original engine regressions."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from hmigbot_ios.core import MigrationError
from hmigbot_ios152.source import Source
from hmigbot_ios152.native_routes import analyze,expected_nav,worklist,apply_verdicts
from hmigbot_ios152.native_routes_entry import normalize_manifest,target_blob,HMOS_INTERACTIVE,compiled,thin_shell
SCRIPTS=ROOT/'skills/arkts-router-verify/scripts'

SWIFT='''import SwiftUI
@main struct DemoApp: App { var body: some Scene { WindowGroup { HomeView() } } }
struct HomeView: View {
 @State var editing = false
 @State var confirming = false
 var body: some View {
  NavigationStack { VStack {
   NavigationLink("Open details") { DetailView() }
   Button("Edit item") { openEditor() }
   Button("Confirm action") { confirming = true }
  }.navigationDestination(isPresented: $editing) { EditorView() }
   .sheet(isPresented: $confirming) { ConfirmSheet(onConfirm: {}) }
  }
 }
 func openEditor() { editing = true }
}
struct DetailView: View { var body: some View { Text("Details") } }
struct EditorView: View { var body: some View { Text("Editor") } }
struct ConfirmSheet: View { var onConfirm: () -> Void; var body: some View { Button("Confirm") { onConfirm() } } }
'''


class NativeRoutes(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory(prefix='native-routes-check-');self.addCleanup(self.temp.cleanup)
  self.base=Path(self.temp.name);self.src=self.base/'source';self.src.mkdir();self.project=self.base/'hmos';self.project.mkdir()
  (self.project/'.agents').mkdir();self.out=self.project/'spec/verify/route';self.out.mkdir(parents=True)
 def source(self,text=SWIFT,name='Main.swift'):
  (self.src/name).write_text(text);return analyze(Source(self.src))
 def runstage(self,stage,*args):
  return subprocess.run([sys.executable,'-B',str(SCRIPTS/(stage+'.py')),*map(str,args)],cwd=self.project,
   env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1','ROUTE_VERIFY_ROOT':str(self.project),'ROUTE_VERIFY_OUT':str(self.out)},
   text=True,capture_output=True,timeout=120)
 def read(self,name):return json.loads((self.out/name).read_text())
 def extract(self,text=SWIFT):
  (self.src/'Main.swift').write_text(text)
  r=self.runstage('extract_nav_graph','--platform','ios','--ios-root',self.src)
  self.assertEqual(r.returncode,0,r.stdout+r.stderr);return self.read('expected_nav.json')
 def target(self):
  p=self.project/'entry/src/main/ets/pages';p.mkdir(parents=True)
  (p/'Index.ets').write_text("import { DetailPage } from './DetailPage'\n@Entry @Component struct Index { nav: NavPathStack = new NavPathStack(); @Builder map(name: string) { if(name === 'DetailPage') { DetailPage() } } build(){ Navigation(this.nav){ Button('Open details').onClick(()=>this.nav.pushPathByName('DetailPage',null)) }.navDestination(this.map) } }")
  (p/'DetailPage.ets').write_text("@Component export struct DetailPage { build(){ NavDestination(){ Text('Details') } } }")
  manifest=self.project/'spec/baseline/ui-manifest.md';manifest.parent.mkdir(parents=True,exist_ok=True)
  manifest.write_text('| 序号 | iOS | ArkTS 产出 | 优先级 | confidence | 状态 |\n|---|---|---|---|---|---|\n| 0000 | HomeView | `entry/src/main/ets/pages/Index.ets` | P0 | high | converted |\n| 0001 | DetailView | → entry/src/main/ets/pages/DetailPage.ets | P0 | high | converted |\n')
 def test_swift_static_graph_and_real_dialog_props(self):
  f=self.source();self.assertEqual({e['target'] for e in f['routes']},{'DetailView','EditorView','ConfirmSheet'})
  d=f['modals']['ConfirmSheet'];self.assertEqual(d['callbacks'][0]['name'],'onConfirm');self.assertEqual(d['controls'][0]['text'],'Confirm')
  self.assertIsNone(d['layout']);self.assertEqual(f['context']['launcher_short'],'DemoApp')
 def test_swift_helper_verdict_is_actually_applied(self):
  f=self.source();exp=expected_nav(f);wl=worklist(f,exp)
  self.assertEqual(wl['unique_methods'],1);self.assertEqual(wl['items'][0]['method_key'],'HomeView.openEditor()')
  with self.assertRaises(MigrationError):apply_verdicts(f,exp,wl,{})
  verdict={'method_verdicts':{'HomeView.openEditor()':{'keep':True,'nav_kind':'page_nav','note':'Actual helper changes editing'}}}
  nav,full=apply_verdicts(f,exp,wl,verdict)
  self.assertEqual(nav['coverage']['covered_methods'],1)
  edge=next(e for e in nav['edges'] if e['target']=='EditorView');self.assertEqual(edge['llm_note'],'Actual helper changes editing')
  self.assertEqual(full['stats_delta']['llm_page_nav'],1)
 def test_dynamic_navigation_is_a_real_work_item(self):
  f=self.source('import SwiftUI\nstruct Home: View { var destination: AnyView; var body: some View { NavigationLink("Dynamic", destination: destination) } }')
  self.assertEqual(len(f['routes']),1);self.assertIsNone(f['routes'][0]['target']);self.assertTrue(f['unknowns'])
  wl=worklist(f,expected_nav(f));self.assertEqual(wl['unique_methods'],1);self.assertIn('destination',wl['items'][0]['method_body'])
  verdict={'method_verdicts':{wl['items'][0]['method_key']:{'keep':False,'nav_kind':'ui_state','note':'reviewed external destination'}}}
  nav,_=apply_verdicts(f,expected_nav(f),wl,verdict);self.assertEqual(nav['count'],0)
 def test_no_navigation_is_legitimate(self):
  f=self.source('import SwiftUI\n@main struct AppRoot: App { var body: some Scene { WindowGroup { Home() } } }\nstruct Home: View { var body: some View { Text("Offline") } }')
  exp=expected_nav(f);wl=worklist(f,exp);nav,_=apply_verdicts(f,exp,wl,{})
  self.assertEqual(nav['count'],0);self.assertEqual(nav['coverage']['flag_methods'],0)
 def test_overloads_and_extensions_keep_distinct_real_keys(self):
  f=self.source('''import UIKit
class Home: UIViewController { func open(_ c: Detail) { show(c, sender:nil) }; func open(named c: Editor) { show(c,sender:nil) } }
extension Home { func showNext() { present(Detail(), animated:true) } }
class Detail: UIViewController {}
class Editor: UIViewController {}
''')
  keys=set(f['methods']);self.assertIn('Home.open(_:Detail)',keys);self.assertIn('Home.open(named:Editor)',keys);self.assertIn('Home.showNext()',keys)
  wl=worklist(f,expected_nav(f));self.assertEqual(wl['unique_methods'],3)
 def test_modal_families_and_tabs_are_not_dropped(self):
  f=self.source('''import SwiftUI
struct Home: View { @State var yes=false; var body:some View { TabView { A().tabItem { Text("A") }; B().tabItem{Text("B")} }.sheet(isPresented:$yes){ A() }.fullScreenCover(isPresented:$yes){ B() }.popover(isPresented:$yes){ A() }.alert("Question",isPresented:$yes){Button("OK") {}}.confirmationDialog("Choose",isPresented:$yes){Button("Pick") {}} } }
struct A:View {var body:some View{Text("A")}}
struct B:View {var body:some View{Text("B")}}
''')
  self.assertTrue({'sheet','fullScreenCover','popover','alert','confirmationDialog'}<={r['via'] for r in f['routes']})
  self.assertFalse(any(r['via']=='TabView' for r in f['routes']))
  self.assertEqual(len(f['tab_groups'][0]['tabs']),2)
  self.assertEqual([item['label'] for item in f['native_tab_groups'][0]['items']],['A','B'])
  alert=next(d for k,d in f['modals'].items() if '.alert@' in k)
  self.assertEqual([c['text'] for c in alert['controls']],['OK'])
  confirmation=next(d for k,d in f['modals'].items() if '.confirmationDialog@' in k)
  self.assertEqual([c['text'] for c in confirmation['controls']],['Pick'])
 def test_uikit_and_storyboard_declarations(self):
  (self.src/'Main.storyboard').write_text('''<document initialViewController="a"><scenes><scene><objects><viewController id="a" customClass="Home"><view><button id="btn"><state title="Next"/></button></view><connections><segue destination="b" identifier="details" kind="show" id="s1"/></connections></viewController><viewController id="b" customClass="Detail"/></objects></scene></scenes></document>''')
  f=self.source('''import UIKit
class Home:UIViewController {func next() {let d=Detail();navigationController?.pushViewController(d,animated:true);present(Detail(),animated:true);show(Detail(),sender:nil);performSegue(withIdentifier:"details",sender:nil);window.rootViewController = Detail()}}
class Detail:UIViewController {}
''')
  routes=f['routes'];self.assertTrue({'pushViewController','present','show','performSegue','rootViewController','storyboard.segue'}<={r['via'] for r in routes})
  self.assertEqual(next(r for r in routes if r['via']=='performSegue')['target'],'Detail')
  self.assertEqual(f['storyboard_initial'][0]['controller'],'Home')
  self.assertTrue(any(c['type']=='UIButton' and c['text']=='Next' for c in f['controls']))
 def test_missing_source_preserves_prior_report(self):
  self.extract();before=(self.out/'expected_nav.json').read_bytes();shutil.rmtree(self.src)
  for name in ['extract_nav_graph','llm_worklist','android_dialog_probe','thin_shell_probe']:
   r=self.runstage(name,'--ios-root',self.src);self.assertEqual(r.returncode,2,r.stdout+r.stderr)
   self.assertEqual((self.out/'expected_nav.json').read_bytes(),before)
  self.assertFalse((self.out/'dialog_specs.json').exists())
 def test_source_change_rejects_stale_worklist_and_reports(self):
  self.extract();self.assertEqual(self.runstage('llm_worklist').returncode,0)
  (self.src/'Main.swift').write_text(SWIFT.replace('Edit item','Edit another'))
  r=self.runstage('apply_llm');self.assertEqual(r.returncode,2);self.assertIn('identity changed',r.stderr);self.assertFalse((self.out/'nav_edges.json').exists())
 def test_mapping_wrappers_preserve_project_and_old_comparator(self):
  self.extract('import SwiftUI\nstruct HomeView:View { var body:some View {NavigationLink("Open details"){DetailView()}}}\nstruct DetailView:View{var body:some View{Text("Details")}}')
  self.target();manifest=self.project/'spec/baseline/ui-manifest.md';before=manifest.read_bytes()
  for stage in ['llm_worklist','apply_llm','hmos_extract','build_page_mapping','build_report','diff_routes','hmos_reachability']:
   r=self.runstage(stage);self.assertEqual(r.returncode,0,r.stdout+r.stderr)
  self.assertEqual(manifest.read_bytes(),before);mapping=self.read('page_mapping.json')['page_mapping']
  self.assertEqual([r['hmos_page'] for r in mapping],['Index','DetailPage']);self.assertTrue(all(r['spec_status']=='converted' for r in mapping))
  self.assertTrue((self.out/'diff_routes.native-input.json').exists())
 def test_api_evidence_is_the_real_modifier_name_token(self):
  f=self.source();edge=next(e for e in f['routes'] if e['via']=='sheet')
  line=next(i for i,text in enumerate(SWIFT.splitlines(),1) if '.sheet(' in text)
  self.assertEqual(edge['evidence_line'],line)
  self.assertEqual(SWIFT[edge['api_span']['start']:edge['api_span']['end']],'sheet')
 def test_nested_types_keep_qualified_owners(self):
  f=self.source('import SwiftUI\nenum Screens { struct Home:View {var body:some View {NavigationLink("Next"){Detail()}}};struct Detail:View{var body:some View{Text("Detail")}} }')
  edge=f['routes'][0];self.assertEqual(edge['source'],'Screens.Home');self.assertEqual(edge['target'],'Screens.Detail')
 def test_objc_markers_share_the_real_enclosing_method_unit(self):
  f=self.source('@interface Home:UIViewController @end\n@implementation Home\n- (void)open { [self.navigationController pushViewController:next animated:YES];\n [self presentViewController:next animated:YES completion:nil]; }\n@end',name='Home.m')
  self.assertEqual(len(f['routes']),2);wl=worklist(f,expected_nav(f));self.assertEqual(wl['unique_methods'],1)
  self.assertIn('pushViewController',wl['items'][0]['method_body']);self.assertIn('Home.-open',wl['items'][0]['method_key'])
  self.assertTrue(any('Objective-C' in u['reason'] for u in f['unknowns']))
 def test_ib_declaration_has_real_element_span(self):
  xml='<document initialViewController="a">\n<viewController id="a" customClass="Home"><connections>\n<segue id="go" destination="b" kind="show"/></connections></viewController>\n<viewController id="b" customClass="Detail"/></document>'
  (self.src/'Main.storyboard').write_text(xml)
  f=self.source('import UIKit\nclass Home:UIViewController{}\nclass Detail:UIViewController{}')
  edge=next(e for e in f['routes'] if e['via']=='storyboard.segue');self.assertEqual(edge['line'],3)
  self.assertEqual(xml[edge['start']:edge['end']],'<segue id="go" destination="b" kind="show"/>')
 def test_true_unique_method_coverage_85_percent(self):
  methods='\n'.join('func route'+str(i)+'() {show(Detail(),sender:nil)}' for i in range(20))
  f=self.source('import UIKit\nclass Home:UIViewController { '+methods+' }\nclass Detail:UIViewController {}')
  exp=expected_nav(f);wl=worklist(f,exp);keys=sorted({i['method_key'] for i in wl['items']})
  self.assertEqual(wl['unique_methods'],20)
  def verdict(n):return {'method_verdicts':{k:{'keep':True,'nav_kind':'page_nav','note':'actual source method'} for k in keys[:n]}}
  with self.assertRaises(MigrationError):apply_verdicts(f,exp,wl,verdict(16))
  nav,_=apply_verdicts(f,exp,wl,verdict(17));self.assertEqual(nav['coverage']['ratio'],.85)
 def test_navigation_path_dynamic_append_is_not_silently_lost(self):
  f=self.source('import SwiftUI\nstruct Home:View { @State var path=NavigationPath(); var body:some View {NavigationStack(path:$path){Button("Next"){path.append(5)}}} }')
  edge=next(e for e in f['routes'] if e['via']=='NavigationPath.append')
  self.assertIsNone(edge['target']);self.assertEqual(worklist(f,expected_nav(f))['unique_methods'],1)
 def test_thin_positive_preserves_original_target_count_and_missing_not_green(self):
  buttons='\n'.join('Button("Missing'+str(i)+'"){}' for i in range(28))
  self.extract('import SwiftUI\nstruct HomeView:View {var body:some View{VStack{'+buttons+'}}}\nstruct DetailView:View{var body:some View{Text("Details")}}')
  self.target()
  (self.project/'entry/src/main/ets/pages/DetailPage.ets').write_text("@Component export struct DetailPage {build(){NavDestination(){Button('Imported').onClick(()=>{})}}}")
  for stage in ['llm_worklist','apply_llm','hmos_extract','build_page_mapping','hmos_reachability','thin_shell_probe']:
   r=self.runstage(stage);self.assertEqual(r.returncode,0,r.stdout+r.stderr)
  report=self.read('thin_shell_report.json');finding=report['findings'][0]
  self.assertEqual(report['thin_shells'],1);self.assertEqual(finding['android_interactive'],28);self.assertEqual(finding['hmos_interactive'],4)
  blob,paths,reason=target_blob(self.project,'Index');self.assertIsNone(reason)
  self.assertEqual(finding['hmos_interactive'],sum(blob.count(t) for t in HMOS_INTERACTIVE))
  # Original Kotlin input, same target text, establishes the old counter independently.
  source=self.base/'kotlin';java=source/'app/src/main/java/com/neutral';java.mkdir(parents=True)
  for i in range(6):(java/('Page'+str(i)+'Activity.kt')).write_text('package com.neutral\nimport android.app.Activity\nclass Page'+str(i)+'Activity : Activity() { fun view() {setContentView(R.layout.home)} }')
  layouts=source/'app/src/main/res/layout';layouts.mkdir(parents=True)
  (layouts/'home.xml').write_text('<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android">'+''.join('<Button android:id="@+id/b'+str(i)+'" android:text="x"/>' for i in range(28))+'</LinearLayout>')
  legacy=self.base/'old-thin';legacy.mkdir()
  (legacy/'expected_nav.json').write_text(json.dumps({'android_root':str(source),'first_party_pkgs':['/com/neutral/','com.neutral'],'edges':[]}))
  (legacy/'reachability_robust.json').write_text(json.dumps({'pages':[{'android_page':'Page0Activity','hmos_page':'Index','layer':'wired_entry','struct_exists':True}]}))
  r=compiled(SCRIPTS,'thin_shell_probe',env={'ROUTE_VERIFY_ROOT':str(self.project),'ROUTE_VERIFY_OUT':str(legacy)})
  self.assertEqual(r.returncode,0,r.stdout+r.stderr)
  original=json.loads((legacy/'thin_shell_report.json').read_text())
  self.assertTrue(original['findings'],r.stdout+r.stderr+str(original))
  self.assertEqual(original['findings'][0]['hmos_interactive'],finding['hmos_interactive'])
  before=(self.out/'thin_shell_report.json').read_bytes()
  (self.project/'entry/src/main/ets/pages/Index.ets').unlink()
  r=self.runstage('thin_shell_probe');self.assertEqual(r.returncode,2,r.stdout+r.stderr)
  self.assertEqual((self.out/'thin_shell_report.json').read_bytes(),before)
  self.assertEqual(self.read('thin_shell_incomplete.json')['status'],'incomplete')
 def test_dialog_wrapper_respects_applied_verdicts_and_real_props(self):
  self.extract();self.assertEqual(self.runstage('llm_worklist').returncode,0)
  wl=self.read('llm_worklist.json');verdicts={'method_verdicts':{i['method_key']:{'keep':True,'nav_kind':'page_nav','note':'real helper'} for i in wl['items']}}
  (self.out/'llm_verdicts.json').write_text(json.dumps(verdicts))
  self.assertEqual(self.runstage('apply_llm').returncode,0)
  r=self.runstage('ios_dialog_probe');self.assertEqual(r.returncode,0,r.stdout+r.stderr)
  dialog=self.read('dialog_specs.json')['dialogs']['ConfirmSheet'];self.assertEqual(dialog['callbacks'][0]['name'],'onConfirm')
  self.assertEqual(dialog['controls'][0]['text'],'Confirm')
 def test_manifest_absence_keeps_original_fallback(self):
  self.extract('import SwiftUI\nstruct HomeView:View {var body:some View{NavigationLink("Next"){DetailView()}}}\nstruct DetailView:View{var body:some View{Text("Detail")}}')
  self.target();(self.project/'spec/baseline/ui-manifest.md').unlink()
  for stage in ['llm_worklist','apply_llm','hmos_extract']:
   r=self.runstage(stage);self.assertEqual(r.returncode,0,r.stdout+r.stderr)
  prior=self.base/'original-map';shutil.copytree(self.out,prior)
  original=compiled(SCRIPTS,'build_page_mapping',env={'ROUTE_VERIFY_ROOT':str(self.project),'ROUTE_VERIFY_OUT':str(prior)})
  adapted=self.runstage('build_page_mapping');self.assertEqual(adapted.returncode,original.returncode,adapted.stdout+adapted.stderr+original.stdout+original.stderr)
  if original.returncode==0:
   self.assertEqual(self.read('page_mapping.json'),json.loads((prior/'page_mapping.json').read_text()))
   self.assertEqual(self.read('build_page_mapping.native-input.json')['manifest_notes'][0]['reason'],'manifest_absent')
 def test_adjudicated_dynamic_null_reaches_original_consumers(self):
  self.extract('import SwiftUI\nstruct HomeView:View {var destination:AnyView;var body:some View {NavigationLink("Dynamic",destination:destination)}}\nstruct DetailView:View{var body:some View{Text("Detail")}}')
  self.target();self.assertEqual(self.runstage('llm_worklist').returncode,0)
  wl=self.read('llm_worklist.json');rules={i['method_key']:{'keep':True,'nav_kind':'page_nav','note':'runtime-selected source destination remains unknown'} for i in wl['items']}
  (self.out/'llm_verdicts.json').write_text(json.dumps({'target_rules':{},'method_verdicts':rules}))
  for stage in ['apply_llm','hmos_extract','build_page_mapping','build_report','diff_routes','hmos_reachability','ios_dialog_probe','build_fix_plan']:
   r=self.runstage(stage);self.assertEqual(r.returncode,0,stage+r.stdout+r.stderr)
  nav=self.read('nav_edges.json');self.assertEqual(nav['unresolved_or_dynamic'],1);self.assertIsNone(nav['edges'][0]['target'])
  self.assertTrue(nav['unknowns']);self.assertIn('runtime-selected',nav['edges'][0]['llm_note'])
 def test_uikit_alert_content_unknown_is_explicit_not_false_complete(self):
  f=self.source('import UIKit\nclass Home:UIViewController {func open(){let a=UIAlertController(title:"Question",message:"Message",preferredStyle:.alert);a.addAction(UIAlertAction(title:"OK",style:.default){_ in});present(a,animated:true)}}')
  self.assertTrue(f['modals']['UIAlertController']['unsupported_content'])
  wl=worklist(f,expected_nav(f));self.assertEqual(wl['unique_methods'],1)
  self.assertIn('UIAlertAction',wl['items'][0]['method_body']);self.assertTrue(f['unknowns'])
 def test_dynamic_modal_is_partial_evidence_and_not_silently_empty(self):
  self.extract('import SwiftUI\nstruct Home:View {@State var show=false;var destination:AnyView;var body:some View{Button("Open"){show=true}.sheet(isPresented:$show){destination}}}')
  self.assertEqual(self.runstage('llm_worklist').returncode,0);wl=self.read('llm_worklist.json')
  rules={i['method_key']:{'keep':True,'nav_kind':'dialog','note':'runtime modal retained as unknown'} for i in wl['items']}
  (self.out/'llm_verdicts.json').write_text(json.dumps({'target_rules':{},'method_verdicts':rules}))
  self.assertEqual(self.runstage('apply_llm').returncode,0)
  r=self.runstage('ios_dialog_probe');self.assertEqual(r.returncode,0,r.stdout+r.stderr)
  spec=self.read('dialog_specs.json');self.assertEqual(spec['status'],'partial_unknowns');self.assertEqual(len(spec['unresolved_modal_routes']),1)
 def test_selected_resource_contract_excludes_other_product_files(self):
  (self.src/'Main.swift').write_text('import SwiftUI\nstruct Home:View{var body:some View{Text("Selected")}}')
  (self.src/'Selected.strings').write_text('"Selected" = "Included value";')
  (self.src/'Selected.plist').write_text('<?xml version="1.0"?><plist version="1.0"><dict/></plist>')
  (self.src/'Other.strings').write_text('"NotSelected" = "Other product value";')
  (self.src/'Other.storyboard').write_text('<document initialViewController="o"><viewController id="o" customClass="OtherProduct"><connections><segue id="s" destination="o" kind="show"/></connections></viewController></document>')
  scope={'files':['Selected.strings','Selected.plist'],'scope':'selected-product-targets','evidence':'test selected-resource contract','owners':{'Selected.strings':['MainApp']},
   'issues':[{'reason':'synchronized_resource_format_subset'}],'excluded':[{'file':'Other.strings'},{'file':'Other.storyboard'}]}
  def facts():
   source=Source(self.src);source._native_resources=scope;return analyze(source)
  f=facts();self.assertIn('Selected',f['localization']);self.assertNotIn('NotSelected',f['localization'])
  self.assertFalse(any(p['name']=='OtherProduct' for p in f['pages']));self.assertFalse(f['routes'])
  self.assertEqual(f['resource_scope']['issues'],scope['issues']);self.assertEqual(worklist(f,expected_nav(f))['count'],0)
  (self.src/'Other.strings').write_text('"NotSelected" = "Changed excluded value";')
  self.assertEqual(f['source_sha'],facts()['source_sha'])
  (self.src/'Selected.plist').write_text('<?xml version="1.0"?><plist version="1.0"><dict><key>Selected</key><string>Changed</string></dict></plist>')
  self.assertNotEqual(f['source_sha'],facts()['source_sha'])
 def test_swiftui_accessibility_applies_only_to_its_direct_base(self):
  text='''import SwiftUI
struct Home:View {var dynamicId:String;var body:some View {VStack {
 Button("One"){}.id("not-accessibility")
 Button("Two"){}.accessibilityIdentifier("second").accessibilityLabel(Text("Second label"))
 Button("Three"){}.accessibilityIdentifier(dynamicId)
}.accessibilityIdentifier("container")}}
'''
  f=self.source(text);buttons={c['text']:c for c in f['controls'] if c['type']=='Button'}
  self.assertIsNone(buttons['One']['accessibility_identifier'])
  self.assertEqual(buttons['Two']['accessibility_identifier'],'second');self.assertEqual(buttons['Two']['accessibility_label'],'Second label')
  self.assertEqual(next(c for c in f['controls'] if c['type']=='VStack')['accessibility_identifier'],'container')
  self.assertIsNone(buttons['Three']['accessibility_identifier']);self.assertTrue(buttons['Three']['accessibility_identifier_dynamic'])
  self.assertTrue(any(u['reason']=='dynamic accessibility_identifier' for u in f['unknowns']))
  self.assertEqual(worklist(f,expected_nav(f))['unique_methods'],0)
  span=buttons['Two']['accessibility_identifier_value_span'];self.assertEqual(text[span['start']:span['end']], '"second"')
 def test_uikit_accessibility_assignment_literal_and_dynamic(self):
  f=self.source('''import UIKit
class Home:UIViewController {let button=UIButton(type:.system);let secondary=UIButton()
 func setup(){button.accessibilityIdentifier="primary";secondary.accessibilityIdentifier="prefix"+suffix;button.accessibilityLabel="Button label";button.setTitle("Title",for:.normal)}}
''')
  buttons={c.get('variable'):c for c in f['controls'] if c['type']=='UIButton'}
  self.assertEqual(buttons['button']['accessibility_identifier'],'primary');self.assertEqual(buttons['button']['accessibility_label'],'Button label')
  self.assertIsNone(buttons['secondary']['accessibility_identifier']);self.assertTrue(buttons['secondary']['accessibility_identifier_dynamic'])
  self.assertEqual(buttons['button']['text'],'Title')
 def test_uikit_accessibility_member_resolves_across_extension_file(self):
  (self.src/'Extension.swift').write_text('import UIKit\nextension Home {func setup(){button.accessibilityIdentifier="from-extension"}}')
  f=self.source('import UIKit\nclass Home:UIViewController{let button=UIButton()}')
  button=next(c for c in f['controls'] if c['type']=='UIButton');self.assertEqual(button['accessibility_identifier'],'from-extension')
  self.assertEqual(button['accessibility_identifier_evidence']['file'],'Extension.swift')
 def test_conflicting_accessibility_values_remain_unknown(self):
  f=self.source('import UIKit\nclass Home:UIViewController{let button=UIButton();func a(){button.accessibilityIdentifier="first"};func b(){button.accessibilityIdentifier="second"}}')
  button=next(c for c in f['controls'] if c['type']=='UIButton');self.assertIsNone(button['accessibility_identifier'])
  self.assertTrue(button['accessibility_identifier_dynamic']);self.assertEqual(len(button['accessibility_identifier_assignments']),2)
 def test_ib_outlet_accessibility_merges_without_duplicate_control(self):
  (self.src/'Main.storyboard').write_text('<document initialViewController="a"><viewController id="a" customClass="Home"><view><button id="b"/></view><connections><outlet property="button" destination="b" id="o"/></connections></viewController></document>')
  f=self.source('import UIKit\nclass Home:UIViewController{func setup(){button.accessibilityIdentifier="from-code"}\n@IBOutlet var button:UIButton!}')
  buttons=[c for c in f['controls'] if c['type']=='UIButton'];self.assertEqual(len(buttons),1)
  self.assertEqual(buttons[0]['id'],'b');self.assertEqual(buttons[0]['accessibility_identifier'],'from-code');self.assertIn('source_declaration',buttons[0])
 def thin_fixture(self,facts,target_value="Widget phrase"):
  target=self.project/'entry/src/main/ets/pages/Index.ets';target.parent.mkdir(parents=True,exist_ok=True)
  target.write_text("@Entry @Component struct Index {build(){Button($r('app.string.renamed'))}}")
  resource=self.project/'entry/src/main/resources/base/element/string.json';resource.parent.mkdir(parents=True,exist_ok=True)
  resource.write_text(json.dumps({'string':[{'name':'renamed','value':target_value}]}))
  (self.out/'page_mapping.json').write_text(json.dumps({'page_mapping':[{'android_page':'HomeView','hmos_page':'Index','spec_status':'converted'}]}))
  (self.out/'reachability_robust.json').write_text(json.dumps({'pages':[{'android_page':'HomeView','hmos_page':'Index','layer':'wired_entry','struct_exists':True}]}))
  return thin_shell(facts,self.project,self.out)
 def localization_products(self,app_key=True,shared_source=False):
  code='import SwiftUI\nstruct HomeView:View{var body:some View{VStack{'+'\n'.join('Button("source_key"){}' for _ in range(6))+'}}}'
  (self.src/'App.swift').write_text(code);(self.src/'Widget.swift').write_text('import SwiftUI\nstruct WidgetView:View{var body:some View{Text("Widget")}}')
  objects={'P':{'isa':'PBXProject','mainGroup':'G','projectDirPath':'','targets':['T1','T2'],'buildConfigurationList':'CL'},
   'G':{'isa':'PBXGroup','sourceTree':'<group>','children':['F1','F2','R1','R2']},
   'CL':{'isa':'XCConfigurationList','buildConfigurations':['C']},'C':{'isa':'XCBuildConfiguration','name':'Release','buildSettings':{}}}
  for n,name,phrase in [('1','App','App phrase'),('2','Widget','Widget phrase')]:
   objects['T'+n]={'isa':'PBXNativeTarget','name':name,'productType':'com.apple.product-type.application' if n=='1' else 'com.apple.product-type.app-extension','buildConfigurationList':'CL','buildPhases':['S'+n,'RP'+n],'dependencies':[]}
   objects['S'+n]={'isa':'PBXSourcesBuildPhase','files':['B'+n]+(['SH'] if n=='2' and shared_source else [])}
   objects['B'+n]={'isa':'PBXBuildFile','fileRef':'F'+n};objects['F'+n]={'isa':'PBXFileReference','sourceTree':'<group>','path':name+'.swift'}
   objects['RP'+n]={'isa':'PBXResourcesBuildPhase','files':['RB'+n]};objects['RB'+n]={'isa':'PBXBuildFile','fileRef':'R'+n}
   objects['R'+n]={'isa':'PBXFileReference','sourceTree':'<group>','path':name+'.xcstrings'}
   (self.src/(name+'.xcstrings')).write_text(json.dumps({'strings':{'source_key':{'localizations':{'en':{'stringUnit':{'value':phrase}}}}} if app_key or n=='2' else {}}))
  if shared_source:objects['SH']={'isa':'PBXBuildFile','fileRef':'F1'}
  pbx=self.src/'Neutral.xcodeproj/project.pbxproj';pbx.parent.mkdir();pbx.write_text(json.dumps({'objects':objects,'rootObject':'P'}))
  variant={'scope':'project-targets','project_path':'Neutral.xcodeproj/project.pbxproj','targets':['App','Widget'],'configuration':'Release'}
  config=self.project/'.migbot/config.json';config.parent.mkdir();config.write_text(json.dumps({'source_platform':'ios','ios':{'source_root':str(self.src),'variant':variant}}))
  return analyze(Source(self.src,self.project))
 def test_tool_managed_target_files_do_not_poison_census(self):
  f=self.source('import SwiftUI\nstruct HomeView:View{var body:some View{VStack{'+'\n'.join('Button("source_key"){}' for _ in range(6))+'}}}')
  before,code=self.thin_fixture(f,target_value='Other real value');self.assertEqual(code,0)
  for directory in ['.agents','.codex','.hmigbot-ios','.migbot']:
   fake=self.project/directory/'template/Index.ets';fake.parent.mkdir(parents=True,exist_ok=True)
   (fake.parent/'string.json').write_text(json.dumps({'string':[{'name':'renamed','value':'source_key'}]}))
  strings_only,code=thin_shell(f,self.project,self.out);self.assertEqual(code,0)
  self.assertEqual(strings_only['findings'][0]['string_overlap'],0)
  for directory in ['.agents','.codex','.hmigbot-ios','.migbot']:
   fake=self.project/directory/'template/Index.ets';fake.write_text('@Component struct Index {build(){'+''.join('Button("source_key"){}' for _ in range(10))+'}}')
  after,code=thin_shell(f,self.project,self.out);self.assertEqual(code,0)
  self.assertEqual(after['findings'][0]['hmos_interactive'],before['findings'][0]['hmos_interactive'])
  self.assertEqual(after['findings'][0]['string_overlap'],before['findings'][0]['string_overlap']);self.assertEqual(after['thin_shells'],1)
  audit=after['target_scope'];self.assertEqual(audit['strings']['excluded_file_count'],4)
  self.assertEqual(audit['ets_by_page']['HomeView']['excluded_file_count'],4)
 def test_two_real_target_declarations_remain_ambiguous(self):
  self.target();extra=self.project/'feature/src/main/ets/Index.ets';extra.parent.mkdir(parents=True);extra.write_text('@Component struct Index {build(){Text("User")}}')
  audit={};blob,paths,reason=target_blob(self.project,'Index',audit)
  self.assertIsNone(blob);self.assertEqual(reason,'ambiguous_hmos_declaration');self.assertEqual(len(audit['matched_declarations']),2)
 def test_widget_localization_cannot_fill_a_missing_app_value(self):
  f=self.localization_products(app_key=False);self.assertEqual(f['source_product_owners']['App.swift'],['App'])
  self.assertEqual(f['localization']['source_key'],['Widget phrase'])
  record=f['localization_records'][0];self.assertEqual(record['product_owners'],['Widget']);self.assertEqual(record['locale'],'en')
  report,code=self.thin_fixture(f);self.assertEqual(code,0);finding=report['findings'][0]
  self.assertEqual(finding['string_overlap'],0);self.assertTrue(finding['thin_shell'])
  self.assertTrue(any(n['reason']=='localization_not_declared_for_source_product' for n in finding['localization_notes']))
 def test_matching_app_localization_is_still_comparable(self):
  f=self.localization_products();report,code=self.thin_fixture(f,'App phrase');self.assertEqual(code,0)
  self.assertEqual(report['findings'][0]['string_overlap'],1);self.assertFalse(report['findings'][0]['thin_shell'])
 def test_shared_product_localization_conflict_stays_unknown(self):
  f=self.localization_products(shared_source=True);self.assertEqual(f['source_product_owners']['App.swift'],['App','Widget'])
  report,code=self.thin_fixture(f,'Widget phrase');self.assertEqual(code,0);finding=report['findings'][0]
  self.assertEqual(finding['string_overlap'],0);self.assertTrue(any(n['reason']=='conflicting_or_non_equivalent_product_localizations' for n in finding['localization_notes']))
  self.assertEqual(finding['localization_evidence_status'],'partial_unknowns')
 def test_unknown_product_does_not_borrow_localized_values_but_keeps_literal_comparison(self):
  (self.src/'All.xcstrings').write_text(json.dumps({'strings':{'source_key':{'localizations':{'en':{'stringUnit':{'value':'Widget phrase'}}}}}}))
  f=self.source('import SwiftUI\nstruct HomeView:View{var body:some View{VStack{'+'\n'.join('Button("source_key"){}' for _ in range(6))+'}}}')
  report,code=self.thin_fixture(f);self.assertEqual(code,0);self.assertEqual(report['findings'][0]['string_overlap'],0)
  self.assertTrue(any(n['reason']=='source_product_ownership_unknown' for n in report['localization_unknowns']))
  target=self.project/'entry/src/main/ets/pages/Index.ets';target.write_text("@Entry @Component struct Index{build(){Button($r('app.string.source_key'))}}")
  (self.project/'entry/src/main/resources/base/element/string.json').write_text(json.dumps({'string':[{'name':'source_key','value':'A literal key remains comparable'}]}))
  report,code=thin_shell(f,self.project,self.out);self.assertEqual(code,0);self.assertEqual(report['findings'][0]['string_overlap'],1)
 def test_native_tab_wire_matches_original_group_contract_and_preserves_evidence(self):
  f=self.source('''import SwiftUI
struct Root:View {var body:some View {TabView {
 NavigationStack{ThirdView()}.tabItem{Label("Third actual",systemImage:"3.circle")}.tag(3)
 FirstView().tabItem{Text(LocalizedStringKey("first_key"))}.tag(1)
 SecondView().tabItem{Text("Second actual")}.tag(2)
}}}
struct FirstView:View{var body:some View{Text("One")}}
struct SecondView:View{var body:some View{Text("Two")}}
struct ThirdView:View{var body:some View{Text("Three")}}
''')
  exp=expected_nav(f);self.assertEqual(exp['tab_groups'],[{'host':'Root','file':'Main.swift','tabs':['ThirdView','FirstView','SecondView']}])
  self.assertEqual(exp['edges'],[]);self.assertEqual(exp['stats']['total_nav_sites'],0)
  items=f['native_tab_groups'][0]['items'];self.assertEqual([i['label'] for i in items],['Third actual','first_key','Second actual'])
  self.assertEqual([i['key_expression'] for i in items],['3','1','2'])
  self.assertTrue(all(i['source']['file']=='Main.swift' and i['label_anchors'] for i in items))
  wl=worklist(f,exp);self.assertEqual(wl['unique_methods'],0)
 def test_tab_dynamic_label_is_null_unknown_not_a_type_name(self):
  f=self.source('''import SwiftUI
struct Root:View {var title:String;var body:some View {TabView {
 FirstView().tabItem{Text(title)}
 SecondView().tabItem{Label("Actual second",systemImage:"2.circle")}
}}}
struct FirstView:View{var body:some View{Text("One")}}
struct SecondView:View{var body:some View{Text("Two")}}
''')
  self.assertIsNone(f['native_tab_groups'][0]['items'][0]['label'])
  self.assertTrue(any(u['reason']=='Tab label is dynamic or unavailable' for u in f['unknowns']))
  self.assertEqual(expected_nav(f)['edges'],[]);self.assertEqual(worklist(f,expected_nav(f))['count'],0)
 def test_single_tab_matches_original_no_group_contract(self):
  f=self.source('import SwiftUI\nstruct Root:View{var body:some View{TabView{FirstView().tabItem{Text("One")}}}}\nstruct FirstView:View{var body:some View{Text("First")}}')
  self.assertEqual(f['tab_groups'],[]);self.assertEqual(expected_nav(f)['edges'],[])
  self.assertEqual(f['native_tab_groups'][0]['members'],['FirstView'])
 def test_dynamic_and_anonymous_nested_tabs_are_not_flattened_or_silent(self):
  f=self.source('''import SwiftUI
struct Root:View {let items=[1,2];var body:some View {TabView {
 FirstView().tabItem{Text("One")}
 TabView {SecondView().tabItem{Text("Two")};ThirdView().tabItem{Text("Three")}}.tabItem{Text("Nested")}
 ForEach(items,id:\.self){_ in FirstView().tabItem{Text("Dynamic")}}
}}}
struct FirstView:View{var body:some View{Text("One")}}
struct SecondView:View{var body:some View{Text("Two")}}
struct ThirdView:View{var body:some View{Text("Three")}}
''')
  self.assertEqual(f['tab_groups'],[{'host':'Root','file':'Main.swift','tabs':['SecondView','ThirdView']}])
  outer=f['native_tab_groups'][0];self.assertEqual(outer['members'],['FirstView']);self.assertFalse(outer['wire_group_emitted'])
  self.assertTrue(any('ForEach' in u['reason'] for u in f['unknowns']));self.assertTrue(any('nested TabView' in u['reason'] for u in f['unknowns']))
  self.assertEqual(expected_nav(f)['edges'],[])
 def test_nonempty_native_tab_group_reaches_all_original_consumers(self):
  self.extract('''import SwiftUI
struct RootView:View{var body:some View{TabView {
 HomeView().tabItem{Text("Home")}
 DetailView().tabItem{Text("Details")}
}}}
struct HomeView:View{var body:some View{NavigationLink("Open details"){DetailView()}}}
struct DetailView:View{var body:some View{Text("Details")}}
''')
  self.target()
  # The original target parser must receive a real Tabs declaration, not a modified app.
  page=self.project/'entry/src/main/ets/pages/Index.ets'
  page.write_text("import { DetailPage } from './DetailPage'\n@Component struct HomePage{build(){Text('Home')}}\n@Entry @Component struct Index{build(){Tabs(){TabContent(){HomePage()}.tabBar('Home');TabContent(){DetailPage()}.tabBar('Details')}}}")
  manifest=self.project/'spec/baseline/ui-manifest.md';manifest.write_text('| 序号 | iOS | ArkTS 产出 | 优先级 | confidence | 状态 |\n| 0000 | RootView | Index.ets | P0 | high | converted |\n| 0001 | HomeView | HomePage.ets | P0 | high | converted |\n| 0002 | DetailView | DetailPage.ets | P0 | high | converted |\n')
  for stage in ['llm_worklist','apply_llm','hmos_extract','build_page_mapping','build_report','diff_routes','hmos_reachability','thin_shell_probe','ios_dialog_probe','build_fix_plan']:
   r=self.runstage(stage);self.assertEqual(r.returncode,0,stage+r.stdout+r.stderr)
  exp=self.read('expected_nav.json');self.assertEqual(exp['tab_groups'][0]['tabs'],['HomeView','DetailView'])
  self.assertEqual(exp['stats']['total_nav_sites'],1);self.assertEqual(self.read('nav_edges.json')['count'],1)
  self.assertNotIn('tab_groups',self.read('nav_edges.json'))
 def test_manifest_normalization_forms(self):
  for cell in ['Index.ets','`entry/pages/Index.ets`','→ entry/pages/Index.ets','[Index](entry/pages/Index.ets)']:
   text='| 0000 | Home | '+cell+' | P0 | high | converted |\n';normal,rows=normalize_manifest(text)
   self.assertIn('| Index.ets |',normal);self.assertEqual(rows[0]['original'],cell)
 def test_manifest_caption_requires_one_real_selected_owner(self):
  facts={'symbols':[{'name':'AlphaScreen','file':'Alpha.swift','line':2,'start':1,'kind':'struct'},
                    {'name':'Screens.Detail','file':'Detail.swift','line':4,'start':3,'kind':'struct'},
                    {'name':'A.Shared','file':'A.swift','line':1,'start':0,'kind':'struct'},
                    {'name':'B.Shared','file':'B.swift','line':1,'start':0,'kind':'struct'}]}
  cases=[('AlphaScreen（Overview）','AlphaScreen','decoded'),
         ('AlphaScreen (Overview)','AlphaScreen','decoded'),
         ('`AlphaScreen（Overview）`','AlphaScreen','decoded'),
         ('`AlphaScreen`（Overview）','AlphaScreen','decoded'),
         ('Screens.Detail（Detail）','Screens.Detail','decoded'),
         ('Detail（Detail）','Screens.Detail','decoded'),
         ('Shared（Common）','Shared（Common）','ambiguous'),
         ('Unknown（Missing）','Unknown（Missing）','unknown'),
         ('Other.Detail（Unknown namespace）','Other.Detail（Unknown namespace）','unknown'),
         ('AlphaScreen/Detail（Two types）','AlphaScreen/Detail（Two types）','multi_type'),
         ('AlphaScreen（One）,Screens.Detail（Two）','AlphaScreen（One）,Screens.Detail（Two）','multi_type'),
         ('AlphaScreen（Nested(x)）','AlphaScreen（Nested(x)）','unknown'),
         ('AlphaScreen.swift（Path）','AlphaScreen.swift（Path）','unknown'),
         ('prefix AlphaScreen（Free text）','prefix AlphaScreen（Free text）','unknown'),
         ('AlphaScreen','AlphaScreen','unchanged_exact')]
  for cell,owner,status in cases:
   with self.subTest(cell=cell):
    original='| 0000 | '+cell+' | `entry/pages/Index.ets` | P0 | high | converted |\n'
    normal,rows=normalize_manifest(original,facts)
    self.assertEqual(normal.split('|')[2].strip(),owner);info=rows[0]['source_identity']
    self.assertEqual(info['status'],status);self.assertEqual(info['original'],cell)
    if status=='decoded':self.assertIn('file',info['declaration']);self.assertIsNotNone(info['label'])
 def test_labelled_manifest_public_chain_preserves_original_and_owner_wire(self):
  self.extract('import SwiftUI\nstruct HomeView:View {var body:some View{NavigationLink("Open details"){DetailView()}}}\nstruct DetailView:View{var body:some View{Text("Details")}}')
  self.target();manifest=self.project/'spec/baseline/ui-manifest.md'
  manifest.write_text(manifest.read_text().replace('| HomeView |','| `HomeView`（Overview） |').replace('| DetailView |','| DetailView (Details) |'))
  before=manifest.read_bytes()
  for stage in ['llm_worklist','apply_llm','hmos_extract','build_page_mapping','build_report','diff_routes','hmos_reachability','thin_shell_probe','build_fix_plan']:
   r=self.runstage(stage);self.assertEqual(r.returncode,0,stage+r.stdout+r.stderr)
  self.assertEqual(manifest.read_bytes(),before)
  self.assertEqual([r['android_page'] for r in self.read('page_mapping.json')['page_mapping']],['HomeView','DetailView'])
  self.assertTrue(all(r['source_identity']['status']=='decoded' for r in self.read('build_page_mapping.native-input.json')['manifest_rows']))
  self.assertFalse(self.read('thin_shell_report.json')['skipped'])
 def test_legacy_android_wrapper_matches_original(self):
  java=self.src/'app/src/main/java/com/neutral';java.mkdir(parents=True)
  for i in range(6):
   body='fun open() { startActivity(Intent(this,Screen1::class.java)) }' if i==0 else ''
   (java/('Screen'+str(i)+'.kt')).write_text('package com.neutral\nimport android.app.Activity\nimport android.content.Intent\nclass Screen'+str(i)+': Activity() {'+body+'}')
  (self.src/'app/src/main/AndroidManifest.xml').write_text('<manifest xmlns:android="http://schemas.android.com/apk/res/android"><application><activity android:name="com.neutral.Screen0"/></application></manifest>')
  original=self.base/'original';adapted=self.base/'adapted'
  args=['--platform','android','--android-root',str(self.src),'--first-party-pkgs','/com/neutral/,com.neutral']
  old=compiled(SCRIPTS,'extract_nav_graph',[*args,'--out-dir',str(original)],{'ROUTE_VERIFY_ROOT':str(self.project)})
  new=self.runstage('extract_nav_graph',*args,'--out-dir',adapted)
  self.assertEqual(new.returncode,old.returncode,new.stderr+old.stderr);self.assertEqual(new.returncode,0,new.stderr+old.stderr)
  self.assertEqual(json.loads((original/'expected_nav.json').read_text()),json.loads((adapted/'expected_nav.json').read_text()))
  self.target()
  manifest=self.project/'spec/baseline/ui-manifest.md'
  manifest.write_text('| 序号 | Android | ArkTS 产出 | 优先级 | confidence | 状态 |\n| 0000 | Screen0 | Index.ets | P0 | high | converted |\n| 0001 | Screen1 | DetailPage.ets | P0 | high | converted |\n')
  verdict={'target_rules':{},'method_verdicts':{'Screen0.open':{'keep':True,'nav_kind':'page_nav','note':'Actual source helper'}}}
  for folder in [original,adapted]:(folder/'llm_verdicts.json').write_text(json.dumps(verdict))
  self.out=adapted
  for stage in ['llm_worklist','apply_llm','hmos_extract','build_page_mapping','build_report','diff_routes','hmos_reachability','thin_shell_probe','android_dialog_probe','build_fix_plan']:
   old=compiled(SCRIPTS,stage,env={'ROUTE_VERIFY_ROOT':str(self.project),'ROUTE_VERIFY_OUT':str(original),'RV_FIRST_PARTY_PKGS':'/com/neutral/,com.neutral'})
   new=self.runstage(stage)
   self.assertEqual(new.returncode,old.returncode,stage+new.stdout+new.stderr+old.stdout+old.stderr)
   self.assertEqual(new.returncode,0,stage+new.stdout+new.stderr)
  for old_path in original.glob('*.json'):
   self.assertEqual(old_path.read_bytes(),(adapted/old_path.name).read_bytes(),old_path.name)


if __name__=='__main__':unittest.main()
