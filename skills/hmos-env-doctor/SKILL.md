---
name: hmos-env-doctor
description: "按所选构建任务诊断DevEco、SDK与目标工程配置；网络权限需求显式三态，设备发现默认不调用，环境信息不冒充构建或签名通过。"
---

# 鸿蒙目标环境诊断

当前发行仅 macOS ARM64。先读 `.migbot/config.json` 的显式配置与已知 DevEco 安装位置，不遍历全部磁盘或改全局环境。源分析与目标SDK诊断是独立能力；缺目标工具不阻断可独立完成的源文件分析。

```sh
python3 <skill>/scripts/env_doctor.py --project <target> --json
```

脚本以真实 argv 调用所选DevEco的hvigorw、ohpm、java、node版本命令，保存实际可用性与版本；版本查询不证明目标工程可编译，也不套用一个适用于所有项目的主版本门槛。实际构建继续使用a2h-build/Hvigor原始命令和日志。

网络权限由开发者确认：`--network-mode required`、`--network-mode not-required`，或省略保持unknown/WARN。按显式产品与HAP配置检查共享权限，不从没有URL猜离线；本步骤不证明依赖权限合并或运行时网络行为。所选网络场景缺实际权限应给具体恢复选项，不要求离线应用补联网配置。

缺签名材料仅提示未签名诊断的限制；真实签名/设备发布任务仍消费对应官方SDK结果。默认不调用hdc。只有开发者明确选择且批准只读设备发现时才可加`--include-devices`，这不授权点击、安装、截图或远控；缺设备不影响普通构建诊断。

使用`--markdown <项目内报告路径>`时才写诊断报告。报告必须区分可用性、实际调用、构建、签名及行为证据；未经调用不造PASS。修复只作用于具体缺项，不删除用户代码、凭据或改变全局安全策略。
