# **--** **契约锁物理用印SDK 鸿蒙** 

## **介绍** 

物理用印鸿蒙应用 SDK可以将私有云移动端的物理用印功能集成至您的APP中,从而在APP内实现连接物理章筒设 备、解锁用印、拍照回传、结束用印等操作。 您只需要将APP内的WebView传入SDK,并使用该WebView打开或 间接跳转到私有云物理用印移动端H5页面,即可实现本SDK所覆盖的物理用印功能。 

### **下载安装** 

ohpm install @genyannetwork/qysbluetoothseal 

### **Web集成** 

Web({ src: this.urlString, controller: this.controller }) 

.javaScriptAccess(true) 

.javaScriptProxy({ object: new QysH5Seal_JSFunction(this.controller), name: 'android', methodList: qysSealScriptProxyMethods(), controller: this.controller }) 

### **使用案例** 

```arkts
import { router } from '@kit.ArkUI' @Entry @Component struct Index { @State text: string = 'http://app201.qiyuesuo.net' placeHolder: string = '输入URL地址' controller: TextInputController = new TextInputController() 
```

build() { Row() { Column() { TextInput({ text: this.text, placeholder: this.placeHolder, controller: this.controller }) 

.placeholderColor(Color.Grey) 

.placeholderFont({ size: 14 }) .width(300) .height(40) .margin(20) .fontSize(14) .fontColor(Color.Black) 

.onChange((value: string) => { this.text = value }) Button('前往') .margin(30) .onClick(() => { router.pushUrl({ url: 'pages/WebPage', params: { webUrl: this.text } }) }) } .width('100%') } .height('100%') } }
