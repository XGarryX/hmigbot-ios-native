> 来源: ohpm 中央仓 README(T1 信源) | 包: `libarcvisrenhance` | ohpm 最新版: 1.0.0 | 抓取: 2026-07-16
> 注意: 版本可能比市场快照新,以此为准时核对 CHANGELOG

# libarcvisrenhance

`libarcvisrenhance` 是 ArcViSr 当虹画质增强 SDK 的 HarmonyOS HAR 封装。它把原 C SDK 包装成 ArkTS 可调用接口,用于将 NV12 视频帧超分为 1920x1080 NV21 输出帧。

## 能力

- 支持输入分辨率:960x540、1280x720、1920x1080。
- 输入格式:NV12。
- 输出格式:NV21。
- 输出分辨率:固定 1920x1080。
- 输入 `pts` 会透传到对应输出帧。

## 集成

通过 ohpm 安装:

```bash
ohpm i libarcvisrenhance
```

在应用模块的 `oh-package.json5` 中添加依赖:

```json5
{
  "dependencies": {
    "libarcvisrenhance": "file:../libArcViSrEnhance"
  }
}
```

在代码中导入:

```ts
import arcvisr from 'libarcvisrenhance';
```

## 模型目录

SDK 初始化前必须能访问模型文件。HAR 中随包提供以下模型文件,使用方需要将模型部署到可读目录,并在初始化前调用:

```ts
arcvisr.setModelDir('/path/to/model_dir');
```

模型文件名需要包含输入分辨率:

| 输入宽高 | 模型文件名要求 |
| --- | --- |
| 960x540 | 文件名包含 `960x540` |
| 1280x720 | 文件名包含 `1280x720` |
| 1920x1080 | 文件名包含 `1920x1080` |

## 基本用法

```ts
import arcvisr, {
  ARC_VI_SR_STATUS_OK,
  ARC_VI_SR_STATUS_NO_OUTPUT
} from 'libarcvisrenhance';

arcvisr.setModelDir('/path/to/model_dir');

const width = 1280;
const height = 720;
const handle = arcvisr.init(width, height);
if (handle === null) {
  const status = arcvisr.getLastStatus();
  throw new Error(`ArcViSr init failed: ${status} ${arcvisr.statusToString(status)}`);
}

const input = new ArrayBuffer(arcvisr.inputByteLength(width, height));
const output = new ArrayBuffer(arcvisr.outputByteLength());

const inputStatus = arcvisr.setInput(handle, input, 0);
if (inputStatus !== ARC_VI_SR_STATUS_OK) {
  throw new Error(`setInput failed: ${inputStatus} ${arcvisr.statusToString(inputStatus)}`);
}

const result = arcvisr.getOutput(handle, output);
if (result.status === ARC_VI_SR_STATUS_OK) {
  // output 中是 1920x1080 NV21 数据,result.pts 是对应输入 pts。
} else if (result.status === ARC_VI_SR_STATUS_NO_OUTPUT) {
  // 当前暂无输出,可稍后继续轮询。
}

arcvisr.release(handle);
```

## 接口

| 接口 | 说明 |
| --- | --- |
| `setModelDir(modelDir)` | 设置模型目录。 |
| `getModelDir()` | 获取当前模型目录。 |
| `init(inputWidth, inputHeight)` | 初始化超分句柄。失败返回 `null`。 |
| `setInput(handle, input, pts)` | 送入一帧 NV12 数据。 |
| `getOutput(handle, output)` | 获取一帧 NV21 输出,写入调用方提供的缓冲区。 |
| `drain(handle, pts)` | 不再送入新帧时,等待内部剩余帧处理完成。 |
| `release(handle)` | 释放句柄。 |
| `getLastStatus()` | 获取最近一次 SDK 失败状态。 |
| `statusToString(status)` | 将状态码转成文本。 |
| `inputByteLength(width, height)` | 计算输入帧字节数。 |
| `outputByteLength()` | 获取输出帧字节数。 |

## 注意事项

- 仅随 SDK 提供 `arm64-v8a` 原生库。
- 输出缓冲区大小不能小于 `1920 * 1080 * 3 / 2` 字节。
- `ARC_VI_SR_STATUS_NO_OUTPUT` 不是错误,只表示当前还没有可取输出。
- 调用 `release` 后不要继续使用同一个句柄。
