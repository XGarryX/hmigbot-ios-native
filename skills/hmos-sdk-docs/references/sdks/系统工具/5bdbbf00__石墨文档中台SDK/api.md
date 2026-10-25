# 石墨预览组件。 

类型: @ComponentV2 struct 。 

# 静态方法 

|名称 类型||说|明|
|---|---|---|---|
|initializ e (options?: => void|OfceInitializeOptions)|初 是|始化石墨预览组件,根据使用场景决定 否需要调用。|
|组件参数 名称|类型|必 填|说明|
|license|License|否|授权证书,如果初始化组件中已经传 入,此处可以神略,否则不传为试用授 权,传入及发生变化将立即验证授权。|
|fle|string|否|Ofce 文件 URI,发生变化会自动打开 预览,传 undefned 将关闭文件预 览。|
|onAuthorize|AuthorizeHandler|否|授权认证回调,首次认证及认证信息发 生变化时触发回调,不可修改。|
|onAttachmentOpe n|AttachmentOpenHandle r|否|附件打开回调,打开预览文件内的附件 时触发回调,不可修改。|
|onAttachmentSave|AttachmentSaveHandle r|否|附件另存回调,另存预览文件内的附件 时触发回调,不可修改。|
|onLinkOpen|LinkOpenHandler|否|链接打开回调,打开预览文件内的链接 时触发回调,不可修改。|
|onFullscreen|FullscreenHandler|否|全屏回调,预览文件请求进入或退出全 屏时触发回调,不可修改。|

file string
onAuthorize
onAttachmentOpe
n r
onAttachmentSave
r

时触发回调,不可修改。
否
屏时触发回调,不可修改。

初始化参数。 类型: Object 

名称 类型
license License
onAuthorize
webCustomSchem
es []

必 说明
填
否 授权证书,不传为试用授权。
否
否
使用了 @ohos.web.webview 的
wController.customizeSchemes

Webvie
 接口,

|名称|类型|必 填|说明|
|---|---|---|---|
|license|License|否|授权证书,不传为试用授权。|
|onAuthorize|AuthorizeHandler|否|授权认证回调,当传入授权证书时生效。|
|webCustomSchem|WebCustomScheme|否|ArkWeb 自定义协议配置。如果您的应用|
|es|[]||使用了 @ohos.web.webview 的Webvie wController.customizeSchemes接口, 则需要改造为将 webCustomSchemes 通 过此参数传入 ShimoOfce.initialize 接 口。|

口。

# 授权证书。 

类型: Object 。 

|名称|类型|必填|说明|
|---|---|---|---|
|data|string|是|授权证书文件文本内容,UTF-8 编 码。|
|key|string|是|授权证书密钥,Base64 编码。|

。
说明

# 授权认证回调。 

类型: (event: AuthorizeEvent) => void 。 

|名称|类型|必填|说明|
|---|---|---|---|
|event|AuthorizeEvent|是|授权认证回调事件。|

授权认证回调事件。
。
说明

# 附件打开回调。 

类型: (event: AttachmentEvent) => void 。 

|名称|类型|必 填|说明|
|---|---|---|---|
|even|AttachmentEven|是|附件打开回调事件。调用 event.preventDefault() 将阻止默|
|t|t||认打开行为。|

even AttachmentEven 是
t t

认打开行为。

。
说明

附件另存回调。 

类型: (event: AttachmentEvent) => void 。 

|名称|类型|必 填|说明|
|---|---|---|---|
|even|AttachmentEven|是|附件另存回调事件。调用 event.preventDefault() 将阻止默|
|t|t||认另存行为。|

认另存行为。
。

# 链接打开回调。 

类型: (event: LinkEvent) => void 。 

|名称|类型|必 填|说明|
|---|---|---|---|
|even|LinkEven|是|链接打开回调事件。调用 event.preventDefault() 将阻止默认打开|
|t|t||行为。|

。
说明

# 全屏回调。 

类型: (event: FullscreenEvent) => void 。 

|名称|类型|必 填|说明|
|---|---|---|---|
|even|FullscreenEve|是|全屏回调事件。调用 event.preventDefault() 将阻止默认进|
|t|nt||入/退出全屏行为。|

入/退出全屏行为。

# 授权认证事件。 

类型: Object 。 

名称 类型
status AuthorizationStatus
license LicenseInfo

必填 说明
是 认证状态。
否 认证证书信息。

|名称|类型|必填|说明|
|---|---|---|---|
|status|AuthorizationStatus|是|认证状态。|
|license|LicenseInfo|否|认证证书信息。|

附件事件。 

类型:IPreventableEvent。 

|名称|类型|必填|说明|
|---|---|---|---|
|fle|string|是|附件文件 URI。|
|preventDefault|() => void|是|继承至IPreventableEvent。阻止默认行为。|

必填 说明
是 附件文件 URI。
是 继承至 IPreventableEvent

链接事件。 

类型:IPreventableEvent。 

|名称|类型|必填|说明|
|---|---|---|---|
|url|string|是|链接 URL。|
|preventDefault|() => void|是|继承至IPreventableEvent。阻止默认行为。|

必填 说明
是 链接 URL。
是 继承至 IPreventableEvent

全屏事件。 

类型:IPreventableEvent。 

|名称|类型|必填|说明|
|---|---|---|---|
|fullscreen|boolean|是|true 表示进入全屏,false表示退出全屏。|
|preventDefault|() => void|是|继承至IPreventableEvent。阻止默认行为。|

必填 说明
是 true 表示进入全屏,false表示退出全屏。
是 继承至 IPreventableEvent

# 可阻止事件类型接口。 

类型: interface 。 

|名称|类型|必填|说明|
|---|---|---|---|
|preventDefault|() => void|是|阻止默认行为。|

必填 说明
是 阻止默认行为。

认证证书信息。 

类型: Object 。 

说明

|名称|类型|必填|说明|
|---|---|---|---|
|expiredAt|number|是|授权证书过期时间戳。|

expiredAt number 是
AuthorizationStatus
认证状态。
 类型: enum 。
名称 值
Trial Trial

授权证书过期时间戳。
说明
试用授权。

|认证状态。 |||
|---|---|---|
|类型: enum|。||
|名称|值|说明|
|Trial|Trial|试用授权。|
|TrialExpired|TrialExpired|试用授权(已过期)。|
|Authorized|Authorized|正式授权。|
|Expired|Expired|正式授权(已过期)。|
|Invalid|Invalid|授权无效。|
|Error|Error|认证失败。|

TrialExpired TrialExpired
Authorized Authorized
Expired Expired
Invalid Invalid
Error Error

试用授权(已过期)。
正式授权。
正式授权(已过期)。
授权无效。
认证失败。
