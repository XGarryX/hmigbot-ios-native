# 标签页管理、页内搜索与 URL/Title 同步

## 1. URL/Title 实时捕获

WebView 回调自动同步当前页面信息，这是所有后续功能（书签、历史、标签页、分享）的数据基础。

```typescript
.onPageBegin((event) => {
  if (event && event.url) {
    this.url = event.url;
    this.inputUrl = event.url;    // 更新地址栏显示
    this.isLoading = true;
  }
})

.onTitleReceive((event) => {
  if (event && event.title) {
    this.title = event.title;
  }
})

.onPageEnd(() => {
  this.isLoading = false;
  this.updateCurrentAlbum(this.url, this.title);
  this.updateNavigationState();
  this.reapplyStyles();
})
```

### 同步到标签页和 ViewModel

```typescript
updateCurrentAlbum(url: string, title: string): void {
  this.viewModel.setCurrentUrl(url);
  this.viewModel.setCurrentTitle(title);
  const album = this.albumManager.getCurrentAlbum();
  if (album) {
    album.updateUrl(url);
    album.updateTitle(title || 'Default Title');
  }
  this.albums = this.albumManager.getAllAlbums();  // 刷新列表
}
```

## 2. 标签页管理（AlbumManager 模式）

### 数据结构

每个标签页是一个 Album 对象，持有 URL、标题和可选的独立 WebviewController：

```typescript
export class AlbumControllerImpl {
  id: string;
  url: string;
  title: string;
  progress: number;
  favicon: string;
  private webController: webview.WebviewController | null = null;

  setWebController(controller: webview.WebviewController): void { ... }
  getWebController(): webview.WebviewController | null { ... }
  updateUrl(url: string): void { ... }
  updateTitle(title: string): void { ... }
}

export class AlbumManager {
  private albums: AlbumControllerImpl[] = [];
  private currentIndex: number = 0;
  private maxAlbums: number = 50;

  createAlbum(url?: string, title?: string): AlbumControllerImpl { ... }
  getCurrentAlbum(): AlbumControllerImpl | null { ... }
  switchToAlbum(index: number): boolean { ... }
  removeAlbum(album: AlbumControllerImpl): boolean { ... }
  getAllAlbums(): AlbumControllerImpl[] { ... }
}
```

### 新建标签页

```typescript
newTab(): void {
  const album = this.albumManager.createAlbum('about:blank', 'New Tab');
  this.albums = this.albumManager.getAllAlbums();
  this.currentIndex = this.albumManager.getCurrentIndex();
  this.url = 'about:blank';
  this.title = 'New Tab';
  if (album) {
    album.setWebController(this.webController);
  }
  this.showTabOverview = false;
}
```

### 切换标签页

```typescript
selectTab(index: number): void {
  this.albumManager.switchToAlbum(index);
  const album = this.albumManager.getCurrentAlbum();
  if (album) {
    this.url = album.url;
    this.title = album.title;
    this.webController.loadUrl(album.url);
  }
  this.currentIndex = this.albumManager.getCurrentIndex();
  this.showTabOverview = false;
  this.updateNavigationState();
}
```

> **共享 Controller vs 独立 Controller**：上面的实现所有标签共享同一个 WebviewController，切换时通过 `loadUrl` 重新加载。如果需要保持每个标签的滚动位置和 DOM 状态，应为每个标签创建独立的 Controller 和 Web 组件。

## 3. 导航状态更新

在每次页面加载完成或标签切换后更新前进/后退按钮状态：

```typescript
updateNavigationState(): void {
  this.canGoBack = this.webController.accessBackward();
  this.canGoForward = this.webController.accessForward();
}
```

## 4. 书签/历史数据源

当前 URL 和标题从 WebView 回调实时同步，用于：
- 添加书签时预填 URL/标题
- 保存到历史记录
- 分享当前页面
- 保存存档文件时的文件名

无需额外查询 — 直接使用 `this.url` 和 `this.title` 即可。

## 5. 页内搜索（Find in Page）

### 状态变量

```typescript
@Local private showFindBar: boolean = false;
@Local private findQuery: string = '';
private lastFindQuery: string = '';    // 区分"首次搜索"和"跳到下一个"
```

### 打开/关闭

```typescript
openFindBar(): void {
  this.showFindBar = true;
  this.findQuery = '';
  this.lastFindQuery = '';
}

hideFindBar(): void {
  this.showFindBar = false;
  this.findQuery = '';
  this.lastFindQuery = '';
  try { this.webController.searchAllAsync(''); } catch (_e) {}  // 清除高亮
}
```

### 实时搜索（输入即高亮）

```typescript
onQueryChange: (query: string) => {
  this.findQuery = query;
  if (query) {
    this.lastFindQuery = query;
    try { this.webController.searchAllAsync(query); } catch (_e) {}
  } else {
    this.lastFindQuery = '';
    try { this.webController.searchAllAsync(''); } catch (_e) {}
  }
}
```

### 上一个/下一个

关键逻辑：如果关键词变了，用 `searchAllAsync` 重新搜索；如果相同，用 `searchNext` 跳转。

```typescript
findNext(query: string): void {
  if (!query) return;
  try {
    if (query !== this.lastFindQuery) {
      this.lastFindQuery = query;
      this.webController.searchAllAsync(query);
    } else {
      this.webController.searchNext(true);
    }
  } catch (_e) {}
}

findPrev(query: string): void {
  if (!query) return;
  try {
    if (query !== this.lastFindQuery) {
      this.lastFindQuery = query;
      this.webController.searchAllAsync(query);
    } else {
      this.webController.searchNext(false);
    }
  } catch (_e) {}
}
```

### FindBar 组件

```typescript
@ComponentV2
export struct FindBar {
  @Local query: string = '';

  @Event onQueryChange: (query: string) => void = () => {};
  @Event onFindNext: (query: string) => void = () => {};
  @Event onFindPrev: (query: string) => void = () => {};
  @Event onClose: () => void = () => {};

  build() {
    Row() {
      TextInput({ text: this.query, placeholder: '搜索页面内容...' })
        .layoutWeight(1).height(40)
        .onChange((value: string) => { this.query = value; this.onQueryChange(value); })
        .onSubmit(() => { this.onFindNext(this.query); })

      Button() { SymbolGlyph($r('sys.symbol.chevron_up')) }
        .onClick(() => { this.onFindPrev(this.query); })

      Button() { SymbolGlyph($r('sys.symbol.chevron_down')) }
        .onClick(() => { this.onFindNext(this.query); })

      Button() { SymbolGlyph($r('sys.symbol.xmark')) }
        .onClick(() => { this.onClose(); })
    }
  }
}
```

## 6. WebView 搜索 API 速查

| API | 用途 |
|-----|------|
| `searchAllAsync(query)` | 高亮页面中所有匹配项 |
| `searchAllAsync('')` | 清除所有搜索高亮 |
| `searchNext(true)` | 跳到下一个匹配项 |
| `searchNext(false)` | 跳到上一个匹配项 |
