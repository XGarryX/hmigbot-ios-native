协同签名客户端接口说明 适用于鸿蒙系统 V5 及以上版本 

2026-04-15 

协同签名客户端接口说明 

2026-04-15 

|目录||||
|---|---|---|---|
|**1** 软件|介绍||**3**|
|**2** 常量|||**3**|
|2.1|返回码|. . . . . . . . . . . . . . . . . . . . . . . . .|. . . . . . . . . . . . . . . . 3|
|2.2|摘要算|法定义. . . . . . . . . . . . . . . . . . . . . .|. . . . . . . . . . . . . . . . 4|
|2.3|对称算|法定义. . . . . . . . . . . . . . . . . . . . . .|. . . . . . . . . . . . . . . . 4|
|2.4|密钥标|志定义. . . . . . . . . . . . . . . . . . . . . .|. . . . . . . . . . . . . . . . 4|
|2.5|日志级|别定义. . . . . . . . . . . . . . . . . . . . . .|. . . . . . . . . . . . . . . . 4|
|**3** 结构|定义||**4**|
|3.1|SCCon|textV2 . . . . . . . . . . . . . . . . . . . . . .|. . . . . . . . . . . . . . . . 4|
|3.2|SCRes|ult . . . . . . . . . . . . . . . . . . . . . . . .|. . . . . . . . . . . . . . . . 5|
|**4** 函数|定义||**5**|
|4.1|环境管|理. . . . . . . . . . . . . . . . . . . . . . . .|. . . . . . . . . . . . . . . . 5|
||4.1.1|version . . . . . . . . . . . . . . . . . . . . .|. . . . . . . . . . . . . . . . 5|
||4.1.2|initialize . . . . . . . . . . . . . . . . . . . .|. . . . . . . . . . . . . . . . 6|
||4.1.3|finalize . . . . . . . . . . . . . . . . . . . . .|. . . . . . . . . . . . . . . . 6|
||4.1.4|lastError . . . . . . . . . . . . . . . . . . . .|. . . . . . . . . . . . . . . . 6|
||4.1.5|setPlugin . . . . . . . . . . . . . . . . . . . .|. . . . . . . . . . . . . . . . 7|
||4.1.6|secCheck . . . . . . . . . . . . . . . . . . . .|. . . . . . . . . . . . . . . . 7|
||4.1.7|secInit . . . . . . . . . . . . . . . . . . . . .|. . . . . . . . . . . . . . . . 7|
||4.1.8|random . . . . . . . . . . . . . . . . . . . .|. . . . . . . . . . . . . . . . 8|
||4.1.9|runtimeInfo . . . . . . . . . . . . . . . . . .|. . . . . . . . . . . . . . . . 8|
|4.2|用户认|证. . . . . . . . . . . . . . . . . . . . . . . .|. . . . . . . . . . . . . . . . 8|
||4.2.1|login . . . . . . . . . . . . . . . . . . . . . .|. . . . . . . . . . . . . . . . 8|
||4.2.2|logout . . . . . . . . . . . . . . . . . . . . .|. . . . . . . . . . . . . . . . 9|
||4.2.3|changePin . . . . . . . . . . . . . . . . . . .|. . . . . . . . . . . . . . . . 9|
|4.3|密钥管|理. . . . . . . . . . . . . . . . . . . . . . . .|. . . . . . . . . . . . . . . . 9|
||4.3.1|keyPairGenerate . . . . . . . . . . . . . . . .|. . . . . . . . . . . . . . . . 9|
||4.3.2|keyPairRemove . . . . . . . . . . . . . . . . .|. . . . . . . . . . . . . . . . 10|
||4.3.3|keyPairExport . . . . . . . . . . . . . . . . .|. . . . . . . . . . . . . . . . 10|
||4.3.4|keyPairBackup . . . . . . . . . . . . . . . . .|. . . . . . . . . . . . . . . . 10|
||4.3.5|keyPairRestore . . . . . . . . . . . . . . . . .|. . . . . . . . . . . . . . . . 11|
|4.4|证书管|理. . . . . . . . . . . . . . . . . . . . . . . .|. . . . . . . . . . . . . . . . 11|
||4.4.1|certLogin . . . . . . . . . . . . . . . . . . . .|. . . . . . . . . . . . . . . . 11|

1 

协同签名客户端接口说明 

2026-04-15 

||4.4.2|certRequest . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 12|
|---|---|---|
||4.4.3|certInstall . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 12|
||4.4.4|certList . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 12|
||4.4.5|certLoad . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 13|
||4.4.6|certPublicKey . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 13|
||4.4.7|certInfo . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 13|
||4.4.8|certRemoteList . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 14|
|4.5|密码服|务. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 14|
||4.5.1|signData . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 14|
||4.5.2|verifySignature . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 14|
||4.5.3|encrypt . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 15|
||4.5.4|decrypt . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 15|
||4.5.5|digest . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 16|
||4.5.6|pkcs7Sign . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 16|
||4.5.7|pkcs7Verify . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 17|
||4.5.8|sm2Encrypt . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 17|
||4.5.9|sm2Decrypt . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 17|
||4.5.10|exSignData . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 18|
||4.5.11|exSm2Decrypt . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 18|
|4.6|服务操|作接口. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 19|
||4.6.1|callRemote . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 19|
|4.7|高层接|口. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 19|
||4.7.1|wsUserExist . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 19|
||4.7.2|wsUserState . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 19|
||4.7.3|wsUserRegister . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 20|
||4.7.4|wsUserCertificates . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 20|
||4.7.5|wsCertDownload . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 20|
||4.7.6|wsCertUpdate . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 21|
||4.7.7|wsCertUpcoming . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 21|

2 

协同签名客户端接口说明 

2026-04-15 

- _VERSION: v1.0_ 

- _updated: 2026-04-29_ 

- 目标系统 _:_ 鸿蒙系统 _v5_ 及以上版本 

# **1** 软件介绍 

手机盾以移动智能终端安全密码模块为安全核心,是为移动智能终端 (包括手机、平板电脑和物联网设备) 提供密码安全功能服务的应用。 

支持国产 SM2/3/4 算法,可部署在包括鸿蒙系统在内的多种种主流移动智能终端。 

移动智能终端安全密码模块由协同密钥管理模块、协同运算模块、通信模块、服务接口模块组成。移动智能 终端安全密码模块产品具有密钥安全存储、身份认证、数字签名、证书安全管理、数据加解密等功能。 

# **2** 常量 

## **2.1** 返回码 

返回 0(EOK) 表示成功,返回其他值表示失败,具体值定义如下: 

|1|`export` **`const`** `Erro`|`rCode = {`||
|---|---|---|---|
|2|`EOK:` |`0,`|`//` 操作成功 |
|3|`ESCBASE:` |`0x01000000,`|`//` 基础错误 |
|4|`ENOTINIT:`|`0x01000001,`|`//` 未调用初始化接口 |
|5|`ENOTLOGIN:`|`0x01000002,`|`//` 未登录 |
|6|`EPINERROR:`|`0x01000003,`|`// PIN`错误 |
|7|`EPINLOCKED:`|`0x01000004,`|`// PIN`锁定 |
|8|`EBADURL:`|`0x01000005,`|`//` 服务器`URL`不正确 |
|9|`ENETWORK:`|`0x01000006,`|`//` 网络错误 |
|10|`ESERVICE:`|`0x01000007,`|`//` 服务异常 |
|11|`EINVPARAM:`|`0x01000008,`|`//` 参数错误 |
|12|`EBUFTOOSMALL:`|`0x01000009,`|`//` 缓冲区过小 |
|13|`ECERTREVOKED:`|`0x0100000A,`|`//` 证书被作废|
|14|`ENOTEXIST:`|`0x0100000B,`|`//` 对象不存在 |
|15|`ECONTEXT:`|`0x0100000C,`|`//` 上下文错误 |
|16|`ENOTNEEDOP:`|`0x0100000D,`|`//` 不需要的操作 |
|17|`ENEEDSYNC:`|`0x0100000E,`|`//` 用户不在`CSVS`上,在`RA`或`4A`上,需要进行同步 |
|18|`EALREADYCERT:`|`0x0100000F,`|`//` 当前设备上用户已经具有证书 |
|19|`ESIGNATURE:`|`0x01000010,`|`//` 错误的签名值 |
|20|`EBACKEND:`|`0x01000011,`|`//` 后台异常|
|21|`EWAITAPPROVE:`|`0x01000012,`|`//` 操作`(`如证书延期`)`等待管理员审核 |
|22|`EDENYORCANCEL:`|`0x01000013,`|`//` 管理员取消或拒绝操作申请`(`如证书延期`)` |
|23|`ENYI:`|`0x010000FF`|`//` 尚未实现|
|24|`};`|||

3 

协同签名客户端接口说明 

2026-04-15 

## **2.2** 摘要算法定义 

1 `export` **`const`** `DigestAlgorithm = {` 2 `SHA1: 1, //` 表示 `SHA1` 3 `SHA256: 2, //` 表示 `SHA256` 4 `SM3: 3 //` 表示 `SM3` 5 `};` 

## **2.3** 对称算法定义 

1 `export` **`const`** `CipherAlgorithm = {` 2 `AES_CBC: 1, //` 表示 `aes-128-cbc` 3 `AES_ECB: 2, //` 表示 `aes-128-ecb` 4 `SM4_CBC: 3, //` 表示 `sm4-cbc` 5 `SM4_ECB: 4 //` 表示 `sm4-ecb` 6 `};` 

## **2.4** 密钥标志定义 

1 `export` **`const`** `KeyFlags = {` 2 `DEFAULT: 1, //` 默认 3 `SIGN: 2, //` 签名 4 `ENCRYPT: 4, //` 加密 5 `BOTH: 6, //` 签名和加密 6 `FORCE: 8, //` 强制 7 `BITS: 16 //` 比特数 8 `};` 

## **2.5** 日志级别定义 

1 `export` **`const`** `LogLevel = {` 2 `DEBUG: 0, //` 调试 3 `INFO: 1, //` 信息 4 `WARN: 2, //` 警告 5 `ERROR: 3, //` 错误 6 `FATAL: 4 //` 致命错误 7 `};` 

# **3** 结构定义 

## **3.1 SCContextV2** 

用于初始化上下文的配置对象。 

4 

协同签名客户端接口说明 

2026-04-15 

|1 `export` **`interface`** `SCCont` 2 `iVersion: number;`|`extV2 {` `//` 版本号`,` 设置设置为`0` |
|---|---|
|3 `iLogLevel: number;`|`//` 日志级别 |
|4 `iFlags: number;`|`//` 标志位`,` 默认设置`0` |
|5 `sBasePath: string;`|`//` 基础路径`,` 存放本地生成数据的目录 |
|6 `sDeviceId: string;`|`//` 设备`ID,` 鸿蒙系统下推荐使用`ODID` |
|7 `sBundleId: string;`|`//` 客户端`APP` 的`ID`|
|8 `sURL: string` 9 `}`|`// URL`|

## **3.2 SCResult** 

### 操作结果对象: 

- number: 接口返回状态码,0 表示成功,其他值表示失败, 请参考 `ErrorCode` . 

- data: 具体的返回参数,接口不同,返回的有效数据不同。 

|1|`export` **`interface`** `SCResult {` ||
|---|---|---|
|2|`status: number;` `//` 状|态码|
|3|`data: {`||
|4|`bool:` **`boolean`**`;` `//` 布|尔值|
|5|`num: number;` `//` 数|字|
|6|`str: string;` `//` 字|符串|
|7|`blob: ArrayBuffer;` `//` 二 |进制数据 |
|8 9 10|`obj: object` `//` 对 `}` `}`|象|

# **4** 函数定义 

## **4.1** 环境管理 

### **4.1.1 version** 

### 获取版本号。 

1 `export` **`const`** `version: () => number;` 

- 输入: 

   - 无 

- 返回值: 

   - number: SDK 的版本号 

5 

协同签名客户端接口说明 

2026-04-15 

### **4.1.2 initialize** 

初始化上下文。 

1 `export` **`const`** `initialize: (context: SCContextV2, extra: string) => SCResult;` 

• 输入: 

**–** context: 初始化上下文配置对象 

**–** extra: 其他配置参数 

- 返回值: 

**–** SCResult: 初始化结果 

- status: 状态码 

- obj: 原生上下文句柄 

### **4.1.3 finalize** 

释放上下文, 该接口会自动调用。 

1 `export` **`const`** `finalize: (handle: object) => number;` 

- 输入: 

**–** handle: 原生上下文句柄 

- 返回值: 

**–** number: 结果码 

### **4.1.4 lastError** 

获取上次错误信息。 

1 `export` **`const`** `lastError: () => string;` 

- 输入: 

**–** 无 

- 返回值: 

**–** string: 上次错误的信息 

6 

协同签名客户端接口说明 

2026-04-15 

### **4.1.5 setPlugin** 

### 设置插件, 插件参数值根据后台集成能力确定。 

- 1 `export` **`const`** `setPlugin: (plugin: string) => number;` 

- 输入: 

   - plugin: 插件类型 

- 返回值: 

**–** number: 结果码 

### **4.1.6 secCheck** 

### 安全检查。 

1 `export` **`const`** `secCheck: () => number;` 

- 输入: 

**–** 无 

- 返回值: 

**–** number: 结果码 

### **4.1.7 secInit** 

### 安全初始化。 

1 `export` **`const`** `secInit: (seed: ArrayBuffer) => number;` 

- 输入: 

   - seed: 种子数据 

- 返回值: 

   - number: 结果码 

7 

协同签名客户端接口说明 

2026-04-15 

### **4.1.8 random** 

生成随机数。 

1 `export` **`const`** `random: (len: number) => SCResult;` 

- 输入: 

**–** len: 随机数长度, 单位字节, 长度范围为 [1, 4096] 

- 返回值: 

**–** SCResult: 包含生成的随机数和状态码 

- status: 状态码 

- blob: 随机字节串 

### **4.1.9 runtimeInfo** 

获取运行时信息。 

1 `export` **`const`** `runtimeInfo: () => SCResult;` 

• 输入: 

**–** 无 

- 返回值: 

**–** SCResult: 运行时信息和状态码 

- status: 状态码 

- str: 运行时信息 

## **4.2** 用户认证 

### **4.2.1 login** 

用户登录。 

1 `export` **`const`** `login: (account: string, password: string) => SCResult;` 

• 输入: 

**–** account: 用户名 

**–** password: 密码 

8 

协同签名客户端接口说明 

2026-04-15 

- 返回值: 

   - SCResult: 登录结果和状态码 

      - status: 状态码 

      - num: 口令剩余重试次数 

### **4.2.2 logout** 

用户登出。 

1 `export` **`const`** `logout: () => number;` 

- 输入: 

**–** 无 

- 返回值: 

**–** number: 结果码 

### **4.2.3 changePin** 

更改 PIN。 

1 `export` **`const`** `changePin: (oldpin: string, newpin: string) => number;` 

• 输入: 

**–** oldpin: 旧 PIN **–** newpin: 新 PIN 

• 返回值: 

**–** number: 结果码 

## **4.3** 密钥管理 

### **4.3.1 keyPairGenerate** 

生成密钥对。 

1 `export` **`const`** `keyPairGenerate: (flags: number) => number;` 

- 输入: 

9 

协同签名客户端接口说明 

2026-04-15 

### **–** flags: 密钥生成控制参数,参考 KeyFlags 

- 返回值: 

   - number: 结果码 

### **4.3.2 keyPairRemove** 

### 移除密钥对。 

- 1 `export` **`const`** `keyPairRemove: (flags: number) => number;` 

- 输入: 

   - flags: 移除控制参数,参考 KeyFlags 

- 返回值: 

   - number: 结果码 

### **4.3.3 keyPairExport** 

导出密钥对。 

1 `export` **`const`** `keyPairExport: (sig: number) => SCResult;` 

- 输入: 

   - sig: 密钥标志,1 为签名密钥对,否则为加密密钥对 

- 返回值: 

   - SCResult: 导出结果和状态码 

      - status: 状态码 

      - blob: 返回的公钥数据 

### **4.3.4 keyPairBackup** 

备份密钥对。 

1 `export` **`const`** `keyPairBackup: (sig: number, secret: string) => SCResult;` 

- 输入: 

   - sig: 密钥标志,1 为签名密钥对,否则为加密密钥对 

10 

协同签名客户端接口说明 

2026-04-15 

   - secret: 待备份的密钥 

- 返回值: 

   - SCResult: 备份结果和状态码 

      - status: 状态码 

      - blob: 返回的备份数据 

### **4.3.5 keyPairRestore** 

恢复密钥对。 

1 `export` **`const`** `keyPairRestore: (sig: number, secret: string, data: ArrayBuffer) => number;` 

- 输入: 

**–** sig: 密钥标志,1 为签名密钥对,否则为加密密钥对 

   - secret: 恢复密钥 

   - data: 备份数据 

- 返回值: 

**–** number: 结果码 

## **4.4** 证书管理 

### **4.4.1 certLogin** 

证书登录。 

1 `export` **`const`** `certLogin: () => number;` 

• 输入: 

**–** 无 

- 返回值: 

**–** number: 结果码 

11 

协同签名客户端接口说明 

2026-04-15 

### **4.4.2 certRequest** 

请求证书。 

1 `export` **`const`** `certRequest: (flags: number, subject?: string) => SCResult;` 

• 输入: 

   - flags: 请求标志,参考 KeyFlags 

   - subject: 主题信息(可选) 

- 返回值: 

**–** SCResult: 请求结果和状态码 

- status: 状态码 

- str: 返回的证书请求数据 

### **4.4.3 certInstall** 

安装证书。 

1 `export` **`const`** `certInstall: (p7b: string, doubleP7b?: string, encryptPrivateKeyBase64?: string) => number;` 

- 输入: 

**–** p7b: 证书数据 

   - doubleP7b: 双证书数据, 可选 

   - encryptPrivateKeyBase64: 加密私钥, 可选 

- 返回值: 

   - number: 结果码 

### **4.4.4 certList** 

获取证书列表。 

- 1 `export` **`const`** `certList: () => string[];` 

• 输入: 

**–** 无 

- 返回值: 

   - string[]: 证书列表 

12 

协同签名客户端接口说明 

2026-04-15 

### **4.4.5 certLoad** 

加载证书。 

1 `export` **`const`** `certLoad: (user?: string, sig?:` **`boolean`** `) => SCResult;` 

• 输入: 

**–** user: 用户名, 可选,默认为当前登录用户 

**–** sig: 是否加载签名证书, 默认位签名证书 

- 返回值: 

**–** SCResult: 加载结果和状态码 

- status: 状态码 

- str: 返回的证书数据 

### **4.4.6 certPublicKey** 

获取公钥。 

1 `export` **`const`** `certPublicKey: (cert: ArrayBuffer|string) => SCResult;` 

• 输入: 

**–** cert: 证书数据 

- 返回值: 

**–** SCResult: 公钥数据和状态码 

- status: 状态码 

- str: 返回的证书公钥 

### **4.4.7 certInfo** 

获取证书信息。 

1 `export` **`const`** `certInfo: (sig?:` **`boolean`** `) => SCResult;` 

• 输入: 

**–** sig: 证书类型,默认为签名证书 

- 返回值: 

13 

协同签名客户端接口说明 

2026-04-15 

- SCResult: 证书信息和状态码 

   - status: 状态码 

   - str: 返回的证书信息 

### **4.4.8 certRemoteList** 

获取远程证书列表。 

1 `export` **`const`** `certRemoteList: () => string[];` 

- 输入: 

**–** 无 

- 返回值: 

**–** string[]: 远程证书列表 

## **4.5** 密码服务 

### **4.5.1 signData** 

数字签名。 

1 `export` **`const`** `signData: (nSignType: number, data: ArrayBuffer|string) => SCResult;` 

- 输入: 

**–** nSignType: 签名摘要计算类型,参考 DigestAlgorithm 

**–** data: 待签名数据 

- 返回值: 

**–** SCResult: 签名结果和状态码 

- status: 状态码 

- blob: 返回的签名结果数据 

### **4.5.2 verifySignature** 

验证签名。 

1 `export` **`const`** `verifySignature: (nSignType: number, pubkey: ArrayBuffer, data: ArrayBuffer|string, signature: ArrayBuffer) => number;` 

14 

协同签名客户端接口说明 

2026-04-15 

• 输入: 

**–** nSignType: 签名摘要计算类型,参考 DigestAlgorithm 

**–** pubkey: 公钥 

**–** data: 待验证数据 

**–** signature: 签名数据 

- 返回值: 

**–** number: 验证结果码 

### **4.5.3 encrypt** 

加密数据。 

1 `export` **`const`** `encrypt: (algs: number, key: ArrayBuffer, iv: ArrayBuffer, plain: ArrayBuffer, pad: number) => SCResult;` 

• 输入: 

**–** algs: 加密算法,参考 CipherAlgorithm 

**–** key: 密钥 

**–** iv: 初始化向量 

**–** plain: 明文数据 

**–** pad: 填充模式 

• 返回值: 

**–** SCResult: 加密结果和状态码 

- status: 状态码 

- blob: 返回的加密结果数据 

### **4.5.4 decrypt** 

解密数据。 

1 `export` **`const`** `decrypt: (algs: number, key: ArrayBuffer, iv: ArrayBuffer, cipher: ArrayBuffer, pad: number) => SCResult;` 

• 输入: 

**–** algs: 解密算法,参考 CipherAlgorithm 

**–** key: 密钥 

**–** iv: 初始化向量 

15 

协同签名客户端接口说明 

2026-04-15 

   - cipher: 密文数据 

   - pad: 填充模式 

- 返回值: 

   - SCResult: 解密结果和状态码 

      - status: 状态码 

      - blob: 返回的解密结果数据 

### **4.5.5 digest** 

计算摘要。 

- 1 `export` **`const`** `digest: (algs: number, dataToHash: ArrayBuffer) => SCResult;` 

• 输入: 

   - algs: 摘要算法,参考 DigestAlgorithm 

   - dataToHash: 待摘要数据 

- 返回值: 

   - SCResult: 摘要结果和状态码 

      - status: 状态码 

      - blob: 返回的摘要值 

### **4.5.6 pkcs7Sign** 

PKCS#7 签名。 

该接口尚未实现 

1 `export` **`const`** `pkcs7Sign: (data: ArrayBuffer, flags: number) => SCResult;` 

• 输入: 

- data: 待签名数据 

**–** flags: 签名方式 

- 返回值: 

**–** SCResult: 签名结果和状态码 

- status: 状态码 

- blob: 返回的结果数据 

16 

协同签名客户端接口说明 

2026-04-15 

### **4.5.7 pkcs7Verify** 

PKCS#7 验签。 

该接口尚未实现 

1 `export` **`const`** `pkcs7Verify: (p7: ArrayBuffer, msg?: ArrayBuffer, cert?: ArrayBuffer, flags?: number) => number;` 

• 输入: **–** p7: 签名数据 **–** msg: 原始数据 **–** cert: 证书数据 **–** flags: 签名方式 • 返回值: **–** number: 验签结果码 

### **4.5.8 sm2Encrypt** 

SM2 加密。 

1 `export` **`const`** `sm2Encrypt: (pubk: ArrayBuffer|string, data: ArrayBuffer|string) => SCResult;` 

• 输入: **–** pubk: 公钥 **–** data: 待加密数据 • 返回值: **–** SCResult: 加密结果和状态码 *status: 状态码 *blob: 返回的加密结果数据 

### **4.5.9 sm2Decrypt** 

SM2 解密。 

1 `export` **`const`** `sm2Decrypt: (encrypted: ArrayBuffer, sig: number) => SCResult;` • 输入: 

17 

协同签名客户端接口说明 

2026-04-15 

   - encrypted: 密文数据 

   - sig: 密钥标志,1 为签名密钥对,否则为加密密钥对 

- 返回值: 

   - SCResult: 解密结果和状态码 

      - status: 状态码 

      - blob: 返回的解密结果数据 

### **4.5.10 exSignData** 

外部密钥签名数据。 

1 `export` **`const`** `exSignData: (nSignType: number, prik: ArrayBuffer, data: ArrayBuffer) => SCResult;` 

- 输入: 

**–** nSignType: 签名摘要计算类型,参考 DigestAlgorithm 

   - prik: 私钥 

   - data: 待签名数据 

- 返回值: 

**–** SCResult: 签名结果和状态码 

- status: 状态码 

- blob: 返回的签名结果数据 

### **4.5.11 exSm2Decrypt** 

外部密钥 SM2 解密。 

1 `export` **`const`** `exSm2Decrypt: (prik: ArrayBuffer, encrypted: ArrayBuffer) => SCResult;` 

- 输入: 

**–** prik: 私钥 

**–** encrypted: 密文数据 

- 返回值: 

**–** SCResult: 解密结果和状态码 

- status: 状态码 

- blob: 返回的解密结果数据 

18 

协同签名客户端接口说明 

2026-04-15 

## **4.6** 服务操作接口 

### **4.6.1 callRemote** 

调用远程服务。 

1 `export` **`const`** `callRemote: (url: string, params?: object, method?:` **`boolean`** `) => SCResult;` 

- 输入: 

**–** url: 服务地址 

**–** params: 请求参数 

   - method: 请求方法 

- 返回值: 

   - SCResult: 远程服务调用结果和状态码 

      - status: HTTP 状态码 

      - str: 返回的响应数据 

## **4.7** 高层接口 

### **4.7.1 wsUserExist** 

### 检查用户是否存在。 

1 `export` **`const`** `wsUserExist: () => SCResult;` 

• 输入: 

**–** 无 

- 返回值: 

**–** SCResult: 检查结果和状态码 

### **4.7.2 wsUserState** 

获取用户状态。 

1 `export` **`const`** `wsUserState: () => SCResult;` 

- 输入: 

19 

协同签名客户端接口说明 

2026-04-15 

**–** 无 

- 返回值: 

   - SCResult: 用户状态和状态码 

      - status: 状态码 

      - num: 用户状态值 

### **4.7.3 wsUserRegister** 

注册用户。 

1 `export` **`const`** `wsUserRegister: (subject: string) => number;` 

- 输入: 

**–** subject: 用户主题信息 

- 返回值: 

**–** number: 注册结果码 

### **4.7.4 wsUserCertificates** 

获取用户证书。 

1 `export` **`const`** `wsUserCertificates: () => SCResult;` 

• 输入: 

**–** 无 

- 返回值: 

**–** SCResult: 用户证书信息和状态码 

- status: 状态码 

- str: 服务器上的用户证书 

### **4.7.5 wsCertDownload** 

下载证书。 

1 `export` **`const`** `wsCertDownload: (authcode?: String) => number;` 

20 

协同签名客户端接口说明 

2026-04-15 

- 输入: 

**–** authcode: 下载授权码,可选 

- 返回值: 

   - number: 下载结果码 

### **4.7.6 wsCertUpdate** 

更新证书。 

1 `export` **`const`** `wsCertUpdate: () => number;` 

- 输入: 

**–** 无 

- 返回值: 

**–** number: 更新结果码 

### **4.7.7 wsCertUpcoming** 

检查证书需要的后续操作。 

1 `export` **`const`** `wsCertUpcoming: (reqId: string) => number;` 

- 输入: 

   - reqId: 请求 ID 

- 返回值: 

   - number: 获取结果码 

21
