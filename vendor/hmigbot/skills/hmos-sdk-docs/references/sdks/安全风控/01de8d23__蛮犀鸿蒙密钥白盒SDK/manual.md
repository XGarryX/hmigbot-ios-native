# # 蛮犀白盒密钥SDK 使用指南 

## 1. 产品概述 

本SDK 用于在HarmonyOS 场景中提供本地白盒密钥保护、对称加解密、单向报 文封装以及native 辅助混淆能力。适用于接口请求保护、关键参数封装、设备 侧轻量白盒演示接入。 

## 2. 安装和设置 ### 2.1 安装 将`sdk` 模块作为HAR 引入工程,并确保本地依赖`libkeywhitebox.so` 可 正常解析。 

### 2.2 环境要求 - DevEco Studio / HarmonyOS SDK 环境已配置 - `DEVECO_SDK_HOME` 有效 

- 工程可正常执行`hvigor assembleHar` 

### 2.3 初始化 SDK 为静态调用,无需额外初始化。业务侧可直接通过`KeyWhiteBoxSdk` 调用。 

## 3. 功能操作指南 ### 3.1 文本加解密 ```ts const encrypted = KeyWhiteBoxSdk.encryptText('hello', { algorithm: 'AES', key: '0123456789abcdef', mode: 'random' }) const plain = KeyWhiteBoxSdk.decryptText(encrypted, '0123456789abcdef') ``` 

### 3.2 单向请求封装 ```ts const request = KeyWhiteBoxSdk.buildOneWayRequest( 'payload-body', { algorithm: 'SM4', key: '0123456789abcdef', mode: 'oneWay' }, 'client-001', '/v1/secure/report' ) ``` 

### 3.3 文件加解密 调用`encryptFile` / `decryptFile` 即可完成文件读写及密文序列化。 

### 3.4 服务端联调 

- 使用`serializeOneWayRequest` 输出传输报文 

- 使用`buildServerContractHint` 提供字段说明 

- 使用`deriveServerIntegritySeed` 生成服务端校验辅助种子 

## 4. 常见问题解答 ### Q1:为什么`oneWay` 模式无法解密? 该模式用于客户端单向上送,请求发起后仅允许服务端验证,不开放客户端逆向 解密。 

### Q2:支持哪些算法? 当前支持`AES` 与`SM4`。 ### Q3:为什么会报native 依赖缺失? 请确认`libkeywhitebox.so` 依赖名、`types/libkeywhitebox` 路径以及 CMake 产物名一致。 

## 5. 故障排除 - 构建失败:检查`DEVECO_SDK_HOME`、`ohpm install`、本地Harmony SDK 配 置 - ArkTS 报错:检查依赖导入名是否为`libkeywhitebox.so` - native 构建失败:检查`sdk/src/main/cpp/CMakeLists.txt` 与NAPI 注册 名称是否一致
