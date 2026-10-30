# V2 业务模式：带校验的表单页 + 底部 Sheet / 模态

> 补 pattern-library 缺的两个高频交互模式。**经 harmony-docs（快照 2026-05-24）核验**，V2 装饰器。
> 弹窗/Sheet 的底层 API 见 `arkts-component-builder/references/v2-dialogs-and-sheets.md`；本文是业务模式编排。

## 模式 A：带校验的表单页（注册 / 资料编辑 / 提交流）

要点：每个字段一个 `@Local`；用 `@Computed` 派生「是否合法」驱动提交按钮；`onChange` 实时校验并写错误文案。

```typescript
@ComponentV2
struct ProfileForm {
  @Local name: string = ''
  @Local phone: string = ''
  @Local nameErr: string = ''
  @Local phoneErr: string = ''

  @Computed get formValid(): boolean {                 // 派生态：随字段自动重算
    return this.name.length >= 2 && /^1\d{10}$/.test(this.phone)
  }

  validateName(v: string): void { this.nameErr = v.length >= 2 ? '' : '至少 2 个字符' }
  validatePhone(v: string): void { this.phoneErr = /^1\d{10}$/.test(v) ? '' : '手机号格式错误' }

  build() {
    Column({ space: 12 }) {
      TextInput({ text: this.name, placeholder: '姓名' })
        .onChange((v: string) => { this.name = v; this.validateName(v) })
      if (this.nameErr) { Text(this.nameErr).fontColor('#E84026').fontSize(12) }

      TextInput({ text: this.phone, placeholder: '手机号' }).type(InputType.PhoneNumber)
        .onChange((v: string) => { this.phone = v; this.validatePhone(v) })
      if (this.phoneErr) { Text(this.phoneErr).fontColor('#E84026').fontSize(12) }

      Button('提交')
        .enabled(this.formValid)                        // 校验不过则禁用提交
        .onClick(() => this.submit())
    }.padding(16)
  }
  submit(): void { /* 调用 arkts-data-layer 的服务层提交 */ }
}
```
**关键点**：`@Computed formValid` 自动随字段变化重算，提交按钮 `.enabled()` 直接绑它；错误文案用 `@Local xxxErr` + 条件渲染。字段多时把校验规则抽成 `validators: Record<string, (v)=>string>` 表统一驱动。

## 模式 B：底部 Sheet / 模态（筛选 / 分享 / 评论面板）

要点：`@Local` 控制显隐；`bindSheet($$..., builder, options)`；面板内编辑**草稿**态，点「应用」才回写生效态（取消则丢弃）。

```typescript
@ComponentV2
struct ListWithFilter {
  @Local showFilter: boolean = false
  @Local applied: string = 'all'        // 已生效筛选
  @Local draft: string = 'all'          // 面板内草稿

  @Builder filterSheet() {
    Column({ space: 12 }) {
      Text('筛选').fontSize(18)
      Row({ space: 8 }) {
        ForEach(['all', 'unread', 'star'], (k: string) => {
          Button(k)
            .type(this.draft === k ? ButtonType.Capsule : ButtonType.Normal)
            .onClick(() => { this.draft = k })
        })
      }
      Row({ space: 12 }) {
        Button('重置').onClick(() => { this.draft = 'all' })
        Button('应用').onClick(() => { this.applied = this.draft; this.showFilter = false })
      }
    }.padding(16)
  }

  build() {
    Column() {
      Button('筛选: ' + this.applied)
        .onClick(() => { this.draft = this.applied; this.showFilter = true })  // 打开时 draft←applied
      List() { /* 按 this.applied 过滤后的列表 */ }
    }
    .bindSheet($$this.showFilter, this.filterSheet(), {
      detents: [SheetSize.MEDIUM], showClose: true,
      onDisappear: () => { this.showFilter = false }
    })
  }
}
```
**关键点**：草稿态 `draft` 与生效态 `applied` 分离——打开时 `draft←applied`，应用时 `applied←draft`，取消则 `draft` 丢弃，列表只随 `applied` 变。`$$` 双向绑定 `showFilter`。多步编辑流程改用 `bindContentCover`（全屏）。

## 跨文档参考
- `arkts-component-builder/references/v2-dialogs-and-sheets.md` — bindSheet / bindContentCover / CustomDialog 底层 API
- `arkts-component-builder/references/v2-scroll-and-form-components.md` — TextArea / Checkbox / Radio 表单控件
- `arkts-state-manager/references/v2-decorators.md` — `@Computed` / `@Local` 规则
