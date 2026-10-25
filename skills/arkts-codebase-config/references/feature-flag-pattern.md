# 功能开关（FeatureFlag）模式

本文档说明HarmonyOS应用中功能开关（FeatureFlag）的设计、实现和使用模式。

## 功能开关概念

功能开关是一种在运行时动态控制功能开启/关闭的机制，常用于：
- 灰度发布
- A/B测试
- 功能降级
- 临时关闭不稳定功能

## 功能开关实现位置

### 1. 常量文件定义

**位置示例**：
- `src/main/ets/common/Constants.ets`
- `src/main/ets/config/FeatureFlag.ets`
- `src/main/ets/utils/Config.ets`

**命名习惯**：
- `Constants.ets` - 通用常量
- `FeatureFlag.ets` - 功能开关
- `AppConfig.ets` - 应用配置
- `Settings.ets` - 设置项

## 功能开关实现模式

### 模式1：静态常量开关

最简单的功能开关形式，编译时确定。

```typescript
// Constants.ets
export class FeatureFlag {
  // 功能开关：是否开启新UI
  static readonly ENABLE_NEW_UI = true;
  
  // 功能开关：是否启用调试模式
  static readonly DEBUG_MODE = false;
  
  // 功能开关：是否启用动画
  static readonly ENABLE_ANIMATION = true;
}
```

**使用方式**：
```typescript
if (FeatureFlag.ENABLE_NEW_UI) {
  // 使用新UI
  NewComponent();
} else {
  // 使用旧UI
  OldComponent();
}
```

**特点**：
- 简单直接
- 编译时确定
- 不能动态修改
- 适合稳定功能

### 模式2：本地存储开关

使用Preferences存储开关状态，可动态修改。

```typescript
// FeatureFlag.ets
import preferences from '@ohos.data.preferences';

export class FeatureFlag {
  private static PREF_NAME = 'feature_flags';
  private static KEY_NEW_UI = 'enable_new_ui';
  private static KEY_DEBUG_MODE = 'debug_mode';
  
  // 默认值
  static readonly DEFAULT_ENABLE_NEW_UI = true;
  static readonly DEFAULT_DEBUG_MODE = false;
  
  // 获取开关状态
  static async getEnableNewUI(context: Context): Promise<boolean> {
    try {
      const prefs = await preferences.getPreferences(context, this.PREF_NAME);
      const value = await prefs.get(this.KEY_NEW_UI, this.DEFAULT_ENABLE_NEW_UI);
      return value as boolean;
    } catch (err) {
      return this.DEFAULT_ENABLE_NEW_UI;
    }
  }
  
  // 设置开关状态
  static async setEnableNewUI(context: Context, enabled: boolean): Promise<void> {
    const prefs = await preferences.getPreferences(context, this.PREF_NAME);
    await prefs.put(this.KEY_NEW_UI, enabled);
    await prefs.flush();
  }
}
```

**使用方式**：
```typescript
// 读取开关状态
const enableNewUI = await FeatureFlag.getEnableNewUI(context);

if (enableNewUI) {
  NewComponent();
} else {
  OldComponent();
}

// 修改开关状态
await FeatureFlag.setEnableNewUI(context, false);
```

**特点**：
- 可动态修改
- 状态持久化
- 适合需要用户控制的功能

### 模式3：配置文件开关

从配置文件读取开关，支持远程配置。

```typescript
// Config.ets
import { JSON } from '@kit.ArkTS';

export class AppConfig {
  private static config: Record<string, boolean> = {};
  
  // 从本地配置文件加载
  static async loadConfig(context: Context): Promise<void> {
    try {
      const file = await context.resourceManager.getRawFileContent('config/feature_flags.json');
      const content = new util.TextDecoder('utf-8').decodeWithStream(file);
      this.config = JSON.parse(content) as Record<string, boolean>;
    } catch (err) {
      console.error('Failed to load config', err);
      // 使用默认配置
      this.config = this.getDefaultConfig();
    }
  }
  
  private static getDefaultConfig(): Record<string, boolean> {
    return {
      'enable_new_ui': true,
      'enable_debug_mode': false,
      'enable_animation': true
    };
  }
  
  static getFlag(key: string, defaultValue: boolean = false): boolean {
    return this.config[key] ?? defaultValue;
  }
  
  static setFlag(key: string, value: boolean): void {
    this.config[key] = value;
  }
}
```

**配置文件**：`resources/rawfile/config/feature_flags.json`
```json
{
  "enable_new_ui": true,
  "enable_debug_mode": false,
  "enable_animation": true
}
```

**使用方式**：
```typescript
await AppConfig.loadConfig(context);

if (AppConfig.getFlag('enable_new_ui', true)) {
  NewComponent();
}
```

**特点**：
- 支持远程配置
- 可批量管理开关
- 适合灰度发布场景

### 模式4：网络配置开关

从服务器获取配置，支持A/B测试。

```typescript
// RemoteConfig.ets
import http from '@ohos.net.http';

export class RemoteConfig {
  private static config: Record<string, any> = {};
  private static defaultConfig = {
    'enable_new_ui': true,
    'experiment_group': 'A'
  };
  
  static async fetchConfig(context: Context): Promise<void> {
    try {
      const httpRequest = http.createHttp();
      const response = await httpRequest.request('https://api.example.com/config', {
        method: http.RequestMethod.GET,
        header: {
          'Content-Type': 'application/json'
        }
      });
      
      if (response.responseCode === 200) {
        this.config = JSON.parse(response.result as string);
      }
      httpRequest.destroy();
    } catch (err) {
      console.error('Failed to fetch remote config', err);
      this.config = this.defaultConfig;
    }
  }
  
  static getFlag(key: string): any {
    return this.config[key] ?? this.defaultConfig[key];
  }
  
  static getBooleanFlag(key: string, defaultValue: boolean = false): boolean {
    const value = this.getFlag(key);
    return typeof value === 'boolean' ? value : defaultValue;
  }
}
```

**使用方式**：
```typescript
// 在应用启动时获取配置
await RemoteConfig.fetchConfig(context);

// 在代码中使用
if (RemoteConfig.getBooleanFlag('enable_new_ui', true)) {
  NewComponent();
}

// A/B测试
const group = RemoteConfig.getFlag('experiment_group');
if (group === 'A') {
  // A组体验
} else {
  // B组体验
}
```

**特点**：
- 支持A/B测试
- 实时更新
- 需要网络连接
- 适合灰度发布

## 功能开关使用场景

### 场景1：新旧功能切换

```typescript
// UI切换（V2 推荐）
@ComponentV2
struct MainPage {
  @Local useNewUI: boolean = false;

  async aboutToAppear() {
    this.useNewUI = await FeatureFlag.getEnableNewUI(this.getUIContext());
  }

  build() {
    if (this.useNewUI) {
      NewUIComponent();
    } else {
      OldUIComponent();
    }
  }
}
```

> 老项目使用 V1 装饰器时，把 `@ComponentV2` 改回 `@Component`、`@Local` 改回 `@State` 即可；其余开关读取逻辑两套版本通用。

### 场景2：功能降级

```typescript
// 网络请求失败时降级
async function fetchData() {
  try {
    const data = await fetchFromNetwork();
    return data;
  } catch (err) {
    // 检查是否启用降级模式
    const enableFallback = await FeatureFlag.getEnableFallback(context);
    if (enableFallback) {
      return fetchFromCache();
    }
    throw err;
  }
}
```

### 场景3：调试模式

```typescript
// 调试日志
function debugLog(message: string) {
  if (FeatureFlag.DEBUG_MODE) {
    console.log(`[DEBUG] ${message}`);
  }
}

// 调试功能
if (FeatureFlag.DEBUG_MODE) {
  showDebugTools();
}
```

### 场景4：灰度发布

```typescript
// 根据用户ID决定是否开启新功能
async function enableNewFeatureForUser(userId: string): Promise<boolean> {
  const enabled = await RemoteConfig.getBooleanFlag('new_feature_enabled', false);
  const percentage = RemoteConfig.getFlag('new_feature_percentage', 0);
  
  if (!enabled) {
    return false;
  }
  
  // 基于用户ID的哈希值决定
  const hash = userId.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
  return (hash % 100) < percentage;
}

// 使用
const shouldUseNewFeature = await enableNewFeatureForUser(userId);
if (shouldUseNewFeature) {
  // 使用新功能
  NewFeatureComponent();
}
```

## 功能开关查找技巧

### 1. 搜索关键词
```bash
# 搜索常量定义
rg "FeatureFlag|ENABLE_|ENABLE_"
rg "static readonly.*=.*true|false"

# 搜索开关使用
rg "if.*FeatureFlag|if.*ENABLE_"
rg "getFlag|setFlag"
```

### 2. 常见文件位置
- `src/main/ets/common/Constants.ets`
- `src/main/ets/config/FeatureFlag.ets`
- `src/main/ets/utils/Config.ets`
- `src/main/ets/appconfig/`
- `resources/rawfile/config/`

### 3. 常见开关名称模式
- `ENABLE_*` - 功能开启开关
- `ENABLED_*` - 功能启用状态
- `USE_*` - 使用某个功能
- `SHOW_*` - 显示某个功能
- `DEBUG_*` - 调试相关开关
- `EXPERIMENT_*` - 实验性功能开关

## 功能开关配置入口

### 开关定义位置
1. **常量文件**：编译时确定的开关
2. **Preferences**：用户可设置的开关
3. **配置文件**：可批量配置的开关
4. **远程配置**：服务器下发的开关

### 开关读取位置
1. **组件初始化**：`aboutToAppear()`
2. **Ability启动**：`onCreate()`
3. **功能入口**：调用功能前检查
4. **定期刷新**：定时更新远程配置

### 开关修改位置
1. **设置页面**：用户手动修改
2. **自动更新**：从服务器同步
3. **开发者模式**：调试时临时修改

## 功能开关管理

### 开关命名规范
```typescript
// 推荐：使用清晰、描述性的名称
export class FeatureFlag {
  static readonly ENABLE_NEW_PAYMENT_METHOD = true;  // 清晰
  static readonly USE_CACHE_FOR_OFFLINE = false;      // 明确
}

// 避免：使用模糊的名称
export class FeatureFlag {
  static readonly FLAG1 = true;        // 不清晰
  static readonly TEMP_FLAG = false;   // 无意义
}
```

### 开关分类管理
```typescript
// 按功能分类
export class FeatureFlag {
  // UI相关
  static readonly ENABLE_NEW_UI = true;
  static readonly ENABLE_DARK_MODE = true;
  
  // 功能相关
  static readonly ENABLE_PAYMENT = true;
  static readonly ENABLE_SHOPPING_CART = true;
  
  // 性能相关
  static readonly ENABLE_CACHE = true;
  static readonly ENABLE_LAZY_LOAD = true;
  
  // 调试相关
  static readonly DEBUG_MODE = false;
  static readonly VERBOSE_LOG = false;
}
```

### 开关文档化
```typescript
/**
 * 功能开关配置
 * 
 * ENABLE_NEW_UI: 是否启用新版UI，默认开启
 * ENABLE_PAYMENT: 是否启用支付功能，默认开启
 * DEBUG_MODE: 调试模式，默认关闭（仅开发环境）
 */
export class FeatureFlag {
  static readonly ENABLE_NEW_UI = true;
  static readonly ENABLE_PAYMENT = true;
  static readonly DEBUG_MODE = false;
}
```

## 功能开关常见问题

### 问题1：开关状态不一致

**可能原因**：
- 多处存储开关状态
- 缓存未更新
- 读取时机不对

**解决方法**：
- 统一开关管理类
- 实现缓存机制
- 提供刷新接口

### 问题2：开关默认值设置错误

**可能原因**：
- 默认值未定义
- 不同环境使用相同默认值

**解决方法**：
- 明确默认值
- 根据环境设置不同默认值

### 问题3：开关影响范围过大

**可能原因**：
- 开关粒度太粗
- 一个开关控制多个功能

**解决方法**：
- 细化开关粒度
- 一个开关只控制一个功能
- 使用组合开关

## 功能开关最佳实践

### 1. 合理命名
- 使用清晰、描述性的名称
- 遵循命名规范（ENABLE_、USE_等）
- 添加注释说明用途

### 2. 默认值策略
- 默认开启稳定功能
- 默认关闭实验性功能
- 生产环境关闭调试功能

### 3. 性能考虑
- 缓存开关状态
- 避免频繁读取
- 使用静态常量提高性能

### 4. 安全考虑
- 敏感开关需要权限验证
- 防止用户随意修改
- 记录开关修改日志

### 5. 文档和注释
- 记录开关用途
- 说明默认值原因
- 提供使用示例
