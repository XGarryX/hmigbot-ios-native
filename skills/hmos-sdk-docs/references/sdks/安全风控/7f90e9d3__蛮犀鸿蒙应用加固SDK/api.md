# 蛮犀鸿蒙加固SDK 接口文档 

## 1. SDK 信息 

- SDK 名称:蛮犀鸿蒙应用加固SDK 

- 包名:`com.mx.reinforce` 

- 版本:`0.5.0` 

- 入口文件:`sdk/Index.ets` 

## 2. 集成方式 

1. 将`sdk` 模块作为HAR 集成到HarmonyOS 工程。 

2. 在业务模块中引入SDK 导出接口。 

```ts import { ReinforceSdk, ReinforceTask, RuntimeSnapshotBuilder } from 'com.mx.reinforce'; ``` 

```

## 3. 主要接口 

### 3.1 ReinforceSdk 统一门面,负责源码处理、风险分析、环境检测、生命周期和保护决策。 ```ts const sdk = new ReinforceSdk(); ``` 

- `listPresets(): ReinforcePreset[]` 返回预设策略列表,当前包括`balanced`、`compat`、`aggressive`。 

- `transform(source: string, options: ReinforceOptions): string` 直接执行源码转换并返回转换结果。 

- `transformWithReport(source: string, options: ReinforceOptions): 

- ReinforceResult` 

执行源码转换并返回详细报告。 

- `analyzeSource(source: string): SourceRiskSummary` 统计源码中的字符串、数字、布尔、注释、成员访问等特征。 

- `runTask(task: ReinforceTask): ReinforceTaskResult` 按任务形式执行处理。 

- `runBatch(tasks: ReinforceTask[]): ReinforceBatchResult` 执行批量任务处理。 

- `previewTask(task: ReinforceTask): string` 返回任务执行预览文本。 

- `inspectEnvironment(snapshot: DeviceRuntimeSnapshot): EnvironmentSecurityReport` 对设备环境进行检测。 

- `summarizeEnvironment(snapshot: DeviceRuntimeSnapshot): string` 返回环境检测摘要。 

- `createSession(appId: string, scene: string): 

- ReinforceSessionContext` 

创建SDK 会话上下文。 

- `recommendPolicy(source: string, snapshot?: DeviceRuntimeSnapshot): 

- PolicyDecision` 

基于源码和环境风险推荐预设策略。 

- `initialize()/activate()/suspend()` 管理SDK 生命周期状态。 

- `loadRemotePolicyConfig(): RemotePolicyConfig` 获取当前策略配置快照。 

- `evaluateStartup(report: EnvironmentSecurityReport): GuardDecision` 对启动阶段进行保护决策。 

- `evaluateSensitiveFlow(report: EnvironmentSecurityReport): 

- GuardDecision` 

对敏感流程进行保护决策。 

- `registerProtectedPage(pageName: string): void` 注册受保护页面。 

- `evaluatePage(pageName: string): GuardDecision` 获取页面保护决策。 

### 3.2 ReinforceTask 用于封装一次处理任务。 

```ts const task = new ReinforceTask( 'task-1', 'entry', 'pages/Index.ets', source, 'balanced' ); ``` 

字段说明: 

- `taskId`:任务唯一标识 

- `moduleName`:模块名称 

- `filePath`:待处理文件路径 

- `source`:源代码内容 

- `presetKey`:预设策略标识 

### 3.3 RuntimeSnapshotBuilder 

用于构建设备运行时快照,供Root、模拟器、调试、Hook 检测使用。 

```ts 

- const snapshot = new RuntimeSnapshotBuilder() 

   - .setDeviceModel('generic_x86') 

   - .setBrand('generic') 

   - .setProductName('sdk_gphone') 

   - .setDebuggerConnected(true) 

   - .build(); 

- ``` 

- ## 4. 返回模型 

- `ReinforceResult`:包含原始源码、转换结果、Pass 报告 

- `ReinforceTaskResult`:包含任务ID、文件路径、是否变更、转换后源码 

- `EnvironmentSecurityReport`:包含总分、高风险标记、各检测器结果 

- `PolicyDecision`:包含建议预设、原因、是否建议启用环境检测 

- `GuardDecision`:包含是否允许、执行动作、原因 

- `RemotePolicyConfig`:包含默认预设、环境阈值、版本等配置 

# ## 5. 建议接入方式 

- 业务接入默认使用`balanced` 预设。 

- 对展示或离线样本处理可使用`aggressive` 预设。 

- 设备环境检测建议在关键页面、启动阶段或敏感流程前执行。 

- 启动保护、敏感流程保护、页面保护建议与业务关键路径联动。
