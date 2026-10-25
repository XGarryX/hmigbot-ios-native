# Phase 2.5 — 功能点 grounding（iOS实测锚定 oracle，dual-oracle 上游）

> 仅当 fact-tree 某 page 的 record 带 `functional_checks[]`（由 a2h-functional-merge 注入）时才跑。
> 目的：在 Phase 2 iOS趟「已经导航到该 page」之后，**逐功能点实操 + 观察 + 结构指纹自验**，把真实iOS行为写进 `expected_ios` / `ios_trusted`，作为下游鸿蒙双 oracle 判定的**主判据（ground truth）**。`expected_llm`（A2H/LLM 静态种子）保留当保底。
>
> **为什么独立成 0.5 不塞进 Phase 2 截图主体**：Phase 2 设计为轻量截图趟；grounding 给每页加「点 N 个按钮各观察一次」是实质新增工作。逻辑上是「导航到页」之后的内循环，但单列一步避免污染截图主流程。functional_checks 为空的 page **完全跳过本步**，零开销。
>
> **写回边界（铁律）**：只改 `functional_checks[].{expected_ios, ios_trusted, precondition}` 三字段——这是 a2h-functional-merge / grounding 自己 own 的字段。**绝不碰** toolkit/app-relationship-tree 已填的 navigation / reach_path / purpose / components 等。

## 触发时机
Phase 2 per-page 循环里，**截图 + 存 dump 之后**（即 phase2-ios-batch-prompt.md Step 1.5 之后），对该 page：
```
读 spec/toolkit-fact-tree.json 该 page record 的 functional_checks[]
  为空 → 跳过，进黑盒/下一页
  非空 → 对每条 check 跑下面 6 步
```

## 每条 functional_check 的 6 步

-1. **check_kind 分流（枚举收敛产物，2026-07-10 fold_enum_groups）**——先看 `check.check_kind`：
   - `enum_group_presence`（组存在性）→ **零点击 grounding**：拿本页已存的 baseline dump（`screenshots/ios/{trip}/{page}.ios.xml`）对 `members[].name` 做文本匹配。全部命中 → 填 `expected_ios="全部 <n> 项存在: <名单>"` + `ios_trusted=true`；有缺 → 如实记缺失名单（可能是滚动区未展开，先滚动重 dump 一次再判）。**不进下面 1-6 步**。
   - `enum_group_behavior`（组代表行为）→ 走正常 1-6 步，tap 目标 = `check.representative`（判据/锚点已随代表成员携带）。组内其余值**不逐个 grounding**——同构组走同一代码路径，代表值即真值。
   - 其它 / 无 check_kind → 正常 1-6 步。

0. **（Q2 透传，若有则先做）读前置态 `precondition_required`**：a2h-functional-merge 透传的源码级前置态（如 `队列非空且未锁定` / `已登录` / `当前已应用筛选条件`）。非空时**先据此把 App 切到该状态再测**（必要时调 arkts-scenario-runner 造态）——否则这条功能点根本到不了、grounding 会误记「无响应」。它也是 step 5 `precondition` 的种子（无需从零现场摸索）。

1. **定位按钮**：**若 check 带 `tap_by=="text"`（Compose 注入，无 resource-id）→ 直接用 `tap_text`/`name` 文字匹配 clickable**，跳过 resource-id 尝试；否则（XML 默认）优先 `ios_anchor.raw_identifier` 当 resource-id 在 `uiautomator dump` 里找节点，找不到再用 `name` 文字匹配。dump 坐标系 = 物理分辨率，tap 直接用节点 bounds 中点。
   - **（Q2 透传）`source_section` 给交互方式**：`context_menu`→长按触发；`dialog`/`bottom_sheet`→该控件在弹层内（先开弹层再找）；`enum_options`→是某选择项（在选择器/列表内）；`seekbar`→拖动而非点击。据此选 tap/longtap/drag，避免对长按项做单击而误判「无响应」。

2. **按 `verify_by` 分流执行（Q2 事务型 oracle）**：

   **2a. `verify_by == "outcome"`（事务型：登录/支付/提交等）——走完事务，抓成功态，不是单点抓门禁。**
   > 病根：单点登录按钮（没填手机号/码/勾协议）只碰到**校验门禁**（toast「请先同意」/ 停留原页），而坏登录**也是**这个表现 → grounding 记成门禁 → 下游门禁配门禁假 PASS。必须**用真凭证走完**才看得出"能不能用"。
   ```text
   python3 $SKILLS_ROOT/arkts-visual-verify/scripts/verify_outcome.py \
       --scenario <check.outcome_scenario> --device ios \
       --device-id $IOS_SERIAL --package <pkg> --project-root .
   ```
   - `reached_outcome=true`（exit 0）→ `ios_trusted=true`，`expected_ios` = 返回的 `outcome_state`（**成功判别态**，如"到达已登录态：我的页显示账号/VIP"），`precondition` 记完成前置（如"未登录起点+真凭证"）。
   - `reached_outcome=false`（exit 1）→ iOS自己都没走通：**大概率配方腐坏/凭证问题**，`ios_trusted=false`、记观察，别当真值（iOS侧该成功；连iOS都失败先修配方，非鸿蒙退化）。失败时输出带 `failure_trace.signatures`（自动抓的设备日志业务错误，逐请求 path→status/toast）——iOS侧用来快判配方哪步腐坏；**鸿蒙 dual-oracle 侧(B.4.5 5c)**据它归因到「首个失败步」当根因、同根 fold，别停在终端症状。
   - `scenario_not_found`（exit 2）→ 该事务**无完成配方**：上报主会话，**由主会话派 `scenario-builder`** 学一份 `spec/scenarios/<name>.yaml`（泛化路径，非手写；sub-agent 无子代理派发权，禁自派（`spawn_agent` 归主会话））；确属自动化走不完（三方 OAuth）→ 该点应回 `landing` + 标 low_confidence，不硬撑。
   - ⚠️ **状态污染**：走完真登录后 App 变已登录态 → 该 page 的 outcome 点**排到本页/本 trip 最后测**，或测完 `pm clear`/登出复位，免得污染同页后续 landing 点。

   **2b. `verify_by == "landing"`（默认，绝大多数控件）——单点看落地（原行为不变）。**
   `input tap` → dump + 截图，概括成一句**实际发生了什么**（跳到 X 页 / 弹出 X 弹窗 / toast X / 停原页无反应）。
   - ⚠️ **toast 易漏**：`expected_llm` 含「toast / 提示 / 已是最新」之类的项，**点完 1s 内立即截图**，否则 toast 消失、dump 抓不到（实测坑）。

   **2c. 落地是 WebView 容器页的特化（2026-07-11，治"activity 名判落地对容器恒真"假阳性）**
   > 病根实证：AIPPT 的 CustomerServiceWebActivity 一个容器承载 举报/联系我们/售后中心 N 个 H5，
   > 三个入口 check 的真值全记成"→ CustomerServiceWebActivity"——鸿蒙把三个入口全接错到同一 H5 也照样 PASS。
   > H5 语义 = 功能项不是 UI 项：内容非迁移物（两端同 URL 同网页），迁移物 = 接线(URL) + 壳(桥接/渲染)。
   - **粒度铁律**：`expected_ios` 禁止只记容器 activity 名，必须记
     `{url: <运行态抓取,phase4-webview 2.1.4-a 方法>, h5_signature: [2-3 个静态结构性文本]}`。
     签名**只准选**页面标题/固定栏目名（如"售后中心/自助服务"），**禁选**动态内容
     （聊天消息/时间戳/运营文案/常见问题列表——服务端随时改版，选了就是未来假 FAIL）。
   - **桥接功能点（L3，registry 把 @JavascriptInterface/onShowFileChooser/setDownloadListener 入册的）**：
     验证深度 = **进 H5 后定向一跳**——在 H5 内找到触发控件（如"一键退款/上传图片/客服电话"）tap 一次，
     **oracle 锚定原生侧反应**（弹原生确认弹窗/系统相册/拨号盘/下载器——dump 稳定，与 H5 DOM 质量无关；
     H5 只是走廊不是判定对象）。破坏性桥（callRefund/unsubscribe）沿用 step 4：点到原生确认弹窗即停。
   - **防偏差降级（H5 是服务端的，会漂）**：H5 内**定位不到**触发控件 → 记 `untriggered`（ios_trusted=false
     + 原因），**绝不判 FAIL 也不硬凑**——定位失败的根因大概率是 H5 改版，不是功能缺失。
   - URL 抓不到（2.1.4-a 全失败）→ 记 h5_signature 为主 + 标 url_unavailable，不阻断。

3. **结构指纹自验（核心，独立于 expected_llm；`verify_by==outcome` 已由 verify_outcome 的 reached_outcome 直接给可信度，跳过本步指纹判）**：判「落点对不对」，**不是**「和 expected_llm 文字像不像」——LLM 种子本就可能写糙，以iOS真实为准。
   - 拿落地页的结构（resource-id 集 / 关键控件 / 标题文本 / 能否在 fact-tree 里匹到对应 record）对照「这个功能点**该去**的地方」（看 name + iOS源码该功能真实目标 + fact-tree 有无该落地 record）。
   - **到达且结构吻合** → `ios_trusted = true`，`expected_ios` = 实测落地一句话。
   - **没到达 / 停在原页 / 跳到明显无关页 / 无响应 / dump 取不到** → `ios_trusted = false`（判为误触或没点中），`expected_ios` 记观察（可空/记「未能到达」）。**绝不在没真到达时瞎写一个 true**——这是挡误触的关键。

4. **破坏性确认照测但点到即停**：退款 / 取消订阅 / 删除 等不可逆确认——点到**弹出确认弹窗**即可（「弹确认弹窗」本身已是足够的 grounding 真值），**不点「确定」**，避免在测试账号上发起真实不可逆操作。若确实触发了不可逆动作，在 `expected_ios` 里注明「⚠️已触发不可逆X」。

5. **记前置态**：把当前测试态（如 `未登录` / `已登录VIP`）写进该 check 的 `precondition`。**下游鸿蒙判定时两端登录态必须一致**，否则可信真值会错配（实测：未登录态测出的「个人中心→跳Login」，只在鸿蒙也未登录时才能正确对比）。

6. **写回** `spec/toolkit-fact-tree.json`（python 改 json，只动这 3 字段，保留其余）：
   ```jsonc
   "expected_ios": "未登录→跳 LoginActivity 手机号登录页",   // 实测；trusted=false 时可空/记未达
   "ios_trusted": true,                                     // 指纹判落点是否可信
   "precondition": "未登录"                                     // 两端须一致
   ```
   测完返回该 page，进下一条（必要时重新 force-stop + 导航回该页）。

## 已验证的真实表现（切片 MineSetting 11 + HSVFX 7）
- 指纹正确挡住 3 个「iOS首页动态配置无入口、UI 够不着」的工具 → `ios_trusted=false`，没瞎写 true。
- 校准了 4 个 LLM 种子的错 oracle：举报（LLM「标签选中」→实际打开反馈H5）、取消订阅（LLM「单选项选中」→实际弹确认弹窗）、个人中心/账号管理（LLM「跳页」→未登录实际跳 Login）、关于我们（LLM「用户协议页」→实际 AboutUsActivity）。

## 门禁/前置功能本身也是功能点(防漏测铁律)
登录 / 上传图 / 授权 / 跳转到态 这类**前置步骤本身就是被迁移的功能**。grounding 时:
- 若该前置功能在 fact-tree 里有对应 functional_check(如 LoginActivity「立即登录」),**必须像普通功能点一样 grounding**(iOS实操→记 expected_ios+trusted),**不能因为它"只是 setup"就跳过**。
- iOS侧建立态时若该前置功能成功(如登录成功),这本身就是它的 `expected_ios` 真值(trusted=true),供鸿蒙端判定时对照。
- **下游鸿蒙判定/scenario 阶段,这类门禁功能若失败,默认假设是"功能退化"而非"环境问题"**——必须按 SKILL.md「门禁功能对照实验铁律」跑对照(另一端同输入是否成功 / 平台是否健康 / 是否即时失败),证明是环境才降级,否则写 P0 FAIL + blocks_subtree。已发生的真实漏测:鸿蒙登录按钮不真正发起登录、即时关页,差点被当成"模拟器网络问题"放过。

## 与下游判定的接口
本步产 `expected_ios` + `ios_trusted` + `precondition`。鸿蒙端判定见 [`sub-agent-batch-prompt.md`](sub-agent-batch-prompt.md) 的「功能点双 oracle 判定」段：
- `ios_trusted=true` → 鸿蒙实测 H 匹配 `expected_ios` 则 PASS，不匹配则 FAIL（A 是可信真值，鸿蒙不符=真退化）。
- `ios_trusted=false` → 退回 `expected_llm` 弱判 + 标 `low_confidence`（iOS无可信真值，保守）；若鸿蒙端实际可达且与源码预测一致，补记一句供人工升级置信。
