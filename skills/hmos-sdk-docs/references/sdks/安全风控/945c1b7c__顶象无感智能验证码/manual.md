# 顶像鸿蒙 **NEXT** 验证码集成文档 

## 前置说明 

本文所用的环境如下 

IDE 版本及详情 DevEco Studio NEXT Developer Preview2 Build Version: 4.1.3.700, built on March 19, 2024 Build #DS-223.8617.56.36.413700 Runtime version: 17.0.6+10-b829.5 amd64 VM: OpenJDK 64-Bit Server VM by JetBrains s.r.o. Windows 10 10.0 GC: G1 Young Generation, G1 Old Generation Memory: 1536M Cores: 8 Registry: external.system.auto.import.disabled=true 

### 基础依赖详情 

build-package.json5 

{ "name": "riskpack", "version": "1.0.0", "description": "Please describe the basic information.", "main": "", "author": "", "license": "", "dependencies": { }, "devDependencies": { "@ohos/hypium": "1.0.16", "@ohos/hamock": "1.0.0" } } 

build-profile.json5 

{ "app": { 

"signingConfigs": [], "products": [ { "name": "default", "signingConfig": "default", "compileSdkVersion": "4.1.0(11)", "compatibleSdkVersion": "4.1.0(11)", "runtimeOS": "HarmonyOS", } ], "buildModeSet": [ { "name": "debug", }, { "name": "release" } ] }, "modules": [ { "name": "entry", "srcPath": "./entry", "targets": [ { "name": "default", "applyToProducts": [ "default" ] } ] } ] } 

### 本文工程的项目树结构 

├─ .hvigor //hvigro 包管理器缓存 │ └─ outputs │ ├─ build-logs │ └─ sync ├─ .idea //ide 缓存 │ └─ .deveco │ └─ module ├─ AppScope // 项目全局配置项 

└─ │ resources │ └─ base │ ├─ element │ └─ media ├─ entry │ ├─ libs //sdk 存放目录 │ └─ src // 源码目录 │ ├─ main │ │ ├─ ets │ │ │ ├─ entryability │ │ │ └─ pages │ │ └─ resources // 资源文件 │ │ ├─ base │ │ │ ├─ element │ │ │ ├─ media │ │ │ └─ profile │ │ ├─ en_US │ │ │ └─ element │ │ ├─ rawfile │ │ └─ zh_CN │ │ └─ element │ ├─ mock // 模拟相关 │ ├─ ohosTest // 测试单元相关 ├─ hvigor // 鸿蒙 hvigor 包管理器 └─ oh_modules // 基础依赖缓存 

### 本项目要求的权限为 

ohos.permission.INTERNET 

## 鸿蒙智能验证码 

## 导出 **API** 接口及类 

顶像鸿蒙验证码以子组件的实现对上层应用提供支持 

导出的子组件如下 

CaptchaView({ callBack:(view:CaptchaViewController) => { view.init(appid:string) view.initTokenProvider(providerCallback) view.initConfig(HashMap<string, JsonValueType>) view.startToLoad(listener) } 

}) 

#### 特殊说明 : 

- view 为子组件的 controller ,控制验证码子组件的行为,其中需要传入 4 个参数,分别由 4 个方法传入 1 、 init 方法,注册 appid 

- 2 、 initTokenConfig ,配合顶像设备指纹 SDK 使用,需要主动调用顶像设备指纹,并以 Callback 的形式进行 注册 , 如无请忽略 

- 3 、 initConfig ,注册验证码配置,此处私有化与 SaaS 有所区分,下文会详细说明 

- 4 、 startToLoad ,开启验证码加载事件,需要传入验证码事件监听器,下文会详细说明 

## 单验证码使用场景 

- 1 、首先将验证码 Sdk *Har* 包放置于工程的 entry/libs 

|如下|||
|---|---|---|
|# ls -a entry\libs|||
|riskpack\entry\libs|||
|Mode|LastWriteTime         Length Name||
|----|-------------         ------ ----||
|-a----|2024/6/12 11:10|40303|
|dx-captcha-sdk-harmon|y-v5.4.8st.341cac08.har||

特殊说明 1 :工程创建时默认的入口点为 entry 模块,这个依情况可自行修改 特殊说明 2 :如入口模块无 libs 文件夹,请自行创建 

- 2 、在 entry\oh-package.json5 中修改成如下 

{ 

"name": "entry", "version": "1.0.0", "description": "Please describe the basic information.", "main": "", "author": "", "license": "", "dependencies": { "dx.captcha" : "dx-captcha-sdk-harmony-v5.4.8st.341cac08.har" // 新增行 

} 

此时 ide 会提示 sync now ,同步三方依赖,点击 sync now ,即可完成依赖同步 

3 、调用验证码 SDK 

SaaS 集成 

SaaS 验证码分为 v2 与 v5 两种版本,调用方式并无区别 

CaptchaView 代表 v2 版本, CaptchaViewV5 代表 v5 版本 

注意!, v2 的默认宽高比为 300x200 , v5 默认宽高比为 362x335 

### 以下以 v2 为例 

```arkts
import {CaptchaView, CaptchaViewV5, CaptchaViewController, JsonValueType} from 'dx.captcha' // 如有客制化配置,请自行配置,然后将下方 initConfig 中的入参换成 config //HashMap<string, JsonValueType> config = new HashMap() //config.set("PRIVATE_CLEAR_TOKEN", "true") // 强制每次请求都刷新 token ,可选配置 //config.set("language", "cn") // 显示语言,可选配置 @Entry @Component struct Index { build() { Row() { Column() { CaptchaView({callBack:(view:CaptchaViewController)=> { view.init("dxdxdxtest2017keyc3e83b6940835") // 请填写自有 Appid view.initTokenProvider(null) view.initConfig(new HashMap()) view.startToLoad((event:string, args:JsonValueType)=> { if (event === "success") { if (args instanceof HashMap) { console.info("Token is : ", args.get("token")) } } }) }}) 
```

.width('100%') .height(200) } .width('100%') } .height('100%') } } 

### 验证成功后应在控制台中打印如下内容 

07-12 14:35:38.287 30369-30369 A03D00/JSAPP com.OpenH...riskpack I Token is B66952D82A844936A6CE0A9980930AAF8E8558E1E5C07176E9BEB73D7071EFFC35392C7C27CA 854959ABE247FDC6BF7E068BE9ECA502552E6F826850EF4566C42F58994440A2157E96224E652 F280B8C: 

### 私有化集成 

私有化仅有 v2 版本,即 CaptchaView 

```arkts
import {CaptchaView, CaptchaViewV5, CaptchaViewController, JsonValueType} from 'dx.captcha' let config:HashMap<string, JsonValueType> = new HashMap(); config.set("isSaaS", false) config.set("ua_js", "http://xxx.xxx.xxx.xxx/dx-captcha/libs/greenseer.js") config.set("language", "cn") // 显示语言,可选配置 config.set("apiServer", "http://xxx.xxx.xxx.xxx") config.set("constIDServer", "http://xxx.xxx.xxx.xxx/udid/m1") config.set("captchaJS", "http://xxx.xxx.xxx.xxx/dx-captcha/index.js") config.set("PRIVATE_CLEAR_TOKEN", "true") // 强制每次请求都刷新 token ,可选配置 config.set("corsBaseURL", "http://xxx.xxx.xxx.xxx/") // 解决跨域问题,私有化必填 config.set("appId", "appid") // 请填写自有 Appid @Entry @Component struct Index { build() { Row() { Column() { 
```

CaptchaView({callBack:(view:CaptchaViewController)=> { view.init("appid") // 请填写自有 Appid view.initTokenProvider(null) view.initConfig(new HashMap()) view.startToLoad((event:string, args:JsonValueType)=> { if (event === "success") { if (args instanceof HashMap) { console.info("Token is : ", args.get("token")) } } }) }}) .width('100%') .height(200) } .width('100%') } .height('100%') } }
