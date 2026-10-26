天融信 TopSAP SDK HarmonyOS API 使用说明 

# 天融信TopSAP SDK HarmonyOS API 说明文档 

天融信 TopSAP SDK HarmonyOS API 使用说明 

# 目录 

##### 目录 

|一、**SDK** 简要介绍**...........................................................................................................................2**|
|---|
|二、**SDK** 运行要求**............................................................................................................................ 2**|
|1. VPN网关要求.............................................................................................................................................2|
|2. 平台要求......................................................................................................................................................2|
|三、集成前准备**................................................................................................................................. 3**|
|1. 测试环境准备............................................................................................................................................ 3|
|2. HARMONYOS平台准备..............................................................................................................................3|
|四、**SDK** 内容说明**............................................................................................................................ 5**|
|五、**API** 文档说明**............................................................................................................................. 5**|
|1. 口令认证......................................................................................................................................................5|
|2. 证书认证......................................................................................................................................................7|
|3. 口令+动态码认证.....................................................................................................................................9|
|4. 隧道状态查询..........................................................................................................................................11|
|5. 退出............................................................................................................................................................. 12|
|6. 修改密码....................................................................................................................................................13|
|六、错误码说明**...............................................................................................................................13**|
|七、功能说明**...................................................................................................................................17**|
|八、注意事项**...................................................................................................................................17**|

1 

天融信 TopSAP SDK HarmonyOS API 使用说明 

## 一、 **SDK** 简要介绍 

随着 HarmonyOS 平台的普及与用户对应用开发个性化需求的不断增长,为 了充分发挥 VPN 网关功能,满足客户的多样化业务场景,我们特别推出了基于 SSLVPN 协议的 SDK 开发包。本 SDK 专为鸿蒙 5 及以上系统设计,旨在为 开发者提供便捷、高效且稳定的二次开发工具,助力打造具备安全远程访问能力 的定制化应用。该 SDK 版本具有以下特点: 

#### **1.** 系统兼容 

支持HarmonyOS 5 或以上系统,确保了在先进操作系统上的稳定运行与功能 发挥,为用户带来流畅且安全的VPN 服务体验。 

#### **2.** 升级便捷 

每次版本升级时,开发者只需进行简单的库文件替换操作,无需因SDK 功 能的拓展(如新增平台支持或工作模式变更)而修改额外代码,极大降低了升级 维护成本与技术门槛,保障了业务的连续性与稳定性。 

#### **3.** 示例Demo 附带 

SDK 包内附有示例Demo,通过简洁明了的代码结构,为开发者呈现最基本 的API 使用方法与应用场景演示,便于开发者快速上手,理解SDK 的核心功能 与调用逻辑,为后续的深入开发奠定坚实基础。 

## 二、 **SDK** 运行要求 

### **1. VPN** 网关要求 

  目前支持 VPN 网关 NGVONE 1.0 、NGVONE2.0 版本。 

### **2.** 平台要求 

####   开发工具的版本 

DevEco Studio 5.0.2 Release 或以上。 

2 

天融信 TopSAP SDK HarmonyOS API 使用说明 

  API 的版本 API Version 14 或以上。 

  开发设备 OS 的版本 Harmony OS 5.0.0.126 SP8 或以上。 

## 三、 集成前准备 

### **1.** 测试环境准备 

在使用之前请配置好用户和资源,确定 VPN 地址和用户可用,一切正常。 如果要在 SDK 中使用同一 VPN 帐号,请给用户配置多点登录功能。资源的配置 请配置全网接入类型的资源,针对资源配置方面有问题请联系管理员,如贵单位 管理员不知道,请咨询天融信客服或相关销售。 

获取 SDK 请联系天融信客服或相关销售,SDK 中需包含名为 TopSecSdk.har 的文件。 

### **2. HarmonyOS** 平台准备 

鉴于目前鸿蒙开发使用华为提供的集成开发环境 DevEco Studio, 所以对鸿 蒙平台提供 har 静态库。SDK 中所包含示例 Demo 也为 DevEco Studio 环境下开 发。故在开发时建议使用集成开发环境 DevEco Studio。在项目中集成 SDK 步骤 如下: 

a) 将 SDK 中 TopSecSdk.har 拷贝至项目中 libs 目录下。 

3 

天融信 TopSAP SDK HarmonyOS API 使用说明 

- b) 修改项目中 app 目录下 oh-package.json5,将 sdk 加入到 dependencies 标 签内。 

- c) 将 Demo 中代码片段,复制到项目工程对应位置,回调信息以 emitter 消 

   - 息形式通知应用,详见 SDK Demo 源码。 

- d) 新增获取 sdk 版本 

let sdk_version = HAR_VERSION 

- e) 新增 sdk 初始化接口 

   - 包含初始化存储目录日志目录 

   - Ex: download/com.topsec.demo/sslvpn. 

TopSecVpnManage.getInstance().initSDK(this.context) 

4 

天融信 TopSAP SDK HarmonyOS API 使用说明 

## 四、 **SDK** 内容说明 

#### **1. SDK** 压缩包说明 

SDK 解压出的文件 

TopSecSDKDemo.zip :实例源码 

天融信TopSAP SDK HarmonyOS API 说明文档.pdf :集成说明文档 Libs :SDK 库文件 

#### **2. SDK** 权限说明 

|**设备权限**|**申请目的**|**申请授权方式**|**是否可关闭**|
|---|---|---|---|
|网络请求权限|请求网络数据|代码设置|否|
||(ohos.permission.INTERNET)|||
|获取网络信息|用于网关能力获取设备网络信息|代码设置|否|
|权限|(ohos.permission.GET_NETWORK_INFO)|||
|获取wifi 信息|用于网关能力获取wifi 信息|代码设置||
|权限|(ohos.permission.GET_WIFI_INFO)|||

## 五、 **API** 文档说明 

### **1.** 口令认证 

|类名|IVPNHelper|
|---|---|
|方法|loginVOne(baiActInfo: BaseAccountInfo): number|

5 

天融信 TopSAP SDK HarmonyOS API 使用说明 

|描述|sdk登录接口,口令认证【必选接口】异步调用|
|---|---|
|参数|入参: m_iLoginType:登录类型 int类型 【1、口令;2、证书;3、 双因子;】必选,类型为1。 m_iAuthType:验证类型 int类型【1、口令,用户+密码;2、证 书:文件证书+证书密码,硬件证书-国密协议+证书密码,硬件证书- 国际协议+证书密码;3、双因子口令密码+2;】必选,类型为1。 m_iExtraCodeType:验证码类型 int类型 m_iProtocolType:协议类型 int类型【1、国密协议;2、国际 协议;】必选 m_strAccount:登录用户名 string类型必选 m_strLoginPasswd:账号密码 string类型必选 m_strCerPath:证书路径 string类型 m_strCerPasswd:证书密码 string类型 m_strExtraCode:附加码 string类型 m_strPhoneFeatureCode:手机特征码string类型 m_strPackageName:当前程序包名string类型 m_strSIM:SIM认证短信验证码 string类型 m_strFingerPrint:证书登录指纹 string类型 m_strContainer:证书登录容器名字 string类型 m_strAuthCode:用户登录auth code string类型|
|返回值|number 类型0:调用成功,-1:调用失败|
|示例|设置登录参数: switch (userInfo.getLoginType()) { case VPNUtils.LOGINTYPE_PASSWORD: //口令登录 this.baseAccountInfo.m_iLoginType = LoginType.LOGIN_TYP E_CODEWORD; this.baseAccountInfo.m_strAccount = userInfo.getPassword_ UserName(); this.baseAccountInfo.m_strLoginPasswd = userInfo.getPass word_Password();|

6 

|天融信TopSAP SDK HarmonyOS API使用说明|
|---|
|this.baseAccountInfo.m_strPackageName = VPNUtils.getInst ance().getBundleName(); this.baseAccountInfo.m_strPhoneFeatureCode = VPNUtils.ge tInstance().getPhoneFearureCode(); this.baseAccountInfo.m_iExtraCodeType = userInfo.getcode Type(); this.baseAccountInfo.m_strExtraCode = userInfo.getCodeInf o();|
|口令登录: public loginVone():void { this.initLoginMessage() VPNService.getInstance().loginVOne(this.baseAccountInfo) }|

### **2.** 证书认证 

|类名|IVPNHelper|
|---|---|
|方法|loginVOne(baiActInfo: BaseAccountInfo): number|
|描述|sdk登录接口,口令认证【必选接口】异步调用|
|参数|入参:|
||m_iLoginType:登录类型 int类型 【1、口令;2、证书;3、|
||双因子;】必选,类型为2。|
||m_iAuthType:验证类型 int类型【1、口令,用户+密码;2、证|
||书:文件证书+证书密码,硬件证书-国密协议+证书密码,硬件证书-|
||国际协议+证书密码;3、双因子口令密码+2;】必选,类型为2。|
||m_iExtraCodeType:验证码类型 int类型|
||m_iProtocolType:协议类型 int类型【1、国密协议;2、国际|
||协议;】必选|

7 

||天融信TopSAP SDK HarmonyOS API使用说明|
|---|---|
||m_strAccount:登录用户名 string类型必选 m_strLoginPasswd:账号密码 string类型必选 m_strCerPath:证书路径 string类型 m_strCerPasswd:证书密码 string类型|
||m_strExtraCode:附加码 string类型 m_strPhoneFeatureCode:手机特征码string类型 m_strPackageName:当前程序包名string类型|
||m_strSIM:SIM认证短信验证码 string类型|
||m_strFingerPrint:证书登录指纹 string类型|
||m_strContainer:证书登录容器名字 string类型|
||m_strAuthCode:用户登录auth code string类型|
|返回值|number 类型0:调用成功,-1:调用失败|
|示例|设置登录参数: switch (userInfo.getLoginType()) { case VPNUtils.LOGINTYPE_CERT: this.baseAccountInfo.m_iLoginType = LoginType.LOGIN_TYP E_CERT;|
||this.baseAccountInfo.m_iAuthType = VerifyType.VERIFY_TY PE_SOFTCERT;|
||this.baseAccountInfo.m_iProtocolType = ProtocolType.PROT OCOL_TYPE_INTERN; // this.baseAccountInfo.m_strCerPath = FileUtils.getInstanc e().getSavePath() + "/" + userInfo.getCert_CertName(); this.baseAccountInfo.m_strCerPath = userInfo.getCert_CertN ame();|
||this.baseAccountInfo.m_strCerPasswd = userInfo.getCert_Pa ssword();|
||this.baseAccountInfo.m_strPackageName = VPNUtils.getInst ance().getBundleName();|
||this.baseAccountInfo.m_iExtraCodeType = userInfo.getcode Type();|
||this.baseAccountInfo.m_strExtraCode = userInfo.getCodeInf|

8 

|天融信TopSAP SDK HarmonyOS API使用说明|
|---|
|o();|
|if (null == this.baseAccountInfo.m_strPhoneFeatureCode) { this.baseAccountInfo.m_strPhoneFeatureCode = VPNUtils.|
|getInstance().getPhoneFearureCode(); }|
|证书登录:|
|public loginVone():void { this.initLoginMessage()|
|VPNService.getInstance().loginVOne(this.baseAccountInfo) }|

### **3.** 口令 **+** 动态码认证 

|类名|IVPNHelper|
|---|---|
|方法|loginVOne(baiActInfo: BaseAccountInfo): number 口令|
||continueToLoginWithExtraCode(eExtraLoginInfo:ExtraLoginInfo):num|
||ber; 动态码。|
|描述|sdk登录接口,口令认证【必选接口】异步调用|
|参数|口令入参:|
||m_iLoginType:登录类型 int类型 【1、口令;2、证书;3、|
||双因子;】必选,类型为3。|
||m_iAuthType:验证类型 int类型【1、口令,用户+密码;2、证|
||书:文件证书+证书密码,硬件证书-国密协议+证书密码,硬件证书-|
||国际协议+证书密码;3、双因子口令密码+2;】必选|
||m_iExtraCodeType:验证码类型 int类型|
||m_iProtocolType:协议类型 int类型【1、国密协议;2、国|

9 

||天融信TopSAP SDK HarmonyOS API使用说明|
|---|---|
||际协议;】必选|
||m_strAccount:登录用户名 string类型必选 m_strLoginPasswd:账号密码 string类型必选|
||m_strCerPath:证书路径 string类型|
||m_strCerPasswd:证书密码 string类型 m_strExtraCode:附加码 string类型 m_strPhoneFeatureCode:手机特征码string类型 m_strPackageName:当前程序包名string类型|
||m_strSIM:SIM认证短信验证码 string类型|
||m_strFingerPrint:证书登录指纹 string类型|
||m_strContainer:证书登录容器名字 string类型|
||m_strAuthCode:用户登录auth code string类型 动态码入参: m_iExtraCodeType:认证类型 m_strSMSCode:短信认证码|
||m_strDynamicCode:动态口令|
|返回值|number 类型0:调用成功,-1:调用失败|
|示例|设置登录参数: switch (userInfo.getLoginType()) { case VPNUtils.LOGINTYPE_PASSWORD: //口令登录 this.baseAccountInfo.m_iLoginType = LoginType.LOGIN_TY PE_CODEWORD; this.baseAccountInfo.m_strAccount = userInfo.getPassword_ UserName();|
||this.baseAccountInfo.m_strLoginPasswd = userInfo.getPass word_Password();|
||this.baseAccountInfo.m_strPackageName = VPNUtils.getInst ance().getBundleName();|
||this.baseAccountInfo.m_strPhoneFeatureCode = VPNUtils.ge tInstance().getPhoneFearureCode();|
||this.baseAccountInfo.m_iExtraCodeType = userInfo.getcode Type();|

10 

天融信 TopSAP SDK HarmonyOS API 使用说明 

|this.baseAccountInfo.m_strExtraCode = userInfo.getCodeInf o(); 口令登录: public loginVone():void { this.initLoginMessage() VPNService.getInstance().loginVOne(this.baseAccountInfo) }|
|---|
|设置动态码: public continueToLoginWithExtraCode(code:string) { let eExtraLoginInfo = new ExtraLoginInfo(); eExtraLoginInfo.m_strSMSCode = code; eExtraLoginInfo.m_iExtraCodeType = ExtraCodeType.EXTRA_CO DE_SMS; VPNService.getInstance().continueToLoginWithExtraCode(eExtra LoginInfo) }|

### **4.** 隧道状态查询 

|类名|IVPNHelper|
|---|---|
|方法|getTunnelInfo(): string;|
|描述|sdk获取隧道信息,【非必选接口】异步调用|
|参数||
|返回值|string类型,|
||m_etsTunnelState:隧道状态|
||m_iTunnelType:隧道类型|
||m_iSendPacketCount:发送数据总数|
||m_iRecvPacketCount:接受数据总数|
||m_iLastSendBytes:发送数据字节总数|

11 

||天融信TopSAP SDK HarmonyOS API使用说明|
|---|---|
||m_iLastRecvBytes:接收数据字节总数 m_fSendSpeed:发送速度 m_fRecvSpeed:接受速度 m_tmLastUpdateTime:最后更新时间 m_lTunnelActiveTime:隧道时间 m_uiupdateClientState:接收速度|
|示例|获取隧道状态: setInterval(()=>{ let svmsgTune = new SVMessage(); svmsgTune.type = EventConstant.APP_INPUT_INDEX_INFO; svmsgTune.message = VPNService.getInstance().getTunnelInf o(); svmsgTune.gatway = VPNService.getInstance().getServerVersi on(); svmsgTune.username = DataPreferencesUtils.getInstance(get Context()).getValueForString(PreferenceConstant.SP_VIRTUAL_IP, '') //console.info('getTunnelInfo ===========' + svmsgTune.m essage) GlobalData.getInstance().getServerWorker().postMessage(svms gTune) }, 1000)|

### **5.** 退出 

|类名|IVPNHelper|
|---|---|
|方法|logoutVOne():number;|
|描述|SDK 登出接口,【非必选接口】异步接口|
|参数|无|

12 

天融信 TopSAP SDK HarmonyOS API 使用说明 

|返回值|number 类型0:调用成功,-1:调用失败|
|---|---|
|示例|退出登录:|
||Public logout():void{|
||VPNService.getInstance().logoutVOne(); }|

### **6.** 修改密码 

|类名|IVPNHelper|
|---|---|
|方法|修改密码,支持首次登录修改密码 modifyPassword(strNewPasswd:string, strOldPasswd:string):number;|
|描述|修改密码;支持首次首次登录修改密码。|
|参数|NewPasswd:新密码。OldPasswd:旧密码。|
|返回值|number 类型0:调用成功,-1:调用失败|
|示例|修改密码: Public modifyPassword(strNewPasswd: string, strOldPasswd: strin g) {|
||VPNService.getInstance().modifyPassword(strNewPasswd, strOl dPasswd) }|

## 六、 错误码说明 

|错误码|错误信息|错误场景|
|---|---|---|
|-1|当前操作失败||
|-2|用户传入了非法的参数||

13 

天融信 TopSAP SDK HarmonyOS API 使用说明 

|-5|内存分配失败|
|---|---|
|-6|用户名或密码错误|
|-7|无法连接到网络服务器或给定的网 络地址不存在|
|-8|Cookie为空|
|-9|与服务器的网络连接已被关闭|
|-11|数据接收失败或数据包不完整"|
|-12|SELECT操作执行失败|
|-13|初始化本地套接字失败|
|-14|非法的Cookie|
|-15|无法和Vone建立安全连接|
|-18|该用户已经登录,当前操作已被拒绝|
|-19|用户尚未登录,请登录|
|-20|当前用户未正确配置可访问的资源, 请与管理员联系|
|-21|当前VPN服务已经在运行中|
|-22|VPN服务已关闭,安全隧道已断开|
|-23|更新数据包失败|
|-24|服务端无响应,未接收到任何数据|
|-25|数据接收发生错误,原因未知|
|-26|发送数据0字节|
|-27|数据发送发生错误,原因未知|
|-28|SSL初始化时发生协议解析错误|
|-29|SSL初始化时创建内容上下文失败|
|-30|VPN服务尚未被实例化|
|-31|项目已存在|
|-32|设置的默认缓存空间不够|
|-33|您当前网络不稳定|
|-34|连接到服务器超时|
|-36|网关错误,无法正常访问|
|-37|等待服务端响应超时|
|-38|非法的地址,连接失败|

14 

天融信 TopSAP SDK HarmonyOS API 使用说明 

|-39|非法的库文件,加载失败|
|---|---|
|-40|当前调用不支持|
|-46|系统内部通信被异常中断,请重试|
|-47|服务正在启动,请稍候|
|-48|配置或启动虚拟网卡失败|
|-49|连接服务器异常,握手失败|
|-50|解码数据不够完整,还需要读取更多 的数据|
|-53|尝试创建VPN隧道失败|
|-54|网关指定功能模块尚未开启,请联系 管理人员开启|
|-76|初始化VPN配置失败,原因未知|
|-85|检测到您本机网络波动,VPN正在尝 试恢复连接|
|-87|当前网关版本不支持|
|-100|IP或掩码格式错误|
|-101|服务器下发给客户端的虚拟地址与 本机IP有冲突,请在服务器重新配置 虚拟地址池|
|-104|与服务器握手失败|
|-105|用户正在进行登录中,请勿重复登录|
|-134|解析数据头失败|
|-40005|生成图形识别码出错|
|-40006|发送图形识别码出错|
|-40014|用户名或口令为空|
|-40016|口令输入错误次数大于3次|
|-40018|验证码输入错误|
|-40019|登录用户被锁定|
|-40020|登录用户被临时锁定|
|-40021|登录用户IP地址非法|
|-40022|登录用户密码有效期已到|
|-40023|此登录用户密码太简单,要求修改密|

15 

天融信 TopSAP SDK HarmonyOS API 使用说明 

||码|
|---|---|
|-40024|第一次登录,请修改初始密码|
|-40025|用户名或口令不正确,认证信息不正 确|
|-40026|密码错误|
|-40027|用户需要证书认证|
|-40028|用户已存在|
|-40030|SSL连接无效|
|-40031|未提交用户证书|
|-40037|修改密码出错|
|-40051|获取资源列表失败|
|-40052|找回密码失败|
|-40058|修改的密码太短|
|-40059|修改的密码至少包含一个大写字母|
|-40060|修改的密码至少包含一个小写字母|
|-40061|修改的密码至少包含一个数字|
|-40062|修改的密码至少包含一个符号|
|-40063|修改的密码不能包含用户名|
|-40064|用户禁止修改密码|
|-40078|改密码时,原密码错误|
|-40080|用户名或密码错误|
|-40081|用户名或密码错误|
|-40082|用户证书认证失败|
|-40107|用户不支持口令认证|
|-40108|用户不支持证书认证|
|-40109|用户不支持双因子认证|
|-40125|用户被禁用|
|-40127|输入用户名范围[1,-127]字节!|
|-40128|新密码长度太长|
|-40129|新密码与旧密码不能相同|
|-40132|踢出用户失败|
|-40137|用户名与证书属性不同|

16 

天融信 TopSAP SDK HarmonyOS API 使用说明 

密码修改太频繁,修改失败 

-40143 

## 七、 功能说明 

SDK 基本功能介绍: 

- 1 全网接入功能 

   - 透明模式:用户接入 SSL VPN 网关后,原有网络不受任何影响,安全访问授 权资源。 

- **2** 用户认证 支持口令认证。 

   - 支持口令+验证码。 

#### **3** 支持多种终端 

支持鸿蒙 next 手机。 

支持鸿蒙 next 平板。 

支持鸿蒙 next 电脑。 

- **4** 支持获取当前隧道流量信息 

- **5** 支持隧道状态查询 

- **6** 提供启动隧道的接口 

- **7** 提供停止隧道的接口 

- **8** 提供重启隧道的接口 

## 八、 注意事项 

1. 请先在 Demo 中自己编写测试代码,测试通过后再做集成。 

2. 对 VPN 网关配置方面的问题,请咨询天融信客服或相关销售。 

3. Demo 实例为功能演示,仅供参考。 

17
