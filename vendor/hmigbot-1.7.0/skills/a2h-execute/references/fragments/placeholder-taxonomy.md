# placeholder-taxonomy — 占位分类法与 deferred_items 字段契约

## 6 类 kind（唯一合法占位；未登记 / 自由文本注释一律 FAIL）
| marker 形态 | kind |
|---|---|
| `// FWD-REF: <说明>` | forward-ref（符号待他人实现）/ resource-pending-asset（资源待产） |
| `// PLACEHOLDER: <说明>` | thirdparty-sdk（三方 SDK 无鸿蒙对等物） |
| 已登记的 `// TODO: <说明>` | forward-ref-uncertain（能否兑现不确定；环境/签名/权益类待办也归此，`resolve_by=closeout`） |
| 资源文件内 `[TODO: translate]` | resource-pending-translation |
| `// HANDOFF: owner=<谁> what=<做什么> verify=<断言>` | handoff（责任移交） |

没有别的 kind：`env-pending`、`forward-ref-resolved` 之类一律拒收。已兑现的 forward-ref 不进 deferred_items，写顶层 `resolved_refs[]`（台账 ID 或 `file#anchor`），脚本据此把台账 registered→resolved。

## deferred_items 字段契约（脚本机械校验，缺一整批拒收）
| 字段 | 必填 | 形态 |
|---|---|---|
| `kind` | 必填 | 上表 6 值之一，逐字 |
| `location` | 必填 | `"entry/.../X.ets#anchor"` 或 `{file, anchor}`：桩所在的文件（你白名单内、已写出）# 桩所在的函数/成员/struct 名 |
| `trigger` | forward-ref / forward-ref-uncertain 可省；handoff 与外部条件型必填 | forward-ref 系**不必写判据**：脚本登记时在 location 锚点上方插入 `// FWD-REF(<ID>)` 并生成桩位判据（stub-cleared），你写的判据只作接线参考；**handoff 必写断言**——交接对象做完时全工程应成立的事实（`grep`：必须出现的调用 / 渲染，如 `GuideStatusPage\(`；或 `artifact` / `slice` / `symbol-implemented`），登记时脚本自检正则（能编译、能命中自身字面形态，多一层转义自动去掉）；外部条件（`sdk-available` / `decision-chosen` / `api-online` / `resource-ready`）照写 `{"type","arg"}` |
| `resolve_by` | forward-ref / forward-ref-uncertain 必填；handoff 可省（缺省 wiring） | 只写波名：`infra` / `domains` / `auditfix` / `wiring` / `closeout`；说明放 `note` |
| `side_effects` | thirdparty-sdk 必填 | `"none"`（纯 SDK 可整体桩）或副作用描述数组；非 none 时同 location 必须另有一条 forward-ref 承载副作用（V9；整块桩掉会让依赖初始化从不发出） |
| `note` | 可选 | 自由文本；所有散文只能放这里 |

trigger.type 8 类与 arg：`symbol-implemented`（`file#symbol`，最常用）/ `sdk-available`（oh 包名如 `@cashier_alipay/cashiersdk`）/ `decision-chosen`（PD-ID）/ `api-online`（接口路径）/ `resource-ready`（资源名）/ `grep`（正则）/ `artifact`（`文件#字段`）/ `slice`（域 key）。

合法样例（SDK 桩 + 配对副作用 + 移交）：
```json
"deferred_items": [
  {"kind": "thirdparty-sdk", "location": "entry/src/main/ets/components/infra-push/PushSdk.ets#init",
   "trigger": {"type": "sdk-available", "arg": "@hw-agconnect/push"}, "side_effects": ["上报 token"]},
  {"kind": "forward-ref", "location": "entry/src/main/ets/components/infra-push/PushSdk.ets#init",
   "resolve_by": "wiring", "note": "等 app-mine 的 UserApi.bindPush（安卓 UserApi.bindPush）"},
  {"kind": "handoff", "location": "entry/src/main/ets/pages/SplashPage.ets#initUser",
   "trigger": {"type": "grep", "arg": "AppConstant\\.setVipProvider\\("},
   "note": "owner=app-vip-function-intercept：宿主须调用 AppConstant.setVipProvider"}
],
"resolved_refs": ["P-DOM-AH-003", "entry/src/main/ets/components/app-home/HomeBridges.ets#openVip"]
```

- 代理只申报不登记：ID 由脚本分配（registered→pending→due→fired→resolved | deferred）。
- **桩位标记与兑现（E244）**：forward-ref 系登记后，脚本在锚点上方插入 `// FWD-REF(<ID>)`，那一行归脚本管，别手改别人的；同时从桩位代码里记下还没落盘的跨文件引用。
  · 桩位已按契约名调用（提供方文件在、方法还没落，或同波别的任务稍后落）：提供方落盘后脚本自动销账、删标记，**你不用再改**；
  · 桩位是空实现 / 本地占位：兑现时把它改成真实调用，并在回执顶层 `resolved_refs[]` 逐字写任务书列出的 ID——脚本核实桩位引用全部已落盘、不是空实现、代码与登记时不同后才销账；
  · 只删标记、只改注释、或改成调用一个还没落盘的符号，都不算兑现（脚本拒）。
- 散文式 defer（"待接入后替换"、"由 xxx 负责"的裸注释）= FAIL；合法延期只有 deferred 项的 `defer` 审批通道。

## HANDOFF 三型机械断言（`verify=` 必填；缺失 = FAIL `ledger-handoff-no-assertion`）
| 断言 | 语义 / 用途 |
|---|---|
| `grep:<正则>` | 全工程 .ets 必须存在匹配（marker 行自身不计）——启动期初始化、跨文件调用点 |
| `artifact:<文件>#<字段>` | 产物存在且该字段非空/非零——委托别的 skill 自愈 |
| `slice:<N>` | 归属切片；切片终态仍未兑现 → GAP(FAIL)——业务接线（等价 FWD-REF） |

成立 → INFO；不成立 → FAIL（`ledger-handoff-unmet`）。pipeline 末尾 verify_handoffs 机械对账（含按 trigger 自动置 resolved）；散文注释各道门全放行、真机才暴露。

## evidence 契约（完成申报的唯一凭据）
- 合法：`文件路径:行号`（`entry/.../Episode.ets:42`）/ spec anchor（`features/F001.md#audio-acceptance`）/ 二者组合。
- 非法：空 / `-` / `N/A` / "已完成" / "编译通过" / 纯描述文字（"按 spec 实现"）。
- 接线专项：evidence 必须指向调用方（如 `pages/X.ets:48 import` + `:81 new XVM()`）；禁用 VM/Repository 自身行号充数（VM 存在 ≠ 被接上）；schema 级校验 `evidence.file == consumer_page`。

<!-- source: a2h-execute/references/agent-prompts/_common.md:L9-62 + a2h-execute/SKILL.md:L480-486 + docs/skills_optimization_818/design/2_contracts.md §2.3；V21 字段契约表 + 样例：aippt_new_v5 复盘（396/506 拒收） -->
