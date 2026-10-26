> 来源: ohpm 中央仓 README(T1 信源) | 包: `@sheca/identity-auth` | ohpm 最新版: 1.0.0 | 抓取: 2026-07-16
> 注意: 版本可能比市场快照新,以此为准时核对 CHANGELOG

# SHECA数字证书SDK

## 下载安装说明

```javascript
ohpm i @sheca/identity-auth
```

## 初始化SDK

```typescriptcript
/**
* enumCASDKType {
*   unknow = 0,
*   QYY = 1, // 企业云SDK
*   SMY = 2, // 市民云SDK
* }
*/
import { FRYZTInterface, CASDKType } from '@sheca/identity-auth'
FRYZTInterface.initSDKType(type: CASDKType)
```

## 加载场景

```typescriptcript
/** 加载场景
* @param context Context对象
* @param url 服务地址
* @param headers  页面请求头信息,企业云不需要,市民云需要放cookie
* @param params 业务参数
* @param isCoordinateEncryptKey  是否协同加密key
* @param callback 数据回调
*/
import { FRYZTInterface, CASDKType } from '@sheca/identity-auth'
FRYZTInterface.loadScene(context: Context,
    url: string,
    headers: Record<string, Object> | undefined,
    params: Record<string, Object> | undefined,
    isCoordinateEncryptKey: boolean,
    callback: (data: Record<string, Object>) => void
  )
```
