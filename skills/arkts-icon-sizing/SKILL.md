---
name: arkts-icon-sizing
description: 依据真实 iOS 源布局、图片尺寸与 Asset Catalog scale 检查鸿蒙 Image 尺寸；复用原审计和显式计划修复，不用全局倍率猜尺寸。
metadata:
  type: domain
  domain: ui
  tags:
  - ui
  - migration
  - icon
  - image
  - sizing
---

> **0.13.4 统一合同（优先于历史示例）**：先读 [执行交界合同](../a2h-run/references/execution-boundary.md)。源读取、选定构建配置、SwiftSyntax/facts、源 AC 和 indexed 计划由当前 git 上游唯一生产；从 execute 起使用本技能的 Garry 实施/收口方法。只使用宿主实际支持的派发字段，不照抄 `agent_type`。已有授权直接沿用；依赖失败输入的任务保持 blocked，不降低静态门禁。当前范围禁止屏幕读取/截图/录屏及设备远控；依赖这些观察的检查记 not_run。未经授权不运行遥测上传。工具修复、工具验证、项目转换、HAP 构建和完整迁移验收分别报告，不能用局部 100% 代表全部完成。



# 原生图标尺寸审计与修复

## 原生输入约束

真实显示尺寸优先取 SwiftUI frame/约束/modifier 顺序、UIKit frame/NSLayoutConstraint/intrinsic size；只有实际图片像素和对应 scale 均有证据时，才能用该张图片的像素/scale 还原名义点尺寸。SF Symbol、可拉伸图、动态图片和布局驱动尺寸不可套固定倍率。显式正确的目标尺寸与比例必须保留。

## 用法 A：pipeline 自动集成

保持原 structural_loop pipeline 的 detector 与状态写入器。原生 launcher 在调用前运行原 icon_audit 和 icon_autofix **dry-run**，读取原程序将会改写的集合；dry-run 的默认倍率预测仅用于识别潜在改写，不能作为正式尺寸计划。

有 would-fix 项时不调用原结构引擎，退出 3，报告具体图标。按实际源证据先补目标尺寸/比例，或用下述显式计划，再重跑。集合为空则原样调用原结构引擎，所有原 detector 均执行；事后对比目标代码，意外改写按工具缺陷停止。原 guard 不写目标代码或三个共享状态账本。

通过 Python structural_loop.py 或 run_loop.sh 入口执行；不要直接调用独立编译入口绕过原生输入保护。原 source-density 参数不接收 Asset Catalog，不能将其机械改名成原生参数。原 icon_dims 默认倍率不用于源尺寸取证。

## 用法 B：原三步审计 / 显式修复 / 复核

1. `python scripts/icon_audit.py --json icon_report.json`：原只读审计发现欠约束候选。先检查实际链，候选不等于一定缺尺寸。原分析器对 Image 同行或同缩进修饰链有识别限制；已有正确尺寸时仅将链改为后续更深缩进的独立行，不更改值，并复审。不要通过改变源尺寸迎合启发式。
2. 沿 source_anchors 读取真实尺寸与资源元数据，形成显式 icon_plan.json：例如 `{ "logo": { "w": 24, "h": 12, "src": "Views/ProfileView.swift:42 explicit frame", "source_anchors": ["Views/ProfileView.swift:42"] } }`。这里只是格式示例，不是默认尺寸；必须核验实际源值。找不到依据则保留缺口，不能用随机合理值解除保护。
3. 复用原 `icon_fix.py --plan icon_plan.json --report icon_report.json` dry-run，核验后加 `--apply`。保留正确的一维、按真实比例处理另一维；不改已有完整尺寸、满铺或有意拉伸的背景。
4. 重跑原 icon_audit，进结构循环前原 dry-run 的 would-fix 集合应为空；动态和无可测资源项按原语义披露，不伪造 0。guard 证据在 spec/execution/autofix-log/native-icon-input，包含原报告、原输出、前后代码哈希、原引擎是否实际调用和退出码。
5. 保留原编译与真实视觉验证区分。尺寸静态正确不等于渲染/行为已验证。

## 边界

独立编译程序及内部兼容参数保留，未实现从 Asset Catalog 自动生成所有 native 尺寸计划。源尺寸不明确时安全停止，不承诺全自动修复。目标文件、资源全局密度及其他已正确图标不批量改写。


退出码约定沿用原程序：0=CONVERGED、1=CONTINUE、2=ESCALATED、3=参数/输入/IO错误（含原生图片保护）。3时立刻停止，不读旧result、不finalize或推进阶段，也不原地自动重试。先读取本次guard证据，按已授权源事实修正输入后才可显式重新调用。原detector仅icon自愈会改产品代码，其余只读；结构修复worker在两次loop调用之间执行，不在guard前后快照范围内。后续格式化若改变Image链排版可能误拦，保留正确尺寸值仅按原解析约定排版复审，不能更改值迎合提示。
