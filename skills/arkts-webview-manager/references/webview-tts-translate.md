# WebView 内容朗读（TTS）与翻译

本文档覆盖两个从 WebView 提取页面内容后交给外部服务处理的功能：**文本朗读（TTS）** 和 **页面翻译**。仅描述功能实现逻辑，不涉及 UI 布局。

---

## 1. TTS 朗读

### 1.1 技术选型决策树

```
设备是否支持 @kit.CoreSpeechKit？
  ├─ 是 → 使用 textToSpeech.createEngine() 系统 TTS
  │       （需检查 code=202 表示不支持）
  └─ 否 → 设备 WebView 是否支持 Web Speech API？
           ├─ 是 → 注入 JS: window.speechSynthesis.speak()
           └─ 否 → 在线 TTS 服务 + AVPlayer 播放 ← 最通用方案
```

E-Ink 设备、部分定制 ROM 通常不支持系统 TTS 和 Web Speech API，因此**在线 TTS + AVPlayer** 是最可靠的降级方案。

### 1.2 系统 TTS 检测（CoreSpeechKit）

通过 `createEngine` 的错误码判断设备是否支持：

```typescript
import { textToSpeech } from '@kit.CoreSpeechKit';
import { BusinessError } from '@kit.BasicServicesKit';

try {
  const engine = await textToSpeech.createEngine({
    language: 'zh-CN', person: 0, online: 1,
    extraParams: { 'style': 'interaction-broadcast', 'locate': 'zh-CN', 'name': 'EngineName' }
  });
  // 成功 → 使用系统 TTS
} catch (error) {
  const bizErr = error as BusinessError;
  if (bizErr.code === 202) {
    // code=202: "this is not systemCap!" → 设备不支持，降级到在线方案
  }
}
```

### 1.3 在线 TTS + AVPlayer 方案（推荐）

#### 核心流程

```
用户点击播放
  → webController.runJavaScript("document.body.innerText")
  → 清理文本、按标点分段（每段 ≤ 180 字符）
  → 拼接 TTS 服务 URL
  → media.createAVPlayer() 播放 URL
  → AVPlayer completed → 自动播放下一段
  → 全部播完 → release()
```

#### 可用的免费 TTS 端点

| 服务 | URL 模板 | 语言参数 | 语速参数 | 适用地区 | 状态 |
|------|---------|---------|---------|---------|------|
| 百度翻译 | `https://fanyi.baidu.com/gettts?lan={lang}&text={text}&spd={spd}&source=web` | zh/en/jp/kor/fra/de | spd=1~9 (5=正常) | 中国大陆 | ✅ 可用 |
| Google 翻译 | `https://translate.google.com/translate_tts?ie=UTF-8&client=tw-ob&tl={lang}&q={text}` | zh-CN/en/ja/ko/de/fr | 无（固定） | 海外 | ✅ 需翻墙 |
| 有道词典 | `https://dict.youdao.com/dictvoice?type=0&audio={text}` | 自动检测 | 无 | 中国大陆 | ✅ 可用 |

> 这些端点为翻译服务的附属功能，适合轻量使用。高频场景建议使用正式 TTS API。

#### AVPlayer 状态机（必须严格按顺序）

```typescript
import { media } from '@kit.MediaKit';

const avPlayer = await media.createAVPlayer();

avPlayer.on('stateChange', (state: string) => {
  switch (state) {
    case 'initialized':
      avPlayer.prepare();      // initialized → prepared
      break;
    case 'prepared':
      avPlayer.setSpeed(media.PlaybackSpeed.SPEED_FORWARD_1_00_X);
      avPlayer.play();         // prepared → playing
      break;
    case 'completed':
      playNextChunk();         // 播放下一段
      break;
    case 'error':
      avPlayer.reset();
      avPlayer.release();
      break;
  }
});

// 设置 URL 触发状态机启动（idle → initialized）
avPlayer.url = ttsUrl;
```

**关键规则**：
- 不能跳过状态：不能在 initialized 直接 `play()`
- `setSpeed()` 必须在 prepared 之后调用
- 每段播放需创建新 AVPlayer（或 `reset()` 后重新设置 URL）
- 播放完成后必须 `release()` 释放资源

#### AVPlayer 倍速映射

AVPlayer 只支持 6 个固定倍速，用户任意值需映射到最近的有效值：

```typescript
private applySpeed(): void {
  let playbackSpeed: media.PlaybackSpeed;
  if (this.speed <= 0.875) {
    playbackSpeed = media.PlaybackSpeed.SPEED_FORWARD_0_75_X;
  } else if (this.speed <= 1.125) {
    playbackSpeed = media.PlaybackSpeed.SPEED_FORWARD_1_00_X;
  } else if (this.speed <= 1.375) {
    playbackSpeed = media.PlaybackSpeed.SPEED_FORWARD_1_25_X;
  } else if (this.speed <= 1.625) {
    playbackSpeed = media.PlaybackSpeed.SPEED_FORWARD_1_50_X;
  } else if (this.speed <= 1.875) {
    playbackSpeed = media.PlaybackSpeed.SPEED_FORWARD_1_75_X;
  } else {
    playbackSpeed = media.PlaybackSpeed.SPEED_FORWARD_2_00_X;
  }
  this.avPlayer.setSpeed(playbackSpeed);
}
```

#### 文本分段策略

在线 TTS URL 有长度限制（约 200 字符），长文本必须分段：

```typescript
private splitText(text: string, maxLen: number): string[] {
  const chunks: string[] = [];
  const sentences = text.split(/(?<=[。！？.!?\n])/);
  let current = '';
  for (let i = 0; i < sentences.length; i++) {
    const sentence = sentences[i].trim();
    if (sentence.length === 0) continue;
    if (current.length + sentence.length <= maxLen) {
      current += sentence;
    } else {
      if (current.length > 0) chunks.push(current);
      if (sentence.length > maxLen) {
        let pos = 0;
        while (pos < sentence.length) {
          chunks.push(sentence.substring(pos, pos + maxLen));
          pos += maxLen;
        }
        current = '';
      } else {
        current = sentence;
      }
    }
  }
  if (current.length > 0) chunks.push(current);
  return chunks;
}
```

### 1.4 从 WebView 获取页面文本

```typescript
this.webController.runJavaScript("document.body.innerText")
  .then((text: string) => {
    // runJavaScript 返回的是 JSON 字符串，需去除首尾引号和转义
    let content = text;
    if (content.startsWith('"') && content.endsWith('"')) {
      content = content.substring(1, content.length - 1);
      content = content.replace(/\\n/g, ' ')
        .replace(/\\t/g, ' ')
        .replace(/\\"/g, '"')
        .replace(/\\\\/g, '\\');
    }
    // content 现在是纯文本
  });
```

> `runJavaScript` 返回的是 JS 表达式结果的 **JSON 字符串化**形式。字符串类型的返回值会被包裹在引号中，内部的换行/制表符会被转义。

---

## 2. 页面翻译

### 2.1 交互模式

采用**点击/长按分离**模式：
- **点击**"翻译" → 立即执行翻译（调用 `translatePage()`）
- **长按**"翻译" → 弹出翻译设置对话框（选择翻译引擎、目标语言等）

实现方式：在 ActionMenu 的菜单项上添加 `LongPressGesture`，通过 `onLongAction` 回调区分长按操作。

### 2.2 翻译方案对比

| 方案 | 原理 | 优点 | 缺点 |
|------|------|------|------|
| A. URL 重定向 | 通过翻译服务代理 URL 加载整个页面 | 实现最简单 | 完全替换页面布局，丢失原始样式 |
| B. 选中文本翻译 | 获取 `window.getSelection()` 发送到翻译 API | 精准、按需 | 只能翻译选中部分，非全页 |
| **C. 原地翻译（推荐）** | JS 注入遍历 DOM 文本节点 → WebView 内 fetch 翻译 API → 替换文本 | **完整保留页面布局、图片、样式** | 翻译速度取决于文本量和 API 响应 |

### 2.3 方案 A：URL 重定向

将当前 URL 通过翻译服务代理打开，**整个页面会被替换**：

```typescript
// 百度翻译（国内可用）—— 注意：页面布局会完全改变
const translateUrl = 'https://fanyi.baidu.com/transpage?query='
  + encodeURIComponent(this.url) + '&from=auto&to=zh&source=url';
this.webController.loadUrl(translateUrl);

// Google 翻译（需翻墙）
const translateUrl = 'https://translate.google.com/translate?sl=auto&tl=zh-CN&u='
  + encodeURIComponent(this.url);
this.webController.loadUrl(translateUrl);
```

### 2.4 方案 C：原地翻译（推荐）

在 WebView 内通过 JS 完成全部操作，不离开当前页面：

#### 核心流程

```
translatePage()
  → runJavaScript(translateJs)
    → JS: TreeWalker 遍历 body 下所有可见文本节点
    → JS: 按字符上限分组（≤450 字符/组），用 \n 连接
    → JS: 逐组 fetch(MyMemory API) 获取译文
    → JS: 按 \n 拆分译文，逐节点替换 textContent
    → JS: 返回替换计数
  → ArkTS: 显示 toast "翻译完成，已替换 N 处文本"
```

#### 关键设计决策

1. **全部在 JS 中执行**：不使用 native HTTP 模块（`@kit.NetworkKit`），直接在 WebView JS 环境中用 `fetch()` 调用翻译 API。好处是避免了 ArkTS ↔ JS 之间多次通信（收集文本 → 发给 native → native 调 API → 返回结果 → 注入回 JS），一次 `runJavaScript` 即完成全部工作。

2. **文本节点过滤**：TreeWalker 的 `acceptNode` 过滤器跳过：
   - `SCRIPT`、`STYLE`、`NOSCRIPT`、`IFRAME`、`CODE`、`PRE` 标签内容
   - `isContentEditable` 的可编辑区域
   - 长度 < 2 的文本（单字符、空白）
   - 纯数字/标点文本（`/^[\d\s\p{P}]+$/u`）

3. **分组策略**：相邻文本节点合并为一组，每组最多 450 字符，用 `\n` 连接后一次性发送翻译。翻译结果按 `\n` 拆分后逐节点回填。

4. **顺序翻译**：各组通过 Promise 链串行执行（`translateGroup(0) → translateGroup(1) → ...`），避免并发请求被 API 限流。单组失败不影响后续组。

#### 可用的免费翻译 API

| 服务 | URL | 方法 | 适用地区 | 状态 |
|------|-----|------|---------|------|
| MyMemory | `https://api.mymemory.translated.net/get?q={text}&langpair=autodetect\|{target}` | GET | 全球 | ✅ 可用，无需 key |
| 有道翻译 | `https://fanyi.youdao.com/translate?doctype=json&type=AUTO&i={text}` | GET | 中国大陆 | ❌ 已返回 302，不可用 |

> MyMemory API 免费额度：匿名 5000 字/天，注册邮箱后 50000 字/天（`&de=your@email.com`）。

#### 完整 JS 注入代码模式

```javascript
// 注入到 WebView 中执行的完整翻译脚本（通过 runJavaScript 执行）
(function(){
  // 1. 收集可见文本节点
  var walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, {
    acceptNode: function(node) {
      var p = node.parentElement;
      if (!p) return NodeFilter.FILTER_REJECT;
      var tag = p.tagName.toUpperCase();
      if (tag==='SCRIPT'||tag==='STYLE'||tag==='NOSCRIPT'||tag==='IFRAME'
          ||tag==='CODE'||tag==='PRE') return NodeFilter.FILTER_REJECT;
      if (p.isContentEditable) return NodeFilter.FILTER_REJECT;
      var t = node.textContent.trim();
      if (t.length < 2) return NodeFilter.FILTER_REJECT;
      if (/^[\d\s\p{P}]+$/u.test(t)) return NodeFilter.FILTER_REJECT;
      return NodeFilter.FILTER_ACCEPT;
    }
  });
  var nodes = [];
  var n;
  while (n = walker.nextNode()) nodes.push(n);
  if (nodes.length === 0) return Promise.resolve('0');

  // 2. 分组（每组 ≤ 450 字符）
  var groups = [], curGroup = [], curLen = 0;
  for (var i = 0; i < nodes.length; i++) {
    var txt = nodes[i].textContent.trim();
    if (curLen + txt.length > 450 && curGroup.length > 0) {
      groups.push(curGroup);
      curGroup = []; curLen = 0;
    }
    curGroup.push({ node: nodes[i], text: txt });
    curLen += txt.length;
  }
  if (curGroup.length > 0) groups.push(curGroup);

  var targetLang = 'zh';
  var translated = 0;

  // 3. 逐组串行翻译
  function translateGroup(gIdx) {
    if (gIdx >= groups.length) return Promise.resolve(translated);
    var grp = groups[gIdx];
    var combined = grp.map(function(g){ return g.text }).join('\n');
    var url = 'https://api.mymemory.translated.net/get?q='
      + encodeURIComponent(combined) + '&langpair=autodetect|' + targetLang;
    return fetch(url).then(function(r){ return r.json() }).then(function(data) {
      if (data.responseStatus === 200 && data.responseData
          && data.responseData.translatedText) {
        var parts = data.responseData.translatedText.split('\n');
        for (var k = 0; k < grp.length && k < parts.length; k++) {
          var tr = parts[k].trim();
          if (tr.length > 0 && tr !== grp[k].text) {
            grp[k].node.textContent = tr;
            translated++;
          }
        }
      }
      return translateGroup(gIdx + 1);
    }).catch(function(){ return translateGroup(gIdx + 1); });
  }

  return translateGroup(0).then(function(c){ return c.toString() });
})()
```

#### ArkTS 调用侧

```typescript
translatePage(): void {
  if (!this.url) {
    promptAction.showToast({ message: '当前无页面可翻译', duration: 2000 });
    return;
  }
  promptAction.showToast({ message: '正在翻译页面...', duration: 3000 });

  const translateJs = `...`;  // 上面的完整 JS 脚本

  this.webController.runJavaScript(translateJs)
    .then((result: string) => {
      const count = parseInt(result.replace(/"/g, '')) || 0;
      if (count > 0) {
        promptAction.showToast({
          message: '翻译完成，已替换 ' + count.toString() + ' 处文本',
          duration: 2000
        });
      } else {
        promptAction.showToast({ message: '翻译完成', duration: 2000 });
      }
    })
    .catch((err: Error) => {
      promptAction.showToast({ message: '翻译失败: ' + err.message, duration: 2000 });
    });
}
```

### 2.5 方案 B：选中文本翻译

```typescript
this.webController.runJavaScript("window.getSelection().toString()")
  .then((selected: string) => {
    // 调用翻译 API，将结果通过 toast 或弹窗展示
  });
```
