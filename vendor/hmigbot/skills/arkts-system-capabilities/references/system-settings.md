# 系统设置跳转

> 使用显式 Want + startAbility 跳转到系统设置页面，替代 Android 的 Settings.ACTION_APPLICATION_DETAILS_SETTINGS。

---

## 基本导入

```typescript
import { common, Want } from '@kit.AbilityKit'
import { hilog } from '@kit.PerformanceAnalysisKit'
import { BusinessError } from '@kit.BasicServicesKit'
```

---

## 跳转到应用权限设置页

> ✅ **验证状态**：已在 PermissionHelper.ets:168-182 中验证

```typescript
function openAppSettings(context: common.UIAbilityContext): void {
  try {
    const params: Record<string, string> = { 'page': 'permission' }
    const want: Want = {
      bundleName: 'com.huawei.settings',              // 华为系统设置包名
      abilityName: 'com.huawei.settings.MainAbility', // 主 Ability
      action: 'action.settings.app.info',             // 应用信息页
      parameters: params                               // 传递参数
    }
    
    context.startAbility(want)
      .then(() => {
        hilog.info(DOMAIN, TAG, 'Opened app settings')
      })
      .catch((err: Error) => {
        hilog.error(DOMAIN, TAG, `Failed to open settings: ${err.message}`)
      })
  } catch (err) {
    const error = err as BusinessError
    hilog.error(DOMAIN, TAG, `openAppSettings error: ${error.message}`)
  }
}
```

---

## 封装为工具方法

```typescript
// common/PermissionHelper.ets
export class PermissionHelper {
  private context: common.UIAbilityContext

  constructor(context: common.UIAbilityContext) {
    this.context = context
  }

  openAppSettings(): void {
    try {
      const params: Record<string, string> = { 'page': 'permission' }
      const want: Want = {
        bundleName: 'com.huawei.settings',
        abilityName: 'com.huawei.settings.MainAbility',
        action: 'action.settings.app.info',
        parameters: params
      }
      this.context.startAbility(want)
    } catch (err) {
      const error = err as BusinessError
      hilog.error(DOMAIN, TAG, `openAppSettings error: ${error.message}`)
    }
  }
}
```

---

## 常见系统设置页面

| Action | 用途 | 说明 |
|--------|------|------|
| `action.settings.app.info` | 应用信息页 | 权限管理、存储占用等 ✅ 已验证 |
| `action.settings.wifi` | WiFi 设置 | ⚠️ 未验证 |
| `action.settings.bluetooth` | 蓝牙设置 | ⚠️ 未验证 |
| `action.settings.location` | 定位设置 | ⚠️ 未验证 |

> ⚠️ **注意**：不同设备的系统设置 action 可能不同，以上为华为设备常用 action

---

## 显式 vs 隐式 Want

### 显式 Want（系统设置跳转使用）
```typescript
const want: Want = {
  bundleName: 'com.huawei.settings',    // 明确指定目标应用
  abilityName: 'com.huawei.settings.MainAbility',
  action: 'action.settings.app.info'
}
```
**特点**：
- 精确跳转到指定应用
- 适用于系统应用跳转
- 不需要在 module.json5 中声明 skills

### 隐式 Want（浏览器/分享使用）
```typescript
const want: Want = {
  action: 'ohos.want.action.viewData',  // 只指定 action
  uri: 'https://example.com'            // 让系统匹配
}
```
**特点**：
- 让系统选择合适的应用
- 适用于第三方应用跳转
- 可能需要在 module.json5 中声明 skills

---

## 使用场景

### 何时跳转到系统设置？

1. ✅ 用户拒绝了关键权限，需要手动开启
2. ✅ 需要用户配置系统级设置（WiFi、蓝牙等）
3. ✅ 应用出现异常，引导用户检查权限

### 最佳实践：权限拒绝后引导

```typescript
import { promptAction } from '@kit.ArkUI'

async function requestPermissionWithFallback(
  context: common.UIAbilityContext
): Promise<void> {
  const atManager = abilityAccessCtrl.createAtManager()
  const permissions: Permissions[] = ['ohos.permission.READ_IMAGEVIDEO']
  
  const result = await atManager.requestPermissionsFromUser(context, permissions)
  
  // 检查是否有权限被拒绝
  const denied = result.authResults.some(r => r !== 0)
  
  if (denied) {
    // 用户拒绝了权限，引导到设置页面
    promptAction.showDialog({
      title: '需要权限',
      message: '请在设置中开启相关权限以使用完整功能',
      buttons: [
        { text: '取消', color: '#999999' },
        { text: '去设置', color: '#007DFF' }
      ]
    }).then((result: promptAction.ShowDialogSuccessResponse) => {
      if (result.index === 1) {
        openAppSettings(context)  // 跳转到设置
      }
    })
  }
}
```

### 完整示例：在页面中使用

```typescript
// pages/Index.ets（V2，API 12+）
@ComponentV2
struct Index {
  private permissionHelper: PermissionHelper | null = null
  @Local permissionDenied: boolean = false

  aboutToAppear(): void {
    const context = getContext(this) as common.UIAbilityContext
    this.permissionHelper = PermissionHelper.getInstance(context)
  }

  build() {
    Column() {
      // 权限错误提示
      if (this.permissionDenied) {
        this.buildPermissionErrorUI()
      }
    }
  }

  @Builder
  buildPermissionErrorUI() {
    Column() {
      Text('权限被拒绝')
        .fontSize(20)
        .fontWeight(FontWeight.Bold)
      
      Text('请在设置中开启相关权限')
        .fontSize(14)
        .margin({ top: 16 })
      
      Button($r('app.string.permission_open_settings'))
        .width(200)
        .margin({ top: 16 })
        .onClick(() => {
          this.permissionHelper?.openAppSettings()
        })
    }
    .width('100%')
    .height('100%')
    .justifyContent(FlexAlign.Center)
  }
}
```

---

## module.json5 配置

系统设置跳转通常**不需要额外配置**，因为是显式调用已知应用。

但如果需要响应外部查看请求，需要配置：
```json5
{
  "skills": [{
    "entities": ["entity.system.home"],
    "actions": [
      "ohos.want.action.home",
      "ohos.want.action.view"
    ]
  }]
}
```

---

## 常见错误

### 错误 1：使用错误的 bundleName

```typescript
// 错误 — 非华为设备可能失败
const want: Want = {
  bundleName: 'com.huawei.settings',
  abilityName: 'com.huawei.settings.MainAbility'
}

// 正确 — 根据设备厂商判断（如果需要跨设备）
import { deviceInfo } from '@kit.BasicServicesKit'

const bundleName = deviceInfo.brand === 'huawei' 
  ? 'com.huawei.settings' 
  : 'com.android.settings'  // 其他设备
```

### 错误 2：忘记错误处理

```typescript
// 错误 — startAbility 可能失败
context.startAbility(want)

// 正确 — 处理失败情况
context.startAbility(want)
  .then(() => {
    hilog.info(DOMAIN, TAG, 'Opened settings')
  })
  .catch((err: Error) => {
    hilog.error(DOMAIN, TAG, `Failed to open settings: ${err.message}`)
    promptAction.showToast({ message: '无法打开设置页面' })
  })
```

### 错误 3：参数传递错误

```typescript
// 错误 — 参数类型错误
const want: Want = {
  bundleName: 'com.huawei.settings',
  parameters: { 'page': 123 }  // ❌ 应该是 string
}

// 正确 — 参数类型正确
const want: Want = {
  bundleName: 'com.huawei.settings',
  parameters: { 'page': 'permission' }  // ✅ string 类型
}
```

---

## 与其他跳转方式的对比

| 跳转类型 | Want 类型 | 是否需要配置 | 适用场景 |
|---------|----------|------------|---------|
| 系统设置跳转 | 显式 Want | 不需要 | 跳转到已知系统应用 |
| 浏览器跳转 | 隐式 Want | 通常不需要 | 打开网页/邮件链接 |
| 分享面板 | 系统 API | 通常不需要 | 分享内容到其他应用 |
| 系统相机 | 系统 API | **需要** | 拍照/录像 |

---

## 调用链分析

```
[UI层] 用户点击"打开设置"按钮
    ↓
[事件层] Button.onClick 回调
    ↓
[工具层] PermissionHelper.openAppSettings()
    ↓
[Want构建] 创建显式 Want 对象
    ↓
[系统API] context.startAbility(want)
    ↓
[系统应用] 华为系统设置应用
    ↓
[页面显示] 应用信息/权限设置页
```

---

## 参考链接

- [AbilityKit API 文档](https://developer.huawei.com/consumer/cn/doc/harmonyos-references-V5/js-apis-app-ability-want-V5)
- [权限管理最佳实践](https://developer.huawei.com/consumer/cn/doc/harmonyos-guides-V5/permission-overview-V5)
