# **智齿Harmony SDK** 

智齿客服 SDK 为企业提供了一整套完善的智能客服解决方案。智齿客服 SDK 既包含客服业务逻辑,也提供 交互界面;企业只需简单两步,便可在 APP 中集成智齿客服,让 APP 拥有 7 * 24 小时客服服务能力。 

管理员可以在后台「 首页 - 在线客服 - 设置 - 对接渠道设置 - 添加渠道 」添加 APP,然后按照本接入文档说 明完成 SDK 对接。 

智齿客服 SDK 具有以下特性: 

- 在线咨询:咨询机器人、咨询人工客服、留言、帮助中心。 

- 指定技能组接待。 

- 排队或客服不在线时引导用户留言。 

- 机器人优先模式下隐藏转人工按钮,N 次机器人未知问题问题是显现。 

- 客服满意度评价:用户主动满意度评价+用户退出时询问评价。 

- 传入用户资料:用户对接 ID + 基础资料 + 自定义字段。 

相关限制及注意事项: 

1、SDK 支持 HarmonyOS NEXT 以及以上的系统。 

## **文档介绍** 

### **● 集成流程示意图** 

## **安装** 

打开 Terminal 命令窗口,进入需要使用 SDK 的模块下,依次执行下边的安装命令进行安装,安装后同步项 目。 ```js ohpm install @sobot/sobot _common ohpm install @sobot/chat_ client 

// ohpm install @sobot/chat_core(从2.0.0版本开始不在使用) ``` 

## **功能说明** 

### **● 域名设置** 

域名说明: 

默认 SaaS 平台域名为: https://www.sobot.com。 

### 如果您是腾讯云服务,请设置为: https://www.soboten.com。 

### 如果您是本地化部署,请使用自己的部署的服务域名。 

### 示例代码: 

let chatParameter = new SobotChatParameter() //可以不设置,默认是阿里云环境域名 chatParameter.api_host = 'https://www.sobot.com' 

### **● 获取 Appkey** 

### 登录 智齿科技管理平台 获取,如图 

### **● 初始化** 

### **【注意:启动智齿 SDK 之前,需要调用初始化方法,在UIAbility的onWindowStageCreate方法中初始化该** 

**方法。】** js ZCSobotApi.init(this.context, windowStage) 

### **● 启动智齿页面** 

### **1. 启动智齿页面** 

let chatParameter = new SobotChatParameter() chatParameter.app_key = '' // appkey不能为空 ZCSobotApi.openZCChat(chatParameter); 

示例代码: 

let chatParameter = new SobotChatParameter() // appkey 必填 chatParameter.app_key = '' //注意:用户唯一标识,不能传入一样的值,选填,最大长度限制为300,建议传入 chatParameter.partnerid = '' //用户昵称,选填 chatParameter.user_nick = '' //用户姓名,选填 chatParameter.user_name = '' //用户电话,选填 chatParameter.user_tels = '' //用户邮箱,选填 chatParameter.user_emails = '' //自定义头像,选填 chatParameter.face = 'https://p3-pc.douyinpic.com/img/316630006a5c196dd9b6b~c5_300x3 //用户QQ,选填 chatParameter.qq = '' //用户备注,选填 chatParameter.remark = '' //访问着陆页标题,选填 chatParameter.visit_title = '' //访问着陆页链接地址,选填 chatParameter.visit_url = '' //用户名称 chatParameter.enterprise_name = '' ZCSobotApi.openZCChat(chatParameter); 

**2. 启动客户服务中心** 

let chatParameter = new SobotChatParameter() // appkey 必填 chatParameter.app_key = '' //注意:用户唯一标识,不能传入一样的值,选填,最大长度限制为300,建议传入 chatParameter.partnerid = '' //用户昵称,选填 chatParameter.user_nick = '' //用户姓名,选填 chatParameter.user_name = '' //用户电话,选填 chatParameter.user_tels = '' //用户邮箱,选填 chatParameter.user_emails = '' //自定义头像,选填 chatParameter.face = 'https://p3-pc.douyinpic.com/img/316630006a5c196dd9b6b~c5_300x3 //用户QQ,选填 chatParameter.qq = '' //用户备注,选填 chatParameter.remark = '' //访问着陆页标题,选填 chatParameter.visit_title = '' //访问着陆页链接地址,选填 chatParameter.visit_url = '' //用户公司名称 chatParameter.enterprise_name = '' ZCSobotApi.openZCServiceCenter(chatParameter); 

### 效果图如下: 

### **● 结束会话** 

用户在应用中退出登陆时可以调用 SDK 的注销操作(在切换账号时调用),该操作会通知服务器进行推送信 息的解绑,避免用户已退出但推送依然发送到当前设备的情况发生。 

当用于用户退出登录时调用以下方法: 

【注意:调用此方法会造成通道连接断开,此时用户将无法再收到消息。】 

ZCSobotApi.outCurrentUserZCLibInfo(); 

**● 机器人客服** 

### **1. 自定义接入模式** 

### 根据自身业务的需要,可进行以下参数配置,控制接入模式: 

#### //人工客服聊天模式下,是否使用语音功能 true使用 false不使用 默认为true 

chatParameter.isShowArtificialVoice = true 

- //是否使用机器人语音功能 true使用 false不使用 默认为false,(语音转文字功能)需要付费才可以使用 chatParameter.isShowRobotVoice = true 

- //客服模式控制 -1不控制 按照接待方案里边设置的模式运行 

//1 仅机器人 2 仅人工 3 机器人优先 4 人工优先 默认 -1 chatParameter.service_mode = -1; 

### **● 人工客服** 

### **1. 对接指定技能组** 

### 在后台获取技能组编号: 

### 在 SDK 代码中配置技能组 ID: 

/** 

* 指定技能组接待 技能组编号 */ chatParameter.group_id = ""; /** 

* 指定技能组接待 技能组名称 */ chatParameter.group_name = ""; 

注意:此字段可选,如果传入技能组 ID,那么 SDK 内部转人工之后不在弹技能组的选择框,直接跳转到传入 ID 所对应的技能组中。 

### **2. 对接指定客服** 

### 在后台获取指定客服 ID : 

在 SDK 代码中设置: 

//转接类型(0-可转入其他客服,1-必须转入指定客服) 

chatParameter.tran_flag = 0 //指定客服id chatParameter.choose_adminid = '' 

### 注意: 

choose_adminid:指定对接的客服,如果不设置,取默认。 

tran_flag :设置指定客服之后是否必须转入指定客服 0 :可转入其他客服, 1:必须转入指定客服, 注意: 如果设置为1 ,当指定的客服不在线,不能再转接到其他客服。 

**3. 设置用户自定义资料和自定义字段** 

开发者可以直接传入这些用户信息,供客服查看。 

在工作台自行配置所需要显示的字段,配置方法如下图: 

//设置用户自定义字段,key必须是后端字段对应的ID 字符串必须是json 格式,不然可能出现不显示的情况 chatParameter.customer_fields ='{"d7c262a61a0f4a1baf725e92f801a092":"aaaaaaaaaa"}' 

### 用户自定义资料 

//自定义用户料 字符串必须是json 格式,不然可能出现不显示的情况 chatParameter.params = '{"title":"标题","url1111":"https://www.baidu.com"}' 

效果图如下: 

**4. 设置指定客户排队优先接入** 

SDK 可以设置当前用户排队优先,当此用户进入排队状态时,将会被优先接待。 

//设置排队优先接入 1:优先接入  0:默认值,正常排队 chatParameter.queue_first = 0 

**5. 设置服务总结自定义字段** 

SDK 可以配置服务总结自定义字段,可以使客服更快速的对会话进行服务总结。 

- 1、获取自定义字段 ID 

- 2、设置服务总结自定义字段 (转人工支持传入服务总结参数) 

//服务总结自定义字段 字符串必须是json 格式,不然可能出现不显示的情况 chatParameter.summary_params = ''; 

### **6. 设置多轮会话接口参数** 

在使用多轮会话功能时,每一个接口我们都会传入 uid 和 mulitParams 两个固定的自定义参数,uid 是用户的 唯一标识,mulitParams 是自定义字段 json字符串、如果用户对接了这两个字段,我们会将这两个字段回传 给第三方接口、如果没有我们会传入空字段。 

//多轮会话自定义参数 字符串必须是json 格式,不然可能出现不显示的情况 chatParameter.multi_params = ''; 

### **7. 商品的咨询信息并支持直接发送消息卡片,仅人工模式下支持** 

//在用户与客服对话时,经常需要将如咨询商品或订单发送给客服以便客服查看。 chatParameter.consultationInfo = { 

// 标题 title: '商品名称发士大夫收到发送的 撒地方士大夫的说法是大发送发', //图片地址 thumbnail: "https://img0.baidu.com/it/u=2419771848,573288357&fm=253&app=120&si // 咨询内容来源地址 

url: "https://www.zhichi.com/", //标签 label: "价格1000元", //描述 

description: "我们面向全球企业,提供基于「客户联络中心」场景的一体化解决方案,包括公域+私域 isAutoSend: true,//转人工后是否自动发送 

isEveryTimeAutoSend: false //每次返回再次进入聊天页面是否都重新发送 true 每次都发,fal } 

效果图如下: 

**8. 发送订单卡片,仅人工模式下支持,订单卡片点击事件可拦截** 启动智齿客服时,自动发送订单卡片消息。 

chatParameter.orderGoodsInfo = { 

//订单状态 

// PendingPayment = 1, //待付款 

- // PendingShipment = 2, //待发货 

// DuringTransportation = 3, //运输中 

// DeliveryInProgress = 4, //派送中 

// Completed = 5, //已完成 

// ToBeEvaluated = 6, //待评价 

// Cancelled = 7, //已取消 

orderStatus: SobotOrderStatusType.PendingPayment, 

statusCustom:'',//自定义订单状态名称 只有订单状态是0时才有效,其他值还按照原有逻辑 orderUrl: "https://www.zhichi.com/", 

orderCode: "zc12321321321321",//订单编号(必填) 

totalFee: 2312,//订单总金额(单位 分) 

goodsCount: 5,//订单商品总数 

createTime: SobotDateUtil.getTodayTime(),//订单创建时间 

goods: [{//订单商品集合 

name: "sfdadsfdsa盛大范德萨分当时发送的fadsfds撒范德萨范德萨发当时s", 

pictureUrl: "https://img0.baidu.com/it/u=2419771848,573288357&fm=253&app=120 

}, { 

name: "sfd", 

pictureUrl: "https://img0.baidu.com/it/u=2419771848,573288357&fm=253&app=120 }], 

isAutoSend: true,//转人工后是否自动发送 

isEveryTimeAutoSend: true//每次返回再次进入聊天页面是否都重新发送 true 每次都发,false } 

效果图如下:

### **9. 设置用户是否是 vip 和用户 vip 级别** 

#### //可在启动智齿客服时设置 

- //指定客户是否为vip,0:普通 1:vip 

chatParameter.is_vip = 1 

//通过名称设置vip级别;vip级别可在智齿管理端(系统设置>自定义字段>客户字段)中编辑,拿到等级对应的 I chatParameter.vip_level = '尊贵' 

**10. 设置用户自定义标签** 

//可在启动智齿客服时设置 

//用户标签可在智齿管理端(系统设置>自定义字段>客户字段)中编辑,拿到用户标签对应的 ID 或者名称 //可添加多个用户标签,多个标签 ID 或者名称之间用,分割 chatParameter.user_label = "明星,记者" 

### **11. 发送自定义卡片到会话记录,以系统的方式推荐给客户** 

### 自定义卡片参数说明文档 

```arkts
chatParameter.showCustomCardAllMode = true; let cardModel = new SobotChatCustomCard(); cardModel.isCustomerIdentity = 0; // cardModel.cardId = (new Date()).toTimeString() cardModel.cardId = systemDateTime.getTime().toString() cardModel.cardGuide = "1234567890123567890123456789012345678901234567890"; cardModel.cardDesc = "通用卡片-超长描述超长描述超长描述超长描述"; cardModel.cardImg = 
```

"https://img.sobot.com/chatres/137647808eba49b8ab81b4cf0b8e8c9d/msg/20230628/4 cardModel.cardLink = 

"https://img.sobot.com/chatres/137647808eba49b8ab81b4cf0b8e8c9d/msg/20230628/4 cardModel.cardStyle = 1; cardModel.cardType = 0; 

// let map:Map<string,string> = new Map() // map.set('自定义字段1','自定义字段11') // map.set('自定义字段2','自定义字段22') // map.set('自定义字段3','自定义字段33') // map.set('自定义字段4','自定义字段44') cardModel.customField = { '自定义字段1': '自定义字段11', '自定义字段2': '自定义字段22', '自定义字段3': '自定义字段33', '自定义字段4': '自定义字段44' }; 

```arkts
let arrInfo: SobotChatCustomCardInfo[] = [] let cardInfo: SobotChatCustomCardInfo = new SobotChatCustomCardInfo() cardInfo.customCardName = "索尼WH-100OXM5头戴式智能降噪智能声控蓝牙耳机"; cardInfo.customCardQuestion = "第一个问题的标问"; cardInfo.customCardId = (new Date()).toString() + '123'; cardInfo.customCardDesc = "我是card描述我是card描述我是card描述我是card描述我是card描述 cardInfo.customCardCode = "10611111"; cardInfo.customCardLink = "https://www.sobot.com/en"; cardInfo.customCardTime = "2023-06-20 18:22:17"; cardInfo.customCardStatus = "发货中"; cardInfo.customCardThumbnail = "http://img3.sobot.com/chatres/a6c9535d3bbf48e7b7c7d5ea3533fcf3/msg/20220531/f 
```

cardInfo.customCardAmountSymbol = "¥"; cardInfo.customCardAmount = "699000.00"; cardInfo.customCardCount = "1"; // 测试数据 cardInfo.customCardLink = 

"https://img.sobot.com/chatres/137647808eba49b8ab81b4cf0b8e8c9d/msg/20230628/4 

#### // 自定义按钮 

let arrMenu: SobotChatCustomCardMenu[] = [] let menu: SobotChatCustomCardMenu = new SobotChatCustomCardMenu(); menu.menuLink = 

"http://img3.sobot.com/chatres/a6c9535d3bbf48e7b7c7d5ea3533fcf3/msg/20220531/f menu.menuType = 2; menu.menuName = "卡片发送1"; menu.menuLinkType = 0; arrMenu.push(menu) 

let menu2: SobotChatCustomCardMenu = new SobotChatCustomCardMenu() menu2.menuTip = "第1件商品的确认按钮提示语"; menu2.menuLink = 

"http://img3.sobot.com/chatres/a6c9535d3bbf48e7b7c7d5ea3533fcf3/msg/20220531/f menu2.menuType = 1; menu2.menuName = "卡片确认1"; menu2.menuLinkType = 0; arrMenu.push(menu2) cardInfo.customMenus = arrMenu; arrInfo.push(cardInfo) cardModel.customCards = arrInfo 

let cardMenu: SobotChatCustomCardMenu[] = [] let cardMenu1: SobotChatCustomCardMenu = new SobotChatCustomCardMenu() menu.menuTip = "按钮提示语"; cardMenu1.menuLink = 

"http://img3.sobot.com/chatres/a6c9535d3bbf48e7b7c7d5ea3533fcf3/msg/20220531/f cardMenu1.menuType = 0; cardMenu1.menuName = "通用卡片跳转按钮"; cardMenu1.menuLinkType = 0; cardMenu.push(cardMenu1) 

let cardMenu2: SobotChatCustomCardMenu = new SobotChatCustomCardMenu() cardMenu2.menuTip = "按钮提示语"; cardMenu2.menuLink = 

"http://img3.sobot.com/chatres/a6c9535d3bbf48e7b7c7d5ea3533fcf3/msg/20220531/f cardMenu2.menuType = 2; cardMenu2.menuName = "通用卡片发送按钮"; cardMenu2.menuLinkType = 0; cardMenu.push(cardMenu2) 

    let cardMenu3: SobotChatCustomCardMenu = new SobotChatCustomCardMenu()
    cardMenu3.menuTip = "通用卡片确认按钮提示语";
    cardMenu3.menuLink =
      "http://img3.sobot.com/chatres/a6c9535d3bbf48e7b7c7d5ea3533fcf3/msg/20220531/f
    cardMenu3.menuType = 1;
    cardMenu3.menuName = "通用卡片确认按钮";
    cardMenu3.menuLinkType = 0;
    cardMenu.push(cardMenu3)
    cardModel.cardMenus = cardMenu;
    chatParameter.customCard = cardModel;

● 评价
1. 设置评价界面
在工作台可以设置,满意度评价界面:

**2. 导航栏左侧点击返回时是否弹出满意度评价** 

注意:只有用户发送过消息,满意度评价窗口才能弹出。 

//点击返回时是否弹出弹窗(您是否结束会话?) chatParameter.isShowLeftBackPop = true 

//导航栏左侧点击返回时是否弹出满意度评价。true弹出,false不弹;默认false chatParameter.isShowBackSatisfaction = true 

效果图如下: 

**3. 导航栏右侧关闭按钮是否显示和点击时是否弹出满意度评价** 

注意:只有用户发送过消息,满意度评价窗口才能弹出。 

//设置是否显示导航栏右侧关闭按钮,true显示,false隐藏;默认false chatParameter.isShowCloseButton = true //导航栏右侧点击关闭按钮时是否弹出满意度评价。true弹出,false不弹;默认false chatParameter.isShowCloseSatisfaction = true 

**4. 左上⻆返回和右上⻆关闭时,人工满意度评价弹窗界面配置是否显示暂不评价按钮** 

/** 

- 左上⻆返回和右上⻆关闭 返回弹出评价窗口时,是否显示暂不评价按钮 默认 false (不显示) */ 

chatParameter.canBackWithNotEvaluation = true 

### **● 消息相关** 

### **1. 设置是否开启消息提醒** 

### 当用户不处在聊天界面时,收到客服的消息,APP 可以在通知栏给出提醒。 

chatParameter.msgNotificationFlag = true //消息提醒开关 

### **2. 自定义超链接的点击事件** 

/**

* 链接点击事件监听或拦截

- 

* from:超链接的位置:  EventFastMenu: 快捷菜单, EventExMenu:更多扩展菜单, EventChatMess
* eventType:超链接的位置:  EventTypeUrl:拦截Url事件,EventTypeLocaLocation:拦截位置事件,
* linkStr:拦截的内容,:例如:超链接地址
* 当返回true时,SDK 内部不处理
*/
ZCSobotApi.addLinkEventCallBack((from: SobotEventSource, eventType: SobotEventType,
linkStr: string): boolean => {

    if (eventType == SobotEventType.EventTypeUrl) {
        //举例:拦截路径里边包含 baidu 的超链接
        if (SobotStrUtil.isNotEmpty(linkStr) && linkStr.includes("baidu")) {
            SobotToastUtil.showShort("拦截超链接:" + linkStr);
            //拦截
            return true;
        }
    }
    //不拦截
    return false;
});

### **● 其它设置** 

1. 控制横竖屏显示开关

chatParameter.orientation = window.Orientation.PORTRAIT; //指定横竖屏设置,默认根据系统 

2.设置夜间(深色)模式

chatParameter.colorMode = ConfigurationConstant.ColorMode.COLOR_MODE_LIGHT //指定白天模 //chatParameter.colorMode = ConfigurationConstant.ColorMode.COLOR_MODE_DARK //指定夜间 

### **3. 智齿日志显示开关** 

/** 

- true 显示日志信息 默认false 不显示 

*/ 

ZCSobotApi.setShowDebug(true) 

### **4. 页面启动和返回监听** 

启动智齿页面或者从智齿页面返回会调用该回调,可用于埋点等功能 

/** 

- 页面状态监听,进入、关闭,可用于埋点等功能 

- from:超链接的位置:   PageChat:聊天页面,PageLeave:留言页面,PageHelperCenter:客户服务 

- pageName:页面描述 

- stateAction:超链接的位置:    PageOpenState:启动页面 ,PageCloseState:离开页面 */ 

ZCSobotApi.addPageStateCallBack((from: SobotPageSource, pageName: string, stateA 

SobotLogUtil.info(pageName + ':' + from + '--------' + stateAction); 

if ((from == SobotPageSource.PageChat || from == SobotPageSource.PageHelperCente stateAction == SobotPageStateAction.PageCloseState) { 

- //举例:从聊天页或者客服服务中心页面返回 

} 

});
