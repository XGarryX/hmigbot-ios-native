# 迁移决策类目 (C0–C17)

> 经验层 checklist —— 跨项目稳定的抽象决策类目。
> grill-with-docs 在 a2h-spec / a2h-plan 内嵌时，以本文件为 lens 逐类目核验本项目 spec。
> **本文件不收录任何项目专有名词**（如 "PPTX 渲染"、"彩铃"）—— 项目实例只活在 `spec/decision-ledger.md`。
> **同理不写业务域名词**（登录 / 支付 / 直播…）：条件化推荐一律写成「**检出信号**」（如"检出跨端字节级契约时"）。本文件对所有项目**始终加载**，写死某业务域会把该域概念灌进相邻类目。
> **且每个 🔴 类目必须自带中性 candidates** —— 候选真空会被上下文里最显著的概念填满（实证：C2 曾无 candidates，被相邻类目的域名词灌成与项目无关的选项）。**连负面示例也别逐字写**——把不该生成的串写进本文件，同样抬高其显著度。
>
> 类目演进：retrospect 阶段评审 escape，**同一 escape 在 ≥2 个项目复现 → 升级为新 C 类目**。

---

## 使用约定

| 标签 | 含义 |
|------|------|
| 🔴 必问用户 | 业务/范围/策略，源码和文档都给不出 |
| 🔵 文档自答 | grill-with-docs 查 HarmonyOS 文档可定，无需用户 |
| 🟡 源码缩窄 | 先扫源码把开放问题变 yes/no 或直接消解 |
| ⚙️ pipeline 默认 | 固定 policy，不 grill |

grill 流程：
1. 加载本 checklist + 项目自动提取事实
2. 逐类目在本项目 spec 找实例 → 实例存在但不清晰 = grill 点
3. 反向扫 spec 不清晰信号 → 归不到任何类目 = escape，标新类目候选

---

## 根决策

### C0 产出定位（决策树根）🔴
**何时拷问**：spec 阶段最先问，决定全局真桩切分尺度。
**candidates**：真机 Demo / MVP / 可上线产品 / 完整复刻。
**默认推荐**：**检出跨端字节级契约**（签名 / 加密 / 身份常量等必须逐字节忠实复现的约定）时，优先 **完整复刻** —— 产出定位决定这类契约能否字节级复刻，降档等于授权走捷径（占位签名、跳过常量真值），契约必断。降档到 Demo / MVP **需用户显式确认"接受契约不保真"**，不得默认降档。（复盘理由见 `android-api-inventory` 的数据链路契约模板）
**联动**：本类目结论是 C5 / C8 / C12 的判定基准。
**ledger 字段建议**：D0 单独成段，作为后续 D-编号决策的依据根。

---

## 范围

### C1 初始 vs 增量 🟢→🔴
- 🟢 自动：`spec/baseline/` 是否存在（a2h-spec 路由已判）
- 🔴 增量时：是 "只生成 spec" 还是 "实现到底"

### C2 迁移范围取舍 🔴
**candidates**：全量 / 仅 P0 高优先级 / V1 核心 + V2 增量 / 按模块垂直切片。
**候选只给"切法"、不预设任何具体模块**——切片边界取自本项目 `feature-index.md`。
**何时拷问**：C0 之后，划定本轮做多少；与 tier（core / standard / peripheral）分档联动。

### C3 目标平台 🔴
- HarmonyOS API version（必问）
- 设备形态（手机/平板/折叠屏/车机）—— 🟡 可通过 Android 资源限定符（`layout-sw600dp` / `leanback`）探测应用**已支持**的形态来缩窄

### C4 横切能力是否本轮迁移 🟡
i18n / 深色 / 大字体 / 无障碍 —— 同一类"能力是否在范围内"。
🟡 缩窄机制：Android 侧能力存在性自动探测（`values-night/` 不存在 → 深色模式自动消解）。

### C5 dead code / 已注释 / 清单外特殊页是否迁移 🟢→🔴
- 🟢 自动：扫源码识别已注释功能、未被引用的页面、伪装页
- 🔴 逐项确认：迁移 / 砍 / 退化保留

---

## 重大架构决策（Gate A 级）

### C6 平台无对等能力时的替代方案 🔵→🔴
**何时触发**：grill 探测到本项目存在 HarmonyOS 无对等 API/库 的功能时。
**流程**（用户预知两阶段 → 本地 skill → 公开文档 → 业务决策）：阶段一 spec Step 3.0c 收集 `spec/ref/hmos-references.md`（可选，跳过不阻断）→ 阶段二 plan grill #2 Step 0 对 Android API 清单逐项先查该文件、未覆盖项批量追问用户 → 残余项查 `harmonyos-development` skill（适用域：相机/图片/ArkUI，命中率高）→ 降级 grill-with-docs 查公开文档 → 都找不到 🔴 进入"替代方案"决策（系统组件 / 自绘 / 服务端渲染）。完整子流程见 `../../a2h-plan/references/grill-2-decision-gates.md` §7.2d。
**联动**：替代方案可能反向改变 UI 形态，需追问 UX 是否可接受。

### C7 一锤定全局的架构选型 🔴
**Gate A 级**：媒体方案、加密/鉴权 passthrough、状态管理总线、网络层基座等一旦定了影响整个架构的选型。
**特征**：单次决策成本低，但落地后回滚成本极高。优先级高于普通 policy。

### C8 三方依赖无鸿蒙等价物时的策略 🔵→🔴
**流程**：同 C6 两阶段用户预知——依赖清单 🟢 自动从 `build.gradle` + api-inventory 提取（带版本号、用途）→ 先查 hmos-references.md、未覆盖项批量追问（鸿蒙版本 / 迁移文档 / 内部镜像 / 合作方未公开版本）→ 残余文档查询（注意：`harmonyos-development` 主要覆盖系统能力侧，三方 SDK 命中率低，多数直接 grill-with-docs）→ 都找不到 🔴 走"占位 / 降级 / 砍 / 换"。完整子流程见 `../../a2h-plan/references/grill-2-decision-gates.md` §7.2d。
**子类提醒**：埋点/分析、推送 SDK 的"全 App 留桩"影响面比普通库大，需单独确认。

---

## 行为差异

### C9 平台行为差异导致的 UX 退化 🔴
**典型触发**：系统选择器 vs 应用内浏览、权限引导弹窗移除、原生组件外观差异。
逐项确认是否接受退化形态。

### C10 后台执行 / 长任务行为差异 🔵→🔴
**典型触发**：长轮询、后台播放、锁屏行为、协程 vs setTimeout 差异。
🔵 先查文档定基线方案，🔴 端到端语义保留度由用户拍板。

### C11 失败降级 / 兜底策略 🔵
渲染失败、API 失败、网络断开等的兜底链。多由文档可定，但 grill 仍需明确"是否实现"。

### C12 忠实复刻 vs 修正原版缺陷 🔴
**典型场景**：原 App 的 bug、欺骗性 UX、过度收敛优化。是否借迁移借机修正。
受 C0 制约（Demo 通常忠实，上线产品倾向修正）。

---

## 工程配置

### C13 签名 / entitlement / AGC / 证书 🔴
HMS Kit、华为账号、签名 Profile 的责任人与时点（不是技术决策，是协作排期决策）。

### C14 密钥 / AppSecret 安全策略 🔴
端侧硬编码 vs 服务端代签 vs 混淆。

---

## 数据

### C15 后端复用 vs 重建；多环境选择 🟢→🟡
- 🟢 自动：api-inventory 已提取 base_urls + 环境
- 🟡 仅当探测到多 base_url（dev/test/prod）时问环境选择，单环境时不问

### C16 持久化键 / 数据迁移范围 🔴
SharedPreferences / MMKV 键的迁移范围取舍标准（核心 vs 全量）；老用户数据迁移是否考虑。

### C17 API 契约与数据逻辑不确定项 🟡→🔴/②
**输入**：`api-inventory.json` 的 `uncertainties[]`（android-api-inventory v1.3 产出；已按 🟡 源码缩窄——① 源码可定项模型已自答不入清单，清单只含 ② 需真包 / ③ 策略待确认两类，且带 `chain` 链路归属与 `impact` 影响面）。
**流程**（两阶段用户预知，同 C6/C8 范式）：阶段一 spec Step 3.0c2 收集 `spec/ref/backend-facts.md`（后端接口文档 / Postman / 响应壳约定 / 业务码与 token 失效码 / 必填字段与 enum）→ api-inventory Phase 3 预销账（命中项建为 `answered`）→ 阶段二 plan grill #2 Step 0 对残余 `open` 项**按链路打包呈现**（auth/登录链路置顶）：**③ 项逐条 🔴 拷问**定策略写 D 编号；**② 项批量索取证据**（后端文档 / 抓包样本 / Postman / 后端同事可确认），索到写 ledger 事实段 + 销账，索不到标 `needs_capture` —— 由 `arkts-network-troubleshoot` Phase 0.3 定向抓包销账、Phase 1.7 DIFF 实证回写。完整子流程见 `../../a2h-plan/references/grill-2-decision-gates.md` §7.2d。
**分级铁律**：① 不问（模型自答）；② 先索证、索不到标记待验，**不逐字段轰炸用户**；③ 必问。
**联动**：本类目答案是 execute 阶段 `arkts-network-troubleshoot` 决策清单「第 0 步 ledger 预填」的直接来源；登录/鉴权链路（`auth_model` 的 `unknown` 字段）优先收口。

---

## 旁路（不进 grill）

以下内容历史上曾被纳入 checklist，已剔除。它们由 pipeline 旁路处理：

**旁路 ① 确定性自动提取**：页面/功能/依赖/权限清单、图标格式、变体目录、API 端点+base_url、module 结构、stub anchor、复杂容器映射、共享组件边界。
→ 由 a2h-spec Phase A/B/C 与 android-api-inventory 自动产出，填 ledger「事实」段。

**旁路 ②a 确定性技术修复**：明文流量 cleartext 白名单、MISSING_xxx 占位、废弃 API 替换。
→ 写入 ledger「技术必做项」段，非决策。

**旁路 ②b pipeline 运行策略默认**：HARD_LIMIT、骨架审计 FAIL 动作、CHECK-6 工具缺失、回环上限、编译轮数。
→ pipeline 默认配置，不 grill。

**例行技术映射**：导航模型、状态管理、列表渲染、持久化映射。
→ 由 domain skill + 文档自动处理，只有上升为项目级架构决策时才落入 C7。

---

## spec 卫生前置闸（grill 之前的确定性检查）

不是 grill 题目，是 grill 之前的**确定性交叉比对**——检查项 + 检测手段表见 `grill-1-decision-gates.md` §C4.7。结论写入 ledger 的 `spec 卫生检查结论` 段。

---

## 类目演进规则

retrospect 阶段：
1. 收集 execute/verify 逃逸的「决策缺口」+ grill 的「escape 新类目候选」
2. 按 escape 主题归并
3. 同一 escape 主题在 **≥2 个项目**重复出现 → 升级为新 C 类目，追加到本文件
4. 否则保留在各项目 ledger 当项目特例

**永不收录"实例"**：项目专有名词永远不进本文件。
