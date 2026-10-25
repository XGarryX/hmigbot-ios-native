> 来源: ohpm 中央仓 README(T1 信源) | 包: `captcha_lib` | ohpm 最新版: 2.0.7 | 抓取: 2026-07-16
> 注意: 版本可能比市场快照新,以此为准时核对 CHANGELOG

# Trusfort 智能验证码 Harmony SDK 集成指南

> 版本:2.0.7  
> 发布单位:北京芯盾时代科技有限公司  
> 最后更新时间:2026 年 3 月

---

## 📌 简介

Trusfort 智能验证码 Harmony SDK 提供了在 OpenHarmony 平台上集成多种类型验证码的能力,支持人机识别、风险控制及多端验证体验。适用于需要高安全性和良好用户体验的业务场景。

---

## 🚀 快速开始

### 前提条件

- 已从服务端获取以下参数:
    - `appid`:验证码业务 ID(由后管平台生成)
    - `server_url`:验证码服务端 API 地址
- 开发环境为 **OpenHarmony 5.0.0(API 12)及以上**

---

## 📦 SDK 集成步骤

### 1. 引入 SDK 包

将 SDK 文件 `xd_captcha_lib_2.0.7.har` 复制到项目根目录。

### 2. 安装命令

`ohpm i captcha_lib`

### 3. 配置依赖

在项目根目录或者使用的module中的 `oh-package.json5` 中添加在线依赖:

```json
{
  "dependencies": {
    "captcha_lib": "2.0.7"
  }
}
```

或者使用离线依赖,在使用的module中的`oh-package.json5`中添加如下依赖:

```json
{
  "dependencies": {
    "captcha_lib": "file:../xd_captcha_lib_2.0.7.har"
  }
}
```

### 4.导入模块

在代码中导入 SDK:

```
import { TrusfortCaptchaManager } from 'captcha_lib';
```

### 5.初始化与调用
初始化 SDK(必须首先调用)

```
TrusfortCaptchaManager.getInstance().init();
```

此操作会初始化运行环境并开始采集传感器数据(用于人机识别)。

### 6.显示验证码

```
let option: Record<string, number | boolean | string | Object | undefined> = {};
option["appid"] = "your_appid";
option["server_url"] = "https://your-server-url.com";

TrusfortCaptchaManager.getInstance().showCaptcha(this.getUIContext(), {
  captchaOption: option,
  onSuccess: (code, data) => {
    // 验证结果回调
    if (code === 1000) {
      console.log("验证成功,token:", data);
    }
  },
  loadingViewBuilder: () => {
    // 可选:自定义加载视图
  }
});
```

### 7.关闭验证码(建议在回调后调用)

```
TrusfortCaptchaManager.getInstance().closeCaptcha();
```
