# HarmonyOS 离线翻译 SDK API 文档

# 目录

概述

1.

核心类接口

2.

NMT 类

ModelManager 类

AssetsHelper 类

Native 引擎接口

3.

语言方向常量

4.

错误码说明

5.

# 概述

harmony_offline_nmt是一款基于 Transformer 深度学习架构的端侧神经机器翻译 SDK,以 HAR 包

形式提供给 HarmonyOS 应用集成。SDK 通过 NAPI 桥接高性能 C++ 推理引擎,支持中英日韩 6 个

语言方向的全离线翻译。

核心特性:

纯端侧推理,零网络依赖

支持中⇄英、中⇄日、中⇄韩共 6 个语言方向(模型初始化默认启用中英双向)

模型补丁热更新

自定义词典扩展(双补丁模式:主补丁+自定义补丁)

HarmonyOS Stage 模型原生适配

授权验证支持(本地授权+远程授权 fallback)

# 核心类接口

## NMT 类

说明:翻译引擎核心类,封装了 Native 引擎的初始化、翻译、资源释放等核心能力。

导入方式:
```
import { NMT } from '@youdaocloud/nmt';
1
```

## 静态属性

| 属性名 | 类型 | 说明 |
|---|---|---|
| isLoaded | boolean | Native 库是否已加载 |
| isInitialized | boolean | 翻译模型是否已初始化 |

## 静态方法

loadLibrary

签名:static loadLibrary(context: common.UIAbilityContext): boolean

功能:加载 Native 库(libmini-nmt.so)。在 HarmonyOS 中,so 库会自动加载,此方法主要做状态标

记。

参数:

| 参数名 | 类型 | 必填 | 说明 |
|---|---|---|---|
| context | UIAbilityContext | 是 | 应用能力上下文 |

返回值:boolean - 是否加载成功

示例:
```
const context = getContext(this) as common.UIAbilityContext;
const success = NMT.loadLibrary(context);
```

initModel

签名:static initModel(modelPath: string, threadNum?: number): number

功能:初始化翻译模型。内部会依次尝试 e2c(英译中)和 c2e(中译英)两个语言方向,任一

成功即完成初始化。

参数:

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|
| modelPath | string | 是 | - | 模型文件所在目录 路径 |
| threadNum | number | 否 | 1 | 推理线程数(建议 值:1-4) |

返回值:number - 初始化结果码(0=成功,负数=失败)

说明:

模型路径下应包含:transformer_e2c/、transformer_c2e/ 目录及 patch/patch.bin 文件

初始化前会自动验证模型路径和关键文件是否存在

内部调用 nativeInit 时使用默认的 deviceId 和 appKey

示例:
```
const modelDir = context.cacheDir + '/model';
const result = NMT.initModel(modelDir, 2);
if (result === 0) {
    console.log('模型初始化成功');
}
```

translate

签名:static translate(sentence: string, direction: string): string

功能:执行文本翻译

参数:

| 参数名 | 类型 | 必填 | 说明 |
|---|---|---|---|
| sentence | string | 是 | 待翻译的源语言文本 |
| direction | string | 是 | 翻译方向(如 "e2c"、"c2e") |

返回值:string - 翻译结果(失败时返回空字符串)

示例:
```
const result = NMT.translate('Hello world', 'e2c');
console.log('翻译结果:', result); // 输出: '你好世界'
```

updatePatch

签名:static updatePatch(patchPath: string): number

功能:更新补丁文件,优化翻译效果

参数:

| 参数名 | 类型 | 必填 | 说明 |
|---|---|---|---|
| patchPath | string | 是 | 补丁文件(patch.bin) 路径 |

返回值:number - 更新结果码(0=成功,-1=失败)

示例:
```
const result = NMT.updatePatch(context.cacheDir + '/patch.bin');
1
```

updateCustomDict

签名:static updateCustomDict(dictPath: string): number

功能:更新自定义词典,支持行业术语强制翻译。采用双补丁模式,自定义补丁作为主补丁的补充,

优先匹配自定义补丁。

参数:

| 参数名 | 类型 | 必填 | 说明 |
|---|---|---|---|
| dictPath | string | 是 | 自定义补丁文件路径 (二进制格式) |

返回值:number - 更新结果码(0=成功,-1=失败)

说明:

双补丁模式:优先查看自定义补丁,未命中则查看主补丁(通过 updatePatch 设置)

自定义补丁允许客户在不修改主补丁的情况下添加自定义翻译条目

文件格式为二进制格式(.bin),非文本格式

示例:
```
const result = NMT.updateCustomDict(context.cacheDir + '/custom_patch.bin');
1
```

release

签名:static release(): void

功能:释放翻译引擎资源

参数:无

返回值:无

示例:

// 在应用退出或不再需要翻译时调用

```
NMT.release();
```

## ModelManager 类

说明:模型文件管理类,负责模型文件的检测、复制和路径管理。

导入方式:
```
import { ModelManager } from '@youdaocloud/nmt';
1
```

## 构造方法

签名:constructor(context: common.UIAbilityContext)

参数:

| 参数名 | 类型 | 必填 | 说明 |
|---|---|---|---|
| context | UIAbilityContext | 是 | 应用能力上下文 |

示例:
```
const modelManager = new ModelManager(context);
1
```

## 实例方法

checkAndCopyModelFiles

签名:async checkAndCopyModelFiles(modelFiles: string[]): Promise<boolean>

功能:检查模型文件是否存在,不存在则从 rawfile 复制

参数:

| 参数名 | 类型 | 必填 | 说明 |
|---|---|---|---|
| modelFiles | string[] | 是 | 需要检查的模型文件路 径列表(相对路径) |

返回值:Promise<boolean> - 是否全部文件都存在

示例:
```
const files = [
    'transformer_c2e/model.bin',
    'transformer_e2c/model.bin',
    'patch/patch.bin'
];
const success = await modelManager.checkAndCopyModelFiles(files);
```

getModelBaseDir

签名:getModelBaseDir(): string

功能:获取模型文件存储基础目录

返回值:string - 模型目录路径

示例:
```
const modelDir = modelManager.getModelBaseDir();
1
```

listModelFiles

签名:listModelFiles(): string[]

功能:列出模型目录中的所有文件

返回值:string[] - 文件相对路径列表

示例:
```
const files = modelManager.listModelFiles();
1
```

## AssetsHelper 类

说明:资源文件辅助类,负责从 rawfile 异步复制模型文件到应用目录。

导入方式:
```
import { AssetsHelper } from '@youdaocloud/nmt';
1
```

## 构造方法

签名:constructor(context: common.UIAbilityContext)

参数:

| 参数名 | 类型 | 必填 | 说明 |
|---|---|---|---|
| context | UIAbilityContext | 是 | 应用能力上下文 |

示例:
```
const assetsHelper = new AssetsHelper(context);
1
```

## 实例方法

copyAssetsFolderToCacheAsync

签名:async copyAssetsFolderToCacheAsync(srcFolder: string, destFolder: string, callback:

|  | (percentage: number) => void): Promise<void> |
|---|---|

功能:异步复制 rawfile 资源到缓存目录

参数:

| 参数名 | 类型 | 必填 | 说明 |
|---|---|---|---|
| srcFolder | string | 是 | rawfile 中的源文件夹名 |
| destFolder | string | 是 | 目标缓存目录路径 |
| callback | (percentage: number) => void | 是 | 进度回调函数(0-100) |

| (percentage: number) |  |  |
|---|---|---|

|  | => void |
|---|---|

返回值:Promise<void>

示例:
```
await assetsHelper.copyAssetsFolderToCacheAsync(
    'model',
    context.cacheDir + '/model',
    (percentage) => {
        console.log(`复制进度: ${percentage}%`);
    }
);
```

# Native 引擎接口

说明:底层 C++ 引擎的 NAPI 接口定义,一般不直接调用。

接口定义:
```
interface MiniNmt {
    /**
```

     * 初始化翻译引擎

```
     * @param deviceId 设备ID
     * @param extraInfo 额外信息(用于获取packageName)
     * @param appKey 应用密钥
     * @param langs 语言方向(如"e2c"、"c2e")
     * @param modelBaseDir 模型文件基础目录
     * @param maxThreads 最大线程数
```

     * @returns 初始化结果(0表示成功,负数表示错误)

```
     */
    nativeInit(deviceId: string, extraInfo: string, appKey: string,
               langs: string, modelBaseDir: string, maxThreads: number):
number;
    /**
     * 执行翻译
     * @param srcSentence 源语句
     * @param lang 目标语言方向(如"e2c")
     * @return s 翻译结果
     */
    nativeTranslate(srcSentence: string, lang: string): string;
    /**
```

     * 清理翻译引擎资源

```
     */
    nativeRelease(): void;
    /**
```

     * 更新主补丁文件

```
     * @param path 补丁文件路径
     * @return s 更新结果(true表示成功)
     */
    nativeUpdatePatch(path: string): boolean;
    /**
```

     * 更新自定义补丁文件

```
     * @param path 自定义补丁文件路径
     * @return s 更新结果(true表示成功)
     */
    nativeUpdateCustomPatch(path: string): boolean;
    /**
```

     * 获取主补丁版本号

```
43
```

     * @returns 版本号(-1=未初始化,0=老版本,正数=新版本号)

```
     */
    nativeGetPatchVersion(): number;
    /**
```

     * 中断正在进行的翻译请求

```
49
```

     * 用于语音翻译场景中取消前序不完整的翻译请求

```
     */
    nativeInterrupt(): void;
}
```

# 语言方向常量

| 常量值 | 含义 | 说明 |
|---|---|---|
| 'e2c' | 英译中 | English to Chinese |
| 'c2e' | 中译英 | Chinese to English |
| 'c2j' | 中译日 | Chinese to Japanese |
| 'j2c' | 日译中 | Japanese to Chinese |
| 'c2k' | 中译韩 | Chinese to Korean |
| 'k2c' | 韩译中 | Korean to Chinese |

# 错误码说明

| 错误码 | 含义 | 解决方案 |
|---|---|---|
| 0 | 成功 | - |
| -1 | 通用错误 | 检查参数是否正确,查看日志 |
| -2 | Native 库未加载 | 先调用 loadLibrary |
| -3 | 模型未初始化 | 先调用 initModel |
| -4 | 模型文件不存在 | 检查模型路径,确保已复制模型 文件 |
| -5 | 语言方向不支持 | 使用支持的语言方向 |

# 接口调用流程

1. 初始化阶段

```
   └─ AssetsHelper.copyAssetsFolderToCacheAsync()  // 复制模型文件
       └─ NMT.loadLibrary()                        // 加载Native库
           └─ NMT.initModel()                      // 初始化模型
```

2. 翻译阶段

```
   └─ NMT.translate()                             // 执行翻译
3. 扩展阶段(可选)
   ├─ NMT.updatePatch()                           // 更新补丁
   └─ NMT.updateCustomDict()                      // 更新自定义词典
```

4. 清理阶段

```
   └─ NMT.release()                               // 释放资源
```

文档版本: v1.0.0

最后更新: 2026-06-11
