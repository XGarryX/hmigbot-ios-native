Cloud Core 标准文档 文件编号:CC-TECH-IP-A-110 

云核客户端国密SSL (鸿蒙版) 用户手册 

北京云核网络技术有限公司 

2025 年 1 月 22 日 

### 文档修改记录 

|版本|内容|编写人|编写日期|审核人|审核日期|
|---|---|---|---|---|---|
|1.0.1|初版|changbf|2024-10-12|||
|1.0.1|savefile更换为download,添加upload上传|changbf|2024-10-24|||
|1.0.2|使用异步交易,提升交易效率|changbf|2024-11-02|||
|1.0.3|添加clear,可在登出等场景清楚cookie|changbf|2024-11-05|||
|1.0.4|form请求使用curl_mime代替curl_formadd|changbf|2024-11-20|||
|1.0.5|cookie清除中添加已有easy handle的清除|changbf|2024-12-04|||
|1.1.0|正式文档发布,同时增加异步和同步,适应 不同场景|changbf|2024-12-13|||

#### 版权申明: 

本文档的版权属于北京云核网络技术有限公司,任何人或组织未经许可,不 得擅自修改、拷贝或以其它方式使用本文档中的内容。 

## 目   录 

|1. 引言.......................................................................................................................... 1|
|---|
|1.1编写目的.......................................................................................................... 1|
|1.2背景知识及参考资料...................................................................................... 2|
|1.3使用环境.......................................................................................................... 2|
|2. 概述.......................................................................................................................... 2|
|2.1系统构成.......................................................................................................... 2|
|2.2功能特点.......................................................................................................... 2|
|2.3技术特点.......................................................................................................... 3|
|2.4接口描述.......................................................................................................... 3|
|2.4.1引用....................................................................................................... 3|
|2.4.2 cGmSSL ................................................................................................. 3|
|2.4.3 HttpDataType ......................................................................................... 4|
|2.4.4 HttpProtocol ........................................................................................... 4|
|2.4.5 RequestMethod ...................................................................................... 4|
|2.4.6 ResponseCode ........................................................................................ 5|
|2.4.7 SSLPolicy .............................................................................................. 7|
|2.4.8 SSLVersion ............................................................................................. 7|
|2.4.9 CHttpClient ............................................................................................ 7|
|2.4.10 HttpGlobalOptions ............................................................................... 8|
|2.4.11 HttpRequestOptions ............................................................................. 9|
|3. 开发流程概述........................................................................................................ 10|
|3.1获取请求对象................................................................................................ 10|
|3.2设置全局参数................................................................................................ 10|
|3.3发起交易........................................................................................................ 10|

云核客户端安全输入系统(鸿蒙版) 用户手册

# **1.** 引言 

## **1.1** 编写目的 

国密 SSL 协议在GM/T 中没有单独规范的文件,而是在SSL VPN 技术规范中定义 了国密SSL 协议。GMT 0024-2014《SSL VPN 技术规范》中,国密 SSL 协议内容参照 传输层安全协议(RFC 4346 TLS1.1),按照我国相关密码政策和法规,结合我国实际 应用需求及实践经验,在TLS 1.1 的握手协议中,增加了ECC、IBC 的认证模式和密 钥交换模式,取消了DH 密钥交换方式,修改了密码套件的定义,另外就是增加了网 关到网关协议。 

国密SSL 协议包括握手协议、密码规格变更协议、报警协议、网关到网关协议和 记录层协议。握手协议用于身份鉴别和安全参数协商;密码规格变更协议用于通知安 全参数的变更;报警协议用于关闭通知和对错误进行报警;网关到网关协议用于建立 网关到网关的传输层隧道;记录层协议用于传输数据的分段、压缩及解压缩、加密及 解密、完整性校验等。 

国密SSL 握手协议族包含密码规格变更协议、握手协议和报警协议3 个子协议, 用于通信双方协商出可供记录层使用的安全参数,进行身份验证以及向对方报告错误 等。 

国密SSL 握手协议协商的会话包括: 

- ⚫ 会话标识:有服务端选取的随意的字节序列,用于识别活跃或可恢复的会话 

- ⚫ 证书:X.509 V3 格式的数字证书,符合GM/T 0015 

- ⚫ 压缩方法:压缩数据的算法 

- ⚫ 密码规格:指定的密码算法 

- ⚫ 主密钥:客户端和服务端共享的48 字节的密钥 

- ⚫ 重用标识:标明能否用该会话发起一个新连接的标识 

利用以上数据可以产生安全参数,利用握手协议的重用特性,可以使用相同会话 建立多个连接。 

文件编号:CC-TECH-IP-A-002 

第1页 

云核客户端安全输入系统(鸿蒙版) 用户手册

云核客户端国密SSL 在原有国际SSL 的基础上新增国密SSL,为金融机构在 Android 手机上国密化提供解决方案。 

## **1.2** 背景知识及参考资料 

假定开发人员对下列技术有一定的理解: 

|技术|有关内容|
|---|---|
|鸿蒙SDK|鸿蒙ETS 的基本知识|
|SSL|SSL 握手协议、SSL 密码参数修改协议、应用数据协议等|
|NAPI-node|实现ArkTS/TS/JS 和C/C++之间的交互|

## **1.3** 使用环境 

鸿蒙星河版。 

# **2.** 概述 

## **2.1** 系统构成 

云核客户端国密SSL 鸿蒙版本以HAR 格式提供,由两部分构成: 

协议核心实现模块:由C++实现的SO 动态库。 

接口模块:由TS 实现。 

## **2.2** 功能特点 

鸿蒙国密 SSL 使用静态共享保(HAR)的引用方式,SO 动态库实现算法主体, typescript 提供接口,通过 HAR 实现国密 SSL 通讯,具备以下基本特征: 

- ⚫ 支持 POST、GET、PUT、DELETE、HEAD、TRACE、OPTIONS 请求 

- ⚫ 支持文件下载和进度提示 

- ⚫ 支持国密 SSL 单向协议 

- ⚫ 支持国密 SSL 双向协议 

- ⚫ 支持 HTTP1.1/2/3 

- ⚫ 支持请求头设置 

- ⚫ 支持字符串/对象请求体 

- ⚫ 支持 SSL2/SSL3/TLS1.0/TLS1.1/TLS1.2/TLS1.3 

文件编号:CC-TECH-IP-A-002 

第2页 

云核客户端安全输入系统(鸿蒙版) 用户手册

## **2.3** 技术特点 

- ⚫ 通过配置,提供国际、国密; 

- ⚫ 提供并发通讯; 

## **2.4** 接口描述 

### **2.4.1** 引用 

|对象|说明|
|---|---|
|`cGmSSL`|国密SSL对象创建接口|
|`CertType`|枚举,证书类型|
|`HttpDataType`|枚举,Http数据类型|
|`HttpProtocol`|枚举,`http`协议|
|`RequestMethod`|枚举,请求方法|
|`ResponseCode`|枚举,`http`应答结果码|
|`SSLPolicy`|枚举,`SSL`握手策略|
|`SSLVersion`|枚举,`SSL`版本|
|`CHttpClient`|`Http`请求对象|
|`HttpGlobalOptions`|全局设置|
|`HttpRequestOptions`|`Http`请求选项|
|`HttpResponse`|`Http`应该结果|

### **2.4.2 cGmSSL** 

**`export class`** `cGmSSL {` _`/** *`_ 国密 _`SSL`_ 版本号 _`* @returns`_ 版本号 _`*/`_ **`public static`** `getVersion(): string {` **`return`** `ccGmSSL.getVersion() }` _`/** *`_ 创建 _`http client`_ 句柄, 在不使用时自动释放 _`* @returns httpclient`_ 句柄 _`*/`_ **`public static`** `createCHttpClient(): CHttpClient {` **`return`** `ccGmSSL.createCHttpClient(); } }` 

文件编号:CC-TECH-IP-A-002 

第3页 

云核客户端安全输入系统(鸿蒙版) 用户手册

### **2.4.3 HttpDataType** 

```
/**
```

_`*  AUTO:`_ 根据 _`response`_ 返回的 _`MIME`_ ,确定数据类型 _`*  STRING:`_ 数据结果为字符串 _`*  OBJECT:`_ 数据结果为对象 _`(Json`_ 对象 _`) *  ARRAY_BUFFER:`_ 数据流 _`*/`_ 

```
export enum HttpDataType {
AUTO = 0,
STRING = 1,
OBJECT = 2,
ARRAY_BUFFER = 3
}
```

### **2.4.4 HttpProtocol** 

```
/**
```

_`*  HTTP_DEFAULT:`_ 不制定版本,由当前 _`Har`_ 中决定,当前默认值问 _`1.1 *  HTTP1_1:`_ 采用 _`HTTP/1.1`_ 进行通信。 _`HTTP/1.1`_ 是一个非常成熟和广泛支持的协议版本, 适用于大多数网络通信需求 _`*  HTTP2:`_ 采用 _`HTTP/2`_ 进行通信 _`*  HTTP3:`_ 采用 _`HTTP/3`_ 进行通信 _`*/`_ 

```
export enum HttpProtocol {
HTTP_DEFAULT,
HTTP1_1,
HTTP2,
HTTP3
}
```

### **2.4.5 RequestMethod** 

```
/**
```

- _`HTTP`_ 请求方法 

- _`GET:`_ 没有请求体,因数据通过 _`URL`_ 发送,使用时避免发送敏感数据。 

- _`POST:`_ 用于提交数据给服务器,例如提交表单或上传文件,数据通常作为请求体发送。 

- _`PUT:`_ 用于更新资源。它通常用于更新资源的全部内容,数据通常作为请求体发送。 

- _`DELETE:`_ 用于删除指定的资源,不需要请求体。 

- _`HEAD:`_ 与 _`GET`_ 类似,但是它不返回请求的响应体,只返回头部信息。 

- _`TRACE:`_ 用于沿着到目标资源的路径执行一个消息回环测试。它回应了请求的最终接收者收 到的原始请求,这样客户端可以看到中间代理添加或更改了哪些首部。 

- _`OPTIONS:`_ 用于描述目标资源的通信选项。可以通过这个方法来确定服务器支持哪些 _`HTTP`_ 方法,或者针对特定资源支持哪些自定义的请求头。 

文件编号:CC-TECH-IP-A-002 

第4页 

云核客户端安全输入系统(鸿蒙版) 用户手册

```
 */
export enum RequestMethod {
GET     = "GET",
POST    = "POST",
PUT     = "PUT",
DELETE  = "DELETE",
HEAD    = "HEAD",
TRACE   = "TRACE",
OPTIONS = "OPTIONS",
}
```

### **2.4.6 ResponseCode** 

```
/**
```

- 响应码( _`Response Code`_ )是服务器发送回客户端的数字状态代码,是 _`HTTP`_ 请求处理结果。 

- _`*   2xx:`_ 成功状态码 

- _`200 OK:`_ 请求成功,服务器返回了请求的资源。 

- _`201 Created:`_ 请求成功,并且服务器创建了新的资源。 

- _`202 Accepted:`_ 请求已被接受处理,但处理尚未完成。 

- _`203 Non-Authoritative Information:`_ 服务器是一个转换代理服务器,它返回了资源 的原始响应的修改版。 

- _`204 No Content:`_ 请求成功,但没有返回任何内容。 

- _`205 Reset Content:`_ 请求成功,客户端应重置文档视图。 

- _`206 Partial Content:`_ 服务器成功处理了部分 _`GET`_ 请求。 

- _`3xx:`_ 重定向状态码 

- _`300 Multiple Choices:`_ 资源有多种表示,用户可以选择一个。 

- _`301 Moved Permanently:`_ 请求的资源已永久移动到新位置。 

- _`302 Found:`_ 请求的资源临时移动到新位置。 

- _`303 See Other:`_ 服务器发送了一个新的位置,客户端应该使用 _`GET`_ 请求它。 

- _`304 Not Modified:`_ 资源未修改,可以使用缓存版本。 

- _`305 Use Proxy:`_ 客户端应通过代理访问请求的资源。 

- _`307 Temporary Redirect:`_ 请求的资源临时移动到新位置,但应保持原始请求方法。 

- _`4xx:`_ 客户端错误状态码 

- _`400 Bad Request:`_ 服务器无法理解请求。 

- _`401 Unauthorized:`_ 请求需要用户身份验证。 

- _`403 Forbidden:`_ 服务器拒绝请求。 

- _`404 Not Found:`_ 请求的资源不存在。 

- _`405 Method Not Allowed:`_ 请求行中指定的方法不允许用于请求的资源。 

- _`406 Not Acceptable:`_ 服务器无法生成符合客户端要求的响应。 

- _`407 Proxy Authentication Required:`_ 客户端必须首先通过代理服务器进行身份验 证。 

- _`408 Request Timeout:`_ 服务器等待客户端发送的请求时间过长,请求超时。 

- _`409 Conflict:`_ 请求与服务器当前状态冲突。 

- _`410 Gone:`_ 请求的资源已被永久删除。 

文件编号:CC-TECH-IP-A-002 

第5页 

云核客户端安全输入系统(鸿蒙版) 用户手册

_`*   5xx:`_ 服务器错误状态码 

_`*    500 Internal Server Error:`_ 服务器遇到了一个意外的情况,阻止它完成请求。 _`*    501 Not Implemented:`_ 服务器不支持请求的功能。 _`*    502 Bad Gateway:`_ 服务器作为网关或代理,从上游服务器收到了无效的响应。 _`*    503 Service Unavailable:`_ 服务器目前无法处理请求,通常是暂时性的。 _`*    504 Gateway Timeout:`_ 服务器作为网关或代理,没有及时从上游服务器收到响应。 _`*    505 HTTP Version Not Supported:`_ 服务器不支持请求的 _`HTTP`_ 版本。 _`*/`_ 

```
export enum ResponseCode {
OK = 200,
CREATED,
ACCEPTED,
NOT_AUTHORITATIVE,
NO_CONTENT,
RESET_CONTENT,
PARTIAL_CONTENT,
MULT_CHOICE = 300,
MOVED_PERM,
MOVED_TEMP,
SEE_OTHER,
NOT_MODIFIED,
USE_PROXY,
BAD_REQUEST = 400,
UNAUTHORIZED,
PAYMENT_REQUIRED,
FORBIDDEN,
NOT_FOUND,
BAD_METHOD,
NOT_ACCEPTABLE,
PROXY_AUTH,
CLIENT_TIMEOUT,
CONFLICT,
GONE,
LENGTH_REQUIRED,
PRECON_FAILED,
ENTITY_TOO_LARGE,
REQ_TOO_LONG,
UNSUPPORTED_TYPE,
INTERNAL_ERROR = 500,
NOT_IMPLEMENTED,
BAD_GATEWAY,
UNAVAILABLE,
GATEWAY_TIMEOUT,
```

文件编号:CC-TECH-IP-A-002 

第6页 

云核客户端安全输入系统(鸿蒙版) 用户手册

```
VERSION
}
```

### **2.4.7 SSLPolicy** 

_`/**`_ _`*  SSL`_ 握手策略 _`*   SSLPOLICY_DEFAULT:`_ 默认 _`*   SSLPOLICY_RSAThenSM2:`_ 先 _`RSA`_ 握手,然后 _`SM2`_ 握手 _`*   SSLPOLICY_RSAThenSM2:`_ 先 _`SM2`_ 握手,然后 _`RSA`_ 握手 _`*/`_ **`export enum`** `SSLPolicy { SSLPOLICY_DEFAULT, SSLPOLICY_RSAThenSM2, SSLPOLICY_SM2ThenRSA }` 

### **2.4.8 SSLVersion** 

_`/**`_ _`*  SSL`_ 协议版本 _`,`_ 默认国密协议 _`*/`_ **`export enum`** `SSLVersion { SSLVERSION_DEFAULT, SSLVERSION_TLSv1,` _`/* TLS 1.x */`_ `SSLVERSION_SSLv2, SSLVERSION_SSLv3, SSLVERSION_TLSv1_0, SSLVERSION_TLSv1_1, SSLVERSION_TLSv1_2, SSLVERSION_TLSv1_3, SSLVERSION_GMTLS` _`// GM SSL version(GM-T 0024-2014)`_ `}` 

### **2.4.9 CHttpClient** 

_`/**`_ _`*  Http Client`_ 对象,用于发起交易请求 _`*/`_ **`export interface`** `CHttpClient {` _`/** *`_ 使用回调,发起请求。 无 _`option`_ 

文件编号:CC-TECH-IP-A-002 

第7页 

云核客户端安全输入系统(鸿蒙版) 用户手册

```arkts
_`* @param url`_ 请求地址 _`* @param callback`_ 返回交易结果 _`*/`_ `request(url: string, callback: AsyncCallback<HttpResponse>): void;` _`/** *`_ 使用回调,发起请求 _`* @param url`_ 请求地址 _`* @param options`_ 请求选项 _`* @param callback`_ 返回交易结果 _`*/`_ `request(url: string, options: HttpRequestOptions, callback: AsyncCallback<HttpResponse>): void;` _`/** *`_ 使用 _`Promise`_ ,发起请求 _`* @param url`_ 请求地址 _`* @param options`_ 请求选项 _`* @return s`_ 返回交易结果 _`*/`_ `request(url: string, options?: HttpRequestOptions): Promise<HttpResponse>;` 
```

_`/** *`_ 设置请求的全局选项 _`* @param option`_ 全局选项 _`*/`_ `set(option: HttpGlobalOptions): void; }` 

### **2.4.10 HttpGlobalOptions** 

_`/**`_ _`*  http`_ 请求全局选项 _`*/`_ **`export  interface`** `HttpGlobalOptions { debug?: boolean,` _`default is false. if this parameter is true, Hilog will print info`_ `readTimeout?: number;` _`// Read timeout period. The default value is 60,000, in ms.`_ `connectTimeout?: number;` _`// Connection timeout interval. The default value is 60,000, in ms.`_ `usingProtocol?: HttpProtocol;` _`// default is automatically specified by`_ 

文件编号:CC-TECH-IP-A-002 

第8页 

云核客户端安全输入系统(鸿蒙版) 用户手册

```
the system.
sslVersion?: SSLVersion;
sslPolicy?: SSLPolicy;
usingProxy?: boolean | connection.HttpProxy;
caCerts?: string;
sslVerify?: boolean; // If this parameter is set, it will via the
incoming url to verify host.
maxLimit?: number;   // The maximum limit of the request .
}
```

### **2.4.11 HttpRequestOptions** 

```
/**
```

_`*`_ 单次请求的参数选项 _`*/`_ **`export  interface`** `HttpRequestOptions { method?: RequestMethod;` _`//`_ 默认 _`GET.`_ `extraData?: string | Object | Uint8Array;` _`// body`_ 数据 _`,`_ 支持三种数据格式 `expectDataType?: HttpDataType;` _`//`_ 期望返回的数据。当返回数据是 _`Object`_ ,可转换成希望的任何类型,当返回 _`string`_ ,可转成成希望的 _`string`_ 和 _`array`_ `header?: Object | string;` _`// HTTP request header.`_ `readTimeout?: number;` _`// Read timeout`_ 不设置使用全局 `connectTimeout?: number;` _`// Connection timeout`_ 不设置使用全局 `realTimeReturn?: boolean;` _`//`_ 实时返回数据,当文件存储时,只返回进度 `download?: string;` _`//`_ 设置数据保存到文件 _`/`_ 路径。当设置路径时,文件 名从返回 _`header`_ 中的 _`Content-Disposition`_ 获取,若获取不到生成随机文件名 `upload?: string;` _`//`_ 设置上传的文件路径,并在 _`header`_ 中使用 _`filename`_ 通知服务端上传的文件名 `usingProtocol?: HttpProtocol;` _`// http`_ 协议 `sslVersion?: SSLVersion;` _`// TLS v1.0 or later.`_ `sslPolicy?: SSLPolicy;` _`// default use sslVersion.`_ `caCerts?: string; }` 

_`/**`_ _`* Defines the response to an HTTP request. */`_ **`export interface`** `HttpResponse { result: string | Object | Uint8Array;` _`// result can be  string / Uint8Array / Object.`_ `resultLength: number;` _`//`_ 结果长度 

文件编号:CC-TECH-IP-A-002 

第9页 

云核客户端安全输入系统(鸿蒙版) 用户手册

`receiveLength: number;` _`//`_ 本次收到长度 `resultType: HttpDataType;` _`//`_ 结果数据类型 `responseCode: ResponseCode | number;` _`// Server status code. /** * All headers in the response from the server. */`_ `header: Object;` _`// All headers in the response from the server.`_ `cookies: string;` _`// Cookies returned by the server.`_ `}` 

# **3.** 开发流程概述 

## **3.1** 获取请求对象 

```
   import {cGmSSL } from '@security/cGmSSL';
   let httpClient: CHttpClient = cGmSSL.createCHttpClient()
```

## **3.2** 设置全局参数 

_`//`_ 全局设置 `httpClient.set({ debug:` **`true`** `,` _`// hilog`_ 输出通讯过程 `readTimeout: 45, connectTimeout: 60, usingProtocol: HttpProtocol.HTTP_DEFAULT, sslVersion: SSLVersion.SSLVERSION_DEFAULT, caCerts:'', sslVerify:` **`false`** `,` _`//`_ 不验证服务端证书和域名 `maxLimit: 10` _`//`_ 同时并发最大 _`10`_ 个 `})` 

## **3.3** 发起交易 

```
httpClient.request(this.baseURL,
{
method: RequestMethod.GET,
header: {'Content-Type': 'application/x-www-form-urlencoded',
'Connection': 'keep-alive'},
// extraData: {"age":"16"},
extraData: {},
expectDataType: HttpDataType.ARRAY_BUFFER,
readTimeout: 30,
connectTimeout:40,
```

文件编号:CC-TECH-IP-A-002 

第10页 

云核客户端安全输入系统(鸿蒙版) 用户手册

```
usingProtocol: HttpProtocol.HTTP1_1,
sslVersion: SSLVersion.SSLVERSION_GMTLS,
sslPolicy: SSLPolicy.SSLPOLICY_DEFAULT,
}, (err: BusinessError<void>, data: HttpResponse) => {
if(!err){
this.text = `${data.result}`
} else {
this.text = JSON.stringify(err);
}
    })
})
```

文件编号:CC-TECH-IP-A-002 

第11页
