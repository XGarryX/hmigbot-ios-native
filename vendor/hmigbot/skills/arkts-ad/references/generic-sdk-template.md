# 未列入清单 SDK 的通用对接模板

> 当 detect 命中的 SDK 不在 sdk-catalog.md 严选 6 个之内（如 Mintegral / TopOn / Unity Ads / AdMob / Facebook Audience），按本模板兜底接入。
>
> 本模板是抽象指导，不含 SDK-specific API 表与完整 before/after 代码（这些由严选 SDK 的 sdk-*.md 提供）。

---

## 0. 前置：确认鸿蒙端可用性

访问 SDK 官方文档（developer 站 / docs / SDK 下载页），按以下顺序检索：

1. 搜"HarmonyOS"或"鸿蒙"关键字
2. 搜"OpenHarmony"
3. 搜"HAR"或".har"
4. 找官方"平台支持矩阵"页面

**结论分支**：
- ✅ 有官方 HAR → 继续 §1
- ⚠️ 文档未提及但社区有 port → 用户自评风险，可选 §1 谨慎接入或走 §0.E 替代方案
- ❌ 明确无对应 → 走 §0.E

### §0.E 鸿蒙端无对应时的替代方案

按业务影响降级：

1. **HMS Ads 兜底**：把该 SDK 承担的广告位（开屏 / 插屏 / 激励 / 信息流 / Banner）改用华为 HMS Ads（参考 sdk-hms-ads.md），并接受流量收益变化
2. **Web H5 落地页**：广告内容由后端动态返回 H5 链接，鸿蒙 Web 组件加载（保留广告业务但失去 SDK 级追踪）
3. **移除该广告场景**：在鸿蒙端跳过此广告，业务降级为 no-op（与 SKILL.md Core Rule 5 一致）

---

## 1. 下载 HAR

- 找官方 HAR 下载入口（通常在"开发者中心 / SDK 下载 / 资源中心"页面）
- 下载到 `entry/libs/{har-name}-X.Y.Z.har`

## 2. ohpm 配置

`entry/oh-package.json5` 增加：

```json5
"dependencies": {
  "{official-ohpm-pkg-name}": "file:libs/{har-name}-X.Y.Z.har"
}
```

如 SDK 文档提到传递依赖（如 adapter HAR 内部声明远端版本），在**根目录** `oh-package.json5` 用 `overrides` 重定向：

```json5
"overrides": {
  "{transitive-pkg-name}": "file:entry/libs/{har-name}-X.Y.Z.har"
}
```

## 3. module.json5 权限确认

按 SDK 官方文档列出"必需 / 推荐 / 可选"三类权限，与用户逐项确认：

- 默认仅加"必需"项
- "可选"项（含定位 / 设备标识 / OAID）默认不加，由用户基于商务需要 + 隐私合规权衡
- 高隐私权限必须绑定隐私协议同意流程

## 4. EntryAbility 初始化

按 SDK 文档要求在 `EntryAbility.onCreate` 中：

```typescript
// 1. 隐私同意检查 — 未同意时跳过 init
if (!privacyService.isAccepted()) return;

// 2. 调 SDK 提供的 init 方法
{SDKName}.init(this.context, {appId: '...'});

// 3. 如 SDK 区分 init 与 start/active，依次调用
{SDKName}.start();

// 4. WindowStage 绑定（onWindowStageCreate）
adService.bindWindowStage(windowStage);
```

## 5. service 层包装

- 在 `services/AdService.ets` 增加该 SDK 对应的 load/show 方法
- 统一回调适配为 `onShow` / `onClick` / `onSkip` / `onComplete` / `onClose` / `onError`
- UI 组件不直接调 SDK API，只调 AdService

## 6. 验证

跑 SKILL.md Stage 4 的"广告不展示 13 步排查清单"，重点关注：
- HAR 是否被 ohpm 解析到（lock 文件确认）
- init / start 是否成功
- 隐私同意状态是否允许
- 广告位 ID 是否申请的鸿蒙专属 ID

## 7. 已知陷阱（通用）

- adapter HAR 传递依赖必须用根 oh-package.json5 overrides
- WindowStage 绑定前调 showFullAd 会失败
- 复用 Android 广告位 ID 不可用，必须申请鸿蒙专属广告位
- 隐私同意前禁止 init / start
