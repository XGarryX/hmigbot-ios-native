# 鸿蒙FIDO1.0 SDK 

### 国民认证科技(重庆)有限公司 2024 年2 月 

版权© 2022-2025 国民认证科技(重庆)有限公司 保留一切权力。 

国民认证科技(重庆)有限公司 

|目录|
|---|
|鸿蒙FIDO1.0 SDK............................................................................................................................... 1|
|一、概述.............................................................................................................................................. 1|
|1.1 简介........................................................................................................................................ 1|
|1.2 环境要求................................................................................................................................ 1|
|二、 接口说明.................................................................................................................................... 5|
|三、开发步骤:................................................................................................................................ 19|
|四、 附录.......................................................................................................................................... 23|

国民认证科技(重庆)有限公司 

## 一、概述 

#### 1.1 简介 

本文档为鸿蒙Fido1.0 集成开发使用手册,方便开发人员快速集成。 基本概念: 

在开发FIDO 免密身份认证功能前,开发者应了解以下基本概念: 

- FIDO 协议 

- FIDO(Fast Identity Online)是一套身份认证框架协议,它由FIDO 联盟推出并持续维护。 FIDO 规范定义了一套在线身份认证的技术架构。 

- UAF 身份认证框架 

UAF(Universal Authentication Framework)意为通用身份认证框架,目的是通过生物识 

- 别(如 指纹识别)和加密技术方式,为用户提供无密码的身份认证体验。 

#### 1.2 环境要求 

#### **1.2.1** 开发环境 

#### 1.2.2 配置 

- 1、har 依赖配置 

- 1)将har 包拷贝到工程下lib 目录(可自定义其他位置) 

- 2)在模块级的oh-package.json5 文件中配置dependencies 

第 1 页 

国民认证科技(重庆)有限公司 

"dependencies": { "@gmrz/fido_ohos_sdk": "file:../lib/gm-ohos-fido-sdk_1_0_2.har" } 

###### 注意:file 路径要根据实际情况修改 

###### 2、权限配置 

###### 在应用的module.json5 文件中增加权限配置 

"requestPermissions": [ { "name": "ohos.permission.ACCESS_BIOMETRIC", "reason": "$string:bio_permission_reason", "usedScene": { "abilities": [], "when": "inuse" } }, { "name": "ohos.permission.STORE_PERSISTENT_DATA", "reason": "$string:bio_permission_reason", "usedScene": { "abilities": [ ], "when": "inuse" } 

第 2 页 

国民认证科技(重庆)有限公司 

} 

] 

###### 3、配置文件(/resources/rawfile/gmrzprofile.json)(可选) 

{ 

"priorityMode": “REMOTE” 

} 

priorityMode:认证器优先级。 

   - 1)如果设置为“REMOTE”,那么接口中mode 参数未设置情况下会优先使用预置FIDO; 

   - 2)如果设置为“LOCAL”,那么接口中mode 参数未设置情况下会优先使用keyStore FIDO; 

   - 3)如果配置文件缺失或prioritMode 设置为“REMOTE“、“LOCAL”以外的值,那么接口中mode 参数未 

- 设 置情况下会优先使用预置FIDO 

   - 4)如果接口中mode 参数传值的情况下,此配置不生效。 

4、SDK Har 包开启了字节码编译构建,在集成时,使用方需要设置useNormalizedOHMUrl 为true 

查看工程级build-profile.json5: 

{ 

"app": { 

"products": [ 

{ 

"buildOption": { 

"strictMode": { 

"useNormalizedOHMUrl": true 

} 

} 

} 

] 

第 3 页 

国民认证科技(重庆)有限公司 

} 

} 

###### 5 、Fido 服务端配置: 

1)渠道配置 

###### 2)应用配置 

应用名称生成方式:调用getFacetId 接口获取。 

3)元数据配置 

第 4 页 

###### 国民认证科技(重庆)有限公司 

4)策略配置 

上述内容需要服务端协助配置。 

## 二、接口说明 

第 5 页 

国民认证科技(重庆)有限公司 

#### **UAF 1.0** 

#### **2.1** process 

该接口负责处理Fido 注册、认证(登录、交易)、注销请求。 

process(context:Context, fidoRequest: FidoRequest): Promise<FidoResponse> 

注意:REMOTE 模式下,如果服务端配置了appID 地址,那么这个地址要确保外网能够访问到。 

##### 【请求参数】 

|名称|数据类型|必填|描述|
|---|---|---|---|
|context|Context|是|应用上下文|
|protocol|enum|否|协议: FidoProtocol.UAF :FIDO1.0 FidoProtocol.CTAP:FIDO2.0 暂未实现 默认UAF|
|fidoRequest mode|enum|否|Fido 实现方式: FidoMode.LOCAL 基于鸿蒙HUKS 实现 (keyStore 版本) FidoMode.REMOTE 基于鸿蒙内置Fido 免 密身份认证实现(预置版) 默认根据配置文件选择|
|authTypes|Array<FidoAuthType>|否|认证方式: 指纹:UAF_FINGER 人脸:UAF_FACE 默认根据服务端策略选择|
|data|string|否|请求报文|

第 6 页 

国民认证科技(重庆)有限公司 

##### 【响应结果】 

||名称|数据类型|必填|描述|
|---|---|---|---|---|
||code|FidoStatus|是|错误码枚举|
||message|string|是|错误描述|
|FidoResponse|data|string|是|响应报文|
||getFidoMode():FidoMode|方法|是|返回fido 实现方式: FidoMode.LCOAL:keyStore FidoMode.REMOTE:预置FIDO|

##### 【错误码】 

|错误码|名称|描述|场景|可能原因|处理方式|
|---|---|---|---|---|---|
|0|SUCCESS|成功|注册、认证、注 销|||
|101|NO_MATCH|无可用认证器|注册、认证|服务端未配置元数据|检查管理系统配置|
||||认证 (LOCAL)|卸载重装应用导致注 册数据丢失|注销、重新注册|
||||注册 (REMOTE)|已注册||
|301|PROTOCOL_ERROR|协议错误|注册、认证、注 销|报文不正确||
|102|KEY_INVALID_PERMANE NTLY|密钥永久失效|认证(LOCAL)|注册后生物特征信息 发生了变化导致认证 失败|注销、重新注册|
|201|CANCELLED|用户取消|注册、认证|用户取消了生物特征 识别操作|重试|
|202|USER_REGISTERED|已经注册|注册 (LOCAL)|已经注册||
|205|NO_PERMISSION|无权限|注册、认证|应用缺少权限配置|参见1.2.2|

第 7 页 

国民认证科技(重庆)有限公司 

|206|TIME_OUT|认证超时|注册、认证 (LOCAL)|生物识别UI 等待用 户操作时长超过3 分 钟||
|---|---|---|---|---|---|
|213|NOT_ENROLLED|未录入生物特 征|注册、认证|未录入生物特征|录入后重试|
|302|INVALID_PARAM|参数错误|注册、认证、注 销|参数不正确||
|303|APP_NOT_FOUND|未找到应用|注册、认证 (REOMTE)|应用配置不正确 (APPID 对应的文件 中facetID 不正确)|检查管APPID 对 应的文件中 facetID 配置是否 正确|
|401|NOT_INSTALL|设备不支持预 置FIDO|注册、认证、注 销 (REOMTE)|设备不支持预置 FIDO||
|999|FAILED|系统内部错误|注册、认证、注 销|运行时异常|可根据具体描述定 位问题|

#### **2.2** getDeviceInfo 

该接口负获取手机设备信息。 

getDeviceInfo(): Promise<FidoResponse> 

##### 【请求参数】 

##### 无。 

##### 【响应结果】 

|名称|数据类型|必填||描述|
|---|---|---|---|---|
|FidoResponse code|FidoStatus|是|错误码枚举||
|message|string|是|错误描述||

第 8 页 

国民认证科技(重庆)有限公司 

|data string|是|响应报文:设备信息JSON 格式字符串,可转|
|---|---|---|
|||换成DeviceInfo 对象|

##### 【错误码】 

|错误码|名称|描述|场景|可能原因|处理方式|
|---|---|---|---|---|---|
|0|NO_ERROR|成功||||
|205|NO_PERMISSION|无权限||应用缺少权限配置|参见1.2.2|
|999|FAILED|系统内部错误||运行时异常|可根据具体描述定 位问题|

#### **2.3** checkSupport 

检查设备是否支持FIDO 认证,支持一种认证方式,返回该认证方式的支持状态。 checkSupport(context: Context,fidoRequest: FidoRequest): Promise<FidoResponse> 

##### 【请求参数】 

|名称|数据类型|必填|描述|
|---|---|---|---|
|context|Context|是|应用上下文|
|fidoRequest protocol|enum|否|协议: FidoProtocol.UAF :FIDO1.0 FidoProtocol.CTAP:FIDO2.0 暂未实现 默认:FidoProtocol.UAF|
|(可选) mode|enum|否|Fido 实现方式: FidoMode.LOCAL 基于鸿蒙HUKS 实现 (keyStore 版本) FidoMode.REMOTE 基于鸿蒙内置Fido 免 密身份认证实现(预置版)|

第 9 页 

国民认证科技(重庆)有限公司 

||||默认:gmrzprofile 文件配置|
|---|---|---|---|
|authTypes|Array<FidoAuthType>|否|认证方式:多选 指纹:UAF_FINGER 人脸:UAF_FACE 虹膜:UAF_EYE(目前不支持) 默认全部|

##### 【响应结果】 

|名称|数据类型|必填|描述|
|---|---|---|---|
|code|FidoStatus|是|错误码枚举|
|message|string|是|错误描述|
|FidoResponse data|HashMap<FidoAuthType,b oolean>|是|K:FidoAuthType: 指纹:UAF_FINGER 人脸:UAF_FACE 虹膜:UAF_EYE V:状态: true:支持,false:不支 持|
|isFingerSupport(): boolean|方法|是|判断指纹支持情况|
|isFaceSupport():bo olean|方法|是|判断人脸支持情况|
|isEyeSupport():boo lean|方法|是|判断虹膜支持情况|
|getFingerStatus(): number|方法|是|获取指纹支持状态|
|getFaceStatus():nu mber|方法|是|获取人脸支持状态|

第 10 页 

国民认证科技(重庆)有限公司 

|getEyeStatus():num ber|方法|是|获取虹膜支持状态|
|---|---|---|---|
|getFidoMode():Fido Mode|方法|是|返回fido 实现方式: FidoMode.LCOAL: keyStore FidoMode.REMOTE:预置 FIDO|

##### 【错误码】 

|错误码|名称|描述|场景|可能原因|处理方式|
|---|---|---|---|---|---|
|0|NO_ERROR|支持||||
|302|INVALID_PARAM|参数错误||参数不正确||
|999|FAILED|不支持||||

##### **2.4 checkNetSupport** 

检查设备和服务端是否支持某种FIDO 认证方式,可指定一种交易场景,多种认证方式,返回该该场景 下,认证方式的支持状态(客户端、服务端同时支持才认为是支持)。 

checkNetSupport(context: Context,fidoRequest: FidoRequest): Promise<FidoResponse> 

前置条件:先调用服务端/v2/device/support 接口,将响应报文作为接口入参fidoRequest.data 字 段的值。 

##### 【请求参数】 

|名称|数据类型|必填|描述|
|---|---|---|---|
|context|Context|是|应用上下文|
|fidoRequest protocol|enum|否|协议: FidoProtocol.UAF :FIDO1.0 FidoProtocol.CTAP:FIDO2.0 暂未实现 默认:FidoProtocol.UAF|

第 11 页 

国民认证科技(重庆)有限公司 

|mode|enum|否|Fido 实现方式: FidoMode.LOCAL 基于鸿蒙HUKS 实现 (keyStore 版本) FidoMode.REMOTE 基于鸿蒙内置Fido 免 密身份认证实现(预置版) 默认:gmrzprofile 文件配置|
|---|---|---|---|
|authTypes|Array<FidoAuthType>|否|认证方式:多选 指纹:UAF_FINGER 人脸:UAF_FACE 虹膜:UAF_EYE(目前不支持) 默认全部|
|transType|FidoTransType|否|使用场景: FidoTransType.UAF_LOGIN:登录 FidoTransType.UAF_TRADE:交易 默认:FidoTransType.UAF_LOGIN|
|data|string|是|服务端v2/device/support 接口响应报 文。支持完整报文,同时兼容uafRequest 节点报文。|

##### 【响应结果】 

||名称|数据类型|必填|描述|
|---|---|---|---|---|
||code|FidoStatus|是|错误码枚举|
||message|string|是|错误描述|
|FidoResponse|data|HashMap<FidoAuthType ,boolean>|是|K:FidoAuthType: 指纹:UAF_FINGER 人脸:UAF_FACE V:状态 true:支持,false:不支持|

第 12 页 

国民认证科技(重庆)有限公司 

|isFingerSupport() :boolean|方法|是|判断指纹支持情况|
|---|---|---|---|
|isFaceSupport(): boolean|方法|是|判断人脸支持情况|
|isEyeSupport(): boolean|方法|是|判断虹膜支持情况|
|getFingerStatus() :number|方法|是|获取指纹支持状态|
|getFaceStatus():n umber|方法|是|获取人脸支持状态|
|getEyeStatus():nu mber|方法|是|获取虹膜支持状态|
|getFidoMode():Fid oMode|方法|是|返回fido 实现方式: FidoMode.LCOAL:keyStore FidoMode.REMOTE:预置FIDO|

##### 【错误码】 

|错误码|名称|描述|场景|可能原因|处理方式|
|---|---|---|---|---|---|
|0|NO_ERROR|支持||||
|302|INVALID_PARAM|参数错误||参数不正确||
|999|FAILED|不支持||||

##### **2.5 getDeviceId** 

###### 获取设备ID 

getDeviceId(): Promise<string> 

##### 【请求参数】 

第 13 页 

国民认证科技(重庆)有限公司 

##### 无 

##### 【响应结果】 

||名称|数据类|型|必填||描述|
|---|---|---|---|---|---|---|
|无||string||是|设备I|D|
|【错误 错误码|码】 名称|描述|场景|可能原|因|处理方式|
|0|NO_ERROR|成功|||||
|205|NO_PERMISSION|无权限||应用缺少权限|配置|参见1.2.2|
|999|FAILED|系统内部错误||运行时异|常|可根据具体描述定 位问题|

##### **2.6 getSdkVersion** 

获取SDK 版本 getSdkVersion(): string 

##### 【请求参数】 

##### 无。 

##### 【响应结果】 

||名称|数据类型|必填||描述|
|---|---|---|---|---|---|
|无||string|是|SDK 版本||

第 14 页 

国民认证科技(重庆)有限公司 

##### 【错误码】 

##### 无。 

##### **2.7 isEnrolled** 

查询设备是否已经录入生物特征。 isEnrolled(authType:FidoAuthType): FidoResponse 

##### 【请求参数】 

|名称|数据类型|必填|描述|
|---|---|---|---|
|authTypes|FidoAuthType[]|否|认证方式:可多选 指纹:UAF_FINGER 人脸:UAF_FACE 虹膜:UAF_EYE 默认全部|

##### 【响应结果】 

||名称|数据类型|必填|描述|
|---|---|---|---|---|
||code|FidoStatus|是|错误码枚举|
||message|string|是|错误描述|
|FidoResponse|data|HashMap<FidoA uthType,numbe r>|是|K:FidoAuthType: 指纹:UAF_FINGER 人脸:UAF_FACE V:状态: 0:已录入生物特征|

第 15 页 

国民认证科技(重庆)有限公司 

|||101:不支持的认证方式 205:未配置权限 213:未录入生物特征 999:其他内部错误|
|---|---|---|
|getFingerEnrollState():nu mber|方法|获取指纹录入状态|
|getFaceEnrollState():numb er|方法|获取人脸录入状态|
|getEyeEnrollState():boole an|方法|获取虹膜录入状态|

##### 【错误码】 

|错误码|名称|描述|场景|可能原因|处理方式|
|---|---|---|---|---|---|
|0|NO_ERROR|已录入||||
|302|INVALID_PARAM|参数错误||参数不正确||
|999|FAILED|未录入||||

##### **2.8 subscribeLog** 

SDK 日志订阅接口。 

subscribeLog(context: Context, callback: Function): Promise<void>; 

##### 【请求参数】 

|名称|数据类型|必填|描述|
|---|---|---|---|
|context|Context|是|上下文|
|callback|Function|是|日志回调函数,返回string 类型JSON 格式 日志|

##### 【响应参数】 

第 16 页 

国民认证科技(重庆)有限公司 

|名称|数据类型|必填|描述|
|---|---|---|---|
|domain_|string|是|事件域,固定值:GM_OH_FIDO|
|name_|string|是|事件类型; DEFAULT:默认 LOCAL_UAF_PROCESS:process 接口调用 LOCAL_UAF_REG:注册操作 LOCAL_UAF_AUTH:认证操作 LOCAL_UAF_DE_REG:注销操作 REMOTE_UAF_REG:预置FIDO 注册操作 REMOTE_UAF_AUTH:预置FIDO 认证操作 REMOTE_UAF_DE_REG:预置FIDO 注销操作 CHECK_NET_SUPPORT:checkNetSuppor 接口调 用 CHECK_SUPPORT:checkSupport 接口调用 GET_DEVICE_ID:getDeviceID 接口调用 GET_DEVICE_INFO:getDeviceInfo 接口调用 GET_SDK_VERSION:getSdkVersion 接口调用 IS_ENROLLED:isEnrolled 接口调用|
|type_|number|是|1 错误事件 4 用户操作|
|time_|number|是|时间戳|
|tz_|string|是|时区|
|pid_|number|是|进程ID|
|tid_|number|是|线程ID|
|time|string|是|格式化时间:yyyy/MM/dd HH:mm:ss:sss|
|level|string|是|日志级别:DEBUG、INFO、WARN、ERROR|
|message|string|是|日志内容|
|tag|String|是|自定义TAG|

第 17 页 

国民认证科技(重庆)有限公司 

|deviceInfo String|是 设备信息,包含sdk 版本信息|
|---|---|

##### 【错误码】 

|错误码|名称|描述|场景|可能原因|处理方式|
|---|---|---|---|---|---|
|999|FAILED|系统内部错误||运行时异常|可根据具体描述定 位问题|

##### **2.9 unsubscribeLog** 

取消SDK 日志订阅。 unSubscribeLog(): void; 

##### 【请求参数】 

无。 

##### 【响应参数】 

无。 

##### **2.10 getFacetId** 

获取应用facetID。 getFacetId(): Promise<string> 

##### 【请求参数】 

##### 无。 

##### 【响应结果】 

||名称|数据类型|必填||描述|
|---|---|---|---|---|---|
|无||string|是|facetID||

##### **2.11 processBase64** 

该接口同process,但要求data 为base64URL 编码报文,且返回FidoResponse.data 也是base64URL 

第 18 页 

国民认证科技(重庆)有限公司 

编码格式。 

processBase64(context:Context, fidoRequest: FidoRequest): Promise<FidoResponse> 

##### **2.12 checkNetSupportBase64** 

该接口同checkNetSupport,但要求data 为base64URL 编码报文。 

checkNetSupportBase64(context: Context,fidoRequest: FidoRequest): Promise<FidoResponse> 

## 三、开发步骤: 

###### 1. 需要业务方自行根据FIDO 标准协议部署FIDO 服务器。 

2. 导入FidoSdk 

import { FidoSdk } from '@gmrz/fido_sdk'; 

###### 3. 获取设备信息(可选) 

###### 实施方可调用该接口获取设备信息,也可自行获取设备信息,用于服务端接口请求报文的填充。 

```arkts
this.fidoSdk.getDeviceInfo().then(response=>{ let deviceInfo = JSON.parse(response.data as string) as DeviceInfo promptAction.showToast({ message: '设备信息:' + JSON.stringify(deviceInfo), duration: 5000 }) console.log("deviceInfo::",JSON.stringify(deviceInfo)); }).then(e:Error)=>{ promptAction.showToast({ message: '获取设备信息失败:' + e.message, duration: 5000 }) }) 
```

4、检查设备是否支持 

第 19 页 

国民认证科技(重庆)有限公司 

let fidoRequest: FidoRequest = { 

protocol: FidoProtocol.UAF, 

op: FidoOperation.DISCOVER, 

mode: FidoMode.LOCAL, 

authTypes: [FidoAuthType.UAF_FINGER] 

} 

this.fidoSdk.checkSupport(getContext(this), fidoRequest).then(response => { 

//调用成功 

let fingerSupport = response.isFingerSupport(); //true 支持 

//或者 

let status = response.getFingerStatus();// 0:支持 

}) 

###### 5、开通FIDO 免密认证 

###### 1)访问FIDO 服务端/uaf/reg/receive 接口,获取注册请求报文(uafRequest 部分) 

###### 2)调用process 接口进行注册 

let fidoRequest: FidoRequest = { 

protocol: FidoProtocol.UAF, 

op: FidoOperation.UAF_OPERATION, 

mode: FidoMode.LOCAL, 

data:serverMessage // 步骤1)返回报文 

authTypes:[FidoAuthType.UAF_FINGER] 

} 

this.fidoSdk.process(getContext(this), fidoRequest).then(fidoResponse => { 

if(fidoResponse.code==FidoStatus.SUCCESS){ 

regSendData.uafResponse = fidoResponse.data as string; 

// 访问FIDO 服务端,完成注册 

httpPost(this.baseUrl + "/uaf/reg/send", JSON.stringify(regSendData)).then(response => { 

if (response.responseCode == http.ResponseCode.OK) { 

let result = response.result as string 

et serverResponse: UAFServerResponse = JSON.parse(result) as UAFServerResponse; 

if (serverResponse.statusCode == 1200) { 

promptAction.showToast({ 

message: '注册成功', 

duration: 5000 

}) 

} else { 

promptAction.showToast({ 

第 20 页 

国民认证科技(重庆)有限公司 

message: '注册失败(server)' + JSON.stringify(serverResponse), duration: 5000 }) } } }) }else{ promptAction.showToast({ message: '注册失败(client)' + JSON.stringify(fidoResponse), duration: 5000 }); } ) 

###### 6、使用FIDO 免密认证 

###### 1)访问FIDO 服务端,获取认证请求报文(uafRequest 部分) 

###### 2)调用process 接口进行认证 

let fidoRequest: FidoRequest = { 

protocol: FidoProtocol.UAF, 

op: FidoOperation.UAF_OPERATION, mode: FidoMode.LOCAL, 

data:serverMessage, // 步骤1)返回报文 authTypes:[FidoAuthType.UAF_FINGER] } 

this.fidoSdk.process(getContext(this), fidoRequest).then(fidoResponse => { 

if(fidoResponse.code==FidoStatus.SUCCESS){ 

//本地认证成功 

regSendData.uafResponse = fidoResponse.data as string; 

// 访问FIDO 服务端,完成认证 

httpPost(this.baseUrl + "/uaf/auth/send", JSON.stringify(regSendData)).then(response => { if (response.responseCode == http.ResponseCode.OK) { 

let result = response.result as string 

et serverResponse: UAFServerResponse = JSON.parse(result) as UAFServerResponse; 

if (serverResponse.statusCode == 1200) { 

promptAction.showToast({ 

message: '认证成功', duration: 5000 

}) 

} else { promptAction.showToast({ 

第 21 页 

国民认证科技(重庆)有限公司 

message: '认证失败(server)' + JSON.stringify(serverResponse), duration: 5000 }) } } }) }else{ promptAction.showToast({ message: '认证失败(client)' + JSON.stringify(fidoResponse), duration: 5000 }); } ) 

###### 7、关闭FIDO 免密认证 

###### 1)访问FIDO 服务端,注销FIDO 

###### 2)调用process 接口进行本地注销 

let fidoRequest: FidoRequest = { protocol: FidoProtocol.UAF, 

op: FidoOperation.UAF_OPERATION, mode: FidoMode.LOCAL, 

data:serverMessage, // 步骤1)返回报文 authTypes:[FidoAuthType.UAF_FINGER] } 

this.fidoSdk.process(getContext(this), fidoRequest).then(response => { console.log("sample", JSON.stringify(response)); 

If(response.code==FidoStatus.SUCCESS){ 

promptAction.showToast({ 

message: '注销成功', duration: 5000 

}) }else{ 

promptAction.showToast({ 

message: '注销失败', duration: 5000 

}) 

} 

}) 

第 22 页 

国民认证科技(重庆)有限公司 

## 四、附录 

#### 错误码 

|Android|英文名|鸿蒙|英文名|
|---|---|---|---|
|0|SUCCESS|0|SUCCESS 旧名:NO_ERROR|
|101|NO_MATCH|101 旧code:5|NO_MATCH 旧名:NO_SUITABLE_AUTHENTICATOR|
|102|KEY_INVALID_PERMANENTLY|102|KEY_INVALID_PERMANENTLY|
|201|CANCELED|201|CANCELED|
|202|USER_REGISTED|202|USER_REGISTED|
|203|WAIT_USER_ACTION(预留未使用)|无|无|
|205|NO_PERMISSION|205|NO_PERMISSION|
|206|SUB_MODULE_RESPONSE_TIMEOUT|206|TIME_OUT|
|207|GM_NEED_REGISTER(预留未使用)|无|无|
|208|EXIT_THIS_TIME|无|无|
|209|IS_BUSY|无|无|
|210|ADDUVI|无|无|
|212|SELECT_MODULE_FAILED|无|无|
|213|NOT_HAVE_FINGERPRINT|213|NOT_ENROLLED|
|301|PROTOCOL_ERROR|301|PROTOCOL_ERROR|
|302|INVALID_PARAM|302|INVALID_PARAM(新增)|
|303|APP_NOT_FOUND|303 (旧code:218)|APP_NOT_FOUND (旧名:UNTRUSTED_FACET_ID)|
|304|NOT_INITFIDO|无|无|
|306|USER_PREFERRED_BIO_IRIS(预留未使用)|无|无|
|401|NOT_INSTALLED|401|NOT_INSTALLED|
|402|NO_BIOLOGICAL(预留未使用)|无|无|

第 23 页 

国民认证科技(重庆)有限公司 

999 FAILED 999 FAILED 旧 code : 255 旧名 :INNER_ERROR 

#### 报文样例 

###### 1. 服务端注册请求报文样例 

{ "context": { "appID": "1121", "opType": "00", "transNo": "transNoUacLocation", "userName": "ctk", "deviceID": "qr/CU6ZY+r7jPihO5SzhsIuOjp77s8kAOktKvk9qVgCFJsawRslIXoo40P5iVU8D", "transType": "00", "authType": "00", "devices": { "deviceID": "qr/CU6ZY+r7jPihO5SzhsIuOjp77s8kAOktKvk9qVgCFJsawRslIXoo40P5iVU8D", deviceName": "NOH-AN00", "deviceAliasName": "HUAWEI Mate 40 Pro", "deviceType": "HUAWEI", "osVersion": 11, “sdkVersion”:0.1.2 "osType": "HarmonyOS", "deviceisRoot": false, "deviceVersion": "LIO-AL00 4.0.0.116(SP10C00E116R5P4)" } } } 

###### 2. 服务端注册完成请求报文样例 

{ "uafResponse": "SDK 注册响应报文", "context": { "appID": "1121", "opType": "00", "transNo": "transNoUacLocation", "userName": "ctk", "transType": "00", "authType": "00", "mobile": "16604469499", "devices": { "deviceID": "qr/CU6ZY+r7jPihO5SzhsIuOjp77s8kAOktKvk9qVgCFJsawRslIXoo40P5iVU8D", deviceName": "NOH-AN00", 

第 24 页 

国民认证科技(重庆)有限公司 

"deviceAliasName": "HUAWEI Mate 40 Pro", 

"deviceType": "HUAWEI", "osVersion": 11, 

“sdkVersion”:0.1.2 

"osType": "HarmonyOS", 

"deviceisRoot": false, 

"deviceVersion": "LIO-AL00 4.0.0.116(SP10C00E116R5P4)" 

} } 

} 

###### 3. 服务端认证请求报文样例 

{ 

"context": { 

"userName": "ctk", 

"appID": "1121", 

"transNo": "transNoUacLocation", "transType": "00", "authType": [ 

"00" 

], 

"devices": { 

"deviceID": "qr/CU6ZY+r7jPihO5SzhsIuOjp77s8kAOktKvk9qVgCFJsawRslIXoo40P5iVU8D", "deviceName": "NOH-AN00", 

"deviceAliasName": "HUAWEI Mate 40 Pro", 

"deviceType": "HUAWEI", "osVersion": 11, 

“sdkVersion”:0.1.2 

"osType": "HarmonyOS", 

"deviceisRoot": false, 

"deviceVersion": "LIO-AL00 4.0.0.116(SP10C00E116R5P4)" 

}, 

"transactionText": 

"6L2s6LSm6YeR6aKdMTAwLjAw5pS25qy-5Lq65byg5LiJ5pS25qy-6LSm5oi3NjIxNDY2NjY2NjY2NjY2NuS7mOasvui0puaIt-aUtuasvui0puaI tzYyMTQ2NjY2NjY2NjY2NjY" 

} 

} 

###### 4. 服务端认证完成请求报文样例 

{ 

"uafResponse": "SDK 认证响应报文", 

"context": { 

"userName": "ctk", 

"appID": "1121", 

第 25 页 

国民认证科技(重庆)有限公司 

"transNo": "transNoUacLocation", "transType": "00", "authType": [ "00" ], "devices": { "deviceID": "qr/CU6ZY+r7jPihO5SzhsIuOjp77s8kAOktKvk9qVgCFJsawRslIXoo40P5iVU8D", deviceName": "NOH-AN00", "deviceAliasName": "HUAWEI Mate 40 Pro", "deviceType": "HUAWEI", "osVersion": 11, “sdkVersion”:0.1.2 "osType": "HarmonyOS", "deviceisRoot": false, "deviceVersion": "LIO-AL00 4.0.0.116(SP10C00E116R5P4)" }, } } 

###### 5. 服务端注销请求报文样例 

{ "context": { "userName": "ctk", "appID": "1121", "transNo": "transNoUacLocation", "transType": "00", "authType": "00", "deviceID": "qr/CU6ZY+r7jPihO5SzhsIuOjp77s8kAOktKvk9qVgCFJsawRslIXoo40P5iVU8D", "from": "00" } } 

#### **HAP 本地安装** 

###### 手机与PC 连接后: 

- 1 通过命令行进入到 <鸿蒙sdk 安装目录>/base/toolchains 目录 

第 26 页 

国民认证科技(重庆)有限公司 

###### 2 执行hdc install -r <安装包绝对或相对路径> 

###### 注意:安装包路径中不能包含中文目录。 

#### **查看手机日志** 

###### 手机与PC 连接后: 

- 1 通过命令行进入到 <鸿蒙sdk 安装目录>/base/toolchains 目录 

- 2 执行hdc hilog 或者 hdc hilog > d:/hos.log 

#### **常见问题** 

1. SDK 是否需要初始化 

- A:不需要 

2. 是否需要本地以及智能登录能力检查 

- A:checkSupport 接口,用于设备本地FIDO 支持能力检查 

第 27 页 

国民认证科技(重庆)有限公司 

3. 注册、认证如何区分指纹、人脸(不是3D) 

- A:增加了authTypes 参数,用于指定用户认证方式。 

###### 4. getDeviceInfo 作用 

- A:辅助功能,用于填充请求报文中设备相关信息。如果用户有自己获取设备信息的方法,此 

###### 接口可忽略。 

5. 注册 uafRequest 字符串, 是否对应 fidoRequest , 之 前是 FidoIn.Builder().setFidoIn(new 

String(Base64.decode(uafRequest,Base64.DEFAULT),"UTF-8")) 

- A:如果服务端返回报文是Base64 格式的话,需要先转码。SDK 本身要求报文为明文字符串。 

###### 报文格式详见集成文档。 

6. 注册、认证怎么区分FidoStatus CANCELED、EXIT_THIS_TIME 

- A:已增加CANCELED 错误码,鸿蒙SDK 暂没有发现EXIT_THIS_TIME 的情况。 

7. REMOTE 方式下注册,服务端报3025 

- A:检查服务器时间是否准确。有可能是在校验证书链个人证书时,服务器时间晚于证书启用 

###### 时间。 

第 28 页
