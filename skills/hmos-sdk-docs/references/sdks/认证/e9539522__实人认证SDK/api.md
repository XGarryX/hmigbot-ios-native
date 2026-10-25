# 实人认证SDK鸿蒙端接入文档 

实人认证SDK 简介与推荐 安装 官方地址 demo下载地址 使用 

N. 初始化 

O. 活体检测 P. OCR识别 身份证双面识别 身份证单面识别 身份证认证 

## 实人认证SDK 

### 简介与推荐 

实人认证SDK,整合活体检测、身份证OCR、人像比对、身份证二要素比对四大要素。提高线上实人认 证用户体验和移动端平台效率。 

### 安装 

"dependencies": { 

"@wanshu/realauthsdk": 'file:../RealAuthSDK' 

} 

### 官方地址 

https://doc.chuanglan.com/document/VTYS7IQDCLTFL3N4 

1 

### demo下载地址 

ps:Demo快速运行,需要配置项目签名,在官方平台申请对应appid和appKey 

### 使用 

#### 1. 初始化 

- `import {CLConfigureUtil,CLOCRManager,CLRealPersonManager } from '@wanshu/r ealauthsdk'` 

- `//` 设置 `appId` 

- `CLConfigureUtil.setAppId(RS_AppKey)` 

- `//` 设置 `token,token` 的获取需要用户服务端对接平台服务端获取对应的 `token` , `demo` 中有本地获 取示例 

- `CLConfigureUtil.setToken("<#token#>")` 

#### 2. 活体检测 

需要'ohos.permission.CAMERA','ohos.permission.MICROPHONE'权限 

- `//` 添加延时防止获取不到 `surfaceId` 

- `setTimeout( ()=>{` 

- `//` 配置相机视图 `4 CLRealPersonManager.getInstance().initWithRecordView(this.context,th is.surfaceId)` 

- `//` 启动活体检测 

- `CLRealPersonManager.getInstance().startLiveDetectWithActionsHandler ((params:CLTypeParamObject,url?:string)=>{` 

- `7` 

- `},(status:CLStatus,params:ESObject)=>{` 

- `})` 

- `},200)` 

#### 3. OCR识别 

##### 身份证双面识别 

2 

`1 /** 2 *` 身份证 `OCR` 接口 `⚠` 先调用人像面(图片大小建议压缩为 `1M` 以内,超过会被 `SDK` 压缩) `3 * @param image:` 传入的身份证图片 `4 * @param isFront: true` :人像面; `false` :国徽面 `5 * @returns Promise<Object>` 返回结果: `6 * @example 7 *` 国徽面数据 `:{ 8 "expire_date"       = "` 失效日期 `"; 9 "issuing_authority" ="` 签发机关 `"; 10 "issuing_date"      = "` 签发日期 `"; 11 }; 12 *` 人像面数据: `{ 13 "address"    = "` 地址 `"; 14 "brith_day"  = "` 出生日期 `"; 15 "id_card_no" = "` 身份证号 `"; 16 "name"       = "` 姓名 `"; 17 "nation"     = "` ⺠族 `"; 18 "sex"        = "` 性别 `"; 19 }; 20 * */ 21 static async realPersonOCROfSignal(image: PixelMap, isFront: boolean): P romise<Object>` 

##### 身份证单面识别 

3 

`1 /** 2 *` 身份证 `OCR` 接口 识别人像面和国徽面(单图片大小建议压缩为 `1M` 以内,超过会被 `SDK` 压 缩) `3 * @param frontImagePixMap` 人像面照片 `4 * @param backImagePixMap` 国徽面照片 `5 * @returns Promise<Object>` 返回结果 `6 * @example { 7 back = { 8 "expire_date"       = "` 失效日期 `"; 9 "issuing_authority" = "` 签发机关 `"; 10 "issuing_date"      = "` 签发日期 `"; 11 }; 12 front =  { 13 "address"    = "` 地址 `"; 14 "brith_day"  = "` 出生日期 `"; 15 "id_card_no" = "` 身份证号 `"; 16 "name"       = "` 姓名 `"; 17 "nation"     = "` ⺠族 `"; 18 "sex"        = "` 性别 `"; 19 }; 20 * */ 21 static async realPersonOCR(frontImagePixMap: PixelMap, backImagePixMap: PixelMap): Promise<Object>` 

##### 身份证认证 

4 

`1 /** 2 *` 身份证认证 `3 * @param name` :姓名 `4 * @param idNumber` :身份证号码 `5 * @returns Promise<Object>` 返回结果: `6 * @example {` 一 `7 "order_no"  : "` 业务唯 流水号 `", 8 "city"      : "` 城市 `", 9 "country"   : "` 县区 `", 10 "gender"    : "` 性别: `1` :男、 `2` :女 `", 11 "age"       : "` 年龄 `", 12 "remark"    : "` 备注,例:一致 `", 13 "birthday"  : "` 生日,格式是 `yyyyMMdd", 14 "result"    : "` 返回结果: `01-` 认证一致 `(` 收费 `) 02-` 认证不一致 `(` 收费 `) 03-` 认证不确定(收费) `04-` 认证失败 `(` 不收费 `)", 15 "handle_time" : "` 查询时间 例: `2018-04-09 15:05:01", 16 "province"  : "` 省份 `" 17 } 18 * */ 19 static async realPersonDetect(name: string, idNumber: string): Promise<O bject>` 

5
