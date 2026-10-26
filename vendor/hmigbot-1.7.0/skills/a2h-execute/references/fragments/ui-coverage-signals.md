# ui-coverage-signals — 二三层页面来源 8 类信号（防整批漏页）

读本域 Android 源时按下表逐项核对；任何一条命中 → 必须产出对应页面条目（带正确 type：Fragment / DialogFragment / BottomSheetDialogFragment / Dialog / PopupWindow）。漏识别 = 整批漏页、下游手工救火（实证：84 页 spec 漏 100+ 二三层页）。

## 8 类信号穷举清单
| # | 信号 | 搜索位置 | 层级 |
|---|---|---|---|
| 1 | `ViewPager.adapter`/`ViewPager2.adapter` → `getItem(int)`（ViewPager2 为 `createFragment(int)`）返回的 Fragment 列表 | .kt/.java | 二层 |
| 2 | `TabLayout` + ViewPager 的 Tab Fragment 子项 | .kt/.java/XML | 二层 |
| 3 | Step/Wizard 类 Fragment（类名常含 Step1/Step2 数字后缀） | 类名/包名 | 二/三层 |
| 4 | `BottomSheetDialogFragment` / `DialogFragment` / `PreferenceDialogFragmentCompat` | .kt/.java | 三层 |
| 5 | 三方弹窗库：`XPopup.Builder.asCustom(...)`（Lxj 等） | .kt/.java | 三层 |
| 6 | `PopupWindow` / `DropDownPopupWindow` 含 layout 引用 | .kt/.java | 三层 |
| 7 | `FragmentTransaction.replace(...)`/`add(...)` 通过类引用反查 | .kt/.java | 二/三层 |
| 8 | Compose `composable("route")` 路由名 | .kt | 一/二层 |

## 页面判定三条件（同时满足才算 screen）
1. 传递继承自 Activity/Fragment/Dialog/PopupWindow；
2. 具体类——abstract 基类不算（BaseActivity/BaseFragment 自身无页面，其具体子类才是）；
3. 有自己的 layout（`setContentView` / `inflate`；ViewBinding 类名可反推：`ActivityMainBinding` → `R.layout.activity_main`）。

另查库提供的 Fragment 子类（PreferenceFragmentCompat / ListFragment / MapFragment 等），被工程使用即是页面。

## 核对纪律
- 8 条逐项过，每条给出「命中 N 处 / 无命中」结论；整体一句"已检查" = 无效。
- 命中处记四件事：类全名、type、layout 引用、宿主（谁弹出/承载它）。
- 拿不准是否页面 → 记为疑似并附证据行号，禁止静默丢弃。

<!-- source: android-ui-graph-builder/SKILL.md:L130-167 -->
