# **娜迦科技鸿蒙安全键盘SDK HarmonyOS 使用文档** 

## **1、集成方式及SDK清单** 

#### **娜迦科技鸿蒙安全键盘SDK版本要求API10及以上版本。** 

#### **SDK文件清单如下:** 

nagainarg.har 

#### **娜迦科技鸿蒙安全键盘SDK采用自定义组件前端技术实现,通过将输入控件封装为自定义组件,供应用开发方进行集成调用,集成步骤如下:** 

01、nagainarg.har文件拷⻉至应用开发工程对于的entry的lib目录中 

02、配置对于entry的oh-package.json5文件,配置dependencies节点内容: "dependencies": { "libnagainarg": "file:./libs/nagainarg.har" } 

- 03、在需要使用密码卫士的ets页面通过import语句引入密码卫士组件 import { NaGainKeyboard } from 'libnagainarg'; 

04、在适当位置插入组件标签并配置相关属性 ``` @State tipsTxt: string = ""; 

controller1: TextInputController = new TextInputController(); @Prop ngRandom: boolean = true; //按键乱序 @Prop ngKeyBoardType: number = 0//键盘Type 0 字母键盘 2字母数字 键盘 3特殊字符键盘 4纯数字键盘 @Prop ngKeyBoardNumKBType: number = 0; //键盘Type设置为4时 小选择 0 默认 1 小数点 2 身份证 X @Prop ngInputValue: string = "111111"; // 输入框inputValue @Prop ngPwd1: string = ""; //密文输出 json格式 

@Prop ngKey: string = "12345678901234567890123456789012"; //sm4 加密随机数 @Prop ngGMPublicXY: string = 

"1093A047C5CBF48283EC7A210703F3FF9EA4448DC15D56B4CD82FCB27DAD2D45F2BB0BF953BCEBB635D9D34E473ECEFC9F25880EB1669F94DE050A29AC86F308"; 

//sm2加密公钥X @Prop ngFocusKey: string = 'KeyP'; //键盘唯一ID @Prop ngEncrypt: boolean = true; //明密文模式 @Prop ngLic: string = 

@Prop ngInputFilter: string = ""//"^[A-Za-z0-9]+$" //输入中字符正则过滤 @Prop ngInputFilterEnd: string = ""//"^[A-Za-z0-9]{3,15}$" //输入完 ismatch 返回正则验证结果 @Prop ngMaxLen: number = 20 //最大输入限制 @Prop ngPresStyle: number = 1 //按键动画 0 没有动画 1按键动画 @Prop ngShowACDone: boolean = true //是否显示 键盘右上⻆收回三⻆ 按钮 @Prop ngNeedHighlighted: boolean = true // 按键状态 true 有按键状态 @Prop ngPlaceholder: string = "密码安全输入-字母数字键盘" //设置placeholder @Prop ngAutoDoneKB: boolean = true // 收起按键自动收起键盘 

@Prop ngKeyBoardType2: number = 4//键盘Type 0 字母键盘 2字母数字键盘 3特殊字符键盘 4纯数字键盘 @Prop ngPlaceholder2: string = "密码安全输入-纯数字键盘" //设置 placeholder @Prop ngInputValue2: string = ""; //输入框inputValue 

NaGainKeyboard({ ngWidth:'100%', ngBackgroundColor:Color.White, ngEncrypt: this.ngEncrypt, ngAutoDoneKB: this.ngAutoDoneKB, ngFocusKey: this.ngFocusKey, ngInputFilter: this.ngInputFilter, ngInputFilterEnd: this.ngInputFilterEnd, ngRandom: this.ngRandom, ngKeyBoardType: this.ngKeyBoardType, ngKeyBoardNumKBType: this.ngKeyBoardNumKBType, ngShowACDone: this.ngShowACDone, ngPresStyle: this.ngPresStyle, ngInputValue: this.ngInputValue, ngLic: this.ngLic, ngPwd: $ngPwd1, ngPlaceholder: this.ngPlaceholder, ngMaxLen: this.ngMaxLen, ngNeedHighlighted: this.ngNeedHighlighted, ngKey: $ngKey, ngGMPublicXY: this.ngGMPublicXY, 

ng _call_ onInputChanged: (inputValue: string, pwd: string) => { console.log("onInputChanged:" + inputValue + "-pwd:" + pwd); this.tipsTxt = "onInputChanged:" + inputValue + "\r\npwd:" + pwd; } , ng _call_ onFocusAction: () => { //键盘首次获取焦点会触发 console.log("kb show!!!"); this.tipsTxt = "onFocusAction:" + this.ngPwd1; ; }, ng _call_ doneAction: () => { console.log("kb done!!!"); // focusControl.requestFocus('button') this.tipsTxt = "doneAction:" + this.ngPwd1; }, ng _call_ onBlurAction: () => { console.log("kb onBlurAction!!!"); // focusControl.requestFocus('button') this.tipsTxt = "onBlurAction:" + this.ngPwd1; } }).height(40).width('80%'); ``` 

完成上述步骤,即可使用娜迦科技鸿蒙安全键盘SDK。 

## **2、属性配置接口(打钩的属于初始化强制属性)** 

## **1. 基础属性 (Regular Properties)** 

此类属性通常由父组件在初始化时单向传入,用于控制输入框的基础样式和交互行为。 

|**属性名**|**类型**|**默认值**|**描述**|
|---|---|---|---|
|**controller**|TextInputController|new TextInputController()|输入框控制器,用于控制光标、拉起/收起键盘 等。|
|**ngPadding**|Padding|{ left: 0, right: 0 }|输入框内边距。|
|**ngBackgroundColor**|ResourceColor|''|输入框背景颜色。|
|**ngWidth**|Length|'100%'|输入框宽度。|
|**ngHeight**|Length|40|输入框高度。|
|**ngFontSize**|Length|18|输入框字体大小。|
|**ngFontColor**|ResourceColor|''|输入文本的字体颜色。|
|**ngPlaceholderColor**|ResourceColor|''|提示文本(Placeholder)的字体颜色。|
|**ngCaretColor**|ResourceColor|''|光标颜色。|
|**ngStyle**|TextInputStyle|TextInputStyle.Default|输入框风格(如 Default 或 Inline )。|
|**ngTextAlign**|TextAlign|TextAlign.Start|文字对齐方式(居左/居中/居右)。|
|**ngCopyOptions**|CopyOptions|CopyOptions.None|复制粘贴选项,默认禁止复制(提升安全性)。|
|**ngMargin**|Margin \| Length|0|外边距。|
|**ngBorderRadius**|Length \| BorderRadiuses|0|边框圆⻆。|
|**ngBorderWidth**|Length \| EdgeWidths|0|边框宽度。|
|**ngBorderColor**|ResourceColor \| EdgeColors|''|边框颜色。|
|**ngDefaultFocus**|boolean|false|是否默认获取焦点。|
|**ngVisibility**|Visibility|Visibility.Visible|组件可见性( Visible/ Hidden/ None )。|
|**ngCancelButtonStyle**|cancelButtonType|{style:CancelButtonStyle.INVISIBLE}|右侧取消/清空按钮的样式,默认不显示。|

## **2. 状态绑定属性 (Link & Watch Properties)** 

此类属性使用 @Link 修饰,支持父子组件 **双向数据绑定** 。其中部分属性带有 @Watch 监听器,当值发生改变时会触发特定的内部逻辑。 

### **2.1 基础交互与配置** 

|**属性名**|**类型**|**描述**|
|---|---|---|
|**ngPlaceholder**|string|提示文本(例如:"请输入密码")。|
|**ngFocusKey**|string|用于标识该输入框焦点的Key值。|
|**ngMaxLen**|number|限制输入的最大长度(默认通常为20)。|

### **2.2 安全与加密配置** 

|**属性名**|**类型**|**描述**|
|---|---|---|
|**ngLic**|string|安全控件所需的License证书字符串。|
|**ngEncrypt**|boolean|是否开启文本加密(密文显示/密文传输)。|
|**ngRandom**|boolean|是否开启乱序键盘(每次弹起键盘时按键顺序随机)。|
|**ngKey**|string|**【带监听 changeInput1】** 一字一密加密密钥,通常由前端向服务器网络请求获取。|
|**ngGMPublicXY**|string|国密(SM2等)公钥坐标,用于前端加密。|
|**ngPwd**|string|加密后的密码密文结果。|

### **2.3 键盘与按键行为** 

|**属性名**|**类型**|**描述**|
|---|---|---|
|**ngKeyBoardNumKBType**|number|**纯数字键盘类型细分**: • 0 :默认纯数字 • 1 :带小数点 • 2 :带身份证X|
|**ngKeyBoardType**|number|**主键盘类型**: • 0 :默认键盘 • 1 :字母键盘(大写) • 2 :字母数字键盘 • 3 :特殊字符键盘 • 4 :纯数字键盘|
|**ngAutoDoneKB**|boolean|输入达到最大长度后,是否自动收起键盘/完成输入。|
|**ngShowACDone**|boolean|是否在键盘工具栏显示“完成”按钮。|
|**ngNeedHighlighted**|boolean|按键是否有高亮状态。默认加密时没有高亮,非加密时有高亮(防止侧窥)。|
|**ngPresStyle**|number|键盘或按键的预设样式风格。|

### **2.4 输入拦截与数据流 (监听器)** 

|**属性名**|**类型**|**描述**|
|---|---|---|
|**ngInputFilter**|string|输入过程中的单个字符过滤器(正则表达式或过滤规则)。|
|**ngInputFilterEnd**|string|**【带监听 inputChange】** 输入完整体后的过滤与判断规则。|
|**ngInputValue**|string|**【带监听 changeInputValue】** 当前输入框的明文真实值(双向绑定)。|

### **回调函数** 

- [ ] ng _call_ onFocusAction: () => void;回调方法,键盘弹出时回调方法 

- [ ] ng _call_ onBlurAction: () => void;回调方法,键盘收起回调方法(包括点击空白处失焦,此处失去焦点建议使用:ets页面声明一个button,设置key属性, focusControl.requestFocus('button')) 

- [ ] ng _call_ doneAction: () => void;回调方法,键盘点击右下部登录按钮方法回调 

- [ ] ng _call_ onInputChanged: (inputValue:string ,pwd: string) => void = () => {}回调方法,字符输入变化 ### 其他接口,此处只是列举,因为组件封装,系统属性无法暴露,此处暴 露部分UI属性,有需要其他属性的,可以联系我们,开放出去: 

- [ ] heightP: Length; 

- [ ] widthP: Length = 220; 

- [ ] placeholderColor: ResourceColor; 

- [ ] caretColor: ResourceColor; 

- [ ] copyOptions: CopyOptions; 

- [ ] fontSize: Length; 

- [ ] fontColor: ResourceColor; 

- [ ] style: TextInputStyle; 

- [ ] textAlign: TextAlign; 

- [ ] marginP: Margin | Length = 0; 

- [ ] borderRadiusP: Length | BorderRadiuses; 

- [ ] borderWidthP: Length | EdgeWidths; 

- [ ] borderColorP: ResourceColor | EdgeColors; 

- [ ] visibilityP: Visibility; 

- [ ] backgroundColorP: ResourceColor = ''; 

- [ ] paddingP:Padding = {left: 0,right:0}; 

- [ ] cancelButtonStyle:CancelButtonStyle = {style:CancelButtonStyle.INVISIBLE}; 

- [ ] defaultFocusP属性,设置为true时主动获取焦点弹起键盘。 ... 

## **3、数据获取接口** 

#### **数据获取项如下所示:** 

m_outputPwd属性,此属性是输出的密文串,格式为json格式 

``` 1.sm2sm4,为用户输入数据的加密密文(SM4(SM2(DATA))) 

2.sm2,为用户输入数据的加密密文SM2(DATA) 

3.sm3,为用户输入数据的SM3 hash值 

4.Sm4,为用户输入数据的SM4 

5.isstatus,为输入数据的字符类型个数 

6.issimple,是否符合弱密码特征 

7.length,为输入数据的长度 

8.issimple,为输入数据是否是简单密码,1是,0不是 

9.ismatch,为输入数据是否匹配reg2正则表达式,1是,0不是 ``` 

```

### **具体集成代码,可参考demo工程。** 

**需要注意:har手动更新,导入har文件后,需要先删除oh_moudle/.ohpm目录下对应的har缓存文件,再重新run install har包**
