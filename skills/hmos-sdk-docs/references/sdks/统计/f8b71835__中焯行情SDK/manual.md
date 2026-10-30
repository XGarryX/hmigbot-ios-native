# **快速接入指南** 

## **环境配置** 

"tztzfhqdatasdk": "./libs/tztzfhqdatasdk.har", 

// == SDK配置 == // 

SseSdk.setDebug(true);//调试开关,输出log,生产环境需注释掉 let sseConfig = new  SSeConfig() config.setAppkey(appKey)//appkey传入与包名对应的key .setContext(this.context) SseSdk.setConfig(sseConfig); 

// ==权限配置(备注: 以上配置信息可放在Application里,若不配置权限,港股默认为沪港1档与深港1 档,其他市场默认为 level1)== // 

SseSdk.permission().setLevel\(ZZPermission.LEVEL_2) //配置沪深境内权限 .addHkPermission\ 

(ZZPermission.HKA1,ZZPermission.HKD1,ZZPermission.SZHK5,ZZPermission.SHHK5,ZZPermission.HK 10,ZZPermission.HKAZ)//添加港股/港股指数权限 

.addHKOverseaPermission\(ZZPermission.OL_HK10)//添加港股境外10档权限 

.addHKOverseaPermission\(ZZPermission.OL_HKA1) //添加港股境外实时1档权限 

.addShSzOverseaPermission\(ZZPermission.OL_LEVEL_1) //添加沪深境外权限 沪深Level1 .setSseLevel\(ZZPermission.LEVEL_1) //统一设置大商所、郑商所、全球、外汇市场的level //单独设置沪深权限,设置后setLevel方法不起效果,不单独设置则setlevel继续有效 

.addShSzPermission\(ZZPermission.SH_LEVEL_2) //添加l2默认会有level1,可以不添加level1 .addShSzPermission\(ZZPermission.SZ_LEVEL_2)//否则想要level1则要添加level1 .addShSzPermission\(ZZPermission.SH_LEVEL_1) 

.addShSzPermission\(ZZPermission.SZ_LEVEL_1) 

//注意:初始化时,配置权限禁止调用submit,后续操作权限才能调用submit方法 .submit();        //权限设置完,统一调用该方法, 更新港股境外权限,切换推送连接 

## **所需应用权限** 

"requestPermissions": [ 

{"name":"ohos.permission.INTERNET"}, 

{"name": "ohos.permission.GET_NETWORK_INFO"}, {"name": "ohos.permission.GET_WIFI_INFO"} ] 

## **注册认证** 

应用程序接口说明: 每次注册需要重新创建新的实体,每次启动APP只需要注册一次,之后SDK会处理 

```arkts
let registerReq = new ZZRegisterReq() registerReq.send({ onSuccess: (resp: RegisterResp) => { //注册成功 }, onFail: (err: ErrorInfo) => { //注册失败 } });
```
