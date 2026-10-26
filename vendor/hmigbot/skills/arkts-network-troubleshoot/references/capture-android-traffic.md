# 抓取 Android 真实请求日志

> Phase 0.3 的展开。目标：把 Android 端真实运行的 request + response 原文落到 `spec/baseline/sample-requests.md`，并按 endpoint key 回填 `api-inventory.json` 的 `runtime` 段。
> 顺序：先过 3 道前置闸门 → 再按 3 种方法之一抓取 → 落表 + 回填 runtime。
> **冷启动场景可全自动**：方法 A 的脚本化抓取 + `extract_startup_requests.py` 提炼，无需人工点屏。

## 何时需要抓 / 何时不用抓

| 你要确认的东西 | 抓不抓 |
|---|---|
| URL 路径、body 字段名与结构、签名算法步骤 | **不用抓** —— 读 Android 源码 / `spec/baseline/api-inventory/api-inventory.json` 就够 |
| 字段真实类型（`userId` 是 int 还是 string）、默认值（`-1` vs `0`） | **要抓** |
| 响应包装层级（`{code,msg,data}` vs `{status,toastMsg,data}` vs `{data:{status}}`） | **要抓** |
| header 真实拼写大小写（`token` vs `Token`） | **要抓** |
| 业务码真实语义（`status:0` 成功 vs `code:0` 成功） | **要抓** |
| signature 真实字节、platformInfo 公参实际填充值（Phase 3 字节对账） | **要抓**，且必须方法 C |

一句话：**静态结构看代码，运行期事实抓真包**。

## 前置检查：3 道闸门

抓包前依次过闸，任一不过先解决再抓，否则白忙一场。

### 闸门 1 — 设备 / 模拟器 存在且在线

```bash
adb devices
```

| 输出 | 含义 | 对策 |
|---|---|---|
| 空（只有表头 `List of devices attached`） | 没有设备 | 真机：插 USB；模拟器：Android Studio → Device Manager 启动一个 AVD |
| `<serial>  unauthorized` | 真机已连但未授权 | 在设备上确认弹窗「允许 USB 调试」 |
| `<serial>  offline` | 连接异常 | `adb kill-server && adb start-server` 重连，或重插 USB |
| `<serial>  device` | ✅ 就绪 | — |

- 区分真机 / 模拟器：`adb shell getprop ro.kernel.qemu` 返回 `1` 即模拟器。
- 真机额外前提：已开「开发者选项」+「USB 调试」。
- 多设备同时连：之后每条 `adb` 命令都要加 `-s <serial>`。

### 闸门 2 — 目标 App 已安装、debug 构建、能跑到业务

```bash
# 1) 源码里的 applicationId 基值 + 后缀（debug 包常带 .debug 后缀！）
grep -n 'applicationId\b\|applicationIdSuffix' android_src/app/build.gradle*
# 2) 别只信源码 —— 直接列设备上实际装的第三方包，按 App 名 / 厂商关键词锁定真实包名
adb shell pm list packages -3 | grep -i <关键词>
# 3) 进程在跑？（有 PID 输出 = 运行中）
adb shell pidof <实际包名>
# 4) 是 debug 构建？（有输出含 DEBUGGABLE = debug 包；无输出 = release 包）
adb shell dumpsys package <实际包名> | grep -i debuggable
```

**「准确」的第一关 —— 包名要解析对**：debug 构建常用 `applicationIdSuffix ".debug"` 把包名改成 `<applicationId>.debug`，源码 grep 到的基值不一定是设备上真实装的那个。务必用第 2 步 `pm list packages -3`（`-3` 只列用户安装的第三方包）核对；后续所有 `adb` 命令都用核对后的真实包名，否则 `pidof` / 启动 / 抓日志全指向错对象。

- 没装 → 用 Android Studio Run，或 `adb install <apk>`。
- 没在跑 → 见方法 A 用 `adb` 脚本化冷启动；要抓的接口若在 UI 深层，需先进到对应页面。
- **不是 debug 构建** → 方法 A 的日志拦截器多半被 `if (BuildConfig.DEBUG)` gating 掉、方法 B 的 Network Inspector 无法 attach。换 debug 包，或只能用方法 C。

### 闸门 3 — Android Studio 就绪（仅方法 B 需要）

- Android Studio 已安装，且能打开 Android 工程（根目录有 `settings.gradle(.kts)`）。
- Gradle sync 成功（底部状态栏无红色 error）。
- 有可运行目标（闸门 1 已过）。
- Network Inspector 面板可用：`View → Tool Windows → App Inspection → Network Inspector` tab。

## ⚠ 隐私 / 授权弹窗门 —— 启动抓包前必读

国产 App 冷启第一屏几乎都是**隐私协议弹窗**。**用户没点「同意」之前，启动网络链一条都不发**
（config / initUser / 首启上报全部被 gating 掉；HMOS 侧表现为 hilog `initThirdSdk skip: ...AGREE... != 1`）。
所以「冷启动 = 自动抓到启动类接口」这个假设**在有隐私门时不成立** —— 必须先过门。

**A. 注入点击（推荐，可半自动）**

```bash
# 1) 冷启后截图，定位「同意」按钮
adb exec-out screencap -p > shot.png                                  # Android
export MSYS_NO_PATHCONV=1                                             # HMOS：见 grep-cheatsheet.md
hdc shell snapshot_display -f /data/local/tmp/s.jpeg && hdc file recv /data/local/tmp/s.jpeg ./s.jpeg
# 2) 读图算「同意」按钮真实像素坐标（注意截图分辨率 vs 显示缩放的换算比）
# 3) 注入点击
adb shell input tap <x> <y>                                           # Android
hdc shell uinput -T -c <x> <y>                                        # HMOS
# 4) 过门后 startup 网络链才发出 → 再按方法 A/C 抓
```

**B. 预置已同意标记**：若 App 把"已同意"存在 Preferences/MMKV，可在抓包前直接写入该键值跳过弹窗
（HMOS 偶尔可经 hdc 改沙箱文件；多数情况不如方法 A 稳）。

> `pm clear` 或首次安装后第一次冷启**一定**遇到隐私门 —— 要抓「真·首启」(firstStart / 首次 config)
> 时尤其注意先过门。Phase 6 双端对账时，Android 基线和 HMOS 各自都要过一次门。

## 3 种抓取方法

### 方法 A：App 自带日志拦截器 → adb logcat（首选，可脚本化）

迁移项目几乎都有 Android 源码，App 通常自挂了 HTTP 日志拦截器（OkHttp `HttpLoggingInterceptor` 或自定义）。先找日志 tag：

```bash
# 1) 找 OkHttp 标准日志拦截器（默认 logcat tag = OkHttp）
grep -rn 'HttpLoggingInterceptor\|Level.BODY\|Level.HEADERS' android_src --include='*.kt' --include='*.java' | grep -v '/build/'
# 2) 找自定义拦截器文件，打开看它 Log.x(TAG, ...) 用的 TAG 常量
grep -rln 'Interceptor\|chain.proceed' android_src --include='*.kt' --include='*.java' | grep -v '/build/'
```

拿到 tag 后，**冷启动抓取 —— 全程纯 adb，无需人工点屏**：

```bash
PKG=<闸门 2 核对出的真实包名>
adb logcat -c                                  # 清旧缓冲
adb shell am force-stop "$PKG"                 # 杀进程，保证下次是冷启动
# 要抓「首次启动」接口（协议上报 / 首启统计）再清数据：adb shell pm clear "$PKG"
adb shell monkey -p "$PKG" -c android.intent.category.LAUNCHER 1   # 拉起 launcher 入口
sleep 20                                       # 等启动类请求发完（按 App 启动耗时调，一般 15-30s）
adb logcat -d -v threadtime --pid="$(adb shell pidof -s "$PKG")" -s OkHttp:V > capture.log
```

- `monkey ... 1` 发一条 launcher intent 拉起 App，不必知道入口 Activity 名（也可 `adb shell am start -n "$PKG"/<Activity>`）。
- `adb logcat -d` dump 当前缓冲后立即退出，无需管理后台进程。
- `--pid=...` 锁定目标 App 进程 + `-s OkHttp:V` 锁定拦截器 tag —— 双重过滤，保证 `capture.log` 只有目标 App 的 HTTP 日志（这是「准确」的关键，否则别的 App 同名 tag 会混入）。
- 必须 `-v threadtime`（带线程号）：冷启动多请求并发，提炼脚本靠线程号把交叉的日志行归位。

冷启动会自动发出 `/app/config`、`/user/initUser`、splash 上报等**启动类接口** → 全进 `capture.log`。

#### 从 capture.log 提炼「有效请求」

`capture.log` 仍是原始流（多请求并发交叉 + 不完整记录 + 可能混入三方 SDK 噪声）。用配套脚本 [`scripts/extract_startup_requests.py`](../scripts/extract_startup_requests.py) 提炼成可直接对账的清单：

```bash
python <本 skill 目录>/scripts/extract_startup_requests.py capture.log --host <自有后端域名>
```

**「有效请求」定义**：① **完整** —— request 块与 response 块成对（能对账请求体 + 响应体）；② **业务域** —— 命中 `--host` 指定的自有后端（滤掉推送 / 统计 / 广告等三方 SDK 调用）；③ **去重** —— 同 `method + path` 只留一条样本。

脚本会先列出日志里出现的所有 host 供你确认业务域，再输出整理好的请求记录（直接贴进 `sample-requests.md`），并把「跳过的不完整 / host 过滤掉 / 去重」条数汇总出来。不传 `--host` 则输出全部完整记录。适配 OkHttp `HttpLoggingInterceptor`（`Level.BODY`）默认格式；自定义拦截器改脚本顶部 `MARK_*` 正则。

> 不完整记录（有请求无响应）多半是 `sleep` 窗口太短截断了 —— 把 `sleep` 调长重抓即可。

**深层接口抓不到**：登录 / 业务 / 支付类接口要先在 UI 里操作才会发出，纯 adb 拉起 App 抓不到 —— 见下方「skill 能自动做到哪一步」。

**局限**：单条 logcat 约 4000 字符上限，大 body 会断行或截断（大响应改用方法 B/C）；**只打拦截器选择输出的字段 —— 绝大多数 App 自带日志只打 path / body / response，不打 request headers**（要对比签名头 `ss`/`tt`、公参头必须用方法 C）；release 包通常 gating 掉拦截器（见闸门 2）。

### 方法 B：Android Studio Network Inspector（要完整 headers / 大 body）

`View → Tool Windows → App Inspection → Network Inspector` tab，以 Debug 方式运行 App，Inspector 自动附着，逐条列出请求，点开看完整 URL / headers / request body / response body / 耗时，可导出 HAR。

- **优势**：HTTPS 明文可见（框架层 hook，免装证书）；body 不截断。
- **前提**：闸门 3 + 设备 API 26+（Android 8.0+）+ App debuggable。
- **局限**：实时抓，必须在请求发生前打开 Inspector；App 进程被杀后历史清空；**不可脚本化**（IDE GUI 面板，只能人工操作）。

### 方法 C：抓包代理 Charles / Fiddler / mitmproxy（要真实字节）

设备级中间人代理，抓 App 在网络上发出的**原始字节** —— 这是 Phase 3 signature 字节对账唯一可靠的事实源（方法 A/B 看到的是框架 / 拦截器重组后的内容，不一定是线缆上的真实字节）。

1. 电脑跑 Charles / mitmproxy，记下 `电脑IP:端口`。
2. 设备与电脑在同一 WiFi。
3. 设备 WiFi 高级设置 → 手动代理 → 填 `电脑IP:端口`（模拟器也可用启动参数 `-http-proxy`）。
4. **HTTPS 必做**：设备装并信任代理工具的 CA 证书；Android 7+ 还需 App 的 `network_security_config.xml` 显式信任 `<certificates src="user"/>`，否则 App 不信任用户证书、只抓到握手失败。能改源码就临时加上重打 debug 包。
5. App 不能开 certificate pinning（`CertificatePinner` / `network_security_config` 的 `<pin-set>`），否则代理握手被拒。

**后端是明文 HTTP（`http://`）时大幅简化**：上面第 4（CA 证书）、第 5（pinning）**都不需要** —— 明文流量代理可直接读。此时无需装 Charles/mitmproxy，用本 skill 自带的极简 Node 转发代理即可（脚本 [`scripts/http-capture-proxy.js`](../scripts/http-capture-proxy.js)，打印每条请求完整 headers+body）：

```bash
node <本 skill 目录>/scripts/http-capture-proxy.js 8888       # host 上起代理（端口可改）
adb shell settings put global http_proxy 10.0.2.2:8888        # 模拟器指向 host（10.0.2.2=宿主）
#   ... force-stop + 冷启动 App，代理 stdout 打印每条请求的 method/headers/body ...
adb shell settings put global http_proxy :0                   # ⚠ 抓完务必还原，否则其它 App 也走代理
```

> 同一个代理也能抓 HMOS 侧的完整请求头：把 HMOS 设备 WiFi 代理指向同一 `host:8888`。hilog 只含应用层 `req.headers`（HttpLogInterceptor 打的），传输层头（user-agent / host 等）只有代理看得到 —— 两端都过同一代理才能逐字节对比 headers。

- **优势**：真实字节，能对账 signature / 公参 / 真实响应包装。
- **局限**：配置成本最高；遇到 pinning 或 App 不信任 user CA 时抓不到 HTTPS；**不可脚本化**（代理配置与抓包查看均为 GUI 操作）。

## 方法选择

**先看后端协议 —— 这决定首选方法：**

- **后端是明文 `http://`** → **首选方法 C**（本 skill 自带的 Node 转发代理）。明文流量代理零 CA 配置、
  一步到位拿到 **完整 headers（含 ss/tt/ee 签名头）+ 完整 body + 响应**、无 logcat 4000 字符截断、
  输出已结构化（连 `extract_startup_requests.py` 都省了）。比方法 A 更全更省事 —— **直接上 C，不必先试 A**。
- **后端是 `https://`** → 按下表 A → B → C 渐进（C 需装 CA / 处理 pinning，成本最高）。

| 你要的东西 | 选哪个 |
|---|---|
| URL / body 字段结构 | 不用抓，读源码 / `api-inventory.json` |
| 启动类接口（config / initUser / splash 上报）的响应结构、字段类型 | http 后端 → 方法 C；https 后端 → 方法 A 冷启动脚本 |
| 登录 / 业务 / 支付类接口的响应结构、字段类型 | http 后端 → 方法 C；https 后端 → 方法 A（人工触发）够，body 大改用 B |
| 完整 headers + 大 body + 导出 HAR | 方法 B（http 后端直接 C 即可） |
| signature 真实字节、公参实际值、Phase 3 字节对账 | 方法 C（http 后端零配置；https 后端需装 CA） |

默认顺序：**http 后端 → 直接 C**；**https 后端 → A（零配置先试）→ 不够上 B → 签名对不齐上 C**。

## skill 能自动做到哪一步

跑本 skill 的 agent 只能执行命令行（`adb`），不能点屏、不能驱动 GUI。能力边界：

| 环节 | 能否纯 adb 自动 |
|---|---|
| 闸门 1/2 检查（设备在线、包名、进程、debuggable） | ✅ 能 |
| 冷启动 App（`force-stop` + `monkey` / `am start`） | ✅ 能 |
| 抓**启动类**接口（config / initUser / splash 上报） | ⚠️ 半自动 —— **无隐私门**时方法 A 脚本全自动；**有隐私门**时需先截图 + 注入点击「同意」（见上方「隐私门」节）再抓 |
| 抓**登录类**接口（发码 / 验证码登录 / 三方授权） | ❌ 需人工 —— 要在 UI 输手机号、点按钮 |
| 抓**业务类**接口（列表 / 详情 / 上传 / 下载） | ⚠️ 部分 —— 简单页可 `am start` 直达 Activity；深层流程需人工 |
| 抓**支付类**接口 | ❌ 需人工 —— 要走下单 + 调起 SDK |
| 方法 B（Network Inspector）/ 方法 C（Charles） | ❌ GUI 工具，全程人工 |

`adb shell input tap <x> <y>` / `input text <str>` 能半自动化简单流程，但基于屏幕坐标、脆弱，多数场景人工点更快更稳。

**结论**：本 skill 能自动闭环「核对设备 / 包名 → 冷启动 App → 抓日志 → 提炼出有效请求清单」—— **前提是没有隐私门**；有隐私门时，过门那步（截图 + 注入点击「同意」）需 agent 半自动完成（见「隐私门」节），其余仍自动。登录 / 业务 / 支付类接口因为要 UI 交互，skill 只能把抓取通道架好（`adb logcat` 跑起来）并同步收日志，触发动作由人在 App 里点。

## 抓完之后

挑 ≥5 条核心接口（启动 / 登录 / 业务 / 上传 / 支付各 1-2 条），把 request line + headers + request body + response body 原文落到 `spec/baseline/sample-requests.md`（模板见 [templates/spec-baseline.md](templates/spec-baseline.md)）。这是 Phase 1 对账、Phase 3 字节验证、Phase 4 unwrap 的共同事实源。启动类那几条可直接用 `extract_startup_requests.py` 的输出贴入；登录 / 支付类人工抓后补齐。

**同时回填 contract `runtime` 段**：若工程内有 `spec/baseline/api-inventory/api-inventory.json`，`sample-requests.md` 是人类可读留存，但对账要的是结构化事实 —— 每抓到一条接口，按 endpoint key（`"<HTTP方法> <path>"`）回填该 endpoint 的 `runtime` 段：响应包装层级、业务码字段、字段真实类型 / 默认值、请求头真实拼写、签名头字节。抓不到的 endpoint（需 UI 触发 / 设备未就绪）`runtime` 留 `null`。详见 [phases.md](phases.md) Phase 0.3「抓包结果回填 contract runtime 段」，`runtime` 段 schema 见 [output_schema.md](../../android-api-inventory/references/output_schema.md)。回填后即可进 Phase 1.7 产 static↔runtime DIFF。

**分层 md 同步**：若 `api-inventory` 采用分层 md 形态（工程内存在 `common.md` + `apis/*.md`，见 [output_schema.md](../../android-api-inventory/references/output_schema.md)「api-inventory 文档结构」），回填 `api-inventory.json` 后须**同步刷新** `apis/*.md` 里对应 endpoint 的 runtime 标记：`⬜ static-only` → `✅ verified`（与 static 一致）或 `⚠️ mismatch`（有差异 —— 差异就近标注并链到 `api-contract-diff.md`）。md 集是 `api-inventory.json` 的投影，json 改了 md 要跟上。

## 与 HMOS 侧冷启动对比（Phase 6 用，不是 Phase 0.3）

> Phase 0.3 抓 Android 基线时，HMOS 网络层还没实现 —— 没有可比对象，**别在 Phase 0.3 做对比**。
> 等 HMOS 拦截器 / SignUtil / HttpClient 写完、进入 Phase 6 联调，再回到这里：冷启动 HMOS App，把它的启动请求与 Android 基线逐接口对账。这是启动链路最硬的证据。

HMOS 冷启动抓取是 adb 流程的 hdc 镜像（同样纯命令行、可脚本化）：

```bash
BUNDLE=<HMOS bundleName>
hdc shell aa force-stop "$BUNDLE"                       # 杀进程
hdc shell hilog -r                                      # 清 hilog 缓冲
hdc shell aa start -b "$BUNDLE" -a EntryAbility          # 冷启动
sleep 20                                                # 等启动类请求发完（多数 App 冷启后 1-3s 内即发完，sleep 是容错余量，可按 hilog 实际出现时刻缩短）
hdc shell hilog -x | grep -E 'HTTP >>>|HTTP <<<' > hmos_capture.log   # -x dump 后退出
```

- 前提：HMOS 端 `AppStorage('isDebug')=true`，否则 HttpLogInterceptor 静默不打日志（见 Phase 2.1）。
- `extract_startup_requests.py` 也能提炼 `hmos_capture.log` —— 把脚本顶部 `MARK_*` 正则改成你 HttpLogInterceptor 的输出格式即可（hilog 行首与 logcat threadtime 接近，前缀解析无需改）。

**逐接口对账表**：左边 Phase 0.3 抓的 Android 基线（`sample-requests.md`），右边 HMOS 实际：

| 启动接口 | 发出? | URL path | request body | response |
|---|---|---|---|---|
| /app/config | 两边都发 | 前缀一致 | 字段集 + 类型一致 | status/data 正确 unwrap |
| /user/initUser | … | … | platformInfo 公参齐全、签名一致 | token/userId 非空 |
| splash 上报 / 其它 | … | … | … | … |

差异直接命中具体 pitfall —— 对不齐就按括号里的 Phase 回去闭环：

- HMOS **漏发**某接口 → 对应 init 没跑（Phase 2 启动顺序）
- URL path 缺 `/user/` `/app/` 等前缀 → pitfalls D2（Phase 1.1）
- request body 少字段 / 类型错 → pitfalls D3（Phase 1.2）
- platformInfo 公参为空 → pitfalls D4 / C2（Phase 1.5 / 2.1）
- signature 与 Android 不一致 → pitfalls A（Phase 3）
- HTTP 200 但响应字段 undefined → pitfalls D1（Phase 4 unwrap）
