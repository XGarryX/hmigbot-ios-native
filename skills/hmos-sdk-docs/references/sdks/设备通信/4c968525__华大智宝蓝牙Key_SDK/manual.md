鸿蒙 Next 接口文档 

# 华大智宝鸿蒙SDK 接口说明 

本文档主要介绍华大智宝鸿蒙Next 移动端SDK 的功能及相应的 API 接口。SDK 主要包含了读取证书、签名等功能。 

## 第一章 **SDK** 说明 

## **1.1** 文件说明 

SDK 共包含一个静态 har 包:HdzbUkeyDrive.har 

## **1.2 SDK** 使用配置 

(1)将 har 包(HdzbUkeyDrive.har)放在您的工程下具体 module 目录的 libs 文件夹下; 

(2)在引入 har 包的 module 下的 oh_package.json5 文件中加入 har 包依赖,示例如下: 

"dependencies": { "@hdzb/ukeydrive": "file:libs/HdzbUkeyDrive.har" } 

### (3)在代码中引用 har 包及相关类,示例如下: 

import { CertInfo, CertType, Hash, HdzbApi, HDZBError, OnSafeCallback, UICallbackType } from '@hdzb/ukeydrive'; 

1 

鸿蒙 Next 接口文档 

## **1.3** 接口使用注意事项 

(1)在使用 SDK 的接口前,需要对 SDK 进行初始化(只需要调用 

一次) 

### 调用示例如下: 

HdzbApi.getInstance().initialize(getContext()); 

(2)接口相关的文件均在 har 中,参考 1.2 章节导入相关文件即可。 

2 

鸿蒙 Next 接口文档 

## 第二章接口相关文件说明 

## **2.1** 回调函数 

export interface OnSafeCallback<T> { /** 

* 执行结果回调函数 * * @param errorCode * 错误码参见 HDZBError 类中错误码定义 * @param result * 函数执行结果返回值 */ onResult(errorCode: number, result: T): void; 

/** 

   - onShowUI 执行 UI 回调函数 

   - @param uicallbackType 返回回调类型,根据此参数判断显示或者关闭 UI 

- @param promptMsg 返回需要显示的信息,用户可忽略此消息,根据 

- uicallbackType 类型,弹出自定义消息提示框 

   - 说明:具体返回信息请看第三章接口说明中的详细解释 

*/ onShowUI(uicallbackType: UICallbackType, promptMsg: string): void; 

} 

## **2.2 UICallbackType** 说明 

export enum UICallbackType { 

HD_CHECK_VERIFY_PIN = 1, //验证PIN确认按键时返回,当PIN剩余尝试次数 小于等于3次时会返回该消息,提醒用户进行确认 

HD_CHECK_CHANGE_PIN = 2, //修改PIN确认按键时返回 

HD_CHECK_SIGN = 3, //签名确认按键时返回 

HD_CHECK_PIN = 4, //PIN确认按键时返回 

HD_CLOSE_UI = 100, //关闭UI返回 

HD_GET_SN = 101, //开始获取序列号时返回 

HD_ENUM_CERT = 102, //开始枚举证书时返回 

3 

鸿蒙 Next 接口文档 

HD_READ_CERT = 103, //开始读取证书时返回 HD_SIGNNING = 104, //开始签名时返回 HD_VERIFY_PIN = 105, //开始验证密码时返回 HD_CHANGE_PIN = 106, //开始修改密码时返回 

HD_CONNECTING_BYKEY = 107, //开始连接蓝牙key时返回 HD_GET_PIN_REMAIN_TIMES = 108, //开始获取pin剩余次数时返回 HD_IS_DEFAULT_PIN = 109 //开始判断是否是默认PIN时返回 

} 

## **2.3 CertType** 说明 

export enum CertType { 

RSA = 1, // RSA证书 

SM2_SHOW = 2, // 交易签名国密证书 

SM2 = 3, // 普通签名国密证书 RSA_SHOW = 4, // RSA签名证书 

} 

## **2.4 Hash** 说明 

export enum Hash { ALG_MD5 = 0x80000001, ALG_SHA1 = 0x80000002, ALG_SHA256 = 0x80000003, ALG_SHA384 = 0x80000004, ALG_SHA512 = 0x80000005, ALG_SM3 = 0x80000006 } 

## **2.4 CertInfo** 说明 

export class CertInfo { 

4 

鸿蒙 Next 接口文档 

private subject: string; private issuer: string; private notBefore: string; private notAfter: string; private certType: number; constructor() { = this.subject ''; this.issuer = ''; this.notBefore = ''; this.notAfter = ''; this.certType = -1; } 

get getSubject(): string { return this.subject } set setSubject(data: string) {this.subject = data} 

get getIssuer(): string { return this.issuer } set setIssuer(data: string) {this.issuer = data} 

get getNotBefore(): string { return this.notBefore } set setNotBefore(data: string) {this.notBefore = data} 

get getNotAfter(): string { return this.notAfter } set setNotAfter(data: string) {this.notAfter = data} 

get getCertType(): number { return this.certType } set setCertType(data: number) {this.certType = data} } 

5 

鸿蒙 Next 接口文档 

## 第三章 接口功能介绍 

SDK 的所提供的功能接口,每一个功能接口基本都包含同步接口 和异步接口两种实现,请根据需要合理选择使用。 

## **3.1** 接口列表 

|序号|接口名|接口功能概述|
|---|---|---|
|1|initialize|SDK 初始化|
|2|getVersion|获取SDK 版本号|
|3|getSn|获取序列号|
|4|enumCerts|枚举所有证书|
|5|readCert|读取证书内容|
|6|readCertificate|读取证书内容,返回|
|||certFramework.X509Cert 对象|
|7|changePin|修改密码|
|8|getPinRetry|获取pin 的剩余次数|
|9|tradeSign|交易签名|
|10|normalSign|普通签名|
|11|getLastErr|获取最后一次操作的错误码|
|12|isConnected|设备是否连接|
|13|connectKey|连接蓝牙Key|
|14|disConnectKey|断开蓝牙连接|

6 

鸿蒙 Next 接口文档 

|15|checkDefaultPin|判断是否为初始密码|
|---|---|---|
|16|getCertSn|获取证书编号|

7 

鸿蒙 Next 接口文档 

## **3.2** 接口说明 

/** 

* SDK 初始化 * @param context 应用上下文 */ initialize(context: Context): void; 

/** 

* 获取版本号 * @returns */ getVersion(): string; 

/** * 获取序列号- 异步 * @param callback 回调函数 */ getSn(callback: OnSafeCallback<String>): void; 

|OnShowUI 方法返回值参见|下表:|
|---|---|
|参数 参数值||
|uiCallbackType HD_GET|_SN(调用方法时返回)|

8 

||鸿蒙Next 接口文档|
|---|---|
||HD_CLOSE_UI(调用结束时返回)|
|promptMsg|返回对应等待信息|

/** 

- 枚举所有证书- 异步 

* @param callback 回调函数 

- @return 

- */ 

enumCerts(callback: OnSafeCallback<List<CertInfo>>): void; 

OnShowUI 方法返回值参见下表: 

|参数|参数值|
|---|---|
|uiCallbackType|HD_ENUM_CERT(调用方法时返回)|
||HD_CLOSE_UI(调用结束时返回)|
|promptMsg|返回对应等待信息|

/** 

- 读取证书内容- 异步 

- @param certType 证书类型,取值参见CertType 

- @param callback 回调函数 

- @return 

9 

鸿蒙 Next 接口文档 

*/ 

readCert(certType: number, callback: 

OnSafeCallback<string>): void; 

OnShowUI 方法返回值参见下表: 

|参数|参数值|
|---|---|
|uiCallbackType|HD_READ_CERT(调用方法时返回)|
||HD_CLOSE_UI(调用结束时返回)|
|promptMsg|返回对应等待信息|

/** 

- 读取证书内容,返回Certificate 对象- 异步 

- @param certType 证书类型,取值参见CertType 

- * @param callback 回调函数 

- @return 

*/ 

readCertificate(certType: number, callback: 

OnSafeCallback<certFramework.X509Cert>): void; 

OnShowUI 方法返回值参见下表: 

|参数|参数值|
|---|---|
|uiCallbackType|HD_READ_CERT(调用方法时返回)|
||HD_CLOSE_UI(调用结束时返回)|

10 

鸿蒙 Next 接口文档 

返回对应等待信息 

promptMsg 

/** 

* 修改密码- 异步 

* @param oldPin 原密码 * @param newPin 新密码 

- @param callback 回调函数 

* @return 

*/ 

changePin(oldPin: string, newPin: string, callback: 

OnSafeCallback<Boolean>): void; 

OnShowUI 方法返回值参见下表: 

|参数|参数值|
|---|---|
|uiCallbackType|HD_CHANGE_PIN(调用方法时返回)|
||HD_CHECK_CHANGE_PIN(等待按键时返回)|
||HD_CLOSE_UI(调用结束时返回)|
|promptMsg|返回对应等待信息|

/** 

11 

鸿蒙 Next 接口文档 

   - 获取pin 的剩余次数- 异步 

   - @param callback 回调函数 

- @return 成功返回长度为2 的数组{剩余重试次数,最大重试次 

- 数},失败返回null 

*/ 

getPinRetry(callback: OnSafeCallback<number[]>): void; 

OnShowUI 方法返回值参见下表: 

|参数|参数值|
|---|---|
|uiCallbackType|HD_GET_PIN_REMAIN_TIMES(调用方法时返回)|
||HD_CLOSE_UI(调用结束时返回)|
|promptMsg|返回对应等待信息|

/** 

* 交易签名- 异步 

* @param certType 证书类型,取值参见 HdzbUKeyInterface.CertType * @param hashAlgId hash 算法,取值HdzbUKeyInterface.Hash * @param msg 签名报文 * @param charseName 编码类型 * @param userPin ukey 密码 * @param bSensitive pin 是否大小写敏感 

12 

鸿蒙 Next 接口文档 

- @param bIsNeedPackPkcs7 

是否需要组装P7 

- @param callback 回调函数 

- @return 

*/ 

tradeSign(certType: number, hashAlgId: number, msg: string, charseName: string, userPin:string, bSensitive:boolean, bIsNeedPackPkcs7: boolean, 

callback: OnSafeCallback<string>): void; 

### OnShowUI 方法返回值参见下表: 

|参数|参数值|
|---|---|
|uiCallbackType|HD_SIGNNING(调用方法时返回)|
||HD_CHECK_VERIFY_PIN(当PIN 剩余尝试次数小|
||于等于2 次时返回,提醒用户按键确认ukey 密|
||码)|
||HD_CHECK_SIGN(等待按键确认时返回)|
||HD_CLOSE_UI(调用结束时返回)|
|promptMsg|返回对应等待信息|

/** 

- 普通签名- 异步 

- @param certType 证书类型,取值参见 

13 

鸿蒙 Next 接口文档 

HdzbUKeyInterface.CertType 

* @param hashAlgId hash 算法,取值HdzbUKeyInterface.Hash 

- @param hashValue hash 值 

- * @param userPin ukey 密码 

- @param bSensitive pin 是否大小写敏感 

- @param bIsNeedPackPkcs7 是否需要组装P7 

- * @param callback 回调函数 

- @return 

*/ 

normalSign(certType: number, hashAlgId: number, hashValue: Uint8Array, userPin:string, bSensitive:boolean, bIsNeedPackPkcs7: boolean, 

callback: OnSafeCallback<string>): void; 

### OnShowUI 方法返回值参见下表: 

|参数|参数值|
|---|---|
|uiCallbackType|HD_SIGNNING(调用方法时返回)|
||HD_CHECK_VERIFY_PIN(当PIN 剩余尝试次数小|
||于等于2 次时返回,提醒用户按键确认ukey 密|
||码)|
||HD_CLOSE_UI(调用结束时返回)|

14 

鸿蒙 Next 接口文档 

/** 

* 获取最后一次操作的错误码 

* @return */ getLastErr(): number; 

/** 

* 设备是否连接 * @return */ 

isConnected(): boolean; 

/** 

* 连接蓝牙Key 

* @param strDeviceSN 蓝牙key 序列号 * @param iSecConnectTimeOut 蓝牙扫描超时时间 * @param callback 回调函数 

*/ 

connectKey(strDeviceSN: string, iSecConnectTimeOut: number, 

callback: OnSafeCallback<String>): void; 

OnShowUI 方法返回值参见下表: 

参数 参数值 

15 

鸿蒙 Next 接口文档 

uiCallbackType HD_CONNECTING_BYKEY(调用方法时返回) HD_CLOSE_UI(调用结束时返回) 

/** 

- 断开蓝牙连接 

- */ 

- disConnectKey(); 

/** 

- 判断是否为初始密码- 异步 

- @param callback 回调函数 

- @return 

- */ 

checkDefaultPin(callback: OnSafeCallback<Boolean>): void; 

OnShowUI 方法返回值参见下表: 

|参数|参数值|
|---|---|
|uiCallbackType|HD_IS_DEFAULT_PIN(调用方法时返回)|
||HD_CLOSE_UI(调用结束时返回)|

/** 

16 

鸿蒙 Next 接口文档 

* 获取证书序列号- 异步 

* @param certType 证 书 类 型 , 取 值 参 见 HdzbUKeyInterface.CertType 

* @param callback 回调函数 

*/ 

getCertSn(certType: number,callback: OnSafeCallback<String>): void; 

OnShowUI 方法返回值参见下表: 

|参数|参数值|
|---|---|
|uiCallbackType|HD_GET_CERT_SN(调用方法时返回)|
||HD_CLOSE_UI(调用结束时返回)|
|promptMsg|返回对应等待信息|

17 

鸿蒙 Next 接口文档 

## 第四章错误码 

export class HDZBError { 

= static readonly ERROR_SUCCESS 0; // 操作成功 = static readonly ERROR_OPERATION_FAILED 1; // 操作失败 = static readonly ERROR_NO_DEVICE 2; // 设备未连接 = static readonly ERROR_DEVICE_BUSY 3; // 设备忙 = static readonly ERROR_INVALID_PARAMETER 4; // 参数错误 = static readonly ERROR_PASSWORD_INVALID 5; // 密码错误 = static readonly ERROR_USER_CANCEL 6; // 用户取消操作 = static readonly ERROR_OPERATION_TIMEOUT 7; // 操作超时 = static readonly ERROR_NO_CERT 8; // 没有证书 = static readonly ERROR_CERT_INVALID 9; // 证书格式不正确 = static readonly ERROR_UNKNOW_ERROR 10; // 未知错误 = static readonly ERROR_PIN_LOCK 11; // 码锁定 

= static readonly ERROR_OPERATION_INTERRUPT 12; // 操作被 打断(如来电等) 

= static readonly ERROR_COMM_FAILED 13; // 通讯错误 = static readonly ERROR_ENERGY_LOW 14; // 设备电量不足, 不能进行通讯 

= static readonly ERROR_CERT_EXPIRED 15; // 证书过期 

18 

鸿蒙 Next 接口文档 = static readonly ERROR_CERT_NOEFFECT 16; // 证书未生效 = static readonly ERROR_COMM_TIMEOUT 17; // 通讯超时 = static readonly ERROR_SN_NOTMATCH 18; // 序列号不匹配 = static readonly ERROR_SAME_PASSWORD 19; // 新旧密码相同 = static readonly ERROR_PASSWORD_INVALID_LENGTH 20; // 新 密码长度错误 

= static readonly ERROR_PASSWORD_DIFFERENT 21; // 新密码 与确认密码不一致 

= static readonly ERROR_PASSWORD_EMPTY 22; // 密码为空 = static readonly ERROR_PASSWORD_TOO_SIMPLE 23; // 密码过 于简单 

= static readonly ERROR_CERT_DN_NOTMATCH 24; // 证书dn 值 不匹配 

= static readonly ERROR_PASSWORD_ERROR_TIMES 25; // 密码 剩余次数 

= static readonly ERROR_PHONE_NO__RECORD_PERMISSION 26; // 提示手机没有录音权限/录音资源被占用,提示进入手机权限管理软 件中进行设置或者关闭相关应用释放录音资源 

= static readonly PROMPT_SIGN_PRESS_KEY 27; // 签名时提示 需要按键 

= static readonly BT_KEY_CONNCT_SUCCESS 28; // 蓝牙Key 连 接成功 

19 

鸿蒙 Next 接口文档 

= static readonly BT_KEY_DISCONNECT 29; // 蓝牙Key 断开 

连接 

= static readonly PHONE_BLE_IS_CLOSED 30; // 手机蓝牙没开 = static readonly ERROR_SIGN_DATA_VALID 31; // 待签名报文 

无效 

} 

20
