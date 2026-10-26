/**
 * 设备 / 应用字段获取（HarmonyOS 通用机制，V2 优先）
 *
 * 本文件只给「各类公参字段在 HarmonyOS 侧怎么取」的**通用机制**，**不绑定**字段最终进 header 还是 body、
 * 也不预设字段名 / 字段集 —— 位置、字段集、字段名由「网络层决策清单」(network-decision-checklist.md)
 * 按你**当前项目**的 Android 源确定，本文件不写死。
 *
 * 原则（务必遵守）：
 *  · 照搬你项目 Android 原版的字段取值；HarmonyOS 有等价 API 就用等价。
 *  · 无等价的【留显式标记】（占位登记），**绝不静默置空**——"空"只能是"照搬原版其值确实为空 + 已登记标记"的结果。
 *  · 设备唯一标识类（Android 的 IMEI / 系统级设备 ID 等）HarmonyOS 因隐私多无直接等价：用 OAID / AAID / ODID /
 *    首启持久化 UUID 等替代并**保持非空**；若后端按某标识反查枚举，空值会触发后端异常。
 *
 * 各类字段的 HarmonyOS 获取入口（按你项目需要取用，不必全用）：
 *  · 应用版本 / 版本号 / 包名   → @kit.AbilityKit  bundleManager.getBundleInfoForSelfSync(...)
 *  · 品牌 / 型号 / 系统版本     → @kit.BasicServicesKit  deviceInfo.brand / .productModel / .osFullName
 *  · 屏幕宽高                   → @kit.ArkUI  display.getDefaultDisplaySync()
 *  · 运营商                     → @kit.TelephonyKit  sim.getSimOperatorNumericSync(0)
 *  · 广告标识 OAID             → @kit.AdsKit  identifier.getOAID()（需 APP_TRACKING_CONSENT；未授权/未接 → 持久化 UUID 兜底，保持非空）
 *  · 设备 / 应用唯一标识        → AAID(@kit.PushKit) / ODID(基础服务) / 首启持久化 UUID
 *  · 应用名                     → resourceManager.getStringSync(labelId)（注意 appInfo.label 可能返回未解析占位）
 *  · 本地标志（安装态/协议态等） → 你项目持久化层（Preferences 等）启动期 seed 到 AppStorage，请求时同步读
 */

import { bundleManager } from '@kit.AbilityKit';
import { deviceInfo } from '@kit.BasicServicesKit';
import { display } from '@kit.ArkUI';
import { sim } from '@kit.TelephonyKit';
import { hilog } from '@kit.PerformanceAnalysisKit';

const TAG = 'DeviceAppFields';
const DOMAIN = 0x0000;

/**
 * 设备 / 应用基础信息缓存（启动期填一次，避免每请求重读 bundleManager / deviceInfo / display）。
 * 这些是**通用 HarmonyOS 读取机制**；字段最终叫什么、进 header 还是 body，由你项目按决策清单决定。
 */
export class DeviceAppFields {
  static brand: string = '';
  static productModel: string = '';
  static systemVersion: string = '';
  static versionName: string = '';
  static versionCode: number = 0;
  static bundleName: string = '';
  static screenW: number = 0;
  static screenH: number = 0;
  static operator: string = '';
  static appName: string = '';
  static initialized: boolean = false;

  static ensureInit(): void {
    if (DeviceAppFields.initialized) {
      return;
    }
    let labelId: number = 0;
    let labelStr: string = '';
    try {
      const info: bundleManager.BundleInfo = bundleManager.getBundleInfoForSelfSync(
        bundleManager.BundleFlag.GET_BUNDLE_INFO_WITH_APPLICATION);
      DeviceAppFields.bundleName = info.name ?? '';
      DeviceAppFields.versionName = info.versionName ?? '';
      DeviceAppFields.versionCode = info.versionCode ?? 0;
      labelId = info.appInfo.labelId;
      labelStr = info.appInfo.label ?? '';
    } catch (e) {
      hilog.warn(DOMAIN, TAG, 'bundle read failed: %{public}s', (e as Error).message);
    }
    DeviceAppFields.appName = DeviceAppFields.resolveAppName(labelId, labelStr);
    try {
      DeviceAppFields.brand = deviceInfo.brand ?? '';
      DeviceAppFields.productModel = deviceInfo.productModel ?? '';
      DeviceAppFields.systemVersion = deviceInfo.osFullName ?? '';
    } catch (e) {
      hilog.warn(DOMAIN, TAG, 'deviceInfo read failed: %{public}s', (e as Error).message);
    }
    try {
      const dsp: display.Display = display.getDefaultDisplaySync();
      DeviceAppFields.screenW = dsp.width;
      DeviceAppFields.screenH = dsp.height;
    } catch (e) {
      hilog.warn(DOMAIN, TAG, 'display read failed: %{public}s', (e as Error).message);
    }
    DeviceAppFields.operator = DeviceAppFields.resolveOperator();
    DeviceAppFields.initialized = true;
  }

  /** 运营商：无 SIM / 无权限时**照搬你项目 Android 的兜底约定值**（去 Android 源确认，勿随手留空）。 */
  private static resolveOperator(): string {
    try {
      const name: string = sim.getSimOperatorNumericSync(0);
      if (name !== undefined && name !== null && name.length > 0) {
        return name;
      }
    } catch (e) {
      hilog.warn(DOMAIN, TAG, 'operator read failed: %{public}s', (e as Error).message);
    }
    // TODO 照搬你项目 Android 无 SIM/无权限的兜底约定值（不是默认空 —— 去源码确认后填）。
    return '';
  }

  /** 应用名：优先用 labelId 经 resourceManager 解析真值（appInfo.label 可能是未解析占位字符串）。 */
  private static resolveAppName(labelId: number, labelStr: string): string {
    if (labelId > 0) {
      try {
        const ctx = AppStorage.get<Context>('context');
        if (ctx !== undefined && ctx !== null) {
          const resName: string = ctx.resourceManager.getStringSync(labelId);
          if (resName.length > 0) {
            return resName;
          }
        }
      } catch (e) {
        hilog.warn(DOMAIN, TAG, 'resolveAppName via labelId failed: %{public}s', (e as Error).message);
      }
    }
    if (labelStr.length > 0 && !labelStr.startsWith('$')) {
      return labelStr;
    }
    return labelStr;
  }
}
