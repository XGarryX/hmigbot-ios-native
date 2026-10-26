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

#### **四、开发步骤** 

1. 需要业务方自行根据标准协议部署服务端、证书服务器等基础设施。 

###### 2. 导入SDK 

|import {|
|---|
|FidoAuthType, FidoCertProSdkUtil, FidoCertSdk,|
|FidoRequest,|
|FidoResponse,|
|FidoStatus,|
|getAuthType,|
|IFidoCertSdk } from '@gmrz/fido_cert_sdk';|

###### 3. 获取设备信息(可选) 

###### 实施方可调用该接口获取设备信息,也可自行获取设备信息,用于服务端接口请求报文的填充。 

this.fidoSdk.getDeviceInfo().then(response=>{ 

```arkts
let deviceInfo = JSON.parse(response.data as string) as DeviceInfo promptAction.showToast({ message: '设备信息:' + JSON.stringify(deviceInfo), duration: 5000 }) console.log("deviceInfo::",JSON.stringify(deviceInfo)); }).then(e:Error)=>{ promptAction.showToast({ message: '获取设备信息失败:' + e.message, duration: 5000 }) }) 
```

###### 4、检查设备是否支持 

async checkNetSupport(): Promise<FidoResponse> { 

let checkNetSupportData = FidoCertProSdkUtil.generateCheckSupportMsg(this.deviceId) 

// server 查询设备支持的认证类型(server) 

let response = await httpPost(this.baseUrl + "/uaf/v2/device/support", checkNetSupportData) 

```arkts
let serverResponse: UAFServerResponse = this.checkServerResponse(response.result as string); let fidoRequest: FidoRequest = { data: serverResponse.uafRequest } //sdk 查询设备支持的认证类型(client and server) 
let fidoResponse = await this.fidoSdk.checkNetSupport(getContext(this), fidoRequest); return fidoResponse; } 
```

###### 5、开通证书 

async register(): Promise<FidoResponse> { 

//生成注册发起报文 let regReceiveRequest = 

FidoCertProSdkUtil.generateRegReceiveMsg(this.userName, this.authType, this.dn, this.deviceId); //调用server 注册发起接口 

let response = await httpPost(this.baseUrl + "/uaf/reg/receive", regReceiveRequest); 

    let serverResponse: UAFServerResponse = this.checkServerResponse(response.result as string);
    let fidoAuthType: FidoAuthType = getAuthType(this.authType) as FidoAuthType
    let fidoRequest: FidoRequest = {
      data: serverResponse.uafRequest,
      authTypes: [fidoAuthType]
    }
    //调用sdk 注册接口
    let fidoResponse: FidoResponse = await this.fidoSdk.process(getContext(this), fidoRequest);
    if (fidoResponse.code == FidoStatus.SUCCESS) {
      let regCertSendRequest =
        FidoCertProSdkUtil.generateRegSendMsg(fidoResponse.data  as  string,  this.userName,  this.authType,
undefined,
          this.deviceId);
      //调用 server 注册完成接口
      response = await httpPost(this.baseUrl + "/uaf/reg/send", regCertSendRequest)
      serverResponse = this.checkServerResponse(response.result as string);
      fidoRequest.data = serverResponse.uafRequest;
      //保存证书
      fidoResponse = await this.fidoSdk.process(getContext(this), fidoRequest);
      if (fidoResponse.code == FidoStatus.SUCCESS) {
        let certUpdateStatusData =
          FidoCertProSdkUtil.generateUpdateStatusMsg(fidoResponse.data as string, this.userName);
        //server 更新证书状态
        let response = await httpPost(this.baseUrl + "/uaf/cert/updatestatus", certUpdateStatusData)
        serverResponse = this.checkServerResponse(response.result as string);
      }
    }
    return fidoResponse;
  }

###### 6、证书认证 

```arkts
async authenticate(electric?:boolean): Promise<FidoResponse> { let transactionText: AuthExt = electric? {"showFlag": "01","showText": " 电 子 签 章 操 作 中 ","esFlag": "01","esHash": "nrC6PyB4JTzHD6I+MO4n/LIU0wFYCouMzBNFk6HuE/U="} : { "showFlag": "01", "showText": this.transactionText }; let ext = buffer.from(JSON.stringify(transactionText)).toString("base64url"); let authCertReceiveData = FidoCertProSdkUtil.generateAuthReceiveMsg(this.userName, this.authType, ext, this.deviceId); 
// server 认证发起接口 
let response = await httpPost(this.baseUrl + "/uaf/auth/receive", authCertReceiveData); let serverResponse: UAFServerResponse = this.checkServerResponse(response.result as string); let fidoRequest: FidoRequest = { data: serverResponse.uafRequest, } //sdk 认证 let fidoResponse = await this.fidoSdk.process(getContext(this), fidoRequest); if (fidoResponse.code == FidoStatus.SUCCESS) { let authCertSendData = FidoCertProSdkUtil.generateAuthSendMsg(fidoResponse.data as string, this.userName, this.authType, this.deviceId); //server 认证完成接口 response = await httpPost(this.baseUrl + "/uaf/auth/send", authCertSendData) this.checkServerResponse(response.result as string); } return fidoResponse; } 
```

###### 7、注销证书 

async deRegister(): Promise<FidoResponse> { 

// server 注销单个设备 

let certDeregData 

- =  FidoCertProSdkUtil.generateRegDeleteMsg(this.userName,this.authType,this.deviceId); // let response = await httpPost(this.baseUrl + "/uaf/reg/delete", certDeregData) 

//server 注销多个设备接口 

```arkts
let certDeregData = FidoCertProSdkUtil.generateRegDeleteAllMsg(this.userName, this.deviceId); let response = await httpPost(this.baseUrl + "/uaf/reg/deleteall", certDeregData) let serverResponse: UAFServerResponse = this.checkServerResponse(response.result as string); let fidoRequest: FidoRequest = { data: serverResponse.uafRequest } return await this.fidoSdk.process(getContext(this), fidoRequest); } 
```

###### 8、证书查询 

```arkts
async getCert(flag:number): Promise<FidoResponse> { let fidoRequest:FidoRequest = {} if(flag==0){ let userInfoQueryData = FidoCertProSdkUtil.generateGetUserInfoMsg(this.userName, this.authType, 
this.deviceId); //server 查询用户注册信息接口 let response = await httpPost(this.baseUrl + "/uaf/user/info", userInfoQueryData); let serverResponse: UAFServerResponse = this.checkServerResponse(response.result as string); fidoRequest = { data: serverResponse.uafRequest, deviceId: this.deviceId } }else{ //兼容 /cert/getinfo 接口 let getCertInfoData = FidoCertProSdkUtil.generateGetCertInfoMsg(this.userName,this.deviceId); //server 查询用户注册信息接口 
let response = await httpPost(this.baseUrl + "/uaf/cert/getinfo", getCertInfoData); 
let serverResponse: UAFServerResponse = this.checkServerResponse(response.result as string); fidoRequest = { data: JSON.stringify(serverResponse.uafRequest), deviceId: this.deviceId } } //sdk 查询证书接口 
```

let fidoResponse = await this.fidoSdk.getCert(getContext(this), fidoRequest); 

console.log("证书状态:", fidoResponse.getCertStatus()) 

console.log("认证方式:", fidoResponse.getAuthType()) 

console.log("安全级别:", fidoResponse.getSecurityLevel()) 

console.log("证书内容", fidoResponse.data) return fidoResponse; 

} 

###### 9、证书重新下载 

async storeCertAgain(): Promise<FidoResponse> { 

if (this.authType == FidoAuthType.UAF_TUI_PIN_CERT) { 

return FidoResponse.wrap(-1, "TUI PIN 不支持证书重新下载", null); 

} 

//needCert 01 下载证书 02 证书延期 

let userInfoQueryData = 

FidoCertProSdkUtil.generateGetUserInfoMsg(this.userName, this.authType, this.deviceId, this.needCert); 

//server 查询用户注册信息接口 

let response = await httpPost(this.baseUrl + "/uaf/user/info", userInfoQueryData); 

let serverResponse: UAFServerResponse = this.checkServerResponse(response.result as string); let fidoRequest: FidoRequest = { 

data: serverResponse.uafRequest 

} 

//sdk 查询证书接口 

let fidoResponse = await this.fidoSdk.storeCertAgain(getContext(this), fidoRequest); 

console.log("证书状态:", fidoResponse.getCertStatus()) 

console.log("认证方式:", fidoResponse.getAuthType()) 

console.log("安全级别:", fidoResponse.getSecurityLevel()) 

console.log("证书内容", fidoResponse.data) 

return fidoResponse; 

} 

###### 10、证书更新 

async updateCert(): Promise<FidoResponse> { 

```arkts
let authExt: AuthExt = { "showFlag": "01", "showText": "确认注销并更新当前数字证书?" }; 
```

let authExtB64 = buffer.from(JSON.stringify(authExt)).toString("base64url"); 

let updateCertData = 

FidoCertProSdkUtil.generateUpdateCertMsg("", this.userName, this.authType, this.deviceId, authExtB64, 

this.dn) //第一次传空字符串 

//server 更新证书接口(1st) 

let response = await httpPost(this.baseUrl + "/uaf/cert/update", updateCertData); 

let serverResponse: UAFServerResponse = this.checkServerResponse(response.result as string); 

let fidoRequest: FidoRequest = { 

data: serverResponse.uafRequest, 

authTypes: [this.authType] 

} 

//sdk 认证 

let fidoResponse = await this.fidoSdk.process(getContext(this), fidoRequest); 

if (fidoResponse.code == FidoStatus.SUCCESS) { 

updateCertData = 

FidoCertProSdkUtil.generateUpdateCertMsg(fidoResponse.data as string, this.userName, this.authType, this.deviceId, authExtB64, 

this.dn); 

//server 更新证书接口(2nd) 

response = await httpPost(this.baseUrl + "/uaf/cert/update", updateCertData); 

serverResponse = this.checkServerResponse(response.result as string); 

fidoRequest.data = serverResponse.uafRequest; 

//sdk 注册 

fidoResponse = await this.fidoSdk.process(getContext(this), fidoRequest); 

if (fidoResponse.code == FidoStatus.SUCCESS) { 

updateCertData = 

FidoCertProSdkUtil.generateUpdateCertMsg(fidoResponse.data as string, this.userName, this.authType, this.deviceId, 

authExtB64, this.dn); 

//server 更新证书接口(3rd) 

response = await httpPost(this.baseUrl + "/uaf/cert/update", updateCertData); serverResponse = this.checkServerResponse(response.result as string); fidoRequest.data = serverResponse.uafRequest; 

//sdk 更新证书 

fidoResponse = await this.fidoSdk.process(getContext(this), fidoRequest); 

} 

} 

###### return fidoResponse; 

} 

###### 11、电子签章 

###### 同认证。但是电子签章的请求报文不同 

###### 12、冗余清除 

async clearCert(): Promise<FidoResponse> { 

let allInfoReqData = FidoCertProSdkUtil.generateClearLostRegMsg(this.userName, this.deviceId,this.rf1); //server 用户信息查询 

let response = await httpPost(this.baseUrl + "/uaf/user/allinfo", allInfoReqData); 

let serverResponse: UAFServerResponse = this.checkServerResponse(response.result as string); let fidoRequest: FidoRequest = { data: serverResponse.uafRequest, 

} 

//sdk 清除冗余 

return await this.fidoSdk.clearCert(getContext(this), fidoRequest); 

} 

###### 13、重置 

async reset(): Promise<FidoResponse> { 

let deviceInfo = FidoCertProSdkUtil.generateDeviceInfoMsg(this.deviceId); 

//server 获取指定渠道的appID 信息 

let response = await httpPost(this.baseUrl + "/uaf/device/info", deviceInfo); 

```arkts
let serverResponse: UAFServerResponse = this.checkServerResponse(response.result as string); let fidoRequest: FidoRequest = { data: serverResponse.uafRequest, } //sdk 清除冗余 return await this.fidoSdk.reset(getContext(this), fidoRequest); } 
```

###### 14、修改PIN 码 

async changePin(): Promise<FidoResponse> { 

let userInfoQueryData = FidoCertProSdkUtil.generateGetUserInfoMsg(this.userName, this.authType, 

this.deviceId); 

//用户信息查询 

let response = await httpPost(this.baseUrl + "/uaf/user/info", userInfoQueryData); 

let serverResponse: UAFServerResponse = this.checkServerResponse(response.result as string); 

let fidoRequest: FidoRequest = { 

data: serverResponse.uafRequest, 

} 

//sdk 修改PIN 

return await this.fidoSdk.changePin(getContext(this), fidoRequest); 

} 

#### **五、报文样例** 

###### 1. 服务端注册请求报文样例(uaf/reg/receive) 

{ 

"context": { 

"appID": "1121", 

"opType": "00", 

"transNo": "transNoUacLocation", 

"userName": "ctk", 

"deviceID": "qr/CU6ZY+r7jPihO5SzhsIuOjp77s8kAOktKvk9qVgCFJsawRslIXoo40P5iVU8D", 

"transType": "02", 

"authType": "20", 

"dn": "eyJjYXJkTk8iOiIxMTEyMjIxOTk5MDkxMDM1MTkiLCJjYXJkVHlwZSI6IjAiLCJjYXJkTmFtZSI6ImN0ayJ9", "devices": { 

"deviceID": "qr/CU6ZY+r7jPihO5SzhsIuOjp77s8kAOktKvk9qVgCFJsawRslIXoo40P5iVU8D", 

deviceName": "NOH-AN00", 

"deviceAliasName": "HUAWEI Mate 40 Pro", 

"deviceType": "HUAWEI", 

"osVersion": 11, 

“sdkVersion”:0.1.2 

"osType": "HarmonyOS", 

"deviceisRoot": false, 

"deviceVersion": "LIO-AL00 4.0.0.116(SP10C00E116R5P4)" 

} 

} 

} 

###### 2. 服务端注册完成请求报文样例(uaf/reg/send) 

{ 

"uafResponse": "SDK 注册响应报文", "context": { "appID": "1121", "opType": "00", "transNo": "transNoUacLocation", "userName": "ctk", "transType": "02", "authType": "20", "mobile": "16604469499", "devices": { 

"deviceID": "qr/CU6ZY+r7jPihO5SzhsIuOjp77s8kAOktKvk9qVgCFJsawRslIXoo40P5iVU8D", deviceName": "NOH-AN00", 

"deviceAliasName": "HUAWEI Mate 40 Pro", 

"deviceType": "HUAWEI", "osVersion": 11, 

“sdkVersion”:0.1.2 

"osType": "HarmonyOS", 

"deviceisRoot": false, 

"deviceVersion": "LIO-AL00 4.0.0.116(SP10C00E116R5P4)" 

} 

} 

} 

###### 3. 服务端认证请求报文样例 (uaf/auth/receive) 

{ 

"context": { 

"userName": "ctk", "appID": "1121", 

"transNo": "transNoUacLocation", "transType": "02", "authType": [ 

"20" ], "ext": 

"eyJzaG93RmxhZyI6IjAxIiwic2hvd1RleHQiOiLot6jooYzovazotKYo5a6e5pe2KeS6pOaYk-WuoeaguCvCpTAuMDIifQ", "devices": { 

"deviceID": "qr/CU6ZY+r7jPihO5SzhsIuOjp77s8kAOktKvk9qVgCFJsawRslIXoo40P5iVU8D", 

"deviceName": "NOH-AN00", 

"deviceAliasName": "HUAWEI Mate 40 Pro", 

"deviceType": "HUAWEI", "osVersion": 11, 

“sdkVersion”:0.1.2 "osType": "HarmonyOS", "deviceisRoot": false, 

"deviceVersion": "LIO-AL00 4.0.0.116(SP10C00E116R5P4)" 

}, 

"transactionText": 

"6L2s6LSm6YeR6aKdMTAwLjAw5pS25qy-5Lq65byg5LiJ5pS25qy-6LSm5oi3NjIxNDY2NjY2NjY2NjY2NuS7mOasvui0p uaIt-aUtuasvui0puaItzYyMTQ2NjY2NjY2NjY2NjY" 

} 

} 

###### 4. 服务端认证完成请求报文样例(uaf/auth/send) 

{ 

"uafResponse": "SDK 认证响应报文", "context": { "userName": "ctk", "appID": "1121", "transNo": "transNoUacLocation", "transType": "02", "authType": [ "20" ], "devices": { 

"deviceID": "qr/CU6ZY+r7jPihO5SzhsIuOjp77s8kAOktKvk9qVgCFJsawRslIXoo40P5iVU8D", deviceName": "NOH-AN00", "deviceAliasName": "HUAWEI Mate 40 Pro", "deviceType": "HUAWEI", "osVersion": 11, “sdkVersion”:0.1.2 "osType": "HarmonyOS", "deviceisRoot": false, "deviceVersion": "LIO-AL00 4.0.0.116(SP10C00E116R5P4)" }, } } 

###### 5. 服务端注销请求报文样例 (uaf/reg/delete) 

{ 

"context": { "userName": "ctk", "appID": "1121", "transNo": "transNoUacLocation", "transType": "02", "authType": "20", 

"deviceID": "qr/CU6ZY+r7jPihO5SzhsIuOjp77s8kAOktKvk9qVgCFJsawRslIXoo40P5iVU8D", "from": "00" 

} 

} 

###### 6. 查询用户信息请求报文(uaf/user/info) 

{ 

"context": { 

"authType": ["20"], "transType": ["02"], "transNo": "transNoUacLocation", "appID": "1106", 

"deviceID": "qr/CU6ZY+r7jPihO5SzhsIuOjp77s8kAOktKvk9qVgCFJsawRslIXoo40P5iVU8D", "userName": "ctk", "ext":{"needCert":"01"} 

} 

} 

###### 7. 查询用户所有信息请求报文(uaf/user/allinfo) 

{ 

"context": { 

"transNo": "transNoUacLocation", "appID": "1106", "deviceID": "qr/CU6ZY+r7jPihO5SzhsIuOjp77s8kAOktKvk9qVgCFJsawRslIXoo40P5iVU8D", "userName": "ctk" 

} 

} 

###### 8. 更新证书状态请求报文(uaf/cert/updatestatus) 

{ 

"context": { "userName": "ctk", "appID": "1106", "transNo": "transNoUacLocation", "keyID": "证书保存返回keyID" }, "uafResponse": "证书保存响应报文" 

} 

###### 9. 证书更新第一次请求报文(uaf/cert/update) 

{ 

"context": { 

"userName": "ctk", "appID": "1106", 

"transNo": "transNoUacLocation", 

"transType": "02", 

"authType": "20", 

"devices": { 

"deviceID": "qr/CU6ZY+r7jPihO5SzhsIuOjp77s8kAOktKvk9qVgCFJsawRslIXoo40P5iVU8D", "deviceName": "PMT-AN70", 

"deviceAliasName": "HNPMT7", 

"deviceType": "HONOR", 

"osVersion": 29, 

"osType": "android", 

"deviceisRoot": false, 

"deviceVersion": "PMT-AN70 2.1.0.125(C00E173R7P4log)" 

}, 

"authExt": 

"eyJzaG93RmxhZyI6IjAxIiwic2hvd1RleHQiOiLmlbDlrZfor4Hkuabmm7TmlrBcbuehruiupOazqOmUgOW9k-WJjeaVsO Wtl-ivgeS5pj9cbiJ9", 

"regExt": "eyJjYXJkTk8iOiIxMTEyMjIxOTk5MDkxMDM1MTkiLCJjYXJkVHlwZSI6IjAiLCJjYXJkTmFtZSI6ImN0ayJ9", "dn": "eyJjYXJkTk8iOiIxMTEyMjIxOTk5MDkxMDM1MTkiLCJjYXJkVHlwZSI6IjAiLCJjYXJkTmFtZSI6ImN0ayJ9" } 

} 

###### 10. 证书更新第二次请求报文 (uaf/cert/update) 

{ 

"context": { 

"userName": "ctk", 

"appID": "1106", 

"transNo": "transNoUacLocation", 

"transType": "02", "authType": "20", 

"devices": { 

"deviceID": "qr/CU6ZY+r7jPihO5SzhsIuOjp77s8kAOktKvk9qVgCFJsawRslIXoo40P5iVU8D", "deviceName": "PMT-AN70", "deviceAliasName": "HNPMT7", "deviceType": "HONOR", 

"osVersion": 29, 

"osType": "android", 

"deviceisRoot": false, 

"deviceVersion": "PMT-AN70 2.1.0.125(C00E173R7P4log)" 

}, 

"authExt": 

"eyJzaG93RmxhZyI6IjAxIiwic2hvd1RleHQiOiLmlbDlrZfor4Hkuabmm7TmlrBcbuehruiupOazqOmUgOW9k-WJjeaVsO Wtl-ivgeS5pj9cbiJ9", 

"regExt": "eyJjYXJkTk8iOiIxMTEyMjIxOTk5MDkxMDM1MTkiLCJjYXJkVHlwZSI6IjAiLCJjYXJkTmFtZSI6ImN0ayJ9", 

"dn": "eyJjYXJkTk8iOiIxMTEyMjIxOTk5MDkxMDM1MTkiLCJjYXJkVHlwZSI6IjAiLCJjYXJkTmFtZSI6ImN0ayJ9" 

}, 

"uafResponse": "SDK 认证返回报文" 

} 

###### 11. 证书更新第三次请求报文 (uaf/cert/update) 

{ 

"context": { 

"userName": "ctk", 

"appID": "1106", 

"transNo": "transNoUacLocation", 

"transType": "02", 

"authType": "20", 

"devices": { 

"deviceID": "qr/CU6ZY+r7jPihO5SzhsIuOjp77s8kAOktKvk9qVgCFJsawRslIXoo40P5iVU8D", 

"deviceName": "PMT-AN70", 

"deviceAliasName": "HNPMT7", 

"deviceType": "HONOR", "osVersion": 29, 

"osType": "android", 

"deviceisRoot": false, 

"deviceVersion": "PMT-AN70 2.1.0.125(C00E173R7P4log)" 

}, "authExt": 

"eyJzaG93RmxhZyI6IjAxIiwic2hvd1RleHQiOiLmlbDlrZfor4Hkuabmm7TmlrBcbuehruiupOazqOmUgOW9k-WJjeaVsO Wtl-ivgeS5pj9cbiJ9", 

"regExt": "eyJjYXJkTk8iOiIxMTEyMjIxOTk5MDkxMDM1MTkiLCJjYXJkVHlwZSI6IjAiLCJjYXJkTmFtZSI6ImN0ayJ9", "dn": "eyJjYXJkTk8iOiIxMTEyMjIxOTk5MDkxMDM1MTkiLCJjYXJkVHlwZSI6IjAiLCJjYXJkTmFtZSI6ImN0ayJ9" }, 

"uafResponse": "SDK 注册返回报文" 

} 

|**六、错误码** 错误码|描述信息|说明信息|
|---|---|---|
|0|NO_ERROR|操作成功 |
|3|CANCELLED|用户取消操作|
|4|TRANSACTION_TEXT_COMPARE_FAILED|交易报文比对失败 |
|5|NO_SUITABLE_AUTHENTICATOR|未找到认证器描述, 原因可能是服务端配 置不正确导致。|
|6|PROTOCOL_ERROR|协议错误,一般为报 文参数校验问题。|
|11|TRANSACTION_TEXT_LENGTH_INVALID|交易报文长度错误|
|63|CHECK_STATUS_FAILED|查询证书失败,本地 无证书|
|117|CERT_GET_FAILED|认证时,获取证书失 败|
|129|CERT_STORE_OVER_LIMIT|注册记录超过20 上 限|
|198|OVER_ATTEMPT_LIMIT|锁定|
|200|TIME_OUT|软PIN 认证超时|
|201|NOT_ENROLLED|未录入生物特征信息|
|202|KEY_INVALID_PERMANENTLY|注册后生物特征信息 发生了变化导致认证 失败|
|204|NO_PERMISSION|权限问题|
|131|CERT_STATUS_ERR_VERIFY_PIN|软PIN 认证pin 错误|
|151|CERT_PIN_CANCELLED|软PIN 取消|
|154|CERT_PIN_LOCKED|软(TUI)PIN 锁定|
|155|INVALID_PIN_LEN|软PIN 长度非法|
|156|INVALID_PIN_NOT_MATCH|软PIN 不匹配|
|157|INVALID_PIN_COMPLEX|软PIN 复杂度低|
|133|TUI_UNWRAP_KEY_FAILED|TUI 导入huks 密钥失 败|
|134|TUI_WRAP_KEY_FAILED|TUI 导出huks 密钥失 败|
|137|TUI_NOT_SET_TUI|TUI PIN 未调用UI 配 置接口|
|149|TUI_PIN_CANCEL|TUI PIN 取消操作|
|255|INNER_ERROR|系统内部错误,可根 据具体描述定位问题|

Android 没有 4、11、63、134 133、137 与Android 错误码含义不一致 

## **内部错误** 

|错误码 **AK 内部错误**|描述信息|说明信息|
|---|---|---|
|
2101|AK_CERT_INVALID_PARAM|0x01  参数错误|
|2102|AK_CERT_STACK_ERROR|0x02 数据开辟的空间 太小|
|2103|AK_CERT_MALLOC_ERROR|0x03 Malloc 空间太小|
|2104|AK_CERT_INVALID_CMD|0x04 指令不支持|
|2108|AK_CERT_INVALID_KH_ACCESS_TOKEN|0x08 校验khtoken 失败|
|2111|AK_CERT_CAL_GET_FAILED|0x0B Cal 层获取失败|
|2112|AK_CERT_UUID_IMPORT_FAILED|0x0C Uuid 导入失败|
|2113|AK_CERT_HASH_FAILED|0x0D Hash 算法失败|
|2114|AK_CERT_USER_SAVE_FAILED|0x0E 存储用户信息失 败|
|2115|AK_CERT_SAVE_FAILED|0x0F 存储证书失败|
|2116|AK_CERT_USER_GET_FAILED|0x10 获取用户信息失 败|
|2117|AK_CERT_GET_FAILED|0x11 获取证书信息失 败|
|2118|AK_CERT_REG_GET_FAILED|0x12 获取已注册信息 失败|
|2120|AK_CERT_PUB_KEY_EXPORT_FAILED|0x14 导出用户公钥失 败|
|2121|AK_CERT_PUB_KEY_WRAP_FAILED|0x15 组装用户公钥结 构失败|
|2122|AK_CERT_P10_SIGN_FAILED|0x16 签名p10 失败|
|2124|AK_CERT_CAL_INIT_FAILED|0x18 Cal 层初始化失败|
|2125|AK_CERT_PRIVATE_KEY_GET_FAILED|0x19 获取用户私钥失 败|
|2126|AK_CERT_TRANS_SIGN_FAILED|0x1A 签名交易信息失 败|
|2129|AK_CERT_STORE_OVER_LIMIT|0x1D 存储已满目前20 个|
|2135|AK_CERT_CRYPTO_FAILED|0x23 加解密数据失败|
|2136|AK_CERT_UUID_EXPORT_FAILED|0x24 导出uuid 失败|
|2137|AK_CERT_AUTHENTICATOR_GET_FAILED|0x25 查询认证器失败|
|2138|AK_CERT_AUTHENTICATOR_ADD_FAILED|0x26 增加认证器失败|
|2140|AK_CERT_TRNAS_HASH_FAILED|0x28 交易信息hash 失 败|
|2141|AK_CERT_TRNAS_PARSE_FAILED|0x29 交易信息解析失 败|

|2180|AK_CERT_RANDOM_GEN_FAILED|0x50 产生随机数失败|
|---|---|---|
|2181|AK_CERT_USER_KEY_PAIR_GEN_FAILED|0x51 产生用户密钥对 失败|
|2182|AK_CERT_P10_GEN_FAILED|0x52 产生p10 失败|
|2183|AK_CERT_P7_GEN_FAILED|0x53 产生p7 失败|
|2198|AK_CERT_INIT_FAILED|AK 初始化失败|
|2199|AKCERTPROCESSFAILED|AK 处理失败|
|
**SDK 内部错误**
|___ |
|
|2200|CMD_ENCODE_FAILED|指令编码失败|
|2201|CMD_EXEC_FAILED|指令执行失败|
|2202|CMD_DECODE_FAILED|指令解码失败|
|2203|ASM_DB_FAILED|数据库操作失败|
|2204|HUK_INIT_SESSION_FAILED|HUKS 会话初始化失败|
|2205|HUK_GEN_KEY_PAIR_FAILED|HUKS 生成公私钥对失 败|
|2206|HUK_EXPORT_PUB_KEY_FAILED|HUKS 导出公钥失败|
|2207|HUK_EXPORT_CERT_CHAIN_FAILED|HUKS 导出证书链失败|
|2208|ASM_INNER_ERROR|ASM 内部错误|
|2209|SYS_GET_BUNDLE_INFO_FAILED|获取bundle info 失败|
|2210|DISCOVER_CACHE_INIT_FAILED|元数据缓存初始化失败|

#### **七、PIN UI 配置项** 

|名称|数据类型|必 填|描述|
|---|---|---|---|
|pinMaxLen|number|否|Pin 码最大长度,6-10 之间,默认6|
|pinMinLen|number|否|Pin 码最小长度,6-10 之间,默认6|
|pinMaxErrCount|number|否|Pin 码最大试错次数,3-8 之间,默认6|
|logo|string|是|Logo 图片base64 格式数据,图片要求png 格 式 Tui PIN 要求图片规格216 x 216 软PIN 要求图片规格: 1080 x 200,1176 x 218,1440 x 267|

|title|string|否|Logo 下方提示文本 软 PIN 默认:温馨提示:本口令是金融盾交 易认证的密码,支持6 位。请妥善保管,勿 设置简单口令。 TUI PIN:不超过30 字节,默认:金融盾注 册|
|---|---|---|---|
|changePinTitle|String|否|修改PIN 时,Logo 下方提示文本 只适用于TUI PIN,不超过30 字节 默认:金融盾修改密码|
|regPinInputLabel1|string|否|注册输入框上方提示文本,默认: 请设置口令(6 位数字) 只适用于软PIN|
|regPinInputLabel2|string|否|注册确认输入框上方提示文本,默认:请再 次输入口令(6 位数字) 只适用于软PIN|
|changePinInputLabel1|string|否|修改pin 时原密码输入框提示文本 默认:请输入原口令(6 位) 如果要显示剩余可尝试次数,在文本中适当 位置加入%占位符,SDK 会将占位符替换成剩 余可尝试次数|
|changePinInputLabel2|string|否|修改pin 时新密码输入框提示文本 默认:请设置新口令(6 位)|
|changePinInputLabel3|string|否|修改pin 时新密码确认输入框提示文本 默认:请再次输入新口令(6 位)|
|authPinInputLabel|string|否|认证输入框上方提示文本,默认: 请输入口令(6 位数字) 只适用于软PIN 如果要显示剩余可尝试次数,在文本中适当 位置加入%占位符,SDK 会将占位符替换成剩 余可尝试次数|
|confirmText|string|否|确认按钮文本,默认:确认|

|cancelText|string|否|取消按钮文本,默认:取消|
|---|---|---|---|
|timeout|number|否|超时时间,单位:秒,默认:180|

#### **八、 PIN TUI 交易报文格式** 

基本格式:key:value|showFlag 

Key 为标签,value 为展示文本,showFlag:0(不显示);1(超出部分折行)2(超出部分 截断) 

多行用\n 分隔,末尾不要加\n 

例如:key:value|showFlag\nkey:value|showFlag\nkey:value|showFlag 

示例: 

交易:转账交易|1\n 收款账号:12345678901234567890|1\n 交易金额:10000000000|1\n 收款账号:12345678901234567890|1\n 收款人:张三丰|1 

页面UI 展示格式为: 

交易:转账交易 收款账号:12345678901234567890 交易金额:10000000000 收款账号:12345678901234567890 收款人:张三丰 

注意事项: 

1)key 和value 之间的冒号,可以是全角也可以是半角,但要统一 

2)多行交易报文用\n 分隔,但末尾不要有\n
