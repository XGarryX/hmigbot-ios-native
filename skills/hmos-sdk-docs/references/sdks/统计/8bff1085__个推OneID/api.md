# **API** 接口文档 

## 接口类说明 

### 本文档所有接口所涉及的相关类及说明如下: 

## 初始化 

|类名|**OneID**|
|---|---|
|接口|static init(context: Context): Promise<string>|

#### 说明: 

初始化 SDK ,获取 OneID 。 

参数: 

context : Context 

#### 示例代码: 

OneID.init(this.context) .then((ret) => { hilog.info(0x0000, 'testOneID', 'OneID.init %{public}s', ret) }) .catch((err: Error) => { hilog.info(0x0000, 'testOneID', 'OneID.init Error %{public}s', err.message) }) 

回调参数: requestId: 单次请求 ID oneAID: 唯一 ID 

{ "requestId": "8af18ba411d14053824588c3147414f7", "oneAID": "A-d141229c1d62fc335f1ea77bf97d7399" } 

## 场景查询 

类 **OneID** 名 接 static queryLBS(context: Context, gpsInterval: number, gpsTimeOut: number): 口 Promise<string> 

#### 说明: 

#### 查询场景信息 

#### 参数: 

gpsInterval: GPS 有效期设置,可以设置范围为 -1 或 [0, 600] ,单位秒。 0 :实时获取 GPS 数据。 -1 :只使用系统缓存的 GPS 数据 gpsTimeout: GPS 实时定位超时时间设置,可以设置范围为 [10, 60] ,单位秒 , 建议设置 20 

#### 说明 **:** 

- 获取 gpsInterval 时间间隔内的 GPS 数据,如果超出间隔则实时获取 GPS 数据,进行查询场景 信息 

- `SDK` 不会主动获取定位权限,需要开发者发起定位授权 , SDK 会根据当前用户的授权状态来进行查 

- 询。 

- 未授权定位 \ 定位失败 \ 定位超时等,都将使用 ip 进行场景查询。 

#### 示例代码: 

// 设置 GPS 有效期为 30 秒,超时 20 秒,进行场景查询 OneID.queryLBS(this.context, 30, 20) .then((ret) => { hilog.info(0x0000, 'testOneID', 'OneID.queryLBS %{public}s', ret) }) .catch((err: Error) => { hilog.info(0x0000, 'testOneID', 'OneID.queryLBS Error %{public}s', err.message) }) 

#### 回调参数: 

requestId: 单次请求 ID sceneInfoList: 场景信息 coarseAddress: 粗略位置 addressCode: 位置代 码 

{ "requestId": "xxxxxxxxf0eb4432897d6be2xxxxxxxx", "sceneInfoList": [ { "sceneTypeList": [ { // 一级分类,指该位置所属的场景的类型,如:交通设施服务、购物服务、餐 饮服务等。 "st1": " 科教文化服务 " } ] } ], "coarseAddress": "xxxxxx", "addressCode": { // 省 Code "province": "450000", // 市 Code "city": "450100", // 区 Code "area": "450108" } } 

## 获取 **SDK** 版本号 

类名 **OneID** 接口 static getVersion(): string 

#### 说明: 

获取当前 SDK 版本号 

#### 返回: 

当前 SDK 版本号字符串
