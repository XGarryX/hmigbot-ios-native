> **iOS 源输入**：读取 Swift/Objective-C、SwiftUI/UIKit、Xcode 工程及原生资源；实际源构建与设备观测依赖可用的源平台环境。鸿蒙侧构建和验收保持原流程。源侧操作详见 `a2h-spec/references/native-input.md`。

# Step 4.-1 — 调用 arkts-scenario-runner 把 App 开到就绪态

> 从 SKILL.md §4 Step 4.-1 抽出。sub-agent 进入页面前 Read。
> 仅非 public 页面需要此步；public 页面直接跳到 [Step 4.0 导航](phase4-navigation.md)。

---

## 执行流程

```
scenarios = page_scenarios.json.pages[{page_id}]
            or (reachability == "login_walled" ? [page_scenarios.json.defaults.login_walled || "login"] : [])

IF scenarios 为空:
  # data_dependent 且没声明场景 → 无法自动到达
  # 不许 silent skip，必须写 CRASH markdown 报告缺口
  status = "blocked"; reason = "scenario_required_undefined"
  写 spec/fix/round-N/ui/CRASH_P{page_id}_scenario_required_undefined.md：
    kind: CRASH
    fixer_layer: feat                                # scenario YAML 改动归 scenario-builder / feat 层
    suggested_files: ["spec/visual-verify/page_scenarios.json"]
    Section 5 修复建议:
      1. 主会话派 scenario-builder agent（sub-agent 无子代理派发权，派发归主会话（`spawn_agent`））：
         学出配方 + 在 page_scenarios.json 声明 → 重跑本页
      2. builder 报 NEED_HUMAN_FIXTURE（需 NFC/支付/真实短信，附穷尽证据）→ 才评审是否豁免本页
  continue 到下一页
  # （v2026-07-10c：无独立预检环节——本分支就是"计划外状态"的正常 at-need 路径，撞到才学。
  #  但若同一状态反复触发本分支 = builder 学的配方没在 page_scenarios.json 声明住，查声明而非重学。）

FOR scenario IN scenarios:
  # 先看 iOS baseline 是否已存在（Phase 2 产出即复用，不重截不重跑 scenario）
  ios_baseline_exists = exists "screenshots/ios/{trip_id}/{page_id}.png"

  IF ios_baseline_exists:
    devices_to_run = [harmonyos]    # iOS 源端跳过 scenario，baseline 已可复用
    log f"✓ skip iOS scenario (baseline exists page={page_id})"
  ELSE:
    devices_to_run = [ios, harmonyos]

  FOR device IN devices_to_run:
    python $SKILLS_ROOT/arkts-scenario-runner/scripts/scenario_run.py \
        --scenario {scenario} --device {device} \
        --device-id {对应 device id} \
        --package {该端的 bundleName/package} \
        --no-interactive           # 循环里禁交互，首次需先单跑一次 login 建立 creds 缓存

    读取 spec/scenarios/artifacts/<最新>_<scenario>/result.json
    IF result.success == false:
      status = "blocked"; reason = f"scenario_failed:{scenario}"
      记录 result.json 路径到 progress.json
      break out to next page

# 把本页用到的 scenario_chain 写进 progress.json.pages[id].scenario_chain（记录用）
progress.pages[{page_id}].scenario_chain = ",".join(scenarios)
全部 scenario pass → App 已在目标状态，进入 Step 4.0 继续导航/截图
```

> **scenario-runner 单端模式依赖**：iOS 缓存命中时只跑 HarmonyOS 端，要求 `scenario_run.py` 能用 `--device harmonyos` 单独跑（不强制对端就绪）。若 scenario-runner 当前不支持，**必须先升级它**——此优化才能生效。

---

## 重要约定

- **首跑前**一次性建凭证档：`scenario_run.py --save-creds --device <ios|harmonyos> --package <pkg> --phone <手机号> --code <万能码>`（写 `spec/scenarios/creds.local.json`，**只录码、不实跑 login、不驱动设备**；两端账号不同各存一份）。之后 visual-verify 自动调用就全程无交互。迁移产物已带 `spec/baseline/dev_info.json`（契约参考文件）时，手机号/万能码可直接从中取值建档，这步免人工。
  > ⚠️ 顺序铁律：**不要**用 `--scenario login --device harmonyos` 来"录码"——那会先驱动 HMOS、越过 Phase 2 iOS基线。login 的首次实跑由 Phase 2（iOS trip_2）触发落在iOS端；HMOS scenario 被 `run_scenario_with_verify.py` 顺序闸（exit 60）拦在iOS全量基线完成之后。
- scenario-runner 的 `strategy: auto` 登录：首次 SMS + 缓存 prefs，之后秒级 static 注入，不会每页都重新走 UI 登录。
- **★鸿蒙登录建态失败（NEED_APP_FIX 且接口 HTTP 200 但业务 status 非 0）排障铁律（2026-08-15，codex 8 次盲猜未果 → 明文抓包 10 分钟定案）**：
  ⓪ **先量设备时钟，再读代码**（2026-08-15 新增，-401 的**第二个**独立成因）：签名里嵌了分钟桶
  `MD5(floor(tt/1000/60)+token)`，后端拿**自己的**时钟重算，容忍窗实测 ≈2 分钟（≤90s 过、≥120s 拒）。
  模拟器在宿主机休眠后必漂且不自愈（本轮实测慢 18.8 分钟 → 全链 -401，代码却一个字没改）。
  量法 `hdc shell date +%s` 与宿主 `date +%s` 相减；**hdc shell 是 uid 2000，改不了时间，只能重启设备**
  （鸿蒙模拟器 reboot 回来很慢且是共享资源，动手前先问用户）。
  ①' **建主机侧直连探针**（本轮最省时间的工具）：50 行 Python 在宿主机复算签名直打后端，一次往返 <1s，
  可随意扫描时间戳/字段序/UA/平台字段，不必"改码→编译→装机→点界面"绕一圈才验一个假设。
  注意**启动顺序是协议的一部分**：陌生 markId 直打 `/user/initUser` 会得 `-500 mediaNo is null`，
  按 app 真实顺序先调 `/app/config` 才正常。
  ① **先两端抓原文再动代码**：iOS走宿主机透明代理（`adb shell settings put global http_proxy 10.0.2.2:<port>`，事后 `:0` 还原）、鸿蒙在请求执行处临时 hilog（>~1KB 单条会丢，按 900 字节分段），拿同一接口的**完整头+体+响应体**逐字节 diff；
  ② **响应 `data.toastMsg` 绝不脱敏**（-401「权限校验未通过」= 看签名/头名；-1001「用户未登录」= 看上游 initUser 会话）——凭据安全靠不记 token 值，不靠抹掉方向标；
  ③ **A2H 高发缺陷类=常量"名/值混淆"**：iOS `Param._t="tt"`/`_s="ss"`（network/Ext.kt），翻译后若 header 写成字面量 `'_t'/'_s'` 则编译零报错、后端永远读不到签名头→必 -401。遇"协议看着全对但后端拒"先 grep 所有 header/参数名字面量对照iOS常量类的**值**；
  ④ **自检矩阵不能复用被检对象的假设**（codex 的契约矩阵用 `header['_s']` 验自己发的 `'_s'`＝同义反复，永远全绿）；校验基准必须来自另一端 wire；
  ⑤ 成功信号看最便宜的：sendSmsCode 成功→「获取验证码」进倒计时；bindMobile 成功→「我的」出现「账号管理」；
  ⑥ 走 app 真实 UI 流程验证，别直连接口。**通用方法论**（分诊表 / 协议逆向手册 / 时钟闸 / 缺陷分类 / 应答真值表 / 刷新缺陷 / 登出对称 / 迟到应答闸 / 验收清单）见 [`references/login-troubleshooting.md`](login-troubleshooting.md)——**先读它**；具体项目的 wire 真值（后端域名/签名 key/字段真值表/改动清单）属项目实录，见被测项目 `spec/scenarios/LOGIN_KNOWLEDGE.md`（有则同时读，示例值不要跨项目照抄）。
  ⑦ **协议通 ≠ 登录好**：`status=0` 只说明请求打通了，**必须逐条看界面**——登录后不切 tab 就该变成
  昵称+ID+已登录头像（登录/未登录是两张不同的默认头像）；退出登录后**杀进程冷启**仍须是登出态；
  已登录**杀进程冷启**昵称须立刻在（`initUser` 应答不带 `nickName`，只能从本地持久化种回）。
  ⑧ **鸿蒙没有 `onResume`**：iOS靠 `onResume()` 重读用户态刷新的页面，若对位页面落在 `Navigation`
  的**根内容**上（tab 首页常见），子页 push/pop 不会重建组件、`aboutToAppear` 不重跑 → 登录态永远是
  进页时的快照。修法是数据侧推 `AppStorage` + 页面 `@StorageProp` 响应式绑定，不要靠生命周期钩子。
  ⑨ **迁移时"额外加的自愈兜底"要专门复查**：一条失败应答不该无条件改全局身份。实测案例：启动期
  `/system/arrival` 先于会话恢复发出、必拿 -1001，无条件重建游客会话就会把刚恢复的登录态洗成游客
  （冷启即掉登录）。判据必须是"这条请求发出时的 token ≠ 当前 token 就丢弃"，
  而不是"当前是否已登录"（后者在真过期时也成立，会把恢复能力一起阉掉）。
- 多个 scenario 按顺序串行（例如 `["login", "upload_image"]` 先登录再上传图再截图）。

---

## Scenario-MUST 硬约束（不得绕过）

<HARD-GATE>

1. **任何 spec / scope 中要求的 `state_label` 都必须验证**。**禁止**仅以"需要 picker / 系统弹窗 / 复杂交互"为理由把状态推给"人工验证保留"。
2. 主代理判定某状态需要前置数据（图片/登录/已上传记录等）时，**必须**：
   - (a) 先查 `spec/visual-verify/page_scenarios.json` 是否已声明对应 scenario
   - (b) 未声明 → **必须派 `scenario-builder` agent 学习并注册新 scenario**（学习归 builder，
     scenario-runner 只回放；sub-agent 无派发权 → 写缺口单由主会话派），**不得**直接 skip
   - (c) builder 学习失败 → 收其 NEED_* 报缺（附 ≥3 次实质不同尝试留痕），校验证据结构合格后
     才走 alignment-rules.md §3 升级用户；证据不合格打回 builder 重跑
3. 状态升级"人工验证"必须满足以下任一条件，且需在 progress.json 记录证据：
   - scenario-runner 反复 ≥3 次失败 + 失败 stderr/screenshot
   - 用户在对话中明确说"这个状态我自己测，跳过"
   - 缺乏目标设备能力（如 NFC 硬件、5G 网络）— 需 `hdc shell` / `adb shell` 命令尝试结果作为证据
4. 缺以上证据视为偷懒，skill 失败，必须重跑该 state_label 的 scenario 调用。

</HARD-GATE>

---

## 已知场景类型清单

不全，遇到新需求 **必须**先派 scenario-builder 学习实现（runner 只回放已有配方），不能因为"清单没有"就 skip。

| scenario | 用途 | 实现方式 |
|---|---|---|
| `login` | 已登录态 | static token 注入 / SMS 验证码 |
| `upload_image` | 相册有图 + 触发 picker | hdc/adb push 图片到 /sdcard/Pictures，点击 picker 入口后由 scenario-runner 完成系统选图 |
| `upload_image_already_done` | 已有上传记录的态（直接展示已上传内容，跳过 picker 触发） | 直接写 prefs/SQLite 注入"已上传"状态 |
| `goto_xxx_page` | 已导航到深层页 | 模拟点击链路 |
| `mock_data_xxx` | 注入测试数据（订单/作品/收藏） | preferences/RDB 写入 |
| 自定义 | 其他 | 写 YAML 注册到 scenario-runner，**禁止**绕过 |
