---
name: arkts-ad
description: Android 广告 SDK 迁移到 HarmonyOS ArkTS 的全流程指导。识别 Android 项目使用的主流广告三方库（穿山甲 CSJ/Pangle、优量汇 GDT、快手 KS、华为 HMS Ads、百度联盟、GroMore 聚合等），匹配鸿蒙端可用 SDK，引导下载 HAR / ohpm 配置 / module.json5 权限明示与用户选择 / EntryAbility 初始化 / WindowStage 绑定 / API 1:1 适配 / 服务层抽象 / 验证排障。当用户提到"广告 SDK 接入 / 广告库迁移 / 检测广告 SDK / 鸿蒙广告 / Android 广告库迁移 / 穿山甲 / CSJ / Pangle / GroMore / GDT / 优量汇 / KS / 快手广告 / HMS Ads / 华为广告 / 百度联盟 / 开屏 / 插屏 / 信息流 / Banner / 激励视频 / 热启动广告 / Tab 切换广告 / 广告不展示 / HAR / ohpm / WindowStage / init / start / 广告权限 / 广告频控 / 广告隐私"等场景时触发本 skill。
metadata:
  type: domain
  domain: system
  tags:
  - domain
  - ad
  - sdk
  - third-party
  - csj
  - gdt
  - ks
  - hms-ads
  - baidu
  - gromore
---
# ArkTS 广告 SDK 迁移

将 Android 广告体系迁移到 HarmonyOS ArkTS 的全流程：detect 识别 → catalog 匹配 → 下载集成（含权限明示与用户选择）→ API 1:1 适配 → 验证排障。

本 skill 不是 Fitness 专用 skill。Fitness 项目中的 `TabBarComponent` / `MainPage` / `AdService` / `TabAdController` 等只作为参考范例，不能作为通用前提。

## When To Use

当用户提到以下任一场景时触发：

- ArkTS / HarmonyOS 广告 SDK 接入或迁移
- 穿山甲 / CSJ / Pangle / GroMore / 优量汇 / GDT / 快手 / KS / 百度联盟 / HMS Ads / 华为广告
- Android 广告 SDK 检测 / 识别 / 梳理
- 开屏 / 热启动 / 插屏 / Tab 切换插屏 / 信息流 / Banner / 激励视频 / 全屏 / Draw / 沉浸式视频
- 广告不展示 / SDK 初始化失败 / `*.start()` 失败 / HAR 依赖失败 / `ohpm` 解析到错误包 / `load` 回调不触发 / `show` 无反应 / `WindowStage` 缺失 / 广告权限 / 频控规则
- 出现关键词：`AdService` / `AdController` / `openadsdk` / `adapter_gdt` / `adapter_ks` / `showFullAd` / `WindowStage` 绑定 / 广告频控

## Core Rules

必须遵守：

1. 页面和组件不得直接调用三方广告 SDK API。它们必须调用项目自有服务（例如 `AdService`）或项目已有广告抽象层。
2. 插屏、全屏、激励视频等需要窗口宿主的广告，必须等 Ability 层绑定 `WindowStage` 后再展示。
3. SDK 初始化和启动/激活步骤是两个独立关口。排查 load/show 失败前必须同时检查通用 init 流程和具体 SDK 的启动/激活流程；例如 CSJ 需要检查 `init()` 和 `CSJAdSdk.start()`。
4. HarmonyOS 广告位 ID 必须视为平台专属配置，不能直接复用 Android 广告位 ID。
5. 所有广告失败都必须从用户业务流程角度降级为 no-op：不展示广告，但启动、Tab 切换、列表加载、播放恢复、奖励结算等业务继续。
6. 不绕过隐私合规。广告相关敏感权限、OAID、跟踪授权、定位能力必须绑定到应用隐私协议同意流程。
7. **SDK 文档列出的权限不全量加**。每个权限必须经用户在 Stage 2.1 显式确认。默认仅加"必需"项；"可选"项（含设备标识 / OAID / 定位 / Wi-Fi 信息）默认不加，由用户基于业务 + 商务 + 隐私合规权衡。
8. **SDK 信息有时效性**。每个 sdk-*.md 顶部的「最后核对」日期超过 6 个月时，主流程必须显式提示用户访问官方索引页核对版本号 / API / 下载 URL，不得静默使用过期信息。

## Inputs To Collect

修改代码前先收集：

- HarmonyOS 项目根目录
- Android 源码根目录（用于 Stage 0 detect）
- 现有 ArkTS 广告文件（如 `AdService` / `AdController` / `TabAdController` / `AdCardComponent`）
- 依赖配置文件：根目录 `oh-package.json5` / `entry/oh-package.json5` / `entry/oh-package-lock.json5`
- HarmonyOS 模块配置：`entry/src/main/module.json5`
- `entry/libs/` 下已有广告 SDK 库
- Android 侧广告 SDK 依赖、封装类、初始化入口、广告场景代码、频控代码、上层触发链路
- 本次变更目标广告场景
- 是否已有隐私协议流程，以及同意状态存储位置

优先用 `rg` / `rg --files` 查找文件和关键词。

## Workflow

### Stage 0: Detect — 识别 Android 项目使用的广告 SDK

加载 `references/detect-commands.md`，按其中的 4 类扫描命令在 Android 项目根目录跑 grep：

1. Gradle 依赖扫描（最权威）
2. SDK init 调用扫描（佐证）
3. Manifest 权限佐证（弱信号）
4. ProGuard keep 规则佐证（弱信号）

输出"使用的 SDK 清单"按以下格式：

| Android dep | 命中位置 | 对应 catalog 行 | 状态 |
|---|---|---|---|
| ... | ... | ... | ... |

未命中任何 SDK → 输出"未识别到广告 SDK 使用，跳过迁移"，结束 skill。

### Stage 1: 匹配 + 鲜度提示

加载 `references/sdk-catalog.md`，逐个命中 SDK 查表得到鸿蒙端可用性 + 对应 sdk-*.md 文件名。

显式检查每个对应 sdk-*.md 顶部的「最后核对」日期：超过 6 个月（相对当前日期）时，主流程必须输出：

```
警示：sdk-{name}.md 最后核对日期为 YYYY-MM，已超过 6 个月。
请先访问官方索引页 {URL} 核对版本号 / API / 下载 URL 是否变更，再继续。
```

按 catalog 中"鸿蒙端状态"分支：

- ✅ 原生 / ✅ 有 HAR → 进入 Stage 2，加载对应 `sdk-<name>.md`
- ⚠️ 待核实 → 引导用户访问官方索引页确认；如确认有可用 HAR，走 `generic-sdk-template.md` 兜底
- ❌ 暂无对应 → 提示替代方案：HMS Ads 兜底 / Web H5 落地页 / 移除该场景；询问用户决策

未列入 catalog 的 SDK：直接走 `generic-sdk-template.md` 的 §0 流程。

### Stage 2: 下载 + 集成（每命中 SDK 循环）

#### 2.0 下载 HAR + ohpm 配置

加载 `references/sdk-<name>.md` §1。输出：

- 官方 HAR 下载页 URL（用户自行下载，skill 不执行外部网络请求）
- HAR 放置位置 `entry/libs/{har-name}-X.Y.Z.har`
- `entry/oh-package.json5` 引用片段
- 根 `oh-package.json5` overrides 配置（如有传递依赖冲突）

提示：必须显式核对 oh-package-lock.json5 中该包是否解析到本地 HAR 文件，而非远端版本。

#### 2.1 权限确认 ⭐

加载 `references/sdk-<name>.md` §2 的权限表，向用户展示并逐项确认：

```
该 SDK 文档列出 N 个权限。请逐项确认：

[1] ohos.permission.INTERNET
    作用：广告请求 + 物料下载
    是否必需：✅ 必需
    默认推荐：✅ 加
    隐私影响：无
    → 你的选择？(✅ 加 / ❌ 不加)

[2] ohos.permission.LOCATION
    作用：LBS 定向广告（精度提升 eCPM）
    是否必需：❌ 可选
    默认推荐：❌ 不加
    隐私影响：高 — 需用户授权 + 写 reason + 绑定隐私协议
    → 你的选择？(✅ 加 / ❌ 不加)

...
```

输出最终的 module.json5 `requestPermissions` 片段（仅含用户确认 ✅ 加 的项）+ 必要的 reason 字符串资源。

高隐私权限（LOCATION / 设备标识 / OAID）额外提示：必须绑定到隐私协议同意流程，且仅在用户同意后才发起权限申请。

#### 2.2 module.json5 写入指导

输出"在 `entry/src/main/module.json5` 的 `module.requestPermissions` 数组中追加以下条目"指令 + 完整代码片段。skill 不直接改文件。

#### 2.3 EntryAbility 初始化

加载 sdk-<name>.md §3，输出 init + start 代码片段（绑定到 EntryAbility.onCreate，前置隐私同意检查）。

#### 2.4 WindowStage 绑定

加载 sdk-<name>.md §4，如该 SDK 包含需 windowStage 的广告类型（全屏/插屏/激励），输出绑定代码（绑定到 EntryAbility.onWindowStageCreate）。

### Stage 3: API 适配

加载 `references/sdk-<name>.md` §5（API 1:1 对照表）+ §6（开屏完整 before/after）。

向用户输出：
- API 对照表（5 种广告类型每种 1 条）
- 开屏广告完整 before/after 代码模板
- 提示："其它广告类型（插屏/激励/信息流/Banner）按 §5 对照表自行映射"

service 层抽象沿用现有 AdService / AdConfig / 隐私控制器架构（保留现状）。回调统一适配为 `onShow` / `onClick` / `onSkip` / `onComplete` / `onClose` / `onError`。

UI 组件事件 → 页面级回调 → 场景控制器（频控门禁）→ AdService 方法 → SDK 回调 → 业务继续或 no-op 降级。

### Stage 4: 验证与排障

广告不展示时，按以下顺序检查：

1. 本地 HAR 文件存在，并被 `entry/oh-package.json5` 引用。
2. 根目录 `oh-package.json5` 使用 `overrides` 重定向有问题的传递依赖。
3. `module.json5` 声明了必要权限和权限 reason。
4. 隐私协议同意状态允许 SDK 或权限申请流程执行。
5. `AdService.init(context)` 已执行。
6. 具体 SDK 的启动/激活步骤成功；例如 CSJ 场景下 `CSJAdSdk.start()` 成功，或日志中出现预期成功码。
7. 全屏、插屏、激励广告展示前已绑定 `WindowStage`。
8. 广告位 ID 是 Harmony 专属广告位，并存在于广告平台。
9. 频控控制器没有跳过本次请求。
10. `load` 回调触发。
11. `show` 回调触发。
12. SDK 日志和项目日志能按场景和广告位对应起来。
13. 失败路径会降级为 no-op，业务流程继续。

## Output Format

每次执行后输出：

- Stage 0 detect 结果（已识别 SDK 清单）
- Stage 1 匹配结果（每 SDK 鸿蒙端状态 + 鲜度警示）
- Stage 2 集成产出（每 SDK 的下载指令 / 权限选择 / module.json5 片段 / EntryAbility 代码）
- Stage 3 API 适配产出（每 SDK 的对照表引用 + 开屏完整代码）
- 已检查文件
- 已修改文件或建议修改文件
- 上层触发链路
- 频控行为
- 未实现广告场景及占位策略
- 验证命令和日志关键词
- 残留风险

## Common Failure Patterns

- 本地 HAR 存在，但 `ohpm` 从 adapter 包解析了远端传递依赖
- 调用了 `init()`，但缺少 `start()`，或 `start()` 失败
- 绑定 `WindowStage` 前调用了 `showFullAd`
- 复用了 Android 广告位 ID
- 页面/组件直接调用 SDK API，绕过服务层降级
- 频控正常拦截，却被误判为 SDK 失败
- 隐私协议未同意，因此权限或 SDK 启动路径被有意阻断
- 广告回调已触发，但业务代码在错误时机增加展示计数
- 激励视频在 load/show 时发放奖励，而不是在完成回调后发放
- SDK 文档列出 10 个权限被全量加进 module.json5（未经 Stage 2.1 用户确认）
- sdk-*.md 最后核对日期已过期但未触发警示

## References

- `references/sdk-catalog.md` — 严选 6 SDK 索引表
- `references/detect-commands.md` — Android 端识别命令清单
- `references/sdk-hms-ads.md` — 华为 HMS Ads
- `references/sdk-csj.md` — 穿山甲 CSJ / Pangle
- `references/sdk-gdt.md` — 优量汇 GDT
- `references/sdk-ks.md` — 快手 KS
- `references/sdk-baidu.md` — 百度联盟（⚠️ 待核实）
- `references/sdk-gromore.md` — GroMore 聚合
- `references/generic-sdk-template.md` — 未列入 SDK 通用对接模板


---

## See Also

- [arkts-login](../arkts-login/SKILL.md) / [arkts-payment](../arkts-payment/SKILL.md) / [arkts-customer-service](../arkts-customer-service/SKILL.md) — 同属第三方 SDK 系列
- [arkts-immersive-safearea](../arkts-immersive-safearea/SKILL.md) — 开屏 / 插屏广告全屏适配
