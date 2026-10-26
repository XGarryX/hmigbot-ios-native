# SDK 接口文档(集成文档) 

## 1. 文档目的 本文档用于指导业务方将`com.mx.softkeyboard` 集成到HarmonyOS 工程,并 调用安全软键盘SDK 的核心能力。 

## 2. SDK 基础信息 - SDK 名称:蛮犀鸿蒙软键盘SDK - 包名:`com.mx.softkeyboard` - 当前版本:`0.2.1` - 交付形态:HAR + Native `so` + Demo + 文档 

## 3. 目录与产物 - HAR 模块:`keyboard/` - Demo 模块:`entry/` - HAR 产物: [keyboard.har](H:\har\softkeyboard\keyboard\build\default\outputs\def ault\keyboard.har) - Native 库:`libmxsoftkeyboard.so` 

## 4. 集成步骤 ### 4.1 配置依赖 在业务模块`oh-package.json5` 中增加: ```json5 { "dependencies": { "com.mx.softkeyboard": "file:../keyboard" } } ``` 

### 4.2 安装依赖 在工程根目录执行: ```powershell & 'C:\Program Files\Huawei\DevEco Studio\tools\ohpm\bin\ohpm.bat' install ``` 

### 4.3 导入类型 ```ts import { SoftKeyboardController, 

SoftKeyboardConfig, KeyModel, KeyRow, KeyboardRenderState } from 'com.mx.softkeyboard'; ``` 

## 5. 核心接口 ### 5.1 `SoftKeyboardConfig` 用于配置品牌、主题、安全策略和功能开关。 

关键字段: 

- `packageName` 

- - `versionName` 

- - `submitLabel` 

- - `branding` 

- - `theme` 

- `securityPolicy` 

- `features` 

### 5.2 `SoftKeyboardController` 负责会话创建、按键处理、状态获取和提交封装。 

```ts const config = new SoftKeyboardConfig(); = config.packageName 'com.mx.softkeyboard'; = config.versionName '0.2.1'; const controller = new SoftKeyboardController(config); ``` 

- 主要方法: - `getConfig(): SoftKeyboardConfig` 

- `getRenderState(): KeyboardRenderState` 

- `handleKey(key: KeyModel): SecureSubmitResult | undefined` 

- `submit(): SecureSubmitResult | undefined` 

```

### 5.3 `KeyboardRenderState` 关键字段: 

- `rows` 

- `maskedText` 

- `prompt` 

- `securityTags` 

- `lastEnvelope` 

- `eventLogs` 

- `inputLength` 

### 5.4 `SecureSubmitResult` 关键字段: 

- `clearTextLength` 

- `masked.maskedText` 

- `masked.tailProof` 

- `envelope` 

- `digest.localProof` 

- `digest.nativeProof` 

## 6. 推荐页面接入方式 建议页面层显式同步SDK 状态,不要只依赖隐式重绘。 

```ts @State maskedText: string = '等待输入'; @State promptText: string = ''; private syncRenderState(): void { const state: KeyboardRenderState = this.controller.getRenderState(); ' this.maskedText = state.maskedText.length > 0 ? state.maskedText : 等待输入'; this.promptText = state.prompt; } 

private handleKeyTap(key: KeyModel): void { this.controller.handleKey(key); this.syncRenderState(); } ``` 

说明: 

- 点击字母/数字/符号键后,应立即重新读取`KeyboardRenderState` 

- 页面展示应绑定到`@State` 

- 提交后建议展示`lastEnvelope`、`localProof`、`nativeProof` 

```

## 7. Native 接口 ArkTS 通过`libmxsoftkeyboard.so` 调用Native 层: - `mixEnvelope(stageOneEnvelope: string, seed: number, sessionId: string): string` - `buildSessionProof(maskedText: string, seed: number): string` 

## 8. 接入建议 

- 页面层持有单例`SoftKeyboardController` 

- 页面渲染使用`getRenderState()` 返回值 

- 服务端接收`SecureSubmitResult.envelope` 

- 正式生产环境应替换原型算法和密钥管理策略
