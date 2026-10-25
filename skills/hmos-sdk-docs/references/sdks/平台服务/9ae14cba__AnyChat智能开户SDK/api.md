# **SDK** 智能开户 **AnyChat** 接口文档使用指南 

广 州 佰 锐 网 络 科 技 有 限 公 司 **Guangzhou BaiRui Network Technology Co.,Ltd.** 

http://www.bairuitech.com http://www.anychat.cn 

|目录|
|---|
|1. 文档及集成说明........................................................................................................................... 3|
|2. 组件业务功能配置说明............................................................................................................... 3|
|2.1. SDK基础配置功能示例.................................................................................................... 4|
|2.2. SDK可选扩展配置功能示例............................................................................................4|
|3. 所需权限说明............................................................................................................................... 5|
|4. 接口说明........................................................................................................................................6|
|4.1. 组件开始调用接口............................................................................................................ 6|
|4.2. 接口参数说明.................................................................................................................... 7|
|4.2.1. 参数说明................................................................................................................. 7|
|4.2.2. 本地话术入参说明................................................................................................. 9|
|4.2.3. 服务器话术入参说明........................................................................................... 11|
|4.2.4. 回调接口说明....................................................................................................... 12|
|4.3. 活体检测环节公安校验结果传递说明..........................................................................13|
|4.4. 客服状态结果传递说明.................................................................................................. 13|
|5. 业务组件混淆加固说明............................................................................................................. 14|
|6. 错误码..........................................................................................................................................14|

1. 文档及集成说明 ........................................................................................................................... 3
2. 组件业务功能配置说明 ............................................................................................................... 3
2.1. SDK 基础配置功能示例 .................................................................................................... 4
2.2. SDK 可选扩展配置功能示例 ............................................................................................4
3. 所需权限说明 ............................................................................................................................... 5
4. 接口说明 ........................................................................................................................................6
4.1. 组件开始调用接口 ............................................................................................................ 6
4.2. 接口参数说明 .................................................................................................................... 7
4.2.1. 参数说明 ................................................................................................................. 7
4.2.2. 本地话术入参说明 ................................................................................................. 9
4.2.3. 服务器话术入参说明 ........................................................................................... 11
4.2.4. 回调接口说明 ....................................................................................................... 12
4.3. 活体检测环节公安校验结果传递说明 ..........................................................................13
4.4. 客服状态结果传递说明 .................................................................................................. 13
5. 业务组件混淆加固说明 ............................................................................................................. 14
6. 错误码 ..........................................................................................................................................14

第 2 页共 19 页 

### **1.** 文档及集成说明 

本文档为 AnyChat 智能开户 SDK 说明文档,为移动端集成开发提供指导。 组件详细调用方式及回调处理操作可参考示例工程 Demo。 

集成说明: AnyChat 智能开户SDK 提供动态库依赖包的方式供客户集成使用 开发工具:DevEco Studio 依赖库名称:AISelfRecordSDK.har 

#### 组件集成资料: 

**arm64-v8a anychat_sdk_harmony.har** 

#### **anychatvideobanksdk.har** 

|集成资料名称|说明及业务用途|集成必须|
|---|---|---|
|arm64-v8a|组件所需so库文件|是|
|anychat_sdk_harmony.har|组件所需sdk文件|是|
|anychatvideobanksdk.har|远程视频银行组件依赖包|是|

### 使用方式: 

- (1)在宿主工程 Module 节点下新建 libs 目录,并将 anychatagentsdk.har 包放在该目 录 

- (2) 在宿主工程 Module 的 oh-package.json5 文件 dependencies 节点添加依赖; "dependencies": { 

"@ohos/anychatagentsdk": "file:./libs/anychatagentsdk.har" 

} 

### **2.** 组件业务功能配置说明 

接入说明:包括基本功能和扩展功能 基本业务功能:音视频录制、视频上传 扩展业务功能:活体检测、实时质检等 

|功能区分|业务功能|功能介绍|配置方式|
|---|---|---|---|
|基本功能|音视频录制|提供实时录音录像|详见SDK基础配置功能示例|

第 3 页共 19 页 

|||相关功能||
|---|---|---|---|
||视频上传|提供视频上传功能|详见SDK基础配置功能示例|
|扩展功能|活体检测|提供活体检测功能|详见SDK可选扩展配置功能示例|
||实时质检|提供实时质检功能|详见SDK可选扩展配置功能示例|

### **2.1. SDK** 基础配置功能示例 

||基础 |配置信息说明 |
|---|---|---|
|信息类型|信息采集目的|配置说明|
|登录信息 用户信息|用于SDK进行连接登录 业务办理所需,如:根据用 户信息查询客户十要素信息|let componentJsonObject: object = new Object(); componentJsonObject[ComponentField.LOGIN_I P] = loginIp; // 集群登录Ip componentJsonObject[ComponentField.LOGIN_ PORT] = loginPort; // 集群登录端口 componentJsonObject[ComponentField.LOGIN_ APP_ID] = loginAppId; // 集群登录appId _//AnyChat_服务器登录扩展参数_(_必传_)_ componentJsonObject[ComponentField.CUST_ID ] = '12345';//客户id componentJsonObject[ComponentField.CUST_N AME] = "张三";//客户名称|
|业务模块|业务办理所需,用于指定客 户端业务办理的环节,如: 活体检测、音视频录制、视 频上传|componentJsonObject[ComponentField.TARGET _MODEL] = TargetModel.TargetModelRecord; // 业务开始选择步骤 targetModel=BUSINESS_STEP_THREE //音视频录制开始|

### **2.2. SDK** 可选扩展配置功能示例 

|信息类型|信息采集目的|配置说明|
|---|---|---|
|活体检测|提供活体检测功能|componentJsonObject[ComponentField.TARGET|

第 4 页共 19 页 

|||_MODEL] = TargetModel.TargetModelFc;|
|---|---|---|
|视频上传 环节|提供视频上传功能|componentJsonObject[ComponentField.TARGET _MODEL] = TargetModel.TargetModelRecord;|
|实时质检|用于坐席服务端展示接入 设备型号|let aiConfig: Array<object> = new Array(); let json1: object = new Object(); json1[ComponentField.CONFIG_NAME] = ComponentField.PARAM_FACE_IN_FRAME; json1[ComponentField.ENABLE] = 1; json1[ComponentField.CONFIG_DEC] = "在框检 测"; let content1: object = new Object(); content1[ComponentField.RATE] = "5" content1[ComponentField.FACE_NUM] = "1" content1[ComponentField.ALLOW_NO_PASS] = "3" content1[ComponentField.ALLOW_MORE_FACE_ NO_PASS] = "1" json1[ComponentField.CONFIG_CONTENT] = content1; aiConfig.push(json1); // 在框检测 componentJsonObject[ComponentField.AI_CONFI G] = JSON.stringify(aiConfig);|
|屏幕信息 (屏幕分 辨率、屏幕 方向、屏幕 常亮)、重 力传感器 信息|用于视频过程中,视频画面 的显示效果,屏幕不自动休 眠,提升用户体验;|_//_获取屏幕分辨率大小(默认获取) componentJsonObject[ComponentField.IS_GET_ SCREEN_SIZE] = true; _//_设置屏幕常亮(默认设置) componentJsonObject[ComponentField.IS_KEEP _SCREEN_ON] = true; _//_获取重力传感器信息(默认获取) componentJsonObject[ComponentField.IS_SENS OR_ENABLE] = true;|

_MODEL] = TargetModel.TargetModelFc;
视频上传 componentJsonObject[ComponentField.TARGET
提供视频上传功能
环节 _MODEL] = TargetModel.TargetModelRecord;
let aiConfig: Array<object> = new Array();
let json1: object = new Object();
json1[ComponentField.CONFIG_NAME] =
ComponentField.PARAM_FACE_IN_FRAME;
json1[ComponentField.ENABLE] = 1;
json1[ComponentField.CONFIG_DEC] = "在框检
测";
let content1: object = new Object();
content1[ComponentField.RATE] = "5"
content1[ComponentField.FACE_NUM] = "1"
用于坐席服务端展示接入
实时质检 content1[ComponentField.ALLOW_NO_PASS] =
设备型号
"3"
content1[ComponentField.ALLOW_MORE_FACE_
NO_PASS] = "1"
json1[ComponentField.CONFIG_CONTENT] =
content1;
aiConfig.push(json1); // 在框检测
componentJsonObject[ComponentField.AI_CONFI
G] = JSON.stringify(aiConfig);
// 获取屏幕分辨率大小(默认获取)
componentJsonObject[ComponentField.IS_GET_
屏幕信息
SCREEN_SIZE] = true;
(屏幕分
// 设置屏幕常亮(默认设置)
辨率、屏幕 用于视频过程中,视频画面
componentJsonObject[ComponentField.IS_KEEP
方向、屏幕 的显示效果,屏幕不自动休
_SCREEN_ON] = true;
常亮)、重 眠,提升用户体验;
// 获取重力传感器信息(默认获取)
力传感器
信息 componentJsonObject[ComponentField.IS_SENS
OR_ENABLE] = true;
3. 所需权限说明
module.json5 配置文件权限统一配置,请在宿主工程的 module.json5 配置文件中添加如

**module.json5** 配置文件权限统一配置,请在宿主工程的 **module.json5** 配置文件中添加如 下权限 **:** 

第 5 页共 19 页 

ohos.permission.INTERNET ohos.permission.CAMERA ohos.permission.MICROPHONE 

|权限名称|业务用途|是否必须|
|---|---|---|
|网络访问权限 ohos.permission.INTERNET|用于访问网络连接; 互联网网络请求;|是|
|相机权限 ohos.permission.CAMERA|用于用户视频通话交互**;** 如果没有该权限,本地摄像头将无法开 启,视频交互时坐席端将无法看到客户 端的画面; 使用场景:用于视频界面开启本地摄像 头操作;|是|
|麦克风权限 ohos.permission.MICROPHONE|用于用户视频通话交互; 如果没有该权限,视频交互时坐席端将 无法听到客户端的声音; 使用场景:用于视频界面开启本地麦克 风操作;|是|

## **4.** 接口说明 

## **4.1.** 组件开始调用接口 

void start(context:Context, model:string, event: VideoRecordEvent) : void 

接口说明 **:** 

(1)开始调用接口; (2)调用接口类:BRAiSelfRecordSDK . ts; 

返回值 **:** 

无 

示例代码 **:** 

//开始调用接口 

BRAiSelfRecordSDK.getInstance().start(getContext(), model, { //组件开始调用回调 

onLoginStart() { }, 

第 6 页共 19 页 

//组件调用登录成功回调 onLoginSuccess() { }, //异常错误回调 onSelfError(result: BusinessResult) { }, //录像完成回调 onSelfRecordCompleted(result: BusinessResult) { }, //人脸捕获完成回调 onSelfFaceCaptureCompleted(result: BusinessResult) { }, //活体检测完成回调 onSelfLiveDetectCompleted(result: BusinessResult) { }, 

//请求人工客服状态 onSelfAgentStatus() { } 

}); 

## **4.2.** 接口参数说明 

## **4.2.1.** 参数说明 

### 接口参数简介: 

|名称|类型|说明|是否必须|
|---|---|---|---|
|context|Context|上下文|是|
|model|string(JSON 格式)|开户业务组件外 部调用业务参数 对象|是|
|event|VideoRecordEvent|相关回调操作|是 注意:不传递 时,登录的回 调(成功失 败,以及完成 视频回调)将 无法获取|

第 7 页共 19 页 

### **model** 业务参数对象参数说明: 

|名称|类型|最 大 长 度|说明|是否 必须|
|---|---|---|---|---|
|nickName|string|20|登录用户昵称|是|
|strUserId|string|50|业务系统用户身份唯一 标识|否|
|loginIp|string|255|服务器登录地址|是|
|loginPort|string|255|服务器登录端口|是|
|loginAppId|string|50|应用ID|是|
|busSerialNumber|string|-|业务流水号 (商户系统自身业务流水 编号,作为本次业务办理 产生流水数据的唯一标 识)|否|
|openDigitalHuma n|number||1:数字人模式 0:非数 字人【默认值】|否|
|faceCompareImag e|string|-|人脸比对校验图片源(如 果有前置活体检测环节 则取活体捕获图片,则此 参数不需要传入)|否|
|showVideoTag|number|-|1:录制完成后标签数据 上传到服务器并返回文 件路径 0:不返回标签 数据【默认值】|否|
|onlineVerify|number|-|活体检测环节大头照是 否回调给应用层(1:是, 0:否)|否|
|liveDetectStage|number|-|活体检测环节退出组件 (1:是,0:否)|否|
|recordQuality|boolean|-|是否进行视频质检|否|
|targetModel|Busines sStepEn um|-|调用模块|否|

第 8 页共 19 页 

|名称|类型|最 大 长 度|说明|是否 必须|
|---|---|---|---|---|
|processBool|boolean|-|话术配置参:yes 传入话 术,no 服务器获取话术, 不传则为服务器获取话 术|否|
|dialogTimeOut|number|-|对话框超时时间|否|
|faceCompareImag e|string|-|人脸比对图片base64 字 符串|否|

targetModel 业务参数说明: 

|名称|类型|说明|是否必须|
|---|---|---|---|
|BUSINESS_STEP_TWO|numb er|活体检测(动作式检测)模块, 录制提醒模块,视频录制模块|否|
|BUSINESS_STEP_THR EE|numb er|录制提醒模块,视频录制模块|否|
|BUSINESS_STEP_FOU R|int|视频录制模块|否|

## **4.2.2.** 本地话术入参说明 

|qualityRuleJso nStr|JSONArray 格式的 string 类 型|话术流程配置参数,如果 使用AnyChat 话术配置 组件不需要传|否|
|---|---|---|---|
|aiConfig|JSONArray 格式的 string 类 型|ai 能力相关配置|当入参 processBool =1 本地话术 使用|

第 9 页共 19 页 

### qualityRuleJsonStr 话术参数包含字段说明 **:** 

|名称|类型|说明|是否必须|
|---|---|---|---|
|checkQuestion|string|话术问题|是|
|expectAnswer|string|当话术类型为问答、朗读类 型时问题的答案,必传|否|
|type|string|话术类型: 0:播报类型 1:问答类型 2:朗读类型|是|
|keywordList|ArrayLi st|朗读声明白名单 (数组元素为string 类型, 可配多值,使用英文逗号分 隔,见下方示例)|朗读声明环 节可选填|
|unExpectAnswer|string|问答环节黑名单|否|

### qualityRuleJsonStr 格式示例: 

" [{"checkQuestion":"请问您是本人吗?请回答是或否。","expectAnswer":"是,是的 ","type":1},{"checkQuestion":" 请您确认无误后,大声朗读以下内容: ","keywordList":["阅读,月度"],"expectAnswer":"我已知晓证券市场风险,并已阅读 且充分理解开户协议条款。 ","unExpectAnswer":" 不理解 , 没有 , 不知晓 ","type":2},{"checkQuestion":"您的开户环节已完毕,感谢您的配合和支持,再见。 ","type":0}]" 

### **aiconfigArr** 参数说明: 

|名称|类型||说明|
|---|---|---|---|
|configContent||Object|Ai能力配置|
|configDec||string|类型说明|
|configName||string|标识名|
|enable||string|是否开启|

### **configContent** 参数说明: 

|名称|类型||说明|
|---|---|---|---|
|rate||string|检测间隔时长|

第 10 页共 19 页 

faceNum string 人脸检测的人脸数
allowNoPass string 错误的最大次数
pass string 通过分数
aiConfig 格式示例:
"[{"configName":"paramFaceInFrame","configContent":{"rate":"5","faceNum":"1","
allowNoPass":"2"},"enable":1,"configDec":" 在 框 检 测
"},{"configName":"paramFaceCompare","configContent":{"pass":"60","allowNoPass
":"1"},"enable":1,"configDec":" 人 脸 比 对
"},{"configName":"paramFaceDistance","configContent":{},"enable":1,"configDec":
"人脸距离检测"}]"
4.2.3. 服务器话术入参说明
用于sdk 获取服务
器的ai 配置,当入
itemCode string 是
参processBool=0
服务器话术使用
custName string 客户姓名 否
custID string 客户号 否
prodType string 产品类型 否
prodCode string 产品代码 是
prodName string 产品名称 否
sysID string 请求渠道 否
sysIDName string 请求渠道描述 否
busType string 业务类别 是
busTypeName string 业务类别描述 否
扩展参数集合(主
要用于创建流水是
extraParam Object 否
否额外需要展示其
他参数信息,

第 11 页共 19 页 

4.2.4. 回调接口说明
VideoRecordEvent 回调接口说明 :
参数(类型):说
返回值 名称 说明
明
onSelfError(result: BusinessResult 异常错误回
void
BusinessResult) :回调结果 调
onSelfRecordCompleted(re BusinessResult 完成视频录
void
sult: BusinessResult) :执行结果 制回调
BusinessResult
onSelfFaceCaptureComplet : 回调结果
活体检测人
void ed (result: (result.faceP
脸捕获成功
BusinessResult) icture:base64
格式正面照片)
活体检测环
节完成
(liveDete
onSelfLiveDetectComplete BusinessResult
void ctStage 设
d(result: BusinessResult) :执行结果
置了1 即在
这里退出了
组件)
通知查询客
void onSelfAgentStatus()
服状态
BusinessResult 参数简介:
名称 类型 说明
aiSerialNo string 双录流水号
aiStatus number 状态码
aiMsg string 状态信息
videoFilePa
string 视频文件路径
th

第 12 页共 19 页 

|videoPrevie wFrame tagsFilePat h|string string|录像首帧base64 标签的服务器文件地址|
|---|---|---|

## **4.3.** 活体检测环节公安校验结果传递说明 

开启公安校验后,将校验结果返回给组件的接口说明(入参 onlineVerify=1 的 情况下): 

|返回值|方法名称|参数(类型):说 明|说明|
|---|---|---|---|
|void|notifyOnlineVerifyResult|boolean isPass: 回调结果 extra:其他参 数,可为null|业务层发送 人脸校验结 果|

示例: 

BRAiSelfRecordSDK.getInstance().notifyOnlineVerifyResult(true, ""); 

说明:组件收到业务层的校验结果后,如果校验结果为通过,则继续进行下一步, 如果结果为不通过,则为退出组件并返回响应错误码。如果开启了 onlineVerify,但超过10s 没有传递结果给组件,则为校验超时并退出组件; 

## **4.4.** 客服状态结果传递说明 

收到 onSelfAgentStatus 回调时查询客服状态,通过以下方法传递到组件: 

|返回值|方法名称|参数(类型):说 明|说明|
|---|---|---|---|
|void|notifyAgentStatus|isAgentOnline: boolean:回调结 果|客服是否在 线|

示例: 

BRAiSelfRecordSDK.getInstance().notifyAgentStatus(true); 

说明:组件收到业务层的校验结果后,根据客服状态是否显示转人工客服按钮; 

第 13 页共 19 页 

5. 业务组件混淆加固说明
说明:混淆详细配置可参考示例工程Demo proguard-project.txt 混淆配置文件。
混淆说明:
6. 错误码
业务组件调用结果状态码
状态码 结果描述
0 智能双录完成
2100001 用户主动退出
2100002 组件调用参数错误
2100003 业务参数错误
2100006 转人工见证服务
操作错误码
错误码 错误描述
-2 操作失败
-1 连接 AnyChat 服务器失败
0 成功
系统错误码
错误码 错误描述
1 数据库错误
2 系统没有初始化
3 还未进入房间
4 没有足够内存
5 出现异常
6 操作被取消

第 14 页共 19 页 

错误码 错误描述
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
107 版本太旧,不允许连接
108 Socket 出错

第 15 页共 19 页 

错误码 错误描述
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
数据流错误码

第 16 页共 19 页 

错误码 错误描述
350 过期数据包
351 相同的数据包
352 数据包丢失
353 数据包出错,帧序号存在误差
354 媒体流缓冲时间不足
SDK 错误码
错误码 错误描述
780 与服务器的 UDP 通信异常,流媒体服务将不能正常工作
781 SDK 加载 brMiscUtil.dll 动态库失败,部分功能将失效
782 SDK 加载 brMediaUtil.dll 动态库失败,部分功能将失效
783 SDK 加载 brMediaCore.dll 动态库失败,部分功能将失效
784 SDK 加载 brMediaShow.dll 动态库失败,部分功能将失效
视频设备错误码
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

第 17 页共 19 页 

错误码 错误描述
10017 VIDIOC_STREAMOFF 失败
10018 当前摄像头可能被其他进程使用
10019 不支持视频采集模式
请求的缓冲类型不支持, 或者 VIDIOC_TRY_FMT 被使用和不支持
10020
这种缓冲类型.
音频设备错误码
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
业务对象错误码
错误码 错误描述
100201 已经进入一个服务区域
100202 已经进入一个服务队列

第 18 页共 19 页 

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

第 19 页共 19 页
