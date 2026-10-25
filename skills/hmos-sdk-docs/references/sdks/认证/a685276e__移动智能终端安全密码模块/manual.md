**libscm_napi SDK** 使用指南 适用于鸿蒙系统 V5 及以上版本 

2026-04-29 

libscm_napi SDK 使用指南 

2026-04-29 

## 目录 

|**1libsc**|**m_nap**|**i SDK**使用指南 **3**|
|---|---|---|
|1.1|�简介|. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 3|
|1.2|�环境|要求. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 3|
|1.3|�快速|集成. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 3|
||1.3.1|1.添加依赖. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 3|
||1.3.2|2.配置权限. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 4|
||1.3.3|3.初始化SDK . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 4|
|1.4|�用户|认证. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 6|
||1.4.1|登录(首次或每次使用). . . . . . . . . . . . . . . . . . . . . . . . . . . . . 6|
||1.4.2|修改PIN . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 6|
||1.4.3|登出. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 6|
|1.5|�密钥|管理. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 7|
||1.5.1|生成密钥对. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 7|
||1.5.2|导出公钥. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 7|
||1.5.3|备份密钥对. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 7|
||1.5.4|恢复密钥对. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 7|
||1.5.5|删除密钥对. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 7|
|1.6|�证书|管理. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 8|
||1.6.1|申请证书(生成CSR). . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 8|
||1.6.2|安装证书. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 8|
||1.6.3|获取证书列表. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 8|
||1.6.4|加载当前用户证书. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 8|
||1.6.5|获取证书详细信息. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 9|
||1.6.6|获取远程证书列表. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 9|
|1.7|�密码|服务. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 9|
||1.7.1|数字签名. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 9|
||1.7.2|验签. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 9|
||1.7.3|SM2加密(使用公钥). . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 10|
||1.7.4|SM2解密(使用本地密钥对). . . . . . . . . . . . . . . . . . . . . . . . . . . 10|
||1.7.5|对称加解密(SM4/AES). . . . . . . . . . . . . . . . . . . . . . . . . . . . . 10|
||1.7.6|摘要计算. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 11|
|1.8|�服务|操作与高层接口 . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 11|
||1.8.1|调用远程服务(REST). . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 11|
||1.8.2|检查用户是否存在. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 11|
||1.8.3|注册用户. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 11|

1 

libscm_napi SDK 使用指南 

|cm_napi SDK使用指南|2026-04-29|
|---|---|
|1.8.4 下载证书. . . . . . . . . . . . . . . . .|. . . . . . . . . . . . . . . . . . . 11|
|1.8.5 更新证书. . . . . . . . . . . . . . . . .|. . . . . . . . . . . . . . . . . . . 12|
|1.9 �注意事项. . . . . . . . . . . . . . . . . . . .|. . . . . . . . . . . . . . . . . . . 12|
|1.10 �常见问题. . . . . . . . . . . . . . . . . . . .|. . . . . . . . . . . . . . . . . . . 12|
|1.11 �技术支持与合规文档 . . . . . . . . . . . . . .|. . . . . . . . . . . . . . . . . . . 12|

2 

libscm_napi SDK 使用指南 

2026-04-29 

# **1 libscm_napi SDK** 使用指南 

### **1.1 �** 简介 

`@sca/libscm_napi` 是移动智能终端安全密码模块的鸿蒙原生实现,支持 **SM2/SM3/SM4** 等国密算法。 本 SDK 以 HAR 形式发布,提供密钥管理、证书管理、数字签名、数据加解密、用户登录认证等功能,可部 署于鸿蒙 V5 及以上版本的手机、平板等设备。 

核心能力: 

- � 协同密钥管理(生成、备份、恢复、删除) 

- 🆔用户登录与 PIN 码认证 

- � 数字证书全生命周期管理(申请、安装、查询、加载) 

- � 数字签名与验签(支持 SM2、PKCS#7) 

- 🔒 数据加解密(SM2/SM4、AES) 

- � 远程服务调用与用户状态管理 

### **1.2 �** 环境要求 

- **DevEco Studio** :5.0.1 及以上 

- **HarmonyOS SDK** :API 13 及以上 

- **Node.js** :14.0+ 

- **ohpm** :最新版本 

### **1.3 �** 快速集成 

#### **1.3.1 1.** 添加依赖 

`-` 在您的模块级 `oh` **`package`** `.json5` 中添加: 

3 

libscm_napi SDK 使用指南 

2026-04-29 

1 `{` 2 `"dependencies": {` 3 `"@sca/libscm_napi": "^1.0.0"` 4 `}` 5 `}` 

#### 执行安装: 

1 `ohpm install` 

#### **1.3.2 2.** 配置权限 

若您的业务需要联网(证书申请、远程服务调用等),请在 `module.json5` 中声明 `INTERNET` 权限: 

1 `{` 2 `"module": {` 3 `"requestPermissions": [` 4 `{` 5 `"name": "ohos.permission.INTERNET",` 6 `"reason": "$string:internet_reason",` 7 `"usedScene": {` 8 `"abilities": ["EntryAbility"],` 9 `"when": "inuse"` 10 `}` 11 `}` 12 `]` 13 `}` 14 `}` 

#### **1.3.3 3.** 初始化 **SDK** 

在应用启动时(如 `AbilityStage.onCreate` 或 `EntryAbility.onCreate` )调用 `initialize` 完成初始化。 

4 

libscm_napi SDK 使用指南 

2026-04-29 

1 **`import`** `{` 2 `initialize,` 3 `version,` 4 `LogLevel,` 5 `SCContextV2,` 6 `SCResult` 7 `} from '@sca/libscm_napi';` 8 9 `//` 获取设备标识(推荐使用 `ODID` ) 10 `let deviceId: string = "YOUR_DEVICE_ID"; //` 需要自行实现获取 11 `let bundleId: string = "com.your.app";` 12 `let serverUrl: string = "https://your.server.com"; //` 业务后台地址 13 14 **`const`** `context: SCContextV2 = {` 15 `iVersion: 0,` 16 `iLogLevel: LogLevel.INFO, //` 调试时可设为 `DEBUG` 17 `iFlags: 0,` 18 `sBasePath: getContext().filesDir, //` 应用沙箱路径 19 `sDeviceId: deviceId,` 20 `sBundleId: bundleId,` 21 `sURL: serverUrl` 22 `};` 23 24 **`const`** `result: SCResult = initialize(context, ""); // extra` 参数暂无用 25 **`if`** `(result.status === 0) {` 26 `console.info(` ``` `SDK` 初始化成功,版本号: `${version()}` ``` `);` 27 `}` **`else`** `{` 28 `console.error(` ``` 初始化失败,错误码: `${result.status}` ``` `);` 29 `}` 

注意: `sBasePath` 必须是一个可写的沙箱目录,推荐使用 `getContext().filesDir` 。 

5 

libscm_napi SDK 使用指南 

2026-04-29 

### **1.4 �** 用户认证 

#### **1.4.1** 登录(首次或每次使用) 

1 **`import`** `{ login, ErrorCode } from '@sca/libscm_napi';` 2 3 **`const`** `account = "user@example.com";` 4 **`const`** `password = "your_pin_or_password";` 5 6 **`const`** `result = login(account, password);` 7 **`if`** `(result.status === ErrorCode.EOK) {` 8 **`const`** `retryCount = result.data.num; //` 口令剩余重试次数 9 `console.info(` ``` 登录成功,剩余重试次数: `${retryCount}` ``` `);` 10 `}` **`else if`** `(result.status === ErrorCode.EPINERROR) {` 11 `console.error("PIN` 错误 `");` 12 `}` **`else if`** `(result.status === ErrorCode.EPINLOCKED) {` 13 `console.error("PIN` 已锁定 `");` 14 `}` 

#### **1.4.2** 修改 **PIN** 

1 **`import`** `{ changePin } from '@sca/libscm_napi';` 2 3 **`const`** `oldPin = "123456";` 4 **`const`** `newPin = "654321";` 5 **`const`** `ret = changePin(oldPin, newPin);` 6 **`if`** `(ret === 0) {` 7 `console.info("PIN` 修改成功 `");` 8 `}` 

#### **1.4.3** 登出 

1 **`import`** `{ logout } from '@sca/libscm_napi';` 2 3 `logout(); //` 清除当前登录态 

6 

libscm_napi SDK 使用指南 

2026-04-29 

### **1.5 �** 密钥管理 

#### **1.5.1** 生成密钥对 

1 **`import`** `{ keyPairGenerate, KeyFlags } from '@sca/libscm_napi';` 2 3 `//` 生成签名密钥对 4 `let ret = keyPairGenerate(KeyFlags.SIGN);` 5 `//` 生成加密密钥对 6 `ret = keyPairGenerate(KeyFlags.ENCRYPT);` 7 `//` 生成同时用于签名和加密的密钥对 8 `ret = keyPairGenerate(KeyFlags.BOTH);` 

#### **1.5.2** 导出公钥 

1 **`import`** `{ keyPairExport } from '@sca/libscm_napi';` 2 3 `// sig=1` 导出签名公钥,否则导出加密公钥 4 **`const`** `result = keyPairExport(1);` 5 **`if`** `(result.status === 0) {` 6 **`const`** `pubKeyBlob: ArrayBuffer = result.data.blob;` 7 `console.info(` ``` 公钥长度: `${pubKeyBlob.byteLength}` ``` `);` 8 `}` 

#### **1.5.3** 备份密钥对 

1 **`import`** `{ keyPairBackup } from '@sca/libscm_napi';` 2 3 **`const`** `result = keyPairBackup(1, "backup_secret_password");` 4 **`if`** `(result.status === 0) {` 5 **`const`** `backupData: ArrayBuffer = result.data.blob;` 6 `//` 可将 `backupData` 上传至服务器 7 `}` 

#### **1.5.4** 恢复密钥对 

1 **`import`** `{ keyPairRestore } from '@sca/libscm_napi';` 2 3 `// backupData` 为之前备份的数据 4 **`const`** `ret = keyPairRestore(1, "backup_secret_password", backupData);` 

#### **1.5.5** 删除密钥对 

1 **`import`** `{ keyPairRemove } from '@sca/libscm_napi';` 2 3 `keyPairRemove(KeyFlags.SIGN); //` 删除签名密钥对 4 `keyPairRemove(KeyFlags.ENCRYPT);` 

7 

libscm_napi SDK 使用指南 

2026-04-29 

### **1.6 �** 证书管理 

#### **1.6.1** 申请证书(生成 **CSR** ) 

1 **`import`** `{ certRequest, KeyFlags } from '@sca/libscm_napi';` 2 3 `// flags` 决定使用哪个密钥对申请证书 4 **`const`** `result = certRequest(KeyFlags.SIGN, "CN=User,O=Org");` 5 **`if`** `(result.status === 0) {` 6 **`const`** `csrPem: string = result.data.str;` 7 `//` 将 `CSR` 提交给 `CA` 8 `}` 

#### **1.6.2** 安装证书 

1 **`import`** `{ certInstall } from '@sca/libscm_napi';` 2 3 `// p7b` 为 `CA` 返回的证书链( `PEM` 或 `DER` ) 4 **`const`** `ret = certInstall(p7bString);` 

#### **1.6.3** 获取证书列表 

1 **`import`** `{ certList } from '@sca/libscm_napi';` 2 3 **`const`** `certs: string[] = certList();` 4 `certs.forEach(cert => console.info(cert));` 

#### **1.6.4** 加载当前用户证书 

1 **`import`** `{ certLoad } from '@sca/libscm_napi';` 2 

3 `//` 加载签名证书 4 **`const`** `result = certLoad(); //` 默认 `sig=true` 5 **`if`** `(result.status === 0) {` 6 **`const`** `certPem: string = result.data.str;` 7 `}` 

8 

libscm_napi SDK 使用指南 

2026-04-29 

#### **1.6.5** 获取证书详细信息 

1 **`import`** `{ certInfo } from '@sca/libscm_napi';` 2 3 **`const`** `result = certInfo(); //` 签名证书信息 4 **`if`** `(result.status === 0) {` 5 `console.info(JSON.parse(result.data.str));` 6 `}` 

#### **1.6.6** 获取远程证书列表 

1 **`import`** `{ certRemoteList } from '@sca/libscm_napi';` 2 3 **`const`** `remoteCerts: string[] = certRemoteList();` 

### **1.7 �** 密码服务 

#### **1.7.1** 数字签名 

1 **`import`** `{ signData, DigestAlgorithm } from '@sca/libscm_napi';` 2 3 **`const`** `data =` **`new`** `Uint8Array([0x01, 0x02, 0x03]);` 4 **`const`** `result = signData(DigestAlgorithm.SM3, data.buffer);` 5 **`if`** `(result.status === 0) {` 6 **`const`** `signature: ArrayBuffer = result.data.blob;` 7 `}` 

#### **1.7.2** 验签 

1 **`import`** `{ verifySignature, DigestAlgorithm } from '@sca/libscm_napi';` 2 3 **`const`** `pubKey: ArrayBuffer = ...; //` 公钥数据 4 **`const`** `data: ArrayBuffer = ...;` 5 **`const`** `signature: ArrayBuffer = ...;` 6 7 **`const`** `ret = verifySignature(DigestAlgorithm.SM3, pubKey, data, signature);` 8 **`if`** `(ret === 0) {` 9 `console.info("` 验签成功 `");` 10 `}` 

9 

libscm_napi SDK 使用指南 

2026-04-29 

#### **1.7.3 SM2** 加密(使用公钥) 

1 **`import`** `{ sm2Encrypt } from '@sca/libscm_napi';` 2 3 **`const`** `pubKey = "04xxxx..."; //` 公钥字符串或 `ArrayBuffer` 4 **`const`** `plainText = "Hello SM2";` 5 6 **`const`** `result = sm2Encrypt(pubKey, plainText);` 7 **`if`** `(result.status === 0) {` 8 **`const`** `cipher: ArrayBuffer = result.data.blob;` 9 `}` 

#### **1.7.4 SM2** 解密(使用本地密钥对) 

1 **`import`** `{ sm2Decrypt } from '@sca/libscm_napi';` 2 3 `// encrypted` 为 `SM2` 密文 4 **`const`** `result = sm2Decrypt(encrypted, 1); // sig=1` 表示使用签名密钥对解密 5 **`if`** `(result.status === 0) {` 6 **`const`** `plain: ArrayBuffer = result.data.blob;` 7 `}` 

#### **1.7.5** 对称加解密( **SM4/AES** ) 

1 **`import`** `{ encrypt, decrypt, CipherAlgorithm } from '@sca/libscm_napi';` 2 3 **`const`** `key =` **`new`** `Uint8Array(16); // 128-bit` 密钥 4 **`const`** `iv =` **`new`** `Uint8Array(16);` 5 **`const`** `plain =` **`new`** `Uint8Array([0x00, 0x11]);` 6 7 `//` 加密 8 **`const`** `encResult = encrypt(CipherAlgorithm.SM4_CBC, key.buffer, iv.buffer, plain .buffer, 1);` 9 **`if`** `(encResult.status === 0) {` 10 **`const`** `cipher = encResult.data.blob;` 11 `//` 解密 12 **`const`** `decResult = decrypt(CipherAlgorithm.SM4_CBC, key.buffer, iv.buffer, cipher, 1);` 13 **`if`** `(decResult.status === 0) {` 14 **`const`** `recovered = decResult.data.blob;` 15 `}` 16 `}` 

10 

libscm_napi SDK 使用指南 

2026-04-29 

#### **1.7.6** 摘要计算 

1 **`import`** `{ digest, DigestAlgorithm } from '@sca/libscm_napi';` 2 3 **`const`** `data =` **`new`** `Uint8Array([0x01, 0x02]);` 4 **`const`** `result = digest(DigestAlgorithm.SM3, data.buffer);` 5 **`if`** `(result.status === 0) {` 6 **`const`** `hash: ArrayBuffer = result.data.blob;` 7 `}` 

### **1.8 �** 服务操作与高层接口 

#### **1.8.1** 调用远程服务( **REST** ) 

1 **`import`** `{ callRemote } from '@sca/libscm_napi';` 2 3 **`const`** `params = { action: "query", id: "123" };` 4 **`const`** `result = callRemote("/api/user/info", params,` **`true`** `); // true` 表示 `POST` 5 **`if`** `(result.status === 200) {` 6 `console.info(result.data.str); //` 响应体 7 `}` 

#### **1.8.2** 检查用户是否存在 

1 **`import`** `{ wsUserExist } from '@sca/libscm_napi';` 2 3 **`const`** `result = wsUserExist();` 4 **`if`** `(result.status === 0) {` 5 `console.info("` 用户存在 `");` 6 `}` 

#### **1.8.3** 注册用户 

1 **`import`** `{ wsUserRegister } from '@sca/libscm_napi';` 2 3 **`const`** `subject = "CN=` 张三 `,O=SCA";` 4 **`const`** `ret = wsUserRegister(subject);` 

#### **1.8.4** 下载证书 

1 **`import`** `{ wsCertDownload } from '@sca/libscm_napi';` 2 3 **`const`** `ret = wsCertDownload("auth_code_optional");` 

11 

libscm_napi SDK 使用指南 

2026-04-29 

#### **1.8.5** 更新证书 

1 **`import`** `{ wsCertUpdate } from '@sca/libscm_napi';` 2 3 **`const`** `ret = wsCertUpdate(); //` 触发证书延期 

### **1.9 �** 注意事项 

1. 初始化时机:必须在应用启动、未调用任何其他 SDK 接口前完成 `initialize` 。 

2. **PIN** 码安全:SDK 不存储原始 PIN,仅存储哈希值。连续 5 次错误将锁定,需调用 `changePin` 或重 新登录。 

3. 并发调用:SDK 接口非线程安全,请确保主线程调用或自行加锁。 

4. 证书有效期:定期检查证书状态,使用 `wsCertUpcoming` 获取续期提醒。 

5. 隐私合规:集成前请务必在应用的隐私政策中披露本 SDK 收集的个人信息(设备标识、证书信息等), 并提供关闭接口。 

### **1.10 �** 常见问题 

- **Q1** :初始化失败,返回 **`ENOTINIT`** ?A:请确保已调用 `initialize` 并传入了正确的 `sBasePath` 路径。 

- **Q2** :调用 **`signData`** 返回 **`ENOTLOGIN`** ?A:未登录或登录态已过期,请先调用 `login` 。 

- **Q3** :如何获取设备 **ID** ( **`sDeviceId`** )?A:推荐使用 `ohos.deviceInfo.ODID` (需配置权限)。 

- **Q4** : **SM2** 加密结果格式?A:遵循 GM/T 0009-2012 标准,输出 `04||X||Y||Ciphertext` 。 

- **Q5** :如何清理所有本地数据?A:调用 `finalize` (可自动调用)并删除 `sBasePath` 目录下 SDK 生成的 文件。 

### **1.11 �** 技术支持与合规文档 

- 公司名称:北京安软天地科技有限公司 

- 技术支持邮箱:support @ scanywhere.com 

- **SDK** 隐私政策:http:://www.scanywhere.com/policy/libscm_napi_policy.html 

12 

libscm_napi SDK 使用指南 

2026-04-29 

- 合规使用指南:http:://www.scanywhere.com/policy/libscm_napi_compliance.html 

北京安软天地科技有限公司 **@sca/libscm_napi SDK** 使用指南版本 **1.0** | 更新日期 2026-04-29 

13
