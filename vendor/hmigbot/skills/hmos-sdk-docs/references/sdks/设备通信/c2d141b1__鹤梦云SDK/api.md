###### **1,SDK初始化/SDK基本信息** 

接口调用 

1.1,SDK 初始化 推荐使用 1.2,SDK 初始化2 1.3,获取服务器链接状态 1.4,设置国际化ID 1.5,获取国际化ID 1.6,设置网络类型 1.7,获取sdk版本号 1.8,获取paasToken 1.9,销毁SDK,释放资源 **2,登录/注册** 获取接口实例 2.1,手机号登录 2.2,邮箱登录 2.3,三方账号登录 2.4,发送验证码 2.5,注册账号 2.6,检查账号 2.7,获取支持的注册方式 2.8,手机号重置密码 2.9,邮箱重置密码 2.10,三方账号绑定手机号 2.11,三方账号绑定邮箱 2.12,退出登录 2.13,是否已经登录 **3,添加设备** 获取接口实例 3.1,用设备ID添加设备 3.2,通过设备ID和组ID添加设备 3.3,通过设备ID和指定的设备类型添加设备 3.4,license添加设备 3.5,获取添加设备的绑定码 3.6,获取蓝牙设备添加管理实例 3.6.1,搜索蓝牙设备 3.6.2,停止搜索蓝牙设备 3.6.3,添加蓝牙设备 3.6.4,断开蓝牙连接 (如果wifi信息以传到设备端则还是会添加到设备) 3.6.5,销毁蓝牙资源 3.7,搜索局域网设备 3.8,获取添加设备的二维码图片 3.9,获取ap直连添加设备实例 3.9.1,开始直连 3.9.2,开始添加设备 3.9.3,关闭ap连接 **4,设备列表** 获取接口实例 4.1,获取网关设备列表 4.2,获取Nvr设备列表 4.3,获取摄像机设备列表 

4.4,获取全部设备的数量 4.5,同步获取全部设备 4.6,销毁数据 **5,设备操作以及设备信息** 获取接口实例 5.1,获取设备的Wifi列表 5.2,获取当前设备在线状态 

5.3,设备信息 5.3,获取设备类型 5.4,预置位接口实例 5.4.1,上传预置位图片到云 5.4.2,删除云端文件 5.4.3,获取预置位配置信息 5.4.4,ptz移动到预置位的位置 5.4.5,巡航一次 5.4.6,添加预置位 5.4.7,更新预置位 5.4.8,删除预置位 5.4.9,添加巡航轨迹 5.4.10,删除巡航轨迹 5.4.11,设置观察点 5.4.11,设置观察点 5.4.11,PTZ自检(矫正) 5.5,人脸相关功能管理 5.5.1,上传人脸图片 5.5.2,删除人脸图片 5.5.3,获取AI人脸信息 5.6,是否是分享设备 5.7,获取低功耗信息 5.8,检查是否在局域网内 5.9,获取设备时区 5.10,设置设备时区 5.11,设置设备时区 5.11,设置夏令时地区 5.12,格式化TF卡 5.13,获取TF卡容量信息 5.14,切换设备WiFi 5.15,获取设备当前连接网络信息 5.16,发送自定义命令 5.17,切换摄像头 5.18,设置休眠等待时间 4.19,重启设备 5.20,修改设备名称 5.21,设备恢复出厂设置 5.22,设置水印 5.23,设置设备麦克风开关 5.24,设置设备指定镜头的麦克风开关 5.25,设置设备镜头开关 5.26,设置设备指定镜头开关 5.27,切换摄像头开关 5.28,切换指定摄像头开关 5.29,设置红外模式 白光灯模式 5.30,设置设置指定镜头的红外模式 白光灯模式 5.31,设置图像翻转类型 5.32,设置设备指定镜头图像翻转类型 5.33,图像水平翻转 5.34,开启PTZ操作 5.35,停止PTZ操作 

5.36,添加预置位 5.37,获取PTZ转动状态 5.38,设置视频参数 5.39,设置指定镜头ID的视频参数 5.40,设置音频参数 5.41,设置录像prop 5.42,获取录像信息 5.43,设置云录像默认prop 5.44,收集设备端日志 5.45,压缩设备下载的日志文件 5.46,发送音频到设备端 5.47,获取设备端报警提示音列表 5.48,播放指定提示用提示音 5.49,删除报警提示音 5.50,设置设备音量 5.51,设置是否打开转发模式 5.52,获取转发模式开关 5.53,切换镜头 5.54,通知支持物理变焦镜头开始变焦或者停止变焦 5.55,通知支持物理变焦镜头开始变焦或者停止变焦 指定镜头camId 

5.56,设置默认镜头ID 5.57,设置宽动态开关 5,58,设置宽动态开关 指定摄像头ID 5.59,唤醒设备 5.60,设置设备接听状态 5.61,低长结合电量工作模式 编辑模式 5.62,设置自动功耗模式 5.63,开始3d定位 5.64,开始3d定位 指定摄像头ID 5.65,获取算法配置 5.66,设置设备的ap热点密码 5.67,设置密码提示开关 用户勾选不再提示后,设置为0 5.68,客流统计参数设置 5.69,客流统计参数设置 5.70,获取人流统计 5.71,设置时间段蜂鸣器开关, 5.72,设置设备蜂鸣器的音量大小 5.73,获取当前设备的动态配置 5.74,获取设备音量 5.75,获取设备的报警设置 5.76,设置设备的一键报警设置 5.77,设置一键报警状态 5.88,获取相机镜头操作相关接口实例 

5.88.1,获取指定摄像机镜头信息 

5.88.2,获取全部摄像机镜头信息 

5.88.3,获取支持ptz的镜头信息 默认返回第一个镜头信息,单镜头返回唯一一个镜头信息 5.88.4,获取支持变倍的摄像头 5.88.5,是否变焦设备状态 5.88.6,设备变焦镜头的最大焦距 

5.88.7,获取多镜头共同配置(共同控制模式) 镜头为共同控制模式时,调用该接口获取镜头共通配置 5.88.8,获取各镜头独立配置(共同控制模式) 

5.88.9,获取设备cam总数 5.88.10,获取设备工作模式 5.88.11,获取流ID 5.89,获取设备分享用户的列表 5.90,设备是否在线 5.91,获取变声的类型 5.92,设置变声类型 

5.93,设置水印 5.94,获取设备套餐 

**6,云服务套餐** 获取接口实例 6.1,删除缓存套餐 6.2,获取云服务套餐 6.3,异步调用获取云服务套餐 子线程调用 6.4,是否购买了鸟类识别服务 6.5,获取当前生效的全部套餐,包含人脸,鸟类识别等套餐 6.6,获取当前设备的事件套餐, 6.7,获取全部存储套餐 除了过期套餐 6.8,请求全部设备的云服务套餐 6.9,获取当前设备的全天存储套餐 6.10,获取当前正在使用套餐的ID 6.11,是否有人脸识别套餐 6.12,获取套餐状态 6.13,获取指定设备当前的所有套餐 6.14,获取正在使用的人脸套餐 6.15,获取全部的ai套餐 6.16,是否购买了套餐 除了AI云服务 6.17,获取当前生效的存储套餐 6.18,获取对应设备ID的套餐 6.19,获取当前的自动订阅套餐 6.20,获取短信套餐 6.21,获取4G套餐 6.22,获取用户的全部套餐 6.23,获取设备套餐循环天数 6.24,获取时光相册开通状态 6.25,获取时光相册云套餐 6.26,获取开通的事件服务 **7,旧设备相关接口** 获取接口实例 7.1,是否是旧设备 7.2,设置内置IOT 7.3,设置时间录像信息 **8,图片下载,获取图片列表** 获取接口实例 8.1,获取一张实时视频图片 8.2,查询设备端图片日历 8.3,查询设备端图片列表 8.4,下载一张设备端图片 8.5,查询云端图片日历 8.6,查询云端图片列表 8.7,下载一张云端图片 8.9,通过FileID下载图片 **9,时光相册** 获取接口实例 9.1,获取相册分类列表 9.2,获取时光相册支付套餐列表 9.3,获取相册服务信息列表 9.4,获取离过期日期最远的套餐 9.5,获取时光相册有数据的日历 9.6,获取时光相册列表 9.7,获取相册图片列表 9.8,删除时光相册视频 9.9,删除一天的时光相册视频 9.10,删除文件列表时光相册视频 

9.11,获取时光相册设置实体 

9.11.1,获取时间段开关状态 9.11.2,获取抓拍间隔 9.11.3,格式化时间 9.11.4,获取开始时间的秒 9.11.5,获取结束时间段 9.11.6,获取周几掩码 9.11.7,设置侦测开关状态 9.11.8,设置时间段开关状态 9.11.9,获取相册视频模式 9.11.10,保存截图间隔 9.11.11,保存相册视频模式 

9.11.12,保存相册视频时间段 

**10,提示音** 获取接口实例 10.1,上传云音频文件 10.2,查询云音频列表 10.3,删除云音频文件 10.4,更改云音频信息 10.5,通知设备下载音频 10.6,通知平台生成文字转语音 **11,设备时间段策略** 获取接口实例 11.1,创建录像时间段策略 11.2,创建默认的时间段策略 11.3,设置定时策略 11.4,获取定时策略列表 11.5,删除定时策略 **12,NVR设备** 获取接口实例 12.1,搜索NVR子设备接口 12.2,绑定NVR子设备 12.3,设置存储配置 12.4,获取存储配置 12.5,获取子设备状态及信息 12.6,获取子设备状态及信息 12.7,忽略提示信息 12.8,获取通道配置信息 12.9,解除通道绑定 12.10,交换通道 **13,音视频媒体流 14,设备组管理** 获取接口实例 14.1,创建组 14.2,创建子组 14.3,获取组列表 14.4,通过groupId获取groupToken 14.5,用deviceId查找groupId 14.6,获取组Bean 14.7,更新组信息 14.8,删除组 14.9,创建角色 14.10,删除角色 14.11,通过UserID邀请用户加入组 14.12,删除用户 **15,消息事件** 获取接口实例 15.1,查询设备端消息日历 15.2,查询设备端消息列表 

15.3,查询云端消息日历 15.4,查询云端消息列表 15.5,设置云端消息 15.6,设置云端消息 15.7,根据条件获取全部设备的云事件 15.8,获取事件消息详情 15.9,删除云事件 **16,视频录像** 获取接口实例 16.1,查询设备端录像日历 16.2,查询设备端录像列表 16.3,查询云端录像日历数据 16.4,查询云端录像列表 16.5,下载事件列表卡录像或云录像 16.6,回看录像下载, 16.7,取消请求 16.8,保存录像时间段 16.9,获取录像时间段 16.10,录像时间段是否开启 16.11,获取云录像购买套餐 **17,设备报警** 获取接口实例 17.1,设置报警策略 17.2,删除报警策略 17.3,添加监测报警区域 17.4,删除监测报警区域 17.5,修改监测报警区域坐标 17.6,获取区域监测区域坐标信息 **18,设备OTA** 获取接口实例 18.1,检查版本号 18.2,开始升级 18.3,停止升级 18.4,设置设备自动升级 **19,设备IOT** 获取接口实例 19.1,添加433设备以及外置设备 19.2,删除一个外置IOT设备 19.3,删除设备的全部外置Iot 19.4,iot开关设置 19.5,设置Iot名称 19.6,设置IOT联动策略 19.7,设置IOT联动策略 19.8,获取设备的全部Iot开关状态 19.9,设置内置Iot开关 19.10,设置内置Iot联动策略 19.11,设置内置Iot的提示音 19.12,设置inIot 开关 19.13,创建Iot报警策略 19.14,搜索Iot 19.15,获取内置Iot信息 19.16,获取外置Iot信息 19.17,获取外置IOT名称 19.18,获取时光相册的iot **20,报警策略** 获取接口实例 20.1,获取报警策略列表 20.2,获取报警策略信息 

20.3,获取设备的报警策略 20.4,获取报警时间段 20.5,获取事件通知设置信息 20.6,设置报警时间段 20.7,根据事件ID获取对应的报警策略 20.8,设置报警策略事件 20.9,格式化报警时间段 20.10,获取报警时间段的星期数 20.11,保存报警策略数据 20.12,设置报警提示音名称 20.13,设置报警提示音播放循环次数 20.14,获取蜂鸣器报警策略提示音名称 20.15,获取推送类型 20.16,设置通知信息 **21,白光灯** 获取接口实例 21.1,白光灯时间段是否打开 21.2,设置白光灯时间段开关 21.3,获取白光灯模式 21.4, 是否全天时间段 21.5,是否定时时间段 21.6,获取全天时间段字符串 21.7,设置时间段策略的开关 21.8,设置时间段 21.9,删除指定的时间段 21.10,时间策略的时间格式化 21.11,获取时间段时长的Time实例 21.12,判断两个时间段是不是一样 21.13,传入数据格式化显示格式的数据 21.14,保存白光灯时间策略 21.15,保存常亮,常亮就是全天时间段,加了重试3次 21.16,保存红外灯模式 21.17,白光灯模式切换 **22,自定义提示音** 获取接口实例 22.1,开始录制音频 22.2,停止录制音频 22.3,删除当前录制的音频文件 22.4,删除后面录制的一段音频,只在录制音频时有效 22.5,释放录制音频资源 22.6,新建录制自定义音频文件名称 22.7,更改提示音名称 22.8,删除提示音音频文件 22.9,获取录音列表 ,提示音列表 22.10,开始播放录音,如果是要试听正在录制的音频可以不入参 22.11,停止播放音频 22.12,保存音频文件到设备 22.13,查找提示音的本地名称 22.14,pcm音频文件转Wav音频文件 **23,用户信息** 获取接口实例 23.1,刷新用户信息缓存 23.2,连接设备的ap 23.3,获取用户ID 23.4,获取用户token 23.5,通过groupID获取用户token 23.6,获取当前登录的账号信息 23.7,获取用户的个人信息 

23.8,获取指定用户的个人信息 23.9,用手机账号获取userID 23.10,用邮箱获取用户ID 23.11,删除当前账号 23.12,设置推送token 23.13,刷新全部的设备状态, 23.14,获取本地缓存大小 23.15,清除本地缓存 23.16,生成属主转移二维码 23.17,创建分享二维码 23.18,获取微信公众号管理实例 23.18.1,获取微信公众号二维码url 23.18.2,获取微信公众号当前的状态 23.18.3,设置微信公众号通知的开关 23.19,获取资源图片,智能事件显示UI的图片从这里获取,如果定制app也可以不用我们云端图片 23.20,设置国家码,目前国内是"CN" 海外是空字符串 23.21,设置本地语言 23.22,获取支持的账号注册方式 23.23,删除设备,设备退组 23.24,获取分享用户的账号 23.25,获取心钻数量 23.26,获取设备命名页面的用途列表 23.27,获取用户昵称 23.28,获取用户账号 23.29,扫码分享设备到当前用户 23.30,扫码登录 23.31,设备属主转移 23.32,获取分享的二维码 23.34,获取用户的paas信息 23.35,是否无缓存工作模式 **24,本地相册** 获取接口实例 24.1,获取本地截图列表 24.2,删除全部的截图 24.3,获取本地录像视频列表 24.4,删除全部的本地录像视频 24.5,删除单个文件 24.6,获取云录像视频列表 24.7,删除全部下载的云录像 24.8,获取sd卡录像视频列表 24.9,删除全部下载的卡录像 24.10,取视频封面图片 24.11,将图片转换为Base64 24.12,保存图片到指定路径 **25,布防管理** 获取接口实例 25.1,获取当前的布防模式 25.2,切换布防模式 25.3,获取布防模式参数 25.4,修改布防模式参数 25.5,修改布防模式参数 25.6,删除布防策略中的hubIot **26,预置位/巡航** 获取接口实例 26.1,是否支持预置位 26.2,获取预置位列表信息 26.3,添加预置位 26.4,获取预置位的文件路径 

26.5,设置看守位 26.6,删除预置位 26.7,转动到预置位位置 26.8,巡航操作 26.9,下载预置位图片 26.10,是否支持巡航 26.11,是否支持看守位 26.12,是否设置了巡航 26.13,开始ptz矫正 26.14,当前预置位是否添加到了巡航 26.15,删除指定预置位巡航 26.16,获取巡航信息列表,如果没有设置过巡航就会返回一个默认的, 26.17,是否正在巡航 26.18,添加预置位巡航 **27,埋点** 获取接口实例 27.1,多事件设置埋点 27.2,事件上报 27.3,用户拥有状态 **28,本地设备缓存** 获取接口实例 28.1,设置hubIot关联信息 28.2,获取hubIot关联信息 28.3,删除hubIot关联信息 28.4,取消hubIot关联信息 28.5,更新hubIot关联信息 28.6,是否支持强提醒 28.7,获取强提醒的设置项 28.8,设置强提醒设置项 **29,设备播放器** MediaVideoPlayer 播放器控制  MediaRenderController 获取接口实例 

1,设置设备ID 

2,初始化流 

3,点播实时流 

4,点播卡录像 

5,点播云录像 

6,设置屏幕画面的布局 

7,获取播放器的显示模式 

8,是否支持双屏模式 

9,切换流,比如切换高清,超清 

10,停止播放器播放 

11,播放设备声音 

12,开始录制视频 

13,停止录制视频 

14,开始说话 15,停止说话 16,设置是否支持手势滑动摄像头 17,设置是否支持手势缩放 

18,设置设备的倍数 20,截取媒体流的一帧图片 21,设备PTZ转动 22,销毁播放资源 

23,开始设备变焦 

**30,回看,卡录像云录像** 

HMTimeLineView 

**31,全局公共函数** 

获取周几数组 获取周几的掩码数组 

###### **32,全局监听接口** 

获取接口实例 

- 1,设备状态监听 

- 2,新事件通知回调 

- 3,新报警事件通知 

- 4,系统公告通知 

- 5,广告发布通知 

- 6,运营管理平台发送系统消息通知 

###### **33,工具类** 

1,二维码数据解析工具类 

QRCodeContentTools 

   - 1,解析二维码数据 

   - 2,是否包含外置设备 

- 2,蓝牙相关工具类 

BluetoothTools 

   - 1,请求蓝牙权限 

   - 2,判断蓝牙权限授权是否已授权 

      - 3,设置蓝牙开关状态 

   - 4,获取蓝牙开关的状态 

   - 5,注册蓝牙开关状态监听 

   - 6,关闭蓝牙开关状态监听 

- 3,设备能力工具类 

DeviceAbilityTools 

- 1,是否有多个摄像头,如:抢球设备 

- 2,是否支持自定义提示音上云,适配旧版本提示音只设置到设备端的问题 ,智能服务284版本 

- 3,是否支持外设IOT 

- 4,是否支持夏令时 

- 5,是否是双频设备,也就是是否支持5Gwifi 

- 6,是否是鱼眼设备 

- 7,设备是否支持ptz 

- 8,设置是否支持云台插件 

- 9,判断是否为低功耗设备 

- 10,是否支持设备日志发送 

- 11,是否支持设置录像时间段 

- 12,是否支持 双向视频 

- 13,是否支持侦测区域设置 

- 14,是否支持自定义提示音设置 

- 15,是否支持卡录像 

- 16,是否支持云录像 

17,是否支持双屏模式 

18,是否支持状态灯开关设置 

19,是否支持宽动态设置 

20,是否支持红外灯 

21,是否支持白光灯 

22,是否支持白光灯时间段 

23,是否支持一键报警 

24,是否支持一件报警设置 

25,是否支持布防 

26,是否支持时光相册 

27,是否支持报警灯 

28,是否支持人形定位 

29,是否支持预置位 

30,是否支持双向对讲 

31,是否支持物理变焦 

32,变倍模式 

33,是否正在巡航 

34,是否支持3D定位 

- 4,设备唤醒接口,(低功耗设备会休眠,所以需要唤醒后才可以播放视频,设置功能) 

- 5:请求权限工具类 

PermissionUtil 

   - 1,请求权限 

   - 2,检查权限是否已授权 

- 6,Wifi工具类 WifiTools 

   - 1,是否打开了系统WIFI开关 

   - 2,获取wifi列表 

   - 3,格式化IP地址 

   - 4,判断wifi列表是否包含传入的wifi 

   - 5,获取当前移动设备连接的wifi 

   - 6,获取当前移动设备连接的wifi ip信息 

   - 7,获取当前移动设备连接的wifi ip信息 

   - 8,获取当前传入的ap 是否加密 

   - 9,获取当前的ap 是否加密 

   - 10,是否连接了wifi 

   - 11,获取国家码 

   - 12,wifi连接状态变更监听,wifi系统开关状态变更监听 

   - 13,关闭wifi状态变更监听 

- 7,下载视频或图片工具 

DownloadImageUtil 

   - 1,下载http地址图片 

   - 2,下载http地址视频文件 

   - 3,下载图片后保存到文件 

   - 4,保存文件到相册 只能是视频和图片 

- 8,全局事件发送工具类 EventUtil 

   - 1,反注册事件监听 

   - 2,注册事件监听 

   - 3,注册字符串事件ID事件 

   - 4,反注册字符串事件ID 

   - 5,发送事件 

      - 6,发送字符串事件ID的事件 

   - 7,发送多参数事件 

- 8,自定义LoadingDialog CustomLoadingDialog 

   - 1,弹出loading 

   - 2,关闭loading 

- 9,网络监听工具类 获取接口实例 

   - 1,设置网络监听 

   - 2,反注册监听 

   - 3,获取网络类型 

- 10,轻量化存储工具类 使用的“用户首选项” 

PreferencesUtil  单例, 

   - 1,获取实例, 

   - 2,获取实例,并且可链接指定存储的文件,取值的时候也需要用这个获取实例 

   - 3,存储字符串数据 

   - 4,删除指定key的数据 

   - 5,获取指定key的数据 

   - 6,存储number数据类型数据 

   - 7,获取number数据类型数据 

   - 8,存储boolean类型数据 

   - 9,获取boolean类型数据 

   - 10,删除首选项对应文件名称的文件 

- 11,提示音,音频播放工具类 

PromptToneUtil 单例 

   - 1,播放本地存储的音频文件 

   - 2,播放app资源音频文件 

   - 3,本地文件播放,接着上次播放的位置继续播放 

   - 4,app本地资源文件播放,接着上次播放的位置继续播放 

   - 5,通过url设置网络地址进行播放 

   - 6,停止播放 

   - 7,释放播放器资源 

- 13,推送相关设置接口 

PushManager 使用方式:直接创建 

   - 1,获取pushToken 

   - 2,删除推送token 

   - 3,将本地的pushToken提交到服务器 

      - 4,推送消息 

   - 5,清除状态栏消息 

- 14,视频插值工具类 

RecordVideoReSampleUtils 

   - 1,获取当前回看类型的StreamId 

   - 2,是否允许视频差值 

   - 3,录像差值到固定值 

- 4,字符串工具类 

StringUtil 

   - 1,资源文本转字符串 

   - 2,判断字符串是否是number类型 

   - 3,判断字符串是否包含数字 

   - 4,是否不存在非法字符 

   - 5,number数据如果是个位数前面补0 

- 5,系统设置页面或系统事件工具类 

SystemEvent 

   - 1,锁屏监听亮屏监听 

   - 2,打开系统授权页面 

   - 3,打开系统通知设置页面 

   - 4,打开系统wifi开关设置页面 

- 6,系统分享工具类 

SystemSharedUtil 

- 1,分享图片 

2,分享视频 

3,分享文件 

- 4,分享多图片 

5,分享多图片 7,文本样式工具类 TextStyleUtil 单例 

1,修改一段文本的颜色 

2,修改一段文本的颜色 8,文件大小单位工具类 ,比如 kb  mb,gb UnitUtils 1,格式化数据长度,返回带单位的字符串 'B', 'K', 'M', 'G', 'T' 

2,格式化数据长度,返回带单位的字符串 'B', 'KB', 'MB', 'GB', 'TB' 

9,震动工具类 VibratorUtil  单例 1,开始震动 

2,停止震动 10,window工具类,比如页面全屏,状态栏颜色修改等 WindowUtils 

- 1,设置页面是否全屏 

- 2,设置全屏是否隐藏状态栏 

- 3,设置窗口的状态栏颜色 

   - 4,监听屏幕变化,横竖屏监听 

5,取消监听屏幕变化,横竖屏监听 

6,设置屏幕方向 

- 7,获取屏幕方向,横屏还是竖屏 

8,开启禁止截屏 11,SDK工具类 ZJUtil 1,获取app当前的语言码 

- 2,读取文件数据 

- 3,获取版本名称 

- 4,获取版本号 

- 5,线程执行到这里后等待多少毫秒后执行下一步, 

- 6,解析二维码数据 

- 7,获取国家码 

8,是否json字符串 

**34,枚举** 

RegionIdEnum ServerStatusEnum AccountTypeEnum VerifyCodePlatEnum DeviceTypeEnum OSTypeEnum ErrorEnum DeviceStatusEnum AwakeAbilityEnum DefaultPolicyIDEnum NetWorkTypeEnum OSDPositionEnum IRModeEnum InversionTypeEnum PTZCtrlTypeEnum RingTypeEnum EnergyModeEnum CamLensTypeEnum ZoomAbilityModeEnum ThreeDGestureTypeEnum MutateTypeEnum CargePackageStatusEnum CloudChargeTypeEnum云服务套餐枚举 AIIoTTypeEnum AlbumStatusEnum PictureTypeEnum SnapTypeEnum AlbumTypeEnum SortTypeEnum AlbumUiTypeEnum EventTypeIDEnum TimeAlbumModeEnum RecordTypeTimeEnum TimerPolicyTypeEnum GroupRightEnum PushTypeEnum FenceDetectAbilityEnum PTZAbilityEnum SensitivityEnum WhiteLightModeEnum SoundTypeEnum CacheWorkModeEnum VideoEncTypeEnum 

ProtectionModeEnum ApplyPermissionEnum ZoomTypeEnum PlayShowModeEnum PlayTypeEnum PTZDirectionEnum NetWorkTypeEnum LanguageEnum **35,接口回调** ITask IBaseCallback IResultCallback ILoginCallback IResultListener ICheckAccountCallback IGetAccountTypeListCallback IAddDeviceCallback IGetBindCodeCallback ISearchBluetoothDeviceCallback AddDeviceCallback LanSearchObserver ICreateQRCodeCallback IAPDirectActivatorCallback IDeviceListChangeCallback IGetWiFiListCallback IUploadFileCallback IGetTimeZoneCallback IGetTFCardInfoCallback ICurNetWorkCallback IPTZStatusCallback IResultListener IGetSoundListCallback IGetSMSPackageCallback I4GChargePackageCallback ILiveImageCallback IImageListCallback IImageLocalCallback IImageCalendarCallback IRecordCalendarCallback IGetAlbumVideoListCallback IGetAlbumPicListCallback INVRSearchSubDevCallback INVRBindSubDevCallback ICreateGroupCallback IEventCalendarCallback IRecordListCallback IModifyfenceResult ICheckVersionCallback IAIIoTStatusCallback ISoundListCallback IRefreshVcardCallback IGetUserIdCallback ICacheSizeCallback IChangeQRCallback IWeChatQRCodeCallback IWeChatCurStatusCallback IGetResourceCallback IGetAccountTypeListCallback 

IScanCodeCallback IGetPaasAccessTokenCallback IRequestPermissionCallback IBluetoothLinkStateCallback IStartRequestCallback IRequestPermissionCallback IWifiStatusCallback EventNoticeObserver AlarmEventObserver SystemNoticeObserver AdNoticeObserver IAppGradeNoticeObserver IRecordMP4Listener TimeLineCallback **36,数据信息** 

LoginUserInfo LoginBindInfo BluetoothDeviceModel LanSearchDeviceModel QRCodeParamModel Device WiFiBean DeviceBean MulMediaBean SimBean PresetInfo PresetBean PresetPointBean CruiseBean CruisePointBean OutputBean TimePolicyBean AIInfoBean DeployFaceLabelBean DeployFaceSampleBean 布控的人脸样本 EnergyInfoBean EnergyModelBean NetworkBean VideoParamBean VideoCircleBean VideoDistortionBean AudioParamBean RecordProp RingFileBn EnergyModelBean AlgorithmInfoBean EventInfBean AlgorithmServiceBean AppSettingModel 获取屏幕分屏数据 ScreenSplitBean 获取百分比 是否打开 是否为四目抢球设备 DeviceAlarmParam 状态灯是否打开 设置状态灯开关 设置报警声音音量 

获取报警音量 CameraBean 是否支持PTZ 是否支持变焦 是否JPEG流编码 获取变倍的镜头ID StreamBean LensBean PrivacyAreaBean FencePointBean GroupUserBean GroupRoleBean ChargePackageInfo ChargePackageData EventIdBean ModuleServiceBean I4GChargePackageBean EventServiceTypeBean InnerDACOption OptionSchedule ScheduleInfo ImageBean AlbumTabInfo AlbumInfo PayInfoBean Relpkg TagX Infolist AiAlbumServiceInfo AIAlbumVideoBean AIAlbumPicBean AlarmTimeBean TimePolicyParam NvrSubDevInfoBean NvrChannelPairBean NvrStorageBean NvrStorageNodeBean NvrChannelConfigBean NvrChannelInfoBean GroupBean GroupUserBean GroupDeviceBean ChildGroupBean MessageBean FaceInfo AiIdentifyBean AiNameBean EventDetailsBean RecognitionImageResult RecordBean AlarmPolicyBean PolicyEventBean FenceInfoBean FencePointBean SceneIDBean TriggerInfoBean HubIoTInfo HubIoTBean 

IoTStatusBean InnerIoTInfo 是否支持报警灯 获取内置IOT信息 获取录像策略 录像的流ID,0:超清,1:高清 InnerIoTBean AlgorithmNodeBean RecordProp 获取持续时长 设置持续时长 设置给对象 AlarmTimeBean EventOutputParam AlarmNoticeInfo NoticeTimeBean CustomAudioBean UserVCardBean UserBean ResourceBean UseModel LocalMediaBean ProtectionModeParam HomeBean MotionBean HumanBean FaceBean AwayBean RemovalBean PresetModel SetPresetModel CruiseBean CruisePointBean PairInfo NoticeSettingBean WifiInfo SystemNoticeBean AdNoticeBean 

# **1,SDK初始化/SDK基本信息** 

### **接口调用** 

```
HmSdk.getInstance()
```

### **1.1,SDK 初始化 推荐使用** 

```
init( companyId, appId, serverEnv,configPath, cachePath): boolean
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|companyId|string|企业ID,从平台注册获取|
|appId|string|appID,从平台注册获取|
|serverEnv|ServerEnvEnum|开发环境|
|configPath|string (可选)|配置缓存路径|
|cachePath|string (可选)|数据缓存路径|

### **1.2,SDK 初始化2** 

##### 可以根据服务域名初始化SDK 

```
initWithHost( companyId: string, appId: string, serverHost: string, baseWebHost:
string, configPath?: string, cachePath?: string): boolean
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|companyId|string|企业ID,从平台注册获取|
|appId|string|appID,从平台注册获取|
|serverHost|string|服务域名|
|baseWebHost|string|webHost|
|configPath|string(可选)|配置缓存路径|
|cachePath|string(可选)|数据缓存路径|

### **1.3,获取服务器链接状态** 

```
getServerStatus(): ServerStatusEnum
```

##### 详见 ServerStatusEnum 

### **1.4,设置国际化ID** 

##### 如果你的包是分国内海外,那么需要给sdk标记 

```
setRegionid(regionId : RegionIdEnum) :void
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|regionId|RegionIdEnum|国内海外标记的枚举|

**1.5,获取国际化ID** 

##### 需要设置区域ID才可以获取区域ID 

```
getRegionid() : RegionIdEnum
```

详见:RegionIdEnum 

### **1.6,设置网络类型** 

##### 内部会获取系统网络类型设置到sdk,所以没有入参 

```
setNetwrokType() : void
```

### **1.7,获取sdk版本号** 

```
getSDKVersion() : void
```

### **1.8,获取paasToken** 

加载web页面的时候拦截获取用户信息接口返回数据时需要paasToken 

```
getPaasToken() : Promise<UserPaasTokenBean>
```

### **1.9,销毁SDK,释放资源** 

```
destroy() : void
```

# **2,登录/注册** 

### **获取接口实例** 

```
HmSdk.getInstance().newLoginModule()
```

### **2.1,手机号登录** 

```
loginByMobile(countryCode : string,mobile : string,password : string,callback :
IResultCallback) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|countryCode|string|国家码,如中国:86|
|mobile|string|手机号|
|password|string|账号密码|
|callback|IResultCallback|回调|

return ITask 

### **2.2,邮箱登录** 

```
loginByEmail(email : string,password : string,callback : IResultCallback) :
ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|email|string|邮箱账号|
|password|string|密码|
|callback|IResultCallback|回调|

return ITask 

### **2.3,三方账号登录** 

```
loginByThirdParty(accountType : AccountTypeEnum,thirdPartyUid :
string,thirdPartyToken : string,callback : ILoginCallback) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|accountType|AccountTypeEnum|三方账号类型|
|thirdPartyUid|string|三方账号UID|
|thirdPartyToken|string|三方账号Token|
|callback|ILoginCallback|回调|

return ITask 

### **2.4,发送验证码** 

```
sendCodeByTencent(account : string,areaCode : string | undefined,codeType :
VerifyCodeTypeEnum,callback : IResultListener<VerifyCodePlatEnum>) : void
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|account|string|账号|
|areaCode|string|区域码 如:86|
|codeType|VerifyCodeTypeEnum|发送验证码类型|
|callback|IResultListener< VerifyCodePlatEnum>|回调|

### **2.5,注册账号** 

```
registerAccount(   account: string, password: string,areaCode: string |
undefined,
    verifyCode: string | undefined, callback: IResultCallback) : void
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|account|string|账号|
|password|string|密码|
|areaCode|string|区域码 如:86|
|verifyCode|string|验证码|
|callback|IResultCallback|回调|

### **2.6,检查账号** 

```
checkAccount(isSupportEmial : boolean,isSupportPhoneNum : boolean ,account :
string,areaCode : string,countryCode : string,callback : ICheckAccountCallback) :
void
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|isSupportEmial|boolean|App是否支持邮箱账号|
|isSupportPhoneNum|boolean|App是否支持手机账号|
|account|string|账号|
|areaCode|string|区域码:86|
|countryCode|string|国家码:CN|
|callback|ICheckAccountCallback|回调|

### **2.7,获取支持的注册方式** 

```
getSupportRegisterAccountTypeList(zoneCode : string,callback :
IGetAccountTypeListCallback) : void
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|zoneCode|string|区域码|
|callback|IGetAccountTypeListCallback|回调|

### **2.8,手机号重置密码** 

```
resetPasswordByMobile(countryCode : string,mobile : string,newPassword :
string,verifyCode : string,verifyCodePlatform : VerifyCodePlatEnum,callback :
IResultCallback) : void
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|countryCode|string|国家码:CN|
|mobile|string|手机号|
|newPassword|string|新密码|
|verifyCode|string|验证码|
|verifyCodePlatform|VerifyCodePlatEnum|验证码平台类型|
|callback|IResultCallback|回调|

### **2.9,邮箱重置密码** 

```
resetPasswordByEmail(email : string,newPassword : string,verifyCode :
string,callback : IResultCallback) : void
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|email|string|邮箱账号|
|newPassword|string|新密码|
|verifyCode|string|验证码|
|callback|IResultCallback|回调|

### **2.10,三方账号绑定手机号** 

```
bindMobile(countryCode : string,mobile : string,verifyCode :
string,verifyCodePlatform : VerifyCodePlatEnum,callback : IResultCallback) :
void
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|countryCode|string|国家码:CN|
|mobile|string|手机号|
|verifyCode|string|验证码|
|verifyCodePlatform|VerifyCodePlatEnum|验证码平台类型|
|callback|IResultCallback|回调|

### **2.11,三方账号绑定邮箱** 

```
bindEmail(email : string,verifyCode : string,callback : IResultCallback) : void
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|email|string|邮箱账号|
|verifyCode|string|验证码|
|callback|IResultCallback|回调|

### **2.12,退出登录** 

```
logout() : void
```

### **2.13,是否已经登录** 

```
isLogin() : boolean
```

# **3,添加设备** 

### **获取接口实例** 

```
HmSdk.getInstance().newLoginModule()
```

### **3.1,用设备ID添加设备** 

```
addDeviceByDID (deviceId: string) : Promise<void>
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|deviceId|string|设备ID|

**3.2,通过设备ID和组ID添加设备** 

```
addDeviceByDeviceId (deviceId: string, groupId: string, callback:
IResultCallback) : void
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|deviceId|string|设备ID|
|groupId|string|组ID|
|callback|IResultCallback|回调|

### **3.3,通过设备ID和指定的设备类型添加设备** 

```
addDeviceByDIDAndDeviceType(deviceTypeEnum : DeviceTypeEnum,deviceId :
string,callback : IResultCallback) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|deviceTypeEnum|DeviceTypeEnum|设备类型|
|deviceId|string|设备ID|
|callback|IResultCallback|回调|

### **3.4,license添加设备** 

```
addDeviceByLicense (license: string, callback: IAddDeviceCallback) : void
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|license|string|license,每个设备都会烧录|
|callback|IAddDeviceCallback|回调接口|

### **3.5,获取添加设备的绑定码** 

```
createBindCode (groupId : string,callback : IGetBindCodeCallback) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|groupId|string|组ID|
|callback|IGetBindCodeCallback|回调接口|

**3.6,获取蓝牙设备添加管理实例** 

```
bluetoothAddDeviceInstance () : IZJViewerBluetoothAddDev
```

#### **3.6.1,搜索蓝牙设备** 

```
searchBluetoothDevice(callbackTime: number, timeOutSeconds: number, callback:
ISearchBluetoothDeviceCallback) : void
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|callbackTime|number|回调时间,间隔多少秒回调一次|
|timeOutSeconds|number|超时时间|
|callback|ISearchBluetoothDeviceCallback|回调接口|

#### **3.6.2,停止搜索蓝牙设备** 

```
stopSearchDevice() : void
```

#### **3.6.3,添加蓝牙设备** 

```
addBluetoothDevice(macAddress: string, ssid: string, paw: string, timeOutSeconds:
number, callback: AddDeviceCallback) : void
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|macAddress|string|蓝牙mac地址|
|ssid|string|wifi名称|
|paw|string|wifi密码|
|timeOutSeconds|number|超时时间 单位秒|
|callback|AddDeviceCallback|回调接口|

#### **3.6.4,断开蓝牙连接 (如果wifi信息以传到设备端则还是会添加到设备)** 

```
stopAddDev() : void
```

#### **3.6.5,销毁蓝牙资源** 

```
destory() : void
```

**3.7,搜索局域网设备** 

```
searchLanDevice (timeOut : number ,callback : LanSearchObserver) : void
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|timeOut|number|超时时间|
|callback|LanSearchObserver|回调接口|

### **3.8,获取添加设备的二维码图片** 

```
getQRCodeAddDeviceEntity (model : QRCodeParamModel,callback :
ICreateQRCodeCallback) : void
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|model|QRCodeParamModel|二维码生成数据|
|callback|ICreateQRCodeCallback|回调接口|

### **3.9,获取ap直连添加设备实例** 

```
 newZJViewerAPDirectInstance () : IZJViewerAPDirectDevice
```

#### **3.9.1,开始直连** 

```
startDirect : (timeOut : number ,callback : IAPDirectActivatorCallback) => void
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|timeOut|number|超时时间|
|callback|IAPDirectActivatorCallback|回调接口|

#### **3.9.2,开始添加设备** 

```
startAddDevice : (deviceId : string,ssid : string,password : string,callback :
IAddDeviceCallback) => void
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|deviceId|string|设备Id|
|ssid|string|wifi名称|
|password|string|wifi密码|
|callback|IAddDeviceCallback|回调接口|

#### **3.9.3,关闭ap连接** 

```
closeAPLink : () => void
```

# **4,设备列表** 

### **获取接口实例** 

```
HmSdk.getInstance().newZJViewerDeviceList()
```

### **4.1,获取网关设备列表** 

```
getGatewayDeviceList() :Array<Device>
```

##### Device 

### **4.2,获取Nvr设备列表** 

```
getNvrDeviceList() :Array<Device>
```

##### Device 

### **4.3,获取摄像机设备列表** 

```
getCameraDeviceList() : Array<Device>
```

##### Device 

**4.4,获取全部设备的数量** 

```
getAllDeviceSize() : number
```

### **4.5,同步获取全部设备** 

```
getAllDeviceListSync : (changeCallback? : IDeviceListChangeCallback) =>
Array<Device>
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|changeCallback|IDeviceListChangeCallback|回调接口|

### **4.6,销毁数据** 

```
destory : () => void
```

# **5,设备操作以及设备信息** 

### **获取接口实例** 

```
HmSdk.getInstance().newZJViewerDevice()
```

### **5.1,获取设备的Wifi列表** 

```
getDeviceWifiList (callback : IGetWiFiListCallback): ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|callback|IGetWiFiListCallback|接口回调|

##### 出参: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

**5.2,获取当前设备在线状态** 

```
getCurrDeviceStatus (): DeviceStatusEnum
```

##### 出参: 

|**参数类型**|**说明**|
|---|---|
|DeviceStatusEnum|设备状态枚举|

### **5.3,设备信息** 

```
getDeviceInfo (): DeviceBean
```

##### 出参: 

|**参数类型**|**说明**|
|---|---|
|DeviceBean|设备信息|

### **5.3,获取设备类型** 

```
getDeviceType () : DeviceTypeEnum
```

##### 出参: 

|**参数类型**|**说明**|
|---|---|
|DeviceTypeEnum|设备类型枚举|

### **5.4,预置位接口实例** 

#### **5.4.1,上传预置位图片到云** 

```
uploadPresetImageToCloud : (filePath : string,callback : IUploadFileCallback) =>
ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|filePath|string|图片文件路径|
|callback|IUploadFileCallback|回调接口|

返回: 

**参数类型** 

**说明** 

ITask 请求任务,可以取消请求 

#### **5.4.2,删除云端文件** 

```
deleteCloudFile : (fileId : string,callback : IResultCallback) => ITask
```

|**参数名**|**参数类型**||**说明**|
|---|---|---|---|
|fileId|string||上传预置位图片时返回的fileID,参考5.4.1|
|callback 返回:|IResultCallb|ack|回调接口|
|**参数类型**||**说明**||
|ITask||请求任务|,可以取消请求|

#### **5.4.3,获取预置位配置信息** 

```
getPresetInfo() : PresetInfo
```

##### 返回: 

**参数类型 说明** PresetInfo 预置位信息 

#### **5.4.4,ptz移动到预置位的位置** 

```
ctrlPtzToPresetPoint(presetId : number,callback : IResultCallback) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|presetId|number|预置位ID|
|callback|IResultCallback|接口回调|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

**一** **5.4.5,巡航 次** 

```
ctrlPtzToCruise(cruiseId : number,callback : IResultCallback) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|cruiseId|number|巡航ID|
|callback|IResultCallback|接口回调|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

#### **5.4.6,添加预置位** 

```
addPtzPresetPointWithZ(presetId : number,presetname : string,picId : string,z :
number,callback : IResultCallback) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|presetId|number|预置位ID|
|presetname|string|预置位名称|
|picId|string|图片ID,需要先上传预置位图片|
|z|number|保存预置位的时候当前的放大倍数|
|callback|IResultCallback|接口回调|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

#### **5.4.7,更新预置位** 

```
updataPreset(presetId : number,presetNewName : string,picId : string,callback :
IResultCallback) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|presetId|number|预置位ID|
|presetNewName|string|需要修改的名称|
|picId|string|需要修改的预置位图片id|
|callback|IResultCallback|回调接口|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

#### **5.4.8,删除预置位** 

```
deletePtzPresetPoint(presetId : number,callback : IResultCallback) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|presetId|number|预置位ID|
|callback|IResultCallback|回调接口|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

#### **5.4.9,添加巡航轨迹** 

```
addPtzCruise(cruiseNode : CruiseBean,callback : IResultCallback) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|cruiseNode|CruiseBean|巡航轨迹|
|callback|IResultCallback|接口回调|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

**5.4.10,删除巡航轨迹** 

```
deletePtzCruise(cruiseId : number,callback : IResultCallback) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|cruiseId|number|巡航ID|
|callback|IResultCallback|接口回调|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

#### **5.4.11,设置观察点** 

```
setPtzWatchPoint(presetId : number,watchTime : number,callback : IResultCallback)
: ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|presetId|number|预置位ID|
|watchTime|number|观察时间|
|callback|IResultCallback|接口回调|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

#### **5.4.11,设置观察点** 

```
deletePtzWatchPoint(callback : IResultCallback) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|callback|IResultCallback|接口回调|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

**5.4.11,PTZ自检(矫正)** 

```
setPTZSelfCheck(callback : IResultCallback) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|callback|IResultCallback|接口回调|

返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

### **5.5,人脸相关功能管理** 

```
getAIFaceApi (): IAIFaceEntity
```

#### **5.5.1,上传人脸图片** 

```
uploadFaceImageToCloud(fileName : string,callback : IUploadFileCallback) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|fileName|string|人脸图片名称|
|callback|IUploadFileCallback|接口回调|

返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

#### **5.5.2,删除人脸图片** 

```
deleteCloudFile(fileId : string,callback : IResultCallback) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|fileId|string|文件ID|
|callback|IResultCallback|接口回调|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

**5.5.3,获取AI人脸信息** 

```
getAIInfo() : AIInfoBean
```

##### 返回: 

**参数类型 说明** AIInfoBean Ai人脸信息 

### **5.6,是否是分享设备** 

```
isDeviceByShare() : boolean
```

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|boolean|true是分享设备,false不是分享设备|

### **5.7,获取低功耗信息** 

```
getEnergyInfo() : EnergyInfoBean
```

##### 返回: 

**参数类型 说明** EnergyInfoBean 设备低功耗信息 

### **5.8,检查是否在局域网内** 

```
checkSameLan() : boolean
```

##### 返回: 

**参数类型 说明** boolean true:在局域网内,false:不在局域网内 

### **5.9,获取设备时区** 

```
getZoneAndTime(callback : IGetTimeZoneCallback) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|callback|IGetTimeZoneCallback|回调接口|

返回: 

**参数类型** 

**说明** 

ITask 请求任务,可以取消请求 

### **5.10,设置设备时区** 

```
setZoneAndTime(autoSync : boolean,time : string,timeZone : number,timezoneArea :
string,timeMode : number,callback : IResultCallback) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|autoSync|boolean|自动同步时区|
|time|string|时间,格式:yyyy-MM-dd HH:mm:ss|
|timeZone|number|时区,单位:秒{getRawOffset()}|
|timezoneArea|string|时区区域ID|
|timeMode|number|设置时间24/12小时制设置参数timeMode(0:24小时1: 12小时)|
|callback|IResultCallback|回调接口|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

### **5.11,设置设备时区** 

```
setTimeZone(timeZoneId : string,timeMode : number,callback : IResultCallback) :
ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|timeZoneId|string|时区区域ID|
|timeMode|number|设置时间24/12小时制设置参数timeMode(0:24小时1:12 小时)|
|callback|IResultCallback|接口回调|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

**5.11,设置夏令时地区** 

```
setZoneID(dstArea : string,timeMode : number , callback : IResultCallback) :
ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|dstArea|string|夏令时地区,时区ID|
|timeMode|number|设置时间24/12小时制设置参数timeMode(0:24小时1:12 小时)|
|callback|IResultCallback|接口回调|

### **5.12,格式化TF卡** 

```
formatTFCard(callback : IResultCallback) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|callback|IResultCallback|接口回调|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

### **5.13,获取TF卡容量信息** 

```
getTFCardInfo(callback : IGetTFCardInfoCallback) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|callback|IGetTFCardInfoCallback|接口回调|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

### **5.14,切换设备WiFi** 

```
changeWiFi(ssid : string,password : string,callback : IResultCallback) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|ssid|string|wifi名称|
|password|string|WiFi密码|
|callback|IResultCallback|接口回调|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

### **5.15,获取设备当前连接网络信息** 

```
getCurNetworkInfo(callback : ICurNetWorkCallback) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|callback|ICurNetWorkCallback|接口回调|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

### **5.16,发送自定义命令** 

```
sendCustomData(data : string) : void
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|data|string|自定义命令策略|

### **5.17,切换摄像头** 

```
switchCamera(callback : IResultCallback) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|callback|IResultCallback|接口回调|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

**5.18,设置休眠等待时间** 

```
setWaitSleepTime(waitTime : number,callback : IResultCallback) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|waitTime|number|等待时间|
|callback|IResultCallback|接口回调|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

### **4.19,重启设备** 

```
rebootDevice(callback : IResultCallback) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|callback|IResultCallback|接口回调|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

### **5.20,修改设备名称** 

```
setDeviceName(deviceName : string,callback : IResultCallback) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|deviceName|string|设备名称|
|callback|IResultCallback|接口回调|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

**5.21,设备恢复出厂设置** 

```
restoreFactorySettings(callback : IResultCallback) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|callback|IResultCallback|接口回调|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

### **5.22,设置水印** 

```
setCamOSDInfo(osdInfo : string,position : OSDPositionEnum,callback :
IResultCallback) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|osdInfo|string|水印信息|
|position|OSDPositionEnum|水印位置|
|callback|IResultCallback|接口回调|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

### **5.23,设置设备麦克风开关** 

```
setMicOpenFlag(micOpenFlag : boolean,callback : IResultCallback) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|micOpenFlag|boolean|麦克风开关|
|callback|IResultCallback|接口回调|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

### **5.24,设置设备指定镜头的麦克风开关** 

```
setMicOpenFlagByCamId(micOpenFlag : boolean,camId : number,callback :
IResultCallback) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|micOpenFlag|boolean|麦克风开关|
|camId|number|摄像头ID|
|callback|IResultCallback|接口回调|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

### **5.25,设置设备镜头开关** 

```
setCameraOpenFlag(cameraOpenFlag : boolean,callback : IResultCallback) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|cameraOpenFlag|boolean|镜头开关|
|callback|IResultCallback|接口回调|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

### **5.26,设置设备指定镜头开关** 

```
setCameraOpenFlagByCamId(cameraOpenFlag : boolean,camId : number,callback :
IResultCallback) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|cameraOpenFlag|boolean|镜头开关|
|camId|number|镜头ID,如果有两个镜头那么一个是0,一个是1|
|callback|IResultCallback|接口回调|

返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

### **5.27,切换摄像头开关** 

```
switchCameraFlash(openFlag : boolean,callback : IResultCallback) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|openFlag|boolean|摄像头开关|
|callback|IResultCallback|接口回调|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

### **5.28,切换指定摄像头开关** 

```
switchCameraFlashByCamId(openFlag : boolean,camId : number,callback :
IResultCallback) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|openFlag|boolean|开关|
|camId|number|摄像头ID|
|callback|IResultCallback|接口回调|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

### **5.29,设置红外模式 白光灯模式** 

```
setCamIRMode(irMode : IRModeEnum,callback : IResultCallback) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|irMode|IRModeEnum|红外模式|
|callback|IResultCallback|接口回调|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

### **5.30,设置设置指定镜头的红外模式 白光灯模式** 

```
setCamIRModeByCamId(irMode : IRModeEnum,camId : number ,callback :
IResultCallback) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|irMode|IRModeEnum|红外模式|
|camId|number|摄像头ID|
|callback|IResultCallback|接口回调|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

### **5.31,设置图像翻转类型** 

```
setCamInversionType(inversionType : InversionTypeEnum | number,callback :
IResultCallback) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|inversionType|InversionTypeEnum|翻转类型,掩码,可以用or一起使用|
|callback|IResultCallback|接口回调|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

**5.32,设置设备指定镜头图像翻转类型** 

```
setCamInversionTypeByCamId(inversionType : InversionTypeEnum | number,camId :
number,callback : IResultCallback) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|inversionType|InversionTypeEnum|画面翻转类型|
|camId|number|摄像头ID|
|callback|IResultCallback|接口回调|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

### **5.33,图像水平翻转** 

```
setCamMirrorType(inversionType : number,camId : number,callback :
IResultCallback) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|inversionType|number|翻转类型(掩码形式)|
|camId|number|镜头ID|
|callback|IResultCallback|接口回调|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

### **5.34,开启PTZ操作** 

```
startCtrlPtz(ptzCtrlType : PTZCtrlTypeEnum,step : number,speed : number,callback
: IResultCallback) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|ptzCtrlType|PTZCtrlTypeEnum|PTZ方向|
|step|number|步长(0-360)|
|speed|number|步速(1-7)|
|callback|IResultCallback|接口回调|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

### **5.35,停止PTZ操作** 

```
stopCtrlPtz(callback : IResultCallback) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|callback|IResultCallback|接口回调|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

### **5.36,添加预置位** 

```
addPtzPresetPoint(presetId : number,presetName : string,picId : string,callback :
IResultCallback) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|presetId|number|预置位ID|
|presetName|string|预置位名称|
|picId|string|图片ID,需要上传图片到云端才会有图片ID|
|callback|IResultCallback|接口回调|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

**5.37,获取PTZ转动状态** 

```
getPTZStatus(callback : IPTZStatusCallback) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|callback|IPTZStatusCallback|接口回调|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

### **5.38,设置视频参数** 

```
setVideoParam(streamId : number,videoParam : VideoParamBean,callback :
IResultCallback) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|streamId|number|流Id|
|videoParam|VideoParamBean|视频生成数据|
|callback|IResultCallback|接口回调|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

### **5.39,设置指定镜头ID的视频参数** 

```
setVideoParamByCamId(streamId : number,camId : number,videoParam :
VideoParamBean,callback : IResultCallback) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|streamId|number|流ID,如果有两路流,那么流ID 0是超清,1是高清|
|camId|number|摄像头ID如果有两个摄像头,一个ID是0,一个ID是1|
|videoParam|VideoParamBean|视频生成数据|
|callback|IResultCallback|接口回调|

返回: 

**参数类型** 

**说明** 

ITask 请求任务,可以取消请求 

### **5.40,设置音频参数** 

```
setAudioParam(audioParam : AudioParamBean,callback : IResultCallback) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|audioParam|AudioParamBean|音频设置数据|
|callback|IResultCallback|接口回调|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

### **5.41,设置录像prop** 

```
setRecordProp(recordProp : RecordProp,callback : IResultCallback) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|recordProp|RecordProp|录像设置项|
|callback|IResultCallback|接口回调|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

### **5.42,获取录像信息** 

```
getRecordInfo() : RecordProp
```

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|RecordProp|录像设置项信息|

### **5.43,设置云录像默认prop** 

云服务录制会根据套餐录制 如:全天,事件,如果调用了这个接口就不允许设置云录制时间段, CLOUD_RECORD_TIME_POLICY 

```
setCloudDefaultRecord(callback : IResultCallback) : void
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|callback|IResultCallback|回调接口|

### **5.44,收集设备端日志** 

```
collectLogFile(callback : IResultListener<string>) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|callback|IResultListener|接口回调|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|RecordProp|录像设置项信息|

### **5.45,压缩设备下载的日志文件** 

```
zipDeviceLogFile(deviceId : string) : Promise<string>
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|deviceId|string|设备Id|

返回: 

|**参数类型**|**说明**|
|---|---|
|Promise|Promise返回文件路径|

### **5.46,发送音频到设备端** 

```
pushSoundFileToDevice(deviceId : string,filePath : string,fileName :
string,callback : IResultCallback) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|deviceId|string|设备ID|
|filePath|string|文件路径|
|fileName|string|文件名称|
|callback|IResultCallback|接口回调|

返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

### **5.47,获取设备端报警提示音列表** 

```
getSoundList(callback : IGetSoundListCallback,ringType? : RingTypeEnum) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|callback|IGetSoundListCallback|接口回调|
|ringType|RingTypeEnum|铃声类型枚举 (可空)|

返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

### **5.48,播放指定提示用提示音** 

```
playSound(soundName : string,callback : IResultCallback) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|soundName|string|提示音名称|
|callback|IResultCallback|接口回调|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

**5.49,删除报警提示音** 

```
deleteSound(soundName : string,callback : IResultCallback) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|soundName|string|提示音名称|
|callback|IResultCallback|接口回调|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

### **5.50,设置设备音量** 

```
setDeviceVolume(volume : number,callback : IResultCallback) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|volume|number|音量(0-100)|
|callback|IResultCallback|接口回调|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

### **5.51,设置是否打开转发模式** 

```
setRelayWorkMode(openFlag : boolean , callback : IResultCallback) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|openFlag|boolean|转发开关|
|callback|IResultCallback|接口回调|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

**5.52,获取转发模式开关** 

```
getRelayModeOpenFlag() : boolean
```

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|boolean|是否是转发模式|

### **5.53,切换镜头** 

```
switchCamLens(lensId : number,callback : IResultCallback) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|lensId|number|镜头ID|
|callback|IResultCallback|接口回调|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

### **5.54,通知支持物理变焦镜头开始变焦或者停止变焦** 

```
setLenFocalLenth(lenId : number,ctrlType : number,direction : number,zoomValue :
number,callback : IResultCallback) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|lenId|number|镜头ID|
|ctrlType|number|0:停止;1:开始|
|direction|number|1:放大;2:缩小|
|zoomValue|number|缩放倍速|
|callback|IResultCallback|接口回调|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

**5.55,通知支持物理变焦镜头开始变焦或者停止变焦 指定镜头camId** 

```
setLenFocalLenthByCamId(camid : number,lenId : number,ctrlType : number,direction
: number,zoomValue : number,callback : IResultCallback) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|camid|number|摄像头Id|
|lenId|number|镜头ID|
|ctrlType|number|0:停止;1:开始|
|direction|number|1:放大;2:缩小|
|zoomValue|number|缩放倍速|
|callback|IResultCallback|接口回调|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

### **5.56,设置默认镜头ID** 

```
setDefaultLensId(lensId : number,autoFlag : boolean,callback : IResultCallback) :
ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|lensId|number|镜头ID|
|autoFlag|boolean|是否自动切换|
|callback|IResultCallback|接口回调|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

### **5.57,设置宽动态开关** 

```
setDeviceCameraWDR(openFlag : boolean,callback : IResultCallback) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|openFlag|boolean|开关|
|callback|IResultCallback|接口回调|

返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

### **5,58,设置宽动态开关 指定摄像头ID** 

```
setDeviceCameraWDRByCamId(openFlag : boolean,camId : number,callback :
IResultCallback) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|openFlag|boolean|宽动态开关|
|camId|number|摄像头ID|
|callback|IResultCallback|接口回调|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

### **5.59,唤醒设备** 

```
awakeDevice(callback : IResultCallback) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|callback|IResultCallback|接口回调|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

### **5.60,设置设备接听状态** 

```
setAcceptDevCallStatus(status : number,callback : IResultCallback) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|status|number|0:挂断;1:接听2:繁忙-当前正在通话中|
|callback|IResultCallback|接口回调|

返回: 

**参数类型** 

**说明** 

ITask 请求任务,可以取消请求 

### **5.61,低长结合电量工作模式 编辑模式** 

```
setEnergyModelParam(energyModelNode : EnergyModelBean,callback : IResultCallback)
: ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|energyModelNode|EnergyModelBean|功耗模式信息|
|callback|IResultCallback|接口回调|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

### **5.62,设置自动功耗模式** 

```
setPeerEnergyWorkType(workType : number,modeId : EnergyModeEnum,callback :
IResultCallback) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|workType|number|0自动;1手动|
|modeId|EnergyModeEnum|功耗模式|
|callback|IResultCallback|接口回调|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

### **5.63,开始3d定位** 

```
startPeer3DPosition(x : number,y : number,callback : IResultCallback) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|x|number|ptz转动的x轴|
|y|number|ptz转动到的y轴|
|callback|IResultCallback|接口回调|

返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

### **5.64,开始3d定位 指定摄像头ID** 

```
startPeer3DPositionByCamId(camId : number,x : number,y : number,callback :
IResultCallback) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|camId|number|摄像头ID|
|x|number|ptz转动的x轴,视频宽度的百分比|
|y|number|ptz转动到的y轴,视频高度的百分比|
|callback|IResultCallback|接口回调|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

### **5.65,获取算法配置** 

```
getAlgorithmEvents() : AlgorithmInfoBean
```

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|AlgorithmInfoBean|算法信息,和算法列表|

### **5.66,设置设备的ap热点密码** 

```
setApPassWd(passwd : string,callback : IResultCallback) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|passwd|string|密码|
|callback|IResultCallback|接口回调|

返回: 

**参数类型 说明** 

ITask 请求任务,可以取消请求 

### **5.67,设置密码提示开关 用户勾选不再提示后,设置为0** 

```
setPromptSetFlag(openFlag : number,callback : IResultCallback) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|openFlag|number|提示开关|
|callback|IResultCallback|接口回调|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

### **5.68,客流统计参数设置** 

```
setHumanCountParam(openFlag : number,interval : number,callback :
IResultCallback) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|openFlag|number|统计开关|
|interval|number|统计间隔|
|callback|IResultCallback|接口回调|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

### **5.69,客流统计参数设置** 

```
setStayParam(openFlag : boolean,stayTime : number,callback : IResultCallback) :
ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|openFlag|boolean|统计开关|
|stayTime|number|逗留时长|
|callback|IResultCallback|接口回调|

返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

### **5.70,获取人流统计** 

```
getHumanCount(fromTime : string,endTime : string,callback : IResultCallback) :
ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|fromTime|string|开始时间2023-04-21 00:00:00|
|endTime|string|结束时间2023-04-21 23:59:59|
|callback|IResultCallback|接口回调|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

### **5.71,设置时间段蜂鸣器开关,** 

```
setTimerBuzzer(openFlag : boolean,callback : IResultCallback) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|openFlag|boolean|蜂鸣器开关|
|callback|IResultCallback|接口回调|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

### **5.72,设置设备蜂鸣器的音量大小** 

```
setVolume(volume : number,callback : IResultCallback) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|volume|number|音量0-100|
|callback|IResultCallback|接口回调|

返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

### **5.73,获取当前设备的动态配置** 

```
getPeerAppSetting() : AppSettingModel
```

##### 返回: 

**参数类型 说明** AppSettingModel 设置信息 

### **5.74,获取设备音量** 

```
getDeviceVolume() : number
```

##### 返回: 

**参数类型 说明** number 设备音量 0-100 

### **5.75,获取设备的报警设置** 

```
getDeviceAlarmParam() : DeviceAlarmParam
```

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|DeviceAlarmParam|设备报警信息|

### **一** **5.76,设置设备的 键报警设置** 

```
setDeviceAlarmParam(param : DeviceAlarmParam,callback : IResultCallback) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|param|DeviceAlarmParam|报警相关信息|
|callback|IResultCallback|接口回调|

返回: 

|**参数类型**|
|---|

|**说明**|
|---|

ITask 请求任务,可以取消请求 

### **一** **5.77,设置 键报警状态** 

```
setOneKeyAlarmStatus(isOpen : boolean,callback : IResultCallback) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|isOpen|boolean|一键报警开关|
|callback|IResultCallback|接口回调|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

### **5.88,获取相机镜头操作相关接口实例** 

```
getCameraApiInstance() : IZJViewerCameraAPI
```

#### **5.88.1,获取指定摄像机镜头信息** 

```
getCamInfo(camId? : number) : CameraBean
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|camId|number|摄像头ID(可空)|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|CameraBean|摄像头信息|

#### **5.88.2,获取全部摄像机镜头信息** 

```
getCamInfos() : Array<CameraBean>
```

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|Array< CameraBean>|摄像头列表信息|

#### **一 一一** **5.88.3,获取支持ptz的镜头信息 默认返回第 个镜头信息,单镜头返回唯 个镜 头信息** 

```
getSupportPtzCameraInfo(isSupportPtz : boolean) : CameraBean
```

**参数类 参数名 说明 型** true:如果多镜头返回支持PTZ的镜头,false: 返回第一个镜头信 isSupportPtz boolean 息 

#### **5.88.4,获取支持变倍的摄像头** 

```
getCameraBean(isZoom : boolean) : CameraBean
```

**参数名 参数类型 说明** isZoom boolean 是否支持变倍 **参数类型 说明** CameraBean 摄像头信息 

返回: 

#### **5.88.5,是否变焦设备状态** 

```
isZoomDevice() : boolean
```

##### 返回: 

**参数类型 说明** boolean 是否支持变倍 

#### **5.88.6,设备变焦镜头的最大焦距** 

```
getMaxFocalLength() : number
```

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|number|最大焦距|

#### **5.88.7,获取多镜头共同配置(共同控制模式) 镜头为共同控制模式时,调用该接口获 取镜头共通配置** 

```
getAllCamConfig() : string
```

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|string|全部的摄像头配置|

#### **5.88.8,获取各镜头独立配置(共同控制模式)** 

```
getSplitCamConfig(camId : number) : string
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|camId|number|摄像头ID|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|string|单个镜头的配置|

#### **5.88.9,获取设备cam总数** 

```
getDeviceCamCount() : number
```

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|number|设备摄像头的数量|

#### **5.88.10,获取设备工作模式** 

```
getDeviceWorkType() : number
```

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|number|0共同控制1独立控制|

#### **5.88.11,获取流ID** 

返回: 

**参数类型** 

##### **说明** 

number 当前的流ID,高清 超清,也是主码流还是次码流 

### **5.89,获取设备分享用户的列表** 

```
getShareUserList() : Array<GroupUserBean>
```

##### 返回: 

**参数类型 说明** Array<GroupUserBean> 设备用户组信息 

### **5.90,设备是否在线** 

```
isDeviceOnline(deviceId : string) : boolean
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|deviceId|string|设备ID|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|boolean|true在线,false离线|

### **5.91,获取变声的类型** 

```
getMutateType() : MutateTypeEnum
```

##### 返回: 

**参数类型 说明** MutateTypeEnum 变声类型枚举 

### **5.92,设置变声类型** 

```
setMutateType(mutateType : MutateTypeEnum) : void
```

**参数名 参数类型 说明** mutateType MutateTypeEnum 变声类型 

**5.93,设置水印** 

```
setCamOSDSwitch(osdType : number,openFlag : boolean ,callback : IResultCallback)
: ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|osdType|number|请求ID|
|openFlag|boolean|水印开关|
|callback|IResultCallback|接口回调|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

### **5.94,获取设备套餐** 

```
getDeviceChargeInfo() : ChargePackageInfo
```

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|ChargePackageInfo|云服务套餐信息|

# **6,云服务套餐** 

### **获取接口实例** 

```
HmSdk.getInstance().newZJViewerCloudPackage()
```

### **6.1,删除缓存套餐** 

```
deleteDeviceCatchCharge:(deviceId: string) => void
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|deviceId|string|设备ID|

**6.2,获取云服务套餐** 

```
getCloudChargePackage : (deviceId: string, resultCallback:
IResultListener<Array<ChargePackageData>> | undefined) => void
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|deviceId|string|设备ID|
|resultCallback|IResultListener<Array< ChargePackageData>>|接口回调|

### **6.3,异步调用获取云服务套餐 子线程调用** 

```
getCloudChargePackageAsync:(deviceId: string)
=>Promise<Array<ChargePackageData>>
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|deviceId|string|设备ID|

返回: 

**参数类型 说明** Promise<Array<ChargePackageData>> Promise返回云套餐数据 

### **6.4,是否购买了鸟类识别服务** 

```
isBirdIdentificationService : (deviceId: string) => boolean
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|deviceId|string|设备ID|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|boolean|true已购买,false未购买|

### **6.5,获取当前生效的全部套餐,包含人脸,鸟类识别等套餐** 

```
getCurrentEffectivePlans : (deviceId: string) => Array<ChargePackageData>
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|deviceId|string|设备ID|

返回: 

**参数类型** 

**说明** 

Array<ChargePackageData> 

|云服务套餐列表|
|---|

### **6.6,获取当前设备的事件套餐,** 

```
getCurrentEventPackage : (deviceId: string) => Array<ChargePackageData>
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|deviceId|string|设备ID|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|Array< ChargePackageData>|云服务套餐列表|

### **6.7,获取全部存储套餐 除了过期套餐** 

```
getAllCloudStorygeChargePackages : (deviceId: string)=> Array<ChargePackageData>
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|deviceId|string|设备ID|
|返回:|||

|**参数类型**|**说明**|
|---|---|
|Array< ChargePackageData>|云服务套餐列表|

### **6.8,请求全部设备的云服务套餐** 

```
queryAllDeviceChargePackages : (devicesList: Array<Device>) => Promise<void>
```

**参数名 参数类型 说明** devicesList Array<Device> 设备列表 

### **6.9,获取当前设备的全天存储套餐** 

```
getCurrentAllDayPackage : (deviceId: string) => Array<ChargePackageData>
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|deviceId|string|设备ID|

返回: 

**参数类型** 

**说明** 

Array<ChargePackageData> 

云服务套餐列表 

### **6.10,获取当前正在使用套餐的ID** 

```
getCurChargePackageID : (deviceId: string) => number
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|deviceId|string|设备ID|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|number|当前使用的套餐ID|

### **6.11,是否有人脸识别套餐** 

```
isFaceCharge : (deviceId: string) => boolean
```

|**参数名**||**参数类型**|**说明**|
|---|---|---|---|
|deviceId||string|设备ID|
|返回:||||
|**参数类型**|**说明**|||
|boolean|true有|人脸套餐,false没有人脸套餐||

### **6.12,获取套餐状态** 

```
getCloudPackageStatus : (packageType : CloudChargeTypeEnum,deviceId : string) =>
CargePackageStatusEnum
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|packageType|CloudChargeTypeEnum|套餐类型|
|deviceId|string|设备ID|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|CargePackageStatusEnum|套餐状态|

**6.13,获取指定设备当前的所有套餐** 

```
getCurrentCloudPackage : (deviceId : string) => Array<ChargePackageData>
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|deviceId|string|设备ID|

##### 返回: 

**参数类型 说明** Array<ChargePackageData> 云服务套餐列表 

### **6.14,获取正在使用的人脸套餐** 

```
getFaceCharge : (deviceId: string) => ChargePackageData | null
```

**参数名 参数类型 说明** deviceId string 设备ID 

返回: 

**参数类型 说明** ChargePackageData 云服务套餐 

### **6.15,获取全部的ai套餐** 

```
getFaceCharges : (deviceId: string) => Array<ChargePackageData>
```

**参数名 参数类型 说明** deviceId string 设备ID 

返回: 

**参数类型 说明** Array<ChargePackageData> 云服务套餐列表 

### **6.16,是否购买了套餐 除了AI云服务** 

```
isPaidCloudService : (deviceId: string) => boolean
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|deviceId|string|设备ID|

返回: 

|**参数类型**|**说明**|
|---|---|
|boolean|除ai套餐外是否购买了其它套餐|

### **6.17,获取当前生效的存储套餐** 

```
getCurEffectCloudStorygePackage : (deviceId: string) => Array<ChargePackageData>
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|deviceId|string|设备ID|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|Array< ChargePackageData>|云服务套餐列表|

### **6.18,获取对应设备ID的套餐** 

```
getChargePackages : (deviceId: string, isFilterExpiredPackages: boolean) =>
Array<ChargePackageData>
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|deviceId|string|设备ID|
|isFilterExpiredPackages|boolean|是否过滤过期套餐|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|Array< ChargePackageData>|云服务套餐列表|

### **6.19,获取当前的自动订阅套餐** 

```
getAutomaticRenewalPackages : (deviceId: string) => ArrayList<ChargePackageData>
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|deviceId|string|设备ID|
|返回:|||

|**参数类型**|**说明**|
|---|---|
|Array< ChargePackageData>|云服务套餐列表|

**6.20,获取短信套餐** 

```
getSMSPackage : (callback: IGetSMSPackageCallback) => ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|callback|IGetSMSPackageCallback|回调接口|

### **6.21,获取4G套餐** 

```
get4GPackage : (deviceId: string, callback: I4GChargePackageCallback) => ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|deviceId|string|设备ID|
|callback|I4GChargePackageCallback|接口回调|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

### **6.22,获取用户的全部套餐** 

```
getOwnerChargePackages : (callback: IChargePackageCallback) => ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|callback|IChargePackageCallback|接口回调|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

### **6.23,获取设备套餐循环天数** 

```
getDeviceChargeDay(deviceId : string) : number
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|deviceId|string|设备ID|

返回: 

##### **参数类型** 

**说明** 

number 获取套餐是多少天循环的 

### **6.24,获取时光相册开通状态** 

```
getAlbumStatus(deviceId : string) : AlbumStatusEnum
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|deviceId|string|设备ID|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|AlbumStatusEnum|时光相册开通状态|

### **6.25,获取时光相册云套餐** 

```
getAlbumCharges(deviceId : string): Promise<Array<ChargePackageData>>
```

**参数名 参数类型 说明** deviceId string 设备ID 返回: 

**参数类型 说明** Promise<Array<ChargePackageData>> 云服务套餐数列表 

### **6.26,获取开通的事件服务** 

```
getEventServiceTypeList(deviceId : string) : Array<EventServiceTypeBean>
```

|**参数名**|**参数类型**||**说明**|
|---|---|---|---|
|deviceId|string||设备ID|
|返回:||||
|**参数类型**||**说明**||
|Array< EventServiceTypeBean>||事件服|务类型的数据|

# **7,旧设备相关接口** 

### **获取接口实例** 

```
HmSdk.getInstance().newZJViewerOldDevice()
```

### **7.1,是否是旧设备** 

```
isOldDevice :(deviceId : string) => boolean
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|deviceId|string|设备ID|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|boolean|是否旧设备 ,true旧设备,false不是旧设备|

### **7.2,设置内置IOT** 

```
setInnerDacTimer :(deviceId : string,dacOption :InnerDACOption,callback :
IResultCallback) =>void
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|deviceId|string|设备ID|
|dacOption|InnerDACOption|内置IOt信息|
|callback|IResultCallback|接口回调|

### **7.3,设置时间录像信息** 

```
setTimeRecordInfo(deviceId : string,infots : Array<ScheduleInfo>,callback :
IResultCallback) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|deviceId|string|设备ID|
|infots|Array< ScheduleInfo>|时间段信息列表|
|callback|IResultCallback|接口回调|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

**8,图片下载,获取图片列表** 

### **获取接口实例** 

```
HmSdk.getInstance().newZJViewerImageInstance(deviceId : string)
```

### **一** **8.1,获取 张实时视频图片** 

```
getLiveStreamImage(picType : PictureTypeEnum,callback : ILiveImageCallback) :
ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|picType|PictureTypeEnum|图片大小|
|callback|ILiveImageCallback|接口回调|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|
|**参数名8.2,查询设** `getLocalImag` `IImageCalend`|**参数类型说明备端图片日历** `eCalendar(fromDay : string,endDay : string,callback :` `arCallback) : ITask`|
|fromDay|string 开始时间yyyy-MM-dd|
|endDay|string 结束时间yyyy-MM-dd|
|callback|IImageCalendarCallback 接口回调|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

### **8.3,查询设备端图片列表** 

```
getLocalImageList(snapType : SnapTypeEnum,fromTime : string,pageNum :
number,callback : IImageListCallback) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|snapType|SnapTypeEnum|图片类型|
|fromTime|string|开始时间,格式:yyyy-MM-dd HH:mm:ss|
|pageNum|number|每次查询数目,不超过60|
|callback|IImageListCallback|接口回调|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

### **一** **8.4,下载 张设备端图片** 

```
downloadLocalImage(imageName : string,callback : IImageLocalCallback) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|imageName|string|图片名称|
|callback|IImageLocalCallback|回调接口|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

### **8.5,查询云端图片日历** 

```
getCloudImageCalendar(fromDay : string,callback : IImageCalendarCallback) :
ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|fromDay|string|开始日期,格式:yyyy-MM-dd|
|callback|IImageCalendarCallback|接口回调|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

**8.6,查询云端图片列表** 

```
getCloudImageList(day : string,callback : IImageListCallback) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|day|string|查询日期,格式:yyyy-MM-dd|
|callback|IImageListCallback|接口回调|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

### **一** **8.7,下载 张云端图片** 

```
downloadCloudImage(imageName : string,imageTime : string,callback :
IImageCloudCallback) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|imageName|string|图片名称|
|imageTime|string|图片时间|
|callback|IImageCloudCallback|接口回调|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

### **8.9,通过FileID下载图片** 

```
downloadImageByFileId(fileId : string,callback : IImageLocalCallback) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|fileId|string|文件Id,只有上传到云端的图片才有文件ID|
|callback|IImageLocalCallback|接口回调|

# **9,时光相册** 

### **获取接口实例** 

```
HmSdk.getInstance().newHMViewerAlbum(deviceId : string)
```

### **9.1,获取相册分类列表** 

```
getAlbumClassifyList(): Promise<AlbumTabInfo[]>
```

##### 返回: 

**参数类型 说明** Promise<Array<AlbumTabInfo>> 相册类型列表 

### **9.2,获取时光相册支付套餐列表** 

```
getAlbumPayList() : Promise<Array<PayInfoBean>>
```

##### 返回: 

**参数类型 说明** Promise<Array<PayInfoBean>> 时光相册购买套餐列表 

### **9.3,获取相册服务信息列表** 

```
getAlbumServiceInfoList() : Promise<Array<AiAlbumServiceInfo>>
```

##### 返回: 

**参数类型 说明** Promise<Array<AiAlbumServiceInfo>> 时光相册服务信息列表 

### **9.4,获取离过期日期最远的套餐** 

```
getLastPackage() : Promise<ChargePackageData | undefined>
```

##### 返回: 

**参数类型 说明** Promise<ChargePackageData> 套餐数据 

**9.5,获取时光相册有数据的日历** 

```
getAlbumCalendar(startDate : string,endDate : string,albumType :
AlbumTypeEnum,callback : IRecordCalendarCallback): ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|startDate|string|开始时间:2025-01-02|
|endDate|string|结束时间:2025-01-20|
|albumType|AlbumTypeEnum|时光相册的类型|
|callback|IRecordCalendarCallback|接口回调|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

### **9.6,获取时光相册列表** 

```
getAlbumList(fromDate:string,
  albumType: AlbumTypeEnum,
  needPicNum: number,
  sortType: SortTypeEnum,
  pageNo: number,
  pageSize: number,
  callback: IGetAlbumVideoListCallback) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|fromDate|string|开始查询的日期,从什么日期开始查|
|albumType|AlbumTypeEnum|相册类型|
|needPicNum|number|获取图片的数量|
|sortType|SortTypeEnum|0:正序,1:倒序|
|pageNo|number|页码|
|pageSize|number|页的数量|
|callback|IGetAlbumVideoListCallback|接口回调|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

**9.7,获取相册图片列表** 

```
getAlbumPicList(
  startDay: string,
  albumType: AlbumTypeEnum,
  sortType: SortTypeEnum,
  pageNo: number,
  pageSize: number,
  callback: IGetAlbumPicListCallback) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|startDay|string|查询日期:2024-01-01|
|albumType|AlbumTypeEnum|相册类型|
|sortType|SortTypeEnum|0:正序,1:倒序|
|pageNo|number|页码|
|pageSize|number|每一页的数量|
|callback|IGetAlbumPicListCallback|接口回调|

返回: 

|**参数类型说明**|
|---|
|ITask 请求任务,可以取消请求|
|**参数名参数类型说明9.8,删除时光相册视频** `deleteAlbum(` `type: number,` `startDay: string,` `albumFileList: Array<string>,` `callback: IResultCallback` `) : ITask`|
|type number 0:删除指定文件2:删除指定日期|
|startDay string 要删除的日期2024-01-01|
|albumFileList Array 要删除的相册文件列表|
|callback IResultCallback 接口回调|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

**一** **9.9,删除 天的时光相册视频** 

```
deleteAlbumByDate(
  startDay: string,
  callback: IResultCallback
) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|startDay|string|要删除的日期2024-01-01|
|callback|IResultCallback|接口回调|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

### **9.10,删除文件列表时光相册视频** 

```
deleteAlbumByFileList(
  startTime : string,
  albumFileList: Array<string>,
  callback: IResultCallback
) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|startTime|string|开始时间|
|albumFileList|Array|需要删除的问题列表|
|callback|IResultCallback|接口回调|

### **9.11,获取时光相册设置实体** 

```
newSettingInstance() : AlbumSettingEntity
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|isSupportMotion|boolean|是否支持移动侦测|
|isSupportHuman|boolean|是否支持人形侦测|
|isOpenMotion|boolean|移动侦测开关|
|isOpenHuman|boolean|人形侦测开关|

**9.11.1,获取时间段开关状态** 

```
getTimerSwitchStatu() : boolean
```

##### 返回: 

**参数类型 说明** boolean 时间段开关状态 

#### **9.11.2,获取抓拍间隔** 

```
getCaptureInterval(): number
```

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|number|相册图片抓拍间隔|

#### **9.11.3,格式化时间** 

```
getFormatTimerPlicy(): string
```

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|string|返回抓图的时间段13:02-13:03|

#### **9.11.4,获取开始时间的秒** 

```
getStartTime() : number
```

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|number|开始时间的秒|

#### **9.11.5,获取结束时间段** 

```
getEndTime() : number
```

##### 返回: 

|**参数类型** number|
|---|

|**说明** 结束时间的秒|
|---|

**9.11.6,获取周几掩码** 

```
getWeekFlag() : number
```

##### 返回: 

**参数类 说明 型** 周几的掩码 星期一: 0x01 星期二: 0x02 星期三: 0x04 星期四: 0x08 星期五: number 0x010 星期六: 0x020 星期日: 0x040 全部:0x7F 

#### **9.11.7,设置侦测开关状态** 

```
setAlarmSwitchStatus(isOn : boolean,eventType : EventTypeIDEnum) : Promise<void>
```

|**参数名**|**参数类型说明**|
|---|---|
|isOn|boolean 开关|
|eventType|EventTypeIDEnum 事件类型|

返回: 

|**参数类型**|**说明**|
|---|---|
|Promise|异步回调|

#### **9.11.8,设置时间段开关状态** 

```
setTimerSwitchStatus(isOn: boolean) : Promise<void>
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|isOn|boolean|开关|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|Promise|异步回调|

#### **9.11.9,获取相册视频模式** 

```
getAlbumMode() : TimeAlbumModeEnum
```

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|TimeAlbumModeEnum|时光相册模式枚举|

**9.11.10,保存截图间隔** 

```
saveInterval(interval : number): Promise<void>
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|interval|number|间隔 单位秒|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|Promise|异步回调|

#### **9.11.11,保存相册视频模式** 

```
saveAlbumMode(mode : TimeAlbumModeEnum) : Promise<void>
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|mode|TimeAlbumModeEnum|相册视频模式|

##### 返回: 

**参数类型 说明** Promise 异步回调 

#### **9.11.12,保存相册视频时间段** 

```
saveAlbumVideoTime(timeBean : AlarmTimeBean) : Promise<void>
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|timeBean|AlarmTimeBean|时间段信息|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|Promise|异步回调|

# **10,提示音** 

### **获取接口实例** 

```
HmSdk.getInstance().newZJViewerSoundInstance(deviceId : string)
```

### **10.1,上传云音频文件** 

```
uploadSoundFile(soundFilePath : string,soundType : SoundTypeEnum,callback :
IUploadFileCallback) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|soundFilePath|string|音频文件绝对路径|
|soundType|SoundTypeEnum|文件类型|
|callback|IUploadFileCallback|接口回调|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

### **10.2,查询云音频列表** 

```
getCloudSoundList(callback : IGetSoundListCallback) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|callback|IGetSoundListCallback|接口回调|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

### **10.3,删除云音频文件** 

```
delCloudSoundFile(soundList : Array<RingFileBn>,callback : IResultCallback) :
ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|soundList|Array< RingFileBn>|需要删除的音频列表|
|callback|IResultCallback|接口回调|

返回: 

**参数类型** 

**说明** 

ITask 请求任务,可以取消请求 

### **10.4,更改云音频信息** 

```
modifyCloudSoundInfo(fileId : string,newName : string,callback : IResultCallback)
: ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|fileId|string|文件id|
|newName|string|件名称|
|callback|IResultCallback|接口回调|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

### **10.5,通知设备下载音频** 

```
noticeDevDownloadSound(fileId : string,callback : IResultCallback) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|fileId|string|文件id|
|callback|IResultCallback|接口回调|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

### **10.6,通知平台生成文字转语音** 

```
turnTextToVoice(voiceType : string,voiceText : string,callback :
IGetSoundListCallback) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|voiceType|string|语音类型|
|voiceText|string|语音文本|
|callback|IGetSoundListCallback|接口回调|

返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

# **11,设备时间段策略** 

### **获取接口实例** 

```
HmSdk.getInstance().newZJViewerDeviceTimePolicy(deviceId : string)
```

### **11.1,创建录像时间段策略** 

##### 这个接口只有第一次添加设备设置录像时间段的时候需要 

```
createTimerRecordPolicy(recordTypeTime? : RecordTypeTimeEnum,param? :
TimePolicyParam) : TimeRecordPolicy
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|recordTypeTime|RecordTypeTimeEnum|策略类型,卡录像和云录像,还是全部都统一控 制|
|param|TimePolicyParam|策略时间段|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|TimeRecordPolicy|录像时间段策略|

### **11.2,创建默认的时间段策略** 

```
createDefalutTimerPolicy(timePolicyType : RecordTypeTimeEnum,timePolicyId :
TimerPolicyTypeEnum) :TimePolicyBean
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|timePolicyType|RecordTypeTimeEnum|策略类型,卡录像和云录像,还是全部都统一控 制|
|timePolicyId|TimerPolicyTypeEnum|时间段类型,是控制什么功能的时间段|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|TimePolicyBean|录像时间段策略|

**11.3,设置定时策略** 

```
setTimerPolicy(timePolicy : TimePolicyBean,callback : IResultCallback) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|timePolicy|TimePolicyBean|时间段策略信息|
|callback|IResultCallback|接口回调|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

### **11.4,获取定时策略列表** 

```
getTimePolicyInfo() : Array<TimePolicyBean>
```

##### 返回: 

**参数类型 说明** Array<TimePolicyBean> 时间段策略列表,包含全部时间段策略 

### **11.5,删除定时策略** 

```
deleteTimerPolicy(timePolicyId : TimerPolicyTypeEnum | number,callback :
IResultCallback) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|timePolicyId|TimerPolicyTypeEnum|策略ID,控制什么功能的策略|
|callback|IResultCallback|接口回调|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

# **12,NVR设备** 

**获取接口实例** 

```
HmSdk.getInstance().newZJViewerNvrDevice(deviceId : string)
```

### **12.1,搜索NVR子设备接口** 

```
searchNVRSubDevice(durationSec: number, callback: INVRSearchSubDevCallback):
ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|durationSec|number|搜索时间|
|callback|INVRSearchSubDevCallback|接口回调|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

### **12.2,绑定NVR子设备** 

```
bindNVRChannels(channelList: ArrayList<NvrChannelPairBean>,callback:
INVRBindSubDevCallback): ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|channelList|number|通道列表|
|callback|INVRBindSubDevCallback|接口回调|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

### **12.3,设置存储配置** 

```
setPeerStorage(storage: NvrStorageBean, callback: IResultCallback): ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|storage|NvrStorageBean|存储信息配置|
|callback|IResultCallback|接口回调|

返回: 

##### **参数类型** 

|**说明**|
|---|

|ITask|请求任务,可以取消请求|
|---|---|

### **12.4,获取存储配置** 

```
getNvrStorage() : NvrStorageBean
```

##### 返回: 

##### **参数类型** 

##### **说明** 

NvrStorageBean 

存储配置信息 

### **12.5,获取子设备状态及信息** 

```
getSubDeviceInfos() : Array<NvrSubDevInfoBean>
```

##### 返回: 

##### **参数类型** 

##### **说明** 

Array<NvrSubDevInfoBean> nvr子设备列表信息 

### **12.6,获取子设备状态及信息** 

```
getSubDeviceInfo() : NvrSubDevInfoBean| undefined
```

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|NvrSubDevInfoBean|子设备信息|

### **12.7,忽略提示信息** 

```
setNVRIngnorePrompt(enType : number) : number
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|enType|number|1磁盘空间不足提示|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|number|0成功,其它失败|

**12.8,获取通道配置信息** 

```
getNvrChannelConfig() : NvrChannelConfigBean
```

返回: 

|**参数类型**|**说明**|
|---|---|
|NvrChannelConfigBean|nvr通道配置|

### **12.9,解除通道绑定** 

```
unbindNVRChannels(channelId : number, callback: IResultCallback) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|channelId|number|通道ID|
|callback|IResultCallback|接口回调|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

### **12.10,交换通道** 

```
exchangeChannel(channelA : number,channelB : number,callback : IResultCallback) :
ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|channelA|number|通道A|
|channelB|number|通道B|
|callback|IResultCallback|接口回调|

# **13,音视频媒体流** 

# **14,设备组管理** 

说明:每个设备都有一个组,添加设备就是把这个设备的ID添加到组里,简称入组,groupID 就是这个 组ID 

### **获取接口实例** 

```
HmSdk.getInstance().newZJViewerGroup()
```

### **14.1,创建组** 

```
createGroup (groupName : string,groupDesc : Map<string,string>| null,callback :
ICreateGroupCallback) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|groupName|string|组名称|
|groupDesc|Map<string,string> | null|组的详情|
|callback|ICreateGroupCallback|接口回调|

### **14.2,创建子组** 

```
createChildGroup (parentGid : string,groupName : string,groupDesc :
Map<string,string>,callback : ICreateGroupCallback) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|parentGid|string|父组ID|
|groupName|string|组名称|
|groupDesc|Map<string,string>|组说明|
|callback|ICreateGroupCallback|接口回调|

### **14.3,获取组列表** 

```
getGroupList () : Array<GroupBean>
```

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|Array< GroupBean>|组详情列表|

### **14.4,通过groupId获取groupToken** 

```
getGroupToken (groupId : string) : string
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|groupId|string|要查询的组ID|

##### 返回: 

**参数类型 说明** string 组Token 

### **14.5,用deviceId查找groupId** 

```
getGroupIdByDID (deviceId : string) : string
```

**参数名 参数类型 说明** deviceId string 设备ID 

返回: 

**参数类型 说明** string 组ID 

### **14.6,获取组Bean** 

getGroupBean (groupId : string) : GroupBean
参数名 参数类型 说明
groupId string 组ID
返回:
参数类型 说明
GroupBean 对应的组信息

### **14.7,更新组信息** 

```
updateGroup (groupId : string,groupName : string,groupDesc :
HashMap<string,string>,callback : IResultCallback) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|groupId|string|组ID|
|groupName|string|组名称|
|groupDesc|HashMap<string,string>|组描述|
|callback|IResultCallback|接口回调|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

### **14.8,删除组** 

```
deleteGroup (groupId : string,callback : IResultCallback): ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|groupId|string|组ID|
|callback|IResultCallback|接口回调|

返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

### **14.9,创建角色** 

```
createOrModifyRole (groupId : string,roleId : string,groupRight :
GroupRightEnum,deviceRight : string,callback : IResultCallback) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|groupId|string|组ID|
|roleId|string|角色ID|
|groupRight|GroupRightEnum|组权限|
|deviceRight|string|设备权限|
|callback|IResultCallback|接口回调|

返回: 

**参数类型** 

**说明** 

ITask 

请求任务,可以取消请求 

### **14.10,删除角色** 

```
deleteRole(groupId : string,roleId : string,callback : IResultCallback) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|groupId|string|组ID|
|roleId|string|角色ID|
|callback|IResultCallback|接口回调|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

### **14.11,通过UserID邀请用户加入组** 

```
inviteUserByUserId(groupId : string,userId : string,roleId : string,callback :
IResultCallback) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|groupId|string|组ID|
|userId|string|用户ID|
|roleId|string|角色ID|
|callback|IResultCallback|接口回调|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

### **14.12,删除用户** 

```
removeUser(groupId : string,userId : string,callback : IResultCallback) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|groupId|string|组ID|
|userId|string|用户ID|
|callback|IResultCallback|接口回调|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

# **15,消息事件** 

### **获取接口实例** 

```
HmSdk.getInstance().newZJViewerMessage()
```

### **15.1,查询设备端消息日历** 

```
getLocalEventCalender(deviceId : string,callback :
IEventCalendarCallback,fromDay? : string,endDay? : string) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|deviceId|string|设备ID|
|callback|IEventCalendarCallback|接口回调|
|fromDay|string|开始日期,格式:yyyy-MM-dd|
|endDay|string|结束日期,格式:yyyy-MM-dd|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

### **15.2,查询设备端消息列表** 

```
getLocalEventListPromise(deviceId : string,day : string,eventTypeIDEnum :
EventTypeIDEnum) : Promise<Array<MessageBean>>
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|deviceId|string|设备ID|
|day|string|查询日期,格式:yyyy-MM-dd|
|eventTypeIDEnum|EventTypeIDEnum|事件类型|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|Promise<Array< MessageBean>>|异步回调,返回消息事件列表|

### **15.3,查询云端消息日历** 

```
getCloudEventCalender(deviceId : string,callback:
IEventCalendarCallback,fromDay?: string) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|deviceId|string|设备ID|
|callback|IEventCalendarCallback|接口回调|
|fromDay|string|开始日期,格式:yyyy-MM-dd|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

### **15.4,查询云端消息列表** 

```
getCloudEventListByPromise(deviceId : string,day : string,eventTypeIDEnum :
EventTypeIDEnum) : Promise<Array<MessageBean>>
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|deviceId|string|设备ID|
|day|string|查询日期,格式:yyyy-MM-dd|
|eventTypeIDEnum|EventTypeIDEnum|事件类型|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|Promise<Array< MessageBean>>|异步回调返回消息列表|

**15.5,设置云端消息** 

```
setCloudEventInfo(eventBean : MessageBean,callback : IResultCallback) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|eventBean|MessageBean|事件信息|
|callback|IResultCallback|接口回调|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

### **15.6,设置云端消息** 

```
setCloudEventMessage(deviceId : string,day : string,eventList :
Array<EventBean>,callback : IResultCallback) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|deviceId|string|设备ID|
|day|string|日期,格式:yyyy-MM-dd|
|eventList|Array< EventBean>|消息列表|
|callback|IResultCallback|接口回调|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

### **15.7,根据条件获取全部设备的云事件** 

```
getCloudEventList(day: string,deviceId? : string,eventType?:
EventTypeIDEnum,deviceType? : FindEventDeviceTypeEnum ) :
Promise<Array<MessageBean>>
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|day|string|需要查询的日期 格式:yyyy-MM-dd|
|deviceId|string|需要返回的设备事件,如果设备ID要传则 eventType必须传|
|eventType|EventTypeIDEnum|需要查询的事件类型,不传则返回全部事件 或者 传EventTypeIDEnum.ALL返回全部事件 如果需 要返回deviceId的事件则eventType必须要传|
|deviceType|FindEventDeviceTypeEnum|设备类型,目前分三种,摄像头,网关,nvr, 如果要查询多种 可以用或'|'传递|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|Promise<Array< MessageBean>>|异步回调,返回事件列表|

### **15.8,获取事件消息详情** 

```
getEventDetailsList(eventBean: MessageBean): Promise<Array<EventDetailsBean>>
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|eventBean|MessageBean|消息事件信息|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|Promise<Array< EventDetailsBean>>|异步回调,返回事件详情|

### **15.9,删除云事件** 

```
deleteCloudEvent(deviceid : string,optionType : number,day : string,eventList :
Array<EventBean>) : Promise<void>
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|deviceid|string|设备ID|
|optionType|number|0:删除事件;1:删除全部2:按天删除|
|day|string|yyyy-MM-dd|
|eventList|Array< MessageBean>|事件列表|

返回: 

**参数类型** 

**说明** 

Promise 异步回调 

# **16,视频录像** 

### **获取接口实例** 

```
HmSdk.getInstance().newZJViewerRecord(deviceId : string)
```

### **16.1,查询设备端录像日历** 

```
getLocalRecordCalendar(fromDay : string,endDay : string,callback :
IRecordCalendarCallback) : ITask
```

|**参数名**|**参数类型**|**说明**||
|---|---|---|---|
|fromDay|string|开始日期,|格式:yyyy-MM-dd|
|endDay|string|结束日期,|格式:yyyy-MM-dd|
|callback|IRecordCalendarCallback|接口回调||

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

### **16.2,查询设备端录像列表** 

```
getLocalRecordList(startTime : string,pageNum : number,callback :
IRecordListCallback) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|startTime|string||
|pageNum|number||
|callback|IRecordListCallback||

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

**16.3,查询云端录像日历数据** 

```
getCloudRecordCalendar(fromDay : string,callback : IRecordCalendarCallback) :
ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|fromDay|string|开始日期,格式:yyyy-MM-dd|
|callback|IRecordCalendarCallback|接口回调|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

### **16.4,查询云端录像列表** 

```
getCloudRecordList(day : string,callback : IRecordListCallback) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|day|string|查询日期,格式:yyyy-MM-dd|
|callback|IRecordListCallback|接口回调|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

### **16.5,下载事件列表卡录像或云录像** 

```
downloadVideoByMessageList(isCloudVideo: boolean, messages: Array<MessageBean>,
  onDownloadProgress: (progress: number) => void): Promise<string>
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|isCloudVideo|boolean|是否云录像|
|messages|Array< MessageBean>|消息列表|
|onDownloadProgress|(progress: number) => void|回调下载进度函数|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|Promise|异步回调,返回下载视频的本地路径|

**16.6,回看录像下载,** 

```
downloadVideo(isCloudVideo: boolean,createTime : string,endTime :
string,onDownloadProgress : (progress : number) => void) : Promise<string>
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|isCloudVideo|boolean|是否云视频|
|createTime|string|开始时间|
|endTime|string|结束时间|
|onDownloadProgress|(progress : number) => void|进度回调,进度100也可以当作成功回 调|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|Promise|异步回调,返回下载视频的本地路径|

```
downloadRecordEx(createTime : string,endTime : string,cameraId :
number,onDownloadProgress : (progress : number) => void) : Promise<string>
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|createTime|string|开始时间|
|endTime|string|结束时间|
|cameraId|number|摄像头ID|
|onDownloadProgress|(progress : number) => void|进度回调,进度100也可以当作成功回 调|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|Promise|异步回调,返回下载视频的本地路径|

### **16.7,取消请求** 

```
cancelRequest()  : void
```

### **16.8,保存录像时间段** 

```
saveRecordTimePolicy(times : Array<TimePolicyBean>) : Promise<void>
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|times|Array< TimePolicyBean>|时间段列表|

返回: 

|**参数类型**|**说明**|
|---|---|
|Promise|异步回调|

### **16.9,获取录像时间段** 

```
getRecordTimePolicy(recordTypeTime: RecordTypeTimeEnum) : Array<TimePolicyBean>
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|recordTypeTime|RecordTypeTimeEnum|录像时间段类型|

##### 返回: 

**参数类型 说明** Array<TimePolicyBean> 时间段列表 

### **16.10,录像时间段是否开启** 

```
isTimingRecordOpen(recordType : RecordTypeTimeEnum) : boolean
```

**参数名 参数类型 说明** recordType RecordTypeTimeEnum 录像时间段类型 **参数类型 说明** boolean true 时间段打开 false时间段关闭 

##### 返回: 

### **16.11,获取云录像购买套餐** 

```
getCloudRecordPayPackage() : Promise<RecordingPackageInfo>
```

##### 返回: 

**参数类型 说明** Promise<RecordingPackageInfo> 异步返回购买录像套餐信息 

**17,设备报警** 

### **获取接口实例** 

```
HmSdk.getInstance().newZJViewerAlarmPolicy(deviceId : string)
```

### **17.1,设置报警策略** 

```
setAlarmPolicy(alarmPolicy : AlarmPolicyBean,callback : IResultCallback) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|alarmPolicy|AlarmPolicyBean|报警策略|
|callback|IResultCallback|回调接口|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

### **17.2,删除报警策略** 

```
deleteAlarmPolicy(iotType : AIIoTTypeEnum,iotId : number,callback :
IResultCallback) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|iotType|AIIoTTypeEnum|iot类型,触发源类型|
|iotId|number|iot设备ID,也可以是内置功能id|
|callback|IResultCallback|接口回调|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

### **17.3,添加监测报警区域** 

```
addFenceMonitorAlarm(fancePoints : Array<FencePointBean>,direction :
FenceDetectAbilityEnum , callback : IModifyfenceResult) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|fancePoints|Array< FencePointBean>|区域数组|
|direction|FenceDetectAbilityEnum|电子围栏绘制模式|
|callback|IModifyfenceResult|接口回调|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

### **17.4,删除监测报警区域** 

```
delFenceMonitorAlarm(fanceInfos : Array<FenceInfoBean>,callback :
IResultCallback) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|fanceInfos|Array< FenceInfoBean>|区域数组|
|callback|IResultCallback|接口回调|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

### **17.5,修改监测报警区域坐标** 

```
changeFenceCoordinate(regionId : number,direction :
FenceDetectAbilityEnum,fancePoints : Array<FencePointBean>,callback :
IResultCallback) :ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|regionId|number|区域ID|
|direction|FenceDetectAbilityEnum|电子围栏检测模式|
|fancePoints|Array< FencePointBean>|区域数组|
|callback|IResultCallback|接口回调|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

**17.6,获取区域监测区域坐标信息** 

```
getFenceInfo() : FenceBean
```

##### 返回: 

**参数类型 说明** FenceBean 区域配置信息 

# **18,设备OTA** 

### **获取接口实例** 

```
HmSdk.getInstance().newZJViewerOtaInstance(deviceId : string)
```

### **18.1,检查版本号** 

```
checkVersion(callback : ICheckVersionCallback) : ITask
```

**参数名 参数类型 说明** callback ICheckVersionCallback 接口回调 

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

### **18.2,开始升级** 

```
startUpgrade(callback : IResultCallback) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|callback|IResultCallback|接口回调|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

**18.3,停止升级** 

```
stopUpgrade(callback : IResultCallback) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|callback|IResultCallback|接口回调|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

### **18.4,设置设备自动升级** 

```
setDeviceAutoUpgrade(autoFlag : boolean,weekFlag : number,time : number,callback
: IResultCallback) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|autoFlag|boolean|是否自动升级|
|weekFlag|number|星期一:0x01星期二:0x02星期三:0x04星期四:0x08 星期五:0x010星期六:0x020星期日:0x040全部:0x7F|
|time|number|距离0点的时间,单位:秒|
|callback|IResultCallback|接口回调|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

# **19,设备IOT** 

### **获取接口实例** 

```
HmSdk.getInstance().newZJViewerIot(deviceId : string)
```

### **19.1,添加433设备以及外置设备** 

```
addHubAIIotDevice (iotType : number , iotId : number,callback :
IResultListener<HubIoTInfo>) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|iotType|number( AIIoTTypeEnum)|功能类型|
|iotId|number|功能id|
|callback|IResultListener< HubIoTInfo>||

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

### **一** **19.2,删除 个外置IOT设备** 

```
removeHubAiIotHub (iotType : AIIoTTypeEnum,iotId : number,callback :
IResultCallback) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|iotType|AIIoTTypeEnum|iot设备类型|
|iotId|number|iot设备ID|
|callback|IResultCallback|接口回调|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

### **19.3,删除设备的全部外置Iot** 

```
removeAllAIIoTFromHub (callback : IResultCallback) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|callback|IResultCallback|接口回调|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

**19.4,iot开关设置** 

```
setAIIoTOpenFlagInHub (iotType : AIIoTTypeEnum,iotId : number,openFlag :
boolean,callback : IResultCallback) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|iotType|AIIoTTypeEnum|iot设备类型|
|iotId|number|iot设备ID|
|openFlag|boolean|开关状态|
|callback|IResultCallback|接口回调|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

### **19.5,设置Iot名称** 

```
setAIIoTNameInHub (iotType : AIIoTTypeEnum,iotId : number,iotName :
string,callback : IResultCallback) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|iotType|AIIoTTypeEnum|iot设备类型|
|iotId|number|iot设备ID|
|iotName|string|iot名称|
|callback|IResultCallback|接口回调|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

### **19.6,设置IOT联动策略** 

```
setAIIoTPropInHub (iotType : AIIoTTypeEnum,iotId : number,ioTProp :
string,callback : IResultCallback) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|iotType|AIIoTTypeEnum|iot设备类型|
|iotId|number|iot设备ID|
|ioTProp|string|iot联动策略|
|callback|IResultCallback|接口回调|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

### **19.7,设置IOT联动策略** 

```
setAIIoTPropInHub1 (iotType : AIIoTTypeEnum,iotId : number,ioTProp :
Map<string,string>,callback : IResultCallback) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|iotType|AIIoTTypeEnum|iot设备类型|
|iotId|number|iot设备Id|
|ioTProp|Map<string,string>|iot联动策略|
|callback|IResultCallback|接口回调|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

### **19.8,获取设备的全部Iot开关状态** 

```
getAIIoTStatus (callback : IAIIoTStatusCallback) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|callback|IAIIoTStatusCallback|接口回调|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

**19.9,设置内置Iot开关** 

```
setInIoTOpenFlag (iotType : AIIoTTypeEnum,iotId : number,openFlag :
boolean,callback : IResultCallback) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|iotType|AIIoTTypeEnum|内置iot类型|
|iotId|number|内置iotID|
|openFlag|boolean|内置iot开关状态|
|callback|IResultCallback|接口回调|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

### **19.10,设置内置Iot联动策略** 

```
setInIoTProp (iotType : AIIoTTypeEnum,iotId : number,iotProp : string,callback :
IResultCallback) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|iotType|AIIoTTypeEnum|内置iot类型枚举|
|iotId|number|内置IOt唯一标识|
|iotProp|string|要设置的策略|
|callback|IResultCallback|接口回调|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

### **19.11,设置内置Iot的提示音** 

```
setInIoTBuss (iotType : AIIoTTypeEnum,iotId : number,iotBuss : string,callback :
IResultCallback) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|iotType|AIIoTTypeEnum|内置Iot的类型枚举|
|iotId|number|内置Iot的唯一标识|
|iotBuss|string|设置的内置iot的提示音策略|
|callback|IResultCallback|回调|

返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

### **19.12,设置inIot 开关** 

```
ctrlAIIotDevice (iotType : AIIoTTypeEnum,iotId : number,isOpen : boolean,callback
: IResultCallback) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|iotType|AIIoTTypeEnum|内置IOT类型|
|iotId|number|内置IOTID|
|isOpen|boolean|开关是否打开|
|callback|IResultCallback|接口回调|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

### **19.13,创建Iot报警策略** 

```
createIoTPolicy(iotType : AIIoTTypeEnum,iotId : number) : AlarmPolicyBean
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|iotType|AIIoTTypeEnum|内置IOT类型|
|iotId|number|内置IOTID|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|AlarmPolicyBean|报警策略|

**19.14,搜索Iot** 

```
searchAIIoT (startFlag : boolean,callback : IResultCallback) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|startFlag|boolean|是否开始搜索|
|callback|IResultCallback|接口回调|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

### **19.15,获取内置Iot信息** 

```
getInnerIoTInfo () : InnerIoTInfo
```

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|InnerIoTInfo|内置iot信息|

### **19.16,获取外置Iot信息** 

```
getIoTHubInfo () :HubIoTInfo
```

返回: 

**参数类型 说明** HubIoTInfo 外置Iot信息 

### **19.17,获取外置IOT名称** 

```
getHubIotName(iotId : number,iotType : number) : string
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|iotId|number|iot设备ID|
|iotType|number AIIoTTypeEnum|iot设备类型|

返回: 

**参数类型 说明** string 外置Iot名称 

### **19.18,获取时光相册的iot** 

```
getTimeAlbumIot(): InnerIoTBean | undefined
```

##### 返回: 

**参数类型 说明** InnerIoTBean InnerIoTBean 

# **20,报警策略** 

##### **在保存之前设置的所有属性都需要传递到这个实例当中,** 

### **获取接口实例** 

```
HmSdk.getInstance().newAlarmPolicyInstance(deviceId : string)
```

|**字段名称**|**数据类型**|**描述**|
|---|---|---|
|motionAlarmInterval|number|运动侦测报警间隔,默认30秒,单位秒|
|humanAlarmInterval|number|人形侦测报警间隔,默认30秒,单位秒|
|mainOpenFlag|boolean|总开关|
|soundLoopCnt|number|蜂鸣器报警提示音循环次数|
|soundName|string|蜂鸣器报警提示音名称|
|isBuzzerOpenFlag|boolean|蜂鸣器开关|
|isWhiteLampAlarmOpenFlag|boolean|白光灯开关|
|recordDuration|number|录像时间|
|isAlarmLampOpenFlag|boolean|报警灯开关|
|smsOpenFlag|boolean|短信报警开关|
|pushInterval|number|远程推送间隔|
|pushOpenFlag|boolean|远程推送开关|
|isSupportAlarmLamp|boolean|是否有报警灯|
|isBirdDetection|boolean|鸟类检测开关|
|isBirdRecognition|boolean|鸟类识别开关|
|isSquirrelDetection|boolean|松鼠检测开关|
|isMotionOpen|boolean|移动侦测开关|
|isMotionTraceOpen|boolean|运动追踪开关|
|isHumanOpen|boolean|人形侦测开关|
|isHumanTraceOpen|boolean|人形追踪开关|
|isDetectFaceOpen|boolean|人脸开关|
|isOpenDetectFence|boolean|是否打开区域侦测|
|isSettingFence|boolean|是否设置了侦测区域|
|fenceIDs|Array|区域ID列表|
|isSupportMotionTrace|boolean|是否支持运动追踪|
|isSupportHumanTrace|boolean|是否支持人形追踪|
|isSupportMotion|boolean|是否支持运动侦测|
|isSupportHuman|boolean|是否支持人形侦测|
|isSupportFace|boolean|是否支持人脸侦测|
|isSupportBuzzer|boolean|是否支持蜂鸣器|

|**字段名称**|**数据类型**|**描述**|
|---|---|---|
|isSuppportFence|boolean|是否支持侦测区域设置|
|sensitivity|SensitivityEnum|灵敏度|
|faceSensitivity|SensitivityEnum|人脸灵敏度|

### **20.1,获取报警策略列表** 

```
getAlarmPolicyList(deviceId : string) :Array<AlarmPolicyBean>
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|deviceId|string|设备ID|

返回: 

|**数据类型**|**描述**|
|---|---|
|Array< AlarmPolicyBean>|报警策略列表|

### **20.2,获取报警策略信息** 

```
getAlarmPolicyInfo() :Array<AlarmPolicyBean>
```

##### 返回: 

|**数据类型**|**描述**|
|---|---|
|Array< AlarmPolicyBean>|报警策略列表|

### **20.3,获取设备的报警策略** 

```
getAlarmPolicy(deviceId: String): AlarmPolicyBean
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|deviceId|string|设备ID|

##### 返回: 

|**数据类型**|**描述**|
|---|---|
|AlarmPolicyBean|报警策略|

**20.4,获取报警时间段** 

```
getAlarmTimer() : AlarmTimeBean
```

##### 返回: 

**数据类型 描述** AlarmTimeBean 报警策略 

### **20.5,获取事件通知设置信息** 

```
getEventNoticeParam() : EventOutputParam
```

##### 返回: 

**数据类型 描述** EventOutputParam 事件通知信息 

### **20.6,设置报警时间段** 

```
setAlarmTimer(alarmTime : AlarmTimeBean)
```

**参数名 参数类型 说明** alarmTime AlarmTimeBean 报警时间段信息 

### **20.7,根据事件ID获取对应的报警策略** 

```
getPolicyEventBean(eventId : EventTypeIDEnum) : PolicyEventBean | undefined
```

**参数名 参数类型 说明** eventId EventTypeIDEnum 事件类型ID枚举 

##### 返回: 

**数据类型 描述** PolicyEventBean 报警事件策略 

### **20.8,设置报警策略事件** 

```
setPolicyEventBean(eventBean: PolicyEventBean,useMotionPolicy? : boolean) :
AlarmPolicyBean | null
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|eventBean|PolicyEventBean|报警事件设置信息|
|useMotionPolicy|boolean(可空)|是否使用运动侦测|

##### 返回: 

|**数据类型**|**描述**|
|---|---|
|AlarmPolicyBean|报警策略|

### **20.9,格式化报警时间段** 

```
getFormatAlarmTime() : string
```

##### 返回: 

|**数据类型**|**描述**|
|---|---|
|string|报警时间段00:00-23:59|

### **20.10,获取报警时间段的星期数** 

```
getWeekArray(): Array<number>
```

##### 返回: 

|**数据类型**|**描述**|
|---|---|
|Array|周的数组,周一:1,周二:2,周三:3....|

### **20.11,保存报警策略数据** 

```
saveAlarmParam(callback: IResultCallback,eventBean?: PolicyEventBean)
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|callback|IResultCallback|接口回调|
|eventBean|PolicyEventBean|报警事件信息,可空|

### **20.12,设置报警提示音名称** 

```
setSoundName(soundName : string,eventId : EventTypeIDEnum)
```

|**参数名**|**参数类型说明**|
|---|---|
|soundName|string 提示音名称|
|eventId|EventTypeIDEnum 事件类型ID|

### **20.13,设置报警提示音播放循环次数** 

```
setSoundLoopCount(loopCount : number,eventId :EventTypeIDEnum )
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|loopCount|number|循环次数|
|eventId|EventTypeIDEnum|事件类型ID|

### **20.14,获取蜂鸣器报警策略提示音名称** 

```
getSoundName() : Promise<string>
```

##### 返回: 

|**数据类型**|**描述**|
|---|---|
|Promise|异步回调,返回提示音名称|

### **20.15,获取推送类型** 

```
getPushFlag() : PushTypeEnum
```

##### 返回: 

|**数据类型**|**描述**|
|---|---|
|PushTypeEnum|推送类型枚举|

### **20.16,设置通知信息** 

```
setNoticeSwitch(noticeInfo : AlarmNoticeInfo,callback : IResultCallback)
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|noticeInfo|AlarmNoticeInfo||
|callback|IResultCallback||

# **21,白光灯** 

### **获取接口实例** 

```
HmSdk.getInstance().newWhiteLampTimePolicy(deviceId : string)
```

|**字段名称**|**数据类型**|**描述**|
|---|---|---|
|startTime|string|格式化后的开始时间 格式:HH:mm|
|durationMin|number|开始时间和结束时间之间间隔时长,单位,秒|
|weekFlag|number|选择了周的几天|
|startHour|number|开始时间的小时|
|startMin|number|开始时间的分钟|

### **21.1,白光灯时间段是否打开** 

```
isTimerPolicyOpen() : boolean
```

##### 返回: 

**数据类型 描述** boolean 开关状态 

### **21.2,设置白光灯时间段开关** 

```
setTimerPolicySwitch(isOpen : boolean,callback : IResultCallback) : void
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|isOpen|boolean|开关状态|
|callback|IResultCallback|接口回调|

### **21.3,获取白光灯模式** 

```
getLightMode() : WhiteLightModeEnum
```

##### 返回: 

|**数据类型**|**描述**|
|---|---|
|WhiteLightModeEnum|白光灯模式|

**21.4, 是否全天时间段** 

```
isDayLong() : boolean
```

##### 返回: 

|**数据类型**|**描述**|
|---|---|
|boolean|是否全天时间段true全天,false自定义|

### **21.5,是否定时时间段** 

```
isTimeing() : boolean
```

##### 返回: 

|**数据类型**|**描述**|
|---|---|
|boolean|是否全天时间段true自定义时间段,false全天时间段|

### **21.6,获取全天时间段字符串** 

```
getAllDayString() : string
```

##### 返回: 

|**数据类型**|**描述**|
|---|---|
|string|白光灯时间段|

### **21.7,设置时间段策略的开关** 

```
switchTimePolicy(isOpen : boolean) : Promise<void>
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|isOpen|boolean|开关状态|

##### 返回: 

|**数据类型**|**描述**|
|---|---|
|Promise|异步返回成功失败|

**21.8,设置时间段** 

```
setTimerPolicy(timePolicy : TimePolicyBean) : Promise<void>
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|timePolicy|TimePolicyBean|时间策略信息|

##### 返回: 

|**数据类型**|**描述**|
|---|---|
|Promise|异步返回成功失败|

### **21.9,删除指定的时间段** 

```
deleteTimerPolicy(timerId : TimerPolicyTypeEnum) : Promise<void>
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|timerId|TimerPolicyTypeEnum|时间段策略类型|

##### 返回: 

|**数据类型**|**描述**|
|---|---|
|Promise|异步返回成功失败|

### **21.10,时间策略的时间格式化** 

```
getFormatTimeStr() : string
```

##### 返回: 

|**数据类型**|**描述**|
|---|---|
|string|格式化时间段:00:00-23:59|

### **21.11,获取时间段时长的Time实例** 

```
getDurationTime() : number
```

##### 返回: 

|**数据类型**|**描述**|
|---|---|
|number|持续时长,开始时间和结束时间间隔多少秒|

**一** **21.12,判断两个时间段是不是 样** 

```
equalsPolicyTimeBean(policyTimeBean : TimePolicyBean) : boolean
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|policyTimeBean|TimePolicyBean|时间段策略信息|

##### 返回: 

|**数据类型**|**描述**|
|---|---|
|boolean|true :两个时间段一样,false两个时间段不一样|

### **21.13,传入数据格式化显示格式的数据** 

```
getCurrentTimeStr(hour : number,min : number,durationMin : number,weekFlag :
number): string
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|hour|number|小时,比如1点 传1|
|min|number|分钟|
|durationMin|number|持续时长分钟|
|weekFlag|number|周几掩码|

##### 返回: 

|**数据类型**|**描述**|
|---|---|
|string|00:00-23:59,周一,周二|

### **21.14,保存白光灯时间策略** 

```
saveTimePolicy() : Promise<void>
```

##### 返回: 

|**数据类型**|**描述**|
|---|---|
|Promise|异步回调成功失败|

### **21.15,保存常亮,常亮就是全天时间段,加了重试3次** 

```
saveDayLong() : Promise<void>
```

返回: 

**数据类型** 

**描述** 

Promise 异步回调成功失败 

### **21.16,保存红外灯模式** 

```
saveIrMode(mode : WhiteLightModeEnum) : Promise<void>
```

|**参数名**|**参数类型**|
|---|---|
|mode|WhiteLightModeEnum|

|**说明**|
|---|

##### 返回: 

|**数据类型**|**描述**|
|---|---|
|Promise|异步回调成功失败|

### **21.17,白光灯模式切换** 

```
openLightByPromise(isOpen : boolean,mode : WhiteLightModeEnum) : Promise<void>
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|isOpen|boolean|白光灯开关|
|mode|WhiteLightModeEnum|白光灯模式|

##### 返回: 

|**数据类型**|**描述**|
|---|---|
|Promise|异步回调成功失败|

# **22,自定义提示音** 

### **获取接口实例** 

```
HmSdk.getInstance().newCustomAudioApi(callback?: ICustomAudioCallback, filePath?:
string)
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|callback|ICustomAudioCallback|自定义提示音回调|
|filePath|string|文件路径|

**22.1,开始录制音频** 

```
startRecordAudio() : void
```

### **22.2,停止录制音频** 

```
stopRecordAudio(): void
```

### **22.3,删除当前录制的音频文件** 

```
deleteCurrentRecordFile(): void
```

### **一** **22.4,删除后面录制的 段音频,只在录制音频时有效** 

```
deleteAudioPeriod() : void
```

### **22.5,释放录制音频资源** 

```
releaseRecordAudio(): Promise<void>
```

##### 返回: 

|**数据类型**|**描述**|
|---|---|
|Promise|异步回调成功失败|

### **22.6,新建录制自定义音频文件名称** 

```
newAudioFileName(deviceId : string,newFileName : string) :
Promise<CustomAudioBean>
```

##### 返回: 

|**数据类型**|**描述**||
|---|---|---|
|Promise< CustomAudioBean>|一部返回,|提示音信息|

### **22.7,更改提示音名称** 

```
reAudioFileName(deviceId : string,bean : CustomAudioBean,newFileName :
string,callback : IResultCallback) : void
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|deviceId|string|设备ID|
|bean|CustomAudioBean|自定义提示音信息|
|newFileName|string|新的提示音名称|
|callback|IResultCallback|接口回调|

### **22.8,删除提示音音频文件** 

```
deleteAudioFile(deviceId : string,bean: CustomAudioBean,callback :
IResultCallback) : void
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|deviceId|string|设备ID|
|bean|CustomAudioBean|自定义提示音信息|
|callback|IResultCallback|接口回调|

### **22.9,获取录音列表 ,提示音列表** 

```
getAudioList(deviceId : string,callback : ISoundListCallback) : void
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|deviceId|string|设备ID|
|callback|ISoundListCallback|接口回调|

### **22.10,开始播放录音,如果是要试听正在录制的音频可以不入参** 

```
startPlayAudio(deviceId : string,bean? : CustomAudioBean) : void
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|deviceId|string|设备ID|
|bean|CustomAudioBean|自定义提示音|

### **22.11,停止播放音频** 

```
stopPlayAudio() : void
```

**22.12,保存音频文件到设备** 

```
saveAudioToDevice(deviceId : string,bean : CustomAudioBean,callback :
IResultCallback) : void
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|deviceId|string|设备ID|
|bean|CustomAudioBean|自定义提示音信息|
|callback|IResultCallback|接口回调|

### **22.13,查找提示音的本地名称** 

```
findSoundAndLocalName(soundName? : string) : string
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|soundName|string|设备端提示音名称|

##### 返回: 

|**数据类型**|**描述**|
|---|---|
|string|本地UI显示的名称|

### **22.14,pcm音频文件转Wav音频文件** 

```
convertPcmToWav(pcmFilePath: string, wavFilePath: string): Promise<fileIo.File>
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|pcmFilePath|string|pcm文件路径|
|wavFilePath|string|wav存储路径|

##### 返回: 

|**数据类型**|**描述**|
|---|---|
|Promise<fileIo.File>|异步回调,返回存储的文件|

# **23,用户信息** 

### **获取接口实例** 

```
HmSdk.getInstance().newZJViewerAddDevice()
```

### **23.1,刷新用户信息缓存** 

```
refreshUserVCardInfo (userId: string, callback: IRefreshVcardCallback) :ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|userId|string|用户ID|
|callback|IRefreshVcardCallback|接口回调|

### **23.2,连接设备的ap** 

```
connectDeviceByAP (ipAddress: string) : void
```

**参数名 参数类型 说明** ipAddress string ip地址 

### **23.3,获取用户ID** 

```
getUserId () : string
```

##### 返回: 

**数据类型 描述** string 用户ID 

### **23.4,获取用户token** 

```
getUserToken () : string
```

##### 返回: 

**数据类型 描述** string 用户Token 

### **23.5,通过groupID获取用户token** 

```
getUserTokenByGroupId (groupId : string) : string
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|groupId|string|组ID|

##### 返回: 

|**数据类型**|**描述**|
|---|---|
|string|用户Token|

### **23.6,获取当前登录的账号信息** 

```
getOwnerAccountInfo () : UserBean
```

##### 返回: 

|**数据类型**|**描述**|
|---|---|
|UserBean|用户信息|

### **23.7,获取用户的个人信息** 

```
getOwnerVCardInfo () : UserVCardBean
```

##### 返回: 

|**数据类型**|**描述**|
|---|---|
|UserVCardBean|用户个人信息|

### **23.8,获取指定用户的个人信息** 

```
getShareUserVCardInfo (userId: string) : UserVCardBean
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|userId|string|用户ID|

##### 返回: 

|**数据类型**|**描述**|
|---|---|
|UserVCardBean|指定用户ID个人信息|

### **23.9,用手机账号获取userID** 

```
getUserIdByMobile (countryCode: string, mobile: string, callback:
IGetUserIdCallback): ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|countryCode|string|国家码 比如中国:86|
|mobile|string|手机号|
|callback|IGetUserIdCallback|接口回调|

### **23.10,用邮箱获取用户ID** 

```
getUserIdByEmail (email: string, callback: IGetUserIdCallback) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|email|string|邮箱|
|callback|IGetUserIdCallback|接口回调|

### **23.11,删除当前账号** 

```
deleteAccount (callback: IResultCallback) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|callback|IResultCallback|接口回调|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

### **23.12,设置推送token** 

```
setPushToken (pushInfoBean: PushInfoBean, callback: IResultCallback) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|pushInfoBean|PushInfoBean|需要设置的推送信息|
|callback|IResultCallback|接口回调|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

**23.13,刷新全部的设备状态,** 

##### 状态会在 registerDeviceStatusObserver回调中返回 

```
refreshDeviceStatus (callback?: IResultCallback) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|callback|IResultCallback|接口回调|

返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

### **23.14,获取本地缓存大小** 

```
getLocalCacheSize (callback: ICacheSizeCallback) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|callback|ICacheSizeCallback|接口回调|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

### **23.15,清除本地缓存** 

```
cleanLocalCache (keepDays: number, callback: IResultCallback) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|keepDays|number|保持几天的|
|callback|IResultCallback|回调|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

**23.16,生成属主转移二维码** 

```
createOwnerChangeQR (groupId: string, deviceId: string,qrCodeImgHeight :
number,qrCodeImgWidth : number, callback: IChangeQRCallback) : void
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|groupId|string|组ID|
|deviceId|string|设备ID|
|qrCodeImgHeight|number|生成二维码图片的高度,默认400|
|qrCodeImgWidth|number|生成二维码图片的宽度,默认400|
|callback|IChangeQRCallback|接口回调|

### **23.17,创建分享二维码** 

```
createShareQRCode (deviceId : string,qrCodeImgHeight : number,qrCodeImgWidth :
number, callback: IChangeQRCallback) :void
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|deviceId|string|设备ID|
|qrCodeImgHeight|number|生成二维码图片的高度,默认400|
|qrCodeImgWidth|number|生成二维码图片的宽度,默认400|
|callback|IChangeQRCallback|接口回调|

### **23.18,获取微信公众号管理实例** 

```
newWeChatOfficialAccountMag () : WeChatOfficialAccount
```

#### **23.18.1,获取微信公众号二维码url** 

```
getWeChatQRCode(wechatAppid : string,callback : IWeChatQRCodeCallback)
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|wechatAppid|string|微信公众号的appID|
|callback|IWeChatQRCodeCallback|接口回调|

#### **23.18.2,获取微信公众号当前的状态** 

```
getWeChatCurStatus(callback : IWeChatCurStatusCallback)
```

**参数名** 

**参数类型** 

**说明** 接口回调 

|callback|IWeChatCurStatusCallback|
|---|---|

#### **23.18.3,设置微信公众号通知的开关** 

```
setWeChatPushFlag(openFlag : boolean,callback : IResultCallback)
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|openFlag|boolean|公众号通知开关|
|callback|IResultCallback|接口回调|

### **23.19,获取资源图片,智能事件显示UI的图片从这里获取,如果定制 app也可以不用我们云端图片** 

```
getResourceByEventID (list : Array<EventIdBean>,callback : IGetResourceCallback)
:ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|list|Array|智能服务事件ID列表|
|callback|IGetResourceCallback|接口回调,返回图片列表|

### **23.20,设置国家码,目前国内是"CN" 海外是空字符串** 

```
setCountryCode (countryCode : string) :void
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|countryCode|string|国家码|

### **23.21,设置本地语言** 

```
setLocalLanguage (language : number) : void
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|language|number|语言码ZJUtil.getCurLanguage()|

### **23.22,获取支持的账号注册方式** 

```
getSupportRegisterAccountTypeList (zoneCode : string,callback :
IGetAccountTypeListCallback) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|zoneCode|string|时区ID|
|callback|IGetAccountTypeListCallback|接口回调|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

### **23.23,删除设备,设备退组** 

```
removeDevice(deviceId : string,callback : IResultCallback) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|deviceId|string|设备ID|
|callback|IResultCallback|接口回调|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

### **23.24,获取分享用户的账号** 

```
getShareUserAccount(userId : string) : string
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|userId|string|用户ID|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|string|用户账号|

### **23.25,获取心钻数量** 

```
getPoints(callback? : IResultListener<number>) : void
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|callback|IResultListener|接口回调|

**23.26,获取设备命名页面的用途列表** 

```
getUseList(country_code : string) : Promise<Array<UseModel>>
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|country_code|string|"EN"或者"CN"|

##### 返回: 

**参数类型 说明** Promise<Array<UseModel>> 用户账号 

### **23.27,获取用户昵称** 

```
getUserNick(userVCardBean: UserVCardBean) : string
```

**参数名 参数类型 说明** userVCardBean UserVCardBean 用户信息 

##### 返回: 

**参数类型 说明** string 用户昵称 

### **23.28,获取用户账号** 

```
getUserAccount(userVCardBean: UserVCardBean) : string
```

**参数名 参数类型 说明** userVCardBean UserVCardBean 用户信息 

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|string|用户账号|

### **23.29,扫码分享设备到当前用户** 

扫码解析出来的分享URl  通过工具类QRCodeContentTools 解析扫描二维码的数据 

```
sharedToUser(sharedUrl : string) : Promise<void>
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|sharedUrl|string|分享的URl|

返回: 

|**参数类型**|**说明**|
|---|---|
|Promise|异步回调|

### **23.30,扫码登录** 

##### 扫码解析出来的分享URl  通过工具类QRCodeContentTools 解析扫描二维码的数据 

```
scanCodeLogin(loginUrl : string) : Promise<void>
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|loginUrl|string|登录URL|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|Promise|异步回调|

### **23.31,设备属主转移** 

##### 扫码解析出来的分享URl  通过工具类QRCodeContentTools 解析扫描二维码的数据 

```
deviceOwnerTransfer(url: string) : Promise<void>
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|url|string|属主转移Url|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|Promise|异步回调|

### **23.32,获取分享的二维码** 

```
getSharedQRCode(groupId : string):Promise<image.PixelMap>
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|groupId|string|组ID|

返回: 

**说明** 

##### **参数类型** 

Promise<image.PixelMap> 

|异步回调,成功后返回图片|
|---|

##### 23.33,压缩日志为zip 

```
zipAllLogFile(isAppLog : boolean ,outFile? : string) : Promise<string>
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|isAppLog|boolean|是否要app日志|
|outFile|string|压缩到存储文件路径 (可空)|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|Promise|返回压缩zip后存储的文件路径|

### **23.34,获取用户的paas信息** 

```
getPaasPlatAccessToken(callback : IGetPaasAccessTokenCallback): ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|callback|IGetPaasAccessTokenCallback|接口回调|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|ITask|请求任务,可以取消请求|

### **23.35,是否无缓存工作模式** 

是否无缓存工作模式;cacheMode: 1 无缓存; 0: 有缓存; sdk 默认0。 无缓存是针对 TF卡的录像列表、图片列表、事件列表有效 

```
setAppCacheWorkMode(mode : CacheWorkModeEnum) : number
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|mode|CacheWorkModeEnum||

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|number|错误码,0成功|

# **24,本地相册** 

### **获取接口实例** 

```
HmSdk.getInstance().newLocalAlbumInstance()
```

### **24.1,获取本地截图列表** 

```
getCaptureImageList() : Array<LocalMediaBean>
```

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|Array< LocalMediaBean>|本地图片列表|

### **24.2,删除全部的截图** 

```
deleteAllCaptureImage()
```

### **24.3,获取本地录像视频列表** 

```
getRecordVideoList() : Promise<Array<LocalMediaBean>>
```

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|Promise<Array< LocalMediaBean>>|异步回调,本地录像视频列表|

### **24.4,删除全部的本地录像视频** 

```
deleteAllRecordVideo()
```

### **24.5,删除单个文件** 

```
deleteFile(bean : LocalMediaBean)
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|bean|LocalMediaBean|文件信息|

**24.6,获取云录像视频列表** 

```
getCloudVideoList() : Promise<Array<LocalMediaBean>>
```

##### 返回: 

##### **参数类型** 

##### **说明** 

Promise<Array<LocalMediaBean>> 异步回调,本地云录像视频列表 

### **24.7,删除全部下载的云录像** 

```
deleteAllCloudVideo()
```

### **24.8,获取sd卡录像视频列表** 

```
getCardVideoList() : Promise<Array<LocalMediaBean>>
```

##### 返回: 

**参数类型 说明** Promise<Array<LocalMediaBean>> 异步回调,本地卡录像视频列表 

### **24.9,删除全部下载的卡录像** 

```
deleteAllCardVideo()
```

### **24.10,取视频封面图片** 

```
getAVImageGenerator(filePath: string) : Promise<image.PixelMap>
```

**参数名 参数类型 说明** filePath string 视频文件路径 **参数类型 说明** Promise<image.PixelMap> 异步回调,返回视频封面图片 

##### 返回: 

### **24.11,将图片转换为Base64** 

```
getImageBase64WithUri(pixelMap:PixelMap): Promise<string>
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|pixelMap|PixelMap|要转换Aase64的图片|

返回: 

|**参数类型**|**说明**|
|---|---|
|Promise|异步回调,返回图片的Base64|

### **24.12,保存图片到指定路径** 

```
savePixelMapToFile(path : string,pixelMap : image.PixelMap)
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|path|string|保存的指定路径|
|pixelMap|image.PixelMap|需要保存的图片|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|Promise|异步回调,|

# **25,布防管理** 

### **获取接口实例** 

```
HmSdk.getInstance().newZJViewerProtectionMode(deviceId : string)
```

### **25.1,获取当前的布防模式** 

```
getCurProtectionMode() : ProtectionModeEnum
```

##### 返回: 

**参数类型 说明** ProtectionModeEnum 布防模式枚举 

### **25.2,切换布防模式** 

```
switchProtectionMode( protectionMode : ProtectionModeEnum,  callback :
IResultCallback) : ITask
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|protectionMode|ProtectionModeEnum|布防模式|
|callback|IResultCallback|回调接口|

### **25.3,获取布防模式参数** 

```
getProtectionModeParam() : ProtectionModeParam
```

##### 返回: 

**参数类型 说明** ProtectionModeParam 布防模式设置信息 

### **25.4,修改布防模式参数** 

```
setProtectionParam(protectionParam : ProtectionModeParam,callback :
IResultCallback) : void
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|protectionParam|ProtectionModeParam|布防模式设置信息|
|callback|IResultCallback|接口回调|

### **25.5,修改布防模式参数** 

```
setProtectionModeParam(protectionMode: ProtectionModeEnum,protectionModeParam? :
ProtectionModeParam) : Promise<void>
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|protectionMode|ProtectionModeEnum|不妨模式枚举|
|protectionModeParam|ProtectionModeParam|布防模式设置信息|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|Promise|异步回调|

### **25.6,删除布防策略中的hubIot** 

```
deleteIotOfProtection(iotType : AIIoTTypeEnum,iotId : number) : Promise<void>
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|iotType|AIIoTTypeEnum|外置iot设备类型|
|iotId|number|外置iotID|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|Promise|异步回调|

# **26,预置位/巡航** 

### **获取接口实例** 

```
HmSdk.getInstance().newZJViewerPresetCruise(deviceId : string)
```

### **26.1,是否支持预置位** 

```
isSupportPreset() : boolean
```

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|boolean|true :支持预置位设置,false不支持预置位设置|

### **26.2,获取预置位列表信息** 

```
getPresetList() : Promise<PresetModel[]>
```

##### 返回: 

**参数类型** Promise<Array<PresetModel>> 

**说明** 异步返回,预置位信息列表 

### **26.3,添加预置位** 

```
addOnePreset(model : SetPresetModel) : Promise<PresetModel>
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|model|SetPresetModel|预置位设置信息|

返回: 

**参数类型** 

**说明** 

Promise<PresetModel> 

异步返回,预置位信息 

### **26.4,获取预置位的文件路径** 

```
getFilePath(fileId : string) : string
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|fileId|string|文件名称|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|string|文件路径|

### **26.5,设置看守位** 

```
setWatchedPtz(presetId : number,watchPollTime : number) : Promise<void>
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|presetId|number|预置位ID|
|watchPollTime|number|是否是看守位|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|Promise|异步回调|

### **26.6,删除预置位** 

```
deleteAllPreset(presetList : Array<PresetModel>) : Promise<void>
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|presetList|Array< PresetModel>|预置位信息列表|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|Promise|异步回调|

**26.7,转动到预置位位置** 

```
ctrlPtzToPresetPoint(presetId : number) : Promise<number>
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|presetId|number|预置位ID|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|Promise|异步回调,PTZ状态|

### **26.8,巡航操作** 

```
ctrlPtzToCruise(cruiseId : number,onSuccess? : () =>void) : Promise<number>
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|cruiseId|number|巡航ID|
|onSuccess|() =>void|函数回调|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|Promise|异步回调,PTZ状态|

### **26.9,下载预置位图片** 

```
downloadPresetImage(fileID : string) : Promise<string>
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|fileID|string|图片ID,只有上传到云端的图片才有图片ID|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|Promise|异步回调,图片绝对路径|

### **26.10,是否支持巡航** 

```
isSupportCruise() : boolean
```

返回: 

|**参数类型**|**说明**|
|---|---|
|boolean|是否支持巡航,true支持巡航 ,false:不支持巡航|

### **26.11,是否支持看守位** 

```
isSupportWatchPresetPos() : boolean
```

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|boolean|是否支持设置看守位,true支持 ,false:不支持|

### **26.12,是否设置了巡航** 

```
isSettingCruise() : boolean
```

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|boolean|是否设置了巡航,true已设置 ,false:未设置|

### **26.13,开始ptz矫正** 

```
startPTZSelfCheck(onSuccess : () =>void) : Promise<number>
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|onSuccess|() =>void|成功回调函数|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|Promise|异步回调,ptz状态|

### **26.14,当前预置位是否添加到了巡航** 

```
whetherAddSmartCruise(presetId : number) : boolean
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|presetId|number|预置位ID|

返回: 

**参数类型** 

**说明** 

boolean true:添加到了巡航,false : 没有添加到巡航 

### **26.15,删除指定预置位巡航** 

```
removeCruiseByPromise(cruiseId : number) :Promise<void>
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|cruiseId|number|巡航ID|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|Promise|异步回调|

**一** **26.16,获取巡航信息列表,如果没有设置过巡航就会返回 个默认 的,** 

```
getCruiseList() : Array<CruiseBean>
```

##### 返回: 

**参数类型 说明** Array<CruiseBean> 巡航列表 

### **26.17,是否正在巡航** 

```
isItCruising() : boolean
```

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|boolean|true :正在巡航,false:没有在巡航|

### **26.18,添加预置位巡航** 

```
setPresetCruise(cruiseBean : CruiseBean): Promise<void>
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|cruiseBean|CruiseBean|巡航信息|

返回: 

**参数类型** 

**说明** 

异步回调 

Promise 

# **27,埋点** 

### **获取接口实例** 

```
HmSdk.getInstance().newHMAnalysis()
```

### **27.1,多事件设置埋点** 

```
setEvents(bussId : number,params : HashMap<string,string>) : number
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|bussId|number|业务ID|
|params|HashMap<string,string>|事件对应上报的参数|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|number|0 :成功|

### **27.2,事件上报** 

```
setEvent(bussId : number,event : string) : number
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|bussId|number|业务ID|
|event|string|事件名称|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|number|0 :成功|

**27.3,用户拥有状态** 

```
userBHavrStat(bussId : number,havrJson : string) : number
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|bussId|number|业务ID|
|havrJson|string|数据json|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|number|0 :成功|

# **28,本地设备缓存** 

### **获取接口实例** 

```
HmSdk.getInstance().newLocalDeviceCatch(deviceId : string)
```

### **28.1,设置hubIot关联信息** 

```
setPairInfo(pairInfo : PairInfo) : void
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|pairInfo|PairInfo|关联信息|

### **28.2,获取hubIot关联信息** 

```
getPairDevID(ioTId : number) : Promise<string>
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|ioTId|number|iot设备ID|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|Promise|异步回调,返回关联的设备ID|

**28.3,删除hubIot关联信息** 

```
removePairInfo() : void
```

### **28.4,取消hubIot关联信息** 

```
cancelPairInfo(iotId : number) : void
```

**参数名 参数类型 说明** ioTId number iot 设备ID 

### **28.5,更新hubIot关联信息** 

```
savePairInfo(pairDeviceId : string,iotId : number) : void
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|pairDeviceId|string|关联设备ID|
|iotId|number|iot设备ID|

### **28.6,是否支持强提醒** 

```
isSupportStrongReminder() : Promise<boolean>
```

##### 返回: 

**参数类型 说明** Promise 异步回调,返回是否支持强提醒 

### **28.7,获取强提醒的设置项** 

```
getStrongReminderSetting() : Promise<Array<NoticeSettingBean>>
```

##### 返回: 

**参数类型 说明** Promise<Array<NoticeSettingBean>> 异步回调,返回强提醒通知设置信息列表 

### **28.8,设置强提醒设置项** 

```
setStrongReminderSetting(bean : NoticeSettingBean) : Promise<void>
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|bean|NoticeSettingBean|强提醒通知设置信息|

返回: 

|**参数类型**|**说明**|
|---|---|
|Promise|异步回调|

# **29,设备播放器** 

播放器可以直接在UI中使用,这是一个UI组件 

## **MediaVideoPlayer** 

```
MediaVideoPlayer({
        mediaRenderController: this.mediaRenderController,
        deviceId: this.deviceId,
        onFirstFrameCall: async () => {//视频出图第一帧回调
        },
        onLoadFailed: (errorCode: ErrorEnum) => {//视频加载失败回调
          if (errorCode == ErrorEnum.TIME_OUT) {//视频加载超时
          }
        },
        onPlayClick: () => {//播放器点击回调,比如播放器点击后你需要隐藏一些UI
        }
      })
        .backgroundColor(Color.Black)
        .width('100%')
        .height('auto')
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|mediaRenderController|MediaRenderController|播放视频控制器|
|deviceId|string|设备ID|

## **播放器控制 MediaRenderController** 

### **获取接口实例** 

```
MediaRenderController.newMediaRenderController(this.deviceId)
```

**1,设置设备ID** 

```
setDeviceId(deviceId: string)
```

#### **2,初始化流** 

```
initStream(deviceId: string, VRMode? : PlayShowModeEnum) : Promise<void>
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|deviceId|string|设备ID|
|VRMode|PlayShowModeEnum|播放器显示模式,(可空)|

#### **3,点播实时流** 

```
startRealTimeStream(streamId : number,playerType? : PlayTypeEnum) : void
```

|**参数名**|**参数类型**|**说明**||
|---|---|---|---|
|streamId|number|播放视频流ID||
|playerType|PlayTypeEnum|播放类型,卡录像,|云录像,实时点播,(可空)|

#### **4,点播卡录像** 

```
startRecordStream(startTime: string)  : void
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|startTime|string|播放卡录像的开始时间2025-03-27 18:17:25|

#### **5,点播云录像** 

```
startCloudStream(startTime: string)  : void
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|startTime|string|播放卡录像的开始时间2025-03-27 18:17:25|

#### **6,设置屏幕画面的布局** 

```
setScreenLayout(isLand : boolean,playMode? : PlayShowModeEnum)
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|isLand|boolean|设备ID|
|playMode|PlayShowModeEnum|播放器显示模式,(可空)|

**7,获取播放器的显示模式** 

```
getPlayShowMode() : Promise<PlayShowModeEnum>
```

返回: 

**参数类型 说明** 

Promise<PlayShowModeEnum> 异步回调,返回播放器的显示模式 

#### **8,是否支持双屏模式** 

```
isSupportDualScreen() : boolean
```

#### **9,切换流,比如切换高清,超清** 

```
switchStream(streamId : number) : void
```

**参数名 参数类型 说明** streamId number 流ID 

#### **10,停止播放器播放** 

```
stopRealTimeStream(isCaptureImage? : boolean)
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|isCaptureImage|boolean|是否停止播放器前截图 (可空)|

#### **11,播放设备声音** 

```
playDeviceSound(isPlay : boolean) : void
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|isPlay|boolean|true播放设备声音,false停止播放设备声音|

#### **12,开始录制视频** 

```
startRecordMP4(callback : IRecordMP4Listener)
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|callback|IRecordMP4Listener|录制视频回调|

**13,停止录制视频** 

```
stopRecordMp4()
```

#### **14,开始说话** 

```
startTalk()
```

#### **15,停止说话** 

```
stopTalk()
```

#### **16,设置是否支持手势滑动摄像头** 

```
enableGestureSwipeCamera(isSupportSwipeCamera : boolean)
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|isSupportSwipeCamera|boolean|true支持手势滑动,false不支持手势滑动|

#### **17,设置是否支持手势缩放** 

```
enableGestureZoom(enable : boolean)
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|enable|boolean|true支持手势缩放,false不支持手势缩放|

#### **18,设置设备的倍数** 

```
setZoomScale(screenIndex : number,scale : number)
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|screenIndex|number|哪个镜头放大倍数|
|scale|number|放大到多少倍|

#### **20,截取媒体流的一帧图片** 

```
captureVideoImage(path? : string) : Promise<string>
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|path|string|路径可空|

返回: 

**参数类型** 

**说明** 

Promise 异步回调,返回图片的存储路径 

#### **21,设备PTZ转动** 

```
startCtrlPtz(value : PTZDirectionEnum)
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|value|PTZDirectionEnum|设备PTZ转动方向枚举|

#### **22,销毁播放资源** 

```
destory()
```

#### **23,开始设备变焦** 

```
startDeviceZoom(scale: number)
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|scale|number|设备变焦的倍数|

# **30,回看,卡录像云录像** 

## **HMTimeLineView** 

```
HMTimeLineView({
  isStopPlayBack : this.isStopPlayBack,
  deviceId : this.deviceId,
  PlayBackType : PlayTypeEnum.TIME_LINE_MODE_CLOUD,
  eventStartTime : this.startTime,
  timeLineCallback : this.callback,
  onLoadVideoSuccess : () =>{
    this.LoadingDialog.dismiss()
  }
})
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|isStopPlayBack|boolean|是否停止播放|
|deviceId|string|设备ID|
|PlayBackType|PlayTypeEnum|播放类型,|
|eventStartTime|string|播放的开始时间 格式:2025-03-27 18:17:25|
|timeLineCallback|TimeLineCallback|时间轴按钮回调|
|onLoadVideoSuccess|箭头函数|加载视频成功|

# **31,全局公共函数** 

### **获取周几数组** 

```
getWeekArray(weekFlag: number): Array<number>
```

|**参数名称**|**参数类型**|**描述**|
|---|---|---|
|weekFlag|number|星期一:0x01星期二:0x02星期三:0x04星期四:0x08星期五: 0x010星期六:0x020星期日:0x040全部:0x7F|

返回: 

|**参数类型**|**描述**|
|---|---|
|Array|周几的数组,周一:1,周二:2,周三:3,。。。|

### **获取周几的掩码数组** 

```
getWeekFlag(weekArray: number[]): number
```

|**参数名称**|**参数类型**|**描述**|
|---|---|---|
|weekArray|Array|周几的数组,周一:1,周二:2,周三:3,。。。|

返回: 

|**参数类型**|**描述**|
|---|---|
|number|周几掩码或起来的结果 比如全部或起来就是0x7F星期一:0x01星期二:0x02星期|
||三:0x04星期四:0x08星期五:0x010星期六:0x020星期日:0x040|

# **32,全局监听接口** 

### **获取接口实例** 

```
NativeInternal.getInstance()
```

### **1,设备状态监听** 

```
/**
 * 注册设备状态监听
 * @param observer
 */
registerDeviceStatusObserver(observer : (groupId : string,deviceId :
string,deviceStatus : DeviceStatusEnum) =>void)
  /**
   * 反注册设备监听
   * @param observer
   */
  unregisterDeviceStatusObserver(observer : (groupId : string,deviceId :
string,deviceStatus : DeviceStatusEnum) =>void)
```

### **2,新事件通知回调** 

```
/**
   * 注册新事件通知回调
   * @param observer
   */
  registerEventNoticeObserver(observer : EventNoticeObserver)
  /**
   * 反注册新事件通知回调
   * @param observer
   */
  unregisterEventNoticeObserver(observer : EventNoticeObserver)
```

|**参数名称**|**参数类型**|**描述**|
|---|---|---|
|observer|EventNoticeObserver|事件通知回调|

### **3,新报警事件通知** 

```
/**
   * 注册新事件通知回调
   * @param observer
   */
  registerAlarmEventObserver(observer : AlarmEventObserver)
  /**
   * 反注册新事件通知回调
   * @param observer
   */
  unregisterAlarmEventObserver(observer : AlarmEventObserver)
```

|**参数名称**|**参数类型**|**描述**|
|---|---|---|
|observer|AlarmEventObserver|报警事件通知回调|

### **4,系统公告通知** 

```
/**
   * 注册系统公告通知
   * @param observer
   */
  registerSystemNoticeObserver(observer : SystemNoticeObserver)
  /**
   * 反注册系统公告通知
   * @param observer
   */
  unregisterSystemNoticeObserver(observer : SystemNoticeObserver)
```

|**参数名称**|**参数类型**|**描述**|
|---|---|---|
|observer|SystemNoticeObserver|系统公告通知回调|

### **5,广告发布通知** 

```
/**
   * 注册广告发布通知
   * @param observer
   */
  registerAdNoticeObserver(observer : AdNoticeObserver)
  /**
   * 反注册广告发布通知
   * @param observer
   */
  unregisterAdNoticeObserver(observer : AdNoticeObserver)
```

|**参数名称**|**参数类型**|**描述**|
|---|---|---|
|observer|AdNoticeObserver|系统公告通知回调|

### **6,运营管理平台发送系统消息通知** 

```
/**
```

- `注册系统可以通过运营管理平台向终端用户发送系统消息通知` 

- `*/` 

- `registerAppGradeNoticeObserver(observer : IAppGradeNoticeObserver) /**` 

- `反注册系统可以通过运营管理平台向终端用户发送系统消息通知` 

- `*/` 

```
unregisterAppGradeNoticeObserver(observer : IAppGradeNoticeObserver)
```

|**参数名称**|**参数类型**|**描述**|
|---|---|---|
|observer|IAppGradeNoticeObserver|通知回调|

**33,工具类** 

## **1,二维码数据解析工具类** 

### **QRCodeContentTools** 

### **1,解析二维码数据** 

```
parseQRCode(qrCodeStr: string, callback: IScanCodeCallback)
```

|**参数名称**|**参数类型**|**描述**|
|---|---|---|
|qrCodeStr|string|识别出的二维码数据|
|callback|IScanCodeCallback|解析回调|

### **2,是否包含外置设备** 

```
isIncludeAddHubIot(deviceId : string,iotType : number,iotId : number)
```

|**参数名称**|**参数类型**|**描述**|
|---|---|---|
|deviceId|string|设备ID|
|iotType|number|iot设备类型|
|iotId|number|iot设备ID|

## **2,蓝牙相关工具类** 

### **BluetoothTools** 

### **1,请求蓝牙权限** 

```
requestBluetoothPermission(callback: IRequestPermissionCallback)
```

|**参数名称**|**参数类型**|**描述**|
|---|---|---|
|callback|IRequestPermissionCallback|请求权限回调|

### **2,判断蓝牙权限授权是否已授权** 

```
isBluetoothPermission(): boolean
```

##### 返回: 

|**参数类型**|**描述**|
|---|---|
|boolean|true:蓝牙权限已授权false:蓝牙权限未授权|

**3,设置蓝牙开关状态** 

```
setBluetoothSwitch(isOpen: boolean)
```

|**参数名称**|**参数类型**|**描述**|
|---|---|---|
|isOpen|boolean|打开:true关闭:false|

### **4,获取蓝牙开关的状态** 

```
getBluetoothState(): access.BluetoothState
```

返回: 

**参数类型 描述** access.BluetoothState 系统的蓝牙state实例 

### **5,注册蓝牙开关状态监听** 

```
registerBluetoothSwitchState(callback: IBluetoothLinkStateCallback)
```

|**参数名称**|**参数类型**|**描述**|
|---|---|---|
|callback|IBluetoothLinkStateCallback|蓝牙开关状态的接口回调|

### **6,关闭蓝牙开关状态监听** 

```
unregisterBluetoothSwitchState()
```

## **3,设备能力工具类** 

### **DeviceAbilityTools** 

### **1,是否有多个摄像头,如:抢球设备** 

```
hasMultipleCamera(deviceID: string): boolean
```

|**参数名称**|**参数类型**|**描述**|
|---|---|---|
|deviceID|string|设备ID|

返回: 

|**参数类型**|**描述**|
|---|---|
|boolean|true:多个摄像头,false:不是多个摄像头|

**2,是否支持自定义提示音上云,适配旧版本提示音只设置到设备端 的问题 ,智能服务284版本** 

```
isSupportPromptToneToCloud(deviceID: string): boolean
```

|**参数名称**|**参数类型**|**描述**|
|---|---|---|
|deviceID|string|设备ID|

返回: 

|**参数类型**|**描述**|
|---|---|
|boolean|true:支持提示音上云,false:不支持提示音上云|

### **3,是否支持外设IOT** 

```
isSupportHubIot(deviceId: string): boolean
```

|**参数名称**|**参数类型**|**描述**|
|---|---|---|
|deviceID|string|设备ID|

##### 返回: 

|**参数类型**|**描述**|
|---|---|
|boolean|true:支持外设IOT,false:不支持外设IOT|

### **4,是否支持夏令时** 

```
isDaylightSavingTtime(deviceid: string): boolean
```

|**参数名称**|**参数类型**|**描述**|
|---|---|---|
|deviceID|string|设备ID|

##### 返回: 

|**参数类型**|**描述**|
|---|---|
|boolean|true:支持夏令时,false:不支持夏令时|

### **5,是否是双频设备,也就是是否支持5Gwifi** 

```
isDeviceSupportDual(deviceId: string): boolean
```

|**参数名称**|**参数类型**|**描述**|
|---|---|---|
|deviceID|string|设备ID|

返回: 

|**参数类型**|**描述**|
|---|---|
|boolean|true:支持5Gwifi,false:不支持5Gwifi|

### **6,是否是鱼眼设备** 

```
isFishCamera(deviceId: string)
```

|**参数名称**|**参数类型**|**描述**|
|---|---|---|
|deviceID|string|设备ID|

### **7,设备是否支持ptz** 

```
isSupportPtz(deviceId: string, camId?: number)
```

|**参数名称**|**参数类型**|**描述**|
|---|---|---|
|deviceID|string|设备ID|
|camId|number|摄像头ID|

### **8,设置是否支持云台插件** 

```
isSupportAttachPtz(deviceId: string) : boolean
```

|**参数名称**|**参数类型**|**描述**|
|---|---|---|
|deviceID|string|设备ID|
|返回:|||

|**参数类型**|**描述**||
|---|---|---|
|boolean|true:|支持云台插件,false:不支持云台插件|

### **9,判断是否为低功耗设备** 

```
isSaveEnergyDevice(deviceId: string): boolean
```

|**参数名称**|**参数类型**|**描述**|
|---|---|---|
|deviceID|string|设备ID|

返回: 

|**参数类型**|**描述**||
|---|---|---|
|boolean|true:|是低功耗设备,false:不是低功耗设备|

### **10,是否支持设备日志发送** 

```
isSupportDeviceLogSend(deviceId : string) : boolean
```

|**参数名称**|**参数类型**|**描述**|
|---|---|---|
|deviceID|string|设备ID|

返回: 

|**参数类型**|**描述**||
|---|---|---|
|boolean|true:|支持设备日志发送,false:不支持设备日志发送|

### **11,是否支持设置录像时间段** 

```
isSupportRecordTime(deviceId : string) : boolean
```

|**参数名称**|**参数类型**|**描述**|
|---|---|---|
|deviceID|string|设备ID|

返回: 

|**参数类型**|**描述**|
|---|---|
|boolean|true:支持设置录像时间段,false:不支持设置录像时间段|

### **12,是否支持 双向视频** 

```
isSupportRSVVideo(deviceId : string) : boolean
```

|**参数名称**|**参数类型**|**描述**|
|---|---|---|
|deviceID|string|设备ID|

返回: 

|**参数类型**|**描述**|
|---|---|
|boolean|true:支持,false:不支持|

**13,是否支持侦测区域设置** 

```
isSupportFence(deviceId : string) : boolean
```

|**参数名称**|**参数类型**|**描述**|
|---|---|---|
|deviceID|string|设备ID|

##### 返回: 

|**参数类型**|**描述**|
|---|---|
|boolean|true:支持,false:不支持|

### **14,是否支持自定义提示音设置** 

```
isRingToneSetAbility(deviceId: string) : boolean
```

|**参数名称**|**参数类型**|**描述**|
|---|---|---|
|deviceID|string|设备ID|

##### 返回: 

|**参数类型**|**描述**|
|---|---|
|boolean|true:支持,false:不支持|

### **15,是否支持卡录像** 

```
isSupportTFCard(deviceId: string) : boolean
```

|**参数名称**|**参数类型**|**描述**|
|---|---|---|
|deviceID|string|设备ID|

##### 返回: 

|**参数类型**|**描述**|
|---|---|
|boolean|true:支持,false:不支持|

### **16,是否支持云录像** 

```
isSupportCloud(deviceId: string) : boolean
```

|**参数名称**|**参数类型**|**描述**|
|---|---|---|
|deviceID|string|设备ID|

返回: 

|**参数类型**|**描述**|
|---|---|
|boolean|true:支持,false:不支持|

### **17,是否支持双屏模式** 

```
isSupportDoubleScreen(deviceId : string) : boolean
```

|**参数名称**|**参数类型**|**描述**|
|---|---|---|
|deviceID|string|设备ID|

##### 返回: 

|**参数类型**|**描述**|
|---|---|
|boolean|true:支持,false:不支持|

### **18,是否支持状态灯开关设置** 

```
isSupportStatusLamp(deviceId: string): boolean
```

|**参数名称**|**参数类型**|**描述**|
|---|---|---|
|deviceID|string|设备ID|

返回: 

|**参数类型**|**描述**|
|---|---|
|boolean|true:支持,false:不支持|

### **19,是否支持宽动态设置** 

```
isSupportWDR(deviceId: string): boolean
```

|**参数名称**|**参数类型**|**描述**|
|---|---|---|
|deviceID|string|设备ID|

返回: 

|**参数类型**|**描述**|
|---|---|
|boolean|true:支持,false:不支持|

**20,是否支持红外灯** 

```
isSupportIRLed(deviceId: string): boolean
```

|**参数名称**|**参数类型**|**描述**|
|---|---|---|
|deviceID|string|设备ID|

##### 返回: 

|**参数类型**|**描述**|
|---|---|
|boolean|true:支持,false:不支持|

### **21,是否支持白光灯** 

```
isSupportWhiteLamp(deviceId: string): boolean
```

|**参数名称**|**参数类型**|**描述**|
|---|---|---|
|deviceID|string|设备ID|

##### 返回: 

|**参数类型**|**描述**|
|---|---|
|boolean|true:支持,false:不支持|

### **22,是否支持白光灯时间段** 

```
isSupportWhiteLampTime(deviceId: string): boolean
```

|**参数名称**|**参数类型**|**描述**|
|---|---|---|
|deviceID|string|设备ID|

##### 返回: 

|**参数类型**|**描述**|
|---|---|
|boolean|true:支持,false:不支持|

### **23,是否支持一键报警** 

```
isSupportOneKeyAlarm(deviceId : string): boolean
```

|**参数名称**|**参数类型**|**描述**|
|---|---|---|
|deviceID|string|设备ID|

返回: 

|**参数类型**|**描述**|
|---|---|
|boolean|true:支持,false:不支持|

### **24,是否支持一件报警设置** 

```
isSupportOneKeyAlarmSetting(deviceId : string): boolean
```

|**参数名称**|**参数类型**|**描述**|
|---|---|---|
|deviceID|string|设备ID|

##### 返回: 

|**参数类型**|**描述**|
|---|---|
|boolean|true:支持,false:不支持|

### **25,是否支持布防** 

```
isSupportDefences(deviceId : string): boolean
```

|**参数名称**|**参数类型**|**描述**|
|---|---|---|
|deviceID|string|设备ID|

##### 返回: 

|**参数类型**|**描述**|
|---|---|
|boolean|true:支持,false:不支持|

### **26,是否支持时光相册** 

```
isSupportAlbum(deviceId : string): boolean
```

|**参数名称**|**参数类型**|**描述**|
|---|---|---|
|deviceID|string|设备ID|

##### 返回: 

|**参数类型**|**描述**|
|---|---|
|boolean|true:支持,false:不支持|

**27,是否支持报警灯** 

```
isSupportAlarmLamp(deviceId : string) : boolean
```

|**参数名称**|**参数类型**|**描述**|
|---|---|---|
|deviceID|string|设备ID|

##### 返回: 

|**参数类型**|**描述**|
|---|---|
|boolean|true:支持,false:不支持|

### **28,是否支持人形定位** 

```
isSupportHumanRegion(deviceId : string) : boolean
```

|**参数名称**|**参数类型**|**描述**|
|---|---|---|
|deviceID|string|设备ID|

##### 返回: 

|**参数类型**|**描述**|
|---|---|
|boolean|true:支持,false:不支持|

### **29,是否支持预置位** 

```
isSupportPreset(deviceId: string): boolean
```

|**参数名称**|**参数类型**|**描述**|
|---|---|---|
|deviceID|string|设备ID|

##### 返回: 

|**参数类型**|**描述**|
|---|---|
|boolean|true:支持,false:不支持|

### **30,是否支持双向对讲** 

```
isDuplex(deviceId : string) : boolean
```

|**参数名称**|**参数类型**|**描述**|
|---|---|---|
|deviceID|string|设备ID|

返回: 

|**参数类型**|**描述**|
|---|---|
|boolean|true:支持,false:不支持|

### **31,是否支持物理变焦** 

```
isSupportPhysicalZoom(deviceId : string) : boolean
```

|**参数名称**|**参数类型**|**描述**|
|---|---|---|
|deviceID|string|设备ID|

##### 返回: 

|**参数类型**|**描述**|
|---|---|
|boolean|true:支持,false:不支持|

### **32,变倍模式** 

```
zoomModeAbility(deviceId : string) : ZoomTypeEnum
```

|**参数名称**|**参数类型**|**描述**|
|---|---|---|
|deviceID|string|设备ID|

##### 返回: 

|**参数类型**|**描述**|
|---|---|
|ZoomTypeEnum|变倍模式|

### **33,是否正在巡航** 

```
isItCruising(deviceId : string): boolean
```

|**参数名称**|**参数类型**|**描述**|
|---|---|---|
|deviceID|string|设备ID|

##### 返回: 

|**参数类型**|**描述**|
|---|---|
|boolean|true:是,false:否|

**34,是否支持3D定位** 

```
isSupport3DPosition(deviceId : string) : boolean
```

|**参数名称**|**参数类型**|**描述**|
|---|---|---|
|deviceID|string|设备ID|

返回: 

|**参数类型**|**描述**|
|---|---|
|boolean|true:是,false:否|

## **4,设备唤醒接口,(低功耗设备会休眠,所以需要唤醒后** **才可以播放视频,设置功能)** 

```
DeviceManager.getInstance().lowPowerConsumption(deviceId : string,listenCanUse :
boolean,callback ?: IStartRequestCallback)
```

|**参数名称**|**参数类型**|**描述**|
|---|---|---|
|deviceId|string|设备ID|
|listenCanUse|boolean|是否等待canuse状态才回调,canuse代表设备完全 启动|
|callback|IStartRequestCallback|接口回调|

## **5:请求权限工具类** 

### **PermissionUtil** 

### **1,请求权限** 

```
requestPermission(permissions : Permissions[],callback :
IRequestPermissionCallback)
```

|**参数名称**|**参数类型**|**描述**|
|---|---|---|
|permissions|Array|权限列表|
|callback|IRequestPermissionCallback|权限回调|

### **2,检查权限是否已授权** 

```
isPermission(permission : Permissions) : boolean
```

**参数名称 参数类型 描述** permission Permissions 要检查的权限 

返回: 

|**参数类型**|**描述**|
|---|---|
|boolean|true:是,false:否|

## **6,Wifi工具类** 

### **WifiTools** 

### **1,是否打开了系统WIFI开关** 

```
isOpenWifi() : boolean
```

返回: 

**参数类型 描述** boolean true:是,false:否 

### **2,获取wifi列表** 

```
getWifiList(isFilterDevAP : boolean) : ArrayList<WifiInfo>
```

**参数名称 参数类型 描述** isFilterDevAP boolean 是否过滤设备的WiFi 

返回: 

**参数类型 描述** ArrayList<WifiInfo> WiFi信息列表 

### **3,格式化IP地址** 

```
formatIpAddress(ipAddress : number)
```

|**参数名称**|**参数类型**|**描述**|
|---|---|---|
|ipAddress|number|ip地址|

返回: 

**参数类型** 

**描述** 

string 格式化后的Ip地址:192.168.x.x 

### **4,判断wifi列表是否包含传入的wifi** 

```
isContainWifi(wifiName : string) : boolean
```

|**参数名称**|**参数类型**|**描述**|
|---|---|---|
|wifiName|string|要判断的wifi|

##### 返回: 

|**参数类型**|**描述**|
|---|---|
|boolean|true :包含,false不包含|

### **5,获取当前移动设备连接的wifi** 

```
getCurrentWifiInfo() : Promise<wifiManager.WifiLinkedInfo>
```

返回: 

|**参数类型**|**描述**|
|---|---|
|Promise<wifiManager.WifiLinkedInfo>|异步回调,返回当前连接的wifi信息|

### **6,获取当前移动设备连接的wifi ip信息** 

```
getCurrentIPInfo() : wifiManager.IpInfo
```

返回: 

|**参数类型**|**描述**|
|---|---|
|wifiManager.IpInfo|设备当前连接wifi的IP信息|

### **7,获取当前移动设备连接的wifi ip信息** 

返回: 

|**参数类型**|**描述**|
|---|---|
|string|当前连接的设备AP格式化后的IP地址|

### **8,获取当前传入的ap 是否加密** 

```
isCurrentApSecurity(apName : string) : boolean
```

|**参数名称**|**参数类型**|**描述**|
|---|---|---|
|apName|string|ap名称|

返回: 

|**参数类型**|**描述**|
|---|---|
|boolean|true :加密,false不加密|

### **9,获取当前的ap 是否加密** 

```
isCurrentApHasPassword() : Promise<boolean>
```

##### 返回: 

**参数类型 描述** Promise 异步回调,返回当前ap是否加密,true 加密,false 不加密 

### **10,是否连接了wifi** 

```
isConnecteWifi() : boolean
```

##### 返回: 

|**参数类型**|**描述**|
|---|---|
|boolean|true: 连接了wifi,false没有连接WiFi|

### **11,获取国家码** 

```
getCountryCode() : string
```

##### 返回: 

|**参数类型**|**描述**|
|---|---|
|string|t返回国家吗CN|

**12,wifi连接状态变更监听,wifi系统开关状态变更监听** 

```
registerWifiStatuChange(callback : IWifiStatusCallback)
```

|**参数名称**|**参数类型**|**描述**|
|---|---|---|
|callback|IWifiStatusCallback|监听回调|

### **13,关闭wifi状态变更监听** 

```
unregisterWifiStatuChange()
```

## **7,下载视频或图片工具** 

### **DownloadImageUtil** 

### **1,下载http地址图片** 

```
downloadImage(url: string) : Promise<image.PixelMap>
```

|**参数名称**|**参数类型**|**描述**|
|---|---|---|
|url|string|下载的图片的URL|

##### 返回: 

|**参数类型**|**描述**|
|---|---|
|Promise<image.PixelMap>|异步回调,返回下载的图片|

### **2,下载http地址视频文件** 

```
downloadVideo(videoUrl: string, videoName?: string): Promise<string>
```

|**参数名称**|**参数类型**|**描述**|
|---|---|---|
|videoUrl|string|下载的图片的URL|
|videoName|string|视频名称,(可空)|

##### 返回: 

|**参数类型**|**描述**|
|---|---|
|Promise|异步回调,返回存储视频的绝对路径|

**3,下载图片后保存到文件** 

```
downloadAndSaveImage(imageUrl: string,savePath? : string): Promise<string>
```

|**参数名称**|**参数类型**|**描述**|
|---|---|---|
|imageUrl|string|下载的图片的URL|
|savePath|string|报错图片的路径,(可空)|

返回: 

|**参数类型**|**描述**|
|---|---|
|Promise|异步回调,返回存储视频的绝对路径|

### **4,保存文件到相册 只能是视频和图片** 

```
saveFileToPhotoAlbum(srcFilePaths: Array<string>, isVideo: boolean = false):
Promise<void>
```

|**参数名称**|**参数类型**|**描述**|
|---|---|---|
|srcFilePaths|Array|资源文件地址列表,|
|isVideo|boolean|是否是视频,默认是图片|

返回: 

|**参数类型**|**描述**|
|---|---|
|Promise|异步回调|

## **8,全局事件发送工具类** 

### **EventUtil** 

### **1,反注册事件监听** 

```
unregisterEvent(customeEventId : number)
```

|**参数名称**|**参数类型**|**描述**|
|---|---|---|
|customeEventId|number|自定义事件ID|

### **2,注册事件监听** 

```
registerEvent(eventId : number ,callback : EventCallback<emitter.EventData>)
```

|**参数名称**|**参数类型**|**描述**|
|---|---|---|
|eventId|number|自定义事件ID|
|callback|EventCallback<emitter.EventData>|事件接收回调|

##### 使用方式: 

```
EventUtil.registerEvent(EventConstants.LOGIN_EVENT_ID,{
  onCallback : (eventData : emitter.EventData) =>{
    let requestId : number = eventData.data?.requestId
    let error : number = eventData.data?.error
    //反注册事件监听
    EventUtil.unregisterEvent(EventConstants.LOGIN_EVENT_ID)
  }
})
```

### **3,注册字符串事件ID事件** 

```
registerStringEvent(eventId : string ,callback :
EventCallback<emitter.EventData>)
```

|**参数名称**|**参数类型**|**描述**|
|---|---|---|
|eventId|number|自定义事件ID|
|callback|EventCallback<emitter.EventData>|事件接收回调|

##### 使用方式: 

```
EventUtil.registerStringEvent(EventConstants.LOGIN_EVENT_ID,{
  onCallback : (eventData : emitter.EventData) =>{
    let requestId : number = eventData.data?.requestId
    let error : number = eventData.data?.errorCode
```

###### `// 反注册事件监听` 

```
    EventUtil.registerStringEvent(EventConstants.LOGIN_EVENT_ID)
  }
})
```

### **4,反注册字符串事件ID** 

```
unregisterStringEvent(eventID : string)
```

**参数名称 参数类型 描述** eventId number 自定义事件ID 

### **5,发送事件** 

```
sendEvent(eventId : number,data : object)
```

|**参数名称**|**参数类型**|**描述**||
|---|---|---|---|
|eventId|number|自定义事件ID||
|data|object|事件内容,任何数据类型,|但是接收的时候自己要强转|

#### **6,发送字符串事件ID的事件** 

```
sendStringEvent(eventId : string,data? : object)
```

|**参数名称**|**参数类型**|**描述**|
|---|---|---|
|eventId|string|自定义事件ID|
|data|object|事件内容,任何数据类型|

### **7,发送多参数事件** 

```
sendMoreEvent(eventId : number,eventData: emitter.EventData)
```

|**参数名称**|**参数类型**|**描述**|
|---|---|---|
|eventId|number|自定义事件ID|
|eventData|emitter.EventData|事件内容|

##### 使用方式: 

```
let eventData : emitter.EventData = {
  data : {
    requestId,
    errorCode
  }
}
EventUtil.sendMoreEvent(EventConstants.SERVER_EVENT_ID,eventData)
```

## **8,自定义LoadingDialog** 

### **CustomLoadingDialog** 

### **1,弹出loading** 

```
openLoadingDialog()
```

### **2,关闭loading** 

```
dismiss()
```

## **9,网络监听工具类** 

### **获取接口实例** 

```
NetWorkUtil.getInstance()
```

### **1,设置网络监听** 

```
setNetWorkLisener(netWorkListener : (isAvailable : boolean ) => void)
```

|**参数名称**|**参数类型**|**描述**|
|---|---|---|
|netWorkListener|(isAvailable : boolean ) => void|箭头函数,传入这个函数作为监听回调|

### **2,反注册监听** 

```
unRegister()
```

### **3,获取网络类型** 

```
getNetType(callback : (type : NetWorkTypeEnum) =>void)
```

|**参数名称**|**参数类型**|**描述**|
|---|---|---|
|callback|(type : NetWorkTypeEnum) =>void|箭头函数,传入这个函数作为监听回调,返回当前 网络类型|

## **10,轻量化存储工具类 使用的“用户首选项”** 

### **PreferencesUtil 单例,** 

### **1,获取实例,** 

```
getInstance(context? : Context) : PreferencesUtil
```

|**参数名称**|**参数类型**|**描述**|
|---|---|---|
|context|Context|可空|

返回: 

|**参数类型**|**描述**|
|---|---|
|PreferencesUtil|返回当前存储工具类实例|

### **2,获取实例,并且可链接指定存储的文件,取值的时候也需要用这 个获取实例** 

```
init(spName : string,context? : Context) : PreferencesUtil
```

|**参数名称**|**参数类型**|**描述**|
|---|---|---|
|spName|string|文件名称|
|context|Context|可空|

返回: 

|**参数类型**|**描述**|
|---|---|
|PreferencesUtil|返回当前存储工具类实例|

### **3,存储字符串数据** 

```
putString(key : string,value : string)
```

|**参数名称**|**参数类型**|**描述**|
|---|---|---|
|key|string|数据key|
|value|string|数据值|

### **4,删除指定key的数据** 

```
delete(key : string)
```

|**参数名称**|**参数类型**|**描述**|
|---|---|---|
|key|string|数据key|

**5,获取指定key的数据** 

```
getString(key : string,defaultValue : string) : string
```

|**参数名称**|**参数类型**|**描述**|
|---|---|---|
|key|string|数据key|
|defaultValue|string|默认数据|

返回: 

|**参数类型**|**描述**|
|---|---|
|string|返回对应key的数据,如果没有就返回默认数据|

### **6,存储number数据类型数据** 

```
putNumber(key : string,value : number)
```

|**参数名称**|**参数类型**|**描述**|
|---|---|---|
|key|string|数据key|
|value|number|默认数据|

### **7,获取number数据类型数据** 

```
getNumber(key : string,defaultValue : number) : number
```

|**参数名称**|**参数类型**|**描述**|
|---|---|---|
|key|string|数据key|
|defaultValue|number|默认数据|

##### 返回: 

|**参数类型**|**描述**|
|---|---|
|number|返回对应key的数据,如果没有就返回默认数据|

**8,存储boolean类型数据** 

```
putBool(key : string,value : boolean)
```

|**参数名称**|**参数类型**|**描述**|
|---|---|---|
|key|string|数据key|
|value|boolean|默认数据|

### **9,获取boolean类型数据** 

```
getBool(key : string,defaultValue : boolean) : boolean
```

|**参数名称**|**参数类型**|**描述**|
|---|---|---|
|key|string|数据key|
|defaultValue|boolean|默认数据|

返回: 

|**参数类型**|**描述**|
|---|---|
|boolean|返回对应key的数据,如果没有就返回默认数据|

### **10,删除首选项对应文件名称的文件** 

deletePreferences(fileName? : string) 

|**参数名称**|**参数类型**|**描述**|
|---|---|---|
|fileName|string|首选项文件名称|

## **11,提示音,音频播放工具类** 

### **PromptToneUtil 单例** 

### **1,播放本地存储的音频文件** 

```
avPlayerUrl(filePath : string,onProgress? : (progress : number, duration :
number) => void,playStop? : () =>void)
```

|**参数名称**|**参数类型**|**描述**|
|---|---|---|
|filePath|string|文件路径|
|onProgress|(progress : number, duration : number) => void|播放进度和文件播放时长回调 (可空)|
|playStop|() =>void|播放停止回调(可空)|

**2,播放app资源音频文件** 

```
avPlayerFdSrc(srcFileName : string)
```

|**参数名称**|**参数类型**|**描述**|
|---|---|---|
|srcFileName|string|资源文件名称|

使用方式: 

```
PromptToneUtil.getInstans().avPlayerFdSrc('promptTone/smokeiot.mp3')
```

### **3,本地文件播放,接着上次播放的位置继续播放** 

```
avPlayerDataSrcSeek(filePath : string)
```

**参数名称 参数类型 描述** filePath string 本地文件路径 

### **4,app本地资源文件播放,接着上次播放的位置继续播放** 

```
avPlayerDataSrcNoSeek(srcFileName : string)
```

**参数名称 参数类型 描述** srcFileName string 本地文件路径 

### **5,通过url设置网络地址进行播放** 

```
avPlayerLive(netUrl : string)
```

**参数名称 参数类型 描述** netUrl string 网络地址 

### **6,停止播放** 

```
stopPlayer()
```

### **7,释放播放器资源** 

```
destoryPlayer()
```

## **13,推送相关设置接口** 

### **PushManager 使用方式:直接创建** 

### **1,获取pushToken** 

```
getPushToken() : Promise<string>
```

##### 返回: 

|**参数类型**|**描述**|
|---|---|
|Promise|异步回调,返回token|

### **2,删除推送token** 

```
deletePushToken() : Promise<void>
```

##### 返回: 

|**参数类型**|**描述**|
|---|---|
|Promise|异步回调,返回成功失败|

### **3,将本地的pushToken提交到服务器** 

```
commitPushToken() : Promise<void>
```

##### 返回: 

|**参数类型**|**描述**|
|---|---|
|Promise|异步回调,返回成功失败|

#### **4,推送消息** 

```
pushLocalMessage(title : Resource, content: Resource)
```

|**参数名称**|**参数类型**|**描述**|
|---|---|---|
|title|Resource|消息title|
|content|Resource|消息内容|

### **5,清除状态栏消息** 

```
clearMessage(id : number)
```

## **14,视频插值工具类** 

### **RecordVideoReSampleUtils** 

### **1,获取当前回看类型的StreamId** 

```
getPlayBackStreamId(deviceId : string,isCloud : boolean) : number
```

|**参数名称**|**参数类型**|**描述**|
|---|---|---|
|deviceId|string|设备ID|
|isCloud|boolean|是否云回看类型|

返回: 

|**参数类型**|**描述**|
|---|---|
|number|流ID|

### **2,是否允许视频差值** 

```
recordVideoCanResample(deviceId : string,streamIndex : number) : boolean
```

|**参数名称**|**参数类型**|**描述**|
|---|---|---|
|deviceId|string|设备ID|
|streamIndex|number|流ID|

##### 返回: 

|**参数类型**|**描述**|
|---|---|
|boolean|true允许插值,false不允许插值|

### **3,录像差值到固定值** 

```
createVideoReSampleObservable(deviceId : string,filePath : string,streamIndex :
number) : Promise<boolean>
```

|**参数名称**|**参数类型**|**描述**|
|---|---|---|
|deviceId|string|设备ID|
|filePath|string|文件路径|
|streamIndex|number|流ID|

## **4,字符串工具类** 

### **StringUtil** 

### **1,资源文本转字符串** 

```
getString(source: Resource) : string
```

|**参数名称**|**参数类型**|**描述**|
|---|---|---|
|source|Resource|文本资源|

返回: 

|**参数类型**|**描述**|
|---|---|
|string|文本资源的字符串|

### **2,判断字符串是否是number类型** 

```
isNumber(value : string) : boolean
```

|**参数名称**|**参数类型**|**描述**|
|---|---|---|
|value|string|需要判断的字符串|

返回: 

|**参数类型**|**描述**|
|---|---|
|boolean|true是number类型,false不是number类型|

### **3,判断字符串是否包含数字** 

```
containWordNum(str : string) : boolean
```

|**参数名称**|**参数类型**|**描述**|
|---|---|---|
|str|string|需要判断的字符串|

##### 返回: 

|**参数类型**|**描述**|
|---|---|
|boolean|true包含,false不包含|

### **4,是否不存在非法字符** 

```
isLegal(str : string) : boolean
```

**参数名称 参数类型 描述** str string 需要判断的字符串 

返回: 

**参数类型 描述** boolean true 不包含,false 包含 

### **5,number数据如果是个位数前面补0** 

```
formatNumberWithLeadingZero(num : number) : string
```

**参数名称 参数类型 描述** num number 需要判断是否补0的数字 返回: **参数类型 描述** string 判断补0后的字符串 

## **5,系统设置页面或系统事件工具类** 

### **SystemEvent** 

### **1,锁屏监听亮屏监听** 

```
monitorScreen(resultCallback : (isScreenLitUp : boolean) => void)
```

**参数名称 参数类型 描述** resultCallback (isScreenLitUp : boolean) => void 箭头函数回调监听 

### **2,打开系统授权页面** 

```
openSystemAccreditAbility()
```

### **3,打开系统通知设置页面** 

```
openSystemNoticeAbility()
```

### **4,打开系统wifi开关设置页面** 

```
openSystemWifiSwitchSetting()
```

## **6,系统分享工具类** 

### **SystemSharedUtil** 

### **1,分享图片** 

```
sharedImage(imagePath : string,shareMode : systemShare.SharePreviewMode)
```

|**参数名称**|**参数类型**|**描述**|
|---|---|---|
|imagePath|string|图片地址|
|shareMode|systemShare.SharePreviewMode|分享模式,默认 systemShare.SharePreviewMode.DEFAULT|

### **2,分享视频** 

```
sharedVideo(filePath : string,shareMode : systemShare.SharePreviewMode)
```

|**参数名称**|**参数类型**|**描述**|
|---|---|---|
|filePath|string|视频地址|
|shareMode|systemShare.SharePreviewMode|分享模式,默认 systemShare.SharePreviewMode.DEFAULT|

### **3,分享文件** 

```
sharedFile(filePath : string,shareMode : systemShare.SharePreviewMode)
```

|**参数名称**|**参数类型**|**描述**|
|---|---|---|
|filePath|string|文件地址|
|shareMode|systemShare.SharePreviewMode|分享模式,默认 systemShare.SharePreviewMode.DEFAULT|

### **4,分享多图片** 

```
sharedImagePathList(fileList : Array<string>)
```

|**参数名称**|**参数类型**|**描述**|
|---|---|---|
|fileList|Array|多文件图片地址列表|

### **5,分享多图片** 

```
sharedPixelMapList(pixelMapList : Array<image.PixelMap>,shareMode :
systemShare.SharePreviewModeL)
```

|**参数名称**|**参数类型**|**描述**|
|---|---|---|
|pixelMapList|Array<image.PixelMap>|多图片列表|
|shareMode|systemShare.SharePreviewMode|分享模式,默认 systemShare.SharePreviewMode.DEFAULT|

## **7,文本样式工具类** 

### **TextStyleUtil 单例** 

### **1,修改一段文本的颜色** 

```
getTextController(content : string,startIndex : number,endIndex : number,isBold :
boolean,textSize : number,color? : ResourceColor) : TextController
```

|**参数名称**|**参数类型**|**描述**|
|---|---|---|
|content|string|文本内容|
|startIndex|number|改颜色文本开始角标|
|endIndex|number|改颜色文本结束角标|
|isBold|boolean|是否加粗|
|textSize|number|文本size传0不修改size|
|color|ResourceColor|颜色|

##### 返回: 

|**参数类型**|**描述**|
|---|---|
|TextController|可以设置给Text组件的TextOptions,|

### **2,修改一段文本的颜色** 

```
getTextStyleString(content : string,startIndex : number,endIndex : number,isBold
: boolean,textSize : number,color? : ResourceColor) : MutableStyledString
```

|**参数名称**|**参数类型**|**描述**|
|---|---|---|
|content|string|文本内容|
|startIndex|number|改颜色文本开始角标|
|endIndex|number|改颜色文本结束角标|
|isBold|boolean|是否加粗|
|textSize|number|文本size传0不修改size|
|color|ResourceColor|颜色|

##### 使用方式: 

```
let controller1: TextController = new TextController();
controller1.setStyledString(this.messageContentStyle)
let options: TextOptions = {controller: this.controller1};
Text(options)
```

## **8,文件大小单位工具类 ,比如 kb mb,gb** 

### **UnitUtils** 

### **1,格式化数据长度,返回带单位的字符串 'B', 'K', 'M', 'G', 'T'** 

```
formatBytes(bytes : number ,decimals?  : number) : string
```

|**参数名称**|**参数类型**|**描述**|
|---|---|---|
|bytes|number|数据长度|
|decimals|number|保留几位小数,默认是0|

##### 返回: 

|**参数类型**|**描述**|
|---|---|
|string|格式化后的字符串|

### **2,格式化数据长度,返回带单位的字符串 'B', 'KB', 'MB', 'GB', 'TB'** 

```
formatByte(bytes : number ,decimals?  : number) : string
```

|**参数名称**|**参数类型**|**描述**|
|---|---|---|
|bytes|number|数据长度|
|decimals|number|保留几位小数,默认是0|

返回: 

|**参数类型**|**描述**|
|---|---|
|string|格式化后的字符串|

## **9,震动工具类** 

### **VibratorUtil 单例** 

### **1,开始震动** 

```
startVibrator()
```

### **2,停止震动** 

```
stopVibrator()
```

## **10,window工具类,比如页面全屏,状态栏颜色修改等** 

### **WindowUtils** 

### **1,设置页面是否全屏** 

```
setPageFullScreen(isFullScreen: boolean)
```

|**参数名称**|**参数类型**|**描述**|
|---|---|---|
|isFullScreen|boolean|true全屏,false非全屏|

### **2,设置全屏是否隐藏状态栏** 

```
setPageFullScreenHindSystemBar(isShowSystemBar : boolean)
```

|**参数名称**|**参数类型**|**描述**|
|---|---|---|
|isShowSystemBar|boolean|true显示状态栏,false不显示状态栏|

### **3,设置窗口的状态栏颜色** 

```
setWindowSystemBarColor(colorStr : string,statusBarContentColor : string)
```

|**参数名称**|**参数类型**|**描述**|
|---|---|---|
|isFullScreen|boolean|true全屏,false非全屏|
|statusBarContentColor|string|颜色值 如 :#ffffff|

**4,监听屏幕变化,横竖屏监听** 

```
monitorHorizontallyVertically(onResultCall : (isLandscape : boolean) =>void)
```

|**参数名称**|**参数类型**|**描述**|
|---|---|---|
|onResultCall|(isLandscape : boolean) =>void|函数回调,isLandscape,true:横屏,false : 竖屏|

### **5,取消监听屏幕变化,横竖屏监听** 

```
unmonitorHorizontallyVertically()
```

### **6,设置屏幕方向** 

```
setOrientation(orientation : window.Orientation)
```

|**参数名称**|**参数类型**|**描述**|
|---|---|---|
|orientation|window.Orientation|横竖屏切换实例|

### **7,获取屏幕方向,横屏还是竖屏** 

```
isLandOrientation() : boolean
```

### **8,开启禁止截屏** 

```
setWindowPrivacyMode(context : Context,isPrivacy : boolean)
```

|**参数名称**|**参数类型**|**描述**|
|---|---|---|
|context|Context|上下文|
|isPrivacy|boolean|是否禁止截屏|

## **11,SDK工具类** 

### **ZJUtil** 

### **1,获取app当前的语言码** 

```
getCurLanguage() : LanguageEnum
```

返回: 

**参数类型** 

**描述** 

LanguageEnum 

语言码枚举 

### **2,读取文件数据** 

```
readFile(filePath: string): ArrayBuffer
```

**参数名称 参数类型 描述** filePath string 文件路径 

##### 返回: 

##### **参数类型 描述** ArrayBuffer 文件数据 

### **3,获取版本名称** 

```
getVersionName(): string
```

##### 返回: 

|**参数类型**|**描述**|
|---|---|
|string|app版本号,如:1.0.3|

### **4,获取版本号** 

```
getVersionCode(): Promise<string>
```

##### 返回: 

|**参数类型**|**描述**|
|---|---|
|Promise|异步回调,成功回调版本号|

### **5,线程执行到这里后等待多少毫秒后执行下一步,** 

```
  /**
   * 休眠多少毫秒
   * @param ms  毫秒
   * @return s
   */
  public static sleep(ms: number) {
    return new Promise<void>(resolve => setTimeout(resolve, ms))
  }
```

**6,解析二维码数据** 

```
parseQRCode(codeStr: string, callback: IScanCodeCallback)
```

|**参数名称**|**参数类型**|**描述**|
|---|---|---|
|codeStr|string|二维码识别结果|
|callback|IScanCodeCallback|接口回调|

### **7,获取国家码** 

```
getCountryID() : Promise<string>
```

返回: 

|**参数类型**|**描述**|
|---|---|
|Promise|异步回调,成功回调国家码|

### **8,是否json字符串** 

```
isJson(str: string): boolean
```

|**参数名称**|**参数类型**|**描述**|
|---|---|---|
|str|string|要判断的字符串|

##### 返回: 

|**参数类型**|**描述**|
|---|---|
|boolean|true是json数据,false不是json数据|

# **34,枚举** 

### **RegionIdEnum** 

|**枚举名称**|**枚举值**|**说明**|
|---|---|---|
|DOMESTIC|0x01|国内|
|FOREIGN|0x02|海外|

### **ServerStatusEnum** 

|**枚举名称**|**枚举值**|**说明**|
|---|---|---|
|UNKNOWN|-1|什么状态都不是|
|INIT|0|初始化状态|
|GET_ADDR|1|正在获取地址|
|CONNECT|2|连接中|
|LOGIN|3|登录中|
|SUCCESS|4|成功|
|INTERRUPT|5|中断|

### **AccountTypeEnum** 

|**枚举名称**|**枚举值**|**说明**|
|---|---|---|
|UNKNOWN|-1||
|EMAIL|1|邮箱账号|
|PHONE|2|手机号|
|ALIPAY|3|支付宝账号|
|WEIXIN|4|微信账号|
|QQ|5|QQ账号|
|SFZ|6||
|TAOBAO|7|淘宝账号|
|FB|8|Facebook账号|
|TWITER|9|twitter账号|
|GOOGLE|10|谷歌账号|
|WEIBO|11|微博账号|
|WECHAT_PLATFORM|14|微信公众平台|
|BAIDU|15|百度账号|
|HUAWEI|18|华为账号|
|USRMNG|||
|DEFAULT|||
|PLATFORM_VERIFICATION|||

### **VerifyCodePlatEnum** 

|**枚举名称**|**枚举值**|**说明**|
|---|---|---|
|UNKNOWN|-1||
|MOBSDK|1|MobSDK|
|ZJSDK|2|ZJSDK|
|EMAILSDK|3|邮件|
|AUTO|255|由平台选择|

### **DeviceTypeEnum** 

|**枚举名称**|**枚举值**|**说明**|
|---|---|---|
|UNKNOWN|-1||
|CAMERA|1|摄像机|
|DOORBELL_SPLIT|2|分体门铃|
|DOORBELL_SINGLE|3|单体门铃|
|NVR|4|NVR|
|NAS|5|nas产品|
|SOLAR_PANEL|6|太阳能,低功耗|
|GATEWAY|7|网关|
|BLUETOOTH_DEVICE|8|蓝牙|
|PICTURE_DOORBELL|9|拍照门铃|
|AIBOX|3103|AIBOX|

### **OSTypeEnum** 

|**枚举名称**|**枚举值**|**说明**|
|---|---|---|
|UNKNOWN|-1||
|LINUX|1|设备系统|
|IOS|2|设备系统|
|ANDROID|3|设备系统|
|ANDROID_TV|4|设备系统|
|WINDOWS|5|设备系统|
|RTOS|6|设备系统|

### **ErrorEnum** 

|**枚举名称**|**枚举值**|**说明**|
|---|---|---|
|ERR|-1||
|ERR_PARAM|-2||
|ERR_NOMEM|-3||
|ERR_NOINIT|-4||
|ERR_NORES|-5||
|ERR_OVERFLOW|-6||
|ERR_MAGIC_N|-7||
|ERR_KEY_UNEXIST|-8||
|ERR_FILE_EXIST|-9||
|ERR_AUTHORITY|-10||
|ERR_CLOSE|-11||
|ERR_SUPPORT|-12||
|ERR_NOADDR|-13||
|ERR_FREQUENTLY|-14||
|ERR_TRYAGAIN|-15||
|ERR_FULL|-16||
|ERR_SPEAK_LIMIT|-17||
|ERR_NET|-80||
|ERR_TIMEOUT|-83||
|DES_CHANGE|-100||
|ERR_FILEEND|-101||
|ERR_FILEWAIT|-102||
|ERR_EXIST|-110||
|SUCCESS|0|请求成功|
|CHARACTER|1001|配置WIFI时,传入SSID有无效字符|
|NO_WIFI_MODULE|1002|查询WIFI列表,设备没有WIFI模块|
|WIFI_IS_CLOSE|1003|查询WIFI列表,WIFI模块关闭|
|SIGN_NO_SVR_DISTRI|1101|SIGN分配服务时,没有可分配的服务|
|FREQUENT_OPERATION|1103|访问频繁|
|COMPANY_ID_INVALID|1111|鉴权的企业ID不存在|

|**枚举名称**|**枚举值**|**说明**|
|---|---|---|
|COMPANY_NO_PRIVILEGE|1112|鉴权的企业ID对应的企业被平台禁用|
|APP_ID_INVALID|1113|鉴权传入的AppID在企业下不存在|
|APP_ID_NO_PRIVILEGE|1114|鉴权传入的AppID没有权限|
|LICENSE_NOT_EXIST|1115|传入授权的CTEI码没有找到|
|LICENSE_EXPIRE|1116|授权用的CTEI码已经过期|
|LICENSE_DISABLE|1117|授权用的CTEI码被平台禁用|
|APP_HAVE_NO_LICENSE_COUNT|1118|按量授权的AppID下无可用的授权数量|
|DEVICE_NO_THERE|1121|设备登陆传入的设备ID无效,设备收到该错 误码,重新注册新的ID|
|DEVICE_DISABLE|1122|该设备被平台禁用,设备无法上云|
|DEVICE_VERSION_DISABLE|1123|设备版本太旧,系统不再兼容。设备此时需 要进行升级|
|DEVICE_SVR_CALL_FAILED|1131|设备配置管理系统访问报错|
|DEVICE_NO_BUSI_CONFIG|1141|设备尚未上传业务配置|
|RESOLUTION_ABILITY_NOT_SUPPORT|1142|设置的设备分辨率,当前设备不支持|
|RESOLUTION_BUSI_NOT_SUPPORT|1143|设置的设备分辨率,可能因业务限制不支持 (授权限制)|
|PTZ_IS_MAX|1144|设备执行PTZ已经转到最大值|
|EXIT_GROUP_ERR|1146|设备要出的组,不是设备当前的组,出组失 败|
|SDCARD_FORMATTING_ERR|1148|设备格式化SD失败|
|SDCARD_NOT_EXIST|1149|格式化SD卡时,SD卡不存在|
|SDCARD_WR_ERR|1150|读写SD卡时,操作失败|
|ADD_CHILD_DEVICE_TIMEOUT|1151|添加HUB子设备时,通信超时,失败|
|CHILD_DEVICE_EXIST|1152|添加HUB子设备时,设备ID重复|
|HUB_OPT_ERR|1153|HUB发生异常,操作失败|
|QUERY_RECORD_NO_PRIVILEGE|1154|当前查询记录没有操作权限|
|CLOUD_SVR_CALL_FAILED|1155|无法访问当前云存记录服务|
|LOCAL_RECORD_NOT_EXIST|1156|当前查询详情的本地记录文件已被清理|
|CLOUD_FILE_EXPIRE|1157|当前查询的云记录文件已经过期|
|BIND_CODE_EXIST|1158|绑定码已存在|

|**枚举名称**|**枚举值**|**说明**|
|---|---|---|
|BIND_CODE_NOT_EXIST|1159|绑定码不存在|
|BIND_CODE_EXPIRE|1160|绑定码已过期|
|BIND_CODE_USED|1161|绑定码已使用|
|SVR_CANNOT_SEND_SMS_ERR|1163|无法发送短信|
|ACCOUNT_IS_EXIST|2001|账号已存在|
|REG_OTHER_ERR|2003|其他注册失败原因|
|ACCOUNT_NOT_EXIST|2004|账号不存在|
|USER_ACCOUNT_PWD_ERR|2005|User登录账号密码错误|
|VERIFY_OPENID_ERR|2006|第三方登陆时,第三方校验失败|
|ACCOUNT_FORBIDDEN|2007|登陆时,发现账户已经被禁用|
|UTOKEN_NOT_EXIST|2008|UTOKEN不存在|
|SMS_CODE_FREQUENT|2009|两次获取短信验证码时间过短,返回失败|
|USER_REJECT_INVITE|2010|给用户发送分享邀请,被邀请者拒绝|
|GTOKEN_NOT_MATCH|2011|通过Gtoken入组,Gtoken失效|
|DEVICE_IS_IN_GROUP|2012|添加设备进组时失败,设备已经加入了另一 个组|
|USER_NO_PRIVILEGE|2013|用户无操作权限|
|ACCOUNT_TYPE_NOT_SUPPORT|2014|获取短信验证码时,不支持手机邮箱以外的 方式获取|
|ACCOUNT_FORMAT_ERR|2015|账号格式错误|
|ACCOUNT_ALREADY_BIND|2016|账号已被绑定|
|ACCOUNT_BIND_ERR|2017|绑定账号错误|
|FILEID_NOT_EXIST|2018|云存储文件ID不存在|
|DEVICEID_NOT_EXIST|2019|设备ID不存在|
|ERR_4GCARDNO_NOT_EXIST|2020|4G卡号不存在|
|ERR_4GCARDNO_REPORT_ERR|2021|4G卡号汇报失败|
|APPID_NOTFOUND_TEMPLATE|2027|APPID未找到对应的短信/ems模板|
|FILE_NOT_EXIST|2028|文件不存在|
|SMS_SEND_FREQUENCY_LIMIT_ERR|2033|单个手机号码在规定时间内短信发送达到上 限|
|SHARE_DEVICE_ERR|2201|分享失败|

|**枚举名称**|**枚举值**|**说明**|
|---|---|---|
|QRCODE_INVALID|2202|无效的二维码|
|REMOVE_DEVICE_ERR|2203|设备出组失败|
|REPEAT_PURCHASE|2205|套餐重复购买|
|VERIFICATION_CODE_NOT_EXIST|2207|验证码不存在|
|DEVICE_P2P_NOT_SUPPORT|3001|当用户向设备请求P2P时,设备返回不支持 P2P|
|CONN_NOT_MATCH|3002|用户与设备的P2P连接校验不匹配|
|MEDIA_MATCH_TIMEOUT|3003|用户和设备在MEDIA上配对超时|
|MEDIA_CHANNEL_NOT_EXIST|3004|媒体操作时,对应的ChannelID不存在|

|**枚举名称**|**枚举值**|**说明**|
|---|---|---|
|MEDIA_PLAY_UPPER_LIMIT|3005|点播流媒体时,人数超上限|
|MEDIA_INVALID|3006|流媒体服务时,资源过期或无效|
|MALLOC_ERR|4001|服务申请内存对象错误|
|JSON_DECODE_ERR|4002|服务解析JSON协议错误|
|JSON_ENCODE_ERR|4003|服务构造JSON字符串错误|
|API_PARAM_ERR|4004|API调用参数错误|
|METHOD_ERR|4005|API返回NIL|
|ENCRYPT_ERR|4006|协议加密错误|
|DECRYPT_ERR|4007|协议解密错误|
|BUF_READ_ERR|4008|链接读取BUFFER错误|
|TLS_PEM_KEY_ERR|4009|TLS链接找不到PEM KEY文件错误|
|AUTH_ATOKEN_ERR|4010|服务器之间访问调用ATOKEN出错|
|REDIS_PUB_ERR|4011|Redis服务访问错误|
|DB_CONNECT_ERR|4012|数据库连接失败|
|DB_INSERT_ERR|4013|数据库数据插入失败|
|DB_SELECT_ERR|4014|数据库数据查询失败|
|DB_UPDATE_ERR|4015|数据库数据更新失败|
|DB_DELETE_ERR|4016|数据库数据删除失败|
|DB_NO_RECORD_ERR|4017|没有找到相关记录|
|DB_DUPLICATE_KEY|4018|主键重复|
|NET_LISTEN_ERR|4019|服务端口侦听错误|
|CLOSED|4020|服务关闭错误|
|IDSVR_NOT_FOUND|4021|IDSVR服务找不到|
|IDSTUNSVR_NOT_FOUND|4022|IDSTUN服务找不到|
|BUSISVR_NOT_FOUND|4023|BUSICENTRE服务找不到|
|MEDIASVR_NOT_FOUND|4024|媒体服务找不到|
|LINKSVR_NOT_FOUND|4025|LINK服务找不到|
|USERSVR_CALL_FAILED|4026|用户系统接口调用失败|
|IDSVR_CALL_FAILED|4027|IDSVR系统接口调用失败|
|IDSTUN_CALL_FAILED|4028|IDSTUN系统接口调用失败|

|**枚举名称**|**枚举值**|**说明**|
|---|---|---|
|PUSHSVR_NOT_FOUND|4029||
|GATEWAYSVR_CALL_FAILED|4030||
|COMPMNGSVR_CALL_FAILED|4031||
|PUBSUBSVR_NOT_FOUND|4032||
|SYSNOTICESVR_NOT_FOUND|4033||
|GATEWAYSVR_NOT_FOUND|4034||
|HTTPSVR_NOT_FOUND|4035||
|HTTPSVR_CALL_FAILED|4036||
|BUSISVR_CALL_FAILED|4037||
|ID_CALL_FAILED|4038||
|SIGN_CALL_FAILED|4039||
|LINK_CALL_FAILED|4040||
|LOGSVR_CALL_FAILED|4041||
|USERSVR_NOT_FOUND|4042||
|SYSNOTICESVR_CALL_FAILED|4043||
|PUBSUBSVR_CALL_FAILED|4044||
|DYNAMICMETHOD_CALL_FAILED|4045||
|PLAYLOAD_IS_FULL|4046||
|GRPCSVR_CALL_FAILED|4047||
|DEVICESVR_NOT_FOUND|4048||
|EVENTSVR_NOT_FOUND|4049||
|ZONE_NOT_FOUND|4050||
|NET_WRITE_BLOCK|4051||
|SOCKET_CLOSED|4052||
|SOCKET_READERR|4053||
|ID_PARSEERR|4054||
|NET_DNSPARSE_ERR|4055||
|NET_REQ_TIMEOUT|4056||
|SUBPUB_TOKEN_NOTEXIST|4057||
|SOCKET_ACCEPT_ERROR|4058||

|**枚举名称**|**枚举值**|**说明**|
|---|---|---|
|OPERATION_TOO_FREQUENT|4059||
|PARSE_IP_ERR|4060||
|GETSVRPUBKEY_ERR|4061|//获取pubkey|
|LINKNOTICESVR_NOT_FOUND|4062||
|ENCRYPTTYPE_ERROR|4064||
|VIDEOSVR_NOT_FOUND|4065||
|EXCEPTIONSVR_NOT_FOUND|4066||
|LOGSVR_NOT_FOUND|4067||
|OPRECORDSVR_NOT_FOUND|4068||
|NATSTUNSVR_NOT_FOUND|4069||
|COMBO_CALL_FAILED|4070||
|COMBO_NOT_FOUND|4071||
|GROUPNOTHERE|4407|组不存在|
|DEVICENOTINGROUP|4409|Device不在组里|
|WAKEUP_DEVICEERR|4422|唤醒出错|
|DEVICEOFFLINE|4602|Device不在线|
|DEVICE_ISSLEEP|4610|设备已休眠|
|HAVENOGROUPS|4612|没有组列表|
|REG_AUTH_ERR|5001|SIGN服务注册SVRID&SVRPWD校验错误|
|SIGN_ATOKEN_NOT_EXIST|5002|SIGN服务通过SVR ATOKEN找不到服务|
|SIGN_MANAGE_NOMETHOD|5004||
|GENERALUTOKEN_ERR|5005|BUSI生成UTOKEN错误|
|UTOKEN_NOTAUTHED|5006||
|USERNOTHERE|5007||
|USERISINGROUP|5011||
|ROLENOTEXIST|5013||
|CHILDGROUPNOTEXIST|5014||
|ROLEISINUSE|5015||
|GROUPISINGROUP|5016||
|USERNOTINGROUP|5017||

|**枚举名称**|**枚举值**|**说明**|
|---|---|---|
|GROUPNOTINGROUP|5019||
|DEVICEISSLEEP|5021||
|ID_MAXIDINDEX_GETERR|5024||
|APPNOTEXIST|5026||
|APPDISABLE|5027||
|APPAUTHTYPE_ERR|5031||
|APPISEXIST|5032||
|ACCOUNTTYPENOTBIND|5034||

|**枚举名称**|**枚举值**|**说明**|
|---|---|---|
|APPAUTHTYPENOTSUPPORT|5036||
|DEVICE_NOT_AUTH|5038||
|UTOKEN_NOT_AUTH|5039||
|DEVICE_FORBIDDEN|5040||
|UTOKEN_FORBIDDEN|5041||
|UTOKEN_CHECKERR|5042||
|SYSCOMMAND_FAIL|5043||
|PUSHTEMPLATENOTEXIST|5044||
|DEVICE_LIMIT_AUTH|5045||
|SIGN_SVRKEY_NOTEXIST|5046||
|SVRPUBKEY_NOTEXIST|5047||
|FILETYPE_NOTEXIST|5048||
|SUBPUB_SUBJ_NOT_EXIST|8000||
|SUBPUB_ID_TYPE_NOT_SUPPORT|8001||
|NOTICE_QUEUE_WRITE_ERR|8002||
|NOTICE_PROTO_NOT_SUPPORT|8003||
|LANGUAGE_NOT_EXIST|8004||
|SUBPUB_PUBLISH_MSG_ERR|8005||
|NOTICE_JUMP_NOTIE_SUPPORT|8006||
|SIGNAL_NOT_SUPPORT|9001|所发送的指令,对方不支持该指令集;(版本/ 型号错误导致)|
|SERVICE_TIMEOUT|9002|指令发送后,超过超时时间仍没有回应;|
|SIGNAL_ALREADY_CACHE|9003|通过服务端转发信令,设备支持信令缓存,设 备在线,则回应。|
|SIGNAL_DISCARD|9004|通过服务端转发信令,不支持信令缓存,设备 不在线,则回应。|
|CMD_NOT_SUPPORT|9010|版本较旧,或设备类型不符合不支持当前指 令。|
|DEVICE_REG_FORBIDDEN|9030|设备注册无权限,或服务限制,设备不再重试|
|DEVICE_LOGIN_FORBIDDEN|9031|设备登陆被禁用,设备不再重试|
|QR_CREATE_FAIL|10000|生成二维码失败,|

|**枚举名称**|**枚举值**|**说明**|
|---|---|---|
|CANT_SHARE_SELF|10001|无法分享自己|
|DEVICE_NOT_REMOVE|10002||
|ALREADY_LOGGED|10999|已经登录了,请先退出登录|
|TIME_OUT|99999|请求超时|

### **DeviceStatusEnum** 

|**枚举名称**|**枚举值**|**说明**|
|---|---|---|
|ONLINE|1|在线|
|OFFLINE|2|离线|
|SLEEP|3|休眠|
|UPGRADE|4|升级中|
|CANUSE|5|通道可用|
|SIM_LIMIT|7|SIM卡未授权|

### **AwakeAbilityEnum** 

|**枚举名称**|**枚举值**|**说明**|
|---|---|---|
|UNKNOWN|-1||
|NOT_SUPPORT|0x00|不支持休眠|
|LOCAL_AWAKE|0x01|支持本地唤醒|
|REMOTE_AWAKE|0x02|支持远程唤醒|
|SUPPROT_AWAKE|0x01 | 0x02|支持远程唤醒|

### **DefaultPolicyIDEnum** 

|**枚举名称**|**枚举值**|**说明**|
|---|---|---|
|TIME_RECORD_1|1|定时录像1|
|TIME_RECORD_2|2|定时录像2|
|TIME_RECORD_3|3|定时录像2|
|TIME_RECORD_4|4|定时录像2|
|TIME_DNSET_1|10|红外灯时间段控制1|
|TIME_DNSET_2|11|红外灯时间段控制2|
|TIME_WHITE_LAMP_CTRL_1|20|白光灯时间段控制1|
|TIME_WHITE_LAMP_CTRL_2|21|白光灯时间段控制2|
|TIME_WHITE_LAMP_CTRL_3|22|白光灯时间段控制3|
|TIME_WHITE_LAMP_CTRL_4|23|白光灯时间段控制4|
|TIME_INTELLIGENT_CRUISE|100600|智能巡航起始位置|
|TIME_BROADCAST_PERIOD|100900|播报时间段的起始位置|
|MOTION_ALARM|100|运动侦测报警|

### **NetWorkTypeEnum** 

|**枚举名称**|**枚举值**|**说明**|
|---|---|---|
|UNKNOWN|-1||
|NONET|0|无网络|
|WIRED|1|有线|
|WIFI|2|无线|
|AP|3|AP模式|
|SIM|8|移动网络5G|
|SIM1|9|移动网络2G|
|SIM2|10|移动网络3G|
|SIM3|11|移动网络4G|

### **OSDPositionEnum** 

|**枚举名称**|**枚举值**|**说明**|
|---|---|---|
|UNKNOWN|-1||
|DEFAULT|0|默认左上角|
|LEFT_UP|1|左上角|
|LEFT_DOWN|2|左下角|
|RIGHT_UP|3|右上角|
|RIGHT_DOWN|4|右下角|

### **IRModeEnum** 

|**枚举名称**|**枚举值**|**说明**||
|---|---|---|---|
|AUTO|0|红外灯:夜晚打开,白天关闭; 白天不亮。|白光灯:发生报警后,晚上点亮,|
|AUTO_NOLAMP|1|红外灯:夜晚打开,白天关闭;|白光灯:关闭|
|FULLCOLOR|2|红外灯:长关, 白光灯:常开,|(固件会晚上点亮,白天关闭)。|
|NATURAL|3|红外灯:关闭 白光灯:关闭||
|IR|4|红外灯:常亮; 白光灯:常关。||

### **InversionTypeEnum** 

|**枚举名称**|**枚举值**|**说明**|
|---|---|---|
|NOT_SUPPORT|0|不支持翻转|
|VERTICAL_UP|0x01|水平向上|
|VERTICAL_DOWN|0x02|水平向下|
|MIRROR_ENABLE|0x04|开启镜像|
|MIRROR_DISABLE|0x08|禁用镜像|

### **PTZCtrlTypeEnum** 

|**枚举名称**|**枚举值**|**说明**|
|---|---|---|
|UNKNOWN|-1||
|UP|1|上|
|DOWN|2|下|
|LEFT|3|左|
|RIGHT|4|右|

### **RingTypeEnum** 

|**枚举名称**|**枚举值**|**说明**|
|---|---|---|
|PROMPT_TONE|0x01|提示音(快捷回复)|
|DOORBELL|0x02|门铃铃声|
|ALARM|0x04|警戒音|

### **EnergyModeEnum** 

|**枚举名称**|**枚举值**|**说明**|
|---|---|---|
|UNKNOWN|0||
|LONG_TELEGRAM_MODE|1|正常工作模式 支持亮白灯,定时录制,支持本地唤醒和远 程唤醒, 红外灯切换阈值正常|
|LOW_ENERGY_MODE|2|节能模式 白灯不亮,只有报警录制,支持本地唤醒和远程 唤醒, 红外灯 切换阈值衰减三分之一|
|SUPER_LOW_ENERGY_MODE|3|低功耗模式 不亮白灯,不录制,仅仅支持远程唤醒 红外灯 阈值继续衰减三分之一|

### **CamLensTypeEnum** 

|**枚举名称**|**枚举值**|**说明**|
|---|---|---|
|UNKNOWN|-1||
|NORMAL|0|默认|
|LENS_360|1|360度|
|LENS_720|2|720度|
|NO_CROP360|3||

### **ZoomAbilityModeEnum** 

|**枚举名称**|**枚举值**|**说明**|
|---|---|---|
|ALL_WAY_UP|1|一直放大(不支持精准,不带刻度)|
|SPECIFIED_MULTIPLE|2|指定倍数(支持精准 带刻度的)|
|ALL_SUPPORT|3|都支持|
|APP_ELECTRONIC_ZOOM|4|app电子变倍|

### **ThreeDGestureTypeEnum** 

|**枚举名称**|**枚举值**|**说明**|
|---|---|---|
|NONSUPPORT|0|不支持|
|THREE_D_CENTER|1|3D居中|
|THREE_D_POSITION|2|3D定位(带定位线的)|

### **MutateTypeEnum** 

|**枚举名称**|**枚举值**|**说明**|
|---|---|---|
|ORIGINAL_SOUND|0|原声|
|GIRL_VOICE|1|大叔音|
|UNCLE_SOUND|2|萝莉音|
|MALE_VOICE|3|男声|
|FEMALE_VOICE|4|女声|

### **CargePackageStatusEnum** 

|**枚举名称**|**枚举值**|**说明**|
|---|---|---|
|NONE_CLOUD_SERVICE|-99||
|HAVE_NOT_OPENED_STATUS|0|未开通套餐状态|
|HAVE_OPENED_STATUS|1|已开通套餐状态|
|ABOUT_TO_EXPIRE_STATUS|2|即将过期套餐状态|
|EXPIRED_STATUS|3|已过期套餐状态|
|WAIT_EFFECT_STATUS|4|待生效套餐状态|
|NO_SUPPORT_STATUS|5|不支持套餐|

### **CloudChargeTypeEnum云服务套餐枚举** 

|**枚举名称**|**枚举值**|**说明**|
|---|---|---|
|DYA_CHARGE|1|全天套餐|
|EVENT_CHARGE|2|事件套餐|

### **AIIoTTypeEnum** 

|**枚举名称**|**枚举值**|**说明**|
|---|---|---|
|UNKNOWN|-1||
|REMOTE_CTRLER|0|遥控器|
|DOOR_SWITCH|1|门磁|
|SMOKE_TRANSDUCER|2|烟雾传感器|
|GAS_SENSOR|3|燃气 探测 传感器|
|LIGHT_SWITCH|4|电灯|
|CURTAIN|5|窗帘|
|JACK|6|插座|
|PIR|7|人体 红外|
|WATER|8|水浸|
|ERG|9|紧急|
|ALARM_BEER|10|警号|
|JCAK_HVAC|11|空调插座|
|MULTI_SWITCH|12|多路开关|
|SHUTTER_MOTOR|13|卷帘 电动机|
|GLASS_BROKEN_SENSOR|20|玻璃破碎 传感器|
|INFRARED_SENSOR|23|红外 对射|
|BATTERY_VALVE|24|电磁阀门|
|AIRFLOW_SENSOR|25|气流传感器|
|MULTI_CTR|32|多功能控制|
|INTEL_LOCK|33|智能锁|
|DOORBELL|34|门铃|
|CO_SENSOR|40|一氧化碳探测器|
|TEMP_HUMI|41|温湿度传感器|
|MOTION|1000|运动检测|
|INNER_DOORBELL|1001|内置 门铃|
|RECORD|1002|录像 不需要注册IOT|
|INNER_PIR|1003|内置人体红外探测器|
|VOICE_ALARM_DETECT|1004|声音报警检测|
|SNAP_SHORT|1005|SnapShot截图 不需要注册IOT|

|**枚举名称**|**枚举值**|**说明**|
|---|---|---|
|PTZ|1006|PTZ不需要用注册IOT|
|INNER_LAMP|1007|内置白光灯|
|INNER_STATE_LAMP|1008|内置状态指示灯|
|BUZZER|1009|内置蜂鸣器|
|CLOUD_RECORD|1010|云端录像|
|CLOUD_SNAP|1011|云端截图|
|CAMERA|1012|定时开关|
|EVENT|1013|事件记录|
|DNSET|1014|图像强制白天黑夜|
|FORCE_REMOVE|1015|强拆|
|STAY|1016|逗留|
|PETS|1029|宠物检测|
|ALARM_LAMP|1030|报警灯|
|PTZ_CRUISE_GARRISON|1032|ptz巡航驻守|
|SIGNLANGUAGE|1034|手势|
|TEMPERATURE|1035|温度|
|HUMIDITY|1036|湿度|
|TOUCHCALL|1037|一键呼叫|
|PTZ_CRUISE_CAPTURE|1033|ptz巡航抓图|
|INFRARED_MODE|1038|功耗模式的灯|
|AIIOT_TYPE_WEBRTC|1063|webrtc功能|
|AIIOT_TYPE_RVSVIDEO|1064|双向视频功能|
|ANTI_BULLYING|1099|防霸凌功能|
|AIIOT_TYPE_ALBUM|1100|时光相册|
|AIIOT_TYPE_VEHICLE_DETECTOR|1083|车辆检测|
|AIIOT_TYPE_DEVICE_STATUS_ALARM|1093|设备状态通知功能|
|AIIOT_TYPE_DOG_MOTOR|1095|4GDog舵机马达|
|AIIOT_TYPE_DOG_RBG_LIGHT|1094|4GDog RGB灯光|
|AIIOT_TYPE_DOG_ONE_SHOW|1050|4GDog一键演示|
|AIIOT_TYPE_INTELLIGENT_ALARM|1098|智能报警|

**AlbumStatusEnum** 

|**枚举名称**|**枚举值**|**说明**|
|---|---|---|
|UN_KNOW|0X00|未知|
|OPEN|0x01|开启|
|CLOSE|0X02|关闭|
|DELAY|0x03|延期,开启过但未过可访问期|

### **PictureTypeEnum** 

|**枚举名称**|**枚举值**|**说明**|
|---|---|---|
|UNKNOWN|-1||
|NORMAL|0x01|码流同等尺寸|
|MIDDLE|0x02|码流缩放一倍尺寸|
|SMALL|0x04|320*240尺寸|
|ICON|0x08|64*48尺寸|

### **SnapTypeEnum** 

|**枚举名称**|**枚举值**|**说明**|
|---|---|---|
|UNKNOWN|-1||
|AUTO|0x01|自动|
|MANUAL|0x02|手动|
|EVENT|0x04|事件|
|FACE|0x08|人脸|

### **AlbumTypeEnum** 

|**枚举名称**|**枚举值**|**说明**|
|---|---|---|
|UN_KNOW|0X00|未知|
|NORMAL|0X01|常规|
|OLD_MAN|0X02|老人|
|KIDS|0X03|儿童|
|PETS|0X04|宠物|

### **SortTypeEnum** 

|**枚举名称**|**枚举值**|**说明**|
|---|---|---|
|FORWARD_ORDER|0|正序|
|REVERSE_ORDER|1|倒序|

### **AlbumUiTypeEnum** 

|**枚举名称**|**枚举值**|**说明**|
|---|---|---|
|UN_KNOW|0X00|没有数据|
|VIDEO|0X01|视频|
|PIC|0X02|图片|
|NO_MORE|0X03|没有更多|

### **EventTypeIDEnum** 

|**枚举名称**|**枚举值**|**说明**|
|---|---|---|
|UNKNOWN|-1||
|ALL|44444444||
|REMOTE_CTRLER|0|遥控器|
|DOOR_MAGNETIC_OPEN_433|101|门磁开门433|
|DOOR_LOW_CURRENT_433|116|门磁低电|
|DOOR_MAGNETIC_CLOSE_433|102|门磁关闭|
|DOOR_MAGNETIC_LOW_RESTORY_433|117|门磁低点恢复|
|SMOKE_ALARM_433|201|烟感报警433|
|LOW_SMOKE_SENSING_POWER_433|216|烟感电量低433|
|SMOKE_LOW_POWER_RECOVERY_433|217|烟感低电恢复433|
|GAS_ALARM_433|301|煤气报警433|
|LOW_GAS_ALARM_SENSING_POWER_433|316|煤气电量低433|
|SMOKE_GAS_ALARM_RECOVERY_433|317|煤气低电恢复433|
|LIGHT_SWITCH|400|电灯|
|CURTAIN|500|窗帘|
|SOCKET_OPEN_433|601|插座开|
|SOCKET_CLOSE_433|602|插座关|
|HUMAN_IR_ALARM_433|701|人体红外触发433|
|HUMAN_IR_LOW_POWER_433|716|人体红外低电433|
|HUMAN_IR_LOW_POWER_RECOVERY_433|717|人体红外低电恢复433|
|WATER_ALARM_433|801|水浸告警433|
|WATER_LOW_POWER_433|816|水浸低电量433|
|WATER_LOW_POWER__RECOVERY_433|817|水浸电量恢复433|
|ERG_ALARM_433|901|紧急报警|
|ERG_LOW_POWER_433|916|紧急低电量433|
|ERG_LOW_POWER_RECOVERY_433|917|紧急电量恢复433|
|DOORBELL_LOW_POWER_433|3403|门铃低电433|
|DOORBELL_LOW_POWER_RECOVERY_433|3405|门铃低电恢复433|
|DOORBELL_RING_433|3408|门铃按钮433|
|CMD_ALARM_433|4001|一氧化碳探测器告警433|

|**枚举名称**|**枚举值**|**说明**|
|---|---|---|
|CMD_LOW_POWER_433|4016|一氧化碳探测器低电量433|
|CMD_LOW_POWER_RECOVERY_433|4017|一氧化碳探测器电量恢复433|
|ALARM_BEER|1000|警号|
|JCAK_HVAC|1100|空调插座|
|MULTI_SWITCH|1200|多路开关|
|SHUTTER_MOTOR|1300|卷帘 电动机|
|GLASS_BROKEN_SENSOR|2000|玻璃破碎 传感器|
|INFRARED_SENSOR|2300|红外 对射|
|BATTERY_VALVE|2400|电磁阀门|
|AIRFLOW_SENSOR|2500|气流传感器|
|MULTI_CTR|3200|多功能控制|
|INTEL_LOCK|3300|智能锁|
|DOORBELL|3400|门铃|
|DOORBELL_IOT|3401|外接设备门铃- 3401 (张晟)|
|CO_SENSOR|4000|一氧化碳探测器|
|TEMP_HUMI|4100|温湿度传感器|
|MOTION|100000|移动侦测|
|HUMAN_DETECT|100001|人形识别|
|FACE|100002|人脸识别|
|FENCE_MOTION_IN|100003|电子围栏移动侦测进入事件|
|FENCE_MOTION_OUT|100004|电子围栏移动侦测离开事件|
|FENCE_HUMAN_IN|100005|电子围栏移动人形进入事件|
|FENCE_HUMAN_OUT|100006|电子围栏移动人形离开事件|
|FENCE_FACE_IN|100007|电子围栏移动人脸进入事件|
|FENCE_FACE_OUT|100008|电子围栏移动人脸离开事件|
|MOTION_EVENT_CAR|100009|车辆检测|
|MOTION_EVENT_FENCE_IN|100010|电子围栏进入事件|
|MOTION_EVENT_FENCE_OUT|100011|电子围栏出去事件|
|FACE_DETECTION|100015|人脸检测事件|
|LICENSE_PLATE_RECOGNITION|100016|车牌识别事件|

|**枚举名称**|**枚举值**|**说明**|
|---|---|---|
|MOVING_OBJECT_CROSSED_THE_LINE|100017|运动物体越线|
|HUMANOID_CROSSING|100018|人形越线|
|FACE_CROSSING|100019|人脸越线|
|ELECTRIC_VEHICLE|100020|电动车识别|
|INNER_DOORBELL|100100|门铃事件|
|LOW_POWER_ALARM|101201|低电报警|
|POWERON|101202|低电恢复|
|INSERT_TF_CARD|101203|插入TF卡|
|PULL_OUT_TF_CARD|101204|拔出TF卡|
|TF_CARD_ANOMALY|101205|TF卡异常|
|SIGNLANGUAGE_OK|103401|ok|
|SIGNLANGUAGE_PALM|103402|手掌|
|SIGNLANGUAGE_UPPER_EIGHT|103403|上八|
|SIGNLANGUAGE_LOWER_EIGHT|103404|下八|
|SIGNLANGUAGE_SHH|103405|嘘|
|SIGNLANGUAGE_FINGER_HEART|103406|比心|
|SIGNLANGUAGE_THUMB_UP|103407|拇指向上|
|SIGNLANGUAGE_THUMB_DOWN|103408|拇指向下|
|TOUCHCALL|103700|一键呼叫事件|
|VIDEO_CALL_ANSWER|103701|双向视频接听|
|VIDEO_CALL_HANG_UP|103702|双向视频挂断|
|FORCE_REMOVE|101500|强拆|
|STAY|101600|逗留|
|ANTI_BULLYING|109900|防霸凌|
|TO_BE_DETERMINED|200000|待定|
|BIRD_DETECTION|200001|鸟类检测|
|BIRD_RECOGNITION|200002|鸟类识别|
|SQUIRREL_DETECTION|200003|松鼠检测|
|STAY_REMINDER|100021|逗留提醒|
|FALL_DETECTION|102400|跌倒检测|

|**枚举名称**|**枚举值**|**说明**|
|---|---|---|
|FLAME_DETECTION|102500|火焰检测|
|CRY_DETECTION|102800|哭声检测|
|PET_IDENTIFICATION|102900|宠物识别|
|CHARACTER_RECOGNITION|200004|人物识别|
|FLOW_STATISTICS|200005|人流统计|
|PARCEL_DETECTION|200006|包裹检测|
|TIMING_CAPTURE_SETTINGS|300000|定时抓拍设置|
|TIMING_REMINDER_SETTING|300001|定时提醒|

|**枚举名称**|**枚举值**|**说明**|
|---|---|---|
|GESTURE_CAPTURE|300002|手势抓拍|
|CLOUD_GESTURE_CALL|300003|手势呼叫套餐里的eventid|
|CLOUD_STORAGE_SERVICE|300004|云存业务|
|INSUFFICIENT_DISK|101206|磁盘不足|
|WEBRTC_ALEXA|300005|alexa语音助手|
|WEBRTC_GOOGLE_HOME|300006|alexa语音助手|
|AI_ALBUM|300007|alexa语音助手|
|TYPE_CHECK_MASK|108400|口罩识别|
|TYPE_HELMET|106800|带安全帽|
|TYPE_NO_HELMET|106801|没带安全帽|
|TYPE_SAFE_VEST|106900|穿反光衣|
|TYPE_NO_SAFE_VEST|106901|没穿反光衣|
|TYPE_LEAVE_JOB|107000|离开岗位|
|TYPE_ON_GUARD|107001|在岗|
|TYPE_PLAY_PHONE|103900|玩手机识别|
|TYPE_ELECTROMOBILE|107100|电瓶车禁止入电梯|
|TYPE_SOMKING|107200|抽烟识别|
|TYPE_SOMKING_PHONE|107300|抽烟打电话识别|
|TYPE_QUICK_TRAVEL|107400|快速移动识别|
|TYPE_PERSONNEL_GATHERING|107500|人员聚集识别|
|TYPE_BRAWL|107600|打架斗殴识别|
|TYPE_PERSON_CROSS_LINE|107700|人员越线识别|
|TYPE_AREA_INVASION|107800|区域入侵识别|
|TYPE_ENTER_AREA|107900|进入区域识别|
|TYPE_OUT_AREA|108000|离开区域识别|
|TYPE_TRASH_FULL|108100|垃圾桶已满|
|TYPE_FIRE_ALARM|102600|火焰报警|
|TYPE_SMOKE_FIRE_ALARM|108200|烟雾和火焰报警|
|TYPE_CEHCK_CAR|108300|车辆检测/车辆识别|
|TYPE_COMPARE_FACE_SUCC|100023|人脸比对成功|

|**枚举名称**|**枚举值**|**说明**|
|---|---|---|
|TYPE_COMPARE_FACE_FAIL|100024|人脸比对失败|
|TYPE_STRANGER_ALARM|100025|陌生人报警|

### **TimeAlbumModeEnum** 

|**枚举名称**|**枚举值**|**说明**|
|---|---|---|
|ALBUM_EPITOME_MODE|"1"|缩影模式|
|ALBUM_CAROUSEL_MODE|"2"|轮播模式|

### **RecordTypeTimeEnum** 

|**枚举名称**|**枚举值**|**说明**|
|---|---|---|
|CLOUD_RECORD_TIME_POLICY|1|云录制时间段|
|LOCAL_RECORD_TIME_POLICY|2|本地录制时间段(卡录像)|
|ALL_RECORD_TIME_POLICY|3|云录像和卡录像都支持的时间段|

### **TimerPolicyTypeEnum** 

|**枚举名称**|**枚举值**|**说明**|
|---|---|---|
|TIME_RECORD_1|1|定时录像1|
|TIME_RECORD_2|2|定时录像2|
|TIME_RECORD_3|3|定时录像3|
|TIME_RECORD_4|4|定时录像4|
|TIME_DNSET_1|10|红外灯时间段控制1|
|TIME_DNSET_2|11|红外灯时间段控制2|
|TIME_WHITE_LAMP_CTRL_1|20|白光灯时间段控制1|
|TIME_WHITE_LAMP_CTRL_2|21|白光灯时间段控制2|
|TIME_WHITE_LAMP_CTRL_3|22|白光灯时间段控制3|
|TIME_WHITE_LAMP_CTRL_4|23|白光灯时间段控制4|
|TIME_INTELLIGENT_CRUISE|100600|智能巡航起始位置,以此类推增长|
|TIME_BROADCAST_PERIOD|100900|播报时间段的起始位置|

### **GroupRightEnum** 

|**枚举名称**|**枚举值**|**说明**|
|---|---|---|
|UNKNOWN|-1||
|ADD_DEVICE|0x01|添加设备|
|REMOVE_DEVICE|0x02|删除设备|
|INVITE_USER|0x04|邀请用户|
|REMOVE_USER|0x08|删除用户|
|ADD_CHILD_GROUP|0x10|添加子组|
|REMOVE_CHILD_GROUP|0x20|删除子组|

### **PushTypeEnum** 

|**枚举名称**|**枚举值**|**说明**|
|---|---|---|
|CLOSE|0|关闭推送|
|PUSH_TXT|0x01|文本推送|
|PUSH_IMAGE|0x02|图片推送|
|PUSH_GIF|0x04|动图推送|
|PUSH_URL|0x05|续费跳转URL推送|
|PUSH_OPEN|0x07|all|

### **FenceDetectAbilityEnum** 

|**枚举名称**|**枚举值**|**说明**|
|---|---|---|
|UNKNOWN|0X00||
|INTO_POLICE|0X01|闯入报警|
|OUT_POLICE|0X02|闯出报警|
|INTO_AND_OUT_POLICE|0X03|闯入和闯出报警|

### **PTZAbilityEnum** 

|**枚举名称**|**枚举值**|**说明**|
|---|---|---|
|UNKNOWN|-1||
|P|1|支持P操作|
|T|2|支持T操作|
|Z|4|支持Z操作|

### **SensitivityEnum** 

|**枚举名称**|**枚举值**|**说明**|
|---|---|---|
|HIGH|75|高|
|MIDDLE|50|中|
|LOW|25|低|

### **WhiteLightModeEnum** 

|**枚举名称**|**枚举值**|**说明**|
|---|---|---|
|LIGHT_INTERVAL_1|100|1小时|
|LIGHT_INTERVAL_3|101|3小时|
|LIGHT_INTERVAL_6|102|6小时|
|LIGHT_INTERVAL_10|103|10小时|
|LIGHT_INTERVAL_AUTO|104|自动模式|
|LIGHT_INTERVAL_IR|105|黑白模式|
|LIGHT_IR_TIME|106|红外灯时间段|
|MULTI_LIGHT_TIME|107|白光灯时间段|
|LIGHT_INTERVAL_FULLCOLOR|108|全彩模式|

### **SoundTypeEnum** 

|**枚举名称**|**枚举值**|**说明**|
|---|---|---|
|DEFAULT_PROMPT_TONE|4|默认配置的提示音|
|CUSTOMIZE_PROMPT_TONE|1|自定义提示音|
|LOCAL_TONE|2|本地提示音,表示从手机本地上传的|
|WORD_TO_LANGUAGE|3|文字转语言|

### **CacheWorkModeEnum** 

|**枚举名称**|**枚举值**|**说明**|
|---|---|---|
|NOT_CACHE_MODE|1|无缓存|
|HAVE_CACHE_MODE|0|有缓存 默认是0|

### **VideoEncTypeEnum** 

|**枚举名称**|**枚举值**|**说明**|
|---|---|---|
|UNKNOWN|-1||
|JPEG|0x01|JPEG图片流|
|H264|0x02|H264流|
|H265|0x04|H265流|

### **ProtectionModeEnum** 

|**枚举名称**|**枚举值**|**说明**|
|---|---|---|
|CLOSE|-1|关闭|
|REMOVAL|0|撤防|
|HOME|1|在家布防|
|AWAY|2|离家布防|

### **ApplyPermissionEnum** 

|**枚举名称**|**枚举值**|**说明**||
|---|---|---|---|
|BE_AUTHORIZED|0|已授权||
|UNAUTHORIZED|-1|未授权,|表示权限已设置,无需弹窗,需要用户在"设置"中修改。|
|ABNORMAL|2|未授权, 权限。|表示请求无效,可能原因有:-未在设置文件中声明目标|

### **ZoomTypeEnum** 

|**枚举名称**|**枚举值**|**说明**|
|---|---|---|
|NON_SUPPORT_ZOOM|0|设备不支持变倍|
|APP_ZOOM|1|双屏变倍|
|DEVICE_ZOOM|2|设备变倍|

### **PlayShowModeEnum** 

|**枚举名称**|**枚举值**|**说明**|
|---|---|---|
|SINGLE_SCREEN_MODE|1|单屏播放样式|
|DUAL_SCREEN_MODE|2|双屏播放样式|
|IMMERSION_MODE|3|沉浸播放样式|

### **PlayTypeEnum** 

|**枚举名称**|**枚举值**|**说明**|
|---|---|---|
|TIME_LINE_MODE_RECORD|1|卡录像点播模式|
|TIME_LINE_MODE_CLOUD|2|云录像点播模式|
|LIVE_VIDEO_MODE|3|实时视频点播模式|
|MULTI_SCREEN_MODE|4|多屏播放模式|

### **PTZDirectionEnum** 

|**枚举名称**|**枚举值**|**说明**|
|---|---|---|
|UNDEFINED||无效|
|LEFT||左|
|RIGHT||右|
|TOP||上|
|BOTTOM||下|
|STOP||停止|

### **NetWorkTypeEnum** 

|**枚举名称**|**枚举值**|**说明**|
|---|---|---|
|UNKNOWN|-1||
|NONET|0|无网络|
|WIRED|1|有线|
|WIFI|2|无线|
|AP|3|AP模式|
|SIM|8|移动网络5G|
|SIM1|9|移动网络2G|
|SIM2|10|移动网络3G|
|SIM3|11|移动网络4G|

### **LanguageEnum** 

|**枚举名称**|**枚举值**|**说明**|
|---|---|---|
|UNKNOWN|0||
|zh_CN|1|中文简体|
|en|2|英语|
|zh_TW|3|中文繁体-台湾|
|zh_HK|3|中文繁体-香港|
|zh_MO|3|中文繁体-澳门|
|fr|4|法语|
|ja|5|日语|
|es|6|西班牙语|
|ko|7|韩语|
|de|8|德语|
|it|9|意大利语|
|ru|10|俄罗斯语|
|pt|11|葡萄牙语|
|vi|12|越南语|
|th|13|泰语|
|tr|14|土耳其语|
|fa|15|波斯语|
|in|16|印尼语|

# **35,接口回调** 

**ITask** 

```
export interface ITask{
  /**
   * 获取任务ID
   */
  getTaskId() : number
  /**
   * 取消请求
   */
  cancelRequest() : void
}
```

### **IBaseCallback** 

```
export interface IBaseCallback{
  /**
   * 请求失败
   * @param errorCode 错误码,详见{ErrorEnum}
   */
  onError : (errorCode : number) => void;
}
```

##### 详见错误码 :ErrorEnum 

### **IResultCallback** 

```
export interface IResultCallback extends IBaseCallback{
/**
*成功回调
*
*/
  onSuccess:() => void
}
```

### **ILoginCallback** 

```
export interface ILoginCallback extends IBaseCallback{
  onSuccess : (firstLoginFlag : number,userInfo : LoginUserInfo |
undefined,bindJson : LoginBindInfo | undefined) => void
}
```

onSuccess : 

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|firstLoginFlag|number|是否第一次登录的标记1第一次登录,0第N次登 录|
|userInfo|LoginUserInfo|
undefined|登录的用户信息|
|bindJson|LoginBindInfo|
undefined|三方登录得用户信息|

### **IResultListener** 

```
export interface IResultListener<T> extends IBaseCallback{
  onResult : (t : T) =>void
}
```

### **ICheckAccountCallback** 

```
export interface ICheckAccountCallback{
  onCheckError:(errorCode : number,accountTypeList?: Array<AccountTypeEnum>)
=>void
  onSuccess:(userId : string)=>void
}
```

onCheckError:(errorCode : number,accountTypeList?: Array) =>void 

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|errorCode|number ErrorEnum|错误码|
|accountTypeList|Array< AccountTypeEnum>|支持的账号类型列表|

### **IGetAccountTypeListCallback** 

```
export interface IGetAccountTypeListCallback extends IBaseCallback{
  getAccountTypeList : (errorCode : number, accountTypeList:
Array<AccountTypeEnum>) => void
}
```

getAccountTypeList : (errorCode : number, accountTypeList: Array) => void 

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|errorCode|number ErrorEnum|错误码|
|accountTypeList|Array< AccountTypeEnum>|支持的账号类型列表|

### **IAddDeviceCallback** 

```
export interface IAddDeviceCallback extends IBaseCallback{
  /**
   * @param deviceId       设备ID
   */
  onSuccess : (deviceId : string) => void
  /**
   * 设备已被当前账号绑定回调
   */
  isBinding : () => void
  /**
   * 设备已被其他账号绑定
   * @param account 绑定设备账号
   */
  isBindOtherOwner : (account : string) => void
}
```

### **IGetBindCodeCallback** 

```
export interface IGetBindCodeCallback extends IBaseCallback{
  /**
   *
   * @param bindCode 绑定码
   * @param ligeTime 有效事件
   */
  onSuccess : (bindCode : string,ligeTime : number) => void
}
```

### **ISearchBluetoothDeviceCallback** 

```
export interface ISearchBluetoothDeviceCallback{
  /**
   *
   * @param resultCode 错误码
   * @param deviceList 搜索到的设备列表
   */
  onSearchResult : (resultCode : ErrorEnum, deviceList :
Array<BluetoothDeviceModel>) => void
}
```

BluetoothDeviceModel 

**AddDeviceCallback** 

```
export interface AddDeviceCallback{
  /**
   * 设备添加成功
   * @param deviceId      设备ID
   */
   onActiveSuccess:(deviceId: string) =>void
   onError:(errorMsg: string) =>void
  /**
   * 设备已经在本账号下
   * @param deviceId      设备ID
   * @param ownerId       用户ID
   */
   onAddedBySelf:(deviceId: string, ownerId: string) =>void
  /**
   * 设备被其他账号添加
   * @param deviceId      设备ID
   * @param userId       用户ID
   */
   onAddedByOther:(deviceId: string, account : string) =>void
  /**
   * 添加进度
   * @param progress     添加设备的进度
   */
   onAddedProgress:(progress : number) =>void
}
```

### **LanSearchObserver** 

```
export interface LanSearchObserver{
  onLanSearchResult : (model : LanSearchDeviceModel) => void;
}
```

##### LanSearchDeviceModel 

### **ICreateQRCodeCallback** 

```
export interface ICreateQRCodeCallback extends IAddDeviceCallback{
  /**
   * @param qrCode 返回的二维码图片
   */
  onCreateQRCodeSuccess: (qrCode : image.PixelMap) => void
}
```

**IAPDirectActivatorCallback** 

```
export interface IAPDirectActivatorCallback extends IBaseCallback {
  /**
   *
   * @param deviceId 连接成功后返回设备ID
   */
  onDirectSuccess : (deviceId : string) => void
}
```

### **IDeviceListChangeCallback** 

```
export interface IDeviceListChangeCallback {
  /**
   *
   * @param deviceList 设备列表
   */
  onDeviceListChange :(deviceList : Array<Device>) =>void
}
```

onDeviceListChange :(deviceList : Array) =>void 

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|deviceList|Array< Device>|设备列表|

### **IGetWiFiListCallback** 

```
export interface IGetWiFiListCallback extends IBaseCallback{
  /**
   *
   * @param wifiList 设备wifi列表
   */
  onSuccess : (wifiList : Array<WiFiBean>) => void
}
```

##### WiFiBean 

### **IUploadFileCallback** 

```
export interface IUploadFileCallback extends IBaseCallback{
  /**
   *
   * @param fileId 成功回调返回文件ID
   */
  onSuccess : (fileId : string) => void
}
```

### **IGetTimeZoneCallback** 

```
export interface IGetTimeZoneCallback extends IBaseCallback{
  /**
   * @param autoSync      自动同步标志
   * @param time          时间,格式:yyyy-MM-dd HH:mm:ss
   * @param timeZone      时区,0点偏移量,单位:秒
   * @param dstArea       夏令时地区
   * @param dstZone       夏令时时区
   */
  onSuccess : (autoSync : boolean,time : string,timeZone : number,dstArea :
string,dstZone : string) => void
}
```

### **IGetTFCardInfoCallback** 

```
export interface IGetTFCardInfoCallback extends IBaseCallback{
  /**
   *
   * @param storageAbility    存储卡支持能力
   * @param totalSize         总容量
   * @param remainSize        剩余容量
   */
  onSuccess : (storageAbility : number , totalSize : number , remainSize :
number) => void
}
```

### **ICurNetWorkCallback** 

```
export interface ICurNetWorkCallback extends IBaseCallback{
  onSuccess : (netWorkInfo : NetworkBean) => void
}
```

onSuccess : (netWorkInfo : NetworkBean) => void 

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|netWorkInfo|NetworkBean|网络信息|

**IPTZStatusCallback** 

```
export interface IPTZStatusCallback extends IBaseCallback{
  /**
   *
   * @param ptzStatus 0 ptz停止没有转动,1 ptz正在转动
   */
  onSuccess : (ptzStatus : number) => void
}
```

### **IResultListener** 

```
export interface IResultListener<T> extends IBaseCallback{
  onResult : (t : T) =>void
}
```

### **IGetSoundListCallback** 

```
export interface IGetSoundListCallback extends IBaseCallback{
  /**
   * @param totalSpace    总空间
   * @param freeSpace     剩余空间
   * @param soundList     声音列表
   */
  onGetSoundList : (totalSpace : number,freeSpace : number,soundList :
Array<RingFileBn>) => void
}
```

onGetSoundList : (totalSpace : number,freeSpace : number,soundList : Array) => void 

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|totalSpace|number|总空间|
|freeSpace|number|剩余空间|
|soundList|Array< RingFileBn>|声音列表|

### **IGetSMSPackageCallback** 

```
export interface IGetSMSPackageCallback extends IBaseCallback{
  /**
   * @param total       总数目
   * @param remain  剩余数目
   */
  onSuccess : (total : number,remain : number) => void
}
```

**I4GChargePackageCallback** 

```
export interface I4GChargePackageCallback extends IBaseCallback{
  onGet4GChargePackage : (chargePackageBean : I4GChargePackageBean) => void
}
```

onGet4GChargePackage : (chargePackageBean : I4GChargePackageBean) => void 

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|chargePackageBean|I4GChargePackageBean|4G套餐信息|

### **ILiveImageCallback** 

```
export interface ILiveImageCallback extends IBaseCallback{
  /**
   *
   * @param data 返回的图片
   */
  onSuccess : (data : image.PixelMap) =>void
}
```

### **IImageListCallback** 

```
export interface IImageListCallback extends IBaseCallback{
  onSuccess : (imageList : Array<ImageBean>) => void
}
```

onSuccess : (imageList : Array) => void 

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|imageList|Array< ImageBean>|图片列表信息|

### **IImageLocalCallback** 

```
export interface IImageLocalCallback extends IBaseCallback{
  /**
   * @param filename  图片路径,文件后缀为.jpg
   */
  onSuccess:(filePath : string) => void
}
```

### **IImageCalendarCallback** 

```
export interface IImageCalendarCallback extends IBaseCallback{
  /**
   *
   * @param calendarList 日历列表
   */
  onSuccess : (calendarList : Array<string>) => void
}
```

### **IRecordCalendarCallback** 

### **IGetAlbumVideoListCallback** 

```
export interface IGetAlbumVideoListCallback extends IBaseCallback {
  getAlbumVideoList : (list: Array<AIAlbumVideoBean>) =>void
}
```

getAlbumVideoList : (list: Array) =>void 

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|list|Array< AIAlbumVideoBean>|时光相册视频列表|

### **IGetAlbumPicListCallback** 

```
export interface IGetAlbumPicListCallback extends IBaseCallback {
  getAlbumPicList : (list: Array<AIAlbumPicBean>) =>void
}
```

getAlbumPicList : (list: Array) =>void 

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|list|Array< AIAlbumPicBean>|时光相册图片列表|

### **INVRSearchSubDevCallback** 

```
export interface INVRSearchSubDevCallback extends IBaseCallback{
  onSuccess(list : Array<NvrSubDevInfoBean>) : void
}
```

onSuccess(list : Array) : void 

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|list|Array< NvrSubDevInfoBean>|Nvr子设备列表|

**INVRBindSubDevCallback** 

```
export interface INVRBindSubDevCallback extends IBaseCallback{
  onSuccess(list : Array<NvrChannelPairBean>) : void
}
```

onSuccess(list : Array) : void 

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|list|Array< NvrChannelPairBean>|nvr通道列表|

### **ICreateGroupCallback** 

```
export interface ICreateGroupCallback extends IBaseCallback{
  /**
   * @param groupId  组ID
   * @param gToken   组Token
   */
  onSuccess : (groupId : string,gToken : string) => void
}
```

### **IEventCalendarCallback** 

```
export interface IEventCalendarCallback extends IBaseCallback{
  /**
   * @param calendarInfoList  日历列表
   */
  onSuccess : (calendarInfoList : Array<string>) => void
}
```

### **IRecordListCallback** 

```
export interface IRecordListCallback extends IBaseCallback{
  onSuccess : (recordList : Array<RecordBean>) => void
}
```

onSuccess : (recordList : Array<RecordBean>) => void 

### **IModifyfenceResult** 

```
export interface IModifyfenceResult extends IBaseCallback{
  /**
   *
   * @param faceId 区域ID
   */
  onSuccess(faceId : number) : void
}
```

**ICheckVersionCallback** 

```
export interface ICheckVersionCallback extends IBaseCallback{
  onSuccess : (updateMode : UpdateModeEnum,version : string,descUrl : string) =>
void
}
onSuccess : (updateMode : UpdateModeEnum,version : string,descUrl : string) =>
void
```

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|updateMode|UpdateModeEnum|更新模式|
|version|string|新版本号|
|descUrl|string|描述http接口|

### **IAIIoTStatusCallback** 

```
export interface IAIIoTStatusCallback extends IBaseCallback{
  /**
   *
   * @param ioTStatusList  iot设备状态列表
   */
  onGetIoTStatus : (ioTStatusList : Array<IoTStatusBean>) => void
}
```

onGetIoTStatus : (ioTStatusList : Array<IoTStatusBean>) => void 

### **ISoundListCallback** 

```
export interface ISoundListCallback extends IBaseCallback{
  /**
   * @param totalSpace    总空间
   * @param freeSpace     剩余空间
   * @param soundList     声音列表
   */
  onGetSoundList : (totalSpace : number,freeSpace : number,soundList :
Array<CustomAudioBean>) => void
}
```

onGetSoundList : (totalSpace : number,freeSpace : number,soundList : Array<CustomAudioBean>) => void 

### **IRefreshVcardCallback** 

```
export interface IRefreshVcardCallback extends IBaseCallback{
  onGetUserVcardInfo : (userVCardBean : UserVCardBean) => void
}
```

onGetUserVcardInfo : (userVCardBean : UserVCardBean) => void 

**IGetUserIdCallback** 

```
export interface IGetUserIdCallback extends IBaseCallback{
  /**
   *
   * @param userId 用户ID
   */
  onSuccess : (userId : string) => void
}
```

### **ICacheSizeCallback** 

```
export interface ICacheSizeCallback extends IBaseCallback{
  /**
   * @param cacheSize  缓存大小,单位KB
   */
  onGetDiskCacheSize : (cacheSize : number) =>void
}
```

### **IChangeQRCallback** 

```
export interface IChangeQRCallback extends IBaseCallback{
  /**
   *
   * @param qrCode 二维码图片
   * @param qrCodeImgPath 二维码图片存储路径
   */
  onSuccess : (qrCode : image.PixelMap,qrCodeImgPath : string) => void
}
```

### **IWeChatQRCodeCallback** 

```
export interface IWeChatQRCodeCallback extends IBaseCallback{
  /**
   * @param qrCodeUrl         二维码图片url
   * @param ticket            二维码唯一标识符
   * @param expireSeconds     二维码到期时间,从生成时间开始算,单位秒
   */
  onSuccess : (qrCodeUrl : string,ticket : string,expireSeconds : number) =>
void
}
```

### **IWeChatCurStatusCallback** 

```
export interface IWeChatCurStatusCallback extends IBaseCallback{
  /**
   * @param WeChatOpenId      绑定微信公众号的微信号开放ID
   * @param status            绑定状态
   * @param content           微信号公开信息(昵称、头像等)
   */
  onSuccess : (weChatOpenId : string,status : WeChatPushStatusEnum , content :
string) => void
}
```

### **IGetResourceCallback** 

```
export interface IGetResourceCallback extends IBaseCallback{
  onSuccess(list : Array<ResourceBean>) : void
}
```

onSuccess(list : Array<ResourceBean>) : void 

### **IGetAccountTypeListCallback** 

```
export interface IGetAccountTypeListCallback extends IBaseCallback{
  /**
   *
   * @param errorCode 错误码
   * @param accountTypeList  账号类型列表
   */
  getAccountTypeList : (errorCode : number, accountTypeList:
Array<AccountTypeEnum>) => void
}
```

getAccountTypeList : (errorCode : number, accountTypeList: Array<AccountTypeEnum>) => void 

### **IScanCodeCallback** 

```
export interface IScanCodeCallback{
  /**
   * 扫码登录回调
   * @param qrLoginUrl 登录的WebURL
   */
  onScanCodeSignIn:(qrLoginUrl : string)=>void
  /**
   * 分享设备回调
   * @param shareUrl 分享URl
   */
  onSharedDevice : (shareUrl : string) => void
  /**
   * 添加外置IOT回调
   * @param iotType iot设备类型
   * @param iotId    iot设备id
   */
  onAddHubIot:(iotType : number,iotId : number) => void
  /**
   * 属主转移回调
   * @param transferUrl 属主转移URL
   */
  onOwnerTransfer : (transferUrl : string) => void
  /**
   * 无法识别结果
   */
  onUnidentifiable : () => void
  /**
   * 添加设备方式
   *
   * @param deviceType  设备类型,比如:摄像机,nvr,网关等设备
   * @param addDeviceMode  添加设备的方式,如: ap添加,二维码添加,蓝牙添加等。。。
   * @param deviceNetType  设备的可配网络类型,如: 4G网络,双频WIFI(包含2.4G和5G的
wifi)等。。
   * @param wifiName  wifi名称
   */
  onAddDeviceMode : (deviceType : DeviceTypeEnum,addDeviceMode :
ConfigNetworkModeEnum,deviceNetType : ConfigNetTypeEnum,wifiName : string | null)
=> void
  /**
   * 添加设备方式
   *
   * @param deviceType  设备类型,比如:摄像机,nvr,网关等设备
   * @param addDeviceMode  添加设备的方式,如: ap添加,二维码添加,蓝牙添加等。。。
   * @param deviceNetType  设备的可配网络类型,如: 4G网络,双频WIFI(包含2.4G和5G的
wifi)等。。
   * @param wifiName  wifi名称
   */
  onLicenseAddDeviceMode : (deviceType : DeviceTypeEnum,addDeviceMode :
ConfigNetworkModeEnum,license : string ) => void
  /**
   * 用deviceId添加设备
   * @param deviceid  设备ID
   * @param deviceType  设备类型
   */
  onAddDeviceByDID : (deviceid : string,deviceType : DeviceTypeEnum) => void
}
```

### **IGetPaasAccessTokenCallback** 

```
export interface IGetPaasAccessTokenCallback extends IBaseCallback{
  onTokenReturn : (accessToken : string,expireSeconds : number,passAddress :
string) => void
}
```

onTokenReturn : (accessToken : string,expireSeconds : number,passAddress : string) => void 

|**参数名**|**参数类型**|**说明**|
|---|---|---|
|accessToken|string|passToken|
|expireSeconds|number|到期的秒|
|passAddress|string|pass地址|

### **IRequestPermissionCallback** 

```
export interface IRequestPermissionCallback{
  onPermissionStatus : (state : ApplyPermissionEnum) =>void
}
```

onPermissionStatus : (state : ApplyPermissionEnum) =>void 

### **IBluetoothLinkStateCallback** 

```
export interface IBluetoothLinkStateCallback{
  /**
   *
   * @param state 系统的蓝牙状态信息实例
   */
  onState : (state : access.BluetoothState) => void
}
```

### **IStartRequestCallback** 

```
export interface IStartRequestCallback {
  startRequest : () =>void
}
```

### **IRequestPermissionCallback** 

```
export interface IRequestPermissionCallback{
  onPermissionStatus : (state : ApplyPermissionEnum) =>void
}
```

onPermissionStatus : (state : ApplyPermissionEnum) =>void 

### **IWifiStatusCallback** 

```
export interface IWifiStatusCallback{
  /**
   *
   * @param isConnect 是否连接
   */
  onStatus : (isConnect : boolean) =>void
}
```

**EventNoticeObserver** 

```
export interface EventNoticeObserver{
  /**
   * @param deviceId      设备ID
   * @param count         新事件数目
   * @param day           日期,格式:yyyy-MM-dd
   */
  onNewEventNotify : (deviceId : string,count : number,day : string) => void
}
```

### **AlarmEventObserver** 

```
export interface AlarmEventObserver{
  onNewEventNotify : (bean : MessageBean) => void
}
```

onNewEventNotify : (bean : MessageBean) => void 

### **SystemNoticeObserver** 

```
export interface SystemNoticeObserver{
  /**
   * @param systemNotice 通知消息
   */
  onSystemNotice : (systemNotice : SystemNoticeBean) => void
}
```

onSystemNotice : (systemNotice : SystemNoticeBean) => void 

### **AdNoticeObserver** 

```
export interface AdNoticeObserver{
  /**
   * @param adNoticeList 广告通知列表
   */
  onAdNotice(adNoticeList : Array<AdNoticeBean>) : void
}
```

onAdNotice(adNoticeList : Array<AdNoticeBean>) : void 

### **IAppGradeNoticeObserver** 

```
export interface IAppGradeNoticeObserver extends IBaseCallback{
  /**
   *
   * @param type 通知类型
   * @param noticeJson  通知内容
   */
  onAppGradeNotice : (type : number,noticeJson : string) => void
}
```

**IRecordMP4Listener** 

```
export interface IRecordMP4Listener{
  /**
   *
   * @param requestId 请求ID
   * @param filePath 文件路径,后缀为.mp4
   */
  onRecordResult : (requestId : number ,filePath : string ) => void
}
```

### **TimeLineCallback** 

export interface TimeLineCallback { /** * 选择的事件下载视频 * @param selectList 选择消息事件列表 */ onDownloadByEvent: (selectList: Array<MessageBean>) => void /** * 下载选择的一段视频, * @param startTime 开始时间 * @param endTime  结束时间 */ onDownloadByVideo : (startTime : string,endTime : string) => void /** * 跳转购买云服务 * @param deviceId 设备ID */ onPurchaseCloud : (deviceId : string) => void } 

# **36,数据信息** 

### **LoginUserInfo** 

|**字段名称**|**数据类型**|**说明**|
|---|---|---|
|RegistFlag|string|0:非注册1:注册|

### **LoginBindInfo** 

|**字段名称**|**数据类型**|**说明**|
|---|---|---|
|AccountType|number|需要绑定的类型 AccountTypeEnum|
|Suggestlevel|number|1:建议; 2:强制|

### **BluetoothDeviceModel** 

|**字段名称**|**数据类型**|**说明**|
|---|---|---|
|bluetoothDeviceName|string|蓝牙设备名称|
|macAddress|string|mac地址|
|uuid|string|uuid,唯一Id|
|lisence|string|设备烧录lisence|
|isLongTong|boolean|厂商的设备|

### **LanSearchDeviceModel** 

|**字段名称**|**数据类型**|**说明**|
|---|---|---|
|license|string|设备的license|
|deviceId|string|设备ID|
|deviceIp|string|设备IP|
|osType|OSTypeEnum|系统类型|
|deviceType|DeviceTypeEnum|设备类型|

### **QRCodeParamModel** 

|**字段名称**|**数据类型**|**说明**|
|---|---|---|
|isOnlySetWifi|boolean|是否只设置wifi,不添加设备|
|is4GDevice|boolean|是否是4G设备|
|isScanSupport4G|boolean|是否是扫码跳转支持的4G|
|wifiName|string|要配网wifi名称|
|password|string|要配网wifi的密码|
|imgHeight|number|要生成二维码图片的高度|
|imgWidth|number|要生成二维码图片的宽度|
|qrCodeTimeoutSeconds|number|二维码生成超时时间,单位秒|

**Device** 

|**字段名称**|**数据类型**|**说明**|
|---|---|---|
|groupId|string|组ID|
|deviceId|string|设备ID|
|isOwner|boolean|是否属主(设备是否是自己的)不是分享的|
|ownerId|string|属主ID|
|deviceType|DeviceTypeEnum|设备类型|
|groupName|string|组名称|
|joinTime|string|添加时间|
|deviceName|string|设备名称|
|sharedAccount|string|分享的账号|
|deviceStatus|DeviceStatusEnum|设备状态|
|lastOfflineTime|string|最后离线的时间|
|deviceImage|image.PixelMap | undefined|设备封面图片|

### **WiFiBean** 

|**字段名称**|**数据类型**|**说明**|
|---|---|---|
|signalStrength|number|信号强度|
|connectFlag|number|是否连接|
|wifiSSID|string|WiFi名称|
|security|number|是否有密码|

DeviceTypeEnum 

### **DeviceBean** 

|**字段名称**|**数据类型**|**说明**|
|---|---|---|
|encryptAbility|number|是否加密|
|otaAbility|number|是否支持ota升级|
|setWiFiAbility|number|是否支持设置wifi|
|awakeAbility|number AwakeAbilityEnum|唤醒能力|
|hasBattery|boolean|是否有电池|
|powerSupply|boolean|是否正在充电-是否插了电源|
|support4G|boolean|是否支持4G,是否支持插物联网卡|
|supportLogCollect|boolean|是否支持日志收集|
|powerLevel|number|电池电量|
|otaStatus|number|升级状态|
|language|number|语言|
|osType|number OSTypeEnum|系统类型|
|sdkVersion|number|sdk版本|
|groupId|string|组ID|
|deviceId|string|设备ID|
|deviceName|string|设备名称|
|deviceVersion|string|设备版本|
|companyId|string|企业ID|
|appId|string|appID|
|devIMEI|string|IMEI号|
|simSlotCnt|number|sim卡数量|
|workSimSlotId|number|正在使用的sim卡id|
|license|string|设备的license|
|simCard|string|物联网卡号|
|dstArea|string|时区地理区域|
|dst|string|时区的详情信息|
|deviceType|number DeviceTypeEnum|设备类型|
|deviceModel|string|设备型号|
|wifiSSid|string|wifi名称|

|**字段名称**|**数据类型**|**说明**|
|---|---|---|
|macAddr|string|wifi mac地址|
|curLedStatus|number|当前指示灯状态|
|timeMode|number|0:24小时显示模式,1 12小时显示模 式|
|autoUpgrade|boolean|自动升级,0关闭,1开启|
|autoUpgradeWeek|number|自动升级 一.0x01,二.0x02,三.0x04, 四.|
|autoUpgradeTime|number|启动升级时间, 当天的秒数|
|autoSyncGmFlag|number|是否开启时间自动同步|
|mulMediaInf|MulMediaBean|流媒体参数配置|
|simList|List< SimBean>|sim卡列表|
|supplyShowPowerAbility|number|表示显示电量的能力,当处于充电状态 的时候|
|dualFrequency|number|双频配网能力0-不是双频配网1-双频 配网|
|apPassWdAbility|number|ap热点设置密码能力|
|promptSetFlag|number|提示用户设置密码开关|
|apHasPassWd|number|表示有没有设置过密码|
|oneClickshowAbility|number|表示有没有设置过密码|
|aliveSessionCnt|number|当前观看人数|
|aucDevThirSn|string|第三方平台的sn号|

### **MulMediaBean** 

|**字段名称**|**数据类型**|**说明**|
|---|---|---|
|port|number|端口|
|enctype|number|加密方式|
|accessToken|string|第三方平台校验Token|
|resourceId|string|登录授权码|
|mediaIp|string|ip地址|
|encLv|string|加密向量|
|encKey|string|加密秘钥|

### **SimBean** 

|**字段名称**|**数据类型**|**说明**|
|---|---|---|
|simSlotId|number|卡槽号|
|iMsi|string|IMSI号|
|iCcid|string|4G卡号|

### **PresetInfo** 

|**字段名称**|**数据类型**|**说明**|
|---|---|---|
|supportPreset|boolean|是否支持预置位|
|watchPresetId|number|看守位ID|
|watchTime|number|看守位回归时间(5-360s)|
|threeDPositionAblity|number|3D定位支持能力|
|cruiseAbility|number|是否支持巡航功能,app根据此能力显示巡航 功能|
|presetList|Array< PresetBean>|预置位列表|
|cruiseList|Array< CruiseBean>|巡航列表|

### **PresetBean** 

|**字段名称**|**数据类型**|**说明**|
|---|---|---|
|presetId|number|预置位ID|
|name|string|预置位名称|
|picId|string|预置位图片ID|
|presetPoint|PresetPointBean|预置位的坐标位置|

### **PresetPointBean** 

|**字段名称**|**数据类型**|**说明**|
|---|---|---|
|x|number|预置位截图时的x轴|
|y|number|预置位截图时的y轴|
|z|number|预置位截图时的z轴|

### **CruiseBean** 

|**字段名称**|**数据类型**|**说明**|
|---|---|---|
|openFlag|boolean|巡航开关|
|cruiseId|number|巡航ID|
|name|string|名称|
|cruiseType|number|是否双向巡航1是,0否|
|speed|number|巡航速度|
|autohome|number|自动返回起点|
|delayTime|number|延迟时间|
|pointList|Array< CruisePointBean>|预置位点的列表|
|actionList|Array< OutputBean>|到达一个预置位执行事件任务|
|cruiseTime|Array< TimePolicyBean>|巡航时间段|

### **CruisePointBean** 

|**字段名称**|**数据类型**|**说明**|
|---|---|---|
|presetId|number|预置位ID|
|dwellTime|number|停留时长|
|speed|number|转速|

### **OutputBean** 

|**字段名称**|**数据类型说明**|
|---|---|
|IoTType|number AIIoTTypeEnum 功能类型|
|IoTId|number 功能ID|
|param|string 这个是json字符串,可以动态配置,解析也需要自己解 析|
|**字段名称TimePoli**|**数据类型说明cyBean**|
|openFlag|boolean 时间段策略开关|
|policyId|number ( DefaultPolicyIDEnum) 策略ID从100600起始|
|policyName|string 策略名|
|weekFlag|number 周几,为掩码代表一周中的一天或多天。0x01, 为周一;0x02周二0x04周三 以倍速类推|
|startTime|number 开始时间 单位:秒 当天的0点到这个时间的秒|
|endTime|number 结束时间 单位:秒 当天的0点到这个时间的秒|
|day|string 哪天|
|loopType|number 0:循环定时任务1:一次性定时任务|
|outputList|Array< OutputBean> 时间段执行的功能策略|

### **AIInfoBean** 

|**字段名称**|**数据类型**|**说明**|
|---|---|---|
|supportAIFace|boolean|AI人脸识别能力|
|supportHumanCount|boolean|客流统计能力|
|aIPicMaxNum|number|AI底库 支持的最大数目|
|curPicNum|number|当前人脸库的数目|
|humanCountOpenFlag|number|客流统计开关|
|humanCountInterval|number|客流统计间隔|
|timerbuzzer|number|蜂鸣器总开关1,开0,关|
|stayTime|number|逗留时间|
|autoInputFaceFlag|boolean|自动录入开关|
|deployFaceLabelList|Array< DeployFaceLabelBean>|人脸标签列表|

### **DeployFaceLabelBean** 

|**字段名称**|**数据类型**|**说明**|
|---|---|---|
|aiGroupId|string|人脸标签组ID|
|faceLabelID|string|人脸文件ID|
|faceLabelName|string|人脸标签名字|
|deploySampleList|Array< DeployFaceSampleBean>|布控的人脸样本列表|
|deployDesc|string|人脸标签备注信息|
|capacity|number|人脸容量|

### **DeployFaceSampleBean 布控的人脸样本** 

|**字段名称**|**数据类型**|**说明**|
|---|---|---|
|faceId|string|人脸ID|

### **EnergyInfoBean** 

|**字段名称**|**数据类型**|**说明**|
|---|---|---|
|energyModeAbility|number|是否支持切换功耗模式能力|
|curModelId|number|1正常工作模式2节能模式3低功耗模式|
|workType|number|0自动1手动|
|modelList|Array< EnergyModelBean>|功耗信息|

### **EnergyModelBean** 

|**字段名称**|**数据类型**|**说明**|
|---|---|---|
|modelId|number|需要修改的工作模式ID|
|upLevel|number|上升电量|
|downLevel|number|下降电量|
|actionList|Array|功耗模式对应可执行的功能|

### **NetworkBean** 

|**字段名称**|**数据类型**|**说明**|
|---|---|---|
|netType|number NetWorkTypeEnum|网络类型0无网, 1有线, 2 Wifi, 4 AP, 5 SIM 卡|
|signalType|number|信号类型:2:2G;3:3G;4:4G|
|signalStrength|number|信号强度,0到100,数值越大表示信号越好|
|ipAddress|string|IP地址|
|macAddress|string|Mac地址|
|wifiSSID|string|WiFi热点名称|
|simCard|string|4G卡号,当NETTYPE是4G时|
|netMask|string|网络掩码|
|gateWay|string|网关|

### **VideoParamBean** 

|**字段名称**|**数据类型**|**说明**|
|---|---|---|
|resolution|number|分辨率,见分辨率定义|
|videoWidth|number|视频宽度|
|videoHeight|number|视频高度|
|encodeType|number|编码类型|
|smartEncode|boolean|Smart编码标记|
|quality|number|编码质量,VBR编码方式时|
|bitRate|number|码率,见码率定义; CBR编码方式|
|frameRate|number|帧率|
|frameInterval|number|I帧间隔|
|rateType|number|编码方式:1=CBR固定码率, 2=VBR固 定质量|

### **VideoCircleBean** 

|**字段名称**|**数据类型**|**说明**||
|---|---|---|---|
|radius|number|半径||
|angle|number|角度||
|c1x|number|圆心坐标X,|若为720度,标识第一个圆|
|c1y|number|圆心坐标Y,|若为720度,标识第一个圆|
|c2x|number|圆心坐标X,|若为720度,标识第二个圆|
|c2y|number|圆心坐标Y,|若为720度,标识第二个圆|

### **VideoDistortionBean** 

|**字段名称**|**数据类型**|**说明**|
|---|---|---|
|fx|number|镜头光轴与图像圆心的水平偏移|
|fy|number|镜头光轴与图像圆心的垂直偏移|
|fa|number|桶形畸变矫正参数|
|fb|number|枕形畸变矫正参数|
|scale|number|图像缩放因子|

**AudioParamBean** 

|**字段名称**|**数据类型**|**说明**|
|---|---|---|
|encType|number|编码模式|
|sampleRate|number|采样率|
|channel|number|声道数|
|depth|number|深度|

### **RecordProp** 

|**字段名称**|**数据类型**|**说明**|
|---|---|---|
|Status|string|本地录像当前状态,0.未录制;1.录制中|
|RecordLoop|string|本地是否循环录像|
|RecordFull|string|本地全天录像标志,1.全天录像;0.按策略进行录像;当设置策略时, 由设置者来修改此项取值;|
|StreamID|string|录制码流选择。0.主码流;1.次码流|
|Duration|string|录制时长(开启事件录制时带有该参数)|

### **RingFileBn** 

|**字段名称**|**数据类型**|**说明**|
|---|---|---|
|fileSize|number|文件大小|
|fileFormat|number|文件格式|
|ringType|number|铃声类型|
|fileContent|string|文件内容|
|fileName|string|文件名称|
|soundfiletype|number|声音文件类型|
|soundFileId|string|提示音文件ID|
|soundDownUrl|string|提示音下载URL|
|showName|string|UI显示的名称|

### **EnergyModelBean** 

|**字段名称**|**数据类型**|**说明**|
|---|---|---|
|modelId|number( EnergyModeEnum)|功耗模式ID|
|upLevel|number|上升电量|
|downLevel|number|下降电量|
|actionList|Array< OutputBean>|功能事件列表|

### **AlgorithmInfoBean** 

|**字段名称**|**数据类型**|**说明**|
|---|---|---|
|eventIdList|Array< EventInfBean>|关联事件列表|
|serviceList|Array< AlgorithmServiceBean>|算法服务列表|

### **EventInfBean** 

|**字段名称**|**数据类型**|**说明**|
|---|---|---|
|eventId|number|事件名称|
|aiiotType|number AIIoTTypeEnum|IotType事件的类型|
|openFlag|number|事件开关|
|name|string|事件名称|

### **AlgorithmServiceBean** 

|**字段名称**|**数据类型**|**说明**|
|---|---|---|
|openFlag|boolean|服务开关|
|serviceId|number|服务ID|

### **AppSettingModel** 

|**字段名称**|**数据类型**|**说明**|
|---|---|---|
|jpgReSampleFlag|number|截图是否重采样|
|resampleHeight|number|重采样的高|
|resamplewidth|number|重采样的宽|
|lampFlag|number|首页设备是否显示灯光控制的图标|
|lightMaxTime|number|单位s|
|lightLevelMode|number|1默认模式, 10分, 20分。。1小时, 2小时|
|clickAlarmFlag|number|页面是否展示 一键报警功能1:展示0不展示|
|priorStreamID|number|设备的默认码流Id|
|splitScreenOpenFlag|number|是否开启虚拟分屏效果|
|splitScreenCamID|number|虚拟分屏的摄像机ID|
|shownPrecent|number|虚拟屏显示源视频的百分比|
|encoderID|number|0:默认编码器;1:XM编码器|
|jvideoReSampleFlag|number|视频是否重采样|

#### **获取屏幕分屏数据** 

```
getScreenSplit() : ScreenSplitBean
```

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|ScreenSplitBean|屏幕分屏数据|

### **ScreenSplitBean** 

|**字段名称**|**数据类型**|**说明**|
|---|---|---|
|openFlag|number|分屏开关|
|splitCamID|number|分屏的摄像头ID|
|shownPrecent|number|显示百分比|

#### **获取百分比** 

```
getHalfPercent() : number
```

返回: 

**参数类型 说明** number 显示的百分比 

#### **是否打开** 

```
isOpen() : boolean
```

返回: 

|**参数类型**|**说明**|
|---|---|
|boolean|是否打开状态|

#### **是否为四目抢球设备** 

```
isFourEyes(deviceId : string) : boolean
```

|**参数名称**|**参数类型**|**说明**|
|---|---|---|
|deviceId|string|设备ID|

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|boolean|是否打开状态|

### **DeviceAlarmParam** 

|**字段名称**|**数据类型**|**说明**|
|---|---|---|
|Duration|string|持续时间|
|FileName|string|文件名称|
|LampFlag|string|报警灯开关0关1开|
|Volume|string|报警音量0-100|

#### **状态灯是否打开** 

```
isLampFlag() : boolean
```

返回: 

**参数类型** 

**说明** 

boolean 

状态灯是否打开 

#### **设置状态灯开关** 

```
setLampFlag(lampFlag : boolean)
```

|**参数名称**|**参数类型**|**说明**|
|---|---|---|
|lampFlag|boolean|状态灯开关|

#### **设置报警声音音量** 

```
setVolume(volume : number)
```

|**参数名称**|**参数类型**|**说明**|
|---|---|---|
|volume|number|报警声音音量0-100|

#### **获取报警音量** 

```
getVolume() : number
```

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|number|报警声音音量0-100|

### **CameraBean** 

|**字段名称**|**数据类型**|**说明**|
|---|---|---|
|streamCount|number|流数量,比如高清 超清|
|voicePlayAbility|number|语音对接能力|
|supportMicrophone|boolean|是否支持麦克风|
|supportSetOSD|boolean|是否支持自定义水印|
|supportIRLed|boolean|是否支持红外灯|
|inversionAbility|number|图像翻转能力|
|mirrorAbility|boolean|图像水平翻转能力|
|curMirrorType|number|图像水平翻转类型|
|supportTFCard|boolean|是否支持tf卡|
|ringToneSetAbility|number|铃声设置能力|
|audioDecAbility|number|音频解码能力|
|supportWDR|boolean|是否支持宽动态WDR|
|supportHDR|boolean|是否支持高动态HDR|
|hdrOpenFlag|boolean|高动态开关|
|supportOSD|boolean|是否支持水印,不支持时需要app侧自 己显示|
|fullColorMode|number|0:没有获取过能力, 需要根据企业id 区分两种模式1:定时全彩,2:夜晚全彩|
|cameraOpenFlag|boolean|设备的配置|
|micOpenFlag|boolean|麦克风开关|
|hasTFCard|boolean|当前tf是否插入|
|wdrOpenFlag|boolean|WDR开关|
|curInversionType|number|当前上下翻转|
|curIRWorkMode|number|白光红外的 工作 模式|
|iRCutMode|number|红外灯模式0x01完全自动0x02支持手 动+自 动 切换0x03仅支持手动切换|
|curScanFrequency|number|当前扫描频率|
|curVolume|number|当前音量|
|audioParam|AudioParamBean|音频参数|
|streamerList|Array< StreamBean>|码流参数链表|
|curLensId|number|当前镜头id|

|**字段名称**|**数据类型**|**说明**|
|---|---|---|
|lensMaxCount|number|最大镜头数量|
|humanRegionAbility|number|人形区域定位|
|lensList|Array< LensBean>|镜头信息链表|
|playMode|number|镜头信息链表|
|zoomType|number|变焦类型0:APP变倍,1:设备变倍|
|maxZoom|number|最大放大倍数|
|curZoom|number|当前放大倍数|
|zoomAbility|ZoomAbilityModeEnum|0x01一直放大模式 (不支持精准); 0X02指定放大倍数模式(支持精准) ,0x03都支持|
|rectifyAbility|number|鱼眼矫正能力0不支持app端矫正;1 支持 设备端矫正|
|camid|number|摄像头id|
|support3dAbility|ThreeDGestureTypeEnum|3D定位方式|
|supportptz|number|ptz操作能力|
|timerOsdSwitch|boolean|时间和LOG显示|
|osdPosition|boolean|自定义水印位置 水印位置1.左上;2.左 下;3.右上;4.右下;0.默认|
|customOsdSwitch|boolean|自定义水印 开关|
|osdName|string|自定义水印名称|
|antiFlickerAbility|number|抗闪烁能力0:不支持; 1:支持|
|privacyMaskAbility|number|隐私部位能力|
|privacyList|Array< PrivacyAreaBean>|隐私区域列表|

#### **是否支持PTZ** 

```
isSupportPtz() : boolean
```

##### 返回: 

|**参数类型**|**说明**|
|---|---|
|boolean|是否支持PTZ转动|

**是否支持变焦** 

```
isZoomLens(lensBean : LensBean)
```

|**参数名称**|**参数类型**|**说明**|
|---|---|---|
|lensBean|LensBean|镜头信息|

#### **是否JPEG流编码** 

```
isJpegEncType()
```

#### **获取变倍的镜头ID** 

```
getZoomLendsId() : number
```

返回: 

|**参数类型**|**说明**|
|---|---|
|number|变倍的镜头I|

### **StreamBean** 

|**字段名称**|**数据类型**|**说明**|
|---|---|---|
|streamId|number|流ID|
|hideFlag|number|隐藏标记|
|resolutionAbility|number|分辨率能力|
|capAbility|number||
|videoParam|VideoParamBean|视频信息|
|videoCircle|VideoCircleBean|当为鱼眼镜头,且参数为圆心半径矫正时|
|videoDistortion|VideoDistortionBean|当为鱼眼镜头,为扭曲度时|

### **LensBean** 

|**字段名称**|**数据类型**|**说明**|
|---|---|---|
|lensId|number|镜头ID|
|lensType|number( CamLensTypeEnum)|镜头类型|
|lensName|number|镜头名称|
|focalLength|number|焦距|
|maxfocalLength|number|最大焦距|
|minfocalLength|number|最小焦距|

### **PrivacyAreaBean** 

|**字段名称**|**数据类型**|**说明**|
|---|---|---|
|useFlag|number|开关|
|regionId|number|区域ID|
|pointList|Array< FencePointBean>|区域点列表|

### **FencePointBean** 

|**字段名称**|**数据类型**|**说明**|
|---|---|---|
|pointX|number|区域X轴描点|
|pointY|number|区域Y轴描点|

### **GroupUserBean** 

|**字段名称**|**数据类型**|**说明**|
|---|---|---|
|userId|string|用户ID|
|roleId|string|组角色ID|
|joinTime|string|添加时间|
|roleBean|GroupRoleBean|组角色信息|

### **GroupRoleBean** 

|**字段名称**|**数据类型**|**说明**|
|---|---|---|
|roleId|string|组角色ID|
|groupRight|number|组权限; 0x01.添加设备; 0x02.删除设备; 0x04.添 加分享用户; 0x08. 删除分享用户; 0x10.添加子组; 0x20.删除子组;以掩码形式 代表多个 权限|
|deviceRight|number|{ "DeviceType": "0x00.所有设备控制, 0x01.分开设备控制", "Rights": [ //如果是TYPE 0x00: // JSON描述符: }, "Devices"Devices": [ //如果 是TYPE 0x01 { "DID": "设备ID", "Rights": { // JSON描述符: } } ] }|

### **ChargePackageInfo** 

|**字段名称**|**数据类型**|**说明**|
|---|---|---|
|autoPayFlag|number|是否自动付费|
|dayExpireFlag|number|-1已过期,0未开通,1即将过期,2使用中,3 待生效|
|eventExpireFlag|number|-1已过期,0未开通,1即将过期,2使用中,3 待生效|
|chargePackageList|Array< ChargePackageData>|云服务套餐数据|

### **ChargePackageData** 

|**字段名称**|**数据类型**|**说明**|
|---|---|---|
|status|number ( CargePackageStatusEnum)|套餐状态,1-未使用;2-正在使 用;3-暂停使用;4-已过期5取消|
|duration|number|套餐使用时长|
|packageId|number|套餐ID|
|poId|number|套餐期限|
|payMode|number|付费方式|
|autoPayFlag|number|是否自动付费|
|buyTime|string|购买时间|
|activeTime|string|激活时间,若未激活,此时间为空|
|expireTime|string|过期时间,若未激活,此时间为空|
|orderId|string|订单ID|
|packageName|string|套餐名称|
|history|string|套餐历史记录,什么时间购买,什 么时间给什么设备激活,什么时间 暂停,什 么时间又激活等等|
|deviceList|Array|设备ID列表套餐类型|
|pckType|number|套餐类型|
|packageBuyUID|string|购买套餐的UID|
|packageBuyAccout|string|购买套餐的账号|
|defaultOpenFlag|number|默认打开状态|
|eventIdList|Array< EventIdBean>|关联事件列表|
|moduleServiceBeanList|Array< ModuleServiceBean>|关联的智能服务事件列表|

### **EventIdBean** 

|**字段名称**|**数据类型**|**说明**|
|---|---|---|
|eventId|number( EventTypeIDEnum)|事件id|

### **ModuleServiceBean** 

|**字段名称**|**数据类型**|**说明**|
|---|---|---|
|serviceId|number|服务ID|
|aiIotType|number( AIIoTTypeEnum)|iot类型|

**I4GChargePackageBean** 

|**字段名称**|**数据类型**|**说明**|
|---|---|---|
|status|number( ChargeStatusEnum)|套餐状态|
|total|number|总流量|
|remain|number|剩余流量|
|pendFlag|number|是否有新套餐0:没有,1:有|
|expireTime|string|套餐到期时间|
|platCard|boolean|是否平台卡|
|firstBuy|boolean|是否首次购买|

### **EventServiceTypeBean** 

|**字段名称**|**数据类型**|**说明**|
|---|---|---|
|eventId|number|事件ID|
|isOpen|boolean|是否打开|
|buyTime|string|支付时间|

### **InnerDACOption** 

|**字段名称**|**数据类型**|**说明**|
|---|---|---|
|dacType|number|内置iot类型|
|optType|number|内置Iot类型|
|loopType|number|循环类型|
|optionScheduleList|Array< OptionSchedule>||

### **OptionSchedule** 

|**字段名称**|**数据类型**|**说明**|
|---|---|---|
|day|string|日期|
|scheduleInfo|ScheduleInfo|时间段|

### **ScheduleInfo** 

|**字段名称**|**数据类型**|**说明**|
|---|---|---|
|enable|boolean|时间段开关|
|weekFlag|number|周几|
|startSecond|number|开始时间|
|endSecond|number|结束时间|

### **ImageBean** 

|**字段名称**|**数据类型**|**说明**|
|---|---|---|
|picType|number( PictureTypeEnum)|图片 大小类型|
|imageTime|string|图片事件|
|imageName|string|图片名称|
|imageDesc|string|图片描述|

### **AlbumTabInfo** 

|**字段名称**|**数据类型**|**说明**|
|---|---|---|
|albumInfo|AlbumInfo|时光相册类型信息|
|packageInfo|ChargePackageData|套餐服务数据|

### **AlbumInfo** 

|**字段名称**|**数据类型**|**说明**|
|---|---|---|
|AlbumType|string( AlbumTypeEnum)|相册类型|
|OpenFlag|string|时光相册开关|

### **PayInfoBean** 

|**字段名称**|**数据类型**|**说明**|
|---|---|---|
|currency_symbol|string|货币符号|
|default|number||
|deviceBuyCount|number||
|freepkg|number||
|google_key|string||
|ios_key|string||
|name|string|云服务名称|
|number|number||
|packageid|string||
|order_type_id|number||
|pay|Array||
|poid|string||
|price|string||
|relpkg|Relpkg||
|showRelName|string||
|showServiceCycle|number||
|showType|number||
|show_price|string||
|subscription|number||
|tag|TagX||
|unit|string||
|updatetime|string||
|userBuyCount|number||
|serviceCycleName|string||
|imageUrl|string||
|campOderNumber|string||
|countdownTime|string||
|canTrialBuy|number||

### **Relpkg** 

|**字段名称**|**数据类型**|**说明**|
|---|---|---|
|currency_symbol|string||
|default|number||
|deviceBuyCount|number||
|freepkg|number||
|google_key|string||
|infolist|Array< Infolist>||
|ios_key|string||
|name|string|服务名称|
|number|number||
|packageid|number||
|pay|Array|支付方式|
|poid|string||
|price|string||
|showRelName|string||
|showServiceCycle|number||
|show_price|string||
|subscription|number||
|tag|TagX||
|unit|string||
|userBuyCount|number||

### **TagX** 

|**字段名称**|**数据类型**|**说明**|
|---|---|---|
|leftSubscript|string||
|type1|string||
|type2|string||
|type3|string||

**Infolist** 

|**字段名称**|**数据类型**|**说明**|
|---|---|---|
|icourl|string||
|maintitle|string||
|subtitle|string||

### **AiAlbumServiceInfo** 

|**字段名称**|**数据类型**|**说明**|
|---|---|---|
|pId|string|套餐ID|
|pType|number( AlbumTypeEnum)|相册类型,比如看老人,看小孩相册|
|title|string|名称|
|descContent|string|描述内容|
|packageInfo|ChargePackageData|套餐数据|
|payInfoBean|PayInfoBean|支付信息|
|albumInfo|AlbumInfo|相册信息|
|isSelected|boolean|是否选择|

### **AIAlbumVideoBean** 

|**字段名称**|**数据类型**|**说明**|
|---|---|---|
|date|string|日期|
|videoFileId|string|视频文件ID|
|videoDownloadUrl|string|视频下载地址|
|videoPicUrl|string|视频图片URL|
|picList|Array< AIAlbumPicBean>|相册图片列表|
|videoDuration|number|视频时间|
|picTotalCount|number|图片最大数量|

### **AIAlbumPicBean** 

|**字段名称**|**数据类型**|**说明**|
|---|---|---|
|fileId|string|相册图片文件ID|
|startTime|string|开始时间|
|picDownloadUrl|string|图片下载URL|
|uiType|number( AlbumUiTypeEnum)|文件类型|
|videoDownloadUrl|string|视频下载地址|

### **AlarmTimeBean** 

|**字段名称**|**数据类型**|**说明**|
|---|---|---|
|startTime|number|开始时间,0点到当前时间的秒,|
|endTime|number|结束时间,0点到当前时间的秒,|
|isCrossDay|boolean|是否跨天|
|time|string|时间段字符串yyyy-MM-dd HH-mm-ss|
|weekArray|Array|周几的数组,1周一,2周二,3周三以此类推|

### **TimePolicyParam** 

|**字段名称**|**数据类型**|**说明**|
|---|---|---|
|policyId|number ( TimerPolicyTypeEnum)|时间段策略ID|
|policyName|string|时间段策略名称|
|startTime|number|开始时间,0到当前时间的秒|
|endTime|number|结束时间,0到当前时间的秒|
|weekFlag|number|星期一:0x01星期二:0x02星期三:0x04星期 四:0x08星期五:0x010星期六:0x020星期 日:0x040全部:0x7F|
|picInterval|number|抓图间隔|

### **NvrSubDevInfoBean** 

|**字段名称**|**数据类型**|**说明**|
|---|---|---|
|channelID|number|通道ID|
|subDevState|number|设备状态|
|subDevAccessProto|number|子设备接入NVR协议|
|subDevName|string|设备名|
|subDevIP|string|设备IP|
|subDevID|string|设备ID|
|firmwareVersion|string|设备固件版本号|
|offlineTime|string|设备固件版本号|
|isSelect|string||
|needAuth|number|0.不需要认证1.需要用户名密码|

### **NvrChannelPairBean** 

|**字段名称**|**数据类型**|**说明**|
|---|---|---|
|channelId|number|通道ID|
|deviceId|string|子设备DID|
|result|number|子操作返回结果,0表示成功,非0表示失败|
|userName|string|用户名|
|passwd|string|密码|

### **NvrStorageBean** 

|**字段名称**|**数据类型**|**说明**|
|---|---|---|
|mode|number|存储模式0满磁存储1轮询存储|
|storageNodes|Array< NvrStorageNodeBean>|存储节点信息|

### **NvrStorageNodeBean** 

|**字段名称**|**数据类型**|**说明**|
|---|---|---|
|path|string|存储路径|
|selected|number|选择的存储空间|
|maxSize|number|最大存储空间 单位:MB|
|usedSize|number|已用存储空间 单位:MB|

**NvrChannelConfigBean** 

|**字段名称**|**数据类型**|**说明**|
|---|---|---|
|maxChannels|number|NVR支持的最大通道数|
|channelInfos|Array< NvrChannelInfoBean>|通道信息列表,包含通道绑定的设备信息|

### **NvrChannelInfoBean** 

|**字段名称**|**数据类型**|**说明**|
|---|---|---|
|channelID|number|通道ID|
|deviceID|string|子设备DID|
|isBind|number|操作返回结果,0表示未被绑定,1表示已被绑定|

### **GroupBean** 

|**字段名称**|**数据类型**|**说明**|
|---|---|---|
|userNum|number|用户数目,包含下级组|
|sonGrpNum|number|子组数量|
|deviceNum|number|设备数目,包含下级组|
|roleNum|number|角色数目|
|groupName|string|组织名称|
|groupId|string|组ID|
|groupToken|string|组Token|
|ownerId|string|根据ownerid可以判定组是不是分享的|
|groupDesc|string|组描述|
|userList|Array< GroupUserBean>|组中的用户列表|
|deviceList|Array< GroupDeviceBean>|组中的设备列表|
|childGroupList|Array< ChildGroupBean>|组的子组信息|
|roleList|Array< GroupRoleBean>|组的角色信息列表|

### **GroupUserBean** 

|**字段名称**|**数据类型**|**说明**|
|---|---|---|
|userId|string|用户ID|
|roleId|string|角色ID|
|joinTime|string|设备入组时间|
|roleBean|GroupRoleBean|角色信息|

### **GroupDeviceBean** 

|**字段名称**|**数据类型**|**说明**|
|---|---|---|
|deviceId|string|设备ID|
|cacheDevState|number|缓存的设备状态|
|joinTime|string|设备入组时间|
|license|string|设备授权码|
|lastOfflineTime|string|设备离线时间|

### **ChildGroupBean** 

|**字段名称**|**数据类型**|**说明**|
|---|---|---|
|deviceNum|number|设备数目|
|groupName|string|组名称|
|groupId|string|组ID|
|parentGroupId|string|父组ID|
|groupToken|string|组Token|
|ownerId|string|属主ID,|
|groupDesc|string|组描述|
|deviceList|Array< GroupDeviceBean>|设备列表|

### **MessageBean** 

|**字段名称**|**数据类型**|**说明**|
|---|---|---|
|eventType|EventTypeIDEnum|事件类型|
|eventId|number|事件ID|
|ioTType|number|告警类型|
|ioTId|number|设备ID|
|createTime|string|事件创建时间|
|endTime|string|事件结束时间|
|cloudEid|string|云事件ID|
|localEid|string|卡事件ID|
|deviceId|string|设备ID|
|picFileID|string|事件图片ID|
|customType|number|自定义类型|
|pushFlag|number( PushTypeEnum)|推送类型|
|duration|number|持续时间|
|showFlag|number|显示标记|
|faceInfoList|Array< FaceInfo>|人脸信息列表|
|customMsg|string|自定义消息|
|deviceName|string|设备名称|
|relateEventTime|string|关联的其他event时间|
|relateEventID|string|关联的其他eventId|
|isSelect|boolean|UI选择flag|

### **FaceInfo** 

|**字段名称**|**数据类型**|**说明**|
|---|---|---|
|faceFileID|string|人脸文件ID|
|pointX|number|x轴位置|
|pointY|number|y轴位置|
|width|number|人脸图片宽度|
|height|number|人脸图片高度|
|faceLabelId|string|人脸的标签ID|
|labelName|string|人脸标签名字|
|aIGroupId|string|人脸标签组ID|
|picIndex|number|图片角标|
|correctFlag|number|正确的标志|
|identifyList|Array< AiIdentifyBean>|图片识别结果|

### **AiIdentifyBean** 

|**字段名称**|**数据类型**|**说明**|
|---|---|---|
|confidence|number|相似度|
|nameList|Array< AiNameBean>|图片识别结果信息列表|

### **AiNameBean** 

|**字段名称**|**数据类型**|**说明**|
|---|---|---|
|aiName|string|识别图片的结果名称|
|languageId|number|语言ID ZJUtil.getCurLanguage()|

### **EventDetailsBean** 

|**字段名称**|**数据类型**|**说明**|
|---|---|---|
|eventImage|PixelMap | null|事件图片|
|recognitionResult|Array< RecognitionImageResult>|图片识别结果列表|

### **RecognitionImageResult** 

|**字段名称**|**数据类型**|**说明**|
|---|---|---|
|imageIcon|PixelMap | undefined|图片图标|
|info|FaceInfo | undefined|图片信息|

**RecordBean** 

|**字段名称**|**数据类型**|**说明**|
|---|---|---|
|startTime|string|开始时间|
|duration|number|持续时间|
|endTime|string|结束时间|

### **AlarmPolicyBean** 

|**字段名称**|**数据类型**|**说明**|
|---|---|---|
|openFlag|boolean|策略是否使用|
|iotType|number AIIoTTypeEnum|"IoT类型|
|iotId|number|设备ID|
|policyId|number DefaultPolicyIDEnum|策略ID|
|policyName|string|策略名|
|prop|string|根据AIIoT类型定义中的prop值|
|policyEventList|Array< PolicyEventBean>|策略事件列表|

### **PolicyEventBean** 

|**字段名称**|**数据类型**|**说明**|
|---|---|---|
|eventId|number ( EventTypeIDEnum)|事件ID|
|weekFlag|number|星期一:0x01星期二:0x02星期三:0x04星期 四:0x08星期五:0x010星期六:0x020星期 日:0x040全部:0x7F|
|startTime|number|开始时间,0到当前时间的秒,比如 凌晨一点,那么 开始时间就是3600秒|
|endTime|number|结束时间,0到当前的秒|
|spanFlag|boolean|是否跨天|
|openFlag|number|开关|
|fenceList|Array< FenceInfoBean>|报警区域信息列表|
|sceneList|Array< SceneIDBean>|布防场景ID|
|triggerList|Array< TriggerInfoBean>|触发源列表|
|outputList|Array< OutputBean>|iot触发类型列表|

**FenceInfoBean** 

|**字段名称**|**数据类型**|**说明**|
|---|---|---|
|regionId|number|区域ID|
|direction|number|持续时间|
|pointList|Array<[FencePointBean])(#FencePointBean)>|区域围栏点列表|

### **FencePointBean** 

|**字段名称**|**数据类型**|**说明**|
|---|---|---|
|pointX|number|x轴位置|
|pointY|number|y轴位置|

### **SceneIDBean** 

|**字段名称**|**数据类型**|**说明**|
|---|---|---|
|sceneId|number|布防场景ID|

### **TriggerInfoBean** 

|**字段名称**|**数据类型**|**说明**|
|---|---|---|
|openFlag|number|是否启用0不用,1启用,默认设1|
|triggerType|number|触发源类型|
|eventId|number|触发源事件id|

### **HubIoTInfo** 

|**字段名称**|**数据类型**|**说明**|
|---|---|---|
|supportHub|boolean|是否支持外置IOT|
|hubConnect|boolean|外置IOT状态|
|maxCount|number|最大数量|
|ioTList|Array< HubIoTBean>|外置IOT列表|

### **HubIoTBean** 

|**字段名称**|**数据类型**|**说明**|
|---|---|---|
|iotType|number AIIoTTypeEnum|设备类型|
|iotId|number|设备ID|
|iotName|string|设备名称|
|enableFlag|boolean|是否可用|
|openFlag|boolean|开关|
|powerLevel|number|电量|
|joinTime|number|添加时间|
|prop|string|联动策略|

### **IoTStatusBean** 

|**字段名称**|**数据类型**|**说明**|
|---|---|---|
|ioTType|number|iot设备类型|
|ioTId|number|iot设备ID|
|status|number|iot设备状态|

### **InnerIoTInfo** 

|**字段名称**|**数据类型**|**说明**|
|---|---|---|
|ptzAbility|number( PTZAbilityEnum)|PTZ能力|
|supportAttachPtz|boolean|外挂PTZ能力,枪机外接云台模式|
|supportSetPtzSpeed|boolean|"PTZ速度设置能力|
|supportMotion|boolean|运动检测支持能力|
|supportDoorBell|boolean|内置门铃按键支持能力|
|supportPIR|boolean|人体红外报警支持能力|
|supportVoiceAlarm|boolean|声音检测支持能力|
|supportSnapJpg|boolean|报警抓图支持能力|
|supportBuzzer|boolean|蜂鸣器支持能力|
|supportStatusLamp|boolean|指示灯控制支持能力|
|supportWhiteLamp|boolean|白光灯控制支持能力|
|supportRecord|boolean|录像能力支持|
|supportCloudRecord|boolean|云录制支持能力|
|supportCloudSnap|boolean|云抓图支持能力|
|supportCtrlCamera|boolean|支持摄像机采集打开关闭控制能力|
|supportEvent|boolean|事件记录能力|
|supportCloud|boolean|是否支持云服务|
|IoTList|Array< InnerIoTBean>|内置IOT列表,也就是功能列表|
|supportAlarmLamp|boolean|报警灯支持能力|

#### **是否支持报警灯** 

```
isSupportAlarmLamp(): boolean
```

#### **获取内置IOT信息** 

getInnerIotBean(typeEnum : AIIoTTypeEnum ) : InnerIoTBean | undefined 

**获取录像策略 录像的流ID,0:超清,1:高清** 

getRecordProp() : RecordProp 

**InnerIoTBean** 

|**字段名称**|**数据类型**|**说明**|
|---|---|---|
|IoTType|number|内置IOT类型|
|IoTId|number|内置IOTID|
|openFlag|boolean|是否打开状态|
|prop|string|联动策略|
|buss|string|设置的内置iot的提示音策略|
|algorithmNodeList|Array< AlgorithmNodeBean>|算法功能链表|

### **AlgorithmNodeBean** 

|**字段名称**|**数据类型**|**说明**|
|---|---|---|
|algorithmId|number|算法id|
|workType|number|算法作用位置1云;2本地3云端和本地结合|
|baseAlgorithmId|number|关联基本算法id|

### **RecordProp** 

|**字段名称**|**数据类型**|**说明**|
|---|---|---|
|Status|string|本地录像当前状态,0.未录制;1.录制中|
|RecordLoop|string|本地是否循环录像|
|RecordFull|string|本地全天录像标志,1.全天录像;0.按策略进行录像;当设置策略时, 由设置者来修改此项取值|
|StreamID|string|录制码流选择。0.主码流;1.次码流|
|Duration|string|录制时长(开启事件录制时带有该参数)|

#### **获取持续时长** 

```
getDuration() : number
```

#### **设置持续时长 设置给对象** 

```
setDuration(duration : number)
```

**AlarmTimeBean** 

|**字段名称**|**数据类型**|**说明**|
|---|---|---|
|startTime|number|开始时间,0点到当前时间的秒,如果是凌晨0点就是0|
|endTime|number|结束时间,单位秒凌晨0点到当前时间的秒|
|isCrossDay|boolean|是否跨天|
|time|string|格式化时间01:22-02:23|
|weekArray|Array|周几,周一:1,周二:2,周三:3以此类推|

### **EventOutputParam** 

|**字段名称**|**数据类型**|**说明**|
|---|---|---|
|PushFlag|string|是否推送(如果Prop中的PushFlag关闭,则无效)|
|SMSFlag|string|是否发送短信|
|EmailFlag|string|是否发送邮件|
|Interval|string|推送间隔,单位分钟|
|StartTime|string|开始时间,单位秒|
|EndTime|string|结束时间,单位秒|
|Week|string|周几推送,掩码|
|SpanFlag|string|是否跨天|

### **AlarmNoticeInfo** 

|**字段名称**|**数据类型**|**说明**|
|---|---|---|
|pushRemindSwitch|boolean|推送提醒开关|
|smsNoticeSwitch|boolean|短息推送提醒开关|
|pushTimeInterval|number|推送时间间隔|
|pushTime|NoticeTimeBean|推送时间段|

### **NoticeTimeBean** 

|**字段名称**|**数据类型**|**说明**|
|---|---|---|
|startTime|string|开始时间|
|endTime|string|结束时间|
|weekFlag|string|星期一:0x01星期二:0x02星期三:0x04星期四:0x08星期 五:0x010星期六:0x020星期日:0x040全部:0x7F|
|spanFlag|boolean|是否跨天|

### **CustomAudioBean** 

|**参数名称**|**参数类型**|**描述**|
|---|---|---|
|fileName|string|文件名称|
|filePath|string|文件路径|
|fileSize|number|文件大小|
|uuid|string|本地文件唯一标识|
|account|string|当前登录的账号|
|isSelect|boolean|当前设备的提示音|
|type|SoundTypeEnum|自定义提示音类型|
|name|string|提示音名称|

### **UserVCardBean** 

|**参数名称**|**参数类型**|**描述**|
|---|---|---|
|married|number|是否已婚|
|sex|number|普通用户性别,1为男性,2为女性|
|mobile|string|手机号|
|birthday|string|生日日期|
|country|string|国家|
|provice|string|省份|
|email|string|邮箱|
|address|string|地址|
|city|string|城市|
|vMid|string||
|nickName|string|昵称|
|photoProfile|string|头像|

### **UserBean** 

|**参数名称**|**参数类型**|**描述**|
|---|---|---|
|userId|string|用户ID|
|mobile|string|手机号|
|email|string|邮箱|
|thirdType|number|三方登录类型|
|thirdId|string|三方登录ID|
|thirdToken|string|三方登录Token|

### **ResourceBean** 

|**参数名称**|**参数类型**|**描述**|
|---|---|---|
|eventid|number|事件ID|
|resourceFormat|number|资源格式1 mp4 4 jpg 9 gif|
|resourceUrl|string|资源文件URL|

**UseModel** 

|**参数名称**|**参数类型**|**描述**|
|---|---|---|
|uuid|string|唯一ID|
|icon|string|图标|
|name|string|名称|
|isSelect|boolean|是否选择|
|isCustom|boolean|是否自定义|
|package_id|string|套餐ID|
|code|string|用途码|

### **LocalMediaBean** 

|**参数名称**|**参数类型**|**描述**|
|---|---|---|
|fileName|string|文件名称|
|fileTime|string|文件时间 (只有视频文件才使用这个字段)|
|fileSize|number|文件大小(只有视频文件才使用这个字段)|
|filePath|string|文件路径|
|duration|string|(只有视频文件才使用这个字段)|
|videoEncType|VideoEncTypeEnum|文件编码类型(只有视频文件才使用这个字段)|
|width|number|文件的宽|
|height|number|文件的高|

### **ProtectionModeParam** 

|**参数名称**|**参数类型**|**描述**|
|---|---|---|
|openFlag|number|布防开关状态:1:开0:关|
|home|HomeBean|在家布防设置信息|
|away|AwayBean|离家布防设置信息|
|removal|RemovalBean|撤防设置信息|

### **HomeBean** 

|**参数名称**|**参数类型**|**描述**|
|---|---|---|
|motion|MotionBean|运动侦测设置信息|
|human|HumanBean|人形侦测设置信息|
|face|FaceBean|人脸侦测设置信息|
|pushFlag|number PushTypeEnum|推送类型|
|buzzerFlag|number|蜂鸣器开关0关,1开|
|hubList|Array< HubBean>|外置iot列表|

### **MotionBean** 

|**参数名称**|**参数类型**|**描述**|
|---|---|---|
|status|number|0关,1开|

### **HumanBean** 

|**参数名称**|**参数类型**|**描述**|
|---|---|---|
|status|number|0关,1开|

### **FaceBean** 

|**参数名称**||**参数类型描述**|
|---|---|---|
|status||number 0关,1开|
|**参数名称**|**参数类型**|**描述**|
|status|number|iot设备开关状态,0:关,1:开|
|type|number|iot设备类型|
|id|number|iot设备ID|
|name|string|iot设备名称|

### **AwayBean** 

|**参数名称**|**参数类型**|**描述**|
|---|---|---|
|motion|MotionBean|运动侦测设置信息|
|human|HumanBean|人形侦测设置信息|
|face|FaceBean|人脸侦测设置信息|
|pushFlag|number PushTypeEnum|推送类型|
|buzzerFlag|number|蜂鸣器开关0关,1开|
|hubList|Array< HubBean>|外置iot列表|

### **RemovalBean** 

|**参数名称**|**参数类型**|**描述**|
|---|---|---|
|motion|MotionBean|运动侦测设置信息|
|human|HumanBean|人形侦测设置信息|
|face|FaceBean|人脸侦测设置信息|
|pushFlag|number PushTypeEnum|推送类型|
|buzzerFlag|number|蜂鸣器开关0关,1开|
|hubList|Array< HubBean>|外置iot列表|

### **PresetModel** 

|**参数名称**|**参数类型**|**描述**|
|---|---|---|
|fileID|string|图片ID|
|deviceID|string|设备ID|
|name|string|预置位名称|
|presetID|number|预置位ID|
|focalLength|string|双目摄像机焦距|
|isSyncCloud|number|图片是否同步到云端|
|isSyncDeviceFileIDFlag|number|上传图片到云端同步fileID到设备端成功和失败的标记|
|isDeleteCloudImagFlag|number|删除云端图片成功或失败的标记1是不需要删除,0是需要 删除的图片|
|isWatched|boolean|是否为看守位true:是看守位false:不是看守位|
|watchPointPollTime|number|看守位循环时间 单位为秒|

### **SetPresetModel** 

|**参数名称**|**参数类型**|**描述**|
|---|---|---|
|presetName|string|预置位的名称|
|filePath|string|预置位的图片|
|pointZ|number|预置位的Z轴,也就是缩放的倍率|
|isWatched|boolean|是否为看守位1:是看守位0:不是看守位|
|watchedPollTime|number|看守位循环时间 单位为秒|

### **CruiseBean** 

|**参数名称**|**参数类型**|**描述**|
|---|---|---|
|openFlag|boolean|巡航开关|
|cruiseId|number|巡航ID|
|name|string|名称|
|cruiseType|number|是否双向巡航1是,0否|
|speed|number|巡航速度|
|autohome|number|自动返回起点|
|delayTime|number|延迟时间|
|pointList|Array< CruisePointBean>|预置位点的列表|
|actionList|Array< OutputBean>|执行事件任务|
|cruiseTime|Array< TimePolicyBean>|巡航时间段|

### **CruisePointBean** 

|**参数名称**|**参数类型**|**描述**|
|---|---|---|
|presetId|number|预置位ID|
|dwellTime|number|停留时间|
|speed|number|速度|

### **PairInfo** 

|**参数名称**|**参数类型**|**描述**|
|---|---|---|
|ringId|number|关联信息ID|
|deviceId|string|设备id|
|pairDeviceId|string|关联的设备|
|userId|string|用户ID|

### **NoticeSettingBean** 

|**参数名称**|**参数类型**|**描述**|
|---|---|---|
|strongReminderSwitch|boolean|强提醒开关|
|voiceSwitch|boolean|提示声音开关|
|vibrationSwitch|boolean|提示震动开关|
|bannersRemindRadio|boolean|banner样式的强提醒|
|fullScreenRemindRadio|boolean|全屏样式的强提醒|
|deviceId|string|设备ID|

### **WifiInfo** 

|**参数名称**|**参数类型**|**描述**|
|---|---|---|
|ssid|string|wifi名称|
|whetherEncrypt|boolean|是否加密|
|is5G|boolean|是否5Gwifi|
|signalStrength|number|信号强度|

### **SystemNoticeBean** 

|**参数名称**|**参数类型**|**描述**|
|---|---|---|
|noticeType|number|1:应用升级通知;2:设备升级通知;3:系统公告通知4:广告发 布通知5:扣款通知|
|flag|number|0不需要升级;1推荐升级; 2强制升级|
|remind|number|是否重复提醒升级|
|version|string|版本号|
|subject|string|title|
|brief|string|简介|
|url|string|默认升级地址|
|did|string|设备升级的时候的 设备did|
|startTime|string|系统 通知的显示 时间|
|duration|number|系统通知显示时长|

### **AdNoticeBean** 

|**参数名称**|**参数类型**|**描述**|
|---|---|---|
|brief|string|简介|
|url|string|web页面地址|
|title|string|title|
