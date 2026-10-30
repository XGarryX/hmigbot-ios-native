// Generic optional Hypium test. Generated data belongs in the selected target,
// never in the tool payload. Uses application-scoped UiTest selectors and an
// active application's window rectangle; does not capture the computer desktop.
import { describe, it, expect } from '@ohos/hypium';
import { abilityDelegatorRegistry, Driver, ON } from '@kit.TestKit';
import { ConfigurationConstant } from '@kit.AbilityKit';
import { fileIo as fs } from '@kit.CoreFileKit';
import { util } from '@kit.ArkTS';

interface Step { action: string; identifier?: string; text?: string; checkpoint_id?: string; timeout_ms?: number }
interface Configuration { language: string; locale: string; theme: string; content_size: string }
interface Request {
  bundle_id: string; ability_name: string; binding_sha256: string;
  configuration: Configuration; steps: Step[]
  observations_only: boolean;
}
interface Event {
  run_id: string; binding_sha256: string; kind: string; name: string;
  sequence: number; parts: number; data: string
}
interface Node {
  identifier: string; type: string; label: string; value: string;
  enabled: boolean; selected: boolean; frame: Object
}
const REQUEST: Request = __HMIGBOT_REQUEST__;

export default function hmigbotUiValidationTest() {
  describe('HMigbotUiValidation', () => {
    it('fixedScenario', 0, async () => {
      const delegator = abilityDelegatorRegistry.getAbilityDelegator();
      const args = abilityDelegatorRegistry.getArguments();
      const runId = args.parameters['hmigbot_run'];
      expect(args.bundleName).assertEqual(REQUEST.bundle_id);
      expect(args.parameters['hmigbot_binding']).assertEqual(REQUEST.binding_sha256);
      const driver = Driver.create();
      const encoder = new util.TextEncoder();
      const base64 = new util.Base64Helper();
      const send = (kind: string, name: string, value: Uint8Array): void => {
        const encoded = base64.encodeToStringSync(value);
        const parts = Math.max(1, Math.ceil(encoded.length / 6000));
        for (let i = 0; i < parts; i++) {
          const event: Event = { run_id: runId, binding_sha256: REQUEST.binding_sha256,
            kind: kind, name: name, sequence: i, parts: parts, data: encoded.slice(i * 6000, (i + 1) * 6000) };
          delegator.printSync('HMIGBOT_UI_V1 ' + JSON.stringify(event));
        }
      };
      const sendJson = (kind: string, name: string, value: Object): void => {
        send(kind, name, encoder.encodeInto(JSON.stringify(value)));
      };
      try {
        await delegator.startAbility({ bundleName: REQUEST.bundle_id, abilityName: REQUEST.ability_name });
        await driver.waitForIdle(500, 5000);
        const top = await delegator.getCurrentTopAbility();
        const appConfiguration = top.context.config;
        const resources = top.context.resourceManager.getConfigurationSync();
        const mode = appConfiguration.colorMode;
        const scale = appConfiguration.fontSizeScale;
        const observed: Configuration = {
          language: (appConfiguration.language || resources.locale).split(/[-_]/)[0],
          locale: resources.locale.replace(/_/g, '-'),
          theme: mode === ConfigurationConstant.ColorMode.COLOR_MODE_DARK ? 'dark' :
            mode === ConfigurationConstant.ColorMode.COLOR_MODE_LIGHT ? 'light' : 'unknown',
          content_size: scale === 1 ? 'normal' : scale && scale > 0 ? 'scale:' + scale : 'unknown'
        };
        sendJson('configuration', 'configuration.json', observed);
        if (!REQUEST.observations_only) {
          expect(observed.language).assertEqual(REQUEST.configuration.language);
          expect(observed.locale).assertEqual(REQUEST.configuration.locale);
          expect(observed.theme).assertEqual(REQUEST.configuration.theme);
          expect(observed.content_size).assertEqual(REQUEST.configuration.content_size);
        }
        const completed: string[] = [];
        for (let i = 0; i < REQUEST.steps.length; i++) {
          const step = REQUEST.steps[i];
          const window = await driver.findWindow({ bundleName: REQUEST.bundle_id });
          expect(await window.getBundleName()).assertEqual(REQUEST.bundle_id);
          expect(await window.isActive()).assertTrue();
          if (step.action === 'checkpoint') {
            const id = step.checkpoint_id || '';
            const rect = await window.getBounds();
            const path = top.context.filesDir + '/hmigbot-ui-' + runId + '-' + id + '.png';
            expect(await driver.screenCapture(path, rect)).assertTrue();
            const length = fs.statSync(path).size;
            if (length > 25 * 1024 * 1024) { throw new Error('capture exceeds explicit protocol byte budget'); }
            const file = fs.openSync(path, fs.OpenMode.READ_ONLY);
            const buffer = new ArrayBuffer(length);
            try { expect(fs.readSync(file.fd, buffer)).assertEqual(length); }
            finally { fs.closeSync(file); }
            send('artifact', 'shots/' + id + '.png', new Uint8Array(buffer));
            fs.unlinkSync(path);
            const components = await driver.findComponents(ON.inWindow(REQUEST.bundle_id));
            const nodes: Node[] = [];
            for (let c = 0; c < components.length; c++) {
              const component = components[c];
              const text = await component.getText();
              nodes.push({ identifier: await component.getId(), type: await component.getType(),
                label: text, value: text, enabled: await component.isEnabled(),
                selected: await component.isSelected(), frame: await component.getBounds() });
            }
            sendJson('artifact', 'hierarchy/' + id + '.json', {
              scope: 'flat exposed controls in selected application window', nodes: nodes,
              viewport: { width: rect.right - rect.left, height: rect.bottom - rect.top, coordinate_space: 'display_pixels' }
            });
            sendJson('checkpoint', id, { id: id, status: 'passed', captured_at: new Date().toISOString(),
              capture_scope: 'device_region_bound_to_active_app_window', window_bundle_id: await window.getBundleName(),
              bounds: rect });
            completed.push(id);
          } else if (step.action === 'back') {
            await driver.pressBack();
          } else {
            const selector = ON.id(step.identifier || '').inWindow(REQUEST.bundle_id);
            const component = await driver.waitForComponent(selector, step.timeout_ms || 5000);
            expect(component !== undefined).assertTrue();
            if (step.action === 'tap') { await component.click(); }
            else if (step.action === 'input') { await component.inputText(step.text || ''); }
            else if (step.action === 'assert_text') { expect(await component.getText()).assertEqual(step.text || ''); }
          }
          await driver.waitForIdle(500, 5000);
        }
        sendJson('complete', 'complete.json', { checkpoints: completed, status: 'passed' });
      } catch (error) {
        sendJson('error', 'error.json', { status: 'failed', message: String(error) });
        throw error;
      }
    });
  });
}
