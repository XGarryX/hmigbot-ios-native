> **iOS 源输入**：读取 Swift/Objective-C、SwiftUI/UIKit、Xcode 工程及原生资源；实际源构建与设备观测依赖可用的源平台环境。鸿蒙侧构建和验收保持原流程。源侧操作详见 `a2h-spec/references/native-input.md`。

# Step 4.1.3 — 长页面分段截图与拼接（可滚动页专用）

> 从 SKILL.md §4 Step 4.1.3 抽出。`capture_mode == "long"` 时 Read。
>
> **适用场景**：详情页 / 设置页 / Feed / 长表单等**合法长页**。区别于 Step 4.2 里 `scroll_needed: true` 的「疑似布局 bug」告警路径——前者是内容本身就超屏，后者是 `layoutWeight` 误用把内容挤出屏幕。**两者优先级：先判定是否长页，再跑对比时出现 `scroll_needed` 才视为 bug。**

---

## 2.1.3-a 触发判定（必须先判断，再决定走单帧还是长图）

对每个页面在截完首屏后立即判定：

| 端 | 判定命令 | 判定规则 |
|----|---------|---------|
| HarmonyOS | `hdc shell uitest dumpLayout` 解析根节点 `bounds` 的 `bottom` | `content_bottom > viewport_height` → 长页 |
| iOS | `adb shell uiautomator dump` 解析根节点 `bounds` | 同上 |

**双保险（DOM 判定失败时的兜底）**：
- 在页面空白区域执行一次 `scrollBy(0, 50px)` 后再截图，与首屏像素差异 > 1% → 可滚动 → 走长图流程；差异 < 1% → 按单帧处理；完成后 `scrollTo(0)` 归位。

判定结果写进 `progress.json`：`"capture_mode": "single" | "long"`，单页闭环内保持一致，避免轮次间抖动。

---

## 2.1.3-b 分段截图算法（每端独立执行，**不依赖「两端滑动距离一致」**）

**核心原则**：不承诺两端滚动像素一致——density、viewport、bounce、惯性都会让 `scrollBy(N)` 在两端滑出不同内容。所以**每端各自滚、各自截、各自拼**，靠**图像内容自对齐**裁掉重叠区，保证每端产出一张内容完整无重复的长图。两端对齐放到 2.1.3-d 再做。

```
单端长图采集伪代码（iOS / HarmonyOS 同构）:

segments = []
scrollTo(0)                               # 强制归位
wait_until_stable(500ms)                  # 等入场动画 + fling 惯性结束
disable_animations()                      # iOS: window_animation_scale=0
                                          # HMOS: Scroller.scrollTo 直接定位，不用 fling

frame_0 = capture_and_resize()
segments.append(frame_0)

viewport_h = get_viewport_height()        # 可滚动容器的高度，非屏幕高度
step = viewport_h * 0.8                   # 故意留 20% 重叠区，给模板匹配用
max_frames = 20                           # 上限，防死循环

FOR i IN 1..max_frames:
    scroll_by_deterministic(step)         # iOS: UiScrollable.scrollForward + 等停
                                          # HMOS: Scroller.scrollTo({ yOffset: i*step })
                                          #       + 监听 onScrollStop
    wait_until_pixel_stable()             # 连续两帧像素差 < 0.1% 视为稳定

    frame_i = capture_and_resize()

    # 终止条件 1：到底（新帧与上一帧底部完全重合）
    IF pixel_identical(frame_i, segments[-1]):
        break

    # 终止条件 2：滚动距离未变（scrollTop 不再增加）
    IF get_scroll_top() == prev_scroll_top:
        break

    segments.append(frame_i)

long_image = stitch_by_template_match(segments, overlap_search_px=300)
scrollTo(0)                               # 归位，便于下一轮
```

---

## 2.1.3-c 重叠区模板匹配拼接

**为什么需要**：即使两帧滚了 80% viewport，受 bounce / sub-pixel 渲染影响，精确偏移仍可能偏几个像素。直接按 `step` 裁会出现错位或重复行。

**做法**（走 `scripts/stitch_long_screenshot.py`，OpenCV `matchTemplate`）：

1. 对相邻两帧 `frame_N` 和 `frame_{N+1}`：
   - 从 `frame_N` 底部取 200px 高的条带作为 template；
   - 在 `frame_{N+1}` 顶部 500px 范围内滑动匹配，取 `TM_CCOEFF_NORMED` 得分最高的 y 偏移 `y_match`。
2. 匹配置信度 `score >= 0.95` → 按 `y_match` 裁掉 `frame_{N+1}` 顶部重叠部分再拼。
3. `score < 0.95`（纯色背景 / 无锚点）→ 降级：按 `step` 像素裁，并在长图 metadata 标 `low_confidence_segments: [i]`。
4. `score < 0.7` → 放弃长图，回退单帧 + 在报告中标 `scroll_stitch_failed, reason: low_content_variation`。

脚本接口（落到 `scripts/stitch_long_screenshot.py`）：
```text
python3 $SKILLS_ROOT/arkts-visual-verify/scripts/stitch_long_screenshot.py \
  --frames spec/visual-verify/screenshots/{side}/{page_id}_seg_*.png \
  --out    spec/visual-verify/screenshots/{side}/{page_id}_long.png \
  --meta   spec/visual-verify/screenshots/{side}/{page_id}_long.json \
  --overlap-search 300 --min-score 0.95
```

产出 `{page_id}_long.png` + `{page_id}_long.json`（记录每段偏移、匹配得分、降级标记）。

---

## 2.1.3-d 两端对齐与分块对比

长图出来后**不要直接整图 diff**——density、状态栏、手势条高度都不同。

1. **裁系统 UI**：两端分别裁掉顶部状态栏 + 底部手势条（固定 y 区间，从 `uitest dumpLayout` 读系统 UI 高度）。
2. **宽度归一**：两张长图 resize 到同一基准宽度（默认 1080px），高度按比例缩放。若归一后总高度差 > 10% → 报 `scroll_content_length_mismatch`（可能一端漏/多内容）。
3. **锚点切段**：在 HarmonyOS 长图上识别结构锚点（标题栏底边、分隔线、卡片边界 —— 可用边缘检测 `cv2.Canny` + 长横向直线 `cv2.HoughLinesP`，或直接让多模态按「找出所有视觉分段线的 y 坐标」输出）。在 iOS 长图上按内容特征（最长的同色/边缘线）找对应锚点。
4. **分块 sbs**：按锚点对把长图切成 N 个「语义块」，每块单独走 `compose_side_by_side.py` 生成 sbs 图，**逐块**喂给多模态做 Step 4.2 的 9 项分析。避免一张超长图被压扁看不清细节。
5. **差异聚合**：各块 `differences[]` 带上 `block_index` 字段合并到页面级 JSON，按 severity 走 Step 4.3 分类。

---

## 2.1.3-e 兜底降级

以下任一情况 → **放弃长图流程，退回单帧 + 在报告标注**，不要强拼出错位长图骗自己：

- 2.1.3-b 里 `max_frames` 用尽但仍未检测到底部（可能无限流 Feed）→ 只取前 N 屏合成，metadata 标 `capped_at: N`。
- 2.1.3-c 连续 2 段匹配 `score < 0.7`。
- 2.1.3-d 两端长度差 > 30%（锚点不可比）。

降级时 progress.json 记 `"capture_mode": "single_fallback", "fallback_reason": "..."`，避免死循环重试。

---

## 2.1.3-f 产物与清理

```
spec/visual-verify/screenshots/{side}/
  {page_id}.png                 # 首屏（始终保留，单帧模式的主图）
  {page_id}_seg_00.png ...      # 分段原图（长图模式，debug 用，可压缩/清理）
  {page_id}_long.png            # 拼接后整张长图
  {page_id}_long.json           # 拼接 metadata（偏移、得分、降级标记）
  {page_id}_block_NN.png        # 锚点切块
  {page_id}_block_NN_sbs.png    # 两端同块 sbs，喂多模态用
```

Phase 6 清理时保留 `{page_id}_long.png` + `_sbs.png` + `_long.json`，删 `_seg_*` 节省空间。

---

## 2.1.3-g 长图复用

iOS 源端长图（`{page_id}_long.png` + `_long.json` 元数据）直接落在 `screenshots/ios/{trip_id}/`，已存在即跨轮复用——跳过整个 iOS 源端分段滚动 + 拼接流程（省 ~30-60s/页）。**段图 `_seg_*` 是中间产物**（罕见地需要重拼时，反正得重跑 iOS 源端）。

HarmonyOS 端长图每轮重跑分段+拼接（代码改了，长页内容可能变）。
