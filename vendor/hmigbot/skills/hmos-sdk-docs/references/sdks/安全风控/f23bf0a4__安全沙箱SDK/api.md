安全沙箱 SDK 接口设计文档 

修改记录 版本 日期 更改原因 编写人 V6.4.0 2025-05-28 创建 李洋 

说明介绍 

# 能力: 

为集成 SDK 的鸿蒙应用提供安全加固能力,通过限制用户访问行为达 到安全操作要求,保护企业数据安全 

# 组成: 

SDK 模块以 HAR 静态库形式提供,全称为 SDPSandboxLibrary.har , 当前使用的鸿蒙 SDK 版本为 5.0.4 ( 16 ),已不再支持 32 位,仅支持 64 位的 arm 、 amd 架构 

# 文件列表: 

SDPSandboxLibrary.har : SDK 库 

开发语言: C/C++ 、 arkts 、 ts 

导出规范: HAR 

架构: arm ,仅支持 64 位 

运行环境:鸿蒙 

SDK : 5.0.4 ( 16 ),具体兼容版本范围待测试 

模型:仅支持 Stage 

集成流程 

# 创建工程 

打开 DevEco Studio ,菜单栏点击 “ 文件 -> 新建 -> 新建项目 ->Empty Ability” , SDK 建议用最新的 5.0.4 ( 16 ): 

SDK 文件拷贝 

拷贝 sdk 及其依赖库到 src 根目录,可基于实际情况调整: 

# SDK 导入流程 

添加依赖:修改 oh-package.json5 

导入库,在 arkts 代码文件如 Index.ets 中通过以下代码导入 sdk ,如 图: 

调用:在 EntryAbility 的 onWindowStageCreate 的 windowStage.loadContent 中调用以下接口即可 

企微版本: initThirdSdkWhenWSCreate 

标准版本:先后调用 SBXSDK_Init , SBXSDK_BindUser 即可 

离线模式:目前仅提供离线版本,离线策略位置如图,同时提供策略 文件 

初始化接口 

接口描述 

# 接口声明 

export function SBX_Init(serverAddr: string, udid: string, windowStage: window.WindowStage, context: common.UIAbilityContext) 

# 接口描述 

【同步】用于初始化参数 

调用时机 

应用启动后,访问业务前的任一时间调用即可 

输入参数 

# 参数名称 

类型 

描述 

可选 / 必选 

serverAddr string 管理平台地址 :https://ip:port 必选(离线版传空字符串) udid string 设备 ID 必选(离线版传空字符串) 

windowStage window.WindowStage 窗口管理器,为 UIAbility 提供可视化载体 必选 

context 

common.UIAbilityContext 

提供操作应用组件、获取应用组件的配置信息等能力 必选 返回值 返回值 

# 描述 

无 

# 示例: 

import { SBXSDK_Init, SBX_BindUser } from 'sdpsandboxlibrary' 

onWindowStageCreate(windowStage: window.WindowStage): void { 

// Main window is created, set main page for this ability 

hilog.info(DOMAIN, 'testTag', '%{public}s', 'Ability onWindowStageCreate'); 

windowStage.loadContent('pages/Index', (err) => { 

if (err.code) { 

hilog.error(DOMAIN, 'testTag', 'Failed to load the content. Cause: %{public}s', JSON.stringify(err)); 

return; 

} 

SBXSDK_Init("", "", windowStage, this.context) 

}); 

} 

绑定用户接口 

接口描述 

接口声明 

export async function SBX_BindUser(userCode: string, bundleName?: string): Promise<void>; 

接口描述 

【异步】用于到管理平台绑定用户设备、获取策略、开启安全监测以 及行为管控 

调用时机 

在初始化接口之后 

输入参数 

参数名称 

类型 

描述 

可选 / 必选 

userCode 

string 

用户标识 

必选 

BundleName 

String 

包名,当测试包名与发布包名不同时,通过指定包名确保用户绑定以 及策略获取接口调用正常 

可选 

返回值 

返回值 

描述 

Promise<void> 

成功: - ,失败: BusinessError 

# 示例: 

import { SBXSDK_Init, SBX_BindUser } from 'sdpsandboxlibrary' 

SBX_BindUser(this.userCode, this.bundleName).then(() => { hilog.info(DOMAIN, TAG, " 绑定用户成功 ") }).catch((err: BusinessError) => { hilog.error(DOMAIN, TAG, " 绑定用户失败 : %{public}s", err) })
