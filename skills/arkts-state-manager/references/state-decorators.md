# ArkTS 状态管理装饰器完整参考（**V1 历史文档 — Legacy**）

> ⚠️ **本项目锁 ArkTS V2**。本文档为 **V1 历史参考**（`@State / @Prop / @Link / @Observed / @ObjectLink / @Provide / @Consume / @StorageLink / @Watch` 等），仅用于阅读老代码或迁移老项目时查阅。
>
> **新代码请使用 V2 装饰器**：参阅 [`v2-decorators.md`](./v2-decorators.md)（主参考）和 [`SKILL.md`](../SKILL.md)。

> 本文档覆盖 ArkTS V1 全部状态装饰器的语法、规则与完整示例。适用于 API 9 - API 12+。

---

## 目录

1. [@State](#1-state)
2. [@Prop](#2-prop)
3. [@Link](#3-link)
4. [@Provide / @Consume](#4-provide--consume)
5. [@ObjectLink + @Observed](#5-objectlink--observed)
6. [@StorageLink / @StorageProp](#6-storagelink--storageprop)
7. [@Watch](#7-watch)
8. [@Track](#8-track-api-12)
9. [LocalStorage](#9-localstorage)

---

## 1. @State

### 语法规则

```
@State 变量名: 类型 = 初始值;
```

- **必须初始化**：声明时必须赋初始值，不可为 `undefined` / `null`（除非类型显式包含）。
- **私有性**：仅组件内部可访问，不会暴露给父组件。
- **支持的类型**：`number`、`string`、`boolean`、`enum`、`object`、`class 实例`、`Array`、`Map`、`Set`、`Date`。不支持 `any` / `unknown`。
- **触发刷新的条件**：
  - 简单类型：值发生变化即刷新。
  - 对象/类：替换整个对象，或修改**第一层**属性。深层嵌套属性变化不会触发（需配合 `@Observed`）。
  - 数组：使用 `push`、`pop`、`splice`、`shift`、`unshift` 等变异方法，或整体替换。通过下标修改元素值可触发刷新。
  - Map/Set：使用 `set`、`delete`、`clear` 等方法。
  - Date：使用 `setFullYear`、`setMonth` 等方法。

### 完整示例

```typescript
// @State 基础用法：计数器
@Entry
@Component
struct StateDemo {
  // 简单类型 —— 赋值即触发刷新
  @State count: number = 0;
  // 对象类型 —— 修改第一层属性可触发刷新
  @State user: Record<string, string> = { name: '张三', role: 'dev' };
  // 数组类型 —— 变异方法或替换可触发刷新
  @State tags: string[] = ['ArkTS', 'HarmonyOS'];

  build() {
    Column({ space: 12 }) {
      Text(`计数: ${this.count}`)
      Button('增加').onClick(() => { this.count++; })

      Text(`用户: ${this.user.name}`)
      Button('改名').onClick(() => { this.user.name = '李四'; })

      Text(`标签: ${this.tags.join(', ')}`)
      Button('加标签').onClick(() => { this.tags.push('OpenHarmony'); })
    }
    .width('100%')
    .padding(20)
  }
}
```

---

## 2. @Prop

### 语法规则

```
@Prop 变量名: 类型;          // API 11 及之前（父组件传值初始化）
@Prop 变量名: 类型 = 默认值;  // API 12+（必须本地初始化）
```

- **单向数据流**：父 -> 子。父组件更新时，子组件同步更新；子组件修改不影响父组件。
- **深拷贝**：传入的值会被深拷贝，子组件持有独立副本。
- **API 12+ 变化**：`@Prop` 变量**必须提供本地初始值**，不可仅依赖父组件传入。
- **支持的类型**：与 `@State` 相同，但不支持 `Map`、`Set`（API 11 之前）。
- **触发刷新**：与 `@State` 相同的规则（因为本质上是本地状态的副本）。

### 完整示例

```typescript
// @Prop 单向同步：父组件控制进度，子组件只读展示
@Component
struct ProgressBar {
  // API 12+: 必须给默认值
  @Prop progress: number = 0;
  @Prop label: string = '进度';

  build() {
    Column({ space: 8 }) {
      Text(`${this.label}: ${this.progress}%`)
        .fontSize(16)
      Progress({ value: this.progress, total: 100 })
        .width('80%')
      // 子组件可以修改自己的副本，但不影响父组件
      Button('本地+10').onClick(() => {
        this.progress = Math.min(this.progress + 10, 100);
      })
    }
  }
}

@Entry
@Component
struct PropDemo {
  @State currentProgress: number = 30;

  build() {
    Column({ space: 20 }) {
      // 父组件传值给 @Prop
      ProgressBar({ progress: this.currentProgress, label: '下载' })
      Button('父组件+20').onClick(() => {
        this.currentProgress = Math.min(this.currentProgress + 20, 100);
      })
    }
    .padding(20)
  }
}
```

---

## 3. @Link

### 语法规则

```
@Link 变量名: 类型;
```

- **双向绑定**：父子组件共享同一份数据，任一方修改都同步到对方。
- **不可本地初始化**：`@Link` 变量禁止在声明时赋初始值，必须由父组件传入。
- **父组件传值方式**：
  - **API 12+（推荐）**：`Child({ link: this.value })`，直接传值
  - **API 11 及之前**：`Child({ link: $value })`，使用 `$` 前缀语法
  - 两种写法在 API 12 都可编译，但新项目统一使用直接传值方式
- **支持的类型**：与 `@State` 相同。

### 传值方式对比

| 场景 | API 12+ 语法 | API 11 旧语法 | 含义 |
|------|------|------|------|
| 传给 @Prop | `Child({ prop: this.value })` | 同左 | 传值（深拷贝） |
| 传给 @Link | `Child({ link: this.value })` | `Child({ link: $value })` | 传引用（双向绑定） |

### 完整示例

```typescript
// @Link 双向绑定：父子共享选中状态
@Component
struct TogglePanel {
  // @Link 不能本地初始化
  @Link isEnabled: boolean;
  @Link selectedColor: string;

  build() {
    Column({ space: 8 }) {
      Toggle({ type: ToggleType.Switch, isOn: this.isEnabled })
        .onChange((isOn: boolean) => {
          // 修改 @Link 变量，父组件同步更新
          this.isEnabled = isOn;
        })
      Text(`颜色: ${this.selectedColor}`)
      Button('切换颜色').onClick(() => {
        this.selectedColor = this.selectedColor === 'red' ? 'blue' : 'red';
      })
    }
    .padding(12)
  }
}

@Entry
@Component
struct LinkDemo {
  @State enabled: boolean = true;
  @State color: string = 'red';

  build() {
    Column({ space: 16 }) {
      Text(`父组件状态 — 开关: ${this.enabled}, 颜色: ${this.color}`)
      // API 12+（推荐）：直接传值给 @Link
      TogglePanel({ isEnabled: this.enabled, selectedColor: this.color })
      // API 11 旧写法（仍可用但不推荐）：
      // TogglePanel({ isEnabled: $enabled, selectedColor: $color })
    }
    .padding(20)
  }
}
```

---

## 4. @Provide / @Consume

### 语法规则

```
// 祖先组件提供数据
@Provide('别名') 变量名: 类型 = 初始值;
@Provide 变量名: 类型 = 初始值;        // 别名默认等于变量名

// 后代组件消费数据（无需逐层传递）
@Consume('别名') 变量名: 类型;
@Consume 变量名: 类型;                  // 按变量名匹配
```

- **跨层级双向同步**：祖先组件通过 `@Provide` 提供，任意后代组件通过 `@Consume` 获取，无需中间组件转发。
- **匹配规则**：优先按字符串别名匹配；无别名时按变量名匹配。就近匹配（最近的祖先优先）。
- **不可本地初始化**：`@Consume` 变量不能赋初始值。
- **触发刷新**：与 `@State` 规则一致。

### 完整示例

```typescript
// @Provide/@Consume 跨层级传递主题
@Entry
@Component
struct ProvideConsumeDemo {
  // 祖先组件提供主题色（使用别名 'themeColor'）
  @Provide('themeColor') theme: string = '#007AFF';
  @Provide fontSize: number = 16;

  build() {
    Column({ space: 16 }) {
      Text('顶层组件').fontColor(this.theme).fontSize(this.fontSize)
      Button('切换主题').onClick(() => {
        this.theme = this.theme === '#007AFF' ? '#FF5722' : '#007AFF';
      })
      // 中间层不需要感知 theme
      MiddleLayer()
    }
    .padding(20)
  }
}

@Component
struct MiddleLayer {
  // 中间层无需声明任何状态变量
  build() {
    Column() {
      Text('中间层（不感知主题）')
      DeepChild()
    }
  }
}

@Component
struct DeepChild {
  // 后代组件通过别名消费
  @Consume('themeColor') theme: string;
  @Consume fontSize: number;

  build() {
    Text('深层子组件 — 我能读到主题')
      .fontColor(this.theme)
      .fontSize(this.fontSize)
  }
}
```

---

## 5. @ObjectLink + @Observed

### @Observed 语法

```typescript
@Observed
class ClassName {
  属性: 类型;
  constructor(...) { ... }
}
```

- **只能装饰 class**：不能用于 `interface`、`type`、`struct`。
- **观察范围**：被 `@Observed` 装饰的类，其**第一层属性**的变化可被 `@ObjectLink` 感知。
- **继承**：父类被 `@Observed` 装饰后，子类自动继承可观察性。

### @ObjectLink 语法

```
@ObjectLink 变量名: ObservedClass;
```

- **必须配合 `@Observed` 类使用**：类型必须是被 `@Observed` 装饰的类的实例。
- **不可本地初始化**：必须由父组件传入。
- **不可整体替换**：不能 `this.obj = new Xxx()`，只能修改属性。如需替换，在父组件操作数组/对象。
- **典型场景**：`@State` 数组 + `ForEach` + 子组件 `@ObjectLink`。

### 完整示例

```typescript
// @Observed + @ObjectLink：可编辑的任务列表
@Observed
class TaskItem {
  id: number;
  title: string;
  done: boolean;

  constructor(id: number, title: string, done: boolean = false) {
    this.id = id;
    this.title = title;
    this.done = done;
  }
}

@Component
struct TaskCard {
  // @ObjectLink 接收 @Observed 类实例的引用
  @ObjectLink task: TaskItem;

  build() {
    Row({ space: 8 }) {
      Checkbox()
        .select(this.task.done)
        .onChange((val: boolean) => {
          // 修改属性可触发刷新（因为是 @Observed 类）
          this.task.done = val;
        })
      Text(this.task.title)
        .decoration({ type: this.task.done ? TextDecorationType.LineThrough : TextDecorationType.None })
    }
    .padding(8)
  }
}

@Entry
@Component
struct ObjectLinkDemo {
  @State tasks: TaskItem[] = [
    new TaskItem(1, '学习 ArkTS'),
    new TaskItem(2, '写状态管理示例'),
    new TaskItem(3, '提交代码')
  ];

  build() {
    Column({ space: 8 }) {
      ForEach(this.tasks, (item: TaskItem) => {
        // 传 @Observed 实例给 @ObjectLink
        TaskCard({ task: item })
      }, (item: TaskItem) => item.id.toString())

      Button('添加任务').onClick(() => {
        this.tasks.push(new TaskItem(Date.now(), `新任务 ${this.tasks.length + 1}`));
      })
    }
    .padding(20)
  }
}
```

---

## 6. @StorageLink / @StorageProp

### 语法规则

```
@StorageLink('key') 变量名: 类型 = 默认值;   // 双向绑定 AppStorage
@StorageProp('key') 变量名: 类型 = 默认值;   // 单向绑定 AppStorage
```

- **@StorageLink**：组件与 `AppStorage` 双向同步。组件修改 → AppStorage 更新 → 其他绑定该 key 的组件同步刷新。
- **@StorageProp**：单向同步（AppStorage → 组件）。组件本地修改不回写到 AppStorage。
- **默认值**：当 AppStorage 中不存在该 key 时，使用本地默认值并写入 AppStorage。
- **初始化顺序**：AppStorage 中已有值 → 使用已有值；不存在 → 使用本地默认值。

### 二者区别

| 特性 | @StorageLink | @StorageProp |
|------|-------------|-------------|
| 方向 | 双向（组件 <-> AppStorage） | 单向（AppStorage -> 组件） |
| 组件修改是否回写 | 是 | 否（仅修改本地副本） |
| 适用场景 | 全局共享状态（如登录态） | 只读配置（如主题色） |

### 完整示例

```typescript
// @StorageLink / @StorageProp：全局登录状态管理

// 通常在 EntryAbility 的 onCreate 中初始化
// AppStorage.setOrCreate('isLoggedIn', false);
// AppStorage.setOrCreate('username', '');
// AppStorage.setOrCreate('themeMode', 'light');

@Entry
@Component
struct StorageDemo {
  // 双向绑定：修改会同步到 AppStorage
  @StorageLink('isLoggedIn') isLoggedIn: boolean = false;
  @StorageLink('username') username: string = '';
  // 单向绑定：只读取，不回写
  @StorageProp('themeMode') themeMode: string = 'light';

  build() {
    Column({ space: 16 }) {
      if (this.isLoggedIn) {
        Text(`欢迎, ${this.username}`).fontSize(20)
        Text(`主题: ${this.themeMode}`)
        Button('退出登录').onClick(() => {
          this.isLoggedIn = false;  // 会同步到 AppStorage
          this.username = '';
        })
      } else {
        Button('登录').onClick(() => {
          this.isLoggedIn = true;
          this.username = '张三';
        })
      }
    }
    .padding(20)
  }
}
```

---

## 7. @Watch

### 语法规则

```
@State @Watch('回调方法名') 变量名: 类型 = 初始值;
```

- **搭配使用**：`@Watch` 必须与其他状态装饰器（`@State`、`@Prop`、`@Link`、`@StorageLink` 等）组合使用。
- **回调签名**：`回调方法名(propName: string): void`。参数 `propName` 是触发变化的变量名字符串。
- **调用时机**：在状态变量值变化之后、UI 重新渲染之前调用。
- **限制**：回调中不宜做耗时操作；避免在回调中修改被 `@Watch` 的同一变量（防止死循环）。

### 完整示例

```typescript
// @Watch 监听变化：搜索防抖 + 数据联动
@Entry
@Component
struct WatchDemo {
  @State @Watch('onKeywordChange') keyword: string = '';
  @State results: string[] = [];
  @State @Watch('onCountChange') count: number = 0;
  @State message: string = '';

  // 监听搜索关键词变化
  onKeywordChange(propName: string): void {
    console.info(`[Watch] ${propName} 变化为: ${this.keyword}`);
    if (this.keyword.length > 0) {
      // 模拟搜索（实际应配合防抖）
      this.results = ['结果1', '结果2', '结果3']
        .map(r => `${this.keyword} - ${r}`);
    } else {
      this.results = [];
    }
  }

  // 监听计数变化，更新消息
  onCountChange(propName: string): void {
    this.message = this.count >= 10 ? '已达上限!' : `当前: ${this.count}`;
  }

  build() {
    Column({ space: 12 }) {
      TextInput({ placeholder: '搜索...', text: this.keyword })
        .onChange((value: string) => { this.keyword = value; })
      ForEach(this.results, (item: string) => {
        Text(item).fontSize(14)
      })
      Text(this.message)
      Button(`计数 ${this.count}`).onClick(() => {
        if (this.count < 10) this.count++;
      })
    }
    .padding(20)
  }
}
```

---

## 8. @Track (API 12+)

### 语法规则

```typescript
@Observed
class MyClass {
  @Track prop1: string = '';   // 被追踪：变化时触发关联 UI 刷新
  prop2: number = 0;           // 未追踪：变化不触发 UI 刷新（但数据仍会改变）
}
```

- **属性级观察**：默认情况下，`@Observed` 类的所有第一层属性变化都触发刷新。`@Track` 让开发者**精确控制**哪些属性变化触发 UI 刷新。
- **规则**：一旦类中有任何属性使用了 `@Track`，则**只有**被 `@Track` 装饰的属性才触发 UI 刷新。
- **适用场景**：大对象中只有少数属性影响 UI，其余属性变化不应触发重绘（性能优化）。

### 完整示例

```typescript
// @Track 精确控制刷新：只有 displayName 变化时刷新 UI
@Observed
class UserProfile {
  @Track displayName: string;   // 变化触发刷新
  @Track avatarUrl: string;     // 变化触发刷新
  lastLoginTime: number;        // 变化不触发刷新（静默更新）
  requestCount: number;         // 变化不触发刷新

  constructor(name: string, avatar: string) {
    this.displayName = name;
    this.avatarUrl = avatar;
    this.lastLoginTime = Date.now();
    this.requestCount = 0;
  }
}

@Component
struct ProfileCard {
  @ObjectLink profile: UserProfile;

  build() {
    Column({ space: 8 }) {
      Image(this.profile.avatarUrl).width(60).height(60).borderRadius(30)
      Text(this.profile.displayName).fontSize(18)
      // lastLoginTime 变化不会导致此组件重新渲染
      Text(`请求次数: ${this.profile.requestCount}`).fontSize(12)
    }
  }
}

@Entry
@Component
struct TrackDemo {
  @State user: UserProfile = new UserProfile('张三', 'avatar.png');

  build() {
    Column({ space: 16 }) {
      ProfileCard({ profile: this.user })
      Button('改名(触发刷新)').onClick(() => {
        this.user.displayName = '李四';
      })
      Button('增加请求计数(不触发刷新)').onClick(() => {
        this.user.requestCount++;
        console.info(`请求次数: ${this.user.requestCount}`);
      })
    }
    .padding(20)
  }
}
```

---

## 9. LocalStorage

### 语法规则

```typescript
// 创建
let storage = new LocalStorage();
storage.setOrCreate('key', value);

// 在组件中使用
@LocalStorageLink('key') 变量名: 类型 = 默认值;   // 双向绑定
@LocalStorageProp('key') 变量名: 类型 = 默认值;   // 单向绑定
```

- **页面级状态**：与 `AppStorage`（应用级）不同，`LocalStorage` 的作用域可限定在单个页面或组件树。
- **创建方式**：手动 `new LocalStorage()`，通过 `@Entry(storage)` 注入到页面组件树。
- **子组件访问**：被注入的 `LocalStorage` 在该页面的所有子组件中可用。
- **多实例**：不同页面可以各自拥有独立的 `LocalStorage` 实例。

### LocalStorage vs AppStorage

| 特性 | LocalStorage | AppStorage |
|------|-------------|-----------|
| 作用域 | 页面 / 组件树 | 整个应用 |
| 生命周期 | 跟随页面 | 跟随应用进程 |
| 实例 | 可多个 | 全局单例 |
| 装饰器 | @LocalStorageLink / @LocalStorageProp | @StorageLink / @StorageProp |

### 完整示例

```typescript
// LocalStorage：页面级状态共享
const pageStorage: LocalStorage = new LocalStorage();
pageStorage.setOrCreate('pageTitle', '设置页');
pageStorage.setOrCreate('itemCount', 0);

@Entry(pageStorage)
@Component
struct LocalStorageDemo {
  // 双向绑定到 LocalStorage
  @LocalStorageLink('pageTitle') title: string = '';
  @LocalStorageLink('itemCount') count: number = 0;

  build() {
    Column({ space: 12 }) {
      Text(this.title).fontSize(24)
      Text(`数量: ${this.count}`)
      Button('增加').onClick(() => { this.count++; })
      // 子组件也能访问同一个 LocalStorage
      LocalStorageChild()
    }
    .padding(20)
  }
}

@Component
struct LocalStorageChild {
  // 单向绑定：只读
  @LocalStorageProp('pageTitle') title: string = '';
  @LocalStorageProp('itemCount') count: number = 0;

  build() {
    Column() {
      Text(`[子组件] 标题: ${this.title}, 数量: ${this.count}`)
        .fontSize(14)
        .fontColor('#666')
    }
  }
}
```

---

## 装饰器速查表

| 装饰器 | 方向 | 初始化 | 搭配 | 典型场景 |
|--------|------|--------|------|---------|
| @State | 组件内部 | 必须本地初始化 | 无 | 组件私有状态 |
| @Prop | 父→子（单向） | API 12+ 必须本地初始化 | 父 @State | 只读传参 |
| @Link | 父↔子（双向） | 禁止本地初始化 | 父 @State (用$传) | 双向表单绑定 |
| @Provide | 祖先提供 | 必须本地初始化 | @Consume | 跨层级共享 |
| @Consume | 后代消费 | 禁止本地初始化 | @Provide | 跨层级共享 |
| @ObjectLink | 父→子（引用） | 禁止本地初始化 | @Observed 类 | 列表项编辑 |
| @StorageLink | 组件↔AppStorage | 提供默认值 | AppStorage | 全局状态 |
| @StorageProp | AppStorage→组件 | 提供默认值 | AppStorage | 只读全局配置 |
| @Watch | 监听变化 | 无 | 其他状态装饰器 | 副作用/联动 |
| @Track | 属性级追踪 | 无 | @Observed 类 | 性能优化 |
| @LocalStorageLink | 组件↔LocalStorage | 提供默认值 | LocalStorage | 页面级状态 |
| @LocalStorageProp | LocalStorage→组件 | 提供默认值 | LocalStorage | 页面级只读 |
