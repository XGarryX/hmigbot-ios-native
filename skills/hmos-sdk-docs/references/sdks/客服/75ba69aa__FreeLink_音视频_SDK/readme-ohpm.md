> 来源: ohpm 中央仓 README(T1 信源) | 包: `@egoo/freelink` | ohpm 最新版: 1.0.0 | 抓取: 2026-07-16
> 注意: 版本可能比市场快照新,以此为准时核对 CHANGELOG

1、简介

Freelink 音视频 SDK 是由易谷网络研发的一款兼容华为鸿蒙(HarmonyOS)系统的实时通信开发工具包。该 SDK 基于 WebRTC 标准协议构建,旨在为移动端应用提供标准化的语音通话、视频通话及多媒体协作能力。

产品核心定位为轻量级、高适配性的通信中间件,支持在鸿蒙原生应用中快速集成音视频能力。除了基础的通信功能外,SDK 集成了音视频无缝切换、合规双录(录音录像)、同屏协作等业务功能,并支持跨渠道(App、Web、小程序、短信链接)的互联互通。目前,该产品已在多个企业级项目中部署应用,具备大规模并发运行的稳定性

2、安装

ohpm install @egoo/freelink

3、所需权限

ohos.permission.INTERNET

ohos.permission.CAMERA

ohos.permission.MICROPHONE

ohos.permission.KEEP_BACKGROUND_RUNNING

4、引入组件

import {

GlobalManager,

User,

VideoUrl

} from 'freelink'

5、使用示例

5.1 设置地址信息参数

let videoUrl: VideoUrl = new VideoUrl();

videoUrl.setVideoPageUrl("https://webrtc.myegoo.com.cn/PSBC_h5/index.html");

videoUrl.setMgwUrl('wss://webrtc.myegoo.com.cn/mgw');

videoUrl.setWsUrl('wss://webrtc.myegoo.com.cn/xchat2');

videoUrl.setHttpUrl('https://devcc.myegoo.com.cn/portal/');

videoUrl.setDbSrvUrl('https://devcc.myegoo.com.cn/dbsrv/');

videoUrl.setFileSrvUrl('https://xchat.myegoo.com.cn/fileserver/');

GlobalManager.getInstance().setVideoUrl(videoUrl);

5.2 设置用户信息

let user: User = new User();

user.setUserId('18769730360');

user.setUserName('js'');

user.setTenantId('default');

user.setBizType('309');

user.setChannelType('appchat');

user.setSkillGroup('jisen');

GlobalManager.getInstance().setUser(user);

5.3 开启视频

GlobalManager.getInstance().startVideoQueue(context, windowStage);

5.4 是否开启满意度评价

GlobalManager.getInstance().setEvaluationEnabled(false);
