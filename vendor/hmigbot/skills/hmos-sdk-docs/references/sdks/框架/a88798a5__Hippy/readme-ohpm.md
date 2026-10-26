> 来源: ohpm 中央仓 README(T1 信源) | 包: `hippy` | ohpm 最新版: 3.3.7 | 抓取: 2026-07-16
> 注意: 版本可能比市场快照新,以此为准时核对 CHANGELOG

# Hippy Cross Platform Framework

[Homepage](https://framework.tds.qq.com)

## 💡 Introduction

Hippy is a cross-platform development framework, that aims to help developers write once, and run on multiple platforms(iOS, Android, ohos, Web, and so on). Hippy is quite friendly to Web developers, especially those who are familiar with React or Vue. With Hippy, developers can create the cross-platform app easily.

Hippy is now applied in [Tencent](http://www.tencent.com/) major apps such as Mobile QQ, Mobile QQ Browser, Tencent Video App, QQ Music App, and Tencent News, reaching hundreds of millions of ordinary users.

## 🔨 Getting started

### Preparing environment

Install latest DevEco Studio.

### Integrate hippy

#### 1. Integrate hippy.har

  ```shell
  ohpm i hippy@latest
  ```

#### 2. Initialization code

- Get libhippy.so and UIAbility context.

  ```TypeScript
  import libHippy from 'libhippy.so'
  AppStorage.setOrCreate("libHippy", libHippy)
  AppStorage.setOrCreate("abilityContext", this.context)
  AppStorage.setOrCreate("mainWindow", mainWindow)
  ```

- Create HippyEngine、init HippyEngine、and load js bundle.

  ```TypeScript
  this.hippyEngine = createHippyEngine(params)
  this.hippyEngine.initEngine()
  this.hippyEngine?.loadModule()
  ```

- Build HippyRoot component.

  ```TypeScript
  HippyRoot({
      hippyEngine: this.hippyEngine,
      rootViewWrapper: this.rootViewWrapper,
      onRenderException: (exception: HippyException) => {
        this.exception = `${exception.message}\n${exception.stack}`
      },
  })
  ```

#### 3. Release code

 ```TypeScript
  hippyEngine?.destroyModule(rootId, () => {
    hippyEngine?.destroyEngine();
  });
  ```

  > More details for [ohos SDK integration](https://github.com/Tencent/Hippy/blob/main/docs/development/native-integration.md).

## 📁 Documentation

To check out [hippy examples](https://github.com/Tencent/Hippy/tree/main/framework/examples/ohos-har-demo) and visit [framework.tds.qq.com](https://framework.tds.qq.com/).
