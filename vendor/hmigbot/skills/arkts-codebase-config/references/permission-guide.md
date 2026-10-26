# HarmonyOS权限配置指南

本文档详细说明HarmonyOS应用中权限的声明、申请、检查和使用。

## 权限分类

### system_grant（系统授权）
- 系统直接授权，无需用户确认
- 例如：ohos.permission.INTERNET

### user_grant（用户授权）
- 需要用户手动授权
- 例如：ohos.permission.CAMERA、ohos.permission.READ_MEDIA

## 权限配置位置

### module.json5中的声明

```json5
{
  "module": {
    "requestPermissions": [
      {
        "name": "ohos.permission.INTERNET",
        "reason": "$string:internet_permission_reason",
        "usedScene": {
          "abilities": ["EntryAbility"],
          "when": "always"
        }
      },
      {
        "name": "ohos.permission.CAMERA",
        "reason": "$string:camera_permission_reason",
        "usedScene": {
          "abilities": ["EntryAbility", "CameraAbility"],
          "when": "inuse"
        }
      }
    ]
  }
}
```

### 配置字段说明
- **name**：权限名称（必填）
- **reason**：权限申请理由（user_grant权限必填，需引用字符串资源）
- **usedScene**：使用场景（必填）
  - **abilities**：使用该权限的Ability列表
  - **when**：使用时机（always/inuse）
    - always：始终需要
    - inuse：使用时需要

## 常见系统权限列表

### 网络相关
- `ohos.permission.INTERNET` - 网络访问
- `ohos.permission.GET_NETWORK_INFO` - 获取网络信息

### 媒体相关
- `ohos.permission.READ_MEDIA` - 读取媒体
- `ohos.permission.WRITE_MEDIA` - 写入媒体
- `ohos.permission.CAMERA` - 相机访问
- `ohos.permission.MICROPHONE` - 麦克风访问

### 存储相关
- `ohos.permission.READ_WRITE_DOWNLOAD_DIRECTORY` - 读写下载目录
- `ohos.permission.FILE_ACCESS_MANAGER` - 文件访问管理器

### 位置相关
- `ohos.permission.APPROXIMATELY_LOCATION` - 大致位置
- `ohos.permission.LOCATION` - 精确位置

### 设备相关
- `ohos.permission.KEEP_BACKGROUND_RUNNING` - 后台运行
- `ohos.permission.NOTIFICATION_CONTROLLER` - 通知控制

### 用户信息
- `ohos.permission.READ_CONTACTS` - 读取联系人
- `ohos.permission.WRITE_CONTACTS` - 写入联系人

## 权限申请流程

### 步骤1：声明权限
在module.json5的requestPermissions中声明权限

### 步骤2：动态申请权限（user_grant类型）

在Ability或Page中动态申请：

```typescript
import abilityAccessCtrl, { Permissions } from '@ohos.abilityAccessCtrl';
import { BusinessError } from '@ohos.base';

// 定义需要申请的权限
const permissions: Array<Permissions> = ['ohos.permission.CAMERA'];

async function requestPermissions(context: Context) {
  const atManager = abilityAccessCtrl.createAtManager();
  const bundleInfo = context.applicationInfo;
  
  try {
    // 检查权限状态
    const grantStatus = await atManager.checkAccessToken(
      bundleInfo.accessTokenId,
      'ohos.permission.CAMERA'
    );
    
    if (grantStatus === abilityAccessCtrl.GrantStatus.PERMISSION_GRANTED) {
      // 已授权
      console.log('Camera permission already granted');
    } else {
      // 请求授权
      const result = await atManager.requestPermissionsFromUser(context, permissions);
      if (result.authResults[0] === 0) {
        // 授权成功
        console.log('Camera permission granted');
      } else {
        // 授权失败
        console.log('Camera permission denied');
      }
    }
  } catch (err) {
    const error = err as BusinessError;
    console.error('Failed to request permissions', error.code, error.message);
  }
}
```

### 步骤3：权限检查

使用权限前先检查：

```typescript
async function checkPermission(context: Context, permission: Permissions): Promise<boolean> {
  const atManager = abilityAccessCtrl.createAtManager();
  const bundleInfo = context.applicationInfo;
  
  const grantStatus = await atManager.checkAccessToken(
    bundleInfo.accessTokenId,
    permission
  );
  
  return grantStatus === abilityAccessCtrl.GrantStatus.PERMISSION_GRANTED;
}
```

### 步骤4：处理权限回调

```typescript
async function handlePermissionCallback(result: abilityAccessCtrl.RequestResult) {
  const authResults = result.authResults;
  const permissions = result.permissions;
  
  permissions.forEach((permission, index) => {
    if (authResults[index] === 0) {
      console.log(`Permission ${permission} granted`);
    } else {
      console.log(`Permission ${permission} denied`);
      // 引导用户到设置页面
      // context.startAbility({ bundleName: 'com.huawei.systemmanager', ... })
    }
  });
}
```

## 权限使用场景

### 场景1：在Ability启动时申请

```typescript
import UIAbility from '@ohos.app.ability.UIAbility';

export default class EntryAbility extends UIAbility {
  async onCreate(want, launchParam) {
    await requestPermissions(this.context);
  }
}
```

### 场景2：在Page加载时申请

```typescript
import { Page } from '@ohos.arkts.node';

@Entry
@ComponentV2
struct CameraPage {
  async aboutToAppear() {
    const hasPermission = await checkPermission(this.getUIContext(), 'ohos.permission.CAMERA');
    if (!hasPermission) {
      await requestPermissions(this.getUIContext());
    }
  }
}
```

> V1 老项目把 `@ComponentV2` 改回 `@Component` 即可，权限申请逻辑两套版本通用。

### 场景3：在使用功能时申请

```typescript
async function takePhoto() {
  const hasPermission = await checkPermission(context, 'ohos.permission.CAMERA');
  if (hasPermission) {
    // 执行拍照
    startCamera();
  } else {
    // 申请权限
    await requestPermissions(context);
  }
}
```

## 权限常见问题

### 问题1：权限申请失败

**可能原因**：
1. 未在module.json5中声明权限
2. reason字段未填写（user_grant权限）
3. 应用未签名或签名不匹配
4. 设备不支持该权限
5. 用户拒绝授权

**排查方法**：
1. 检查module.json5中的requestPermissions配置
2. 查看日志中的错误信息
3. 确认应用签名配置
4. 检查设备权限设置

### 问题2：权限状态获取错误

**常见错误码**：
- 201：权限名称错误
- 202：参数错误
- 401：调用者信息错误
- 801：内部错误

**解决方法**：
```typescript
try {
  const grantStatus = await atManager.checkAccessToken(...);
} catch (err) {
  const error = err as BusinessError;
  if (error.code === 201) {
    console.error('Permission name is invalid');
  }
}
```

### 问题3：权限申请对话框不弹出

**可能原因**：
1. 权限已授权
2. 权限被永久拒绝
3. 应用在前台但不具备条件

**解决方法**：
1. 先检查权限状态
2. 引导用户到设置页面重新授权
3. 检查应用运行状态

## 权限最佳实践

### 1. 最小权限原则
- 只申请必要的权限
- 及时释放权限
- 分场景申请权限

### 2. 及时说明用途
- reason字段清晰说明权限用途
- 在UI上提示用户为何需要权限
- 提供拒绝后的功能降级方案

### 3. 权限检查时机
- 在需要使用功能前检查
- 避免在启动时一次性申请所有权限
- 对于敏感权限，在使用时申请

### 4. 处理拒绝情况
- 提供友好的提示信息
- 提供设置入口让用户手动授权
- 提供功能降级方案

### 5. 权限状态缓存
- 缓存权限状态减少检查次数
- 权限状态变化时及时更新
- 监听权限状态变化

```typescript
// 监听权限状态变化
function onPermissionStatusChanged(callback: (permission: Permissions, status: number) => void) {
  const atManager = abilityAccessCtrl.createAtManager();
  atManager.on('acquireData', (data) => {
    callback(data.permission, data.status);
  });
}
```

## 权限配置示例

### 示例1：网络应用

```json5
{
  "requestPermissions": [
    {
      "name": "ohos.permission.INTERNET",
      "usedScene": {
        "abilities": ["EntryAbility"],
        "when": "always"
      }
    }
  ]
}
```

### 示例2：相机应用

```json5
{
  "requestPermissions": [
    {
      "name": "ohos.permission.CAMERA",
      "reason": "$string:camera_reason",
      "usedScene": {
        "abilities": ["CameraAbility"],
        "when": "inuse"
      }
    },
    {
      "name": "ohos.permission.WRITE_MEDIA",
      "reason": "$string:write_media_reason",
      "usedScene": {
        "abilities": ["CameraAbility"],
        "when": "inuse"
      }
    }
  ]
}
```

### 示例3：位置应用

```json5
{
  "requestPermissions": [
    {
      "name": "ohos.permission.LOCATION",
      "reason": "$string:location_reason",
      "usedScene": {
        "abilities": ["MapAbility"],
        "when": "inuse"
      }
    }
  ]
}
```

## 权限配置索引

### 查找权限配置的位置
1. **module.json5** → requestPermissions字段
2. **string资源文件** → 权限说明文字
3. **Ability代码** → 权限请求逻辑
4. **Page代码** → 权限检查和使用

### 权限相关代码搜索关键词
- `requestPermissionsFromUser` - 请求权限
- `checkAccessToken` - 检查权限
- `createAtManager` - 创建权限管理器
- `GrantStatus` - 权限状态枚举

## 权限调试技巧

### 查看已授权权限
```typescript
const atManager = abilityAccessCtrl.createAtManager();
const permissions = await atManager.getPermissionsStatus(context);
console.log('Granted permissions:', permissions);
```

### 重置权限状态（开发环境）
- 在设备设置中手动清除应用权限
- 重新安装应用
- 使用adb命令清除权限（需要root）

### 日志调试
```typescript
console.log('Permission status:', grantStatus);
console.log('Permission result:', JSON.stringify(result));
```
