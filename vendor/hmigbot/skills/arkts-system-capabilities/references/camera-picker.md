# 系统相机 CameraKit

> 使用 `@kit.CameraKit` 的 `cameraPicker` 拉起系统相机，替代 Android 的 `MediaStore.ACTION_IMAGE_CAPTURE`。

---

## 基本导入

```typescript
import { cameraPicker, camera } from '@kit.CameraKit'
import { common } from '@kit.AbilityKit'
```

---

## 拉起系统相机拍照

```typescript
async function openCamera(context: common.UIAbilityContext): Promise<string | null> {
  // 配置相机参数
  const pickerProfile: cameraPicker.PickerProfile = {
    cameraPosition: camera.CameraPosition.CAMERA_POSITION_BACK  // 后置相机 ✅ 已验证
    // cameraPosition: camera.CameraPosition.CAMERA_POSITION_FRONT  // 前置相机 ⚠️ 未验证
  }

  try {
    // 拉起系统相机，用户拍照后返回
    const result: cameraPicker.PickerResult = await cameraPicker.pick(
      context,
      [cameraPicker.PickerMediaType.PHOTO],  // 拍照
      pickerProfile
    )

    hilog.info(DOMAIN, TAG, `Photo picked: ${result.resultUri}`)
    return result.resultUri
  } catch (err) {
    hilog.error(DOMAIN, TAG, `Pick photo error: ${err.code}, ${err.message}`)
    return null
  }
}
```

---

## 拉起系统相机录像

> ⚠️ **验证状态**：录像功能在当前代码仓未使用，仅供参考

```typescript
async function openCameraVideo(context: common.UIAbilityContext): Promise<string | null> {
  const pickerProfile: cameraPicker.PickerProfile = {
    cameraPosition: camera.CameraPosition.CAMERA_POSITION_BACK
  }

  try {
    const result: cameraPicker.PickerResult = await cameraPicker.pick(
      context,
      [cameraPicker.PickerMediaType.VIDEO],  // 录像
      pickerProfile
    )

    hilog.info(DOMAIN, TAG, `Video picked: ${result.resultUri}`)
    return result.resultUri
  } catch (err) {
    hilog.error(DOMAIN, TAG, `Pick video error: ${err.code}, ${err.message}`)
    return null
  }
}
```

---

## PickerMediaType 类型

| 类型 | 用途 | 验证状态 |
|------|------|---------|
| `PHOTO` | 拍照 | ✅ 已验证（Index.ets） |
| `VIDEO` | 录像 | ⚠️ 未验证 |

---

## PickerResult 返回

```typescript
interface PickerResult {
  resultUri: string   // 拍摄/录制后的文件 URI
  // 其他字段见官方 API 文档
}
```

---

## module.json5 配置

需要在 skills 中声明相机相关 action 和 entity：

```json5
{
  "skills": [{
    "entities": [
      "entity.system.home",
      "entity.system.camera"    // ← 关键：声明相机能力
    ],
    "actions": [
      "ohos.want.action.home",
      "ohos.want.action.camera"  // ← 关键：声明相机 action
    ]
  }]
}
```

---

## 常见错误

### 错误：未在 module.json5 声明 camera entity

如果未声明 `entity.system.camera`，调用 `cameraPicker.pick()` 会失败，错误码因设备而异。
