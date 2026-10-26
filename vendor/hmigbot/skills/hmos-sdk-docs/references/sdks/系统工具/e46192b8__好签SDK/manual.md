# pdfsdk 接入说明 

# 介绍 

pdfsdk 是一款为 HarmonyOS Next 平台量身定制的 pdf 预览编辑开发 工具包 , 模拟真实笔迹,实现如同纸上同样签字效果 

矢量笔迹写入,缩放不模糊,无锯齿 

全文圈批,支持手笔分离,圈批更自然 

用词说明 

签名 支持 签名位置、大小、旋转 调整操作。 支持 签名保存为签名 模版,反复调用。 

圈批 在圈批模式,可全文手写批注,具备擦除,清空笔迹等功能,也 可根据需求调节笔迹的粗细,颜色等属性 

图片 支持插入图片,调整图片位置、大小、旋转 

文本 可输入文字插入文件指定位置,并调整文本位置、大小、旋转 

验签 SDK 自动记录插入到 PDF 文件中对象和身份信息,并生成验签信 息。 支持显示验签信息 卡片,点击该卡片实现签名对象的快速定位 

demo 项目 

具体集成插件方法可参考工程, 

注意:内部授权码和 demo 项目属性绑定,仅可用于 demo 项目,其他 项目需申请授权码才可以正常使用 

下载安装 

ohpm install @wellsign/pdfsdk 

# 依赖说明 

由于本工具包依赖 harmony-utils 和 harmony-dialog 插件,项目需要 

# 按照对应插件的文档在 UIAbility 中做插件初始化 

# 安装 

ohpm i @pura/harmony-utils 

ohpm i @pura/harmony-dialog 

初始化 

DialogHelper.setDefaultConfig((config) => { config.uiAbilityContext = this.context; 

}) 

AppUtil.init(this.context); 

HqManager 接口和属性列表 

接口列表 

接口 参数 

功能 

HqManager.init(context,clientId,secretKey) 

context : UIAbilityContext,clientId: 授权端 id,secretKey: 授权码 sdk 初始化 

属性列表 

属性 

描述 

HqManager.signUser 

# 设置当前签署人相关信息 ,隔离不同签署人数据 

HqManager.openCache 

设置当用户退出编辑 pdf 时,是否缓存用户签批数据,默认开启 

HqManager.onlyPen 

设置当圈批时,是否只允许华为笔输入笔迹(不影响翻页及拖拽) 

HqManager 使用示例 

SDK 初始化 

在 APP 冷启动后,使用本插件打开 pdf 前,需调用初始化接口,传入 正确的 clientId 及授权码 , 才可对 pdf 文件做后续操作。 当授权失败 时,会抛出异常,代码中须做错误处理 

import { HqManager } from 'pdfsdk'; 

async aboutToAppear() { 

// 初始化授权 

try { 

await HqManager.init(getContext(this) as common.UIAbilityContext,this.clientId,this.authKey) 

}catch (e){ 

let err:Error =e 

console.log(err.message) 

} 

} 

HqPdfView 组件和 OperateController 对象 

# HqPdfView 组件属性列表 

属性 

类型 

功能 

controller 

OperateController 

组件控制器 

onEditText 

回调函数,参数 objectId :当前操作的文本对象 id , textContent :当 前文本对象文本内容, fontColor: 文本颜色 文本编辑时回调 

solidResult 

回调函数,参数 success : boolean 类型, pdf 是否保存成功, msg : 失败时,失败原因 

保存 pdf 成功回调 

pdfPath 

string 类型,需要打开编辑的 pdf 文件绝对路径 

pdf 路径 

onPageChange 

回调函数,参数 currentPage :当前页码 

返回当前页页码 

OperateController 方法列表 

名称 

参数 

功能 

addImage(path) 

path :图片绝对路径 

向当前 pdf 页,插入图片对象 

addSign() 

打开签名管理界面,向当前 pdf 页,插入签名对象 

addText(textContent,fontColor) 

textContent :文本内容, fontColor :文本颜色 

向当前 pdf 页,插入文本对象 

editText(objectId,textContent,fontColor) 

objectId :当前文本对象 id , textContent :新修改文本内容, fontColor :新修改文本颜色 

重新编辑文本对象 

solidFile() 

保存当前 pdf ,注意:保存结果 HqPdfView 组件的 solidResult 回调返回 

clearCurrentPageHandwriting() 

圈批模式下,清除当前页所有的圈批内容 

showSignInfo() 

展示当前 pdf 文件已保存的签批信息(使用好签 

# 工具保存的数据) 

setStrokeColor(strokeColor) 

strokeColor :圈批笔迹颜色 

设置圈批笔迹颜色 

getCurrentStrokeColor() 

获取当前圈批笔迹颜色 

setStrokeThickness(strokeThickness) 

strokeThickness :圈批笔迹粗细 

设置圈批笔迹粗细 

getCurrentStrokeThickness() 

# 获取当前圈批笔迹粗细 

changeOperateType(operateType) 

operateType : OperateType 类型,更改操作种类 

更改当前操作种类(普通,圈批,橡皮擦) 

使用示例 

```arkts
import { LoadingDialog, router } from '@kit.ArkUI'; 
import { photoAccessHelper } from '@kit.MediaLibraryKit'; 
import { common } from '@kit.AbilityKit'; 
import { fileUri, fileIo as fs } from '@kit.CoreFileKit'; 
```

import { HqPdfView, OperateController ,OperateType} from '@wellsign/pdfsdk'; 

import { TextInputDialog } from '../dialog/TextInputDialog'; 

import { StrUtil, ToastUtil } from '@pura/harmony-utils'; import { StrokeSetDialog } from '../dialog/StrokeSetDialog'; 

controller: OperateController = new OperateController(); 

inputDialogController: CustomDialogController | null = new CustomDialogController({ 

builder: TextInputDialog({ 

inputContent: this.inputContent, 

selectColor: this.textSelectColor, 

onConfirm: () => { 

if (StrUtil.isEmpty(this.textObjectId)) { 

this.controller.addText(this.inputContent, this.textSelectColor) 

} else { 

this.controller.editText(this.textObjectId, this.inputContent, this.textSelectColor) 

} 

} 

}), 

autoCancel: true, 

onWillDismiss: (dismissDialogAction: DismissDialogAction) => { 

if (dismissDialogAction.reason == DismissReason.PRESS_BACK) { 

dismissDialogAction.dismiss() 

} 

if (dismissDialogAction.reason == DismissReason.TOUCH_OUTSIDE) { 

dismissDialogAction.dismiss() 

} 

}, 

backgroundColor: Color.White, 

isModal: true, 

alignment: DialogAlignment.Bottom, 

cornerRadius: { 

topLeft: 0, topRight: 0, bottomLeft: 0, 

bottomRight: 0 

}, 

width: '100%', 

customStyle: true, 

}) 

strokeDialogController: CustomDialogController | null = new CustomDialogController({ 

builder: StrokeSetDialog({ 

strokeThickness: this.strokeThickness, 

selectColor: this.strokeSelectColor, 

onConfirm: () => { 

this.controller.setStrokeColor(this.strokeSelectColor) this.controller.setStrokeThickness(this.strokeThickness) 

} 

}), 

autoCancel: true, 

onWillDismiss: (dismissDialogAction: DismissDialogAction) => { 

if (dismissDialogAction.reason == DismissReason.PRESS_BACK) { dismissDialogAction.dismiss() 

} 

if (dismissDialogAction.reason == DismissReason.TOUCH_OUTSIDE) { 

dismissDialogAction.dismiss() 

} 

}, 

backgroundColor: Color.White, 

isModal: true, 

alignment: DialogAlignment.Bottom, 

cornerRadius: { 

topLeft: 0, 

topRight: 0, 

bottomLeft: 0, bottomRight: 0 }, offset:{ dx:0, dy:-55 }, width: '80%', customStyle: true, }) ... ... 

HqPdfView({ pdfPath: this.pdfPath, controller: this.controller, 

onEditText: (objectId, textContent, fontColor) => { this.inputContent = textContent this.textSelectColor = fontColor this.textObjectId = objectId this.inputDialogController?.open() 

}, 

solidResult: (success, msg) => { 

this.loadingDialog.close() 

if (success) { 

router.back() 

}else{ 

ToastUtil.showToast(msg) 

} 

} 

}) 

... 

... 

RelativeContainer() 

{ 

Flex({ direction: FlexDirection.Row, alignItems: ItemAlign.Center, justifyContent: FlexAlign.SpaceAround }) { 

Column() { 

Image($r('app.media.icon_sign')).width(25).height(25) 

Text(' 签名 ').fontSize(14).fontColor(Color.White) 

} 

.onClick((e) => { 

this.controller.addSign() 

}); 

# Column() { 

Image($r('app.media.icon_image')).width(25).height(25) Text(' 图片 ').fontSize(14).fontColor(Color.White) 

} 

.onClick((e) => { 

this.insertImage(); 

}); 

Column() { 

Image($r('app.media.icon_text')).width(25).height(25) Text(' 文本 ').fontSize(14).fontColor(Color.White) 

} 

.onClick((e) => { 

this.insertText(); 

}); 

Column() { 

Image($r('app.media.icon_stroke')).width(25).height(25) Text(' 圈批 ').fontSize(14).fontColor(Color.White) 

} 

.onClick((e) => { 

this.operateType = OperateType.Pen 

this.controller.changeOperateType(this.operateType) 

}); 

Column() { 

Image($r('app.media.icon_more')).width(25).height(25) 

Text(' 验签 ').fontSize(14).fontColor(Color.White) 

} 

.onClick((e) => { 

this.controller.showSignInfo() 

}); 

} 

. 

backgroundColor($r('app.color.main_blue_color')) 

.visibility(this.operateType == OperateType.Touch ? Visibility.Visible : Visibility.Hidden) 

.width('100%') 

.height('100%') 

Flex({ direction: FlexDirection.Row, alignItems: ItemAlign.Center, justifyContent: FlexAlign.SpaceEvenly }) { 

Text(' 退出圈批 ').fontSize(18).onClick((e) => { 

this.operateType = OperateType.Touch 

this.controller.changeOperateType(this.operateType) 

}); 

Text(' 设置 ').fontSize(18).onClick((e) => { 

if(this.operateType!=OperateType.Pen){ 

this.operateType = OperateType.Pen 

this.controller.changeOperateType(this.operateType) 

return 

} 

this.strokeSelectColor =this.controller.getCurrentStrokeColor() this.strokeThickness = this.controller.getCurrentStrokeThickness() this.strokeDialogController?.open() 

}); 

Text(' 橡皮擦 ').fontSize(18).onClick((e) => { 

this.operateType = OperateType.Eraser 

this.controller.changeOperateType(this.operateType) 

}); 

Text(' 清除 ').fontSize(18).onClick((e) => { 

this.controller.clearCurrentPageHandwriting() 

}); 

}.visibility(this.operateType!= OperateType.Touch ? Visibility.Visible : Visibility.Hidden) 

.width('100%') 

.height('100%') 

... 

... 

insertText() 

{ 

this.inputContent = '' 

this.textObjectId = '' 

this.inputDialogController?.open() 

} 

private async insertImage() 

{ 

let context = getContext(this) as common.Context; 

let PhotoSelectOptions = new photoAccessHelper.PhotoSelectOptions(); 

PhotoSelectOptions.MIMEType = photoAccessHelper.PhotoViewMIMETypes.IMAGE_TYPE; 

PhotoSelectOptions.maxSelectNumber = 1; 

let photoPicker = new photoAccessHelper.PhotoViewPicker(); 

let promise = photoPicker.select(PhotoSelectOptions); 

let result = await promise; 

let uris = result.photoUris; if (uris.length > 0) { 

let file = fs.openSync(uris[0], fs.OpenMode.READ_ONLY); 

let imagePath = context.cacheDir + '/' + file.name; 

# // 如果有旧文件就删除 

try { 

fs.accessSync(imagePath); 

fs.unlinkSync(imagePath); 

} catch (err) { 

} 

let dstUri = fileUri.getUriFromPath(imagePath); await fs.copy(uris[0], dstUri); 

try { 

this.controller.addImage(imagePath) 

} catch (e) { 

let err : 

Error = e 

console.log(err.message) 

} 

} 

} 

HqTool 接口 HqTool 方法列表 

名称 

参数 

# 功能 

getPageCount(pdfPath,password) 

pdfPath : pdf 文件绝对路径, password :默认值为空, pdf 密码 获取指定路径 pdf 文件的页数 

checkNeedsPassword(pdfPath) 

pdfPath : pdf 文件绝对路径 检查 pdf 是否需要密码
