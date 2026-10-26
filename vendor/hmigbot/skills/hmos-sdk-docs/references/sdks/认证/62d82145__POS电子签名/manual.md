# POS 电子签名 SDK 使用指南 

版本: v1.0.0 | HarmonyOS API 9+ 

本文档旨在帮助开发者快速完成 POS 电子签名 SDK 的集成,涵盖 HAR 包引入、配置、代码接入以及常见错误码排查。 

一、安装 

SDK 以 HAR 包形式发布,请按以下步骤完成引入: 

步骤 1 :将生成的 gfalibrary.har 文件复制到目标项目的 libs 目录 步骤 3 :在目标模块的 oh-package.json5 中添加依赖: 

{ 

"dependencies": { 

"gfalibrary": "file:./libs/gfalibrary.har" 

} 

} 

步骤 4 :执行安装命令: 

ohpm install 

安装完成后,即可在代码中通过 import 语句引用 SDK 提供的组件与 类型。 

二、配置 

# 2.1 创建配置文件 

在项目的 rawfile 目录( your-module/src/main/resources/ rawfile/ )下创建 gfa_config.json 文件: 

{ 

"appConfig": { 

"appId": "your-app-id", 

"apiUrl": "https://your-api-endpoint.com/api", 

"deviceIdType": "ODID" 

} 

} 

配置字段说明: 字段 类型 必填 说明 

appId string 是 应用标识符,由服务端分配 apiUrl string 是 服务端 API 地址,必须使用域名 

deviceIdType 

string 

否 

设备标识类型。配置为 "ODID" 时使用系统 ODID 作为终端标识;不 配置或留空时,自动生成 "unkow"+ 随机 ID 作为匿名标识 

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

SDK 支持 HTTPS 双向认证方式上传签名数据,需要将以下证书文件 放入 rawfile 目录: your-module/src/main/resources/rawfile/ 

`├──` client.crt # 客户端证书( PEM 格式) 

`├──` client.key # 客户端私钥( PEM 格式,无密码) 

`└──` server_ca.crt # 服务端根 CA 证书(用于验证服务端证书) 

# ⚠ 证书配置注意事项: 

apiUrl 必须使用域名而非 IP 地址,否则会因证书主机名不匹配导致 SSL 验证失败 server_ca.crt 必须是签发服务端证书的根 CA 证书(自签名),而非 

# 服务端叶证书 

client.key 为明文 RSA 私钥( BEGIN RSA PRIVATE KEY ),无需密 码 

证书文件每次启动时会自动覆盖写入沙箱,确保使用最新版本 

双向认证为可选功能: SDK 会优先尝试加载证书启用双向认证,加载 失败则自动降级为普通 HTTPS ,不阻断业务流程 

三、使用示例 

3.1 基础使用(单订单签名) 

最简集成场景:在页面中直接嵌入 GFAHardSign 组件,传入单个订 单数据即可。 

import { GFAHardSign, OrderData, SaveEvidenceResponse } from 'gfalibrary'; 

@Entry 

@Component 

struct SignPage { 

@State orderDataList: OrderData[] = []; 

aboutToAppear() { 

const order = new OrderData(); 

order.orderId = 'ORDER2024001'; 

order.name = ' 张三 '; 

order.money = '100.00'; 

order.number = '1'; 

order.phone = '13800138000'; 

# order.address = ' 北京市朝阳区 xxx 街道 '; 

this.orderDataList = [order]; 

} 

build() { 

Column() { 

GFAHardSign({ 

orderDataList: this.orderDataList, 

onComplete: (response: SaveEvidenceResponse) => { 

console.info(' 签名成功 :', JSON.stringify(response)); 

} 

}) 

} 

} 

} 

# 3.2 批量订单签名 

一次签名同时覆盖多个订单,签名图片将应用于全部订单。 

import { GFAHardSign, OrderData, SaveEvidenceResponse } from 'gfalibrary'; 

@Entry 

@Component 

struct BatchSignPage { 

@State orderDataList: OrderData[] = []; 

aboutToAppear() { 

const order1 = new OrderData(); 

order1.orderId = 'ORDER001'; 

order1.name = ' 张三 '; order1.money = '100.00'; order1.number = '1'; order1.phone = '13800138001'; order1.address = ' 北京市朝阳区地址 1'; 

```arkts
const order2 = new OrderData(); order2.orderId = 'ORDER002'; order2.name = ' 李四 '; order2.money = '200.00'; order2.number = '2'; order2.phone = '13800138002'; order2.address = ' 北京市海淀区地址 2'; this.orderDataList = [order1, order2]; } build() { Column() { 
```

# GFAHardSign({ 

orderDataList: this.orderDataList, 

onComplete: (response: SaveEvidenceResponse) => { console.info(' 批量签名成功 :', JSON.stringify(response)); 

} 

# }) 

} 

} 

} 

# 3.3 订单数据结构 

OrderData 是 SDK 定义的订单数据模型,包含以下字段: 属性 类型 说明 

orderId 

string 订单编号 

name 

string 收件人姓名 

money 

string 

# 订单金额 

number 

string 

商品数量 

phone string 联系电话 

address string 

收货地址 

# 创建示例: 

import { OrderData } from 'gfalibrary'; 

const orderData: OrderData = new OrderData(); 

orderData.orderId = 'ORDER2024001'; 

orderData.name = ' 张三 '; 

orderData.money = '100.00'; 

orderData.number = '1'; 

orderData.phone = '13800138000'; 

orderData.address = ' 北京市朝阳区 xxx 街道 '; 

# 3.4 处理签名响应 

onComplete 回调返回 SaveEvidenceResponse 对象,可通过其嵌套结 

# 构获取签名结果与证书信息: 

import { SaveEvidenceResponse, EvidenceResponse, CertResponse } from 'gfalibrary'; 

GFAHardSign({ 

orderDataList: this.orderDataList, 

onComplete: (response: SaveEvidenceResponse) => { 

const evidence: EvidenceResponse = response.evidenceResponse; 

console.info(' 响应消息 :', evidence.message); 

console.info(' 响应状态 :', evidence.status); 

# // 遍历证书响应列表 

for (let cert of evidence.certResponseList) { 

console.info(` 订单 ${cert.orderId}: 状态 =${cert.status}, 消息 =${cert.message}`); 

} 

} 

}) 

# 3.5 签名交互说明 

GFAHardSign 组件的用户交互流程如下: 

用户在签名区内手写签名,轨迹实时渲染 

停笔 1 秒后自动截图并锁定签名区,期间不可继续书写 

" " " " 锁定后触摸签名区会提示: 如要重新签名请点击 删除 后重新签名 " " 点击 删除 按钮可清空笔迹,重新书写 

点击 " 完成 " 按钮触发签名流程: Hash 计算 → RSA 加密 → P10 生成 → 上传服务器 → 回调 onComplete " " " " 未签名时点击 完成 会提示 请您先签名 

四、常见错误码 

集成过程中若遇到问题,可参考以下错误码进行排查: 

错误码 

说明 

排查建议 

210001 

订单签名成功,整体操作成功 正常返回,无需处理 

210005 

订单申请证书成功 

正常返回,无需处理 

210011 

重复订单 

检查传入的 orderId 是否已被签名过 

220001 

网络连接失败 

检查网络连接与 apiUrl 配置是否正确 

220002 

上传订单发生错误 

# 检查服务端接口是否正常, XML 数据格式是否符合预期 

220003 

查询订单失败 

检查服务端是否支持订单状态查询接口 

北京国富安电子商务安全认证有限公司 · POS 电子签名 SDK 使用指南
