> 来源: ohpm 中央仓 README(T1 信源) | 包: `@ocrgroup/idcardlibrary` | ohpm 最新版: 1.2.22 | 抓取: 2026-07-16
> 注意: 版本可能比市场快照新,以此为准时核对 CHANGELOG

# 简介
译图智讯证件识别系统是一款功能强大、高度集成的工具包(SDK),利用深度学习OCR技术通过智能手机的摄像头或相册,快速、准确地识别和提取各类证照的关键信息。其核心目标是简化信息录入流程,提升用户体验和操作效率。

# 主要功能
自动检测与裁剪:自动定位图像中的证件区域并进行精准裁剪。

字段识别:精确识别证件上的关键字段(如姓名、性别、民族、出生日期、住址、身份证号、签发机关、有效期限等)。

头像提取:自动提取证件上的头像照片。

辅助检测(可选):提供证件实时距离、角度、缺边缺角、光线检测,并提供复印件判断结果、反光判断结果。

# 环境要求
系统:HarmonyOS支持 5.0.0版本(api-12版本及以上)

CPU架构:支持arm64-v8a及64位架构

支持机型:手机和平板

硬件要求:要求设备上有可正常使用的相机模块。

网络:OCR本地离线识别,无需网络

# 安装说明

## 安装

>ohpm install @ocrgroup/idcardlibrary

## 权限配置
>ohos.permission.CAMERA

# API参考

### 初始化与配置

| 方法名 | 参数 | 返回值 | 描述 |
|--------|------|--------|------|
| initSIDCardKernal | context: Context lic: string| int (错误码) | 初始化身份证识别内核 |
| unInitSIDCardKernal | - | int (错误码) | 反初始化身份证识别内核,释放资源 |
| setSIDCardType | type: number | - | 设置身份证类型 1:人像  2:国徽  0:自动 |
| setProductType | type: number | - | 设置识别产品类型 0: 身份证  1:港澳台居住证 |
| setSwitchShow | isShow: boolean | - | 设置是否显示扫描的切换按钮 |
| setSaveCrop | isSave: boolean | - | 是否保存切图 |
| setDefect | isDefect: boolean | - | 设置缺陷检测参数 |

### 识别功能

| 方法名 | 参数 | 返回值 | 描述 |
|--------|------|--------|------|
| cameraSIDCardRecog | type: number path: string | IdcardResult | 通过相机进行身份证识别 |
| cameraSIDCardRecogBuffer | type: number buffer: ArrayBuffer | IdcardResult | 通过相机缓冲区数据进行识别 |
| importSIDCardRecog | context: Context type: number path: string | IdcardResult | 导入本地图片进行身份证识别 |
| streamSIDCardRecogFormat | nvbuffer: ArrayBuffer lineX: number[] lineY: number[] preWidth: number preHeight: number type: number detectState: number format: number | IdcardResult | 通过数据流进行身份证识别 |
| streamSIDCardDetectFormat | nvbuffer: ArrayBuffer lineX: number[] lineY: number[] preWidth: number preHeight: number type: number format: number onDetectCall: (detectCode: number, lineX: number[], lineY: number[]) => void | number | 通过数据流进行身份证检测 |

### 工具方法

| 方法名 | 参数 | 返回值 | 描述 |
|--------|------|--------|------|
| saveCropIdcardImage | type: number path: string | boolean | 保存裁剪后的身份证图片到指定路径 |
| saveBaseIdcardImage | path: string | boolean | 保存原始身份证图片到指定路径 |
| getSIDCardVersion | - | string | 获取身份证识别模块版本号 |
| getProductType | - | int | 获取当前产品类型 |

#### 具体使用可参考文档和Demo

#### *使用之前参考集成文档添加资源文件

# 使用示例

### 初始化核心与释放核心

```aboutToAppear() {
    // 初始化核心
    IdcardOcrApi.initSIDCardKernal(this.context, "7332DBAFD2FD18301EF6").then(code => {
      console.error(IdcardConfig.SDK_TAG + "initSIDCardKernal code:" + code)
      this.m_error = "初始化失败:" + code;
      this.b_error = code == 0 ? false : true;
      this.m_StrVersion = IdcardOcrApi.getSIDCardVersion();
    })
  }
 aboutToDisappear() {
    // 释放核心
    IdcardOcrApi.unInitSIDCardKernal().then(code => {
      console.error(IdcardConfig.SDK_TAG + "unInitSIDCardKernal" + code)
    });
  }
```

##### IdcardResult
识别结果集合
| 参数  | 描述 |
|------|------|
|    code: number   |   识别码 0成功 其他为识别失败   |
|    msg: string   |   错误信息  |
|    name: string  |   姓名     |
|    id: string    |   身份证号   |
|   sex: string    |  性别 |
|   nation: string  |   民族  | 
|   birth: string  |   出生日期  | 
|   address: string  |   住址  | 
|   sign: string  |  签发机关   | 
|   valid: string  |   有效期  | 
|   passNum: string  |   通行证号码  | 
|  checkCopy: number  | 复印件检测 0 原件  1 复印件  |
|  checkLight: number | 反光检测  0 不反光 1 反光  |
|  checkDefect: number |  边角检测  0 无缺失 1 边角缺失 |
|  frontPath: string |  人像页切图 |
|  headPath: string |  头像切图 |
|  backPath: string |  国徽页切图 |
|  frontBasePath: string  | 人像原图  |
|  backBasePath: string |  国徽页原图 |

# 联系我们

### 北京译图智讯科技有限公司
销售热线:400-805-9676

售后热线:010-57105990

服务邮箱:service@etoplive.com

地址:北京市昌平区黄平路19号院1号楼B区20层
