Trusfort 

# 芯盾时代智能人机识别 SDK 集成文档 

V2.0.7 

北京芯盾时代科技有限公司 2024 年 6 月 

版本号 修订人 修订日期 修订描述 V1.4.6 高英明 2024 年 03 月 04 日 首次建立 v2.0.0 高英明 

2024 年 03 月 29 日 

更换托底 SDK 

V2.0.3 

高英明 

2026 年 01 月 07 日 

去除多余信息采集,修复 bug 

V2.0.4 

高英明 

2026 年 01 月 07 日 去除不使用的 ohos.permission.STORE_PERSISTENT_DATA 权限 V2.0.5 

高英明 

2026 年 03 月 03 日 

增加配置初始化后是否自动开始采集传感器信息 

V2.0.6 

高英明 

2026 年 03 月 18 日 去除初始化后开始自动采集 

V2.0.7 

高英明 

2026 年 03 月 24 日 

去除设置自动开始采集接口 

目录 

1. 集成向导 4 

2. SDK 集成 4 

2.1. SDK 内容 4 

2.2. 集成方法 4 

2.3. 其它依赖库 4 

2.4. 支持系统版本 4 

2.5. 隐私权限 5 

3. Harmony 集成流程解读 5 

3.1. Harmony 端支持验证码类型 5 

3.2. 验证码调用流程图 5 

4. SDK 接口详情 6 

4.1. SDK 整体接口列表 6 

4.1.1. SDK 主体接口列表 6 

4.1.2. options 设置接口参数列表 8 

4.1.3. 验证码结果回调接口 9 

5. 接口错误码 10 

# 集成向导 

验证码客户端集成的前提, serverurl 和 appid 都需要服务端提供,找 项目负责人申请。 

# SDK 集成 

SDK 内容 

xd_capthca_lib_2.0.7.har : har 格式的 lib 包 

集成方法 

将 xd_capthca_lib_2.0.7.har ,复制到工程根目录下。 在代码工程目录下的 oh-package.son5 中添加如下配置 dependencies{ 

xd_captcha:"file:./xd_capthca_lib_2.0.7.har" 

} 

其它依赖库 

无 

支持系统版本 

Openharmony5.0.0 ( api 12 )及以上 

隐私权限 

涉及到弹框提示的权限:无 

Harmony 集成流程解读 

Harmony 端支持验证码类型 

# 验证类型 

PC 

手机 H5 

IOS 

Android 

# Harmony 

微信小程序 智能无感 支持 支持 支持 支持 支持 支持 滑动拼图 支持 支持 支持 支持 支持 支持 文字点选 支持 支持 支持 支持 支持 

# 支持 

语序点选 支持 支持 支持 支持 支持 支持 乱序拼图 支持 支持 支持 支持 支持 不支持 空间推理 支持 支持 支持 支持 支持 支持 

# 语音验证 

支持 支持 支持 支持 支持 支持 刮刮卡 支持 不支持 不支持 不支持 不支持 不支持 滑动还原 支持 支持 支持 支持 支持 支持 旋转验证 

支持 

支持 

支持 

支持 

支持 

支持 

验证码调用流程图 

1-1 Harmony 流程 

描述与注释: 

SDK 初始化是芯盾验证码 SDK 必须调用的第一步,必须优先调用。 1 

2会检查传入参数并调用服务端接口检查 js 文件是否有更新。并将最 新的 js 文件信息保存到本地。 

3是真正弹出验证码。 

4调用接口报错,可根据返回结果查看错误原因。 

5是在目前验证码无法情况下,使用其他验证方式完成验证 

6是验证结束 

SDK 接口详情 

SDK 整体接口列表 

SDK 引入: 

import { TrusfortCaptchaManager } from 'captcha_lib' 

SDK 主体接口列表 

# 接口 

接口详情 

接口释义 

1.1 

TrusfortCaptchaManager.getInstance().init(); 

初始化接口 

初始化验证码运行环境 

* 描述: init 初始化接口 

1.2 

TrusfortCaptchaManager.getInstance().showCaptcha(uiContext,param) 

验证码显示接口 

@param uiContext 上下文,需要使用 UIContext 。 

@param param 验证码参数。 

{ 

captchaOption:{},// 验证码配置,类型为 Record<string,string| Object|number|boolean|undefined> ,参考 4.1.2option 配置项 onSuccess:(code,data)=>{},// 验证结果回调 

loadingViewBuilder:()=>{} // 可选,自定义 Loading 

} 

示例: 

let option: Record<string, number | boolean | string | Object | undefined> = {} option["appid"] = this.appId 

TrusfortCaptchaManager.getInstance().showCaptcha(this.getUIContext(), 

{ captchaOption: option, onSuccess: this.captchaOnSuccess }) 

1.3 

TrusfortCaptchaManager.getInstance().closeCaptcha(); 

关闭验证码。 

- 需在验证码结果回调后主动调用关掉验证码 

1.4 

TrusfortCaptchaManager.getInstance().startCollection() 

开始采集数据。 

- 当调用 init 函数初始化后会自动开始采集,如手动采集需至少采集 3 

- 秒数据再显示验证码,以保证人机识别的准确性。 

1.5 

TrusfortCaptchaManager.getInstance()).stopCollection() 

停止采集数据。 

- 请在验证码结束以后再调用,否则可能会引起采集不到数据导致结 

- 果不准确的问题。 

1.6 

TrusfortCaptchaManager.getInstance().devfp = devid; 

设置设备指纹。 

# @param devid 设备指纹 id 。 

- 可自定义传入设备指纹。 

1.7 

TrusfortCaptchaManager.getInstance().deviceInfo = devinfo 

设置设备信息 

@param deviceInfo 设备信息的字符串 

- 可传入自定义设备信息,需服务端修改解析逻辑保证传入的设备信 

- 息正确解码。 

1.8 

TrusfortCaptchaManager.getInstance().mirrorServerUrl = mirrorServerUrl 

设置资源服务器地址 

- 用于解决多环境问题。 

option 配置项 

参数 

类型 

说明 

默认 

appid 

string 

验证码业务 ID ,在验证码后管平台生成的业务场景 ID 

无 

server_url 

string 

验证码服务端 API 地址 

conn_timeout 

string 

请求超时时间 ( 单位:毫秒 ) 

3000ms 

custom_style 

JSONObject 

自定义样式 (json 格式 ) ,详情参见下面 4.1.4custom_style 说明 

ext_data 

JSONObject 

扩展字段 (json 格式 ) 

debug 

boolean 

是否开启 debug 输出,仅建议在联调阶段使用 

false 

img_server_url 

string 

客户端传递静态资源图片地址,如果传递则使用该地址,否则使用服 务端返回的地址 

空 

timeout_retry_limit 

int 

请求超时尝试次数,请求超时超过指定次数之后自动在 error 回调返回 离线校验 token 

3 

captcaptcha_load_timer_count 

int 

静态资源加载超时时间 ,500 的倍数,单位是毫秒 

3 

sm 

boolean 

是否使用国密 

false 

custom_style 设置接口参数列表 

参数 

数据类型 

说明 

borderRadius 

string 

边角大小,单位 px 示例 : 5px 

themeColor 

string 

主题色 示例: #F5F5F5 

# 覆盖范围: 

- 点选按钮背景色 

- 点选类验证码提示条字体颜色、边框颜色 

- 加载中 文字效果 

fontFamily 

string 

整体字体 示例: PingFangSC-Regular,PingFang SC layerTop 

string 

layer 方式弹框距离页面顶部距离 示例 :100px 

layerClose 

string 

弹窗右上角关闭按钮图标 base64 字符串 

loadingImg 

string 

主体背景加载中动态图片 base64 字符串 

refreshImg 

string 

右下角刷新按钮图片 base64 字符串 

tipBgImg 

string 

默认样式提示图片 base64 字符串 

errorImg 

string 

错误提示背景图 base64 字符串 

voice 

json 

语音类验证码配置信息 

- playingImg 

string 

播放语音时显示的播放中图片 base64 字符串 

- replayImg 

string 

点击播放后显示的重新播放按钮图片 base64 字符串 

- bgColor 

string 

语音验证码整体背景色 示例: #F5F5F5 

- playImg 

string 

页面加载后默认引导点击播放按钮图片 base64 字符串 

- inputText 

json 

# 录入语音验证码输入框样式 

- borderColor 

string 

# 边框颜色 

- color 

string 

# 录入框字体颜色 

- fontSize 

string 

字号 

- verifyBtn 

json 

验证按钮样式 

-borderRadius 

string 

验证按钮边框大小 示例 : 20px 

-fontSize 

string 

字号 

tip 

json 

提示信息提示条样式 

# -fontWeight 

string 

字体粗细 

-fontSize 

string 

字号 

- success 

json 成功时提示信息样式 

- color 

string 字体或边框颜色 

- fail 

json 失败时提示信息样式 

- color 

string 字体或边框颜色 

- warn 

json 告警时提示信息样式 

- color 

string 

# 字体或边框颜色 

slide 

json 

滑动类验证码样式配置 

- bgImg 

json 

# 滑块背景图片 

- wait 

string 

等待验证时滑块背景图片 

- ing string 

验证时滑块背景图片 

- success 

string 

验证成功时滑块背景图片 

- fail 

string 

验证失败时滑块背景图片 

- bgColor 

json 

# 滑块背景颜色 

- wait 

string 

等待验证时滑块背景颜色 

- ing 

string 

验证时滑块背景颜色 

- success 

string 

验证成功时滑块背景颜色 

- fail 

string 

验证失败时滑块背景颜色 

- border 

json 

滑块边框颜色 

- wait 

string 

等待验证时滑块边框颜色 

- ing 

string 

验证时滑块边框颜色 

# - success 

string 

# 验证成功时滑块边框颜色 

- fail 

string 

# 验证失败时滑块边框颜色 

- tip 

json 

# 滑块提示按钮 

- borderColor 

string 

# 边框颜色 

- color 

string 

字体颜色 

验证码结果回调接口 

3.1 

onSuccess(code: number, data: string)=>void 

验证码结果回调接口 

# * 验证码结果 

@param code 验证结果的状态码 

@param data 验证通过返回的数据。当 code 值为 1000 时返回,其余 

# 情况返回空 , 返回格式如下: 

{ 

"token":"f64d0c42260e4fb2a7ff66485e9b4bb5", 

"sid":"949ff505c2be4baeba4a350c2fa95256", 

"code":1000, 

"msg":"" 

} 

接口错误码 错误码 错误码说明 后续动作 

1000 

接口请求成功 

- 

1001 参数错误 必要的参数缺失,具体可以参考 msg 1002 

用户取消验证 

5004 

请求超时 

# 有可能是断网或服务宕机 

5005 

降级 

走降级逻辑,跳过验证码,走其他方式 

5099 

服务端返回数据有问题 

联调服务排查是否是配置问题 

9001 

参数有问题 

一般为请求参数有问题,查看服务日志查看 

9002 

数据不存在 

排查 SDK 集成配置的 appid 在后管平台场景配置中是否存在 

排查 SDK 集成配置中 appid 对应的验证码在 “ 自定义 -> 验证码管理 ” 页 面是否有生成验证码 

9003 

请求超时 

点击尝试重试 

9004 

二次校验 TOKEN 不存在或已经过期 

重新进行验证码验证 

9005 

流控控制 

短期流控,稍候重试 

9007 

验证失败,滑动或点击位置校验失败 继续重新验证 

9008 

TOKEN-SID 变动 , 下发 TOKEN 时 SID 与 TOKEN 校验 SID 不一致 检查二次校验上送的 token 和 sid 是否匹配 

9009 

TOKEN-IP 变动 , 下发 TOKEN 时 IP 与 TOKEN 校验 IP 不一致 排查 IP 获取的是否都正确 

9010 

终端存在风险,需进行加强验证 

9011 命中风控阻断规则 

验证码验证被阻断,改用其他验证方式 

9999 

服务器内部错误 服务不可用,改用其他验证方式
