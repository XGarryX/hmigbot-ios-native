# 自定义 EventBus 实现模板

> 替代 Android 的 greenrobot EventBus，使用 Map<string, Function[]> 实现简单的发布-订阅事件总线。
>
> **ArkTS V2 lock**：组件示例使用 `@ComponentV2`（V1 legacy: `@Component`）。EventBus 本身是纯 TS class，与装饰器版本无关。

---

## 为什么不直接用系统 EventHub？

| 特性 | 系统 EventHub | 自定义 EventBus |
|------|-------------|----------------|
| 依赖 | 需要 UIAbilityContext | 无依赖 |
| 作用域 | 绑定 Ability 生命周期 | 全局独立 |
| 类型安全 | 弱（Object） | 可自定义类型约束 |
| 适用场景 | 组件间通信（需 context） | 任意代码间通信（包括 Service、DAO） |

**结论**：UI 组件间通信优先用系统 EventHub；跨层通信（如 DAO → ViewModel → UI）用自定义 EventBus。

---

## 完整实现

```typescript
// common/EventBus.ets
type EventCallback = (data: Object) => void

export class EventBus {
  private static listeners: Map<string, EventCallback[]> = new Map()

  /**
   * 注册事件监听
   */
  static on(event: string, callback: EventCallback): void {
    const list = EventBus.listeners.get(event) || []
    list.push(callback)
    EventBus.listeners.set(event, list)
  }

  /**
   * 取消事件监听
   */
  static off(event: string, callback: EventCallback): void {
    const list = EventBus.listeners.get(event)
    if (list) {
      const index = list.indexOf(callback)
      if (index >= 0) list.splice(index, 1)
    }
  }

  /**
   * 取消某事件的所有监听
   */
  static offAll(event: string): void {
    EventBus.listeners.delete(event)
  }

  /**
   * 发送事件
   */
  static emit(event: string, data: Object = {}): void {
    const list = EventBus.listeners.get(event)
    if (list) {
      for (const cb of list) {
        cb(data)
      }
    }
  }
}
```

---

## 事件名常量定义

```typescript
// common/EventConstants.ets
export class EventConstants {
  static readonly DATABASE_UPDATED = 'database_updated'
  static readonly CONFIG_CHANGED = 'config_changed'
  static readonly MEDIA_DELETED = 'media_deleted'
  static readonly MEDIA_RENAMED = 'media_renamed'
  static readonly FAVORITES_CHANGED = 'favorites_changed'
  static readonly PLAYBACK_STATE_CHANGED = 'playback_state_changed'
}
```

---

## 使用示例

### 在 DAO 中发送事件

```typescript
async deleteMedium(id: number): Promise<void> {
  // ... 执行删除
  EventBus.emit(EventConstants.MEDIA_DELETED, { id: id })
}
```

### 在组件中监听事件

```typescript
@ComponentV2
struct MediaListView {
  private onMediaDeleted = (data: Object) => {
    const info = data as Record<string, number>
    this.refreshList()
  }

  aboutToAppear(): void {
    EventBus.on(EventConstants.MEDIA_DELETED, this.onMediaDeleted)
  }

  aboutToDisappear(): void {
    EventBus.off(EventConstants.MEDIA_DELETED, this.onMediaDeleted)
  }
}
```

**关键**：
- ✅ 在 `aboutToDisappear` 中取消监听，防止内存泄漏
- ✅ 回调函数保存为类属性（箭头函数），确保 `off` 时能匹配同一引用
- ❌ 不要在 `on` 时用匿名函数，否则无法 `off`
