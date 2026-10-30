# 资源文件结构模板

> HarmonyOS 应用完整国际化资源目录结构

---

## 完整目录结构

```
entry/src/main/resources/
├── base/                          # Fallback 资源（当系统语言无匹配时使用）
│   ├── element/
│   │   ├── string.json            # 字符串资源
│   │   ├── color.json             # 颜色资源
│   │   ├── float.json             # 浮点数资源
│   │   ├── integer.json           # 整数资源
│   │   └── plural.json            # 复数资源
│   ├── media/                      # 图片资源
│   │   ├── app_icon.png
│   │   ├── logo.png
│   │   ├── placeholder.png
│   │   └── background.png
│   ├── profile/                    # 配置资源
│   │   ├── main_pages.json
│   │   └── backup_config.json
│   └── layout/                     # 布局资源（很少用）
│
├── zh_CN/                         # 简体中文
│   └── element/
│       └── string.json
│
├── en_US/                         # 美国英文
│   └── element/
│       └── string.json
│
├── en_GB/                         # 英国英文
│   └── element/
│       └── string.json
│
├── zh_TW/                         # 繁体中文（台湾）
│   └── element/
│       └── string.json
│
├── ja/                            # 日文
│   └── element/
│       └── string.json
│
└── dark/                          # 深色模式资源（与语言无关）
    ├── element/
    │   └── color.json
    └── media/
        └── background_dark.png
```

### ⚠️ 重要：base/ 目录不是"中文目录"

**base/ 是 Fallback 目录**，当系统语言找不到匹配的资源目录时使用。

**常见误解**：
```markdown
❌ 错误理解：base/ = 中文目录
✅ 正确理解：base/ = 无匹配时的 Fallback 目录
```

**资源匹配规则**：
```
系统语言 = 中文
  ↓
查找：zh、zh_CN、zh_Hans、zh_TW 等
  ↓
找到？ → 使用该目录
找不到？ → 使用 base/（Fallback）
```

**推荐做法**：

| 方案 | base/ 内容 | 其他目录 | 适用场景 |
|------|-----------|---------|---------|
| **方案 1** | 主要市场语言（如中文） | en_US/ 等 | 单一市场应用 |
| **方案 2** | 英文或其他通用语言 | zh_CN/、en_US/ 等 | 国际化应用 |

**方案 1 示例**（代码仓采用）：
```
resources/
├── base/element/string.json       # 中文（主要市场）
└── en_US/element/string.json      # 英文
```
- 系统中文 → 无 zh 目录 → 使用 base/ → 显示中文 ✅
- 系统英文 → 找到 en_US → 显示英文 ✅

**方案 2 示例**（标准做法）：
```
resources/
├── base/element/string.json       # 英文（Fallback）
├── zh_CN/element/string.json      # 中文
└── en_US/element/string.json      # 英文
```
- 系统中文 → 找到 zh_CN → 显示中文 ✅
- 系统英文 → 找到 en_US → 显示英文 ✅
- 其他语言 → 无匹配 → 使用 base/ → 显示英文 ✅

---

## string.json 详细格式

### 基础格式

```json
{
  "string": [
    { "name": "app_name", "value": "应用名称" },
    { "name": "button_ok", "value": "确定" },
    { "name": "button_cancel", "value": "取消" }
  ]
}
```

### 带占位符的字符串

```json
{
  "string": [
    { "name": "file_count", "value": "共 %d 个文件" },
    { "name": "welcome_name", "value": "欢迎，%s" },
    { "name": "storage_used", "value": "已使用 %s，共 %s" },
    { "name": "delete_confirm", "value": "确定要删除 %s 吗？" }
  ]
}
```

### 多行字符串

```json
{
  "string": [
    { "name": "terms_of_service", "value": "服务条款\n请仔细阅读以下条款" },
    { "name": "address_multiline", "value": "北京市朝阳区\n建国路88号\nSOHO现代城" }
  ]
}
```

### 特殊字符转义

```json
{
  "string": [
    { "name": "path_format", "value": "路径：C:\\Users\\test" },
    { "name": "url_format", "value": "网址：https://example.com?q=a&b=c" },
    { "name": "quote_example", "value": "他 说：\"你好\"" }
  ]
}
```

---

## 其他资源文件格式

### color.json

```json
{
  "color": [
    { "name": "primary_color", "value": "#FF007AFF" },
    { "name": "secondary_color", "value": "#FF5858D6" },
    { "name": "background_light", "value": "#FFFFFFFF" },
    { "name": "background_dark", "value": "#FF000000" }
  ]
}
```

### float.json

```json
{
  "float": [
    { "name": "button_corner_radius", "value": "12.0" },
    { "name": "text_size_large", "value": "24.0" },
    { "name": "spacing_medium", "value": "16.0" }
  ]
}
```

### integer.json

```json
{
  "integer": [
    { "name": "grid_columns", "value": "3" },
    { "name": "max_retry_count", "value": "5" },
    { "name": "cache_expire_days", "value": "30" }
  ]
}
```

---

## media 资源组织

### 按功能分类

```
base/media/
├── icon/
│   ├── home.png
│   ├── back.png
│   └── menu.png
├── image/
│   ├── logo.png
│   ├── splash.png
│   └── placeholder.png
├── photo/
│   └── default_avatar.png
└── other/
    └── watermark.png
```

### 按语言分类（可选）

```
base/media/
└── logo.png              # 默认 logo

en/media/
└── logo.png              # 英文版 logo

ja/media/
└── logo.png              # 日文版 logo
```

---

## module.json5 语言声明模板

```json5
{
  "module": {
    "name": "entry",
    "type": "entry",
    "supportedLanguages": [
      "zh-Hans",    // 简体中文
      "zh-Hant",    // 繁体中文
      "en",         // 英文
      "ja",         // 日文
      "ko",         // 韩文
      "de",         // 德文
      "fr",         // 法文
      "es",         // 西班牙文
      "pt",         // 葡萄牙文
      "ru",         // 俄文
      "ar",         // 阿拉伯文
      "hi",         // 印地文
      "th",         // 泰文
      "vi",         // 越南文
      "id",         // 印尼文
      "ms",         // 马来文
      "tr",         // 土耳其文
      "pl",         // 波兰文
      "nl",         // 荷兰文
      "it",         // 意大利文
      "he",         // 希伯来文
      "cs",         // 捷克文
      "sv",         // 瑞典文
      "da",         // 丹麦文
      "fi",         // 芬兰文
      "no",         // 挪威文
      "el",         // 希腊文
      "hu",         // 匈牙利文
      "ro",         // 罗马尼亚文
      "sk",         // 斯洛伐克文
      "uk",         // 乌克兰文
      "bg",         // 保加利亚文
      "hr",         // 克罗地亚文
      "sl",         // 斯洛文尼亚文
      "et",         // 爱沙尼亚文
      "lv",         // 拉脱维亚文
      "lt",         // 立陶宛文
      "tl",         // 菲律宾文
      "bn",         // 孟加拉文
      "ta",         // 泰米尔文
      "mr",         // 马拉地文
      "te",         // 泰卢固文
      "ml",         // 马拉雅拉姆文
      "kn",         // 卡纳达文
      "gu",         // 古吉拉特文
      "pa",         // 旁遮普文
      "my",         // 缅甸文
      "km",         // 高棉文
      "lo",         // 老挝文
      "ne",         // 尼泊尔文
      "si",         // 僧伽罗文
      "ur",         // 乌尔都文
      "fa",         // 波斯文
      "uz",         // 乌兹别克文
      "az",         // 阿塞拜疆文
      "ka",         // 格鲁吉亚文
      "am"          // 阿姆哈拉文
    ]
  }
}
```

---

## AppScope vs Entry 资源

### AppScope 资源（应用级）

```
AppScope/
└── resources/
    ├── base/
    │   └── element/
    │       └── string.json    # 应用级字符串（如 app_name）
    └── media/
        └── app_icon.png
```

### Entry 资源（模块级）

```
entry/src/main/resources/
├── base/
│   ├── element/
│   │   └── string.json        # 模块级字符串
│   └── media/
│       └── module_icon.png
└── ...
```

### 引用优先级

1. Entry 模块资源（优先）
2. AppScope 应用资源（fallback）

### 引用方式

```typescript
// Entry 模块资源
$r('app.string.xxx')

// AppScope 应用资源
$r('entry.string.app_name')  // ⚠️ 通常不这样用
```

> 建议：所有国际化字符串放在 Entry 模块，避免混淆

---

## 当前代码仓实践分析

> 基于 SimpleGallery_Arkts 代码仓的实际实现

### ⚠️ 重要说明：代码仓的特殊实践

**代码仓采用的是"方案 1"：base/ 放中文**

```
entry/src/main/resources/
├── base/element/string.json       # 中文（主要市场）
└── en_US/element/string.json      # 英文
```

**这种做法的特点**：
- ✅ 简单：只需维护两个目录
- ✅ 适合单一市场（中文为主）
- ⚠️ 不规范：base/ 应该是 Fallback，不是"中文目录"
- ⚠️ 如果系统语言是日语等，会显示中文（base/）

**为什么可以工作？**
```
系统语言 = 中文
  ↓
查找：zh、zh_CN、zh_Hans 等
  ↓
找不到？ → 使用 base/ → 显示中文 ✅

系统语言 = 英文
  ↓
查找：en、en_US 等
  ↓
找到 en_US → 显示英文 ✅
```

### 目录结构

```
entry/src/main/resources/
├── base/                  # 中文（默认）
│   ├── element/
│   │   ├── string.json    # 996 行字符串资源
│   │   ├── color.json     # 颜色资源
│   │   └── float.json     # 浮点数资源
│   ├── media/              # 图片资源（19+ 文件）
│   │   ├── camera.png
│   │   ├── favorite.png
│   │   └── ...
│   └── profile/            # 配置资源
│
├── en_US/                 # 美国英文
│   └── element/
│       └── string.json    # 996 行（与 base 完全对应）
│
├── dark/                  # 深色模式
│   └── element/
│       └── color.json
│
└── rawfile/               # 原始文件
```

**关键特性**：
- ✅ base/ 和 en_US/ 的 string.json **行数完全一致**（996 行）
- ✅ 所有字符串 key 在两个文件中**完全对应**
- ✅ 使用 `en_US/` 而非 `en/`（精确区域划分）
- ✅ 支持深色模式（dark/ 目录）
- ⚠️ **base/ 放中文**（非标准做法，但适合单一市场应用）

**为什么中文系统显示中文？**
```
系统语言 = 中文
  ↓
查找：zh、zh_CN 等 → 找不到
  ↓
使用 base/ → base/ 里是中文 → 显示中文 ✅
```

**如果您的项目中文系统显示英文，请检查**：
1. base/element/string.json 的内容是否是中文？
2. 是否创建了 zh_CN 目录但内容是英文？

---

### 选择 en_US 而非 en 的原因

#### 方案对比

| 方案 | 目录名 | 优点 | 缺点 | 代码仓选择 |
|------|--------|------|------|-----------|
| **简单方案** | `en/` | 简单，适配所有英文区域 | 无法区分不同区域（US/GB/AU） | ❌ 未选择 |
| **精确方案** | `en_US/` | 精确区域划分，可扩展 | 目录稍多 | ✅ 已选择 |

#### 选择 en_US 的三大原因

**1. 精确区域划分**

```
en_US/    # 美国英语（代码仓已实现）
en_GB/    # 英国英语（未来可扩展）
en_AU/    # 澳大利亚英语（未来可扩展）
en_CA/    # 加拿大英语（未来可扩展）
```

- ✅ 明确标识为美国英语
- ✅ 与其他英文区域区分（如英国、澳大利亚）
- ✅ 符合 ISO 3166-1 标准

**2. 扩展性好**

当前代码仓只支持中英文，但使用 `en_US/` 为未来扩展留出空间：

```
未来可能的扩展：
├── en_US/     # 已实现
├── en_GB/     # 可添加：英国英语
├── ja/        # 可添加：日文
├── ko/        # 可添加：韩文
└── zh_TW/     # 可添加：繁体中文
```

**3. 代码仓实际情况**

- ✅ base/ 和 en_US/ 的 key **完全对应**（996 行）
- ✅ 所有翻译已完成，维护方便
- ✅ 新增语言时可直接复制结构

---

### 资源文件对应关系验证

**base/element/string.json**（中文，代码仓采用方案 1）：
```json
{
  "string": [
    { "name": "module_desc", "value": "图库 - 简单快速的相册应用" },
    { "name": "app_name", "value": "Gallery_debug" },
    { "name": "menu_sort", "value": "排序方式" },
    { "name": "all_photos", "value": "所有照片" },
    { "name": "favorites", "value": "收藏" },
    // ... 共 996 行
  ]
}
```

**en_US/element/string.json**（英文）：
```json
{
  "string": [
    { "name": "module_desc", "value": "Gallery - A simple and fast gallery app" },
    { "name": "app_name", "value": "Gallery_debug" },
    { "name": "menu_sort", "value": "Sort by" },
    { "name": "all_photos", "value": "All Photos" },
    { "name": "favorites", "value": "Favorites" },
    // ... 共 996 行
  ]
}
```

**验证结果**：
- ✅ 行数一致：996 行
- ✅ Key 完全对应
- ✅ Value 类型一致（字符串）
- ✅ 无语法错误（无尾随逗号）

---

### 代码仓实际使用方式

#### 方式 1：静态引用（95%+ 使用）

**分布**：遍布所有 `.ets` 文件（270+ 处使用）

**示例**：
```typescript
// pages/Index.ets:180
Text($r('app.string.all_photos'))

// pages/AboutPage.ets:32
.title($r('app.string.about_title'))

// components/dialogs/ColumnsDialog.ets:56
Text($r('app.string.dialog_columns_title'))
```

**特点**：
- ✅ 编译时确定资源路径
- ✅ 自动跟随系统语言
- ✅ 无需额外代码

#### 方式 2：动态获取（<5% 使用）

**位置**：`components/dialogs/ColumnsDialog.ets`

**示例**：
```typescript
// ColumnsDialog.ets:22
const resourceManager = context.resourceManager
const str = resourceManager.getStringByNameSync('dialog_column')
str = str.replace('%d', num.toString())  // 动态替换占位符
```

**使用场景**：
- 需要替换占位符（如 `"%d 列"` → `"3 列"`）
- 需要处理复数（如 `"1 column"` vs `"2 columns"`）
- 需要判断语言环境

---

### module.json5 配置现状

**当前配置**：
```json5
{
  "module": {
    "name": "entry",
    "type": "entry",
    "description": "$string:module_desc",  // ✅ 使用 $string 引用
    "abilities": [
      {
        "name": "EntryAbility",
        "description": "$string:EntryAbility_desc",  // ✅ 使用 $string
        "label": "$string:EntryAbility_label"       // ✅ 使用 $string
      }
    ]
    // ⚠️ 注意：未配置 supportedLanguages
  }
}
```

**分析**：
- ✅ description 和 label 支持国际化引用
- ⚠️ 未配置 `supportedLanguages` 字段
- 💡 当前实现仍然可以正常工作（系统自动检测）

**建议配置**（可选）：
```json5
{
  "module": {
    "supportedLanguages": ["zh-Hans", "en"]  // 明确声明支持的语言
  }
}
```

---

### 实现特点总结

| 特性 | 实现情况 | 说明 |
|------|---------|------|
| **静态引用** | ✅ 95%+ | 主流方式，编译时确定 |
| **动态获取** | ✅ <5% | 少数场景（占位符、复数） |
| **动态语言切换** | ❌ 未实现 | 依赖系统语言自动匹配 |
| **supportedLanguages** | ❌ 未配置 | 可选字段，未配置也能工作 |
| **资源完整性** | ✅ 完整 | base 和 en_US 完全对应 |
| **目录命名** | ✅ en_US/ | 精确区域划分 |

---

## ❓ 常见问题排查：中文系统显示英文

### 问题现象

系统语言是中文，但应用显示英文。

### 排查步骤

#### 步骤 1：检查 base/ 目录内容

**问题**：base/element/string.json 的内容是英文

```
❌ 错误示例：
resources/base/element/string.json
{
  "string": [
    { "name": "app_name", "value": "App Name" },  // 英文！
    { "name": "hello", "value": "Hello" }
  ]
}
```

**原因**：
- 系统中文 → 找不到 zh、zh_CN 目录 → 使用 base/
- base/ 是英文 → 显示英文 ❌

**解决方案**：

**方案 1：修改 base/ 内容为中文**（代码仓采用）
```
✅ 正确示例：
resources/base/element/string.json
{
  "string": [
    { "name": "app_name", "value": "应用名" },  // 中文！
    { "name": "hello", "value": "你好" }
  ]
}
```

**方案 2：创建 zh_CN 目录**（标准做法）
```
✅ 标准做法：
resources/
├── base/element/string.json       # Fallback（可以是英文）
├── zh_CN/element/string.json      # 中文 ✅
└── en_US/element/string.json      # 英文
```

---

#### 步骤 2：检查目录命名

**问题**：目录名包含错误字符

```
❌ 错误示例：
resources/
└── en_US(element/     ← 括号错误！
```

**解决方案**：重命名目录为 `en_US/element/`

---

#### 步骤 3：检查系统语言设置

确认设备/模拟器的系统语言是中文：
```
设置 → 系统和更新 → 语言和输入法 → 语言
→ 确认是"简体中文"或"中文（简体）"
```

---

#### 步骤 4：检查 module.json5（可选）

**问题**：supportedLanguages 配置不正确

```json5
// ❌ 可能的问题
"supportedLanguages": ["en"]  // 只声明了英文

// ✅ 正确配置
"supportedLanguages": ["zh-Hans", "en"]  // 声明中英文
```

---

### 快速诊断表格

| 检查项 | 当前状态 | 问题 | 解决方案 |
|--------|---------|------|---------|
| base/string.json 内容 | 英文 | ❌ | 改为中文 |
| zh_CN 目录 | 不存在 | ⚠️ | 创建或改 base/ |
| 目录命名 | en_US(element | ❌ | 重命名为 en_US/element |
| 系统语言 | 非中文 | ❌ | 设置为中文 |
| supportedLanguages | ["en"] | ⚠️ | 添加 "zh-Hans" |

---

### 最佳实践建议

#### 推荐方案（适用于大多数应用）

**适用场景**：
- ✅ 跟随系统语言即可
- ✅ 无应用内切换需求
- ✅ 追求简单可靠

**实现步骤**：

1. **组织资源文件**
   ```
   resources/
   ├── base/element/string.json      # 中文
   └── en_US/element/string.json     # 英文
   ```

2. **确保 key 完全对应**
   - 使用脚本或工具验证
   - 确保行数一致

3. **主流使用静态引用**
   ```typescript
   Text($r('app.string.xxx'))
   ```

4. **少数场景使用动态获取**
   ```typescript
   const str = resourceManager.getStringByNameSync('key')
   ```

5. **可选：配置 supportedLanguages**
   ```json5
   "supportedLanguages": ["zh-Hans", "en"]
   ```

#### 不推荐方案

- ❌ 使用 `en/` 而非 `en_US/`（无法精确划分）
- ❌ base 和 en 的 key 不对应（运行时错误）
- ❌ 过度使用动态获取（性能问题）
- ❌ 实现复杂的动态语言切换（除非必需）

---

### 代码仓选择结论

**选择**：纯静态方案 + `en_US/` 目录

**核心原因**：

1. **简单可靠**
   - ✅ 无需维护复杂的状态管理
   - ✅ 自动跟随系统语言
   - ✅ 代码量少，维护成本低

2. **性能最优**
   - ✅ 编译时确定资源路径
   - ✅ 无运行时语言切换开销

3. **需求匹配**
   - ✅ 只需支持中英文
   - ✅ 无应用内切换需求
   - ✅ 精确区域划分（en_US）

**适用性**：✅ 该方案适用于 **大多数不需要应用内语言切换的应用**
