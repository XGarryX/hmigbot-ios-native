# 有道离线翻译SDK

- 市场详情页: https://developer.huawei.com/consumer/cn/market/prod-detail/56f484154e36476781f0bdabb053f1b4/PLATFORM
- 分类: 人工智能 > 文字识别
- 版本: 1.0.1(市场快照)
- ohpm 包名: @youdaocloud/nmt
- 语言: ArkTs
- 提供商: 网易有道信息技术(北京)有限公司()
- 市场更新时间: 2026-06-26 02:34:00
- 简介: 基于 Transformer 深度学习架构的端侧神经机器翻译 SDK,以 HAR 包形式提供给 HarmonyOS 应用集成。通过 NAPI 桥接高性能 C++ 推理引擎,支持中英日韩 6 个语言方向的全离线翻译。

### SDK介绍

有道离线翻译 SDK(harmony_offline_nmt),是一款基于 Transformer 深度学习架构的端侧神经机器翻译组件,以 HAR 静态共享包形式提供给 HarmonyOS 应用集成。SDK 通过 NAPI 桥接高性能 C++ 推理引擎 libmini-nmt.so,在设备本地完成全部翻译推理,零网络依赖、零数据上传,支持中⇄英、中⇄日、中⇄韩三对语言共 6 个方向的高质量离线翻译,并提供模型部署管理、补丁热更新、自定义词典扩展等进阶能力,满足对数据隐私安全、无网络场景、低延迟交互有严格要求的应用场景。

核心能力:

离线翻译:中英日韩 6 方向全离线翻译,无需联网

Transformer 模型:基于深度学习的端到端神经翻译引擎

模型管理:自动从 rawfile 部署模型到应用目录,支持增量更新

补丁热更新:通过 patch.bin 动态修正翻译效果

自定义词典:支持行业术语/企业术语强制翻译

Promise 风格 API:模型部署异步化,翻译同步调用

### 提供商介绍

提供商是一家在自然语言处理(NLP)与机器翻译领域具备深厚积累的技术服务公司,是端侧轻量 NMT(神经机器翻译)技术的开拓者与实践者,致力于将复杂的 AI 模型通过模型压缩、量化、知识蒸馏等技术手段部署到移动端、嵌入式设备等资源受限环境,帮助客户实现跨语言沟通与全球化业务。 核心团队在 Transformer 模型优化、多语言平行语料训练、端侧推理引擎(C++/NAPI)等方向拥有从训练到部署的完整工程能力,服务客户覆盖跨境电商、海外商旅工具、跨国制造业、政务办公、在线教育等多个行业。团队总部设在中文技术核心区,并在多个城市拥有本地化技术支持与研发团队,可提供从 SDK 集成、模型定制、行业语料微调、到术语词典管理等全链路一对一技术服务。在端侧 AI 翻译领域积累了多项核心关键技术,包括 Transformer 轻量化推理、Beam Search 低耗时优化、模型补丁增量训练、自定义词典融合策略、以及数据安全与隐私保护等方向。

### 核心优势

**1\. 纯端侧推理,数据零上传(差异化核心能力)**

与市面主流云翻译 API 形成根本差异:本 SDK 全部翻译推理在设备本地由 C++ 引擎 libmini-nmt.so 完成,不向任何云端发送原文或译文数据。对于政务公文、法律合同、医疗病历、金融合同、企业内部文档等敏感文本翻译场景具备不可替代性。

**2\. Transformer 模型轻量化部署(技术能力)**

底层采用 Transformer 架构(对应 transformer_c2e、transformer_e2c、transformer_c2j、transformer_j2c、transformer_c2k、transformer_k2c 六套模型文件),通过模型量化/剪枝/蒸馏技术压缩至移动端可部署体量,在 arm64-v8a 架构下以有限 CPU 算力实现高质量翻译输出。

**3\. 补丁 + 自定义词典双轨扩展(差异化扩展机制)**

SDK 提供两套不重新打包即可提升翻译效果的机制:

补丁更新:NMT.updatePatch(patchPath) 动态加载 patch.bin,针对高频翻译错误、行业语料进行模型增量修正;

自定义词典:NMT.updateCustomDict(dictPath) 注入企业/行业术语词典,实现品牌名、专业术语的强制统一翻译,尤其适合 B 端行业翻译场景。

**4\. HarmonyOS 深度适配(兼容性与性能)**

SDK 以 HAR 静态共享包(@youdaocloud/nmt v1.0.0) 形式发行,使用 ArkTS + NAPI + C++ 三层架构,直接对接 HarmonyOS Stage 模型,而非通过 Android 兼容层运行,包体、启动速度、内存占用均优于混合方案;模型文件通过 HarmonyOS 的 rawfile 资源系统部署,由 ModelManager 与 AssetsHelper 负责异步复制到应用私有目录,支持进度回调,首句翻译前的部署过程对用户透明友好。

**5\. 极简集成与完善状态管理(易用性与稳定性)**

三步出结果:1 AssetsHelper.copyAssetsFolderToCacheAsync 部署模型 → 2 NMT.initModel(modelDir) 初始化引擎 → 3 NMT.translate(text, "e2c") 获取译文;

状态位防重入:NMT.isLoaded / NMT.isInitialized 布尔状态位防止重复初始化;

全链路 try-catch 防护:所有 NAPI 跨语言调用与文件操作均被异常保护,任何底层错误均以降级方式返回,不影响上层应用继续运行;

完善日志:关键路径统一输出 youdaonmt: 前缀日志,集成排障直观高效;

自带示例工程:项目内附带 entry(ArkTS 示例)与 nmt_cpp(C++ 调试版)两套演示工程,含主页模型加载流程与多语言翻译交互页,开发者可直接参考完成接入。

###
