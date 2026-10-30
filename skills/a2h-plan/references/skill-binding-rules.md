> **当前发行边界：旧设备/视觉后端延期，官方应用测试单独取证。** `arkts-scenario-runner`、`arkts-visual-verify`、`arkts-ui-verifier`、`ios-screenshot-analyzer`（及历史 Android 截图别名）和 `scenario-builder` / `visual-fixer` / `visual-fixer-reviewer` 尚未恢复交付，不调用或要求补装这些旧后端，也不因其缺件阻断基本转换/构建/报告。指定应用/模拟器的官方截图、控件查询和固定回放按执行交界合同及实际适配入口运行，不因旧后端延期或缺少桌面屏幕权限一概记 not_run。许可、宿主可用、已实现、实际执行与验收结果分开；缺真实后端/输入仅限制对应检查。外部原始证据核对版本、配置、范围和来源，未执行不记 PASS，真实产品失败保留。下文旧调用/目录仅为兼容映射。

# iOS 迁移的目标技能绑定

按 spec 行为与接口绑定；关键词只作候选，不代表 SDK 可用或行为等价。每项读取完整技能和适用参考。

| 需求/源事实 | 包内技能 |
|---|---|
| 工程初始化 | arkts-project-scaffolder |
| 资源/本地化 | ios-resources-convert, arkts-i18n |
| 页面转换 | ios-ui-to-arkui, arkts-component-builder |
| 状态所有权/Binding/模型 | arkts-state-manager |
| 约束/对齐/安全区 | arkts-ui-alignment, arkts-immersive-safearea |
| 导航/模态/深链 | arkts-navigation-builder |
| 网络/持久化/数据模型 | arkts-data-layer |
| 网络契约联调 | arkts-network-troubleshoot |
| 平台调用/权限/文件 | arkts-system-capabilities |
| 三方依赖 | arkts-library-migration, hmos-sdk-docs |
| 登录/授权 | arkts-login |
| 支付/订阅 | arkts-payment |
| 广告 | arkts-ad |
| 客服/IM | arkts-customer-service |
| 视频/音频 | arkts-video-playback, arkts-media-playback |
| 动画 | arkts-animation-migrate, arkts-animation-builder |
| Web 内容 | arkts-webview |
| 下载 | arkts-download-manager |
| 身份 | arkts-app-identity |
| 无障碍/字号/多语言 | arkts-accessibility, arkts-large-font, arkts-i18n |
| 多设备/窗口/深色 | arkts-multi-device, arkts-multi-window, arkts-dark-mode |
| 主题/字面量 | arkts-design-tokens-extractor |
| 文本截断 | arkts-text-truncation, arkts-truncation-fix |
| 图片尺寸 | arkts-icon-sizing |
| 结构/编译 | arkts-structural-closure, hmos-fix-build-errors |
| UI/功能覆盖 | arkts-ui-coverage-auditor, arkts-feature-coverage-auditor |
| 逻辑 | arkts-ut-verifier（仅按本次明确选择与实际能力） |
| 交互/视觉（延期） | arkts-ui-verifier / arkts-visual-verify 仅未来标记；当前不强绑、不派发，deferred/not_run，可消费开发者外部证据 |

未有目标方案的接缝进入 decision/placeholder，不能因出现厂商名字视为适配完成。

## 基于 meta.json 字段的强绑规则（HARD-RULE）

以下规则**基于 meta.json 字段而非词汇匹配触发**，比词汇触发更可靠（不依赖 spec 文档措辞）。这类规则用于解决「iOS 源码无信号但 HarmonyOS 必须显式」的范式差异。

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
- `page_type` 由 ios-ui-analyzer 按真实呈现/生命周期事实判定并在 meta 中注明证据（4 类：`full_screen_page` / `modal_overlay` / `dialog` / `sub_component`）
- 不依赖词汇匹配——即使 spec / Slice 任务描述里完全没出现「沉浸式」「安全区」等关键词，只要任一 page 是 `full_screen_page`，本 skill 必须出现在 suggested_skills
- 设计依据：iOS 默认系统处理状态栏避让，源码层面无信号；HarmonyOS 全屏页必须显式四件套，否则系统栏遮挡内容（详见 `docs/immersive-safearea-coupling.md`）

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
