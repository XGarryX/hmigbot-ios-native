鸿蒙 SDK 集成文档说明 

### 北京数字联盟网络科技有限公司 

# 目录 

|1集成准备.......................................................................................................................... 3|
|---|
|2集成步骤.......................................................................................................................... 3|
|1. 引入 HAR 包................................................................................................................................................. 3|
|2. 设备 ID............................................................................................................................................................. 3|
|3. 权限说明........................................................................................................................................................... 4|
|4. 设备 OAID...................................................................................................................................................... 5|
|3 API说明............................................................................................................................ 6|
|1. getInstance 函数.......................................................................................................................................... 6|
|2. getQueryID 函数.......................................................................................................................................... 6|
|3. setConfig 函数............................................................................................................................................... 6|
|4集成示例........................................................................................................................... 7|
|5其他说明.......................................................................................................................... 8|

© Copyright 2026.版权所有 北京数字联盟网络科技有限公司 

## 1 `集成准` **备** 

模块集成测试前,请确保已完成以下操作: 

1、开通账户,包括添加应用包名。 

- 2、获取 apiKey 。 

## 2 `集成步` **骤** 

### **1. 引入 HAR 包** 

将 hmcore.har 拷贝到项目工程对应目录下,然后在工程的oh-package.json5 或者需要引入的Hap 模块所对应的oh-package.json5 中设置三方包依赖。如下 示例: 

参考示例: 

`HAR` 包所在的目录 `Demoprogram/dependencies/hmcare.har` 工程的 `oh-package.json5` 中设置依赖 `"dependencies": { "hmcore": "file:../dependencies/hmcore_vxxx.har" }` 

### **2. 设备 ID** 

- 1) 在需要引入的ets 文件中初始化数盟模块; 

```
import {DUMain} from 'hmcore'
```

- 2) 获取上下文context,类型为UIAbilityContext; 

参考示例: 

- © Copyright 2026.版权所有 北京数字联盟网络科技有限公司 

`//` 获取当前 `UIAbilityContext` 类型的上下文 `let context: common.UIAbilityContext  = this.context` 

- 3) 先调用getInstance 获取数盟方法实例,该方法需要传入context。 

#### 参考示例: 

`//` 获取数盟方法实例 `let duMain = DUMain.getInstance(context);` 

4) 获取实例完成后,使用setConfig 方法配置参数;setConfig 支持配置私有化 域名url、备份恢复后的应用沙箱文件存储目录repath 和原Android 包名 package。 

#### 参考示例: 

```
duMain.setConfig("host", "");
duMain.setConfig("package", "com.example");
duMain.setConfig("apikey", "xxx");
```

- 5) 最后调用getQueryID 获取数盟ID 

#### 参考示例: 

`//` 获取 `ID duMain.getQueryID("messages" , (id:string)=>{ console.log("shumengID=>", id) });` 

### **3. 权限说明** 

权限列表: 

© Copyright 2026.版权所有 北京数字联盟网络科技有限公司 

|权`限名称`|权`限描述`|`授`权类`型`|
|---|---|---|
|ohos.permission.INTERNET|`允` 许 `使` `用` Internet`网`络|system_grant`(必`选`)`|
|ohos.permission.GET_BUNDLE_INFO|`允`许查询应`用的` `基本信息`|system_grant`(必`选`)`|
|ohos.permission.GET_WIFI_INFO|`允`许获`取`Wi-Fi `信息`|system_grant`(必`选`)`|
|ohos.permission.GET_NETWORK_INFO|`允`许应`用`获`取数` `据网`络`信息`|system_grant`(必`选`)`|
|ohos.permission.APP_TRACKING_CONSEN T|`允`许应`用`读`取` OAID|user_grant`(可`选`,建`议`)`|
|ohos.permission.DISTRIBUTED_DATASYNC|`多`设备协`同`权`限`|user_grant`(可`选`,建`议`)`|

以上权限在 module.json5 中添加,示例: 

`"requestPermissions":[ { "name" : "ohos.permission.GET_NETWORK_INFO", "usedScene": { "abilities": [ "index","entry" ], "when":"inuse" } },` ...... `]` 

### **4. 设备 OAID** 

获取设备oaid 请调用getOpenAnmsID 方法,调用该方法建议应用拥有读取开放 匿名设备标识符权限:ohos.permission.APP_TRACKING_CONSENT 。 

`//` 获取上下文 `context` 

© Copyright 2026.版权所有 北京数字联盟网络科技有限公司 

```
let context: common.UIAbilityContext = this.context;
```

`//` 获取实例 `let duMain = DUMain.getInstance(context);` 

## 3 API **说** `明` 

### **1. getInstance 函数** 

`/** *` 实例化数盟方法 `* @field {UIAbilityContext}   context` 当前上下文 `*/` 

```
function getInstance(context: common.UIAbilityContext);
```

### **2. getQueryID 函数** 

`/** *` 获取 `ID` 方法 `* @field {string}   customMessage` 自定义信息 `* @field {function(string)} callback` 回调方法 `*/` 

```
function getQueryID(customMessage: string, callback: Callback);
```

### **3. setConfig 函数** 

`/** *` 设置配置参数,传入键 `-` 值对,可以多次调用 `* @param key` 键 

© Copyright 2026.版权所有 北京数字联盟网络科技有限公司 

`* @param value` 值 `* @return void */` 

```
function setConfig(key: string, value: string);
```

#### 该方法支持自定义配置信息采集和服务地址等,具体参数说明如下: 

|key|value 示例|描述|
|---|---|---|
|package|com.example|原 Android 应用包名,用于数据关联,关联历史 数据。具体联系相关人员。|
|host|xxx.com|自定义域名,可用于业务转发等,具体联系相关 人员。|
|apiley|xxx|apikey|
|wifi|1|设置值为“1”时,是屏蔽 wifi 相关信息的采 集。如 bssid / ssid 等。值为 “0”时表示走 默认逻辑。|
|location|1|设置值为“1”时,是屏蔽位置相关信息的采集。 如 gps 经纬度、ip 信息等。值为 “0”时表示 走默认逻辑。|
|storage|1|设置值为“1”时,是屏蔽存储空间相关信息的采 集。值为 “0”时表示走默认逻辑。|

## 4 `集成示例` 

`import {DUMain} from 'hmcore' ..... //` 获取上下文 `context let context: common.UIAbilityContext = this.context; //` 获取实例 `let duMain = DUMain.getInstance(context); //` 配置参数,可根据实际情况决定是否调用 `duMain.setConfig("package"` , `"com.example"); //` 设置 `apikey duMain.setConfig("apikey"` , `"xxx"); //` 获取数盟 `ID` 

© Copyright 2026.版权所有 北京数字联盟网络科技有限公司 

```
duMain.getQueryID("message", (id:string) =>{
   console.log(id);
});
```

## 5 `其他` **说** `明` 

对 `于元服` 务 `的模` 块 `集成,需要配置 “元服` 务 `服` 务 `器域名”,模` 块 `内固定域名` 为 

“https://hmuni.telecome.cn” `,` 请 `按需求` 处 `理。具体可参考:` 

https://developer.huawei.com/consumer/cn/doc/atomic-guides-V5/agc-help-harmonyos-serv 

er-domain-V5 

© Copyright 2026.版权所有 北京数字联盟网络科技有限公司
