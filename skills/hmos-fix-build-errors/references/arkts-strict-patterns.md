# ArkTS 严格模式确定性修复 Pattern
# 适用于: ArkTS 严格模式编译错误
# 触发场景: 编译报错 arkts-no-xxx 系列
# 经验来源: EinkBro 迁移 (2026-03-26)

---

## Pattern 1: throw 语句

### 错误写法
```typescript
throw err;                    // ERROR: arkts-limited-throw
throw 'error string';         // ERROR: arkts-limited-throw
throw unknownVariable;        // ERROR: arkts-limited-throw
```

### 正确写法
```typescript
throw new Error(String(error));
```

### 不需要修改的情况
```typescript
throw new Error('specific message');  // OK - 已经是 Error 实例
```

---

## Pattern 2: 对象字面量作为参数 (arkts-no-untyped-obj-literals)

### 错误写法
```typescript
// ERROR: Object literal must correspond to some explicitly declared class or interface
const response = await this.sendRequest(url, { contents });
```

### 正确写法 — 先声明变量
```typescript
interface GeminiRequestBody {
  contents: GeminiContent[];
}

const requestBody: GeminiRequestBody = { contents };
const response = await this.sendRequest(url, requestBody);
```

### 内联参数场景
```typescript
// 方法参数也是对象字面量，同样需要处理
httpRequest.request(url, {
  method: http.RequestMethod.POST,
  header: { 'Content-Type': 'application/json' },
  extraData: JSON.stringify(body),
  connectTimeout: 30000,
  readTimeout: 30000
});
// ^ 这种场景 SDK 方法签名本身接受 object 类型，通常 OK
// 但自定义方法调用时必须用已声明接口的变量
```

---

## Pattern 3: Margin vertical 简写不支持

### 错误写法
```typescript
.margin({ vertical: 8 });     // ERROR: 'vertical' does not exist in type
```

### 正确写法
```typescript
.margin({ top: 8, bottom: 8 });
```

### 常见场景
| 错误 | 正确 |
|------|------|
| `.margin({ vertical: 8 })` | `.margin({ top: 8, bottom: 8 })` |
| `.margin({ horizontal: 16 })` | `.margin({ left: 16, right: 16 })` |

---

## Pattern 4: List 内不能直接放 Divider

### 错误写法
```typescript
List() {
  ForEach(items, (item) => {
    ListItem() { /* ... */ }
  })
  Divider()  // ERROR: List children must be ListItem only
}
```

### 正确写法 — 用 ListItem + border
```typescript
List() {
  ForEach(items, (item) => {
    ListItem() {
      Column() {
        Text(item.name)
      }
      .width('100%')
      .padding(12)
      .border({ width: { bottom: 1 }, color: '#E0E0E0' })  // 替代 Divider 分隔线
    }
  })
}
```

### 另一种方案 — border 直接在 ListItem 上
```typescript
ListItem() {
  // content
}
.border({ width: { bottom: 1 }, color: '#E0E0E0' })
```

---

## Pattern 5: 数组字面量类型推断 (arkts-no-noninferrable-arr-literals)

### 错误写法
```typescript
const arr = [1, 2, 3].map(x => ({ val: x }));
// ERROR: Array literals must contain elements of only inferrable types
```

### 正确写法 — 显式类型
```typescript
interface Item { val: number; }
const arr: Item[] = [1, 2, 3].map((x): Item => ({ val: x }));
```

---

## Pattern 6: TextDecoder 不存在

### 错误写法
```typescript
const decoder = new TextDecoder();  // ERROR: Cannot find name 'TextDecoder'
const str = decoder.decode(data);
```

### 正确写法
```typescript
const bytes = new Uint8Array(data);
let chunk = '';
for (let i = 0; i < bytes.length; i++) {
  chunk += String.fromCharCode(bytes[i]);
}
```

---

## Pattern 7: HTTP 组件事件名

| 错误事件 | 正确事件 | 说明 |
|---------|---------|------|
| `request.on('requestEnd', ...)` | `request.on('dataEnd', ...)` | 请求结束事件 |
| `request.on('error', ...)` | 改用 Promise 的 catch | HTTP 组件 error 事件签名不标准 |

---

## Pattern 8: GeminiService 等自定义类缺少成员

### 错误场景
```typescript
class GeminiService {
  private async sendRequest(url: string, body: object): Promise<Object> {
    httpRequest.request(url, { extraData: JSON.stringify(body),
      connectTimeout: this.timeout,  // ERROR: Property 'timeout' does not exist
      readTimeout: this.timeout
    });
  }
  // timeout 属性忘记声明
}
```

### 正确 — 确保所有成员都在类体内声明
```typescript
class GeminiService {
  private timeout: number = 30000;  // 在类体内声明
  private async sendRequest(...) { ... }
}
```

---

## Pattern 9: Button 不支持 emoji

### 错误写法
```typescript
Button('X')  // 有时 emoji 渲染异常
Button('🗑')
```

### 正确写法
```typescript
Button('Del')   // 纯文本
Button('Copy')
Button('Back')
```

---

## 快速检查清单

遇到 ArkTS 编译错误时，按序检查：

1. throw → `throw new Error(String(x))`
2. 对象字面量作为参数 → 先赋值给显式类型变量
3. any / unknown → `Object` + `as Function` / `as SomeType`
4. // @ts-ignore → 禁止，必须用类型操作替代
5. ValuesBucket → 普通对象字面量 `{}`
6. margin { vertical } → `{ top, bottom }`
7. List 内 Divider → ListItem + border
8. TextDecoder → Uint8Array 遍历
9. `new SomeType()` 报错 → 检查是否是 type alias 而非 class
