# 手写信息数字签名移动端SDK (Harmony 版)接口手册 

### **北京数字认证股份有限公司** 

2024 年9 月 

手写信息数字签名移动端SDK(Harmony 版)接口手册 

#### 目 录 

|1 概述**..............................................................................................................................................................................5**|
|---|
|1.1 文档用途................................................................................................................................................................5|
|1.2 产品简介................................................................................................................................................................5|
|**2** 集成说明**...................................................................................................................................................................... 6**|
|2.1 API 包结构及功能介绍........................................................................................................................................... 6|
|2.2 证书配置............................................................................................................................................................... 6|
|2.3 集成流程................................................................................................................................................................6|
|2.4 注意事项............................................................................................................................................................... 7|
|3 SPS 接口说明**.................................................................................................................................................................8**|
|3.1 初始化SIGNATUREAPI实例................................................................................................................................... 8|
|3.2 设置渠道号............................................................................................................................................................8|
|3.3 设置签名原文数据.................................................................................................................................................9|
|3.4 添加单字签名配置信息....................................................................................................................................... 10|
|3.5 添加批注配置信息...............................................................................................................................................11|
|3.6 设置页面屏幕方向...............................................................................................................................................12|
|3.7 显示单字签名框.................................................................................................................................................. 12|
|3.8 显示批注框..........................................................................................................................................................13|
|3.9 自定义手写页面.................................................................................................................................................. 14|
|3.10 添加证据配置信息.............................................................................................................................................15|
|3.11 添加证据HASH配置信息...................................................................................................................................15|
|3.12 添加公章........................................................................................................................................................... 16|
|3.13 生成签名请求加密包.........................................................................................................................................17|
|3.14 签名请求包是否准备就绪..................................................................................................................................17|
|3.15 API释放并重置................................................................................................................................................. 18|
|3.16 开启手写识别....................................................................................................................................................18|
|3.17 提取缓存数据,返回给用户缓存数据................................................................................................................19|
|3.18 恢复缓存数据....................................................................................................................................................19|
|3.19 获取签名图片....................................................................................................................................................20|
|3.20 获取批注图片....................................................................................................................................................20|

第 2 页共 36 页 

手写信息数字签名移动端SDK(Harmony 版)接口手册 

|
3.21 添加附件........................................................................................................................................................... 21|
|---|
|3.22 删除指定附件....................................................................................................................................................21|
|3.23 隐私协议弹窗接口.............................................................................................................................................22|
|3.24 错误码列表........................................................................................................................................................22|
|3.25 附录:对象定义................................................................................................................................................ 24|
|_3.25.1_H5Result_.....................................................................................................................................................24_|
|3.25.2 OriginalContent_............................................................................................................................................. 24_|
|3.25.3 SignatureObj_................................................................................................................................................. 25_|
|_3.25.4 CommentObj.............................................................................................................................................27_|
|3.25.5 CachetObj_.....................................................................................................................................................29_|
|3.25.6 Signer_...........................................................................................................................................................30_|
|3.25.7 SignRule_.......................................................................................................................................................31_|
|3.25.8 BJCASignatureBoardType_...............................................................................................................................33_|
|_3.25.9 CommentInputType...................................................................................................................................33_|
|_3.25.10 DataType................................................................................................................................................. 34_|
|_3.25.11 BioType................................................................................................................................................... 34_|
|_3.25.12 SignatureType......................................................................................................................................... 35_|

第 3 页共 36 页 

手写信息数字签名移动端SDK(Harmony 版)接口手册 

## 欢迎使用 

欢迎您使用手写信息数字签名移动端 SDK,如果本手册能为您提供帮助,带来便利,我们将深 感欣慰。如果您在使用过程中,遇到了问题,或对我们产品有好的建议,可以: 

- 致电客户服务热线 40091978881 

- 或访问公司网站:www.bjca.cn 

与我们联系,对您提出的问题或建议,我们表示衷心的感谢。 

## 版权声明 

本手册著作权属北京数字认证股份有限公司所有,在未经本公司许可的情况下,任何单位或个 人不得以任何方式对本手册的部分或全部内容擅自进行增删、改编、节录、翻印、改写,仅限和北 京数字认证公司的项目合作方公司使用 

北京数字认证股份有限公司 ©2024 

第 4 页共 36 页 

手写信息数字签名移动端SDK(Harmony 版)接口手册 

## 1 概述 

### 1.1 文档用途 

文档主要介绍手写信息数字签名移动端SDK 接口的集成环境、集成流程、接口规范、接口功能, 用以指导集成开发人员正确、准确的完成集成,避免发生差错。 

### 1.2 产品简介 

手写信息数字签名移动端SDK 是一款应用于大众签字确认场景,为个人顾客提供手写签名可信 电子化服务的安全产品。将可靠的电子签名与手写呈像完美结合,以基于 PKI 证书应用体系的数字 签名代替传统纸张书写签字。手写信息数字签名移动端SDK 使现场签字确认不再耗费纸张,大幅降 低成本,提升管理水平,提高业务效率,以权威可信的产品理念,绿色环保的服务初衷、为客户带 来经济、安全、高效的综合效益提升。 

第 5 页共 36 页 

手写信息数字签名移动端SDK(Harmony 版)接口手册 

## **2** 集成说明 

### 2.1 API 包结构及功能介绍 

|放置目录|文件名称|说明|
|---|---|---|
|libs|anysign.har|SDK 核心包,必须集成|
|rawfile|CAServerCert.txt|详见2.2 证书配置|

### **2.2** 证书配置 

注:har 包中默认配置了2.0 证书,如果是用的手写信息数字签名2.0 服务器可跳过此步骤,如需使用 1.X 服务器,需重新对内容进行修改 

CAServerCert.txt:加密证书配置(放在集成工程resources/rawfile 目录下) 

加密证书处理: 

把项目经理提供的证书base64 内容替换到CAServerCert.txt 文件中,只替换文件中的证书base64 内容,-----BEGIN CERTIFICATE-----和-----END CERTIFICATE----- 要保留 

PS:如果是证书文件,需证书转base64 操作,使用代码编辑器(如:NotePad)打开后,会看到一些乱码,全选之后 进行Base64 Encode 操作 

### 2.3 集成流程 

第四步
调用显示签名/批注/批注批注
接口弹出书写框

第三步
配置签名数据,

第二步
初始化 API

第一步
部署配置文件,引

第一步 第二步 第三步 第四步
部署配置文件,引 初始化 API 配置签名数据, 调用显示签名/批注/批注批注
接口弹出书写框
resetAPI
第五步
第六步
提交配置,调用签名
添加签名证据信息
生成加密报文

第五步
添加签名证据信息

第六步
生成加密报文

第 6 页共 36 页 

手写信息数字签名移动端SDK(Harmony 版)接口手册 

- 将CAServerCert.txt 放到工程resources/rawfile 目录下面,将har 包放置工程目录下,在oh-package.json5 文件 的dependencies 下设置har 包的引用。 

- 在工程Ability 中的onWindowStageCreate 方法中添加如下代码: 

let windowClass: window.Window = windowStage.getMainWindowSync() 

let storage: LocalStorage = new LocalStorage() 

storage.setOrCreate("mainWindow", windowClass) 

- 接口调用 

- 1)初始化SignatureAPI。 

- 2) 调用setChannel(mChannel:string)配置渠道号,调用setOrigialContent ( originalContent:OriginalContent )配置签名 对应的模版数据原文。 

- 3) 调用api.addSignatureObj(signatureObj:SignatureObj ) 或者api.addCommentObj(commentObj:CommentObj )配置 签名(前者对应手写签名,后者对应批注)。 

- 4) 调用addEvidence(int signIndex,int index,byte[] content,BioType biotype, DataType evidenceType)添加签名证据信 息。 

- 5) 上述步骤设置完成后,然后调用api.showSignatureDialog(int index, confirmCallback: (result: H5Result) => void, cancelCallback: () => void) 或者api.showCommentDialog(int index, confirmCallback: (result: H5Result) => void, cancelCallback: () => void) 弹出输入框完成签名(注:此处的index 与4 中设置的index 要对应上),签名图片会在 confirmCallback 回调函数中返回,以便用户获取签名状态、签名数据拷贝,用于展现等操作。 

- 6) 调用api.genSignRequest()获取包含签字图片、表单信息等加密信息的报文用于上传服务端。注:必须在用户输 入完成配置文件定义的所有手写数据之后此接口才能传出报文,否则会抛出异常。 

通过调用api.resetAPI()来重置签名对象及业务数据对象,以便重新调用3,4,5,6,7,8 完成其它业务操作。 

### **2.4** 注意事项 

- 1)在鸿蒙中页面反向sdk 新增设置屏幕方向接口setPageOrientation(orientation: window.Orientation),需在调用 showSignatureDialog 或是showCommentDialog 方法前调用,调用后弹出的签名或批注页面方向为设置的方向 

第 7 页共 36 页 

手写信息数字签名移动端SDK(Harmony 版)接口手册 

2)调用手写信息数字签名移动端SDK 必须要有模板数据,而且模板数据类型必须正确,比如xml,需注明是xml, 设置模板接口的参数1 设置为ContextID.FORMDATA_HTML。具体模板类型的定义是:10: XML 格式,11:HTML 格式,12:PDF 格式。 

- 3)配置的签名的index 必须与showSignatureDialog(index)或者showCommentDialog(index)中的index 一致,否则弹框 无效。 

- 4)签名的index 的范围为0~99,不应该超过该范围。 

- 5)配置输入弹出框的时候务必要设置签名人信息和签名规则,如obj.Signer = new Signer("李磊", "11101110", 

Signer.TYPE_IDENTITY_CARD),否则会弹框无效。 

## 3 SPS 接口说明 

### **3.1** 初始化 **SignatureAPI** 实例 

功能: 

获得一个对象实例,初始化对象。可以在签名事务开始时初始化。 

函数定义: 

public SignatureAPI(); 

示例代码: 

let api: SignatureAPI = new SignatureAPI() 

### **3.2** 设置渠道号 

功能: 

设置渠道号。 

函数定义: 

public setChannel(mChannel: string): number 

参数: 

mChannel:业务渠道号,渠道号应该为小于20 位的数字,不能包含字母。 

返回: 

第 8 页共 36 页 

手写信息数字签名移动端SDK(Harmony 版)接口手册 

SUCCESS(0)成功,非0 失败,具体参考错误码列表 

示例代码: 

let apiResul:numbert = this.api.setChannel('999999') 

### **3.3** 设置签名原文数据 

功能: 

向API 数据缓存中放入表单配置数据。 

函数定义: 

public setOrigialContent(origialContent: OriginalContent): Promise<number> 

参数: 

originalContent:原文内容对象,对象内容如下: 

constructor(typeOrContentType: OriginalContentType | number, contentUtf8: Uint8Array, businessId: string, 

templateSerial?: string) 

参数: 

contentType:原文类型 contentUtf8:原文二进制数据 businessId:业务工单号 templateSerial:模板序列号 

注:contentType 为XML 时要配置templateSerial,其他格式时使用第一个构造函数。 

返回: 

SUCCESS(0)成功,非0 失败,具体参考错误码列表 

示例代码: 

let original = await getContext().resourceManager.getRawFileContent("original.pdf") 

let originalContent: OriginalContent = new OriginalContent(OriginalContentType.CONTENT_TYPE_PDF, original, "111") this.api.setOrigialContent(originalContent).then(result => { 

console.log("apiResult -- setOrigialContent:" + result) 

}) 

第 9 页共 36 页 

手写信息数字签名移动端SDK(Harmony 版)接口手册 

### **3.4** 添加单字签名配置信息 

功能: 

注册一个用户签名对象。 

函数定义: 

public addSignatureObj(signatureObj: SignatureObj): number 

参数: 

SignatureObj :单字签名对象。 

返回: 

SUCCESS(0)成功,非0 失败,具体参考错误码列表 

示例代码: 

let signRule: SignRule = SignRule.getInstance(SignRuleType.TYPE_XYZ) 

signRule.setXYZRule(new XYZRule(84, 523, 200, 411, 1, "dp")) 

//签名人信息 

let signer: Signer = new Signer("古力", "534933199608021286", SignerCardType.TYPE_IDENTITY_CARD, false) 

//签名对象 

let obj: SignatureObj = new SignatureObj(this.INDEX_MULTI_SIGN, signRule, signer) 

obj.signatureBoardType = SignatureBoardType.BJCAAnySignWordNumberTransformType 

obj.title = '请小明签字' 

obj.titleSpanFromOffset = 1 obj.titleSpanToOffset = 3 obj.isdistinguish = false 

obj.ocrErrorTime = -1 

obj.penColor = '#00FF00' 

obj.nessesary = false obj.penSize = 14 

obj.single_width = 100 obj.single_height = 100 

obj.distinguishErrorText= '识别失败了,重新输入' 

obj.isNoBrushes = false 

第 10 页共 36 页 

手写信息数字签名移动端SDK(Harmony 版)接口手册 

obj.minWidth = 8 

obj.maxWidth = 14 

obj.isShowTouchViewBg = true obj.isShowHintText = true 

this.apiResult = this.api.addSignatureObj(obj) 

### **3.5** 添加批注配置信息 

功能: 

注册一个用户批注对象。 

函数定义: 

public addCommentObj(signatureObj: CommentObj): number 

参数: 

commentObj :批注对象。 

返回: 

SUCCESS(0)成功,非0 失败,具体参考错误码列表 

示例代码: 

//批注对象 

let massobj_Normal: CommentObj = new CommentObj(this.INDEX_ANIMATION_COMMENT, signRule1, signer) let text = '本人已经阅读保险条款,产品说明书和投保提示书,了解本产品的特点和保单利益的不确定性。' massobj_Normal.mass_dlg_type = CommentInputType.DoubleView; 

massobj_Normal.commitment = text 

//识别错误提示语 

massobj_Normal.distinguishErrorText = "错误"; 

//背景字是否显示 

massobj_Normal.isShowHintText = true; 

//背景图片是否显示 

massobj_Normal.isShowTouchViewBg = true; 

//是否开启手写识别开关 

第 11 页共 36 页 

手写信息数字签名移动端SDK(Harmony 版)接口手册 

massobj_Normal.isdistinguish = false; 

//设置笔迹颜色,默认为黑色 

massobj_Normal.penColor = '#FF0000'; 

//设置笔迹粗细 

massobj_Normal.penSize =10; 

massobj_Normal.isNoBrushes = true; massobj_Normal.maxWidth = 15; 

massobj_Normal.minWidth = 4; 

//识别错误的次数,超过识别错误个数时直接跳出识别,直接返回结果。默认为0 时,一直走识别。此参数的前提 是识别系统为true 时 

massobj_Normal.ocrErrorTime = 3; 

this.apiResult = this.api.addCommentObj(massobj_Normal) 

### **3.6** 设置页面屏幕方向 

##### 功能: 

##### 设置后续弹出的签名或批注页面的屏幕方向 

函数定义: 

public setPageOrientation(orientation: window.Orientation, revertOnBack?: boolean) 

参数: 

orientation:鸿蒙页面方向对象 

revertOnBack:可选参数,是否在回调后转回原调用页面方向,默认true 

示例代码: 

this.api.setPageOrientation(window.Orientation.AUTO_ROTATION_LANDSCAPE) 

### **3.7** 显示单字签名框 

功能: 

录入手写签名, 

第 12 页共 36 页 

手写信息数字签名移动端SDK(Harmony 版)接口手册 

函数定义: 

public showSignatureDialog(index: number, confirmCallback: (result: H5Result) => void, cancelCallback: () => void): 

number 

参数: 

index:签名的索引值,默认从0 开始,最大为99。此处的index 值应该与初始化中的注册签名对象的index 值相同。 

confirmCallback:完成事件侦听处理,签名结束时传出签名图片base64、识别结果等内容。具体H5Result 对 象信息详见 3.24.1 H5Result 

cancelCallback:取消签名页时执行,用于某一个签名页取消时事件侦听处理。 

返回: 

SUCCESS(0)成功,非0 失败,具体参考错误码列表 

###### 示例代码: 

this.apiResult = this.api.showSignatureDialog(this.INDEX_BATCH_SIGN, (result: H5Result) => { 

console.log("apiResult -- " + JSON.stringify(result)) 

this.result = JSON.stringify(result) 

- }, () => { 

console.log("apiResult -- cancelCallback") 

}) 

### **3.8** 显示批注框 

功能: 

录入批注信息。 

函数定义: 

public showCommentDialog(index: number, confirmCallback: (result: H5Result) => void, cancelCallback: () => void, 

isSplitPicture?: boolean): number 

参数: 

index:签名的索引值,默认从0 开始,最大为99 

confirmCallback:完成事件侦听处理,签名结束时传出签名图片base64、识别结果等内容。具体H5Result 对 

第 13 页共 36 页 

手写信息数字签名移动端SDK(Harmony 版)接口手册 

象信息详见 3.24.1 H5Result 

cancelCallback:取消签名页时执行,用于某一个签名页取消时事件侦听处理。 

返回: 

SUCCESS(0)成功,非0 失败,具体参考错误码列表 

示例代码: 

this.apiResult = this.api.showCommentDialog(this.INDEX_ANIMATION_COMMENT, (result: H5Result) => { 

console.log("apiResult -- " + JSON.stringify(result)) 

this.result = JSON.stringify(result) 

- }, () => { 

console.log("apiResult -- cancelCallback") 

}) 

### **3.9** 自定义手写页面 

##### 功能: 

自定义手写签名或批注框样式,可参考 demo 中 CustomizeSignPage 类集成 

集成步骤 

- 1,初始化签名人信息 

- 在 aboutToAppear()初始化签名人信息,并调用 showSignatureDialog 接口用于接收返回数据 

- 2,自定义签名板样式 

在页面 build()中添加 SignComponent()画布控件进行自定义 

- 3,清屏功能触发 

getContext().eventHub.emit(EventConsts.EVENT_CUSTOMIZE_BTN, SignEvent.CLEAR) 

- 4,完成签名功能触发 

getContext().eventHub.emit(EventConsts.EVENT_CUSTOMIZE_BTN, SignEvent.CONFIRM) 

- 5,释放 evenHub 

- //在合适的时机,移除 evenHub,比如 aboutToDisappear 中 

getContext().eventHub.off(EventConsts.EVENT_CUSTOMIZE_BTN) 

第 14 页共 36 页 

手写信息数字签名移动端SDK(Harmony 版)接口手册 

示例代码: 

各接口调用和以上示例相同 

### **3.10** 添加证据配置信息 

功能: 

设置第三方自采证据。 

函数定义: 

public async addEvidence(signIndex: number, index: number, content: Uint8Array, bioType: BioType, dataType: 

DataType): Promise<number> 

参数: 

signIndex:签名的索引值,默认从0 开始,最大为99。对应于添加签名时的index,只有V1.3.1 添加证据才有 

效。 

index:证据的索引值,默认从0 开始,最大为99,代表第几个证据。 

content:证据数据原文。 biotype: 证据内容类型 dataType:证据类型。 

返回: 

SUCCESS(0)成功,非0 失败,具体参考错误码列表 

示例代码: 

this.api.addEvidence(this.INDEX_MULTI_SIGN,0,picContent,BioType.PHOTO_SIGNER_IDENTITY_CARD_FRONT, 

DataType.IMAGE_GIF).then(result=> { 

console.log("apiResult 添加证据回调-- addEvidence:" + result) 

}) 

### **3.11** 添加证据 **Hash** 配置信息 

功能: 

第 15 页共 36 页 

手写信息数字签名移动端SDK(Harmony 版)接口手册 

设置第三方自采证据Hash。 

###### 函数定义: 

public addEvidenceHash(signIndex: number, index: number, contentHash: string, bioType: BioType, dataType: 

DataType): number 

参数: 

signIndex:签名的索引值,默认从0 开始,最大为99。对应于添加签名时的index,只有V1.3.1 添加证据才有 效。 

index:证据的索引值,默认从0 开始,最大为99,代表第几个证据。 

contentHash:证据Hash。 

biotype: 证据内容类型 

dataType:证据类型。 

返回: 

SUCCESS(0)成功,非0 失败,具体参考错误码列表 

###### 示例代码: 

this.api.addEvidenceHash(this.INDEX_MULTI_SIGN,0,hashStr,BioType.PHOTO_SIGNER_IDENTITY_CARD_FRON 

T,DataType.IMAGE_GIF).then(result=> { 

console.log("apiResult 添加证据回调-- addEvidence:" + result) 

}) 

### **3.12** 添加公章 

功能: 

配置公章、单位章。 

###### 函数定义: 

public addChachetObj(cachetObj: CachetObj): number 

参数: 

cachetObj:公章对象。 

返回: 

SUCCESS(0)成功,非0 失败,具体参考错误码列表 

第 16 页共 36 页 

手写信息数字签名移动端SDK(Harmony 版)接口手册 

示例代码: 

Let obj = new CacheObj() 

obj.Signer = signer 

obj.SignRule = signRule 

obj.IsTSS = true 

this.apiResult = this.api.addChachetObj(obj) 

### **3.13** 生成签名请求加密包 

功能: 

产生上传服务端的数据报文,需要手写签名、知情确认均签署完毕。 函数定义: 

public async genSignRequest(): Promise<Object> 

返回: 

加密包返回的是String 类型。 

示例代码: 

this.api.genSignRequest().then((signRequest: Object) => { 

this.result = signRequest as string 

let context = getContext(this) as common.Context; 

writeStringToFile(context, 'test88.txt', this.result); 

console.log("apiResult -- genSignRequest:" + signRequest) 

}); 

### **3.14** 签名请求包是否准备就绪 

###### 功能: 

是否签名均已签署,以及附件均已添加等。 

函数定义: 

public isReadyToGen(): number 

返回: 

第 17 页共 36 页 

手写信息数字签名移动端SDK(Harmony 版)接口手册 

SUCCESS(0)成功,非0 失败,具体参考错误码列表 

示例代码: 

this.apiResult = this.api.isReadyToGen(); 

### **3.15 API** 释放并重置 

功能: 

每次使用API 之前,或者使用完毕后调用,清空临时缓存数据,包含数据模板,相关签名、批 注图片轨迹等等。 

函数定义: 

public resetAPI(); 

示例代码: 

this.api.resetAPI() 

### **3.16** 开启手写识别 

功能:开启手写识别。开启后,可在手写配置信息中打开识别开关。 函数定义: 

public startOCR(ocrCapture: AnySignOCRCapture): number 

参数: 

ocrCapture:手写识别配置对象 

##### 返回: 

SUCCESS(0)成功,非0 失败,具体参考错误码列表 

示例代码: 

let ocrCapture: AnySignOCRCapture = new AnySignOCRCapture(); 

ocrCapture.IPAddress = "http://223.70.139.221:11204/HWRV2/RecvServlet" 

ocrCapture.serviceID = 'yeshiwaimianpeide' 

ocrCapture.appID = 'waimianpeide o' 

this.apiResult = this.api.startOCR(ocrCapture) 

第 18 页共 36 页 

手写信息数字签名移动端SDK(Harmony 版)接口手册 

### **3.17** 提取缓存数据,返回给用户缓存数据 

功能: 

提取缓存数据并返回给用户,用来让用户存储现阶段进行的数据 

函数定义: 

public getCacheDatas(key: string): Promise<string> 

参数: 

key: 加密缓存的密钥 

返回: 

String 加密字符串 

示例代码: 

let keyData = new Uint8Array([238, 249, 61, 55, 128, 220, 183, 224, 139, 253, 248, 239, 239, 41, 71, 25, 235, 206, 230, 162, 249, 27, 234, 114]); 

this.randData = new util.Base64Helper().encodeToStringSync(keyData); 

this.api.getCacheDatas(this.randData).then((encData => { 

this.cacheResult = encData 

})) 

### **3.18** 恢复缓存数据 

功能: 

恢复缓存数据并继续 

函数定义: 

public setCacheDatas(cacheData: string, key: string): Promise<number> 

参数: 

cacheData:加密数据 

key: 解密缓存的密钥 

第 19 页共 36 页 

手写信息数字签名移动端SDK(Harmony 版)接口手册 

返回: 

SUCCESS(0)成功,非0 失败,具体参考错误码列表 

示例代码: 

this.api.setCacheDatas(this.cacheResult, this.randData).then(code => { 

console.log("apiResult -- setCacheDatas:" + code) 

}) 

### **3.19** 获取签名图片 

功能: 

获取指定index 的手写签名图片 

函数定义: 

public getSignatureBitmap(index: number): string 参数: cid : 签名索引值 返回: 图片base64 数据 示例代码: 

this.resultImageBase64 = this.api.getSignatureBitmap(this.INDEX_WHITE_BOARD_SIGN) 

### **3.20** 获取批注图片 

功能: 

获取指定index 的手写批注图片 

函数定义: 

public getCommentBitmap(index: number): string 

参数: 

cid : 签名索引值 

返回: 

图片base64 数据 

示例代码: 

第 20 页共 36 页 

手写信息数字签名移动端SDK(Harmony 版)接口手册 

this.resultImageBase64 = this.api.getCommentBitmap(this.INDEX_ANIMATION_COMMENT); 

### **3.21** 添加附件 

功能: 

添加附件 

函数定义: 

public addPicAttach(index: number, utf8File: Uint8Array, dataType: DataType): number 参数: 

index:附件索引值 utfFile:附件数据 dataType:数据类型 返回: 

SUCCESS(0)成功,非0 失败,具体参考错误码列表 

示例代码: 

let content = new Uint8Array([1, 2, 3, 4]) 

this.apiResult = this.api.addPicAttach(0, content, DataType.IMAGE_PNG) 

### **3.22** 删除指定附件 

功能:删除指定附件 

函数定义: 

public deleteData(index: number): number 

参数: 

index:删除附件的索引值 

返回: 

SUCCESS(0)成功,非0 失败,具体参考错误码列表 

示例代码: 

this.apiResult = this.api.deleteData(1) 

第 21 页共 36 页 

手写信息数字签名移动端SDK(Harmony 版)接口手册 

### **3.23** 隐私协议弹窗接口 

功能:显示隐私协议弹窗,可查看协议详情等 函数定义: 

public async showSecurityAlertView():Promise<boolean> 

参数: 

无 

返回: 

true 同意,false 不同意 

示例代码: 

let result = await this.api.showSecurityAlertView() 

### **3.24** 错误码列表 

|异常类型|错误码|
|---|---|
|调用成功|0|
|api 尚未初始化|31000101|
|渠道号长度不符或者是包含非法字符|31000201|
|渠道号不能为空|31000202|
|未设置工单号|31000301|
|设置单位章中规则为空|31000302|
|签名人信息不能为空|31000401|
|签名规则信息不能为空|31000402|
|签名框正在显示,不能再次显示|31000403|
|内存不足|31000404|
|签名索引值超出范围|31000405|
|未发现有效的签名配置索引值|31000406|
|边签名边拍照,未获取权限|31000407|

第 22 页共 36 页 

|手写信息数字签名移动端SDK(Harmony 版)接口手册|
|---|
|未设置KW 关键字 31000408|
|未设置XYZ 坐标 31000409|
|未设置服务端配置信息 31000410|
|签名标题栏高亮索引值错误 31000411|
|签名数据保存对象 AnySignMemcache,AnySignSealMemcache 为空 31000412|
|姓名格式是身份证时,传入的姓名格式或者身份证号不 正确 31000413|
|批注内容为空 31000415|
|已经签名,不能再对其添加证据 31000501|
|添加证据时,证据原文信息不能为空 31000502|
|添加证据时,证据类型设置错误 31000503|
|添加证据hash 时,证据原文信息不能为空 31000504|
|判断上传数据是否就绪或者生成加密包时,如果是 nessary 则必须签名 31000601|
|判断上传数据是否就绪时,应该至少保证有一个签名 31000602|
|添加单位章对象不合法 31000701|
|添加图片附件,索引值不合法 31000801|
|参数为空,sessionId 或者key 为空 31000901|
|缓存数据失败 31000902|
|读取缓存数据失败 31000903|
|删除缓存失败 31000904|
|没有需要缓存的数据 31000905|
|没有需要删除的附件数据 31000906|
|重复点击异常 31000908|
|用户拒绝隐私政策 31000909|

第 23 页共 36 页 

手写信息数字签名移动端SDK(Harmony 版)接口手册 

### **3.25** 附录:对象定义 

#### **3.25.1** H5Result 

|string Image|
|---|
|签名或批注图片base64|
|number ocrState|
|0:不识别 1:识别通过 2:识别失败|

#### 3.25.2 OriginalContent 

|static|||
|---|---|---|
||number|CONTENT_TPYE_PDF 代表PDF 数据|
||number|CONTENT_TPYE_HTML 代表HTML 数据|
||number|CONTENT_TPYE_XML 代表XML 数据|
|OriginalContentType|CONTENT_TPYE_|PDF、CONTENT_TPYE_HTML、CONTENT_TPYE_XML|
|Uint8Array|content 原文数据||
|String|businessId 业务工单号||
|String|templateSerial 模板序列号,当co 况,不需要设置|ntentType 为CONTENT_TPYE_XML,此项有效,其他情|

第 24 页共 36 页 

手写信息数字签名移动端SDK(Harmony 版)接口手册 

#### **3.25.3** SignatureObj 

|number|index 签名对象的索引值,从0开始,取值0-99;|
|---|---|
|Signer|Signer 签名人信息对象,详见附件Signer 对象定义;|
|SignRule|SignRule 签名规则,详见附件SignRule 对象定义|
|String|title 需要显示在签名框顶栏的标题|
|number|titleSpanFromOffset 单字签名框中需要突出显示部分的起始位置|
|number|titleSpanToOffset 单字签名框中需要突出显示部分的结束位置|
|float|single_width 产生图片的宽,单位dip(动画签名界面和双屏界面则为单字的宽),默 认为150.|
|float|single_height 标识产生图片的高,单位dip(动画签名界面和双屏界面则为单字的高), 默认为150.|
|boolean|nessesary 是否为必备数据项,如果为false,当此签名没有签名内容时仍可正常生成 加密包|
|string|penColor 字迹颜色,默认黑色,格式为ARGB,每通道8bit,默认为黑色。|
|number|penSize|

第 25 页共 36 页 

手写信息数字签名移动端SDK(Harmony 版)接口手册 

||
isNoBrushes 为true 时有效,字迹粗细,默认值为6;isNoBrushes 为false 时,
笔迹粗细通过minWidth 和maxWidth
设置。|
|---|---|
|boolean|isdistinguish 是否开启字迹识别功能,默认为false|
|number|ocrErrorTime 识别错误的次数,超过识别错误个数时直接跳出识别,直接返回结果。默 认为0时,一直走识别。此参数的前提是识别系统为true 时|
|String|distinguishErrorText 识别字迹错误提示语句,默认为“识别失败”|
|String|agentName 手写识别要识别的姓名,设置了会决定背景字显示,如不设置此属性则以 Signer中的姓名为主|
|BJCASignatureBoardTy pe|signatureBoardType 显示框样式的类型|
|boolean|isNoBrushes 是否关闭笔锋,true为不要笔锋,false为要笔锋。默认为true|
|number|lineMax 生成图片每行字的个数(仅在动画签名中生效)|
|number|hintTextSize 背景提示字大小,单位sp,默认120(只限于动画模式生效)|
|string|hintTextColor 背景提示字颜色,(只限于动画模式生效) 请调用Color.parseColor()方法将颜色字符串解析为颜色值,颜色字符串 支持#RRGGBB 和#AARRGGBB 两种。 默认颜色为#5b7b7e80|
|float|currentEditBarTextSize 设置当前正在签署提示字的大小,仅在动画签名模式中生效|

第 26 页共 36 页 

手写信息数字签名移动端SDK(Harmony 版)接口手册 

|string|highlightTextColor 设置签署的高亮字的颜色|
|---|---|
|string|titleColor 设置提示字的颜色,多字签名有效|
|boolean|isShowTouchViewBg 动画模式是否显示米字格,默认为true。|
|boolean|isShowHintText 动画模式是否显示背景字,默认为true。|
|number|minWidth 笔锋的最细大小(要笔锋情况下生效)默认值6.|
|number|maxWidth 笔锋的最粗大小(要笔锋情况下生效),默认值6.|

#### **3.25.4 CommentObj** 

|number|index 签名对象的索引值,从0开始,取值0-99;|
|---|---|
|Signer|signer 签名人信息对象,详见附件Signer 对象定义;|
|SignRule|signRule 签名规则,详见附件SignRule 对象定义|
|float|single_width 标识产生图片的宽,单位dip。(动画界面和双屏界面则为单格的宽)默认值 150.|
|float|single_height 标识产生图片的高,单位dip。(动画界面和双屏界面则为单格的高)默认值 150.|

第 27 页共 36 页 

手写信息数字签名移动端SDK(Harmony 版)接口手册 

|number|
lineMax
在动画批注中生效,每行的最大字数,默认为25|
|---|---|
|string|penColor 字迹颜色,默认黑色,格式为ARGB,每通道8bit,默认为黑色。|
|number|penSize isNoBrushes 为true 时有效,字迹粗细,默认值为6;isNoBrushes 为false 时,笔 迹粗细通过minWidth 和maxWidth 设置。|
|boolean|isNoBrushes 是否关闭笔锋,true为不要笔锋,false为要笔锋。默认值true。|
|String|commitment 对于多字签名框,需要用户抄录的内容|
|CommentInputType|mass_dlg_type 多字输入框类型,默认为{@link CommentInputType#Normal}|
|number|editBarTextSize 设置提示字的大小,仅在动画批注模式中生效|
|String|editBarTextColor 设置提示字的颜色,仅在动画批注模式中生效|
|float|currentEditBarTextSize 设置当前正在签署提示字的大小,仅在动画批注模式中生效|
|String|currentEditBarTextColor 设置当前正在签署提示字的颜色,仅在动画批注模式中生效|
|String|distinguishErrorText 识别错误提示语|
|boolean|isdistinguish 是否开启字迹识别功能,默认为false|
|number|ocrErrorTime 识别错误的次数,超过识别错误个数时直接跳出识别,直接返回结果。默认|

第 28 页共 36 页 

手写信息数字签名移动端SDK(Harmony 版)接口手册 

|为0时,一直走识别。此参数的前提是识别系统为true 时|
|---|
|boolean isShowTouchViewBg 动画模式是否显示米字格,默认为true。|
|boolean isShowHintText 动画模式是否显示背景字,默认为true。|
|number minWidth 笔锋的最细大小(要笔锋情况下生效),默认值6.|
|number maxWidth 笔锋的最粗大小(要笔锋情况下生效),默认值6.|

#### 3.25.5 CachetObj 

String tid 服务号 Signer signer 签名人信息对象,详见附件Signer 对象定义; 

构造函数摘要 

CachetObj(String tid, Signer signer) 

tid :服务号 signer:签名人信息 

方法摘要 

第 29 页共 36 页 

手写信息数字签名移动端SDK(Harmony 版)接口手册 

void setTid(String tid) 设置tid void setSigner(Signer signer) 设置签名人信息 

#### 3.25.6 Signer 

SignerCardType enum SignerCardType
{
TYPE_IDENTITY_CARD ,
居民身份证
TYPE_OFFICER_CARD ,
军官证
TYPE_PASSPORT_CARD ,
护照
TYPE_RESIDENT_CARD,
户口本
TYPE_RETURNHOME_CARD,
港澳台回乡证
TYPE_BIRTH_CARD,
出生证
TYPE_PERMANENTRESIDENCE_CARD
外国人永久居留身份证
TYPE_OTHER_CARD
其他证件
};
构造函数摘要

第 30 页共 36 页 

手写信息数字签名移动端SDK(Harmony 版)接口手册 

Signer(String name, String id,SignerCardType type) 配置手写签名或单位章时使用 name:签名人姓名 id :签名人证件号 type:签名人证件类型(不传默认身份证) 

#### 3.25.7 SignRule 

嵌套类摘要 static class SignRule.KWRule static class SignRule.SignRuleType static class SignRule.XYZRule 

|方法摘要||
|---|---|
|staticSignRule|getInstance(SignRule.SignRuleTypetype) 获取签名定位规则实例|
|SignRule.KWRule|getKWRule()|
|SignRule.SignRuleType|getmSignRuleType()|
|SignRule.XYZRule|getXYZRule()|
|void|setKWRule(SignRule.KWRulerule)|
|void|setServerConfigRule(String configName)|
|void|setXYZRule(SignRule.XYZRulerule)|

第 31 页共 36 页 

手写信息数字签名移动端SDK(Harmony 版)接口手册 

|SignRuleType|SignRuleType 枚举数据类型 enum SignRu { TYP 使用 TYP 使用 TYP 使用 };|leType E_KEY_WORD, 关键字方式定位签名图片位置 E_XYZ, 坐标定位签名图片位置 E_USE_SERVER_SIDE_CONFIG 在服务器端配置好的信息定位签名图片位置|
|---|---|---|
|KWRule|String|keyWord 关键字|
||number|XOffset 签名图片相对于关键字X 轴偏移量|
||number|YOffset 签名图片相对于关键字Y 轴偏移量|
||number|PageNo 签名在PDF 中的页码|
||String|KWIndex 从Pdf 的第pageNo 页开始搜索第几个此关键字|

第 32 页共 36 页 

手写信息数字签名移动端SDK(Harmony 版)接口手册 

|XYZRule float|Bottom 签名图片底边坐标值,相对于PDF 当页最左下角(0,0)点|
|---|---|
|float|Left 签名图片最左边坐标值,相对于PDF 当页最左下角(0,0)点|
|float|Right 签名图片最右边坐标值,相对于PDF 当页最左下角(0,0)点|
|float|Top 签名图片顶边坐标值,相对于PDF 当页最左下角(0,0)点|
|number|PageNo 签名在PDF 中的页码|

#### 3.25.8 BJCASignatureBoardType 

|BJCASignatureBoar dType|public enum BJCASignatureBoardType { BJCAAnySignWordNumberTransformType 姓名5字以内是白板模式,超过5字则为动画模式 BJCAAnySignSinglePageType 默认模式,白板模式 BJCAAnySignMultiwordType 动画模式 BJCAAnySignDoubleViewType 双屏无限签模式(仅支持横屏) whiteBackTextBtn 自定义签名 }|
|---|---|

#### **3.25.9 CommentInputType** 

public enum CommentInputType CommentInputType { Normal, 

第 33 页共 36 页 

||手写信息数字签名移动端SDK(Harmony 版)接口手册|
|---|---|
|动画批注界面 DoubleView, 双屏无限签界面(仅支持横屏) }||

#### **3.25.10 DataType** 

|DataType public enumDataType {|
|---|
|IMAGE_GIF,|
|IMAGE_JPEG,|
|IMAGE_PNG,|
|MEDIA_AU,|
|MEDIA_AIFF,|
|MEDIA_WAVE,|
|MEDIA_MIDI,|
|MEDIA_MP4,|
|MEDIA_M4V,|
|MEDIA_3G2,|
|MEDIA_3GP2,|
|MEDIA_3GP,|
|MEDIA_3GPP|
|}|

#### **3.25.11 BioType** 

BioType public enum BioType { /** 签名人居民身份证正面**/ PHOTO_SIGNER_IDENTITY_CARD_FRONT, /** 签名人居民身份证背面**/ 

第 34 页共 36 页 

手写信息数字签名移动端SDK(Harmony 版)接口手册 

PHOTO_SIGNER_IDENTITY_CARD_BACK, /** 签署动作视频**/ VIDEO_SIGNER_ACTIVE, /** 其他视频**/ VIDEO_SIGNER_ACTIVE_OTHER, /** 签名人复述录音**/ SOUND_SIGNER_RETELL, /** 签名人自定义录音**/ SOUND_SIGNER_OTHER, /**签名人当前位置**/ CURRENT_SIGNER_POSITION, /**签名人面部正面照**/ FACE_PHOTO_OF_SIGNER, /**签名人其他证件照**/ SIGNER_OTHER_CERTIFICATES, /**签名动作照片**/ SIGNATURE_ACTION_PHOTO, /**签名现场环境照片**/ SIGNATURE_SITE_ENVIRONMENT_PHOTO, /**其他照片**/ OTHER_PHOTO, /**其他类型的证据**/ OTHER_TYPES_OF_EVIDENCE } 

#### **3.25.12 SignatureType** 

SignatureType public enum SignatureType { SIGN_TYPE_SIGN, 签名 SIGN_TYPE_SIGN_COMMENT 

第 35 页共 36 页 

手写信息数字签名移动端SDK(Harmony 版)接口手册 批签 SIGN_TYPE_COMMENT 批注 } 

第 36 页共 36 页
