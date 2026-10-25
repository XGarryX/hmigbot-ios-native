# **MobLink-OHOS** 

# **SDK-集成** 

## **一** **.添加SDK依赖** 

在 **Terminal** 窗口中,执行如下命令进行安装 

ohpm install @zztsdk/zztcore 

ohpm install @zztsdk/moblink 

## **二.权限** 

ohos.permission.INTERNET 

### **建议权限** 

ohos.permission.APP_TRACKING_CONSENT // 用于产生设备ID ohos.permission.GET_NETWORK_INFO // 用于判断网络类型,进行连接与数据传输优化 

## **三.导入模块** 

import { ZztSDK } from '@zztsdk/zztcore'; 

import mobLink from '@zztsdk/moblink'; 

## **四.Deep Linking配置** 

配置module.json5文件 

为了能够支持被其他应用访问,目标应用需要在module.json5配置文件中配置skills标签。 配置示例如下 

{ "module": { // ... "abilities": [ { // ... "skills": [ { "entities": [ "entity.system.home" 

], "actions": [ "action.system.home" ] }, { "actions": [ // actions不能为空,actions为空会造成目标方匹配失败。 "ohos.want.action.viewData" ], "uris": [ { // scheme必选,可以自定义,以link为例,需要替换为实际的scheme "scheme": "link", // host必选,配置待匹配的域名 "host": "www.example.com" } ] } // 新增一个skill对象,用于跳转场景。如果存在多个跳转场景,需配置多个skill对象。 ] } ] } } 

# **SDK-API** 

## **约束** 

本模块首批接口从 OpenHarmony SDK API version 12 开始支持。 

## **ZztSDK初始化** 

#### **注意:请确保传入context非空** 

init()接口内部会做隐私授权状态的判断,在应用向ZztSDK提交隐私授权同意状态之前不会做任何业务的初始化, 可放心调用 

" " ZztSDK.init(context, 您的AppKey", 您的AppSecret") 

## **ZztSDK隐私提交** 

#### **注意:请确保在调用初始化方法后调用该方法** 

应用在向终端用户展示“隐私声明”弹框,并获取终端用户的隐私授权结果后,需将隐私授权结果回传给ZztSDK。 

//仅当授权结果为“true”时,ZztSDK各项功能才可正常使用。 ZztSDK.submitPolicyGrantResult(granted) 

## **MobLink初始化** 

#### **注意:请确保在调用ZztSDK初始化和隐私提交方法之后调用该方法** 

export function init(context: Context): void 

//示例代码: //请确保传入context非空 mobLink.init(this.context) 

#### **MobLink初始化示例代码** : 

//ZztSDK初始化 " " ZztSDK.init(this.context, 您的AppKey", 您的AppSecret") //ZztSDK隐私提交 ZztSDK.submitPolicyGrantResult(true) //MobLink初始化 mobLink.init(this.context) 

## **制作场景(getMobID)** 

可使用下面的方式来获取MobLink的场景ID:MobId,并将其用于和对应链接进行拼接 (eg:***&mobid=4557513629786705920) 

。在场景数据还原时MobLink会根据MobId还原出场景数据,并回调用户进行特定的操作 

export function getMobID(scene: Scene, listener: MobIDListener) 

//示例代码: let scene = new mobLink.Scene() scene.path = "/demo/a" scene.params.set("testKey", "testValue") let receiver: mobLink.MobIDListener = { onResult: (mobid: string) => { console.log("mobId:" + mobid) }, onError: (e: Error) => { console.log("onError:" + e.message) } } mobLink.getMobID(scene, receiver) 

## **增加全局场景还原监听器** 

#### 建议在AbilityStage中设置 

export function setRestoreSceneListener(receiver: RestoreSceneListener) //示例代码: let receiver: mobLink.RestoreSceneListener = { 

```arkts
completeRestore: (scene: mobLink.Scene) => { //在"拉起"处理场景的ability之后调用 //处理跳转 if (scene) { console.log("scene path:" + scene.path) let action = scene.path if (action == "xxx") { //逻辑处理 } } }, notFoundScene: (scene: mobLink.Scene) => { //未找到处理scene的ability时回调 } } mobLink.setRestoreSceneListener(receiver) 
```

## **处理onNewWant生命周期** 

防止MobLink在某些情景下无法还原,您需要在Ability.onNewIntent里调用此函数 

export function updateNewWant(want: Want) 

//示例代码 

export default class EntryAbility extends UIAbility { 

```arkts
.... onNewWant(want: Want, launchParam: AbilityConstant.LaunchParam): void { console.log("EntryAbility onNewWant") mobLink.updateNewWant(want) } } 
```

## **获取场景还原内容** 

可在ability的onCreate,onNewWant中获取后自行处理还原 

export function getSceneFromWant(want: Want): Promise<Scene | undefined> //示例代码: mobLink.getSceneFromWant(want).then((scene) => { if (scene) { console.log("scene path:" + scene.path) //逻辑处理 ... } else { console.log("scene undefined") } })
