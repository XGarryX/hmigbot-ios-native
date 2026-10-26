# 无 Mac：云端编译与 Windows 本地 iPhone 安装

适用路线：普通 Apple 账户，GitHub 的 macOS/Xcode 编译未签名真机 IPA，Windows 本地签名并安装到自己的 iPhone。本工具已跑通独立技术样例的云构建、下载和 IPA 检查；未代替用户完成 Apple 登录、手机信任或真机验收。

## 1. 准备工程与云构建配置

需要可构建的原生 Xcode project/workspace 和共享 scheme。在 providers/xcode/cloud.example.json 的副本中填写实际参数：

```json
{
  "project": "NativeCounter.xcodeproj",
  "scheme": "NativeCounter",
  "configuration": "Release",
  "runner": "xcode-27",
  "developer_dir": "/Applications/Xcode_27.app/Contents/Developer"
}
```

示例使用本次实测环境。runner 及 Xcode 路径要按项目要求核对；`xcode-27` 在核对日是 public preview，不能假设以后仍保持相同内容。[GitHub 官方 runner 清单](https://docs.github.com/en/actions/reference/runners/github-hosted-runners)

可选 `test_destination`：填写当前 Xcode 真实可用的 simulator destination；没有测试 target 时不要填写。可选 `setup_commands`：如 `[["pod","install","--deployment"]]`，用于你审核过的依赖准备命令，运行在 source 下。工具不自动推断或执行 Podfile。需要固定锁文件与依赖版本，准备命令若改变纳入摘要的源文件，本次证据会被拒绝；应将变更后的源码重新固定，再提交构建。私有依赖权限按组织现有 CI 管理，不能在配置里写明文 token。

```powershell
python scripts/ios2harmony.py cloud-prepare --source tests/fixtures/cloud_counter --config providers/xcode/cloud.example.json --output work/cloud-export
```

输出包含 source、最小运行时、构建脚本与 `.github/workflows/hmigbot-ios.yml`。这一步不会上传。拒绝打包常见私钥/证书文件；这不是完整的 secret scanner，上传前仍应检查工程中不应进入云端的内容。示例无 Apple 账号、签名证书或业务 App 数据。

## 2. 私有仓库与手动构建

将准备好的输出作为独立私有仓库提交。以下命令在输出目录执行，仓库名自行选择；已有仓库时直接正常提交，不重新创建：

```powershell
git init --initial-branch=main
git add .
git commit -m "Prepare native iOS cloud build"
gh repo create your-private-ios-build --private --source . --remote origin --push
```

只提交准备好的工程目录，不提交整个上级工作区。GitHub CLI 使用用户已有登录；需要首次登录时在本机执行 `gh auth login --web`。Apple 凭证不需要上传到 GitHub。

回到工具根目录，执行：

```text
python scripts/ios2harmony.py cloud-dispatch --repository OWNER/REPOSITORY --ref main
gh run list --repo OWNER/REPOSITORY --limit 5
```

dispatch 校验仓库为 private，工作流仅手动触发，最多运行30分钟。私有仓库使用账号的 Actions 额度，超出部分受其计费设置约束。[官方手动运行说明](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/manually-run-a-workflow)

## 3. 下载并核对指定构建

```text
python scripts/ios2harmony.py cloud-fetch --repository OWNER/REPOSITORY --run-id RUN_ID --source <matching-source> --output <new-download-dir>
python scripts/ios2harmony.py ipa-inspect --ipa <download-dir>/application-unsigned.ipa
```

运行未完成时返回 pending。下载失败后保留现场，排查网络再使用新的下载目录；不要将残缺目录当作成功产物。不会关闭 TLS 证书验证。

下载完成后核对 GitHub run、源码摘要、所有产物摘要、证据包和 IPA。IPA 检查 ZIP CRC、主应用/扩展 Info.plist、arm64 Mach-O 和 iPhoneOS load command，可以拒绝伪装成真机的 arm64 模拟器包。profile 文件存在仍不代表签名有效。

输出含 application-unsigned.ipa、capture 日志、evidence 证据包、cloud-result.json 和 github-run.json。构建产物默认在 GitHub 保留7天，本地下载不受此期限影响。未签名 IPA 不能直接安装。

## 4. Windows 本地签名

使用 [Sideloadly 官方下载](https://sideloadly.io/) 的 Windows 版本。这是独立第三方 GUI，不是 Apple 官方工具，也未内置在本包。按其官网准备 Windows 前置组件；官网要求网页版 iTunes/iCloud。已有 Apple 软件时先核对版本，不由本工具擅自卸载或替换。

1. 用数据线连接并解锁 iPhone，在手机上确认信任电脑，先让 Apple 驱动正常识别设备。
2. 打开 Sideloadly，选中自己的 iPhone，将 `application-unsigned.ipa` 拖入。
3. 选择 Apple ID sideload，使用自己的普通 Apple 账户，在该本地软件内完成登录和验证码。无需将凭证发给 Codex。
4. 开始签名安装，保留真实结果日志。若需要，按手机提示开启“设置 → 隐私与安全性 → 开发者模式”，重启确认；在“通用 → VPN 与设备管理”信任开发者。
5. 启动 App，执行源端场景并记录结果，再进入迁移验证。

免费账户的签名有效期通常为7天，需续签；维持相同 Apple 账户和 Bundle ID 便于覆盖更新和保留应用数据。自动刷新需要本地软件运行且能连接手机。[Sideloadly 官方 FAQ](https://sideloadly.io/faq)

## 5. 特殊能力与失败处理

普通账户并不保证所有 entitlement、扩展、App Group、推送、支付、登录或生态服务可用。检查每个 bundle 的标识、描述文件、授权与源码配置。签名工具修改 Bundle ID 或去掉扩展可能改变行为；若作为排障降级使用，必须把受影响功能标为未验收，不能默默删掉功能。

| 现象 | 排查 |
| --- | --- |
| Actions 中没有工作流 | workflow 文件需位于仓库默认分支，包含 workflow_dispatch；确认上传了真实目录而非仅源码 ZIP |
| scheme 找不到 | 提交共享 scheme，核对 workspace/project 相对路径及大小写 |
| 依赖解析失败 | 核对锁文件、私有包读取权限和已审核的 setup_commands |
| build-settings JSON 解析失败 | 阅读 capture/settings 日志；不接受混有其他输出的 JSON |
| 下载 TLS/EOF 失败 | 排查当前网络/代理，用官方 gh 重试；不禁用 TLS 验证 |
| Sideloadly 看不到手机 | 检查数据线、解锁/信任、Apple 驱动和软件版本 |
| 扩展或权限签名失败 | 逐 bundle 核对 entitlement，按普通账户实际支持决定功能处置；可能需要具备对应权限的开发者账号 |
| 安装成功但不能启动 | 检查开发者模式、信任、签名时效、系统版本和启动日志 |

本工具的安装脚本安装迁移工具与技能；手机 App 安装是本节的另一个步骤。
