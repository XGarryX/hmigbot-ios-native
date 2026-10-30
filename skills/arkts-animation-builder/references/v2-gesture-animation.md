# 手势 + 动画组合完整参考（V2）

> 本文档基于 ArkTS V2（API 12+ 推荐）。**本项目锁 V2**，本文档为主参考。
> `PanGesture / TapGesture / LongPressGesture / PinchGesture / GestureGroup / DragEvent / .draggable()` 等手势 API 在 V1/V2 完全相同；仅持有手势驱动状态（offsetX、scaleValue 等）的装饰器从 `@State` → `@Local`、`@Component` → `@ComponentV2`。
> V1 版本查阅请见 [`gesture-animation.md`](./gesture-animation.md)。
>
> **必要 import**：本文示例凡用到 `curves.springMotion` 处，文件顶部须有 `import { curves } from '@kit.ArkUI';`（真实模块导出，非 ambient；`*Gesture / GestureGroup / DragEvent / .draggable` 才是 ambient 免 import）。
> **拖拽收尾用 `onDragEnd`，没有 `onDragCancel`**；`@Builder` 预览方法名避开 `dragPreview`（内置 attribute）——用 `dragPreviewBuilder`。

---

## 1. 卡片滑动（Tinder 风格 PanGesture 卡片切换）

```typescript
import { curves } from '@kit.ArkUI';   // curves.* 是真实模块导出，必须 import

// Tinder 风格的左右滑动卡片：拖动时卡片跟手旋转，松手后判断方向飞出或弹回
@ComponentV2
struct SwipeCard {
  @Local offsetX: number = 0
  @Local offsetY: number = 0
  @Local rotateAngle: number = 0
  @Local cardOpacity: number = 1
  @Local currentIndex: number = 0
  private cards: string[] = ['卡片 A', '卡片 B', '卡片 C', '卡片 D', '卡片 E']
  private colors: string[] = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']

  build() {
    Column() {
      Stack() {
        // 下一张卡片（底层）
        if (this.currentIndex + 1 < this.cards.length) {
          Column() {
            Text(this.cards[this.currentIndex + 1])
              .fontSize(24).fontColor(Color.White).fontWeight(FontWeight.Bold)
          }
          .width(280).height(380)
          .backgroundColor(this.colors[(this.currentIndex + 1) % this.colors.length])
          .borderRadius(20).justifyContent(FlexAlign.Center)
          .scale({ x: 0.95, y: 0.95 })
        }

        // 当前卡片（顶层，可拖动）
        if (this.currentIndex < this.cards.length) {
          Column({ space: 12 }) {
            Text(this.cards[this.currentIndex])
              .fontSize(28).fontColor(Color.White).fontWeight(FontWeight.Bold)
            Text('← 左滑拒绝  右滑喜欢 →').fontSize(12).fontColor('#FFFFFFAA')
          }
          .width(280).height(380)
          .backgroundColor(this.colors[this.currentIndex % this.colors.length])
          .borderRadius(20).justifyContent(FlexAlign.Center)
          .shadow({ radius: 16, color: '#33000000', offsetY: 4 })
          .translate({ x: this.offsetX, y: this.offsetY })
          .rotate({ angle: this.rotateAngle })
          .opacity(this.cardOpacity)
          .gesture(
            PanGesture()
              .onActionUpdate((event: GestureEvent) => {
                this.offsetX = event.offsetX
                this.offsetY = event.offsetY
                this.rotateAngle = event.offsetX * 0.05
              })
              .onActionEnd((event: GestureEvent) => {
                let velocityX = event.velocity
                if (Math.abs(this.offsetX) > 120 || Math.abs(velocityX) > 800) {
                  let direction = this.offsetX > 0 ? 1 : -1
                  animateTo({ duration: 300, curve: Curve.EaseOut }, () => {
                    this.offsetX = direction * 500
                    this.rotateAngle = direction * 30
                    this.cardOpacity = 0
                  })
                  setTimeout(() => {
                    this.offsetX = 0
                    this.offsetY = 0
                    this.rotateAngle = 0
                    this.cardOpacity = 1
                    this.currentIndex++
                  }, 300)
                } else {
                  animateTo({
                    duration: 400,
                    curve: curves.springMotion(0.5, 0.8)
                  }, () => {
                    this.offsetX = 0
                    this.offsetY = 0
                    this.rotateAngle = 0
                  })
                }
              })
          )
        }
      }

      if (this.currentIndex >= this.cards.length) {
        Text('没有更多卡片了').fontSize(18).fontColor('#999999').margin({ top: 40 })
      }
    }
    .width('100%').height('100%').justifyContent(FlexAlign.Center).backgroundColor('#F5F5F5')
  }
}
```

## 2. 下拉刷新自定义动画

```typescript
// 自定义下拉刷新：拖动时显示加载指示器，松手后触发刷新
@ComponentV2
struct PullToRefreshCustom {
  @Local pullDistance: number = 0
  @Local isRefreshing: boolean = false
  @Local rotateAngle: number = 0
  @Local items: string[] = ['项目 1', '项目 2', '项目 3', '项目 4', '项目 5']
  private threshold: number = 80
  private timer: number = -1

  // 模拟刷新
  private startRefresh(): void {
    this.isRefreshing = true
    this.startSpinning()
    setTimeout(() => {
      this.isRefreshing = false
      if (this.timer !== -1) {
        clearInterval(this.timer)
        this.timer = -1
      }
      animateTo({ duration: 300, curve: Curve.EaseOut }, () => {
        this.pullDistance = 0
        this.rotateAngle = 0
      })
      this.items.splice(0, 0, `新项目 ${Date.now() % 1000}`)
    }, 2000)
  }

  private startSpinning(): void {
    this.timer = setInterval(() => {
      this.rotateAngle = (this.rotateAngle + 10) % 360
    }, 16)
  }

  build() {
    Column() {
      Column() {
        if (this.pullDistance > 10 || this.isRefreshing) {
          Column() {
            Text('↻').fontSize(28)
              .rotate({ angle: this.isRefreshing ? this.rotateAngle : this.pullDistance * 3 })
            Text(this.isRefreshing ? '刷新中...' :
              (this.pullDistance >= this.threshold ? '释放刷新' : '下拉刷新'))
              .fontSize(12).fontColor('#999999').margin({ top: 4 })
          }
        }
      }
      .width('100%').height(Math.min(this.pullDistance, 120))
      .justifyContent(FlexAlign.Center)

      List({ space: 8 }) {
        ForEach(this.items, (item: string) => {
          ListItem() {
            Row() { Text(item).fontSize(16) }
              .width('100%').height(56).padding({ left: 16 })
              .backgroundColor(Color.White).borderRadius(8)
          }
        }, (item: string, index: number) => `${item}_${index}`)
      }
      .width('90%').layoutWeight(1)
    }
    .width('100%').height('100%')
    .backgroundColor('#F5F5F5').padding({ top: 10 })
    .gesture(
      PanGesture({ direction: PanDirection.Vertical })
        .onActionUpdate((event: GestureEvent) => {
          if (!this.isRefreshing && event.offsetY > 0) {
            this.pullDistance = event.offsetY * 0.5
          }
        })
        .onActionEnd(() => {
          if (!this.isRefreshing) {
            if (this.pullDistance >= this.threshold) {
              animateTo({ duration: 200 }, () => { this.pullDistance = 60 })
              this.startRefresh()
            } else {
              animateTo({ duration: 300, curve: Curve.EaseOut }, () => {
                this.pullDistance = 0
              })
            }
          }
        })
    )
  }
}
```

## 3. 捏合缩放（PinchGesture + scale）

```typescript
// 图片捏合缩放 + 双击还原
@ComponentV2
struct PinchZoomImage {
  @Local scaleValue: number = 1
  @Local lastScale: number = 1
  @Local offsetX: number = 0
  @Local offsetY: number = 0
  @Local lastOffsetX: number = 0
  @Local lastOffsetY: number = 0

  build() {
    Column() {
      Text('捏合缩放 / 双击还原').fontSize(16).fontColor('#999999').margin({ bottom: 20 })

      Stack() {
        Image($r('app.media.icon'))
          .width('100%').height('100%').objectFit(ImageFit.Contain)
          .scale({ x: this.scaleValue, y: this.scaleValue })
          .translate({ x: this.offsetX, y: this.offsetY })
      }
      .width('90%').height(400)
      .backgroundColor('#F0F0F0').borderRadius(12).clip(true)
      .gesture(
        GestureGroup(GestureMode.Parallel,
          PinchGesture({ fingers: 2 })
            .onActionUpdate((event: GestureEvent) => {
              let newScale = this.lastScale * event.scale
              this.scaleValue = Math.max(0.5, Math.min(5, newScale))
            })
            .onActionEnd(() => {
              this.lastScale = this.scaleValue
              if (this.scaleValue < 1) {
                animateTo({
                  duration: 300,
                  curve: curves.springMotion(0.6, 0.9)
                }, () => {
                  this.scaleValue = 1
                  this.lastScale = 1
                  this.offsetX = 0
                  this.offsetY = 0
                  this.lastOffsetX = 0
                  this.lastOffsetY = 0
                })
              }
            }),
          PanGesture()
            .onActionUpdate((event: GestureEvent) => {
              if (this.scaleValue > 1) {
                this.offsetX = this.lastOffsetX + event.offsetX
                this.offsetY = this.lastOffsetY + event.offsetY
              }
            })
            .onActionEnd(() => {
              this.lastOffsetX = this.offsetX
              this.lastOffsetY = this.offsetY
            }),
          TapGesture({ count: 2 })
            .onAction(() => {
              animateTo({
                duration: 300,
                curve: curves.springMotion(0.6, 0.9)
              }, () => {
                this.scaleValue = 1
                this.lastScale = 1
                this.offsetX = 0
                this.offsetY = 0
                this.lastOffsetX = 0
                this.lastOffsetY = 0
              })
            })
        )
      )
    }
    .width('100%').height('100%').justifyContent(FlexAlign.Center)
  }
}
```

## 4. 长按 + 拖拽重排序

```typescript
// 长按激活拖拽，拖动排列列表项
@ComponentV2
struct LongPressDragReorder {
  @Local items: string[] = ['苹果', '香蕉', '橙子', '葡萄', '西瓜', '草莓']
  @Local dragIndex: number = -1
  @Local dragOffsetY: number = 0
  @Local itemScales: number[] = [1, 1, 1, 1, 1, 1]

  build() {
    Column({ space: 0 }) {
      Text('长按拖拽排序').fontSize(20).fontWeight(FontWeight.Bold).margin({ bottom: 16 })

      ForEach(this.items, (item: string, index: number) => {
        Row() {
          Text('≡').fontSize(20).fontColor('#CCCCCC').margin({ right: 12 })
          Text(item).fontSize(16)
          Blank()
          Text(`#${index + 1}`).fontSize(14).fontColor('#999999')
        }
        .width('90%').height(56)
        .padding({ left: 16, right: 16 })
        .backgroundColor(this.dragIndex === index ? '#E3F2FD' : Color.White)
        .borderRadius(8).margin({ bottom: 6 })
        .shadow({
          radius: this.dragIndex === index ? 12 : 2,
          color: '#1A000000',
          offsetY: this.dragIndex === index ? 4 : 1
        })
        .scale({ x: this.itemScales[index], y: this.itemScales[index] })
        .zIndex(this.dragIndex === index ? 100 : 0)
        .translate({ y: this.dragIndex === index ? this.dragOffsetY : 0 })
        .gesture(
          GestureGroup(GestureMode.Sequence,
            LongPressGesture({ repeat: false })
              .onAction(() => {
                this.dragIndex = index
                animateTo({ duration: 200 }, () => {
                  this.itemScales[index] = 1.05
                })
              }),
            PanGesture()
              .onActionUpdate((event: GestureEvent) => {
                this.dragOffsetY = event.offsetY
                let targetIndex = index + Math.round(event.offsetY / 62)
                targetIndex = Math.max(0, Math.min(this.items.length - 1, targetIndex))
                if (targetIndex !== this.dragIndex && targetIndex !== index) {
                  animateTo({ duration: 200 }, () => {
                    let dragItem = this.items.splice(this.dragIndex, 1)[0]
                    this.items.splice(targetIndex, 0, dragItem)
                    this.dragIndex = targetIndex
                    this.dragOffsetY = 0
                  })
                }
              })
              .onActionEnd(() => {
                animateTo({
                  duration: 300,
                  curve: curves.springMotion(0.6, 0.9)
                }, () => {
                  this.dragOffsetY = 0
                  if (this.dragIndex >= 0 && this.dragIndex < this.itemScales.length) {
                    this.itemScales[this.dragIndex] = 1
                  }
                  this.dragIndex = -1
                })
              })
          )
        )
      }, (item: string) => item)
    }
    .width('100%').height('100%').padding({ top: 20 })
    .backgroundColor('#F5F5F5').justifyContent(FlexAlign.Start)
  }
}
```

## 4-B. 列表拖拽排序（DragEvent 框架）

> **适用于**：列表/网格中的拖拽排序，跨容器拖拽，配合 LazyForEach 使用
> **对比**：若需要拖拽时带旋转/倾斜等复杂动画效果，参见 **4-A PanGesture 方案**

**必要依赖**：无需额外 import，使用 ArkUI 内置 `DragEvent` 即可。

```typescript
// 拖拽排序列表 — 使用 ArkTS 内置 DragEvent 框架
@ComponentV2
struct DragReorderList {
  @Local items: string[] = ['苹果', '香蕉', '橙子', '葡萄', '西瓜', '草莓']
  @Local dragIndex: number = -1
  @Local dragItem: string | null = null
  @Local isReorderMode: boolean = false

  @Builder
  dragPreviewBuilder() {
    Column() {
      Text(this.dragItem || '')
        .fontSize(14).maxLines(1)
        .textOverflow({ overflow: TextOverflow.Ellipsis })
    }
    .width(200).height(48)
    .padding({ left: 16, right: 16 })
    .backgroundColor('#FFFFFF')
    .border({ width: 1, color: '#CCCCCC', radius: 4 })
    .shadow({ radius: 4, color: 'rgba(0,0,0,0.15)', offsetX: 0, offsetY: 2 })
  }

  build() {
    Column({ space: 0 }) {
      Text('长按拖拽排序（DragEvent）')
        .fontSize(20).fontWeight(FontWeight.Bold).margin({ bottom: 16 })

      List() {
        ForEach(this.items, (item: string, index: number) => {
          ListItem() {
            Row() {
              if (this.isReorderMode) {
                SymbolGlyph($r('sys.symbol.line_3_horizontal'))
                  .fontSize(18).fontColor('#999999').margin({ right: 8 })
              }
              Text(item).fontSize(16)
              Blank()
              Text(`#${index + 1}`).fontSize(14).fontColor('#999999')
            }
            .width('100%').height(56)
            .padding({ left: 16, right: 16 })
            .backgroundColor(Color.White).borderRadius(8)
            .margin({ bottom: 6 })
            .shadow({ radius: 2, color: '#1A000000', offsetY: 1 })
          }
          .draggable(this.isReorderMode)
          .onDragStart(() => {
            this.dragIndex = index
            this.dragItem = item
            return this.dragPreviewBuilder()
          })
          .onDrop((event: DragEvent) => {
            if (this.dragIndex >= 0 && this.dragIndex !== index) {
              animateTo({ duration: 200 }, () => {
                const arr = [...this.items]
                const moved = arr.splice(this.dragIndex, 1)[0]
                arr.splice(index, 0, moved)
                this.items = arr
              })
            }
            this.dragIndex = -1
            this.dragItem = null
          })
          .onDragEnd(() => {   // 拖拽结束/取消统一在此清理（无 onDragCancel 事件）
            this.dragIndex = -1
            this.dragItem = null
          })
        }, (item: string) => item)
      }
      .width('90%').scrollBar(BarState.Auto)

      Row() {
        Button(this.isReorderMode ? '完成排序' : '进入排序模式')
          .onClick(() => { this.isReorderMode = !this.isReorderMode })
      }
      .margin({ top: 16 })
    }
    .width('100%').height('100%').padding({ top: 20 }).backgroundColor('#F5F5F5')
  }
}
```

**关键 API 说明**（V1/V2 通用）：

| API | 作用 |
|-----|------|
| `.draggable(boolean)` | 声明组件是否可拖拽 |
| `onDragStart()` | 拖拽开始，返回 `@Builder` 自定义拖拽预览 |
| `onDrop(DragEvent)` | 拖拽释放时执行排序逻辑 |
| `onDragEnd(DragEvent)` | 拖拽结束（含被取消）后清理状态。**注意：没有 `onDragCancel` 事件**，收尾统一用 `onDragEnd` |

### 两种方案对比

| 维度 | DragEvent 框架（本节） | PanGesture 方案（4-A） |
|------|----------------------|----------------------|
| 激活方式 | `.draggable(true)` 声明式启用 | `GestureGroup(Sequence, LongPressGesture...)` |
| 拖拽回调 | `onDragStart` / `onDrop` / `onDragEnd` | `PanGesture.onActionUpdate` |
| 预览 | `@Builder` 自定义，返回给系统渲染 | 自己用 `scale/translate` 模拟 |
| 性能 | 配合 LazyForEach 更优，系统级支持 | 需手动处理列表更新 |
| 适用场景 | 列表排序、跨容器拖拽 | 卡片滑动、自定义动画 |

---

## 5. 双击点赞（带心形动画）

```typescript
// 双击图片弹出心形点赞动画
@ComponentV2
struct DoubleTapLike {
  @Local isLiked: boolean = false
  @Local showHeart: boolean = false
  @Local heartScale: number = 0
  @Local heartOpacity: number = 0
  @Local likeCount: number = 128

  build() {
    Column({ space: 16 }) {
      Stack() {
        Column().width('100%').height('100%').backgroundColor('#E0E0E0')
        Image($r('app.media.icon'))
          .width('100%').height('100%').objectFit(ImageFit.Cover)

        if (this.showHeart) {
          Text('♥')
            .fontSize(80).fontColor(Color.White)
            .scale({ x: this.heartScale, y: this.heartScale })
            .opacity(this.heartOpacity)
        }
      }
      .width('100%').height(350).clip(true)
      .gesture(
        TapGesture({ count: 2 })
          .onAction(() => {
            if (!this.isLiked) {
              this.isLiked = true
              this.likeCount++
            }
            this.showHeart = true
            this.heartScale = 0
            this.heartOpacity = 1
            animateTo({
              duration: 400,
              curve: curves.springMotion(0.4, 0.7)
            }, () => {
              this.heartScale = 1.2
            })
            setTimeout(() => {
              animateTo({ duration: 300, curve: Curve.EaseOut }, () => {
                this.heartScale = 1.5
                this.heartOpacity = 0
              })
              setTimeout(() => { this.showHeart = false }, 300)
            }, 600)
          })
      )

      Row({ space: 8 }) {
        Text(this.isLiked ? '♥' : '♡')
          .fontSize(24).fontColor(this.isLiked ? Color.Red : '#333333')
          .onClick(() => {
            animateTo({ duration: 200 }, () => {
              this.isLiked = !this.isLiked
              this.likeCount += this.isLiked ? 1 : -1
            })
          })
        Text(`${this.likeCount}`).fontSize(16).fontColor('#333333')
      }
      .width('100%').padding({ left: 16 })
    }
    .width('100%').height('100%').backgroundColor(Color.White)
  }
}
```

## 5-B. 长按触发辅助操作（独立 LongPressGesture）

> **适用于**：点击做 A 操作，长按做 B 操作（如"查看列表"vs"新增内容"）
> **对比**：若长按后还需拖拽排序，参见 **4-A GestureGroup 方案**

**必要依赖**：无需额外 import，使用 `@kit.ArkUI` 中的 `LongPressGesture` 即可。

```typescript
// 点击 + 长按分工：点击查看已有内容，长按触发新增操作
@ComponentV2
struct LongPressSecondaryAction {
  @Local isBookmarked: boolean = false
  controller: CustomDialogController = new CustomDialogController({ builder: {} })

  build() {
    Column({ space: 20 }) {
      Text('书签图标').fontSize(20).fontWeight(FontWeight.Bold)

      Button('书签')
        .onClick(() => { console.info('点击：查看书签列表') })
        .gesture(
          LongPressGesture({ repeat: false })
            .onAction(() => { console.info('长按：打开添加书签表单') })
        )

      Text('点击按钮查看效果，长按按钮查看另一种效果').fontSize(12).fontColor('#999999')
    }
    .width('100%').height('100%').justifyContent(FlexAlign.Center)
  }
}
```

**关键要点**（V1/V2 通用）：

| 要点 | 说明 |
|------|------|
| `repeat: false` | 长按时只触发一次，避免重复触发 |
| `onClick` + `LongPressGesture` 同时绑定 | 两者互不冲突，系统已处理手势优先级 |
| 典型场景 | 图标按钮："查看已有"（点击）vs "新增"（长按） |
| 无需 GestureGroup | 本方案仅需独立的 `LongPressGesture`，比 GestureGroup 更简洁 |

---

## 6. 滑动删除（列表项侧滑显示操作按钮）

```typescript
// 列表项向左滑动露出删除按钮
@ComponentV2
struct SwipeToDelete {
  @Local items: string[] = ['消息 1: 你好', '消息 2: 明天见', '消息 3: 收到', '消息 4: 好的', '消息 5: 谢谢']
  @Local offsets: number[] = [0, 0, 0, 0, 0]

  build() {
    Column({ space: 8 }) {
      Text('滑动删除').fontSize(20).fontWeight(FontWeight.Bold).margin({ bottom: 12 })

      ForEach(this.items, (item: string, index: number) => {
        Row() {
          Row() {
            Column({ space: 4 }) {
              Text(item).fontSize(16)
              Text('2024-01-15 10:30').fontSize(12).fontColor('#999999')
            }
            .alignItems(HorizontalAlign.Start)
          }
          .width('100%').height(70).padding({ left: 16 })
          .backgroundColor(Color.White)
          .translate({ x: this.offsets[index] })
          .gesture(
            PanGesture({ direction: PanDirection.Horizontal })
              .onActionUpdate((event: GestureEvent) => {
                let newOffset = event.offsetX
                if (newOffset < 0) {
                  this.offsets[index] = Math.max(-80, newOffset)
                } else {
                  this.offsets[index] = 0
                }
              })
              .onActionEnd(() => {
                if (this.offsets[index] < -40) {
                  animateTo({ duration: 200, curve: Curve.EaseOut }, () => {
                    this.offsets[index] = -80
                  })
                } else {
                  animateTo({ duration: 200, curve: Curve.EaseOut }, () => {
                    this.offsets[index] = 0
                  })
                }
              })
          )

          Row() { Text('删除').fontSize(14).fontColor(Color.White) }
            .width(80).height(70).backgroundColor(Color.Red)
            .justifyContent(FlexAlign.Center)
            .position({ x: '100%', y: 0 })
            .translate({ x: this.offsets[index] })
            .onClick(() => {
              animateTo({ duration: 300, curve: Curve.EaseOut }, () => {
                this.offsets[index] = -400
              })
              setTimeout(() => {
                animateTo({ duration: 200 }, () => {
                  this.items.splice(index, 1)
                  this.offsets.splice(index, 1)
                })
              }, 300)
            })
        }
        .width('90%').height(70).borderRadius(8).clip(true)
        .shadow({ radius: 2, color: '#0D000000', offsetY: 1 })
      }, (item: string, index: number) => `${item}_${index}`)
    }
    .width('100%').height('100%').padding({ top: 20 }).backgroundColor('#F5F5F5')
  }
}
```

---

## 7. 把手势动画状态封装到 @ObservedV2 类

复杂的手势页面（含多个变量），把状态打包成类，便于复用 + 测试：

```typescript
@ObservedV2
class SwipeState {
  @Trace offsetX: number = 0
  @Trace offsetY: number = 0
  @Trace rotateAngle: number = 0
  @Trace cardOpacity: number = 1

  reset(): void {
    this.offsetX = 0
    this.offsetY = 0
    this.rotateAngle = 0
    this.cardOpacity = 1
  }
}

@ComponentV2
struct CardSwiper {
  @Local state: SwipeState = new SwipeState()

  build() {
    Column()
      .width(280).height(380).borderRadius(20)
      .backgroundColor('#FF6B6B')
      .translate({ x: this.state.offsetX, y: this.state.offsetY })
      .rotate({ angle: this.state.rotateAngle })
      .opacity(this.state.cardOpacity)
      .gesture(
        PanGesture()
          .onActionUpdate((e: GestureEvent) => {
            this.state.offsetX = e.offsetX
            this.state.offsetY = e.offsetY
            this.state.rotateAngle = e.offsetX * 0.05
          })
          .onActionEnd(() => {
            animateTo({
              duration: 400,
              curve: curves.springMotion(0.5, 0.8)
            }, () => {
              this.state.reset()
            })
          })
      )
  }
}
```
