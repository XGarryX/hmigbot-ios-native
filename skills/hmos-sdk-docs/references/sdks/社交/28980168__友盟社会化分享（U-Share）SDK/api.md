# 社会化分享 SDK 接口调用说明 

SDK 方法(微信) 

前置检查 

确保已按照快速开始文档的各步骤安装集成成功。 

在需要使用的页面中按需使用分享功能,获取包签名可参见微信鸿蒙 文档 目前仅支持微信端的分享和登录功能,可参见微信分享说明 

功能说明 

一、判断是否安装微信 

需要先在 module.json5 增加如下固定配置 

调用微信安装的方法 

import { WX } from "@umeng/share"; 

WX.isInstalled((obj: object) => { 

// obj.isInstalled 为 true 表示微信已安装 

console.warn(` 安装微信回调 : ${JSON.stringify(obj)}`); 

}); 

二、分享面板 

分享面板组件可在 UI 页面中按需使用,控制是否展示。 

ShareBoard 分享面板组件。 

visible 可选,若配置则分享或取消会自动关闭面板,若配置则根据开 发者限制面板的显示状态,不会自动关闭。 

confirm 必选,表示点击面板的类型如微信图标后的回调, wxsession 

表示分享到微信平台,用户可在确认分享的回调中调用分享的方法。 cancel 必须,分享面板点击取消的回调。 

import { WX, ShareBoard, wxConfig } from "@umeng/share"; 

ShareBoard({ 

visible: this.visible, // 可选,若不传则分享或取消会自动关闭面板, 若传则根据开发者限制面板的显示状态,不会自动关闭。 

confirm: (pl: string) => { 

// pf 表示分享的应用平台 

if (pl === 'wxsession') { // wxsession 分享到微信好友会话 

const config: wxConfig.TextObject = { 

"scene": 'wxsession', 

"text": " 分享文本文本文本 ~", 

}; 

WX.shareText(config, (obj: object) => { 

console.warn(` 文本回调 : ${JSON.stringify(obj)}`); 

}); 

}; 

if (pl === 'wxtimeline') { // wxtimeline 分享到微信朋友圈 

const config: wxConfig.TextObject = { 

"scene": 'wxtimeline', 

"text": " 分享文本到微信朋友圈 ~", 

}; 

WX.shareText(config, (obj: object) => { 

console.warn(` 文本回调 : ${JSON.stringify(obj)}`); 

}); 

}; 

}, 

cancel: () => { 

this.visible = false; 

console.log(' 取消分享了 '); 

}, 

}); 

三、分享文本 

分享文本到微信,文本限制大于 0 且不超过 10K ,不可都是空。 

scene 表示分享到微信的类型, wxtimeline 是分享到朋友圈, wxsession 是分享到好友会话,默认好友会话。 

import { WX, wxConfig } from "@umeng/share"; 

# // 分享文本到微信会话或朋友圈 

const config: wxConfig.TextObject = { 

"scene": 'wxtimeline', 

"text": " 分享文本文本文本 ~", 

}; 

WX.shareText(config, (obj: object) => { 

console.warn(` 文本回调 : ${JSON.stringify(obj)}`); 

}); 

四、分享图片 

# 分享图片到微信 

注意:缩略图 imageUri 和 imageData 为二选一,如果都配置了则仅会 生效 imageUri 。 

scene 表示分享到微信的类型, wxtimeline 是分享到朋友圈, wxsession 是分享到好友会话,默认好友会话。 

imageUri 可选,图片本地路径的 uri 。支持 jpeg/png 类型的图片,图片 限制 25M 。 

imageData 可选,图片二进制数据的 base64 字符串,限制 64KB 以内。 

callbackAbility 可选,表示分享后返回应用打开的 ability 名称,开发 者应用内配置可能会影响实际生效。 

import { WX, wxConfig } from "@umeng/share"; // 引用 share sdk 

// 调用 sdk 分享 

const config: wxConfig.ImageObject = { 

"scene": 'wxtimeline', // 分享到会话或朋友圈 

"imageUri": uri, 

// "imageData": imgData, 

"callbackAbility": "EntryAbility" 

}; 

WX.shareImage(config, (obj: object) => { 

console.warn(` 图片回调 : ${JSON.stringify(obj)}`); 

# }); 

# 获取 uri 分享 

uri 分享手机相册照片分享和本地路径图片方式,限制图片 25M 。 分享手机相册图片的 uri 代码示例如下: 

import common from '@ohos.app.ability.common'; 

```arkts
import { fileIo as fs, fileUri } from '@kit.CoreFileKit'; 
import { photoAccessHelper } from '@kit.MediaLibraryKit'; 
```

// 选取相册照片示例,得到返回的 uri 调用分享图片方法 

async getPictureUriFromAlbum(type: 'video'|'image'): Promise<string[]> { 

let PhotoSelectOptions = new photoAccessHelper.PhotoSelectOptions(); 

if (type === 'video') { 

PhotoSelectOptions.MIMEType = photoAccessHelper.PhotoViewMIMETypes.VIDEO_TYPE; 

PhotoSelectOptions.maxSelectNumber = 1; 

} else { 

PhotoSelectOptions.MIMEType = photoAccessHelper.PhotoViewMIMETypes.IMAGE_TYPE; 

PhotoSelectOptions.maxSelectNumber = 1; 

} 

let photoPicker = new photoAccessHelper.PhotoViewPicker(); 

let photoSelectResult: photoAccessHelper.PhotoSelectResult = 

await photoPicker.select(PhotoSelectOptions); 

let selectPhoto = photoSelectResult.photoUris; 

console.warn(` 选中的图片 : ${JSON.stringify(selectPhoto)}`); 

// 将选中的图片转 uri 路径 

let albumPath = selectPhoto[0]; 

let context = getContext(this) as common.UIAbilityContext; 

```arkts
let filePath = `${context.filesDir}/original-${Date.now()}.${type === 'video' ? 'mp4' : 'jpg'}`; 
```

let file: fs.File | undefined; 

file = fs.openSync(albumPath, fs.OpenMode.READ_ONLY); 

fs.copyFileSync(file.fd, filePath); 

fs.closeSync(file); 

let uri: string = fileUri.getUriFromPath(filePath); // uri 路径 

return uri; 

}; 

分享本地路径沙箱图片 uri 示例如下: 

```arkts
import { fileIo as fs, fileUri } from '@kit.CoreFileKit'; 
```

// 可选,相册照片分享示例,获取 uri 后调用 sdk 方法。 

const uri = await this.getPictureUriFromAlbum('image'); 

console.warn('uri', uri); 

获取 imageData 分享 

imageData 可以是本地路径图片,也可以是网络链接图片,只要将图 

片转为 ArrayBuffer 的 base64 字符串格式即可,限制 64KB 。 

示例代码如下: 

import { image } from '@kit.ImageKit'; 

import buffer from '@ohos.buffer'; 

// 可选,使用 imageData 分享图片示例,获取 imgData 后调用 sdk 方法 分享图片。 

// const resourceManager = getContext(this).resourceManager; 

// const imageArray = await resourceManager.getMediaContent($r('app.media.app_icon')); 

// const data1: ArrayBuffer = imageArray.buffer as ArrayBuffer; 

// const imageResource = image.createImageSource(data1); 

// const imagePixelMap: image.PixelMap = imageResource.createPixelMapSync(); 

// const imagePackerApi: image.ImagePacker = image.createImagePacker(); // 创建 ImagePacker 实例,用于图片压 缩和编码。 

// const data: ArrayBuffer = await imagePackerApi.packing(imagePixelMap, { format: 'image/jpeg', quality: 100 }); 

// const buf: buffer.Buffer = buffer.from(data); // data 是压缩的 图,也可用 data1 原始图 

// const imgData: string = buf.toString('base64', 0, buf.length); 

// // console.warn(`imgData: ${imgData}`); 

五、分享网页链接 

分享网页链接到微信: 

注意:缩略图 imageUrl 和 imageData 为二选一,如果都配置了则仅会 生效 imageUrl 。缩略图限制 64KB 内,超出大小会忽略缩略图的展 示。 

scene 可选,表示分享到微信的类型, wxtimeline 是分享到朋友圈, wxsession 是分享到好友会话,默认好友会话。 

webpageUrl 必填,网页链接地址。 

title 必填,网页链接名称。 

description 可选,网页摘要说明。 

imageUrl 可选,网页缩略图(网络图片链接地址), 64KB 以内。 

imageData 可选,网页缩略图(图片二进制数据), 64KB 以内。 

callbackAbility 可选,表示分享后返回应用打开的 ability 名称,开发 者应用内配置可能会影响生效。 

import { WX, wxConfig } from "@umeng/share"; 

// 可选,获取 imageData 示例,注意 imageData 是 ArrayBuffer 类型, 而不是二进制字符串格式 

// const resourceManager = getContext(this).resourceManager; 

// const imageArray = await resourceManager.getMediaContent($r('app.media.app_icon')); 

// const imgData: ArrayBuffer = imageArray.buffer as ArrayBuffer; 

# // 调用分享 

const config: wxConfig.WebPageObject = { 

"scene": 'wxtimeline', // 分享到会话或朋友圈 

"webpageUrl": "https://www.umeng.com/", 

"title": " 测试 qq 网页链接 ", 

"description": " 测试 qq 网页摘要 ", 

// "imageUrl": "https://img.alicdn.com/imgextra/i2/ O1CN01OQQ7ec1MNmf3xFWAX_!!6000000001423-2tps-96-96.png", 

"imageData": imgData, 

"callbackAbility": "EntryAbility" 

}; 

WX.shareWebPage(config, (obj: object) => { 

console.warn(` 网页回调 : ${JSON.stringify(obj)}`); 

}); 

六、分享小程序 

分享小程序到微信: 

注意:缩略图 imageUrl 和 imageData 为二选一,如果都配置了则仅会 生效 imageUrl 。缩略图限制 64KB 内,超出大小会忽略缩略图的展 示。 

userName 必填,小程序的原始 id (gh_xxxx 形式的 id ) 

path 必填,小程序的 path 。 

title 必填,小程序的标题名称。 

description 可选,小程序描述。 

miniprogramType 可选,小程序的类型,默认正式版 0, 测试版 1, 预览 版 2 。 

withShareTicket 可选,是否使用带 shareTicket 的分享。可以设置 withShareTicket 为 true ,当分享卡片在群聊中被其他用户打开时, 可以获取到 shareTicket ,用于获取更多分享信息。 

imageUrl 可选,小程序缩略图(网络图片链接地址), 64KB 以内。 

imageData 可选,小程序缩略图(图片二进制数据), 64KB 以内。 

callbackAbility 可选,表示分享后返回应用打开的 ability 名称,开发 者应用内配置可能会影响生效。 

import { WX, wxConfig } from "@umeng/share"; 

// 可选,获取 imageData 示例,注意 imageData 是 ArrayBuffer 类型, 而不是二进制字符串格式 

// const resourceManager = getContext(this).resourceManager; 

// const imageArray = await resourceManager.getMediaContent($r('app.media.app_icon')); 

// const imgData: ArrayBuffer = imageArray.buffer as ArrayBuffer; 

# // 调用分享 

const config: wxConfig.MiniProgramObject = { 

"userName": 'gh_ddab9f37054f', 

"path": 'udopkg/home/home', 

"miniprogramType": 0, 

"title": " 友小萌小程序 Title", 

"description": " 友小萌小程序描述信息 ", 

// "imageUrl": "https://img.alicdn.com/imgextra/i2/ O1CN01OQQ7ec1MNmf3xFWAX_!!6000000001423-2tps-96-96.png", 

"imageData": imgData, 

"callbackAbility": "EntryAbility2" 

}; 

WX.shareMiniProgram(config, (obj: object) => { 

console.warn(` 小程序回调 : ${JSON.stringify(obj)}`); 

}); 

七、分享视频 

# 分享视频到微信: 

注意:缩略图 imageUrl 和 imageData 为二选一,如果都配置了则仅会 生效 imageUrl 。缩略图限制 64KB 内,超出大小会忽略缩略图的展 示,推荐使用 png/jpg 格式图片。 

scene 可选,表示分享到微信的类型, wxtimeline 是分享到朋友圈, wxsession 是分享到好友会话,默认好友会话。 

分享到好友会话时: 

videoUrl 必填,视频链接地址,限制长度不超过 10KB 。 

videoLowBandUrl 可选,视频链接地址。供低带宽的环境下使用的视 频链接,限制长度不超过 10KB 。 

title 可选,标题。 

description 可选,描述。 

imageUrl 可选,视频封面图(网络图片链接地址), 64KB 以内。 

imageData 可选,视频封面图(图片二进制数据), 64KB 以内。 

callbackAbility 可选,表示分享后返回应用打开的 ability 名称,开发 者应用内配置可能会影响生效。 

分享到朋友圈时: 

videoUri 必填,视频 uri 格式地址。 

imageUrl 可选,视频封面图(网络图片链接地址), 64KB 以内。 

imageData 可选,视频封面图(图片二进制数据), 64KB 以内。 import { WX, wxConfig } from "@umeng/share"; 

# // 调用分享 

// 可选,相册照片分享示例,获取 uri 后调用 sdk 方法。 

const uri = await this.getPictureUriFromAlbum('video'); 

console.warn('uri', uris); 

const config: wxConfig.VideoObject = { 

"scene": 'wxtimeline', // 分享到会话或朋友圈 

"videoUri": uri, 

// "videoUrl": "https://video.umeng.com/college/ 

// "videoLowBandUrl": "https://video.umeng.com/college/ 

// "title": " 标题 xxx", 

// "description": " 描述 xxx", 

// "imageUrl": "https://img.alicdn.com/imgextra/i2/ O1CN01OQQ7ec1MNmf3xFWAX_!!6000000001423-2tps-96-96.png", 

// "imageData": imgData, 

// "callbackAbility": "EntryAbility" 

}; 

WX.shareVideo(config, (obj: object) => { 

console.warn(` 视频回调 : ${JSON.stringify(obj)}`); 

}); 

八、调用微信登录 

微信授权登录让微信用户使用微信身份登录第三方应用或网站,在微 信用户授权登录已接入微信的第三方应用后,第三方可以获取到用户 的接口调用凭证( access_token ),通过 access_token 可以进行微信 开放平台授权关系接口调用,从而可实现获取微信用户基本开放信息 和帮助用户实现基础开放功能等。 

目前移动应用上微信登录只提供原生的登录方式,需要用户安装微信 客户端才能配合使用。 

友盟 sdk 微信登录方法仅在获取到 access_token 后即返回到开发者,再 由开发者通过 access_token 调用获取用户信息的 /sns/userinfo 接口取 值。 

参见微信登录功能文档,登录方法返回其中第二步的值即结束。 

import { WX } from "@umeng/share"; 

WX.login((obj: object) => { 

// 返回 access_token 和 openid 等信息,用于开发者调取微信 api 获取微 信个人信息 

console.warn(` 开发者调用登录回调 : ${JSON.stringify(obj)}`); 

}); 

# SDK 方法(微博) 

# 前置检查 

本文介绍微博的分享和登录功能,参见微博分享说明、微博移动端接 入文档,微博常见问题文档。 

确保已在微博开放平台创建应用,且审核通过,签名可调用 

# Weibo.getSign() 方法查看。 

@umeng/share 从 1.1.5 版本支持微博,确保已按照快速开始文档的各 步骤安装集成成功。 

功能说明 

一、判断微博是否安装 

需要先在 module.json5 增加如下 sinaweibo 固定配置, 

调用微博方法 

import { Weibo } from "@umeng/share"; 

// 须先在应用的 module.json5 文件中先配置 querySchemes: ["sinaweibo"] 

Weibo.isInstalled((data: Record<string, string>) => { 

// obj.isInstalled 为 true 表示已安装 

console.warn(` 微博是否安装 : ${JSON.stringify(data)}`); 

}); 

二、分享面板 

分享面板组件可在 UI 页面中按需使用,控制是否展示。 

ShareBoard 分享面板组件。 

visible 可选,若配置则分享或取消会自动关闭面板,若配置则根据开 发者限制面板的显示状态,不会自动关闭。 

confirm 必选,点击面板的确认分享回调。 “weibo” 表示分享到微博平 台。 

cancel 必选,分享面板点击取消的回调。 

import { ShareBoard, Weibo, weiboConfig } from "@umeng/share"; 

ShareBoard({ 

visible: this.visible, // 可选,若不传则分享或取消会自动关闭面板, 若传则根据开发者限制面板的显示状态,不会自动关闭。 

confirm: (pl: string) => { 

if (pl === 'weibo') { // 分享的应用平台, weibo 表示分享到微博 

// 如下以分享文本到微博为例 

const config: weiboConfig.TextObject = { 

"text": " 友盟分享 SDK 支持 sina 微博的登录和分享功能了 ~", 

}; 

Weibo.shareText(config, (obj: object) => { 

console.warn(` 文本回调 : ${JSON.stringify(obj)}`); 

}); 

}; 

}, 

cancel: () => { 

this.visible = false; 

console.log(' 取消分享了 '); 

}, 

}); 

三、分享文本 

# 分享纯文本到微博,文本限制 5000 个字符,不可为空。 

import { Weibo, weiboConfig } from "@umeng/share"; 

const config: weiboConfig.TextObject = { 

text: ' 分享文本到微博 ~' 

}; 

Weibo.shareText(config, (obj: Record<string, string>) => { console.warn(` 分享文本的返回: ${JSON.stringify(obj)}`); 

# }); 

四、分享图片 

# 分享图片或图文到微博。 

注意:图片仅支持 uri 格式,且每次分享对多限制 18 张图片。 text 可选,文本限制 5000 个字符以内。 

uris 必选,图片 uri 格式的数组集合。支持 png/jpg 格式,大小不限。 

import { Weibo, weiboConfig } from "@umeng/share"; 

const uris: string[] = []; // ["file://com.umeng.hm.share/data/ storage/el2/base/haps/entry/files/original-1766137214639.jpg"] 

// 或者以从相册选取照片为例,参见文档下方 getPictureUriFromAlbum 方法调试。 

// const uris: string[] = await this.getPictureUriFromAlbum('image'); 

const config: weiboConfig.ImageObject = { 

text: ' 分享图片的文本说明 ~', 

uris: uris, 

}; 

Weibo.shareMultiImage(config, (obj: Record<string, string>) => { console.warn(` 分享图片的返回: ${JSON.stringify(obj)}`); 

# }); 

五、分享视频 

分享视频到微博,可设置文本、视频地址、封面图,仅支持 uri 格式。 text 可选,文本限制 5000 个字符以内。 

videoUri 必选,视频的 uri 格式字符串,大小不限。(建议分享视频不 超过 2G ) coverUri 可选,视频的封面图地址, uri 格式字符串,大小不限。 

import { Weibo, weiboConfig } from "@umeng/share"; 

const uri: string[] = []; // await this.getPictureUriFromAlbum('video'); 

const config: weiboConfig.VideoObject = { 

text: ' 分享视频的描述 ~', 

videoUri: uri[0], 

// coverUri: "file://com.umeng.hm.share/data/storage/el2/base/ haps/entry/files/original-1765264648540.jpg", 

}; 

Weibo.shareVideo(config, (obj: Record<string, string>) => { console.warn(` 分享视频的返回: ${JSON.stringify(obj)}`); 

# }); 

# 六、微博登录 

微博登录提供 SSO 授权、 SSO 授权(客户端)、 SSO 授权( WEB )三 种登录方式。 

微博授权登录让用户使用微博身份登录第三方应用或网站,在微博登 录授权后,第三方可以获取到用户的接口调用凭证( access_token 、 uid ),通过 access_token 和 uid 发起 get 请求调用 (https:// api.weibo.com/2/users/show.json? 

接口,即可获得用户的微博账号信息。 

import { Weibo } from "@umeng/share"; 

# // SSO 授权登录 

Weibo.authorize((data: Record<string, string>) => { 

console.warn(`SSO 授权返回 : ${JSON.stringify(data)}`); 

# }); 

# // SSO 授权登录(客户端) 

Weibo.authorizeClient((data: Record<string, string>) => { console.warn(`SSO 授权(客户端)返回 : ${JSON.stringify(data)}`); 

# }); 

# // SSO 授权登录( WEB ) 

Weibo.authorizeWeb((data: Record<string, string>) => { console.warn(`SSO 授权( WEB )返回 : ${JSON.stringify(data)}`); 

}); 

# 七、其他参考方法 

从手机相册选取照片,返回 uris 的示例方法,从开发调试时参考。 

import common from '@ohos.app.ability.common'; 

```arkts
import { fileIo as fs, fileUri } from '@kit.CoreFileKit'; 
import { photoAccessHelper } from '@kit.MediaLibraryKit'; 
```

// 选取相册照片示例,返回选中图片 uri 的数组格式,即 uris 。 

async getPictureUriFromAlbum(type: 'video'|'image'): Promise<string[]> { 

let PhotoSelectOptions = new photoAccessHelper.PhotoSelectOptions(); 

if (type === 'video') { 

PhotoSelectOptions.MIMEType = photoAccessHelper.PhotoViewMIMETypes.VIDEO_TYPE; 

PhotoSelectOptions.maxSelectNumber = 1; 

} 

if (type === 'image') { 

PhotoSelectOptions.MIMEType = photoAccessHelper.PhotoViewMIMETypes.IMAGE_TYPE; 

PhotoSelectOptions.maxSelectNumber = 18; 

} 

let photoPicker = new photoAccessHelper.PhotoViewPicker(); 

let photoSelectResult: photoAccessHelper.PhotoSelectResult = await photoPicker.select(PhotoSelectOptions); 

let selectPhoto = photoSelectResult.photoUris; 

console.warn(` 选中的图片 : ${JSON.stringify(selectPhoto)}`); 

// 将选中的图片转 uri 路径 

const allPath: string[] = selectPhoto.reduce((m: string[], itemPath) => { 

let albumPath = itemPath; 

let context = getContext(this) as common.UIAbilityContext; 

```arkts
let filePath = `${context.filesDir}/original-${Date.now()}.${type === 'video' ? 'mp4' : 'jpg'}`; 
```

let file: fs.File | undefined; 

file = fs.openSync(albumPath, fs.OpenMode.READ_ONLY); 

fs.copyFileSync(file.fd, filePath); 

fs.closeSync(file); 

let uri: string = fileUri.getUriFromPath(filePath); // uri 路径 

m.push(uri); 

return m; 

}, []); 

console.log(` 选中的图片 uri 地址 : ${JSON.stringify(allPath)}`); 

return allPath; 

} 

生成签名,用于微博开放平台创建应用时使用。 

import { Weibo } from "@umeng/share"; 

# // 生成签名 

Weibo.getSign().then(sign => { 

console.warn('get sign : ' + sign); 

}); 

SDK 方法( QQ ) 

# 前置检查 

本文介绍 QQ 的分享和登录功能,可参见 QQ 鸿蒙接入指南、 QQ 接口 说明、 QQ 鸿蒙常见问题文档。 

确保已在 QQ 互联平台创建应用,且审核通过。 

@umeng/share 从 1.1.8 版本支持 QQ ,确保已按照快速开始文档的各 步骤安装集成成功。 

module.json5 配置文件如下修改,可参见 QQ 环境搭建说明。 

// module.json5 的 "module" 节点下配置 querySchemes 

"querySchemes": [ 

"https", 

"qqopenapi" 

] 

// 在 Ability 的 skills 节点中配置 scheme 

"skills": [ 

{ 

"entities": [ 

"entity.system.browsable" 

], 

"actions": [ 

"ohos.want.action.viewData" 

], 

"uris": [ 

{ 

"scheme": "qqopenapi", // 接收 QQ 回调数据 

"host": "1112396455", // 业务申请的互联 appId ,如果填错会导致 QQ 无法回调 

"pathRegex": "\\b(auth|share)\\b", 

} 

] 

} 

] 

可选, QQ 互联平台的 applinking 校验,可参见下图示例,在鸿蒙开发 者平台去配置后,再填写到互联开放平台校验,若 QQ 互联平台未校 验 applinking 会导致无法调用登录功能。 

# 功能说明 

一、判断 QQ 是否安装 

import { QQ } from "@umeng/share"; 

# // 判断 QQ 是否安装方法 

// 注意:须先在应用的 module.json5 文件中先配置 querySchemes: ["https", "qqopenapi"] 

QQ.isInstalled((data: Record<string, string>) => { 

console.warn(`qq 是否安装 : ${JSON.stringify(data)}`); 

# }); 

二、分享面板 

分享面板组件可在 UI 页面中按需使用,控制是否展示。 

ShareBoard 分享面板组件。 

visible 可选,若配置则分享或取消会自动关闭面板,若配置则根据开 发者限制面板的显示状态,不会自动关闭。 

confirm 必选,点击面板的确认分享回调。 "qq" 表示分享 QQ 好 友, "qzone" 表示分享 QQ 空间。 

cancel 必选,分享面板点击取消的回调。 

import { ShareBoard, QQ, qqConfig } from "@umeng/share"; 

ShareBoard({ 

visible: this.visible, // 可选,若不传则分享或取消会自动关闭面板, 若传则根据开发者限制面板的显示状态,不会自动关闭。 

confirm: (pl: string) => { 

if (pl === 'qq') { // 分享到 QQ 好友 

// 如下以分享网页链接为例 

const params: qqConfig.WebPageObject = { 

"msg_style": 0, // 固定值 

"title": " 鸿蒙 ArkTS 分享 ", // 必传 

"summary": "qq 互联 sdk 分享到好友 ", 

"brief": " 互联分享 ", 

"url": "https://devs.umeng.com/", // 必传 

// 图片若不传,则使用的是应用的图标 

"picture_url": "https://img.alicdn.com/imgextra/i1/ O1CN016IZkgf1bbj0hS3IsD_!!6000000003484-2tps-1080-1080.png" 

}; 

QQ.shareWebPage(params, (obj: Record<string, string>) => { console.warn(` 分享网页的返回: ${JSON.stringify(obj)}`); 

# }); 

}; 

if (pl === 'qzone') { // 分享到 QQ 空间 

// 。。。。 

} 

}, 

cancel: () => { 

this.visible = false; console.log(' 取消分享了 '); 

}, 

}); 

三、分享网页链接(好友) 

分享网页链接到 QQ 好友,即 QQ 文档中的图文消息。 

# title 大小限制 10KB 内。 

import { QQ, qqConfig } from "@umeng/share"; 

const params: qqConfig.WebPageObject = { 

"msg_style": 0, // 必传,传固定值 0 即可 

"title": " 鸿蒙 ArkTS 分享 ", // 必传,网页链接的标题 

"summary": "qq 互联 sdk 分享到好友 ", // 可选,网页链接的摘要 

"brief": " 互联分享 ", // 可选 

"url": "https://devs.umeng.com/", // 必传,网页链接地址 

// 可选,网页链接图标 

// 图片若不传,则使用的是应用的图标 

"picture_url": "https://img.alicdn.com/imgextra/i1/ O1CN016IZkgf1bbj0hS3IsD_!!6000000003484-2tps-1080-1080.png" 

}; 

QQ.shareWebPage(params, (obj: Record<string, string>) => { console.warn(` 分享网页的返回: ${JSON.stringify(obj)}`); 

}); 

四、分享图片(好友) 

分享图片到 QQ 好友,即 QQ 文档中的大图消息。 注意:分享图片限制 条件: 图片仅支持 uri 格式,如果传多张图片,只取列表中的第 1 张; 图片格式:目前只支持 png 、 jpeg 、 gif 、 bmp 、 webp 格式的图片; 

图片文件大小:只支持小于等于 32M 的图片; 

图片分辨率:图片宽、高分别限制 30000 像素,总像素限制 250000000 。 

import { QQ, qqConfig } from "@umeng/share"; 

const uris: string[] = []; // ["file://com.umeng.hm.share/data/ storage/el2/base/haps/entry/files/original-1766137214639.jpg"] 

// 或者以从相册选取照片为例,参见文档下方 getPictureUriFromAlbum 方法调试。 

// const uris: string[] = await this.getPictureUriFromAlbum('image'); 

const params: qqConfig.ImageObject = { 

"msg_style": 6, // 必填,传固定值 6 即可 

"share_uris": uris, // 必填, uri 格式图片地址,数组类型。如果传多 张图片,只取列表中的第 1 张。 

}; 

QQ.shareImage(params, (obj: Record<string, string>) => { console.warn(` 分享图片的返回: ${JSON.stringify(obj)}`); 

}); 

五、分享网页链接(空间) 

分享网页链接到 QQ 空间,即 QQ 文档中的图文消息。 

title 大小限制 10KB 内。 

import { QQ, qqConfig } from "@umeng/share"; 

const params: qqConfig.ZoneWebPageObject = { 

"title": " 鸿蒙 ArkTS 分享 ", // 必传,网页链接的标题 

"summary": "qq 互联 sdk 分享到空间 ", // 可选,网页链接的摘要 

"targetUrl": "https://devs.umeng.com/", // 必传,网页链接地址 

// 可选,网页链接图标列表 

// 首张图即是封面链接(仅支持网络图片链接) 

"imageUrls": [ 

"https://img.alicdn.com/imgextra/i1/O1CN016IZkgf1bbj0hS3IsD_!! 6000000003484-2-tps-1080-1080.png", 

"https://img.alicdn.com/imgextra/i2/ O1CN01OQQ7ec1MNmf3xFWAX_!!6000000001423-2tps-96-96.png", 

], 

}; 

QQ.shareZoneWebPage(params, (obj: Record<string, string>) => { 

console.warn(` 分享空间的返回: ${JSON.stringify(obj)}`); 

}); 

六、 QQ 登录 

QQ 登录要确保在 QQ 互联平台的 applinking 校验通过,在鸿蒙开发者 平台去配置后,再填写到互联开放平台校验。 

import { QQ, qqConfig } from "@umeng/share"; 

let obj: qqConfig.LoginReqOptions = { 

"scope": "all", // 可选。申请授权权限列表 , 默认值为 "all" 

"forceWebLogin": false, // 可选。是否强制使用网页登录 , 默认 false 

"useQrCode": false, // 可选。是否使用扫码登录 ( 仅在 forceWebLogin 为 true 时生效 ) ,默认 false 

"networkTimeout": 0, // 可选。配置 sdk 内部 WebView 网页加载超时 时长 ( 单位 ms ,仅在 >0 时生效,如传入 <=0 则 sdk 内部会使用默认 值 5000ms) 

}; 

QQ.login(obj, (obj: Record<string, string>) => { 

/** 

* 返回中有 access_token 和 openid ,及申请的开放平台 appid , get 请求 如下地址获取 qq 的用户信息。 

* https://graph.qq.com/user/get_user_info? 

**/ 

console.warn(`qq 登录返回: ${JSON.stringify(obj)}`); 

}); 

七、其他参考方法 

从手机相册选取照片,返回 uris 的示例方法,从开发调试时参考。 import common from '@ohos.app.ability.common'; 

```arkts
import { fileIo as fs, fileUri } from '@kit.CoreFileKit'; 
import { photoAccessHelper } from '@kit.MediaLibraryKit'; 
```

// 选取相册照片示例,返回选中图片 uri 的数组格式,即 uris 。 

async getPictureUriFromAlbum(type: 'video'|'image'): Promise<string[]> { 

let PhotoSelectOptions = new photoAccessHelper.PhotoSelectOptions(); 

if (type === 'video') { 

PhotoSelectOptions.MIMEType = photoAccessHelper.PhotoViewMIMETypes.VIDEO_TYPE; 

PhotoSelectOptions.maxSelectNumber = 1; 

} 

if (type === 'image') { 

PhotoSelectOptions.MIMEType = photoAccessHelper.PhotoViewMIMETypes.IMAGE_TYPE; 

PhotoSelectOptions.maxSelectNumber = 18; 

} 

let photoPicker = new photoAccessHelper.PhotoViewPicker(); 

let photoSelectResult: photoAccessHelper.PhotoSelectResult = await photoPicker.select(PhotoSelectOptions); 

let selectPhoto = photoSelectResult.photoUris; 

console.warn(` 选中的图片 : ${JSON.stringify(selectPhoto)}`); 

// 将选中的图片转 uri 路径 

const allPath: string[] = selectPhoto.reduce((m: string[], itemPath) => { 

let albumPath = itemPath; 

let context = getContext(this) as common.UIAbilityContext; 

```arkts
let filePath = `${context.filesDir}/original-${Date.now()}.${type === 'video' ? 'mp4' : 'jpg'}`; 
```

let file: fs.File | undefined; 

file = fs.openSync(albumPath, fs.OpenMode.READ_ONLY); 

fs.copyFileSync(file.fd, filePath); 

fs.closeSync(file); 

let uri: string = fileUri.getUriFromPath(filePath); // uri 路径 m.push(uri); 

return m; 

}, []); console.log(` 选中的图片 uri 地址 : ${JSON.stringify(allPath)}`); return allPath; 

} 

# 更多内容请参考友盟官方文档说明: 

https://developer.umeng.com/docs/128606/detail/2938161 https://developer.umeng.com/docs/128606/detail/3002400 https://developer.umeng.com/docs/128606/detail/3020975
