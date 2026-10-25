> **iOS 源输入**：读取 Swift/Objective-C、SwiftUI/UIKit、Xcode 工程及原生资源；实际源构建与设备观测依赖可用的源平台环境。鸿蒙侧构建和验收保持原流程。源侧操作详见 `a2h-spec/references/native-input.md`。

# Upload Image 场景实现指南

"上传图片"在本 App 里是高频前置：VFX、AI 绘画、证件照、视频都需要先选一张图。本文档给出可复用的实现 pattern。

## 拆解

一个完整的"上传图片"场景包含 5 步：

1. **准备图片** — 测试用图放 `spec/scenarios/fixtures/images/<name>.jpg`
2. **push 到设备** — 到相册目录
3. **触发媒体扫描** — 让系统感知到新文件（否则 Picker 看不到）
4. **驱动 App 触发选图** — 点开"从相册选"入口
5. **在系统 Picker 里选中图片** — 两端 Picker UI 不同，分别处理

## 1. 测试图片规范

准备 3-4 张覆盖主要尺寸：
- `portrait_1080x1920.jpg` — 竖图（最常见）
- `landscape_1920x1080.jpg` — 横图
- `square_1024x1024.jpg` — 方图
- `tiny_100x100.jpg` — 小图（测边界）

放在 `spec/scenarios/fixtures/images/`，纳入 git。

## 2. push 到相册

### HarmonyOS
HarmonyOS 的媒体库路径随 API 版本变化，模拟器上常见：
```bash
# 沙箱 Pictures 目录（推荐，系统会扫）
hdc file send portrait.jpg /data/storage/el2/base/haps/entry/files/Pictures/

# 或直接 media library（需要 root）
hdc shell mkdir -p /data/media/0/Pictures
hdc file send portrait.jpg /data/media/0/Pictures/test_image.jpg
```

**更可靠的方案**：通过 `photoAccessHelper` 的 API 写入。需要 App 里提供一个 debug 入口（见下）。

### iOS
```text
[历史源平台示例：不适用于 iOS，不可执行。iOS 源设备/构建按本文件适配及 native-input 协议；目标 hdc/hvigor 检查仍须实际执行。]
# 原源平台历史命令（iOS 按本文件适配说明执行）: adb push portrait.jpg /sdcard/Pictures/test_image.jpg
# 原源平台历史命令（iOS 按本文件适配说明执行）: adb shell am broadcast -a ios.intent.action.MEDIA_SCANNER_SCAN_FILE \
  -d file:///sdcard/Pictures/test_image.jpg
```
## 3. 媒体扫描

### HarmonyOS
没有直接的广播。两种方式：
- **重启 media service**：`hdc shell killall media_service`（粗暴但有效）
- **App 内触发**：通过 debug 入口调 `photoAccessHelper.getPhotoAccessHelper(context).release()` + `.refresh()`，详见 HarmonyOS 文档

### iOS
广播 `MEDIA_SCANNER_SCAN_FILE`（见上）。iOS 10+ 在 scoped storage 下最稳的是写到 `MediaStore` 通过 ContentResolver — 但这需要 App 配合。测试场景直接 broadcast 通常够用。

## 4. 触发 App 选图入口

不同功能入口坐标不同。通用模式：

```yaml
- action: tap
  selector: { text: "从相册选择" }   # 或 resource_id
- action: wait_for
  signal: ui_contains
  value: "最近"                      # Picker 出现的标志词
  timeout_ms: 3000
```

## 5. 在 Picker 里选图

### HarmonyOS Picker
包名通常是 `com.huawei.hmos.photos`（photos app）或系统 Photo Picker。
```yaml
- action: wait_for
  signal: ui_contains
  value: "最近"
  timeout_ms: 5000
- action: tap
  selector: { class_name: "Image", index: 0 }   # 第一张图
- action: tap
  selector: { text: "完成" }
```

### iOS DocumentsUI
```yaml
- action: wait_for
  signal: ui_contains
  value: "Pictures"
  timeout_ms: 5000
# DocumentsUI 按缩略图布局，坐标点击更实用
- action: tap
  coords: { x: 270, y: 600 }
```

## 完整 YAML 示例

```yaml
name: upload_image
description: 推一张图到相册并选中它
platforms: [ios, harmonyos]
preconditions: [login]
steps:
  - action: push_file
    src: spec/scenarios/fixtures/images/portrait_1080x1920.jpg
    ios:
      dst: /sdcard/Pictures/test_upload.jpg
    harmonyos:
      dst: /data/storage/el2/base/haps/entry/files/Pictures/test_upload.jpg
    trigger_media_scan: true

  - action: launch_app
    package: com.example.demoapp

  # 假设从首页"AI 绘画"入口
  - action: tap
    selector: { text: "AI 绘画" }
  - action: tap
    selector: { text: "上传照片" }

  # picker
  - action: wait_for
    signal: ui_contains
    value: "最近"
    timeout_ms: 5000
  - action: tap
    harmonyos:
      selector: { class_name: "Image", index: 0 }
    ios:
      coords: { x: 270, y: 600 }
  - action: tap
    selector: { text: "完成" }

  - action: wait_for
    signal: ui_contains
    value: "开始生成"   # App 回到"已选图"状态的标志
    timeout_ms: 8000

success_signals:
  - type: ui_contains
    value: "开始生成"
```

## 常见问题

**Q：push 进去了但 App 里"最近"看不到**
A：没触发扫描。iOS 先试广播，HarmonyOS 先试 kill media_service。仍不行就冷启 emulator。

**Q：Picker 里图片顺序不固定**
A：按文件 mtime 降序。push 时用 `touch` 设最新时间，或文件名带时间戳。

**Q：权限弹窗挡住 Picker**
A：在 `launch_app` 后加 `grant_permissions` action（或 `hdc shell aa tools setFreePermission` / `adb shell pm grant`），把读相册权限直接给了。

**Q：选图后 App 卡在 loading**
A：可能是图片太大触发压缩。换小图测试，或在 wait_for 里加大 timeout_ms。
