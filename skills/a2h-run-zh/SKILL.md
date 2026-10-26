---
name: a2h-run-zh
description: "运行原生 iOS→HarmonyOS 的 a2h-spec → a2h-plan → a2h-execute → a2h-verify → a2h-retrospect 全流水线；按已有授权推进，真实记录生成、编译和行为验证状态。"
---


# a2h 原生 iOS 迁移主控

## 启动

读取用户目标、范围、路径和已经授权的步骤；先检查 a2h-init 配置。
未选具体应用时只执行工具开发/安装请求，不把工具仓自身当作 iOS 项目。
所有技能、模板、目标 helper 和 roles 从本包读取，不查找外部插件目录。

## 流水线与阶段门

| 阶段 | 输入 | 交付与必须检查 |
|---|---|---|
| a2h-spec | 真实 iOS 源码与范围 | 工程/UI/功能/API 事实、native semantics、baseline、稳定 AC、source-check 与 trace index |
| a2h-plan | 审阅后的 baseline/decisions | ui-plan、indexed feature-plan、base-plan、slice 归属与 plan coverage |
| a2h-execute | 只读计划与源行为 | 资源、UI、Base、Slice、唯一 closer、真实目标代码与结构/编译闭环 |
| a2h-verify | 当前实现与独立源证据 | 静态/编译/单测/交互/视觉/设备的真实结果和未执行项 |
| a2h-retrospect | 计划、brief、验证记录 | 可复用经验、未关闭项、源版本与变更记录 |

阶段开始前加载该 SKILL.md 及本轮必需 references，不能只读取目录摘要。
使用已有授权自动推进；新的不可推断产品决策才请求用户选择，先完成可审阅材料。
失败按原 `spec/.a2h/open-findings.json` 回流责任阶段，不能将失败步骤记为成功后继续验收。
独立工作可继续，依赖失败输入的部分保持 blocked。不要将“部分可用”写成整轮完成。

## 角色、断点与收口

按任务粒度分配唯一文件 owner，保留原 worker/closer/构建角色职责。
宿主支持且本次工作适合分工时用实际可用的代理接口；不要臆造 agent_type 参数。
不支持具名角色时读取随包角色规程顺序执行。每次完成都回读预期产物，
共享文件由指定 closer 统一落盘，未结束的并发任务不能遗弃。

恢复前检查源 hash、spec/plan 版本、brief 和实际 .ets；不能仅凭 done 文件跳过检查。
重试已成功的纯校验可以复用相同输入证据；源码/构建输入变化必须重新验证。

## 交付

给目标项目路径、实现范围、构建产物、已验证行为和待验证清单。
无 Mac 可完成静态源理解；无设备不能给设备/视觉通过结论。
工具辅助脚本不调用 LLM，不会独立完成任意应用的语义迁移；宿主按技能执行分析与实现。
