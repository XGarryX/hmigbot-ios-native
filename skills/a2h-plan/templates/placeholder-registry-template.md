# 占位符注册表

## 统计
- 总数: 0
- registered: 0
- pending: 0
- due: 0
- fired: 0
- resolved: 0
- deferred: 0

## Schema 说明

每个占位符 6 个字段：前 4 个为核心字段（既有读取方按列名 / 前 4 列向后兼容），后 2 个为「延迟 / 待接工作分类法」新增列，**追加在表末尾**。

| 字段 | 必填 | 说明 |
|------|------|------|
| `P-ID` | 是 | 占位编号。命名空间：<br>- `P-S{SliceN}-{序号}`：Slice 产生（含 forward-ref / forward-ref-uncertain）<br>- `P-B{BaseN}-{序号}`：Base 层产生（forward-ref）<br>- `P-RES-TRANS-{序号}`：资源翻译（resource-pending-translation）<br>- `P-RES-ASSET-{序号}`：资源资产（resource-pending-asset）<br>- `P-CB-L3-{序号}`：arkts-component-builder L3 签名占位（forward-ref，子类）<br>例：`P-S3-001`、`P-B6-002`、`P-RES-TRANS-001`。 |
| `location` | 是 | 占位代码落地位置。**必须**是文件路径（可附行号或锚定符）。例：`entry/src/main/ets/pages/PartFivePage.ets:128`、`entry/src/main/ets/repositories/PaymentRepository.ets#processPayment`。 |
| `trigger_condition` | 是 | **可机器校验的**唤起条件（见下方白/黑名单）。 |
| `status` | 是 | 状态枚举:`registered` / `pending` / `due` / `fired` / `resolved` / `deferred`。 |
| `kind` | 是 | 占位类别（6 类枚举，详见下方"kind 枚举详解"）：<br>① `thirdparty-sdk`（三方 SDK 无鸿蒙等价物）<br>② `forward-ref`（前向引用代码桩）<br>③ `resource-pending-translation`（多语言翻译待补）<br>④ `resource-pending-asset`（资源资产待补）<br>⑤ `forward-ref-uncertain`（converter 转换期自判的不确定区域）<br>⑥ `handoff`（**责任移交**：代码结构完整但需别处兑现） |
| `resolve_by` | forward-ref / forward-ref-uncertain 必填 | 前向引用归属，格式 `Slice {N} Step {3c\|3d}` 或 `Slice {N} Step 3a`（uncertain 由生产 converter Slice 接线）。`kind=thirdparty-sdk` / `resource-pending-*` 时留空（用 `trigger_condition` 表达条件）。 |

### kind 枚举详解（6 类）

| kind | 适用场景 | location 格式 | trigger_condition 模板 | 产生方 |
|------|---------|--------------|----------------------|-------|
| `thirdparty-sdk` | 三方 SDK **没有对应的 HMOS 适配 skill**（skill-binding-rules.md 未命中，如自研 / 小众 / 埋点等）；已有 skill 的 SDK 直接走 task `suggested_skills` 路径、**已有 decision-ledger approved 原生/自建替代决策的归 owned task**（Step 4.1 判据 0）——两者都不进本表 | `entry/src/main/ets/<file>#<symbol>` | `<业务类别> SDK 入仓` / `<api> 上线` 等白名单 | plan 阶段直写（Step 4.1 SDK 决策树未命中项） |
| `forward-ref` | 早阶段代码桩（converter UI 钩子 / Base signature / 跨切片 handler） | `entry/src/main/ets/<file>#<symbol>` | `Slice {N} Step {3c\|3d}` | a2h-execute converter / Base worker 执行期自登记 |
| `resource-pending-translation` | 多语言资源 value 含 `[TODO: translate]` 前缀 | `entry/src/main/resources/<locale>/element/<file>.json:<key>` | `<locale> 翻译就绪`（脚本检测：`grep '\[TODO: translate\]' resources/<locale>/element/*.json` → 0 hits） | ios-resources-convert 在生成 fallback 翻译时自登记 |
| `resource-pending-asset` | 媒体资源用 fallback（如 `ic_default_avatar` / `ic_placeholder` / `default_thumb` 等占位资产） | `entry/src/main/ets/<file>#<usage>` 或 `entry/src/main/resources/base/media/<asset-id>` | `<resource-id> 就绪`（复用既有：`grep "<resource-id>" entry/src/main/resources/` 命中即视为真实资产已替换 fallback） | a2h-ios-converter / Base worker 用 fallback 资产时自登记 |
| `forward-ref-uncertain` | converter 转换期自判的不确定动态值 / 不确定区域（几何近似 / 动态值运行时才知）| `entry/src/main/ets/pages/<page>.ets:<line>` | `Slice {N} Step 3a 确认`（由 Stage 3 Slice Step 3a 二次审视时人工确认或升级） | a2h-ios-converter 转换时自判自登记 |
| `handoff` | **代码结构完整、编译通过，但要靠别处才算真正完成**：① 委托另一个 skill（"尺寸交 icon-sizing 自愈"）② 依赖别处的调用点（"由启动序列调 setDebug()"）。marker `// HANDOFF: owner=… what=… verify=…` | `entry/src/main/ets/<file>:<line>` | 由 marker 的 `verify=` 断言表达：`grep:<正则>` / `artifact:<文件>#<字段>` / `slice:<N>` | converter / Base worker 在写下"交给 X 处理"这类注释时**同步**登记 |

> **kind 选择决策树**：
> - 是不是资源文件（resources/<locale>/element/*.json）？ → `resource-pending-translation`
> - 是不是 fallback 资产引用？ → `resource-pending-asset`
> - 是不是三方 SDK 缺失？ → `thirdparty-sdk`
> - 是不是转换期自判的不确定区域？ → `forward-ref-uncertain`
> - 其余跨阶段代码桩 → `forward-ref`

### status 状态机

```
registered → pending → due → fired → resolved
                    ↘
                      deferred（用户显式延期，需附理由）
```

- `registered`：plan 阶段直写（Step 4.1）或执行期铸号登记，代码尚未落地
- `pending`：代码已落地占位，trigger_condition 未满足，等待唤起
- `due`：trigger_condition 自动检测命中，需要回填真实实现
- `fired`：已通知 owner（或日志告警已抛出），等待回填
- `resolved`：真实代码已回填且编译/验证通过
- `deferred`：经过用户审批延期到下一里程碑（必须含 `defer_until` + 理由）

### trigger_condition 白名单（合法格式）

trigger_condition 必须能被脚本机器解析。支持以下 8 类格式：

| 格式 | 适用 kind | 语义 | 检测方式 |
|------|----------|------|---------|
| `D-{N} chosen` | thirdparty-sdk / forward-ref | Decision Card 已选定 | `grep "D-{N}.*chosen" spec/migration-decisions.md` |
| `<path> 实现 <symbol>` | thirdparty-sdk / forward-ref | 指定文件实现指定符号 | `grep -n "<symbol>" {path}` |
| `<业务类别> SDK 入仓` | thirdparty-sdk | 指定业务类别的三方 SDK 适配方案已就位（可能是：新 skill 入仓 / 私仓 har 包入仓 / 官方 SDK 适配文档发布 / 团队内部决策完成等） | 不强依赖 skill 命名约定，多形式满足：<br>① `test -d arkts-skills/skills/<new-skill-name>`（新 skill 入仓）<br>② `test -f oh_modules/<sdk-package>/...`（私仓 har 入仓）<br>③ grep 决策记录文档命中（团队决策） |
| `<api-endpoint> 上线` | thirdparty-sdk | API 路由已加入网络层 | `grep "<api-endpoint>" entry/src/main/ets/network/` |
| `<resource-id> 就绪` | forward-ref / resource-pending-asset | 资源已就绪（也覆盖 fallback 资产被真实资产替换的场景） | `grep "<resource-id>" entry/src/main/resources/` |
| `Slice {N} Step {3c\|3d}` | forward-ref | 前向引用待接线工作的归属 Slice/Step | `location` 文件无 `// FWD-REF:` marker 且真实实现存在 → `resolved` |
| `Slice {N} Step 3a 确认` | forward-ref-uncertain | Slice 阶段二次审视确认或升级实现 | Slice 3a worker 报告 `uncertain_regions_resolved[]` 含本 P-ID |
| `<locale> 翻译就绪` | resource-pending-translation | 指定 locale 全部翻译完成 | `grep '\[TODO: translate\]' resources/<locale>/element/*.json` 返 0 hits |

### trigger_condition 黑名单（**禁止**使用）

以下模糊措辞**一律禁止**作为 trigger_condition，converter / hard-gate 将直接 FAIL：

- `等真机接入` / `等设备就绪` / `真机联调时`
- `等 SDK 决策` / `SDK 接入后` / `待 SDK 到位`
- `联调时补` / `联调后再说` / `联调阶段处理`
- `上线前补` / `上线前再确认` / `上线时补`
- `后续` / `稍后` / `暂时` / `先这样` / `回头再说`

判定脚本（伪代码）：**白名单优先短路**——命中上方 8 类白名单格式的 trigger 直接 PASS，豁免黑名单；黑名单用**模糊短语**匹配（不用裸词 `SDK`/`真机`，否则会误杀合法白名单形 `<业务类别> SDK 入仓`、`<resource-id> 就绪` 等——这类含 `SDK`/整词但语义合规）。
```python
if matches_any_whitelist(trigger_condition):     # 白名单 8 类格式命中 → 合法，短路
    return PASS
BLOCKLIST_PHRASES = ["等真机", "真机联调", "等设备就绪", "等 SDK", "SDK 接入后",
                     "待 SDK", "联调时", "联调后", "联调阶段", "上线前", "上线时补",
                     "后续", "稍后", "暂时", "先这样", "回头"]
if any(p in trigger_condition for p in BLOCKLIST_PHRASES):
    return FAIL("trigger_condition 含模糊延期措辞，必须改为可机器校验的具体条件")
```

## 注册表

> `kind` / `resolve_by` 为新增列，追加在表末尾；既有读取方（如 a2h-verify CHECK-3）按列名 / 前 4 列读取，向后兼容。

| P-ID | location | trigger_condition | status | kind | resolve_by |
|------|----------|-------------------|--------|------|------------|

## 延期记录（仅 status=deferred 时填写）

| P-ID | defer_until | reason | approved_by |
|------|-------------|--------|-------------|


---

## 写入规则（registry = 唯一写入位 + 唯一合法性来源）

**plan 期直写（a2h-plan Step 4.1）**：plan 阶段识别的占位（thirdparty-sdk 决策树未命中项等）**直接 append 本表**（status=registered），不经 coverage-matrix 中转、slice 文件不持有占位内容；§7 校验（trigger 白名单 / 格式 / resolve_by）直接对本表跑。

**执行期铸号**：全部铸号者（converter / worker / closer / repair）遵守 execute `_common.md` §2.1c 发号协议——写代码 marker **之前**先 append 本表行（**登记即占号**），瞬时 forward-ref 同样登记（检测器 Class 1 契约：marker 的 P-ID 不在本表即 FAIL）。

**resolved 即清行（防膨胀）**：group-closer 收组时把本组已 resolved 的 P-ID 记入 writeback manifest `registry.resolve`，由 `apply_writeback.py` **删除** `kind=forward-ref` 行（历史记录在组 brief 小节）；lifecycle 类（`thirdparty-sdk` / `resource-pending-*` / `forward-ref-uncertain` / `deferred`）resolved 后**保留**（V2 解锁与审计需要）。删行安全性：若 marker 仍残留，dangling-fwd-ref Class 1（unregistered）照常 FAIL 兜底。本表稳态 ≈ 当前活债 + lifecycle 条目。

**单元格限长**：`trigger_condition` / `status` 等单元格 ≤120 字符；resolve 过程叙事写 brief，不塞表格。

**不同 kind 的产生时机**：
- `thirdparty-sdk` → plan 阶段直写（Step 4.1 SDK 决策树未命中项）
- `forward-ref` / `forward-ref-uncertain` → a2h-execute converter / worker 执行期铸号（写 marker 前登记）
- `resource-pending-translation` → ios-resources-convert 生成 fallback 翻译时自登记（Stage 0）
- `resource-pending-asset` → a2h-ios-converter 用 fallback 资产时自登记

**行 schema 示例**：

| P-ID | location | trigger_condition | status | kind | resolve_by |
|------|----------|-------------------|--------|------|------------|
| P-S2-001 | entry/src/main/ets/services/EventTrackService.ets#initVolcEngine | 火山引擎 AppLog HMOS 等价 SDK 入仓 | registered | thirdparty-sdk | |
| P-S6-001 | entry/src/main/ets/services/LoginService.ets#aliOneClickLogin | 阿里一键登录 HMOS 等价 SDK 入仓 | registered | thirdparty-sdk | |
| P-RES-TRANS-001 | entry/src/main/resources/zh_CN/element/string.json:home_feed | zh_CN 翻译就绪 | registered | resource-pending-translation | |
| P-RES-ASSET-001 | entry/src/main/ets/components/Avatar.ets#defaultAvatar | ic_user_avatar 就绪 | registered | resource-pending-asset | |
| P-S3-UNC-001 | entry/src/main/ets/pages/SearchPage.ets:128 | Slice 3 Step 3a 确认 | registered | forward-ref-uncertain | Slice 3 Step 3a |

**路径**：`spec/placeholder-registry.md`（在 `spec/` 根目录，与既有惯例对齐，不在 `spec/baseline/plans/` 下）

**校验**（a2h-plan §7 对本表直接跑）：全部条目 trigger 白名单命中、P-ID 格式合法、`kind ∈ {forward-ref, forward-ref-uncertain}` 含 `resolve_by`，任一不达标 plan FAIL。
