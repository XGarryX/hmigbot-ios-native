> 来源: 厂商官方文档页(T2 信源) | https://docs.geetest.com/gt4/compliance | 抓取: 2026-07-17
> 注意: 单页快照,站内其余页面见来源链接

[ 文档中心  ](https://docs.geetest.com/index.html)

搜索全网

[ 登录后台 ](https://auth.geetest.com/login) [ 注册 ](https://auth.geetest.com/register)

_ _

简体中文 

English 

> > 

[ ](/)

  * 产品介绍 
    * [产品介绍及流程](/gt4/overview/flowchart)
  * 接入指南 
    * [交付与集成说明](/gt4/handbook)
    * [快捷集成指南](/gt4/quick_integration_guide)
  * 开发文档
    * [服务端部署](/gt4/deploy/server)
    * 客户端部署

[ios](/gt4/deploy/client/ios) [Android](/gt4/deploy/client/android) [HarmonyOS](/gt4/deploy/client/harmonyos) [Web](/gt4/deploy/client/web) 小程序

[微信小程序](/gt4/deploy/client/miniprogram/wx) [支付宝小程序](/gt4/deploy/client/miniprogram/my) [字节小程序](/gt4/deploy/client/miniprogram/tt) [百度小程序](/gt4/deploy/client/miniprogram/swan) [QQ小程序](/gt4/deploy/client/miniprogram/qq) [快手小程序](/gt4/deploy/client/miniprogram/ks) [快应用](/gt4/deploy/client/miniprogram/qa) [uniapp](/gt4/deploy/client/miniprogram/uniapp) [taro](/gt4/deploy/client/miniprogram/taro)

  * API 参考
    * API

[server](/gt4/apirefer/api/server) [Web](/gt4/apirefer/api/web) [iOS](/gt4/apirefer/api/ios) [Android](/gt4/apirefer/api/android) [HarmonyOS](/gt4/apirefer/api/harmonyos) 小程序

[微信小程序](/gt4/apirefer/api/miniprogram/wx) [支付宝小程序](/gt4/apirefer/api/miniprogram/my) [字节小程序](/gt4/apirefer/api/miniprogram/tt) [百度小程序](/gt4/apirefer/api/miniprogram/swan) [QQ小程序](/gt4/apirefer/api/miniprogram/qq) [快手小程序](/gt4/apirefer/api/miniprogram/ks) [快应用](/gt4/apirefer/api/miniprogram/qa)

    * 错误码

[server](/gt4/apirefer/errorcode/server) [Web](/gt4/apirefer/errorcode/web) [iOS](/gt4/apirefer/errorcode/ios) [Android](/gt4/apirefer/errorcode/android) [HarmonyOS](/gt4/apirefer/errorcode/harmonyos)

  * [ 业务容灾](/gt4/bypass)
  * [ 安全合规](/gt4/compliance)
  * FAQ
    * [常见问题](/gt4/faq/other)
    * [Web FAQ](/gt4/faq/web)
    * [IOS FAQ](/gt4/faq/ios)
    * [Android FAQ](/gt4/faq/android)
    * [服务端 FAQ](/gt4/faq/server)
    * [小程序 FAQ](/gt4/faq/miniprogram)
  * 问题帮助
    * [名词解释](/gt4/help/glossary)

  * []()

# 极验行为验证第四代-合规指南

根据《个人信息保护法》、《数据安全法》、《网络安全法》等法律法规和监管部门规章要求,App开发运营者(以下简称为“开发者”)在提供网络产品服务时应尊重和保护最终用户的个人信息,不得违法违规收集使用个人信息,保证和承诺就个人信息处理行为获得最终用户的授权同意,遵循最小必要原则,且应当采取有效的技术措施和组织措施确保个人信息安全。为帮助开发者在使用【极验行为验证第四代】服务(以下称“行为验证第四代或“行为验证第四代产品和/或服务”)的过程中更好地落实用户个人信息保护相关要求,避免出现侵害最终用户个人信息权益的情形,特制定本合规使用说明,供开发者在接入使用【极验行为验证第四代】服务时参照自查和合理配置,不断提升个人信息保护水平。

## 一、行为验证第四代配置能力说明

### 1、接入/升级至满足监管新规的最新SDK版本

我们高度重视SDK的功能优化、个人信息安全和保护,将适时升级迭代SDK版本以提升产品的安全性和稳定性,确保符合相关法律法规及、监管及标准的最新合规要求。强烈建议您升级使用最新版本SDK,以便保障您正常使用SDK最新功能、避免因您更新不及时产生的不利影响(例如APP被通报或下架等)。 SDK更新后,我们会及时通过官网[【文档中心】](https://docs.geetest.com/)展示更新的内容,以便您及时了解SDK最新版本信息。同时,您通过登录用户后台获取SDK最新版本。

### 2、SDK可选个人信息的配置说明

**要求内容:** 《SDK合规使用说明》应详细说明SDK各项可选个人信息使用目的、场景及对应关闭的配置方式、示例。

**接入说明:** 行为验证第四代暂未提供可选收集的个人信息,遵照最小化收集原则,仅收集了必要的个人信息,如后期增加相关可选个人信息配置,将及时告知。

### 3、SDK可按照不同频次、精度收集个人信息的配置说明

**要求内容:** 如果SDK可按照不同频次、精度收集个人信息的,《SDK合规使用说明》应说明不同频次、精度的使用目的、场景及对应选择的配置方式、示例。

**接入说明:** 收集频次方面,行为验证第四代的数据采集仅在App调用/最终用户触发相关功能时触发,不涉及定时逻辑等频次控制选项。收集精度方面,行为验证第四代不涉及可根据精度收集个人信息的情形。

**行为验证第四代个人信息收集频次及对应配置情况:**

**设备信息**

个人信息类型 | 是否可配置 | 用途和目的 | 频次 | 端侧  
---|---|---|---|---  
设备品牌 | 不可配置 | 用于安全策略 | 每次调用被动获取 | 安卓/IOS/HarmonyOS  
设备型号 | 不可配置 | 用于安全策略 | 每次调用被动获取 | 安卓/IOS/HarmonyOS  
设备系统 | 不可配置 | 用于安全策略 | 每次调用被动获取 | 安卓/IOS/HarmonyOS  
系统版本 | 不可配置 | 用于安全策略 | 每次调用被动获取 | 安卓/IOS/HarmonyOS  
系统语言 | 不可配置 | 用于安全策略 | 每次调用被动获取 | 安卓/IOS/HarmonyOS  
设备名称 | 不可配置 | 用于安全策略 | 每次调用被动获取 | 安卓/IOS  
内存大小 | 不可配置 | 用于安全策略 | 每次调用被动获取 | 安卓/IOS  
运营商名称 | 不可配置 | 用于安全策略 | 每次调用被动获取 | 安卓/IOS  
屏幕高度 | 不可配置 | 用于安全策略 | 每次调用被动获取 | 安卓/IOS  
屏幕宽度 | 不可配置 | 用于安全策略 | 每次调用被动获取 | 安卓/IOS  
是否为平板 | 不可配置 | 用于安全策略 | 每次调用被动获取 | 安卓/IOS  
OAID | 用户可配置 | 业务数据支撑 | 每次调用被动获取 | 安卓  
  
**网络信息**

个人信息类型 | 是否可配置 | 用途和目的 | 频次 | 端侧  
---|---|---|---|---  
IP | 不可配置 | 用于支撑业务及安全策略 | 每次调用被动获取 | 安卓/IOS/HarmonyOS/WEB/小程序  
是否 WI-FI | 不可配置 | 用于支撑业务及安全策略 | 每次调用被动获取 | 安卓/IOS/HarmonyOS/WEB/小程序  
网络制式 | 不可配置 | 用于支撑业务及安全策略 | 每次调用被动获取 | 安卓/IOS/HarmonyOS/WEB/小程序  
  
### 4、SDK申请系统权限的说明

**要求内容:** 《SDK合规使用说明》应详细说明SDK所需的系统权限与各业务功能间的关系,并说明权限申请时机。

**接入说明:** 对于行为验证第四代可选申请的系统权限,您可以参考相关如下表格的内容,详细了解相关权限与各业务功能的关系及其申请时机。行为验证第四代不主动申请可选系统权限,但相关权限的不申请将会对其对应的功能造成影响,您可以结合业务实际需要进行合理配置。

**安卓操作系统应用权限列表:**

权限 | 权限类别 | 用途和目的 | 申请时机  
---|---|---|---  
android.permission.INTERNET | 必选 | 设备访问网络 | App 首次安装  
  
**iOS操作系统应用权限列表:**

权限 | 权限功能说明 | 用途和目的 | 申请时机  
---|---|---|---  
Cellular | 可选 | 进行网络请求 | 调用时通过蜂窝网络访问网络  
  
**鸿蒙操作系统应用权限列表:**

权限 | 权限类别 | 用途和目的 | 申请时机  
---|---|---|---  
ohos.permission.INTERNET | 必选 | 设备访问网络 | App 首次安装  
  
### 5、SDK初始化及业务功能调用时机

**要求内容:** 《SDK合规使用说明》应详细说明SDK初始化及各项业务功能接口合规调用时机。App应当在App登录注册页面及App首次运行时,通过弹窗、文本链接及附件等简洁明显且易于访问的方式,向最终用户告知涵盖个人信息处理主体、处理目的、处理方式、处理类型、保存期限等内容的个人信息处理规则,并且获得最终用户授权同意后才能处置最终用户数据。

**接入说明:** 请务必在用户同意您App中的隐私政策后,再进行行为验证第四代的初始化。用户同意隐私政策之前,避免动态申请涉及用户个人信息的敏感设备权限;用户同意隐私政策前,您应避免私自采集和上报个人信息。当您的App未向用户提供服务时,例如App在后台运行时,请勿请求行为验证第四代的相关服务。具体的初始化时机可以详细查阅相关接入文档的内容。

**IOS集成初始化示例与详细文档:[详细文档地址](https://docs.geetest.com/gt4/deploy/client/ios)**

初始化验证管理器`GTCaptcha4Session`的实例, 在`UIButton`初始化方法中对`GTCaptcha4Session`实例调用注册方法以获得注册数据:
    
    
    #define captchaID @"xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"  
      
    @interface ViewController () <GTCaptcha4SessionTaskDelegate>  
      
    @property (strong, nonatomic) IBOutlet UIButton *startBtn;  
      
    @property (nonatomic, strong) GTCaptcha4Session *captchaSession;  
      
    @end  
      
    @implementation ViewController  
      
    - (GTCaptcha4Session *)captchaSession {  
        if (!_captchaSession) {  
            _captchaSession = [GTCaptcha4Session sessionWithCaptchaID:captchaID];  
            /// 如需修改默认配置  
            /// 可选择下面注释的方式创建实例  
            // GTCaptcha4SessionConfiguration *config = [GTCaptcha4SessionConfiguration defaultConfiguration];  
            // config.timeout = 8.0f;  
            // ...  
            // _captchaSession = [GTCaptcha4Session sessionWithCaptchaID:captchaID configuration:config];  
              
            _captchaSession.delegate = self;  
        }  
          
        return _captchaSession;  
    }  
      
    - (void)viewDidLoad {  
        [super viewDidLoad];  
          
        // 提前初始化验证会话,如果不在此位置调用,将使用懒加载模式  
        [self captchaSession];  
          
        [self.startBtn addTarget:self action:@selector(start) forControlEvents:UIControlEventTouchUpInside];  
    }  
      
  
---  
`

**Android集成初始化示例与详细文档:[详细文档地址](https://docs.geetest.com/gt4/deploy/client/android)**
    
    
    private void click(){  
        GTCaptcha4Config config = new GTCaptcha4Config.Builder()  
                .setDebug(true) // TODO 线上务必关闭  
                .setLanguage("zh")  
                .setTimeOut(10000)  
                .setCanceledOnTouchOutside(true)  
                .build();  
        gtCaptcha4Client = GTCaptcha4Client.getClient(activity)  
                .init("your captcha_id", config)  
                .addOnSuccessListener(new GTCaptcha4Client.OnSuccessListener {  
                    @Override  
                    public void onSuccess(boolean status, String response) {  
                        if(status){  
                            // TODO 开启二次验证  
                        }else {  
                            // TODO 用户答案验证错误  
                        }  
                    }  
                })  
                .addOnFailureListener(new GTCaptcha4Client.OnFailureListener {  
                    @Override  
                    public void onFailure(String error) {  
                    }  
                })  
                .verifyWithCaptcha();  
    }  
      
  
---  
  
**HarmonyOS集成初始化示例与详细文档:[详细文档地址](https://docs.geetest.com/gt4/deploy/client/harmonyos)**
    
    
    onClick(() => {  
        gtCaptcha4Config: GTCaptcha4Config =  new GTCaptcha4Config()  
                .setIsDebug(false) // TODO 线上务必关闭  
                .setLanguage("zh")  
                .setTimeOut(10000)  
                .setIsCanceledOnTouchOutside(true);  
        gtCaptcha4Client: GTCaptcha4Client = GTCaptcha4Client.getClient()  
                .init("your captcha_id", config)  
                .addOnSuccessListener({  
                async onSuccess(status: boolean, response: string) {  
                  AlertDialog.show({ message: response })  
                    if(status){  
                        // TODO 开启二次验证  
                    }else {  
                        // TODO 用户答案验证错误  
                    }  
                }  
              })  
               .addOnFailureListener({  
                 onFailure: function (error: string) {  
                   console.log('onFailure' + error);  
                 }  
              })  
               .addOnWebViewShowListener({  
                 onWebViewShow: function () {  
                   console.log(`onWebViewShow`);  
                 }  
              })  
               .verifyWithCaptcha();  
    })  
      
  
---  
  
### 6、SDK隐私政策披露要求与示例

**要求内容:** 《SDK合规使用说明》应提供App向最终用户披露SDK隐私政策条款的示例,包括SDK名称、公司名称、处理个人信息种类及目的、采集方式、隐私政策链接等内容。

**接入说明:** 开发者在App集成行为验证第四代后,行为验证第四代的正常运行会收集必要的最终用户信息,实现行为验证功能。行为验证第四代是第三代的升级版本。通过无时无刻的动态变化,适应不同的攻击方式,大幅提升黑产攻击成本,通过模块化的动态贴合,适应不同的交互环境,与您的业务场景进行深度融合,适应不同行业不同企业在不同生命周期下对安全与体验的平衡诉求。请开发者根据集成行为验证第四代的实际情况,在您App的隐私政策中,对行为验证第四代名称、公司名称、处理个人信息种类及目的、采集方式、隐私政策链接等内容进行披露。建议:确认您所接入的行为验证第四代版本和功能模块;根据上述版本和模块,从隐私政策中确定与行为验证第四代交互的数据内容;在您App的隐私政策中,以文字或列表的方式向公众披露行为验证第四代的相关信息。

**隐私政策披露示例:**

**极验行为验证第四代隐私政策:**

第三方SDK名称:极验行为验证第四代

第三方主体:武汉极意网络科技有限公司

使用目的:通过无时无刻的动态变化,适应企业在不同的攻击方式下对安全与体验的平衡诉求

收集个人信息类型:设备品牌、设备型号、设备系统、系统版本、系统语言、设备名称、内存大小、运营商名称、屏幕高度、屏幕宽度、是否为平板 、OAID、IP、是否WI-FI、网络制式

收集方式:SDK本机采集

第三方隐私政策或者协议链接:[极验行为验证第四代隐私政策](https://www.geetest.com/Private/gt4)

### 7、最终用户同意方式的示例

**要求内容:** 《SDK合规使用说明》应详细说明App获取最终用户授权同意的建议方式,其中需要取得最终用户单独同意的,应显著提示并给出示例。

**接入说明:** Demo首次运行时应当有隐私弹窗,隐私弹窗中应公示简版隐私政策内容并附完整版隐私政策链接,并明确提示最终用户阅读并选择是否同意隐私政策;隐私弹窗应提供同意按钮和拒绝同意的按钮,并由最终用户主动选择。

**披露示例:**

### 8、最终用户行使权利的配置说明

**要求内容:** 最终用户对其个人信息的处理享有知情、决定、查阅、复制、补充、更正、撤回授权同意、删除、注销账号等权利。以嵌入接口形式向最终用户提供行使权利的,应提供接口调用方式、示例。

**接入说明:** 开发者在其App中集成行为验证第四代后,行为验证第四代的正常运行会收集必要的最终用户信息用于实现一键验证功能。开发者应根据相关法律法规为最终用户提供行使个人信息主体权利的路径或功能,需要行为验证第四代配合的,请与行为验证第四代及时进行联系,我们将与开发者协同妥善解决最终用户的诉求。

投诉电话:027-87855826,电子邮箱地址:[service@geetest.com](mailto:service@geetest.com)。

__ 极验行为验证第四代

[极验行为验证第三代](/sensebot/overview/guide/operate) [极验行为验证第四代](/gt4/overview/flowchart) [极验一键认证](/onelogin/overview/prodes) [极验设备指纹](/guard/introduce/overview) [极验决策引擎](/brde/prodes)

  * 产品介绍 
    * [产品概述](/gt4/overview/prodes)
    * [通讯流程图](/gt4/overview/flowchart)
  * [快速开始](/gt4/handbook)
  * [快捷集成指南](/gt4/quick_integration_guide)
  * 部署文档 
    *     * [服务端部署](/gt4/deploy/server)
    * 客户端部署
      * [ Web ](/gt4/deploy/client/web)
      * [iOS](/gt4/deploy/client/ios)
      * [Android](/gt4/deploy/client/android)
      * [HarmonyOS](/gt4/deploy/client/harmonyos)
      * 小程序
        * [微信小程序](/gt4/deploy/client/miniprogram/wx)
        * [支付宝小程序](/gt4/deploy/client/miniprogram/my)
        * [字节小程序](/gt4/deploy/client/miniprogram/tt)
        * [百度小程序](/gt4/deploy/client/miniprogram/swan)
        * [QQ小程序](/gt4/deploy/client/miniprogram/qq)
        * [快手小程序](/gt4/deploy/client/miniprogram/ks)
        * [快应用](/gt4/deploy/client/miniprogram/qa)
        * [uniapp](/gt4/deploy/client/miniprogram/uniapp)
        * [taro](/gt4/deploy/client/miniprogram/taro)
    * 更新日志
      * [iOS](/gt4/deploy/changelog/ios)
      * [Android](/gt4/deploy/changelog/android)
      * [HarmonyOS](/gt4/deploy/changelog/harmonyos)
  * API 参考
    * [Web/H5](/gt4/apirefer/api/web)
    * [IOS](/gt4/apirefer/api/ios)
    * [Android](/gt4/apirefer/api/android)
    * [HarmonyOS](/gt4/apirefer/api/harmonyos)
    * 小程序
      * [微信小程序](/gt4/apirefer/api/miniprogram/wx)
      * [支付宝小程序](/gt4/apirefer/api/miniprogram/my)
      * [字节小程序](/gt4/apirefer/api/miniprogram/tt)
      * [百度小程序](/gt4/apirefer/api/miniprogram/swan)
      * [QQ小程序](/gt4/apirefer/api/miniprogram/qq)
      * [快手小程序](/gt4/apirefer/api/miniprogram/ks)
      * [快应用](/gt4/apirefer/api/miniprogram/qa)
    * 错误码
      * [server](/gt4/apirefer/errorcode/server)
      * [web](/gt4/apirefer/errorcode/web)
      * [iOS](/gt4/apirefer/errorcode/ios)
      * [Android](/gt4/apirefer/errorcode/android)
      * [HarmonyOS](/gt4/apirefer/errorcode/harmonyos)
  * [降级方案](/gt4/bypass)
  * [名词解释](/gt4/help/glossary)
  * 常见问题
    * [常见问题](/gt4/faq/other)
    * [Web FAQ](/gt4/faq/web)
    * [IOS FAQ](/gt4/faq/ios)
    * [Android FAQ](/gt4/faq/android)
    * [服务端 FAQ](/gt4/faq/server)
    * [小程序 FAQ](/gt4/faq/miniprogram)
  * [合规指南](/gt4/compliance)
  * [隐私政策](https://www.geetest.com/Private/gt4)

对以上内容做个评价吧:

您是否在阅读文档中遇到以下问题?

链接错误 描述过于简单 缺少示例 其他

写下您的建议:

请描述问题详情或建议~方便的话留下您的联系方式哟~

提交

提交成功

非常感谢您的反馈!
