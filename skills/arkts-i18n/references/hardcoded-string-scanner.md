# 硬编码字符串扫描与迁移工具

> 辅助扫描项目中硬编码字符串并迁移到 resources 的工具和脚本

---

## 扫描工具汇总

### 1. rg（ripgrep）快速扫描

```bash
# 安装：Windows 使用 winget install Andersonby.rg 或 choco install ripgrep

# 扫描 Text() 硬编码
rg "Text\(['\"]" --type ets -n -o

# 扫描 Button() 硬编码
rg "Button\(['\"]" --type ets -n -o

# 扫描 showToast() 硬编码
rg "showToast\(['\"]" --type ets -n -o

# 扫描 AlertDialog 硬编码
rg "AlertDialog" --type ets -n -o

# 扫描 promptAction 硬编码
rg "promptAction\." --type ets -n
```

### 2. PowerShell 扫描脚本

```powershell
# 扫描所有 .ets 文件中的硬编码字符串
Get-ChildItem -Recurse -Filter "*.ets" | ForEach-Object {
    $content = Get-Content $_.FullName -Raw
    # 匹配单引号字符串
    if ($content -match "Text\(['\']([^'\)]+)['\']") {
        Write-Host "$($_.FullName): $($matches[1])"
    }
}
```

### 3. Node.js 扫描脚本

```javascript
// scan-hardcoded-strings.js
const fs = require('fs');
const path = require('path');

const patterns = [
  /Text\(['"]([^'"]+)['"]\)/g,
  /Button\(['"]([^'"]+)['"]\)/g,
  /\.title\(['"]([^'"]+)['"]\)/g,
  /\.placeholder\(['"]([^'"]+)['"]\)/g,
  /\.promptText\(['"]([^'"]+)['"]\)/g,
  /showToast\(['"]([^'"]+)['"]\)/g,
];

function scanFile(filePath) {
  const content = fs.readFileSync(filePath, 'utf-8');
  const results = [];

  for (const pattern of patterns) {
    let match;
    while ((match = pattern.exec(content)) !== null) {
      const str = match[1];
      // 过滤
      if (str.length > 1 && /[\u4e00-\u9fa5a-zA-Z]/.test(str)) {
        results.push({
          file: filePath,
          line: content.substring(0, match.index).split('\n').length,
          pattern: match[0],
          value: str
        });
      }
    }
  }
  return results;
}

function scanDirectory(dir) {
  const results = [];
  const files = fs.readdirSync(dir, { withFileTypes: true });

  for (const file of files) {
    const fullPath = path.join(dir, file.name);
    if (file.isDirectory() && !file.name.startsWith('.')) {
      results.push(...scanDirectory(fullPath));
    } else if (file.name.endsWith('.ets')) {
      results.push(...scanFile(fullPath));
    }
  }
  return results;
}

const results = scanDirectory('./entry/src/main/ets');
console.log(JSON.stringify(results, null, 2));
```

---

## 过滤规则

### 必须排除的模式

```javascript
// 排除 $r() 引用
const filtered = results.filter(r => !r.value.includes('$r'));

// 排除纯数字
const filtered = results.filter(r => !/^\d+$/.test(r.value));

// 排除单字符
const filtered = results.filter(r => r.value.length > 1);

// 排除 URL
const filtered = results.filter(r => !/^https?:\/\//.test(r.value));

// 排除技术术语
const filtered = results.filter(r => !/^<[^>]+>$/.test(r.value)); // HTML 标签
const filtered = results.filter(r => !/^\{[^}]+\}$/.test(r.value)); // 变量引用

// 排除正则表达式
const filtered = results.filter(r => !/^[\[\]\{\}\(\)\.\?\+\*\^\\]$/.test(r.value));
```

---

## key 生成算法

```javascript
function generateKey(str) {
  // 1. 转小写
  let key = str.toLowerCase();

  // 2. 移除特殊字符
  key = key.replace(/[^a-z0-9\u4e00-\u9fa5]/g, '_');

  // 3. 移除连续下划线
  key = key.replace(/_+/g, '_');

  // 4. 移除首尾下划线
  key = key.replace(/^_|_$/g, '');

  // 5. 截断过长 key
  if (key.length > 30) {
    key = key.substring(0, 30);
  }

  return key || 'unknown';
}

// 示例
console.log(generateKey('确认'));           // confirm
console.log(generateKey('确定要删除吗？'));   // 确定要删除吗
console.log(generateKey('Search Files'));   // search_files
```

---

## 迁移报告模板

```markdown
# 硬编码字符串迁移报告

## 扫描时间
2024-xx-xx

## 扫描范围
- entry/src/main/ets/**/*.ets

## 发现数量
- 总计：XX 个硬编码字符串
- 已迁移：XX 个
- 待处理：XX 个

## 按文件分布
| 文件 | 数量 |
|------|------|
| page1.ets | 10 |
| page2.ets | 5 |
| dialog1.ets | 3 |

## 待迁移列表

| # | 原文本 | 建议 key | 优先级 |
|---|--------|---------|--------|
| 1 | 确认 | confirm | P0 |
| 2 | 取消 | cancel | P0 |
| 3 | 保存成功 | toast_save_success | P1 |

## 已完成迁移

| # | 原文本 | key | 文件 |
|---|--------|-----|------|
| 1 | 设置 | title_settings | SettingsPage.ets |
| 2 | 搜索 | hint_search | SearchBar.ets |
```

---

## 批量替换脚本

```javascript
// migrate-to-resources.js
const fs = require('fs');
const path = require('path');

// 迁移映射表（从扫描结果生成）
const migrationMap = {
  '确认': 'app.string.confirm',
  '取消': 'app.string.cancel',
  '保存': 'app.string.save',
  '删除': 'app.string.delete',
  '设置': 'app.string.title_settings',
  '搜索': 'app.string.hint_search',
};

function migrateFile(filePath) {
  let content = fs.readFileSync(filePath, 'utf-8');
  let modified = false;

  for (const [oldStr, newRef] of Object.entries(migrationMap)) {
    // 替换 Text('xxx')
    const textPattern = new RegExp(`Text\\(['"]${escapeRegExp(oldStr)}['"]\\)`, 'g');
    if (textPattern.test(content)) {
      content = content.replace(textPattern, `Text(\$r('${newRef}'))`);
      modified = true;
    }

    // 替换 Button('xxx')
    const buttonPattern = new RegExp(`Button\\(['"]${escapeRegExp(oldStr)}['"]\\)`, 'g');
    if (buttonPattern.test(content)) {
      content = content.replace(buttonPattern, `Button(\$r('${newRef}'))`);
      modified = true;
    }
  }

  if (modified) {
    fs.writeFileSync(filePath, content);
    console.log(`Migrated: ${filePath}`);
  }
}

function escapeRegExp(string) {
  return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

function migrateDirectory(dir) {
  const files = fs.readdirSync(dir, { withFileTypes: true });

  for (const file of files) {
    const fullPath = path.join(dir, file.name);
    if (file.isDirectory() && !file.name.startsWith('.')) {
      migrateDirectory(fullPath);
    } else if (file.name.endsWith('.ets')) {
      migrateFile(fullPath);
    }
  }
}

migrateDirectory('./entry/src/main/ets');
console.log('Migration complete!');
```

---

## string.json 更新脚本

```javascript
// update-string-json.js
const fs = require('fs');

// 新增的 key-value 对
const newEntries = [
  { name: 'confirm', value: 'Confirm' },
  { name: 'cancel', value: 'Cancel' },
  { name: 'save', value: 'Save' },
  { name: 'delete', value: 'Delete' },
];

function updateStringJson(filePath) {
  const content = fs.readFileSync(filePath, 'utf-8');
  const json = JSON.parse(content);

  // 检查是否已存在
  const existingNames = json.string.map(s => s.name);
  const toAdd = newEntries.filter(e => !existingNames.includes(e.name));

  if (toAdd.length > 0) {
    json.string.push(...toAdd);
    fs.writeFileSync(filePath, JSON.stringify(json, null, 2));
    console.log(`Updated: ${filePath} (+${toAdd.length} entries)`);
  }
}

// 更新 base 和 en_US
updateStringJson('./entry/src/main/resources/base/element/string.json');
updateStringJson('./entry/src/main/resources/en_US/element/string.json');

console.log('Done!');
```

---

## 使用流程

### 完整迁移流程

```
1. 扫描阶段
   ├── 运行 scan-hardcoded-strings.js
   ├── 生成迁移报告
   └── 人工审核

2. 准备阶段
   ├── 创建 migrationMap
   └── 验证 key 不冲突

3. 迁移阶段
   ├── 运行 update-string-json.js（更新资源文件）
   ├── 运行 migrate-to-resources.js（替换代码）
   └── 人工检查修改

4. 验证阶段
   ├── 编译项目
   ├── 运行应用检查
   └── 如有问题，回滚修改
```

### 推荐工具链

| 阶段 | 工具 | 说明 |
|------|------|------|
| 扫描 | rg / grep | 快速定位 |
| 分析 | Node.js 脚本 | 生成报告 |
| 迁移 | VS Code 多文件替换 | 人工确认 |
| 验证 | DevEco Studio 编译 | 检查错误 |

---

## 注意事项

1. **先备份**：迁移前先 commit 或备份
2. **小步快跑**：分批次迁移，每次只处理 10-20 个
3. **编译验证**：每批次迁移后立即编译检查
4. **人工审核**：自动化替换后需要人工复核
5. **key 冲突**：避免重复 key，如已存在则复用
