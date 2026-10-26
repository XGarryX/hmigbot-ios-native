# 顶象鸿蒙风险控制与态势感知 **SDK** 

# 前置说明 

### 本文所用的环境如下 

### IDE 版本及详情 

DevEco Studio NEXT Developer Preview2 Build Version: 4.1.3.700, built on March 19, 2024 Build #DS-223.8617.56.36.413700 Runtime version: 17.0.6+10-b829.5 amd64 VM: OpenJDK 64-Bit Server VM by JetBrains s.r.o. Windows 10 10.0 GC: G1 Young Generation, G1 Old Generation Memory: 1536M Cores: 8 Registry: external.system.auto.import.disabled=true 

### 基础依赖详情 

build-package.json5 

{ 

```arkts
"name": "riskpack", "version": "1.0.0", "description": "Please describe the basic information.", "main": "", "author": "", "license": "", "dependencies": { }, "devDependencies": { "@ohos/hypium": "1.0.16", "@ohos/hamock": "1.0.0" } } 
```

build-profile.json5 

{ "app": { "signingConfigs": [], "products": [ { "name": "default", "signingConfig": "default", "compileSdkVersion": "4.1.0(11)", "compatibleSdkVersion": "4.1.0(11)", "runtimeOS": "HarmonyOS", } ], "buildModeSet": [ { "name": "debug", }, { "name": "release" } ] }, "modules": [ { "name": "entry", "srcPath": "./entry", "targets": [ { 

"name": "default", "applyToProducts": [ "default" ] } ] } ] } 

### 本文工程的项目树结构 

- ├─.hvigor //hvigro 包管理器缓存 

- │ └─outputs 

- │ ├─build-logs 

- │ └─sync 

- ├─.idea //ide 缓存 

- │ └─.deveco 

- │ └─module 

- ├─AppScope // 项目全局配置项 

- │ └─resources 

- │ └─base 

- │ ├─element 

- │ └─media 

├─entry 

- │ ├─libs //sdk 存放目录 

- │ └─src //源码目录 

- │ ├─main 

│ │ ├─ets 

│ │ │ ├─entryability 

│ │ │ └─pages 

│ │ └─resources //资源文件 

│ │ ├─base 

│ │ │ ├─element 

│ │ │ ├─media 

│ │ │ └─profile 

│ │ ├─en_US 

│ │ │ └─element 

│ │ ├─rawfile 

│ │ └─zh_CN 

│ │ └─element 

│ ├─mock //模拟相关 

│ ├─ohosTest //测试单元相关 

├─hvigor //鸿蒙hvigor 包管理器 

└─oh_modules //基础依赖缓存 

本项目要求的权限为 

ohos.permission.INTERNET 

## 鸿蒙设备指纹 

## 导出的接口及类 

目前已实现RiskApp、RiskSdk 相关功能及接口 

### 态势感知相关的RiskSituationEventHandler、RiskSituation 暂未实现 

### 导出的类如下 

export { RiskApp,RiskSituationEventHandler,RiskSituation,RiskSdk } 

### 导出的API 如下 

### RiskSdk 导出的API 

static setupInstance(context:common.ApplicationContext): Promise<RiskSdk> getRiskApp(appId:string) : RiskAppImpl 

### RiskSdk 导出的Properties 

public static KEY_USER_ID:string = "U1"; public static KEY_USER_EMAIL:string = "U2"; public static KEY_USER_PHONE:string = "U3"; public static KEY_USER_EXTEND1:string = "U100"; public static KEY_USER_EXTEND2:string = "U101"; public static KEY_URL:string = "KEY_URL"; public static KEY_ALGORITHM:string = "KEY_MANAGER_ALGORITHM"; public static KEY_TIMEOUT_MS:string = "KEY_DELAY_MS_TIME"; public static KEY_DELAY_MS_TIME:string = "KEY_DELAY_MS_TIME"; public static KEY_SITUATION_URL:string = "KEY_SITUATION_URL"; 

### RiskApp 导出的API 

getRiskSdk():RiskSdk getAppId():string init(defaultConfig: HashMap<string, string>) : void getDegradeToken(overrideConfig:HashMap<string, string>):Promise<string> 

getToken(overrideConfig?:HashMap<string, string>):Promise<string> isDegradeToken( token:string):boolean getRiskSituation():RiskSituation 

## 单设备指纹使用场景指导 

1、首先将指纹Sdk *Har* 包放置于工程的entry/libs 

如下 

# ls -a entry\libs riskpack\entry\libs Mode LastWriteTime Length Name ---- ------------- ------ ----a---- 2024/6/4 14:18 575348 dx-risk-sdk-harmony-7.3.21.har 

特殊说明1:工程创建时默认的入口点为entry 模块,这个依情况可自行修改 特殊说明2:如入口模块无libs 文件夹,请自行创建 

2、在entry\oh-package.json5 中修改成如下 

{ "name": "entry", "version": "1.0.0", "description": "Please describe the basic information.", "main": "", "author": "", "license": "", 

"dependencies": { 

"risk" : "file:libs/dx-risk-sdk-harmony-7.3.21.har" // 新增行 } } 

此时ide 会提示sync now,同步三方依赖,点击sync now,即可完成依赖同 

步 

3、调用指纹sdk 

在工程默认创建的src\main\ets\pages\Index.ets 中,加入如下代码 

```arkts
import { RiskSdk } from "risk" import { HashMap } from '@kit.ArkTS' 
```

let riskSdk = RiskSdk.setupInstance(getContext().getApplicationContext()) let tokenConfig:HashMap<string,string> = new HashMap(); 

tokenConfig.set(RiskSdk.KEY_URL, "https://constid.dingxiang-inc.com/udid/m1") // 请填写自有 的 m1 接口地址 , 此处为 saas 服务 

riskSdk.then((riskApp) => { 

riskApp.getRiskApp("dxdxdxtest2017keyc3e83b6940835").getToken(tokenConfig).then((token) => { // 请填写自有的 appId ,此处为试用的 appId console.info("Token is : ", token) }) }) 

### 如无意外,控制台中将打印如下信息 

07-12 12:28:31.744 10861-10861 A03D00/JSAPP pid-10861 I Token is : 

666923f0uN7DzdPbEoOcv0gJeodijKbq2zqu9qg3
