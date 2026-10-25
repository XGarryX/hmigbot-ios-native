汽车数字钥匙系统 移动端 SDK 接口文档 

二○二五年十月 

###### 目录 

|1. 范围...............................................................................................................................................2|
|---|
|2. 第三方框架.................................................................................................................................. 2|
|3. SDK集成方式...............................................................................................................................2 |
|3.1. SDK 集成........................................................................................................................... 2|
|3.2. DevEco-Studio 配置....................................................................................................... 2|
|3.2.1 运行环境配置........................................................................................................ 2 |
|3.2.2 添加权限................................................................................................................ 3|
|3.3. 对蓝牙模组依赖.............................................................................................................. 3 |
|4. 接口定义...................................................................................................................................... 4|
|4.1. 初始化.............................................................................................................................. 4|
|4.1.1 初始化SDK.............................................................................................................4|
|4.1.2 配置蓝牙服务........................................................................................................ 5|
|4.2. 蓝牙模块.......................................................................................................................... 6|
|4.2.1 手动连接车辆........................................................................................................ 6|
|4.2.2 断开车辆连接........................................................................................................ 6|
|4.2.3 获取蓝牙状态........................................................................................................ 7|
|4.2.4 获取PIN码.............................................................................................................7|
|4.3. 数字钥匙模块.................................................................................................................. 7|
|4.3.1 数字钥匙激活........................................................................................................ 7|
|4.3.2 数字钥匙下载........................................................................................................ 8|
|4.3.3 设置当前钥匙........................................................................................................ 9|
|4.3.4 获取分享限制次数................................................................................................ 9 |
|4.3.5 获取权限配置信息..............................................................................................10|
|4.3.6 数字钥匙分享...................................................................................................... 11|
|4.3.7 数字钥匙撤销分享..............................................................................................12|
|4.3.8 获取被分享钥匙列表..........................................................................................12|
|4.3.9 获取车主钥匙状态..............................................................................................14|
|4.3.10 获取车主授权钥匙列表....................................................................................15|
|4.3.11 删除车主授权钥匙............................................................................................16|
|4.3.12 获取设备列表....................................................................................................16|
|4.3.13 设备注销............................................................................................................ 17|
|4.3.14 蓝牙钥匙推送....................................................................................................18|
|4.3.15 数字钥匙归还....................................................................................................18|
|4.3.16 日志上传............................................................................................................ 18|
|4.3.17 蓝牙标定参数下载............................................................................................19|
|4.3.18 获取标定参数....................................................................................................20|
|4.3.19 修改用户自标定参数........................................................................................21|
|4.3.20 恢复标定参数....................................................................................................22|
|4.4. 指令模块........................................................................................................................ 22|
|4.4.1 蓝牙发送指令...................................................................................................... 22|
|4.4.2 蓝牙指令监听...................................................................................................... 23|

|4.5. 缓存清理........................................................................................................................ 24|
|---|
|4.5.1 清空数据.............................................................................................................. 24|
|5. 附录.............................................................................................................................................24|
|5.1. 错误码............................................................................................................................ 24|

### 修订记录 

|编号|日期|描述|版本|作者|审核|发布日期|
|---|---|---|---|---|---|---|
|1|2025.10.21|预定义接口|V1.0|郭旭|||

1 

# 1. 范围 

此文档用于数字钥匙项目鸿蒙端集成使用。功能包含库初始化、蓝牙初始化、 数字钥匙蓝牙连接、手机与硬件通信的双向认证、控车及通信数据加密、数字钥 匙激活、数字钥匙下载、数字钥匙分享、数字钥匙撤销、同步数字钥匙状态、注 销数字钥匙、挂失冻结数字钥匙、解冻数字钥匙、清空数据、销毁缓存数据等功 能。 

# 2. 第三方框架 

使用系统 Api 实现,未使用第三方框架 

# 3. **SDK** 集成方式 

## 3.1. SDK 集成 

将 DigitalKeylibrary.har 和 BaseAlgorithmlibrary.har 添加到工程中 配置文件路径 

## 3.2. DevEco-Studio 配置 

## 3.2.1 运行环境配置 

- 开发 IDE: 华为官方 IDE, Dev_ECO 版本 6.0.0 及以上 

- ●SDK 版本:5.0.0(12)及以上 

- ●runtimeOS:HarmonyOS 

2 

## 3.2.2 添加权限 

- ohos.permission.GET_NETWORK_INFO // 获取网络信息 

- ohos.permission.INTERNET // 网络权限 

- ohos.permission.STORE_PERSISTENT_DATA // 关键资产信息 

- ohos.permission.USE_BLUETOOTH // 允许应用查看蓝牙的配置 

- ohos.permission.ACCESS_BLUETOOTH // 蓝牙权限 

注意:配置蓝牙权限需在代码中添加用户授权代码 

###### 权限配置示例 

## 3.3. 对蓝牙模组依赖 

- (1)蓝牙模组使用低功率模式(BLE) 

- (2)蓝牙模组 GATT 读特征值模式为 notify 

3 

# 4. 接口定义 

## 4.1. 初始化 

## 4.1.1 初始化 **SDK** 

接口名称: 

public async initDigitalKeySDK(config: DKConfiguration): Promise<boolean> 

接口说明:使用 SDK 首先要初始化 SDK,建议在使用数字钥匙时调用,初始化 SDK 接口主要是对基础参数的存储和初始化,和对网络请求的配置。 

#### DKConfiguration 参数说明: 

|名称|类型|必填|说明|
|---|---|---|---|
|context|common.UIAblityContext|Y|context上下文|
|userId|string|Y|用户id|
|baseURL|string|Y|网络请求根路径|
|requestHeader|HashMa<String:String>|N|请求头|
|isLog|boolean|N|是否打印内部输出|
|securityPolicy|Record<string, string>|N|客户端CA证书信息|
|accessKey|string|N|token访问key|
|secretKey|string|N|token密钥Key|

返回参数说明:NULL 

代码示例: 

let config = new DKConfiguration(); 

config.context = context 

config.userId = userId 

= config.baseURL Constants.BaseURLString 

let reqHeader: HashMap<string, string> = new HashMap() 

= config.requestHeader reqHeader 

4 

config.isLog = true 

config.securityPolicy = undefined 

config.accesskey = "1694F642139340A3" 

= config.secretKey "s3f529YTaZ0qNEO2kMVZYrvIJjRZ0LMm" 

DKAuthSDK.getInstance().initDigitalKeySDK(config).then((dict)=>{ 

hilog.info(0xff,'bleDemo', "初始化结果成功" + JSON.stringify(dict)); }).catch((err: Error) => { 

hilog.error(0xff,'bleDemo', "初始化结果失败" + JSON.stringify(err)) 

}); 

## 4.1.2 配置蓝牙服务 

接口名称: 

#### public configeBleService(config: DKBleConfiguration) 

接口说明:配置蓝牙服务信息。蓝牙连接配对码输入时间较长,建议扫描超时 时间为 20s 以上。 

#### DKBleConfiguration 参数说明: 

|名称|类型|必填|说明|
|---|---|---|---|
|validMTULength|number|Y|有效的MTU长度|
|serviceUUID|string|Y|蓝牙服务 UUID|
|readUUID|string|Y|蓝牙读特征UUID|
|writeUUID|string|Y|蓝牙写特征UUID|
|scanTimeOut|number|N|蓝牙扫描超时时间,单位/ 毫秒|
|sendTimeOut|number|N|蓝牙发送超时时间,单位/ 毫秒|

#### 代码示例: 

let bleConfig = new DKBleConfiguration(); bleConfig.validMTULength = 224 bleConfig.serviceUUID = "0000FFF0-0000-1000-8000-00805F9B34FB" bleConfig.readUUID = "0000FFF1-0000-1000-8000-00805F9B34FB" bleConfig.writeUUID = "0000FFF2-0000-1000-8000-00805F9B34FB" 

bleConfig.scanTimeOut = 15000 

5 

bleConfig.sendTimeOut = 3000 

DKAuthSDK.getInstance().configeBleService(bleConfig); 

## 4.2. 蓝牙模块 

## 4.2.1 手动连接车辆 

接口名称:public async connectVehicle(): Promise<void> 

接口说明:手动连接车辆包括,蓝牙连接、蓝牙唤醒、蓝牙认证过程。当蓝牙连 接成功、唤醒成功、认证成功以后返回连接车辆成功。如果认证失败,则断开蓝 牙。 

结果说明: 

连接结果监听获取连接状态变更 

public bleConnectStateListener(callback: (type: number, result: boolean, error?: 

DKError) => void) 

代码示例: 

DKAuthSDK.getInstance().connectVehicle().then(() => { 

}).catch(() => { 

}) 

## 4.2.2 断开车辆连接 

接口名称:public async disconnectVehicle(): Promise<void> 

接口说明:手动断开车辆蓝牙连接 

结果说明: 

连接结果监听获取连接状态变更 

public bleConnectStateListener(callback: (type: number, result: boolean, error?: 

DKError) => void) 

代码示例: 

DKAuthSDK.getInstance().disconnectVehicle().then(() => { 

}).catch(() => { 

}) 

6 

## 4.2.3 获取蓝牙状态 

接口名称:public getBleState(): number 

接口说明:获取当前的蓝牙状态 

请求参数说明:无 

返回参数说明:当前蓝牙状态 1 蓝牙已连接,2 蓝牙未连接, 3 蓝牙不可用。 

#### 代码示例: 

DKAuthSDK.getInstance().getBleState() 

## 4.2.4 获取 **PIN** 码 

#### 接口名称:public getBlePin(vin: string): string | undefined 

接口说明:获取蓝牙 passkey 配对模式下,蓝牙连接成功以后输入的配对码 参数说明: 

|名称|类型|必填|说明|
|---|---|---|---|
|vin|String|Y|车辆信息|

#### 返回参数说明:六位 PIN 配对码 

#### 代码示例: 

DKAuthSDK.getInstance().getBlePin("12345678901234567") 

## 4.3. 数字钥匙模块 

## 4.3.1 数字钥匙激活 

接口名称: 

public async activateDigitalKey(vin?: string[], authToken?: string): Promise<string[]> 接口说明:激活数字钥匙,数字钥匙需激活后才能使用。 

参数说明: 

|名称|类型|是否必填|说明|
|---|---|---|---|

7 

|vins|string[]|Y|车辆信息数组|
|---|---|---|---|
|authToken|string|N|用户在数字钥匙激活前需进行|
||||强身份认证,认证成功后身份平|
||||台会返回authToken给客户端。|
||||数字钥匙平台配置查询用户|

#### 返回参数说明: 

success 回调参数: 

|名称 类型|说明|
|---|---|
|ids string[]|与vins 对应的钥匙id 数组|
|failure回调参数: 名称 类型|说明|
|error Error|错误信息|

#### 代码示例: 

DKAuthSDK.getInstance().activateDigitalKey([this.item.vin]).then((dkIds: string[]) => { 

}).catch((err: BusinessError) => { 

}) 

## 4.3.2 数字钥匙下载 

接口名称: 

public async downloadDigitalKey(vin?: string, dkId?: string, authToken?: string): Promise<void> 

接口说明: 

用于车主或被分享者下载数字钥匙。车主激活的数字钥匙被删除后需要调用此接 口重新下载数字钥匙(需要进行强身份认证),被分享者调用此接口下载被分享 的数字钥匙(无需强身份认证)。 

参数说明: 

|名称|类型|是否必填|说明|
|---|---|---|---|
|vin|string|Y|车辆信息|
|dkId|string|Y|数字钥匙ID|
|authToken|string|N|认证Token|
||||用户在数字钥匙激活前需进行 强身份认证,认证成功后身份平 台会返回authToken给客户端。|

8 

数字钥匙平台配置查询用户认 证状态的策略为必选项下,客户 端需携带此参数;否则无需填充 此参数 

返回参数说明: 

failure 回调参数: 

|名称|类型|说明|
|---|---|---|
|error|Error|错误信息|

代码示例: 

DKAuthSDK.getInstance().downloadDigitalKey(vin, this.item.dkID, "").then(() => { 

- }).catch((err: BusinessError) => { 

}); 

## 4.3.3 设置当前钥匙 

#### 接口名称:public async setCurrentDigitalKey(dkId?: string) 

接口说明:当切换车辆时,要设置为当前车辆的钥匙 

请求参数说明: 

|名称|类型|是否必填|说明|
|---|---|---|---|
|dkId|string|Y|钥匙id|

回调方法说明:NULL 

代码示例: 

#### DKAuthSDK.getInstance().setCurrentDigitalKey(dkId) 

## 4.3.4 获取分享限制次数 

接口名称: 

public async getShareDigitalKeyLimit(vin: string): Promise<Record<string, number | undefined>> 

接口说明:获取分享限制的次数 

9 

#### 参数说明: 

|名称|类型||是否必填|说明|
|---|---|---|---|---|
|vin|string||Y|车辆vin|
|返回参数:|||||
|名称|类型|说明|||
|maxAmount|number|最大数量|||
|useAmount|number|已用数量|||
|available|number|可用数量|||

#### 代码示例: 

DKAuthSDK.getInstance().getShareDigitalKeyLimit(vin).then((availeDic: Record<string, number | undefined>) => { 

avalibaleNumber = availeDic["available"] as number 

}).catch((err:BusinessError) => { 

console.log("获取分享次数错误" + err.message); 

}); 

## 4.3.5 获取权限配置信息 

#### 接口名称: 

public async getVehiclePermissions(vin: string, type: number): Promise<DKPermissionModel[]> 

接口说明:当 SDK 已完成初始化。调用此接口,实现获取分享钥匙的权限设置。 参数说明: 

|名称|类型||是否必填 说明|
|---|---|---|---|
|vin|string||Y 车辆VIN|
|type|numb|er|Y 权限类型 0:全部 1:近控 2:远控|
|返回参数:返回 名称|权限列|表数组。 类型|说明|
|permissionType||number|权限类型 1:近控 2:远控|
|permissionMask||string|权限分类掩码|

10 

|permissionDescription|string|权限分类描述|
|---|---|---|
|isChoice|boolean|是否被选中|

#### 代码示例: 

DKAuthSDK.getInstance().getVehiclePermissions(vin, 1).then((list: DKPermissionModel[]) => {}) 

## 4.3.6 数字钥匙分享 

#### 接口名称: 

public async shareDigitalKey(vin: string, permission: DKPermissionModel[], startTime: string, endTime: string, keyType: number, times: number, recipient: string[]) 

接口说明:分享数字钥匙,可以使被分享人使用数字钥匙 

#### 参数说明: 

|名称|类型|必填|说明|
|---|---|---|---|
|vin|string|Y|车辆信息|
|permissions|DKPermissionModel[]|Y|权限信息列表|
|startTime|string|Y|开始时间|
|endTime|string|Y|结束时间|
|keyType|number|Y|钥匙类型(亲友身份1, 临时身份2,试乘试驾3, 租赁类型4)|
|times|number|Y|数字钥匙可用次数, 大于等于0|
|recipient|string[]|Y|接收者信息|

#### 返回参数:返回分享钥匙列表数组。 

|名称|类型|说明|
|---|---|---|
|recipient|string|手机号|
|dkId|string|车辆钥匙Id|

#### 代码示例: 

DKAuthSDK.getInstance().shareDigitalKey(this.vin, permissionList, startTime, endTime, keyType, times, recipient) 

11 

## 4.3.7 数字钥匙撤销分享 

#### 接口名称: 

public async repealShareDigitalKey(vin: string, dkId: string): Promise<void> 

接口说明:撤销分享的数字钥匙 

#### 参数说明: 

|名称|类型|是否必填|说明|
|---|---|---|---|
|vin|string|Y|车辆信息|
|dkId|string|Y|车辆钥匙Id|

#### 代码示例: 

DKAuthSDK.getInstance().repealShareDigitalKey(this.item?.vin ?? "", this.item?.dkId ?? "").then(() => { 

}).catch((err: BusinessError) => { 

}) 

## 4.3.8 获取被分享钥匙列表 

#### 接口名称: 

public async getSharedDigitalKeyList(vin: string = "", type: number, pageNumber: number, pageSize: number): Promise<DKInfoModel[]> 

接口说明:获取被分享数字钥匙列表信息 

参数说明: 

|名称|类型|是否必填|说明|
|---|---|---|---|
|vin|string|Y|车辆信息,空即为全部|
|type|number|Y|钥匙类型 0:全部钥匙 1:有效钥匙(在有效期 内)|
||||2:无效钥匙(冻结,吊|
||||销,过期)|
|pageNum|number|Y|分页参数,0开始|

12 

|pageSize n|umber|Y 每页数量|
|---|---|---|
|返回参数:DKIn|foModel列表||
|名称|类型|说明|
|dkId|string|数字钥匙ID|
|vin|string|车辆VIN|
|mobileId|string|手机标识|
|userId|string|用户id|
|phoneNumber|string|钥匙用户手机号|
|startTime|string|数字钥匙生效时间 yyyy-MM-dd HH:mm:ss|
|endTime|string|数字钥匙到期时间 yyyy-MM-dd HH:mm:ss|
|requestTime|string|激活钥匙请求时间或钥匙分享请求时间 yyyy-MM-dd HH:mm:ss|
|keyType|number|数字钥匙类型(车主身份0,亲友身份1, 临时身份2,试乘试驾3,租赁类型4)|
|times|number|数字钥匙可用次数属性 0标识使用时间,大于0,表示使用次数的 限制。同时,时间限制的功能不变。|
|isDownLoaded|number|是否已下载: 0:未下载; 1:已下载|
|status|number|数字钥匙状态 1:正常 2:冻结 3:吊销 4:过期 5:非正常(钥匙状态已下载,但是本地数 据库没有)|
|changeStatus|number|数字钥匙状态变更原因: 0:正常 1:司机用户删除 2:车辆变更车主|
|permissionList|List<Permission>|权限|

|Permission说明|
|---|

|名称|类型|说明|
|---|---|---|

13 

|permissionMask|string|权限分类掩码|
|---|---|---|
|permissionDescription|string|权限分类描述|

#### 代码示例: 

DKAuthSDK.getInstance().getSharedDigitalKeyList(this.vin, 0, page, 20).then((list: DKInfoModel[]) 

=> { 

}).catch((err: BusinessError) => { 

}) 

## 4.3.9 获取车主钥匙状态 

#### 接口名称: 

public async getOwnerDigitalKeyStatus(vin: string): Promise<Record<string, string | number 

| undefined>> 接口说明:获取车主钥匙状态。返回状态时会返回 dkId,状态 1 正常时调用设 置当前钥匙接口,状态 4 未激活时调用激活接口,状态 5 未下载、6 钥匙更新时 调用下载接口。 #### 参数说明: |名称|类型|是否必填|说明|
|---|---|---|---|
|vin 返回参数:|string|Y|车辆VIN|
|名称|类型|说明||
|status|number|数字钥匙状态 1:正常 2:冻结 3:吊销 4:未激活 5:未下载||
|||6:钥匙更新||
|dkId|string|钥匙id||

#### 代码示例: 

DKAuthSDK.getInstance().getOwnerDigitalKeyStatus(vin) .then((statusDic: Record<string, string | number | undefined>) => { 

14 

}).catch((err:BusinessError) => { 

}); 

## 4.3.10 获取车主授权钥匙列表 

#### 接口名称: 

public async getOwnerAuthorizationDigitalKeyList(vin: string, dkStatus: number, pageNum: number, pageSize: number): Promise<DKInfoModel[]> 接口说明:获取车主授权钥匙列表, 参数说明: 

|名称|类型|是否必填|说明|
|---|---|---|---|
|vin|string|Y|车辆信息|
|dkStatus|number|Y|钥匙状态 0: 全部钥匙 1: 正常状态钥匙 (可 使用)|
||||2: 非正常状态钥匙 (已过期、已冻结、已吊销)|
|pageNum|number|Y|分页参数,从0 开始|
|pageSize|number|Y|页码大小|

#### 返回参数:List 接口 

|名称|类型|说明|
|---|---|---|
|dkId|string|数字钥匙ID|
|vin|string|车辆VIN|
|mobileId|string|手机标识|
|userId|string|用户id|
|phoneNumber|string|钥匙用户手机号|
|startTime|string|数字钥匙生效时间 yyyy-MM-dd HH:mm:ss|
|endTime|string|数字钥匙到期时间 yyyy-MM-dd HH:mm:ss|
|requestTime|string|激活钥匙请求时间或钥匙分享请求时间 yyyy-MM-dd HH:mm:ss|
|keyType|number|数字钥匙类型(车主身份0,亲友身份1, 临时身份2,试乘试驾3,租赁类型4)|
|times|number|数字钥匙可用次数属性 0标识使用时间,大于0,表示使用次数的 限制。同时,时间限制的功能不变。|
|isDownLoaded|number|是否已下载: 0:未下载; 1:已下载|

15 

|status|numb|er|数 1: 2: 3: 4: 5:|字钥匙状态 正常; 冻结; 吊销 过期 未激活|
|---|---|---|---|---|
|permissionList|List<|Permission>|权|限|
|mobileId|strin|g|手|机唯一标识|
|Permission 说明|||||
|名称||类型||说明|
|permissionMask||string||权限分类掩码|
|permissionDescri|ption|string||权限分类描述|

代码示例: 

DKAuthSDK.getInstance().getOwnerAuthorizationDigitalKeyList(vin, 0, pageNum, 20) 

## 4.3.11 删除车主授权钥匙 

接口名称: 

public async deleteOwnerAuthorizationDigitalKey(vin: string, dkIds: string[]) 接口说明:删除车主授权历史钥匙(无效的钥匙) 

#### 参数说明: 

|名称|类型|是否必填|说明|
|---|---|---|---|
|vin|string|Y|车辆信息|
|dkIds|string[]|Y|车辆钥匙Id 数组|

代码示例: 

DKAuthSDK.getInstance().deleteOwnerAuthorizationDigitalKey(vin, dkIds: [dkId]) 

## 4.3.12 获取设备列表 

#### 接口名称: 

public async getDeviceList(vin: string): Promise<Array<DKDeviceModel>> 接口说明:获取数字钥匙的设备的列表 参数说明: 

|名称|类型|是否必填|说明|
|---|---|---|---|
|vin|string|Y|车辆Vin|
|回调方法说明:||||

返回参数说明: 

16 

|名称|类型|说明|
|---|---|---|
|deviceId|string|手机唯一标识|
|mobileName|string|手机名称|
|mobileBrand|string|手机品牌|
|mobileModel|string|手机型号|
|osVersion|string|操作系统版本|
|bindTime|string|设备绑定时间|

代码示例: 

DKAuthSDK.getInstance().getDeviceList(vin).then((lsit: DKDeviceModel[]) => { 

}).catch((err: BusinessError) => { 

}); 

## 4.3.13 设备注销 

接口名称: 

public async cancelDevice(deviceId: string, vin: string) 

接口说明:对指定的车辆指定设备进行注销,注销后的设备不能有任何钥匙的操 作。比方说手机丢失,对丢失的手机进行注销。 

参数说明: 

|名称|类型|是否必|说明|
|---|---|---|---|
|||填||
|deviceId|string|Y|要注销的设备|
||||id|
|vin|string|Y|车辆VIN|

代码示例: 

DKAuthSDK.getInstance().cancelDevice(cell.deviceModel?.mobileId, vin: vin) 

17 

## 4.3.14 蓝牙钥匙推送 

#### 接口名称: 

public async pushDigitalKeyMessage(messageStr: string): Promise<void> 

接口说明:数字钥匙业务推送消息由 App 层的推送通道给到客户端,客户端解 析 sdkMessage 部分信息给到 SDK,SDK 根据推送类型进行相应的处理。(例如 平台注销钥匙推送给 APP,App 解析内容通知 SDK) 

#### 参数说明: 

|名称|类型|是否必填|说明|
|---|---|---|---|
|message|string|Y|推送数据|
||||解析后的|
||||sdkMessage|

#### 代码示例: 

DKAuthSDK.getInstance().pushDigitalKeyMessage(message) 

## 4.3.15 数字钥匙归还 

#### 接口名称: 

public async giveBackDigitalKey(vin: string, dkId: string): Promise<void> 

接口说明:被分享者归还被分享的数字钥匙 

#### 注意:需要被分享者下载钥匙后,才能调用数字钥匙归还。 

#### 参数说明: 

|名称|类型|是否必填|说明|
|---|---|---|---|
|vin|string|Y|车辆信息|
|dkId|string|Y|车辆钥匙Id|

#### 代码示例: 

DKAuthSDK.getInstance().giveBackDigitalKey(model?.vin, dkId: model?.dkId) 

## 4.3.16 日志上传 

#### 接口名称: 

public async controlLogUpload(logList: Record<string, string| number>[]) 

18 

接口说明:控车日志上传接口,由 APP 控制上传的时间和内容。 参数说明: 

|名称|类型|是否必填|说明|
|---|---|---|---|
|logList|Record<string, string||Y|控车日志集合|
||number>[]|||

##### logList 参数说明 

|名称|类型|必填|说明|
|---|---|---|---|
|dkId|string|Y|数字钥匙ID|
|commendControlMes|string|Y|控车指令描述|
|commendSendTime|string|Y|指令下发时间(yyyy-MM-dd HH:mm:ss 格 式)|
|bleConnectStatus|number|Y|蓝牙连接状态(0:未连接;1:已连接)|
|controlResult|string|Y|控车结果|
|commendResTime|string|Y|控车指令响应时间(yyyy-MM-dd HH:mm:ss 格式)|
|userId|string|Y|用户ID|
|phoneNumber|string|Y|用户手机号|
|failureCode|String|Y|失败原因|

代码示例: 

DKAuthSDK.getInstance.controlLogUpload(list) 

## 4.3.17 蓝牙标定参数下载 

接口名称: 

public async calibrationParamDownload(vin: string): Promise<number> 

接口说明:手机下载车型标定参数,如果平台存在指定车型以及机型的标定参数, 下发指定的,否则下载默认参数,默认参数不存在的情况返回空值,正常情况下 标定参数随数字钥匙一起下发,当车型的标定参数有更新时,可通过该接口更新 标定参数。 

参数说明: 

|名称|类型|是否必填|说明|
|---|---|---|---|
|vin|string|Y|车辆VIN 号|

#### 返回参数说明: 

success 回调参数: 

|名称 类型 说明|
|---|

19 

|result|number|0: 平台下发标定数据为空|
|---|---|---|
|||1: 下载成功|

#### 代码示例: 

DKAuthSDK.getInstance().calibrationParamDownload(vin).then((result) => { 

if (result == 1) { 

Prompt.showToast({message: "下载成功"}) 

} else { 

Prompt.showToast({message: "平台标定数据为空"}) 

} 

}).catch((err: Error) => { 

}) 

## 4.3.18 获取标定参数 

#### 接口名称: 

public async getCalibrationParam(dkId: string): Promise<DKCalibrationParam> 

接口说明:获取数字钥匙的标定参数,用户自标定后返回用户标定后的参数,用 户未自标定过,返回下载的默认参数。 

#### 参数说明: 

|名称|类型|是否必填|说明|
|---|---|---|---|
|dkId|string|Y|数字钥匙ID|

#### 返回参数说明: 

|名称|类型|说明|
|---|---|---|
|param DKCalibration|DKCalibration Param说明:|Param 返回的参数数据实体|
|名称|类型|说明|
|carInsider|number|车内|
|leftUnlock|number|左解锁|

20 

|rightUnlock|number|右解锁|
|---|---|---|
|tailUnlock|number|尾解锁|
|leftLock|number|左闭锁|
|rightLock|number|右闭锁|
|tailLock|number|尾闭锁|
|allLock|number|全局闭锁|
|calibrationTag|number|返回的状态值0: 下载的标定值1: 自标定值|

#### 代码示例: 

DKAuthSDK.getInstance().getCalibrationParam(this.dkId).then((param) => { 

}).catch((err: BusinessError) => { 

}) 

## 4.3.19 修改用户自标定参数 

#### 接口名称: 

public async modifyUserCalibrationParam(dkId: string, calibrationParam: 

DKCalibrationParam): Promise<void> 

接口说明:此接口的功能是用户自标定修改完成后,保存参数接口。 注意:修改完后要调用设置当前钥匙接口后才生效 注意:标定参数范围为5-99 

参数说明: 

|名称|类型|是否必填|说明|
|---|---|---|---|
|dkId|string|Y|钥匙ID|
|calibrationParam|DKCalibrationParam|Y|保存的用户参数实体|

##### DKCalibrationParam 说明: 

|名称|类型|说明|
|---|---|---|
|carInsider|number|车内|
|leftUnlock|number|左解锁|

21 

|rightUnlock|number|右解锁|
|---|---|---|
|tailUnlock|number|尾解锁|
|leftLock|number|左闭锁|
|rightLock|number|右闭锁|
|tailLock|number|尾闭锁|
|allLock|number|全局闭锁|

#### 代码示例: 

DKAuthSDK.getInstance().modifyUserCalibrationParam(self.dkId, calibrationParam: model) 

## 4.3.20 恢复标定参数 

#### 接口名称: 

public async recoverCalibrationParam(dkId: string): Promise<void> 

接口说明:将用户自标定参数恢复为下载的参数,覆盖用户的标定结果。参数修 改后,如需立即生效需要调用设置默认钥匙接口。 

参数说明: 

|名称|类型|是否必填|说明|
|---|---|---|---|
|dkId|string|Y|钥匙ID|

#### 代码示例: 

DKAuthSDK.getInstance.recoverCalibrationParam(self.dkId) 

## 4.4. 指令模块 

## 4.4.1 蓝牙发送指令 

#### 接口名称: 

public sendCommand(instruction: string, permissionMask?: string, type: number = 1) 

22 

接口说明:在认证完成后,对指令进行封装,并把封装好的指令发送到 Tbox。 参数说明: 

|名称|类型|是否必填|说明|
|---|---|---|---|
|instruction|string|Y|原始的指令|
|permissionMask|string|N|权限掩码(2个字节 Hex 编码0xFF0xFF)|
|type|number|Y|指令类型: 1:控车指令 2:数据传输指令|

#### 代码示例: 

DKAuthSDK.getInstance().sendCommand(“0101”, “0000”, 2) 

## 4.4.2 蓝牙指令监听 

#### 接口名称: 

public commandResponseListener(callback: (type: number, data?: Uint8Array, error?: DKError) => void) 

接口说明:在认证完成后,监听 Tbox 返回的数据,返回解析成功后数据。 返回参数说明: 

void callback(type: number, data?: Uint8Array, error?: DKError) 

#### 参数说明: 

|名称|类型|说明|
|---|---|---|
|type|number|指令类型:1:控车指令 2:数据传输指令|
|data|Uint8Array|解析后的Tbox端返回的数据|
|error|DKError|发送失败错误描述|

23 

## 4.5. 缓存清理 

## 4.5.1 清空数据 

接口名称:public async clearData() 

接口说明:清空 SDK 的数据(vin、数字钥匙、通信密钥、身份密钥) 代码示例: 

DKAuthSDK.getInstance().clearData() 

# 5. 附录 

## 5.1. 错误码 

|错误码|错误描述|
|---|---|
|基础库错误||
|10000001|参数为空或NULL|
|10000002|CRC校验错误|
|10000003|SLIP帧,帧头帧尾错误|
|10000004|VIN校验错误|
|10000005|MobileId校验错误|
|10000006|DKID校验错误|
|10000007|数据长度校验错误|
|10000008|命令号错误|
|10000009|计数器错误|
|10000010|身份密钥不存在|
|10000011|认证密钥不存在|
|10000012|认证密钥校验错误|
|10000013|会话密钥不存在|
|10000014|无效数据|

24 

|10000015|密钥需要更新|
|---|---|
|10000016|蓝牙特征交换错误|
|10000017|双向身份认证手机端随机数不匹配|
|10000018|域名错误|
|10000019|数据库为空|
|10000020|数据库保存失败|
|10000021|临时密钥为空|
|数字钥匙库错误 ||
|11000001|SDK未初始化|
|11000002|蓝牙不可用|
|11000003|蓝牙厂商配置未初始化|
|11000004|参数为空或NULL|
|11000005|参数不在范围内|
|11000006|DKID校验错误|
|11000007|本地mobileId和dk中的mobileId不一致|
|11000008|钥匙有效期过期|
|11000009|钥匙未到使用时间|
|11000010|蓝牙设备未找到|
|11000011|蓝牙连接超时|
|11000012|蓝牙唤醒失败|
|11000013|认证失败|
|11000014|蓝牙未连接|
|11000015|发送超时|
|11000016|指令发送失败|
|11000017|数据库为空|
|11000018|网络错误|
|11000019|网络请求参数不正确|

25 

|11000020|报文解析错误|
|---|---|
|11000021|主密钥不存在|
|11000022|平台未返回签名值|
|11000023|平台返回签名值验签不通过|
|11000024|网络数据格式不正确|
|11000025|格式错误|
|11000026|开始时间大于结束时间|

26
