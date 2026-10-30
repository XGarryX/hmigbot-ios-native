# 归档报告

## 归档信息
- 变更类型：{新增功能 / 功能变更 / 缺陷修复 / 优化或重构 / 平台迁移}
- 变更名称：{名称}
- 关联特性：feat-{特性}
- 归档日期：{YYYY-MM-DD}

## 代码完成情况
- 开发任务：{已完成数}/{总任务数}
- 单元测试：{通过/未通过}
- 集成测试：{通过/未通过（如有）}

## 设计制品归档
| 制品 | 归档路径 | 状态 |
|------|----------|------|
| proposal.md | {CHANGES_ROOT}/{YYYYMMDD}-{类型}-{名称}/proposal.md | 已保留 |
| delta-spec.md | {SPECS_FEATURE_ROOT}/feat-{特性}/spec.md | 已合并 |
| new-arch.md | {SPECS_FEATURE_ROOT}/feat-{特性}/arch.md | 已合并（如有） |
| delta-design.md | {SPECS_FEATURE_ROOT}/feat-{特性}/design.md | 已合并（如有） |
| tasks.md | {CHANGES_ROOT}/{YYYYMMDD}-{类型}-{名称}/tasks.md | 已保留 |
| design-review.md | {CHANGES_ROOT}/{YYYYMMDD}-{类型}-{名称}/design-review.md | 已保留 |
| apply-report.md | {CHANGES_ROOT}/{YYYYMMDD}-{类型}-{名称}/apply-report.md | 已保留 |

## 变更记录

### 新增需求
{列出本次归档新增的需求}

### 架构变更
{列出本次归档涉及的架构变更（如有）}

### 设计变更
{列出本次归档涉及的设计变更（如有）}

### 代码实现
{列出本次归档实现的代码模块}

## 归档确认
- [ ] 设计制品已合并到 feat-{特性} 目录
- [ ] 变更记录保留在 {CHANGES_ROOT}/{YYYYMMDD}-{类型}-{名称}/ 目录
- [ ] 临时文件已清理
- [ ] todo.md 已更新

## 归档后目录结构

```
{SPECS_FEATURE_ROOT}/feat-{特性}/
├── spec.md                         # 已更新，包含新增需求
├── arch.md                         # 已更新，包含架构变更（如有）
└── design.md                       # 已更新，包含设计变更（如有）

{CHANGES_ROOT}/{YYYYMMDD}-{类型}-{名称}/             # 历史记录保留
├── proposal.md                     # 需求提案
├── tasks.md                        # 开发任务
├── design-review.md                # 设计审视报告
├── apply-report.md                 # 应用测试报告
├── archive-report.md               # 本归档报告
└── todo.md                         # 任务进度（已标记完成）
```
