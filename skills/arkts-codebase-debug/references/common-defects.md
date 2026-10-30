# HarmonyOS 常见缺陷模式

本文件汇总HarmonyOS ArkTS应用开发中常见的功能缺陷模式、原因分析和解决方案。

> **说明**：示例代码默认使用 ArkTS V2（API 12+，本项目锁 V2，主要装饰器：`@ComponentV2` / `@Local` / `@Param` (+ `@Once`) / `@Event` / `@Provider` / `@Consumer` / `@ObservedV2` + `@Trace` / `AppStorageV2.connect` / `@Monitor`）。若你正在排查的是 V1 老项目（`@Component` / `@State` / `@Prop` / `@Link` / `@Provide` / `@Consume` / `@Observed` + `@ObjectLink` / `@StorageLink` / `@Watch`），按下面映射换回 V1 装饰器即可，缺陷模式与排查思路两套版本通用：
>
> | V2 | V1 |
> |---|---|
> | `@ComponentV2` | `@Component` |
> | `@Local` | `@State` |
> | `@Param` (+ 可选 `@Once`) | `@Prop` |
> | `@Param` + `@Event` 回调 | `@Link`（父用 `$value` 传） |
> | `@Provider()` / `@Consumer()` | `@Provide` / `@Consume` |
> | `@ObservedV2` + `@Trace` | `@Observed` + `@ObjectLink` |
> | `AppStorageV2.connect(...)` | `@StorageLink` / `@StorageProp` |
> | `@Monitor('prop')` | `@Watch('callbackName')` |

## UI渲染缺陷

### 缺陷1：页面空白或组件不显示
**表现**：页面加载后显示空白，某些组件没有渲染

**可能原因**：
- 渲染条件判断错误
- 组件被隐藏或移出屏幕
- 数据初始化失败
- 布局配置错误

**诊断步骤**：
1. 检查`build()`方法是否正确返回组件
2. 检查if/else条件渲染的逻辑
3. 验证数据是否正确初始化
4. 检查组件的宽高和可见性设置

**解决方案**：
```typescript
// 错误示例
build() {
  if (this.isLoading) {
    LoadingSpinner()
  }
  // 没有else分支，加载完成后显示空白
}

// 正确示例
build() {
  if (this.isLoading) {
    LoadingSpinner()
  } else {
    Content()
  }
}
```

### 缺陷2：布局错位或重叠
**表现**：组件位置不正确，相互重叠

**可能原因**：
- 布局容器选择不当
- 组件宽高设置不合理
- 对齐方式配置错误
- 优先级和权重设置问题

**解决方案**：
```typescript
// 错误示例
Row() {
  Text('Title')
  Button('Action')
} // Row中组件宽度未设置，可能导致挤压

// 正确示例
Row() {
  Text('Title')
    .layoutWeight(1) // 占用剩余空间
  Button('Action')
}
```

### 缺陷3：样式不生效
**表现**：设置的样式没有应用到组件

**可能原因**：
- 样式被后续设置覆盖
- 样式优先级问题
- 样式属性值不合法
- 条件渲染导致样式丢失

**解决方案**：
```typescript
// 错误示例
Text('Hello')
  .fontSize(20)
  .fontSize(30) // 第一个设置被覆盖

// 正确示例
Text('Hello')
  .fontSize(30)
  .fontWeight(FontWeight.Bold)
```

## 数据绑定缺陷

### 缺陷4：数据修改后视图不更新
**表现**：修改数据后，UI没有相应变化

**可能原因**：
- 没有使用状态装饰器
- 直接修改对象属性不触发观察
- 异步更新时机问题
- 状态变量被重新赋值

**解决方案**：
```typescript
// 错误示例（V2）
@ComponentV2
struct Counter {
  count: number = 0 // 没有 @Local（V1 对应没有 @State）

  build() {
    Button(`${this.count}`)
      .onClick(() => {
        this.count++ // 不会触发更新
      })
  }
}

// 正确示例（V2）
@ComponentV2
struct Counter {
  @Local count: number = 0 // 使用 @Local（V1 对应 @State）

  build() {
    Button(`${this.count}`)
      .onClick(() => {
        this.count++ // 触发更新
      })
  }
}
```

### 缺陷5：父子组件数据不同步
**表现**：父组件修改数据，子组件没有更新

**可能原因**：
- V2：用了 `@Param` 但缺少回写父的 `@Event` 回调（V1 对应：用了 `@Prop` 而非 `@Link`）
- 父组件没有正确更新状态
- 数据类型不匹配
- 对象引用问题

**解决方案**：
```typescript
// 错误示例：V2 仅用 @Param（单向，子改不回传父）
@ComponentV2
struct Parent {
  @Local value: string = 'Hello'

  build() {
    Child({ value: this.value })
  }
}

@ComponentV2
struct Child {
  @Param value: string = '' // 单向，子组件修改不影响父组件
}

// 正确示例：V2 使用 @Param + @Event 回调（替代 V1 @Link）
@ComponentV2
struct Parent {
  @Local value: string = 'Hello'

  build() {
    Child({
      value: this.value,
      onValueChange: (v: string) => { this.value = v } // 父在回调中写回
    })
  }
}

@ComponentV2
struct Child {
  @Param value: string = ''
  @Event onValueChange: (v: string) => void = () => {}
  // 子组件需要修改时
  // this.onValueChange(newValue)
}
```

> V1 等价写法：父组件 `@State value` + `Child({ value: $value })`，子组件 `@Link value: string`。本项目锁 V2，新代码统一用 `@Param + @Event`。

### 缺陷6：嵌套对象属性修改不触发更新
**表现**：修改嵌套对象的属性，视图不更新

**可能原因**：
- V2 缺少 `@ObservedV2` + `@Trace`（V1 对应：缺少 `@Observed` + `@ObjectLink`）
- 直接修改对象属性
- 数组元素替换方式错误

**解决方案**：
```typescript
// 错误示例（V2）
@Local items: Array<{ id: number, name: string }> = []

updateName(index: number, newName: string) {
  this.items[index].name = newName // 不触发更新（普通对象属性变化无感知）
}

// 正确示例（V2）
@ObservedV2
class Item {
  @Trace name: string = ''
  id: number = 0
  constructor(id: number, name: string) {
    this.id = id
    this.name = name
  }
}

@ComponentV2
struct ListComponent {
  @Local items: Item[] = []

  updateName(index: number, newName: string) {
    this.items[index].name = newName // 触发更新（@Trace 属性级观察）
  }
}
```

> V1 等价写法：`@Observed class Item { @Track name: string }` + 组件 `@State items: Item[]`，子组件用 `@ObjectLink` 持有单个 Item。

## 事件处理缺陷

### 缺陷7：点击事件不触发
**表现**：点击按钮或组件没有任何反应

**可能原因**：
- onClick事件未正确绑定
- 组件被其他组件遮挡
- 事件冒泡被阻止
- 组件不可交互（disabled）

**解决方案**：
```typescript
// 错误示例
Button('Click Me')
  .onClick() // 没有回调函数

// 正确示例
Button('Click Me')
  .onClick(() => {
    console.log('Button clicked')
  })
```

### 缺陷8：回调函数中的this指向错误
**表现**：事件回调中无法访问组件成员

**可能原因**：
- 回调函数this丢失
- 使用了普通函数而非箭头函数
- 回调绑定方式不正确

**解决方案**：
```typescript
// 错误示例（V2）
@ComponentV2
struct MyComponent {
  @Local count: number = 0

  build() {
    Button('Increase')
      .onClick(function() {
        this.count++ // this指向undefined
      })
  }
}

// 正确示例1：使用箭头函数
@ComponentV2
struct MyComponent {
  @Local count: number = 0

  build() {
    Button('Increase')
      .onClick(() => {
        this.count++ // this正确
      })
  }
}

// 正确示例2：使用bind
@ComponentV2
struct MyComponent {
  @Local count: number = 0

  handleClick() {
    this.count++
  }

  build() {
    Button('Increase')
      .onClick(this.handleClick.bind(this))
  }
}
```

> V1 等价写法：把 `@ComponentV2` 改回 `@Component`、`@Local` 改回 `@State` 即可，this 绑定问题与排查方式两套版本完全一致。

### 缺陷9：事件监听器未清理
**表现**：组件销毁后仍有事件监听，导致内存泄漏

**可能原因**：
- 没有在aboutToDisappear中清理监听
- 全局事件未正确管理
- 定时器未清除

**解决方案**：
```typescript
@ComponentV2
struct EventComponent {
  private eventHandler: Function = () => {}

  aboutToAppear() {
    this.eventHandler = () => {
      console.log('Event triggered')
    }
    someEvent.on('change', this.eventHandler)
  }

  aboutToDisappear() {
    someEvent.off('change', this.eventHandler) // 清理监听
  }

  build() {
    Text('Event Component')
  }
}
```

> V1 老项目把 `@ComponentV2` 改回 `@Component`，生命周期清理逻辑两套版本完全一致。

## 路由导航缺陷

### 缺陷10：页面跳转失败
**表现**：调用router.pushUrl()后没有跳转

**可能原因**：
- 路由路径错误
- 目标页面未注册
- 路由模式配置错误
- 权限或状态限制

**解决方案**：
```typescript
// 错误示例
router.pushUrl({
  url: 'detail' // 路径不完整
})

// 正确示例
router.pushUrl({
  url: 'pages/Detail', // 完整路径
  params: { id: 123 }
}, router.RouterMode.Standard).catch((error: Error) => {
  console.error('Navigation failed:', error)
})
```

### 缺陷11：路由参数丢失
**表现**：页面跳转后无法获取传递的参数

**可能原因**：
- 参数名称拼写错误
- 参数类型不匹配
- getParams()调用时机错误
- 路由模式不支持参数

**解决方案**：
```typescript
// 发送页面
router.pushUrl({
  url: 'pages/Detail',
  params: {
    userId: 123,
    userName: 'John'
  }
})

// 接收页面（V2）
@ComponentV2
struct DetailPage {
  @Local userId: number = 0
  @Local userName: string = ''

  aboutToAppear() {
    const params = router.getParams() as Record<string, Object>
    this.userId = params['userId'] as number
    this.userName = params['userName'] as string
  }

  build() {
    Text(`User: ${this.userName} (${this.userId})`)
  }
}
```

> V1 等价：`@Component struct DetailPage { @State userId: number = 0; @State userName: string = '' }`。

## 网络请求缺陷

### 缺陷12：网络请求失败
**表现**：API调用失败，无法获取数据

**可能原因**：
- 网络权限未配置
- URL格式错误
- 请求超时
- 服务器错误

**解决方案**：
```typescript
// 1. 在module.json5中配置权限
{
  "module": {
    "requestPermissions": [
      {
        "name": "ohos.permission.INTERNET"
      }
    ]
  }
}

// 2. 正确发起请求
import http from '@ohos.net.http'

async fetchData() {
  const httpRequest = http.createHttp()

  try {
    const response = await httpRequest.request('https://api.example.com/data', {
      method: http.RequestMethod.GET,
      header: {
        'Content-Type': 'application/json'
      },
      connectTimeout: 60000,
      readTimeout: 60000
    })

    if (response.responseCode === 200) {
      const data = JSON.parse(response.result as string)
      return data
    } else {
      console.error('Request failed:', response.responseCode)
      throw new Error(`HTTP ${response.responseCode}`)
    }
  } catch (error) {
    console.error('Network error:', error)
    throw error
  } finally {
    httpRequest.destroy()
  }
}
```

### 缺陷13：请求参数格式错误
**表现**：服务器返回400错误或参数无效

**可能原因**：
- 参数编码错误
- Content-Type不匹配
- 参数结构不正确
- 特殊字符未处理

**解决方案**：
```typescript
// 错误示例
const response = await httpRequest.request(url, {
  method: http.RequestMethod.POST,
  extraData: JSON.stringify({ name: 'Test' }) // 但没有设置Content-Type
})

// 正确示例
const response = await httpRequest.request(url, {
  method: http.RequestMethod.POST,
  header: {
    'Content-Type': 'application/json'
  },
  extraData: JSON.stringify({
    name: 'Test',
    age: 25
  })
})
```

## 生命周期缺陷

### 缺陷14：初始化逻辑未执行
**表现**：页面加载后初始化数据为空

**可能原因**：
- aboutToAppear未被调用
- 初始化依赖未满足
- 异步操作未等待
- 条件判断错误

**解决方案**：
```typescript
@ComponentV2
struct DataComponent {
  @Local data: string = ''

  async aboutToAppear() {
    console.log('Component appearing')
    await this.loadData()
  }

  async loadData() {
    try {
      const result = await api.getData()
      this.data = result
    } catch (error) {
      console.error('Load data failed:', error)
    }
  }

  build() {
    Text(this.data || 'Loading...')
  }
}
```

> V1 等价：`@Component struct DataComponent { @State data: string = '' }`，初始化逻辑和生命周期方法两套版本一致。

### 缺陷15：内存泄漏
**表现**：应用长时间运行后内存占用持续增长

**可能原因**：
- 组件销毁后仍有引用
- 事件监听器未清理
- 定时器未清除
- 大对象未释放

**解决方案**：
```typescript
@ComponentV2
struct SafeComponent {
  private timerId: number = -1
  private eventHandler: Function = () => {}

  aboutToAppear() {
    // 创建定时器
    this.timerId = setInterval(() => {
      console.log('Timer tick')
    }, 1000)

    // 添加事件监听
    this.eventHandler = () => {
      console.log('Event')
    }
    someEvent.on('change', this.eventHandler)
  }

  aboutToDisappear() {
    // 清理定时器
    if (this.timerId !== -1) {
      clearInterval(this.timerId)
      this.timerId = -1
    }

    // 清理事件监听
    someEvent.off('change', this.eventHandler)

    // 清空大对象
    this.eventHandler = () => {}
  }

  build() {
    Text('Safe Component')
  }
}
```

## 性能缺陷

### 缺陷16：列表渲染卡顿
**表现**：滚动长列表时卡顿明显

**可能原因**：
- 使用ForEach而非LazyForEach
- 组件复用不当
- 每次渲染创建新对象
- 复杂的计算逻辑

**解决方案**：
```typescript
// 错误示例：使用ForEach
build() {
  List() {
    ForEach(this.largeArray, (item) => {
      ListItem() {
        // 每次都创建新组件
      }
    })
  }
}

// 正确示例：使用LazyForEach
build() {
  List() {
    LazyForEach(this.dataSource, (item) => {
      ListItem() {
        // 使用@Reusable组件
        ReusableItem({ data: item })
      }
    }, (item) => item.id)
  }
}
```

### 缺陷17：频繁更新导致性能问题
**表现**：状态频繁更新，UI不断重绘

**可能原因**：
- 不必要的更新
- 状态更新粒度过细
- 合并更新未使用

**解决方案**：
```typescript
// 错误示例：频繁更新
updateValues() {
  this.value1 = 1
  this.value2 = 2
  this.value3 = 3
  this.value4 = 4 // 触发4次渲染
}

// 正确示例：批量更新
updateValues() {
  animateTo({ duration: 0 }, () => {
    this.value1 = 1
    this.value2 = 2
    this.value3 = 3
    this.value4 = 4 // 只触发1次渲染
  })
}
```

## 权限缺陷

### 缺陷18：权限申请失败
**表现**：调用权限相关API时报错

**可能原因**：
- module.json5中未声明权限
- 权限申请时机不当
- 权限级别不匹配
- 用户拒绝权限

**解决方案**：
```typescript
// 1. 在module.json5中声明
{
  "module": {
    "requestPermissions": [
      {
        "name": "ohos.permission.INTERNET",
        "reason": "$string:internet_reason",
        "usedScene": {
          "abilities": ["EntryAbility"],
          "when": "inuse"
        }
      },
      {
        "name": "ohos.permission.CAMERA"
      }
    ]
  }
}

// 2. 在代码中申请
import abilityAccessCtrl from '@ohos.abilityAccessCtrl'

async requestPermission() {
  const atManager = abilityAccessCtrl.createAtManager()
  const permissions = ['ohos.permission.CAMERA']

  const result = await atManager.requestPermissionsFromUser(
    getContext(this),
    permissions
  )

  if (result.authResults[0] === 0) {
    console.log('Permission granted')
  } else {
    console.log('Permission denied')
  }
}
```

## 诊断检查清单

### UI渲染问题检查
- [ ] build()方法是否正确返回组件
- [ ] 条件渲染逻辑是否正确
- [ ] 组件宽高和可见性是否设置
- [ ] 数据是否正确初始化

### 数据绑定问题检查
- [ ] 是否使用了正确的状态装饰器（V1: `@State` / V2: `@Local`）
- [ ] 状态更新是否在正确的时机
- [ ] 父子组件通信方式是否正确（V1: `@Link` 双向 / V2: `@Param` + `@Event` 回调）
- [ ] 嵌套对象是否使用了观察类（V1: `@Observed` + `@ObjectLink`；V2: `@ObservedV2` + `@Trace`，子组件用 `@Param` 持有）
- [ ] 全局状态是否走推荐 API（V1: `@StorageLink` / `@StorageProp`；V2: `AppStorageV2.connect`）
- [ ] 持久化是否走推荐 API（V1: `PersistentStorage.persistProp` 双层模式；V2: `PersistenceV2.globalConnect` 一站式）
- [ ] 监听属性变化的 API 是否正确（V1: `@Watch('callbackName')`；V2: `@Monitor('propName')` + `IMonitor` 参数）
- [ ] 同一组件没有混用 V1 / V2 装饰器（如 `@ComponentV2 struct` 中混入 `@State`）

### 事件处理问题检查
- [ ] 事件是否正确绑定
- [ ] 回调函数中this指向是否正确
- [ ] 事件监听器是否正确清理
- [ ] 组件是否可交互

### 路由导航问题检查
- [ ] 路由路径是否正确
- [ ] 目标页面是否注册
- [ ] 参数传递和接收是否匹配
- [ ] 错误处理是否完善

### 网络请求问题检查
- [ ] 权限是否配置
- [ ] URL和参数格式是否正确
- [ ] Content-Type是否匹配
- [ ] 错误处理是否完善

### 生命周期问题检查
- [ ] 生命周期方法是否被调用
- [ ] 初始化逻辑是否完整
- [ ] 资源是否正确清理
- [ ] 内存泄漏风险是否消除

通过这个检查清单，可以系统地排查和解决HarmonyOS应用开发中的常见缺陷。

## 装饰器版本兼容性诊断要点（V1 vs V2）

排查疑难杂症时，先确认目标项目用的是哪一套装饰器：

```bash
# V1 信号（排除同名 V2 前缀）
grep -rEI '@Component|@State|@Prop|@Link|@Provide|@Consume|@Observed|@ObjectLink|@StorageLink|@StorageProp|@LocalStorageLink|@LocalStorageProp|@Watch' \
  | grep -vE '@ComponentV2|@ObservedV2|@Provider|@Consumer|StorageV2'

# V2 信号
grep -rEI '@ComponentV2|@ObservedV2|@Local|@Param|@Once|@Provider|@Consumer|@Monitor|@Computed|AppStorageV2|PersistenceV2|@Trace'
```

**典型混用陷阱**：
- `@ComponentV2 struct X { @State count = 0 }` — V2 不允许 V1 装饰器，编译/运行报错
- V2 类用 `@Observed`（V1）但组件用 `@Param` 期望它响应 — 应改 `@ObservedV2` + `@Trace`
- 同一文件出现 `@Provide` + `@Consumer()` — 提供/消费两端必须对齐（V1: `@Provide`/`@Consume`；V2: `@Provider()`/`@Consumer()`）
- V2 `@Consumer()` 没带括号，或没给默认值 — V2 强制要求
