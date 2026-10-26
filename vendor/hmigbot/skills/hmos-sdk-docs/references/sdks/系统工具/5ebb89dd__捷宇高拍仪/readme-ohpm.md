> 来源: ohpm 中央仓 README(T1 信源) | 包: `@joyusing/doccamerasdk` | ohpm 最新版: 1.0.0 | 抓取: 2026-07-16
> 注意: 版本可能比市场快照新,以此为准时核对 CHANGELOG

# 捷宇高拍仪SDK

## 介绍

```

福建捷宇高拍仪sdk是基于鸿蒙操作系统专属研发的适配程序,深度契合鸿蒙系统生态.

聚焦高拍仪影像采集核心需求,为鸿蒙设备用户提供高效、稳定、便捷的影像采集解决方案,全面覆盖多领域使用场景,助力数字化办公升级。

```

## 功能说明

- 实时画面预览:实时呈现拍摄画面,画面显示真实精准,方便用户提前调整拍摄角度、摆放位置,确保采集内容精准无误,避免无效采集

- 单页高清拍照:支持高清成像技术,可清晰捕捉文档、证件、实物等各类采集对象的细节,还原真实色彩与纹理,满足专业高清存档需求;适配办公文档处理、影像采集存档、政务办公等多类场景,同时凭借稳定的驱动性能,确保拍照过程高效顺畅,助力提升办公效率

## 权限说明

接入sdk需要如下权限:

- ohos.permission.CAMERA:用于拍照和录制视频

- ohos.permission.MICROPHONE 用于拍照和录制视频

- ohos.permission.WRITE_IMAGEVIDEO  用于保存拍摄的照片和视频

## 集成方式

### 1.1 安装(OHPM)

从 **OHPM 三方库中心仓** 安装本包(在项目根目录或目标模块目录执行均可,以实际工程与 OHPM 文档为准):

```bash

ohpm install @joyusing/doccamerasdk

```

简写:

```bash

ohpm i @joyusing/doccamerasdk

```

安装完成后,宿主模块的 `oh-package.json5` 中会出现对应依赖;再在工程内执行 `ohpm install` 拉取依赖树。

### 1.2 本地依赖(源码 / 工程内路径)

在宿主模块的 `oh-package.json5` 中增加本地路径依赖(例子:与引用模块内 `entry` 一致时可使用 `file:`):

```json5

{

  "dependencies": {

    "@joyusing/doccamerasdk": "file:../doccamerasdk"

  }

}

```
