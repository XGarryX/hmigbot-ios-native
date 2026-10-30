# HarmonyOS 离线翻译 SDK 使用指南

# 目录

环境要求

1.

安装与集成

2.

快速开始

3.

完整示例

4.

进阶用法

5.

最佳实践

6.

常见问题

7.

# 环境要求

| 项目 | 要求 |
|---|---|
| 操作系统 | HarmonyOS NEXT / HarmonyOS 4.0+ |
| API Level | API 12+ |
| DevEco Studio | 4.1+ |
| CPU 架构 | arm64-v8a |

# 安装与集成

## 步骤 1:添加依赖

在应用工程的 oh-package.json5 文件中添加 SDK 依赖:

```
{
  "dependencies": {
    "@youdaocloud/nmt": "^1.0.0"
  }
}
```

## 步骤 2:安装依赖

在项目根目录执行以下命令安装依赖:

```
ohpm install
1
```

## 步骤 3:配置模型文件

SDK 需要翻译模型文件才能正常工作。模型文件包含以下目录结构:

```
model/
├── patch/
│   └── patch.bin           # 主补丁文件(加密二进制格式)
├── transformer_c2e/        # 中译英模型
│   ├── model.bin           # 模型权重
│   └── model.dat           # 模型配置/词典
├── transformer_e2c/        # 英译中模型
│   ├── model.bin
│   └── model.dat
├── transformer_c2j/        # 中译日模型(可选)
│   ├── model.bin
│   └── model.dat
├── transformer_j2c/        # 日译中模型(可选)
│   ├── model.bin
│   └── model.dat
├── transformer_c2k/        # 中译韩模型(可选)
│   ├── model.bin
│   └── model.dat
└── transformer_k2c/        # 韩译中模型(可选)
    ├── model.bin
    └── model.dat
```

部署说明:

将模型文件放入应用的 src/main/resources/rawfile/model/ 目录下

transformer_e2c 和 transformer_c2e 为必需模型(NMT.initModel 默认只初始化这两个方向)

其他语言方向模型为可选,按需部署以减小安装包体积

# 快速开始

以下是一个简单的翻译示例:

```
import { NMT, AssetsHelper } from '@youdaocloud/nmt';
import common from '@ohos.app.ability.common';
// 获取应用上下文
const context = getContext(this) as common.UIAbilityContext;
async function initAndTranslate() {
    // 1. 复制模型文件到应用目录
    const assetsHelper = new AssetsHelper(context);
    const modelDir = context.cacheDir + '/model';
    await assetsHelper.copyAssetsFolderToCacheAsync(
        'model',
        modelDir,
        (percentage) => {
            console.log(`模型部署进度: ${percentage}%`);
        }
    );
    // 2. 加载 Native 库
    const loadSuccess = NMT.loadLibrary(context);
    if (!loadSuccess) {
        console.error('加载 Native 库失败');
        return;
    }
    // 3. 初始化模型
    const initResult = NMT.initModel(modelDir, 2);
    if (initResult !== 0) {
        console.error('初始化模型失败,错误码:', initResult);
        return;
    }
    // 4. 执行翻译
    const result = NMT.translate('Hello world', 'e2c');
    console.log('翻译结果:', result); // 输出: '你好世界'
    // 5. 应用退出时释放资源(建议在 Ability 的 onDestroy 中调用)
    // NMT.release();
}
```

# 完整示例

## 示例 1:基本翻译流程

```
import { NMT, AssetsHelper } from '@youdaocloud/nmt';
import common from '@ohos.app.ability.common';
@Entry
@Component
struct TranslatePage {
    @State inputText: string = '';
    @State outputText: string = '';
    @State isLoading: boolean = false;
    @State isReady: boolean = false;
    private context: common.UIAbilityContext | null = null;
    private modelDir: string = '';
    aboutToAppear() {
        this.context = getContext(this) as common.UIAbilityContext;
        if (this.context) {
            this.modelDir = this.context.cacheDir + '/model';
            this.initSDK();
        }
    }
    async initSDK() {
        this.isLoading = true;
        try {
            // 部署模型文件
            const assetsHelper = new AssetsHelper(this.context!);
            await assetsHelper.copyAssetsFolderToCacheAsync(
                'model',
                this.modelDir,
                (percentage) => {
                    console.log(`部署进度: ${percentage}%`);
                }
            );
            // 加载库并初始化模型
            NMT.loadLibrary(this.context!);
            const result = NMT.initModel(this.modelDir, 1);
            if (result === 0) {
                this.isReady = true;
                console.log('SDK 初始化成功');
            } else {
                console.error('模型初始化失败:', result);
            }
        } catch (error) {
            console.error('初始化失败:', error);
        } finally {
            this.isLoading = false;
        }
    }
    onTranslate() {
        if (!this.isReady || !this.inputText.trim()) return;
        this.outputText = NMT.translate(this.inputText, 'e2c');
    }
    build() {
        Column() {
            Text('离线翻译')
                .fontSize(24)
                .fontWeight(FontWeight.Bold)
                .margin({ top: 30 })
            TextInput({ placeholder: '请输入要翻译的文本' })
                .width('90%')
                .height(80)
                .margin({ top: 30 })
                .onChange((value: string) => {
                    this.inputText = value;
                })
            Button('翻译')
                .width('200dp')
                .height('50dp')
                .margin({ top: 20 })
                .enabled(this.isReady && !this.isLoading)
                .onClick(() => {
                    this.onTranslate();
                })
            Text(this.outputText)
                .width('90%')
                .margin({ top: 30 })
                .fontColor('#1890ff')
        }
        .width('100%')
        .height('100%')
        .justifyContent(FlexAlign.Start)
    }
}
```

## 示例 2:多语言方向切换

```
import { NMT } from '@youdaocloud/nmt';
// 语言方向映射
const languageDirections = [
    { code: 'e2c', label: '英语 → 中文' },
    { code: 'c2e', label: '中文 → 英语' },
    { code: 'c2j', label: '中文 → 日语' },
    { code: 'j2c', label: '日语 → 中文' },
    { code: 'c2k', label: '中文 → 韩语' },
    { code: 'k2c', label: '韩语 → 中文' }
];
// 执行翻译
function translateWithDirection(text: string, direction: string): string {
    if (!NMT.isInitialized) {
        console.error('模型未初始化');
        return '';
    }
    return NMT.translate(text, direction);
}
```

# 进阶用法

## 1. 自定义补丁(词典)

自定义补丁用于强制指定某些词汇的翻译结果,适用于专业术语、品牌名称等场景。采用双补丁模

式,自定义补丁作为主补丁的补充,优先匹配自定义补丁。

注意:自定义补丁文件必须为二进制格式(.bin),非文本格式。二进制补丁文件由有道云翻译平台生

成,客户可以通过平台管理自定义翻译条目并导出补丁文件。

```
import { NMT } from '@youdaocloud/nmt';
import fs from '@ohos.file.fs';
import common from '@ohos.app.ability.common';
async function loadCustomPatch(context: common.UIAbilityContext) {
    // 自定义补丁文件路径(从服务器下载或从rawfile复制)
    const patchPath = context.cacheDir + '/custom_patch.bin';
    // 加载自定义补丁
    const result = NMT.updateCustomDict(patchPath);
    if (result === 0) {
        console.log('自定义补丁加载成功');
    } else {
        console.error('自定义补丁加载失败');
    }
}
```

双补丁模式说明:

句子替换规则:只要命中一个补丁,就立即返回相应条目的结果

优先级:优先查看自定义补丁,未命中则查看主补丁

敏感词过滤:两个补丁里的敏感词都会进行过滤检查

## 2. 补丁更新

补丁文件用于修复翻译错误或优化翻译效果,无需重新发布应用即可更新。

```
import { NMT } from '@youdaocloud/nmt';
async function updateTranslationPatch(patchFilePath: string) {
    // 从服务器下载补丁文件后调用
    const result = NMT.updatePatch(patchFilePath);
    if (result === 0) {
        console.log('补丁更新成功');
    } else {
        console.error('补丁更新失败');
    }
}
```

## 3. 多线程优化

根据设备性能调整推理线程数:

```
import { NMT } from '@youdaocloud/nmt';
// 获取设备 CPU 核心数
function getCpuCount(): number {
    // 简化实现,实际应根据设备能力获取
    return 4;
}
// 根据设备性能设置线程数
const cpuCount = getCpuCount();
const threadNum = Math.min(cpuCount, 4); // 最多使用4线程
// 初始化模型时传入线程数
NMT.initModel(modelDir, threadNum);
```

# 最佳实践

## 1. 模型预加载

建议在应用启动时预加载模型,避免用户首次使用时等待:

```
// 在 EntryAbility 的 onCreate 中预加载
onCreate(want: Want, launchParam: AbilityConstant.LaunchParam) {
    this.preloadModel();
}
async preloadModel() {
    const context = this.context;
    const modelDir = context.cacheDir + '/model';
    try {
        // 部署模型
        const assetsHelper = new AssetsHelper(context);
        await assetsHelper.copyAssetsFolderToCacheAsync('model', modelDir, ()
=> {});
        // 加载库并初始化
        NMT.loadLibrary(context);
        NMT.initModel(modelDir, 2);
        console.log('模型预加载完成');
    } catch (error) {
        console.error('模型预加载失败:', error);
    }
}
23
```

## 2. 错误处理

完善的错误处理能提升用户体验:

```
function safeTranslate(text: string, direction: string): string {
    try {
        if (!NMT.isLoaded) {
            throw new Error('Native 库未加载');
        }
        if (!NMT.isInitialized) {
            throw new Error('模型未初始化');
        }
        if (!text || !text.trim()) {
            return '';
        }
        const result = NMT.translate(text, direction);
        if (!result) {
            throw new Error('翻译失败');
        }
        return result;
    } catch (error) {
        console.error('翻译错误:', error);
        return '翻译失败,请稍后重试';
    }
}
```

## 3. 资源释放

在应用退出或不再需要翻译时释放资源:

```
// 在 Ability 的 onDestroy 中调用
1
onDestroy() {
    NMT.release();
    console.log('翻译资源已释放');
}
```

## 4. 日志调试

SDK 内置了详细的日志,便于调试:

```
// 日志格式: youdaonmt: [message]
1
// 可以通过日志级别过滤
console.log('youdaonmt: 翻译完成');
console.error('youdaonmt: 翻译失败');
```

# 常见问题

## Q1:模型文件太大,安装包体积过大怎么办?

解决方案:

只打包常用的语言方向模型(如中英)

使用延迟下载策略,用户使用时再下载其他语言模型

利用应用市场的差分更新能力

## Q2:翻译速度慢怎么办?

解决方案:

增加线程数:NMT.initModel(modelDir, 4)

减少单次翻译文本长度

在后台线程执行翻译,避免阻塞 UI

## Q3:翻译结果不准确怎么办?

解决方案:

使用补丁更新功能优化翻译效果

加载自定义词典

确保使用最新版本的模型文件

## Q4:如何检查模型是否已初始化?

解决方案:

```
if (NMT.isInitialized) {
1
    // 模型已初始化,可以进行翻译
    const result = NMT.translate(text, 'e2c');
} else {
    // 模型未初始化,需要先初始化
}
```

## Q5:支持哪些语言方向?

回答:

e2c: 英语 → 中文

c2e: 中文 → 英语

c2j: 中文 → 日语

j2c: 日语 → 中文

c2k: 中文 → 韩语

k2c: 韩语 → 中文

注意:NMT.initModel() 默认只初始化 e2c 和 c2e 两个方向,其他方向需要额外处理。

## Q6:初始化失败,错误码为负数怎么办?

解决方案:

错误码 -1:通用错误,检查参数是否正确,查看日志

错误码 -2:Native 库未加载,先调用 NMT.loadLibrary(context)

错误码 -3:模型未初始化,先调用 NMT.initModel()

错误码 -4:模型文件不存在,检查模型路径,确保已复制模型文件

错误码 -5:语言方向不支持,使用支持的语言方向

检查模型目录结构是否正确

验证 model.bin 和 model.dat 文件是否存在且大小正常

## Q7:什么是双补丁模式?

回答:双补丁模式允许客户在使用默认主补丁的基础上,添加自定义补丁文件:

主补丁:由有道官方发布的二进制补丁文件(patch.bin)

自定义补丁:客户自行维护的二进制补丁文件

优先级:自定义补丁优先于主补丁

敏感词过滤:两个补丁都会进行敏感词检查

## Q8:自定义补丁文件格式是什么?

回答:自定义补丁文件必须为二进制格式(.bin),由有道云翻译平台生成。客户无法直接编辑二进制

文件,需要通过平台管理自定义翻译条目并导出补丁文件。

文档版本: v1.0.0

最后更新: 2026-06-11
