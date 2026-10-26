# **娜迦科技鸿蒙清场SDK HarmonyOS 使用** 

**文档** 

#### 目录 

|1 SDK简介......................................................................................................................2|
|---|
|2 SDK内容......................................................................................................................2|
|3 使用指南......................................................................................................................2|
|3.1 导入SDK...........................................................................................................2|
|3.2获取检测数据......................................................................................................2|
|(1) :获取设备信息......................................................................................................2|
|(2) wifi代理检测........................................................................................................3|
|(3) 模拟器检测......................................................................................................... 4|
|(4) 截屏、录屏、投屏检测........................................................................................4|
|(5) 签名校验.............................................................................................................4|
|(6) 模拟点击检测......................................................................................................5|
|1. 使用自定义回调函数..................................................................................... 5|
|2.不使用自定义回调函数(检测到模拟点击自动退出)........................................... 5|
|(7) 系统完整性检测.................................................................................................. 5|

## **1 SDK** 简介 

娜迦科技鸿蒙清场 SDK 是一款专注于风险采集与识别的 SDK,具备信息搜集、wifi 代 理检测、模拟器检测、截屏、录屏检测、签名校验。 

## **2 SDK** 内容 

娜迦科技鸿蒙清场 SDK 包含如下内容:Har 文件:SecureSDK.har 

## **3** 使用指南 

### **3.1** 导入 **SDK** 

安装SDK: ohpm install SecureSDK.har 

引入SDK:import { SecureSdk } from 'securesdk'; 

### **3.2** 获取检测数据 

### **(1):** 获取设备信息 

public static getDeviceData(): DeviceInfoData 

#### 导入设备信息模块: 

import { DeviceInfoData } from 'ngsecuresdk' DeviceInfoData 数据结构 

model: 设备型号 manufacturer:制造商 memory:内存大小 osVersion:系统版本 apiLevel:API 等级 securityPatch:安全补丁版本 cpuAbi:CPU 架构 bootloader:引导程序 使用: let deviceData: DeviceInfoData = SecureSdk.getDeviceData(); api 版本:12 

### **(2)wifi** 代理检测 

public static wifiProxyDetect(callback?: Function) 说明:callback: 自定义回调函数(可选参数)。 result:true 检测到 wifi 代理、 false 未检测到 wifi 代理 api 版本:12 使用: 1.使用自定义回调函数 SecureSdk.wifiProxyDetect((result: boolean) => { if (result) { 检测到 wifi 代理逻辑 }else { 未检测到 wifi 代理逻辑 } }) 

- 2.不使用自定义回调函数(检测到 wifi 代理自动退出) SecureSdk.wifiProxyDetect() 

(3) 模拟器检测 

public static isEmulator(): boolean api 版本:12 

#### 使用: 

let isInEmulator:boolean = SecureSdk.isEmulator() 

说明:true 检测到模拟器、false 未检测到模拟器 

#### (4) 截屏、录屏、投屏检测 

public static screenCapturedDetect(callback: Function) api 版本:12 

#### 使用: 

SecureSdk.screenCapturedDetect(() => { 

检测到截屏、录屏、投屏逻辑 

}) 

说明:callback: 自定义回调函数 

#### (5) 签名校验 

public static signatureDetector(fingerPrint: string, callback?: Function) 

说明: fingerPrint:签名指纹 

callback:回调函数(可选参数) 

api 版本:12 

fingerPrint 签名指纹获取方式: 

#### 1. 已安装应用: 

bm dump -n <bundlename> | grep fingerprint 

#### 2. 未安装应用: 

步骤 1:打开该签名文件(后缀为.p7b),打开后在文件内搜索“development-certificate”, 将“-----BEGIN CERTIFICATE-----”和“-----END CERTIFICATE-----”以及中间的信 息拷贝到新的文本中,注意换行并去掉换行符,保存为一个新的.cer 文件,如命名为 xxx.cer。 

步骤 2、使用 keytool 工具(在 jdk 目录 bin 文件夹内),执行如下命令通过.cer 文 件获取证书指纹的 SHA256 值。 keytool -printcert -file xxx.cer 

步骤 3、将证书指纹中 SHA256 的内容去掉冒号,即为最终要获得的签名指纹 

使用: 

#### 1.使用自定义回调函数 

SecureSdk.signatureDetector('B1C2C85ACFDB0E3C9CA7F34A4A8DB212C710017A07 89D9D1AF7597EAF23EE323', (result:boolean) => { 

if (result) { 

hilog.info(DOMAIN, 'testTag', '检测到签名不一致'); 

}else{ 

hilog.info(DOMAIN, 'testTag', '检测到签名一致'); 

} 

}) 

#### 2.不使用自定义回调函数(签名不一致退出) 

SecureSdk.signatureDetector('B1C2C85ACFDB0E3C9CA7F34A4A8DB212C710017A07 89D9D1AF7597EAF23EE323') 

#### (6) 模拟点击检测 

public static simulatedClickDetect(callback?: Function) 说明: callback:回调函数(可选参数) api 版本:20 

#### 1. 使用自定义回调函数 

SecureSdk.simulatedClickDetect(() => { 检测到模拟点击逻辑 

}) 

#### 2.不使用自定义回调函数(检测到模拟点击自动退出) 

SecureSdk.simulatedClickDetect() 

#### (7) 系统完整性检测 

public static checkSysIntegrity(callback: Function) api 版本:18 

使用: 

SecureSdk.checkSysIntegrity((result: string) => { 根据 result 值进行业务处理 

}) 

说明: callback:回调函数 

使用前请确保已打开安全检测服务开关并申请 Profile 

本地系统完整性检测结果 result 是一个格式为JSON 格式的字符串,当本地系统完整性检测结 果为false 时,您可以根据自身功能对安全的要求决定是否提醒用户,内容示例如下: { "basicIntegrity": false, "detail": [ "attack", "jailbreak", "emulator" ] 

} 

#### 字段说明: 

basicIntegrity:系统完整性检测的结果,true 表示检测结果完整,false 表示存在风险。 detail:可选字段,当basicIntegrity 结果为false 时,该字段将提供存在风险的原因,App 开发者可以根据不同风险做出不同的决策,详情如下: jailbreak:设备被越狱。 emulator:非真实设备。 attack:设备被攻击。 unlock:设备被解锁。
