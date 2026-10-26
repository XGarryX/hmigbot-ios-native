# TTLock HarmonyOS SDK **使用指南** 

#### 最近更新:2026-06-30 

本文档面向首次接入 TTLock HarmonyOS SDK 的开发者,说明环境准备、工程集成与常见业务场景的完整调用流程。 各接口的参数与返回值详见 HMOS_API.md。 

## **本页目录** 

概述 

- 环境要求 

- 快速集成 

- 架构说明 

- 通用准备 

- 场景一:蓝牙智能锁 

- 场景二:智能电表 / 水表 

- 场景三:WiFi 门磁 

- 场景四:NFC 无源锁 

- 特征值与能力判断 

- 常见问题 

- Demo 工程说明 

## **概述** 

TTLock HarmonyOS SDK(ohpm 包名 **`@sciener/ttlock`** )用于在鸿蒙应用内通过 **蓝牙** 或 NFC 与通通锁生态设备通信,主要 能力包括: 

|**模块**|**类名**|**通信方式**|
|---|---|---|
|智能锁/网关/配件|`TTLock`|蓝牙|
|智能电表|`TTElectricMeter`|蓝牙+ HTTP|
|智能水表|`TTWaterMeter`|蓝牙+ HTTP|
|WiFi门磁|`TTWiFiDoorMagnetic`|蓝牙|
|NFC无源锁|`TTNfcPassiveLock`|NFC|

## **环境要求** 

|**项目**|**要求**|
|---|---|
|SDK版本|`@sciener/ttlock` 1.0.5 及以上|
|最低系统API|HarmonyOS API 14(5.0.2 Release)及以上|
|开发工具|DevEco Studio(建议配套安装对应HarmonyOS SDK)|
|开放平台|使用电表/水表绑定、OTA等能力时需注册 通通锁开放平台 并获取 `clientId` 、 `accessToken`|

工程级需开启(HAR 字节码依赖): 

// 工程级 build-profile.json5 ! products ! buildOption ! strictMode "useNormalizedOHMUrl": true 

## **快速集成** 

### 1. **安装** SDK 

在 entry **模块** 的 `oh-package.json5` 中添加依赖: 

{ "dependencies": { "@sciener/ttlock": "1.0.5" } } 

本地联调时可指向源码 HAR: 

"@sciener/ttlock": "../TTLockSDK" 

#### 执行安装: 

ohpm install 

### 2. **声明权限** 

在 entry 模块 `module.json5` 中按需声明: 

"requestPermissions": [ 

{ "name": "ohos.permission.INTERNET" }, 

{ "name": "ohos.permission.ACCESS_BLUETOOTH", "reason": "$string:bluetooth_permission", "usedScene": {} } ] 

使用 NFC 无源锁时额外声明 `ohos.permission.NFC_TAG` ,并在 Ability `skills.actions` 中加入 `ohos.nfc.tag.action.TAG_FOUND` (详见 场景四)。 

### 3. **导入与初始化** 

import { TTLock, TTLog } from '@sciener/ttlock'; // 建议在 UIAbility.onCreate 中开启日志,便于排查 TTLock.printLog(true); 

### 4. **验证集成** 

编译运行 Demo 或最小示例:申请蓝牙权限 → 扫描锁 → 控制台输出 `TTLog` 日志即表示 SDK 加载正常。 

**架构说明** 

典型业务分为两层: 

"#################$         "##################$ %   您的鸿蒙 App   %  SDK    %   智能设备(锁/表)  % %  @sciener/ttlock % `◄` #BLE## `►` %   蓝牙 / NFC      % &########'########(         &##################( % HTTP(可选) `▼` "#################$ % 通通锁 Open API  % `←` 账号、钥匙、设备绑定、远程管理 %  (您的服务端)   % &#################( 

#### **建议做法:** 

- App 通过 SDK 完成 **近场操作** (扫描、初始化、开锁、配网等)。 

- 账号体系、电子钥匙下发、设备列表等业务由 **您的服务端** 调用 Open API,App 只与服务端交互。 

- `lockData` 初始化成功后需上传服务端保存,后续开锁/管理均依赖此字符串。 

## **通用准备** 

### **申请蓝牙权限** 

所有蓝牙类业务( `TTLock` 、电表、水表、WiFi 门磁)在扫描前执行: 

```arkts
import { abilityAccessCtrl } from '@kit.AbilityKit'; let status = await TTLock.verifyBluetoothPermission(); if (status !== abilityAccessCtrl.GrantStatus.PERMISSION_GRANTED) { // 用户拒绝时可引导至设置页 status = await TTLock.verifyBluetoothPermissionOnSetting(); } 
```

### **确认蓝牙已开启** 

import { BLEState } from '@sciener/ttlock'; if (TTLock.getState() !== BLEState.turnOn) { // 提示用户打开系统蓝牙 } 

### **停止扫描** 

SDK 内部共用扫描器, **离开页面或切换业务前务必调用** 对应 `stopScan()` ,避免扫描冲突与耗电: 

TTLock.stopScan(); // 锁 / 键盘 / 电表 / 水表 / WiFi 门磁 TTLock.stopScanGateway(); // 网关 

### **回调与错误** 

#### 蓝牙类 API 使用 `ITTLockResult<T>` : 

{ success: (data) => { /* 成功 */ }, failure: (error: SNError) => { /* 失败,可打印 error 定位 */ }, } 

NFC 类 API 返回 `Promise<TTLockResult<T>>` ,请检查 `isSuccess` 与 `error` 。 

## **场景一:蓝牙智能锁** 

### **流程概览** 

申请权限 ! 扫描锁 ! 初始化(initLock) ! 上传 lockData 至服务端 ! 后续用 lockData 开锁/管理 

### **步骤** 1 **:扫描** 

import { TTLock, TTLog } from '@sciener/ttlock'; TTLock.startScanLock((scanModel) => { TTLog.info(`发现锁:${scanModel.name} mac=${scanModel.mac}`); TTLog.info(`是否已初始化:${scanModel.isInited}`); // 选中目标锁后停止扫描 TTLock.stopScan(); }); 

### **步骤** 2 **:初始化(未添加过的锁)** 

锁需处于 **可添加状态** (通常长按锁上设置键进入添加模式,具体以设备说明书为准)。 

TTLock.initLock( { mac: scanModel.mac, lockVersion: scanModel.lockVersion, clientPara: null, }, { success: (lockData: string) => { // 1. 本地安全保存 lockData // 2. 上传至您的服务端,由服务端调用 Open API 完成绑定 TTLog.info('初始化成功'); }, failure: (error) => { TTLog.error(`初始化失败:${error}`); }, }, ); 

### **步骤** 3 **:开锁** 

使用服务端下发的 `lockData` (或本地已保存的管理员 lockData): 

import { TTControlAction } from '@sciener/ttlock'; TTLock.controlLockWithControlAction(lockData, TTControlAction.unlock, { success: (info) => { TTLog.info(`开锁成功,电量:${info.electricQuantity}`); }, failure: (error) => { TTLog.error(`开锁失败:${error}`); }, }); 

### **步骤** 4 **:电子钥匙开锁(典型** B **端流程)** 

1. 用户在 App 登录您的账号。 

2. App 向您的服务端请求该锁的电子钥匙数据。 

3. 服务端从通通锁 Open API 获取钥匙并返回 `lockData` 。 

4. App 用上述 `lockData` 调用 `controlLockWithControlAction` 开锁。 

SDK **不负责** 账号登录与钥匙云端同步,这部分由 Open API + 您的后端完成。 

## **场景二:智能电表** / **水表** 

### **流程概览** 

setClientParam ! 扫描 ! connect ! add* ! 业务读写(合闸/读数/充值等) 

### **电表示例** 

import { TTElectricMeter, TTLog } from '@sciener/ttlock'; // 1. 配置开放平台鉴权(添加前调用一次) TTElectricMeter.setClientParam( 'https://your-open-api-host', 'your_client_id', 'your_access_token', ); // 2. 扫描 TTElectricMeter.startScanElectricMeter((model) => { TTLog.info(`电表 MAC:${model.mac}`); }); // 3. 连接 TTElectricMeter.connect(mac, { success: () => { // 4. 添加绑定 TTElectricMeter.addElectricMeter( { number: '101', mac: mac, payMode: 1, price: '1.0' }, { success: (result) => { TTLog.info(`添加成功 id=${result.electricMeterId}`); }, failure: (e) => TTLog.error(`${e}`), }, ); }, failure: (e) => TTLog.error(`${e}`), }); // 5. 读数示例 TTElectricMeter.readData(mac, { success: (status) => { TTLog.info(`剩余电量:${status.remainderKwh} kWh`); }, failure: (e) => TTLog.error(`${e}`), }); 

### **水表** 

- 将 `TTElectricMeter` 替换为 `TTWaterMeter` ,扫描接口为 `startScanWaterMeter` ,添加为 `addWaterMeter` ,读数为 `readWaterData` ,其余流程一致。 

**场景三:** WiFi **门磁** 

### **流程概览** 

扫描 ! 初始化(配网 + 绑定)! 查询信息 / 设置报警 

import { TTWiFiDoorMagnetic, TTLog } from '@sciener/ttlock'; TTWiFiDoorMagnetic.startScanWiFiDoorMagnetic((model) => { TTLog.info(`发现门磁:${model.mac}`); TTWiFiDoorMagnetic.stopScan(); TTWiFiDoorMagnetic.initializeDoorMagnetic( model.mac, { SSID: 'YourWiFi', wifiPwd: 'password', serverAddress: 'your.server.com', portNumber: '4999', }, { success: (info) => { TTLog.info(`初始化成功,电量:${info.electricQuantity}`); }, failure: (e) => TTLog.error(`${e}`), }, ); }); 

## **场景四:** NFC **无源锁** 

NFC 能力与其他模块独立,需额外配置 Ability **生命周期** 。 

### 1. module.json5 

"requestPermissions": [ { "name": "ohos.permission.NFC_TAG", "reason": "$string:nfc_permission", "usedScene": {} } ], "abilities": [{ "skills": [{ "actions": [ "action.system.home", "ohos.nfc.tag.action.TAG_FOUND" ] }] }] 

### 2. EntryAbility **生命周期** 

import { TTNfcPassiveLock, TTLock } from '@sciener/ttlock'; 

```arkts
onCreate(want: Want): void { TTLock.printLog(true); TTNfcPassiveLock.configureReaderFromWant(want); } 
onForeground(): void { TTNfcPassiveLock.registerForegroundReader(); } 
onBackground(): void { TTNfcPassiveLock.unregisterForegroundReader(); } 
onDestroy(): void { TTNfcPassiveLock.unregisterForegroundReader(); } 
```

### 3. **初始化与开锁** 

操作前:App **在前台** + **手机贴近** NFC **标签** 。 

// 初始化(锁处于添加模式) let initRes = await TTNfcPassiveLock.initLock(); if (initRes.isSuccess) { let lockData = initRes.data!.lockData; // 上传服务端保存 } 

// 开锁(lockData 来自服务端或本地) let unlockRes = await TTNfcPassiveLock.unlock(lockData, (progress) => { TTLog.info(`充电进度 ${progress}%`); 

}); if (unlockRes.isSuccess) { // 务必用返回的新 lockData 覆盖旧值 lockData = unlockRes.data!; } 

## **特征值与能力判断** 

#### 不同硬件支持的功能不同,调用前应判断: 

import { TTLock, TTLockFeatureValue } from '@sciener/ttlock'; 

let supportCycle = await TTLock.supportFunction(lockData, TTLockFeatureValue.cyclePassword); if (!supportCycle) { 

// 该锁不支持周期密码,勿调用相关接口 } 

电表/水表/门磁使用各类 `supportFunction(func, featureValue)` ,需先通过 `getFeatureValue` 获取特征值字符串。 

## **常见问题** 

|**现象**|**可能原因**|**处理建议**|
|---|---|---|
|扫描不到设备|未授权蓝牙/蓝牙未开|调用 `verifyBluetoothPermission` ,检查 `getState()`|
|扫描不到设备|未停止上次扫描|先调用 `stopScan()` 再重新开始|
|初始化失败|锁未进入添加模式|按设备说明书进入设置/添加模式|
|NFC操作timeout|未贴近标签或App在后台|保持前台+贴近;确认已 `registerForegroundReader`|
||未调用||

|NFC操作timeout|`configureReaderFromWant`|检查 `onCreate` 是否配置|
|---|---|---|
|开锁失败noPermission|lockData无效或钥匙过期|向服务端重新同步lockData|
|电表/水表添加失败|未 `setClientParam` 或token 过期|检查开放平台鉴权参数|
|编译报compatibleSdkVersion 过低|SDK要求API 14+|升级工程 `compatibleSdkVersion`|

开启 SDK 日志后,过滤 `TTLog` / 赛脑智能 标签可快速定位蓝牙与 NFC 交互细节: 

TTLock.printLog(true); 

## Demo **工程说明** 

本仓库 `ttlock_hm` 为 SDK 联调 Demo,结构如下: 

|**路径**|**说明**|
|---|---|
|`TTLockSDK/`|SDK源码(HAR模块)|
|`entry/`|Demo应用,集成 `@sciener/ttlock`|
|`entry/src/main/ets/pages/Index.ets`|各业务API按钮示例|
|`entry/src/main/ets/entryability/EntryAbility.ets`|NFC生命周期示例|
|`TTLockSDK/docs/HMOS_API.md`|完整API参考文档|

#### 本地运行: 

1. 用 DevEco Studio 打开工程根目录。 

2. 确认 `build-profile.json5` 中 `useNormalizedOHMUrl: true` 。 

3. 连接真机(蓝牙/NFC 需真机调试)。 

4. 运行 entry 模块,在 Index 页按业务场景测试。 

## **相关文档** 

HMOS_API.md — 完整 API 参考 

- 通通锁开放平台 — Open API 与开发者账号 

- OpenHarmony ohpm 安装说明
