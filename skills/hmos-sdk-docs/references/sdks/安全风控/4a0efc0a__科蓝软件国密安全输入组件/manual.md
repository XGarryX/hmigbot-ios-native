CSIITM 标准文档 

文档编号:CSII-PS-PEC-2016003 

# POWERENTER 客户端安全输入控件 ( **Harmony** 版) 用户手册 

#### 北京科蓝软件系统股份有限公司 

2024 年 3 月 1 日 

#### 文档修改记录 

|版本|内容|编写时间|编写|审核|
|---|---|---|---|---|
|1.0|新建|2024-03-01|彭佳星|赵阳|
|1.1|新增校验密文md5|2024-04-02|彭佳星|赵阳|
|1.2|新增控件公钥通过属性设置|2024-04-02|彭佳星|赵阳|
|1.3|新增弹出获取键盘高度|2024-05-10|彭佳星|赵阳|

##### 版权申明: 

本文档的版权属于北京科蓝软件系统股份有限公司,任何人或组织未经许可, 

不得擅自修改、拷贝或以其它方式使用本文档中的内容。 

### 目   录 

|一、 引言........................................................................................................................1|
|---|
|1.1编写目的...........................................................................................................1|
|1.2背景知识及参考资料.......................................................................................1|
|1.3使用环境...........................................................................................................1|
|二、 控件概述................................................................................................................2|
|2.1系统构成...........................................................................................................2|
|2.2功能特点...........................................................................................................2|
|2.3技术特点...........................................................................................................2|
|2.4控件接口描述...................................................................................................2|
|2.4.1 package引用...........................................................................................3|
|2.4.2 POWERENTER安全输入框属性.........................................................3|
|2.4.3 CSIIKeyBoardUtil POWERENTER数据加密模块和方法..................3|
|2.4.4 ClickType POWERENTER安全键盘状态监听...................................3|
|三、 开发流程概述........................................................................................................4|
|3.1使用安全输入框........................................................................................4|
|3.2调用安全输入框方法................................................................................4|
|3.3接受安全键盘状态信息方法....................................................................4|
|四、DevEcoStudio相关设置说明................................................................................4|
|4.1 Har文件导入.....................................................................................................5|
|五、 代码示例................................................................................................................4|

用户手册 

POWERENTER 安全输入控件 

## 一、引言 

### **1.1** 编写目的 

- “POWERENTER 客户端安全输入控件”是保护用户敏感信息输入的重要手段,能 

- 对客户端操作系统进行安全增强,可大幅提升“木马”程序非法获取用户敏感输入信息 “成本”的软件集合。 

“POWERENTER 客户端安全输入控件”的 Harmony 版本由安全输入框模块和安全 键盘核心实现模块组成。开发人员通常不直接调用安全键盘核心实现模块,而是主要 通过使用 Harmony SDK 调用安全输入框模块来实现与自身业务系统的整合。本《用户 手册》中将以一个典型的开发部署为例,为开发人员展示安全输入框的调用方法及注 意事项,使开发人员能够独立应用 POWERENTER 客户端安全输入控件。 

### **1.2** 背景知识及参考资料 

假定读者对下列技术有一定的理解: 

|技术|有关内容|
|---|---|
|Harmony SDK|Harmony SDK的基本常识|
|Harmony|Harmony的Ability基本知识|
|Ability||
|通信|Ability的通信方法(非必须)|
|NAPI|NAPI相关知识(非必须)|

### **1.3** 使用环境 

DevEco Studio3.1.1Release(及以上含) 

文件编号:CSII-PS-PEC-2016003 

第 1 页 

用户手册 

POWERENTER 安全输入控件 

## 二、安全输入控件概述 

### **2.1** 系统构成 

PWERENTER 客户端安全输入控件 Harmony 版本由两部分构成: 

安全键盘核心实现模块——由 C++实现的 so 动态库。 

安全输入框模块——提供 PWERENTER 安全输入框的 Har 包,供 Harmony SDK 

调用通过 NAPI 方式调用加密核心实现模块动态库。 

### **2.2** 功能特点 

- 防止 Hook 类木马程序攻击。 

- 防止网络传输泄密 

- 支持时间戳,防止重放攻击 

- 防破解保护 

### **2.3** 技术特点 

- 用户输入的敏感信息不在界面框中保存,而是通过加密后存放在安全键盘输 入核心库中,有效防止敏感信息泄露。 

- 安全键盘样式基于 Harmony 原生开发,核心由安全键盘输入核心动态库实现 

- 支持多种加密方式。 

- 支持自定义属性,按键乱序、最大/小长度等等。 

### **2.4** 控件接口描述 

#### **2.4.1Package** 引用 

|包|说明|
|---|---|
|CSIIPwdKeyboardLibrary/src/main/ets/ components/mainpage/CSIIPwdInput.ets|POWERENTER安全输入框|
|CSIIPwdKeyboardLibrary/src/main/ets/ components/mainpage/CSIINumberInput.ets|POWERENTER纯数字安全输入框|
|CSIIPwdKeyboardLibrary/src/main/ets/ PwdKeyBoard/ClickType.ets|POWERENTER安全键盘监听接口|

文件编号:CSII-PS-PEC-2016003 

第 2 页 

用户手册 

POWERENTER 安全输入控件 

|CSIIPwdKeyboardLibrary/src/main/ets/|POWERENTER加密模块|
|---|---|
|PwdKeyBoard/model/CSIIKeyBoardUtil.ets||

文件编号:CSII-PS-PEC-2016003 

第 3 页 

用户手册 

POWERENTER 安全输入控件 

#### **2.4.2POWERENTER** 安全输入框属性 

#### **Input** 框 **{** 

**@State name:string = ‘CSII-POWERENTER’ @Provide menuType:number = 0 @State fontColor:string = “” @State fontSize:string =“14fp” @State placeholderColoar:Color|number|string =”#333333” @State placeholderFont:string|number=12 @State maskchar:string = “*” @State accept:string = ‘[:print:]+’ @State maxLength:number = 12 @State minLength:number = 6 @State encryptType:number = 0** 

**@State isRandom:boolean = false** 

**@State kbdVibrator:boolean = false** 

**@State clearWhenOpenKbd:boolean = false** 

**@State whenMaxCloseKbd:boolean = false** 

**@State dataDictionary:string = “”** 

**@State keyBoardMode:number = 0** 

**@State isRandomType:number = 0** 

**@State caretColor:string|undefined = “#00000000”** 

**@State isPlaintextShow:boolean = false** 

**@State screenCapture:boolean = true** 

**@State isBounceUp:boolean = false** 

**@State bgColor:string = “”** 

**@State isShowUnderLine:boolean = false** 

**@State publicKey:string = “”** 

#### **}** 

#### 参数说明: 

|属性|说明|
|---|---|
|name:string|POWERENTER 安全输入框的名|

文件编号:CSII-PS-PEC-2016003 

第 4 页 

用户手册 

POWERENTER 安全输入控件 

||字 。 默 认 名 为 CSII- POWERENTER。若同时使用多个 输入框,每个输入框的名字必须单 独指定,并且不能相同|
|---|---|
|FontColor:string|Color|number|字体颜色,初始化时指定。默认为 黑色;|
|FontSize:string|number|字体大小,初始化时指定。默认为 14fp;|
|placeholderColor:Color|number|
string|设置placeholder文本颜色。默认为
#333333|
|placeholderFont:string|number|设置placeholder文本样式。默认为 12|
|maskchar:string|控件显示的掩码,初始化时指定。|
||默认为*,一般密码为*、#等字符掩 码。|
|menuType:number|软键盘类型,初始化时指定。0:全 键盘字母键盘;1:全键盘符号键 盘|

文件编号:CSII-PS-PEC-2016003 

第 5 页 

用户手册 

POWERENTER 安全输入控件 

||默认为全键盘字母键盘。|
|---|---|
|keyboardMode:number|设置软键盘DOWN时,按键是否 变化。 0:放大效果1:无变化 默认为0|
|accept:string|可以接受的字符,初始化时指定全 字符。accept为正则表达式。默认” [:print:]+”|
|maxLength:number|最大长度,初始化时指定。默认为 12,当输入内容达到最大长度内容 时,将不能再输入|
|minLength:number|最小长度,初始化时指定。默认为 6,cipherValidityVerify()方法会最 小值判断输入内容是否满足要求|
|isRandom:boolean|设置软键盘按键位置是否随机,初 始化时指定。可选值:true、false, 默认选择不随机 多个键盘要保持统一,不要一个乱 序 一个不乱序,会出现键值错乱|

文件编号:CSII-PS-PEC-2016003 

第 6 页 

用户手册 

POWERENTER 安全输入控件 

||情况|
|---|---|
|isRandomType:number|可供选择键盘乱序 设置这个属性 需要设置isRandom为true 0:按照isRandom属性设置全部乱 序或者不乱序 1:数字乱序其他不乱序 2:字母乱序其他不乱序 3:数字和字母乱序其他不乱序 多个键盘要保持统一,不要一个乱 序 一个不乱序,会出现键值错乱 情况|
|kbdVibrator:boolean|设置触屏震动,可选值:true、false 默认为false,触屏不震动|
|clearWhenOpenKbd:boolean|打开键盘时,是否清空原本输入的|
||内容。默认为true可选值: true、false|
|whenMaxCloseKbd:boolean|当输入长度达到maxLength是否自 动关闭键盘|

文件编号:CSII-PS-PEC-2016003 

第 7 页 

用户手册 

POWERENTER 安全输入控件 

||默认是false可选值:true、false|
|---|---|
|encryptType:number|设置密码的加密类型,初始化时指 定更多信息,请咨询技术支持工程 师,默认0一层加密|
|screenCapture:boolean|设置是否开启键盘截屏录屏功能, 默认是true可选值:true、false|
|dataDictionary:string|设置数据字典,传入值|
||如” 123456,abcdef” 一般与 cipherValidityVerify()连用 默认值是” ” ,可以不设置|
|caretColor:string|underfined|Color|设置输入框光标颜色,默认值是 #000000|
|isBounceUp:boolean|设置键盘是否自动弹出,默认值是 false可选值:true、false|
|bgColor:string|Color|number|设置背景颜色,默认值是””|
|publicKey:string|设置控件加密外传公钥,默认值是 “”|
|textAlign:TextAlign|设置内容在输入框中的水平对齐方|

文件编号:CSII-PS-PEC-2016003 

第 8 页 

用户手册 

POWERENTER 安全输入控件 

||式。默认值是:TextAlign.Start|
|---|---|
|pwdInputHeight:number|获取全键盘高度,键盘首次弹出的 时候获取,使用键盘的时候一定要 定义属性 @Provide pwdInputHeight:number=0|
|numberInputHeight:number|获取数字键盘高度,键盘首次弹出 的时候获取,使用键盘的时候一定 要定义属性 @Provide numberInputHeight:number=0|
|isPreventScreen:boolean|关闭键盘后移除防截屏录屏|
||true:不移除false:移除 默认值: true|
|clearWhenClickKbd:boolean|键盘弹出后点击输入框是否清除输 入内容false:不清除true:清除 默认值:false|
|inputController:TextInputController|组件控制|

文件编号:CSII-PS-PEC-2016003 

第 9 页 

用户手册 

POWERENTER 安全输入控件 

||器,inputController.stopEditing()可|
|---|---|
||关闭键盘|
|supportAvoidance:boolean|键盘避让,false:不避让true:避让|
||默认值:false|
|keyBoardBottom: string | number|调整键盘和底部距离|
|keyboardSize:string|number|修改全键盘内字体大小,默认:18|
|keyboardNumberSize : string||修改数字键盘内字体大小,默认|
|number|24|
|menuKeyboardType:number|关闭键盘后再次打开显示哪种键|
||盘.默认:0|

#### **2.4.3 POWERENTER** 安全输入框方法 **POWERENTER** 安全输入框 **CSIIKeyBoardUtil** 提供的方法有: 

|包|说明|
|---|---|
|getValue(name:string,timeStamp:str ing)|获取输入加密后的输入内容。 name:对应加密内容的键盘名称|
||timestamp:时间戳,单位:毫秒|
|getCipherValidtyVerify(name:string )|依据输入框属性中设置的accepts 正则表达式验证用户输入信息是否|

文件编号:CSII-PS-PEC-2016003 

第 10 页 

用户手册 

POWERENTER 安全输入控件 

||合法|
|---|---|
||name:对应要获取的键盘名称 返回值: 0:合法|
||-1:内容为空|
||-2:输入小于最小长度|
||-3:输入字符不合法,跟 accepts有关|
||-4:内容数据字典验证未通过 跟输入框设置的dataDictionary 属 性有关|
|getNativeCipherLength(name:strin|获取的内容长度|
|g)|name:对应要获取的键盘名称|
|clearKeyboard(name:string)|清除输入内容 name:对应要清除的键盘名称|
|getTextStandardEncrypt(text:string,|对明文进行一层加密,并返回密|
|timeStamp:string)|文,常用于手势密码(此方法需要|
||定制,如有需要请与技术支持工程|

文件编号:CSII-PS-PEC-2016003 

第 11 页 

用户手册 

POWERENTER 安全输入控件 

||师联系)|
|---|---|
||text:需要加密的明文数据 timeStamp:时间戳,单位:毫秒|
|getTextOfDoubleEncrypt(text:strin|使用内置公钥对text 进行两层加|
|g,timestamp:string,publickey:string, encryptType:number)|密,并返回密文,常用于手势密码 (此方法需要定制,如有需要请与 技术支持工程师联系) text:需要加密的明文数据 timeStamp:时间戳,单位:毫秒 publickey:外传公钥 encryptType:加密类型|
|getContentDegree(name:string)|判断输入密码的密码强度,返回值 E(密码为空)、S(强)、M (中)、W(弱) 判断规则如下: A、全数字或全小写字母或全大写 字母或全符号|
||B、满足以下任意条件:|

文件编号:CSII-PS-PEC-2016003 

第 12 页 

用户手册 

POWERENTER 安全输入控件 

||a、密码长度2/3及以上是连续|
|---|---|
||位数|
||b、密码长度2/3及以上的相邻 密码是相同位数|
||弱:满足A和B或长度小于6位|
||中:满足A不满足B|
||满足B不满足A|
||强:同时不满足A和B name:需要获取的对应键盘名称|
|getCipherContentDegreeJNNCBA|密码强度判断|
|NK(name:string)|返回值E (密码为空),S (强),W(弱)|
||规则如下:|
||A,条件|
||a,至少包含1个数字 b,至少包含1个小写字母|
||c,至少包含1个大写字母|

文件编号:CSII-PS-PEC-2016003 

第 13 页 

用户手册 

POWERENTER 安全输入控件 

|d,至少包含1个特殊字符|
|---|
|B,条件|
|a,数字和字母(大小写不区分)|
|向上|
|连续大于等于3|
|b,数字和字母(大小写不区分)|
|向下|
|连续大于等于3|
|c,连续相同个数大于等于3(字|
|母不|
|区分大小写)|
|弱:密码长度小于8位|
|强:满足A中4个(a,b,c,d)条件 至|
|少3|
|个(>=3)且不满足B中(a,b,c)|
|弱:满足B中(a,b,c)任何一个或|
|满足|
|A中4个(a,b,c,d)条件小于3个|

文件编号:CSII-PS-PEC-2016003 

第 14 页 

用户手册 

POWERENTER 安全输入控件 

||(<3)|
|---|---|
|getCipherContenType(name:string)|获得输入密码内容类型判断值,共 7种类型, 八个返回值 返回值类型说明: 0内容为空 1内容只含有数字 2内容只含有字母 3内容包含数字和字母 4内容只含有符号 5内容含有符号和数字 6内容含有符号和字母 7内容含有符号,数字和字母 _name_:需要获取的对应键盘名称|
|setKeyBoardHidden(name:string,is Hidden:boolean)|设置点击完成键是否隐藏键盘 name:需要设置的对应键盘名 isHidden:是否隐藏true、false|
|destroy(name:string)|销毁键盘|

文件编号:CSII-PS-PEC-2016003 

第 15 页 

用户手册 

POWERENTER 安全输入控件 

||name:需要销毁的对应键盘名|
|---|---|
|getInputData(name:string,callback:|设置获取键盘输入值回调|
|Function)||
|getMd5Hash(name:string)|获得输入内容32位md5结果,用|
||于比较两个密码是否相等|

#### **2.4.4ClickType POWERENTER** 安全键盘状态监听接口 **Clicktype** 接口内部状态有: 

|回调状态|说明|
|---|---|
|ClickType.CLICK_INPUT|键盘输入|
|ClickType.CLICK_DELETE|键盘删除|
|ClickType.CLICK_DOWN|键盘完成按钮|
|ClickType.CLICK_MAXCLOSEK|最大值关闭键盘|
|BD||
|ClickType.CLICK_ONBLUR|失去焦点|
|ClickType.CLICK_OPEN|获取焦点|

文件编号:CSII-PS-PEC-2016003 

第 16 页 

用户手册 

POWERENTER 安全输入控件 

## 三、开发流程概述 

### **3.1** 使用安全输入框 

### **3.2** 调用安全输入框的方法 

### 根据业务需要调用安全输入框的方法,比如判断输入内容的强度、 

### 长度等。 

### **3.3** 接收安全键盘状态信息的方法 

文件编号:CSII-PS-PEC-2016003 

第 17 页 

用户手册 

POWERENTER 安全输入控件 

文件编号:CSII-PS-PEC-2016003 

第 18 页 

用户手册 

POWERENTER 安全输入控件 

## 四、 **DevEcoStudio** 相关设置说明 

### **4.1Har** 文件导入 

首先在 **entry** 目录下创建 **libs-har** 目录,将 **SDK** 放入这个目录, 然后在 **entry** 目录下有个 **oh-package.json5** 文件,打开这个 

文 件 , 找 到 **dependencies** 属 性 添 加” **CSIIPwdkeyboardLibrary“** :” **file:../entry/libs-har/** 

### **CSIIPwdkeyboardLibrary.har“** 

文件编号:CSII-PS-PEC-2016003 

第 19 页 

用户手册 

POWERENTER 安全输入控件 

## 五、代码示例 

private scroller: Scroller = new Scroller() 

文件编号:CSII-PS-PEC-2016003 

第 20 页 

用户手册 

POWERENTER 安全输入控件 

文件编号:CSII-PS-PEC-2016003 

第 21 页 

用户手册 

POWERENTER 安全输入控件 

文件编号:CSII-PS-PEC-2016003 

第 22 页 

用户手册 

POWERENTER 安全输入控件 

## 六、注意事项 

- 1:调用键盘关闭可通过 inputController.stopEditing() 在需要点击的按钮处关闭,需要 给键盘传递 inputController 属性 

- 2:点击其他按钮打开键盘,调用 focusControl.requestFocus("Stack"); 转移焦点到键盘 上,键盘外层需要套一层 Stack()  id 设置在 Stack 上,要不然无法转移。 

3:如果键盘需要跟 h5 交互,可把键盘包装成一个 dialog,设置键盘宽高为 0,正常 设置属性,h5 点击输入框回调中转移焦点到键盘上可调用 dialog 的打开 或者是定义一个宽高为 0 的输入框,键盘外层需要套一层 Stack()  具体例子可查看 demo 

- 4: 注意如果要使用多个键盘不要一个开启乱序 一个不开启乱序,要保持一致,可能 会导致出现键盘底层绑定键值出现错乱情况。 

5: 

如遇到此类崩溃,大概率是延迟销毁导致此类问题,导致键盘传值为空。可尝试设置 键盘 name+随机数 

文件编号:CSII-PS-PEC-2016003 

第 23 页
