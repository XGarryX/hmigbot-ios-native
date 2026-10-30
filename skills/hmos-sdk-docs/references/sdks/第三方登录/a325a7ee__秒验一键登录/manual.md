# **SDK-集成** 

## **一** **.添加SDK依赖** 

在 **Terminal** 窗口中,执行如下命令进行安装 

ohpm install @zztsdk/zztcore 

ohpm install @zztsdk/flyverify 

在我方官网下载运营商har放入工程中,移动运营商har必须集成,否则会引起异常 

使用命令进行安装 

//安装电信sdk ohpm install EAccountApiHarmonyOS_V1.0.6.har //安装联通sdk ohpm install unicom_login_harmony_v1.0.3AR001B1030.har //安装移动sdk ohpm install quick_login_harmony_5.9.7.1.har 

#### 在项目级的build-profile.json5中添加必要属性 

1. OpenHarmony SDK API version 12 开始支持。 

2. 使用useNormalizedOHMUrl以支持运营商的字节码har 

"app": { "products": [ { "compatibleSdkVersion":"5.0.0(12)", "buildOption":{ "strictMode":{ "useNormalizedOHMUrl":true } } } ] } 

## **二.权限** 

ohos.permission.GET_NETWORK_INFO //获取网络状态 ohos.permission.INTERNET //业务请求 

## **三.导入模块** 

import { ZztSDK } from '@zztsdk/zztcore'; 

import FlyVerify from '@zztsdk/flyverify'; 

## **四.使用说明** 

本模块首批接口从 OpenHarmony SDK API version 12 开始支持。 

#### 1. 初始化: 

ZztSDK.init(context, this.appkey, this.secret) context请在@Component页面中通过let context = getContext(this)获取 请勿在UIAbility中用this.context获取,否则会影响主题设置 

#### 2. 同意隐私: 

ZztSDK.submitPolicyGrantResult(true) 

#### 3. 预取号回调方式: 

```arkts
let callback: OperationCallback<void> = { onSuccess: () => { let result = new Date() + " onSuccess" }, onFailure: (e) => { let result = new Date() + " onFailure:" + JSON.stringify(e) } }; FlyVerify.preVerify(callback); 
```

#### 4. 预取号promise方式: 

FlyVerify.preVerify().then((data)=>{ let result = new Date() + " onSuccess" 

}).catch((e:VerifyException)=>{ let result = new Date() + " onFailure:" + JSON.stringify(e) }) 

#### 5. 打开授权页回调方式: 

```arkts
let callback: OperationCallback<VerifyResult> = { onSuccess: (data) => { this.content = new Date() + " onSuccess:" + JSON.stringify(data) this.result = data; }, onFailure: (error) => { this.content = new Date() + " onFailure:" + JSON.stringify(error) } }; FlyVerify.verify(callback); 
```

#### 5.1 取号结果: 

VerifyResult{ //运营商名称: CUCC->中国联通, CTCC->中国电信, CMCC->中国移动 operator:string; //脱敏号码 securityPhone:string; //见3.1 uiElement:UiElement; //运营商token opToken:string; //token token:string; } 

#### 6. 打开授权页promise方式: 

FlyVerify.verify().then((data)=>{ this.content = new Date() + " onSuccess:" + JSON.stringify(data) this.result = data; }).catch((e:VerifyResult)=>{ this.content = new Date() + " onFailure:" + JSON.stringify(e) }); 

#### 7. 设置预取号超时: 

//timeout毫秒时间 FlyVerify.setPreVerifyTimeout(timeout); 

## **五.授权页ui相关** 

### **设置ui主题** 

#### 1. 创建主题,设置需要的属性,可使用链式设置多个属性 

let theme = new ThemeConfig().setNumberSize(18).setLogBtnText('本机号码一键登录')... 

#### 2. 传入主题 

FlyVerify.setTheme(theme) 

### **状态栏** 

1. 设置窗口内导航栏、状态栏属性,参数是window.SystemBarProperties 

new ThemeConfig().setSystemBarProperties({ statusBarColor: '#ffffff', statusBarContentColor: '#000000' }) 

### **号码** 

#### 1. 设置号码栏字体大小 

new ThemeConfig().setNumberSize(18) 

#### 2. 设置号码栏偏移量 

new ThemeConfig().setNumberMargin({ top:10 }) 

#### 3. 设置号码栏相对布局偏移规则 

new ThemeConfig().setNumberAlignRuleOption({ 

middle: { anchor: '__container__', align: HorizontalAlign.Center }, top: { anchor: '__container__', align: VerticalAlign.Top} }) 

#### 4. 设置号码字体颜色 

new ThemeConfig().setNumberColor('#ffffff') 

### **登录按钮** 

#### 1. 设置登录按钮文本内容 

new ThemeConfig().setLogBtnText('本机号码一键登录') 

#### 2. 设置授权登录文本字体大小 

new ThemeConfig().setLoginBtnTextSize(18) 

#### 3. 设置授权登录按钮字体颜色 

new ThemeConfig().setLoginBtnTextColor('#ffffff') 

#### 4. 设置登录按钮背景颜色 

new ThemeConfig().setLoginBtnColor('#ffffff') 

5. 设置登录按钮背景图片,图片会覆盖在setLoginBtnColor效果上面,建议setLoginBtnColor和 setLoginBtnImgPath二选一 

new ThemeConfig().setLoginBtnImgPath($r('app.media.btn_nor')) 

#### 6. 设置登录按钮宽度 

new ThemeConfig().setLoginBtnWidth('200') 

#### 7. 设置登录按钮高度 

new ThemeConfig().setLoginBtnHeight('200') 

#### 8. 设置登录按钮边缘边距 

new ThemeConfig().setLoginBtnMargin({ top:10 }) 

#### 9. 设置登录按钮相对布局偏移规则 

new ThemeConfig().setLoginBtnAlignRuleOption({ middle: { anchor: '__container__', align: HorizontalAlign.Center }, top: { anchor: '__container__', align: VerticalAlign.Top} }) 

#### 10. 设置勾上同意隐私协议框时的登录按钮点击监听事件 

new ThemeConfig().setCheckedLoginListener({ onLoginClickStart(context: UIContext) { //开始登录授权 } , onLoginClickComplete(context: UIContext) { //登录授权响应完成 } }) 

11. 设置未勾上同意隐私协议框时的登录按钮点击监听事件,可以自己定义确认框,并使用SetCheckCallback控 制勾选上框并点击登录 

new ThemeConfig().setUncheckedLoginListener({ onAuthLoginListener(context: UIContext, callBack: SetCheckCallback) { promptAction.showDialog({ message: '是否登录授权', buttons: [ { text: '确定', color: '#000000' }, { text: '取消', color: '#000000' } ], }) .then(data => { if (data.index == 0) { callBack.onAuthLoginCallBack(true) } else { callBack.onAuthLoginCallBack(false) } }) } }) 

### **授权页自定义组件** 

1. 设置授权页布局自定义组件,只能设置一个组件,后设置覆盖之前的,可用一个容器组件实现多组件场景 

```arkts
new ThemeConfig().setLoginPageComponent(authPageComponent) @Builder function authPageComponent(): void { Column() { Text('自定义布局') .fontSize(40) .alignRules({ middle: { anchor: '__container__', align: HorizontalAlign.Center }, top: { anchor: '__container__', align: VerticalAlign.Top }, }) Button('自定义按钮') .alignRules({ middle: { anchor: '__container__', align: HorizontalAlign.Center }, top: { anchor: '__container__', align: VerticalAlign.Top }, }).margin({top:'150%'}).onClick(()=>{ 
```

showToast("click") }) }.width('100%') .height('100%') .alignRules({ top: { anchor: '__container__', align: VerticalAlign.Top }, bottom: { anchor: '__container__', align: VerticalAlign.Bottom }, left:{ anchor: '__container__', align: HorizontalAlign.Start } }) } 

### **勾选框** 

#### 1. 设置隐私条款勾选框宽高 

new ThemeConfig().setCheckBox(15, 15) 

#### 2. 设置隐私条款勾选框偏移边距 

new ThemeConfig().setCheckBoxMargin({ top:10 }) 

#### 3. 设置隐私条款勾选框相对布局偏移规则 

new ThemeConfig().setCheckBoxAlignRuleOption({ top: { anchor: '__container__', align: VerticalAlign.Top }, bottom: { anchor: '__container__', align: VerticalAlign.Bottom }, left:{ anchor: '__container__', align: HorizontalAlign.Start } }) 

#### 4. 设置勾选框类型(圆⻆矩形/圆形) 

new ThemeConfig().setCheckBoxShape(CheckBoxShape.CIRCLE) 

#### 5. 设置授权页勾选框是否勾选的监听事件 

new ThemeConfig().setCheckBoxChangeListener({ onCheckedChanged(b: boolean) { //勾选框状态 + b } }) 

#### 6. 设置隐私条款勾选框勾选状态 

new ThemeConfig().setClauseState(false) 

### **隐私协议入口** 

1. 设置隐私条款的协议文本,自定义条款,自定义条款链接、字体颜色 

   - ,使用ClauseSpan[]的形式,长度最多3个,按顺序展示,其中type = ClauseSpan.NORMAL为普通文本 

   - ,type = ClauseSpan.OPERATOR_PROTOCOL为隐私协议入口,因合规原因,此时text、url随便填写不会生 效,内部会转为运营商定义的标题和隐私链接,点击会跳转隐私协议页面 

   - ,type = ClauseSpan.CUSTOM_PROTOCOL为自定义协议入口,点击会跳转对应的url页面 

new ThemeConfig().setClauses([{ text: "登录即同意", type: ClauseSpan.NORMAL, fontColor: '#ff3680ec', fontSize: 15, fontWeight: FontWeight.Bold }, { text: "", type: ClauseSpan.OPERATOR_PROTOCOL, fontColor: '#ff15468d', fontSize: 15, fontWeight: FontWeight.Bold }, { text: "自定义协议", type: ClauseSpan.CUSTOM_PROTOCOL, fontColor: '#ffd23064', fontSize: 15, fontWeight: FontWeight.Bold, url : "http://www.baidu.com" }]) 

#### 2. 设置隐私条款偏移边距 

new ThemeConfig().setClauseMargin({ top:10 }) 

#### 3. 设置隐私条款相对布局偏移规则 

new ThemeConfig().setClauseAlignRuleOption({ 'bottom': { 'anchor': '__container__', 'align': VerticalAlign.Bottom }, 'middle': { 'anchor': '__container__', 'align': HorizontalAlign.Center }, }) 

### **隐私条款页** 

#### 1. 设置服务条款标题字体大小 

new ThemeConfig().setNavTextSize(18) 

#### 2. 设置服务条款标题字体颜色 

new ThemeConfig().setNavTextColor('#ffffff') 

#### 3. 设置服务条款标题颜色 

new ThemeConfig().setNavColor('#ffffff') 

#### 4. 设置服务条款标题栏自定义组件,该自定义组件是以替换默认标题的形式来展示 

```arkts
new ThemeConfig().setClauseComponent(clauseComponent) @Builder function clauseComponent(): void { Column() { Text('自定义协议页标题栏') .fontSize(20) .alignRules({ middle: { anchor: '__container__', align: HorizontalAlign.Center }, center: { anchor: '__container__', align: VerticalAlign.Center }, }) }.width('100%') .height(50) } 
```

### **其他** 

#### 1. 弹窗模式,传入类型参数参考CustomDialogControllerOptions 

new ThemeConfig().useDialogMode({ alignment: DialogAlignment.Center, width: '100%', height: '80%' }) 

#### 2. 设置授权页返回键监听事件 

new ThemeConfig().setBackPressedListener({ onBackPressed: () => { //返回键监听 } })
