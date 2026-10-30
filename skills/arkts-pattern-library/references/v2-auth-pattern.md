# 登录认证状态管理完整参考（V2）

> 本项目锁 ArkTS V2，本文档为 V2 主参考。V1 历史写法（`AppStorage + @StorageLink + AppStorage.setOrCreate` 模式）见 [`auth-pattern.md`](./auth-pattern.md)。

## V2 升级要点

V1 用 `@StorageLink('isLoggedIn')` + `AppStorage.setOrCreate(...)` 在多个组件间共享登录状态，散点式键管理；V2 改为：

1. **定义 `@ObservedV2` 类** `AuthState`，承载所有登录相关状态
2. **`AppStorageV2.connect(AuthState, 'auth', () => new AuthState())!`** 一次连接获得共享实例
3. **修改实例的 `@Trace` 属性自动同步到所有 connect 的组件**，无需手动 setOrCreate
4. **Token 持久化**：业务上仍用 `preferences` 写磁盘；如需"内存级 + 自动落盘"，可改用 `PersistenceV2.globalConnect`

## 完整实现：AuthState + 登录页 + 个人中心 + Token 管理（V2）

```typescript
import { AppStorageV2 } from '@kit.ArkUI'  // AppStorageV2/PersistenceV2 是 @kit.ArkUI 的真实导出，必须 import（装饰器/IMonitor 才是 ambient）
import { preferences } from '@kit.ArkData'
import { common } from '@kit.AbilityKit'

// ===================== Token / 用户信息模型 =====================
interface UserInfo {
  userId: string
  userName: string
  avatar: string
  phone: string
}

// ===================== V2 全局登录状态类 =====================
@ObservedV2
class AuthState {
  @Trace isLoggedIn: boolean = false
  @Trace userId: string = ''
  @Trace userName: string = ''
  @Trace avatar: string = ''
  @Trace phone: string = ''

  fillFrom(user: UserInfo): void {
    this.isLoggedIn = true
    this.userId = user.userId
    this.userName = user.userName
    this.avatar = user.avatar
    this.phone = user.phone
  }

  clear(): void {
    this.isLoggedIn = false
    this.userId = ''
    this.userName = ''
    this.avatar = ''
    this.phone = ''
  }

  toUserInfo(): UserInfo {
    return {
      userId: this.userId,
      userName: this.userName,
      avatar: this.avatar,
      phone: this.phone
    }
  }
}

// ===================== 认证服务（Token 管理） =====================
class AuthService {
  private static readonly PREFS_NAME = 'auth_prefs'
  private static readonly TOKEN_KEY = 'access_token'
  private static readonly USER_KEY = 'user_info'

  static async saveToken(context: common.Context, token: string): Promise<void> {
    let prefs = await preferences.getPreferences(context, AuthService.PREFS_NAME)
    await prefs.put(AuthService.TOKEN_KEY, token)
    await prefs.flush()
  }

  static async getToken(context: common.Context): Promise<string> {
    let prefs = await preferences.getPreferences(context, AuthService.PREFS_NAME)
    let token = await prefs.get(AuthService.TOKEN_KEY, '')
    return token as string
  }

  static async saveUserInfo(context: common.Context, user: UserInfo): Promise<void> {
    let prefs = await preferences.getPreferences(context, AuthService.PREFS_NAME)
    await prefs.put(AuthService.USER_KEY, JSON.stringify(user))
    await prefs.flush()
  }

  static async getUserInfo(context: common.Context): Promise<UserInfo | null> {
    let prefs = await preferences.getPreferences(context, AuthService.PREFS_NAME)
    let data = await prefs.get(AuthService.USER_KEY, '')
    if ((data as string).length > 0) {
      return JSON.parse(data as string) as UserInfo
    }
    return null
  }

  static async clearAuth(context: common.Context): Promise<void> {
    let prefs = await preferences.getPreferences(context, AuthService.PREFS_NAME)
    await prefs.delete(AuthService.TOKEN_KEY)
    await prefs.delete(AuthService.USER_KEY)
    await prefs.flush()
  }
}

// ===================== Storage Key 常量 =====================
export class StorageKeys {
  static readonly AUTH = 'auth'
}

// ===================== 入口页面（自动登录检查） =====================
@Entry
@ComponentV2
struct AuthEntry {
  // V2: 通过 connect 获得共享 AuthState 实例
  @Local auth: AuthState = AppStorageV2.connect(AuthState, StorageKeys.AUTH, () => new AuthState())!

  aboutToAppear(): void {
    this.checkAutoLogin()
  }

  private async checkAutoLogin(): Promise<void> {
    try {
      let context = getContext(this) as common.Context
      let token = await AuthService.getToken(context)
      if (token.length > 0) {
        let userInfo = await AuthService.getUserInfo(context)
        if (userInfo) {
          this.auth.fillFrom(userInfo)  // 直接修改 @Trace 属性，自动同步到所有组件
        }
      }
    } catch (e) {
      // 自动登录失败，保持未登录状态
    }
  }

  build() {
    Column() {
      if (this.auth.isLoggedIn) {
        ProfilePage()
      } else {
        LoginPage()
      }
    }
    .width('100%')
    .height('100%')
  }
}

// ===================== 登录页（V2） =====================
@ComponentV2
struct LoginPage {
  @Local phone: string = ''
  @Local password: string = ''
  @Local isLoading: boolean = false
  @Local errorMessage: string = ''
  @Local passwordVisible: boolean = false
  // 共享 AuthState 实例
  @Local auth: AuthState = AppStorageV2.connect(AuthState, StorageKeys.AUTH, () => new AuthState())!

  private validateForm(): boolean {
    if (this.phone.trim().length === 0) {
      this.errorMessage = '请输入手机号'
      return false
    }
    this.errorMessage = ''
    return true
  }

  private async login(): Promise<void> {
    if (!this.validateForm()) {
      return
    }
    this.isLoading = true
    this.errorMessage = ''

    try {
      // 模拟登录 API 请求（替换为真实接口）
      await new Promise<void>((resolve) => {
        setTimeout(() => resolve(), 1500)
      })

      let token = 'mock_token_' + Date.now()
      let userInfo: UserInfo = {
        userId: 'user_001',
        userName: '张三',
        avatar: '',
        phone: this.phone
      }

      // 持久化存储
      let context = getContext(this) as common.Context
      await AuthService.saveToken(context, token)
      await AuthService.saveUserInfo(context, userInfo)

      // V2: 修改 @ObservedV2 实例属性，自动同步到所有 connect('auth') 的组件
      this.auth.fillFrom(userInfo)
    } catch (e) {
      this.errorMessage = '登录失败，请检查网络'
    } finally {
      this.isLoading = false
    }
  }

  build() {
    Column({ space: 20 }) {
      Column({ space: 8 }) {
        Text('欢迎登录')
          .fontSize(28)
          .fontWeight(FontWeight.Bold)
        Text('请输入手机号和密码')
          .fontSize(14)
          .fontColor('#999999')
      }
      .margin({ top: 80, bottom: 40 })

      TextInput({ placeholder: '手机号', text: this.phone })
        .type(InputType.PhoneNumber)
        .width('85%')
        .height(48)
        .onChange((value: string) => {
          this.phone = value
          this.errorMessage = ''
        })

      TextInput({ placeholder: '密码', text: this.password })
        .type(this.passwordVisible ? InputType.Normal : InputType.Password)
        .width('85%')
        .height(48)
        .onChange((value: string) => {
          this.password = value
          this.errorMessage = ''
        })

      if (this.errorMessage.length > 0) {
        Text(this.errorMessage)
          .fontSize(13)
          .fontColor(Color.Red)
          .width('85%')
      }

      Button(this.isLoading ? '登录中...' : '登录')
        .width('85%')
        .height(48)
        .fontSize(16)
        .enabled(!this.isLoading)
        .backgroundColor('#667EEA')
        .onClick(() => {
          this.login()
        })

      Row({ space: 20 }) {
        Text('忘记密码')
          .fontSize(13)
          .fontColor('#667EEA')
        Text('注册账号')
          .fontSize(13)
          .fontColor('#667EEA')
      }
      .margin({ top: 10 })
    }
    .width('100%')
    .height('100%')
    .backgroundColor(Color.White)
  }
}

// ===================== 个人中心页（V2，已登录） =====================
@ComponentV2
struct ProfilePage {
  @Local auth: AuthState = AppStorageV2.connect(AuthState, StorageKeys.AUTH, () => new AuthState())!
  @Local showLogoutDialog: boolean = false

  private async logout(): Promise<void> {
    try {
      let context = getContext(this) as common.Context
      await AuthService.clearAuth(context)
    } catch (e) {
      // 清除失败不影响退出
    }
    this.auth.clear()  // 自动同步到所有组件
  }

  build() {
    Column() {
      Column({ space: 12 }) {
        Column() {
          Text(this.auth.userName.length > 0 ? this.auth.userName.charAt(0) : '?')
            .fontSize(32)
            .fontColor(Color.White)
            .fontWeight(FontWeight.Bold)
        }
        .width(80)
        .height(80)
        .borderRadius(40)
        .backgroundColor('#667EEA')
        .justifyContent(FlexAlign.Center)

        Text(this.auth.userName.length > 0 ? this.auth.userName : '未知用户')
          .fontSize(22)
          .fontWeight(FontWeight.Bold)
        Text(this.auth.phone)
          .fontSize(14)
          .fontColor('#999999')
      }
      .width('100%')
      .padding({ top: 60, bottom: 30 })
      .backgroundColor(Color.White)

      Column() {
        this.MenuItem('个人资料', '查看和编辑')
        this.MenuItem('账号安全', '修改密码')
        this.MenuItem('消息通知', '推送设置')
        this.MenuItem('关于我们', 'v1.0.0')
      }
      .width('100%')
      .margin({ top: 12 })
      .backgroundColor(Color.White)

      Blank()

      Button('退出登录')
        .width('85%')
        .height(44)
        .fontSize(16)
        .fontColor(Color.Red)
        .backgroundColor('#FFF0F0')
        .margin({ bottom: 40 })
        .onClick(() => {
          // 现行实例形确认框：全局 AlertDialog.show 自 API18 已 deprecated，用 UIContext 实例形
          this.getUIContext().showAlertDialog({
            title: '提示',
            message: '确定要退出登录吗？',
            primaryButton: {
              value: '取消',
              action: () => {}
            },
            secondaryButton: {
              value: '退出',
              fontColor: Color.Red,
              action: () => {
                this.logout()
              }
            }
          })
        })
    }
    .width('100%')
    .height('100%')
    .backgroundColor('#F5F5F5')
  }

  @Builder
  MenuItem(title: string, subtitle: string) {
    Row() {
      Column({ space: 2 }) {
        Text(title)
          .fontSize(16)
        Text(subtitle)
          .fontSize(12)
          .fontColor('#999999')
      }
      .alignItems(HorizontalAlign.Start)
      Blank()
      Text('>')
        .fontSize(16)
        .fontColor('#CCCCCC')
    }
    .width('100%')
    .height(64)
    .padding({ left: 20, right: 20 })
    .border({ width: { bottom: 0.5 }, color: '#F0F0F0' })
  }
}
```

---

## 进阶：用 PersistenceV2 替代 preferences 手动持久化

如果不需要在登录前后做"明文 token"加密之类的特殊处理，V2 推荐用 `PersistenceV2` 把 `AuthState` 直接落盘：

```typescript
@ObservedV2
class AuthState {
  @Trace isLoggedIn: boolean = false
  @Trace userId: string = ''
  @Trace userName: string = ''
  @Trace token: string = ''
}

@ComponentV2
struct AuthEntry {
  // 一站式：磁盘持久化 + UI 响应式（无需 preferences + AppStorageV2 双层）
  @Local auth: AuthState = PersistenceV2.globalConnect({
    type: AuthState,
    key: 'auth',
    defaultCreator: () => new AuthState()
  })!

  build() {
    if (this.auth.isLoggedIn) {
      ProfilePage()
    } else {
      LoginPage()
    }
  }
}
```

何时用哪种：

| 场景 | 选择 |
|---|---|
| Token 需要加密 / 写入安全存储 | 仍用 `preferences`/系统 KMS + `AppStorageV2` 同步内存 |
| Token 明文存即可（极简场景） | `PersistenceV2.globalConnect` 一站式 |
| 只需运行时共享、不持久化 | `AppStorageV2.connect` |

---

## V2 关键变更对照（vs V1）

| 位置 | V1 | V2 |
|---|---|---|
| 入口 struct | `@Entry @Component` | `@Entry @ComponentV2` |
| 全局登录状态 | `@StorageLink('isLoggedIn') isLoggedIn` 散点 | `@Local auth: AuthState = AppStorageV2.connect(...)` |
| 用户信息 | `@StorageLink('currentUser') currentUserStr: string`（JSON 字符串） | `@Trace` 属性直接持有，无需序列化 |
| 写入全局状态 | `AppStorage.setOrCreate('isLoggedIn', true)` | `this.auth.isLoggedIn = true`（自动同步） |
| 局部状态 | `@State phone: string = ''` | `@Local phone: string = ''` |
| 持久化 token | `preferences.put + flush` | 同左；或用 `PersistenceV2.globalConnect` 一站式 |
