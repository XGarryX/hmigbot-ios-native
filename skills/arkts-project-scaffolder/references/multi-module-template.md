# Multi-Module HarmonyOS Project Template

A production-grade multi-module project structure following the recommended layered architecture. This template demonstrates how to split a HarmonyOS app into reusable HAR library modules and an entry product module.

> **ArkTS V2 lock**: All `.ets` page / component templates emit V2 decorators (`@ComponentV2 / @Local / @Param / @Once / @Event / @ObservedV2 / @Trace / AppStorageV2 / PersistenceV2`). Module configuration files (`module.json5 / oh-package.json5 / build-profile.json5 / hvigorfile.ts`) are V1/V2 agnostic — they describe the build, not the UI runtime. For V1 (`@Component / @State / @Prop / @Link / @StorageLink`) reference, see `arkts-state-manager/references/state-decorators.md`.

## Architecture Layers

```
products/    -- Entry modules (one per device form-factor). Depends on features/.
features/    -- Feature modules (one per business domain). Depends on commons/.
commons/     -- Shared infrastructure modules. No upward dependencies.
```

Dependency direction is strictly **top-down**: products -> features -> commons.

## Full Directory Tree

```
MyMultiModuleApp/
├── AppScope/
│   ├── app.json5
│   └── resources/base/element/string.json
│
├── commons/
│   ├── common/                          # HAR: utilities, constants, models
│   │   ├── src/main/
│   │   │   ├── module.json5
│   │   │   └── ets/
│   │   │       ├── constants/
│   │   │       │   └── AppConstants.ets
│   │   │       ├── utils/
│   │   │       │   └── Logger.ets
│   │   │       └── Index.ets            # Barrel exports
│   │   ├── oh-package.json5
│   │   └── hvigorfile.ts
│   │
│   └── uicomponents/                    # HAR: shared UI components
│       ├── src/main/
│       │   ├── module.json5
│       │   └── ets/
│       │       ├── components/
│       │       │   └── CommonHeader.ets
│       │       └── Index.ets
│       ├── oh-package.json5
│       └── hvigorfile.ts
│
├── features/
│   ├── home/                            # HAR: home tab feature
│   │   ├── src/main/
│   │   │   ├── module.json5
│   │   │   └── ets/
│   │   │       ├── pages/
│   │   │       │   └── HomePage.ets
│   │   │       └── Index.ets
│   │   ├── oh-package.json5
│   │   └── hvigorfile.ts
│   │
│   └── mine/                            # HAR: profile/mine tab feature
│       ├── src/main/
│       │   ├── module.json5
│       │   └── ets/
│       │       ├── pages/
│       │       │   └── MinePage.ets
│       │       └── Index.ets
│       ├── oh-package.json5
│       └── hvigorfile.ts
│
├── products/
│   └── phone/                           # Entry module for phone
│       ├── src/main/
│       │   ├── module.json5
│       │   ├── ets/
│       │   │   ├── entryability/
│       │   │   │   └── EntryAbility.ets
│       │   │   └── pages/
│       │   │       └── Index.ets
│       │   └── resources/
│       │       └── base/
│       │           ├── profile/
│       │           │   └── main_pages.json
│       │           └── element/
│       │               ├── string.json
│       │               └── color.json
│       ├── oh-package.json5
│       └── hvigorfile.ts
│
├── build-profile.json5
├── oh-package.json5
└── hvigorfile.ts
```

---

## AppScope/app.json5

Identical structure to single-module. Shown briefly.

```json5
{
  "app": {
    "bundleName": "com.example.multimmoduleapp",
    "vendor": "example",
    "versionCode": 1000000,
    "versionName": "1.0.0",
    "icon": "$media:app_icon",
    "label": "$string:app_name",
    "minAPIVersion": 12,
    "targetAPIVersion": 12
    // no "apiReleaseType" -- it is toolchain-generated; manual config is invalid and the
    //   bare "Release" form fails the PreBuild schema (see config-reference.md app.json5).
  }
}
```

---

## Root-Level Config Files

### oh-package.json5 (root)

```json5
{
  "name": "multi-module-app",
  "version": "1.0.0",
  "description": "Multi-module HarmonyOS application.",
  "main": "",
  "author": "",
  "license": "Apache-2.0",
  "dependencies": {},
  "devDependencies": {}
}
```

### build-profile.json5 (root)

```json5
{
  "app": {
    "signingConfigs": [
      {
        "name": "default",
        "material": {
          "certpath": "",
          "storeFile": "",
          "keyAlias": "",
          "storePassword": "",
          "keyPassword": "",
          "profile": "",
          "signAlg": "SHA256withECDSA"
        }
      }
    ],
    "products": [
      {
        "name": "default",
        "signingConfig": "default",
        "compileSdkVersion": 12,
        "compatibleSdkVersion": 12,
        "runtimeOS": "HarmonyOS"
      }
    ]
  },
  "modules": [
    // --- Commons layer ---
    {
      "name": "common",
      "srcPath": "./commons/common",
      "targets": [
        {
          "name": "default",
          "applyToProducts": ["default"]
        }
      ]
    },
    {
      "name": "uicomponents",
      "srcPath": "./commons/uicomponents",
      "targets": [
        {
          "name": "default",
          "applyToProducts": ["default"]
        }
      ]
    },
    // --- Features layer ---
    {
      "name": "home",
      "srcPath": "./features/home",
      "targets": [
        {
          "name": "default",
          "applyToProducts": ["default"]
        }
      ]
    },
    {
      "name": "mine",
      "srcPath": "./features/mine",
      "targets": [
        {
          "name": "default",
          "applyToProducts": ["default"]
        }
      ]
    },
    // --- Products layer ---
    {
      "name": "phone",
      "srcPath": "./products/phone",
      "targets": [
        {
          "name": "default",
          "applyToProducts": ["default"]
        }
      ]
    }
  ]
}
```

### hvigorfile.ts (root)

```typescript
import { appTasks } from '@ohos/hvigor-ohos-plugin';

export default {
  system: appTasks
}
```

---

## commons/common/ -- Shared Utilities HAR Module

### commons/common/src/main/module.json5

```json5
{
  "module": {
    // Module name must match build-profile.json5 and oh-package.json5.
    "name": "common",

    // "har" = HarmonyOS Archive (library module).
    // HAR modules cannot run independently; they are compiled into consuming modules.
    "type": "har",

    // Device types this library supports.
    "deviceTypes": [
      "phone",
      "tablet",
      "2in1"
    ],

    // Description of the module.
    "description": "$string:module_desc"

    // NOTE: HAR modules do NOT have:
    //   - "abilities" (no UI entry point)
    //   - "pages" (no page registration)
    //   - "mainElement"
    //   - "deliveryWithInstall"
  }
}
```

### commons/common/oh-package.json5

```json5
{
  // Package name. When other modules depend on this, they use this name.
  // Convention: use @<scope>/<name> for organizational packages.
  "name": "@ohos/common",

  "version": "1.0.0",
  "description": "Common utilities, constants, and data models.",

  // Main entry file: the barrel export index.
  // When another module imports "@ohos/common", it resolves to this file.
  "main": "Index.ets",

  "author": "",
  "license": "Apache-2.0",

  // This module has no dependencies on other project modules.
  "dependencies": {},
  "devDependencies": {}
}
```

### commons/common/hvigorfile.ts

```typescript
// HAR modules use harTasks (not hapTasks).
import { harTasks } from '@ohos/hvigor-ohos-plugin';

export default {
  system: harTasks
}
```

### commons/common/src/main/ets/Index.ets

The **barrel export** file. Every public API of this module must be re-exported here. Consumers import from the module name, which resolves to this file.

```typescript
// Re-export everything that should be publicly accessible.
// Consumers write: import { AppConstants, Logger } from '@ohos/common'

// Export constants
export { AppConstants } from './constants/AppConstants';

// Export utilities
export { Logger } from './utils/Logger';
```

### commons/common/src/main/ets/constants/AppConstants.ets

```typescript
/**
 * Application-wide constants.
 * Centralizing magic strings/numbers prevents duplication and eases maintenance.
 */
export class AppConstants {
  // Tab bar configuration.
  static readonly TAB_HOME: string = 'home';
  static readonly TAB_MINE: string = 'mine';

  // Network configuration.
  static readonly BASE_URL: string = 'https://api.example.com';
  static readonly REQUEST_TIMEOUT: number = 15000;  // milliseconds

  // Layout constants (in vp).
  static readonly FULL_WIDTH: string = '100%';
  static readonly FULL_HEIGHT: string = '100%';
  static readonly COMMON_PADDING: number = 16;
  static readonly BORDER_RADIUS: number = 12;

  // Prevent instantiation.
  private constructor() {}
}
```

### commons/common/src/main/ets/utils/Logger.ets

```typescript
import { hilog } from '@kit.PerformanceAnalysisKit';

/**
 * Centralized logger wrapping hilog.
 * Provides a consistent logging interface across all modules.
 */
export class Logger {
  // Log domain identifier. Use different values per module for filtering.
  private static readonly DOMAIN: number = 0xFF00;

  // Log tag prefix.
  private tag: string;

  constructor(tag: string) {
    this.tag = tag;
  }

  debug(message: string, ...args: string[]): void {
    hilog.debug(Logger.DOMAIN, this.tag, message, args);
  }

  info(message: string, ...args: string[]): void {
    hilog.info(Logger.DOMAIN, this.tag, message, args);
  }

  warn(message: string, ...args: string[]): void {
    hilog.warn(Logger.DOMAIN, this.tag, message, args);
  }

  error(message: string, ...args: string[]): void {
    hilog.error(Logger.DOMAIN, this.tag, message, args);
  }
}
```

---

## commons/uicomponents/ -- Shared UI Components HAR Module

### commons/uicomponents/src/main/module.json5

```json5
{
  "module": {
    "name": "uicomponents",
    "type": "har",
    "deviceTypes": [
      "phone",
      "tablet",
      "2in1"
    ],
    "description": "$string:module_desc"
  }
}
```

### commons/uicomponents/oh-package.json5

```json5
{
  "name": "@ohos/uicomponents",
  "version": "1.0.0",
  "description": "Shared UI components used across feature modules.",
  "main": "Index.ets",
  "author": "",
  "license": "Apache-2.0",

  "dependencies": {
    // UI components may need common utilities/constants.
    // "file:" prefix references a local module by relative path.
    // At build time, Hvigor resolves this to the local HAR.
    "@ohos/common": "file:../../commons/common"
  },
  "devDependencies": {}
}
```

### commons/uicomponents/hvigorfile.ts

```typescript
import { harTasks } from '@ohos/hvigor-ohos-plugin';

export default {
  system: harTasks
}
```

### commons/uicomponents/src/main/ets/Index.ets

```typescript
// Barrel export for shared UI components.
// Consumers write: import { CommonHeader } from '@ohos/uicomponents'

export { CommonHeader } from './components/CommonHeader';
```

### commons/uicomponents/src/main/ets/components/CommonHeader.ets

```typescript
import { AppConstants } from '@ohos/common';

/**
 * A reusable page header component.
 * @ComponentV2 makes this a V2 declarative ArkUI building block.
 * @Preview enables preview in DevEco Studio.
 * (V1 legacy used @Component + @Prop — only retain in API < 12 projects.)
 */
@ComponentV2
export struct CommonHeader {
  // @Param + @Once: one-way read-only data binding from parent to child (V2 replacement for V1 @Prop).
  // Parent passes a value; child cannot mutate it; parent updates flow in automatically.
  @Param @Once title: string = '';

  // Show the back button only when the parent opts in. V2 @Event always has a default,
  // so we use an explicit boolean flag instead of nullable callback existence checks.
  @Param @Once showBack: boolean = false;

  // V2 @Event: parent→child callback for the back button tap. Always defined (no nullable),
  // defaulting to a no-op so children can fire it unconditionally.
  @Event onBackClick: () => void = () => {};

  build() {
    Row() {
      // Back button only rendered when the parent opts in via showBack.
      if (this.showBack) {
        Image($r('sys.media.ohos_ic_back'))
          .width(24)
          .height(24)
          .margin({ right: 16 })
          .onClick(() => {
            this.onBackClick();
          })
      }

      // Title text.
      Text(this.title)
        .fontSize(20)
        .fontWeight(FontWeight.Bold)
        .layoutWeight(1)   // Takes remaining horizontal space.

    }
    .width(AppConstants.FULL_WIDTH)
    .height(56)
    .padding({ left: AppConstants.COMMON_PADDING, right: AppConstants.COMMON_PADDING })
    .alignItems(VerticalAlign.Center)
  }
}
```

---

## features/home/ -- Home Feature HAR Module

### features/home/src/main/module.json5

```json5
{
  "module": {
    "name": "home",
    "type": "har",
    "deviceTypes": [
      "phone",
      "tablet",
      "2in1"
    ],
    "description": "$string:module_desc"
  }
}
```

### features/home/oh-package.json5

```json5
{
  "name": "@ohos/home",
  "version": "1.0.0",
  "description": "Home tab feature module.",
  "main": "Index.ets",
  "author": "",
  "license": "Apache-2.0",

  "dependencies": {
    // Feature modules depend on commons but NEVER on other features or products.
    "@ohos/common": "file:../../commons/common",
    "@ohos/uicomponents": "file:../../commons/uicomponents"
  },
  "devDependencies": {}
}
```

### features/home/hvigorfile.ts

```typescript
import { harTasks } from '@ohos/hvigor-ohos-plugin';

export default {
  system: harTasks
}
```

### features/home/src/main/ets/Index.ets

```typescript
// Barrel export for the home feature.
// The entry module imports this to embed the home page.
// Consumers write: import { HomePage } from '@ohos/home'

export { HomePage } from './pages/HomePage';
```

### features/home/src/main/ets/pages/HomePage.ets

```typescript
import { AppConstants, Logger } from '@ohos/common';
import { CommonHeader } from '@ohos/uicomponents';

const logger = new Logger('HomePage');

/**
 * Home page component.
 * Exported as a @ComponentV2 (not @Entry) so the products/phone entry can embed it.
 * Only the entry module's pages use @Entry.
 * (V1 legacy used @Component + @State — only retain in API < 12 projects.)
 */
@ComponentV2
export struct HomePage {
  @Local currentIndex: number = 0;

  // aboutToAppear lifecycle: called before the component's build() runs for the first time.
  aboutToAppear(): void {
    logger.info('HomePage aboutToAppear');
  }

  // aboutToDisappear lifecycle: called before the component is destroyed.
  aboutToDisappear(): void {
    logger.info('HomePage aboutToDisappear');
  }

  build() {
    Column() {
      // Use the shared header component from uicomponents module.
      CommonHeader({ title: 'Home' })

      // Main content area.
      Column({ space: 16 }) {
        Text('Welcome to the Home page')
          .fontSize(18)
          .fontColor('#182431')

        // Example: a simple list of cards.
        List({ space: 12 }) {
          ForEach(
            ['Item 1', 'Item 2', 'Item 3', 'Item 4'],
            (item: string) => {
              ListItem() {
                Row() {
                  Text(item)
                    .fontSize(16)
                    .layoutWeight(1)
                  Image($r('sys.media.ohos_ic_public_arrow_right'))
                    .width(20)
                    .height(20)
                }
                .width(AppConstants.FULL_WIDTH)
                .padding(AppConstants.COMMON_PADDING)
                .backgroundColor(Color.White)
                .borderRadius(AppConstants.BORDER_RADIUS)
              }
            }
          )
        }
        .width(AppConstants.FULL_WIDTH)
        .layoutWeight(1)
      }
      .width(AppConstants.FULL_WIDTH)
      .layoutWeight(1)
      .padding(AppConstants.COMMON_PADDING)
    }
    .width(AppConstants.FULL_WIDTH)
    .height(AppConstants.FULL_HEIGHT)
    .backgroundColor('#F1F3F5')
  }
}
```

---

## features/mine/ -- Profile/Mine Feature HAR Module

### features/mine/src/main/module.json5

```json5
{
  "module": {
    "name": "mine",
    "type": "har",
    "deviceTypes": [
      "phone",
      "tablet",
      "2in1"
    ],
    "description": "$string:module_desc"
  }
}
```

### features/mine/oh-package.json5

```json5
{
  "name": "@ohos/mine",
  "version": "1.0.0",
  "description": "User profile (Mine) tab feature module.",
  "main": "Index.ets",
  "author": "",
  "license": "Apache-2.0",

  "dependencies": {
    "@ohos/common": "file:../../commons/common",
    "@ohos/uicomponents": "file:../../commons/uicomponents"
  },
  "devDependencies": {}
}
```

### features/mine/hvigorfile.ts

```typescript
import { harTasks } from '@ohos/hvigor-ohos-plugin';

export default {
  system: harTasks
}
```

### features/mine/src/main/ets/Index.ets

```typescript
// Barrel export for the mine feature.
// Consumers write: import { MinePage } from '@ohos/mine'

export { MinePage } from './pages/MinePage';
```

### features/mine/src/main/ets/pages/MinePage.ets

```typescript
import { AppConstants, Logger } from '@ohos/common';
import { CommonHeader } from '@ohos/uicomponents';

const logger = new Logger('MinePage');

/**
 * User profile page component.
 * Demonstrates AppStorageV2.connect for app-level shared state via an @ObservedV2 model.
 * (V1 legacy used @StorageLink('userName') / @StorageProp(...) directly on string keys —
 *  V2 always groups related fields into an @ObservedV2 class shared via AppStorageV2.connect.)
 */
@ObservedV2
class UserProfileModel {
  @Trace userName: string = 'Guest User';
  @Trace avatarUrl: string = '';
}

@ComponentV2
export struct MinePage {
  // @Local + AppStorageV2.connect: shared, reactive app-wide state.
  // First connect to 'userProfile' creates the singleton; later connects share the same instance.
  @Local profile: UserProfileModel = AppStorageV2.connect(
    UserProfileModel,
    'userProfile',
    () => new UserProfileModel()
  )!;

  aboutToAppear(): void {
    logger.info('MinePage aboutToAppear');
  }

  build() {
    Column() {
      CommonHeader({ title: 'Profile' })

      Column({ space: 24 }) {
        // User avatar and name. @Trace fields trigger UI re-render when reassigned anywhere.
        Column({ space: 12 }) {
          Image(this.profile.avatarUrl || $r('sys.media.ohos_user_auth_icon_face'))
            .width(80)
            .height(80)
            .borderRadius(40)             // Circular avatar.
            .backgroundColor('#E5E5E5')

          Text(this.profile.userName)
            .fontSize(20)
            .fontWeight(FontWeight.Medium)
        }
        .alignItems(HorizontalAlign.Center)
        .width(AppConstants.FULL_WIDTH)
        .padding({ top: 24, bottom: 24 })

        // Settings menu items.
        Column({ space: 1 }) {
          this.MenuItem('Settings', () => {
            logger.info('Navigate to Settings');
          })
          this.MenuItem('About', () => {
            logger.info('Navigate to About');
          })
          this.MenuItem('Privacy Policy', () => {
            logger.info('Navigate to Privacy Policy');
          })
        }
        .backgroundColor(Color.White)
        .borderRadius(AppConstants.BORDER_RADIUS)
      }
      .width(AppConstants.FULL_WIDTH)
      .layoutWeight(1)
      .padding(AppConstants.COMMON_PADDING)
    }
    .width(AppConstants.FULL_WIDTH)
    .height(AppConstants.FULL_HEIGHT)
    .backgroundColor('#F1F3F5')
  }

  // @Builder: a lightweight builder function for reusable UI fragments.
  // Unlike @ComponentV2 structs, builders share the owning component's state scope (no @Local).
  @Builder
  MenuItem(title: string, onClick: () => void) {
    Row() {
      Text(title)
        .fontSize(16)
        .layoutWeight(1)
      Image($r('sys.media.ohos_ic_public_arrow_right'))
        .width(20)
        .height(20)
    }
    .width(AppConstants.FULL_WIDTH)
    .height(52)
    .padding({ left: 16, right: 16 })
    .alignItems(VerticalAlign.Center)
    .onClick(onClick)
  }
}
```

---

## products/phone/ -- Entry Module for Phone

### products/phone/src/main/module.json5

```json5
{
  "module": {
    // Name must match build-profile.json5 entry.
    "name": "phone",

    // Entry type: this is the installable/runnable module.
    "type": "entry",

    "description": "$string:module_desc",
    "mainElement": "EntryAbility",

    "deviceTypes": [
      "phone",
      "tablet",
      "2in1"
    ],

    "deliveryWithInstall": true,
    "installationFree": false,

    // Points to the pages registration file.
    "pages": "$profile:main_pages",

    "abilities": [
      {
        "name": "EntryAbility",
        "srcEntry": "./ets/entryability/EntryAbility.ets",
        "description": "$string:EntryAbility_desc",
        "icon": "$media:layered_image",
        "label": "$string:EntryAbility_label",
        "launchType": "singleton",
        "startWindowIcon": "$media:startIcon",
        "startWindowBackground": "$color:start_window_background",
        "exported": true,
        "skills": [
          {
            "entities": ["entity.system.home"],
            "actions": ["action.system.home"]
          }
        ]
      }
    ],

    "requestPermissions": [
      {
        "name": "ohos.permission.INTERNET",
        "reason": "$string:permission_internet_reason",
        "usedScene": {
          "abilities": ["EntryAbility"],
          "when": "always"
        }
      }
    ]
  }
}
```

### products/phone/oh-package.json5

```json5
{
  "name": "phone",
  "version": "1.0.0",
  "description": "Phone entry module. Assembles feature modules into the final app.",
  "main": "",
  "author": "",
  "license": "Apache-2.0",

  "dependencies": {
    // The entry module depends on feature modules.
    // Feature modules transitively bring in commons modules.
    "@ohos/home": "file:../../features/home",
    "@ohos/mine": "file:../../features/mine",

    // Direct commons dependency (for shared constants used in the shell).
    "@ohos/common": "file:../../commons/common"
  },

  "devDependencies": {
    "@ohos/hypium": "1.0.19"
  }
}
```

### products/phone/hvigorfile.ts

```typescript
// Entry modules use hapTasks.
import { hapTasks } from '@ohos/hvigor-ohos-plugin';

export default {
  system: hapTasks
}
```

### products/phone/src/main/resources/base/profile/main_pages.json

```json
{
  "src": [
    "pages/Index"
  ]
}
```

### products/phone/src/main/resources/base/element/string.json

```json
{
  "string": [
    {
      "name": "module_desc",
      "value": "Phone entry module"
    },
    {
      "name": "EntryAbility_desc",
      "value": "Main entry ability"
    },
    {
      "name": "EntryAbility_label",
      "value": "MultiModuleApp"
    },
    {
      "name": "permission_internet_reason",
      "value": "This app requires internet access to load content."
    }
  ]
}
```

### products/phone/src/main/resources/base/element/color.json

```json
{
  "color": [
    {
      "name": "start_window_background",
      "value": "#FFFFFF"
    }
  ]
}
```

### products/phone/src/main/ets/entryability/EntryAbility.ets

```typescript
import { UIAbility, Want, AbilityConstant } from '@kit.AbilityKit';
import { window } from '@kit.ArkUI';
import { Logger } from '@ohos/common';

const logger = new Logger('EntryAbility');

export default class EntryAbility extends UIAbility {
  onCreate(want: Want, launchParam: AbilityConstant.LaunchParam): void {
    logger.info('onCreate');
  }

  onDestroy(): void {
    logger.info('onDestroy');
  }

  onWindowStageCreate(windowStage: window.WindowStage): void {
    logger.info('onWindowStageCreate');
    windowStage.loadContent('pages/Index', (err) => {
      if (err.code) {
        logger.error('Failed to load content: %{public}s', JSON.stringify(err));
        return;
      }
      logger.info('Content loaded successfully.');
    });
  }

  onWindowStageDestroy(): void {
    logger.info('onWindowStageDestroy');
  }

  onForeground(): void {
    logger.info('onForeground');
  }

  onBackground(): void {
    logger.info('onBackground');
  }
}
```

### products/phone/src/main/ets/pages/Index.ets

This is the shell page that hosts the tab-based navigation, embedding feature module pages.

```typescript
// Import page components from feature modules.
// These resolve via oh-package.json5 "file:" dependencies -> barrel Index.ets exports.
import { HomePage } from '@ohos/home';
import { MinePage } from '@ohos/mine';
import { AppConstants } from '@ohos/common';

@Entry
@ComponentV2
struct Index {
  // Track the currently selected tab. @Local is the V2 replacement for V1 @State.
  @Local currentTabIndex: number = 0;

  // Tabs controller for programmatic tab switching.
  private tabsController: TabsController = new TabsController();

  build() {
    // Tabs container: the top-level layout for a tab-based app.
    Tabs({
      barPosition: BarPosition.End,      // Tab bar at the bottom.
      controller: this.tabsController,
      index: this.currentTabIndex        // Bound to state for reactivity.
    }) {

      // --- Home Tab ---
      TabContent() {
        // Embed the HomePage component from the home feature module.
        HomePage()
      }
      .tabBar(this.TabBarBuilder(
        'Home',
        0,
        $r('sys.media.ohos_ic_public_home'),
        $r('sys.media.ohos_ic_public_home_filled')
      ))

      // --- Mine Tab ---
      TabContent() {
        // Embed the MinePage component from the mine feature module.
        MinePage()
      }
      .tabBar(this.TabBarBuilder(
        'Mine',
        1,
        $r('sys.media.ohos_ic_public_contacts'),
        $r('sys.media.ohos_ic_public_contacts_filled')
      ))

    }
    .barMode(BarMode.Fixed)              // Fixed width tabs (equal spacing).
    .barWidth(AppConstants.FULL_WIDTH)
    .barHeight(56)
    .onChange((index: number) => {
      // Update state when user swipes or taps a tab.
      this.currentTabIndex = index;
    })
    .width(AppConstants.FULL_WIDTH)
    .height(AppConstants.FULL_HEIGHT)
  }

  // @Builder for the custom tab bar item.
  @Builder
  TabBarBuilder(title: string, index: number, normalIcon: Resource, selectedIcon: Resource) {
    Column({ space: 4 }) {
      Image(this.currentTabIndex === index ? selectedIcon : normalIcon)
        .width(24)
        .height(24)
      Text(title)
        .fontSize(10)
        .fontColor(this.currentTabIndex === index ? '#007DFF' : '#99000000')
    }
    .width('100%')
    .height('100%')
    .justifyContent(FlexAlign.Center)
    .alignItems(HorizontalAlign.Center)
  }
}
```

---

## Module Dependency Graph

```
products/phone
  ├── @ohos/home (features/home)
  │     ├── @ohos/common (commons/common)
  │     └── @ohos/uicomponents (commons/uicomponents)
  │           └── @ohos/common (commons/common)  [deduplicated]
  ├── @ohos/mine (features/mine)
  │     ├── @ohos/common (commons/common)        [deduplicated]
  │     └── @ohos/uicomponents (commons/uicomponents) [deduplicated]
  └── @ohos/common (commons/common)              [deduplicated]
```

## Key Rules for Multi-Module Projects

1. **Every module must appear in `build-profile.json5`** under the `modules` array with the correct `srcPath`.
2. **Inter-module dependencies use `"file:../relative/path"`** in `oh-package.json5`.
3. **HAR modules must have `"main": "Index.ets"`** pointing to a barrel export file.
4. **Only entry modules use `@Entry` on page components.** HAR page components use `@ComponentV2` only (V1 legacy: `@Component`).
5. **Dependency direction is strictly top-down:** products -> features -> commons. Never create circular dependencies.
6. **Each HAR module's `hvigorfile.ts` uses `harTasks`.** Each entry module's `hvigorfile.ts` uses `hapTasks`.
7. **Only entry modules have `abilities`, `pages`, and `requestPermissions`** in their `module.json5`.
8. **Resource files (`string.json`, `color.json`) only need to exist in modules that reference `$string:` or `$color:` tokens.** HAR modules that do not use resource tokens in their `module.json5` can omit resource files.
