> 来源: ohpm 中央仓 README(T1 信源) | 包: `@shimo/sdk-client` | ohpm 最新版: 1.1.0 | 抓取: 2026-07-16
> 注意: 版本可能比市场快照新,以此为准时核对 CHANGELOG

## Description

石墨文档中台鸿蒙 SDK。  
一行代码即可让你的鸿蒙应用支持 Word 文档、Excel 表格、PowerPoint 幻灯片等 Office 文件离线预览。  
详情请访问石墨文档中台官网 [https://open.shimo.im/client](https://open.shimo.im/client)。  
支持 API12 release 及以上版本。  
已支持的文件类型:`.docx` `.doc` `.docm` `.xlsx` `.xls` `.xlsm` `.pptx` `.ppt` `.pptm`

---

## Install

```bash
ohpm install @shimo/sdk-client
```

---

## Usage

1. 在页面中引入 ShimoOffice 组件。

```extendtypescript
import { ShimoOffice } from '@shimo/sdk-client';
```

2. (可选)初始化 ShimoOffice 组件。

- 如果您的应用使用了 ArkWeb 的 [`Web`](https://developer.huawei.com/consumer/cn/doc/harmonyos-references/ts-basic-components-web) 组件,则需要在 ArkWeb 引擎初始化之前调用此静态方法。
- 如果您的应用使用了 `@ohos.web.webview` 的 [`WebviewController.customizeSchemes`](https://developer.huawei.com/consumer/cn/doc/harmonyos-references/js-apis-webview#customizeschemes) 接口,则需要改造为将 `webCustomSchemes` 通过 ShimoOffice 初始化接口传入。
- 如果您通过初始化接口传入了授权文件、授权密钥,则后续使用 ShimoOffice 组件时可以省略。

```extendtypescript
ShimoOffice.initialize({ license: { data: '[license file content]', key: '[license key]', webCustomSchemes: [] }' })
```

3. 在页面构造中使用 ShimoOffice 组件,并传入授权文件、授权密钥、Office 文件 uri。

- 如果在初始化中已经传入授权文件、授权密钥,则可以省略。

```extendtypescript
ShimoOffice({ license: { data: '[license file content]', key: '[license key]' }, file: '[office file uri]' })
```

---

## Interface

### ShimoOffice

石墨预览组件。  
类型:`@ComponentV2 struct`。

静态方法
| 名称 | 类型 | 说明 |
| ---------------- | ----------------------------------------------- | ---------------------------------------------------------------------- |
| initialize | (options?: [OfficeInitializeOptions](#OfficeInitializeOptions)) => void | 初始化石墨预览组件,根据使用场景决定是否需要调用。 |

组件参数
| 名称 | 类型 | 必填 | 说明 |
| ---------------- | ----------------------------------------------- | ---- | ---------------------------------------------------------------------- |
| license | [License](#License) | 否 | 授权证书,如果初始化组件中已经传入,此处可以神略,否则不传为试用授权,传入及发生变化将立即验证授权。 |
| file | string | 否 | Office 文件 URI,发生变化会自动打开预览,传 `undefined` 将关闭文件预览。 |
| onAuthorize | [AuthorizeHandler](#AuthorizeHandler) | 否 | 授权认证回调,首次认证及认证信息发生变化时触发回调,不可修改。 |
| onAttachmentOpen | [AttachmentOpenHandler](#AttachmentOpenHandler) | 否 | 附件打开回调,打开预览文件内的附件时触发回调,不可修改。 |
| onAttachmentSave | [AttachmentSaveHandler](#AttachmentSaveHandler) | 否 | 附件另存回调,另存预览文件内的附件时触发回调,不可修改。 |
| onLinkOpen | [LinkOpenHandler](#LinkOpenHandler) | 否 | 链接打开回调,打开预览文件内的链接时触发回调,不可修改。 |
| onFullscreen | [FullscreenHandler](#FullscreenHandler) | 否 | 全屏回调,预览文件请求进入或退出全屏时触发回调,不可修改。 |

---

### OfficeInitializeOptions

初始化参数。
类型:`Object`

| 名称             | 类型                                                                                                                   | 必填 | 说明                                                                                                                                                                                                                                                                                             |
| ---------------- | ---------------------------------------------------------------------------------------------------------------------- | ---- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| license          | [License](#License)                                                                                                    | 否   | 授权证书,不传为试用授权。                                                                                                                                                                                                                                                                       |
| onAuthorize      | [AuthorizeHandler](#AuthorizeHandler)                                                                                  | 否   | 授权认证回调,当传入授权证书时生效。                                                                                                                                                                                                                                                             |
| webCustomSchemes | [WebCustomScheme[]](https://developer.huawei.com/consumer/cn/doc/harmonyos-references/js-apis-webview#webcustomscheme) | 否   | ArkWeb 自定义协议配置。如果您的应用使用了 `@ohos.web.webview` 的 [`WebviewController.customizeSchemes`](https://developer.huawei.com/consumer/cn/doc/harmonyos-references/js-apis-webview#customizeschemes) 接口,则需要改造为将 webCustomSchemes 通过此参数传入 `ShimoOffice.initialize` 接口。 |

---

### License

授权证书。  
类型:`Object`。

| 名称 | 类型   | 必填 | 说明                               |
| ---- | ------ | ---- | ---------------------------------- |
| data | string | 是   | 授权证书文件文本内容,UTF-8 编码。 |
| key  | string | 是   | 授权证书密钥,Base64 编码。        |

---

### AuthorizeHandler

授权认证回调。  
类型:`(event: AuthorizeEvent) => void`。

| 名称  | 类型                              | 必填 | 说明               |
| ----- | --------------------------------- | ---- | ------------------ |
| event | [AuthorizeEvent](#AuthorizeEvent) | 是   | 授权认证回调事件。 |

---

### AttachmentOpenHandler

附件打开回调。  
类型:`(event: AttachmentEvent) => void`。

| 名称  | 类型                                | 必填 | 说明                                                                 |
| ----- | ----------------------------------- | ---- | -------------------------------------------------------------------- |
| event | [AttachmentEvent](#AttachmentEvent) | 是   | 附件打开回调事件。调用 `event.preventDefault()` 将阻止默认打开行为。 |

---

### AttachmentSaveHandler

附件另存回调。  
类型:`(event: AttachmentEvent) => void`。

| 名称  | 类型                                | 必填 | 说明                                                                 |
| ----- | ----------------------------------- | ---- | -------------------------------------------------------------------- |
| event | [AttachmentEvent](#AttachmentEvent) | 是   | 附件另存回调事件。调用 `event.preventDefault()` 将阻止默认另存行为。 |

---

### LinkOpenHandler

链接打开回调。  
类型:`(event: LinkEvent) => void`。

| 名称  | 类型                    | 必填 | 说明                                                                 |
| ----- | ----------------------- | ---- | -------------------------------------------------------------------- |
| event | [LinkEvent](#LinkEvent) | 是   | 链接打开回调事件。调用 `event.preventDefault()` 将阻止默认打开行为。 |

---

### FullscreenHandler

全屏回调。  
类型:`(event: FullscreenEvent) => void`。

| 名称  | 类型                                | 必填 | 说明                                                                      |
| ----- | ----------------------------------- | ---- | ------------------------------------------------------------------------- |
| event | [FullscreenEvent](#FullscreenEvent) | 是   | 全屏回调事件。调用 `event.preventDefault()` 将阻止默认进入/退出全屏行为。 |

---

### AuthorizeEvent

授权认证事件。  
类型:`Object`。

| 名称    | 类型                                        | 必填 | 说明           |
| ------- | ------------------------------------------- | ---- | -------------- |
| status  | [AuthorizationStatus](#AuthorizationStatus) | 是   | 认证状态。     |
| license | [LicenseInfo](#LicenseInfo)                 | 否   | 认证证书信息。 |

---

### AttachmentEvent

附件事件。  
类型:[IPreventableEvent](#IPreventableEvent)。

| 名称           | 类型       | 必填 | 说明                                                           |
| -------------- | ---------- | ---- | -------------------------------------------------------------- |
| file           | string     | 是   | 附件文件 URI。                                                 |
| preventDefault | () => void | 是   | 继承至 [IPreventableEvent](#IPreventableEvent)。阻止默认行为。 |

---

### LinkEvent

链接事件。  
类型:[IPreventableEvent](#IPreventableEvent)。

| 名称           | 类型       | 必填 | 说明                                                           |
| -------------- | ---------- | ---- | -------------------------------------------------------------- |
| url            | string     | 是   | 链接 URL。                                                     |
| preventDefault | () => void | 是   | 继承至 [IPreventableEvent](#IPreventableEvent)。阻止默认行为。 |

---

### FullscreenEvent

全屏事件。  
类型:[IPreventableEvent](#IPreventableEvent)。

| 名称           | 类型       | 必填 | 说明                                                           |
| -------------- | ---------- | ---- | -------------------------------------------------------------- |
| fullscreen     | boolean    | 是   | `true` 表示进入全屏,`false`表示退出全屏。                     |
| preventDefault | () => void | 是   | 继承至 [IPreventableEvent](#IPreventableEvent)。阻止默认行为。 |

---

### IPreventableEvent

可阻止事件类型接口。  
类型:`interface`。

| 名称           | 类型       | 必填 | 说明           |
| -------------- | ---------- | ---- | -------------- |
| preventDefault | () => void | 是   | 阻止默认行为。 |

---

### LicenseInfo

认证证书信息。  
类型:`Object`。

| 名称      | 类型   | 必填 | 说明                 |
| --------- | ------ | ---- | -------------------- |
| expiredAt | number | 是   | 授权证书过期时间戳。 |

---

### AuthorizationStatus

认证状态。  
类型:`enum`。

| 名称         | 值           | 说明                 |
| ------------ | ------------ | -------------------- |
| Trial        | Trial        | 试用授权。           |
| TrialExpired | TrialExpired | 试用授权(已过期)。 |
| Authorized   | Authorized   | 正式授权。           |
| Expired      | Expired      | 正式授权(已过期)。 |
| Invalid      | Invalid      | 授权无效。           |
| Error        | Error        | 认证失败。           |

---

## Example

```extendtypescript
import { ShimoOffice, License, AuthorizationStatus, AuthorizeHandler, FullscreenHandler } from '@shimo/sdk-client';
import { picker, fileIo } from '@kit.CoreFileKit';
import { buffer } from '@kit.ArkTS';

interface AuthorizationInfo {
  status: string
  expiredAt?: number;
}

const COMPONENT_SPACE = 10;

@Entry
@Component
struct Index {
  // 授权证书
  @State private license?: License = undefined;
  // 授权信息
  @State authorizationInfo?: AuthorizationInfo = undefined;
  // Office 文件 uri
  @State private officeFile?: string = undefined;
  // 是否允许全屏模式
  @State private enableFullscreen: boolean = true;
  // 全屏模式
  @State private fullscreen: boolean = false;

  build() {
    Column({ space: COMPONENT_SPACE }) {
      Row({ space: COMPONENT_SPACE }) {
        Button('授权')
          .onClick(this.onAuthorizationClick)
        Button('打开')
          .onClick(this.onOpenClick)
        Button('关闭')
          .enabled(!!this.officeFile)
          .onClick(this.onCloseClick)
        Column() {
          Row() {
            Checkbox()
              .select($$this.enableFullscreen)
            Text('允许全屏')
          }
        }
      }
      .alignSelf(ItemAlign.Start)
      .visibility(this.fullscreen ? Visibility.None : Visibility.Visible)

      Row() {
        ShimoOffice({
          license: this.license ? { data: this.license.data, key: this.license.key } : undefined,
          file: this.officeFile,
          onAuthorize: this.onAuthorize,
          onFullscreen: this.onFullscreen
        })
          .border({ width: 1, color: '#41464b' })
      }
      .layoutWeight(1)
    }
    .layoutWeight(1)
    .padding(this.fullscreen ? undefined : COMPONENT_SPACE)
  }

  // 点击打开按钮
  private readonly onOpenClick = () => {
    const docPicker = new picker.DocumentViewPicker();
    const pickerOptions = new picker.DocumentSelectOptions();
    pickerOptions.fileSuffixFilters = ['.docx,.doc,.docm,.xlsx,.xls,.xlsm,.pptx,.ppt,.pptm'];
    docPicker.select(pickerOptions).then(selectResult => {
      const fileUri = selectResult[0];
      if (fileUri) {
        this.officeFile = fileUri;
      }
    });
  };

  // 点击关闭按钮
  private readonly onCloseClick = () => {
    this.officeFile = undefined;
  };

  // 授权完成
  private readonly onAuthorize: AuthorizeHandler = (event) => {
    this.authorizationInfo = {
      status: event.status,
      expiredAt: event.license?.expiredAt,
    }
  }

  // 切换全屏模式
  private readonly onFullscreen: FullscreenHandler = (event) => {
    if (this.enableFullscreen) {
      this.fullscreen = event.fullscreen;
    } else {
      event.preventDefault();
    }
  };

  // 授权证书
  @State private licenseFile?: string = undefined;
  // 证书密钥
  @State private licenseKey: string = '';

  // 授权弹窗 ID
  private authorizationDialogId: number = 0;

  // 授权弹窗
  @Builder
  private authorizationDialog() {
    Column({ space: COMPONENT_SPACE }) {
      Row({ space: COMPONENT_SPACE }) {
        Text('授权信息:')
        Text(this.getAuthorizationText())
          .layoutWeight(1)
          .maxLines(1)
          .textOverflow({ overflow: TextOverflow.MARQUEE })
      }
      .alignSelf(ItemAlign.Start)
      Row({ space: COMPONENT_SPACE }) {
        Button('选择证书')
          .onClick(this.onSelectLicenseClick)
        Text(this.licenseFile ? decodeURI(this.licenseFile) : undefined)
          .layoutWeight(1)
          .maxLines(1)
          .textOverflow({ overflow: TextOverflow.Ellipsis })
          .ellipsisMode(EllipsisMode.START)
        Button('导入密钥')
          .onClick(this.onSelectLicenseKeyClick)
      }
      .alignSelf(ItemAlign.Start)

      Row({ space: COMPONENT_SPACE }) {
        TextArea({ text: $$this.licenseKey, placeholder: '请输入证书密钥' })
          .layoutWeight(1)
          .height('100%')
      }
      .layoutWeight(1)

      Row({ space: COMPONENT_SPACE }) {
        Button('撤销')
          .visibility(this.license ? Visibility.Visible : Visibility.Hidden)
          .onClick(this.onRevokeAuthorizationClick)
        Button('授权')
          .enabled(!!this.licenseFile && !!this.licenseKey)
          .onClick(this.onAuthorizeClick)
        Button('关闭').onClick(this.onCloseAuthorizationClick)
      }
      .alignSelf(ItemAlign.End)
    }
    .padding(COMPONENT_SPACE * 2)
    .constraintSize({ maxWidth: 600, maxHeight: 400 })
    .onClick(this.onAuthorizationDialogClick)
  }

  private getAuthorizationText() {
    let text: string;
    if (!this.authorizationInfo) {
      text = '未授权';
    } else {
      switch (this.authorizationInfo.status) {
        case AuthorizationStatus.Trial:
          text = '试用';
          break;
        case AuthorizationStatus.TrialExpired:
          text = '试用过期';
          break;
        case AuthorizationStatus.Authorized:
          text = '已授权';
          break;
        case AuthorizationStatus.Expired:
          text = '过期';
          break;
        case AuthorizationStatus.Invalid:
          text = '无效';
          break;
        case AuthorizationStatus.Error:
          text = '异常';
          break;
        default:
          text = '未授权';
          break;
      }
      if (this.authorizationInfo.expiredAt) {
        const expiredDate = new Date(this.authorizationInfo.expiredAt);
        text += `(至 ${expiredDate.getFullYear()}年${expiredDate.getMonth() + 1}月${expiredDate.getDate()}日)`
      }
    }
    return text;
  }

  // 密钥输入框失焦
  private blurLicenseKeyInput() {
    this.getUIContext().getFocusController().clearFocus();
  }

  // 读取文件文本
  private readFileText(fileUri: string) {
    let file: fileIo.File | undefined;
    try {
      file = fileIo.openSync(fileUri, fileIo.OpenMode.READ_ONLY);
      const fileSize = fileIo.statSync(file.fd).size;
      const fileBuffer = new ArrayBuffer(fileSize);
      fileIo.readSync(file.fd, fileBuffer);
      const text = buffer.from(fileBuffer).toString();
      return text;
    } catch {
      return '';
    } finally {
      if (file) {
        try {
          fileIo.closeSync(file);
        } catch {}
      }
    }
  }

  // 点击授权按钮
  private readonly onAuthorizationClick = () => {
    this.getUIContext().getPromptAction().openCustomDialog({
      builder: () => {
        this.authorizationDialog()
      }
    }).then((dialogId: number) => {
      this.authorizationDialogId = dialogId;
    });
  };

  // 点击窗口空白处
  private readonly onAuthorizationDialogClick = () => {
    this.blurLicenseKeyInput();
  }

  // 点击选择证书按钮
  private readonly onSelectLicenseClick = () => {
    const docPicker = new picker.DocumentViewPicker();
    docPicker.select().then(selectResult => {
      const fileUri = selectResult[0];
      if (fileUri) {
        this.licenseFile = fileUri;
      }
    });
  };

  // 点击从文件导入密钥按钮
  private readonly onSelectLicenseKeyClick = () => {
    const docPicker = new picker.DocumentViewPicker();
    docPicker.select().then(selectResult => {
      const fileUri = selectResult[0];
      if (fileUri) {
        this.licenseKey = this.readFileText(fileUri);
      }
    });
  }

  // 点击授权弹窗撤销按钮
  private readonly onRevokeAuthorizationClick = () => {
    this.blurLicenseKeyInput();
    this.license = undefined;
    this.licenseFile = undefined;
    this.licenseKey = '';
  };

  // 点击授权弹窗授权按钮
  private readonly onAuthorizeClick = () => {
    this.blurLicenseKeyInput();
    if (this.licenseFile && this.licenseKey) {
      const licenseData = this.readFileText(this.licenseFile);
      if (licenseData) {
        this.license = { data: licenseData, key: this.licenseKey };
      } else {
        this.license = undefined;
      }
    }
  };

  // 点击授权弹窗关闭按钮
  private readonly onCloseAuthorizationClick = () => {
    this.blurLicenseKeyInput();
    this.getUIContext().getPromptAction().closeCustomDialog(this.authorizationDialogId);
  }
}
```

---

## Contact

[授权申请](https://shimo.im/forms/77XTY8eb5OCFl3m5/fill?channel=sdk)  
技术支持: [raoxin@shimo.im](mailto:raoxin@shimo.im)  
[石墨文档 shimo.im](https://shimo.im)  
Copyright © 武汉初心科技有限公司
