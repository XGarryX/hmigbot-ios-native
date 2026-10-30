# **API Sign SDK(HarmonyOS)接口文档** 

## **产品概述** 

API Sign SDK 用于为业务接口生成动态签名,帮助服务端识别合法请求,防止接口被恶意调用、参数篡改、脚本攻 击等风险。 

SDK 提供轻量级本地签名能力,接入简单,无需额外配置即可完成接口加签。 

## **环境要求** 

|**项目**|**要求**|
|---|---|
|HarmonyOS API|API 12及以上|
|支持架构|arm64-v8a、x86_64|

## **安装配置** 

### **安装 SDK** 

ohpm install @trustdecision/apisign 

### **添加依赖** 

在项目 oh-package.json5 中配置: 

{ "dependencies": { "@trustdecision/apisign": "1.0.1" } } 

## **接口说明** 

### **生成接口签名** 

#### **方法定义** 

TDAPISign.sign(path: string): TDAPISignResult 

#### **参数说明** 

|**参数**|**类型**|**必填**|**说明**|
|---|---|---|---|
|path|string|是|API请求路径,不包含域名和参数|

#### **返回值** 

export class TDAPISignResult { signature: string code: number message: string } 

|**字段**|**类型**|**说明**|
|---|---|---|
|signature|string|签名结果|
|code|number|状态码|
|message|string|状态描述|

## **调用示例** 

待保护接口: 

https://sg.apitd.net/de/v1?name=jacky&age=12 

##### 获取签名: 

import { TDAPISign } from '@trustdecision/apisign' 

const result = TDAPISign.sign('de/v1') 

if (result.code === 0) { const signature = result.signature 

// 将 signature 添加到请求头或请求参数中 } else { console.error(result.message) } 

## **状态检查** 

##### 签名成功判断: 

result.code === 0 

## **状态码说明** 

|**状态码**|**描述**|
|---|---|
|0|成功|
|2000|path参数为空|
|22xx|SDK内部异常|
|5001|SO文件加载失败|
