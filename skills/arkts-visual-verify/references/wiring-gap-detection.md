# 组装根未接线检测（wiring gap）

> **一句话**：多个页面因同一个「XX 未配置 / 未就绪 / 暂不可用」根因被判 blocked 时，**先查该配置的注入入口有没有调用点**。零调用点 = 实现缺口（P0），不是上游阻塞（noop）。

## 0. 为什么需要这道闸（真实事故，2026-08-21 AIPPT）

迁移产物里 `ApplicationCompositionRoot.installApiClient(client)` 定义齐全、下游
`configure()/isConfigured()/assertRuntimeReady()` 守卫链完整、注释写着
`absent ports remain fail-closed`——**但全工程零调用点，也从未 `new ApiClient(...)`**。
后果：`AuthApi.client` 恒 null → 登录必抛「认证网络尚未配置」→ token 恒空 →
「我的」页几乎所有入口落 `unavailable` Toast，模板页报「认证网络未配置」。

这个空壳**骗过了所有既有闸**：编译过（语法完整）、占位符扫描过（`fail-closed` 注释不是
登记占位符）、页面状态审计过（.ets 文件都存在）、功能验收过（账本自洽）。
visual-verify 也把现象报出来了，但按"上游未就绪"判成 `pending_upstream_fix / noop`，
**没有捅到"这压根是实现漏了最后一颗螺丝"**。

失效本质：**把「策略约束」误当成「免除接线义务」**。
- ledger D-022「认证/支付 fail-closed 并可重试」= 失败时不许假装成功（**错误处理策略**）
- ledger D-023「开发联调沿用 `http://dev-api.whiap.cn`」= **已批准装配**，host 也确实写在
  `ApiEndpointRegistry.MAIN_BASE_URL` 里
- 两者都不等于"不要装 ApiClient"。骨架越规范、注释越自洽，越容易被当成有意设计放过。

## 1. 触发条件（命中任一即跑本判据）

- 跨 batch 聚类发现 **≥2 页共享同一「未配置/未就绪/unavailable」根因**
- 页面本体存在（.ets 在、Builder 注册了）**但功能入口成片失效**
- 错误文案统一（同一个 `$r('app.string.xxx_unavailable')` / 同一句 throw message）
- 单据里出现 `pending_upstream_fix`、`suggested_fix_owner: noop`、
  `not_migration_evidence: "等后端/等 provider"` 这类措辞

## 2. 三步机械判据（纯 grep，零模型判断）

```bash
# ① 从错误信息反查守卫函数
grep -rn "认证网络尚未配置\|<你看到的错误文案>" entry/src/main/ets --include="*.ets"
#    → 定位到守卫，如 AuthService.assertRuntimeReady()

# ② 找守卫依赖的开关字段 / 判据函数
grep -rn -A6 "assertRuntimeReady\|isConfigured()\|isXxxApproved()" <守卫所在文件>
#    → 得到开关，如 AuthApi.isConfigured() → client !== null
#                   DeviceIdentityService.backendMappingApproved

# ③ 数装配入口的调用点（关键：排除定义处自身）
grep -rn "installApiClient\|approveBackendMapping\|\.configure(" entry/src/main/ets --include="*.ets" \
  | grep -v "static installApiClient\|installApiClient(client\|approveBackendMapping(): void\|configure(client"
grep -rn "new ApiClient" entry/src/main/ets --include="*.ets"
```

## 3. 判定表

| ③ 的结果 | 定性 | 出单方式 |
|---|---|---|
| **调用点 = 0**（含从未 `new` 过实现类） | **实现缺口**（组装根未接线） | `kind=IMPL_MISSING`、`severity=P0`、`is_migration_bug=true`、`layer=feat`、`suggested_fix_owner=fixer`；**禁止 `noop`/`pending_upstream_fix`** |
| 调用点存在，但运行期条件不满足（等后端返回 / 等真实订单 / provider 未上线） | 真上游阻塞 | 维持 `blocked` + `noop` 合法，但 `not_migration_evidence` 必须写明**调用点在哪一行**，证明接线已完成 |
| 调用点存在但在死分支里（if(false)、被注释、未被启动链引用） | 视同调用点 = 0 | 同第一行 |

> **硬约束**：标 `noop` / `pending_upstream_fix` 前必须跑完 ③ 并把计数写进单据的
> `not_migration_evidence`。**没跑过判据就标 noop = 假阴性**，视同 [`context-discipline.md`](context-discipline.md)
> 里"缺页无人认领"同级事故。

## 4. 出单要点

一个组装缺口通常喂多个下游（本例 `installApiClient` 一处喂了 Auth/Outline/Payment/
PptGeneration/FreeCount/TemplateCatalog 六个 service），因此：

- **只出一张 SYSTEMIC 根因单**，把受影响页面全部挂进 `affects[]`，不要每页各出一张 P0
- 单据 §2 期望写清"**装配点应在哪**"（启动链：EntryAbility → CompositionRoot →
  privacyAccepted/sessionStable 等），而不是只写"网络不通"
- 受影响的页面单保持 blocked 占位，`systemic_root` 指向该根因单

## 5. 泛化：不只是 ApiClient

任何**"定义了装配入口但没人调用"**的模式都适用，常见形态：

- `configure(x)` / `install*(x)` / `attach*(x)` / `register*(x)` 定义了没调用方
- 单例 `shared()` 里的 `private client: X | null = null` 永远为 null
- `approve*()` / `enable*()` 开关字段初值 false 且无 setter 调用
- Provider/Registry 注册表为空却被当成"provider 不可用"
