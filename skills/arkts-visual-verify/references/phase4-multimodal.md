# Step 4.2 — 多模态对比

> 从 SKILL.md §4 Step 4.2 抽出。sub-agent 多模态读图前 Read。

---

## 2.2.0-pre 禁止手动替代（HARD-GATE）

<HARD-GATE>

arkts-visual-verify 必须作为**独立 skill 调用**，由它产出结构化 JSON（`differences[]` + `siblings_order_checks[]` + `icon_semantic_checks[]`）。

**禁止的替代做法**：
- 主代理直接用 `Bash screencap + Read 图片 + 肉眼自然语言对比` 代替 skill 调用
- 用 "看了下都差不多" 当作 PASS 证据

**必须的做法**：
- 调用方（arkts-spec-evolver Step 11、a2h-verify CHECK-6 等）必须通过 Skill tool 正式调用 arkts-visual-verify
- skill 完成后必须向调用方返回 JSON 报告，调用方凭 JSON 做 status 升级判断
- 缺 JSON = 视为未跑 = 不得升级 status

本条规则的来源：2026-04-24 增量迁移中，主代理全程用手动替代，漏掉 Tab 顺序和 FAB 图标两处显著差异。结构化 JSON 是抓这类差异的底线。

</HARD-GATE>

---

## 2.2-pre 结构 oracle（确定性，多模态之前先跑，P0-B）

在合成 sbs / 喂多模态**之前**，先跑确定性结构比对，拿两端 UI dump 机械比组件存在性 + 兄弟顺序。它产两样东西：① 硬差异（缺/多/序，直接进 findings）② 给多模态的"划重点"清单（组件核对表 + 位置软提示）。

```text
# A_XML  = spec/visual-verify/screenshots/ios/{trip_id}/{page_id}.ios.xml          # Phase 2 存
# H_JSON = spec/visual-verify/screenshots/harmony/round-{N}/{trip_id}/{page_id}.hmos.json  # Step 4.1-b.2 存
# STRUCT_OUT = spec/visual-verify/screenshots/sbs/round-{N}/{trip_id}/{page_id}.struct.json
# IF A_XML 与 H_JSON 都存在（Glob/Test-Path/os.path.isfile 均可）:
python3 $SKILLS_ROOT/arkts-visual-verify/scripts/structural_diff.py \
    --ios "<A_XML>" --hmos "<H_JSON>" --page-id "{page_id}" --out "<STRUCT_OUT>"
# ELSE: 打印 "[结构 oracle] 跳过：缺 iOS-dump / HMOS-dump（写明缺哪个）→ 本页仅多模态"
```

**两条用法**（dump 缺失则整步跳过，退化为纯多模态，不阻断）：

1. **`differences[]` 直接进 findings**：`category` ∈ {missing, extra, order} 的条目是**确定性硬差异**（分辨率/宽高比无关，零漏报），与多模态 `differences[]` **合并去重**后一起走 Step 4.3 分类写盘。`source="structural_oracle"` 字段标明来源。**`dynamic_suspect: true` 的 missing/extra 先不当硬 bug**（多为时钟/日期等动态文本），转交多模态在 sbs 复核。

2. **`attention_for_multimodal` 拼进多模态 prompt**：把 `component_checklist[]` + `position_hints[]` 注入下面 2.2.1 的 prompt（见该节"结构 oracle 划重点"占位），让多模态**带着清单逐项核对**，而不是裸眼盲扫——直接治单遍穷举漏报。

---

## 2.2.0-resources iOS 资源反查（强制前置）

在跑多模态对比前，先做一轮"iOS layout XML 资源反查"，建立期望图标/drawable 映射：

```text
# 对页面关联的 iOS layout XML 提取所有 drawable 引用（去重）——跨平台 python 一行式
#（bash 等价：grep -hoE '@(drawable|mipmap)/[a-z0-9_]+' <xml> | sort -u）
python3 -c "import re,sys;print(sorted(set(re.findall(r'@(?:drawable|mipmap)/[a-z0-9_]+',open(sys.argv[1],encoding='utf-8').read()))))" {ios_dir}/app/src/main/res/layout/{related}.xml
# 逐条检查 HMOS 是否有同名（或映射过的）资源：用 Glob 工具在
#   {hmos_project}/entry/src/main/resources/base/media/ 下按名字（忽略大小写）匹配
```

产出 `ios_drawable_refs` 字段塞进对比 prompt，作为图标语义 ground truth：

```yaml
ios_drawable_refs:
  - ios_id: tv_upload_item
    drawable: "@mipmap/icon_import_doc"
    hmos_expected: "icon_import_doc"   # HMOS 同名资源或映射名
    hmos_actual:  # 由多模态对比填（读 .ets 源码 + 截图双端核验）
    match: ?
```

若 `hmos_actual != hmos_expected` → 归 `severity: high, is_migration_bug: true, category: icon`。

---

## 2.2.0 先合成双端并排图（强制）

两端独立截图给模型易漏位置偏差（实测案例：HomeView Tab 顺序 iOS=`输入主题|上传模板|导入文档` vs HMOS=`输入主题|导入文档|上传模板`，两张独立图各看各的，一致性检查漏掉）。先用 `scripts/compose_side_by_side.py` 合成一张左 iOS 右 HarmonyOS 的并排图，再交给模型：

```text
# HMOS 截图 + sbs 都按 round 永久归档；iOS 仍跨 round 共用
# （输出目录 spec/visual-verify/screenshots/sbs/round-${ROUND}/${TRIP_ID}/ 由脚本自建，无需 mkdir）
python3 $SKILLS_ROOT/arkts-visual-verify/scripts/compose_side_by_side.py \
  spec/visual-verify/screenshots/ios/${TRIP_ID}/{page_id}.png \
  spec/visual-verify/screenshots/harmony/round-${ROUND}/${TRIP_ID}/{page_id}.jpeg \
  spec/visual-verify/screenshots/sbs/round-${ROUND}/${TRIP_ID}/{page_id}.jpeg \
  "iOS | HarmonyOS"
# → 输出带顶部标签、最长边 ≤1800 的并排图
```

**硬性要求**：
1. 每一轮对比都**必须**重新合成 sbs 图（禁止只传两张独立图给模型；这是本 skill 的一个已知失效模式）
2. Read 工具只读合成后的 sbs 图；对比 prompt 里明确"下图左侧为 iOS，右侧为 HarmonyOS，标签带 iOS / HarmonyOS"
3. 合成脚本失败（无 Python PIL 等）→ 不允许降级为独立图对比；先修环境（`pip3 install Pillow`）再继续
4. sbs 图同样受 ≤1800px 限制（脚本已内置 resize）
5. 有序 Tab / 列表 / 多按钮的 acceptance → **必须对每个激活态单独截一张并合成**，一张并排图只能覆盖一个激活态

---

## 2.2.1 多模态 prompt

将合成后的并排图传给多模态模型，使用以下 prompt：

```
你是一个 iOS→HarmonyOS 迁移 UI 对比专家。请对比以下两张截图：

左图：iOS 原始应用的「{页面名称}」页面
右图：HarmonyOS 迁移后的「{页面名称}」页面

【结构 oracle 划重点】（若 2.2-pre 跑出了结构数据则注入，否则删除本段）：
下面是确定性脚本从两端 UI dump 提取的**组件核对表**——iOS 上每个组件 + 它所在的粗略区域。请**逐项**确认右图 HMOS 是否在对应区域存在该组件、且颜色/图标/字号/样式与左图一致；任何一项对不上都要写进 differences[]：
{component_checklist 渲染：- [类型] 「文本」@ 区域（present_in_hmos=真/假）}
另有**位置软提示**（结构上疑似移位，但绝对位置由你看 sbs 定夺，可能是真移位也可能两端宽高比不同）：
{position_hints 渲染：- 「文本」iOS在X区 / HMOS在Y区，请重点核对实际位置}
（注：组件存在性与兄弟顺序脚本已硬判并直接入库，你**不必**重复报这两类；你的增量价值在颜色/图标/样式/精确位置/留白这些脚本判不了的维度。）

**绝对总目标**：HMOS（右）必须与 iOS（左）**100% 视觉一致**。"100%" 不是修辞——任何**肉眼能看出的**差别都是 bug，无论大小、位置、是否在已列分析维度内。

**穷举铁律**（违反 = 本次输出作废重跑）：
- `differences[]` 必须**穷举**所有肉眼可辨的不同，不准只列"主要的几条"
- 不准因为"看起来不影响功能" / "鸿蒙平台默认这样" / "细微差别可忽略" 就省略——所有判断留给 fixer，多模态只负责**穷尽报告**
- 下列**结构层差异**特别容易漏报，必须主动扫：
  - 任何区域的**留白/spacing**多了或少了（顶部 safe-area、标题栏下方、卡片间、底部）
  - 同一位置**叠了两个同语义组件**（双 header、双返回箭头、H5 自带 nav + app 原生 nav）
  - 外层多了一个**包裹容器**（多余 padding/margin/背景色框）
  - 元素相对位置偏移（即便元素都在）

**完备性自检**（输出前强制做一次）：
output JSON 前问自己 3 遍："我把每一处肉眼能看出的差别都列了吗？再扫一遍 sbs 拼图，从上到下，左右两边逐区域比对，是否还有遗漏？" 想到 1 处遗漏 → 补进 `differences[]` 再输出。

请区分两类问题后，输出 JSON。**多模态的职责是「识别 + 穷举描述」差异，不负责给出最终修复方案——下面提到的 ArkTS 代码模式仅作为帮助多模态识别症状的参考线索（例如看到"元素消失"时联想是否是 layoutWeight 引起），是不是真的根因、怎么修，由 visual-fixer 自己读源码决定。**

【迁移 Bug】：代码实现错误。常见症状（识别线索，非修复指令）：
- 元素消失（症状线索：可能是 layoutWeight 在无固定高度父容器中撑高/收缩）
- 元素尺寸异常（症状线索：可能是 ImageFit.Contain 在无固定高度 Stack 中按原始像素展开）
- 组件宽度撑满而非收缩（症状线索：iOS wrap_content → ArkTS 中需 Row 包裹）
- 内容被裁剪消失（症状线索：clip(true) 与 borderRadius 组合问题）
- 颜色/字号明显错误
- 按钮样式不一致（圆角、描边、渐变、背景色）
- 组件位置偏移（元素间距、对齐方式）
- **组件位置错乱（无条件出单铁律）**：元素落在错误的屏幕三分区（iOS在顶部/底部、鸿蒙跑到中部）、或元素相互叠压遮挡 → **必须**列入 `differences[]`（category=layout_bug, severity=high, is_migration_bug=true），**无论 overall_similarity 多高**。`overall_similarity` 只是参考值，**从来不是"不列差异"的理由**（实爆：相机 overlay 页顶栏/底钮全部居中叠压，判 0.96 放行零出单）。微偏（几 vp 级、同一三分区内）不适用本条，仍按普通位置差异分级。
- **相机预览 / 实景 overlay 页**：背景是实景，双端画面**注定不同——背景差异不判罚、不计入相似度惩罚**；但 UI 元素（顶栏/按钮/toast/计时条）的**位置与尺寸必须逐项核对**，判据与修法见 [`layout-troubleshooting.md`](layout-troubleshooting.md)。
- 尺寸比例失调

【平台差异】：HarmonyOS 与 iOS 的设计规范差异。常见表现：
- 状态栏、导航栏样式/高度不同
- 字体渲染方式细微差异
- 系统默认图标风格不同
- dp 与 vp 之间的细微尺寸差异（±10% 以内）

输出格式：
{
  "overall_similarity": 0.85,
  "differences": [
    {
      "category": "layout" | "color" | "font" | "spacing" | "component" | "icon" | "missing" | "layout_bug",
      "severity": "high" | "medium" | "low",
      "is_migration_bug": true | false,
      "description": "具体描述，包含在哪里、有什么不同",
      "root_cause_hint": "[可选] 多模态根据症状给的根因猜测（如「疑似 layoutWeight 撑高」），仅作 fixer 参考。fixer 必须读源码核实，不得直接照抄"
      // 注意：本 skill **不输出** suggested_fix / file / property / expected_value 等字段——
      // 那是 fixer 的职责，多模态没有源码读权限，凭视觉猜出来的"改法"会误导 fixer
    }
  ],
  "missing_elements": ["..."],
  "extra_elements": ["..."],
  "scroll_needed": true | false
}

分析维度（全部 9 项都必须检查）：
1. 布局结构：元素是否全部可见，顺序是否一致，有无内容被推出屏幕
2. 组件类型：列表/卡片/按钮/输入框等是否对应
3. 颜色：背景色、文字色、主题色是否一致
4. 字体大小：标题、正文、辅助文字的相对大小关系
5. 间距：padding、margin、元素间距
6. 图标：图标样式和位置
7. 缺失/多余元素
8. scroll_needed：**仅在 `capture_mode == "single"` 时有意义**——HarmonyOS 页面在本该单屏显示的场景下却需要滚动（通常是 `layoutWeight` 误用把内容撑出屏幕）。`capture_mode == "long"` 时本字段置 `null`，长页分段逻辑已在 Step 4.1.3 处理，不再作为 bug 告警
9. **图标语义检查（强制）**：对每个可见图标（FAB / Tab icon / button icon / list item icon 等）单独输出视觉特征：主形状（`cloud` / `folder` / `arrow_up` / `arrow_down` / `file` / `check` / `plus` / …）、方向（`up/down/left/right/none`）、颜色类（`dark/light/accent/transparent`）、是否含箭头/尾标/叠加。**sbs 图 resize 后小图标分辨率 <50px 时必须额外拉一张 zoom-in 子图放大比对**。输出字段：
   ```
   "icon_semantic_checks": [
     {
       "context": "Works FAB",
       "ios": {"shape": "folder", "arrow": "down", "color": "dark"},
       "hmos":    {"shape": "cloud",  "arrow": "up",   "color": "accent"},
       "match": false,
       "ios_drawable_ref": "@mipmap/icon_import_doc"  // 若 2.2.0-resources 有获取
     }
   ]
   ```
   每个可见非纯文本按钮/FAB **至少输出一条**；缺字段 → 视为跳过 → 结果作废重跑
10. **兄弟元素顺序（强制）**：对图中同一横向 Row 或同一纵向 Column 内含 ≥2 个兄弟节点（Tab 行 / 底部 BottomNav / 子菜单 / 并列按钮 / 列表项顺序）的容器，必须枚举左→右（或上→下）的 1st/2nd/3rd 位置，两端逐位比对，顺序不一致时一律归 `severity: high, is_migration_bug: true, category: layout`。输出字段：
   ```
   "siblings_order_checks": [
     {
       "container": "HomeView Tab Row",
       "axis": "horizontal",
       "ios_order": ["输入主题", "上传模板", "导入文档"],
       "hmos_order":    ["输入主题", "导入文档", "上传模板"],
       "match": false
     }
   ]
   ```
   每个容器**至少输出一条** check；没有 siblings_order_checks 字段 → 视为跳过此维度 → 返回结果作废重跑

```
