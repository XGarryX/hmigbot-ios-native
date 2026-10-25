---
name: ios-screenshot-analyzer
description: App 页面截图分析与命名 skill。当用户需要分析截图、识别页面功能/布局/视觉风格、提取页面内容、或为截图生成结构化文档（含页面名/布局/功能/视觉风格/交互字段的 markdown 报告）时触发。支持文件路径和 glob 模式输入，批量处理多张截图。适用于产品经理写页面规格、设计师整理界面文档、开发者理解他人 UI。不处理设计稿/Figma/Sketch 文件、动画识别或代码生成。
metadata:
  type: domain
  domain: migration
  tags:
  - migration
  - ios
  - screenshot
  - ui-analysis
---

> **iOS 源输入适配**：执行源分析/源设备操作前，读 [原生输入协议](../a2h-spec/references/native-input.md)。它仅替换平台输入；原阶段、模板、规则、门禁、模式和 target 侧执行保持 1.5.2。

# iOS Screenshot Analyzer

分析 App 页面截图，识别页面功能、布局、风格，并输出结构化文档。

---

## 自动识别 App 类型

**如果用户未告知 App 类型或用途**，在分析前先自动搜索：

1. 从截图文件名提取关键词（如 `wechat`、`gallery`、`shopping`）
2. 使用网络搜索工具搜索关键词 + `App` 确定 App 类型
3. 如果有多张截图，选择第一张或最有代表性的一张进行分析
4. 在分析报告中标注 `（App 类型为推测）`

```
用户：帮我分析 screenshots/app.png
Agent：
  1. 截图文件名无明显 App 线索
  2. 网络搜索 "screenshot app UI design 2024"
  3. 推测为某类 App
  4. 开始分析截图
```

---

## 输入格式

用户需提供：
1. **截图路径**：文件路径或 glob 模式（如 `screenshots/*.png`）
2. **App 类型/用途**：（可选）告知 app 的主要用途，如"图库应用"、"电商应用"等，帮助更准确判断页面功能

```
分析 screenshots/home.png，这是一个图库应用的首页
分析 screenshots/*.png，这是一个电商应用的截图
分析 screenshots/*.png  # App 类型未知，自动搜索
```

---

## 输出结构

每个截图输出一个独立章节，包含：

```markdown
## 截图: {原文件名}

### 页面名称
{根据内容和 App 类型推断的页面名称}

### 页面类型
{页面功能分类：如首页、个人中心、商品详情、搜索结果等}

### 布局结构
{描述页面布局：导航栏、内容区、底部 Tab 等}

### 内容元素
{描述页面可见的主要元素和内容}

### 视觉风格
{描述配色、图标风格、圆角、阴影等 UI 特征}

### 交互特征
{描述可识别的按钮、输入框、手势区域等}

### 功能推测
{基于页面内容推测的交互功能和业务流程}
```

## 批量处理

处理多张截图时：
1. 按文件名排序依次分析
2. 所有分析结果合并到一个 md 文件
3. 文件名：使用第一张截图所在目录 + `screenshot_analysis.md`
4. 如果用户指定了输出路径，使用用户指定路径

## 总结表格

md 文件末尾必须包含：

```markdown
## 截图分析汇总

| 原文件名 | 页面名称 | 页面类型 | 页面摘要 |
|---------|---------|---------|---------|
| home.png | 首页 | 首页/主导航 | 展示应用核心功能入口，包含图片瀑布流和分类标签栏 |
| profile.png | 个人中心 | 用户中心 | 用户头像、信息展示、功能入口列表 |
```

## 分析原则

1. **读取图片**：使用 Read 工具读取截图文件
2. **识别图标**：对照 `references/component-icon-mapping.md` 识别组件功能
3. **推断上下文**：结合 app 类型（已知或推测）推断页面功能
4. **结构化输出**：每个字段清晰分隔
5. **保持一致性**：多张截图采用统一分析维度
6. **生成 md**：最终输出为单个 markdown 文件

---

## References

- `references/component-icon-mapping.md` — UI 组件图标→功能映射表，用于辅助从截图识别功能

## 输出文件名确定规则

1. 用户指定了输出路径 → 使用用户路径
2. 多张截图 → 第一张截图所在目录 + `screenshot_analysis_{timestamp}.md`
3. 单张截图 → 截图同目录 + `{原文件名}_analysis.md`

## 示例

**输入**：
```
分析 screenshots/app_home.png，这是一个图库应用
```

**输出**：生成 `screenshots/app_home_analysis.md`，内容结构如上所述。
