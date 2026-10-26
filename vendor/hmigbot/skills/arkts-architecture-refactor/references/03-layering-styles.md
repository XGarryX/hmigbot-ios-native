# 代码分层 + 资源 + 样式（R3/R4/R5）

## R3 代码分层（**SHOULD**——按职责拆分；不是命名硬规范）

规范原文："各业务代码类**应按照**模块功能进行拆分放置...**以下是实例**："

```
ets/
├── components/   可视组件
├── constants/    常量、字符串、枚举
├── pages/        Navigation 注册的整页
├── viewmodel/    状态容器
├── bean/         DTO
└── util/         工具函数
```

**关键解读**：

- 这是 "**示例性指引**"，不是"目录命名硬规范"——`viewmodels`（复数）/`utils`/`services`/`dialog`/`vm`/`api`/`db` 都是合理变体，**audit 不要标违规**。
- 真正要约束的是"**职责单一性**"："应保证类职责单一性，避免将不同的业务代码、方法堆砌在同一个类中"。判违规要看：
  1. 单文件 > 500 行 + 多职责（建议拆）
  2. pages/ 下混了多个不相关业务（说明 business 模块拆分有问题）
  3. 一个类里塞了网络 + 持久化 + UI 状态（违反职责单一）

> **不要把 audit 写成"目录拼写检查"**——AI 工程里 7 个 business 都用了 `viewmodels` 复数形态，那是合理的，因为本质职责清晰。

## R4 静态资源（**MUST**——客户已升级严格度）

> **客户校准**（2026-04）：R4.1 / R4.2 / R4.3 / R4.4 全部 **MUST**。新增图片资源**必须** webp/svg；动画**必须** webp，**禁止** gif；需要不同色版的图标**必须**用 `ColorUtils.hexToColorMatrix`（私仓 lib_common）+ `colorFilter` 实现，禁止预生成多色版本。

| 反例 | 正例 |
|---|---|
| `.png` 图标 | `.svg` 矢量 |
| `.png` 位图 | `.webp` 3x（设计稿尺寸 × 3，对应 Android xxhdpi） |
| `.gif` 动画 | `.webp` 动画（对齐 Android）|
| 直接用不同色版的图 | 单色 webp + `colorFilter(ColorUtils.hexToColorMatrix(hex))` —— **客户必查样例** |

### 单色 webp 着色（规范第四章 — R4.4 客户必查样例）

```ts
import { ColorUtils } from 'lib_common';

@ComponentV2
struct ThemedIcon {
  @Param iconRes: ResourceStr = $r('app.media.icon_play');
  @Param tintHex: string = '#FF3D7FFF';   // 任意 hex 色

  build() {
    Image(this.iconRes)
      .width(24).height(24)
      .colorFilter(ColorUtils.hexToColorMatrix(this.tintHex))
      // ColorUtils 把 hex 转成 4x5 ColorMatrix，配合 colorFilter
      // 把单色 webp 实时着色成任意目标色，避免一图多色版
  }
}
```

> 单色资源 + 运行时着色，比预生成多套色版本省体积也省维护——这是规范第四章特别推荐的做法。

转换批量脚本可用 `cwebp -q 80 input.png -o output.webp`，但 **改色 / 改尺寸的源图请走设计同学**，不要随手用脚本掉精度。

## R5 公共样式

### 颜色（区分通用色 vs 业务自有色）

规范定义的是"**通用**色 token"——跨业务、跨平台统一命名的全局公共色，**统一放在 business_common**。

**正确解读**：

| 类型 | 例子 | 命名要求 |
|---|---|---|
| 通用色（MUST） | 主色、主文字色、对话框按钮色 | 必须用规范的 19 个 token，放 business_common |
| 业务自有色（MAY） | 播放器轨道色、视频时长底纹、数字滚动数字色 | 业务模块自定义命名合理（slide_track_color 这类不算违规） |

**业务自有色判定**：颜色仅在该业务模块内使用、与"通用 UI 元素（主按钮 / 文字 / 对话框 / 标题栏）"无对应关系→属业务自有色，audit 不标违规。

`features/business_common/src/main/resources/base/element/color.json` 必须包含规范定义的 19 个通用 token：

| 规范名 | 用途 |
|---|---|
| `color_main` | 通用主色 |
| `color_page_bg` | 页面背景 |
| `color_text` / `color_text_hint` / `color_text_low` | 主/次/最次文字 |
| `color_main_btn_bg_start` / `color_main_btn_bg_end` | 强调按钮渐变 |
| `color_main_btn_bg_disabled` | 强调按钮禁用 |
| `color_title` / `color_title_right` | 标题栏 / 标题栏右侧菜单 |
| `color_dialog_bg` / `color_dialog_title` / `color_dialog_content` | 对话框背景/标题/内容 |
| `color_dialog_sure_bg_start` / `color_dialog_sure_bg_end` / `color_dialog_sure_text` | 对话框确定按钮 |
| `color_dialog_cancel_bg` / `color_dialog_cancel_text` | 对话框取消按钮 |
| `color_dialog_disable_bg` | 对话框按钮禁用 |

> 全平台同名很重要：Android/iOS/HarmonyOS 用同一套 token 才能高效迁移。重命名时对比 Android `colors.xml` 的命名约定。

### 字体 weight

```ts
// 反例
.fontWeight(FontWeight.Bold)

// 正例（用 UI 给的具体数值）
.fontWeight(500)
.fontWeight(600)
```

### 间距

```ts
// 反例：写死
.padding({ left: 16, right: 16 })

// 正例
import { BreakpointModel } from 'lib_common';
@Local breakpoint: BreakpointModel = AppStorageV2.connect(BreakpointModel)!;
// ...
.padding({ left: this.breakpoint.pagePadding, right: this.breakpoint.pagePadding })
```

`BaseViewModel` 已经暴露 `breakpoint` 引用，组件里若已持有 vm，可直接 `vm.breakpoint.pagePadding`。
