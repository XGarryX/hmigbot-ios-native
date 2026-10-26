# 财人汇 **sdk** 集成文档 

财人汇sdk集成文档 

一 、业务介绍 

二、环境要求 

- 三、快速接入 

      1. 引用sdk 

   - 2.entry中设置包名间接引用 

   - 3.声明本地引用三方har库及核心库 

      2. 初始化sdk 

   - 3.权限配置 

   4. 调起业务 

4.1 通过配置文件打开 

4.2 通过url打开 

4.3 打开页面的入参 

5. 业务交互 

一 5.1 统 登录(账号密码方式) 

一 5.2 统 登录(token方式) 

- 5.2 SDK通知客戶端信息 

- 5.3 双录集成 

## 一 、业务介绍 

## 二、环境要求 

##### SDK 

SDK基于 `HarmonyOS Next API 12` 开发 

##### DevEco Studio 

需要 `5.0.3.800+` 

## 三、快速接入 

### **1.** 引用 **sdk** 

Harmony SDK 需要在 `entry` 的 `oh-package.json5` 中添加Har引用。 

```
根据不同业务,har库可能有所不同,只需要按sdk中提供的har包引用即可。
"dependencies":{
//anychat
"@crh/anychat":"file:../libs/CRHAnychat.har",
//活体
"@crh/yidao_detect":"file:../libs/CRHYidaoDetect.har",
//易道ocr
"@crh/yidao_ocr":"file:../libs/CRHOcrManager.har",
//核心库
"@crh/main":"file:../libs/CRHMain.har",
//单向性
"@crh/single":"file:../libs/CRHSingle.har",
"@crh/record_base":"file:../libs/CRHRecordBase.har"
}
```

易道OCR授权文件 `dom_exocr.lic` ,放在 `entry` 的 `rawfile` 文件夹下 

##### SDK介绍 

1. CRHAnychat: Anychat提供的双向视频SDK 

2. CRHCore:财人汇通用库 

3. CRHAnychat:财人汇双向视频业务逻辑 

4. CRHSingle:财人汇单项视频业务逻辑 

5. CRHMain: 财人汇网厅开戶基础业务逻辑 

6. exocrdomsdk:易道博识提供的OCR sdk 

7. class-transformer:易道OCR支持库 

8. CRHOcrManager:财人汇网厅开戶OCR业务逻辑 

9. sdk_liveness:商汤活体sdk 

10. CRHSTDetect:财人汇商汤活体业务逻辑 

### **2.entry** 中设置包名间接引用 

一 在 `entry` 中的 `build-profile.json5` ,引用需要和 `工程级` 的 `oh-package.json5` 中的 样 

```
"buildOption":{
"arkOptions":{
"runtimeOnly":{
"packages":[
"@crh/main",
"@crh/yidao_ocr",
"@crh/st_detect",
"@crh/anychat",
"@crh/single",
"@crh/record_base"
]
}
}
}
```

### **3.** 声明本地引用三方 **har** 库及核心库 

Harmony SDK 需要在 `主工程` 的 `oh-package.json5` 中添加Har引用 

"overrides": { //核心库 "@crh/core": "file:./libs/CRHCore.har", "anychat_sdk": "file:./libs/anychat_sdk.har", "exocrdomsdk": "file:./libs/exocrdomsdk.har", "hisignlive": "file:./libs/hisignlive.har", } 

### **2.** 初始化 **sdk** 

在调起sdk之前,需要对sdk进行初始化,需要在 `Ability` 中的 `onCreate` 方法中初始化 

```
export defaultclassEntryAbilityextendsUIAbility{
onCreate(want: Want, launchParam: AbilityConstant.LaunchParam):void{
    CRHModule.instance().init(this.context)
}
}
```

### **3.** 权限配置 

财人汇sdk依赖以下权限声明,需要在 `module.json5` 中声明以下权限 

|权限|说明|使用范围|
|---|---|---|
|ohos.permission.INTERNET|网络访问|通用|
|ohos.permission.CAMERA|摄像头|OCR识别、单项视频录制, 双向视频,活体检测|
|ohos.permission.MICROPHONE|麦克风|双向视频,单项视频录制|
|ohos.permission.LOCATION|精准定位|定位附近营业厅|
|ohos.permission.APPROXIMATELY_LOCATION|模糊定位|定位附近营业厅|
|ohos.permission.GET_WIFI_INFO|获取网络信息|业务办理留档|
|ohos.permission.GET_NETWORK_INFO|获取网络信息|业务办理留档|

```
"requestPermissions":[
{
"name":"ohos.permission.INTERNET",
"usedScene":{
"abilities":[
"EntryAbility"
],
"when":"always"
}
},
{
"name":"ohos.permission.CAMERA",
"reason":"$string:reason",
"usedScene":{
"abilities":[
"EntryAbility"
],
"when":"inuse"
}
},
{
"name":"ohos.permission.MICROPHONE",
"reason":"$string:reason",
"usedScene":{
"abilities":[
"EntryAbility"
],
"when":"inuse"
}
},
{
"name":"ohos.permission.LOCATION",
//用于获取精准位置,精准度在米级别
"reason":"$string:reason",
"usedScene":{
"abilities":[
"EntryAbility"
],
"when":"inuse"
}
},
{
//获取到模糊位置,精确度为5公里。
"name":"ohos.permission.APPROXIMATELY_LOCATION",
"reason":"$string:reason",
"usedScene":{
"abilities":[
"EntryAbility"
],
"when":"inuse"
}
}
{
//获取网络类型
"name":"ohos.permission.GET_WIFI_INFO"
},
{
"name":"ohos.permission.GET_NETWORK_INFO",
"usedScene":{
"abilities":[
"EntryAbility"
],
"when":"always"
}
}
]
```

### **4.** 调起业务 

#### **4.1** 通过配置文件打开 

把配置文件 `servers.xml` 放入 `rawfile` 文件夹中 打开页面 

```
let crhParams: CRHParams ={
            type:0
}
  CRHOpenModule.getInstance().openCrhSdkModule(crhParams);
```

#### **4.2** 通过 **url** 打开 

```
let crhParams: CRHParams ={
            indexUrl:url
}
  CRHOpenModule.getInstance().openCrhSdkModule(crhParams);
```

#### **4.3** 打开页面的入参 

```
 CRHParams
```

|参数|类型|说明|
|---|---|---|
|indexUrl|string|打开对应的业务的indexUrl|
|mobileNo|string|注册手机号,第三方嵌入时如果要传入手机号 用此方法 (手机号已经在第三方客戶端获取)|
|channel|string|打开sdk所对应的渠道 非必填不传默认读菜单列表页配置渠道|
|username|string|登录网厅所需的资金账号,账号需要拼接类型参数,拼接方式如下表格|
|password|string|登录网厅所需的资金账号密码|
|ext|string|新增拓展参数crhParams.ext = @"&a=b&c=d"|
|appId|string|开戶的appID|
|opStation|string|站点信息|

### **5.** 业务交互 

#### 一 **5.1** 统 登录(账号密码方式) 

##### 一 `注册` 统 登录回调、并在回调方法中调起登录页面 

###### `// 使用账号密码方式统一登录` 

```
RHOpenModule.getInstance().setCallLoginView((loginSuccess:(userName:string, loginPassWord:str
// 唤起统一登录界面
});
```

一 `登录完成` 后,调用统 登录调起提供的 `loginSuccess` 方法 

```
//登录成功之后调用回调 loginType没有传""
loginSuccess('userName','passWord','loginType');
```

`网厅退出` 通知客戶端 

```
     CRHOpenModule.getInstance().setCallLogout(()=>{
//app退出登录
})
```

> `页面打开前` 已经登陆,则打开页面时候入参账号密码 

```
let crhParams: CRHParams ={
            type:0,
            password:"",
            username:""
}
  CRHOpenModule.getInstance().openCrhSdkModule(crhParams);
```

`取消登录` 时,调用取消登录方法 

```
//取消登录
loginCancel();
退出登录
CRHOpenModule.getInstance().logout()
```

#### 一 **5.2** 统 登录( **token** 方式) 

##### 一 `注册` 统 登录回调、并在回调方法中调起登录页面 

```
//token登录
    CRHOpenModule.getInstance()
.setDoLogin((loginSuccess:(token:string, mobileNo:string)=>void,loginCancel:()=>v
})
```

一 `登录完成` 后,调用统 登录调起提供的 `loginSuccess` 方法 

```
//登录成功之后调用回调
loginSuccess('token','mobileNo');
```

##### `页面打开前` 已经登陆,则打开页面时候入参账号密码 

```
let crhParams: CRHParams ={
            type:0,
            token:"token"
}
  CRHOpenModule.getInstance().openCrhSdkModule(crhParams);
```

##### `网厅退出` 通知客戶端 

```
     CRHOpenModule.getInstance().setCallLogout(()=>{
//app退出登录
})
```

##### `取消登录` 时,调用取消登录方法 

```
//取消登录
loginCancel();
退出登录
CRHOpenModule.getInstance().logout()
```

#### **5.2 SDK** 通知客戶端信息 

一 SDK与客戶端的交互都是通过 `openExtraModule` 接口的,交互协议与ios和安卓 致。 

##### 注册交互接口 

```
//调起第三方页面
    CRHOpenModule.getInstance().setOpenExtraModule((jsonStr:string,callback:(json:string)=>
//回调sdk
callback("json")
})
```

#### **5.3** 双录集成 

##### 调起双录 

```
let doubleRecordJsModel: DoubleRecordJsModel ={
          url:'https://hl.sltest.cairenhui.com/#/index',//双录地址
          username:'10000005',// 资产账户【必须】
          password:'111111',// 密码【必须】
          prodCode:'S49148',// 产品代码【必须】
          prodNo:'CZZ',// 产品TA编号【必须】
          apiBase:'http://192.168.9.14:9090',
          apiUrl:'',
          callback:'',
          token:'',// token 和账号密码二选1
          deviceId:'3',
          demoMode:false,
          securitiesTrader:'',
};
        CRHOpenModule.getInstance().openCRHDRModule(doubleRecordJsModel)
```

##### 设置回调 

```
 CRHModuleManger.getInstance().setDRecordCallback((code:number)=>{
// code =200 成功
})
```
