# RDB Entity 确定性修复 Pattern
# 适用于: ArkTS 严格模式 + @kit.ArkData relationalStore
# 触发场景: 迁移 Android RDB 实体类到 ArkTS 时
# 经验来源: EinkBro 迁移 (2026-03-26)

---

## Pattern 1: ValuesBucket 正确用法

### 错误写法 (编译报错)
```typescript
import { relationalStore, ValuesBucket } from '@kit.ArkData';

toValuesBucket(): ValuesBucket {
  const bucket = new ValuesBucket();  // ERROR: 'ValuesBucket' only refers to a type
  bucket.put('key', value);           // ERROR: ValuesBucket has no .put() method
  return bucket;
}
```

### 正确写法
```typescript
type EntityValuesBucket = Record<string, number | string | boolean | Uint8Array | null>;

toValuesBucket(): EntityValuesBucket {
  const bucket: EntityValuesBucket = {};
  bucket['key'] = value;
  return bucket;
}
```

**原因**: `ValuesBucket` 在 SDK 中是 type alias (`Record<string, ValueType>`)，不是可实例化的类。

---

## Pattern 2: fromResultSet 参数类型 (禁止 any)

### 错误写法 (编译报错)
```typescript
// ArkTS 严格模式禁止 any
static fromResultSet(resultSet: any): EntityName {  // ERROR: arkts-no-any-unknown
```

### 正确写法
```typescript
static fromResultSet(resultSet: Object): EntityName {
  const rs = resultSet as Record<string, Object>;
  const colIndex = (name: string): number =>
    (rs['getColumnIndex'] as Function)(name) as number;

  entity.field = (rs['getLong'] as Function)(colIndex('field_name')) as number;
  entity.name  = (rs['getString'] as Function)(colIndex('name')) as string;
  return entity;
}
```

**替代方案** (更简洁但运行时开销略高):
```typescript
// 使用类型断言避免 any，运行时通过 Record<string, Function> 调用
static fromResultSet(resultSet: Object): EntityName {
  const getCol = (name: string): number =>
    (resultSet as Record<string, Function>)['getColumnIndex'](name) as number;
  const getLong = (name: string): number =>
    (resultSet as Record<string, Function>)['getLong'](getCol(name)) as number;
  const getStr = (name: string): string =>
    (resultSet as Record<string, Function>)['getString'](getCol(name)) as string;

  const entity = new EntityName();
  entity.id   = getLong('id');
  entity.name = getStr('name');
  return entity;
}
```

---

## Pattern 3: // @ts-ignore 不可用

### 错误尝试
```typescript
// @ts-ignore  // ERROR: Switching off type checks with in-place comments is not allowed
static fromResultSet(resultSet: any): EntityName {
```

### 必须用 Pattern 2 替代

---

## Pattern 4: toValuesBucket() 返回类型注解

```typescript
type EntityValuesBucket = Record<string, number | string | boolean | Uint8Array | null>;

toValuesBucket(): EntityValuesBucket {
  const bucket: EntityValuesBucket = {} as EntityValuesBucket;
  // ...
  return bucket;
}
```

---

## 完整 Entity 模板

```typescript
type EntityValuesBucket = Record<string, number | string | boolean | Uint8Array | null>;

export class MyEntity {
  id: number = 0;
  name: string = '';
  value: number = 0;

  static fromResultSet(resultSet: Object): MyEntity {
    const rs = resultSet as Record<string, Object>;
    const col = (n: string): number => (rs['getColumnIndex'] as Function)(n) as number;
    const entity = new MyEntity();
    entity.id   = (rs['getLong']   as Function)(col('id'))   as number;
    entity.name = (rs['getString'] as Function)(col('name')) as string;
    entity.value = (rs['getLong']  as Function)(col('value')) as number;
    return entity;
  }

  toValuesBucket(): EntityValuesBucket {
    const bucket: EntityValuesBucket = {} as EntityValuesBucket;
    if (this.id > 0) { bucket['id'] = this.id; }
    bucket['name'] = this.name;
    bucket['value'] = this.value;
    return bucket;
  }
}
```
