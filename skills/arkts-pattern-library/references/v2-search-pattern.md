# 搜索功能完整参考（V2）

> 本项目锁 ArkTS V2，本文档为 V2 主参考。V1 历史写法见 [`search-pattern.md`](./search-pattern.md)。

## 完整实现：搜索框 + 防抖 + 搜索历史持久化 + 结果列表（V2）

```typescript
import { LengthMetrics } from '@kit.ArkUI'  // LengthMetrics 是 @kit.ArkUI 真实导出；用作值（LengthMetrics.vp(n)）必须 import，否则报 'only refers to a type, but is being used as a value'
import { preferences } from '@kit.ArkData'

// ===================== 搜索结果模型（V2） =====================
@ObservedV2
class SearchResult {
  id: string = ''
  @Trace title: string = ''
  @Trace description: string = ''

  static of(id: string, title: string, description: string): SearchResult {
    const r = new SearchResult()
    r.id = id
    r.title = title
    r.description = description
    return r
  }
}

// ===================== 搜索页面（V2） =====================
@Entry
@ComponentV2
struct SearchPage {
  @Local searchText: string = ''
  @Local searchHistory: string[] = []
  @Local searchResults: SearchResult[] = []
  @Local isSearching: boolean = false
  @Local showResults: boolean = false
  private debounceTimer: number = -1
  private preferencesName: string = 'search_prefs'
  private historyKey: string = 'search_history'
  private maxHistory: number = 20

  aboutToAppear(): void {
    this.loadHistory()
  }

  // ---- 搜索历史持久化 ----

  private async loadHistory(): Promise<void> {
    try {
      let context = getContext(this)
      let prefs = await preferences.getPreferences(context, this.preferencesName)
      let history = await prefs.get(this.historyKey, '[]')
      this.searchHistory = JSON.parse(history as string) as string[]
    } catch (e) {
      this.searchHistory = []
    }
  }

  private async saveHistory(): Promise<void> {
    try {
      let context = getContext(this)
      let prefs = await preferences.getPreferences(context, this.preferencesName)
      await prefs.put(this.historyKey, JSON.stringify(this.searchHistory))
      await prefs.flush()
    } catch (e) {
      // 保存失败静默处理
    }
  }

  private addToHistory(keyword: string): void {
    let trimmed = keyword.trim()
    if (trimmed.length === 0) {
      return
    }
    let existIndex = this.searchHistory.indexOf(trimmed)
    if (existIndex >= 0) {
      this.searchHistory.splice(existIndex, 1)
    }
    this.searchHistory.unshift(trimmed)
    if (this.searchHistory.length > this.maxHistory) {
      this.searchHistory = this.searchHistory.slice(0, this.maxHistory)
    }
    this.saveHistory()
  }

  private clearHistory(): void {
    this.searchHistory = []
    this.saveHistory()
  }

  // ---- 搜索逻辑（防抖） ----

  private debouncedSearch(keyword: string): void {
    if (this.debounceTimer !== -1) {
      clearTimeout(this.debounceTimer)
    }
    if (keyword.trim().length === 0) {
      this.showResults = false
      this.searchResults = []
      return
    }
    this.debounceTimer = setTimeout(() => {
      this.performSearch(keyword)
    }, 300)
  }

  // 也可改用 V2 @Monitor 监听 searchText（同等效果）：
  //
  //   @Monitor('searchText')
  //   onSearchTextChange(monitor: IMonitor): void {
  //     this.debouncedSearch(this.searchText)
  //   }

  private performSearch(keyword: string): void {
    this.isSearching = true
    this.showResults = true
    setTimeout(() => {
      let results: SearchResult[] = []
      for (let i = 0; i < 10; i++) {
        results.push(SearchResult.of(
          `result_${i}`,
          `${keyword} 相关结果 ${i + 1}`,
          `包含关键词「${keyword}」的搜索结果描述信息...`
        ))
      }
      this.searchResults = results
      this.isSearching = false
    }, 500)
  }

  private submitSearch(keyword: string): void {
    let trimmed = keyword.trim()
    if (trimmed.length === 0) {
      return
    }
    this.addToHistory(trimmed)
    if (this.debounceTimer !== -1) {
      clearTimeout(this.debounceTimer)
    }
    this.performSearch(trimmed)
  }

  build() {
    Column() {
      Row({ space: 10 }) {
        Search({ value: this.searchText, placeholder: '搜索内容...' })
          .layoutWeight(1)
          .height(40)
          .onChange((value: string) => {
            this.searchText = value
            this.debouncedSearch(value)
          })
          .onSubmit((value: string) => {
            this.submitSearch(value)
          })

        if (this.searchText.length > 0) {
          Text('取消')
            .fontSize(14)
            .fontColor('#667EEA')
            .onClick(() => {
              this.searchText = ''
              this.showResults = false
              this.searchResults = []
            })
        }
      }
      .width('100%')
      .padding({ left: 16, right: 16, top: 12, bottom: 12 })
      .backgroundColor(Color.White)

      if (this.showResults) {
        this.SearchResultsView()
      } else {
        this.SearchHistoryView()
      }
    }
    .width('100%')
    .height('100%')
    .backgroundColor('#F5F5F5')
  }

  @Builder
  SearchHistoryView() {
    if (this.searchHistory.length > 0) {
      Column({ space: 12 }) {
        Row() {
          Text('搜索历史')
            .fontSize(16)
            .fontWeight(FontWeight.Bold)
          Blank()
          Text('清空')
            .fontSize(14)
            .fontColor('#999999')
            .onClick(() => {
              this.clearHistory()
            })
        }
        .width('100%')

        Flex({ wrap: FlexWrap.Wrap, space: { main: LengthMetrics.vp(8), cross: LengthMetrics.vp(8) } }) {
          ForEach(this.searchHistory, (keyword: string) => {
            Text(keyword)
              .fontSize(13)
              .fontColor('#666666')
              .padding({ left: 12, right: 12, top: 6, bottom: 6 })
              .backgroundColor('#F0F0F0')
              .borderRadius(16)
              .onClick(() => {
                this.searchText = keyword
                this.submitSearch(keyword)
              })
          }, (keyword: string, index: number) => `${keyword}_${index}`)
        }
        .width('100%')
      }
      .padding(16)
    } else {
      Column() {
        Text('暂无搜索历史')
          .fontSize(14)
          .fontColor('#CCCCCC')
          .margin({ top: 80 })
      }
      .width('100%')
    }
  }

  @Builder
  SearchResultsView() {
    if (this.isSearching) {
      Column({ space: 12 }) {
        LoadingProgress().width(36).height(36)
        Text('搜索中...')
          .fontSize(14)
          .fontColor('#999999')
      }
      .width('100%')
      .height('50%')
      .justifyContent(FlexAlign.Center)
    } else if (this.searchResults.length === 0) {
      Column() {
        Text('无搜索结果')
          .fontSize(16)
          .fontColor('#999999')
          .margin({ top: 80 })
      }
      .width('100%')
    } else {
      List({ space: 1 }) {
        ForEach(this.searchResults, (item: SearchResult) => {
          ListItem() {
            Column({ space: 6 }) {
              Text(item.title)
                .fontSize(16)
                .fontWeight(FontWeight.Medium)
                .maxLines(1)
                .textOverflow({ overflow: TextOverflow.Ellipsis })
              Text(item.description)
                .fontSize(13)
                .fontColor('#999999')
                .maxLines(2)
                .textOverflow({ overflow: TextOverflow.Ellipsis })
            }
            .width('100%')
            .padding(16)
            .backgroundColor(Color.White)
            .alignItems(HorizontalAlign.Start)
          }
        }, (item: SearchResult) => item.id)
      }
      .width('100%')
      .layoutWeight(1)
      .divider({ strokeWidth: 0.5, color: '#F0F0F0', startMargin: 16, endMargin: 16 })
    }
  }
}
```

---

## V2 关键变更对照（vs V1）

| 位置 | V1 | V2 |
|---|---|---|
| 入口 struct | `@Entry @Component` | `@Entry @ComponentV2` |
| 状态变量 | `@State searchText: string = ''` | `@Local searchText: string = ''` |
| 搜索结果模型 | `interface SearchResult` | `@ObservedV2 class SearchResult { @Trace ... }` |
| 监听文本变化 | 在 `Search.onChange` 内手动调防抖 | 同左；或用 `@Monitor('searchText')` 方法 |

> 防抖搜索可用两种 V2 风格：
>
> 1. **保留 `Search.onChange` 调用 `debouncedSearch`**（与 V1 风格一致）—— 推荐，路径清晰
> 2. **`@Monitor('searchText')` 方法响应**—— 更"声明式"，但方法签名带 `IMonitor` 参数稍重
>
> 两种等价，团队风格统一即可。
