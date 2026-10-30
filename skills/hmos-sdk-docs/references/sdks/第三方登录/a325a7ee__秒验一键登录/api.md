# **接口文档** 

本模块首批接口从 OpenHarmony SDK API version 12 开始支持。 

## **ZztSDK.init** 

init(context: Context, appkey: string, secret: string):void 

#### 初始化sdk 

### **参数:** 

|**参数名**|**类型**|**必填**|**说明**|
|---|---|---|---|
|context|Context|是|上下文context请在@Component页面中通过let context = getContext(this) 获取请勿在UIAbility中用this.context获取,否则会影响主题设置|
|appkey|string|是|sdk的appkey|
|secret|string|是|sdk的secret|

### **返回值:** 

|**类型**|**说明**|
|---|---|
|void||

### **示例:** 

ZztSDK.init(getContext(this), 'your appkey', 'your secret') 

## **ZztSDK.submitPolicyGrantResult** 

submitPolicyGrantResult(granted: boolean): void 

#### 提交隐私结果 

### **参数:** 

|**参数名**|**类型**|**必填**|**说明**|
|---|---|---|---|
|granted|boolean|是|true代表同意隐私, false代表不同意隐私|

### **返回值:** 

|**类型**|**说明**|
|---|---|
|void||

### **示例:** 

ZztSDK.submitPolicyGrantResult(true) 

## **FlyVerify.preVerify** 

preVerify(callback?: OperationCallback<void>):Promise<void> 

#### 预取号 

### **参数:** 

|**参数名**|**类型**|**必填**|**说明**|
|---|---|---|---|
|callback|OperationCallback|否|若传入回调,代表结果通过回调传递出去|

### **返回值:** 

|**类型**|**说明**|
|---|---|
|Promise<void>|若未传入回调,代表结果通过Promise<void>传递出去|

### **示例:** 

//回调形式 

```arkts
let callback: OperationCallback<void> = { onSuccess: () => { let result = new Date() + " onSuccess" }, onFailure: (e) => { let result = new Date() + " onFailure:" + JSON.stringify(e) } }; FlyVerify.preVerify(callback); 
```

//Promise形式 FlyVerify.preVerify().then((data)=>{ let result = new Date() + " onSuccess" }).catch((e:VerifyException)=>{ 

let result = new Date() + " onFailure:" + JSON.stringify(e) }) 

## **FlyVerify.verify** 

verify(callback?: OperationCallback<VerifyResult>):Promise<VerifyResult> 

#### 打开授权页 

### **参数:** 

|**参数名**|**类型**|**必填**|**说明**|
|---|---|---|---|
|callback|OperationCallback|否|若传入回调,代表结果通过回调传递出去|

### **返回值:** 

|**类型**|**说明**|
|---|---|
|Promise<void>|若未传入回调,代表结果通过Promise<void>传递出去|

### **示例:** 

//回调形式 let callback: OperationCallback<VerifyResult> = { onSuccess: (data) => { this.content = new Date() + " onSuccess:" + JSON.stringify(data) this.result = data; }, onFailure: (error) => { this.content = new Date() + " onFailure:" + JSON.stringify(error) } }; FlyVerify.verify(callback); //Promise形式 FlyVerify.verify().then((data)=>{ this.content = new Date() + " onSuccess:" + JSON.stringify(data) this.result = data; }).catch((e:VerifyResult)=>{ this.content = new Date() + " onFailure:" + JSON.stringify(e) }); 

## **VerifyResult** 

取号结果 

|**名称**|**类型**|**必填**|**说明**|
|---|---|---|---|
|operator|string|是|运营商名称: CUCC->中国联通, CTCC->中国电信, CMCC->中国移动|
|opToken|string|是|运营商token|
|token|string|是|token|

## **FlyVerify.setPreVerifyTimeout** 

setPreVerifyTimeout(timeout:number) 

#### 设置预取号超时 

### **参数:** 

|**参数名**|**类型**|**必填**|**说明**|
|---|---|---|---|
|timeout|number|是|预取号设置超时时间单位毫秒,若小于2000,内部会设为2000|

### **返回值:** 

|**类型**|**说明**|
|---|---|
|void||

### **示例:** 

//timeout毫秒时间 

FlyVerify.setPreVerifyTimeout(5000); 

# **五.授权页ui相关** 

## **FlyVerify.setTheme** 

setTheme(theme: ThemeConfig) 

#### 设置ui主题 

### **参数:** 

|**参数名**|**类型**|**必填**|**说明**|
|---|---|---|---|
|theme|ThemeConfig|是|设置自定义主题|

### **返回值:** 

|**类型**|**说明**|
|---|---|
|void||

**示例:** 

//创建主题,设置需要的属性,可使用链式设置多个属性 

let theme = new ThemeConfig().setNumberSize(18).setLogBtnText('本机号码一键登录')... //传入主题 

FlyVerify.setTheme(theme) 

## **ThemeConfig.setSystemBarProperties** 

setSystemBarProperties(systemBarProperties: window.SystemBarProperties): ThemeConfig 

设置窗口内导航栏、状态栏属性 

### **参数:** 

|**参数名**|**类型**|**必填**|**说明**|
|---|---|---|---|
|systemBarProperties|window.SystemBarProperties|是|窗口内导航栏、状态栏属性|
|**返回值:**||||
|**类型**||**说明**||
|ThemeConfig||主题对象||

### **示例** 

new ThemeConfig().setSystemBarProperties({ statusBarColor: '#ffffff', statusBarContentColor: '#000000' }) 

## **ThemeConfig.setNumberSize** 

setNumberSize(value: number): ThemeConfig 

#### 设置号码栏字体大小 

### **参数:** 

|**参数名**|**类型**|**必填**|**说明**|
|---|---|---|---|
|value **返回值:**|number|是|字体大小|
|**类型**||**说明**||
|ThemeConfig||主题对象||

### **示例** 

new ThemeConfig().setNumberSize(18) 

## **ThemeConfig.setNumberMargin** 

setNumberMargin(margin: Margin): ThemeConfig 

#### 设置号码栏偏移量 

### **参数:** 

|**参数名**|**类型**|**必填**|**说明**|
|---|---|---|---|
|value|Margin|是|号码栏偏移量大小|

### **返回值:** 

|**类型**|**说明**|
|---|---|
|ThemeConfig|主题对象|

### **示例** 

new ThemeConfig().setNumberMargin({ top:10 }) 

## **ThemeConfig.setNumberAlignRuleOption** 

setNumberAlignRuleOption(value: AlignRuleOption): ThemeConfig 

设置号码栏相对布局偏移规则 

### **参数:** 

|**参数名**|**类型**|**必填**|**说明**|
|---|---|---|---|
|value|AlignRuleOption|是|号码栏相对布局偏移规则|
|**返回值:**||||
|**类型**|||**说明**|
|ThemeConfig|||主题对象|

|**示例**|
|---|

new ThemeConfig().setNumberAlignRuleOption({ 

middle: { anchor: '__container__', align: HorizontalAlign.Center }, top: { anchor: '__container__', align: VerticalAlign.Top} }) 

## **ThemeConfig.setNumberColor** 

setNumberColor(value: ResourceColor): ThemeConfig 

#### 设置号码字体颜色 

### **参数:** 

|**参数名**|**类型**|**必填**|**说明**|
|---|---|---|---|
|value|ResourceColor|是|号码字体颜色|

### **返回值:** 

|**类型**|**说明**|
|---|---|
|ThemeConfig|主题对象|

### **示例** 

new ThemeConfig().setNumberColor('#ffffff') 

## **ThemeConfig.setLogBtnText** 

setLogBtnText(value: string): ThemeConfig 

设置登录按钮文本内容 

### **参数:** 

|**参数名**|**类型**|**必填**|**说明**|
|---|---|---|---|
|value|string|是|登录按钮文本内容|

### **返回值:** 

|**类型**|**说明**|
|---|---|
|ThemeConfig|主题对象|

### **示例** 

```typescript 

new ThemeConfig().setLogBtnText('本机号码一键登录') 

```

## **ThemeConfig.setLoginBtnTextSize** 

setLoginBtnTextSize(value: number): ThemeConfig 

设置授权登录文本字体大小 

### **参数:** 

|**参数名**|**类型**|**必填**|**说明**|
|---|---|---|---|
|value|number|是|授权登录文本字体大小|
|**返回值:**||||
|**类型**|||**说明**|
|ThemeConfig|||主题对象|

### **示例** 

new ThemeConfig().setLoginBtnTextSize(18) 

## **ThemeConfig.setLoginBtnTextColor** 

setLoginBtnTextColor(value: ResourceColor): ThemeConfig 

设置授权登录按钮字体颜色 

### **参数:** 

|**参数名**|**类型**|**必填**|**说明**|
|---|---|---|---|
|value|ResourceColor|是|授权登录按钮字体颜色|

### **返回值:** 

|**类型**|**说明**|
|---|---|
|ThemeConfig|主题对象|

### **示例** 

new ThemeConfig().setLoginBtnTextColor('#ffffff') 

## **ThemeConfig.setLoginBtnColor** 

setLoginBtnColor(value: ResourceColor): ThemeConfig 

设置登录按钮背景颜色 

### **参数:** 

参数名 类型 必填 说明
value ResourceColor 是 登录按钮背景颜色
返回值:
类型 说明
ThemeConfig 主题对象
示例

new ThemeConfig().setLoginBtnColor('#ffffff') 

## **ThemeConfig.setLoginBtnImgPath** 

setLoginBtnImgPath(value: ResourceStr|undefined): ThemeConfig 

设置登录按钮背景图片 

### **参数:** 

参数名 类型 必填 说明
value ResourceStr undefined 是
返回值:
类型 说明
ThemeConfig 主题对象
示例

new ThemeConfig().setLoginBtnImgPath($r('app.media.btn_nor')) 

# **ThemeConfig.setLoginBtnWidth** 

setLoginBtnWidth(value: Length): ThemeConfig 

#### 设置登录按钮宽度 

### **参数:** 

|**参数名**|**类型**|**必填**|**说明**|
|---|---|---|---|
|value|ResourceStr|undefined|是|

### **返回值:** 

|**类型**|**说明**|
|---|---|
|ThemeConfig|主题对象|

### **示例** 

new ThemeConfig().setLoginBtnWidth('200') 

## **ThemeConfig.setLoginBtnHeight** 

setLoginBtnHeight(value: Length): ThemeConfig 

#### 设置登录按钮高度 

### **参数:** 

|**参数名**|**类型**|**必填**|**说明**|
|---|---|---|---|
|value|Length|是|登录按钮高度|

### **返回值:** 

|**类型**|**说明**|
|---|---|
|ThemeConfig|主题对象|

### **示例** 

new ThemeConfig().setLoginBtnHeight('200') 

## **ThemeConfig.setLoginBtnMargin** 

setLoginBtnMargin(value: Margin): ThemeConfig 

设置登录按钮边缘边距 

**参数:** 

|**参数名**|**类型**|**必填**|**说明**|
|---|---|---|---|
|value|Margin|是|登录按钮边缘边距|

### **返回值:** 

|**类型**|**说明**|
|---|---|
|ThemeConfig|主题对象|

### **示例** 

new ThemeConfig().setLoginBtnMargin({ top:10 }) 

## **ThemeConfig.setLoginBtnAlignRuleOption** 

setLoginBtnAlignRuleOption(value: AlignRuleOption): ThemeConfig 

设置登录按钮相对布局偏移规则 

### **参数:** 

|**参数名**|**类型**|**必填**|**说明**|
|---|---|---|---|
|value|AlignRuleOption|是|录按钮相对布局偏移规则|

### **返回值:** 

|**类型**|**说明**|
|---|---|
|ThemeConfig|主题对象|

### **示例** 

new ThemeConfig().setLoginBtnAlignRuleOption({ 

middle: { anchor: '__container__', align: HorizontalAlign.Center }, top: { anchor: '__container__', align: VerticalAlign.Top} }) 

## **ThemeConfig.setCheckedLoginListener** 

setCheckedLoginListener(value:CheckedLoginListener|undefined): ThemeConfig 

设置勾上同意隐私协议框时的登录按钮点击监听事件 

**参数:** 

|**参数名**|**类型**|**必填**|**说明**|
|---|---|---|---|
|value|CheckedLoginListener|undefined|是|

### **返回值:** 

|**类型**|**说明**|
|---|---|
|ThemeConfig|主题对象|

### **示例** 

new ThemeConfig().setCheckedLoginListener({ onLoginClickStart(context: UIContext) { //开始登录授权 

} , onLoginClickComplete(context: UIContext) { 

//登录授权响应完成 } }) 

## **ThemeConfig.setUncheckedLoginListener** 

setUncheckedLoginListener(value: UncheckedLoginListener |undefined): ThemeConfig 

设置未勾上同意隐私协议框时的登录按钮点击监听事件,可以自己定义确认框,并使用SetCheckCallback控制勾选 上框并点击登录 

### **参数:** 

|**参数名**|**类型**|**必填**|**说明**|
|---|---|---|---|
|value|UncheckedLoginListener|undefined|是|

### **返回值:** 

|**类型**|**说明**|
|---|---|
|ThemeConfig|主题对象|

### **示例** 

new ThemeConfig().setUncheckedLoginListener({ 

onAuthLoginListener(context: UIContext, callBack: SetCheckCallback) { promptAction.showDialog({ 

message: '是否登录授权', 

buttons: [ { 

text: '确定', color: '#000000' }, { text: '取消', color: '#000000' } ], }) .then(data => { if (data.index == 0) { callBack.onAuthLoginCallBack(true) } else { callBack.onAuthLoginCallBack(false) } }) } }) 

## **ThemeConfig.setLoginPageComponent** 

setLoginPageComponent(component: (() => void)|undefined): ThemeConfig 

设置授权页布局自定义组件 

### **参数:** 

|**参数名**|**类型**|**必填**|**说明**|
|---|---|---|---|
|value|(() => void)|undefined|是|

### **返回值:** 

|**类型**|**说明**|
|---|---|
|ThemeConfig|主题对象|

### **示例** 

new ThemeConfig().setLoginPageComponent(authPageComponent) 

```arkts
@Builder function authPageComponent(): void { Column() { Text('自定义布局') .fontSize(40) .alignRules({ middle: { anchor: '__container__', align: HorizontalAlign.Center }, top: { anchor: '__container__', align: VerticalAlign.Top }, 
```

}) Button('自定义按钮') .alignRules({ middle: { anchor: '__container__', align: HorizontalAlign.Center }, top: { anchor: '__container__', align: VerticalAlign.Top }, }).margin({top:'150%'}).onClick(()=>{ showToast("click") }) }.width('100%') .height('100%') .alignRules({ top: { anchor: '__container__', align: VerticalAlign.Top }, bottom: { anchor: '__container__', align: VerticalAlign.Bottom }, left:{ anchor: '__container__', align: HorizontalAlign.Start } }) } 

## **ThemeConfig.setCheckBox** 

setCheckBox(width: Length, height: Length): ThemeConfig 

设置隐私条款勾选框宽高 

### **参数:** 

|**参数名**|**类型**|**必填**|**说明**|
|---|---|---|---|
|width|Length|是|勾选框宽度|
|height|Length|是|勾选框高度|

### **返回值:** 

|**类型**|**说明**|
|---|---|
|ThemeConfig|主题对象|

### **示例** 

new ThemeConfig().setCheckBox(15, 15) 

## **ThemeConfig.setCheckBoxMargin** 

setCheckBoxMargin(value: Margin): ThemeConfig 

设置隐私条款勾选框偏移边距 

**参数:** 

|**参数名**|**类型**|**必填**|**说明**|
|---|---|---|---|
|value|Margin|是|勾选框边距|

### **返回值:** 

|**类型**|**说明**|
|---|---|
|ThemeConfig|主题对象|

### **示例** 

new ThemeConfig().setCheckBoxMargin({ top:10 }) 

## **ThemeConfig.setCheckBoxAlignRuleOption** 

setCheckBoxAlignRuleOption(value: AlignRuleOption): ThemeConfig 

设置隐私条款勾选框相对布局偏移规则 

### **参数:** 

|**参数名**|**类型**|**必填**|**说明**|
|---|---|---|---|
|value|AlignRuleOption|是|隐私条款勾选框相对布局偏移规则|

### **返回值:** 

|**类型**|**说明**|
|---|---|
|ThemeConfig|主题对象|

### **示例** 

new ThemeConfig().setCheckBoxAlignRuleOption({ top: { anchor: '__container__', align: VerticalAlign.Top }, bottom: { anchor: '__container__', align: VerticalAlign.Bottom }, left:{ anchor: '__container__', align: HorizontalAlign.Start } }) 

## **ThemeConfig.setCheckBoxShape** 

setCheckBoxShape(value: CheckBoxShape): ThemeConfig 

设置勾选框类型(圆⻆矩形/圆形) 

### **参数:** 

|**参数名**|**类型**|**必填**|**说明**||
|---|---|---|---|---|
|value|CheckBoxShape|是|勾选框类型|(圆⻆矩形/圆形)|

### **返回值:** 

|**类型**|**说明**|
|---|---|
|ThemeConfig|主题对象|

### **示例** 

new ThemeConfig().setCheckBoxShape(CheckBoxShape.CIRCLE) 

## **ThemeConfig.setCheckBoxChangeListener** 

setCheckBoxChangeListener(value: CheckBoxChangeListener|undefined): ThemeConfig 

设置授权页勾选框是否勾选的监听事件 

### **参数:** 

|**参数名**|**类型**|**必填**|**说明**|
|---|---|---|---|
|value|CheckBoxChangeListener|undefined|是|

### **返回值:** 

|**类型**|**说明**|
|---|---|
|ThemeConfig|主题对象|

### **示例** 

new ThemeConfig().setCheckBoxChangeListener({ onCheckedChanged(b: boolean) { //勾选框状态 + b 

} }) 

## **ThemeConfig.setClauseState** 

setClauseState(value: boolean): ThemeConfig 

设置隐私条款勾选框勾选状态 

### **参数:** 

|**参数名**|**类型**|**必填**|**说明**|
|---|---|---|---|
|value|boolean|是|隐私条款勾选框勾选状态|

### **返回值:** 

|**类型**|**说明**|
|---|---|
|ThemeConfig|主题对象|

### **示例** 

new ThemeConfig().setClauseState(false) 

## **ThemeConfig.setClauses** 

setClauses(value: Array<ClauseSpan>): ThemeConfig 

设置隐私条款的协议文本,自定义条款,自定义条款链接、字体颜色 

### **参数:** 

|**参数名**|**类型**|**必填**|**说明**|
|---|---|---|---|
|value|Array<ClauseSpan>|是|隐私条款的协议文本,自定义条款,自定义条款链接、字体颜 色|

### **返回值:** 

|**类型**|**说明**|
|---|---|
|ThemeConfig|主题对象|

### **示例** 

//使用ClauseSpan[]的形式,长度最多3个,按顺序展示,其中type = ClauseSpan.NORMAL为普通文本 

//,type = ClauseSpan.OPERATOR_PROTOCOL为隐私协议入口,因合规原因,此时text、url随便填写不会生效, 内部会转为运营商定义的标题和隐私链接,点击会跳转隐私协议页面 

//,type = ClauseSpan.CUSTOM_PROTOCOL为自定义协议入口,点击会跳转对应的url页面 

new ThemeConfig().setClauses([{ 

text: "登录即同意", 

type: ClauseSpan.NORMAL, fontColor: '#ff3680ec', fontSize: 15, fontWeight: FontWeight.Bold 

}, { text: "", type: ClauseSpan.OPERATOR_PROTOCOL, fontColor: '#ff15468d', fontSize: 15, fontWeight: FontWeight.Bold }, { text: "自定义协议", type: ClauseSpan.CUSTOM_PROTOCOL, fontColor: '#ffd23064', fontSize: 15, fontWeight: FontWeight.Bold, url : "http://www.baidu.com" }]) 

## **ThemeConfig.setClauseMargin** 

setClauseMargin(value: Margin): ThemeConfig 

#### 设置隐私条款偏移边距 

### **参数:** 

|**参数名**|**类型**|**必填**|**说明**|
|---|---|---|---|
|value|Margin|是|隐私条款偏移边距|

### **返回值:** 

|**类型**|**说明**|
|---|---|
|ThemeConfig|主题对象|

### **示例** 

new ThemeConfig().setClauseMargin({ top:10 }) 

## **ThemeConfig.setClauseAlignRuleOption** 

setClauseAlignRuleOption(value: AlignRuleOption): ThemeConfig 

设置隐私条款相对布局偏移规则 

**参数:** 

|**参数名**|**类型**|**必填**|**说明**|
|---|---|---|---|
|value|AlignRuleOption|是|隐私条款相对布局偏移规则|

### **返回值:** 

|**类型**|**说明**|
|---|---|
|ThemeConfig|主题对象|

### **示例** 

new ThemeConfig().setClauseAlignRuleOption({ 'bottom': { 'anchor': '__container__', 'align': VerticalAlign.Bottom }, 'middle': { 'anchor': '__container__', 'align': HorizontalAlign.Center }, }) 

## **ThemeConfig.setNavTextSize** 

setNavTextSize(value: number): ThemeConfig 

设置服务条款标题字体大小 

### **参数:** 

|**参数名**|**类型**|**必填**|**说明**|
|---|---|---|---|
|value|number|是|服务条款标题字体大小|

### **返回值:** 

|**类型**|**说明**|
|---|---|
|ThemeConfig|主题对象|

### **示例** 

new ThemeConfig().setNavTextSize(18) 

## **ThemeConfig.setNavTextColor** 

setNavTextColor(value: ResourceColor): ThemeConfig 

设置服务条款标题字体颜色 

**参数:** 

|**参数名**|**类型**|**必填**|**说明**|
|---|---|---|---|
|value|ResourceColor|是|服务条款标题字体颜色|

### **返回值:** 

|**类型**|**说明**|
|---|---|
|ThemeConfig|主题对象|

### **示例** 

new ThemeConfig().setNavTextColor('#ffffff') 

## **ThemeConfig.setNavColor** 

setNavColor(value: ResourceColor): ThemeConfig 

#### 设置服务条款标题颜色 

### **参数:** 

|**参数名**|**类型**|**必填**|**说明**|
|---|---|---|---|
|value|ResourceColor|是|服务条款标题字体颜色|
|**类型返回值:**|||**说明**|
|ThemeConfig|||主题对象|
|**示例**||||

new ThemeConfig().setNavColor('#ffffff') 

## **ThemeConfig.setClauseComponent** 

setClauseComponent(component: (() => void)|undefined): ThemeConfig 

设置服务条款标题栏自定义组件,该自定义组件是以替换默认标题的形式来展示 

### **参数:** 

|**参数名**|**类型**|**必填**|**说明**|
|---|---|---|---|
|component|(() => void)|undefined|是|

### **返回值:** 

|**类型**|**说明**|
|---|---|
|ThemeConfig|主题对象|

### **示例** 

new ThemeConfig().setClauseComponent(clauseComponent) 

```arkts
@Builder function clauseComponent(): void { Column() { Text('自定义协议页标题栏') .fontSize(20) .alignRules({ middle: { anchor: '__container__', align: HorizontalAlign.Center }, center: { anchor: '__container__', align: VerticalAlign.Center }, }) }.width('100%') .height(50) } 
```

## **ThemeConfig.useDialogMode** 

useDialogMode(value?:DialogOptions):ThemeConfig 

#### 弹窗模式 

### **参数:** 

|**参数名**|**类型**|**必填**|**说明**|
|---|---|---|---|
|value|DialogOptions|否|弹窗参数,传入类型参数参考CustomDialogControllerOptions|

### **返回值:** 

**类型 说明** ThemeConfig 主题对象 

### **示例** 

new ThemeConfig().useDialogMode({ alignment: DialogAlignment.Center, width: '100%', height: '80%' }) 

## **ThemeConfig.setBackPressedListener** 

setBackPressedListener(value: BackListener|undefined): ThemeConfig 

设置授权页返回键监听事件 

### **参数:** 

|**参数名**|**类型**|**必填**|**说明**|
|---|---|---|---|
|value|BackListener|undefined|是|
|**返回值:**||||
|**类型**||**说明**||
|ThemeConfig||主题对象||

### **示例** 

new ThemeConfig().setBackPressedListener({ onBackPressed: () => { //返回键监听 } }) 

## **FlyVerify.closeAuthLoginPage** 

closeAuthLoginPage():void 

关闭授权页 

### **参数:** 

|**参数名**|**类型**|**必填**|**说明**|
|---|---|---|---|
|**返回值:**||||
|**类型**||**说明**||
|void||||

### **示例** 

FlyVerify.closeAuthLoginPage()
