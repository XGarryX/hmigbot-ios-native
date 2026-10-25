> **iOS 源输入**：读取 Swift/Objective-C、SwiftUI/UIKit、Xcode 工程及原生资源；实际源构建与设备观测依赖可用的源平台环境。鸿蒙侧构建和验收保持原流程。源侧操作详见 `a2h-spec/references/native-input.md`。

# 双端驱动命令速查（adb / hdc）

两端同能力的命令对照表。executor 在分发 action 时根据 `--device` 参数选择分支。

## UI Dump（获取当前 UI 树 → 查 selector 的基础）

| 能力 | iOS | HarmonyOS |
|---|---|---|
| dump 到设备 | `adb shell uiautomator dump /sdcard/ui.xml` | `hdc shell uitest dumpLayout -p /data/local/tmp/ui.json` |
| 拉取到本地 | `adb pull /sdcard/ui.xml` | `hdc file recv /data/local/tmp/ui.json` |
| 格式 | XML（uiautomator） | JSON（uitest，结构不同） |

HarmonyOS 的 dumpLayout 偶发卡住 → 重试 2 次，仍不行 `hdc shell pkill uitest` 后再试。

## 截图

```text
[历史源平台示例：不适用于 iOS，不可执行。iOS 源设备/构建按本文件适配及 native-input 协议；目标 hdc/hvigor 检查仍须实际执行。]
# iOS
# 原源平台历史命令（iOS 按本文件适配说明执行）: adb shell screencap -p /sdcard/shot.png && adb pull /sdcard/shot.png

# HarmonyOS
hdc shell snapshot_display -f /data/local/tmp/shot.png
hdc file recv /data/local/tmp/shot.png
```
## 点击 / 滑动 / 输入

| 能力 | iOS | HarmonyOS |
|---|---|---|
| tap | `adb shell input tap <x> <y>` | `hdc shell uitest uiInput click <x> <y>` |
| long press | `adb shell input swipe <x> <y> <x> <y> 800` | `hdc shell uitest uiInput longClick <x> <y>` |
| swipe | `adb shell input swipe <x1> <y1> <x2> <y2> <ms>` | `hdc shell uitest uiInput swipe <x1> <y1> <x2> <y2> <速度>` |
| text | `adb shell input text "hello"` | `hdc shell uitest uiInput inputText <x> <y> "hello"` |
| 回删 | `adb shell input keyevent 67` | `hdc shell uitest uiInput keyEvent Back` |

注意 HarmonyOS 的 `inputText` 需要先点进输入框给焦点。

## 按键

| 键 | iOS | HarmonyOS |
|---|---|---|
| 返回 | `input keyevent 4` | `uitest uiInput keyEvent Back` |
| Home | `input keyevent 3` | `uitest uiInput keyEvent Home` |
| 菜单 | `input keyevent 82` | `uitest uiInput keyEvent Menu` |

## App 生命周期

```text
[历史源平台示例：不适用于 iOS，不可执行。iOS 源设备/构建按本文件适配及 native-input 协议；目标 hdc/hvigor 检查仍须实际执行。]
# iOS
# 原源平台历史命令（iOS 按本文件适配说明执行）: adb shell am start -n com.example.demoapp/.MainActivity
# 原源平台历史命令（iOS 按本文件适配说明执行）: adb shell am force-stop com.example.demoapp

# HarmonyOS
hdc shell aa start -a EntryAbility -b com.example.demoapp
hdc shell aa force-stop com.example.demoapp
```
## 文件传输

| 能力 | iOS | HarmonyOS |
|---|---|---|
| 推文件 | `adb push <local> <remote>` | `hdc file send <local> <remote>` |
| 拉文件 | `adb pull <remote> <local>` | `hdc file recv <remote> <local>` |
| 应用沙箱写 | `run-as <pkg> + cp` | `hdc file send` 到 `/data/app/el2/100/base/<pkg>/haps/entry/files/` |

## 日志

```text
[历史源平台示例：不适用于 iOS，不可执行。iOS 源设备/构建按本文件适配及 native-input 协议；目标 hdc/hvigor 检查仍须实际执行。]
# iOS
# 原源平台历史命令（iOS 按本文件适配说明执行）: adb logcat -v time -T 100 | grep -i demoapp

# HarmonyOS
hdc shell hilog -x | grep -i demoapp
hdc shell hilog -b D  # 切 debug 级别
```
## 权限

```text
[历史源平台示例：不适用于 iOS，不可执行。iOS 源设备/构建按本文件适配及 native-input 协议；目标 hdc/hvigor 检查仍须实际执行。]
# iOS 运行时授权
# 原源平台历史命令（iOS 按本文件适配说明执行）: adb shell pm grant com.example.demoapp ios.permission.READ_EXTERNAL_STORAGE

# HarmonyOS（模拟器）
hdc shell bm dump -n com.example.demoapp   # 先看有哪些权限声明
# 授权通常需要弹窗确认；模拟器可用
hdc shell aa tools setFreePermission -n com.example.demoapp
```
## 设备选择

多台设备时：
```text
[历史源平台示例：不适用于 iOS，不可执行。iOS 源设备/构建按本文件适配及 native-input 协议；目标 hdc/hvigor 检查仍须实际执行。]
# 原源平台历史命令（iOS 按本文件适配说明执行）: adb -s <serial>  devices              # 找 serial
hdc -t <connect_key> ...              # hdc 用 connect_key
```
executor 参数 `--device-id` 映射过去。

## 本 skill 的驱动抽象

`scripts/drivers/` 下两个 adapter：
- `ios.py` — 封装 adb 命令
- `harmonyos.py` — 封装 hdc 命令

两者实现同一个 `DeviceDriver` 接口：
```python
class DeviceDriver:
    def launch_app(pkg, activity=None): ...
    def kill_app(pkg): ...
    def tap(selector=None, coords=None): ...
    def input_text(text, selector=None): ...
    def swipe(from_, to, duration_ms): ...
    def wait_for(signal, value, timeout_ms): ...
    def dump_ui() -> dict: ...      # 统一成 dict 便于 selector 匹配
    def screenshot(save_to): ...
    def push_file(src, dst): ...
    def shell(cmd) -> str: ...      # 逃生舱
```

executor 拿到 action 后根据 `--device` 实例化对应 driver，调接口。新增 action 只需在两个 adapter 里各实现一遍。
