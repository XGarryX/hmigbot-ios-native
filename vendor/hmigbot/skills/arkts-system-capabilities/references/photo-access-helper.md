# photoAccessHelper 媒体查询指南

> HarmonyOS 媒体库访问的完整使用模式，替代 Android 的 MediaStore + ContentProvider。

---

## 基本导入与初始化

```typescript
import { photoAccessHelper } from '@kit.MediaLibraryKit'
import { dataSharePredicates } from '@kit.ArkData'

const phAccessHelper = photoAccessHelper.getPhotoAccessHelper(context)
```

---

## 查询媒体资源

```typescript
async function getMediaAssets(context: Context): Promise<photoAccessHelper.PhotoAsset[]> {
  const phAccessHelper = photoAccessHelper.getPhotoAccessHelper(context)

  const fetchOptions: photoAccessHelper.FetchOptions = {
    fetchColumns: [
      photoAccessHelper.PhotoKeys.URI,
      photoAccessHelper.PhotoKeys.DISPLAY_NAME,
      photoAccessHelper.PhotoKeys.SIZE,
      photoAccessHelper.PhotoKeys.DATE_ADDED,
      photoAccessHelper.PhotoKeys.DURATION,
      photoAccessHelper.PhotoKeys.WIDTH,
      photoAccessHelper.PhotoKeys.HEIGHT,
      photoAccessHelper.PhotoKeys.PHOTO_TYPE,
    ],
    predicates: new dataSharePredicates.DataSharePredicates()
  }

  const fetchResult = await phAccessHelper.getAssets(fetchOptions)
  const count = fetchResult.getCount()
  const assets: photoAccessHelper.PhotoAsset[] = []

  if (count > 0) {
    let asset = await fetchResult.getFirstObject()
    let index = 0
    while (index < count) {
      assets.push(asset)
      index++
      if (index < count) {
        asset = await fetchResult.getNextObject()
      }
    }
  }

  fetchResult.close()  // 必须关闭！
  return assets
}
```

---

## FetchResult 遍历模式（关键）

**FetchResult 不是数组**，是游标式迭代器。必须按以下模式遍历：

```typescript
// ✅ 正确模式
let asset = await fetchResult.getFirstObject()
let index = 0
while (index < count) {
  // 处理 asset
  processAsset(asset)
  index++
  if (index < count) {
    asset = await fetchResult.getNextObject()
  }
}
fetchResult.close()  // 必须关闭

// ❌ 错误 — 不能用 for...of
for (const asset of fetchResult) { ... }  // 不支持

// ❌ 错误 — 不能一次性获取全部
const allAssets = await fetchResult.getAllObjects()  // 大量数据会内存溢出
```

---

## 获取文件 URI

```typescript
// 获取资源 URI（可用于 Image 组件显示）
const uri = asset.uri  // 格式: file://media/Photo/xxx

// ⚠️ 视频 URI 不能传给 Image 组件（会显示灰色空白）
// 图片 URI 可以直接传给 Image 组件
Image(asset.uri)
  .sourceSize({ width: 256, height: 256 })  // 缩略图优化
```

---

## 按类型筛选

```typescript
// 只查图片
const predicates = new dataSharePredicates.DataSharePredicates()
predicates.equalTo(photoAccessHelper.PhotoKeys.PHOTO_TYPE, photoAccessHelper.PhotoType.IMAGE)

// 只查视频
predicates.equalTo(photoAccessHelper.PhotoKeys.PHOTO_TYPE, photoAccessHelper.PhotoType.VIDEO)
```

---

## 保存图片到系统相册（MediaAssetChangeRequest 三步）

把 app 生成/下载的图片写入系统相册，**走资产变更请求范式**，不要臆造一步式 `saveImage`，也**不要用 `phAccessHelper.createAsset(...)` + `fileIo.open(uri)` + `copyFile` 直写文件**（普通应用无公开的 `createAsset` 直写 API）。

三步（编译校验过）：

```typescript
import { photoAccessHelper } from '@kit.MediaLibraryKit'
import { common } from '@kit.AbilityKit'

// srcFileUri：沙箱内源图片的 file:// URI（沙箱路径可用 fileUri.getUriFromPath 转换）
async function saveImageToAlbum(context: common.UIAbilityContext, srcFileUri: string): Promise<void> {
  const phAccessHelper: photoAccessHelper.PhotoAccessHelper =
    photoAccessHelper.getPhotoAccessHelper(context)

  // 1) 创建图片资产变更请求（photoType + 扩展名；options 可选）
  const req: photoAccessHelper.MediaAssetChangeRequest =
    photoAccessHelper.MediaAssetChangeRequest.createAssetRequest(
      context, photoAccessHelper.PhotoType.IMAGE, 'jpg'
    )

  // 2) 注入图片数据：源文件 URI（string）或 ArrayBuffer 二选一
  req.addResource(photoAccessHelper.ResourceType.IMAGE_RESOURCE, srcFileUri)

  // 3) 提交生效（异步，必须 await / then）
  await phAccessHelper.applyChanges(req)
}
```

关键签名与要点：

| 项 | 内容 |
|----|------|
| 创建请求 | `MediaAssetChangeRequest.createAssetRequest(context: Context, photoType: PhotoType, extension: string, options?: CreateOptions): MediaAssetChangeRequest` |
| 注入数据 | `req.addResource(type: ResourceType, fileUri: string \| ArrayBuffer): void`，类型用 `photoAccessHelper.ResourceType.IMAGE_RESOURCE` |
| 提交 | `await phAccessHelper.applyChanges(req)`（返回 Promise） |
| 权限 | `ohos.permission.WRITE_IMAGEVIDEO`（user_grant：module.json5 声明 + 运行时 `abilityAccessCtrl` 请求，缺一不可） |

> `addResource` 传源文件 URI 时，须确保该 URI 对应的资源实际存在。已有现成图片文件时也可用 `MediaAssetChangeRequest.createImageAssetRequest(context, fileUri)` 一步建请求再 `applyChanges`。

---

## 权限要求

媒体库访问需要声明权限：

```json5
// module.json5
"requestPermissions": [
  {
    "name": "ohos.permission.READ_IMAGEVIDEO",
    "reason": "$string:permission_read_media_reason",
    "usedScene": {
      "abilities": ["EntryAbility"],
      "when": "inuse"
    }
  }
]
```

并在运行时用 `abilityAccessCtrl` 动态请求（见 permission-helper.md）。

> 读相册用 `ohos.permission.READ_IMAGEVIDEO`；**写入相册**（上面的 MediaAssetChangeRequest 保存）必须改用 `ohos.permission.WRITE_IMAGEVIDEO`——只声明读权限不足以写入。两者都是 user_grant，须声明 + 运行时请求。
