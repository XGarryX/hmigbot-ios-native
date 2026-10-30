# WebView 字体与样式设置

本文档涵盖通过 WebView 控制页面视觉样式的通用模式：字体缩放、字体族、粗体、颜色覆盖、反转颜色，以及样式持久化。

> 代码示例使用 ArkTS V2 装饰器（`@ComponentV2 / @Local / @Param + @Once / AppStorageV2`，API 12+ 推荐）。V1 老项目把 `@Local → @State`、`@Param @Once → @Prop`、`AppStorageV2.connect → AppStorage.setOrCreate/get` 即可。

## 1. 状态变量模式

```typescript
@Local private currentFontSize: number = 100;     // textZoomRatio 百分比
@Local private currentFontType: string = '0';      // 字体族 ID（'0'=默认）
@Local private isFontBold: boolean = false;         // 粗体
@Local private isWhiteBg: boolean = false;          // 白色背景
@Local private isBlackText: boolean = false;        // 黑色文本
private isInvertColors: boolean = false;            // 反转颜色（非 @Local — 不直接驱动 UI 时可省去）
```

## 2. 字体缩放（textZoomRatio）

最简单的方式 — 通过 Web 组件的声明式属性直接绑定 `@Local`：

```typescript
Web({ src: this.url, controller: this.webController })
  .textZoomRatio(this.currentFontSize)    // 100 = 正常, 150 = 放大 50%
```

修改 `this.currentFontSize` 即可自动生效，无需手动注入 CSS。

### 持久化（V2：PersistenceV2 + @ObservedV2）

```typescript
// 1. 定义可观察设置类
@ObservedV2
class WebFontSettings {
  @Trace fontSize: number = 100;
  @Trace fontType: string = '0';
}

// 2. 在组件中 connect 持久化实例（应用重启后值仍保留）
@ComponentV2
struct BrowserPage {
  @Local fontSettings: WebFontSettings = PersistenceV2.globalConnect({
    type: WebFontSettings,
    key: 'web_font_settings',
    defaultCreator: () => new WebFontSettings()
  })!

  // 直接修改 @Trace 属性即自动落盘 + UI 刷新
  setFontSize(v: number): void { this.fontSettings.fontSize = v; }
}
```

> 老 V1 写法（参考）：`AppStorage.setOrCreate<number>('webFontSize', fontSize)` + `AppStorage.get<number>('webFontSize')`，V2 用 `PersistenceV2.globalConnect` 一站式取代"内存存储 + 持久化"双层模式。

## 3. 字体族切换

通过 CSS 注入实现。默认字体时移除注入的样式并刷新，恢复页面原始字体。

```typescript
private applyFontType(fontTypeId: string): void {
  this.currentFontType = fontTypeId;
  this.fontSettings.fontType = fontTypeId;  // V2: PersistenceV2 自动落盘

  if (fontTypeId === '0') {
    // 默认字体：移除样式 + 刷新
    this.runJs(`(function(){var el=document.getElementById('myapp_font_style');if(el)el.remove();})()`);
    this.webController.refresh();
  } else {
    const css = getFontCss(fontTypeId);  // 根据 ID 返回 font-family CSS
    if (css.length > 0) {
      this.injectCssString(css, 'myapp_font_style');
    }
  }
}
```

## 4. 可逆 Toggle 模式（粗体为例）

开启时注入 CSS，关闭时移除对应 style 元素。这是最常用的样式 toggle 模式：

```typescript
toggleFontBold(): void {
  this.isFontBold = !this.isFontBold;
  if (this.isFontBold) {
    this.injectCssString('*{font-weight:bold!important}', 'myapp_bold_style');
  } else {
    this.runJs(`(function(){var el=document.getElementById('myapp_bold_style');if(el)el.remove();})()`);
  }
}
```

## 5. 幂等 Toggle 模式（黑色文本为例）

只能开启、不能关闭（或关闭需刷新页面）。重复点击时提示用户已开启。

```typescript
toggleBlackText(): void {
  if (this.isBlackText) {
    promptAction.showToast({ message: '已是黑色文本', duration: 1500 });
    return;
  }
  this.isBlackText = true;
  this.injectCssString('*{color:#000000!important}', 'myapp_blacktext_style');
}
```

白色背景同理，覆盖常见容器元素：
```typescript
const css = 'html,body,div,section,article,main,aside,header,footer,nav' +
  '{background-color:#FFFFFF!important;background-image:none!important}';
this.injectCssString(css, 'myapp_whitebg_style');
```

## 6. 互斥样式（反转颜色为例）

反转颜色开启时自动关闭冲突的黑色文本和白色背景：

```typescript
toggleInvertColors(): void {
  this.isInvertColors = !this.isInvertColors;
  if (this.isInvertColors) {
    const css = 'html,body,div,section,article,main,aside,header,footer,nav,' +
      'p,span,li,td,th,dd,dt,h1,h2,h3,h4,h5,h6,a,label,input,textarea,select,button' +
      '{color:#FFFFFF!important;background-color:#000000!important}' +
      'img,video,canvas,svg{filter:none!important}';
    this.injectCssString(css, 'myapp_invert_style');

    // 清除冲突样式
    this.isBlackText = false;
    this.isWhiteBg = false;
    this.runJs(`(function(){
      var a=document.getElementById('myapp_blacktext_style');if(a)a.remove();
      var b=document.getElementById('myapp_whitebg_style');if(b)b.remove();
    })()`);
  } else {
    this.runJs(`(function(){var el=document.getElementById('myapp_invert_style');if(el)el.remove();})()`);
  }
}
```

## 7. 样式持久化（reapplyStyles）

WebView 页面导航后，注入的 `<style>` 元素会丢失。在 `onPageEnd` 中统一重新注入所有已开启的样式：

```typescript
private reapplyStyles(): void {
  if (this.currentFontType !== '0') {
    this.applyFontType(this.currentFontType);
  }
  if (this.isFontBold) {
    this.injectCssString('*{font-weight:bold!important}', 'myapp_bold_style');
  }
  if (this.isBlackText) {
    this.injectCssString('*{color:#000000!important}', 'myapp_blacktext_style');
  }
  if (this.isWhiteBg) {
    // 注入白色背景 CSS...
  }
  if (this.isInvertColors) {
    // 注入反转颜色 CSS...
  }
}
```

> 阅读模式和竖排文本不在 `reapplyStyles` 中恢复 — 它们替换了页面 DOM，新页面无法恢复之前的解析结果。

## 8. 动态图标状态

按钮根据样式开关状态显示不同图标，通过 `@Param @Once` 传递只读状态到子组件（V1 等价：`@Prop`）：

```typescript
@ComponentV2
struct StyleToggleIcon {
  @Param @Once isFontBoldOn: boolean = false;

  getIconResource(): Resource {
    return this.isFontBoldOn
      ? $r('app.media.ic_bold_active')
      : $r('app.media.ic_bold');
  }

  build() {
    Image(this.getIconResource())
  }
}
```

## 9. 样式优先级与冲突规则

| 操作 | 副作用 |
|------|--------|
| 开启反转颜色 | 自动关闭黑色文本 + 白色背景 |
| 关闭反转颜色 | 不恢复黑色文本/白色背景 |
| 页面导航 | 所有 CSS 样式通过 `reapplyStyles` 恢复；阅读/竖排模式重置 |

设计新样式时，先确认它是否与现有样式冲突，必要时在 toggle 函数中处理互斥关系。
