# 修复指南 — 四维度路由问题(改 HMOS / ArkTS 源码)

> 铁律一:**改之前先读 HMOS 源码确认问题是真的**。很多 `missing_jump` 是抽取盲点(跳转其实存在)、
> 死代码、或 spec 计划的合并。错改比不改更糟。
> 铁律二:**弹窗与页面同等修**。弹窗是一等路由目的地，不许按类划成"功能层遗留"。
> 铁律三:**弹窗内容以 `dialog_specs.json` 为准**(先跑 `android_dialog_probe.py`)。构造参数、
> 回调签名、单选/勾选/输入控件、文案，全部用抽取事实，不靠模型对原 App 的记忆。

## 0. 修复前信息采集(每仓一次)

| 要修什么 | 先查什么 | 怎么查 |
|---|---|---|
| 任何弹窗(A2/C) | 弹窗规格 | `python3 android_dialog_probe.py` → `dialog_specs.json`(ctor_params→props、callbacks→onConfirm 签名、controls→内容控件、route_relevant→优先级) |
| 任何页面(A1) | 该仓注册方式 | 看 `main_pages.json` 内容多寡 + 全仓搜 `.navDestination(`：router 仓注册在 main_pages，Navigation 仓注册在宿主页 pageMap `name === 'X'` 分支(或 route_map.json) |
| 绑定(C) | 该页既有导航写法 | `actual_nav.json` 的 `by_via` 哪种多 + 该页源码现成 push 例子，**沿用同页风格不混用** |
| 回调接什么后端 | 现成 ViewModel/Config API | grep `viewmodels/`、`preferences/` 的方法签名(排序/筛选/删除/复制移动等多半已有) |
| 弹窗触发点形态 | Android 触发语境 | `nav_edges.json` 该边的 `context`/`trigger_*`：菜单(R.id.x)→HMOS 菜单数组项；CAB(多选)→CAB 菜单；按钮→组件 onClick |

## 1. 导航 API(页面跳转，按本仓实际用法选)

```ets
// A) 经典 router(目标是 'pages/X' 路径，注册在 main_pages.json)
import { router } from '@kit.ArkUI';
router.pushUrl({ url: 'pages/MemberCenterPage', params: { from: 'mine' } })
router.back()

// B) Navigation(NavPathStack；目标是路由名，注册在 pageMap/route_map.json)
this.navPathStack.pushPathByName('MediaPage', navParams)
this.navPathStack.pushPath({ name: 'SettingsPage' })
this.navPathStack.pop()
```

判断:看 `actual_nav.json` 的 `by_via` 哪个多、目标页注册在哪。**沿用该页周围已有写法**。
Navigation 仓的子页拿栈用 `@Consume('navPathStack')`(与宿主 `@Provide` 配对，照抄已有子页)。

## 2. 弹窗 API(@CustomDialog 标准形状 —— 必须能被 hmos_extract 识别)

```ets
// dialogs/ChangeSortingDialog.ets —— 组件名 = Android 弹窗类名(canon 自动对账，不用进 ALIAS)
@CustomDialog
export struct ChangeSortingDialog {
  controller?: CustomDialogController
  isDirectorySorting: boolean = true            // ← dialog_specs.ctor_params 照搬
  onConfirm: (sorting: number) => void = () => {}   // ← dialog_specs.callbacks 照搬签名
  @State selectedFlag: number = 8
  build() { /* 控件照 dialog_specs.controls：RadioGroup→Radio 列、Checkbox、TextInput… */ }
}

// 宿主页 —— ★声明初始化形状是硬约束：
//   `名字: CustomDialogController = new CustomDialogController({ builder: 类名(…) })`
//   不要写 `| null` / 不要在方法里 new —— RE_DIALOG_CTRL 只认声明处，认不出=复检假阴
sortDialogCtrl: CustomDialogController = new CustomDialogController({
  builder: ChangeSortingDialog({
    isDirectorySorting: true,
    onConfirm: (sorting: number): void => { this.persistSorting(sorting) }
  }),
  autoCancel: true
})
// 触发点：
.onClick(() => { this.sortDialogCtrl.open() })     // RE_DIALOG_OPEN 认 xxx.open()
```

**形态选择表**(A2 建弹窗前先定形态——看 Android 原类的基类/库形态,probe 的 `file` 字段回读确认):

| Android 原形态 | 判别特征 | HMOS 等价形态(修复用) | 抽取器识别要点 |
|---|---|---|---|
| 居中弹窗 | 普通类自建 AlertDialog / DialogFragment / XPopup `CenterPopupView` | `@CustomDialog` + controller(§2 标准形状) | controller 声明初始化 + `.open()` |
| 底部面板 | `BottomSheetDialog(Fragment)` / XPopup `BottomPopupView` / `*Sheet` | `.bindSheet($$show, this.XxxBuilder(), …)` 或 `@CustomDialog`+`alignment: Bottom` | bindSheet 实参里写 `this.XxxBuilder()`(组件名可解析);builder 命名 = Android 类名 |
| 锚定气泡/菜单 | `PopupMenu`/`ListPopupWindow`/XPopup `AttachPopupView`/`PopupWindow` 带 anchor | 菜单语义 → `.bindMenu([...])`;自定义内容 → `.bindPopup(show, {builder: this.XxxBuilder()})` | bindMenu action 是点击触发源;bindPopup 记页面级边 |
| 全屏覆盖 | XPopup `FullScreenPopupView` / 全屏 DialogFragment | `.bindContentCover(show, XxxView())` 或 NavDestination(DIALOG 模式) | bindContentCover 记页面级边 |
| 程序化任意点弹 | 工具类/任意上下文 show | `promptAction.openCustomDialog`/`UIContext.openCustomDialog` | 实参里组件/`wrapBuilder(X)` 可解析;在 onClick 链里=控件级边 |

> 框架级 `PopupMenu`/`ListPopupWindow`(Android 端 inline 记数不对账)的 HMOS 等价是 bindMenu——
> 属**触发形态**不是独立路由目的地,缺了按维度 B(加菜单项)修,不按 A2 建组件。

数据流约定:
- **动态内容走 @Link**(删除确认的 message、选择器的列表)：弹窗里 `@Link message: string`，
  宿主 `@State` + builder 传 `$message`，open 前先赋值。普通 prop 在 controller 构造时只捕获
  一次，开第二次就是陈旧值——这是最常见的坑。
- **回调接真实后端**：specs 的 callback 签名定形状，体内优先接现成 ViewModel/Config
  (排序→config.setXxxSorting、删除→FileOperationsViewModel.deleteFiles…)。没有现成后端时
  回调体留 `// TODO: <缺的后端>`——**路由链必须真实可达，业务深度可以分期**，但不许造假实现。
- **弹窗→弹窗链**(specs 里子弹窗调用可见，如 PickMedium 的"其他文件夹"→PickDirectory)：
  在子弹窗组件内部声明嵌套 controller，@Link 数据由宿主一路传下。

## 3. 维度 A1 — 目标页面不存在

**检出**: `page_mapping.divergence` 含"孤儿/无此 struct"；`reachability_robust` 分层
`pagelevel_missing`/`struct_only_no_push`；**`pushed_but_unregistered`(最高优,运行时必崩)**。

**调查**(决定改不改):
1. 全仓搜该页是否被任何机制到达(`pushPath*`/`router.push`/tab/loadContent)。**有 → 抽取盲点,不改,扩抽取器。**
2. Android 侧入口是不是外部 intent/系统回调(manifest-only,App 内无导航)。**是 → 随"外部打开"特性
   定性遗留(需 UIAbility/Want),不是接线问题。**
3. `ui-manifest.md` 是否写了"合并到 X"(含 EntryAbility 承担 Splash 这类)。**是 → 核对承接逻辑在,记等价。**

**修法(确属真缺页)**:
1. 建 `entry/src/main/ets/pages/XxxPage.ets`,照同类已有页骨架(NavDestination/标题栏/返回/@Consume 栈)。
2. 注册(按 0 节侦察结果): main_pages.json `src` 加项 / 宿主 pageMap 加 `name === 'XxxPage'` 分支+import /
   route_map.json 加 routerMap 项。
3. 来源页补绑定(维度 C)。
4. 闭环断言: robust 转 wired、`pushed_but_unregistered` 仍空。

## 4. 维度 A2 — 目标弹窗不存在

**检出**: `diff_routes_report.json` 的 `dest_missing_inline_overlay`(目的地) +
`edge_missing_inline_overlay`(源→弹窗边) —— 这两个清单就是弹窗修复工作列表。

**调查**:
1. HMOS 是否已用**别的形态**实现同功能:全仓搜 bindSheet/bindContentCover/promptAction/AlertDialog/
   ActionSheet + 对应文案。**有 → 内嵌等价实现,记 matched-by-equivalence,不重复建。**
2. 弹窗是不是平台特定(Android R+ 权限提示/PESDK 三方页)。**是 → LLM 裁决阶段就该剔,漏网的在此定性,不建。**
3. 目标是 commons 库的"页面"而非弹窗(About/Customization)→ 归维度 A1 判断。

**修法(确属真缺弹窗)** —— 五步,全部以 `dialog_specs.json` 为依据:
1. **读 specs**: `dialogs[Name]` 的 ctor_params/callbacks/controls;控件数可疑地少(RadioGroup 空组)
   → 回读 `file` 指向的 Kotlin 类体,把动态 add 的选项抄全。
2. **建组件** `entry/src/main/ets/dialogs/Name.ets`(@CustomDialog,§2 形状):
   props=ctor_params 去 activity/binding 类参数;onConfirm=callbacks 签名;build()=controls 翻译
   (RadioGroup→Radio 列,CheckBox→Checkbox,EditText→TextInput,SeekBar→Slider;文案有 $r 资源用资源,
   specs 里解析不到的 commons key 用原文案字面量);底部 cancel/ok 按钮。
3. **宿主接线**: 触发页声明 controller(§2 硬形状) + 触发点 `.open()`(触发点不存在则先按维度 B 建)。
4. **回调接后端**(§2 数据流约定);flag 位值若 HMOS Config 注释已定义(如 `8|1024`),沿用仓内值,
   不引入 Android commons 的不同取值。
5. **闭环断言**: 重跑 `hmos_extract.py` 后 `actual_nav` 出现该 `dialog.open` 边;`diff_routes` 里
   该目的地移入 `dest_matched`。

## 5. 维度 B — 触发控件不存在

**检出**: `missing_jump` 的 Android 触发(text/trigger_value)在 HMOS 对应页 `controls[]` 无匹配。

**调查**:
1. 按**目标**匹配兜底:Android 图标按钮在 HMOS 可能是带文字的菜单项,目标对上就不缺。
2. 控件可能在子组件/菜单数组/CAB 菜单里(不在 build() 直接层)。
3. Android 触发形态决定 HMOS 形态: menu R.id.x → 菜单数组加项;多选 CAB → CAB 菜单加项;
   普通按钮 → build() 加组件。

**修法**: 照该页已有同类项的写法加(菜单项加 `{id, title}` + switch case;CAB 加 MenuElement;
组件按钮贴近 Android 原位置加),文案用既有 string 资源,缺的补进 string.json(连带 dark 等限定目录)。

## 6. 维度 C — 触发存在但未绑定(最常见)

**检出**: `actual_nav` 该控件 `bound=false`;或 onClick/menu case 体是 `console.info('TODO…')` 空壳;
或间接链断(onClick→this.go()→体内没真跳)。

**修法**:
1. 目标是页面 → 补 push(§1,参数形状照目标页 onReady 读的 key 抄,别发明新 key)。
2. 目标是弹窗 → 补 `this.xxxCtrl.open()`(controller 不存在则先走 A2 的宿主接线步)。
3. 间接链断 → 在断的那个方法体里补,不要在 onClick 里绕过原方法。
4. 守卫式(条件跳转)→ 保留条件,补对应分支跳转,guard 信息在 `nav_edges.json` 的 `guard` 字段。

## 7. 复检验证(每修一条都要能闭环)

修完重跑全链(SKILL Phase 5 命令)。逐维度断言:
- A1: robust 转 wired;`pushed_but_unregistered` 保持空
- A2: `actual_nav` 出现 `dialog.open` 边;目的地进 `dest_matched`
- B/C: 控件出现且 `bound=true`;对应 `missing_jump` 移入 `jumps`
- 全局: 有构建环境时编译一次(`DEVECO_SDK_HOME=… hvigorw assembleHap`),防"对账闭环但语法不过";
  ArkTS 注意 noImplicitAny(lambda 参数显式标类型)、`Object` 与字面量不能直接 `===`(先 as 收窄)

未闭环 = 改错了(文件/目标名/注册/controller 形状不合规),回头查。源页归因 mismatch(Android
adapter/extension 宿主 vs HMOS 页面宿主)目标可达即记"重构等价",不算未闭环。
复检结论回写 `fix_plan.json`(fixed → verified / reopened)，报告从清单生成(SKILL Phase 5)。

## 8. 修复分派与 agent 工作协议(fix_plan.json 驱动)

**主会话职责**(分派前):
1. `build_fix_plan.py` 产清单 → 逐条 triage(approved/wontfix + verdict_basis)——**只有 approved
   项进入分派**;
2. 整包: 一个文件只属于一个包;含 pageMap/`main_pages.json` 的注册热点包**串行**(或排最前);
   跨包共享的新弹窗组件归首用包,其余包 `depends_on` 它(被依赖包先跑完再发依赖包);
3. 按包并行发 通用子代理。

**每个修复 agent 的 prompt 模板**(主会话按包实例化,自包含——agent 没有本会话上下文):

```
你修复 HarmonyOS 工程 <HMOS仓绝对路径> 的一组路由问题(work package: <包名>)。
依据三份文件(都在 <仓>/spec/verify/route/ 下):
1. fix_plan.json 中 id ∈ [<本包 item id 列表>] 的条目——每条含维度/证据/fix_hint/files_expected
2. dialog_specs.json——A2/C-dlg 条目的弹窗构造参数/回调签名/控件清单,内容以此为准不要自创
3. <仓>/.agents/skills/arkts-router-verify/references/fix-guide.md §1-§7——代码模板与硬约束
   (特别是 §2 的 controller 声明初始化形状、@Link 动态数据、组件名=Android 类名)

边界与纪律:
- 只改本包 files_expected 内的文件(新建文件按 files_expected 路径);改别的文件=越界,停下来在
  notes 里说明而不是动手
- 回调能接 <仓>/entry/src/main/ets/{viewmodels,preferences}/ 的现成 API 就接真的;没有就留
  // TODO 注释,路由链必须真实可达
- 缺字符串/颜色资源 → 补进 resources/base/element/(连带 dark 限定目录同名资源)
- 每条修完,把 fix_plan.json 里该条目 status 改为 "fixed",填 files_changed(相对路径数组)和
  notes(一句话实际修法);修不了的保持 approved 并在 notes 写明阻塞原因
完成后返回:本包逐条 id → fixed/blocked 简表 + 你对 fix_plan.json 的回写已落盘的确认。
```

**并发回写约定**: fix_plan.json 是共享文件——并行包各自只改自己条目的 status/files_changed/notes
字段,不碰别人的条目、不动 items 顺序、不重排 JSON;主会话在所有包返回后通读一遍清单做一致性
检查(有冲突以 git diff 仲裁),再进 Phase 5 复检回写 verified/reopened。

**复检轮**: reopened 项重新分派(可并入新一轮 `build_fix_plan.py --round N` 的清单);两轮仍
reopened 的升级人工,不无限循环。
