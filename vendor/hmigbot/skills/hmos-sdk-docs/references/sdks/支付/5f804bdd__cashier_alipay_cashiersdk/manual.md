# 支付宝标准版本 **sdk** 接入说明 

## 隐私说明 

https://opendocs.alipay.com/common/02kiq3 

## 功能说明 

- H5 支付 

- 唤起支付宝支付 

## **compileSdkVersion** 

12 

## **minSdkVersion** 

12 

## 安装说明 

`ohpm install @cashier_alipay/cashiersdk` 

## 使用说明 

### 基础说明 

如果还没有接入过支付宝其他版本 SDK ,请参考文档: https://opendocs.alipay.com/open/204/105051? pathHash=b91b9616&ref=api 进行服务端接入 

### 使用 

1. 默认方式, H5 通过 router 进行跳转 

`// orderInfo 由服务端生成 // 第二个参数 控制是否展示支付宝 loading new Pay().pay(orderInfo, true).then((result) => { let message = `resultStatus: ${result.get('resultStatus')} memo: ${result.get('memo')} result: ${result.get('result')}`; console.log(message); }).catch((error: BusinessError) => { console.log(error.message); });` 

#### 2. 使用 navigator 进行跳转 

```
步骤一:通过调用payWithNav方法
- 第三个参数由sdk回调传入H5页面名称和需要传入到H5页面的参数,开发者自行进行nav跳转
- 第四个参数必传,传入 NavPathStack 实例
new Pay().payWithNav(orderInfo, true, (name: string, params: Object) => {
this.pageInfos.pushPathByName(name, params);
}, this.pageInfos).then((result) => {
letmessage =
`resultStatus: ${result.get('resultStatus')} memo: ${result.get('memo')} result:
${result.get('result')}`;
  console.log(message);
}).catch((error: BusinessError) => {
  console.log(error.message);
});
步骤二:在你的navigation的navDestination builder中配置对应页面
Navigation(this.pageInfos)...
        .navDestination(this.PagesMap)
        ...
@Builder
PagesMap(name: string, navPageIntent: Map<string, Object>) {
if (name === 'alipay/cashier/H5Page') {
// name 固定为这个,当然如果你的项目支持动态import的话可以使用回调中的name,二者值一致
    AlipayH5Page({ navPageIntent: navPageIntent })
  }
}
```

3. 使用 navigator 进行跳转,使用系统路由表 

- 该方式依赖鸿蒙更新系统,预计 6 月底可用 

```
new Pay().payWithNav(orderInfo, true, undefined, this.pageInfos).then((result) => {
letmessage =
`resultStatus: ${result.get('resultStatus')} memo: ${result.get('memo')} result:
${result.get('result')}`;
  console.log(message);
  }).catch((error: BusinessError) => {
  console.log(error.message);
  });
```

### 日志获取 

```
 Log.setupLogCallback((log) => {
      hilog.info(0x00, "sdk_demo", log);
    });
```

## **demo** 下载 

以下文档顶部的 zip 包就是 demo https://alidocs.dingtalk.com/i/nodes/qnYMoO1rWxrkmoj2IOpZR6yaJ47Z3je9? iframeQuery=utm_source%3Dportal%26utm_medium%3Dportal_recent&rnd=0.2928087218087806 

## **FAQ** 

1. 是否支持 API 11 ? 

   - 不支持,后续也不会支持,请及时升级 api 到 12 

2. 现在跳转 H5 是以什么方式? 

router 默认 支持 nav 自定义跳转 华为系统路由表方案等华为系统更新 

3. 是否支持 auth ? 

   - 不支持,如果要接入 auth 能力,联系华为支持 

4. 唤端支付能力是否可验证? 

   - 暂时不行,依赖支付宝 app ,目前还未公测。 

5. 服务端是否需要改造? 

   - 目前来看不需要。附支付产品文档: https://opendocs.alipay.com/open/204/105051?pathHash=b91b9616&ref=api 

6. 遇到错误怎么排查 

   - 过滤 alipay_sdk 日志,查看错误信息。目前 99% 都是订单串传入错误,请多检查检查订单串,是否和 android 传入到支付宝 sdk 

   - 中的一致。订单串用 android 验证之后可以支付,再反馈问题
