# **SDK 接入文档** 

## **导入SDK** 

##### 以下内容可参考Demo的实现。 

1. 将 gamesdkLibrary.har 包放在工程的 libs 目录下: 

2. 在 App Module 的 oh-package.json5中,添加依赖项: 

- "dependencies": { 

"gamesdklibrary": "file:./libs/gamesdkLibrary.har" 

} 

##### 如下图: 

3. 在 App Module 的 module.json5中,配置网络访问权限: 

"requestPermissions": [ 

- { 

"name": "ohos.permission.INTERNET" 

}], 

如下图: 

4. 在项目级 build-profile.json5 中开启 useNormalizedOHMUrl (必须): 

如果接入方使用的是字节码 HAR(本 SDK 默认发布形态), useNormalizedOHMUrl 不是 true 会在编译 时报错: 

Bytecode HARS ... not supported when useNormalizedOHMUrl is not true 

{ "app": { "products": [ { "name": "default", "buildOption": { "strictMode": { "useNormalizedOHMUrl": true } } } ] } } 

##### 说明: 

该配置应写在 **项目级** build-profile.json5 (不是 module 级) 

   - 如果项目有多个 product ,请在实际构建使用的 product 下都保持为 true 

5. 在 App Module 的 module.json5的module节点增加如下client_id和app_id属性配置,用于华为登录和内购 的应用身份鉴权: 

"metadata": [ 

{ 

"name": "client_id", 

"value": "xxxxxxxxx" 

}, { "name": "app_id", "value": "xxxxxxxxx" 

} ] 

如下图: 

**华为后台获取** Client ID和APP ID: 

## **导入SDK接口** 

**import { GameSDKManager, GameSDKUser, GameSDKRoleInfo, GameSDKOrderInfo, NotificationCenter, GameSDKCallBackData } from 'gamesdklibrary'** 

## **接口调用** 

##### **创建接口实例对象** 

// 创建GameSDKManager实例对象 ,参数传SDK后台的productCode参数 

gamesdkInstance: GameSDKManager = GameSDKManager.getInstance('44021448506430380961470188790224') 

##### **初始化接口** 

this.gamesdkInstance.initWithProductCode('44021448506430380961470188790224') 

##### **华为账号登录接口** 

//打开华为登录界面 

this.gamesdkInstance.huaweiLogin(this.getUIContext()) 

1. 华为后台需要添加公钥指纹,同时这里的证书需要和研发工程里使用的证书保持一致 

##### 2. sdk后台游戏管理 -功能配置里需配置鸿蒙参数 

**支付接口** 

###### //创建订单数据对象 

let orderInfo: GameSDKOrderInfo = { productId:'testProductId', productName: 'testProductName', cpOrderID: 'testCpOrderID', amount: ‘6’,//单位元 callbackUrl: 'testCallbackUrl', extrasParams: 'testExtrasParams', productType: '0' //商品类型(可选,默认"0"):"0"消耗型, "1"非消耗型, "2"自动续期订阅, "3"非续期订 阅 } 

###### //调用支付 

this.gamesdkInstance.payWithOrderInfo(orderInfo) 

##### **productType 取值说明:** 

|**值**|**类型**|**说明**|
|---|---|---|
|"0"|消耗型|可重复购买的商品(如钻石、金币),默认值|
|"1"|非消耗型|一次性购买的商品(如去广告、永久解锁⻆色)|
|"2"|自动续期订阅|自动续费型订阅(如月卡、VIP会员)|
|"3"|非续期订阅|固定时长、不自动续费的订阅(如30天体验卡)|

##### 1. 华为后台开通应用内购买服务 

2. sdk后台游戏管理  -> 支付通道需添加鸿蒙支付并配置参数: 

注意:1.沙盒测试需要在华为后台添加测试账号,同时测试设备的系统设置里面需要登录该账号 

- 2.华为后台的商品id状态处于”草稿“状态不能测试,必须是”待提交“或者”审核通过“的状态 

- 3.SDK后台需正确配置包名,商品id,商品金额。否则支付完成无法到账 

##### **查询订阅状态接口(选接)** 

当使用自动续期订阅(productType="2")时,可通过此接口查询用户当前的订阅状态。 

//查询订阅状态,参数为业务自定义的订阅组标识,会透传到回调中 

this.gamesdkInstance.querySubscriptionStatus('mySubGroupId') 

查询结果通过 GAMESDK_NOTIFICATION_KEY_SUBSCRIPTION_STATUS 回调通知返回,见下方"注册SDK回调通 知"章节。 

##### **上传⻆色接口** 

//创建⻆色数据对象 let roleInfo: GameSDKRoleInfo = { roleId:'testRoleId', roleName: 'testRoleName', serverId: 'testServerId', serverName: 'testServerName', roleLevel: 'testRoleLevel', vipLevel: 'testVipLevel' } 

//上传游戏⻆色 

this.gamesdkInstance.updateRoleInfo(roleInfo) 

##### **隐私弹窗接口** 

###### //打开隐私弹窗 

this.gamesdkInstance.openPrivacyDialog(this.getUIContext()) 

##### **解绑华为账号接口** 

//是华为用户登录可解绑 

if (this.gamesdkInstance.isHuaweiUser()) { this.gamesdkInstance.unbindHuaweiAccount() } 

##### **退出登录接口** 

//退出登录 

this.gamesdkInstance.logout() 

##### **去掉游戏官方账号登录接口** 

//无官包体系的游戏,可以调这个接口来关闭游戏官方账号登录,需在登录之前调用 this.gamesdkInstance.enableGameOfficeLogin(false) 

##### **设置游戏官方账号登录按钮文案接口** 

说明:华为联合登录面板中,第三方游戏官方账号入口的展示名称由 

gamePlayer.ThirdAccountInfo.accountName 传入,SDK 默认文案为「游戏官方账号登录」。若需改为「xx游 账号登录」「xx通行证登录」等,可在调用 huaweiLogin / 触发联合登录前调用本接口。文案会先 trim() ,若 为空则恢复默认。 

###### // 需在华为账号登录前调用 

this.gamesdkInstance.setOfficialAccountLoginButtonText('XX账号登录(官服)') 

##### **HarmonyOS 5.0与HarmonyOS 4及以下账号互通** 

说明:华为转移登录时,HarmonyOS 4及以下游戏的玩家标识应与HarmonyOS 5.0及以上游戏的玩家标识 gamePlayerId建立映射 

1.前往AppGallery Connect配置新老系统游戏的APP ID映射关系 

参考华为文档: https://developer.huawei.com/consumer/cn/doc/harmonyos-guides/gameservice-gam eplayer-huawei#section3907114313255 

##### 2.处理登录回调返回的gamePlayerId 

当gamePlayerId不为空值时,代表华为转移用户登录,即该玩家是之前在HarmonyOS 4及以下游戏的玩家, 此时需要实现和HarmonyOS 4及以下系统上游戏内资产互通。这里返回的gamePlayerId就是安卓华为渠道的 uid,通过判断gamePlayerId和安卓华为渠道的uid值是否一样,值一样就互通游戏内资产。如果安卓华为渠道的 uid拼接了渠道号,那么gamePlayerId需要拼接同一个渠道号 

##### **判断是否华为转移用户接口** 

//是否华为转移用户 this.gamesdkInstance.isHuaweiTransferAccount() 

##### **打开云客服接口** 

1. 需先联系商务开通Quick云客服,获取客服产品code,将产品code传入客服接口 

//打开云客服,参数传云客服后台的产品code this.gamesdkInstance.openServiceCenter(this.getUIContext(), '11145220560844xxxxxxxxxxxxxxx') 

##### 2. 初始化窗口对象,需在Ability的onWindowStageCreate中调用如下方法 

windowStage.getMainWindow((err, data) => { if (err.code) { console.error('获取失败' + JSON.stringify(err)); return; } console.info('获取主窗口的实例:' + JSON.stringify(data)); globalThis.windowClass = data // 赋值给全局变量windowClass }); 

如下图: 

##### **注册SDK回调通知** 

###### //注册SDK初始化回调事件 

NotificationCenter.getInstance().addObserver('GAMESDK_NOTIFICATION_KEY_INIT_SUCCESS', (data: GameSDKCallBackData) => { 

` console.log(`SDK初始化成功:message:${data.message} ) 

}); 

//注册SDK登录回调事件 

NotificationCenter.getInstance().addObserver('GAMESDK_NOTIFICATION_KEY_LOGIN_SUCCESS', (data: GameSDKCallBackData) => { 

//回调返回用户信息: 

console.log(`SDK登录成功:uid:${data.uid}, userName:${data.userName}, 

token:${data.token}, gamePlayerId:${data.gamePlayerId},`) 

//通过GameSDKUser用户类获取用户信息 

promptAction.showDialog({ message: `uid:${GameSDKUser.getInstance().uid}, 

userName:${GameSDKUser.getInstance().userName}, token:${GameSDKUser.getInstance().token}` }) 

//HarmonyOS 4及以下游戏的玩家标识openId/playerId,如何与HarmonyOS 5.0及以上游戏的玩家标识 gamePlayerId建立映射 

//1. 前往AppGallery Connect配置新老系统游戏的APP ID映射关 

系,https://developer.huawei.com/consumer/cn/doc/harmonyos-guides/gameservice-gameplayerhuawei#section3907114313255 

//2. 当回调里的gamePlayerId不为空值时,代表华为转移用户登录,即该玩家是之前在HarmonyOS 4及以下游戏 的玩家,此时需要实现和HarmonyOS 4及以下系统上游 戏内资产互通。这里返回的gamePlayerId就是安卓华为 渠道的uid,通过判断gamePlayerId和安卓华为渠道的uid值是否一样,值一样就互通游戏内资产。 

//3. 如果安卓华为渠道的uid拼接了渠道号,那么gamePlayerId需要拼接同一个渠道号。 }); 

###### //注册SDK支付成功回调事件 

NotificationCenter.getInstance().addObserver('GAMESDK_NOTIFICATION_KEY_PAY_SUCCESS', (data: GameSDKCallBackData) => { 

//回调返回支付成功信息: 

console.log(`SDK支付成功:${data.message}:orderNo:${data.orderNo}, productId:${data.productId}, extrasParams:${data.extrasParams}`) }); 

//注册SDK支付失败回调事件 

NotificationCenter.getInstance().addObserver('GAMESDK_NOTIFICATION_KEY_PAY_FAIL', (data: GameSDKCallBackData) => { 

//回调返回支付失败信息: 

console.log(`SDK支付失败:${data.message}:orderNo:${data.orderNo}, productId:${data.productId}, extrasParams:${data.extrasParams}`) }); 

//注册隐私弹窗同意回调事件 

NotificationCenter.getInstance().addObserver('GAMESDK_NOTIFICATION_KEY_AGREE_PRIVACY', (data: GameSDKCallBackData) => { 

` console.log( 点击了同意隐私协议:message:${data.message} ,isAgreePrivacy:${data.isAgreePrivacy}`) 

}); 

###### //注册隐私弹窗不同意回调事件 

NotificationCenter.getInstance().addObserver('GAMESDK_NOTIFICATION_KEY_REFUSE_PRIVACY', (data: GameSDKCallBackData) => { 

` console.log( 点击了不同意隐私协议:message:${data.message} ,isAgreePrivacy:${data.isAgreePrivacy}`) 

}); 

//注册退出登录回调事件 

NotificationCenter.getInstance().addObserver('GAMESDK_NOTIFICATION_KEY_LOGOUT_SUCCESS', (data: GameSDKCallBackData) => { 

` ` console.log( 退出登录成功 ) }); 

//注册订阅状态查询回调事件(使用自动续期订阅时需要) 

NotificationCenter.getInstance().addObserver('GAMESDK_NOTIFICATION_KEY_SUBSCRIPTION_STATUS ', (data: GameSDKCallBackData) => { console.log(`订阅状态查询结果:subGroupId=${data.subGroupId}, code=${data.code}, message=${data.message}`) 

if (data.subscriptions) { 

data.subscriptions.forEach((sub) => { 

console.log(`订阅条目:productId=${sub.productId}, status=${sub.status}, expirationDate=${sub.expirationDate}`) 

}) } }); 

//注册解绑华为账号回调事件 

NotificationCenter.getInstance().addObserver('GAMESDK_NOTIFICATION_KEY_UNBIND_SUCCESS', (data: GameSDKCallBackData) => { ` ` console.log( 华为账号解绑成功 ) 

}); 

###### //注册华为登录失败回调事件 

NotificationCenter.getInstance().addObserver('GAMESDK_NOTIFICATION_KEY_HUAWEILOGIN_FAIL', (data: GameSDKCallBackData) => { 

` ` console.log( 华为登录失败 ) if (data.code === 1002000016) {//用户点击关闭华为登录框 ` ` console.log( 用户点击关闭华为登录框 ) } 

}); 

### **其他接口(选接)** 

#### **初始化微信QQ登录(选接)** 

###### //初始化微信登录 

this.gamesdkInstance.initWxLogin("wxd6bxxxxxxxxxxx", "8606969ec8eb7ebxxxxxxxxxxxxx") 

###### //初始化QQ登录 

this.gamesdkInstance.initQQLogin("1022xxxxxx", "iNr8Hxxxxxxxx") 

//在EntryAbility中响应来自微信/QQ的回调 onNewWant(want: Want, launchParam: AbilityConstant.LaunchParam): void { '' GameSDKManager.getInstance( ).handleAuthResult(want) } 

注意:微信登录时工程需要使用手动签名,不然会报错:"由于应用BundleID信息校验不通过,无法使用微信登录" 

QQ后台需要正确配置鸿蒙应用签名,不然会报错:"error authResponse is null" 

参考文档:https://wiki.connect.qq.com/harmonyos_sdk%e5%b8%b8%e8%a7%81%e9%97%ae%e9%a 2%98 

QQ后台AppLinking状态需要验证通过 

##### **module.json5 配置文件修改** 

// module.json5 的"module"节点下配置 querySchemes "querySchemes": [ "https", "qqopenapi", "weixin" ] // 在 Ability 的 skills 节点中配置scheme "skills": [ { "entities": [ "entity.system.browser" ], "actions": [ "ohos.want.action.viewData" ], "uris": [ { "scheme": "qqopenapi", // 接收 QQ 回调数据 "host": "(替换申请的互联 appId)", // 业务申请的互联 appId,如果填错会导致 QQ 无法回调 "path": "auth", "linkFeature": "Login", } ] } ] 

如下图: 

在业务 Ability.onNewWant() 中调用SDK如下方法: 

//在EntryAbility中响应来自微信/QQ的回调 '' GameSDKManager.getInstance( ).handleAuthResult(want) 

## **一** **阿里云手机号码 键登录(选接)** 

### **配置方式** 

- **方式一: sdk_config.json (与 mainurl 同级数组项)** 

|**name**|**value说明**|
|---|---|
|enableNumberAuthLogin|1 开启展示一键登录入口, 0 关闭|
|numberAuthSdkInfo|阿里云控制台应用密钥,传入SDK setAuthSDKInfo(勿将生产密钥提交到 公开仓库)|

##### **方式二:代码初始化(与 initDouyinLogin 类似,二者可覆盖或补充配置)** 

' ' GameSDKManager.getInstance(productCode).initNumberAuthLogin( 您的阿里云密钥串 ) 

一键登录失败或无网络时,用户仍可使用手机号 + 短信验证码登录。更新 oh-package.json5 中 file:libs/... 文件名。 

## **SDK域名配置(选接)** 

当需要修改sdk的默认域名时,可通过配置文件或代码接口两种方式设置SDK主接口地址。 

### **方式一:修改配置文件** 

##### 打开工程找到sdk配置文件,文件路径: 

oh_modules/gamesdklibrary/src/main/resources/rawfile/sdk_config.json,然后修改文件中mainurl对应的 value值 

### **方式二:调用接口动态设置** 

###### //设置SDK主接口地址,需在初始化前调用 

this.gamesdkInstance.setApiBaseUrl('https://sdkapi.example.com') 

###### //再调用初始化 

this.gamesdkInstance.initWithProductCode('44021448506430380xxxxxxxxxxxxx') 

##### 说明: 

1. mainurl 用于配置SDK主接口默认域名 

2. setApiBaseUrl() 用于运行时动态设置SDK主接口地址,建议在初始化前调用 

3. 优先级: setApiBaseUrl() 设置的地址 > sdk_config.json 中的 mainurl > SDK默认地址 

可参考 SDK Demo 接入
