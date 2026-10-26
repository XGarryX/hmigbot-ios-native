# 移动安全MBSSDK

# API 文档说明(鸿蒙)

移动安全MBS SDK API 文档说明(鸿蒙)

# 版权申明

本文档版权归指掌易科技有限公司(以下简称“指掌易”)所有,并保留一切权利,

非经本公司书面许可任何单位和个人不得擅自摘抄、复制本书内容的部分或者全部,并不得

以任何形式进行传播。对应本手册出现的其他公司的商标,产品标识和商品名称,由各自权

利人拥有。除非另有约定,本手册仅作为使用指导,本手册中的所有陈述、信息和建议,不

构成任何明示和暗示的担保。如需获取最新手册请联系指掌易科技有限公司产品部。

# 免责声明

本文档仅提供阶段性信息,所含内容可根据产品的实际情况随时更新,恕不另行通知。

如因文档使用不当造成的直接或间接损失,本公司不承担任何责任。

# 联系我们

网址:www.zhizhangyi.com

服务电话:4008987798

地址:北京市朝阳区北苑路58号航空科技大厦7层

| 2 |  |
|---|---|

移动安全MBS SDK API 文档说明(鸿蒙)

目录

移动安全MBSSDK..............................................................................................................................1

API文档说明(鸿蒙)..........................................................................................................................1

版权申明......................................................................................................................................... 2

免责声明......................................................................................................................................... 2

1

API 文档说明.............................................................................................................................. 4

1.1基础配置........................................................................................................................... 4

1.1.1initWithOnCreate......................................................................................................4

1.1.2initSandbox...............................................................................................................6

1.1.3初始化..................................................................................................................... 6

1.2认证操作........................................................................................................................... 7

1.2.1登录认证..................................................................................................................7

1.2.2免密认证..................................................................................................................9

1.2.3登出登录................................................................................................................11

1.2.4检测登录状态........................................................................................................ 12

1.2.5获取短信验证码.....................................................................................................13

1.2.6二次认证................................................................................................................16

1.2.7修改密码................................................................................................................18

1.2.8重置密码................................................................................................................19

1.3高级配置..........................................................................................................................25

1.3.1异常状态监听........................................................................................................ 25

1.3.2检测SDP隧道状态................................................................................................. 26

1.3.3开启水印................................................................................................................28

1.3.4关闭水印............................................................................................................... 29

1.4工具方法..........................................................................................................................29

1.4.1导出日志................................................................................................................29

1.4.2获取SDK 版本........................................................................................................ 31

2

常见数据结构.......................................................................................................................... 31

3

错误码说明..............................................................................................................................36

3.1SDP+MOS.........................................................................................................................36

| 3 |  |
|---|---|

移动安全MBS SDK API 文档说明(鸿蒙)

目录

移动安全MBSSDK............................................................................................................................... 1

API文档说明(鸿蒙)............................................................................................................................1

版权申明...........................................................................................................................................2

免责声明...........................................................................................................................................2

1

API 文档说明................................................................................................................................4

1.1基础配置............................................................................................................................. 4

1.1.1initWithOnCreate........................................................................................................4

1.1.2initSandbox................................................................................................................ 6

1.1.3初始化.......................................................................................................................6

1.2认证操作............................................................................................................................. 7

1.2.1登录认证................................................................................................................... 7

1.2.2免密认证................................................................................................................... 9

1.2.3登出登录................................................................................................................. 11

1.2.4检测登录状态.......................................................................................................... 12

1.2.5获取短信验证码.......................................................................................................13

1.2.6二次认证................................................................................................................. 16

1.2.7修改密码................................................................................................................. 18

1.2.8重置密码................................................................................................................. 19

1.3高级配置............................................................................................................................25

1.3.1异常状态监听.......................................................................................................... 25

1.3.2检测SDP隧道状态...................................................................................................26

1.3.3开启水印................................................................................................................. 28

1.3.4关闭水印................................................................................................................. 29

1.4工具方法............................................................................................................................29

1.4.1导出日志................................................................................................................. 29

1.4.2获取SDK 版本.......................................................................................................... 31

2

常见数据结构............................................................................................................................ 31

3

错误码说明................................................................................................................................36

3.1SDP+MOS.......................................................................................................................... 36

# 1

# API文档说明

## 1.1基础配置

## 1.1.1initWithOnCreate

| 类名 | UUMos |
|---|---|
| 方法 | initWithOnCreate(context:Context,args: Map<string, Object>): number |
| 描述 | 初始化 SDK 模块 在 UIAbility 的 onCreate 中调用,【必选接口】同步接口 |

移动安全MBS SDK API 文档说明(鸿蒙)

| 参数 | context:启动上下文 UIAbilityContext 类型 args:接口参数,按照接口协议添加需要的登录信息: 接口传参键值对 ,{key=xxx,value=xxx}key 使用枚举字符串 ,详细定义查看 UUCommParamsKey 枚举类定义 入参: mos debug 调试模式,是否是 Debug 模式,boolean 类型,如果是 Debug 模式, _ 会打印调试日志,可选参数 |
|---|---|
| 返回 | number 类型 0: 初始化成功, 其他: 初始化失败 |
| 示例 | export default class EntryAbility extends UIAbility { onCreate(want: Want, launchParam: AbilityConstant.LaunchParam): void { |

| 4 |  |
|---|---|

移动安全MBS SDK API 文档说明(鸿蒙)

|  | let args: Map<string, Object> = new Map () ; UUMos.initWithOnCreate(this.context,args) } } |
|---|---|

## 1.1.2initSandbox

| 类名 | UUMos |
|---|---|
| 方法 | initSandbox(stage: AbilityStage, objectMap: Map<string, Object>): void |
| 描述 | 初始化沙箱 SDK 模块,有沙箱能力场景调用 在 AbilityStage 的 onCreate 中调用,【非必选接口】同步接口 AbilityStage 的实现方法请参考官方文档: https://developer.huawei.com/consumer/cn/doc/harmonyos-guides/abilitystage-000000 1774119982 |
| 参数 | stage:启动上下文 AbilityStage 类型 args:接口参数,按照接口协议添加需要的登录信息: 接口传参键值对,{key=xxx,value=xxx}key 使用枚举字符串,详细定义查看 |
| 返回 | 无 |
| 示例 | export default class MyAbilityStage extends AbilityStage { onCreate(): void { // 应用的HAP 在首次加载的时,为该Module 初始化操作 let args: Map<string, object> = new Map () ; UUMos.initSandbox(this,args); } onAcceptWant(want: Want): string { // 仅 specified 模式下触发 return 'MyAbilityStage'; } } |

## 1.1.3初始化

| 类名 | UUMos |
|---|---|
| 方法 | init(ctx: Context, args: Map<string, Object>, initBack: UUInitBack): number |
| 描述 | SDK 初始化,SDK 初始化,同步接口 |

| 5 |  |
|---|---|

移动安全MBS SDK API 文档说明(鸿蒙)

|  | 注:必选方法,调用初始化接口成功后才能调用SDK 其他接口 |
|---|---|
| 参数 | context:启动上下文 Context 类型 args:接口参数,按照接口协议添加需要的登录信息: 接 口传参键值对 ,{key=xxx,value=xxx}key 使用枚举字符 串 ,详细定义查看 UUInitParamsKey 枚举类定义 |
| 返回 | number 类型 0:调用成功,-1:调用失败 |
| 示例 | let args: Map<string, Object> = new Map(); //MOS 服务器地址,string 类型,必填 args.set(UUInitParamsKey.UU INIT MBS URL, “ https://172.16.30.36:9070”); _ _ _ args.set(UUInitParamsKey.UU INIT MBS ORGCODE, “租户信息(zzydemo)”); _ _ _ //SDP 配置 // 安全网关服务器地址,支持主机名和 IP 地,string 类型 args.set(UUInitParamsKey.UU INIT SDP HOST, “172.16.30.82”); _ _ _ args.set(UUInitParamsKey.UU INIT SDP PORT, new Number(port)); //SDP 端口 _ _ _ initBack = new UUInitBack(); UUMos.init(context, args, initBack); |

## 1.2认证操作

## 1.2.1登录认证

| 类名 | UUMos |  |
|---|---|---|
| 方法 | login(args: Map<string, Object>, callBack: IUUSDKCallback): number |  |
| 描述 | SDK 登录接口,【必选接口】,异步接口 注:必选方法,建议第三方应用登录界面调用 |  |
| 参数 | args:接口参数,按照接口协议添加需要的登录信息: 接 口传参键值对 ,{key=xxx,value=xxx} 使用枚举字符 串 ,详细定义查看 UULoginParamsKey 枚举类定义 入参: login loginname 登录用户名,String 类型,必选项 _ login password 登录密码,String 类型,必选项 _ login logintype 登陆类型,UUAuthType 枚举 int 值,支持类型介绍参考 UUAuthType _ 枚举定义,必选项 |  |

|  | 6 |  |
|---|---|---|

移动安全MBS SDK API 文档说明(鸿蒙)

|  | login loginmode 登录模式,UUSDKMode 枚举类型 int 值 0:仅启动 mos,1:仅启动 _ sdp ,2:启用 MOS 和 SDP,必选项 mos deviceid //设备 id 用于标识设备唯一性,项目如果需要自定义设备唯一标识 _ 需要传递 mos deviceid ,32 位字符串类型,可选项 _ callBack: IUUSDKCallback 接口类 export interface IUUSDKCallback{ /** * 接口调用回调 * @param map 回传参数 * 接口传参键值对,{key=xxx,value=xxx} * key 定义: * key=”kMosCallbackCode” ,value:int 类型,接口调用响应码,0:成功:-1:失败,其他参考 错误码定义 * key= ”kMosCallbackError ” ,value:String 类型,接口调用响应错误信息, * @return */ handleSDKEvent:(map:Map<string, Object>) => void; } |
|---|---|
| 返回 | number 类型 0:调用成功,-1:调用失败 |
| 示例 | 用户名密码登录代码示例 let args: Map<string, Object> = new Map(); //登陆类型,UUAuthType 枚举int 类型,支持类型介绍参考UUAuthType 枚举定义 args.set(UULoginParamsKey.UU LOGIN LOGINTYPE, UUAuthType.AUTH TYPE PASSWORD); _ _ _ _ //登录用户名,String 类型,必填 args.set(UULoginParamsKey.UU LOGIN LOGINNAME, mUserName); _ _ //登录密码,String 类型,必填 args.set(UULoginParamsKey.UU LOGIN PASSWORD, mPassword); _ _ //0:仅启动 mos,1:仅启动sdp ,2:启用MOS 和SDP,SDP 前置 必填 args.set(UULoginParamsKey.UU LOGIN LOGINMODE, UUSDKMode.UU MODE SDP SANDBOX); _ _ _ _ _ //设备 id 用于标识设备唯一性,项目如果需要自定义设备唯一标识需要传递 mbs securityId,32 _ 位字符串类型,非必填 // args.put(UU LOGIN DEVICEID,"APP 自己生成设备ID"); _ _ //设置 SDP 通道状态监听 UUMos.login(args, { handleSDKEvent: (map: Map<string, Object>): void => { if (map != null) { let resultCode = UUMosUtils.getMapNumber(UUCallbackKey.UU KEY KMOSCALLBACKERRORCODE, map, -1); _ _ let message = UUMosUtils.getMapString(UUCallbackKey.UU KEY KMOSCALLBACKERROR, map, ""); _ _ let suggest: UUCallbackSuggest = UUMosUtils.getMapEnumSuggest(UUCallbackKey.UU KEY KMOSCALLBACKSUGGEST, map, _ _ UUCallbackSuggest.UU CALLBACK SUGGEST FINISH); _ _ _ |

| 7 |  |
|---|---|

移动安全MBS SDK API 文档说明(鸿蒙)

|  | if (suggest == UUCallbackSuggest.UU CALLBACK SUGGEST TIP) { _ _ _ //提示错误信息 message promptAction.showToast({ message: "登录失败:" + message + ":" + resultCode, duration: 2000}) } else if (suggest == UUCallbackSuggest.UU CALLBACK SUGGEST FINISH) { _ _ _ promptAction.showToast({message: "登录成功",duration: 2000}) router.replaceUrl({url:'pages/MainPage'}).then(()=>{ console.info('testTag', `MainPage .`); }).catch((err:BusinessError)=>{ console.error('testTag',"MainPage ") }) } else if (suggest == UUCallbackSuggest.UU CALLBACK SUGGEST SAFECONTROL) { _ _ _ let authType: UUSafeControlType = UUMosUtils.getMapEnumSuggestSafeControlType(UUCallbackKey.UU KEY KMOSSAFECONTROLTYPE, _ _ map, UUSafeControlType.SAFE CONTROL MODIFY PASSWORD); _ _ _ if (authType == UUSafeControlType.SAFE CONTROL MODIFY PASSWORD) { _ _ _ }}}}}); |
|---|---|

## 1.2.2免密认证

| 类名 |  | UUMos |  |
|---|---|---|---|
| 方法 |  | sign(args: Map<string, Object>, callBack: IUUSDKCallback): number |  |
| 描述 |  | SDK 登录接口,【必选接口】,异步接口 注:必选方法,建议第三方应用登录界面调用, |  |
| 参数 |  | args:接口参数,按照接口协议添加需要的免密认证信息: 接口传参键值对,{key=xxx,value=xxx} callBack: IUUSDKCallback 接口类 export interface IUUSDKCallback{ /** * 接口调用回调 * @param map 回传参数 * 接口传参键值对,{key=xxx,value=xxx} * key 定义: * key=”kMosCallbackCode” ,value:int 类型,接口调用响应码,0:成功:-1:失败,其他参考 错误码定义 * key= ”kMosCallbackError ” ,value:String 类型,接口调用响应错误信息, * @return */ handleSDKEvent:(map:Map<string, Object>) => void; |  |
|  |  |  |  |
|  | 8 |  |  |

移动安全MBS SDK API 文档说明(鸿蒙)

|  | } |
|---|---|
| 返回 | number 类型 0:调用成功,-1:调用失败 |
| 示例 | if(UUMos.checkSign() == 0) { //设置 SDP 通道状态监听 let args:Map<string, Object> = new Map(); UUMos.sign(args, { handleSDKEvent:(map:Map<string, Object>):void=>{ if(map != null) {//错误码 let resultCode = UUMosUtils.getMapNumber(UUCallbackKey.UU KEY KMOSCALLBACKERRORCODE,map,-1); _ _ //错误码对应信息描述 let message = UUMosUtils.getMapString(UUCallbackKey.UU KEY KMOSCALLBACKERROR, map,""); _ _ //返回接收到状态码后的下一步执行动作,枚举型 let suggest:UUCallbackSuggest = UUMosUtils.getMapEnumSuggest(UUCallbackKey.UU KEY KMOSCALLBACKSUGGEST,map,UUCallbackS _ _ uggest.UU CALLBACK SUGGEST FINISH); _ _ _ if(suggest == UUCallbackSuggest.UU CALLBACK SUGGEST TIP) _ _ _ { //弹出错误码 let msg:string = message + ":" + resultCode; promptAction.showToast({message: msg,duration: 2000}) router.replaceUrl({url:'pages/LoginPage'}).then(()=>{ console.info('testTag', `Succeeded .`); }).catch((err:BusinessError)=>{ console.error('testTag',"Failed ") }) } else if(suggest == UUCallbackSuggest.UU CALLBACK SUGGEST FINISH) _ _ _ { //调用成功,流程已完成,跳转到APP 主界面 router.replaceUrl({url:'pages/MainPage'}).then(()=>{ console.info('testTag', `Succeeded .`); }).catch((err:BusinessError)=>{ console.error('testTag',"Failed ") }) } else if(suggest == UUCallbackSuggest.UU CALLBACK SUGGEST RELOGIN) _ _ _ { //应用需要返回登录页面,重新执行SDK 登录流程 router.replaceUrl({url:'pages/LoginPage'}).then(()=>{ |

| 9 |  |
|---|---|

移动安全MBS SDK API 文档说明(鸿蒙)

|  | console.info('testTag', `Succeeded .`); }).catch((err:BusinessError)=>{ console.error('testTag',"Failed ") }) } else if(suggest == UUCallbackSuggest.UU CALLBACK SUGGEST ERASE) _ _ _ { //管理员执行了设备擦除策略,SDK 将主动执行擦除应用数据并关闭应用 } else if(suggest == UUCallbackSuggest.UU CALLBACK SUGGEST RETRY) _ _ _ { //由于网络原因导致签到失败,建议弹框提示然后重试 promptAction.showToast({ message: message, duration: 2000 }) } } } }); } |
|---|---|

## 1.2.3登出登录

| 类名 | UUMos |
|---|---|
| 方法 | logout(args: Map<string, Object>, callBack: IUUSDKCallback): number |
| 描述 | SDK 登出接口,【非必选接口】异步接口 注:非必选方法,建议第三方集成应用登出后调用 |
| 参数 | args:接口参数,按照接口协议添加需要的登出信息: 接 口传参键值对 ,{key=xxx,value=xxx} 使用枚举字符 串 ,详细定义查看 UUCommParamsKey 枚举类定义 入参: sdp close tunnel 断开 sdp 通道,1:断开 SDP 连接,0:退出登录,适用于仅断开 SDP _ _ 通道不退出账号登录的场景,可选项 callBack: IUUSDKCallback 接口类 export interface IUUSDKCallback{ /** * 接口调用回调 * @param map 回传参数 * 接口传参键值对,{key=xxx,value=xxx} |

| 10 |  |
|---|---|

移动安全MBS SDK API 文档说明(鸿蒙)

|  | * key 定义: * key=”kMosCallbackCode” ,value:int 类型,接口调用响应码,0:成功:-1:失败,其他参考 错误码定义 * key= ”kMosCallbackError ” ,value:String 类型,接口调用响应错误信息, * @return */ handleSDKEvent:(map:Map<string, Object>) => void; } |
|---|---|
| 返回 | number 类型 0:调用成功,-1:调用失败 |
| 示例 | let args:Map<string, Object> = new Map(); UUMos.logout(args,{ handleSDKEvent:(map:Map<string, Object>):void=>{ //错误码 let resultCode = UUMosUtils.getMapNumber(UUCallbackKey.UU KEY KMOSCALLBACKERRORCODE,map,-1); _ _ //错误码对应信息描述 let message = UUMosUtils.getMapString(UUCallbackKey.UU KEY KMOSCALLBACKERROR,map,""); _ _ //返回接收到状态码后的下一步执行动作,枚举型 let suggest:UUCallbackSuggest = UUMosUtils.getMapEnumSuggest(UUCallbackKey.UU KEY KMOSCALLBACKSUGGEST,map,UUCallbackS _ _ uggest.UU CALLBACK SUGGEST FINISH); _ _ _ if(suggest == UUCallbackSuggest.UU CALLBACK SUGGEST FINISH) _ _ _ { //退回到登录界面 promptAction.showToast({message: "退出登录成功:" + message + ":" + resultCode, duration: 2000 }) router.replaceUrl({url:'pages/LoginPage'}).then(()=>{ console.info('testTag', `Succeeded .`); }).catch((err:BusinessError)=>{ console.error('testTag',"Failed ") })}} }) |

## 1.2.4检测登录状态

| 类名 | UUMos |
|---|---|
| 方法 | checkSign():number |
| 描述 | 【非必选接口】,同步接口 判断本地是否存在缓存的会话可以走 sign 流程 |

| 11 |  |
|---|---|

移动安全MBS SDK API 文档说明(鸿蒙)

| 参数 | 无 |
|---|---|
| 返回 | 0:已登录,走免密认证流程 -1:未登录,走登录流程 |
| 示例 | int res = UUMos.checkSign() If(res == 0) { //已经登录过,走免密认证流程 } else { //未登录,走登录流程 } |

## 1.2.5获取短信验证码

### 1.2.5.1.获取短信验证码

| 类名 | UUMos |
|---|---|
| 方法 | getSmsCode(objectMap: Map<string, Object>, callBack: IUUSDKCallback) |
| 描述 | 用于短信验证码登录时,获取验证码,【非必选接口】异步接口 |
| 参数 | args:接口参数: 接口传参键值对 ,{key=xxx,value=xxx}key 使用枚举字符串 ,详细定义查看 UUSmsCodeParamsKey 枚举类定义 入参: phone number 手机号码 字符串类型,必选项 _ country code 国家电话代码 字符串类型,可选项,默认+86 即中国 _ callBack: IUUSDKCallback 接口类 export interface IUUSDKCallback{ /** * 接口调用回调 * @param map 回传参数 * 接口传参键值对,{key=xxx,value=xxx} * key 定义: * key=”kMosCallbackCode” ,value:int 类型,接口调用响应码,0:成功:-1:失败,其他参考 |

| 12 |  |
|---|---|

移动安全MBS SDK API 文档说明(鸿蒙)

|  | 错误码定义 * key= ”kMosCallbackError ” ,value:String 类型,接口调用响应错误信息, * @return */ handleSDKEvent:(map:Map<string, Object>) => void; } |
|---|---|
| 返回 | 无 |
| 示例 | SDP 获取短信验证码代码示例 Map<String, Object> map = new HashMap<>(); //手机号 map.put(UU COMM PHONE NUMBER.stringValue(),”13300000000”); _ _ _ // //国家电话代码 字符串类型,可选项,默认+86 即中国 map.put(UU COMM COUNTRY CODE.stringValue(),"+86"); _ _ _ UUMos.getSmsCode(map, new IUUSDKCallback() { @Override public void handleSDKEvent(Map<String, Object> map) { if(map != null){ int resultCode = UUMosUtils.getMapInteger(UU KEY KMOSCALLBACKERRORCODE.stringValue(),map,-1); _ _ String message = UUMosUtils.getMapString(UU KEY KMOSCALLBACKERROR.stringValue(), map,""); _ _ UUCallbackSuggest suggest = UUMosUtils.getMapEnumSuggest(UU KEY KMOSCALLBACKSUGGEST.stringValue(),map,UU CALLBACK _ _ _ SUGGEST FINISH); _ _ if(suggest == UUCallbackSuggest.UU CALLBACK SUGGEST TIP){ _ _ _ //提示错误信息 message } else if(suggest == UUCallbackSuggest.UU CALLBACK SUGGEST FINISH{ _ _ _ //验证码已下发 //短信发送倒计时,数字,单位秒 int smsCountdown = |

| 13 |  |
|---|---|

移动安全MBS SDK API 文档说明(鸿蒙)

|  | UUMosUtils.getMapInteger(UU KEY KMOSSMSCOUNTDOWN.stringValue(),map,0); _ _ }}}}); |
|---|---|

### 1.2.5.2.刷新短信验证码

| 类名 |  | UUMos |  |
|---|---|---|---|
| 方法 |  | refreshSmsCode(objectMap: Map<string, Object>, callBack: IUUSDKCallback) |  |
| 描述 |  | 用于二次认证失败或者短信验证码超时刷新短信验证码,【非必选接口】异步接口 |  |
| 参数 |  | args:接口参数: 接口传参键值对 ,{key=xxx,value=xxx}key 使用枚举字符串 ,详细定义查看 UUSmsCodeParamsKey 枚举类定义 callBack: IUUSDKCallback 接口类 export interface IUUSDKCallback{ /** * 接口调用回调 * @param map 回传参数 * 接口传参键值对,{key=xxx,value=xxx} * key 定义: * key=”kMosCallbackCode” ,value:int 类型,接口调用响应码,0:成功:-1:失败,其他参考 错误码定义 * key= ”kMosCallbackError ” ,value:String 类型,接口调用响应错误信息, * @return */ handleSDKEvent:(map:Map<string, Object>) => void; } |  |
| 返回 |  | 无 |  |
| 示例 |  | let map: Map<string, Object> = new Map(); UUMos.refreshSmsCode(map, { handleSDKEvent: (map: Map<string, Object>): void => { if (map) { //接口调用状态码 let resultCode = UUMosUtils.getMapNumber(UUCallbackKey.UU KEY KMOSCALLBACKERRORCODE, map, -1); _ _ |  |
|  | 14 |  |  |

移动安全MBS SDK API 文档说明(鸿蒙)

|  | //错误描述信息 let message UUMosUtils.getMapString(UUCallbackKey.UU KEY KMOSCALLBACKERROR, map, ""); _ _ //返回接收到状态码后的下一步执行动作,枚举型 let suggest = UUMosUtils.getMapEnumSuggest(UUCallbackKey.UU KEY KMOSCALLBACKSUGGEST, map, _ _ UUCallbackSuggest.UU CALLBACK SUGGEST FINISH); _ _ _ //短信发送倒计时,数字,单位秒 let smsCountdown = UUMosUtils.getMapNumber(UUCallbackKey.UU KEY KMOSSMSCOUNTDOWN, map, 60); _ _ if (suggest == UUCallbackSuggest.UU CALLBACK SUGGEST TIP) { _ _ _ //刷新验证码失败,提示错误信息 message promptAction.showToast({message: message,duration: 2000}) } else if (suggest == UUCallbackSuggest.UU CALLBACK SUGGEST FINISH) { _ _ _ promptAction.showToast({message: "刷新验证码成功",duration: 2000 }) } }}}); |
|---|---|

## 1.2.6二次认证

| 类名 | UUMos |
|---|---|
| 方法 | void secondaryAuth(Map<String, Object> args, IUUSDKCallback callBack) |
| 描述 | SDK 二次认证接口,【非必选接口】,异步接口 注:非必选方法,服务器开启二次认证场景使用, |
| 参数 | args:接口参数,按照接口协议添加需要的登录信息: 接 口传参键值对 ,{key=xxx,value=xxx} 使用枚举字符 串 ,详细定义查看 UULoginParamsKey 枚举类定义 入参: login password 认证密码,String 类型,可选项, _ 当二次认证类型为 AUTH TYPE SECOND CUSTOM 时使用 _ _ _ login Identify code 短信验证码,String 类型,可选项 _ _ 当二次认证类型为 AUTH TYPE SECOND SMS 时使用 _ _ _ |

| 15 |  |
|---|---|

移动安全MBS SDK API 文档说明(鸿蒙)

|  | callBack: IUUSDKCallback 接口类 export interface IUUSDKCallback{ /** * 接口调用回调 * @param map 回传参数 * 接口传参键值对,{key=xxx,value=xxx} * key 定义: * key=”kMosCallbackCode” ,value:int 类型,接口调用响应码,0:成功:-1:失败,其他参考 错误码定义 * key= ”kMosCallbackError ” ,value:String 类型,接口调用响应错误信息, * @return */ handleSDKEvent:(map:Map<string, Object>) => void; } |
|---|---|
| 返回 | 无 |
| 示例 | //短信二次认证代码示例 let args: Map<string, Object> = new Map(); //登陆类型,UUAuthType 枚举int 类型,支持类型介绍参考UUAuthType 枚举定义 args.set(UULoginParamsKey.UU LOGIN LOGINTYPE,UUSecondaryAuthType.AUTH TYPE SECOND SMS) _ _ _ _ _ ; //登录用户名,String 类型,必填 args.set(UULoginParamsKey.UU LOGIN IDENTIFY CODE, smsCode); _ _ _ //设置 SDP 通道状态监听 UUMos.secondaryAuth(args, { handleSDKEvent: (map: Map<string, Object>): void => { if (map) { //错误码 let resultCode = UUMosUtils.getMapNumber(UUCallbackKey.UU KEY KMOSCALLBACKERRORCODE, map, -1); _ _ //错误码对应信息描述 let message = UUMosUtils.getMapString(UUCallbackKey.UU KEY KMOSCALLBACKERROR, map, ""); _ _ //返回接收到状态码后的下一步执行动作,枚举型 let suggest = UUMosUtils.getMapEnumSuggest(UUCallbackKey.UU KEY KMOSCALLBACKSUGGEST, map, _ _ UUCallbackSuggest.UU CALLBACK SUGGEST FINISH); _ _ _ if (suggest == UUCallbackSuggest.UU CALLBACK SUGGEST TIP) { _ _ _ //提示错误信息 message promptAction.showToast({message: "登录失败:" + message + ":" + resultCode, duration: 2000}) } else if (suggest == UUCallbackSuggest.UU CALLBACK SUGGEST FINISH) { _ _ _ //认证成功,认证结束进入主应用 |

| 16 |  |
|---|---|

移动安全MBS SDK API 文档说明(鸿蒙)

|  | promptAction.showToast({message: "登录成功",duration: 2000}) router.replaceUrl({ url: 'pages/MainPage' }).then(() => { console.info('testTag', `MainPage .`); }).catch((err: BusinessError) => { console.error('testTag', "MainPage ") }) } }} }); |
|---|---|

## 1.2.7修改密码

| 类名 | UUMos |
|---|---|
| 方法 | modifyPassword(args: Map<string, Object>, callBack: IUUSDKCallback):void |
| 描述 | SDK 修改密码接口,【非必选接口】 异步接口 注:非必选方法,服务器开启首次登录强制修改密码场景使用, |
| 参数 | args:接口参数,按照接口协议添加需要的信息: 接 口传参键值对 ,{key=xxx,value=xxx} 使用枚举字符 串 ,详细定义查看 UULoginParamsKey 枚举类定义 入参: login password 原密码,String 类型,必填, _ login new password 新密码,String 类型,必填 _ _ callBack: IUUSDKCallback 接口类 export interface IUUSDKCallback{ /** * 接口调用回调 * @param map 回传参数 * 接口传参键值对,{key=xxx,value=xxx} * key 定义: * key=”kMosCallbackCode” ,value:int 类型,接口调用响应码,0:成功:-1:失败,其他参考 错误码定义 * key= ”kMosCallbackError ” ,value:String 类型,接口调用响应错误信息, * @return */ handleSDKEvent:(map:Map<string, Object>) => void; } |
| 返回 | 无 |

| 17 |  |
|---|---|

移动安全MBS SDK API 文档说明(鸿蒙)

| 示例 | 修改密码代码示例 let args: Map<string, Object> = new Map(); //原密码,String 类型,必填 args.set(UULoginParamsKey.UU LOGIN PASSWORD, oldPwd); _ _ //新密码,String 类型,必填 args.set(UULoginParamsKey.UU LOGIN NEW PASSWORD, newPwd); _ _ _ UUMos.modifyPassword(args, { handleSDKEvent: (map: Map<string, Object>): void => { if (map) { //错误码 let resultCode = UUMosUtils.getMapNumber(UUCallbackKey.UU KEY KMOSCALLBACKERRORCODE, map, -1); _ _ //错误码对应信息描述 let message = UUMosUtils.getMapString(UUCallbackKey.UU KEY KMOSCALLBACKERROR, map, ""); _ _ //返回接收到状态码后的下一步执行动作,枚举型 let suggest = UUMosUtils.getMapEnumSuggest(UUCallbackKey.UU KEY KMOSCALLBACKSUGGEST, map, _ _ UUCallbackSuggest.UU CALLBACK SUGGEST FINISH); _ _ _ if (suggest == UUCallbackSuggest.UU CALLBACK SUGGEST TIP) { _ _ _ //提示错误信息 message promptAction.showToast({message: "修改密码失败",duration: 2000}) } else if (suggest == UUCallbackSuggest.UU CALLBACK SUGGEST FINISH) { _ _ _ //密码重置成功,重新登录 promptAction.showToast({message: "密码修改成功,请重新登录",duration: 2000}) router.back() } } } }); |
|---|---|

## 1.2.8重置密码

### 1.2.8.1.获取验证码

| 类名 | UUMos |
|---|---|
| 方法 | getResetPasswordSmsCode(args: Map<string, Object>, callBack: IUUSDKCallback) |
| 描述 | 用于重置密码时获取验证码,调用成功后会给手机号下发验证码,【非必选接口】 异步接口 |
| 参数 | args:接口参数: |

| 18 |  |
|---|---|

移动安全MBS SDK API 文档说明(鸿蒙)

|  | 接口传参键值对 ,{key=xxx,value=xxx}key 使用枚举字符串 ,详细定义查看 UUSmsCodeParamsKey 枚举类定义 入参: phone number 手机号码 字符串类型,必选项 _ country code 国家电话代码 字符串类型,可选项,默认+86 即中国 _ mos deviceid //设备 id 用于标识设备唯一性,项目如果需要自定义设备 _ 唯一标识需要传递 mos deviceid ,32 位字符串类型,非必填 _ callBack: IUUSDKCallback 接口类 export interface IUUSDKCallback{ /** * 接口调用回调 * @param map 回传参数 * 接口传参键值对,{key=xxx,value=xxx} * key 定义: * key=”kMosCallbackCode” ,value:int 类型,接口调用响应码,0:成功:-1:失败,其他参考 错误码定义 * key= ”kMosCallbackError ” ,value:String 类型,接口调用响应错误信息, * @return */ handleSDKEvent:(map:Map<string, Object>) => void; } |
|---|---|
| 返回 | 无 |
| 示例 | let map: Map<string, Object> = new Map(); //手机号 map.set(UUSmsCodeParamsKey.UU COMM PHONE NUMBER, phoneNumber); _ _ _ //国家电话代码 字符串类型,可选项,默认+86 即中国 map.set(UUSmsCodeParamsKey.UU COMM COUNTRY CODE, "+86"); _ _ _ UUMos.getResetPasswordSmsCode(map, { handleSDKEvent: (map: Map<string, Object>): void => { if (map != null) { //错误码 let resultCode = UUMosUtils.getMapNumber(UUCallbackKey.UU KEY KMOSCALLBACKERRORCODE, map, -1); _ _ |

| 19 |  |
|---|---|

移动安全MBS SDK API 文档说明(鸿蒙)

|  | //错误码对应信息描述 let message = UUMosUtils.getMapString(UUCallbackKey.UU KEY KMOSCALLBACKERROR, map, ""); _ _ //返回接收到状态码后的下一步执行动作,枚举型 let suggest: UUCallbackSuggest = UUMosUtils.getMapEnumSuggest(UUCallbackKey.UU KEY KMOSCALLBACKSUGGEST, _ _ map,UUCallbackSuggest.UU CALLBACK SUGGEST FINISH); _ _ _ let smsCountdown = UUMosUtils.getMapNumber(UUCallbackKey.UU KEY KMOSSMSCOUNTDOWN, map, 0); //短信验证码 _ _ 倒计时 if (suggest == UUCallbackSuggest.UU CALLBACK SUGGEST TIP) { _ _ _ //获取短信验证码失败,提示错误信息 message promptAction.showToast({message: message,duration: 2000}) } else if (suggest == UUCallbackSuggest.UU CALLBACK SUGGEST FINISH) { _ _ _ //短信验证码获取成功 promptAction.showToast({message: "验证码已下发",duration: 2000}) } }} }); |
|---|---|

### 1.2.8.2.校验验证码

| 类名 | UUMos |
|---|---|
| 方法 | checkSmsCode(args: Map<string, Object>, callBack: IUUSDKCallback) |
| 描述 | 用于重置密码时校验身份,【非必选接口】异步接口 |
| 参数 | args:接口参数: 接口传参键值对 ,{key=xxx,value=xxx}key 使用枚举字符串 ,详细定义查看 UUSmsCodeParamsKey 枚举类定义 入参: phone number 手机号码 字符串类型,必选项 _ |

| 20 |  |
|---|---|

移动安全MBS SDK API 文档说明(鸿蒙)

|  | country code 国家电话代码 字符串类型,可选项,默认+86 即中国 _ smscode 短信验证码 callBack: IUUSDKCallback 接口类 export interface IUUSDKCallback{ /** * 接口调用回调 * @param map 回传参数 * 接口传参键值对,{key=xxx,value=xxx}使用枚举字符串,详细定义查看 UUCallbackKey 枚举类定义 * pwdLevel 密码复杂度 密码复杂度等级,1-简单,2-中等,3- 复杂 * 密码复杂度 密码复杂度等级,1-简单,2-中等,3-复杂 * 简单:密码需包含数字、大写字母、小写字母、符号中的一项,8-20 个字符 * 中等:密码需包含数字、大写字母、小写字母、符号中的两项,8-20 个字符 * 复杂:密码需包含数字、大写字母、小写字母、符号全部四项,8-20 个字符 * * @return */ handleSDKEvent:(map:Map<string, Object>) => void; } |
|---|---|
| 返回 | 无 |
| 示例 | let args: Map<string, Object> = new Map(); //手机号 args.set(UUSmsCodeParamsKey.UU COMM PHONE NUMBER,phoneNumber); _ _ _ //国家电话代码 字符串类型,可选项,默认+86 即中国 args.set(UUSmsCodeParamsKey.UU COMM COUNTRY CODE,"+86"); _ _ _ //短信验证码 args.set(UUCommParamsKey.UU COMM MOS SMSCODE,smsCode); _ _ _ UUMos.checkSmsCode(args, { handleSDKEvent: (map: Map<string, Object>): void => { if (map != null) { let resultCode = UUMosUtils.getMapNumber(UUCallbackKey.UU KEY KMOSCALLBACKERRORCODE, map, -1); _ _ let message = |

| 21 |  |
|---|---|

移动安全MBS SDK API 文档说明(鸿蒙)

|  | UUMosUtils.getMapString(UUCallbackKey.UU KEY KMOSCALLBACKERROR, map, ""); _ _ let suggest: UUCallbackSuggest = UUMosUtils.getMapEnumSuggest(UUCallbackKey.UU KEY KMOSCALLBACKSUGGEST, map, _ _ UUCallbackSuggest.UU CALLBACK SUGGEST FINISH); _ _ _ //密码复杂度 密码复杂度等级,1-简单,2-中等,3-复杂,默认 1,密码复杂度在管理端配置,密码 重置时需要校验密码复杂度是否符合要求 //简单:密码长度不小于 6 位,密码内容中只需使用数字、字母、符号中的一项 //中等:密码长度不小于 8 位,密码内容需包含数字、字母、符号中的两项 //复杂:密码长度不小于 8 位,密码内容需包含数字、字母、符号这三项 let pwdLevel = UUMosUtils.getMapNumber(UUCallbackKey.UU KEY MOS PWDLEVEL,map,0);//密码复杂度 _ _ _ if (suggest == UUCallbackSuggest.UU CALLBACK SUGGEST TIP) { _ _ _ //提示错误信息 message promptAction.showToast({message: "验证码校验失败:" + message + ":" + resultCode, duration: 2000}) } else if (suggest == UUCallbackSuggest.UU CALLBACK SUGGEST FINISH) { _ _ _ promptAction.showToast({message: "验证码校验成功",duration: 2000}) router.replaceUrl({ url: 'pages/ResetPasswordPage' }).then(() => { console.info('testTag', `MainPage .`); }).catch((err: BusinessError) => { console.error('testTag', "MainPage ") }) }}}}); |
|---|---|

### 1.2.8.3.重置密码

| 类名 | UUMos |
|---|---|
| 方法 | resetPassword(args: Map<string, Object>, callBack: IUUSDKCallback) |
| 描述 | 重置用户密码,【非必选接口】异步接口 |
| 参数 | args:接口参数: |

| 22 |  |
|---|---|

移动安全MBS SDK API 文档说明(鸿蒙)

|  | 接口传参键值对 ,{key=xxx,value=xxx}key 使用枚举字符串 ,详细定义查看 UUSmsCodeParamsKey 枚举类定义 入参: login new password 新密码,String 类型,必填 _ _ callBack: IUUSDKCallback 接口类 export interface IUUSDKCallback{ /** * 接口调用回调 * @param map 回传参数 * 接口传参键值对,{key=xxx,value=xxx} * key 定义: * key=”kMosCallbackCode” ,value:int 类型,接口调用响应码,0:成功:-1:失败,其他参考 错误码定义 * key= ”kMosCallbackError ” ,value:String 类型,接口调用响应错误信息, * @return */ handleSDKEvent:(map:Map<string, Object>) => void; } |
|---|---|
| 返回 | 无 |
| 示例 | let args: Map<string, Object> = new Map(); args.set(UULoginParamsKey.UU LOGIN NEW PASSWORD,newPwd); _ _ _ //设置 SDP 通道状态监听 UUMos.resetPassword(args, { handleSDKEvent: (map: Map<string, Object>): void => { if (map) { //错误码 let resultCode = UUMosUtils.getMapNumber(UUCallbackKey.UU KEY KMOSCALLBACKERRORCODE, map, -1); _ _ //错误码对应信息描述 let message = UUMosUtils.getMapString(UUCallbackKey.UU KEY KMOSCALLBACKERROR, map, ""); _ _ //返回接收到状态码后的下一步执行动作,枚举型 let suggest = |

| 23 |  |
|---|---|

移动安全MBS SDK API 文档说明(鸿蒙)

|  | UUMosUtils.getMapEnumSuggest(UUCallbackKey.UU KEY KMOSCALLBACKSUGGEST, _ _ map,UUCallbackSuggest.UU CALLBACK SUGGEST FINISH); _ _ _ if (suggest == UUCallbackSuggest.UU CALLBACK SUGGEST TIP) { _ _ _ //提示错误信息 message promptAction.showToast({ message: "密码重置失败:" + message + ":" + resultCode,duration: 2000}) } else if (suggest == UUCallbackSuggest.UU CALLBACK SUGGEST FINISH) { _ _ _ //密码重置成功,重新登录 promptAction.showToast({message: "密码重置成功",duration: 2000}) router.back() }}}}); |
|---|---|

## 1.3高级配置

## 1.3.1异常状态监听

| 类名 | UUMos |
|---|---|
| 方法 | setListener(callBack: IUUSDKCallback): number |
| 描述 | 【必选接口】,异步接口 设置 SDK 状态监听,监听 APP 使用过程中网络通道、设备、用户登录状态,当通道 被服务器踢出,设备被禁用或删除,用户被禁用或删除等会回调具体错误,并指示 下一步执行动作 |
| 参数 | callBack: IUUSDKCallback 接口类 export interface IUUSDKCallback{ /** * 接口调用回调 * @param map 回传参数 * 接口传参键值对,{key=xxx,value=xxx} * key 定义: * key=”kMosCallbackCode” ,value:int 类型,接口调用响应码,0:成功:-1:失败,其他参考 |

| 24 |  |
|---|---|

移动安全MBS SDK API 文档说明(鸿蒙)

|  | 错误码定义 * key= ”kMosCallbackError ” ,value:String 类型,接口调用响应错误信息, * @return */ handleSDKEvent:(map:Map<string, Object>) => void; } |
|---|---|
| 返回 | number 类型 0:调用成功,-1:调用失败 |
| 示例 | UUMos.setListener({handleSDKEvent: (map: Map<string, Object>): void => { if (map != null) { //错误码 let resultCode = UUMosUtils.getMapNumber(UUCallbackKey.UU KEY KMOSCALLBACKERRORCODE, _ _ map, -1) ; //错误码对应信息描述 let message = UUMosUtils.getMapString (UUCallbackKey.UU KEY KMOSCALLBACKERROR, map, _ _ "") ; //返回接收到状态码后的下一步执行动作,枚举型 let suggest: UUCallbackSuggest = UUMosUtils.getMapEnumSuggest(UUCallbackKey.UU KEY KMOSCALLBACKSUGGEST, map, _ _ UUCallbackSuggest.UU CALLBACK SUGGEST FINISH) ; _ _ _ if (suggest == UUCallbackSuggest.UU CALLBACK SUGGEST TIP) { _ _ _ //提示错误信息 message promptAction.showToast({ message: message,duration: 2000}) } else if (suggest == UUCallbackSuggest.UU CALLBACK SUGGEST RELOGIN) { _ _ _ //需要退回到登录界面重新登录 } else if (suggest == UUCallbackSuggest.UU CALLBACK SUGGEST ERASE) { _ _ _ //设备擦除 } } } }); |

## 1.3.2检测SDP隧道状态

| 类名 | UUMos |
|---|---|
| 方法 | checkSdpStatus(objectMap: Map<string, Object>, callBack: IUUSDKCallback) |
| 描述 | 【非必选接口】,检测隧道状态 异步方 法 使用场景: 1 :集成应用切换至前台,有立即发送网络请求需求,之前可调用 checkSdpStatus 方法,success 回调中发送网络请求 |

| 25 |  |
|---|---|

移动安全MBS SDK API 文档说明(鸿蒙)

|  | 2:集成应用网络层拦截到业务请求失败后,可调用 checkSdpStatus 方法执行处理 如:手机熄屏切换为亮屏,应用切换至前台,SDP 隧道会进行隧道恢复,该过程 中若集成应用立即发送网络请求则可能触发业务请求失败 |
|---|---|
| 参数 | args:接口参数,按照接口协议添加需要的登录信息: 接 口传参键值对 ,{key=xxx,value=xxx} 使用枚举字符 串 ,详细定义查看 UUCommParamsKey 枚举类定义 callBack: IUUSDKCallback 接口类 export interface IUUSDKCallback{ /** * 接口调用回调 * @param map 回传参数 * 接口传参键值对,{key=xxx,value=xxx} * key 定义: * key=”kMosCallbackCode” ,value:int 类型,接口调用响应码,0:成功:-1:失败,其他参考 错误码定义 * key= ”kMosCallbackError ” ,value:String 类型,接口调用响应错误信息, * @return */ handleSDKEvent:(map:Map<string, Object>) => void; } |
| 返回 | 无 |
| 示例 | let hashMap: Map<string, Object> = new Map(); UUMos.checkSdpStatus(hashMap, { handleSDKEvent: (map: Map<string, Object>): void => { let resultCode = UUMosUtils.getMapNumber(UUCallbackKey.UU KEY KMOSCALLBACKERRORCODE, map, -1); _ _ let message = UUMosUtils.getMapString(UUCallbackKey.UU KEY KMOSCALLBACKERROR, map, ""); _ _ let suggest = UUMosUtils.getMapEnumSuggest(UUCallbackKey.UU KEY KMOSCALLBACKSUGGEST, map, _ _ UUCallbackSuggest.UU CALLBACK SUGGEST FINISH); _ _ _ if (suggest == UUCallbackSuggest.UU CALLBACK SUGGEST RELOGIN) { _ _ _ |

| 26 |  |
|---|---|

移动安全MBS SDK API 文档说明(鸿蒙)

|  | //跳转到登录界面 } else if (suggest == UUCallbackSuggest.UU CALLBACK SUGGEST TIP) { _ _ _ promptAction.showToast({ message: "通道状态," + message, duration: 2000 }) } if (resultCode == 0) { promptAction.showToast({ message: "通道已开启", duration: 2000 }) } }}); |
|---|---|

## 1.3.3开启水印

| 类名 | UUMos |
|---|---|
| 方法 | showWatermark(args: Map<string, Object>): number |
| 描述 | 【非必选接口】,同步接口,有沙箱能力场景调用 将 VsaWatermark.ets 放到工程的 pages 目录中 在 resources\base\profile\main pages.json 添加 page 的声明: _ { "src": [ "pages/Index", "pages/VsaWatermark" ] } 注意事项 1. 水印设置后不是立即生效,而是需要程序冷启动才能生效。 2. 调用水印接口设置更新水印后,当应用到后台,计时 30 秒后自动退出应用,无 需用户手动杀应用后台。再次启动后,新的水印生效。 3. 如果 24 小时内过于频繁更新水印,则第二条的自动退出机制会失效。建议 24 小 时内,变更水印内容的次数不超过 5 次。否则只能等待用户手动杀后台,或者系统 自动清理后台 |

| 27 |  |
|---|---|

移动安全MBS SDK API 文档说明(鸿蒙)

| 参数 | args:接口参数 如果需要自定义页面级水印样式需要传水印配置相关参数 接口传参键值对,{key=xxx,value=xxx},详细定义查看 UUWatermarkParamsKey 枚举类定义 text 水印内容, String 类型 |
|---|---|
| 返回 | Int 类型,0:成功; 其它:失败 |
| 示例 | 传递水印显示内容 let args: Map<string, Object> = new Map () ; args.set(UUWatermarkParamsKey.UU SANDBOX WATERMARK TEXT,"gyf") _ _ _ UUMos.showWatermark(args) |

## 1.3.4关闭水印

| 类名 | UUMos |
|---|---|
| 方法 | hideWatermark(args: Map<string, Object>): number |
| 描述 | 【非必选接口】,同步接口,有沙箱能力场景调用 关闭水印 |
| 参数 | 无 |
| 返回 | Int 类型,0:成功; 其它:失败 |
| 示例 | let args: Map<string, Object> = new Map () ; UUMos.hideWatermark(args) |

## 1.4工具方法

## 1.4.1导出日志

| 类名 | UUMos |
|---|---|
| 方法 | int exportLog(Map<String, Object> args, IUUSDKCallback callBack) |
| 描述 | 【非必选接口】,异步接口 导出日志方法,导出SDK 运行时日志 |

| 参数 | args:接口参数,按照接口协议添加需要的登出信息: 接口传参键值对,{key=xxx,value=xxx}UUCallbackKey callBack: IUUSDKCallback 接口类 public interface IUUSDKCallback { /** * 接口调用回调 * @param map 回传参数 * 接口传参键值对,{key=xxx,value=xxx}使用枚举字符串,详细定义查看 UUCallbackKey 枚举类定义 * * @return */ void handleSDKEvent(Map<String, Object> map); } |
|---|---|

| 29 |  |
|---|---|

移动安全MBS SDK API 文档说明(鸿蒙)

| 返回 | 无 |
|---|---|
| 示例 | //日志导出 UUMos.exportLog(null, new IUUSDKCallback() { @Override public void handleSDKEvent(Map<String, Object> map) { //导出日志路径 String logPath = UUMosUtils.getMapString(UU KEY MBS LOGPATH.stringValue(),map,"");} _ _ _ }); |

## 1.4.2获取SDK 版本

| 类名 | UUMos |
|---|---|
| 方法 | getSdkVersion():string |
| 描述 | 【非必选接口】,同步接 口 获取 SDK 版本信息 |
| 参数 | 无 |
| 返回 | 返回SDK 主版本及各模块版本,可用于快速确定当前应用集成的SDK 版本及模块功 能 返回 Json 字符串 version: 主版本,沙箱版本,SDP 版本 |
| 示例 | //获取SDK 版本信息 Let sdkVersion:string = UUMos.getSdkVersion() ; |

# 2

# 常见数据结构

描述SDK中集成方法可能涉及到的关键类和枚举型常量说明

接口回调参数枚举UUInitParamsKey说明

| 枚举值 |  | 描述 |  |  |
|---|---|---|---|---|
| UU INIT MBS URL _ _ _ |  | MOS 服务器地址 |  |  |
|  | 30 |  |  |  |

移动安全MBS SDK API 文档说明(鸿蒙)

| UU INIT MBS ORGCODE _ _ _ | MOS 服务器租户信息 |  |
|---|---|---|
| UU INIT MBS USAGELOG _ _ _ | 是否开启应用使用日志上报 |  |
| UU INIT MBS TIMEOUT _ _ _ | 超时时间 |  |
| UU INIT MBS SECRETKEY _ _ _ | 应用密钥认证 secretkey |  |
| UU INIT MBS APPKEY _ _ _ | 应用密钥认证 appKey |  |
| UU INIT MBS SECUREHTTPENABLE _ _ _ | 请求体双向加密开关 |  |
| UU INIT SDP PORT _ _ _ | SDP 服务器端口 |  |
| UU INIT SDP HOST _ _ _ | 安全网关服务器地址 |  |
| UU INIT MBS LANGUAGE _ _ _ | 语言设置,0-简体中文 1-英文 2-繁体中文 |  |
| UU INIT SDP MTU _ _ _ | mtu 设置特殊机型需要配置,正 常情况不需要关注 |  |
| UU INIT SDP APPID _ _ _ | SDP 应用标识,SDP 应用级互踢 场景使用,Android/ IOS/鸿蒙保 持一致,例如: com.zzy.sdp.appclient |  |

登录接口请求参数枚举UULoginParamsKey说明

| 枚举值 | 描述 |
|---|---|
| UU LOGIN LOGINNAME _ _ | 登录用户名 |
| UU LOGIN PASSWORD _ _ | 登录密码 |
| UU LOGIN DEVICEID _ _ | 设备唯一标识 |
| UU LOGIN LOGINMODE _ _ | sdk 模式 |
| UU LOGIN LOGINTYPE _ _ | 登录类型 |
| UU LOGIN PHONE NUMBER _ _ _ | 登录手机号码 |
| UU LOGIN COUNTRY CODE _ _ _ | 登录国家电话代码 |
| UU LOGIN IDENTIFY CODE _ _ _ | 短信验证码 |
| UU LOGIN NEW PASSWORD _ _ _ | 新密码,修改密码接口使用 |

接口回调参数枚举UUCallbackKey说明

| 枚举值 | 描述 |
|---|---|

| 31 |  |
|---|---|

移动安全MBS SDK API 文档说明(鸿蒙)

| UU KEY KMOSCALLBACKERRORCODE _ _ | 状态码 |  |
|---|---|---|
| UU KEY KMOSCALLBACKERROR _ _ | 状态码对应描述 |  |
| UU KEY KMOSCALLBACKSUGGEST _ _ | 下一步执行动作 |  |
| UU KEY KMOSSMSCOUNTDOWN _ _ | 短信发送倒计时 |  |
| UU KEY KMOSSECONDARYAUTHTYPE _ _ | 返回接二次认证类型 |  |
| UU KEY MOS RSP TOKEN _ _ _ _ | MOS 响应 token |  |
| UU KEY MOS RSP PHONENUMBER _ _ _ _ | 手机号 |  |
| UU KEY MOS RSP USERID _ _ _ _ | 用户 ID |  |
| UU KEY MOS RSP USERNAME _ _ _ _ | 用户名 |  |
| UU KEY MBS LOGPATH _ _ _ | 日志导出路径 |  |
| UU KEY SDP TCPCONNECTED _ _ _ | TCP 连接状态 |  |
| UU KEY SDP TICKET _ _ _ | sdp 响应 ticket |  |
| UU KEY MOS EXTENDPARAM _ _ _ | 响应扩展字段 |  |
| UU KEY MOS PWDLEVEL _ _ _ | 重置密码密码复杂度 |  |
| UU KEY MOS AUTH RSP CONFIG PRO _ _ _ _ _ _ | 追加/风险认证集合, 如果配置 多种方式,二次认证需要从集 合中选择采用哪种方式认证, sdp2.0 场景使用 |  |

短信验证码参数枚举UUSmsCodeParamsKey说明

| 枚举值 | 描述 |
|---|---|
| UU COMM PHONE NUMBER _ _ _ | 手机号码 |
| UU COMM COUNTRY CODE _ _ _ | 国家电话代码 |

下一步执行动作参数枚举UUCallbackSuggest说明

| 枚举值 | 描述 |
|---|---|
| UU CALLBACK SUGGEST FINISH _ _ _ | 流程已完成 |
| UU CALLBACK SUGGEST RELOGIN _ _ _ | 返回登录页面,执行重新登录 |
| UU CALLBACK SUGGEST ERASE _ _ _ | 执行设备擦除并关闭应用 |
| UU CALLBACK SUGGEST PROGRESS _ _ _ | 执行二次认证 |

| 32 |  |
|---|---|

移动安全MBS SDK API 文档说明(鸿蒙)

| UU CALLBACK SUGGEST TIP _ _ _ | 弹出错误提示 |  |
|---|---|---|
| UU CALLBACK SUGGEST RETRY _ _ _ | 重试 |  |
| UU CALLBACK SUGGEST SAFECONTROL _ _ _ | 安全控制, 比如首次登录强制 修改密码场景 |  |

二次认证参数枚举UUSecondaryAuthType说明

| 枚举值 | 描述 |
|---|---|
| AUTH TYPE SECOND SMS _ _ _ | 短信认证 |
| AUTH TYPE SECOND CUSTOM _ _ _ | 第三方认证 |
| AUTH TYPE SECOND CUSTOM PRO _ _ _ _ | 二次认证,包括风险认证和二 次追加,sdp2.0 场景使用 |

鉴权类型参数枚举UUAuthType说明

| 枚举值 | 描述 |
|---|---|
| AUTH TYPE PASSWORD _ _ | 账号密码认证 |
| AUTH TYPE TOKEN _ _ | 第三方令牌认证 |
| AUTH TYPE SMS _ _ | 短信验证码认证 |
| AUTH TYPE APPKEY _ _ | 应用密钥认证 |
| AUTH TYPE OTP _ _ | OTP 令牌,sdp2.0 场景使用 |

Sdk模式枚举UUSDKMode说明

| 枚举值 | 描述 |
|---|---|
| UU MODE SDP SANDBOX _ _ _ | 启用 MOS 和 SDP |
| UU MODE SDP _ _ | 仅启动 sdp |
| UU MODE SANDBOX _ _ | 仅启动 mos |

Sdk 接口调用类型参数枚举UUCommParamsKey说明

| 枚举值 | 描述 |
|---|---|
| UU COMM MOS DEBUG _ _ _ | 调试模式,是否是 Debug 模式, boolean 类型,如果是 Debug 模 式,会打印调试日志 |
| UU COMM SDP CHECKTIMEOUT _ _ _ | 检测资源超时时间 ,int 类型, 单位秒 |

| 33 |  |
|---|---|

移动安全MBS SDK API 文档说明(鸿蒙)

| UU COMM SDP CHECK TARGETHOST _ _ _ _ | 检测资源的 host,String 类型 |  |
|---|---|---|
| UU COMM SDP CHECK TARGETPORT _ _ _ _ | 检测资源的 port,int 类型 |  |
| UU COMM SDP STATE _ _ _ | sdp 状态,int 类型,0:通道已经 关闭 1:通道已开启 |  |
| UU COMM MOS BYPASS _ _ _ | bypass 模式,int 类型,1:不启用, 2 :启动,默认:1 |  |
| UU COMM MOS INITWORKSPACE DELAY _ _ _ _ | boolean 类型,SDK 目录初始化 延时,true:延时,false:不延时, 默认 false(用户隐私合规相关) |  |
| UU COMM MOS SMSCODE _ _ _ | 短信验证码,重置密码时使用 |  |
| UU COMM MOS SANDBOXENCRYPTPATHLIST _ _ _ | 黑白名单路径列表 |  |
| UU COMM MOS SANDBOXENCRYPTTYPE _ _ _ | 指定路径名单类 型 1 : 白名 单:2:黑名单 |  |
| UU COMM SDP CLOSE TUNNEL _ _ _ _ | 断开sdp 通道,1:断开SDP 连接, 0 :退出登录,默认:0 |  |

Sdk安全控制枚举UUSafeControlType说明

| 枚举值 | 描述 |
|---|---|
| SAFE CONTROL MODIFY PASSWORD _ _ _ | 首次登录强制修改密码 |

页面级水印配置枚举UUWatermarkParamsKey说明

| 枚举值 | 描述 |
|---|---|
| UU SANDBOX WATERMARK TEXT _ _ _ | 水印内容 |
| UU SANDBOX WATERMARK TEXTCOLOR _ _ _ | 水印字体颜色 |
| UU SANDBOX WATERMARK TEXTSIZE _ _ _ | 水印文字大小 |
| UU SANDBOX WATERMARK TEXTROTATION _ _ _ | 水印文字旋转角度 |
| UU SANDBOX WATERMARK TEXTSTAMP _ _ _ | 水印时间戳 |

| 34 |  |
|---|---|

移动安全MBS SDK API 文档说明(鸿蒙)

# 3

# 错误码说明

## 3.1SDP+MOS

| 错误码 | 错误信息 | 错误场景 |
|---|---|---|
| code=2000101 | 登录参数异常 | 申请 VPN 权限时,被用户拒绝 |
| code=2000102 | 服务器安全策略不满足 |  |
| code=2000103 | 登录请求超 时 | 1.网络问题; 2.服务端不通 |
| code=2000104 | 强制修改密码 |  |
| code=2000110 | 其他错误 | vpn 启动过程异常 , 需查看异常日志排查 |
| code=2000201 | GoBackend 流 程 异 常 | 账号登录成功, VPN 启动过程异常,需 配合异常日志排查原因 |
| code=2000202 | 构建登录响应数据异常 | 账号登录成功, VPN 启动过程异常,需 配合异常日志排查原因 |
| code=2000203 | 配置文件丢失 |  |
| code=2000204 | vpn 权 限未 申请 | 应用VPN 权限未申请或被关闭 |
| code=2000205 | vpnservice 启 动 异 常 |  |
| code=2000206 | vpnservice 通 道 建 立 异 常 |  |
| code=2000207 | wg 启 动返回值异常 |  |
| code=2000208 | 内网检测不可达 | 内网检测不可达 |
| code=2001001 | 客 户端存在 安全 问 题,禁 止登录 |  |
| code=2001002 | 需要追加短信登录 |  |
| code=20001003 | 您 的帐户未绑定手 机号 码,请联系管 理员 |  |
| code=2001004 | 没有可访问的资源 |  |
| code=2001005 | 短信限流 |  |

| 35 |  |
|---|---|

移动安全MBS SDK API 文档说明(鸿蒙)

| code=2001006 | 验证码错误 |  |
|---|---|---|
| code=2001007 | 客户端版本号不合法 |  |
| code=2001008 | license 受 限,禁止登录 |  |
| code=2001009 | 不支持的客户端版本 |  |
| code=2001010 | 用户名或密码错误 | 账号密码错误,请重新输入 |
| code=2001011 | 无效的用户 | 账号密码错误,请重新输入 |
| code=2001012 | 用户未激活 | 账号密码错误,请重新输入 |
| code=2001013 | 账号已禁用 | 联系管理员处理账号 |
| code=2001014 | 账号已锁定 | 联系管理员处理账号 |
| code=2001016 | 无效的手机号码 | 联系管理员处理账号 |
| code=2002002 | 访问地限制,禁止登录 | 当前设备环境不符合监测需求 , 限制 登 录 |
| code=2002003 | 设 备已 root/越狱 , 禁止登 录 | 当前设备环境不符合监测需求 , 限制 登 录 |
| code=2002004 | 设备未开启全盘加密,禁 止登录 | 当前设备环境不符合监测需求, 限制登录 |
| code=2002005 | 低于操作版本限制要 求, 禁止登录 | 当前设备环境不符合监测需求 , 限制 登 录 |
| code=2002006 | 非允许访问的网络类 型, 禁止登录 | 当前设备环境不符合监测需求 , 限制 登 录 |
| code=2002007 | 设备绑定限制,禁止登录 | 当前设备环境不符合监测需求 , 限制 登 录 |
| code=2002008 | 违法防火墙限制 | 当前设备环境不符合监测需求 , 限制 登 录 |
| code=2002009 | 违法安全软件限制 | 当前设备环境不符合监测需求 , 限制 登 录 |
| code=2002010 | 未设置密码 | 当前设备环境不符合监测需求 , 限制 登 录 |
| code=2002011 | 未设置生物密码 | 当前设备环境不符合监测需求 , 限制 登 录 |

| 36 |  |
|---|---|

移动安全MBS SDK API 文档说明(鸿蒙)

| code=2002012 | 模拟器设备 | 当前设备环境不符合监测需求 , 限制 登 录 |
|---|---|---|
| code=2002013 | DEBUG 设备 | 当前设备环境不符合监测需求 , 限制 登 录 |
| code=2002014 | 非连续性登录风险告警 |  |
| code=2002015 | 新设备登录风险告警 |  |
| code=2002016 | 非常用地登录风险告警 |  |
| code=2002017 | 非指定时间登录风险告 警 |  |
| code=2002018 | 非指定 IP 登录风险告警 |  |
| code=3000002 | 会话失效 | 登录会话失效需要重新登录 |
| code=3000003 | 服务器 license 过期等情 况 | 管理员在 MOS 服务端重新导入 license |
| code=3000005 | 检测到该服务器下配置的 标 识码不存在 | 接口传递/容器化配置的标识码错误, 检查 后再试 |
| code=3000100 | 用户不存在,账号或密码错 误 | 客户端输入正确的用户名 |
| code=3000103 | 用户被禁用 | 管理员解锁用户 |
| code=3000107 | 用户未激活 | 管理员手动激活用户 |
| code=3000108 | 用户 license 超限 | 管理员重新导入合规 license |
| code=3000116 | 不允许 admin 或 sysadmin 登 录客户端 | 不允许 admin 或 sysadmin 登录客户 端; 客户端输入非管理员之外的用户 名 |
| code=3000118 | 应用接入时,登录的用户名 和约定的用户名不一致 | 应用接入时输入/配置约定的 appkey |
| code=3000119 | 应用接入时,根据登录的 appkey 找对应的 secrekey, 跟传入的 secrekey 不一致 | 应用接入时输入/配置约定的 secrekey |
| code=3001001 | 管理员后台擦除设备 | 客户端等待设备完成擦除指令 |
| code=3001002 | 管理员后台禁用设备 | 管理员手动启用设备 |

| 37 |  |
|---|---|

移动安全MBS SDK API 文档说明(鸿蒙)

| code=3001003 | 用户绑定设备数已满 | 方案一 :管理端在后台调整用户绑定 设备 数 方案二:用户自行退出应用 解 绑设备, 减少绑定设备 |  |
|---|---|---|---|
| code=3001004 | 当前设备已被其他人绑定, 以前登录后未登出,导致未 解除绑定关系 | 方案一:管理员手动删除被绑定的设 备 方 案二:使用指定用户名(绑定 用 户) 登录 设备后再退出登录 |  |
| code=3001005 | 账号或密码错误 | 提示错误信息,检查账号重试 |  |
| code=3001001 | 设备待擦除 | SDK 内部做擦除应用数据处理, 包括内部数据和 sd 卡上的数据, 擦除完成后退出应用,集成方不需要处理 |  |
| code=3001002 | 设备已禁用 |  |  |
| code=3001008 | 租户不存在 |  |  |
| code=3001009 | 用户名不存在 |  |  |
| code=3001011 | 尝试登陆超过 5 次,您的帐 号被锁定,请 10 分钟后再 试 |  |  |
| code=3001012 | 用户被禁用 |  |  |
| code=3001017 | 免密认证操作失败 |  |  |
| code=3001019 | 手机号未注册 |  |  |
| code=3001018 | 手机号不能为空 |  |  |
| code=3001014 | 验证码多次输入错误,请重 新获取验证码 |  |  |
| code=3001020 | 用户停用禁止发短信 |  |  |
| code=3001021 | 用户被锁定禁止发送短信 |  |  |
| code=3001022 | 设备禁用禁止发短信 |  |  |
| code=3001023 | 验证码获取次数超限,请稍 后重试 |  |  |
| code=3001024 | 短信申请失败 | 提示错误信息,联系管理员处理, 再重新登录 |  |
| code=3001026 | 用户被锁定不能进行短信 验证 |  |  |
| code=3001025 | 用户停用不能进行短信验 证 |  |  |
| 38 |  |  |  |

移动安全MBS SDK API 文档说明(鸿蒙)

| code=3001029 | 验证码验证多次失败,请重 新获取验证码 |  |
|---|---|---|
| code=3001050 | 系统授权设备总数已满,无 法绑定 | 管理员重新导入合规 license |
| code=3001040 | 登出失败 |  |
| code=3001041 | 手机号码已被绑定 |  |
| code=3001042 | 手机号码绑定失败 |  |
| code=3001055 | 手机号码未绑定,请先使用 帐号密码登录 |  |
| code=3001056 | 手机号被多个用户绑定,请 使用其他方式登录或联系 管理员 |  |
| code=3001057 | 当前手机号码跟用户绑定 的号码不一致 |  |
| code=3001065 | 服务器异常 |  |
| code=3001068 | 手机号下绑定的多个用户, 状态均异常,不能进行短信 验证 |  |
| code=3010005 | 网络请求异常,请检查后重 试 | 本地网络问题 |
| code=3010001 | 服务端响应异常 | 联系管理员处理问题 |
| code=3010003 | 登录超时 | 服务不通,联系管理员处理网络问题 |
| code=-1000001 | 未知错误 | 未知错误 |

| 39 |  |
|---|---|
