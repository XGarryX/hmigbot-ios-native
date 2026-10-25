> **iOS 源输入**：读取 Swift/Objective-C、SwiftUI/UIKit、Xcode 工程及原生资源；实际源构建与设备观测依赖可用的源平台环境。鸿蒙侧构建和验收保持原流程。源侧操作详见 `a2h-spec/references/native-input.md`。

# 设备自动化踩坑速查（真机 / 模拟器通用）

本文记录在 HarmonyOS 设备（真机 + 模拟器）+ 系统进程（PhotoPicker/Photos/权限弹窗）上自动化时真正踩过的坑。4 条铁律**真机和模拟器共用**；个别条目里真机上后果更严重时会明确标注。

## 铁律 1：永远 dumpLayout，不要目测坐标

**踩过的坑**：HarmonyOS 系统 PhotoPicker 跑在独立进程 `com.huawei.hmos.photos`，凭经验以为"系统进程 uitest 看不到"，改用目测坐标（比如从 1216×2688 的截图按比例算），误差动辄 100+px，tap 落在权限 banner / 空白区域，连试几轮毫无进展。这个坑在模拟器上同样成立——模拟器上系统 picker 也是独立进程。

**真相**：`hdc shell uitest dumpLayout` / `adb shell uiautomator dump` 在真机和模拟器上行为一致，**都**能看到系统 PhotoPicker 的节点（实测可见 `完成 [1001,2389][1093,2442]`、`所有图片`、`拍照`、`安全访问图库` 等）。先 dump 再 click，一次命中。

**规则**：
- 设备物理坐标空间 = `snapshot_display` / `screencap` 返回的 width/height（比如 1216×2688），**不是**截图文件在 IDE / 浏览器里渲染的视觉尺寸
- 任何 tap 之前 `dumpLayout` 一次，从 `bounds="[x1,y1][x2,y2]"` 算中心点
- 第一次 dump 可能拿到过渡态空树（动画中、页面未 onReady），参考 `scripts/scenario_run.py::_poll_nodes` 做 6 次 0.5s 轮询

## 铁律 2：长等待前防熄屏，永远别主动按 Power

**踩过的坑**：AI 生成要 10-15 秒，`sleep 15` 期间设备进入熄屏 / 锁屏态；再 tap 看起来"没反应"，实际是屏幕已关。真机上后果更重：`uitest uiInput swipe` 解不开 PIN / 指纹，链路硬断；模拟器通常是无密码 swipe 就能解锁，但也会浪费一轮 dump + tap。

**规则（按优先级，真机 + 模拟器通用）**：
1. **脚本开头把自动熄屏延到足够长**（首选）：
   ```bash
   hdc shell settings put system screen_off_timeout 1800000   # 30 分钟
   # 场景跑完恢复默认
   hdc shell settings put system screen_off_timeout 60000
   ```
   不同 HarmonyOS 版本 settings 命名不一样，跑不通走方案 2。
2. **心跳保活**：长等待期间每 20s 触发一次 `uitest uiInput swipe 600 1500 600 1400 500`（小幅假触摸），真机 + 模拟器都能阻止熄屏。
3. **永远别主动按 Power 键**。"想唤醒屏幕"而按 Power → 亮屏设备反而被按灭，等于倒扣一步。确认状态直接 `snapshot_display`，亮屏与否都能截。
4. 真机额外风险：一旦进了 PIN / 指纹锁屏，`uitest swipe` 解不开，提示用户手动解锁，不要靠脚本硬 swipe。模拟器通常无密码 swipe 可解，但仍建议用规则 1/2 完全规避。

## 铁律 3：取证用 aa dump，别动不动截图

**踩过的坑**：
```
Bash: tap 完成
Bash: sleep 3
Bash: snapshot
Bash: file recv
Read: /tmp/xxx.jpeg    ← 只是为了确认"有没有跳到下一页"
```
一个动作 5 次工具来回。真机 + 模拟器同样吃亏，差别只在单步快慢。

**规则**：
- "跳没跳到下一页"用 `hdc shell aa dump -l | grep ability` / `adb shell dumpsys activity top | grep mResumedActivity` 判断，文本匹配，便宜准确
- 截图只用于**最终视觉取证**（对比用、报告用），不用于中途状态判断
- 一个"执行 + 取证"单元打成一条 bash，不要拆：
  ```bash
  hdc shell uitest uiInput click X Y && sleep 2 && \
    hdc shell aa dump -l | grep -m1 ability
  ```
  需要截图时再把 `snapshot_display + file recv` 串在同一条 bash 里

## 铁律 4：摸到稳定 selector 立刻回写 reference，不要只留在会话里

**踩过的坑**：这次摸出来"HarmonyOS 系统 PhotoPicker 完成按钮 bounds=[1001,2389][1093,2442]"、"拍照 tile 在第一列不要误选"——这些知识只存在当前会话，换人跑一遍还要再摸一次。真机和模拟器上同一系统 App 的布局一致，复用价值高。

**规则**：一旦发现一个系统页 / 外部 App 的稳定 selector，立刻补到 `references/upload-image.md`（或对应场景文档）的"已知 selector"小节，并更新 `assets/*.yaml` 模板。
- **文本 selector 优先**（如 `{ text: "完成" }`）：真机、模拟器、不同屏幕尺寸都能复用
- **类名 + index** 次之（如 `{ class_name: "Image", index: 1 }`）
- **硬编码坐标最后**：在 reference 里必须标注"坐标参考 1216×2688，其他分辨率需等比换算"

## 已知稳定 selector 速查（真机 / 模拟器通用）

### HarmonyOS 系统 PhotoPicker（`com.huawei.hmos.photos`）

| 元素 | selector（推荐） | 坐标参考（1216×2688） | 备注 |
|---|---|---|---|
| "完成"按钮 | `{ text: "完成" }` | ~(1047, 2415) | dumpLayout 可见 |
| "所有图片" tab | `{ text: "所有图片" }` | ~(423, 249) | 顶部分段控件 |
| 第一张真实缩略图 | `{ class_name: "Image", index: 1 }` | ~(380, 1000) | row1 col2 |
| "拍照" tile | `{ text: "拍照" }` | ~(149, 1016) | ❗️它在 col1，不要误选为"第一张图" |
| "安全访问图库" banner | `{ text: "安全访问图库" }` | — | 仅部分授权时出现，点关闭即可 |

### 图片选中后的 App 回流信号（文本 selector，真机 / 模拟器通用）

- VFX 流程：`作品生成` / `作品正在生成中` 标题出现 = 已进入 `VFXCreatePage`
- AI 绘画流程：`开始生成` 按钮出现 = 回到已选图状态
