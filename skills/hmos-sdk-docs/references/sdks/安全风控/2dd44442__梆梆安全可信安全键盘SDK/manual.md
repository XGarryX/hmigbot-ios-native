梆梆安全|BANGCLE 

北京梆梆安全科技有限公司 

# **梆梆安全可信安全键盘SDK** 

# **接口文档** 

(Ver1.1.0)

#### 北京梆梆安全科技有限公司 

## 目录 

|**1 修改历史记录.....................................................................................................3**|
|---|
|**2 文档说明............................................................................................................ 4**|
|**3 安全键盘SDK 功能...........................................................................................4**|
|**4 SDK 集成方法.................................................................................................... 4**|
|4.1DEVECOSTUDIONEXT 集成方案.............................................................................................4|
|4.2 集成授权许可文件.....................................................................................................................5|
|4.3 注意事项.....................................................................................................................................6|
|**5 SDK 使用方式.................................................................................................... 6**|
|5.1 设置键盘全局参数.....................................................................................................................6|
|5.2 引用安全键盘.............................................................................................................................8|
|5.3 初始化.........................................................................................................................................9|
|5.4 修改密码.................................................................................................................................. 10|
|5.5 调用.......................................................................................................................................... 10|
|5.6 设置键盘自动弹出.................................................................................................................. 10|
|5.7 获取加密数据.......................................................................................................................... 11|

4.1 DEVECO STUDIO NEXT 集成方案 .............................................................................................4
4.2 集成授权许可文件 .....................................................................................................................5
4.3 注意事项 .....................................................................................................................................6
5 SDK 使用方式 .................................................................................................... 6
5.1 设置键盘全局参数 .....................................................................................................................6
5.2 引用安全键盘 .............................................................................................................................8
5.3 初始化 .........................................................................................................................................9

## **1 修改历史记录** 

编号 修改日期 内容 备注
1 2024-05-30 鸿蒙键盘initial Bangcle
2 2024-07-05 修订部分章节内容 Bangcle
3 2024-07-22 增加键盘可配置项 Bangcle

## **2 文档说明** 

本文档描述了梆梆出品的可信安全键盘SDK 的功能、集成方法以及使用方式。SDK 功 能请参考本文档第3 部分,集成方法请参考本文档第4 部分,使用方式请参考本文档第5 部分。 

## **3 安全键盘SDK 功能** 

SDK 提供了一个自定义的安全键盘控件。该控件使用严格的加密方式对用户输入的信 息进行安全处理,并提供多种类型的输入字符供用户随意切换。避免了使用HarmonyOS Next 自带输入键盘所带来的安全隐患。 

## **4 SDK 集成方法** 

### **4.1 DevEco Studio NEXT 集成方案** 

- 拷贝压缩包中的【SafeKeyboard.har】文件到当前项目APP 主模块的libs 目录下 

- 修改APP 主模块下的oh-package.json5,添加SDK 依赖, 代码如下: 

"dependencies": { 

"@ohos/SafeKeyboard" : 'file:./libs/SafeKeyboard.har' 

} 

##### 集成完毕后如下图所示,红框内是新添加的部分: 

### **4.2 集成授权许可文件** 

拷贝license 文件bangcle_sdk_safekb_licence 到resources/rawfile 目 

录下 

注: 

1. 没有授权文件,或授权文件无效时,键盘会提示“未授权” 

2. 更新授权文件方法 

通过动态更新hap 包中resources/rawfile 来实现更新licenses 

### **4.3 注意事项** 

- SDK 中包含arm64-v8a 和x86_64 两种CPU 指令集的so 库,请根据项目本身需求进 

行删减,否则可能导致项目其它so 库无法匹配而报错。 

## **5 SDK 使用方式** 

### **5.1 设置键盘全局参数** 

SDK 提供了部分键盘全局参数的设置接口,请在应用初始化代码中做相应设置: 

@state ishide:boolean=true; 

@state has_sound:boolean=true; 

@state has_shock:boolean=true; 

@State title_text: string = " 梆梆安全键盘"; 

@State title_image: Resource = $r("app.media.bangcle_kb_img_dialog_icon"); 

@State title_iscenter: boolean = true; 

@State textlimitlen: number = 6; 

@State title_show: boolean = false; 

##### **参数说明:** 

ishide - [boolean]型,true为隐藏输入内容,false为显示输入内容。 has_sound - [boolean]型,true为有按键音,false为无按键音。 has_shock - [boolean]型,true为有案件震动,false为无按键震动。 title_text - [String]型,定义键盘显示的名称。 

- title_image [Resource],定义键盘显示的icon,文件路径为 

resources/base/media/bangcle_kb_img_dialog_icon。 

title_iscenter - [boolean]型,true为居中显示,false为左显示。 textlimitlen - [number]型,运行输入的长度,如6。 

title_show - [boolean]型,true为显示title_bar,false为不显示title_bar。 kb_visibility - [String]型,Visible为显示输入框,Hidden为不显示输入框。 clearInput - [boolean]型,true为清除输入内容,false为不清除输入内容。 numberRandom - [boolean]型,true为数字随机,false为数字固定。 

kb_defaultFocus - [boolean]型,true为默认focus,false为默认不focus。 kb_height - [number]型,配置输入框的宽度。 kb_width - [String]型,配置输入框的高度。 kb_borderStyle - [String]型,配置输入框类型。 kb_borderColor - [String]型,配置border颜色。 kb_padding - [String]型,配置输入框。 kb_borderRadius - [String]型,配置输入框的边角。 kb_borderWidth - [String]型,配置输入框的边角宽度。 kb_backgroundColor - [String]型,配置输入框的颜色。 kboard_backgroundColor - [String]型,配置键盘背景颜色。 onchange_call - 监听输入内容长度 finish_call - 监听输入内容是否完成 

##### **备注:** 

图标建议:透明背景,纯图标大小40x40(即剪切掉图标有效像素外的所有透明边界区域后的大小) 

### **5.2 引用安全键盘** 

在需要使用的view 中引入安全键盘 

```arkts
import { BangcleTextInput } from '@ohos/SafeKeyboard' export enum EKeyboardType { NUMERIC, //数字键盘 PAPERS, PASSWORD, UPPERCASE, // 大写字母键盘 LOWERCASE, // 小写字母键盘 SPECIAL, // 特殊字符键盘 } 
```

export enum EKeyboardType {
NUMERIC, //数字键盘
PAPERS,
PASSWORD,
UPPERCASE, // 大写字母键盘
LOWERCASE, // 小写字母键盘
SPECIAL, // 特殊字符键盘
}
finish_call(encvalue:string){
console.log("finish_call............"+encvalue);
}
//监听输入,等于6个就自动关闭
onchange_call(controller: TextInputController ,position: number, count:
number) {
console.log("onchange_call............count " + count);
==
if(count 6){
controller.stopEditing();
}
}

### **5.3 初始化** 

@Builder customBangcleKeyboardBuilderpassword() { BangcleTextInput({ keyboardid:this.keyboardid, // 定义键盘id ishide:this.ishide, // 键盘显示是否隐藏 has_sound:this.has_sound, // 键盘按键音设置 has_shock:this.has_shock, // 键盘震动设置 title_text:this.title_text,title_image:this.title_image, // 键盘 显示icon title_iscenter:this.title_iscenter, // 键盘显示位置 textlimitlen:this.textlimitlen, // 键盘输入长度限制 title_show: this.title_show, // 设置title_bar是否显示 encValue: this.encValue, // 加密后字符串 curKeyboardType: this.curKeyboardType, // 加盘类型需传入 EKeyboardType.NUMERIC 等 placeholder: this.placeholder, // 编辑框预显示内容 kb_visibility: this.kb_visibility, // 输入是否可见 clearInput: this.clearInput, // 输入框内容是否自动清除 numberRandom: this.numberRandom, // 数字键盘是否随机变化 kb_defaultFocus:this.kb_defaultFocus, // 配置默认focus kb_height: this.kb_height, // 配置输入框宽度 kb_width: this.kb_width, // 配置输入框高度 kb_borderStyle: this.kb_borderStyle, kb_borderColor: this.kb_borderColor, kb_padding: this.kb_padding, kb_borderRadius: this.kb_borderRadius, kb_borderWidth: this.kb_borderWidth, kb_backgroundColor: this.kb_backgroundColor, // 配置输入颜色 kboard_backgroundColor: this.kboard_backgroundColor, // 配置键盘 颜色 onKeyboardFinish:this.finish_call, //输入完成状态监听 onKeyboardChange:this.onchange_call, //输入监听 controller: this.controller //输入控制 }) } 

title_text:this.title_text,title_image:this.title_image, // 键盘
显示icon
title_iscenter:this.title_iscenter, // 键盘显示位置
textlimitlen:this.textlimitlen, // 键盘输入长度限制
title_show: this.title_show, // 设置title_bar是否显示
encValue: this.encValue, // 加密后字符串
curKeyboardType: this.curKeyboardType, // 加盘类型需传入
EKeyboardType.NUMERIC 等
placeholder: this.placeholder, // 编辑框预显示内容
kb_visibility: this.kb_visibility, // 输入是否可见
clearInput: this.clearInput, // 输入框内容是否自动清除
numberRandom: this.numberRandom, // 数字键盘是否随机变化
kb_defaultFocus:this.kb_defaultFocus, // 配置默认focus
kb_height: this.kb_height, // 配置输入框宽度
kb_width: this.kb_width, // 配置输入框高度
kb_borderStyle: this.kb_borderStyle,
kb_borderColor: this.kb_borderColor,
kb_padding: this.kb_padding,
kb_borderRadius: this.kb_borderRadius,
kb_borderWidth: this.kb_borderWidth,
kb_backgroundColor: this.kb_backgroundColor, // 配置输入颜色
kboard_backgroundColor: this.kboard_backgroundColor, // 配置键盘
颜色
onKeyboardFinish:this.finish_call, //输入完成状态监听

### **5.4 修改密码** 

在键盘中,SM4 密钥随机生成,不可配置;SM2 密钥可通过下面方式配置: 

```arkts
async aboutToAppear(){ let sm2key = "***"; BangcleUtils.RestPubKey(sm2key); } **5.5 调用** 
```

在需要试用安全键盘的位置调用: 

this.customBangcleKeyboardBuilderpassword(); 

### **5.6 设置键盘自动弹出** 

##### 首先定义keyboardid 

@State keyboardid: string = 'Bangcle_kb1'; 

##### 然后进行初始化 

customBangcleKeyboardBuilderpassword() { BangcleTextInput({ 

keyboardid:this.keyboardid, }) } 

##### 最后在需要地方进行引用 

focusControl.requestFocus(this.keyboardid); 

### **5.7 获取加密数据** 

加密数据保存在 encValue 中,可以通过下面方式获取 

console.log(“secdata:”+ this.encValue);
