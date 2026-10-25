# POS 电子签名 SDK 接口文档 

版本: v1.0.0 | HarmonyOS API 9+ 

一、概述 

POS 电子签名 SDK 是一个鸿蒙 HarmonyOS 签名组件库,提供手写签 名、订单信息处理和证据保存功能。 

# 1.1 功能特性 

手写签名组件 (GFAHardSign) :支持手写签名、签名图片生成和保 存,支持批量订单处理 

订单数据管理 (OrderData) :订单信息的结构化定义 

证据响应处理 (EvidenceResponse) :签名证据保存的响应数据模型, 支持多证书响应 

HUKS P10 生成器 (HuksP10Generator) :基于华为通用密钥库安全生 成 P10 证书请求 

HTTP 工具类 (HttpUtils) :支持普通 POST 和 HTTPS 双向认证请求 XML 数据处理 (XmlDataUtils) :支持批量订单 XML 生成和解析 配置管理 (ConfigUtils) :支持从配置文件加载应用配置 

1.2 版本要求 

项目 

要求 

HarmonyOS API 版本 

API 9 及以上 

DevEco Studio 

3.1.0 Release 及以上 

# 1.3 依赖说明 

本库依赖以下 HarmonyOS 系统能力: 

依赖模块 说明 

@kit.ArkUI UI 组件能力 @kit.ImageKit 图片处理能力 

@kit.BasicServicesKit 

基础服务 

@kit.CryptoArchitectureKit 

加密架构 

@kit.CoreFileKit 

文件处理能力 

@ohos.security.huks HUKS 密钥管理服务 

@kit.NetworkKit 

网络请求能力 

二、配置说明 

# 2.1 创建配置文件 

在项目的 rawfile 目录下创建 gfa_config.json 文件: 

{ 

"appConfig": { 

"appId": "your-app-id", 

"apiUrl": "https://your-api-endpoint.com/api", 

"deviceIdType": "ODID" 

} 

} 

配置字段说明: 字段 类型 必填 说明 

appId string 是 

应用标识符 

apiUrl 

string 是 服务端 API 地址 

deviceIdType 

string 

# 否 

设备标识类型。配置为 "ODID" 时使用系统 ODID 作为终端标识;不配 置或留空时,自动生成 "unkow"+ 随机 ID 作为匿名标识。默认不配 置。 

# 2.2 配置网络权限 

在 module.json5 中添加网络权限: 

{ 

"requestPermissions": [ 

{ 

"name": "ohos.permission.INTERNET" 

} 

] 

} 

# 2.3 配置 HTTPS 双向认证证书 

组件默认使用 HTTPS 双向认证方式上传签名数据,需要将以下证书 文件放入 rawfile 目录: 

your-module/src/main/resources/rawfile/ 

`├──` client.crt # 客户端证书( PEM 格式) 

`├──` client.key # 客户端私钥( PEM 格式,无密码) 

`└──` server_ca.crt # 服务端根 CA 证书(用于验证服务端证书) 

# ⚠ 注意事项: 

apiUrl 必须使用域名而非 IP 地址,否则会因证书主机名不匹配导致 

# SSL 验证失败 

server_ca.crt 必须是签发服务端证书的根 CA 证书(自签名),而非 服务端叶证书 

client.key 为明文 RSA 私钥( BEGIN RSA PRIVATE KEY ),无需密 码 

证书文件每次启动时会自动覆盖写入沙箱,确保使用最新版本 

三、 API 文档 

3.1 GFAHardSign 组件 

手写签名核心组件,支持单订单和批量订单签名。 

属性 

类型 

必填 

说明 

orderDataList 

OrderData[] 

是 

订单信息数据列表(支持批量订单) 

onComplete 

(response: SaveEvidenceResponse) => void 

否 

签名完成回调,结果以此为准 

签名交互说明: 

用户完成手写后,组件会在停笔 1 秒后自动截图并锁定签名区,期间 不可继续书写 

" " " " 锁定后触摸签名区会提示: 如要重新签名请点击 删除 后重新签名 " " 点击 删除 按钮可清空笔迹并重新书写 

注意:使用时传入包含一个元素的数组即可完成单订单签名。 

3.2 OrderData 类 订单信息数据模型。 

属性 类型 说明 

orderId string 订单编号 

name 

string 收件人姓名 

money string 订单金额 number string 商品数量 

phone 

string 

联系电话 

address 

string 

收货地址 

3.3 SaveEvidenceResponse 类 签名保存响应模型。 

属性 

类型 说明 

evidenceResponse EvidenceResponse 

证据响应主体 

3.4 EvidenceResponse 类 证据响应数据模型,支持多证书响应。 属性 类型 说明 

message 

string 

# 响应消息 

status string 响应状态 

certResponseList CertResponse[] 证书响应列表 3.5 CertResponse 类 单条证书响应数据模型。 属性 类型 说明 

message string 证书消息 status string 证书状态 orderId string 订单编号 

# 四、使用示例 

# 4.1 基础使用(单订单) 

import { GFAHardSign, OrderData, SaveEvidenceResponse } from 'gfalibrary'; 

@Entry 

@Component 

struct SignPage { 

@State orderDataList: OrderData[] = []; 

aboutToAppear() { 

const order = new OrderData(); 

order.orderId = 'ORDER2024001'; 

order.name = ' 张三 '; order.money = '100.00'; order.number = '1'; 

order.phone = '13800138000'; order.address = ' 北京市朝阳区 xxx 街道 '; 

this.orderDataList = [order]; 

} 

build() { 

Column() { GFAHardSign({ 

orderDataList: this.orderDataList, 

onComplete: (response: SaveEvidenceResponse) => { 

console.info(' 签名成功 :', JSON.stringify(response)); 

} 

}) 

} 

} 

} 

# 4.2 批量订单签名 

import { GFAHardSign, OrderData, SaveEvidenceResponse } from 'gfalibrary'; 

@Entry 

@Component 

struct BatchSignPage { 

@State orderDataList: OrderData[] = []; 

aboutToAppear() { 

const order1 = new OrderData(); 

order1.orderId = 'ORDER001'; 

order1.name = ' 张三 '; 

order1.money = '100.00'; 

order1.number = '1'; 

order1.phone = '13800138001'; 

order1.address = ' 北京市朝阳区地址 1'; 

const order2 = new OrderData(); 

order2.orderId = 'ORDER002'; 

order2.name = ' 李四 '; order2.money = '200.00'; order2.number = '2'; order2.phone = '13800138002'; order2.address = ' 北京市海淀区地址 2'; 

this.orderDataList = [order1, order2]; } 

build() { Column() { GFAHardSign({ orderDataList: this.orderDataList, 

onComplete: (response: SaveEvidenceResponse) => { console.info(' 批量签名成功 :', JSON.stringify(response)); 

} 

}) 

} 

} 

} 

# 4.3 订单数据结构示例 

import { OrderData } from 'gfalibrary'; 

const orderData: OrderData = new OrderData(); 

orderData.orderId = 'ORDER2024001'; 

orderData.name = ' 张三 '; 

orderData.money = '100.00'; 

orderData.number = '1'; 

orderData.phone = '13800138000'; 

orderData.address = ' 北京市朝阳区 xxx 街道 '; 

# 4.4 处理签名响应 

import { SaveEvidenceResponse, EvidenceResponse, CertResponse } from 'gfalibrary'; 

function handleSignResponse(response: SaveEvidenceResponse) { 

const evidenceResponse: EvidenceResponse = response.evidenceResponse; 

console.info(' 消息 :', evidenceResponse.message); 

console.info(' 状态 :', evidenceResponse.status); 

if (evidenceResponse.certResponseList.length > 0) { 

const cert: CertResponse = evidenceResponse.certResponseList[0]; 

console.info(' 证书消息 :', cert.message); 

console.info(' 证书状态 :', cert.status); 

console.info(' 订单 ID:', cert.orderId); 

} } 

五、错误码说明 错误码 说明 210001 订单签名成功,整体操作成功 210005 订单申请证书成功 210011 重复订单 220001 网络连接失败 220002 上传订单发生错误 220003 查询订单失败 

北京国富安电子商务安全认证有限公司 · POS 电子签名 SDK 接口文档
