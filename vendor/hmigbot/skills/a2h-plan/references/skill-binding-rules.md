<!-- when: §4 给 task 标注 suggested_skills 时加载 -->
<!-- topics: suggested_skills, task→skill 映射, Domain Skill 绑定, 特殊领域追加 -->
<!-- 分工: 本表是 task→skill 映射数据的唯一权威(plan 期标注 + execute runtime 漏标兜底共用同一张表); execute 派发前的覆盖/注入/降级行为规则见 a2h-execute references/skill-binding-override.md -->

# suggested_skills 主映射表

根据 task 内容 / 业务类别匹配到对应 Domain Skill。一个 task 可标注多个 skill（按执行顺序排列）。

「典型 Android 厂商 SDK」列同时供 a2h-plan §Step 4.1 三方 SDK 决策树使用：feature spec 中提到的 SDK 命中本列任一关键词 → 直接 `suggested_skills` 追加对应 skill，**不登记 placeholder-registry**；未命中 → 登记 `kind=thirdparty-sdk` 等待适配方案到位。

| Task 内容 / 业务类别（关键词） | suggested_skill | 典型 Android 厂商 SDK / 库                     |
|------------------------------|----------------|-------------------------------------------|
| UI 页面转换 | `a2h-activity-converter` (agent) | —                                         |
| 项目结构 / 模块配置 | `arkts-project-scaffolder` | —                                         |
| 第三方库替换 | `arkts-library-migration` | —                                         |
| 三方 SDK 集成事实（初始化/API 签名/权限/ohpm 包名版本） | `hmos-sdk-docs` | 极光推送 / 环信 / 融云 / 声网 / 友盟 / 支付宝 / 穿山甲 / 高德 |
| 数据库 / DAO / Model / 网络请求 / HTTP / 持久化 | `arkts-data-layer` | Room / Retrofit / OkHttp / SQLite         |
| 网络层联调 / 拦截器签名（HMAC）/ 响应 unwrap / API contract 对账 / 抓包验证 / 启动期初始化排障 | `arkts-network-troubleshoot` | OkHttp Interceptor / MMKV / 自定义签名链        |
| 文件操作 / 权限 / 扫码 / 震动 / 相机 / PhotoViewPicker / 系统能力 | `arkts-system-capabilities` | Zxing / 系统 API                            |
| 导航框架 / 路由 | `arkts-navigation-builder` | Navigation Compose / ARouter              |
| 状态管理 / 数据绑定 / 全局状态 / 持久化偏好 | `arkts-state-manager` | LiveData / Flow / SharedPreferences       |
| 页面组件 / 列表 | `arkts-component-builder` | —                                         |
| 音频播放 / AVPlayer / 后台播放 | `arkts-media-playback` | Android MediaPlayer                       |
| 大文件下载 / 断点续传 | `arkts-download-manager` | OkDownload / FileDownloader               |
| 动画 / 转场 | `arkts-animation-builder` | —                                         |
| Lottie / 帧动画 / 共享元素转场 / SVGA / ObjectAnimator | `arkts-animation-migrate` | Lottie / SVGA                             |
| 编译修复 | `hmos-builder` (agent)；Stage 1 Batch / Stage 3 group 收尾 subagent 内改调 `hmos-fix-build-errors` | —                                         |
| API 验证 | `arkts-knowledge-verifier` | —                                         |
| App 身份配置 | `arkts-app-identity` | —                                         |
| 资源转换 | `android2hmos-resources-convert` | —                                         |
| UI 页面转换（含 FrameLayout/层叠/复杂对齐） | `arkts-ui-alignment` | Stage 1 converter / Step 3a 必带——.align 误用 60 处事故后 HARD |
| 文本截断/省略号缺陷修复 | `arkts-truncation-fix` | Step 3a UI 修复语境按需（供给线闸 0824：OFF skill 零点名=知识孤儿） |
| 安卓截图辅助分析（ui-snapshots 含截图时） | `android-screenshot-analyzer` | spec Phase A 按需；快照纯合成（无截图）时不适用 |
| 公共组件库 | `arkts-component-builder`, `arkts-pattern-library` | —                                         |
| 客服 / IM / 在线聊天 | `arkts-customer-service` | 七鱼 / 云信 / 腾讯云 IM                          |
| 沉浸式 / 安全区 / 状态栏 / 全屏背景 / NavDestination 模板 | `arkts-immersive-safearea` | —                                         |
| **任一涉及 page** 的 Slice，且该 page 的 meta.json 含 `needs_immersive_safearea: true` | **强绑** `arkts-immersive-safearea`| —                                         |
| 登录 / 授权 / OAuth / 一键登录 / 第三方账号 | `arkts-login` | 微信登录 / 支付宝登录 / 华为账号                       |
| 支付 / 收银台 / 订单 / IAP / 订阅签约 | `arkts-payment` | 微信支付 / 支付宝 / 华为 IAP                       |
| 广告 SDK / 开屏 / 插屏 / 信息流 / 激励视频 / Banner / Splash | `arkts-ad` | 穿山甲 / 优量汇 / 快手 / GroMore / 百度联盟 / HMS Ads |
| 魔鬼数字 / 硬编码 / 设计系统 / DesignTokens / 资源化 / 字面量去重 | `arkts-design-tokens-extractor` | —                                         |
| 视频 / 视频播放 / XComponent / Surface / 横屏播放器 / Letterbox / PiP | `arkts-video-playback` | ExoPlayer / Aliyun Player                 |
| UI 覆盖率 / 漏页 / 补页 / 子页对齐 / 二三层 UI | `arkts-ui-coverage-auditor` | —                                         |
| 多设备 / 平板 / 折叠屏 / 车机 / TV / 断点 sm/md/lg/xl | `arkts-multi-device` | Android Adaptive layouts                  |
| 分屏 / 自由窗口 / 悬浮窗 / PiP / UIExtension | `arkts-multi-window` | —                                         |
| 深色模式 / dark / resources/dark / ColorMode | `arkts-dark-mode` | DayNight                                  |
| 大字体 / 字体缩放 / fontSizeScale | `arkts-large-font` | —                                         |
| 无障碍 / 适老化 / 读屏 / 焦点 / tabIndex / 触达热区 | `arkts-accessibility` | —                                         |
| 文本截断 / Ellipsis / maxLines / 弹窗超屏裁切 | `arkts-text-truncation` | —                                         |
| 国际化 / 多语言 | `arkts-i18n` | —                                         |
| 架构重构 / 整改 / 私仓接入 / develop_rule / lib_common | `arkts-architecture-refactor` | —                                         |
| API 清单 / 接口梳理 / 接口文档 / 有哪些 API | `android-api-inventory` | —                                         |
| 页面关系树 / 导航关系图 / app-relationship | `app-relationship-tree` | —                                         |
| 视觉对比 / 截图验证 / adb hdc 截图 | `arkts-visual-verify` | —                                         |
| WebView / Web 组件 / 网页加载 / CSS 注入 / JS 注入 / 页内搜索 / 页面翻译 / TTS 朗读 | `arkts-webview` | 系统 WebView / X5 内核 / Crosswalk            |

**匹配规则**：feature spec 中提到的关键词命中"Task 内容 / 业务类别"列或"典型 Android 厂商 SDK"列任一时，按对应 skill 处理；同时含多个关键词时取最具体的。

**未命中本表的 SDK**（如自研、小众厂商、埋点、风控等本仓尚未覆盖类别）：
- 登记 `kind=thirdparty-sdk` placeholder
- `trigger_condition = <业务类别> SDK 入仓`（描述业务类别即可，不强依赖具体 skill 名；开发者后续可通过任一形式提供适配方案）
- 例：`trigger_condition = 埋点 SDK 入仓` / `trigger_condition = 风控 SDK 入仓` / `trigger_condition = 火山引擎 AppLog SDK 入仓`
- 适配方案到位的多种形式（任一命中即 resolved）：
  ① 新 skill 入仓 arkts-skills/skills/
  ② 私仓 har 包入仓 oh_modules/
  ③ 官方 SDK 适配文档发布
  ④ 团队内部决策完成（记入 spec/migration-decisions.md）

---

## 基于 meta.json 字段的强绑规则（HARD-RULE）

以下规则**基于 meta.json 字段而非词汇匹配触发**，比词汇触发更可靠（不依赖 spec 文档措辞）。这类规则用于解决「Android 源码无信号但 HarmonyOS 必须显式」的范式差异。

### Rule IS-1: 全屏页 ⇒ 必须绑 arkts-immersive-safearea

**触发条件**：Slice 涉及的任一 page 的 `meta.json` 满足：

```json
{
  "page_type": "full_screen_page",
  "needs_immersive_safearea": true
}
```

**强绑 skill**：`arkts-immersive-safearea`

**说明**：
- `page_type` 由 `android-ui-graph-builder/scripts/synthesize_meta_json.py` 的 `detect_page_type()` 自动判定（4 类：`full_screen_page` / `modal_overlay` / `dialog` / `sub_component`）
- 不依赖词汇匹配——即使 spec / Slice 任务描述里完全没出现「沉浸式」「安全区」等关键词，只要任一 page 是 `full_screen_page`，本 skill 必须出现在 suggested_skills
- 设计依据：Android 默认系统处理状态栏避让，源码层面无信号；HarmonyOS 全屏页必须显式四件套，否则系统栏遮挡内容（详见 `docs/immersive-safearea-coupling.md`）

**校验时机**：a2h-plan §7 coverage-matrix 输出前；缺绑 → plan FAIL。

---

## 风格 Skills 追加（style_set != none 时）

读取 spec 文档 `style_set` 字段（缺失视为 `none`）：`none` → 不追加；非 none（如 `wfhc-standard`）→ 按 task 领域从风格集选取追加：

| Task 内容 | 追加的风格 Skill |
|-----------|-----------------|
| UI 页面 / 组件 | style-set 中 domain=ui 的风格 skill |
| 状态管理 / ViewModel | domain=state |
| 导航 / 路由 | domain=navigation |
| 网络请求 | domain=data |
| 项目结构 / 配置 | domain=engineering |
| 特殊领域（扫描等） | domain=system |

选取依据：扫描 skills 目录中 frontmatter `style-set` 值匹配的条目，按 `domain` 字段与 task 领域匹配；一个 task 可追加多个。风格 skills 追加在 domain skills 之后（风格规则叠加而非覆盖基线）。
