# **sdp_sdk使用指南** 

本文档旨在让接入方能了解大概接入和使用流程,具体的接口,参数还需要参照接口文档。 

## **1、添加SDK依赖** 

### **1.1、在Terminal窗口中,执行如下命令进行安装。** 

```
ohpm install @venus_sdp/sdp_sdk
```

### **1.2、联系产品经理获得har静态包安装** 

产品经理邮箱: [wang_yiming@venusgrouip.com.cn] 

```
ohpm install sdp_sdk.har
```

## **2、权限** 

```
"requestPermissions": [
 {
 "name": "ohos.permission.INTERNET",   // 网络权限
},
 {
 "name": "ohos.permission.STORE_PERSISTENT_DATA" // asset文件系统权限
},
 {
 "name": "ohos.permission.GET_NETWORK_INFO"   // 网络信息权限
}
 ]
```

## **3、导入模块** 

```
import { SDPService } from '@venus_sdp/sdp_sdk';
```

## **4、使用说明** 

### **4.1、初始化** 

SDPService 是 VPN SDK 的核心服务类,采用单例模式管理 VPN 相关功能模块,提供初始化、网关配 置、用户认证、退出登录等核心能力,需要在调用这些接口前先调用此接口,需要用户同意隐私协议之 后调用。 

```
letsdkFeature=newSDKFeature()
SDPService.getInstance().initSDK(this.context,sdkFeature)
```

**4.2、设置控制器信息** 

调用设置控制器信息相关的接口可以设置网关信息并连接网关。连接网关的结果在回调中返回。 

### 设置控制器信息: 

```
SDPService.getInstance().setControllerInfo("198.98.174.114",5443,0,"asdfasklfa
sfasdfasdfasf","1")
```

### 设置控制器信息回调: 

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

### **4.3、认证** 

SDK提供多种认证方式,可以根据具体的业务进行调用。认证的结果通过回调返回。以口令认证为示 例: 

### 调用口令认证: 

```
SDPService.getInstance().userPasswordAuth("czf","1",1)
```

### 认证回调: 

```
SDPService.getInstance().registerAuthStateListener((authState: AuthState, msg:
string)=>{
LogHelper.info("UserAuthManager"," authState is"+authState)
if (authState==AuthState.ETRUST_FINISH_GET_INTERGRATION) {
"
ToastUtil.showToast(认证成功! ")
 } elseif (authState==AuthState.NEED_VERIFICATION_CODE) {
// 需要获取图形验证码
} elseif (authState==AuthState.NEED_USERNAMEPASSWORD_CHALLENGE_AUTH) {
// 需要挑战认证
}
 },(errorCode: number, msg: string)=>{
"
ToastUtil.showToast(认证失败! msg:"+msg+"errorCode:"+errorCode)
 })
```

### **注意:** 其他认证和认证的详细参数等信息请参考接口文档。 

### **4.4、启动系统级别安全网关** 

- 1、新建一个类集成SDK中的VpnExtAbility 

```
 export class MyVpnExtServices extends VpnExtAbility {
    TAG = "MyVpnExtServices"
    constructor() {
        super()
    }
    onCreate(want: Want): void {
        super.onCreate(want)
    }
 }
```

### 2、在module.json5中配置 

```
"extensionAbilities": [
 {
 "name": "VpnExtAbility",
 "description": "vpnServices",
 "type": "vpn",
 "srcEntry": "./ets/extensionAbility/MyVpnExtServices.ets"
 }
 ]
```

### 3、认证1成功之后启动系统级别的网关代理 

```
SDPService.getInstance().startNCTunnel("VpnExtAbility","com.vsg.demo")
```

### 4、各种资源连接状态回调 

```
let tunnelConnectFinish = () =>{
 // 隧道协商完成,可以访问业务
}
 let tunnelConnectSuccessStateListener = (tunnelName: string, tunnelState:
TunnelState) => {
 }
 let tunnelConnectFailedStateListener = (tunnelName: string, error:
TunnelErrorCode) => {
 }
 SDPService.getInstance().registerTunnelAllConnectStateListener(tunnelConnectSuc
 cessStateListener,tunnelConnectFailedStateListener,tunnelConnectFinish)
```

### **4.5、退出登录** 

### 调用此接口可以退出用户登录。 

```
 SDPService.getInstance().logout()
```
