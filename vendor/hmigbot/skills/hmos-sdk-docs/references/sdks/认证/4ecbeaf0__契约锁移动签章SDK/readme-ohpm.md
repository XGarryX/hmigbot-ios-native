> 来源: ohpm 中央仓 README(T1 信源) | 包: `@genyannetwork/qysmobilecertlibrary` | ohpm 最新版: 1.0.3 | 抓取: 2026-07-16
> 注意: 版本可能比市场快照新,以此为准时核对 CHANGELOG

# 契约锁移动印章SDK -- 鸿蒙

### 介绍

移动签章鸿蒙APP SDK可以将契约锁移动端的特有功能【移动签章】集成至您的APP。

移动签章是移动端APP特有功能,它用手机APP作为数字证书和私钥的存储介质,通过PIN码和指纹/面容等校验方式可以使用存储在手机APP内的证书进行签名,移动签章相比UKey更加简易方便。

您只需要将APP内的WebView传入SDK,并使用该WebView打开或间接跳转到私有云电子签约移动端H5页面,即可在您的手机APP内使用移动签章在私有云进行电子签约;同时SDK内也提供二维码过滤器以及唤起移动签章管理页等API,满足移动签章制作、查看、管理等不同场景的需要。

#### 下载安装

```
ohpm install @genyannetwork/qysmobilecertlibrary
```

#### 代码集成
1.初始化,在EntryAbility.ets onWindowStageCreate()方法中执行初始化,如下

```
export default class EntryAbility extends UIAbility {
  onWindowStageCreate(windowStage: window.WindowStage): void {
    // 向用户明确提示是否允许SDK使用生物识别功能,然后再初始化SDK
    // 这里简写,默认用户已经授权同意,具体业务逻辑由App处理
    let userBioAuthAgree = true
    QysCertSDK.getInstance().init(this.context,userBioAuthAgree)
  }
}
2.注册当前移动证书环境(或者切换证书环境需要执行下面方法)
/**
* @param inputHost 契约锁私有化环境
* @param optionAppName 可选参数,集成应用App名称,用于后续弹窗显示第三方App名称,如果该方法多次调用,只需传一次即可
* @param inQysApp 可选参数,第三方集成忽略
* @return s 初始化是否成功 Promiss
*/
QysCertSDK.getInstance().switchHost('当前契约锁私有化环境','集成App应用名称')
```

3.如何需要展示证书列表

```
/**
 * 显示移动证书列表管理页面
 */
QysCertSDK.getInstance().showManagerPage()
```

4.扫码活如何使用,第三方应用扫码后获取结果调用processQRCode方法

```
/**
 * @param qrCode 二维码扫描结果
 * @return s boolean类型,为true表示属于移动证书相关二维码以及内部默认处理,false表示由第三方自己处理
 */
let belongToQys= QysCertSDK.getInstance().processQRCode(qrCode)
```

5.JSFuction 集成

方案一:对于未集成过契约锁任何SDK适用

```
Web({ src: this.urlString, controller: this.controller })
  .javaScriptAccess(true)
  .domStorageAccess(true)
  .javaScriptProxy({
    name: 'android',
    methodList: ['xxx'].concat(...qysCertScriptProxyMethods(),
    controller: this.controller,
    object: new QysH5Cert_JSFunction(this.controller)
  })
  .mixedMode(MixedMode.All)
  .zoomAccess(true)
  .onControllerAttached(() => {
    this.attached = true
  })
```

方案二:对于已经集成过契约锁SDK,如指纹/物理用印...
通过拓展JSFunction实现

```
Web({ src: this.urlString, controller: this.controller })
  .javaScriptAccess(true)
  .domStorageAccess(true)
  .javaScriptProxy({
    name: 'android',
    methodList: ['xxx'].concat(...qysCertScriptProxyMethods(),
    controller: this.controller,
    object: new JSFunction(this.controller)
  })
  .mixedMode(MixedMode.All)
  .zoomAccess(true)
  .onControllerAttached(() => {
    this.attached = true
  })

export class JSFunction implements QysH5Cert_JSFunction_Impl{
  controller: webview.WebviewController = new webview.WebviewController();

  constructor(controller: webview.WebviewController) {
    this.controller = controller
  }

  qysApi_MCertAvailable(jsParams: string){
    QysH5Cert_JSFunction_Run.qysApi_MCertAvailable(jsParams,this.controller)
  }

  qysApi_mobileCertActive(jsParams: string) {
    QysH5Cert_JSFunction_Run.qysApi_mobileCertActive(jsParams,this.controller)
  }

  qysApi_mobileCertAvailable(jsParams: string){
    QysH5Cert_JSFunction_Run.qysApi_mobileCertAvailable(jsParams,this.controller)
  }

  qysApi_mobileCertSign(jsParams: string) {
    QysH5Cert_JSFunction_Run.qysApi_mobileCertSign(jsParams,this.controller)
  }

  qysApi_mobileCertAvailableSeals(jsParams: string) {
    QysH5Cert_JSFunction_Run.qysApi_mobileCertAvailableSeals(jsParams,this.controller)
  }

  qysApi_goMobileCert(jsParams: string) {
    QysH5Cert_JSFunction_Run.qysApi_goMobileCert(jsParams,this.controller)
  }

  qysApi_returnApp(jsParams: string) {
    QysH5Cert_JSFunction_Run.qysApi_returnApp(jsParams,this.controller)
  }
}
```
