# **Hippy使用指南** 

## **1. 概述** 

Hippy 是 TDSF 腾讯端框架(Tencent Device-oriented Service Framework)下的开源跨平台 应用开发解决方案。Hippy 可以理解为一个精简版的浏览器,从底层做了大量工作,抹平了 Ohos、iOS、Android三端差异,提供了接近 Web 的开发体验,目前上层支持了 React 和 Vue 两套界面框架,前端开发人员可以通过它,将前端代码转换为终端的原生指令,进行原生 终端 App 的开发。同时,Hippy 从底层进行了大量优化,在启动速度、渲染性能、动画速 度、内存占用、包体积等方面都提供了业内顶尖的性能表现。 

项目地址:https://framework.tds.qq.com 

## **2. 开始使用** 

### **环境准备** 

安装最新 DevEco Studio。 

### **集成 Hippy SDK** 

#### **1. 集成 hippy.har** 

ohpm i hippy@latest 

#### **2. 初始化代码** 

加载 libhippy.so 和获取 UIAbility context 

import libHippy from 'libhippy.so' AppStorage.setOrCreate("libHippy", libHippy) AppStorage.setOrCreate("abilityContext", this.context) 

初始化 HippyEngine 并加载页面 

this.hippyEngine = createHippyEngine(params) this.hippyEngine.initEngine() this.hippyEngine?.loadModule() 

##### 组装 Hippy 根组件 

HippyRoot({ hippyEngine: this.hippyEngine, rootViewWrapper: this.rootViewWrapper, onRenderException: (exception: HippyException) => { this.exception = `${exception.message}\n${exception.stack}` }, }) 

#### **3. 销毁代码** 

##### 释放页面和 HippyEngine 

hippyEngine?.destroyModule(rootId, () => { hippyEngine?.destroyEngine(); }); 

更多细节参考 SDK 集成文档 和 Hippy Demo
