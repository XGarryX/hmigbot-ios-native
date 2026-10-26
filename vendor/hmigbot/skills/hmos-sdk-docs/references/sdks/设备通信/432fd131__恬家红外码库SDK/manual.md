# 恬家码库 SDK 鸿蒙版调试文档 

恬家(上海)信息科技有限公司 

2025.09 

## 目录 

|1.|SDK 初始化............................................................................................................................... 3|
|---|---|
|1.1|引入HAR 包...............................................................................................................................3|
|1.2|SDK 配置.....................................................................................................................................3|
|2.|EPG 服务调试............................................................................................................................4|
|2.1|运营商相关接口.........................................................................................................................4|
|3.|遥控服务调试............................................................................................................................ 5|
|3.1|获取品牌列表.............................................................................................................................5|
|3.2|下载遥控器.................................................................................................................................6|
|3.3|精确匹配(适用有屏空调以外的遥控器)............................................................................6|
|3.4|自动匹配(适用有屏空调).................................................................................................... 6|
|3.5|搜素.............................................................................................................................................7|
|3.6|精确匹配(根据指定按键).................................................................................................... 8|
|3.7|信号辅助匹配(一般用于寻找和筛选有屏空调遥控器)....................................................8|
|3.8|信号辅助匹配(智能设备,一般用于寻找和筛选有屏空调遥控器)................................9|

### 1. SDK 初始化 

#### 1.1 引入HAR 包 

根据项目结构建立libs 文件夹。将TiqiaaSDK.har 文件置于该文件夹下。 

在module.json5 内配置网络请求权限 

"requestPermissions": [ { "name": "ohos.permission.INTERNET"}] 

在项目结构下的oh-package.json5 中做如下配置 

"dependencies": { 'tiqiaasdk': 'file:./entry/libs/TiqiaaSDK.har'} 

等待SDK 安装完毕即可 

#### 1.2 SDK 配置 

在Ability 生命周期内做如下配置: 

OnCreate 内进行SDK 初始化配置: 

获取包名、签名信息 

```arkts
let bundleFlags = bundleManager.BundleFlag.GET_BUNDLE_INFO_WITH_APPLICATION|bundleManag er.BundleFlag.GET_BUNDLE_INFO_WITH_SIGNATURE_INFO; let bundleInfo = bundleManager.getBundleInfoForSelfSync(bundleFlags); let signatureInfo = bundleInfo.signatureInfo; 
```

根据获取到的包名、签名等信息到恬家官网获取全局唯一key,其类型为Uint8Array 

地址如下: 

https://developer.tiqiaa.com/cn/mainconsole.html 

#### 调用初始化方法: 

TiqiaaService.init(this.context, appKey); 

#### 至此,OnCreate 内SDK 初始化完成 

#### 在OnDestory 内做配置如下代码: 

TiqiaaService.exit(); 

### 2. EPG 服务调试 

- 2.1 运营商相关接口 

调试步骤如下: 

#### 获取推荐遥控器列表步骤:获取省份列表->根据省分id 获取城市列表->根据城市id 

#### 获取运营商列表->根据城市id、电视台id 获取推荐的遥控器列表。 

#### 获取省份列表:接口无需参数。 

let provinceList = tvClient.getAllProvinces(); 

#### 获取城市列表:参数province_id:number 

let cityList = tvClient.getProvinceCities(provinceId); 

获取运营商列表:参数city_id:number 

let providerList = tvClient.getProvidersFromCity(cityId); 

获取运营商推荐的遥控器列表:参数province_id:number,city_id:number,需在回 

#### 调中实现业务逻辑。 

tvClient.load_provider_remotes(provinceID, cityID, (errcode, cpRemotes: 

TvCityProviderRemote[]) => { 

if (cpRemotes.length > 0) { 

doSomething }}) 

获取运营商频道列表步骤:获取省份列表->根据省分id 获取城市列表->根据城市id 

获取运营商列表->根据城市id、电视台id 获取运营商配置信息->根据配置信息获取频道列 

表步骤。获取省、市、电视台信息在此不在赘述。获取运营配置列表代码如下:参数 

tvStation_id:number,city_id:number,需在回调中实现业务逻辑。 

```arkts
tvClient.loadProviderChannelNumConfig(cityId, provider, (errcode, channelNums: TvChannelNum[]) => { if (channelNums?.length) { const channel_ids: number[] = channelNums.map(channelNum => channelNum.channel_id); }}) 
```

获取运营频道列表代码如下:参数channel_ids: number[],需在回调中实现业务逻辑。 

tvClient.loadChannels(channel_ids, (errcode, tvChannel: TvChannel[]) => { if (tvChannel?.length) { resolve(tvChannel)}}) 

注:channel_ids: number[]为获取运营商配置接口中,回调函数中channel 集合内所 

#### 有对象的id 构成的id 数组。 

### 3. 遥控服务调试 

- 3.1 获取品牌列表 

获取品牌列表代码如下:接口无需参数。需在回调中实现业务逻辑。 

remoteClient.load_brands((errcode) => { 

const brandList: Brand[] = remoteClient.getBrandByType(id);
resolve(brandList);
})

#### 3.2 下载遥控器 

下载遥控器列表代码如下:参数remote_id: number,需在回调中实现业务逻辑。 

remoteClient.download_remote(id, (errorCode, remote) => { 

#### DoSomething 

#### }) 

#### 3.3 精确匹配(适用有屏空调以外的遥控器) 

精确匹配的的代码如下:参数page:MatchPage。初始化对象如下: 

page: MatchPage = new MatchPage(); 

#### 在精确匹配接口中,需要给其以下属性赋值。 

品牌类型:page.appliance_type:ApplianceType 

品牌id:page.brand_id:bigInt 

系统语言:page.lang = RemoteUtil.getLocalLanguage(); 

remoteClient.exactMatchRemotes(this.page, (errcode, remoteList) => { 

doSometing 

#### }); 

#### 3.4 自动匹配(适用有屏空调) 

自动匹配的的代码如下:参数page:MatchPage。初始化对象如下: 

page: MatchPage = new MatchPage(); 

在自动匹配接口中,需要给其以下属性赋值。 

品牌类型:page.appliance_type:ApplianceType 

品牌id:page.brand_id:bigInt 

系统语言:page.lang = RemoteUtil.getLocalLanguage(); 

remoteClient.autoMatchRemotes(this.page, (errcode, remoteList) => { 

doSometing 

}); 

#### 3.5 搜素 

搜索官方库的代码如下:参数page:MatchPage。初始化对象如下: 

page: MatchPage = new MatchPage(); 

在搜索官方库接口中,需要给其以下属性赋值。 

品牌类型:page.appliance_type:ApplianceType 

品牌id:page.brand_id:bigInt 

系统语言:page.lang = RemoteUtil.getLocalLanguage(); 

关键字:page.keywords:string 

remoteClient.searchOfficial(this.page, (errcode, remoteList) => { 

doSomething 

#### }); 

#### 搜索DIY 库的代码如下:参数page:MatchPage。初始化对象如下: 

page: MatchPage = new MatchPage(); 

在搜索DIY 库接口中,需要给其以下属性赋值。 

品牌类型:page.appliance_type:ApplianceType 

品牌id:page.brand_id:bigInt 

系统语言:page.lang = RemoteUtil.getLocalLanguage(); 

关键字:page.keywords:string 

remoteClient.searchDiy(this.page, (errcode, remoteList) => { 

doSomething 

#### }); 

#### 3.6 精确匹配(根据指定按键) 

精确匹配代码如下:参数page:MatchPage。初始化对象如下: 

page: MatchPage = new MatchPage(); 

在搜索DIY 库接口中,需要给其以下属性赋值。 

品牌类型:page.appliance_type:ApplianceType 

品牌id:page.brand_id:bigInt 

系统语言:page.lang = RemoteUtil.getLocalLanguage(); 

当前匹配的按键:page.next_key:KeyType 

remoteClient.exactMatchRemotes(this.page, (errcode, remoteList) => { 

doSomething 

#### }); 

#### 3.7 信号辅助匹配(一般用于寻找和筛选有屏空调遥控器) 

智能设备信号辅助匹配表代码如下:参数page:IrMatchPage。初始化对象如下: 

#### page: IrMatchParam = new IrMatchParam(); 

#### 在搜索DIY 库接口中,需要给其以下属性赋值。 

品牌类型:page.appliance_type:ApplianceType 

品牌id:page.brand_id:bigInt 

Data:page.data :Uint8Array 

remoteClient.irmatch(this.bean, (errcode, idList) => { 

dosomething 

}); 

注:bean 的类型为IrMatchParam。其中属性data 为一个Uint8Array 数组。在实例代码 

中,给其付了一个测试数据。开发者应注意根据自己服务端实际响应的数据进行数据传递。 

如响应的类型为number。可根据实例代码内对数据类型进行转化。 

- 3.8 信号辅助匹配(智能设备,一般用于寻找和筛选有屏空调遥控器) 

智能设备信号辅助匹配表代码如下:参数为bean: IotIrMatchInfo 

remoteClient.irMatchNew(irBean.bean, (errcode, idList) => { 

dosometing 

#### }); 

注:其bean 内属性keyIrInfos 为一个对象数组,示例代码为测试数据。开发者应根据自己 

服务端提供对应的数据。
