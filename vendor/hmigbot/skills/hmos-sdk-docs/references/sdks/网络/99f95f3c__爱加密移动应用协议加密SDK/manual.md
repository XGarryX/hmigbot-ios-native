# 北京智游网安科技有限公司 

北京智游网安科技有限公司 

爱加密移动应用协议加密 SDK 

集成手册(鸿蒙) 

V1.5.0 

文档密级:完全公开 

# ■ 版权声明 

本文档中出现的文字叙述、文档格式、插图、照片、方法、过程等内 容,除另有特别注明,版权均属智游网安所有,受到有关产权及版权 法保护。任何个人、机构未经智游网安的书面授权许可,不得以任何 方式复制或引用本文的任何片断。 

# ■ 免责条款 

本文档所含内容仅用于为平台最终用户提供信息,如内容有更改或撤 回,恕不另行通知。本公司已尽最大努力保证资料的准确可靠,但不 提供任何形式的担保。 

# 目 录 

1 文档定义 1 

1.1 编写目的 1 

1.2 适用范围 1 

1.3 术语与缩略语 1 

1.4 运行环境 1 

- 2 集成步骤 2 

2.1 SDK 文件结构 2 

2.2 使用 HAR 导入 SDK 2 

3 API 接口 3 

3.1 授权字符串接口 3 

3.1.1 引入授权类 3 

3.1.2 接口 3 

3.1.3 参数说明 3 

3.1.4 返回值 3 

3.1.5 建议 4 

3.2 普通固定模式 4 

3.2.1 引用普通固定模式算法类 4 

3.2.2 字符串加密接口 4 

3.2.3 字符串解密接口 5 

3.2.4 数据流加密接口 5 

3.2.5 数据流解密接口 5 

3.3 一次一密 6 

# 3.3.1 引入一次一密算法类 6 

3.3.2 字符串加密接口 6 

3.3.3 字符串解密接口 6 

3.3.4 数据流加密接口 6 

3.3.5 数据流解密接口 7 

3.4 单向模式接口 7 

3.4.1 引入单向模式算法类 7 

3.4.2 字符串加密接口 7 

3.4.3 字符串解密接口 7 

3.4.4 数据流加密接口 8 

3.4.5 数据流解密接口 8 

3.5 Demo 实现演示代码 8 

3.6 注意 9 

4 公司介绍 10 

文档定义 

# 编写目的 

为了用户更好的使用爱加密移动应用协议加密 SDK (鸿蒙版)的相关 功能,特编写该文档。 

# 适用范围 

本文档适用于使用爱加密移动应用协议加密 SDK (鸿蒙版)的客户公 司内部开发人员、测试人员,爱加密安全技术人员、测试人员、售后 实施人员。 

# 术语与缩略语 

说明:本部分主要是对本文档所出现的重要缩略语进行解释 

编写、术语 

解释 

SDK 

协议加密 SDK (鸿蒙版) 

运行环境 

SDK 编译环境: DevEco Studio 5.0.3.800 Release SDK 运行环境:鸿蒙 api 12 以上版本系统 

集成步骤 

SDK 文件结构 

使用 HAR 导入 SDK 

将 har 文件复制到项目 libs 目录。 

在需要使用 sdk 文件模块的 oh-package.json5 文件中加入如下配置。 

"dependencies": { 

"@ohos/ohosJMEBoxLib": "file:../libs/ohosJMEBoxLib.har" 

} 

# 安装依赖包 

DevEco 命令行运行 ohpm install 安装依赖包 

API 接口 

# 授权字符串接口 

引入授权类 

```arkts
import { OhosJMEncryptBox } from '@ohos/ohosJMEBoxLib'; 
```

接口 

static init(lic: string): string; 

参数说明 参数名称 类型 描述 可选 / 必选 

licensekey 

字符串 授权码 必选 

返回值 

Json 字符串 {"statusCode":1,"expiredDate":"0","describe":"success"} 获取授权状态返回码 

JSON.parse(res).statusCode 

# 获取状态描述 

JSON.parse(res).describe 

获取到期时间 

JSON.parse(res).expiredDate 

# 授权状态码说明: 

状态码 

描述 

0 

授权码错误 

1 

授权成功 

-1 

# 授权码错误或者格式错误 

-2 

授权码或者格式错误 

-3 

# 授权到期 

-4 

包名验证失败 

-5 

签名验证失败 

-6 

napi 获取参数失败 

建议 

授权接口放在应用入口 onCreate 调用即可。注意:在调用加解密方法 

# 之前要先设置从爱加密获取的授权串 

# 普通固定模式 

引用普通固定模式算法类 

```arkts
import { OhosJMEncryptBox } from '@ohos/ohosJMEBoxLib'; 
```

# 字符串加密接口 

将字符串进行加密并用 Base64 编码,定义如下: 

static encryptToBase64(encryptStr: string, algoType: number): string; 

encryptStr :需要加密的字符串。 

algorithmType: 选择的加密算法,支持 AES 和 SM4, 如 OhosJMEncryptBox.AES 或者 OhosJMEncryptBox.SM4 

返回加密后的字符串的 base64 编码 

字符串解密接口 

将 Base64 解密回原字符串,定义如下: 

static decryptFromBase64(decryptStr: string, algoType: number): string; 

decryptStr :需要解密的字符串的 base64 编码。 

algorithmType: 选择的加密算法,支持 AES 和 SM4, 如 OhosJMEncryptBox.AES 或者 OhosJMEncryptBox.SM4 

# 数据流加密接口 

加密数据流,用于对文件进行加密,返回 byte 数组。定义如下: 

static encryptToBytesFromBytes(data: ArrayBuffer, algoType: number): ArrayBuffer; 

data :需要加密的 ArrayBuffer 数组。 

algorithmType: 选择的加密算法,支持 AES 和 SM4, 如 OhosJMEncryptBox.AES 或者 OhosJMEncryptBox.SM4 

返回加密后的 ArrayBuffer 类型数据 

# 数据流解密接口 

解密数据流,用于对文件进行解密,返回 ArrayBuffer 数组。定义如 下: 

static decryptFromBytesToBytes(data: ArrayBuffer, algoType: number): ArrayBuffer; 

data :需要解密的 ArrayBuffer 数组。 

algorithmType: 选择的加密算法,支持 AES 和 SM4, 如 OhosJMEncryptBox.AES 或者 OhosJMEncryptBox.SM4 

返回解密后的 ArrayBuffer 类型数据 

一次一密 

引入一次一密算法类 

```arkts
import { OhosJMEncryptBoxByRandom } from '@ohos/ ohosJMEBoxLib'; 
```

# 字符串加密接口 

将字符串进行加密并用 Base64 编码,定义如下: 

static encryptToBase64(encryptStr: string, algoType: number): string; 

encryptStr :需要加密的字符串。 

algorithmType: 选择的加密算法,支持 AES 和 SM4, 如 OhosJMEncryptBoxByRandom .AES 或者 OhosJMEncryptBoxByRandom .SM4 

返回加密后的字符串的 base64 编码 

字符串解密接口 

# 将 Base64 解密回原字符串,定义如下: 

static decryptFromBase64(decryptStr: string, algoType: number): string; 

decryptStr :需要解密的字符串的 base64 编码。 

algorithmType: 选择的加密算法,支持 AES 和 SM4, 如 OhosJMEncryptBoxByRandom.AES 或者 OhosJMEncryptBoxByRandom.SM4 

# 数据流加密接口 

# 加密数据流,用于对文件进行加密,返回 byte 数组。定义如下: 

static encryptToBytesFromBytes(data: ArrayBuffer, algoType: number): ArrayBuffer; 

data :需要加密的 ArrayBuffer 数组。 

algorithmType: 选择的加密算法,支持 AES 和 SM4, 如 OhosJMEncryptBoxByRandom.AES 或者 OhosJMEncryptBoxByRandom.SM4 

返回加密后的 ArrayBuffer 类型数据 

# 数据流解密接口 

解密数据流,用于对文件进行解密,返回 ArrayBuffer 数组。定义如 下: 

static decryptFromBytesToBytes(data: ArrayBuffer, algoType: number): ArrayBuffer; 

data :需要解密的 ArrayBuffer 数组。 

algorithmType: 选择的加密算法,支持 AES 和 SM4, 如 OhosJMEncryptBoxByRandom.AES 或者 OhosJMEncryptBoxByRandom.SM4 

返回解密后的 ArrayBuffer 类型数据 

单向模式接口 

# 引入单向模式算法类 

```arkts
import { OhosJMEncryptBoxByUnidirectional } from '@ohos/ ohosJMEBoxLib'; 
```

# 字符串加密接口 

将字符串进行加密并用 Base64 编码,定义如下: 

static encryptToBase64(encryptStr: string, encMode: number): string; 

encryptStr :需要加密的字符串。 

encMode: 选择的算法模式,支持固定模式 Normal 和随机模式 Random, 如 OhosJMEncryptBoxByUnidirectional.NormalMode 或者 OhosJMEncryptBoxByUnidirectional .RandomMode 

返回加密后的字符串的 base64 编码 

字符串解密接口 

将 Base64 解密回原字符串,定义如下: 

static decryptFromBase64(decryptStr: string, encMode: number): string; 

decryptStr :需要解密的字符串的 base64 编码。 

encMode: 选择的算法模式,支持固定模式 Normal 和随机模式 Random, 如 OhosJMEncryptBoxByUnidirectional.NormalMode 或者 OhosJMEncryptBoxByUnidirectional .RandomMode 

# 数据流加密接口 

加密数据流,用于对文件进行加密,返回 byte 数组。定义如下: 

static encryptToBytesFromBytes(data: ArrayBuffer, encMode: number): ArrayBuffer; 

data :需要加密的 ArrayBuffer 数组。 

encMode: 选择的算法模式,支持固定模式 Normal 和随机模式 

Random, 如 OhosJMEncryptBoxByUnidirectional.NormalMode 或者 OhosJMEncryptBoxByUnidirectional .RandomMode 

返回加密后的 ArrayBuffer 类型数据 

# 数据流解密接口 

解密数据流,用于对文件进行解密,返回 ArrayBuffer 数组。定义如 下: 

static decryptFromBytesToBytes(data: ArrayBuffer, encMode: number): ArrayBuffer; 

data :需要解密的 ArrayBuffer 数组。 

选择的算法模式,支持固定模式 Normal 和随机模式 Random, 如 OhosJMEncryptBoxByUnidirectional.NormalMode 或者 OhosJMEncryptBoxByUnidirectional .RandomMode 

返回解密后的 ArrayBuffer 类型数据 

# Demo 实现演示代码 

在 App 的 onCreate 方法中,添加 licenceKey 授权认证。如下图 

export default class App extends AbilityStage { 

onCreate() { 

console.info('Application onCreate') 

let key = ' 请填写授权码 '; 

let res = OhosJMEncryptBox.init(key); 

} 

} 

# 注意 

授权码:用户需提供应用包名和证书指纹给售后生成授权码。 

# 公司介绍 

北京智游网安科技有限公司(爱加密)成立于 2013 年,总部位于北 京,研发及运营中心位于深圳,同时在全国各地设立了 12 个分支机 构,拥有员工 400 多人。 

爱加密( www.ijiami.cn) 是专业的移动信息安全服务提供商,专注于 移动应用安全、大数据、物联网及工业互联网安全,坚持以用户需求 为导向、持续不断的创新,致力于为客户提供全方位、一站式的移动 安全全生命周期解决方案。爱加密的服务宗旨是通过革新性安全方案 和 7x24 小时全天候的专业服务,打造和谐、强大、高度安全的万物互 联生态环境。 

爱加密拥有安全防护、安全检测、安全管理、业务运营、威胁感知、 安全监管、安全服务七大产品体系,贯穿了应用设计评估、安全开发 测试、应用优化、应用安全发布及应用上线运营阶段的整个生命周 期。目前行业用户遍及金融、运营商、政府、电商、能源、教育、游 戏等多个行业。至今共服务企业及开发者用户 50 万 + ,保护移动应用 100 万 + ,监测互联网应用 1500 万 + ,累计覆盖 10 亿移动终端。
