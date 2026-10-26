# **-** **邦盛科技设备指纹鸿蒙 SDK集成手册V8.3.x** 

## **文档说明** 

### **本文档适用人员** 

- 邦盛设备指纹测试人员 

- 邦盛设备指纹实施人员 

- 客户鸿蒙开发以及相关人员 

### **本文档适用的SDK版本范围** 

8.3.x 

## **名词解释** 

### **设备指纹** 

通过设备信息和其他信息,确定唯一设备的技术。 

### **外码** 

设备指纹服务端返回给终端的设备指纹码。同设备每次访问服务端获取的外码都不一致。160位的 字符串。 

### **内码** 

将外码通过校验模块解析后,得到内码。同设备的内码相同,最终使用的设备指纹码。32位的字符 串。 

## **集成须知** 

支持鸿蒙5.0 (API 12) 及以上的鸿蒙系统设备; 

- DevEco Studio版本5.0.3.800 及以上; 

- 在同意隐私协议之后调用获取指纹; 

- 建议超时时间设置为5s; 

## **包内容** 

### **内容** 

dfp-sdk-harmony-{版本号}-{定制客户}-{定制版本号}-{git分支号} .har 

### **说明** 

版本号:SDK版本号,譬如8.2.0。 

- 定制客户 定制版本号:如是标准版本则未standard-。 

- git分支号:对应git分支。 

**集成步骤** 

### **导入SDK** 

1. 将下载包中的dfp-sdk-harmony-{版本号}-{定制客户}-{定制版本号}-{git分支号} .har合并入本地工 程的libs子目录下; 

2. 在项目的oh-package.json5 中的dependencies 中添加依赖"dfp_sdk": "file:./libs/dfp-sdkharmony-{版本号}-{定制客户}-{定制版本号}-{git分支号} .har"; 

3. 工程级build-profile.json5中配置 _useNormalizedOHMUrl_ 为true 

### **配置环境** 

权限配置 : 需要在module.json5文件中配置如下权限: 

```
"requestPermissions": [
      {
"name": "ohos.permission.INTERNET"// 使用网络权限
      },
      {
"name": "ohos.permission.APPROXIMATELY_LOCATION"// 模糊定位
      },
      {
"name": "ohos.permission.GET_WIFI_INFO"// WiFi信息
      },
      {
"name": "ohos.permission.GET_NETWORK_INFO"// 网络信息
      },
      {
"name": "ohos.permission.APP_TRACKING_CONSENT"// 广告ID
      },
      {
"name": "ohos.permission.ACCESS_BLUETOOTH"// 蓝牙
      }
    ]
```

## **最佳实践** 

### **普通指纹** 

#### **一、初始化** 

我们建议您在应用启动时进行初始化操作,初始化不会进行要素采集符合合规性要求,示例代码如 

下: 

```
export defaultclassEntryAbilityextendsUIAbility {
onCreate(_want: Want, _launchParam: AbilityConstant.LaunchParam): void {
frms
// 服务地址
        .setURL("http://ip:port")
// 渠道
        .setCustID("***")
// 公钥
        .setSM2PublicKey("***")
        .startup(this.context.getApplicationContext())
  }
}
```

##### 注意: 

请求地址、渠道ID、公钥请联系指纹服务端运维人员获取 

#### **二、同意授权,获取指纹** 

**获取指纹应确保用户已经接受了隐私协议** ,若为新用户或者隐私协议发生变更的情况,需确保在用 户勾选同意隐私协议之后再调用SDK获取指纹接口。示例代码如下: 

```
if("用户同意了隐私协议"){
frms.getFingerPrint(5000).then((data:string) => {
// 指纹
    }).catch((e: string) => {
// 错误信息
    })
}
```

#### **三、业务埋点** 

成功获取指纹后,即可在发起业务请求时将指纹上送,指纹数据为成功回调中返回的值。如您的业 务场景关联了指纹强规则,请确认拿到指纹后再发起业务请求,以避免出现指纹为空导致触发风控规则 增加。 

## **失败回调信息** 

|**code**|**errorMessage**|**reason**|
|---|---|---|
|1000|No network|无网络|
|1001|unknown error|未知错误|
|1002|The response data is wrong|返回数据格式错误或者内容为空|
|1004|Time out|请求超时|
|1005|Request exception|请求错误|
|1006|Get config fail|配置获取失败|
|1009|Request url is null|请求地址为空|
|1012|encrypt request body fail|加密请求体失败|
|2000|No data collected|未采集到数据|
|2001|Context is null|没有初始化|
|2002|app background|应用进入了后台|
|2003|collect fail|采集错误|
|3000|The CCID is not update|CCID不需要更新|
|3001|get sign fail|CCID获取签名失败|
|3002|get token fail|CCID获取token失败|
|3003|echange ccid fail|token换取ccid失败|
|3004|merId is null|商户ID为空|
|3005|CCID is null|CCID为空,未获取到|
|4000|verification code time out|获取认证码超时|
|4001|verification code response error|获取认证码返回错误|
|4002|verification code is unavailable|认证码开关关闭|
|4003|ccid param is not set|CCID参数错误|
