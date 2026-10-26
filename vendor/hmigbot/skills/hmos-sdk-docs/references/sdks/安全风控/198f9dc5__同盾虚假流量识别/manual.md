# **API Si n SDK(Harmon** **)使用指南 g yOS** 

## **产品简介** 

API Sign SDK 为客户端请求提供动态签名能力,用于增强接口安全性,降低接口被伪造、重放或恶意调用的风险。 适用于: 

- 用户登录 

- 注册认证 

- 支付交易 

- 营销活动 风控验证 

- 业务敏感接口 

## **快速开始** 

### **第一步:安装 SDK** 

ohpm install @trustdecision/apisign 

### **第二步:配置依赖** 

{ "dependencies": { "@trustdecision/apisign": "1.0.1" } } 

### **第三步:生成签名** 

import { TDAPISign } from '@trustdecision/apisign' 

const signResult = TDAPISign.sign('de/v1') 

### **第四步:携带签名发起请求** 

if (signResult.code === 0) { const signature = signResult.signature 

// 示例 request.header['x-td-sign'] = signature } 

## **功能操作指南** 

### **获取接口签名** 

const result = TDAPISign.sign('de/v1') 

#### 成功时: 

result.code === 0 

#### 获取签名: 

const sign = result.signature 

#### 异常时: 

console.error(result.code) console.error(result.message) 

## **常见问题** 

### **: Q1 path 应该传什么?** 

传接口路径即可,不需要包含域名和请求参数。 

正确示例: 

TDAPISign.sign('de/v1') 

#### 错误示例: 

TDAPISign.sign('https://sg.apitd.net/de/v1') TDAPISign.sign('de/v1?name=test') 

### **Q2:签名失败是否影响业务?** 

#### 不会。 

当 SDK 返回非 0 状态码时,建议记录日志并继续业务流程,可根据业务需求决定是否使用空签名发起请求。 

### **Q3:签名需要缓存吗?** 

不需要。 

建议每次请求前实时生成签名。 

## **故障排除** 

### **path 为空** 

现象: 

code = 2000 

处理方式: 

检查调用时是否正确传入接口路径。 

### **SO 文件加载失败** 

现象: 

code = 5001 

处理方式: 

检查应用是否包含当前设备架构对应的 SO 文件。 

支持架构: 

arm64-v8a x86_64 

### **SDK 内部异常** 

现象: 

code = 22xx 

#### 处理方式: 

1. 升级至最新 SDK 版本。 

2. 检查运行环境是否符合要求。 

3. 联系 TrustDecision 技术支持协助排查。 

## **最佳实践** 

每次接口请求前生成最新签名。 

- 仅传入接口路径进行加签。 

- 服务端同步校验签名有效性。 

对登录、支付、营销等关键接口启用签名保护。
