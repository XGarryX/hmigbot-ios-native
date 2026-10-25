# Scenario YAML Schema

## 顶层字段

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `name` | string | 是 | 场景唯一名，和文件名保持一致 |
| `description` | string | 否 | 一句话说明 |
| `platforms` | list[string] | 是 | `ios` / `harmonyos` / 两者 |
| `preconditions` | list[string] | 否 | 依赖的其他场景名（执行前自动跑） |
| `steps` | list[Action] | 是 | 有序执行的动作列表 |
| `success_signals` | list[Signal] | 是 | 全部匹配才算成功；空则只看 steps 都没报错 |
| `artifacts` | list[Artifact] | 否 | 要采集的产物 |
| `timeout_ms` | int | 否 | 整体超时，默认 60000 |

## Action 通用结构

```yaml
- action: <type>
  # 仅在多端行为不同时使用，覆盖上面的字段
  ios: { ... }
  harmonyos: { ... }
  # 公共参数
  timeout_ms: 3000
  retry: 2
```

## Action 类型详解

### launch_app / relaunch_app / kill_app
```yaml
- action: launch_app
  package: com.example.demoapp
  ability: EntryAbility   # HarmonyOS 需要
  activity: .MainActivity # iOS 需要
```

### inject_token（登录注入）
```yaml
- action: inject_token
  strategy: static            # static | sms | oauth（后两者预留）
  token_file: spec/scenarios/fixtures/test_token.json
  targets: [preferences, appstorage, lib_network]  # 默认全部
```

### push_file
```yaml
- action: push_file
  src: spec/scenarios/fixtures/test_image.jpg
  dst: /storage/emulated/0/Pictures/test_image.jpg   # iOS
  # 或
  harmonyos:
    dst: /data/media/0/Pictures/test_image.jpg
  trigger_media_scan: true
```

### tap / long_press
```yaml
- action: tap
  selector: { resource_id: "com.example.demoapp:id/btn_login" }
  # 或 selector: { text: "登录" }
  # 或坐标回退
  coords: { x: 540, y: 1800 }
```

`selector` 的匹配优先级：`resource_id` > `text` > `content_desc` > `class_name`。坐标仅在 selector 失败时使用。

### swipe
```yaml
- action: swipe
  from: { x: 540, y: 1800 }
  to: { x: 540, y: 600 }
  duration_ms: 300
```

### input_text
```yaml
- action: input_text
  selector: { resource_id: "...:id/input_phone" }
  text: "10000000000"
  clear_first: true
```

### wait_for
```yaml
- action: wait_for
  signal: ui_contains   # ui_contains | ui_gone | log_line | process_alive
  value: "首页"
  timeout_ms: 5000
  poll_ms: 500
```

### screenshot / dump_ui
```yaml
- action: screenshot
  save_to: artifacts/{timestamp}/after.png   # {timestamp} 由 runner 替换
```

### assert
```yaml
- action: assert
  signal: ui_contains
  value: "您已登录"
  on_fail: abort        # abort | warn | continue
```

### run_scenario（嵌套）
```yaml
- action: run_scenario
  name: login            # 跑另一个场景当作子步骤
```

## Signal 类型

| signal | value 含义 |
|---|---|
| `ui_contains` | UI dump 里出现的文本或 resource-id |
| `ui_gone` | UI dump 里某元素消失 |
| `log_line` | logcat / hilog 出现指定正则 |
| `process_alive` | 进程存活（默认就是 App 自己） |
| `file_exists` | 设备上某路径的文件存在 |

## 完整示例：login.yaml

```yaml
name: login
description: 静态 token 注入，跳过登录 UI
platforms: [ios, harmonyos]
preconditions: []
steps:
  - action: kill_app
    package: com.example.demoapp
  - action: inject_token
    strategy: static
    token_file: spec/scenarios/fixtures/test_token.json
  - action: launch_app
    package: com.example.demoapp
  - action: wait_for
    signal: ui_contains
    value: "首页"
    timeout_ms: 8000
success_signals:
  - type: ui_contains
    value: "首页"
artifacts:
  - screenshot: after.png
  - ui_dump: ui_dump_after.xml
timeout_ms: 30000
```
