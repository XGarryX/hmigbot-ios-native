### 北京易道博识科技有限公司 

OCR SDK 易道博识 识别 **HarmonyOS** 平台接口文档 

**2024/2/20** 

### 摘要 

本文档主要包括深度学习证件识别SDK(HarmonyOS 平台)产品技术特点、 功能、系统架构、工作流程、API 说明等内容,是用户接入证件识别SDK 的重要 参考依据。 

北京易道博识科技有限公司 www.exocr.com 

### 历史修订记录 

|版本|作者|修改日期|修改内容|
|---|---|---|---|
|V1.0.1_beta|许翔、王 朝阳|2024-02-28|初始版本,修改版式、内容等。|
|V1.0.2_beta|许翔|2024-04-22|新增自定义模式|
|V1.0.9_beta V1.1.1_beta|许翔 许翔|2024-06-17 2024-08-14|修改识别接口、新增默认模式超时检测 去除json 解析三方库,新增默认UI 配置接 口|
|V1.1.2_beta|许翔|2024-08-30|扫描识别和相册识别的算法引擎做区分|
|V1.1.3_beta|许翔|2024-09-16|适配pad 大屏幕UI 和相机|
|V1.1.4_beta|许翔|2024-09-27|适配折叠屏UI 和相机|
|V1.1.5|许翔|2024-10-20|修复Release 版SDK 获取不到算法版本和过 期时间的问题;优化横竖屏切换UI错误问题|
|V1.1.6|许翔|2024-10-24|优化自定义模式前后台切换相机流畅度|
|V1.1.7 V2.0.0|许翔 许翔|2024-12-16 2024-12-25|1. 算法更新三方库和鸿蒙版本 2. 修复质检功能不生效的问题 1.算法多平台版本对齐、身份证识别深圳居 住证过滤 2.修复释放引擎过慢导致不可多次识别的 问题 3.新增默认模式物理返回触发回调接口 setUseSystemBack|
|V2.1.0|许翔|2025-01-20|1.算法更新三方库zlib 版本 2.新增平安银行卡bin|

北京易道博识科技有限公司 www.exocr.com 

||||1.算法优化更新模糊质检模型 |
|---|---|---|---|
|V3.0.0|许翔|2025-03-10|2.更新温州银行卡bin 3.新增银行卡号识别银行信息接口 1.算法优化更新反光质检模型|
|V3.1.0|许翔|2025-03-19|2.大陆来往港澳台通行证英文姓名标点符 号识别错误修复|
|V3.2.0|许翔|2025-05-26|1. 算法优化授权流程;更新银行卡Bin 2. 修复默认模式超时不生效问题|
|V3.4.0 V3.4.1|许翔 许翔|2025-05-30 2025-06-26|1. 算法新增身份证国徽面有效期格式校验 2. 修复Mate 70Pro 无法扫描识别问题 3. 相机报错返回错误码和错误信息 1. 适配三折叠设备 2. 优化横竖屏显示 3. 新增旋转模式接口|
|V3.5.0|许翔|2025-07-10|1. 新增新老反光质检算切换接口 2. 修复相册识别质检阈值设置不生效的问 题|
|V3.5.1|许翔|2025-08-14|1.优化自定义模式下获取图片方法|
|V3.5.2|许翔|2025-08-19|1.优化打包模式|

### 目录 

###### 目录 

|摘要............................................................... 2|
|---|
|1 产品技术特点..................................................... 6|
|2 功能介绍......................................................... 7|
|2.1 识别能力....................................................7|
|2.2 证件分割....................................................7|
|2.3 证件质检....................................................8|
|2.4 License授权.................................................. 8|
|3 系统架构......................................................... 9|
|4 工作流程........................................................ 10|
|4.1 识别工作流程.............................................. 10|
|4.2 用户App 与SDK 交互过程.................................... 11|
|5 接入SDK .........................................................12|
|5.1 添加SDK 文件.............................................. 12|
|5.1.1 复制har 包.......................................... 12|
|5.1.2 添加lic 授权文件.................................... 12|
|5.1.3 ~~下载~~ ~~json~~ ~~解析库~~ ..................................... 12|
|5.2 识别引擎操作类EngineManager 接口.......................... 13|
|5.3 证件识别管理类DomCardManagerAPI 说明...................... 13|
|5.3.1 扫描接口............................................ 13|
|5.3.2 相册接口............................................ 13|
|5.3.3 自定义扫描接口...................................... 14|
|5.3.4 公共接口............................................ 14|
|5.4 类与枚举值定义............................................ 16|
|5.4.1 CardInfo ............................................ 16|
|5.4.2 RecoItem ............................................ 17|
|5.4.3 cardType ............................................ 23|

北京易道博识科技有限公司 www.exocr.com 

|5.4.4 ExStatus ............................................ 23|
|---|
|描述:默认UI 回调ExStatus 类型枚举定义........................... 23|
|6 常见问题及解决方法.............................................. 25|
|7 兼容性注意事项.................................................. 25|

## 1 产品技术特点 

- 基于深度学习技术 

- 支持预览模式下的视频流识别 

- 支持身份证件正面、反面,并能自动判断身份证件正反面 

- 支持银行卡卡号、银行、日期等信息识别 

- 支持各种双语身份证件识别 

- 头像提取 

- 图像校正 

- 支持Android、iOS、HarmonyOS 平台 

- 支持任意角度扫描模式 

- 自动对焦 

- 支持光线不足时打开闪光灯 

- SDK 执行程序体积较小,约10M; 

- 整张识别率大于98% 

- 端到端识别速度较快,身份证约400ms,银行卡约200ms 

- 支持基于License 文件授权 

- 具有良好的可扩展性,可快速支持新证件的模型化识别功能。 

北京易道博识科技有限公司 www.exocr.com 

## 2 功能介绍 

该部分主要包括DOM 产品的重点功能介绍以及与旧版SDK 的比对。整体上讲,DOM 产品相比旧版SDK 具有更全面的功能支持、更高的精度以及更好的扩展性。 

#### **2.1** 识别能力 

DOM 识别核心以深度学习技术为基础,利用CNN 和RNN 等深度神经网络强大 的自动特征编码能力,以大量样本为驱动,采用反复迭代训练的优化方式,得到 最优的,并具备强大泛化能力的移动端OCR 模型组。该组模型具有体积小、速度 快和识别精度高等特点,可以出色的满足移动端卡证等场景下的识别需求,并具 备良好的横向模型扩展能力,可以快速扩展支持新种类的证件或样本。 

相比于传统的OCR 方法,基于深度学习技术的DOM 识别核心具有大幅度领先 的识别精度,具体表现在如生僻字、少数民族证件等场景下更好的识别效果。 

#### **2.2** 证件分割 

DOM 证件分割基于深度学习图像分割技术,利用CNN 网络强大的视觉识别能 力,完成对证件等对象的高精度分割。证件分割模型采用FPN 结构,结合基于空 洞卷积和空间金字塔池化等操作的网络头部机构,能够更好地学习高级别对象语 义和低级别细节特征,并更好地分割多尺度的对象。从而具备分割精度高、体积 小、速度快等特点。 

相比传统SDK 中基于四边定位的的方法,深度学习的方法能够更好地排除背 景噪声的干扰,如存在背景线条或背景特征与证件接近的情况,从而可以得到更 精确的证件轮廓信息。 

北京易道博识科技有限公司 www.exocr.com 

#### **2.3** 证件质检 

证件质检主要完成对拍摄的证件图片中异常情况的检测,如模糊、缺角、形 变、切边、光斑以及遮挡等,并做出相应地提示,如异常类型、区域等。DOM 质 检模块采用深度学习模型和规则相结合的方式,提供更高可靠性的证件异常检测。 其中光斑、遮挡等基于深度检测模型完成,模糊、缺角、形变、切边等则基于对 证件几何特征的分析完成。 

相比现有SDK 完全基于图像分析的方法,DOM 质检具有更高的精度和更好的 可靠性。 

#### **2.4 License** 授权 

DOM 产品支持基于License 文件的授权模式,进而将SDK 版本的发布与授权 操作进行解耦,以减小不必要的版本发布流程,同时更灵活地满足客户在各种应 用场景下的授权需求。 

License 文件主要内容, 

- 授权类型 

   - 正式或测试。正式授权方式基于用户App 包名和特性进行授权,测试 授权方式则基于限时时间进行授权。 

- 授权包名列表 

Andorid、iOS、HarmonyOS 平台授权包名列表。 

- 限时时间 

授权有效期,指定测试授权方式下版本的有效期限。 

- 授权特性 

授权的特性列表,如身份证、银行卡等。 

DOM SDK 提供独立的授权接口,用户App 可以通过调用此接口完成授权操作。 成功后即可调用其它接口完成正常的识别操作。同时,SDK 也提供授权查询接口, 方便用户查看当前的授权状态信息。 

北京易道博识科技有限公司 www.exocr.com 

## 3 系统架构 

图1 系统架构图 

证件SDK 主要包含四大模块,如上图: 

#####   控制模块 

该模块是证件SDK 的控制核心,主要负责识别流程的整体调度工作,包括 准备接口、启动摄像头接收数据、传递数据到识别核心以及停止摄像头并 返回识别结果等工作。 

#####   接口模块 

用户App 通过接口模块启动或停止识别SDK,并调用SDK 完成识别任务。 

#####   摄像头驱动 

摄像头驱动模块接收来自控制模块的指令,如启动、停止等。启动后,摄 像头驱动获取视频流数据,并通过回调的方式传递回控制模块。 

#####   识别核心 

识别核心基于深度学习平台,是整个SDK 的算法核心。通过识别模型的前 向预测来完成输入证件图像的识别。返回识别结果或错误状态码。 

北京易道博识科技有限公司 www.exocr.com 

# 4工作流程 

## **4.1** 识别工作流程 

图3 识别流程图 

##### 工作步骤简单描述如下: 

1. 用户app 启动识别功能 

2. 启动摄像头 

3. 让摄像头自动对焦 

4. 接收图像数据 

5. 调用识别核心完成识别 

6. 识别成功,解析识别结果 

7. 成功,返回;失败,返回3。 

北京易道博识科技有限公司 www.exocr.com 

## **4.2** 用户 **App** 与 **SDK** 交互过程 

图3 用户App 与SDK 交互示意图

- 与用户app 的交互过程如上图,大体可分为以下步骤: 

   1. 用户App 通过用户按下按钮启动识别功能 

   2. 识别SDK 启动摄像头 

   3. 获取摄像头数据 

   4. 识别 

   5. 识别成功,返回识别结果,不成功继续获取数据并识别 

   6. 成功返回后,通过回调函数通知用户App 

   7. 用户App 读取识别结果 

   8. 用户App 填充识别模式 

北京易道博识科技有限公司 www.exocr.com 

# 5接入SDK 

如4.3,证件SDK 支持视频流和静态图识别两种模式。视频流模式下下 支持默认扫描页和自定义扫描页方式,用户可根据需求做选择。视频流模式 下证件SDK 需要相机使用权限,因此,开启识别之前调用App 需要做相机的 权限申请。打开扫描页时如果没有访问权限证件SDK 会通过回调接口通知调 用App。 

## **5.1** 添加 **SDK** 文件 

### 5.1.1 复制 **har** 包 

复制ExDomCardSDK.har 到用户工程entry 的libs 目录下,然后在 entry 目录下的oh-package.json5 文件里面添加har 依赖: 

"dependencies": { 

//exocrsdk 可自定义名字 路径可以自己设置只要传入的路径是正确的 "exocrsdk": "file:./libs/ExDomCardSDK.har" 

} 

### 5.1.2 添加 **lic** 授权文件 

将授权文件复制到手机中。然后将授权文件路径传入SDK(授权接口见 5.2,具体代码参考Demo) 

### 5.1.3 ~~下载~~ **~~json~~** ~~解析库~~ 

~~SDK 使用了三方的 json 解析库 需要输入 ohpm i class-transformer 来下载三方库 2023.08.12 不再需要三方 json 解析库~~ 

北京易道博识科技有限公司 www.exocr.com 

## **5.2** 识别引擎操作类 **EngineManager** 接口 

|接口|原型|描述|
|---|---|---|
|授权|EngineManager.getInstance().applyForAuth(licPat h,context)||
|获取SDK 版本号|EngineManager.getInstance().getSDKVersion()|返回String 类型|
|获取核心版本号|EngineManager.getInstance().getKernelVersion()|返回String 类型|
||EngineManager.getInstance().getKernelType()||
||EngineManager.getInstance().getKernelValidDate()|返回String 类型|
|获取授权包名|EngineManager.getInstance().getKernelBundleName()|返回String 类型|
|是否是测试版|EngineManager.getInstance().isBeta()|返回boolean 类型|

## **5.3** 证件识别管理类 **DomCardManagerAPI** 说明 

### 5.3.1 扫描接口 

|名称|原型|描述|
|---|---|---|
|扫描识别|DomCardManager.getInstance().recognize(ExData CallBack, getContext(), CardType)|调起相机进行扫描识 别|

### 5.3.2 相册接口 

|名称|原型|描述|
|---|---|---|
|静态图片识别|DomCardManager.getInstance().recPhoto(PhotoCa llBack,image.PixelMap,getContext(),CardType)|传入图片进行识别|

北京易道博识科技有限公司 www.exocr.com 

### 5.3.3 自定义扫描接口 

|名称|原型|描述|
|---|---|---|
|自定义扫描识别|DomCardManager.getInstance().recognizeCustom(E xCustomCallBack,getContext(),CardType)|设置回调和识别类型|

### 5.3.4 公共接口 

|名称|原型|描述|
|---|---|---|
|设置默认扫描界面 的UI 模式(默认为 四边定位)|DomCardManager.getInstance().setScanType (ScanType)|传入enum ScanType: DEFAULT_QUAD,(固定 框) SCAN_QUAD,(四边定位)|
|||NO_SCAN_QUAD(无框)|
|默认扫描界面是否 显示切换界面UI 按 钮|DomCardManager.getInstance().setUseSelectMode(bool ean)|默认为true:显示切换 界面UI 按钮|
|默认扫描界面是否 显示相册|DomCardManager.getInstance().setShowPhoto(boolean)|默认为true:显示相册 面按钮|
|设置留白大小|DomCardManager.getInstance().setMargin(number)|0-128 整数,默认为10|
|设置遮挡阈值|DomCardManager.getInstance().setCover(number)|0-1 浮点数,默认为0.2|
|设置反光阈值|DomCardManager.getInstance().setReflective (number)|0-1 浮点数,默认为0.3|
|设置过远阈值|DomCardManager.getInstance().setDistFar (number)|默认为6|
|设置扫描识别模糊|DomCardManager.getInstance().setBlurScore|0-1 浮点数,默认为|

北京易道博识科技有限公司 www.exocr.com 

|阈值|(number,number)|0.6(全图)-0.5(切图)|
|---|---|---|
|设置图片识别模糊 阈值|DomCardManager.getInstance().setPhotoBlurScore(num ber,number)|0-1 浮点数,默认为 0.6(全图)-0.5(切图)|
|设置角度变形阈值|DomCardManager.getInstance().setAngle(number)|默认为12|
|自定义扫描暂停识 别|DomCardManager.getInstance().pauseRecognizeWithStr eam()|暂停识别|
|自定义扫描停止识 别|DomCardManager.getInstance().stopRecognizeWithStre am()|停止识别|
|自定义扫描继续识 别|DomCardManager.getInstance().continueRecognizeWith Side()|继续识别|
|自定义扫描退出识 别|DomCardManager.getInstance().stopRecognize ()|退出识别|
|设置闪光灯|DomCardManager.getInstance().setFlashMode (boolean)|打开闪光灯:true 关闭闪光灯:false|
|默认模式超时|DomCardManager.getInstance().setTimeOut(number)|设置超时毫秒,默认为 10000|
|默认扫描界面设置 提示文本颜色|DomCardManager.getInstance().setErrorTextColor(num ber)|默认为红色|
|默认扫描界面设置 提示文本大小|DomCardManager.getInstance().setErrorTextSize(numb er)|默认为16fp|
|默认扫描界面是否 显示logo|DomCardManager.getInstance().setShowLogo (boolean)|默认为true:显示logo|
|默认扫描物理返回 触发回调|DomCardManager.getInstance().setUseSystemBack (boolean)|默认为false:不触发|
|设置顶部按钮顶部 距离|DomCardManager.getInstance().setTopMargin(number)|默认为0|

北京易道博识科技有限公司 www.exocr.com 

|根据银行卡号识别 银行信息|DomCardManager.getInstance().getBankInfoB yBankNumber(number)|返回: undefined|CardInfo|
|---|---|---|
|设置忽略模糊质检|DomCardManager.getInstance().setIgnoreBlu r(boolean)|默认:false 不忽略|
|设置忽略反光质检|DomCardManager.getInstance().setIgnoreRef lective(boolean)|默认:false 不忽略|
|设置忽略缺角、过远 变形质检|DomCardManager.getInstance().setIgnoreSha pe(boolean)|默认:false 不忽略|
|设置忽略遮挡质检|DomCardManager.getInstance().setIgnoreOcc lusion(boolean)|默认:false 不忽略|
|设置旋转模式|DomCardManager.getInstance().setAllowRota tion(boolean)|默认:false|
|设置使用新反光质|DomCardManager.getInstance().setUseNewRef|默认:true 使用新反光|
|检算法|lectionAlgorithm(boolean)|质检算法|

## **5.4** 类与枚举值定义 

### 5.4.1 **CardInfo** 

##### 描述:证件识别信息类 

|成员与方法|描述|
|---|---|
|_public_ CardType _cardType_|卡证类型,1:银行卡;2:身份证。|
|public int pageType;|卡证正反面,1:人像面;2:反面|
|public EXIDCardPage idCardPage;|卡证正反面,EXIDCARDFACE 为人像面,EXIDCARDBACK 为国徽 面;身份证独有属性|
|public Map<String, RecoItem> items|识别结果条目(map 的key 为条目英文)|
|public PixelMap | undefined cardImg;|识别后身份证切图。用于兼容以前版本。|

北京易道博识科技有限公司 www.exocr.com 

|public PixelMap | undefined faceImg|面部截图|
|---|---|
|public PixelMap | undefined originalImg|预览帧全图|
|public boolean isMarginComplete|留白切图后的点是否在图像外|
|public boolean isFromStream|是否是视频流识别|
|public boolean isFar|是否过近,主要针对静态图识别(老版本无)|
|public boolean isBlurred|是否模糊,主要针对静态图识别(老版本无)|
|public boolean isReflective|是否反光,主要针对静态图识别(老版本无)|
|public boolean isOutside|是否缺角,主要针对静态图识别(老版本无)|
|public boolean isDeformed|是否变形,主要针对静态图识别(老版本无)|
|public boolean isCover|是否遮挡(老版本无)|
|public int pageVersion|外国人永居证的版本2023 和2017 其他卡证为0|

### 5.4.2 **RecoItem** 

描述: 识别条目类 

|成员与方法|描述|
|---|---|
|public String chinese_key|条目名称。身份证包含姓名, 性别, 民族,住址,民身份号|
||码,出生日期,签发机关,有效期;银行卡包含number,|
||bank_name, card_name, card_type, date。|
|public String item_words|识别的条目文字|
|public String item_quad|条目坐标|
|public String item_id|条目id|

### 5.4.3 各卡证 **key-value** 对应信息 

身份证: 

北京易道博识科技有限公司 www.exocr.com 

|字段||含义|
|---|---|---|
|name|姓名||
|gender|性别||
|nation|民族||
|birth|出生||
|address|住址||
|cardNum|公民身份号码||
|issuance|签发机关||
|validDate|有效期||

##### 银行卡: 

|字段||含义|
|---|---|---|
|bankName|银行名称||
|cardName|卡名称||
|bankCardType|卡类型||
|cardNum|卡号||
|validDate|有限期||

##### 港澳台居住证: 

|字段||含义|
|---|---|---|
|name|姓名||
|gender|性别||
|birth|出生||
|address|住址||
|cardNum|公民身份号码||
|issuance|签发机关||
|validDate|有效期限||

北京易道博识科技有限公司 www.exocr.com 

|issueTimes|签发次数|
|---|---|
|passCardNum|通行证号码|

##### 香港身份证: 

|字段||含义|
|---|---|---|
|chName|中文姓名||
|gender|性别||
|enName|英文姓名||
|telegraphCode|电码||
|birth|出生日期||
|cardNum|身份证号码||
|firstIssueDate|首次签发日期||
|issueDate|本次签发日期||
|certMark|证件标记||

##### 澳门身份证: 

|字段||含义|
|---|---|---|
|chName|中文姓名||
|gender|性别||
|enName|英文姓名||
|cardNum|身份证号码||
|telegraphCode|电码||
|height|身高||
|birth|出生||
|firstIssueDate|首次发证||
|issueDate|本次发证||
|validDate|有效日期||
|certMark|证件标记||

北京易道博识科技有限公司 www.exocr.com 

MRZ 码 MRZCode 

##### 港澳台来往内地通行证: 

|字段||含义|
|---|---|---|
|chName|中文姓名||
|gender|性别||
|enName|英文姓名||
|birth|出生日期||
|cardNum|身份证号码||
|validDate|有效期限||
|issuance|签发机关||
|issuePlace|签发地点||
|renewalTimes|换证次数||
|nationality|国籍||
|IDCardName|身份证姓名||
|cardNum|身份证号码||
|MRZCode|MRZ 码||

##### 外国人永久居留证: 

|字段||含义|
|---|---|---|
|chName|中文姓名||
|gender|性别||
|enName|英文姓名||
|birth|出生日期||
|nationality|国籍||
|validDate|有效期限||
|issuance|签发机关||
|cardNum|证件号码||

北京易道博识科技有限公司 www.exocr.com 

|issuance|签发机关|
|---|---|
|oldCardnum|曾持有证件号|

##### 临时身份证: 

|字段||含义|
|---|---|---|
|name|姓名||
|gender|性别||
|nation|民族||
|birth|出生日期||
|address|住址||
|validDate|有效期限||
|issuance|签发机关||
|cardNum|公民身份号码||

##### 护照: 

|字段||含义|
|---|---|---|
|chName|中文姓名||
|gender|性别||
|name|姓名||
|nationality|国籍||
|birth|出生日期||
|birthPlace|出生地点||
|number|护照号||
|type|护照类型||
|issueDate|签发日期||
|validDate|有效期至||
|issueCountry|签发国家||

北京易道博识科技有限公司 www.exocr.com 

|issuance|签发机关|
|---|---|
|issuePlace|签发地点|
|MRZCode|MRZCode|

##### 大陆往来港澳台通行证: 

|字段||含义|
|---|---|---|
|chName|中文姓名||
|gender|性别||
|enName|英文姓名||
|cardNum|证号||
|birth|出生日期||
|validDate|有效期限||
|issuance|签发机关||
|issuePlace|签发地点||
|MRPZ|MRPZ30||

##### 营业执照: 

|字段||含义|
|---|---|---|
|unifiedSocialCreditCode|统一社会信用代码||
|company|名称||
|type|类型||
|address|营业场所||
|corporation|经营者||
|registrationCapital|注册资本||
|paidInCapital|实收资本||
|registrationDate|注册日期||
|operationPeriod|营业期限||

北京易道博识科技有限公司 www.exocr.com 

|businessScope|经营范围|
|---|---|
|composition|组成形式|
|IntegrationOfMultipleCertificates|多证合一|
|issuedDate|签发日期|

### 5.4.4 **cardType** 

##### 描述: 不同的枚举值代表不同的卡证类型 

|枚举值|描述|
|---|---|
|EXOCRCardTypeIDCARD|身份证|
|EXOCRCardTypeBankCARD|银行卡|
|EXOCRCardTypeGAT_RES_PERMIT|港澳台居住证|
|EXOCRCardTypeBUSINESS_LICENSE|营业执照|
|EXOCRCardTypeHK_IDCARD|香港身份证|
|EXOCRCardTypeMO_IDCARD|澳门身份证|
|EXOCRCardTypeGATJMLWNDTXZ|港澳台居民来往内地通行证|
|EXOCRCardTypeIDCARD_FOREIGN|外国人身份证|
|EXOCRCardTypeTMP_IDCARD|临时身份证|
|EXOCRCardTypePASSPORT|护照|
|EXOCRCardTypeDLJMLWGATTXZ|大陆居民来往港澳台通行证|

### 5.4.5 **ExStatus** 

描述 :默认UI 回调ExStatus 类型枚举定义 

|枚举值||描述||
|---|---|---|---|
|RECOGNIZE_SUCCESS|识别成功|||
|RECOGNIZE_FAILED|识别失败|||
|RECOGNIZE_CANCEL|取消识别|||
||||23 / 25|

北京易道博识科技有限公司 www.exocr.com 

|CAMERA_PERMISSION|相机权限|
|---|---|
|RECOGNIZE_TIMEOUT|超时|
|INIT_FAILED|初始化失败|
|INIT_LOAD_MODLE_FAIL|加载模型失败|

# 6常见问题及解决方法 

|序号|问题描述|常见原因|解决方法|
|---|---|---|---|
|1|Hap 文件无法运行|鸿蒙暂不支持未上架的应用 程序只装|使用命令行安装,使用hdc.exe 命令行工具, 进入cmd 命令行界面,输入hdc install 应 用路径。进行命令行安装|
|2|调用扫描识别没有 反应|1.相机权限没有开放授 2.在Hsp 中调用的sdk|1. 调用前先做相机授权 2. 在Hsp 中调用时需要更改传入的context 为let context:Context= await application.createModuleContext(getCon text(),"hsplibrary") as Context,其中 hsplibrary 为项目中真实的module 包名|

7 兼容性注意事项
