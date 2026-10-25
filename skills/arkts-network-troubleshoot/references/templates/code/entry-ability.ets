/**
 * EntryAbility 启动模板（Phase 2）
 *
 * 核心模式：sync onCreate + async onWindowStageCreate + PreferencesUtil Promise 保留
 * 替换占位符：<BASE_URL> 自有业务域；handleSdkWant 如有 OAuth SDK 才需要
 */

import { AbilityConstant, ConfigurationConstant, UIAbility, Want } from '@kit.AbilityKit';
import { hilog } from '@kit.PerformanceAnalysisKit';
import { window } from '@kit.ArkUI';
import { EventBus } from '../events/EventBus';
import { PreferencesUtil } from '../common/PreferencesUtil';
// import { GlobalCont } from 'lib_common';                       // 可选，引入私仓 lib_common 才需要
// import { handleSdkWant } from '../services/sdk/SdkWantDispatcher';  // 可选，有 OAuth SDK 才需要

const DOMAIN = 0x0000;

export default class EntryAbility extends UIAbility {
  private prefsInitPromise: Promise<void> | null = null;

  onCreate(want: Want, launchParam: AbilityConstant.LaunchParam): void {
    try {
      this.context.getApplicationContext().setColorMode(ConfigurationConstant.ColorMode.COLOR_MODE_NOT_SET);
    } catch (err) {
      hilog.error(DOMAIN, 'EntryAbility', 'colorMode set failed: %{public}s', JSON.stringify(err));
    }

    // 1) lib_common 全局 Context 入口（可选）
    // try { GlobalCont.initContext(this.context); } catch (err) { /* ignore */ }

    // 2) AppStorage 必备 key 同步注入
    //    'context': HttpClient.download / 资源解析依赖
    //    'isDebug': HttpLogInterceptor 守卫；release 改 false
    //    'mHttpUrl': 拦截器 isOwnBusinessRequest / resolveDefaultBaseUrl
    try {
      AppStorage.setOrCreate('context', this.context);
      AppStorage.setOrCreate<boolean>('isDebug', true);
      AppStorage.setOrCreate<string>('mHttpUrl', '<BASE_URL>');
    } catch (err) {
      hilog.error(DOMAIN, 'EntryAbility', 'AppStorage init failed: %{public}s', JSON.stringify(err));
    }

    // 3) EventBus 注入 UIAbilityContext.eventHub
    try {
      EventBus.init(this.context);
    } catch (err) {
      hilog.error(DOMAIN, 'EntryAbility', 'EventBus.init failed: %{public}s', JSON.stringify(err));
    }

    // 4) PreferencesUtil 异步初始化 — 保留 Promise，onWindowStageCreate 内 await
    this.prefsInitPromise = PreferencesUtil.init(this.context);
    this.prefsInitPromise.catch((err: Object) => {
      hilog.error(DOMAIN, 'EntryAbility', 'PreferencesUtil.init failed: %{public}s', JSON.stringify(err));
    });

    // 5) SDK want 分发（冷启动）— OAuth / 三方登录 SDK 回调必备（如有，按你项目接入的 SDK 定）
    // try { handleSdkWant(want); } catch (err) { /* ignore */ }

    hilog.info(DOMAIN, 'EntryAbility', 'onCreate done');
  }

  /** 热启动从 OAuth SDK 跳回必走；漏调会导致 onResp 永不触发 */
  onNewWant(want: Want, launchParam: AbilityConstant.LaunchParam): void {
    // try { handleSdkWant(want); } catch (err) { /* ignore */ }
    hilog.info(DOMAIN, 'EntryAbility', 'onNewWant done');
  }

  onDestroy(): void {
    hilog.info(DOMAIN, 'EntryAbility', 'onDestroy');
  }

  async onWindowStageCreate(windowStage: window.WindowStage): Promise<void> {
    // 关键：必须等 PreferencesUtil.init 完成后再 loadContent
    // 否则 SplashPage.aboutToAppear → PreferencesUtil.getLong 拿默认 0 → 协议每次冷启都弹
    try {
      if (this.prefsInitPromise !== null) {
        await this.prefsInitPromise;
        hilog.info(DOMAIN, 'EntryAbility', 'PreferencesUtil ready before loadContent');
      }
    } catch (err) {
      hilog.warn(DOMAIN, 'EntryAbility', 'Wait PreferencesUtil failed: %{public}s', JSON.stringify(err));
    }

    windowStage.loadContent('pages/SplashPage', (err) => {
      if (err.code) {
        hilog.error(DOMAIN, 'EntryAbility', 'loadContent failed: %{public}s', JSON.stringify(err));
        return;
      }
      hilog.info(DOMAIN, 'EntryAbility', 'loadContent done');
    });
  }

  onWindowStageDestroy(): void {
    hilog.info(DOMAIN, 'EntryAbility', 'onWindowStageDestroy');
  }

  onForeground(): void {}

  onBackground(): void {}
}
