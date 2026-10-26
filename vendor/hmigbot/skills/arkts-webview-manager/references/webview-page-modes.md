# WebView 页面模式

本文档涵盖常见的 WebView 页面模式实现：桌面模式、隐私模式、阅读模式、竖排文本、分屏。

> 代码示例使用 ArkTS V2 装饰器（`@ComponentV2 / @Local`）。V1 老项目把 `@Local → @State` 即可，WebView API 部分原样保留。

## 1. 桌面模式（Desktop Mode）

通过切换 User-Agent 实现。切换后必须 `refresh()` 才能生效，因为服务器根据 UA 返回不同内容。

```typescript
@Local private isDesktopMode: boolean = false;

toggleDesktopMode(): void {
  const desktopUA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36';
  const mobileUA = 'Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36 Chrome/90.0.0.0 Mobile Safari/537.36';
  this.isDesktopMode = !this.isDesktopMode;
  this.webController.setCustomUserAgent(this.isDesktopMode ? desktopUA : mobileUA);
  this.webController.refresh();
}
```

## 2. 隐私模式（Incognito Mode）

隐私模式的核心是 UI 外观切换（如深色主题）。实际的隐私行为（不保存历史、清除 Cookie 等）需在业务层实现。

```typescript
@Local private isIncognito: boolean = false;

toggleIncognito(): void {
  this.isIncognito = !this.isIncognito;
  // 通知 ViewModel 或业务层处理隐私逻辑
}

// UI 条件样式示例
.backgroundColor(this.isIncognito ? '#1D1D1D' : '#FFFFFF')
```

## 3. 阅读模式（Read Mode）

使用 Mozilla Readability.js 提取文章正文，替换页面 body。这是一个完整的"进入-退出"模式，需要缓存原始 HTML 以便恢复。

### 实现流程

```
进入阅读模式:
1. 注入阅读模式 CSS（rawfile → style 元素）
2. 加载 Readability.js 库（rawfile → runJavaScript）
3. 执行 Readability 解析 → 获取 article 对象
4. 缓存原始 HTML → document.innerHTMLCache
5. 替换 body → createHtmlBody(article)
6. 滚动到顶部

退出阅读模式:
1. 从缓存恢复原始 body
2. 移除阅读模式 CSS
3. 滚动到顶部
```

### 代码模式

```typescript
@Local private isReadMode: boolean = false;

toggleReadMode(): void {
  this.isReadMode = !this.isReadMode;
  if (this.isReadMode) {
    // 1. 注入阅读模式 CSS
    this.injectCssFromRawfile('readerview.css', 'myapp_readerview_style');

    // 2-5. 加载库 → 解析 → 缓存 → 替换
    this.loadAndRunRawfile('MozReadability.js').then(() => {
      const replaceBodyJs = `(function(){
        var dc = document.cloneNode(true);
        var article = new Readability(dc, {classesToPreserve: preservedClasses, overwriteImgSrc: true}).parse();
        if (!article) { document.title = '__READER_FAIL__'; return; }
        document.innerHTMLCache = document.body.innerHTML;
        document.body.outerHTML = createHtmlBody(article);
      })()`;
      this.webController.runJavaScript(replaceBodyJs).then(() => {
        this.runJs('window.scrollTo(0,0)');
      });
    });
  } else {
    // 从缓存恢复原始页面
    const restoreJs = `(function(){
      if (document.innerHTMLCache) {
        document.body.innerHTML = document.innerHTMLCache;
        document.body.classList.remove('mozac-readerview-body');
      }
      var s = document.getElementById('myapp_readerview_style'); if(s) s.remove();
      window.scrollTo(0,0);
    })()`;
    this.runJs(restoreJs);
  }
}
```

### 所需 rawfile 资源

| 文件 | 用途 |
|------|------|
| `MozReadability.js` | Mozilla Readability 解析器 |
| `readerview.css` | 阅读模式横排样式 |

> 加载大型 JS 文件时必须使用分块 `uint8ArrayToString()`，否则栈溢出。见 `webview-controller.md` 第 7 节。

## 4. 竖排文本模式（Vertical Text）

在阅读模式基础上叠加 CJK 竖排布局。实质是"阅读模式 + 竖排 CSS + CJK 文本处理"。

```typescript
private isVerticalText: boolean = false;

toggleVerticalText(): void {
  this.isVerticalText = !this.isVerticalText;
  if (this.isVerticalText) {
    // 1. 注入竖排阅读 CSS（替换横排版本）
    this.injectCssFromRawfile('verticalReaderview.css', 'myapp_readerview_style');

    // 2. 注入竖排布局 CSS
    const verticalLayoutCss =
      `body{-webkit-writing-mode:vertical-rl;writing-mode:vertical-rl;}` +
      `img{margin:10px;float:left;display:block;}`;
    this.injectCssString(verticalLayoutCss, 'myapp_vertical_layout');

    // 3. 加载 Readability → 解析 → 替换
    this.loadAndRunRawfile('MozReadability.js').then(() => {
      // ... 同阅读模式的替换逻辑 ...
      // 4. 加载 CJK 文本处理脚本
      this.loadAndRunRawfile('process_text_nodes.js').then(() => {
        this.runJs('window.scrollTo(0,0)');
      });
    });
    this.isReadMode = true;  // 竖排隐含阅读模式
  } else {
    this.isReadMode = false;
    this.webController.refresh();  // 关闭竖排：直接刷新恢复
  }
}
```

### 额外 rawfile 资源

| 文件 | 用途 |
|------|------|
| `verticalReaderview.css` | 阅读模式竖排样式 |
| `process_text_nodes.js` | CJK 竖排文本处理（日期转换、文字旋转） |

## 5. 分屏模式（Split Screen）

双 WebView 布局，核心挑战是两个 WebView 之间的通信。

### 状态变量

```typescript
@Local private isSplitScreen: boolean = false;
@Local private isSplitVertical: boolean = false;     // false=左右, true=上下
@Local private isSplitLinked: boolean = false;        // 右跟随左 URL
@Local private isSplitSyncScroll: boolean = false;    // 同步滚动
@Local private splitRatio: number = 0.5;              // 左侧比例 0.15~0.85
private splitWebController: webview.WebviewController = new webview.WebviewController();
```

### 分割条拖拽

使用 `PanGesture` + `onAreaChange` 获取容器尺寸，计算新比例：

```typescript
Column()
  .width(14)
  .gesture(
    PanGesture({ direction: PanDirection.Horizontal })
      .onActionStart(() => {
        this.splitDragStartRatio = this.splitRatio;
      })
      .onActionUpdate((event: GestureEvent) => {
        if (this.splitContainerSize > 0) {
          const delta = event.offsetX / this.splitContainerSize;
          this.splitRatio = Math.max(0.15, Math.min(0.85,
            this.splitDragStartRatio + delta
          ));
        }
      })
  )
```

### WebView 间通信（document.title 通道）

两个 WebView 之间无法直接通信。已验证的方案是借用 `document.title` 通道：

- **发送方**：通过 JS 设置 `document.title = '__MSG_TYPE__' + payload`
- **接收方**：在 `onTitleReceive` 回调中检测前缀，拦截处理，不更新真实标题

#### 同步滚动示例

```typescript
// 左侧注入 scroll 监听器
private setupSyncScroll(): void {
  const js = `(function(){
    if(window.__syncScroll) window.removeEventListener('scroll', window.__syncScroll);
    window.__syncScroll = function(){
      var pct = window.scrollY / (document.documentElement.scrollHeight - window.innerHeight || 1);
      document.title = '__SYNC_SCROLL__' + pct;
    };
    window.addEventListener('scroll', window.__syncScroll);
  })()`;
  this.runJs(js);
}

// 右侧 onTitleReceive 拦截
.onTitleReceive((event) => {
  if (event && event.title) {
    if (event.title.startsWith('__SYNC_SCROLL__') && this.isSplitSyncScroll) {
      const pct = parseFloat(event.title.replace('__SYNC_SCROLL__', ''));
      if (!isNaN(pct)) {
        const scrollJs = `window.scrollTo(0,(document.documentElement.scrollHeight-window.innerHeight)*${pct})`;
        this.splitWebController.runJavaScript(scrollJs).catch(() => {});
      }
    } else {
      this.title = event.title;  // 正常标题更新
    }
  }
})
```

#### URL 联动

```typescript
// 在主 WebView 的 onPageEnd 中
.onPageEnd(() => {
  if (this.isSplitScreen && this.isSplitLinked) {
    try { this.splitWebController.loadUrl(this.url); } catch (_e) {}
  }
})
```

### 工具栏自动收起

分屏工具栏按钮较多时，可设置超时自动收起为单个图标，点击再展开：

```typescript
private resetToolbarAutoHide(): void {
  clearTimeout(this.toolbarTimer);
  this.toolbarTimer = setTimeout(() => {
    this.toolbarExpanded = false;
  }, 3000) as number;
}
```

## 6. onPageEnd 中的模式重置

页面导航后，阅读模式和竖排模式应自动重置（新页面 DOM 不同，无法恢复解析结果），但其他 CSS 样式应重新注入：

```typescript
.onPageEnd(() => {
  // 重置内容替换类模式
  if (this.isReadMode || this.isVerticalText) {
    this.isReadMode = false;
    this.isVerticalText = false;
  }
  // 恢复 CSS 注入类样式
  this.reapplyStyles();
})
```

> 关键区分：**CSS 注入类样式**（粗体、颜色等）可以在任何页面重新注入；**内容替换类模式**（阅读、竖排）依赖特定页面的解析结果，不可跨页面恢复。
