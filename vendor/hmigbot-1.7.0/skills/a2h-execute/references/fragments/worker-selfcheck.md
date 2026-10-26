# worker-selfcheck — 域实现收尾自检（提交前必过）

## 子依赖完成度（逐页重读 Android 源类核对，不凭记忆）
| # | 检查 | 方法 |
|---|---|---|
| 1 | include 布局 | layout XML 搜 `<include layout=`，每个被引布局已译成子组件或内联进目标 |
| 2 | Adapter | RecyclerView/ListView 的 Adapter item layout 已迁为独立 `@ComponentV2` 子组件 |
| 3 | ViewHolder | Adapter 的复杂 ViewHolder 布局已进目标组件 |
| 4 | 弹窗 | 源类搜 `Dialog` / `.show()` / `AlertDialog` / `BottomSheet`，每个已迁或已登记占位 |
| 5 | 菜单 | 源类 inflate 的 menu XML，全部动作已译成标题栏 action / 按钮 |
| 6 | 导航目标 | 所有 `Intent` / `NavController.navigate` 目标已入迁移索引或 manifest |
| 7 | 子 Fragment | `FragmentTransaction` / `childFragmentManager` 添加的子 Fragment 已迁成子组件 |
| 8 | HitTest 死区 | 本域 `.hitTestBehavior(HitTestMode.Block)` 逐处核对：所在组件子树内无 onClick/Button/TextInput/Toggle（有 → 改 Default 或遮罩 `.onClick(()=>{})`，见 arkui-enums 四值语义表） |

发现缺项二选一，不许沉默：本批立即补齐，或按占位分类法登记 deferred 并写进结果申报。

## 申报格式（每项都要有数字，"已自检"一句话 = 无效）
```
include 检查 N 处，全处理 ✅/❌
Adapter 检查 N 个，全处理 ✅/❌
弹窗检查 N 个，全处理 ✅/❌
菜单检查 N 个，全处理 ✅/❌
子 Fragment 检查 N 个，全处理 ✅/❌
HitTestMode.Block 共 N 处，逐处子树无交互组件 ✅/❌
自检期间补齐项：N
```
结论 ✅ PASS / ⚠️ FIXED 才可进编译验证；❌ BLOCKED 必须先处置缺项。

## 布局陷阱：margin 计入自身尺寸（编译不报，真机才现形）
- ArkUI 的 margin 算在组件自身尺寸内（与 Android layout_margin 相反）：`width('100%')` + 横向 margin = 溢出父容器，编译器不拦。
- 修法：横向 margin 下沉为父容器 `padding`，或宽度写 `calc(100% - Nvp)`；纵向 margin 可保留。
- 禁把 `layout_width` / `match_parent` / `layout_margin` 逐字直译。

<!-- source: android-view-to-arkui/SKILL.md:L123,L153-186 -->
