# ArkTS 全局状态管理完整模板（**V1 历史文档 — Legacy**）

> ⚠️ **本项目锁 ArkTS V2**。本文档为 **V1 历史参考**（`AppStorage + @StorageLink / PersistentStorage / LocalStorage` 等），仅用于阅读老代码或迁移老项目时查阅。
>
> **新代码请使用 V2 全局状态**：参阅 [`v2-global-state.md`](./v2-global-state.md)（主参考，含 `AppStorageV2.connect / PersistenceV2.globalConnect`；V2 无 LocalStorageV2）。

> 本文档覆盖 V1 的 AppStorage、PersistentStorage、Preferences 数据持久化、LocalStorage 的完整用法与模板代码。

---

## 目录

1. [AppStorage 完整用法](#1-appstorage-完整用法)
2. [PersistentStorage 持久化存储](#2-persistentstorage-持久化存储)
3. [Preferences 数据持久化](#3-preferences-数据持久化)
4. [LocalStorage 页面级状态](#4-localstorage-页面级状态)

---

## 1. AppStorage 完整用法

`AppStorage` 是应用级的全局状态存储，在整个应用进程中共享，属于内存存储（应用退出后丢失）。

### 1.1 在 EntryAbility 中初始化

```typescript
// entry/src/main/ets/entryability/EntryAbility.ets

import { AbilityConstant, UIAbility, Want } from '@kit.AbilityKit';
import { window } from '@kit.ArkUI';

// 统一管理 AppStorage 的 key，避免硬编码字符串
export class StorageKeys {
  static readonly IS_LOGGED_IN: string = 'isLoggedIn';
  static readonly USER_NAME: string = 'userName';
  static readonly USER_TOKEN: string = 'userToken';
  static readonly THEME_MODE: string = 'themeMode';
  static readonly FONT_SIZE: string = 'fontSize';
  static readonly LANGUAGE: string = 'language';
  static readonly DEVICE_TYPE: string = 'deviceType';
}

export default class EntryAbility extends UIAbility {
  onCreate(want: Want, launchParam: AbilityConstant.LaunchParam): void {
    // 在 onCreate 中初始化全局状态（早于任何页面加载）
    AppStorage.setOrCreate(StorageKeys.IS_LOGGED_IN, false);
    AppStorage.setOrCreate(StorageKeys.USER_NAME, '');
    AppStorage.setOrCreate(StorageKeys.USER_TOKEN, '');
    AppStorage.setOrCreate(StorageKeys.THEME_MODE, 'light');
    AppStorage.setOrCreate(StorageKeys.FONT_SIZE, 16);
    AppStorage.setOrCreate(StorageKeys.LANGUAGE, 'zh-CN');
  }

  onWindowStageCreate(windowStage: window.WindowStage): void {
    // 获取设备信息并存入 AppStorage
    AppStorage.setOrCreate(StorageKeys.DEVICE_TYPE, 'phone');

    windowStage.loadContent('pages/Index', (err) => {
      if (err.code) {
        console.error(`Failed to load content: ${err.message}`);
      }
    });
  }
}
```

### 1.2 在组件中使用 @StorageLink / @StorageProp

```typescript
// pages/Index.ets

import { StorageKeys } from '../entryability/EntryAbility';

// ============================================================
// @StorageLink: 双向绑定 —— 组件修改会同步到 AppStorage
// @StorageProp: 单向绑定 —— 只从 AppStorage 读取，修改不回写
// ============================================================

@Entry
@Component
struct MainPage {
  // 双向绑定：登录状态和用户名（组件可以修改）
  @StorageLink('isLoggedIn') isLoggedIn: boolean = false;
  @StorageLink('userName') userName: string = '';
  @StorageLink('userToken') token: string = '';

  // 单向绑定：主题和字体大小（此组件只读取，不负责修改）
  @StorageProp('themeMode') themeMode: string = 'light';
  @StorageProp('fontSize') fontSize: number = 16;

  build() {
    Column({ space: 16 }) {
      // 根据全局登录状态展示不同内容
      if (this.isLoggedIn) {
        Text(`欢迎回来, ${this.userName}`)
          .fontSize(this.fontSize + 4)
        Text(`当前主题: ${this.themeMode}`)
          .fontSize(this.fontSize)
        Button('退出登录').onClick(() => {
          // 修改 @StorageLink 变量 → 自动同步到 AppStorage → 所有绑定组件刷新
          this.isLoggedIn = false;
          this.userName = '';
          this.token = '';
        })
      } else {
        Button('登录').onClick(() => {
          this.isLoggedIn = true;
          this.userName = '张三';
          this.token = 'mock_token_123';
        })
      }

      // 子组件也能读取 AppStorage
      SettingsPanel()
    }
    .padding(20)
    .width('100%')
  }
}

@Component
struct SettingsPanel {
  // 在任何子组件中都可以绑定 AppStorage
  @StorageLink('themeMode') themeMode: string = 'light';
  @StorageLink('fontSize') fontSize: number = 16;

  build() {
    Column({ space: 12 }) {
      Text('设置面板').fontSize(20).fontWeight(FontWeight.Bold)

      Row({ space: 8 }) {
        Text('主题:')
        Button(this.themeMode === 'light' ? '浅色' : '深色').onClick(() => {
          // 修改 → 所有绑定 'themeMode' 的组件同步刷新
          this.themeMode = this.themeMode === 'light' ? 'dark' : 'light';
        })
      }

      Row({ space: 8 }) {
        Text(`字体大小: ${this.fontSize}`)
        Button('+').onClick(() => { this.fontSize = Math.min(this.fontSize + 2, 30); })
        Button('-').onClick(() => { this.fontSize = Math.max(this.fontSize - 2, 12); })
      }
    }
    .padding(16)
    .border({ width: 1, color: '#ddd', radius: 8 })
  }
}
```

### 1.3 编程式访问 AppStorage

```typescript
// 在非组件代码（工具类、服务类）中访问 AppStorage

// 设置或创建（如果 key 不存在则创建，存在则更新）
AppStorage.setOrCreate('isLoggedIn', true);

// 获取值（返回 T | undefined）
let isLoggedIn: boolean | undefined = AppStorage.get<boolean>('isLoggedIn');

// 设置值（key 必须已存在，否则返回 false）
let success: boolean = AppStorage.set<string>('userName', '李四');

// 检查 key 是否存在
let hasKey: boolean = AppStorage.has('userName');

// 删除 key
let deleted: boolean = AppStorage.delete('userToken');

// 获取所有 key
let keys: IterableIterator<string> = AppStorage.keys();

// 获取存储大小
let size: number = AppStorage.size();

// 清空所有（谨慎使用）
AppStorage.clear();

// 实际场景：网络请求工具类中获取 token
class HttpUtil {
  static getAuthHeader(): Record<string, string> {
    let token: string | undefined = AppStorage.get<string>('userToken');
    if (token) {
      return { 'Authorization': `Bearer ${token}` };
    }
    return {};
  }

  // 登录成功后更新全局状态
  static onLoginSuccess(userName: string, token: string): void {
    AppStorage.setOrCreate('isLoggedIn', true);
    AppStorage.setOrCreate('userName', userName);
    AppStorage.setOrCreate('userToken', token);
  }

  // 登出时清除用户状态
  static onLogout(): void {
    AppStorage.setOrCreate('isLoggedIn', false);
    AppStorage.setOrCreate('userName', '');
    AppStorage.setOrCreate('userToken', '');
  }
}
```

### 1.4 Key 常量管理最佳实践

```typescript
// common/constants/StorageKeys.ets
// 统一管理所有 AppStorage 的 key，避免字符串拼写错误

export class StorageKeys {
  // 用户相关
  static readonly IS_LOGGED_IN: string = 'app_isLoggedIn';
  static readonly USER_NAME: string = 'app_userName';
  static readonly USER_TOKEN: string = 'app_userToken';
  static readonly USER_ID: string = 'app_userId';

  // 设置相关
  static readonly THEME_MODE: string = 'app_themeMode';
  static readonly FONT_SIZE: string = 'app_fontSize';
  static readonly LANGUAGE: string = 'app_language';

  // 设备相关
  static readonly DEVICE_TYPE: string = 'app_deviceType';
  static readonly SCREEN_WIDTH: string = 'app_screenWidth';

  // 应用状态
  static readonly IS_FIRST_LAUNCH: string = 'app_isFirstLaunch';
  static readonly LAST_SYNC_TIME: string = 'app_lastSyncTime';
}

// 使用方式：
// import { StorageKeys } from '../common/constants/StorageKeys';
// AppStorage.setOrCreate(StorageKeys.IS_LOGGED_IN, true);
// @StorageLink(StorageKeys.IS_LOGGED_IN) isLoggedIn: boolean = false;
```

---

## 2. PersistentStorage 持久化存储

`PersistentStorage` 将 `AppStorage` 中的指定 key 持久化到磁盘，应用重启后自动恢复。

### 2.1 基本用法

```typescript
// 必须在 EntryAbility 的 onCreate 中、AppStorage 初始化之前调用
// PersistentStorage 会自动与 AppStorage 双向同步

export default class EntryAbility extends UIAbility {
  onCreate(want: Want, launchParam: AbilityConstant.LaunchParam): void {
    // ========================================
    // 关键：先调用 PersistentStorage，再初始化 AppStorage
    // ========================================

    // 持久化指定的 key（如果磁盘中有值，自动恢复到 AppStorage）
    PersistentStorage.persistProp('isLoggedIn', false);
    PersistentStorage.persistProp('userName', '');
    PersistentStorage.persistProp('themeMode', 'light');
    PersistentStorage.persistProp('fontSize', 16);
    PersistentStorage.persistProp('language', 'zh-CN');
    PersistentStorage.persistProp('isFirstLaunch', true);

    // 之后可以用 AppStorage 正常读写这些 key
    // 对这些 key 的任何修改都会自动持久化
  }
}
```

### 2.2 支持的类型

```typescript
// PersistentStorage 支持的类型（均为可序列化类型）：
// - number
// - string
// - boolean
// - enum（本质是 number 或 string）

// 不支持的类型：
// - object / class 实例（不能直接持久化）
// - Array
// - Map / Set
// - undefined / null

// 对于复杂数据，可将其序列化为 JSON 字符串存储
PersistentStorage.persistProp('userSettings', '{}');

// 读取时反序列化
let settingsStr: string | undefined = AppStorage.get<string>('userSettings');
if (settingsStr) {
  let settings: Record<string, Object> = JSON.parse(settingsStr);
}

// 写入时序列化
let newSettings: Record<string, Object> = { theme: 'dark', lang: 'en' };
AppStorage.setOrCreate('userSettings', JSON.stringify(newSettings));
```

### 2.3 PersistentStorage 与 AppStorage 的关系

```typescript
// 流程图解：
//
// 应用启动时:
//   磁盘 → PersistentStorage.persistProp() → AppStorage
//   (如果磁盘有值用磁盘值; 否则用 persistProp 的默认值)
//
// 运行时修改:
//   组件 @StorageLink → AppStorage → PersistentStorage → 磁盘
//   (自动同步，无需手动操作)
//
// 应用重启时:
//   磁盘 → PersistentStorage → AppStorage → 组件
//   (自动恢复)

// 完整示例
@Entry
@Component
struct PersistentDemo {
  // 这些值在应用重启后会自动恢复
  @StorageLink('themeMode') theme: string = 'light';
  @StorageLink('fontSize') fontSize: number = 16;
  @StorageLink('isFirstLaunch') isFirst: boolean = true;

  build() {
    Column({ space: 16 }) {
      if (this.isFirst) {
        Text('首次启动，欢迎！').fontSize(24)
        Button('我知道了').onClick(() => {
          // 修改后自动持久化，下次启动不再显示
          this.isFirst = false;
        })
      }

      Text(`主题: ${this.theme}`).fontSize(this.fontSize)

      Button(`切换主题 (当前: ${this.theme})`).onClick(() => {
        // 修改 → AppStorage 更新 → PersistentStorage 自动写磁盘
        this.theme = this.theme === 'light' ? 'dark' : 'light';
      })

      Row({ space: 8 }) {
        Text(`字体: ${this.fontSize}`)
        Button('+').onClick(() => { this.fontSize += 2; })
        Button('-').onClick(() => { this.fontSize -= 2; })
      }

      Text('以上设置会在重启后保留').fontSize(12).fontColor('#999')
    }
    .padding(20)
  }
}
```

### 2.4 删除持久化数据

```typescript
// 删除单个 key 的持久化（从磁盘删除，但 AppStorage 中仍存在）
PersistentStorage.deleteProp('isFirstLaunch');

// 获取当前所有持久化的 key
let persistedKeys: Array<string> = PersistentStorage.keys();
```

---

## 3. Preferences 数据持久化

`Preferences`（用户首选项）是 HarmonyOS 提供的轻量级键值对存储，适合保存配置项、用户设置等少量数据。与 `PersistentStorage` 不同，它提供了更灵活的 API，支持异步操作，且可存储更多数据类型。

### 3.1 完整 PreferencesUtil 工具类

```typescript
// common/utils/PreferencesUtil.ets

import { preferences } from '@kit.ArkData';
import { common } from '@kit.AbilityKit';

// Preferences 工具类封装
// 提供统一的读写接口，隐藏异步复杂度

export class PreferencesUtil {
  private static prefsMap: Map<string, preferences.Preferences> = new Map();

  // ============================================================
  // 初始化：在 EntryAbility 或页面 aboutToAppear 中调用
  // ============================================================
  static async init(context: common.UIAbilityContext, storeName: string = 'default_prefs'): Promise<void> {
    if (!PreferencesUtil.prefsMap.has(storeName)) {
      let prefs = await preferences.getPreferences(context, storeName);
      PreferencesUtil.prefsMap.set(storeName, prefs);
      console.info(`[PreferencesUtil] 初始化成功: ${storeName}`);
    }
  }

  // 获取 Preferences 实例
  private static getPrefs(storeName: string = 'default_prefs'): preferences.Preferences {
    let prefs = PreferencesUtil.prefsMap.get(storeName);
    if (!prefs) {
      throw new Error(`Preferences "${storeName}" 未初始化，请先调用 PreferencesUtil.init()`);
    }
    return prefs;
  }

  // ============================================================
  // 写入操作
  // ============================================================

  // 写入字符串
  static async putString(key: string, value: string, storeName?: string): Promise<void> {
    let prefs = PreferencesUtil.getPrefs(storeName);
    await prefs.put(key, value);
    await prefs.flush(); // 刷盘
  }

  // 写入数字
  static async putNumber(key: string, value: number, storeName?: string): Promise<void> {
    let prefs = PreferencesUtil.getPrefs(storeName);
    await prefs.put(key, value);
    await prefs.flush();
  }

  // 写入布尔值
  static async putBoolean(key: string, value: boolean, storeName?: string): Promise<void> {
    let prefs = PreferencesUtil.getPrefs(storeName);
    await prefs.put(key, value);
    await prefs.flush();
  }

  // 写入对象（序列化为 JSON 字符串）
  static async putObject<T>(key: string, value: T, storeName?: string): Promise<void> {
    let prefs = PreferencesUtil.getPrefs(storeName);
    await prefs.put(key, JSON.stringify(value));
    await prefs.flush();
  }

  // ============================================================
  // 读取操作
  // ============================================================

  // 读取字符串
  static async getString(key: string, defaultValue: string = '', storeName?: string): Promise<string> {
    let prefs = PreferencesUtil.getPrefs(storeName);
    let value = await prefs.get(key, defaultValue);
    return value as string;
  }

  // 读取数字
  static async getNumber(key: string, defaultValue: number = 0, storeName?: string): Promise<number> {
    let prefs = PreferencesUtil.getPrefs(storeName);
    let value = await prefs.get(key, defaultValue);
    return value as number;
  }

  // 读取布尔值
  static async getBoolean(key: string, defaultValue: boolean = false, storeName?: string): Promise<boolean> {
    let prefs = PreferencesUtil.getPrefs(storeName);
    let value = await prefs.get(key, defaultValue);
    return value as boolean;
  }

  // 读取对象（从 JSON 字符串反序列化）
  static async getObject<T>(key: string, defaultValue: T, storeName?: string): Promise<T> {
    let prefs = PreferencesUtil.getPrefs(storeName);
    let value = await prefs.get(key, JSON.stringify(defaultValue));
    return JSON.parse(value as string) as T;
  }

  // ============================================================
  // 删除与管理
  // ============================================================

  // 删除指定 key
  static async delete(key: string, storeName?: string): Promise<void> {
    let prefs = PreferencesUtil.getPrefs(storeName);
    await prefs.delete(key);
    await prefs.flush();
  }

  // 检查 key 是否存在
  static async has(key: string, storeName?: string): Promise<boolean> {
    let prefs = PreferencesUtil.getPrefs(storeName);
    return await prefs.has(key);
  }

  // 清空所有数据
  static async clear(storeName?: string): Promise<void> {
    let prefs = PreferencesUtil.getPrefs(storeName);
    await prefs.clear();
    await prefs.flush();
  }

  // 删除整个 Preferences 文件
  static async deleteStore(context: common.UIAbilityContext, storeName: string = 'default_prefs'): Promise<void> {
    await preferences.deletePreferences(context, storeName);
    PreferencesUtil.prefsMap.delete(storeName);
  }
}
```

### 3.2 在 EntryAbility 中初始化

```typescript
// entry/src/main/ets/entryability/EntryAbility.ets

import { PreferencesUtil } from '../common/utils/PreferencesUtil';

export default class EntryAbility extends UIAbility {
  async onCreate(want: Want, launchParam: AbilityConstant.LaunchParam): Promise<void> {
    // 初始化 Preferences（可以初始化多个 store）
    await PreferencesUtil.init(this.context, 'user_settings');
    await PreferencesUtil.init(this.context, 'search_history');
    await PreferencesUtil.init(this.context, 'cache_data');
  }
}
```

### 3.3 常见使用场景

#### 场景一：用户设置

```typescript
// pages/SettingsPage.ets

import { PreferencesUtil } from '../common/utils/PreferencesUtil';

// 设置项的数据模型
interface UserSettings {
  themeMode: string;
  fontSize: number;
  notificationsEnabled: boolean;
  language: string;
}

@Entry
@Component
struct SettingsPage {
  @State settings: UserSettings = {
    themeMode: 'light',
    fontSize: 16,
    notificationsEnabled: true,
    language: 'zh-CN'
  };

  // 页面加载时从 Preferences 读取设置
  async aboutToAppear(): Promise<void> {
    this.settings = await PreferencesUtil.getObject<UserSettings>(
      'userSettings',
      this.settings,     // 默认值
      'user_settings'    // store 名称
    );
  }

  // 保存设置到 Preferences
  async saveSettings(): Promise<void> {
    await PreferencesUtil.putObject<UserSettings>(
      'userSettings',
      this.settings,
      'user_settings'
    );
    // 同步到 AppStorage 以便其他组件立即使用
    AppStorage.setOrCreate('themeMode', this.settings.themeMode);
    AppStorage.setOrCreate('fontSize', this.settings.fontSize);
  }

  build() {
    Column({ space: 16 }) {
      Text('设置').fontSize(24).fontWeight(FontWeight.Bold)

      // 主题切换
      Row() {
        Text('主题模式')
        Blank()
        Toggle({ type: ToggleType.Switch, isOn: this.settings.themeMode === 'dark' })
          .onChange(async (isOn: boolean) => {
            this.settings.themeMode = isOn ? 'dark' : 'light';
            // 立即保存
            await this.saveSettings();
          })
      }
      .width('100%')

      // 字体大小
      Row() {
        Text(`字体大小: ${this.settings.fontSize}`)
        Blank()
        Button('-').onClick(async () => {
          this.settings.fontSize = Math.max(12, this.settings.fontSize - 2);
          await this.saveSettings();
        })
        Button('+').onClick(async () => {
          this.settings.fontSize = Math.min(30, this.settings.fontSize + 2);
          await this.saveSettings();
        })
      }
      .width('100%')

      // 通知开关
      Row() {
        Text('启用通知')
        Blank()
        Toggle({ type: ToggleType.Switch, isOn: this.settings.notificationsEnabled })
          .onChange(async (isOn: boolean) => {
            this.settings.notificationsEnabled = isOn;
            await this.saveSettings();
          })
      }
      .width('100%')
    }
    .padding(20)
  }
}
```

#### 场景二：搜索历史

```typescript
// common/utils/SearchHistoryManager.ets

import { PreferencesUtil } from './PreferencesUtil';

const STORE_NAME = 'search_history';
const KEY_HISTORY = 'history_list';
const MAX_HISTORY = 20;

// 搜索历史管理器
export class SearchHistoryManager {
  // 获取搜索历史列表
  static async getHistory(): Promise<string[]> {
    return await PreferencesUtil.getObject<string[]>(KEY_HISTORY, [], STORE_NAME);
  }

  // 添加搜索记录（去重 + 限制数量）
  static async addHistory(keyword: string): Promise<string[]> {
    let history = await SearchHistoryManager.getHistory();

    // 去重：如果已存在，先移除旧的
    let existIndex = history.indexOf(keyword);
    if (existIndex !== -1) {
      history.splice(existIndex, 1);
    }

    // 添加到最前面
    history.unshift(keyword);

    // 限制最大数量
    if (history.length > MAX_HISTORY) {
      history = history.slice(0, MAX_HISTORY);
    }

    await PreferencesUtil.putObject<string[]>(KEY_HISTORY, history, STORE_NAME);
    return history;
  }

  // 删除单条记录
  static async removeHistory(keyword: string): Promise<string[]> {
    let history = await SearchHistoryManager.getHistory();
    history = history.filter(item => item !== keyword);
    await PreferencesUtil.putObject<string[]>(KEY_HISTORY, history, STORE_NAME);
    return history;
  }

  // 清空所有历史
  static async clearHistory(): Promise<void> {
    await PreferencesUtil.putObject<string[]>(KEY_HISTORY, [], STORE_NAME);
  }
}

// 使用示例组件
@Entry
@Component
struct SearchPage {
  @State keyword: string = '';
  @State history: string[] = [];

  async aboutToAppear(): Promise<void> {
    this.history = await SearchHistoryManager.getHistory();
  }

  build() {
    Column({ space: 12 }) {
      // 搜索输入
      Row({ space: 8 }) {
        TextInput({ placeholder: '搜索...', text: this.keyword })
          .layoutWeight(1)
          .onChange((value: string) => { this.keyword = value; })
        Button('搜索').onClick(async () => {
          if (this.keyword.trim().length > 0) {
            this.history = await SearchHistoryManager.addHistory(this.keyword.trim());
            // 执行搜索逻辑...
          }
        })
      }

      // 搜索历史
      if (this.history.length > 0) {
        Row() {
          Text('搜索历史').fontSize(14).fontColor('#999')
          Blank()
          Button('清空').fontSize(12).onClick(async () => {
            await SearchHistoryManager.clearHistory();
            this.history = [];
          })
        }
        .width('100%')

        Flex({ wrap: FlexWrap.Wrap }) {
          ForEach(this.history, (item: string) => {
            Text(item)
              .fontSize(14)
              .padding({ left: 12, right: 12, top: 6, bottom: 6 })
              .margin(4)
              .backgroundColor('#f5f5f5')
              .borderRadius(16)
              .onClick(() => { this.keyword = item; })
          }, (item: string) => item)
        }
      }
    }
    .padding(16)
  }
}
```

#### 场景三：缓存管理

```typescript
// common/utils/CacheManager.ets

import { PreferencesUtil } from './PreferencesUtil';

const STORE_NAME = 'cache_data';

// 带过期时间的缓存项
interface CacheEntry<T> {
  data: T;
  timestamp: number;  // 写入时间戳（毫秒）
  ttl: number;        // 生存时间（毫秒）
}

export class CacheManager {
  // 写入缓存（默认 TTL: 30 分钟）
  static async set<T>(key: string, data: T, ttlMs: number = 30 * 60 * 1000): Promise<void> {
    let entry: CacheEntry<T> = {
      data: data,
      timestamp: Date.now(),
      ttl: ttlMs
    };
    await PreferencesUtil.putObject<CacheEntry<T>>(key, entry, STORE_NAME);
  }

  // 读取缓存（过期返回 null）
  static async get<T>(key: string): Promise<T | null> {
    let exists = await PreferencesUtil.has(key, STORE_NAME);
    if (!exists) {
      return null;
    }

    let entry = await PreferencesUtil.getObject<CacheEntry<T>>(
      key,
      { data: null as T, timestamp: 0, ttl: 0 },
      STORE_NAME
    );

    // 检查是否过期
    let now = Date.now();
    if (now - entry.timestamp > entry.ttl) {
      // 过期 → 删除并返回 null
      await PreferencesUtil.delete(key, STORE_NAME);
      return null;
    }

    return entry.data;
  }

  // 删除指定缓存
  static async remove(key: string): Promise<void> {
    await PreferencesUtil.delete(key, STORE_NAME);
  }

  // 清空所有缓存
  static async clearAll(): Promise<void> {
    await PreferencesUtil.clear(STORE_NAME);
  }
}

// 使用示例：缓存 API 数据
// async function loadUserProfile(userId: string): Promise<UserProfile> {
//   let cacheKey = `profile_${userId}`;
//
//   // 先尝试读缓存
//   let cached = await CacheManager.get<UserProfile>(cacheKey);
//   if (cached) {
//     return cached;
//   }
//
//   // 缓存未命中 → 请求网络
//   let profile = await fetchProfileFromApi(userId);
//
//   // 写入缓存（TTL: 10 分钟）
//   await CacheManager.set<UserProfile>(cacheKey, profile, 10 * 60 * 1000);
//
//   return profile;
// }
```

---

## 4. LocalStorage 页面级状态

`LocalStorage` 是页面级（组件树级）的状态存储，不同页面可拥有独立的 `LocalStorage` 实例。

### 4.1 创建与注入

```typescript
// pages/DetailPage.ets

// 步骤1: 在页面文件顶层创建 LocalStorage 实例
const detailStorage: LocalStorage = new LocalStorage();
detailStorage.setOrCreate('pageTitle', '详情页');
detailStorage.setOrCreate('itemId', 0);
detailStorage.setOrCreate('isEditing', false);
detailStorage.setOrCreate('editCount', 0);

// 步骤2: 通过 @Entry 参数注入到组件树
@Entry(detailStorage)
@Component
struct DetailPage {
  // 双向绑定 LocalStorage
  @LocalStorageLink('pageTitle') title: string = '';
  @LocalStorageLink('itemId') itemId: number = 0;
  @LocalStorageLink('isEditing') isEditing: boolean = false;

  build() {
    Column({ space: 16 }) {
      Text(this.title).fontSize(24).fontWeight(FontWeight.Bold)
      Text(`ID: ${this.itemId}`)

      if (this.isEditing) {
        Text('编辑模式').fontColor('#FF5722')
        DetailEditor()
      }

      Button(this.isEditing ? '完成' : '编辑').onClick(() => {
        this.isEditing = !this.isEditing;
      })

      // 子组件也可以访问同一个 LocalStorage
      DetailFooter()
    }
    .padding(20)
  }
}
```

### 4.2 子组件访问 LocalStorage

```typescript
// 子组件自动继承 @Entry 注入的 LocalStorage

@Component
struct DetailEditor {
  // 双向绑定：修改会同步到 LocalStorage → 同页面其他组件
  @LocalStorageLink('pageTitle') title: string = '';
  @LocalStorageLink('editCount') editCount: number = 0;

  build() {
    Column({ space: 8 }) {
      TextInput({ text: this.title })
        .onChange((value: string) => {
          this.title = value;
          this.editCount++;
        })
      Text(`编辑次数: ${this.editCount}`).fontSize(12).fontColor('#999')
    }
    .padding(12)
    .border({ width: 1, color: '#eee' })
  }
}

@Component
struct DetailFooter {
  // 单向绑定：只读取，不回写
  @LocalStorageProp('pageTitle') title: string = '';
  @LocalStorageProp('editCount') editCount: number = 0;

  build() {
    Column() {
      Divider().margin({ top: 20, bottom: 10 })
      Text(`页脚 — ${this.title} (编辑${this.editCount}次)`)
        .fontSize(12)
        .fontColor('#999')
    }
  }
}
```

### 4.3 编程式操作 LocalStorage

```typescript
// 在组件代码中编程式操作 LocalStorage

@Entry(detailStorage)
@Component
struct ProgrammaticLocalStorage {
  // 获取注入的 LocalStorage 实例
  private storage: LocalStorage = new LocalStorage();

  aboutToAppear(): void {
    // 也可以在生命周期中操作
    // 注意：this.storage 不等于 detailStorage
    // 要操作 @Entry 注入的 LocalStorage，直接用模块级变量
    detailStorage.setOrCreate('itemId', 42);

    // 读取
    let title: string | undefined = detailStorage.get<string>('pageTitle');

    // 检查
    let has: boolean = detailStorage.has('pageTitle');

    // 链接（创建双向绑定的引用）
    let titleLink: SubscribedAbstractProperty<string> = detailStorage.link('pageTitle');
    titleLink.set('新标题');

    // Prop（创建单向绑定的引用）
    let titleProp: SubscribedAbstractProperty<string> = detailStorage.prop('pageTitle');
    let currentTitle: string = titleProp.get();
  }

  build() {
    Column() {
      Text('编程式操作示例')
    }
  }
}
```

### 4.4 跨页面传递 LocalStorage

```typescript
// 通过路由参数在页面间共享 LocalStorage
// （注意：LocalStorage 本身不能直接通过路由传递，但可以使用模块级变量共享）

// common/SharedStorage.ets
// 将需要跨页面共享的 LocalStorage 导出为模块变量
export const sharedStorage: LocalStorage = new LocalStorage();
sharedStorage.setOrCreate('sharedCount', 0);
sharedStorage.setOrCreate('sharedMessage', '');

// pages/PageA.ets
import { sharedStorage } from '../common/SharedStorage';
import { router } from '@kit.ArkUI';

@Entry(sharedStorage)
@Component
struct PageA {
  @LocalStorageLink('sharedCount') count: number = 0;

  build() {
    Column({ space: 16 }) {
      Text('页面 A').fontSize(24)
      Text(`共享计数: ${this.count}`)
      Button('增加').onClick(() => { this.count++; })
      Button('跳转到页面B').onClick(() => {
        router.pushUrl({ url: 'pages/PageB' });
      })
    }
    .padding(20)
  }
}

// pages/PageB.ets
import { sharedStorage } from '../common/SharedStorage';

@Entry(sharedStorage)
@Component
struct PageB {
  @LocalStorageLink('sharedCount') count: number = 0;

  build() {
    Column({ space: 16 }) {
      Text('页面 B').fontSize(24)
      // 可以看到页面 A 修改的值
      Text(`共享计数: ${this.count}`)
      Button('在 B 页面增加').onClick(() => { this.count++; })
    }
    .padding(20)
  }
}
```

---

## 存储方案对比速查表

| 特性 | AppStorage | PersistentStorage | Preferences | LocalStorage |
|------|-----------|-------------------|-------------|-------------|
| 作用域 | 应用全局 | 应用全局（持久化） | 应用全局（持久化） | 页面 / 组件树 |
| 生命周期 | 进程内 | 跨进程（磁盘） | 跨进程（磁盘） | 跟随页面 |
| 存储位置 | 内存 | 磁盘（自动） | 磁盘（手动flush） | 内存 |
| 支持类型 | 所有 JS 类型 | number/string/boolean | number/string/boolean/数组 | 所有 JS 类型 |
| 绑定装饰器 | @StorageLink/Prop | 通过 AppStorage | 无（编程式） | @LocalStorageLink/Prop |
| 适用场景 | 全局运行时状态 | 简单持久化配置 | 用户设置、历史、缓存 | 页面内共享状态 |
| 数据量 | 适中 | 少量 | 适中 | 适中 |
| 异步 API | 否 | 否 | 是 | 否 |
