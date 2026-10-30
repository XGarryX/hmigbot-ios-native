# 接入文档: 

## 一、开发环境 

HarmonyOS 6.0.0 Release SDK DevEco Studio 6.0.0 Release 

## 二、基本配置 

##### 1、har 依赖配置 

- 1)将har 包拷贝到工程下lib 目录(可自定义其他位置) 

- 2)在应用级的oh-package.json5 文件中配置dependencies 

"dependencies": { "@gmrz/fido-ohos-cert-sdk": "file:./libs/gm-fido-ohos-cert-sdk-5.5.3-b.har" } 

##### 注意: 

##### 1 file 路径要根据实际情况修改 

- 2、配置文件(gmrzprofile.json 可选) 

{ 

##### //指纹超时时间,单位:秒,可选,默认180 秒 

"timeout": 60, 

//pin 认证器pin 码复杂度校验正则表达式base64 编码,可选 

"pinRegx":"Xi4qKFswLTldKVwxezR9Lip8LiooWzAtOV0pXDIoWzAtOV0pXDMoWzAtOV0pXDQuK nwuKihbMC05XSlcNVw1KFswLTldKVw2XDYuKnwuKig/OjAxMjM0fDEyMzQ1fDIzNDU2fDM0NTY3fDQ 1Njc4fDU2Nzg5fDk4NzY1fDg3NjU0fDc2NTQzfDY1NDMyfDU0MzIxfDQzMjEwfDA5ODc2KS4qJA==" 

} 

##### 注:文件位置:app 主应用rawfile 资源目录 

##### 3、权限配置 

###### 在应用的module.json5 文件中增加权限配置 

"requestPermissions": [ 

{ 

"name": "ohos.permission.ACCESS_BIOMETRIC", 

"reason": "$string:bio_permission_reason", "usedScene": { "abilities": [], "when": "inuse" } }, { 

"name": "ohos.permission.STORE_PERSISTENT_DATA", "reason": "$string:bio_permission_reason", "usedScene": { "abilities": [ ], "when": "inuse" } } ] 

#### **三、接口说明** 

### FidoCertSdk 

#### process 

该接口负责处理Fido 注册、认证、注销等请求。 

process(context:Context, fidoRequest: FidoRequest): Promise<FidoResponse> 

### 【请求参数】 

|名称|数据类型|必 填|描述|
|---|---|---|---|
|context|Context|是|应用上下文|
|protocol|FidoProtocol|否|协议: FidoProtocol.UAF_CERT :FIDO 证书 默认:FidoProtocol.UAF_CERT|
|fidoRequest mode|FidoMode|否|Fido 实现方式: FidoMode.LOCAL 基于鸿蒙HUKS 实现 默认:FidoMode.LOCAL|
|authTypes|Array<FidoAuthType>|否|认证方式:多选一(1 个元素的 数组) 指纹:UAF_CERT_FINGER|
|data|string|否|请求报文|

### 【响应结果】 

|名称|数据类型|必填|描述|
|---|---|---|---|
|code|FidoStatus|是|错误码枚举|
|FidoResponse message|string|是|错误描述|
|data|string|boolean|是|响应报文|

#### checkSupport 

检查设备是否支持认证,可同时指定多种认证方式,返回每种认证方式的支持状态。 checkSupport(context: Context,fidoRequest: FidoRequest): Promise<FidoResponse> 

### 【请求参数】 

|名称|数据类型|必 填|描述|
|---|---|---|---|
|context|Context|是|应用上下文|
|protocol|FidoProtocol|否|协议: FidoProtocol.UAF_CERT :FIDO 证书|
|FidoRequest mode|FidoMode|否|Fido 实现方式: FidoMode.LOCAL 基于鸿蒙HUKS 实现 默认:FidoMode.LOCAL|
|authTypes|Array<FidoAuthType>|否|认证方式:可多选 指纹:UAF_FINGER_CERT PIN:UAF_PIN_CERT TUI PIN:UAF_TUI_PIN_CERT(默 认)|

### 【响应结果】 

||名称|数据类型|必填|描述|
|---|---|---|---|---|
|FidoRespons|code|FidoStatus|是|错误码枚举|

|e|message|string|是|错误描述|
|---|---|---|---|---|
||data|HashMap<FidoAuthType, boolean>|是|K:FidoAuthType: 指纹:UAF_FINGER 人脸:UAF_FACE V:状态: true:支持,false:不支 持|
||isFingerSupport() :boolean|方法|是|判断是否支持指纹认证 方式|

#### checkNetSupport 

检查设备和服务端是否支持某种FIDO 认证方式,可同时指定多种认证方式,返回每种认 证方式的支持状态(客户端、服务端同时支持才返回true,否则返回false)。 

checkNetSupport(context: Promise<FidoResponse> 

Context,fidoRequest: FidoRequest): 

前置条件:先调用服务端v2/device/support 接口,将响应报文作为接口入参 fidoRequest.data 字段的值。 

### 【请求参数】 

|名称|数据类型|必 填|描述|
|---|---|---|---|
|context|Context|是|应用上下文|
|FidoRequest protocol|FidoProtocol|否|协议: FidoProtocol.UAF_CERT : FIDO1.0 FidoProtocol.CTAP:FIDO2.0 暂未实现|

||||默认:FidoProtocol.UAF_CERT|
|---|---|---|---|
|mode|FidoMode|否|Fido 实现方式: FidoMode.LOCAL 基于鸿蒙HUKS 实现 默认:FidoMode.LOCAL|
|authTypes|Array<FidoAuthType>|否|认证方式:可多选 指纹:UAF_FINGER_CERT PIN:UAF_PIN_CERT TUI PIN:UAF_TUI_PIN_CERT(默 认)|
|data|string|是|服务端v2/device/support 接 口响应报文。支持完整报文,同 时兼容uafRequest 节点报文。|

### 【响应结果】 

||名称|数据类型|必 填|
描述|
|---|---|---|---|---|
||code|FidoStatus||是错误码枚举|
||message|string|是|错误描述|
|FidoRespon se|data|HashMap<FidoAuthType,bool ean>|是|K: FidoAuthType : 指纹: UAF_FINGER 人脸: UAF_FACE [0] V:状态 true:支 持,false:不 支持|

|isFingerSupport():boo|方法|是 判断是否支持|
|---|---|---|
|lean||指纹认证方式|

#### getCert 

##### 查询证书信息 

getCert(context: Context, fidoRequest: FidoRequest): Promise<FidoResponse>; 依赖:访问服务端接口/uaf/user/info 接口 

### 【请求参数】 

|名称|数据类型|必 填|描述|
|---|---|---|---|
|context|Context|是|应用上下文|
|protocol|enum|否|协议: 默认: FidoProtocol.UAF_CERT :FIDO 证书|
|fidoRequest mode|enum|否|Fido 实现方式: FidoMode.LOCAL 基于鸿蒙HUKS 实现 默认:FidoMode.LOCAL|
|authTypes|Array<FidoAuthType>|是|认证方式:(1 个元素的数组) 指纹:UAF_FINGER_CERT PIN:UAF_PIN_CERT TUI PIN:UAF_TUI_PIN_CERT|
|data|string|否|通过调用服务端接口 /uaf/user/info 接口获取|

### 【响应结果】 

|名称|数据类型|必填|描述|
|---|---|---|---|
|code|FidoStatus|是|错误码枚举|
|message|string|是|错误描述|
|FidoResponse data|string|是|JSON 格式证书详细信息 issuerName:string 证书颁发者 subjectName:string 证书主体 version:number 证书版本 serialNumber:证书序列号 beginTime:string 证书启用时间 endTime:string 证书停用时间 algoName:string 证书签名算法 pubKey:string 证书公钥(raw 格 式)|

#### storeCertAgain 

##### 证书重新下载 

storeCertAgain(context: Context, fidoRequest: FidoRequest): Promise<FidoResponse>; 依赖:访问服务端接口/uaf/user/info 接口 

### 【请求参数】 

|名称|数据类型|必 填|描述|
|---|---|---|---|
|context|Context|是|应用上下文|
|fidoRequest protocol|enum|否|协议: 默认: FidoProtocol.UAF_CERT :FIDO 证书|
|mode|enum|否|Fido 实现方式: FidoMode.LOCAL基于鸿蒙HUKS|

||||实现 默认:FidoMode.LOCAL|
|---|---|---|---|
|authTypes|Array<FidoAuthType>|是|认证方式:(1 个元素的数组) 指纹:UAF_FINGER_CERT|
||||PIN:UAF_PIN_CERT|
||||TUI PIN:UAF_TUI_PIN_CERT|
|data|string|否|通过调用服务端接口 /uaf/user/info 接口获取|

### 【响应结果】 

|名称|数据类型|必填|描述|
|---|---|---|---|
|code|FidoStatus|是|错误码枚举|
|FidoResponse message|string|是|错误描述|
|data|string|是|JSON 数组字符串格式 [{“keyID”:“value”}]|

#### clearCert 

##### 清除手机端冗余数据 

clearCert(context: Context, fidoRequest: FidoRequest): Promise<FidoResponse>; 依赖:访问服务端接口/uaf/user/allinfo 接口 

### 【请求参数】 

|名称 context|数据类型 Context|必 填 是|描述 应用上下文|
|---|---|---|---|
|fidoRequest protocol|enum|否|协议: 默认:|

||||FidoProtocol.UAF_CERT :FIDO 证书|
|---|---|---|---|
|mode|enum|否|Fido 实现方式: FidoMode.LOCAL 基于鸿蒙HUKS 实现 默认:FidoMode.LOCAL|
|authTypes|Array<FidoAuthType>|
否|认证方式:(1 个元素的数组)
指纹:UAF_FINGER_CERT
PIN:UAF_PIN_CERT
TUI PIN:UAF_TUI_PIN_CERT|
|data|string|是|通过调用服务端接口 /uaf/user/allinfo 接口获取|

### 【响应结果】 

|名称|数据类型|必填|描述|
|---|---|---|---|
|code|FidoStatus|是|错误码枚举|
|FidoResponse message|string|是|错误描述|
|data||否||

#### reset 

清除客户端所有注册记录 

reset(): Promise<FidoResponse> 

依赖:访问服务端接口/uaf/devcie/info 接口获取请求报文 

### 【请求参数】 

|名称|数据类型|必 填|描述|
|---|---|---|---|
|context|Context|是|应用上下文|
|protocol|enum|否|协议: 默认: FidoProtocol.UAF_CERT :FIDO 证书|
|fidoRequest mode|enum|否|Fido 实现方式: FidoMode.LOCAL 基于鸿蒙HUKS 实现 默认:FidoMode.LOCAL|
|authTypes|Array<FidoAuthType>|
否|认证方式:(1 个元素的数组)
指纹:UAF_FINGER_CERT
PIN:UAF_PIN_CERT
TUI PIN:UAF_TUI_PIN_CERT|
|data|string|是|通过调用服务端接口 /uaf/device/info 接口获取|

### 【响应结果】 

|名称|数据类型|必填|描述|
|---|---|---|---|
|code|FidoStatus|是|错误码枚举|
|FidoResponse message|string|是|错误描述|
|data||否||

processBase64 

该接口同process,但要求data 为base64URL 编码报文,且返回FidoResponse.data 

也是base64URL 编码格式。 

processBase64(context:Context, Promise<FidoResponse> 

fidoRequest: FidoRequest): 

#### checkNetSupportBase64 

该接口同checkNetSupport,但要求data 为base64URL 编码报文。 checkNetSupportBase64(context: Context,fidoRequest: FidoRequest): 

Promise<FidoResponse> 

#### changePin 

修改PIN 码 changePin(context:Context,fidoRequest:FidoRequest): Promise<FidoResponse> 

依赖:访问服务端接口/uaf/user/info 接口获取请求报文 

### 【请求参数】 

|名称|数据类型|必填|描述|
|---|---|---|---|
|context|Context|是|应用上下文|
|protocol|enum|否|协议: 默认:FidoProtocol.UAF_CERT : FIDO 证书|
|fidoRequest mode|enum|否|Fido 实现方式: FidoMode.LOCAL 基于鸿蒙HUKS 实 现 默认:FidoMode.LOCAL|
|data|string|是|通过调用服务端接口 /uaf/user/info 接口获取|

### 【响应结果】 

|名称 数据类型|必填 描述|
|---|---|

||code|FidoStatus|是|错误码枚举|
|---|---|---|---|---|
|FidoResponse|message|string|是|错误描述|
||data||否||

#### setTUI 

设置PIN UI 页面,并将保存设置。软PIN 应用卸载重装后,设置内容丢失,需要重新 设置,TUI PIN 设置后,设置内容不会丢失。 

注意:如果使用TUI 功能,使用前必须调用该方法至少一次,因为TUI 无缺省图片 

setTUI(context:Context, fidoRequest: FidoRequest): Promise<FidoResponse> 

### 【请求参数】 

|名称|数据类型|必 填|描述|
|---|---|---|---|
|context|Context|是|应用上下文|
|protocol|enum|否|协议: 默认: FidoProtocol.UAF_CERT :FIDO 证书|
|fidoRequest authTypes|Array<FidoAuthType>|否|认证方式:多选一(1 个元素的 数组) PIN:UAF_PIN_CERT TUI PIN:UAF_TUI_PIN_CERT|
|data|string|是|JSON 格式配置项,详见附录PIN 配置项|

### 【响应结果】 

|名称|数据类型|必填|描述|
|---|---|---|---|
|code|FidoStatus|是|错误码枚举|
|FidoResponse message|string|是|错误描述|
|data|string|否||

### FidoCertProSdk 

#### checkSupport 

检查设备和服务端是否支持某种FIDO 认证方式,可同时指定多种认证方式,返回每种认 证方式的支持状态(客户端、服务端同时支持才返回true,否则返回false),并可以根据 用户指定的认证方式优先级,返回优先支持的认证方式。 

checkSupport(context: Context,fidoRequest: FidoRequest, 

priorityPolicy:string,certStyle?: CertStyle, isBase64?: boolean): 

Promise<FidoResponse> 

前置条件:先调用服务端v2/device/support 接口,将响应报文作为接口入参 fidoRequest.data 字段的值。 

### 【请求参数】 

|名称|数据类型|必 填|描述|
|---|---|---|---|
|context|Context|是|应用上下文|
|protocol|FidoProtocol|否|协议: FidoProtocol.UAF_CERT :|
|FidoRequest|||FIDO1.0 FidoProtocol.CTAP:FIDO2.0 暂未实现|

||||默认:FidoProtocol.UAF_CERT|
|---|---|---|---|
|mode|FidoMode|否|Fido 实现方式: FidoMode.LOCAL 基于鸿蒙 HUKS 实现 默认:FidoMode.LOCAL|
|authTypes|Array<FidoAuthType>|否|认证方式:可多选 指纹:UAF_FINGER_CERT PIN:UAF_PIN_CERT TUI PIN:UAF_TUI_PIN_CERT(默 认)|
|data|string|是|服务端v2/device/support 接 口响应报文。支持完整报文,同 时兼容uafRequest 节点报文。|
|priorityPolicy|string|否|认证方式优先级,JSON 格式字 符串 默认TUI PIN 优先|
|certStyle|CertStyle|否|查询类型 SOLO:单个 GROUP:组 在鸿蒙上未使用,可选|
|isBase664|Boolean|否|报文是否为Base64 格式 true:是,false:否 可选,默认false|

### 【响应结果】 

||名称|数据类型|必填|描述|
|---|---|---|---|---|
|FidoRespons|code|FidoStatus|是|错误码枚举|

|e message|string|是|错误描述|
|---|---|---|---|
|data|HashMap<FidoAuthType,boolea n>|是|K: FidoAuthType: 指纹: UAF_FINGER 人脸:UAF_FACE [1] V:状态 true:支 持,false:不支 持|
|isFingerSupport():boolean|方法|是|判断是否支持 指纹认证方式|
|isPinSupport():boolean|方法|是|判断是否支持 PIN 认证方式|
|isTuiPinSupport(): boolean|方法|是|判断是否支持 TUI PIN 认证方 式|
|getAuthType():FidoAuthType|方法|是|返回认证方式|
|getLevel():number|方法|是|返回安全级别|
|getPinAuthType():FidoAuthT ype|方法|是|返回Pin 的认证 方式|
|getFpAuthType():FidoAuthTy pe|方法|是|返回指纹认证 方式|
|getTuiPinAuthType(): FidoAuthType|方法|是|返回TUI PIN 认 证方式|
|getFpLevel():number|方法|是|返回指纹安全 级别|
|getPinLevel():number|方法|是|返回Pin 安全级 别|
|getTuiPinLevel():number|方法|是|返回TUI PIN 安 全级别|

#### regCert 

证书注册。 

regCert(context:Context, fidoRequest: FidoRequest): Promise<FidoResponse> 

依赖:访问服务端接口uaf/reg/receive 

### 【请求参数】 

|名称|数据类型|必 填|描述|
|---|---|---|---|
|context|Context|是|应用上下文|
|protocol|FidoProtocol|否|协议: FidoProtocol.UAF_CERT :FIDO 证书 默认:FidoProtocol.UAF_CERT|
|mode|FidoMode|否|Fido 实现方式: FidoMode.LOCAL 基于鸿蒙HUKS 实现 默认:FidoMode.LOCAL|
|fidoRequest authTypes|Array<FidoAuthType>|
否|认证方式:多选一(1 个元素的
数组)
指纹:UAF_FINGER_CERT
PIN:UAF_PIN_CERT
TUI PIN:UAF_TUI_PIN_CERT
注:checkSupport 返回的
authType,或直接指定|
|data|string|是|请求报文 注:服务端/reg/receive 接口 响应报文uafRequest 节点内容|

|isBase664|Boolean|否|报文是否为Base64 格式|
|---|---|---|---|
||||true:是,false:否|
||||可选,默认false|

### 【响应结果】 

|名称|数据类型|必填|描述|
|---|---|---|---|
|code|FidoStatus|是|错误码枚举|
|FidoResponse message|string|是|错误描述|
|data|string|是|响应报文|

#### saveCert 

保存证书。 

saveCert(context:Context, fidoRequest: FidoRequest): Promise<FidoResponse> 

依赖:访问服务端接口uaf/reg/send 

### 【请求参数】 

|名称|数据类型|必 填|描述|
|---|---|---|---|
|context|Context|是|应用上下文|
|fidoRequest protocol|FidoProtocol|否|协议: FidoProtocol.UAF_CERT :FIDO 证书 默认:FidoProtocol.UAF_CERT|
|mode|FidoMode|否|Fido 实现方式:|

||||FidoMode.LOCAL 基于鸿蒙HUKS 实现 默认:FidoMode.LOCAL|
|---|---|---|---|
|authTypes|Array<FidoAuthType>|
否|认证方式:多选一(1 个元素的
数组)
指纹:UAF_FINGER_CERT
PIN:UAF_PIN_CERT
TUI PIN:UAF_TUI_PIN_CERT
注:checkSupport 返回的
authType,或直接指定|
|data|string|是|请求报文 注:服务端/reg/send 接口响应 报文uafRequest 节点内容|
|isBase664|Boolean|否|报文是否为Base64 格式 true:是,false:否 可选,默认false|

### 【响应结果】 

|名称|数据类型|必填|描述|
|---|---|---|---|
|code|FidoStatus|是|错误码枚举|
|FidoResponse message|string|是|错误描述|
|data|string|是|响应报文|

#### authCert 

##### 证书认证。 

authCert(context:Context, fidoRequest: FidoRequest): Promise<FidoResponse> 

##### 依赖:访问服务端接口uaf/auth/receive 

### 【请求参数】 

|名称|数据类型|必 填|描述|
|---|---|---|---|
|context|Context|是|应用上下文|
|protocol|FidoProtocol|否|协议: FidoProtocol.UAF_CERT :FIDO 证书 默认:FidoProtocol.UAF_CERT|
|mode|FidoMode|否|Fido 实现方式: FidoMode.LOCAL 基于鸿蒙HUKS 实现 默认:FidoMode.LOCAL|
|fidoRequest authTypes|Array<FidoAuthType>|
否|认证方式:多选一(1 个元素的
数组)
指纹:UAF_FINGER_CERT
PIN:UAF_PIN_CERT
TUI PIN:UAF_TUI_PIN_CERT
注:checkSupport 返回的
authType,或直接指定;亦或通
过服务端/cert/getinfo 接口,
获取authType 值|
|data|string|是|请求报文 注:服务端/auth/receive 接口 响应报文uafRequest 节点内容|
|isBase664|Boolean|否|报文是否为Base64 格式 true:是,false:否 可选,默认false|

### 【响应结果】 

|名称|数据类型|必填|描述|
|---|---|---|---|
|code|FidoStatus|是|错误码枚举|
|FidoResponse message|string|是|错误描述|
|data|string|是|响应报文|

#### updateCert 

证书更新。 

updateCert(context:Context, fidoRequest: FidoRequest): Promise<FidoResponse> 

依赖:访问服务端接口uaf/cert/update 

### 【请求参数】 

|名称|数据类型|必 填|描述|
|---|---|---|---|
|context|Context|是|应用上下文|
|protocol|FidoProtocol|否|协议: FidoProtocol.UAF_CERT :FIDO 证书 默认:FidoProtocol.UAF_CERT|
|fidoRequest mode|FidoMode|否|Fido 实现方式: FidoMode.LOCAL 基于鸿蒙HUKS 实现 默认:FidoMode.LOCAL|
|authTypes|Array<FidoAuthType>|
否|认证方式:多选一(1 个元素的
数组)
指纹:UAF_FINGER_CERT
PIN:UAF_PIN_CERT|

|||TUI PIN:UAF_TUI_PIN_CERT 注:checkSupport 返回的 authType,或直接指定;亦或通 过服务端/cert/getinfo 接口, 获取authType 值|
|---|---|---|
|data string|是|请求报文 注:服务端/cert/update 接口 响应报文uafRequest 节点内容|
|isBase664 Boolean|否|报文是否为Base64 格式 true:是,false:否 可选,默认false|

### 【响应结果】 

|名称|数据类型|必填|描述|
|---|---|---|---|
|code|FidoStatus|是|错误码枚举|
|FidoResponse message|string|是|错误描述|
|data|string|是|响应报文|

#### delCert 

##### 证书注销。 

delCert(context:Context, fidoRequest: FidoRequest): Promise<FidoResponse> 

依赖:访问服务端接口uaf/reg/delete 

### 【请求参数】 

|名称|数据类型|必 填|描述|
|---|---|---|---|
|context|Context|是|应用上下文|

|protocol|FidoProtocol|否|协议: FidoProtocol.UAF_CERT :FIDO 证书 默认:FidoProtocol.UAF_CERT|
|---|---|---|---|
|mode|FidoMode|否|Fido 实现方式: FidoMode.LOCAL 基于鸿蒙HUKS 实现 默认:FidoMode.LOCAL|
|fidoRequest authTypes|Array<FidoAuthType>|
否|认证方式:多选一(1 个元素的
数组)
指纹:UAF_FINGER_CERT
PIN:UAF_PIN_CERT
TUI PIN:UAF_TUI_PIN_CERT
注:checkSupport 返回的
authType,或直接指定;亦或通
过服务端/cert/getinfo 接口,
获取authType 值|
|data|string|是|请求报文 注:服务端/reg/delete 接口响 应报文uafRequest 节点内容|
|isBase664|Boolean|否|报文是否为Base64 格式 true:是,false:否 可选,默认false|

### 【响应结果】 

|名称|数据类型|必填|描述|
|---|---|---|---|
|code|FidoStatus|是|错误码枚举|
|FidoResponse message|string|是|错误描述|
|data|string|否||

#### setTUI 

设置PIN UI 页面,并将保存设置。软PIN 应用卸载重装后,设置内容丢失,需要重新 设置,TUI PIN 设置后,设置内容不会丢失。 

注意:如果使用TUI 功能,使用前必须调用该方法至少一次,因为TUI 无缺省图片 

setTUI(context:Context, fidoRequest: FidoRequest): Promise<FidoResponse> 

### 【请求参数】 

|名称|数据类型|必 填|描述|
|---|---|---|---|
|context|Context|是|应用上下文|
|protocol|enum|否|协议: 默认: FidoProtocol.UAF_CERT :FIDO 证书|
|fidoRequest authTypes|Array<FidoAuthType>|否|认证方式:多选一(1 个元素的 数组) PIN:UAF_PIN_CERT TUI PIN:UAF_TUI_PIN_CERT|
|data|string|是|JSON 格式配置项,详见附录PIN 配置项|

### 【响应结果】 

|名称 数据类型|必填 描述|
|---|---|

||code|FidoStatus|是|错误码枚举|
|---|---|---|---|---|
|FidoResponse|message|string|是|错误描述|
||data|string|否||

#### changePin 

修改PIN。 

changePin(context:Context, fidoRequest: FidoRequest): Promise<FidoResponse> 

依赖:访问服务端接口uaf/user/info 

### 【请求参数】 

|名称|数据类型|必 填|描述|
|---|---|---|---|
|context|Context|是|应用上下文|
|protocol|FidoProtocol|否|协议: FidoProtocol.UAF_CERT :FIDO 证书 默认:FidoProtocol.UAF_CERT|
|fidoRequest mode|FidoMode|否|Fido 实现方式: FidoMode.LOCAL 基于鸿蒙HUKS 实现 默认:FidoMode.LOCAL|
|authTypes|Array<FidoAuthType>|
否|认证方式:
PIN:UAF_CERT_PIN(默认)
TUI PIN:UAF_TUI_PIN_CERT|
|data|string|是|请求报文 注:服务端/user/info 接口响 应报文uafRequest 节点内容|

### 【响应结果】 

|名称|数据类型|必填|描述|
|---|---|---|---|
|code|FidoStatus|是|错误码枚举|
|FidoResponse message|string|是|错误描述|
|data|string|否||

#### clearLoseRegs 

清除设备中当前用户、同渠道、同APP ID 下注册的冗余(服务端没有,本地有)记录 信息。 

clearLoseRegs(context: Context, fidoRequest: FidoRequest): Promise<FidoResponse>; 

依赖:访问服务端接口/uaf/user/allinfo 

### 【请求参数】 

|名称|数据类型|必 填|描述|
|---|---|---|---|
|context|Context|是|应用上下文|
|protocol|enum|否|协议: 默认: FidoProtocol.UAF_CERT :FIDO 证书|
|fidoRequest mode|enum|否|Fido 实现方式: FidoMode.LOCAL 基于鸿蒙HUKS 实现 默认:FidoMode.LOCAL|
|authTypes|Array<FidoAuthType>|
否|认证方式:多选一(1 个元素的
数组)
指纹:UAF_CERT_FINGER(默认)
PIN:UAF_PIN_CERT|

|||TUI PIN:UAF_TUI_PIN_CERT 注: checkSupport 返回的 authType,或直接指定;亦或通 过服务端/cert/getinfo 接口, 获取authType 值|
|---|---|---|
|data string|是|通过调用服务端接口 /uaf/user/allinfo 接口获取|

### 【响应结果】 

|名称|数据类型|必填|描述|
|---|---|---|---|
|code|FidoStatus|是|错误码枚举|
|FidoResponse message|string|是|错误描述|
|data||否||

#### deviceReset 

设备重置,清除客户端所有注册记录 deviceReset(context: Context, fidoRequest: FidoRequest): Promise<FidoResponse> 

依赖:访问服务端接口/uaf/devcie/info 接口获取请求报文 

### 【请求参数】 

|名称|数据类型|必 填|描述|
|---|---|---|---|
|context|Context|是|应用上下文|
|protocol|enum|否|协议: 默认:|
|fidoRequest|||FidoProtocol.UAF_CERT :FIDO 证书|
|mode|enum|否|Fido 实现方式:|

||||FidoMode.LOCAL 基于鸿蒙HUKS 实现 默认:FidoMode.LOCAL|
|---|---|---|---|
|authTypes|Array<FidoAuthType>|
否|认证方式:(1 个元素的数组)
指纹:UAF_FINGER_CERT
PIN:UAF_PIN_CERT
TUI PIN:UAF_TUI_PIN_CERT
注:checkSupport 返回的
authType,或直接指定;亦或通
过服务端/cert/getinfo 接口,
获取authType 值|
|data|string|是|通过调用服务端接口 /uaf/device/info 接口获取 注:checkSupport 返回的 authType,或直接指定;亦或通 过服务端/cert/getinfo 接口, 获取authType 值|

### 【响应结果】 

|名称|数据类型|必填|描述|
|---|---|---|---|
|code|FidoStatus|是|错误码枚举|
|FidoResponse message|string|是|错误描述|
|data||否||

### FidoCertProSdkUtil 

#### getSdkVersion 

获取SDK 版本 getSdkVersion(): string 

### 【请求参数】 

### 无。 

### 【响应结果】 

|名称|数据类型|必填|描述|
|---|---|---|---|
|无|string|是|SDK 版本|

#### subscribeLogger 

##### SDK 日志订阅接口。 

subscribeLogger(context: Context, callback: Function): Promise<void>; 

### 【请求参数】 

|名称|数据类型|必填|描述|
|---|---|---|---|
|context|Context|是|上下文|
|callback|Function|是|日志回调函数,返回JSON 格式日志|

### 【响应参数】 

|名称|数据类型|必填|描述|
|---|---|---|---|
|domain_|string|是|事件域,固定值:GM_OH_FIDO_CERT|
|name_|string|是|事件类型; DEFAULT:默认 UAF_CERT_PROCESS:process 接口调用 UAF_CERT_REG:注册操作 UAF_CERT_AUTH:认证操作 UAF_CERT_DE_REG:注销操作 UAF_CERT_UPDATE:证书更新 UAF_CERT_QUERY:证书查询 EVENT_STORE_CERT_AGAIN:证书重新下 载 EVENT_CERT_CLEAR:冗余清除操作 CHECK_NET_SUPPORT:checkNetSuppor 接口调用 CHECK_SUPPORT:checkSupport 接口调 用 GET_DEVICE_ID:getDeviceID 接口调用 GET_DEVICE_INFO:getDeviceInfo 接口 调用 GET_SDK_VERSION:getSdkVersion 接口 调用 IS_ENROLLED:isEnrolled 接口调用|
|type_|number|是|1 错误事件 4 用户操作|
|time_|number|是|时间戳|
|tz_|string|是|时区|
|pid_|number|是|进程ID|
|tid_|number|是|线程ID|
|time|string|是|格式化时间:yyyy/MM/dd HH:mm:ss:sss|

|level|string|是|DEBUG、INFO、WARN、ERROR|
|---|---|---|---|
|message|string|是|日志内容|
|tag|String|是|自定义TAG|
|deviceInfo|String|是|设备信息,包含sdk 版本信息|

#### unsubscribeLogger 

取消SDK 日志订阅。 unSubscribeLogger(): void; 

### 【请求参数】 

无。 

### 【响应参数】 

##### 无。 

#### getFacetId 

获取facetID。 getFacetId(): Promise<string> 

### 【请求参数】 

### 无。 

### 【响应结果】 

|名称|数据类型|必填||描述|
|---|---|---|---|---|
|无|string|是|facetID||

#### isEnrolled 

查询设备是否已经录入生物特征。 

isEnrolled(authTypes:Array<FidoAuthType>): FidoResponse 

### 【请求参数】 

|名称|数据类型|必填|描述|
|---|---|---|---|
|authTypes|Array<FidoAuthType>|否|认证方式:可多选|
||||指纹:UAF_CERT_FINGER|

### 【响应结果】 

||名称|数据类型|必填|描述|
|---|---|---|---|---|
||code|FidoStatus|是|错误码枚举|
||message|string|是|错误描述|
|FidoResponse|data|HashMap<FidoAuthT ype,number>|是|K:FidoAuthType: 指纹: UAF_CERT_FINGER V:状态: 0:已录入生物特征 5:不支持的认证方 式 201:未录入生物特 征 204:无权限 255:其他内部错误|
||getFingerEnrollState(): number|方法|是|获取指纹是否录入 状态|

#### startBioSetting 

##### 开启指纹录入引导页面。 

static startBioSetting(context: common.UIAbilityContext) 

### 【请求参数】 

|名称|数据类型|必填|描述|
|---|---|---|---|
|context|Context|是||

### 【响应结果】 

### 无。 

#### generateCheckSupportMsg 

构建/uaf/v2/device/support 接口报文,用于设备支持检测。 static generateCheckSupportMsg(deviceID: string):string 

### 【请求参数】 

|名称|数据类型|必填|描述|
|---|---|---|---|
|deviceID|string|是|设备ID|

### 【响应结果】 

### string 类型JSON 格式报文 

#### generateRegReceiveMsg 

构建/uaf/reg/receive 接口报文,用于注册发起 

static generateRegReceiveMsg(username: string, authType: FidoAuthType,dn: string, 

deviceID: string): string 

### 【请求参数】 

|名称 数据类型|必填 描述|
|---|---|

|username|string|是|用户标识|
|---|---|---|---|
|authType|FidoAuthType|是|认证方式 指纹:UAF_FINGER_CERT PIN:UAF_PIN_CERT|
||||TUI PIN:UAF_TUI_PIN_CERT|
|dn|string|是|证书主体标识|
|deviceID|string|是|设备ID|

### 【响应结果】 

### string 类型JSON 格式报文 

#### generateRegSendMsg 

构建/uaf/reg/send 接口报文,用于注册完成确认。 static generateRegSendMsg(sdkResponse: string, username: string, authType: FidoAuthType,deviceID:string): string 

### 【请求参数】 

|名称|数据类型|必填|描述|
|---|---|---|---|
|sdkResponse|String|是|sdk regCert 接口返回的 fidoResponse.data 的值|
|username|string|是|用户标识|
|authType|FidoAuthType|是|认证方式 指纹:UAF_FINGER_CERT PIN:UAF_PIN_CERT TUI PIN:UAF_TUI_PIN_CERT|
|deviceID|string|是|设备ID|

### 【响应结果】 

### string 类型JSON 格式报文 

#### generateUpdateStatusMsg 

构建/uaf/cert/updatestatus 请求报文,用于保存证书(saveCert)完成后更新证书状 态。 

static generateUpdateStatusMsg(sdkResponse: string, username: string): string 

### 【请求参数】 

|名称|数据类型|必填|描述|
|---|---|---|---|
|sdkResponse|string|是|sdk saveCert 接口返回报文 fidoResponse.data 值|
|username|string|是|用户标识|

### 【响应结果】 

### string 类型JSON 格式报文 

#### generateRegDeleteMsg 

构建/uaf/reg/delete 请求报文,用于单个设备注销。 

static generateRegDeleteMsg(username: string, authType: FidoAuthType, deviceID: string): string 

### 【请求参数】 

|名称|数据类型|必填|描述|
|---|---|---|---|
|username|string|是|用户标识|
|authType|FidoAuthType|是|认证方式 指纹:UAF_FINGER_CERT PIN:UAF_PIN_CERT TUI PIN:UAF_TUI_PIN_CERT|

|deviceID|string|是 设备ID|
|---|---|---|

### 【响应结果】 

### string 类型JSON 格式报文 

#### generateRegDeleteAllMsg 

构建/uaf/reg/deleteall 请求报文,用于多个设备注销。 static 

generateRegDeleteAllMsg(username:string,deviceID:string,authTypes?:FidoAuth Type[]):string 

### 【请求参数】 

|名称|数据类型|必填|描述|
|---|---|---|---|
|username|string|是|用户标识|
|deviceID|string|是|设备ID|
|authTypes|FidoAuthType[]|否|认证方式 指纹:UAF_FINGER_CERT PIN:UAF_PIN_CERT TUI PIN:UAF_TUI_PIN_CERT|

### 【响应结果】 

### string 类型JSON 格式报文 

#### generateClearLostRegMsg 

构建/uaf/user/allinfo 请求报文,用于冗余清除。 

static generateClearLostRegMsg(username: string, deviceID: string):string 

### 【请求参数】 

|名称|数据类型|必填||描述|
|---|---|---|---|---|
|username|string|是|用户标识||
|deviceID|string|是|设备ID||

### 【响应结果】 

### string 类型JSON 格式报文 

#### generateUpdateCertMsg 

构建/uaf/cert/update 请求报文,用于证书更新。 

static generateUpdateCertMsg(sdkResponse:string,username:string,authType: FidoAuthType,deviceID: string, authExt: string, dn: string): string 

### 【请求参数】 

|名称|数据类型|必填|描述|
|---|---|---|---|
|sdkResponse|string|是|第一次请求传空字符串 第二次请求 sdk authCert 接口返回报文 fidoResponse.data 值 第三次请求 sdk regCert 接口返回报文 fidoResponse.data 值|
|username|string|是|用户标识|
|authType|FidoAuthType|是|认证方式 指纹:UAF_FINGER_CERT|

||||PIN:UAF_PIN_CERT TUI PIN:UAF_TUI_PIN_CERT|
|---|---|---|---|
|deviceID|string|是|设备ID|
|authExt|string|是|证书更新提示性文字 明文内容格式: { "showFlag": "01", "showText": " 提示性文字" } 参数格式: Base64URL(JSON.stringify(明文内 容))|
|dn|string|是|证书主体标识|

### 【响应结果】 

### string 类型JSON 格式报文 

#### generateGetUserInfoMsg 

构建/uaf/user/info 接口报文,用于修改PIN。 static generateGetUserInfoMsg(username: string, authType: FidoAuthType, deviceID: string):string 

### 【请求参数】 

|名称|数据类型|必填|描述|
|---|---|---|---|
|username|string|是|用户标识|
|authType|FidoAuthType|是|认证方式 指纹:UAF_FINGER_CERT PIN:UAF_PIN_CERT|
||||TUI PIN:UAF_TUI_PIN_CERT|
|deviceID|string|是|设备ID|

### 【响应结果】 

### string 类型JSON 格式报文 

#### generateDeviceInfoMsg 

构建/uaf/device/info 请求报文,用于设备重置。 

static generateDeviceInfoMsg(deviceID: string): string 

### 【请求参数】 

|名称|数据类型|必填|描述|
|---|---|---|---|
|deviceID|string|是|设备ID|

### 【响应结果】 

### string 类型JSON 格式报文
