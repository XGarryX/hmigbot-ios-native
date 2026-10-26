---
name: arkts-library-migration
description: 三方库替代方案查找与决策。当用户提到三方库替代、ohpm 搜索、库迁移、Android 库用什么替代、依赖替换、build.gradle 迁移、npm 包替代等场景时，务必触发此 skill。即使用户只是说"这个库在鸿蒙上有吗"或"用什么替代 Glide"，也应触发。如果用户需要的是完整业务功能（如下拉刷新列表、列表详情页），应优先触发 arkts-pattern-library。
metadata:
  type: domain
  domain: migration
  tags:
  - migration
  - third-party-library
  - ohpm
---
# ArkTS Library Migration — 三方库迁移决策器

## API 版本

本 skill 基于 **API 12+**（HarmonyOS 5.0.0+）。三方库安装使用 ohpm 包管理器。遇到版本兼容性或其他不确定的 ArkTS 知识点，参阅 arkts-knowledge-verifier skill。

---

## 五层查找策略

遇到任何 Android 三方库需要替代时，按以下层次逐级查找：

```
┌─────────────────────────────────────────────────┐
│  Level 1: OpenHarmony 三方库 (ohpm)              │  成本最低，直接 ohpm install
│  搜索渠道：                                       │
│   - ohpm.openharmony.cn                          │
│   - gitee.com/openharmony-tpc                    │
│   - gitee.com/HarmonyOS-tpc                      │
├─────────────────────────────────────────────────┤
│  Level 2: HarmonyOS 原生 API (@kit.*)            │  零依赖，需自写业务代码
│   - @kit.ImageKit (图片处理)                      │
│   - @kit.ArkData (数据库/偏好)                   │
│   - @kit.MediaLibraryKit (媒体库)                │
│   - @kit.CoreFileKit (文件操作)                  │
│   - @kit.NetworkKit (网络请求)                   │
│   - ArkUI 内置组件 (Video/Image/Canvas/Web)      │
├─────────────────────────────────────────────────┤
│  Level 3: NAPI 桥接 C/C++ 开源库                 │  功能完整，集成成本高
│   - FFmpeg (音视频处理)                           │
│   - OpenCV (图像处理)                             │
│   - libjpeg-turbo (图片解码)                     │
├─────────────────────────────────────────────────┤
│  Level 4: WebView + JS 库                        │  开发快，性能有损
│   - Three.js (3D/全景/VR)                        │
│   - Fabric.js (图片编辑画布)                     │
├─────────────────────────────────────────────────┤
│  Level 5: 自研实现或功能降级                       │  最后手段
└─────────────────────────────────────────────────┘
```

---

## 决策树

```
Android 三方库 X
  ├─ ohpm / openharmony-tpc 搜索 → 有直接替代？
  │   ├─ 是 → Level 1: ohpm install（最优）
  │   └─ 否 ↓
  ├─ HarmonyOS 原生 @kit.* API 能覆盖？
  │   ├─ 是 → Level 2: 用原生 API 实现
  │   └─ 否 ↓
  ├─ 该库有 C/C++ 开源核心？
  │   ├─ 是 → Level 3: NAPI 桥接（交叉编译 .so）
  │   └─ 否 ↓
  ├─ JS/Web 生态有等价库？
  │   ├─ 是 → Level 4: ArkWeb 组件 + JS 库
  │   └─ 否 ↓
  └─ Level 5: 自研简化版 / 功能降级 / 标记 Skip
```

---

## 下载 API 选型

```
文件下载用哪个 API？
├─ http.request() + ARRAY_BUFFER
│   ⚠️ 约 5MB 大小限制（错误码 2300023）
│   ✓ 适合小文件（JSON 配置、图标）
├─ http.requestInStream()
│   ❌ 不推荐 — dataEnd 事件在实际设备上不触发
│   ❌ Promise 在收到响应头后即 resolve
└─ request.agent（推荐）
    ✓ 无文件大小限制
    ✓ 稳定的 progress/completed/failed 回调
    ✓ 支持前台/后台模式
```

> 详细对比和代码模板见 `references/download-api-decision.md`

---

## RxJava / EventBus 迁移

> **MUST**：RxJava→async/await 评估表、EventBus 自建 vs 三方对照见 `references/library-mapping-table.md`。

---

## 响应头提取 workaround

`http.request()` 的 `response.header` 类型是 `Object`，ArkTS 禁止用 `[]` 索引访问：

```typescript
// ❌ 错误 — Object 不能用索引访问
const contentType = response.header['content-type'];

// ✓ 正确 — JSON 桥接
const headerStr = JSON.stringify(response.header);
const headerJson = JSON.parse(headerStr);
```

---

## 每层代价分析

| Level | 开发代价 | 维护代价 | 运行性能 | 适用场景 |
|-------|---------|---------|---------|---------|
| **L1 ohpm** | 低 | 低（社区维护） | 高 | 有成熟鸿蒙包的功能 |
| **L2 原生 API** | 中 | 低（系统级） | 高 | 系统已提供基础能力 |
| **L3 NAPI** | 高（需 C/C++ + CMake） | 中（需跟进上游） | 高 | 音视频处理、图像算法等计算密集型 |
| **L4 WebView** | 中 | 中 | 中（JS 桥接开销） | 全景/VR/复杂编辑 UI |
| **L5 自研** | 高 | 高 | 视实现而定 | 无任何替代方案 |

---

## 华为官方四类法

华为推荐按以下分类处理三方库迁移：

| 类型 | 描述 | 处理方式 |
|------|------|---------|
| **A 类** | ohpm 已有鸿蒙版 | 直接 `ohpm install` |
| **B 类** | 无鸿蒙版但有开源替代 | 用 L2 原生 API 或 L3 NAPI |
| **C 类** | 闭源 SDK，厂商已/将适配 | 联系厂商获取鸿蒙版 |
| **D 类** | 无替代方案 | L5 自研或功能降级/Skip |

---

## 技术栈替换表填写指南

迁移项目时，需为每个 Android 依赖填写替换方案表：

### 步骤
1. **提取依赖清单** — 从 `build.gradle` / `build.gradle.kts` / `libs.versions.toml` 提取所有 implementation 依赖
2. **逐个查对照表** — 在 `references/library-mapping-table.md` 中查找，命中则直接填入
3. **未命中走决策树** — 按 L1→L5 逐层尝试
4. **闭源 SDK** — 查看 `references/closed-source-sdk.md` 的处理路径
5. **标注风险等级**：🟢 低（L1-L2 有成熟替代）、🟡 中（L2-L3 API 差异大）、🔴 高（L3-L5 需重写）

### 格式

```markdown
| Android 依赖 | ArkTS 替代 | Level | 风险 | 迁移类型 | 备注 |
|-------------|-----------|-------|------|---------|------|
| Glide 4.16.0 | @ohos/imageknife | L1 | 🟢 | Auto | ohpm install |
| Room 2.6.0 | relationalStore @kit.ArkData | L2 | 🟢 | Semi-Auto | 手写 SQL |
| ExoPlayer 1.1.0 | Video 组件 / AVPlayer | L2 | 🟡 | Manual | 状态机适配 |
```

---

## 常见错误 vs 正确做法

### 错误 1：直接搜索 npm 包

```typescript
// 错误 — npm 包在 ArkTS 中不可用
import axios from 'axios'

// 正确 — 使用 ohpm 包或原生 API
import { http } from '@kit.NetworkKit'
// 或
// ohpm install @ohos/axios
```

### 错误 2：假设 Android 库有同名鸿蒙版

```
// 错误 — 直接假设存在
ohpm install glide  // 不存在

// 正确 — 先查对照表，再走决策树
// Glide → @ohos/imageknife（L1）
ohpm install @ohos/imageknife
```

### 错误 3：闭源 SDK 直接标记为不可迁移

```
// 错误 — 直接放弃
微信 SDK → Skip

// 正确 — 先查厂商适配状态，再考虑 JS-Bridge 过渡
微信 SDK → 联系厂商获取鸿蒙版（类型 C）
         → 临时方案：ArkWeb + JS-Bridge
```

---

## 生成检查清单

- [ ] 每个 Android 依赖都有对应的替代方案或标记 Skip
- [ ] 每个依赖标注了 Level（L1-L5）
- [ ] 每个依赖标注了风险等级（🟢/🟡/🔴）
- [ ] 高风险项（🔴）有缓解策略
- [ ] 闭源 SDK 有厂商联系记录或替代方案
- [ ] ohpm 包安装命令正确
- [ ] 没有使用 npm 包

---

## 跨 Skill 协作

| 需要什么 | 读取哪里 |
|---------|---------|
| 网络请求替代方案代码模板 | `arkts-data-layer/references/network-service.md` |
| 数据库替代方案代码模板 | `arkts-data-layer/references/rdbstore-dao-patterns.md` |
| 系统 API 使用指南 | `arkts-system-capabilities/SKILL.md` |
| 验证 API 兼容性 | `arkts-knowledge-verifier/SKILL.md` |
| 完整项目依赖配置 | `arkts-project-scaffolder/SKILL.md` |
| 媒体播放 | `arkts-media-playback/SKILL.md` |
| 文件下载 | `arkts-download-manager/SKILL.md` |
| Android UI 对齐 | `arkts-ui-alignment/SKILL.md` |

> 完整路由矩阵见 `arkts-knowledge-verifier/references/skill-routing-guide.md`

---

## References

- `references/library-mapping-table.md` — 50+ 库完整对照表（7 个分类：图片/视频/网络/UI/工具/编辑/商业SDK）
- `references/ohpm-search-guide.md` — ohpm 搜索渠道 + 质量评估清单 + 已验证库列表
- `references/napi-compile-guide.md` — C/C++ 库交叉编译方法（CMake + oh-compile-script）
- `references/closed-source-sdk.md` — 闭源 SDK 三种处理路径 + JS-Bridge 过渡方案代码模板
- `references/download-api-decision.md` — http.request vs requestInStream vs request.agent 对比 + 错误码
- 遇到版本兼容性或其他不确定的 ArkTS 知识点，参阅 **arkts-knowledge-verifier** skill
