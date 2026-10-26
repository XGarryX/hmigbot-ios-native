# 系统打印管理

> 使用 `@kit.BasicServicesKit` 的 `print` 模块拉起系统打印服务，替代 Android 的 `WebView.print()` 和 `PrintDocumentAdapter`。

---

## 基本导入

```typescript
import { print } from '@kit.BasicServicesKit';
import { common } from '@kit.AbilityKit';
```

---

## 打印当前 Web 页面

> 对应 Android：`WebView.print()`

### 基础用法

```typescript
import { print } from '@kit.BasicServicesKit';

function printWebPage(context: common.UIAbilityContext, webController: WebviewController, jobName: string): void {
  // 创建 Web 打印文档适配器
  const adapter = webController.createWebPrintDocumentAdapter(jobName);

  // 发起打印
  print.print(jobName, adapter, null, context)
    .then(() => {
      hilog.info(DOMAIN, TAG, `Print job ${jobName} sent successfully`);
    })
    .catch((err: Error) => {
      hilog.error(DOMAIN, TAG, `Print failed: ${err.message}`);
    });
}
```

### 在 BrowserPage 中的调用示例

```typescript
import { print } from '@kit.BasicServicesKit';
import { promptAction } from '@kit.ArkUI';

savePdf(): void {
  const adapter = this.webController.createWebPrintDocumentAdapter('savePdf');
  print.print('printJob', adapter, null, getContext(this))
    .then(() => {
      promptAction.showToast({ message: '已发送至打印服务', duration: 2000 });
    })
    .catch((err: Error) => {
      promptAction.showToast({ message: '打印失败: ' + err.message, duration: 2000 });
    });
}
```

---

## 打印自定义内容（PrintDocumentAdapter）

> 用于打印非 Web 内容，如自定义绘制的页面、生成的 PDF 等

```typescript
import { print } from '@kit.BasicServicesKit';
import { common } from '@kit.AbilityKit';

interface PrintRenderParameters {
  webviewController?: WebviewController;
  fileName?: string;
}

class CustomPrintDocumentAdapter extends print.PrintDocumentAdapter {
  private context: common.UIAbilityContext;
  private renderParams?: PrintRenderParameters;

  constructor(context: common.UIAbilityContext) {
    super();
    this.context = context;
  }

  onLayout(jobName: string, printAttributes: print.PrintAttributes,
            onLayoutFinishedCallback: (result: print.PrintLayoutResult) => void,
            data: object): void {
    hilog.info(DOMAIN, TAG, `onLayout called for job: ${jobName}`);
    // 根据 printAttributes 计算布局
    // 计算完成后调用回调
    onLayoutFinishedCallback({ result: print.PrintResult.SUCCESS });
  }

  onWrite(pageNumber: number, printAttributes: print.PrintAttributes,
          onWriteFinishedCallback: (result: print.PrintWriteResult) => void,
          data: object): void {
    hilog.info(DOMAIN, TAG, `onWrite called for page: ${pageNumber}`);
    // 渲染页面内容到打印缓冲区
    // 完成后调用回调
    const fd = ...; // 获取文件描述符
    onWriteFinishedCallback({ result: print.PrintResult.SUCCESS, fileDescriptor: fd });
  }

  onStartLayoutRender(jobName: string, startPageNumber: number, endPageNumber: number,
                      printAttributes: print.PrintAttributes): void {
    hilog.info(DOMAIN, TAG, `Starting layout render from page ${startPageNumber} to ${endPageNumber}`);
  }

  onFinish(): void {
    hilog.info(DOMAIN, TAG, 'Print job finished');
  }
}

function startCustomPrint(context: common.UIAbilityContext): void {
  const adapter = new CustomPrintDocumentAdapter(context);
  const jobName = 'CustomPrintJob';

  print.print(jobName, adapter, null, context)
    .then(() => {
      hilog.info(DOMAIN, TAG, 'Print started successfully');
    })
    .catch((err: Error) => {
      hilog.error(DOMAIN, TAG, `Print error: ${err.message}`);
    });
}
```

---

## print.print() 参数说明

| 参数 | 类型 | 说明 |
|------|------|------|
| `jobName` | `string` | 打印任务名称，会显示在系统打印管理器中 |
| `adapter` | `PrintDocumentAdapter` | 文档适配器，提供页面布局和渲染 |
| `printAttributes` | `PrintAttributes \| null` | 打印属性（纸张大小、方向等），传 null 使用默认 |
| `context` | `UIAbilityContext` | Ability 上下文 |

### PrintAttributes 常用配置

```typescript
const attributes: print.PrintAttributes = {
  orientation: print.Orientation.PORTRAIT,  // 纵向
  // orientation: print.Orientation.LANDSCAPE, // 横向
  // margin: { top: 10, bottom: 10, left: 10, right: 10 },
  // pageSize: { width: 595, height: 842 },  // A4 尺寸（单位：磅）
};
```

### PrintResult 枚举值

| 值 | 说明 |
|----|------|
| `SUCCESS` | 成功 |
| `FAIL` | 失败 |
| `UNKNOWN` | 未知错误 |

---

## module.json5 配置

> ⚠️ **重要**：`print.print()` 通常**不需要**额外权限声明（系统内置能力）。

```json5
{
  // 通常无需配置，以下仅为可能需要的场景
  "requestPermissions": [
    // {
    //   "name": "ohos.permission.PRINT",
    //   "reason": "$string:reason",
    //   "usedScene": {
    //     "abilities": ["EntryAbility"],
    //     "when": "always"
    //   }
    // }
  ]
}
```

---

## 常见错误

### 错误 1：Web 打印适配器未创建

```typescript
// 错误 — webController 可能为 null
const adapter = this.webController.createWebPrintDocumentAdapter('job');

// 正确 — 确保 webController 已初始化
if (this.webController) {
  const adapter = this.webController.createWebPrintDocumentAdapter('job');
  print.print('job', adapter, null, getContext(this));
}
```

### 错误 2：未处理 print.print() 的 Promise  rejection

```typescript
// 错误 — 可能静默失败
print.print(jobName, adapter, null, context);

// 正确 — 必须处理错误
print.print(jobName, adapter, null, context)
  .catch((err: Error) => {
    hilog.error(DOMAIN, TAG, `Print failed: ${err.message}`);
  });
```

---

## Android 对应关系

| Android | HarmonyOS |
|---------|-----------|
| `WebView.print()` | `webController.createWebPrintDocumentAdapter()` + `print.print()` |
| `PrintDocumentAdapter` | `class CustomPrintDocumentAdapter extends print.PrintDocumentAdapter` |
| `PrintManager.print()` | `print.print()` |
| `PrintAttributes` | `print.PrintAttributes` |

---

## 与 documentPicker.save() 的区别

| 维度 | 打印 (`print.print`) | 保存文件 (`DocumentViewPicker.save`) |
|------|---------------------|-------------------------------------|
| 用途 | 发送给打印服务 | 保存到文件系统 |
| 输出 | 纸质打印 / 虚拟 PDF | 文件（.mht / .pdf 等） |
| 用户操作 | 选择打印机、份数 | 选择保存位置和文件名 |
| Web 内容 | ✅ `WebPrintDocumentAdapter` | ❌ 不支持 |
| 自定义内容 | ✅ `PrintDocumentAdapter` | ❌ 不支持 |
| module.json5 配置 | 通常不需要 | 不需要 |
