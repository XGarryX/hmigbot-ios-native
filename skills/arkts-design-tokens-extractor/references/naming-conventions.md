# DesignTokens 命名风格指南

本 skill 在生成 `DesignTokens.ets` / `float.json` / `color.json` 增量补丁时遵循的命名规则。

---

## 1. 通用原则

- **语义优先于值**：`Card.coverHeight=160` 优于 `dp_160`（值改了语义不动）
- **驼峰用于 ArkTS**：`Button.circle.lg`
- **下划线用于资源**：`button_circle_lg`
- **层级最多 3 级**：`Component.Variant.Size`（如 `Badge.vip.width`）
- **避免单字符前缀**（除非是 ArkTS 项目惯例如 `gy_xxx`）

---

## 2. DesignTokens.ets 类内命名

```typescript
export class DesignTokens {
  // ① 字号 — Typography
  static readonly Typography = {
    caption: 12,      // 副文本 / 标签
    bodySmall: 14,    // 正文小
    body: 16,         // 正文
    title3: 18,       // 三级标题
    title2: 20,       // 二级标题
    title1: 24,       // 一级标题
    display: 28,      // 大数字 / 营销文案
  };

  // ② 间距 — Spacing
  static readonly Spacing = {
    xs: 4,
    sm: 8,
    md: 12,
    lg: 16,
    xl: 24,
    xxl: 32,
  };

  // ③ 圆角 — Radius
  static readonly Radius = {
    sm: 4,
    md: 8,
    lg: 14,
    xl: 20,
    pill: 9999,    // 胶囊
  };

  // ④ 按业务组件命名（无现成类别时新增）
  static readonly Card = {
    coverHeight: 160,
    scrollerWidth: 200,
  };

  static readonly Badge = {
    vip: { width: 38, height: 20 },
    new: { width: 28, height: 16 },
  };

  static readonly Button = {
    circle: { sm: 32, md: 40, lg: 48 },
    height: { sm: 32, md: 40, lg: 48 },
    radius: { default: 8, pill: 9999 },
  };

  static readonly Dialog = {
    paddingHorizontal: 33,
    paddingVertical: 24,
  };

  // ⑤ 颜色 — Colors
  static readonly Colors = {
    // 文字层级
    textPrimary: '#FF2D2D2D',
    textSecondary: '#FF999999',
    textTertiary: '#FFCCCCCC',
    textInverse: '#FFFFFFFF',

    // 背景
    bgPrimary: '#FFFFFFFF',
    bgSecondary: '#FFF5F5F5',
    skeleton: '#FFF2F2F2',

    // 品牌
    brand: {
      lime: '#FFD0FE37',
      lemon: '#FFFFF965',
      orange: '#FFFF852A',
    },

    // 半透明（按透明度命名）
    overlay: {
      mask20: 'rgba(0,0,0,0.20)',
      mask50: 'rgba(0,0,0,0.50)',
      mask80: 'rgba(0,0,0,0.80)',
    },

    // 业务高亮
    scaleHighlight: '#3632D178',  // ARGB
  };
}
```

---

## 3. float.json 资源命名

| 用法 | 命名前缀 | 示例 |
|---|---|---|
| 通用尺寸 | `dp_` | `dp_4 / dp_8 / dp_12 / dp_16` |
| 业务专用 | `<scope>_<purpose>` | `card_cover_height / scroller_card_width / dialog_padding_h` |
| 字号（如不进 Typography） | `font_` | `font_caption / font_body / font_title1` |

```json5
{
  "float": [
    { "name": "dp_8", "value": "8vp" },
    { "name": "dp_12", "value": "12vp" },
    { "name": "card_cover_height", "value": "160vp" },
    { "name": "scroller_card_width", "value": "200vp" },
    { "name": "dialog_padding_h", "value": "33vp" }
  ]
}
```

**禁止**：`size1 / size2 / value_a / margin_xxx_yyy_zzz_aaa`（不可读 / 过深）

---

## 4. color.json 资源命名

| 用法 | 命名前缀 | 示例 |
|---|---|---|
| 文字 | `text_` | `text_primary / text_secondary` |
| 背景 | `bg_` | `bg_primary / bg_skeleton` |
| 品牌 | `brand_` | `brand_lime / brand_lemon` |
| 半透明蒙版 | `mask_<alpha>` | `mask_20 / mask_50` |

```json5
{
  "color": [
    { "name": "text_primary", "value": "#FF2D2D2D" },
    { "name": "text_secondary", "value": "#FF999999" },
    { "name": "brand_lime", "value": "#FFD0FE37" },
    { "name": "mask_50", "value": "#80000000" }
  ]
}
```

**ARGB 顺序**：`#AARRGGBB`（HarmonyOS 标准 8 位 hex 含 alpha）

---

## 5. 反例（避免）

| ❌ | 为什么不好 | ✅ |
|---|---|---|
| `dp_color_red_button` | 跨类别拼接、含义重复 | `Colors.brand.red` + `Button.height.md` 分开 |
| `dp_140_card` | 把值嵌入名字 | `Card.coverHeight=140`（值变名字不动） |
| `c1 / c2 / c3` | 无语义 | `textPrimary / textSecondary / textTertiary` |
| `MyCustomButton_padding_left_inner` | 过深 + 主观命名 | `Button.padding.start` |
| `font20bold` | 大小+样式拼接 | `Typography.title2` + `.fontWeight(FontWeight.Bold)` |

---

## 6. 命名推断速查（codemod 自动建议）

按字面量上下文推断目标命名：

| 上下文 | 值 | 推断目标 |
|---|---|---|
| `.fontSize(N)` | 12-28 | `Typography.<size>` |
| `.padding/margin({N})` | 4-32 | `Spacing.<xs/sm/md/lg/xl>` |
| `.borderRadius(N)` | 4-20 | `Radius.<sm/md/lg/xl>` |
| `.borderRadius(50/9999)` | 圆形 | `Radius.pill` |
| `.width/height(N)` + `Image` 上下文 | 100-300 | `Card.coverHeight / Card.thumbnail` 等 |
| `.width/height(N)` + `Button` 上下文 | 32-56 | `Button.height.<sm/md/lg>` |
| `.fontColor('#xxx')` 高频 | 任意 | `Colors.text<Primary/Secondary/Tertiary>` |
| `.backgroundColor('#xxx')` 含半透明 | rgba | `Colors.overlay.mask<alpha>` |
| `linearGradient.colors[..]` 品牌色 | 高饱和 | `Colors.brand.<color-name>` |

---

## 7. 增量演进

DesignTokens **只增不删**——已有 token 不重命名（可能被业务代码大量引用）。新增 token 时：

1. 检查是否能用现有 token 表达（如 `Spacing.md=12` 已有，避免新建 `dp_12_card`）
2. 若必须新增，遵循 §1 通用原则
3. 写入对应 `float.json` / `color.json` 资源条目
4. 在 codemod patch 中替换字面量

---

> 本指南被 [arkts-design-tokens-extractor](../SKILL.md) 在生成命名建议时引用。
