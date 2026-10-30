# 文鼎创蓝牙 Key SDK 集成说明 

深圳市文鼎创数据科技有限公司 版权所有 侵权必究 

All rights reserved 

目录 

文鼎创蓝牙 Key SDK 集成说明 1 

1. 产品模块列表 1 

2. SDK 使用说明 1 

2.1. 集成说明 1 

3. 接口定义 2 

3.1. 接口概述 2 

3.1.1. 设备连接类接口 2 

3.1.2. PIN 码管理类接口 2 

3.1.3. 证书查询类接口 2 

3.1.4. 签名类接口 2 

3.2 接口工作流程 3 

3.2.1 基本签名流程 3 

3.2.2 证书查询流程 3 

3.3 接口定义代码 4 

3.3.1 证书与算法类型定义 4 

3.3.2 证书结构体定义 5 

3.3.3 接口定义 6 

3.3.4 错误码定义 9 

3.4 接口使用示例 12 

3.4.1 场景一:连接蓝牙 Key 和断开 12 

3.4.2 场景二: PIN 管理(检查 / 修改 PIN ) 13 

3.4.3 场景三:证书查询 14 

3.4.4 场景四:签名操作 16 

# 产品模块列表 

序号 

部件名称 

产品信息 

1 

ESBankSdk 库 

部署方式:编译集成 

厂商提交 har : ESBankSdk.har 

2 

文鼎创蓝牙 Key 

厂商单独提供:已配置好 RSA 和 SM2 证书的蓝牙 Key 

SDK 使用说明 

集成说明 

我司提供的 SDK 的使用方式是:静态集成 ESBankSdk.har ,以下是主 要步骤: 

"dependencies": { 

"es_banksdk": "file:./dependencies/ESBankSdk.har", 

} 

"dependencies": { 

"es_banksdk": "file:./dependencies/ESBankSdk.har", 

} 

将 ESBankSdk.har 放入工程对应目录下,并在对应 oh-package.json5 的 dependencies{} 中添加依赖。 

import { IUKeyInterface, ESBankBT_WD} from 'es_banksdk' 

let device: IUKeyInterface = 

ESBankBT_WD.getInstance(getContext(this)); 

import { IUKeyInterface, ESBankBT_WD} from 'es_banksdk' 

let device: IUKeyInterface = ESBankBT_WD.getInstance(getContext(this)); 

加载 SDK ,获取接口实例,示例代码如下: 

调用 device 接口实例的方法,使用相关功能。 

在 module.json5 中添加必要的权限 

{ 

"requestPermissions": [ 

{ 

"name": "ohos.permission.ACCESS_BLUETOOTH", 

"reason": " 用于蓝牙连接 Key" 

} 

] 

} 

接口定义 

# 3.1. 接口概述 

SDK 提供了完整的蓝牙 Key 操作接口,按功能可分为以下几类: 

# 3.1.1. 设备连接类接口 

connect: 连接蓝牙 Key 设备 

getSn: 获取已连接设备的序列号 

# isConnected: 检查设备连接状态 

disconnect: 断开设备连接 

3.1.2. PIN 码管理类接口 

modifyPIN: 修改设备 PIN 码 getPinRetryTimes: 获取 PIN 码剩余重试次数 isDefaultPIN: 检查密码是否为默认密码 

3.1.3. 证书查询类接口 

getCert: 获取设备中的证书 getCertCN: 获取证书 CN 信息 getCertTime: 获取证书有效期 

enumCert: 枚举设备中的证书以及其主要信息 

3.1.4. 签名类接口 

sign: 对字符串数据进行签名 

# 3.2 接口工作流程 

3.2.1 基本签名流程 

适用于已有证书的设备进行签名操作: connect(sn, timeout, callback) 

└─ > 连接蓝牙 Key 设备 

# modifyPIN() 

└─ > 修改密码,二代签名不可使用默认密码,需修改密码后方可签 名 

sign(sn, signData, pin, signAlg, hashId, callback) 

└─ > 对签名原文数据进行签名,签名原文数据可参考该格式: 

<?xml version="1.0" encoding="utf-8"?><T><D><M><k 〉 手机号: </k><v> 

15077260729</v></M><M><k 〉流水号 :</ k><v>046386c5694f4e10a3e972601bd 

12b4c</v></M></D></T> 

(签名原文开头去掉 xml 则为一代签名,保留 xml 则为二代签名) 

└─ > 返回 Base64 编码的签名结果 

disconnect() 

└─ > 断开设备连接 

3.2.2 证书查询流程 

适用于校验设备证书信息或展示证书给用户: 

connect(sn, timeout, callback) 

└─ > 连接蓝牙 Key 设备 

enumCert(sn, certType, callback) 

└─ > 枚举设备中的证书 

getCertCN(sn, certType, callback) 

└─ > 获取证书 CN 信息(颁发者 - 持有人),可用于展示 / 校验 

getCertTime(sn, certType, callback) 

# └─ > 获取证书有效期(起止日期),可用于过期检查 

getCert(sn, certType, callback) 

└─ > 获取证书内容( Base64 编码) 

disconnect() 

└─ > 断开设备连接 

3.3 接口定义代码 

# 3.3.1 证书与算法类型定义 

export namespace IUKeyInterface { 

/** 

# * RSA 类型证书 

*/ 

export const RSA: number = 0x00000001 

/** 

- SM2 类型证书(只可使用 SM3 类型算法签名) 

*/ 

export const SM2: number = 0x00000002 

/** 

* MD5 哈希算法 

*/ 

export const MD5: number = 0x00000001 

/** 

* SHA1 哈希算法 

*/ 

export const SHA1: number = 0x00000002 

/** 

# * SHA256 哈希算法 

*/ 

export const SHA256: number = 0x00000003 

/** 

* SHA384 哈希算法 

*/ 

export const SHA384: number = 0x00000004 

/** 

- SHA512 哈希算法 

*/ 

export const SHA512: number = 0x00000005 

/** 

- SM3 哈希算法(只可使用 SM2 类型证书签名) 

*/ 

export const SM3: number = 0x00000006 

/** 

- 回到接口时用于在接口的调用过程中 app 与接口之前的交互工作, 

- 比如在签名过程中需要用户进行按键确认,这时候就需要利用回调通 知 app 提示用户进行按键 

*/ 

export interface OnSafeCallback<T> { 

/** 

# * 执行结果回调函数 

- @param errorCode 状态码 / 错误码,见错误码定义 

- @param result 回调数据(比如 PIN 码的可重试次数等) 

*/ 

onResult: (errorCode: number, result: T) => void 

} 

# 3.3.2 证书结构体定义 

export interface CertInfo { /** * 证书类型( RSA 为 1 ; SM2 为 2 ) */ certType: number /** * 证书 CN ,格式为 " 证书颁发者 CN- 证书拥有者 CN" */ certCN: string /** * 证书主体完整 DN */ certSubjectDN: string /** * 证书颁发者完整 DN */ certIssureDN: string 

/** * 证书生效时间(原始字符串格式) */ certStartTime: string 

/** * 证书失效时间(原始字符串格式) */ certEndTime: string } 

# 3.3.3 接口定义 

export interface IUKeyInterface { 

/** 

# * 连接蓝牙 Key 

- @param sn 蓝牙 Key 的序列号 

- @param timeoutSeconds 连接超时时间 

- @param callback 回调函数,可通过回调提示设备断开 

*/ 

connect(sn: string, timeoutSeconds: number, callback: OnSafeCallback<number>): void 

/** 

- 连接状态下,获取蓝牙 Key 的 SN 

- @param callback 回调函数,可通过回调提示按键 

*/ 

getSn(callback: OnSafeCallback<string>): void 

/** * 判断设备是否已连接 * @param callback 回调函数,返回 true 表示设备已连接, false 表示未连接 */ isConnected(callback: OnSafeCallback<boolean>): void 

/** 

- 修改蓝牙 Key 的 PIN 码 

- @param sn 蓝牙 Key 的序列号 

- @param oldPin 蓝牙 Key 的旧 PIN 码 

- *@param newPin 蓝牙 Key 的新 PIN 码 

* @param callback 回调函数,可通过回调获取 PIN 的剩余次数,以 及是否 

# 需要按键 */ 

modifyPIN(sn:string, oldPin:string, newPin: string, callback: OnSafeCallback<string> 

): void 

/** 

# * 通过序列号获取密码剩余次数 

- @param sn 蓝牙 Key 的序列号 

- @param callback 回调函数,可通过回调提示按键 

*/ 

getPinRetryTimes(sn: string, callback: OnSafeCallback<number>): void 

/** 

- 通过序列号获取证书 CN 

- 格式为 " 证书颁发者 CN- 证书拥有者 CN" 

- @param sn 蓝牙 Key 的序列号 

- @param certType 查看的证书类型, 1 为 rsa 签名证书, 2 为 sm2 签名 

- 证书 

- @param callback 回调函数,可通过回调提示按键。 */ 

getCertCN(sn: string, certType: number, callback: OnSafeCallback<string>): void 

/** 

- 通过序列号获取证书起止时间 

- 格式为 "XXXX-XX-XX:XXXX-XX-XX" 

- @param sn 蓝牙 Key 的序列号 

- @param certType 查看的证书类型, 1 为 RSA 签名证书, 2 为 SM2 签 名 

证书 

- @param callback 回调函数,可通过回调提示按键 */ 

getCertTime(sn: string, certType: number, callback: OnSafeCallback<string>): void 

/** * 判断 PIN 码是否为初始化的默认 PIN 码 * @param sn 蓝牙 Key 的 序列号 * @param callback 回调函数,返回 true 表示是默认 PIN 码, false 表示已修 

改过 */ isDefaultPIN(sn: string, callback: OnSafeCallback<boolean>): void 

/** 

- 通过序列号获取证书 

- 返回证书内容的 Base64 编码字符串 

- @param sn 蓝牙 Key 的序列号 

* @param certType 查看的证书类型, 1 为 RSA 签名证书, 2 为 SM2 签 名 

证书 

- @param callback 回调函数,可通过回调提示按键 

*/ 

getCert(sn: string, certType: number, callback: OnSafeCallback<string>): void 

/** * 枚举设备中的证书 * @param sn 蓝牙 Key 的序列号 * @param certType 证书类型( RSA 为 1 ; SM2 为 2 ;枚举所有类型为 0 ) * @param callback 回调函数,返回证书信息列表 */ enumCert(sn: string, certType: number, callback: OnSafeCallback<CertInfo[]>): void 

/** 

- @param sn 蓝牙 Key 的序列号 

- @param signData 签名原文 

- @param pin 蓝牙 Key 的 pin 

- @param signAlg 签名密钥算法( 1 : RSA , 2 : SM2) 

- @param hashId 签名哈希算法 (见算法类型定义) 

- @param callback 回调函数,可通过回调提示按键 

*/ 

sign(sn: string, signData: string, pin: string, signAlg: number, hashId: number, 

callback: OnSafeCallback<string>): void 

/** 

- 断开 APP 与蓝牙 Key 的连接 

*/ 

disconnect(): void 

# 3.3.4 错误码定义 

export namespace EsErrorCodes { 

/** 

* 操作成功 

*/ 

export const ES_SUCCESS: number = 0x00000000; 

/** 

* 操作失败 

*/ 

export const ES_OPERATION_FAILED: number = 0x00000001; 

/** 

# * 设备未连接 

*/ 

export const ES_NO_DEVICE: number = 0x00000002; 

/** 

* 设备忙 

*/ 

export const ES_DEVICE_BUSY: number = 0x0000003; 

/** 

* 参数错误 

*/ 

export const ES_INVALID_PARAMETER: number = 0x0000004; /** 

* 密码错误 

*/ 

export const ES_PASSWORD_INVALID: number = 0x00000005; 

/** 

* 用户取消操作 

*/ 

export const ES_USER_CANCEL: number = 0x00000006; 

/** 

* 操作超时 

*/ 

export const ES_OPERATION_TIMEOUT: number = 0x00000007; 

/** 

# * 没有证书 

*/ 

export const ES_NO_CERT: number = 0x00000008; 

/** 

# * 证书格式不正确 

*/ 

export const ES_CERT_INVALID: number = 0x00000009; 

/** 

* 未知错误 

*/ 

export const ES_UNKNOWN_ERROR: number = 0x0000000A; 

/** 

* PIN 码锁定 

*/ 

export const ES_PIN_LOCK: number = 0x0000000B; 

/** 

# * 操作被打断 

*/ 

export const ES_OPERATION_INTERRUPT: number = 0x0000000C; 

/** 

# * 通讯错误 

*/ 

export const ES_COMM_FAILED: number = 0x0000000D; 

/** 

# * 设备电量不足,不能进行通讯 

*/ 

export const ES_ENERGY_LOW: number = 0x0000000E; 

/** 

# * 蓝牙未打开 

*/ 

export const ES_BLUETOOTH_DISABLE: number = 0x0000000F; 

/** 

# * 不支持蓝牙 ble 

*/ 

export const ES_DEV_WITHOUT_BLE: number = 0x00000010; 

/** 

# * 按键确认 

*/ 

export const ES_PRESS_KEY: number = 0x00000011; 

/** 

* PIN 码为默认 PIN 

*/ 

export const ES_DEFAULT_PIN: number = 0x00000012; 

/** 

# * 设备连接超时 

*/ 

export const ES_CONNECT_TIMEOUT: number = 0x00000013; 

/** 

# * 设备连接断开 

*/ 

export const ES_KEY_DISCONNECT: number = 0x00000014; 

/** 

# * PIN 码长度错误 

*/ 

export const ES_PIN_INVALID_LENGTH: number = 0x00000015; 

/** 

# * PIN 码过于简单 

*/ 

export const ES_PIN_TOO_SIMPLE: number = 0x00000016; 

/** 

# * 新旧密码相同 

*/ 

export const ES_PIN_SAME: number = 0x00000017; 

/** 

# * 序列号与设备不匹配 

*/ 

export const ES_SN_NOT_MATCH: number = 0x00000018; 

} 

} 

# 3.4 接口使用示例 

# 3.4.1 场景一:连接蓝牙 Key 和断开 

根据传入的蓝牙 Key 序列号 SN 建立连接,并在不需要时断开。 典型调用流程 

调用 connect(sn, timeoutSeconds, callback) 发起连接 

使用 getSn(callback) 验证当前连接设备 

使用 disconnect() 断开连接 

# 示例代码 

const esDevice = ESBankBT_WD.getInstance(getContext(this)) 

function connectToKey(sn: string) { 

esDevice.connect(sn, 30, { 

onResult: (errorCode: number, result: number) => { 

if (errorCode === IUKeyInterface.EsErrorCodes.ES_SUCCESS) { 

// 连接成功,可继续业务流程 

} else { 

// TODO: 根据错误码提示用户(如蓝牙未开、超时等) 

} 

} 

# } as IUKeyInterface.OnSafeCallback) 

} 

function disconnectKey() { 

esDevice.disconnect() 

} 

# 3.4.2 场景二: PIN 管理(检查 / 修改 PIN ) 

使用场景 

检查当前 PIN 是否默认 PIN 

获取剩余重试次数 

修改设备 PIN 码 

典型调用流程 

isDefaultPIN(sn, callback) 

getPinRetryTimes(sn, callback) 

modifyPIN(sn, oldPin, newPin, callback) 

示例代码 

检查是否默认 PIN : 

function checkDefaultPIN(sn: string) { 

esDevice.isDefaultPIN(sn, { 

onResult: (errorCode: number, result: boolean) => { 

if (errorCode === IUKeyInterface.EsErrorCodes.ES_SUCCESS) { 

if (result) { 

# // 当前为默认 PIN ,建议提示用户修改 

} else { 

// 已修改过 PIN 

} 

} else { 

// TODO: 错误处理 

} 

} 

} as IUKeyInterface.OnSafeCallback) 

} 

# 获取剩余重试次数: 

function queryPinRetryTimes(sn: string) { 

esDevice.getPinRetryTimes(sn, { 

onResult: (errorCode: number, times: number) => { 

if (errorCode === IUKeyInterface.EsErrorCodes.ES_SUCCESS) { 

// times 为剩余可重试次数 

} else { 

// TODO: 错误处理 

} 

} 

# } as IUKeyInterface.OnSafeCallback) 

} 

修改 PIN : 

function modifyPin(sn: string, oldPin: string, newPin: string) { esDevice.modifyPIN(sn, oldPin, newPin, { 

onResult: (errorCode: number, result: string) => { 

if (errorCode === IUKeyInterface.EsErrorCodes.ES_SUCCESS) { 

# // 修改成功 

} else { 

// 可根据错误码区分:长度不合法、过于简单、 PIN 相同等 

} 

} 

} as IUKeyInterface.OnSafeCallback) 

} 

# 3.4.3 场景三:证书查询 

# 获取设备中证书列表 

获取单个证书的 CN 信息、有效期和证书内容 证书类型说明 

IUKeyInterface.RSA : RSA 证书,约定值为 1 IUKeyInterface.SM2 : SM2 证书,约定值为 2 

若支持枚举所有证书类型,可使用约定值 0 

# 典型调用流程 

enumCert(sn, certType, callback) :获取证书列表 

getCertCN(sn, certType, callback) :获取 CN 

getCertTime(sn, certType, callback) :获取有效期 

getCert(sn, certType, callback) :获取证书内容( Base64 ) 

示例代码 

枚举证书列表: 

function enumCerts(sn: string, certType: number) { 

esDevice.enumCert(sn, certType, { 

onResult: (errorCode: number, certs: IUKeyInterface.CertInfo[]) => { 

if (errorCode === IUKeyInterface.EsErrorCodes.ES_SUCCESS) { 

// certs 中包含证书类型、 CN 、起止时间等 

} else { 

# // TODO: 错误处理 

} 

} 

} as IUKeyInterface.OnSafeCallback<IUKeyInterface.CertInfo[]>) 

} 

获取证书 CN / 有效期 / 内容: 

function getCertInfo(sn: string, certType: number) { 

esDevice.getCertCN(sn, certType, { 

onResult: (code, cn) => { 

if (code === IUKeyInterface.EsErrorCodes.ES_SUCCESS) { // cn 形如 " 颁发者 CN- 持有人 CN" 

} 

# } 

} as IUKeyInterface.OnSafeCallback) 

esDevice.getCertTime(sn, certType, { 

onResult: (code, timeRange) => { 

if (code === IUKeyInterface.EsErrorCodes.ES_SUCCESS) { // 证书起止时间,格式为 “XXXX-XX-XX:XXXX-XX-XX” 

} 

} 

} as IUKeyInterface.OnSafeCallback<string>) 

esDevice.getCert(sn, certType, { 

onResult: (code, certBase64) => { 

if (code === IUKeyInterface.EsErrorCodes.ES_SUCCESS) { 

// certBase64 为 Base64 编码证书 

} 

} 

} as IUKeyInterface.OnSafeCallback<string>) 

} 

3.4.3 场景四:签名操作 

使用蓝牙 Key 对字符串原文进行数字签名,并将签名结果返回 

# 关键参数 

sn: 设备序列号 

signData: 签名原文字符串 

pin: 当前有效 PIN 码 

signAlg: 签名算法( IUKeyInterface.RSA 或 IUKeyInterface.SM2 ) 

hashId: 哈希算法( IUKeyInterface.MD5/SHA1/SHA256/SHA384/ SHA512/SM3 等) 

# 示例代码 

function signData(sn: string, pin: string, data: string, signAlg: number, hashId: number) { 

esDevice.sign(sn, data, pin, signAlg, hashId, { 

onResult: (errorCode: number, signatureBase64: string) => { 

if (errorCode === IUKeyInterface.EsErrorCodes.ES_SUCCESS) { 

// signatureBase64 为 Base64 编码签名结果 

} else if (errorCode === IUKeyInterface.EsErrorCodes.ES_PASSWORD_INVALID) { 

// PIN 错误,可结合 getPinRetryTimes 提示剩余次数 

} else { 

// TODO: 其他错误处理 

} 

} 

} as IUKeyInterface.OnSafeCallback) 

}
