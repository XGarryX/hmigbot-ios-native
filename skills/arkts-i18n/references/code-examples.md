# 代码仓验证示例（V2）

> 基于代码仓实际实现的完整代码示例。**本项目锁 V2**：所有 struct 用 `@ComponentV2`，状态用 `@Local / @Param / @ObservedV2`。i18n API（`resourceManager.getStringByNameSync` / `$r()` 等）与装饰器版本无关。
>
> V1 老项目兼容写法见 [`v1-compat.md`](./v1-compat.md)。

---

## ✅ 已验证：获取字符串资源

基于 `entry/src/main/ets/components/dialogs/ColumnsDialog.ets:9-22`

```typescript
import { common } from '@kit.AbilityKit'
import { hilog } from '@kit.PerformanceAnalysisKit'

const DOMAIN = 0xFF00
const TAG = 'ColumnsDialog'

@CustomDialog
export struct ColumnsDialog {
  dialogController: CustomDialogController

  aboutToAppear(): void {
    try {
      const context = getContext(this) as common.UIAbilityContext
      const resourceManager = context.resourceManager
      
      // ✅ 已验证：同步获取字符串资源
      const str = resourceManager.getStringByNameSync('dialog_column')
      hilog.info(DOMAIN, TAG, `Loaded string: ${str}`)
    } catch (err) {
      const error = err as Error
      hilog.error(DOMAIN, TAG, `Failed to load string: ${error.message}`)
    }
  }
}
```

**关键点**：
1. ✅ 使用 `getContext(this)` 获取 context
2. ✅ 使用 `resourceManager.getStringByNameSync()` 同步获取字符串
3. ✅ 使用 try-catch 处理错误

---

## ✅ 已验证：语言环境检测

> 基于代码仓 `components/dialogs/ColumnsDialog.ets:7-16` 的实际实现

**适用场景**：
- 需要根据语言执行不同逻辑（如复数处理）
- 不依赖未知 API 的可靠方案
- 判断当前加载的是中文还是英文资源

**完整实现**：

```typescript
@ComponentV2
export struct ColumnsDialog {
  /**
   * 检测当前语言环境是否为中文
   * @returns true 表示中文环境，false 表示非中文环境
   */
  private isChineseLocale(): boolean {
    const context = getContext(this)
    const resourceManager = context.resourceManager
    try {
      // 获取任意包含中文的字符串
      const str = resourceManager.getStringByNameSync('dialog_column')
      // 检测中文字符（Unicode 范围：0x4e00 - 0x9fa5）
      return /[\u4e00-\u9fa5]/.test(str)
    } catch {
      return false  // 默认非中文环境
    }
  }
}
```

**原理解释**：
- `[\u4e00-\u9fa5]` 匹配中文常用汉字的 Unicode 范围
- 如果字符串包含中文字符，说明加载了中文资源
- 无需依赖未知 API，可靠性高

**使用示例**：

```typescript
if (this.isChineseLocale()) {
  // 中文环境：无需复数处理
  label = `${count} 列`
} else {
  // 英文环境：需要复数处理
  label = count === 1 ? '1 column' : `${count} columns`
}
```

**注意事项**：
- ✅ 选择有明显中文特征的字符串（如 'dialog_column'、'app_name'）
- ✅ 提供 try-catch 错误处理
- ✅ 提供默认返回值（false）
- ⚠️ 字符串需要包含中文才能准确判断

---

## ✅ 已验证：复数处理完整实现

> 基于代码仓 `components/dialogs/ColumnsDialog.ets:18-31` 的实际实现

**适用场景**：
- 需要显示带数字的文本（如 "3 列"、"3 columns"）
- 英文环境需要复数处理
- 需要动态替换占位符

**完整代码示例**：

```typescript
@ComponentV2
export struct ColumnsDialog {
  @Param @Once currentColumns: number = 3

  /**
   * 获取列数标签（带复数处理）
   * @param num 列数
   * @returns 格式化后的字符串
   */
  private getColumnLabel(num: number): string {
    const context = getContext(this)
    const resourceManager = context.resourceManager
    
    try {
      // 1. 获取字符串资源（包含占位符 %d）
      let str = resourceManager.getStringByNameSync('dialog_column')
      // str = "%d 列" (中文) 或 "%d column" (英文)
      
      // 2. 替换占位符
      str = str.replace('%d', num.toString())
      
      // 3. 英文复数处理（大于1时添加 's'）
      if (num > 1 && !this.isChineseLocale() && !str.endsWith('s')) {
        str = str + 's'  // "2 column" → "2 columns"
      }
      
      return str
    } catch {
      // 4. 兜底逻辑：确保始终有返回值
      return num === 1 ? '1 column' : `${num} columns`
    }
  }
}
```

**处理流程**：
1. **获取字符串资源**：从 string.json 加载（含占位符 `%d`）
2. **替换占位符**：`str.replace('%d', value)` 替换为实际数字
3. **判断复数**：`num > 1 && !isChineseLocale() && !str.endsWith('s')`
4. **添加复数标记**：英文环境且 num > 1 时添加 's'
5. **兜底逻辑**：确保异常时也有返回值

**关键点**：
- ✅ 占位符替换：`str.replace('%d', value.toString())`
- ✅ 复数判断：`num > 1 && !isChineseLocale() && !str.endsWith('s')`
- ✅ 兜底逻辑：`catch { return num === 1 ? '1 column' : `${num} columns` }`

**支持的占位符**：

| 占位符 | 类型 | 示例 string.json | 替换结果 |
|--------|------|-----------------|----------|
| `%d` | 整数 | `"%d 列"` | `"3 列"` |
| `%s` | 字符串 | `"文件：%s"` | `"文件：photo.jpg"` |
| `%f` | 浮点数 | `"大小：%f MB"` | `"大小：1.5 MB"` |

**注意事项**：
- ⚠️ 仅支持规则复数（+s），不规则复数需特殊处理（如 child → children）
- ⚠️ 中文字符串无需复数处理
- ✅ 始终提供兜底逻辑，避免崩溃
- ✅ 使用 `toString()` 转换数字为字符串

---

## ✅ 已验证：完整业务场景示例（ColumnsDialog）

> 基于代码仓 `components/dialogs/ColumnsDialog.ets` 的完整实现

**业务场景**：让用户选择网格列数（1-20），需要：
- 显示格式化文本（"3 列" 或 "3 columns"）
- 根据语言环境处理复数
- 提供友好的用户界面

**完整代码**：

```typescript
@ComponentV2
export struct ColumnsDialog {
  @Param @Once currentColumns: number = 3
  @Event onColumnsChange: (columns: number) => void = () => {}
  @Event onCancel: () => void = () => {}

  // ✅ 技术点1：语言环境检测
  private isChineseLocale(): boolean {
    const context = getContext(this)
    const resourceManager = context.resourceManager
    try {
      const str = resourceManager.getStringByNameSync('dialog_column')
      return /[\u4e00-\u9fa5]/.test(str)
    } catch {
      return false
    }
  }

  // ✅ 技术点2：复数处理 + 占位符替换
  private getColumnLabel(num: number): string {
    const context = getContext(this)
    const resourceManager = context.resourceManager
    try {
      let str = resourceManager.getStringByNameSync('dialog_column')
      str = str.replace('%d', num.toString())
      
      // 英文复数处理
      if (num > 1 && !this.isChineseLocale() && !str.endsWith('s')) {
        str = str + 's'
      }
      return str
    } catch {
      // 兜底逻辑
      return num === 1 ? '1 column' : `${num} columns`
    }
  }

  @Builder
  columnOption(num: number) {
    Row() {
      Text(this.currentColumns === num ? '✓ ' : '  ')
        .fontSize(14)
        .fontColor('#007DFF')
        .width(24)
      Text(this.getColumnLabel(num))
        .fontSize(14)
        .fontColor(this.currentColumns === num ? '#007DFF' : '#333333')
    }
    .width('100%')
    .padding({ left: 12, right: 12, top: 10, bottom: 10 })
    .backgroundColor(this.currentColumns === num ? '#E6F0FF' : '#FFFFFF')
    .borderRadius(8)
    .margin({ bottom: 4 })
    .onClick(() => {
      this.onColumnsChange(num)
    })
  }

  build() {
    Column() {
      // ✅ 技术点3：静态资源引用
      Text($r('app.string.dialog_columns_title'))
        .fontSize(18)
        .fontWeight(FontWeight.Bold)
        .margin({ top: 20, bottom: 16 })

      Scroll() {
        Column() {
          // 动态生成 1-20 的列选项
          ForEach([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20], 
            (num: number) => {
              this.columnOption(num)
            }
          )
        }
        .width('100%')
      }
      .constraintSize({ maxHeight: 360 })
      .scrollBar(BarState.Auto)

      Button($r('app.string.dialog_cancel'))
        .width('100%')
        .height(40)
        .backgroundColor('#F0F0F0')
        .fontColor('#333333')
        .margin({ top: 16 })
        .onClick(() => this.onCancel())
    }
    .width(280)
    .padding(20)
    .backgroundColor('#FFFFFF')
    .borderRadius(16)
  }
}
```

**技术要点总结**：

| 技术点 | 代码位置 | 说明 |
|--------|---------|------|
| 语言环境检测 | `isChineseLocale():7-16` | 通过中文字符判断语言 |
| 复数处理 | `getColumnLabel():18-31` | 占位符替换 + 复数规则 |
| 占位符替换 | `getColumnLabel():23` | `str.replace('%d', value)` |
| 静态引用 | `build():56` | `$r('app.string.xxx')` |
| 动态获取 | `getColumnLabel():22` | `resourceManager.getStringByNameSync()` |
| 错误处理 | `getColumnLabel():28-30` | try-catch + 兜底逻辑 |

**文件位置**：
- 实现代码：`entry/src/main/ets/components/dialogs/ColumnsDialog.ets`
- 中文资源：`entry/src/main/resources/base/element/string.json`
- 英文资源：`entry/src/main/resources/en_US/element/string.json`
