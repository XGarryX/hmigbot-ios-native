# auth-chain 活性探针 Runbook（场景 E · 有界自愈循环）

> spec 收尾、grill #1 之前跑。**无需设备**：用静态签名 + 设备替代值从零构造真实请求、打后端测试环境，判**业务成功码**。
> **不是单发** —— 是一个**有界自愈循环**：发→读业务错误→归类→从源码派生候选调一个字段→重试，直到 code:0 或到上限跳过。把"人肉剥洋葱"自动化掉，避免"发现一个门补一个 spec"的打地鼠。

## 前置（缺则不静默跳过，产早期 grill 问题）

| 前置 | 来源 | 缺失动作 |
|---|---|---|
| 测试 `base_url` + 业务成功码 + 测试账号 | `spec/baseline/dev_info.json`（a2h-spec Step 3.0c2） | 建 `U-ENV`/`U-CODE`/`U-ACCOUNT` → grill 兜底问 |
| 靶点 + 签名/设备事实 + **公参字段的值来源** | `chain-auth.md` + `auth_model` | chain-auth 未生成 → 先跑 android-api-inventory Phase 2.8 |
| 签名字节真值（密钥/盐/参数序） | 源码 file:line（chain-auth L2 记的位置） | 掩码/缺失（`MISSING-TRUTH`）→ 停、冒泡（人输，见下） |

> **关键：捕获抓的是"值的来源"，不必是精确值。** 带签名的公参对象（platformInfo/公共请求参数）的字段值常散在 **flavor 配置（product.xml 等被 build.gradle 解析的 XML）+ 渠道清单（walle `channel/*.txt`）+ buildConfig**，且**不能用 gradle 默认占位**（如 versionName `1.0`）。循环从这些**来源**试出能通的值，成功后回填精确值——这比静态钉死每个值更 robust（"渠道必须真值不是 fallback"静态根本猜不到）。

## 选靶点（越深越好、不需人工凭证）

据 chain-auth 的轴 A/B 选：
- **轴A ≠ 无**（有游客/设备 token）：优先免凭证、走完整 L2 头/签名/设备栈的端点——`initUser`/`vistorToken`/`deviceNo→deviceLogin`/`getUserConfig`/图形验证码。一发命中即证明 L0–L3。
- **body 加密杀手风险**（登录体 AES，轴C 有密码/验证码）：用**垃圾凭证**打登录端点，区分 `业务拒绝(账密错=字节对)` vs `协议拒绝(解密失败=字节错)`。
- **轴B = 请求可信化组件**（deviceNo 进签名）：靶点选换 deviceNo 的端点（`device`）。
- **公共配置端点**（若存在真免 token 的 config/system/version）：干净隔离签名层——正确签名 code:0、错签名被拒（对照可证签名字节正确）。

## 自愈循环（核心）

```
attempts = 0
构造初始请求（靶点 body + 公参对象[字段值从"来源"试] + 签名[源码真值]）
loop while attempts < N (默认 N=10):
  发请求 → 读业务码/文案（非 HTTP 200，用 dev_info.business_success_code）
  ┌ code:0 成功 ────────────→ 存 golden + 回填发现的真值到 chain-auth/uncertainties → 退出 PASS
  ├ 客户端可调错误 ──────────→ 查 probe-error-remediation.md 取"修法+候选来源"，调**一个**字段 → attempts++ → 重试
  ├ 后端侧 / 人输 / MISSING-TRUTH → **立即停**（不耗次数）→ 冒泡 grill（见下）→ 退出 BLOCKED
  └ 未知错误（KB 无匹配）────→ 停 → 冒泡 grill + 追加一条待补 KB 条目 → 退出 UNKNOWN
到达 N 仍没通 ──────────────→ **跳过**（不阻断 execute）+ 记最后错误 + 试过的候选 → 冒泡 grill → 退出 EXHAUSTED
```

**每步只调一个字段**（便于定位是哪个门），候选从**源码派生的有限集**取——**绝不随机 fuzz**。错误→修法查 [probe-error-remediation.md](probe-error-remediation.md)（可增长知识库）。

### 错误三分类（决定循环还是停）

| 类 | 特征 | 动作 |
|---|---|---|
| **客户端可调** | 版本/包/baseType 门、渠道→媒体号映射、DB 非空约束、键序/hex 大小写/时间窗、防重打包指纹(有 keystore 可算) | **循环调**（从源码派生候选） |
| **后端侧** | "后端需为鸿蒙放开设备识别口径"、渠道/媒体号后端表里没有、后端全局 token 门(新客户端如何 bootstrap) | **立即停 + 冒泡**（backend-contract，需后端） |
| **人输 / MISSING-TRUTH** | 签名/AES 密钥被掩码或封在不可读 AAR、测试账号/环境缺 | **立即停 + 冒泡**（值在源码/需用户，循环修不了） |

> 循环**只**啃"客户端可调"类；后端/人输类**不硬试**（硬试既刷屏后端又假装能自愈）。

### 候选来源约定（禁 fuzz）

| 字段 | 候选来源（有限集） |
|---|---|
| versionCode/versionName/baseType/packageName | flavor 配置 XML（product.xml 等）；**禁 gradle 默认占位** |
| 渠道 channel | walle 渠道清单 `channel/*.txt` 的**真实值**；**禁 fallback 默认** |
| 设备指纹 oaid/androidId | 非空占位（OAID 非全 0 否则持久 UUID；androidId 16 hex）；**禁空串/全 0** |
| 防重打包签名指纹 | 从项目 keystore（`app/sign/*`）用 keytool 导出证书算 MD5（见 KB motu 条目） |
| 签名键序/hex/时间窗 | chain-auth L2 记的算法；试大小写/毫秒vs秒/键排序 |

## 护栏（安全，缺一不可）

1. **上限 N 次就跳**（默认 10）——非阻断，交 grill。
2. **候选是源码派生有限集，不随机枚举**（不刷屏后端、不像攻击）。
3. **后端/人输类立即停**，不浪费次数硬试。
4. **不循环猜凭证、不刷短信、不做写状态的重试**——只对**幂等游客态端点**（device/initUser/vistorToken/config）循环；带真凭证的 login/register/发码**不循环**（发码会真发短信）。

## 成功回填（治打地鼠：发现即沉淀）

PASS 时：
1. **存 golden**：`spec/baseline/api-inventory/data-chains/chain-auth.golden.json`（endpoint/headers/body/签名输入串/响应）——供 execute 期 `verify-sign.js` 字节对账（见 [phases.md](phases.md) Phase 3）。
2. **回填真值**：把循环试出的能通值（真实版本/baseType/渠道/指纹）回填 `chain-auth`/`uncertainties`（`resolved-by-probe`），android-api-inventory 重投影 chain-auth（RED→GREEN）。
3. **沉淀 KB**：若这轮撞到**新的**"错误→修法"模式，追加一条到 [probe-error-remediation.md](probe-error-remediation.md)——下个项目**自动**受益，novel 门只发现一次。

## 冒泡（BLOCKED/EXHAUSTED/UNKNOWN）

回写**共享** `uncertainties[]`（`chain=auth`）：后端类 → `backend-contract 未对齐`；人输/MISSING-TRUTH → 对应 U-id；EXHAUSTED → 记最后错误 + 试过的候选。grill 据此带证据问。**绝不记 static-only 蒙混。**

## 边界

- probe 证明的是 **L0–L3 请求可信层**（最硬、最共性的死因层），不完整证明 L5 真实登录（需真凭证）。
- probe **不改代码、不落 HMOS 实现**——只发请求 + 回填 + 存 golden。
- 循环能自愈的只有**客户端可调**门；**后端配置 / 字节真值缺失**它修不了、只冒泡（这是对的，不是缺陷）。
