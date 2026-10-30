# 北京智游网安科技有限公司 

北京智游网安科技有限公司 

爱加密移动应用安全键盘 SDK 

集成手册(鸿蒙) 

V1.3.0 

文档密级:完全公开 

# ■ 版权声明 

本文档中出现的文字叙述、文档格式、插图、照片、方法、过程等内 容,除另有特别注明,版权均属智游网安所有,受到有关产权及版权 法保护。任何个人、机构未经智游网安的书面授权许可,不得以任何 方式复制或引用本文的任何片断。 

# ■ 免责条款 

本文档所含内容仅用于为平台最终用户提供信息,如内容有更改或撤 回,恕不另行通知。本公司已尽最大努力保证资料的准确可靠,但不 提供任何形式的担保。 

# 目 录 

0 

1 文档定义 1 

1.1 编写目的 1 

1.2 适用范围 1 

1.3 术语与缩略语 1 

1.4 运行环境 1 

2 集成步骤 2 

2.1 使用 HAR 导入 SDK 2 

2.2 编写代码 3 

2.2.1 定义输入框 3 

2.2.2 定义键盘组件 3 

2.2.3 设置授权码 3 

2.2.4 设置键盘数据 4 

3 接口说明 4 

3.1 授权字符串接口 4 

3.1.1 引入授权类 4 3.1.2 接口 4 

3.1.3 参数说明 4 

3.1.4 返回值 4 

3.1.5 建议 5 

3.2 获取键盘 bin 文件 5 

3.2.1 引入授权类 5 

3.2.2 接口 5 

3.2.3 参数说明 6 

3.2.4 返回值 6 

3.3 键盘配置 6 

3.3.1 引入键盘组件 6 

3.3.2 接口 6 

3.3.3 参数说明 6 

3.3.4 参数说明 8 

3.4 获取文本 9 

3.4.1 引入加密类 9 

3.4.2 接口 9 

3.4.3 参数说明 9 

3.4.4 返回值 9 

3.5 切换键盘页 9 

3.5.1 接口 9 

3.5.2 参数说明 10 

3.6 填充算法 10 

3.6.1 接口 10 

3.6.2 参数说明 10 

3.6.3 标识 1 算法 10 

3.6.4 标识 2 算法 11 

3.6.5 标识 3 算法 12 

3.7 显示键盘 13 

3.8 隐藏键盘 13 

3.9 设置键位随机 13 

3.9.1 接口 13 

3.9.2 参数说明 14 

3.10 设置输入框最大长度 14 

3.10.1 接口 14 

3.10.2 参数说明 14 

3.11 键盘事件 14 

3.11.1 接口 14 

3.11.2 参数说明 15 

3.12 获取版本号 15 

3.12.1 接口 15 

3.12.2 返回值 15 

3.13 设置键盘高度 16 

3.13.1 接口 16 

3.13.2 返回值 16 

3.14 获取当前键盘高度 16 

3.14.1 接口 16 

3.14.2 返回值 16 

3.15 设置按下背景色提示 16 

3.15.1 接口 16 

3.15.2 参数说明 16 

3.16 设置放大镜预览效果 17 

3.16.1 接口 17 

3.16.2 参数说明 17 

3.17 设置放大镜样式 17 

3.17.1 接口 17 

3.17.2 参数说明 17 

3.18 设置是否加密 18 

3.18.1 接口 18 

3.18.2 参数说明 18 

3.19 防截屏设置 18 

3.19.1 接口 18 

3.19.2 参数说明 18 

3.20 按键震动设置 18 

3.20.1 接口 19 

3.20.2 参数说明 19 

3.21 设置键盘明文显示 19 

3.21.1 接口 19 

3.21.2 参数说明 19 

3.22 动态更新秘钥 19 

3.22.1 接口 19 

3.22.2 参数说明 19 

3.23 设置键盘预制值 20 

3.23.1 接口 20 

3.23.2 参数说明 20 

3.24 注意 20 

4 借助 Webview 让网页和原生键盘交互 21 

4.1 服务端的集成与设置 21 

4.1.1 集成步骤 21 

4.2 客户端的配置 22 

4.2.1 集成步骤 22 

4.2.2 功能配置 23 

5 个性化设置 23 

5.1 更换图标 23 

5.2 修改键盘按键文本 25 

5.3 按下效果预览放大镜样式 26 

6 键盘界面 26 

6.1 字母键盘基础界面 26 

6.2 数字键盘基础界面 27 

6.3 特殊字母基础界面 27 

7 密码安全校验策略 28 

7.1 密码策略相关 API 28 

# 7.1.1 判断密码中是否包含敏感信息 28 

# 7.1.2 获取输入文本对应策略类型 29 

7.1.3 实时监听输入文本安全强度策略类型 29 

7.1.4 设置密码最小长度 29 

7.1.5 新增密码校验策略类型 30 

7.1.6 删除密码校验策略类型 30 

7.1.7 获取所有密码校验策略类型 31 

7.2 默认策略类型相关常量 31 

7.3 自定义校验策略说明 34 

7.3.1 校验策略优先级与注意事项 34 

7.3.2 自定义策略的正则表达式说明 34 

8 公司介绍 35 

文档定义 

# 编写目的 

为了用户更好的使用爱加密移动应用安全键盘 SDK (鸿蒙版)的相关 功能,特编写该文档。 

# 适用范围 

本文档适用于使用爱加密移动应用安全键盘 SDK (鸿蒙版)的客户公 司内部开发人员、测试人员,爱加密安全技术人员、测试人员、售后 实施人员。 

# 术语与缩略语 

说明:本部分主要是对本文档所出现的重要缩略语进行解释 

编写、术语 

解释 

SDK 

安全键盘 SDK (鸿蒙版) 

运行环境 

SDK 编译环境: DevEco Studio 4.0 Release 

SDK 运行环境:鸿蒙 API 11 以上版本系统 

集成步骤 

使用 HAR 导入 SDK 

将 har 文件复制到项目 libs 目录。 

在需要使用 sdk 文件模块的 oh-package.json5 文件中加入如下配置。 

"dependencies": { 

"@ohos/ohosKeyboardLib": "file:../libs/ohosKeyboardLib.har" 

} 

# 安装依赖包 

DevEco 命令行运行 ohpm install 安装依赖包 

关于鸿蒙引用静态共享包可以参考链接 :https:// developer.harmonyos.com/cn/docs/documentation/doc-guides-V3/ creating_har_api9-0000001518082393-V3 

编写代码 

# 模块导入 

# 在工程中需要使用键盘的页面导入模块 

import {KeyLayout,IJMKeyType,ijmKeyboardController} from "@ohos/ohosKeyboardLib" 

# 定义键盘输入框 

# 在工程中需要使用安全键盘的地方,使用系统输入框的 customKeyboard 事件调用安全键盘组件 

@State inputValue: string=‘’ 

@State placeholder:string=‘’ 

@State isPassword:boolean = false 

@State inputMaxLength:number = 16 

@State curKeyboardType:number = 0 

textInputController: TextInputController = new TextInputController() 

TextInput({ placeholder:this.placeholder, text: this.inputValue, controller: this.textInputController }) .type(this.isPassword? InputType.Normal:InputType.Password) .selectionMenuHidden(true) .onEditChange(() => { // 设置最大输 入长度 this.setInputMaxLength(this.inputMaxLength) // 设置键盘页 this.setcurKeyboardType(this.curKeyboardType) }) .showPasswordIcon(false) // 绑定爱加密安全键盘 

.customKeyboard(this.IjmKeyboardBuilder(this.textInputController)) .onChange(() => { 

this.textInputController.caretPosition(ijmKeyboardController.cursorIndex) }) 

加载键盘组件 

interface ijmKeyProp{ 

type:IJMKeyType 

value?:Length | Array<Length> | Array<number> 

} 

@State inputContent:Array<number|string>=[] 

# // 键盘回调事件 

onKeyMethodEvent(item: ijmKeyProp): void { 

... ... 

} 

// 自定义键盘组件 @Builder IjmKeyboardBuilder(controller:TextInputController) { KeyLayout({ controller: controller, onKeyMethodEvent: (item: ijmKeyProp) => this.onKeyMethodEvent(item), keyBoardBindVal:this.inputContent, }) } 

# 设置授权码 

# 方式 1 在 entryability 中初始化授权和获取键盘配置文件 

```arkts
import AbilityStage from '@ohos.app.ability.AbilityStage'; import {ijmKeyboardController} from "@ohos/ohosKeyboardLib" export default class App extends AbilityStage { onCreate() { const const binFileName:string="appsafekb.bin" 
```

=> { console.info("lic result " + AppLicenseKeyResult); if (AppLicenseKeyResult.getStatus() == 1) { ijmKeyboardController.getKeyBoardBin(binFileName,this.context) 

} }) } } 

# 方式 2 在 UIAbility 中初始化授权和获取键盘配置文件 

aboutToAppear() { 

=> { if (AppLicenseKeyResult.getStatus() == 1) { ijmKeyboardController.getKeyBoardBin(this.binFileName) } }) 

} 

全局授权码必须在键盘对象未被初始化时设置,因此推荐在 aboutToAppear 里面设置。 

注意:授权码需要改成自己应用对应包名所对应的授权码,否则无法 使用安全键盘。 

接口说明 

授权字符串接口 

引入授权类 

```arkts
import { ijmKeyboardController} from @ohos/ohosKeyboardLib'; 接口 
```

static oauthIjmKeyBoard(keyboardAuthCode: string): Promise; 

参数说明 

参数名称 

类型 

描述 

# 可选 / 必选 

keyboardAuthCode 

string 

授权码,请联系爱加密客服电话 4000-618-110 获取授权码。 必选 

返回值 

Json 字符串 {"statusCode":1,"expiredDate":"0","describe":"success"} 获取授权状态返回码 

JSON.parse(res).statusCode 

# 获取状态描述 

JSON.parse(res).describe 

# 获取到期时间 

JSON.parse(res).expiredDate 

# 授权状态码说明: 

状态码 

描述 

0 

授权码错误 

1 

授权成功 

-1 

# 授权码错误或者格式错误 

-2 

# 授权码或者格式错误 

-3 

# 授权到期 

-4 

包名验证失败 

-5 

签名验证失败 

-6 

napi 获取参数失败 

# 建议 

授权接口放在应用入口 onCreate 调用即可。注意:在调用加解密方法 之前要先设置从爱加密获取的授权串 

获取键盘 bin 文件 

引入授权类 

```arkts
import { ijmKeyboardController} from @ohos/ohosKeyboardLib'; 
```

接口 

static getKeyBoardBin(binFileName: string): Promise<string>; 

参数说明 

参数名称 

类型 

描述 

可选 / 必选 

binFileName 

string 

文件名称(默认 resources/rawfile 文件夹下) 

必选 

# 返回值 

参考鸿蒙系统 resourceManager.getRawFileContent() 方法返回值 键盘配置 

引入键盘组件 

import {KeyLayout} from "@ohos/ohosKeyboardLib" 

# 接口 

static KeyLayout({ 

controller: TextInputController , 

onKeyMethodEvent: (item: ijmKeyProp) => { 

this.onKeyMethodEvent(item) 

} , 

inputKeyConfig:this.keyConfig 

} 

参数说明 

参数名称 

类型 

描述 

可选 / 必选 

controller 

TextInputController TextInput 组件的控制器。 

必选 

onKeyMethodEvent 

onKeyMethodEvent 

键盘按键回调事件 必选 

inputKeyConfig 

keyInitConfig 

键盘配置信息 必选 

TextInputController 说明 

TextInput 组件的控制器。 

参考鸿蒙官方文档: https://developer.huawei.com/consumer/cn/ doc/harmonyos-references-V3/ts-basic-componentstextinput-0000001333321201-V3#ZHCN_TOPIC_0000001333321201__textinputcontroller8 

onKeyMethodEvent 说明 

# 安全键盘 SDK 键盘回调事件(参考键盘事件) 

keyInitConfig 说明 

参数名称 

类型 

描述 

pub_key string 

公钥 

is_random 

boolean 

是否随机 

true 每次随机生成密文 

false 每次生成一样密文 

random_seed_str 

string 

需要 is_random=true, 

传入随机数的字符串 ( 数字和字母的组合 ) ,保证长度为 32 位,否则系 统使用自己的随机字符串 

fillAlgo 

number 

算法类型 

取值 1 、 2 、 3 。 

fillAlgo 定制填充算法(算法有三种分别 1/2/3 ),具体算法填充规则 参见 3.5.1 接口 

ijmKeyboardController.setcurKeyboardType(num:number) 

参数说明 参数名称 

类型 

描述 

num 

number 

键盘的 index 默认 0 第一页 

填充算法。 

isHasID 

boolean 

密文前缀 

true 开启密文前缀 false 关闭密文前缀 

keyboardAuthCode 

string 授权码 

key_random 

boolean 

# 键盘键位随机 

true 开启键位随机 false 关闭键位随机 

maxInputLength number 输入长度限制, 0 不限制 mContent Array<number> 输入框绑定输入值 curKeyboardType IJMKeyboardType 键盘类型 

keyLayoutJSON new Object() 键盘数据文件 

IJMKeyboardType 说明 

来自配置文件中所配置的页面数组索引,传入需要索引 ID , 索引计数从 0 开始,传递 0 那么表示切换到键盘页 0 

名称 描述 

LETTER 

# 表示切换到键盘页 0( 默认字母键盘 ) 

# NUMERIC 

表示切换到键盘页 1( 默认数字键盘 ) 

# SPECIAL 

表示切换到键盘页 2( 默认特殊字符键盘 ) 

# 获取文本 

引入加密类 

Import {ijmKeyboardController} from "@ohos/ohosKeyboardLib" 接口 

static keyboardEncrypt(): Promise<string>; 

参数说明 

安全键盘激活时会与键盘输入框双向绑定,所以无需传入参数 返回值 

参数名称 

类型 

描述 

可选 / 必选 

callback 

(res:string) => res 

回调函数 

返回加密之后的密文 

必选 

# 切换键盘页 

通过键盘配置接口传入参数 curKeyboardType 切换键盘页 

{ 

... 

curKeyboardType: IJMKeyboardType.LETTER , 

... 

} 

接口 

ijmKeyboardController.setcurKeyboardType(num:number) 参数说明 参数名称 类型 描述 

num 

number 键盘的 index 默认 0 第一页 填充算法 

通过键盘配置接口传入参数 fillAlgo 变更填充算法 

{ 

... 

fillAlgo: 1 , 

... 

} 

# 接口 

ijmKeyboardController.setFillAlgo(num:number) 

参数说明 参数名称 

类型 描述 

num 

number 

算法标识 

标识 1 算法 

<1>pin = 123456 在开头补进长度 

<2>pin1 = 06123456 转为十六进制 

<3>pin2 = 3036313233343536 后面补 F 将长度补到 64 或 64 的倍数 

<4>pin3 = 

3036313233343536FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF 将十六进制转成 byte 

<5>pin4 = 06123456ÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿ 加密 

<6>pin5 = 

# 调用解密函数解密: 

<7>pin6 = 06123456ÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿ 转换成十六进 制 

<8>pin7 = 

3036313233343536FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF 去除补位 

<9>pin8 = 3036313233343536 将十六进制转成 byte 

<10>pin9 = 06123456 获取长度 06 ,提取明文 

<11>pin10 = 123456 

# 标识 2 算法 

<1>pin = huangjian 随机填充六位大小写字母 

<2>pin1 = WpCgJzhuangjian 加密 

<3>pin2 = 

在加密的密文前添加六个随机字符,得到密文 

<4>pin3 = 

# 调用解密函数解密: 

<5>pin3 = 

去除前六个随机字符 

<6>pin4 = 

<7>pin5 = WpCgJzhuangjian 去除前六个字符得到明文 

<8>pin6 = huangjian 

# 标识 3 算法 

<1>pin = 123456 在开头补进长度 

<2>pin1 = 06123456 转为十六进制 

<3>pin2 = 3036313233343536 后面补 F 将长度补到 64 或 64 的倍数 

<4>pin3 = 

将十六进制转成 byte 

- <5>pin4 = 06123456ÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿ 加密 

<6>pin5 = 

# 调用解密函数解密: 

<7>pin6 = 06123456ÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿÿ 转换成十六进 制 

<8>pin7 = 去除补位 

<9>pin8 = 3036313233343536 将十六进制转成 byte 

<10>pin9 = 06123456 获取长度 06 ,提取明文 

<11>pin10 = 123456 

# 显示键盘 

# 安全键盘输入框激活光标即可调用按键盘 

# 隐藏键盘 

Controller = new TextInputController() 

Controller.stopEditing() 

# 设置键位随机 

方式 1 :初始化键盘时传入 

方式 2 :采用接口来动态更新 

{ 

... 

key_random: true , 

... 

} 

# 接口 

jmKeyboardController.setKeyRandom(status:boolean) 参数说明 参数名称 类型 描述 

status 

Boolean 

设置键盘键位是否随机展示 

设置输入框最大长度 

方式 1 :初始化键盘时传入 

方式 2 :采用接口来动态更新 

{ 

... 

maxInputLength: 5 , 

... 

} 

# 接口 

ijmKeyboardController.setInputMaxLength(num:number) 

参数说明 参数名称 

类型 

描述 

num 

Number 

设置输入框对应键盘最大输入长度 键盘事件 

接口 

static onKeyMethodEvent(ijmKeyProp: ijmKeyProp); 

参数说明 参数名称 

类型 

描述 

# 可选 / 必选 

type 

IJMKeyType 

键盘操作枚举 

必选 

value 

Length | Array<Length> 输入返回 可选 

IJMKeyType 说明 

名称 描述 

INPUT 输入操作 DELETE 删除操作 

CONFIRM 

完成 / 确定操作 

HIDE 

隐藏键盘 

CLEAR 

清空操作 

# CAPSLOCK 

切换大小写操作 

SWITCH 

切换 / 更多操作 

获取版本号 

返回类型为 String 的版本号。 

接口 

ijmKeyboardController.getSdkVersion 

返回值 返回类型为 String 的版本号。 设置键盘高度 

接口 

ijmKeyboardController.setKeyboardHeight(size:higt) 返回值 参数名称 类型 描述 

higt 

number 

设置的键盘高度 (px2vp 使用 px 则转换成对应的 vp) 获取当前键盘高度 

# 接口 

ijmKeyboardController.getKeyboardHeight 

返回值 

返回当前键盘页的逻辑分辨率高度,单位( px ),类型 number 。 设置按下背景色提示 

设置按键按下时是否有背景色。 

# 接口 

ijmKeyboardController.setKeyBgColor(value:Array<boolean>) 参数说明 

参数名称 

类型 

描述 

value 

Array<boolean> 

根据下标指定键盘页,传递 true 表示开启此功能,传递 false 表示关闭 此功能。 设置放大镜预览效果 

接口 

ijmKeyboardController.setPreviewFocus(status) 

参数说明 

参数名称 

类型 

# 描述 

status 

Boolean 

是否开启按下按钮显示放大镜 设置放大镜样式 

接口 

ijmKeyboardController.setPreviewFocusClass(options) 

参数说明 参数名称 类型 描述 

options 

{ 

fontSize?:number | string | Resource fontWeight?:number | FontWeight | string fontColor?:ResourceColor width?:Length height?:Length offsetY?:Length radius?:Dimension enableArrow?:boolean bgColor?:ResourceColor shadow?: ShadowOptions | ShadowStyle; 

} 

自定义放大镜样式 

设置是否加密 

接口 

ijmKeyboardController.setEncInput(status:boolean) 

# 参数说明 

参数名称 

类型 描述 

status 

boolean 

true :表示加密。 false :表示不加密 默认值为 true 。 

# 防截屏设置 

此功能需要防截屏录屏的权限,所以在 har 里面默认配置了此权限 ohos.permission.PRIVACY_WINDOW 接口 

ijmKeyboardController.setPrivacyWindow(value) 

参数说明 

参数名称 

类型 

描述 

value 

boolean 

当前使用安全键盘的页面禁止截屏。 

按键震动设置 

此功能需要调用手机震动的权限,所以在 har 里面默认配置了此权限 

ohos.permission.VIBRATE 

接口 

ijmKeyboardController.setVibration(status) 

参数说明 

参数名称 

类型 

描述 

status 

boolean 

当前使用安全键盘的页面是否开启振动(默认不开启)。 设置键盘明文显示 

接口 

ijmKeyboardController.setPlainKeyboard(isShowPlaintext) 

参数说明 

参数名称 

类型 

描述 

isShowPlaintext 

boolean 

当前安全键盘控件明文显示,默认非明文设置(无需设置) 动态更新秘钥 

# 接口 

ijmKeyboardController.setEncPubkey(pub_key:string) 

参数说明 

参数名称 

类型 

描述 

pub_key 

String 

对应加密密钥对的公钥 

# 设置键盘预制值 

接口 

ijmKeyboardController. setDefaultText(defaultVal) 

参数说明 参数名称 类型 描述 

defaultVal 

String 

预制的字符串 

注意 

授权码:用户需提供应用包名给售后生成授权码。 

# 项目开启混淆配置 需配置混淆保留属性名 

-keep-property-name np0 

借助 Webview 让网页和原生键盘交互 

目前仅支持鸿蒙原生 webview 对象构建的浏览器和键盘进行绑定 , 即被 webview 框架展示的网页内输入框能够启用在安全键盘进行输入,建 议新手先运行 demo 感受效果 , 然后根据 demo 的模板进行配置。 

服务端的集成与设置 

集成步骤 

# 准备文件 

拷贝 /entry/src/main/resources/rawfile 目录下 resource 文件夹 引入文件 

在 html 的 <head></head> 节点插入如下代码 

<link rel="stylesheet" type="text/css" ref="./resource/css/ demo.css"> 

<script src="./resource/js/demo.js"></script> 

# 定义输入框 

在 html 的 <body></body> 节点定义 

 

 

 爱加密安全键盘  

 

 

 

 

# 注意 : 

class 样式名称不建议更改 , 否则对应的 js/css 文件也需要更改。 

客户端的配置 

集成步骤 

注册 JS 交互桥接 

描述与代码 

在 webview 所在 activity 的 onControllerAttached 中拿到 webview, 然后 绑定,具体可以参考鸿蒙官方文档 

Web({ src: '', controller: this.webviewController }) 

.javaScriptAccess(true) 

.onRequestSelected(() => { 

# // 授权键盘 

this.KeyBoardUtil.oauthKeyBorad() 

}) 

.onControllerAttached(() => { 

// 挂载 H5 页面 this.webviewController.loadUrl($rawfile("keyboard_h5.html")); 

// 注入键盘相关事件 

let keyBoardFun:Array<string>=[] 

}) 

接口 

参数说明 参数名称 类型 描述 

KeyBoardUtil new KeyBoardUtil() 必须传递键盘的 activity IjmKeyBoard 

string Activity 中所设置的名称 keyBoardFun Array 暴露的方法集合 功能配置 设置键盘授权码等信息 接口 

ijmKeyboardController.oauthIjmKeyBoard(keyboardAuthCode) 参数说明 参数名称 

类型 

描述 

keyboardAuthCode 

String 

授权码 code 

个性化设置 

更换图标 

替换的方式和原理和正常开发一样 , 如主项目有同样的资源名称则可以 实现资源名称的替换。 

修改方式 

打开 resources 文件夹找到 base/media , bcs_ 开头的为键盘所使用的图 片,根据需要自行替换即可 

修改键盘按键文本 

方法 1 

修改的方式和原理和正常开发一样( resources 文件夹找到 base/ element/string.json ) , 如主项目有同样的资源名称则可以实现资源名 称的替换 , 字符串默认实现了中文( resources 文件夹下 base/zh_CN ) 和英文语言( resources 文件夹下 base/en_US )的适配 

方法 2 

可以通过 bin 文件( resources/rawfile/appsafekb.bin )修改对应的文 本 按下效果预览放大镜样式 

键盘界面 

字母键盘基础界面 

数字键盘基础界面 

特殊字母基础界面 

密码安全校验策略 

密码策略相关 API 

判断密码中是否包含敏感信息 

接口 

功能 

解释用于检测密码是否包含了生日年月、部分或完整身份证号码 、手 机号码等,以防止用户输入弱类型密码。 

参数说明 

参数名称 

类型 

描述 

str 

String 

敏感字符串数组,可以传递 1 个或者多个要检测的敏感信息字符串 , 多 个敏感词以英文 ”,” 分割。 返回值 

true :代表当前输入的信息包含敏感信息字符串,或者当前输入的信 息是敏感信息字符串的部分内容。 

false :代表当前输入的信息不包含敏感信息字符串。 

# 获取输入文本对应策略类型 

# 接口 

# 功能 

调用此方法将获取当前键盘密码安全强度策略类型, 内置的具体类型 有输入长度过短、纯数字、纯字母、纯符号、整体字符串连续顺序、 整体字符串重复、两种组合 、三种组合 、以及三种以上组合的类 型。 

参数说明 

具体 int 值参见默认密码策略类型相关常量。 

实时监听输入文本安全强度策略类型 

# 功能 

每次用户输入一个字符或者删除一个字符时触发 , 不设置监听则不会实 时检测输入的安全强度类型。在键盘输入删除事件中调用获取文本对 应策略类型。 

返回值 

获取当前已添加的策略类型 , 返回的是一个 Map 集合 

设置密码最小长度 

接口 

ijmKeyboardController.setNKeyboardMinInputLength(number) 

功能 

用于安全强度类型检查中的最小长度检查。 

参数说明 

参数名称 

# 类型 

描述 

number 

int 

# 新增密码校验策略类型 

接口 

ijmKeyboardController.addValidationPolicy(ruleKey,ruleRegx) 

功能 

加入一条密码校验策略,这个策略将会在实时监听输入的字符串安全 强度类型回调和获取输入的字符串安全类型方法中体现。 参数说明 参数名称 

类型 

描述 

ruleKey 

number 

为唯一值 , 具体参考 自定义校验策略说明校验机制部分 

ruleRegx 

String 

正则表达式 , 具体参考 自定义校验策略说明自定义策略正则表达式部 分。 

删除密码校验策略类型 

# 接口 

ijmKeyboardController.removeValidationPolicy(key:CharactersType) 

功能 

删除已添加的密码校验策略类型。 

参数说明 

参数名称 

类型 

描述 

key 

int 

可以传递默认密码策略类型常量值,也可以传递自己曾经添加的。 获取所有密码校验策略类型 

接口 

ijmKeyboardController.getAllValidationPolicy(): Promise<Object> 

功能 

获取当前已添加的策略类型。 

返回值 

获取当前已添加的策略类型 , 返回的是一个 Map 集合,因此用户能够通 过 JavaApi 任意增删改查。 

默认策略类型相关常量 

用户判断类型建议使用常量进行判断 , 不应该直接用数值判断,判断强 度范围可以用 if(>=ALL_DIGHTER){ } 这样的常量来实现。 

export enum CharactersType { // 输入长度没有达到要求设置的最小 

长度 ( 默认为 8 位 ) LENGTH_ILLEGAL = 10100, /** * 整体是重复时 满足为此 type 12121212 或者 111111111 */ REPEAT = 10200, /** * 字母连续有规律。 */ SEQUENCE = 10300, /** * 全是数字 */ ALL_DIGHTER = 10400, /** * 全是特殊符号 */ ALL_SPECITALSYMBOL = 10500, /** * 全是大写字母 */ ALL_UPPER_LETTER = 10600, /** * 全是小写字母 */ ALL_LOWER_LETTER = 10700, /** * 数字小写字母 与数字混合或数 字小写与数字混合。 */ MIX_TWO_LETTER_AND_DIGHT = 10800, / ** * 字母大小写 两种 混合 */ MIX_TWO_UPPER_LOWER_LETTER = 10900, /** * 小写 & 特殊 | 大写 & 特殊 | 数字 & 特殊 */ MIX_TWO_OTHER_WITH_SPECIALSYMBOL = 11000, /** * 小写 & 大 写 & 数字 数字与大小写字母 的三种混合混合 */ MIX_THREE_NUMBER_LETTER = 11100, /** * 大写 & 小写 & 特殊 | 大 写 & 特殊 & 数字 | 特殊 & 小写 & 数字 三种混合 */ MIX_THREE_OTHER = 11200, /** * 大写 & 小写 & 数字 & 特殊 最复杂的一种混合 */ MIX_ALL_NUMBER_LETTER_SEPICAL = 11300, } 

自定义校验策略说明 

校验策略优先级与注意事项 

优先级 : 

键盘内部将由 type 值数字大小从最小值往最大值升序遍历 , 键盘内置 的每一个策略 type 值之间差比较大,因此用户能够做到在任何一条内 部的策略之前或者之后执行自己的校验策略。 

举例 : 如定义 10101 值 为 .*? ,也就说在只要长度满足 ( 长度 type:10100 ,因此优先级在长度校验策略之后在重复检测之前 ) 的情 况下输入任何字符就会命中此校验策略。 

注意事项 : 

键盘默认的的 type 值从 10000 开始 

type 必须是唯一值 

当调用或监听获取当前密码强度类型时将按遍历已添加的所有策略集 合,逐个匹配验证 , 如果正则匹配成功将跳出循环返回当前匹配的 type 。 

避免重复插入 , 当用户自定义插入的值已存在则会抛出异常告知已经插 

# 入 , 应该先移除 , 以避免不小心导致覆盖问题。 

键盘内置的 type 值具体对应的值参考 ( 默认密码策略类型相关常 量)。 自定义策略的正则表达式说明 

自定义策略的正则表达式即校验当前密码是否符合校验策略的正则表 达式,如果当前密码匹配某一条正则通过后将不再继续进行匹配 , 直接 返回正则所对应的 type 值。正则表达式支持引用变量,目前只有 3 个 内置变量 , 暂不支持用户自定义变量。 

# 语法 

##{ 变量名 } 或 ##{ 变量名 , 基于当前变量增减值 } 

举例 

##{length} 当前密码字符串长度 

##{max} 当前键盘设置的最大值 

##{min} 当前键盘设置的最小值 

##{length,-2} 当前密码字符串长度 length 减 2 如密码为 1234 那么将被 替换为 2 

##{length,2} length 加 2 

举例 : 

假设设置密码最小长度为 6, 正则表达式为 ^.{##{min},}$ 在检测过程 中将被替换为 ^.{6,}$ ,当输入的内容长度为 6 或 6 以上会命中此校验策 略。 

假设设置密码最小长度为 6, 正则表达式为 ^.{0,##{length,-1}}$ 在检 测过程中将被替换为 ^.{0,5}$ ,当用户输入的长度如果小于 6 将会命中 此校验策略。 

# 公司介绍 

北京智游网安科技有限公司(爱加密)成立于 2013 年,总部位于北 京,研发及运营中心位于深圳,同时在全国各地设立了 12 个分支机 

构,拥有员工 400 多人。 

爱加密( www.ijiami.cn) 是专业的移动信息安全服务提供商,专注于 移动应用安全、大数据、物联网及工业互联网安全,坚持以用户需求 为导向、持续不断的创新,致力于为客户提供全方位、一站式的移动 安全全生命周期解决方案。爱加密的服务宗旨是通过革新性安全方案 和 7x24 小时全天候的专业服务,打造和谐、强大、高度安全的万物互 联生态环境。 

爱加密拥有安全防护、安全检测、安全管理、业务运营、威胁感知、 安全监管、安全服务七大产品体系,贯穿了应用设计评估、安全开发 测试、应用优化、应用安全发布及应用上线运营阶段的整个生命周 期。目前行业用户遍及金融、运营商、政府、电商、能源、教育、游 戏等多个行业。至今共服务企业及开发者用户 50 万 + ,保护移动应用 100 万 + ,监测互联网应用 1500 万 + ,累计覆盖 10 亿移动终端。
