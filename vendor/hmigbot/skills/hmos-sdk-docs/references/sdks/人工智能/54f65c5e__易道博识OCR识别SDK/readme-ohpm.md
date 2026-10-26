> 来源: ohpm 中央仓 README(T1 信源) | 包: `exocrdomsdk` | ohpm 最新版: 3.5.2 | 抓取: 2026-07-16
> 注意: 版本可能比市场快照新,以此为准时核对 CHANGELOG

# ExDomCardSDK

## 简介

易道博识OCR识别SDK,采用深度学习OCR技术,通过手机或带有摄像头的终端设备对证件进行拍照,或者直接输入静态图片,即可快速完成证件的识别,输出结构化数据。

- 深度学习OCR技术
- 图像的矫正与裁剪
- 证件质检
- 纯离线无需任何网络

## 下载安装

```
ohpm install exocrdomsdk
```

将授权文件复制到手机中, 然后将授权文件路径传入 SDK

## 需要权限

```
ohos.permission.CAMERA
```

##  接口和属性列表

| **接口**         | **原型**                                                     | **描述**                          |
| ---------------- | ------------------------------------------------------------ | --------------------------------- |
| 授权             | *EngineManager.getInstance().applyForAuth(**licPath,context**)* | 注意,使用SDK的首要条件是检查授权 |
| 获取SDK版本号    | *EngineManager.getInstance().getSDKVersion()*                | 返回String类型                    |
| 获取核心版本号   | *EngineManager.getInstance().getKernelVersion()*             | 返回String类型                    |
| 获取核心版本类型 | *EngineManager.getInstance().getKernelType()*                |                                   |
| 获取到期时间     | *EngineManager.getInstance().getKernelValidDate()*           | 返回String类型                    |
| 获取授权包名     | *EngineManager.getInstance()**.**getKernel**BundleName()*    | 返回String类型                    |
| 是否是测试版     | *EngineManager.getInstance().isBeta()*                       | 返回boolean类型                   |

### 扫描接口

| **名称**     | **原型**                                                     | **描述**             |
| ------------ | ------------------------------------------------------------ | -------------------- |
| **扫描识别** | DomCardManager.getInstance().recognize(ExDataCallBack,  getContext(), CardType) | 调起相机进行扫描识别 |

### 相册接口

| **名称**         | **原型**                                                     | **描述**         |
| ---------------- | ------------------------------------------------------------ | ---------------- |
| **静态图片识别** | DomCardManager.getInstance().recPhoto(PhotoCallBack,image.PixelMap,getContext(),CardType) | 传入图片进行识别 |

### 自定义扫描接口

| **名称**           | **原型**                                                     | **描述**           |
| ------------------ | ------------------------------------------------------------ | ------------------ |
| **自定义扫描识别** | DomCardManager.getInstance().recognizeCustom(ExCustomCallBack,getContext(),CardType) | 设置回调和识别类型 |

### CardInfo

描述:证件识别结果

| **成员与方法**                             | **描述**                                                     |
| ------------------------------------------ | ------------------------------------------------------------ |
| *public CardType cardType*                 | 卡证类型,1: 银行卡;2:身份证。                            |
| *public int pageType;*                     | 卡证正反面,1:人像面;2:反面                               |
| *public EXIDCardPage idCardPage;*          | 卡证正反面,EXIDCARDFACE为人像面,EXIDCARDBACK为国徽面;身份证独有属性 |
| *public  Map<String, RecoItem> items*      | 识别结果条目(map的key为条目英文)                           |
| *public PixelMap \| undefined  cardImg;*   | 识别后身份证切图。用于兼容以前版本。                         |
| *public PixelMap \|  undefined faceImg*    | 面部截图                                                     |
| *public PixelMap \| undefined originalImg* | 预览帧全图                                                   |
| *public boolean  isMarginComplete*         | 留白切图后的点是否在图像外                                   |
| *public boolean isFromStream*              | 是否是视频流识别                                             |
| *public  boolean isFar*                    | 是否过近,主要针对静态图识别(老版本无)                     |
| *public boolean isBlurred*                 | 是否模糊,主要针对静态图识别(老版本无)                     |
| *public  boolean isReflective*             | 是否反光,主要针对静态图识别(老版本无)                     |
| *public boolean isOutside*                 | 是否缺角,主要针对静态图识别(老版本无)                     |
| *public  boolean isDeformed*               | 是否变形,主要针对静态图识别(老版本无)                     |
| *public boolean isCover*                   | 是否遮挡(老版本无)                                         |
| *public int pageVersion*                   | 外国人永居证的版本 2023和2017 其他卡证为0                    |

### RecoItem

**描述:**识别条目类

| **成员与方法**                | **描述**                                                     |
| ----------------------------- | ------------------------------------------------------------ |
| **public String chinese_key** | 条目名称。身份证包含姓名, 性别, 民族,住址,民身份号码,出生日期,签发机关,有效期;银行卡包含number, bank_name, card_name, card_type, date。 |
| **public String item_words**  | 识别的条目文字                                               |
| **public String item_quad**   | 条目坐标                                                     |
| **public String item_id**     | 条目id                                                       |
