# 密鸽产品 移动端 SDK 接口文档 

二○二六年五月 

###### 目录 

|1. 范围...............................................................................................................................................1|
|---|
|2. 第三方框架.................................................................................................................................. 1|
|3. SDK集成方式...............................................................................................................................1|
|3.1. SDK 集成........................................................................................................................... 1|
|3.2. DevEco-Studio 配置....................................................................................................... 1|
|3.2.1 运行环境配置........................................................................................................ 1|
|4. 接口定义...................................................................................................................................... 2|
|4.1. 初始化SDK.......................................................................................................................2|
|4.1.1 SDK初始化.............................................................................................................2|
|4.2. CPK管理...........................................................................................................................2|
|4.2.1 请求CPK密钥对....................................................................................................2|
|4.2.2 导出密钥................................................................................................................ 3|
|4.2.3 CPK公钥矩阵加密.................................................................................................3|
|4.2.4 CPK私钥解密.........................................................................................................4|
|4.3. 加密工具.......................................................................................................................... 4|
|4.3.1 数据转Hex字符串................................................................................................4|
|4.3.2 hex字符串转字节数据......................................................................................... 5|
|4.3.3 md5摘要算法........................................................................................................5|
|4.3.4 sha256摘要算法................................................................................................... 6|
|4.3.5 sm3摘要算法........................................................................................................ 6|
|4.3.6 3DES加密算法.......................................................................................................7|
|4.3.7 3DES解密算法.......................................................................................................8|
|4.3.8 合并Uint8Array......................................................................................................8|
|4.3.9 sm2 解密............................................................................................................... 9|
|4.3.10 sm4-CBC 加密......................................................................................................9|
|4.3.11 sm4-CBC 解密....................................................................................................10|

#### 修订记录 

|编号|日期|描述|版本|作者|审核|发布日期|
|---|---|---|---|---|---|---|
|1|2026.05.20|预定义接口|V1.0|郭旭|||

## 1. 范围 

此文档用于密鸽加密 SDK 集成使用。功能包含请求 CPK 密钥对、导出密钥、使用 公钥矩阵制作信封、使用私钥解密、哈希字符串转换、md5 摘要算法、sha256 摘要算 法、sm3 消息摘要算法、3DES 加密、3DES 解密、sm4-CBC 加密、sm4-CBC 解密、sm2 加解密等功能。 

## 2. 第三方框架 

使用系统 Api 实现,未使用第三方框架 

## 3. **SDK** 集成方式 

### 3.1. SDK 集成 

- 将 migelibrary.har 添加到工程中。 

### 3.2. DevEco-Studio 配置 

### 3.2.1 运行环境配置 

- 开发 IDE: 华为官方 IDE, Dev_ECO 版本 6.0.2 及以上 

- ●SDK 版本:5.0.1(13)及以上 

- ●runtimeOS:HarmonyOS 

1 

## 4. 接口定义 

### 4.1. 初始化 **SDK** 

### 4.1.1 **SDK** 初始化 

##### 接口名称: 

public initMigeSDK(context: Context | undefined, isLog: boolean): boolean 接口说明:初始化 SDK。 

##### 参数说明: 

|名称|类型|必填|说明|
|---|---|---|---|
|context|Context|Y|上下文|
|isLog|boolean|Y|是否打印日志|

##### 代码示例: 

MigeSDKAuth.getInstance().initMigeSDK(this.getUIContext().getHostContext(), true); 

### 4.2. **CPK** 管理 

### 4.2.1 请求 **CPK** 密钥对 

##### 接口名称: 

public IWGenKeyRequest(userInfo: string): string | undefined 

接口说明:通过接口获取用户对应的 CPK 密钥对。 

参数说明: 

|名称|类型|必填|说明|
|---|---|---|---|
|userInfo|string|Y|用户标识|
|返回参数说明:||||
|名称|类型|说明||

2 

返回的密钥信息 

res string 

##### 代码示例: 

let res= CPKHandle.getInstance().IWGenKeyRequest(userID); 

### 4.2.2 导出密钥 

##### 接口名称: 

public IWImportKeyPair(keyCard: string): string | undefined 

接口说明:根据传入的密钥信息,导出 CPK 密钥对字符串保存在本地。 

##### DKConfiguration 参数说明: 

|名称|类型|必填|说明|
|---|---|---|---|
|keyCard|string|Y|密钥信息|
|返回参数说明:||||
|名称|类型|说明||
|res|string|导出的|服务器密钥对|

##### 代码示例: 

let res= CPKHandle.getInstance().IWImportKeyPair(keyCard); 

### 4.2.3 **CPK** 公钥矩阵加密 

##### 接口名称: 

public IWSM2Encrypt(pubMatrixData: Uint8Array, userInfo: string, cipherText: string): string | undefined 

接口说明:根据公钥使用 SM2 加密生成加密数据。 

##### DKConfiguration 参数说明: 

|名称|类型|必填|说明|
|---|---|---|---|
|pubMatrixData|Uint8Array|Y|公钥|
|userInfo|string|Y|用户信息|

3 

|cipherText|string|Y 原文|
|---|---|---|
|返回参数说明:|||
|名称|类型|说明|
|res|string|加密后的信封数据|

##### 代码示例: 

let res = CPKHandle.getInstance().IWSM2Encrypt(pkmData, identify, data) 

### 4.2.4 **CPK** 私钥解密 

##### 接口名称: 

public IWSM2Decrypt(keyString: string, cipherText: string): string | undefined 接口说明:根据公钥使用 SM2 加密生成加密数据。 

##### DKConfiguration 参数说明: 

|名称|类型|必填|说明|
|---|---|---|---|
|keyString|string|Y|私钥|
|cipherText|string|Y|原文|
|返回参数说明:||||
|名称|类型|说明||
|res|string|解密后|的结果数据|

##### 代码示例: 

let res = CPKHandle.getInstance().IWSM2Decrypt(key as string, env) 

### 4.3. 加密工具 

### 4.3.1 数据转 **Hex** 字符串 

##### 接口名称: 

static hexEncodeString(data: Uint8Array): string 

4 

接口说明:将字节数组转成 hex 字符串。 

##### DKConfiguration 参数说明: 

|名称|类型|必填|说明|
|---|---|---|---|
|data|Uint8Array|Y|字节数据|
|返回参数说明:||||
|名称|类型|说明||
|res|string|hex字|符串|

##### 代码示例: 

let res = CryptoUtils.hexEncodeString(data) 

### 4.3.2 **hex** 字符串转字节数据 

##### 接口名称: 

static stringData(data: string): Uint8Array 

接口说明:将 hex 字符串转为字节数据。 

##### DKConfiguration 参数说明: 

|名称|类型|必填|说明|
|---|---|---|---|
|data|string|Y|hex字符串|
|返回参数说明:||||
|名称|类型|说明||
|res|Uint8Array|字节数|据|

##### 代码示例: 

let res = CryptoUtils.stringData(data) 

### 4.3.3 **md5** 摘要算法 

##### 接口名称: 

static domd5(message: Uint8Array): Uint8Array 

5 

接口说明:将数据进行 md5 加密。 

##### DKConfiguration 参数说明: 

|名称|类型|必填|说明|
|---|---|---|---|
|message|Uint8Array|Y|原文|
|返回参数说明:||||
|名称|类型|说明||
|res|Uint8Array|加密结|果|

##### 代码示例: 

let res = CryptoUtils.domd5(data) 

### 4.3.4 **sha256** 摘要算法 

##### 接口名称: 

static dk_sha256(message: Uint8Array): Uint8Array 

接口说明:将数据进行 sha256 加密。 

##### DKConfiguration 参数说明: 

|名称|类型|必填|说明|
|---|---|---|---|
|message|Uint8Array|Y|原文|
|返回参数说明:||||
|名称|类型|说明||
|res|Uint8Array|加密结|果|

##### 代码示例: 

let res = CryptoUtils.dk_sha256(data) 

### 4.3.5 **sm3** 摘要算法 

##### 接口名称: 

static doSm3(message: Uint8Array): Uint8Array 

6 

##### 接口说明:将数据进行 sm3 加密。 

DKConfiguration 参数说明: 

|名称|类型|必填|说明|
|---|---|---|---|
|message|Uint8Array|Y|原文|
|返回参数说明:||||
|名称|类型|说明||
|res|Uint8Array|加密结|果|

##### 代码示例: 

let res = CryptoUtils.doSm3(data) 

### 4.3.6 **3DES** 加密算法 

##### 接口名称: 

static async tripleDesEncrypt(plainText: string, key: string): Promise<string> 

接口说明:对数据进行 3DES 加密。 

##### DKConfiguration 参数说明: 

|名称|类型|必填|说明|
|---|---|---|---|
|plainText|string|Y|原文|
|key|string|Y|密钥|
|返回参数说明:||||
|名称|类型|说明||
|res|string|加密结|果|

##### 代码示例: 

let encStr = await CryptoUtils.tripleDesEncrypt(data, BaseApi.NET_KEY); 

7 

### 4.3.7 **3DES** 解密算法 

##### 接口名称: 

static async tripleDesDecrypt(cipherText: string, key: string): 

Promise<string> 

接口说明:对数据进行 3DES 解密。 

##### DKConfiguration 参数说明: 

|名称|类型|必填|说明|
|---|---|---|---|
|cipherText|string|Y|原文|
|key|string|Y|密钥|
|返回参数说明:||||
|名称|类型|说明||
|res|string|解密结|果|

##### 代码示例: 

let desStr = await CryptoUtils.tripleDesDecrypt(data, BaseApi.NET_KEY); 

### 4.3.8 合并 **Uint8Array** 

##### 接口名称: 

public static mergeUint8Arrays(...arrays: Uint8Array[]): Uint8Array 接口说明:对多个 Uint8Array 合并成一个。 

##### DKConfiguration 参数说明: 

|名称|类型|必填|说明|
|---|---|---|---|
|arrays|Uint8Array[]|Y|数据数组|
|返回参数说明:||||
|名称|类型|说明||
|res|Uint8Array|合并的|Uint8Array结果|

代码示例: 

8 

let res = CryptoUtils.mergeUint8Arrays(headerOneData, resData) 

### 4.3.9 **sm2** 解密 

##### 接口名称: 

static SM2decrypt(cipherText: string, keyStr: string): string 接口说明:对数据进行 sm2 解密。 

##### DKConfiguration 参数说明: 

|名称|类型|必填|说明|
|---|---|---|---|
|cipherText|string|Y|原文|
|keyStr|string|Y|密钥|
|返回参数说明:||||
|名称|类型|说明||
|res|string|解密结|果|

##### 代码示例: 

let res = CryptoUtils.SM2decrypt(data, key) 

### 4.3.10 **sm4-CBC** 加密 

##### 接口名称: 

= public async encData(data: Uint8Array, key?: Uint8Array, padding: string "PKCS7", progress?:(progress: number, updateData: Uint8Array) => void): Promise<boolean> 

接口说明:对数据进行 sm2 解密。 

DKConfiguration 参数说明: 

|名称|类型|必填|说明|
|---|---|---|---|
|data|Uint8Array|Y|原文|
|key|Uint8Array|N|密钥|
|padding|string|Y|加密模式|

9 

|progress|(progress: number,|Y|加密过程的数据,加密结|
|---|---|---|---|
||updateData:||果从这里获取|
||Uint8Array) => void)|||
|返回参数说明:||||
|名称|类型|说明||
|res|boolean|加密是|否成功|

##### 代码示例: 

let res = await sm4Enc.encData(headerTwo, undefined, "PKCS7", (_, resData) => { 

if (resData) { encHeaderTwo = resData model.encDataLen = resData.length } }) 

### 4.3.11 **sm4-CBC** 解密 

##### 接口名称: 

= public async decData(data: Uint8Array, key?: Uint8Array, padding: string "PKCS7", progress?:(progress: number, updateData: Uint8Array) => void): Promise<boolean> 

接口说明:对数据进行 sm2 解密。 

##### DKConfiguration 参数说明: 

|名称|类型|必填|说明|
|---|---|---|---|
|data|Uint8Array|Y|原文|
|key|Uint8Array|N|密钥|
|padding|string|Y|加密模式|
|progress|(progress: number,|Y|解密过程的数据,解密结|
||updateData:||果从这里获取|
||Uint8Array) => void)|||

10 

##### 返回参数说明: 

|名称|类型|说明|
|---|---|---|
|res|boolean|解密是否成功|

##### 代码示例: 

let res = await sm4Enc.decData(new Uint8Array(buf.slice(16,32)), undefined, "NoPadding", (_, resData) => { 

headerOneData = CryptoUtils.mergeUint8Arrays(headerOneData, resData) 

- }) 

11
