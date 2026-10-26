# **一** **键认证SDK API接口** 

本文档仅适用于GY-HM-1.0.3及以上版本。 

## **1. 结果回调** 

### **接口说明** 

大部分gysdk接口,执行的结果都通过 Promise<GyResponse> 进行回调通知。 

//如初始化接口 public init(config: GyConfig): Promise<GyResponse> 

### **参数说明** 

public class GyResponse { /* 个验用户唯一标识 */ getGyuid(): string; /* 接口请求是否成功 */ isSuccess(): boolean; /* code 返回结果,30000为成功,详见状态码说明,代码引用可参考 GyCode */ getCode(): number; 

/* data 返回结果详情,为json格式,包含errorCode、errorDesc、metadata、及其他业务自定义的字段 * - errorCode 错误码,0为成功,详见状态码说明,代码引用可参考 GyErrorCode * - errorDesc 错误描述 

* - metadata 原始信息,比如运营商/服务器的原始返回信息、异常出错信息等等 */ getData(): Record<string, Object>; 

/* 请求的运营商,CM 移动、CT 电信、CU 联通 */ getOperator(): string; /** * 请求成功的耗时,失败时为-1 */ getCostTime(): number; } 

### **调用示例** 

```arkts
const response = await GyManager.getInstance().init(new GyConfig(getContext()) .setDebug(false) .setPreLoginUseCache(true) .setChannel("huawei")) if (response.isSuccess()) { hilog.info(0x0000, "GY", `init success ==>${response}`) } else { hilog.info(0x0000, "GY", `init failed==>${response}`) } 
```

### **返回示例** 

#### 返回成功,解析对应业务的自定义字段 

返回失败,解析 msg.errorCode、msg.errorDesc 了解详细失败原因 

##### 初始化成功 

{ "costTime": 81, "gyuid": "gtc_eafb4e7ddbfe059a3eaebde0c6ef858030", "code": 30000, "operator": "CT", "data": { "errorCode": 0, "errorDesc": "gysdk success!", "operatorType": 3, "processId": "e031130b158417d38324c48adf3829cf" }, "success": true } 初始化失败 { "costTime": -1, "gyuid": "gtc_eafb4e7ddbfe059a3eaebde0c6ef858030", "code": 30004, "operator": "", "data": { "errorCode": -20101, "errorDesc": "gysdk appid为空!", "operatorType": 0, "processId": "a4ad9fb60e278cd023a1b815a4f4bbc7" }, "success": false } 

## **2. 初始化** 

**接口说明** 

建议在 EntryAbility.onCreate()中判断用户已经同意隐私政策后初始化gysdk,读取配置参数并注册GYUID 

/** * 初始化sdk接口。 * @param gyConfig 初始化配置. */ public init(config: GyConfig): Promise<GyResponse> 

### **调用示例** 

//必须传入context上下文 const response = await GyManager.getInstance().init(new GyConfig(getContext()) //非必选 .setDebug(false) 

//非必选,此处设置的appid优先级高于优先级高于module.json5中配置的 GETUI_APPID 

" .setAppid( 个推平台的appid") 

//非必选 

.setPreLoginUseCache(true) 

//非必选,此处设置的channel优先级高于module.json5中配置的 GT_INSTALL_CHANNEL 

.setChannel("huawei")) 

## **3. 版本信息** 

### **接口说明** 

获取gysdk版本信息。 

/** * 获取版本号. * @return version 版本号. */ public getVersion(): string; 

### **调用示例** 

GyManager.getInstance().getVersion(); 

## **4. 预登录** 

### **接口说明** 

在调用一键登录接口之前,必须先预登录,预登录成功之后才可以一键登录。 

/** 

- 预登录,每次调用都会有且只有一次回调。连续多次调用,后面的会等第一次完成后返回相同的结果。调用init 

- 紧接着就可以调用ePreLogin,sdk内部会自行等待init完成再预登录。 

* @param timeout    超时时间,一般5000~15000ms,<=0则使用15s,建议设为5000ms以上(在不影响用 户体验的地方比如EntryAbility.onCreate中调用,建议设置的更长一些比如8000ms) 

*/ 

public ePreLogin(timeout: number): Promise<GyResponse> 

#### **注意:** 

- 预登录是一个耗时操作,我们建议开发者提前进行预登录,例如在EntryAbility.onCreate初始化gysdk之后、 闪屏页面或者其他任何地方,这样可以在调用一键登录的时候节省用户等待的时间; 

- 预登录成功表示当前设备可以使用一键登录,失败则表示不可用,开发者在失败的时候可以进行重试、或者换 成其他登录方式; 

- 预登录的结果在一定时间内有效,具体的有效期会在预登录成功的结果里面返回(一般移动电信电信一小时有 效);预登录的结果只能用于一次一键登录,一键登录成功之后需要再次进行预登录; SDK提供了 isPreLoginResultValid 接口来帮助开发者判断当前的预登录结果是否有效。 

### **调用示例** 

const isValid = await GyManager.getInstance().isPreLoginResultValid(); if (!isValid) { 

//预登录无效,调用预登录接口 const response = await GyManager.getInstance().ePreLogin(5000); if (response.isSuccess()) { hilog.info(0x0000, "GY", `preLogin success ==>${response}`) } else { hilog.info(0x0000, "GY", `preLogin failed==>${response}`) } } 

### **返回示例** 

返回成功,调用登录 

返回失败,解析data.errorCode、data.errorDesc了解详细失败原因 

预登录成功 { "costTime": 862, "gyuid": "gtc_eafb4e7ddbfe059a3eaebde0c6ef858030", "code": 30000, "operator": "CT", "data": { "errorCode": 0, "errorDesc": "gysdk success!", "operatorType": 3, "processId": "000a9b675ceeb997f425291687213b8a", "expiredTime": 1731489627313, "number": "191****1003" 

}, "success": true } 

预登录失败 

{ "costTime": -1, "gyuid": "gtc_eafb4e7ddbfe059a3eaebde0c6ef858030", "code": 30004, "operator": "CT", "data": { "errorCode": -20102, "errorDesc": "gysdk appid或者签名无效!", "operatorType": 3, "processId": "2346ea4e36e3ad3dd481e6c440831885", "metadata": "{\"errno\":0,\"data\":{\"msg\":\"应用无效,应用不存在 \",\"result\":\"40004\"}}" }, "success": false } 

## **5. 预登录是否有效** 

### **接口说明** 

在再次预登录、或者一键登录之前判断是否已经有效预登录。 

/** * 判断预登录结果是否有效. */ public isPreLoginResultValid(): Promise<boolean> 

### **调用示例** 

//见上面“预登录”调用示例 

## **一** **6. 键登录** 

### **接口说明** 

使用 GyAuthThemeConfig 参数的传入登录接口,可由开发者自行配置页面的样式 

/** 

* 一键登录,app启动Page授权页、预登录成功、设置好隐私协议之后调用 

* sdk需要对授权页设置OnAuthLoginPageListener自定义监听 

* 

* @param timeout 一键登录请求运营商的超时时间. 

* @param config 自定义全局配置接口,用来配置授权页面 UI 样式 */ 

public eAccountLogin(timeout: number, config: GyAuthThemeConfig): Promise<GyResponse> { 

return GyAuthLoginManager.getInstance().eAccountLogin(timeout, config) } 

#### **注意:** 

- 一般是在进入授权页前,先判断预登录有效/无效时候预登录返回成功后,再调用接口 登录成功会回调成功,登录失败或者监听到授权页被销毁都会回调失败。 

- **请务必严格遵循** 《授权页规范》,设置必要元素:号码栏(NumberTextview),品牌露出(SloganTextview), 登录按钮(LoginButton),隐私确认(PrivacyCheckbox),隐私标题(PrivacyTextview); 

### **参数说明** 

GyAuthThemeConfig 是控制页面样式、页面监听、隐私协议等的配置参数,开发者可根据需求自行设置; 

config内置了默认样式,直接传入new GyAuthThemeConfig()展示的就是默认演示 

|**方法**|**参数类型**|**说明**|**默认值**|
|---|---|---|---|
|方法|参数类型|说明|默认值|
|setSystemBarProperties|SystemBarProperties|设置窗口内导航栏、状态栏属性。|无|
|setLoginPageComponent|() => void|设置授权页布局自定义View|无|
|setPrivacyNavTextSize|number|设置服务条款标题字体大小|18|
|setPrivacyNavTextColor|ResourceColor|设置服务条款标题字体颜色|Color.White|
|setPrivacyNavColor|ResourceColor|设置服务条款标题栏颜色|#0086d0|
|setPrivacyNavHeight|Length|设置服务条款标题栏高度|50|
|setLogoWidth|Length|授权页logo的宽度|80|
|setLogoHeight|Length|授权页logo的高度|80|
|setLogoImgPath|ResourceStr|授权页logo的图片|gy_login_logo|
|setLogoMargin|Margin|授权页logo的偏移|-|
|setLogoAlignRuleOption|AlignRuleOption|授权页logo的对齐规则|-|
|setNumberSize|number|设置号码栏字体大小|28|
|setNumberColor|ResourceColor|设置手机号码字体颜色|#FF3D424C|
|setNumberMargin|Margin|设置号码栏偏移|-|
|setNumberAlignRuleOption|AlignRuleOption|设置号码栏对齐规则|-|
|setSloganTextColor|ResourceColor|设置标语字体颜色|#FFA8A8A8|
|setSloganTextSize|number|设置标语字体大小|12|
|setSloganMargin|Margin|设置标语边距|-|
|setSloganAlignRuleOption|AlignRuleOption|设置标语对齐规则|-|
|setLoginBtnText|ResourceStr|设置登录按钮文本内容|"本机号码一键登录"|

|setLoginBtnTextSize|number 设置授权登录文本字体大小|18|
|---|---|---|
|setLoginBtnTextColor|ResourceColor 设置授权登录按钮字体颜色|Color.White|
|setLoginBtnColor|ResourceColor 设置登录按钮背景颜色|#FF3973FF|
|setLoginBtnWidth|Length 设置登录按钮宽度|70%|
|setLoginBtnHeight|Length 设置登录按钮高度|50|
|setLoginBtnMargin|Margin 设置登录按钮偏移|-|
|setLoginBtnAlignRuleOption|AlignRuleOption 设置登录按钮对齐规则|-|
|setOnAuthLoginPageListener|OnAuthLoginPageListener 设置授权页面监听onLoginPageInComplete授权页成功拉起 onLoginClickStart点击登录开始onLoginClickComplete点击登录结 束onBackPressed按下返回键注意:窗口模式不支持 onCheckedChanged (checked)授权页勾选框状态改变 onAuthLogin (message, callback?)授权页其他回调信息多次点击 登录按钮,会回调重复登录当callback存在时,表示未同意隐私协 议, 如果调用callback(true),则SDK会自行 勾选隐私协议并继续 登录|无|
|setCheckBoxSize|width: Length, height: Length 设置隐私条款勾选框宽高|20|
|setCheckBoxMargin|Margin 设置隐私条款勾选框偏移|-|
|setCheckBoxAlignRuleOption|AlignRuleOption 设置隐私条款勾选框对齐规则|-|
|setCheckedColor|ResourceColor 设置隐私条款勾选框选中的颜色|#FF3973FF|
|setCheckBoxShape|CheckBoxShape 设置勾选框类型(圆⻆矩形/圆形)|ROUNDED_SQUARE|
|setClauses|SpanEntity[] 设置隐私条款的协议文本,自定义条款, 自定义条款链接、字体颜 色|默认为运营商隐私协 议|
|setClauseMargin|Margin 设置隐私条款偏移|-|
|setClauseAlignRuleOption|AlignRuleOption 设置隐私条款对齐规则|-|
|setShowPrivacyUncheckedToast|boolean 设置是否弹出Toast提示文字|true|
|setPrivacyUnCheckedToastText|ResourceStr 设置未同意隐私条款的文字提示相关|"请同意服务条款"|
|setWindowMode|CustomDialogController 或undefined 设置窗口模式授权页宽高、偏移、窗口属性等|无|
|**调用示例** const config:GyAu statusBarCol navigationBa statusBarCon navigationBa }) .setPrivacyN .setPrivacyN .setPrivacyN .setPrivacyU .setNumberCo .setNumberSi .setNumberMa .setNumberAl middle: top: {a|thThemeConfig = new GyAuthThemeConfig().setSystemBarPrope or:'#ffffff', rColor:'#ffffff', tentColor:'#000000', rContentColor:'#00ffff' avTextColor(Color.White) avTextSize(20) avHeight(50) nCheckedToastText("测试未同意隐私协议") lor("#3973ff") ze(28) rgin({top:30}) ignRuleOption({ {anchor:'__container__',align:HorizontalAlign.Center nchor:'gy_login_logo_image',align:VerticalAlign.Bottom|rties({ }, },|

### **调用示例** 

}) .setCheckedColor(Color.Blue) " " .setLoginBtnText( 本机号码一键登录 ) .setLoginBtnTextSize(20) .setLoginBtnTextColor(Color.White) .setLoginBtnColor("#3973ff") .setLoginBtnWidth('70%') .setLoginBtnHeight(48) .setLoginBtnMargin({ top: 0 }) .setLoginBtnAlignRuleOption({ top: { anchor: '__container__', align: VerticalAlign.Center }, middle: { anchor: '__container__', align: HorizontalAlign.Center } }) .setClauses([{ text: "同意", isProtocol: false, fontColor: Color.Black, fontSize: 16, fontWeight: FontWeight.Normal, }, { text: "《&&Clause&&》", isProtocol: true, fontColor: "#3973ff", fontSize: 16, fontWeight: FontWeight.Normal, }, { text: "自定义协议", isProtocol: true, fontColor: "#3973ff", fontSize: 16, fontWeight: FontWeight.Normal, url: "https://www.baidu.com/" }, { text: "并使用本机号码校验", isProtocol: false, fontColor: Color.Black, fontSize: 16, fontWeight: FontWeight.Normal } ]) .setCheckBoxSize(20, 20) .setCheckBoxShape(CheckBoxShape.ROUNDED_SQUARE) .setCheckBoxMargin({ left: 20, bottom: 20 }) .setCheckBoxAlignRuleOption({ bottom: { anchor: '__container__', align: VerticalAlign.Bottom }, left: { anchor: '__container__', align: HorizontalAlign.Start } }) .setClauseMargin({ left: 5, right: 15 }) .setClauseAlignRuleOption({ left: { anchor: 'gy_login_clause_checkbox', align: HorizontalAlign.End }, 

```arkts
top: { anchor: 'gy_login_clause_checkbox', align: VerticalAlign.Top }, right: { anchor: '__container__', align: HorizontalAlign.End } }) .setOnAuthLoginPageListener({ onLoginPageInComplete: () => { " GyLog.debug("login page 成功拉起授权页 ) }, onCheckedChanged: (checked): void => { GyLog.debug("login page checkBok 选中状态:" + checked) }, onBackPressed: () => { " GyLog.debug("login page 返回事件 ) }, onLoginClickStart: () => { " GyLog.debug("login page 点击登录按钮 ) }, onLoginClickComplete: () => { " GyLog.debug("login page 登录返回响应 ) }, onAuthLogin: (message, callback?): void => { if (callback) { promptAction.showDialog({ message: '是否授权登录', buttons: [ { text: '确定', color: '#000000' }, { text: '取消', color: '#000000' } ], }).then(data => { if (data.index == 0) { callback(true) } else { callback(false) } }) } } }); const response = await GyManager.getInstance().eAccountLogin(5000, this.config) if (response.isSuccess()) { hilog.info(0x0000, "GY", `login success ==>${response}`) } else { hilog.info(0x0000, "GY", `login failed==>${response}`) } //可选择是否关闭授权页 GyManager.getInstance().closeAuthLoginPage() 
```

### **返回示例** 

返回成功,解析data.token用于置换手机号 返回失败,解析data.errorCode、data.errorDesc 了解详细失败原因 

登录成功 { "costTime": 3, "gyuid": "gtc_eafb4e7ddbfe059a3eaebde0c6ef858030", "code": 30000, "operator": "CT", "data": { "errorCode": 0, "errorDesc": "gysdk success!", "operatorType": 3, "processId": "bb3d486851b231beed21f46905582adc", "expiredTime": 1731491334433, "token": 

"bm1jODI0MmZjMDgwZjI0YWZmYjUwOTQwY2FmMWViOTkwYXx8M3x2MnwzfGJiM2Q0ODY4NTFiMjMxYmVlZDIxZjQ2O TA1NTgyYWRjfHw=" }, "success": true } 

登录失败 { "costTime": -1, "gyuid": "gtc_eafb4e7ddbfe059a3eaebde0c6ef858030", "code": 30006, "operator": "CT", "data": { "errorCode": -20104, "errorDesc": "gysdk预登录无效!", "operatorType": 3, "processId": "4b7204ebcd2324f41282cc1d4dd82de7", "metadata": "请先调用预取号接口" }, "success": false } 

## **7. 本机号码校验token** 

### **接口说明** 

#### 本机号码校验需要先获取通行证,然后再进行本机号码校验。 

/** * 获取本机号码校验通行证. * * @param phone      手机号码. * @param timeout    超时时间,一般5000~15000ms,<=0则使用15s,建议设为5000ms * @param gyCallBack 回调. */ public getVerifyToken(phone: string, timeout: number): Promise<GyResponse> 

### **调用示例** 

const response = await GyManager.getInstance().getVerifyToken(phone, 5000); if (response.isSuccess()) { 

hilog.info(0x0000, "GY", `getVerifyToken success ==>${response}`) } else { 

hilog.info(0x0000, "GY", `getVerifyToken failed==>${response}`) } 

### **返回示例** 

- 返回成功,解析data.accessCode、processId、operatorType进行本机号码校验 返回失败,解析 data.errorCode、data.errorDesc 了解详细失败原因 

##### 号码校验token成功 

{ "costTime": 365, "gyuid": "gtc_eafb4e7ddbfe059a3eaebde0c6ef858030", "code": 30000, "operator": "CT", "data": { "errorCode": 0, "errorDesc": "gysdk success!", "operatorType": 3, "processId": "d793ea85bca6cc609314a0eb2c7f107c", "expiredTime": 1731492081904, "token": "nm664c16c00d7f454294ac0d1c65f29952", "phone": "19157611003" }, "success": true } 

##### 号码校验token失败 

{ "costTime": -1, "gyuid": "gtc_eafb4e7ddbfe059a3eaebde0c6ef858030", "code": 30007, "operator": "CT", "data": { "errorCode": -40001, "errorDesc": "运营商返回错误,具体见msg!", "operatorType": 3, "processId": "1e4be2b66c172da9f9d01513902b4ff5", "metadata": "{\"code\":\"80004\",\"msg\":\"移动网络未开启 \",\"number\":\"\",\"accessCode\":\"\",\"expiredTime\":\"\",\"operatorType\":\"\",\"reqID\ ":\"\"}" }, "success": false } 

## **8. 本机号码校验** 

### **接口说明** 

我们还提供了服务端的本机号码校验接口,如果开发者有这方面的需求,请参考服务端的文档。 

/** * 验证本机号码. * * @param accessCode   本机号码校验通行证. * @param processId    processId. * @param phone        待校验号码. * @param operatorType 校验类型. * @param gyCallBack   回调. */ public verifyPhoneNumber(token: string, processId: string, phone: string, operatorType: number): Promise<GyResponse> 

### **调用示例** 

const response = await GyManager.getInstance().verifyPhoneNumber(token, processId, phone, operatorType); 

if (response.isSuccess()) { hilog.info(0x0000, "GY", `verifyPhoneNumber success ==>${response}`) } else { hilog.info(0x0000, "GY", `verifyPhoneNumber failed==>${response}`) } 

### **返回示例** 

返回成功,本机号码校验通过 

返回失败,解析data.errorCode、data.errorDesc 了解详细失败原因 

##### 号码校验成功 

{ "costTime": 504, "gyuid": "gtc_eafb4e7ddbfe059a3eaebde0c6ef858030", "code": 30000, "operator": "CT", "data": { "errorCode": 0, "errorDesc": "gysdk success!", "operatorType": 3, "processId": "7efbbab711d917af9bce182c8e571861", "metadata": "校验成功" }, "success": true 

} 

号码校验失败 { "costTime": -1, "gyuid": "gtc_eafb4e7ddbfe059a3eaebde0c6ef858030", "code": 30008, "operator": "CT", "data": { "errorCode": -30001, "errorDesc": "服务器返回错误,具体见msg!", "operatorType": 3, "processId": "473a735429882f11f1aece897cd5f588", "metadata": "{\"errno\":0,\"data\":{\"msg\":\"手机号校验失败 \",\"result\":\"40053\"}}" }, "success": false }
