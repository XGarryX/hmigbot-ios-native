# **SDK** 虚拟营业厅 **AnyChat** 接口文档使用指南 

广 州 佰 锐 网 络 科 技 有 限 公 司 **Guangzhou BaiRui Network Technology Co.,Ltd.** http://www.bairuitech.com http://www.anychat.cn 

#### 目录 

|1. 文档及集成说明........................................................................................................................... 2|
|---|
|1.1. 集成方式说明.................................................................................................................... 2|
|2. 组件业务功能配置说明............................................................................................................... 2|
|2.1. SDK基础配置功能示例.................................................................................................... 3|
|2.2. SDK可选扩展配置功能示例............................................................................................4|
|3. 组件所需权限信息及合规要求................................................................................................... 6|
|3.1. 权限使用说明.................................................................................................................... 6|
|4. 视频组件接口说明....................................................................................................................... 7|
|4.1. 组件开始调用接口............................................................................................................ 7|
|4.2. AnyChat虚拟营业厅SDK组件层与业务层信息交互回调接口说明......................... 12|
|5. 错误码..........................................................................................................................................16|
|5.1. 自定义异常错误码.......................................................................................................... 16|
|5.2. 操作错误码...................................................................................................................... 16|
|5.3. 系统错误码...................................................................................................................... 17|
|5.4. 连接错误码...................................................................................................................... 17|
|5.5. 进入房间错误码.............................................................................................................. 18|
|5.6. 数据流错误码.................................................................................................................. 19|
|5.7. 视频呼叫错误码.............................................................................................................. 19|
|5.8. 排队错误码...................................................................................................................... 20|
|5.9. sdk错误码.........................................................................................................................20|
|5.10. 视频设备错误码............................................................................................................ 20|
|5.11. 音频设备错误码............................................................................................................ 21|
|5.12. 业务对象错误码............................................................................................................ 21|
|5.13. APP ID错误码................................................................................................................ 22|
|5.14. 业务服务器错误码........................................................................................................ 22|

第 1 页共 23 页 

## **1.** 文档及集成说明 

本文档为 AnyChat 虚拟营业厅 SDK 集成说明文档,为移动端集成开发提供指导。 组件详细调用方式及回调处理操作可参考示例工程 Demo。 

### 集成说明: **AnyChat** 虚拟营业厅 **SDK** 提供 **har** 包方式供集成使用 **;** 

开发工具: **DevEco Studio** 

### 组件集成资料: 

### **arm64-v8a** 

**anychat_sdk_harmony.har anychatvideobanksdk.har** 

|集成资料名称|说明及业务用途|集成必须|
|---|---|---|
|arm64-v8a、armeabi|组件所需so库文件|是|
|anychat_sdk_harmony.har|组件所需sdk文件|是|
|anychatvideobanksdk.har|远程视频银行组件依赖包|是|

## **1.1.** 集成方式说明 

(1)将 **anychatvideobanksdk.har** 、 **anychat_sdk_harmony.har** 、 **arm64-v8a** 库文件放在 宿主工程的 libs 目录下; 

(2)选择宿主工程的 【 **oh-package.json5** 】 文件,将远程视频银行组件依赖添加到宿主 工程中; 

**"dependencies": {** 

**"anychat_sdk_harmony": "file:./libs/anychat_sdk_harmony.har",** 

**"anychatvideobanksdk": "file:./libs/anychatvideobanksdk.har"** 

**}** 

## **2.** 组件业务功能配置说明 

接入说明:包括基本功能和扩展功能 基本业务功能:音视频通话 扩展业务功能:坐席画面展示模式、业务扩展透传、智能播报变量配置等 

第 2 页共 23 页 

功能区分 业务功能 功能介绍 配置方式
提供实时音视频通
基本功能 音视频通话 详见 SDK 基础配置功能示例
话能力
提供坐席服务人员
坐席画面展示模
画面展示模式设置 详见 SDK 可选扩展配置功能示例
式
功能
根据 业务办理需要
业务扩展透传 用于业务层透传相 详见 SDK 可选扩展配置功能示例
扩展功能
关扩展信息数据
根据 业务办理需要
智能播报变量配
透传相关业务产品 详见 SDK 可选扩展配置功能示例
置
信息
2.1. SDK 基础配置功能示例
基础配置信息说明
信息类型 信息采集目的 配置说明
let  transferModel: BRTransferModel =  new
BRTransferModel();
transferModel.loginIp = loginIp;  // 接入音视频能
力平台 IP  地址 ( 必传 )
transferModel.loginPort = loginPort;  // 接入音视
频能力平台端口 ( 必传 )
transferModel.loginAppId = loginAppId;  // 接入
登录信息 用于 SDK 进行连接登录 音视频能力平台应用 ID( 必传 )
//AnyChat  服务器登录扩展参数 ( 必传 )
let  loginStrObject: object =
BRStringUtils.getJsonObject();
loginStrObject['callTradeNo'] = callTradeNo;
loginStrObject['sysCode'] = sysCode;
transferModel.loginStrParam =
JSON.stringify(loginStrObject);
let  transferModel: BRTransferModel =  new
业务办理所需,如:根 BRTransferModel();
用户信息 据用户信息查询客户十 // 用户姓名 ( 必传 )
要素信息 transferModel.userName = loginName;
// 身份证号码 ( 必传 )

第 3 页共 23 页 

transferModel.idCardNumber =
loginIDCardNum;
// 证件类型字典名称 ( 必传 )
transferModel.idCardTypeName =
idCardTypeName;
// 证件类型字典值 ( 必传 )
transferModel.idCardTypeValue =
idCardTypeValue;
// 用户手机号 ( 必传 )
transferModel.phoneNumber = loginPhone;
let  transferModel: BRTransferModel =  new
业务办理所需,用于指
BRTransferModel();
定客户端业务办理的渠
// 渠道名称 ( 必传 )
业务渠道信息 道类型,如:移动端渠
transferModel.integratorName = integratorName;
道、H5 渠道、小程序渠
道 // 渠道编码 ( 必传 )
transferModel.integratorCode = integratorCode;
2.2. SDK 可选扩展配置功能示例
信息类型 信息采集目的 配置说明
let  transferModel: BRTransferModel =  new
BRTransferModel();
坐席画面展示 提供坐席服务人员画
// 坐席画面是否全屏展示
模式 面展示模式设置功能
transferModel.isShowRemoteFullScreen =
isSelectAgentShowLarge;
let  transferModel: BRTransferModel =  new
业务层 APP 版 用于坐席服务端展示 BRTransferModel();
本 APP 版本接入信息 // 手机版本信息 ( 非必传 )
transferModel.appVersion = "版本号"
let  transferModel: BRTransferModel =  new
用于坐席服务端展示 BRTransferModel();
设备型号
接入设备型号 // 设备型号 ( 非必传 )
transferModel.deviceModel = "设备型号";
用于坐席服务端展示 let  transferModel: BRTransferModel =  new
接入设备标识,用于 BRTransferModel();
设备标识
app 换设备绑定业务所 // 设备唯一标识 ( 非必传 )
需 transferModel.deviceId =

第 4 页共 23 页 

|||'3F2504E0-4F89-11D3-9A0C-0305E82C3301';|
|---|---|---|
|业务扩展透传 参数|根据业务办理需要用 于业务层透传相关扩 展信息数据,如客户位 置信息、业务办理备注 信息等|**let**transferModel:BRTransferModel=**new** BRTransferModel(); **let**expansionObject:object=**new**Object(); _//_外层自定义扩展参数_(_非必传_)_ **let**remarksArray:Array<object> =**new**Array; **let**remarksObject:object= BRStringUtils.getJsonObject(); remarksObject["groupName"]="备注信息"; **let**groupDataArray:Array<object> =**new**Array; **let**object1:object= BRStringUtils.getJsonObject(); object1["key"]="beizhu"; object1["name"]="备注信息"; object1["value"]="支持展示进线渠道或关联系 统相关信息"; groupDataArray.push(object1); remarksObject["groupData"]=groupDataArray; remarksArray.push(remarksObject); expansionObject["remarks"]=remarksArray;_//_备 注信息_(_非必传_)_ expansionObject["address"]="广东省广州市天 河区科韵路";_//_位置信息_(_非必传_)_ _//_设置扩展参数信息 transferModel.expansion= JSON.stringify(expansionObject);|
|智能播报变量 配置|根据业务办理需要透 传相关业务产品信息|**let**transferModel:BRTransferModel=**new** BRTransferModel(); _//_智能播报动态配置参数 transferModel.aiReportExtraParam= "{**\"**time**\"**:**\"**2026年1月1日**\"**}";|
|屏幕信息(屏幕 分辨率、屏幕方 向、屏幕常亮)、 重力传感器信 息|用于视频通话过程中, 视频画面的显示效果, 屏幕不自动休眠,提升 用户体验;|transferModel.isGetScreenSize=**true**;_//_获取屏幕 分辨率大小(默认获取) transferModel.isKeepScreenOn=**true**;_//_设置屏 幕常亮(默认设置) transferModel.isGetScreenDirection=**true**;_//_获取 屏幕方向(默认获取) transferModel.isSensorEnable=**true**;_//_获取重力 传感器信息(默认获取)|

'3F2504E0-4F89-11D3-9A0C-0305E82C3301';
let  transferModel: BRTransferModel =  new
BRTransferModel();
let  expansionObject: object =  new  Object();
// 外层自定义扩展参数 ( 非必传 )
let  remarksArray: Array<object> =  new  Array;
let  remarksObject: object =
BRStringUtils.getJsonObject();
remarksObject["groupName"] = "备注信息";
let  groupDataArray: Array<object> =  new  Array;
let  object1: object =
根据 业务办理需要 用 BRStringUtils.getJsonObject();
于业务层透传相关扩 object1["key"] = "beizhu";
业务扩展透传 展信息数据,如客户位 object1["name"] = "备注信息";
参数
置信息、业务办理备注 object1["value"] = "支持展示进线渠道或关联系
信息等 统相关信息";
groupDataArray.push(object1);
remarksObject["groupData"] = groupDataArray;
remarksArray.push(remarksObject);
expansionObject["remarks"] = remarksArray;  // 备
注信息 ( 非必传 )
expansionObject["address"] = "广东省广州市天
河区科韵路";  // 位置信息 ( 非必传 )
// 设置扩展参数信息
transferModel.expansion =
JSON.stringify(expansionObject);
let  transferModel: BRTransferModel =  new
BRTransferModel();
智能播报变量 根据 业务办理需要 透
// 智能播报动态配置参数
配置 传相关业务产品信息
transferModel.aiReportExtraParam =
"{ \" time \" : \" 2026 年 1 月 1 日 \" }";
transferModel.isGetScreenSize =  true ; // 获取屏幕
分辨率大小(默认获取)
屏幕信息(屏幕
用于视频通话过程中, transferModel.isKeepScreenOn =  true ; // 设置屏
分辨率、屏幕方
视频画面的显示效果, 幕常亮(默认设置)
向、屏幕常亮)、
屏幕不自动休眠,提升 transferModel.isGetScreenDirection =  true ; // 获取
重力传感器信
用户体验; 屏幕方向(默认获取)
息
transferModel.isSensorEnable =  true ; // 获取重力
传感器信息(默认获取)

第 5 页共 23 页 

## **3.** 组件所需权限信息及合规要求 

## **3.1.** 权限使用说明 

为实现音视频通信功能所必需的系统权限、使用目的及建议申请时机如下, 因相关权限的不申请将会对其对应的功能造成影响,您可以结合业务实际需要进 

## 行合理配置。 

在宿主工程的 **module.json5** 文件中统一配置权限,请在 **module.json5** 中添加如下权限 **:** 

ohos.permission.INTERNET 

ohos.permission.CAMERA 

ohos.permission.MICROPHONE 

|权限名称|权限说明|使用目的|是否可 选|申请时机|
|---|---|---|---|---|
|ohos.permission.I NTERNET|网络访问权限|用于访问网络连接; 互联网网络请求;|必选|初始化时调用|
|ohos.permission. CAMERA|相机权限|用于用户视频通话交互**;** 使用视频通话功能,需要开启 摄像头|必选|打开摄像头时 调用|
|ohos.permission. MICROPHONE|麦克风权限|用于用户视频通话交互; 使用视频通话功能,需要开启 麦克风;|必选|打开麦克风时 调用|

### 必选权限 

以下为必选权限,必须配置以下权限才能满足基本的音视频通话能力: 

"requestPermissions": [ 

{ //网络权限 "name": "ohos.permission.INTERNET" }, { 

//麦克风权限 

"name": "ohos.permission.MICROPHONE" }, { 

//摄像头权限 

"name": "ohos.permission.CAMERA" } 

] 

第 6 页共 23 页 

## **4.** 视频组件接口说明 

## **4.1.** 组件开始调用接口 

## **start(context: Context, model: BRTransferModel, event: BRVideoRecordEvent);** 

接口说明 **:** 

(1)AnyChat 虚拟营业厅 SDK 视频银行组件开始调用接口; 

(2)AnyChat 虚拟营业厅 SDK 调用接口类:AnyChatVideoBankSDK. ts; 

(3)详细调用方式可参考示例 Demo; 

返回值 **:** 

无 

示例代码 **:** 

_//_ 视频银行服务大厅业务调用接口 

AnyChatVideoBankSDK.getInstance().start(getContext(), transferModel, { 

_//_ 组件开始调用回调 _(_ 用于业务层开始 _loading_ 展示 _)_ 

onAnyChatLoginStart() { 

}, 

_//_ 组件调用登录成功 _(_ 用于业务层结束 _loading_ 展示 _)_ onAnyChatLoginSuccess() { 

}, 

_//_ 异常错误回调 

onAnyChatClientError(result: BRResultMode) { 

}, _//_ 业务完成回调 

onAnyChatClientCompleted(result: BRResultMode) { }, 

_//_ 执行向业务层发起业务回调请求 

onBusinessRequestEvent(businessType: string, requestType: BRBusinessRequestType, requestStr: string){ 

} 

}); 

## **4.1.1.** 详细接口参数说明 

### 接口参数简介: 

|名称|类型|说明|是否必 须|
|---|---|---|---|
|context|Context|上下文|是|

第 7 页共 23 页 

|model|BRTransferModel|组件外部调用业务参数对象|是|
|---|---|---|---|
|event|BRVideoRecordEvent|结果回调操作(详细说明请参考本文档3.1.5章 节)|是|

### **BRTransferModel** 业务参数对象说明 **:** 

|名称|类型|说明|是否必须|
|---|---|---|---|
|||用户参数信息 ||
|userName|string|用户姓名|是|
|idCardNumber|string|用户身份证号码|是|
|idCardTypeKey|string|证件类型字典定义标识(非必传默认 为idCardType)|否|
|idCardTypeName|string|证件类型字典名称 如:居民身份证|是|
|idCardTypeValue|string|证件类型字典值 如:110001|是|
|phoneNumber|string|用户手机号|是|
|||登录参数信息 ||
|loginIp|string|服务器登录地址|是|
|loginPort|string|服务器登录端口|是|
|loginAppId|string|商户应用ID (商户唯一标识,由佰锐科技提供)|是|
|loginStrParam|string|服务器登录自定义参数(json字符串) |是|
|||(详细说明请参考本文档3.1.2章节)||
|||业务参数信息 ||
|integratorName|string|渠道名称|是|
|integratorCode|string|渠道编码|是|
|expansion|string|扩展参数(json字符串) (详细说明请参考本文档3.1.3章节)|否|
|aiReportExtraParam|string|智能播报变量配置参数(json字符串) (详细说明请参考本文档3.1.4章节)|否|

第 8 页共 23 页 

|||其他参数信息 坐席画面是否全屏展示控制||
|---|---|---|---|
|isShowRemoteFullScreen|boolean|(默认true全屏展示)|否|
|appVersion|string|手机银行版本|否|
|deviceModel|string|设备型号|否|
|deviceId|string|设备标识|否|

## **4.1.2.** 服务器登录自定义参数说明 

#### 数据格式 **(** 标准 **json** 字符串 **):** 

{ "callTradeNo": "20221104161DEC38F0186634C4B9EDBC88D7202AE7", "sysCode": "VIRTUALHALL" 

} 

|名称|类型|说明|是否必须|
|---|---|---|---|
|callTradeNo|string|通话流水号(业务初始化接口返回)|是|
|sysCode|string|系统编号(业务初始化接口返回)|是|

#### 示例代码: 

### _//AnyChat_ 服务器登录扩展参数 _(_ 必传 _)_ 

**let** loginStrObject = {}; loginStrObject['callTradeNo'] = callTradeNo; loginStrObject['sysCode'] = sysCode; transferModel.loginStrParam = JSON.stringify(loginStrObject); 

## **4.1.3.** 扩展参数说明 

#### 说明: 

扩展参数信息,可用于传递客户当前位置信息、备注信息展示等; 

#### 数据格式 **(** 标准 **json** 字符串 **):** 

{ "address": "广州市天河区科韵路", "remarks": [ { "groupData": [ { "key": "beizhu", "name": "备注信息", "value": "支持展示支行添加客户名单时填写的备注信息" 

第 9 页共 23 页 

} 

], "groupName": "备注信息" } 

] 

#### } 

|名称|类型|说明|是否必须|
|---|---|---|---|
|address|string|位置信息,用于业务流水信息展示客户位置信息|否|
|remarks|Array|扩展分组展示信息|否|
|||remarks||
|groupName|string|分组展示名称(如:备注信息、财产信息等)|否|
|groupData|Array|分组展示具体内容|否|
|||groupData||
|key|string|属性标识|是|
|name|string|属性名称|是|
|value|string|属性值|是|

#### 示例代码: 

**let** remarksArray: Array<object> = **new** Array; **let** remarksObject = {}; remarksObject["groupName"] = "备注信息"; 

**let** groupDataArray: Array<object> = **new** Array; **let** object1 = {}; object1["key"] = "beizhu"; object1["name"] = "备注信息"; object1["value"] = "支持展示支行添加客户名单时填写的备注信息"; groupDataArray.push(object1); 

remarksObject["groupData"] = groupDataArray; remarksArray.push(remarksObject); 

**let** expansionObject = {} expansionObject["address"] = "广州市天河区科韵路"; 

第 10 页共 23 页 

expansionObject["remarks"] = remarksArray; _//_ 设置扩展参数信息 transferModel.expansion = JSON.stringify(expansionObject); 

## **4.1.4.** 智能播报变量动态配置参数说明 

#### 说明: 

智能播报变量扩展参数信息,可用于传递智能播放话术配置的变量信息,包含变量 key、 变量 value 信息; 

#### 数据格式 **(** 标准 **json** 字符串 **):** 

{ "age": "18", "amount": "10 万" } 

#### 示例代码: 

**let** extraParamJsonObject: object = **new** Object(); extraParamJsonObject['age'] = '18'; extraParamJsonObject['amount'] = '10 万'; 

**let** aiReportParam = JSON.stringify(extraParamJsonObject); _//_ 智能播报动态配置参数 

transferModel.aiReportExtraParam = aiReportParam; 

## **4.1.5. BRVideoRecordEvent** 结果回调说明 

### **BRVideoRecordEvent** 结果回调接口说明 **:** 

|返回值|名称|参数(类型):说 明|说明|备注|
|---|---|---|---|---|
|void|onAnyChatLoginS tart()|无|组件开始调用 回调(用于业 务层开始 loading展示)||
|void|onAnyChatLoginS uccess()|无|组件调用登录 成功回调(用 于业务层结束 loading展示)||

第 11 页共 23 页 

result.errCode:
onAnyChatClientE result(BRResul
状态码
void rror(result: tMode ):执行 异常错误回调
result.errMsg:
BRResultMode) 结果
描述信息
result.errCode:
状态码
onAnyChatClientC result(BRResul
0 表示本次业
void ompleted(result: tMode ):执行 结果回调
务办理结束;
BRResultMode) 结果
result.errMsg:
描述信息
uiContext : 上
uiContext : 上
onBusinessReques 下文
下文
tEvent(uiContext: businessType :
businessType :
UIContext, 当前执行请求
当前执行请求
businessType: 的业务类型 用于业务层获
的业务类型
void string, requestType : 取组件内部业
requestType: 当前请求类型 务操作请求明 requestType :
当前请求类型
BRBusinessReque requestStr : 当
requestStr :当
stType, 前请求详细数
前请求详细数
requestStr: string); 据信息(json 字
据信息
符)
4.2. AnyChat 虚拟营业厅 SDK 组件层与业务层信息交互回调接口说明
4.2.1. 业务层获取组件内部请求回调操作说明
onBusinessRequestEvent(uiContext: UIContext,businessType: string,
requestType: BRBusinessRequestType, requestStr: string);
示例代码 :
// 视频银行服务大厅业务开始调用接口
AnyChatVideoBankSDK.getInstance().start(getContext(), transferModel, {
// 组件开始调用回调 ( 用于业务层开始 loading  展示 )
onAnyChatLoginStart() {
},
// 组件调用登录成功 ( 用于业务层结束 loading  展示 )
onAnyChatLoginSuccess() {
},
// 异常错误回调
onAnyChatClientError(result: BRResultMode) {
},

_//_ 双录完成回调 

第 12 页共 23 页 

onAnyChatClientCompleted(result: BRResultMode) { 

}, 

##### _//_ 执行向业务层发起业务回调请求 

onBusinessRequestEvent(uiContext: UIContext,businessType: string, requestType: BRBusinessRequestType, requestStr: string) { 

**switch** (requestType) { 

**case** BRBusinessRequestType.TradePswInput: _//_ 交易密码输入请求 

**break** ; 

**case** BRBusinessRequestType.PswSet: _//_ 密码设置请求 

**break** ; 

**case** BRBusinessRequestType.BusinessCancel: _//_ 坐席取消业务 _(_ 用于业务层处理弹窗展示销毁处理等 _)_ **break** ; 

} 

} 

}); 

### 接口参数简介: 

|名称|类型|说明|是否必须|
|---|---|---|---|
|businessType|string|当前执行请求的业 务场景类型|是|
|requestType|BRBusinessRequestType|请求类型枚举类|是|
|requestStr|string|请求参数信息|否|
||BRBusinessRequestType 请求|类型枚举值说明||
|TradePswInput|BRBusinessRequestType|交易密码输入验证 请求|是|
|PswSet|BRBusinessRequestType|密码设置请求|是|
|BusinessCancel|BRBusinessRequestType|坐席取消业务办理|是|

## **4.2.1.1.** 交易密码输入验证请求 

||requestType请求类型定 |义字段说明 ||
|---|---|---|---|
|名称|类型|说明|是否必须|
|TradePswInput|BRBusinessRequestType requestStr组件内部请求详细|交易密码输入验证 请求 数据信息说明|是|
|userAccountNo|string|银行卡号|是|
|tradeNo|string|视频银行流水号|是|

### **requestStr** 交易密码输入验证示例数据: 

第 13 页共 23 页 

如:{"userAccountNo":"62629292919191919","tradeNo":"2023010101202310321310"} 

## **4.2.1.2.** 密码设置请求 

||requestType请求类型定义 |字段说明 ||
|---|---|---|---|
|名称|类型|说明|是否必须|
|PswSet|BRBusinessRequestType requestStr组件内部请求详细|密码设置请求 数据信息说明 |是 |
|userAccountNo|string|银行卡号|是|
|tradeNo|string|视频银行流水号|是|

**requestStr** 密码设置输入示例数据: 

如:{"userAccountNo":"62629292919191919","tradeNo":"2023010101202310321310"} 

## **4.2.1.3.** 坐席取消业务办理 

### 说明: 

主要用于在业务办理过程中,业务层弹窗(如交易密码弹窗、密码设置弹窗等)正在 展示时,坐席执行取消业务办理时,组件通知业务层执行弹窗的隐藏、销毁处理; 

||requestType请求类型定义 |字段说明 ||
|---|---|---|---|
|名称|类型|说明|是否必须|
|BusinessCancel|BRBusinessRequestType requestStr组件内部请求详细|坐席取消业务办理 数据信息说明|是|
|tradeNo|string|视频银行流水号|否|

## **4.2.2.** 业务层向组件内发送响应结果状态说明 

## **void sendBRBusinessResponse(String businessType, BRBusinessRequestType requestType, String responseStr)** 

## 说明: 

此回调接口可用于业务层向组件内部告知对应请求的响应结果状态,如交易密码输 入状态(输入完成|取消输入)、密码设置输入状态(输入完成|取消输入)等; 示例代码: 

_//_ 业务层向组件内部发送业务请求结果 

第 14 页共 23 页 

AnyChatVideoBankSDK.getInstance().sendBRBusinessResponse(businessType,requestType,response Str); 

### 接口参数简介: 

|名称|类型|说明|是否必须|
|---|---|---|---|
|businessType|string|当前执行对应请求响应 的业务类型|否|
|requestType|BRBusinessRequestType|请求类型|是|
|responseStr|string|当前响应详细数据信息 (json字符)|是|

## **4.2.2.1.** 发送交易密码输入验证请求结果详细说明 

||requestType请求类型 |定义字段说明 ||
|---|---|---|---|
|名称|类型|说明|是否必须|
|TradePswInput|BRBusinessRequestType responseStr请求业务层响|交易密码输入验证 请求 应数据信息说明|是|
|status|number|相关状态|是|
|pswCipherText|string|密码密文数据|否|

### **responseStr** 交易密码输入验证结果示例数据: 

如:输入完成:{"status":0,"pswCipherText": "密码密文数据"} 

如:输入取消:{"status":1} 

## **4.2.2.2.** 发送密码设置请求结果详细说明 

||requestType请求类型 |定义字段说明 ||
|---|---|---|---|
|名称|类型|说明|是否必须|
|PswSet|BRBusinessRequestType responseStr请求业务层响|密码设置请求 应数据信息说明 |是 |
|status|number|相关状态|是|

第 15 页共 23 页 

|pswCipherText|string|密码密文数据|否|
|---|---|---|---|

#### responseStr 交易密码输入示例数据: 

如:密码设置输入完成:{"status":0,"pswCipherText": "密码密文数据"} 如:密码设置取消输入:{"status":1} 

## **5.** 错误码 

### **5.1.** 自定义异常错误码 

|错误码|错误描述|
|---|---|
|0|业务办理结束|
|100901|组件调用相关参数校验异常提示|
|100902|服务队列获取失败|
|100903|营业厅信息获取失败|
|100904|进入营业厅失败|
|100905|进入队列失败|
|100906|进线参数错误|
|100907|进入房间失败|
|100908|坐席转接数据异常|
|100909|坐席转接进线参数错误|
|100911|用户主动挂断|
|100912|视频会话异常|
|100913|用户取消呼叫|
|100914|用户取消排队|
|100915|坐席服务异常|
|100920|本次业务办理失败|

### **5.2.** 操作错误码 

|错误码|错误描述|
|---|---|
|-2|操作失败|
|-1|connect to anychat server failed|
|0|success|

第 16 页共 23 页 

### **5.3.** 系统错误码 

错误码 错误描述
1 数据库错误
2 系统没有初始化
3 还未进入房间
4 没有足够内存
5 出现异常
6 操作被取消
7 通信协议出错
8 会话不存在
9 数据不存在
10 数据已经存在
11 无效 GUID
12 资源被回收
13 资源被占用
14 Json 解析出错
15 对象被删除
16 会话已存在
17 会话没有初始化
20 函数功能不允许
21 函数参数错误
22 设备打开错误或设备未被安装
23 没有足够的资源
24 指定的格式不能被显示设备所支持
25 指定的 IP 地址不是有效的组播地址
26 不支持多实例运行
27 文件签名验证失败
28 授权验证失败
5.4. 连接错误码
错误码 错误描述

第 17 页共 23 页 

|错误码|错误描述|
|---|---|
|100|连接服务器超时|
|101|与服务器的连接中断|
|102|连接服务器认证失败(服务器设置了认证密码)|
|103|域名解析失败|
|104|超过授权用户数|
|105|服务器功能受限制(演示模式)|
|106|只能在内网使用|
|107|版本太旧,不允许连接|
|108|Socket出错|
|109|设备连接限制(没有授权)|
|110|服务已被暂停|
|111|热备服务器不支持连接(主服务在启动状态)|
|112|授权用户数校验出错,可能内存被修改|
|113|IP被禁止连接|
|114|连接类型错误,服务器不支持当前类型的连接|
|115|服务器IP地址不正确|
|116|连接被主动关闭|
|117|没有获取到服务器列表|
|118|连接负载均衡服务器超时|
|119|服务器不在工作状态|
|120|服务器不在线|
|121|网络带宽受限|
|122|网络流量不足|
|123|不支持IPv6 Only网络|
|124|没有Master服务器在线|
|125|没有上报工作状态|

错误码 错误描述
100 连接服务器超时
101 与服务器的连接中断
102 连接服务器认证失败(服务器设置了认证密码)
103 域名解析失败
104 超过授权用户数
105 服务器功能受限制(演示模式)
106 只能在内网使用
107 版本太旧,不允许连接
108 Socket 出错
109 设备连接限制(没有授权)
110 服务已被暂停
111 热备服务器不支持连接(主服务在启动状态)
112 授权用户数校验出错,可能内存被修改
113 IP 被禁止连接
114 连接类型错误,服务器不支持当前类型的连接
115 服务器 IP 地址不正确
116 连接被主动关闭
117 没有获取到服务器列表
118 连接负载均衡服务器超时
119 服务器不在工作状态
120 服务器不在线
121 网络带宽受限
122 网络流量不足
123 不支持 IPv6 Only 网络
124 没有 Master 服务器在线
125 没有上报工作状态
5.5. 进入房间错误码
错误码 错误描述
300 房间已被锁住,禁止进入
301 房间密码错误,禁止进入

第 18 页共 23 页 

错误码 错误描述
302 房间已满员,不能进入
303 房间不存在
304 房间服务时间已到期
305 房主拒绝进入
306 房主不在,不能进入房间
307 不能进入房间
308 已经在房间里面了,本次进入房间请求忽略
309 不在房间中,对房间相关的 API 操作失败
5.6. 数据流错误码
错误码 错误描述
350 过期数据包
351 相同的数据包
352 数据包丢失
353 数据包出错,帧序号存在误差
354 媒体流缓冲时间不足
5.7. 视频呼叫错误码
错误码 错误描述
440 正在通话中
500 说话时间太长,请休息一下
501 有高级别用户需要发言,请休息一下
100101 源用户主动放弃会话
100102 目标用户不在线
100103 目标用户忙
100104 目标用户拒绝会话
100105 会话请求超时
100106 网络断线
100107 用户不在呼叫状态

第 19 页共 23 页 

### **5.8.** 排队错误码 

错误码 错误描述
750 无效的队列 ID
751 准备接受服务,离开队列
5.9. sdk 错误码
错误码 错误描述
780 与服务器的 UDP 通信异常,流媒体服务将不能正常工作
781 SDK 加载 brMiscUtil.dll 动态库失败,部分功能将失效
782 SDK 加载 brMediaUtil.dll 动态库失败,部分功能将失效
783 SDK 加载 brMediaCore.dll 动态库失败,部分功能将失效
784 SDK 加载 brMediaShow.dll 动态库失败,部分功能将失效
5.10. 视频设备错误码
错误码 错误描述
10001 打开视频设备失败
10002 未知视频输出格式
10003 驱动不支持 VIDIOC_G_FMT
10004 驱动不支持 VIDIOC_S_FMT
10005 驱动不支持 VIDIOC_G_PARM
10006 驱动不支持 VIDIOC_S_PARM
10007 驱动不支持 VIDIOC_QUERYCAP
10008 当前设备非视频采集设备
10009 采集发生错误
10010 设备不支持 mmap 和 usermap 模式
10011 获取块物理地址失败
10012 物理地址映射到虚拟地址失败
10013 视频预缓存失败
10014 获取视频失败
10015 QBUF 失败
10016 VIDIOC_STREAMON 失败

第 20 页共 23 页 

错误码 错误描述
10017 VIDIOC_STREAMOFF 失败
10018 当前摄像头可能被其他进程使用
10019 不支持视频采集模式
请求的缓冲类型不支持, 或者 VIDIOC_TRY_FMT 被使用和不支
10020
持这种缓冲类型.
5.11. 音频设备错误码
错误码 错误描述
10500 打开音频设备失败
10501 请求 hwparams 失败
10502 设置 interleaved 模式失败
10503 设置 wBitsPerSample 失败
10504 设置 SamplesPerSec 失败
10505 设置 channels 失败
10506 设置 periods 失败
10507 设置缓存尺寸失败
10508 函数:snd_pcm_hw_params 调用失败
10509 设置 rebuffer time 失败
10510 设置 rebuffer frames 失败
10511 获取 period time 失败
10512 获取 period frame 失败
10513 请求 swparams 失败
10514 设置 start threshoid 失败
10515 设置 start avail min 失败
10516 函数 snd_pcm_prepare 调用失败
10517 函数 read 调用失败
30000 创建会话失败
5.12. 业务对象错误码
错误码 错误描述
100201 已经进入一个服务区域

第 21 页共 23 页 

错误码 错误描述
100202 已经进入一个服务队列
5.13. APP ID 错误码
错误码 错误描述
100300 默认的应用 ID(空)不被支持
100301 应用登录需要签名
100302 应用签名校验失败
100303 应用 ID 不存在
100304 应用 ID 被系统锁定
100305 应用 ID 与当前服务不匹配
100306 连接的服务器不是云平台地址
100307 应用所对应的计费服务器不足
100308 应用计费模式改变
5.14. 业务服务器错误码
错误码 错误描述
100701 无效参数
100702 应用 ID 不存在
100703 Body 无效
100704 签名验证失败
100705 签名时间戳无效
100706 可用内存不够
100707 出现异常
100708 通信协议出错
100709 业务服务器执行任务超时
100710 文件不存在

第 22 页共 23 页
