# **智能风控 鸿蒙 端接入文档(ArkTS)** 

## **隐私说明** 

### **三方SDK采集说明** 

为保证符合国家隐私合规政策,需要在隐私政策中的三方SDK列表中补充易盾智能风控SDK相关说明 

##### **易盾智能风控SDK(鸿蒙版)** 

第三方公司名称:杭州网易智企科技有限公司 

集成方式:内嵌SDK 

共享信息:设备唯一识别码:OAID(可选)、AAID;设备运行状态(SIM卡状态、USB状态、充电状态、电池容量 及电量、启动时间);设备基本信息(设备品牌及型号、设备厂商、设备所运行系统版本、名称、系统内核信息、 CPU型号、设备内存及存储大小、屏幕亮度及分辨率、设备架构、基带信息、辅助功能列表、模拟器类型);日志 信息(网络连接类型及状态、IP地址、运营商信息、网络代理、WIFI信息(可选))、自身安装包信息(包名,版 本号,签名) 

使用目的:用于风险控制、反欺诈、设备环境风险,以保障账户和交易安全 

使用场景:提高应用及合作伙伴服务的安全性,保证用户人身财产安全、预防钓鱼网站、欺诈、网络漏洞、计算机 病毒、网络入侵等风险 

共享方式:(内部)接口共享 

第三方隐私链接:https://dun.163.com/clause/privacy 

## **接入说明** 

接入 “智能风控” SDK,开发者需要完成以下步骤: 

1. 根据应用/游戏开发平台,将SDK拷⻉到指定的工程目录,并修改项目配置; 

2. 初始化SDK(初始化接口:init); 

3. 调用getToken获取token信息(getToken接口:getToken); 

4. 验证SDK接入是否正确; 

5. 可选择性的接入相关功能性接口; 

6. 本SDK支持系统版本:15 ~ 20 

##### **接入建议:** 

全局必须要接入的接口:初始化接口 

##### 关键业务埋点时必须要使用的接口:获取凭证 

- Worker方式接入参考:Worker方式接入 

## **接入步骤** 

SDK 涉及到以下文件: 

YiDunProtector-HarmonyNEXT-x.x.x.zip   //其中x.x.x是对应版本号 

##### **注意:** 

SDK只支持64位架构,默认只包含arm64-v8a和x86_64两个架构 

SDK最低支持API 15(2.4.0版本+) 

### **导入SDK** 

- (1)以 DevEco Studio 5.0.13.230 为例,将SDK文件放到工程中的 libs 文件夹下(没有libs文件夹可以自行创 建,不限制文件夹名称),然后在 工程根目录 的 oh-package.json5 文件中增加如下代码: 

"dependencies": { "@yidun/protector": "file:./libs/YiDunProtector-2.4.0.har", //其中x.x.x为版本,新的字节码 Har包接入方式 }, 

(2)点击右上方的Sync Now刷新工程 

## **SDK 接入调用说明** 

### **SDK 初始化接口(init)** 

#### **接口用途:** 

用于初始化智能风控 SDK。 

#### **接入须知:** 

- 使用其他接口之前,必须先调用初始化接口(init),建议在应用/游戏启动过后第一时间调用(初始化后,并 不会获取任何个人隐私相关信息); 

该接口为 **必须调用接口** 。 

#### **函数原型:** 

import { HTProtect, HTProtectConfig, AntiCheatResult } from '@yidun/protector'; 

static init(context: Context, productId: string, config?: HTProtectConfig): number; 

//2.4.0+版本以上支持,两者差异仅为是否需要设置context参数 static initV2(productId: string, config?: HTProtectConfig): number; 

#### **参数说明:** 

|**参数**|**说明**|**必要性**|
|---|---|---|
|context|当前环境的上下文|必填,V2接口下不 用传|
|productId|易盾HTP分配的productId,可登录易盾后台获取,格式为YDxxxx, 长度16位|必填|
|config|配置类的对象|可选,不需要可忽 略|

#### **返回值说明:** 

|**code**|**说明**|
|---|---|
|200|初始化成功|
|1001|context为空|
|1002|加载so失败|
|1003|productId格式错误,格式为YDxxxx,长度16位|
|1004|校验私有化host失败,格式不正确|
|1005|context获取异常|

#### **配置类HTProtectConfig设置:** 

##### **(1) 设置渠道信息** 

channel: string = ''; 

若需要传递当前应用包体来源渠道可调用该接口(比如:应用宝渠道编号/信息)。 

##### **(2) 设置禁止采集项** 

privacyList: Array<string> = [] //如['wifi']表示不采集wifi名称和wifimac信息 

若需要禁止某些数据采集可调用该接口,目前仅支持配置wifi、oaid相关,不调用默认会采集 

##### **(3) 设置自定义域名** 

host?: string = '';//自定义域名,私有化时需要使用,格式为https://xxx.xxx.xxx或xxx.xxx.xxx,非完 整url地址,当配置xxx.xxx.xxx时,默认前缀加上https:// 

若需要私有化部署,需设置该域名为私有化域名,saas服务时,请勿配置该参数 

如需要示例 demo 请联系易盾获取。 

#### **示例代码:** 

.... 

import { HTProtect, HTProtectConfig, AntiCheatResult } from '@yidun/protector'; 

.... 

@Entry @Component struct Index { @State message: string = 'Hello World'; 

```arkts
build() { Row() { Column() { Text(this.message) .fontSize(50) .fontWeight(FontWeight.Bold) .onClick(() => { let config: HTProtectConfig = new HTProtectConfig(); config.channel = "测试";//设置渠道信息 config.privacyList = ['wifi']; //不采集wifi信息 config.host = 'https://dun.163.com'; //仅针对私有化部署时需要设置该属性 let ret = HTProtect.init(getContext(this), "product id", config); //调用初始化, 带配置 
... let ret = HTProtect.init(getContext(this), "product id");//调用初始化,不带配置 ... let ret = HTProtect.initV2("product id");//调用初始化,不带配置 ... hilog.info(0x0000, 'testTag', '%{public}s  %{public}d', 'init htp status', ret); 
```

}); } .width('100%') } .height('100%') } } 

### **获取凭证(getToken)** 

#### **接口用途:** 

用于关键业务节点风险防控场景中,比如注册、登录、领劵、抽卡、兑换、点赞、评论等业务场景。业务方可通过 此接口,获取检测唯一凭证 token。业务服务端通过此凭证实时获取当前用户/玩家风险检测结果,并根据结果进行 处置。 

###### 接口适用场景为: 

- 1、游戏类应用,当 SDK 数据上报接口被屏蔽导致数据上报失败时,通过 getToken 接口获取 SDK 采集信息,并由客 户服务端传递给易盾服务器; 

- 2、全类型应用,在关键业务节点主动调用检测时,通过 getToken 接口获取检测凭证,由客户服务端通过 token 凭证 从易盾服务器查询检测结果。 

#### **接入须知:** 

- 须在 SDK 初始化且用户同意隐私政策后才能调用该接口,网易易盾隐私说明。 

- 接口支持同步或者异步模式。 

#### **函数原型:** 

static async getToken(timeout: number, businessId: string): Promise<AntiCheatResult> 

#### **参数说明:** 

|**参数**|**说明**|**必要性**|
|---|---|---|
|timeout|函数 超时 时间|必填,单位毫秒,[400,10000],此区间外默认为3000,建议设置3000,表示 getToken函数超时时间,超过时间自动降级为离线token|
|businessId|业务 ID|必填,由易盾后台分配(32位),并在官网“服务管理”中查询|

#### **返回值说明:** 

##### AntiCheatResult类说明: 

interface AntiCheatResult { code: number; codeStr: string; token: string; } 

##### 变量说明: 

|**变量**|**说明**|
|---|---|
|code|结果码,不同结果码含义如下:200:表示调用成功,其他结果码均表示调用失败;199:产品ID 不合法;201:SDK未初始化;202:在主线程运行;203:businessId不合法;204:其他情 况,比如受到攻击|
|codeStr|结果码对应的字符说明,200:success,199:productId invalid;201:error not init;202: error. run on main thread;203:businessId invalid;204:gen token error|
|token|当code为200时,返回正常token(40位)。当网络状态不佳或者超时时,会返回离线token (几KB左右)|

#### **示例代码:** 

.... import { HTProtect, HTProtectConfig, AntiCheatResult } from '@yidun/protector'; .... 

//异步模式,通过promise进行异步调用 HTProtect.getToken(5000, "business id").then((result) => { hilog.info(0x0000, 'testTag', 'getAsync htp token  code:%{public}d token:%{public}s codeStr:%{public}s', result.code, result.token, result.codeStr); }); 

//同步模式,通过await将结果直接返回到result中 let result = await HTProtect.getToken(5000, "business id"); hilog.info(0x0000, 'testTag', 'getSync htp token  code:%{public}d token:%{public}s codeStr:%{public}s', result.code, result.token, result.codeStr); 

### **Worker方式接入** 

#### **方法用途:** 

用于适配部分框架无法直接支持ArkTS接入的问题,如团结引擎,需使用Worker进行接入,需注意目前仅支持单 Worker调用。 

#### **接入须知:** 

需保证初始化时能够正确的传递context变量,保证风控init接口可以初始化成功 

#### **示例代码:** 

如团结引擎可在TuanjiePlayerAbility.ts类的onCreate方法中,使用自带Worker类或自定义Worker来实现风控SDK 初始化,以下为自定义Worker初始化示例。 

workerInstance: worker.ThreadWorker = new worker.ThreadWorker('entry/ets/workers/MyWorker.ets'); //传递context信息,必须在UI线程调用,如需要传递额外的信息可通过其他变量传递,团结引擎可使用 this.context 

```arkts
this.workerInstance.postMessage({ type: 'initDun', data: getContext(this) }); //在UI线程监听worker线程的传递信息,并根据返回值进行处理 this.workerInstance.onmessage = (e: MessageEvents) => { let data: ESObject = e.data; switch (data.type) { case "dunCode": hilog.info(0x0000, 'testTag', '%{public}s  %{public}d', 'init htp status', data.data); if (data.data == 200) { //当初始化成功时,执行获取token的方法,通过type传递给worker线程,此处为演示方法,应根据自 身业务需要在必要的地方进行调用,避免产生隐私合规问题 this.workerInstance.postMessage({ type: 'getDunToken' }); } break; case "dunToken": //监听worker线程调用风控getToken方法的返回值 
```

hilog.info(0x0000, 'testTag', 'get htp token  % {public}s',JSON.stringify(e.data)); break; } } 

##### Worker线程内处理方式 

```arkts
workerPort.onmessage = (e: MessageEvents) => { let data: ESObject = e.data; switch (data.type) { case "initDun": let config: HTProtectConfig = new HTProtectConfig(); config.channel = "testChannel"; config.privacyList = ['wifi']; //此处data.data为UI线程传递过来的context变量 let ret: number = HTProtect.init(data.data, "productCode", config); hilog.info(0x0000, 'testTag', '%{public}s  %{public}d', 'init htp status', ret); workerPort.postMessage({ type: 'dunCode', data: ret }) break; case "getDunToken": HTProtect.getToken(3000, "businessID").then((result: AntiCheatResult) => { 
```

hilog.info(0x0000, 'testTag', 'get htp token  code:%{public}d token:%{public}s codeStr:%{public}s', 

result.code, result.token, result.codeStr); workerPort.postMessage({ type: 'dunToken', data: result }) }); break; } } 

### **常见问题FAQ** 

1.  当前SDK是否支持beta1开发者版本. 

答:自2.3.2版本之后,SDK最低支持API 12 beta5,之后版本将只支持至少API 12 Release. 

2.  linux或者开启caseSensitiveCheck时提示Cannot resolved import statement 

- @ohos/YiDunProtector/index. Please check the case. 

答:目前临时方案可以强制引入from '@ohos/YiDunProtector/Index'; 

3.  sdk接入后运行在模拟器上出现崩溃. 

答:由于模拟器不强制要求签名,sdk在获取签名时出现空指针,临时可以通过签名hap避免该问题,从2.2.0 sdk版 本后会兼容该问题. 

4.  IDE升级到5.0.3.800后,如果工程级build-profile.json5文件的useNormalizedOHMUrl字段为true,当 oh-package.json5中依赖的包使用的别名和依赖包的oh-package.json5的name不一致时报错. 

答:1.参考https://developer.huawei.com/consumer/cn/doc/harmonyos-releases-V5/idechangelogs-nb1-V5适配指导或者更改引入方式为import { AntiCheatResult, HTProtect} from 'yidunprotector'; 下个风控版本会原生兼容新版本命名规范.
