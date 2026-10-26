**启明星辰零信任SDK v1.0.8使用说明** 

启明星辰零信任SDK v1.0.8使用说明 1、修改历史 2、接入说明 

2.1、SDK开发包组成 

2.2、SDK接入 

2.2.1、通过线下静态包接入 

2.2.2、通过线上ohpm接入 

2.3、依赖的权限配置 

2.4、混淆相关 

2.5、支持的鸿蒙系统版本 

3、接口调用指南 

4、初始化SDK 

5、控制器相关接口 

5.1、设置控制器信息 

5.2、设置控制器信息回调 

6、认证相关接口 

6.1、口令认证相关 

6.1.1、口令认证 

6.1.2、修改口令密码 

6.2、扫码认证相关 

6.2.1、扫码认证 

6.2.2、获取认证二维码 6.2.3、获取二维码的Code 

6.3、短信认证相关 6.3.1、发送短信认证码 

6.3.2、短信认证 

6.4、SIM快捷认证相关 

6.4.1、SIM快捷认证 

6.4.2、停止SIM快捷认证轮询 

6.5、证书认证相关 6.5.1、本地p12证书认证 

6.6、短信主认证相关 

6.6.1、证获取图形验证码 

6.6.2、获取短信验证码 

6.6.3、短信认证 6.6.4、获取短信验证码超时时间 

6.6.5、获取发送的手机号 

6.7、获取多因素认证用户名 7、用户认证回调接口 

7.1、注册、注销认证回调 

7.2、AuthSuccessListener解析 7.4、AuthFailedListener解析 

7.5、调用示例 8、系统级别安全网关代理接口 

8.1、系统级别安全网关代理配置 

8.2、启动系统级别安全网关代理 

8.3、注册、注销隧道协商状态回调 

8.3、TunnelConnectSuccessStateListener解析 8.4、TunnelConnectFailedStateListener解析 

8.5、TunnelConnectFinishListener解析 

9、SPA种子相关接口 

- 9.1、检查种子的合法性 

   - 9.2、控制器分发种子回调 

- 10、日志相关接口 

   - 10.1、调用日志打印和存储 

   - 10.2、分享日志 

- 11、退出登录 

- 12、其他接口 12.1、获取SDK版本 

# **1、修改历史** 

|**版本号**|**日期**|**说明**|
|---|---|---|
|1.0.0||eTrust SDK基础版本|
|1.0.4|2025-08-25|1、支持SIM快捷认证 2、支持短信认证 3、支持本地P12证书认证 4、支持扫码认证 5、支持种子分发和校验。|
|1.0.8|2026-03-03|1、支持短信主认证|

# **2、接入说明** 

## **2.1、SDK开发包组成** 

**DevEcoStudio无法使用vpn type处理.pdf:** DevEcoStudio无法使用vpn type处理配置文件 

**启明星辰零信任SDKv1.0.8 使用说明.pdf:** etrust鸿蒙SDK接入文档。 

**sdp_sdk_1.0.8.har:** sdp鸿蒙SDK。 

**sdp_demo.zip:** 示例代码。 

**小于1.0.5老版本更新到最新版本编译不过可参考.pdf:** 如果已经接入了老版本,在接入新版本的时候可能 会编译失败,可以参考。 

**2.2、SDK接入** 

### **2.2.1、通过线下静态包接入** 

在项目的entry下新建一个文件夹libs,将sdp_sdk.har导入: 

**注意:** 这里为了统一管理SDK,将har包导入到此路径,pc上其他路径都行,只要ohpm install的 时候能找到,都可以。 

- 在DevEco Studio的命令行下跳转到entry目录,并通过ohpm安装sdp_sdk.har 

```
PS C:\Users\11373\DevEcoStudioProjects\sdp_demo\entry> ohpm install
libs\sdp_sdk.har
```

### **2.2.2、通过线上ohpm接入** 

sdk已经上架鸿蒙SDK应用市场:启明星辰零信任SDK-华为生态市场 

sdk已经上架ohpm库:OpenHarmony三方库中心仓 

### 可以通过如下安装命令安装SDK: 

```
ohpm install @venus_sdp/sdp_sdk
```

可以检查entry下的oh_modules路径,如果存在 @venus_sdp/sdp_sdk,那则代表导入成功! 

## **2.3、依赖的权限配置** 

### 需要依赖以下权限,缺少权限可能功能出现异常。 

```
"requestPermissions": [
      {
"name": "ohos.permission.INTERNET",   // 网络权限
      },
      {
"name": "ohos.permission.STORE_PERSISTENT_DATA"// asset文件系统权限
      },
      {
"name": "ohos.permission.GET_NETWORK_INFO"// 网络信息权限
      }
    ]
```

## **2.4、混淆相关** 

无 

## **2.5、支持的鸿蒙系统版本** 

鸿蒙5.0~最新 

# **3、接口调用指南** 

本文档提供的接口众多,可以根据以下的顺序去调用接口迅速获得系统级别的安全网关代理能力: 

### 1、调用接口 **4、初始化SDK接口** 

- 2、调用接口 **5.1、设置网关信息** 并从接口 **5.2、设置网关信息回调** 获取到链接网关成功的回调。 

- 3、调用接口 **6.1、口令认证** 并从接口 **7、用户认证回调接口** 获取到认证成功的回调 

- 4、调用接口 **8、系统级别安全网关代理接口** 开启安全网关的能力。并从接口 **8.3、注册、注销隧道 协商状态回调** 获取到隧道协商状态。获取到 tunnelConnectFinish回调之后代表隧道连接完毕,可 以访问具体业务。 

# **4、初始化SDK** 

### **接口说明:** 

`SDPService` 是 VPN SDK 的核心服务类,采用单例模式管理 VPN 相关功能模块,提供初始化、网关配 置、用户认证、退出登录等核心能力。 

### **接口定义:** 

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

|**参数**|**类型**|**必填**|**说明**|
|---|---|---|---|
|context|common.UIAbilityContext|是|UIAbilityContext|
|sdkFeature|SDKFeature|是|SDK初始化的参数,可以设置语言等,具体 看SDKFeature解析|

**SDKFeature解析:** 

|**参数**|**类型**|**说明**|
|---|---|---|
|languageType|number|语言类型SDKFeature.LANGUAGE_TYPE_CHINESE:中文 SDKFeature.LANGUAGE_TYPE_ENGLISH:英语|

### **返回值解析:** 

无 

### **调用示例:** 

```
letsdkFeature=newSDKFeature()
SDPService.getInstance().initSDK(this.context,sdkFeature)
```

### **注意:** 

建议在UIAbility的onCreate方法中调用。 

# **5、控制器相关接口** 

## **5.1、设置控制器信息** 

### **接口说明:** 

通过此接口可以设置网关信息并连接网关。连接网关的结果在 **接口5.2、设置控制器信息回调** 中返回。 

### **接口定义:** 

```
/**
   * 设置控制器接口
   * @param controller 控制器地址
   * @param port 端口
   * @param useSeed 是否使用seed
   * @param seed seed
   * @param seedPwd seedPwd
   */
setControllerInfo(controller:string, port:number, useSeed:number, seed:string,
seedPwd:string)
```

### **参数解析:** 

|**参数**|**类型**|**必填**|**说明**|
|---|---|---|---|
|controller|string|是|控制器地址|
|port|number|是|控制器端口号|
|useSeed|number|是|0不使用种子1使用种子|
|seed|string|否|种子,useSeed为1时必传|
|seedPwd|string|否|种子密码,useSeed为1时必传|

### **返回值解析:** 

无,连接网关的结果在 **接口5.2、设置控制器信息回调** 中返回。 

**调用示例:** 

```
SDPService.getInstance().setControllerInfo("198.98.174.114",5443,0,"asdfasklfa
sfasdfasdfasf","1")
```

## **5.2、设置控制器信息回调** 

### **接口说明:** 

接口 **5.1、设置网关信息** 调用之后,连接网关的结果在这个接口中返回。这部分分为两个接口, registerSetControllerInfoListener注册设置网关信息回调;unRegisterSetControllerInfoListener注销 设置网关信息回调 

### **接口定义:** 

```
/**
   * 注册设置控制器信息回调
   * @param listener listener
   */
registerSetControllerInfoListener(listener:SetControllerInfoListener)
/**
   * 注销设置控制器信息回调
   * @param listener
   */
unRegisterSetControllerInfoListener(listener:SetControllerInfoListener)
```

### **参数解析:** 

|**参数**|**类型**|**必填**|**说明**|
|---|---|---|---|
|listener|SetControllerInfoListener|是|网关配置变更回调接口实例|

### **SetGatewayInfoListener定义:** 

```
export typeSetControllerInfoListener= (retCode: SetControllerInfoRetCode) =>
void;
```

### **SetGatewayInfoRetCode参数解析:** 

SetGatewayInfoRetCode枚举提供多个参数用于标注连接控制器的状态: 

|**参数**|**说明**|**解决方案**|
|---|---|---|
|SETCONTROLLERINFO_SUCCESS|连接控制器 成功|无|
|SETCONTROLLERINFO_RESOLVE_FAILED|域名解析失 败|检查控制器地址是否正 确。|
|SETCONTROLLERINFO_SEED_INVALID|种子不 合法|检查spa种子是否传入正 确。|
|SETCONTROLLERINFO_UNREACHABLE|控制器 不可 达|检查网络是否能正常访问 的控制台地址, 可以在手机浏览器直接访 问控制台地址。|
|SETCONTROLLERINFO_SERVER_REPLY_ILLEGAL|服务端 返回 数 据错误|将日志取出给技术支持提 供分析|
|SETCONTROLLERINFO_CONNECT_SSL_ERROR|SSL协商 错误|将日志取出给技术支持提 供分析|
|其他状态|网关可能存 在其他状态|将日志提交技术支持分析|

### **返回值解析:** 

无 

### **调用示例:** 

```
letlistener= (code:SetControllerInfoRetCode)=>{
if (retCode==SetControllerInfoRetCode.SETCONTROLLERINFO_SUCCESS) {
"
ToastUtil.showToast(连接控制台成功! ")
      }
    }
// 注册连接控制器回调
SDPService.getInstance().registerSetControllerInfoListener(listener)
// 注销连接控制器的回调
SDPService.getInstance().unRegisterSetControllerInfoListener(listener)
```

# **6、认证相关接口** 

此模块详细介绍了网关的用户认证,用户认证是应用获取vpn能力的核心校验。通过用户认证,应用可 以获取到资源并且开启NC隧道。用户认证的结果在 **接口7、用户认证回调** 中返回。 

## **6.1、口令认证相关** 

**6.1.1、口令认证** 

### **接口说明:** 

通过用户名密码认证。 

### **接口定义:** 

```
/**
   * 用户口令认证
   * @param userName 用户名
   * @param userPassword 密码
   * @param isBaseAuth 是否为主认证
   */
userPasswordAuth(userName:string, userPassword:string, isBaseAuth:number)
```

### **参数解析:** 

|**参数**|**类型**|**说明**|
|---|---|---|
|userName|string|用户名|
|userPassword|string|密码|
|isBaseAuth|number|是否为主认证1主认证2辅助认证|

### **调用示例:** 

```
SDPService.getInstance().userPasswordAuth("czf","1",1)
```

### **6.1.2、修改口令密码** 

### **接口说明:** 

修改口令密码 

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

**调用示例:** 

```
SDPService.getInstance().updatePassword(this.oldPwd, this.newPwd,
this.isFirstLogin)
```

注意。当 **接口7、用户认证回调接口** 中的registerUserAuthStateListener回调 AuthState.MODIFY_PASSWD_SUCCESS状态时,代表修改口令成功。 

## **6.2、扫码认证相关** 

### **6.2.1、扫码认证** 

### **接口说明:** 

通过扫码二维码认证,当 **接口7、用户认证回调接口** 中的registerUserAuthStateListener回调 AuthState.ETRUST_QRCODEAPPSCAN_SUCCESS状态时则代表扫码认证成功。 

### **接口定义:** 

```
/**
   * 二维码code认证
   * @param uuid
   */
qrCodeAuth(qrcode:string)
```

### **参数解析:** 

|**参数**|**类型**|**说明**|
|---|---|---|
|qrcode|string|扫码二维码的code|

### **调用示例:** 

```
SDPService.getInstance().qrCodeAuth("dfdsfsdfsdf")
```

### **6.2.2、获取认证二维码** 

### **接口说明:** 

通过此接口获取认证二维码的code 

### **接口定义:** 

```
/**
   * 获取二维码认证的code
   */
getQrAuthCode()
```

### **参数解析:** 

无 

**调用示例:** 

```
SDPService.getInstance().getQrAuthCode()
```

### **6.2.3、获取二维码的Code** 

### **接口说明:** 

获取认证的二维Code的数据。当 **接口7、用户认证回调接口** 中的registerUserAuthStateListener回调 AuthState.ETRUST_QRCODEGET_SUCCESS状态时,可以调用此接口获取认证的二维码。 

### **接口定义:** 

```
/**
   * 获取二维码的数据字符
   * @return s
   */
getQrAuthCodeString():string
```

### **参数解析:** 

无 

### **调用示例:** 

```
SDPService.getInstance().getQrAuthCodeString()
```

**注意:** 此code无法直接通过Image展示,需要将其生成能给Image展示的PixelMap,具体可以参考示例 代码。 

## **6.3、短信认证相关** 

**6.3.1、发送短信认证码** 

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

|**参数**|**类型**|**说明**|
|---|---|---|
|isBaseAuth|number|是否为主认证1主认证2辅助认证|

### **调用示例:** 

```
SDPService.getInstance().sendSMSAuthCode(0)
```

**注意: 接口7、用户认证回调接口** 中的registerUserAuthStateListener回调 AuthState.BEGIN_TO_SMS_COUNT_DOWN状态时,代表发送短信成功。 

### **6.3.2、短信认证** 

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
SDPService.getInstance().startSMSCodeAuth(this.verificationCode)
```

## **6.4、SIM快捷认证相关** 

### **6.4.1、SIM快捷认证** 

### **接口说明:** 

调用此接口可以使用SIM快捷认证 

### **接口定义:** 

```
/**
   * sim快捷认证
   * @param userName 用户名
   * @param verifyCode 验证码
   * @param isBaseAuth 是否为主认证
   */
simQuickAuth(userName: string, verifyCode: string, isBaseAuth: number)
```

### **参数解析:** 

|**参数**|**类型**|**说明**|
|---|---|---|
|userName|string|用户名|
|verifyCode|string|短信验证码(sim快捷转短信认证时需要)|
|isBaseAuth|number|是否为主认证|

### **调用示例:** 

```
SDPService.getInstance().startSMSCodeAuth(this.verificationCode)
```

### **6.4.2、停止SIM快捷认证轮询** 

### **接口说明:** 

停止sim快捷轮询,可以主动停止获取sim快捷认证结果。sim快捷认证的结果为轮询获取,调用此接口 可以直接停止获取轮询结果。 

### **接口定义:** 

```
/**
   * 停止SIM快捷认证的轮询
   */
stopSimQuickPolling()
```

### **参数解析:** 

无 

### **调用示例:** 

```
SDPService.getInstance().stopSimQuickPolling()
```

## **6.5、证书认证相关** 

**6.5.1、本地p12证书认证** 

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

**参数解析:** 

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

## **6.6、短信主认证相关** 

### **6.6.1、证获取图形验证码** 

### **接口说明:** 

短信主认证获取图形验证码。 

### **接口定义:** 

```
/**
   * 短信主认证请求图形验证码
   */
SMSAuthGetVerifyCode()
/**
   * 获取二维码图片
   * @return s
   */
getVerifyCodeImage():image.PixelMap|null
```

### **参数解析:** 

无 

### **调用示例:** 

```
SDPService.getInstance().SMSAuthGetVerifyCode()
SDPService.getInstance().getVerifyCodeImage()
```

### **注意:** 

先调用SMSAuthGetVerifyCode接口,获取图形验证码,获取成功之后会在接口: **7、用户认证回调接口** 回调。关注AuthSuccessListener回调,当返回 **GET_VERIFICATION_CODE_IMAGE_SUCCESS** 时,即可 调用getVerifyCodeImage接口获取图片。图片返回的格式为:image.PixelMap, 可以直接通过Image控件 展示。比如: 

```
Image(this.pixelMap)
     .fitOriginalSize(true)
     .alt($r("app.media.ic_veriy_code_loading"))
     .height(35)
```

### **6.6.2、获取短信验证码** 

### **接口说明:** 

### 调用此接口可以请求发送短信验证码 

### **接口定义:** 

```
/**
   *
   * @param userName 用户名
   * @param verifyCode 图形验证码
   * @param isBaseAuth 是否为主认证
   */
SMSAuthSendSMSCode(userName: string, verifyCode: string, isBaseAuth: number)
```

### **参数解析:** 

|**参数**|**类型**|**说明**|
|---|---|---|
|userName|string|用户名|
|verifyCode|string|图形验证码|
|isBaseAuth|number|是否为主认证。1主认证。2多因素认证。|

### **调用示例:** 

```
SDPService.getInstance().SMSAuthSendSMSCode(this.userName, this.verifyCode,
1)
```

**注意:** 调用此接口的结果会在接口: **7、用户认证回调接口** 回调,当AuthSuccessListener回调 **BEGIN_TO_SMS_COUNT_DOWN** 时,则代表短信发送成功。 

**6.6.3、短信认证** 

### **接口说明:** 

调用此接口可以进行短信认证 

**接口定义:** 

```
/**
   * 短信认证
   * @param sms 短信
   */
startSMSAuth(sms: string)
```

### **参数解析:** 

|**参数**|**类型**|**说明**|
|---|---|---|
|sms|string|短信|

### **调用示例:** 

```
SDPService.getInstance().SMSAuthSendSMSCode(this.userName, this.verifyCode,
1)
```

**注意:** 调用此接口的结果会在接口: **7、用户认证回调接口** 回调。 

### **6.6.4、获取短信验证码超时时间** 

### **接口说明:** 

调用此接口可以获取短信验证的超时时间 

### **接口定义:** 

```
/**
   * 获取短信验证码超时时间
   * @return s
   */
getSMSTimeOut(): number
```

### **参数解析:** 

无 

### **返回值解析:** 

number,获取超时时间,单位为秒。 

### **调用示例:** 

```
SDPService.getInstance().getSMSTimeOut()
```

### **6.6.5、获取发送的手机号** 

### **接口说明:** 

调用此接口可以获取接收短信的手机号 

**接口定义:** 

```
/**
   * 获取接收短信的手机号
   * @return s
   */
getSendToPhone(): string
```

### **参数解析:** 

无 

### **返回值解析:** 

string,获取手机号。 

### **调用示例:** 

```
SDPService.getInstance().getSendToPhone()
```

## **6.7、获取多因素认证用户名** 

### **接口说明:** 

当多因素认证需要用户名时,可以调用此接口获取。 

### **接口定义:** 

```
/**
   * 获取多因素认证的用户名称
   */
getMFALoginName(): string
```

### **参数解析:** 

无 

### **返回值解析:** 

string,获取认证的用户名 

### **调用示例:** 

```
SDPService.getInstance().getMFALoginName()
```

# **7、用户认证回调接口** 

## **7.1、注册、注销认证回调** 

### **接口说明:** 

调用 **接口6、认证相关** 的认证接口,认证结果会在此接口返回。 

**接口定义:** 

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

### **参数解析:** 

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

**注意:** 这个接口会返回很多的正常的流程状态,一般来说只需要关注 

**ETRUST_FINISH_GET_INTERGRATION** 这个参数即可,这个参数是已经成功获取到所有的参数,代表 认证流程已经全部结束。 

### **AuthSuccessListener定义:** 

```
/**
     * 认证正常流程回调
     */
export typeAuthSuccessListener= (authState: AuthState, msg: string) =>
void
```

**AuthState参数解析:** 

AuthState是一个枚举,代表当前认证成功的状态。 

|**参数**|**说明**|
|---|---|
|AUTH_SUCCESS|认证成功(认证成功后,sdk会自动获取 资源)|
|ETRUST_START_GET_INTERGRATION|正在获取资源|
|ETRUST_FINISH_GET_INTERGRATION|获取资源结束,认证流程完成。|
|NEED_PASSWORD_AUTH|需要口令认证|
|NEED_CERT_AUTH|需要证书认证|
|NEED_DYNAMIC_TOKEN|需要动态令牌认证|
|NEED_SMS_AUTH|需要短信认证|
|NEED_TERMINAL_AUTH|需要终端认证|
|NEED_COMMIT_TERMINAL_INFO|需要提交终端信息|
|GET_REGISTERINFO_AUTH_SUCCESS|获取终端注册信息成功|
|NEED_MODIFY_PASSWORD|需要修改密码|
|NEED_VERIFICATION_CODE|需要验证码|
|NEED_USERNAMEPASSWORD_CHALLENGE_AUTH|需要挑战认证|
|GET_VERIFICATION_CODE_IMAGE_SUCCESS|获取图形验证码成功|

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

## **7.5、调用示例** 

```
SDPService.getInstance().registerAuthStateListener((authState: AuthState, msg:
string)=>{
      LogHelper.info("UserAuthManager"," authState is"+authState)
      if (authState == AuthState.ETRUST_FINISH_GET_INTERGRATION) {
        ToastUtil.showToast("认证成功! ")
        // 策略更新成功,可以开始开启vpn进程
        VpnAbilityHelper.getInstance().startVpnAbility("VpnExtAbility",
"com.sdp.sdp_demo")
      } else if (authState == AuthState.NEED_VERIFICATION_CODE) {
        // 需要获取图形验证码
      } else if (authState == AuthState.NEED_USERNAMEPASSWORD_CHALLENGE_AUTH) {
        // 需要挑战认证
      }
    },(errorCode: number, msg: string)=>{
      ToastUtil.showToast("认证失败! msg:"+msg+"errorCode:"+errorCode)
    })
```

# **8、系统级别安全网关代理接口** 

SDK支持应用级别的安全代理,在初始化SDK的时候传入 

## **8.1、系统级别安全网关代理配置** 

- 1、新建一个类集成SDK中的VpnExtAbility 

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

### **返回值解析:** 

无 

### **调用示例:** 

```
SDPService.getInstance().startNCTunnel("VpnExtAbility","com.vsg.demo")
```

## **8.3、注册、注销隧道协商状态回调** 

### **接口说明:** 

调用 **接口8.2、启动系统级别安全网关代理** 之后资源连接完成可以访问业务的回调在此接口中返回。也可 以通过此接口获取到单个资源连接的状态。 

### **接口定义:** 

```
/**
   * 注册隧道连接的所有状态回调
   * @param tunnelConnectSuccessStateListener 正常连接状态回调
   * @param tunnelConnectFailedStateListener 异常连接状态回调
   * @param tunnelConnectFinishListener 隧道连接完成回调
   */
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
SDPService.getInstance().registerTunnelAllConnectStateListener(tunnelConnectSuc
cessStateListener,tunnelConnectFailedStateListener,tunnelConnectFinish)
SDPService.getInstance().unRegisterTunnelAllConnectStateListener(tunnelConnectS
uccessStateListener,tunnelConnectFailedStateListener,tunnelConnectFinish)
```

## **8.3、TunnelConnectSuccessStateListener解析** 

### **接口说明:** 

### 资源连接的正常状态回调。 

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

**TunnelErrorCode解析:** 

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

### **参数解析:** 

无 

# **9、SPA种子相关接口** 

## **9.1、检查种子的合法性** 

### **接口说明:** 

调用此接口可以检查种子的合法性 

### **接口定义:** 

```
/**
   * 检查种子的合法性
   * @param seed 种子
   * @param pwd 种子密码
   * @return s true 合法 false 不合法
   */
seedCheck(seed: string, pwd: string): boolean
```

### **参数解析:** 

|**参数**|**类型**|**说明**|
|---|---|---|
|seed|string|SPA种子|
|pwd|string|种子密码|

### **返回值解析:** 

无 

**调用示例:** 

```
SDPService.getInstance().seedCheck(this.seed, this.seedPwd)
```

## **9.2、控制器分发种子回调** 

### **接口说明:** 

用户认证成功之后会控制器会主动分发一个种子给客户端,通过调用此接口可以获取到控制器给设备分 发的种子。 

### **接口定义:** 

```
/**
   * 注册请求种子监听
   * @param seedUpdateListener
   */
registerSeedUpdateListener(seedUpdateListener: SeedUpdateListener)
/**
   * 注销种子请求回调
   * @param tunnelConnectFinishListener  隧道全部正常连接回调,可以访问业务回调
   */
unRegisterSeedUpdateListener(seedUpdateListener: SeedUpdateListener)
```

### **参数解析:** 

|**参数**|**类型**|**说明**|
|---|---|---|
|SeedUpdateListener|种子更新监听|请看SeedUpdateListener说明|

### **SeedUpdateListener说明:** 

```
export type SeedUpdateListener = (controller: string, port: number, seed:string)
=> void
```

### **SeedUpdateListener参数解析:** 

|**参数**|**类型**|**说明**|
|---|---|---|
|controller|string|控制器|
|port|number|端口|
|seed|string|分发的种子|

### **返回值解析:** 

无 

### **调用示例:** 

```
seedUpdateListener= (controller: string, port: number, seed:string) => {
  }
registerSeedUpdate() {
SDPService.getInstance().registerSeedUpdateListener(this.seedUpdateListener)
  }
onDestroy() {
SDPService.getInstance().unRegisterSeedUpdateListener(this.seedUpdateListener)
  }
```

**注意:** 分发的种子默认密码为1. 

# **10、日志相关接口** 

SDK日志保存在应用的沙箱路径,通过本章接口可以将日志进行分享,也可以调用接口将日志打印并记 录到日志文件中。 

## **10.1、调用日志打印和存储** 

### **接口说明:** 

通过此方法可以将需要保存的日志保存到日志文件。目前SDK提供info,debug,和error三种日志记录 和打印。 

### **接口定义:** 

### 以info日志为例子: 

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

**注意:** 

debug、fatal、error日志调用方法类似。' 

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
SDPService.LogI("ShareLog", "share success")
```

## **10.2、分享日志** 

### **接口说明:** 

### 通过此接口可以直接将日志压缩并且分享到外部路径和应用。 

### **接口定义:** 

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
|zipName|string|zip包的名称,如果不传入则默认名称为:etrust_log.zip|

### **返回值解析:** 

无 

### **调用示例:** 

```
""
SDPService.getInstance().shareLogZip()
```

# **11、退出登录** 

### **接口说明:** 

调用此接口会退出用户登录,停止隧道连通。 

### **接口定义:** 

```
/**
   * 退出登录
   */
logout()
```

### **参数解析:** 

无 

### **返回值解析:** 

### 无 

### **调用示例:** 

```
SDPService.getInstance().logout();
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
SDK_VERSION="1.0.2"
```

### **参数解析:** 

无 

### **返回值解析:** 

string,代表当前SDK的版本号。 

### **调用示例:** 

```
letversion=SDPService.getInstance().SDK_VERSION
```
