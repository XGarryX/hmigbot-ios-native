# 登录认证状态管理完整参考（**V1 历史文档 — Legacy**）

> ⚠️ **本项目锁 ArkTS V2**。本文档为 **V1 历史参考**（`@Component / @State / @StorageLink + AppStorage.setOrCreate` 等），仅用于阅读老代码或迁移老项目时查阅。
>
> **新代码请使用 V2 装饰器**：参阅 [`v2-auth-pattern.md`](./v2-auth-pattern.md)（V2 主参考）和 [`../SKILL.md`](../SKILL.md)。

---

## 完整实现：AppStorage 登录状态 + 登录页 + 个人中心 + Token 管理

```typescript
import { preferences } from '@kit.ArkData'

// ===================== Token / 用户信息模型 =====================
interface UserInfo {
  userId: string
  userName: string
  avatar: string
  phone: string
}

// ===================== 认证服务（Token 管理） =====================
class AuthService {
  private static readonly PREFS_NAME = 'auth_prefs'
  private static readonly TOKEN_KEY = 'access_token'
  private static readonly USER_KEY = 'user_info'

  // 保存 Token
  static async saveToken(context: Context, token: string): Promise<void> {
    let prefs = await preferences.getPreferences(context, AuthService.PREFS_NAME)
    await prefs.put(AuthService.TOKEN_KEY, token)
    await prefs.flush()
  }

  // 获取 Token
  static async getToken(context: Context): Promise<string> {
    let prefs = await preferences.getPreferences(context, AuthService.PREFS_NAME)
    let token = await prefs.get(AuthService.TOKEN_KEY, '')
    return token as string
  }

  // 保存用户信息
  static async saveUserInfo(context: Context, user: UserInfo): Promise<void> {
    let prefs = await preferences.getPreferences(context, AuthService.PREFS_NAME)
    await prefs.put(AuthService.USER_KEY, JSON.stringify(user))
    await prefs.flush()
  }

  // 获取用户信息
  static async getUserInfo(context: Context): Promise<UserInfo | null> {
    let prefs = await preferences.getPreferences(context, AuthService.PREFS_NAME)
    let data = await prefs.get(AuthService.USER_KEY, '')
    if ((data as string).length > 0) {
      return JSON.parse(data as string) as UserInfo
    }
    return null
  }

  // 清除登录信息（退出登录）
  static async clearAuth(context: Context): Promise<void> {
    let prefs = await preferences.getPreferences(context, AuthService.PREFS_NAME)
    await prefs.delete(AuthService.TOKEN_KEY)
    await prefs.delete(AuthService.USER_KEY)
    await prefs.flush()
  }
}

// ===================== 入口页面（自动登录检查） =====================
@Entry
@Component
struct AuthEntry {
  // AppStorage 全局登录状态，所有页面可观察
  @StorageLink('isLoggedIn') isLoggedIn: boolean = false
  @StorageLink('currentUser') currentUser: string = ''

  aboutToAppear(): void {
    this.checkAutoLogin()
  }

  // 自动登录：检查本地是否有有效 Token
  private async checkAutoLogin(): Promise<void> {
    try {
      let context = getContext(this)
      let token = await AuthService.getToken(context)
      if (token.length > 0) {
        // Token 存在，尝试用 token 获取用户信息
        let userInfo = await AuthService.getUserInfo(context)
        if (userInfo) {
          AppStorage.setOrCreate('isLoggedIn', true)
          AppStorage.setOrCreate('currentUser', JSON.stringify(userInfo))
        }
      }
    } catch (e) {
      // 自动登录失败，保持未登录状态
    }
  }

  build() {
    Column() {
      if (this.isLoggedIn) {
        ProfilePage()
      } else {
        LoginPage()
      }
    }
    .width('100%')
    .height('100%')
  }
}

// ===================== 登录页 =====================
@Component
struct LoginPage {
  @State phone: string = ''
  @State password: string = ''
  @State isLoading: boolean = false
  @State errorMessage: string = ''
  @State passwordVisible: boolean = false

  // 表单验证
  private validateForm(): boolean {
    if (this.phone.trim().length === 0) {
      this.errorMessage = '请输入手机号'
      return false
    }
    if (this.phone.length !== 11) {
      this.errorMessage = '请输入正确的手机号'
      return false
    }
    if (this.password.length < 6) {
      this.errorMessage = '密码至少6位'
      return false
    }
    this.errorMessage = ''
    return true
  }

  // 登录请求
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

      // 模拟登录成功，获取 token 和用户信息
      let token = 'mock_token_' + Date.now()
      let userInfo: UserInfo = {
        userId: 'user_001',
        userName: '张三',
        avatar: '',
        phone: this.phone
      }

      // 持久化存储
      let context = getContext(this)
      await AuthService.saveToken(context, token)
      await AuthService.saveUserInfo(context, userInfo)

      // 更新全局状态
      AppStorage.setOrCreate('isLoggedIn', true)
      AppStorage.setOrCreate('currentUser', JSON.stringify(userInfo))
    } catch (e) {
      this.errorMessage = '登录失败，请检查网络'
    } finally {
      this.isLoading = false
    }
  }

  build() {
    Column({ space: 20 }) {
      // Logo 和标题
      Column({ space: 8 }) {
        Text('欢迎登录')
          .fontSize(28)
          .fontWeight(FontWeight.Bold)
        Text('请输入手机号和密码')
          .fontSize(14)
          .fontColor('#999999')
      }
      .margin({ top: 80, bottom: 40 })

      // 手机号输入
      TextInput({ placeholder: '手机号', text: this.phone })
        .type(InputType.PhoneNumber)
        .width('85%')
        .height(48)
        .onChange((value: string) => {
          this.phone = value
          this.errorMessage = ''
        })

      // 密码输入
      TextInput({ placeholder: '密码', text: this.password })
        .type(this.passwordVisible ? InputType.Normal : InputType.Password)
        .width('85%')
        .height(48)
        .onChange((value: string) => {
          this.password = value
          this.errorMessage = ''
        })

      // 错误信息
      if (this.errorMessage.length > 0) {
        Text(this.errorMessage)
          .fontSize(13)
          .fontColor(Color.Red)
          .width('85%')
      }

      // 登录按钮
      Button(this.isLoading ? '登录中...' : '登录')
        .width('85%')
        .height(48)
        .fontSize(16)
        .enabled(!this.isLoading)
        .backgroundColor('#667EEA')
        .onClick(() => {
          this.login()
        })

      // 其他选项
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

// ===================== 个人中心页（已登录） =====================
@Component
struct ProfilePage {
  @StorageLink('isLoggedIn') isLoggedIn: boolean = false
  @StorageLink('currentUser') currentUserStr: string = ''
  @State userInfo: UserInfo | null = null
  @State showLogoutDialog: boolean = false

  aboutToAppear(): void {
    if (this.currentUserStr.length > 0) {
      this.userInfo = JSON.parse(this.currentUserStr) as UserInfo
    }
  }

  // 退出登录
  private async logout(): Promise<void> {
    try {
      let context = getContext(this)
      await AuthService.clearAuth(context)
    } catch (e) {
      // 清除失败不影响退出
    }
    AppStorage.setOrCreate('isLoggedIn', false)
    AppStorage.setOrCreate('currentUser', '')
  }

  build() {
    Column() {
      // 用户信息卡片
      Column({ space: 12 }) {
        // 头像
        Column() {
          Text(this.userInfo?.userName?.charAt(0) ?? '?')
            .fontSize(32)
            .fontColor(Color.White)
            .fontWeight(FontWeight.Bold)
        }
        .width(80)
        .height(80)
        .borderRadius(40)
        .backgroundColor('#667EEA')
        .justifyContent(FlexAlign.Center)

        Text(this.userInfo?.userName ?? '未知用户')
          .fontSize(22)
          .fontWeight(FontWeight.Bold)
        Text(this.userInfo?.phone ?? '')
          .fontSize(14)
          .fontColor('#999999')
      }
      .width('100%')
      .padding({ top: 60, bottom: 30 })
      .backgroundColor(Color.White)

      // 功能菜单
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

      // 退出登录按钮
      Button('退出登录')
        .width('85%')
        .height(44)
        .fontSize(16)
        .fontColor(Color.Red)
        .backgroundColor('#FFF0F0')
        .margin({ bottom: 40 })
        .onClick(() => {
          // 弹窗确认
          AlertDialog.show({
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
