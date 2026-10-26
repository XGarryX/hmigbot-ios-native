> 来源: ohpm 中央仓 README(T1 信源) | 包: `@genyannetwork/qysbluetoothseal` | ohpm 最新版: 1.0.5 | 抓取: 2026-07-16
> 注意: 版本可能比市场快照新,以此为准时核对 CHANGELOG

# 契约锁物理用印SDK -- 鸿蒙

### 介绍

物理用印原生APP SDK可以将私有云移动端的物理用印功能集成至您的APP中,从而在APP内实现连接物理章筒设备、解锁用印、拍照回传、结束用印等操作。 您只需要将APP内的WebView传入SDK,并使用该WebView打开或间接跳转到私有云物理用印移动端H5页面,即可实现本SDK所覆盖的物理用印功能。

#### 下载安装

```
ohpm install @genyannetwork/qysbluetoothseal
```

#### Web集成

```
Web({ src: this.urlString, controller: this.controller })
  .javaScriptAccess(true)
  .javaScriptProxy({
    object: new QysH5Seal_JSFunction(this.controller),
    name: 'android',
    methodList: qysSealScriptProxyMethods(),
    controller: this.controller
  })
```

#### 使用案例

```
import { router } from '@kit.ArkUI'

@Entry
@Component
struct Index {
  @State text: string = 'http://app201.qiyuesuo.net'
  placeHolder: string = '输入URL地址'
  controller: TextInputController = new TextInputController()

  build() {
    Row() {
      Column() {
        TextInput({ text: this.text, placeholder: this.placeHolder, controller: this.controller })
          .placeholderColor(Color.Grey)
          .placeholderFont({ size: 14 })
          .width(300)
          .height(40)
          .margin(20)
          .fontSize(14)
          .fontColor(Color.Black)
          .onChange((value: string) => {
            this.text = value
          })
        Button('前往')
          .margin(30)
          .onClick(() => {
            router.pushUrl({ url: 'pages/WebPage', params: { webUrl: this.text } })
          })
      }
      .width('100%')
    }
    .height('100%')
  }
}
```
