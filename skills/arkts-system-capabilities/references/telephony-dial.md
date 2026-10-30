# 电话拨号（Telephony Kit）

> 拉起系统拨号界面（显示待拨号码）用 Telephony Kit 的 `call.makeCall`——**不是** `Want + startAbility`。这与浏览器/URL 跳转（`references/browser-intent.md`，走 `viewData`）是**不同机制**，勿混用。

---

## 基本导入

```typescript
import { call } from '@kit.TelephonyKit'
import { BusinessError } from '@kit.BasicServicesKit'
```

---

## 拉起系统拨号界面

> ✅ **验证状态**：已 probe 编译通过（`call.makeCall('10086')`，BUILD SUCCESSFUL）

```typescript
// makeCall(phoneNumber: string): Promise<void>
// 号码作为 string 实参直接传入；跳转到系统拨号界面并显示待拨号码。
// 只支持在 UIAbility 中调用；可能失败（如设备无电话能力），须接 .catch。
function dialNumber(phoneNumber: string): void {
  call.makeCall(phoneNumber)
    .then(() => {
      hilog.info(DOMAIN, TAG, `Dialer opened for ${phoneNumber}`)
    })
    .catch((err: BusinessError) => {
      hilog.error(DOMAIN, TAG, `makeCall failed: code=${err.code}, message=${err.message}`)
    })
}
```

---

## 关键约定

- **用 `call.makeCall(phoneNumber)`**，号码是纯字符串（如 `'1234567890'`），**不带 `tel:` 前缀**。
- **不要**把拨号走 `Want{action:'ohos.want.action.viewData', uri:'tel:<号码>'}` + `startAbility`——那条隐式路径非正解。
- **不要**用已废弃的 `call.dial(...)`（自 API 9 起废弃，替代能力仅对系统应用开放）；应用侧拉起拨号界面用 `makeCall`。
- `call` 从 `@kit.TelephonyKit` 导入，不要从 `@kit.AbilityKit` / Want 相关模块导入。
- syscap `SystemCapability.Applications.Contacts`（since API 7）；`makeCall` 只是拉起拨号界面（不直接拨出），本身无需额外权限。

---

## module.json5 配置

拉起系统拨号界面（`makeCall`）**无需**在 module.json5 声明 action/entity——直接调用即可（区别于隐式 Want 拉起需声明 skills 的场景）。
