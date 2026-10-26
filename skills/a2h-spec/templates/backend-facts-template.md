# 后端契约事实 — {项目名}

> 用户预提供的后端契约参考。由 a2h-spec Step 3.0c2 在源码路径确认后收集，落到 `spec/ref/backend-facts.md`。
> 下游消费方：`ios-api-inventory` Phase 3.1b（对 `uncertainties[]` 预销账）、a2h-plan grill #2 Step 0-C17（残余项收口）、`arkts-network-troubleshoot` Phase 0.6（execute 期向后端正式索取时只补本文件缺口）。
> **本文件可在项目全周期手工追加 / 修改**；每次 api-inventory 或 grill 跑时会重新读，无需重新生成。

---

## 1. 接口文档入口

> Swagger / Postman 集合 / 内部 API wiki / YAPI 等总入口。模型判定"某接口契约长什么样"时优先查这些。

- [ ] Swagger / OpenAPI: __
- [ ] Postman 集合: __
- [ ] 内部 API Wiki / YAPI: __
- [ ] 其他: __

---

## 2. 全局响应约定

> 这些是源码推不准、抓包才能定的 ② 类事实——用户直接填了，api-inventory 就不用留 uncertainty 给 grill 问。

| 约定项 | 取值 | 备注 |
|--------|------|------|
| 响应壳形状 | __（如 `{code,msg,data}` / `{status,toastMsg,data}` / 扁平） | 自有业务域；三方域另列 |
| 业务成功码 | __（字段名 + 成功取值，如 `status == 0`） | |
| token 失效码集 | __（如 `-1001`） | 客户端预期动作：__（清 token / 跳登录 / 广播）；guest 态是否同样处理：__ |
| 其他全局错误码 | __ | |

---

## 3. 关键接口细节（登录 / 启动 / 支付优先）

> 每个关键接口一小节：必填字段、服务端 enum 允许取值、DB NOT NULL 约束、样例响应。没有的删掉。

### {POST /user/initUser}（示例，替换为实际）

- 必填字段：__
- 服务端 enum 约束：__（如 channel 允许取值列表）
- DB NOT NULL：__（如 USER_INFO.iOS_ID）
- 样例响应（可贴脱敏 JSON）：

```json
```

---

## 4. 后端联系人 / 环境

- [ ] 可确认契约的后端同事: __
- [ ] 测试环境 base_url / 账号: → **结构化存 `spec/baseline/dev_info.json`**（模板 `templates/dev-info-template.json`，供 auth-chain probe 消费）；本处**不重复填**，避免两处记同一事实
- [ ] 后端代码仓（如可读）: __

---

## 使用约定（给下游 skill 消费方）

- 本文件**完全可选**：未提供时 api-inventory 的所有 ②③ 不确定项以 `open` 状态交给 plan grill #2 C17 临时收集
- 消费方对每条 uncertainty：**优先匹配本文件条目**；命中即预销账（`answered`，`resolved_by` 标 `spec/ref/backend-facts.md#section`）
- ⚠ 本文件**不要**粘贴任何密钥 / token 值；凭证类只写"在哪能拿到"
