# animateTo 显式动画完整参考（V2）

> 本文档基于 ArkTS V2（API 12+ 推荐）。**本项目锁 V2**，本文档为主参考。
> 动画 API 本身（`animateTo / curves / Curve / PlayMode`）在 V1/V2 完全相同；仅持有动画值的状态装饰器从 `@State` → `@Local`、`@Component` → `@ComponentV2`。
> V1 版本查阅请见 [`explicit-animation.md`](./explicit-animation.md)。
>
> **必要 import**：本文示例凡出现 `curves.springMotion / curves.interpolatingSpring` 处，文件顶部都须有 `import { curves } from '@kit.ArkUI';`（`curves` 是真实模块导出，非 ambient；漏则 `Cannot find name 'curves'`）。为省略未在每段重复，生成时务必补上。

---

## 1. 按钮缩放动画（弹跳效果）

```typescript
import { curves } from '@kit.ArkUI';   // curves.* 是真实模块导出，必须 import

// 按钮点击时产生弹跳缩放效果
@ComponentV2
struct BounceButton {
  @Local scaleValue: number = 1

  build() {
    Column() {
      Button('点击弹跳')
        .fontSize(18)
        .width(200)
        .height(50)
        .scale({ x: this.scaleValue, y: this.scaleValue })
        .onClick(() => {
          // 先缩小
          animateTo({ duration: 100, curve: Curve.EaseIn }, () => {
            this.scaleValue = 0.85
          })
          // 再弹回，使用弹簧曲线
          setTimeout(() => {
            animateTo({
              duration: 400,
              curve: curves.springMotion(0.6, 0.9)
            }, () => {
              this.scaleValue = 1
            })
          }, 100)
        })
    }
    .width('100%')
    .height('100%')
    .justifyContent(FlexAlign.Center)
  }
}
```

## 2. 卡片展开/收起动画

```typescript
// 卡片点击后展开显示详情，再次点击收起
@ComponentV2
struct ExpandableCard {
  @Local isExpanded: boolean = false
  @Local cardHeight: number = 80

  build() {
    Column() {
      Column() {
        Row() {
          Text('订单详情')
            .fontSize(18)
            .fontWeight(FontWeight.Bold)
          Blank()
          Image($r('sys.media.ohos_ic_public_arrow_down'))
            .width(20)
            .height(20)
            .rotate({ angle: this.isExpanded ? 180 : 0 })
        }
        .width('100%')
        .padding(16)

        if (this.isExpanded) {
          Column({ space: 8 }) {
            Text('商品：ArkTS开发指南').fontSize(14)
            Text('价格：¥99.00').fontSize(14)
            Text('数量：1').fontSize(14)
            Text('总计：¥99.00').fontSize(16).fontWeight(FontWeight.Bold)
          }
          .width('100%')
          .padding({ left: 16, right: 16, bottom: 16 })
          .transition(TransitionEffect.OPACITY.combine(
            TransitionEffect.translate({ y: -20 })
          ))
        }
      }
      .width('90%')
      .backgroundColor(Color.White)
      .borderRadius(12)
      .shadow({ radius: 8, color: '#1A000000', offsetY: 2 })
      .clip(true)
      .onClick(() => {
        animateTo({ duration: 300, curve: Curve.EaseInOut }, () => {
          this.isExpanded = !this.isExpanded
        })
      })
    }
    .width('100%')
    .height('100%')
    .justifyContent(FlexAlign.Center)
    .backgroundColor('#F5F5F5')
  }
}
```

## 3. 数字计数器动画（值插值）

```typescript
// 数字从当前值平滑过渡到目标值
@ComponentV2
struct AnimatedCounter {
  @Local displayValue: number = 0
  @Local targetValue: number = 0
  private timer: number = -1

  // 模拟数值插值动画
  private animateToValue(target: number): void {
    let start = this.displayValue
    let diff = target - start
    let steps = 30
    let step = 0
    if (this.timer !== -1) {
      clearInterval(this.timer)
    }
    this.timer = setInterval(() => {
      step++
      // easeOut 插值
      let progress = 1 - Math.pow(1 - step / steps, 3)
      this.displayValue = Math.round(start + diff * progress)
      if (step >= steps) {
        clearInterval(this.timer)
        this.timer = -1
        this.displayValue = target
      }
    }, 16)
  }

  build() {
    Column({ space: 30 }) {
      Text(this.displayValue.toString())
        .fontSize(60)
        .fontWeight(FontWeight.Bold)
        .fontColor('#333333')

      Row({ space: 20 }) {
        Button('+100').onClick(() => {
          this.targetValue += 100
          this.animateToValue(this.targetValue)
        })
        Button('+1000').onClick(() => {
          this.targetValue += 1000
          this.animateToValue(this.targetValue)
        })
        Button('重置').backgroundColor(Color.Gray).onClick(() => {
          this.targetValue = 0
          this.animateToValue(0)
        })
      }
    }
    .width('100%').height('100%').justifyContent(FlexAlign.Center)
  }
}
```

## 4. 交错列表项入场动画

```typescript
// 列表项依次延迟入场，产生交错动画效果
@ComponentV2
struct StaggeredList {
  @Local items: number[] = []
  @Local itemOpacities: number[] = []
  @Local itemTranslateY: number[] = []
  private allItems: number[] = [1, 2, 3, 4, 5, 6, 7, 8]

  aboutToAppear(): void {
    // 初始化所有项为不可见状态
    this.allItems.forEach(() => {
      this.itemOpacities.push(0)
      this.itemTranslateY.push(40)
    })
    this.items = this.allItems

    // 交错入场动画：每项延迟 80ms
    this.allItems.forEach((_, index) => {
      setTimeout(() => {
        animateTo({
          duration: 400,
          curve: curves.springMotion(0.6, 1.0)
        }, () => {
          this.itemOpacities[index] = 1
          this.itemTranslateY[index] = 0
        })
      }, index * 80)
    })
  }

  build() {
    Column() {
      ForEach(this.items, (item: number, index: number) => {
        Row() {
          Text(`列表项 ${item}`).fontSize(16)
        }
        .width('90%').height(60)
        .backgroundColor(Color.White).borderRadius(8)
        .padding({ left: 16 })
        .shadow({ radius: 4, color: '#0D000000', offsetY: 1 })
        .opacity(index < this.itemOpacities.length ? this.itemOpacities[index] : 0)
        .translate({ y: index < this.itemTranslateY.length ? this.itemTranslateY[index] : 40 })
        .margin({ bottom: 8 })
      }, (item: number) => item.toString())
    }
    .width('100%').height('100%').padding({ top: 20 }).backgroundColor('#F5F5F5')
  }
}
```

## 5. 颜色过渡动画

```typescript
// 点击按钮在多种颜色之间平滑过渡
@ComponentV2
struct ColorTransition {
  @Local bgColor: ResourceColor = '#FF6B6B'
  @Local colorIndex: number = 0
  private colors: string[] = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD']

  build() {
    Column({ space: 30 }) {
      Column()
        .width(200).height(200).borderRadius(100)
        .backgroundColor(this.bgColor)
        .shadow({ radius: 20, color: '#33000000' })

      Text('当前颜色').fontSize(16).fontColor('#666666')

      Button('切换颜色')
        .fontSize(16)
        .onClick(() => {
          this.colorIndex = (this.colorIndex + 1) % this.colors.length
          animateTo({ duration: 600, curve: Curve.EaseInOut }, () => {
            this.bgColor = this.colors[this.colorIndex]
          })
        })
    }
    .width('100%').height('100%').justifyContent(FlexAlign.Center).backgroundColor('#FFFFFF')
  }
}
```

## 6. 多属性同时动画（位移 + 缩放 + 透明度）

```typescript
// 同时对位移、缩放、透明度做动画
@ComponentV2
struct MultiPropertyAnimation {
  @Local translateX: number = -150
  @Local scaleVal: number = 0.3
  @Local opacityVal: number = 0
  @Local isShown: boolean = false

  build() {
    Column({ space: 40 }) {
      // 动画目标元素
      Text('Hello ArkTS')
        .fontSize(28).fontWeight(FontWeight.Bold)
        .fontColor(Color.White).padding(20)
        .backgroundColor('#667EEA').borderRadius(16)
        .translate({ x: this.translateX })
        .scale({ x: this.scaleVal, y: this.scaleVal })
        .opacity(this.opacityVal)

      Button(this.isShown ? '隐藏' : '显示')
        .fontSize(16)
        .onClick(() => {
          this.isShown = !this.isShown
          animateTo({ duration: 500, curve: curves.springMotion(0.4, 0.8) }, () => {
            if (this.isShown) {
              this.translateX = 0
              this.scaleVal = 1
              this.opacityVal = 1
            } else {
              this.translateX = -150
              this.scaleVal = 0.3
              this.opacityVal = 0
            }
          })
        })
    }
    .width('100%').height('100%').justifyContent(FlexAlign.Center)
  }
}
```

## 7. 串行动画（链式 animateTo）

```typescript
// 多步动画依次执行：先移动 -> 再旋转 -> 再缩放 -> 最后恢复
@ComponentV2
struct SequentialAnimation {
  @Local translateX: number = 0
  @Local rotateAngle: number = 0
  @Local scaleVal: number = 1
  @Local bgColor: ResourceColor = '#667EEA'

  // 执行串行动画序列
  private runSequence(): void {
    // 第 1 步：向右移动
    animateTo({ duration: 300, curve: Curve.EaseOut, onFinish: () => {
      // 第 2 步：旋转
      animateTo({ duration: 300, curve: Curve.EaseInOut, onFinish: () => {
        // 第 3 步：缩放 + 变色
        animateTo({ duration: 300, curve: Curve.EaseInOut, onFinish: () => {
          // 第 4 步：恢复初始状态
          animateTo({
            duration: 500,
            curve: curves.springMotion(0.5, 0.9)
          }, () => {
            this.translateX = 0
            this.rotateAngle = 0
            this.scaleVal = 1
            this.bgColor = '#667EEA'
          })
        }}, () => {
          this.scaleVal = 1.5
          this.bgColor = '#FF6B6B'
        })
      }}, () => {
        this.rotateAngle = 360
      })
    }}, () => {
      this.translateX = 100
    })
  }

  build() {
    Column({ space: 60 }) {
      Column()
        .width(80).height(80).borderRadius(16)
        .backgroundColor(this.bgColor)
        .translate({ x: this.translateX })
        .rotate({ angle: this.rotateAngle })
        .scale({ x: this.scaleVal, y: this.scaleVal })

      Button('播放序列动画').fontSize(16).onClick(() => { this.runSequence() })
    }
    .width('100%').height('100%').justifyContent(FlexAlign.Center)
  }
}
```

## 8. 弹簧动画（不同参数对比）

```typescript
// 展示不同弹簧参数的动画效果
@ComponentV2
struct SpringAnimationDemo {
  @Local positions: number[] = [0, 0, 0, 0]
  private isRight: boolean = false

  build() {
    Column({ space: 20 }) {
      Text('弹簧动画参数对比')
        .fontSize(20).fontWeight(FontWeight.Bold).margin({ bottom: 20 })

      // 欠阻尼弹簧：弹性大，多次振荡
      this.SpringRow('欠阻尼 (0.3, 0.6)', 0)
      // 临界阻尼：快速到位，无振荡
      this.SpringRow('临界阻尼 (0.8, 1.0)', 1)
      // 过阻尼：缓慢到位
      this.SpringRow('过阻尼 (0.3, 1.5)', 2)
      // 高刚度快速弹簧
      this.SpringRow('高刚度 (0.9, 0.8)', 3)

      Button('触发动画').fontSize(16).margin({ top: 40 })
        .onClick(() => {
          let target = this.isRight ? 0 : 150
          this.isRight = !this.isRight

          // 欠阻尼
          animateTo({ duration: 1000, curve: curves.springMotion(0.3, 0.6) },
            () => { this.positions[0] = target })
          // 临界阻尼
          animateTo({ duration: 1000, curve: curves.springMotion(0.8, 1.0) },
            () => { this.positions[1] = target })
          // 过阻尼
          animateTo({ duration: 1000, curve: curves.springMotion(0.3, 1.5) },
            () => { this.positions[2] = target })
          // 高刚度
          animateTo({ duration: 1000, curve: curves.springMotion(0.9, 0.8) },
            () => { this.positions[3] = target })
        })
    }
    .width('100%').height('100%').justifyContent(FlexAlign.Center).padding(20)
  }

  @Builder
  SpringRow(label: string, index: number) {
    Column({ space: 4 }) {
      Text(label).fontSize(12).fontColor('#999999')
      Row() {
        Column()
          .width(40).height(40).borderRadius(20)
          .backgroundColor('#667EEA')
          .translate({ x: this.positions[index] })
      }
      .width('100%').height(50).padding({ left: 20 }).alignItems(VerticalAlign.Center)
    }
  }
}
```

---

## 9. 把动画值放进 @ObservedV2 类（多组件复用）

```typescript
// 多个动画卡片共享同一份 ScaleModel，避免每个组件重复声明 @Local
@ObservedV2
class ScaleModel {
  @Trace value: number = 1
}

@ComponentV2
struct ScaleCard {
  @Param model: ScaleModel = new ScaleModel()
  @Param @Once label: string = ''

  build() {
    Column() {
      Text(this.label).fontSize(14)
      Column()
        .width(80).height(80).borderRadius(16)
        .backgroundColor('#667EEA')
        .scale({ x: this.model.value, y: this.model.value })
    }
    .padding(16)
    .onClick(() => {
      animateTo({ duration: 300, curve: curves.springMotion(0.5, 0.8) }, () => {
        this.model.value = this.model.value === 1 ? 1.5 : 1  // @Trace 触发自身 + 父 + 兄弟刷新
      })
    })
  }
}

@ComponentV2
struct ScaleGallery {
  @Local left: ScaleModel = new ScaleModel()
  @Local right: ScaleModel = new ScaleModel()

  build() {
    Row({ space: 16 }) {
      ScaleCard({ model: this.left, label: '左侧' })
      ScaleCard({ model: this.right, label: '右侧' })
    }
  }
}
```

---

## 10. 父子双向动画（@Param + @Event 替代 V1 @Link）

```typescript
// 子组件控制 angle，但真值由父持有 — 用 @Param 接 + @Event 回传
@ComponentV2
struct RotateKnob {
  @Param angle: number = 0
  @Event onAngleChange: (v: number) => void = () => {}

  build() {
    Column() {
      Image($r('app.media.knob'))
        .width(80).height(80)
        .rotate({ angle: this.angle })
      Button('+30').onClick(() => {
        animateTo({ duration: 200, curve: Curve.EaseInOut }, () => {
          this.onAngleChange(this.angle + 30)  // 通知父组件
        })
      })
    }
  }
}

@ComponentV2
struct ParentDial {
  @Local currentAngle: number = 0

  build() {
    Column() {
      RotateKnob({
        angle: this.currentAngle,
        onAngleChange: (v: number) => { this.currentAngle = v }
      })
      Text(`当前角度: ${this.currentAngle}`)
    }
  }
}
```
