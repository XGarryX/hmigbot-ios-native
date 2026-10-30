# 接入文档-易谷网络 

## 1、安装 

ohpm install @egoo/freelink 

## 2、所需权限 

ohos.permission.INTERNET ohos.permission.CAMERA ohos.permission.MICROPHONE ohos.permission.KEEP_BACKGROUND_RUNNING 

## 3、引入组件 

import { GlobalManager, User, VideoUrl } from 'freelink' 

## 4、使用示例 

### **4.1** 设置地址信息参数 

```arkts
let videoUrl: VideoUrl = new VideoUrl(); videoUrl.setVideoPageUrl("https://webrtc.myegoo.com.cn/PSBC_h5/index. html"); videoUrl.setMgwUrl('wss://webrtc.myegoo.com.cn/mgw'); videoUrl.setWsUrl('wss://webrtc.myegoo.com.cn/xchat2'); videoUrl.setHttpUrl('https://devcc.myegoo.com.cn/portal/'); videoUrl.setDbSrvUrl('https://devcc.myegoo.com.cn/dbsrv/'); videoUrl.setFileSrvUrl('https://xchat.myegoo.com.cn/fileserver/'); GlobalManager.getInstance().setVideoUrl(videoUrl); 
```

### **4.2** 设置用户信息 

let user: User = new User(); 

user.setUserId('155555555'); user.setUserName('js''); user.setTenantId('default'); user.setBizType('309'); user.setChannelType('appchat'); user.setSkillGroup('jisen'); GlobalManager.getInstance().setUser(user); 

### **4.3** 开启视频 

GlobalManager.getInstance().startVideoQueue(context, windowStage);
