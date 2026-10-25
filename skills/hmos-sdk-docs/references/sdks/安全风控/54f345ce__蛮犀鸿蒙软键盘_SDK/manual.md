# # SDK 使用指南 

## 1. 产品概述 

蛮犀鸿蒙软键盘SDK 用于在HarmonyOS 应用内提供安全输入能力,当前版本支 持随机键位、输入去标识化、协议封装、品牌主题自定义以及ArkTS + Native 双 层安全增强。 

当前Demo 已实现完整交互链路: 

- 字母/数字/符号输入 

- 删除、清空、大小写切换 

- 模式切换 

- 安全提交后生成envelope 

- 页面显式同步掩码文本、输入长度、最近按键和封装结果 

## 2. 安装和设置步骤 ### 2.1 环境要求 

- DevEco Studio - HarmonyOS SDK / OpenHarmony Native 工具链 - `ohpm` - `hvigor` 

### 2.2 添加依赖 ```json5 { "dependencies": { "com.mx.softkeyboard": "file:../keyboard" } } ``` 

### 2.3 安装依赖 ```powershell 

& 'C:\Program Files\Huawei\DevEco Studio\tools\ohpm\bin\ohpm.bat' install ``` 

### 2.4 构建SDK 与Demo ```powershell 

$env:DEVECO_SDK_HOME='C:\Program Files\Huawei\DevEco Studio\sdk' 

& 'C:\Program Files\Huawei\DevEco Studio\tools\hvigor\bin\hvigorw.bat' --mode module -p module=keyboard assembleHar 

& 'C:\Program Files\Huawei\DevEco Studio\tools\hvigor\bin\hvigorw.bat' --mode module -p module=entry assembleHap ``` 

## 3. 功能操作指南 ### 3.1 初始化控制器 ```ts const config = new SoftKeyboardConfig(); = config.packageName 'com.mx.softkeyboard'; = config.versionName '0.2.1'; const controller = new SoftKeyboardController(config); ``` 

### 3.2 页面渲染 - 使用`controller.getRenderState().rows` 渲染键盘行与键位 - 点击键位时调用`controller.handleKey(key)` - 点击后显式调用一次状态同步,把结果写入`@State` - 使用`maskedText` 做回显,不直接展示明文 

### 3.3 推荐交互同步方式 ```ts @State maskedText: string = '等待输入'; @State promptText: string = ''; @State lastEnvelopeText: string = '尚未提交'; private syncRenderState(): void { const state = this.controller.getRenderState(); ' this.maskedText = state.maskedText.length > 0 ? state.maskedText : 等待输入'; this.promptText = state.prompt; this.lastEnvelopeText = state.lastEnvelope.length > 0 ? state.lastEnvelope : '尚未提交'; } private handleKeyTap(key: KeyModel): void { this.controller.handleKey(key); this.syncRenderState(); } ``` 

### 3.4 提交结果 - 点击“安全提交”后,SDK 输出`SecureSubmitResult` - 业务侧读取`envelope`、`localProof`、`nativeProof` - 建议仅上传`envelope` 到服务端 ### 3.5 可配置项 - 品牌名称、LOGO、标题、副标题 

- 提交按钮文案 - 主题色、边框色、掩码色 - 是否启用随机键位 - 是否启用去标识化 - 是否启用Native 增强 

## 4. 常见问题解答 ### Q1:为什么输入框里看不到真实字符? 因为SDK 默认启用去标识化回显,只展示掩码字符,避免肩窥和录屏泄露。 

### Q2:为什么每次进入页面键位顺序不同? 因为默认启用了随机键位布局,属于核心安全能力。 

### Q3:为什么日志里点击到了Button,但页面没变化? 通常是页面没有在点击后重新同步`controller.getRenderState()`。建议把掩 码文本、提示文案、最近封装结果映射到`@State`。 ### Q4:Native 层可以关闭吗? 可以,通过`features.nativeReinforce = false` 关闭,但不建议在交付版中 关闭。 

### Q5:当前版本是不是正式商用密码实现? 不是。当前仓库是方案展示和交付原型,若投产应替换为正式密码算法和密钥体 系。 

## 5. 故障排除 ### 5.1 `DEVECO_SDK_HOME` 无效 现象:`Invalid value of 'DEVECO_SDK_HOME'` 

处理: ```powershell $env:DEVECO_SDK_HOME='C:\Program Files\Huawei\DevEco Studio\sdk' ``` 

### 5.2 hvigor 缓存损坏 现象:提示`hvigor.js` 不存在 处理:删除对应`.hvigor\project_caches` 后重新构建。 

### 5.3 Native 链接失败 现象:`undefined symbol: napi_*` 处理:确认`CMakeLists.txt` 已链接`ace_napi.z`。 

### 5.4 HAR 依赖未解析 

现象:`com.mx.softkeyboard` 被当成external dependency 

# 处理: 

- 检查`entry/oh-package.json5` 依赖声明 

- 重新执行`ohpm install` 

- ### 5.5 按键点击无视觉反馈 

现象:日志有点击事件,但`等待输入` 无变化 

# 处理: 

- 检查页面是否在`handleKeyTap` 后调用`syncRenderState` 

- 检查展示文本是否绑定到`@State` 

- 检查键盘区是否用了旧的静态文本而非最新状态值 

- ## 6. 推荐上线前动作 

- 替换原型算法为正式算法 

- 增加服务端验签/解封能力 

- 补充压力测试、兼容性测试和隐私合规材料
