# **移动终端密码模块SDK-鸿蒙-V1.0.0** 

# **引入移动终端密码模块SDK** 

将移动终端密码模块SDK `.har` 包文件放入项目中的适当文件夹,如 `libs` 或 `assets` 目录,并把该 `.har` 包文 件加载到项目中。 

```
// oh-package.json5
{
...
"dependencies": {
...
"cosdk": "file:./libs/cosdk.har"
    }
}
```

# **初始化** 

**函数说明:** SDK 初始化 **函数名称:** `init` **调用方式:** 函数调用 **函数定义:** 

```
/**
 * 初始化
 * @param context 上下文对象
```

- `@param host 主机地址` 

- `@param appId 应用 ID` 

- `@param appKey 应用 Key` 

- `@returns true :初始化成功 false :初始化失败 */` 

```
functioninit(context: Context, host: string, appId: string, appKey: string): boolean
```

## **请求参数:** 

|**参数名**|**参数类型**|**参数说明**|**必填**|
|---|---|---|---|
|context|Context|上下文对象|是|
|host|string|主机地址|是|
|appId|string|应用ID|是|
|appKey|string|应用Key|是|

## **返回参数:** 

`true` :初始化成功。 `false` :初始化失败。 

## **调用示例:** 

```
// 移动终端密码模块SDK初始化
constsuccess=init(this.context, 'host', 'appId', 'appKey')
```

其中, `host` 、 `appId` 和 `appKey` 请联系 ZJCA 获取。 

# **生成虚拟介质SN** 

**函数说明:** 生成虚拟介质 SN 

**函数名称:** `generateKeySn` **调用方式:** 函数调用 **函数定义:** 

```
/**
 * 生成虚拟介质SN
 * @return Promise
 */
functiongenerateKeySn(): Promise<string>
```

## **请求参数:** 

无 

## **返回参数:** 

|**参数名**|**参数类型**|**参数说明**|**备注**|
|---|---|---|---|
|code|number|状态码|0表示成功,非0表示失败|
|msg|string|响应信息|当code不为0时,返回错误信息|
|data|string|虚拟介质SN|当code不为0时,此值为空|

## **调用示例:** 

```
// 生成虚拟介质SN
generateKeySn()
.then(data=> {
constkeySN: string =data?.['data']
console.error(`keySN = ${keySN}`)
})
```

# **申请公钥** 

**函数说明:** 申请公钥 **函数名称:** `applyPublicKey` **调用方式:** 函数调用 **函数定义:** 

```
/**
 * 申请公钥
 * @param keySN 虚拟介质SN
 * @param pin PIN码,用来保护密钥
 * @return Promise
 */
functionapplyPublicKey(keySN: string, pin: string): Promise<string>
```

## **请求参数:** 

|**参数名**|**参数类型**|**参数说明**|**必填**|
|---|---|---|---|
|keySN|string|虚拟介质SN|是|
|pin|string|PIN码,用来保护密钥|是|

**返回参数:** 

|**参数名**|**参数类型**|**参数说明**|**备注**|
|---|---|---|---|
|code|number|状态码|0表示成功,非0表示失败|
|msg|string|响应信息|当code不为0时,返回错误信息|
|data|string|公钥|当code不为0时,此值为空|

## **调用示例:** 

```
// 申请公钥
constkeySN='9824080100000802'// 虚拟介质SN
constpin='123456'// PIN码
applyPublicKey(keySN, pin)
.then(data=> {
constpubKey: string =data?.['data']
console.error(`pubKey = ${pubKey}`)
})
```

# **导入证书** 

**函数说明:** 导入证书 **函数名称:** `importCert` **调用方式:** 函数调用 **函数定义:** 

```
/**
 * 导入证书
 * @param keySN 虚拟介质SN
 * @param base64Cert Base64证书
 */
functionimportCert(keySN: string, base64Cert: string): void
```

## **请求参数:** 

|**参数名**|**参数类型**|**参数说明**|**必填**|
|---|---|---|---|
|keySN|string|虚拟介质SN|是|
|base64Cert|string|Base64证书|是|

## **返回参数:** 

无 

## **调用示例:** 

```
constkeySN='9824080100000802'// 虚拟介质SN
constbase64Cert='......'
importCert(keySN, base64Cert)
```

**协同签名** 

## **函数说明:** 协同签名 **函数名称:** `sign` **调用方式:** 函数调用 **函数定义:** 

```
/**
 * 协同签名
 * @param keySN 虚拟介质 SN
```

- `@param pin PIN 码,用来保护密钥` 

- `@param base64Data 待签原文, base64 字符串,当签 hash 时,待签原文是 32 个字节` 

- `@param hash 是否签 hash` 

```
 * @return Promise
 */
functionsign(keySN: string, pin: string, base64Data: string, hash=false):
Promise<string>
```

## **请求参数:** 

|**参数名**|**参数类型**|**参数说明**|**必填**|
|---|---|---|---|
|keySN|string|虚拟介质SN|是|
|pin|string|PIN码,用来保护密钥|是|
|base64Data|string|待签原文,base64字符串,当签hash时,待签原文是32个字节|是|
|hash|boolean|是否签hash|是|

## **返回参数:** 

|**参数名**|**参数类型**|**参数说明**|**备注**|
|---|---|---|---|
|code|number|状态码|0表示成功,非0表示失败|
|msg|string|响应信息|当code不为0时,返回错误信息|
|data|string|签名值|当code不为0时,此值为空|

## **调用示例:** 

### `// 协同签名` 

```
constkeySN='9824080100000802'// 虚拟介质SN
constpin='123456'// PIN码
constbase64Data='MTIzNDU2Nzg5MDEyMzQ1Njc4OTAxMjM0NTY3ODkwMTI='// 签名原文Base64格式
constsignHash=false; // 是否签hash
sign(keySN, pin, base64Data, signHash)
.then(data=> {
constsignedValue: string =data?.['data']
console.error(`signedValue = ${signedValue}`)
})
```

**获取证书** 

**函数说明:** 获取证书 **函数名称:** `getCert` **调用方式:** 函数调用 **函数定义:** 

```
/**
 * 获取证书
 * @param keySN 虚拟介质SN
 * @return s Base64格式的证书
 */
functiongetCert(keySN: string): string
```

## **请求参数:** 

|**参数名**|**参数类型**|**参数说明**|**必填**|
|---|---|---|---|
|keySN|string|虚拟介质SN|是|

## **返回参数:** 

|**参数名**|**参数类型**|**参数说明**|**备注**|
|---|---|---|---|
|code|number|状态码|0表示成功,非0表示失败|
|msg|string|响应信息|当code不为0时,返回错误信息|
|data|string|Base64证书|当code不为0时,此值为空|

## **调用示例:** 

```
constkeySN='9824080100000802'// 虚拟介质SN
constbase64Cert=getCert(keySN)
console.error(`base64Cert = ${base64Cert}`)
```

# **获取证书信息** 

**函数说明:** 获取证书信息 **函数名称:** `getCertInfo` **调用方式:** 函数调用 **函数定义:** 

```
/**
 * 获取证书信息
 * @param keySN 虚拟介质SN
 * @param icert 回调函数
 */
functiongetCertInfo(keySN: string, icert: ICert): void
```

## **请求参数:** 

|**参数名**|**参数类型**|**参数说明**|**必填**|
|---|---|---|---|
|keySN|string|虚拟介质SN|是|

|**参数名**|**参数类型**|**参数说明**|**必填**|
|---|---|---|---|
|icert|ICert|回调函数|是|

## **返回参数:** 

无 

## **调用示例:** 

```
constkeySN='9824080100000802'// 虚拟介质SN
consticert: ICert =Object({
onSuccess: (x509Cert: cert.X509Cert): void=> {
// 在此处获取证书的详细信息
......
    },
onFailed: (error: BusinessError<void>): void=> {
`
thrownewError(错误码:${error.code},错误信息:${error.message}`)
    }
})
getCertInfo(keySN, icert)
```

# **错误码** 

|**错误码**|**错误信息**|
|---|---|
|0|成功|
|非0|错误,错误信息详见返回的msg|
