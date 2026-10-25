AnyChat 虚拟营业厅 SDK 

# 接口文档使用指南 

(版本: V4.3.0 ) 

# 广州佰锐网络科技有限公司 

Guangzhou BaiRui Network Technology Co.,Ltd. http://www.bairuitech.com http://www.anychat.cn 2025 年 10 月 

目录 

1. 文档及集成说明 2 

组件集成资料: 2 

1.1. 集成方式说明 2 

2. 组件所需权限及敏感信息说明 3 

2.1. 所需权限说明 3 

2.2. 敏感信息说明 4 

3. 视频组件接口说明 4 

# 3.1. 组件开始调用接口 4 

- 3.2. 远程视频银行组件层与业务层信息交互回调接口说明 10 

# 4. 错误码 16 

# 文档及集成说明 

本文档为远程视频银行组件移动端集成说明文档,为移动端集成开发 提供指导。组件详细调用方式及回调处理操作可参考示例工程 Demo 。 

集成说明: AnyChat 远程视频银行组件提供 har 包方式供集成使用 ; 开发工具: DevEco Studio 组件集成资料: 

arm64-v8a 

anychat_sdk_harmony.har 

anychatvideobanksdk.har 

集成资料名称 

说明及业务用途 

集成必须 

arm64-v8a 

组件所需 so 库文件 

是 

anychat_sdk_harmony.har 

组件所需 sdk 文件 

是 

anychatvideobanksdk.har 

# 远程视频银行组件依赖包 

是 

# 集成方式说明 

将 anychatvideobanksdk.har 、 anychat_sdk_harmony.har 、 arm64v8a 库文件放在宿主工程的 libs 目录下 ; 

选择宿主工程的【 oh-package.json5 】文件,将远程视频银行组件依 赖添加到宿主工程中; 

"dependencies": { "anychat_sdk_harmony": "file:./libs/ anychat_sdk_harmony.har", "anychatvideobanksdk": "file:./libs/ anychatvideobanksdk.har" } 

组件所需权限及敏感信息说明 

# 所需权限说明 

在宿主工程的 module.json5 文件中统一配置权限,请在 module.json5 中添加如下权限 : 

ohos.permission.INTERNET 

ohos.permission.CAMERA 

ohos.permission.MICROPHONE 

权限名称 

业务用途 

是否必须 

# 网络访问权限 

ohos.permission.INTERNET 

用于访问网络连接:互联网网络请求; 

使用场景:用于正常执行网络请求及响应、正常进行音视频交互等; 

是 

# 相机权限 

ohos.permission.CAMERA 

用于视频通话交互 ; 

如果没有该权限,本地摄像头将无法开启,视频交互时坐席端将无法 看到客户端的画面; 

使用场景:用于视频界面开启本地摄像头操作; 

是 

麦克风权限 

ohos.permission.MICROPHONE 

用于视频通话交互; 

如果没有该权限,视频交互时坐席端将无法听到客户端的声音; 使用场景:用于视频界面开启本地麦克风操作; 

是 

敏感信息说明 

信息类型 

使用信息 

使用场景 

# 收集方式 

# 设备信息 

设备型号、系统版本号、 IP 信息 

用于客户端日志分析,如分析对应设备机型无法正常业务交互等; SDK 直接获取 

个人信息 

用户信息:姓名、手机号登 

业务场景办理所需,用于坐席端用户信息展示 

集成商调用时提供 

视频组件接口说明 

组件开始调用接口 

start(context: Context, model: BRTransferModel, event: BRVideoRecordEvent); 

# 接口说明 : 

远程视频银行组件视频银行组件开始调用接口; 

远程视频银行组件调用接口类: AnyChatVideoBankSDK. ts ; 

( 3 )详细调用方式可参考示例 Demo ; 

返回值 : 

无 

示例代码 : 

// 视频银行服务大厅业务调用接口 

AnyChatVideoBankSDK.getInstance().start(getContext(), transferModel, { // 组件开始调用回调 ( 用于业务层开始 loading 展示 ) onAnyChatLoginStart() { }, // 组件调用登录成功 ( 用于业务层结束 loading 展示 ) onAnyChatLoginSuccess() { }, // 异常错误回调 onAnyChatClientError(result: BRResultMode) { }, // 业务完成回调 onAnyChatClientCompleted(result: BRResultMode) { }, 

// 执行向业务层发起业务回调请求 onBusinessRequestEvent(businessType: string, requestType: BRBusinessRequestType, requestStr: string){ } 

}); 

详细接口参数说明 接口参数简介: 

名称 

类型 

说明 

是否必须 

context 

Context 

上下文 

是 

model 

BRTransferModel 

组件外部调用业务参数对象 

是 

event 

# BRVideoRecordEvent 

结果回调操作 ( 详细说明请参考本文档 3.1.5 章节 ) 

是 

BRTransferModel 业务参数对象说明 : 

名称 类型 说明 是否必须 用户参数信息 

userName string 用户姓名 是 

custId String 客户号 否 

idCardNumber 

string 用户身份证号码 是 

idCardTypeKey 

# string 

证件类型字典定义标识 ( 非必传默认为 idCardType) 

是 

idCardTypeName 

string 

证件类型字典名称 如:居民身份证 是 

idCardTypeValue 

string 证件类型字典值 如: 110001 

是 

phoneNumber 

string 用户手机号 是 登录参数信息 

loginIp 

string 服务器登录地址 

是 

loginPort 

string 

服务器登录端口 

是 

loginAppId 

string 

商户应用 ID 

(商户唯一标识,由佰锐科技提供) 是 

loginSign string 

AnyChat 签名登录签名字符串 

否 

loginStrUserId 

string 

AnyChat 签名登录用户 id 

否 

loginTimeStamp 

number 

AnyChat 签名登录时间戳 

否 

loginStrParam 

# string 

服务器登录自定义参数( json 字符串) ( 详细说明请参考本文档 3.1.2 章节 ) 

是 

业务参数信息 

integratorName 

string 

渠道名称 

是 

integratorCode 

string 渠道编码 

是 

expansion 

string 

扩展参数( json 字符串) 

( 详细说明请参考本文档 3.1.3 章节 ) 否 

aiReportExtraParam 

string 

智能播报变量配置参数( json 字符串) ( 详细说明请参考本文档 3.1.4 章节 ) 

# 否 

# 其他参数信息 

isShowRemoteFullScreen 

boolean 

# 坐席画面是否全屏展示控制 

( 默认 true 全屏展示 ) 

否 

appVersion 

string 

手机银行版本 

否 

deviceModel 

string 

设备型号 

否 

deviceId 

string 

设备标识 

否 

服务器登录自定义参数说明 数据格式 ( 标准 json 字符串 ): 

{ 

"callTradeNo": "20221104161DEC38F0186634C4B9EDBC88D7202AE7", 

"sysCode": "VIRTUALHALL" 

} 

名称 

类型 

说明 是否必须 

callTradeNo 

string 

通话流水号(业务初始化接口返回) 是 

sysCode 

string 

系统编号(业务初始化接口返回) 

是 

示例代码: 

//AnyChat 服务器登录扩展参数 ( 必传 ) let loginStrObject = {}; loginStrObject['callTradeNo'] = callTradeNo; loginStrObject['sysCode'] = sysCode; transferModel.loginStrParam = JSON.stringify(loginStrObject); 

扩展参数说明 

# 说明: 

扩展参数信息,可用于传递客户当前位置信息、备注信息展示等; 

# 数据格式 ( 标准 json 字符串 ): 

{ 

"address": " 广州市天河区科韵路 ", 

"remarks": [ 

{ 

"groupData": [ 

{ 

"key": "beizhu", 

"name": " 备注信息 ", 

"value": " 支持展示支行添加客户名单时填写的备注信息 " 

} 

], 

"groupName": " 备注信息 " 

} 

] 

} 

名称 

类型 说明 

是否必须 

address 

string 

位置信息,用于业务流水信息展示客户位置信息 

否 

remarks 

Array 

扩展分组展示信息 

否 

remarks 

groupName 

string 

分组展示名称 ( 如:备注信息、财产信息等 ) 否 

groupData 

Array 

分组展示具体内容 

否 

groupData 

key 

string 

属性标识 

是 

name 

string 

# 属性名称 

# 是 

value 

string 

属性值 

是 

# 示例代码: 

```arkts
let remarksArray: Array<object> = new Array; let remarksObject = {}; remarksObject["groupName"] = " 备注信息 "; let groupDataArray: Array<object> = new Array; let object1 = {}; object1["key"] = "beizhu"; object1["name"] = " 备注信息 "; object1["value"] = " 支持展示支行添加客户名单时填写的备注信息 "; groupDataArray.push(object1); remarksObject["groupData"] = groupDataArray; remarksArray.push(remarksObject); let expansionObject = {} expansionObject["address"] = " 广州市天河区 科韵路 "; expansionObject["remarks"] = remarksArray; // 设置扩展 参数信息 transferModel.expansion = JSON.stringify(expansionObject); 
```

# 智能播报变量动态配置参数说明 

# 说明: 

智能播报变量扩展参数信息,可用于传递智能播放话术配置的变量信 息,包含变量 key 、变量 value 信息; 

# 数据格式 ( 标准 json 字符串 ): 

{ 

"age": "18", 

"amount": "10 万 " 

} 

# 示例代码: 

```arkts
let extraParamJsonObject: object = new Object(); extraParamJsonObject['age'] = '18'; extraParamJsonObject['amount'] = '10 万 '; 
```

let aiReportParam = JSON.stringify(extraParamJsonObject); 

// 智能播报动态配置参数 

transferModel.aiReportExtraParam = aiReportParam; 

BRVideoRecordEvent 结果回调说明 

BRVideoRecordEvent 结果回调接口说明 : 

返回值 

名称 

参数 ( 类型 ): 说明 

说明 

备注 

void 

onAnyChatLoginStart() 

无 

组件开始调用回调 ( 用于业务层开始 loading 展示 ) 

void 

onAnyChatLoginSuccess() 

无 

组件调用登录成功回调 ( 用于业务层结束 loading 展示 ) 

void 

onAnyChatClientError(result: BRResultMode) 

result(BRResultMode ): 执行结果 异常错误回调 

result.errCode: 状态码 result.errMsg: 描述信息 

void 

onAnyChatClientCompleted(result: BRResultMode) 

result(BRResultMode ): 执行结果 

结果回调 

result.errCode: 状态码 

- 0 表示本次业务办理结束; 

result.errMsg: 描述信息 

void 

onBusinessRequestEvent(uiContext: UIContext, 

businessType: string, requestType: BRBusinessRequestType, 

requestStr: string); 

uiContext :上下文 

businessType :当前执行请求的业务类型 

requestType :当前请求类型 

requestStr :当前请求详细数据信息 (json 字符 ) 

# 用于业务层获取组件内部业务操作请求明 

uiContext :上下文 

businessType :当前执行请求的业务类型 

requestType :当前请求类型 

requestStr :当前请求详细数据信息 

# 远程视频银行组件层与业务层信息交互回调接口说明 

# 业务层获取组件内部请求回调操作说明 

onBusinessRequestEvent(uiContext: UIContext,businessType: string, requestType: BRBusinessRequestType, requestStr: string); 

# 示例代码 : 

# // 视频银行服务大厅业务开始调用接口 

AnyChatVideoBankSDK.getInstance().start(getContext(), transferModel, { // 组件开始调用回调 ( 用于业务层开始 loading 展示 ) onAnyChatLoginStart() { }, // 组件调用登录成功 ( 用于业务层结束 loading 展示 ) onAnyChatLoginSuccess() { }, // 异常错误回调 onAnyChatClientError(result: BRResultMode) { }, // 双录完成回调 onAnyChatClientCompleted(result: BRResultMode) { }, // 执行向业 务层发起业务回调请求 onBusinessRequestEvent(uiContext: UIContext,businessType: string, requestType: 

BRBusinessRequestType, requestStr: string) { switch (requestType) { 

case BRBusinessRequestType.TradePswInput: // 交易密码输入请求 break; case BRBusinessRequestType.PswSet: // 密码设置请求 break; case BRBusinessRequestType.BusinessCancel: // 坐席取消业务 ( 用于 业务层处理弹窗展示销毁处理等 ) 

break; } } }); 

接口参数简介: 

名称 

类型 

说明 

是否必须 

businessType 

string 

当前执行请求的业务场景类型 

是 

requestType 

BRBusinessRequestType 

# 请求类型枚举类 

是 

requestStr 

string 

# 请求参数信息 

否 

BRBusinessRequestType 请求类型枚举值说明 

TradePswInput 

BRBusinessRequestType 

# 交易密码输入验证请求 

是 

PswSet 

BRBusinessRequestType 

密码设置请求 

是 

BusinessCancel 

BRBusinessRequestType 

坐席取消业务办理 

是 

密码验证环节交互流程简要说明: 

密码重置环节交互流程简要说明: 

# 交易密码输入验证请求 

requestType 请求类型定义字段说明 

名称 

类型 

说明 

是否必须 

TradePswInput 

BRBusinessRequestType 

# 交易密码输入验证请求 

是 

# requestStr 组件内部请求详细数据信息说明 

userAccountNo 

string 

银行卡号 

是 

tradeNo 

string 

视频银行流水号 

是 

requestStr 交易密码输入验证示例数据: 

# 如: 

# 密码设置请求 

requestType 请求类型定义字段说明 

名称 

类型 

说明 

是否必须 

PswSet 

BRBusinessRequestType 

密码设置请求 

是 

requestStr 组件内部请求详细数据信息说明 

userAccountNo 

string 

银行卡号 

是 

tradeNo 

string 

视频银行流水号 

是 

requestStr 密码设置输入示例数据: 

# 如: 

坐席取消业务办理 

说明: 

主要用于在业务办理过程中,业务层弹窗 ( 如交易密码弹窗、密码设 置弹窗等 ) 正在展示时,坐席执行取消业务办理时,组件通知业务层 执行弹窗的隐藏、销毁处理; 

requestType 请求类型定义字段说明 

名称 

类型 

说明 

是否必须 

BusinessCancel 

BRBusinessRequestType 

坐席取消业务办理 

是 

requestStr 组件内部请求详细数据信息说明 

tradeNo 

string 

视频银行流水号 

否 

# 业务层向组件内发送响应结果状态说明 

void sendBRBusinessResponse(String businessType, BRBusinessRequestType requestType, String responseStr) 

说明: 

此回调接口可用于业务层向组件内部告知对应请求的响应结果状态, 如交易密码输 

入状态 ( 输入完成 | 取消输入 ) 、密码设置输入状态 ( 输入完成 | 取消输入 ) 等; 

示例代码: 

# // 业务层向组件内部发送业务请求结果 

接口参数简介: 

名称 

类型 

说明 

是否必须 businessType string 当前执行对应请求响应的业务类型 否 

requestType BRBusinessRequestType 

请求类型 

是 

responseStr 

string 当前响应详细数据信息 (json 字符 ) 

是 

发送交易密码输入验证请求结果详细说明 requestType 请求类型定义字段说明 

名称 

# 类型 

说明 

是否必须 

TradePswInput 

BRBusinessRequestType 

# 交易密码输入验证请求 

# 是 

# responseStr 请求业务层响应数据信息说明 

status 

number 

相关状态 

是 

pswCipherText 

string 

密码密文数据 

否 

# responseStr 交易密码输入验证结果示例数据: 

如:输入完成: {"status":0,"pswCipherText": " 密码密文数据 "} 如:输入取消: {"status":1} 

# 发送密码设置请求结果详细说明 

requestType 请求类型定义字段说明 

名称 

类型 

说明 

是否必须 

PswSet 

BRBusinessRequestType 

密码设置请求 

是 

responseStr 请求业务层响应数据信息说明 

status 

number 

相关状态 

是 

pswCipherText 

string 

密码密文数据 

否 

responseStr 交易密码输入示例数据: 

如:密码设置输入完成: {"status":0,"pswCipherText": " 密码密文数 据 "} 

如:密码设置取消输入: {"status":1} 

# 错误码 

自定义异常错误码 

错误码 

错误描述 

0 业务办理结束 

100901 组件调用相关参数校验异常提示 100902 服务队列获取失败 100903 营业厅信息获取失败 100904 进入营业厅失败 100905 

进入队列失败 100906 

进线参数错误 100907 进入房间失败 

100908 坐席转接数据异常 

100909 

坐席转接进线参数错误 

100911 

用户主动挂断 

100912 

视频会话异常 

100913 

用户取消呼叫 100914 用户取消排队 100915 坐席服务异常 

100920 

本次业务办理失败 

操作错误码 

错误码 

错误描述 

-2 

操作失败 

-1 

connect to anychat server failed 

0 

success 

系统错误码 

错误码 

错误描述 

1 

数据库错误 

2 

系统没有初始化 

3 

还未进入房间 

4 

没有足够内存 

5 

出现异常 

6 

操作被取消 

7 

通信协议出错 

8 

会话不存在 

9 

# 数据不存在 

10 

数据已经存在 

11 

无效 GUID 

12 

资源被回收 

13 

资源被占用 

14 

Json 解析出错 

15 

对象被删除 

16 

会话已存在 

17 

会话没有初始化 

20 

函数功能不允许 

21 函数参数错误 

22 

# 设备打开错误或设备未被安装 

23 

# 没有足够的资源 

24 

指定的格式不能被显示设备所支持 

25 

指定的 IP 地址不是有效的组播地址 

26 

不支持多实例运行 

27 

文件签名验证失败 

28 

授权验证失败 

连接错误码 错误码 错误描述 

100 

连接服务器超时 

101 

与服务器的连接中断 

102 

连接服务器认证失败(服务器设置了认证密码) 

103 

域名解析失败 

104 

超过授权用户数 

105 

服务器功能受限制(演示模式) 

106 

只能在内网使用 

107 

版本太旧,不允许连接 

108 

Socket 出错 

109 

设备连接限制(没有授权) 

110 

服务已被暂停 

111 

热备服务器不支持连接(主服务在启动状态) 

112 

授权用户数校验出错,可能内存被修改 

113 

IP 被禁止连接 

114 

连接类型错误,服务器不支持当前类型的连接 

115 

服务器 IP 地址不正确 

116 

连接被主动关闭 

117 

没有获取到服务器列表 

118 

连接负载均衡服务器超时 

119 

服务器不在工作状态 

120 

服务器不在线 

121 

网络带宽受限 

122 

网络流量不足 

123 

不支持 IPv6 Only 网络 

124 

没有 Master 服务器在线 

125 

没有上报工作状态 

进入房间错误码 

错误码 

错误描述 

300 

房间已被锁住,禁止进入 301 房间密码错误,禁止进入 302 房间已满员,不能进入 303 房间不存在 304 房间服务时间已到期 

305 

房主拒绝进入 

306 

房主不在,不能进入房间 

307 

不能进入房间 

308 

已经在房间里面了,本次进入房间请求忽略 

309 

不在房间中,对房间相关的 API 操作失败 数据流错误码 

错误码 

错误描述 

350 

过期数据包 

351 

相同的数据包 

352 

数据包丢失 

353 

数据包出错,帧序号存在误差 

354 

媒体流缓冲时间不足 视频呼叫错误码 错误码 错误描述 

440 

正在通话中 

500 

# 说话时间太长,请休息一下 

501 

有高级别用户需要发言,请休息一下 100101 源用户主动放弃会话 100102 目标用户不在线 100103 目标用户忙 100104 目标用户拒绝会话 100105 会话请求超时 100106 网络断线 100107 用户不在呼叫状态 排队错误码 错误码 错误描述 750 无效的队列 ID 

751 

准备接受服务,离开队列 

AnyChat 虚拟营业厅 SDK 错误码 

错误码 

错误描述 

780 

与服务器的 UDP 通信异常,流媒体服务将不能正常工作 

781 

AnyChat 虚拟营业厅 SDK 加载 brMiscUtil.dll 动态库失败,部分功能将 失效 782 

AnyChat 虚拟营业厅 SDK 加载 brMediaUtil.dll 动态库失败,部分功能 将失效 783 

AnyChat 虚拟营业厅 SDK 加载 brMediaCore.dll 动态库失败,部分功能 将失效 

784 

AnyChat 虚拟营业厅 SDK 加载 brMediaShow.dll 动态库失败,部分功 能将失效 

视频设备错误码 

错误码 

错误描述 

10001 

打开视频设备失败 

10002 

# 未知视频输出格式 

10003 

驱动不支持 VIDIOC_G_FMT 

10004 

驱动不支持 VIDIOC_S_FMT 

10005 

驱动不支持 VIDIOC_G_PARM 10006 

驱动不支持 VIDIOC_S_PARM 

10007 

驱动不支持 VIDIOC_QUERYCAP 

10008 

当前设备非视频采集设备 

10009 

采集发生错误 

10010 

设备不支持 mmap 和 usermap 模式 

10011 

获取块物理地址失败 

10012 

物理地址映射到虚拟地址失败 

10013 

视频预缓存失败 

10014 

获取视频失败 

10015 

QBUF 失败 

10016 

VIDIOC_STREAMON 失败 

10017 

VIDIOC_STREAMOFF 失败 

10018 

当前摄像头可能被其他进程使用 

10019 

不支持视频采集模式 

10020 

请求的缓冲类型不支持 , 或者 VIDIOC_TRY_FMT 被使用和不支持这种 缓冲类型 . 音频设备错误码 

错误码 

错误描述 

10500 

打开音频设备失败 

10501 

请求 hwparams 失败 

10502 

设置 interleaved 模式失败 

10503 

设置 wBitsPerSample 失败 10504 

设置 SamplesPerSec 失败 10505 设置 channels 失败 10506 

设置 periods 失败 10507 设置缓存尺寸失败 

10508 

函数 :snd_pcm_hw_params 调用失败 

10509 

设置 rebuffer time 失败 

10510 

设置 rebuffer frames 失败 

10511 

获取 period time 失败 

10512 

获取 period frame 失败 

10513 

请求 swparams 失败 

10514 

设置 start threshoid 失败 10515 

设置 start avail min 失败 10516 

函数 snd_pcm_prepare 调用失败 10517 函数 read 调用失败 

30000 

创建会话失败 业务对象错误码 错误码 错误描述 100201 已经进入一个服务区域 100202 已经进入一个服务队列 APP ID 错误码 

# 错误码 

错误描述 

100300 

默认的应用 ID (空)不被支持 100301 

应用登录需要签名 100302 

应用签名校验失败 

100303 

应用 ID 不存在 

100304 应用 ID 被系统锁定 

100305 

应用 ID 与当前服务不匹配 

100306 

连接的服务器不是云平台地址 

100307 

应用所对应的计费服务器不足 

100308 

应用计费模式改变 业务服务器错误码 

错误码 

错误描述 

100701 无效参数 100702 应用 ID 不存在 100703 Body 无效 100704 签名验证失败 100705 签名时间戳无效 100706 可用内存不够 100707 出现异常 100708 通信协议出错 100709 业务服务器执行任务超时 100710 文件不存在
