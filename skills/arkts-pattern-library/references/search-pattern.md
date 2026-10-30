# 搜索功能完整参考（**V1 历史文档 — Legacy**）

> ⚠️ **本项目锁 ArkTS V2**。本文档为 **V1 历史参考**（`@Component / @State` 等），仅用于阅读老代码或迁移老项目时查阅。
>
> **新代码请使用 V2 装饰器**：参阅 [`v2-search-pattern.md`](./v2-search-pattern.md)（V2 主参考）和 [`../SKILL.md`](../SKILL.md)。

---

## 完整实现：搜索框 + 防抖 + 搜索历史持久化 + 结果列表

```typescript
import { LengthMetrics } from '@kit.ArkUI'  // 用作值（LengthMetrics.vp(n)）须 import，否则 'only refers to a type, used as value'
import { preferences } from '@kit.ArkData'

// ===================== 搜索结果模型 =====================
interface SearchResult {
  id: string
  title: string
  description: string
}

// ===================== 搜索页面 =====================
@Entry
@Component
struct SearchPage {
  @State searchText: string = ''
  @State searchHistory: string[] = []
  @State searchResults: SearchResult[] = []
  @State isSearching: boolean = false
  @State showResults: boolean = false
  private debounceTimer: number = -1
  private preferencesName: string = 'search_prefs'
  private historyKey: string = 'search_history'
  private maxHistory: number = 20

  aboutToAppear(): void {
    this.loadHistory()
  }

  // ---- 搜索历史持久化 ----

  // 从 Preferences 加载搜索历史
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

  // 保存搜索历史到 Preferences
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

  // 添加搜索词到历史记录
  private addToHistory(keyword: string): void {
    let trimmed = keyword.trim()
    if (trimmed.length === 0) {
      return
    }
    // 去重：如果已存在则移到最前
    let existIndex = this.searchHistory.indexOf(trimmed)
    if (existIndex >= 0) {
      this.searchHistory.splice(existIndex, 1)
    }
    this.searchHistory.unshift(trimmed)
    // 超过上限则删除最旧的
    if (this.searchHistory.length > this.maxHistory) {
      this.searchHistory = this.searchHistory.slice(0, this.maxHistory)
    }
    this.saveHistory()
  }

  // 清空搜索历史
  private clearHistory(): void {
    this.searchHistory = []
    this.saveHistory()
  }

  // ---- 搜索逻辑 ----

  // 防抖搜索：用户停止输入 300ms 后才执行搜索
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

  // 执行搜索（替换为真实 API 调用）
  private performSearch(keyword: string): void {
    this.isSearching = true
    this.showResults = true
    // 模拟网络请求
    setTimeout(() => {
      let results: SearchResult[] = []
      for (let i = 0; i < 10; i++) {
        results.push({
          id: `result_${i}`,
          title: `${keyword} 相关结果 ${i + 1}`,
          description: `包含关键词「${keyword}」的搜索结果描述信息...`
        } as SearchResult)
      }
      this.searchResults = results
      this.isSearching = false
    }, 500)
  }

  // 提交搜索（用户点击搜索按钮或回车时）
  private submitSearch(keyword: string): void {
    let trimmed = keyword.trim()
    if (trimmed.length === 0) {
      return
    }
    this.addToHistory(trimmed)
    // 清除防抖定时器，立即搜索
    if (this.debounceTimer !== -1) {
      clearTimeout(this.debounceTimer)
    }
    this.performSearch(trimmed)
  }

  // ---- UI 构建 ----

  build() {
    Column() {
      // 搜索栏
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
        // 搜索结果
        this.SearchResultsView()
      } else {
        // 搜索历史
        this.SearchHistoryView()
      }
    }
    .width('100%')
    .height('100%')
    .backgroundColor('#F5F5F5')
  }

  // 搜索历史视图
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

        // 使用 Flex wrap 布局显示历史标签
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

  // 搜索结果视图
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
