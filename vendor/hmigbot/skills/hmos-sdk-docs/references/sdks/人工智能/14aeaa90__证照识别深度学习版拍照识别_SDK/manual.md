# 证照识别深度学习版拍照识别 **SDK** 集成使用指南 

# 一、概述 

### **1.1** 产品简介 

证照识别深度学习版拍照识别 SDK 为 HarmonyOS 应用提供专业 的卡证识别能力,基于深度学习算法,支持各类证照的文字检测、识 别与提取。 

### **1.2** 主要功能 

拍照识别:调用相机拍摄证照并进行识别 

选图识别:从相册选择图片进行识别 

质量检测:检测图像质量,识别复印件、翻拍、模糊、光斑、完整性 等问题 

预览识别:实时预览并自动识别证照 

### **1.3** 支持证照类型 

证照类型说明 

身份证 支持正反面识别 银行卡 支持银行卡号识别 营业执照支持营业执照信息识别 驾驶证 支持驾驶证信息识别 行驶证 支持行驶证信息识别 香港身份证 支持香港身份证识别 港澳通行证 支持港澳通行证识别 户口本 支持户口本信息识别 医学出生证明 支持医学出生证明识别 教师资格证 支持教师资格证识别 结婚证 支持结婚证识别 

台胞证回乡证 支持台胞证回乡证识别 香港/澳门入境小票支持入境小票识别 香港 BR 支持香港商业登记证识别 

# 二、环境要求 

项目 要求 

操作系统 HarmonyOS 

最低 API 版本 5.0 

开发工具 DevEco Studio 5.0 及以上 

开发语言 ArkTS / TypeScript 

# 三、快速集成 

### **3.1** 添加 **SDK** 文件 

将 SDK 包中的 hh_card_recognize.har 文件拷贝到项目的 libs 目录下。 

text 

项目根目录/ 

├── entry/ │ ├── libs/ │ │ └── hh_card_recognize.har // SDK 文件 │ └── src/ │ └── main/ │ ├── module.json5 │ └── resources/ │ └── rawfile/ │ └──模型文件存放目录 

### **3.2** 配置依赖 

在 entry 目录下的 oh-package.json5 文件中添加依赖: 

json 

{ 

"dependencies": { 

"library": "file:./libs/hh_card_recognize.har" 

} 

} 

执行同步操作: 

bash 

ohpm install 

### **3.3** 拷贝模型文件 

将以下模型文件拷贝到 entry/src/main/resources/rawfile/ 目录下: 

必须拷贝的模型文件: 

文件名 说明 

kv_mnn_det.data 切边区域检测模型 

mnn3d1_mobile_202300410_2.5.22.data 全文识别模型文件 可选模型文件: 

文件名 说明 

kv_qualityinspect.data 质量检测模型文件(质检功能需要) kv_bank_card.data + BIN_TABLE.csv 银行卡识别模型(银行卡识 别需要) 

kv_driver_license.data 驾驶证识别模型(驾驶证识别需要) kv_vehicle_license.data 行驶证识别模型(行驶证识别需要) kv_hongkong_entry_ticket.data 香港入境小票识别模型 kv_macau_entry_ticket.data 澳门入境小票识别模型 kv_hongkong_br.data 香港 BR 识别模型 kv_medical_birth_certificate.data 医学出生证明识别模型 kv_guang_da_bank_household_register.data 户口本识别模型 kv_teacher_qualification_certificate.data教师资格证识别模型 kv_taiwan_hk_macao_compatriot.data 台胞证回乡证识别模型 kv_marriage_certificate.data 结婚证识别模型 face.xml 人脸检测模型(不需要头像可不拷贝) 

### **3.4** 配置权限 

在 entry/src/main/module.json5 文件中声明所需权限: 

json 

{ 

"module": { 

"requestPermissions": [ 

{ 

"name": "ohos.permission.INTERNET", 

"reason": "$string:internet_permission_reason", 

"usedScene": { 

"abilities": ["EntryAbility"], 

"when": "inuse" 

} 

}, 

{ 

"name": "ohos.permission.CAMERA", 

"reason": "$string:camera_permission_reason", 

"usedScene": { 

"abilities": ["EntryAbility"], 

"when": "inuse" 

} 

}, 

{ 

"name": "ohos.permission.STORE_PERSISTENT_DATA", 

"reason": "$string:store_permission_reason", 

"usedScene": { 

"abilities": ["EntryAbility"], 

"when": "always" 

} 

} 

] 

} 

} 

在 src/main/resources/base/element/string.json 中添加权限说明: 

json 

{ 

"string": [ 

{ 

"name": "internet_permission_reason", 

"value": "用于联网验证设备授权" 

}, 

{ 

"name": "camera_permission_reason", 

"value": "用于卡证拍照识别功能" 

}, 

{ 

"name": "store_permission_reason", 

"value": "用于存储 SDK 配置参数" 

} 

] 

} 

# 五、 **API** 接口说明 

## **5.1** 导入 **SDK** 

typescript 

import { VpuMoreCardPicPreKVTS } from 'library'; 

```arkts
import { common } from '@kit.AbilityKit'; 
```

import { image } from '@kit.ImageKit'; 

## **5.2** 初始化 **SDK** 

typescript 

/** 

## * 初始化 OCR 识别引擎 

- @param appkey 授权 APP_KEY,由盈五蓄授权提供 

- @param uiContext UIAbility 上下文(在启动类中调用时需要传入) 

- @returns Promise<number> 返回初始化结果码,0 表示成功 

*/ 

static async initICCardRecognizer(appkey: string, uiContext?: 

common.UIAbilityContext): Promise<number> 

调用示例: 

typescript 

import { VpuMoreCardPicPreKVTS } from 'library'; 

```arkts
import { common } from '@kit.AbilityKit'; 
```

## @Entry 

## @Component 

struct Index { 

## private context = getContext(this) as common.UIAbilityContext; 

## async aboutToAppear() { 

const appkey = "your_app_key"; // 替换为您的 APP_KEY 

const result = await 

VpuMoreCardPicPreKVTS.initICCardRecognizer(appkey, 

this.context); 

if (result === 0) { 

console.log('初始化成功'); 

## } else { 

console.error('初始化失败,错误码:', result); 

} 

} 

} 

## **5.3** 设置识别类型 

## typescript 

/** 

- 设置 OCR 识别类型 

- @param recognizerType 识别类型枚举 

*/ 

static setRecognizerType(recognizerType: RecognizerType): void 

/** 

- 获取当前 OCR 识别类型 

- @returns RecognizerType 当前识别类型 

*/ 

## static getRecognizerType(): RecognizerType 

识别类型枚举: 

typescript 

public enum RecognizerType { 

id_card, // 身份证 bank_card, // 银行卡 business_license, // 营业执照 vehicle_license, // 行驶证 driver_license, // 驾驶证 hongkong_id_card, // 香港身份证 

hk_mocao_taiwan_passport // 港澳台通行证 

} 

调用示例: 

## typescript 

// 设置识别类型为身份证 

VpuMoreCardPicPreKVTS.setRecognizerType(RecognizerType.id_ 

card); 

// 获取当前识别类型 

const 

= 

currentType 

VpuMoreCardPicPreKVTS.getRecognizerType(); 

## **5.4** 图片路径识别 

### **5.4.1 Promise** 方式 

typescript 

/** 

- 通过图片路径进行识别 

- @param imgPath 识别图片路径 

- @param rootPath 识别结果保存路径 

- @param expand_pix 切图外扩边距(像素) 

- @returns Promise<string> 返回识别结果 JSON 字符串 

*/ 

static async recognizeCard(imgPath: string, rootPath: string, expand_pix: number): Promise<string> 

### **5.4.2 Callback** 方式 

typescript 

/** 

- 通过图片路径进行识别(回调方式) 

- @param imgPath 识别图片路径 

- @param rootPath 识别结果保存路径 

- @param expand_pix 切图外扩边距(像素) 

- @param success 识别成功回调 

- @param error 识别失败回调 

*/ 

## static recognizeCardCallback( 

imgPath: string, 

rootPath: string, 

expand_pix: number, 

success: (result: string) => void, 

error: (code: number, msg: string) => void 

): void 

调用示例: 

typescript 

// Promise 方式 

## async recognizeImage(imgPath: string) { 

try { 

const rootPath = getContext().filesDir; 

const expand_pix = 0; 

const result = await 

VpuMoreCardPicPreKVTS.recognizeCard(imgPath, rootPath, 

expand_pix); 

console.log('识别结果:', result); 

return JSON.parse(result); 

} catch (error) { 

console.error('识别失败:', error); 

} 

} 

// Callback 方式 

VpuMoreCardPicPreKVTS.recognizeCardCallback( 

imgPath, 

rootPath, 

expand_pix, 

(result) => { 

console.log('识别成功:', result); 

}, 

(code, msg) => { 

console.error(`识别失败:${code} - ${msg}`); 

} 

); 

## **5.5 PixelMap** 识别 

### **5.5.1 Promise** 方式 

typescript 

/** 

- 通过 PixelMap 进行识别 

- @param pixelMap 需要识别的图片 PixelMap 

- @param rootPath 识别结果保存路径 

- @param expand_pix 切图外扩边距(像素) 

- @param enableQualityInspect 是否开启质量检测,默认 false 

- @returns Promise<string> 返回识别结果 JSON 字符串 

*/ 

static async recognizeCardPixelMap( 

pixelMap: image.PixelMap, 

rootPath: string, 

expand_pix: number, 

enableQualityInspect: boolean = false 

- ): Promise<string> 

### **5.5.2 Callback** 方式 

typescript 

/** 

- 通过 PixelMap 进行识别(回调方式) 

- @param pixelMap 需要识别的图片 PixelMap 

- @param rootPath 识别结果保存路径 

- @param expand_pix 切图外扩边距(像素) 

- @param enableQualityInspect 是否开启质量检测 

- @param success 识别成功回调 

- @param error 识别失败回调 

*/ 

static recognizeCardPixelMapCallback( 

pixelMap: image.PixelMap, 

rootPath: string, 

expand_pix: number, 

enableQualityInspect: boolean, 

success: (result: string) => void, 

error: (code: number, msg: string) => void 

): void 

## **5.6** 预览识别 

### **5.6.1 Promise** 方式 

typescript 

/** 

- 通过 YUV 预览帧进行识别 

- @param yuv 预览帧 YUV 数据 

- @param width 预览帧宽度 

- @param height 预览帧高度 

- @param rootPath 识别结果保存路径 

- @param expand_pix 切图外扩边距(像素) 

- @param enableQualityInspect 是否开启质量检测,默认 false 

- @returns Promise<string> 返回识别结果 JSON 字符串 

*/ 

static async recognizeCardYUV( 

yuv: ArrayBuffer, 

width: number, 

height: number, 

rootPath: string, 

expand_pix: number, 

enableQualityInspect: boolean = false 

- ): Promise<string> 

### **5.6.2 Callback** 方式 

typescript 

/** 

- 通过 YUV 预览帧进行识别(回调方式) 

- @param yuv 预览帧 YUV 数据 

- @param width 预览帧宽度 

- @param height 预览帧高度 

- @param rootPath 识别结果保存路径 

- @param expand_pix 切图外扩边距(像素) 

- @param enableQualityInspect 是否开启质量检测 

- @param success 识别成功回调 

- @param error 识别失败回调 

*/ 

static recognizeCardYUVCallback( 

yuv: ArrayBuffer, 

width: number, 

height: number, 

rootPath: string, 

expand_pix: number, 

enableQualityInspect: boolean, 

success: (result: string) => void, 

error: (code: number, msg: string) => void 

): void 

## **5.7** 质量检测接口 

### **5.7.1** 设置质检阈值 

typescript 

/** 

- 设置质量检测判断阈值 

- @param photocopyThreshold 复印件检测阈值,默认 0.5 

- @param screenRemarkThreshold 屏幕翻拍检测阈值,默认 0.5 

- @param lightSpotThreshold 光斑检测阈值,默认 0.5 

- @param blurryThreshold 模糊检测阈值,默认 0.5 

- @param unIntegrityThreshold 完整性缺失检测阈值,默认 0.5 

- @returns number 返回 0 表示设置成功 

*/ 

static setQualityInspectionThreshold( 

photocopyThreshold: number = 0.5, 

screenRemarkThreshold: number = 0.5, 

lightSpotThreshold: number = 0.5, 

blurryThreshold: number = 0.5, 

unIntegrityThreshold: number = 0.5 

): number 

说明:可能性大于阈值时,判定为存在该质量问题。 

### **5.7.2** 预览帧质量检测 

typescript 

/** 

- 获取预览帧的质量检测信息 

- @param yuv 预览帧 YUV 数据 

- @param width 预览帧宽度 

- @param height 预览帧高度 

- @param expand_pix 切图外扩边距 

- @returns Promise<string> 返回质量检测结果 JSON 字符串 

*/ 

static async qualityInspectYUV( 

yuv: ArrayBuffer, 

width: number, 

height: number, 

expand_pix: number 

- ): Promise<string> 

### **5.7.3** 边框检测 

typescript 

/** 

- 检测预览帧边框 

- @param yuv 预览帧 YUV 数据 

- @param width 预览帧宽度 

- @param height 预览帧高度 

- @param border 边框四个点坐标数组 

*/ 

static detectBorderYUV( 

yuv: ArrayBuffer, 

width: number, 

height: number, 

border: Array<number> 

- ): void 

## **5.8** 其他接口 

### **5.8.1** 获取版本号 

typescript 

/** 

- 获取 SDK 版本号 

- @returns string SDK 版本号 

*/ 

## static getVersion(): string 

### **5.8.2** 释放模型资源 

typescript 

/** 

- 释放模型资源 

*/ 

static releaseMemory(): void 

调用示例: 

typescript 

aboutToDisappear() { 

## VpuMoreCardPicPreKVTS.releaseMemory(); 

} 

# 六、错误码说明 

initICCardRecognizer() 函数返回值说明: 

## 返回值 说明 解决方法 

- 0 初始化成功 

- 101 包名错误检查工程包名是否与授权绑定的包名一致 

- 102 appKey 错误检查传入的 appKey 是否与授权 APP_KEY 一致 

- 103 超过时间限制 授权已到期,请联系盈五蓄技术支持 

- 104 达到设备上限 设备数量超限,请联系盈五蓄技术支持 

- 201 签名错误检查 MD5 签名是否与授权绑定的签名一致 

- 202 其他错误将错误日志发给盈五蓄技术支持 

- 203 服务器错误 将错误日志发给盈五蓄技术支持 

- 204 网络错误检查网络连接是否畅通 

- 205 包名/签名都不匹配检查包名和签名是否与授权信息一致 

- 302 使用了未授权 SDK 请联系盈五蓄技术支持新增 SDK 授权 303 当前 key 是旧版授权 key APP_KEY 需要包含 newAuth 标 

## 识 

- 304 子模块授权不支持 请联系盈五蓄技术支持新增授权子模块 309 模型文件加载错误 检查模型文件是否拷贝成功 

# 七、识别结果说明 

## **7.1** 身份证识别结果 

json 

{ 

"cropImagePath": "/data/storage/.../cropImagePath.jpg", 

"originalImagePath": "/data/storage/.../originalImagePath.jpg", 

"type": "id_card", 

"image_angle": 0, 

"rotated_image_width": 500, 

"rotated_image_height": 308, 

"is_front": 1, 

"quality_inspect": { 

"photocopy": { "key": false, "score": 0.001 }, 

"screen_remark": { "key": true, "score": 0.998 }, 

"light_spot": { "key": false, "score": 0.035 }, 

"blurry": { "key": false, "score": 0.491 }, 

"un_integrity": { "key": false, "score": 0.453 }, 

"ret": 1 

}, "item_list": [ 

{ "key": "name", "description": " 姓名 ", "value": " 韦小宝 ", 

"confidence": 1.0 }, 

{ "key": "sex", "description": " 性别 ", "value": " 男 ", "confidence": 1.0 }, 

{ "key": "nationality", "description": " 民族 ", "value": " 汉 ", "confidence": 1.0 }, 

{ "key": "birth", "description": "出生", "value": "1654 年 12 月 20 日", "confidence": 1.0 }, 

{ "key": "address", "description": "地址", "value": "北京市东城 区景山前街 4 号紫禁城敬事房", "confidence": 1.0 }, 

{ "key": "id_number", "description": " 身份证号码 ", "value": "11204416541220243X", "confidence": 1.0 }, 

{ "key": "validate_date", "description": " 有效期限 ", "value": "" }, 

{ "key": "issue_authority", "description": "签发机构", "value": "" }, 

{ "key": "id_card_type", "description": "身份证类别", "value": " 身份证信息面" }, 

{ "key": "avatar_path", "description": " 头像切图 ", "value": "/data/storage/.../avatarPath.jpg" }, 

{ "key": "id_number_path", "description": " 身份证号切图 ", "value": "/data/storage/.../idNumberPath.jpg" } 

] 

} 

字段说明: 

外层字段说明 

cropImagePath 切图路径 

originalImagePath 原图路径 

type 证件类型 

is_front 是否头像面(1:头像面, 2:国徽面, 3:临时, 0:其他) quality_inspect 质检结果 

质检结果字段: 

字段 说明 

photocopy 疑似复印件 

screen_remark 疑似屏幕翻拍 

light_spot 疑似光斑 

blurry 疑似模糊 

un_integrity 疑似完整性缺失 

## **7.2** 银行卡识别结果 

json 

{ 

"cropImagePath": "/data/storage/.../cropImagePath.jpg", 

"originalImagePath": "/data/storage/.../originalImagePath.jpg", "type": "other", 

"quality_inspect": {}, 

"item_list": [ 

{ "key": "card_number", "description": " 银行卡号 ", "value": "6217****1234", "confidence": 0.99 }, 

{ "key": "card_type", "description": "卡片类型", "value": "借记 卡", "confidence": 0.95 }, 

{ "key": "card_issuer", "description": "发卡机构", "value": "中 国银行", "confidence": 0.98 }, 

{ "key": "card_issuer_code", "description": " 发卡机构号 ", "value": "104", "confidence": 0.92 }, 

{ "key": "name_of_business", "description": "持卡人", "value": "张三", "confidence": 0.96 }, 

{ "key": "validate", "description": "有效日期", "value": "12/25", "confidence": 0.94 }, 

{ "key": "bank_number_path", "description": "银行卡号切图", "value": "/data/storage/.../bankNumberPath.jpg" } 

] 

} 

# 八、完整示例代码 

typescript 

import { VpuMoreCardPicPreKVTS, RecognizerType } from 'library'; 

```arkts
import { common } from '@kit.AbilityKit'; 
import { camera } from '@kit.CameraKit'; 
import { image } from '@kit.ImageKit'; 
import { BusinessError } from '@kit.BasicServicesKit'; 
```

@Entry 

@Component 

struct OcrDemoPage { 

@State recognitionResult: string = ''; 

private context = getContext(this) as common.UIAbilityContext; private rootPath: string = this.context.filesDir; 

async aboutToAppear() { 

// 1. 初始化 SDK 

const appkey = "your_app_key"; 

const initResult = await 

VpuMoreCardPicPreKVTS.initICCardRecognizer(appkey, 

this.context); 

if (initResult !== 0) { 

this.recognitionResult = `初始化失败,错误码:${initResult}`; 

return; 

} 

- // 2. 设置识别类型 

VpuMoreCardPicPreKVTS.setRecognizerType(RecognizerType.id_ 

card); 

- // 3. 可选:设置质检阈值 

VpuMoreCardPicPreKVTS.setQualityInspectionThreshold(0.5, 

0.5, 0.5, 0.5, 0.5); 

console.log('SDK 版 本 : ', 

VpuMoreCardPicPreKVTS.getVersion()); 

} 

- // 拍照识别 

async startCameraRecognition() { 

try { 

// 调用相机拍照(此处简化,实际需实现相机拍照逻辑) const imgPath = await this.takePhoto(); 

// 调用识别接口 

const expand_pix = 0; 

const result = await 

VpuMoreCardPicPreKVTS.recognizeCard(imgPath, this.rootPath, expand_pix); 

this.recognitionResult = result; 

} catch (error) { 

const err = error as BusinessError; 

this.recognitionResult = `识别失败:${err.message}`; 

} 

} 

// 选图识别 

async startGalleryRecognition() { 

try { 

// 从相册选择图片(此处简化,实际需实现相册选择逻辑) const imgPath = await this.selectFromGallery(); 

// 调用识别接口 

const expand_pix = 0; const result = await 

VpuMoreCardPicPreKVTS.recognizeCard(imgPath, this.rootPath, expand_pix); 

this.recognitionResult = result; 

} catch (error) { 

const err = error as BusinessError; 

this.recognitionResult = `识别失败:${err.message}`; 

} 

} 

// 质量检测 

async checkImageQuality(imgPath: string) { 

try { 

const result = await VpuMoreCardPicPreKVTS.recognizeCard(imgPath, this.rootPath, 

0); 

const parsed = JSON.parse(result); 

const quality = parsed.quality_inspect; 

if (quality) { 

const issues = []; 

if (quality.photocopy?.key) issues.push('复印件'); if (quality.screen_remark?.key) issues.push('屏幕翻拍'); 

if (quality.light_spot?.key) issues.push('光斑'); 

if (quality.blurry?.key) issues.push('模糊'); 

if (quality.un_integrity?.key) issues.push('完整性缺失'); 

if (issues.length > 0) { 

console.log('质量问题:', issues.join(', ')); 

} else { 

console.log('图像质量合格'); } 

} 

} catch (error) { console.error('质量检测失败:', error); 

} 

} 

aboutToDisappear() { 

// 释放模型资源 

VpuMoreCardPicPreKVTS.releaseMemory(); 

} 

## build() { 

Column({ space: 20 }) { 

Text('证照识别 SDK Demo') 

.fontSize(24) 

.fontWeight(FontWeight.Bold) 

Button('拍照识别') 

.onClick(() => this.startCameraRecognition()) 

## Button('选图识别') 

.onClick(() => this.startGalleryRecognition()) 

Text('识别结果:') 

.fontSize(16) 

.fontWeight(FontWeight.Bold) 

## Scroll() { 

Text(this.recognitionResult) 

.fontSize(12) 

.padding(10) 

.backgroundColor('#F5F5F5') 

.width('100%') 

} 

.height(400) 

} 

.padding(20) .width('100%') 

.height('100%') 

} 

} 

# 九、常见问题 

## **9.1** 初始化失败,返回错误码 **309** 

原因:模型文件加载错误 

解决方法: 

检查模型文件是否已拷贝到 src/main/resources/rawfile/ 目录 

确 认 必 须 的 模 型 文 件 ( kv_mnn_det.data 、 mnn3d1_mobile_202300410_2.5.22.data)已正确放置 

## **9.2** 初始化失败,返回错误码 **101/201/205** 

原因:包名或签名与授权信息不匹配 

解决方法: 

检查工程中的包名是否与授权绑定的包名一致 检查 MD5 签名是否与授权绑定的签名一致 

## **9.3** 识别结果为空或不准确 

可能原因: 

图像质量不佳(模糊、光线不足、遮挡) 

识别类型设置错误 

未拷贝对应的证照识别模型文件 

解决方法: 

使用质量检测功能筛选合格图像 

确认 setRecognizerType() 设置了正确的识别类型 

确认已拷贝对应证照的识别模型文件 

## **9.4** 相机无法打开 

解决方法: 

确认已在 module.json5 中声明相机权限 

检查用户是否已授予相机权限 

确认设备摄像头可用 

# 十、技术支持 

## **10.1** 联系方式 

项目 信息 

公司名称上海盈五蓄科技股份有限公司 

客服电话 021-26022775 

客服邮箱 support@textin.com 

官方网站 https://www.textin.com 

## **10.2** 问题反馈 

如遇到技术问题,请提供以下信息: 

SDK 版本号 

设备型号和系统版本 完整的错误日志
