# ArkTS V2 数据源模式参考

> 本文档基于 **ArkTS V2（API 12+）** 装饰器体系。本项目锁 V2，本文档为主参考。V1 历史写法见 [`datasource-patterns.md`](./datasource-patterns.md)（已加 legacy 标识）。
>
> 完整的 V2 数据源模式，涵盖 BasicDataSource / PaginatedDataSource / FilteredDataSource 实现、与 LazyForEach 配合、以及 V2 新推荐的 `Repeat<T>` 替代方案。
>
> **重要**：`BasicDataSource / PaginatedDataSource / FilteredDataSource` 等数据源类**实现本身不依赖装饰器**，可直接复用 V1 实现。本文档重点在于 V2 中如何配合 `@ObservedV2 + @Trace` Model 与 `@ComponentV2 + @Local + @Param` 组件使用。

---

## 1. BasicDataSource 完整实现（V1/V2 通用）

`IDataSource` 是 LazyForEach 要求的数据源接口。`BasicDataSource` 是对该接口的通用封装，提供增删改查和监听器通知。**实现与 V1 完全一致**。

```typescript
// ==========================================
// BasicDataSource<T> —— 通用数据源基类
// 实现 IDataSource 接口，供 LazyForEach 使用
// ==========================================

export class BasicDataSource<T> implements IDataSource {
  private dataArray: T[] = []
  private listeners: DataChangeListener[] = []

  // ---- IDataSource 接口方法 ----

  totalCount(): number {
    return this.dataArray.length
  }

  getData(index: number): T {
    return this.dataArray[index]
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

  // ---- 通知方法 ----

  notifyDataReloaded(): void {
    this.listeners.forEach((listener: DataChangeListener) => {
      listener.onDataReloaded()
    })
  }

  notifyDataAdd(index: number): void {
    this.listeners.forEach((listener: DataChangeListener) => {
      listener.onDataAdd(index)
    })
  }

  notifyDataChange(index: number): void {
    this.listeners.forEach((listener: DataChangeListener) => {
      listener.onDataChange(index)
    })
  }

  notifyDataDelete(index: number): void {
    this.listeners.forEach((listener: DataChangeListener) => {
      listener.onDataDelete(index)
    })
  }

  notifyDataMove(from: number, to: number): void {
    this.listeners.forEach((listener: DataChangeListener) => {
      listener.onDataMove(from, to)
    })
  }

  // ---- CRUD 操作 ----

  pushData(data: T): void {
    this.dataArray.push(data)
    this.notifyDataAdd(this.dataArray.length - 1)
  }

  pushDataArray(dataList: T[]): void {
    let startIndex = this.dataArray.length
    for (let item of dataList) {
      this.dataArray.push(item)
    }
    // 批量新增逐个通知 add（保证 LazyForEach 局部刷新）
    for (let i = startIndex; i < this.dataArray.length; i++) {
      this.notifyDataAdd(i)
    }
  }

  insertData(index: number, data: T): void {
    if (index >= 0 && index <= this.dataArray.length) {
      this.dataArray.splice(index, 0, data)
      this.notifyDataAdd(index)
    }
  }

  updateData(index: number, data: T): void {
    if (index >= 0 && index < this.dataArray.length) {
      this.dataArray[index] = data
      this.notifyDataChange(index)
    }
  }

  deleteData(index: number): void {
    if (index >= 0 && index < this.dataArray.length) {
      this.dataArray.splice(index, 1)
      this.notifyDataDelete(index)
    }
  }

  moveData(from: number, to: number): void {
    if (from >= 0 && from < this.dataArray.length &&
        to >= 0 && to < this.dataArray.length && from !== to) {
      let item = this.dataArray[from]
      this.dataArray.splice(from, 1)
      this.dataArray.splice(to, 0, item)
      this.notifyDataMove(from, to)
    }
  }

  clearData(): void {
    this.dataArray = []
    this.notifyDataReloaded()
  }

  reloadData(dataList: T[]): void {
    this.dataArray = dataList
    this.notifyDataReloaded()
  }

  getAllData(): T[] {
    return [...this.dataArray]
  }

  indexOf(predicate: (item: T) => boolean): number {
    for (let i = 0; i < this.dataArray.length; i++) {
      if (predicate(this.dataArray[i])) {
        return i
      }
    }
    return -1
  }
}
```

**V2 中使用示例：**

```typescript
import { BasicDataSource } from './BasicDataSource'

@ObservedV2
class ArticleModel {
  @Trace id: number = 0
  @Trace title: string = ''
  @Trace summary: string = ''

  constructor(id: number, title: string, summary: string) {
    this.id = id
    this.title = title
    this.summary = summary
  }
}

@Entry
@ComponentV2
struct ArticleListPage {
  private dataSource: BasicDataSource<ArticleModel> = new BasicDataSource<ArticleModel>()

  aboutToAppear(): void {
    let articles: ArticleModel[] = []
    for (let i = 1; i <= 50; i++) {
      articles.push(new ArticleModel(i, `文章标题 ${i}`, `这是第${i}篇文章的摘要`))
    }
    this.dataSource.reloadData(articles)
  }

  build() {
    List() {
      LazyForEach(this.dataSource, (item: ArticleModel) => {
        ListItem() {
          Column() {
            Text(item.title)
              .fontSize(16)
              .fontWeight(FontWeight.Bold)
            Text(item.summary)
              .fontSize(14)
              .fontColor('#666666')
          }
          .padding(12)
          .width('100%')
          .alignItems(HorizontalAlign.Start)
        }
      }, (item: ArticleModel) => item.id.toString())
    }
  }
}
```

---

## 2. 分页数据源（PaginatedDataSource）

继承 BasicDataSource，增加分页加载能力。**实现本身与 V1 一致**，V2 中使用时配合 `@Local` 持有数据源。

```typescript
type PageFetcher<T> = (page: number, pageSize: number) => Promise<T[]>

export class PaginatedDataSource<T> extends BasicDataSource<T> {
  private currentPage: number = 0
  private pageSize: number = 20
  private _hasMore: boolean = true
  private _isLoading: boolean = false
  private fetcher: PageFetcher<T>

  constructor(fetcher: PageFetcher<T>, pageSize: number = 20) {
    super()
    this.fetcher = fetcher
    this.pageSize = pageSize
  }

  get hasMore(): boolean {
    return this._hasMore
  }

  get isLoading(): boolean {
    return this._isLoading
  }

  async reload(): Promise<void> {
    if (this._isLoading) {
      return
    }
    this._isLoading = true
    this.currentPage = 1
    this._hasMore = true

    try {
      let data = await this.fetcher(this.currentPage, this.pageSize)
      this.reloadData(data)
      if (data.length < this.pageSize) {
        this._hasMore = false
      }
    } catch (error) {
      console.error(`分页加载失败: ${JSON.stringify(error)}`)
    } finally {
      this._isLoading = false
    }
  }

  async loadMore(): Promise<void> {
    if (this._isLoading || !this._hasMore) {
      return
    }
    this._isLoading = true

    try {
      let nextPage = this.currentPage + 1
      let data = await this.fetcher(nextPage, this.pageSize)
      if (data.length > 0) {
        this.currentPage = nextPage
        this.pushDataArray(data)
      }
      if (data.length < this.pageSize) {
        this._hasMore = false
      }
    } catch (error) {
      console.error(`加载更多失败: ${JSON.stringify(error)}`)
    } finally {
      this._isLoading = false
    }
  }

  getCurrentPage(): number {
    return this.currentPage
  }

  reset(): void {
    this.currentPage = 0
    this._hasMore = true
    this._isLoading = false
    this.clearData()
  }
}
```

**V2 使用示例（含下拉刷新 + 上拉加载）：**

```typescript
import { PaginatedDataSource } from './PaginatedDataSource'
import { http } from '@kit.NetworkKit'

@ObservedV2
class NewsItem {
  @Trace id: number = 0
  @Trace title: string = ''
  @Trace content: string = ''

  constructor(id: number, title: string, content: string) {
    this.id = id
    this.title = title
    this.content = content
  }
}

@Entry
@ComponentV2
struct NewsFeedPage {
  private dataSource: PaginatedDataSource<NewsItem> = new PaginatedDataSource<NewsItem>(
    async (page: number, pageSize: number): Promise<NewsItem[]> => {
      let httpRequest = http.createHttp()
      try {
        let response = await httpRequest.request(
          `https://api.example.com/news?page=${page}&size=${pageSize}`,
          { method: http.RequestMethod.GET }
        )
        if (response.responseCode === 200) {
          let jsonResult = JSON.parse(response.result as string) as Record<string, Object>
          let list = jsonResult['data'] as Record<string, Object>[]
          let items: NewsItem[] = []
          for (let item of list) {
            items.push(new NewsItem(
              item['id'] as number,
              item['title'] as string,
              item['content'] as string
            ))
          }
          return items
        }
        return []
      } finally {
        httpRequest.destroy()
      }
    },
    20
  )

  @Local isRefreshing: boolean = false

  aboutToAppear(): void {
    this.dataSource.reload()
  }

  build() {
    Refresh({ refreshing: this.isRefreshing }) {
      List() {
        LazyForEach(this.dataSource, (item: NewsItem) => {
          ListItem() {
            Column() {
              Text(item.title).fontSize(16)
              Text(item.content).fontSize(14).fontColor('#999999')
            }
            .padding(12)
            .width('100%')
          }
        }, (item: NewsItem) => item.id.toString())

        ListItem() {
          Row() {
            if (this.dataSource.hasMore) {
              LoadingProgress().width(24).height(24)
              Text('加载中...').fontSize(14).fontColor('#999999').margin({ left: 8 })
            } else {
              Text('没有更多了').fontSize(14).fontColor('#cccccc')
            }
          }
          .width('100%')
          .justifyContent(FlexAlign.Center)
          .padding(16)
        }
      }
      .onReachEnd(() => {
        this.dataSource.loadMore()
      })
    }
    .onRefreshing(async () => {
      await this.dataSource.reload()
      this.isRefreshing = false
    })
  }
}
```

---

## 3. 过滤/排序数据源（FilteredDataSource）

数据源实现完全复用 V1（与装饰器无关）。V2 使用时仅区别于持有数据源的组件装饰器：

```typescript
type FilterPredicate<T> = (item: T) => boolean
type SortComparator<T> = (a: T, b: T) => number

export class FilteredDataSource<T> implements IDataSource {
  private originalData: T[] = []
  private filteredData: T[] = []
  private currentFilter: FilterPredicate<T> | null = null
  private currentSorter: SortComparator<T> | null = null
  private listeners: DataChangeListener[] = []

  totalCount(): number {
    return this.filteredData.length
  }

  getData(index: number): T {
    return this.filteredData[index]
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

  private notifyReloaded(): void {
    this.listeners.forEach((listener: DataChangeListener) => {
      listener.onDataReloaded()
    })
  }

  setData(data: T[]): void {
    this.originalData = [...data]
    this.applyFilterAndSort()
  }

  appendData(data: T[]): void {
    for (let item of data) {
      this.originalData.push(item)
    }
    this.applyFilterAndSort()
  }

  getOriginalCount(): number {
    return this.originalData.length
  }

  filter(predicate: FilterPredicate<T>): void {
    this.currentFilter = predicate
    this.applyFilterAndSort()
  }

  clearFilter(): void {
    this.currentFilter = null
    this.applyFilterAndSort()
  }

  sort(comparator: SortComparator<T>): void {
    this.currentSorter = comparator
    this.applyFilterAndSort()
  }

  clearSort(): void {
    this.currentSorter = null
    this.applyFilterAndSort()
  }

  filterAndSort(predicate: FilterPredicate<T>, comparator: SortComparator<T>): void {
    this.currentFilter = predicate
    this.currentSorter = comparator
    this.applyFilterAndSort()
  }

  clearAll(): void {
    this.currentFilter = null
    this.currentSorter = null
    this.applyFilterAndSort()
  }

  private applyFilterAndSort(): void {
    if (this.currentFilter !== null) {
      this.filteredData = this.originalData.filter(this.currentFilter)
    } else {
      this.filteredData = [...this.originalData]
    }

    if (this.currentSorter !== null) {
      this.filteredData.sort(this.currentSorter)
    }

    this.notifyReloaded()
  }
}
```

**V2 使用示例：**

```typescript
import { FilteredDataSource } from './FilteredDataSource'

@ObservedV2
class ProductItem {
  @Trace id: number = 0
  @Trace name: string = ''
  @Trace price: number = 0
  @Trace category: string = ''
  @Trace sales: number = 0

  constructor(id: number, name: string, price: number, category: string, sales: number) {
    this.id = id
    this.name = name
    this.price = price
    this.category = category
    this.sales = sales
  }
}

@Entry
@ComponentV2
struct ProductListPage {
  private dataSource: FilteredDataSource<ProductItem> = new FilteredDataSource<ProductItem>()
  @Local selectedCategory: string = '全部'
  @Local sortType: string = 'default'

  private categories: string[] = ['全部', '手机', '电脑', '配件']

  aboutToAppear(): void {
    let products: ProductItem[] = [
      new ProductItem(1, 'HarmonyOS手机', 4999, '手机', 1200),
      new ProductItem(2, '华为笔记本', 6999, '电脑', 800),
      new ProductItem(3, '蓝牙耳机', 299, '配件', 5000),
      new ProductItem(4, '折叠屏手机', 9999, '手机', 600),
      new ProductItem(5, '平板电脑', 3999, '电脑', 1500),
      new ProductItem(6, '手机壳', 29, '配件', 20000)
    ]
    this.dataSource.setData(products)
  }

  applyFilters(): void {
    let categoryFilter = this.selectedCategory
    let filterFn: ((item: ProductItem) => boolean) | null = null
    if (categoryFilter !== '全部') {
      filterFn = (item: ProductItem): boolean => item.category === categoryFilter
    }

    let sortFn: ((a: ProductItem, b: ProductItem) => number) | null = null
    switch (this.sortType) {
      case 'price_asc':
        sortFn = (a, b) => a.price - b.price
        break
      case 'price_desc':
        sortFn = (a, b) => b.price - a.price
        break
      case 'sales':
        sortFn = (a, b) => b.sales - a.sales
        break
    }

    if (filterFn !== null && sortFn !== null) {
      this.dataSource.filterAndSort(filterFn, sortFn)
    } else if (filterFn !== null) {
      this.dataSource.filter(filterFn)
    } else if (sortFn !== null) {
      this.dataSource.clearFilter()
      this.dataSource.sort(sortFn)
    } else {
      this.dataSource.clearAll()
    }
  }

  build() {
    Column() {
      Row({ space: 8 }) {
        ForEach(this.categories, (cat: string) => {
          Button(cat)
            .backgroundColor(this.selectedCategory === cat ? '#007DFF' : '#F5F5F5')
            .fontColor(this.selectedCategory === cat ? Color.White : Color.Black)
            .onClick(() => {
              this.selectedCategory = cat
              this.applyFilters()
            })
        })
      }
      .width('100%')
      .padding(8)

      Row({ space: 8 }) {
        Button('默认').onClick(() => { this.sortType = 'default'; this.applyFilters() })
        Button('价格↑').onClick(() => { this.sortType = 'price_asc'; this.applyFilters() })
        Button('价格↓').onClick(() => { this.sortType = 'price_desc'; this.applyFilters() })
        Button('销量').onClick(() => { this.sortType = 'sales'; this.applyFilters() })
      }
      .width('100%')
      .padding(8)

      Text(`共 ${this.dataSource.totalCount()} 件商品`)
        .fontSize(12)
        .fontColor('#999999')
        .padding({ left: 12 })

      List() {
        LazyForEach(this.dataSource, (item: ProductItem) => {
          ListItem() {
            Row() {
              Column() {
                Text(item.name).fontSize(16)
                Text(item.category).fontSize(12).fontColor('#999999')
              }
              .layoutWeight(1)
              .alignItems(HorizontalAlign.Start)

              Column() {
                Text(`¥${item.price}`).fontColor(Color.Red)
                Text(`销量: ${item.sales}`).fontSize(12).fontColor('#999999')
              }
              .alignItems(HorizontalAlign.End)
            }
            .padding(12)
            .width('100%')
          }
        }, (item: ProductItem) => item.id.toString())
      }
      .layoutWeight(1)
    }
  }
}
```

---

## 4. LazyForEach 详细配合模式（V2）

LazyForEach 的关键配置和最佳实践，V2 中使用与 V1 相同。

### 4.1 cachedCount 配置

```typescript
@Entry
@ComponentV2
struct OptimizedListPage {
  private dataSource: BasicDataSource<string> = new BasicDataSource<string>()

  aboutToAppear(): void {
    let items: string[] = []
    for (let i = 0; i < 1000; i++) {
      items.push(`Item ${i}`)
    }
    this.dataSource.reloadData(items)
  }

  build() {
    List() {
      LazyForEach(this.dataSource, (item: string, index: number) => {
        ListItem() {
          Text(item).width('100%').height(60).padding(12)
        }
      }, (item: string, index: number) => `${index}_${item}`)
    }
    // cachedCount: 在可视区域前后各缓存的组件数量
    // 默认 1。建议根据列表项高度和屏幕高度调整：
    //   - 简单列表项（高度小）：5~10
    //   - 复杂列表项（高度大）：2~5
    //   - 图片列表（需预加载）：3~8
    .cachedCount(5)
  }
}
```

### 4.2 keyGenerator 最佳实践

```typescript
// 模式 1：使用唯一 ID（推荐）
LazyForEach(this.dataSource, (item: ArticleModel) => {
  ListItem() { Text(item.title) }
}, (item: ArticleModel) => item.id.toString())

// 模式 2：组合 key
LazyForEach(this.dataSource, (item: ArticleModel) => {
  ListItem() { Text(item.title) }
}, (item: ArticleModel) => `${item.id}_${item.updatedAt}`)

// ---- 错误示范 ----
// 错误：key 不唯一（重复的 key 会导致渲染异常）
// 错误：key 中包含随机值（每次渲染都不同，失去缓存优势）
```

### 4.3 onMove 拖拽排序

```typescript
@ObservedV2
class SortableItem {
  @Trace id: number = 0
  @Trace title: string = ''
  @Trace order: number = 0

  constructor(id: number, title: string, order: number) {
    this.id = id
    this.title = title
    this.order = order
  }
}

@Entry
@ComponentV2
struct DraggableListPage {
  private dataSource: BasicDataSource<SortableItem> = new BasicDataSource<SortableItem>()

  aboutToAppear(): void {
    let items: SortableItem[] = [
      new SortableItem(1, '推荐', 0),
      new SortableItem(2, '热点', 1),
      new SortableItem(3, '科技', 2),
      new SortableItem(4, '财经', 3),
      new SortableItem(5, '体育', 4),
      new SortableItem(6, '娱乐', 5)
    ]
    this.dataSource.reloadData(items)
  }

  build() {
    Column() {
      Text('长按拖拽排序').fontSize(16).padding(12)

      List() {
        LazyForEach(this.dataSource, (item: SortableItem) => {
          ListItem() {
            Row() {
              Image($r('app.media.drag_handle')).width(24).height(24).margin({ right: 12 })
              Text(item.title).fontSize(16).layoutWeight(1)
            }
            .padding(16).width('100%')
          }
        }, (item: SortableItem) => item.id.toString())
      }
      .onMove((from: number, to: number) => {
        this.dataSource.moveData(from, to)
      })
    }
  }
}
```

### 4.4 LazyForEach + @Param 配合（V2 替代 @ObjectLink）

V1 中 LazyForEach 渲染 `@Observed` 对象时，子组件用 `@ObjectLink` 接收。**V2 直接用 `@Param`** 接收 `@ObservedV2` 实例：

```typescript
@ObservedV2
class TaskModel {
  @Trace id: number = 0
  @Trace title: string = ''
  @Trace isCompleted: boolean = false

  constructor(id: number, title: string, isCompleted: boolean = false) {
    this.id = id
    this.title = title
    this.isCompleted = isCompleted
  }
}

// V2 子组件：直接用 @Param 接收 @ObservedV2 实例
@ComponentV2
struct TaskItemView {
  @Param task: TaskModel = new TaskModel(0, '')

  build() {
    Row() {
      Checkbox()
        .select(this.task.isCompleted)
        .onChange((value: boolean) => {
          this.task.isCompleted = value  // @Trace 属性变化自动刷新
        })
      Text(this.task.title)
        .decoration({
          type: this.task.isCompleted ? TextDecorationType.LineThrough : TextDecorationType.None
        })
        .fontColor(this.task.isCompleted ? '#999999' : '#333333')
        .layoutWeight(1)
    }
    .padding(12)
    .width('100%')
  }
}

@Entry
@ComponentV2
struct TaskListPage {
  private dataSource: BasicDataSource<TaskModel> = new BasicDataSource<TaskModel>()
  @Local newTaskTitle: string = ''

  aboutToAppear(): void {
    this.dataSource.reloadData([
      new TaskModel(1, '学习 ArkTS V2'),
      new TaskModel(2, '完成数据层设计'),
      new TaskModel(3, '编写单元测试')
    ])
  }

  build() {
    Column() {
      Row() {
        TextInput({ placeholder: '新任务', text: this.newTaskTitle })
          .layoutWeight(1)
          .onChange((value: string) => {
            this.newTaskTitle = value
          })
        Button('添加')
          .onClick(() => {
            if (this.newTaskTitle.length > 0) {
              let newId = Date.now()
              this.dataSource.pushData(new TaskModel(newId, this.newTaskTitle))
              this.newTaskTitle = ''
            }
          })
      }
      .padding(12)

      List() {
        LazyForEach(this.dataSource, (task: TaskModel) => {
          ListItem() {
            TaskItemView({ task: task })
          }
          .swipeAction({
            end: { builder: () => { this.DeleteButton(task) } }
          })
        }, (task: TaskModel) => task.id.toString())
      }
      .layoutWeight(1)
      .cachedCount(5)
    }
  }

  @Builder
  DeleteButton(task: TaskModel) {
    Button('删除')
      .backgroundColor(Color.Red)
      .fontColor(Color.White)
      .onClick(() => {
        let index = this.dataSource.indexOf((item: TaskModel) => item.id === task.id)
        if (index >= 0) {
          this.dataSource.deleteData(index)
        }
      })
  }
}
```

---

## 5. V2 推荐：Repeat<T> 替代 LazyForEach（可选）

V2 引入 `Repeat<T>` 作为新一代列表渲染器，对纯内存数组的渲染更直观（不需要实现 IDataSource）。**LazyForEach 仍可用，Repeat 是新选择**。

```typescript
@Entry
@ComponentV2
struct TaskListPageRepeat {
  @Local tasks: TaskModel[] = [
    new TaskModel(1, '学习 ArkTS V2'),
    new TaskModel(2, '完成数据层设计')
  ]

  build() {
    Column() {
      List() {
        Repeat<TaskModel>(this.tasks)
          .each((item: RepeatItem<TaskModel>) => {
            ListItem() {
              TaskItemView({ task: item.item })
            }
          })
          .key((item: TaskModel) => item.id.toString())
          // Repeat 也支持虚拟滚动模式
          .virtualScroll({ totalCount: this.tasks.length })
      }
      .layoutWeight(1)
    }
  }
}
```

**何时用 LazyForEach vs Repeat？**

| 场景 | 推荐 |
|---|---|
| 数据来自 IDataSource（如分页 API、过滤排序、需要监听 add/delete/move 事件） | `LazyForEach + BasicDataSource` |
| 数据是简单内存数组，UI 自然响应数组变化即可 | `Repeat<T>` |
| 需要复用 Android `RecyclerView.Adapter` 风格代码 | `LazyForEach + BasicDataSource` |

---

## V1 → V2 速查对照（数据源场景）

| V1 写法 | V2 写法 | 备注 |
|---|---|---|
| `@Component struct ListPage` | `@ComponentV2 struct ListPage` | |
| `@State isRefreshing: boolean = false` | `@Local isRefreshing: boolean = false` | |
| `@Observed class Item { x: T }` | `@ObservedV2 class Item { @Trace x: T = ... }` | |
| `@ObjectLink item: Item` | `@Param item: Item = new Item()` | 子组件接收 |
| `Refresh({ refreshing: $$this.isRefreshing })` | `Refresh({ refreshing: this.isRefreshing })` | V2 不再用 `$$` |
| `LazyForEach(ds, (item) => {...})` | 同上 / 或换 `Repeat<T>(arr).each(...).key(...)` | |
