# 列表-详情模式完整参考（V2）

> 本项目锁 ArkTS V2，本文档为 V2 主参考。V1 历史写法见 [`list-detail-pattern.md`](./list-detail-pattern.md)。

## 完整实现：列表分页加载 + 下拉刷新 + 详情页 + 状态管理（V2）

```typescript
// ===================== 数据源 =====================
// BasicDataSource 实现 IDataSource 接口，配合 LazyForEach 实现按需加载
// 与 V1 一致 — IDataSource 与装饰器无关
class BasicDataSource<T> implements IDataSource {
  private listeners: DataChangeListener[] = []
  private dataArray: T[] = []

  totalCount(): number {
    return this.dataArray.length
  }

  getData(index: number): T {
    return this.dataArray[index]
  }

  reloadData(data: T[]): void {
    this.dataArray = data
    this.notifyDataReload()
  }

  appendData(data: T[]): void {
    let startIndex = this.dataArray.length
    this.dataArray = this.dataArray.concat(data)
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

// ===================== 数据模型（V2 用 @ObservedV2 + @Trace） =====================
// @Trace 只加在驱动 UI 渲染的字段上；内部标识（如下 id）与 VM 内部记账字段（请求计数器/
// 重试次数/非渲染标志）用普通字段、不加 @Trace（自增不触发刷新）。判定规则与范例见
// references/v2-performance-patterns.md §3。
@ObservedV2
class ArticleItem {
  id: string = ''
  @Trace title: string = ''
  @Trace summary: string = ''
  @Trace author: string = ''
  @Trace date: string = ''
  @Trace content: string = ''

  static create(id: string, title: string, summary: string, author: string, date: string, content: string): ArticleItem {
    const item = new ArticleItem()
    item.id = id
    item.title = title
    item.summary = summary
    item.author = author
    item.date = date
    item.content = content
    return item
  }
}

// ===================== 页面状态枚举 =====================
enum PageState {
  LOADING,
  SUCCESS,
  ERROR,
  EMPTY
}

// ===================== 列表页（V2） =====================
@ComponentV2
struct ArticleListPage {
  @Local pageState: PageState = PageState.LOADING
  @Local isRefreshing: boolean = false
  @Local isLoadingMore: boolean = false
  @Local currentPage: number = 1
  @Local hasMore: boolean = true
  private dataSource: BasicDataSource<ArticleItem> = new BasicDataSource<ArticleItem>()
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
    setTimeout(() => {
      let newItems: ArticleItem[] = []
      for (let i = 0; i < this.pageSize; i++) {
        let idx = (this.currentPage - 1) * this.pageSize + i
        newItems.push(ArticleItem.create(
          `article_${idx}`,
          `文章标题 ${idx + 1}`,
          `这是文章 ${idx + 1} 的摘要内容，介绍文章的主要内容...`,
          `作者 ${idx % 5 + 1}`,
          '2024-01-15',
          `这是文章 ${idx + 1} 的完整内容。包含详细的技术介绍和代码示例。`
        ))
      }

      if (isRefresh) {
        this.dataSource.reloadData(newItems)
        this.isRefreshing = false
      } else {
        this.dataSource.appendData(newItems)
        this.isLoadingMore = false
      }

      this.hasMore = this.currentPage < 5
      this.pageState = this.dataSource.totalCount() > 0 ? PageState.SUCCESS : PageState.EMPTY
    }, 1000)
  }

  build() {
    NavDestination() {
      if (this.pageState === PageState.LOADING && this.currentPage === 1) {
        this.LoadingView()
      } else if (this.pageState === PageState.ERROR) {
        this.ErrorView()
      } else if (this.pageState === PageState.EMPTY) {
        this.EmptyView()
      } else {
        Refresh({ refreshing: $$this.isRefreshing }) {
          List({ space: 8 }) {
            LazyForEach(this.dataSource, (item: ArticleItem) => {
              ListItem() {
                this.ArticleCard(item)
              }
            }, (item: ArticleItem) => item.id)

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
            if (this.hasMore && !this.isLoadingMore) {
              this.isLoadingMore = true
              this.currentPage++
              this.loadData(false)
            }
          })
        }
        .onRefreshing(() => {
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
      // NavDestination 子组件用 queryNavigationInfo 抓 Navigation 栈（API 12+）
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

// ===================== 详情页（V2） =====================
@ComponentV2
struct ArticleDetailPage {
  @Local article: ArticleItem | null = null

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
      this.article = context.pathInfo.param as ArticleItem
    })
  }
}

// ===================== 导航入口（V2） =====================
@Entry
@ComponentV2
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

---

## V2 关键变更对照（vs V1）

| 位置 | V1 | V2 |
|---|---|---|
| 列表页 struct | `@Component struct ArticleListPage` | `@ComponentV2 struct ArticleListPage` |
| 状态变量 | `@State pageState: PageState = ...` | `@Local pageState: PageState = ...` |
| 数据模型 | `interface ArticleItem`（不可观察） | `@ObservedV2 class ArticleItem { @Trace ... }` |
| 详情接收路由参数 | `@State article: ArticleItem \| null = null` | `@Local article: ArticleItem \| null = null` |
| 入口页 | `@Entry @Component` | `@Entry @ComponentV2` |

`Refresh({ refreshing: $$this.isRefreshing })` 的双向语法是内置组件的能力（不依赖 V1/V2 装饰器），V2 中仍可直接使用。

如需父子组件互传刷新状态（V1 用 `@Link`），V2 改为 `@Param + @Event` 回调：

```typescript
// 父
@ComponentV2
struct PageA {
  @Local refreshing: boolean = false
  build() {
    RefreshControl({
      refreshing: this.refreshing,
      onRefreshingChange: (v: boolean) => { this.refreshing = v }
    })
  }
}

// 子
@ComponentV2
struct RefreshControl {
  @Param refreshing: boolean = false
  @Event onRefreshingChange: (v: boolean) => void = () => {}
  build() {
    Refresh({ refreshing: $$this.refreshing })
      .onRefreshing(() => { this.onRefreshingChange(true) })
  }
}
```
