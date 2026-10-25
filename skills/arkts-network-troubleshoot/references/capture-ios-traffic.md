# 抓取 iOS 真实请求日志

这是原 Phase 0.3 的源平台实现。仍按三道前置检查→三种采集方法之一→原始样本与 runtime 回填的顺序，不新增阶段。静态 URL/body/签名候选优先读 [选定 Source](native-source-search.md) 和本轮 api-inventory；真实响应、服务端成功码、动态值和签名字节按实际观测核对。

没有可用 iPhone/Simulator、Mac 诊断工具、测试账号或采集通道时，把对应源观测记 DEFERRED/needs_capture，写明原因、owner 和关闭条件。Base-3 的静态实现依原设备依赖边界继续；不能把空样本或设置导出当作真实运行。不得为填满样本数而试探真实注册、发码或支付。

## 前置检查：三道闸门

1. **真实源设备与采集工具就绪。** 记录 iPhone/Simulator 标识和状态、主机/工具版本；Windows 上没有原生运行环境不冒称已启动源应用。Mac 可先用当前 Xcode 的 `xcrun simctl help` 核对能力，再用 `xcrun simctl list devices booted --json` 核对已启动模拟器。真实 iPhone 通过实际 Xcode/设备工具确认；不要把模拟器命令用于真机。
2. **源应用、构建配置和业务状态一致。** 核实实际 bundle ID、选定 target/configuration、应用已安装和可达业务路径。日志功能可能受配置控制；若另用诊断构建，记录与 Release 的差异，不能充当 Release 编译或行为证明。账号、同意状态和新装状态必须与对比目标对应；不静默清数据或替用户购买。
3. **所选采集通道确实可用。** 用一条已授权请求验证捕获字段、请求响应配对、时序、进程和 endpoint 归属。只确认有工具或有连接不能算通道通过。缺失哪些字段逐项登记。

## 方法 A：源 App 实际网络日志

从选定 Source 沿 URLSession/URLRequest、实际三方客户端或自定义包装器查明日志位置和构建条件。用实际 Xcode 控制台、Simulator/设备日志能力采集，保存真实来源、时间窗口、进程与日志格式。

日志没有输出 headers、body 或响应时，不自行补齐为“实测”。并发请求须有真实请求标识或可靠的配对依据。原包的日志解析器针对特定格式；只有用当前原生样本验证正确后才能复用，不能把任意控制台输出直接喂入并当全部成功。冷启动是否发请求取决于原生应用实际隐私门、登录和启动链，不能默认自动触发全部端点。

## 方法 B：Xcode/Instruments 的实际诊断材料

按当前 Xcode 版本和目标进程的真实能力选择网络诊断。先核对是否能看到所需 URL、方法、headers、请求/响应体和时间信息，再保存实际可导出的记录。诊断工具名、面板或文件存在不证明所有字段可捕获；不宣称其必然支持所有 SDK 或自动导出完整 HAR。

涉及 UI 的深层请求使用真实 XCUITest/已就绪原生设备工具或用户操作进入。`simctl` 的启动、截图能力不等于通用点击/填表能力，不能凭脚本配置声称已操作。没有相应驱动时将该操作记 DEFERRED。

## 方法 C：实际可用的请求代理

在已授权测试环境中，使用真实可用的 Charles/mitmproxy 等工具采集。记录设备代理设置、HTTPS 信任与应用 TLS 策略是否允许采集；不能把握手失败当业务响应。原生 ATS、证书验证和 pinning 是否影响通道须依据实际代码与结果，不能承诺任意应用都可拦截。

保留抓取前的网络配置，结束后恢复本次修改。所需签名、公参、编码和正文按真实样本逐字段或逐字节核对；代理可能重组传输层信息，不能将重组内容冒称所有线缆级细节。已有明文 HTTP 测试链可按原代理工具的真实能力复用，不能因工具存在就改变源端 URL/TLS 契约。

## 隐私、登录及其他前置页面

先读取本轮源导航与启动状态，按真实可见 UI 到达业务；记录是否有同意/登录/授权页面。只操作已有用户授权范围。截图、点击、跳转或状态准备未真实执行就保留缺口，不能通过伪造持久化值宣称通过。

## 方法选择与能力边界

| 需要确认 | 方法与边界 |
|---|---|
| URL/body/签名静态结构 | 本轮 Source/API static；不标 runtime |
| 实际响应形状、业务码、动态类型 | A/B/C 中真正捕获到该字段的方法 |
| 完整请求头、公参、签名输入 | 选择实际能保留这些字段的诊断或代理，不从缺失日志猜值 |
| 深层登录/业务/支付 | 需要真实可达路径、设备工具和相应授权；缺失则 DEFERRED |
| 无源环境 | 保留 static-only/needs_capture 和关闭条件，按原 Base-3 边界推进静态实现 |

## 抓完之后：原样本与 contract 回填

依原流程覆盖核心启动、登录、业务、上传和支付端点；不适用的类别按原范围记录。每条完整样本保存请求行、实际 headers/body、响应及来源时间，落 `spec/baseline/sample-requests.md`。缺请求、缺响应或归属不明的样本不能算完整。

有 `api-inventory.json` 时，按原 endpoint key（HTTP 方法 + path）仅回填真正捕获的 `runtime` 字段：响应包装、成功码、字段类型/默认值、headers、签名字节、source/captured_at。未抓到的 runtime 留 null，reconciled 维持 static-only。能回答 uncertainties 的才用证据销账；同步 decision-ledger 和原分层 apis/*.md 投影，不改 static 的出处或冒充后端接受了新通道。

之后走原 Phase 1.7 的 static/runtime DIFF。JSON 字段所有权、状态及 [schema](../../ios-api-inventory/references/output_schema.md) 保持；对账表见 [模板](templates/spec-baseline.md)。

## 与 HMOS 侧冷启动对比（Phase 6 用，不是 Phase 0.3）

> Phase 0.3 抓 iOS 基线时，HMOS 网络层还没实现 —— 没有可比对象，**别在 Phase 0.3 做对比**。
> 等 HMOS 拦截器 / SignUtil / HttpClient 写完、进入 Phase 6 联调，再回到这里：冷启动 HMOS App，把它的启动请求与 iOS 基线逐接口对账。这是启动链路最硬的证据。

HMOS 冷启动按原目标 hdc 流程实际采集：

```bash
BUNDLE=<HMOS bundleName>
hdc shell aa force-stop "$BUNDLE"                       # 杀进程
hdc shell hilog -r                                      # 清 hilog 缓冲
hdc shell aa start -b "$BUNDLE" -a EntryAbility          # 冷启动
sleep 20                                                # 等启动类请求发完（多数 App 冷启后 1-3s 内即发完，sleep 是容错余量，可按 hilog 实际出现时刻缩短）
hdc shell hilog -x | grep -E 'HTTP >>>|HTTP <<<' > hmos_capture.log   # -x dump 后退出
```

- 前提：HMOS 端 `AppStorage('isDebug')=true`，否则 HttpLogInterceptor 静默不打日志（见 Phase 2.1）。
- 提炼日志前先核对目标日志格式。原 extract_startup_requests.py 是特定格式解析器；只有真实样本验证可正确配对、归属和提取后才能采用，不能宣称所有源/目标日志均自动兼容。

**逐接口对账表**：左边 Phase 0.3 抓的 iOS 基线（`sample-requests.md`），右边 HMOS 实际：

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
- signature 与 iOS 不一致 → pitfalls A（Phase 3）
- HTTP 200 但响应字段 undefined → pitfalls D1（Phase 4 unwrap）
