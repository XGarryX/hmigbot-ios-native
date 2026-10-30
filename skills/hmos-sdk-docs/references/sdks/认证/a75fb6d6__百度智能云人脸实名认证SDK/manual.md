# **前言** 

【本文】方案集成指南适用于需要集成APP方案,实现 **权威库核验** 、 **自传照片人脸比对** 、 **仅活体检测** 这3个业 务需求时来参考。百度人脸实名认证APP方案默认开启风控功能,即使用人脸识别V4系列API接口接受SDK端 传入本地环境扫描的设备指纹及安全信息,对SDK端进行设备风险识别,辨别是否为风险设备、并返回识别 结果。 **此方案可有效防御黑产批量虚拟机、病毒侵入等攻击手段,降低第三方黑产攻破概率,提升业务安全 性。** 

特殊的,如果控制台 **风控选项** 设定“ **关闭** ”,则需要配合开通人脸识别V3系列API接口实现 **权威库核验** 、 **自传照 片人脸比对** 、 **仅活体检测** 这3个业务需求。 

# **快速定位** 

人脸实名认证(权威库核验)实现方式 

人脸比对(自传图片)实现方式 

#### 仅活体检测实现方式 

获取认证人脸接口(服务端) 

核验及计费结果获取(服务端) 

#### 历史集成方案 

# **1. 文档说明** 

|**文档名称**|**人脸实名认证APP方案 6.4版本集成文档**|
|---|---|
|所属平台|HarmonyOS|
|提交日期|2024-09-03|

# **2. 版本说明** 

|**名称**|**版本号**|
|---|---|
|名镜方案|6.4.0|
|系统支持|HarmonyOS NEXT.0.0.36|

# **3. SDK说明** 

|**文件名称**|**版本号**|**说明**|
|---|---|---|
|lib_Enhance.har|名镜SDK业务逻辑封装|包含人脸采集、人脸安全等功能|
|注:获取SDK可参考: 获取示例工程|||

# **4. 配置包名和签名** 

从百度云控制台下载鸿蒙Demo之后,首先需要在app.json5中配置鸿蒙应用名称,更新宿主应用的 bundleName 

然后需要在build-profile.json5中配置好宿主应用的签名信息,更新宿主应用的所有签名信息material 

# **5. SDK集成与授权** 

- 首先在app工程中增加 **3. SDK说明** 中的依赖库资源 

- 其次将百度云控制台创建应用时获取的人脸授权文件( **idl-license.face-harmony** )放置于Assets目录下。*// 如果集成物料下载渠道为控制台,可忽略 

# **6. 人脸初始化接口(SDK)** 

初始化接口调用 

|**返**|||
|---|---|---|
|**回**|**API**|**描述**|
|**值**|||
|void|init(context: Context, licenseKey: string, licenseName: string, keyName: string, faceInitCallback: FaceInitCallback)|人脸初始 化接口|

#### 入参说明 

|**参数**|**类型**|**说明**|
|---|---|---|
|context|Context|上下文|
|licenseKey|String|授权Key|
|licenseName|String|授权文件名称|
|keyName|String|加解密文件名称|

#### onCallback回调说明 

|**参数**|**类型**|**含义**|**值**|
|---|---|---|---|
|resultCode|int|错误码|1000为成功,其他为失败,详情参考resultCode错 误码说明|
|resultMsg|String|详情见resultCode错误码 说明||

#### resultCode错误码说明 

|**resultCode**|**resultMsg**|**自查方案**|
|---|---|---|
|1001|License未初始化|请按照集成文档说明完成SDK初始化|
|1002|License数据解密失败|请检查License文件是否正确|
|1003|Licesen数据格式错误|请检查license文件内容有被修改过|
|1004|License-Key校验错误|请检查工程代码初始化参数中的licenseId,和申请license文件 的licenseId是否匹配|
|1005|算法ID校验错误|请提交工单或者线下联系百度产研人员|
|1006|鸿蒙应用指纹校验错误|请检查工程所使用的鸿蒙测试或发布证书,查看指纹和申请 license文件时的信息是否匹配|
|1007|设备ID校验错误|采集SDK的授权模式不会出现这个错误码|
|1008|鸿蒙bundleName应用 名称校验错误|请检查工程代码中的bundleName(包名)和申请license文件 时的信息是否匹配|
|1009|过期时间不正确|请提交工单或者线下联系百度产研人员|
|1010|功能未授权|请查看授权文件中是否缺少必要的采集SDK功能声明(funclist 参数),例如炫瞳活体|
|1011|授权已过期|请查看当前设备时间是否已不在授权文件有效期内|

|1012|本地文件读取失败|请检查授权文件名称以及路径|
|---|---|---|
|1013|远程数据拉取失败|本地鉴权失败之后,会远程拉取授权文件;若远程鉴权依然失 败,可以关闭网络后重试|
|1014|本地时间校验错误|请检查当前设备时间是否早于实际时间|
|2001|非法的参数|请提交工单或者线下联系百度产研人员|
|2002|内存分配失败|请提交工单或者线下联系百度产研人员|
|2003|实例对象为空|请提交工单或者线下联系百度产研人员|
|2004|模型内容为空|请提交工单或者线下联系百度产研人员|
|2005|不支持的能力类型|请提交工单或者线下联系百度产研人员|
|2006|不支持的预测库类型|请提交工单或者线下联系百度产研人员|
|2007|预测库对象创建失|请提交工单或者线下联系百度产研人员|
|2009|预测库对象初始化失败|请提交工单或者线下联系百度产研人员|
|2010|人脸能力初始化失败|请按照集成文档说明正常完成SDK初始化|
|2011|能力未加载|请确认当前人脸相关资源库是否完整引用|
|2012|人脸能力已加载|底层已做过滤,无需关注|
|2013|未授权|检查授权文件是否按照集成文档正常使用|
|2014|人脸能力运行异常|请提交工单或者线下联系百度产研人员|
|2015|不支持的图像类型|请提交工单或者线下联系百度产研人员|
|2016|图像转换失败|检查摄像头分辨率,格式要求%2==0|

# **7. 获取verify_token接口(服务端)** 

本接口为实名认证APP方案的verify_token获取接口,利用所获取的verify_token进行实名认证流程的有效期为 **2小 时** 。 

### **在线调试** 

**您可以在** **示例代码中心 中调试该接口** ,可进行签名验证、查看在线调用的请求内容和返回结果、示例代码的自动 生成。 

### **调用方式** 

#### **请求URL数据格式** 

向API服务地址使用POST发送请求,必须在URL中带上参数 access_token ,可通过后台的API Key和Secret Key 生成,具体方式请参考“Access Token获取”。 

**注意** : access_token 的有效期为30天, **切记需要每30天进行定期更换,或者每次请求都拉取新token** ; 

POST中Body的参数,按照下方请求参数说明选择即可。 

**提示** :如果您为百度云老用户,正在使用其他非AI的服务,可以参考百度云AKSK鉴权方式发送请求,虽然 **请 求方式** 和 **鉴权方法** 和本文所介绍的不同,但请求参数和返回结果一致。 

### **请求说明** 

#### **注意事项** : 

**请求体格式化** :Content-Type为 application/json ,通过 json 格式化请求体。 

#### **请求示例** 

#### HTTP方法: POST 

请求URL: https://aip.baidubce.com/rpc/2.0/brain/solution/faceprint/verifyToken/generate URL参数: 

|**参数**|**值**|
|---|---|
|access_token|通过API Key和Secret Key获取的access_token,参考“ Access Token获取”|

#### Header: 

|**参数**|**值**|
|---|---|
|Content-Type|application/json|

#### Body中放置请求参数,参数详情如下: 

#### **请求参数** : 

|**参数**|**必选**|**类型**|**说明**|
|---|---|---|---|
|match_source|是|int|方案类型(比对源);0:实名认证(权威库);1:人脸比对(上传照 片);2:仅活体检测。|
|plan_id|是|string|方案的id信息,请在人脸实名认证控制台查看创建的APP方案ID信息|

请求示例 

{ 

"match_source": 0, //以权威库核验场景为例,需要传入0 "plan_id": 16144, } 

#### **返回参数** 

|返回结果||||
|---|---|---|---|
|**字段**|**必选**|**类型**|**说明**|
||||返回请求是否成功信息。|
|success|是|boolean|若请求成功返回ture; 请求失败则返回false|
|result|是|object|请求结果|
|+verify_token|是|string|请求获取的verify_token|
|返回示例||||

{ "success": true, "result": { "verify_token": "Yz9rWITm4vak16PBAh5x8oG7" }, "log_id": "1814798895" } 

# **8. 人脸实名认证实现方式** 

实现方式请参考如下时许图 

## **8.1 指定用户信息上报接口(服务端)** 

本接口用于,控制台APP方案中选择身份信息录入方式为 **业务调用时传入** ,需要先调用此接口输入指定用户的姓名 +身份证号信息,再继续请求 **人脸权威库核验接口(SDK)** 

### **在线调试** 

**您可以在** **示例代码中心 中调试该接口** ,可进行签名验证、查看在线调用的请求内容和返回结果、示例代码的自动 生成。 

### **调用方式** 

#### **请求URL数据格式** 

向API服务地址使用POST发送请求,必须在URL中带上参数 access_token ,可通过后台的API Key和Secret Key 生成,具体方式请参考“Access Token获取”。 

- **注意** : access_token 的有效期为30天, **切记需要每30天进行定期更换,或者每次请求都拉取新token** ; 

POST中Body的参数,按照下方请求参数说明选择即可。 

**提示** :如果您为百度云老用户,正在使用其他非AI的服务,可以参考百度云AKSK鉴权方式发送请求,虽然 **请 求方式** 和 **鉴权方法** 和本文所介绍的不同,但请求参数和返回结果一致。 

### **请求说明** 

#### **注意事项** : 

#### **请求体格式化** :Content-Type为 application/json ,通过 json 格式化请求体。 

#### **请求示例** 

#### HTTP方法: POST 

请求URL:https://aip.baidubce.com/rpc/2.0/brain/solution/faceprint/idcard/submit 

#### URL参数: 

|**参数**|**值**|
|---|---|
|access_token|通过API Key和Secret Key获取的access_token,参考“ Access Token获取”|

#### Header: 

|**参数**|**值**|
|---|---|
|Content-Type|application/json|

#### Body中放置请求参数,参数详情如下: 

|**参数**|**必选**|**类型**|**值**|
|---|---|---|---|
|verify_token|是|string|通过access_token获取的verify_token|
|id_name|是|string|指定输入用户的姓名信息|
|id_no|是|string|指定输入用户的身份证件号信息|
|certificate_type|否|int|证件类型: 0大陆居⺠二代身份证 4港澳台居⺠居住证|

#### 请求示例: 

{ 

"verify_token": "2sF3nE5mXOHkx2aQwWG4n5WI", 

"id_name": "张三", 

"id_no": "500***********3390", 

"certificate_type": 0 // 证件类型:0:大陆居⺠二代身份证,4:港澳台居⺠居住证 } 

**返回参数** 

返回结果 

|**字段**|**必选**|**类型**|**说明**|
|---|---|---|---|
|success|是|boolean|返回请求是否成功信息。 若请求成功返回ture; 请求失败则返回false|
|result|是|int|请求结果,返回固定结果1,可忽略|
|log_id|是|string|本次查询接口请求的logid|

#### 返回示例 

{ "success": true, "result": 1, "log_id": "1244068892" } 

## **8.2 人脸权威库核验接口(SDK)** 

基于姓名、身份证号、当前SDK获取的人脸图片,与权威库进行对比,并得出比对分数,并基于此进行业务判断是 否为同一人。包含活体检测、质量检测、实名认证功能,可通过传入参数进行控制,如您的业务场景核心为实名认 证,无需重复请求 **7.4 人脸活体检测** 接口。 

|**返回值**|**API**|**描述**|
|---|---|---|
|void|startFaceVerify(params: HashMap<string, Object>, faceServiceCallbck: FaceServiceCallbck)|SDK核验接 口|

入参params (HashMap类型) key值列表如下: 

|**参数**|**类型**|**说明**|**必选**|
|---|---|---|---|
|verify_token|String|需要APP服务端通过AK、SK获取access_token,参考 https://ai.baidu .com/docs#/Auth/top,然后通过access_token获取verify_token**【此处需要注意】verify_token有效期两个小时,建议每次调用接口重新获取verify_token**|是|
|plan_id|String|在控制台配置的方案Id|否|
|certificate_type|int|证件类型;0:中国居⺠二代身份证,1:港澳台来往内地通行证,2: 外国人永久居留证,3:定居国外的中国公⺠护照,4:港澳台居⺠居 住证。默认为0|否|
|match_source|int|方案类型(比对源);0:实名认证(权威库);1:人脸比对(上传 照片);2:仅活体检测;**这里默认传入0**|是|
|onCallback回 调说明||||
|**参数** |**类型**|**含义值**||
|resultCode |int|错误码 0为成功,其他为失败,详情参考resultCode错误码说|明|
|resultMap |HashMap|回调结果Map 详情见下表||

resultMap key值列表说明: 

|**Key值**|**类型**|**含义**|
|---|---|---|
|resultMsg|String|详情见resultCode错误码说明|
|data|String|服务端返回结果json,只有错误码为0时会返回 此字段,具体内容可以参考 人脸实名 认证V4 或 人脸实名认证V3 接口文档|

#### 返回示例 

{ 

"error_code": 0,  //认证建议结果为通过,该结果仅供参考;可通过调用服务端getall接口获取最终认证结 果 

"log_id": "1790651229035123218" 

} 

# **9. 人脸对比(自传照片)实现方式** 

实现方式请参考如下时许图 

## **9.1 对比图片上传接口(服务端)** 

本接口适用于人脸比对(自传照片)业务场景,为了保证用户信息安全,您需要提前通过服务端请求本接口来上报 比对人脸信息。 

### **在线调试** 

**您可以在** **示例代码中心 中调试该接口** ,可进行签名验证、查看在线调用的请求内容和返回结果、示例代码的自动 生成。 

### **调用方式** 

#### **请求URL数据格式** 

向API服务地址使用POST发送请求,必须在URL中带上参数 access_token ,可通过后台的API Key和Secret Key 生成,具体方式请参考“Access Token获取”。 

**注意** : access_token 的有效期为30天, **切记需要每30天进行定期更换,或者每次请求都拉取新token** ; 

POST中Body的参数,按照下方请求参数说明选择即可。 

**提示** :如果您为百度云老用户,正在使用其他非AI的服务,可以参考百度云AKSK鉴权方式发送请求,虽然 **请 求方式** 和 **鉴权方法** 和本文所介绍的不同,但请求参数和返回结果一致。 

### **请求说明** 

#### **注意事项** : 

#### **请求体格式化** :Content-Type为 application/json ,通过 json 格式化请求体。 

#### **请求示例** 

#### HTTP方法: POST 

请求URL: https://aip.baidubce.com/rpc/2.0/brain/solution/faceprint/uploadMatchImage 

#### URL参数: 

|**参数**|**值**|
|---|---|
|access_token|通过API Key和Secret Key获取的access_token,参考“ Access Token获取”|

#### Header: 

|**参数**|**值**|
|---|---|
|Content-Type|application/json|

#### Body中放置请求参数,参数详情如下: 

|**参数**|**必选**|**类型**|**值**|
|---|---|---|---|
|verify_token|是|string|通过access_token获取的verify_token|
|image|是|string|图片base64字符串,编码后的图片大小不超过10M,图片分辨率小 于1920*1080|
|quality_control|否|string|“**NONE**”、“**LOW**”、“**NORMAL**”、“**HIGH**”; 质量控制参数,未主动传入时默认为“NONE”|
|liveness_control|否|string|“**NONE**”、“**LOW**”、“**NORMAL**”、“**HIGH**”; 活体控制参数,未主动传入时默认为“NONE”|

请求示例: 

{ 

"verify_token": "2sF3nE5mXOHkx2aQwWG4n5WI", 

"image": "/9j/4AAQSkZJRgABAQAAAQABAAD/", "quality_control" : "LOW", "liveness_control" : "LOW", } 

#### **返回参数** 

#### 返回结果 

|**字段**|**必选**|**类型**|**说明**|
|---|---|---|---|
|success|是|boolean|返回请求是否成功信息。 若请求成功返回ture; 请求失败则返回false|
|log_id|是|string|logid|
|result|是|object|返回结果|

#### 返回示例 

{ "success": true, "result": null, "log_id": "1329130892" } 

## **9.2 人脸对比(SDK)** 

包含活体检测、质量检测、人脸1:1识别功能,可通过传入参数进行控制,如您的业务场景核心为人脸对比(自传 照片),无需重复请求 **7.4 人脸活体检测** 接口。 

|**返回值**|**API**|**描述**|
|---|---|---|
|void|startFaceVerify(params: HashMap<string, Object>, faceServiceCallbck: FaceServiceCallbck)|SDK核验接 口|

入参params (HashMap类型) key值列表如下: 

|**参数**|**类型**|**说明**|**必选**|
|---|---|---|---|
|verify_token|String|需要APP服务端通过AK、SK获取access_token,参考 https://ai.baidu.c om/docs#/Auth/top,然后通过access_token获取verify_token**【此处需要注意】verify_token有效期两个小时,建议每次调用接口重新获取verify_token**|是|
|match_source onCallback回调说|int 明|方案类型(比对源);0:实名认证(权威库);1:人脸比对(上传照 片);2:仅活体检测;**这里默认传入1**|是|
|**参数**|**类型**|**含义值**||
|resultCode|int|错误码 0为成功,其他为失败,详情参考实名认证resultCode错 说明|误码|
|resultMap|HashMap|回调结果 Map 详情见下表||

#### resultMap key值列表说明: 

|**Key值**|**类型**|**含义**|
|---|---|---|
|resultMsg|String|详情见resultCode错误码说明|
|data|String|服务端返回结果json,只有错误码为0时会返回 此字段,具体内容可以参考 人脸对比 V4 或 人脸对比V3 接口文档|

#### 返回示例 

#### { 

"error_code": 0,  //认证建议结果为通过,该结果仅供参考;可通过调用服务端getall接口获取最终认证结 果 

"log_id": "1790651229035123218" 

} 

# **10. 人脸活体检测实现方式** 

实现方式请参考如下时许图 

## **10.1 活体检测(SDK)** 

包含本地活体加云端活体,本地活体分静默活体、炫瞳活体、动作活体三种,云端活体可以判断图片中的人脸是否 为二次翻拍以及是否为合成图攻击。实现二次验证采集图片是否存在假体攻击破绽的情况。 

如您的业务场景核心为人脸实名认证(权威源),请直接参考 **7. 人脸实名认证实现方式** 。 

|**返回值**|**API**|**描述**|
|---|---|---|
|void|startFaceVerify(Context context, Map params, FaceServiceCallbck FaceServiceCallbck)|SDK核验接 口|

入参params (HashMap类型) key值列表如下: 

|**参数**|**类型**|**说明**|**必选**|
|---|---|---|---|
|verify_token|String|需要APP服务端通过AK、SK获取access_token,参考 https://ai.baidu.c om/docs#/Auth/top,然后通过access_token获取verify_token**【此处需要注意】verify_token有效期两个小时,建议每次调用接口重新获取verify_token**|是|
|match_source onCallback回调说|int 明|方案类型(比对源);0:实名认证(权威库);1:人脸比对(上传照 片);2:仅活体检测;**这里默认传入2**.|是|
|**参数**|**类型**|**含义值**||
|resultCode|int|错误码 0为成功,其他为失败,详情参考实名认证resultCode错 说明|误码|
|resultMap|HashMap|回调结果 Map 详情见下表||

#### resultMap key值列表说明: 

|**Key值**|**类型**|**含义**|
|---|---|---|
|resultMsg|String|详情见resultCode错误码说明|
|data|String|服务端返回结果json,只有错误码为0时会返回 此字段,具体内容可以参考 在线图片 活体检测V4 或 在线图片活体检测V3接口|

#### 返回示例 

#### { 

"error_code": 0,  //认证建议结果为通过,该结果仅供参考;可通过调用服务端getall接口获取最终认证结 果 

"log_id": "1790651229035123218" 

} 

# **11. 验证后查询接口** 

## **11.1 获取认证人脸接口(服务端)** 

本接口返回进行人脸实名认证过程中进行认证的最终采集的人脸信息。根据Verify_token返回的结果信息会在云端 保留 **3天** ,您可根据需要在此期间进行调取查询。 

### **在线调试** 

**您可以在** **示例代码中心 中调试该接口** ,可进行签名验证、查看在线调用的请求内容和返回结果、示例代码的自动 生成。 

### **调用方式** 

#### **请求URL数据格式** 

向API服务地址使用POST发送请求,必须在URL中带上参数 access_token ,可通过后台的API Key和Secret Key 生成,具体方式请参考“Access Token获取”。 

**注意** : access_token 的有效期为30天, **切记需要每30天进行定期更换,或者每次请求都拉取新token** ; 

POST中Body的参数,按照下方请求参数说明选择即可。 

**提示** :如果您为百度云老用户,正在使用其他非AI的服务,可以参考百度云AKSK鉴权方式发送请求,虽然 **请 求方式** 和 **鉴权方法** 和本文所介绍的不同,但请求参数和返回结果一致。 

### **请求说明** 

#### **注意事项** : 

**请求体格式化** :Content-Type为 application/json ,通过 json 格式化请求体。 

#### **请求示例** 

#### HTTP方法: POST 

请求URL: https://aip.baidubce.com/rpc/2.0/brain/solution/faceprint/result/simple 

#### URL参数: 

|**参数**|**值**|
|---|---|
|access_token|通过API Key和Secret Key获取的access_token,参考“ Access Token获取”|

#### Header: 

|**参数**|**值**|
|---|---|
|Content-Type|application/json|

#### Body中放置请求参数,参数详情如下: 

|**参数**|**值**|
|---|---|
|verify_token|通过access_token获取的verify_token|

请求示例: 

{ 

"verify_token" : "cIupeyP51sn28XzxGVTfYqoN" 

} 

#### **返回参数** 

返回结果 

|**字段**|**必选**|**类型**|**说明**|
|---|---|---|---|
|success|是|boolean|返回请求是否成功信息。 若请求成功返回ture; 请求失败则返回false|
|result|是|object|请求结果|
|+image|是|string|返回采集的用户人脸信息|

返回示例 

{ "success": true, 

"result": { 

"image":"https://brain.baidu.com/solution/faceprint/image/query? verify_token=xxxxxx" }, "log_id": "1054986003" } 

## **11.2 核验及计费信息获取(服务端)** 

根据Verify_token返回的信息会在云端保留 **3天** ,您可根据需要在此期间进行调取查询。 

### **调用方式** 

#### **请求URL数据格式** 

向API服务地址使用POST发送请求,必须在URL中带上参数 access_token ,可通过后台的API Key和Secret Key 生成,具体方式请参考“Access Token获取”。 

**注意** : access_token 的有效期为30天, **切记需要每30天进行定期更换,或者每次请求都拉取新token** ; 

POST中Body的参数,按照下方请求参数说明选择即可。 

**提示** :如果您为百度云老用户,正在使用其他非AI的服务,可以参考百度云AKSK鉴权方式发送请求,虽然 **请 求方式** 和 **鉴权方法** 和本文所介绍的不同,但请求参数和返回结果一致。 

### **在线调试** 

**您可以在** **示例代码中心 中调试该接口** ,可进行签名验证、查看在线调用的请求内容和返回结果、示例代码的自动 生成。 

### **请求说明** 

#### **注意事项** : 

**请求体格式化** :Content-Type为 application/json ,通过 json 格式化请求体。 

#### **请求示例** 

HTTP方法: POST 

请求URL: https://aip.baidubce.com/rpc/2.0/brain/solution/faceprint/result/getall 

#### URL参数: 

|**参数**|**值**|
|---|---|
|access_token Header:|通过API Key和Secret Key获取的access_token,参考“ Access Token获取”|
|**参数**|**值**|
|Content-Type|application/json|

#### Body中放置请求参数,参数详情如下: 

|**参数**|**值**|
|---|---|
|verify_token|通过access_token获取的verify_token|

#### 请求示例: 

{ "verify_token" : "cIupeyP51sn28XzxGVTfYqoN" } 

#### **返回参数** 

#### 返回结果 

|**字段**|**必选**|**类型**|**说明**|
|---|---|---|---|
||||返回请求是否成功信息。|
|success|是|boolean|若请求成功返回ture; 请求失败则返回false|

|log_id|是|string|本次查询接口请求的logid|
|---|---|---|---|
|result|是|object|结果信息|
||||当前verify_token对应的核验次数,核验次数为几,后面就有 几个对象数组|
|+verify_count|是|int|如方案配置为“认证未通过时URL失效”,则该verify_token核 验次数为1; 如方案配置为“认证未通过时URL不失效”,则该verify_token 对应的核验次数可能大于1(用户核验失败后多次重试)|
|+ocr_charge_count|是|int|身份证识别OCR接口的计费次数//鸿蒙APP方案暂不支持|
|+match_charge_count|是|int|人脸对比接口的计费次数|
|+verify_charge_count|是|int|人脸实名认证接口的计费次数|
|+verify_result|是|object[]|核验结果信息,verify_count的值为几,就返回几个该对象|
|++order|是|int|代表本次核验结果在verify_token所有核验次数中的顺序,按 时间先后排序,第一次核验返回值为1,第二次核验返回值 为2,以此类推|
|++is_verify_passed|是|boolean|本次核验是否通过 核验成功返回true 核验失败返回false|
|++code|是|string|本次核验的错误码 核验成功时返回0 核验失败返回非0错误码|
|++message|是|string|本次核验的错误信息 核验成功时返回“核验成功” 核验失败时返回具体错误原因,如“身份证姓名不匹配”|
|++verify_time|是|string|本次核验完成的时间点,包含年月日、时分秒,如“2023-6- 20 18:00:00”|
|++is_charged|是|boolean|本次核验是否计费 计费返回true 不计费返回false|
|++charge_type|是|string|计费类型:**verify**(人脸实名认证)、**match**(人脸对 比)、**live**(在线图片活体)|
|++charge_time|是|string|本次计费的时间点,如不计费则该字段为空,包含年月日、 时分秒,如“2023-6-20 18:00:00”|
|++is_ocr_charge|否|boolean|身份证识别OCR是否计费//鸿蒙APP方案暂不支持 计费返回true 不计费返回false|

|++ocr_charge_time|否|string|ocr收费时间点,如不收费则该字段为空,包含年月日、时 分秒,如“2023-6-20 18:00:00”|
|---|---|---|---|
|++ocr_count|否|int|ocr次数|
|++verify_detail|是|object|核验的详细信息|
|+++face_image|是|string|本次核验流程中采集的人脸最佳质量图下载url|
|+++verify_log_id|是|string|本次核验流程中请求的人脸实名认证(方案配置权威库比 对)、人脸对比(方案配置自建人脸库比对)、在线图片活 体(仅活体检测)后端接口logid,支持在记录查询平台中通 过logid查询到3天内的记录。 少数核验失败情况下,实际并未发生上述俩接口的请求,则 该字段为空,如:用户拒绝摄像头授权且不允许降级|
|+++score|是|float|人脸相似度得分,大于等于方案设置阈值为同一人;当身份 证姓名不匹配或活体不通过时,该项为空|
|+++threshold|是|float|本次核验时,所使用的方案配置相似度阈值|
|+++liveness_score|是|float|活体检测得分,注:预留功能字段,当前返回为0|
|+++spoofing_score|否|float|方案配置使用合成图功能,将返回合成图得分,注:预留功 能字段,当前返回为0|
|+++risk_level|否|string|安全风控等级 方案配置启用安全风控,将返回该字段 值为1或2时表示触发了安全风险,值为3或4时无风险|
|+++risk_tag|否|string|安全风控标签 方案配置启用安全风控,将返回该字段 当risk_level值为1或2时,返回具体风险类型,risk_level值为 3或4时,为空|
|+++is_demote|否|boolean|H5方案相关,可忽略|
|++idcard_confirm|是|object|用户手动输入或二次确认的身份证信息|
|+++name|是|string|姓名|
|+++idcard_number|是|string|证件号|
|+++idcard_type|是|string|证件类型,大陆居⺠二代身份证返回0|
|++idcard_ocr_result|否|object|OCR采集的身份证信息,当方案配置使用OCR采集证件照时 返回该参数//鸿蒙APP方案暂不支持|
|++idcard_images|否|object|返回采集的身份证图片信息 当人脸实名认证控制台设置为使用OCR识别时返回此参数信 息//鸿蒙APP方案暂不支持|

返回示例 

{ 

"success": true, "result": { "verify_count": 1, "ocr_charge_count": 0, "match_charge_count": 0, "verify_charge_count": 1, "verify_result": [ { "order": 1, "code": "0", "message": "核验成功", "is_verify_passed": true, "verify_time": "2024-04-02 16:15:01", "is_charged": true, "charge_type": "verify", "charge_time": "2024-04-02 16:15:01", "is_ocr_charge": false, "ocr_count": 0, "ocr_charge_time": null, "verify_detail": { "score": 84.4000015258789, "threshold": 80.0, "app": true, 

"face_image": "https://bj.bcebos.com/v1/mingjing-qa/hb/h5-videotemp/temp/202404/16130/ZWCCBxXUz48Q9wuR/Igi1n0SpQRtzm9ySWLQwdwvn-00.jpg? authorization=bce-auth-v1%2F89e9208d0d5a497cbc8922a4d74d4f71%2F2024-04- 

02T08%3A19%3A23Z%2F86400%2F%2Fb3abf9eef0b7f897ccf0350d7d59bbfd4498ab214ef73d437a45e319e 5028688", 

"verify_log_id": "1775074433891895605", "liveness_score": 0.99999183, "spoofing_score": null, "risk_level": null, "risk_tag": null, "is_demote": false }, "idcard_confirm": { "name": "李跃坤", "idcard_number": "140522199804101534", "idcard_type": "0", "idcard_ocr_result": null, "idcard_images": null } } ] }, "log_id": "1775075543214005842" 

} 

# **12. 人脸释放接口(SDK)** 

人脸释放接口调用,实现对采集功能、模型的释放,减小内存。 

|**返回值**|**API**|**描述**|
|---|---|---|
|void|release()|人脸释放接口|

# **13. 人脸采集相关配置(SDK)** 

人脸相关配置来自于百度云控制台下发的console_config.json文件,详情请参考Demo的BaseFragment类中以下 2个方法: 

- setFaceQualityConfig():人脸质量判断相关配置 

- faceLiveConfig():设置活体类型、活体动作 

注:不设置,将使用默认值。 

// 是否开启炫彩活体能力 

faceLiveConfig.setIsOpenColorLive(true); 

// 是否开启动作活体能力 

faceLiveConfig.setIsOpenActionLive(true); 

livenessValueModel = faceLiveConfig.getLivenessValueModel(); 

//设置活体动作池,如眨眨眼、张张嘴等 

```arkts
for (let i = 0; i < this.consoleConfig.getActions().length; i++) { 
```

livenessValueModel.actionList.add(this.consoleConfig.getActions()[i]); } 

//设置随机动作数量,实现M选N的随机动作效果 

livenessValueModel.actionRandomNumber = this.consoleConfig.getFaceActionNum(); 

# **权限** 

|**名称**|**说明**|**必选**|
|---|---|---|
|需要动态申请的权限|||
|ohos.permission.CAMERA|拍照权限|是|
|不需要动态申请的权限|||
|ohos.permission.INTERNET|允许访问网络|是|

# **14. 历史集成方案** 

如果您曾经在控制台创建过人脸实名认证应用与APP方案,希望通过SDK采集获取人脸加密数据,经由服务端转 发,配合百度云端接口调用的形式实现实名认证、活体检测及人脸比对的业务流程。可参考如下时许图进行集成与 前后端联调: 

## **14.1 修改accessToken** 

#### 在完成 **4.配置包名和签名** 后,需要实现动态获取accessToken。 

- access_token是是用户的访问令牌,承载了用户的身份、权限等信息。 

- 出于安全性考虑,正式环境需要APP服务端通过AK、SK来获取access_token,移动端测试可以链接拼接AK、 SK的方式来获取access_token。【此处需要注意】 

- access_token存在有效期,正式环境需要APP服务端通过AK、SK来获取access_token,此处只测试使(http 

- s://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=【百度云应用的AK】 &client_secret=【百度云应用的SK】)。 

## **14.2 人脸采集及人脸比对接口(无源)** 

包含本地质量和本地活体,本地质量可以确保采集到的人脸图像符合各条件校验(满足姿态⻆、光照、模糊度、遮 挡等校验),本地活体分静默活体、炫瞳活体、动作活体三种。 

此处最终采集到的数据经过加密处理,需要配合开放平台人脸对比V4接口使用,包含活体检测、质量检测、人脸 1:1识别功能,可通过传入参数进行控制,如您的业务场景核心为实名认证,无需重复请求 **7.3活体检测接口** 

- (startFaceLiveness)。 

|**返回值**|**API**|**描述**|
|---|---|---|
|void|startFaceCollect(params: HashMap<string, Object>, faceServiceCallbck: FaceServiceCallbck)|人脸采集 接口|

#### onCallback回调说明 

|**参数**|**类型**|**含义**|**值**|
|---|---|---|---|
|resultCode|int|错误码|0为成功,其他为失败,详情参考实名认证resultCode错误码 说明|
|resultMap|HashMap|回调结果 Map|详情见下表|

resultMap key值列表说明: 

|**Key值**|**类型**|**含义**|
|---|---|---|
|resultMsg|String|详情见resultCode错误码说明|
|sKey|String|安全相关:sKey|
|xDeviceId|String|安全相关:xDeviceId|
|data|String|安全相关数据|

# **常见问题** 

## **如何获取鸿蒙应用指纹** 

#### (1)方法1,测试证书 

- “应用指纹”signatureInfo.fingerprint是鸿蒙应用签名证书(.cer文件)的SHA-256hash值,当前支持获取本应用 的“应用指纹”。示例代码如下: 

```arkts
import { bundleManager } from '@kit.AbilityKit'; 
import { hilog } from '@kit.PerformanceAnalysisKit'; 
import { BusinessError } from '@kit.BasicServicesKit'; 
```

let bundleFlags = bundleManager.BundleFlag.GET_BUNDLE_INFO_WITH_SIGNATURE_INFO; 

try { 

bundleManager.getBundleInfoForSelf(bundleFlags).then((data) => { 

hilog.info(0x0000, 'testTag', 'getBundleInfoForSelf successfully. Data: % 

{public}s', JSON.stringify(data)); 

//data里可以获取到signatureInfo,即应用的签名证书信息 

}).catch((err: BusinessError) => { 

hilog.error(0x0000, 'testTag', 'getBundleInfoForSelf failed. Cause: %{public}s', err.message); 

}); 

- } catch (err) { 

let message = (err as BusinessError).message; 

hilog.error(0x0000, 'testTag', 'getBundleInfoForSelf failed: %{public}s', message); } 

#### (2)方法2,测试证书+发布证书 

- 在项目级build-profile.json5文件中,signingConfigs字段内的profile的值即为签名文件的存储路径。 打开该签名文件( **后缀为.p7b** ),打开后在文件内搜索“development-certificate”,将“-----BEGIN CERTIFICATE-----”和“-----END CERTIFICATE-----”以及中间的信息拷⻉到新的文本中,注意换行并去掉换行符, 保存为一个新的.cer文件,如命名为xxx.cer。新的.cer文件格式如下图(仅作为格式示意,内容以实际为 准): 

- 使用keytool工具(在DevEco Studio安装目录下的jbr/bin文件夹内),执行如下命令通过.cer文件获取证书 指纹的SHA256值。 

keytool -printcert -file xxx.cer 

- 将证书指纹中SHA256的内容去掉冒号,即为最终要获得的签名指纹。如SHA256值为下图(仅作为格式示 意,内容以实际为准): 

#### 去掉冒号后的签名指纹为: 

5753DDBC1A8EF88A62058A9FC4B6AFAFC1C5D8D1A1B86FB3532739B625F8F3DB 

## **verify_token的详细说明** 

(1)access_token 有效期为 30 天,重复生成 access_token 的话,对之前的不影响,依旧能使用; access_token 与verify_token 是包含关系,即 verify_token 是由 access_token生成的,如果一个 verify_token 是 和一个不匹配的 access_token 使用,会提示“Token无效或者已过期” 

(2)verify_token 的核验有效期为 2 小时,在有效期内可以进行了核验动作,如果超过了 2 小时没有使用该 token 进行核验的话会提示“Token无效或者已过期” 

(3) verify_token 核验完毕后(核验成功,或设置了认证未通过时URL失效),无法再进行核验,如果再次进行 核验,会提示“Token无效或者已过期” 

(4) verify_token 核验完毕后(核验成功,或设置了认证未通过时URL失效),支持对后验接口的查询,有效期 均为 3 天,3 天后再次查询后验接口,会提示“Token无效或者已过期” 

## **获取认证人脸、查询认证结果、核验及计费信息获取接口持续返回错误码 18,提示openapi限制,且有返回logid** 

**答:** 检查APP方案依赖的“人脸实名认证V3/V4”、“人脸对比V3/V4”、“在线图片活体检测V3/V4” 三项付费接口,是 否有免费额度,或者直接开通后付费,以消除该报错提示。开通后,再进行重试。
