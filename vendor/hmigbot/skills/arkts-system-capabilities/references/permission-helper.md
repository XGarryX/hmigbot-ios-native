# 权限请求与检查

> abilityAccessCtrl 权限管理的完整使用模式，替代 Android 的 ActivityCompat.requestPermissions。

---

## 基本导入

```typescript
import { abilityAccessCtrl, Permissions, bundleManager, common } from '@kit.AbilityKit'
```

---

## 完整权限请求封装

```typescript
// helpers/PermissionHelper.ets
export class PermissionHelper {
  /**
   * 检查并请求权限
   * @returns true 表示已获得所有权限
   */
  static async requestPermissions(
    context: common.UIAbilityContext,
    permissions: Permissions[]
  ): Promise<boolean> {
    const atManager = abilityAccessCtrl.createAtManager()

    // 先检查是否已有权限
    const allGranted = await PermissionHelper.checkPermissions(context, permissions)
    if (allGranted) return true

    // 请求权限
    const result = await atManager.requestPermissionsFromUser(context, permissions)

    // 检查结果
    for (let i = 0; i < result.authResults.length; i++) {
      if (result.authResults[i] !== 0) {
        return false  // 有权限被拒绝
      }
    }
    return true
  }

  /**
   * 检查权限状态
   */
  static async checkPermissions(
    context: common.UIAbilityContext,
    permissions: Permissions[]
  ): Promise<boolean> {
    const atManager = abilityAccessCtrl.createAtManager()
    const bundleInfo = await bundleManager.getBundleInfoForSelf(
      bundleManager.BundleFlag.GET_BUNDLE_INFO_WITH_APPLICATION
    )
    const tokenId = bundleInfo.appInfo.accessTokenId

    for (const permission of permissions) {
      const grantStatus = await atManager.checkAccessToken(tokenId, permission)
      if (grantStatus !== abilityAccessCtrl.GrantStatus.PERMISSION_GRANTED) {
        return false
      }
    }
    return true
  }
}
```

---

## 使用示例

```typescript
// 在页面中请求权限
async aboutToAppear(): Promise<void> {
  const context = getContext(this) as common.UIAbilityContext
  const granted = await PermissionHelper.requestPermissions(context, [
    'ohos.permission.READ_IMAGEVIDEO' as Permissions,
    'ohos.permission.INTERNET' as Permissions,
  ])

  if (granted) {
    await this.loadData()
  } else {
    // 提示用户去设置页面开启权限
    this.showPermissionDeniedTip()
  }
}
```

---

## 常用权限列表

| 权限 | 用途 | 类型 |
|------|------|------|
| `ohos.permission.INTERNET` | 网络访问 | system_grant（自动授权）|
| `ohos.permission.READ_IMAGEVIDEO` | 读取媒体文件 | user_grant（需用户同意）|
| `ohos.permission.WRITE_IMAGEVIDEO` | 写入媒体文件 | user_grant |
| `ohos.permission.CAMERA` | 相机 | user_grant |
| `ohos.permission.MICROPHONE` | 麦克风 | user_grant |
| `ohos.permission.LOCATION` | 精确定位 | user_grant |
| `ohos.permission.KEEP_BACKGROUND_RUNNING` | 后台运行 | system_grant |

**system_grant**：在 module.json5 中声明即可，系统自动授权。
**user_grant**：需要在 module.json5 声明 + 代码运行时请求用户同意。
