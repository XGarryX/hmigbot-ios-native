# 用户预知阶段一收集：HarmonyOS 参考文档（3.0c）+ 后端契约（3.0c2）

> 本文件是 a2h-spec SKILL.md §3.0c 与 §3.0c2 的**完整执行规范**。SKILL.md 仅保留摘要 + 指针；执行到对应步骤时 **MUST Read 本文件全文**。两步同构（检查文件 → 三选一 → 记变量 → 完全可选不阻断），前半部分写 3.0c，§后端契约预知收集 写 3.0c2。

> 用户内部已知的 HarmonyOS 文档 / 厂商手册 / 私有镜像在 api-inventory 跑之前就收集，让 api-inventory 阶段就能利用。后续 plan grill #2 Step 0（用户预知阶段二）再针对未闭环的具体 API/SDK 项做精细化追问。
> 配套模板：`templates/hmos-references-template.md`。

执行逻辑：

```
检查 spec/ref/hmos-references.md 是否存在
  │
  ├─ 已存在 → 记录 $HMOS_REFS_FILE = spec/ref/hmos-references.md，跳过本步后续，进入 Phase A
  │
  └─ 不存在 → 询问用户三选一：
      - **选项 A**：现在引导填写（模型逐类问：总索引 / 厂商手册 / 内部资源）
      - **选项 B**：以模板创建空文件 `spec/ref/hmos-references.md`，用户手工编辑后再继续
      - **选项 C【可跳过】**：跳过不创建（后续仍能在 plan grill #2 Step 0 临时收集，仅缺 api-inventory 阶段预标注）
```

**选项 A 引导流程**：三类逐一询问（总索引：HarmonyOS Developer Docs / ArkTS 手册 / 内部 Wiki；厂商手册：微信 / 支付宝 / 华为账号等逐条；内部资源：私有镜像 / 合作方鸿蒙包 / 已迁移方案），每类允许"暂不提供"。收集到任意一条 → 以 `templates/hmos-references-template.md` 为骨架生成文件填入链接；全部"暂不提供" → 视为选项 C。

**选项 B 流程**：把模板整文件拷到 `spec/ref/hmos-references.md` → 提示用户手工编辑后说"继续" → 记录 `$HMOS_REFS_FILE`，进入 Phase A。

**选项 C 流程**：不创建文件，记 `$HMOS_REFS_FILE=null`，进入 Phase A。

**HARD-GATE**：本步骤**完全可选**，不阻断任何后续。`$HMOS_REFS_FILE=null` 时 Step B0 的子 agent prompt 不传该参数；plan grill #2 Step 0 检测到该文件不存在则按原逻辑全量问用户。

## 与下游的契约

- 本步产出 `$HMOS_REFS_FILE`（= `spec/ref/hmos-references.md` 或 `null`），由 Step B0 作为 `hmos_references_file` 参数透传给 `android-api-inventory` 子 agent。
- 子 agent 据此在 Phase 2.5 产「HarmonyOS 等价物提示段」，状态经 Step B-join 的 `hmos_hint_status` 传给下游 a2h-plan grill #2 Step 0，决定是否重复追问。

---

## 后端契约预知收集（3.0c2 · v1.3）

> 收集对象与 3.0c 不同：3.0c 收「HarmonyOS 侧知识」（等价物文档），本步收「**后端契约事实**」——接口文档 / Postman / Swagger、响应壳约定、业务成功码与 token 失效码、关键接口必填字段与 enum、后端联系人。这类信息**只有用户或后端团队掌握**，模型查公开文档查无可查；不前置收集，就只能等 execute 联调撞坑后再回头问。
> 配套模板：`templates/backend-facts-template.md`。

执行逻辑（与 3.0c 同构）：

```
检查 spec/ref/backend-facts.md 是否存在
  │
  ├─ 已存在 → 记录 $BACKEND_FACTS_FILE = spec/ref/backend-facts.md，进入 Phase A
  │
  └─ 不存在 → 询问用户三选一：
      - **选项 A【推荐 —— 项目有带鉴权的后端接口时】**：现在引导填写（模型逐类问：接口文档入口 / 全局响应约定 / 关键接口细节 / 后端联系人）
      - **选项 B**：以模板创建空文件 spec/ref/backend-facts.md，用户手工编辑后再继续
      - **选项 C【可跳过；有鉴权后端接口的项目不建议跳】**：跳过不创建（后续 plan grill #2 Step 0-C17 仍能临时收集，
        仅缺 api-inventory 阶段的 uncertainties 预销账；且 dev_info 缺失 → spec 期 probe 跑不了，见要点 4）
```

**选项 A 引导要点**：逐类询问，每类允许"暂不提供"——
1. **接口文档入口**：Swagger / Postman 集合 / 内部 API wiki / YAPI 链接
2. **全局响应约定**：响应壳形状（`{code,msg,data}` 还是别的）、业务成功码、token 失效码集 + 客户端预期动作
3. **关键接口细节**（登录/启动/支付优先）：必填字段、服务端 enum 允许取值、DB NOT NULL 约束
4. **后端联系人 / 环境**：可确认契约的后端同事、测试环境地址与账号 —— 其中**测试访问三件套（测试 base_url + 业务成功码 + 测试账号）是 spec 期 auth-chain probe 的唯一前置**，另结构化落 `spec/baseline/dev_info.json`（见 a2h-spec Step 3.0c2）；缺则 probe 跳过、鉴权链路的打通验证退回 execute 联调期撞坑

收集到任意一条 → 以模板为骨架生成文件；全部"暂不提供" → 视为选项 C，记 `$BACKEND_FACTS_FILE=null`。

**HARD-GATE**：本步**完全可选**，不阻断任何后续。

### 与下游的契约（3.0c2）

- 产出 `$BACKEND_FACTS_FILE`（= `spec/ref/backend-facts.md` 或 `null`），由 Step B0 作为 `backend_facts_file` 参数透传给 `android-api-inventory` 子 agent。
- 子 agent 在 Phase 3.1b 生成 `uncertainties[]` 时用它**预销账**（能直接回答的项建为 `answered`，`resolved_by` 标本文件 section）；残余 `open` 项由 a2h-plan grill #2 Step 0-C17 按链路收口。
- `arkts-network-troubleshoot` Phase 0.6（服务端契约）与本文件互补：本文件是 spec 期用户预知，Phase 0.6 是 execute 期向后端的正式索取——已有本文件时 Phase 0.6 只补缺口。
- 用户可在项目全周期手工追加；下次 api-inventory 或 grill 跑时自动消费新内容。
