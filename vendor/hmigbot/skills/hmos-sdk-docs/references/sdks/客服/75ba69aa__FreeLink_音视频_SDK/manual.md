# FreeLink 音视频 SDK 使用指南 

版本: V1.0.0 

公司:易谷网络科技股份有限公司 

产品概述 

FreeLink 音视频 SDK 是易谷网络自主研发,兼容华为鸿蒙 ( HarmonyOS )系统的实时通信开发工具包,基于 WebRTC 标准协 议构建,属于轻量级、高适配性通信中间件,可快速为鸿蒙原生应用 提供稳定的音视频通话与协作能力。 

核心功能: 

语音通话、视频通话 

音视频无缝切换 

合规双录(录音录像) 

同屏协作 

跨渠道互联互通( App 、 Web 、小程序、短信链接) 

后台通话保活 

产品特点: 

鸿蒙原生适配,集成简单 

支持大规模并发,运行稳定 

权限最小化,符合隐私合规要求 

已在金融、政务等企业级项目落地使用 

二、安装与设置步骤 

1. 安装 SDK 执行命令: 

ohpm install @egoo/freelink 

# 2. 权限配置(必须配置) 

ohos.permission.INTERNET :网络访问 

ohos.permission.CAMERA :摄像头使用 

ohos.permission.MICROPHONE :麦克风使用 

ohos.permission.KEEP_BACKGROUND_RUNNING :后台保活 

# 3. 初始化规范 

必须先获取用户授权同意,再初始化 SDK ,禁止未授权调用摄像头、 麦克风。 

# 引入组件 

import {GlobalManager, User, VideoUrl} from 'freelink' 

# 5. 设置地址信息 

let videoUrl: VideoUrl = new VideoUrl (); 

videoUrl.setVideoPageUrl("https://webrtc.myegoo.com.cn/ PSBC_h5/index.html"); 

videoUrl.setMgwUrl('wss://webrtc.myegoo.com.cn/mgw'); 

videoUrl.setWsUrl('wss://webrtc.myegoo.com.cn/xchat2'); 

videoUrl.setHttpUrl("https://devcc.myegoo.com.cn/portal/"); 

videoUrl.setDbSrvUrl("https://devcc.myegoo.com.cn/dbsrv/"); 

videoUrl.setFileSrvUrl("https://xchat.myegoo.com.cn/fileserver/"); GlobalManager.getInstance().setVideoUrl(videoUrl); 

设置用户信息 

let user: User = new User (); 

user.setUserId (' 用户 ID'); 

user.setUserName (' 用户名称 '); 

user.setTenantId (' 租户 ID'); 

user.setBizType (' 业务类型 '); 

user.setChannelType ('appchat'); 

user.setSkillGroup (' 技能组 '); 

GlobalManager.getInstance ().setUser (user); 

三、功能操作指南 

# 1. 开启视频通话调用接口: 

GlobalManager.getInstance ().startVideoQueue (context, windowStage); 

# 核心功能使用 

音视频无缝切换:通话中可直接切换语音 / 视频模式, 

无需重连合规双录:自动录音录像,满足金融、政务等行业合规要求 后台保活:应用切到后台,通话不中断 

# 合规使用 

要求权限仅在发起视频通话时申请,不提前获取 

SDK 不收集任何个人信息 

遵循功能最小化使用原则,仅启用音视频相关能力 

四、常见问题解答( FAQ ) 

1. Q : SDK 支持哪些系统? 

A :当前 V1.0.0 仅支持华为鸿蒙( HarmonyOS )系统。 

Q : SDK 是否收集个人信息? 

A 不收集任何个人信息,符合隐私合规。 

Q :权限什么时候申请? 

- A :仅在发起视频时申请,不可提前。 

- Q :未获得用户授权可以初始化 SDK 吗? 

- A :不可以,必须用户同意授权后再初始化。 

- Q :是否支持高并发场景? 

- A :支持,已在多个大型企业项目验证。 

五、故障排除 

# 1. 安装失败原因: 

ohpm 环境异常、网络不稳定解决:检查环境配置,切换网络后重新 执行安装命令 

无法开启视频通话原因: 

权限未配置 / 未授权、参数错误、未完成初始化解决:核对权限、确 认用户授权、检查地址与用户参数 

无画面 / 无声音原因: 

摄像头 / 麦克风未授权、设备硬件异常解决:在系统设置开启权限, 检查硬件是否正常 

切后台通话中断原因: 

未配置后台保活权限解决:添加后台保活权限并获取授权 跨渠道无法连接原因: 

渠道类型配置错误、服务地址异常解决:核对 channelType 参数,检 

查网络与服务地址是否可达 

版本信息 

产品名称: FreeLink 音视频 SDK 

当前版本: V1.0.0 开发公司:易谷网络科技股份有限公司
