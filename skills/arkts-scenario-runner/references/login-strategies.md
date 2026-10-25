> **iOS 源输入**：读取 Swift/Objective-C、SwiftUI/UIKit、Xcode 工程及原生资源；实际源构建与设备观测依赖可用的源平台环境。鸿蒙侧构建和验收保持原流程。源侧操作详见 `a2h-spec/references/native-input.md`。

# Login Strategies

本文件为 `inject_token` action 的实现参考。当前落地：`auto`（推荐）、`static`、`sms`。`oauth` 保留待实现。

## Strategy: `auto`（推荐，默认）

最省事的路径，零配置。逻辑：

1. 找 `spec/scenarios/fixtures/prefs_logged_in/<package>_user_prefs`
2. 存在 → 走 `static`（秒级，直接 push 文件到沙箱并冷启动）
3. 不存在 → 走 `sms` 首次登录，**成功后自动把 user_prefs 拉回缓存**，以后都走 static 快速路径

用户只需：
- 第一次运行时交互式输入手机号 + 万能验证码（存到 `<project>/spec/scenarios/creds.local.json`，按 bundleName + device 存；自动加 .gitignore）
- 之后什么都不用做

YAML：
```yaml
- action: inject_token
  strategy: auto
  package: com.example.demoapp
  ability: EntryAbility
  activity: .MainActivity
  # sms_flow 可选 —— 只在默认 selector 匹配不上时补
  sms_flow:
    enter_login:   { text: "我的" }
    enter_login_2: { text: "登录" }
    phone_input:   { resource_id: "phone_input" }
    send_code_btn: { text: "获取验证码" }
    code_input:    { resource_id: "code_input" }
    submit_btn:    { text: "登录" }
    home_signal:   "首页"
```

---

## Strategy: `static`（当前实现）

### 原理
绕过 UI 登录流程。把一份**已签发的有效 token**（通过人工登录测试账号一次性获得）直接写到 App 的持久化存储，App 冷启动后读配置文件认为自己已登录。

### 为什么可行
本项目（AGENTS.md）明确 token 在三处同步：
- `AppStorage['token']`
- `UserPreferences`（键见 `PreferenceKeys.ets`）
- `lib_network.UserData.getInstance()`

只要这三处都写对，App 的 TokenInterceptor 就会把 token 挂到所有请求上，业务层就认为"已登录"。

### 前置资产

**`spec/scenarios/fixtures/test_token.json`**（人工准备一次）：
```json
{
  "token": "<真实从测试账号登录后抓到的 token>",
  "refresh_token": "<可选>",
  "userId": "<userId>",
  "phone": "138****0000",
  "nickname": "测试用户",
  "vipLevel": 0,
  "expire_at": 1767225600
}
```

**获取方式**（一次性）：
1. 模拟器上手工完成登录
2. HarmonyOS：`hdc shell cat /data/app/el2/100/base/com.example.demoapp/haps/entry/files/preferences/user_prefs`
3. iOS：`adb shell run-as com.example.demoapp cat shared_prefs/user_prefs.xml`
4. 提取 token + 关键字段存为 JSON

> **安全提醒**：`fixtures/test_token.json` 是测试账号的真实 token，加到 `.gitignore`，别提交到仓库。

### 注入手段（三选一）

#### 手段 A：push Preferences 文件（首选，最稳）

**思路**：把一份预置的、已登录态的 Preferences 文件直接覆盖到 App 沙箱，重启 App。

```text
[历史源平台示例：不适用于 iOS，不可执行。iOS 源设备/构建按本文件适配及 native-input 协议；目标 hdc/hvigor 检查仍须实际执行。]
# HarmonyOS
hdc shell am force-stop com.example.demoapp
hdc file send spec/scenarios/fixtures/prefs_logged_in/user_prefs \
  /data/app/el2/100/base/com.example.demoapp/haps/entry/files/preferences/user_prefs
hdc shell aa start -a EntryAbility -b com.example.demoapp

# iOS（需要 root 或 run-as）
# 原源平台历史命令（iOS 按本文件适配说明执行）: adb shell am force-stop com.example.demoapp
# 原源平台历史命令（iOS 按本文件适配说明执行）: adb push spec/scenarios/fixtures/prefs_logged_in/user_prefs.xml /tmp/user_prefs.xml
# 原源平台历史命令（iOS 按本文件适配说明执行）: adb shell run-as com.example.demoapp cp /tmp/user_prefs.xml shared_prefs/user_prefs.xml
# 原源平台历史命令（iOS 按本文件适配说明执行）: adb shell am start -n com.example.demoapp/.MainActivity
```
**陷阱**：非 root 设备写不到沙箱。HarmonyOS 模拟器默认可用 hdc file send 写入用户应用沙箱的 files 目录；iOS 必须用 `run-as`（debug build）或 root。release 包走不通。

#### 手段 B：Debug Entry 启动参数（`strategy: debug_entry`，已实现）

**为什么推荐 B 而不是 A（手段 A = push prefs）**：
- 手段 A 依赖沙箱写权限：**非 root 真机 / 非 debug iOS 包写不进去**，static fast path 直接挂
- prefs 文件格式 iOS/鸿蒙不兼容（XML vs @ohos.data.preferences 二进制），跨端不能复用
- 只 push prefs 只写了三处中的一处（UserPreferences），靠冷启动读回来——任何字段对不上 TokenInterceptor 就不挂 token
- B 方案 **10 行代码**在 EntryAbility 里主动写三处，确定性强，不依赖文件系统权限

**思路**：在 App 里预埋一个 debug-only 的启动入口，识别特定 Want 参数，把传入的 token 直接写到三处（对齐 AGENTS.md 的 token 三路同步：`AppStorage['token']` + `UserPreferences` + `lib_network.UserData`）。

##### 账号依赖：一次性登录即可，后续免手机号免验证码

debug_entry 只解决"把 token 塞进 App"，**token 本身必须由后端真发才能通过服务端校验**（你的 TokenInterceptor 挂上去后，任何业务接口都会被验）。所以 token 来源二选一：

**方式 1：人工登录一次导出 token（推荐，零后端依赖）**

1. 任何端登录一次测试账号（鸿蒙 SMS 流程 / iOS 已有登录页 / 甚至生产包临时登录）
2. 导出 token：
   ```bash
   # 鸿蒙（debug 包或开发态设备）
   hdc shell cat /data/app/el2/100/base/com.example.demoapp/haps/entry/files/preferences/user_prefs
   # iOS debug 包
   # 原源平台历史命令（iOS 按本文件适配说明执行）: adb shell run-as com.example.demoapp cat shared_prefs/user_prefs.xml
   ```
3. 把 token 字段抠出来存到 `spec/scenarios/fixtures/test_token.json`：
   ```json
   { "token": "eyJhbGc...", "userId": "12345", "expire_at": 1767225600 }
   ```
4. **把这个文件加到 `.gitignore`**，token 是敏感凭证
5. 之后所有 scenario 跑 `strategy: debug_entry` + 指向这个 `token_file`，**全程不需要再输手机号/验证码**
6. token 过期（一般几天到几周）再手动刷一次——推荐在 `test_token.json` 里记 `expire_at`，runner 可以提前提醒

**方式 2：后端签发测试长效 token（彻底免人工，需后端配合）**

让后端测试环境加个 whitelist，给某个固定 test userId 签一个长期有效 token，直接写进 `test_token.json`。以后完全不用人工登录。

##### App 侧最小改动（一次性）

`entry/src/main/ets/entryability/EntryAbility.ets`：

```typescript
import { AbilityConstant, UIAbility, Want } from '@kit.AbilityKit'
import { BuildProfile } from '@native/BuildProfile'       // hvigor 自动生成
import { UserPreferences } from '<your path>/UserPreferences'
import { PreferenceKeys } from '<your path>/PreferenceKeys'
import { UserData } from '@example/lib_network'

export default class EntryAbility extends UIAbility {
  onCreate(want: Want, _launchParam: AbilityConstant.LaunchParam) {
    // ... 原有初始化
    this.tryInjectDebugToken(want)
  }

  onNewWant(want: Want, _launchParam: AbilityConstant.LaunchParam) {
    this.tryInjectDebugToken(want)
  }

  // TODO[release]: 上架前删除此方法 + onCreate/onNewWant 两处调用点。
  //                定位残留:  grep -rn "debug_inject_token" entry/
  private tryInjectDebugToken(want: Want): void {
    // release 签名包的 appProvisionType 必然是 'release'，且该字段由证书决定、
    // 改 BuildProfile 常量改不掉它。走到这里 = 忘删后门 = 冷启动直接 crash，
    // 红旗摆在眼前，比静默留后门好。
    if (this.context.applicationInfo.appProvisionType === 'release') {
      throw new Error('dev-only injector reached in release build')
    }
    if (!BuildProfile.DEBUG) return
    const tok = want.parameters?.['debug_inject_token'] as string | undefined
    if (!tok) return
    AppStorage.setOrCreate('token', tok)
    UserPreferences.getInstance().putSync(PreferenceKeys.TOKEN, tok)
    UserData.getInstance().setToken(tok)
    console.info(`[debug_entry] token injected len=${tok.length}`)
  }
}
```

**上架前清理清单**（只要忘一条，release 启动就 crash，不会静默留后门）：
1. 删除 `tryInjectDebugToken` 方法 + `onCreate` / `onNewWant` 两处调用
2. `grep -rn "debug_inject_token" entry/` 必须零命中
3. （可选）给 hvigor release 构建挂 pre-build 脚本跑上面这条 grep，命中就 `exit 1`

要点：
- **双闸设计**：`BuildProfile.DEBUG` 是编译期常量（debug/release 构建模式），`appProvisionType` 是签名期属性（由证书决定）。两者一起把"误发布 debug 包"和"忘删代码的 release 包"都兜住
- 同时处理 `onCreate`（冷启动）和 `onNewWant`（热启动 / App 已在后台时 aa start 走这个回调）
- 字段名固定为 `debug_inject_token`，scenario-runner 按此名发送

##### YAML 调用

```yaml
- action: inject_token
  strategy: debug_entry
  package: com.example.demoapp
  ability: EntryAbility
  token_file: spec/scenarios/fixtures/test_token.json   # { "token": "..." }
  verify_signal: home_hint                                # 可选: 注入后 wait_for 的文本/ID
  verify_timeout_ms: 6000
```

runner 行为：
1. 读 `token_file` 里的 `token` 字段
2. `hdc shell aa force-stop <pkg>` 然后 `aa start -a <ability> -b <pkg> --ps debug_inject_token '<tok>'`
3. （可选）`wait_for` `verify_signal` 确认已登录态
4. 若 `verify_signal` 未命中 → 退化为 static 或报 `app_not_debuggable`（release 包会静默丢弃参数）

##### 校验 App 是否埋了这个入口

```bash
# 发一个假 token，App 日志里出现 [debug_entry] 就说明埋成功
hdc shell aa start -a EntryAbility -b com.example.demoapp --ps debug_inject_token 'TEST_PROBE'
hdc shell hilog -t EntryAbility | grep debug_entry
```

##### 代价 vs 好处

- 代价：App 里加 ~15 行代码，release 构建自动剥离
- 好处：不依赖沙箱写权限（避开真机 root 要求），不依赖 iOS/HarmonyOS prefs 格式对齐，三处一次写齐，**登录页未实现也能跑登录态测试**

#### 手段 C：UI 自动化走完整登录流程（下策）

走真实登录 UI（输手机号、填验证码、点登录）。慢，且短信验证码是外部依赖。只在手段 A/B 都不可用时兜底。

### 推荐落地顺序
1. **首选手段 B**（debug entry）—— 10 行代码不依赖沙箱权限，release 自动剥离
2. 手段 A（push prefs）只在"根本不能改 App 源码"时用，要求 root 真机 / debug iOS 包
3. 手段 C（UI 自动化）兜底

---

## Strategy: `sms`（已实现，通常由 `auto` 内部调用）

手机号 + 万能验证码登录。

### 依赖
后端提供**万能验证码**。不同项目 / 不同 App 可能用不同账号，所以 creds 按 **项目目录** + **bundleName** + **device** 三层分键。

**存储位置（v3）：** `<project_root>/spec/scenarios/creds.local.json`

- 文件名带 `.local.` 中缀 = 「不上传仓库」标记
- 首次写入时脚本会自动把规则追加到项目 `.gitignore`
- 文件顶层带 `_marker` 字段提醒不可上传
- 提包前一键清理：`python scenario_run.py --purge-creds`

> 旧版本 `~/.arkts-scenario-runner/creds.json` 仍兼容读（找不到新路径时降级查），方便迁移。

```json
{
  "com.example.demoapp": {
    "ios":   { "phone": "13800000000", "code": "888888" },
    "harmonyos": { "phone": "13900000000", "code": "888888" }
  },
  "_marker": {
    "do_not_ship": true,
    "purge_cmd": "python <scenario_run.py path> --purge-creds",
    "note": "Local test credentials. ..."
  }
}
```

- 首次运行 `scenario_run.py --scenario login --package <pkg>` 时，脚本发现缺失 creds 就交互式询问，答完就保存（chmod 600，自动加 .gitignore）
- 也可命令行一次性覆盖：`--phone 138... --code 888888`
- 不同设备建议用不同测试账号，避免 iOS / HarmonyOS 同号互踢

### 提包前清理（CI 推荐）

```bash
# 一键删除本项目下的 creds
python <path>/scenario_run.py --purge-creds

# 或在 CI release 流水线里加一道防呆 grep
find spec -name "creds.local*" -print -exec false \; || {
  echo "ERROR: creds.local.* still present, refusing to package" >&2
  exit 1
}
```

### UI 自动化流程
由 `_inject_token_sms()` 实现：kill → launch → 按 `sms_flow` selector 依次点击/输入 → `wait_for home_signal` → 自动 `hdc pull user_prefs` 回缓存。

### 失败兜底
UI 结构和默认 selector 对不上 → `_rescue_capture_prefs()` 交互式引导用户手工登录一次，再自动拉回 prefs 建档。

---

## Strategy: `oauth`（预留）

一键登录 / 第三方（微信、华为账号）。

### 难点
第三方登录的 token 回调走外部 App（微信/账号中心）。模拟器上这些 App 通常不存在或未登录，所以**不能走真实 OAuth 流程**。

### 两条可行路径

**路径 1：deep link 注入 OAuth 回调**
App 侧处理完 OAuth 的回调通常是通过 scheme（如 `com.example.demoapp://oauth?code=xxx`）。自动化里直接发：
```bash
hdc shell aa start -U "com.example.demoapp://oauth?code=FAKE_CODE&state=..."
```
前提是后端能对 `FAKE_CODE` 发有效 token（测试环境 whitelist）。

**路径 2：跳过 OAuth 直接走手段 B**
第三方登录成功后本质还是拿到 token 塞进去，所以**复用 `static` 策略**：
```yaml
- action: inject_token
  strategy: static
  token_file: spec/scenarios/fixtures/oauth_huawei_token.json
```
就是 `test_token.json` 的一个变体，表示"通过华为账号登录拿到的 token"。

### 推荐
路径 2 在绝大多数测试场景下足够。路径 1 只有在需要验证 OAuth 回调代码路径本身时才用。

---

## 通用：token 过期怎么办

测试 token 终会过期。策略：
- 每次 `inject_token` 前先用 token 调一个轻量接口（如 `/user/info`）探活
- 失败 → 提示人工重新准备 `test_token.json`，本 skill 不实现自动刷新（刷新机制会扩散复杂度，测试场景不值得）
- 也可以在 `test_token.json` 里保存 `refresh_token` + `expire_at`，executor 发现过期时调刷新接口。这是可选增强，默认不做。
