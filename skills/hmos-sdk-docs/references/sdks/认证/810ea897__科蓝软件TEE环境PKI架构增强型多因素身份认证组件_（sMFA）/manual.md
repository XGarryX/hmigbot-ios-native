科蓝鸿蒙 TEE 环境 PKI 架构增强多因素身份认证组件接入文档 

SDK 名称 

科蓝鸿蒙 TEE 环境 PKI 架构增强多因素身份认证组件 (sMFA) 集成配置 

引用 SDK 

在 entry/oh-package.json5 文件中添加依赖 

"dependencies": { 

"mftp_smfa": "file:./libs/smfa.har" 

} 

# 功能介绍 

支持验证设备真实可信性 

支持指纹、人脸认证 

支持指纹手势滑动组件认证 

支持密码键盘认证,支持 sm2 、 rsa 、 aes 、 sm4 加密方式 支持身份证专用键盘、银行卡专用键盘、手机号专用键盘 

模块介绍 

模块 介绍 

SMFAClient 

sMFA 初始化及专用键盘功能、数字资产保险箱等功能 

SMFAFingerClient 

# 指纹认证类 

SMFAFaceClient 

人脸认证类 

SMFAPasswordClient 

密码认证类 

NumberComponent 

数字密码组件 

GestureLockView 

手势密码组件 

API 详解及样例 

SMFAClient 方法说明 

方法 

介绍 

windowStage 

设置 windowStage 对象 , 在 UIAbility 的 onWindowStageCreate 方法中初 始化该方法 

init 

配置初始化交易地址 , 内部进行设备注册流程 

registryCustomEncryption 

注册加减密适配器 , 对外暴露加密解密方法 

registerInitMTC 

注册 MTC 适配器 

# initSMFAKeyBoard 

初始化键盘掩码数据 

setKeyboardVibrator 

配置专用键盘按键是否振动 

startIDCardKeyboard 

调用身份证专用键盘 , 身份证号通过密文返回 startBankCardKeyboard 

调用银行卡专用键盘 , 银行卡通过密文返回 startPhoneNumKeyboard 

调用手机号专用键盘 , 手机号通过密文返回 startDigitalAssets 

拉起数字资产保险箱页面 

uninstallIsStore 

APP 卸载时是否删除 SDK 内存数据 , 默认删除 

getSignData 

数据加签 

SetDeviceId 

设置 SDK 的设备唯一标识 

getDeviceId 

获取 SDK 的设备唯一标识 

removeDeviceId 

移除 SDK 的设备唯一标识 

# onDestroy 

销毁 SDK 

# 使用示例 : 

// 初始化 

SMFAClient.init(this.URL).then((result) => { let data: object = JSON.parse(result) let code: string = data['code'] if code="000000" { 

# // 初始化键盘数据 

SMFAClient.initSMFAKeyBoard().then((result: string) => { let data: object = JSON.parse(result) let code: string = data['code'] if code="000000" { 

# // 初始化成功 

} else { 

# // 初始化失败 

} 

}) 

} 

}).catch((err: BusinessError) => { 

console.log("sMFA", 错误信息 . Code is ${err.code}, message is ${err.message}) 

# }); 

# // 身份证专用键盘 

SMFAClient.startIDCardKeyboard(this.getUIContext(), 

(state: KBState, IDNumber: string, cip: string) => { console.log(" 脱敏数据 :" + IDNumber + "\n 密文 :" + cip) 

# }) 

# // 银行卡专用键盘 

SMFAClient.startBankCardKeyboard(this.getUIContext(), 

(state: KBState, bankCardNum: string, cip: string) => { console.log(" 脱敏数据 :" + bankCardNum + "\n 密文 :" + cip) 

# }) 

// 手机号码专用键盘 

SMFAClient.startPhoneNumKeyboard(this.getUIContext(), 

(state: KBState, phoneNum: string, cip: string) => { console.log(" 脱敏数据 :" + phoneNum + "\n 密文 :" + cip) 

# }) 

SMFAFingerClient 方法说明 

方法 

介绍 

isSupport 

检测当前设备是否支持指纹认证 

initFinger 

# 初始化指纹识别 

isFingerKeyExist 

指纹密钥是否存在 

startFingerVerify 

开始进行指纹认证 

# 使用示例: 

```arkts
let isSupport = SMFAFingerClient.isSupport() if (isSupport) { SMFAFingerClient.isFingerKeyExist().then(async (isExist: boolean)=>{ if (!isExist) { // 初始化 await SMFAFingerClient.initFinger() } SMFAFingerClient.startFingerVerify((data: string) => { let fingerObj: object = JSON.parse(data) let code: string = fingerObj["code"] let message: string = fingerObj["message"] if (code == '000000') { //TODO 待验证 // 验证成功 } else { 
```

// 验证失败 } }) }) } else { console.log(" 不支持指纹识别 ") } 

3 、 SMFAFaceClient 方法说明 

方法 

介绍 

isSupport 

检测当前设备是否支持人脸认证 

initFace 

初始化人脸识别 

isFaceKeyExist 

指纹密钥是否存在 

startFaceVerify 

# 开始进行人脸认证 

# 使用示例: 

```arkts
let isSupport = SMFAFaceClient.isSupport() if (isSupport) { SMFAFaceClient.isFaceKeyExist().then(async (isExist: boolean)=>{ if (!isExist) { await SMFAFaceClient.initFace() } SMFAFaceClient.startFaceVerify((data: string) => { let fingerObj: object = JSON.parse(data) let code: string = fingerObj["code"] let message: string = fingerObj["message"] if (code == '000000') { // 验证成功 } else { 
```

// 验证失败 } }) }) } else { console.log(" 不支持人脸认证 ") } 

4 、 SMFAPasswordClient 方法说明 

方法 

介绍 

setRandomCode 

# 设置键盘数据是否随机显示 , 默认不随机 

setParameter 

设置键盘底层数据 

startVibrator 

设置按键是否振动 

setEncyType 

设置加密数据加密类型 , 默认 sm2 

registerPwdResult 

按键数据回调 , 配合键盘组件使用 

使用示例: 

aboutToAppear(): void { 

SMFAPasswordClient.registerPwdResult((data: string) => { // 密 码输入完成 console.error( 输入密码完成 : ${data}) }) } 

build() { NavDestination() { Column() { NumberComponent({ keyBgColor: "#eeeeee", encryptType: EncryptType.ENCRYPT_AES, isRandom: false, isVibrator: true }) } 

}.title(" 账密认证 ") 

} 

GestureLockView 组件说明 

方法 

介绍 

encryptType 

手势数据加密类型 ,, 默认 sm2 

pressImg 

按压后的图片 , 类型 -Resource 

normalImg 

默认图片 , 类型 -Resource 

lineColor 

连接线的颜色 , 默认 #008CE7 

minLength 

最低连接个数 

mWidth 

组件的宽高长度 , 数据类型 -number 

resetCount 

手势重置 , 通过改变 @prop 状态值来重置 

callBack 

ResultCode: success: 成功 fail: 失败 clearTest: 掩码数据 encryptData: 手势密文 

使用示例: 

@State reset: number = 0 

GestureLockView({ mWidth: 300, lineColor: "#008ce7", minLength: 5, resetCount: this.reset, // 重置 UI 每次值变化时都会清除当前手势滑 块 callBack: async (code: ResultCode, clearTest: string, encryptData: string) => { if (code == ResultCode.success) { // 成功 } this.reset++ } })
