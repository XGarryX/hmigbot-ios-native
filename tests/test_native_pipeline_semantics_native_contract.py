"""Meaningful positive/negative native source proofs; no app test generation."""
import copy
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
import subprocess

ROOT = Path(os.environ.get('HMIGBOT_TEST_RUNTIME', Path(__file__).resolve().parents[1])).resolve()
sys.path.insert(0, str(ROOT / 'src'))
from hmigbot_ios.native_pipeline_semantics import (
    adapt_assembly, adapt_orphans, assembly_binding, form_surfaces,
    safearea_report, source_bounded_image, static_resource_use, pipeline_iterate, stage_runtime,
    source_scope_reports)
from hmigbot_ios.native_structural_evidence import EvidenceIndex


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8')


class NativeSemanticsTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='native-semantics-')
        self.addCleanup(self.temporary.cleanup)
        self.project = Path(self.temporary.name) / 'project'
        self.source = Path(self.temporary.name) / 'ios'
        self.ets = self.project / 'entry/src/main/ets'
        self.write('build-profile.json5', json.dumps({'app': {'products': [
            {'name': 'default', 'compatibleSdkVersion': '6.0.2(22)'}]},
            'modules': [{'name': 'entry', 'srcPath': './entry'}]}))
        self.write('.migbot/config.json', json.dumps({'source_platform': 'ios', 'ios': str(self.source)}))
        self.module = {'module': {'name': 'entry', 'type': 'entry', 'pages': '$profile:main_pages',
            'abilities': [{'name': 'Host', 'srcEntry': './ets/Host.ets'}]}}
        self.write('entry/src/main/module.json5', json.dumps(self.module))
        self.write('entry/src/main/resources/base/profile/main_pages.json', '{"src":["pages/Root"]}')
        self.code('Host.ets', "export default class Host extends UIAbility { onWindowStageCreate(stage: window.WindowStage): void { stage.loadContent('pages/Root'); } }")
        self.code('pages/Root.ets', "import { Action } from '../components/Shared';\n@Entry\n@ComponentV2\nstruct Root { build() { Column() { Action() } } }")
        self.shared = """export class Glyph {
 static source(symbol: string): Resource { return $r('app.media.icon'); }
}
@ComponentV2
export struct Action {
 build() { Image(Glyph.source('go')).width(20).height(20); }
}
@ComponentV2
export struct UnusedCard { build() { Text('unused'); } }
"""
        self.code('components/Shared.ets', self.shared)

    def write(self, relative, text):
        write(self.project / relative, text)

    def code(self, relative, text):
        write(self.ets / relative, text)

    def snapshot(self):
        return {p.relative_to(self.project).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in self.project.rglob('*') if p.is_file()}

    def orphan(self):
        return static_resource_use(EvidenceIndex(self.project),
            'entry/src/main/ets/components/Shared.ets', 'Glyph')

    def test_live_same_file_static_resource_is_consumed_without_fake_import(self):
        before = self.snapshot()
        self.assertEqual(self.orphan()['kind'], 'same_file_static_resource_consumed_by_image')
        report = {'orphans': [{'file': 'entry/src/main/ets/components/Shared.ets', 'class_name': name,
                              'reason': 'NO_IMPORTER'} for name in ('Glyph', 'UnusedCard')],
                  'orphan_count': 2, 'component_orphan_count': 2}
        fixed = adapt_orphans(self.project, report)
        self.assertEqual(fixed['original_report'], report)
        self.assertEqual([f['class_name'] for f in fixed['orphans']], ['UnusedCard'])
        self.assertEqual(fixed['orphan_count'], 1)
        self.assertEqual(before, self.snapshot())

    def test_comments_strings_and_unused_helper_cannot_consume_static_class(self):
        for replacement in ("Text('Image(Glyph.source(x))')", "Text('live'); /* Image(Glyph.source(x)) */",
                            "const hidden = (): void => { Image(Glyph.source('go')); }; Text('live')"):
            with self.subTest(replacement=replacement):
                self.code('components/Shared.ets', self.shared.replace("Image(Glyph.source('go')).width(20).height(20)", replacement))
                self.assertIsNone(self.orphan())

    def test_shadowed_receiver_and_unrendered_parent_remain_orphans(self):
        self.code('components/Shared.ets', self.shared.replace('build() { Image', 'build() { const Glyph = Other; Image'))
        self.assertIsNone(self.orphan())

    def test_only_actual_entry_struct_seeds_main_file_reachability(self):
        self.code('pages/Root.ets', "export class Glyph { static source(): Resource { return $r('app.media.icon'); } }\n"
            "@Entry @ComponentV2 struct Root { build() { Text('live'); } }\n"
            "@ComponentV2 struct Unused { build() { Image(Glyph.source()).width(20).height(20); } }\n")
        proof = static_resource_use(EvidenceIndex(self.project), 'entry/src/main/ets/pages/Root.ets', 'Glyph')
        self.assertIsNone(proof)
        self.code('components/Shared.ets', self.shared)
        self.code('pages/Root.ets', '@Entry\n@ComponentV2\nstruct Root { build() { Text("live"); } }')
        self.assertIsNone(self.orphan())

    def assembly(self):
        self.code('Services.ets', "export class Store { read(): number { return 2; } }\nexport class Preferences { read(): number { return 3; } }\nexport class Router {\n private static singleton: Router | undefined = undefined;\n static get shared(): Router { if (Router.singleton === undefined) { Router.singleton = new Router(); } return Router.singleton; }\n go(): void { this.running = true; }\n running: boolean = false;\n}\n")
        self.assembly_source = """import { Store, Preferences, Router } from './Services';
export interface CapabilityTable {
 store: Store;
 preferences: Preferences;
 router: Router;
}
export let capabilityTable: CapabilityTable;
export function install(context: Context): Promise<void> {
 const preferences = new Preferences();
 const router = Router.shared;
 capabilityTable = { store: new Store(), preferences: preferences, router: router };
 return hydrate();
}
function hydrate(): Promise<void> { return Promise.resolve(); }
"""
        self.code('AppAssembly.ets', self.assembly_source)
        self.code('Host.ets', "import { install } from './AppAssembly';\nexport default class Host extends UIAbility {\n private startup: Promise<void> | undefined = undefined;\n onCreate(): void { this.startup = install(this.context); }\n async onWindowStageCreate(stage: window.WindowStage): Promise<void> { if (this.startup !== undefined) { await this.startup; } await stage.loadContent('pages/Root'); }\n}\n")
        self.code('pages/Root.ets', "import { capabilityTable } from '../AppAssembly';\n@Entry\n@ComponentV2\nstruct Root { build() { Text(capabilityTable.store.read().toString()); } }")

    def proof(self):
        return assembly_binding(self.project, 'entry/src/main/ets/AppAssembly.ets')

    def test_unique_delayed_object_constructor_alias_singleton_and_awaited_host(self):
        self.assembly()
        before = self.snapshot()
        result = self.proof()
        self.assertIsNotNone(result)
        self.assertEqual(result['slots'], ['preferences', 'router', 'store'])
        original = {'passed': False, 'findings': [{'severity': 'FAIL', 'kind': 'capability-table-missing',
                    'file': 'entry/src/main/ets/AppAssembly.ets'}]}
        adapted = adapt_assembly(self.project, original)
        self.assertTrue(adapted['passed'])
        self.assertEqual(adapted['original_report'], original)
        self.assertEqual(self.snapshot(), before)

    def test_assembly_rejects_missing_or_duplicate_slot_multiple_producer_and_wrong_alias(self):
        self.assembly()
        changes = [('preferences: preferences, ', ''),
                   ('store: new Store(),', 'store: new Store(), store: new Store(),'),
                   ('return hydrate();', 'capabilityTable = { store: new Store(), preferences: preferences, router: router }; return hydrate();'),
                   ('const preferences = new Preferences();', 'const preferences = new Store();'),
                   ('const preferences = new Preferences();', 'const preferences = factory();'),
                   ('export let capabilityTable:', 'let capabilityTable:')]
        for old, new in changes:
            with self.subTest(change=new):
                self.code('AppAssembly.ets', self.assembly_source.replace(old, new))
                self.assertIsNone(self.proof())

    def test_assembly_rejects_uncalled_factory_wrong_consumer_and_load_before_hydration(self):
        self.assembly()
        host = (self.ets / 'Host.ets').read_text(encoding='utf-8')
        for text in (host.replace('this.startup = install(this.context);', ''),
                     host.replace('await this.startup;', ''),
                     host.replace('await this.startup;', "stage.loadContent('early'); await this.startup;"),
                     host.replace('onCreate(): void {', 'onCreate(): void { const install = other;')):
            with self.subTest(text=text):
                self.code('Host.ets', text)
                self.assertIsNone(self.proof())
        self.code('Host.ets', host)
        self.code('pages/Root.ets', '@Entry\n@ComponentV2\nstruct Root { build() { Text("unrelated capabilityTable.store"); } }')
        self.assertIsNone(self.proof())

    def test_direct_noop_capability_is_not_exempted_by_typed_binding_shape(self):
        self.assembly()
        for name in ('Services.ets', 'AppAssembly.ets'):
            path = self.ets / name
            path.write_text(path.read_text(encoding='utf8').replace('Store', 'NoopStore'), encoding='utf8')
        self.assertIsNone(self.proof())

    def test_initialization_and_await_in_unreachable_branches_do_not_dominate_ui(self):
        self.assembly()
        path = self.ets / 'Host.ets'
        original = path.read_text(encoding='utf8')
        for changed in (
            original.replace('if (this.startup !== undefined)', 'if (false)'),
            original.replace('this.startup = install(this.context);', 'if (false) { this.startup = install(this.context); }'),
            original.replace('if (this.startup !== undefined)', 'if (unrelatedReady)'),
            original.replace('this.startup = install(this.context);', 'const idle = (): void => { this.startup = install(this.context); };')):
            with self.subTest(changed=changed):
                path.write_text(changed, encoding='utf8')
                self.assertIsNone(self.proof())

    def background(self):
        self.code('components/Shared.ets', "@ComponentV2\nexport struct Background {\n @Builder empty(): void { Column() {} }\n @BuilderParam content: () => void = this.empty;\n build(): void { Stack() { Rect().fill('#fff').width('100%').height('100%').expandSafeArea([SafeAreaType.SYSTEM], [SafeAreaEdge.TOP, SafeAreaEdge.BOTTOM]).hitTestBehavior(HitTestMode.None); this.content(); }.width('100%').height('100%'); }\n}")
        self.code('pages/Root.ets', "import { Background } from '../components/Shared';\n@Entry\n@ComponentV2\nstruct Root { build() { Background() { Text('safe foreground'); } } }")
        self.original_safe = {'passed': False, 'returncode': 1, 'engine': 'python-native',
            'stdout_excerpt': '❌ L1 [EntryAbility]: 缺 setWindowLayoutFullScreen\n❌ L3 [pages\\Root.ets]: 全屏页未发现任何安全区响应\n扫描结果\n❌ 校验 FAIL'}

    def test_api10_default_policy_leaf_background_keeps_visual_unverified(self):
        self.background()
        result = safearea_report(self.project, self.original_safe)
        self.assertTrue(result['passed'])
        self.assertTrue(result['source_visual_unverified'])
        self.assertFalse(result['native_dispositions'][0]['cutout_avoidance_configured'])
        self.assertEqual(result['original_report'], self.original_safe)

    def test_true_immersive_and_expanded_foreground_are_not_exempt(self):
        self.background()
        host = (self.ets / 'Host.ets').read_text(encoding='utf-8')
        self.code('Host.ets', host.replace("stage.loadContent", "window.setWindowLayoutFullScreen(true); stage.loadContent"))
        self.assertFalse(safearea_report(self.project, self.original_safe)['passed'])
        self.code('Host.ets', host)
        path = self.ets / 'components/Shared.ets'
        original = path.read_text(encoding='utf-8')
        for changed in (original.replace('Rect()', 'Column()'),
                        original.replace('.hitTestBehavior(HitTestMode.None)', '.onClick(() => { save(); })'),
                        original.replace('.expandSafeArea', '.ignoreLayoutSafeArea')):
            with self.subTest(changed=changed):
                path.write_text(changed, encoding='utf-8')
                self.assertFalse(safearea_report(self.project, self.original_safe)['passed'])

    def test_unreachable_background_and_unsupported_api_do_not_prove_policy(self):
        self.background()
        self.code('pages/Root.ets', '@Entry\n@ComponentV2\nstruct Root { build() { Text("live"); } }')
        self.assertFalse(safearea_report(self.project, self.original_safe)['passed'])

    def test_foreground_transform_unknown_failure_and_truncated_report_remain_findings(self):
        self.background()
        root = self.ets / 'pages/Root.ets'
        root.write_text(root.read_text(encoding='utf8').replace("Text('safe foreground')", "Text('safe foreground').offset({ y: -200 })"), encoding='utf8')
        self.assertFalse(safearea_report(self.project, self.original_safe)['passed'])

    def test_custom_rendered_foreground_transform_requires_actual_unchanged_clip_ancestor(self):
        self.background()
        path = self.ets / 'components/Shared.ets'
        background = path.read_text(encoding='utf8')
        self.code('pages/Root.ets', "import { Background, Foreground } from '../components/Shared';\n"
            "@Entry @ComponentV2 struct Root { build() { Background() { Foreground(); } } }")
        unsafe = "\n@ComponentV2 export struct Foreground { build() { Text('offscreen').offset({ y: -200 }); } }\n"
        path.write_text(background + unsafe, encoding='utf8')
        self.assertFalse(safearea_report(self.project, self.original_safe)['passed'])
        safe = "\n@ComponentV2 export struct Foreground { build() { Stack() { Text('inside clip').offset({ y: -200 }); }.width(100).height(100).clip(true); } }\n"
        path.write_text(background + safe, encoding='utf8')
        self.assertTrue(safearea_report(self.project, self.original_safe)['passed'])
        path.write_text(background + safe.replace('.clip(true)', '.clip(true).offset({ y: -200 })'), encoding='utf8')
        self.assertFalse(safearea_report(self.project, self.original_safe)['passed'])

    def test_sdk_scroll_clip_follows_each_render_occurrence_and_last_modifier(self):
        self.background()
        shared = self.ets / 'components/Shared.ets'
        shared.write_text(shared.read_text(encoding='utf8') +
            "\n@ComponentV2 export struct Foreground { build() { Text('bounded by host').offset({ y: -200 }); } }\n", encoding='utf8')
        root = "import { Background, Foreground } from '../components/Shared';\n@Entry @ComponentV2 struct Root { build() { Background() { Scroll() { Foreground(); } SCROLL_MODIFIERS } EXTRA } }"
        for modifiers, extra, passed in (
            ('', '', True), ('.clip(false)', '', False),
            ('.clip(true).clip(false)', '', False), ('.clip(false).clip(true)', '', True),
            ('.offset({ y: -200 })', '', False), ('', 'Foreground();', False)):
            with self.subTest(modifiers=modifiers, extra=extra):
                self.code('pages/Root.ets', root.replace('SCROLL_MODIFIERS', modifiers).replace('EXTRA', extra))
                result = safearea_report(self.project, self.original_safe)
                self.assertEqual(result['passed'], passed)
                if passed:
                    self.assertTrue(result['native_dispositions'][0]['bounded_rendered_transforms'])
        # A same-spelling custom Scroll has no SDK default clipping guarantee.
        for shadow in ('\n@ComponentV2 struct Scroll { build() { Text("custom"); } }',
                       '\n@Builder function Scroll(): void { Text("custom builder"); }'):
            self.code('pages/Root.ets', root.replace('SCROLL_MODIFIERS', '').replace('EXTRA', '') + shadow)
            self.assertFalse(safearea_report(self.project, self.original_safe)['passed'])
        self.background()
        for report in ({**self.original_safe, 'returncode': 124},
                       {**self.original_safe, 'stderr_excerpt': 'Traceback: failed detector'},
                       {**self.original_safe, 'stdout_excerpt': '❌ L1 [EntryAbility]: 缺 setWindowLayoutFullScreen'},
                       {**self.original_safe, 'stdout_excerpt': self.original_safe['stdout_excerpt'] + '\n❌ L3 [Unknown.ets]: 全屏页未发现任何安全区响应'}):
            with self.subTest(report=report):
                self.assertFalse(safearea_report(self.project, report)['passed'])
        self.background()
        profile = self.project / 'build-profile.json5'
        profile.write_text(profile.read_text(encoding='utf8').replace('6.0.2(22)', '9'), encoding='utf8')
        self.assertFalse(safearea_report(self.project, self.original_safe)['passed'])

    def test_form_requires_actual_extension_profile_and_is_not_main_page(self):
        self.code('widget/Tile.ets', '@Entry\n@Component\nstruct Tile { @LocalStorageProp("title") title: string = ""; build() { Column() { Text(this.title); }.padding(16); } }')
        self.module['module']['extensionAbilities'] = [{'name': 'FormHost', 'type': 'form',
            'metadata': [{'name': 'ohos.extension.form', 'resource': '$profile:forms'}]}]
        self.write('entry/src/main/module.json5', json.dumps(self.module))
        self.write('entry/src/main/resources/base/profile/forms.json', '{"forms":[{"src":"./ets/widget/Tile.ets"}]}')
        self.assertIn('entry/src/main/ets/widget/Tile.ets', form_surfaces(EvidenceIndex(self.project)))
        self.module['module']['extensionAbilities'][0]['type'] = 'service'
        self.write('entry/src/main/module.json5', json.dumps(self.module))
        self.assertEqual({}, form_surfaces(EvidenceIndex(self.project)))
        self.module['module']['extensionAbilities'][0]['type'] = 'form'
        self.write('entry/src/main/module.json5', json.dumps(self.module))
        self.write('entry/src/main/resources/base/profile/main_pages.json', '{"src":["pages/Root","widget/Tile"]}')
        self.assertEqual({}, form_surfaces(EvidenceIndex(self.project)))

    def image_fixture(self):
        self.image_code = """import { image } from '@kit.ImageKit';
@ComponentV2
export struct Editor {
 @Param sourceImage: image.PixelMap | undefined = undefined;
 build() { if (this.sourceImage !== undefined) {
  Image(this.sourceImage).width('100%').constraintSize({ maxHeight: 220 }).objectFit(ImageFit.Contain);
 } }
}
"""
        self.code('pages/Editor.ets', self.image_code)
        self.write('spec/baseline/ui/editor.md', '```yaml\nsource_anchors:\n - role: view\n   path: App/Editor.swift\n   symbol: NativeEditor\n```\n目标：`entry/src/main/ets/pages/Editor.ets`\nImage resizable→scaledToFit→maxHeight220 sourceImage transient')
        self.swift_code = 'struct NativeEditor: View { var sourceImage: UIImage? = nil; var body: some View { if let sourceImage { Image(uiImage: sourceImage).resizable().scaledToFit().frame(maxHeight: 220) } } }'
        write(self.source / 'App/Editor.swift', self.swift_code)

    def image_proof(self):
        return source_bounded_image(self.project, 'entry/src/main/ets/pages/Editor.ets', 6)

    def test_source_anchored_pixelmap_max_height_contain_is_not_fixed_height(self):
        self.image_fixture()
        before = self.snapshot()
        proof = self.image_proof()
        self.assertEqual(proof['max_height'], 220)
        self.assertEqual(proof['kind'], 'source_max_height_contain')
        self.assertTrue(proof['source_visual_unverified'])
        self.assertEqual(before, self.snapshot())

    def test_bounded_image_rejects_wrong_cap_cover_untyped_input_and_borrowed_dimensions(self):
        self.image_fixture()
        changes = [('{ maxHeight: 220 }', '{ maxHeight: 0 }'),
                   ('{ maxHeight: 220 }', '{ maxHeight: -1 }'),
                   ('{ maxHeight: 220 }', '{ maxHeight: Infinity }'),
                   ('{ maxHeight: 220 }', '{ maxHeight: 221 }'),
                   ('ImageFit.Contain', 'ImageFit.Cover'),
                   ('image.PixelMap | undefined', 'string | undefined'),
                   ('.constraintSize({ maxHeight: 220 })', "; Text('live').constraintSize({ maxHeight: 220 })"),
                   ('.constraintSize({ maxHeight: 220 })', ".onClick(() => { Text('x').constraintSize({ maxHeight: 220 }); })"),
                   ('.width(\'100%\')', '.width(0)')]
        for old, new in changes:
            with self.subTest(changed=new):
                self.code('pages/Editor.ets', self.image_code.replace(old, new))
                self.assertIsNone(self.image_proof())

    def test_bounded_image_rejects_missing_source_contract_and_swift_mismatch(self):
        self.image_fixture()
        write(self.source / 'App/Editor.swift', self.swift_code.replace('maxHeight: 220', 'maxHeight: 221'))
        self.assertIsNone(self.image_proof())
        write(self.source / 'App/Editor.swift', self.swift_code)
        (self.project / 'spec/baseline/ui/editor.md').unlink()
        self.assertIsNone(self.image_proof())

    def raw_pipeline(self, arguments):
        from hmigbot_ios.native_pipeline_runtime import runtime_layout
        from hmigbot_ios.scheduler_windows_runtime import run
        with runtime_layout() as (executable, env):
            stage_runtime(executable.parent.parent.parent)
            command = [str(executable), 'structural_loop', *map(str, arguments)]
            result = run(command, cwd=self.project, env=env, timeout=60)
        return subprocess.CompletedProcess(result.args, result.returncode,
            result.stdout.decode('utf8', 'replace'), result.stderr.decode('utf8', 'replace'))

    def scope_noise(self):
        relatives = [
            'arkts-network-troubleshoot/references/templates/code/platform-info.ets',
            *['arkts-structural-closure/scripts/tests/fixtures/c16_component_orphans/entry/src/main/ets/' + name
              for name in ('services/DeadService.ets', 'components/OrphanCard.ets', 'dialogs/PrivacyPolicyDialog.ets')]]
        paths = []
        for relative in relatives:
            path = self.project / '.hmigbot-ios/plugin/vendor/hmigbot/skills' / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes((ROOT / 'vendor/hmigbot/skills' / relative).read_bytes())
            paths.append(path.relative_to(self.project).as_posix())
        return paths

    def scope_reports(self, audit_files, orphan_files):
        audit = {'findings': [{'file': path, 'line': 97, 'subtype': 'naked-TODO',
            'level': 'L3', 'severity_at_scope': 'FAIL'} for path in audit_files],
            'summary': {'FAIL': len(audit_files), 'WARN': 0, 'L3': len(audit_files)},
            'handoff_escape_hatches': []}
        orphans = {'orphans': [{'file': path, 'class_name': Path(path).stem, 'reason': 'NO_IMPORTER'}
            for path in orphan_files], 'orphan_count': len(orphan_files),
            'component_orphan_count': sum(any(part in {'components', 'dialogs'} for part in Path(path).parts)
                for path in orphan_files)}
        return audit, orphans

    def test_real_runtime_fixture_scope_partitions_counts_without_changing_raw_bytes(self):
        paths = self.scope_noise()
        audit, orphans = self.scope_reports(paths[:1], paths[1:])
        before = self.snapshot()
        effective_audit, effective_orphans = source_scope_reports(self.project, audit, orphans)
        self.assertEqual(effective_audit['original_report'], audit)
        self.assertEqual(effective_orphans['original_report'], orphans)
        self.assertEqual(effective_audit['summary'], {'FAIL': 0, 'WARN': 0, 'L3': 0})
        self.assertEqual(effective_orphans['orphan_count'], 0)
        self.assertEqual(effective_orphans['component_orphan_count'], 0)
        for row in effective_audit['native_scope_dispositions'] + effective_orphans['native_scope_dispositions']:
            self.assertEqual(row['file_sha256'], hashlib.sha256((self.project / row['resolved_relative']).read_bytes()).hexdigest())
        self.assertEqual(before, self.snapshot())

    def test_main_source_todo_and_orphan_are_retained_even_in_hidden_subdirectories(self):
        self.code('.embedded/ActualRules.ets', '// TODO implement actual business\nexport class ActualRules {}\n')
        self.code('store/ActualStore.ets', 'export class ActualStore { value: number = 1; }\n')
        paths = ['entry/src/main/ets/.embedded/ActualRules.ets', 'entry/src/main/ets/store/ActualStore.ets']
        audit, orphans = self.scope_reports(paths[:1], paths[1:])
        ea, eo = source_scope_reports(self.project, audit, orphans)
        self.assertEqual(ea['summary']['FAIL'], 1)
        self.assertEqual(eo['orphan_count'], 1)
        self.assertEqual(ea['native_scope_dispositions'], [])
        self.assertEqual(eo['native_scope_dispositions'], [])

    def test_scope_unknown_paths_aliases_traversal_and_count_mismatch_fail_closed(self):
        paths = self.scope_noise()
        for unknown in ('missing.ets', '../outside.ets', 'tools/../' + paths[0], 'file:alternate.ets', ''):
            with self.subTest(unknown=unknown):
                audit, orphans = self.scope_reports([unknown], [])
                with self.assertRaises(ValueError):
                    source_scope_reports(self.project, audit, orphans)
        audit, orphans = self.scope_reports(paths[:1], paths[1:])
        for field in ('FAIL', 'L3'):
            wrong = copy.deepcopy(audit)
            wrong['summary'][field] += 1
            with self.assertRaises(ValueError):
                source_scope_reports(self.project, wrong, orphans)
        wrong = copy.deepcopy(orphans)
        wrong['component_orphan_count'] += 1
        with self.assertRaises(ValueError):
            source_scope_reports(self.project, audit, wrong)
        alias = self.project / 'tools/aliased-main.ets'
        alias.parent.mkdir()
        os.link(self.ets / 'Host.ets', alias)
        audit, orphans = self.scope_reports(['tools/aliased-main.ets'], [])
        with self.assertRaises(ValueError):
            source_scope_reports(self.project, audit, orphans)

    def test_actual_original_13_detectors_then_original_runner_and_finalize(self):
        self.background()
        shared = self.ets / 'components/Shared.ets'
        shared.write_text(shared.read_text(encoding='utf8') + self.shared[:self.shared.index('@ComponentV2\nexport struct UnusedCard')], encoding='utf8')
        self.code('pages/Root.ets', "import { Background, Action } from '../components/Shared';\n@Entry\n@ComponentV2\nstruct Root { build() { Background() { Action(); } } }")
        self.write('spec/baseline/plans/feature-plan.md', '# Feature Plan\n')
        self.scope_noise()
        before = self.snapshot()
        state, output = self.project / 'spec/execution/native-loop.json', self.project / 'result.json'
        arguments = ['iterate', '--project-root', str(self.project), '--mode', 'pipeline',
                     '--target', 'final', '--state-file', str(state), '--output-json', str(output), '--max-iter', '3']
        result = pipeline_iterate(arguments, self.raw_pipeline)
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        data = json.loads(output.read_text(encoding='utf8'))
        self.assertEqual(data['verdict'], 'CONVERGED')
        audit = json.loads(Path(data['native_dispositions_report']).read_text(encoding='utf8'))
        self.assertEqual(len(audit['all_original_detectors_executed']), 13)
        self.assertEqual(audit['raw_verdict'], 'CONTINUE')
        self.assertGreaterEqual(len(audit['resolved_fingerprints']), 1)
        self.assertEqual(len(audit['scope_disposition_files_sha256']), 4)
        self.assertEqual((audit['original_audit_fail'], audit['effective_audit_fail']), (1, 0))
        for name, sha in audit['raw_files_sha256'].items():
            self.assertEqual(hashlib.sha256((Path(audit['raw_state']).parent / name).read_bytes()).hexdigest(), sha)
        final = self.raw_pipeline(['finalize', '--state-file', str(state), '--output-json', str(self.project / 'final.json')])
        self.assertEqual(final.returncode, 0, final.stderr + final.stdout)
        self.assertEqual(json.loads((self.project / 'final.json').read_text(encoding='utf8'))['final_state'], 'PASS')
        after = self.snapshot()
        self.assertEqual(before, {key: after[key] for key in before})

    def test_actual_runner_keeps_true_component_gap_and_original_finalize_rejects_it(self):
        self.background()
        shared = self.ets / 'components/Shared.ets'
        shared.write_text(shared.read_text(encoding='utf8') + '\n@ComponentV2\nexport struct GenuineGap { build() { Text("unrendered"); } }\n', encoding='utf8')
        self.write('spec/baseline/plans/feature-plan.md', '# Feature Plan\n')
        self.scope_noise()
        self.code('core/ActualRules.ets', '// TODO implement actual business\nexport class ActualRules { value: number = 1; }\n')
        self.code('store/ActualStore.ets', 'export class ActualStore { value: number = 1; read(): number { return this.value; } }\n')
        state, output = self.project / 'spec/execution/native-loop.json', self.project / 'result.json'
        result = pipeline_iterate(['iterate', '--project-root', str(self.project), '--mode', 'pipeline',
            '--target', 'final', '--state-file', str(state), '--output-json', str(output), '--max-iter', '3'], self.raw_pipeline)
        self.assertEqual(result.returncode, 1, result.stderr + result.stdout)
        self.assertEqual(json.loads(output.read_text(encoding='utf8'))['verdict'], 'CONTINUE')
        remaining = json.loads((state.parent / 'orphans-pipeline-iter0.json').read_text(encoding='utf8'))
        self.assertIn('GenuineGap', [f['class_name'] for f in remaining['orphans']])
        self.assertIn('ActualStore', [f['class_name'] for f in remaining['orphans']])
        audit = json.loads((state.parent / 'audit-pipeline-iter0.json').read_text(encoding='utf8'))
        main_raw = [row for row in audit['original_report']['findings']
                    if row['file'].replace('\\', '/').startswith('entry/src/main/ets/')]
        self.assertEqual(audit['findings'], main_raw)
        self.assertEqual(audit['summary']['FAIL'], sum(row['severity_at_scope'] == 'FAIL' for row in main_raw))
        self.assertTrue(any(row['subtype'] == 'naked-TODO' for row in audit['findings']))
        self.assertTrue(all(row['file'].replace('\\', '/').startswith('entry/src/main/ets/')
                            for row in audit['findings']))
        final = self.raw_pipeline(['finalize', '--state-file', str(state), '--output-json', str(self.project / 'final.json')])
        self.assertNotEqual(final.returncode, 0, final.stderr + final.stdout)


if __name__ == '__main__':
    unittest.main()
