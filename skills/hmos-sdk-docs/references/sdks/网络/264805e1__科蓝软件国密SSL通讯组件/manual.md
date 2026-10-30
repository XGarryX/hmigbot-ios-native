CSIITM 标准文档 

文档编号:CSII-PS-PEC-2016003 

# PowerSsl 通道加密 ( **Harmony** 版) 用户手册 

##### 北京科蓝软件系统股份有限公司 

2024 年 2 月 2 日 

##### 文档修改记录 

|版本|内容|编写|审核|
|---|---|---|---|
|1.0|新建|彭佳星|赵阳|
|1.0|新增x86架构|彭佳星|赵阳|
|1.0|修改返回类型|彭佳星|赵阳|
|1.0|修复请求崩溃问题|彭佳星|赵阳|
|1.0|修改body返回类型,以用于通过流传输|彭佳星|赵阳|

###### 版权申明: 

本文档的版权属于北京科蓝软件系统股份有限公司,任何人或组织未经许可, 

不得擅自修改、拷贝或以其它方式使用本文档中的内容。 

#### 目   录 

|一、 引言........................................................................................................................1|
|---|
|1.1编写目的...........................................................................................................1|
|1.2背景知识及参考资料.......................................................................................1|
|二、 控件概述................................................................................................................2|
|2.1控件组成...........................................................................................................2|
|2.2功能特点...........................................................................................................2|
|2.3技术特点...........................................................................................................3|
|2.4控件接口描述...................................................................................................3|
|三、DevEcoStudio相关设置说明................................................................................4|
|3.1 Har文件导入.....................................................................................................4|
|3.2代码示例............................................................................................................5|

用户手册 

PowerSsl 通道加密 

## 一、引言 

#### **1.1** 编写目的 

“Powerssl 通道加密”是保护用户敏感信息输入的重要手段,能对客户端操作系统 进行安全增强,可大幅提升“木马”程序非法获取用户敏感输入信息“成本”的软件集合。 

“Powerssl 通道加密”的 Harmony 版本由加密模块组成。本《用户手册》中将以一个 典型的开发部署为例,为读者叙述一个典型开发的全过程,使读者能独立应用 Powerssl 通道加密。 

#### **1.2** 背景知识及参考资料 

假定读者对下列技术有一定的理解: 

|技术|有关内容|
|---|---|
|Harmony SDK|Harmony SDK的基本常识|
|Harmony|Harmony的Ability基本知识|
|Ability||
|通信|Ability的通信方法(非必须)|
|NAPI|NAPI相关知识(非必须)|

文件编号:CSII-PS-PEC-2016003 

第 1 页 

用户手册 

PowerSsl 通道加密 

## 二、控件概述 

#### **2.1** 控件组成 

Powerssl 通道加密 Harmony 版本两部分构成: 

加密核心实现模块——由 C++实现的 so 动态库。 

加密模块——提供 Powerssl 通道加密的 HAR 包,供 Harmony SDK 调用通过 

NAPI 方式调用加密核心实现模块动态库。 

#### **2.2** 功能特点 

- 防止 Hook 类木马程序攻击。 

- 防止网络传输泄密 

- 防破解保护 

#### **2.3** 技术特点 

- 敏感信息通过加密后有效防止敏感信息泄露。 

#### **2.4** 控件接口描述 

函数说明: 

|函数|说明|备注|
|---|---|---|
|handleAbilityAction(context:Context)|用于解 析xml|参数: Context:传入上下文,在EntryAbility.ets的onCreate方法 中调用 例子: onCreate(want:Want,launchParam:AbilityConstant.LaunchP aram): void { PowerSsl.getInstance().handleAbilityAction(this.context) |
|postHttpSsl(postUrl:string,postBody: Uint8Array,requestHeaders:string[],c ertPath: string|undefined) : HttpResponse|POST 请求接 口|} 参数: postUrl:服务端地址 格式例子:https://test1.gmssl.cn/|

文件编号:CSII-PS-PEC-2016003 

第 2 页 

用户手册 

PowerSsl 通道加密 

|||postBody:请求报文 requestHeaders:请求头String数组类型键值对的形式 格式例子: headers: string[] = ['Content-Type:application/json', 'Accept: */*','Connection:keep-alive','Accept-Language:zh- CN,zh;q=0.9'] certPath:服务端CA证书目录精确到证书名,如存在多个 证书需要合并为一个。如为null则不验证服务端证书 格式例子:context.filesDir + "/ca-gm-cert.pem"|
|---|---|---|
|getHttpSsl(getUrl :string,requestHead ers:string[],certPath:string|
undefined):HttpResponse|GET
请求接
口|参数:
getUrl:服务端地址
格式例子:https://test1.gmssl.cn/
requestHeaders:请求头String数组类型键值对的形式
格式例子:
headers: string[] = ['Content-Type:application/json', 'Accept:
*/*','Connection:keep-alive','Accept-Language:zh-
CN,zh;q=0.9']
certPath:服务端CA证书目录精确到证书名,如存在多个
证书需要合并为一个。如为null则不验证服务端证书
传证书格式例子:context.filesDir + "/ca-gm-cert.pem"|
|downloadFile(downloadUrl:string,file Name: string, certPath: string|
undefined):number|下载请
求接口|参数:
downloadUrl:服务端地址
格式例子:https://test1.gmssl.cn/
fileName:文件路径(包含文件名称)
格式例子:context.filesDir +"/fullPlogo.png"
certPath:服务端CA证书目录精确到证书名,如存在多个
证书需要合并为一个。如为null则不验证服务端证书
传证书格式例子:context.filesDir + "/ca-gm-cert.pem"|
|uploadFile(uploadUrl:string,headers:s tring[],params:string[],fileNames:stri ng [ ],certPath:string||上传请 求接口|参数: uploadUrl:服务端地址|

文件编号:CSII-PS-PEC-2016003 

第 3 页 

用户手册 

PowerSsl 通道加密 

|undefined):number|格式例子:https://test1.gmssl.cn/ requestHeaders:请求头String数组类型键值对的形式 格式例子: headers: string[] = ['Content-Type:application/json', 'Accept: */*','Connection:keep-alive','Accept-Language:zh- CN,zh;q=0.9'] params:请求参数 相当于文件类型 格式例子:['filetype:pem'] fileNames:上传文件的数组(文件名中带全路径) 格式例子:[context.filesDir + "/ca-gm-cert.pem"] certPath:服务端CA证书目录精确到证书名,如存在多个 证书需要合并为一个。如为null则不验证服务端证书 传证书格式例子:context.filesDir + "/ca-gm-cert.pem"|
|---|---|
|返回格式|格式:|
|export class HttpResponse { statusCode: number ;|statusCode:响应码 body:响应报文|
|body: Uint8Array|bodyLen:响应报文长度|
|bodyLen: number; respHeaders:string; respHeadersLen: number; }|respHeaders :响应头 respHeadersLen:响应头长度|
|xml解析后 验证错误码会在调用其 他方法的响应码中返回:|错误码: -901:component为空 -902:bankName为空 -903:xml文件中的packageName为空 -904:expiration为空 -905:signValue为空|

文件编号:CSII-PS-PEC-2016003 

第 4 页 

用户手册 

PowerSsl 通道加密 

|-906:bundleName获取为空|
|---|
|-907:packageName与bundleName不一致|
|-908:没有发现许可文件|
|-909:无效的许可文件|
|-910:许可文件过期|

文件编号:CSII-PS-PEC-2016003 

第 5 页 

用户手册 

PowerSsl 通道加密 

## 三、 **DevEcoStudio** 相关设置说明 

#### **3.1** 、 **HAR** 文件导入 

entry 目录下创建 libs-har 目录,将 SDK 放入这个目录,然后在 entry 目 录下有个 oh-package.json5 文件,打开这个文件,找到 dependencies 属性 

添加” powerssllibrary.har“:” file:../entry/libs-har/ powerssllibrary.har“ 

文件编号:CSII-PS-PEC-2016003 

第 6 页 

用户手册 

PowerSsl 通道加密 

#### **3.2** 、将 **License** 文件导入 

#### 注意 **:** 文件名不可修改 

文件编号:CSII-PS-PEC-2016003 

第 7 页 

用户手册 

PowerSsl 通道加密 

#### **3.3** 、代码示例 

### EntryAbility.ets 中代码: 

文件编号:CSII-PS-PEC-2016003 

第 8 页 

用户手册 

PowerSsl 通道加密 

**import { AbilityConstant, UIAbility, Want } from '@kit.AbilityKit';** 

**import { hilog } from '@kit.PerformanceAnalysisKit';** 

**import { window } from '@kit.ArkUI';** 

**import { PowerSsl } from 'powerssllibrary';** 

**export default class EntryAbility extends UIAbility {** 

**onCreate(want: Want, launchParam: AbilityConstant.LaunchParam): void {** 

**hilog.info(0x0000, 'testTag', '%{public}s', 'Ability onCreate');** 

**PowerSsl.getInstance().handleAbilityAction(this.context)** 

#### **}** 

**onDestroy(): void {** 

**hilog.info(0x0000, 'testTag', '%{public}s', 'Ability onDestroy');** 

#### **}** 

文件编号:CSII-PS-PEC-2016003 

第 9 页 

用户手册 

PowerSsl 通道加密 

**onWindowStageCreate(windowStage: window.WindowStage): void {** 

**// Main window is created, set main page for this ability** 

**hilog.info(0x0000, 'testTag', '%{public}s', 'Ability onWindowStageCreate');** 

**windowStage.loadContent('pages/Index', (err, data) => { if (err.code) {** 

**hilog.error(0x0000, 'testTag', 'Failed to load the content. Cause: %{public}s', JSON.stringify(err) ?? ''); return;** 

**}** 

**hilog.info(0x0000, 'testTag', 'Succeeded in loading the content. Data: %{public}s', JSON.stringify(data) ?? '');** 

**});** 

**}** 

#### **onWindowStageDestroy(): void {** 

**// Main window is destroyed, release UI related** 

#### **resources** 

文件编号:CSII-PS-PEC-2016003 

第 10 页 

用户手册 

PowerSsl 通道加密 

#### **hilog.info(0x0000, 'testTag', '%{public}s', 'Ability onWindowStageDestroy');** 

**}** 

#### **onForeground(): void {** 

**// Ability has brought to foreground** 

**hilog.info(0x0000, 'testTag', '%{public}s', 'Ability onForeground');** 

#### **}** 

#### **onBackground(): void {** 

**// Ability has back to background** 

**hilog.info(0x0000, 'testTag', '%{public}s', 'Ability onBackground');** 

**}** 

**}** 

## Index.ets 中代码 

```arkts
import { common } from '@kit.AbilityKit'; 
import { fileIo } from '@kit.CoreFileKit'; 
import { BusinessError } from '@kit.BasicServicesKit'; 
```

文件编号:CSII-PS-PEC-2016003 

第 11 页 

用户手册 

PowerSsl 通道加密 

```arkts
import { ErrorEvent, MessageEvents, util, worker } from '@kit.ArkTS'; import Log from './Log'; 
```

let url: string = "https://test1.gmssl.cn/"; 

let headers: string[] = ['Accept:text/xml,application/json', 'Content-Type:application/json;charset=utf-8','Accept-Language:zhCN,zh;q=0.8','Connection:Keep-Alive','Expect:'] 

```arkts
let puzBuff: string = "[{\"_requestBody\" :\" {_ChannelCode\":\"EMBS\"}\"}]"; let params:string[] =['filetype:crt']; 
```

let context: common.UIAbilityContext = getContext(this) as common.UIAbilityContext; 

let filenames: string[] = [context.filesDir + "/dd.crt"]; // 正确拼接路径 

@Entry 

@Component 

struct Index { 

@State message: string = 'Hello World' 

/** 

- 将 RawFile 下的文件读出来然后再写入沙箱 

- @param context 

- @param fileName 

- @returns 

*/ 

static async getWriteFile(context: common.UIAbilityContext, fileName: string): Promise<string> { 

try { 

const value = await context.resourceManager.getRawFileContent(fileName) 

文件编号:CSII-PS-PEC-2016003 

第 12 页 

用户手册 

PowerSsl 通道加密 

let rawFile = value; 

let filesDir = context.filesDir; 

let file = fileIo.openSync(filesDir + "/" + fileName, fileIo.OpenMode.READ_WRITE | fileIo.OpenMode.CREATE) 

fileIo.writeSync(file.fd, rawFile.buffer) 

//关闭文件 

fileIo.closeSync(file) 

//文件全路径 let filePath = filesDir + "/" + fileName 

//查文件是否存在 

fileName = filesDir + "/icon.png"; 

fileIo.access(filePath).then((res: boolean) => { 

if (res) { 

console.info("file exists"); 

} else { console.info("file not exists"); 

} 

}).catch((err: BusinessError) => { 

console.error("access failed with error message: " + err.message + ", error code: " + err.code); 

}); return filePath } catch (error) { return ""; 

} 

} 

aboutToAppear() { 

文件编号:CSII-PS-PEC-2016003 

第 13 页 

用户手册 

PowerSsl 通道加密 

Index.getWriteFile(getContext(this) as common.UIAbilityContext, "dd.crt"); } // 添加一个安全销毁 Worker 的方法 

private safeTerminateWorker(w: worker.ThreadWorker): void { 

try { w.terminate(); } catch (error) { // 忽略错误 } } build() { Row() { Column() { Text(this.message) .fontSize(10) .fontWeight(FontWeight.Bold) Blank() Row() { Button("POST").onClick(() => { 

let w: worker.ThreadWorker = new worker.ThreadWorker('entry/ets/workers/MyWorker.ets'); 

//接收子线程的消息 w.onmessage = (e: MessageEvents): void => { // data:worker 线程发送的信息 let statusCode: number = e.data['statusCode']; let uint8Body: Uint8Array = e.data['body'] let bodyLen: number = e.data['bodyLen'] let respHeaders: string = e.data['respHeaders'] let respHeadersLen: number = e.data['respHeadersLen'] let decoder = util.TextDecoder.create('utf-8'); 

文件编号:CSII-PS-PEC-2016003 

第 14 页 

用户手册 

PowerSsl 通道加密 

let body = decoder.decodeToString(uint8Body); 

Log.showError("SSLDemo", "国密 POST 接口返回响应码:" + statusCode); 

Log.showError("SSLDemo", "国密 POST 接口返回报文长度:" + bodyLen); 

Log.showError("SSLDemo", "国密 POST 接口返回报文:" + body); 

Log.showError("SSLDemo", "国密 POST 接口返回响应头:" + respHeaders); 

Log.showError("SSLDemo", " 国密 POST 接口返回响应头长度: " + respHeadersLen) 

// 处理完成后立即销毁 Worker 

this.safeTerminateWorker(w); 

} 

//接收子线程的错误消息 

w.onerror = (e: ErrorEvent): void => { 

// 处理完成后立即销毁 Worker 

this.safeTerminateWorker(w); 

} 

//发送 post 请求 

try { 

w.postMessage({ 

'SSL': 0, 

'url': url, 

'body': puzBuff, 

'headers': headers, 'context': context, 

}) 

} catch (error) { 

// 处理完成后立即销毁 Worker 

this.safeTerminateWorker(w); 

// TODO: Implement error handling. 

} 

文件编号:CSII-PS-PEC-2016003 

第 15 页 

用户手册 

PowerSsl 通道加密 

}) 

Button("GET").onClick(() => { 

let w: worker.ThreadWorker = new 

worker.ThreadWorker('entry/ets/workers/MyWorker.ets'); 

//接收子线程的消息 

w.onmessage = (e: MessageEvents): void => { 

// data:worker 线程发送的信息 

let statusCode: number = e.data['statusCode']; 

let uint8Body: Uint8Array = e.data['body'] 

let decoder = util.TextDecoder.create('utf-8'); 

let body = decoder.decodeToString(uint8Body); 

let bodyLen: number = e.data['bodyLen'] 

let respHeaders: string = e.data['respHeaders'] 

let respHeadersLen: number = e.data['respHeadersLen'] 

Log.showError("SSLDemo", "国密 GET 接口返回响应码:" + statusCode); 

Log.showError("SSLDemo", "国密 GET 接口返回报文:" + body); 

Log.showError("SSLDemo", "国密 GET 接口返回报文长度:" + bodyLen); 

Log.showError("SSLDemo", "国密 GET 接口返回响应头:" + respHeaders); 

Log.showError("SSLDemo", " 国密 GET 接口返回响应头长度: " + respHeadersLen); 

// 处理完成后立即销毁 Worker 

this.safeTerminateWorker(w); 

} 

//接收子线程的错误消息 

w.onerror = (e: ErrorEvent): void => { 

Log.showError("SSLDemo", "接收错误信息:" + e); 

文件编号:CSII-PS-PEC-2016003 

第 16 页 

用户手册 

PowerSsl 通道加密 

// 处理完成后立即销毁 Worker 

this.safeTerminateWorker(w); 

} 

//发送 post 请求 

try { 

w.postMessage({ 

'SSL': 1, 'url': url, 'headers': headers, 

'context':context 

}) 

} catch (error) { 

// 处理完成后立即销毁 Worker 

this.safeTerminateWorker(w); 

// TODO: Implement error handling. 

} 

}) 

} 

} .width('100%') 

} .height('100%') 

} 

} 

### Worker 中代码示例: 

import { buffer, ErrorEvent, MessageEvents, ThreadWorkerGlobalScope, worker } from 

文件编号:CSII-PS-PEC-2016003 

第 17 页 

用户手册 

PowerSsl 通道加密 

'@kit.ArkTS'; 

import { HttpResponse, PowerSsl, PowerSslJni } from 'powerssllibrary'; import Log from '../pages/Log'; 

```arkts
import { common, Context } from '@kit.AbilityKit'; 
```

const workerPort: ThreadWorkerGlobalScope = worker.workerPort; 

/** 

* Defines the event handler to be called when the worker thread receives a message sent by the host thread. 

* The event handler is executed in the worker thread. 

* 

* @param e message data 

*/ 

workerPort.onmessage = (e: MessageEvents) => { 

switch (e.data['SSL']as number) { 

case 0: 

postStrData(e.data['context'],e.data['url'], e.data['body'], e.data['headers']); 

break; 

case 1: 

getStrData(e.data['context'],e.data['url'], e.data['headers']) 

break; 

// case 2: 

// 

fileStrData(e.data['context'],e.data['url'],e.data['headers'],e.data['params'],e.data['fileName']) 

//   break; 

// case 3: 

// 

downloadFileStrData(e.data['context'],e.data['url'],e.data['fileName'],e.data['certPath']) 

//   break; 

文件编号:CSII-PS-PEC-2016003 

第 18 页 

用户手册 

PowerSsl 通道加密 

} 

} 

async function postData(context: Context, url: string, body?: string, headers: string[] = []): Promise<object> { 

try { 

```arkts
const defaultBody = '[{"_requestBody":"{\"_ChannelCode\":\"EMBS\"}"}]'; 
```

const requestBody = body || defaultBody; 

const buf = stringToUint8Array(requestBody); 

const postResult: HttpResponse = await PowerSsl.getInstance().postHttpSsl(context, url, buf, headers, undefined); 

return postResult as object; 

- } catch (error) { 

```arkts
const errorMsg = `POST 请求异常:${(error as Error).message}`; 
```

Log.showError("SSL", errorMsg); 

throw new Error(errorMsg); 

} 

} 

async function getData(context: Context, url: string, headers: string[]): Promise<object> { 

try { 

Log.showError("SSL", "licence:" + 222222); 

const response: HttpResponse = await PowerSsl.getInstance().getHttpSsl(context, url, headers, undefined); 

return response; 

}catch (error) { 

Log.showError("SSL", "licence:" + 33333); 

```arkts
const errorMsg = `get 请求异常:${(error as Error).message}`; 
```

Log.showError("SSL", errorMsg); 

throw new Error(errorMsg); 

} 

文件编号:CSII-PS-PEC-2016003 

第 19 页 

用户手册 

PowerSsl 通道加密 

} 

// async function fileUpData(context:Context,url: string, headers: string [],params:string[],fileName:string[]) { 

//    try { 

//      const response: HttpResponse = await PowerSsl.getInstance().uploadFile(context,url, headers, params,fileName, undefined); 

//      return response; 

- //    }catch (error) { 

- //      const errorMsg = `文件上传失败:${(error as Error).message}`; 

//      Log.showError("SSL", errorMsg); 

//      throw new Error(errorMsg); 

//    } 

// } 

// 

// async function downloadFileData(context:Context,url: 

string,fileName:string,certPath:string|undefined) { 

//    try{ 

//      const response: number = await PowerSsl.getInstance().downloadFile(context, url, fileName, certPath); 

//      return response; 

//      }catch (error) { 

//      const errorMsg = `文件下载失败:${(error as Error).message}`; 

//      Log.showError("SSL", errorMsg); 

//      throw new Error(errorMsg); 

//    } 

// 

// } 

function stringToUint8Array(str: string) { 

return new Uint8Array(buffer.from(str, 'utf-8').buffer); 

} 

文件编号:CSII-PS-PEC-2016003 

第 20 页 

用户手册 

PowerSsl 通道加密 

async function postStrData(context:Context,url: string, body: string, headers: string []) { 

try { 

const dataString = await postData(context,url, body, headers); // 等待 fetchData 完成并 返回结果 

// if (dataString['statusCode'] == 0) { 

workerPort.postMessage(dataString) 

// } else { 

// workerPort.postMessage("ssl:Echo from worker Random: " + dataString['statusCode']) 

// } 

} catch (error) { 

console.error("数据获取失败:", error); 

} 

} 

// 

// async function downloadFileStrData(context : Context,downloadUrl: string, fileName: string, certPath: string | undefined) { 

//   try { 

//     const dataString = await downloadFileData(context,downloadUrl, fileName, certPath); // 等待 fetchData 完成并返回结果 

//       workerPort.postMessage(dataString) 

//   } catch (error) { 

//     Log.showError("SSL", "数据获取失败:" + error); 

//   } 

// } 

// 

// async function fileStrData(context : Context,url: string, headers: string 

文件编号:CSII-PS-PEC-2016003 

第 21 页 

用户手册 

PowerSsl 通道加密 

[],params:string[],fileName:string[]) { 

//   try { 

//     const dataString = await fileUpData(context,url, headers, params,fileName); // 等待 fetchData 完成并返回结果 

// 

//     if (dataString['statusCode'] == 0) { 

//       workerPort.postMessage(dataString) 

//     } else { 

//       workerPort.postMessage(dataString) 

//     } 

// 

//   } catch (error) { 

//     Log.showError("SSL", "数据获取失败:" + error); 

//   } 

// } 

// 使用 async/await 调用上面的函数 

async function getStrData(context: Context, url: string, headers: string[]) { 

try { 

const getStr = await getData(context, url, headers); 

if (getStr['statusCode'] === 0) { 

workerPort.postMessage(getStr); 

} else { 

workerPort.postMessage(`ssl:Error ${getStr['statusCode']}`); 

} } catch (error) { 

Log.showError("请求失败", error); workerPort.postMessage("ssl:Request Failed"); 

} } 

文件编号:CSII-PS-PEC-2016003 

第 22 页 

用户手册 

PowerSsl 通道加密 

/** 

* Defines the event handler to be called when the worker receives a message that cannot be deserialized. 

* The event handler is executed in the worker thread. 

* 

* @param e message data 

*/ 

workerPort.onmessageerror = (e: MessageEvents) => { 

} 

/** 

* Defines the event handler to be called when an exception occurs during worker execution. 

* The event handler is executed in the worker thread. 

* 

* @param e error message 

*/ 

workerPort.onerror = (e: ErrorEvent) => { 

} 

文件编号:CSII-PS-PEC-2016003 

第 23 页 

用户手册 

PowerSsl 通道加密 

#### **3.3** 、注意事项 

**1** :使用 **SSL** 通道不要在主线程请求,因为华为机制,在主线程请求如 果 **6** 秒接收不到服务端响应会导致应用崩溃,需开启多线程 **taskpool** 或者 **worker** 进行请求, **worker** 用法可参考 **demo** 示例 工程。 

#### **2** :如使用 **worker** 需要在模块级的 **build-profile.json5** 文件中定 义引用 **Worker** 

#### **3** : **xml** 要放在 **entry** 模块下的 **main/resources/rawfile** 文件夹 

#### 下,不要修改 **xml** 名称,否则会找不到 

#### **4** :使用 **SSL** 通道需要申请网络请求权限 

在主工程的 **module.json5** 中添加 

#### **"requestPermissions": [** 

文件编号:CSII-PS-PEC-2016003 

第 24 页 

用户手册 

PowerSsl 通道加密 

#### **{** 

#### **"name": "ohos.permission.INTERNET"** 

#### **}** 

**]** 

文件编号:CSII-PS-PEC-2016003 

第 25 页
