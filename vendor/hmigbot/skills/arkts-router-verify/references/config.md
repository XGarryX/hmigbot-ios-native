# 换仓配置 — repo-specific 适配点

本 skill 引擎通用,**差异在数据**。换到新的 Android→HarmonyOS 迁移仓时,改以下几处。

## 1. 路径(自推导 + 一个必传参数)

**安放约定:本 skill 固定放在 `<HMOS工程根>/.agents/skills/arkts-router-verify/`。**
产物落点锚定**整个工程目录**(= 含 `.agents/` 的那一级,**不是 skill 目录**):`nav_common.py`
从脚本 `__file__` 位置向上找第一个含 `.agents/` 的祖先作为工程根。基于 `__file__` 而非
`Path.cwd()`,所以 `cd scripts` 后再运行也不会把产物落进 skill 目录。要改落点用环境变量/CLI
覆盖,**不在代码里写死绝对路径**:

| 路径 | 推导值(默认) | 覆盖方式(高→低) |
|---|---|---|
| `hmos_root`(工程根) | `__file__` 向上含 `.agents/` 的祖先;找不到退到 `Path.cwd()` | env `ROUTE_VERIFY_ROOT` / `hmos_extract.py --hmos-root` |
| `out_dir`(产物目录) | `<hmos_root>/spec/verify/route` | env `ROUTE_VERIFY_OUT` / 各脚本 `--out-dir` |
| `android_root` | **无默认,必传**:`extract_nav_graph.py --android-root <Android仓根>` | — |

> 注:`reuse.py` 已自包含(确定性抽取原语就地实现,仅依赖标准库),不再加载兄弟 skill,
> 故无 `skills_dir` 参数。

Android 仓根只需传一次:`extract_nav_graph.py` 会把它写进 `expected_nav.json`,
下游 `llm_worklist.py`/`apply_llm.py` 自动从产物里读,不再各自配置。

## 2. 命名对齐表(`diff_routes.py` + `build_page_mapping.py`)

这些是**该仓特有的改名/重构**,必须按新仓的 `ui-manifest.md` 调:

- **第一方包路径前缀(`FIRST_PARTY_PKGS`)** — 必配项,**从外部传入,不必改代码**(优先级 高→低):
  1. CLI：`extract_nav_graph.py --first-party-pkgs '/com/yourapp/,/com.yourapp.'`(多模块仓列全)
  2. 环境变量：`export RV_FIRST_PARTY_PKGS='/com/yourapp/,/com.yourapp.'`(一次 export 全工作流生效)
  3. extract 会把最终值写进 `expected_nav.json`,`android_dialog_probe.py` 等下游自动回灌,无需重复传
  4. 兜底默认在 `nav_common.py::_DEFAULT_FIRST_PARTY_PKGS`(仅示例/本地调试,换仓不必动)

  留空(env/默认都没有)脚本直接报错;错配会把第一方模块当三方库过滤掉(历史教训:整仓只抽到 1 条边)。
- `diff_routes.py::ALIAS` — Android↔HMOS 不规则改名(canon 后小写 token),如
  `"newdir": "adddir"` 表示 `NewDirDialog→AddDirPage` 这类改名迁移。规则同名(XxxActivity↔XxxPage、
  XxxDialogFragment↔XxxDialog)由 canon 剥后缀自动对齐,不用列;初跑后看 diff 报告里
  dest_missing/dest_extra 的成对项,核实源码后回填。
- `diff_routes.py::RESTRUCTURED` — Android 独立页被合并成 tab/子视图/合并页、无独立 HMOS 页
  (人工确认非"漏迁"后填,canon 后小写)。
- `diff_routes.py::ENTRY` — 入口/启动/系统回调页,不计 App 内导航。默认 `{splash, index}`,
  按仓补充(通知点击/分享接收/支付回调入口等)。
- `build_page_mapping.py::FRAGMENT_MAP` — Android Fragment → HMOS 子组件 View(无此重构留空,
  fragment 由 canon 回退匹配到同名 Page)。
- `build_page_mapping.py::AUTO_TAB_PAGES` — 经冷启/生命周期/tab 到达(非 onClick router)的页,
  不按孤儿判。默认入口三件套,按仓补底部 tab 各成员页。

**怎么得到这些**:读新仓 `spec/baseline/ui-manifest.md` 的页面清单 + 合并说明 + tab 结构,照着填。
没有 ui-manifest 时,跑一遍 `build_page_mapping.py` 看 `divergence` 和 `hmos_extra_pages`,据此回填 ALIAS。

## 3. 导航 API

**HMOS 端**(`hmos_extract.py`): router(`router.pushUrl`)、Navigation(`RouterUtils.pushPathByName`/
`navStack.pushPathByName`/`pushPath({name:…})` 对象式)、CustomDialog(controller 声明 + `.open()`、
`openCustomDialog`(promptAction/UIContext,含 `wrapBuilder` 实参))、**popup/sheet 族**
(`bindSheet`/`bindContentCover`/`bindPopup`——属性式弹层由状态翻转显示,记页面级 dialog 边,
内容目标按 this.XxxBuilder > wrapBuilder(X) > 自定义组件实例化的优先级解析;`bindMenu` 的
action 回调按点击触发源)。路由名支持字面量 + **常量符号表**(`RouteConstants.X` 全仓
`static readonly`/`const` 字符串常量自动解析,无需适配);纯变量解析不出 → `nav_target_unresolved`。
若新仓用了别的封装名(不是 `RouterUtils`),改 `RE_RU_PUSH` / `RE_NAVSTACK` 的正则。

**Android 端**(`nav_common.py`): `Intent(_, X::class)` / companion / `XxxDialog.show()` /
**业务弹窗/popup 裸构造**(`XxxDialog(…)`/`XxxPopup(Window|View)?(…)`/`XxxSheet(…)`,SMT 风格,
仅第一方 dialog 类入账) / XPopup `asCustom` 与内置便捷弹窗(inline) / **框架锚定菜单**
(`PopupMenu`/`ListPopupWindow` → inline 只记数,HMOS 等价物是 bindMenu/bindPopup) /
**Jetpack Navigation**(`res/navigation/*.xml` 的 action→destination 自动解析,
`navigate(R.id.action_x)` 直连,`navigate(变量)` 标 dynamic 交 LLM)/ `startActivity(ForResult)`。
两端扫描均**先剥注释**(保行号),注释里的示例代码不会被当成路由点。

**注册识别**(`hmos_reachability.py`): `main_pages.json` + 含 `.navDestination(` 文件里的
`name === 'X'` 分支(pageMap 路由表)。若新仓用 route_map.json 或 Map 结构注册,扩
`RE_PAGEMAP_BRANCH`。

**返回/关闭键审计**(`hmos_extract.py`,按仓微调): 返回意图按 media 资源名认——
`RE_BACK_INTENT_MEDIA`(名含 back|close 的 token) + `BACK_MEDIA_EXCLUDE`(剔除同词干非返回
语义:eye/tag/feedback/backup/background/playback)。新仓图标命名不同时改这两个正则;返回
效果识别 `RE_BACK_EFFECT` 用 `pop\w*` 兜住 popSafely 等封装变体,新仓另有封装名时补。
页面级 `no_back_affordance` 审计在 `hmos_reachability.py`(hideTitleBar(true) 且全文件无
返回效果/图标的被推注册页)。

## 4. tab 容器

- HMOS: `hmos_extract.py::extract_tab_groups` 认 `Tabs{ TabContent{…} }`,TabContent 首子是
  Stack/Column 等内建容器时向内找第一个自定义组件(`BUILTIN_COMPONENTS` 过滤)。
- Android: `extract_nav_graph.py::extract_android_tab_groups` 认含 `ViewPager` 的 Activity 里的
  `listOf(XxxFragment.newInstance()…)`。若新仓 tab 用别的容器(BottomNavigation、fragment-swap 等),
  扩这两处——抽不到 tab 组只影响"tab 兄弟互达"的救援判定,不影响主对账。

## 5. 内置通用过滤(跨仓生效,无需配置)

- **companion 自环过滤**(`apply_llm.py`):`resolution=companion_receiver` 且 `target==source`
  的边自动剔除(`this@Class` 类内自引用是定义点不是路由点);`direct` 自环保留(真实自跳)。
- **死 Builder 检测**(`hmos_extract.py::dead_builders`):零引用的非 export `@Builder` 体内
  的边打 `dead_builder` 标记,三份报告自动排除;`FIRST_PARTY_PKGS` 错配硬门禁(命中 0 个
  .kt 直接报错,防换仓残留配置静默跑偏;1–4 个 .kt 的极小工程放行,Windows 反斜杠路径自动归一化)。

## 6. 薄壳占位探针(`thin_shell_probe.py`)

脚本顶部三个阈值 + 控件对账表是换仓适配点:

- `OVERLAP_T = 0.40`:字符串键迁移率下限。**前提是该仓迁移时沿用安卓 string key**
  (`@string/x` → `$r('app.string.x')` 同名);若目标仓全部自创文案 key,overlap 恒低,
  应调低权重、主要靠 ratio/gaps 判(探针的 AND 结构已天然兜底——overlap 低但交互数
  平衡的页不会误判,如本仓 HandWritingHubStickyPage 0.00/26↔26 判 ok)。
- `RATIO_T = 0.50` / `MIN_CTRLS = 6`:交互控件数比与安卓侧最小控件数(太小的页没有"薄"的空间)。
- `WIDGET_MAP`:安卓控件类 → ArkUI 对应 token。目标仓有自封装组件体系时按惯用法补
  (如自研 `XxxSlider` 计入 SeekBar 的对应物)。
- 已内置的坑:HMOS 同名文件取真声明 `struct X` 的(排除 re-export 转发壳)、跟随
  `export{X}from`、ViewBinding 泛型反推布局、`<include>` 递归。
- 局限(判读时记得):import 只扫一层,深组件树会低估 HMOS 侧 → 探针是**出工单的探测器,
  不是自动裁决器**,thin 项仍需 triage 读码确认。

## 依赖

- Python 3.8+(标准库即可)
- **无跨 skill 依赖**:确定性抽取原语已全部就地实现于 `scripts/reuse.py`
  (历史上从 `toolkit-fact-indexer`、`app-relationship-tree` 动态加载,现已内联,可独立分发)
