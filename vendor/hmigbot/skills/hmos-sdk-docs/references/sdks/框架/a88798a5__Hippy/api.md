# **Hippy接口文档** 

## **1. 概述** 

Hippy 是 TDSF 腾讯端框架(Tencent Device-oriented Service Framework)下的开源跨平台 应用开发解决方案。Hippy 可以理解为一个精简版的浏览器,从底层做了大量工作,抹平了 Ohos、iOS、Android三端差异,提供了接近 Web 的开发体验,目前上层支持了 React 和 Vue 两套界面框架,前端开发人员可以通过它,将前端代码转换为终端的原生指令,进行原生 终端 App 的开发。同时,Hippy 从底层进行了大量优化,在启动速度、渲染性能、动画速 度、内存占用、包体积等方面都提供了业内顶尖的性能表现。 

- 项目地址:https://framework.tds.qq.com 安装: 

ohpm i hippy 

## **2. 核心类和接口** 

|**类/接口名**|**描述**|
|---|---|
|EngineInitParams|HippyEngine初始化参数|
|ModuleLoadParams|业务JS页面加载参数|
|HippyEngine|HippyEngine接口|
|EngineListener|HippyEngine初始化结果的Listener|
|ModuleListener|业务JS页面加载结果的Listener|
|HippyRoot|Hippy根组件|
|HippyAPIProvider|业务自定义组件和自定义Native模块的注册类|
|HippyCustomComponentView|业务自定义组件的基类|
|HippyNativeModuleBase|业务自定义Native模块的基类|

## **3. 常用函数说明** 

createHippyEngine 

- 功能:创建一个 HippyEngine 

- 参数:params - 初始化参数 

- 返回:一个 HippyEngine 

## **4. 常用方法说明** 

### **HippyEngine** 

initEngine 

- 功能:初始化 HippyEngine 参数:listener - 结果 listener 

loadModuleWithListener 

- 功能:加载 JS 页面 

- 参数:loadParams - 加载参数 

- 参数:listener - 结果 listener 

- 返回:一个 HippyRootView 或空 

destroyModule 

功能:销毁 JS 页面 

参数:rootId - 页面根节点 id 

- 参数:destroyCallback - 结果回调 

destroyEngine 

功能:销毁 HippyEngine 

### **EngineListener** 

onInitialized 

- 功能:初始化 HippyEngine 的结果监听 参数:statusCode - 结果码 

- 参数:msg - 结果描述 

### **ModuleListener** 

onLoadCompleted 

- 功能:加载 JS 页面的结果监听 参数:statusCode - 结果码 

- 参数:msg - 结果描述 

### **HippyAPIProvider** 

getCustomNativeModuleCreatorMap 

功能:向 Hippy 注册自定义的 Native 模块 返回:注册 map 

getCustomRenderViewCreatorMap 

功能:向 Hippy 注册自定义的组件 View 返回:注册 map 

### **HippyCustomComponentView** 

setProp 

功能:自定义组件的属性设置处理 参数:propKey - 属性 key 参数:propValue - 属性 value 

返回:true 表示处理了对应属性,false 表示没有处理 

call 

- 功能:自定义组件的方法调用处理 

参数:method - 方法名 参数:params - 方法参数 

### **HippyNativeModuleBase** 

call 

功能:自定义 Native 模块的方法调用处理 参数:method - 方法名 参数:params - 方法参数 参数:promise - 结果回调 

## **5. 代码示例** 

### **初始化 HippyEngine 并加载页面** 

this.hippyEngine = createHippyEngine(params) this.hippyEngine.initEngine() this.hippyEngine?.loadModule() 

### **组装 Hippy 根组件** 

HippyRoot({ hippyEngine: this.hippyEngine, rootViewWrapper: this.rootViewWrapper, onRenderException: (exception: HippyException) => { this.exception = `${exception.message}\n${exception.stack}` }, }) 

### **释放页面和 HippyEngine** 

hippyEngine?.destroyModule(rootId, () => { hippyEngine?.destroyEngine(); }); 

## **6. 注意事项** 

- 初始化时序:判断到 initEngine 成功后再 loadModule。 

- 销毁时序:判断到 destroyModule 回调后再 destroyEngine。 

- 有效销毁:判断到 loadModule 成功再 destroyModule,判断到 initEngine 成功再 destroyEngine。
