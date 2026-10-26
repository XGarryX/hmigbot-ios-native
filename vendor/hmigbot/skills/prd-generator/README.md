# PRD Generator SKILL

基于终端V2.1 PRD模板的产品需求文档生成与分析工具。

## 概述

`prd-generator` 是一个专门用于生成和分析产品需求文档（PRD）的SKILL，基于华为终端V2.1 PRD模板标准。它支持：

- **PRD生成**：根据需求描述自动生成符合V2.1模板规范的PRD文档
- **PRD分析**：分析现有PRD文档，验证完整性和合规性
- **KEP/KEI管理**：提取、验证和管理关键体验路径（KEP）及关键体验指标（KEI）
- **公共需求检查**：自动检查国际化、安全隐私、全局业务等公共需求覆盖情况

## 目录结构

```
prd-generator/
├── SKILL.md                          # SKILL主文件
├── README.md                         # 说明文档
├── references/                       # 参考文档目录
│   ├── prd_format.md                # PRD格式规范
│   ├── completeness_rules.md        # 完整性检查规则
│   ├── kep_validation.md            # KEP验证规则
│   ├── public_requirements.md       # 公共需求参考
│   └── template_reference.md        # 模板章节参考
├── assets/                           # 资源模板目录
│   ├── prd_template.md              # PRD空白模板
│   ├── analysis_report_template.md  # 分析报告模板
│   └── public_requirements_checklist.md  # 公共需求检查清单
└── scripts/                          # Python脚本目录
    ├── prd_generator.py             # PRD生成脚本
    └── prd_analyzer.py              # PRD分析脚本
```

## 功能特性

### 1. PRD生成

支持从需求描述自动生成完整的PRD文档，包括：

- 文档信息与变更记录
- 需求来源、背景、价值分析
- 需求适用范围分析（产品品类、发布范围）
- 目标用户分析
- 竞品分析
- 需求描述（参与者、前置条件、业务流程、功能描述）
- KEP和KEI表格
- 公共需求/能力交互影响分析
- 运营策略
- 非功能需求
- 附录和审批记录

### 2. PRD分析

对现有PRD文档进行全面分析：

- **完整性检查**：验证所有必需章节是否存在
- **格式验证**：检查文档格式是否符合V2.1模板规范
- **KEP验证**：验证KEP格式、命名和完整性
- **KEI验证**：验证关键体验指标的完整性
- **公共需求检查**：检查国际化、安全隐私、全局业务等覆盖情况
- **冲突检测**：识别潜在的需求冲突

### 3. KEP/KEI管理

- **KEP提取**：从PRD中提取所有关键体验路径
- **KEP验证**：验证KEP ID格式、命名规范、优先级等
- **KEI提取**：提取关键体验指标
- **覆盖率分析**：分析KEP/KEI对需求的覆盖情况

### 4. 公共需求检查

自动检查以下公共需求类别：

- **国际化**：中国大陆、全球
- **安全隐私**：儿童账号、个人信息清单、隐私空间、停止服务
- **全局业务**：无障碍、适老化、退/注销账号、OOBE、克隆备份、旋转屏、分屏、外屏适配、自由多窗、双升单、三方应用关联启动、单回退双、小艺问答操控、统一交互

## 使用方法

### SKILL调用方式

在对话中使用以下指令：

#### 生成PRD

```
生成PRD文档：[需求描述]
```

示例：
```
生成PRD文档：开发一个文件管理器功能，支持文件浏览、搜索、复制、移动、删除等操作
```

#### 分析PRD

```
分析PRD文档：[PRD文件路径]
```

示例：
```
分析PRD文档：D:\docs\file_manager_prd.md
```

#### 提取KEP

```
从PRD中提取KEP：[PRD文件路径]
```

#### 检查完整性

```
检查PRD完整性：[PRD文件路径]
```

#### 检查公共需求

```
检查PRD公共需求：[PRD文件路径]
```

### Python脚本使用

#### PRD生成器

```bash
cd scripts
python prd_generator.py --input "需求描述.txt" --output "prd_v1.0.md"
```

选项：
- `--input`: 输入需求描述文件
- `--output`: 输出PRD文件路径
- `--version`: PRD版本号（默认V1.0）
- `--author`: 文档作者

#### PRD分析器

```bash
cd scripts
python prd_analyzer.py --input "prd_v1.0.md" --output "analysis_report.md"
```

选项：
- `--input`: 输入PRD文件路径
- `--output`: 输出分析报告路径
- `--format`: 输出格式（markdown/json，默认markdown）
- `--check-completeness`: 检查完整性
- `--extract-kep`: 提取KEP
- `--check-public`: 检查公共需求

## PRD模板章节说明

### 必需章节

1. **文档信息** - 版本、日期、状态等基本信息
2. **文档变更记录** - 版本历史记录
3. **产品需求**
   - 需求来源
   - 需求背景及业务定位
   - 需求价值分析
   - 需求适用范围分析
   - 目标用户分析（可选）
   - 竞品分析（可选）
   - 需求描述
     - 需求参与者（角色）
     - 前置条件
     - 业务流程
     - 业务功能描述
     - 关键体验路径（KEP）
     - 关键体验指标（KEI）
     - 公共需求/能力交互影响分析
     - 运营策略
4. **非功能需求**
   - 性能要求
   - 安全要求
   - 兼容性要求
5. **附录**
   - 术语表
   - 参考资料
   - 相关文档
6. **审批记录**

### 可选章节

- 目标用户分析（2.5）
- 竞品分析（2.5）
- 受影响的相关功能分析（1.7.7-2）

## KEP格式规范

### KEP ID格式

KEP ID必须遵循模式：`KEP{N}-{NN}`

- **KEP**：字面量前缀
- **{N}**：KEP类别编号（1-9）
- **{NN}**：类别内的顺序编号（01-99）

示例：
- `KEP1-01` - 第1类第01个KEP
- `KEP2-15` - 第2类第15个KEP

### KEP命名规范

- **动词优先**：以中文动词开头
- **简洁**：不超过10个汉字
- **清晰**：避免歧义

示例：
- ✅ 查看文件列表
- ✅ 复制文件
- ❌ 文件列表查看（不是动词优先）
- ❌ 执行（太模糊）

## KEI格式规范

### KEI必需字段

| 字段 | 说明 |
|------|------|
| 评估体系 | 评估体系名称（如用户体验、性能等） |
| 维度 | 评估维度（如响应时间、稳定性等） |
| 评估类型 | 评估类型（定量/定性） |
| 是否必选 | 是否必选（是/否） |
| 评估标准 | 具体的评估标准 |
| IR需求编号 | 关联的需求编号 |
| 功能名称 | 功能名称 |
| 功能编码 | 功能编码 |

## 公共需求检查清单

### 国际化

- [ ] 中国大陆 - 6种语言（中/英/港/台/藏/维）
- [ ] 全球 - 海外销售/上架，个人信息收集

### 安全隐私

- [ ] 儿童账号 - 儿童个人信息保护
- [ ] 已收集个人信息清单上报 - 隐私声明明确
- [ ] 隐私空间 - 不支持功能隐藏
- [ ] 停止服务 - 注销服务方案

### 全局业务

- [ ] 无障碍 - 页面走焦和播报文本
- [ ] 适老化 - 适老化支持
- [ ] 退账号 - 账号退出机制
- [ ] 注销账号 - 注销服务方案
- [ ] OOBE - 首次开机体验
- [ ] 克隆备份 - 数据备份支持
- [ ] 旋转屏 - 横屏支持
- [ ] 分屏 - 多窗口交互
- [ ] 外屏适配 - 折叠机外屏支持
- [ ] 自由多窗 - 自由多窗支持
- [ ] 双升单 - 双屏到单屏
- [ ] 三方应用关联启动管理 - 关联启动控制
- [ ] 单回退双 - 数据继承
- [ ] 小艺问答操控 - 语音控制
- [ ] 统一交互 - 统一交互模式

## 输出格式

### Markdown格式（默认）

生成结构化的Markdown报告，包含：
- 文档信息
- 需求概述
- KEP/KEI清单
- 完整性检查结果
- 公共需求检查结果
- 冲突检测结果
- 改进建议

### JSON格式

```json
{
  "meta": {
    "generated_at": "2026-02-10T20:00:00Z",
    "tool_version": "1.0.0",
    "prd_file": "prd_v1.0.md"
  },
  "document_info": {
    "file": "prd_v1.0.md",
    "version": "V1.0",
    "date": "2026-02-10",
    "author": "产品经理"
  },
  "requirements": {
    "total": 15,
    "kep_count": 8,
    "kei_count": 12
  },
  "completeness": {
    "score": 10,
    "max_score": 12,
    "level": "良好"
  },
  "public_requirements": {
    "internationalization": {
      "china_mainland": "涉及",
      "global": "不涉及"
    },
    "security": {
      "children_account": "不涉及",
      "personal_info": "涉及"
    }
  }
}
```

## 参考文档

- [PRD格式规范](references/prd_format.md)
- [完整性检查规则](references/completeness_rules.md)
- [KEP验证规则](references/kep_validation.md)
- [公共需求参考](references/public_requirements.md)
- [模板章节参考](references/template_reference.md)

## 模板文件

- [PRD空白模板](assets/prd_template.md)
- [分析报告模板](assets/analysis_report_template.md)
- [公共需求检查清单](assets/public_requirements_checklist.md)

## 版本历史

| 版本 | 日期 | 修改内容 |
|------|------|----------|
| V1.0 | 2026-02-10 | 初始版本，支持PRD生成和分析 |

## 许可证

本SKILL遵循与主项目相同的许可证。

## 贡献

欢迎提交问题和改进建议！

## 联系方式

如有问题或建议，请联系项目维护者。