# ArkTS 数据更新与 UI 刷新模式完整指南（**V1 历史文档 — Legacy**）

> ⚠️ **本项目锁 ArkTS V2**。本文档为 **V1 历史参考**（`@State / @ObjectLink` 等更新模式），仅用于阅读老代码或迁移老项目时查阅。
>
> **新代码请使用 V2 模式**：参阅 [`v2-update-patterns.md`](./v2-update-patterns.md)（主参考，含 `@Trace` 属性级精确观察）。

> 本文档详细说明 V1 装饰器下如何正确更新各类数据以触发 ArkTS UI 刷新，包括常见反模式与修正方案。

---

## 目录

1. [简单类型（number / string / boolean）](#1-简单类型)
2. [数组更新](#2-数组更新)
3. [对象更新与嵌套属性](#3-对象更新与嵌套属性)
4. [Map / Set 更新](#4-map--set-更新)
5. [@Observed 类属性更新](#5-observed-类属性更新)
6. [@Observed 对象数组更新](#6-observed-对象数组更新)
7. [常见反模式汇总](#7-常见反模式汇总)

---

## 核心原则

ArkTS 的状态管理基于**浅观察**：
- `@State` 只观察变量自身的赋值和**第一层**属性变化。
- 深层嵌套属性变化默认不可观察。
- 数组的变异方法（`push`、`splice` 等）可被观察。
- 要观察类实例的属性变化，必须使用 `@Observed` + `@ObjectLink`。

---

## 1. 简单类型

简单类型（`number`、`string`、`boolean`、`enum`）直接赋值即可触发刷新。

### 正确写法

```typescript
@Entry
@Component
struct SimpleTypeUpdate {
  @State count: number = 0;
  @State name: string = '初始值';
  @State isActive: boolean = false;

  build() {
    Column({ space: 12 }) {
      Text(`${this.count} | ${this.name} | ${this.isActive}`)

      // 直接赋值 —— 触发刷新
      Button('计数+1').onClick(() => { this.count++; })
      Button('改名').onClick(() => { this.name = '新值'; })
      Button('切换').onClick(() => { this.isActive = !this.isActive; })
    }
  }
}
```

### 错误写法

```typescript
// 错误：赋相同的值不会触发刷新
Button('无效操作').onClick(() => {
  this.count = this.count; // 值未变化，不刷新
})
```

---

## 2. 数组更新

### 2.1 添加元素

```typescript
@State list: string[] = ['A', 'B'];

// 正确：使用 push（变异方法，可触发刷新）
addItem() {
  this.list.push('C');
}

// 正确：使用 unshift 在头部添加
addToFront() {
  this.list.unshift('Z');
}

// 正确：使用 splice 在指定位置插入
insertAt(index: number) {
  this.list.splice(index, 0, '新项');
}

// 错误：展开运算符创建新数组但未赋值回去
addItemWrong() {
  [...this.list, 'C']; // 没有赋值，不触发刷新
}
```

### 2.2 删除元素

```typescript
@State items: string[] = ['A', 'B', 'C', 'D'];

// 正确：splice 删除指定位置
removeAt(index: number) {
  this.items.splice(index, 1);
}

// 正确：pop 删除最后一个
removeLast() {
  this.items.pop();
}

// 正确：shift 删除第一个
removeFirst() {
  this.items.shift();
}

// 错误：filter 返回新数组但未赋值
removeItemWrong(target: string) {
  this.items.filter(item => item !== target); // 未赋值，不刷新
}

// 正确：filter + 赋值
removeItemRight(target: string) {
  this.items = this.items.filter(item => item !== target);
}
```

### 2.3 更新指定元素

```typescript
@State scores: number[] = [80, 90, 70];

// 正确：通过下标直接修改
updateByIndex(index: number, newScore: number) {
  this.scores[index] = newScore;
}

// 正确：splice 替换
updateBySplice(index: number, newScore: number) {
  this.scores.splice(index, 1, newScore);
}
```

### 2.4 重新排序

```typescript
@State names: string[] = ['张三', '李四', '王五'];

// 正确：sort 是变异方法，可触发刷新
sortAsc() {
  this.names.sort();
}

// 正确：reverse 是变异方法
reverseList() {
  this.names.reverse();
}
```

### 2.5 过滤 / 整体替换

```typescript
@State data: number[] = [1, 2, 3, 4, 5];

// 正确：整体替换触发刷新
filterEven() {
  this.data = this.data.filter(n => n % 2 === 0);
}

// 正确：map + 赋值
doubleAll() {
  this.data = this.data.map(n => n * 2);
}

// 正确：清空数组
clearAll() {
  this.data = [];
  // 或者: this.data.splice(0, this.data.length);
}
```

### 完整示例

```typescript
@Entry
@Component
struct ArrayUpdateDemo {
  @State fruits: string[] = ['苹果', '香蕉', '橙子'];

  build() {
    Column({ space: 8 }) {
      ForEach(this.fruits, (item: string, index: number) => {
        Row({ space: 8 }) {
          Text(`${index}: ${item}`)
          Button('删').onClick(() => { this.fruits.splice(index, 1); })
        }
      }, (item: string, index: number) => `${item}_${index}`)

      Button('添加葡萄').onClick(() => { this.fruits.push('葡萄'); })
      Button('排序').onClick(() => { this.fruits.sort(); })
      Button('反转').onClick(() => { this.fruits.reverse(); })
      Button('只保留苹果').onClick(() => {
        this.fruits = this.fruits.filter(f => f === '苹果');
      })
    }
    .padding(20)
  }
}
```

---

## 3. 对象更新与嵌套属性

### 第一层属性 —— 可以直接修改

```typescript
@State user: Record<string, string | number> = {
  name: '张三',
  age: 25
};

// 正确：修改第一层属性触发刷新
updateName() {
  this.user.name = '李四';
}

// 正确：整体替换触发刷新
replaceUser() {
  this.user = { name: '王五', age: 30 };
}
```

### 嵌套属性 —— 直接修改不触发刷新

```typescript
// 数据模型
interface Address {
  city: string;
  street: string;
}

interface Person {
  name: string;
  address: Address;
}

@Entry
@Component
struct NestedObjectDemo {
  @State person: Person = {
    name: '张三',
    address: { city: '北京', street: '长安街' }
  };

  build() {
    Column({ space: 12 }) {
      Text(`${this.person.name} - ${this.person.address.city}`)

      // 错误：修改嵌套属性不触发刷新
      Button('错误: 直接改城市').onClick(() => {
        this.person.address.city = '上海'; // 不触发刷新!
      })

      // 正确方式1：替换嵌套对象（修改第一层属性）
      Button('正确1: 替换 address').onClick(() => {
        this.person.address = { city: '上海', street: '南京路' };
      })

      // 正确方式2：替换整个对象
      Button('正确2: 替换 person').onClick(() => {
        this.person = {
          name: this.person.name,
          address: { city: '上海', street: '南京路' }
        };
      })

      // 正确方式3：使用 JSON 深拷贝（简单场景可用）
      Button('正确3: 深拷贝').onClick(() => {
        let temp: Person = JSON.parse(JSON.stringify(this.person));
        temp.address.city = '上海';
        this.person = temp;
      })
    }
    .padding(20)
  }
}
```

---

## 4. Map / Set 更新

Map 和 Set 作为 `@State` 变量时，使用其自身方法即可触发刷新。

### Map 更新

```typescript
@Entry
@Component
struct MapUpdateDemo {
  @State settings: Map<string, string> = new Map([
    ['theme', 'light'],
    ['lang', 'zh']
  ]);

  build() {
    Column({ space: 12 }) {
      // 遍历显示
      ForEach(Array.from(this.settings.entries()), (entry: [string, string]) => {
        Text(`${entry[0]}: ${entry[1]}`)
      }, (entry: [string, string]) => entry[0])

      // 正确：set 方法触发刷新
      Button('切换主题').onClick(() => {
        let current = this.settings.get('theme');
        this.settings.set('theme', current === 'light' ? 'dark' : 'light');
      })

      // 正确：delete 方法触发刷新
      Button('删除语言设置').onClick(() => {
        this.settings.delete('lang');
      })

      // 正确：clear 方法触发刷新
      Button('清空').onClick(() => {
        this.settings.clear();
      })

      // 正确：新增键值对
      Button('添加字体大小').onClick(() => {
        this.settings.set('fontSize', '16');
      })
    }
    .padding(20)
  }
}
```

### Set 更新

```typescript
@Entry
@Component
struct SetUpdateDemo {
  @State selectedIds: Set<number> = new Set([1, 2, 3]);

  build() {
    Column({ space: 12 }) {
      Text(`已选: ${Array.from(this.selectedIds).join(', ')}`)

      // 正确：add 触发刷新
      Button('添加 4').onClick(() => { this.selectedIds.add(4); })

      // 正确：delete 触发刷新
      Button('移除 1').onClick(() => { this.selectedIds.delete(1); })

      // 正确：clear 触发刷新
      Button('清空').onClick(() => { this.selectedIds.clear(); })
    }
    .padding(20)
  }
}
```

---

## 5. @Observed 类属性更新

### 正确更新模式

```typescript
@Observed
class ProductInfo {
  name: string;
  price: number;
  tags: string[];

  constructor(name: string, price: number, tags: string[] = []) {
    this.name = name;
    this.price = price;
    this.tags = tags;
  }
}

@Component
struct ProductCard {
  @ObjectLink product: ProductInfo;

  build() {
    Column({ space: 8 }) {
      Text(this.product.name).fontSize(18)
      Text(`价格: ¥${this.product.price}`).fontColor('#FF5722')
      Text(`标签: ${this.product.tags.join(', ')}`)

      // 正确：修改 @Observed 类的第一层属性
      Button('涨价').onClick(() => {
        this.product.price += 10;
      })

      // 正确：修改第一层数组属性（push 是变异方法）
      Button('加标签').onClick(() => {
        this.product.tags.push('热卖');
      })

      // 错误：不能整体替换 @ObjectLink 变量
      // Button('替换').onClick(() => {
      //   this.product = new ProductInfo('新品', 100); // 编译错误!
      // })
    }
    .padding(12)
    .border({ width: 1, color: '#eee' })
  }
}
```

### 嵌套 @Observed 类

```typescript
// 嵌套 @Observed：内层属性变化也可触发刷新
@Observed
class Address {
  city: string;
  district: string;

  constructor(city: string, district: string) {
    this.city = city;
    this.district = district;
  }
}

@Observed
class Store {
  name: string;
  address: Address; // 嵌套的 @Observed 类

  constructor(name: string, address: Address) {
    this.name = name;
    this.address = address;
  }
}

@Component
struct AddressEditor {
  // 单独用 @ObjectLink 接收嵌套的 @Observed 对象
  @ObjectLink addr: Address;

  build() {
    Column({ space: 4 }) {
      Text(`城市: ${this.addr.city}`)
      Text(`区: ${this.addr.district}`)
      Button('改区').onClick(() => {
        // 正确：修改嵌套 @Observed 类的属性
        this.addr.district = '海淀区';
      })
    }
  }
}

@Component
struct StoreCard {
  @ObjectLink store: Store;

  build() {
    Column({ space: 8 }) {
      Text(this.store.name).fontSize(18)
      // 将嵌套的 @Observed 对象传给子组件
      AddressEditor({ addr: this.store.address })
    }
    .padding(12)
  }
}

@Entry
@Component
struct NestedObservedDemo {
  @State stores: Store[] = [
    new Store('旗舰店', new Address('北京', '朝阳区')),
    new Store('分店', new Address('上海', '浦东新区'))
  ];

  build() {
    Column({ space: 16 }) {
      ForEach(this.stores, (store: Store) => {
        StoreCard({ store: store })
      }, (store: Store) => store.name)
    }
    .padding(20)
  }
}
```

---

## 6. @Observed 对象数组更新

### 在父组件中操作数组

```typescript
@Observed
class TodoItem {
  id: number;
  text: string;
  done: boolean;

  constructor(id: number, text: string) {
    this.id = id;
    this.text = text;
    this.done = false;
  }
}

@Component
struct TodoCard {
  @ObjectLink todo: TodoItem;
  // 删除操作需要通过回调通知父组件
  onDelete: () => void = () => {};

  build() {
    Row({ space: 8 }) {
      Checkbox()
        .select(this.todo.done)
        .onChange((val: boolean) => {
          // 正确：修改 @Observed 类属性
          this.todo.done = val;
        })
      Text(this.todo.text)
        .decoration({
          type: this.todo.done ? TextDecorationType.LineThrough : TextDecorationType.None
        })
        .layoutWeight(1)
      Button('删').onClick(() => { this.onDelete(); })
    }
    .padding(8)
  }
}

@Entry
@Component
struct TodoListDemo {
  @State todos: TodoItem[] = [
    new TodoItem(1, '买菜'),
    new TodoItem(2, '写代码'),
    new TodoItem(3, '跑步')
  ];
  @State nextId: number = 4;

  build() {
    Column({ space: 8 }) {
      // 添加新项 —— push 触发刷新
      Button('添加任务').onClick(() => {
        this.todos.push(new TodoItem(this.nextId++, `任务${this.nextId}`));
      })

      ForEach(this.todos, (item: TodoItem, index: number) => {
        TodoCard({
          todo: item,
          // 删除操作在父组件执行（操作数组）
          onDelete: () => {
            this.todos.splice(index, 1);
          }
        })
      }, (item: TodoItem) => item.id.toString())

      // 整体替换 —— 过滤已完成的
      Button('清除已完成').onClick(() => {
        this.todos = this.todos.filter(t => !t.done);
      })

      // 排序
      Button('按文本排序').onClick(() => {
        this.todos.sort((a, b) => a.text.localeCompare(b.text));
      })
    }
    .padding(20)
  }
}
```

### 在子组件中替换数组元素（通过回调）

```typescript
@Observed
class EditableItem {
  id: number;
  value: string;

  constructor(id: number, value: string) {
    this.id = id;
    this.value = value;
  }
}

@Component
struct ItemEditor {
  @ObjectLink item: EditableItem;
  // 需要替换整个对象时，通过回调让父组件处理
  onReplace: (newItem: EditableItem) => void = () => {};

  build() {
    Row({ space: 8 }) {
      Text(this.item.value)

      // 正确：修改属性
      Button('改值').onClick(() => {
        this.item.value = '已修改';
      })

      // 正确：通过回调让父组件替换整个对象
      Button('重置').onClick(() => {
        this.onReplace(new EditableItem(this.item.id, '默认值'));
      })
    }
  }
}

@Entry
@Component
struct ReplaceItemDemo {
  @State items: EditableItem[] = [
    new EditableItem(1, '项目A'),
    new EditableItem(2, '项目B')
  ];

  build() {
    Column({ space: 8 }) {
      ForEach(this.items, (item: EditableItem, index: number) => {
        ItemEditor({
          item: item,
          onReplace: (newItem: EditableItem) => {
            // 在父组件中替换数组元素
            this.items[index] = newItem;
          }
        })
      }, (item: EditableItem) => item.id.toString())
    }
    .padding(20)
  }
}
```

---

## 7. 常见反模式汇总

### 反模式 1：修改嵌套属性期望刷新

```typescript
// 错误
@State config: { theme: { color: string } } = {
  theme: { color: 'blue' }
};
// this.config.theme.color = 'red'; // 不刷新! 嵌套第二层

// 正确：替换第一层对象
this.config.theme = { color: 'red' };

// 正确：替换整个对象
this.config = { theme: { color: 'red' } };
```

### 反模式 2：数组方法返回新数组但未赋值

```typescript
@State list: number[] = [3, 1, 2];

// 错误：map/filter/slice 返回新数组，不修改原数组
this.list.map(n => n * 2);       // 返回值被丢弃，原数组不变
this.list.filter(n => n > 1);    // 返回值被丢弃
this.list.slice(0, 2);           // 返回值被丢弃

// 正确：赋值回去
this.list = this.list.map(n => n * 2);
this.list = this.list.filter(n => n > 1);
this.list = this.list.slice(0, 2);
```

### 反模式 3：在 @ObjectLink 子组件中替换整个对象

```typescript
@Component
struct ChildComponent {
  @ObjectLink item: MyObservedClass;

  // 错误：@ObjectLink 禁止整体赋值
  resetItem() {
    // this.item = new MyObservedClass(); // 编译错误!
  }

  // 正确：逐个修改属性
  resetItem() {
    this.item.name = '';
    this.item.value = 0;
  }

  // 正确：通过回调让父组件替换
  onReset: () => void = () => {};
  resetViaParent() {
    this.onReset();
  }
}
```

### 反模式 4：异步回调中丢失 this 上下文

```typescript
// 错误：普通函数丢失 this
@State data: string = '';

aboutToAppear() {
  fetchData(function(result: string) {
    this.data = result; // this 不指向组件!
  });
}

// 正确：使用箭头函数保持 this
aboutToAppear() {
  fetchData((result: string) => {
    this.data = result; // 箭头函数保持 this 指向组件
  });
}
```

### 反模式 5：期望 @Prop 修改影响父组件

```typescript
// 错误认知：@Prop 是深拷贝，修改不影响父组件
@Component
struct ChildComp {
  @Prop value: number = 0;

  build() {
    Button(`子: ${this.value}`).onClick(() => {
      this.value++; // 只改本地副本，父组件不变!
    })
  }
}

// 如需双向同步，应使用 @Link
@Component
struct ChildCompFixed {
  @Link value: number;

  build() {
    Button(`子: ${this.value}`).onClick(() => {
      this.value++; // @Link 双向同步，父组件也变
    })
  }
}
```

### 反模式 6：不使用 @Observed 就期望类属性变化触发子组件刷新

```typescript
// 错误：普通 class 的属性变化不触发子组件刷新
class PlainItem {
  name: string = '';
  count: number = 0;
}

// 正确：必须用 @Observed 装饰
@Observed
class ObservableItem {
  name: string = '';
  count: number = 0;

  constructor(name: string, count: number) {
    this.name = name;
    this.count = count;
  }
}
```

### 反模式 7：ForEach 的 keyGenerator 不唯一导致渲染异常

```typescript
@State items: string[] = ['A', 'B', 'A']; // 有重复

// 错误：直接用 item 作为 key，重复值导致渲染问题
ForEach(this.items, (item: string) => {
  Text(item)
}, (item: string) => item) // 'A' 出现两次，key 重复!

// 正确：使用 index 保证唯一性
ForEach(this.items, (item: string, index: number) => {
  Text(item)
}, (item: string, index: number) => `${index}_${item}`)
```

---

## 总结：触发刷新的操作速查

| 数据类型 | 触发刷新的操作 | 不触发刷新的操作 |
|---------|--------------|----------------|
| number/string/boolean | 赋新值 | 赋相同值 |
| Array | push/pop/splice/shift/unshift/sort/reverse/下标赋值/整体替换 | map/filter/slice 不赋值 |
| Object | 修改第一层属性 / 整体替换 | 修改嵌套属性 |
| Map | set/delete/clear | get（只读） |
| Set | add/delete/clear | has（只读） |
| @Observed 类 | 修改被观察的属性 | 修改未被 @Track 的属性（当使用 @Track 时） |
| Date | setFullYear/setMonth/setDate 等 | 直接修改内部值 |
