# 引力引擎SDK鸿蒙版接入文档

本文档为鸿蒙设备接入引力引擎的技术接入方案,支持 HarmonyOS NEXT,基于 OpenHarmony

API 12。

## 1. 下载安装

-
通过 ohpm 集成(推荐使用)

```
ohpm install @gravityengine/analytics
1
```

-
通过本地 har 集成

请联系引力获取到最新的.har 放到项目目录中,再在终端执行:

```
ohpm install 本地目录/gravityengine.har
1
```

## 2. 配置 SDK

### 2.1 初始化 SDK

请使用如下代码进行初始化:

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

### 2.2 配置权限

在 module.json5 中配置所需权限:

```
"requestPermissions": [
  {
"name": "ohos.permission.INTERNET"
  },
  {
"name":
"ohos.permission.GET_NETWORK_INFO"
  }
]
```

## 3. 常用功能

### 3.1 初始化

在用户可以获取到用户唯一 ID 时调用此方法,推荐首次启动时调用。

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

首次调用 initialize 后,需要等回调成功之后才能继续调用其他事件上报的方法。

### 3.2 开启 log

开启后,请在日志中输入 gravityAnalytics 过滤出引力的 log。

```
GravityEngineSDK.enableLog(true);
1
```

### 3.3 设置静态公共属性

```
GravityEngineSDK.setSuperProperties({
superKey: "superValue",
});
```

### 3.4 清除所有静态公共属性

```
GravityEngineSDK.clearSuperProperties();
1
```

## 4. 行为事件上报

### 4.1 业务注册事件上报(可选)

当用户完成应用内业务注册后,您可以调用trackRegisterEvent方法来上报用户注册事件

($AppRegister)给引力,引力会使用该事件统计指标:标准_注册数。

```
GravityEngineSDK.trackRegisterEvent();
1
```

### 4.2 付费事件上报

当用户发生付费行为时,需要调用trackPayEvent方法记录用户付费事件,此事件非常重要,会

影响买量和 ROI 统计,请务必重点测试!

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

国际标准组织 ISO 4217 代码表

### 4.3 广告观看事件上报

若您的产品内有广告变现,则需要在用户点击广告观看的同时上报用户广告观看事件给引力,具体参

考如下:

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

参数ecpm单位为元,请务必注意,做好单位转换,传错单位可能会导致买量受到影响!

### 4.4 提现事件上报(可选)

当用户发生应用内提现行为时,需要调用trackWithdrawEvent方法记录用户提现事件!

```
/**
```

 * 上报提现事件

```
 * @param payAmount     提现金额单位为分
```

 * @param payType       货币类型按照国际标准组织ISO 4217中规范的3位字母,例如CNY人民

币、USD美金等

```
 * @param orderId       订单号
```

 * @param payReason     提现原因例如:用户首次提现、用户抽奖提现

```
7
```

 * @param payMethod     提现支付方式例如:支付宝、微信、银联等

```
 * @param isFirstPay    是否首次提现
 */
GravityEngineSDK.trackWithdrawEvent({
payAmount: 300,
payType: "CNY",
orderId: "your_order_id",
payReason: "月卡",
payMethod: "支付宝",
isFirstPay: true,
});
```

国际标准组织 ISO 4217 代码表

### 4.5 记录事件时长

如果您需要记录某个事件持续时长,您可以调用timeEvent

来开始计时,配置您想要计时的事件名称,当您上传该事件时,将会自动在您的事件属性中加入

$event_duration这一属性来表示记录的时长,单位为秒。

```
// 调用 timeEvent 开启对 TIME_EVENT 事件的计时
GravityEngineSDK.timeEvent("TIME_EVENT");
// do some thing...
// 通过 track 上传 TIME_EVENT 事件时,会在属性中添加 $event_duration 属性
GravityEngineSDK.track("TIME_EVENT", {});
```

### 4.6 上报自定义事件

您可以直接调用track上传自定义事件,建议您根据准备阶段梳理的文档来设置事件的属性以及发

送信息的条件,此处以购买商品为范例:

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

-
track接口共有两个参数,第一个参数为事件的名称,第二个参数为事件的属性

-
事件的名称是字符串,只能以字母开头,可包含数字,字母和下划线“_”,长度最大为 50 个字

符。

-
事件的属性是 JS 对象,每个元素代表一个属性。

-
元素的 name 对应属性的名称,规定只能以字母开头,包含数字,字母和下划线“_”,长度最大

为 50 个字符。

-
元素的 Value 为该属性的值,支持String、Integer、Float、Boolean、Date、

```
DateTime和Array;Array
```

中的内容可以为String

如需上报自定义事件,建议您先在元事件中添加,否则会上报失败!

## 5. 用户属性上报

### 5.1 设置用户属性

对于一般的用户属性,您可以调用userSet来进行设置,使用该接口上传的属性将会覆盖原有的属

性值,如果之前不存在该用户属性,则会新建该用户属性

```
//设置用户属性,会员等级
GravityEngineSDK.userSet({ vip_level: "钻石会员" });
```

属性格式要求与事件属性保持一致。

### 5.2 初始化用户属性

如果您要上传的用户属性只要设置一次,则可以调用userSetOnce来进行设置,当该属性之前已经

有值的时候,将会忽略这条信息。

```
//以设置用户名为例,如果用户名已设置,则忽略本次设置,如果不存在,则设置为传入值
GravityEngineSDK.userSetOnce({ user_name: "TestUser" });
```

属性格式要求与事件属性保持一致。

### 5.3 累加用户属性

当您要上传数值型的属性时,您可以调用userAdd来对该属性进行累加操作,如果该属性还未被设

置,则会赋值 0 后再进行计算

```
//以付费为例,用户每次付费时调用此接口,则'total_revenue'字段每次会做累加付费金额的处理
GravityEngineSDK.userAdd({ total_revenue: 50 });
```

设置的属性 key 为字符串,Value 只允许为数值。

### 5.4 重置用户属性

当您要清空用户的某个用户属性值时,您可以调用userUnset

来对指定属性进行清空操作,如果该属性还未在集群中被创建,则userUnset不会创建该属性

```
//清空属性名为userPropertyKey的用户属性值该用户,即设置成NULL
GravityEngineSDK.userUnset("userPropertyKey");
```

userUnset: 的传入值为被清空属性的 Key 值。

### 5.5 清空用户属性

如果您要删除某个用户,可以调用userDelete将这名用户删除,您将无法再查询该名用户的用户

属性,但该用户产生的事件仍然可以被查询到

```
GravityEngineSDK.userDelete();
1
```

### 5.6 Array 属性追加

您可以调用userAppend对 Array (List) 类型的用户数据追加元素。

```
GravityEngineSDK.userAppend({
Movies: ["Interstellar", "The Negro Motorist Green Book"],
});
```

### 5.7 Array 属性去重追加

userUniqAppend用来对 Array (List) 类型的用户数据去重追加元素。

```
GravityEngineSDK.userUniqAppend({
Movies: ["Interstellar", "The Negro Motorist Green Book"],
});
```

### 5.8 用户属性取最大值

userNumberMax用来比较数值大小,保存较大的,如果没有这个 key,则新增 key,value 取本次

的值

```
GravityEngineSDK.userNumberMax({
ad_ecpm_max: 300,
});
```

### 5.9 用户属性取最小值

userNumberMin用来比较数值大小,保存较小的,如果没有这个 key,则新增 key,value 取本次

的值

```
GravityEngineSDK.userNumberMin({
ad_ecpm_min: 17,
});
```

## 6. 其他功能

### 6.1 绑定数数

```
/**
```

 * 绑定数数

```
 * @param taAccountId     当前[CHANGELOG.md](CHANGELOG.md)用户的数数账户 ID
(#account_id)
 * @param taDistinctId       当前用户的数数访客 ID (#distinct_id)
 */
GravityEngineSDK.bindTAThirdPlatform({
taAccountId: "account_id",
});
```

引力会自动将引力client ID和您传入的数数account_id以及distinct_id做关联,

在回调数数接口时,通过这个关联传递对应的

```
account_id、distinct_id给数数后台
```

## 7. 发版记录

| 版本 | 日期 | 备注 |
|---|---|---|
| 1.0.0 | 2024-12-03 | 首次发布 |
| 1.0.4 | 2024-12-11 | 优化代码 |
