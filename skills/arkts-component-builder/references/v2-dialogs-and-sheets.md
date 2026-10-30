# ArkTS V2 弹窗 / Sheet / 模态完整模板

> 覆盖 SKILL.md description 声明的「弹窗」能力。**经 harmony-docs（快照 2026-05-24）核验**。
> ⚠️ 已废弃：全局 `AlertDialog.show()`、全局 `promptAction.*`（@ohos.promptAction）。**V2 一律用 UIContext 形式** `this.getUIContext().getPromptAction()` 或 builder 形式（bindSheet/bindContentCover/openCustomDialog）。

## 选型速查

| 需求 | 用 |
|---|---|
| 轻提示（Toast） | `getUIContext().getPromptAction().showToast(...)` |
| 系统确认框（标题+按钮） | `getPromptAction().showDialog(...)` |
| 操作菜单（动作列表） | `getPromptAction().showActionMenu(...)` |
| 自定义内容弹窗（V2 推荐 builder） | `getPromptAction().openCustomDialog({ builder })` 或 `@CustomDialog` + `CustomDialogController` |
| 底部半模态面板（筛选/分享/评论） | `.bindSheet(...)` |
| 全屏模态（详情/编辑流） | `.bindContentCover(...)` |

> **层级维度（易漏）**：`@CustomDialog` / `openCustomDialog` / `showDialog` 默认是**全局级**，层级高于所有路由页——打开弹窗后再路由跳转，弹窗不会自动关闭且盖在新页之上。若迁移的 iOS 弹窗是「打开后仍要跳新页、返回后弹窗还在」的页面级语义（按实际 SwiftUI/UIKit 宿主和展示作用域核实），见 §2c 页面级弹窗，别直接套 §2a/§2b。

---

## 1. promptAction（UIContext 形式）—— Toast / 确认框 / 操作菜单

```typescript
@ComponentV2
struct DemoPage {
  build() {
    Column() {
      Button('提示').onClick(() => {
        this.getUIContext().getPromptAction().showToast({ message: '已保存', duration: 2000 })
      })
      Button('确认框').onClick(async () => {
        const res = await this.getUIContext().getPromptAction().showDialog({
          title: '删除', message: '确定删除该项？',
          buttons: [{ text: '取消', color: '#666' }, { text: '删除', color: '#E84026' }]
        })
        if (res.index === 1) { /* 用户点了"删除" */ }
      })
      Button('操作菜单').onClick(async () => {
        const res = await this.getUIContext().getPromptAction().showActionMenu({
          title: '更多', buttons: [{ text: '分享', color: '#000' }, { text: '举报', color: '#000' }]
        })
        console.info('选了第 ' + res.index + ' 项')
      })
    }
  }
}
```

## 2. 自定义内容弹窗

### 2a. @CustomDialog + CustomDialogController（经典，组件即弹窗）

```typescript
@CustomDialog
struct ConfirmDialog {
  controller: CustomDialogController
  title: string = ''
  confirm: () => void = () => {}

  build() {
    Column({ space: 16 }) {
      Text(this.title).fontSize(18)
      Row({ space: 12 }) {
        Button('取消').onClick(() => this.controller.close())
        Button('确定').onClick(() => { this.confirm(); this.controller.close() })
      }
    }.padding(24)
  }
}

@ComponentV2
struct Page {
  dialog: CustomDialogController = new CustomDialogController({
    builder: ConfirmDialog({ title: '确认操作', confirm: () => { /* ... */ } }),
    autoCancel: true, alignment: DialogAlignment.Center
  })
  build() {
    Button('打开').onClick(() => this.dialog.open())   // .open() / .close()
  }
}
```

### 2b. builder 形式（V2 首选，不耦合装饰器）

```typescript
@ComponentV2
struct Page2 {
  @Local count: number = 0
  @Builder dialogContent() {
    Column() { Text('当前 ' + this.count); Button('+1').onClick(() => this.count++) }.padding(24)
  }
  async openIt() {
    const id = await this.getUIContext().getPromptAction().openCustomDialog({
      builder: () => { this.dialogContent() }, alignment: DialogAlignment.Bottom
    })
    // 需要时：this.getUIContext().getPromptAction().closeCustomDialog(id)
  }
  build() { Button('打开').onClick(() => this.openIt()) }
}
```

### 2c. 页面级弹窗（实际原生宿主作用域的语义迁移）

- **症状**：只有实际源代码/观测证明弹层属于页面作用域、随宿主销毁且新页覆盖它时，才按该语义迁移；SwiftUI sheet/overlay 与 UIKit present 的生命周期和层级须逐项核实，不能一概视为相同。直接套 §2a/§2b（默认全局级）行为相反：弹窗层级高于所有路由页，跳转后**恒盖在新页之上**，且不主动 `close` 就不消失。
- **正解**：`openCustomDialog` 的 options 设 `levelMode: LevelMode.EMBEDDED` 启用页面级——弹窗节点挂到当前 Page 下；配 `levelUniqueId`（某 FrameNode 的 uniqueId）则挂到该节点所在 NavDestination 下。

```typescript
import { LevelMode, ImmersiveMode } from '@kit.ArkUI'

const node = this.getUIContext().getFrameNodeById('target_node')
this.getUIContext().getPromptAction().openCustomDialog({
  builder: () => { this.dialogContent() },
  levelMode: LevelMode.EMBEDDED,
  levelUniqueId: node?.getUniqueId(),          // 节点须在某 NavDestination 内才挂该 NavDestination；否则（含省略）挂当前 Page
  immersiveMode: ImmersiveMode.EXTEND,          // 蒙层默认不遮状态栏/导航条，需覆盖时设 EXTEND
})
```

- **约束**：`levelMode` 页面级能力自 **API 15+** 起可用；仅**非子窗模式**生效（`showInSubWindow` 不设或 `false`）；`levelUniqueId` 找不到节点则页面级能力不生效；更隐蔽的是 `levelUniqueId` 指向的节点存在、但**向上遍历不存在 NavDestination 节点**（如宿主视图是 Navigation 的 navBar 首页内容）——弹窗节点挂到 **Page 节点下**，显示层级高于该 Page 下所有 Navigation 页面，静默退化为盖住后续 push 的所有页面。交互差异：页面级弹窗侧滑手势先关弹窗再返回上一页（需两次侧滑）。
- **备选**：宿主是 Navigation navBar/首页内容（EMBEDDED 会静默退化），或需弹窗参与路由栈被后续 push 天然覆盖 → 用透明弹窗页 `NavDestinationMode.DIALOG`（指针 → `arkts-navigation-builder`，此处不展开）；navBar 宿主，或纯页内、不涉路由的简单场景 → 用页内 `Stack` 叠一层浮层替代（push 页完整覆盖、返回后浮层仍在）。
- **负向守卫**：用完即关、不跨路由跳转的普通确认框 / Toast / 半模态 Sheet **无需** `levelMode`——它们本就随交互关闭，别硬套页面级。

## 3. bindSheet —— 底部半模态面板

```typescript
@ComponentV2
struct SheetDemo {
  @Local isShow: boolean = false
  @Builder sheetBody() {
    Column() { Text('筛选条件').fontSize(18); /* ... */ }.padding(16)
  }
  build() {
    Button('打开面板')
      .onClick(() => { this.isShow = true })
      .bindSheet($$this.isShow, this.sheetBody(), {   // $$ 双向绑定 isShow
        detents: [SheetSize.MEDIUM, SheetSize.LARGE], // 多档高度，可上拉
        showClose: true,
        preferType: SheetType.BOTTOM,
        title: { title: '筛选' },
        onDisappear: () => { this.isShow = false }
      })
  }
}
```

## 4. bindContentCover —— 全屏模态

```typescript
@ComponentV2
struct CoverDemo {
  @Local isShow: boolean = false
  @Builder coverBody() {
    Column() {
      Row() { Button('关闭').onClick(() => { this.isShow = false }) }
      Text('全屏内容（详情 / 编辑流）')
    }.width('100%').height('100%')
  }
  build() {
    Button('全屏打开')
      .onClick(() => { this.isShow = true })
      .bindContentCover($$this.isShow, this.coverBody(), {
        modalTransition: ModalTransition.DEFAULT,  // DEFAULT / NONE / ALPHA
        onDisappear: () => { this.isShow = false }
      })
  }
}
```

## 关键规则

- **V2 一律 UIContext 形式**：`this.getUIContext().getPromptAction()` —— 不要用已废弃的全局 `promptAction.showToast(...)` / `AlertDialog.show(...)`。
- `bindSheet` / `bindContentCover` 的第一参用 **`$$this.isShow`** 双向绑定，关闭时回写 `false`（或在 `onDisappear` 里同步），否则二次打开失效。
- `@CustomDialog` 弹窗内的状态用其自身组件装饰器；跨弹窗共享状态用 `AppStorageV2` / `@Provider`。
- 选 Sheet 还是 ContentCover：半屏可交互保留背景上下文 → bindSheet；全屏独立流程 → bindContentCover。
