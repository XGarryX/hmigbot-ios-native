# ArkTS 数据源模式参考（**V1 历史文档 — Legacy**）

> ⚠️ **本项目锁 ArkTS V2**。本文档为 **V1 历史参考**（`@Observed / @ObjectLink / @State / @Component / @Entry` 等），仅用于阅读老代码或迁移老项目时查阅。
>
> **新代码请使用 V2 装饰器**：参阅 [`v2-datasource-patterns.md`](./v2-datasource-patterns.md)（V2 主参考）和 [`SKILL.md`](../SKILL.md)。
>
> 注意：`BasicDataSource / PaginatedDataSource / FilteredDataSource` 等数据源类**本身不依赖装饰器**，V1/V2 通用。本文档中需要 V1→V2 替换的地方主要是消费数据源的 UI 组件部分：
> - `@Component` → `@ComponentV2`
> - `@State` → `@Local`
> - `@Observed` → `@ObservedV2`（类内可观察属性加 `@Trace`）
> - `@ObjectLink xxx: Cls` → `@Param xxx: Cls = new Cls()`
> - V2 也可使用 `Repeat<T>(this.items).each(...).key(...)` 替代 `LazyForEach`

---

> 完整的 IDataSource / BasicDataSource 实现模式，涵盖基础数据源、分页、过滤排序，以及与 LazyForEach 的配合使用。

---

## 1. BasicDataSource 完整实现

`IDataSource` 是 LazyForEach 要求的数据源接口。`BasicDataSource` 是对该接口的通用封装，提供增删改查和监听器通知。

```typescript
// ==========================================
// BasicDataSource<T> —— 通用数据源基类
// 实现 IDataSource 接口，供 LazyForEach 使用
// ==========================================

export class BasicDataSource<T> implements IDataSource {
  // 内部数据存储
  private dataArray: T[] = []
  // 数据变化监听器列表（LazyForEach 会注册监听器）
  private listeners: DataChangeListener[] = []

  // ---- IDataSource 接口方法 ----

  // 获取数据总数
  totalCount(): number {
    return this.dataArray.length
  }

  // 获取指定索引的数据
  getData(index: number): T {
    return this.dataArray[index]
  }

  // 注册数据变化监听器（LazyForEach 内部调用）
  registerDataChangeListener(listener: DataChangeListener): void {
    if (this.listeners.indexOf(listener) < 0) {
      this.listeners.push(listener)
    }
  }

  // 注销数据变化监听器
  unregisterDataChangeListener(listener: DataChangeListener): void {
    const index = this.listeners.indexOf(listener)
    if (index >= 0) {
      this.listeners.splice(index, 1)
    }
  }

  // ---- 通知方法（触发 LazyForEach 局部刷新）----

  // 通知数据重新加载（全量刷新，慎用）
  notifyDataReloaded(): void {
    this.listeners.forEach((listener: DataChangeListener) => {
      listener.onDataReloaded()
    })
  }

  // 通知新增数据
  notifyDataAdd(index: number): void {
    this.listeners.forEach((listener: DataChangeListener) => {
      listener.onDataAdd(index)
    })
  }

  // 通知数据变化（指定索引的数据发生更新）
  notifyDataChange(index: number): void {
    this.listeners.forEach((listener: DataChangeListener) => {
      listener.onDataChange(index)
    })
  }

  // 通知数据删除
  notifyDataDelete(index: number): void {
    this.listeners.forEach((listener: DataChangeListener) => {
      listener.onDataDelete(index)
    })
  }

  // 通知数据移动
  notifyDataMove(from: number, to: number): void {
    this.listeners.forEach((listener: DataChangeListener) => {
      listener.onDataMove(from, to)
    })
  }

  // ---- CRUD 操作 ----

  // 追加单条数据到末尾
  pushData(data: T): void {
    this.dataArray.push(data)
    this.notifyDataAdd(this.dataArray.length - 1)
  }

  // 批量追加数据
  pushDataArray(dataList: T[]): void {
    let startIndex = this.dataArray.length
    for (let item of dataList) {
      this.dataArray.push(item)
    }
    // 批量新增用 reload 效率更高
    this.notifyDataReloaded()
  }

  // 在指定位置插入数据
  insertData(index: number, data: T): void {
    if (index >= 0 && index <= this.dataArray.length) {
      this.dataArray.splice(index, 0, data)
      this.notifyDataAdd(index)
    }
  }

  // 更新指定索引的数据
  updateData(index: number, data: T): void {
    if (index >= 0 && index < this.dataArray.length) {
      this.dataArray[index] = data
      this.notifyDataChange(index)
    }
  }

  // 删除指定索引的数据
  deleteData(index: number): void {
    if (index >= 0 && index < this.dataArray.length) {
      this.dataArray.splice(index, 1)
      this.notifyDataDelete(index)
    }
  }

  // 移动数据（用于拖拽排序）
  moveData(from: number, to: number): void {
    if (from >= 0 && from < this.dataArray.length &&
        to >= 0 && to < this.dataArray.length && from !== to) {
      let item = this.dataArray[from]
      this.dataArray.splice(from, 1)
      this.dataArray.splice(to, 0, item)
      this.notifyDataMove(from, to)
    }
  }

  // 清空所有数据
  clearData(): void {
    this.dataArray = []
    this.notifyDataReloaded()
  }

  // 用新数据替换全部（常见于下拉刷新场景）
  reloadData(dataList: T[]): void {
    this.dataArray = dataList
    this.notifyDataReloaded()
  }

  // 获取内部数据数组的副本
  getAllData(): T[] {
    return [...this.dataArray]
  }

  // 查找数据的索引
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

**基础使用示例：**

```typescript
import { BasicDataSource } from './BasicDataSource'

// 定义数据模型
@Observed
class ArticleModel {
  id: number
  title: string
  summary: string

  constructor(id: number, title: string, summary: string) {
    this.id = id
    this.title = title
    this.summary = summary
  }
}

@Entry
@Component
struct ArticleListPage {
  // 创建数据源实例
  private dataSource: BasicDataSource<ArticleModel> = new BasicDataSource<ArticleModel>()

  aboutToAppear(): void {
    // 模拟加载数据
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

继承 BasicDataSource，增加分页加载能力。适用于无限滚动列表场景。

```typescript
// ==========================================
// PaginatedDataSource<T> —— 分页数据源
// 支持下拉刷新 + 上拉加载更多
// ==========================================

// 分页请求回调类型
// page: 页码（从1开始），pageSize: 每页数量
// 返回 Promise<T[]>
type PageFetcher<T> = (page: number, pageSize: number) => Promise<T[]>

export class PaginatedDataSource<T> extends BasicDataSource<T> {
  // 当前页码
  private currentPage: number = 0
  // 每页数据量
  private pageSize: number = 20
  // 是否还有更多数据
  private _hasMore: boolean = true
  // 是否正在加载
  private _isLoading: boolean = false
  // 数据请求回调
  private fetcher: PageFetcher<T>

  constructor(fetcher: PageFetcher<T>, pageSize: number = 20) {
    super()
    this.fetcher = fetcher
    this.pageSize = pageSize
  }

  // 是否还有更多数据（供 UI 判断是否显示加载更多）
  get hasMore(): boolean {
    return this._hasMore
  }

  // 是否正在加载
  get isLoading(): boolean {
    return this._isLoading
  }

  // 加载首页（下拉刷新时调用）
  async reload(): Promise<void> {
    if (this._isLoading) {
      return
    }
    this._isLoading = true
    this.currentPage = 1
    this._hasMore = true

    try {
      let data = await this.fetcher(this.currentPage, this.pageSize)
      // 用新数据替换全部
      this.reloadData(data)
      // 如果返回数据量小于 pageSize，说明没有更多了
      if (data.length < this.pageSize) {
        this._hasMore = false
      }
    } catch (error) {
      console.error(`分页加载失败: ${JSON.stringify(error)}`)
      // 加载失败时不清空已有数据
    } finally {
      this._isLoading = false
    }
  }

  // 加载下一页（上拉加载更多时调用）
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

  // 获取当前页码
  getCurrentPage(): number {
    return this.currentPage
  }

  // 重置状态
  reset(): void {
    this.currentPage = 0
    this._hasMore = true
    this._isLoading = false
    this.clearData()
  }
}
```

**分页数据源使用示例：**

```typescript
import { PaginatedDataSource } from './PaginatedDataSource'
import { http } from '@kit.NetworkKit'

@Observed
class NewsItem {
  id: number
  title: string
  content: string

  constructor(id: number, title: string, content: string) {
    this.id = id
    this.title = title
    this.content = content
  }
}

@Entry
@Component
struct NewsFeedPage {
  // 创建分页数据源，传入请求回调
  private dataSource: PaginatedDataSource<NewsItem> = new PaginatedDataSource<NewsItem>(
    async (page: number, pageSize: number): Promise<NewsItem[]> => {
      // 实际项目中这里调用 API
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
    20  // 每页20条
  )

  @State isRefreshing: boolean = false

  aboutToAppear(): void {
    // 页面加载时自动请求首页
    this.dataSource.reload()
  }

  build() {
    Refresh({ refreshing: $$this.isRefreshing }) {
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

        // 底部加载更多指示器
        ListItem() {
          Row() {
            if (this.dataSource.hasMore) {
              LoadingProgress()
                .width(24).height(24)
              Text('加载中...')
                .fontSize(14)
                .fontColor('#999999')
                .margin({ left: 8 })
            } else {
              Text('没有更多了')
                .fontSize(14)
                .fontColor('#cccccc')
            }
          }
          .width('100%')
          .justifyContent(FlexAlign.Center)
          .padding(16)
        }
      }
      .onReachEnd(() => {
        // 滚动到底部时自动加载下一页
        this.dataSource.loadMore()
      })
    }
    .onRefreshing(async () => {
      // 下拉刷新
      await this.dataSource.reload()
      this.isRefreshing = false
    })
  }
}
```

---

## 3. 过滤/排序数据源（FilteredDataSource）

保留原始数据，在上层维护过滤后的视图。支持多条件过滤和排序，不修改原始数据。

```typescript
// ==========================================
// FilteredDataSource<T> —— 支持过滤和排序
// 原始数据不变，维护一个过滤后的视图
// ==========================================

// 过滤条件函数类型
type FilterPredicate<T> = (item: T) => boolean
// 排序比较函数类型
type SortComparator<T> = (a: T, b: T) => number

export class FilteredDataSource<T> implements IDataSource {
  // 原始完整数据
  private originalData: T[] = []
  // 过滤后的视图数据（展示用）
  private filteredData: T[] = []
  // 当前过滤条件
  private currentFilter: FilterPredicate<T> | null = null
  // 当前排序规则
  private currentSorter: SortComparator<T> | null = null
  // 监听器
  private listeners: DataChangeListener[] = []

  // ---- IDataSource 接口 ----

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

  // ---- 数据操作 ----

  // 设置原始数据（首次加载或刷新时调用）
  setData(data: T[]): void {
    this.originalData = [...data]
    this.applyFilterAndSort()
  }

  // 追加数据到原始数据（加载更多时调用）
  appendData(data: T[]): void {
    for (let item of data) {
      this.originalData.push(item)
    }
    this.applyFilterAndSort()
  }

  // 获取原始数据总数
  getOriginalCount(): number {
    return this.originalData.length
  }

  // ---- 过滤 ----

  // 设置过滤条件并立即应用
  filter(predicate: FilterPredicate<T>): void {
    this.currentFilter = predicate
    this.applyFilterAndSort()
  }

  // 清除过滤条件（恢复显示全部数据）
  clearFilter(): void {
    this.currentFilter = null
    this.applyFilterAndSort()
  }

  // ---- 排序 ----

  // 设置排序规则并立即应用
  sort(comparator: SortComparator<T>): void {
    this.currentSorter = comparator
    this.applyFilterAndSort()
  }

  // 清除排序规则
  clearSort(): void {
    this.currentSorter = null
    this.applyFilterAndSort()
  }

  // ---- 组合：过滤 + 排序 ----

  // 同时设置过滤和排序
  filterAndSort(predicate: FilterPredicate<T>, comparator: SortComparator<T>): void {
    this.currentFilter = predicate
    this.currentSorter = comparator
    this.applyFilterAndSort()
  }

  // 清除所有过滤和排序
  clearAll(): void {
    this.currentFilter = null
    this.currentSorter = null
    this.applyFilterAndSort()
  }

  // 核心方法：应用过滤和排序，更新视图数据
  private applyFilterAndSort(): void {
    // 第一步：过滤
    if (this.currentFilter !== null) {
      this.filteredData = this.originalData.filter(this.currentFilter)
    } else {
      this.filteredData = [...this.originalData]
    }

    // 第二步：排序
    if (this.currentSorter !== null) {
      this.filteredData.sort(this.currentSorter)
    }

    // 通知 LazyForEach 刷新
    this.notifyReloaded()
  }
}
```

**过滤数据源使用示例：**

```typescript
import { FilteredDataSource } from './FilteredDataSource'

@Observed
class ProductItem {
  id: number
  name: string
  price: number
  category: string
  sales: number

  constructor(id: number, name: string, price: number, category: string, sales: number) {
    this.id = id
    this.name = name
    this.price = price
    this.category = category
    this.sales = sales
  }
}

@Entry
@Component
struct ProductListPage {
  private dataSource: FilteredDataSource<ProductItem> = new FilteredDataSource<ProductItem>()
  @State selectedCategory: string = '全部'
  @State sortType: string = 'default'  // default | price_asc | price_desc | sales

  private categories: string[] = ['全部', '手机', '电脑', '配件']

  aboutToAppear(): void {
    // 模拟商品数据
    let products: ProductItem[] = [
      new ProductItem(1, 'HarmonyOS手机', 4999, '手机', 1200),
      new ProductItem(2, '华为笔记本', 6999, '电脑', 800),
      new ProductItem(3, '蓝牙耳机', 299, '配件', 5000),
      new ProductItem(4, '折叠屏手机', 9999, '手机', 600),
      new ProductItem(5, '平板电脑', 3999, '电脑', 1500),
      new ProductItem(6, '手机壳', 29, '配件', 20000),
      new ProductItem(7, '旗舰手机', 5999, '手机', 3000),
      new ProductItem(8, '智能手表', 1999, '配件', 2500),
    ]
    this.dataSource.setData(products)
  }

  // 应用当前的过滤和排序条件
  applyFilters(): void {
    // 分类过滤
    let categoryFilter = this.selectedCategory
    let filterFn: ((item: ProductItem) => boolean) | null = null
    if (categoryFilter !== '全部') {
      filterFn = (item: ProductItem): boolean => {
        return item.category === categoryFilter
      }
    }

    // 排序
    let sortFn: ((a: ProductItem, b: ProductItem) => number) | null = null
    switch (this.sortType) {
      case 'price_asc':
        sortFn = (a: ProductItem, b: ProductItem): number => a.price - b.price
        break
      case 'price_desc':
        sortFn = (a: ProductItem, b: ProductItem): number => b.price - a.price
        break
      case 'sales':
        sortFn = (a: ProductItem, b: ProductItem): number => b.sales - a.sales
        break
    }

    // 根据条件组合应用
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
      // 分类选择栏
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

      // 排序选择栏
      Row({ space: 8 }) {
        Button('默认')
          .onClick(() => { this.sortType = 'default'; this.applyFilters() })
        Button('价格↑')
          .onClick(() => { this.sortType = 'price_asc'; this.applyFilters() })
        Button('价格↓')
          .onClick(() => { this.sortType = 'price_desc'; this.applyFilters() })
        Button('销量')
          .onClick(() => { this.sortType = 'sales'; this.applyFilters() })
      }
      .width('100%')
      .padding(8)

      // 结果计数
      Text(`共 ${this.dataSource.totalCount()} 件商品（原始 ${this.dataSource.getOriginalCount()} 件）`)
        .fontSize(12)
        .fontColor('#999999')
        .padding({ left: 12 })

      // 商品列表
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

## 4. LazyForEach 详细配合模式

LazyForEach 的关键配置和最佳实践。

### 4.1 cachedCount 配置

`cachedCount` 控制 LazyForEach 在可视区域外预创建的子组件数量。

```typescript
// ==========================================
// cachedCount 配置说明
// ==========================================

@Entry
@Component
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
          Text(item)
            .width('100%')
            .height(60)
            .padding(12)
        }
      }, (item: string, index: number) => `${index}_${item}`)
    }
    // cachedCount: 在可视区域前后各缓存的组件数量
    // 默认值为 1。建议根据列表项高度和屏幕高度调整：
    //   - 简单列表项（高度小）：设置 5~10
    //   - 复杂列表项（高度大）：设置 2~5
    //   - 图片列表（需预加载）：设置 3~8
    .cachedCount(5)
  }
}
```

### 4.2 keyGenerator 最佳实践

`keyGenerator` 是 LazyForEach 的第三个参数，用于生成每项的唯一标识。正确的 key 对局部刷新至关重要。

```typescript
// ==========================================
// keyGenerator 模式
// ==========================================

// 模式 1：使用唯一 ID（推荐）
LazyForEach(this.dataSource, (item: ArticleModel) => {
  ListItem() {
    Text(item.title)
  }
}, (item: ArticleModel) => item.id.toString())
// key = "123"

// 模式 2：组合 key（当单个字段不够唯一时）
LazyForEach(this.dataSource, (item: ArticleModel) => {
  ListItem() {
    Text(item.title)
  }
}, (item: ArticleModel) => `${item.id}_${item.updatedAt}`)
// key = "123_1704067200000"
// 优势：数据更新时 key 变化，LazyForEach 会重新创建组件

// 模式 3：使用 index（仅当数据没有唯一标识时）
LazyForEach(this.dataSource, (item: string, index: number) => {
  ListItem() {
    Text(item)
  }
}, (item: string, index: number) => index.toString())
// 注意：使用 index 作为 key 时，数据增删会导致大量不必要的刷新

// ---- 错误示范 ----

// 错误：key 不唯一（重复的 key 会导致渲染异常）
// LazyForEach(dataSource, (item) => { ... }, (item) => item.category)
// 如果多个 item 的 category 相同，key 重复！

// 错误：key 中包含随机值（每次渲染都不同，失去缓存优势）
// LazyForEach(dataSource, (item) => { ... }, (item) => `${item.id}_${Math.random()}`)
```

### 4.3 onDataMove 拖拽排序

配合 `List` 的拖拽能力实现列表项排序。

```typescript
// ==========================================
// 拖拽排序完整示例
// ==========================================

@Observed
class SortableItem {
  id: number
  title: string
  order: number

  constructor(id: number, title: string, order: number) {
    this.id = id
    this.title = title
    this.order = order
  }
}

@Entry
@Component
struct DraggableListPage {
  private dataSource: BasicDataSource<SortableItem> = new BasicDataSource<SortableItem>()

  aboutToAppear(): void {
    let items: SortableItem[] = [
      new SortableItem(1, '推荐', 0),
      new SortableItem(2, '热点', 1),
      new SortableItem(3, '科技', 2),
      new SortableItem(4, '财经', 3),
      new SortableItem(5, '体育', 4),
      new SortableItem(6, '娱乐', 5),
    ]
    this.dataSource.reloadData(items)
  }

  build() {
    Column() {
      Text('长按拖拽排序')
        .fontSize(16)
        .padding(12)

      List() {
        LazyForEach(this.dataSource, (item: SortableItem) => {
          ListItem() {
            Row() {
              Image($r('app.media.drag_handle'))
                .width(24)
                .height(24)
                .margin({ right: 12 })
              Text(item.title)
                .fontSize(16)
                .layoutWeight(1)
            }
            .padding(16)
            .width('100%')
          }
        }, (item: SortableItem) => item.id.toString())
      }
      .onMove((from: number, to: number) => {
        // 调用数据源的移动方法，内部会触发 notifyDataMove
        this.dataSource.moveData(from, to)
      })
    }
  }
}
```

### 4.4 LazyForEach 与 @ObjectLink 配合

当 LazyForEach 渲染 `@Observed` 对象时，子组件需用 `@ObjectLink` 接收以支持属性级更新。

```typescript
// ==========================================
// LazyForEach + @ObjectLink 完整模式
// ==========================================

@Observed
class TaskModel {
  id: number
  title: string
  isCompleted: boolean

  constructor(id: number, title: string, isCompleted: boolean = false) {
    this.id = id
    this.title = title
    this.isCompleted = isCompleted
  }
}

// 子组件：用 @ObjectLink 接收 @Observed 对象
// 对象属性变化时只刷新该子组件，不影响列表中其他项
@Component
struct TaskItemView {
  @ObjectLink task: TaskModel

  build() {
    Row() {
      Checkbox()
        .select(this.task.isCompleted)
        .onChange((value: boolean) => {
          // 直接修改属性，UI 自动更新
          this.task.isCompleted = value
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
@Component
struct TaskListPage {
  private dataSource: BasicDataSource<TaskModel> = new BasicDataSource<TaskModel>()
  @State newTaskTitle: string = ''

  aboutToAppear(): void {
    this.dataSource.reloadData([
      new TaskModel(1, '学习 ArkTS'),
      new TaskModel(2, '完成数据层设计'),
      new TaskModel(3, '编写单元测试'),
    ])
  }

  build() {
    Column() {
      // 新增任务
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
              this.dataSource.pushData(
                new TaskModel(newId, this.newTaskTitle)
              )
              this.newTaskTitle = ''
            }
          })
      }
      .padding(12)

      // 任务列表
      List() {
        LazyForEach(this.dataSource, (task: TaskModel) => {
          ListItem() {
            // 使用 @ObjectLink 子组件
            TaskItemView({ task: task })
          }
          .swipeAction({
            end: {
              builder: () => {
                this.DeleteButton(task)
              }
            }
          })
        }, (task: TaskModel) => task.id.toString())
      }
      .layoutWeight(1)
      .cachedCount(5)
    }
  }

  // 左滑删除按钮
  @Builder
  DeleteButton(task: TaskModel) {
    Button('删除')
      .backgroundColor(Color.Red)
      .fontColor(Color.White)
      .onClick(() => {
        let index = this.dataSource.indexOf(
          (item: TaskModel) => item.id === task.id
        )
        if (index >= 0) {
          this.dataSource.deleteData(index)
        }
      })
  }
}
```
