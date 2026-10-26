# **版本信息** 

|**版本**|**作者**|**日期**|**说明**|**评审人**|
|---|---|---|---|---|
|Plugin v2402.1|zengzhang|2024.10|||

# **一** **、 系统概述** 

非常感谢您使用菊风系统软件的产品,我们将为您提供最好的服务。 

本手册可能包含技术上不准确的地方或排版错误。本手册的内容将做定期的更新,恕不另行通知;更新 的内容将会在本手册的新版本中加入。我们随时会改进或更新本手册中描述的产品或程序。 

智能双录插件的主要目标是推出远程双录、现场双录、自助双录的产品,为银行、机构提供保险、理 财、信贷等金融场景高可用的音视频双录服务。 

# **二、 关于菊风软件** 

宁波菊风系统软件有限公司(简称“菊风 ”,英文简称“Juphoon”)成立于2005年,现有员工200余 人, 注册资金2050万元,总部位于宁波,在北京、广州、长沙设有区域中心(研发、销售和交付),在郑州 和杭州设有交付中心,是一家提供实时音视频通信和RCS融合通信解决方案的供应商。宁波总部研发中 心主要负责客户端SDK 和 APP、音视频引擎、服务器等产品的研发;云平台和服务器系统的运维、网管 等支撑系统研发,现中心成员有180名。 

菊风经过15年+音视频底层技术积累,为众多行业合作伙伴提供了超优音视频通信服务。凭借卓越的产 品以及优质的服务,迄今为止,已有数十亿终端用户以及众多企业用户通过菊风云实现了音视频场景化 沟通,涉及社交、教育、医疗、智能硬件、金融、电商等多个行业领域,为其提供了有针对性的行业化 解决方案。 

菊风为开发者提供的优而小的 SDK 极简接入,快速助其实现实时音视频通信能力。基于客户不同需求, —— 菊风云提供灵活的部署模式 公有云,专有云,私有云,海外云以及混合云。对主流系统平台全覆 盖,支持 iOS、Android、鸿蒙Next、Windows、UOS、Kylin、微信小程序、H5 等。支持各移动设备 (电脑、手机、平板)、VTM机等多终端设备的适配。 

## **2.1 技术支持** 

在您使用 Juphoon RTC SDK 的过程中,遇到任何困难,请与我们联系,我们将热忱为您提供帮助。 

您可以通过如下方式与我们取得联系: 

公司官网:https://rtc.juphoon.com 产品咨询:sales@juphoon.com 加急热线:13056832331 咨询电话:400-800-8708 / 0574-87901227 

售前工程师微信二维码: 

## **2.2 版权申明** 

“Juphoon RTC for Android SDK”是由宁波菊风系统软件有限公司开发,拥有自主知识产权(软著正式编 号 2020SR0369466号)的系统平台,宁波菊风系统软件有限公司拥有与本产品所用技术相关的知识产 一 权。这些知识 产 权 包 括 但 不 限 于 项 或 多 项 发 明 专 利 或 者 正 在 进 行 申 请 的 专 利 (ZL202010288867.7 、ZL201911393580.4 )。 

本产品发行所依照的许可协议限制其使用、复制分发和反编译。未经宁波菊风系统软件有限公司事先书 面授权,不得以任何形式或借助任何手段复制本产品的任何部分。随本SDK 一同发布的Demo 演示程序 源代码版权归宁波菊风系统软件有限公司。Juphoon 是宁波菊风系统软件有限公司的商标。 

# **三、快速集成 SDK** 

本文为您介绍了 Android 端集成 SDK 的操作步骤,帮助您快速集成 SDK 并实现多方视频通话的基本功 能。 

## **3.1 集成常见问题** 

见 FAQ 

## **3.2 前提条件** 

- HarmonyOS SDK 5.0.0(12) 及以上 

- 支持 HarmonyOS Next.0.0.70 以上版本的移动设备 

## **3.3 创建 Harmony Next 项目** 

参考以下步骤创建一个 Harmony Next 项目。若已有 Harmony Next 项目,可以直接查看【集成 SDK】。 

打开 **DevEco Studio** ,点击 **文件 -> 新建 -> Create Project** 。 

- 在 **Choose your ability Template** 界面,选择 **Application -> Empty Ability** ,然后点击 **Next** 。 

- 在 **Configure Your Project** 界面,依次填入以下内容: 

   - **Project Name** :您的项目名称,如 HelloJuphoon。 

   - **Bundle name** :您的项目包的名称,如 io.helloJuphoon。 

   - **Save location** :项目的存储路径 

   - **Compatible SDK** :项目的最低 API 等级,选5.0.0(12)及以上版本 **Module name** :项目入口 **Device type** : 支持的设备 

然后点击 **Finish** 。根据屏幕提示,安装可能需要的插件。 

## **3.4 集成步骤** 

### **步骤一: 获取 Juphoon_Record_Plugin_for_Harmony** 

您可在 Juphoon 的产品官方网站下载到最新版的 Juphoon Record Plugin 和Juphoon RTC SDK 

### **步骤二:导入 SDK** 

1. 拷贝 SDK 文件夹内相关的har包 到您工程目录中的 sdk 目录下,并打开工程,如下图所示 

2. 为能连接到我们的 so 库,在您工程 oh-package.json5 文件中确保增加以下配置,如图: 

### **步骤三:添加权限** 

根据工程需要,打开 src/main/module.json5 文件,配置权限。 

```
"requestPermissions": [
      {
"name": "ohos.permission.INTERNET"
      },
      {
"name": "ohos.permission.GET_NETWORK_INFO"
      },
      {
"name": "ohos.permission.GET_WIFI_INFO"
      },
      {
"name": "ohos.permission.MODIFY_AUDIO_SETTINGS"
      },
      {
"name": "ohos.permission.USE_BLUETOOTH"
      },
      {
"name": "ohos.permission.KEEP_BACKGROUND_RUNNING"
      },
      {
"name": "ohos.permission.LOCATION",
"reason": "$string:location_request",
"usedScene": {
"when": "inuse",
"abilities": [
"JRecordAppAbility"
          ]
        }
      },
      {
"name": "ohos.permission.APPROXIMATELY_LOCATION",
"reason": "$string:location_request",
"usedScene": {
"when": "inuse",
"abilities": [
"JRecordAppAbility"
          ]
        }
      },
      {
"name": "ohos.permission.MICROPHONE",
"reason": "$string:reasonUseMicrophone",
"usedScene": {
"abilities": [
"JRecordAppAbility"
          ],
"when": "always"
        }
      },
      {
"name": "ohos.permission.CAMERA",
"reason": "$string:reasonUseCamera",
"usedScene": {
"abilities": [
"JRecordAppAbility"
          ],
"when": "always"
        }
      },
    ],
```

|**权限名称**|**权限说明**|**使用目的**|
|---|---|---|
|ohos.permission.INTERNET|网络 访问 权限|用于用户登录、音视频通话、 文件上传、资源下载操作|
|ohos.permission.GET_NETWORK_INFO|获取 数据 网络 信息|用于显示用户当前网络状态|
|ohos.permission.GET_WIFI_INFO|获取 无线 网络 信息|获取Wi-Fi状态、扫描到的热点 列表、已连接Wi-Fi的SSID等 网络信息|
|ohos.permission.MODIFY_AUDIO_SETTINGS|修改 应用 音频 设置|控制音频音量大小需要|
|ohos.permission.KEEP_BACKGROUND_RUNNING|后台 长时 任务 权限|用于后台长时间任务,切换到 后台时保持程序不退出|
|ohos.permission.LOCATION|精准 点位|用于精准地理位置文字水印的 设置|
|ohos.permission. APPROXIMATELY_LOCATION|基准 定位|用于大致地理位置文字水印的 设置|
|ohos.permission.MICROPHONE|麦克 风权 限|用于音频通话、Asr语言识别必 需|
|ohos.permission.CAMERA|相机 权限|用于视频通话、证件识别、人 脸对比必需|
|ohos.permission.USE_BLUETOOTH|蓝牙|用户蓝牙设备通话|

# **四、快速搭建 Plugin** 

## **4.1 初始化插件** 

```
/**
 * 初始化
```

- `@param context ability Context` 

- `@param param 基本初始化配置信息` 

- `@return 调用是否成功` 

```
 */
public initPlugin(Context context, RecordInitParam param): boolean
/**
 * 初始化相关参数
 */
public class RecordInitParam {
    /**
     * appKey(必填)
     */
    private appKey: string;
    /**
     * Cloud服务器地址(usePortalConfig = true 选填)
     */
    private cloudServe: string;
    /**
     * 业务服务器地址(usePortalConfig = true 选填)
     */
    private busnissServer: string;
    /**
     * portal地址(必填)
     */
    private portalServer: string;
    /**
     * 使用 portal配置终端参数(必填)
     * true 不需要设置 cloudServer,busnissServer
     * false 需要设置 cloudServer,busnissServer
     * 默认需要
     */
    private usePortalConfig: boolean = true;
    /**
     * 应用名(选填)
     */
    private appName: string;
    /**
     * 设置SDK信息存储目录,该目录下的log目录为日志目录(选填)
     */
    private sdkInfoDir: string;
    /**
     * 设备id(选填)
     */
    private deviceId: string;
}
public initPlugin(context: Context) {
    const initParam = new RecordInitParam();
    initParam.appKey = "appKey"; // appKey
    initParam.appName = "_appName"; // 设置应用名
    initParam.businessServer = "business服务地址";
    initParam.cloudServer = "Cloud服务地址"; // 设置cloud媒体房间服务地址
    initParam.portalServer = "portal服务地址"; // 设置portal服务地址
    initParam.isUsePortalConfig = true;// 使用 portal配置终端参数
    let res = RecordManager.instance.initPlugin(getContext(), initParam);
    //添加回调事件,需要继承RecordCallBack接口
    if (RecordManager.instance.getRecordCallBacks() != null) {
      RecordManager.instance.addRecordCallback(this);
    }
  }
```

## **4.2 销毁插件** 

```
/**
 * 销毁
 * @return 调用成功或失败
 */
public unitPlugin():boolean;
```

## **4.3 登录** 

```
/**
 * 登录
 * 登录结果通过 onLoginStateChanged 回调
 * @return 调用成功或失败
 */
public login(loginParam:LoginParam);
/**
 * 登录参数
 */
export class LoginParam {
  /**
   * 用户名(必填)确保唯一
   */
  public userName: string = '';
  /**
   * token校验类型(选填)
   */
  public tokenType: string = "jrtc_access";
  /**
   * token(选填)
   */
  public token: string = '';
  /**
   * 昵称,显示的昵称
   */
  public displayName:string = "";
}
```

## **4.4 登出** 

```
/**
 * 登出
 * 登出结果通过 onLoginStateChanged 回调
 * @return 调用成功或失败
 */
public logout(): boolean;
```

## **4.5 签入** 

```
/**
   * 签入
   * @param params 登录相关配置(必填)
   * @param recordConfig 业务相关配置信息
   * @param location 定位信息, 可为null
   * @param roles 参会角色多个情况下以英文逗号 "," 分割
   * @return 调用成功或失败
 */
public checkIn(params: LoginParam, recordConfig?: RecordConfig, location?:
Location, roles?: string): boolean;
/**
 * 录制相关参数
 */
export class RecordConfig {
  /**
   * 人脸标准图路径键值对(选填),映射关系 “角色”->"路径"
   * 不填,流程编排服务主动获取联网图片
   * 角色和人脸标准图路径对应,支持url路径以及本地图片绝对路径
   */
  public standardPicList: HashMap<string, string> = new HashMap();
  /**
   * 本地录制水印开关(选填)
   * 默认关闭
   */
  public openWatermark: boolean = false;
  /**
   * 本地录制水印集合(选填)
   * 内容包括水印类型, 内容, 显示的坐标位置
   */
  public watermarks: ArrayList<WatermarkItem> | undefined;
  /**
   * 是否需要环境检测界面(选填)
   * 默认需要
   */
  public showDetectView: boolean = true;
  /**
   * 是否转人工操作插件内部调用排队呼叫(选填)
   * false : 转人工后插件不进行排队呼叫; true : 转人工后插件内部根据业务参数进行排队呼叫
   * 默认需要
   */
  public initiativeTurnQueuing = false;
  /**
   * 是否打开人脸在框检测(选填)
   * (针对自助场景),决定自助业务中是否打开人脸检测功能
   * 默认需要
   */
  public openFaceCompare = true;
  /**
   * 是否打开人脸在框检测(选填)
   * (针对自助场景),决定自助业务中是否打开人脸检测功能
   * 默认需要
   */
  public openFaceDetect = true;
  /**
   * 排队业务呼叫超时时间, 秒(选填)
   * (针对排队呼叫场景),决定超时时间
   * 默认需要
   */
  public callingTimeout = -1;
  /**
   * 业务额外参数(选填)
   * 业务额外参数,传给业务房间
   * 默认空
   */
  public extraCallParam = '';
  /**
   * 屏幕共享模式(选填)
   * 只有屏幕共享的业务模式,不加入业务界面
   * 默认否
   */
  public onlyShareMode = false;
  /**
   * 失败需要留存话单(选填)
   * 针对自助业务,失败情况下依旧留存话单信息
   * 默认否
   */
  public retainCallRecord = false;
}
```

## **4.6 签出** 

```
/**
 * 签出
 * 签出结果通过 onCheckStateChanged 回调
 * @return 调用成功或失败
 */
public checkOut(): boolean
```

## **4.7 媒体配置** 

```
/**
 * 媒体配置
 * @param config   媒体配置参数
 * @return 调用成功或失败
 */
public setRecordMediaConfig(config: RecordMediaConfig): boolean;
/*
媒体配置参数
 */
export class RecordMediaConfig {
  audioSourceType: number = -1;
  audioSourcePath: string = "";
  /**
   * 摄像头采集分辨率宽
   */
  cameraCaptureWidth: number = 1280;
  /**
   * 摄像头采集分辨率高
   */
  cameraCaptureHeight: number = 720;
  /**
   * 摄像头采集分辨率码率
   */
  cameraCaptureFrameRate: number = 18;
  /**
   * 屏幕采集分辨率宽
   */
  screenCaptureWidth: number = 1280;
  /**
   * 屏幕采集分辨率高
   */
  screenCaptureHeight: number = 720;
  /**
   * 屏幕采集帧率
   */
  screenCaptureFrameRate: number = 10;
  /**
   * 屏幕录制分辨率宽
   */
  screenRecordWidth: number = 1280;
  /**
   * 屏幕录制分辨率高
   */
  screenRecordHeight: number = 720;
  /**
   * 会场svc层级设置
   */
  svc: string = "1 240 250 480 600";
  /**
   * 会场最大帧率
   */
  maxFrameRate: number = 18;
  /**
   * 排队远程设置远程录制
   */
  remoteRecord: boolean = true;
  /**
   * 订阅成员画面分辨率
   */
  panticipantVideoSize: JRTCVideoSize = new JRTCVideoSize(640, 360);
  /**
   * 订阅屏幕共享画面分辨率
   */
  screenVideoSize: JRTCVideoSize = new JRTCVideoSize(1280, 720);
}
```

## **4.8 客户经理进入业务流程** 

```
/**
```

#### `* 经理加入业务` 

- `加会结果通过 onRecordStateChanged, onFinish 回调` 

- `@param orderId 订单编号(必填)` 

- `@param roles 参会角色(必填)多个情况下以英文逗号 "," 分割` 

- `@param config 业务相关配置信息(必填)` 

- `@param location 地理位置 , 可为 null` 

- `@return 调用是否成功` 

```
 */
public startRecordForManager(orderId: string, config: RecordConfig, roles?:
string, location?: Location): boolean;
```

## **4.9 客户进入业务流程** 

- `/**` 

#### `* 客户加入业务` 

- `加会结果通过 onRecordStateChanged, onFinish 回调` 

- `@param orderId 订单编号(必填)` 

- `@param roles 参会角色(必填)多个情况下以英文逗号 "," 分割` 

- `@param config 业务相关配置信息(必填)` 

- `@return 调用是否成功` 

- `*/` 

```
public startRecordForClient(orderId: string, config: RecordConfig, roles?:
string): boolean;
```

## **4.10 结束业务** 

```
/**
 * 结束业务
```

- `结果通过 onRecordStateChanged, onFinish 回调` 

- `@param orderId 订单号` 

```
 * @return 调用是否成功
 */
public finishRecord(orderId: string): boolean
```

## **4.11 文件上传** 

```
/**
 * 上传文件, 仅上传获取上传结果
 * 上传结果通过 onUploadRecordResult 回调
 * @param order 订单编号id
 */
public uploadRecordFileByOrderId(order: string)
/**
```

- `上传文件,实时显示上传进度弹窗并显示结果` 

- `上传结果通过 onUploadRecordProgress 回调` 

- `@param activity 弹窗显示的界面` 

```
 * @param order 订单编号id
 */
public uploadRecordFileByOrderIdWithDialog(activity: Ability, order: string)
```

## **4.12 查询本地订单数据** 

```
/**
 * 查询本地订单数据
 * 查询结果通过 onRecordEntitiesResult 回调
 * @param order 订单号
 */
public searchDataByOrderId(order?: string)
```

## **4.13 发送会议消息** 

```
/**
 * 发送会议消息
 * @param type 消息类型
```

- `@param content 消息内容` 

- `@param userId 发给的用户 id, 空值传给会议所有成员` 

```
 * @return
 */
public sendMessage(type: string, content: string, userId: string): boolean;
```

## **4.14 查询订单是否正在办理** 

```
/**
 * 查询订单是否正在办理
 * 查询结果通过 onCheckOrderInProcessResult 回调
 * @return 调用成功或失败
 */
public checkOrderInProcess(orderId: string)
```

## **4.15 注册回调** 

```
/**
 * 注册回调
 */
public addRecordCallback(callback: RecordCallBack);
```

## **4.16 取消回调** 

```
/**
 * 取消回调
 */
public removeRecordCallBack(callback: RecordCallBack)
```

## **4.17 获取SDK版本信息** 

```
/**
 * 获取SDK版本信息
 */
public get version(): string[];
```

## **4.18 设置主窗口** 

```
/**
 * 设置主窗口
 * */
public setMainWindow(win: window.Window);
```
