# 蛮犀鸿蒙加固SDK 使用指南 

## 1. 产品概述 

蛮犀鸿蒙应用加固SDK 用于在HarmonyOS 场景下提供源码处理、交付型加固能 力编排、设备运行环境检测、保护决策与风险结果输出。当前版本主要包括源码 转换框架、任务协调能力、预设策略、Root/模拟器/调试/Hook 检测、生命周期 管理、缓存、批处理和Guard 模块。 

## 2. 安装与设置 1. 将`sdk` 模块接入工程并参与构建。 2. 确认`oh-package.json5` 中已包含对应HAR 依赖或模块引用。 3. 在业务代码中引入`ReinforceSdk`。 

```ts import { ReinforceSdk } from 'com.mx.reinforce'; const sdk = new ReinforceSdk(); ``` 

```

## 3. 功能操作指南 

### 3.1 执行源码处理 ```ts import { ReinforceSdk, ReinforceTask } from 'com.mx.reinforce'; 

```arkts
const sdk = new ReinforceSdk(); const task = new ReinforceTask( 'demo-task', 'entry', 'pages/Index.ets', sourceCode, 'balanced' ); const result = sdk.runTask(task); ``` 
```

### 3.2 执行源码分析 ```ts const summary = sdk.analyzeSource(sourceCode); ``` 

### 3.3 执行环境检测 ```ts import { ReinforceSdk, RuntimeSnapshotBuilder } from 'com.mx.reinforce'; 

const snapshot = new RuntimeSnapshotBuilder() .setDeviceModel('generic_x86') .setBrand('generic') .setProductName('sdk_gphone') .setVirtualScene(true) .build(); 

const report = sdk.inspectEnvironment(snapshot); ``` 

### 3.4 启动保护与敏感流程保护 ```ts const report = sdk.inspectEnvironment(snapshot); const startupDecision = sdk.evaluateStartup(report); const sensitiveDecision = sdk.evaluateSensitiveFlow(report); ``` 

### 3.5 页面保护 ```ts sdk.registerProtectedPage('PayPage'); const pageDecision = sdk.evaluatePage('PayPage'); ``` 

### 3.6 生命周期与批处理 ```ts sdk.initialize(); sdk.activate(); const batchResult = sdk.runBatch(tasks); ``` 

## 4. 常见问题解答 

### Q1:默认推荐哪个策略? 推荐`balanced`,兼顾效果、结构完整性与交付可解释性。 

### Q2:为什么环境检测需要运行时快照? 当前SDK 采用“采集层”和“检测层”分离设计,便于在不同项目中按需接入 真实设备信息来源。 

### Q3:是否可以直接替代完整编译期混淆工具? 当前版本更适合作为交付型SDK 框架与能力底座,不等同于完整AST 编译器或 商用构建插件。 

### Q4:Guard 模块适合放在哪些场景? 

适合启动页、登录页、支付页、会员权益页、内容解锁页等敏感页面或流程。 

# ## 5. 故障排除 

- 如果`runTask` 结果未发生变化,请确认源代码中确实存在布尔、数字、对 

- 象键、成员访问等可处理特征。 

- 如果环境检测结果为空,请检查`DeviceRuntimeSnapshot` 是否填充了模型、 

- 包名、路径、系统属性等字段。 

- 如果集成后找不到导出接口,请检查`sdk/Index.ets` 是否被正确导出并参 

- 与构建。 

- 如果需要更保守的效果,请切换到`compat` 预设并逐步启用规则。 

- 如果启动保护误拦截,请检查策略阈值和运行时快照是否存在误报特征。
