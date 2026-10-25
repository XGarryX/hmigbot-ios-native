# HY Harmony Common ESC vN.L.L接口文档 

##### 文档修改记录 

一.使用说明 

N.N工程配置说明 

二.样列演示 

O.N连接打印机流程 

O.N.N搜索打印机 

O.N.O蓝牙连接打印机 

三.接口说明 

P.N.N创建连接 

P.N.O蓝牙连接 

P.N.PWIFI连接 

P.N.QUSB连接 

P.N.S连接状态 

P.N.T断开连接 

P.O.N创建打印 

P.O.O设置SDK字符编码 

P.O.P打印文本 

P.O.Q设置字体样式 

P.O.S设置对齐方式 

P.O.T初始化打印机 

P.O.V设置字体缩放 

P.O.W打印图片 

P.O.X定位 

P.O.NL走纸 

P.O.NN设置行间距 

P.O.NO设置打印机编码 

P.O.NP设置页模式 

P.O.NQ设置页模式打印区域 

1 

P.O.NS清除页模式缓存数据 

P.O.NT设置页模式打印方向 

P.O.NV设置页模式绝对位置 

P.O.NW发送页模式打印数据 

P.O.NX获取打印机状态 

P.O.OL设置打印浓度 

P.O.ON设置打印速度 

P.O.OO设置走纸切刀 

P.O.OP打开钱箱 

P.O.OQ开启蜂鸣器 

P.O.OS打印条码 

P.O.OS打印二维码 

P.O.OT打印PDFQNV 

P.O.OV获取打印机序列号 

P.O.OW获取打印机电量 

P.O.OX获取打印机版本号 

Q.N.N编码表 

Q.N.O条码类型 

## 文档修改记录 

|序号|版本号|修改内容|修改者|修改日期|
|---|---|---|---|---|
|01|v1.0.0|文档建立|邱贤|2025-03-05|

## 一 .使用说明 

### 1.1工程配置说明 

##### 1.本SDK接口需运行在鸿蒙系统上 

2.把CommonLib.har放到工程entry/src目录下, oh-package.json5增加引入har 

2 

JSON 

- `"dependencies": { 2 "package": "file:./src/CommonLib.har" 3 }` 

##### 3.蓝牙权限配置 

entry/src/main/module.json5中配置 JSON 

- `"requestPermissions": [{` 

- `"name": "ohos.permission.ACCESS_BLUETOOTH",` 

- `"reason": "$string:app_name",` 

- `"usedScene": {` 

- `"abilities": ["EntryAbility"]` 

- `} 7 }]` 

在代码中动态配置定位权限 ArkTS 

- `reqPermissionsFromUser(permissions: Array<Permissions>): void {` 

- `let context: Context = getContext(this) as common.UIAbilityContext;` 

- `let atManager: abilityAccessCtrl.AtManager =` 

- `abilityAccessCtrl.createAtManager();` 

- `// requestPermissionsFromUser` 会判断权限的授权状态来决定是否唤起弹窗 

- `atManager.requestPermissionsFromUser(context, permissions)` 

- `.then((data: PermissionRequestResult) => {` 

- `let grantStatus: Array<number> = data.authResults;` 

- `let length: number = grantStatus.length;` 

- `for (let i = 0; i < length; i++) {` 

- `if (grantStatus[i] === 0) {` 

- `//` 用户授权,可以继续访问目标操作 

- `console.log('` 用户授权,可以继续访问目标操作 `');` 

- `router.pushUrl({ url: 'pages/BTConnect' }).then(() => {` 

- `console.info('Succeeded in jumping to the second page.')` 

- `16` 

- `}).catch((err: BusinessError) => {` 

- `} else {` 

- `return;` 

- `} 21 }` 

- `}).catch((err: BusinessError) => { 23 }) 24 }` 

3 

## 二.样列演示 

### 2.1连接打印机流程 

#### 2.1.1搜索打印机 

4 

ArkTS 

- `import connection from '@ohos.bluetooth.connection'; 2 //` 蓝牙搜索回调( `data` 是加密后的蓝牙地址) `3 connection.on('bluetoothDeviceFind', (data) => { 4 for (let i = 0; i < data.length; i++) { 5 let name = connection.getRemoteDeviceName(data[i])//` 获取蓝牙名字 `6 if (name) { 7 let remoteDeviceClass: connection.DeviceClass = 8 connection.getRemoteDeviceClass(data[i]) 9 if (remoteDeviceClass.classOfDevice == 1050240) {//` 过滤掉不是打印机的蓝 牙 

- `this.macList.push(data[i]) 11 } 12 } 13 } 14 }); 15 connection.startBluetoothDiscovery();//` 开启搜索 

#### 2.1.2蓝牙连接打印机 

ArkTS 

- `import {BTConnection, BaseConnection} from 'package'; 2 baseConnect: BaseConnection = new BTConnection() 3 this.baseConnect.connectBT(info, { 4 connectSucceed() {` 

- `index.message = "` 连接成功 `" 6 promptAction.showToast({ 7 message: '` 连接成功 `', 8 duration: 2000 9 })` 

- `index.helper = new PrinterESCHelper(index.baseConnect) 11 }, 12 connectFail(message: string, errCode: number) { 13 index.message = "` 连接失败 `" 14 promptAction.showToast({ 15 message: '` 连接失败 `' + message, 16 duration: 2000 17 }) 18 } 19 })` 

## 三.接口说明 

5 

### 3.1.1创建连接 

ArkTS 

- `import {BTConnection, BaseConnection} from 'package';` 

- `2` 

- `baseConnect: BaseConnection = new BTConnection()//` 创建蓝牙连接 

- `this.baseConnect = new WifiConnection();//` 创建 `WIFI` 连接 

- `this.baseConnect = new USBConnection();//` 创建 `USB` 连接 

### 3.1.2蓝牙连接 

- 描述 

蓝牙连接 

ArkTS 

- `connectBT(deviceId: string, listener: ConnectListener)` 

- 参数 

参数 描述 deviceId 蓝牙地址(搜索出来的) listener 回调监听 

- 例子 

6 

ArkTS 

`1 this.baseConnect.connectBT(info, { 2 connectSucceed() { 3 index.message = "` 连接成功 `" 4 promptAction.showToast({ 5 message: '` 连接成功 `', 6 duration: 2000 7 }) 8 index.helper = new PrinterESCHelper(index.baseConnect) 9 }, 10 connectFail(message: string, errCode: number) { 11 index.message = "` 连接失败 `" 12 promptAction.showToast({ 13 message: '` 连接失败 `' + message, 14 duration: 2000 15 }) 16 } 17 })` 

### 3.1.3WIFI连接 

- 描述 

- 用wifi和以太网连接打印机,注意该接口需要调用权限 'ohos.permission.INTERNET',具体可以参考 

- Demo 

ArkTS `1 connectWifi(ip: string, listener: ConnectListener)` ● 参数 参数 描述 ip IP地址 listener 回调监听 

- 例子 

7 

ArkTS 

- `//` 创建 `wifi` 连接 

- `this.baseConnect = new WifiConnection();` 

- `this.baseConnect.connectWifi(this.ip, {` 

- `connectSucceed: async (): Promise<void> => {` 

- `await PreferencesUtil.saveData(IP, this.ip)` 

- `promptAction.showToast({` 

- `message: $r('app.string.connect_success'), 8 duration: 2000` 

- `});` 

- `PrinterHelp.baseConnect = this.baseConnect; 11 loadingDialog.close()` 

- `}, 13 connectFail: (message: string, errCode: number): void => {` 

- `promptAction.showToast({` 

- `message: $r('app.string.connect_fail') + message, 16 duration: 2000` 

- `});` 

- `loadingDialog.close() 19 } 20 });` 

### 3.1.4USB连接 

- 描述 

   - 用USB连接打印机 

|ArkTS|
|---|

- `connectUSB(device: usbManager.USBDevice, listener: ConnectListener)` 

##### ● 参数 

|参数|描述|
|---|---|
|device|需要连接的USB对象,由系统生成,可以通过系 统列表获取。|
|listener|回调监听|

> ● 例子 

8 

ArkTS 

- `//` 创建 `USB` 连接 

- `this.baseConnect = new USBConnection() 3 this.baseConnect.connectUSB(deviceList[0], { 4 connectSucceed: (): void => {` 

- `promptAction.showToast({` 

- `message: $r('app.string.connect_success'), 7 duration: 2000 8 }) 9 PrinterHelp.baseConnect = this.baseConnect` 

- `}, 11 connectFail: (message: string, errCode: number): void => { 12 promptAction.showToast({ 13 message: $r('app.string.connect_fail') + message, 14 duration: 2000 15 }) 16 } 17 })` 

### 3.1.5连接状态 

##### ● 描述 

ArkTS 

- `isConnect(): boolean` 

##### ● 例子 

ArkTS 

- `this.baseConnect.isConnect() 2 //true` 已连接 `3 //false` 未连接 

### 3.1.6断开连接 

- 描述 

9 

ArkTS

1 disConnect(): boolean
● 例子
ArkTS
1 this.baseConnect.disConnect()

### 3.2.1创建打印 

● 描述

ArkTS

- `import {PrinterESCHelper} from 'package'; 2 3 helper: PrinterESCHelper = new PrinterESCHelper(this.baseConnect)` 

● 参数

参数 描述 connect: BaseConnection 连接对象 

### 3.2.2设置SDK字符编码 

- 描述 

- 设置SDK所需的字符编码,例如中文设置GB2312 

ArkTS

```
1public setLanguageEncode(languageEncode: string)
```

- 参数 

10 

参数 描述 languageEncode 编码(例:GBK)详情可以查看4.1.1 

##### ● 例子 

ArkTS 

- `this.helper.setLanguageEncode('GBK')` 

### 3.2.3打印文本 

- 描述 

向打印机发送文本数据,该接口可以设置对齐方式,字体样式,字体缩放, 

ArkTS 

- `public printText(data: string, alignment: number, isFontSmall: boolean, 2 isBold: boolean, isUnderline: boolean, isTurnWhite: boolea n,` 

- `widthMultiplier: number, heightMultiplier: number): boolea n` 

##### ● 参数 

|参数|描述|
|---|---|
|data|文本数据|
|alignment|对齐方式(0:左对齐,1:居中,2:右对齐)|
|isFontSmall|是否使用小字体 (小字体:9X17,大字体: 12X24)|
|isBold|是否加粗|
|isUnderline|是否使用下划线|
|isTurnWhite|是否反白|
|widthMultiplier|字体横向放大倍数(0-8)最大倍数跟随打印机|
|heightMultiplier|字体纵向放大倍数(0-8)最大倍数跟随打印机|

11 

> ● 返回 

值 描述 true 发送成功 false 发送失败 ● 例子 ArkTS 

- `this.helper.printText("text",1, false, false, false, false, 1, 1)` 

### 3.2.4设置字体样式 

- 描述 

- 该接口用于给文本数据添加字体样式,但是对于printText接口无效,printText自身已有设置字体样式 

的参数 

ArkTS 

- `public setFontStyle(isFontSmall: boolean, isBold: boolean, 2 isUnderline: boolean): boolean` 

- 参数 

|参数|描述|
|---|---|
|isFontSmall|是否使用小字体 (小字体:9X17,大字体: 12X24)|
|isBold|是否加粗|
|isUnderline|是否使用下划线|

- 返回 

值 

描述 

12 

true 发送成功 false 发送失败 

##### ● 例子 

ArkTS

- `this.helper.setFontStyle(true, true, true) 2 this.baseConnect.writeData(UintUtils.stringToBuffer('Test\r\n').buffer)` 

### 3.2.5设置对齐方式 

- 描述 

- 该接口用于设置整体的对齐方式,但是对于一些接口本身有带设置对齐方式的无效(例如: printText,printImage,printBarCode,printQRCode等) 

ArkTS 

- `public setAlignment(alignment: number): boolean` 

- 参数 

|参数|描述|
|---|---|
|alignment|对齐方式(0:左对齐,1:居中,2:右对齐)|

- 返回 

值 描述 true 发送成功 false 发送失败 

- 例子 

13 

ArkTS 

- `this.helper.setAlignment(1) 2 this.baseConnect.writeData(UintUtils.stringToBuffer('Test\r\n').buffer)` 

### 3.2.6初始化打印机 

● 描述
该接口可以初始化打印机,清除字体样式,对齐方式等等。
ArkTS
1 public setInitialize(): boolean
● 返回
值 描述
true  发送成功
false  发送失败
● 例子
ArkTS
1 this.helper.setInitialize()

### 3.2.7设置字体缩放 

- 描述 

- 该接口用于给文本数据进行字体的放大,但是对于printText接口无效,printText自身已有设置字体放 

- 大的参数 

ArkTS

- `public setFontMultiplier(widthMultiplier: number, heightMultiplier: number) 2 : boolean` 

14 

##### ● 参数 

|参数|描述|
|---|---|
|widthMultiplier|字体横向放大倍数(0-8)最大倍数跟随打印机|
|heightMultiplier|字体纵向放大倍数(0-8)最大倍数跟随打印机|
|例子 ●|ArkTS|

- `this.helper.setFontMultiplier(1,1) 2 this.baseConnect.writeData(UintUtils.stringToBuffer('Test\r\n').buffer)` 

### 3.2.8打印图片 

- 描述 

- 该接口可以图片打印,可以设置对齐方式,图片算法 200dpi的打印机  8点 = 1毫米 

   - 300dpi的打印机  11.8点 = 1毫米 

ArkTS 

- `public async printImage(alignment: number, imageType: ImageTypeEnum, 2 pm: image.PixelMap): Promise<boolean>` 

##### ● 参数 

|参数|描述|
|---|---|
|alignment|对齐方式(0:左对齐,1:居中,2:右对齐)|
||图片算法|
|imageType|ImageTypeEnum.Threshold:二值|
||ImageTypeEnum.RasterMono:抖动|
|pm|图片|

15 

> ● 例子 

ArkTS

```
1await this.helper.printImage(1,  ImageTypeEnum.RasterMono, pixelMap)
```

### 3.2.9定位 

● 描述
该接口可以在打印标签或者黑标时用于定位功能
ArkTS
1 public setPositioning(): boolean
● 返回
值 描述
true  发送成功
false  发送失败
● 例子
ArkTS
1 this.helper.setPositioning()
3.2.10走纸
● 描述
该接口可以让打印机按你设置的行数走纸
ArkTS
1 public setFeedLine(lines: number): boolean

> ● 参数 

16 

|参数|描述|
|---|---|
|lines|走纸行数|
|返回 ●||
|值|描述|
|true|发送成功|
|false|发送失败|
|例子 ●||
||ArkTS|
|`this.helper.setFeedLine(100)` `1`||

### 3.2.11设置行间距 

- 描述 

- 该接口用于设置行间距,单位是行 

ArkTS 

`1 public setLineSpace(lineSpace: number): boolean` ● 参数 参数 描述 lineSpace 行间距(单位:行) ● 返回 值 描述 true 发送成功 

17 

发送失败 

false 

> ● 例子 

ArkTS 

- `this.helper.setLineSpace(2)` 

### 3.2.12设置打印机编码 

- 描述 

   - 该接口可以用于设置打印机编码 

ArkTS 

- `public setPrinterCharacter(character: number): boolean` 

##### ● 参数 

|参数|描述|
|---|---|
|character|打印机编码代号(详情查看4.1.1)|

##### ● 返回 

|值|描述|
|---|---|
|true|发送成功|
|false|发送失败|
|例子 ●|ArkTS|

- `this.helper.setPrinterCharacter(1)` 

### 3.2.13设置页模式 

18 

● 描述
该接口是让打印机进入页模式

ArkTS
1 public setSelectPageMode(): boolean
● 返回
值 描述
true  发送成功
false  发送失败
● 例子
ArkTS

- `this.helper.setSelectPageMode();//` 进入页模式 `2 this.helper.setClearPageModePrintAreaData();//` 清除页面模式缓存数据 `3 this.helper.setPageModePrintArea(0,0,200,200);//` 设置打印区域 `4 this.helper.setPageModePrintDirection(0);//` 设置打印方向 `5 this.helper.setPageModeAbsolutePosition(0,0);//` 设置打印起始坐标 `6 this.helper.setQRCode("Test print QRCode",6, 48, 1);//` 打印二维码 `7 this.helper.setPrintPageModeData();//` 设置打印 

### 3.2.14设置页模式打印区域 

● 描述
该接口用于创建页模式的画布,可以设置起始位置和宽高

ArkTS

- `public setPageModePrintArea(horizontal: number, vertical: number, 2 width: number, height: number): boolean` 

● 参数

参数 

描述 

19 

|horizontal|起始点横坐标(单位:点)|
|---|---|
|vertical|起始点纵坐标(单位:点)|
|width|区域宽度(单位:点)|
|height|区域高度(单位:点)|
|返回 ●||
|值|描述|
|true|发送成功|
|false|发送失败|
|例子 ●||
||ArkTS|

- `this.helper.setSelectPageMode();//` 进入页模式 `2 this.helper.setClearPageModePrintAreaData();//` 清除页面模式缓存数据 

- `this.helper.setPageModePrintArea(0,0,200,200);//` 设置打印区域 

- `this.helper.setPageModePrintDirection(0);//` 设置打印方向 

- `this.helper.setPageModeAbsolutePosition(0,0);//` 设置打印起始坐标 

- `this.helper.setQRCode("Test print QRCode",6, 48, 1);//` 打印二维码 `7 this.helper.setPrintPageModeData();//` 设置打印 

### 3.2.15清除页模式缓存数据 

- 描述 

- 该接口可以清除上一次的页模式缓存的数据,最好是在为创建页模式打印区域前使用 

ArkTS

- `public setClearPageModePrintAreaData(): boolean` 

- 返回 

值 

描述 

20 

true 发送成功 false 发送失败 

● 例子

ArkTS

- `this.helper.setSelectPageMode();//` 进入页模式 `2 this.helper.setClearPageModePrintAreaData();//` 清除页面模式缓存数据 

- `this.helper.setPageModePrintArea(0,0,200,200);//` 设置打印区域 

- `this.helper.setPageModePrintDirection(0);//` 设置打印方向 

- `this.helper.setPageModeAbsolutePosition(0,0);//` 设置打印起始坐标 

- `this.helper.setQRCode("Test print QRCode",6, 48, 1);//` 打印二维码 `7 this.helper.setPrintPageModeData();//` 设置打印 

### 3.2.16设置页模式打印方向 

- 描述 

- 该接口用于设置页模式里面的打印方向 

ArkTS 

- `public setPageModePrintDirection(direction: number): boolean` 

- 参数 

参数 描述 direction 方向(0:从左到右,1:从下到上,2:从右到左,3:从上到 下) 

- 返回 

值 描述 true 发送成功 false 发送失败 

21 

> ● 例子 

1
2
3
4
5
6
7

- `this.helper.setSelectPageMode();//` 进入页模式 

- `this.helper.setClearPageModePrintAreaData();//` 清除页面模式缓存数据 

- `this.helper.setPageModePrintArea(0,0,200,200);//` 设置打印区域 

- `this.helper.setPageModePrintDirection(0);//` 设置打印方向 

- `this.helper.setPageModeAbsolutePosition(0,0);//` 设置打印起始坐标 

- `this.helper.setQRCode("Test print QRCode",6, 48, 1);//` 打印二维码 

- `this.helper.setPrintPageModeData();//` 设置打印 

### 3.2.17设置页模式绝对位置 

- 描述 

- 该接口用于页模式下设置打印点的绝对位置,设置完该接口后,再跟随一个打印内容,那么该内容就 

- 可以在这个位置上打印。 

ArkTS 

- `public setPageModeAbsolutePosition(xPosition: number, yPosition: number): b oolean` 

##### ● 参数 

|参数|描述|
|---|---|
|xPosition|打印横坐标|
|yPosition|打印纵坐标|

- 返回 

|值|描述|
|---|---|
|true|发送成功|
|false|发送失败|

> ● 例子 

22 

ArkTS 

- `this.helper.setSelectPageMode();//` 进入页模式 

- `this.helper.setClearPageModePrintAreaData();//` 清除页面模式缓存数据 

- `this.helper.setPageModePrintArea(0,0,200,200);//` 设置打印区域 

- `this.helper.setPageModePrintDirection(0);//` 设置打印方向 

- `this.helper.setPageModeAbsolutePosition(0,0);//` 设置打印起始坐标 

- `this.helper.setQRCode("Test print QRCode",6, 48, 1);//` 打印二维码 `7 this.helper.setPrintPageModeData();//` 设置打印 

### 3.2.18发送页模式打印数据 

- 描述 

- 该接口用于让打印机知道打印页模式下储存的数据 

ArkTS 

- `public setPrintPageModeData(): boolean` 

> ● 返回 值 描述 true 发送成功 false 发送失败 

● 例子

- `this.helper.setSelectPageMode();//` 进入页模式 `2 this.helper.setClearPageModePrintAreaData();//` 清除页面模式缓存数据 `3 this.helper.setPageModePrintArea(0,0,200,200);//` 设置打印区域 

- `this.helper.setPageModePrintDirection(0);//` 设置打印方向 `5 this.helper.setPageModeAbsolutePosition(0,0);//` 设置打印起始坐标 `6 this.helper.setQRCode("Test print QRCode",6, 48, 1);//` 打印二维码 `7 this.helper.setPrintPageModeData();//` 设置打印 

23 

### 3.2.19获取打印机状态 

##### ● 描述 

该接口可以获取打印机的开合盖和纸张状态 

ArkTS

- `public getPrinterStatus(listener: PrinterStatusListener)` 

##### ● 参数 

参数 listener 

描述 打印机状态回调 

##### ● 状态 

code  description  说明
0  normal  打印机正常
1  no paper  缺纸
2  open lid  开盖

- 例子 

ArkTS 

- `this.helper.getPrinterStatus({ 2 onStatus(status: Array<PrinterStatus>){ 3 if (status) {` 

- `for (let i = 0; i < status.length; i++) { 5 promptAction.showToast({ message: status[i].description, durat ion: 2000 })` 

- `} 7 } 8 }, 9 onFail(message: string){` 

- `promptAction.showToast({ message: message, duration: 2000 }) 11 } 12 })` 

24 

### 3.2.20设置打印浓度 

##### ● 描述 用于添加打印机浓度,但是不同的机型会有不同的浓度范围,详情咨询客服 

|`public setPrintDensity(density: number): boolean` `1` ArkTS|
|---|
|参数 ●|
|参数 描述|
|density 打印浓度,范围根据机型而定|
|返回 ●|
|值 描述|
|true 发送成功|
|false 发送失败|
|例子 ●|
|ArkTS|
|`this.helper.setPrintDensity(1)` `1`|

### 3.2.21设置打印速度 

- 描述 

- 用于添加打印速度,但是不同的机型会有不同的速度范围,详情咨询客服 

ArkTS 

```
1public setPrintSpeed(speed: number): boolean
```

25 

> ● 参数 

|参数|描述|
|---|---|
|speed|打印速度,范围根据机型而定|
|返回 ●||
|值|描述|
|true|发送成功|
|false|发送失败|
|例子 ●||
||ArkTS|
|`this.helper.setPrintSpeed(1)` `1`||

### 3.2.22设置走纸切刀 

|描述 该接口可以用于走纸后切刀 ●||
|---|---|
||ArkTS|
|`public setCutterPaperFeedin` `1`|`g(cutMode: number, distance: number): boolean`|
|参数 ●||
|参数|描述|
|cutMode|切刀模式(0:半切,1:全切)|
|distance|走纸距离(0-255单位点)|

> ● 返回 

26 

|值|描述|
|---|---|
|true|发送成功|
|false|发送失败|
|例子 ●||
||Kotlin|

- `this.helper.setCutterPaperFeeding(0, 100)` 

### 3.2.23打开钱箱 

- 描述 

- 该接口用于打开跟打印机连接的钱箱 

ArkTS

- `public openCashDrawer(openMode: number): boolean` 

- 参数 

参数 描述 openMode 0:打开1号钱箱,1:打开2号钱箱,2:打开全部 钱箱 

> ● 返回 值 描述 true 发送成功 false 发送失败 

- 例子 

27 

ArkTS 

- `this.helper.openCashDrawer(0)` 

### 3.2.24开启蜂鸣器 

##### ● 描述 

##### 该接口用于让蜂鸣器鸣叫 

|ArkTS|
|---|

- `public openBeepBuzzer(times: number, t1: number, t2: number): boolean` 

##### ● 参数 

|参数|描述|
|---|---|
|times|蜂鸣器响的次数|
|t1|响的时间(单位100ms)|
|t2|停止时间(单位100ms)|

##### ● 返回 

|值|描述|
|---|---|
|true|发送成功|
|false|发送失败|

##### ● 例子 

- ArkTS 

- `this.helper.openBeepBuzzer(1, 2, 2)` 

### 3.2.25打印条码 

28 

- 描述 

- 该接口用于打印条码,可以打印 UPC-A,UPC-E,JAN13/EAN13,JAN8/EAN8,CODE39, 

- ITF,CODABAR(NW-7),CODE93,CODE128类型的条码 

ArkTS 

- `public printBarCode(bcType: ESCBarcodeEnum, bcData: string, 2 width: number, height: number, 3 hriPosition: number, alignment: number): boolean` 

##### ● 参数 

|参数|描述|
|---|---|
|bcType|条码类型(详情查看表4.1.2)|
|bcData|条码内容|
|width|条码宽度(1-6等级)|
|height|条码高度(1-255等级)|
|hriPosition|文本位置 (0:不打印,1:条码上方,2:条码下方,3:条码上方及下方)|
|alignment|对齐方式(0:左对齐,1:居中,2:右对齐)|

##### ● 例子 

ArkTS 

- `this.helper.printBarCode(ESCBarcodeEnum.BC_UPCA, '075678164125', 2, 50, 2, 0)` 

### 3.2.25打印二维码 

- 描述 

- 该接口用于打印二维码 

29 

ArkTS 

- `public printQRCode(qrData: string, sizeOfModule: number, errorLevel: numbe r,` 

- `alignment: number): boolean` 

##### ● 参数 

|参数|描述|
|---|---|
|qrData|二维码内容|
|sizeOfModule|尺寸(1-16等级)|
|errorLevel|纠错等级(48-51,对应L,M,Q,R)|
|alignment|对齐方式(0:左对齐,1:居中,2:右对齐)|

##### ● 返回 

|值|描述|
|---|---|
|true|发送成功|
|false|发送失败|

##### ● 例子 

ArkTS 

- `this.helper.printQRCode("Test print QRCode",6, 48, 1)` 

### 3.2.26打印PDF417 

- 描述 

   - 该接口用于打印PDF417码 

30 

ArkTS 

- `public printPDF417(data: string, dataColumns: number, dataRows: number, 2 moduleWidth: number, rowHeight: number, errorMode: numbe r,` 

- `errorLevel: number, options: number): boolean` 

##### ● 参数 

|参数|描述|
|---|---|
|data|数据内容|
|dataColumns|设置列数(0-30)0:自动处理,根据数据来确定列数|
|dataRows|设置行数(0,3-90)0:自动处理,根据数据来确定 行数|
|moduleWidth|设置模块宽度(2-8)|
|rowHeight|设置模块高度(2-8)|
|errorMode|纠错模式(48:等级模式,49:比率模式)|
|errorLevel|纠错等级(详情查看4.1.3)|
|options|模式(0:标准模式,1:压缩模式)|

##### ● 返回 

|值|描述|
|---|---|
|true|发送成功|
|false|发送失败|

##### ● 例子 

ArkTS 

```
1this.helper.printPDF417("123456",0, 0, 3, 3, 49, 1, 0)
```

31 

### 3.2.27获取打印机序列号 

● 描述
该接口可以用于获取打印机的序列号

ArkTS

- `public getPrinterSN(listener: PrinterSNListener)` 

2
3 export interface PrinterSNListener{
4     onPrinterSN(sn: string): void// 打印机序列号
5     onFail(message: string): void// 错误信息
6 }
● 参数
参数 描述
listener  监听回调
● 例子
ArkTS
1 this.helper.getPrinterSN({
2       onPrinterSN(sn: string){
3         promptAction.showToast({ message: "sn:"+sn, duration: 2000 })
4       },
5       onFail(message: string){
6         promptAction.showToast({ message: message, duration: 2000 })
7       }
8     })

### 3.2.28获取打印机电量 

- 描述 

- 该接口获取打印机电量百分比,该接口只适用于部分带电池的打印机 

32 

ArkTS 

- `public getPrinterQuantity(listener: ElectricityListener) 2 3 export interface ElectricityListener{ 4 onElectricity(electricity: number): void//` 电量百分比 `5 onFail(message: string): void//` 错误信息 `6 }` 

● 参数
参数 描述
listener  监听回调
● 例子
ArkTS
1 this.helper.getPrinterQuantity({
2       onElectricity(electricity: number){
3         promptAction.showToast({ message: "electricity:"+electricity, durat
ion: 2000 })
4       },
5       onFail(message: string){
6         promptAction.showToast({ message: message, duration: 2000 })
7       }
8     })

- 3.2.29获取打印机版本号 ● 描述 该接口获取打印机版本号 

- `public getPrinterVersion(listener: PrinterVersionListener) 2 3 export interface PrinterVersionListener{ 4 onVersion(version: string): void//` 打印机版本号 `5 onFail(message: string): void//` 错误信息 `6 }` 

ArkTS

33 

##### ● 参数 

|参数|描述|
|---|---|
|listener|监听回调|
|例子 ●|ArkTS|

- `this.helper.getPrinterVersion({ 2 onVersion(version: string){` 

- `promptAction.showToast({ message: "version:"+version, duration: 200 0 })` 

- `}, 5 onFail(message: string){ 6 promptAction.showToast({ message: message, duration: 2000 }) 7 } 8 })` 

### 4.1.1编码表 

|名称|打印机编码代号|SDK编码|
|---|---|---|
|Default|0|gb2312|
|Chinese Simplified|0|gb2312|
|Chinese Traditional|0|big5|
|PC437(USA)|0|iso8859-1|
|KataKana|1|Shift_JIS|
|PC850(Multilingual)|2|iso8859-3|
|PC860(Portuguese)|3|34 iso8859-6|

|PC863(Canadian-|||
|---|---|---|
|French)|4|iso8859-1|
|PC865(Nordic)|5|iso8859-1|
|PC857(Turkish)|13|IBM857|
|PC737(Greek)|14|iso8859-7|
|ISO8859-7(Greek)|15|iso8859-7|
|WCP1252|16|iso8859-1|
|PC866(Cyrillic #2)|17|iso8859-5|
|PC852(Latin 2)|18|iso8859-2|
|PC858(Euro)|19|iso8859-15|
|KU42|20|ISO8859-11|
|TIS11(Thai)|21|ISO8859-11|
|TIS18(Thai)|26|ISO8859-11|
|PC720|32|iso8859-6|
|WPC775|33|iso8859-1|
|PC855(Cyrillic)|34|iso8859-5|
|PC862(Hebrew)|36|iso8859-8|
|PC864(Arabic)|37|iso8859-6|
|ISO8859-2(Latin2)|39|iso8859-2|
|ISO8859-15(Latin9)|40|iso8859-15|
|WPC1250|45|iso8859-2|
|WPC1251(Cyrillic)|46|35 iso8859-5|

|WPC1253|47|iso8859-7|
|---|---|---|
|WPC1254|48|iso8859-3|
|WPC1255|49|iso8859-8|
|WPC1256|50|Windows-1256|
|WPC1257|51|iso8859-1|
|WPC1258|52|bg2312|
|MIK(Cyrillic/Bulgarian)|54|iso8859-15|
|CP755|55|iso8859-5|
|Iran|56|iso8859-6|
|Iran II|57|iso8859-6|
|Latvian|58|iso8859-4|
|ISO-8859-1(West|59|iso8859-1|
|Europe)|||
|ISO-8859-3(Latin 3)|60|iso8859-3|
|ISO-8859-4(Baltic)|61|iso8859-4|
|ISO-8859-5(Cyrillic)|62|iso8859-5|
|ISO-8859-6(Arabic)|63|iso8859-6|
|ISO-8859-8(Hebrew)|64|iso8859-8|
|ISO-8859-9(Turkish)|65|iso8859-9|
|PC856|66|iso8859-8|
|ABICOIM|67|iso8859-15|

36 

### 4.1.2条码类型 

|bcType|名称|长度|数据范围|
|---|---|---|---|
|ESCBarcodeEnum.BC_UPCA|UPC-A|11-12|数字|
|ESCBarcodeEnum.BC_UPCE|UPC-E|11-12|数字(第一个数字必须是0)|
|ESCBarcodeEnum.BC_EAN13|JAN13/EAN13|12-13|数字|
|ESCBarcodeEnum.BC_EAN8|JAN8/EAN8|7-8|数字|
|ESCBarcodeEnum.BC_CODE39|CODE39|1-255|数字,字母,部分符号|
|ESCBarcodeEnum.BC_ITF|ITF|2-254|数字|
|ESCBarcodeEnum.BC_CODEB AR|CODABAR(NW- 7)|2-255|数字,部分字母,部分符号(起始 和结束必须是A,B,C,D)|
|ESCBarcodeEnum.BC_CODE93|CODE93|1-255|数字,字母,符号|
||||数字,字母,符号(先选择字符|
|ESCBarcodeEnum.BC_CODE12 8|CODE128|2-255|集,{A:ASCII字符00H到5FH {B:ASCII字符20H到7FH {C: 00-99的100个数字)|

37
