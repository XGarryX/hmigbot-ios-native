XYLINK Developer Center

### MeetingKit_Harmony_API概览-description_html2

### MeetingKit_Harmony_API概览-description_html2

### API 概览

# 小鱼易连           小鱼

基础API

UI配置

业务回调

### 1

### 2

2

2

2

2

2

2

3

3

3

3

3

获取Meetingkit实例(XYMeetingKitImp)

初始化(XYMeetingKitInterface)

添加代理(XYMeetingKitInterface)

移除代理(XYMeetingKitInterface)

呼叫(XYMeetingKitInterface)

获取通话状态(XYMeetingKitInterface)

页面代理(XYMeetingKitDelegate)

设置上下文(XYScreenUtil)

# 小鱼易连           小鱼易连           小鱼易连           小鱼易连

小鱼易连           小鱼易连           小鱼易连           小鱼易连           小鱼易连           小鱼易连

小鱼易连           小鱼易连           小鱼易连           小鱼易连           小鱼易连           小鱼易连           小鱼易连           小鱼

小鱼易连           小鱼易连           小鱼易连           小鱼易连           小鱼易连           小鱼易连           小鱼易连           小鱼

小鱼易连           小鱼易连           小鱼易连           小鱼易连           小鱼易连

# 小鱼易连           小鱼易连           小鱼易连

# 小鱼易连

第1页/共4页

XYLINK Developer Center

# API 概览

基础API

# 小鱼易连           小鱼

| 小 方法 | 易 连 鱼 描述 易 |
|---|---|
| getInstance | 小 鱼 获取meetingkit 实例 小 |
| 连 startup 易 | 初始化meetingkit |
| 鱼 易 addDelegate 小 | 连 退出sdk 连 |
| 鱼 小 removeDelegate | 易 移除代理 鱼 |
| makeCall 连 | 小 呼叫 |
| 连 getCallState | 获取通话状态 |

# UI配置

| 连 方法 | 小 描述 |
|---|---|
| 易 鱼 setWindowStage 易 | 连 设置上下文(请在windowStage.loadContent之后调用) |

# 业务回调

| 连 方法 易 | 描述 |
|---|---|
| 鱼 onDidBackRootPage 小 | 连 页面退出规则 易 |

获取Meetingkit实例(XYMeetingKitImp)

/**

 * 获取meeting 实例

 * @returns

 */

 static getInstance(): XYMeetingKitInterface;

初始化(XYMeetingKitInterface)

 /**

  * 初始化

  */

 startup(): void

添加代理(XYMeetingKitInterface)

小鱼易连           小鱼易连           小鱼易连           小鱼易连           小鱼易连           小鱼易连           小鱼易连           小鱼

小鱼易连           小鱼易连           小鱼易连           小鱼易连           小鱼易连

# 小鱼易连           小鱼易连           小鱼易连

# 小鱼易连

第2页/共4页

XYLINK Developer Center

| 鱼 易 | 鱼 小 连 /** * 添加代理 连 * @param delegate 易 连 */ 鱼 易 addDelegate(delegate: XYMeetingKitDelegate): void 小 连 鱼 |  |
|---|---|---|

移除代理(XYMeetingKitInterface)

 /**

  * 移除代理

  * @param delegate

  */

 removeDelegate(delegate: XYMeetingKitDelegate): void

# 小鱼易连           小鱼易连           小鱼易连           小鱼易连

呼叫(XYMeetingKitInterface)

 /**

  * 呼叫

  * @param callConfig

  */

 makeCall(callConfig: XYSDKCallConfig): void;

获取通话状态(XYMeetingKitInterface)

小鱼易连           小鱼易连           小鱼易连           小鱼易连           小鱼易连           小鱼易连

 /**

  * 获取通话状态

  */

 getCallState(): XYSDKCallState;

页面代理(XYMeetingKitDelegate)

小鱼易连           小鱼易连           小鱼易连           小鱼易连           小鱼易连           小鱼易连           小鱼易连           小鱼

/**

  * 返回root 默认不处理则返回上一级页面

  * @returns

  */

 onDidBackRootPage?(): boolean;

设置上下文(XYScreenUtil)

小鱼易连           小鱼易连           小鱼易连           小鱼易连           小鱼易连           小鱼易连           小鱼易连           小鱼

小鱼易连           小鱼易连           小鱼易连           小鱼易连           小鱼易连

# 小鱼易连           小鱼易连           小鱼易连

# 小鱼易连

第3页/共4页

XYLINK Developer Center

| 鱼 易 | 鱼 小 连 /** * 设置上下文 连 * @param windowStage 易 连 * @param callback 鱼 易 */ 小 连 鱼 易 setWindowStage(windowStage: window.WindowStage, callback?: ()=> void): void 小 鱼 |  |
|---|---|---|

小鱼易连           小鱼易连           小鱼易连           小鱼易连           小鱼易连           小鱼易连

小鱼易连           小鱼易连           小鱼易连           小鱼易连           小鱼易连           小鱼易连           小鱼易连           小鱼

小鱼易连           小鱼易连           小鱼易连           小鱼易连           小鱼易连           小鱼易连           小鱼易连           小鱼

小鱼易连           小鱼易连           小鱼易连           小鱼易连           小鱼易连

# 小鱼易连           小鱼易连           小鱼易连

# 小鱼易连

第4页/共4页
