// 断点 + 折叠屏工具类（V2 — 已移除安全区适配，与 arkts-immersive-safearea 二选一）
//
// 安全区适配（windowTopPadding / windowBottomPadding 等）请使用：
//   arkts-skills/skills/arkts-immersive-safearea/SKILL.md 的 WindowModel 方案
//   （EntryAbility 一次性测量 + AppStorageV2.connect + windowSizeChange 响应式）
//
// 本文件提供（V2 风格）：
//   1. 断点常量 (xs/sm/md/lg/xl) — 阈值 + 字符串标识
//   2. BreakpointType<T> 泛型按断点取值
//   3. 断点计算函数（getBreakpointByWidth / getVerticalBreakpoint / isLargeBreakpoint / getMaxContentWidth）
//   4. @ObservedV2 BreakpointModel — 当前窗口/断点/折叠屏状态全局响应式模型
//   5. AdaptiveWindowObserver 综合观察者（windowSize + 折叠屏，直接写入 BreakpointModel）
//
// V1 → V2 迁移说明：
//   原本通过 AppStorage.setOrCreate / @StorageProp(key) 暴露的 8 个全局键
//   （currentBreakpoint / currentVerticalBreakpoint / windowWidth / windowHeight /
//   windowWidthPx / isFoldableDevice / currentFoldStatus / currentFoldDisplayMode）
//   已统一封装为 @ObservedV2 BreakpointModel 类的 @Trace 属性。
//   消费侧用法：
//     @ComponentV2
//     struct MyPage {
//       @Local bp: BreakpointModel = getBreakpointModel();
//       build() { Text(`当前断点: ${this.bp.currentBreakpoint}`) }
//     }

import window from '@ohos.window';
import display from '@ohos.display';
import { AppStorageV2 } from '@kit.ArkUI';

// ─────────────────────────────────────────
// 1. 断点常量（阈值 + 标识）
// ─────────────────────────────────────────

export class BreakpointConstants {
  static readonly BREAKPOINT_XS_VALUE: number = 320;
  static readonly BREAKPOINT_SM_VALUE: number = 600;
  static readonly BREAKPOINT_MD_VALUE: number = 840;
  static readonly BREAKPOINT_LG_VALUE: number = 1440;

  static readonly BREAKPOINT_XS: string = 'xs';
  static readonly BREAKPOINT_SM: string = 'sm';
  static readonly BREAKPOINT_MD: string = 'md';
  static readonly BREAKPOINT_LG: string = 'lg';
  static readonly BREAKPOINT_XL: string = 'xl';

  static readonly VERTICAL_BREAKPOINT_SM: number = 0.8;
  static readonly VERTICAL_BREAKPOINT_MD: number = 1.2;

  static readonly VERTICAL_SM: string = 'vertical_sm';
  static readonly VERTICAL_MD: string = 'vertical_md';
  static readonly VERTICAL_LG: string = 'vertical_lg';

  // 注：原 V1 时代的 storage 键常量（CURRENT_BREAKPOINT / WINDOW_WIDTH / IS_FOLDABLE_DEVICE 等）
  // 已迁移为 BreakpointModel 类的 @Trace 属性，不再以独立 string 键存在。
  // 安全区常量 (windowTopPadding / windowBottomPadding / cutoutTop / keyboardHeight)
  // 已迁移到 arkts-immersive-safearea 的 WindowModel
}

// ─────────────────────────────────────────
// 2. 按断点返回不同值的泛型工具
// ─────────────────────────────────────────

export class BreakpointType<T> {
  sm: T;
  md?: T;
  lg?: T;
  xl?: T;

  constructor(sm: T, md?: T, lg?: T, xl?: T) {
    this.sm = sm;
    this.md = md;
    this.lg = lg;
    this.xl = xl;
  }

  getValue(breakpoint: string): T {
    switch (breakpoint) {
      case 'xl':
        return this.xl ?? this.lg ?? this.md ?? this.sm;
      case 'lg':
        return this.lg ?? this.md ?? this.sm;
      case 'md':
        return this.md ?? this.sm;
      default:
        return this.sm;
    }
  }
}

// ─────────────────────────────────────────
// 3. 断点计算函数
// ─────────────────────────────────────────

export function getBreakpointByWidth(width: number): string {
  if (width < BreakpointConstants.BREAKPOINT_XS_VALUE) {
    return BreakpointConstants.BREAKPOINT_XS;
  } else if (width < BreakpointConstants.BREAKPOINT_SM_VALUE) {
    return BreakpointConstants.BREAKPOINT_SM;
  } else if (width < BreakpointConstants.BREAKPOINT_MD_VALUE) {
    return BreakpointConstants.BREAKPOINT_MD;
  } else if (width < BreakpointConstants.BREAKPOINT_LG_VALUE) {
    return BreakpointConstants.BREAKPOINT_LG;
  } else {
    return BreakpointConstants.BREAKPOINT_XL;
  }
}

export function getVerticalBreakpoint(width: number, height: number): string {
  const ratio = height / Math.max(width, 1);
  if (ratio < BreakpointConstants.VERTICAL_BREAKPOINT_SM) {
    return BreakpointConstants.VERTICAL_SM;
  } else if (ratio < BreakpointConstants.VERTICAL_BREAKPOINT_MD) {
    return BreakpointConstants.VERTICAL_MD;
  } else {
    return BreakpointConstants.VERTICAL_LG;
  }
}

export function isLargeBreakpoint(breakpoint: string): boolean {
  return breakpoint === BreakpointConstants.BREAKPOINT_LG ||
         breakpoint === BreakpointConstants.BREAKPOINT_XL;
}

export function getMaxContentWidth(breakpoint: string): number {
  if (breakpoint === BreakpointConstants.BREAKPOINT_XL) return 1280;
  if (breakpoint === BreakpointConstants.BREAKPOINT_LG) return 980;
  return 10000;
}

// ─────────────────────────────────────────
// 4. @ObservedV2 BreakpointModel — 全局响应式模型
// ─────────────────────────────────────────

@ObservedV2
export class BreakpointModel {
  @Trace currentBreakpoint: string = BreakpointConstants.BREAKPOINT_SM;
  @Trace currentVerticalBreakpoint: string = BreakpointConstants.VERTICAL_LG;
  @Trace windowWidth: number = 0;
  @Trace windowHeight: number = 0;
  @Trace windowWidthPx: number = 0;
  @Trace isFoldableDevice: boolean = false;
  @Trace currentFoldStatus: number = 0;
  @Trace currentFoldDisplayMode: number = 0;
}

const BREAKPOINT_MODEL_KEY: string = 'breakpoint_model';

// 全局单例 helper（在任何 @ComponentV2 组件 / Observer / Service 中调用）
// 第一次调用时创建实例，后续调用返回同一实例（属性变化自动同步到所有引用方）
export function getBreakpointModel(): BreakpointModel {
  return AppStorageV2.connect(BreakpointModel, BREAKPOINT_MODEL_KEY, () => new BreakpointModel())!;
}

// ─────────────────────────────────────────
// 5. 综合窗口观察者（断点 + 折叠屏，写入 BreakpointModel）
// ─────────────────────────────────────────

export class AdaptiveWindowObserver {
  private static currentWindow?: window.Window;
  private static initialized: boolean = false;
  private static model: BreakpointModel = getBreakpointModel();

  private static readonly onWindowSizeChange: Callback<window.Size> = (size: window.Size): void => {
    AdaptiveWindowObserver.updateWindowMetrics(size.width, size.height);
  };

  // onAvoidAreaChange 已迁移到 arkts-immersive-safearea 的 WindowModel

  private static readonly onFoldStatusChange: Callback<number> = (status: number): void => {
    AdaptiveWindowObserver.model.currentFoldStatus = status;
  };

  private static readonly onFoldDisplayModeChange: Callback<number> = (mode: number): void => {
    AdaptiveWindowObserver.model.currentFoldDisplayMode = mode;
  };

  static async init(context: Context): Promise<void> {
    if (AdaptiveWindowObserver.initialized) return;
    // V2 模型构造函数已设置默认值，无需 V1 时代的 initDefaults() 显式 setOrCreate
    try {
      const win = await window.getLastWindow(context);
      AdaptiveWindowObserver.bindWindow(win);
    } catch (error) {
      console.error('AdaptiveWindowObserver init failed:', JSON.stringify(error));
    }
  }

  static destroy(): void {
    if (!AdaptiveWindowObserver.currentWindow) return;
    AdaptiveWindowObserver.currentWindow.off('windowSizeChange', AdaptiveWindowObserver.onWindowSizeChange);
    try {
      display.off('foldStatusChange', AdaptiveWindowObserver.onFoldStatusChange);
      display.off('foldDisplayModeChange', AdaptiveWindowObserver.onFoldDisplayModeChange);
    } catch (_) {}
    AdaptiveWindowObserver.currentWindow = undefined;
    AdaptiveWindowObserver.initialized = false;
  }

  private static updateWindowMetrics(widthPx: number, heightPx: number): void {
    const w = px2vp(widthPx);
    const h = px2vp(heightPx);
    const m = AdaptiveWindowObserver.model;
    m.windowWidth = w;
    m.windowHeight = h;
    m.windowWidthPx = widthPx;
    m.currentBreakpoint = getBreakpointByWidth(w);
    m.currentVerticalBreakpoint = getVerticalBreakpoint(w, h);
  }

  // updateAvoidAreas() 已删除 - 安全区适配请使用 arkts-immersive-safearea 的 WindowModel

  private static updateFoldMetrics(): void {
    try {
      const foldable = display.isFoldable();
      if (foldable) {
        const m = AdaptiveWindowObserver.model;
        m.isFoldableDevice = true;
        m.currentFoldStatus = display.getFoldStatus() as number;
        m.currentFoldDisplayMode = display.getFoldDisplayMode() as number;
      }
    } catch (_) {}
  }

  private static bindWindow(win: window.Window): void {
    AdaptiveWindowObserver.currentWindow = win;
    const props = win.getWindowProperties();
    AdaptiveWindowObserver.updateWindowMetrics(props.windowRect.width, props.windowRect.height);
    AdaptiveWindowObserver.updateFoldMetrics();
    win.on('windowSizeChange', AdaptiveWindowObserver.onWindowSizeChange);
    try {
      display.on('foldStatusChange', AdaptiveWindowObserver.onFoldStatusChange);
      display.on('foldDisplayModeChange', AdaptiveWindowObserver.onFoldDisplayModeChange);
    } catch (_) {}
    AdaptiveWindowObserver.initialized = true;
  }
}
