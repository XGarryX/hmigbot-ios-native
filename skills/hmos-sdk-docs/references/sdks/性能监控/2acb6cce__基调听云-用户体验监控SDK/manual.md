# **HarmonyOS NEXT 部署** 

## **环境需求** 

最低支持: API 12 Release 

## **安装SDK** 

进入工程根目录,执行以下命令 

```
ohpm install @tingyun/sdk-core
如果需要安装指定版本的SDK, 可手动指定版本( `<version>` 为具体的版本号) 
ohpm install @tingyun/sdk-core@<version>
```

## **确认项目适配字节码格式HAR包** 

SDK HAR包为字节码格式, 需要将工程级 `build-profile.json5` 中 `useNormalizedOHMUrl` 设置为true 

```
{
"app": {
"products": [
      {
"buildOption": {
"strictMode": {
"useNormalizedOHMUrl": true
          }
        }
      }
    ]
  }
}
```

## **权限配置** 

|**权限名称**|**用途**|**是否必须**|
|---|---|---|
|ohos.permission.INTERNET|SDK发送数据。不配置SDK无法启动|是|
|ohos.permission.GET_NETWORK_INFO|获取网络连接信息。配置后可以获取 网络类型和连接方式信息|否|
|ohos.permission.STORE_PERSISTENT_DATA|存储设备ID。配置后SDK可以更准确 的获取到设备ID|否|

## **初始化SDK** 

在entry类型模块AbilityStage的 `onCreate` 方法中初始化SDK 

```
import tingyun from '@tingyun/sdk-core'
export default class MyAbilityStage extends AbilityStage {
  onCreate(): void {
    tingyun.init({
      // redirect服务器地址, 在控制台设置页面获取
      redirectHost: '<Redirect服务器地址>',
      // appKey, 在控制台设置页面获取
      appKey: '<AppKey>',
      // 上下文
      context: this.context
    })
  }
}
```

## **可选设置** 

### **配置首次启动模块开关** 

默认情况下,SDK首次启动仅开启崩溃数据采集,其他功能模块需要与服务端交互后开启。 如需在首次启动时就启用其他功能模块,可以在 `tingyun.init` 时手动配置对应模块的开启状态。 示例: 

```
import tingyun from '@tingyun/sdk-core'
tingyun.init({
  // 其他配置...
  network: {
    // 打开网络请求采集
    enabled: true
  },
  ue: {
    // 打开用户体验数据采集,包括启动、页面、操作采集
    enabled: true
  },
  webview: {
    // 打开webview数据采集
    enabled: true
  }
})
```

更多配置选项请参考API文档中的"SDK配置选项"章节 

### **网络请求采集** 

SDK支持多种网络请求数据采集方式,其中Axios和RCP需要进行相应配置。 

#### **Axios** 

SDK支持 `@ohos/axios` 库,主要包括两种配置方式: 

1. 在 `tingyun.init` 时传入axios实例: 

```
import tingyun from '@tingyun/sdk-core'
import axios from '@ohos/axios'
tingyun.init({
  // 其他配置...
  // 传入axios实例对象
  axios: axios
})
```

2. 使用 `tingyun.registerAxiosInstance` 注册axios实例(可通过多次调用注册多个): 

```
import tingyun from '@tingyun/sdk-core'
import { axiosInstance } from './your-axios-config'
tingyun.registerAxiosInstance(axiosInstance)
```

#### **RCP** 

RCP数据采集需要在调用 `createSession` 时加入SDK提供的拦截器: 

```
import tingyun from '@tingyun/sdk-core'
const session = rcp.createSession({
  // 其他配置...
  // 加入拦截器
  interceptors: [new tingyun.RCPInterceptor()]
})
```

#### **首次启动采集配置** 

如需采集首次启动时的网络请求数据,需要在 `tingyun.init` 时开启网络请求采集: 

```
import tingyun from '@tingyun/sdk-core'
tingyun.init({
  // 其他配置...
  network: {
    enabled: true
  }
})
```

### **用户体验监控** 

用户体验监控包括启动监控、页面监控和操作监控。 

#### **启动监控配置** 

如需采集首次启动数据,需要在 `tingyun.init` 时开启用户体验监控: 

```
import tingyun from '@tingyun/sdk-core'
tingyun.init({
  // 其他配置...
  ue: {
    enabled: true
  }
})
```

#### **页面和操作监控配置** 

页面和操作监控需要使用 `tingyun.registerUIContext` API注册UIContext。 

##### 示例: 

```
import tingyun from '@tingyun/sdk-core'
export default class EntryAbility extends UIAbility {
  onWindowStageCreate(windowStage: window.WindowStage): void {
    windowStage.loadContent('pages/Index', (err, data) => {
      // 获取当前UIAbility的主窗口
      windowStage.getMainWindow((err: BusinessError, data) => {
        const uiContext = data.getUIContext()
        // 注册当前窗口的UIContext
        tingyun.registerUIContext(uiContext)
      })
    });
  }
}
```

### **设置用户ID** 

```
import tingyun from '@tingyun/sdk-core'
// 设置用户ID(<userId>为具体的用户ID)
tingyun.setUserId('<userId>')
```

### **Webview数据采集** 

##### Webview数据采集主要包括两个操作: 

1. 使用 `tingyun.registerWebviewController` 注册webview控制器 

2. 使用 `tingyun.getWebScriptItem` 获取监控脚本并注入到webview中 

示例: 

```
import tingyun from '@tingyun/sdk-core'
Web({ src: '<URL>', controller: this.controller })
  // 确保javaScriptAccess和domStorageAccess都是开启状态
  .javaScriptAccess(true)
  .domStorageAccess(true)
  .onControllerAttached(() => {
    // 在onControllerAttached回调中注册webview控制器
    tingyun.registerWebviewController(this.controller)
  })
  // 注入监控所需的JS代码
  .javaScriptOnDocumentStart([tingyun.getWebScriptItem()])
```

### **启用国密加密** 

SDK支持使用国密加密方式发送数据,可通过在 `tingyun.init` 时设置 `encEnabled: true` 配置开启, 平台服务端也需要同步开启国密加密功能。 

```
import tingyun from '@tingyun/sdk-core'
tingyun.init({
  // 其他配置...
  // 启用国密加密
  encEnabled: true
})
```

## **嵌码验证** 

嵌码完成后,启动APP,在IDE中打开Log -> HiLog菜单,选择对应的APP,查看日志,搜索tag为 `Tingyun` 的日志,如果存在 `init success` 关键字的日志说明嵌码成功
