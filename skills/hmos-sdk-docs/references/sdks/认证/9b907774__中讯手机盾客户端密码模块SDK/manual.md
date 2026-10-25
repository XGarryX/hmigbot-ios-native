手机盾客户端密码模块 V2.10.2 东方中讯数字证书认证有限公司 

2025 年 8 月 

使用指南 

WtxtgmHelper SDK 工具类 函数名称 

# 简要描述 

setDefaultConfig 

SDK 设置配置,使用 SDK 之前需要配置 

switchUser 

SDK 初始化,切换用户 

systemConfig 

获取服务端配置 

moduleInfo 

获取模块信息,包括版本号、用户名、密钥标识与对应的证书标识等 信息 

moduleState 

获取模块状态 

resetModule 

模块置零 

setAuthenticateMode 

设置本地身份鉴别模式 

getAuthenticateMode 

获取本地身份鉴别模式 

requestSmsAck 

请求短信验证码 

changePassword 

修改口令 

forgetPassword 

忘记口令 

genRandom 生成随机数 

sm2Sign SM2 协同签名 

sm2Verify SM2 验签 sm2Encrypt SM2 加密 sm2Decrypt SM2 协同解密 

requestCertWithCA 

请求生成证书(指定 CA ) readSignCert 

读签名证书 

readSignCert 

读加密证书 

getCertInfo 解析证书信息 

verifyPassword 

校验口令 

uploadLogs 

# 上传日志 

# 下载安装与使用说明 

`ohpm i @ezca/wtxt-sdk` 

import { SdkConfig, SzOther } from "../model/SdkConfig"; 

import { Asn1, WTXT_Cert, WTXT_CertGB, WTXT_PasswordCount, WTXT_RequestCertOut, WTXT_SM2CoDecryptPlain, WTXT_ModuleState, WTXT_MODULEINFO, WTXT_SystemConfig, WTXT_ArrayBuffer, WTXT_LocalPinMode } from "../model/ WtxtModel"; 

/** 

* ArrayBuffer 转 base64 

*/ 

export declare function arrayBufferToB64(arraybuffer: ArrayBuffer): string; 

export declare class WtxtgmHelper { 

private static wtxtgm; 

/** 

- 是否已经初始化, true 已初始化, false 未初始化 

*/ 

static initStatus: boolean; 

/** 

# * sdk 配置信息 

*/ 

private static config; 

/** 

# * 用户信息 

*/ 

private static userInfo; 

/** 

# * 设置默认配置 

*/ 

static setDefaultConfig(configs: (config: SdkConfig) => void): void; 

/** 

# * 查询模块状态 

*/ 

static moduleState(): WTXT_ModuleState; 

/** 

# * 查询模块信息 

- @returns 

*/ 

static moduleInfo(): WTXT_MODULEINFO; 

/** 

# * 获取配置 

- @param appId 应用唯一标识 

- @param unit 单位 UTF8 编码 

*/ 

static systemConfig(appId?: string, unit?: string): WTXT_SystemConfig; 

static resetModule(): number; 

/** 

# * 初始化 SDK 

*/ 

static init(): number; 

/** 

# * 切换用户 

- @param mobileNum 手机号码 

- @param userName 用户名 

- @param appId 应用唯一标识 

- @param uuId 用户唯一标识 

- @param unit 单位 UTF8 编码 

*/ 

static switchUser(mobileNum: string, userName: string, uuId: string, appId?: string, unit?: string): number; 

/** 

- 请求证书 (CA) 

- @param smsCode 短信验证码 

- @param password 密码 

- @param szCA 指定 CA 

# * @param szOther 请求信息 JSON 格式 

*/ 

static requestCertWithCA(smsCode: string, password: string, szCA: string, szOther: SzOther, certUseType: number): Promise<WTXT_RequestCertOut>; 

/** 

# * 发送短信验证 

*/ 

static requestSmsAck(): number; 

/** 

# * 修改口令 

- @param szSmsAck 短信验证码,可为空 

- @param szOldPassword 旧密码 

- @param szNewPassword 新密码 

*/ 

static changePassword(szSmsAck: string, szOldPassword: string, szNewPassword: string): WTXT_PasswordCount; 

/** 

# * 忘记口令 

- @param szSmsAck 短信验证码 

- @param szNewPassword 新密码 

- @returns 错误码 

*/ 

static forgetPassword(szSmsAck: string, szNewPassword: string): number; 

/** 

# * 验证口令 

# * @param password 密码 

*/ 

static verifyPassword(password: string): WTXT_PasswordCount; 

/** 

# * 读取签名证书 

*/ 

static readSignCert(): WTXT_Cert; 

/** 

# * 读取加密证书 

*/ 

static readEncCert(): WTXT_Cert; 

/** 

# * 解析证书 

- @param iNameID 证书信息项 

- @param iSubNameID 证书信息子项 

- @returns 证书项信息 

*/ 

static getCertInfo(szCert: ArrayBuffer, iNameID: number, iSubNameID: number): WTXT_CertGB; 

/** 

* sm2 加密 

# * @param intData 原文数据 

*/ 

static sm2Encrypt(intData: ArrayBuffer): Asn1; 

/** 

* sm2 解密 

- @param intData 密文数据 

*/ 

static sm2Decrypt(encData: ArrayBuffer): WTXT_SM2CoDecryptPlain; 

/** 

- sm2 签名 

- @param intData 原文数据 

*/ 

static sm2Sign(inData: ArrayBuffer): Asn1; 

/** 

- sm2 签名验证 

- @param signData 签名值 

- @param inData 签名原文 

*/ 

static sm2Verify(signData: ArrayBuffer, inData: ArrayBuffer): number; 

/** 

# * 产生随机数 

# * @param randomLen 随机数长度 

*/ 

static genRandom(randomLen: number): WTXT_ArrayBuffer; 

/** 

# * 设置身份鉴别模式 

- @param authMode 鉴别模式 0= 密码, 1= 指纹, 2= 人脸 

# * @returns 错误码 

*/ 

static setAuthenticateMode(authMode: number): number; 

/** 

# * 获取身份鉴别模式 

# * @returns 错误码 

*/ 

static getAuthenticateMode(): WTXT_LocalPinMode; 

/** 

# * 上传日志 

*/ 

static uploadLogs(appName: string): number; 

}
