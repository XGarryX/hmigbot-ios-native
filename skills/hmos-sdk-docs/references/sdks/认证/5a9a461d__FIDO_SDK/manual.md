# 一、开发步骤: 

1. 需要业务方自行根据FIDO 标准协议部署FIDO 服务器。 

2. 导入FidoSdk 

import { FidoSdk } from '@gmrz/fido_sdk'; 

### 3. 获取设备信息(可选) 

### 实施方可调用该接口获取设备信息,也可自行获取设备信息,用于服务端接口请求报文的填充。 

```arkts
this.fidoSdk.getDeviceInfo().then(response=>{ let deviceInfo = JSON.parse(response.data as string) as DeviceInfo promptAction.showToast({ message: '设备信息:' + JSON.stringify(deviceInfo), duration: 5000 }) console.log("deviceInfo::",JSON.stringify(deviceInfo)); }).then(e:Error)=>{ promptAction.showToast({ message: '获取设备信息失败:' + e.message, duration: 5000 }) }) 
```

### 4、检查设备是否支持 

```arkts
let fidoRequest: FidoRequest = { protocol: FidoProtocol.UAF, op: FidoOperation.DISCOVER, mode: FidoMode.LOCAL, authTypes: [FidoAuthType.UAF_FINGER] } this.fidoSdk.checkSupport(getContext(this), fidoRequest).then(response => { //调用成功 
let fingerSupport = response.isFingerSupport(); //true 支持 //或者 let status = response.getFingerStatus();// 0:支持 }) 
```

### 5、开通FIDO 免密认证 

1)访问FIDO 服务端/uaf/reg/receive 接口,获取注册请求报文(uafRequest 部分) 

### 2)调用process 接口进行注册 

```arkts
let fidoRequest: FidoRequest = { protocol: FidoProtocol.UAF, op: FidoOperation.UAF_OPERATION, mode: FidoMode.LOCAL, data:serverMessage // 步骤1)返回报文 authTypes:[FidoAuthType.UAF_FINGER] } this.fidoSdk.process(getContext(this), fidoRequest).then(fidoResponse => { if(fidoResponse.code==FidoStatus.SUCCESS){ regSendData.uafResponse = fidoResponse.data as string; // 访问FIDO 服务端,完成注册 httpPost(this.baseUrl + "/uaf/reg/send", JSON.stringify(regSendData)).then(response => { if (response.responseCode == http.ResponseCode.OK) { let result = response.result as string et serverResponse: UAFServerResponse = JSON.parse(result) as UAFServerResponse; if (serverResponse.statusCode == 1200) { promptAction.showToast({ message: '注册成功', duration: 5000 }) } else { promptAction.showToast({ message: '注册失败(server)' + JSON.stringify(serverResponse), duration: 5000 }) } } }) }else{ promptAction.showToast({ message: '注册失败(client)' + JSON.stringify(fidoResponse), 
```

duration: 5000 }); } ) 

### 6、使用FIDO 免密认证 

### 1)访问FIDO 服务端,获取认证请求报文(uafRequest 部分) 

### 2)调用process 接口进行认证 

let fidoRequest: FidoRequest = { 

protocol: FidoProtocol.UAF, 

op: FidoOperation.UAF_OPERATION, 

mode: FidoMode.LOCAL, 

data:serverMessage, // 步骤1)返回报文 

authTypes:[FidoAuthType.UAF_FINGER] 

} 

this.fidoSdk.process(getContext(this), fidoRequest).then(fidoResponse => { 

if(fidoResponse.code==FidoStatus.SUCCESS){ 

#### //本地认证成功 

regSendData.uafResponse = fidoResponse.data as string; 

// 访问FIDO 服务端,完成认证 

httpPost(this.baseUrl + "/uaf/auth/send", JSON.stringify(regSendData)).then(response => { 

if (response.responseCode == http.ResponseCode.OK) { 

let result = response.result as string 

et serverResponse: UAFServerResponse = JSON.parse(result) as UAFServerResponse; 

if (serverResponse.statusCode == 1200) { 

promptAction.showToast({ 

message: '认证成功', 

duration: 5000 

}) 

} else { 

promptAction.showToast({ 

message: '认证失败(server)' + JSON.stringify(serverResponse), 

duration: 5000 

}) 

} 

} 

}) 

}else{ 

promptAction.showToast({ 

message: '认证失败(client)' + JSON.stringify(fidoResponse), 

duration: 5000 }); } ) 

### 7、关闭FIDO 免密认证 

### 1)访问FIDO 服务端,注销FIDO 

### 2)调用process 接口进行本地注销 

let fidoRequest: FidoRequest = { 

protocol: FidoProtocol.UAF, 

op: FidoOperation.UAF_OPERATION, 

mode: FidoMode.LOCAL, 

data:serverMessage, // 步骤1)返回报文 

authTypes:[FidoAuthType.UAF_FINGER] 

} 

this.fidoSdk.process(getContext(this), fidoRequest).then(response => { console.log("sample", JSON.stringify(response)); 

If(response.code==FidoStatus.SUCCESS){ 

promptAction.showToast({ 

message: '注销成功', 

duration: 5000 

}) 

}else{ 

promptAction.showToast({ 

message: '注销失败', 

duration: 5000 

}) } }) 

# 二、HAP 本地安装 

手机与PC 连接后: 

- 1 通过命令行进入到 <鸿蒙sdk 安装目录>/base/toolchains 目录 

- 2 执行hdc install -r <安装包绝对或相对路径> 

## 注意:安装包路径中不能包含中文目录。 

## 查看手机日志 

## 手机与PC 连接后: 

- 1 通过命令行进入到 <鸿蒙sdk 安装目录>/base/toolchains 目录 

- 2 执行hdc hilog 或者 hdc hilog > d:/hos.log 

# 三、常见问题 

1. SDK 是否需要初始化 

A:不需要 

## 2. 是否需要本地以及智能登录能力检查 

- A:checkSupport 接口,用于设备本地FIDO 支持能力检查 

3. 注册、认证如何区分指纹、人脸(不是3D) 

## A:增加了authTypes 参数,用于指定用户认证方式。 

4. getDeviceInfo 作用 

- A:辅助功能,用于填充请求报文中设备相关信息。如果用户有自己获取设备信息的方法,此接 

## 口可忽略。 

5. 注册uafRequest 字符串,是否对应fidoRequest,之前是FidoIn.Builder().setFidoIn(new String(Base64.decode(uafRequest,Base64.DEFAULT),"UTF-8")) 

- A:如果服务端返回报文是Base64 格式的话,需要先转码。SDK 本身要求报文为明文字符串。 

## 报文格式详见集成文档。 

6. 注册、认证怎么区分FidoStatus CANCELED、EXIT_THIS_TIME 

- A:已增加CANCELED 错误码,鸿蒙SDK 暂没有发现EXIT_THIS_TIME 的情况。 

7. REMOTE 方式下注册,服务端报3025 

- A:检查服务器时间是否准确。有可能是在校验证书链个人证书时,服务器时间晚于证书启用时 

间。
