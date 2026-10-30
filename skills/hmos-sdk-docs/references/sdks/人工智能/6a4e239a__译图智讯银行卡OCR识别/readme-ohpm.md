> 来源: ohpm 中央仓 README(T1 信源) | 包: `banklibrary` | ohpm 最新版: 1.4.23 | 抓取: 2026-07-16
> 注意: 版本可能比市场快照新,以此为准时核对 CHANGELOG

# 简介
译图智讯证件识别系统是一款功能强大、高度集成的工具包(SDK),利用深度学习OCR技术通过智能手机的摄像头或相册,快速、准确地识别和提取各类证照的关键信息。其核心目标是简化信息录入流程,提升用户体验和操作效率。

# 主要功能
自动检测与裁剪:自动定位图像中的证件区域并进行精准裁剪。

字段识别:精确识别证件上的关键字段。

辅助检测(可选):提供证件实时距离、角度、光线检测。

# 环境要求
系统:HarmonyOS支持 5.0.0版本(api-12版本及以上)

CPU架构:支持arm64-v8a及64位架构

支持机型:手机和平板

硬件要求:要求设备上有可正常使用的相机模块。

网络:OCR本地离线识别,无需网络

# 安装说明

## 安装

>ohpm install banklibrary

## 权限配置
>ohos.permission.CAMERA

# API参考

### 初始化与配置

| 方法名 | 参数 | 返回值 | 描述 |
|--------|------|--------|------|
| initBankKernal | context: Context lic: string| int (错误码) | 初始化识别内核 |
| unInitBankKernal | - | int (错误码) | 反初始化识别内核,释放资源 |
| setImportEntry | isImport: boolean | - | 是否显示相机界面的导入入口 |
| setSuccessTip | isShow: boolean | - | 设置银行卡确认框显示 |

### 识别功能

| 方法名 | 参数 | 返回值 | 描述 |
|--------|------|--------|------|
| cameraBankRecog | type: number path: string | BankResult | 通过相机进行识别 |
| bufferBankRecog | type: number buffer: ArrayBuffer | BankResult | 图片识别方法(buffer)-拍照界面 |
| picBankRecog | context: Context path: string | BankResult | 导入本地图片进行身份证识别 |
| setScanRegion | left: number right: number top: number bottom: number | - | 设置扫描识别区域 |
| streamBankRecogFormat | context: Context buffer: ArrayBuffer preWidth: number preHeight: number line: number[] lineWarp: number[] orientation: number format: number | - | 视频流识别方法-位置识别format |
| streamBankRecogCornerFormat |context: Context buffer: ArrayBuffer lineX: number[] lineY: number[] preWidth: number preHeight: number format: number onDetectCall: (detectCode: number lineX: number[] lineY: number[]) => void | - | 视频流检测方法-实时检测 |

### 工具方法

| 方法名 | 参数 | 返回值 | 描述 |
|--------|------|--------|------|
| setDefect | isDefect: boolean | - | 是否开启强制边角检测  true: 强制检测,缺角后不识别  false: 只进行提示 |
| getBankVersion | - | string | 获取身份证识别模块版本号 |

#### 具体使用可参考文档和Demo

#### *使用之前参考集成文档添加资源文件

# 使用示例

### 初始化核心与释放核心

```
  aboutToAppear() {
    // TODO 初始化核心
    BankOcrApi.initBankKernal(this.context, "7332DBAFD2FD18301EF6").then(code => {
      console.error(BankConfig.SDK_TAG + "initSIDCardKernal code:" + code)
      this.m_error = "初始化失败:" + code;
      this.b_error = code == 0 ? false : true;
      // 获取版本号
      this.m_StrVersion = BankOcrApi.getBankVersion();
    })
  }
  aboutToDisappear() {
    // TODO 释放核心
    BankOcrApi.unInitBankKernal().then(code => {
      console.error(BankConfig.SDK_TAG + "unInitSIDCardKernal" + code)
    });
  }
```

##### BankResult
识别结果集合
| 参数  | 描述 |
|------|------|
|    code: number   |   识别码 0成功 其他为识别失败   |
|    msg: string   |   错误信息  |
|    bankNum: string  |   银行卡号     |
|    bankName: string    |    银行名称   |
|   bankCode: string    |  银行代码 |
|   bankCardName: string  |   卡名称  | 
|   bankType: string  |   卡类型  | 
|   bankDate: string  |   有效期限  | 
|   bankHolder: string |  持卡人   | 
|   cropNoPath: string |   证卡切图  | 
|   basePath: string  |   原始图  | 
|  checkDefect: number  | 边角检测  0 无缺失 1 边角缺失  |

# 联系我们

### 北京译图智讯科技有限公司
销售热线:400-805-9676

售后热线:010-57105990

服务邮箱:service@etoplive.com

地址:北京市昌平区黄平路19号院1号楼B区20层
