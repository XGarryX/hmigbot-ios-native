# 布局迁移排障方法论（A2H 迁移 · 测量闭环 / 盒模型溢出 / Stack 定位）

> 何时读本手册：visual-verify 判读或 fixer 修复中出现**布局类**差异——区域空白/组件消失、内容溢出被裁、
> 元素位置错乱（尤其"都挤在中间"）。这三类不是随机渲染故障，而是 iOS 与 ArkUI 的**测量、盒模型、
> 定位语义不同**，按属性名机械映射会**稳定复现**——所以它们是 SYSTEMIC 聚类的高优候选：同类工单先归并，
> 修一类只需一套改法。本手册只讲"怎么认、怎么修、怎么验"；生成链的上游预防见 §7。

## 0. 三十秒分诊表（症状 → 缺陷类 → 第一探针）

| 截图/工单症状 | 缺陷类 | 第一探针（源码侧） |
|---|---|---|
| 整块区域空白 / 组件"消失"、dump 里高宽为 0 | **A 测量闭环**（wrap 父 + 100% 子） | 找该区域容器：父无显式尺寸且子全是 `width('100%')/height('100%')` |
| 区域反常撑满全屏/撑满祖先（iOS上只是小块） | **A 测量闭环**（百分比向上解析） | 同上——百分比找不到父约束会向上找祖先 |
| 内容右侧/底部被裁、贴边溢出、多一条滚动 | **B 满尺寸+margin 溢出** | 同一组件上 `width('100%')` 与水平 margin（或 `height('100%')` 与垂直 margin）并存 |
| 顶栏/底钮/浮层全挤在页面中间；元素位置与iOS明显不符 | **C Stack 定位失效** | Stack 子项用 `.align()` 承接iOS `layout_gravity`；或 `alignContent` 一刀切 |
| toast/弹窗/浮层从「随内容小容器」变成大卡（近全宽/明显变高变白） | **A 测量闭环**（反向变体：wrap 语义丢失被放大） | 该容器 ArkTS 侧被写成固定大尺寸或 `'100%'`+padding，iOS侧是 wrap_content |

> **相机预览 / overlay 类页面的判分铁律**：这类页面 90%+ 像素是实景，双端画面**注定不同**，
> 相似度分数（哪怕 ≥0.95）**不是有效判据**——必须逐项核 UI 元素的**位置**（顶栏在顶、底钮在底、
> toast 尺寸随内容），任何一项位置/尺寸与iOS不符即出单，禁止以整体高分放行。
> （实爆：一批相机 overlay 页顶栏/底钮全部居中叠压，判分 0.96 放行、零出单。）

> 判读注意：A 的两种表现（坍塌为 0 / 反常撑满）是**同一个闭环**在不同约束下的两个出口，归同一类单。

## 1. 语义对照表（为什么机械映射必错）

| 语义 | iOS | ArkUI | 机械映射的坑 |
|---|---|---|---|
| 父由子定尺寸 | `wrap_content` 可与 `match_parent` 子共存（测量协议两趟） | 省略尺寸=由内容定；子 `'100%'` 依赖父 → **闭环** | `wrap→省略、match→'100%'` 直译 = 闭环 |
| margin 记账 | margin 在组件尺寸**之外**（父负责留白） | margin 计入组件**占用**尺寸 | `'100%'`+margin = 100%+margin 之和，必溢出 |
| 子项在父中的位置 | `layout_gravity`（FrameLayout 等） | Stack 子项 `.layoutGravity(...)`（API 20+） | 译成 `.align()` 只改**组件内容**在自身绘制区的对齐，位置不动 |
| 组件内部内容对齐 | `gravity` | 按组件型：`textAlign` / `justifyContent` / `alignItems` | 与 `layout_gravity` 混用/互换 |
| Stack 全体默认位置 | 无对位物 | `Stack({alignContent})` | 拿它代替每个子项各自的 gravity |

## 2. 缺陷 A：wrap_content 父级测量闭环

### 2.1 判据
- 触发结构（iOS侧）：`wrap_content` 父容器内，子项 `match_parent`（常见：背景 View / 蒙层 / 描边层）。
- ArkTS 侧特征：父容器**无显式宽/高**，而其尺寸贡献子项全是 `'100%'` 或 `LayoutPolicy.matchParent`。
- dump 验证：该容器 bounds 高或宽为 0（坍塌），或远大于iOS侧对应区域（向上解析撑满）。
- **反向变体**：iOS wrap_content 的小容器（toast/小弹窗）在 ArkTS 被写成固定大尺寸/近全宽白卡——同属「尺寸来源错误」，修法同 §2.2（找回由内容定尺寸的语义，样式按iOS侧还原）。

### 2.2 修法原则
1. **先找"谁真正决定父级固有尺寸"**：文字、图片、固定尺寸子项、兄弟约束——背景/描边/蒙层**不得**反向参与父级测量。
2. 背景只需随内容等大时，**把背景/边框画在内容容器本身**（`.backgroundColor/.border`），删掉那层 `'100%'` 背景子项——这是最常见也最干净的修法。
3. 确需保留结构时，按场景用 `LayoutPolicy.wrapContent / matchParent`（API 21+ 可用即评估），**不得**无条件用"省略尺寸 + '100%'"组合。
4. 两头都没有固有尺寸来源时，从iOS约束、资源尺寸（dimen）或外层可用空间**恢复出明确尺寸**；禁止拍脑袋写常量。

## 3. 缺陷 B：满尺寸与 margin 叠加溢出

### 3.1 判据（**按轴**，别跨轴误杀）
- `width('100%')` / `width(LayoutPolicy.matchParent)` 与 left/right/start/end margin 并存 → 横向溢出；
- `height('100%')` / `height(LayoutPolicy.matchParent)` 与 top/bottom margin 并存 → 纵向溢出；
- 非同轴的间距是安全的（满宽 + 上下 margin 合法），**不要顺手删掉**。
- 嵌套多层满尺寸时每层独立检查——溢出会逐层累加。

### 3.2 修法（按优先序）
1. 该轴间距**上移为父容器 padding**（语义最贴近iOS：父留白）；
2. 或尺寸改 `calc(100% - <marginSum>vp)`；
3. 保留哪种取决于同级兄弟是否共享该留白：多子共享 → 父 padding；仅此一项 → calc。

> 示例（勿跨项目照抄数值）：考生信息卡片 `width('100%')`+`margin({left:16,right:16})` → 右侧溢出 32vp；
> 修为父容器 `.padding({left:16,right:16})` + 子项去水平 margin。

## 4. 缺陷 C：Stack 子项定位失效

### 4.1 判据
- iOS FrameLayout 子项带 `layout_gravity`（尤其混合 top/bottom/center），ArkTS 侧：
  - 子项用 `.align(...)` 承接（无效——那是内容对齐）；或
  - `Stack({alignContent: Alignment.Center})` 一刀切，子项无各自定位。
- 截图特征：本应分布在顶/底/角落的元素**全部居中堆叠**。

### 4.2 修法
1. 每个子项按源 `layout_gravity` 写 `.layoutGravity(LocalizedAlignment...)`（API 20+）；
2. `gravity`（内容对齐）按组件类型另行映射：Text→`textAlign`，容器→`justifyContent/alignItems`；两者**不可互换**；
3. 源 FrameLayout 没有统一居中语义时，Stack **不得**用 `alignContent: Center` 代替逐项定位；
4. 同一 Stack 混合顶/中/底子项 → 逐项保留，一个都不能并。

> 示例：录制页浮层——iOS style 要求结束按钮 `center_horizontal|bottom`，ArkTS 用
> `Stack({alignContent:Center})` + 子项 `.align(Bottom)` → 顶栏/按钮全在页面中间；
> 修为子项 `.layoutGravity()` 逐项定位、删 alignContent 一刀切。

## 5. fixer 速查：静态硬规则 + grep

| # | 硬规则（命中即 FAIL，进对应缺陷类） | 缺陷 |
|---|---|---|
| R1 | wrap/无定尺寸父级 + 唯一尺寸贡献子项为 `'100%'`/matchParent | A |
| R2 | `width('100%'\|matchParent)` + 水平 margin 同组件 | B |
| R3 | `height('100%'\|matchParent)` + 垂直 margin 同组件 | B |
| R4 | Stack 子项以 `.align()` 承接源 `layout_gravity` | C |
| R5 | `alignContent: Center` 但源子项存在混合 top/bottom/start/end gravity | C |

```bash
# 粗筛（命中后必须人工看 Builder 展开后的真实父子关系，单行正则命中不作结论）
rg -n "width\('100%'\)" --type-add 'ets:*.ets' -t ets -A3 <页面目录> | rg -B1 "margin.*(left|right|start|end)"
rg -n "height\('100%'\)" -t ets -A3 <页面目录> | rg -B1 "margin.*(top|bottom)"
rg -n "alignContent.*Center|\.align\(Alignment\." -t ets <页面目录>
```
- 对账方向：拿iOS侧布局 XML 的 `layout_gravity`/`layout_margin*`/尺寸三元组当真值，逐项核 ArkTS 对位——不要只看 ArkTS 自身"顺不顺眼"。

## 6. 验收清单（编译通过 ≠ 布局迁移通过）

- [ ] 修后 dump：目标容器 bounds 非 0 且与iOS侧对应区域比例一致（A）
- [ ] 修后截图：无右侧/底部裁切，无多余滚动（B）；受影响的**每一层**嵌套都复核过
- [ ] 顶/中/底元素坐标与iOS截图逐项对位（C），横竖屏各验一次
- [ ] 同类单（SYSTEMIC）全量回归：一类缺陷修一处规则后，其余同类页面逐页复核，不是只修报单那页

## 7. 上游根因（供出 systemic 单时填 suggested_fix_owner，不在本手册执行）

三类缺陷的生成源头在迁移链 `a2h-execute → a2h-ios-converter → ios-ui-graph-query/references`：
尺寸规则粗略（wrap→省略、match→'100%'）、`layout_gravity` 两处映射互相冲突、`ios-view-to-arkui`
已验证的盒模型规则未被主链加载。修单侧页面之外，同类单堆积时应出 systemic 单指向上游映射规则
（单属性映射 ≠ 属性组合约束；尺寸、margin、父容器类型不能分别翻译后拼接）。
