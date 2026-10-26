<!--
android-api-inventory 的数据链路契约模板。由 Phase 2.8「数据链路契约生成」消费。
本文件是"模板"（通用骨架 + auth 首个 profile + 实例填写区）。
生成产物 = spec/baseline/api-inventory/data-chains/chain-<name>.md（首个 chain-auth.md）。
实例的 API 层投影自 api-inventory.json 的 auth_model（含轴 A/B/C 分类字段），非 API 层（L1 隐私/L0 应用身份）交叉核 feature-index owner。
-->

# 数据链路契约模板（chain-contract-template）

## 一、这是什么（先读）

**数据链路契约（data-chain contract）** = 一条横切数据链路（登录 / 支付 / 推送…）的"逐层装配图"：每层**点名 owner + 标捕获/接线状态 + 给打通信号 + 定 probe 靶子**。它是对 `api-inventory.json` 里 `data_flows[].chain` 的**可执行 + 可验证 + 点名 owner** 投影，也是对抗 feature 分解漏层的**正交完整性兜底**。

**两层结构**：
- **模板（本文件，链路无关骨架 + 各链路 profile）** —— 放 `android-api-inventory`。
- **实例（`data-chains/chain-<name>.md`，本项目填好）** —— spec 期生成，auth 首个（`chain-auth.md`），未来 `chain-pay.md` 等复用同骨架。

**单一源护栏（务必遵守）**：
1. **API 层是投影，不是第二份捕获** —— L0(base_url)/L2/L3/L4/L5/L6 的事实取自 `api-inventory.json` 的 `auth_model`（加轴分类字段），**不在本契约里重新捕获**，否则造互斥事实（xiaoyibang 模式 F）。
2. **非 API 层去 feature-index 交叉核** —— L1 隐私、L0 应用身份等不是 API、`auth_model` 里没有，本契约**去 feature-index + 源码交叉核 owner**（补 api-inventory 的 L1 盲区）。这是"新事实"，不违反护栏 1。
3. **不抄鸿蒙实现细节** —— 每层只给"实现 skill 指针"，具体怎么写留在 `arkts-network-troubleshoot`(L0–L3) / `arkts-login`(L4–L6) 各自 references。

**谁消费**：probe 模式（读靶子）、grill（读 RED 行与 uncertainty）、execute 登录切片（读逐层 owner/接线做落地自检）。

---

## 二、通用填写规则（chain-agnostic）

1. **逐层一块**，每块两个关键列：**`捕获?`（源里有没有、值/算法是什么）** 与 **`消费/接线者`（谁在下游把它接上）**。二者都实心才算这层通。
2. **完备性铁律**：每层**必须点名一个 owner**（哪个 feature / base / skill 实现它），或**显式写 `N/A + 理由`**。**无 owner = RED**。
3. **迁移性质四分类**逐层标：`契约照搬`（字节级复现，禁掩码/占位）/ `结构照搬`（同构重写）/ `平台重写`（按鸿蒙范式重做）/ `平台替代`（值会变、需后端配合——**风险点**）。
4. **novelty 逃逸口**：某层/某轴对不上任何已知分支 → **不硬套**，标 `→ U-<id>`（建 uncertainty）冒泡给 grill。反复出现的新形态由 retrospect 回灌、升级为新层/新轴。
5. **RED 类型与冒泡**：以下任一为 RED → 汇总到末尾 `RED 汇总` → 转 `uncertainties[]` 喂 grill（execute 期走已有"决策缺口"机制）：
   - `无 owner`（某层没 feature/base/skill 认领）
   - `捕获=unknown`（源码判不出）
   - `MISSING-TRUTH`（契约照搬层字节真值缺失/被掩码/封在不可读 AAR）
   - `接线悬空`（下游没接，如 no-op 恒等、token 没同步到拦截器）
   - `backend-contract 未对齐`（平台替代层，见规则8）
   - `红旗-需复查`（**捕获+接线都完整、但违背铁律或属罕见形态**——如证实"无全局签名层"、签名为内联实现、加密封在 AAR；既非 unknown 也非 MISSING-TRUTH，需后端/人工复查真实完整性）
   > **未 probe ≠ RED**：契约照搬层（签名/加密）若**捕获+接线都完整、仅未经 probe 字节验证** → 判 **🟢 + `needs-capture`**（待 probe/golden 核对），不是 🔴；🔴 只留给上面几类真断点。
6. **硬/软**逐层标：硬前置不通则该链必失败；软前置不影响链路成败（如 L7 下游）。
7. **一层多机制拆子行**：一层若含**多个独立机制**（如 L2 的 `签名` + `body 加密` + `防重打包指纹` 相互独立），逐机制拆子行、各自独立 `捕获/接线/probe`——别塞一行（fitness 的 md5 签名与 Cusrep body 加密是两回事；xiaoyibang 的 MD5 签名与登录体 AES 也是两回事）。
8. **平台替代层必填 `backend-contract` 状态**：凡 `平台替代` 层（设备标识、签名/防重打包指纹、body 加密密钥、租户常量…）强制填 `backend-contract: 未对齐 / 已对齐(附联调结论)`。**未对齐即 🔴 `BLOCKED-PENDING-BACKEND`**——禁 "传空串兼容后端""照搬安卓" 这类把跨团队 blocker 伪装成客户端占位的软化措辞（fitness 模式 G）。区别于 `契约照搬` 层的字节真值缺失（那是 `MISSING-TRUTH → U`，值在源码里、只是没抓到/被掩码，如 xiaoyibang 的 AES 密钥）。

---

## 三、auth 链档案（首个 profile · 固定参考，勿改字节真值来源）

> 新增链路时照此另写一份 profile（见 §六）。auth 层清单 = L0–L7。

### 3.1 铁律（固定行 · 5/5 项目命中，逐条必须成立或显式说明例外）
- **铁律1**：L1 隐私同意是所有采集/三方 SDK init 的硬闸门，且**门控 L2/L3 的 SDK（签名/OAID）init**。〔退化：若 L2 签名是**内联实现（无 SDK）**、且无设备采集 SDK，则 DEP1 的"门控 SDK init"**退化为 N/A**，不算漏层；L1 仍门控其余采集类 SDK（推送/统计/实人等）。〕
- **铁律2**：L2 请求可信化层是登录接口的硬前置——签名对了才谈得上发码/登录。
- **铁律3**：单 token、无 refresh，失效靠错误码重登（L6）。凭空发明 refreshToken = 红旗（fitness 模式 H）。

### 3.2 变化轴（分支选择 + 逃逸口）
- **轴A — 游客/设备 token 角色**：`持久业务基线(进Header)` / `一次性防刷` / `无` / `其他→U`
- **轴B — 设备身份对登录的作用**：`身份基线(换游客token)` / `请求可信化组件(进签名或防重放头)` / `与登录无关` / `其他→U`（可同时占前两个，如 deviceNo 既是身份又进签名）
- **轴C — 登录方式矩阵**（可多选）：`验证码` / `一键` / `三方` / `账号密码` / `其他→U`

### 3.3 层清单 L0–L7（发现指引 + 打通信号 + 实现 skill + 默认硬软）

| 层 | 该层要点 | 迁移性质 | 默认 owner 类别 | 安卓找什么（grep 起手式） | 打通信号 | 硬/软 |
|---|---|---|---|---|---|---|
| L0 | BaseUrl + 本地存储 + 身份常量(AppId/租户码/渠道) | 平台重写+契约照搬 | feature-base / app-identity | `BASE_URL` `buildConfigField` `API_ENV` `tenantCode` `productId` `appId`；**沉在资源子模块的常量往下层模块找** | 请求能带上正确 base_url + 身份常量 | 硬 |
| L1 | 隐私同意标志 + **门控 SDK init**（非 API，交叉核 owner） | 平台重写(UI)+结构照搬(门控) | bootstrap/startup **feature** | `isAgree` `privacy` `HAS_READ` `AGREE_PRIVACY` `initThirdSdk` `initPrivacyCompliantSDKs` | 未同意不 init 采集类 SDK + 进不到登录页；**同意后确有 init L2/L3 的 SDK** | 硬 |
| L2 | 签名 / body 加密 / 设备头（请求可信化） | 契约照搬 | Base-3 network | `Interceptor` `sign` `nonce` `authSign` `signature` `safe-env` `private-key` `encrypt` `getEncList` `decodeType` | probe 发一个业务请求返回**业务成功码**（非签名错/非 500） | 硬 |
| L3 | 设备标识 + 游客/设备 token | 平台替代(设备标识值变) | Base-3 network | `oaid` `deviceId` `getDeviceId` `uuid` `MediaDrm` `initUser` `deviceLogin` `vistorToken` `guest` `device/register` | probe 拿到游客 token / 设备被后端接受 | 硬/半(看轴A、轴B) |
| L4 | 方式凭证：发码 / 一键预取号 / 三方授权 | 平台替代(一键·三方) | auth feature(arkts-login) | `sendCode` `authcode` `kaptcha` `preLogin` `getLoginToken` `oneKey` `wxlogin` `authV2` | 拿到 code / loginToken / authCode | 按方式硬 |
| L5 | 登录接口 → 主 token | 契约照搬 | auth feature | `login` `bindMobile` `loginQuick` `fastLogin` `ringLogin` | 返回成功码 + 非空主 token | 硬 |
| L6 | 存 token + 头注入 + 失效码 + **冷启再水合** | 平台重写+结构照搬 | auth feature + Base-5 preferences | `saveToken` `isLogin` `TokenInterceptor` `401` `logout` + 冷启读回路径 | isLogin=true + 拉用户信息成功 + **冷启后 token 仍在** | 硬(存/注入) |
| L7 | 下游 IM / 推送 / 埋点 | 平台替代 | 各下游 feature | `connectIM` `chat/register` `setAlias` | 登录后连 IM / 收推送 | **软**(非前置) |

> **跨层依赖 + 链内时序（隐形杀手，实例 §5.2b 逐条显式记）**：层与层之间的依赖/供数/时序散落在 feature 之间、谁也不 own，正是本契约要 own 的。auth 链已知两类：
> - **门控依赖**：`L2/L3 的 SDK(签名/OAID) init 门控在 L1 同意之后` —— 登录切片不能假设 SDK 已就绪。
> - **供数 + 时序依赖（项目相关）**：某层产物是另一层输入、且有先后。典型：`deviceNo(L3) 掺进 L2 签名` → L2 依赖 L3 先换到 deviceNo；但**换 deviceNo 的首个请求本身不带 deviceNo**（只带四指纹），之后的签名请求才带——这类时序拐点必须记，否则实现顺序错、首请求就挂。

> **L6 冷启再水合是强制接线项（易漏，必须逐项判）**：不只记"token 存哪"，还要记"**冷启后谁把 token 从存储读回 UserSession**"。尤其当存储在鸿蒙侧从**同步读（Android SP/GreenDAO）→ 异步读（HMOS `relationalStore`/`preferences`）**时，若沿用同步 `getToken()` 假设、无冷启再水合步骤 → 冷启 token 空 → 首个鉴权请求即失效码踢回登录。**冷启再水合 owner/接线不清即 RED**（`接线悬空`），不因"token 存储已捕获"就放过。

---

## 四、probe 规格（喂 arkts-network-troubleshoot 的 probe 模式）

> probe 是**有界自愈循环**（非单发）：发→读业务错误→归类→从源码派生候选调一个字段→重试，直到 code:0 或上限跳过。详见 `arkts-network-troubleshoot` 的 [probe-runbook.md] + [probe-error-remediation.md]（错误→修法知识库）。**本契约给 probe 的是"靶点 + 公参字段的值来源"**（不必是精确值——精确值交循环实测后回填），尤其带签名的公参对象（platformInfo/公共请求参数）要记清各字段值来源（flavor 配置 XML / 渠道清单 / buildConfig），**别用 gradle 默认占位**。

- **前置（必答，否则 probe 无法判 PASS）**：`业务成功码`（§5.0）+ 测试 `base_url`。缺任一 → **不静默 static-only**，产早期 grill 问题（U-CODE / U-ENV）。
- **靶点选择**（越深越好、不需人工凭证）：优先免凭证却走完整 L2 头/签名/设备栈的端点——`initUser`/`vistorToken`/`deviceNo→deviceLogin`/`getUserConfig` 或图形验证码；一发命中即证明 L0–L3 整条。
- **body 加密杀手风险**（如登录体 AES）：用**垃圾凭证**打登录端点，靠区分 `业务拒绝(账密错)` vs `协议拒绝(解密失败/-xxx)` 证明加密层字节对不对——查的是"请求有没有走到能做业务判断那一步"，不是"有没有登录成功"。
- **判定口径**：`backend-facts` 里的**业务成功码**（`status==0`/`code=='200'`），**不是 HTTP 200**。
- **PASS/FAIL → 回写 `uncertainties[]`**：
  - PASS → 相关不确定项 `resolved-by-probe`；设备替代值被接受 → 轴B 平台替代顾虑消解。
  - FAIL-签名/加密 → 收窄成"密钥/算法/AES 参数不对"的阻断问题。
  - FAIL-设备 → 收窄成"后端需为鸿蒙设备标识放开识别口径"。
  - 无测试环境可打 → 产出"给测试 base_url/账号"的早期 grill 问题，**不静默 static-only**。
- **golden fixture**：probe 成功的那次**请求/响应存档**，交给 execute 的 `verify-sign.js` 离线核对 ArkTS `SignUtil` 字节复现（闭"spec 证明 ≠ ArkTS 实现"跳）。

---

## 五、本项目实例填写区（→ 生成 `data-chains/chain-auth.md`）

> 以下 `〈…〉` 为待填。填法：API 层从 `auth_model` 投影；L1/L0-身份去 feature-index 交叉核；每层两列都要实心或标 RED/U-id。

### 5.0 元信息
- 项目：〈name〉　| chain：`auth`　| 目标 BaseUrl(测试)：〈url / U-ENV〉　| 业务成功码：〈status==0 / code=='200' / U-CODE〉 **（probe 前置：必答）**
- 变化轴选择：轴A=〈持久基线/一次性防刷/无/U-〉　轴B=〈身份基线/进签名/无关/U-〉　轴C=〈验证码+一键+三方+密码 的实际子集〉
- probe 结果：〈PASS / FAIL-xxx / 无环境〉→ 证据：〈golden fixture 路径 / U-id〉

### 5.1 完备性总表（一眼看 RED/GREEN）

| 层 | owner | 捕获? | 接线? | 硬/软 | 状态 |
|---|---|---|---|---|---|
| L0 | 〈〉 | 〈〉 | 〈〉 | 硬 | 🟢/🔴 |
| L1 | 〈feature〉 | 〈〉 | 〈门控L2/L3?〉 | 硬 | 🟢/🔴 |
| L2 | 〈Base-3〉 | 〈sign算法+密钥 file:line / U-〉 | 〈拦截器挂载?〉 | 硬 | 🟢/🔴 |
| L3 | 〈Base-3〉 | 〈设备标识源 / U-〉 | 〈进头/进签名?〉 | 〈〉 | 🟢/🔴 |
| L4 | 〈auth feat〉 | 〈〉 | 〈〉 | 〈〉 | 🟢/🔴 |
| L5 | 〈auth feat〉 | 〈端点+字段〉 | 〈〉 | 硬 | 🟢/🔴 |
| L6 | 〈auth feat+Base-5〉 | 〈token key〉 | 〈头注入+失效+冷启水合?〉 | 硬 | 🟢/🔴 |
| L7 | 〈下游 feat〉 | 〈〉 | 〈懒连接〉 | 软 | 🟢/🔴 |

### 5.2 逐层明细（每层两列）

> 每层照此块填。示例注释见 `〈…〉`。

```
### L2 请求可信化  ← 多机制拆子行（规则7）
- owner: 〈Base-3 network〉                      ← 无 owner 即 🔴
- [签名] 迁移性质:契约照搬  硬/软:硬
    捕获[源→值]: 〈sign=MD5(参数字典序+盐)；盐/密钥从源码 file:line 现读(禁掩码)；排序=CASE_INSENSITIVE；hex大写〉 / 〈unknown→U-〉
    消费/接线: 〈rcp Session 挂 SignInterceptor @file〉 / 〈悬空→🔴〉
- [body加密] 迁移性质:契约照搬  硬/软:硬(命中清单/特定端点)
    捕获[源→值]: 〈算法(AES-CBC/自研)+密钥+IV+清单来源 file:line〉 / 〈密钥掩码/未抓→MISSING-TRUTH→U-〉
    消费/接线: 〈命中才加密的拦截器 @file〉 / 〈no-op 恒等→🔴〉
- [防重打包指纹] 迁移性质:平台替代  硬/软:硬(若后端强校验)
    backend-contract: 〈未对齐→🔴 BLOCKED-PENDING-BACKEND / 已对齐(联调结论) / N-A〉  ← 规则8，HAP 指纹≠APK
- 打通信号: probe 发图形码/发码端点 → 业务成功码（非签名错）；body 加密另用垃圾凭证打登录端点验"业务拒绝 vs 协议拒绝"
- 证据: 〈file:line / U-id / golden fixture〉
```
> 其余层各填一块；**单机制层不拆子行**。`平台替代` 层（L3 设备标识、L2 防重打包…）按规则 8 补 `backend-contract`；`契约照搬` 层的字节真值缺失标 `MISSING-TRUTH→U`（值在源码、别当占位混过）。

### 5.2b 跨层依赖与链内时序（隐形杀手，逐条显式记）

| DEP-id | 类型 | 依赖/供数/时序 | owner | 是否已接 / 时序拐点 |
|---|---|---|---|---|
| DEP1 | 门控 | L2/L3 的 SDK(签名/OAID) init 门控在 L1 同意之后 | 〈bootstrap feature〉 | 〈是/否→🔴〉 |
| DEP2 | 供数+时序 | 〈如 deviceNo(L3) 掺进 L2 签名；换 deviceNo 首请求不带 deviceNo、之后才带〉 | 〈〉 | 〈时序拐点→错则首请求挂〉 |

### 5.3 RED 汇总（→ uncertainties[] / grill）

| RED-id | 层 | 类型(无owner/捕获unknown/接线悬空/probe-FAIL) | 描述 | 转 U-id | 触发点(spec收尾核/execute自检) |
|---|---|---|---|---|---|
| 〈R-1〉 | 〈L1〉 | 〈无owner〉 | 〈feature-index 无隐私/启动 feature owns L1〉 | 〈U-〉 | spec 收尾核 |

---

## 六、如何新增一条链路（chain-pay / chain-push …）

1. 在 §三 旁另写一份 profile：定义**该链的有序层清单**（payment 不是 L0–L7，是它自己的 env→签名→支付凭证→SDK→回调→订单核验）、**它的铁律**、**它的变化轴**、每层的**发现字典/打通信号/实现 skill**。
2. §四 probe 规格照搬（靶点换成该链最便宜的可验证端点）。
3. §五 实例填写区结构不变，层清单换成该链的。
4. **不预先建**——某条链路反复出问题时再填它，profile 的铁律/轴由 retrospect 从实战回灌沉淀。

<!-- 单一源不变：任何链路的 API 层都投影自 api-inventory.json（对应 chain 的 auth_model/等价段），非 API 层交叉核 feature-index。 -->
