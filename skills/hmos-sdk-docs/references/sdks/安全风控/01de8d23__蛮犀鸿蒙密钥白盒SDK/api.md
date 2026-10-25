# 蛮犀白盒密钥SDK 接口文档(集成文档) 

## 1. SDK 说明 本SDK 以HAR 形式提供,入口文件为`sdk/Index.ets`,核心导出包括: - `KeyWhiteBoxSdk` - `NativeWhiteBox` - 类型:`EncryptedPayload`、`OneWayRequestPacket`、`OneWayPacketReport`、 `ServerContractHint`、`WhiteBoxOptions` 

## 2. 接入方式 在业务模块中引入HAR 后,按如下方式调用: ```ts import { KeyWhiteBoxSdk } from '@mx/keywhitebox' ``` 

## 3. 核心接口 ### 3.1 encryptText ```ts KeyWhiteBoxSdk.encryptText(plainText: string, options: WhiteBoxOptions): EncryptedPayload ``` 

用途:对文本执行白盒加密。 参数: - `plainText`:待加密字符串 - `options.algorithm`:`'AES' | 'SM4'` - `options.key`:密钥字符串或`Uint8Array` - `options.mode`:`'normal' | 'random' | 'oneWay'` ### 3.2 decryptText ```ts KeyWhiteBoxSdk.decryptText(payload: EncryptedPayload, key: Uint8Array | string): string ``` 

用途:对双向模式密文解密。`oneWay` 模式不允许客户端解密。 ### 3.3 buildOneWayRequest ```ts KeyWhiteBoxSdk.buildOneWayRequest( plainText: string, options: WhiteBoxOptions, clientId: string, 

route: string ): OneWayRequestPacket ``` 

用途:构建单向上送协议包,输出包含`meta`、`fingerprint`、`keySlots`、 `payload`、`nativeEnvelope`、`integrityHex`。 

### 3.4 serialize / deserialize ```ts KeyWhiteBoxSdk.serialize(payload: EncryptedPayload): string KeyWhiteBoxSdk.deserialize(serialized: string): EncryptedPayload ``` 

用途:密文对象与字符串之间转换。 

# ### 3.5 单向协议辅助接口 

- `serializeOneWayRequest(packet)`:协议包序列化 

- `deserializeOneWayRequest(serialized)`:协议包反序列化 

- `inspectOneWayRequest(packet)`:输出报文摘要信息 

- `buildServerContractHint(packet)`:生成服务端对接提示 

- `deriveServerIntegritySeed(packet)`:生成服务端完整性种子 

# ### 3.6 文件接口 

- `encryptFile(sourcePath, targetPath, options)` 

- `decryptFile(sourcePath, targetPath, key)` 

# ### 3.7 Native 接口 

- `KeyWhiteBoxSdk.nativeRuntimeSummary()`:查询native 运行时摘要 

- `NativeWhiteBox.fingerprint(payloadHex, saltHex)`:native 指纹 

- `NativeWhiteBox.mixHex(leftHex, rightHex)`:native 混淆混合 

- `NativeWhiteBox.buildEnvelope(payloadHex, nonceHex, fingerprint)`: 

- native 信封构造 

# ## 4. 调用示例 

```ts 

const payload = KeyWhiteBoxSdk.encryptText('demo', { 

- algorithm: 'SM4', 

- key: '0123456789abcdef', 

- mode: 'oneWay' 

}) 

```
