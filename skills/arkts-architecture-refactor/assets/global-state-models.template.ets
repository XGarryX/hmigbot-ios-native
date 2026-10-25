/**
 * GlobalStateModels.ets — 跨页响应式状态模型基础骨架
 *
 * 用途：替代 v1 `AppStorage.setOrCreate('key', v) + @StorageProp('key') var: T = default` 模式。
 * 配合 v1→v2 全栈迁移使用，详见 references/v2-migration-playbook.md。
 *
 * 部署：
 *   features/business_common/src/main/ets/models/GlobalStateModels.ets
 *
 * 使用：
 *   // setter (任何位置)
 *   GlobalState.vip.isVipState = true;
 *
 *   // reader (在 @ComponentV2 page)
 *   safeArea: SafeAreaModel = AppStorageV2.connect(SafeAreaModel, () => new SafeAreaModel())!;
 *   build() { Text(`top: ${this.safeArea.statusBarHeight}`) }
 *
 * 自定义：
 *   把项目里 @StorageProp 用到的所有 key 收编进对应的 @ObservedV2 类。
 *   一个业务域一个类。例如：
 *     - SafeAreaModel  → 安全间距（statusBarHeight / bottomAvoidHeight）
 *     - LoginStateModel → 登录态（loginStateVersion / userId / token）
 *     - VipStateModel   → VIP 态（isVipState / vipExpireTime）
 *     - <YourDomain>Model → 业务自定义
 *
 * 同时记得：
 *   1. business_common/Index.ets 导出 GlobalState + 各 Model
 *   2. 所有 AppStorage.setOrCreate(...) 旁追加 GlobalState.X.field = v 双写
 *   3. business_common 内部文件 import 用相对路径 './GlobalStateModels'，不能 'business_common'
 */

import { AppStorageV2 } from '@kit.ArkUI';

// ============== 安全间距 ==============

/**
 * 沉浸式安全间距（顶部状态栏 + 底部 home indicator）
 * 通常在 SplashPage 一次性测量后写入，全局其他页面读
 */
@ObservedV2
export class SafeAreaModel {
  @Trace statusBarHeight: number = 36;
  @Trace bottomAvoidHeight: number = 28;
}

// ============== 登录态 ==============

/**
 * 登录状态版本号 — 登录/登出时 +1 触发跨页刷新
 * 配合 @Monitor('login.loginStateVersion') 在依赖登录态的 page 重拉数据
 */
@ObservedV2
export class LoginStateModel {
  @Trace loginStateVersion: number = 0;
}

// ============== VIP 态 ==============

/**
 * VIP 状态 — UserData.persist() 时同步
 * 配合 @ComponentV2 page 直接 reactive 渲染会员标识
 */
@ObservedV2
export class VipStateModel {
  @Trace isVipState: boolean = false;
}

// ============== 单例聚合器 ==============

/**
 * GlobalState — AppStorageV2.connect 单例聚合器。
 *
 * 全局只有一份实例，所有 page 通过 import 直接读写 / connect。
 * 类型注册在第一次访问时由 AppStorageV2.connect 自动完成。
 */
export class GlobalState {
  static readonly safeArea: SafeAreaModel =
    AppStorageV2.connect(SafeAreaModel, () => new SafeAreaModel())!;

  static readonly login: LoginStateModel =
    AppStorageV2.connect(LoginStateModel, () => new LoginStateModel())!;

  static readonly vip: VipStateModel =
    AppStorageV2.connect(VipStateModel, () => new VipStateModel())!;
}
