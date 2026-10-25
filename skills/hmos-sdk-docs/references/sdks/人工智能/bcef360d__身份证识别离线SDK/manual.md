# **ocr_collection_idcard HAR** 包使用文档 

## **1. HAR** 包位置 

```
output/ocr_collection_idcard.har
```

## **2.** 集成方式 

### **2.1** 修改 **entry/oh-package.json5** 

将依赖改为 har 包路径: 

```
{
  "dependencies": {
    "ocr_collection_idcard": "file:../output/ocr_collection_idcard.har"
  }
}
```

### **2.2** 修改 **build-profile.json5** 

从 modules 中移除 ocr_collection_idcard 模块(仅保留 entry): 

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

## **3.** 代码中使用 

### **3.1** 导入方式 

所有导入必须从包名导入,不能使用内部路径: 

`//` 正确 `import { DeviceScreen, BDCardManager, CustomLoading, BDCardCallBackManager, BDCallBackResultModel, BDDetectResultModel } from 'ocr_collection_idcard' import { Logger } from 'ocr_collection_idcard'` 

`//` 错误( `har` 包不支持内部路径) `import { DeviceScreen } from 'ocr_collection_idcard/src/main/ets/...'` 

### **3.2** 可用导出 

|导出名称|说明|
|---|---|
|OCRCollectionTool|OCR采集工具|
|BDCardManager|卡片管理器|
|BDOcrHome|OCR主页组件|
|DeviceScreen|设备屏幕工具类|
|Logger|日志工具|
|CustomLoading|自定义加载组件|
|BDCardCallBackManager|回调管理接口|
|BDCallBackResultModel|回调结果模型|
|BDDetectResultModel|检测结果模型|

## **4. OCR** 身份证识别 

### **4.1** 初始化 **License** 

在页面 `aboutToAppear` 中初始化: 

`import { BDCardManager, BDCardCallBackManager, BDDetectResultModel, CustomLoading } from 'ocr_collection_idcard' @Entry @Component struct IDCardPage { private isLicense: boolean = false //` 加载弹窗 `customLoading: CustomDialogController = new CustomDialogController({ builder: CustomLoading({}), customStyle: true, autoCancel: false }) aboutToAppear(): void { this.customLoading.open() // License` 配置 `let licenseKey = "YOUR-LICENSE-KEY" let licenseName = getContext().resourceDir + '/' + "your-licensefile.license" //` 初始化 `BDCardManager.getInstance().initLicense(licenseKey, licenseName, true) .then(async (res: boolean) => { this.isLicense = res this.customLoading.close() //` 提示初始化结果 `}) } }` 

### **4.2** 设置识别回调 

`let callback: BDCardCallBackManager = { //` 识别结果回调 `listImageCallBack: (model: BDDetectResultModel) => { console.info('` 识别结果: `' + JSON.stringify(model)) //` 处理识别结果 `}, //` 取消回调 `cancelHandler: (str: string): void => { //` 用户取消操作 `} } BDCardManager.getInstance().setBDCallBack(callback)` 

### **4.3** 配置识别参数 

`//` 设置证件类型 `BDCardManager.getInstance().setCategoryType(0)  // 0:` 身份证 `, 2:` 银行卡 `//` 设置卡片面 `BDCardManager.getInstance().setCardType(0)      // 0:` 正面 `(` 头像面 `), 1:` 反面 `(` 国徽面 `) //` 设置识别模式 `BDCardManager.getInstance().setCardModelType(1) // 1:` 扫描模式 `, 2:` 拍照模式 

### **4.4** 启动识别 

`import { abilityAccessCtrl } from '@kit.AbilityKit' //` 需要先申请相机权限 `async function startOCR() { if (this.isLicense) { //` 申请权限后启动 `await grantPermission().then(() => { BDCardManager.getInstance().startCollection() }).catch((err) => { console.error('` 权限申请失败 `') }) } }` 

### **4.5** 完整示例 

```
import { DeviceScreen, BDCardManager, CustomLoading, BDCardCallBackManager,
BDDetectResultModel } from 'ocr_collection_idcard'
import { JSON } from '@kit.ArkTS'
@Entry
@Component
struct BDIDcardVC {
  private isLicense: boolean = false
  customLoading: CustomDialogController = new CustomDialogController({
    builder: CustomLoading({}),
    customStyle: true,
    autoCancel: false
  })
  aboutToAppear(): void {
```

`this.customLoading.open() let licenseKey = "YOUR-LICENSE-KEY" let licenseName = getContext().resourceDir + '/' + "your-license.license" BDCardManager.getInstance().initLicense(licenseKey, licenseName, true) .then(async (res: boolean) => { this.isLicense = res this.customLoading.close() }) //` 设置回调 `let callback: BDCardCallBackManager = { listImageCallBack: (model: BDDetectResultModel) => { console.info('` 识别结果: `' + JSON.stringify(model)) }, cancelHandler: (str: string): void => {} } BDCardManager.getInstance().setBDCallBack(callback) } build() { Column() { Button("` 身份证头像面扫描 `") .onClick(async () => { BDCardManager.getInstance().setCategoryType(0)   //` 身份证 `BDCardManager.getInstance().setCardType(0)       //` 正面 `BDCardManager.getInstance().setCardModelType(1)  //` 扫描 `if (this.isLicense) { await grantPermission().then(() => { BDCardManager.getInstance().startCollection() }) } }) Button("` 身份证国徽面拍照 `") .onClick(async () => { BDCardManager.getInstance().setCategoryType(0)   //` 身份证 `BDCardManager.getInstance().setCardType(1)       //` 反面 `BDCardManager.getInstance().setCardModelType(2)  //` 拍照 `if (this.isLicense) { await grantPermission().then(() => { BDCardManager.getInstance().startCollection() }) } }) } } }` 

### **4.6** 参数说明 

|方法|参数值|说明|
|---|---|---|
|setCategoryType|0|身份证|
|setCategoryType|2|银行卡|
|setCardType|0|正面(身份证头像面)|
|setCardType|1|反面(身份证国徽面)|
|setCardModelType|1|扫描模式|
|setCardModelType|2|拍照模式|

### **4.7** 权限要求 

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
