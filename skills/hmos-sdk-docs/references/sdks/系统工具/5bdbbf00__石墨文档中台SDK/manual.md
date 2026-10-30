https://open.shimo.im/client。  。
.doc .docm .xlsx .xls .xlsm .pptx

石墨文档中台鸿蒙 SDK。 

一行代码即可让你的鸿蒙应用支持 Word 文档、Excel 表格、PowerPoint 幻灯片等 Office 文 件离线预览。 

详情请访问石墨文档中台官网 https://open.shimo.im/client。  。 支持 API12 release 及以上版本。 

 已支持的文件类型: .docx
Install
1
Usage
1.

.doc .docm .xlsx .xls .xlsm .pptx

已支持的文件类型: .docx .doc .docm .xlsx .xls .xlsm .pptx .ppt .pptm 

> 1 `ohpm install @shimo/sdk-client` 

1. 在页面中引入 ShimoOffice 组件。 

1
1.
  如果您的应用使用了 ArkWeb 的
态方法。
  如果您的应用使用了
需要改造为将
 
省略。
1

Web
 的  WebviewController.customizeSchemes
 通过 ShimoOffice 初始化接口传入。

 接口,则

> 1 `import { ShimoOffice } from '@shimo/sdk-client';` 

1. (可选)初始化 ShimoOffice 组件。 

- 如果您的应用使用了 ArkWeb 的 Web 组件,则需要在 ArkWeb 引擎初始化之前调用此静 态方法。 

- 如果您的应用使用了 @ohos.web.webview 的 WebviewController.customizeSchemes 接口,则 需要改造为将 webCustomSchemes 通过 ShimoOffice 初始化接口传入。 

- 如果您通过初始化接口传入了授权文件、授权密钥,则后续使用 ShimoOffice 组件时可以 省略。 

> 1 `ShimoOffice.initialize({ license: { data: '[license file content]', ke y: '[license key]', webCustomSchemes: [] }' })` 

1.
 
1
Interface
ShimoOffice

1. 在页面构造中使用 ShimoOffice 组件,并传入授权文件、授权密钥、Office 文件 uri。 

- 如果在初始化中已经传入授权文件、授权密钥,则可以省略。 

> 1 `ShimoOffice({ license: { data: '[license file content]', key: '[licens e key]' }, file: '[office file uri]' })` 

石墨预览组件。 类型: @ComponentV2 struct 。 

说明
)
是否需要调用。

静态方法 

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

license License
file string
onAuthorize

onAttachmentOpe
n r
onAttachmentSave
r
onLinkOpen
onFullscreen
OfficeInitializeOptions

否
时触发回调,不可修改。
否
时触发回调,不可修改。
否
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

Webvie

|名称|类型|必 填|说明|
|---|---|---|---|
|license|License|否|授权证书,不传为试用授权。|
|onAuthorize|AuthorizeHandler|否|授权认证回调,当传入授权证书时生效。|
|webCustomSchem|WebCustomScheme|否|ArkWeb 自定义协议配置。如果您的应用|
|es|[]||使用了 @ohos.web.webview 的Webvie wController.customizeSchemes接口, 则需要改造为将 webCustomSchemes 通 过此参数传入 ShimoOfce.initialize 接 口。|

wController.customizeSchemes
口。

 接口,

# 授权证书。 

类型: Object 。 

|名称|类型|必填|说明|
|---|---|---|---|
|data|string|是|授权证书文件文本内容,UTF-8 编 码。|
|key|string|是|授权证书密钥,Base64 编码。|

# 授权认证回调。 

类型: (event: AuthorizeEvent) => void 。 

。
说明
授权认证回调事件。
。

|名称|类型|必填|说明|
|---|---|---|---|
|event|AuthorizeEvent|是|授权认证回调事件。|

# 附件打开回调。 

类型: (event: AttachmentEvent) => void 。 

名称 类型 必 说明
填
even AttachmentEven 是
t t

说明
认打开行为。

|名称|类型|必|说明|
|---|---|---|---|
|||填||
|even|AttachmentEven|是|附件打开回调事件。调用 event.preventDefault() 将阻止默|
|t|t||认打开行为。|

。

附件另存回调。 

类型: (event: AttachmentEvent) => void 。 

说明
认另存行为。
。

|名称|类型|必 填|说明|
|---|---|---|---|
|even|AttachmentEven|是|附件另存回调事件。调用 event.preventDefault() 将阻止默|
|t|t||认另存行为。|

# 链接打开回调。 

类型: (event: LinkEvent) => void 。 

|名称|类型|必 填|说明|
|---|---|---|---|
|even|LinkEven|是|链接打开回调事件。调用 event.preventDefault() 将阻止默认打开|
|t|t||行为。|

全屏回调。 

类型: (event: FullscreenEvent) => void 。 

 类型:
名称 类型 必
填
even FullscreenEve 是
t nt
AuthorizeEvent
授权认证事件。

。
说明
入/退出全屏行为。

|名称|类型|必 填|说明||
|---|---|---|---|---|
|Author 授权认证 类型: even t|izeEvent 事件。 Object 。 FullscreenEve nt|是|全屏回调 入/退出|事件。调用 event.preventDefault() 将阻止默认进 全屏行为。|
|名称|类型||必填|说明|
|status|Authorization|Status|是|认证状态。|
|license|LicenseInfo||否|认证证书信息。|

必填 说明
是 认证状态。
否 认证证书信息。

AttachmentEvent

附件事件。 

必填 说明
是 附件文件 URI。
是 继承至 IPreventableEvent

类型:IPreventableEvent。 

|名称|类型|必填|说明|
|---|---|---|---|
|fle|string|是|附件文件 URI。|
|preventDefault|() => void|是|继承至IPreventableEvent。阻止默认行为。|

链接事件。 

必填 说明
是 链接 URL。
是 继承至 IPreventableEvent

类型:IPreventableEvent。 

|名称|类型|必填|说明|
|---|---|---|---|
|url|string|是|链接 URL。|
|preventDefault|() => void|是|继承至IPreventableEvent。阻止默认行为。|

全屏事件。 

必填 说明
是 true 表示进入全屏,false表示退出全屏。
是 继承至 IPreventableEvent

类型:IPreventableEvent。 

|名称|类型|必填|说明|
|---|---|---|---|
|fullscreen|boolean|是|true 表示进入全屏,false表示退出全屏。|
|preventDefault|() => void|是|继承至IPreventableEvent。阻止默认行为。|

可阻止事件类型接口。 

必填 说明
是 阻止默认行为。

类型: interface 。 

|名称|类型|必填|说明|
|---|---|---|---|
|preventDefault|() => void|是|阻止默认行为。|

认证证书信息。 

类型: Object 。 

 类型: Object 。

说明
授权证书过期时间戳。

|名称|类型|必填|说明|
|---|---|---|---|
|expiredAt|number|是|授权证书过期时间戳。|

认证状态。 

类型: enum 。 

名称 值
Trial Trial
TrialExpired TrialExpired
Authorized Authorized
Expired Expired
Invalid Invalid
Error Error

|名称|值|说明|
|---|---|---|
|Trial|Trial|试用授权。|
|TrialExpired|TrialExpired|试用授权(已过期)。|
|Authorized|Authorized|正式授权。|
|Expired|Expired|正式授权(已过期)。|
|Invalid|Invalid|授权无效。|
|Error|Error|认证失败。|

试用授权。
试用授权(已过期)。
正式授权。
正式授权(已过期)。
授权无效。
认证失败。

Example
1
2
3
4
5
6   status: string
7   expiredAt?: number;
8 }

> 1 `import { ShimoOffice, License, AuthorizationStatus, AuthorizeHandler, FullscreenHandler } from '@shimo/sdk-client';` 

> 2 `import { picker, fileIo } from '@kit.CoreFileKit';` 

> 3 `import { buffer } from '@kit.ArkTS';` 4 

> 5 `interface AuthorizationInfo {` 

> 6 `status: string` 

> 7 `expiredAt?: number;` 

> 8 `}` 9 

> 10 `const COMPONENT_SPACE = 10;` 11 

> 12 `@Entry` 

> 13 `@Component` 

> 14 `struct Index {` 

> 15 `//` 授权证书 

> 16 `@State private license?: License = undefined;` 

> 17 `//` 授权信息 

> 18 `@State authorizationInfo?: AuthorizationInfo = undefined;` 

> 19 `// Office` 文件 `uri` 

> 20 `@State private officeFile?: string = undefined;` 

> 21 `//` 是否允许全屏模式 

9
10 const COMPONENT_SPACE = 10;
11
12 @Entry
13 @Component
14 struct Index {
15   //  授权证书
16
17   //  授权信息
18
19   // Office  文件  uri

21   //  是否允许全屏模式

22
23   //  全屏模式
24
25
26   build() {
27
28
29         Button(' 授权 ')
30
31         Button(' 打开 ')

|`@State private enableFullscreen: boolean = true;` 22 |
|---|
|`//`全屏模式 23|
|
`@State private fullscreen: boolean = false;`
24
25|
|`build() {` 26|
|`Column({ space: COMPONENT_SPACE }) {` 27 `Row({ space: COMPONENT_SPACE }) {` 28|
|`Button('`授权`')` 29 `.onClick(this.onAuthorizationClick)` 30|
|`Button('`打开`')` 31 `.onClick(this.onOpenClick)` 32|
|`Button('`关闭`')` 33 `.enabled(!!this.officeFile)` 34|
|`.onClick(this.onCloseClick)` 35|
|`Column() {` 36|
|`Row() {` 37|
|`Checkbox()` 38|
|`.select($$this.enableFullscreen)` 39|
|`Text('`允许全屏`')` 40|
|`}` 41 |
|`}` 42 |
|`}` 43|
|`.alignSelf(ItemAlign.Start)` 44 |
|`.visibility(this.fullscreen ? Visibility.None : Visibility.Visib` 45|
|`le)` |
|46 `Row() {` 47|
|`ShimoOffice({` 48|
|`license: this.license ? { data: this.license.data, key: thi` 49|
|`s.license.key } : undefined,`|
|`file: this.officeFile,` 50|
|`onAuthorize: this.onAuthorize,` 51|
|`onFullscreen: this.onFullscreen` 52|
|`})` 53|
|`.border({ width: 1, color: '#41464b' })` 54|
|`}` 55|
|`.layoutWeight(1)` 56|
|`}` 57|
|`.layoutWeight(1)` 58 `.padding(this.fullscreen ? undefined : COMPONENT_SPACE)` 59|
|`}` 60 |
|61|
|`//`点击打开按钮 62|
|`private readonly onOpenClick = () => {` 63|
|`const docPicker = new picker.DocumentViewPicker();` 64|
|`const pickerOptions = new picker.DocumentSelectOptions();` 65|
|`pickerOptions.fileSuffixFilters = ['.docx,.doc,.docm,.xlsx,.xls,.x` 66|
|`lsm,.pptx,.ppt,.pptm'];`|
|`docPicker.select(pickerOptions).then(selectResult => {` 67|

32
33         Button(' 关闭 ')
34
35
36         Column() {
37           Row() {
38             Checkbox()
39
40             Text('
41           }
42         }
43       }

44
45
le)
46
47       Row() {
48         ShimoOffice({
49
s.license.key } : undefined,
50
51
52

54
55       }
56       .layoutWeight(1)
57     }
58     .layoutWeight(1)
59
60   }
61
62   //  点击打开按钮
63
64

68
69       if (fileUri) {
70
71       }
72     });
73   };
74
75

|
68
 
|`const fileUri = selectResult[0];` |
|---|---|
|
69
 
70
 
71|`if (fileUri) {`
`this.officeFile = fileUri;`
`}`|
|
 
72|
`});`|
|
73
74|`};`|
|
75
 
76
 
77
 
78
79|`//`点击关闭按钮
`private readonly onCloseClick = () => {`
`this.officeFile = undefined;`
`};`|
|
80|`//`授权完成|
|
81|`private readonly onAuthorize: AuthorizeHandler = (event) => {`|
|
82|`this.authorizationInfo = {`|
|
83|`status: event.status,`|
|
84|`expiredAt: event.license?.expiredAt,`|
|
85|`}`|
|
86
87|`}`|
|
88|`//`切换全屏模式|
|
89|`private readonly onFullscreen: FullscreenHandler = (event) => {`|
|
90|`if (this.enableFullscreen) {`|
|
91|`this.fullscreen = event.fullscreen;`|
|
92|`} else {`|
|
93|`event.preventDefault();`|
|
94|`}`|
|
95|`};`|
|
96||
|
97|`//`授权证书|
|
98|`@State private licenseFile?: string = undefined;`|
|
99|`//`证书密钥|
|
100
101|`@State private licenseKey: string = '';`|
|
102|`//`授权弹窗`ID`|
|
103
104|`private authorizationDialogId: number = 0;`|
|
105|`//`授权弹窗|
|
106|`@Builder`|
|
107|`private authorizationDialog() {`|
|
108|`Column({ space: COMPONENT_SPACE }) {`|
|
109|`Row({ space: COMPONENT_SPACE }) {`|
|
110|`Text('`授权信息:`')`|
|
111|`Text(this.getAuthorizationText())`|
|
112|`.layoutWeight(1)`|
|
113|`.maxLines(1)`|
|
114|`.textOverflow({ overflow: TextOverflow.MARQUEE })`|
|
115|`}`|
|
116|`.alignSelf(ItemAlign.Start)`|

76
77
78   };
79
80   //  授权完成
81
82
83       status: event.status,
84
85     }
86   }

88   //  切换全屏模式
89
90
91
92     } else {
93
94     }
95   };
96
97   //  授权证书
98

99   //  证书密钥
100
101
102   //  授权弹窗  ID
103
104
105   //  授权弹窗
106   @Builder
107
108
109
110         Text(' 授权信息:

111
112           .layoutWeight(1)
113           .maxLines(1)
114
115       }
116

117
118         Button(' 选择证书
119
120
d)

')

|117 118|`Row({ space: COMPONENT_SPACE }) {` `Button('`选择证书`')`|
|---|---|
|119|
`.onClick(this.onSelectLicenseClick)`|
|120|`Text(this.licenseFile ? decodeURI(this.licenseFile) : undefine`|
||`d)`|
|121|`.layoutWeight(1)`|
|122|`.maxLines(1)`|
|123|`.textOverflow({ overflow: TextOverflow.Ellipsis })`|
|124|`.ellipsisMode(EllipsisMode.START)`|
|125|`Button('`导入密钥`')`|
|126|`.onClick(this.onSelectLicenseKeyClick)`|
|127|`}`|
|128 129|`.alignSelf(ItemAlign.Start)`|
|130|`Row({ space: COMPONENT_SPACE }) {`|
|131|`TextArea({ text: $$this.licenseKey, placeholder: '`请输入证书密钥`'`|
||`})`|
|132|`.layoutWeight(1)`|
|133|`.height('100%')`|
|134|`}`|
|135 136|`.layoutWeight(1)`|
|137|`Row({ space: COMPONENT_SPACE }) {` |
|138|`Button('`撤销`')`|
|139|`.visibility(this.license ? Visibility.Visible : Visibility.H`|
||`idden)`|
|140|`.onClick(this.onRevokeAuthorizationClick)`|
|141|`Button('`授权`')`|
|142|`.enabled(!!this.licenseFile && !!this.licenseKey)`|
|143|`.onClick(this.onAuthorizeClick)`|
|144|`Button('`关闭`').onClick(this.onCloseAuthorizationClick)`|
|145|`}`|
|146|`.alignSelf(ItemAlign.End)`|
|147|`}`|
|148|`.padding(COMPONENT_SPACE * 2)`|
|149|`.constraintSize({ maxWidth: 600, maxHeight: 400 })`|
|150|`.onClick(this.onAuthorizationDialogClick)`|
|151 152|`}`|
|153|`private getAuthorizationText() {`|
|154|`let text: string;`|
|155|`if (!this.authorizationInfo) {`|
|156|`text = '`未授权`';`|
|157|`} else {`|
|158|`switch (this.authorizationInfo.status) {`|
|159|`case AuthorizationStatus.Trial:`|
|160|`text = '`试用`';`|
|161|`break;`|
|162|`case AuthorizationStatus.TrialExpired:`|

121           .layoutWeight(1)
122           .maxLines(1)
123
124
125         Button(' 导入密钥
126
127       }
128
129
130
131
})

请输入证书密钥 '

132           .layoutWeight(1)
133           .height('100%')
134       }
135       .layoutWeight(1)
136
137
138         Button(' 撤销 ')
139
idden)
140
141         Button(' 授权 ')
142

143
144         Button(' 关闭
145       }
146
147     }
148
149
150
151   }
152
153

155
156       text = ' 未授权 ';
157     } else {
158
159
160           text = ' 试用 ';
161           break;
162

163           text = '
164           break;
165

';

> 163 `text = '` 试用过期 `';` 

> 164 `break;` 

> 165 `case AuthorizationStatus.Authorized:` 

> 166 `text = '` 已授权 `';` 

> 167 `break;` 

> 168 `case AuthorizationStatus.Expired:` 

> 169 `text = '` 过期 `';` 

> 170 `break;` 

> 171 `case AuthorizationStatus.Invalid:` 

> 172 `text = '` 无效 `';` 

> 173 `break;` 

> 174 `case AuthorizationStatus.Error:` 

> 175 `text = '` 异常 `';` 

> 176 `break;` 

> 177 `default:` 

> 178 `text = '` 未授权 `';` 

> 179 `break;` 

> 180 `}` 

> 181 `if (this.authorizationInfo.expiredAt) {` 

> 182 `const expiredDate = new Date(this.authorizationInfo.expiredA t);` 

> 183 `text += `` (至 `${expiredDate.getFullYear()}` 年 `${expiredDate.getMo nth() + 1}` 月 `${expiredDate.getDate()}` 日) ``` 

> 184 `}` 

> 185 `}` 

> 186 `return text;` 

> 187 `}` 188 

> 189 `//` 密钥输入框失焦 

> 190 `private blurLicenseKeyInput() {` 

> 191 `this.getUIContext().getFocusController().clearFocus();` 

> 192 `}` 193 

166           text = ' 已授权
167           break;
168
169           text = ' 过期 ';
170           break;
171
172           text = ' 无效 ';
173           break;
174
175           text = ' 异常 ';
176           break;

178           text = ' 未授权
179           break;
180       }
181
182
t);
183         text += ` (至
nth() + 1} 月
184       }
185     }
186     return text;

> 194 `//` 读取文件文本 

- 195 `private readFileText(fileUri: string) {` 

- 196 `let file: fileIo.File | undefined;` 

- 197 `try {` 

- 198 `file = fileIo.openSync(fileUri, fileIo.OpenMode.READ_ONLY);` 

199
200
201
202
203       return text;
204     } catch {
205       return '';
206     } finally {
207       if (file) {
208         try {
209

- 199 `const fileSize = fileIo.statSync(file.fd).size;` 

- 200 `const fileBuffer = new ArrayBuffer(fileSize);` 

- 201 `fileIo.readSync(file.fd, fileBuffer);` 

|
202|`const text = buffer.from(fileBuffer).toString();`|
|---|---|
|
203|`return text;`|
|
204|`} catch {`|
|
205|`return '';`|
|
206|`} finally {`|
|
207|`if (file) {`|
|
208|`try {`|
|
209|`fileIo.closeSync(file);`|

> 210 `} catch {}` 

> 211 `}` 

> 212 `}` 

> 213 `}` 214 

|215|`//`点击授权按钮|
|---|---|
|216|`private readonly onAuthorizationClick = () => {`|
|217 218 219 220 221 222|`this.getUIContext().getPromptAction().openCustomDialog({` `builder: () => {` `this.authorizationDialog()` `}` `}).then((dialogId: number) => {` `this.authorizationDialogId = dialogId;`|
|223 224 |`});` `};`|
|225 226 227 228 229 230|`//`点击窗口空白处 `private readonly onAuthorizationDialogClick = () => {` `this.blurLicenseKeyInput();` `}`|
|231|`//`点击选择证书按钮|
|232 233|`private readonly onSelectLicenseClick = () => {` `const docPicker = new picker.DocumentViewPicker();`|
|234 235|`docPicker.select().then(selectResult => {` `const fileUri = selectResult[0];`|
|236 237|`if (fileUri) {` `this.licenseFile = fileUri;`|
|238|`}`|
|239 240|`});` `};`|
|241||
|242|`//`点击从文件导入密钥按钮|
|243|`private readonly onSelectLicenseKeyClick = () => {`|
|244|`const docPicker = new picker.DocumentViewPicker();`|
|245|`docPicker.select().then(selectResult => {`|
|246|`const fileUri = selectResult[0];`|
|247 248|`if (fileUri) {` `this.licenseKey = this.readFileText(fileUri);`|
|249|`}`|
|250 251 |`});` `}`|
|252 253|`//`点击授权弹窗撤销按钮|
|254|`private readonly onRevokeAuthorizationClick = () => {`|
|255|`this.blurLicenseKeyInput();`|
|256|`this.license = undefined;`|
|257|`this.licenseFile = undefined;`|
|258|`this.licenseKey = '';`|

222
223     });
224   };
225
226   //  点击窗口空白处
227
228
229   }
230
231   //  点击选择证书按钮
232
233

234
235
236       if (fileUri) {
237
238       }
239     });
240   };
241
242   //  点击从文件导入密钥按钮
243
244

246
247       if (fileUri) {
248
249       }
250     });
251   }
252
253   //  点击授权弹窗撤销按钮
254
255
256

257
258     this.licenseKey = '';

259   };
260
261   //  点击授权弹窗授权按钮
262
263
264
265
266       if (licenseData) {
267

> 259 `};` 260 

> 261 `//` 点击授权弹窗授权按钮 

> 262 `private readonly onAuthorizeClick = () => {` 

> 263 `this.blurLicenseKeyInput();` 

> 264 `if (this.licenseFile && this.licenseKey) {` 

> 265 `const licenseData = this.readFileText(this.licenseFile);` 

> 266 `if (licenseData) {` 

> 267 `this.license = { data: licenseData, key: this.licenseKey };` 

> 268 `} else {` 

> 269 `this.license = undefined;` 

> 270 `}` 

> 271 `}` 

> 272 `};` 273 

> 274 `//` 点击授权弹窗关闭按钮 

> 275 `private readonly onCloseAuthorizationClick = () => {` 

> 276 `this.blurLicenseKeyInput();` 

> 277 `this.getUIContext().getPromptAction().closeCustomDialog(this.autho rizationDialogId);` 

> 278 `}` 

> 279 `}` 

269
270       }
271     }
272   };
273
274   //  点击授权弹窗关闭按钮
275
276
277
rizationDialogId);
278   }

}
Contact
授权申请
 技术支持: raoxin@shimo.imraoxin@shimo.im
石墨文档 shimo.im
Copyright © 武汉初心科技有限公司

授权申请 技术支持: raoxin@shimo.imraoxin@shimo.im 石墨文档 shimo.im
