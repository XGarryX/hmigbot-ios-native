# 智能双录 **SDK AnyChat** 接口文档使用指南 

广 州 佰 锐 网 络 科 技 有 限 公 司 **Guangzhou BaiRui Network Technology Co.,Ltd.** 

http://www.bairuitech.com http://www.anychat.cn 

目录
1. 文档及集成说明 .............................................................................................................................2
2. 组件业务功能配置说明 ................................................................................................................. 2
2.1. SDK 基础配置功能示例 ...............................................................................................................2
2.2. SDK 可选扩展配置功能示例 .......................................................................................................3
3. 组件所需权限信息及合规要求 ......................................................................................................4
3.1. 权限使用说明 ............................................................................................................................... 4
4. 业务组件API 说明 ........................................................................................................................6
4.1. 组件启动接口说明 ....................................................................................................................... 6
4.2. 代理回调接口说明 ..................................................................................................................... 11
5. 视频组件混淆加固说明 ............................................................................................................... 12
6. 错误码 .......................................................................................................................................... 12

|目录|
|---|
|**1.** 文档及集成说明**.............................................................................................................................2**|
|**2.** 组件业务功能配置说明**................................................................................................................. 2**|
|2.1. SDK基础配置功能示例...............................................................................................................2|
|2.2. SDK可选扩展配置功能示例.......................................................................................................3|
|**3.** 组件所需权限信息及合规要求**......................................................................................................4**|
|3.1. 权限使用说明............................................................................................................................... 4|
|4. 业务组件API 说明**........................................................................................................................6**|
|4.1. 组件启动接口说明....................................................................................................................... 6|
|4.2. 代理回调接口说明..................................................................................................................... 11|
|**5.** 视频组件混淆加固说明**............................................................................................................... 12**|
|**6.** 错误码**.......................................................................................................................................... 12**|

第 1 页 16 页 

### **1.** 文档及集成说明 

本文档为 AnyChat 智能双录 SDK 接口文档使用指南说明文档,为移动端集成开发提供 指导。组件详细调用方式及回调处理操作可参考示例工程 Demo。 

#### 集成说明 **:** 提供 **har** 包的方式供客户集成使用 **;** 

#### 开发工具 **: DevEco Studio** 

#### 依赖包名称 **:AnyChatAIShuangLuCFSelf.har** 

#### 集成方式: 

将 har 包放在自己工程目录的 libs 目录下(注意一定要是此目录,如果放在 main 目录下 的 jniLibs 目录下无效) 

(1) 在 module 的 oh-package.json5 文件 dependencies 添加如下 gradle 依赖; "@ohos/AnyChatAIShuangLuCFSelf":"file:./libs/AnyChatAIShuangLuCFSelf.har" 将 arm64-v8a 库文件、anychat-sdk-harmony.jar 文件复制到工程的 libs 目录下 

### **2.** 组件业务功能配置说明 

### 接入说明:包括基本功能和扩展功能 基本业务功能:音视频录制、视频上传 

扩展业务功能:活体检测、AI 实时质检、业务扩展参数透传、智能播报变量配置等 

|功能区分|业务功能|功能介绍|配置方式|
|---|---|---|---|
|基本功能|音视频录制|提供实时录音录像 相关功能|/|
||视频上传|提供视频上传功能|详见SDK基础配置功能示例|
|扩展功能|活体检测 AI实时质检|提供活体检测功能 提供实时质检功能|详见SDK可选扩展配置功能示例 详见SDK可选扩展配置功能示例|

### **2.1. SDK** 基础配置功能示例 

|信息类型|信息采集目的|基础配置信息说明 配置说明|
|---|---|---|
|登录信息|用于SDK进行连 接登录|let componentJsonObject: object = new Object(); componentJsonObject[ComponentField.LOGIN_IP] = loginIp; // 集群登录Ip|

第 2 页 16 页 

componentJsonObject[ComponentField.LOGIN_PORT] =
loginPort; // 集群登录端口
componentJsonObject[ComponentField.LOGIN_APP_ID] =
loginAppId; // 集群登录 appId
//AnyChat  服务器登录扩展参数 ( 必传 )
componentJsonObject[ComponentField.CUST_ID] =
业务办理所需,如:'12345'; //客户 id
用户信息 根据用户信息查询 componentJsonObject[ComponentField.CUST_NAME] = "
客户十要素信息 张三"; //客户名称
业务办理所需,用
于指定客户端业务 componentJsonObject[ComponentField.TARGET_MODEL]
业务模块 办理的环节,如: = TargetModel.TargetModelRecord; // 业务开始选择步
活体检测、音视频 骤
录制、视频上传
2.2. SDK 可选扩展配置功能示例
信息类型 信息采集目的 配置说明
componentJsonObject[ComponentField.TARGET
活体检测环节 提供活体检测功能
_MODEL] = TargetModel.TargetModelFc;
componentJsonObject[ComponentField.TARGET
视频上传环节 提供视频上传功能
_MODEL] = TargetModel.TargetModelRecord;
let aiConfig: Array<object> = new Array();
let json1: object = new Object();
json1[ComponentField.CONFIG_NAME] =
ComponentField.PARAM_FACE_IN_FRAME;
json1[ComponentField.ENABLE] = 1;
json1[ComponentField.CONFIG_DEC] = "在框检
用于坐席服务端展
AI 实时质检 测";
示接入设备型号
let content1: object = new Object();
content1[ComponentField.RATE] = "5"
content1[ComponentField.FACE_NUM] = "1"
content1[ComponentField.ALLOW_NO_PASS] =
"3"
content1[ComponentField.ALLOW_MORE_FACE_

第 3 页 16 页 

NO_PASS] = "1" json1[ComponentField.CONFIG_CONTENT] = content1; aiConfig.push(json1); // 在框检测 componentJsonObject[ComponentField.AI_CONFI G] = JSON.stringify(aiConfig); 

### **3.** 组件所需权限信息及合规要求 

### **3.1.** 权限使用说明 

为实现音视频通信功能所必需的系统权限、使用目的及建议申请时机如下,因相 关权限的不申请将会对其对应的功能造成影响,您可以结合业务实际需要进行合 理配置。 

**module.json5** 配置文件权限统一配置,请在宿主工程的 **module.json5** 配置文件中添加如 下权限 **:** 

ohos.permission.INTERNET 

ohos.permission.CAMERA 

ohos.permission.MICROPHONE 

ohos.permission.MEDIA_LOCATION 

ohos.permission.READ_MEDIA 

ohos.permission.WRITE_MEDIA 

|权限名称|权限说明|使用目的|是否 可选|申请时机|
|---|---|---|---|---|
|ohos.permission.INTE RNET|网络访问权限|用于访问网络连接; 互联网网络请求;|必选|初始化时调用|
|ohos.permission.CAM ERA|相机权限|用于用户视频通话交 互**;** 使用视频通话功能,需要 开启摄像头|必选|打开摄像头时 调用|
|ohos.permission.MIC ROPHONE|麦克风权限|用于用户视频通话交 互; 使用视频通话功能,需要 开启麦克风;|必选|打开麦克风时 调用|

第 4 页 16 页 

|ohos.permission.MED IA_LOCATION|媒体文件(例如照 片、视频)中包含 的地理位置信息 权限|用于用户选择照片; 针对媒体文件内部的地理 位置数据|必选|选择照片时调 用|
|---|---|---|---|---|
|ohos.permission.REA D_MEDIA|读取外部存储媒 体文件权限|用于用户选择照片; 允许应用读取用户外部存 储中的媒体文件信息|必选|选择照片时调 用|
|ohos.permission.WRI TE_MEDIA|读写外部存储媒 体文件权限|用于用户选择照片; 允许应用读写用户外部存 储中的媒体文件信息。|必选|选择照片时调 用|

#### 必选权限 

以下为必选权限,必须配置以下权限才能满足基本的音视频通话能力: 

"requestPermissions": [ 

{ "name": "ohos.permission.INTERNET" }, { "name": "ohos.permission.MICROPHONE", }, { "name": "ohos.permission.CAMERA", }, 

{ "name": "ohos.permission.MEDIA_LOCATION", }, { "name": "ohos.permission.READ_MEDIA", }, { "name": "ohos.permission.WRITE_MEDIA", 

} 

第 5 页 16 页 

] 

## 4. 业务组件API 说明 

调用前请保证业务参数的正确,SDK 会对参数进行必要的校验。 

## **4.1.** 组件启动接口说明 

## **4.1.1.** 接口说明 

**import** 

**('@ohos/AnyChatAIShuangLuCFSelf/src/main/ets/anychat/cfrecordsdk/pages/Pi ckIdCard')** 导入类名 

### **void start(Context context, String importJson, VideoRecordEvent event);** 

接口说明 **:** (1)组件开始调用接口; (2)组件调用接口类:BRCFRecordSDK. java; 返回值 **:** 无 示例代码 **:** _//_ 视频组件唤起调用接口 BRCFRecordSDK.getInstance().start(context, importJson, { _/** *_ 开始加载组件回调 _*/_ loadingStart( ) { } _/** *_ 结束加载组件回调 _*/_ loadingEnd() { } _/** *_ 异常错误回调 _*/_ 

第 6 页 16 页 

onBRCFRecordError(result:BusinessResult) { } _/** *_ 双录完成回调 _*/_ 

onBRCFRecordCompleted(result:BusinessResult) { 

} _/** *_ 活体检测完成回调 _*/_ 

onSelfFaceCaptureCompleted(result:BusinessResult) { } 

}); 

## **4.1.2.** 参数说明 

### 4.1.2.1. 接口参数简介 

|名称|类型|说明|是否必须|
|---|---|---|---|
|context|Context|上下文(集成页面)|是|
|importJs on|String(JSON格式)|智能双录业务组件外部调用业 务参数|是|
|event|BRCFRecordEve nt|回调通知事件,SDK调用过程中 异常或者结果回调给集成页 面,方便业务处理和异常收集。 代理回调说明|是 注意:不传递时, 登录的回调(成 功失败,以及完 成视频回调)将 无法获取|

### 4.1.2.2. 主要业务参数说明 

### importJson 业务参数对象参数说明: 

|名称|类型|最大 长度|说明|是否 必须|
|---|---|---|---|---|
|**1**、环境参数|||||
|loginIp|String|255|智能双录服务器登录地址|是|

第 7 页 16 页 

|名称|类型|最大 长度|说明|是否 必须|
|---|---|---|---|---|
|loginPort|String|255|智能双录服务器登录端口|是|
|loginAppId|String|50|智能双录服务器登录应用 appID|是|
|appId|String|-|应用app ID|是|
|busSerialNumber|String|-|业务流水号 (系统自身流水编号,可作为 系统关联)|否|
|loginSign|String|-|应用签名|否|
|loginTimeStamp|String|-|应用签名时间|否|
|strUserId|String|-|业务系统用户身份唯一标识 |否|
||||(签名登录需要传)||
|**2**、客户信息|||||
|custName|String|-|客户姓名|是|
|custID|String|-|客户号|是|
|custLevel|String|-|客户等级|是|
|custPhone|String|-|客户手机号|否|
|customerType|String|-|客户类型1-对私2-对公|否|
|socialType|String|-|证件类别|是|
|socialTypeName|String|-|证件类别描述|是|
|socialID|String|-|证件编号|是|
|socialAddress|String|-|证件地址|否|
|socialBeginTime|String|-|证件起始日期yyyyMMdd|否|
|socialEndTime|String|-|证件截止日期yyyyMMdd|否|
|custRiskLevel|String|-|客户风险等级|是|
|custRiskLevelName|String|-|客户风险等级描述|是|

最大 是否
名称 类型 说明
长度 必须
loginPort String 255 智能双录服务器登录端口 是
智能双录服务器登录应用
loginAppId String 50 是
appID
-
appId String 应用 app ID 是
业务流水号
busSerialNumber String - (系统自身流水编号,可作为 否
系统关联)
-
loginSign String 应用签名 否
-
loginTimeStamp String 应用签名时间 否
业务系统用户身份唯一标识
strUserId String - 否
(签名登录需要传)
2 、客户信息
custName String - 客户姓名 是
custID String - 客户号 是
custLevel String - 客户等级 是
custPhone String - 客户手机号 否
customerType String - 客户类型 1-对私 2-对公 否
-
socialType String 证件类别 是
-
socialTypeName String 证件类别描述 是
socialID String - 证件编号 是
socialAddress String - 证件地址 否
-
socialBeginTime String 证件起始日期 yyyyMMdd 否
socialEndTime String - 证件截止日期 yyyyMMdd 否
custRiskLevel String - 客户风险等级 是
custRiskLevelName String - 客户风险等级描述 是

第 8 页 16 页 

|名称|类型|最大 长度|说明|是否 必须|
|---|---|---|---|---|
|custCardNumber|String|-|客户卡号|是|
|**3**、产品信息相关|||||
|prodCode|String|-|产品代码|是|
|prodName|String|-|产品名称|是|
|productType|String|-|产品类型|是|
|prodTypeName|String|-|产品类型名称|是|
|productSubType|String|-|产品子类型|是|
|productSubTypeName|String|-|产品子类型名称|是|
|prodAmount|String|-|产品购买金额|是|
|prodRiskLevel|String|-|产品风险等级|是|
|prodRiskLevelName|String|-|产品风险等级描述|是|
|prodPushOrg|String|-|产品发行型机构|是|
|prodInvestmentTime|String|-|产品投资期限|否|
|prodInvestmentTimeN ame|String|-|产品投资期限描述|否|
|prodInvestmentType|String|-|产品投资品种|否|
|prodInvestmentTypeN ame|String|-|产品投资品种描述|否|
|prodMinAmount|String|-|产品最低购买金额|否|
|**4**、发起人信息相关|||||
|belongToAccount|String|-|发起人所属账号|是|
|belongToUserName|String|-|发起人所属账号名字|是|
|shuangluOrgCode|String|-|双录组织代码|是|
|companyCode|String|-|双录商户编码|是|
|**5**、系统渠道、业务信息|相关||||

第 9 页 16 页 

|名称|类型|最大 长度|说明|是否 必须|
|---|---|---|---|---|
|sysID|String|-|请求渠道|是|
|sysIDName|String|-|请求渠道描述|是|
|busType|String|-|双录业务类别|是|
|busSubType|String|-|双录业务子类别|是|
|**6**、其他信息|||||
|fileList|String|-|图片列表参数,用后台关联 绑定图片和人脸比对源:参 考样例|否|
|targetModel|TargetMo del|-|调用模块。参考说明|否|
|processBool|boolean|-|话术配置参:true 传入话 术,false服务器获取话术,默 认为false|否|
|extraParam|JSON 对 象|-|扩展参数(额外信息展示或 者特殊变量)|否|

### 4.1.2.3. fileList 对象参数说明 

|名称|类型|说明|是否必须|
|---|---|---|---|
|type|String|业务类型 1-身份证正面 2-身份证反面 3-客服照片|是|
|fileType|String|文件类型 2-fileBase64|是|
|fileBase64|String|图片base64数据|是|
|示例代码:||||

```arkts
let fileArray = []; let fileObject1 = {}; fileObject1["fileType"] = "2"; fileObject1["type"] = "0"; fileObject1["fileBase64"] = 图片 base64; fileArray[0] = fileObject1; 
```

第 10 页 16 页 

```arkts
let fileObject2 = {}; fileObject2 ["fileType"] = "2"; fileObject2 ["type"] = "1"; fileObject2 ["fileBase64"] = 图片 base64; fileArray[1] = fileObject2 ; JSON.stringify(fileArray) //转 json 字符 
```

### 4.1.2.4. targetModel 参数说明 

业务 SDK 包含多个功能模块,根据需求进行设置。部分模块功能可能需要授权,请确保授 权的有效性。功能模块按顺序为:OCR 证件识别 --> 活体检测 --> 录制提示 -->视频录制 --> 结束。设置该模块属性,即为选择启动开始的模块点。根据项目需求设置起点。 

|名称|类型|说明(**SDK** 模块起点)|是否 必须|
|---|---|---|---|
|TargetModelDefaul|int|默认(全流程)|否|
|TargetModelFc|int|活体检测-->录制提醒-->视频录制-->结束|否|
|TargetModelRecordResul t|int|录制提醒-->视频录制-->结束|否|
|TargetModelRecord|int|视频录制-->结束|否|

## **4.2.** 代理回调接口说明 

BRCFRecordSDKEvent 回调接口说明: 

|loadingStart();||开始加载组件回调|
|---|---|---|
|loadingEnd();||结束加载组件回调|
|onCFRecordComplet|ed(result:BusinessResult );|智能双录完成回调|
|onCFRecordError(r|esult:BusinessResult );|异常错误回调|
|onSelfFaceCapture|Completed(result:BusinessResult );|活体检测完成回调|
||BRBusinessResult 说明||
|aiSerialNo|String|智能双录流水号|
|errorCode|int|智能双录状态码,具体参 考下面错误码 详情|
|errorMsg|String|智能双录信息|
|videoFilePath|String|智能双录视频文件路径|

第 11 页 16 页 

### **5.** 视频组件混淆加固说明 

说明:混淆详细配置可参考示例工程 Demo obfuscation-rules.txt 混淆配置文件。
混淆说明:
在混淆配置文件中加入

# bairuitech
-keep class com.bairuitech.** {*;}
-keep class com.anychat.** {*;}
-keep class com.bairuitech.anychat.** {*;}
-keep class com.bairuitech.anychat.cfrecordsdk.** {*;}
6. 错误码
自定义异常错误码
错误码 错误描述
0 智能双录完成
2100001 用户主动退出
2100002 组件调用参数错误
2100003 业务参数错误
2100004 用户长时间无操作
2100006 转人工见证服务
操作错误码
错误码 错误描述
-2 操作失败
-1 connect to anychat server failed
0 success
系统错误码
错误码 错误描述
1 数据库错误
2 系统没有初始化
3 还未进入房间
4 没有足够内存

第 12 页 16 页 

错误码 错误描述
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
连接错误码
错误码 错误描述
100 连接服务器超时
101 与服务器的连接中断
102 连接服务器认证失败(服务器设置了认证密码)
103 域名解析失败
104 超过授权用户数
105 服务器功能受限制(演示模式)
106 只能在内网使用

第 13 页 16 页 

错误码 错误描述
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
进入房间错误码
错误码 错误描述
300 房间已被锁住,禁止进入
301 房间密码错误,禁止进入
302 房间已满员,不能进入
303 房间不存在
304 房间服务时间已到期
305 房主拒绝进入
306 房主不在,不能进入房间
307 不能进入房间
308 已经在房间里面了,本次进入房间请求忽略
309 不在房间中,对房间相关的 API 操作失败

第 14 页 16 页 

### 数据流错误码 

错误码 错误描述
350 过期数据包
351 相同的数据包
352 数据包丢失
353 数据包出错,帧序号存在误差
354 媒体流缓冲时间不足
视频呼叫错误码
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
排队错误码
错误码 错误描述
750 无效的队列 ID
751 准备接受服务,离开队列
sdk 错误码
错误码 错误描述
780 与服务器的 UDP 通信异常,流媒体服务将不能正常工作
781 SDK 加载 brMiscUtil.dll 动态库失败,部分功能将失效
782 SDK 加载 brMediaUtil.dll 动态库失败,部分功能将失效
783 SDK 加载 brMediaCore.dll 动态库失败,部分功能将失效
784 SDK 加载 brMediaShow.dll 动态库失败,部分功能将失效

第 15 页 16 页 

|视频设 错误 码|备错误码 错误描述|
|---|---|
|10001|打开视频设备失败|
|10002|未知视频输出格式|
|10003|驱动不支持VIDIOC_G_FMT|
|10004|驱动不支持VIDIOC_S_FMT|
|10005|驱动不支持VIDIOC_G_PARM|
|10006|驱动不支持VIDIOC_S_PARM|
|10007|驱动不支持VIDIOC_QUERYCAP|
|10008|当前设备非视频采集设备|
|10009|采集发生错误|
|10010|设备不支持mmap 和usermap 模式|
|10011|获取块物理地址失败|
|10012|物理地址映射到虚拟地址失败|
|10013|视频预缓存失败|
|10014|获取视频失败|
|10015|QBUF 失败|
|10016|VIDIOC_STREAMON 失败|
|10017|VIDIOC_STREAMOFF 失败|
|10018|当前摄像头可能被其他进程使用|
|10019|不支持视频采集模式|
|10020|请求的缓冲类型不支持, 或者VIDIOC_TRY_FMT 被使用和不支持这种缓 冲类型.|

错误
错误描述
码
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
10017 VIDIOC_STREAMOFF 失败
10018 当前摄像头可能被其他进程使用
10019 不支持视频采集模式
请求的缓冲类型不支持, 或者 VIDIOC_TRY_FMT 被使用和不支持这种缓
10020
冲类型.
音频设备错误码
错误码 错误描述
10500 打开音频设备失败
10501 请求 hwparams 失败
10502 设置 interleaved 模式失败
10503 设置 wBitsPerSample 失败
10504 设置 SamplesPerSec 失败
10505 设置 channels 失败

第 16 页 16 页 

错误码 错误描述
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
业务对象错误码
错误码 错误描述
100201 已经进入一个服务区域
100202 已经进入一个服务队列
APP ID 错误码
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
业务服务器错误码
错误码 错误描述

第 17 页 16 页 

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

第 18 页 16 页
