# 引力引擎&鸿蒙接口文档

## GravityEngineSDK.setupAndStart

setupAndStart(context: Context, config: gravityConfig):void

初始化SDK

参数:

| 参数名 | 类型 | 必填 | 说明 |
|---|---|---|---|
| context | Context | 是 | 上下文context请在@Component页面中通过let context = getContext(this)  获取请勿在UIAbility中用this.context获取,否则会影响主题设 置 |
| config | gravityConfi g | 是 | 引力初始化参数,具体参考下方的gravityConfig类 |

返回值

| 类型 | 说明 |
|---|---|
| void |  |

示例:

```
import { GravityEngineSDK, gravityConfig } from"@gravityengine/analytics";
const config = newgravityConfig({
accessToken: "your_access_token", // 项目通行证,在:网站后台-->设置-->应用列表中
找到Access Token列复制(首次使用可能需要先新增应用)
clientId: "your_client_id", // 用户唯一 ID(例如 UID 或者设备 ID)
```

debugMode: "debug", // 是否开启测试模式,开启测试模式后,可以在网站后台--设置--元数

据--事件流中查看实时数据上报结果。(测试时可使用,上线之后一定要关掉,改成none或者不传)

```
});
awaitGravityEngineSDK.setupAndStart(this.context, config); // 注意setupAndStart
```

是异步方法,需要等其完成后再执行sdk其他方法

```
gravityConfig类说明如下:
export class gravityConfig {
clientId: string
accessToken: string
  debugMode?: 'none' | 'debug'
constructor(options: gravityConfig) {
this.accessToken = options.accessToken // 项目通行证
this.clientId = options.clientId  // 用户唯一 ID
this.debugMode = options?.debugMode || 'none'// 是否开启测试模式
  }
}
```

## GravityEngineSDK.initialize

initialize(data: any): any;

用户初始化

参数:

| 参数名 | 类型 | 必填 | 说明 |
|---|---|---|---|
| data | Map | 是 |  |

返回值

| 类型 | 说明 |
|---|---|
| void |  |

示例:

```
GravityEngineSDK.initialize({
USER_CLIENT_NAME: "your_client_name", // 用户昵称
CHANNEL: "your_channel", // 用户初始化渠道
ENABLE_SYNC_ATTRIBUTION: false, // 是否开启同步获取归因信息,具体请参考
https://doc.gravity-engine.com/turbo-integrated/sync_attribution.html
})
  .then((res) => {
console.log("gravityAnalytics initialize success ", JSON.stringify(res));
  })
  .catch((err: object) => {
console.log(
"gravityAnalytics initialize failed error",
JSON.stringify(err)
    );
  });
```

## GravityEngineSDK.setSuperProperties

setSuperProperties(data: any): any;

设置静态公共属性

参数:

| 参数名 | 类型 | 必填 | 说明 |
|---|---|---|---|
| data | Map | 是 | 属性值 |

返回值

| 类型 | 说明 |
|---|---|
| void |  |

示例:

```
GravityEngineSDK.setSuperProperties({
superKey: "superValue",
});
```

## GravityEngineSDK.clearSuperProperties

clearSuperProperties(): any;

清除所有静态公共属性

参数:

| 参数名 | 类型 | 必填 | 说明 |
|---|---|---|---|
|  |  |  |  |

返回值

| 类型 | 说明 |
|---|---|
| void |  |

示例:

```
GravityEngineSDK.clearSuperProperties();
1
```

## GravityEngineSDK.trackRegisterEvent

trackRegisterEvent(): any;

业务注册事件上报

参数:

| 参数名 | 类型 | 必填 | 说明 |
|---|---|---|---|
|  |  |  |  |

返回值

| 类型 | 说明 |
|---|---|
| void |  |

示例:

```
GravityEngineSDK.trackRegisterEvent();
1
```

## GravityEngineSDK.trackPayEvent

trackPayEvent(): any;

清除所有静态公共属性

参数:

| 参数名 | 类型 | 必填 | 说明 |
|---|---|---|---|
| data | Map | 是 | 付费参数 |

返回值

| 类型 | 说明 |
|---|---|
| void |  |

示例:

```
/**
```

 * 上报付费事件

```
 * @param payAmount     付费金额单位为分
```

 * @param payType       货币类型按照国际标准组织ISO 4217中规范的3位字母,例如CNY人民

币、USD美金等

```
 * @param orderId       订单号
 * @param payReason     付费原因例如:购买钻石、办理月卡
```

 * @param payMethod     付费方式例如:支付宝、微信、银联等

```
 */
GravityEngineSDK.trackPayEvent({
payAmount: 300,
payType: "CNY",
orderId: "your_order_id",
payReason: "月卡",
payMethod: "支付宝",
});
```

## GravityEngineSDK.trackAdShowEvent

trackAdShowEvent(): any;

清除所有静态公共属性

参数:

| 参数名 | 类型 | 必填 | 说明 |
|---|---|---|---|
| data | Map | 是 | 广告参数 |

返回值

| 类型 | 说明 |
|---|---|
| void |  |

示例:

```
/**
```

 * 上报广告观看事件参数如下

```
 * @param adUnionType   广告聚合平台类型(取值为:topon、gromore、admore、self,分
别对应Topon、Gromore、Admore、自建聚合)
 * @param adPlacementId 广告瀑布流ID(广告位ID)
 * @param adSourceId    广告源ID(代码位ID)
 * @param adType        广告类型(取值为:reward、banner、 native 、
interstitial、 splash ,分别对应激励视频广告、横幅广告、信息流广告、插屏广告、开屏广告)
7
 * @param adnType       广告平台类型(取值为:csj、gdt、ks、 mint 、baidu、other,分
别对应为穿山甲、优量汇、快手联盟、Mintegral、百度联盟、其他平台)
 * @param ecpm          预估ECPM价格(千次展示收入(单位元))
 */
GravityEngineSDK.trackAdShowEvent({
adUnionType: "topon",
adPlacementId: "placement_id",
adSourceId: "ad_source_id",
adType: "reward",
adnType: "csj",
ecpm: 1,
});
```

## GravityEngineSDK.track

track(): any;

清除所有静态公共属性

参数:

| 参数名 | 类型 | 必填 | 说明 |
|---|---|---|---|
| eventName | string | 是 | 事件名 |
| data | Map | 否 | 事件属性 |

返回值

| 类型 | 说明 |
|---|---|
| void |  |

示例:

```
GravityEngineSDK.track(
"$purchase", //追踪事件的名称
  {
// 需要上传的事件属性
Item: "商品A",
ItemNum: 1,
Cost: 100,
Elements: ["apple", "ball", "cat"],
  }
);
```
