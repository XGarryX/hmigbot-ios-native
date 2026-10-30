# 工程结构规范（R1）

## 规则原文

整体采用 **壳工程 + 业务组件工程 + 公共独立组件工程** 三段式：

```
App
├── products/          壳工程
│   └── phone/         (具体设备入口)
├── AppScope/          全局资源
├── features/          业务组件工程
│   ├── business_xxx/
│   ├── business_xxx/
│   └── business_common/   (业务公共依赖)
└── components/        公共独立组件（含三方独立组件）
    ├── module_xxx/
    └── module_xxx/
```

> **为什么这么拆**：便于业务线之间代码迁移、私仓独立维护。把不同业务塞进同一个目录就丧失了这个好处。

## 反例 → 正例

### 反例：单 entry 模块全堆

```
MyApp/
├── entry/
│   └── src/main/ets/
│       ├── pages/HomePage.ets
│       ├── pages/MinePage.ets
│       ├── pages/LoginPage.ets
│       └── viewmodel/...
└── oh-package.json5
```

### 正例：拆三段

```
MyApp/
├── products/phone/
│   └── src/main/ets/entryability/EntryAbility.ets
├── AppScope/
├── features/
│   ├── business_home/   src/main/ets/{pages,viewmodel,components,constants,bean,util}
│   ├── business_mine/   ...
│   ├── business_login/  ...
│   └── business_common/ (其他 business 共用的常量/工具/UI)
└── components/
    └── module_advertisement/  (跨业务复用的独立 UI 模块)
```

## 改造步骤

1. 在根目录建 `products/phone/`、`features/`、`components/` 三个目录。
2. 把 `entry` 模块改名为 `products/phone`（或新建后迁移）。修改其 `module.json5`、`build-profile` 中模块名。
3. 按业务拆 features：从 entry 的 `pages/` 出发，按页面归属拆出 business_xxx，每个 business 独立 har 模块（带自己的 oh-package.json5、Index.ets、ets/ 子目录）。
4. 公共类（无业务属性、跨 business 复用）下沉到 `features/business_common`；纯 UI 组件（独立可复用）下沉到 `components/module_xxx`。
5. 跟根 `build-profile.json5` 的 `modules` 数组同步注册新模块。

## 拆分判定

- 一段代码只服务单一业务（"我的"、"播放"、"登录"等） → `features/business_<name>`
- 一段代码服务多个业务（颜色 token、字符串、网络封装、Base 类） → `features/business_common`
- 一段代码是纯 UI 组件且跟业务无耦合（广告位、分享面板、字号设置） → `components/module_<name>`
- 一段代码只服务 entry 启动（Ability/AppStorage 初始化） → `products/phone`

---

## 反作弊：禁止用单 business_main 当过渡形态

> **来自 AIPPT_ArkTS_rebuild 项目实战教训**：第一轮重构因为单 turn 风险控制偷懒，把 22 page 全塞进单 business_main，被客户当场识破。本段是硬性约束。

### 硬规则

**audit / verify 阶段必须验证**：
1. `features/business_* (排除 business_common) >= 2` —— 否则**等价于把所有业务堆进单模块**，违反 R1.2 字面"务必将不同业务代码拆分为独立的 business 组件工程"，**判 P0 FAIL**
2. **禁止任何"过渡形态"借口**：单 business_main 不是合规中间态，是合规失败态
3. **顶层 `components/` 目录必须存在**且至少 1 个 `module_*` —— R1.3 三段式不能省一段

### 双 baseline 实证（最低基准）

| baseline | features/ | 非 common business 数 | components/module_* |
|---|---|---|---|
| AI 工程 | business_common + business_home + business_login + business_mine + business_setting + business_video + business_interaction | **6** | 6 个（advertisement / setfontsize / share / swipeplayer / text_reader / transition）|
| Scan 工程 | business_common + business_home + business_login + business_mine + business_setting | **4** | 同上 6 个 |

**结论**：合规项目的 features/ 至少 4 个非 common business，components/ 至少 6 个 module_*。**少于此基线不算合规**。

### 拆分指引（按域）

按 page 域用途归口，不按"页面数量平均"。常见域：

- `business_home` — 首页 / 主 Tab 容器 / 启动 / 引导（home / splash / guide / main 等）
- `business_login` — 登录注册 / 账号 / 实名（login / accountInfo 等）
- `business_mine` — 个人中心 / 设置 / 关于 / 反馈 / 客服（about / feedback / customerService 等）
- `business_setting` — 偏好设置 / 主题 / 字体（如有）
- `business_video` / `business_template` / `business_ppt` — 各业务核心域，视产品定义
- `business_vip` — 会员中心 / 支付 / 订阅 / 退款（memberCenter / manageRenew / refundProgress 等）
- `business_interaction` — 评论 / 点赞 / 分享 / 互动（如有）
- `business_common` — **必有**，承载跨业务 model / event / preference / network / database 等无 UI 的基础设施

### components/module_* 拆分指引

跨业务可复用且独立可发布（可以脱离当前业务存在）的 UI / 工具模块，例如：

- `module_advertisement` — 广告位 / 信息流广告组件
- `module_share` — 分享面板（封装微信 / 微博 / 钉钉等三方 SDK）
- `module_setfontsize` — 全局字号调节器
- `module_swipeplayer` — 自定义滑动播放器
- `module_text_reader` — 文本阅读器
- `module_transition` — 自定义转场动画
- 也可放一些"业务无关但项目特有"的 UI（如 Loading 全局组件）

#### components/module_* 颗粒度抽取判断（**重要补充**）

> **不要硬凑 6 个 module 跟 baseline 对齐**，但也**不要把可独立的组件偷懒塞在 `business_common/components/` 里**。

**Baseline（AI/Scan）有的 6 个 module 是工程实有功能映射**，不是模板配额：
- AI/Scan 都是综合 AI/扫描工具，本来就有：广告变现、字号调节、短视频/图集横滑、小说阅读、自定义转场
- 工具型工程（PPT 生成、计算器、记事本）功能面窄，少几个 module 是合理的（**不能也不应**强凑成"广告/转场/阅读器"）

**真正的判定标准（按下表 grep）**：

| 触发器（grep 命中） | 说明 | 应抽到 |
|---|---|---|
| `Web({...})` 出现在 ≥2 个 page | H5/支付/客服/隐私页都在重复 UA / referer / scheme 拦截 boilerplate | `module_webview` |
| 跨 ≥2 个 business 的纯 UI 组件类（如 `*Item.ets` / `*Card.ets` 被多页面引用） | 真正的"跨业务复用"，违反 R1.2 不应在 business_common | `module_<组件名>` |
| 自定义 `PageTransition` / `transitionEffect` / `customTransition` | 独立转场动画 | `module_transition` |
| Lottie 引导 / 复杂 SVG 动画组件 | 动画引擎独立 | `module_animation`（如有） |
| 广告 SDK 调用（CSJ / GroMore / Pangle） | 必须独立模块化 | `module_advertisement` |
| 富文本 / Markdown 渲染 | 第三方 SDK 包装 | `module_text_reader` 或 `module_markdown` |

**反模式（refactor audit 必查）**：
- ❌ 多个 page 用 `Web({})` 但项目 `components/` 目录里没有 `module_webview` — 漏抽
- ❌ 用"AI 也只有 6 个"做借口拒绝抽 → **不对**，颗粒度看复用证据，不看数量配额
- ❌ 把 **业务耦合的 *Item.ets / *Card.ets** 强行抽到 `components/module_*` —— **也不对**，这会割裂"Bean + VM + Service + Pages"的完整子系统。例如 PptTemplateItem 依赖 PptTemplateBean、TemplateService、TemplateViewModel，这些都在 features 侧；单独把 UI 抽到 components 等于让 components 反向依赖 features，违反三段式

**抽与不抽的判定标准（baseline 实证）**：

AI 工程的 `module_swipeplayer/VideoCard.ets` 是范本：
```ts
import { ... } from '../type/Index'           // ← Bean 在 module 内
import { ... } from '../viewmodel/VideoCardModel'  // ← VM 在 module 内
import { AVPlayerManager } from '../controller/AVPlayerManager'  // ← Controller 也在 module 内
```
**`components/module_*` 是"包含 Bean/VM/Controller/UI 的自包含子系统"**，不是裸 UI 组件容器。

| 决策 | 触发条件 | 例子 |
|---|---|---|
| **抽到 `components/module_*`** | 业务无关 + 子系统能整体迁出（Bean/VM 都不依赖 features） | Web 容器、广告、转场、字号、分享 SDK |
| **留在 `features/business_common/components/`** | 业务相关（依赖 business 的 Bean/Service/VM）+ 跨 business 引用 | PptTemplateItem、VideoItem、TemplateCardItem |
| **留在所属 business 模块内** | 仅单 business 使用 | RecommendBanner（仅 home） |

**第 4 阶段 audit 补充 grep**：
```bash
# 检查 Web 容器复用
grep -rln "Web({" features/business_*/src/main/ets/pages/ | wc -l   # ≥2 → 应有 module_webview

# 检查 business_common/components 跨 business 引用
for f in features/business_common/src/main/ets/components/**/*.ets; do
  name=$(basename "$f" .ets)
  refs=$(grep -rln "$name" features/business_*/src/main/ets/pages/ | wc -l)
  echo "$refs $f"
done | sort -rn   # ≥2 引用 → 应下沉到 components/module_*

# 检查自定义转场
grep -rln "PageTransition\|customTransition\|transitionEffect" features/ | head -5  # 任意命中 → 应有 module_transition
```

### 当 page 数量不足以拆 business_* 时

例如简单 utility app 只有 5 个 page。此时仍**应**至少拆 3 个：

- `business_home`（主 page + 启动）
- `business_mine` 或 `business_setting`（侧边/抽屉）
- `business_common`

而不是塞进单 business_main。**业务粒度边界看域，不看页数**。
