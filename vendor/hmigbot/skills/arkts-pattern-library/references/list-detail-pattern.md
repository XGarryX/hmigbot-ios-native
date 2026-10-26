# 列表-详情模式完整参考（**V1 历史文档 — Legacy**）

> ⚠️ **本项目锁 ArkTS V2**。本文档为 **V1 历史参考**（`@Component / @State` 等），仅用于阅读老代码或迁移老项目时查阅。
>
> **新代码请使用 V2 装饰器**：参阅 [`v2-list-detail-pattern.md`](./v2-list-detail-pattern.md)（V2 主参考）和 [`../SKILL.md`](../SKILL.md)。

---

## 完整实现：列表分页加载 + 下拉刷新 + 详情页 + 状态管理

```typescript
// ===================== 数据源 =====================
// BasicDataSource 实现 IDataSource 接口，配合 LazyForEach 实现按需加载
class BasicDataSource<T> implements IDataSource {
  private listeners: DataChangeListener[] = []
  private dataArray: T[] = []

  totalCount(): number {
    return this.dataArray.length
  }

  getData(index: number): T {
    return this.dataArray[index]
  }

  // 整体替换数据（用于刷新）
  reloadData(data: T[]): void {
    this.dataArray = data
    this.notifyDataReload()
  }

  // 追加数据（用于分页加载）
  appendData(data: T[]): void {
    let startIndex = this.dataArray.length
    this.dataArray = this.dataArray.concat(data)
    // 逐条通知新增，确保 LazyForEach 正确渲染
    data.forEach((_, i) => {
      this.notifyDataAdd(startIndex + i)
    })
  }

  registerDataChangeListener(listener: DataChangeListener): void {
    if (this.listeners.indexOf(listener) < 0) {
      this.listeners.push(listener)
    }
  }

  unregisterDataChangeListener(listener: DataChangeListener): void {
    const index = this.listeners.indexOf(listener)
    if (index >= 0) {
      this.listeners.splice(index, 1)
    }
  }

  private notifyDataReload(): void {
    this.listeners.forEach(listener => listener.onDataReloaded())
  }

  private notifyDataAdd(index: number): void {
    this.listeners.forEach(listener => listener.onDataAdd(index))
  }
}

// ===================== 数据模型 =====================
interface ArticleItem {
  id: string
  title: string
  summary: string
  author: string
  date: string
  content: string
}

// ===================== 页面状态枚举 =====================
enum PageState {
  LOADING,   // 加载中
  SUCCESS,   // 加载成功
  ERROR,     // 加载失败
  EMPTY      // 无数据
}

// ===================== 列表页 =====================
@Component
struct ArticleListPage {
  @State pageState: PageState = PageState.LOADING
  @State isRefreshing: boolean = false
  @State isLoadingMore: boolean = false
  @State currentPage: number = 1
  @State hasMore: boolean = true
  private dataSource: BasicDataSource<ArticleItem> = new BasicDataSource()
  private pageSize: number = 15

  aboutToAppear(): void {
    this.loadData(true)
  }

  // 模拟加载数据（替换为真实 API 调用）
  private loadData(isRefresh: boolean): void {
    if (isRefresh) {
      this.currentPage = 1
      this.pageState = PageState.LOADING
    }
    // 模拟网络请求延迟
    setTimeout(() => {
      let newItems: ArticleItem[] = []
      for (let i = 0; i < this.pageSize; i++) {
        let idx = (this.currentPage - 1) * this.pageSize + i
        newItems.push({
          id: `article_${idx}`,
          title: `文章标题 ${idx + 1}`,
          summary: `这是文章 ${idx + 1} 的摘要内容，介绍文章的主要内容...`,
          author: `作者 ${idx % 5 + 1}`,
          date: '2024-01-15',
          content: `这是文章 ${idx + 1} 的完整内容。包含详细的技术介绍和代码示例。`
        } as ArticleItem)
      }

      if (isRefresh) {
        this.dataSource.reloadData(newItems)
        this.isRefreshing = false
      } else {
        this.dataSource.appendData(newItems)
        this.isLoadingMore = false
      }

      this.hasMore = this.currentPage < 5 // 模拟总共 5 页
      this.pageState = this.dataSource.totalCount() > 0 ? PageState.SUCCESS : PageState.EMPTY
    }, 1000)
  }

  build() {
    NavDestination() {
      if (this.pageState === PageState.LOADING && this.currentPage === 1) {
        // 首次加载状态
        this.LoadingView()
      } else if (this.pageState === PageState.ERROR) {
        // 错误状态
        this.ErrorView()
      } else if (this.pageState === PageState.EMPTY) {
        // 空状态
        this.EmptyView()
      } else {
        // 正常列表
        Refresh({ refreshing: $$this.isRefreshing }) {
          List({ space: 8 }) {
            LazyForEach(this.dataSource, (item: ArticleItem) => {
              ListItem() {
                this.ArticleCard(item)
              }
            }, (item: ArticleItem) => item.id)

            // 加载更多指示器
            if (this.hasMore) {
              ListItem() {
                Row() {
                  LoadingProgress().width(24).height(24)
                  Text('加载中...')
                    .fontSize(14)
                    .fontColor('#999999')
                    .margin({ left: 8 })
                }
                .width('100%')
                .height(50)
                .justifyContent(FlexAlign.Center)
              }
            }
          }
          .width('100%')
          .height('100%')
          .padding({ left: 12, right: 12 })
          .cachedCount(5)
          .onReachEnd(() => {
            // 触底加载更多
            if (this.hasMore && !this.isLoadingMore) {
              this.isLoadingMore = true
              this.currentPage++
              this.loadData(false)
            }
          })
        }
        .onRefreshing(() => {
          // 下拉刷新
          this.loadData(true)
        })
      }
    }
    .title('文章列表')
    .backgroundColor('#F5F5F5')
  }

  @Builder
  ArticleCard(item: ArticleItem) {
    Column({ space: 8 }) {
      Text(item.title)
        .fontSize(17)
        .fontWeight(FontWeight.Bold)
        .maxLines(2)
        .textOverflow({ overflow: TextOverflow.Ellipsis })
      Text(item.summary)
        .fontSize(14)
        .fontColor('#666666')
        .maxLines(2)
        .textOverflow({ overflow: TextOverflow.Ellipsis })
      Row() {
        Text(item.author)
          .fontSize(12)
          .fontColor('#999999')
        Blank()
        Text(item.date)
          .fontSize(12)
          .fontColor('#999999')
      }
      .width('100%')
    }
    .width('100%')
    .padding(16)
    .backgroundColor(Color.White)
    .borderRadius(10)
    .shadow({ radius: 4, color: '#0A000000', offsetY: 1 })
    .onClick(() => {
      // 跳转详情页，传递文章 ID：NavDestination 子组件用 queryNavigationInfo 抓 Navigation 栈（API 12+）
      // 不要 getRouter() as NavPathStack —— getRouter() 返回 @ohos.router 的 Router，与 NavPathStack 类型不重叠，强转编译报错
      let pathStack: NavPathStack | undefined = this.queryNavigationInfo()?.pathStack
      pathStack?.pushPath({ name: 'ArticleDetail', param: item })
    })
  }

  @Builder
  LoadingView() {
    Column({ space: 12 }) {
      LoadingProgress().width(48).height(48)
      Text('加载中...')
        .fontSize(14)
        .fontColor('#999999')
    }
    .width('100%')
    .height('100%')
    .justifyContent(FlexAlign.Center)
  }

  @Builder
  ErrorView() {
    Column({ space: 16 }) {
      Text('加载失败')
        .fontSize(18)
        .fontColor('#999999')
      Button('重试')
        .onClick(() => {
          this.loadData(true)
        })
    }
    .width('100%')
    .height('100%')
    .justifyContent(FlexAlign.Center)
  }

  @Builder
  EmptyView() {
    Column({ space: 12 }) {
      Text('暂无数据')
        .fontSize(18)
        .fontColor('#CCCCCC')
      Text('下拉刷新试试')
        .fontSize(14)
        .fontColor('#999999')
    }
    .width('100%')
    .height('100%')
    .justifyContent(FlexAlign.Center)
  }
}

// ===================== 详情页 =====================
@Component
struct ArticleDetailPage {
  @State article: ArticleItem | null = null

  build() {
    NavDestination() {
      if (this.article) {
        Scroll() {
          Column({ space: 16 }) {
            Text(this.article.title)
              .fontSize(24)
              .fontWeight(FontWeight.Bold)
              .width('100%')

            Row({ space: 8 }) {
              Text(this.article.author)
                .fontSize(14)
                .fontColor('#667EEA')
              Text('|')
                .fontSize(14)
                .fontColor('#CCCCCC')
              Text(this.article.date)
                .fontSize(14)
                .fontColor('#999999')
            }

            Divider().color('#F0F0F0')

            Text(this.article.content)
              .fontSize(16)
              .lineHeight(28)
              .fontColor('#333333')
          }
          .padding(20)
          .width('100%')
        }
        .width('100%')
        .height('100%')
      } else {
        Column() {
          Text('文章不存在')
            .fontSize(16)
            .fontColor('#999999')
        }
        .width('100%')
        .height('100%')
        .justifyContent(FlexAlign.Center)
      }
    }
    .title('文章详情')
    .onReady((context: NavDestinationContext) => {
      // 从路由参数获取文章数据
      this.article = context.pathInfo.param as ArticleItem
    })
  }
}

// ===================== 导航入口 =====================
@Entry
@Component
struct ListDetailEntry {
  private navStack: NavPathStack = new NavPathStack()

  @Builder
  routerMap(name: string) {
    if (name === 'ArticleList') {
      ArticleListPage()
    } else if (name === 'ArticleDetail') {
      ArticleDetailPage()
    }
  }

  build() {
    Navigation(this.navStack) {
      ArticleListPage()
    }
    .navDestination(this.routerMap)
    .mode(NavigationMode.Stack)
  }
}
```
