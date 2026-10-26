# **ocr_collection_bank HAR** 包使用文档 

## **1.** 集成方式 

### **2.1** 修改 **entry/oh-package.json5** 

将依赖改为 har 包路径: 

```
{
  "dependencies": {
    "ocr_collection_bank": "file:../output/ocr_collection_bank.har"
  }
}
```

### **2.2** 修改 **build-profile.json5** 

从 modules 中移除 ocr_collection_bank 模块(仅保留 entry): 

```
{
  "modules": [
    {
      "name": "entry",
      "srcPath": "./entry",
      "targets": [
        {
          "name": "default",
          "applyToProducts": ["default"]
        }
      ]
    }
  ]
}
```

### **2.3** 安装依赖 

```
ohpm install
```

## **2.** 代码中使用 

### **2.1** 导入方式 

所有导入必须从包名导入,不能使用内部路径: 

`//` 正确 `import { BDBankCardManager, BDBankCallBackManager, BDBankDetectResultModel, BDBankDeviceScreen, CustomLoading } from 'ocr_collection_bank'` 

`//` 错误( `har` 包不支持内部路径) `import { BDBankCardManager } from 'ocr_collection_bank/src/main/ets/util/...'` 

### **2.2** 可用导出 

|导出名称|说明|
|---|---|
|BDBankCardManager|银行卡管理器|
|BDOcrHome|OCR银行卡扫描页面组件|

|导出名称|说明|
|---|---|
|BDBankDeviceScreen|设备屏幕工具类|
|CustomLoading|自定义加载组件|
|BDBankCallBackManager|回调管理接口|
|BDBankDetectResultModel|识别结果模型|

## **3. OCR** 银行卡识别 

### **3.1** 初始化 **License** 

在页面 `aboutToAppear` 中初始化: 

`import { BDBankCardManager, BDBankCallBackManager, BDBankDetectResultModel, CustomLoading } from 'ocr_collection_bank' @Entry @Component struct BankCardPage { private isLicense: boolean = false //` 加载弹窗 `customLoading: CustomDialogController = new CustomDialogController({ builder: CustomLoading({}), customStyle: true, autoCancel: false }) aboutToAppear(): void { this.customLoading.open() // License` 配置 `let licenseKey = "YOUR-LICENSE-KEY" let licenseName = getContext().resourceDir + '/' + "your-licensefile.license" //` 初始化 `BDBankCardManager.getInstance().initLicense(licenseKey, licenseName, true) .then(async (res: boolean) => { this.isLicense = res this.customLoading.close() //` 提示初始化结果 `}) } }` 

### **3.2** 设置识别回调 

`let callback: BDBankCallBackManager = { //` 识别结果回调 `listImageCallBack: (model: BDBankDetectResultModel) => { console.info('` 识别结果: `' + JSON.stringify(model)) //` 处理识别结果 `// model.card_no      -` 银行卡号 `// model.valid_date   -` 有效期 `// model.name         -` 持卡人 `// model.bank_name    -` 银行名称 `// model.bank_card_type -` 银行卡类型 

`}, //` 取消回调 `cancelHandler: (str: string): void => { //` 用户取消操作 `} } BDBankCardManager.getInstance().setBDCallBack(callback)` 

### **3.3** 配置识别参数 

`//` 设置识别模式 `BDBankCardManager.getInstance().setCardModelType(1) // 1:` 扫描模式 `, 2:` 拍照模式 

### **3.4** 启动识别 

`//` 需要先申请相机权限 `async function startOCR() { if (this.isLicense) { //` 申请权限后启动 `await grantPermission().then(() => { BDBankCardManager.getInstance().startCollection() }).catch((err) => { console.error('` 权限申请失败 `') }) } }` 

### **3.5** 完整示例 

`import { BDBankDeviceScreen, BDBankCardManager, CustomLoading, BDBankCallBackManager, BDBankDetectResultModel } from 'ocr_collection_bank' import { promptAction } from '@kit.ArkUI' import { BusinessError } from '@kit.BasicServicesKit' import grantPermission from '../utils/PermissionUtils' @Entry @Component struct BDBankVC { private isLicense: boolean = false customLoading: CustomDialogController = new CustomDialogController({ builder: CustomLoading({}), customStyle: true, autoCancel: false }) aboutToAppear(): void { this.customLoading.open() let licenseKey = "YOUR-LICENSE-KEY" let licenseName = getContext().resourceDir + '/' + "your-license.license" BDBankCardManager.getInstance().initLicense(licenseKey, licenseName, true) .then(async (res: boolean) => { this.isLicense = res this.customLoading.close() this.getUIContext().getPromptAction().showToast({ message: this.isLicense ? "` 初始化成功 `" : "` 初始化失败 `", duration: 1000, showMode: promptAction.ToastShowMode.DEFAULT, bottom: 80` 

`}) }) //` 设置回调 `let callback: BDBankCallBackManager = { listImageCallBack: (model: BDBankDetectResultModel) => { console.info('` 识别结果: `' + JSON.stringify(model)) //` 处理银行卡识别结果 `console.info('` 银行卡号: `' + model.card_no) console.info('` 有效期: `' + model.valid_date) console.info('` 持卡人: `' + model.name) console.info('` 银行名称: `' + model.bank_name) console.info('` 卡类型: `' + model.bank_card_type) }, cancelHandler: (str: string): void => {} } BDBankCardManager.getInstance().setBDCallBack(callback) } build() { Column() { Button("` 扫描识别 `") .width(BDBankDeviceScreen.getDeviceWidth() - 50) .height(50) .margin({ top: 30 }) .onClick(async () => { BDBankCardManager.getInstance().setCardModelType(1)  //` 扫描模式 `if (this.isLicense) { await grantPermission().then(() => { BDBankCardManager.getInstance().startCollection() }).catch((err: BusinessError) => { console.info("` 权限申请失败: `" + JSON.stringify(err.code)) }) } }) Button("` 拍照识别 `") .width(BDBankDeviceScreen.getDeviceWidth() - 50) .height(50) .margin({ top: 30 }) .onClick(async () => { BDBankCardManager.getInstance().setCardModelType(2)  //` 拍照模式 `if (this.isLicense) { await grantPermission().then(() => { BDBankCardManager.getInstance().startCollection() }).catch((err: BusinessError) => { console.info("` 权限申请失败: `" + JSON.stringify(err.code)) }) } }) } .width("100%") .height("100%") .alignItems(HorizontalAlign.Center) } }` 

### **3.6** 参数说明 

|方法|参数值|说明|
|---|---|---|
|setCardModelType|1|扫描模式|

|方法|参数值|说明|
|---|---|---|
|setCardModelType|2|拍照模式|

### **3.7** 识别结果字段 

|字段|类型|说明|
|---|---|---|
|card_no|string|银行卡号|
|valid_date|string|有效期|
|name|string|持卡人姓名|
|bank_name|string|银行名称|
|bank_card_type|string|银行卡类型|
|image|PixelMap|识别的卡片图像|

### **3.8** 权限要求 

需要在 `module.json5` 中配置权限: 

```
{
  "requestPermissions": [
    {
      "name": "ohos.permission.CAMERA",
      "reason": "$string:camera_reason",
      "usedScene": {
        "abilities": ["EntryAbility"],
        "when": "inuse"
      }
    },
    {
      "name": "ohos.permission.WRITE_IMAGEVIDEO"
    }
  ]
}
```
