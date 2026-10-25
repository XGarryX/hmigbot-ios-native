> **iOS 源输入**：读取 Swift/Objective-C、SwiftUI/UIKit、Xcode 工程及原生资源；实际源构建与设备观测依赖可用的源平台环境。鸿蒙侧构建和验收保持原流程。源侧操作详见 `a2h-spec/references/native-input.md`。

# CLI 命令速查表 + 设备自动化铁律

> 从 SKILL.md §7 拆出。仅在 Phase 4 实际跑命令时按需 Read。

## HarmonyOS 模拟器命令

| 操作 | 正确命令 | ❌ 错误命令 |
|------|---------|-----------|
| 截图 | `hdc shell snapshot_display -f /data/local/tmp/x.jpeg`（必须 `.jpeg`） | `snapshot_display -f x.png`（不支持 png） |
| 点击 | `hdc shell uitest uiInput click {x} {y}` | `hdc shell uinput -T ...`（不存在）/ `input tap`（不存在） |
| 返回键 | `hdc shell uitest uiInput keyEvent Back` | `input keyevent KEYCODE_BACK`（不存在） |
| 滑动 | `hdc shell uitest uiInput swipe {x1} {y1} {x2} {y2} {speed}` | `input swipe`（不存在） |
| 布局分析 | `hdc shell uitest dumpLayout` | `uiautomator dump`（iOS 命令） |
| 启动应用 | `hdc shell aa start -a EntryAbility -b {bundleName}` | 无 `-W` 等待选项 |
| 强制停止 | `hdc shell aa force-stop {bundleName}` | `am force-stop`（iOS 命令） |
| hdc 路径 | `python3 $SKILLS_ROOT/arkts-visual-verify/scripts/lib_tools.py` 打印的 `hdc`（env HDC > PATH > 平台候选，macOS `/Applications/DevEco-Studio.app/.../toolchains/hdc`、Windows `...\DevEco Studio\sdk\...\hdc.exe`） | 直接 `hdc`（可能不在 PATH） |
| aa start 传参 | `--ps key value`（string 参数） | `-e key value`（旧语法/iOS 语法） |

## iOS 模拟器命令

| 操作 | 命令 |
|------|------|
| 截图 | `adb shell screencap -p /sdcard/x.png` |
| 点击 | `adb shell input tap {x} {y}` |
| 返回键 | `adb shell input keyevent KEYCODE_BACK` |
| 布局分析 | `adb shell uiautomator dump /sdcard/ui.xml` 再 `adb pull /sdcard/ui.xml` |
| 启动 Activity | `adb shell am start -n "{package}/{activity}" -W` |
| 强制停止 | `adb shell am force-stop {package}` |

## 坐标获取规范（必须遵守）

```
⚠️ 禁止使用目测坐标。所有点击坐标必须通过以下流程获取：

1. 执行 dumpLayout / uiautomator dump
2. 解析 JSON/XML，找到目标元素的 bounds
3. bounds 格式: [left, top][right, bottom]
4. 中心点 = ((left + right) / 2, (top + bottom) / 2)
5. 使用中心点坐标执行 click

原因: 目测坐标偏差通常 50-100px，导致点击到错误元素或空白区域，
      浪费大量时间重试。dumpLayout 获取坐标是零成本操作。
```

## 设备自动化铁律（真机 / 模拟器通用，必读）

以下 5 条真机和模拟器**都**成立，任何一条违反，单页截图就能从 30 秒变成 10+ 分钟或直接触发 API 报错：

0. **截图必须 resize 到 ≤1800px**（见 SKILL.md Step 4.1 BLOCKER 级强制约束）。每次拉取完立即过 `scripts/resize_screenshot.py`；读未 resize 的原图一定触发 `API Error: An image ... exceeds the dimension limit (2000px)`，**触发后不可恢复，整轮对话必须从头开始**。rapid capture、debug peek 图同样适用。**resize 脚本 exit code != 0 时禁止继续读图。**

1. **系统进程可 dump**。HarmonyOS 系统 PhotoPicker（`com.huawei.hmos.photos`）、AlbumsActivity 等跑在独立进程的系统 App，`dumpLayout` 依然能拿到它们的节点（实测可见 `完成`、`所有图片`、`拍照` 等 bounds），真机模拟器一致。不要凭"系统进程看不到"的经验跳过 dump 直接目测。

2. **坐标是物理像素**。`snapshot_display` / `screencap` 报告的 width/height（例如 1216×2688）才是 tap 坐标空间，不是截图文件在 IDE / 浏览器里渲染的视觉尺寸。目测比例换算必然 100+px 误差。selector 优先级：`{ text: ... }` > `{ class_name, index }` > 硬编码坐标（仅在无 selector 时，且要在 reference 里标注参考分辨率）。

3. **禁按 Power / 防自动熄屏**。设备到时间会自动熄屏，熄屏后 tap 无响应；真机上更严重——锁屏后 `uitest swipe` 无法解开 PIN / 指纹，链路硬断；模拟器通常 swipe 可解锁，但也会浪费一轮 dump + tap。长等待（AI 生成 10-15s）之前：
   - 首选 `hdc shell settings put system screen_off_timeout 1800000`（跑完恢复）
   - 次选每 20s 发一次小幅 swipe 心跳保活
   - **永远不要**主动按 Power 键"唤醒"——亮屏态按 Power 反而会灭屏

4. **取证用 aa dump 而非截图**。中途"点击后是否进下一页"用 `hdc shell aa dump -l`（看 ability 行）/ `adb shell dumpsys activity top` 便宜准确，不要截图 + Read。截图只留给最终视觉对比。把 tap + sleep + dump 打成一条 shell 调用（bash `;` / PowerShell `;` 均可），别拆成 4 次工具调用。

一旦摸到一个外部 App / 系统页的稳定 selector，**立刻回写**到对应 skill 的 reference（HarmonyOS 系统 App 真机模拟器布局一致，复用价值高），不要只留在当前会话里。
