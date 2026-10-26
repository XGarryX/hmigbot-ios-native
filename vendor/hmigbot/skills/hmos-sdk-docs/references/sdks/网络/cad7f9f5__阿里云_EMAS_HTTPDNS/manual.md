# **HarmonyOS SDK接入** 

本章节介绍了 HarmonyOS SDK 的接入方法。 

## **前言** 

本 SDK 基于 HarmonyOS API 12 开发, compileSdkVersion 为 5.0.0(12) 。 

#### **说明** 

在 Beta5 以下版本的 HarmonyOS 中,开发者在通过定制 DNS 解析规则访问特定 IP 的服务器时,必须在 URL 中显式指定访 问端口,否则可能会导致定制 DNS 解析规则不生效,自动降级到 LocalDNS 

## **准备工作** 

1. 请了解产品使用流程,获取 Account ID 

2. 请参考 HarmonyOS 应用开发文档准备 HarmonyOS 应用开发环境 

## **第一步:安装SDK** 

在 HarmonyOS 应用根目录执行以下命令安装 SDK : 

ohpm install @aliyun/httpdns 

ohpm 工具及更多关于 OpenHarmony 安装第三方 SDK 的信息请参考 OpenHarmony 三方库中心仓说明。 

## **第二步:配置SDK** 

在 Alibity onCreate 生命周期回调中执行以下代码配置 SDK : 

```arkts
import { AbilityConstant, UIAbility, Want } from '@kit.AbilityKit'; import { window } from '@kit.ArkUI'; import { httpdns } from '@aliyun/httpdns'; 
```

const ACCOUNT_ID = ' 这里需要替换为阿里云 HTTPDNS 控制台的 Account ID' 

```arkts
export default class EntryAbility extends UIAbility { onCreate(want: Want, launchParam: AbilityConstant.LaunchParam): void { // ************* 初始化配置 begin ************* httpdns.configService(ACCOUNT_ID, { context: this.context, }); // ************* 初始化配置 end ************* } // 省略其它代码 } 
```

其中 ACCOUNT_ID 变量为产品使用流程中获取 Account ID 。 

## **第三步:使用SDK** 

### **addCustomDnsRule方式** 

在发起网络请求之前,调用 SDK 的 API 进行 HTTPDNS 解析,通过 connection.addCustomDnsRuleAPI 配置 HTTPDNS 的解 析结果,以 HTTP 请求为例,代码如下: 

```arkts
import { http } from '@kit.NetworkKit'; import connection from '@ohos.net.connection'; import { httpdns, IpType, } from '@aliyun/httpdns'; import Url from '@ohos.url'; 
```

const ACCOUNT_ID = ' 这里需要替换为阿里云 HTTPDNS 控制台的 Account ID' 

export async function requestWithHttpDns(url: string, options: http.HttpRequestOptions): Promise<http. HttpResponse> { 

```arkts
let urlObject = Url.URL.parseURL(url); const host = urlObject.hostname; // ************* HTTPDNS 解析获取域名 begin ************* const httpdnsService = await httpdns.getService(ACCOUNT_ID); const result = await httpdnsService.getHttpDnsResultAsync(host, IpType.Auto); // ************* HTTPDNS 解析获取域名 end ************* // ************* 通过系统 API 设置 DNS 规则 begin ************* try { await connection.removeCustomDnsRule(host); } catch (ignored) { } if (result.ipv4s?.length ?? 0 > 0) { await connection.addCustomDnsRule(host, result.ipv4s); } else if (result.ipv6s?.length ?? 0 > 0) { await connection.addCustomDnsRule(host, result.ipv6s); } else { console.log(`httpdns 解析没有结果,不设置 dns`); } // ************* 通过系统 API 设置 DNS 规则 begin ************* // ************* 通过系统 API 进行网络请求 begin ************* const httpRequest = http.createHttp(); return httpRequest.request(url, options); // ************* 通过系统 API 进行网络请求 end ************* } 
```

其中 ACCOUNT_ID 变量为产品使用流程中获取 Account ID 。 

#### **重要** 

### **HarmonyOS 如何定制DNS解析规则** 

HarmonyOS 提供了定制 DNS 解析规则的 API : addCustomDnsRule 、 removeCustomDnsRule 、 clearCustomDnsRules 。 

通过 addCustomDnsRule API 应用可以添加自定义 host 和对应的 IP 地址的映射, 

通过 removeCustomDnsRule API 应用可以删除对应 host 的自定义 DNS 规则, 

通过 clearCustomDnsRules API 应用可以删除所有的自定义 DNS 规则。 

因此,当应用想要定制网络请求的 DNS 规则时,可以在网络请求之前,通过上述 API 设置对应的规则,然后再发起网络请 求。 

### **Remote Communication Kit的dnsRules方式** 

当使用 Remote Communication Kit 包进行网络请求时,可以通过配置 dnsRules 字段,修改 DNS 规则,以 fetch 请求为例, 代码如下: 

```arkts
import { httpdns, IpType } from '@aliyun/httpdns'; import { rcp } from '@kit.RemoteCommunicationKit'; import Url from '@ohos.url'; 
const ACCOUNT_ID = ' 这里需要替换为阿里云 HTTPDNS 控制台的 Account ID'; 
export async function rcpWithHttpDns(url: string): Promise<rcp.Response> { let urlObject = Url.URL.parseURL(url); const host = urlObject.hostname; // ************* HTTPDNS 解析域名获取 IP 结果 begin ************* const httpdnsService = await httpdns.getService(ACCOUNT_ID); const httpdnsResult = await httpdnsService.getHttpDnsResultAsync(host, IpType.Auto); let addresses: string[] = []; if (httpdnsResult.ipv4s) { addresses.push(...httpdnsResult.ipv4s) } if (httpdnsResult.ipv6s) { addresses.push(...httpdnsResult.ipv6s) } // ************* HTTPDNS 解析域名获取 IP 结果 end ************* const request = new rcp.Request(url, "GET"); request.configuration = { dns: { // ************* 通过 dnsRules 设置 IP begin ************* dnsRules: [{ host, port: 80, ipAddresses: addresses }, { host, port: 443, ipAddresses: addresses }] // ************* 通过 dnsRules 设置 IP end ************* } } // ************* 通过系统 API 进行网络请求 begin ************* const session = rcp.createSession(); return session.fetch(request); // ************* 通过系统 API 进行网络请求 end ************* } 
```

其中 ACCOUNT_ID 变量为产品使用流程中获取 Account ID 。 

## **后续步骤** 

如果要对 SDK 进行更精细的配置或者使用鉴权请求等其它功能,可以参考 HarmonyOS SDK API 。
