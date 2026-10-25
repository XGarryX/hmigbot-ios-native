# **Harmony** **OS SDK开发指南** 

```
OLYM鸿蒙SDK安全中间件
```

## **修订记录** 

|**版本**|**修订内容**|**修订人**|**修订日期**|**备注**|
|---|---|---|---|---|
|V1.0.0|文档创建|钟锡伟|2025-03-18|初始版本|

## **概述** 

##### 内部SDK说明: 

奥联密码中间件Harmony OS SDK:cryptoterminate-(xxx).har(目前鸿蒙版本:xxx为提供的版 本日期),目前提供HAR方式集成sdk。 

**DevEco Studio版本建议5.0.4以上(包含5.0.4版本)** 

## **集成步骤** 

### **服务器增加相应的帐号** 

请参考服务器相关文档 

### **导入SDK** 

安装命令:ohpm i cryptoterminate 

也可通过以下方式手动工程引用 

#### **集成奥联SDK** 

奥联提供安全的密码中间件,用于进行密码运算等,目前版本鸿蒙版。 

新建文件夹libs,将cryptoterminate-(xxx).har文件拷贝到libs目录下; 

工程目录下oh-package.json5文件中添加如下配置: 

```
{
//...
"dependencies": {
//...
"cryptoterminate": "file:../libs/cryptoterminate-(xxx).har"
  }
}
```

cryptoterminate-(xxx).har文件名称中的xxx指版本日期,请注意替换。 

**版本说明** 

支持API12及以上版本。 

#### **权限说明** 

module.json5文件添加如下权限: 

```
{
  "module": {
    "requestPermissions":[
      {
        "name": "ohos.permission.INTERNET"
      }
    ]
  }
}
```

## **功能使用说明** 

1、执行SDK密钥加载、密码运算相关操作之前,必需先初始化SDK; 

2、SDK相关的API主要在SM9Pcs.ets、SM2Pcs.ets类中,这里和密钥类型对应,SM9分片密钥选 择SM9Pcs.ets,SM2分片密钥类型选择SM2Pcs.ets,密钥类型详见"初始化SDK"的keyType。 

### **SDK初始化** 

SDK初始化方法涉及到密钥的下载、加载以及密码相关操作相关,使用这些功能前需执行初始化操 作。 

#### **接口名称** 

initSDK 

#### **参数说明** 

|**字段名称**|**字段类型**|**字段描述**|
|---|---|---|
|context|Context|上下文对象|
|config|EngineConfig|引擎配置信息。 属性如下: { "serverURL": "", //统服地址,用于下载密钥等 "clientId":"",//机构AppId(如果是默认机构,可不填) "clientSecret":"",//机构secretKey(如果是默认机构,可不填) "getRandomURL": "", //第三方获取随机数服务器地址 "verifyServerURL": "", //第三方认证服务器地址 "keyType": 3, //密钥类型,常用类型1:SM9完整密钥,3:SM9分 片密钥5:SM2分片密钥 具体查看PMKEYTYPE枚举类 }|

#### **返回值** 

TsRes对象: 

{ 

"ts_code":1,//状态码,1:成功,其它:错误编码 

"ts_data":"", 

"ts_msg":"初始化成功", 

} 

#### **示例** 

```
SM9Pcs.getInstance().initSDK(context, engineConfig).then((value: TsRes) => {
showToast(value.ts_msg);
        });
```

### **查找密钥** 

查找本地有没有密钥 

#### **接口名称** 

findKey 

#### **参数说明** 

|**字段名称**|**字段类型**|**字段描述**|
|---|---|---|
|userId|string|用户标识|

#### **返回值** 

PMKeyRes对象: 

{ 

"ts_code":1,//状态码,1:成功,其它:错误编码 

"ts_data":"", 

"pmKey": [obj23],//PMKey对象 

} 

#### **示例** 

```
letpmKey=SM9Pcs.getInstance().findPMKey(modeConfig.userId).pmKey;
```

### **加载密钥(密码方式)** 

使用密钥之前,先加载,如果没有密钥,则会下载。 

#### **接口名称** 

loadKey 

#### **参数说明** 

|**字段名称**|**字段类型**|**字段描述**|
|---|---|---|
|userId|string|用户标识|
|password|string|标识密码|

#### **返回值** 

PMKeyRes对象: 

{ 

"ts_code":1,//状态码,1:成功,其它:错误编码 

"ts_data":"", 

"pmKey": [obj23],//PMKey对象 

"ts_msg":"加载密钥成功", 

} 

#### **示例** 

```
SM9Pcs.getInstance().loadKey(modeConfig.userId,modeConfig.password).then((value:
PMKeyRes) => {
showToast(value.ts_msg);
        });
```

### **发送短信验证码** 

通过双因子(密码、短信验证码)下载密钥,先发送短信验证码。 

#### **接口名称** 

sendVerifyCode 

#### **参数说明** 

|**字段名称**|**字段类型**|**字段描述**|
|---|---|---|
|userId|string|用户标识|
|password|string|标识密码|

#### **返回值** 

TsRes对象: 

{ 

"ts_code":1,//状态码,1:成功,其它:错误编码 

"ts_data":"", 

"ts_msg":"", 

} 

```
SM9Pcs.getInstance().sendVerifyCode(modeConfig.userId,modeConfig.password).then(
(value: TsRes) => {
showToast(value.ts_msg);
        });
```

### **加载密钥(验证码方式)** 

使用密钥之前,先加载,如果没有密钥,通过密码、短信验证码下载密钥。 

#### **接口名称** 

loadKeyByCode 

#### **参数说明** 

|**字段名称**|**字段类型**|**字段描述**|
|---|---|---|
|userId|string|用户标识|
|password|string|标识密码|
|verifyCode|string|短信验证码|

#### **返回值** 

PMKeyRes对象: 

{ 

"ts_code":1,//状态码,1:成功,其它:错误编码 

"ts_data":"", 

"pmKey": [obj23],//PMKey对象 

"ts_msg":"下载密钥成功", 

} 

**示例** 

```
SM9Pcs.getInstance().loadKeyByCode(config.userId,config.password,verifyCode).th
en(tsRes=> {
showToast(tsRes.ts_msg);
      });
```

### **连接VPN** 

设置配置信息,进行vpn连接,常用连接SRP5(临时通道)、TLS、SSL。 

#### **接口名称** 

connectVPN 

#### **参数说明** 

|**字段名**|**字段类型**|**字段描述**|
|---|---|---|
|userId|string|用户标识|
|vpnContext|VpnExtensionContext|创建vpn的上下文对象|
|vpnConfig|VPNConfig|建立vpn连接的配置信息。 属性如下(以下值为默认值): { "NTLSServer": "", //VPN服务器地址 "NTLSServerPort": 3000, //VPN端口 "connectType":2, //连接类型:0:VPN_SRP5 1:VPN_TLS 2:VPN_SSL具体查看枚举类VPNConnectType "networkLayer":true, //VPN工作模式,false为四层 true为三层模式 "bindDevice":false, //是否绑定设备 deviceId:"",//设备ID autoReconnect:true,//自动重连 compressed:false,//压缩 cipherAlg:ALG_DEM2_SM4_CBC_HMAC_SM3,//加密类 型,PbcMacro.ts文件中的的常量 protocol:VPNConnectProtocol.VPN_TCP,//通信协议 (VPN_TCP = 1, VPN_UDT = 2) callBack: OnVpnListener |null,//vpn回调监听 trustedAppArr: string[]|null, //白名单,允许访问vpn的 应用 blackAppArr: string[] |null,//黑名单,禁止访问vpn的应 用 }|

#### **返回值** 

VPNConfig配置回调监听setOnVpnListener。 

```
classVPNCallBackextendsOnVpnListener {
private TAG="VPNCallBack";
onConnectResult(vpnStatus: PMVPNStatus, exception: PMException) {
""
letmsg=连接中;
if (vpnStatus==PMVPNStatus.PMVPNStatusConnected) {
""
msg=已连接;
console.log(msg);
    } elseif (vpnStatus==PMVPNStatus.PMVPNStatusDisconnected) {
""
msg=连接已断开;
msg=exception.getMessage();
console.log(msg);
    } elseif (vpnStatus==PMVPNStatus.PMVPNStatusInvalid) {
msg=exception.getMessage();
console.log(msg);
    }
showToast(msg)
console.log("onConnectResult:vpnStatus="+vpnStatus.toString() +" msg="+
msg);
  }
vpnState(vpnStatus: PMVPNStatus): void {
""
letmsg=连接中;
if (vpnStatus==PMVPNStatus.PMVPNStatusConnecting) {
""
msg=连接中;
    } elseif (vpnStatus==PMVPNStatus.PMVPNStatusConnected) {
""
msg=已连接;
console.log(msg);
    } elseif (vpnStatus==PMVPNStatus.PMVPNStatusDisconnected) {
""
msg=连接已断开;
console.log(msg);
    } elseif (vpnStatus==PMVPNStatus.PMVPNStatusDisconnecting) {
""
msg=连接断开中;
    }elseif (vpnStatus==PMVPNStatus.PMVPNStatusReasserting) {
""
msg=安全连接正在重连;
showToast("安全连接正在重连,请稍后...")
    }
console.log("vpnState:vpnStatus="+vpnStatus.toString() +" msg="+msg);
  }
initVpnConfig(configStatus: VPNConfigStatus, error: string): void {
console.log( error );
  }
vpnBroken(connectHandle: bigint, isKickOff: boolean): void {
if (isKickOff) {
// getContext(this).eventHub.emit('vpnBroken', isKickOff);
    }
  }
}
```

**示例** 

```
//建立VPN连接。
letvpnConfig=newVPNConfig();
vpnConfig.setNTLSServer(modeConfig.NTLSServer)
          .setNTLSServerPort(modeConfig.NTLSServerPort)
          .setConnectType(VPNConnectType.VPN_TLS)
          .setNetworkLayer(true)
          .setOnVpnListener(newVPNCallBack());
SM9Pcs.getInstance().connectVPN(modeConfig.userId, modeConfig.password,
vpnConfig);
//建立VPN连接,使用VPN_SRP5连接类型,建立临时通道。
letvpnConfig=newVPNConfig();
vpnConfig.setNTLSServer(modeConfig.NTLSServer)
          .setNTLSServerPort(modeConfig.NTLSServerPort)
          .setConnectType(VPNConnectType.VPN_SRP5)
          .setNetworkLayer(false)
          .setOnVpnListener(newVPNCallBack());
SM9Pcs.getInstance().connectVPN(modeConfig.userId, modeConfig.password,
vpnConfig);
```

### **断开vpn连接** 

断开已经连接的vpn,返回状态在上述接口的回调中体现(vpnStatus == PMVPNStatus.PMVPNStatusDisconnected)。 

#### **接口名称** 

disConnectNTLS 

#### **参数说明** 

无 

#### **返回值** 

无 

#### **示例** 

```
SM9Pcs.getInstance().disConnectNTLS();
```

### **删除密钥** 

删除下载的密钥。 

#### **接口名称** 

deleteKey 

**参数说明** 

|**字段名**|**字段类型**|**字段描述**|
|---|---|---|
|userId|string|用户标识|

#### **返回值** 

TsRes对象: 

{ 

"ts_code":1,//状态码,1:成功,其它:错误编码 

"ts_data":"", 

"ts_msg":"删除密钥成功", 

} 

#### **示例** 

```
SM9Pcs.getInstance().deleteKey(modeConfig.userId).then((value: TsRes) => {
showToast(value.ts_msg);
        });
```

### **SM9加密** 

使用密钥进行SM9加密 

#### **接口名称** 

encryptText 

#### **参数说明** 

|**字段名称**|**字段类型**|**字段描述**|
|---|---|---|
|text|string|待加密的明文|

#### **返回值** 

TsRes对象: 

{ 

"ts_code":1,//状态码,1:成功,其它:错误编码 

"ts_data":"xxx",//密文,hex字符串 

"ts_msg":"加密成功", 

} 

**示例** 

```
letencryptRes=SM9Pcs.getInstance().encryptText(this.TAG);
this.encryptedText=encryptRes.ts_data;
console.log(this.TAG, "encryptedText="+this.encryptedText+" "+
encryptRes.ts_msg);
showToast(encryptRes.ts_msg);
```

### **SM9解密** 

使用密钥进行SM9解密 

#### **接口名称** 

decryptText 

#### **参数说明** 

|**字段名称**|**字段类型**|**字段描述**|
|---|---|---|
|cipher|string|待解密的密文|

#### **返回值** 

TsRes对象: 

{ 

"ts_code":1,//状态码,1:成功,其它:错误编码 

"ts_data":"xxx",//解密后的内容 

"ts_msg":"解密成功", 

} 

#### **示例** 

```
letdecryptRes=SM9Pcs.getInstance().decryptText(this.encryptedText);
console.log(this.TAG, "decryptedText="+decryptRes.ts_data+" "+
decryptRes.ts_msg);
showToast(decryptRes.ts_msg);
```

### **SM9签名** 

使用密钥进行SM9签名 

#### **接口名称** 

signData 

**参数说明** 

|**字段名称**|**字段类型**|**字段描述**|
|---|---|---|
|text|string|待签名的明文|

#### **返回值** 

TsRes对象: 

{ 

"ts_code":1,//状态码,1:成功,其它:错误编码 

"ts_data":"xxx",//签名后的内容 

"ts_msg":"签名成功", 

} 

#### **示例** 

```
lettsRes=SM9Pcs.getInstance().signData(this.TAG);
this.signedText=tsRes.ts_data;
console.log(this.TAG, "signData="+this.signedText+" "+
tsRes.ts_msg);
showToast(tsRes.ts_msg);
```

### **SM9本地验签** 

使用密钥进行SM9本地验签 

#### **接口名称** 

verifyData 

#### **参数说明** 

|**字段名称**|**字段类型**|**字段描述**|
|---|---|---|
|plainText|string|待签名的明文|
|signedText|string|签名值|

#### **返回值** 

TsRes对象: 

{ 

"ts_code":1,//状态码,1:成功,其它:错误编码 

"ts_data":"", 

"ts_msg":"签名验签成功", 

} 

**示例** 

```
letverifyRes=SM9Pcs.getInstance().verifyData(this.TAG, this.signedText);
console.log(this.TAG, "verifyData="+this.signedText+" "+this.TAG);
showToast(verifyRes.ts_msg);
```

### **释放引擎** 

释放加密引擎 

#### **接口名称** 

destroy 

#### **参数说明** 

无 

**返回值** 无 

**示例** 

```
SM9Pcs.getInstance().destroy();
```
