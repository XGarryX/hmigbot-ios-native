证照识别深度学习版鸿蒙Next SDK 集成说明文档 v7.3.1_2025.10.17 

## 目录 

|一、SDK简介说明.....................................................................................................................1|
|---|
|二、支持的系统和硬件版本....................................................................................................... 1|
|三、SDK集成配置说明..............................................................................................................1|
|四、SDK调用流程图................................................................................................................. 4|
|五、SDK调用API接口说明........................................................................................................ 4|
|六、Appkey Code说明............................................................................................................. 6|
|七、识别结果说明..................................................................................................................... 7|
|八、维护与故障.......................................................................................................................19|
|九、信息与权限.......................................................................................................................20|
|十、SDK合规使用说明............................................................................................................20|
|十一、版本更新记录................................................................................................................24|

# 一、 **SDK** 简介说明 

通过上海盈五蓄数据科技有限公司全球领先的OCR 技术,对图片进行OCR 文字识别,返回 图片上的每个段落,每行,每个词组,每个文字的属性等信息,可以省去用户手动录入的 过程,给用户带来极大的便利。为了给用户提供本地OCR 文字识别的体验,合合信息支持 提供Android 与iOS 系统和鸿蒙系统的OCR 文字识别SDK。用户只需在APP 中集成合合信 息提供的OCR 文字识别SDK,就可以给用户提供本地OCR 文字识别功能。本文档主要介绍 OCR 鸿蒙SDK的安装和使用。在使用本文档前,您需要先了解Optical Character Recognition(OCR) 的基础知识,并已经开通了OCR服务. sdk信息如下: ohpm地址:https://ohpm.openharm 

ony.cn/#/cn/detail/hh_card_recognize 

dependencies": ( SDK包名:hh_card_recognize 版本号:7.3.1 MD5值:70bf89e64c78824e4de39a151221609d ) 隐私政策链接:https://www.textin.com/privacy 合规说明:如文中第十项 

# **二、支持的系统和硬件版本** 

- 鸿蒙:HarmonyOS NEXT Developer Preview1 

- 架构:x86_64 arm64-v8a armeabi-v7a(此处支持模拟器有客户需要模拟器模式下调试) 

# **三、SDK集成配置说明** 

功能列表 

type类型 

是否支持拍照选图 

是否支持预览 

|身份证|支持|支持|id_card|
|---|---|---|---|
|银行卡|支持|支持|bank_card|
|营业执照|支持|支持|business_license|
|行驶证|支持|支持|vehicle_license|
|驾驶证|支持|支持|driver_license|
|香港身份证|支持|支持|hongkong_id_card|
|港澳台通行证|支持|支持|hk_mocao_taiwan_p assport|
|外国人居住证|支持|支持|foreign_permantent_ resident_id_card|
|香港小票|支持|支持|hongkong_entry_tic ket|
|澳门小票|支持|支持|macau_entry_ticket|
|港澳通行证|支持|支持|hk_to_macau_card|
|护照|支持|支持|pass_port|
|医学出生证明|支持|支持|medical_birth_certif icate|
|社保卡|支持|支持|social_security_card|
|户口本|支持|支持|guang_da_bank_hou sehold_register|
|港澳台居民居住证|支持|支持|hkmctw_residence_ permit|
|教师资格证|支持|支持|teacher_qualificatio n_certificate|
|台胞证回乡证|支持|支持|taiwan_hk_macao_c ompatriot|
|结婚证|支持|支持|marriage_certificate|

#### SDK导入准备步骤如下 

#### **拷贝相关配置依赖文件** 

1. 将library.har 文件拷贝到项目工程libs文件夹下 

2. 安装library.har到项目在对应的目录的oh-package.json5文件里配置har文件安装路径: 

   - "dependencies": { "library": "file:./libs/library.har" } 

   - 如下图: 

#### 3. 拷贝需要对接的模型.data 文件到src/main/resources/rawfile文件目录下 

#### 1. kv_mnn_det.data **是切边区域检测模型** , **切边区域检测模型是必须拷贝的,其他证照 识别模型可根据需要识别的证照添加选择添加** ; 

2. mnn3d1_mobile_202300410_2.5.22.data 也是必要的全文文件需要导入的必须文件 

3. kv_qualityinspect.data 质量检测模型文件质检检测必须要导入的文件 

4. face.xml **是人脸检测模型文件(不需要头像可不拷贝** face.xml **)** ; 

5. kv_bank_card.data BIN_TABLE.csv **是银行卡识别模型,银行卡识别需要拷贝** 

#### **该模型文件** ; 

6. kv_driver_license.data **是驾驶证识别模型,驾驶证识别需要拷贝该模型文件** ; 

7. kv_vehicle_license.data **是行驶证识别模型,行驶证识别需要拷贝该模型文件** ; 

8. kv_hongkong_entry_ticket.data香港小票 

9. kv_macau_entry_ticket.data澳门小票 

10. kv_hongkong_br.data香港br 

11. kv_medical_birth_certificate.data医学出生证明 

12. kv_guang_da_bank_household_register.data 户口本 

13. kv_ teacher_qualification_certificate.data 教师资格证 

14. kv_taiwan_hk_macao_compatriot.data 台胞证回乡证 

15. kv_marriage_certificate.data 结婚证 

4. 配置项目权限在项目目录下如entry目录下的module.json5,申明权限目的、是否必须、调用 频率详情参考“九、信息与权限”章节内容。 

"requestPermissions": [ 

{ 

"name": "ohos.permission.INTERNET" 

}, 

{ 

"name": "ohos.permission.CAMERA" 

}, 

- { 

"name": "ohos.permission.STORE_PERSISTENT_DATA" 

} 

] 

# **四、SDK调用流程图** 

# **五、SDK调用API接口说明** 

1. 调用static async initICCardRecognizer(appkey: string): Promise<number>进行OCR识别初始 化,appKey根据第三方鸿蒙程序包名和签名信息生成的APP_KEY,由合合信息授权提供, **识 别前必须先调用授权校验** ;特别注意:如果是在启动类里调用需要自己获取context并传入 

static async initICCardRecognizer(appkey: string,_uiContext:common.UIAbilityContext = context ): Promise<number> 

2. 调用setRecognizerType(RecognizerType recognizerType) 设置OCR识别类型,默认识别身 份证,修改识别类型需在识别前设置,需要拷贝对应证照识别的模型文件到集成项目的assets 目录下; 

public enum RecognizerType { 

id_card, bank_card, business_license, vehicle_license, driver_license, hongkong_id_card, hk_mocao_taiwan_passport } 

调用示例: 

VpuMoreCardPicPreKVTS.setRecognizerType(RecognizerType.id_card); 

3. 调用 getRecognizerType() 获取OCR识别类型; 

4. 传入路径识别证件: 

   - a) 调用recognizeCard(imgPath: string, rootPath: string, expand_pix: number)进行识别, picPath识别图片路径 

rootPath识别保存需要的文件夹路径 

expand_pix设置外扩的大小 

- b) 调用recognizeCardCallback(imgPath: string, rootPath: string, expand_pix: 

number,success:(result:string)=>void,error:(code:number,msg:string)=>void)进行识别 

picPath识别图片路径 

rootPath识别保存需要的文件夹路径 

expand_pix设置外扩的大小 success为识别成功的回调 

error:(code:number,msg:string)为识别失败回调 

5. 传入pixelmap识别 

   - a) 调用recognizeCardPixelMap(pixelMap: image.PixelMap, rootPath: string, expand_pix: number,enableQualityInspect: boolean = false) 

pixelMap:需要识别的图片 

rootPath识别保存需要的文件夹路径 

expand_pix设置外扩的大小 

enableQualityInspect为是否打开质检,默认关闭 

- b) 调用recognizeCardPixelMapCallback(pixelMap: image.PixelMap, rootPath: string, expand_pix: number,enableQualityInspect: 

boolean,success:(result:string)=>void,error:(code:number,msg:string)=>void)进行识别 

pixelMap:需要识别的图片 

rootPath识别保存需要的文件夹路径 

expand_pix设置外扩的大小 enableQualityInspect为是否打开质检,默认关闭 

success为成功的回调 

error:(code:number,msg:string)为失败回调 

6. 预览识别: 

   - a) recognizeCardYUV(yuv: ArrayBuffer, width: number, height: number, rootPath: string, expand_pix: number,enableQualityInspect: boolean = false):Promise<string>; 

yuv:为获取的预览帧 

width为预览帧的宽 

height为预览帧的高 rootPath为图片保存路径 expand_pix为切图外扩边距 

enableQualityInspect为是否开启质检 

- b) recognizeCardYUVCallback(yuv: ArrayBuffer, width: number, height: number, rootPath: string, expand_pix: number, enableQualityInspect: boolean,success:(result:string)=>void,error:(code:number,msg:string)=>void) 

yuv:为获取的预览帧 

width为预览帧的宽 height为预览帧的高 rootPath为图片保存路径 expand_pix为切图外扩边距 enableQualityInspect为是否开启质检 success为成功的回调 error:(code:number,msg:string)为失败回调 

7. 调用setQualityInspectionThreshold(photocopyThreshold: number = 

   - 0.5,screenRemarkThreshold: number = 0.5,lightSpotThreshold: number = 

   - 0.5,blurryThreshold: number = 0.5,unIntegrityThreshold: number = 0.5): number设置质检判 

断阈值,默认为0.5,即:,返回的可能性大于0.5,则为true,反之为false。方法返回值为0, 则设置成功。 

8. 调用detectBorderYUV(yuv: ArrayBuffer, width: number, height: number, border: Array<number>)进行预览识别 

yuv预览数据 

width预览数据宽 height预览数据高 border预览四个点的坐标; 

9. 获取预览质量检测信息 static async qualityInspectYUV(yuv: ArrayBuffer, width: number, height: number,expand_pix: number): Promise<string> 

10. 调用getVersion()返回SDK版本。 

11. releaseMemory() 释放模型资源,一般在aboutToDisappear()时进行模型释放。 

# **六、Appkey Code** 说明 

#### initICCardRecognizer ()函数返回int值说明如下: 

|int返回值|说明|
|---|---|
|0|初始化成功|
|101|原因:包名错误, 授权APP_KEY与绑定的APP包名不匹配;|
||解决方法:请检查工程中的包名是否与提供给合合信息授权绑定 的包名一致。|
|102|原因:appKey错误, 传递的APP_KEY填写错误;|
||解决方法:请检查工程中传入的appKey是否与合合信息授权的|

||APP_KEY一致。|
|---|---|
|103|原因:超过时间限制, 授权的APP_KEY超出使用时间限制; 解决方法:授权到期,如需延长,请与合合信息技术支持联系。|
|104|原因:达到设备上限, 授权的APP_KEY使用设备数量达到限制; 解决方法:设备超限,请与合合信息技术支持联系新增设备的授 权。|
|201|原因:签名错误, 授权的APP_KEY与绑定的APP签名不匹配; 解决方法:请检查工程中的MD5签名是否与提供给合合信息授权 绑定的签名信息一致。|
|202|原因:其他错误, 其他未知错误,比如初始化有问题; 解决方法:请将具体日志发给合合技术支持,方便定位具体问题|
|203|原因:服务器错误, 第一次联网验证时,因服务器问题,没有验证 通过; 解决方法:将错误日志及重现流程反馈给合合信息技术支持。|
|204|原因:网络错误, 第一次联网验证时,没有网络连接,导致没有验 证通过; 解决方法:检查网络是否畅通,尝试打开4G网络是否可以正常运 行;如果在联网状态仍然报错,请将错误日志及重现流程反馈给 合合信息技术支持。|
|205|原因:包名/签名错误,授权的APP_KEY与绑定的APP包名和签 名都不匹配; 解决方法:请检查工程中的包名、MD5签名是否与提供给合合信 息授权绑定的包名、签名信息一致。|
|302|原因:使用了未授权sdk,授权的APP_KEY与SDK授权不匹配; 解决方法:请联系合合信息技术支持新增sdk授权。|
|303|原因:当前key是旧版授权key; 解决方法:APP_KEY判断是否包含newAuth|
|304|原因:子模块授权不支持; 解决方法:请与合合信息技术支持新增授权子模块。|
|309|原因:模型文件加载错误 解决方法:检查模型文件是否拷贝成功,参考SDK集成配置说明。|
|1001|原因:身份证识别时输入的图片类型不符 解决方法:更换正确的证件类型|

# **七、** 识别结果说明 

#### **1. 身份证:** 

{ 

"cropImagePath": "/data/storage/el2/base/haps/entry/files/cropIm agePath.jpg", "image_angle": 0, 

"item_list": [ 

{ 

||"confidence": 1.0, "description": "姓名",|
|---|---|
||"key": "name", "position": [ 96, 33, 164, 33, 164, 57, 96, 57 ], "value": "韦小宝"|
|}, {|"confidence": 1.0, "description": "性别",|
|}, {|"key": "sex", "position": [ 96, 76, 119, 76, 119, 99, 96, 99 ], "value": "男"|
||"confidence": 1.0, "description": "民族", "key": "nationality", "position": [ 192, 76, 216, 76,|

216, 99, 192, 99 ], "value": "汉" }, { "confidence": 1.0, "description": "出生", "key": "birth", "position": [ 93, 113, 261, 113, 261, 136, 93, 136 ], "value": "1654年12月20日" }, { "confidence": 1.0, "description": "地址", "key": "address", "position": [ 89, 153, 317, 153, 317, 209, 89, 209 ], "value": "北京市东城区景山前街4号紫禁城敬事房" }, { "confidence": 1.0, "description": "身份证号码", 

"key": "id_number", "position": [ 171, 255, 424, 255, 424, 275, 171, 275 ], "value": "11204416541220243X" }, { "description": "有效期限", "key": "validate_date", "position": [], "value": "" }, { "description": "签发机构", "key": "issue_authority", "position": [], "value": "" }, { 

"description": "身份证号码图像", "key": "id_number_image", "position": [], "value": "168,244,435,284" }, { 

"description": "头像", 

"key": "head_portrait", "position": [], "value": "296,0,465,234" 

}, { "confidence": 1.0, "description": "身份证类别", "key": "id_card_type", "position": [], 

"value": "身份证信息面" 

}, { 

"description": "头像切图", 

"key": "avatar_path", 

"value": "/data/storage/el2/base/haps/entry/files/avatarPath.jpg" 

}, 

{ 

"description": "身份证号切图", 

"key": "id_number_path", 

"value": "/data/storage/el2/base/haps/entry/files/idNumberPath.jpg" 

}, 

{ 

"description": "是否头像面", 

"key": "is_front", 

"value": "1" 

} 

], 

"originalImagePath": "/data/storage/el2/base/haps/entry/files/originalImagePath.jpg", "polylinesPath": "", 

"rotated_image_height": 308, 

"rotated_image_width": 500, 

"type": "id_card", 

{ 

"cropImagePath": "/data/storage/el2/base/haps/entry/files/cropIm agePath.jpg", "image_angle": 0, 

"item_list": [ 

{ 

"confidence": 1.0, 

"description": "姓名", "key": "name", 

"position": [ 

96, 33, 164, 33, 164, 57, 96, 57 ], "value": "韦小宝" 

}, 

{ 

"confidence": 1.0, "description": "性别", "key": "sex", "position": [ 

96, 76, 119, 76, 119, 99, 96, 99 

], 

"value": "男" 

}, 

{ 

"confidence": 1.0, 

"description": "民族", "key": "nationality", "position": [ 192, 76, 216, 76, 216, 99, 192, 99 ], "value": "汉" }, { "confidence": 1.0, "description": "出生", "key": "birth", "position": [ 93, 113, 261, 113, 

261, 136, 93, 

136 

], 

"value": "1654年12月20日" 

}, { "confidence": 1.0, 

"description": "地址", "key": "address", 

"position": [ 

89, 153, 317, 153, 317, 209, 89, 209 

], 

"value": "北京市东城区景山前街4号紫禁城敬事房" 

}, { 

"confidence": 1.0, 

"description": "身份证号码", 

"key": "id_number", 

"position": [ 

171, 255, 424, 255, 424, 275, 171, 275 ], "value": "11204416541220243X" }, { "description": "有效期限", "key": "validate_date", 

"position": [], 

"value": "" 

}, { 

"description": "签发机构", "key": "issue_authority", 

"position": [], 

"value": "" 

}, { 

"description": "身份证号码图像", 

"key": "id_number_image", "position": [], 

"value": "168,244,435,284" 

}, { 

"description": "头像", 

"key": "head_portrait", "position": [], 

"value": "296,0,465,234" 

}, 

{ 

"confidence": 1.0, 

"description": "身份证类别", 

"key": "id_card_type", 

"position": [], 

"value": "身份证信息面" 

}, 

{ 

"description": "头像切图", 

"key": "avatar_path", 

"value": "/data/storage/el2/base/haps/entry/files/avatarPath.jpg" 

}, { 

"description": "身份证号切图", 

"key": "id_number_path", 

"value": "/data/storage/el2/base/haps/entry/files/idNumberPath.jpg" 

}, 

{ 

"description": "是否头像面", 

"key": "is_front", 

"value": "1" 

} 

], 

"originalImagePath": 

"/data/storage/el2/base/haps/entry/files/originalImagePath.jpg", 

"polylinesPath": "", 

"rotated_image_height": 308, 

"rotated_image_width": 500, 

"type": "id_card", 

"quality_inspect": { 

"photocopy": { 

"key": false, 

"score": 0.0010406806832179427 

}, 

"screen_remark": { 

"key": true, 

"score": 0.9986193180084229 

}, 

"light_spot": { 

"key": false, 

"score": 0.03584058955311775 

}, 

"blurry": { 

"key": false, 

"score": 0.49114593863487244 

}, 

"un_integrity": { 

"key": false, 

"score": 0.4533633887767792 

}, 

"ret": 1 

} 

} 

|外层字段||
|---|---|
|cropImagePath|切图路径|
|originalImagePath|原图路径|
|type|类型|
|is_front|是否头像面1头像面2.国徽面3.临时0.其他|
|quality_inspect|质检结果|
|**item_list** 返回字段: avatar_path|头像路径|
|id_number_path|身份证号码路径|
|name|姓名|

|sex|性别|
|---|---|
|nationality|民族|
|birth|出生日期|
|id_number|身份证号码|
|address|地址|
|validate_date|有效期|
|issue_authority|签发机构|
|id_card_type|**身份证类别**(身份证信息面身份证国徽临时 身份证其他)可判断身份证正反面|

quality_inspect返回字段:key为结果,score为可能性(0 - 1) 

|photocopy|疑似复印件|
|---|---|
|screen_remark|疑似屏幕翻拍|
|light_spot|疑似光斑|
|blurry|疑似模糊|
|un_integrity|疑似完整性缺失|

#### **2.** 银行卡 **:** 

{ 

"cropImagePath": "/data/storage/el2/base/haps/entry/files/cropImagePath.jpg", "image_angle": 0, "item_list": [ { "description": "发卡机构", "key": "card_issuer", "position": [ 212, 1035, 2793, 1047, 2791, 1243, 212, 1233 ], 

"value": "兴业银行" }, { 

"description": "发卡机构号", "key": "card_issuer_code", "position": [ 212, 1035, 2793, 1047, 

2791, 1243, 212, 1233 

], "value": "03090000" }, { "description": "银行卡号", "key": "card_number", "position": [ 212, 1035, 2793, 1047, 2791, 1243, 212, 1233 ], 

"value": "622908 363069 818488" }, { 

"description": "卡片类型", "key": "card_type", "position": [ 212, 1035, 2793, 1047, 2791, 1243, 212, 1233 ], "value": "借记卡" }, { "description": "持卡人", "key": "name_of_business", "position": [ 0, 

0, 0, 0, 

0, 0, 0, 0 

], 

"value": "" 

}, 

{ 

"description": "有效日期", 

"key": "validate", 

"position": [ 

1343, 1385, 1783, 1383, 1784, 1511, 1343, 1514 

], 

"value": "10/28" 

}, 

{ 

"description": "银行卡号切图", 

"key": "bank_number_path", 

"value": "/data/storage/el2/base/haps/entry/files/bankNumberPath.jpg" 

} 

], 

"originalImagePath": "/data/storage/el2/base/haps/entry/files/originalImagePath.jpg", "polylinesPath": "", 

"rotated_image_height": 1876, 

"rotated_image_width": 2976, 

"type": "bank_card", 

"quality_inspect": { 

"photocopy": { 

"key": false, 

"score": 0.0010406806832179427 

}, 

"screen_remark": { 

"key": true, 

"score": 0.9986193180084229 

}, 

"light_spot": { 

"key": false, 

"score": 0.03584058955311775 

}, 

"blurry": { "key": false, "score": 0.49114593863487244 

}, "un_integrity": { "key": false, "score": 0.4533633887767792 }, "ret": 1 } } 

字段含义说明:每一个字段代表的含义都在 description 这个字段里不清楚字段的含义可 以参照这个字段的描述信息 

外层字段: 

|cropImagePath|切图路径|
|---|---|
|originalImagePath|原图路径|
|type|证件类型(other)|
|quality_inspect|质检结果|

#### **item_list** 返回字段: 

|card_issuer|发卡机构|
|---|---|
|card_issuer_code|发卡机构号|
|card_number|银行卡号|
|card_type|卡片类型|
|name_of_business|持卡人|
|validate|有效日期|
|bank_number_path|银行卡号切图|

# **八、** 维护与故障 

#### 1. SDK维护说明: 

对SDK的调用,请按照SDK文档说明进行开发与调用。集成SDK时,验证SDK提供的功能 是否都可 以正常工作。 

2.SDK故障排除说明: 

通过提供的demo,对清晰的OCR图片进行识别,测试返回的识别结果是否正确。如果可以正确返回 识别结果,则说明SDK运行正常。 

如果不能返回识别结果或识别结果有错,请提供测试的图片与SDK log给我们分析: 

tsupport@intsig.net 

# 九、信息与权限 

|名称|类别|目的|是否必须|调用频率|
|---|---|---|---|---|
|UUID|信息|用于鸿蒙授权设备识别,基于设备 提供识别服务|是|首次启动时获取1 次 ,并缓存到本地|
|应用包名、签 名信息|信息|用于授权应用识别|是|首次启动时获取1 次|
|网络权限|权限|用于联网验证设备授权,离线授权 时可不授权|否|由开发者应用决定, 当您同意向开发者应 用授予该权限时开启|
|相机权限|权限|用于开发者通过预览识别、拍照 识别方式向您提供卡证文字识别 服务,仅使用选图识别方式时可 不授权。|否|由开发者应用决定, 当您同意向开发者应 用授予该权限时开启|
|存储权限|权限|用于开发者通过选图识别方式向 您提供卡证文字识别服务,仅使 用预览识别、拍照识别方式时可 不授权。|否|由开发者应用决定, 当您同意向开发者应 用授予该权限时开启|

# **十、SDK** 合规使用说明 

### 尊敬的开发者: 

感谢您使用Textln平台产品和服务。根据《个人信息保护法》、《数据安全法》、《 网络安全法》等法律法规,在提供网络产品服务时需遵循合法、正当、最小必要原则 ,不得违法违规收集使用个人信息。为保障最终用户的权利,特制定以下SDK合规使 用说明,协助开发者在使用Textln平台SDK的过程中更好地落实用户个人信息保护相 关要求,不断提升个人信息保护水平,请开发者仔细阅读并参考执行落实。 

### **一、SDK隐私政策披露要求与示例** 

开发者应确保集成Textln平台相关SDK的产品应用有单独的《隐私政策》,开发者应 用的《隐私政策》“第三方信息数据共享清单”或“第三方SDK情况说明”或“第三方SDK 列表”条款部分应参考Textln平台隐私政策中明示的相关SDK收集使用个人信息的目的 、方式和范围,条款内容可参考示例如下,并且在用户首次打开开发者应用时弹出《 隐私政策》并取得最终用户同意。 

**披露示例(仅供参考,请以实际合作情况为准):** 

|**SDK名称**|**第三方名称**|**使用目的**|**收集个人信息**|**权限使用**|**收集方式**|
|---|---|---|---|---|---|
|通用文字识 别深度学习 版拍照识别 SDK|上海合合信 息科技股份 有限公司|为了向用户 提供通用文 字识别服务|设备标识(A ndroidID 、 UDID)、应 用信息(应 用包名、签 名信息)|**Android:**网络 、相机、存 储权限 **iOS:**网络、相 机、相册权 限|SDK本机采 集|
|证照识别深 度学习版拍 照识别SDK|上海盈五蓄 数据科技有 限公司|为了向用户 提供卡证文 字识别服务|设备标识(**Android:** AndroidIDiO S :UDID 、 **HarmonyOS:**UUID )应用信息 (应用包名 、签名信息 )|**Android:**网络 、相机、存 储权限 **iOS:**网络、相 机、相册权 限 **HarmonyOS:** 网络、相机 、存储权限|SDK本机采 集|
|图像切边增 强+自动拍照 +pdf识别 SDK|上海合合信 息科技股份 有限公司|为了向用户 提供图像处 理服务|设备标识(A ndroidID 、 UDID 、 UUID )、应用信 息(应用包 名、签名信 息)|**Android:**网络 、相机、存 储权限 **iOS:**网络、相 机、相册权 限 **HarmonyOS:** 网络、相机 、存储权限|SDK本机采 集|

### **二、SDK业务功能调用时机** 

请务必在用户同意您App中的隐私政策后,在使用具体业务功能场景时再进行Textln 平台相关SDK的调用。用户同意隐私政策之前,您应避免动态申请涉及用户个人信息 的敏感设备权限、私自采集和上报个人信息。当您的App未向用户提供服务时,例如 App在后台运行时,请勿请求Textln平台相关SDK服务。 

### **三、最终用户同意方式的示例** 

App首次运行时进行隐私政策弹窗提醒,提醒弹窗中应包含隐私政策核心内容并附完 整版隐私政策链接,明示提醒最终用户阅读并选择是否同意隐私政策,并提供同意按 钮和拒绝同意的按钮,并由最终用户主动选择。 

## **四、最终用户行使权利说明** 

最终用户对其个人信息的处理享有知情、决定、查阅、复制、补充、更 正、撤回授权同意、删除、注销账号等权利。如开发者应用集成了Textln 平台相关SDK,开发者应根据相关法律法规为最终用户提供行使个人信息 

主体权利的路径或功能,需要配合的请及时联系,我们将与开发者协同 妥善解决最终用户的诉求。电话:021-26022775,邮箱: support@textin.com。 

# **十一、** 版本更新记录 

|上线日期|版本号|更新内容|变更人|
|---|---|---|---|
|2024.03.15|v1.0.1.20240320|1.新增集成文档|王俊|
|2024.04.12|v1.0.2.20240412|1.新增四个证件香港ID 澳门ID 护照港 澳通行证|王俊|
|2024.06.12|v1.0.7.20240612|1.新增香港小票|王俊|
|2024.07.16|v1.0.8.20240716|1.新增出生证明2.户口本3.社保卡4.驾驶 证5.行驶证6.银行卡新集成方式|王俊|
|2024.07.25|v1.0.9.20240725|1.鸿蒙NEXT0.0.31系统不再支持2.预览黑 屏优化|王俊|
|2024.08.26|v1.1.0.20240826|1. 鸿蒙NEXT0.0.36 2.预览闪退优化 3.新增银行卡卡号切图4.修改har文件包名 5.修复头像灰色|王俊|
|2024.10.14|v7.1.1.20241014|1. IDE升级5.0.3.900 2.修改SDK Version 3.Release版本出包4.新增港澳台居民居住证|王俊|
|2024.11.06|v7.1.3.20241106|1.新增是正反面返回字段2.Demo内预览新 增正反面参数预览判断|王俊|
|2024.12.16|v7.1.5.20241216|1. 新增id_card_type字段2.新增户口本 kv_guang_da_bank_household_register.data3. 新增医学证明 kv_medical_birth_certificate.data 4.优化识别 速度5.新增流程图|王俊|
|2025.01.06|v7.1.6.20250106|1. type 返回other 新增类型 2. id_card_type 返回other 新增类型|王俊|
|2025.02.11|v7.1.7.20250211|新增质检模块|bin_cheng|
|2025.03.03|v7.1.8.20250103|1.修复返回按钮和闪光灯按钮无反应 2.预览页面添加质检参|bin_cheng|
|2025.03.13|v7.1.9.20250313|修复鸿蒙pad预览画面变形的问题|bin_cheng|
|2025.04.07|v7.2.0.20250407|修复预览界面识别成功后再次调用识别接口 的问题|bin_cheng|

|2025.04.23|v7.2.1.20250423|1. 新增质量检测模型kv_qualityinspect.data 2. 缩小har SDK体积大小|王俊|
|---|---|---|---|
|2025.04.28|v7.2.2.20250428|1. 修复预览页切图不完整的问题 2. 2.修复预览识别过快的问题|bin_cheng|
|2025.04.29|v7.2.3.20250429|新增:身份证识别时输入的图片类型不 符,则返回错误码1001|bin_cheng|
|2025.05.14|v7.2.4.20250514|新增识别方法的callback接口|bin_cheng|
|2025.05.28|v7.2.5.20250528|1. UI新改版 2. 新增图片旋正功能 3. 修改启动时调用initICCardRecognizer初 始化方法时需要传context参数|jun_wang|
|2025.06.03|v7.2.6_2025.05.03|新增教师资格证识别能力|bin_cheng|
|2025.06.11|v7.2.7.20250611|1.新增kv_taiwan_hk_macao_compatriot.data 台胞证回乡证支持|jun_wang|
|2025.07.09|v7.2.8.20250709|1. 新增kv_marriage_certificate.data 结婚证支持|jun_wang|
|||2. Demo定制版本身份证UI||
|2025.07.29|v7.2.9.20250729|1. 通用卡证通用版本新增结婚证|jun_wang|
|2025.08.12|v7.3.0_2025.08.12|修复漏洞: 1.去除服务端Banner泄露风险 2.去除md5加密破解风|bin_cheng|
|2025.10.17|v7.3.1_2025.10.17|1.修复身份证第三行地址不显示|jun_wang|
