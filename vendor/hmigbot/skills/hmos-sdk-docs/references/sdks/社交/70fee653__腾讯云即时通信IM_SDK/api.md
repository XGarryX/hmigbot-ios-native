即时通信 IM 

客户端 API

版权所有:腾讯云计算(北京)有限责任公司 

第1 共117页 

即时通信 IM 

## 【版权声明】 

## ©2013-2025 腾讯云版权所有 

本文档(含所有文字、数据、图片等内容)完整的著作权归腾讯云计算(北京)有限责任公司单独所有,未经腾讯云 事先明确书面许可,任何主体不得以任何形式复制、修改、使用、抄袭、传播本文档全部或部分内容。前述行为构成 对腾讯云著作权的侵犯,腾讯云将依法采取措施追究法律责任。 

## 【商标声明】 

及其它腾讯云服务相关的商标均为腾讯云计算(北京)有限责任公司及其关联公司所有。本文档涉及的第三方主体的 商标,依法由权利人所有。未经腾讯云及有关权利人书面许可,任何主体不得以任何方式对前述商标进行使用、复 制、修改、传播、抄录等行为,否则将构成对腾讯云及有关权利人商标权的侵犯,腾讯云将依法采取措施追究法律责 任。 

## 【服务声明】 

本文档意在向您介绍腾讯云全部或部分产品、服务的当时的相关概况,部分产品、服务的内容可能不时有所调整。 您所购买的腾讯云产品、服务的种类、服务标准等应由您与腾讯云之间的商业合同约定,除非双方另有约定,否则, 腾讯云对本文档内容不做任何明示或默示的承诺或保证。 

## 【联系我们】 

我们致力于为您提供个性化的售前购买咨询服务,及相应的技术售后服务,任何问题请联系 4009100100或 95716。 

版权所有:腾讯云计算(北京)有限责任公司 

第2 共117页 

即时通信 IM 

## 客户端 API 

Web & 小程序 & uni-app 

Android 

iOS & Mac Swift Flutter Unity 

C 接口 

IM SDK 接口 

IM SDK 关键类型 

C++ 

React Native HarmonyOS 

版权所有:腾讯云计算(北京)有限责任公司 

第3 共117页 

即时通信 IM 

# 客户端 API Web & 小程序 & uni-app 

最近更新时间:2024-12-26 11:05:12 

以下视频将帮助您快速了解 Web 和小程序端 SDK API: 观看视频 

TencentCloudChat 是 IM Web SDK 的命名空间,提供了创建 SDK 实例的静态方法 create() ,以及事件常 量 EVENT ,类型常量 TYPES , 信令常量 TSignaling 。 

|API|描述|
|---|---|
|create|创建 SDK 实例。|
|SDK 实例 基本概念|说明|
|Message(消息)|IM SDK 中Message表示要发送给对方的内容,消息包括若干属性,例 如自己是否为发送者,发送人账号以及消息产生时间等。|
|Conversation(会话)|IM SDK 中Conversation分为两种: C2C(Client to Client)会话,表示单聊情况,自己与对方建立的对 话。 GROUP(群)会话,表示群聊情况下群内成员组成的会话。|
|Profile(资料)|IM SDK 中Profile描述个人的常用基本信息,例如昵称、性别、个性签 名以及头像地址等。|
|Friend(好友)|IM SDK 中Friend描述好友的常用基本信息,例如备注、分组等。|
|FriendApplication(好友 申请)|IM SDK 中FriendApplication描述好友申请的常用基本信息,例如加 好友来源、备注等。|
|FriendGroup(好友分组)|IM SDK 中FriendGroup描述好友分组的常用基本信息,例如分组名、 分组成员等。|
|Group(群组)|IM SDK 中Group表示一个支持多人聊天的通信系统,支持好友工作 群、陌生人社交群、临时会议群以及直播群。|

版权所有:腾讯云计算(北京)有限责任公司 

第4 共117页 

即时通信 IM 

|GroupMember(群成员)|IM SDK 中GroupMember描述群内成员的常用基本信息,例如 ID、 昵称、群内身份以及入群时间等。|
|---|---|
|Signaling(信令)|IM SDK 中Signaling描述信令的常用基本信息。例如 ID、邀请者 ID、 被邀请人 ID 列表,操作类型、超时时间等。|
|群提示消息|当有用户被邀请加入群组或被移出群组等事件发生时,群内会产生提示消 息,接入侧可以根据实际需求展示给群组用户或忽略。 群提示消息有多种类型,详细描述请参见 Message.GroupTipPayload。|
|群系统通知消息|当有用户申请加群等事件发生时,管理员会收到申请加群等系统消息。管理 员同意或拒绝加群申请,IM SDK 会通过群系统通知消息将申请加群等相 应消息发送给接入侧,由接入侧展示给用户。 群系统通知消息有多种类型,详细描述请参见 Message.GroupSystemNoticePayload。|
|消息上屏|用户单击发送后,事先输入的文字或选择的图片等信息显示在用户电脑屏幕 或手机屏幕上的过程。|

|API|描述|
|---|---|
|on|监听事件。|
|off|取消监听事件。|

|API|描述|
|---|---|
|registerPlugin|注册插件。|

|API|描述|
|---|---|
|setLogLevel|设置日志级别。|
|SDK 是否 ready API|描述|

版权所有:腾讯云计算(北京)有限责任公司 

第5 共117页 

即时通信 IM 

|isReady|SDK 是否 ready。SDK ready 后,开发者可调用 SDK 发送消息等 API,使用 SDK 的各项功能。|
|---|---|
|销毁 SDK 实例 API|描述|
|destroy|销毁 SDK 实例。|

|API|描述|
|---|---|
|login|登录。|
|logout|登出。|
|getLoginUser|已登录返回登录用户的 userID,未登录返回 '' 。|
|getServerTime|获取服务器时间。|

|API|描述|
|---|---|
|createTextMessage|创建文本消息。|
|createTextAtMessage|创建可以附带 @ 提醒功能的文本消息。|
|createImageMessage|创建图片消息。|
|createAudioMessage|创建音频消息。|
|createVideoMessage|创建视频消息。|
|createCustomMessage|创建自定义消息。|
|createFaceMessage|创建表情消息。|
|createFileMessage|创建文件消息。|
|createLocationMessag e|创建地理位置消息。|
|createMergerMessage|创建合并消息。|

版权所有:腾讯云计算(北京)有限责任公司 

第6 共117页 

即时通信 IM 

|downloadMergerMessa ge|下载合并消息。|
|---|---|
|createForwardMessag e|创建转发消息。|
|sendMessage|发送消息。|
|revokeMessage|撤回消息。|
|resendMessage|重发消息。|
|deleteMessage|删除消息。|
|translateText|翻译文本消息。|
|convertVoiceToText|语音转文字。|
|setMessageExtensions|设置消息扩展。|
|getMessageExtensions|获取消息扩展。|
|deleteMessageExtensi ons|删除消息扩展。|
|addMessageReaction|添加消息回应。|
|removeMessageReacti on|删除消息回应。|
|getMessageReactions|批量拉取多条消息回应信息。|
|getAllUserListOfMessa geReaction|分页拉取指定消息回应的用户列表。|

|API|描述|
|---|---|
|modifyMessage|变更消息。|
|getMessageList|获取消息列表。|
|getMessageListHoppin g|根据指定的消息 sequence 或 消息时间拉取会话的消息列表。|
|sendMessageReadRec eipt|发送消息已读回执。|

版权所有:腾讯云计算(北京)有限责任公司 

第7 共117页 

即时通信 IM 

|getMessageReadRecei ptList|拉取已读回执列表。|
|---|---|
|getGroupMessageRead MemberList|获取群消息已读(或未读)群成员列表。|
|findMessage|根据 messageID 查询会话的本地消息。|
|setMessageRead|将某会话下的未读消息状态设置为已读,置为已读的消息不会计入到未读统 计。|
|getConversationList|获取会话列表。|
|getConversationProfile|获取会话资料。|
|deleteConversation|删除会话。|
|clearHistoryMessage|清空单聊或群聊本地及云端的消息(不删除会话)。|
|pinConversation|置顶或取消置顶会话。|
|setAllMessageRead|将所有会话的未读消息设置为已读。|
|setMessageRemindTyp e|设置会话消息提醒类型,您可以使用此接口实现“消息免打扰”,“拒收消 息”的功能。|
|getTotalUnreadMessag eCount|获取会话未读总数。|

|API|描述|
|---|---|
|setConversationCusto mData|设置会话自定义数据。|
|markConversation|标记会话。|
|getConversationGroup List|获取会话分组列表。|
|createConversationGro up|创建会话分组。|
|deleteConversationGro up|删除会话分组。|

版权所有:腾讯云计算(北京)有限责任公司 

第8 共117页 

即时通信 IM 

|renameConversationGr oup|重命名会话分组。|
|---|---|
|addConversationsToGr oup|添加会话到一个会话分组。|
|deleteConversationsFr omGroup|从一个会话分组中删除会话。|

|API|描述|
|---|---|
|searchCloudMessages|搜索云端消息。|
|searchCloudUsers|搜索云端用户。|
|searchCloudGroups|搜索云端群列表。|
|searchCloudGroupMe mbers|搜索云端群成员列表。|

|API|描述|
|---|---|
|getMyProfile|获取个人资料。|
|getUserProfile|获取其他用户资料。|
|updateMyProfile|更新个人资料。|
|getBlacklist|获取我的黑名单列表。|
|addToBlacklist|添加用户到黑名单列表。|
|removeFromBlacklist|将用户从黑名单中移除。|

|API|描述|
|---|---|
|setSelfStatus|设置自己的自定义状态。|
|getUserStatus|查询用户状态。|

版权所有:腾讯云计算(北京)有限责任公司 

第9 共117页 

即时通信 IM 

|subscribeUserStatus|订阅用户状态。|
|---|---|
|unsubscribeUserStatu s|取消订阅用户状态。|

|API|描述|
|---|---|
|getFriendList|获取 SDK 缓存的好友列表。|
|addFriend|添加好友。|
|deleteFriend|删除好友。|
|checkFriend|校验好友关系。|
|getFriendProfile|获取指定好友的好友数据和资料数据。|
|updateFriend|更新好友的关系链数据。|
|getFriendApplicationLis t|获取 SDK 缓存的好友申请列表。|
|acceptFriendApplicatio n|同意好友申请。|
|refuseFriendApplicatio n|拒绝好友申请。|
|deleteFriendApplicatio n|删除好友申请。|
|setFriendApplicationRe ad|上报好友申请已读。|
|getFriendGroupList|获取 SDK 缓存的好友分组列表。|
|createFriendGroup|创建好友分组。|
|deleteFriendGroup|删除好友分组。|
|addToFriendGroup|添加好友到分组列表。|
|removeFromFriendGro up|从好友分组移除好友。|
|renameFriendGroup|修改好友分组的名称。|

版权所有:腾讯云计算(北京)有限责任公司 

第10 共117页 

即时通信 IM 

|API|描述|
|---|---|
|followUser|关注用户。|
|unfollowUser|取消关注。|
|getMyFollowersList|获取我的粉丝列表。|
|getMyFollowingList|获取我的关注列表。|
|getMutualFollowersList|获取互关列表。|
|getUserFollowInfo|获取指定用户的 关注/粉丝/互关 数量信息。|
|checkFollowType|检查指定用户的关注关系。|

|API|描述|
|---|---|
|getGroupList|获取群组列表。|
|getGroupProfile|获取群详细资料。|
|createGroup|创建群组。|
|dismissGroup|解散群组。|
|updateGroupProfile|修改群组资料。|
|joinGroup|申请加群。|
|quitGroup|退出群组。|
|searchGroupByID|搜索群组。|
|getGroupOnlineMembe rCount|获取群在线人数。|
|changeGroupOwner|转让群组。|
|getGroupApplicationLis t|获取加群申请列表。|
|handleGroupApplicatio n|处理申请加群。|

版权所有:腾讯云计算(北京)有限责任公司 

第11 共117页 

即时通信 IM 

|initGroupAttributes|初始化群属性。|
|---|---|
|setGroupAttributes|设置群属性。|
|deleteGroupAttributes|删除群属性。|
|getGroupAttributes|获取群属性。|
|setGroupCounters|设置群计数器。|
|increaseGroupCounter|递增群计数器。|
|decreaseGroupCounte r|递减群计数器。|
|getGroupCounters|获取群计数器。|

|API|描述|
|---|---|
|getGroupMemberList|获取群成员列表。|
|getGroupMemberProfil e|获取群成员资料。|
|addGroupMember|添加群成员。|
|deleteGroupMember|删除群成员。|
|setGroupMemberMute Time|设置群成员的禁言时间。|
|setGroupMemberRole|修改群成员角色。|
|setGroupMemberName Card|设置群成员名片。|
|setGroupMemberCusto mField|设置群成员自定义字段。|
|markGroupMemberList|标记群成员。|
|话题 API|描述|

版权所有:腾讯云计算(北京)有限责任公司 

第12 共117页 

即时通信 IM 

|getJoinedCommunityLi st|获取当前用户已经加入的支持话题的社群列表。|
|---|---|
|createTopicInCommuni ty|创建话题。|
|deleteTopicFromComm unity|删除话题。|
|updateTopicProfile|更新话题资料。|
|getTopicList|获取话题列表。|

|API|描述|
|---|---|
|addSignalingListener|监听信令事件。|
|removeSignalingListen er|移除监听信令事件。|
|invite|邀请某个人。|
|inviteInGroup|邀请群内的某些人。|
|cancel|邀请发起者取消邀请。|
|accept|被邀请人接受邀请。|
|reject|被邀请人拒绝邀请。|
|getSignalingInfo|获取信令信息。|
|modifyInvitation|修改邀请信令。|

版权所有:腾讯云计算(北京)有限责任公司 

第13 共117页 

即时通信 IM 

# Android 

最近更新时间:2025-02-25 15:32:12 

新老版本 API 请勿混合使用。 

## 初始化并成功登录,是正常使用腾讯云 IM 服务的前提。 

|API|描述|
|---|---|
|initSDK|初始化 SDK|
|unInitSDK|unsubscribeUserInfo 反初始化 SDK|
|addIMSDKListener|添加 IM 监听|
|removeIMSDKListener|移除 IM 监听|
|getVersion|获取版本号|
|getServerTime|获取服务器当前时间|
|login|登录|
|logout|登出|
|getLoginStatus|获取登录状态|
|getLoginUser|获取当前登录用户的 UserID|

## 如果您只需要使用文本和信令(即一段自定义buffer)消息,只需要使用这套简单消息收发接口即可。 

|API|描述|
|---|---|
|addSimpleMsgListener|设置基本消息(文本消息和自定义消息)的事件监听 器,请不要同addAdvancedMsgListener混 用|
|removeSimpleMsgListener|移除基本消息(文本消息和自定义消息)的事件监听 器|

版权所有:腾讯云计算(北京)有限责任公司 

第14 共117页 

即时通信 IM 

|sendC2CTextMessage|发送单聊(C2C)普通文本消息|
|---|---|
|sendC2CCustomMessage|发送单聊(C2C)自定义(信令)消息|
|sendGroupTextMessage|发送群聊普通文本消息|
|sendGroupCustomMessage|发送群聊自定义(信令)消息|

|API|描述|
|---|---|
|addSignalingListener|添加信令监听|
|removeSignalingListener|移除信令监听|
|invite|邀请某个人|
|inviteInGroup|邀请群内的某些人|
|cancel|邀请方取消邀请|
|accept|接收方接收邀请|
|reject|接收方拒绝邀请|
|getSignalingInfo|获取信令信息|
|addInvitedSignaling|添加邀请信令(可以用于群离线推送消息触发的邀请 信令)|
|modifyInvitation|修改邀请信令|

如果您需要收发图片、视频、文件等富媒体消息,并需要撤回消息、标记已读、查询历史消息等高级功能,推荐使用 下面这套高级消息接口(简单消息接口和高级消息接口请不要混用)。 

|API|描述|
|---|---|
|addAdvancedMsgListener|设置高级消息的事件监听器,请不要同 addSimpleMsgListener混用|
|removeAdvancedMsgListener|移除高级消息的事件监听器|
|createTextMessage|创建文本消息|

版权所有:腾讯云计算(北京)有限责任公司 

第15 共117页 

即时通信 IM 

|createCustomMessage|创建自定义消息|
|---|---|
|createImageMessage|创建图片消息|
|createSoundMessage|创建语音消息|
|createVideoMessage|创建视频消息|
|createFileMessage|创建文件消息|
|createLocationMessage|创建地理位置消息|
|createFaceMessage|创建表情消息|
|createMergerMessage|创建合并转发消息|
|createForwardMessage|创建单条转发消息|
|createTargetedGroupMessage|创建定向群消息|
|createAtSignedGroupMessage|创建带 @ 标记的群消息|
|sendMessage|发送消息,消息对象可以由 createXXXMessage 接口创建得来|
|setC2CReceiveMessageOpt|设置单聊消息免打扰|
|getC2CReceiveMessageOpt|获取单聊消息免打扰状态|
|setGroupReceiveMessageOpt|设置群聊消息免打扰状态|
|setAllReceiveMessageOpt|设置全局消息免打扰状态(可实现按天重复)|
|setAllReceiveMessageOpt|设置全局消息免打扰状态|
|getAllReceiveMessageOpt|获取全局消息免打扰状态|
|getC2CHistoryMessageList|获取单聊(C2C)历史消息|
|getGroupHistoryMessageList|获取群组历史消息|
|getHistoryMessageList|获取历史消息高级接口|
|revokeMessage|撤回消息,消息对象可以由 createXXXMessage 接口创建得来|
|modifyMessage|消息变更|

版权所有:腾讯云计算(北京)有限责任公司 

第16 共117页 

即时通信 IM 

|markC2CMessageAsRead|设置单聊(C2C)消息已读 (待废弃接口,请使用 cleanConversationUnreadMessageCount 接口)|
|---|---|
|markGroupMessageAsRead|设置群组消息已读 (待废弃接口,请使用 cleanConversationUnreadMessageCount 接口)|
|markAllMessageAsRead|标记所有会话为已读 (待废弃接口,请使用 cleanConversationUnreadMessageCount 接口)|
|deleteMessageFromLocalStorage|删除本地消息|
|deleteMessages|删除本地及云端的消息|
|clearC2CHistoryMessage|清空单聊本地及云端的消息|
|clearGroupHistoryMessage|清空群聊本地及云端的消息|
|insertGroupMessageToLocalStorage|向群组消息列表中添加一条消息|
|insertC2CMessageToLocalStorage|向单聊消息列表中添加一条消息|
|findMessages|根据 msgID 查找本地消息|
|searchLocalMessages|搜索本地消息|
|searchCloudMessages|搜索云端消息|
|sendMessageReadReceipts|发送消息已读回执|
|getMessageReadReceipts|获取消息已读回执|
|getGroupMessageReadMemberList|获取群消息已读群成员列表|
|setMessageExtensions|设置消息扩展|
|getMessageExtensions|获取消息扩展|
|deleteMessageExtensions|删除消息扩展|
|addMessageReaction|添加消息回应|
|removeMessageReaction|删除消息回应|
|getMessageReactions|批量拉取多条消息回应信息|
|getAllUserListOfMessageReaction|分页拉取消息回应全部用户资料|

版权所有:腾讯云计算(北京)有限责任公司 

第17 共117页 

即时通信 IM 

|translateText|翻译文本消息|
|---|---|
|pinGroupMessage|设置群消息置顶|
|getPinnedGroupMessageList|获取已置顶的群消息列表|

腾讯云 IM SDK 支持五种预设的群组类型,每种类型都有其适用场景: 

- 工作群(Work) :类似普通微信群,创建后不能自由加入,必须由已经在群的用户邀请入群,同旧版本中的 Private。 

- 公开群(Public):类似 QQ 群,用户申请加入,但需要群主或管理员审批。 

- 会议群(Meeting):适合跟 TRTC 结合实现视频会议和在线教育等场景,支持随意进出,支持查看进群前的 历史消息,同旧版本中的 ChatRoom。 

- 社群(Community):创建后可以随意进出,适合用于知识分享和游戏交流等超大社区群聊场景。该功能支持 

- 终端 SDK 5.8.1668增强版及以上版本、Web SDK 2.17.0及以上版本,需 购买旗舰版或企业版套餐包 并在 控制台 > 功能配置 > 群组配置 > 群功能配置 > 社群中开通。 

- 直播群(AVChatRoom):适合直播弹幕聊天室等场景,支持随意进出,人数无上限。 

|API|描述|
|---|---|
|addGroupListener|添加群组监听器|
|removeGroupListener|移除群组监听器|
|createGroup|创建群组(简单版本)|
|createGroup|创建群组(高级版本),可在建群同时设置群信息和 初始的群成员|
|joinGroup|加入群组|
|quitGroup|退出群组|
|dismissGroup|解散群组(仅群主和管理员可以解散)|
|getJoinedGroupList|获取已经加入的群列表(不包括已加入的直播群)|
|getGroupsInfo|拉取群资料|
|searchGroups|搜索本地群资料|
|searchCloudGroups|搜索云端群资料|
|setGroupInfo|修改群资料|

版权所有:腾讯云计算(北京)有限责任公司 

第18 共117页 

即时通信 IM 

|initGroupAttributes|初始化群属性|
|---|---|
|setGroupAttributes|设置群属性|
|deleteGroupAttributes|删除群属性|
|getGroupAttributes|获取群属性|
|getGroupOnlineMemberCount|获取群在线人数|
|setGroupCounters|设置群计数器|
|getGroupCounters|获取群计数器|
|increaseGroupCounter|递增群计数器|
|decreaseGroupCounter|递减群计数器|
|getGroupMemberList|获取群成员列表|
|getGroupMembersInfo|获取指定的群成员资料|
|searchGroupMembers|搜索本地群成员资料|
|searchCloudGroupMembers|搜索云端群成员资料|
|setGroupMemberInfo|修改指定的群成员资料|
|muteGroupMember|禁言|
|muteAllGroupMembers|禁言全体群成员,只有管理员或群主能够调用|
|kickGroupMember|踢人|
|setGroupMemberRole|切换群成员的角色|
|markGroupMemberList|标记群成员|
|transferGroupOwner|转让群主|
|inviteUserToGroup|邀请他人入群|
|getGroupApplicationList|获取加群的申请列表|
|acceptGroupApplication|同意某一条加群申请|
|refuseGroupApplication|拒绝某一条加群申请|
|setGroupApplicationRead|标记申请列表为已读|

版权所有:腾讯云计算(北京)有限责任公司 

第19 共117页 

即时通信 IM 

|getJoinedCommunityList|获取当前用户已经加入的支持话题的社群列表|
|---|---|
|createTopicInCommunity|创建话题|
|deleteTopicFromCommunity|删除话题|
|setTopicInfo|修改话题信息|
|getTopicInfoList|获取话题列表|

如果您需要在社群下创建话题,请使用这套接口。社群用来管理群成员,社群下的所有话题不仅可以共享社群成员, 还可以独立收发消息而不相互干扰。 

|API|描述|
|---|---|
|addCommunityListener|添加社群监听器|
|removeCommunityListener|移除社群监听器|
|createCommunity|创建支持话题的社群|
|getJoinedCommunityList|获取当前用户已经加入的支持话题的社群列表|
|createTopicInCommunity|创建话题|
|deleteTopicFromCommunity|删除话题|
|setTopicInfo|修改话题信息|
|getTopicInfoList|获取话题列表|
|createPermissionGroupInCommunity|创建社群权限组|
|deletePermissionGroupFromCommunity|删除社群权限组|
|modifyPermissionGroupInfoInCommunity|修改社群权限组|
|getJoinedPermissionGroupListInCommun ity|获取已加入的社群权限组列表|
|getPermissionGroupListInCommunity|获取社群权限组列表|
|addCommunityMembersToPermissionGro up|向社群权限组添加成员|

版权所有:腾讯云计算(北京)有限责任公司 

第20 共117页 

即时通信 IM 

|removeCommunityMembersFromPermiss ionGroup|从社群权限组删除成员|
|---|---|
|getCommunityMemberListInPermissionGr oup|获取社群权限组成员列表|
|addTopicPermissionToPermissionGroup|向权限组添加话题权限|
|deleteTopicPermissionFromPermissionGr oup|从权限组中删除话题权限|
|modifyTopicPermissionInPermissionGrou p|修改权限组中的话题权限|
|getTopicPermissionInPermissionGroup|获取权限组中的话题权限|

会话列表,即登录微信或 QQ 后首屏看到的列表,包含会话节点、会话名称、群名称、最后一条消息以及未读消息 数等元素。 

|API|描述|
|---|---|
|addConversationListener|添加会话监听器|
|removeConversationListener|移除会话监听器|
|getConversationList|获取会话列表|
|getConversationListByFilter|获取会话高级接口,可以指定会话类型、标记类型、 分组名等|
|getConversation|获取指定单个会话|
|getConversationList|获取指定多个会话|
|deleteConversation|删除会话|
|deleteConversationList|删除会话列表|
|setConversationDraft|设置会话草稿|
|setConversationCustomData|设置会话自定义数据|
|pinConversation|置顶会话|
|markConversation|标记会话|

版权所有:腾讯云计算(北京)有限责任公司 

第21 共117页 

即时通信 IM 

|getTotalUnreadMessageCount|获取会话总未读数|
|---|---|
|getUnreadMessageCountByFilter|获取按会话 filter 过滤的未读总数|
|subscribeUnreadMessageCountByFilter|注册监听指定 filter 的会话未读总数变化|
|unsubscribeUnreadMessageCountByFilte r|取消监听指定 filter 的会话未读总数变化|
|cleanConversationUnreadMessageCount|清理会话的未读消息计数|
|createConversationGroup|创建会话分组|
|getConversationGroupList|获取会话分组列表|
|deleteConversationGroup|删除会话分组|
|renameConversationGroup|重命名会话分组|
|addConversationsToGroup|添加会话到一个会话分组|
|deleteConversationsFromGroup|从一个会话分组中删除会话|

## 包含查询用户资料、修改个人资料以及屏蔽某人消息(即把某用户加入黑名单中)的相关接口。 

|API|描述|
|---|---|
|getUsersInfo|获取用户资料|
|setSelfInfo|修改个人资料|
|subscribeUserInfo|订阅用户资料|
|unsubscribeUserInfo|取消订阅用户资料|
|getUserStatus|查询用户状态|
|setSelfStatus|设置自己的状态|
|subscribeUserStatus|订阅用户状态|
|unsubscribeUserStatus|取消订阅用户状态|
|searchUsers|搜索云端用户资料|
|addToBlackList|屏蔽某人的消息(添加该用户到黑名单中)|

版权所有:腾讯云计算(北京)有限责任公司 

第22 共117页 

即时通信 IM 

|deleteFromBlackList|取消某人的消息屏蔽(把该用户从黑名单中移除)|
|---|---|
|getBlackList|获取黑名单列表|

如果想要在 App 切后台时依然能够实时收到 IM 消息,可以使用离线推送服务。由于大陆境内尚没有统一的推送服 务,Android 的离线推送需要针对不同厂商的手机进行 逐一适配 。 

|API|描述|
|---|---|
|setOfflinePushConfig|设置离线推送配置信息|
|doBackground|APP 检测到应用退后台时可以调用此接口,可以用 作桌面应用角标的初始化未读数量。|
|doForeground|APP 检测到应用进前台时可以调用此接口|

腾讯云 IM 在收发消息时默认不检查是不是好友关系,您可以在 控制台 >功能配置>登录与消息>好友关系检查中开 启"发送单聊消息检查关系链"开关,并使用如下接口增删好友和管理好友列表。 

|API|描述|
|---|---|
|addFriendListener|添加关系链监听器|
|removeFriendListener|移除关系链监听器|
|getFriendList|获取好友列表|
|getFriendsInfo|获取指定好友资料|
|setFriendInfo|设置指定好友资料|
|searchFriends|搜索好友列表|
|addFriend|添加好友|
|deleteFromFriendList|删除好友|
|checkFriend|检查指定用户的好友关系|
|getFriendApplicationList|获取好友申请列表|
|acceptFriendApplication|同意好友申请|

版权所有:腾讯云计算(北京)有限责任公司 

第23 共117页 

即时通信 IM 

|refuseFriendApplication|拒绝好友申请|
|---|---|
|deleteFriendApplication|删除好友申请|
|setFriendApplicationRead|设置好友申请已读|
|createFriendGroup|新建好友分组|
|getFriendGroups|获取分组信息|
|deleteFriendGroup|删除好友分组|
|renameFriendGroup|修改好友分组的名称|
|addFriendsToFriendGroup|添加好友到一个好友分组|
|deleteFriendsFromFriendGroup|从好友分组中删除好友|
|subscribeOfficialAccount|订阅公众号|
|unsubscribeOfficialAccount|取消订阅公众号|
|getOfficialAccountsInfo|获取公众号列表|
|followUser|关注用户|
|unfollowUser|取消关注用户|
|getMyFollowingList|获取我的关注列表|
|getMyFollowersList|获取我的粉丝列表|
|getMutualFollowersList|获取我的互关列表|
|getUserFollowInfo|获取指定用户的 关注/粉丝/互关 数量信息|
|checkFollowType|检查指定用户的关注类型|

版权所有:腾讯云计算(北京)有限责任公司 

第24 共117页 

即时通信 IM 

# iOS & Mac 

最近更新时间:2025-02-25 15:32:12 

新老版本 API 请勿混合使用。 

## 初始化并成功登录,是正常使用腾讯云 IM 服务的前提。 

|API|描述|
|---|---|
|initSDK|初始化|
|unInitSDK|反初始化|
|addIMSDKListener|添加 IM 监听|
|removeIMSDKListener|移除 IM 监听|
|getVersion|获取版本号|
|getServerTime|获取服务器当前时间|
|login|登录|
|logout|退出登录|
|getLoginUser|获取登录用户|
|getLoginStatus|获取登录状态|

## 如果您只需要使用文本和信令(即一段自定义buffer)消息,只需要使用这套简单消息收发接口即可。 

|API|描述|
|---|---|
|addSimpleMsgListener|设置基本消息(文本消息和自定义消息)的事件监听器,请不要同 addAdvancedMsgListener混用|
|removeSimpleMsgList ener|移除基本消息(文本消息和自定义消息)的事件监听器|

版权所有:腾讯云计算(北京)有限责任公司 

第25 共117页 

即时通信 IM 

|sendC2CTextMessage|发送单聊(C2C)普通文本消息|
|---|---|
|sendC2CCustomMess age|发送单聊(C2C)自定义(信令)消息|
|sendGroupTextMessag e|发送群聊普通文本消息|
|sendGroupCustomMes sage|发送群聊自定义(信令)消息|

|API|描述|
|---|---|
|addSignalingListener|添加信令监听|
|removeSignalingListen er|移除信令监听|
|invite|邀请某个人|
|inviteInGroup|邀请群内的某些人|
|cancel|邀请方取消邀请|
|accept|接收方接收邀请|
|reject|接收方拒绝邀请|
|getSignalingInfo|获取信令信息|
|addInvitedSignaling|添加邀请信令(可以用于群离线推送消息触发的邀请信令)|
|modifyInvitation|修改邀请信令|

如果您需要收发图片、视频、文件等富媒体消息,并需要撤回消息、标记已读、查询历史消息等高级功能,推荐使用 下面这套高级消息接口(简单消息接口和高级消息接口请不要混用)。 

|API|描述|
|---|---|
|addAdvancedMsgListe ner|设置高级消息的事件监听器,请不要同addSimpleMsgListener混用|

版权所有:腾讯云计算(北京)有限责任公司 

第26 共117页 

即时通信 IM 

|removeAdvancedMsgL istener|移除高级消息监听器|
|---|---|
|createTextMessage|创建文本消息|
|createTextAtMessage|创建 @ 文本消息|
|createCustomMessag e|创建自定义消息|
|createImageMessage|创建图片消息|
|createSoundMessage|创建语音消息|
|createVideoMessage|创建视频消息|
|createFileMessage|创建文件消息|
|createLocationMessag e|创建地理位置消息|
|createFaceMessage|创建表情消息|
|createMergerMessage|创建合并转发消息|
|createForwardMessag e|创建单条转发消息|
|createTargetedGroup Message|创建定向群消息|
|createAtSignedGroup Message|创建带 @ 标记的群消息|
|sendMessage|发送消息,消息对象可以由 createXXXMessage 接口创建得来|
|setC2CReceiveMessag eOpt|设置单聊消息免打扰|
|getC2CReceiveMessag eOpt|获取单聊消息免打扰状态|
|setGroupReceiveMess ageOpt|设置群聊消息免打扰状态|
|setAllReceiveMessage Opt|设置全局消息接收选项(可实现按天重复)|

版权所有:腾讯云计算(北京)有限责任公司 

第27 共117页 

即时通信 IM 

|setAllReceiveMessage Opt|设置全局消息接收选项|
|---|---|
|getAllReceiveMessage Opt|获取登录用户全局消息接收选项|
|getC2CHistoryMessag eList|获取单聊(C2C)历史消息|
|getGroupHistoryMessa geList|获取群组历史消息|
|getHistoryMessageList|获取历史消息高级接口|
|revokeMessage|撤回消息,消息对象可以由 createXXXMessage 接口创建得来|
|modifyMessage|消息变更|
|deleteMessageFromLo calStorage|删除本地消息|
|deleteMessages|删除本地及云端的消息|
|clearC2CHistoryMessa ge|清空单聊本地及云端的消息|
|clearGroupHistoryMes sage|清空群聊本地及云端的消息|
|insertGroupMessageT oLocalStorage|向群组消息列表中添加一条消息|
|insertC2CMessageToL ocalStorage|向单聊消息列表中添加一条消息|
|findMessages|根据 msgID 查找本地消息|
|searchLocalMessages|搜索本地消息|
|searchCloudMessages|搜索云端消息|
|sendMessageReadRec eipts|发送消息已读回执|
|getMessageReadRecei pts|获取消息已读回执|

版权所有:腾讯云计算(北京)有限责任公司 

第28 共117页 

即时通信 IM 

|getGroupMessageRea dMemberList|获取群消息已读群成员列表|
|---|---|
|setMessageExtension s|设置消息扩展|
|getMessageExtension s|获取消息扩展|
|deleteMessageExtensi ons|删除消息扩展|
|addMessageReaction|添加消息回应|
|removeMessageReacti on|删除消息回应|
|getMessageReactions|批量拉取多条消息回应信息|
|getAllUserListOfMessa geReaction|分页拉取消息回应全部用户资料|
|translateText|翻译文本消息|
|pinGroupMessage|设置群消息置顶|
|getPinnedGroupMessa geList|获取已置顶的群消息列表|
|markC2CMessageAsR ead|设置单聊(C2C)消息已读(待废弃接口,请使用 cleanConversationUnreadMessageCount接口)|
|markGroupMessageAs Read|设置群组消息已读(待废弃接口,请使用 cleanConversationUnreadMessageCount接口)|
|markAllMessageAsRea|标记所有会话为已读(待废弃接口,请使用|
|d|cleanConversationUnreadMessageCount接口)|

## 腾讯云 IM SDK 支持五种预设的群组类型,每种类型都有其适用场景: 

工作群(Work) :类似普通微信群,创建后不能自由加入,必须由已经在群的用户邀请入群,同旧版本中的 Private。 

公开群(Public)   :类似 QQ 群,用户申请加入,但需要群主或管理员审批。 

会议群(Meeting):适合跟 TRTC 结合实现视频会议和在线教育等场景,支持随意进出,支持查看进群前的 历史消息,同旧版本中的 ChatRoom。 

版权所有:腾讯云计算(北京)有限责任公司 

第29 共117页 

即时通信 IM 

社群(Community):创建后可以随意进出,适合用于知识分享和游戏交流等超大社区群聊场景。该功能支持 终端 SDK 5.8.1668增强版及以上版本、Web SDK 2.17.0及以上版本,需 购买旗舰版或企业版套餐包 并在 控制台 > 功能配置 > 群组配置 > 群功能配置 > 社群中开通。 

直播群(AVChatRoom):适合直播弹幕聊天室等场景,支持随意进出,人数无上限。 

|直播群(AVChatRoom): API|合直播弹幕聊天室等场景,支持随意进出,人数无上限。 描述|
|---|---|
|setGroupListener|设置群组监听器(待废弃接口,请使用 addGroupListener 和 removeGroupListener 接口)|
|addGroupListener|添加群组监听器|
|removeGroupListener|移除群组监听器|
|createGroup|创建群组(简单版本)|
|createGroup|创建群组(高级版本),可在建群同时设置群信息和初始的群成员|
|joinGroup|加入群组|
|quitGroup|退出群组|
|dismissGroup|解散群组(仅群主和管理员可以解散)|
|getJoinedGroupList|获取已经加入的群列表(不包括已加入的直播群)|
|getGroupsInfo|拉取群资料|
|searchGroups|搜索本地群资料|
|searchCloudGroups|搜索云端群资料|
|setGroupInfo|修改群资料|
|initGroupAttributes|初始化群属性|
|setGroupAttributes|设置群属性|
|deleteGroupAttributes|删除群属性|
|getGroupAttributes|获取群属性|
|getGroupOnlineMembe rCount|获取群在线人数|
|setGroupCounters|设置群计数器|
|getGroupCounters|获取群计数器|

版权所有:腾讯云计算(北京)有限责任公司 

第30 共117页 

即时通信 IM 

|increaseGroupCounter|递增群计数器|
|---|---|
|decreaseGroupCounte r|递减群计数器|
|getGroupMemberList|获取群成员列表|
|getGroupMembersInfo|获取指定的群成员资料|
|searchGroupMembers|搜索本地群成员资料|
|searchCloudGroupMe mbers|搜索云端群成员资料|
|setGroupMemberInfo|修改指定的群成员资料|
|muteGroupMember|禁言|
|muteAllGroupMembers|禁言全体群成员|
|inviteUserToGroup|邀请他人入群|
|kickGroupMember|踢人|
|setGroupMemberRole|切换群成员的角色|
|markGroupMemberLis t|标记群成员|
|transferGroupOwner|转让群主|
|kickGroupMember|踢人|
|getGroupApplicationLi st|获取加群的申请列表|
|acceptGroupApplicatio n|同意某一条加群申请|
|refuseGroupApplicatio n|拒绝某一条加群申请|
|setGroupApplicationRe ad 社群话题相关接口|标记申请列表为已读|

版权所有:腾讯云计算(北京)有限责任公司 

第31 共117页 

即时通信 IM 

## 如果您需要在社群下创建话题,请使用这套接口。社群用来管理群成员,社群下的所有话题不仅可以共享社群成员, 还可以独立收发消息而不相互干扰。 

|API|描述|
|---|---|
|addCommunityListene r|添加社群监听器|
|removeCommunityList ener|移除社群监听器|
|createCommunity|创建支持话题的社群|
|getJoinedCommunityLi st|获取当前用户已经加入的支持话题的社群列表|
|createTopicInCommuni ty|创建话题|
|deleteTopicFromCom munity|删除话题|
|setTopicInfo|修改话题信息|
|getTopicInfoList|获取话题列表|
|createPermissionGrou pInCommunity|创建社群权限组|
|deletePermissionGrou pFromCommunity|删除社群权限组|
|modifyPermissionGrou pInfoInCommunity|修改社群权限组|
|getJoinedPermissionG roupListInCommunity|获取已加入的社群权限组列表|
|getPermissionGroupLi stInCommunity|获取社群权限组列表|
|addCommunityMember sToPermissionGroup|向社群权限组添加成员|
|removeCommunityMe mbersFromPermission Group|从社群权限组删除成员|

版权所有:腾讯云计算(北京)有限责任公司 

第32 共117页 

即时通信 IM 

|getCommunityMember ListInPermissionGroup|获取社群权限组成员列表|
|---|---|
|addTopicPermissionTo PermissionGroup|向权限组添加话题权限|
|deleteTopicPermission FromPermissionGroup|从权限组中删除话题权限|
|modifyTopicPermission InPermissionGroup|修改权限组中的话题权限|
|getTopicPermissionInP ermissionGroup|获取权限组中的话题权限|

会话列表,即登录微信或 QQ 后首屏看到的列表,包含会话节点、会话名称、群名称、最后一条消息以及未读消息 数等元素。 

|API|描述|
|---|---|
|setConversationListen er|设置会话监听器 (待废弃接口,请使用 addConversationListener 和 removeConversationListener 接口)|
|addConversationListen er|添加会话监听器|
|removeConversationLi stener|移除会话监听器|
|getConversationList|获取会话列表|
|getConversation|获取指定单个会话|
|getConversationList|获取指定多个会话|
|getConversationListBy Filter|获取会话高级接口,可以指定会话类型、标记类型、分组名等|
|deleteConversation|删除会话|
|deleteConversationLis t|删除会话列表|
|setConversationDraft|设置会话草稿|

版权所有:腾讯云计算(北京)有限责任公司 

第33 共117页 

即时通信 IM 

|setConversationCusto mData|设置会话自定义数据|
|---|---|
|pinConversation|置顶会话|
|markConversation|标记会话|
|getTotalUnreadMessa geCount|获取会话总未读数|
|getUnreadMessageCo untByFilter|获取根据 filter 过滤的会话未读总数|
|subscribeUnreadMess ageCountByFilter|注册监听指定 filter 的会话未读总数变化|
|unsubscribeUnreadMe ssageCountByFilter|取消监听指定 filter 的会话未读总数变化|
|cleanConversationUnr eadMessageCount|清理会话的未读消息计数|
|createConversationGro up|创建会话分组|
|getConversationGroup List|获取会话分组列表|
|deleteConversationGro up|删除会话分组|
|renameConversationGr oup|重命名会话分组|
|addConversationsToGr oup|添加会话到一个会话分组|
|deleteConversationsFr omGroup 用户资料相关接口|从一个会话分组中删除会话|

版权所有:腾讯云计算(北京)有限责任公司 

第34 共117页 

即时通信 IM 

## 包含查询用户资料、修改个人资料以及屏蔽某人消息(即把某用户加入黑名单中)的相关接口。 

|API|描述|
|---|---|
|getUsersInfo|获取用户资料|
|setSelfInfo|修改个人资料|
|subscribeUserInfo|订阅用户资料|
|unsubscribeUserInfo|取消订阅用户资料|
|getUserStatus|订阅用户资料|
|setSelfStatus|取消订阅用户资料|
|subscribeUserStatus|订阅用户状态|
|unsubscribeUserStatu s|取消订阅用户状态|
|searchUsers|搜索云端用户资料|
|addToBlackList|屏蔽某人的消息(添加该用户到黑名单中)|
|deleteFromBlackList|取消某人的消息屏蔽(把该用户从黑名单中移除)|
|getBlackList|获取黑名单列表|

## 如果想要在 App 切后台时依然能够实时收到 IM 消息,可以使用离线推送服务,详细配置请参考 离线推送 。 

|API|描述|
|---|---|
|setAPNSListener|设置 APNs 监听|
|setAPNS|配置 APNS 推送信息|
|setVOIP|配置 VOIP 推送信息|

腾讯云 IM 在收发消息时默认不检查是不是好友关系,您可以在 控制台 >功能配置>登录与消息>好友关系检查中开 启"发送单聊消息检查关系链"开关,并使用如下接口增删好友和管理好友列表。 

|API 描述|
|---|

版权所有:腾讯云计算(北京)有限责任公司 

第35 共117页 

即时通信 IM 

|setFriendListener|设置关系链与好友资料监听器(待废弃接口,请使用 addFriendListener 和 removeFriendListener 接口)|
|---|---|
|addFriendListener|添加关系链监听器|
|removeFriendListener|移除关系链监听器|
|getFriendList|获取好友列表|
|getFriendsInfo|获取指定好友资料|
|setFriendInfo|设置指定好友资料|
|searchFriends|搜索好友列表|
|addFriend|添加好友|
|deleteFromFriendList|删除好友|
|checkFriend|检查指定用户的好友关系|
|getFriendApplicationLi st|获取好友申请列表|
|acceptFriendApplicatio n|同意好友申请|
|refuseFriendApplicatio n|拒绝好友申请|
|deleteFriendApplicatio n|删除好友申请|
|setFriendApplicationRe ad|设置好友申请已读|
|createFriendGroup|新建好友分组|
|getFriendGroups|获取分组信息|
|deleteFriendGroup|删除好友分组|
|renameFriendGroup|修改好友分组的名称|
|addFriendsToFriendGr oup|添加好友到一个好友分组|
|deleteFriendsFromFrie|从好友分组中删除好友|

版权所有:腾讯云计算(北京)有限责任公司 

第36 共117页 

即时通信 IM 

|ndGroup||
|---|---|
|subscribeOfficialAccou nt|订阅公众号|
|unsubscribeOfficialAcc ount|取消订阅公众号|
|getOfficialAccountsInf o|获取公众号列表|
|followUser|关注用户|
|unfollowUser|取消关注用户|
|getMyFollowingList|获取我的关注列表|
|getMutualFollowersLis t|获取我的互关列表|
|getUserFollowInfo|获取指定用户的 关注/粉丝/互关 数量信息|
|checkFollowType|检查指定用户的关注类型|

版权所有:腾讯云计算(北京)有限责任公司 

第37 共117页 

即时通信 IM 

# Swift 

## 最近更新时间:2025-01-21 17:44:53 

新老版本 API 请勿混合使用。 

## 初始化并成功登录,是正常使用腾讯云 IM 服务的前提。 

|API|描述|
|---|---|
|initSDK|初始化|
|unInitSDK|反初始化|
|addIMSDKListener|添加 IM 监听|
|removeIMSDKListener|移除 IM 监听|
|getVersion|获取版本号|
|getServerTime|获取服务器当前时间|
|login|登录|
|logout|退出登录|
|getLoginUser|获取登录用户|
|getLoginStatus|获取登录状态|

## 如果您只需要使用文本和信令(即一段自定义buffer)消息,只需要使用这套简单消息收发接口即可。 

|API|描述|
|---|---|
|addSimpleMsgListener|设置基本消息(文本消息和自定义消息)的事件监听器,请不要同 addAdvancedMsgListener混用|
|removeSimpleMsgList ener|移除基本消息(文本消息和自定义消息)的事件监听器|

版权所有:腾讯云计算(北京)有限责任公司 

第38 共117页 

即时通信 IM 

|sendC2CTextMessage|发送单聊(C2C)普通文本消息|
|---|---|
|sendC2CCustomMess age|发送单聊(C2C)自定义(信令)消息|
|sendGroupTextMessag e|发送群聊普通文本消息|
|sendGroupCustomMes sage|发送群聊自定义(信令)消息|

|API|描述|
|---|---|
|addSignalingListener|添加信令监听|
|removeSignalingListen er|移除信令监听|
|invite|邀请某个人|
|inviteInGroup|邀请群内的某些人|
|cancel|邀请方取消邀请|
|accept|接收方接收邀请|
|reject|接收方拒绝邀请|
|getSignalingInfo|获取信令信息|
|addInvitedSignaling|添加邀请信令(可以用于群离线推送消息触发的邀请信令)|
|modifyInvitation|修改邀请信令|

如果您需要收发图片、视频、文件等富媒体消息,并需要撤回消息、标记已读、查询历史消息等高级功能,推荐使用 下面这套高级消息接口(简单消息接口和高级消息接口请不要混用)。 

|API|描述|
|---|---|
|addAdvancedMsgListe ner|设置高级消息的事件监听器,请不要同addSimpleMsgListener混用|

版权所有:腾讯云计算(北京)有限责任公司 

第39 共117页 

即时通信 IM 

|removeAdvancedMsgL istener|移除高级消息监听器|
|---|---|
|createTextMessage|创建文本消息|
|createCustomMessag e|创建自定义消息|
|createImageMessage|创建图片消息|
|createSoundMessage|创建语音消息|
|createVideoMessage|创建视频消息|
|createFileMessage|创建文件消息|
|createLocationMessag e|创建地理位置消息|
|createFaceMessage|创建表情消息|
|createMergerMessage|创建合并转发消息|
|createForwardMessag e|创建单条转发消息|
|createTargetedGroup Message|创建定向群消息|
|createAtSignedGroup Message|创建带 @ 标记的群消息|
|sendMessage|发送消息,消息对象可以由 createXXXMessage 接口创建得来|
|setC2CReceiveMessag eOpt|设置单聊消息秒打扰|
|getC2CReceiveMessag eOpt|获取单聊消息免打扰状态|
|setGroupReceiveMess ageOpt|设置群聊消息免打扰状态|
|setAllReceiveMessage Opt|设置全局消息接收选项(可实现按天重复)|
|setAllReceiveMessage Opt|设置全局消息接收选项|

版权所有:腾讯云计算(北京)有限责任公司 

第40 共117页 

即时通信 IM 

|getAllReceiveMessage Opt|获取登录用户全局消息接收选项|
|---|---|
|getC2CHistoryMessag eList|获取单聊(C2C)历史消息|
|getGroupHistoryMessa geList|获取群组历史消息|
|getHistoryMessageList|获取历史消息高级接口|
|revokeMessage|撤回消息,消息对象可以由 createXXXMessage 接口创建得来|
|modifyMessage|修改消息,消息对象可以由 createXXXMessage 接口创建得来|
|markC2CMessageAsR ead|设置单聊(C2C)消息已读|
|markGroupMessageAs Read|设置群组消息已读|
|markAllMessageAsRea d|标记所有会话为已读|
|deleteMessageFromLo calStorage|删除本地消息|
|deleteMessages|删除本地及云端的消息|
|clearC2CHistoryMessa ge|清空单聊本地及云端的消息|
|clearGroupHistoryMes sage|清空群组本地及云端的消息|
|insertGroupMessageT oLocalStorage|向群组消息列表中添加一条消息|
|insertC2CMessageToL ocalStorage|向单聊消息列表中添加一条消息|
|findMessages|根据 msgID 查找本地消息|
|searchLocalMessages|搜索本地消息|
|sendMessageReadRec eipts|发送消息已读回执|

版权所有:腾讯云计算(北京)有限责任公司 

第41 共117页 

即时通信 IM 

|getMessageReadRecei pts|获取消息已读回执|
|---|---|
|getGroupMessageRea dMemberList|获取群消息已读群成员列表|
|setMessageExtension s|设置消息扩展|
|getMessageExtension s|获取消息扩展|
|deleteMessageExtensi ons|删除消息扩展|
|add Message Reaction|添加消息回应|
|remove Message Reaction|删除消息回应|
|get Message Reactions|批量获取多条消息回应信息|
|get All User List OfMessage Reaction|分页拉取消息回应全量用户资料|
|translateText|翻译文本消息|
|markC2CMessageAsR ead|设置单聊(C2C)消息已读(待废弃接口,请使用 cleanConversationUnreadMessageCount接口)|
|markGroupMessageAs Read|设置群组消息已读(待废弃接口,请使用 cleanConversationUnreadMessageCount接口)|
|markAllMessageAsRea|标记所有会话为已读(待废弃接口,请使用|
|d|cleanConversationUnreadMessageCount接口)|

## 腾讯云 IM SDK 支持四种预设的群组类型,每种类型都有其适用场景: 

工作群(Work) :类似普通微信群,创建后不能自由加入,必须由已经在群的用户邀请入群。 

公开群(Public)   :类似 QQ 群,用户申请加入,但需要群主或管理员审批。 

- 会议群(Meeting):适合跟 TRTC 结合实现视频会议和在线教育等场景,支持随意进出,支持查看进群前的 历史消息。 

直播群(AVChatRoom):适合直播弹幕聊天室等场景,支持随意进出,人数无上限。 

版权所有:腾讯云计算(北京)有限责任公司 

第42 共117页 

即时通信 IM 

|API|描述|
|---|---|
|addGroupListener|添加群组相关的事件监听器|
|removeGroupListener|移除群组相关的事件监听器|
|createGroup|创建群组(简单版本)|
|createGroup|创建群组(高级版本),可在建群同时设置群信息和初始的群成员|
|joinGroup|加入群组|
|quitGroup|退出群组|
|dismissGroup|解散群组(仅群组和管理员可以解散)|
|getJoinedGroupList|获取已经加入的群列表(不包括已加入的直播群)|
|getGroupsInfo|拉取群资料|
|searchGroups|搜索本地群资料|
|searchCloudGroups|搜索云端群资料|
|setGroupInfo|修改群资料|
|initGroupAttributes|初始化群属性|
|setGroupAttributes|设置群属性|
|deleteGroupAttributes|删除群属性|
|getGroupAttributes|获取群属性|
|getGroupOnlineMembe rCount|获取群在线人数|
|setGroupCounters|设置群计数器|
|getGroupCounters|获取群计数器|
|increaseGroupCounter|递增群计数器|
|decreaseGroupCounte r|递减群计数器|
|getGroupMemberList|获取群成员列表|
|getGroupMembersInfo|获取指定的群成员资料|

版权所有:腾讯云计算(北京)有限责任公司 

第43 共117页 

即时通信 IM 

|searchGroupMembers|搜索本地群成员资料|
|---|---|
|searchCloudGroupMe mbers|搜索云端群成员资料|
|setGroupMemberInfo|修改指定的群成员资料|
|muteGroupMember|禁言|
|muteAllGroupMembers|禁言全体群成员|
|inviteUserToGroup|邀请他人入群|
|kickGroupMember|踢人|
|setGroupMemberRole|切换群成员的角色|
|markGroupMemberLis t|标记群成员|
|transferGroupOwner|转让群主|
|getGroupApplicationLi st|获取加群的申请列表|
|acceptGroupApplicatio n|同意某一条加群申请|
|refuseGroupApplicatio n|拒绝某一条加群申请|
|setGroupApplicationRe ad|标记申请列表为已读|

如果您需要在社群下创建话题,请使用这套接口。社群用来管理群成员,社群下的所有话题不仅可以共享社群成员, 还可以独立收发消息而不相互干扰。 

|API|描述|
|---|---|
|addCommunityListene r|添加社群监听器|
|removeCommunityList ener|移除社群监听器|

版权所有:腾讯云计算(北京)有限责任公司 

第44 共117页 

即时通信 IM 

|createCommunity|创建支持话题的社群|
|---|---|
|getJoinedCommunityLi st|获取当前用户已经加入的支持话题的社群列表|
|createTopicInCommuni ty|创建话题|
|deleteTopicFromCom munity|删除话题|
|setTopicInfo|修改话题信息|
|getTopicInfoList|获取话题列表|

会话列表,即登录微信或 QQ 后首屏看到的列表,包含会话节点、会话名称、群名称、最后一条消息以及未读消息 数等元素。 

|API|描述|
|---|---|
|addConversationListen er|添加会话监听器|
|removeConversationLi stener|移除会话监听器|
|getConversationList|获取会话列表|
|getConversation|获取指定单个会话|
|getConversationList|获取指定多个会话|
|getConversationListBy Filter|获取会话列表(高级接口)|
|deleteConversation|删除会话|
|deleteConversationLis t|删除会话列表|
|setConversationDraft|设置会话草稿|
|setConversationCusto mData|设置会话自定义数据|

版权所有:腾讯云计算(北京)有限责任公司 

第45 共117页 

即时通信 IM 

|pinConversation|置顶会话|
|---|---|
|markConversation|标记会话|
|getTotalUnreadMessa geCount|获取会话总未读数|
|getUnreadMessageCo untByFilter|获取根据 filter 过滤的会话未读总数|
|subscribeUnreadMess ageCountByFilter|注册监听指定 filter 的会话未读总数变化|
|unsubscribeUnreadMe ssageCountByFilter|取消监听指定 filter 的会话未读总数变化|
|cleanConversationUnr eadMessageCount|清理会话的未读消息计数|
|createConversationGr oup|创建会话分组|
|getConversationGroup List|获取会话分组列表|
|deleteConversationGro up|删除会话分组|
|renameConversationG roup|重命名会话分组|
|addConversationsToGr oup|添加会话到一个会话分组|
|deleteConversationsFr omGroup|从一个会话分组中删除会话|

## 包含查询用户资料、修改个人资料以及屏蔽某人消息(即把某用户加入黑名单中)的相关接口。 

|API|描述|
|---|---|
|getUsersInfo|获取用户资料|
|setSelfInfo|修改个人资料|

版权所有:腾讯云计算(北京)有限责任公司 

第46 共117页 

即时通信 IM 

|getUserStatus|订阅用户资料|
|---|---|
|setSelfStatus|取消订阅用户资料|
|subscribeUserStatus|订阅用户状态|
|unsubscribeUserStatu s|取消订阅用户状态|
|searchUsers|搜索云端用户资料|
|addToBlackList|屏蔽某人的消息(添加该用户到黑名单中)|
|deleteFromBlackList|取消某人的消息屏蔽(把该用户从黑名单中移除)|
|getBlackList|获取黑名单列表|

如果想要在 App 切后台时依然能够实时收到 IM 消息,可以使用离线推送服务,详细配置请参见 离线推送 。 

|API|描述|
|---|---|
|setAPNSListener|设置 APNs 监听|
|setAPNS|配置 APNs 推送信息|
|setVOIP|配置 VoIP 推送信息|

腾讯云 IM 在收发消息时默认不检查是不是好友关系,您可以在 控制台 > 功能配置 > 登录与消息 > 好友关系检查 中开启"发送单聊消息检查关系链"开关,并使用如下接口增删好友和管理好友列表。 

|API|描述|
|---|---|
|addFriendListener|添加关系链的监听器,用于接收好友列表和黑名单的变更事件|
|removeFriendListener|移除关系链的监听器|
|getFriendList|获取好友列表|
|getFriendsInfo|获取指定好友资料|
|setFriendInfo|设置指定好友资料|
|searchFriends|搜索好友列表|

版权所有:腾讯云计算(北京)有限责任公司 

第47 共117页 

即时通信 IM 

|addFriend|添加好友|
|---|---|
|deleteFromFriendList|删除好友|
|checkFriend|检查指定用户的好友关系|
|getFriendApplicationLi st|获取好友申请列表|
|acceptFriendApplicatio n|同意好友申请|
|refuseFriendApplicatio n|拒绝好友申请|
|deleteFriendApplicatio n|删除好友申请|
|setFriendApplicationRe ad|设置好友申请已读|
|createFriendGroup|新建好友分组|
|get Friend Group List|获取分组列表|
|deleteFriendGroup|删除好友分组|
|renameFriendGroup|修改好友分组的名称|
|addFriendsToFriendGr oup|添加好友到一个好友分组|
|deleteFriendsFromFrie ndGroup|从好友分组中删除好友|
|subscribeOfficialAccou nt|订阅公众号|
|unsubscribeOfficialAcc ount|取消订阅公众号|
|getOfficialAccountsInf o|获取公众号列表|
|followUser|关注用户|
|unfollowUser|取消关注用户|

版权所有:腾讯云计算(北京)有限责任公司 

第48 共117页 

即时通信 IM 

|getMyFollowingList|获取我的关注列表|
|---|---|
|getMutualFollowersLis t|获取我的互关列表|
|getUserFollowInfo|获取指定用户的 关注/粉丝/互关 数量信息|
|checkFollowType|检查指定用户的关注类型|

版权所有:腾讯云计算(北京)有限责任公司 

第49 共117页 

即时通信 IM 

# Flutter 

最近更新时间:2024-02-27 14:08:21 

即时通信 IM 为您准备了 Flutter 的 API 调用示例,您可以访问 GitHub 获取源码。 

## 初始化并成功登录,是正常使用腾讯云 IM 服务的前提。 

|API|描述|
|---|---|
|initSDK|初始化 SDK|
|unInitSDK|反初始化 SDK|
|login|登录|
|logout|登出|
|getLoginUser|获取当前登录用户的 UserID|
|getLoginStatus|获取登录状态|
|getServerTime|获取服务器当前时间(Web不支持)|
|getVersion|获取版本号|
|getConversationManager|会话功能模块|
|getFriendshipManager|关系链功能模块|
|getGroupManager|高级群组功能模块|
|getMessageManager|高级消息功能模块|
|getOfflinePushManager|离线推送模块|
|getSignalingManager|信令模块|

|API|描述|
|---|---|
|addSignalingListener|添加信令监听|

版权所有:腾讯云计算(北京)有限责任公司 

第50 共117页 

即时通信 IM 

|removeSignalingListener|移除信令监听|
|---|---|
|invite|邀请某个人|
|inviteInGroup|邀请群内的某些人|
|cancel|邀请方取消邀请|
|accept|接收方接受邀请|
|reject|接收方拒绝邀请|
|getSignalingInfo|获取信令信息|
|addInvitedSignaling|创建一个信令请求|

## 创建的消息会返回一个id字段,将id字段等传递给统一的发送接口(sendMessage)即可发送消息。 

|API|描述|
|---|---|
|createTextMessage|创建文本消息|
|createCustomMessage|创建定制化消息|
|createImageMessage|创建图片消息|
|createSoundMessage|创建音频文件|
|createVideoMessage|创建视频文件|
|createTextAtMessage|创建AT消息|
|createFileMessage|创建文件消息|
|createLocationMessage|创建位置信息|
|createFaceMessage|创建表情消息|
|createMergerMessage|创建合并消息|
|createForwardMessage|创建转发消息|
|createTargetedGroupMessage|创建一条定向群消息|
|appendMessage|添加多Element消息|

版权所有:腾讯云计算(北京)有限责任公司 

第51 共117页 

即时通信 IM 

如果您需要收发图片、视频、文件等富媒体消息,并需要撤回消息、标记已读、查询历史消息等高级功能,推荐使用 下面这套高级消息接口(原3.6.0前的高级消息部分接口已弃用,请使用新版创建消息接口后调用发送消息接口)。 

|API|描述|
|---|---|
|addAdvancedMsgListener|设置高级消息的事件监听器|
|removeAdvancedMsgListener|移除高级消息的事件监听器|
|getC2CHistoryMessageList|获取单聊(C2C)历史消息|
|getHistoryMessageList|获取历史消息高级接口|
|getGroupHistoryMessageList|获取群组历史消息|
|markC2CMessageAsRead|设置单聊(C2C)消息已读|
|markGroupMessageAsRead|设置群组消息已读|
|markAllMessageAsRead|标记所有消息为已读|
|deleteMessageFromLocalStorag e|删除本地消息|
|deleteMessages|删除本地及漫游消息|
|insertGroupMessageToLocalSto rage|向群组消息列表中添加一条消息|
|insertC2CMessageToLocalStora ge|向C2C消息列表中添加一条消息|
|clearC2CHistoryMessage|清空单聊本地及云端的消息(不删除会话)|
|clearGroupHistoryMessage|清空群组及云端的消息(不删除会话)|
|downloadMergerMessage|获取合并消息的子消息|
|reSendMessage|消息重发|
|setC2CReceiveMessageOpt|设置针对某个用户的 C2C 消息接收选项(支持批量设置)|
|getC2CReceiveMessageOpt|查询针对某个用户的 C2C 消息接收选项|
|setGroupReceiveMessageOpt|修改群消息接收选项|

版权所有:腾讯云计算(北京)有限责任公司 

第52 共117页 

即时通信 IM 

|setLocalCustomData|设置消息自定义数据(本地保存,不会发送到对端,程序卸载重 装后失效)|
|---|---|
|setLocalCustomInt|设置消息自定义数据,可以用来标记语音、视频消息是否已经播 放(本地保存,不会发送到对端,程序卸载重装后失效)|
|revokeMessage|撤回消息的时间限制默认 2 minutes,超过 2 minutes 的消 息不能撤回,您也可以在 控制台(功能配置 -> 登录与消息 -> 消息撤回设置)自定义撤回时间限制。|
|modifyMessage|消息变更|
|sendMessage|发送消息|
|sendReplyMessage|发送回复消息|
|searchLocalMessages|搜索本地消息|
|sendMessageReadReceipts|发送群消息已读回执|
|getMessageReadReceipts|获取自己发送消息的已读回执|
|getGroupMessageReadMember List|获取自己发送的群消息已读(未读)群成员列表|

## 腾讯云 IM SDK 支持五种预设的群组类型,每种类型都有其适用场景: 

- 工作群(Work) :类似普通微信群,创建后不能自由加入,必须由已经在群的用户邀请入群,同旧版本中的 Private。 

- 公开群(Public) :类似 QQ 群,用户申请加入,但需要群主或管理员审批。 

- 会议群(Meeting):适合跟 TRTC 结合实现视频会议和在线教育等场景,支持随意进出,支持查看进群前的 历史消息,同旧版本中的 ChatRoom。 

- 社群(Community):创建后可以随意进出,适合用于知识分享和游戏交流等超大社区群聊场景。 

- 直播群(AVChatRoom):适合直播弹幕聊天室等场景,支持随意进出,人数无上限。 

|API|描述|
|---|---|
|addGroupListener|添加群组监听器|
|setGroupListener|设置群组相关的事件监听器|
|removeGroupListener|移除群组监听器|
|createGroup|创建群组(高级版本),可在建群同时设置群信息和初始的群成|

版权所有:腾讯云计算(北京)有限责任公司 

第53 共117页 

即时通信 IM 

||员|
|---|---|
|joinGroup|加入群组|
|quitGroup|退出群组|
|dismissGroup|解散群组(仅群主和管理员可以解散)|
|getJoinedGroupList|获取已经加入的群列表(不包括已加入的直播群)|
|getGroupsInfo|拉取群资料|
|setGroupInfo|修改群资料|
|initGroupAttributes|初始化群属性,会清空原有的群属性列表|
|setGroupAttributes|设置群属性。已有该群属性则更新其 value 值,没有该群属性 则添加该属性。|
|deleteGroupAttributes|删除指定群属性,keys 传 null 则清空所有群属性。|
|getGroupAttributes|获取指定群属性,keys 传 null 则获取所有群属性。|
|searchGroups|搜索群列表|
|getGroupOnlineMemberCount|获取指定群在线人数(目前只支持直播群)|
|getGroupMemberList|获取群成员列表|
|getGroupMembersInfo|获取指定的群成员资料|
|setGroupMemberInfo|修改指定的群成员资料|
|searchGroupMembers|搜索群成员|
|muteGroupMember|禁言|
|kickGroupMember|踢人|
|setGroupMemberRole|切换群成员的角色|
|transferGroupOwner|转让群主|
|inviteUserToGroup|邀请他人入群|
|getGroupApplicationList|获取加群的申请列表|
|acceptGroupApplication|同意某一条加群申请|
|refuseGroupApplication|拒绝某一条加群申请|

版权所有:腾讯云计算(北京)有限责任公司 

第54 共117页 

即时通信 IM 

|setGroupApplicationRead|标记申请列表为已读|
|---|---|
|getJoinedCommunityList|获取当前用户已经加入的支持话题的社群列表|
|createTopicInCommunity|创建话题|
|deleteTopicFromCommunity|删除话题|
|setTopicInfo|设置话题属性|
|getTopicInfoList|获取话题属性的列表|

会话列表,即登录微信或 QQ 后首屏看到的列表,包含会话节点、会话名称、群名称、最后一条消息以及未读消息 数等元素。 

|API|描述|
|---|---|
|addConversationListener|添加关系链监听器|
|removeConversationListener|移除关系链监听器|
|setConversationListener|设置会话监听器|
|getConversationList|获取会话列表|
|getConversationListByConversa ionIds|通过会话ID获取指定会话列表|
|pinConversation|会话置顶|
|getTotalUnreadMessageCount|获取会话未读总数|
|getConversation|获取指定会话|
|deleteConversation|删除会话|
|setConversationDraft|设置会话草稿|

## 包含查询用户资料、修改个人资料以及屏蔽某人消息(即把某用户加入黑名单中)的相关接口。 

|API|描述|
|---|---|
|getUsersInfo|获取用户资料|

版权所有:腾讯云计算(北京)有限责任公司 

第55 共117页 

即时通信 IM 

|getUserStatus|获取用户在线状态|
|---|---|
|setSelfInfo|修改个人资料|
|setSelfStatus|设置当前登录用户在线状态|
|addToBlackList|屏蔽某人的消息(添加该用户到黑名单中)|
|deleteFromBlackList|取消某人的消息屏蔽(把该用户从黑名单中移除)|
|getBlackList|获取黑名单列表|

如果想要在 App 切后台时依然能够实时收到 IM 消息,可以使用离线推送服务。由于大陆境内尚没有统一的推送服 务,Android 的离线推送需要针对不同厂商的手机进行 逐一适配 。 

|API|描述|
|---|---|
|setAPNSListener|设置苹果系统离线推送专用监听器|
|doBackground|设置离线推送配置信息|
|doForeground|设置离线推送配置信息|
|setOfflinePushConfig|设置离线推送配置信息|

腾讯云 IM 在收发消息时默认不检查是不是好友关系,您可以在 控制台 > 功能配置 > 登录与消息 > 好友关系检查 中开启"发送单聊消息检查关系链"开关,并使用如下接口增删好友和管理好友列表。 

|API|描述|
|---|---|
|setFriendListener|设置关系链的监听器,用于接收好友列表和黑名单的变更事件|
|addFriendListener|添加关系链监听器|
|removeFriendListener|移除关系链监听器|
|getFriendList|获取好友列表|
|getFriendsInfo|获取指定好友资料|
|setFriendInfo|设置指定好友资料|
|addFriend|添加好友|

版权所有:腾讯云计算(北京)有限责任公司 

第56 共117页 

即时通信 IM 

|deleteFromFriendList|删除好友|
|---|---|
|checkFriend|检查指定用户的好友关系|
|getFriendApplicationList|获取好友申请列表|
|acceptFriendApplication|同意好友申请|
|refuseFriendApplication|拒绝好友申请|
|deleteFriendApplication|删除好友申请|
|setFriendApplicationRead|设置好友申请已读|
|createFriendGroup|新建好友分组|
|getFriendGroups|获取分组信息|
|deleteFriendGroup|删除好友分组|
|renameFriendGroup|修改好友分组的名称|
|addFriendsToFriendGroup|添加好友到一个好友分组|
|deleteFriendsFromFriendGroup|从好友分组中删除好友|
|searchFriends|搜索好友|

版权所有:腾讯云计算(北京)有限责任公司 

第57 共117页 

即时通信 IM 

# Unity 

最近更新时间:2022-12-06 17:16:59 

更为详细的接口,请参见 Unity 全部接口 。 

|API|描述|
|---|---|
|ConvCancelDraft|取消会话草稿|
|ConvDelete|删除会话|
|ConvGetConvInfo|获取会话信息|
|ConvGetConvList|获取会话列表|
|ConvGetTotalUnreadMessageCount|获取全部会话未读数|
|ConvPinConversation|会话置顶|
|ConvSetDraft|设置会话草稿|

|API|描述|
|---|---|
|FriendshipAddFriend|添加好友|
|FriendshipAddToBlackList|添加黑名单|
|FriendshipCheckFriendType|检测好友关系|
|FriendshipCreateFriendGroup|创建好友分组|
|FriendshipDeleteFriend|删除好友|
|FriendshipDeleteFriendGroup|删除好友分组列表|
|FriendshipDeleteFromBlackList|从黑名单删除|
|FriendshipDeletePendency|删除好友申请未决|

版权所有:腾讯云计算(北京)有限责任公司 

第58 共117页 

即时通信 IM 

|FriendshipGetBlackList|获取黑名单列表|
|---|---|
|FriendshipGetFriendGroupList|获取好友分组列表|
|FriendshipGetFriendProfileList|获取好友列表信息|
|FriendshipGetFriendsInfo|获取好友信息|
|FriendshipGetPendencyList|获取好友申请未决|
|FriendshipHandleFriendAddRequest|处理好友申请|
|FriendshipModifyFriendGroup|修改好友分组列表|
|FriendshipModifyFriendProfile|修改好友信息|
|FriendshipReportPendencyReaded|上报好友申请未决已读|
|FriendshipSearchFriends|搜索好友|

|API|描述|
|---|---|
|GroupCreate|创建群|
|GroupCreateTopicInCommunity|创建话题|
|GroupDelete|删除群|
|GroupDeleteGroupAttributes|删除群自定义属性|
|GroupDeleteMember|踢出群成员|
|GroupDeleteTopicFromCommunity|删除话题|
|GroupGetGroupAttributes|获取群指定属性|
|GroupGetGroupInfoList|获取群信息|
|GroupGetJoinedCommunityList|获取当前用户已经加入的支持话题的社群列表|
|GroupGetJoinedGroupList|获取已加入的群组列表|
|GroupGetMemberInfoList|获取群成员信息|
|GroupGetOnlineMemberCount|获取群在线用户数|

版权所有:腾讯云计算(北京)有限责任公司 

第59 共117页 

即时通信 IM 

|GroupGetPendencyList|获取群未决信息列表|
|---|---|
|GroupGetTopicInfoList|获取话题列表|
|GroupHandlePendency|处理群未决信息|
|GroupInitGroupAttributes|初始化群自定义属性|
|GroupInviteMember|邀请用户进群|
|GroupJoin|加入群|
|GroupModifyGroupInfo|修改群信息|
|GroupModifyMemberInfo|修改群成员信息|
|GroupQuit|退出群|
|GroupReportPendencyReaded|上报群未决信息已读|
|GroupSearchGroupMembers|搜索群成员|
|GroupSearchGroups|搜索群资料|
|GroupSetGroupAttributes|设置群属性|
|GroupSetTopicInfo|修改话题信息|

|API|描述|
|---|---|
|GetSDKVersion|获取SDK底层库版本|
|GetServerTime|获取服务端时间(秒)|
|Init|初始化IM SDK|
|SetConfig|设置全局配置|
|Uninit|反初始化IM SDK|

|API|描述|
|---|---|
|GetLoginStatus|获取当前登录状态|

版权所有:腾讯云计算(北京)有限责任公司 

第60 共117页 

即时通信 IM 

|GetLoginUserID|获取当前登录用户ID|
|---|---|
|Login|登录|
|Logout|登出|

|API|描述|
|---|---|
|GetMsgGroupMessageReadMemberList|获取群消息已读群成员列表|
|MsgBatchSend|批量发送消息|
|MsgCancelSend|取消消息发送|
|MsgClearHistoryMessage|清除历史消息|
|MsgDelete|消息删除|
|MsgDoBackground|APP 检测到应用退后台时可以调用此接口。|
|MsgDoForeground|APP 检测到应用进前台时可以调用此接口|
|MsgDownloadElemToPath|下载多媒体消息|
|MsgDownloadMergerMessage|下载合并消息|
|MsgFindByMsgLocatorList|通过消息定位符查找消息|
|MsgFindMessages|从本地查找消息|
|MsgGetC2CReceiveMessageOpt|获取C2C收消息选项|
|MsgGetMessageReadReceipts|获取消息已读回执|
|MsgGetMsgList|获取历史消息列表|
|MsgImportMsgList|导入消息|
|MsgListDelete|消息删除|
|MsgMarkAllMessageAsRead|标记所有消息为已读|
|MsgModifyMessage|消息变更|
|MsgReportReaded|消息已读上报 C2C|

版权所有:腾讯云计算(北京)有限责任公司 

第61 共117页 

即时通信 IM 

|MsgRevoke|消息撤回|
|---|---|
|MsgSaveMsg|保存消息|
|MsgSearchLocalMessages|搜索本地消息|
|MsgSendMessage|发送消息|
|MsgSendMessageReadReceipts|发送消息已读回执|
|MsgSetC2CReceiveMessageOpt|设置收消息选项|
|MsgSetGroupReceiveMessageOpt|设置群收消息选项|
|MsgSetLocalCustomData|设置消息本地数据|
|MsgSetOfflinePushToken|设置离线推送配置信息|

|API|描述|
|---|---|
|GetUserStatus|查询用户状态|
|ProfileGetUserProfileList|获取用户信息列表|
|ProfileModifySelfUserProfile|修改自己的信息|
|SetSelfStatus|设置自己的状态|
|SubscribeUserStatus|订阅用户状态|
|UnsubscribeUserStatus|取消订阅用户状态|

|API|描述|
|---|---|
|AddRecvNewMsgCallback|注册收到新消息回调|
|RemoveRecvNewMsgCallback|移除收到新消息回调|
|SetConvEventCallback|设置会话事件回调|
|SetConvTotalUnreadMessageCountChangedCal lback|设置会话未读消息总数变更的回调|

版权所有:腾讯云计算(北京)有限责任公司 

第62 共117页 

即时通信 IM 

|SetFriendAddRequestCallback|设置好友添加请求的回调|
|---|---|
|SetFriendApplicationListDeletedCallback|设置好友申请被删除的回调|
|SetFriendApplicationListReadCallback|设置好友申请已读的回调|
|SetFriendBlackListAddedCallback|设置黑名单新增的回调|
|SetFriendBlackListDeletedCallback|设置黑名单删除的回调|
|SetGroupAttributeChangedCallback|设置群组属性变更回调|
|SetGroupTipsEventCallback|设置群组系统消息回调|
|SetGroupTopicChangedCallback|设置话题更新回调|
|SetGroupTopicCreatedCallback|设置话题创建回调|
|SetGroupTopicDeletedCallback|设置话题被删除回调|
|SetKickedOfflineCallback|设置被踢下线通知回调|
|SetLogCallback|设置日志回调|
|SetMsgElemUploadProgressCallback|设置消息内元素相关文件上传进度回调|
|SetMsgReadedReceiptCallback|设置消息已读回执回调|
|SetMsgRevokeCallback|设置接收的消息被撤回回调|
|SetMsgUpdateCallback|设置消息在云端被修改后回传回来的更新通 知回调|
|SetNetworkStatusListenerCallback|设置网络连接状态监听回调|
|SetOnAddFriendCallback|设置添加好友的回调|
|SetOnDeleteFriendCallback|设置删除好友的回调|
|SetSelfInfoUpdatedCallback|设置当前用户的资料发生更新时的回调|
|SetUpdateFriendProfileCallback|设置更新好友资料的回调|
|SetUserSigExpiredCallback|设置票据过期回调|
|SetUserStatusChangedCallback|设置用户状态变更通知回调|

版权所有:腾讯云计算(北京)有限责任公司 

第63 共117页 

即时通信 IM 

# C 接口 IM SDK 接口 

最近更新时间:2025-01-21 17:44:53 

## 初始化并成功登录,是正常使用腾讯云 IM 服务的前提。 

|API|描述|
|---|---|
|TIMInit|IM SDK 初始化|
|TIMUninit|IM SDK 卸载|
|TIMGetSDKVersion|获取 IM SDK 版本号|
|TIMGetServerTime|获取服务器当前时间|
|TIMSetConfig|设置额外的用户配置|

|API|描述|
|---|---|
|TIMLogin|登录|
|TIMLogout|登出|
|TIMGetLoginUserID|获取登录用户的 userID|
|TIMGetLoginStatus|获取登录状态|

|API|描述|
|---|---|
|TIMMsgSendMessage|发送新消息|
|TIMMsgCancelSend|根据消息 messageID 取消发送中的消息|
|TIMMsgBatchSend|群发消息,该接口不支持向群组发送消息。|
|TIMMsgDownloadElemToPath|下载消息内元素到指定文件路径(图片、视频、音 频、文件)|

版权所有:腾讯云计算(北京)有限责任公司 

第64 共117页 

即时通信 IM 

|TIMMsgDownloadMergerMessage|下载合并消息|
|---|---|
|TIMMsgSetLocalCustomData|设置消息自定义数据(本地保存,不会发送到对端, 程序卸载重装后失效)|
|TIMMsgSetC2CReceiveMessageOpt|设置针对某个用户的 C2C 消息接收选项(支持批量 设置)|
|TIMMsgGetC2CReceiveMessageOpt|查询针对某个用户的 C2C 消息接收选项|
|TIMMsgSetGroupReceiveMessageOpt|设置群消息的接收选项|
|TIMMsgSetAllReceiveMessageOpt|设置登录用户全局消息接收选项|
|TIMMsgSetAllReceiveMessageOpt2|设置登录用户全局消息接收选项|
|TIMMsgGetAllReceiveMessageOpt|获取登录用户全局消息接收选项|
|TIMMsgGetMsgList|获取指定会话的消息列表|
|TIMMsgRevoke|消息撤回|
|TIMMsgModifyMessage|消息修改|
|TIMMsgDelete|删除指定会话的消息|
|TIMMsgListDelete|删除指定会话的本地及漫游消息列表|
|TIMMsgClearHistoryMessage|清空指定会话的消息|
|TIMMsgSaveMsg|保存自定义消息|
|TIMMsgImportMsgList|导入消息列表到指定会话|
|TIMMsgFindMessages|根据消息 messageID 查询本地的消息列表|
|TIMMsgFindByMsgLocatorList|根据消息定位精准查找指定会话的消息|
|TIMMsgSearchLocalMessages|搜索本地消息|
|TIMMsgSearchCloudMessages|搜索云端消息|
|TIMMsgSendMessageReadReceipts|发送消息已读回执|
|TIMMsgGetMessageReadReceipts|获取消息已读回执|
|TIMMsgGetGroupMessageReadMemberL ist|获取群消息已读群成员列表|

版权所有:腾讯云计算(北京)有限责任公司 

第65 共117页 

即时通信 IM 

|TIMMsgSetMessageExtensions|设置消息扩展|
|---|---|
|TIMMsgGetMessageExtensions|获取消息扩展|
|TIMMsgDeleteMessageExtensions|删除消息扩展|
|TIMMsgAddMessageReaction|添加消息回应|
|TIMMsgRemoveMessageReaction|删除消息回应|
|TIMMsgGetMessageReactions|批量拉取多条消息回应信息|
|TIMMsgGetAllUserListOfMessageReactio n|分页拉取使用指定消息回应用户信息|
|TIMMsgTranslateText|翻译文本消息|
|TIMPinGroupMessage|设置群消息置顶|
|TIMGetPinnedMessageList|获取已置顶的群消息列表|

会话列表,即登录微信或 QQ 后首屏看到的列表,包含会话节点、会话名称、群名称、最后一条消息以及未读消息 数等元素。 

|API|描述|
|---|---|
|TIMConvGetConvList|获取会话列表|
|TIMConvGetConvInfo|查询一组会话列表|
|TIMConvGetConversationListByFilter|获取会话列表高级接口|
|TIMConvDelete|删除会话|
|TIMConvDeleteConversationList|删除会话列表|
|TIMConvSetDraft|设置指定会话的草稿|
|TIMConvCancelDraft|删除指定会话的草稿|
|TIMConvSetConversationCustomData|设置会话自定义数据|
|TIMConvPinConversation|设置会话置顶|
|TIMConvMarkConversation|标记会话|

版权所有:腾讯云计算(北京)有限责任公司 

第66 共117页 

即时通信 IM 

|TIMConvGetTotalUnreadMessageCount|获取所有会话总的未读消息数|
|---|---|
|TIMConvGetUnreadMessageCountByFilte r|根据 filter 获取未读总数|
|TIMConvSubscribeUnreadMessageCount ByFilter|注册监听指定 filter 的会话未读总数变化|
|TIMConvUnsubscribeUnreadMessageCou ntByFilter|取消监听指定 filter 的会话未读总数变化|
|TIMConvCleanConversationUnreadMessa geCount|清理会话的未读消息计数|
|TIMConvCreateConversationGroup|创建会话分组|
|TIMConvGetConversationGroupList|获取会话分组列表|
|TIMConvDeleteConversationGroup|删除会话分组|
|TIMConvRenameConversationGroup|重命名会话分组|
|TIMConvAddConversationsToGroup|添加会话到一个会话分组|
|TIMConvDeleteConversationsFromGroup|从会话分组中删除多个会话|

## 腾讯云 IM SDK 支持以下预设的群组类型,每种类型都有其适用场景: 

- 工作群(Work):类似普通微信群,创建后不能自由加入,必须由已经在群的用户邀请入群。 

- 公开群(Public):类似 QQ 群,用户申请加入,但需要群主或管理员审批。 

- 会议群(Meeting):适合跟 TRTC 结合实现视频会议和在线教育等场景,支持随意进出,支持查看进群前的 历史消息。 

- 社群(Community):社群成员上限 100000 人,任何人都可以自由进出,且加群无需被审批,适合用于知 识分享和游戏交流等超大社区群聊场景。5.8 版本开始支持,需 购买旗舰版或企业版套餐包 并在 控制台 >功能 配置  > 群组配置 > 群功能配置 > 社群 中开通。 

直播群(AVChatRoom):适合直播弹幕聊天室等场景,支持随意进出,人数无上限。 

|API|描述|
|---|---|
|TIMGroupCreate|创建群组|
|TIMGroupDelete|删除(解散)群组|
|TIMGroupJoin|申请加入群组|

版权所有:腾讯云计算(北京)有限责任公司 

第67 共117页 

即时通信 IM 

|TIMGroupQuit|退出群组|
|---|---|
|TIMGroupGetJoinedGroupList|获取已加入群组列表|
|TIMGroupGetGroupInfoList|获取群组信息列表|
|TIMGroupSearchGroups|搜索本地群资料|
|TIMGroupSearchCloudGroups|搜索云端群资料|
|TIMGroupModifyGroupInfo|修改群信息|
|TIMGroupInitGroupAttributes|初始化群属性,会清空原有的群属性列表|
|TIMGroupSetGroupAttributes|设置群属性,已有该群属性则更新其 value 值,没 有该群属性则添加该群属性|
|TIMGroupDeleteGroupAttributes|删除群属性|
|TIMGroupGetGroupAttributes|获取群指定属性,若传入的 json_keys 为空,则获 取所有群属性|
|TIMGroupGetOnlineMemberCount|获取指定群在线人数|
|TIMGroupSetGroupCounters|设置群计数器|
|TIMGroupGetGroupCounters|获取群计数器|
|TIMGroupIncreaseGroupCounter|递增群计数器|
|TIMGroupDecreaseGroupCounter|递减群计数器|
|TIMGroupGetJoinedCommunityList|获取当前用户已经加入的支持话题的社群列表|
|TIMGroupCreateTopicInCommunity|创建话题|
|TIMGroupDeleteTopicFromCommunity|删除话题|
|TIMGroupSetTopicInfo|修改话题信息|
|TIMGroupGetTopicInfoList|获取话题列表|
|TIMGroupGetMemberInfoList|获取群成员信息列表|
|TIMGroupSearchGroupMembers|搜索本地群成员资料|
|TIMGroupSearchCloudGroupMembers|搜索云端群成员资料|
|TIMGroupModifyMemberInfo|修改群成员信息|

版权所有:腾讯云计算(北京)有限责任公司 

第68 共117页 

即时通信 IM 

|TIMGroupInviteMember|邀请加入群组|
|---|---|
|TIMGroupDeleteMember|删除群组成员|
|TIMGroupMarkGroupMemberList|标记群成员|
|TIMGroupGetPendencyList|获取群未决信息列表。 群未决信息是指还没有处理的操作,例如,邀请加群 或者请求加群操作还没有被处理,称之为群未决信息|
|TIMGroupHandlePendency|处理群未决信息|
|TIMGroupReportPendencyReaded|上报群未决信息已读|

|API|描述|
|---|---|
|TIMCommunityCreate|创建支持话题的社群|
|TIMCommunityGetJoinedCommunityList|获取当前用户已经加入的支持话题的社群列表|
|TIMCommunityCreateTopicInCommunity|创建话题|
|TIMCommunityDeleteTopicFromCommuni ty|删除话题|
|TIMCommunitySetTopicInfo|修改话题信息|
|TIMCommunityGetTopicInfoList|获取话题列表|
|TIMCommunityCreatePermissionGroupIn Community|创建权限组|
|TIMCommunityDeletePermissionGroupFr omCommunity|删除权限组|
|TIMCommunityModifyPermissionGroupInf oInCommunity|修改权限组信息|
|TIMCommunityGetJoinedPermissionGrou pListInCommunity|获取已加入的权限组列表|
|TIMCommunityGetPermissionGroupListIn Community|获取权限组列表|
|TIMCommunityAddCommunityMembersT|向社群权限组添加成员|

版权所有:腾讯云计算(北京)有限责任公司 

第69 共117页 

即时通信 IM 

|oPermissionGroup||
|---|---|
|TIMCommunityRemoveCommunityMemb ersFromPermissionGroup|从社群权限组删除成员|
|TIMCommunityGetCommunityMemberList InPermissionGroup|获取社群权限组成员列表|
|TIMCommunityAddTopicPermissionToPer missionGroup|向权限组添加话题权限|
|TIMCommunityDeleteTopicPermissionFro mPermissionGroup|从权限组中删除话题权限|
|TIMCommunityModifyTopicPermissionInP ermissionGroup|修改权限组中的话题权限|
|TIMCommunityGetTopicPermissionInPer missionGroup|获取权限组中的话题权限|

|API|描述|
|---|---|
|TIMProfileGetUserProfileList|获取指定用户列表的个人资料|
|TIMProfileModifySelfUserProfile|修改自己的个人资料|
|TIMSubscribeUserInfo|订阅陌生人资料|
|TIMUnsubscribeUserInfo|取消订阅陌生人资料|
|TIMSearchUsers|搜索云端用户资料|

|API|描述|
|---|---|
|TIMGetUserStatus|获取指定用户列表的状态|
|TIMSetSelfStatus|设置自己的状态|
|TIMSubscribeUserStatus|订阅用户状态|
|TIMUnsubscribeUserStatus|取消订阅用户状态|

版权所有:腾讯云计算(北京)有限责任公司 

第70 共117页 

即时通信 IM 

腾讯云 IM 在收发消息时默认不检查是不是好友关系,您可以在 控制台 >功能配置>登录与消息>好友关系检查 中 开启"发送单聊消息检查关系链"开关,并使用如下接口增删好友和管理好友列表。 

|API|描述|
|---|---|
|TIMFriendshipGetFriendProfileList|获取好友列表|
|TIMFriendshipGetFriendsInfo|获取好友信息|
|TIMFriendshipModifyFriendProfile|更新好友资料(备注等)|
|TIMFriendshipSearchFriends|搜索好友|
|TIMFriendshipAddFriend|添加好友|
|TIMFriendshipDeleteFriend|删除好友|
|TIMFriendshipCheckFriendType|检测好友类型(单向或双向)|
|TIMFriendshipGetPendencyList|获取好友添加请求未决信息列表|
|TIMFriendshipHandleFriendAddRequest|处理好友请求|
|TIMFriendshipReportPendencyReaded|上报好友添加请求未决信息已读|
|TIMFriendshipDeletePendency|删除指定好友添加请求未决信息|
|TIMFriendshipGetBlackList|获取黑名单列表|
|TIMFriendshipAddToBlackList|添加指定用户到黑名单|
|TIMFriendshipDeleteFromBlackList|从黑名单中删除指定用户列表|
|TIMFriendshipCreateFriendGroup|创建好友分组|
|TIMFriendshipGetFriendGroupList|获取指定好友分组的分组信息|
|TIMFriendshipDeleteFriendGroup|删除好友分组|
|TIMFriendshipModifyFriendGroup|修改好友分组|

## 公众号可以为订阅的用户发送广播消息,也可以与订阅的用户进行单聊。 

|API|描述|
|---|---|
|TIMSubscribeOfficialAccount|订阅公众号|

版权所有:腾讯云计算(北京)有限责任公司 

第71 共117页 

即时通信 IM 

|TIMUnsubscribeOfficialAccount|取消订阅公众号|
|---|---|
|TIMGetOfficialAccountsInfo|获取公众号列表|

## 关注和粉丝功能可以帮助建立和维护用户之间相对简单的连接关系,方便促进用户之间的互动和交流。 

|API|描述|
|---|---|
|TIMFollowUser|关注用户|
|TIMUnfollowUser|取消关注用户|
|TIMGetMyFollowingList|获取我的关注列表|
|TIMGetMyFollowersList|获取我的粉丝列表|
|TIMGetMutualFollowersList|获取我的互关列表|
|TIMGetUserFollowInfo|获取指定用户的 关注/粉丝/互关 数量信息|
|TIMCheckFollowType|检查指定用户的关注类型|

|API|描述|
|---|---|
|TIMMsgSetOfflinePushToken|设置离线推送配置信息(iOS 和 Android 平台专 用)|
|TIMMsgDoBackground|APP 检测到应用退后台时可以调用此接口,可以用 作桌面应用角标的初始化未读数量(iOS 和 Android 平台专用)|
|TIMMsgDoForeground|APP 检测到应用进前台时可以调用此接口(iOS 和 Android 平台专用)|

|API|描述|
|---|---|
|TIMSignalingInvite|邀请某个人|
|TIMSignalingInviteInGroup|邀请群内的某些人|

版权所有:腾讯云计算(北京)有限责任公司 

第72 共117页 

即时通信 IM 

|TIMSignalingCancel|邀请方取消邀请|
|---|---|
|TIMSignalingAccept|被邀请方接受邀请|
|TIMSignalingReject|被邀请方拒绝邀请|
|TIMGetSignalingInfo|获取信令信息|
|TIMSignalingModifyInvitation|修改邀请信令|

事件回调设置接口
初始化以及登录相关回调设置接口

|API|描述|
|---|---|
|TIMSetNetworkStatusListenerCallback|设置网络状态回调|
|TIMSetKickedOfflineCallback|设置被踢下线回调|
|TIMSetUserSigExpiredCallback|设置用户票据过期回调|
|TIMSetLogCallback|设置日志回调|

|API|描述|
|---|---|
|TIMAddRecvNewMsgCallback|增加接收新消息回调|
|TIMRemoveRecvNewMsgCallback|删除接收新消息回调|
|TIMSetMsgElemUploadProgressCallback|设置消息内元素相关文件上传进度回调|
|TIMSetMsgReadedReceiptCallback|设置消息已读回执回调|
|TIMSetMsgRevokeCallback|设置接收的消息被撤回回调|
|TIMSetMsgUpdateCallback|设置消息在云端被修改后回传回来的消息更新通知回 调|
|TIMSetMsgExtensionsChangedCallback|设置消息扩展信息更新的回调|
|TIMSetMsgExtensionsDeletedCallback|设置消息扩展信息删除的回调|
|TIMSetMsgReactionsChangedCallback|设置消息回应信息更新的回调|

版权所有:腾讯云计算(北京)有限责任公司 

第73 共117页 

即时通信 IM 

|TIMSetMsgAllMessageReceiveOptionCall back|设置全局消息接收选项的回调|
|---|---|

|API|描述|
|---|---|
|TIMSetConvEventCallback|设置会话事件回调|
|TIMSetConvTotalUnreadMessageCountC hangedCallback|设置会话未读消息总数变更的回调|
|TIMSetConvUnreadMessageCountChang edByFilterCallback|设置按会话 filter 过滤的未读消息总数变更的回调|
|TIMSetConvConversationGroupCreatedC allback|设置会话分组被创建回调|
|TIMSetConvConversationGroupDeletedC allback|设置会话分组被删除的回调|
|TIMSetConvConversationGroupNameCha ngedCallback|设置会话分组命名变更回调|
|TIMSetConvConversationsAddedToGroup Callback|设置会话分组新增会话的回调|
|TIMSetConvConversationsDeletedFromG roupCallback|设置会话分组删除会话的回调|

|API|描述|
|---|---|
|TIMSetGroupTipsEventCallback|设置群组系统消息回调|
|TIMSetGroupAttributeChangedCallback|设置群组属性变更回调|
|TIMSetGroupCounterChangedCallback|设置群计数器变更回调|
|TIMSetGroupTopicCreatedCallback|设置话题被创建的回调|
|TIMSetGroupTopicDeletedCallback|设置话题被删除的回调|
|TIMSetGroupTopicChangedCallback|设置话题更新的回调|

版权所有:腾讯云计算(北京)有限责任公司 

第74 共117页 

即时通信 IM 

|API|描述|
|---|---|
|TIMSetCommunityCreateTopicCallback|设置话题被创建的回调|
|TIMSetCommunityDeleteTopicCallback|设置话题被删除的回调|
|TIMSetCommunityChangeTopicInfoCallba ck|设置话题更新的回调|
|TIMSetCommunityReceiveTopicRESTCus tomDataCallback|设置 RESTAPI 下发的话题自定义系统消息的回调|
|TIMSetCommunityCreatePermissionGrou pCallback|设置权限组被创建的回调|
|TIMSetCommunityDeletePermissionGrou pCallback|设置权限组被删除的回调|
|TIMSetCommunityChangePermissionGro upInfoCallback|设置权限组更新的回调|
|TIMSetCommunityAddMembersToPermis sionGroupCallback|设置向权限组中添加成员的回调|
|TIMSetCommunityRemoveMembersFrom PermissionGroupCallback|设置从权限组中删除成员的回调|
|TIMSetCommunityAddTopicPermissionCa llback|设置向权限组中增加话题权限的回调|
|TIMSetCommunityDeleteTopicPermission Callback|设置从权限组删除话题权限的回调|
|TIMSetCommunityModifyTopicPermission Callback|设置权限组中的话题权限修改的回调|

|API|描述|
|---|---|
|TIMSetSelfInfoUpdatedCallback|设置当前用户资料更新回调|
|TIMSetUserStatusChangedCallback|设置用户状态变更回调|
|TIMSetUserInfoChangedCallback|设置已订阅用户资料变更回调|

版权所有:腾讯云计算(北京)有限责任公司 

第75 共117页 

即时通信 IM 

|API|描述|
|---|---|
|TIMSetOnAddFriendCallback|设置添加好友的回调|
|TIMSetOnDeleteFriendCallback|设置删除好友的回调|
|TIMSetUpdateFriendProfileCallback|设置更新好友资料的回调|
|TIMSetFriendAddRequestCallback|设置好友添加请求的回调|
|TIMSetFriendApplicationListDeletedCallb ack|设置好友申请被删除的回调|
|TIMSetFriendApplicationListReadCallbac k|设置好友申请已读的回调|
|TIMSetFriendBlackListAddedCallback|设置黑名单新增的回调|
|TIMSetFriendBlackListDeletedCallback|设置黑名单删除的回调|
|TIMSetFriendGroupCreatedCallback|设置好友分组被创建的回调|
|TIMSetFriendGroupDeletedCallback|设置好友分组被删除的回调|
|TIMSetFriendGroupNameChangedCallba ck|设置好友分组名变更的回调|
|TIMSetFriendsAddedToGroupCallback|设置好友分组新增好友的回调|
|TIMSetFriendsDeletedFromGroupCallbac k|设置好友分组删除好友的回调|

|API|描述|
|---|---|
|TIMSetOfficialAccountSubscribedCallbac k|设置公众号订阅的回调|
|TIMSetOfficialAccountUnsubscribedCallb ack|设置公众号取消订阅的回调|
|TIMSetOfficialAccountDeletedCallback|设置订阅的公众号被删除的回调|
|TIMSetOfficialAccountInfoChangedCallba ck|设置订阅的公众号资料更新的回调|

版权所有:腾讯云计算(北京)有限责任公司 

第76 共117页 

即时通信 IM 

|API|描述|
|---|---|
|TIMSetMyFollowingListChangedCallback|设置关注列表变更的回调|
|TIMSetMyFollowersListChangedCallback|设置粉丝列表变更的回调|
|TIMSetMutualFollowersListChangedCallb ack|设置互关列表变更的回调|

|API|描述|
|---|---|
|TIMSetSignalingReceiveNewInvitationCall back|设置收到信令邀请的回调|
|TIMSetSignalingInvitationCancelledCallba ck|设置信令邀请被取消的回调|
|TIMSetSignalingInviteeAcceptedCallback|设置信令邀请被接收者同意的回调|
|TIMSetSignalingInviteeRejectedCallback|设置信令邀请被接收者拒绝的回调|
|TIMSetSignalingInvitationTimeoutCallbac k|设置信令邀请超时的回调|
|TIMSetSignalingInvitationModifiedCallbac k|设置信令邀请被修改的回调|

点此进入 IM 社群 ,享有专业工程师的支持,解决您的难题。 

版权所有:腾讯云计算(北京)有限责任公司 

第77 共117页 

即时通信 IM 

# IM SDK 关键类型 

最近更新时间:2024-06-18 14:56:51 

|名称|含义|
|---|---|
|SdKConfig|初始化 IM SDK 的配置|
|UserConfig|用户配置信息|
|HttpProxyInfo|HTTP 代理配置信息|
|Socks5ProxyInfo|SOCKS5 代理配置信息|
|PACProxyInfo|PAC 代理配置信息|
|SetConfig|更新配置|

|名称|含义|
|---|---|
|FriendShipGetProfileListParam|获取指定用户列表的个人资料的参数|
|TIMUserStatus|用户状态|
|UserProfile|用户个人资料|
|UserProfileItem|用户自身资料可修改的各个项|
|UserProfileCustomStringInfo|用户自定义资料字段, 字符串|
|ProfileChangeElem|资料变更通知|

|名称|含义|
|---|---|
|ElemType|消息元素的类型|
|TextElem|文本元素|
|CustomElem|自定义元素|

版权所有:腾讯云计算(北京)有限责任公司 

第78 共117页 

即时通信 IM 

|ImageElem|图片元素|
|---|---|
|SoundElem|音频元素|
|VideoElem|视频元素|
|FileElem|文件元素|
|LocationElem|位置元素|
|FaceElem|表情元素|
|MergerElem|合并消息元素|
|GroupMessageAtALL|@ 群里所有人的参数|
|GroupTipsElem|群组系统消息元素|
|GroupReportElem|群组系统通知元素|
|Message|消息|
|MsgBatchSendParam|消息群发接口的参数|
|MsgBatchSendResult|消息群发接口的返回|
|DownloadElemParam|下载元素接口的参数|
|MsgDownloadElemResult|下载元素接口的返回|

|名称|含义|
|---|---|
|MsgGetMsgListParam|获取历史消息接口的参数|
|MsgLocator|消息定位符|
|MessageSearchParam|消息搜索参数|
|MessageSearchResultItem|消息搜索结果项|
|MessageSearchResult|消息搜索结果返回|
|MsgDeleteParam|消息删除接口的参数|

版权所有:腾讯云计算(北京)有限责任公司 

第79 共117页 

即时通信 IM 

|名称|含义|
|---|---|
|GetC2CRecvMsgOptResult|查询 C2C 消息接收选项的返回|
|TIMReceiveMessageOptInfo|全局消息消息接收选项|

|名称|含义|
|---|---|
|MessageTranslateTextResult|文本消息翻译结果|
|MessageReceipt|消息已读回执|
|MessageExtension|消息扩展信息|
|MessageExtensionResult|消息扩展操作结果|
|MessageReaction|消息回应信息|
|MessageReactionResult|消息回应列表拉取结果|
|MessageReactionUserResult|消息回应用户列表拉取结果|
|MessageReactionChangeInfo|消息回应列表更新信息|

|名称|含义|
|---|---|
|Draft|草稿信息|
|GroupAtInfo|群 @ 信息|
|ConvInfo|会话信息|
|TIMConversationListFilter|获取会话列表高级接口的 filter|
|TIMConversationListResult|获取会话列表的结果|
|GetConversationListParam|获取指定的会话列表|
|GetTotalUnreadNumberResult|获取会话未读消息个数|
|TIMConversationOperationResult|会话操作结果|

版权所有:腾讯云计算(北京)有限责任公司 

第80 共117页 

即时通信 IM 

|名称|含义|
|---|---|
|GroupTipGroupChangeInfo|群组系统消息-群组信息修改|
|GroupTipMemberChangeInfo|群组系统消息-群组成员禁言|
|GroupTipMemberMarkChangeInfo|群组系统消息-群组成员标记变更|
|GroupTipsElem|群组系统消息元素|

|名称|含义|
|---|---|
|GroupMemberInfo|群成员信息|
|CreateGroupParam|创建群组接口的参数|
|CreateGroupResult|创建群组接口的返回|
|GroupSelfInfo|群组内本人的信息|
|GroupBaseInfo|群组基础信息, 获取已加入群组列表接口的返回信息|
|GroupInfoCustomString|群资料自定义字段|
|GroupDetailInfo|群组详细信息|
|GetGroupInfoResult|获取群组信息列表接口的返回|
|GroupSearchParam|群搜索参数|
|GroupModifyInfoParam|设置群信息接口的参数|
|GroupAttributes|设置群属性的 map 对象|
|GroupCounter|群计数器信息|
|GroupGetOnlineMemberCountResult|获取指定群在线人数结果|

|名称|含义|
|---|---|
|TIMGroupTopicInfo|获取指定群话题信息结果|
|TIMGroupTopicOperationResult|话题操作结果|

版权所有:腾讯云计算(北京)有限责任公司 

第81 共117页 

即时通信 IM 

|TIMGroupTopicInfoResult|获取话题信息的结果|
|---|---|

|名称|含义|
|---|---|
|GroupMemberGetInfoOption|获取群组成员信息的选项|
|GroupGetMemberInfoListParam|获取群成员列表接口的参数|
|GroupGetMemberInfoListResult|获取群成员列表接口的返回|
|GroupMemberSearchParam|群成员搜索参数|
|GroupSearchGroupMembersResult|群成员搜索结果|
|GroupMemberInfoCustomString|群成员信息自定义字段|
|GroupModifyMemberInfoParam|设置群成员信息接口的参数|
|GroupInviteMemberParam|邀请成员接口的参数|
|GroupInviteMemberResult|邀请成员接口的返回|
|GroupDeleteMemberParam|删除成员接口的参数|
|GroupDeleteMemberResult|删除成员接口的返回|

|名称|含义|
|---|---|
|GroupPendencyOption|获取群未决信息列表的参数|
|GroupPendency|群未决信息定义|
|GroupPendencyResult|获取群未决信息列表的返回|
|GroupHandlePendencyParam|处理群未决消息接口的参数|

|名称|含义|
|---|---|
|TopicInfo|话题信息|
|TopicOperationResult|话题操作结果|

版权所有:腾讯云计算(北京)有限责任公司 

第82 共117页 

即时通信 IM 

|TopicInfoResult|获取话题信息的结果|
|---|---|
|PermissionGroupInfo|权限组信息|
|TopicPermissionMap|话题权限 map|
|PermissionGroupInfoResult|获取权限组信息的结果|
|PermissionGroupOperationResult|权限组操作结果|
|PermissionGroupMemberOperationResul t|权限组成员处理结果|
|PermissionGroupMemberInfoResult|获取权限组成员列表接口的返回|
|TopicPermissionResult|获取话题权限列表接口的返回|
|PermissionGroupCallback|权限组相关监听回调|

|名称|含义|
|---|---|
|FriendProfileCustomStringInfo|好友自定义资料字段|
|FriendProfile|好友资料|
|FriendProfileItem|好友资料可修改的各个项|
|FriendshipModifyFriendProfileParam|修改好友资料接口的参数|
|FriendProfileUpdate|好友资料更新信息|

|名称|含义|
|---|---|
|FriendshipAddFriendParam|添加好友接口的参数|
|FriendshipDeleteFriendParam|删除好友接口的参数|
|FriendAddPendency|好友申请未决信息|
|FriendshipGetPendencyListParam|分页获取好友申请未决信息列表的参数|
|PendencyPage|好友申请未决信息页|

版权所有:腾讯云计算(北京)有限责任公司 

第83 共117页 

即时通信 IM 

|FriendAddPendencyInfo|好友申请未决信息|
|---|---|
|FriendResponse|处理好友申请未决信息接口的参数|
|FriendshipDeletePendencyParam|删除好友申请未决信息接口的参数|

|名称|含义|
|---|---|
|FriendshipCheckFriendTypeParam|检测好友的类型接口的参数|
|FriendshipCheckFriendTypeResult|检测好友的类型接口返回|

|名称|含义|
|---|---|
|FriendResult|关系链操作接口的返回结果|

|名称|含义|
|---|---|
|CreateFriendGroupParam|创建好友分组接口参数|
|FriendGroupInfo|好友分组信息|
|FriendshipModifyFriendGroupParam|修改好友分组信息的接口参数|

|名称|含义|
|---|---|
|FriendSearchParam|搜索好友的参数|
|FriendInfoGetResult|搜索好友结果|

|名称|含义|
|---|---|
|OfficialAccountInfo|公众号信息|
|GetOfficialAccountInfoResult|获取公众号信息列表接口的返回|

版权所有:腾讯云计算(北京)有限责任公司 

第84 共117页 

即时通信 IM 

|名称|含义|
|---|---|
|FollowOperationResult|关注/取关操作接口的返回结果|
|FollowListResult|获取 关注/粉丝/互关 列表的结果|
|FollowInfo|用户关注信息|
|FollowTypeCheckResult|指定用户关注类型的检查结果|

|名称|含义|
|---|---|
|OfflinePushToken|设置离线推送配置信息|
|IOSOfflinePushConfigSoundConfig|iOS 离线推送声音设置选项|
|IOSOfflinePushConfig|消息在 iOS 系统上的离线推送配置|
|AndroidOfflinePushConfig|消息在 Android 系统上的离线推送配置|
|OfflinePushConfig|消息离线推送配置|

|名称|含义|
|---|---|
|SignalingInfo|信令基础信息定义|

点此进入 IM 社群 ,享有专业工程师的支持,解决您的难题。 

版权所有:腾讯云计算(北京)有限责任公司 

第85 共117页 

即时通信 IM 

# C++ 

最近更新时间:2025-02-25 15:32:12 

## 初始化并成功登录,是正常使用腾讯云 IM 服务的前提。 

|API|描述|
|---|---|
|InitSDK|初始化 SDK|
|UnInitSDK|反初始化 SDK|
|GetVersion|获取版本号|
|GetServerTime|获取服务器当前时间|
|Login|登录|
|Logout|登出|
|GetLoginStatus|获取登录状态|
|GetLoginUser|获取当前登录用户的 UserID|

## 如果您只需要使用文本和信令(即一段自定义 buffer)消息,可通过如下消息收发接口实现。 

|API|描述|
|---|---|
|AddSimpleMsgListener|设置基本消息(文本消息和自定义消息)的事件监听器, 请不要同 AddAdvancedMsgListener混用|
|RemoveSimpleMsgListener|移除基本消息(文本消息和自定义消息)的事件监听器|
|SendC2CTextMessage|发送单聊(C2C)普通文本消息|
|SendC2CCustomMessage|发送单聊(C2C)自定义(信令)消息|
|SendGroupTextMessage|发送群聊普通文本消息|
|SendGroupCustomMessag e|发送群聊自定义(信令)消息|

版权所有:腾讯云计算(北京)有限责任公司 

第86 共117页 

即时通信 IM 

|API|描述|
|---|---|
|AddSignalingListener|添加信令监听|
|RemoveSignalingListener|移除信令监听|
|Invite|邀请某个人|
|InviteInGroup|邀请群内的某些人|
|Cancel|邀请方取消邀请|
|Accept|接收方接收邀请|
|Reject|接收方拒绝邀请|
|GetSignalingInfo|获取信令信息|
|AddInvitedSignaling|添加邀请信令(可以用于群离线推送消息触发的邀请信令)|
|ModifyInvitation|修改邀请信令|

如果您需要收发图片、视频、文件等富媒体消息,并需要撤回消息、标记已读、查询历史消息等高级功能,推荐使用 下面这套高级消息接口(简单消息接口和高级消息接口请不要混用)。 

|API|描述|
|---|---|
|AddAdvancedMsgListener|设置高级消息的事件监听器, 请不要同AddSimpleMsgListener 混用|
|RemoveAdvancedMsgListe ner|移除高级消息的事件监听器|
|CreateTextMessage|创建文本消息|
|CreateTextAtMessage|创建 @ 文本消息|
|CreateCustomMessage|创建自定义消息|
|CreateCustomMessage|创建自定义消息(支持设置离线推送的信息)|
|CreateImageMessage|创建图片消息|
|CreateSoundMessage|创建语音消息|
|CreateVideoMessage|创建视频消息|

版权所有:腾讯云计算(北京)有限责任公司 

第87 共117页 

即时通信 IM 

|CreateFileMessage|创建文件消息|
|---|---|
|CreateLocationMessage|创建地理位置消息|
|CreateFaceMessage|创建表情消息|
|CreateMergerMessage|创建合并转发消息|
|CreateForwardMessage|创建单条转发消息|
|CreateTargetedGroupMess age|创建定向群消息|
|CreateAtSignedGroupMess age|创建带 @ 标记的群消息|
|SendMessage|发送消息,消息对象可以由 CreateXXXMessage 接口创建得来|
|SetC2CReceiveMessageOp t|设置单聊消息免打扰|
|GetC2CReceiveMessageOp t|获取单聊消息免打扰状态|
|SetGroupReceiveMessage Opt|设置群聊消息免打扰状态|
|SetAllReceiveMessageOpt|设置全局消息接收选项(支持设置每天的免打扰时间)|
|SetAllReceiveMessageOpt|设置全局消息接收选项|
|GetAllReceiveMessageOpt|获取登录用户全局消息接收选项|
|GetHistoryMessageList|获取历史消息高级接口|
|RevokeMessage|撤回消息,消息对象可以由 CreateXXXMessage 接口创建得来|
|ModifyMessage|修改消息,消息对象可以由 createXXXMessage 接口创建得来|
|MarkC2CMessageAsRead|设置单聊(C2C)消息已读(待废弃接口,请使用 CleanConversationUnreadMessageCount接口)|
|MarkGroupMessageAsRea d|设置群组消息已读(待废弃接口,请使用 CleanConversationUnreadMessageCount接口)|
|MarkAllMessageAsRead|标记所有会话为已读(待废弃接口,请使用 CleanConversationUnreadMessageCount接口)|

版权所有:腾讯云计算(北京)有限责任公司 

第88 共117页 

即时通信 IM 

|DeleteMessages|删除本地及云端的消息|
|---|---|
|ClearC2CHistoryMessage|清空单聊本地及云端的消息|
|ClearGroupHistoryMessage|清空群聊本地及云端的消息|
|InsertGroupMessageToLoc alStorage|向群组消息列表中添加一条消息|
|InsertC2CMessageToLocal Storage|向单聊消息列表中添加一条消息|
|FindMessages|根据 msgID 查找本地消息|
|SearchLocalMessages|搜索本地消息|
|SearchCloudMessages|搜索云端消息|
|SendMessageReadReceipt s|发送消息已读回执|
|GetMessageReadReceipts|获取消息已读回执|
|GetGroupMessageReadMe mberList|获取群消息已读群成员列表|
|SetMessageExtensions|设置消息扩展|
|GetMessageExtensions|获取消息扩展|
|DeleteMessageExtensions|删除消息扩展|
|AddMessageReaction|添加消息回应|
|RemoveMessageReaction|删除消息回应|
|GetMessageReactions|批量拉取多条消息回应信息|
|GetAllUserListOfMessageR eaction|分页拉取消息回应全量用户资料|
|pinGroupMessage|设置群消息置顶|
|getPinnedGroupMessageLi st 群组相关接口|获取已置顶的群消息列表|

版权所有:腾讯云计算(北京)有限责任公司 

第89 共117页 

即时通信 IM 

## 腾讯云 IM SDK 支持以下预设的群组类型,每种类型都有其适用场景: 

- 工作群(Work) :类似普通微信群,创建后不能自由加入,必须由已经在群的用户邀请入群。 

- 公开群(Public) :类似 QQ 群,用户申请加入,但需要群主或管理员审批。 

- 会议群(Meeting):适合跟 TRTC 结合实现视频会议和在线教育等场景,支持随意进出,支持查看进群前的 历史消息。 

- 社群(Community):社群成员上限 100000 人,任何人都可以自由进出,且加群无需被审批,适合用于知 识分享和游戏交流等超大社区群聊场景。5.8 版本开始支持,需 购买旗舰版或企业版套餐包 并在 控制台 >功能 配置  > 群组配置 > 群功能配置 > 社群 中开通。 

## 直播群(AVChatRoom):适合直播弹幕聊天室等场景,支持随意进出,人数无上限。 

|API|描述|
|---|---|
|AddGroupListener|添加群组相关的事件监听器|
|RemoveGroupListener|移除群组相关的事件监听器|
|CreateGroup|创建群组(简单版本)|
|CreateGroup|创建群组(高级版本),可在建群同时设置群信息和初始的群成员|
|JoinGroup|加入群组|
|QuitGroup|退出群组|
|DismissGroup|解散群组(仅群主和管理员可以解散)|
|GetJoinedGroupList|获取已经加入的群列表(不包括已加入的直播群)|
|GetGroupsInfo|拉取群资料|
|SearchGroups|搜索本地群资料|
|SearchCloudGroups|搜索云端群资料|
|SetGroupInfo|修改群资料|
|InitGroupAttributes|初始化群属性|
|SetGroupAttributes|设置群属性|
|DeleteGroupAttributes|删除群属性|
|GetGroupAttributes|获取群属性|
|GetGroupOnlineMemberCo unt|获取群在线人数|

版权所有:腾讯云计算(北京)有限责任公司 

第90 共117页 

即时通信 IM 

|GetGroupMemberList|获取群成员列表|
|---|---|
|GetGroupMembersInfo|获取指定的群成员资料|
|SearchGroupMembers|搜索本地群成员资料|
|SearchCloudGroupMember s|搜索云端群成员资料|
|SetGroupMemberInfo|修改指定的群成员资料|
|MuteGroupMember|禁言|
|MuteAllGroupMembers|禁言全体群成员,只有管理员或群主能够调用|
|KickGroupMember|踢人|
|KickGroupMember|踢人(支持设置禁止加群时长)|
|SetGroupMemberRole|切换群成员的角色|
|MarkGroupMemberList|标记群成员|
|TransferGroupOwner|转让群主|
|InviteUserToGroup|邀请他人入群|
|GetGroupApplicationList|获取加群的申请列表|
|AcceptGroupApplication|同意某一条加群申请|
|RefuseGroupApplication|拒绝某一条加群申请|
|SetGroupApplicationRead|标记申请列表为已读|
|GetJoinedCommunityList|获取当前用户已经加入的支持话题的社群列表|
|CreateTopicInCommunity|创建话题|
|DeleteTopicFromCommunit y|删除话题|
|SetTopicInfo|修改话题信息|
|GetTopicInfoList|获取话题列表|
|SetGroupCounters|设置群计数器|
|GetGroupCounters|获取群计数器|

版权所有:腾讯云计算(北京)有限责任公司 

第91 共117页 

即时通信 IM 

|IncreaseGroupCounter|递增群计数器|
|---|---|
|DecreaseGroupCounter|递减群计数器|

## 社群用来管理群成员。社群下的所有话题不仅可以共享社群成员,还可以独立收发消息而不相互干扰。 

|API|描述|
|---|---|
|AddCommunityListener|添加社群监听器|
|RemoveCommunityListener|移除社群监听器|
|CreateCommunity|创建支持话题的社群|
|GetJoinedCommunityList|获取当前用户已经加入的支持话题的社群列表|
|CreateTopicInCommunity|创建话题|
|DeleteTopicFromCommunit y|删除话题|
|SetTopicInfo|修改话题信息|
|GetTopicInfoList|获取话题列表|
|CreatePermissionGroupInC ommunity|创建社群权限组|
|DeletePermissionGroupFro mCommunity|删除社群权限组|
|ModifyPermissionGroupInfo InCommunity|修改社群权限组|
|GetJoinedPermissionGroup ListInCommunity|获取已加入的社群权限组列表|
|GetPermissionGroupListInC ommunity|获取社群权限组列表|
|AddCommunityMembersTo PermissionGroup|向社群权限组添加成员|
|RemoveCommunityMember sFromPermissionGroup|从社群权限组删除成员|

版权所有:腾讯云计算(北京)有限责任公司 

第92 共117页 

即时通信 IM 

|GetCommunityMemberListI nPermissionGroup|获取社群权限组成员列表|
|---|---|
|AddTopicPermissionToPer missionGroup|向权限组添加话题权限|
|DeleteTopicPermissionFro mPermissionGroup|从权限组中删除话题权限|
|ModifyTopicPermissionInPe rmissionGroup|修改权限组中的话题权限|
|GetTopicPermissionInPermi ssionGroup|获取权限组中的话题权限|

会话列表,即登录微信或 QQ 后首屏看到的列表,包含会话节点、会话名称、群名称、最后一条消息以及未读消息 数等元素。 

|API|描述|
|---|---|
|AddConversationListener|添加会话监听器|
|RemoveConversationListen er|移除会话监听器|
|GetConversationList|获取会话列表|
|GetConversation|获取指定单个会话|
|GetConversationList|获取指定多个会话|
|GetConversationListByFilte r|获取会话高级接口,可以指定会话类型、标记类型、分组名等|
|DeleteConversation|删除会话|
|DeleteConversationList|删除会话列表|
|SetConversationDraft|设置会话草稿|
|SetConversationCustomDat a|设置会话自定义数据|
|PinConversation|置顶会话|

版权所有:腾讯云计算(北京)有限责任公司 

第93 共117页 

即时通信 IM 

|MarkConversation|标记会话|
|---|---|
|GetTotalUnreadMessageCo unt|获取会话总未读数|
|CleanConversationUnread MessageCount|清理会话的未读消息计数|
|CreateConversationGroup|创建会话分组|
|GetConversationGroupList|获取会话分组列表|
|DeleteConversationGroup|删除会话分组|
|RenameConversationGrou p|重命名会话分组|
|AddConversationsToGroup|添加会话到一个会话分组|
|DeleteConversationsFromG roup|从一个会话分组中删除会话|
|GetUnreadMessageCountB yFilter|获取按会话 filter 过滤的未读总数|
|SubscribeUnreadMessageC ountByFilter|注册监听指定 filter 的会话未读总数变化|
|UnsubscribeUnreadMessag eCountByFilter|取消监听指定 filter 的会话未读总数变化|

## 包含查询用户资料、修改个人资料以及屏蔽某人消息(即把某用户加入黑名单中)的相关接口。 

|API|描述|
|---|---|
|GetUsersInfo|获取用户资料|
|SetSelfInfo|修改个人资料|
|SubscribeUserInfo|订阅用户资料|
|UnsubscribeUserInfo|取消订阅用户资料|
|GetUserStatus|查询用户状态|
|SetSelfStatus|设置自己的状态|

版权所有:腾讯云计算(北京)有限责任公司 

第94 共117页 

即时通信 IM 

|SubscribeUserStatus|订阅用户状态|
|---|---|
|UnsubscribeUserStatus|取消订阅用户状态|
|SearchUsers|搜索云端用户资料|
|AddToBlackList|屏蔽某人的消息(添加该用户到黑名单中)|
|DeleteFromBlackList|取消某人的消息屏蔽(把该用户从黑名单中移除)|
|GetBlackList|获取黑名单列表|

腾讯云 IM 在收发消息时默认不检查是不是好友关系,您可以在 控制台 >功能配置>登录与消息>好友关系检查中开 启"发送单聊消息检查关系链"开关,并使用如下接口增删好友和管理好友列表。 

|API|描述|
|---|---|
|AddFriendListener|添加关系链监听器|
|RemoveFriendListener|移除关系链监听器|
|GetFriendList|获取好友列表|
|GetFriendsInfo|获取指定好友资料|
|SetFriendInfo|设置指定好友资料|
|SearchFriends|搜索好友列表|
|AddFriend|添加好友|
|DeleteFromFriendList|删除好友|
|CheckFriend|检查指定用户的好友关系|
|GetFriendApplicationList|获取好友申请列表|
|AcceptFriendApplication|同意好友申请|
|RefuseFriendApplication|拒绝好友申请|
|DeleteFriendApplication|删除好友申请|
|SetFriendApplicationRead|设置好友申请已读|
|CreateFriendGroup|新建好友分组|

版权所有:腾讯云计算(北京)有限责任公司 

第95 共117页 

即时通信 IM 

|GetFriendGroups|获取分组信息|
|---|---|
|DeleteFriendGroup|删除好友分组|
|RenameFriendGroup|修改好友分组的名称|
|AddFriendsToFriendGroup|添加好友到一个好友分组|
|DeleteFriendsFromFriendGr oup|从好友分组中删除好友|

## 公众号可以为订阅的用户发送广播消息,也可以与订阅的用户进行单聊。 

|API|描述|
|---|---|
|SubscribeOfficialAccount|订阅公众号|
|UnsubscribeOfficialAccoun t|取消订阅公众号|
|GetOfficialAccountsInfo|获取公众号列表|

## 关注和粉丝功能可以帮助建立和维护用户之间相对简单的连接关系,方便促进用户之间的互动和交流。 

|API|描述|
|---|---|
|FollowUser|关注用户|
|UnfollowUser|取消关注用户|
|GetMyFollowingList|获取我的关注列表|
|GetMyFollowersList|获取我的粉丝列表|
|GetMutualFollowersList|获取我的互关列表|
|GetUserFollowInfo|获取指定用户的 关注/粉丝/互关 数量信息|
|CheckFollowType|检查指定用户的关注类型|

点此进入 IM 社群 ,享有专业工程师的支持,解决您的难题。 

版权所有:腾讯云计算(北京)有限责任公司 

第96 共117页 

即时通信 IM 

# React Native 

最近更新时间:2024-12-26 11:05:13 

TencentCloudChat 是 IM React Native SDK 的命名空间,提供了创建 SDK 实例的静态方法 create() , 以及事件常量 EVENT ,类型常量 TYPES , 信令常量 TSignaling 。 

|API|描述|
|---|---|
|create|创建 SDK 实例。|
|SDK 实例 基本概念|说明|
|Message(消息)|IM SDK 中Message表示要发送给对方的内容,消息包括若干属性,例 如自己是否为发送者,发送人账号以及消息产生时间等。|
|Conversation(会话)|IM SDK 中Conversation分为两种: C2C(Client to Client)会话,表示单聊情况,自己与对方建立的对 话。 GROUP(群)会话,表示群聊情况下群内成员组成的会话。|
|Profile(资料)|IM SDK 中Profile描述个人的常用基本信息,例如昵称、性别、个性签 名以及头像地址等。|
|Friend(好友)|IM SDK 中Friend描述好友的常用基本信息,例如备注、分组等。|
|FriendApplication(好友 申请)|IM SDK 中FriendApplication描述好友申请的常用基本信息,例如加 好友来源、备注等。|
|FriendGroup(好友分组)|IM SDK 中FriendGroup描述好友分组的常用基本信息,例如分组名、 分组成员等。|
|Group(群组)|IM SDK 中Group表示一个支持多人聊天的通信系统,支持好友工作 群、陌生人社交群、临时会议群以及直播群。|
|GroupMember(群成员)|IM SDK 中GroupMember描述群内成员的常用基本信息,例如 ID、 昵称、群内身份以及入群时间等。|
|Signaling(信令)|IM SDK 中Signaling描述信令的常用基本信息。例如 ID、邀请者 ID、|

版权所有:腾讯云计算(北京)有限责任公司 

第97 共117页 

即时通信 IM 

||被邀请人 ID 列表,操作类型、超时时间等。|
|---|---|
|群提示消息|当有用户被邀请加入群组或被移出群组等事件发生时,群内会产生提示消 息,接入侧可以根据实际需求展示给群组用户或忽略。 群提示消息有多种类型,详细描述请参见 Message.GroupTipPayload。|
|群系统通知消息|当有用户申请加群等事件发生时,管理员会收到申请加群等系统消息。管理 员同意或拒绝加群申请,IM SDK 会通过群系统通知消息将申请加群等相 应消息发送给接入侧,由接入侧展示给用户。 群系统通知消息有多种类型,详细描述请参见 Message.GroupSystemNoticePayload。|
|消息上屏|用户单击发送后,事先输入的文字或选择的图片等信息显示在用户电脑屏幕 或手机屏幕上的过程。|

|API|描述|
|---|---|
|on|监听事件。|
|off|取消监听事件。|

|API|描述|
|---|---|
|registerPlugin|注册插件。|

|API|描述|
|---|---|
|setLogLevel|设置日志级别。|

|API|描述|
|---|---|
|isReady|SDK 是否 ready。SDK ready 后,开发者可调用 SDK 发送消息等 API,使用 SDK 的各项功能。|

版权所有:腾讯云计算(北京)有限责任公司 

第98 共117页 

即时通信 IM 

|API|描述|
|---|---|
|destroy|销毁 SDK 实例。|

|API|描述|
|---|---|
|login|登录。|
|logout|登出。|
|getLoginUser|已登录返回登录用户的 userID,未登录返回 '' 。|

|API|描述|
|---|---|
|createTextMessage|创建文本消息。|
|createTextAtMessage|创建可以附带 @ 提醒功能的文本消息。|
|createImageMessage|创建图片消息。|
|createAudioMessage|创建音频消息。|
|createVideoMessage|创建视频消息。|
|createCustomMessage|创建自定义消息。|
|createFaceMessage|创建表情消息。|
|createFileMessage|创建文件消息。|
|createLocationMessag e|创建地理位置消息。|
|createMergerMessage|创建合并消息。|
|downloadMergerMessa ge|下载合并消息。|
|createForwardMessag e|创建转发消息。|
|sendMessage|发送消息。|

版权所有:腾讯云计算(北京)有限责任公司 

第99 共117页 

即时通信 IM 

|searchCloudMessages|搜索云端消息。|
|---|---|
|revokeMessage|撤回消息。|
|resendMessage|重发消息。|
|deleteMessage|删除消息。|
|translateText|翻译文本消息。|
|convertVoiceToText|语音转文字。|
|setMessageExtensions|设置消息扩展。|
|getMessageExtensions|获取消息扩展。|
|deleteMessageExtensi ons|删除消息扩展。|
|addMessageReaction|添加消息回应。|
|removeMessageReacti on|删除消息回应。|
|getMessageReactions|批量拉取多条消息回应信息。|
|getAllUserListOfMessa geReaction|分页拉取指定消息回应的用户列表。|

|API|描述|
|---|---|
|modifyMessage|变更消息。|
|getMessageList|获取消息列表。|
|getMessageListHoppin g|根据指定的消息 sequence 或 消息时间拉取会话的消息列表。|
|sendMessageReadRec eipt|发送消息已读回执。|
|getMessageReadRecei ptList|拉取已读回执列表。|
|getGroupMessageRead MemberList|获取群消息已读(或未读)群成员列表。|

版权所有:腾讯云计算(北京)有限责任公司 

第100 共117页 

即时通信 IM 

|findMessage|根据 messageID 查询会话的本地消息。|
|---|---|
|setMessageRead|将某会话下的未读消息状态设置为已读,置为已读的消息不会计入到未读统 计。|
|getConversationList|获取会话列表。|
|getConversationProfile|获取会话资料。|
|deleteConversation|删除会话。|
|clearHistoryMessage|清空单聊或群聊本地及云端的消息(不删除会话)。|
|pinConversation|置顶或取消置顶会话。|
|setAllMessageRead|将所有会话的未读消息设置为已读。|
|setMessageRemindTyp e|设置会话消息提醒类型,您可以使用此接口实现“消息免打扰”,“拒收消 息”的功能。|
|getTotalUnreadMessag eCount|获取会话未读总数。|

|API|描述|
|---|---|
|setConversationCusto mData|设置会话自定义数据。|
|markConversation|标记会话。|
|getConversationGroup List|获取会话分组列表。|
|createConversationGro up|创建会话分组。|
|deleteConversationGro up|删除会话分组。|
|renameConversationGr oup|重命名会话分组。|
|addConversationsToGr oup|添加会话到一个会话分组。|

版权所有:腾讯云计算(北京)有限责任公司 

第101 共117页 

即时通信 IM 

|deleteConversationsFr omGroup 从一个会话分组中删除会话。|
|---|

|API|描述|
|---|---|
|searchCloudMessages|搜索云端消息。|
|searchCloudUsers|搜索云端用户。|
|searchCloudGroups|搜索云端群列表。|
|searchCloudGroupMe mbers|搜索云端群成员列表。|

|API|描述|
|---|---|
|getMyProfile|获取个人资料。|
|getUserProfile|获取其他用户资料。|
|updateMyProfile|更新个人资料。|
|getBlacklist|获取我的黑名单列表。|
|addToBlacklist|添加用户到黑名单列表。|
|removeFromBlacklist|将用户从黑名单中移除。|

|API|描述|
|---|---|
|setSelfStatus|设置自己的自定义状态。|
|getUserStatus|查询用户状态。|
|subscribeUserStatus|订阅用户状态。|
|unsubscribeUserStatu s|取消订阅用户状态。|

版权所有:腾讯云计算(北京)有限责任公司 

第102 共117页 

即时通信 IM 

|API|描述|
|---|---|
|getFriendList|获取 SDK 缓存的好友列表。|
|addFriend|添加好友。|
|deleteFriend|删除好友。|
|checkFriend|校验好友关系。|
|getFriendProfile|获取指定好友的好友数据和资料数据。|
|updateFriend|更新好友的关系链数据。|
|getFriendApplicationLis t|获取 SDK 缓存的好友申请列表。|
|acceptFriendApplicatio n|同意好友申请。|
|refuseFriendApplicatio n|拒绝好友申请。|
|deleteFriendApplicatio n|删除好友申请。|
|setFriendApplicationRe ad|上报好友申请已读。|
|getFriendGroupList|获取 SDK 缓存的好友分组列表。|
|createFriendGroup|创建好友分组。|
|deleteFriendGroup|删除好友分组。|
|addToFriendGroup|添加好友到分组列表。|
|removeFromFriendGro up|从好友分组移除好友。|
|renameFriendGroup 关注和粉丝|修改好友分组的名称。|

|API|描述|
|---|---|
|followUser|关注用户。|

版权所有:腾讯云计算(北京)有限责任公司 

第103 共117页 

即时通信 IM 

|unfollowUser|取消关注。|
|---|---|
|getMyFollowersList|获取我的粉丝列表。|
|getMyFollowingList|获取我的关注列表。|
|getMutualFollowersList|获取互关列表。|
|getUserFollowInfo|获取指定用户的 关注/粉丝/互关 数量信息。|
|checkFollowType|检查指定用户的关注关系。|

|API|描述|
|---|---|
|getGroupList|获取群组列表。|
|getGroupProfile|获取群详细资料。|
|createGroup|创建群组。|
|dismissGroup|解散群组。|
|updateGroupProfile|修改群组资料。|
|joinGroup|申请加群。|
|quitGroup|退出群组。|
|searchGroupByID|搜索群组。|
|getGroupOnlineMembe rCount|获取群在线人数。|
|changeGroupOwner|转让群组。|
|getGroupApplicationLis t|获取加群申请列表。|
|handleGroupApplicatio n|处理申请加群。|
|initGroupAttributes|初始化群属性。|
|setGroupAttributes|设置群属性。|
|deleteGroupAttributes|删除群属性。|

版权所有:腾讯云计算(北京)有限责任公司 

第104 共117页 

即时通信 IM 

|getGroupAttributes|获取群属性。|
|---|---|
|setGroupCounters|设置群计数器。|
|increaseGroupCounter|递增群计数器。|
|decreaseGroupCounte r|递减群计数器。|
|getGroupCounters|获取群计数器。|

|API|描述|
|---|---|
|getGroupMemberList|获取群成员列表。|
|getGroupMemberProfil e|获取群成员资料。|
|addGroupMember|添加群成员。|
|deleteGroupMember|删除群成员。|
|setGroupMemberMute Time|设置群成员的禁言时间。|
|setGroupMemberRole|修改群成员角色。|
|setGroupMemberName Card|设置群成员名片。|
|setGroupMemberCusto mField|设置群成员自定义字段。|
|markGroupMemberList|标记群成员。|

|API|描述|
|---|---|
|getJoinedCommunityLi st|获取当前用户已经加入的支持话题的社群列表。|
|createTopicInCommuni ty|创建话题。|

版权所有:腾讯云计算(北京)有限责任公司 

第105 共117页 

即时通信 IM 

|deleteTopicFromComm unity|删除话题。|
|---|---|
|updateTopicProfile|更新话题资料。|
|getTopicList 信令|获取话题列表。|
|API|描述|
|addSignalingListener|监听信令事件。|
|removeSignalingListen er|移除监听信令事件。|
|invite|邀请某个人。|
|inviteInGroup|邀请群内的某些人。|
|cancel|邀请发起者取消邀请。|
|accept|被邀请人接受邀请。|
|reject|被邀请人拒绝邀请。|
|getSignalingInfo|获取信令信息。|
|modifyInvitation|修改邀请信令。|

版权所有:腾讯云计算(北京)有限责任公司 

第106 共117页 

即时通信 IM 

# HarmonyOS 

最近更新时间:2025-02-25 15:32:12 

## 初始化并成功登录,是正常使用腾讯云 IM 服务的前提。 

|API|描述|
|---|---|
|initSDK|初始化 SDK。|
|unInitSDK|反初始化 SDK。|
|addIMSDKListener|添加 IM 监听。|
|removeIMSDKListener|移除 IM 监听。|
|getVersion|获取版本号。|
|getServerTime|获取服务器当前时间。|
|login|登录。|
|logout|登出。|
|getLoginStatus|获取登录状态。|
|getLoginUser|获取当前登录用户的 UserID。|

## 如果您只需要使用文本和信令(即一段自定义buffer)消息,只需要使用这套简单消息收发接口即可。 

|API|描述|
|---|---|
|addSimpleMsgListener|设置基本消息(文本消息和自定义消息)的事件监听器,请不要同 addAdvancedMsgListener混用。|
|removeSimpleMsgList ener|移除基本消息(文本消息和自定义消息)的事件监听器。|
|sendC2CTextMessage|发送单聊(C2C)普通文本消息。|
|sendC2CCustomMess age|发送单聊(C2C)自定义(信令)消息。|

版权所有:腾讯云计算(北京)有限责任公司 

第107 共117页 

即时通信 IM 

|sendGroupTextMessag e|发送群聊普通文本消息。|
|---|---|
|sendGroupCustomMes sage|发送群聊自定义(信令)消息。|

如果您需要收发图片、视频、文件等富媒体消息,并需要撤回消息、标记已读、查询历史消息等高级功能,推荐使用 下面这套高级消息接口(简单消息接口和高级消息接口请不要混用)。 

|API|描述|
|---|---|
|addAdvancedMsgListe ner|设置高级消息的事件监听器,请不要同addSimpleMsgListener混 用。|
|removeAdvancedMsgL istener|移除高级消息的事件监听器。|
|createTextMessage|创建文本消息。|
|createCustomMessag e|创建自定义消息。|
|createImageMessage|创建图片消息。|
|createSoundMessage|创建语音消息。|
|createVideoMessage|创建视频消息。|
|createFileMessage|创建文件消息。|
|createLocationMessag e|创建地理位置消息。|
|createFaceMessage|创建表情消息。|
|createMergerMessage|创建合并转发消息。|
|createForwardMessag e|创建单条转发消息。|
|createTargetedGroup Message|创建定向群消息。|
|createAtSignedGroup Message|创建带 @ 标记的群消息。|

版权所有:腾讯云计算(北京)有限责任公司 

第108 共117页 

即时通信 IM 

|sendMessage|发送消息,消息对象可以由 createXXXMessage 接口创建得来。|
|---|---|
|setC2CReceiveMessag eOpt|设置单聊消息免打扰。|
|getC2CReceiveMessag eOpt|获取单聊消息免打扰状态。|
|setGroupReceiveMess ageOpt|设置群聊消息免打扰状态。|
|setAllReceiveMessage Opt|设置全局消息接收选项。|
|setAllReceiveMessage Opt2|设置全局消息接收选项。|
|getAllReceiveMessage Opt|获取登录用户全局消息接收选项。|
|getHistoryMessageList|获取历史消息高级接口。|
|revokeMessage|撤回消息,消息对象可以由 createXXXMessage 接口创建得来。|
|modifyMessage|消息变更。|
|deleteMessages|删除本地及云端的消息。|
|clearC2CHistoryMessa ge|清空单聊本地及云端的消息。|
|clearGroupHistoryMes sage|清空群聊本地及云端的消息。|
|insertGroupMessageT oLocalStorage|向群组消息列表中添加一条消息。|
|insertC2CMessageToL ocalStorage|向单聊消息列表中添加一条消息。|
|findMessages|根据 msgID 查找本地消息。|
|searchLocalMessages|搜索本地消息。|
|searchCloudMessages|搜索云端消息。|
|sendMessageReadRec eipts|发送消息已读回执。|

版权所有:腾讯云计算(北京)有限责任公司 

第109 共117页 

即时通信 IM 

|getMessageReadRecei pts|获取消息已读回执。|
|---|---|
|getGroupMessageRea dMemberList|获取群消息已读群成员列表。|
|setMessageExtension s|设置消息扩展。|
|getMessageExtension s|获取消息扩展。|
|deleteMessageExtensi ons|删除消息扩展。|
|addMessageReaction|添加消息回应。|
|removeMessageReacti on|删除消息回应。|
|getMessageReactions|批量拉取多条消息回应信息。|
|getMessageReactionU serList|分页拉取消息回应全部用户资料。|
|translateText|翻译文本消息。|
|pinGroupMessage|设置群消息置顶。|
|getPinnedGroupMessa geList|获取已置顶的群消息列表。|

## 腾讯云 IM SDK 支持五种预设的群组类型,每种类型都有其适用场景: 

- 工作群(Work):类似普通微信群,创建后不能自由加入,必须由已经在群的用户邀请入群,同旧版本中的 Private。 

- 公开群(Public):类似 QQ 群,用户申请加入,但需要群主或管理员审批。 

- 会议群(Meeting):适合跟 TRTC 结合实现视频会议和在线教育等场景,支持随意进出,支持查看进群前的 历史消息,同旧版本中的 ChatRoom。 

- 社群(Community):创建后可以随意进出,适合用于知识分享和游戏交流等超大社区群聊场景。该功能支持 

- 终端 SDK 5.8.1668增强版及以上版本、Web SDK 2.17.0及以上版本,需 购买旗舰版或企业版套餐包 并在 控制台 > 功能配置 > 群组配置 > 群功能配置 > 社群中开通。 

直播群(AVChatRoom):适合直播弹幕聊天室等场景,支持随意进出,人数无上限。 

版权所有:腾讯云计算(北京)有限责任公司 

第110 共117页 

即时通信 IM 

|API|描述|
|---|---|
|addGroupListener|添加群组监听器。|
|removeGroupListener|移除群组监听器。|
|createGroup|创建群组(简单版本)。|
|createGroup|创建群组(高级版本),可在建群同时设置群信息和初始的群成员。|
|joinGroup|加入群组。|
|quitGroup|退出群组。|
|dismissGroup|解散群组(仅群主和管理员可以解散)。|
|getJoinedGroupList|获取已经加入的群列表(不包括已加入的直播群)。|
|getGroupsInfo|拉取群资料。|
|searchGroups|搜索群列表。|
|setGroupInfo|修改群资料。|
|initGroupAttributes|初始化群属性。|
|setGroupAttributes|设置群属性。|
|deleteGroupAttributes|删除群属性。|
|getGroupAttributes|获取群属性。|
|getGroupOnlineMembe rCount|获取群在线人数。|
|setGroupCounters|设置群计数器。|
|getGroupCounters|获取群计数器。|
|increaseGroupCounter|递增群计数器。|
|decreaseGroupCounte r|递减群计数器。|
|getGroupMemberList|获取群成员列表。|
|getGroupMembersInfo|获取指定的群成员资料。|
|searchGroupMembers|搜索群成员。|

版权所有:腾讯云计算(北京)有限责任公司 

第111 共117页 

即时通信 IM 

|setGroupMemberInfo|修改指定的群成员资料。|
|---|---|
|muteGroupMember|禁言。|
|muteAllGroupMembers|禁言全体群成员。|
|inviteUserToGroup|邀请他人入群。|
|kickGroupMember|踢人。|
|setGroupMemberRole|切换群成员的角色。|
|markGroupMemberLis t|标记群成员。|
|transferGroupOwner|转让群主。|
|getGroupApplicationLi st|获取加群的申请列表。|
|acceptGroupApplicatio n|同意某一条加群申请。|
|refuseGroupApplicatio n|拒绝某一条加群申请。|
|setGroupApplicationRe ad|标记申请列表为已读。|

会话列表,即登录微信或 QQ 后首屏看到的列表,包含会话节点、会话名称、群名称、最后一条消息以及未读消息 数等元素。 

|API|描述|
|---|---|
|addConversationListener|添加会话监听器。|
|removeConversationListener|移除会话监听器。|
|getConversations|获取会话列表。|
|getConversationListByFilter|获取会话高级接口,可以指定会话类型、标记类型、分组名等。|
|getConversation|获取指定单个会话。|
|deleteConversation|删除会话。|

版权所有:腾讯云计算(北京)有限责任公司 

第112 共117页 

即时通信 IM 

|deleteConversationList|删除会话列表。|
|---|---|
|setConversationDraft|设置会话草稿。|
|setConversationCustomData|设置会话自定义数据。|
|pinConversation|置顶会话。|
|markConversation|标记会话。|
|getTotalUnreadMessageCount|获取会话总未读数。|
|getUnreadMessageCountByFilte r|获取按会话 filter 过滤的未读总数。|
|subscribeUnreadMessageCount ByFilter|注册监听指定 filter 的会话未读总数变化。|
|unsubscribeUnreadMessageCo untByFilter|取消监听指定 filter 的会话未读总数变化。|
|cleanConversationUnreadMessa geCount|清理会话的未读消息计数。|
|createConversationGroup|创建会话分组。|
|getConversationGroupList|获取会话分组列表。|
|deleteConversationGroup|删除会话分组。|
|renameConversationGroup|重命名会话分组。|
|addConversationsToGroup|添加会话到一个会话分组。|
|deleteConversationsFromGroup|从一个会话分组中删除会话。|

## 包含查询用户资料、修改个人资料以及屏蔽某人消息(即把某用户加入黑名单中)的相关接口。 

|API|描述|
|---|---|
|getUsersInfo|获取用户资料。|
|setSelfInfo|修改个人资料。|
|subscribeUserInfo|订阅用户资料。|

版权所有:腾讯云计算(北京)有限责任公司 

第113 共117页 

即时通信 IM 

|unsubscribeUserInfo|取消订阅用户资料。|
|---|---|
|getUserStatus|查询用户状态。|
|setSelfStatus|设置自己的状态。|
|subscribeUserStatus|订阅用户状态。|
|unsubscribeUserStatu s|取消订阅用户状态。|
|addToBlackList|屏蔽某人的消息(添加该用户到黑名单中)。|
|deleteFromBlackList|取消某人的消息屏蔽(把该用户从黑名单中移除)。|
|getBlackList|获取黑名单列表。|

腾讯云 IM 在收发消息时默认不检查是不是好友关系,您可以在 控制台 >功能配置>登录与消息>好友关系检查中开 启"发送单聊消息检查关系链"开关,并使用如下接口增删好友和管理好友列表。 

|API|描述|
|---|---|
|addFriendListener|添加关系链监听器。|
|removeFriendListener|移除关系链监听器。|
|getFriendList|获取好友列表。|
|getFriendsInfo|获取指定好友资料。|
|setFriendInfo|设置指定好友资料。|
|searchFriends|搜索好友列表。|
|addFriend|添加好友。|
|deleteFromFriendList|删除好友。|
|checkFriend|检查指定用户的好友关系。|
|getFriendApplicationLi st|获取好友申请列表。|
|acceptFriendApplicatio n|同意好友申请。|

版权所有:腾讯云计算(北京)有限责任公司 

第114 共117页 

即时通信 IM 

|refuseFriendApplicatio n|拒绝好友申请。|
|---|---|
|deleteFriendApplicatio n|删除好友申请。|
|setFriendApplicationRe ad|设置好友申请已读。|
|createFriendGroup|新建好友分组。|
|getFriendGroups|获取分组信息。|
|deleteFriendGroup|删除好友分组。|
|renameFriendGroup|修改好友分组的名称。|
|addFriendsToFriendGr oup|添加好友到一个好友分组。|
|deleteFriendsFromFrie ndGroup|从好友分组中删除好友。|
|subscribeOfficialAccou nt|订阅公众号。|
|unsubscribeOfficialAcc ount|取消订阅公众号。|
|getOfficialAccountsInf o|获取公众号列表。|
|followUser|关注用户。|
|unfollowUser|取消关注用户。|
|getMyFollowingList|获取我的关注列表。|
|getMyFollowersList|获取我的粉丝列表。|
|getMutualFollowersLis t|获取我的互关列表。|
|getUserFollowInfo|获取指定用户的 关注/粉丝/互关 数量信息。|
|checkFollowType 信令相关接口|检查指定用户的关注类型。|

版权所有:腾讯云计算(北京)有限责任公司 

第115 共117页 

即时通信 IM 

|API|描述|
|---|---|
|addSignalingListener|添加信令监听。|
|removeSignalingListen er|移除信令监听。|
|invite|邀请某个人。|
|inviteInGroup|邀请群内的某些人。|
|cancel|邀请方取消邀请。|
|accept|接收方接收邀请。|
|reject|接收方拒绝邀请。|
|getSignalingInfo|获取信令信息。|
|modifyInvitation|修改邀请信令。|

|API|描述|
|---|---|
|addCommunityListener|添加社群监听器。|
|removeCommunityListener|移除社群监听器。|
|createCommunity|创建支持话题的社群。|
|getJoinedCommunityList|获取当前用户已经加入的支持话题的社群列表。|
|createTopicInCommunity|创建话题。|
|deleteTopicFromCommunity|删除话题。|
|setTopicInfo|修改话题信息。|
|getTopicInfoList|获取话题列表。|
|createPermissionGroupInComm unity|创建社群权限组。|
|deletePermissionGroupFromCo mmunity|删除社群权限组|

版权所有:腾讯云计算(北京)有限责任公司 

第116 共117页 

即时通信 IM 

|modifyPermissionGroupInfoInCo mmunity|修改社群权限组。|
|---|---|
|getJoinedPermissionGroupListIn Community|获取已加入的社群权限组列表。|
|getPermissionGroupListInComm unity|获取社群权限组列表。|
|addCommunityMembersToPerm issionGroup|向社群权限组添加成员。|
|removeCommunityMembersFro mPermissionGroup|从社群权限组删除成员。|
|getCommunityMemberListInPer missionGroup|获取社群权限组成员列表。|
|addTopicPermissionToPermissi onGroup|向权限组添加话题权限。|
|deleteTopicPermissionFromPer missionGroup|从权限组中删除话题权限。|
|modifyTopicPermissionInPermis sionGroup|修改权限组中的话题权限。|
|getTopicPermissionInPermissio nGroup|获取权限组中的话题权限。|

点此进入 IM 社群 ,享有专业工程师的支持,解决您的难题。 

下载 IM SDK(HarmonyOS) 集成 IM SDK(HarmonyOS) 

运行 IM Demo(HarmonyOS) 

版权所有:腾讯云计算(北京)有限责任公司 

第117 共117页
