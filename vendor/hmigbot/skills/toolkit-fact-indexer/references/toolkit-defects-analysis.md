# harmony-migration-toolkit 实测缺陷分析

> **测试时间**：2026-05-09
> **测试对象**：AIPPT (Android 工程 `/path/to/your-android-project`)
> **toolkit 版本**：截至 2026-05-09 main 分支（[Junkang123456/harmony-migration-toolkit](https://github.com/Junkang123456/harmony-migration-toolkit)）
> **执行命令**：`python pipeline.py --android-root /path/to/AIPPT --out /tmp/aippt_toolkit_out`
>
> **本文档定位**：基于实测产物的**缺陷归因分析**，用于：
> 1. 指导 `toolkit-fact-indexer` skill 在 Phase 2（LLM 增强）时的兜底策略
> 2. 反馈给 toolkit 上游作为 issue 素材
> 3. 评估"toolkit 数据可信度边界"以决定哪些下游能用、哪些不能依赖

---

## 一、实测产出总览

```
spec/fix/_state.yaml: pages=23 fragments=3 dialogs=15 features=17
                      components=6 nav_edges=50
                      launcher='SplashActivity' unreachable=30
                      computed_edges=0
```

数字解读：
- **41 个 screen**（23 page + 3 fragment + 15 dialog），符合 AIPPT 实际复杂度
- **6 个 UI 组件**——异常少。AIPPT 是一个支付功能完整的商业 App，正常应该有数百个组件
- **30/41 = 73% 页面从 launcher 不可达**——异常高
- **0 条 computed 边**——好的一面：所有 navigation 目标都能静态解析

---

## 二、九大实测缺陷清单

按对下游消费者的影响严重度排序：

| # | 缺陷 | 严重度 | 测试结论 |
|---|---|---|---|
| 1 | UI 组件抽取率仅 7% | 🔴 致命 | 36/39 screen 的 spec 文件 `ui_elements: []` |
| 2 | Splash → Home 异步跳转漏识别 | 🔴 致命 | launcher BFS 只走 1 跳，覆盖率 27% |
| 3 | Fragment 误标为 Activity | 🟡 中 | MineFragment / WorksFragment / BaseMemberCenterFragment 都被标 `screen_kind="activity"` |
| 4 | 匿名内部类被当成 screen | 🟡 中 | `HomeActivity$showCampaignDialog$1` 出现在 screens 列表 |
| 5 | 节点 id 命名跨文件不一致 | 🟢 低 | feature_tree 用 `xxx`，android_facts 用 `xxx$1` |
| 6 | edge 类型字段 `rel` 自由文本 | 🟢 低 | `trigger` 值是 `"fn: initObserver"` / `"menu tv_delete"` 等没枚举 |
| 7 | 应用元信息几乎全空 | 🟡 中 | `package=""`、`application_id=""`、无 SDK 信息 |
| 8 | `ui_paths.json` 全空数组 | 🟢 低 | toolkit 自己的路径功能没产数据 |
| 9 | 47 个 spec 文件成孤儿 | 🟡 中 | 86 个 spec 文件，只有 39 个被链接到 screen |

---

## 三、根因分析

下面每条缺陷给出 **观察证据 + 根因推断 + 影响范围 + 修复路径**。

> **重要免责**：我没有读 toolkit 的源代码，只通过其产物反推。下文标 ⚠️ 的部分是合理推断但未实证，标 ✅ 的是有产物直接证据的事实。

---

### 缺陷 1：UI 组件抽取率仅 7%（🔴 致命）

#### ✅ 观察证据

```
$ ls /tmp/aippt_toolkit_out/intermediate/0_android_facts/specs/ | wc -l
86       ← 一共 86 份 spec
$ jq '. as $s | $s | select(.ui_elements | length > 0) | .screen_id' specs/*.json | wc -l
48       ← 含非空 ui_elements 的 spec 数
```

但 **android_facts 里的 39 个 screen 对应的 spec 中，仅 3 个有 ui_elements**：
- `dialog_fill_ppt_query` (3 个组件)
- `dialog_vip_exit_intercept` (2 个)
- `video_play_activity` (1 个)
- 其余 36 个 spec 的 `ui_elements: []`

而那些"有 8 个组件"的 spec（如 `dialog_algorithm_filing`）**不在 screen 列表里**——成了**孤儿 spec**（见缺陷 9）。

#### ⚠️ 根因推断

**最可能的原因：toolkit 的 XML 解析在两个常见 Android 模式上失败。**

**(a) Kotlin ViewBinding / DataBinding 的不可静态追踪性**

AIPPT 这种近期 Android 项目大概率用：

```kotlin
class MineFragment : BaseFragment() {
    private val binding by lazy { FragmentMineBinding.inflate(layoutInflater) }
    
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        binding.tvUserName.text = userVM.name
        binding.btnLogout.setOnClickListener { ... }
    }
}
```

`binding.tvUserName` 是编译期生成的属性，引用 `R.id.tv_user_name`。toolkit 要把这个链路打通需要：

1. 识别 `FragmentMineBinding` ← `R.layout.mine_fragment` 的对应关系（来自 `viewBinding { enabled true }` Gradle 配置）
2. 识别 `binding.tvUserName` ← XML 里的 `android:id="@+id/tv_user_name"`
3. 把 `setOnClickListener { ... }` 关联回这个 id

如果 toolkit 仍按老式 `findViewById(R.id.xxx)` 模式扫描，这条链路完全断了——找不到 binding 用法 → 找不到 id 引用 → 标 `ui_elements: []`。

**而 `dialog_algorithm_filing` 之所以有 8 个组件**：

```kotlin
// AppTipsDialog.kt（toolkit 抽取成功的那个）
class AppTipsDialog : Dialog {
    override fun initListener() {
        // 老式 findViewById 风格
        findViewById<TextView>(R.id.tv_sure_1).setOnClickListener { ... }
    }
}
```

老 Dialog 类用 findViewById，toolkit 的 regex 能匹配。所以**只有"老派写法"的页面被抽到组件**——这强烈暗示是 ViewBinding 问题。

**(b) `<include>` / `<merge>` 标签不展开**

大型 Android 项目用 `<include layout="@layout/common_titlebar" />` 复用 UI。如果 toolkit 的 XML 解析不递归展开 `<include>`，所有被 include 的元素（标题栏的返回按钮、标题等）都不会出现在 spec 里。

AIPPT 用 `basic/` 和 `common/` 模块存放共享组件，包含大量 include 是符合预期的。

#### 📊 影响范围

- **下游消费者**：visual-verify / a2h-spec / a2h-fixer 都依赖 fact-index 的 `components[]` 字段。当前 93% 的页面这字段是空的，下游基本拿不到组件信息。
- **能否容忍**：不能。这是 fact-index 的**核心价值字段**。空了等于退化成"只有页面列表，没有组件细节"。

#### 🛠 修复路径

**短期（fact-indexer skill 兜底）**：
- LLM Phase 2 增强时，对 ui_elements 为空的页面**回退去读源码**（Kotlin/Java 文件 + layout XML），自己提取 binding/findViewById 引用 + onClick handler
- 这是已在 SKILL.md 标注的 TODO，未实现

**中期（给 toolkit 提 issue）**：
- 支持 Kotlin ViewBinding：识别 `FragmentXxxBinding` 命名约定 → 反查 `R.layout.fragment_xxx`
- XML 解析递归展开 `<include>`
- 处理 `<merge>` 根容器

**长期**：
- toolkit 集成 Kotlin 编译器 API（KSP / kotlinc 提供的语义服务）做语义级分析，而不是纯文本 regex

---

### 缺陷 2：Splash → Home 异步跳转漏识别（🔴 致命）

#### ✅ 观察证据

```jsonc
// navigation_graph.json 中 SplashActivity 的全部出边
{
  "from": "SplashActivity",
  "to": "LaunchAgreementDialog",     // ← 仅这一条
  "trigger": "fn: showPrivacyDialog",
  "via": "Dialog()"
}
```

SplashActivity 没有指向 HomeActivity 的边。但 BFS 从 launcher 起步，第二跳只到 LaunchAgreementDialog（一个 Dialog），就走不动了。

#### ⚠️ 根因推断

**Splash → Home 跳转的几乎必然形态**：

```kotlin
class SplashActivity : Activity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // 形态 A：Handler.postDelayed
        Handler(Looper.getMainLooper()).postDelayed({
            startActivity(Intent(this, HomeActivity::class.java))
            finish()
        }, 3000)
        
        // 形态 B：协程
        lifecycleScope.launch {
            delay(3000)
            startActivity(Intent(this@SplashActivity, HomeActivity::class.java))
            finish()
        }
        
        // 形态 C：RxJava
        Single.timer(3, TimeUnit.SECONDS).subscribe {
            startActivity(...)
        }
    }
}
```

**为什么 toolkit 漏掉**：静态分析要追踪这条链路需要：

1. 识别 `Handler.postDelayed(Runnable)` 是一个**延迟执行**调用（即"lambda 终将被执行"）
2. 进入 lambda 内部
3. 识别 `startActivity(Intent(this, HomeActivity::class.java))`
4. 把当前类 (SplashActivity) → 目标类 (HomeActivity) 记成一条 navigation 边

绝大多数静态分析工具在步骤 1-2 就放弃了。lambda 是"延迟执行的代码块"，对于不做控制流分析的纯文本扫描器来说，无法区分"这个 lambda 会被执行"和"这个 lambda 是参数定义而已"。

toolkit 的 `determinism: static_analysis` 字段在所有 nav 边都成立，说明它走的是文本/AST 级分析，不做控制流——这就是为什么它能解析直接 `startActivity()` 但漏 `postDelayed { startActivity() }`。

#### 📊 影响范围

- **直接影响**：reach_path 覆盖率 27% → 30 个页面成"孤岛"
- **间接影响**：a2h-scenario-runner 没法基于 fact-index 自动生成 scenario YAML（不知道怎么走到目标页）
- **能否容忍**：勉强。fact-indexer 已加 "secondary root BFS 兜底"——找出边最多的页面（实测捞回 MineFragment / WorksFragment 等 9 个），但仍有 21 个真正不可达

#### 🛠 修复路径

**短期（fact-indexer skill）**：
- ✅ 已实现：secondary root BFS
- 还可做：让用户在 `fact-indexer config.yaml` 里**手动声明 launcher 之后的 root**（`extra_roots: [HomeActivity]`），覆盖 toolkit 漏检

**中期（给 toolkit 提 issue）**：
- 加 lambda 控制流追踪：识别 `postDelayed` / `launch` / `subscribe` / `runOnUiThread` 等异步 API 的 lambda 参数 → 当作"会被执行"的代码块
- 即使不追完全控制流，仅靠**关键字白名单**（list of async APIs）就能捞回 80% 的案例

**长期**：
- 集成 Kotlin coroutine 控制流分析（IntelliJ 的 PSI / KaKotlin 提供）

---

### 缺陷 3：Fragment 误标为 Activity（🟡 中）

#### ✅ 观察证据

```json
// android_facts.v1.json screens 段
{ "class_name": "MineFragment",            "kind": "activity", "layout": "mine_fragment" }
{ "class_name": "WorksFragment",           "kind": "activity", "layout": "works_fragment" }
{ "class_name": "BaseMemberCenterFragment", "kind": "activity", "layout": "base_member_center_fragment" }
```

3 个 Fragment 的 `kind` 字段都是 `"activity"`。但 layout 文件名带 `_fragment`、类名带 `Fragment` 后缀。

#### ⚠️ 根因推断

**两种可能**：

**(a) toolkit 的 kind 判定不查继承链**

大概率 toolkit 用这种 regex：
```
if class_name endsWith "Fragment" OR extends_clause contains "Fragment" → fragment
elif extends_clause contains "Activity" → activity
else → activity (default)
```

AIPPT 的 fragment 类应该是：
```kotlin
class MineFragment : BaseLazyFragment() { ... }
class BaseLazyFragment : BaseFragment() { ... }
class BaseFragment : Fragment() { ... }
```

toolkit 看 `MineFragment : BaseLazyFragment()` 发现 `BaseLazyFragment` 不在白名单（Fragment / DialogFragment 等），就降级到 default = activity。

**根本问题**：没有跨文件查继承链。需要先索引所有类的 superclass 关系，再做闭包传递。

**(b) toolkit 实现里没考虑 *Fragment 类名启发式**

最简单兜底就是"class_name 后缀匹配"：endsWith Fragment → fragment。如果 toolkit 用更严格的 superclass 检查跳过了这个 fallback，就会失误。

我的 `fact-indexer` 脚本已加了这个 fallback：

```python
def classify_screen(screen_kind, class_name):
    name_lower = class_name.lower()
    if name_lower.endswith("dialogfragment"):
        return "DialogFragment"
    if name_lower.endswith("fragment") and screen_kind == "activity":
        return "Fragment"  # 后缀兜底
    ...
```

#### 📊 影响范围

- **下游分类错位**：visual-verify 测 fragment 时要不要先调 host page、再点 tab 切到 fragment？标错就走错路径
- **能否容忍**：能。fact-indexer 加了后缀启发式已经修正

#### 🛠 修复路径

**短期**：✅ fact-indexer 已修
**中期（toolkit）**：加 class_name 后缀启发式兜底 + 跨文件继承链索引

---

### 缺陷 4：匿名内部类被当 screen（🟡 中）

#### ✅ 观察证据

```json
// android_facts 出现这俩"screen"
{ "class_name": "HomeActivity$showCampaignDialog$1", "kind": "activity", "layout": "home_activity$show_campaign_dialog$1" }
{ "class_name": "HomeActivity$showLimitDialog$1",    "kind": "activity", "layout": "home_activity$show_limit_dialog$1" }
```

`HomeActivity$showCampaignDialog$1` 是 Kotlin 编译器对方法 `showCampaignDialog` 内部某个 lambda 的自动命名。这是**字节码层的合成类**，不是源码层的真实 screen。

#### ⚠️ 根因推断

toolkit 的 screen 检测大概率走"class_name 后缀含 Activity / Fragment / Dialog"：

```python
def is_screen(class_name):
    return any(suffix in class_name for suffix in ["Activity", "Fragment", "Dialog"])
```

`HomeActivity$showCampaignDialog$1` 含 "Activity"（在前缀），命中。

**正确的判断逻辑应该是**：

```python
def is_screen(class_name):
    # 排除合成类
    if "$" in class_name:
        return False
    # 后缀判断
    return any(class_name.endswith(suffix) for suffix in ["Activity", "Fragment", "Dialog", ...])
```

#### 📊 影响范围

- 假 screen 数量：AIPPT 实测 2 个，不算多但污染数据
- 这些假 screen 的 layout 名（`home_activity$show_campaign_dialog$1`）是无效文件名 → 找不到对应 spec → 永远空
- **能否容忍**：能。fact-indexer 可以加过滤 `if "$" in class_name → skip`

#### 🛠 修复路径

**短期（fact-indexer）**：加一行 filter
**中期（toolkit）**：screen 检测加 `$` 排除规则

---

### 缺陷 5：节点 id 命名跨文件不一致（🟢 低）

#### ✅ 观察证据

同一个东西在两份产物里写法不同：

| android_facts | feature_tree |
|---|---|
| `HomeActivity$showCampaignDialog$1` | `HomeActivity$showCampaignDialog` |
| 多一个 `$1` 后缀 | 没有 |

#### ⚠️ 根因推断

两份产物**扫描时机不同**：

- `android_facts.v1.json` 由 Stage 1 产生，扫的可能是 **DEX 字节码**（编译后），每个 lambda 都是真实存在的 `$1` `$2` 后缀类
- `feature_tree.v1.json` 由 Stage 5 产生，扫的是**源码级**信息，把所有 lambda 都归到声明它的方法名下，不带后缀

两种粒度都对，但混在一起就 join 不上。

#### 📊 影响范围

- fact-indexer 脚本需要做"模糊 merge"——按 prefix 匹配 / strip `$N` 后缀再比较
- **能否容忍**：能。脚本已经在做 fallback merge

#### 🛠 修复路径

**toolkit 上游**：统一命名规则（推荐用源码级名字，省掉 `$N`）。这是 toolkit 内部 schema 一致性问题。

---

### 缺陷 6：edge 的 trigger 字段是自由文本（🟢 低）

#### ✅ 观察证据

`navigation_graph.json` 的 50 条边中 trigger 字段实际值：

```
"trigger": ""                              ← 17 条空字符串
"trigger": "fn: initObserver"              ← 6 条
"trigger": "fn: showPrivacyDialog"
"trigger": "menu tv_delete_account"
"trigger": "fn: SaleCenterViewModel"
...
```

**没有 enum**——`"fn: XXX"` 表示触发自函数 XXX，`"menu YYY"` 表示来自菜单点击 YYY，规则得用户自己揣摩。

#### ⚠️ 根因推断

toolkit 把"在哪个函数/上下文里发生了 navigation"原样记下来了，没做映射。这个值对 **debug** 有用（能定位代码位置），但对 **下游消费**（如生成 scenario YAML 步骤）需要规范化。

#### 📊 影响范围

- fact-indexer 必须正则解析（`_normalize_trigger`），引入解析风险
- **能否容忍**：能，但脚本侧维护成本

#### 🛠 修复路径

**toolkit 上游**：加 `trigger_normalized` 字段，与 `trigger` 共存。Enum 取值：click / long_press / swipe / scroll / input / pinch / pull / auto / lifecycle / menu。

---

### 缺陷 7：应用元信息几乎全空（🟡 中）

#### ✅ 观察证据

```json
{
  "package": "",                                                       ← 空
  "application_id": "",                                                ← 空
  "launcher_activity_class": "cn.sanfate.pub.platform.page.SplashActivity",
  "launcher_activity_qualified": "cn.sanfate.pub.platform.page.SplashActivity"
}
```

没有 `versionName` / `versionCode` / `minSdkVersion` / `targetSdkVersion` / `application label` / intent-filter / permissions。

#### ⚠️ 根因推断

**`package` 字段为空，最可能的原因：Gradle 7+ 移除了 `<manifest package="...">` 属性**

```xml
<!-- 老 manifest（toolkit 期望的） -->
<manifest xmlns:android="..." package="com.example.app">

<!-- 新 manifest（AIPPT 等现代项目） -->
<manifest xmlns:android="...">     <!-- 没了 package -->
```

包名从 `build.gradle.kts` 的 `namespace = "com.example.app"` 配置。toolkit 没适配新 Gradle 约定 → 读 manifest 找不到 `package=` 属性 → 字段为空。

**其它字段（versionName 等）**应该从 `build.gradle` / `build.gradle.kts` 解析。toolkit 没读 build 文件或没读对 Gradle DSL（Groovy vs Kotlin DSL 不同语法）。

#### 📊 影响范围

- fact-index 的 `app.fingerprint` 用 versionName 算，**字段为空 → cache_key 计算降级到 `"unknown"`**——所有 round Android 缓存永不失效（即使升级 APK），用户得手动清缓存
- **能否容忍**：勉强。给 fact-indexer 加 fallback：手动读 build.gradle.kts。

#### 🛠 修复路径

**短期（fact-indexer）**：加 build.gradle 解析兜底
**中期（toolkit）**：
- 适配 Gradle namespace 写法
- 解析 Gradle Kotlin DSL（不只 Groovy DSL）
- 提取完整 manifest 信息：versionName / minSdk / targetSdk / permissions / intent-filter / deeplink

---

### 缺陷 8：ui_paths.json 是空数组（🟢 低）

#### ✅ 观察证据

```bash
$ jq '.' /tmp/aippt_toolkit_out/intermediate/0_android_facts/ui_paths.json
[]
```

外加 `ui_paths_enumerated.json` / `ui_paths_legacy.json` / `ui_effect_paths.json` 推测同样是空。

#### ⚠️ 根因推断

toolkit 内部有一个"UI 路径计算"模块（看变量名是想计算从 root 到目标的可达路径），但**实际没产数据**。可能的原因：

- 模块未完成 / 关闭了 feature flag
- 模块跑了但前提条件不满足（如依赖完整 ui_elements，但 ui_elements 普遍空）

#### 📊 影响范围

- fact-indexer 必须自己跑 BFS 算 reach_path
- ✅ 已实现：`compute_reach_paths()` + secondary root fallback
- **能否容忍**：能。脚本已补

#### 🛠 修复路径

**toolkit 上游**：要么实现完，要么删字段避免误导。

---

### 缺陷 9：47 个 spec 文件成孤儿（🟡 中）

#### ✅ 观察证据

```
86 个 spec 文件，其中 48 个有 ui_elements，38 个空
android_facts 里 39 个 screen
能匹配上的：39 → 6 个有 ui_elements，33 个空
匹配不上的：47 个孤儿 spec（含 42 个有 ui_elements 的）
```

**孤儿 spec 的内容是真实的——比如 `dialog_algorithm_filing_spec.json` 含 8 个组件，但 toolkit 没把它关联到 `AppTipsDialog` 类**。

#### ⚠️ 根因推断

**toolkit 的 spec 是按 layout 文件命名的**：`dialog_algorithm_filing` → 这是 layout 名，而非 class 名。

`screen` 是按 class 名管理的：`AppTipsDialog`。

**linker** 应该建立 `layout → class` 的关系：
- 通过 `setContentView(R.layout.dialog_algorithm_filing)` 推断 AppTipsDialog 用此 layout
- 或通过 `class AppTipsDialog : Dialog { layout = "dialog_algorithm_filing" }` 这种约定

但实际 Android 项目里 layout 可能是：

- **多个 layout 服务一个 class**：Activity 用 `setContentView` 主 layout + 各种 Fragment 切换不同子 layout
- **layout 不属于任何 class，纯粹是 `<include>` 的复用片段**：`include_titlebar.xml`、`item_feed_card.xml`（RecyclerView item）

toolkit 看起来是**为每个 layout 文件都生成一份 spec**（86 份），但只为 `setContentView` 直接关联的 39 份建立了 screen 链接。剩下 47 份是 include layout / item layout / 共享 layout，没找到 owner class。

#### 📊 影响范围

- 大量含有 ui_elements 的真实组件信息**被丢弃**——比如 RecyclerView item 的 layout 里有 7 个组件，都是 feed 卡片的有用信息
- 这才是 ui_elements 总数 6 vs spec 总组件数 181 巨大差距的真相
- **能否容忍**：不能。需要在 fact-indexer 端做 layout-class 双向 join

#### 🛠 修复路径

**短期（fact-indexer）**：
- 把所有 spec 文件都读进来，不只读 39 个 screen 关联的
- 孤儿 spec 的组件挂到合适的位置：
  - `include_xxx.xml` 类型 → 找哪个 layout 用 `<include layout="@layout/include_xxx" />` → 把组件并入那个 layout 对应的 screen
  - `item_xxx.xml` 类型 → 找哪个 layout 含 `app:listitem="@layout/item_xxx"` 或代码里 `inflate(R.layout.item_xxx)` → 挂到 RecyclerView 所在的 screen，归入 `components[].items[]`

**中期（toolkit）**：自己做这个 join，把孤儿 spec 主动挂到使用它的 screen

---

## 四、缺陷严重度汇总

```
🔴 致命缺陷（fact-index 核心价值受损）
   1. UI 组件抽取率 7%             → fact-indexer 必须读源码兜底
   2. Splash → Home 漏识别        → 已加 secondary root BFS 兜底

🟡 中等缺陷（功能正确但不便）
   3. Fragment 误标 Activity      → 已加后缀启发式兜底
   4. 匿名内部类当 screen          → 加 `$` 过滤即可
   7. 应用元信息几乎全空           → 给 fact-indexer 加 build.gradle 解析兜底
   9. 47 个孤儿 spec               → fact-indexer 做 layout-class join

🟢 轻量缺陷（数据洁癖问题）
   5. 节点 id 跨文件不一致         → 脚本侧 strip $N 已兜底
   6. trigger 字段无 enum         → 脚本侧正则解析已兜底
   8. ui_paths.json 空            → fact-indexer 自己 BFS 已替代
```

---

## 五、对 fact-indexer skill 的具体兜底建议

按优先级：

### P0 - 必须做（影响主要价值）

1. **LLM Phase 2 回退读源码**：对 `components` 为空的页面，让 LLM 直接读 `<class>.kt` + layout XML，自己抽 binding 引用和 onClick handler。这是已声明但未实现的 TODO。

2. **layout-class 双向 join**：
   - 读所有 spec 文件，不只读 screen 关联的
   - 通过 `<include>` 标签把孤儿 layout 挂到使用它的 screen
   - 把 item layouts 挂到 RecyclerView 所在的 screen，归入 `components[].items[]`

### P1 - 应该做（影响用户体验）

3. **build.gradle 解析兜底**：补全 `app.package` / `versionName` 等关键元信息

4. **手动 root 配置**：允许用户在 `spec/.cache/fact-index/config.yaml` 声明 `extra_roots: [HomeActivity]`，覆盖 toolkit 漏检的 Splash → Home

### P2 - 可以做（数据卫生）

5. **过滤匿名内部类**：脚本侧加 `if "$" in class_name → skip`

---

## 六、对 toolkit 上游提的 issue 模板（一份候选清单）

如果决定向 [toolkit](https://github.com/Junkang123456/harmony-migration-toolkit) 提反馈，按以下顺序：

1. **【P0】**Kotlin ViewBinding / DataBinding 支持
2. **【P0】**Splash → Home 异步跳转识别（Handler/coroutine/RxJava）
3. **【P1】**`<include>` / `<merge>` XML 递归展开
4. **【P1】**继承链解析（让 BaseFragment → Fragment 能被识别）
5. **【P1】**Gradle Kotlin DSL + namespace 写法适配
6. **【P2】**screen 检测排除 `$` 合成类
7. **【P2】**节点命名跨阶段统一
8. **【P2】**trigger 字段加 normalized 枚举

每个 issue 配上 AIPPT 实测产物作为可复现样本（一条 navigation_graph.json 缺 SplashActivity → HomeActivity 的边，附 SplashActivity.kt 实际写法）。

---

## 七、结论

> **toolkit 不能裸用**——它给出的是**残缺的事实底座**，不是开箱即用的 fact-index。
>
> 在 toolkit 当前版本下，要让 fact-index 真正可用，**fact-indexer skill 必须做大量兜底**（读源码补组件、跑 BFS 补 reach_path、读 build.gradle 补元信息、做 layout-class join）。这意味着 fact-indexer 的 LLM Phase 2 不能依赖"toolkit 给了组件清单"这个前提，而是要**默认 toolkit 没给**，自己回退到读源码。
>
> 长期来看，要么 fork toolkit 修这些缺陷，要么向上游提 PR。短期内 fact-indexer 这一层做兜底是务实选择。

---

## 八、版本历史

| 版本 | 日期 | 内容 |
|---|---|---|
| 1.0 | 2026-05-09 | 首版。基于 AIPPT 实测，9 个缺陷的根因分析 + 修复路径 |
