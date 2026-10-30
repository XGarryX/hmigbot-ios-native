让软件触达未来用户 

# 鸿蒙系统集成说明 

2024.07.16,北京比特安索信息技术有限公司 

## 1. 集成流程 

- 1) 在 https://bit.bitanswer.cn 注册公司帐号之后,登录比特授权云平台。 

- 2) 在比特授权云平台创建鸿蒙业务和模板。 

- 3) 到比特授权云平台下载页,切换到鸿蒙产品,并下载相关文件: libsc_library.so 、 bitanswer.d.ts 、 bitanswer.ets 。 

- 4) 在 ArkTS 应用中配置授权库及相关文件。 

   - 库文件: entry 目录下创建 libs/${OHOS_ARCH} 目录(例如: libs/arm64-v8a ),将 bitanswer.so 及其依赖库拷贝到该目录下,包括: libcurl.so 、 libnghttp2.so 、 libzstd.so 等。 

   - ArkTS 接口文件: entry/src/main 目录下创建 types/libbitanswer 目录,添加 bitanswer.d.ts 、 bitanswer.ets 和对应的 oh-package.json5 文件。 

   - 配置文件: entry/oh-package.json5 中添加 dependencies ,指向上述 types 目录。 

### 配置完成后,可参考如下示例调用授权接口: 

```arkts
import { Bitanswer } from "../../types/libbitanswer/bitanswer"; import { AAID } from '@kit.PushKit'; 
```

1 

让软件触达未来用户 

```arkts
import { identifier } from '@kit.AdsKit';
import { BusinessError } from '@ohos.base';
import { hilog } from '@kit.PerformanceAnalysisKit';
```

@Entry
@Component
struct Index {
@State message: string = 'Hello World';
  build() {
    Row() {
      Column() {
        Text(this.message)
          .fontSize(50)
          .fontWeight(FontWeight.Bold)
          .onClick(() => {
            AAID.getAAID((err: BusinessError, aaid: string) => {
              if (err) {
                hilog.error(0x0000, 'test', '%{public}d %{public}s', err.code, err.message);
              } else {
                identifier.getOAID().then((oaid) => {
                const bit = new Bitanswer(aaid, oaid);
                bit.update_online(url, sn);
                }).catch((err: BusinessError) => {
                hilog.info(0x0000, 'test', '%{public}d %{public}s', err.code, err.message);
                })
              }
            });
        })
      }
      .width('100%')
    }
    .height('100%')
  }
}

## 2. 权限配置 

授权功能需要额外提供:网络访问权限、设备标识权限,可在 entry/src/main/module.json5 中配置相关权限: 

{  "name": "ohos.permission.INTERNET" }, { "name": "ohos.permission.GET_NETWORK_INFO" 

2 

让软件触达未来用户 

}, { "reason": "$string:reason", "usedScene": { "abilities": [ "EntryFormAbility" ], "when": "inuse" }, "name": "ohos.permission.APP_TRACKING_CONSENT" } 

- 1) ohos.permission.APP_TRACKING_CONSENT 为 user_grant 权限, reason 、 abilities 标签必填,且需要通过弹窗形式向用户申请,具体配置方式参考华为广告标识服务。 

- 2) $string:reason 为字符串资源,需要添加到 entry/src/main/resources 对应语言资源中。 

## 3. 常见问题 

如果授权接口调用时返回了如下错误信息: 

Cannot read property initialize of undefined 

则说明授权接口查找失败,请确认: entry/src/main/oh-package.json5 、 entry/ohpackage.json5 中引用的授权库名称与 libs 目录下的授权库名称是否一致。 

## 4. 其他说明 

相关权限的使用目的和申请时机参见: 

《比特授权云 合规性说明 .pdf 》 

隐私政策链接: https://account.bitanswer.cn/privacy 

3
