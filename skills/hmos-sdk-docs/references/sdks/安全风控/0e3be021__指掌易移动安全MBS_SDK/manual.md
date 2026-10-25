# 移动安全MBSSDK 集成指南

# 业务SDK 集成指南(鸿蒙)

1

移动安全MBS SDK 集成指南(鸿蒙)

# 版权申明

### 本文档版权归指掌易科技有限公司(以下简称“指掌易”)所有,并保留一切权利,

### 非经本公司书面许可任何单位和个人不得擅自摘抄、复制本书内容的部分或者全部,并不得

### 以任何形式进行传播。对应本手册出现的其他公司的商标,产品标识和商品名称,由各自权

### 利人拥有。除非另有约定,本手册仅作为使用指导,本手册中的所有陈述、信息和建议,不

### 构成任何明示和暗示的担保。如需获取最新手册请联系指掌易科技有限公司产品部。

# 免责声明

### 本文档仅提供阶段性信息,所含内容可根据产品的实际情况随时更新,恕不另行通知。

### 如因文档使用不当造成的直接或间接损失,本公司不承担任何责任。

# 联系我们

### 网址:www.zhizhangyi.com

### 服务电话:4008987798

### 地址:北京市朝阳区北苑路58 号航空科技大厦7 层

| 2 |  |
|---|---|

移动安全MBS SDK 集成指南(鸿蒙)

# 目

# 录

产品概述........................................................................................................................................ 5

2 SDK 内容说明.................................................................................................................................. 6

2.1 SDK 压缩包说明...................................................................................................................6

2.2 SDK 权限...............................................................................................................................7

2.3集成文档使用概述............................................................................................................. 8

2.3.1排障阶段说明..........................................................................................................8

3 SDK 集成指南.................................................................................................................................. 9

3.1快速入门............................................................................................................................. 9

3.1.1开发准备.................................................................................................................. 9

3.1.2 Demo 使用说明........................................................................................................ 9

3.1.3启动时序图............................................................................................................12

3.2典型场景........................................................................................................................... 14

3.2.1 SDP+MOS 场景........................................................................................................14

3.2.1.1单次认证.....................................................................................................14

3.2.1.1.1用户名密码认证..............................................................................14

3.2.1.1.2第三方令牌认证..............................................................................21

3.2.1.1.3应用密钥认证..................................................................................28

3.2.1.1.4短信认证..........................................................................................34

3.2.1.2二次认证.....................................................................................................42

3.2.1.2.1用户名密码+短信认证....................................................................42

3.2.1.2.2用户名密码+第三方令牌认证........................................................51

3.3流程自检........................................................................................................................... 59

3.3.1是否正确处理了登录............................................................................................59

3.3.1.1注意事项.....................................................................................................59

3.3.1.2测试步骤.....................................................................................................60

3.3.1.3期望结果.....................................................................................................60

| 3 |  |
|---|---|

移动安全MBS SDK 集成指南(鸿蒙)

3.3.1.4失败排查.....................................................................................................60

3.3.2是否正确处理了免密认证....................................................................................60

3.3.2.1注意事项.....................................................................................................60

3.3.2.2测试步骤.....................................................................................................61

3.3.2.3期望结果.....................................................................................................61

3.3.2.4失败排查.....................................................................................................61

3.3.3是否正确处理了注销............................................................................................62

3.3.3.1注意事项.....................................................................................................62

3.3.3.2测试步骤.....................................................................................................62

3.3.3.3期望结果.....................................................................................................62

3.3.3.4失败排查.....................................................................................................62

3.3.4是否正确处理了监听............................................................................................62

3.3.4.1注意事项.....................................................................................................62

3.3.4.2测试步骤.....................................................................................................63

3.3.4.3期望结果.....................................................................................................63

3.3.4.4失败排查.....................................................................................................63

常见问题汇总.............................................................................................................................. 63

4.1如何获取SDK 日志?.......................................................................................................63

4.2集成过程中出现崩溃,应该如何处理?.......................................................................64

4.3应用能否获取SDK 版本号?...........................................................................................64

4.4 SDK 登录阶段,出现"103接收超时,服务器无回应"提示,排查步骤?....................64

4.5 SDK 登录阶段,出现"1004没有可访问的资源"的提示,排查步骤?.............................64

4.6登录认证成功后,部分资源无法访问,排查步骤?...................................................65

4.7 SDK 是否有断链重连机制,集成应用是否需要关注?................................................ 65

4.8 SDP 通道状态监听setListener(IUUSDKCallback callback)如何使用?........................... 65

4.9应用能否获取当前SDP 隧道连接状态?...................................................................... 66

4.10 SDK 认证成功后,是否会代理集成SDK 应用的所有网络请求?...............................66

4.11同一个帐号可以在多少个设备上同时登录使用?.....................................................66

| 4 |  |
|---|---|

移动安全MBS SDK 集成指南(鸿蒙)

# 1

# 产品概述

### 指掌易的移动端安全接入SDK 解决方案,从安全与效率双方面助力企业移动办公的转

### 型与优化。通过全方位的安全防护措施和高效的办公管理能力,帮助企业在保障数据和系统

### 安全的前提下,充分利用移动办公的优势,提高企业整体运营效率。

### 该方案主要包含两个部分:移动安全管理(MOS)和零信任安全网关(SDP)。

### 移动安全管理通过身份认证、数据加密、设备管理、和应用安全管理等措施,确保企业

### 移动办公的每一个环节都受到严密保护。

###  

### 身份安全:通过严格的身份认证和访问控制机制,确保只有经过授权的用户才能访问

### 企业资源,防止身份盗用和未经授权的访问。

###  

### 数据安全:通过全流程的数据加密,保护数据在收集、存储、传输等过程中的安全,

### 防止敏感信息泄露。

###  

### 设备安全:监控和管理移动设备,确保设备符合企业的安全标准,通过擦除设备、禁

### 用设备等管理措施防范设备丢失或被盗后可能带来的安全威胁。

###  

### 应用安全:对企业内部和外部应用进行DLP 防护及安全加固,防止应用漏洞带来的安

### 全风险,上报应用风险行为,保障企业业务系统的安全运行。

### 零信任安全网关解决方案基于零信任模型实现,以基于身份的细粒度访问代替广泛的网

### 络接入,为用户提供安全可靠的访问业务系统方案。

###  

### 可信认证:对包括用户、设备、网络、时间、位置等多因素的身份信息进行验证,确认

### 身份的可信度和可靠性。

| 5 |  |
|---|---|

移动安全MBS SDK 集成指南(鸿蒙)

###  

### 最小化授权:基于位置、时间、安全状态和一些自定义属性实施访问控制管理。通过用

### 户身份、终端类型、设备属性、接入方式、接入位置、接入时间来感知用户的访问上下

### 文行为,并动态调整用户信任级别。

###  

### 服务隐藏:基于UDP 协议的SPA 单包授权认证机制,默认“拒绝一切”请求,仅在接

### 收到合法的认证数据包的情况下,对用户身份进行认证。

###  

### 隧道通信安全:通过高强度密钥安全、防中间人攻击、防重放攻击,保证隧道通信安全。

###  

### 动态信任评估:进行持续的自适应风险与信任评估,信任度和风险级别会随着时间和空

### 间发生变化,根据安全等级的要求、网络环境等因素,达到信任和风险的平衡。

### 其中零信任安全网关(SDP)支持两种模式:应用级模式、设备级模式,这两种模式各有优

### 缺点,对比见下表所示,项目使用时根据需求选择不同模式,然后在SDK 打包平台获

# 2

# SDK 内容说明

# 2.1SDK 压缩包说明

| 图1 SDK 解压出来的文件 |  |  |
|---|---|---|
|  |  |  |
|  | 1. sdkdemo: SDK demo 实例源码 |  |
|  | 2. doc: SDK 集成说明文档 |  |
|  | 3. sdk: SDK 库文件 |  |
|  | 图2 SDK 库文件 |  |
|  |  |  |
| 1. libs: SDK 的har 库 |  |  |
|  | 图3 SDK har 库文件 |  |
| 6 |  |  |

移动安全MBS SDK 集成指南(鸿蒙)

# 2.2SDK 权限

|  | 描述应用集成SDK 时,不同场景集成SDK 需要添加的权限,包括:类型,权限名,获 |  |  |  |  |  |  |  |  |
|---|---|---|---|---|---|---|---|---|---|
|  | 取时机,获取原因 等 |  |  |  |  |  |  |  |  |
|  | 设备权限 |  | 申请目的 |  |  | 申请授权方 式 | 是否可关 闭 |  |  |
|  | 网络请求权限 |  | 请求网络数据(ohos.permission.INTERNET) |  |  |  | 否 | 否 |  |
|  | 获取网络信息权 |  |  | 用于网关能力获取设备网络信息 |  |  | 否 | 否 |  |
|  | 限 |  |  | (ohos.permission.GET NETWORK INFO) _ _ |  |  |  |  |  |
|  | 获取wifi 信息权 |  |  | 用于网关能力获取wifi 信息 |  |  |  |  |  |
|  | 限 |  |  | (ohos.permission.GET WIFI INFO) _ _ |  |  |  |  |  |
|  | 关键资产存储权 |  |  | 用于存储设备ID |  |  | 否 | 否 |  |
|  | 限 |  |  | (ohos.permission.STORE PERSISTENT DATA) _ _ |  |  |  |  |  |
|  |  |  |  |  |  |  |  |  |  |

| 7 |  |
|---|---|

移动安全MBS SDK 集成指南(鸿蒙)

# 2.3集成文档使用概述

## 2.3.1排障阶段说明

| 8 |  |
|---|---|

移动安全MBS SDK 集成指南(鸿蒙)

# 3

# SDK 集成指南

# 3.1快速入门

## 3.1.1开发准备

### 1.编译环境

### 开发工具:DevEco Studio 5.0.1 及以上

### API 版本:5.0.1(api 13)及以上

### 2.运行环境

### 支持HarmonyOS NEXT 5.0.0.110 及以上设备

### 3.导入SDK 到工程

### 拷贝SDK 压缩包中的har 文件到项目的libs 路径

//har 文件路径

```
/sdk/libs/@zzy-unmossdk.har
//har 文件拷贝到工程的目标目录,以SDKDemo 工程为例
/entry/libs/@zzy-unmossdk.har
```

### 添加SDK 依赖

在entry 下的oh-package.json5 里面添加如下依赖:

```
dependencies{
"@zzy/unmossdk":"file:./libs/@zzy-unmossdk.har"
}
```

## 3.1.2Demo 使用说明

| 1. 业务场景描述 |  |
|---|---|
| Demo 里面包含了文档中典型场景的实现,下面介绍各个场景在Demo 中的关键代码 |  |
| SDK 初始化 |  |
| Demo 中示例代码如下: |  |
| 9 |  |

移动安全MBS SDK 集成指南(鸿蒙)

|  | export default class EntryAbility extends UIAbility { |  |
|---|---|---|
|  | onCreate(want: Want, launchParam: AbilityConstant.LaunchParam): void { |  |
|  | let args: Map<string, object> = new Map(); |  |
|  | UUMos.initWithOnCreate(this.context,args) |  |
|  | } |  |
|  |  |  |
|  | } |  |
|  | 沙箱初始化 |  |
|  | 在AbilityStage 的onCreate 中调用。 |  |
|  | AbilityStage 的实现方法请参考官方文档: |  |
|  | https://developer.huawei.com/consumer/cn/doc/harmonyos-guides/abilitystage |  |
|  | -0000001774119982 |  |
|  | 调用实例: |  |
|  | export default class MyAbilityStage extends AbilityStage { |  |
|  | onCreate(): void { |  |
|  | // 应用的HAP 在首次加载的时,为该Module 初始化操作 |  |
|  | let args: Map<string, object> = new Map(); |  |
|  | UUMos.initSandbox(this,args); |  |
|  | } |  |
|  | onAcceptWant(want: Want): string { |  |
|  | // 仅specified 模式下触发 |  |
|  | return 'MyAbilityStage'; |  |
|  | } |  |
|  | SDP+MOS 场景 |  |
|  | 单次认证 |  |
|  | 用户名密码认证场景 |  |
|  | Demo 中示例代码如下: |  |
| @Entry |  |  |
| @Component |  |  |
| @Preview |  |  |
| export struct UserPasswordLoginPage { |  |  |
|  |  |  |
|  | 10 |  |

移动安全MBS SDK 集成指南(鸿蒙)

| } |  |  |
|---|---|---|
|  | 短信认证场景 |  |
|  | Demo 中示例代码如下: |  |
|  | @Entry |  |
|  | @Component |  |
|  | @Preview |  |
|  | export struct SMSCodeLoginPage { |  |
|  | } |  |
|  | 远程单品证场景 |  |
|  | Demo 中示例代码如下: |  |
| @Entry |  |  |
| @Component |  |  |
| @Preview |  |  |
| export struct AppKeyLoginPage { |  |  |
| } |  |  |
|  | 第三方令牌证场景 |  |
|  | Demo 中示例代码如下: |  |
|  | @Entry |  |
|  | @Component |  |
|  | @Preview |  |
|  | export struct TokenLoginPage { |  |
|  | } |  |
|  | 二次认证 |  |
|  | 用户名密码+短信认证场景 |  |
|  | Demo 中示例代码如下: |  |
|  | @Entry |  |
|  | @Component |  |
|  | @Preview |  |
|  | export struct UserAndSmsCodeSecondaryLoginPage { |  |
|  | } |  |
|  | 用户名密码+第三方令牌认证场景 |  |

| 11 |  |
|---|---|

移动安全MBS SDK 集成指南(鸿蒙)

| Demo 中示例代码如下: |  |
|---|---|
| @Entry |  |
| @Component |  |
| @Preview |  |
| export struct UserAndSmsCodeSecondaryLoginPage { |  |
| } |  |

## 3.1.3启动时序图

### 首次安装启动流程

### 1:app实现UIAbility的onCreate接口,在onCreate中调用SDK的接口,调用方法:

### UUMos.initWithOnCreate(this.context,args)

| 12 |  |
|---|---|

移动安全MBS SDK 集成指南(鸿蒙)

### 2:app实现AbilityStage的onCreate 接口,在onCreate 中调用SDK的接口,调用方法:

### UUMos.initSandbox(this,args)

### 3:调用初始化接口初始化登录服务器的IP、端口、租户登信息,接口方法:UUMos.init(),

### 初始化接口需要在UIAbility onCreate 的主进程中执行,具体调用示例参考初始化接口说明

### 3:根据APP 具体场景选择登录模式,标准场景使用账号+密码登录,如果要选择其他方式

### 需要结合APP 场景制定登录鉴权方案,接口方法:UUMos.login(),接口调用和参数传递参考

### 登录接口说明

### 冷启动流程

### 1:app实现UIAbility的onCreate接口,在onCreate中调用SDK的接口,调用方法:

### UUMos.initWithOnCreate(this.context,args)

### 2:app实现AbilityStage的onCreate 接口,在onCreate 中调用SDK的接口,调用方法:

| 13 |  |
|---|---|

移动安全MBS SDK 集成指南(鸿蒙)

### UUMos.initSandbox(this,args)

### 3:调用初始化接口初始化登录服务器的IP、端口、租户登信息,接口方法:UUMos.init(),

### 初始化接口需要在UIAbility onCreate 的主进程中执行,具体调用示例参考初始化接口说明

### 3:调用checkSign()接口检测是否已经登录过,如果已经登录过调用sign()免密认证接口进行

### 免密认证流程成功后就可以进去到APP,如果失败根据错误码走不通的流程。如果未登录跳

### 转到登录界面走登录流程,接口调用和参数传递参考登录接口说明

# 3.2典型场景

## 3.2.1SDP+MOS 场景

### 3.2.1.1单次认证

### 3.2.1.1.1用户名密码认证

### 3.2.1.1.1.1场景简介

### 管理端已从第三方同步账号及密码

### SDK 登录

### SDK 用户名/密码进行登录,鉴权成功后管理端生成token 并返回

### 3.2.1.1.1.2前置步骤

### 在实际集成之前,要确保已按【开发环境构建】执行

### 在管理端创建测试用户,并配置好用户名密码认证

| 14 |  |
|---|---|

移动安全MBS SDK 集成指南(鸿蒙)

### 3.2.1.1.1.3流程图

### 3.2.1.1.1.4集成步骤

### 初始化SDK

### 注意:

### SDK 接口都需要在SDK 初始化后才能调用。

### 初始化SDK 主要是完成SDK 沙箱能力和SDK 配置信息初始化,沙箱能力初始化接口需

要在AbilityStage 的onCreate 中调用,配置信息初始化建议在UIAbility 的onCreate 中调用

### 示例代码如下:

| export default class MyAbilityStage extends AbilityStage { |  |
|---|---|
| onCreate(): void { |  |
| // 应用的HAP 在首次加载的时,为该Module 初始化操作 |  |
| let args: Map<string, object> = new Map(); |  |
| UUMos.initSandbox(this,args); |  |
| } |  |
| 15 |  |

移动安全MBS SDK 集成指南(鸿蒙)

```
onAcceptWant(want:Want):string{
//仅specified 模式下触发
return'MyAbilityStage';
}
}
export defaultclassEntryAbilityextendsUIAbility{
onCreate(want:Want,launchParam:AbilityConstant.LaunchParam):void{
letargs:Map<string,Object>=newMap();
UUMos.initWithOnCreate(this.context,args)
this.initUUSdk(this.context)
}
}
initUUSdk(context:Context){
letargs:Map<string,Object>=newMap();
//MOS 服务器地址,String 类型,必填
args.set(UUInitParamsKey.UU_INIT_MBS_URL,
"https://172.16.30.37:9070");
//MOS 服务器租户信息,/String 类型,必填
args.set(UUInitParamsKey.UU_INIT_MBS_ORGCODE,"zzydemo");
```

//网关配置

//安全网关服务器地址,支持主机名和IP 地,String 类型

```
args.set(UUInitParamsKey.UU_INIT_SDP_HOST,"172.16.30.82");
args.set(UUInitParamsKey.UU_INIT_SDP_PORT,8888);//SDP 端口
letinitBack=newUUInitBack();
letres=UUMos.init(context,args,initBack);
//0:调用成功,-1:调用失败。
if(res==0){//0:调用成功
}else{
//-1:调用失败。
}
}
```

### 首次登录

### 应用登录页,点击登录按钮后,先调用login 接口使用用户填写账号/密码登录,登录

### 成功后再执行应用登录

### 实例参考UserPasswordLoginPage

### 示例代码如下:

```
letargs:Map<string,Object>=newMap();
```

//登陆类型,UUAuthType 枚举int 类型,支持类型介绍参考UUAuthType 枚举定义

| 16 |  |
|---|---|

移动安全MBS SDK 集成指南(鸿蒙)

| args.set(UULoginParamsKey.UU_LOGIN_LOGINTYPE, |  |
|---|---|
| UUAuthType.AUTH_TYPE_PASSWORD); |  |
| //登录用户名,String 类型,必填 |  |
| args.set(UULoginParamsKey.UU_LOGIN_LOGINNAME, mUserName); |  |
| //登录密码,String 类型,必填 |  |
| args.set(UULoginParamsKey.UU_LOGIN_PASSWORD, mPassword); |  |
| //0:仅启动mos,1:仅启动sdp ,2:启用MOS 和SDP,SDP 前置 必填 |  |
| args.set(UULoginParamsKey.UU_LOGIN_LOGINMODE, |  |
| UUSDKMode.UU_MODE_SDP_SANDBOX); |  |
| UUMos.login(args, { |  |
| handleSDKEvent: (map: Map<string, Object>): void => { |  |
| if (map != null) { |  |
| let resultCode = |  |
| UUMosUtils.getMapNumber(UUCallbackKey.UU_KEY_KMOSCALLBACKERRORCODE, map, |  |
| -1); |  |
| let message = |  |
| UUMosUtils.getMapString(UUCallbackKey.UU_KEY_KMOSCALLBACKERROR, map, ""); |  |
| let suggest: UUCallbackSuggest = |  |
| UUMosUtils.getMapEnumSuggest(UUCallbackKey.UU_KEY_KMOSCALLBACKSUGGEST, map, |  |
| UUCallbackSuggest.UU_CALLBACK_SUGGEST_FINISH); |  |
| if (suggest == UUCallbackSuggest.UU_CALLBACK_SUGGEST_TIP) { |  |
| //提示错误信息 message |  |
| promptAction.showToast({ |  |
| message: "登录失败:" + message + ":" + resultCode, |  |
| duration: 2000 |  |
| }) |  |
| } else if (suggest == UUCallbackSuggest.UU_CALLBACK_SUGGEST_FINISH) { |  |
| promptAction.showToast({message: "登录成功", duration: 2000 |  |
| }) |  |
| router.replaceUrl({url:'pages/MainPage'}).then(()=>{ |  |
| console.info('testTag', `MainPage .`); |  |
| }).catch((err:BusinessError)=>{ |  |
| console.error('testTag',"MainPage ") |  |
| }) |  |
| } else if (suggest == UUCallbackSuggest.UU_CALLBACK_SUGGEST_SAFECONTROL) |  |
| { |  |
| let authType: UUSafeControlType = |  |
|  |  |
| UUMosUtils.getMapEnumSuggestSafeControlType(UUCallbackKey.UU_KEY_KMOSSAFECO |  |
| NTROLTYPE, map, |  |
| UUSafeControlType.SAFE_CONTROL_MODIFY_PASSWORD); |  |
| if (authType == UUSafeControlType.SAFE_CONTROL_MODIFY_PASSWORD) { |  |
| } |  |
| 17 |  |

移动安全MBS SDK 集成指南(鸿蒙)

```
}
}
});
```

### 免密认证

### 调用sign 接口(如应用闪屏页),成功后再执行应用自身网络业务请求

### 示例代码如下:

| //检测是否支持免密登录 |  |  |
|---|---|---|
| if(UUMos.checkSign() == 0) |  |  |
| { //设置SDP 通道状态监听 |  |  |
| let args:Map<string, Object> = new Map(); |  |  |
| UUMos.sign(args, { |  |  |
| handleSDKEvent:(map:Map<string, Object>):void=>{ |  |  |
| if(map != null) |  |  |
| { |  |  |
| //错误码 |  |  |
| let resultCode = |  |  |
| UUMosUtils.getMapNumber(UUCallbackKey.UU_KEY_KMOSCALLBACKERRORCODE,map,-1); |  |  |
| //错误码对应信息描述 |  |  |
| let message = UUMosUtils.getMapString(UUCallbackKey.UU_KEY_KMOSCALLBACKERROR, |  |  |
| map,""); |  |  |
| //返回接收到状态码后的下一步执行动作,枚举型 |  |  |
| let suggest:UUCallbackSuggest = |  |  |
| UUMosUtils.getMapEnumSuggest(UUCallbackKey.UU_KEY_KMOSCALLBACKSUGGEST,map,UU |  |  |
| CallbackSuggest.UU_CALLBACK_SUGGEST_FINISH); |  |  |
| if(suggest == UUCallbackSuggest.UU_CALLBACK_SUGGEST_TIP) |  |  |
| { |  |  |
| //弹出错误码 |  |  |
| let msg:string = message + ":" + resultCode; |  |  |
| promptAction.showToast({message: msg,duration: 2000}) |  |  |
| router.replaceUrl({url:'pages/SelectSceneLoginPage'}).then(()=>{ |  |  |
| }).catch((err:BusinessError)=>{ }) |  |  |
| } |  |  |
| else if(suggest == UUCallbackSuggest.UU_CALLBACK_SUGGEST_FINISH) |  |  |
| { |  |  |
| //调用成功,流程已完成,跳转到APP 主界面 |  |  |
| router.replaceUrl({url:'pages/MainPage'}).then(()=>{ |  |  |
| console.info('testTag', `Succeeded .`); |  |  |
| }).catch((err:BusinessError)=>{ |  |  |
| console.error('testTag',"Failed ") |  |  |
| }) |  |  |
| } |  |  |
|  | 18 |  |

移动安全MBS SDK 集成指南(鸿蒙)

```
elseif(suggest==UUCallbackSuggest.UU_CALLBACK_SUGGEST_RELOGIN)
{
//应用需要返回登录页面,重新执行SDK 登录流程
router.replaceUrl({url:'pages/SelectSceneLoginPage'}).then(()=>{
}).catch((err:BusinessError)=>{
})
}
elseif(suggest==UUCallbackSuggest.UU_CALLBACK_SUGGEST_ERASE)
{
//管理员执行了设备擦除策略,SDK 将主动执行擦除应用数据并关闭应用
}
elseif(suggest==UUCallbackSuggest.UU_CALLBACK_SUGGEST_RETRY)
{
//由于网络原因导致签到失败,建议弹框提示然后重试
promptAction.showToast({message:message,duration:2000})
}}
}});}
```

### 登出登录

### 先调用应用自身登出,成功后再调用logout 登出接口(如:应用中点击登出按钮)

### 示例代码如下:

```
letargs:Map<string,Object>=newMap();
UUMos.logout(args,{
handleSDKEvent:(map:Map<string,Object>):void=>{
//错误码
letresultCode=
UUMosUtils.getMapNumber(UUCallbackKey.UU_KEY_KMOSCALLBACKERRORCODE,map,-1);
//错误码对应信息描述
letmessage=
UUMosUtils.getMapString(UUCallbackKey.UU_KEY_KMOSCALLBACKERROR,map,"");
//返回接收到状态码后的下一步执行动作,枚举型
letsuggest:UUCallbackSuggest=
UUMosUtils.getMapEnumSuggest(UUCallbackKey.UU_KEY_KMOSCALLBACKSUGGEST,map,
UUCallbackSuggest.UU_CALLBACK_SUGGEST_FINISH);
if(suggest==UUCallbackSuggest.UU_CALLBACK_SUGGEST_FINISH){
//退回到登录界面
}
}
})
```

### 监听处理

### 应用激活/切至前台

| 19 |  |
|---|---|

移动安全MBS SDK 集成指南(鸿蒙)

### 应用有激活立即发送网络请求

### 建议调用获取SDP 通道状态方法,通道开启后再调用网络请求

### 应用无激活立即发送网络请求

### SDP 在应用激活后,会主动检测并做自动重连,正常1s 内可恢复

### 隧道状态监听

### 隧达关闭

### 注册SDP 通道状态监听接口,收到错误码后若应用需要处理这些错误码,则根据

### 应用实际的业务需求,给出用户提示/登出/联系管理员等

### 隧道打开

### 一般无需关注

### 隧道重连机制

### SDK 会在应用切换至前台,网络切换等情况下主动监听网络状态,自动重连,保证

### 隧道连通性,应用一般无需关注

### 示例代码如下:

| //SDP 通道状态监听 |  |  |
|---|---|---|
| UUMos.setListener({ |  |  |
| handleSDKEvent: (map: Map<string, Object>): void => { |  |  |
| if (map != null) { |  |  |
| //错误码 |  |  |
| let resultCode = |  |  |
| UUMosUtils.getMapNumber(UUCallbackKey.UU_KEY_KMOSCALLBACKERRORCODE, map, -1); |  |  |
| //错误码对应信息描述 |  |  |
| let message = |  |  |
| UUMosUtils.getMapString(UUCallbackKey.UU_KEY_KMOSCALLBACKERROR, map, ""); |  |  |
| //返回接收到状态码后的下一步执行动作,枚举型 |  |  |
| let suggest: UUCallbackSuggest = |  |  |
| UUMosUtils.getMapEnumSuggest(UUCallbackKey.UU_KEY_KMOSCALLBACKSUGGEST, map, |  |  |
| UUCallbackSuggest.UU_CALLBACK_SUGGEST_FINISH); |  |  |
| if (suggest == UUCallbackSuggest.UU_CALLBACK_SUGGEST_TIP) { |  |  |
| //提示错误信息 message |  |  |
| } else if (suggest == UUCallbackSuggest.UU_CALLBACK_SUGGEST_RELOGIN) { |  |  |
| //需要退回到登录界面重新登录 |  |  |
| } else if (suggest == UUCallbackSuggest.UU_CALLBACK_SUGGEST_ERASE) { |  |  |
| //设备擦除 |  |  |
| } |  |  |
|  | 20 |  |

移动安全MBS SDK 集成指南(鸿蒙)

```
});
```

### 3.2.1.1.2第三方令牌认证

### 3.2.1.1.2.1场景简介

### 标准登录模式无法满足,需要服务端开发插件对接第三方业务系统

### 服务端插件:指掌易插件开发人员开发,包括:1:同第三方业务系统对接2:同客户端token

### 认证接口对接,需要定义登录数据格式

### 集成方登录参数:服务端插件开发人员告知集成方数据传递格式

### SDK 登录

### 根据服务端插件开发人员告知token 认证数据格式,进行登录

### 集成应用登录

### 根据项目实际需求确定

### 3.2.1.1.2.2前置步骤

### 在实际集成之前,要确保已按【开发环境构建】执行

### 协调服务端插件开发人员,对接第三方业务系统,定义token 认证数据格式

| 21 |  |
|---|---|

移动安全MBS SDK 集成指南(鸿蒙)

### 3.2.1.1.2.3流程图

### 3.2.1.1.2.4集成步骤

### 初始化SDK

### 注意:

### SDK 接口都需要在SDK 初始化后才能调用。

### 初始化SDK 主要是完成SDK 沙箱能力和SDK 配置信息初始化,沙箱能力初始化接口需

要在AbilityStage 的onCreate 中调用,配置信息初始化建议在UIAbility 的onCreate 中调用

### 示例代码如下:

| export default class MyAbilityStage extends AbilityStage { |  |
|---|---|
| onCreate(): void { |  |
| // 应用的HAP 在首次加载的时,为该Module 初始化操作 |  |
| let args: Map<string, object> = new Map(); |  |
| 22 |  |

移动安全MBS SDK 集成指南(鸿蒙)

```
UUMos.initSandbox(this,args);
}
onAcceptWant(want:Want):string{
//仅specified 模式下触发
return'MyAbilityStage';
}
}
export defaultclassEntryAbilityextendsUIAbility{
onCreate(want:Want,launchParam:AbilityConstant.LaunchParam):void{
letargs:Map<string,Object>=newMap();
UUMos.initWithOnCreate(this.context,args)
this.initUUSdk(this.context)
}
}
initUUSdk(context:Context){
letargs:Map<string,Object>=newMap();
//MOS 服务器地址,String 类型,必填
args.set(UUInitParamsKey.UU_INIT_MBS_URL,
"https://172.16.30.37:9070");
//MOS 服务器租户信息,/String 类型,必填
args.set(UUInitParamsKey.UU_INIT_MBS_ORGCODE,"zzydemo");
```

//网关配置

//安全网关服务器地址,支持主机名和IP 地,String 类型

```
args.set(UUInitParamsKey.UU_INIT_SDP_HOST,"172.16.30.82");
args.set(UUInitParamsKey.UU_INIT_SDP_PORT,8888);//SDP 端口
letinitBack=newUUInitBack();
letres=UUMos.init(context,args,initBack);
//0:调用成功,-1:调用失败。
if(res==0){//0:调用成功
}else{
//-1:调用失败。
}
}
```

### 首次登录

### 应用登录页,点击登录按钮后,根据协商定义的token 认证数据格式组装数据,登录成

### 功后再执行应用登录

### 实例参考TokenLoginPage

### 示例代码如下:

| 23 |  |
|---|---|

移动安全MBS SDK 集成指南(鸿蒙)

| let args: Map<string, Object> = new Map(); |  |  |
|---|---|---|
| //第三方token |  |  |
| let mPassword:string = "第三方认证token";; |  |  |
| //登陆类型,UUAuthType 枚举int 类型,支持类型介绍参考UUAuthType 枚举定义 |  |  |
| args.set(UULoginParamsKey.UU LOGIN LOGINTYPE,UUAuthType.AUTH TYPE TOKEN); _ _ _ _ |  |  |
| //登录用户名,String 类型,必填 |  |  |
| args.set(UULoginParamsKey.UU LOGIN LOGINNAME,userName); _ _ |  |  |
| //登录密码,String 类型,必填 |  |  |
| args.set(UULoginParamsKey.UU LOGIN PASSWORD,mPassword); _ _ |  |  |
| //2:启用MOS 和SDP 必填 |  |  |
| args.set(UULoginParamsKey.UU LOGIN LOGINMODE,UUSDKMode.UU MODE SDP SANDBOX); _ _ _ _ _ |  |  |
|  |  |  |
| //设置SDP 通道状态监听 |  |  |
| UUMos.login(args, { |  |  |
| handleSDKEvent: (map: Map<string, Object>): void => { |  |  |
| if (map) { |  |  |
| //错误码 |  |  |
| let resultCode = |  |  |
| UUMosUtils.getMapNumber(UUCallbackKey.UU KEY KMOSCALLBACKERRORCODE, map, -1); _ _ |  |  |
| //错误码对应信息描述 |  |  |
| let message = UUMosUtils.getMapString(UUCallbackKey.UU KEY KMOSCALLBACKERROR, _ _ |  |  |
| map, ""); |  |  |
| //返回接收到状态码后的下一步执行动作,枚举型 |  |  |
| let suggest = |  |  |
| UUMosUtils.getMapEnumSuggest(UUCallbackKey.UU KEY KMOSCALLBACKSUGGEST, map, _ _ |  |  |
| UUCallbackSuggest.UU CALLBACK SUGGEST FINISH); _ _ _ |  |  |
| if (suggest == UUCallbackSuggest.UU CALLBACK SUGGEST TIP) { _ _ _ |  |  |
| //提示错误信息 message |  |  |
| promptAction.showToast({ |  |  |
| message: "登录失败:" + message + ":" + resultCode, |  |  |
| duration: 2000 |  |  |
| }) |  |  |
| } else if (suggest == UUCallbackSuggest.UU CALLBACK SUGGEST FINISH) { _ _ _ |  |  |
| //认证成功,认证结束进入主应用 |  |  |
| promptAction.showToast({ |  |  |
| message: "登录成功", |  |  |
| duration: 2000 |  |  |
| }) |  |  |
| router.replaceUrl({ url: 'pages/MainPage' }).then(() => { |  |  |
| console.info('testTag', `MainPage .`); |  |  |
| }).catch((err: BusinessError) => { |  |  |
| console.error('testTag', "MainPage ") |  |  |
| }) |  |  |
| } |  |  |
|  | 24 |  |

移动安全MBS SDK 集成指南(鸿蒙)

}

}

});

### 免密认证

### 调用sign 接口(如应用闪屏页),成功后再执行应用自身网络业务请求

### 示例代码如下:

| //检测是否支持免密登录 |  |  |
|---|---|---|
| if(UUMos.checkSign() == 0) |  |  |
| { //设置SDP 通道状态监听 |  |  |
| let args:Map<string, Object> = new Map(); |  |  |
| UUMos.sign(args, { |  |  |
| handleSDKEvent:(map:Map<string, Object>):void=>{ |  |  |
| if(map != null) |  |  |
| { |  |  |
| //错误码 |  |  |
| let resultCode = |  |  |
| UUMosUtils.getMapNumber(UUCallbackKey.UU_KEY_KMOSCALLBACKERRORCODE,map,-1); |  |  |
| //错误码对应信息描述 |  |  |
| let message = UUMosUtils.getMapString(UUCallbackKey.UU_KEY_KMOSCALLBACKERROR, |  |  |
| map,""); |  |  |
| //返回接收到状态码后的下一步执行动作,枚举型 |  |  |
| let suggest:UUCallbackSuggest = |  |  |
| UUMosUtils.getMapEnumSuggest(UUCallbackKey.UU_KEY_KMOSCALLBACKSUGGEST,map,UU |  |  |
| CallbackSuggest.UU_CALLBACK_SUGGEST_FINISH); |  |  |
| if(suggest == UUCallbackSuggest.UU_CALLBACK_SUGGEST_TIP) |  |  |
| { |  |  |
| //弹出错误码 |  |  |
| let msg:string = message + ":" + resultCode; |  |  |
| promptAction.showToast({message: msg,duration: 2000}) |  |  |
| router.replaceUrl({url:'pages/SelectSceneLoginPage'}).then(()=>{ |  |  |
| }).catch((err:BusinessError)=>{ }) |  |  |
| } |  |  |
| else if(suggest == UUCallbackSuggest.UU_CALLBACK_SUGGEST_FINISH) |  |  |
| { |  |  |
| //调用成功,流程已完成,跳转到APP 主界面 |  |  |
| router.replaceUrl({url:'pages/MainPage'}).then(()=>{ |  |  |
| console.info('testTag', `Succeeded .`); |  |  |
| }).catch((err:BusinessError)=>{ |  |  |
| console.error('testTag',"Failed ") |  |  |
| }) |  |  |
| } |  |  |
| else if(suggest == UUCallbackSuggest.UU_CALLBACK_SUGGEST_RELOGIN) |  |  |
|  | 25 |  |

移动安全MBS SDK 集成指南(鸿蒙)

```
{
//应用需要返回登录页面,重新执行SDK 登录流程
router.replaceUrl({url:'pages/SelectSceneLoginPage'}).then(()=>{
}).catch((err:BusinessError)=>{
})
}
elseif(suggest==UUCallbackSuggest.UU_CALLBACK_SUGGEST_ERASE)
{
//管理员执行了设备擦除策略,SDK 将主动执行擦除应用数据并关闭应用
}
elseif(suggest==UUCallbackSuggest.UU_CALLBACK_SUGGEST_RETRY)
{
//由于网络原因导致签到失败,建议弹框提示然后重试
promptAction.showToast({message:message,duration:2000})
}}
}});}
```

### 登出登录

### 先调用应用自身登出,成功后再调用logout 登出接口(如:应用中点击登出按钮)

### 示例代码如下:

```
letargs:Map<string,Object>=newMap();
UUMos.logout(args,{
handleSDKEvent:(map:Map<string,Object>):void=>{
//错误码
letresultCode=
UUMosUtils.getMapNumber(UUCallbackKey.UU_KEY_KMOSCALLBACKERRORCODE,map,-1);
//错误码对应信息描述
letmessage=
UUMosUtils.getMapString(UUCallbackKey.UU_KEY_KMOSCALLBACKERROR,map,"");
//返回接收到状态码后的下一步执行动作,枚举型
letsuggest:UUCallbackSuggest=
UUMosUtils.getMapEnumSuggest(UUCallbackKey.UU_KEY_KMOSCALLBACKSUGGEST,map,
UUCallbackSuggest.UU_CALLBACK_SUGGEST_FINISH);
if(suggest==UUCallbackSuggest.UU_CALLBACK_SUGGEST_FINISH){
//退回到登录界面
}
}
})
```

### 监听处理

### 应用激活/切至前台

| 26 |  |
|---|---|

移动安全MBS SDK 集成指南(鸿蒙)

### 应用有激活立即发送网络请求

### 建议调用获取SDP 通道状态方法,通道开启后再调用网络请求

### 应用无激活立即发送网络请求

### SDP 在应用激活后,会主动检测并做自动重连,正常1s 内可恢复

### 隧道状态监听

### 隧达关闭

### 注册SDP 通道状态监听接口,收到错误码后若应用需要处理这些错误码,则根据

### 应用实际的业务需求,给出用户提示/登出/联系管理员等

### 隧道打开

### 一般无需关注

### 隧道重连机制

### SDK 会在应用切换至前台,网络切换等情况下主动监听网络状态,自动重连,保证

### 隧道连通性,应用一般无需关注

### 示例代码如下:

| //SDP 通道状态监听 |  |  |
|---|---|---|
| UUMos.setListener({ |  |  |
| handleSDKEvent: (map: Map<string, Object>): void => { |  |  |
| if (map != null) { |  |  |
| //错误码 |  |  |
| let resultCode = |  |  |
| UUMosUtils.getMapNumber(UUCallbackKey.UU_KEY_KMOSCALLBACKERRORCODE, map, -1); |  |  |
| //错误码对应信息描述 |  |  |
| let message = |  |  |
| UUMosUtils.getMapString(UUCallbackKey.UU_KEY_KMOSCALLBACKERROR, map, ""); |  |  |
| //返回接收到状态码后的下一步执行动作,枚举型 |  |  |
| let suggest: UUCallbackSuggest = |  |  |
| UUMosUtils.getMapEnumSuggest(UUCallbackKey.UU_KEY_KMOSCALLBACKSUGGEST, map, |  |  |
| UUCallbackSuggest.UU_CALLBACK_SUGGEST_FINISH); |  |  |
| if (suggest == UUCallbackSuggest.UU_CALLBACK_SUGGEST_TIP) { |  |  |
| //提示错误信息 message |  |  |
| } else if (suggest == UUCallbackSuggest.UU_CALLBACK_SUGGEST_RELOGIN) { |  |  |
| //需要退回到登录界面重新登录 |  |  |
| } else if (suggest == UUCallbackSuggest.UU_CALLBACK_SUGGEST_ERASE) { |  |  |
| //设备擦除 |  |  |
| } |  |  |
|  | 27 |  |

移动安全MBS SDK 集成指南(鸿蒙)

```
});
```

### 3.2.1.1.3应用密钥认证

### 3.2.1.1.3.1场景简介

### SDP 管理端可从第三方同步账号,但无法同步密码

### SDK 登录

### SDK 使用配置的APPKey 和SecretKey 进行登录,鉴权成功后管理端生成token 并

### 返回

### 3.2.1.1.3.2前置步骤

### 在实际集成之前,要确保已按【开发环境构建】执行

### 在管理端第三方接入配置中配置应用接入APPKey 和SecretKey

### 3.2.1.1.3.3流程图

| 28 |  |
|---|---|

移动安全MBS SDK 集成指南(鸿蒙)

### 3.2.1.1.3.4集成步骤

### 初始化SDK

### 注意:

### SDK 接口都需要在SDK 初始化后才能调用。

### 初始化SDK 主要是完成SDK 沙箱能力和SDK 配置信息初始化,沙箱能力初始化接口需

要在AbilityStage 的onCreate 中调用,配置信息初始化建议在UIAbility 的onCreate 中调用

### 示例代码如下:

```
export defaultclassMyAbilityStageextendsAbilityStage{
onCreate():void{
//应用的HAP 在首次加载的时,为该Module 初始化操作
letargs:Map<string,object>=newMap();
UUMos.initSandbox(this,args);
}
onAcceptWant(want:Want):string{
//仅specified 模式下触发
return'MyAbilityStage';
}
}
export defaultclassEntryAbilityextendsUIAbility{
onCreate(want:Want,launchParam:AbilityConstant.LaunchParam):void{
letargs:Map<string,Object>=newMap();
UUMos.initWithOnCreate(this.context,args)
this.initUUSdk(this.context)
}
}
initUUSdk(context:Context){
letargs:Map<string,Object>=newMap();
//MOS 服务器地址,String 类型,必填
args.set(UUInitParamsKey.UU_INIT_MBS_URL,
"https://172.16.30.37:9070");
//MOS 服务器租户信息,/String 类型,必填
args.set(UUInitParamsKey.UU_INIT_MBS_ORGCODE,"zzydemo");
```

//网关配置

//安全网关服务器地址,支持主机名和IP 地,String 类型

```
args.set(UUInitParamsKey.UU_INIT_SDP_HOST,"172.16.30.82");
args.set(UUInitParamsKey.UU_INIT_SDP_PORT,8888);//SDP 端口
letinitBack=newUUInitBack();
letres=UUMos.init(context,args,initBack);
```

//0:调用成功,-1:调用失败。

| 29 |  |
|---|---|

移动安全MBS SDK 集成指南(鸿蒙)

```
if(res==0){//0:调用成功
}else{
//-1:调用失败。
}
}
```

### 首次登录

### 应用登录页,点击登录按钮后,先调用login 接口使用APPKey 和SecretKey 登录,登

### 录成功后再执行应用登录

### 实例参考AppKeyLoginPage

### 示例代码如下:

let args: Map<string, Object> = new Map();

let appKey = "njzzy"

let appSecretKey = "njzzy"

//appkey+”||”+loginName+”||”+secretkey

let mPassword = appKey + "||" + userName + "||" + appSecretKey;

//登陆类型,UUAuthType 枚举int 类型,支持类型介绍参考UUAuthType 枚举定义

args.set(UULoginParamsKey.UU_LOGIN_LOGINTYPE, UUAuthType.AUTH_TYPE_APPKEY);

//登录用户名,String 类型,必填

args.set(UULoginParamsKey.UU_LOGIN_LOGINNAME, userName);

//登录密码,String 类型,必填

args.set(UULoginParamsKey.UU_LOGIN_PASSWORD, mPassword);

//2:启用MOS 和SDP必填

args.set(UULoginParamsKey.UU_LOGIN_LOGINMODE, UUSDKMode.UU_MODE_SDP_SANDBOX);

//设置SDP 通道状态监听

UUMos.login(args, {

handleSDKEvent: (map: Map<string, Object>): void => {

if (map) {

//错误码

let resultCode =

UUMosUtils.getMapNumber(UUCallbackKey.UU_KEY_KMOSCALLBACKERRORCODE, map, -1);

//错误码对应信息描述

let message = UUMosUtils.getMapString(UUCallbackKey.UU_KEY_KMOSCALLBACKERROR,

map, "");

//返回接收到状态码后的下一步执行动作,枚举型

let suggest =

UUMosUtils.getMapEnumSuggest(UUCallbackKey.UU_KEY_KMOSCALLBACKSUGGEST, map,

UUCallbackSuggest.UU_CALLBACK_SUGGEST_FINISH);

if (suggest == UUCallbackSuggest.UU_CALLBACK_SUGGEST_TIP) {

//提示错误信息

message

| 30 |  |
|---|---|

移动安全MBS SDK 集成指南(鸿蒙)

promptAction.showToast({

message: "登录失败:" + message + ":" + resultCode,

duration: 2000

})

} else if (suggest == UUCallbackSuggest.UU_CALLBACK_SUGGEST_FINISH) {

//认证成功,认证结束进入主应用

promptAction.showToast({

message: "登录成功",

duration: 2000

})

router.replaceUrl({ url: 'pages/MainPage' }).then(() => {

console.info('testTag', `MainPage .`);

}).catch((err: BusinessError) => {

console.error('testTag', "MainPage ")

})

}

}

}

});

### 免密认证

### 调用sign 接口(如应用闪屏页),成功后再执行应用自身网络业务请求

### 示例代码如下:

| //检测是否支持免密登录 |  |  |
|---|---|---|
| if(UUMos.checkSign() == 0) |  |  |
| { //设置SDP 通道状态监听 |  |  |
| let args:Map<string, Object> = new Map(); |  |  |
| UUMos.sign(args, { |  |  |
| handleSDKEvent:(map:Map<string, Object>):void=>{ |  |  |
| if(map != null) |  |  |
| { |  |  |
| //错误码 |  |  |
| let resultCode = |  |  |
| UUMosUtils.getMapNumber(UUCallbackKey.UU_KEY_KMOSCALLBACKERRORCODE,map,-1); |  |  |
| //错误码对应信息描述 |  |  |
| let message = UUMosUtils.getMapString(UUCallbackKey.UU_KEY_KMOSCALLBACKERROR, |  |  |
| map,""); |  |  |
| //返回接收到状态码后的下一步执行动作,枚举型 |  |  |
| let suggest:UUCallbackSuggest = |  |  |
| UUMosUtils.getMapEnumSuggest(UUCallbackKey.UU_KEY_KMOSCALLBACKSUGGEST,map,UU |  |  |
| CallbackSuggest.UU_CALLBACK_SUGGEST_FINISH); |  |  |
| if(suggest == UUCallbackSuggest.UU_CALLBACK_SUGGEST_TIP) |  |  |
| { |  |  |
|  | 31 |  |

移动安全MBS SDK 集成指南(鸿蒙)

//弹出错误码

```
letmsg:string=message+":"+resultCode;
promptAction.showToast({message:msg,duration:2000})
router.replaceUrl({url:'pages/SelectSceneLoginPage'}).then(()=>{
}).catch((err:BusinessError)=>{
})
}
elseif(suggest==UUCallbackSuggest.UU_CALLBACK_SUGGEST_FINISH)
{
//调用成功,流程已完成,跳转到APP 主界面
router.replaceUrl({url:'pages/MainPage'}).then(()=>{
console.info('testTag',`Succeeded.`);
}).catch((err:BusinessError)=>{
console.error('testTag',"Failed")
})
}
elseif(suggest==UUCallbackSuggest.UU_CALLBACK_SUGGEST_RELOGIN)
{
//应用需要返回登录页面,重新执行SDK 登录流程
router.replaceUrl({url:'pages/SelectSceneLoginPage'}).then(()=>{
}).catch((err:BusinessError)=>{
})
}
elseif(suggest==UUCallbackSuggest.UU_CALLBACK_SUGGEST_ERASE)
{
//管理员执行了设备擦除策略,SDK 将主动执行擦除应用数据并关闭应用
}
elseif(suggest==UUCallbackSuggest.UU_CALLBACK_SUGGEST_RETRY)
{
//由于网络原因导致签到失败,建议弹框提示然后重试
promptAction.showToast({message:message,duration:2000})
}}
}});}
```

### 登出登录

### 先调用应用自身登出,成功后再调用logout 登出接口(如:应用中点击登出按钮)

### 示例代码如下:

| let args: Map<string, Object> = new Map(); |  |  |
|---|---|---|
| UUMos.logout(args, { |  |  |
| handleSDKEvent: (map: Map<string, Object>): void => { |  |  |
| //错误码 |  |  |
| let resultCode = |  |  |
| UUMosUtils.getMapNumber(UUCallbackKey.UU_KEY_KMOSCALLBACKERRORCODE, map, -1); |  |  |
| //错误码对应信息描述 |  |  |
|  | 32 |  |

移动安全MBS SDK 集成指南(鸿蒙)

```
letmessage=
UUMosUtils.getMapString(UUCallbackKey.UU_KEY_KMOSCALLBACKERROR,map,"");
//返回接收到状态码后的下一步执行动作,枚举型
letsuggest:UUCallbackSuggest=
UUMosUtils.getMapEnumSuggest(UUCallbackKey.UU_KEY_KMOSCALLBACKSUGGEST,map,
UUCallbackSuggest.UU_CALLBACK_SUGGEST_FINISH);
if(suggest==UUCallbackSuggest.UU_CALLBACK_SUGGEST_FINISH){
//退回到登录界面
}
}
})
```

### 监听处理

### 应用激活/切至前台

### 应用有激活立即发送网络请求

### 建议调用获取SDP 通道状态方法,通道开启后再调用网络请求

### 应用无激活立即发送网络请求

### SDP 在应用激活后,会主动检测并做自动重连,正常1s 内可恢复

### 隧道状态监听

### 隧达关闭

### 注册SDP 通道状态监听接口,收到错误码后若应用需要处理这些错误码,则根据

### 应用实际的业务需求,给出用户提示/登出/联系管理员等

### 隧道打开

### 一般无需关注

### 隧道重连机制

### SDK 会在应用切换至前台,网络切换等情况下主动监听网络状态,自动重连,保证

### 隧道连通性,应用一般无需关注

### 示例代码如下:

//SDP 通道状态监听

```
UUMos.setListener({
handleSDKEvent:(map:Map<string,Object>):void=>{
if(map!=null){
```

//错误码

| 33 |  |
|---|---|

```
letresultCode=
UUMosUtils.getMapNumber(UUCallbackKey.UU_KEY_KMOSCALLBACKERRORCODE,map,-1);
```

移动安全MBS SDK 集成指南(鸿蒙)

//错误码对应信息描述

```
letmessage=
UUMosUtils.getMapString(UUCallbackKey.UU_KEY_KMOSCALLBACKERROR,map,"");
//返回接收到状态码后的下一步执行动作,枚举型
letsuggest:UUCallbackSuggest=
UUMosUtils.getMapEnumSuggest(UUCallbackKey.UU_KEY_KMOSCALLBACKSUGGEST,map,
UUCallbackSuggest.UU_CALLBACK_SUGGEST_FINISH);
if(suggest==UUCallbackSuggest.UU_CALLBACK_SUGGEST_TIP){
//提示错误信息
message
}elseif(suggest==UUCallbackSuggest.UU_CALLBACK_SUGGEST_RELOGIN){
//需要退回到登录界面重新登录
}elseif(suggest==UUCallbackSuggest.UU_CALLBACK_SUGGEST_ERASE){
//设备擦除
}
}
}
});
```

### 3.2.1.1.4短信认证

### 3.2.1.1.4.1场景简介

### 管理端已配置好短信认证方式,对接短信网关

### SDK 登录

### 1:SDK 调用接口获取短信验证码

### 2:SDK 调用接口使用验证码登录,服务端透传验证码至短信网关鉴权,鉴权成功

### 后透传短信网关生成token 并返回

### 3:调用SDK 登录接口成功后响应鉴权token,主应用携带token 到统一身份认证中

### 心鉴权,鉴权成功后主应用登录成功

### 3.2.1.1.4.2前置步骤

### 在实际集成之前,要确保已按【开发环境构建】执行

### 在管理端已配置完成对接第三方短信网关

| 34 |  |
|---|---|

移动安全MBS SDK 集成指南(鸿蒙)

### 3.2.1.1.4.3流程图

### 3.2.1.1.4.4集成步骤

### 初始化SDK

### 注意:

### SDK 接口都需要在SDK 初始化后才能调用。

### 初始化SDK 主要是完成SDK 沙箱能力和SDK 配置信息初始化,沙箱能力初始化接口需

要在AbilityStage 的onCreate 中调用,配置信息初始化建议在UIAbility 的onCreate 中调用

### 示例代码如下:

| export default class MyAbilityStage extends AbilityStage { |  |
|---|---|
| 35 |  |

移动安全MBS SDK 集成指南(鸿蒙)

```
onCreate():void{
//应用的HAP 在首次加载的时,为该Module 初始化操作
letargs:Map<string,object>=newMap();
UUMos.initSandbox(this,args);
}
onAcceptWant(want:Want):string{
//仅specified 模式下触发
return'MyAbilityStage';
}
}
export defaultclassEntryAbilityextendsUIAbility{
onCreate(want:Want,launchParam:AbilityConstant.LaunchParam):void{
letargs:Map<string,Object>=newMap();
UUMos.initWithOnCreate(this.context,args)
this.initUUSdk(this.context)
}
}
initUUSdk(context:Context){
letargs:Map<string,Object>=newMap();
//MOS 服务器地址,String 类型,必填
args.set(UUInitParamsKey.UU_INIT_MBS_URL,
"https://172.16.30.37:9070");
//MOS 服务器租户信息,/String 类型,必填
args.set(UUInitParamsKey.UU_INIT_MBS_ORGCODE,"zzydemo");
```

//网关配置

//安全网关服务器地址,支持主机名和IP 地,String 类型

```
args.set(UUInitParamsKey.UU_INIT_SDP_HOST,"172.16.30.82");
args.set(UUInitParamsKey.UU_INIT_SDP_PORT,8888);//SDP 端口
letinitBack=newUUInitBack();
letres=UUMos.init(context,args,initBack);
//0:调用成功,-1:调用失败。
if(res==0){//0:调用成功
}else{
//-1:调用失败。
}
}
```

### 首次登录

### 应用登录页,填下手机号调用登录接口获取验证码,再调用SDK 登录接口进行验证码

### 校验

| 36 |  |
|---|---|

移动安全MBS SDK 集成指南(鸿蒙)

### 登录成功后返回token,应用获取后执行应用自身登录

### 短信验证码获取示例代码如下:

```
letmap:Map<string,Object>=newMap();
//手机号
map.set(UUSmsCodeParamsKey.UU_COMM_PHONE_NUMBER,phoneNumber);
```

//国家电话代码

字符串类型,可选项,默认+86 即中国

```
map.set(UUSmsCodeParamsKey.UU_COMM_COUNTRY_CODE,"+86");
UUMos.getSmsCode(map,{
handleSDKEvent:(map:Map<string,Object>):void=>{
if(map!=null){
//错误码
letresultCode=
UUMosUtils.getMapNumber(UUCallbackKey.UU_KEY_KMOSCALLBACKERRORCODE,map,-1);
//错误码对应信息描述
letmessage=
UUMosUtils.getMapString(UUCallbackKey.UU_KEY_KMOSCALLBACKERROR,map,"");
//返回接收到状态码后的下一步执行动作,枚举型
letsuggest:UUCallbackSuggest=
UUMosUtils.getMapEnumSuggest(UUCallbackKey.UU_KEY_KMOSCALLBACKSUGGEST,map,
UUCallbackSuggest.UU_CALLBACK_SUGGEST_FINISH);
letsmsCountdown=
UUMosUtils.getMapNumber(UUCallbackKey.UU_KEY_KMOSSMSCOUNTDOWN,map,0);//短信
```

验证码倒计时

```
if(suggest==UUCallbackSuggest.UU_CALLBACK_SUGGEST_TIP){
//提示错误信息
message
promptAction.showToast({
message:message,
duration:2000
})
}elseif(suggest==UUCallbackSuggest.UU_CALLBACK_SUGGEST_FINISH){
promptAction.showToast({
message:"验证码已下发",
duration:2000
})
}
}
}
});
```

### 短信验证码登录示例代码如下:

| let args: Map<string, Object> = new Map(); |  |  |
|---|---|---|
| //登陆类型,UUAuthType 枚举int 类型,支持类型介绍参考UUAuthType 枚举定义 |  |  |
| args.set(UULoginParamsKey.UU_LOGIN_LOGINTYPE, UUAuthType.AUTH_TYPE_SMS); |  |  |
|  | 37 |  |

移动安全MBS SDK 集成指南(鸿蒙)

| //手机号码,短信验证码登录,String 类型,必填 |  |  |
|---|---|---|
| args.set(UULoginParamsKey.UU_LOGIN_PHONE_NUMBER, phoneNumber); |  |  |
| //国家电话代码,短信验证码登录时使用,String 类型,可选项,默认+86 即中国 |  |  |
| args.set(UULoginParamsKey.UU_LOGIN_COUNTRY_CODE, "+86"); //登录用户名) |  |  |
| //手机号+验证吗登录验证码,String 类型,必填 |  |  |
| args.set(UULoginParamsKey.UU_LOGIN_IDENTIFY_CODE, smsCode); //手机号+验证吗登 |  |  |
| 录) |  |  |
| //2:启用MOS 和SDP 必填 |  |  |
| args.set(UULoginParamsKey.UU_LOGIN_LOGINMODE, |  |  |
| UUSDKMode.UU_MODE_SDP_SANDBOX); |  |  |
| UUMos.login(args, { |  |  |
| handleSDKEvent: (map: Map<string, Object>): void => { |  |  |
| if (map != null) { |  |  |
| let resultCode = |  |  |
| UUMosUtils.getMapNumber(UUCallbackKey.UU_KEY_KMOSCALLBACKERRORCODE, map, -1); |  |  |
| let message = |  |  |
| UUMosUtils.getMapString(UUCallbackKey.UU_KEY_KMOSCALLBACKERROR, map, ""); |  |  |
| let suggest: UUCallbackSuggest = |  |  |
| UUMosUtils.getMapEnumSuggest(UUCallbackKey.UU_KEY_KMOSCALLBACKSUGGEST, map, |  |  |
| UUCallbackSuggest.UU_CALLBACK_SUGGEST_FINISH); |  |  |
| if (suggest == UUCallbackSuggest.UU_CALLBACK_SUGGEST_TIP) { |  |  |
| //提示错误信息 message |  |  |
| promptAction.showToast({ |  |  |
| message: "登录失败:" + message + ":" + resultCode, |  |  |
| duration: 2000 |  |  |
| }) |  |  |
| } else if (suggest == UUCallbackSuggest.UU_CALLBACK_SUGGEST_FINISH) { |  |  |
| promptAction.showToast({ |  |  |
| message: "登录成功", |  |  |
| duration: 2000 |  |  |
| }) |  |  |
| router.replaceUrl({ url: 'pages/MainPage' }).then(() => { |  |  |
| console.info('testTag', `MainPage .`); |  |  |
| }).catch((err: BusinessError) => { |  |  |
| console.error('testTag', "MainPage ") |  |  |
| }) |  |  |
| } else if (suggest == UUCallbackSuggest.UU_CALLBACK_SUGGEST_SAFECONTROL) |  |  |
| { |  |  |
| let authType: UUSafeControlType = |  |  |
|  |  |  |
| UUMosUtils.getMapEnumSuggestSafeControlType(UUCallbackKey.UU_KEY_KMOSSAFECON |  |  |
| TROLTYPE, map, |  |  |
| UUSafeControlType.SAFE_CONTROL_MODIFY_PASSWORD); |  |  |
| if (authType == UUSafeControlType.SAFE_CONTROL_MODIFY_PASSWORD) { |  |  |
|  | 38 |  |

移动安全MBS SDK 集成指南(鸿蒙)

```
}
}
}
}
});
```

### 免密认证

### 调用sign 接口(如应用闪屏页),成功后再执行应用自身网络业务请求

### 示例代码如下:

| //检测是否支持免密登录 |  |  |
|---|---|---|
| if(UUMos.checkSign() == 0) |  |  |
| { //设置SDP 通道状态监听 |  |  |
| let args:Map<string, Object> = new Map(); |  |  |
| UUMos.sign(args, { |  |  |
| handleSDKEvent:(map:Map<string, Object>):void=>{ |  |  |
| if(map != null) |  |  |
| { |  |  |
| //错误码 |  |  |
| let resultCode = |  |  |
| UUMosUtils.getMapNumber(UUCallbackKey.UU_KEY_KMOSCALLBACKERRORCODE,map,-1); |  |  |
| //错误码对应信息描述 |  |  |
| let message = UUMosUtils.getMapString(UUCallbackKey.UU_KEY_KMOSCALLBACKERROR, |  |  |
| map,""); |  |  |
| //返回接收到状态码后的下一步执行动作,枚举型 |  |  |
| let suggest:UUCallbackSuggest = |  |  |
| UUMosUtils.getMapEnumSuggest(UUCallbackKey.UU_KEY_KMOSCALLBACKSUGGEST,map,UU |  |  |
| CallbackSuggest.UU_CALLBACK_SUGGEST_FINISH); |  |  |
| if(suggest == UUCallbackSuggest.UU_CALLBACK_SUGGEST_TIP) |  |  |
| { |  |  |
| //弹出错误码 |  |  |
| let msg:string = message + ":" + resultCode; |  |  |
| promptAction.showToast({message: msg,duration: 2000}) |  |  |
| router.replaceUrl({url:'pages/SelectSceneLoginPage'}).then(()=>{ |  |  |
| }).catch((err:BusinessError)=>{ }) |  |  |
| } |  |  |
| else if(suggest == UUCallbackSuggest.UU_CALLBACK_SUGGEST_FINISH) |  |  |
| { |  |  |
| //调用成功,流程已完成,跳转到APP 主界面 |  |  |
| router.replaceUrl({url:'pages/MainPage'}).then(()=>{ |  |  |
| console.info('testTag', `Succeeded .`); |  |  |
| }).catch((err:BusinessError)=>{ |  |  |
| console.error('testTag',"Failed ") |  |  |
| }) |  |  |
|  | 39 |  |

移动安全MBS SDK 集成指南(鸿蒙)

```
}
elseif(suggest==UUCallbackSuggest.UU_CALLBACK_SUGGEST_RELOGIN)
{
//应用需要返回登录页面,重新执行SDK 登录流程
router.replaceUrl({url:'pages/SelectSceneLoginPage'}).then(()=>{
}).catch((err:BusinessError)=>{
})
}
elseif(suggest==UUCallbackSuggest.UU_CALLBACK_SUGGEST_ERASE)
{
//管理员执行了设备擦除策略,SDK 将主动执行擦除应用数据并关闭应用
}
elseif(suggest==UUCallbackSuggest.UU_CALLBACK_SUGGEST_RETRY)
{
//由于网络原因导致签到失败,建议弹框提示然后重试
promptAction.showToast({message:message,duration:2000})
}}
}});}
```

### 登出登录

### 先调用应用自身登出,成功后再调用logout 登出接口(如:应用中点击登出按钮)

### 示例代码如下:

```
letargs:Map<string,Object>=newMap();
UUMos.logout(args,{
handleSDKEvent:(map:Map<string,Object>):void=>{
//错误码
letresultCode=
UUMosUtils.getMapNumber(UUCallbackKey.UU_KEY_KMOSCALLBACKERRORCODE,map,-1);
//错误码对应信息描述
letmessage=
UUMosUtils.getMapString(UUCallbackKey.UU_KEY_KMOSCALLBACKERROR,map,"");
//返回接收到状态码后的下一步执行动作,枚举型
letsuggest:UUCallbackSuggest=
UUMosUtils.getMapEnumSuggest(UUCallbackKey.UU_KEY_KMOSCALLBACKSUGGEST,map,
UUCallbackSuggest.UU_CALLBACK_SUGGEST_FINISH);
if(suggest==UUCallbackSuggest.UU_CALLBACK_SUGGEST_FINISH){
//退回到登录界面
}
}
})
```

### 监听处理

| 40 |  |
|---|---|

移动安全MBS SDK 集成指南(鸿蒙)

### 应用激活/切至前台

### 应用有激活立即发送网络请求

### 建议调用获取SDP 通道状态方法,通道开启后再调用网络请求

### 应用无激活立即发送网络请求

### SDP 在应用激活后,会主动检测并做自动重连,正常1s 内可恢复

### 隧道状态监听

### 隧达关闭

### 注册SDP 通道状态监听接口,收到错误码后若应用需要处理这些错误码,则根据

### 应用实际的业务需求,给出用户提示/登出/联系管理员等

### 隧道打开

### 一般无需关注

### 隧道重连机制

### SDK 会在应用切换至前台,网络切换等情况下主动监听网络状态,自动重连,保证

### 隧道连通性,应用一般无需关注

### 示例代码如下:

//SDP 通道状态监听

```
UUMos.setListener({
handleSDKEvent:(map:Map<string,Object>):void=>{
if(map!=null){
//错误码
letresultCode=
UUMosUtils.getMapNumber(UUCallbackKey.UU_KEY_KMOSCALLBACKERRORCODE,map,-1);
//错误码对应信息描述
letmessage=
UUMosUtils.getMapString(UUCallbackKey.UU_KEY_KMOSCALLBACKERROR,map,"");
//返回接收到状态码后的下一步执行动作,枚举型
letsuggest:UUCallbackSuggest=
UUMosUtils.getMapEnumSuggest(UUCallbackKey.UU_KEY_KMOSCALLBACKSUGGEST,map,
UUCallbackSuggest.UU_CALLBACK_SUGGEST_FINISH);
if(suggest==UUCallbackSuggest.UU_CALLBACK_SUGGEST_TIP){
//提示错误信息
message
}elseif(suggest==UUCallbackSuggest.UU_CALLBACK_SUGGEST_RELOGIN){
//需要退回到登录界面重新登录
}elseif(suggest==UUCallbackSuggest.UU_CALLBACK_SUGGEST_ERASE){
```

//设备擦除

| 41 |  |
|---|---|

```
}
移动安全MBS SDK 集成指南(鸿蒙)
}
}
});
```

### 3.2.1.2二次认证

### 3.2.1.2.1用户名密码+短信认证

### 3.2.1.2.1.1场景简介

### 1:管理端已从第三方同步账号及密码

### 2:管理端->安全管理->接入安全,开启风险认证,选择认证方式为短信验证

### 3:管理端已配置好短信认证方式,对接短信网关

### SDK 登录

### 1:SDK 用户名/密码进行登录,鉴权成功后管理端返回需要二次短信认证

### 2:SDK 调用接口获取短信验证码

### 3:SDK 调用接口使用验证码登录,服务端透传验证码至短信网关鉴权,鉴权成功

### 后透传短信网关生成token 并返回

### 集成应用登录

### 用户名/密码进行登录

### SDK 返回token 登录,向短信网关提供RestApi 接口鉴权

### 3.2.1.2.1.2前置步骤

### 在实际集成之前,要确保已按【开发环境构建】执行

### 在管理端创建测试用户,并配置好用户名密码认证

### 在管理端已配置完成对接第三方短信网关

### 管理端->安全管理->接入安全,开启风险认证,选择认证方式为短信验证

| 42 |  |
|---|---|

移动安全MBS SDK 集成指南(鸿蒙)

### 3.2.1.2.1.3流程图

### 3.2.1.2.1.4集成步骤

### 初始化SDK

### 注意:

### SDK 接口都需要在SDK 初始化后才能调用。

### 初始化SDK 主要是完成SDK 沙箱能力和SDK 配置信息初始化,沙箱能力初始化接口需

要在AbilityStage 的onCreate 中调用,配置信息初始化建议在UIAbility 的onCreate 中调用

### 示例代码如下:

| export default class MyAbilityStage extends AbilityStage { |  |
|---|---|
| onCreate(): void { |  |
| // 应用的HAP 在首次加载的时,为该Module 初始化操作 |  |
| let args: Map<string, object> = new Map(); |  |
| UUMos.initSandbox(this,args); |  |
| } |  |
| onAcceptWant(want: Want): string { |  |
| // 仅specified 模式下触发 |  |
| 43 |  |

移动安全MBS SDK 集成指南(鸿蒙)

```
return'MyAbilityStage';
}
}
export defaultclassEntryAbilityextendsUIAbility{
onCreate(want:Want,launchParam:AbilityConstant.LaunchParam):void{
letargs:Map<string,Object>=newMap();
UUMos.initWithOnCreate(this.context,args)
this.initUUSdk(this.context)
}
}
initUUSdk(context:Context){
letargs:Map<string,Object>=newMap();
//MOS 服务器地址,String 类型,必填
args.set(UUInitParamsKey.UU_INIT_MBS_URL,
"https://172.16.30.37:9070");
//MOS 服务器租户信息,/String 类型,必填
args.set(UUInitParamsKey.UU_INIT_MBS_ORGCODE,"zzydemo");
```

//网关配置

//安全网关服务器地址,支持主机名和IP 地,String 类型

```
args.set(UUInitParamsKey.UU_INIT_SDP_HOST,"172.16.30.82");
args.set(UUInitParamsKey.UU_INIT_SDP_PORT,8888);//SDP 端口
letinitBack=newUUInitBack();
letres=UUMos.init(context,args,initBack);
//0:调用成功,-1:调用失败。
if(res==0){//0:调用成功
}else{
//-1:调用失败。
}
}
```

### 首次登录

### 1:应用登录页,点击登录按钮后,先调用login 接口使用用户填写账号/密码登录,

### 服务器返回需要二次短信认证

### 2:填写短信验证码,再调用SDK 登录接口进行验证码校验

### 3:登录成功后返回token,应用获取后执行应用自身登录

### 用户名密码登录示例代码如下:

```
letargs:Map<string,Object>=newMap();
```

//登陆类型,UUAuthType 枚举int 类型,支持类型介绍参考UUAuthType 枚举定义

| 44 |  |
|---|---|

移动安全MBS SDK 集成指南(鸿蒙)

```
args.set(UULoginParamsKey.UU_LOGIN_LOGINTYPE,
UUAuthType.AUTH_TYPE_PASSWORD);
//登录用户名,String 类型,必填
args.set(UULoginParamsKey.UU_LOGIN_LOGINNAME,mUserName);
//登录密码,String 类型,必填
args.set(UULoginParamsKey.UU_LOGIN_PASSWORD,mPassword);
//0:仅启动mos,1:仅启动sdp,2:启用MOS 和SDP,SDP 前置必填
args.set(UULoginParamsKey.UU_LOGIN_LOGINMODE,
UUSDKMode.UU_MODE_SDP_SANDBOX);
```

//设备id 用于标识设备唯一性,项目如果需要自定义设备唯一标识需要传递mbs_securityId,32

位字符串类型,非必填

```
//
args.put(UU_LOGIN_DEVICEID,"APP 自己生成设备ID");
//设置SDP 通道状态监听
//DemoBridge.getInstance().setListener(this);
UUMos.login(args,{
handleSDKEvent:(map:Map<string,Object>):void=>{
if(map!=null){
letresultCode=
UUMosUtils.getMapNumber(UUCallbackKey.UU_KEY_KMOSCALLBACKERRORCODE,map,-1);
letmessage=
UUMosUtils.getMapString(UUCallbackKey.UU_KEY_KMOSCALLBACKERROR,map,"");
letsuggest:UUCallbackSuggest=
UUMosUtils.getMapEnumSuggest(UUCallbackKey.UU_KEY_KMOSCALLBACKSUGGEST,map,
UUCallbackSuggest.UU_CALLBACK_SUGGEST_FINISH);
if(suggest==UUCallbackSuggest.UU_CALLBACK_SUGGEST_TIP){
```

//提示错误信息

| 45 |  |
|---|---|

```
message
promptAction.showToast({
message:"登录失败:"+message+":"+resultCode,
duration:2000
})
}elseif(suggest==UUCallbackSuggest.UU_CALLBACK_SUGGEST_FINISH){
promptAction.showToast({
message:"登录成功",
duration:2000
})
router.replaceUrl({url:'pages/MainPage'}).then(()=>{
console.info('testTag',`MainPage.`);
}).catch((err:BusinessError)=>{
console.error('testTag',"MainPage")
})
}elseif(suggest==UUCallbackSuggest.UU_CALLBACK_SUGGEST_SAFECONTROL)
{
letauthType:UUSafeControlType=
移动安全MBS SDK 集成指南(鸿蒙)
UUMosUtils.getMapEnumSuggestSafeControlType(UUCallbackKey.UU_KEY_KMOSSAFECON
TROLTYPE,map,
UUSafeControlType.SAFE_CONTROL_MODIFY_PASSWORD);
if(authType==UUSafeControlType.SAFE_CONTROL_MODIFY_PASSWORD){
}
}
elseif(suggest==UUCallbackSuggest.UU_CALLBACK_SUGGEST_PROGRESS)
{
letauthType:UUSecondaryAuthType=
UUMosUtils.getMapEnumSuggestAuthType(UUCallbackKey.UU_KEY_KMOSSECONDARYAUTHT
YPE,map,UUSecondaryAuthType.AUTH_TYPE_SECOND_SMS);
if(authType==UUSecondaryAuthType.AUTH_TYPE_SECOND_SMS)
{
//需要短信二次认证,等待服务器下发验证码后,输入验证码进行二次认证
router.replaceUrl({url:'pages/SmsCodeSecondAuthPage'}).then(()=>{
console.info('testTag',`MainPage.`);
}).catch((err:BusinessError)=>{
console.error('testTag',"MainPage")
})
}
else
{
//二次认证类型不匹配,请检查需求
}
}
}
}
});
```

### 短信验证码二次认证示例代码如下:

```
letargs:Map<string,Object>=newMap();
//登陆类型,UUAuthType 枚举int 类型,支持类型介绍参考UUAuthType 枚举定义
args.set(UULoginParamsKey.UU_LOGIN_LOGINTYPE,
UUSecondaryAuthType.AUTH_TYPE_SECOND_SMS);
//登录用户名,String 类型,必填
args.set(UULoginParamsKey.UU_LOGIN_IDENTIFY_CODE,smsCode);
//设置SDP 通道状态监听
UUMos.secondaryAuth(args,{
handleSDKEvent:(map:Map<string,Object>):void=>{
if(map){
```

//错误码

| 46 |  |
|---|---|

移动安全MBS SDK 集成指南(鸿蒙)

```
letresultCode=
UUMosUtils.getMapNumber(UUCallbackKey.UU_KEY_KMOSCALLBACKERRORCODE,map,-1);
//错误码对应信息描述
letmessage=
UUMosUtils.getMapString(UUCallbackKey.UU_KEY_KMOSCALLBACKERROR,map,"");
//返回接收到状态码后的下一步执行动作,枚举型
letsuggest=
UUMosUtils.getMapEnumSuggest(UUCallbackKey.UU_KEY_KMOSCALLBACKSUGGEST,map,
UUCallbackSuggest.UU_CALLBACK_SUGGEST_FINISH);
if(suggest==UUCallbackSuggest.UU_CALLBACK_SUGGEST_TIP){
//提示错误信息
message
promptAction.showToast({
message:"登录失败:"+message+":"+resultCode,
duration:2000
})
}elseif(suggest==UUCallbackSuggest.UU_CALLBACK_SUGGEST_FINISH){
//认证成功,认证结束进入主应用
promptAction.showToast({
message:"登录成功",
duration:2000
})
router.replaceUrl({url:'pages/MainPage'}).then(()=>{
console.info('testTag',`MainPage.`);
}).catch((err:BusinessError)=>{
console.error('testTag',"MainPage")
})
}
}
}
});
```

### 短信验证码重发示例代码如下:

```
letmap:Map<string,Object>=newMap();
UUMos.refreshSmsCode(map,{
handleSDKEvent:(map:Map<string,Object>):void=>{
if(map!=null){
//接口调用状态码
letresultCode=
UUMosUtils.getMapNumber(UUCallbackKey.UU_KEY_KMOSCALLBACKERRORCODE,map,-1);
//错误描述信息
letmessage=
UUMosUtils.getMapString(UUCallbackKey.UU_KEY_KMOSCALLBACKERROR,map,"");
```

//返回接收到状态码后的下一步执行动作,枚举型

| 47 |  |
|---|---|

移动安全MBS SDK 集成指南(鸿蒙)

```
letsuggest=
UUMosUtils.getMapEnumSuggest(UUCallbackKey.UU_KEY_KMOSCALLBACKSUGGEST,map,
UUCallbackSuggest.UU_CALLBACK_SUGGEST_FINISH);
//短信发送倒计时,数字,单位秒
letsmsCountdown=
UUMosUtils.getMapNumber(UUCallbackKey.UU_KEY_KMOSSMSCOUNTDOWN,map,60);
if(suggest==UUCallbackSuggest.UU_CALLBACK_SUGGEST_TIP){
//刷新验证码失败,提示错误信息
message
promptAction.showToast({
message:message,
duration:2000
})
}elseif(suggest==UUCallbackSuggest.UU_CALLBACK_SUGGEST_FINISH){
promptAction.showToast({
message:"刷新验证码成功",
duration:2000
})
}
}
}
});
```

### 免密认证

### 调用sign 接口(如应用闪屏页),成功后再执行应用自身网络业务请求

### 示例代码如下:

| //检测是否支持免密登录 |  |  |
|---|---|---|
| if(UUMos.checkSign() == 0) |  |  |
| { |  |  |
| Map<String, Object> args = new HashMap<>(); |  |  |
| UUMos.sign(args, new IUUSDKCallback() { |  |  |
| @Override |  |  |
| public void handleSDKEvent(Map<String, Object> map) { |  |  |
| //错误码 |  |  |
| int resultCode = |  |  |
| UUMosUtils.getMapInteger(UU_KEY_KMOSCALLBACKERRORCODE.stringValue(),map,-1); |  |  |
| //错误描述信息 |  |  |
| String message = |  |  |
| UUMosUtils.getMapString(UU_KEY_KMOSCALLBACKERROR.stringValue(),map,""); |  |  |
| //接口调用下一步支持动作 |  |  |
| UUCallbackSuggest suggest = |  |  |
| UUMosUtils.getMapEnumSuggest(UU_KEY_KMOSCALLBACKSUGGEST.stringValue(),map,UU |  |  |
| _CALLBACK_SUGGEST_FINISH); |  |  |
| if(suggest == UUCallbackSuggest.UU_CALLBACK_SUGGEST_TIP) |  |  |
|  | 48 |  |

移动安全MBS SDK 集成指南(鸿蒙)

```
{
//弹出错误码
}
elseif(suggest==UUCallbackSuggest.UU_CALLBACK_SUGGEST_FINISH)
{
//调用成功,流程已完成,跳转到APP 主界面
}
elseif(suggest==UUCallbackSuggest.UU_CALLBACK_SUGGEST_RELOGIN)
{
//应用需要返回登录页面,重新执行SDK 登录流程
}
elseif(suggest==UUCallbackSuggest.UU_CALLBACK_SUGGEST_ERASE)
{
//管理员执行了设备擦除策略,SDK 将主动执行擦除应用数据并关闭应用
}
elseif(suggest==UUCallbackSuggest.UU_CALLBACK_SUGGEST_RETRY)
{
//由于网络原因导致免密认证失败,建议弹框提示然后重试
showErrorMessage(message);
}
}
});
}
```

### 登出登录

### 先调用应用自身登出,成功后再调用logout 登出接口(如:应用中点击登出按钮)

### 示例代码如下:

| Map<String, Object> args = new HashMap<>(); |  |  |
|---|---|---|
| UUMos.logout(args, new IUUSDKCallback() { |  |  |
| @Override |  |  |
| public void handleSDKEvent(Map<String, Object> map) { |  |  |
| //错误码 |  |  |
| int resultCode = |  |  |
| UUMosUtils.getMapInteger(UU_KEY_KMOSCALLBACKERRORCODE.stringValue(),map,-1); |  |  |
| //错误码对应信息描述 |  |  |
| String message = |  |  |
| UUMosUtils.getMapString(UU_KEY_KMOSCALLBACKERROR.stringValue(), map,""); |  |  |
| //返回接收到状态码后的下一步执行动作,枚举型 |  |  |
| UUCallbackSuggest suggest = |  |  |
| UUMosUtils.getMapEnumSuggest(UU_KEY_KMOSCALLBACKSUGGEST.stringValue(),map,UU |  |  |
| _CALLBACK_SUGGEST_FINISH); |  |  |
| if(suggest == UUCallbackSuggest.UU_CALLBACK_SUGGEST_FINISH) |  |  |
| { |  |  |
|  | 49 |  |

移动安全MBS SDK 集成指南(鸿蒙)

//退回到登录界面

```
}
}
});
```

### 监听处理

### 应用激活/切至前台

### 应用有激活立即发送网络请求

### 建议调用获取SDP 通道状态方法,通道开启后再调用网络请求

### 应用无激活立即发送网络请求

### SDP 在应用激活后,会主动检测并做自动重连,正常1s 内可恢复

### 隧道状态监听

### 隧达关闭

### 注册SDP 通道状态监听接口,收到错误码后若应用需要处理这些错误码,

### 则根据应用实际的业务需求,给出用户提示/登出/联系管理员等

### 隧道打开

### 一般无需关注

### 隧道重连机制

### SDK 会在应用切换至前台,网络切换等情况下主动监听网络状态,自动重连,

### 保证隧道连通性,应用一般无需关注

### 示例代码如下:

```
UUMos.setListener(newIUUSDKCallback(){
@Override
public voidhandleSDKEvent(Map<String,Object>map){
//0:SDP 通道已经关闭1:SDP 通道已开启
if(map!=null)
{
//错误码
intresultCode=
UUMosUtils.getMapInteger(UU_KEY_KMOSCALLBACKERRORCODE.stringValue(),map,-1);
//错误码对应信息描述
Stringmessage=
UUMosUtils.getMapString(UU_KEY_KMOSCALLBACKERROR.stringValue(),map,"");
```

//返回接收到状态码后的下一步执行动作,枚举型

| 50 |  |
|---|---|

移动安全MBS SDK 集成指南(鸿蒙)

```
UUCallbackSuggestsuggest=
UUMosUtils.getMapEnumSuggest(UU_KEY_KMOSCALLBACKSUGGEST.stringValue(),map,UU
_CALLBACK_SUGGEST_FINISH);
if(suggest==UUCallbackSuggest.UU_CALLBACK_SUGGEST_TIP)
{
//提示错误信息
message
}
elseif(suggest==UUCallbackSuggest.UU_CALLBACK_SUGGEST_RELOGIN)
{
//需要退回到登录界面重新登录
}
elseif(suggest==UUCallbackSuggest.UU_CALLBACK_SUGGEST_ERASE)
{
//设备擦除
}
}
}
});
```

### 3.2.1.2.2用户名密码+第三方令牌认证

### 3.2.1.2.2.1场景描述

### 1:管理端已从第三方同步账号及密码

### 2:管理端->安全管理->接入安全,开启风险认证,选择认证方式为风险认证

### SDK 登录

### 1:SDK 用户名/密码进行登录,鉴权成功后管理端返回需要自定义安全认证

### 2:通过其它突进获取认证所需信息,比如OTP 码、第三方token 等

### 3:SDK 调用接口使用风险自定义认证,服务端透传认证信息到认证插件,鉴权成

### 功后透传认证插件生成token 并返回

### 集成应用登录

### 用户名/密码进行登录

### SDK 返回token 登录

### 3.2.1.2.2.2前置步骤

### 在实际集成之前,要确保已按【开发环境构建】执行

### 在管理端创建测试用户,并配置好用户名密码认证

| 51 |  |
|---|---|

移动安全MBS SDK 集成指南(鸿蒙)

### 在管理端已配置完成对接第三方认证插件

### 管理端->安全管理->接入安全,开启风险认证,选择认证方式为风险自定义认证

### 3.2.1.2.2.3流程图

### 3.2.1.2.2.4集成步骤

### 初始化SDK

### 注意:

### SDK 接口都需要在SDK 初始化后才能调用。

### 初始化SDK 主要是完成SDK 沙箱能力和SDK 配置信息初始化,沙箱能力初始化接口需

要在AbilityStage 的onCreate 中调用,配置信息初始化建议在UIAbility 的onCreate 中调用

### 示例代码如下:

```
export defaultclassMyAbilityStageextendsAbilityStage{
onCreate():void{
```

//应用的HAP 在首次加载的时,为该Module 初始化操作

| 52 |  |
|---|---|

```
letargs:Map<string,object>=newMap();
移动安全MBS SDK 集成指南(鸿蒙)
UUMos.initSandbox(this,args);
}
onAcceptWant(want:Want):string{
//仅specified 模式下触发
return'MyAbilityStage';
}
}
export defaultclassEntryAbilityextendsUIAbility{
onCreate(want:Want,launchParam:AbilityConstant.LaunchParam):void{
letargs:Map<string,Object>=newMap();
UUMos.initWithOnCreate(this.context,args)
this.initUUSdk(this.context)
}
}
initUUSdk(context:Context){
letargs:Map<string,Object>=newMap();
//MOS 服务器地址,String 类型,必填
args.set(UUInitParamsKey.UU_INIT_MBS_URL,
"https://172.16.30.37:9070");
//MOS 服务器租户信息,/String 类型,必填
args.set(UUInitParamsKey.UU_INIT_MBS_ORGCODE,"zzydemo");
```

//网关配置

//安全网关服务器地址,支持主机名和IP 地,String 类型

```
args.set(UUInitParamsKey.UU_INIT_SDP_HOST,"172.16.30.82");
args.set(UUInitParamsKey.UU_INIT_SDP_PORT,8888);//SDP 端口
letinitBack=newUUInitBack();
letres=UUMos.init(context,args,initBack);
//0:调用成功,-1:调用失败。
if(res==0){//0:调用成功
}else{
//-1:调用失败。
}
}
```

### 首次登录

### 1:应用登录页,点击登录按钮后,先调用login 接口使用用户填写账号/密码登录,

### 服务器返回需要二次短信认证

### 2:获取第三方令牌调用SDK 登录接口进行令牌校验

### 3:登录成功后返回token,应用获取后执行应用自身登录

### 用户名密码登录示例代码如下:

| 53 |  |
|---|---|

移动安全MBS SDK 集成指南(鸿蒙)

```
letargs:Map<string,Object>=newMap();
//登陆类型,UUAuthType 枚举int 类型,支持类型介绍参考UUAuthType 枚举定义
args.set(UULoginParamsKey.UU_LOGIN_LOGINTYPE,
UUAuthType.AUTH_TYPE_PASSWORD);
//登录用户名,String 类型,必填
args.set(UULoginParamsKey.UU_LOGIN_LOGINNAME,mUserName);
//登录密码,String 类型,必填
args.set(UULoginParamsKey.UU_LOGIN_PASSWORD,mPassword);
//0:仅启动mos,1:仅启动sdp,2:启用MOS 和SDP,SDP 前置必填
args.set(UULoginParamsKey.UU_LOGIN_LOGINMODE,
UUSDKMode.UU_MODE_SDP_SANDBOX);
//设置SDP 通道状态监听
//DemoBridge.getInstance().setListener(this);
UUMos.login(args,{
handleSDKEvent:(map:Map<string,Object>):void=>{
if(map!=null){
letresultCode=
UUMosUtils.getMapNumber(UUCallbackKey.UU_KEY_KMOSCALLBACKERRORCODE,map,-1);
letmessage=
UUMosUtils.getMapString(UUCallbackKey.UU_KEY_KMOSCALLBACKERROR,map,"");
letsuggest:UUCallbackSuggest=
UUMosUtils.getMapEnumSuggest(UUCallbackKey.UU_KEY_KMOSCALLBACKSUGGEST,map,
UUCallbackSuggest.UU_CALLBACK_SUGGEST_FINISH);
if(suggest==UUCallbackSuggest.UU_CALLBACK_SUGGEST_TIP){
```

//提示错误信息

| 54 |  |
|---|---|

```
message
promptAction.showToast({
message:"登录失败:"+message+":"+resultCode,
duration:2000
})
}elseif(suggest==UUCallbackSuggest.UU_CALLBACK_SUGGEST_FINISH){
promptAction.showToast({
message:"登录成功",
duration:2000
})
router.replaceUrl({url:'pages/MainPage'}).then(()=>{
console.info('testTag',`MainPage.`);
}).catch((err:BusinessError)=>{
console.error('testTag',"MainPage")
})
}elseif(suggest==UUCallbackSuggest.UU_CALLBACK_SUGGEST_SAFECONTROL)
{
letauthType:UUSafeControlType=
移动安全MBS SDK 集成指南(鸿蒙)
UUMosUtils.getMapEnumSuggestSafeControlType(UUCallbackKey.UU_KEY_KMOSSAFECON
TROLTYPE,map,
UUSafeControlType.SAFE_CONTROL_MODIFY_PASSWORD);
if(authType==UUSafeControlType.SAFE_CONTROL_MODIFY_PASSWORD){
}
}
elseif(suggest==UUCallbackSuggest.UU_CALLBACK_SUGGEST_PROGRESS)
{
letauthType:UUSecondaryAuthType=
UUMosUtils.getMapEnumSuggestAuthType(UUCallbackKey.UU_KEY_KMOSSECONDARYAUTHT
YPE,map,UUSecondaryAuthType.AUTH_TYPE_SECOND_SMS);
//登录扩展字段,二次认证需要用到扩展字段里面的信息
letextendParam=
UUMosUtils.getMapString(UUCallbackKey.UU_KEY_MOS_EXTENDPARAM,map,"");
if(authType==UUSecondaryAuthType.AUTH_TYPE_SECOND_CUSTOM)
{
//需要短信二次认证,等待服务器下发验证码后,输入验证码进行二次认证
router.replaceUrl({url:'pages/TokenSecondAuthPage'}).then(()=>{
console.info('testTag',`MainPage.`);
}).catch((err:BusinessError)=>{
console.error('testTag',"MainPage")
})
}
else
{
//二次认证类型不匹配,请检查需求
}
}
}
}
});
```

### 令牌二次认证示例代码如下:

| let args: Map<string, Object> = new Map(); |  |  |
|---|---|---|
| //登陆类型,UUAuthType 枚举int 类型,支持类型介绍参考UUAuthType 枚举定义 |  |  |
| args.set(UULoginParamsKey.UU_LOGIN_LOGINTYPE, |  |  |
| UUSecondaryAuthType.AUTH_TYPE_SECOND_CUSTOM); |  |  |
| //登录用户名,String 类型,必填 |  |  |
| //第三方令牌认证密码字段根据项目需求自定义,具体格式和值根据服务器认证插件定义为准 |  |  |
| args.set(UULoginParamsKey.UU_LOGIN_IDENTIFY_CODE, token); |  |  |
| //设置SDP 通道状态监听 |  |  |
| UUMos.secondaryAuth(args, { |  |  |
|  | 55 |  |

移动安全MBS SDK 集成指南(鸿蒙)

```
handleSDKEvent:(map:Map<string,Object>):void=>{
if(map){
//错误码
letresultCode=
UUMosUtils.getMapNumber(UUCallbackKey.UU_KEY_KMOSCALLBACKERRORCODE,map,-1);
//错误码对应信息描述
letmessage=
UUMosUtils.getMapString(UUCallbackKey.UU_KEY_KMOSCALLBACKERROR,map,"");
//返回接收到状态码后的下一步执行动作,枚举型
letsuggest=
UUMosUtils.getMapEnumSuggest(UUCallbackKey.UU_KEY_KMOSCALLBACKSUGGEST,map,
UUCallbackSuggest.UU_CALLBACK_SUGGEST_FINISH);
if(suggest==UUCallbackSuggest.UU_CALLBACK_SUGGEST_TIP){
//提示错误信息
message
promptAction.showToast({
message:"登录失败:"+message+":"+resultCode,
duration:2000
})
}elseif(suggest==UUCallbackSuggest.UU_CALLBACK_SUGGEST_FINISH){
//认证成功,认证结束进入主应用
promptAction.showToast({
message:"登录成功",
duration:2000
})
router.replaceUrl({url:'pages/MainPage'}).then(()=>{
console.info('testTag',`MainPage.`);
}).catch((err:BusinessError)=>{
console.error('testTag',"MainPage")
})
}
}
}
});
```

### 免密认证

### 调用sign 接口(如应用闪屏页),成功后再执行应用自身网络业务请求

### 示例代码如下:

| //检测是否支持免密登录 |  |  |
|---|---|---|
| if(UUMos.checkSign() == 0) |  |  |
| { |  |  |
| Map<String, Object> args = new HashMap<>(); |  |  |
| UUMos.sign(args, new IUUSDKCallback() { |  |  |
| @Override |  |  |
|  | 56 |  |

移动安全MBS SDK 集成指南(鸿蒙)

```
public voidhandleSDKEvent(Map<String,Object>map){
//错误码
intresultCode=
UUMosUtils.getMapInteger(UU_KEY_KMOSCALLBACKERRORCODE.stringValue(),map,-1);
//错误描述信息
Stringmessage=
UUMosUtils.getMapString(UU_KEY_KMOSCALLBACKERROR.stringValue(),map,"");
//接口调用下一步支持动作
UUCallbackSuggestsuggest=
UUMosUtils.getMapEnumSuggest(UU_KEY_KMOSCALLBACKSUGGEST.stringValue(),map,UU
_CALLBACK_SUGGEST_FINISH);
if(suggest==UUCallbackSuggest.UU_CALLBACK_SUGGEST_TIP)
{
//弹出错误码
}
elseif(suggest==UUCallbackSuggest.UU_CALLBACK_SUGGEST_FINISH)
{
//调用成功,流程已完成,跳转到APP 主界面
}
elseif(suggest==UUCallbackSuggest.UU_CALLBACK_SUGGEST_RELOGIN)
{
//应用需要返回登录页面,重新执行SDK 登录流程
}
elseif(suggest==UUCallbackSuggest.UU_CALLBACK_SUGGEST_ERASE)
{
//管理员执行了设备擦除策略,SDK 将主动执行擦除应用数据并关闭应用
}
elseif(suggest==UUCallbackSuggest.UU_CALLBACK_SUGGEST_RETRY)
{
//由于网络原因导致免密认证失败,建议弹框提示然后重试
showErrorMessage(message);
}
}
});
}
```

### 登出登录

### 先调用应用自身登出,成功后再调用logout 登出接口(如:应用中点击登出按钮)

### 示例代码如下:

| Map<String, Object> args = new HashMap<>(); |  |  |
|---|---|---|
| UUMos.logout(args, new IUUSDKCallback() { |  |  |
| @Override |  |  |
| public void handleSDKEvent(Map<String, Object> map) { |  |  |
|  | 57 |  |

移动安全MBS SDK 集成指南(鸿蒙)

//错误码

```
intresultCode=
UUMosUtils.getMapInteger(UU_KEY_KMOSCALLBACKERRORCODE.stringValue(),map,-1);
//错误码对应信息描述
Stringmessage=
UUMosUtils.getMapString(UU_KEY_KMOSCALLBACKERROR.stringValue(),map,"");
//返回接收到状态码后的下一步执行动作,枚举型
UUCallbackSuggestsuggest=
UUMosUtils.getMapEnumSuggest(UU_KEY_KMOSCALLBACKSUGGEST.stringValue(),map,UU
_CALLBACK_SUGGEST_FINISH);
if(suggest==UUCallbackSuggest.UU_CALLBACK_SUGGEST_FINISH)
{
//退回到登录界面
}
}
});
```

### 监听处理

### 应用激活/切至前台

### 应用有激活立即发送网络请求

### 建议调用获取SDP 通道状态方法,通道开启后再调用网络请求

### 应用无激活立即发送网络请求

### SDP 在应用激活后,会主动检测并做自动重连,正常1s 内可恢复

### 隧道状态监听

### 隧达关闭

### 注册SDP 通道状态监听接口,收到错误码后若应用需要处理这些错误码,

### 则根据应用实际的业务需求,给出用户提示/登出/联系管理员等

### 隧道打开

### 一般无需关注

### 隧道重连机制

### SDK 会在应用切换至前台,网络切换等情况下主动监听网络状态,自动重连,

### 保证隧道连通性,应用一般无需关注

### 示例代码如下:

| 58 |  |
|---|---|

```
UUMos.setListener(newIUUSDKCallback(){
@Override
public voidhandleSDKEvent(Map<String,Object>map){
```

移动安全MBS SDK 集成指南(鸿蒙)

//0:SDP 通道已经关闭1:SDP 通道已开启

```
if(map!=null)
{
//错误码
intresultCode=
UUMosUtils.getMapInteger(UU_KEY_KMOSCALLBACKERRORCODE.stringValue(),map,-1);
//错误码对应信息描述
Stringmessage=
UUMosUtils.getMapString(UU_KEY_KMOSCALLBACKERROR.stringValue(),map,"");
//返回接收到状态码后的下一步执行动作,枚举型
UUCallbackSuggestsuggest=
UUMosUtils.getMapEnumSuggest(UU_KEY_KMOSCALLBACKSUGGEST.stringValue(),map,UU
_CALLBACK_SUGGEST_FINISH);
if(suggest==UUCallbackSuggest.UU_CALLBACK_SUGGEST_TIP)
{
//提示错误信息
message
}
elseif(suggest==UUCallbackSuggest.UU_CALLBACK_SUGGEST_RELOGIN)
{
//需要退回到登录界面重新登录
}
elseif(suggest==UUCallbackSuggest.UU_CALLBACK_SUGGEST_ERASE)
{
//设备擦除
}
}
}
});
```

# 3.3流程自检

## 3.3.1是否正确处理了登录

### 3.3.1.1注意事项

### 1.调用登录前检查是否调用SDK 初始化接口,并检测参数是否正确

### 2.登录接口调用是否与项目场景相符,注意必填参数

### 3.参照API 接口使用说明处理登录接口回调,登录鉴权完成后会启动安全通道和拉取安全

### 防护策略,需要正确处理登录接口回调,具体使用参考API 使用说明

| 59 |  |
|---|---|

移动安全MBS SDK 集成指南(鸿蒙)

### 3.3.1.2测试步骤

### 1.填入用户信息登录集成SDK 应用

### 2.登录管理平台,在设备中心查看设备

### 3.访问资源

### 3.3.1.3期望结果

### 1.登录成功

### 2.设备状态正常

### 3.资源访问正常

### 3.3.1.4失败排查

### 1.认证失败问题排查:查看登录接口回调错误码和错误信息描述,从API 文档中查找具体

### 错误码说明,通过查看说明后问题仍未处理,使用Demo 测试是否正常,如果Demo 正常则

### 说明配置无问题,需要再查看下文档中典型场景的集成步骤,同步对比下Demo 集成步骤,

### 确认集成流程是否正确;如果Demo 也不正常,看下文档中常见咨询问题是否有问题答案;

### 若完成上述流程,问题仍未处理,可联系技术支持排查

### 2.资源访问问题排查:确认资源是否已经发布给登录用户,同步看下文档中常见咨询问

### 题是否有问题答案,如果仍未解决,使用Demo 测试是否正常,如果Demo 正常则说明配置

### 无问题,需要再查看下文档中典型场景的集成步骤,同步对比下Demo 集成步骤,确认集成

### 流程是否正确;若完成上述流程,问题仍未处理,可联系技术支持排查

## 3.3.2是否正确处理了免密认证

### 3.3.2.1注意事项

### 1.调用免密认证前检查是否调用SDK 初始化接口,并检测参数是否正确

### 2.先调接口检测是否支持免密认证,只有在成功登录后重启APP 的情况下才支持免密认证

### 3.参照API 接口使用说明处理免密认证接口回调

### 4.免密认证是使用上次登录成功缓存的token 走免密认证,如果token 失效会免密认证失

### 败需用重新登录,具体处理参考场景说明或API 使用说明

| 60 |  |
|---|---|

移动安全MBS SDK 集成指南(鸿蒙)

### 3.3.2.2测试步骤

### 1.登录管理平台,在设备中心查看设备

### 2.访问资源

### 3.杀掉SDK 应用重新启动

### 4.重启启动后测试资源访问

### 3.3.2.3期望结果

### 1.登录成功

### 2.设备状态正常

### 3.资源访问正常

### 4.安全防护策略生效

### 3.3.2.4失败排查

### 1.免密认证失败问题排查:查看接口回调错误码和错误信息描述,从API 文档中查找具体

### 错误码说明,通过查看说明后问题仍未处理,使用Demo 测试是否正常,如果Demo 正常

### 则说明配置无问题,需要再查看下文档中典型场景的集成步骤,同步对比下Demo 集成步

### 骤,确认集成流程是否正确;如果Demo 也不正常,看下文档中常见咨询问题是否有问题

### 答案;若完成上述流程,问题仍未处理,可联系技术支持排查

### 2.资源访问问题排查:确认资源是否已经发布给登录用户,同步看下文档中常见咨询问

### 题是否有问题答案,如果仍未解决,使用Demo 测试是否正常,如果Demo 正常则说明配

### 置无问题,需要再查看下文档中典型场景的集成步骤,同步对比下Demo 集成步骤,确认

### 集成流程是否正确;若完成上述流程,问题仍未处理,可联系技术支持排查

### 3.安全防护策略问题排查:确认安全防护策略是否已经下发给登录用户,同步看下文档中

### 常见咨询问题是否有问题答案,如果仍未解决,使用Demo 测试是否正常,如果Demo 正

### 常则说明配置无问题,需要再查看下文档中典型场景的集成步骤,同步对比下Demo 集成

### 步骤,确认集成流程是否正确;若完成上述流程,问题仍未处理,可联系技术支持排查

| 61 |  |
|---|---|

移动安全MBS SDK 集成指南(鸿蒙)

## 3.3.3是否正确处理了注销

### 3.3.3.1注意事项

### 1.检测集成sdk 应用是否处于登录状态

### 2.查看管理平台设备状态是否正常

### 3.注销会解绑设备绑定关系并关闭安全隧道,只有在APP 退出登录或某些特定场景才需

### 要调用注销

### 3.3.3.2测试步骤

### 1.登录集成SDK 应用

### 2.调用退出接口

### 3.在管理平台设备管理中查找设备

### 4.测试资源访问

### 3.3.3.3期望结果

### 1.集成SDK 应用退出成功

### 2.设备管理中查不到具体设备信息

### 3.资源无法访问

### 3.3.3.4失败排查

### 1.退出失败问题排查:查看退出接口回调错误码和错误信息描述,从API 文档中查找具体

### 错误码说明,通过查看说明后问题仍未处理,使用Demo 测试是否正常,如果Demo 正常

### 则说明配置无问题,需要再查看下文档中典型场景的集成步骤,同步对比下Demo 集成步

### 骤,确认集成流程是否正确;如果Demo 也不正常,看下文档中常见咨询问题是否有问题

### 答案;若完成上述流程,问题仍未处理,可联系技术支持排查

## 3.3.4是否正确处理了监听

### 3.3.4.1注意事项

### 1.SDK 状态监听属于全局监听,生命周期跟随APP

| 62 |  |
|---|---|

移动安全MBS SDK 集成指南(鸿蒙)

### 2.监听APP 使用过程中网络通道、设备、用户登录状态,当通道被服务器踢出,设备被

### 禁用或删除,用户被禁用或删除等会回调具体错误,并指示下一步执行动作

### 3.需要根据场景说明和接口使用说明正确处理回调

### 3.3.4.2测试步骤

### 1.集成SDK 应用中设置监听

### 2.应用正常登录

### 3.登录管理平台,在设备管理中找到具体设备,执行删除设备操作

### 4.应用前后台切换

### 3.3.4.3期望结果

### 1.能正常收到接口回调

### 2.接口回调中携带错误码、错误信息和下一步支持动作

### 3.应用退出登录

### 3.3.4.4失败排查

### 1.监听失败问题排查:优先使用Demo 测试是否正常,如果Demo 正常则说明配置无问题,

### 需要再查看下文档中典型场景的集成步骤,同步对比下Demo 集成步骤,确认集成流程是

### 否正确;如果Demo 也不正常,看下文档中常见咨询问题是否有问题答案;若完成上述流

### 程,问题仍未处理,可联系技术支持排查

# 4

# 常见问题汇总

# 4.1如何获取SDK 日志?

### 有几种方式可以获取SDK 日志,可根据不同的场景需求选择对应的日志采集方式

### 方法1:通过SDK 提供的日志导出函数获取

### 该方法适用于开发者集成SDK 时,实现自身应用导出日志功能。用于普通用户使用线上

### APP 遇到问题后,只需在APP 中导出日志给到APP 研发人员即可。

### 示例:

| 63 |  |
|---|---|

移动安全MBS SDK 集成指南(鸿蒙)

//开发人员通过该Api 获取SDP 日志文件导出路径,zip 包格式

```
UUMos.export Log(args,{
handleSDKEvent:(map:Map<string,Object>):void=>{
letlogPath=UUMosUtils.getMapString(UUCallbackKey.UU_KEY_MBS_LOGPATH,map,
"");
}
})
```

# 4.2集成过程中出现崩溃,应该如何处理?

### 1.集成开发先判断是否为集成SDK 后导致的崩溃问题

### 2.抓取崩溃日志排查

# 4.3应用能否获取SDK 版本号?

### 支持,可调用SDK方法获取,返回SDK 版本信息的JSON 字符串,排查问题时可将版本信

### 息一并发给指掌易SDK 开发协助排查

# 4.4SDK 登录阶段,出现"103接收超时,服务器无回应"提示,排

# 查步骤?

### 1.检查手机网络是否正常

### 2.确定SDP 网关正常开启,并检查调用SDK init 接口传递的sdp_host 配置正确

### 3.使用SDK Demo 应用,填写相同配置,若可登录成功则集成方需要检查SDK 调用参

### 数区别

### 4.若以上步骤未解决,需要导出SDK 日志排查

# 4.5SDK 登录阶段,出现"1004没有可访问的资源"的提示,排查步

# 骤?

### 1.检查SDP 管理端是否给当前帐号正确配置了隧道资源,若没有则需要添加隧道资源

### 配置,然后重新登录看是否解决

| 64 |  |
|---|---|

移动安全MBS SDK 集成指南(鸿蒙)

### 2.若以上步骤未解决,需要导出SDK 日志排查

# 4.6登录认证成功后,部分资源无法访问,排查步骤?

### 1.检查手机网络是否正常

### 2.联系SDP 管理员,检查无法访问的资源是否正确配置给当前用户

### 3.调用SDK网络检测方法,检查是否能正常连通该资源对应的业务服务器

### 4.若以上步骤未解决,需要导出SDK 日志排查

# 4.7SDK 是否有断链重连机制,集成应用是否需要关注?

### 集成应用调用SDK登录完成后,应用就可以访问内网资源了。对于设备网络切换或

### 网络断开恢复等,隧道会自动重连,无需用户关注。应用只需监听SDK setListener 状态回调,

### 如果未收到错误监听回调,集成应用就可以认为隧道是正常的,可以随时请求资源;如果收

### 到了错误监听回调,根据回调函数中返回的UUCallbackSuggest 下一步建议执行动作进行

### 处理,若集成应用确实需要获取状态来感知当前隧道是否正常,可以调用SDK checkSdpStatus

### 方法,只要返回为true,就可以认为当前隧道状态是正常连接的

# 4.8SDP 通道状态监听setListener(IUUSDKCallback callback)如何

# 使用?

### 对于设备网络切换或网络断开恢复等,隧道会自动重连,无需用户关注。集成应用若需

### 获取当前隧道状态来做业务流程处理,可关注通道关闭回调,根据回调函数中返回的

### UUCallbackSuggest 下一步建议执行动作进行处理

### 下一步执行动作参数枚举UUCallbackSuggest 说明

| 枚举值 | 描述 |
|---|---|
| UU CALLBACK SUGGEST FINISH _ _ _ | 流程已完成 |
| UU CALLBACK SUGGEST RELOGIN _ _ _ | 返回登录页面,执行重新登录 |
| UU CALLBACK SUGGEST ERASE _ _ _ | 执行设备擦除并关闭应用 |
| UU CALLBACK SUGGEST PROGRESS _ _ _ | 执行二次认证 |
| UU CALLBACK SUGGEST TIP _ _ _ | 弹出错误提示 |

| 65 |  |
|---|---|

移动安全MBS SDK 集成指南(鸿蒙)

| UU CALLBACK SUGGEST RETRY _ _ _ | 重试 |  |
|---|---|---|

# 4.9应用能否获取当前SDP 隧道连接状态?

### 支持,可调用SDK检测网络状态获取,该方法使用场景建议:

### 1.集成应用需在界面中显示隧道状态,可主动触发或周期性调用SDK checkSdpStatus

### 方法获取状态后展示

### 2.集成应用切换至前台,有立即发送网络请求需求前可调用SDK checkSdpStatus 方法,

### success 回调中发送网络请求

### 3.集成应用网络层拦截到业务请求失败后,如:手机熄屏切换为亮屏,应用切换至前

### 台,SDP 隧道会进行隧道恢复,该过程中若集成应用立即发送网络请求则可能触发业务请求

### 失败。可调用SDK checkSdpStatus 方法执行处理

# 4.10

# SDK 认证成功后,是否会代理集成SDK 应用的所有网络请

# 求?

### SDK 只会代理资源地址的网络请求,资源地址是需要在管理端配置并关联给登录用户

### 的,其他请求会则走应用原有逻辑发往互联网

# 4.11

# 同一个帐号可以在多少个设备上同时登录使用?

### 单SDP 场景

### 可在SDP 管理管理页面配置,系统管理->系统设置->用户配置,【设备绑定限制】项

### 配置,支持无限制,也可自定义限制,如下所示:

### 单MOS 场景

### 可在MOS 管理页面配置,基础管理->策略中心->全局策略->用户权限,【设备激

### 活】项配置,如下所示:

| 66 |  |
|---|---|

移动安全MBS SDK 集成指南(鸿蒙)

### SDP+MOS 场景

### 取以上配置交集

| 67 |  |
|---|---|
