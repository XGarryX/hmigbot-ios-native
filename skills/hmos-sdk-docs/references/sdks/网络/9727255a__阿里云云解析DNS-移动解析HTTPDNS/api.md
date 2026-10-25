# 阿里云云解析DNS-移动解析HTTPDNS 接口文档 

接口文档分为两个部分介绍,SDK 接入和 SDK 服务 API 介绍 

# 一、 **SDK** 接入 

阿里云云解析 DNS-移动解析 HTTPDNS SDK 接入,分为如下几个步骤:SDK 集成、SDK 初始化、调用解析接口使用 SDK。 

### 第一步: **SDK** 集成 

支持使用 DevEco Studio 自动导入和手动导入两种方式,将SDK 导入到您的应用工程中。 

### 环境要求 

HarmonyOS SDK API 12 及以上 

- 1,自动导入,使用ohpm 从OpenHarmony 三方库中心仓安装。 

##### 2.0.1 版本开始支持 OpenHarmony 三方库中心仓 获取SDK 

在工程的根目录执行:ohpm install @alidns/httpdns 

ohpm 工具以及更多关于OpenHarmony 安装第三方SDK 的信息请参考 OpenHarmony 三方库中心仓说明 

- 2,手动导入,引用本地HAR 包方式集成SDK。 

参考 SDK 下载,获取鸿蒙SDK,并集成SDK 在自己的App 工程项目中,您可以 参考 Demo 示例工程源码了解如何使用本SDK。 

在工程的oh-package.json5 中设置三方包依赖。以HAR 包在工程根目录下为 例,配置示例如下(实际配置时请以HAR 包实际目录为准): 

"dependencies": { "@alidns/httpdns": "file:alipdnslibrary.har" } 

依赖设置完成后,需要执行ohpm install 命令安装依赖包,依赖包会存储在工 程的oh_modules 目录下。 

ohpm install 

### 第二步: **SDK** 初始化 

import { Alipdns,schemaType,DNSDomainInfo, DNSLogger } from '@alidns/httpdns' 

#### 设置鉴权模式 

开启鉴权模式,以保障用户身份安全,不被第三方未授权者盗用,用户在 Alibity onCreate 生命周期回调中执行以下代码配置SDK。 

参考创建密钥在控制台创建 AccessKey ID 和 AccessKey Secret 。 

import { Alipdns,schemaType,DNSDomainInfo, DNSLogger } from '@alidns/httpdns' 

const AccountID = '这里需要替换为设置您在控制台接入SDK 的Account ID'; 

const AccessKeID = '这里需要替换为您在控制台“接入配置”创建的密钥的 AccessKey ID'; 

const AccessKeySecret = '这里需要替换为您在控制台“接入配置”创建的密 钥的 AccessKey Secret'; 

export default class EntryAbility extends UIAbility { 

onCreate(want: Want, launchParam: AbilityConstant.LaunchParam): void { 

// ************* 阿里pdns-sdk 配置 begin ************* DNSLogger.getInstance().setEnableLogger = true; let alipdns = Alipdns.getInstance(); 

alipdns.Init(this.context,AccountID,AccessKeID,AccessKeySecret); alipdns.setKeepAliveDomains(['*****','*****']); alipdns.setSchemaType(schemaType.https); 

alipdns.preLoadDomains(alipdns.QTYPE_V4,['*****','*****','*****']); // ************* 阿里pdns-sdk 配置 end ************* } 

- // 省略其它代码 } 

### 第三步: 调用解析接口使用 **SDK** 

#### addCustomDnsRule 方式 

在发起网络请求之前,调用SDK 的域名解析API 进行DNS 解析,通过 connection.addCustomDnsRuleAPI 配置DNS 的解析结果,为当前应用程序添加 自定义host 和对应的IP 地址的映射。以 HTTP 请求为例,代码如下: 

```arkts
import { http } from '@kit.NetworkKit'; import connection from '@ohos.net.connection'; import { Alipdns,schemaType,DNSDomainInfo } from '@alidns/httpdns' import Url from '@ohos.url'; 
export async function requestWithHttpDns(url: string, options: http.HttpRequestOptions): Promise<http.HttpResponse> { let urlObject = Url.URL.parseURL(url); const host = urlObject.hostname; 
```

// ************* 移动解析HTTPDNS 解析获取域名 begin ************* const result = Alipdns.getInstance().getIpsByHostFromCache(Alipdns.getInstance().QTY PE_V4,host,true); 

// ************* 移动解析HTTPDNS 解析获取域名 end ************* // ************* 通过系统API 设置DNS 规则 begin ************* try { await connection.removeCustomDnsRule(host); } catch (ignored) { } if (result.length ?? 0 > 0) { await connection.addCustomDnsRule(host, result); } else { console.log(`httpdns 解析没有结果,不设置dns`); } // ************* 通过系统API 设置DNS 规则 begin ************* // ************* 通过系统API 进行网络请求 begin ************* 

```arkts
const httpRequest = http.createHttp(); return httpRequest.request(url, options); // ************* 通过系统API 进行网络请求 end ************* } 
```

#### Remote Communication Kit 的dnsRules 方式 

当使用 Remote Communication Kit 包进行网络请求时,可以先调用SDK 的域名 解析API 进行DNS 解析,然后通过配置dnsRules 字段,修改DNS 规则,以 fetch 请求为例,代码如下: 

```arkts
import { Alipdns,schemaType,DNSDomainInfo } from '@alidns/httpdns' import { rcp } from '@kit.RemoteCommunicationKit'; import Url from '@ohos.url'; 
export async function rcpWithHttpDns(url: string): Promise<rcp.Response> { let urlObject = Url.URL.parseURL(url); const host = urlObject.hostname; // ************* 移动解析HTTPDNS 解析域名获取IP 结果 begin 
```

************* const result = Alipdns.getInstance().getIpsByHostFromCache(Alipdns.getInstance().QTY PE_V4,host,true); 

// ************* 移动解析HTTPDNS 解析域名获取IP 结果 end ************* const request = new rcp.Request(url, "GET"); if (result.length ?? 0 > 0) { request.configuration = { dns: { // ************* 通过dnsRules 设置IP begin ************* dnsRules: [{ host, port: 443, ipAddresses: result },{ host, port: 80, ipAddresses: result }] // ************* 通过dnsRules 设置IP end ************* } } } // ************* 通过系统API 进行网络请求 begin ************* const session = rcp.createSession(); return session.fetch(request); 

// ************* 通过系统API 进行网络请求 end ************* } 

# 二、 **SDK** 服务 **API** 介绍 

## API 介绍 

#### 1. Account ID 和鉴权 

必传参数,您在控制台注册自己的应用后,控制台会为此应用生成唯一标识 Account ID ,鉴权功能来保障用户身份安全,防止被第三方未授权者盗用。用 户请参考创建密钥在控制台创建 AccessKey ,并在APP 中通过如下代码设置: 

Alipdns.getInstance().Init(this.context,AccountID,AccessKeID,AccessKe ySecret); 

#### 2. 解析协议设置 

SDK 支持设置DNS 解析请求协议类型,可自主选择通过HTTP 或HTTPS 协议解 析,具体可通过scheme 属性进行设置。 

SDK 默认并推荐使用HTTPS 协议进行解析,因为HTTPS 协议安全性更好。移动 解析HTTPDNS 的计费项是按HTTP 的解析次数进行收费,其中HTTPS 是按5 倍 HTTP 流量进行计费,开发者可以根据自身实际业务需要选择scheme 类型。如 下设置: 

Alipdns.getInstance().setSchemaType(schemaType.https); 

#### 3. 设置域名缓存保持 

SDK 在缓存功能已开启的情况下,可设置针对某些域名开启缓存保持功能,如 果该功能开启,SDK 会自动更新这些域名的过期缓存,保障用户缓存数据及时 更新,但是可能会带来域名解析次数和客户端流量消耗的增多。如果不设置该 功能,那么SDK 不会自动进行过期缓存更新,只有当用户调用解析方法时,才 会再次进行缓存更新。若要设置某些域名的缓存保持需要通过以下代码设置: 

Alipdns.getInstance().setKeepAliveDomains(['*****','*****']); 

#### 4. 预解析 

由于SDK 可以设置开启缓存功能,在第一次解析完域名产生缓存后,后续再次 解析此域名时解析速度可提升至0 时延。因此,建议在app 启动后,对app 中 可能要解析的域名进行预解析。 

代码示例: 

Alipdns.getInstance().preLoadDomains(alipdns.QTYPE_V4,['*****','***** ','*****']); 

#### 5. 设置开启SDK 调试日志开关 

用户可以设置是否开启SDK 调试日志开关(true 为开启调试日志,false 为关 闭调试日志),该方法请在SDK 初始化前设置。 

DNSLogger.getInstance().setEnableLogger = true; 

#### 6. 设置是否开启使用 移动解析HTTPDNS 解析失败时自动降级到 

#### localdns 进行兜底解析 

SDK 默认开启使用移动解析HTTPDNS 解析失败时自动降级到localdns 兜底解析 Alipdns.getInstance().setEnableLocalDns(true);//默认开启使用移动解析 HTTPDNS 解析失败时自动降级到localdns 兜底解析 

#### 7. 设置域名解析的超时时间 

timeout 属性为域名解析的超时时间。默认超时时间为3s,用户可自定义超时 时间,建议设置在2~5s 之间。 

Alipdns.getInstance().setTimeout(3);//默认超时时间为3s 

#### 8. 解析方法 

SDK 提供不同的域名解析方法,示例如下: 

/// 异步解析方法 /// Alipdns.getInstance().QTYPE_V4           解析ip 地址类型:ipv4 /// host                                     要解析的域名 /// ips                                      回调(所有ip 地址) Alipdns.getInstance().getIpsByHostAsync(Alipdns.getInstance().QTYPE_V 4, host,(ips:string[]) => {}); /// 同步解析方法(取缓存中的数据) /// Alipdns.getInstance().QTYPE_V4           解析ip 地址类型:ipv4 /// host                                     要解析的域名 /// true                                     是否允许返回过期ip 结果 const result = Alipdns.getInstance().getIpsByHostFromCache(Alipdns.getInstance().QTY PE_V4,host,true);
