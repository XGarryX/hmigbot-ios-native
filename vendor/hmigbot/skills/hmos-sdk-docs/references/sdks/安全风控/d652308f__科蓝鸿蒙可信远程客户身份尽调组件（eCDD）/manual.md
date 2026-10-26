## **eCDD 科蓝鸿蒙可信远程客户身份尽调组件( )使用指南** 

该组件库可帮助应用快速实现NFC识读居民二代身份证件信息、NFC识读银行卡信息。组件内部实现NFC识读UI、 NFC识读引导动画、NFC开关判断以及引导开启NFC开关等体验。ML组件库提供OCR识读身份证正反面,银行卡以及提 供活体检测的能力。 

# **一** **、集成说明** 

##### **oh-package 引入** 

```
'@csii/nfc': 'file:./libs/csii_nfc.har'
"@csii/ml": "file:./libs/csii_ml.har"
```

##### **约束和限制** 

最低兼容: API Version 11 

# **二、使用说明** 

### **相关代码** 

- NFCClient 用于调用NFC识读身份证银行卡 

- NFCOptions 用于配置NFC功能的选项 

- NFCReadState 定义NFC读取操作的状态枚举(读取成功、读取过程中出现错误、读取操作被取消) MLClient 用于调用OCR识读身份证、OCR识读银行卡以及活体检测 

### **使用示例** 

#### **NFC组件初始化** 

```
import { NFCOptions } from'@csii/nfc';
//在UIAbility的onWindowStageCreate方法中
NFCOptions.buildInstance()
      .windowStage(windowStage)
""
      .urlHost(服务器地址)
      .appID("appID")
""
      .channelID(渠道号)
```

#### **NFC标签保持和释放** 

```
import { NFCClient } from'@csii/nfc';
private nfcClient=NFCClient.buildInstance();
onPageShow(): void {
this.nfcClient.holdNFC();// 保持对NFC标签的读取权限
}
onPageHide(): void {
this.nfcClient.unHoldNFC();// 释放对NFC标签的读取权限
}
```

#### **NFC识读身份证** 

```
import { NFCClient, NFCReadState } from'@csii/nfc';
//NFC识读身份证
this.nfcClient.readIDCardInfo((state: NFCReadState, nfcData: string) => {
""
console.info("readIDCardInfo code:+state+" data:+nfcData);
if (state==NFCReadState.OK) {
console.log(nfcData)
     } else {
""
console.log(识读失败)
     }
})
```

#### **NFC识读银行卡** 

```
import { NFCClient, NFCReadState } from'@csii/nfc';
//NFC识读银行卡
this.nfcClient.startBankCardRead((state: NFCReadState, result: string) => {
if (state==NFCReadState.OK) {
console.log(result)
    } else {
console.error("result:"+result)
    }
})
```

#### **OCR识读身份证正面** 

```
import { CCRState, CCRType, MLClient } from'@csii/lib_ml';
//调用OCR识别身份证正面,通过CCRType来确定识别类型
MLClient.startCCR(CCRType.IdCardFront, (state: CCRState, result: string) => {
if (state==CCRState.OK) {
""
console.log(识别成功:+result)
            } elseif (state==CCRState.ERROR) {
"
console.log(识别失败: "+result)
            } elseif (state==CCRState.CANCEL) {
"
console.log(取消识别: "+result)
            }
    })
```

#### **OCR识读身份证反面** 

```
import { CCRState, CCRType, MLClient } from'@csii/lib_ml';
//调用OCR识别身份证正面,通过CCRType来确定识别类型
MLClient.startCCR(CCRType.IdCardBack, (state: CCRState, result: string) => {
if (state==CCRState.OK) {
""
console.log(识别成功,结果:+result)
            } elseif (state==CCRState.ERROR) {
"
console.log(识别失败: "+result)
            } elseif (state==CCRState.CANCEL) {
"
console.log(取消识别: "+result)
            }
      })
```

#### **OCR识读银行卡** 

```
import { CCRState, CCRType, MLClient } from'@csii/lib_ml';
//调用OCR识别身份证正面,通过CCRType来确定识别类型
MLClient.startCCR(CCRType.BankCard, (state: CCRState, result: string) => {
if (state==CCRState.OK) {
""
console.log(识别成功,结果:+result)
            } elseif (state==CCRState.ERROR) {
"
console.log(识别失败: "+result)
            } elseif (state==CCRState.CANCEL) {
"
console.log(取消识别: "+result)
            }
     })
```

#### **活体检测** 

```
import { CCRState, CCRType, MLClient } from'@csii/lib_ml';
//调用OCR识别身份证正面,通过CCRType来确定识别类型
MLClient.startLiveness((state: CCRState, result: string) => {
if (state==CCRState.OK) {
""
console.log(活体检测成功,结果:+result)
            } elseif (state==CCRState.ERROR) {
"
console.log(活体检测失败: "+result)
            } elseif (state==CCRState.CANCEL) {
"
console.log(取消活体检测: "+result)
            }
   })
```

#### **ML组件字段说明** 

|**名称**|**类型**|**说明**|
|---|---|---|
|CCRType|enum|IdCardFront :身份证正面 IdCardBack:身份证反面 BankCard:银行卡识别|
|**名称**|**类型**|**说明**|
|CCRState|enum|OK:成功 ERROR:错误 CANCEL:取消识别|
|**名称**|**类型**|**说明**|
|身份证正面|string|返回JSON字符串 name:姓名 sex:性别 nationality:民族 birth;生日 address:住址 idNumber:身份证号码 idCardFaceImage:头像base64|
|身份证反面|string|返回JSON字符串 authority:签证机关 validPeriod:身份证有效期|
|银行卡|string|返回JSON字符串 bankNum:银行卡号 validPeriod:有效期|
|活体检测|string|返回JSON字符串 imageBase64:人脸图片base64|
