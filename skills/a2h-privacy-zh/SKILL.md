---
name: a2h-privacy-zh
description: "查看或关闭本项目数据设置；本包迁移在本地执行，不以参加上游数据计划为前提，也不自动上传材料。"
---

# 本地迁移的数据设置

本发行不安装遥测 hooks，不自动上传源码、会话、spec 或运行证据；迁移不以参与上游数据计划为条件。
读 .migbot/config.json 与当前安装状态，区分保存的历史 consent 值和实际上传能力。

## status

1. 读取现有 config；缺文件说明尚未初始化，不创建假源路径。
2. 报告 telemetry_consent 的现值；本包上传入口未启用，不把 granted 当作曾经上传。
3. 若发现用户自行配置的 hooks/outbox，报告真实配置与待发送状态，不执行上传。

## off / deny

用户明确请求关闭时，在保留其他字段的情况下将 telemetry_consent 分别写 off / denied。
只修改本项目配置；保留既有证据、应用产物及用户其他设置。重新读取确认实际写入。
已在其他系统发送的数据是否删除不能由本地设置推断。

## accept

本包没有配置数据接收服务或同意上传的执行入口。解释此状态，不调用原归档的 enrol/upload 命令。
用户另行决定配置外部服务时，以其明确范围与实际政策处理，不继承历史客户的授权。
所有这些设置都不关闭 a2h-spec/plan/execute/verify/retrospect 的本地迁移能力。
