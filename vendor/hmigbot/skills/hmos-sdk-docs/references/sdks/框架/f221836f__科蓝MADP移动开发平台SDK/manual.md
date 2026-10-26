# **科蓝MADP移动开发平台鸿蒙SDK使用指南** 

主要介绍madp移动开发平台鸿蒙SDK使用,包括种子工程的目录结构、配置、以及组件注册使用等 

## **一、项目目录** 

```
├──entry// 项目主入口
│├──libs// 存放使用的依赖(.har文件)。
|├──src
||├──main
|||├──ets// 用于存放ArkTS源码。
||||├──components// 项目业务组件,首页动态楼层所使用组件及通用组件。
||||├──config// 主题信息配置
||||├──entryability//应用/服务的入口文件
||||├──ohos_sdk// SDK金融方法、方法详情查看 harmonyOS SDK金融组件
||||├──pages// 应用的页面
|||||├──demopage// 项目金融基础组件及 SDK金融方法使用案例
|||||├──launcher// 项目首页
|||||├──nativescene// 透明场景交互插件扩展示例
|||||├──splash// 启动页(倒计时广告页)
|||||├──tab// 底部菜单页面
|||||├──theme// 切换主题页
||||├──uicomponents// 项目金融基础组件,组件详情查看项目金融基础组件
||||├──utils// 存放公共方法
|||├──resources// 用于存放应用所用到的资源文件,如图形、多媒体、字符串、布局文件等
|||├──module.json5// 用于存放应用/服务所用到的资源文件,如图形、多媒体、字符串、布局文件等
|├──build-profile.json5// 当前的模块信息、编译信息配置项
|├──hvigorfile.ts// 模块级编译构建任务脚本
|├──oh-package.json5// 三方包配置
```

## **二、产品配置** 

### **1、导入madp2.0 鸿蒙产品库** 

entry目录下新建libs文件夹,导入MADCore_xxx.har 

### **2、引入madp2.0 鸿蒙产品库** 

entry目录下oh-package.json5增加 **file:./libs/MADCore_xxx.har** 

如果更换har库 需同步此文件,否则不会生效 

```
{
"name": "entry",
"version": "1.0.0",
"description": "Please describe the basic information.",
"main": "",
"author": "",
"license": "",
"dependencies": {
"@ohos/crypto-js": "2.0.0",
"@csii/madcore": "file:./libs/MADCore_xxx.har",
  }
  }
```

### **3、导入注册表registry.dat** 

注册表放入entry/src/main/resources/rawfile/目录下 

### **4、配置网络权限** 

entry/src/main/module.json5配置网络权限 

```
// entry/src/main/module.json5
{
"module": {
...
"requestPermissions": [
      {
"name": "ohos.permission.INTERNET"
      },
    ],
...
  }
}
```

### **3、初始化MADP** 

entry入口页面madp产品初始化(Engine.initMADP) 

初始化位置可根据项目组实际情况调整,非必须entry入口页面 

```
// entry/src/main/ets/pages/Index.ets
import { Engine } from'@ohos/madcore';
@Entry
@Component
structIndex {
aboutToAppear(): void {
// 初始化MADP
Engine.initMADP((code: number, result: string) => {
if (code===200) {
// 配置启动
Engine.startup()
      }
    })
  }
}
```

## **三、项目配置** 

### **1、闪屏页、主页面配置** 

如果原项目是weex实现,现将weex实现的逻辑翻成鸿蒙技术栈 

如果原项目是android、IOS实现,现将android、IOS实现的逻辑翻成鸿蒙技术栈 

```
// 参考闪屏页和主页面
"entry/src/main/ets/pages/launcher/SplashPage.ets"
"entry/src/main/ets/pages/launcher/Launcher.ets"
```

### **2、注册场景** 

后管配置的weex场景,运行在鸿蒙端,需手动注册场景 

```
// entry/entryability/EntryAbility.ets
""
Engine.registerModule(场景名称, "pages/nativescene/PasswordInput(页面路径)")
```

### **2、注册组件** 

现有组件库无法满足主页面业务需求,项目组增加自定义组件的情况,需要手动注册组件。 组件工厂:entry/src/main/ets/util/ComponentsFactory.ets 

```
//以menu组件为例
// 第一步实现组件逻辑
import { MenuComponent } from"../components/MenuComponent";
// 第二步调用组件
@Builder
functionmenu(data: object) {
// data为MenuComponent 的 @Prop data: object; 所需要的数据
MenuComponent({ data: data });
}
// 第三步讲组件加入组件工厂
factoryMap.set('menu', wrapBuilder(menu))
```

### **3、权限最小化说明** 

#### **说明:** 

- 1)应用申请的权限,都必须有明确、合理的使用场景和功能说明,确保用户能够清晰明了地知道申请权限的目 的、场景、用途 

- 2)应用权限申请遵循最小化原则,只申请业务功能所必要的权限,禁止申请不必要的权限,权限须在用户使用对 应业务功能时动态申请,避免频繁弹窗申请多个权限 

#### **调用相机权限示例** 

```
// 配置路径
"entry/src/main/module.json5"
// 配置格式
{
"name": "ohos.permission.CAMERA",  // 申请权限类型
"reason": "$string:app_name", // 描述申请权限的原因
"usedScene": {
"abilities": [
"EntryAbility"
       ],
"when": "always"//标识权限使用的时机,值为- inuse:表示为仅允许前台使用/- always:表示前后
台都可使用
    }
},
```

## **三、接口请求** 

#### **1.说明** 

- 可以使用HttpClient集成好的方法,进行请求接口的调用,需配置请求地址(textBody)、请求体(text)及回调 接收(exexute) 

- 请求体支持两种传参,json格式和对象{key:value}格式 

- url 支持http、https全路径和/xxx/xxx.do映射路径 

具体实现参考entry/main/ets/pages/demopage/uidemo/HttpDemoPage.ets 

#### **(1)json格式** 

```
HttpClient
      .textBody(url) // 请求地址
      .text(JSON.stringify(Params)) // 请求体,此处为json格式传参(text)
      .execute((code: number, result: string) => {  // 回调,此处可获取接口的返回值,进行下一步操作
Logger.info('code:'+code+'result:'+result)
})
```

#### **(2)对象格式** 

```
HttpClient
      .paramsBody(url) // 请求地址
      .param(key, value) // 请求体,此处为对象{key:value}格式传参(param)
      .execute((code: number, result: string) => {  // 回调,此处可获取接口的返回值,进行下一步操作
Logger.info('code:'+code+'result:'+result)
})
```

### **1、自定义报文加解密** 

- 增加报文加密适配器,以key,value的方式传入加密算法和实现接口类,key的名字与后管配置算法对应 MDHttp.addCryptoAdapter('SM4', new SM4CryptoAdapter3_5()); 

- 实现CryptoAdapter接口类,加解密算法 

```
export interfaceCryptoAdapter {
setCryptoKey: (cryptoKey: string) =>void;
//加密方法
encrypt: (data: string) =>Promise<string>;
//解密方法
decrypt: (encryptData: string) =>Promise<string>;
  }
```

### **1、自定义SSL通道** 

- 默认是国际通讯,如果使用国密或者其他加密算法,需要手动配置。以国密为例 增加http拦截器MDHttp.addInterceptor(new GMInterceptor()) 

实现Interceptor拦截器.参考:entry/main/ets/pages/utils/GMInterceptor.ets 

- 实现Http请求。参考:entry/main/ets/pages/utils/GMHttp.ets 

```
//应用层调用方法
GMHttp() {
leturl="/gmdemo/mgw.htm"
letheaders: Record<string, string>= {
"Content-Type": "application/json",
"AppId": "5D62B01021839",
  }
letparms: Array<object>= [newObject({
"_requestBody": newObject({ "_ChannelCode": "EMBS" })
  })]
MDHttp
  .textPost(url)//使用非完整URL,SDK内部拦截器会补全URL
  .json(JSON.stringify(parms))
  .addMultiHeader(headers)
  .asString((code: number, result: string) => {
MDLogger.info("HttpDemoPage", 'code:'+code+'result:'+result)
      })
  }
```

# **使用DevEco Studio签名打包** 

## **一、应用/服务签名** 

DevEco Studio为开发者提供了 **自动签名** 和 **手动签名** 两种方式,自动签名仅调试阶段使用,打包发布app请使用手动签 名。 

### **1、自动签名** 

#### 1)连接真机设备 

在Phone中打开“开发者模式”,打开 **“USB调试”** 开关。 

2)进入File->Project Structure...->Project->Signing Configs界面,勾选“Automatically generate signature”(如果是 API 8和9工程,需同时勾选“SupportHarmonyOS”),如果未登录,请先单击 **Sign In** 进行登录,然后点击Apply和OK 按钮,完成自动签名。 

### **2、手动签名** 

HarmonyOS应用/服务通过数字证书(.cer文件)和Profile文件(.p7b文件)来保证应用/服务的完整性。在申请数 字证书和Profile文件前,首先需要通过DevEco Studio或命令行工具来生成密钥(存储在格式为.p12的密钥库文件中) 和证书请求文件(.csr文件)。然后,申请调试数字证书和调试Profile文件。最后,将密钥(.p12)文件、数字证书 (.cer)文件和Profile(.p7b)文件配置到工程中。 

#### **1)生成密钥和证书请求文件** 

点击Build > Generate Key and CSR。 

- 在 **Key Store File** 中,可以单击 **Choose Existing** 选择已有的密钥库文件(存储有密钥的.p12文件);如果没有密 钥库文件,单击 **New** 进行创建。 

**Key Store File** :设置密钥库文件存储路径,并填写p12文件名。如:D:\key\myApplocation_debug.p12 **Password** :设置密钥库密码,必须由大写字母、小写字母、数字和特殊符号中的两种以上字符的组合,长 度至少为8位。请记住该密码,后续签名配置需要使用。 **Confirm Password** :再次输入密钥库密码。 

**Alias:** 密钥的别名信息,用于标识密钥名称。请记住该别名,后续签名配置需要使用。 

- **Password** :密钥对应的密码,与密钥库密码保持一致,无需手动输入。 

- **Validity** :证书有效期,建议设置为25年及以上,覆盖应用/服务的完整生命周期。 

**Certificate** :输入证书基本信息,如组织、城市或地区、国家码等。 

点击Next,,设置CSR文件存储路径和CSR文件名 

单击 **OK** ,创建CSR文件成功,可以在存储路径下获取生成的密钥库文件(.p12)和证书请求文件(.csr) 

#### **2)申请调试证书和调试Profile文件** 

通过生成的证书请求文件,向AppGallery Connect申请调试证书和Profile文件,操作如下: 

- 创建HarmonyOS应用/服务:在AppGallery Connect项目中,创建一个HarmonyOS应用/服务,用于调试证书和 Profile文件申请,具体请参考创建HarmonyOS应用。 

- 申请调试证书和Profile文件:在AppGallery Connect中申请、下载调试证书和Profile文件,具体请参考申请调试 证书和Profile文件。 

#### **3)手动配置签名信息** 

在 **File > Project Structure >Project > Signing Configs** 窗口中,去勾选“Automatically generate signature”(API 8 和9工程请勾选“support HarmonyOS”),然后配置工程的签名信息。 

- **Store File** :选择密钥库文件,文件后缀为.p12,该文件为 **生成密钥和证书请求文件** 中生成的.p12文件。 

- **Store Password** :输入密钥库密码,该密码与 **生成密钥和证书请求文件** 中填写的密钥库密码保持一致。 **Key Alias** :输入密钥的别名信息,与 **生成密钥和证书请求文件** 中填写的别名保持一致。 

- **Key Password** :输入密钥的密码,与 **生成密钥和证书请求文件** 中填写的 **Store Password** 保持一致。 **Sign Alg** :签名算法,固定为SHA256withECDSA。 

- **Profile File** :选择 **申请调试证书和调试Profile文件** 中生成的Profile文件,文件后缀为.p7b。 

- **Certpath File** :选择 **申请调试证书和调试Profile文件** 中生成的数字证书文件,文件后缀为.cer。 

## **二、编译构建.app文件** 

打包APP时,DevEco Studio会将工程目录下的所有HAP模块打包到APP中,因此,如果工程目录中存在不需要打包到 APP的HAP模块,请手动删除后再进行编译构建生成APP。 

1. 单击 **Build > Build Hap(s)/APP(s) > Build APP(s)** ,等待编译构建完成已签名的APP。 

2. 编译构建完成后,可以在工程目录 **build > outputs > app > release** 下,获取带签名的APP 

# **常见问题** 

## **1.如何使用Web场景的进度条功能** 

在后管中的web场景下配置以下场景参数即可(仅对已配置的web场景生效) 

|**key**|**value**|**desc**|
|---|---|---|
|x-progressBar|yes|进度条开关,yes:显示进度条,no:不显示进度条|
|x-progressBarHeight|4|进度条高度,默认4像素|
|x-progressBarBgColor|#000000|进度条底色,例如:#000000|
|x-progressBarPgColor|#F3F3F3|进度条已加载部分颜色,例如:#F3F3F3|

## **2.后管配置** 

启动链设置为导航栏(page_launcher),并在导航栏(page_launcher)场景上设置以下场景参数: 

|**key**|**value**|**desc**|
|---|---|---|
|x-splash|yes|闪屏开关|
|x-splashSeconds|3|倒计时秒数,例如:3|
|x-splashImgUrl|../weex/imgs/splash.png|闪屏图片路径,例如:../weex/imgs/splash.png|
|x-splashStageUrl|http://www.baidu.com|闪屏图片点击事件跳转的外链url,例如: http://www.b aidu.com|
|x- placeholderImageResourceName|splash|从drawable目录下取的闪屏图片作为 placeholderImage使用,只需要配置闪屏图片名即可, 不需要.png后缀名 例如:splash|

|**key**|**value**|**desc**|
|---|---|---|
|x-fullscreen|yes|全屏开关|
|x-noAnimation|yes|关闭转场动画(默认为No)|

## **3.获取json文件** 

```
// 请求
Engine.resourceApi(url)
// 解密
Engine.base64Decode(base64Data)
```

#### **参数:** 

url - 请求地址 

base64Data - base64Data返回的加密数据 

#### **结果:** 

返回的base64加密数据,经Engine.base64Decode()方法解密为JSON格式字符 

#### **示例:** 

```
Engine.resourceApi(url).then((themebase64Data: string) => {
lettheme: string=Engine.base64Decode(themebase64Data);
letdataObg: Array<object>=JSON.parse(theme);
    }).catch((error: BusinessError) => {
MDLogger.error("getAppTheme", `getMDResource failed, error code: ${error.code},
message: ${error.message}.`);
});
```
