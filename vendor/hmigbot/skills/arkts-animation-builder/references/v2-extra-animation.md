# ArkTS V2 进阶动画模板（geometryTransition / 循环 / 动画状态封装 / 全局动画状态）

> 从 `arkts-animation-builder/SKILL.md` 下沉的未被其他 reference 覆盖的进阶动画模板。SKILL.md 通过 MUST-read 指针引用本文件。

## 4. geometryTransition（共享元素转场）

让同一个 id 的组件在不同位置间平滑过渡：

```typescript
@ComponentV2
struct SharedElementExample {
  @Local isExpanded: boolean = false

  build() {
    Stack() {
      if (!this.isExpanded) {
        // 缩略图
        Image($r('app.media.photo'))
          .width(100)
          .height(100)
          .borderRadius(8)
          .geometryTransition('photo_1')  // 相同 id
          .onClick(() => {
            animateTo({ duration: 500, curve: Curve.EaseInOut }, () => {
              this.isExpanded = true
            })
          })
      } else {
        // 大图
        Image($r('app.media.photo'))
          .width('100%')
          .height(300)
          .geometryTransition('photo_1')  // 相同 id
          .onClick(() => {
            animateTo({ duration: 500, curve: Curve.EaseInOut }, () => {
              this.isExpanded = false
            })
          })
      }
    }
  }
}
```

---


## 6. 循环动画

### Loading 旋转

```typescript
@ComponentV2
struct LoadingSpinner {
  @Local angle: number = 0

  aboutToAppear(): void {
    // 启动无限旋转
    animateTo({
      duration: 1000,
      curve: Curve.Linear,
      iterations: -1,        // 无限循环
      playMode: PlayMode.Normal
    }, () => {
      this.angle = 360
    })
  }

  build() {
    Image($r('app.media.loading'))
      .width(40)
      .height(40)
      .rotate({ angle: this.angle })
  }
}
```

### 呼吸灯效果

```typescript
@ComponentV2
struct BreathingLight {
  // 字段名避开内置 attribute `scale`，否则报 Property 'scale' ... not assignable to base type 'CustomComponent'
  @Local breathScale: number = 1

  aboutToAppear(): void {
    animateTo({
      duration: 1500,
      curve: Curve.EaseInOut,
      iterations: -1,
      playMode: PlayMode.Alternate  // 来回播放
    }, () => {
      this.breathScale = 1.2
    })
  }

  build() {
    Circle()
      .width(100)
      .height(100)
      .fill(Color.Blue)
      .opacity(0.6)
      .scale({ x: this.breathScale, y: this.breathScale })
  }
}
```

---

## 7. 把动画状态封装到 @ObservedV2 类（推荐用于复用）

当多个组件共享同一份动画状态（如 MiniPlayer / FullPlayer 共享 isPlaying），把状态封装到 `@ObservedV2` 类，组件用 `@Param` / `@Local` 持有：

```typescript
@ObservedV2
class PlaybackUIModel {
  @Trace isPlaying: boolean = false
  @Trace progress: number = 0          // 0..100
  @Trace isPlayerVisible: boolean = false
}

// 父：持有
@ComponentV2
struct PlayerPage {
  @Local model: PlaybackUIModel = new PlaybackUIModel()

  build() {
    Column() {
      MiniPlayer({ model: this.model })
      Button('Play / Pause').onClick(() => {
        animateTo({ duration: 200 }, () => {
          this.model.isPlaying = !this.model.isPlaying  // @Trace 触发刷新
        })
      })
    }
  }
}

// 子：直接 @Param 传 @ObservedV2 实例（V2 不再用 @ObjectLink）
@ComponentV2
struct MiniPlayer {
  @Param model: PlaybackUIModel = new PlaybackUIModel()

  build() {
    SymbolGlyph(this.model.isPlaying ? $r('sys.symbol.pause_fill') : $r('sys.symbol.play_fill'))
      .fontSize(20)
  }
}
```

> 全局共享场景（多页面同一份）见 §8 `AppStorageV2.connect`。

---

## 8. 全局动画状态（替代 V1 @StorageLink）

V2 用 `AppStorageV2.connect()` + `@ObservedV2` 类替代 V1 的 `@StorageLink`：

```typescript
import { AppStorageV2 } from '@kit.ArkUI';   // AppStorageV2 是真实模块导出，必须 import

@ObservedV2
class PlaybackModel {
  @Trace isPlaying: boolean = false
  @Trace currentEpisodeId: string = ''
}

// 任意组件中使用
@ComponentV2
struct MiniPlayerGlobal {
  @Local playback: PlaybackModel = AppStorageV2.connect(
    PlaybackModel,
    'playback',
    () => new PlaybackModel()
  )!

  build() {
    SymbolGlyph(this.playback.isPlaying ? $r('sys.symbol.pause_fill') : $r('sys.symbol.play_fill'))
      .fontSize(20)
      .onClick(() => {
        animateTo({ duration: 150 }, () => {
          this.playback.isPlaying = !this.playback.isPlaying
        })
        // 自动同步到所有 connect 同一 key 的组件
      })
  }
}
```

---
