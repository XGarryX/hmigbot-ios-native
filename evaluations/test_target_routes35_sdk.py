"""Real official ETS regressions for render-bound target route supplementation."""
from __future__ import annotations
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
import uuid

ROOT = Path(__file__).resolve().parents[1]
NODE = Path(os.environ.get('HMIGBOT_ETS_NODE', '/Applications/DevEco-Studio.app/Contents/tools/node/bin/node'))
PARSER = Path(os.environ.get('HMIGBOT_ETS_PARSER', '/Applications/DevEco-Studio.app/Contents/sdk/default/openharmony/ets/build-tools/ets-loader/node_modules/typescript/lib/typescript.js'))
if PARSER.is_dir():
    PARSER = PARSER / 'lib/typescript.js'
SDK = ROOT / 'src/hmigbot_ios152/target_routes_sdk.cjs'
QA = Path(os.environ.get('HMIGBOT_TEST_QA_ROOT', tempfile.gettempdir()))

@unittest.skipUnless(NODE.is_file() and PARSER.is_file(), 'selected official ETS runtime is unavailable')
class RenderBoundTargetFacts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        QA.mkdir(parents=True, exist_ok=True)
        cls.workspace = tempfile.TemporaryDirectory(prefix='sdk-cases-', dir=QA)
        cls.base = Path(cls.workspace.name)
        cls.counter = 0

    @classmethod
    def tearDownClass(cls):
        cls.workspace.cleanup()

    def fixture(self, members='', build="Text('Empty')", extra='', imports='', sources=None):
        type(self).counter += 1
        root = self.base / f'case{self.counter}'
        pages = root / 'entry/src/main/ets/pages'; pages.mkdir(parents=True)
        names = "@Component struct SheetPage{build(){Text('Sheet')}}\n@Component struct OtherPage{build(){Text('Other')}}\n@Component struct DetailPage{build(){Text('Detail')}}\n"
        (pages / 'Root.ets').write_text(imports + '\n' + names + extra + '\n@Entry @Component struct Root{' + members + ' build(){' + build + '} }\n')
        for rel, content in (sources or {}).items():
            p = root / rel; p.parent.mkdir(parents=True, exist_ok=True); p.write_text(content)
        return root

    def proof(self, root):
        payload = {'runId': uuid.uuid4().hex, 'project': str(root), 'files': [str(p) for p in sorted(root.rglob('*.ets'))],
                   'parserModule': str(PARSER), 'sdkSelection': {'test': 'explicit official SDK'}}
        p = subprocess.run([str(NODE), str(SDK)], input=json.dumps(payload), text=True, capture_output=True, timeout=60)
        try: out = json.loads(p.stdout)
        except ValueError: self.fail(p.stdout + p.stderr)
        self.assertEqual(p.returncode, 0, out.get('error', p.stderr))
        self.assertIs(out.get('valid'), True, out.get('error'))
        return out

    def overlays(self, root):
        return self.proof(root)['overlayBindings']

    def stack(self, extra=''):
        return "private stack:NavPathStack=new NavPathStack(); @Builder dest(name:string,param:Object){if(name==='DetailPage'){DetailPage()}} " + extra

    def navigation(self, body):
        return 'Navigation(this.stack){' + body + '}.navDestination(this.dest)'

    def test_call_form_sheet_builder(self):
        root = self.fixture('@State shown:boolean=false; @Builder sheet(){SheetPage()}', "Column(){Text('Body')}.bindSheet($$this.shown,this.sheet())")
        rows = self.overlays(root)
        self.assertEqual([(r['source'], r['target'], r['api']) for r in rows], [('Root', 'SheetPage', 'bindSheet')])
        self.assertTrue(any(a['kind'] == 'builder-call' for a in rows[0]['chain']))

    def test_trailing_builder_overrides_default_for_real_instance(self):
        child = "@Component struct Wrapper{@State shown:boolean=false; @Builder fallback(){OtherPage()} @BuilderParam content:()=>void=this.fallback; build(){Column(){}.bindSheet(this.shown,this.content)}}"
        root = self.fixture(build='Wrapper(){SheetPage()}', extra=child)
        rows = self.overlays(root)
        self.assertEqual([row['target'] for row in rows], ['SheetPage'])
        self.assertTrue(all('>' in value['instance'] for value in rows[0]['instance_witnesses']))

    def test_two_concrete_overlay_targets_do_not_choose_first(self):
        child = "@Component struct Wrapper{@State shown:boolean=false; @BuilderParam content:()=>void; build(){Column(){}.bindSheet(this.shown,this.content)}}"
        root = self.fixture(build='Column(){Wrapper(){SheetPage()};Wrapper(){OtherPage()}}', extra=child)
        out = self.proof(root)
        self.assertEqual(out['overlayBindings'], [])
        self.assertTrue(any('concrete instance' in row['reason'] for row in out['unknowns']))

    def test_unresolved_concrete_overlay_instance_blocks_partial_target(self):
        child = "@Component struct Wrapper{@State shown:boolean=false; @BuilderParam content:()=>void; build(){Column(){}.bindSheet(this.shown,this.content)}}"
        root = self.fixture(build='Column(){Wrapper(){SheetPage()};Wrapper()}', extra=child)
        self.assertEqual(self.overlays(root), [])

    def test_prop_stack_cannot_borrow_parent_reference_identity(self):
        child = "@Component struct Child{@Prop stack:NavPathStack=new NavPathStack(); build(){Button('Open').onClick(()=>this.stack?.pushPathByName('DetailPage',{}))}}"
        root = self.fixture(self.stack(), self.navigation('Child({stack:this.stack})'), extra=child)
        self.assertEqual(self.proof(root)['optionalPushes'], [])

    def test_mutated_intermediate_stack_cannot_borrow_parent_registration(self):
        child = "@ComponentV2 struct Child{@Param stack:NavPathStack=new NavPathStack(); build(){Button('Open').onClick(()=>this.stack?.pushPathByName('DetailPage',{}))}}"
        middle = "@ComponentV2 struct Middle{@Param stack:NavPathStack=new NavPathStack(); change(){this.stack=new NavPathStack()} build(){Child({stack:this.stack})}}"
        root = self.fixture(self.stack(), self.navigation('Middle({stack:this.stack})'), extra=child+middle)
        self.assertEqual(self.proof(root)['optionalPushes'], [])

    def test_guarded_optional_event_is_explicitly_out_of_scope(self):
        root = self.fixture(self.stack('@State ready:boolean=true;'), self.navigation("Button('Open').onClick(()=>{if(this.ready){this.stack?.pushPathByName('DetailPage',{})}})"))
        out = self.proof(root)
        self.assertEqual(out['optionalPushes'], [])
        self.assertTrue(any('guarded optional' in row['reason'] for row in out['unknowns']))

    def test_seed_push_cannot_replace_ambiguous_concrete_registration(self):
        child = "@Component struct Child{stack:NavPathStack=new NavPathStack(); @Builder map(name:string){if(name==='DetailPage'){OtherPage()}} build(){Navigation(this.stack){Button('Open').onClick(()=>this.stack?.pushPathByName('DetailPage',{}))}.navDestination(this.map)}}"
        root = self.fixture(self.stack(), self.navigation('Child({stack:this.stack})'), extra=child)
        out = self.proof(root)
        self.assertEqual(out['optionalPushes'], [])
        self.assertTrue(any('seed push excluded' in row['reason'] for row in out['unknowns']))
        self.assertTrue(any('ambiguous literal' in row['reason'] for row in out['unknowns']))

    def test_seed_default_event_does_not_run_after_concrete_override(self):
        child = "@Component struct Child{stack:NavPathStack=new NavPathStack(); @Event action:()=>void=()=>{this.stack?.pushPathByName('DetailPage',{})}; @Builder map(name:string){if(name==='DetailPage'){DetailPage()}} build(){Navigation(this.stack){Button('Open').onClick(()=>this.action())}.navDestination(this.map)}}"
        root = self.fixture(build='Child({action:()=>{}})', extra=child)
        self.assertEqual(self.proof(root)['optionalPushes'], [])

    def test_current_registration_replaces_independent_legacy_seed_candidate(self):
        child = "@Component struct Child{stack:NavPathStack=new NavPathStack(); @Builder map(name:string){if(name==='DetailPage'){DetailPage()}} build(){Navigation(this.stack){Button('Open').onClick(()=>this.stack?.pushPathByName('DetailPage',{}))}.navDestination(this.map)}}"
        root = self.fixture('stack:NavPathStack=new NavPathStack();', 'Navigation(this.stack){Child({stack:this.stack})}', extra=child)
        rows = self.proof(root)['optionalPushes']
        self.assertEqual(len(rows), 1)
        self.assertIn('>', rows[0]['instance'])
        self.assertEqual(len(rows[0]['stack_binding_chain']), 1)
        self.assertTrue(all('>' in witness['instance'] for witness in rows[0]['instance_witnesses']))
        out = self.proof(root)
        self.assertEqual({value['stack_identity'] for value in out['registrations']},
                         {value['registration']['stack_identity'] for value in out['eventBindings']})

    def test_nullish_and_logical_assignment_events_stay_unknown(self):
        for operator in ['??', '&&=', '||=', '??=']:
            with self.subTest(operator=operator):
                root = self.fixture(self.stack("flag:Object|null=null; open(){this.stack?.pushPathByName('DetailPage',{})}"), self.navigation("Button('Open').onClick(()=>{this.flag "+operator+" this.open()})"))
                out = self.proof(root)
                self.assertEqual(out['optionalPushes'], [])
                self.assertTrue(any('conditional event' in row['reason'] for row in out['unknowns']))

    def test_call_form_cover_and_nested_state(self):
        root = self.fixture('private controller:Control=new Control(); @Builder cover(){SheetPage()}',
                            "Column(){Text('Body')}.bindContentCover($$this.controller.shown,this.cover())", extra='class Control{shown:boolean=false;}')
        self.assertEqual(self.overlays(root)[0]['target'], 'SheetPage')

    def test_conditional_unique_overlay_keeps_condition(self):
        root = self.fixture('@State ready:boolean=false; @State shown:boolean=false; @Builder sheet(){if(this.ready){SheetPage()}}',
                            "Column(){}.bindSheet(this.shown,this.sheet)")
        rows = self.overlays(root)
        self.assertEqual(rows[0]['target'], 'SheetPage'); self.assertTrue(rows[0]['conditions'])
        self.assertEqual(rows[0]['conditions'][0]['runtime_value'], 'unknown')

    def test_same_component_both_branches(self):
        root = self.fixture('@State ready:boolean=false; @State shown:boolean=false; @Builder sheet(){if(this.ready){SheetPage()}else{SheetPage()}}',
                            "Column(){}.bindSheet(this.shown,this.sheet())")
        self.assertEqual(len(self.overlays(root)), 1)

    def test_different_overlay_branches_stay_unknown(self):
        root = self.fixture('@State ready:boolean=false; @State shown:boolean=false; @Builder sheet(){if(this.ready){SheetPage()}else{OtherPage()}}',
                            "Column(){}.bindSheet(this.shown,this.sheet())")
        out = self.proof(root); self.assertEqual(out['overlayBindings'], [])
        self.assertTrue(any('unique' in r['reason'] for r in out['unknowns']))

    def test_foreach_overlay_is_symbolic(self):
        root = self.fixture('@State shown:boolean=false; values:number[]=[]; @Builder sheet(){ForEach(this.values,(v:number)=>{SheetPage()})}',
                            "Column(){}.bindSheet(this.shown,this.sheet())")
        rows = self.overlays(root); self.assertEqual(rows[0]['target'], 'SheetPage')
        self.assertEqual(rows[0]['render_loops'][0]['cardinality'], 'unknown')
        self.assertEqual(rows[0]['possible_instances'], 'unknown')

    def test_shadowed_foreach_is_not_a_render_loop(self):
        root = self.fixture('@State shown:boolean=false; @Builder sheet(){ForEach([1],(v:number)=>{SheetPage()})}',
                            "Column(){}.bindSheet(this.shown,this.sheet())", extra='function ForEach(a:number[], f:(v:number)=>void){f(1)}')
        self.assertEqual(self.overlays(root), [])

    def test_recursive_overlay_remains_unknown(self):
        root = self.fixture('@State shown:boolean=false; @Builder sheet(){SheetPage();this.sheet()}', "Column(){}.bindSheet(this.shown,this.sheet())")
        self.assertEqual(self.overlays(root), [])

    def test_uninvoked_overlay_builder_does_not_create_relation(self):
        root = self.fixture('@State shown:boolean=false; @Builder unused(){Column(){}.bindSheet(this.shown,()=>{SheetPage()})}')
        self.assertEqual(self.overlays(root), [])

    def test_optional_helper_is_indirect_and_proves_registration(self):
        root = self.fixture(self.stack("open(){this.stack?.pushPathByName('DetailPage',{})}"), self.navigation("Button('Open').onClick(()=>this.open())"))
        out = self.proof(root); rows = out['optionalPushes']
        self.assertEqual(len(rows), 1); self.assertIs(rows[0]['indirect'], True)
        self.assertEqual(rows[0]['source'], 'Root'); self.assertEqual(rows[0]['target'], 'DetailPage')
        self.assertEqual(rows[0]['registration']['target'], 'DetailPage')
        self.assertTrue(any(a['kind'] == 'event-method-call' for a in rows[0]['chain']))
        self.assertEqual(rows[0]['line'], rows[0]['push_call_site']['line'])
        token=rows[0]['optional_token'];self.assertEqual(token['token_text'],'?.');self.assertEqual(token['placement'],'receiver')
        text=(root/token['file']).read_text();self.assertEqual(text[token['start_utf16']:token['end_utf16']],'?.')
        click=rows[0]['onclick_binding'];self.assertEqual(text[click['start_utf16']:click['end_utf16']],'onClick')

    def test_uncalled_helper_does_not_prove_click(self):
        root = self.fixture(self.stack("open(){this.stack?.pushPathByName('DetailPage',{})}"), self.navigation("Button('Open').onClick(()=>{})"))
        self.assertEqual(self.proof(root)['optionalPushes'], [])

    def test_different_stack_does_not_borrow_registration(self):
        root = self.fixture(self.stack("private other:NavPathStack=new NavPathStack(); open(){this.other?.pushPathByName('DetailPage',{})}"), self.navigation("Button('Open').onClick(()=>this.open())"))
        self.assertEqual(self.proof(root)['optionalPushes'], [])

    def test_mutated_stack_is_not_a_stable_instance(self):
        root = self.fixture(self.stack("open(){this.stack=new NavPathStack();this.stack?.pushPathByName('DetailPage',{})}"), self.navigation("Button('Open').onClick(()=>this.open())"))
        self.assertEqual(self.proof(root)['optionalPushes'], [])

    def test_dynamic_route_name_does_not_resolve(self):
        root = self.fixture(self.stack("name:string='DetailPage'; open(){this.stack?.pushPathByName(this.name,{})}"), self.navigation("Button('Open').onClick(()=>this.open())"))
        self.assertEqual(self.proof(root)['optionalPushes'], [])

    def test_parameterized_builder_and_event_forwarding(self):
        extra="@ComponentV2 struct PrimaryButton{@Event action:()=>void=()=>{};build(){Button('Open').onClick(()=>this.action())}}"
        members=self.stack("@Builder actionButton(action:()=>void){PrimaryButton({action:action})} open(){this.stack?.pushPathByName('DetailPage',{})}")
        out=self.proof(self.fixture(members,self.navigation('this.actionButton(()=>this.open())'),extra))
        rows=out['optionalPushes'];self.assertEqual(len(rows),1)
        self.assertEqual(rows[0]['source'],'Root');self.assertIs(rows[0]['indirect'],True)
        self.assertTrue(any(a['kind']=='event-parameter-invoke' for a in rows[0]['chain']))

    def test_builderparam_caller_body_reaches_event(self):
        extra="@Component struct Surface{@BuilderParam content:()=>void;build(){Column(){this.content()}}}"
        members=self.stack("open(){this.stack?.pushPathByName('DetailPage',{})}")
        out=self.proof(self.fixture(members,self.navigation("Surface(){Button('Open').onClick(()=>this.open())}"),extra))
        self.assertEqual(len(out['optionalPushes']),1)
        self.assertTrue(any(a['kind']=='component-instance' for a in out['optionalPushes'][0]['chain']))

    def test_child_stack_tracks_parent_instance(self):
        extra="@ComponentV2 struct Child{@Param stack:NavPathStack|undefined=undefined;open(){this.stack?.pushPathByName('DetailPage',{})}build(){Button('Open').onClick(()=>this.open())}}"
        out=self.proof(self.fixture(self.stack(),self.navigation('Child({stack:this.stack})'),extra))
        rows=out['optionalPushes'];self.assertEqual(len(rows),1)
        self.assertEqual(rows[0]['source'],'Child');self.assertTrue(rows[0]['stack_binding_chain'])
        self.assertEqual(rows[0]['registration']['instance'],rows[0]['stack_identity'].split('|')[-1])

    def test_unregistered_second_parent_remains_distinct_unknown(self):
        extra="""@ComponentV2 struct Child{@Param stack:NavPathStack|undefined=undefined;open(){this.stack?.pushPathByName('DetailPage',{})}build(){Button('Open').onClick(()=>this.open())}}
        @Component struct Registered{private stack:NavPathStack=new NavPathStack();@Builder dest(name:string,param:Object){if(name==='DetailPage'){DetailPage()}}build(){Navigation(this.stack){Child({stack:this.stack})}.navDestination(this.dest)}}
        @Component struct Unregistered{private stack:NavPathStack=new NavPathStack();build(){Navigation(this.stack){Child({stack:this.stack})}}}
        """
        root=self.fixture(build='Column(){Registered();Unregistered()}',extra=extra)
        source=(root/'entry/src/main/ets/pages/Root.ets').read_text()
        registered_start=source.index('@Component struct Registered')
        unregistered_start=source.index('@Component struct Unregistered')
        out=self.proof(root)
        self.assertTrue(out['optionalPushes'])
        for row in out['optionalPushes']:
            self.assertGreaterEqual(row['registration']['stack_property']['start_utf16'],registered_start)
            self.assertLess(row['registration']['stack_property']['start_utf16'],unregistered_start)
        self.assertTrue(any('stack instance' in r['reason'] and r.get('registration_count')==0 for r in out['unknowns']))
        self.assertTrue(all(r['registration']['stack_identity']==r['stack_identity'] for r in out['eventBindings']))

    def test_recursive_event_method_does_not_prove_push(self):
        root=self.fixture(self.stack("open(){this.open();this.stack?.pushPathByName('DetailPage',{})}"),self.navigation("Button('Open').onClick(()=>this.open())"))
        out=self.proof(root);self.assertEqual(out['optionalPushes'],[])
        self.assertTrue(any('recursive event' in r['reason'] for r in out['unknowns']))

    def test_returned_helper_does_not_visit_unreachable_push(self):
        root=self.fixture(self.stack("open(){return;this.stack?.pushPathByName('DetailPage',{})}"),self.navigation("Button('Open').onClick(()=>this.open())"))
        self.assertEqual(self.proof(root)['optionalPushes'],[])

    def test_both_returning_branches_stop_following_push(self):
        root=self.fixture(self.stack("ready:boolean=false;open(){if(this.ready){return}else{return};this.stack?.pushPathByName('DetailPage',{})}"),self.navigation("Button('Open').onClick(()=>this.open())"))
        self.assertEqual(self.proof(root)['optionalPushes'],[])

    def test_uninvoked_event_lambda_is_not_a_route(self):
        root=self.fixture(self.stack("open(){this.stack?.pushPathByName('DetailPage',{})}"),self.navigation("Button('Open').onClick(()=>{const later=()=>this.open()})"))
        self.assertEqual(self.proof(root)['optionalPushes'],[])

    def test_direct_return_does_not_keep_legacy_unreachable_proof(self):
        root=self.fixture(self.stack(),self.navigation("Button('Open').onClick(()=>{return;this.stack?.pushPathByName('DetailPage',{})})"))
        out=self.proof(root);self.assertEqual(out['optionalPushes'],[])
        self.assertTrue(any('proof' in r['reason'] for r in out['unknowns']))

    def test_direct_mutated_stack_does_not_keep_legacy_proof(self):
        root=self.fixture(self.stack(),self.navigation("Button('Open').onClick(()=>{this.stack=new NavPathStack();this.stack?.pushPathByName('DetailPage',{})})"))
        self.assertEqual(self.proof(root)['optionalPushes'],[])

    def test_nonoptional_existing_route_only_gets_evidence(self):
        out=self.proof(self.fixture(self.stack("open(){this.stack.pushPathByName('DetailPage',{})}"),self.navigation("Button('Open').onClick(()=>this.open())")))
        self.assertEqual(out['optionalPushes'],[]);self.assertTrue(out['eventBindings'])
        self.assertFalse(out['eventBindings'][0]['optional'])

    def test_old_direct_optional_keeps_single_compatible_record(self):
        out=self.proof(self.fixture(self.stack(),self.navigation("Button('Open').onClick(()=>this.stack?.pushPathByName('DetailPage',{}))")))
        self.assertEqual(len(out['optionalPushes']),1)
        self.assertIn('control_site',out['optionalPushes'][0])
        self.assertIs(out['optionalPushes'][0]['indirect'], False)
        self.assertEqual(out['optionalPushes'][0]['registration'], out['eventBindings'][0]['registration'])

if __name__=='__main__':unittest.main()
