**TrustAccess SDK v1.0.4 使用说明** 

TrustAccess SDK v1.0.4 使用说明 1、修改历史 2、接入说明 2.1、SDK开发包组成 2.2、SDK接入 2.3、依赖的权限配置 2.4、混淆相关 2.5、支持的鸿蒙系统版本 3、调用指南 3.1、接口调用指南 3.2、用户会话处理 4、初始化SDK接口 5、网关相关接口 5.1、设置网关信息 5.2、设置网关信息回调 6、认证相关接口 6.1、口令认证相关 6.1.1、口令认证 6.1.2、修改口令密码 6.2、短信认证相关 6.2.1、发送短信认证码 6.2.2、短信认证 6.3、证书认证相关 6.3.1、本地p12证书认证 6.3.2、本地国密双证书认证 7、用户认证回调接口 7.1、注册、注销认证回调 

7.2、AuthSuccessListener解析 7.4、AuthFailedListener解析 8、系统级别安全网关代理接口 8.1、系统级别安全网关代理配置 8.2、启动系统级别安全网关代理 8.3、注册、注销隧道协商状态回调 8.3、TunnelConnectSuccessStateListener解析 8.4、TunnelConnectFailedStateListener解析 8.5、TunnelConnectFinishListener解析 9、资源相关接口 9.1、是否有nc资源 10、用户相关接口 10.1、获取用户状态接口 10.2、用户状态回调 10.3、主动获取用户的实时在线状态 11、日志相关接口 11.1、调用日志打印和存储 11.2、分享日志 12、其他接口 12.1、获取SDK版本 

# **1、修改历史** 

|**版本号**|**日期**|**说明**|
|---|---|---|
|1.0.0|2025\04\08|鸿蒙基础版本,支持NC资源访问|
|1.0.1|2025\09\12|1、支持证书认证 2、支持短信认证 3、支持修改口令密码|
|1.0.4|2026\07\03|1、支持国密认证 2、支持本地国密双证书认证|

# **2、接入说明** 

## **2.1、SDK开发包组成** 

HarmonyOS TrustAccess SDK v1.0.4使用说明.pdf 

SDK的使用文档,详细说明了SDK的接入方式和SDK提供的接口。 

- VpnDemo.zip 

SDK接入的示例代码,可以参照此示例代码迅速获得安全网关代理能力。 

- trust_sdk_v1.0.4.har 

SDK包 

- DevEcoStudio无法使用vpn type处理.pdf 

如果DevEcoStudio无法使用Vpn字段,可以参照这个文档设置。 

## **2.2、SDK接入** 

在项目的entry下新建一个libs文件夹 

将trust_sdk.har复制到libs文件夹中 

- 使用DevEcoStudio自带的命令行安装 

```
# 先cd到entry文件夹下
 D:\VpnCode\harmony\VpnDemo> cd entry
 D:\VpnCode\harmony\VpnDemo\entry>
# 使用ohpm install 命令安装
PS D:\VpnCode\harmony\VpnDemo\entry> ohpm install libs/trust_sdk.har
ohpm INFO: remove useless folder succeed:
"D:\VpnCode\harmony\VpnDemo\oh_modules\.tmp"
install completed in 0s 132ms
```

**注意:** 本SDK为静态共享包,以上只是推荐的一种安装方式,如果项目中已经有其他的SDK存放路径或 者其他的安装方式也可以。 

## **2.3、依赖的权限配置** 

```
"requestPermissions": [
      {
"name": "ohos.permission.INTERNET",
      },
      {
"name": "ohos.permission.STORE_PERSISTENT_DATA"
      },
      {
"name": "ohos.permission.GET_NETWORK_INFO"
      }
    ]
```

### **2.4、混淆相关** 

无 

### **2.5、支持的鸿蒙系统版本** 

鸿蒙5.0~最新 

# **3、调用指南** 

## **3.1、接口调用指南** 

本文档接口众多,可以参照以下的方式迅速获得安全网关代理能力。 

- 1、调用接口 **4、初始化SDK接口** 

- 2、调用接口 **5.1、设置网关信息** 并从接口 **5.2、设置网关信息回调** 获取到链接网关成功的回调。 

- 3、调用接口 **6.1、口令认证** 并从接口 **7、用户认证回调接口** 获取到认证成功的回调 

- 4、调用接口 **8、系统级别安全网关代理接口** 开启安全网关的能力。并从接口 **8.3、注册、注销隧道 协商状态回调** 获取到隧道协商状态。获取到 tunnelConnectFinish回调之后代表隧道连接完毕,可 以访问具体业务。 

## **3.2、用户会话处理** 

- 当用户上线或者下线时,接口: **10.2、用户状态回调** 此接口会回调用户状态。此时可以根据业务情 况对用户状态进行处理。 

# **4、初始化SDK接口** 

### **接口说明:** 

`VSGService` 是 VPN SDK 的核心服务类,采用单例模式管理 VPN 相关功能模块,提供初始化、网关配 置、用户认证、退出登录等核心能力。 

### **接口定义:** 

```
/**
   * 初始化SDK
   *
   * @param context UIAbilityContext
   * @param sdkFeature SDK的配置
   */
initSDK(context: common.UIAbilityContext, sdkFeature:SDKFeature)
```

### **参数解析:** 

|**参数**|**类型**||**必填**|**说明**|
|---|---|---|---|---|
|context|common.UIA|bilityContext|是|UIAbilityContext|
|sdkFeature **SDKFeature解析**|SDKFeature **:**||是|SDK初始化的参数,可以设置语言、自动启 动VPN等,具体看SDKFeature解析|
|**参数**||**类型**|**说明**||
|languageType||number|语言类型 中文 SDKFeat|SDKFeature.LANGUAGE_TYPE_CHINESE: ure.LANGUAGE_TYPE_ENGLISH:英语|
|useNC||boolean|是否使用 代理;fa|系统安全网关代理。true使用系统安全网关 lse不使用系统安全网关代理|
|autoStartVpnAb|ilityName|string|自动启动 自动启动 **统级别安** 可以根据|VPN的Ability名称。如果传入,认证成功就 VPN,如果未传入需要调用**接口8.2、启动系全网关代理**自行启动VPN。 场景自行选择。|

### **返回值解析:** 

无 

### **调用示例:** 

```
letsdkFeature=newSDKFeature()
VSGService.getInstance().initSDK(this.context,sdkFeature)
```

### **注意:** 

建议在UIAbility的onCreate方法中调用。 

# **5、网关相关接口** 

## **5.1、设置网关信息** 

### **接口说明:** 

通过此接口可以设置网关信息并连接网关。连接网关的结果在 **接口5.2、设置网关信息回调** 中返回。 

### **接口定义:** 

```
/**
   * 设置网关信息
   * @param gateWay 网关地址
   * @param port 网关ip
   */
setGatewayInfo(gateWay:string, port:number, algo:number=0)
```

### **参数解析:** 

|**参数**|**类型**|**必填**|**说明**|
|---|---|---|---|
|gateWay|string|是|网关服务器地址|
|port|number|是|网关服务器端口号|
|algo|number|否|加密算法。 `0` 国际; `1` 国密|

### **返回值解析:** 

无,连接网关的结果在 **接口5.2、设置网关信息回调** 中返回。 

### **调用示例:** 

```
VSGService.getInstance().setGatewayInfo(this.gateway, this.port, 0)
```

### **补充说明:** 

当后续要执行国密认证时,需要在这里传入 `algo = 1` ,例如: 

```
VSGService.getInstance().setGatewayInfo(this.gateway, this.port, 1)
```

## **5.2、设置网关信息回调** 

### **接口说明:** 

接口 **5.1、设置网关信息** 调用之后,连接网关的结果在这个接口中返回。这部分分为两个接口, registerSetGatewayInfoListener注册设置网关信息回调;unRegisterSetGateWayInfoListener注销设 置网关信息回调 

### **接口定义:** 

```
/**
     * 注册设置网关回调
     * @param listener
     */
registerSetGatewayInfoListener(listener: SetGatewayInfoListener)
/**
     * 注销设置网关回调
     * @param listener
     */
unRegisterSetGateWayInfoListener(listener: SetGatewayInfoListener)
```

### **参数解析:** 

|**参数**|**类型**|**必填**|**说明**|
|---|---|---|---|
|listener|SetGatewayInfoListener|是|网关配置变更回调接口实例|

### **SetGatewayInfoListener定义:** 

```
export typeSetGatewayInfoListener= (retCode: SetGatewayInfoRetCode) =>void;
```

### **SetGatewayInfoRetCode参数解析:** 

### SetGatewayInfoRetCode枚举提供多个参数用于标注连接控制器的状态: 

|**参数**|**说明**|**解决方案**|
|---|---|---|
|SETGATEWAYINFO_SUCCESS|连接网关成功||
|SETGATEWAYINFO_RESOLE_FAILED|域名解析失败|检查域名、ip是否正确。|
|SETGATEWAYINFO_UNREACHABLE|网关不可达|网关不可达。 1、可以使用手机浏览器访问网关测 试是否能访问。 2、通过ping工具ping网关测试是否 能正常接收包。|
|其他状态|网关可能存在 其他状态|将日志提交技术支持分析|

### **返回值解析:** 

无 

### **调用示例:** 

```
letlistener= (retCode:SetGatewayInfoRetCode)=>{
if (retCode==SetGatewayInfoRetCode.SETGATEWAYINFO_SUCCESS) {
"
ToastUtil.showToast(连接控制台成功! ")
      }
    }
// 注册连接控制器回调
GateWayManager.getInstance().registerSetGatewayInfoListener(listener)
// 注销连接控制器的回调
GateWayManager.getInstance().unRegisterSetGatewayInfoListener(listener)
```

# **6、认证相关接口** 

此模块详细介绍了网关的用户认证,用户认证是应用获取vpn能力的核心校验。通过用户认证,应用可 以获取到资源并且开启NC隧道。用户认证的结果在 **接口7、用户认证回调** 中返回。 

## **6.1、口令认证相关** 

**6.1.1、口令认证** 

### **接口说明:** 

通过此接口可以使用用户名密码进行认证。 

### **接口定义:** 

```
/**
   * 用户口令认证
   * @param userName 用户名
   * @param password 密码
   * @param isBaseAuth 是否为主认证
   */
userPasswordAuth(userName:string, password:string, isBaseAuth:number)
```

### **参数解析:** 

|**参数**|**类型**|**必填**|**说明**|
|---|---|---|---|
|userName|string|是|用户账号|
|password|string|是|用户密码|
|isBaseAuth|number|是|是否为主认证。1主认证;0非主认证 ; 当存在二次认证的 时候需要传0|

### **返回值解析:** 

无 

### **调用示例:** 

```
VSGService.getInstance().userPasswordAuth(this.userName, this.userPwd, 1)
```

### **6.1.2、修改口令密码** 

### **接口说明:** 

### 调用此接口可以修改口令密码 

### **接口定义:** 

```
/**
   * 修改密码
   * @param oldPwd 旧密码
   * @param newPwd 新密码
   * @param isFirstLogin 是否为第一次认证
   */
updatePassword(oldPwd:string, newPwd:string, isFirstLogin:boolean)
```

### **参数解析:** 

|**参数**|**类型**|**说明**|
|---|---|---|
|oldPwd|string|旧密码|
|newPwd|string|新密码|
|isFirstLogin|number|是否为主认证1主认证2辅助认证|

### **调用示例:** 

```
VSGService.getInstance().updatePassword(this.oldPwd, this.newPwd,
this.isFirstLogin)
```

注意。当 **接口7、用户认证回调接口** 中的registerUserAuthStateListener回调 AuthState.MODIFY_PASSWD_SUCCESS状态时,代表修改口令成功。 

## **6.2、短信认证相关** 

**6.2.1、发送短信认证码** 

### **接口说明:** 

发送短信认证码。 

### **接口定义:** 

```
/**
   * 发送短信认证码
   * @param isBaseAuth 是否为主认证
   */
sendSMSAuthCode(isBaseAuth: number)
```

### **参数解析:** 

**参数 类型 说明** isBaseAuth number 是否为主认证 1主认证 2 辅助认证 

### **调用示例:** 

```
VSGService.getInstance().sendSMSAuthCode(0)
```

**注意: 接口7、用户认证回调接口** 中的registerUserAuthStateListener回调 AuthState.BEGIN_TO_SMS_COUNT_DOWN状态时,代表发送短信成功。 

### **6.2.2、短信认证** 

### **接口说明:** 

短信验证码认证。 

### **接口定义:** 

```
/**
   * 开始短信验证码登录
   * @param smsCode 短信验证码
   */
startSMSCodeAuth(smsCode: string)
```

### **参数解析:** 

|**参数**|**类型**|**说明**|
|---|---|---|
|smsCode|string|短信认证码|

### **调用示例:** 

```
VSGService.getInstance().startSMSCodeAuth(this.verificationCode)
```

## **6.3、证书认证相关** 

**6.3.1、本地p12证书认证** 

### **接口说明:** 

调用此接口可以使用本地P12证书认证 

### **接口定义:** 

```
/**
   * 使用本地p12证书认证
   * @param p12CertPath 证书地址
   * @param p12CertPwd 证书密码
   */
startCertificateAuth(p12CertPath: string, p12CertPwd: string, isBaseAuth:
number)
```

### **参数解析:** 

|**参数**|**类型**|**说明**|
|---|---|---|
|p12CertPath|string|P12证书路径|
|p12CertPwd|string|P12证书地址|
|isBaseAuth|number|是否为主认证|

### **调用示例:** 

```
SDPService.getInstance().startCertificateAuth(certPath,this.selectCertUser.pass
word, 1)
```

### **6.3.2、本地国密双证书认证** 

### **接口说明:** 

调用此接口可以使用本地国密双 `p12` 证书进行认证。业务侧需要同时传入签名证书和加密证书的 **完整文 件路径** 及对应密码。 

调用前需满足以下前置条件: 

- 已完成 **接口4、初始化SDK接口** 

- 已调用 **接口5.1、设置网关信息** ,并传入 `algo = 1` 

- 已准备好本地签名 `p12` 和加密 `p12` 

### **接口定义:** 

```
/**
```

- `使用本地国密双证书认证` 

- `@param signCertPath 签名证书路径` 

- `@param signCertPwd 签名证书密码` 

```
   * @param encCertPath 加密证书路径
   * @param encCertPwd 加密证书密码
   * @param isBaseAuth 是否为主认证
   */
startSM2CertificateAuth(
signCertPath: string,
signCertPwd: string,
encCertPath: string,
encCertPwd: string,
isBaseAuth: number
  )
```

### **参数解析:** 

|**参数**|**类型**|**说明**|
|---|---|---|
|signCertPath|string|签名 `p12` 证书完整路径|
|signCertPwd|string|签名 `p12` 证书密码|
|encCertPath|string|加密 `p12` 证书完整路径|
|encCertPwd|string|加密 `p12` 证书密码|
|isBaseAuth|number|是否为主认证。 `1` 主认证; `0` 非主认证|

### **调用示例:** 

```
VSGService.getInstance().setGatewayInfo(this.gateway, this.port, 1)
VSGService.getInstance().startSM2CertificateAuth(
this.signP12Path,
this.signP12Password,
this.encP12Path,
this.encP12Password,
1
)
```

### **注意:** 

1、 `signCertPath` 和 `encCertPath` 需要传入完整路径,不能只传文件名 

- 2、接口当前对应的是本地双证书认证链路,不是外部证书认证链路 

# **7、用户认证回调接口** 

## **7.1、注册、注销认证回调** 

### **接口说明:** 

调用 **接口6、认证相关** 的认证接口,认证结果会在此接口返回。 

### **接口定义:** 

```
/**
     * 注册用户认证状态回调
     * @param authSuccessListener 认证成功状态回调
     * @param authFailedListener 认证失败状态回调
     */
registerUserAuthStateListener(authSuccessListener: AuthSuccessListener,
authFailedListener: AuthFailedListener)
/**
      * 注销用户认证状态回调
      * @param authSuccessListener
      * @param authFailedListener
      */
unRegisterUserAuthStateListener(authSuccessListener:AuthSuccessListener,
authFailedListener:AuthFailedListener)
```

**参数解析:** 

|**参数**|**说明**||
|---|---|---|
|AuthSuccessListener|认证成功状态回调,|详情请看AuthSuccessListener解析|
|AuthFailedListener|认证失败状态回调,|详情请看AuthFailedListener解析|

### **返回值解析:** 

无 

### **调用示例:** 

```
UserAuthManager.getInstance().registerAuthStateListener((authState:
AuthState, msg: string)=>{
if (authState==AuthState.GET_INTERGRATION_XML_SUCCESS) {
// 认证成功
      }
    },(errorCode: number, msg: string)=>{
// 认证失败
    })
```

## **7.2、AuthSuccessListener解析** 

此接口为认证成功状态回调。 

### **注意:** 这个接口会返回很多的正常的流程状态,一般来说只需要关注 

**GET_INTERGRATION_XML_SUCCESS** 这个参数即可,这个参数是已经成功获取到所有的参数,代表认 证流程已经全部结束。 

### **AuthSuccessListener定义:** 

```
/**
     * 认证正常流程回调
     */
export typeAuthSuccessListener= (authState: AuthState, msg: string) =>
void
```

### **AuthState参数解析:** 

AuthState是一个枚举,代表当前认证成功的状态。 

|**参数**|**说明**|
|---|---|
|AUTH_SUCCESS|认证成功(认证成功后,sdk会自动获取资源)|
|GET_INTERGRATION_XML|正在获取资源|
|GET_INTERGRATION_XML_SUCCESS|获取资源成功(获取资源成功后,需要主动调查询是否 有可访问的资isHaveAccessResource接口)。 如有资源,则根据AccessMode类型启动不同的资源。 详情请参考代码实例。|
|NEED_PASSWORD_AUTH|需要口令认证|
|NEED_CERT_AUTH|需要证书认证|
|NEED_DYNAMIC_TOKEN|需要动态令牌认证|
|NEED_SMS_AUTH|需要短信认证|
|NEED_TERMINAL_AUTH|需要终端认证|
|NEED_COMMIT_TERMINAL_INFO|需要提交终端信息|
|GET_REGISTERINFO_AUTH_SUCCESS|获取终端注册信息成功|
|NEED_MODIFY_PASSWORD|需要修改密码|

### **msg参数解析:** 

认证时返回的一些msg信息。 

## **7.4、AuthFailedListener解析** 

此接口为认证失败状态回调。 

### **AuthSuccessListener定义:** 

```
/**
 * 认证错误流程回调
 */
export typeAuthFailedListener= (errorCode: number, msg: string) =>void
```

### **参数解析:** 

|**参数**|**说明**|
|---|---|
|errorCode|错误code|
|msg|错误说明|

# **8、系统级别安全网关代理接口** 

SDK支持应用级别的安全代理,在初始化SDK的时候传入 

## **8.1、系统级别安全网关代理配置** 

### 1、新建一个类集成SDK中的VpnExtAbility 

```
export classMyVpnExtServicesextendsVpnExtAbility {
TAG="MyVpnExtServices"
constructor() {
super()
  }
onCreate(want: Want): void {
super.onCreate(want)
  }
}
```

- 2、在module.json5中配置这个Ability 

```
"extensionAbilities": [
      {
"name": "VpnExtAbility",
"description": "vpnServices",
"type": "vpn",
"srcEntry": "./ets/extensionAbility/MyVpnExtServices.ets"
      }
    ],
```

## **8.2、启动系统级别安全网关代理** 

### **接口说明:** 

调用此接口可以启动系统级别的安全网关代理。 

### **接口定义:** 

```
/**
   * 启动系统级别安全网关代理
   * @param abilityName ability的名称
   * @param bundleName 应用的包名
   */
startNCTunnel(abilityName:string, bundleName:string)
```

### **参数解析:** 

|**参数**|**类型**|**是否必传**|**说明**|
|---|---|---|---|
|abilityName|string|是|Ability名字,配置在module.json5的name,比如文档中这 个参数要传:VpnExtAbility|
|bundleName|string|是|应用的包名。|

**返回值解析:** 

无 

### **调用示例:** 

```
VSGService.getInstance().startNCTunnel("VpnExtAbility","com.vsg.demo")
```

## **8.3、注册、注销隧道协商状态回调** 

### **接口说明:** 

调用 **接口8.2、启动系统级别安全网关代理** 之后资源连接完成可以访问业务的回调在此接口中返回。也可 以通过此接口获取到单个资源连接的状态。 

### **接口定义:** 

```
/**
```

#### `* 注册隧道连接的所有状态回调` 

- `@param tunnelConnectSuccessStateListener 正常连接状态回调` 

- `@param tunnelConnectFailedStateListener 异常连接状态回调` 

- `@param tunnelConnectFinishListener 隧道连接完成回调 */` 

```
registerTunnelAllConnectStateListener(tunnelConnectSuccessStateListener:Tunnel
ConnectSuccessStateListener,
tunnelConnectFailedStateListener:TunnelConnectFailedStateListener,
tunnelConnectFinishListener:TunnelConnectFinishListener)
/**
   * 注销隧道连接的所有状态回调
   * @param tunnelConnectSuccessStateListener
   * @param tunnelConnectFailedStateListener
   * @param tunnelConnectFinishListener
   */
unRegisterTunnelAllConnectStateListener
(tunnelConnectSuccessStateListener:TunnelConnectSuccessStateListener,
tunnelConnectFailedStateListener:TunnelConnectFailedStateListener,
tunnelConnectFinishListener:TunnelConnectFinishListener)
```

### **参数解析:** 

|**参数**|**说明**|
|---|---|
|tunnelConnectSuccessStateListener|连接正常状态回调,具体看 TunnelConnectSuccessStateListener解析|
|tunnelConnectFailedStateListener|连接异常状态回调,具体看 TunnelConnectFailedStateListener解析|
|tunnelConnectFinishListener|所有资源连接完成,可以开始访问业务。具体看 TunnelConnectFinishListener解析|

### **返回值解析:** 

无 

### **调用示例:** 

```
lettunnelConnectFinish= () =>{
// 隧道协商完成,可以访问业务
    }
lettunnelConnectSuccessStateListener= (tunnelName: string, tunnelState:
TunnelState) => {
    }
lettunnelConnectFailedStateListener= (tunnelName: string, error:
TunnelErrorCode) => {
    }
VSGService.getInstance().registerTunnelAllConnectStateListener(tunnelConnectSuc
cessStateListener,tunnelConnectFailedStateListener,tunnelConnectFinish)
VSGService.getInstance().unRegisterTunnelAllConnectStateListener(tunnelConnectS
uccessStateListener,tunnelConnectFailedStateListener,tunnelConnectFinish)
```

## **8.3、TunnelConnectSuccessStateListener解析** 

### **接口说明:** 

资源连接的正常状态回调。 

### **接口定义:** 

```
/**
 * 隧道正常连接状态回调
 */
export typeTunnelConnectSuccessStateListener= (tunnelName: string,
tunnelState: TunnelState) =>void
```

### **参数解析:** 

|**参数**|**说明**|
|---|---|
|tunnelName|资源名称|
|tunnelState|连接状态,具体看TunnelState解析|

### **TunnelState解析:** 

|**参数**|**说明**|
|---|---|
|TunnelState. DISABLED|未连接|
|TunnelState. CONNECTING|连接中|
|TunnelState. CONNECTED|已连接|
|TunnelState. DISCONNECTING|断开连接中|
|TunnelState. CONNECTTIMEOUT|连接超时|

## **8.4、TunnelConnectFailedStateListener解析** 

### **接口说明:** 

资源连接的异常状态回调。 

### **接口定义:** 

```
/**
 * 隧道连接失败状态回调
 */
export typeTunnelConnectFailedStateListener= (tunnelName: string, error:
TunnelErrorCode) =>void
```

### **参数解析:** 

|**参数**|**说明**|
|---|---|
|tunnelName|资源名称|
|error|TunnelErrorCode隧道异常状态,具体看TunnelErrorCode的解析|

### **TunnelErrorCode解析:** 

|**参数**|**说明**|
|---|---|
|TunnelErrorState.NO_ERROR|无错误|
|TunnelErrorState. AUTH_FAILED|NC认证失败|
|其他|内部错误|

## **8.5、TunnelConnectFinishListener解析** 

### **接口说明:** 

所有资源连接完成,可以访问业务。 

### **接口定义:** 

```
/**
 * 隧道全部正常连接回调,可以访问业务回调
 */
export typeTunnelConnectFinishListener= () =>void
```

**参数解析:** 

无 

# **9、资源相关接口** 

## **9.1、是否有nc资源** 

### **接口说明:** 

调用此接口可以判断是否有NC资源可以访问。 

### **接口定义:** 

```
/**
   * 是否有nc资源
   *
   * @return s true 是 false 否
   */
haveNcResources():boolean
```

### **参数解析:** 

无 

### **返回值解析:** 

true,有NC资源; false,无NC资源。 

### **调用示例:** 

```
lethaveNcResource=VSGService.getInstance().haveNcResources()
```

**注意:** 可以在启动系统级别代理前添加此判断,如果没有nc资源,启动系统级别代理也无法去连接资 源。 

# **10、用户相关接口** 

## **10.1、获取用户状态接口** 

### **接口说明:** 

通过此接口可以获取到用户的在线状态。 

### **接口定义:** 

```
/**
   * 用户是否在线
   * @return s true 在线, false 不在线
   */
isUserOnline():boolean
```

**参数解析:** 

无 

### **返回值解析:** 

true,用户在线;false,用户不在线。 

### **调用示例:** 

## **10.2、用户状态回调** 

### **接口说明:** 

通过此接口可以获取到用户的在线状态。 

### **接口定义:** 

```
/**
   * 注册用户状态回调
   * @param stateListener 用户状态回调
   */
registerUserStateListener(stateListener:UserStateListener)
/**
   * 注销用户状态回调
   * @param stateListener
   */
unRegisterUserStateListener(stateListener:UserStateListener)
```

### **参数解析:** 

UserState枚举,表示用户在线状态。 

### **UserState解析:** 

|**参数**|**说明**|
|---|---|
|ON_LINE|用户在线|
|OFF_LINE|用户不在线|

### **返回值解析:** 

无 

### **调用示例:** 

```
letuserStateListener= (userState:UserState)=>{
if (userState==UserState.ON_LINE) {
// 用户在线
        } else {
// 用户不在线
        }
    }
VSGService.getInstance().registerUserStateListener(userStateListener)
VSGService.getInstance().unRegisterUserStateListener(userStateListener)
```

## **10.3、主动获取用户的实时在线状态** 

### **接口说明:** 

通过此接口可以主动从服务端获取用户在线状态。 

### **接口定义:** 

```
/**
   * 主动从获取用户是否在线
   * @return s
   */
getUserOnline(userStateCallBack:UserRealStateListener)
```

### **参数解析:** 

UserRealStateListener,用户是否在线回调, 

### **UserState解析:** 

|**参数**|**说明**|
|---|---|
|true|用户在线|
|false|用户不在线|

### **返回值解析:** 

无 

### **调用示例:** 

```
VSGService.getInstance().getUserOnline((isOnline: boolean)=>{
if (isOnline) {
// 在线
           } else {
// 不在线
           }
        })
```

**注意:** 此接口是直接和网关通信,获取用户在线状态,如果当前网络无法和网关连通,也会回调false。 

# **11、日志相关接口** 

SDK日志保存在应用的沙箱路径,通过本章接口可以将日志进行分享,也可以调用接口将日志打印并记 录到日志文件中。 

## **11.1、调用日志打印和存储** 

### **接口说明:** 

通过此方法可以将需要保存的日志保存到日志文件。目前SDK提供info,debug,和error三种日志记录 和打印。 

**接口定义:** 

以info日志为例子: 

```
/**
   * 打印info日志
   * @param tag tag
   * @param message message
   */
static LogI(tag:string, message:string)
```

### **参数解析:** 

|**参数**|**类型**|**说明**|
|---|---|---|
|tag|string|日志的TAG,用于日志标记。|
|message|string|日志的值,用于实际的日志|

### **返回值解析:** 

无 

### **注意:** 

### debug、fatal、error日志调用方法类似。' 

```
/**
   * 打印error日志
   * @param tag tag
   * @param message message
   */
static LogE(tag:string, message:string)
/**
   * 打印debug日志
   * @param tag tag
   * @param message message
   */
static LogD(tag:string, message:string)
```

### **调用示例:** 

```
VSGService.LogI("ShareLog", "share success")
```

## **11.2、分享日志** 

### **接口说明:** 

通过此接口可以直接将日志压缩并且分享到外部路径和应用。 

**接口定义:** 

```
/**
   * 分享日志zip包
   *
   * @param zipName
   */
shareLogZip(zipName:string)
```

### **参数解析:** 

|**参数**|**类型**|**说明**|
|---|---|---|
|zipName|string|zip包的名称,如果不传入则默认名称为:trust_access.zip|

### **返回值解析:** 

无 

### **调用示例:** 

```
""
VSGService.getInstance().shareLogZip()
```

# **12、其他接口** 

## **12.1、获取SDK版本** 

### **接口说明:** 

通过此接口可以获取到SDK的版本号。 

### **接口定义:** 

```
/**
   * SDK版本
   */
SDK_VERSION="1.0.0"
```

### **参数解析:** 

无 

### **返回值解析:** 

string,代表当前SDK的版本号。 

### **调用示例:** 

```
letversion=VSGService.getInstance().SDK_VERSION
```
