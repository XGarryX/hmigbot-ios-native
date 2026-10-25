> 来源: ohpm 中央仓 README(T1 信源) | 包: `@hw-agconnect/petal-aegis` | ohpm 最新版: 1.4.11-300 | 抓取: 2026-07-16
> 注意: 版本可能比市场快照新,以此为准时核对 CHANGELOG

## 简介

Aegis安全编码SDK提供丰富、易用、安全的加解密算法能力,几行代码实现加解密。基于HarmonyOS官方SDK封装,支持国际标准算法、国密算法,专业团队持续维护更新。

将原本复杂的加解密算法简化到几行代码,让您轻松保护个人数据和敏感信息,保障用户数据和应用数据的机密性、完整性和不可抵赖性。

## 主要功能

- 机密性保护:各种类型的安全加解密算法保障用户数据的机密性。

- 完整性和不可抵赖性保护:各种类型的安全消息摘要算法和数字签名算法,保障用户数据的完整性和不可抵赖性。

- 密钥管理:提供密钥的安全生成、存储、协商、派生等全生命周期管理能力。

## 主要优势

- 安全可靠:基于HarmonyOS官方SDK封装,提供强安全密码算法。

- 功能丰富:支持国际密码算法、国家商用密码算法(国密)、基于密钥管理服务的国际密码算法和国密算法。

- 极简集成:API简单易用,几行代码实现加解密。

- 轻量级:SDK包体积小,对应用包体积大小影响极低。

[更多](https://developer.huawei.com/consumer/cn/doc/AppGallery-connect-Guides/aegis-overview-0000001819350860)

## 下载安装

```shell

ohpm install @hw-agconnect/petal-aegis

```

## 功能列表

| 类型           | 地址                                                                                                                                   |

|--------------|--------------------------------------------------------------------------------------------------------------------------------------|

| 密钥生成         | [安全随机数生成](https://developer.huawei.com/consumer/cn/doc/AppGallery-connect-References/ohaegrandom-0000001819216574)                   | 

| 密钥生成         | [RSA密钥生成](https://developer.huawei.com/consumer/cn/doc/AppGallery-connect-References/ohaeggeneratersakeypairbase64-0000001864601898) | 

| 密钥生成         | [ECC密钥生成](https://developer.huawei.com/consumer/cn/doc/AppGallery-connect-References/ohaeggenecckeypairbase64-0000001910481573)      | 

| 密钥派生         | [PBKDF2密钥派生](https://developer.huawei.com/consumer/cn/doc/AppGallery-connect-References/ohaegpbkdf2sha256-0000001910590365)          |

| 消息摘要Hash     | [哈希算法(消息摘要)](https://developer.huawei.com/consumer/cn/doc/AppGallery-connect-References/ohaegsha256texthex-0000001864411716)         |

| 消息认证Mac      | [消息认证算法](https://developer.huawei.com/consumer/cn/doc/AppGallery-connect-References/ohaeghmacsha256texthex-0000001864411720)         | 

| 对称加密         | [AES-GCM对称加解密](https://developer.huawei.com/consumer/cn/doc/AppGallery-connect-References/ohaegaesgcmenctext-0000001909994589)       | 

| 对称加密         | [AES-CBC对称加解密](https://developer.huawei.com/consumer/cn/doc/AppGallery-connect-References/ohaegaescbcenctext-0000001866096105)       | 

| 对称加密         | [基于HUKS的AES-GCM对称加解密](https://developer.huawei.com/consumer/cn/doc/AppGallery-connect-References/ohaeghuksenctext-0000001911924845)  | 

| 对称加密         | [SM4-CBC对称加解密](https://developer.huawei.com/consumer/cn/doc/AppGallery-connect-References/ohaegsmenctext-0000001864225580)           | 

| 非对称加密        | [RSA非对称加解密](https://developer.huawei.com/consumer/cn/doc/AppGallery-connect-References/ohaegrsaenctext-0000001864467536)             | 

| 签名           | [RSA签名验签](https://developer.huawei.com/consumer/cn/doc/AppGallery-connect-References/ohaegsignrsawithpsstext-0000001910388781)       | 

| 签名           | [ECDSA签名验签](https://developer.huawei.com/consumer/cn/doc/AppGallery-connect-References/ohaegeccsigntext-0000001910515581)            | 

| 编码转换工具       | [编码转换工具](https://developer.huawei.com/consumer/cn/doc/AppGallery-connect-References/aegstrutil-0000001867413772)                     |

------

## 全量api详情

[请查看api详情](https://developer.huawei.com/consumer/cn/doc/AppGallery-connect-Guides/aegis-overview-0000001819350860)

------

## 接入Skill(可选)

[接入Skill](https://developer.huawei.com/consumer/cn/doc/AppGallery-connect-Guides/aegis-skill-0000002583700274)

------

## 意见反馈

[意见反馈链接](https://developer.huawei.com/consumer/cn/doc/AppGallery-connect-Guides/aegis-feedback-0000002014975881)
