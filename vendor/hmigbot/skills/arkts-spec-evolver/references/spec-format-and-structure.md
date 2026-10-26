# 增量 spec 文件格式 + Spec 目录结构 + spec-index 格式

> 从 arkts-spec-evolver/SKILL.md 下沉。SKILL.md 通过 MUST-read 指针引用本文件。

## 增量 spec 文件格式

增量 spec 文件使用模板 `templates/increment-spec-template.md` 生成。

### frontmatter 字段

```yaml
---
id: F-xxx                           # 唯一编号
type: feature                       # feature | bugfix | optimization
title: 播放速度控制                   # 简短标题
priority: P0                        # P0/P1/P2
status: pending                     # pending | planned | in_progress | verifying | done | failed | deprecated
created: YYYY-MM-DD                 # 创建日期
source: issue #45                   # 来源（issue/用户反馈/测试发现/审计发现）
affects:                            # 影响哪些 baseline 文件
  - feature-index: F001
  - feature-base: database
  - ui: page_0001
# deprecated_by:                    # 被哪个增量替代（废弃时填写）
# deprecated_reason:                # 废弃原因（废弃时填写）
---
```

### 正文区域

- **背景** — 为什么需要这个变更
- **复现步骤** — bugfix 类型专用
- **根因分析** — bugfix 类型专用
- **变更描述** — 对 feature-index/feature-base/features/ui 的影响
- **实现指引** — 具体实现方案、注意事项、参考踩坑
- **验收标准** — 可检查的验收条件列表
- **实现计划** — plan 阶段自动生成
- **执行记录** — execute 阶段自动填充
- **验证记录** — verify 阶段自动填充
- **回退记录** — 仅在验证失败回退时填充

---


## Spec 目录结构

```
spec/
├── spec-config.yaml              ← 层定义 + ref 扫描规则（不变）
├── spec-index.md                 ← 主索引（baseline + 增量串联视图）
├── baseline/                     ← 初始生成的 spec（只读基准）
│   ├── ui-manifest.md            ← 页面清单 + 全局约定
│   ├── ui/                       ← 分页 UI spec
│   │   └── page_NNNN.md
│   ├── ui-snapshots/             ← 三源数据
│   ├── feature-index.md          ← 功能清单 + 依赖图
│   ├── feature-base.md           ← 共享基础设施
│   ├── features/                 ← 按功能分 spec
│   │   └── F00x.md
│   └── plans/
│       ├── ui-plan.md
│       ├── feature-plan.md           ← L1 调度索引（plan_format: indexed-v1；Base stub + Group 分节）
│       ├── base-plan.md              ← Base 层任务正文（Stage 2 消费；只读无 checkbox/evidence）
│       ├── slices/slice-NN-<fid>.md  ← L2 逐 slice 只读调度账本
│       └── coverage-matrix.md
├── ref/                          ← 只读输入源（不变）
│   ├── *_design.md
│   ├── *_spec.md
│   └── ui/
├── features/                     ← 功能补全 / 新功能
│   ├── YYYY-MM-DD-Fxxx-description.md
│   └── plans/                    ← 对应的实现计划
│       └── YYYY-MM-DD-Fxxx-plan.md
├── bugfixes/                     ← Bug 修复
│   ├── YYYY-MM-DD-BFxxx-description.md
│   └── plans/
│       └── YYYY-MM-DD-BFxxx-plan.md
└── optimizations/                ← 性能优化 / UI 对齐 / 重构
    ├── YYYY-MM-DD-OPTxxx-description.md
    └── plans/
        └── YYYY-MM-DD-OPTxxx-plan.md
```

**设计原则**: spec 目录完全自包含——每一层 spec（baseline 或增量）都有对应的 plan，spec → plan → code 的完整链路在一个目录树中可追溯。

---

## spec-index.md 作为统一入口

所有 skill 读 spec 时的入口是 `spec/spec-index.md`:

```
任何 skill 需要了解"当前功能全貌"时:
  1. 读 spec-index.md
  2. 看 baseline 摘要
  3. 看增量变更中 status=done 的项
  4. 按需深入读具体文件
```

### spec-index.md 升级格式

```markdown
# Project Migration Spec

## 元数据
- 源项目: <project> (Android)
- 生成时间: YYYY-MM-DD
- a2h-spec 版本: v4
- ref 来源: ai-generated

## Baseline

| 层 | 文件 | 摘要 |
|----|------|------|
| UI | baseline/ui-manifest.md | X 页面, P0*a P1*b P2*c |
| 功能 | baseline/feature-index.md | X 功能, 依赖图 |
| 基础 | baseline/feature-base.md | Models, DB, Network, Events |

## 增量变更

### Features

| ID | 标题 | 优先级 | 状态 | 影响层 | 文件 |
|----|------|--------|------|--------|------|

### Bugfixes

| ID | 标题 | 状态 | 影响层 | 文件 |
|----|------|------|--------|------|

### Optimizations

| ID | 标题 | 状态 | 影响层 | 文件 |
|----|------|------|--------|------|

## 当前状态摘要

- Baseline: ui-manifest(X页面) + feature-index(X功能) + feature-base + features(X个)
- 增量: Features x0 | Bugfixes x0 | Optimizations x0
- 下一编号: F-xxx / BF-xxx / OPT-xxx（从 spec-index.md 读取）

## 交叉引用

<!-- baseline 交叉引用 -->
<!-- 增量交叉引用追加 -->
```

---
