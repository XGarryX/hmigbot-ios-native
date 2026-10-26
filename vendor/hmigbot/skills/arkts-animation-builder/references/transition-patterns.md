# Transition 转场动画完整参考（**V1 历史文档 — Legacy**）

> ⚠️ **本项目锁 ArkTS V2**。本文档为 **V1 历史参考**（`@Component / @State` 装饰器持有 transition 触发条件），仅用于阅读老代码或迁移老项目时查阅。
>
> **新代码请使用 V2 装饰器**：参阅 [`v2-transition-patterns.md`](./v2-transition-patterns.md)（V2 主参考）和 [`SKILL.md`](../SKILL.md)。
>
> 注意：`TransitionEffect / .transition() / .animation()` 等转场 API 在 V1/V2 中完全相同；仅持有触发条件的状态装饰器从 `@State` → `@Local`、`@Component` → `@ComponentV2`。

---

## 1. 淡入淡出（opacity transition）

```typescript
// 元素出现/消失时做透明度过渡
@Component
struct FadeTransition {
  @State isVisible: boolean = false

  build() {
    Column({ space: 30 }) {
      Button(this.isVisible ? '隐藏内容' : '显示内容')
        .fontSize(16)
        .onClick(() => {
          animateTo({ duration: 400, curve: Curve.EaseInOut }, () => {
            this.isVisible = !this.isVisible
          })
        })

      if (this.isVisible) {
        Column() {
          Text('淡入淡出内容')
            .fontSize(20)
            .fontColor(Color.White)
        }
        .width(250)
        .height(150)
        .backgroundColor('#667EEA')
        .borderRadius(16)
        .justifyContent(FlexAlign.Center)
        .transition(TransitionEffect.OPACITY)
      }
    }
    .width('100%')
    .height('100%')
    .justifyContent(FlexAlign.Center)
  }
}
```

## 2. 从底部滑入（模态弹窗风格）

```typescript
// 模拟从底部滑出的模态面板
@Component
struct SlideFromBottom {
  @State showPanel: boolean = false

  build() {
    Stack({ alignContent: Alignment.Bottom }) {
      // 主内容
      Column() {
        Button('打开面板')
          .fontSize(16)
          .onClick(() => {
            animateTo({
              duration: 350,
              curve: curves.springMotion(0.6, 0.9)
            }, () => {
              this.showPanel = true
            })
          })
      }
      .width('100%')
      .height('100%')
      .justifyContent(FlexAlign.Center)

      // 遮罩层
      if (this.showPanel) {
        Column()
          .width('100%')
          .height('100%')
          .backgroundColor('#00000066')
          .transition(TransitionEffect.OPACITY)
          .onClick(() => {
            animateTo({ duration: 300, curve: Curve.EaseOut }, () => {
              this.showPanel = false
            })
          })
      }

      // 底部面板
      if (this.showPanel) {
        Column({ space: 16 }) {
          Row()
            .width(40)
            .height(4)
            .borderRadius(2)
            .backgroundColor('#CCCCCC')
            .margin({ top: 8 })
          Text('底部面板标题')
            .fontSize(20)
            .fontWeight(FontWeight.Bold)
          Text('这是从底部滑入的内容面板，常用于显示详情或操作选项。')
            .fontSize(14)
            .fontColor('#666666')
            .padding({ left: 20, right: 20 })
          Button('确定')
            .width('80%')
            .margin({ top: 10, bottom: 20 })
            .onClick(() => {
              animateTo({ duration: 300, curve: Curve.EaseOut }, () => {
                this.showPanel = false
              })
            })
        }
        .width('100%')
        .backgroundColor(Color.White)
        .borderRadius({ topLeft: 20, topRight: 20 })
        .transition(TransitionEffect.translate({ y: 300 }).combine(TransitionEffect.OPACITY))
      }
    }
    .width('100%')
    .height('100%')
  }
}
```

## 3. 缩放 + 淡入（弹窗/对话框风格）

```typescript
// 弹窗从中心缩放弹出
@Component
struct ScaleFadeDialog {
  @State showDialog: boolean = false

  build() {
    Stack() {
      Button('显示对话框')
        .fontSize(16)
        .onClick(() => {
          animateTo({
            duration: 250,
            curve: curves.springMotion(0.5, 0.8)
          }, () => {
            this.showDialog = true
          })
        })

      if (this.showDialog) {
        // 遮罩
        Column()
          .width('100%')
          .height('100%')
          .backgroundColor('#00000055')
          .transition(TransitionEffect.OPACITY)
          .onClick(() => {
            animateTo({ duration: 200, curve: Curve.EaseIn }, () => {
              this.showDialog = false
            })
          })

        // 对话框内容
        Column({ space: 16 }) {
          Text('提示')
            .fontSize(20)
            .fontWeight(FontWeight.Bold)
          Text('确定要执行此操作吗？此操作不可撤销。')
            .fontSize(14)
            .fontColor('#666666')
            .textAlign(TextAlign.Center)
          Row({ space: 12 }) {
            Button('取消')
              .backgroundColor(Color.Gray)
              .layoutWeight(1)
              .onClick(() => {
                animateTo({ duration: 200 }, () => {
                  this.showDialog = false
                })
              })
            Button('确定')
              .layoutWeight(1)
              .onClick(() => {
                animateTo({ duration: 200 }, () => {
                  this.showDialog = false
                })
              })
          }
          .width('100%')
        }
        .width('80%')
        .padding(24)
        .backgroundColor(Color.White)
        .borderRadius(16)
        .shadow({ radius: 20, color: '#33000000' })
        .transition(
          TransitionEffect.scale({ x: 0.7, y: 0.7 })
            .combine(TransitionEffect.OPACITY)
        )
      }
    }
    .width('100%')
    .height('100%')
  }
}
```

## 4. 左右滑动（页面导航风格）

```typescript
// 模拟页面左右切换的滑动动画
@Component
struct SlideNavigation {
  @State currentPage: number = 0

  build() {
    Column() {
      // 页面内容区
      Stack() {
        if (this.currentPage === 0) {
          Column() {
            Text('第一页')
              .fontSize(28)
              .fontWeight(FontWeight.Bold)
            Text('向右滑动查看下一页')
              .fontSize(14)
              .fontColor('#999999')
              .margin({ top: 10 })
          }
          .width('100%')
          .height('100%')
          .justifyContent(FlexAlign.Center)
          .backgroundColor('#E3F2FD')
          .transition(TransitionEffect.translate({ x: -300 }).combine(TransitionEffect.OPACITY))
        }

        if (this.currentPage === 1) {
          Column() {
            Text('第二页')
              .fontSize(28)
              .fontWeight(FontWeight.Bold)
            Text('可以返回上一页')
              .fontSize(14)
              .fontColor('#999999')
              .margin({ top: 10 })
          }
          .width('100%')
          .height('100%')
          .justifyContent(FlexAlign.Center)
          .backgroundColor('#F3E5F5')
          .transition(TransitionEffect.translate({ x: 300 }).combine(TransitionEffect.OPACITY))
        }
      }
      .layoutWeight(1)
      .width('100%')
      .clip(true)

      // 导航按钮
      Row({ space: 20 }) {
        Button('上一页')
          .enabled(this.currentPage > 0)
          .onClick(() => {
            animateTo({ duration: 300, curve: Curve.EaseInOut }, () => {
              this.currentPage = 0
            })
          })
        Button('下一页')
          .enabled(this.currentPage < 1)
          .onClick(() => {
            animateTo({ duration: 300, curve: Curve.EaseInOut }, () => {
              this.currentPage = 1
            })
          })
      }
      .width('100%')
      .justifyContent(FlexAlign.Center)
      .padding(20)
    }
    .width('100%')
    .height('100%')
  }
}
```

## 5. 非对称转场（进入和退出不同）

```typescript
// 进入时从下方弹入，退出时向右滑出
@Component
struct AsymmetricTransition {
  @State showCard: boolean = false

  build() {
    Column({ space: 30 }) {
      Button(this.showCard ? '移除卡片' : '添加卡片')
        .fontSize(16)
        .onClick(() => {
          animateTo({
            duration: 400,
            curve: curves.springMotion(0.6, 0.9)
          }, () => {
            this.showCard = !this.showCard
          })
        })

      if (this.showCard) {
        Column({ space: 10 }) {
          Image($r('app.media.icon'))
            .width(60)
            .height(60)
            .borderRadius(30)
          Text('用户名称')
            .fontSize(18)
            .fontWeight(FontWeight.Bold)
          Text('这张卡片进入时从下方弹入，退出时向右滑出消失')
            .fontSize(12)
            .fontColor('#999999')
            .textAlign(TextAlign.Center)
        }
        .width('80%')
        .padding(24)
        .backgroundColor(Color.White)
        .borderRadius(16)
        .shadow({ radius: 12, color: '#22000000', offsetY: 4 })
        .transition(
          TransitionEffect.asymmetric(
            // 进入效果：从下方滑入 + 淡入
            TransitionEffect.translate({ y: 200 })
              .combine(TransitionEffect.OPACITY)
              .animation({ duration: 400, curve: curves.springMotion(0.6, 0.9) }),
            // 退出效果：向右滑出 + 缩小 + 淡出
            TransitionEffect.translate({ x: 300 })
              .combine(TransitionEffect.scale({ x: 0.8, y: 0.8 }))
              .combine(TransitionEffect.OPACITY)
              .animation({ duration: 300, curve: Curve.EaseIn })
          )
        )
      }
    }
    .width('100%')
    .height('100%')
    .justifyContent(FlexAlign.Center)
    .backgroundColor('#F5F5F5')
  }
}
```

## 6. 列表项添加/删除转场

```typescript
// 列表动态添加和删除项时带有动画效果
@Component
struct ListTransition {
  @State items: string[] = ['项目 A', '项目 B', '项目 C']
  private counter: number = 0

  build() {
    Column({ space: 16 }) {
      Row({ space: 12 }) {
        Button('添加项')
          .fontSize(14)
          .onClick(() => {
            this.counter++
            animateTo({
              duration: 350,
              curve: curves.springMotion(0.6, 0.9)
            }, () => {
              this.items.splice(0, 0, `新增项 ${this.counter}`)
            })
          })
        Button('删除首项')
          .fontSize(14)
          .backgroundColor(Color.Red)
          .enabled(this.items.length > 0)
          .onClick(() => {
            animateTo({
              duration: 300,
              curve: Curve.EaseOut
            }, () => {
              this.items.splice(0, 1)
            })
          })
      }

      List({ space: 8 }) {
        ForEach(this.items, (item: string) => {
          ListItem() {
            Row() {
              Text(item)
                .fontSize(16)
              Blank()
              Text('>')
                .fontSize(14)
                .fontColor('#CCCCCC')
            }
            .width('100%')
            .padding(16)
            .backgroundColor(Color.White)
            .borderRadius(8)
            .shadow({ radius: 4, color: '#0A000000', offsetY: 1 })
          }
          .transition(
            TransitionEffect.asymmetric(
              // 添加时：从左侧滑入 + 淡入
              TransitionEffect.translate({ x: -300 })
                .combine(TransitionEffect.OPACITY),
              // 删除时：向右滑出 + 缩小
              TransitionEffect.translate({ x: 300 })
                .combine(TransitionEffect.scale({ x: 0.8, y: 0.8 }))
                .combine(TransitionEffect.OPACITY)
            )
          )
        }, (item: string) => item)
      }
      .width('90%')
      .layoutWeight(1)
    }
    .width('100%')
    .height('100%')
    .padding({ top: 20 })
    .backgroundColor('#F5F5F5')
  }
}
```

## 7. 旋转转场动画

```typescript
// 元素出现时带旋转效果
@Component
struct RotateTransition {
  @State showElements: boolean = false

  build() {
    Column({ space: 30 }) {
      Button(this.showElements ? '隐藏' : '显示图标')
        .fontSize(16)
        .onClick(() => {
          animateTo({
            duration: 500,
            curve: curves.springMotion(0.5, 0.8)
          }, () => {
            this.showElements = !this.showElements
          })
        })

      if (this.showElements) {
        Row({ space: 20 }) {
          // 顺时针旋转进入
          Column() {
            Text('+')
              .fontSize(30)
              .fontColor(Color.White)
          }
          .width(60)
          .height(60)
          .borderRadius(30)
          .backgroundColor('#FF6B6B')
          .justifyContent(FlexAlign.Center)
          .transition(
            TransitionEffect.rotate({ angle: -180 })
              .combine(TransitionEffect.scale({ x: 0, y: 0 }))
              .combine(TransitionEffect.OPACITY)
          )

          // 逆时针旋转进入
          Column() {
            Text('★')
              .fontSize(24)
              .fontColor(Color.White)
          }
          .width(60)
          .height(60)
          .borderRadius(30)
          .backgroundColor('#4ECDC4')
          .justifyContent(FlexAlign.Center)
          .transition(
            TransitionEffect.rotate({ angle: 180 })
              .combine(TransitionEffect.scale({ x: 0, y: 0 }))
              .combine(TransitionEffect.OPACITY)
          )

          // 3D 翻转效果
          Column() {
            Text('♥')
              .fontSize(24)
              .fontColor(Color.White)
          }
          .width(60)
          .height(60)
          .borderRadius(30)
          .backgroundColor('#667EEA')
          .justifyContent(FlexAlign.Center)
          .transition(
            TransitionEffect.rotate({ x: 1, angle: -90 })
              .combine(TransitionEffect.OPACITY)
          )
        }
      }
    }
    .width('100%')
    .height('100%')
    .justifyContent(FlexAlign.Center)
  }
}
```

## 8. 组合多个 TransitionEffect

```typescript
// 展示 TransitionEffect 的多种组合方式
@Component
struct CombinedTransitions {
  @State showA: boolean = false
  @State showB: boolean = false
  @State showC: boolean = false

  build() {
    Column({ space: 20 }) {
      // 按钮区
      Row({ space: 10 }) {
        Button('效果A')
          .fontSize(14)
          .onClick(() => {
            animateTo({ duration: 400, curve: curves.springMotion(0.6, 0.9) }, () => {
              this.showA = !this.showA
            })
          })
        Button('效果B')
          .fontSize(14)
          .onClick(() => {
            animateTo({ duration: 400, curve: curves.springMotion(0.6, 0.9) }, () => {
              this.showB = !this.showB
            })
          })
        Button('效果C')
          .fontSize(14)
          .onClick(() => {
            animateTo({ duration: 400, curve: curves.springMotion(0.6, 0.9) }, () => {
              this.showC = !this.showC
            })
          })
      }

      // 效果 A：滑入 + 缩放 + 透明度
      if (this.showA) {
        Text('滑入 + 缩放 + 透明')
          .fontSize(16)
          .fontColor(Color.White)
          .padding(16)
          .backgroundColor('#FF6B6B')
          .borderRadius(12)
          .transition(
            TransitionEffect.OPACITY
              .combine(TransitionEffect.translate({ y: 50 }))
              .combine(TransitionEffect.scale({ x: 0.5, y: 0.5 }))
          )
      }

      // 效果 B：旋转 + 滑入 + 透明度（带自定义动画参数）
      if (this.showB) {
        Text('旋转 + 滑入 + 透明')
          .fontSize(16)
          .fontColor(Color.White)
          .padding(16)
          .backgroundColor('#4ECDC4')
          .borderRadius(12)
          .transition(
            TransitionEffect.OPACITY
              .combine(TransitionEffect.translate({ x: -100 }))
              .combine(TransitionEffect.rotate({ angle: -45 }))
              .animation({ duration: 500, curve: Curve.EaseOut })
          )
      }

      // 效果 C：非对称组合（进入和退出分别组合不同效果）
      if (this.showC) {
        Text('非对称组合效果')
          .fontSize(16)
          .fontColor(Color.White)
          .padding(16)
          .backgroundColor('#667EEA')
          .borderRadius(12)
          .transition(
            TransitionEffect.asymmetric(
              // 进入：从底部弹入 + 旋转 + 缩放
              TransitionEffect.translate({ y: 100 })
                .combine(TransitionEffect.rotate({ angle: -30 }))
                .combine(TransitionEffect.scale({ x: 0.3, y: 0.3 }))
                .combine(TransitionEffect.OPACITY)
                .animation({ duration: 500, curve: curves.springMotion(0.5, 0.8) }),
              // 退出：向上飞出 + 缩小
              TransitionEffect.translate({ y: -200 })
                .combine(TransitionEffect.scale({ x: 0, y: 0 }))
                .combine(TransitionEffect.OPACITY)
                .animation({ duration: 300, curve: Curve.EaseIn })
            )
          )
      }
    }
    .width('100%')
    .height('100%')
    .justifyContent(FlexAlign.Center)
    .padding(20)
  }
}
```
