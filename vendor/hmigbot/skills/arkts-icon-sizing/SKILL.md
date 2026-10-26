---
name: arkts-icon-sizing
description: 检测并修复 Android→HarmonyOS UI 迁移中，因丢失 `.width()/.height()` 而导致渲染尺寸错误或比例 失真的 ArkUI/HarmonyOS `Image` 组件。转换器保留了 `.objectFit()` 却丢掉了尺寸，使 `resources/base/media` 里的位图图标按**原始像素尺寸**渲染（通常大 3 倍，非方形的还会被拉伸）。当用户反馈图标/图片在鸿蒙页面 （主页、我的、弹窗、列表项——任何位置）上「太大 / 太小 / 被拉伸 / 被压扁 / 比例异常 / 图标变形 / 显示太大 / icons look off」，或要求「统一检查/修复各页图标比例」，或刚做完 a2h / ArkUI UI 迁移（大量 Android ImageView 用了 wrap_content）时触发。内置「审计→测量→修复」三步流水线：用源位图的像素尺寸 ÷ 密度还原每个图标的正确 vp 尺寸，同时保留真实宽高比。即使用户只说「图标比例不对」而未指明原因，也应触发。
metadata:
  type: domain
  domain: ui
  tags:
  - ui
  - migration
  - icon
  - image
  - sizing
---
# ArkUI 图标尺寸修复（Android→HarmonyOS 迁移修复）

## 问题与成因

在 Android 中，`android:layout_width/height="wrap_content"` 的 `ImageView` 会按 drawable 的**标称 dp**
尺寸渲染。一张只放在 `*-xxhdpi`（3 倍密度）目录的位图，磁盘上可能是 `90×90 px`，显示为 `30×30 dp`。

Android→HarmonyOS UI 转换器常常复刻了 `ImageView` 的 `.objectFit(...)`，却**丢掉了 `.width()/.height()`**
（因为 `wrap_content` 没有固定数值可抄）。位图被原样拷进 HarmonyOS 的 `resources/base/media`——而**该目录无密度
限定符**——于是 ArkUI 按 `Image` 的**字面像素尺寸（当成 vp）**渲染。那张 `90×90 px` 的图标现在显示为 `90×90 vp`，
即**大了 3 倍**。更糟的是，非方形图标（`45×23` 的电池、`44×26` 的箭头）在没有显式尺寸时保持原始像素框，一旦
某根轴被布局约束触碰，宽高比就明显失真——这就是用户看到的「比例异常 / 图标变形」。

修复办法是把每个欠约束的 `Image` 还原成它的**标称 vp 尺寸**：

```
标称 vp = 源位图像素 ÷ 源密度倍数
```

宽和高**分别独立**相除，这正是还原正确宽高比的关键。已经带显式 `.width()/.height()` 的图标是正常的——**不要**
碰它们，也**不要**用「把位图挪进带密度限定的目录」这种全局手段去修（那会把本来正确的图标缩小）。缺陷只针对
**那一部分丢了尺寸的 `Image`**。

## 何时使用

- 用户反馈图标/图片在鸿蒙页面上过大、过小、被拉伸或被压扁——尤其刚做完 a2h / ArkUI UI 迁移之后。
- 用户要求「统一检查/修复图标比例」。
- 做迁移 QA，想横扫每个页面排查这一类缺陷。

不属于本 skill：文本截断（`arkts-text-truncation`）、大字体布局溢出（`arkts-large-font`）、深色模式图标变色
（`arkts-dark-mode`）、生成全新 UI（`arkts-component-builder`）。那些是不同的问题。

## 两种用法

本 skill 有两条路径，共用同一套确定性逻辑：

| 路径 | 入口 | 是否有人工审核 | 适用 |
|---|---|---|---|
| **A. 全自动（集成入口）** | `icon_autofix.py` | 无 | 被 `arkts-structural-closure` pipeline 模式调用；CI / 无人值守批量修复 |
| **B. 人工三步流** | `icon_audit.py` → `icon_dims.py` → `icon_fix.py` | 有（审 `icon_plan.json` 后再 `--apply`） | 人工 ad-hoc 排查，想逐步检查中间产物 |

> **先提交或暂存你的工作。** 修复会就地改源文件；干净的 git 状态让一次坏的运行可以秒回滚。

---

## 用法 A：全自动（headless 单入口）

```bash
# 最佳：让 Android 源逐图决定密度（多模块 → 传所有 res 根）
python <skill>/scripts/icon_autofix.py --apply \
    --android-res <android>/app/src/main/res <android>/base/src/main/res \
    --output-json icon_autofix.json

# 无 Android 源 → 用工程单一密度桶兜底（默认 3 = xxhdpi）
python <skill>/scripts/icon_autofix.py --apply --density 3 --output-json icon_autofix.json
```

一次跑完 `审计 → 测量 → 修复 --apply → 复审`，**无任何人工 gate**，只输出一个机读 JSON
（`passed / scanned / fixed_count / fixed[] / dynamic_unresolved[] / no_raster_unresolved[] / residual_static[]`）。
**从 HarmonyOS 工程根目录运行**（脚本自动发现 `*/src/main/ets` 与 `resources/base/media`）。

**为什么无人工审核也安全：** 尺寸是 `像素 ÷ 密度` 的确定性计算；只动「无尺寸 / 单尺寸无 aspectRatio」的
`Image`，绝不碰已带尺寸的；幂等（重复跑第二次 `fixed_count=0`）；git 可整体回滚。**建议传 `--android-res`
以获得逐图精确密度**，缺省回退 `--density 3`。动态源图标 / 无 raster 的项**只记录、不修改**（见用法 B 第 4 步）。

---

## 用法 B：人工三步流

三个脚本按序运行，通过两个 JSON 文件（`icon_report.json`、`icon_plan.json`）通信，每一步落盘前都可检查。

### 1. 审计 — 找出每一个欠约束的 Image

```bash
python <skill>/scripts/icon_audit.py
```

自动发现 `*/src/main/ets` 根并写出 `icon_report.json`。它打印两份清单：**静态**欠约束图标
（`$r('app.media.xxx')`，可自动修）与**动态源**图片（`Image(this.foo())`、三元、`@Builder` 参数——需手工解析，
见下）。`ImageFit.Fill` 用法单列供人工复核：`Fill` 会拉伸填满，通常是**可拉伸背景图形**（`shape_*_bg` 弹窗横幅）
的有意为之，除非真有图标用了 `Fill`，否则放着别动。

被标记 = 修饰链**无 width 且无 height**（`NO-DIMS`）或**只有其中一个且无 `aspectRatio`**
（`ONE-DIM-NO-ASPECT`）。`width('100%') + height('100%')` 视为有意的满铺，不标记。

### 2. 测量 — 还原每个图标的正确 vp 尺寸

```bash
# 最佳：让 Android 源逐图决定密度（多模块 → 传所有 res 根）
python <skill>/scripts/icon_dims.py --report icon_report.json \
    --android-res <android>/app/src/main/res <android>/base/src/main/res

# 无 Android 源 → 用工程单一密度桶兜底（默认 3 = xxhdpi）
python <skill>/scripts/icon_dims.py --report icon_report.json --density 3
```

对每个被标记的静态图标，读取 HarmonyOS media 文件（webp/png/jpg/svg）的像素尺寸，除以密度倍数，写出
`icon_plan.json`（`{icon: {w, h, px, density, src}}`）。

**落地前务必审 `icon_plan.json`。** 核对 `src` 列是真实密度目录（如 `mipmap-xxhdpi`），且算出的 vp 尺寸对一个
图标而言合理（小图标个/十位数，插图更大）。若大量图标显示 `assumed Nx`，说明没找到 Android 源——确认工程实际密度
或补 `--android-res`。

标为 **UNRESOLVED** 的图标没有 raster（属动态引用、纯 SVG `<shape>` 转换或矢量图）——手工处理（下一节）。

### 3. 修复 — 插入尺寸（先 dry-run）

```bash
python <skill>/scripts/icon_fix.py --plan icon_plan.json --report icon_report.json          # 预览
python <skill>/scripts/icon_fix.py --plan icon_plan.json --report icon_report.json --apply   # 落盘
```

逐处在 `Image(...)` 开头之后插入：
- **NO-DIMS** → `.width(W)` `.height(H)`（还原的标称 vp；固定尺寸、真实比例）。
- **ONE-DIM** → 仅 `.aspectRatio(W/H)`——保留有意的那一维（如满宽横幅的 `.width('100%')`），只修比例。

它实时重扫，所以即使前面的插入移动了行号也安全。动态图片只报告，绝不自动改。

### 4. 手工解析动态源图片

审计/修复读不出 `Image(this.vipEditRes())` 或 `Image(cond ? $r('app.media.a') : $r('app.media.b'))` 的尺寸。
对每一处：

1. 读代码找出它能解析到的具体资源名（顺着方法/三元跟踪）。勾选类开关通常指向两张同尺寸资源。
2. 查这些名字：`python <skill>/scripts/icon_dims.py --media <media_dir> --icons ic_a,ic_b`。
3. 手工给 `Image(...)` 加 `.width(W).height(H)`（若已设一维则用 `.aspectRatio()`）。`@Builder tabItem(icon: Resource)`
   会让所有调用方共享一个尺寸——在 Builder 的 `Image` 上设一次即可。

### 5. 校验

```bash
python <skill>/scripts/icon_audit.py        # 静态被标记数应为 0
```

然后**编译工程**（如 `hvigorw assembleHap ...`）——插入的都是普通 `.width(n)/.height(n)/.aspectRatio(n)`（vp 数值），
编译通过即确认语法无误。只应剩下有意跳过的动态项（已手工修）和 `Fill` 背景。

## 决策规则与边界

- **密度是逐图的，不是全局的。** 传了 `--android-res` 时 `icon_dims.py`/`icon_autofix.py` 读每个图标的真实源目录。
  多数 app 只发一个桶（xxhdpi=3），但别假设——通过 `src` 列核实。倍数表：ldpi .75，mdpi 1，hdpi 1.5，xhdpi 2，
  xxhdpi 3，xxxhdpi 4。
- **方形 SVG 不会失真。** 方形 viewBox 的 `<shape>`/矢量图按标称 vp 渲染、比例正确——它不会「比例错」，只可能
  「尺寸错」。若这种 SVG 渲染得过大（如 `100×100` viewBox 显示成 100vp，而本意是小图标），查 **Android drawable 的
  `android:width/height`** 取本意 dp 并显式设上。否则优先级低。
- **`shape_*_bg` 上的 `ImageFit.Fill`** 是可拉伸横幅背景——放着别动。只在真图标的盒子比例 ≠ 图标比例时才管 `Fill`。
- **别碰已带尺寸的图标。** 重点就是欠约束的那部分；全局改资源密度会破坏本来正确的图标。
- **多模块 Android 工程**把共享资源放在 `base`/`common` 模块——把每个 `*/src/main/res` 根都传给 `--android-res`，
  密度查找才能找到它们。

## 脚本

| 脚本 | 职责 |
|---|---|
| `scripts/icon_audit.py` | 扫 `.ets` → `icon_report.json`（被标记静态 + 动态 + Fill）。导出 `discover_roots()` / `audit()`。 |
| `scripts/icon_dims.py`  | `report` → `icon_plan.json`：标称 vp = media 像素 ÷ 源密度。导出 `build_plan()`；亦支持 `--icons` 临时查询。 |
| `scripts/icon_fix.py`   | `report`+`plan` → 插入 `.width/.height`（NO-DIMS）或 `.aspectRatio`（ONE-DIM）。导出 `apply_fixes()`；默认 dry-run，`--apply` 落盘。 |
| `scripts/icon_autofix.py` | **全自动单入口**：审计→测量→修复→复审一次跑完，输出单个 JSON，无人工 gate。被 `arkts-structural-closure` 调用。 |

四者均为纯 Python 标准库（无依赖），支持 `--help`，从工程根运行时自动发现 ets 根与 `resources/base/media`。

## 与 arkts-structural-closure 的集成

本 skill 通过 `icon_autofix.py` 接入 `arkts-structural-closure` 的 **pipeline 模式**（§2.3，全局兜底，Stage 3 末尾），
作为一个**自愈 detector**：structural-closure 在整工程结构性兜底时顺带调用本入口，自动补齐欠约束图标的尺寸，
**无任何人工介入**，且**非阻断**（动态源/无 raster 项只记录）。a2h-execute §6 已调 structural-closure pipeline 模式，
因此集成后图标尺寸修复随之自动运行。传 `--android-res` 可提升密度精度，缺省回退 `--density 3`。

## 与其他 skill 的关系

- **arkts-structural-closure**：⭐ 全自动全局图标尺寸自愈的集成宿主（pipeline 模式调用本 skill 的 `icon_autofix.py`）。
- **arkts-truncation-fix**：图片被裁切 / 容器溢出 / 多设备响应式（方向相反——它倾向去掉固定尺寸换 `%`/`aspectRatio`）。
- **android2hmos-resources-convert**：资源/资产侧转换（res/ → resources/、SVG 坐标/格式修复）；本 skill 修的是 `.ets` 消费侧。
- **arkts-ui-alignment**：Android UI 迁移对齐 / SymbolGlyph 图标体系。
- **arkts-knowledge-verifier**：不确定某 API 是否存在 / 版本兼容时。
