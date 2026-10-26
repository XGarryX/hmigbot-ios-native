# **一** **键认证 HarmonyOS SDK 集成指南** 

## **前言** 

本文是一键认证 HarmonyOS SDK 的集成文档,用于指导一键认证鸿蒙版本 SDK 的集成,读者需具有一定 HarmonyOS ArkTs 编程知识基础。 

本文默认读者已经具有基础的鸿蒙知识,以及项目工程结构如下: 

GtsdkDemo/ 

|- entry/ (项目主模块) |    |- libs/ (第三方库,用户手动创建) |    |- src/ (代码目录) |    |- oh-package.json5(模块级oh-package.json5文件) |- build-profile.json5 |- hvigorfile.ts |- oh-package.json5 (顶层oh-package.json5文件) | ...... 注:其中 “......” 表示省略其他与本教程无关的内容,以下 “......” 表示相同意义,不再重复说明。 ## **准备工作** ### **1.创建应用** 鸿蒙应用的bundlename 鸿蒙应用的fingerprint fingerprint长度为64个字符 ###### //在程序里调用该方法获取当前签名 getSign(): string { let bundleFlags = bundleManager.BundleFlag.GET_BUNDLE_INFO_WITH_SIGNATURE_INFO; let bundleInfo = bundleManager.getBundleInfoForSelfSync(bundleFlags) return bundleInfo.signatureInfo.fingerprint } ##### 应用唯一标识 填入鸿蒙应用的appIdentifier信息。该appIdentifier信息就是在华为AppGallery Connect上获取到的APPID 值,保存后无法修改。 ##### 创建个推应用 在开发者中心提交 APP 包名等信息后即可获取 APPID 等参数,然后等十分钟左右运营商侧报备成功后就可以 正常使用了。点击前往开发者中心创建应用 ### **2.demo体验** HarmonyOS 压缩包附带的 demo 文件夹中是个验的示例工程,使用 DevEco Studio 打开示例工程,成以下配置 步骤进行本地测试: 1. 将包名修改成对应的测试包名;

2. 将签名配置改成您的签名配置; 

3. 将 APPID 换成您的信息(需注意 APPID 和包名/包签名的一致性); 

4. 参照服务端接入文档完成服务端接口的对接, **注意客户端** APPID **与服务端保持一致** 。如未完成该步 

骤则仅能体验APP端功能,不能获取真实手机号。 

### **3. 自动集成** 

1. 打开工程项目,在 entry 模块下的 oh-package.json5 文件添加: 

{ "dependencies": { "@getui/gysdk": "x.x.x"//填写对应版本号,如:"@getui/gysdk": "1.0.9" } } 

2. 一键认证SDK har 为字节码,必须使用 DevEco Studio 5.0.3.800 及以上版本,并在工程级(最外层)buildprofile.json5,配置"useNormalizedOHMUrl": true,如下图: 

{ "app": { "products": [ { "buildOption": { "strictMode": { "useNormalizedOHMUrl": true } } } ] } } 

### **4.本地集成** 

将获取的 GY-HM-XXX.har 文件拖拽到模块中的 libs 文件夹下。 

- 在拖入 .har 到 libs 文件夹后,还要检查 .har 是否被 install ,要在模块的 oh-package.json5 下添加如下代码 

dependencies": { "@getui/gysdk": "file:./libs/GY-HM-XXX.har" } 

### **5.配置依赖及参数** 

- 配置APPID(必选) 和 CHANNEL(非必选) 

项目的module.json5文件中配置appid 

"metadata": [ { "name": "GETUI_APPID", //替换成个推平台申请的appid "value":"APPID" }, { "name": "GT_INSTALL_CHANNEL", "value": "CHANNEL" }] 

module.json5 权限配置: 

sdk内部已配置了以下权限 

"requestPermissions": [ { //允许应用程序联网,用于访问网关和认证服务器 "name": "ohos.permission.INTERNET", }, { //获取网络状态,判断是否数据、wifi等 "name": "ohos.permission.GET_NETWORK_INFO" }, { //允许获取wifi信息 "name": "ohos.permission.GET_WIFI_INFO" }, { //允许应用配置数据网络 "name": "ohos.permission.SET_NETWORK_INFO" }, { //用于创建唯一的gyuid标识 "name": "ohos.permission.APP_TRACKING_CONSENT", "reason": "$string:gy_oaid_tracking" } ] 

##### 工程配置 

请设置 useNormalizedOHMUrl 为true,查看工程级build-profile.json5: 

"products": [ { "name": "default", //换成app报备时的签名 "signingConfig": "xxxxxx", 

"compatibleSdkVersion": "5.0.0(12)", "runtimeOS": "HarmonyOS", "buildOption": { "strictMode": { "useNormalizedOHMUrl": true } } } ] 

## **初始化** 

#### **注意事项** 

为了保证 SDK 服务稳定,开发者需在 App《隐私政策》的 “与授权合作伙伴共享”条款中,将 个推的用户隐私政策 加入其中。在判断用户已经同意隐私政策后、或者弹出确认框用户同意后再初始化 gysdk,注意:此时SDK功能尚 未启用,GYUID暂未生成。详情可查看:个推合规指南 。 

#### **方法描述** 

生成唯一的客户端ID,即GYUID,为了保障一键认证可以正常使用,您务必确保用户同意《隐私政策》之后,调用 初始化 方法。若不调用则无法注册GYUID ,一键认证功能无法正常使用 

public init(config: GyConfig): Promise<GyResponse> 

#### **参数说明** 

##### GyConfig配置包含以下信息 

|**参数**|**类型**|**说明**|
|---|---|---|
|context|Context|上下文|
|debug|boolean|设置是否开启SDK日志打印功能,默认为false|
|preLoginUseCache|boolean|预登录是否支持缓存,默认为true|
|channel|string|设置当前的渠道|

## **一** **键登录** 

### **1.调用逻辑** 

预登录 

ePreLogin 预登录获取带星PN 

登录 

确保预登录是有效时才调用登录接口,通过 isPreLoginResultValid 判断 

- eAccountLogin 拉起授权页,点击登录成功返回token 

关闭授权页 

closeAuthLoginPage 可关闭当前授权页 

### **2.预登录** 

在登录前调用,登录成功后预登录结果就失效了,如果需要再次登录请重新调用 ePreLogin 确保预登录的有效性 

#### **方法描述** 

public ePreLogin(timeout: number): Promise<GyResponse> 

#### **参数说明** 

|**参数**|**类型**|**说明**|
|---|---|---|
|timeout|number|超时时间|

### **3.登录** 

此接口会拉起授权页登录才能获取token,成功获取token即可用于服务端取号 

#### **方法描述** 

public eAccountLogin(timeout: number, config?: GyAuthThemeConfig): Promise<GyResponse> 

#### **参数说明** 

|**参数**|**类型**|**说明**|
|---|---|---|
|timeout|number|超时时间|
|config|GyAuthThemeConfig|移动的授权页样式配置|

### **4.授权页规范** 

**为了确保用户在登录过程中将手机号码信息授权给开发者使用的知情权,一键登录需要开发者提供授权页登录页面 供用户授权确认。开发者必须弹出授权页,明确告知用户当前操作会将用户的本机号码信息传递给应用。** 

授权页示例如下: 

##### **注意:** 

- **_1_ 、页面必要元素有:号码栏** **_(NumberTextview)_ ,品牌露出** **_(SloganTextview)_ ,登录按钮** **_(LoginButton)_ ,隐私确** 

- **认** **_(PrivacyCheckbox)_ ,隐私标题** **_(PrivacyTextview)_ ;** 

- **_2_ 、开发者不得通过任何技术手段,破解授权页,或将上述授权页面的必要元素内容隐藏、覆盖、或者动态变更;** 

- **_3_ 、登录按钮文字描述必须包含** **_“_ 登录** **_”_ 或** **_“_ 注册** **_”_ 等文字,不得诱导用户授权;** 

- **_4_ 、对于接入** **_GYSDK_ 并上线的应用,我方和运营商会对上线的应用授权页面做审查,如果有出现未按要求弹出或设 计授权页面的,将关闭应用的认证取号服务。** 

### **5.关闭授权页** 

SDK不会主动关闭授权页,需要开发者在回调结束后自行实现关闭授权页 

#### **方法描述** 

public closeAuthLoginPage() 

## **本机号码校验** 

### **1.调用逻辑** 

##### 获取号码校验token 

- getVerifyToken 获取校验token(对于双卡手机,则认证是否为当前流量对应的本机号码) 

- 号码校验 

   - verifyPhoneNumber 验证手机号码是否为本机号码 

### **2.获取token** 

获取需要校验的手机号码的token 

#### **方法描述** 

public getVerifyToken(phone: string, timeout: number): Promise<GyResponse> 

#### **参数说明** 

|**参数**|**类型**|**说明**|
|---|---|---|
|phone|string|需进行认证的手机号码|
|timeout|number|超时时间|

### **3.号码校验** 

验证手机号码是否为本机号码 

#### **方法描述** 

public verifyPhoneNumber(token: string, processId: string, phone: string, operatorType: number): Promise<GyResponse> 

#### **参数说明** 

以下参数可以通过 getVerifyToken 返回的 GyResponse 中获取 

|**参数**|**类型**|**说明**|
|---|---|---|
|timeout|number|超时时间|
|processId|string|流水号|
|phone|string|需进行认证的手机号码|
|operatorType|number|运营商类型|
