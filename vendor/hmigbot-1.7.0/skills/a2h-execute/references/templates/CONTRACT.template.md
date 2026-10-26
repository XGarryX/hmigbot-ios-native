<!-- ============================================================
TEMPLATE-HEADER —— 实例化时删除本块（含本行至 TEMPLATE-HEADER-END 行）及全部 GAP 注释行

CONTRACT.template.md —— 项目实现契约模板（A2H v2）
底稿：docs/skills_optimization_818/design/corpus/CONTRACT.md（dynamic1 实测件，7 节结构原样保留）
实例化产物：<project>/spec/CONTRACT.md（落工程 spec/ 随工程持久，禁落会话 scratchpad——2 册 §2.6）
消费方：全部 wave 的实现/审计/修复代理（prompt ② 段注入其路径，代理开工前全文读取）

槽位表（{{SLOT}} 形态；全部必填，填参后不得残留 "{{" 字样——生成侧应 grep 校验）：
  {{APP_NAME}}             应用人读名（domain-map.json#app）
  {{PROJECT_ROOT}}         HarmonyOS 工程根绝对路径（workflow-params.json#project.root）
  {{ANDROID_SRC}}          Android 源码根绝对路径（workflow-params.json#project.android_src）
  {{API_TARGET}}           目标 API 行，如 "API 6.0.1(21)"
  {{MODULE_NAME}}          模块名，通常 "entry"（多 module 工程按 module 各生成一份）
  {{ETS_SOURCE_ROOT}}      ets 源根相对路径，如 "entry/src/main/ets"
  {{SPEC_DOMAINS_DIR}}     域 spec 目录路径，如 "<PROJECT_ROOT>/spec/domains"
  {{POLLUTION_BLOCKLIST}}  禁读路径列表（workflow-params.json#pollution_blocklist 渲染，每行 "- `<路径>`"）
  {{ROUTES_TABLE}}         路由表 markdown 表（Routes 常量 | 页面文件 | 参数类），blueprint 路由清单渲染
  {{DESIGN_WIDTH}}         设计宽度数值（vp），如 360
  {{RAWFILE_ASSETS}}       rawfile 资产清单（资源转换产物渲染，每行 "- `<路径>` —— <用途>"）
  {{STRING_STRATEGY}}      字符串策略一句话（如 "应用 zh-only：优先按 spec 硬编码中文字面量；
                           $r('app.string.<name>') 同样存在但仅在动态取值时使用"）
  {{INFRA_QUICKREF}}       共享 infra 速查块（contracts.json#modules[status!=planned] 渲染：
                           每文件一行 "- `<文件>` -> <导出符号+签名要点>"，seed 层在前）
  {{ARKTS_STRICT_REF}}     arkts-strict 片段的解析后路径（a2h-execute/references/fragments/arkts-strict.md，
                           经 ARKTS_SKILL_DIR 解析为实际可读路径）
TEMPLATE-HEADER-END
============================================================ -->
<!-- GAP: CONTRACT.md 的填参执行者未在 IMPL-CONTRACT §8 CLI 表中出现（generate_waves.py 无对应
     参数，§1 只说"由 CONTRACT.template.md 填参生成"）；本模板按"生成链在审批门后、
     wave-infra 前实例化"编写，上方槽位表即填参契约——script-S1 或 blueprint 阶段脚本需认领。 -->

# {{APP_NAME}} → HarmonyOS 实现契约（所有实现/审计/修复代理必须遵守）

工程：{{PROJECT_ROOT}}（HarmonyOS {{MODULE_NAME}} HAP，ArkTS，{{API_TARGET}}）
域 spec：{{SPEC_DOMAINS_DIR}}/ —— 先读你任务书指定的 spec；spec 有歧义时回读 Android 源码取精确值。
Android 源码（仅按 spec 引证回读）：{{ANDROID_SRC}}

防污染红线（与 prompt ① 红线段同源）：本次是全新迁移，**禁止读取**以下路径，读到旧迁移产物即污染：
{{POLLUTION_BLOCKLIST}}

## 1. File layout（{{ETS_SOURCE_ROOT}}/）

- `pages/<Name>Page.ets` —— 每路由一个；若已有 stub：只替换内容，**必须保留**导出的 `<Name>PageBuilder` @Builder 与 struct 名。页面 = NavDestination，统一 `.hideTitleBar(true)`。
- `components/<feature>/…` —— 页面私有组件；只在你 ownership 白名单内的 feature 目录自由创建。
- `dialogs/<Name>Dialog.ets` —— 共享弹窗；owner 在任务书列明，不属于你的禁止编辑。
- `common/`、`api/`、`model/`、`store/`、`db/` —— 共享 infra，对域代理**一律只读**。缺功能：先在自己 feature 目录写局部 helper 顶上，并在 StructuredOutput 申报（`skipped` 附 `required_owner`，或 `deferred_items` 走 forward-ref）；禁止越界修改共享层。

## 2. Routing

Navigation + NavPathStack（API 12+；`@ohos.router` 已废弃，禁用）。宿主入口页 = `main_pages.json` 首项，由 `host_page.py` 脚本单写并 `@Provider('navPathStack')`，**任何代理不得改宿主页、不得自建第二个 NavPathStack**（会遮蔽宿主栈，导航静默失效）。

- 页面取栈：`@Consumer('navPathStack') navPathStack: NavPathStack = new NavPathStack();`（V2，必须给默认值；缺宿主 Provider 由 sync_pagemap 对账门判 FAIL）。
- 跳转 ≙ startActivity / show(DialogFragment) / navigate：`this.navPathStack.pushPathByName('<路由名>', <参数类实例>)`，路由名 = 下表「页面」列（= 页面导出的 `<Name>PageBuilder` 去掉 `Builder`）。**只此一种写法**（E77）：禁止把契约导航边改写成 `@Event`/回调"交给父组件"。
- 返回 ≙ finish()：`this.navPathStack.pop()`；替换 ≙ start+finish：`this.navPathStack.replacePathByName('<路由名>', <参数>)`；回栈中某页 ≙ singleTask：`this.navPathStack.popToName('<路由名>')`。
- 带结果返回 ≙ startActivityForResult：`this.navPathStack.pushPathByName('<路由名>', <参数>, (info: PopInfo) => { … })`，目标页 `this.navPathStack.pop(<结果>)`。
- 取参：NavDestination `.onReady((ctx: NavDestinationContext) => { const p = ctx.pathInfo.param as YourParamClass; })`。参数类：在你的页面文件内定义并 `export`（路由表生成器 PageMapGen 需要 import 它）。
- 系统返回键：NavDestination `.onBackPressed(() => boolean)`，返回 `true` 表示消费。

路由表（真值单源来自 blueprint；擅自新增路由 = 越界，走 `decision_gaps` 上报）：

{{ROUTES_TABLE}}

## 3. Resources（已转换打包——只用现成资源，禁止新建）

- 颜色：`$r('app.color.<android_color_name>')` —— Android colors.xml 全部名称逐字存在。
- 字符串：{{STRING_STRATEGY}}
- 图片：`$r('app.media.<android_file_stem>')` —— Android 全部 mipmap/webp/png 以同名小写词干存在，如 `$r('app.media.icon_home_top_vip')`。
- rawfile 资产：
{{RAWFILE_ASSETS}}
- 尺寸换算：Android dp → vp 1:1，sp → fp 1:1（设计宽 {{DESIGN_WIDTH}}）。shape drawable → `.backgroundColor` + `.borderRadius` + `.border` + `linearGradient`，按 spec 数值精确落。

## 4. Immersive layout（沉浸式）

```
import { AppContext } from '../common/AppContext';
```

窗口为 layout-fullscreen。页首内边距：`AppContext.statusBarHeight`（vp）；底部安全区：`AppContext.navBarHeight`。
域标记 `needs_immersive_safearea=true` 的页面另遵随 prompt 注入的 safearea 片段，且 StructuredOutput 必填 `safearea_layers`（4 层 file:line，脚本反查校验）。

## 5. 共享 infra 速查

{{INFRA_QUICKREF}}

- 本节是生成期快照；你任务 prompt 内的契约段 cheat sheet 经 contract-sync 回写更新，两者不一致时**以 prompt 契约段为准**。
- 用前先读对应源文件确认签名——`api/`、`store/` 下的源码是最终真值。

### 环境事实单源（V4，OPT-PLAN-V3 P5）

渠道号 / 调试开关 / base_url / 设备身份策略是**运行期后端契约**，不是普通常量——分散硬编码
会在真机期集体发作（v3 实证：channel 三处两种取值、isDebug 未接线、androidId 恒空，登录链
108 分钟）。全部收敛到单源文件（seed 层，主循环按 `spec/ref/backend-facts.md` +
`spec/baseline/dev_info.json` 落盘；worker 只 import，禁自写字面量）：

```
import { EnvFacts } from '../common/env/EnvFacts';
// EnvFacts.CHANNEL / EnvFacts.IS_DEBUG / EnvFacts.BASE_URL / EnvFacts.deviceId()
```

业务代码出现字面量渠道号 / base_url = 审计 P1（round-0 grep 面）；真机期改环境事实只改此一处。

## 6. ArkTS 严格模式（单源，不双写）

严格模式规则的唯一正文是 arkts-strict 片段：`{{ARKTS_STRICT_REF}}`。
该片段由任务书生成器按波 fragments_default 与触发词注入（⑤ 规则片段段）；**若你的 prompt 规则段没有该片段，实现前必须自行 Read 上述路径**——本契约**不复制正文**，避免双写漂移（dynamic1 的 COMMON 与 CONTRACT 双写为已识别反模式；「已注入」不做无条件承诺——AIPPT-0818 实证假声明反向劝退了 worker 自读）。
一句话底线：严格模式违规 = 构建失败 = 返工——收尾前按片段逐条自查。

## 7. Quality bar（质量线）

- 视觉 1:1：颜色、圆角、字号、间距、文案、图片与 Android 布局 spec 完全一致。
- 行为 1:1：同导航、同 API 调用（一律走共享 `api/` 层）、同存储键、同 toast 文案、同边界分支。
- 中文字符串与 Android **逐字节一致**。
- 构建保持绿：你的文件必须过 ArkTS 严格模式编译（见 §6），完成前在脑内过一遍 lint。
- 输出纪律：最终消息只回 StructuredOutput 结构化摘要（files / exports / stubs / deferred_items / decision_gaps / skipped…）；重内容一律落盘文件，不进消息正文。
