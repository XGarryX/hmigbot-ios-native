# **MobLink 接口文档** 

## **init** 

init(context: Context, appkey: string, secret: string):void 

初始化Zztsdk 

### **参数:** 

|**参数名**|**类型**|**必填**|**说明**|
|---|---|---|---|
|context|Context|是|上下文context|
|appkey|string|是|sdk的appkey|
|secret|string|是|sdk的secret|

### **返回值:** 

|**类型**|**说明**|
|---|---|
|void|无|

### **示例:** 

1 ZztSDK.init(getContext(this), 'your appkey', 'your secret') 

## **submitPolicyGrantResult** 

submitPolicyGrantResult(granted: boolean): void 

#### 提交隐私结果 

### **参数:** 

|**参数名**|**类型**|**必填**|**说明**|
|---|---|---|---|
|granted|boolean|是|true代表同意隐私, false代表不同意隐私|

### **返回值:** 

|**类型**|**说明**|
|---|---|
|void|无|

### **示例:** 

1 ZztSDK.submitPolicyGrantResult(true) 

## **init** 

export function init(context: Context): void 

初始化MobLink 

### **参数:** 

|**参数名**|**类型**|**必填**|**说明**|
|---|---|---|---|
|context|Context|是|上下文context|

### **返回值:** 

|**类型**|**说明**|
|---|---|
|void|无|

### **示例:** 

1 mobLink.init(this.context) 

## **getMobID** 

export function getMobID(scene: Scene, listener: MobIDListener) 

制作场景 

### **参数:** 

|**参数名**|**类型**|**必填**|**说明**|
|---|---|---|---|
|scene|Scene|是|场景信息内容|
|listener|MobIDListener|是|生成场景内容回调|

### **返回值:** 

|**类型**|**说明**|
|---|---|
|void|无|

### **示例:** 

1 let scene = new mobLink.Scene() 2 scene.path = "/demo/a" 3 scene.params.set("testKey", "testValue") 4 let receiver: mobLink.MobIDListener = { 5 onResult: (mobid: string) => { 6 console.log("mobId:" + mobid) 7 }, 8 onError: (e: Error) => { 9 console.log("onError:" + e.message) 10 } 11 } 12 mobLink.getMobID(scene, receiver) 

## **setRestoreSceneListener** 

export function setRestoreSceneListener(receiver: RestoreSceneListener) 

增加全局场景还原监听器 

### **参数:** 

|**参数名**|**类型**|**必填**|**说明**|
|---|---|---|---|
|receiver|RestoreSceneListener|是|场景还原监听器|

|**返回值:**||
|---|---|
|**类型**|**说明**|
|void|无|

### **示例:** 

1 let receiver: mobLink.RestoreSceneListener = { 2 completeRestore: (scene: mobLink.Scene) => { 3 //在"拉起"处理场景的ability之后调用 4 //处理跳转 5 if (scene) { 6 console.log("scene path:" + scene.path) 7 let action = scene.path 8 if (action == "xxx") { 9 //逻辑处理 10 } 11 } 12 }, 13 notFoundScene: (scene: mobLink.Scene) => { 

- 14 //未找到处理scene的ability时回调 

- 15 } 16 } 

- 17 mobLink.setRestoreSceneListener(receiver) 

## **updateNewWant** 

export function updateNewWant(want: Want) 

处理onNewWant生命周期(防止MobLink在某些情景下无法还原) 

### **参数:** 

|**参数名**|**类型**|**必填**|**说明**|
|---|---|---|---|
|want **返回值:**|Want|是|ability启动时的want参数|
|**类型**|||**说明**|
|void|||无|

### **示例:** 

- 1 export function updateNewWant(want: Want) 2 3 //示例代码 4 export default class EntryAbility extends UIAbility { 

- 5 .... 6 onNewWant(want: Want, launchParam: AbilityConstant.LaunchParam): void { 7 console.log("EntryAbility onNewWant") 8 mobLink.updateNewWant(want) 9 } 

- 10 } 

## **getSceneFromWant** 

export function getSceneFromWant(want: Want): Promise<Scene | undefined> 

获取场景还原内容 

### **参数:** 

|**参数名**|**类型**|**必填**|**说明**|
|---|---|---|---|
|want|Want|是|ability启动时的want参数|

### **返回值:** 

|**类型**|**说明**|
|---|---|
|Promise<Scene | undefined>|undefined是为未获取到场景还原内容,Scene为场景还原内容|

### **示例:** 

1 mobLink.getSceneFromWant(want).then((scene) => { 2 if (scene) { 3 console.log("scene path:" + scene.path) 4 //逻辑处理 5 ... 6 } else { 7 console.log("scene undefined") 8 } 9 }) 

##
