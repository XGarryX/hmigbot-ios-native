# 源端 UI 采集与规格消费

此能力属于现有 source-analysis 的可选 source-ui 步骤，不另建迁移流水线。init 首次展示 capture/replay/skip 策略及所需应用、模拟器、构建和场景范围；已有授权沿用。直接进入 spec 时同样展示选择卡。MCP 与原生应用测试分别选择；MCP 不可用不代表 XCUITest 不可用。

## 输入与调用

在 `spec/ref/ios-analysis-config.json` 中配置 `ui_capture`，或以 `--source-ui capture/replay/skip` 传入当前会话的选择。请求和证据必须位于本目标工程 `spec/ref/`。主控依据已确认范围与源分析填写，不要求开发者手写协议，不猜应用、设备或业务路径。

```json
{
  "schema_version": 1,
  "mode": "auto",
  "ui_capture": {
    "mode": "capture",
    "request": "spec/ref/ui-validation/source-request.json",
    "required": false,
    "bindings": [{
      "page_id": "page_0001",
      "checkpoint_id": "home",
      "source_anchors": [{"path": "Screens/Home.swift", "line": 10, "symbol": "Home.body"}]
    }]
  }
}
```

request 使用现有 `hmigbot-ios-ui-request/1`：真实模拟器 `.app`、bundle ID、精确模拟器 UDID、源根、配置、固定步骤和共享 business_recipe。仅存在路径或历史截图不构成新设备/场景授权。页面 ID 沿用本轮稳定分配，源码锚点与 checkpoint 的对应由分析 owner 明确提供；程序核对文件、行号和摘要，不声称自动理解了该对应关系。

`source-analysis` 在源事实及专业资料准备后、规格候选生成前实际调用原适配器 prepare/run。原生 XCTest 产出应用截图、无障碍树和配置收据。SDK、应用构建、模拟器运行时和实际系统批准仍须可用。没有有效模拟器 App 时，主控按实际工程选择调用官方 Xcode CLI 构建或给出具体替代路径；不能将 iphoneos 包拿去模拟器测试，也不自动修改产品最低版本、业务源码或授权设置。

源编译分析的 auto/native/replay/static 与显式 UI 采集是独立范围。比如源码静态分析可以同时具有明确选中的 Simulator UI 观察；后者不能证明 iphoneos/device-only 分支。报告分别列源编译和 UI 调用，不混成一次完整语义/业务验证。
单独选择 static 时不会继承历史 capture 策略，也不弹出冗余运行请求或启动应用。只有本次配置明确写入 ui_capture.mode=capture，或本次显式传入 --source-ui capture 时才组合执行；执行计划和可读提示会说明将安装启动所选测试 App。只读 replay 不启动应用。

## 存储与复用

机器索引为 `spec/ref/ios-source-ui-observations.json`；每个检查点引用原始截图和层级摘要，保存本次范围、配置缺口、耗时、真实执行或复用标记。原始 XCTest 工作目录位于目标 `.build/hmigbot-source-ui/`，保留构建缓存、xcresult 和 CLI 日志；只把原 manifest、请求、准备收据及其列举附件按原字节发布到当前分析 run 的 source-ui 目录。原绝对执行路径保留为来源，配置绑定消费发布后的同字节收据。这样编译缓存软链不会进入 Spec 输入枚举。

capture 会先核对所选/上次当前证据；源码、App 字节、设备、场景脚本、配置请求、provider 和附件仍匹配时直接复用。明确 replay 只消费 `manifest` 指定的当前收据，过期不能悄悄当通过。首次和恢复记录本次是否执行原生 UI，复用不得冒称又启动了设备。原 App 配置缺失保留 unknown，设备设置不能替代 App 的环境覆盖。

没有选择、缺少输入、过期证据与实际执行失败分别记录；独立源分析可以继续。`required:true` 仅用于用户已明确要求的这部分运行证据，缺失时返回 needs_ui_evidence 和具体恢复条件，保留已完成事实；不能将它变成所有项目的默认门禁。已规划/冻结项目拒绝改变 UI 证据，继续使用受审 source-refresh/replan，不删除原索引或改 hash 绕过。

## 规格作者的实际消费

`spec-authoring` 为每个对应页面提供 runtime_observations，包含原图、控件树、源码对应、检查点与配置缺口；未观测的页面不继承首屏状态。作者实际打开原图和层级再补规格，不能只看“captured”标签。

渲染候选在该页加入绑定的原生观察段；若已有规范 meta，则只更新本页 runtime=captured、真实 screenshot 与 extensions 内的完整观察列表。原页面内容和源码语义保留，旧 not_run 说明若已与新观察冲突由原作者明确修订，不用批量替换假装所有状态通过。候选不直接写 baseline，仍需独立内容复核和原门禁。

截图、层级、请求及 manifest 纳入作者/计划实际输入摘要，后续改动会失效，构建缓存与无关历史采集不整体冻结。captured 只证明固定场景下的观察；状态默认值、业务计算、全部导航、持久化及条件分支继续以相应源码/运行证据判断。

后续 execute 在目标页面可运行后采集鸿蒙端并配对；verify 复用仍有效的源端证据终验，不能在 spec 阶段伪造尚未生成的鸿蒙结果。
