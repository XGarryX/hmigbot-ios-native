---
name: arkts-codebase-config
description: '专门用于回答ArkTS语言的Harmony应用代码仓中功能配置/权限/开关类问题的技能。专注于回答配置项的定义位置、读取位置、默认值及覆盖路径等问题。例如："这个能力受哪个flag控制？"、"如何开启这个功能？"、"这个权限在哪里配置？"。当问题涉及模块配置（module.json5）、应用配置（app.json5）、权限配置、FeatureFlag、常量配置、资源配置、系统功能开关，或全局状态相关配置（V1: AppStorage / @StorageLink / @StorageProp / PersistentStorage；V2: AppStorageV2 / PersistenceV2）时使用此技能。本技能同时识别 ArkTS V1（@Component / @State / @Prop 等）与 V2（@ComponentV2 / @Local / @Param 等）装饰器代码。'
metadata:
  type: codebase
  domain: general
---
# HarmonyOS配置问答

本技能专注于回答ArkTS语言的Harmony应用代码仓中功能配置、权限、开关类问题。

## 问题类型识别

HarmonyOS开发者常见功能配置类问题包括以下类型：

### 1. 功能开关/Flag类问题
- "这个能力受哪个flag控制？"
- "如何开启/关闭某个功能？"
- "这个功能的开关在哪里？"
- "FeatureFlag的定义位置在哪里？"
- "某个功能默认是开启还是关闭？"

### 2. 权限配置类问题
- "这个权限在哪里声明？"
- "如何申请某个系统权限？"
- "权限的默认值是什么？"
- "为什么某个权限申请失败？"
- "权限的请求配置在哪个文件？"

### 3. 模块配置类问题（module.json5）
- "模块配置中某个字段的作用是什么？"
- "某个模块能力如何配置？"
- "模块的入口在哪里配置？"
- "模块依赖关系如何配置？"
- "某个页面或Ability在哪个模块中？"

### 4. 应用配置类问题（app.json5）
- "应用的全局配置在哪里？"
- "如何配置应用的bundle名称、版本号？"
- "应用的能力（capabilities）如何配置？"
- "应用图标和主题在哪里配置？"

### 5. 常量配置类问题
- "某个常量在哪里定义？"
- "这个默认值来自哪里？"
- "如何修改某个配置项的默认值？"
- "配置项的读取逻辑在哪里？"

### 6. 构建配置类问题（build-profile.json5）
- "不同环境的配置差异在哪里？"
- "如何配置多包构建？"
- "某个构建选项的作用是什么？"

### 7. 资源配置类问题
- "某个资源文件在哪里？"
- "如何配置多语言资源？"
- "主题色、样式在哪里定义？"

### 8. 系统能力配置类问题
- "某个系统API是否可用？"
- "如何配置使用受限的系统能力？"
- "设备的兼容性配置在哪里？"

### 9. 自定义配置类问题
- "项目中的自定义配置在哪里？"
- "如何添加新的配置项？"
- "配置项的读取路径是什么？"

## 工作流程

回答HarmonyOS配置类问题遵循以下步骤：

### 步骤1：识别问题类型

首先识别用户问题的类型（见上文"问题类型识别"），判断属于哪一类配置问题。根据问题类型确定：
- 需要查找的配置文件类型（module.json5、app.json5、build-profile.json5、常量文件等）
- 需要关注的配置项特征（flag名称、权限名称、模块名称等）
- 问题涉及的功能领域（UI、网络、存储、权限、系统能力等）

### 步骤2：利用Locator信息

使用locator传递的定位信息，了解问题的总体定位位置：
- 定位模块：问题涉及的应用模块（entry、feature、har、hsp等）
- 核心文件：关键配置文件路径
- 关键入口点：功能的主要代码入口
- 相关文件：可能与配置相关的其他文件

### 步骤3：判断文件重要性并读取代码

根据问题类型和locator信息，判断文件的重要性，进入对应的DAG组合读取代码：

**DAG组合策略**：

- **功能开关/Flag问题**：
  1. 读取常量配置文件（如Constants.ets、Config.ets）
  2. 搜索FeatureFlag相关代码
  3. 读取功能入口文件的开关判断逻辑
  4. 查看配置覆盖路径（如用户设置、本地存储）

- **权限配置问题**：
  1. 读取module.json5中的requestPermissions配置
  2. 查找权限请求的代码逻辑
  3. 检查权限回调处理
  4. 查看权限使用场景

- **模块配置问题**：
  1. 读取对应模块的module.json5
  2. 查看Ability、ExtensionAbility配置
  3. 检查pages和skills配置
  4. 查看deviceType和apiLevel配置

- **应用配置问题**：
  1. 读取app.json5
  2. 查看bundle信息、version信息
  3. 检查appSignature配置
  4. 查看requestPermissions全局配置

- **常量配置问题**：
  1. 搜索常量定义（grep "const.*=.*{关键词}"）
  2. 读取配置读取逻辑
  3. 查找配置的默认值定义
  4. 检查配置的赋值和修改点

- **构建配置问题**：
  1. 读取build-profile.json5
  2. 查看不同产品的配置差异
  3. 检查多包配置
  4. 查看编译选项

使用Read工具按重要性顺序读取文件：
1. 先读取核心配置文件（module.json5、app.json5等）
2. 再读取相关常量文件
3. 最后读取功能实现代码

### 步骤4：判断配置方法和建议位置

根据问题类型，判断功能配置的配置方法，给出建议位置：

**不同问题类型的配置位置建议**：

- **功能开关**：
  - 通常定义在：常量文件（Constants.ets、FeatureFlag.ets）
  - 可能覆盖位置：Preferences、用户设置页面、云端配置
  - 建议读取顺序：常量定义 → 使用位置 → 配置读取逻辑

- **权限配置**：
  - 声明位置：module.json5的requestPermissions字段
  - 请求位置：Ability的onStart、Page的aboutToAppear
  - 检查位置：权限回调处理、权限检查工具类
  - 建议读取顺序：module.json5 → 权限请求代码 → 权限使用代码

- **模块配置**：
  - 主要位置：对应模块的module.json5
  - Ability配置：name、exported、type等字段
  - 页面配置：pages数组、window配置
  - 建议读取顺序：module.json5 → Ability实现代码 → 页面路由配置

- **应用配置**：
  - 主要位置：app.json5
  - 版本管理：versionCode、versionName
  - 能力声明：abilities、extensionAbilities
  - 建议读取顺序：app.json5 → 入口模块module.json5

- **常量配置**：
  - 定义位置：ets文件中的常量声明
  - 读取位置：通过getContext().resourceManager或Preferences读取
  - 默认值：常量声明时的初始化值
  - 建议读取顺序：常量定义 → 常量使用 → 资源文件

**回退机制**：
- 当在预计位置找不到配置时，回退到上一步骤重新判断
- 使用grep搜索关键词（如flag名称、权限名称、配置项名称）
- 搜索相关的配置文件（*.json5、*.ets）
- 如果重试三次仍无法定位，尝试使用repomap自行定位
- 通过repomap了解模块说明和重要组件，重新分析问题

### 步骤5：按模板回答

使用以下模板结构回答问题：

```
## 功能配置分析

### 配置定义位置
- **文件路径**：[文件路径:行号]
- **配置项**：[具体配置名称]
- **定义内容**：[代码片段]

### 配置读取逻辑
- **读取位置**：[文件路径:行号]
- **读取方式**：[代码片段或说明]

### 默认值/覆盖路径
- **默认值**：[值]
- **覆盖位置**：[文件路径:行号]
- **覆盖逻辑**：[说明]

### 功能入口
- **入口文件**：[文件路径]
- **入口函数**：[函数名]
- **关键流程**：[流程说明]

### 关键代码
[核心代码片段]

### 修改建议
[如果需要修改，给出建议位置和方法]

```

### 步骤6：忠于事实

**重要原则**：
1. 所有回答必须基于真实代码仓内容
2. 记录分析、探索过程和核心发现
3. 当信息不足时，明确承认未知
4. 不要对缺失的细节进行假设
5. 禁止臆断或猜测

**信息不足处理**：
- 明确说明哪些信息无法在代码仓中找到
- 列出已查找的位置和方法
- 询问用户提供更多信息或上下文
- 提供可能的查找方向或建议

**探索过程记录**：
- 记录已读取的文件列表
- 记录已搜索的关键词
- 记录发现的线索和推理过程
- 记录尝试但失败的查找路径

### 步骤7：工具使用限制

**严格限制**：
1. 禁止使用edit工具修改代码
2. 仅限于问答场景
3. 只能提供分析和建议
4. 不能直接修改配置文件或代码

## 常见配置文件位置

### module.json5
- 位置：每个模块的根目录（如entry/src/main/module.json5）
- 作用：模块级配置，包括Ability、页面、权限声明等
- 关键字段：
  - module.name：模块名称
  - module.type：模块类型（entry、feature、har、hsp）
  - abilities：Ability配置列表
  - requestPermissions：权限请求列表
  - pages：页面路由配置

### app.json5
- 位置：AppScope/app.json5
- 作用：应用级全局配置
- 关键字段：
  - bundleName：应用包名
  - versionCode/versionName：版本信息
  - abilities：所有模块的Ability汇总
  - apiReleaseType：API版本类型

### build-profile.json5
- 位置：项目根目录和每个模块目录
- 作用：构建配置
- 关键字段：
  - buildMode：构建模式
  - targets：多包构建配置
  - products：产品级配置

### 常量文件
- 常见位置：
  - src/main/ets/common/Constants.ets
  - src/main/ets/config/Config.ets
  - src/main/ets/utils/Constants.ets
- 命名习惯：Constants、Config、FeatureFlag、Setting等

### 资源文件
- 位置：src/main/resources/base/element/
- 文件类型：
  - string.json：字符串资源
  - color.json：颜色资源
  - float.json：尺寸资源

## 参考文件

详见references目录中的详细参考文档：
- [config-file-types.md](references/config-file-types.md) - 配置文件类型详解
- [permission-guide.md](references/permission-guide.md) - 权限配置指南
- [feature-flag-pattern.md](references/feature-flag-pattern.md) - 功能开关模式
- [common-config-locations.md](references/common-config-locations.md) - 常见配置位置索引

根据问题类型，在需要时加载对应的参考文件以获取更详细的信息。
