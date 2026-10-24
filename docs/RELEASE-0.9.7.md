# 0.9.7 工具修复与项目交接 · 2026-10-23

权威生产源为 `hmigbot-ios-main`。本轮改动直接维护该目录；临时目录只保存补丁传输、回归日志和发布证据，不作为第二套生产源码。

## 已修复的通用工具链

1. plist 不再作为 UTF-8 源码扫描或绕过：格式解析器验证 binary/XML 内容，资源事实/义务保留，坏资源报 IOS.RESOURCE_PARSE；二进制语义证据必须声明 resource_document 和当前字节 SHA-256。普通 Swift/Objective-C 文本继续严格解码。文本型 AC 真值依然要求真实文本行，不能给二进制伪造物理行。
2. 单一 source responsibility 投影贯通源门禁、原生 typed claims、coverage、Spec、计划、调度、动作和质量视图。保留原始分母与源历史，活动目标分母来自原 helper 的当前重建结果。批准替代不会把未知源私有行为改成已知。
3. 历史动作绑定精确替代边界；公开 ObjC selector 保留冒号参数数量；合法 target action 可保留普通应用 AC。源/审阅/决策/页面/构建证据和原 parser 代码纳入冻结，候选不能直接派发。
4. UI 登记消费结构化精确 source_anchors，避免 .h/.m 展示字符串及同名 SDK slice 误报；完整展示 compound 分类。已有作者计划保留，派生草稿不能充当可执行计划。
5. 修复 macOS `/var` 与 `/private/var` 同目录别名下共享合同闭包报错，原内容与传递依赖完整冻结。
6. 固化 [工具/项目结果分离规则](../rules/tool-project-status-separation.md)，并由安装程序写入托管 AGENTS 提示。工具回归、发布、安装和项目实测分开记录。

0.9.6 的 Objective-C property/ivar 状态、条件构建证据消费和原有发布一致性修复保留。新责任合同见 [source-responsibility](../skills/a2h-spec/references/source-responsibility.md)。

## 不应被改写成工具通过的缺口

缺少完整可回放可达性证据的 unused_symbol 继续阻断。未批准/无授权的差异、遗漏 app 行为、过期图或 coverage、未完成的独立语义复核仍需项目 owner 处理。不能以更新工具、文件存在、单测通过或 UI 报告无 unmapped 宣称项目门禁和行为通过。

## 安装和项目重跑

macOS 从本目录运行 `PYTHON=python3 sh install.sh <workspace>`；Windows 见 [INSTALL](INSTALL.md)。升级先核对托管修改与当前版本；已编辑文件由现有安装保护协议处理，不强行覆盖。

项目 owner 安装后使用真实现有 variant/provider/manifest 参数重新运行 facts（本次资源事实增加解析元数据，旧图会失效），复审 ios-semantics / ios-responsibility / ios-coverage 的新摘要、AC/决策和公开调用链，再运行 spec-check、source-check --harness。旧冻结计划需按原 replan 流程处理。只有正式门禁通过才进入 a2h-plan/execute；生成、编译、设备行为各留真实证据。

本轮发行验证日志和包清单由发布过程单独保存。该工具版本说明不宣称 OFDDemo 已转换、已编译或已行为验收，不创建远端标签或上传服务器。

## 本轮新增的升级要求

- 按需项目内 xattr 修复已接入安装器、原helper、调度与结构运行层；严格拒绝越界路径/链接、HOME、系统根，对临时runtime不执行xattr。原launcher中的隐式无边界调用不再沿用。
- 升级前事务归档并清理精确、内容可识别的机器派生产物，失败恢复。作者Spec/AC/决策、source-index、语义/coverage/responsibility、原始证据与三账本保留。详见 [清理与回滚规则](UPGRADE-CLEANUP.md)。
- `repair-permissions` 提供当前项目范围的显式入口，失败保留实际命令、退出码及可能部分变更的真实状态。
