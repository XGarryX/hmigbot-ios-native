# 纯静态 vs 动态语言切换方案

> 基于代码仓实际实现的方案对比分析

---

## ✅ 已验证：纯静态国际化方案

> 基于代码仓实际实现（95%+ 使用静态引用，无动态语言切换）

### 方案特点

**代码仓实践**：
- ✅ 依赖系统语言自动匹配
- ✅ 95%+ 使用 `$r('app.string.xxx')` 静态引用（270+ 处）
- ✅ 少数场景使用 `resourceManager.getStringByNameSync()` 动态获取
- ❌ 未实现运行时语言切换
- ⚠️ module.json5 未配置 `supportedLanguages`

**优点**：
- ✅ 实现简单，无需复杂状态管理
- ✅ 性能最优（编译时确定资源路径）
- ✅ 自动跟随系统语言，用户无感知
- ✅ 代码量少，维护成本低

**缺点**：
- ⚠️ 无法在应用内动态切换语言
- ⚠️ 用户需要通过系统设置更改语言
- ⚠️ 需要重启应用才能看到语言变化

### 适用场景

| 场景 | 是否适用 | 说明 |
|------|---------|------|
| 跟随系统语言 | ✅ 推荐 | 无需额外开发，自动适配 |
| 单一市场应用 | ✅ 推荐 | 简化实现，降低复杂度 |
| 国际化应用（无切换需求）| ✅ 推荐 | 依赖系统设置即可 |
| 需要应用内切换语言 | ❌ 不适用 | 需实现动态方案 |
| 需要记住用户语言偏好 | ❌ 不适用 | 需实现状态持久化 |

---

## 实现要点

### 1. 资源文件组织

**方案 1：base/ 放中文**（代码仓采用，适合单一市场）

```
entry/src/main/resources/
├── base/element/string.json       # 中文（主要市场）
└── en_US/element/string.json      # 英文
```

**工作原理**：
- 系统中文 → 找不到 zh 目录 → 使用 base/ → 显示中文 ✅
- 系统英文 → 找到 en_US → 显示英文 ✅

**方案 2：创建 zh_CN 目录**（标准做法，适合国际化应用）

```
entry/src/main/resources/
├── base/element/string.json       # Fallback（英文或其他）
├── zh_CN/element/string.json      # 中文
└── en_US/element/string.json      # 英文
```

**工作原理**：
- 系统中文 → 找到 zh_CN → 显示中文 ✅
- 系统英文 → 找到 en_US → 显示英文 ✅
- 其他语言 → 无匹配 → 使用 base/ → 显示 Fallback 语言 ✅

**关键规范**：
- ✅ base/ 和 en_US/（或 zh_CN/）的 string.json **行数完全一致**
- ✅ 所有字符串 key 在不同语言文件中**完全对应**
- ✅ 使用 `en_US/` 而非 `en/`（精确区域划分）

### 2. 静态资源引用（主流方式，95%+）

**使用场景**：Button 文本、Text 标签、Title 标题等固定文本

```typescript
// ✅ 推荐：在 build() 中使用静态引用
Text($r('app.string.app_name'))
Button($r('app.string.confirm'))
.title($r('app.string.settings_title'))
Image($r('app.media.logo'))
```

**工作原理**：
1. 编译时扫描所有 `$r()` 引用
2. 根据系统语言自动选择资源文件：
   - 中文环境 → `base/element/string.json`
   - 英文环境 → `en_US/element/string.json`
3. 运行时自动加载匹配的资源

### 3. 动态资源获取（少数场景，<5%）

**使用场景**：需要动态处理字符串（如占位符替换、复数处理）

```typescript
// ✅ 基于代码仓 ColumnsDialog.ets:22
const context = getContext(this)
const resourceManager = context.resourceManager
const str = resourceManager.getStringByNameSync('dialog_column')
```

**何时使用**：
- 需要替换占位符（如 `"%d 列"` → `"3 列"`）
- 需要处理复数（如 `"1 column"` vs `"2 columns"`）
- 需要根据字符串内容判断语言环境

### 4. module.json5 配置（可选）

```json5
{
  "module": {
    "name": "entry",
    "type": "entry",
    "description": "$string:module_desc",  // ✅ 使用 $string 引用
    "abilities": [
      {
        "name": "EntryAbility",
        "description": "$string:EntryAbility_desc",
        "label": "$string:EntryAbility_label"
      }
    ]
    // ⚠️ 当前代码仓未配置 supportedLanguages
    // 如需配置，可添加：
    // "supportedLanguages": ["zh-Hans", "en"]
  }
}
```

**配置说明**：
- ✅ `description` 和 `label` 也支持 `$string` 引用
- ⚠️ `supportedLanguages` 不是必需字段（当前代码仓未配置）
- 💡 配置后可明确告知系统应用支持的语言

---

## 对比动态语言切换方案

| 特性 | 纯静态方案 | 动态切换方案 |
|------|-----------|------------|
| **实现复杂度** | ✅ 低（仅资源文件） | ⚠️ 高（需状态管理 + UI 刷新） |
| **性能** | ✅ 最优（编译时确定） | ⚠️ 中等（运行时切换） |
| **用户体验** | ✅ 一致（自动跟随系统） | ⚠️ 需手动切换 |
| **维护成本** | ✅ 低 | ⚠️ 高 |
| **适用场景** | ✅ 大多数应用 | ⚠️ 特殊需求（如学习类应用） |
| **代码量** | ✅ 少（仅配置） | ⚠️ 多（需实现切换逻辑） |

---

## 当前代码仓选择分析

**选择方案**：纯静态方案 + `en_US/` 目录

**选择原因**：

1. **简单可靠**
   - ✅ 无需维护复杂的状态管理
   - ✅ 自动跟随系统语言，用户无感知
   - ✅ 代码量少，维护成本低

2. **性能最优**
   - ✅ 编译时确定资源路径
   - ✅ 无运行时语言切换开销
   - ✅ 资源加载效率高

3. **需求匹配**
   - ✅ 代码仓只需支持中英文
   - ✅ 无应用内切换语言需求
   - ✅ 跟随系统语言即可满足需求

**使用 `en_US/` 而非 `en/` 的原因**：

| 方案 | 优点 | 缺点 | 代码仓选择 |
|------|------|------|-----------|
| `en/` | 简单，适配所有英文区域 | 无法区分不同区域（US/GB/AU） | ❌ 未选择 |
| `en_US/` | 精确区域划分，可扩展 | 目录稍多 | ✅ 已选择 |

**结论**：
- ✅ 代码仓选择 `en_US/` 是为了精确区域划分和未来扩展性
- ✅ 纯静态方案满足当前需求，无需引入动态切换的复杂性
- 💡 如果未来需要动态切换，可参考 `dynamic-language-switch.md` 实现

---

## ⚠️ 未验证：动态语言切换

以下代码基于 HarmonyOS 理论 API，需要查证官方文档：

```typescript
import { resourceManager } from '@kit.LocalizationKit'
import { common } from '@kit.AbilityKit'

// ⚠️ 未验证 - 需要确认 API 是否存在
async function switchLanguage(lang: string): Promise<void> {
  try {
    const context = getContext(this) as common.UIAbilityContext
    const resMgr = context.resourceManager
    
    // ⚠️ 以下两个 API 需要查证官方文档
    await resMgr.setPreferredLanguage([lang])
    const langs = await resMgr.getPreferredLanguage()
    
    console.log(`Switched to: ${langs[0]}`)
  } catch (err) {
    console.error(`Failed to switch language: ${err}`)
  }
}
```

**替代方案**（如 API 不存在）：
- 方案 1：引导用户到系统设置修改语言
- 方案 2：应用内维护语言状态，手动切换资源

---

## ✅ 已验证：资源文件结构

基于 `entry/src/main/resources/` 目录结构：

```
resources/
├── base/
│   └── element/
│       └── string.json          # 中文（996 行）
├── en_US/
│   └── element/
│       └── string.json          # 英文（996 行）
├── dark/
│   └── element/
│       └── color.json           # 深色模式颜色
└── rawfile/                     # 原始文件
```

**验证结果**：
- ✅ base 和 en_US 的 string.json 行数一致（996 行）
- ✅ 两个文件的 key 完全对应
- ✅ 使用 en_US 而非 en（精确区域划分）
