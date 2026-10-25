# §M2 Source-compare 模式 — 详细执行手册

主 SKILL.md §M2 卡片的详细执行手册。**当只有两份代码（iOS 项目 + HMOS 项目），无 commit 信息也无具体功能锚点时使用本模式。**

## 核心方法论

三层并行：
1. **LLM 读源码还原 UI/行为**（主扫描，§M2.2）
2. **符号差集扫资源层**（仅资源层 name-as-identity 时允许，§M2.4）
3. **LLM 对比数据/逻辑层**（§M2.3）

无需模拟器/截图/视觉对齐。

**关键认知**：UI 层跨范式**不能用符号字面差集**（80% 假阳性），但可以用 LLM 并排阅读 iOS SwiftUI/UIKit/IB 与处理逻辑 与 HMOS `.ets` 的 `build()`，以"行为轨迹"维度对齐；资源层 name-as-identity，符号扫描高效；数据/逻辑层靠 LLM 读源码还原。三层互补。

## M2.1 建立页面配对（先做页面级索引）

```bash
IOS={ios_dir}; HMOS={hmos_project}

# iOS 页面单位：实际 App/Scene、路由/Tab/模态中的 SwiftUI 页面与 UIKit 控制器
# 源页面清单：读取本轮 Source 与已核对的原生页面/导航清单；不按文件后缀猜页面。

# HMOS 页面单位：page 文件（v2 @ComponentV2 struct，或 legacy @Entry/@Component）
# 三段式工程优先；空则回退 entry/ 单模块（兼容老项目）
HMOS_PAGES=$(find $HMOS/features/business_*/src/main/ets \
                  $HMOS/products/*/src/main/ets \
                  $HMOS/components/module_*/src/main/ets \
                  -name "*.ets" 2>/dev/null | sort)
[ -z "$HMOS_PAGES" ] && HMOS_PAGES=$(find $HMOS/entry/src/main/ets -name "*.ets" 2>/dev/null | sort)
echo "$HMOS_PAGES"
```

用 §4 架构映射表推导配对（原生子页常嵌入宿主 Tab/容器，不必 1:1）。**无法配对的 iOS 原生页面/子容器 = 候选新页面**，进 §S2 让用户确认。

## M2.2 UI + 行为层：LLM 源码并排阅读（**主扫描路径**）

> ⚠ 死代码过滤（必跑）：LLM 阅读源码时必须忽略注释、`@Deprecated`、`if(false)`、feature flag 关闭。详见 references/dead-code-filter.md

### 三步阅读

1. **iOS 源侧**：读 实际 SwiftUI/UIKit/IB + Swift/Objective-C 页面与实际 Storyboard/XIB，对每个交互入口追 `实际 Button/action 或 UIKit target-action/委托` → handler → store/service，形成行为轨迹 `{控件} → {触发} → {数据调用} → {UI 反馈}`
2. **HMOS 侧**：同样规则读 `.ets` 的 `build()` + `aboutToAppear` + `onClick` handler
3. **对齐**：两份轨迹逐条对比 → iOS 有 HMOS 无 = 🔴 / 入口在但 handler 缺步骤 = 🟠 / 完全对齐 = ✅

**严禁**仅比对 layout id 集合或 onClick 字面量集合（§1.1 已禁的符号差集方法）。**必须**阅读实际行为。

**必须补一步**：HMOS 行为轨迹后跑 §3.5 的 HMOS Spec 双重验证。

### M2.2.x 每条差异必带 5 个证据字段（硬性）

子代理产出每条 🔴/🟠 必须含：`ios_trace` / `hmos_read`（含行号 + 摘要） / `hmos_synonyms`（≥3 个同义关键词 + grep stdout） / `hmos_spec_status`（❌/✅/⚠） / `confidence`（high/medium/low）。

**缺任一字段 → 自动降级 `confidence: low`**，进 §S2"待验证桶"不直接进 🔴/🟠。

**主代理验收**：对每条 `confidence: high` 的 🔴 抽样 20% 复核——Read 对应 `hmos_read.file` 行范围 + 重跑 `hmos_synonyms` grep。复核不通过 → **全部 🔴 回炉重做**。

> 📖 详细操作（5 字段完整定义 / 子代理返回 yaml 完整样例 / 复核流程 / 完整输出示例）→ **references/m2-source-reading.md**

## M2.3 数据/逻辑层：LLM 读源码补齐

对关键业务模块（登录/支付/上传/作品/会员），LLM 读 iOS `*Repository` / `*Store` / `*UseCase` / `*Service`：

1. 提取每个公开方法的"输入 → 输出 → 副作用（网络/本地存储/事件）"
2. 在 HMOS `services/` / `store/` 找对应方法，对比输入/输出/副作用
3. 不一致进 §S2 清单（例：iOS 新增 `force: boolean` 参数，HMOS 没有）

## M2.4 资源层：符号差集（**本模式唯一允许的符号扫描**）

name-as-identity，符号扫描高效准确。

**四类差集**：
- (a) 图片资源（实际 Image/UIImage 引用、Asset Catalog 与其他已核实资源）
- (b) strings/xcstrings key（覆盖实际语言、复数与变体）
- (c) 实际源网络 endpoint（从本轮 API inventory 的真实请求方法和路径取候选）
- (d) 权限（真实权限调用、Info.plist/entitlements 与目标权限映射）

**HARD-GATE**：
- 每个差集命令的 stdout 必须在对话里以 code fence 出现
- 命令返回空 → 写"空结果"，不是跳过
- 命令报错 → 写 `SKIPPED(原因)`
- 差集结果**不等于**"一定要迁"——每条要 LLM 读上下文判断后进 §S2

> 📖 完整 grep/sed/comm 命令 → **references/resource-diff-commands.md**

→ 进 §S2 用户对齐。

原生增量输入：diff/关键词/文件列表只产候选；before/after 各自须绑定真实 Xcode target/Release 与相应 Source 条件视图，再按原模式读取完整相关行为。原 helper 未验证 Swift/Objective-C 支持时明确技术缺口，不把空扫描当无差异；不新增 baseline 验收或更改原用户对齐、判/真与回归状态合同。
