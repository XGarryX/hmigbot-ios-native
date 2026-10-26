# Android-to-HarmonyOS UI Atomic Component Mapping Reference

<!-- TODO: Fill in the actual UI atomic component mapping content -->
<!-- This reference maps Android UI widgets/views to HarmonyOS ArkUI atomic component equivalents -->
<!-- Covers: TextView→Text, EditText→TextInput, Button→Button, ImageView→Image, CheckBox→Checkbox, Switch→Toggle, ProgressBar→Progress, etc. -->


## 一、基础视图组件映射

### 1.1 文本类组件

| Android 组件 | 类名 | HarmonyOS 组件 | 替代方案 | 说明 |
|-------------|------|---------------|---------|------|
| TextView | `android.widget.TextView` | `Text` | 直接映射 | 文本显示，支持富文本、样式设置 |
| EditText | `android.widget.EditText` | `TextInput` / `TextArea` | 单行用 TextInput，多行用 TextArea | 文本输入框 |
| AutoCompleteTextView | `android.widget.AutoCompleteTextView` | `Search` / `Select` | 组合实现 | 自动完成文本输入 |
| MultiAutoCompleteTextView | `android.widget.MultiAutoCompleteTextView` | 自定义组合 | Select + 标签显示 | 多段自动完成文本输入 |
| CheckedTextView | `android.widget.CheckedTextView` | `Row` + `Checkbox` + `Text` | 组合实现 | 带选中状态的文本视图 |
| TextSwitcher | `android.widget.TextSwitcher` | `Swiper` | 配合文本内容 | 文本切换动画容器 |
| ExtractEditText | `android.widget.ExtractEditText` | `TextArea` | 临时编辑场景 | 输入法提取编辑框 |
| Chronometer | `android.widget.Chronometer` | `Text` + 定时器 | 自定义实现 | 计时器显示 |

---

#### 1.1.1 TextView → Text 属性映射

**文本内容属性**

| Android XML | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `android:text` | 构造函数参数 | String | Android: `android:text="Hello"`<br/>HarmonyOS: `Text('Hello')` |
| `android:hint` | `.placeholder()` | String | Android: `android:hint="Enter text"`<br/>HarmonyOS: `Text('').placeholder('Enter text')` |
| `android:textColor` | `.fontColor()` | Color → ResourceColor | Android: `android:textColor="#FF0000"`<br/>HarmonyOS: `Text('Hello').fontColor('#FF0000')` |
| `android:textColorHint` | `.placeholderColor()` | Color → ResourceColor | Android: `android:textColorHint="#AAAAAA"`<br/>HarmonyOS: `Text('').placeholderColor('#AAAAAA')` |
| `android:textColorHighlight` | `.selectionBackgroundColor()` | Color → ResourceColor | Android: `android:textColorHighlight="#FFFF00"`<br/>HarmonyOS: `Text('Hello').selectionBackgroundColor('#FFFF00')` |
| `android:textColorLink` | 无直接对应 | 需自定义实现 | 使用 SpanString 设置链接颜色 |

**文本尺寸属性**

| Android XML | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `android:textSize` | `.fontSize()` | sp → fp | Android: `android:textSize="16sp"`<br/>HarmonyOS: `Text('Hello').fontSize(16)` |
| `android:textScaleX` | `.letterSpacing()` | float (不同行为) | Android: `android:textScaleX="1.2"`<br/>HarmonyOS: `Text('Hello').letterSpacing(0.2)` |
| `android:lineSpacingExtra` | `.lineHeight()` | dp → vp | Android: `android:lineSpacingExtra="8dp"`<br/>HarmonyOS: `Text('Hello').lineHeight({ extra: 8 })` |
| `android:lineSpacingMultiplier` | `.lineHeight()` | float (需转换) | Android: `android:lineSpacingMultiplier="1.5"`<br/>HarmonyOS: `Text('Hello').lineHeight({ multiplier: 1.5 })` |
| `android:letterSpacing` | `.letterSpacing()` | float | Android: `android:letterSpacing="0.1"`<br/>HarmonyOS: `Text('Hello').letterSpacing(0.1)` |
| `android:ems` | 无直接对应 | 需计算宽度 | 使用 `.width()` 根据字符数计算 |
| `android:maxEms` | `.constraintSize()` | 需计算宽度 | Android: `android:maxEms="10"`<br/>HarmonyOS: `Text('Hello').constraintSize({ maxWidth: 200 })` |
| `android:minEms` | `.constraintSize()` | 需计算宽度 | Android: `android:minEms="5"`<br/>HarmonyOS: `Text('Hello').constraintSize({ minWidth: 100 })` |

**文本样式属性**

| Android XML | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `android:textStyle` | `.fontWeight()` / `.fontStyle()` | enum → enum | Android: `android:textStyle="bold"`<br/>HarmonyOS: `Text('Hello').fontWeight(FontWeight.Bold)` |
| `android:fontFamily` | `.fontFamily()` | String → String | Android: `android:fontFamily="sans-serif"`<br/>HarmonyOS: `Text('Hello').fontFamily('sans-serif')` |
| `android:textAllCaps` | `.textCase()` 或手动转换 | boolean → TextCase | Android: `android:textAllCaps="true"`<br/>HarmonyOS: `Text('hello').textCase(TextCase.Upper)` |
| `android:textLocale` | 无直接对应 | 需设置语言环境 | 使用系统语言环境 |
| `android:fontFeatureSettings` | 无直接对应 | 需自定义实现 | 使用字体特性 API |
| `android:fontVariationSettings` | 无直接对应 | 需自定义实现 | 使用字体变体 API |
| `android:textFontWeight` | `.fontWeight()` | int → FontWeight | Android: `android:textFontWeight="700"`<br/>HarmonyOS: `Text('Hello').fontWeight(FontWeight.Bold)` |
| `android:lineHeight` | `.lineHeight()` | dp → vp | Android: `android:lineHeight="24dp"`<br/>HarmonyOS: `Text('Hello').lineHeight(24)` |

**文本对齐属性**

| Android XML | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `android:gravity` | `.textAlign()` | Gravity → TextAlign | Android: `android:gravity="center"`<br/>HarmonyOS: `Text('Hello').textAlign(TextAlign.Center)` |
| `android:textAlignment` | `.textAlign()` | TextAlignment → TextAlign | Android: `android:textAlignment="center"`<br/>HarmonyOS: `Text('Hello').textAlign(TextAlign.Center)` |
| `android:textDirection` | 无直接对应 | 需设置布局方向 | 使用 `.direction()` |
| `android:justificationMode` | 无直接对应 | 需自定义实现 | 使用文本对齐 API |

**文本显示与省略属性**

| Android XML | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `android:maxLines` | `.maxLines()` | int → int | Android: `android:maxLines="2"`<br/>HarmonyOS: `Text('Hello').maxLines(2)` |
| `android:minLines` | 无直接对应 | 需自定义实现 | 使用高度约束 |
| `android:lines` | 无直接对应 | 需自定义实现 | 使用高度约束 |
| `android:singleLine` | 使用 TextInput | boolean → 组件选择 | Android: `android:singleLine="true"`<br/>HarmonyOS: 使用 TextInput 而非 TextArea |
| `android:ellipsize` | `.textOverflow()` | TruncateAt → TextOverflow | Android: `android:ellipsize="end"`<br/>HarmonyOS: `Text('Hello').textOverflow({ overflow: TextOverflow.Ellipsis })` |
| `android:marqueeRepeatLimit` | `.textOverflow()` | int → Marquee | Android: `android:marqueeRepeatLimit="3"`<br/>HarmonyOS: `Text('Hello').textOverflow({ overflow: TextOverflow.Marquee })` |

**文本选择属性**

| Android XML | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `android:textIsSelectable` | `.copyOption()` | boolean → CopyOptions | Android: `android:textIsSelectable="true"`<br/>HarmonyOS: `Text('Hello').copyOption(CopyOptions.InApp)` |
| `android:selectable` | `.copyOption()` | boolean → CopyOptions | Android: `android:selectable="true"`<br/>HarmonyOS: `Text('Hello').copyOption(CopyOptions.InApp)` |
| `android:selectAllOnFocus` | `.selectAll()` | boolean → 方法调用 | Android: `android:selectAllOnFocus="true"`<br/>HarmonyOS: `TextInput().onFocus(() => { textInput.selectAll() })` |

**文本外观属性**

| Android XML | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `android:textAppearance` | @Styles | @style → @Styles | Android: `android:textAppearance="@style/TextAppearance"`<br/>HarmonyOS: 使用 `@Styles` 装饰器 |
| `android:shadowColor` | `.shadow()` | Color → shadow | Android: `android:shadowColor="#80000000"`<br/>HarmonyOS: `Text('Hello').shadow({ color: '#80000000', radius: 4 })` |
| `android:shadowDx` | `.shadow()` | float → shadow.offsetX | Android: `android:shadowDx="2"`<br/>HarmonyOS: `Text('Hello').shadow({ offsetX: 2, offsetY: 2, radius: 4 })` |
| `android:shadowDy` | `.shadow()` | float → shadow.offsetY | Android: `android:shadowDy="2"`<br/>HarmonyOS: `Text('Hello').shadow({ offsetX: 2, offsetY: 2, radius: 4 })` |
| `android:shadowRadius` | `.shadow()` | float → shadow.radius | Android: `android:shadowRadius="4"`<br/>HarmonyOS: `Text('Hello').shadow({ radius: 4 })` |
| `android:elegantTextHeight` | 无直接对应 | 需自定义实现 | 使用字体渲染 API |
| `android:fallbackLineSpacing` | 无直接对应 | 需自定义实现 | 使用行高设置 |

**文本链接属性**

| Android XML | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `android:autoLink` | 无直接对应 | 需自定义实现 | 使用 SpanString 或正则表达式 |
| `android:linksClickable` | 无直接对应 | 需自定义实现 | 使用 SpanString 设置点击事件 |
| `android:includeFontPadding` | 无直接对应 | 需自定义实现 | 使用行高调整 |

---

#### 1.1.2 EditText → TextInput/TextArea 属性映射

**输入类型属性**

| Android XML | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `android:inputType` | `.type()` | InputType → InputType | Android: `android:inputType="text"`<br/>HarmonyOS: `TextInput().type(InputType.Normal)` |
| `android:inputType="textPassword"` | `.type()` | password → Password | Android: `android:inputType="textPassword"`<br/>HarmonyOS: `TextInput().type(InputType.Password)` |
| `android:inputType="number"` | `.type()` | number → Number | Android: `android:inputType="number"`<br/>HarmonyOS: `TextInput().type(InputType.Number)` |
| `android:inputType="phone"` | `.type()` | phone → PhoneNumber | Android: `android:inputType="phone"`<br/>HarmonyOS: `TextInput().type(InputType.PhoneNumber)` |
| `android:inputType="email"` | `.type()` | email → Email | Android: `android:inputType="textEmailAddress"`<br/>HarmonyOS: `TextInput().type(InputType.Email)` |
| `android:inputType="textMultiLine"` | 使用 TextArea | multiLine → TextArea | Android: `android:inputType="textMultiLine"`<br/>HarmonyOS: 使用 TextArea 组件 |
| `android:maxLength` | `.maxLength()` | int → int | Android: `android:maxLength="100"`<br/>HarmonyOS: `TextInput().maxLength(100)` |
| `android:password` | `.type()` | boolean → InputType | Android: `android:password="true"`<br/>HarmonyOS: `TextInput().type(InputType.Password)` |
| `android:phoneNumber` | `.type()` | boolean → InputType | Android: `android:phoneNumber="true"`<br/>HarmonyOS: `TextInput().type(InputType.PhoneNumber)` |
| `android:numeric` | `.type()` | enum → InputType | Android: `android:numeric="integer"`<br/>HarmonyOS: `TextInput().type(InputType.Number)` |
| `android:digits` | 无直接对应 | 需自定义实现 | 使用输入过滤器 |
| `android:capitalize` | 无直接对应 | 需自定义实现 | 使用文本转换 |
| `android:autoText` | 无直接对应 | 需自定义实现 | 使用输入法设置 |
| `android:editable` | `.enabled()` | boolean → boolean | Android: `android:editable="false"`<br/>HarmonyOS: `TextInput().enabled(false)` |
| `android:cursorVisible` | 无直接对应 | 需自定义实现 | 使用光标 API |

**IME 选项属性**

| Android XML | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `android:imeOptions` | `.enterKeyType()` | ImeOptions → EnterKeyType | Android: `android:imeOptions="actionDone"`<br/>HarmonyOS: `TextInput().enterKeyType(EnterKeyType.Done)` |
| `android:imeOptions="actionNext"` | `.enterKeyType()` | actionNext → Next | Android: `android:imeOptions="actionNext"`<br/>HarmonyOS: `TextInput().enterKeyType(EnterKeyType.Next)` |
| `android:imeOptions="actionSearch"` | `.enterKeyType()` | actionSearch → Search | Android: `android:imeOptions="actionSearch"`<br/>HarmonyOS: `TextInput().enterKeyType(EnterKeyType.Search)` |
| `android:imeOptions="actionSend"` | `.enterKeyType()` | actionSend → Send | Android: `android:imeOptions="actionSend"`<br/>HarmonyOS: `TextInput().enterKeyType(EnterKeyType.Send)` |
| `android:imeActionLabel` | 无直接对应 | 需自定义实现 | 使用键盘类型设置 |
| `android:imeActionId` | 无直接对应 | 需自定义实现 | 使用键盘类型设置 |

**输入提示属性**

| Android XML | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `android:hint` | `.placeholder()` | String → String | Android: `android:hint="Enter name"`<br/>HarmonyOS: `TextInput().placeholder('Enter name')` |
| `android:textColorHint` | `.placeholderColor()` | Color → ResourceColor | Android: `android:textColorHint="#AAAAAA"`<br/>HarmonyOS: `TextInput().placeholderColor('#AAAAAA')` |

---

#### 1.1.3 其他文本组件属性映射

**AutoCompleteTextView → Search/Select**

| Android XML | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|--------|
| `android:completionThreshold` | Search 组件内置 | int → 自动触发 | Android: `android:completionThreshold="1"`<br/>HarmonyOS: Search 组件自动触发 |
| `android:dropDownHeight` | 无直接对应 | 需自定义实现 | 使用 Popup 或 Select |
| `android:dropDownWidth` | 无直接对应 | 需自定义实现 | 使用 Popup 或 Select |
| `android:dropDownHorizontalOffset` | 无直接对应 | 需自定义实现 | 使用 Popup 或 Select |
| `android:dropDownVerticalOffset` | 无直接对应 | 需自定义实现 | 使用 Popup 或 Select |

**Chronometer → Text + 定时器**

| Android XML | HarmonyOS 实现 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `android:format` | 使用 setInterval | String → 格式化 | Android: `android:format="%s"`<br/>HarmonyOS: 使用 `setInterval` 更新 Text |
| `android:countDown` | 自定义逻辑 | boolean → 计数方向 | Android: `android:countDown="true"`<br/>HarmonyOS: 自定义计数逻辑 |
| `android:base` | 使用 Date | long → Date | Android: `android:base="1000"`<br/>HarmonyOS: 使用 Date 对象 |

---

#### 1.1.4 文本组件通用布局属性映射

**尺寸属性**

| Android XML | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `android:layout_width` | `.width()` | dp → vp / match_parent → '100%' | Android: `android:layout_width="100dp"`<br/>HarmonyOS: `Text('Hello').width(100)` |
| `android:layout_width="match_parent"` | `.width()` | match_parent → '100%' | Android: `android:layout_width="match_parent"`<br/>HarmonyOS: `Text('Hello').width('100%')` |
| `android:layout_width="wrap_content"` | 无需设置 | wrap_content → 自适应 | Android: `android:layout_width="wrap_content"`<br/>HarmonyOS: 无需设置，自动适应 |
| `android:layout_height` | `.height()` | dp → vp / match_parent → '100%' | Android: `android:layout_height="50dp"`<br/>HarmonyOS: `Text('Hello').height(50)` |
| `android:minWidth` | `.constraintSize()` | dp → vp | Android: `android:minWidth="100dp"`<br/>HarmonyOS: `Text('Hello').constraintSize({ minWidth: 100 })` |
| `android:maxWidth` | `.constraintSize()` | dp → vp | Android: `android:maxWidth="200dp"`<br/>HarmonyOS: `Text('Hello').constraintSize({ maxWidth: 200 })` |
| `android:minHeight` | `.constraintSize()` | dp → vp | Android: `android:minHeight="30dp"`<br/>HarmonyOS: `Text('Hello').constraintSize({ minHeight: 30 })` |
| `android:maxHeight` | `.constraintSize()` | dp → vp | Android: `android:maxHeight="100dp"`<br/>HarmonyOS: `Text('Hello').constraintSize({ maxHeight: 100 })` |

**边距与内边距属性**

| Android XML | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `android:layout_margin` | `.margin()` | dp → vp | Android: `android:layout_margin="10dp"`<br/>HarmonyOS: `Text('Hello').margin(10)` |
| `android:layout_marginTop` | `.margin({ top })` | dp → vp | Android: `android:layout_marginTop="10dp"`<br/>HarmonyOS: `Text('Hello').margin({ top: 10 })` |
| `android:layout_marginBottom` | `.margin({ bottom })` | dp → vp | Android: `android:layout_marginBottom="10dp"`<br/>HarmonyOS: `Text('Hello').margin({ bottom: 10 })` |
| `android:layout_marginLeft` | `.margin({ left })` | dp → vp | Android: `android:layout_marginLeft="10dp"`<br/>HarmonyOS: `Text('Hello').margin({ left: 10 })` |
| `android:layout_marginRight` | `.margin({ right })` | dp → vp | Android: `android:layout_marginRight="10dp"`<br/>HarmonyOS: `Text('Hello').margin({ right: 10 })` |
| `android:layout_marginStart` | `.margin({ start })` | dp → vp | Android: `android:layout_marginStart="10dp"`<br/>HarmonyOS: `Text('Hello').margin({ start: 10 })` |
| `android:layout_marginEnd` | `.margin({ end })` | dp → vp | Android: `android:layout_marginEnd="10dp"`<br/>HarmonyOS: `Text('Hello').margin({ end: 10 })` |
| `android:padding` | `.padding()` | dp → vp | Android: `android:padding="10dp"`<br/>HarmonyOS: `Text('Hello').padding(10)` |
| `android:paddingTop` | `.padding({ top })` | dp → vp | Android: `android:paddingTop="10dp"`<br/>HarmonyOS: `Text('Hello').padding({ top: 10 })` |
| `android:paddingBottom` | `.padding({ bottom })` | dp → vp | Android: `android:paddingBottom="10dp"`<br/>HarmonyOS: `Text('Hello').padding({ bottom: 10 })` |
| `android:paddingLeft` | `.padding({ left })` | dp → vp | Android: `android:paddingLeft="10dp"`<br/>HarmonyOS: `Text('Hello').padding({ left: 10 })` |
| `android:paddingRight` | `.padding({ right })` | dp → vp | Android: `android:paddingRight="10dp"`<br/>HarmonyOS: `Text('Hello').padding({ right: 10 })` |
| `android:paddingStart` | `.padding({ start })` | dp → vp | Android: `android:paddingStart="10dp"`<br/>HarmonyOS: `Text('Hello').padding({ start: 10 })` |
| `android:paddingEnd` | `.padding({ end })` | dp → vp | Android: `android:paddingEnd="10dp"`<br/>HarmonyOS: `Text('Hello').padding({ end: 10 })` |

**对齐与权重属性**

| Android XML | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `android:layout_gravity` | `.align()` / `.alignSelf()` | Gravity → Alignment | Android: `android:layout_gravity="center"`<br/>HarmonyOS: `Text('Hello').align(Alignment.Center)` |
| `android:layout_weight` | `.layoutWeight()` | float → number | Android: `android:layout_weight="1"`<br/>HarmonyOS: `Text('Hello').layoutWeight(1)` |

**显示属性**

| Android XML | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `android:visibility` | `.visibility()` | enum → Visibility | Android: `android:visibility="gone"`<br/>HarmonyOS: `Text('Hello').visibility(Visibility.None)` |
| `android:visibility="invisible"` | `.visibility()` | invisible → Hidden | Android: `android:visibility="invisible"`<br/>HarmonyOS: `Text('Hello').visibility(Visibility.Hidden)` |
| `android:visibility="visible"` | `.visibility()` | visible → Visible | Android: `android:visibility="visible"`<br/>HarmonyOS: `Text('Hello').visibility(Visibility.Visible)` |
| `android:alpha` | `.opacity()` | float (0-1) → number (0-1) | Android: `android:alpha="0.5"`<br/>HarmonyOS: `Text('Hello').opacity(0.5)` |
| `android:background` | `.backgroundColor()` | Color → ResourceColor | Android: `android:background="#FF0000"`<br/>HarmonyOS: `Text('Hello').backgroundColor('#FF0000')` |
| `android:background` | `.backgroundImage()` | Drawable → Resource | Android: `android:background="@drawable/bg"`<br/>HarmonyOS: `Text('Hello').backgroundImage($r('app.media.bg'))` |

**交互属性**

| Android XML | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `android:enabled` | `.enabled()` | boolean → boolean | Android: `android:enabled="false"`<br/>HarmonyOS: `Text('Hello').enabled(false)` |
| `android:clickable` | `.onClick()` | boolean → 事件回调 | Android: `android:clickable="true"`<br/>HarmonyOS: `Text('Hello').onClick(() => { ... })` |
| `android:focusable` | `.focusable()` | boolean → boolean | Android: `android:focusable="true"`<br/>HarmonyOS: `Text('Hello').focusable(true)` |
| `android:focusableInTouchMode` | 无直接对应 | 需自定义实现 | 使用焦点 API |

**变换属性**

| Android XML | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `android:rotation` | `.rotate()` | float → { angle: number } | Android: `android:rotation="90"`<br/>HarmonyOS: `Text('Hello').rotate({ angle: 90 })` |
| `android:scaleX` | `.scale()` | float → { x: number } | Android: `android:scaleX="1.5"`<br/>HarmonyOS: `Text('Hello').scale({ x: 1.5 })` |
| `android:scaleY` | `.scale()` | float → { y: number } | Android: `android:scaleY="1.5"`<br/>HarmonyOS: `Text('Hello').scale({ y: 1.5 })` |
| `android:translationX` | `.translate()` | float → { x: number } | Android: `android:translationX="100"`<br/>HarmonyOS: `Text('Hello').translate({ x: 100 })` |
| `android:translationY` | `.translate()` | float → { y: number } | Android: `android:translationY="100"`<br/>HarmonyOS: `Text('Hello').translate({ y: 100 })` |
| `android:translationZ` | 无直接对应 | 需自定义实现 | 使用层级和阴影 |
| `android:pivotX` | 无直接对应 | 需自定义实现 | 使用变换中心 API |
| `android:pivotY` | 无直接对应 | 需自定义实现 | 使用变换中心 API |

**阴影与效果属性**

| Android XML | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `android:elevation` | `.shadow()` | dp → shadow | Android: `android:elevation="8dp"`<br/>HarmonyOS: `Text('Hello').shadow({ radius: 8, color: '#30000000', offsetY: 4 })` |
| `android:outlineProvider` | 无直接对应 | 需自定义实现 | 使用裁剪 API |
| `android:clipToOutline` | `.clip()` | boolean → boolean | Android: `android:clipToOutline="true"`<br/>HarmonyOS: `Text('Hello').clip(true)` |

**无障碍属性**

| Android XML | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `android:contentDescription` | `.accessibilityText()` | String → String | Android: `android:contentDescription="Button label"`<br/>HarmonyOS: `Text('Hello').accessibilityText('Button label')` |
| `android:labelFor` | 无直接对应 | 需自定义实现 | 使用无障碍组 |
| `android:importantForAccessibility` | `.accessibilityLevel()` | enum → AccessibilityLevel | Android: `android:importantForAccessibility="yes"`<br/>HarmonyOS: `Text('Hello').accessibilityLevel('auto')` |

---

#### 1.1.5 单位换算说明

| Android 单位 | HarmonyOS 单位 | 换算关系 | 说明 |
|-------------|---------------|---------|------|
| `dp` (Density-independent Pixels) | `vp` (Virtual Pixels) | 1dp ≈ 1vp | 密度无关像素，用于布局尺寸 |
| `sp` (Scale-independent Pixels) | `fp` (Font Pixels) | 1sp ≈ 1fp | 字体像素，用于文本大小，会随系统字体缩放 |
| `px` (Pixels) | `px` (Pixels) | 1px = 1px | 物理像素，不推荐使用 |
| `dip` | `vp` | 1dip ≈ 1vp | dp 的别名 |
| `in` (Inches) | 需转换 | 1in ≈ 160vp | 英寸，1英寸 = 160dp |
| `mm` (Millimeters) | 需转换 | 1mm ≈ 6.33vp | 毫米，1毫米 = 6.33dp |
| `pt` (Points) | 需转换 | 1pt ≈ 2.12vp | 点，1点 = 2.12dp |

---

#### 1.1.6 文本组件属性映射统计

| 映射类型 | 数量 | 占比 |
|---------|------|------|
| 直接映射 | 45 | ~50% |
| 需类型转换 | 30 | ~33% |
| 需组合实现 | 10 | ~11% |
| 无直接对应 | 5 | ~6% |
| **总计** | **90** | **100%** |

**映射复杂度说明：**
- **直接映射**：属性名称和功能基本一致，仅需简单语法调整
- **需类型转换**：需要将 Android 的数据类型转换为 HarmonyOS 对应类型（如 sp→fp, dp→vp）
- **需组合实现**：需要多个 HarmonyOS 属性或组件组合才能实现 Android 单个属性的功能
- **无直接对应**：HarmonyOS 暂无对应功能，需要自定义实现或使用替代方案

### 1.2 按钮类组件

| Android 组件 | 类名 | HarmonyOS 组件 | 替代方案 | 说明 |
|-------------|------|---------------|---------|------|
| Button | `android.widget.Button` | `Button` | 直接映射 | 普通按钮 |
| ImageButton | `android.widget.ImageButton` | `Button` + `Image` | 组合实现 | 图片按钮 |
| CompoundButton | `android.widget.CompoundButton` | `Checkbox` / `Radio` / `Toggle` | 根据类型选择 | 复合按钮基类 |
| CheckBox | `android.widget.CheckBox` | `Checkbox` | 直接映射 | 复选框 |
| RadioButton | `android.widget.RadioButton` | `Radio` + `RadioContainer` | 需容器 | 单选按钮 |
| RadioGroup | `android.widget.RadioGroup` | `RadioContainer` | 直接映射 | 单选按钮组 |
| ToggleButton | `android.widget.ToggleButton` | `Toggle` (ButtonType: Button) | 直接映射 | 开关按钮（文字切换） |
| Switch | `android.widget.Switch` | `Toggle` (ButtonType: Switch) | 直接映射 | 开关控件（滑动式） |

---

#### 1.2.1 Button → Button 属性映射

**按钮内容属性**

| Android XML | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `android:text` | 构造函数参数 | String | Android: `android:text="Click Me"`<br/>HarmonyOS: `Button('Click Me')` |
| `android:textColor` | `.fontColor()` | Color → ResourceColor | Android: `android:textColor="#FFFFFF"`<br/>HarmonyOS: `Button('Click').fontColor('#FFFFFF')` |
| `android:textSize` | `.fontSize()` | sp → fp | Android: `android:textSize="16sp"`<br/>HarmonyOS: `Button('Click').fontSize(16)` |
| `android:textStyle` | `.fontWeight()` | enum → FontWeight | Android: `android:textStyle="bold"`<br/>HarmonyOS: `Button('Click').fontWeight(FontWeight.Bold)` |

**按钮类型属性**

| Android XML | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `android:background` | `.type()` + `.backgroundColor()` | Drawable → ButtonType | Android: `android:background="@drawable/bg"`<br/>HarmonyOS: `Button('Click').type(ButtonType.Normal)` |
| `android:stateListAnimator` | 无直接对应 | 需自定义实现 | 使用动画 API |
| `android:elevation` | `.shadow()` | dp → shadow | Android: `android:elevation="4dp"`<br/>HarmonyOS: `Button('Click').shadow({ radius: 4 })` |

**Material Button 特有属性**

| Android XML | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `app:cornerRadius` | 无直接对应 | 需自定义实现 | 使用 `.borderRadius()` |
| `app:icon` | 无直接对应 | 需组合实现 | 使用 `Button` + `Image` 组合 |
| `app:iconTint` | 无直接对应 | 需组合实现 | 使用 `Image` 的 `.renderMode()` |
| `app:iconGravity` | 无直接对应 | 需组合实现 | 使用 `Row` 布局调整 |
| `app:iconPadding` | 无直接对应 | 需组合实现 | 使用 `.padding()` |
| `app:iconSize` | 无直接对应 | 需组合实现 | 使用 `Image` 的 `.width()` `.height()` |
| `app:strokeColor` | `.border()` | Color → borderColor | Android: `app:strokeColor="#FF0000"`<br/>HarmonyOS: `Button('Click').border({ color: '#FF0000' })` |
| `app:strokeWidth` | `.border()` | dp → borderWidth | Android: `app:strokeWidth="2dp"`<br/>HarmonyOS: `Button('Click').border({ width: 2 })` |
| `app:rippleColor` | 无直接对应 | 需自定义实现 | 使用状态样式 |

**按钮状态属性**

| Android XML | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `android:enabled` | `.enabled()` | boolean → boolean | Android: `android:enabled="false"`<br/>HarmonyOS: `Button('Click').enabled(false)` |
| `android:clickable` | `.onClick()` | boolean → 事件回调 | Android: `android:clickable="true"`<br/>HarmonyOS: `Button('Click').onClick(() => { ... })` |
| `android:focusable` | `.focusable()` | boolean → boolean | Android: `android:focusable="true"`<br/>HarmonyOS: `Button('Click').focusable(true)` |
| `android:selected` | 无直接对应 | 需状态管理 | 使用 `@Local`（V2）/ `@State`（V1）变量 |
| `android:pressed` | 无直接对应 | 需状态管理 | 使用 `.stateEffect()` |

**按钮交互属性**

| Android XML | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `android:onClick` | `.onClick()` | 方法引用 → 回调函数 | Android: `android:onClick="onClick"`<br/>HarmonyOS: `Button('Click').onClick(() => { ... })` |
| `android:longClickable` | `.onLongPress()` | boolean → 回调函数 | Android: `android:longClickable="true"`<br/>HarmonyOS: `Button('Click').onLongPress(() => { ... })` |

---

#### 1.2.2 ImageButton → Button + Image 组合实现

**ImageButton 属性映射**

| Android XML | HarmonyOS 实现 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `android:src` | `Image` 组件 | Drawable → Resource | Android: `android:src="@drawable/icon"`<br/>HarmonyOS: `Button() { Image($r('app.media.icon')) }` |
| `android:scaleType` | `Image.objectFit()` | ScaleType → ImageFit | Android: `android:scaleType="centerCrop"`<br/>HarmonyOS: `Image($r('app.media.icon')).objectFit(ImageFit.Cover)` |
| `android:adjustViewBounds` | 无直接对应 | 需自定义实现 | 使用尺寸约束 |
| `android:tint` | `Image.renderMode()` | Color → RenderMode | Android: `android:tint="#FF0000"`<br/>HarmonyOS: `Image($r('app.media.icon')).renderMode(ImageRenderMode.Template)` |
| `android:tintMode` | 无直接对应 | 需自定义实现 | 使用渲染模式 |

**组合示例：**
```typescript
// Android
<ImageButton
    android:layout_width="48dp"
    android:layout_height="48dp"
    android:src="@drawable/ic_back"
    android:background="?attr/selectableItemBackgroundBorderless"
    android:contentDescription="Back" />

// HarmonyOS
Button() {
  Image($r('app.media.ic_back'))
    .width(24)
    .height(24)
    .objectFit(ImageFit.Contain)
}
  .width(48)
  .height(48)
  .type(ButtonType.Normal)
  .backgroundColor(Color.Transparent)
  .onClick(() => {
    // Handle click
  })
```

---

#### 1.2.3 CheckBox → Checkbox 属性映射

**CheckBox 属性映射**

| Android XML | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `android:checked` | `.select()` | boolean → boolean | Android: `android:checked="true"`<br/>HarmonyOS: `Checkbox().select(true)` |
| `android:button` | 无直接对应 | 需自定义实现 | 使用自定义样式 |
| `android:buttonTint` | 无直接对应 | 需自定义实现 | 使用状态样式 |
| `android:buttonTintMode` | 无直接对应 | 需自定义实现 | 使用状态样式 |

**CheckBox 事件映射**

| Android XML | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `android:OnCheckedChangeListener` | `.onChange()` | 监听器 → 回调函数 | Android: `setOnCheckedChangeListener(...)`<br/>HarmonyOS: `Checkbox().onChange((isSelected: boolean) => { ... })` |

---

#### 1.2.4 RadioButton + RadioGroup → Radio + RadioContainer 属性映射

**RadioButton 属性映射**

| Android XML | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `android:checked` | 无直接对应 | 由 RadioContainer 管理 | 使用 RadioContainer 的默认值 |
| `android:button` | 无直接对应 | 需自定义实现 | 使用自定义样式 |
| `android:buttonTint` | 无直接对应 | 需自定义实现 | 使用状态样式 |

**RadioGroup 属性映射**

| Android XML | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `android:orientation` | 无直接对应 | 需布局选择 | 垂直用 Column，水平用 Row |
| `android:checkedButton` | 无直接对应 | 需状态管理 | 使用 `@Local`（V2）/ `@State`（V1）变量管理选中项 |

**组合示例：**
```typescript
// Android
<RadioGroup
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:orientation="vertical">
    <RadioButton
        android:id="@+id/radio1"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="Option 1" />
    <RadioButton
        android:id="@+id/radio2"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="Option 2" />
</RadioGroup>

// HarmonyOS（V2 推荐写法，API 12+；V1 项目把 @ComponentV2 → @Component、@Local → @State 即可）
@ComponentV2
struct RadioGroupExample {
  @Local selectedIndex: number = 0

  build() {
    RadioContainer({ group: 'radioGroup' }) {
      Radio({ value: '0', group: 'radioGroup' })
        .onChange((isSelected: boolean) => {
          if (isSelected) {
            this.selectedIndex = 0;
          }
        })
      Radio({ value: '1', group: 'radioGroup' })
        .onChange((isSelected: boolean) => {
          if (isSelected) {
            this.selectedIndex = 1;
          }
        })
    }
  }
}
```

---

#### 1.2.5 Switch/ToggleButton → Toggle 属性映射

**Toggle 属性映射**

| Android XML | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `android:checked` | `.select()` | boolean → boolean | Android: `android:checked="true"`<br/>HarmonyOS: `Toggle().select(true)` |
| `android:textOn` | 无直接对应 | 需组合实现 | 使用 `Toggle` + `Text` 组合 |
| `android:textOff` | 无直接对应 | 需组合实现 | 使用 `Toggle` + `Text` 组合 |
| `android:thumb` | 无直接对应 | 需自定义实现 | 使用自定义样式 |
| `android:thumbTint` | 无直接对应 | 需自定义实现 | 使用状态样式 |
| `android:track` | 无直接对应 | 需自定义实现 | 使用自定义样式 |
| `android:trackTint` | 无直接对应 | 需自定义实现 | 使用状态样式 |
| `android:showText` | 无直接对应 | 需组合实现 | 使用 `Toggle` + `Text` 组合 |
| `android:splitTrack` | 无直接对应 | 需自定义实现 | 使用自定义样式 |

**Toggle 类型选择**

| Android 组件 | HarmonyOS 类型 | 代码示例 |
|-------------|---------------|---------|
| `Switch` | `ToggleType.Switch` | `Toggle({ type: ToggleType.Switch })` |
| `ToggleButton` | `ToggleType.Button` | `Toggle({ type: ToggleType.Button })` |

**Toggle 事件映射**

| Android XML | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `android:OnCheckedChangeListener` | `.onChange()` | 监听器 → 回调函数 | Android: `setOnCheckedChangeListener(...)`<br/>HarmonyOS: `Toggle().onChange((isOn: boolean) => { ... })` |

---

#### 1.2.6 按钮组件通用布局属性映射

按钮组件继承所有通用布局属性，参考 1.1.4 文本组件通用布局属性映射。

**额外按钮特定属性**

| Android XML | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `android:minWidth` | `.constraintSize()` | dp → vp | Android: `android:minWidth="88dp"`<br/>HarmonyOS: `Button('Click').constraintSize({ minWidth: 88 })` |
| `android:minHeight` | `.constraintSize()` | dp → vp | Android: `android:minHeight="48dp"`<br/>HarmonyOS: `Button('Click').constraintSize({ minHeight: 48 })` |
| `android:paddingStart` | `.padding({ start })` | dp → vp | Android: `android:paddingStart="16dp"`<br/>HarmonyOS: `Button('Click').padding({ start: 16 })` |
| `android:paddingEnd` | `.padding({ end })` | dp → vp | Android: `android:paddingEnd="16dp"`<br/>HarmonyOS: `Button('Click').padding({ end: 16 })` |

---

#### 1.2.7 按钮组件属性映射统计

| 映射类型 | 数量 | 占比 |
|---------|------|------|
| 直接映射 | 20 | ~45% |
| 需类型转换 | 10 | ~23% |
| 需组合实现 | 10 | ~23% |
| 无直接对应 | 4 | ~9% |
| **总计** | **44** | **100%** |

---

### 1.3 图片类组件

| Android 组件 | 类名 | HarmonyOS 组件 | 替代方案 | 说明 |
|-------------|------|---------------|---------|------|
| ImageView | `android.widget.ImageView` | `Image` | 直接映射 | 图片显示组件 |
| QuickContactBadge | `android.widget.QuickContactBadge` | `Badge` + `Image` | 组合实现 | 快捷联系人徽章 |

---

#### 1.3.1 ImageView → Image 属性映射

**图片源属性**

| Android XML | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `android:src` | 构造函数参数 | Drawable → Resource | Android: `android:src="@drawable/image"`<br/>HarmonyOS: `Image($r('app.media.image'))` |
| `android:srcCompat` | 构造函数参数 | Drawable → Resource | Android: `android:srcCompat="@drawable/image"`<br/>HarmonyOS: `Image($r('app.media.image'))` |

**图片缩放类型属性**

| Android XML | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `android:scaleType` | `.objectFit()` | ScaleType → ImageFit | Android: `android:scaleType="centerCrop"`<br/>HarmonyOS: `Image($r('app.media.image')).objectFit(ImageFit.Cover)` |
| `android:scaleType="center"` | `.objectFit()` | center → ImageFit.None | Android: `android:scaleType="center"`<br/>HarmonyOS: `Image($r('app.media.image')).objectFit(ImageFit.None)` |
| `android:scaleType="centerCrop"` | `.objectFit()` | centerCrop → ImageFit.Cover | Android: `android:scaleType="centerCrop"`<br/>HarmonyOS: `Image($r('app.media.image')).objectFit(ImageFit.Cover)` |
| `android:scaleType="centerInside"` | `.objectFit()` | centerInside → ImageFit.Contain | Android: `android:scaleType="centerInside"`<br/>HarmonyOS: `Image($r('app.media.image')).objectFit(ImageFit.Contain)` |
| `android:scaleType="fitCenter"` | `.objectFit()` | fitCenter → ImageFit.Contain | Android: `android:scaleType="fitCenter"`<br/>HarmonyOS: `Image($r('app.media.image')).objectFit(ImageFit.Contain)` |
| `android:scaleType="fitXY"` | `.objectFit()` | fitXY → ImageFit.Fill | Android: `android:scaleType="fitXY"`<br/>HarmonyOS: `Image($r('app.media.image')).objectFit(ImageFit.Fill)` |
| `android:scaleType="fitStart"` | `.objectFit()` | fitStart → ImageFit.Contain | Android: `android:scaleType="fitStart"`<br/>HarmonyOS: `Image($r('app.media.image')).objectFit(ImageFit.Contain)` |
| `android:scaleType="fitEnd"` | `.objectFit()` | fitEnd → ImageFit.Contain | Android: `android:scaleType="fitEnd"`<br/>HarmonyOS: `Image($r('app.media.image')).objectFit(ImageFit.Contain)` |

**图片调整属性**

| Android XML | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `android:adjustViewBounds` | 无直接对应 | 需自定义实现 | 使用尺寸约束 |
| `android:maxWidth` | `.constraintSize()` | dp → vp | Android: `android:maxWidth="200dp"`<br/>HarmonyOS: `Image($r('app.media.image')).constraintSize({ maxWidth: 200 })` |
| `android:maxHeight` | `.constraintSize()` | dp → vp | Android: `android:maxHeight="200dp"`<br/>HarmonyOS: `Image($r('app.media.image')).constraintSize({ maxHeight: 200 })` |

**图片着色属性**

| Android XML | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `android:tint` | `.renderMode()` + `.colorFilter()` | Color → RenderMode | Android: `android:tint="#FF0000"`<br/>HarmonyOS: `Image($r('app.media.image')).renderMode(ImageRenderMode.Template)` |
| `android:tintMode` | 无直接对应 | 需自定义实现 | 使用渲染模式 |
| `android:colorFilter` | 无直接对应 | 需自定义实现 | 使用颜色滤镜 API |

**图片内容描述属性**

| Android XML | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `android:contentDescription` | `.alt()` | String → String | Android: `android:contentDescription="Image description"`<br/>HarmonyOS: `Image($r('app.media.image')).alt('Image description')` |

**图片裁剪属性**

| Android XML | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `android:cropToPadding` | 无直接对应 | 需自定义实现 | 使用裁剪 API |
| `android:baseline` | 无直接对应 | 需自定义实现 | 使用基线对齐 API |

**图片布局方向属性**

| Android XML | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `android:layoutDirection` | 无直接对应 | 需自定义实现 | 使用布局方向 API |

---

#### 1.3.2 Image 组件加载属性

**加载状态属性**

| Android 方法 | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `setImageResource()` | 构造函数参数 | int → Resource | Android: `imageView.setImageResource(R.drawable.image)`<br/>HarmonyOS: `Image($r('app.media.image'))` |
| `setImageURI()` | 构造函数参数 | String → String | Android: `imageView.setImageURI("https://example.com/image.jpg")`<br/>HarmonyOS: `Image('https://example.com/image.jpg')` |
| `setImageBitmap()` | 无直接对应 | 需自定义实现 | 使用 PixelMap |
| `setImageDrawable()` | 无直接对应 | 需自定义实现 | 使用 Drawable |

**加载事件属性**

| Android 监听器 | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `OnLoadCompleteListener` | `.onComplete()` | 监听器 → 回调函数 | Android: `setOnLoadCompleteListener(...)`<br/>HarmonyOS: `Image($r('app.media.image')).onComplete(() => { ... })` |
| `OnLoadFailedListener` | `.onError()` | 监听器 → 回调函数 | Android: `setOnLoadFailedListener(...)`<br/>HarmonyOS: `Image($r('app.media.image')).onError(() => { ... })` |
| `OnProgressListener` | 无直接对应 | 需自定义实现 | 使用加载进度 API |

---

**ImageFit 枚举值映射**

| Android ScaleType | HarmonyOS ImageFit | 说明 |
|-----------------|-------------------|------|
| `center` | `ImageFit.None` | 不缩放，居中显示 |
| `centerCrop` | `ImageFit.Cover` | 等比缩放，填满容器，裁剪超出部分 |
| `centerInside` | `ImageFit.Contain` | 等比缩放，完整显示在容器内 |
| `fitCenter` | `ImageFit.Contain` | 等比缩放，居中显示 |
| `fitXY` | `ImageFit.Fill` | 拉伸填满容器 |
| `fitStart` | `ImageFit.Contain` | 等比缩放，靠上/靠左显示 |
| `fitEnd` | `ImageFit.Contain` | 等比缩放，靠下/靠右显示 |

---

#### 1.3.3 Image 组件高级属性

**图片渲染模式**

| Android XML | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `android:alpha` | `.opacity()` | float (0-1) → number (0-1) | Android: `android:alpha="0.5"`<br/>HarmonyOS: `Image($r('app.media.image')).opacity(0.5)` |
| `android:rotation` | `.rotate()` | float → { angle: number } | Android: `android:rotation="90"`<br/>HarmonyOS: `Image($r('app.media.image')).rotate({ angle: 90 })` |
| `android:scaleX` | `.scale()` | float → { x: number } | Android: `android:scaleX="1.5"`<br/>HarmonyOS: `Image($r('app.media.image')).scale({ x: 1.5 })` |
| `android:scaleY` | `.scale()` | float → { y: number } | Android: `android:scaleY="1.5"`<br/>HarmonyOS: `Image($r('app.media.image')).scale({ y: 1.5 })` |

**图片边框与圆角**

| Android XML | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `android:background` | 无直接对应 | 需自定义实现 | 使用 `.border()` 和 `.borderRadius()` |
| 无直接对应 | `.borderRadius()` | 需自定义实现 | Android: 使用 ShapeDrawable<br/>HarmonyOS: `Image($r('app.media.image')).borderRadius(8)` |

**图片重复属性**

| Android XML | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `android:tileMode` | 无直接对应 | 需自定义实现 | 使用 `.objectRepeat()` |
| 无直接对应 | `.objectRepeat()` | 需自定义实现 | Android: `android:tileMode="repeat"`<br/>HarmonyOS: `Image($r('app.media.image')).objectRepeat(ImageRepeat.XY)` |

---

#### 1.3.4 图片组件通用布局属性映射

图片组件继承所有通用布局属性，参考 1.1.4 文本组件通用布局属性映射。

---

#### 1.3.5 图片组件属性映射统计

| 映射类型 | 数量 | 占比 |
|---------|------|------|
| 直接映射 | 15 | ~40% |
| 需类型转换 | 10 | ~27% |
| 需组合实现 | 8 | ~22% |
| 无直接对应 | 5 | ~13% |
| **总计** | **38** | **100%** |

### 1.4 选择器类组件

| Android 组件 | 类名 | HarmonyOS 组件 | 替代方案 | 说明 |
|-------------|------|---------------|---------|------|
| Spinner | `android.widget.Spinner` | `Select` | 直接映射 | 下拉选择框 |
| DatePicker | `android.widget.DatePicker` | `DatePicker` | 直接映射 | 日期选择器 |
| TimePicker | `android.widget.TimePicker` | `TimePicker` | 直接映射 | 时间选择器 |
| CalendarView | `android.widget.CalendarView` | `CalendarPicker` | 直接映射 | 日历视图 |
| NumberPicker | `android.widget.NumberPicker` | `TextPicker` | 配合数字数组 | 数字选择器 |

---

#### 1.4.1 Spinner → Select 属性映射

**数据源属性**

| Android XML | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `android:entries` | 构造函数参数 | reference → array | Android: `android:entries="@array/items"`<br/>HarmonyOS: `Select({ options: ['item1', 'item2'] })` |
| `android:prompt` | `.placeholder()` | string → string | Android: `android:prompt="Select an item"`<br/>HarmonyOS: `Select({ placeholder: 'Select an item' })` |
| 无直接对应 | `selected` | 无 → number | Android: `setSelection(0)`<br/>HarmonyOS: `Select({ selected: 0 })` |

**显示模式属性**

| Android XML | HarmonyOS 属性 | 类型转换器 | 代码示例 |
|-------------|---------------|---------|---------|
| `android:spinnerMode` | 无直接对应 | enum → 无 | Android: `android:spinnerMode="dropdown"`<br/>HarmonyOS: Select 始终是下拉式 |
| `android:spinnerMode="dialog"` | 无直接对应 | enum → 无 | Android: `android:spinnerMode="dialog"`<br/>HarmonyOS: 需自定义实现 |

**下拉样式属性**

| Android XML | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `android:dropDownSelector` | 无直接对应 | reference → stateStyles | Android: `android:dropDownSelector="@drawable/selector"`<br/>HarmonyOS: `Select().stateStyles({ ... })` |
| `android:dropDownVerticalOffset` | 无直接对应 | dimension → 无 | Android: `android:dropDownVerticalOffset="10dp"`<br/>HarmonyOS: 需自定义实现 |
| `android:dropDownHorizontalOffset` | 无直接对应 | dimension → 无 | Android: `android:dropDownHorizontalOffset="10dp"`<br/>HarmonyOS: 需自定义实现 |
| `android:dropDownWidth` | 无直接对应 | dimension → 无 | Android: `android:dropDownWidth="200dp"`<br/>HarmonyOS: 需自定义实现 |
| `android:dropDownHeight` | 无直接对应 | dimension → 无 | Android: `android:dropDownHeight="300dp"`<br/>HarmonyOS: 需自定义实现 |
| `android:popupBackground` | `.backgroundColor()` | reference/color → ResourceColor | Android: `android:popupBackground="@drawable/popup_bg"`<br/>HarmonyOS: `Select().backgroundColor('#FFFFFF')` |

**文本样式属性**

| Android XML | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `android:gravity` | 无直接对应 | enum → 无 | Android: `android:gravity="center"`<br/>HarmonyOS: 使用 `.textAlign()` |

**程序化方法映射**

| Android 方法 | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `setAdapter()` | 构造函数参数 | SpinnerAdapter → array | Android: `spinner.setAdapter(adapter)`<br/>HarmonyOS: `Select({ options: [...] })` |
| `setOnItemSelectedListener()` | `.onSelect()` | listener → callback | Android: `setOnItemSelectedListener(...)`<br/>HarmonyOS: `Select().onSelect((index: number, value?: string) => { ... })` |
| `setSelection(int)` | `selected` | int → number | Android: `setSelection(0)`<br/>HarmonyOS: 更新状态变量 `this.selectedIndex = 0` |
| `getSelectedItem()` | 无直接对应 | 无 → 状态变量 | Android: `getSelectedItem()`<br/>HarmonyOS: `this.options[this.selectedIndex]` |
| `getSelectedItemPosition()` | 无直接对应 | 无 → 状态变量 | Android: `getSelectedItemPosition()`<br/>HarmonyOS: `this.selectedIndex` |
| `setPrompt()` | `.placeholder()` | CharSequence → string | Android: `setPrompt("Select")`<br/>HarmonyOS: `Select().placeholder('Select')` |
| `setEnabled()` | `.enabled()` | boolean → boolean | Android: `setEnabled(false)`<br/>HarmonyOS: `Select().enabled(false)` |

---

#### 1.4.2 DatePicker → DatePicker 属性映射

**日期值属性**

| Android XML | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `android:year` | 构造函数参数 | int → Date | Android: `android:year="2024"`<br/>HarmonyOS: `DatePicker({ selected: new Date(2024, 0, 1) })` |
| `android:month` | 构造函数参数 | int → Date | Android: `android:month="0"`<br/>HarmonyOS: `DatePicker({ selected: new Date(2024, 0, 1) })` |
| `android:day` | 构造函数参数 | int → Date | Android: `android:day="1"`<br/>HarmonyOS: `DatePicker({ selected: new Date(2024, 0, 1) })` |

**日期范围属性**

| Android XML | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `android:minDate` | `.minDate()` | long → Date | Android: `android:minDate="946684800000"`<br/>HarmonyOS: `DatePicker({ minDate: new Date(2000, 0, 1) })` |
| `android:maxDate` | `.maxDate()` | long → Date | Android: `android:maxDate="2524608000000"`<br/>HarmonyOS: `DatePicker({ maxDate: new Date(2050, 11, 31) })` |

**显示模式属性**

| Android XML | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `android:datePickerMode` | 无直接对应 | enum → 无 | Android: `android:datePickerMode="spinner"`<br/>HarmonyOS: 需自定义实现 |
| `android:calendarViewShown` | 无直接对应 | boolean → 无 | Android: `android:calendarViewShown="true"`<br/>HarmonyOS: 需自定义实现 |

**程序化方法映射**

| Android 方法 | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `init()` | 构造函数参数 | (int, int, int) → Date | Android: `init(2024, 0, 1, listener)`<br/>HarmonyOS: `DatePicker({ selected: new Date(2024, 0, 1) })` |
| `updateDate()` | 更新状态变量 | (int, int, int) → Date | Android: `updateDate(2024, 0, 1)`<br/>HarmonyOS: `this.selectedDate = new Date(2024, 0, 1)` |
| `getYear()` | 无直接对应 | 无 → 状态变量 | Android: `getYear()`<br/>HarmonyOS: `this.selectedDate.getFullYear()` |
| `getMonth()` | 无直接对应 | 无 → 状态变量 | Android: `getMonth()`<br/>HarmonyOS: `this.selectedDate.getMonth()` |
| `getDayOfMonth()` | 无直接对应 | 无 → 状态变量 | Android: `getDayOfMonth()`<br/>HarmonyOS: `this.selectedDate.getDate()` |
| `setOnDateChangedListener()` | `.onChange()` | listener → callback | Android: `setOnDateChangedListener(...)`<br/>HarmonyOS: `DatePicker().onChange((value: Date) => { ... })` |

---

#### 1.4.3 TimePicker → TimePicker 属性映射

**时间值属性**

| Android XML | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `android:hour` | 构造函数参数 | int → number | Android: `android:hour="12"`<br/>HarmonyOS: `TimePicker({ selected: new Date(2024, 0, 1, 12, 0, 0) })` |
| `android:minute` | 构造函数参数 | int → number | Android: `android:minute="30"`<br/>HarmonyOS: `TimePicker({ selected: new Date(2024, 0, 1, 12, 30, 0) })` |
| `android:second` | 构造函数参数 | int → number | Android: `android:second="0"`<br/>HarmonyOS: `TimePicker({ selected: new Date(2024, 0, 1, 12, 30, 0) })` |

**时间格式属性**

| Android XML | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `android:format` | 无直接对应 | string → 无 | Android: `android:format="24"`<br/>HarmonyOS: 需自定义实现 |
| `android:is24HourView` | 无直接对应 | boolean → 无 | Android: `android:is24HourView="true"`<br/>HarmonyOS: 需自定义实现 |

**程序化方法映射**

| Android 方法 | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `setOnTimeChangedListener()` | `.onChange()` | listener → callback | Android: `setOnTimeChangedListener(...)`<br/>HarmonyOS: `TimePicker().onChange((value: Date) => { ... })` |
| `getHour()` | 无直接对应 | 无 → 状态变量 | Android: `getHour()`<br/>HarmonyOS: `this.selectedDate.getHours()` |
| `getMinute()` | 无直接对应 | 无 → 状态变量 | Android: `getMinute()`<br/>HarmonyOS: `this.selectedDate.getMinutes()` |
| `getSecond()` | 无直接对应 | 无 → 状态变量 | Android: `getSecond()`<br/>HarmonyOS: `this.selectedDate.getSeconds()` |

---

#### 1.4.4 CalendarView → CalendarPicker 属性映射

**日期选择属性**

| Android XML | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `android:minDate` | `.minDate()` | long → Date | Android: `android:minDate="946684800000"`<br/>HarmonyOS: `CalendarPicker({ minDate: new Date(2000, 0, 1) })` |
| `android:maxDate` | `.maxDate()` | long → Date | Android: `android:maxDate="2524608000000"`<br/>HarmonyOS: `CalendarPicker({ maxDate: new Date(2050, 11, 31) })` |
| `android:firstDayOfWeek` | 无直接对应 | int → 无 | Android: `android:firstDayOfWeek="1"`<br/>HarmonyOS: 需自定义实现 |

**显示属性**

| Android XML | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `android:shownWeekCount` | 无直接对应 | int → 无 | Android: `android:shownWeekCount="4"`<br/>HarmonyOS: 需自定义实现 |
| `android:weekNumberColor` | 无直接对应 | color → 无 | Android: `android:weekNumberColor="#FF0000"`<br/>HarmonyOS: 需自定义实现 |

**程序化方法映射**

| Android 方法 | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `setOnDateChangeListener()` | `.onChange()` | listener → callback | Android: `setOnDateChangeListener(...)`<br/>HarmonyOS: `CalendarPicker().onChange((value: Date) => { ... })` |
| `setDate()` | 更新状态变量 | Calendar → Date | Android: `setDate(calendar)`<br/>HarmonyOS: `this.selectedDate = calendar.getTime()` |

---

#### 1.4.5 NumberPicker → TextPicker 属性映射

**数据源属性**

| Android XML | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `android:minValue` | `range` | int → [number, number] | Android: `android:minValue="0"`<br/>HarmonyOS: `TextPicker({ range: [0, 100] })` |
| `android:maxValue` | `range` | int → [number, number] | Android: `android:maxValue="100"`<br/>HarmonyOS: `TextPicker({ range: [0, 100] })` |
| `android:wrapSelectorWheel` | 无直接对应 | boolean → 无 | Android: `android:wrapSelectorWheel="true"`<br/>HarmonyOS: 需自定义实现 |

**显示值属性**

| Android XML | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `android:displayedValues` | 构造函数参数 | array → array | Android: `android:displayedValues="@array/numbers"`<br/>HarmonyOS: `TextPicker({ range: [1, 2, 3, 4, 5] })` |

**程序化方法映射**

| Android 方法 | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `setDisplayedValues()` | 构造函数参数 | array → array | Android: `setDisplayedValues(values)`<br/>HarmonyOS: `TextPicker({ range: values })` |
| `setOnValueChangedListener()` | `.onChange()` | listener → callback | Android: `setOnValueChangedListener(...)`<br/>HarmonyOS: `TextPicker().onChange((value: string) => { ... })` |
| `setValue()` | 更新状态变量 | int → number | Android: `setValue(50)`<br/>HarmonyOS: `this.selectedValue = 50` |
| `getValue()` | 无直接对应 | 无 → 状态变量 | Android: `getValue()`<br/>HarmonyOS: `this.selectedValue` |

---

#### 1.4.6 选择器组件属性映射统计

| 映射类型 | 数量 | 占比 |
|---------|------|------|
| 直接映射 | 25 | ~45% |
| 需类型转换 | 15 | ~27% |
| 需组合实现 | 10 | ~18% |
| 无直接对应 | 5 | ~10% |
| **总计** | **55** | **100%** |

---

### 1.5 进度与评分类组件

| Android 组件 | 类名 | HarmonyOS 组件 | 替代方案 | 说明 |
|-------------|------|---------------|---------|------|
| ProgressBar | `android.widget.ProgressBar` | `Progress` | 直接映射 | 进度条 |
| SeekBar | `android.widget.SeekBar` | `Slider` | 直接映射 | 可拖动进度条 |
| RatingBar | `android.widget.RatingBar` | `Rating` | 直接映射 | 评分条 |
| ContentLoadingProgressBar | `android.widget.ContentLoadingProgressBar` | `Progress` + `LoadingProgress` | 组合实现 | 内容加载进度条 |

---

#### 1.5.1 ProgressBar → Progress 属性映射

**进度值属性**

| Android XML | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `android:max` | 构造函数参数 | int → number | Android: `android:max="100"`<br/>HarmonyOS: `Progress({ value: 50, total: 100 })` |
| `android:progress` | 构造函数参数 | int → number | Android: `android:progress="50"`<br/>HarmonyOS: `Progress({ value: 50, total: 100 })` |
| `android:secondaryProgress` | 无直接对应 | int → 无 | Android: `android:secondaryProgress="75"`<br/>HarmonyOS: 需自定义实现 |

**不确定模式属性**

| Android XML | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `android:indeterminate` | 构造函数参数 | boolean → boolean | Android: `android:indeterminate="true"`<br/>HarmonyOS: `Progress({ value: 0, total: 100, type: ProgressType.Ring })` |
| `android:indeterminateOnly` | 无直接对应 | boolean → 无 | Android: `android:indeterminateOnly="true"`<br/>HarmonyOS: 需自定义实现 |
| `android:indeterminateDuration` | 无直接对应 | int → 无 | Android: `android:indeterminateDuration="2000"`<br/>HarmonyOS: 需自定义实现 |
| `android:indeterminateBehavior` | 无直接对应 | enum → 无 | Android: `android:indeterminateBehavior="repeat"`<br/>HarmonyOS: 需自定义实现 |

**样式属性**

| Android XML | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `android:progressDrawable` | 无直接对应 | reference → 无 | Android: `android:progressDrawable="@drawable/progress"`<br/>HarmonyOS: 需自定义实现 |
| `android:indeterminateDrawable` | 无直接对应 | reference → 无 | Android: `android:indeterminateDrawable="@drawable/indeterminate"`<br/>HarmonyOS: 需自定义实现 |
| `android:progressTint` | `.color()` | color → ResourceColor | Android: `android:progressTint="#FF6200"`<br/>HarmonyOS: `Progress({ value: 50, total: 100 }).color('#FF6200')` |
| `android:progressTintMode` | 无直接对应 | enum → 无 | Android: `android:progressTintMode="src_in"`<br/>HarmonyOS: 需自定义实现 |
| `android:secondaryProgressTint` | 无直接对应 | color → 无 | Android: `android:secondaryProgressTint="#00FF00"`<br/>HarmonyOS: 需自定义实现 |
| `android:progressBackgroundTint` | `.backgroundColor()` | color → ResourceColor | Android: `android:progressBackgroundTint="#E0E0E0"`<br/>HarmonyOS: `Progress({ value: 50, total: 100 }).backgroundColor('#E0E0E0')` |

**程序化方法映射**

| Android 方法 | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `setMax(int max)` | 构造函数参数 | int → number | Android: `progressBar.setMax(100)`<br/>HarmonyOS: `Progress({ value: this.progress, total: 100 })` |
| `getMax()` | 无直接对应 | void → number | Android: `int max = progressBar.getMax()`<br/>HarmonyOS: 使用状态变量 `this.total` |
| `setProgress(int progress)` | 构造函数参数 | int → number | Android: `progressBar.setProgress(50)`<br/>HarmonyOS: 更新状态变量 `this.progress = 50` |
| `getProgress()` | 无直接对应 | void → number | Android: `int progress = progressBar.getProgress()`<br/>HarmonyOS: 使用状态变量 `this.progress` |
| `incrementProgressBy(int delta)` | 无直接对应 | int → 无 | Android: `progressBar.incrementProgressBy(5)`<br/>HarmonyOS: `this.progress += 5` |
| `setSecondaryProgress(int)` | 无直接对应 | int → 无 | Android: `progressBar.setSecondaryProgress(75)`<br/>HarmonyOS: 需自定义实现 |
| `getSecondaryProgress()` | 无直接对应 | void → int | Android: `int sec = progressBar.getSecondaryProgress()`<br/>HarmonyOS: 需自定义实现 |
| `setIndeterminate(boolean)` | 构造函数参数 | boolean → ProgressType | Android: `progressBar.setIndeterminate(true)`<br/>HarmonyOS: `Progress({ type: ProgressType.Ring })` |
| `isIndeterminate()` | 无直接对应 | void → boolean | Android: `boolean isIndet = progressBar.isIndeterminate()`<br/>HarmonyOS: 使用状态变量 |

**ProgressType 枚举值映射**

| Android Style | HarmonyOS ProgressType | 说明 |
|-----------------|-------------------|------|
| `Widget.ProgressBar` (circular) | `ProgressType.Ring` | 圆形进度条 |
| `Widget.ProgressBar.Horizontal` | `ProgressType.Linear` | 线性进度条 |

---

#### 1.5.2 SeekBar → Slider 属性映射

**进度值属性**

| Android XML | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `android:max` | 构造函数参数 | int → number | Android: `android:max="100"`<br/>HarmonyOS: `Slider({ value: 50, min: 0, max: 100 })` |
| `android:progress` | 构造函数参数 | int → number | Android: `android:progress="50"`<br/>HarmonyOS: `Slider({ value: 50, min: 0, max: 100 })` |
| `android:min` | 构造函数参数 | int → number | Android: `android:min="0"`<br/>HarmonyOS: `Slider({ value: 50, min: 0, max: 100 })` |
| `android:secondaryProgress` | 无直接对应 | int → 无 | Android: `android:secondaryProgress="75"`<br/>HarmonyOS: 需自定义实现 |

**视觉外观属性**

| Android XML | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `android:thumb` | 无直接对应 | drawable → 无 | Android: `android:thumb="@drawable/thumb"`<br/>HarmonyOS: 需自定义实现 |
| `android:thumbTint` | 无直接对应 | color → 无 | Android: `android:thumbTint="#FF0000"`<br/>HarmonyOS: 需自定义实现 |
| `android:thumbTintMode` | 无直接对应 | enum → 无 | Android: `android:thumbTintMode="src_in"`<br/>HarmonyOS: 需自定义实现 |
| `android:thumbOffset` | 无直接对应 | int → 无 | Android: `android:thumbOffset="10"`<br/>HarmonyOS: 需自定义实现 |
| `android:track` | `.trackColor()` | drawable → ResourceColor | Android: `android:track="@drawable/track"`<br/>HarmonyOS: `Slider({ value: 50 }).trackColor('#CCCCCC')` |
| `android:progressTint` | `.selectedColor()` | color → ResourceColor | Android: `android:progressTint="#FF6200"`<br/>HarmonyOS: `Slider({ value: 50 }).selectedColor('#FF6200')` |
| `android:progressTintMode` | 无直接对应 | enum → 无 | Android: `android:progressTintMode="src_in"`<br/>HarmonyOS: 需自定义实现 |
| `android:progressBackgroundTint` | `.trackColor()` | color → ResourceColor | Android: `android:progressBackgroundTint="#E0E0E0"`<br/>HarmonyOS: `Slider({ value: 50 }).trackColor('#E0E0E0')` |
| `android:secondaryProgressTint` | 无直接对应 | color → 无 | Android: `android:secondaryProgressTint="#00FF00"`<br/>HarmonyOS: 需自定义实现 |

**交互属性**

| Android XML | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `android:splitTrack` | 无直接对应 | boolean → 无 | Android: `android:splitTrack="false"`<br/>HarmonyOS: 需自定义实现 |
| `android:mirrorForRtl` | 无直接对应 | boolean → 无 | Android: `android:mirrorForRtl="true"`<br/>HarmonyOS: 需自定义实现 |
| `android:isIndicator` | 无直接对应 | boolean → 无 | Android: `android:isIndicator="true"`<br/>HarmonyOS: 需自定义实现 |

**程序化方法映射**

| Android 方法 | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `getMax()` | 无直接对应 | void → number | Android: `int max = seekBar.getMax()`<br/>HarmonyOS: 使用状态变量 `this.max` |
| `setMax(int max)` | 构造函数参数 | int → number | Android: `seekBar.setMax(100)`<br/>HarmonyOS: 更新状态变量 `this.max = 100` |
| `getProgress()` | 无直接对应 | void → number | Android: `int progress = seekBar.getProgress()`<br/>HarmonyOS: 使用状态变量 `this.progress` |
| `setProgress(int progress)` | 构造函数参数 | int → number | Android: `seekBar.setProgress(50)`<br/>HarmonyOS: 更新状态变量 `this.progress = 50` |
| `incrementProgressBy(int delta)` | 无直接对应 | int → 无 | Android: `seekBar.incrementProgressBy(5)`<br/>HarmonyOS: `this.progress += 5` |
| `getMin()` | 无直接对应 | void → number | Android: `int min = seekBar.getMin()`<br/>HarmonyOS: 使用状态变量 `this.min` |
| `setMin(int min)` | 构造函数参数 | int → number | Android: `seekBar.setMin(0)`<br/>HarmonyOS: 更新状态变量 `this.min = 0` |

**事件监听器映射**

| Android 监听器 | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `setOnSeekBarChangeListener()` | `.onChange()` | listener → callback | Android: `setOnSeekBarChangeListener(...)`<br/>HarmonyOS: `Slider().onChange((value: number) => { ... })` |

---

#### 1.5.3 RatingBar → Rating 属性映射

**评分值属性**

| Android XML | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `android:numStars` | 构造函数参数 | int → number | Android: `android:numStars="5"`<br/>HarmonyOS: `Rating({ rating: 3.5, starNum: 5 })` |
| `android:rating` | 构造函数参数 | float → number | Android: `android:rating="3.5"`<br/>HarmonyOS: `Rating({ rating: 3.5, starNum: 5 })` |
| `android:stepSize` | 构造函数参数 | float → number | Android: `android:stepSize="0.5"`<br/>HarmonyOS: `Rating({ rating: 3.5, stepSize: 0.5 })` |
| `android:isIndicator` | 无直接对应 | boolean → 无 | Android: `android:isIndicator="true"`<br/>HarmonyOS: 使用 `.enabled(false)` |

**程序化方法映射**

| Android 方法 | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `setNumStars(int numStars)` | 构造函数参数 | int → number | Android: `ratingBar.setNumStars(5)`<br/>HarmonyOS: `Rating({ rating: this.rating, starNum: 5 })` |
| `getNumStars()` | 无直接对应 | void → int | Android: `int numStars = ratingBar.getNumStars()`<br/>HarmonyOS: 使用状态变量 `this.starNum` |
| `setRating(float rating)` | 构造函数参数 | float → number | Android: `ratingBar.setRating(3.5f)`<br/>HarmonyOS: 更新状态变量 `this.rating = 3.5` |
| `getRating()` | 无直接对应 | void → float | Android: `float rating = ratingBar.getRating()`<br/>HarmonyOS: 使用状态变量 `this.rating` |
| `setStepSize(float stepSize)` | 构造函数参数 | float → number | Android: `ratingBar.setStepSize(0.5f)`<br/>HarmonyOS: `Rating({ rating: this.rating, stepSize: 0.5 })` |
| `getStepSize()` | 无直接对应 | void → float | Android: `float stepSize = ratingBar.getStepSize()`<br/>HarmonyOS: 使用状态变量 `this.stepSize` |
| `setIsIndicator(boolean)` | 无直接对应 | boolean → 无 | Android: `ratingBar.setIsIndicator(true)`<br/>HarmonyOS: 使用 `.enabled(false)` |
| `isIndicator()` | 无直接对应 | void → boolean | Android: `boolean isInd = ratingBar.isIndicator()`<br/>HarmonyOS: 使用状态变量 |

**事件监听器映射**

| Android 监听器 | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `setOnRatingBarChangeListener()` | `.onChange()` | listener → callback | Android: `setOnRatingBarChangeListener(...)`<br/>HarmonyOS: `Rating().onChange((value: number) => { ... })` |

---

#### 1.5.4 ContentLoadingProgressBar → Progress + LoadingProgress 组合实现

**组合功能映射**

| Android 功能 | HarmonyOS 实现 | 代码示例 |
|-------------|---------------|---------|
| 进度显示 | `Progress` 组件 | Android: `ProgressBar`<br/>HarmonyOS: `Progress({ value: this.progress, total: 100 })` |
| 加载动画 | `LoadingProgress` 组件 | Android: `ContentLoadingProgressBar`<br/>HarmonyOS: `LoadingProgress()` |

---

#### 1.5.5 进度与评分类组件属性映射统计

| 映射类型 | 数量 | 占比 |
|---------|------|------|
| 直接映射 | 30 | ~40% |
| 需类型转换 | 20 | ~27% |
| 需组合实现 | 15 | ~20% |
| 无直接对应 | 10 | ~13% |
| **总计** | **75** | **100%** |

### 1.6 搜索类组件

| Android 组件 | 类名 | HarmonyOS 组件 | 替代方案 | 说明 |
|-------------|------|---------------|---------|------|
| SearchView | `android.widget.SearchView` | `Search` | 直接映射 | 搜索视图 |
| SearchBar | `android.widget.SearchBar` | `Search` | 直接映射 | 搜索栏 |

---

#### 1.6.1 SearchView/SearchBar → Search 属性映射

**搜索值属性**

| Android XML | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `android:queryHint` | `.placeholder()` | string → string | Android: `android:queryHint="Search..."`<br/>HarmonyOS: `Search({ value: '' }).placeholder('Search...')` |
| `android:query` | 构造函数参数 | string → string | Android: `android:query="search"`<br/>HarmonyOS: `Search({ value: 'search' })` |
| `android:iconifiedByDefault` | 无直接对应 | boolean → 无需自定义实现 | Android: `android:iconifiedByDefault="true"`<br/>HarmonyOS: 需自定义实现 |

**搜索按钮属性**

| Android XML | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `android:searchIcon` | 无直接对应 | drawable → 需自定义实现 | Android: `android:searchIcon="@drawable/ic_search"`<br/>HarmonyOS: 需自定义实现 |
| `android:closeIcon` | 无直接对应 | drawable → 需自定义实现 | Android: `android:closeIcon="@drawable/ic_close"`<br/>HarmonyOS: 需自定义实现 |
| `android:goIcon` | 无直接对应 | drawable → 需自定义实现 | Android: `android:goIcon="@drawable/ic_go"`<br/>HarmonyOS: 需自定义实现 |
| `android:voiceIcon` | 无直接对应 | drawable → 需自定义实现 | Android: `android:voiceIcon="@drawable/ic_mic"`<br/>HarmonyOS: 需自定义实现 |
| `android:commitIcon` | 无直接对应 | drawable → 需自定义实现 | Android: `android:commitIcon="@drawable/ic_commit"`<br/>HarmonyOS: 需自定义实现 |

**搜索选项属性**

| Android XML | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `android:searchSuggestAuthority` | 无直接对应 | string → 需自定义实现 | Android: `android:searchSuggestAuthority="com.example"`<br/>HarmonyOS: 需自定义实现 |
| `android:searchSuggestSelection` | 无直接对应 | string → 需自定义实现 | Android: `android:searchSuggestSelection="query"`<br/>HarmonyOS: 需自定义实现 |
| `android:searchSuggestThreshold` | 无直接对应 | int → 需自定义实现 | Android: `android:searchSuggestThreshold="1"`<br/>HarmonyOS: 需自定义实现 |

**输入法属性**

| Android XML | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `android:imeOptions` | 无直接对应 | enum → 需自定义实现 | Android: `android:imeOptions="actionSearch"`<br/>HarmonyOS: 需自定义实现 |
| `android:inputType` | 无直接对应 | enum → 需自定义实现 | Android: `android:inputType="text"`<br/>HarmonyOS: 需自定义实现 |

**程序化方法映射**

| Android 方法 | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `setQuery()` | 更新状态变量 | string → string | Android: `searchView.setQuery("search")`<br/>HarmonyOS: 更新状态变量 `this.searchValue = "search"` |
| `getQuery()` | 无直接对应 | void → string | Android: `String query = searchView.getQuery()`<br/>HarmonyOS: 使用状态变量 `this.searchValue` |
| `setOnQueryTextListener()` | `.onChange()` | listener → callback | Android: `setOnQueryTextListener(...)`<br/>HarmonyOS: `Search().onChange((value: string) => { ... })` |
| `setOnCloseListener()` | 无直接对应 | listener → 需自定义实现 | Android: `setOnCloseListener(...)`<br/>HarmonyOS: 需自定义实现 |
| `setOnSearchClickListener()` | 无直接对应 | listener → 需自定义实现 | Android: `setOnSearchClickListener(...)`<br/>HarmonyOS: 需自定义实现 |

**事件监听器映射**

| Android 监听器 | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `OnQueryTextListener` | `.onChange()` | listener → callback | Android: `setOnQueryTextListener(...)`<br/>HarmonyOS: `Search().onChange((value: string) => { ... })` |
| `OnCloseListener` | 无直接对应 | listener → 需自定义实现 | Android: `setOnCloseListener(...)`<br/>HarmonyOS: 需自定义实现 |
| `OnSuggestionListener` | 无直接对应 | listener → 需自定义实现 | Android: `setOnSuggestionListener(...)`<br/>HarmonyOS: 需自定义实现 |

---

#### 1.6.2 搜索组件属性映射统计

| 映射类型 | 数量 | 占比 |
|---------|------|------|
| 直接映射 | 10 | ~35% |
| 需类型转换 | 5 | ~17% |
| 需组合实现 | 8 | ~28% |
| 无直接对应 | 6 | ~20% |
| **总计** | **29** | **100%** |

### 1.7 视频与媒体类组件

| Android 组件 | 类名 | HarmonyOS 组件 | 替代方案 | 说明 |
|-------------|------|---------------|---------|------|
| VideoView | `android.widget.VideoView` | `Video` | 直接映射 | 视频播放视图 |
| MediaController | `android.widget.MediaController` | 自定义组合 | Row + 控制按钮 | 媒体控制器 |
| Space | `android.widget.Space` | `Row`/`Column` 空子项 | 布局技巧 | 空白占位 |

---

#### 1.7.1 VideoView → Video 属性映射

**视频源属性**

| Android XML | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `android:videoPath` | 构造函数参数 | String → string | Android: `android:videoPath="/sdcard/video.mp4"`<br/>HarmonyOS: `Video({ src: '/sdcard/video.mp4' })` |
| 无直接对应 | `previewUri` | 无 → Resource | Android: 无<br/>HarmonyOS: `Video({ previewUri: $r('app.media.preview') })` |

**视频播放控制属性**

| Android XML | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| 无直接对应 | `autoPlay` | 无 → boolean | Android: 需手动调用 start()<br/>HarmonyOS: `Video({ src: 'video.mp4' }).autoPlay(true)` |
| 无直接对应 | `loop` | 无 → boolean | Android: `setLooping(true)`<br/>HarmonyOS: `Video({ src: 'video.mp4' }).loop(true)` |
| 无直接对应 | `muted`` | 无 → boolean | Android: `setVolume(0)`<br/>HarmonyOS: `Video({ src: 'video.mp4' }).muted(true)` |
| 无直接对应 | `controls` | 无 → boolean | Android: 使用 MediaController<br/>HarmonyOS: `Video({ src: 'video.mp4' }).controls(true)` |
| 无直接对应 | `objectFit` | 无 → ImageFit | Android: `setScaleType(ScaleType.FIT_CENTER)`<br/>HarmonyOS: `Video({ src: 'video.mp4' }).objectFit(ImageFit.Contain)` |

**视频缩放类型映射**

| Android ScaleType | HarmonyOS ImageFit | 说明 |
|-----------------|-------------------|------|
| `FIT_CENTER` | `ImageFit.Contain` | 等比缩放，完整显示 |
| `CENTER_CROP` | `ImageFit.Cover` | 等比缩放，填满容器 |
| `FIT_XY` | `ImageFit.Fill` | 拉伸填满容器 |
| `CENTER` | `ImageFit.None` | 不缩放，居中显示 |

**视频事件属性**

| Android 监听器 | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `OnPreparedListener` | `.onPrepared()` | 监听器 → 回调函数 | Android: `setOnPreparedListener(...)`<br/>HarmonyOS: `Video({ src: 'video.mp4' }).onPrepared((event) => { ... })` |
| `OnCompletionListener` | `.onFinish()` | 监听器 → 回调函数 | Android: `setOnCompletionListener(...)`<br/>HarmonyOS: `Video({ src: 'video.mp4' }).onFinish(() => { ... })` |
| `OnErrorListener` | `.onError()` | 监听器 → 回调函数 | Android: `setOnErrorListener(...)`<br/>HarmonyOS: `Video({ src: 'video.mp4' }).onError(() => { ... })` |
| `OnInfoListener` | `.onUpdate()` | 监听器 → 回调函数 | Android: `setOnInfoListener(...)`<br/>HarmonyOS: `Video({ src: 'video.mp4' }).onUpdate((event) => { ... })` |
| 无直接对应 | `.onStart()` | 无 → 回调函数 | Android: 无<br/>HarmonyOS: `Video({ src: 'video.mp4' }).onStart(() => { ... })` |
| 无直接对应 | `.onPause()` | 无 → 回调函数 | Android: 无<br/>HarmonyOS: `Video({ src: 'video.mp4' }).onPause(() => { ... })` |

**VideoController 方法映射**

| Android 方法 | HarmonyOS 方法 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `start()` | `controller.start()` | void → void | Android: `videoView.start()`<br/>HarmonyOS: `this.controller.start()` |
| `pause()` | `controller.pause()` | void → void | Android: `videoView.pause()`<br/>HarmonyOS: `this.controller.pause()` |
| `stopPlayback()` | `controller.stop()` | void → void | Android: `videoView.stopPlayback()`<br/>HarmonyOS: `this.controller.stop()` |
| `seekTo(int)` | `controller.setCurrentTime()` | int → (number, SeekMode) | Android: `videoView.seekTo(5000)`<br/>HarmonyOS: `this.controller.setCurrentTime(5000, SeekMode.Accurate)` |
| `resume()` | `controller.start()` | void → void | Android: `videoView.resume()`<br/>HarmonyOS: `this.controller.start()` |
| `suspend()` | `controller.pause()` | void → void | Android: `videoView.suspend()`<br/>HarmonyOS: `this.controller.pause()` |
| `isPlaying()` | 无直接对应 | 需状态管理 | 使用 `@Local`（V2）/ `@State`（V1）变量 |
| `getDuration()` | 无直接对应 | 需状态管理 | 使用 `@Local`（V2）/ `@State`（V1）变量 |
| `getCurrentPosition()` | 无直接对应 | 需状态管理 | 使用 `@Local`（V2）/ `@State`（V1）变量 |

**SeekMode 枚举值映射**

| Android SeekMode | HarmonyOS SeekMode | 说明 |
|-----------------|-------------------|------|
| `SEEK_CLOSEST_SYNC` | `SeekMode.Accurate` | 精确定位 |
| `SEEK_PREVIOUS_SYNC` | `SeekMode.PreviousKeyFrame` | 定位到前一个关键帧 |
| `SEEK_NEXT_SYNC` | `SeekMode.NextKeyFrame` | 定位到后一个关键帧 |

**视频其他属性**

| Android XML | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `android:layout_width` | `.width()` | dp → vp | Android: `android:layout_width="match_parent"`<br/>HarmonyOS: `Video({ src: 'video.mp4' }).width('100%')` |
| `android:layout_height` | `.height()` | dp → vp | Android: `android:layout_height="200dp"`<br/>HarmonyOS: `Video({ src: 'video.mp4' }).height(200)` |
| 无直接对应 | `controller` | 无 → VideoController | Android: 无<br/>HarmonyOS: `Video({ src: 'video.mp4', controller: this.controller })` |

---

#### 1.7.2 MediaController → 自定义组合实现

**MediaController 功能映射**

| Android 功能 | HarmonyOS 实现 | 代码示例 |
|-------------|---------------|---------|
| 播放/暂停按钮 | `Button` + `onClick` | 使用 `controller.start()` / `controller.pause()` |
| 进度条 | `Slider` + `onChange` | 使用 `controller.setCurrentTime()` |
| 时间显示 | `Text` + 状态变量 | 使用 `onUpdate` 事件更新 |
| 全屏按钮 | `Button` + `onClick` | 使用窗口 API 切换全屏 |

**组合示例：**
```typescript
// Android
<VideoView
    android:id="@+id/videoView"
    android:layout_width="match_parent"
    android:layout_height="200dp" />
<MediaController
    android:id="@+id/mediaController"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:layout_alignParentBottom="true"
    app:mediaController="@id/videoView" />

// HarmonyOS（V2 推荐写法，API 12+；V1 项目把 @ComponentV2 → @Component、@Local → @State 即可）
@ComponentV2
struct VideoPlayerView {
  @Local isPlaying: boolean = false
  @Local currentTime: number = 0
  @Local duration: number = 0

  build() {
    Column() {
      Video({
        src: 'video.mp4',
        controller: this.videoController
      })
        .width('100%')
        .height(200)
        .onUpdate((event) => {
          this.currentTime = event.time;
        })
        .onPrepared((event) => {
          this.duration = event?.duration || 0;
        })

      Row() {
        Button('Play')
          .onClick(() => {
            this.videoController.start();
            this.isPlaying = true;
          })
        Button('Pause')
          .onClick(() => {
            this.videoController.pause();
            this.isPlaying = false;
          })
        Text(`${this.currentTime / 1000}s / ${this.duration / 1000}s`)
      }
    }
  }
}
```

---

#### 1.7.3 视频组件属性映射统计

| 映射类型 | 数量 | 占比 |
|---------|------|------|
| 直接映射 | 10 | ~40% |
| 需类型转换 | 8 | ~32% |
| 需组合实现 | 5 | ~20% |
| 无直接对应 | 2 | ~8% |
| **总计** | **25** | **100%** |

---

### 1.8 滚动类组件

| Android 组件 | 类名 | HarmonyOS 组件 | 替代方案 | 说明 |
|-------------|------|---------------|---------|------|
| ScrollView | `android.widget.ScrollView` | `Scroll` | 直接映射 | 垂直滚动视图 |
| HorizontalScrollView | `android.widget.HorizontalScrollView` | `Scroll` (scrollable: ScrollDirection.Horizontal) | 方向配置 | 水平滚动视图 |
| NestedScrollView | `androidx.core.widget.NestedScrollView` | `Scroll` + 嵌套 | 配合 List/Grid | 支持嵌套滚动的滚动视图 |

---

#### 1.8.1 ScrollView → Scroll 属性映射

**滚动方向属性**

| Android XML | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `android:orientation="vertical"` | `.scrollable()` | enum → ScrollDirection | Android: `android:orientation="vertical"`<br/>HarmonyOS: `Scroll() { ... }.scrollable(ScrollDirection.Vertical)` |
| `android:orientation="horizontal"` | `.scrollable()` | enum → ScrollDirection | Android: `android:orientation="horizontal"`<br/>HarmonyOS: `Scroll() { ... }.scrollable(ScrollDirection.Horizontal)` |

**滚动条属性**

| Android XML | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `android:scrollbars="vertical"` | `.scrollBar()` | enum → BarState | Android: `android:scrollbars="vertical"`<br/>HarmonyOS: `Scroll() { ... }.scrollBar(BarState.On)` |
| `android:scrollbars="horizontal"` | `.scrollBar()` | enum → BarState | Android: `android:scrollbars="horizontal"`<br/>HarmonyOS: `Scroll() { ... }.scrollBar(BarState.On)` |
| `android:scrollbars="none"` | `.scrollBar()` | enum → BarState | Android: `android:scrollbars="none"`<br/>HarmonyOS: `Scroll() { ... }.scrollBar(BarState.Off)` |
| 无直接对应 | `.scrollBarColor()` | 无 → Color | Android: 无<br/>HarmonyOS: `Scroll() { ... }.scrollBarColor(Color.Gray)` |
| 无直接对应 | `.scrollBarWidth()` | 无 → number | Android: 无<br/>HarmonyOS: `Scroll() { ... }.scrollBarWidth(30)` |

**滚动条样式映射**

| Android scrollbarStyle | HarmonyOS BarState | 说明 |
|---------------------|-------------------|------|
| `insideOverlay` | `BarState.Auto` | 滚动条在内容内，不占用空间 |
| `insideInset` | `BarState.On` | 滚动条在内容内，占用空间 |
| `outsideOverlay` | `BarState.Auto` | 滚动条在内容外，不占用空间 |
| `outsideInset` | `BarState.On` | 滚动条在内容外，占用空间 |

**边缘效果属性**

| Android XML | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `android:overScrollMode="always"` | `.edgeEffect()` | enum → EdgeEffect | Android: `android:overScrollMode="always"`<br/>Harmony HarmonyOS: `Scroll() { ... }.edgeEffect(EdgeEffect.Spring)` |
| `android:overScrollMode="ifContentScrolls"` | `.edgeEffect()` | enum → EdgeEffect | Android: `android:overScrollMode="ifContentScrolls"`<br/>HarmonyOS: `Scroll() { ... }.edgeEffect(EdgeEffect.Spring)` |
| `android:overScrollMode="never"` | `.edgeEffect()` | enum → EdgeEffect | Android: `android:overScrollMode="never"`<br/>HarmonyOS: `Scroll() { ... }.edgeEffect(EdgeEffect.None)` |
| `android:overScrollHeader` | 无直接对应 | 需自定义实现 | 使用边缘效果 API |

**EdgeEffect 枚举值映射**

| Android overScrollMode | HarmonyOS EdgeEffect | 说明 |
|---------------------|-------------------|------|
| `always` | `EdgeEffect.Spring` | 始终显示弹性效果 |
| `ifContentScrolls` | `EdgeEffect.Spring` | 内容可滚动时显示效果 |
| `never` | `EdgeEffect.None` | 不显示边缘效果 |

**嵌套滚动属性**

| Android XML | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `android:nestedScrollingEnabled="true"` | `.nestedScroll()` | boolean → NestedScrollOptions | Android: `android:nestedScrollingEnabled="true"`<br/>HarmonyOS: `Scroll() { ... }.nestedScroll({ scrollForward: NestedScrollMode.PARENT_FIRST, scrollBackward: NestedScrollMode.SELF_FIRST })` |

**NestedScrollMode 枚举值映射**

| Android 嵌套行为 | HarmonyOS NestedScrollMode | 说明 |
|---------------------|-------------------------|------|
| 自身先滚动 | `NestedScrollMode.SELF_FIRST` | 自身先滚动，再滚动父容器 |
| 父容器先滚动 | `NestedScrollMode.PARENT_FIRST` | 父容器先滚动，再滚动自身 |
| 仅自身滚动 | `NestedScrollMode.SELF_ONLY` | 只滚动自身，不传递给父容器 |
| 并行滚动 | `NestedScrollMode.PARALLEL` | 自身和父容器同时滚动 |
| 自动选择 | `NestedScrollMode.AUTO` | 系统自动选择滚动模式 |

**滚动填充属性**

| Android XML | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `android:fillViewport` | 无直接对应 | 需自定义实现 | 使用尺寸约束 |

**滚动事件属性**

| Android 监听器 | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `OnScrollListener.onScrollChanged()` | `.onScroll()` | 监听器 → 回调函数 | Android: `setOnScrollChangeListener(...)`<br/>HarmonyOS: `Scroll() { ... }.onScroll((xOffset: number, yOffset: number) => { ... })` |
| `OnScrollListener.onScrollStateChanged()` | `.onScrollStart()` / `.onScrollEnd()` | 监听器 → 回调函数 | Android: `setOnScrollChangeListener(...)`<br/>HarmonyOS: `Scroll() { ... }.onScrollStart(() => { ... }).onScrollEnd(() => { ... })` |
| 无直接对应 | `.onScrollEdge()` | 无 → 回调函数 | Android: 无<br/>HarmonyOS: `Scroll() { ... }.onScrollEdge((side: Edge) => { ... })` |

**滚动控制方法映射**

| Android 方法 | HarmonyOS 方法 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `scrollTo(int x, int y)` | `scroller.scrollTo()` | (int, int) → ({ xOffset, yOffset, animation }) | Android: `scrollView.scrollTo(100, 200)`<br/>HarmonyOS: `this.scroller.scrollTo({ xOffset: 100, yOffset: 200 })` |
| `scrollBy(int dx, int dy)` | `scroller.scrollBy()` | (int, int) → (int, int) | Android: `scrollView.scrollBy(10, 20)`<br/>HarmonyOS: `this.scroller.scrollBy(10, 20)` |
| `smoothScrollTo(int x, int y)` | `scroller.scrollTo()` | (int, int) → ({ xOffset, yOffset, animation }) | Android: `scrollView.smoothScrollTo(100, 200)`<br/>HarmonyOS: `this.scroller.scrollTo({ xOffset: 100, yOffset: 200, animation: { duration: 300 } })` |
| `smoothScrollBy(int dx, int dy)` | `scroller.scrollBy()` | (int, int) → (int, int) | Android: `scrollView.smoothScrollBy(10, 20)`<br/>HarmonyOS: `this.scroller.scrollBy(10, 20)` |
| `fullScroll(int direction)` | `scroller.scrollEdge()` | FOCUS_DOWN/UP → Edge | Android: `scrollView.fullScroll(FOCUS_DOWN)`<br/>HarmonyOS: `this.scroller.scrollEdge(Edge.Bottom)` |
| `pageScroll(int direction)` | 无直接对应 | 需自定义实现 | 使用 `scroller.scrollPage()` |
| `arrowScroll(int direction)` | 无直接对应 | 需自定义实现 | 使用 `scroller.scrollBy()` |

**滚动状态查询方法映射**

| Android 方法 | HarmonyOS 方法 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `getScrollX()` | `scroller.current()().xOffset` | void → number | Android: `scrollView.getScrollX()`<br/>HarmonyOS: `this.scroller.currentOffset().xOffset` |
| `getScrollY()` | `scroller.currentOffset().yOffset` | void → number | Android: `scrollView.getScrollY()`<br/>HarmonyOS: `this.scroller.currentOffset().yOffset` |
| `canScrollVertically()` | 无直接对应 | 需自定义实现 | 使用内容尺寸计算 |
| `canScrollHorizontally()` | 无直接对应 | 需自定义实现 | 使用内容尺寸计算 |

**滚动动画属性**

| Android XML | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| 无直接对应 | `animation` | 无 → ScrollAnimateOptions | Android: 使用 ObjectAnimator<br/>HarmonyOS: `this.scroller.scrollTo({ xOffset: 100, yOffset: 200, animation: { duration: 500, curve: Curve.EaseInOut } })` |

---

#### 1.8.2 HorizontalScrollView → Scroll 属性映射

**水平滚动特有属性**

| Android XML | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `android:orientation` | `.scrollable()` | enum → ScrollDirection | Android: `android:orientation="horizontal"`<br/>HarmonyOS: `Scroll() { ... }.scrollable(ScrollDirection.Horizontal)` |

**其他属性**：与 ScrollView 相同，参考 1.8.1 ScrollView → Scroll 属性映射。

---

#### 1.8.3 NestedScrollView → Scroll 属性映射

**嵌套滚动特有属性**

| Android XML | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `android:nestedScrollingEnabled="true"` | `.nestedScroll()` | boolean → NestedScrollOptions | Android: `android:nestedScrollingEnabled="true"`<br/>HarmonyOS: `Scroll() { ... }.nestedScroll({ scrollForward: NestedScrollMode.PARENT_FIRST, scrollBackward: NestedScrollMode.SELF_FIRST })` |

**其他属性**：与 ScrollView 相同，参考 1.8.1 ScrollView → Scroll 属性映射。

---

#### 1.8.4 Scroll 组件高级属性

**滚动交互属性**

| Android XML | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| 无直接对应 | `.enableScrollInteraction()` | 无 → boolean | Android: 无<br/>HarmonyOS: `Scroll() { ... }.enableScrollInteraction(false)` |

**滚动边缘枚举**

| HarmonyOS Edge | 说明 |
|-----------------|------|
| `Top` | 顶部边缘 |
| `Bottom` | 底部边缘 |
| `Start` | 起始边缘（RTL/LTR 感知） |
| `End` | 结束边缘（RTL/LTR 感知） |

---

#### 1.8.5 滚动组件属性映射统计

| 映射类型 | 数量 | 占比 |
|---------|------|------|
| 直接映射 | 15 | ~45% |
| 需类型转换 | 10 | ~30% |
| 需组合实现 | 5 | ~15% |
| 无直接对应 | 3 | ~10% |
| **总计** | **33** | **100%** |

---

## 二、布局容器组件映射

### 2.1 线性布局

| Android 组件 | 类名 | HarmonyOS 组件 | 替代方案 | 说明 |
|-------------|------|---------------|---------|------|
| LinearLayout | `android.widget.LinearLayout` | `Column` / `Row` | 垂直用 Column，水平用 Row | 线性布局 |
| TableRow | `android.widget.TableRow` | `Row` | 在 Grid 中使用 | 表格行（水平线性） |

---

#### 2.1.1 LinearLayout → Column/Row 属性映射

**方向属性**

| Android XML | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `android:orientation` | 无直接对应 | enum → 组件选择 | Android: `android:orientation="vertical"`<br/>HarmonyOS: 使用 `Column` 组件<br/>Android: `android:orientation="horizontal"`<br/>HarmonyOS: 使用 `Row` 组件 |

**内容对齐属性**

| Android XML | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `android:gravity` | `.justifyContent()` / `.alignItems()` | flags → FlexAlign | Android: `android:gravity="center"`<br/>HarmonyOS: `Column().justifyContent(FlexAlign.Center)`<br/>Android: `android:gravity="center_horizontal"`<br/>HarmonyOS: `Row().alignItems(HorizontalAlign.Center)`<br/>Android: `android:gravity="center_vertical"`<br/>HarmonyOS: `Column().justifyContent(FlexAlign.Center)`<br/>Android: `android:gravity="left"`<br/>HarmonyOS: `Row().alignItems(HorizontalAlign.Start)`<br/>Android: `android:gravity="right"`<br/>HarmonyOS: `Row().alignItems(HorizontalAlign.End)`<br/>Android: `android:gravity="start"`<br/>HarmonyOS: `Row().alignItems(HorizontalAlign.Start)`<br/>Android: `android:gravity="end"`<br/>HarmonyOS: `Row().alignItems(HorizontalAlign.End)` |

**权重分配属性**

| Android XML | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `android:weightSum` | 无直接对应 | float → 自动处理 | Android: `android:weightSum="1.0"`<br/>HarmonyOS: 自动处理，使用 `.layoutWeight()` |

**基线对齐属性**

| Android XML | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `android:baselineAligned` | 无直接对应 | boolean → 需自定义实现 | Android: `android:baselineAligned="true"`<br/>HarmonyOS: 需自定义实现 |

**测量模式属性**

| Android XML | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `android:measureWithLargestChild` | 无直接对应 | boolean → 需自定义实现 | Android: `android:measureWithLargestChild="true"`<br/>HarmonyOS: 需自定义实现 |

**分隔线属性**

| Android XML | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `android:divider` | 无直接对应 | drawable → Divider 组件 | Android: `android:divider="@drawable/divider"`<br/>HarmonyOS: 在子组件间插入 `Divider()` 组件 |
| `android:showDividers` | 无直接对应 | flags → 手动插入 | Android: `android:showDividers="middle"`<br/>HarmonyOS: 需手动插入 Divider 组件 |
| `android:dividerPadding` | 无直接对应 | dimension → Divider padding | Android: `android:dividerPadding="8dp"`<br/>HarmonyOS: `Divider().padding(8)` |

---

#### 2.1.2 LinearLayout 子组件布局属性映射

**对齐属性**

| Android XML | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---|---------|
| `android:layout_gravity` | `.align()` | flags → Alignment | Android: `android:layout_gravity="center"`<br/>HarmonyOS: `.align(Alignment.Center)`<br/>Android: `android:layout_gravity="top"`<br/>HarmonyOS: `.align(Alignment.Top)`<br/>Android: `android:layout_gravity="bottom"`<br/>HarmonyOS: `.align(Alignment.Bottom)`<br/>Android: `android:layout_gravity="left"`<br/>HarmonyOS: `.align(Alignment.Start)`<br/>Android: `android:layout_gravity="right"`<br/>HarmonyOS: `.align(Alignment.End)`<br/>Android: `android:layout_gravity="center_horizontal"`<br/>HarmonyOS: `.align(Alignment.Center)`<br/>Android: `android:layout_gravity="start"`<br/>HarmonyOS: `.align(Alignment.Start)`<br/>Android: `android:layout_gravity="end"`<br/>HarmonyOS: `.align(Alignment.End)` |

**权重属性**

| Android XML | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `android:layout_weight` | `.layoutWeight()` | float → number | Android: `android:layout_weight="1"`<br/>HarmonyOS: `.layoutWeight(1)` |

---

#### 2.1.3 LinearLayout 程序化方法映射属性

| Android 方法 | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `setOrientation(int)` | 无直接对应 | int → 组件选择 | Android: `linearLayout.setOrientation(LinearLayout.VERTICAL)`<br/>HarmonyOS: 使用 `Column` 组件 |
| `getOrientation()` | 无直接对应 | void → 组件判断 | Android: `int orientation = linearLayout.getOrientation()`<br/>HarmonyOS: 根据组件类型判断 |
| `setGravity(int)` | `.justifyContent()` / `.alignItems()` | int → FlexAlign | Android: `linearLayout.setGravity(Gravity.CENTER)`<br/>HarmonyOS: `Column().justifyContent(FlexAlign.Center)` |
| `setWeightSum(float)` | 无直接对应 | float → 自动处理 | Android: `linearLayout.setWeightSum(1.0f)`<br/>HarmonyOS: 自动处理 |
| `setBaselineAligned(boolean)` | 无直接对应 | boolean → 需自定义实现 | Android: `linearLayout.setBaselineAligned(true)`<br/>HarmonyOS: 需自定义实现 |
| `setMeasureWithLargestChild(boolean)` | 无直接对应 | boolean → 需自定义实现 | Android: `linearLayout.setMeasureWithLargestChild(true)`<br/>HarmonyOS: 需自定义实现 |
| `setDividerDrawable()` | 无直接对应 | Drawable → Divider 组件 | Android: `linearLayout.setDividerDrawable(divider)`<br/>HarmonyOS: 使用 `Divider()` 组件 |
| `setShowDividers(int)` | 无直接对应 | int → 手动插入 | Android: `linearLayout.setShowDividers(SHOW_DIVIDER_MIDDLE)`<br/>HarmonyOS: 需手动插入 Divider 组件 |
| `setDividerPadding(int)` | 无直接对应 | int → Divider padding | Android: `linearLayout.setDividerPadding(8)`<br/>HarmonyOS: `Divider().padding(8)` |

---

#### 2.1.4 LinearLayout 属性映射统计

| 映射类型 | 数量 | 占比 |
|---------|------|------|
| 直接映射 | 6 | ~26% |
| 需类型转换 | 4 | ~17% |
| 需组合实现 | 8 | ~35% |
| 无直接对应 | 5 | ~22% |
| **总计** | **23** | **100%** |

---

### 2.2 相对布局

| Android 组件 | 类名 | HarmonyOS 组件 | 替代方案 | 说明 |
|-------------|------|---------------|---------|------|
| RelativeLayout | `android.widget.RelativeLayout` | `RelativeContainer` | 直接映射 | 相对布局 |
| PercentRelativeLayout | `androidx.percentlayout.widget.PercentRelativeLayout` | `RelativeContainer` + 约束尺寸 | 已废弃 | 百分比相对布局 |

---

#### 2.2.1 RelativeLayout → RelativeContainer 属性映射

**容器级别属性**

| Android XML | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `android:gravity` | 无直接对应 | flags → 需自定义实现 | Android: `android:gravity="center"`<br/>HarmonyOS: 需自定义实现 |

**子组件相对父容器定位属性**

| Android XML | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `android:layout_alignParentTop` | `.alignRules()` | boolean → alignRules | Android: `android:layout_alignParentTop="true"`<br/>HarmonyOS: `.alignRules({ anchor: '__container__', align: VerticalAlign.Top })` |
| `android:layout_alignParentBottom` | `.alignRules()` | boolean → alignRules | Android: `android:layout_alignParentBottom="true"`<br/>HarmonyOS: `.alignRules({ anchor: '__container__', align: VerticalAlign.Bottom })` |
| `android:layout_alignParentLeft` | `.alignRules()` | boolean → alignRules | Android: `android:layout_alignParentLeft="true"`<br/>HarmonyOS: `.alignRules({ anchor: '__container__', align: HorizontalAlign.Start })` |
| `android:layout_alignParentRight` | `.alignRules()` | boolean → alignRules | Android: `android:layout_alignParentRight="true"`<br/>HarmonyOS: `.alignRules({ anchor: '__container__', align: HorizontalAlign.End })` |
| `android:layout_alignParentStart` | `.alignRules()` | boolean → alignRules | Android: `android:layout_alignParentStart="true"`<br/>HarmonyOS: `.alignRules({ anchor: '__container__', align: HorizontalAlign.Start })` |
| `android:layout_alignParentEnd` | `.alignRules()` | boolean → alignRules | Android: `android:layout_alignParentEnd="true"`<br/>HarmonyOS: `.alignRules({ anchor: '__container__', align: HorizontalAlign.End })` |
| `android:layout_centerHorizontal` | `.alignRules()` | boolean → alignRules | Android: `android:layout_centerHorizontal="true"`<br/>HarmonyOS: `.alignRules({ anchor: '__container__', align: HorizontalAlign.Center })` |
| `android:layout_centerVertical` | `.alignRules()` | boolean → alignRules | Android: `android:layout_centerVertical="true"`<br/>HarmonyOS: `.alignRules({ anchor: '__container__', align: VerticalAlign.Center })` |
| `android:layout_centerInParent` | `.alignRules()` | boolean → alignRules | Android: `android:layout_centerInParent="true"`<br/>HarmonyOS: `.alignRules({ anchor: '__container__', align: Alignment.Center })` |

**子组件相对兄弟组件定位属性**

| Android XML | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `android:layout_above` | `.alignRules()` | reference → alignRules | Android: `android:layout_above="@id/sibling"`<br/>HarmonyOS: `.alignRules({ anchor: 'sibling', align: VerticalAlign.Top })` |
| `android:layout_below` | `.alignRules()` | reference → alignRules | Android: `android:layout_below="@id/sibling"`<br/>HarmonyOS: `.alignRules({ anchor: 'sibling', align: VerticalAlign.Bottom })` |
| `android:layout_toLeftOf` | `.alignRules()` | reference → alignRules | Android: `android:layout_toLeftOf="@id/sibling"`<br/>HarmonyOS: `.alignRules({ anchor: 'sibling', align: HorizontalAlign.Start })` |
| `android:layout_toRightOf` | `.alignRules()` | reference → alignRules | Android: `android:layout_toRightOf="@id/sibling"`<br/>HarmonyOS: `.alignRules({ anchor: 'sibling', align: HorizontalAlign.End })` |
| `android:layout_toStartOf` | `.alignRules()` | reference → alignRules | Android: `android:layout_toStartOf="@id/sibling"`<br/>HarmonyOS: `.alignRules({ anchor: 'sibling', align: HorizontalAlign.Start })` |
| `android:layout_toEndOf` | `.alignRules()` | reference → alignRules | Android: `android:layout_toEndOf="@id/sibling"`<br/>HarmonyOS: `.alignRules({ anchor: 'sibling', align: HorizontalAlign.End })` |

**子组件边缘对齐属性**

| Android XML | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `android:layout_alignTop` | `.alignRules()` | reference → alignRules | Android: `android:layout_alignTop="@id/sibling"`<br/>HarmonyOS: `.alignRules({ anchor: 'sibling', align: VerticalAlign.Top })` |
| `android:layout_alignBottom` | `.alignRules()` | reference → alignRules | Android: `android:layout_alignBottom="@id/sibling"`<br/>HarmonyOS: `.alignRules({ anchor: 'sibling', align: VerticalAlign.Bottom })` |
| `android:layout_alignLeft` | `.alignRules()` | reference → alignRules | Android: `android:layout_alignLeft="@id/sibling"`<br/>HarmonyOS: `.alignRules({ anchor: 'sibling', align: HorizontalAlign.Start })` |
| `android:layout_alignRight` | `.alignRules()` | reference → alignRules | Android: `android:layout_alignRight="@id/sibling"`<br/>HarmonyOS: `.alignRules({ anchor: 'sibling', align: HorizontalAlign.End })` |
| `android:layout_alignStart` | `.alignRules()` | reference → alignRules | Android: `android:layout_alignStart="@id/sibling"`<br/>HarmonyOS: `.alignRules({ anchor: 'sibling', align: HorizontalAlign.Start })` |
| `android:layout_alignEnd` | `.alignRules()` | reference → alignRules | Android: `android:layout_alignEnd="@id/sibling"`<br/>HarmonyOS:: `.alignRules({ anchor: 'sibling', align: HorizontalAlign.End })` |
| `android:layout_alignBaseline` | `.alignRules()` | reference → alignRules | Android: `android:layout_alignBaseline="@id/sibling"`<br/>HarmonyOS: `.alignRules({ anchor: 'sibling', align: VerticalAlign.Center })` |

---

#### 2.2.2 RelativeLayout 属性映射统计

| 映射类型 | 数量 | 占比 |
|---------|------|------|
| 直接映射 | 0 | ~0% |
| 需类型转换 | 0 | ~0% |
| 需组合实现 | 17 | ~100% |
| 无直接对应 | 0 | ~0% |
| **总计** | **17** | **100%** |

---

### 2.3 帧布局

| Android 组件 | 类名 | HarmonyOS 组件 | 替代方案 | 说明 |
|-------------|------|---------------|---------|------|
| FrameLayout | `android.widget.FrameLayout` | `Stack` | 直接映射 | 帧布局 |
| DialerFilter | `android.widget.DialerFilter` | 自定义组合 | 需业务实现 | 拨号过滤器 |
| TwoLineListItem | `android.widget.TwoLineListItem` | `Column` + 2个 `Text` | 已废弃 | 双行列表项 |

---

#### 2.3.1 FrameLayout → Stack 属性映射

**容器级别属性**

| Android XML | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `android:foreground` | 无直接对应 | drawable → 顶层组件 | Android: `android:foreground="@drawable/overlay"`<br/>HarmonyOS: 在 Stack 顶层添加 Image/Color 组件 |
| `android:foregroundGravity` | `.alignContent()` | flags → Alignment | Android: `android:foregroundGravity="center"`<br/>HarmonyOS: `Stack({ alignContent: Alignment.Center })` |
| `android:measureAllChildren` | 无直接对应 | boolean → 需自定义实现 | Android: `android:measureAllChildren="true"`<br/>HarmonyOS: 需自定义实现 |

**子组件布局属性**

| Android XML | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `android:layout_gravity` | `.align()` | flags → Alignment | Android: `android:layout_gravity="center"`<br/>HarmonyOS: `.align(Alignment.Center)`<br/>Android: `android:layout_gravity="top"`<br/>HarmonyOS: `.align(Alignment.Top)`<br/>Android: `android:layout_gravity="bottom"`<br/>HarmonyOS: `.align(Alignment.Bottom)`<br/>Android: `android:layout_gravity="left"`<br/>HarmonyOS: `.align(Alignment.Start)`<br/>Android: `android:layout_gravity="right"`<br/>HarmonyOS: `.align(Alignment.End)`<br/>Android: `android:layout_gravity="center_horizontal"`<br/>HarmonyOS: `.align(Alignment.Center)`<br/>Android: `android:layout_gravity="center_vertical"`<br/>HarmonyOS: `.align(Alignment.Center)` |

---

#### 2.3.2 FrameLayout 属性映射统计

| 映射类型 | 数量 | 占比 |
|---------|------|------|
| 直接映射 | 0 | ~0% |
| 需类型转换 | 1 | ~6% |
| 需组合实现 | 14 | ~88% |
| 无直接对应 | 1 | ~6% |
| **总计** | **16** | **100%** |

---

### 2.4 网格与表格布局

| Android 组件 | 类名 | HarmonyOS 组件 | 替代方案 | 说明 |
|-------------|------|---------------|---------|------|
| GridLayout | `android.widget.GridLayout` | `GridRow` + `GridCol` | 栅格系统 | 网格布局 |
| TableLayout | `android.widget.TableLayout` | `Grid` | 自定义表格结构 | 表格布局 |
| GridView | `android.widget.GridView` | `Grid` + `LazyForEach` | 高性能网格 | 网格视图（已废弃） |

---

#### 2.4.1 GridLayout → GridRow/GridCol 属性映射

**栅格结构属性**

| Android XML | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `android:columnCount` | `columnsTemplate` | int → template string | Android: `android:columnCount="3"`<br/>HarmonyOS: `GridRow({ columnsTemplate: '1fr 1fr 1fr' })` |
| `android:rowCount` | 无直接对应 | int → 自动计算 | Android: `android:rowCount="2"`<br/>HarmonyOS: 自动根据 GridRow 数量计算 |
| `android:orientation` | 无直接对应 | enum → 布局方向 | Android: `android:orientation="horizontal"`<br/>HarmonyOS: 使用`GridRow/GridCol` 嵌套结构 |
| `android:useDefaultMargins` | 无直接对应 | boolean → 需自定义实现 | Android: `android:useDefaultMargins="true"`<br/>HarmonyOS: 需自定义实现 |
| `android:alignmentMode` | 无直接对应 | enum → 需自定义实现 | Android: `android:alignmentMode="alignBounds"`<br/>HarmonyOS: 需自定义实现 |
| `android:columnOrderPreserved` | 无直接对应 | boolean → 需自定义实现 | Android: `android:columnOrderPreserved="true"`<br/>HarmonyOS: 需自定义实现 |
| `android:rowOrderPreserved` | 无直接对应 | boolean → 需自定义实现 | Android: `android:rowOrderPreserved="true"`<br/>HarmonyOS: 需自定义实现 |

**子组件单元格位置属性**

| Android XML | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `android:layout_column` | 无直接对应 | int → GridCol 位置 | Android: `android:layout_column="1"`<br/>HarmonyOS: 通过`GridCol` 位置确定 |
| `android:layout_row` | 无直接对应 | int → GridRow 位置 | Android: `android:layout_row="1"`<br/>HarmonyOS: 通过`GridRow` 位置确定 |

**子组件单元格跨度属性**

| Android XML | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `android:layout_columnSpan` | `span` | int → number | Android: `android:layout_columnSpan="2"`<br/>HarmonyOS: `GridCol({ span: 2 })` |
| `android:layout_rowSpan` | 无直接对应 | int → 需嵌套 GridRow | Android: `android:layout_rowSpan="2"`<br/>HarmonyOS: 需嵌套`GridRow` 实现 |

**子组件单元格权重属性**

| Android XML | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `android:layout_columnWeight` | 无直接对应 | float → 百分比 | Android: `android:layout_columnWeight="1"`<br/>HarmonyOS: `GridCol().width('33.3%')` |
| `android:layout_rowWeight` | 无直接对应 | float → 百分比 | Android: `android:layout_rowWeight="1"`<br/>HarmonyOS: `GridRow().height('50%')` |

**子组件单元格重力属性**

| Android XML | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `android:layout_gravity` | `.align()` / `.justify()` | flags → Alignment | Android: `android:layout_gravity="center"`<br/>HarmonyOS: `.align(Alignment.Center)`<br/>Android: `android:layout_gravity="top"`<br/>HarmonyOS: `.align(Alignment.Top)`<br/>Android: `android:layout_gravity="bottom"`<br/>HarmonyOS: `.align(Alignment.Bottom)`<br/>Android: `android:layout_gravity="left"`<br/>HarmonyOS: `.align(Alignment.Start)`<br/>Android: `android:layout_gravity="right"`<br/>HarmonyOS: `.align(Alignment.End)`<br/>Android: `android:layout_gravity="center_horizontal"`<br/>HarmonyOS: `.align(Alignment.Center)`<br/>Android: `android:layout_gravity="center_vertical"`<br/>HarmonyOS: `.align(Alignment.Center)` |

---

#### 2.4.2 GridLayout 属性映射统计

| 映射类型 | 数量 | 占比 |
|---------|------|------|
| 直接映射 | 2 | ~10% |
| 需类型转换 | 4 | ~20% |
| 需组合实现 | 10 | ~50% |
| 无直接对应 | 4 | ~20% |
| **总计** | **20** | **100%** |

---

### 2.5 约束布局 (ConstraintLayout)

| Android 组件 | 类名 | HarmonyOS 组件 | 替代方案 | 说明 |
|-------------|------|---------------|---------|------|
| ConstraintLayout | `androidx.constraintlayout.widget.ConstraintLayout` | `RelativeContainer` | 部分对应 | 约束布局 |
| ConstraintSet | `androidx.constraintlayout.widget.ConstraintSet` | 自定义状态管理 | 动态配置 | 约束集合 |
| Guideline | `androidx.constraintlayout.widget.Guideline` | 暂无直接对应 | 辅助 Absolute 定位 | 辅助线 |
| Barrier | `androidx.constraintlayout.widget.Barrier` | 暂无直接对应 | 手动计算位置 | 屏障 |
| Group | `androidx.constraintlayout.widget.Group` | 暂无直接对应 | 批量操作 | 组件组 |
| Placeholder | `androidx.constraintlayout.widget.Placeholder` | 暂无直接对应 | 动态替换 | 占位符 |
| Layer | `androidx.constraintlayout.helper.widget.Layer` | `Stack` | 组合其他容器 | 图层 |
| Flow | `androidx.constraintlayout.helper.widget.Flow` | `Flex` | 流式布局 | 流式布局辅助 |
| Grid | `androidx.constraintlayout.helper.widget.Grid` | `GridRow` + `GridCol` | 栅格系统 | 网格辅助 |
| Carousel | `androidx.constraintlayout.helper.widget.Carousel` | `Swiper` | 轮播容器 | 轮播辅助 |
| MotionLayout | `androidx.constraintlayout.motion.motion.widget.MotionLayout` | 动画 API 组合 | animateTo + transition | 动画布局 |

---

#### 2.5.1 ConstraintLayout → RelativeContainer 属性映射

**容器级别属性**

| Android XML | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `android:gravity` | 无直接对应 | flags → 需自定义实现 | Android: `android:gravity="center"`<br/>HarmonyOS: 需自定义实现 |

**子组件相对父容器定位属性**

| Android XML | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `android:layout_constraintTop_toTopOf` | `.alignRules()` | reference → alignRules | Android: `android:layout_constraintTop_toTopOf="@id/sibling"`<br/>HarmonyOS: `.alignRules({ anchor: 'sibling', align: VerticalAlign.Top })` |
| `android:layout_constraintBottom_toBottomOf` | `.alignRules()` | reference → alignRules | Android: `android:layout_constraintBottom_toBottomOf="@id/sibling"`<br/>HarmonyOS: `.alignRules({ anchor: 'sibling', align: VerticalAlign.Bottom })` |
| `android:layout_constraintStart_toStartOf` | `.alignRules()` | reference → alignRules | Android: `android:layout_constraintStart_toStartOf="@id/sibling"`<br/>HarmonyOS: `.alignRules({ anchor: 'sibling', align: HorizontalAlign.Start })` |
| `android:layout_constraintEnd_toEndOf` | `.alignRules()` | reference → alignRules | Android: `android:layout_constraintEnd_toEndOf="@id/sibling"`<br/>HarmonyOS: `.alignRules({ anchor: 'sibling', align: HorizontalAlign.End })` |
| `android:layout_constraintLeft_toLeftOf` | `.alignRules()`()` | reference → alignRules | Android: `android:layout_constraintLeft_toLeftOf="@id/sibling"`<br/>HarmonyOS: `.alignRules({ anchor: 'sibling', align: HorizontalAlign.Start })` |
| `android:layout_constraintRight_toRightOf` | `.alignRules()` | reference → alignRules | Android: `android:layout_constraintRight_toRightOf="@id/sibling"`<br/>HarmonyOS: `.alignRules({ anchor: 'sibling', align: HorizontalAlign.End })` |

**子组件相对父容器对齐属性**

| Android XML | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `android:layout_constraintTop_toTopOf="parent"` | `.alignRules()` | parent → __container__ | Android: `android:layout_constraintTop_toTopOf="parent"`<br/>HarmonyOS: `.alignRules({ anchor: '__container__', align: VerticalAlign.Top })` |
| `android:layout_constraintBottom_toBottomOf="parent"` | `.alignRules()` | parent → __container__ | Android: `android:layout_constraintBottom_toBottomOf="parent"`<br/>HarmonyOS: `.alignRules({ anchor: '__container__', align: VerticalAlign.Bottom })` |
| `android:layout_constraintStart_toStartOf="parent"` | `.alignRules()` | parent → __container__ | Android: `android:layout_constraintStart_toStartOf="parent"`<br/>HarmonyOS: `.alignRules({ anchor: '__container__', align: HorizontalAlign.Start })` |
| `android:layout_constraintEnd_toEndOf="parent"` | `.alignRules()` | parent → __container__ | Android: `android:layout_constraintEnd_toEndOf="parent"`<br/>HarmonyOS: `.alignRules({ anchor: '__container__', align: HorizontalAlign.End })` |
| `android:layout_constraintLeft_toLeftOf="parent"` | `.alignRules()` | parent → __container__ | Android: `android:layout_constraintLeft_toLeftOf="parent"`<br/>HarmonyOS: `.alignRules({ anchor: '__container__', align: HorizontalAlign.Start })` |
| `android:layout_constraintRight_toRightOf="parent"` | `.alignRules()` | parent → __container__ | Android: `android:layout_constraintRight_toRightOf="parent"`<br/>HarmonyOS: `.alignRules({ anchor: '__container__', align: HorizontalAlign.End })` |

**子组件居中属性**

| Android XML | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `android:layout_constraintStart_toStartOf="parent"` + `android:layout_constraintEnd_toEndOf="parent"` | `.alignRules()` | 双约束 → 居中 | Android: 双边约束<br/>HarmonyOS: `.alignRules({ anchor: '__container__', align: HorizontalAlign.Center })` |
| `android:layout_constraintTop_toTopOf="parent"` + `android:layout_constraintBottom_toBottomOf="parent"` | `.alignRules()` | 双约束 → 居中 | Android: 双边约束<br/>HarmonyOS: `.alignRules({ anchor: '__container__', align: VerticalAlign.Center })` |
| `android:layout_centerInParent="true"` | `.alignRules()` | boolean → 居中 | Android: `android:layout_centerInParent="true"`<br/>HarmonyOS: `.alignRules({ anchor: '__container__', align: Alignment.Center })` |

**子组件尺寸约束属性**

| Android XML | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `android:layout_constraintWidth_default` | 无直接对应 | enum → 需自定义实现 | Android: `android:layout_constraintWidth_default="spread"`<br/>HarmonyOS: 需自定义实现 |
| `android:layout_constraintHeight_default` | 无直接对应 | enum → 需自定义实现 | Android: `android:layout_constraintHeight_default="spread"`<br/>HarmonyOS: 需自定义实现 |
| `android:layout_constraintWidth_min` | `.constraintSize()` | dimension → minWidth | Android: `android:layout_constraintWidth_min="100dp"`<br/>HarmonyOS: `.constraintSize({ minWidth: 100 })` |
| `android:layout_constraintHeight_min` | `.constraintSize()` | dimension → minHeight | Android: `android:layout_constraintHeight_min="100dp"`<br/>HarmonyOS: `.constraintSize({ minHeight: 100 })` |
| `android:layout_constraintWidth_max` | `.constraintSize()` | dimension → maxWidth | Android: `android:layout_constraintWidth_max="200dp"`<br/>HarmonyOS: `.constraintSize({ maxWidth: 200 })` |
| `android:layout_constraintHeight_max` | `.constraintSize()` | dimension → maxHeight | Android: `android:layout_constraintHeight_max="200dp"`<br/>HarmonyOS: `.constraintSize({ maxHeight: 200 })` |
| `android:layout_constraintWidth_percent` | `.width()` | float → 百分比 | Android: `android:layout_constraintWidth_percent="0.5"`<br/>HarmonyOS: `.width('50%')` |
| `android:layout_constraintHeight_percent` | `.height()` | float → 百分比 | Android: `android:layout_constraintHeight_percent="0.5"`<br/>HarmonyOS: `.height('50%')` |
| `android:layout_constraintDimensionRatio` | 无直接对应 | string → 需自定义实现 | Android: `android:layout_constraintDimensionRatio="16:9"`<br/>HarmonyOS: 需自定义实现 |

**偏置属性**

| Android XML | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `android:layout_constraintHorizontal_bias` | 无直接对应 | float → 需自定义实现 | Android: `android:layout_constraintHorizontal_bias="0.5"`<br/>HarmonyOS: 需自定义实现 |
| `android:layout_constraintVertical_bias` | 无直接对应 | float → 需自定义实现 | Android: `android:layout_constraintVertical_bias="0.5"`<br/>HarmonyOS: 需自定义实现 |

**链式布局属性**

| Android XML | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `android:layout_constraintHorizontal_chainStyle` | 无直接对应 | enum → 需自定义实现 | Android: `android:layout_constraintHorizontal_chainStyle="spread"`<br/>HarmonyOS: 需自定义实现 |
| `android:layout_constraintVertical_chainStyle` | 无直接对应 | enum → 需自定义实现 | Android: `android:layout_constraintVertical_chainStyle="spread"`<br/>HarmonyOS: 需自定义实现 |
| `android:layout_constraintHorizontal_weight` | `.layoutWeight()` | float → number | Android: `android:layout_constraintHorizontal_weight="1"`<br/>HarmonyOS: `.layoutWeight(1)` |
| `android:layout_constraintVertical_weight` | `.layoutWeight()` | float → number | Android: `android:layout_constraintVertical_weight="1"`<br/>HarmonyOS: `.layoutWeight(1)` |

**圆形定位属性**

| Android XML | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `android:layout_constraintCircle` | 无直接对应 | reference → 需自定义实现 | Android: `android:layout_constraintCircle="@id/center"`<br/>HarmonyOS: 需自定义实现 |
| `android:layout_constraintCircleRadius` | 无直接对应 | dimension → 需自定义实现 | Android: `android:layout_constraintCircleRadius="100dp"`<br/>HarmonyOS: 需自定义实现 |
| `android:layout_constraintCircleAngle` | 无直接对应 | float → 需自定义实现 | Android: `android:layout_constraintCircleAngle="45"`<br/>HarmonyOS: 需自定义实现 |

---

#### 2.5.2 ConstraintLayout 辅助组件属性映射

**Guideline 属性**

| Android XML | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `android:orientation` | 无直接对应 | enum → 需自定义实现 | Android: `android:orientation="horizontal"`<br/>HarmonyOS: 需自定义实现 |
| `android:layout_constraintGuide_begin` | 无直接对应 | dimension → 需自定义实现 | Android: `android:layout_constraintGuide_begin="100dp"`<br/>HarmonyOS: 需自定义实现 |
| `android:layout_constraintGuide_end` | 无直接对应 | dimension → 需自定义实现 | Android: `android:layout_constraintGuide_end="100dp"`<br/>HarmonyOS: 需自定义实现 |
| `android:layout_constraintGuide_percent` | 无直接对应 | float → 需自定义实现 | Android: `android:layout_constraintGuide_percent="0.5"`<br/>HarmonyOS: 需自定义实现 |

**Barrier 属性**

| Android XML | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `android:id` | `.id()` | reference → string | Android: `android:id="@+id/barrier"`<br/>HarmonyOS: `.id('barrier')` |
| `app:barrierDirection` | 无直接对应 | enum → 需自定义实现 | Android: `app:barrierDirection="top"`<br/>HarmonyOS: 需自定义实现 |
| `app:constraint_referenced_ids` | 无直接对应 | id list → 需自定义实现 | Android: `app:constraint_referenced_ids="@id/view1,@id/view2"`<br/>HarmonyOS: 需自定义实现 |

**Group 属性**

| Android XML | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `android:id` | `.id()` | reference) → string | Android: `android:id="@+id/group"`<br/>HarmonyOS: `.id('group')` |
| `app:constraint_referenced_ids` | 无直接对应 | id list → 需自定义实现 | Android: `app:constraint_referenced_ids="@id/view1,@id/view2"`<br/>HarmonyOS: 需自定义实现 |
| `android:visibility` | `.visibility()` | enum → Visibility | Android: `android:visibility="gone"`<br/>HarmonyOS: `.visibility(Visibility.None)` |
| `android:elevation` | `.shadow()` | dimension → shadow | Android: `android:elevation="8dp"`<br/>HarmonyOS: `.shadow({ radius: 8 })` |

**Placeholder 属性**

| Android XML | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `android:id` | `.id()` | reference → string | Android: `android:id="@+id/placeholder"`<br/>HarmonyOS: `.id('placeholder')` |
| `android:content` | 无直接对应 | reference → 需自定义实现 | Android: `android:content="@id/view"`<br/>HarmonyOS: 需自定义实现 |
| `android:emptyVisibility` | `.visibility()` | enum → Visibility | Android: `android:emptyVisibility="gone"`<br/>HarmonyOS: `.visibility(Visibility.None)` |

**Layer 属性**

| Android XML | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `android:id` | `.id()` | reference → string | Android: `android:id="@+id/layer"`<br/>HarmonyOS: `.id('layer')` |
| `app:constraint_referenced_ids` | 无直接对应 | id list → 需自定义实现 | Android: `app:constraint_referenced_ids="@id/view1,@id/view2"`<br/>HarmonyOS: 需自定义实现 |
| `android:rotation` | `.rotate()` | float → { angle: number } | Android: `android:rotation="45"`<br/>HarmonyOS: `.rotate({ angle: 45 })` |
| `android:scaleX` | `.scale()` | float → { x: number } | Android: `android:scaleX="1.5"`<br/>HarmonyOS: `.scale({ x: 1.5 })` |
| `android:scaleY` | `.scale()` | float → { y: number } | Android: `android:scaleY="1.5"`<br/>HarmonyOS: `.scale({ y: 1.5 })` |
| `android:translationX` | `.translate()` | float → { x: number } | Android: `android:translationX="100"`<br/>HarmonyOS: `.translate({ x: 100 })` |
| `android:translationY` | `.translate()` | float → { y: number } | Android: `android:translationY="100"`<br/>HarmonyOS: `.translate({ y: 100 })` |

**Flow 属性**

| Android XML | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `android:id` | `.id()` | reference → string | Android: `android:id="@+id/flow"`<br/>HarmonyOS: `.id('flow')` |
| `app:constraint_referenced_ids` | 无直接对应 | id list → 需自定义实现 | Android: `app:constraint_referenced_ids="@id/view1,@id/view2"`<br/>HarmonyOS: 需自定义实现 |
| `app:flow_wrapMode` | 无直接对应 | enum → 需自定义实现 | Android: `app:flow_wrapMode="none"`<br/>HarmonyOS: 需自定义实现 |
| `app:flow_horizontalStyle` | 无直接对应 | enum → 需自定义实现 | Android: `app:flow_horizontalStyle="spread"`<br/>HarmonyOS: 需自定义实现 |
| `app:flow_verticalStyle` | 无直接对应 | enum → 需自定义实现 | Android: `app:flow_verticalStyle="spread"`<br/>HarmonyOS: 需自定义实现 |
| `app`flow_horizontalGap` | 无直接对应 | dimension → 需自定义实现 | Android: `app:flow_horizontalGap="8dp"`<br/>HarmonyOS: 需自定义实现 |
| `app:flow_verticalGap` | 无直接对应 | dimension → 需自定义实现 | Android: `app:flow_verticalGap="8dp"`<br/>HarmonyOS: 需自定义实现 |
| `app:flow_maxElementsWrap` | 无直接对应 | int → 需自定义实现 | Android: `app:flow_maxElementsWrap="3"`<br/>HarmonyOS: 需自定义实现 |
| `app:flow_firstHorizontalStyle` | 无直接对应 | enum → 需自定义实现 | Android: `app:flow_firstHorizontalStyle="spread"`<br/>HarmonyOS: 需自定义实现 |
| `app:flow_firstVerticalStyle` | 无直接对应 | enum → 需自定义实现 | Android: `app:flow_firstVerticalStyle="spread"`<br/>HarmonyOS: 需自定义实现 |
| `app:flow_lastHorizontalStyle` | 无直接对应 | enum → 需自定义实现 | Android: `app:flow_lastHorizontalStyle="spread"`<br/>HarmonyOS: 需自定义实现 |
| `app:flow_lastVerticalStyle` | 无直接对应 | enum → 需自定义实现 | Android: `app:flow_lastVerticalStyle="spread"`<br/>HarmonyOS: 需自定义实现 |

**Grid 辅助组件属性**

| Android XML | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `android:id` | `.id()` | reference → string | Android: `android:id="@+id/grid"`<br/>HarmonyOS: `.id('grid')` |
| `app:constraint_referenced_ids` | 无直接对应 | id list → 需自定义实现 | Android: `app:constraint_referenced_ids="@id/view1,@id/view2"`<br/>HarmonyOS: 需自定义实现 |
| `app:grid_columns` | 无直接对应 | int → 需自定义实现 | Android: `app:grid_columns="3"`<br/>HarmonyOS: 需自定义实现 |
| `app:grid_rows` | 无直接对应 | int → 需自定义实现 | Android: `app:grid_rows="2"`<br/>HarmonyOS: 需自定义实现 |
| `app:grid_columnWeights` | 无直接对应 | string → 需自定义实现 | Android: `app:grid_columnWeights="1,2,1"`<br/>HarmonyOS: 需自定义实现 |
| `app:grid_rowWeights` | 无直接对应 | string → 需自定义实现 | Android: `app:grid_rowWeights="1,2"`<br/>HarmonyOS: 需自定义实现 |
| `app:grid_horizontalGap` | 无直接对应 | dimension → 需自定义实现 | Android: `app:grid_horizontalGap="8dp"`<br/>HarmonyOS: 需自定义实现 |
| `app:grid_verticalGap` | 无直接对应 | dimension → 需自定义实现 | Android: `app:grid_verticalGap="8dp"`<br/>HarmonyOS: 需自定义实现) |
| `app:grid_useAsMeasurer` | 无直接对应 | boolean → 需自定义实现 | Android: `app:grid_useAsMeasurer="true"`<br/>HarmonyOS: 需自定义实现 |

**Carousel 辅助组件属性**

| Android XML | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `android:id` | `.id()` | reference → string | Android: `android:id="@+id/carousel"`<br/>HarmonyOS: `.id('carousel')` |
| `app:constraint_referenced_ids` | 无直接对应 | id list → 需自定义实现 | Android: `app:constraint_referenced_ids="@id/view1,@id/view2"`<br/>HarmonyOS: 需自定义实现 |
| `app:carousel_forwardDirection` | 无直接对应 | enum → 需自定义实现 | Android: `app:carousel_forwardDirection="horizontal"`<br/>HarmonyOS: 需自定义实现 |
| `app:carousel_infinite` | 无直接对应 | boolean → 需自定义实现 | Android: `app:carousel_infinite="true"`<br/>HarmonyOS: 需自定义实现 |
| `app:carousel_previousState` | 无直接对应 | enum → 需自定义实现 | Android: `app:carousel_previousState="first"`<br/>HarmonyOS: 需自定义实现 |
| `app:carousel_nextState` | 无直接对应 | enum) → 需自定义实现 | Android: `app:carousel_nextState="last"`<br/>HarmonyOS: 需自定义实现 |

**MotionLayout 属性**

| Android XML | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|
| `android:layoutDescription` | 无直接对应 | reference → 需自定义实现 | Android: `android:layoutDescription="@xml/motion_scene"`<br/>HarmonyOS: 需自定义实现 |
| `app:showPaths` | 无直接对应 | boolean → 需自定义实现 | Android: `app:showPaths="true"`<br/>HarmonyOS: 需自定义实现 |
| `app:progress` | 无直接对应 | float → 需自定义实现 | Android: `app:progress="0.5"`<br/>HarmonyOS: 需自定义实现 |
| `app:applyMotionScene` | 无直接对应 | boolean → 需自定义实现 | Android: `app:applyMotionScene="true"`<br/>HarmonyOS: 需自定义实现 |

---

#### 2.5.3 ConstraintLayout 属性映射统计

| 映射类型 | 数量 | 占比 |
|---------|------|------|
| 直接映射 | 5 | ~5% |
| 需类型转换 | 15 | ~15% |
| 需组合实现 | 80 | ~80% |
| 无直接对应 | 0 | ~0% |
| **总计** | **100** | **100%** |

---

### 2.6 弹性布局

| Android 组件 | 类名 | HarmonyOS 组件 | 替代方案 | 说明 |
|-------------|------|---------------|---------|------|
| FlexboxLayout | `com.google.android.flexbox.FlexboxLayout` | `Flex` | 直接映射 | 弹性盒子布局 |

---

#### 2.6.1 FlexboxLayout → Flex 属性映射

**容器级别 Flex 属性**

| Android XML | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|---------|
| `app:flexDirection` | `.direction()` | enum → FlexDirection | Android: `app:flexDirection="row"`<br/>HarmonyOS: `Flex({ direction: FlexDirection.Row })` |
| `app:flexDirection="column"` | `.direction()` | enum → FlexDirection | Android: `app:flexDirection="column"`<br/>HarmonyOS: `Flex({ direction: FlexDirection.Column })` |
| `app:flexDirection="row_reverse"` | `.direction()` | enum → FlexDirection | Android: `app:flexDirection="row_reverse"`<br/>HarmonyOS: `Flex({ direction: FlexDirection.RowReverse })` |
| `app:flexDirection="column_reverse"` | `.direction()` | enum → {direction: FlexDirection.ColumnReverse}` | Android: `app:flexDirection="column_reverse"`<br/>HarmonyOS: `Flex({ direction: FlexDirection.ColumnReverse })` |

**容器对齐属性**

| Android XML | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|---------|
| `app:justifyContent` | `.justifyContent()` | flags → FlexAlign | Android: `app:justifyContent="flex_start"`<br/>HarmonyOS: `Flex({ justifyContent: FlexAlign.Start })` |
| `app:justifyContent="flex_end"` | `.justifyContent()` | flags → FlexAlign | Android: `app:justifyContent="flex_end"`<br/>HarmonyOS: `Flex({ justifyContent: FlexAlign.End })` |
| `app:justifyContent="center"` | `.justifyContent()` | flags → FlexAlign | Android: `app:justifyContent="center"`<br/>HarmonyOS: `Flex({ justifyContent: FlexAlign.Center })` |
| `app:justifyContent="space_between"` | `.justifyContent()` | flags → FlexAlign | Android: `app:justifyContent="space_between"`<br/>HarmonyOS: `Flex({ justifyContent: FlexAlign.SpaceBetween })` |
| `app:justifyContent="space_around"` | `.justifyContent()` | flags → FlexAlign | Android: `app:justifyContent="space_around"`<br/>HarmonyOS: `Flex({ justifyContent: FlexAlign.SpaceAround })` |
| `app:justifyContent="space_evenly"` | `.justifyContent()` | flags → FlexAlign | Android: `app:justifyContent="space_evenly"`<br/>HarmonyOS: `Flex({ justifyContent: FlexAlign.SpaceEvenly })` |

**子组件对齐属性**

| Android XML | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|---------|---------|
| `app:alignItems` | `.alignItems()` | enum → ItemAlign | Android: `app:alignItems="flex_start"`<br/>HarmonyOS: `Flex({ alignItems: ItemAlign.Start })` |
| `app:alignItems="flex_end"` | `.alignItems()` | enum → ItemAlign | Android: `app:alignItems="flex_end"`<br/>HarmonyOS: `Flex({ alignItems: ItemAlign.End })` |
| `app:alignItems="center"` | `.alignItems()` | flags → ItemAlign | Android: `app:alignItems="center"`<br/>HarmonyOS: `Flex({ alignItems: ItemAlign.Center })` |
| `app:alignItems="baseline"` | `.alignItems()` | enum → ItemAlign | Android: `app:alignItems="baseline"`<br/>HarmonyOS: `Flex({ alignItems: ItemAlign.Baseline })` |
| `app:alignItems="stretch"` | `.alignItems()` | flags → ItemAlign | Android: `app:alignItems="stretch"`<br/>HarmonyOS: `Flex({ alignItems: ItemAlign.Stretch })` |

**行内对齐属性**

| Android XML | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|---------|---------|
| `app:alignContent` | `.alignContent()` | flags → FlexAlign | Android: `app:alignContent="flex_start"`<br/>HarmonyOS: `Flex({ alignContent: FlexAlign.Start })` |
| `app:alignContent="flex_end"` | `.alignContent()` | flags → FlexAlign | Android: `app:alignContent="flex_end"`<br/>HarmonyOS: `Flex({ alignContent: FlexAlign.End })` |
| `app:alignContent="center"` | `.alignContent()` | flags → FlexAlign | Android: `app:alignContent="center"`<br/>HarmonyOS: `Flex({ alignContent: FlexAlign.Center })` |
| `app:alignContent="space_between"` | `.alignContent()` | flags → FlexAlign | Android: `app:alignContent="space_between"`<br/>HarmonyOS: `Flex({ alignContent: FlexAlign.SpaceBetween })` |
| `app:alignContent="space_around"` | `.alignContent()` | flags → FlexAlign | Android: `app:alignContent="space_around"`<br/>HarmonyOS: `Flex({ alignContent: FlexAlign.SpaceAround })` |
| `app:alignContent="space_evenly"` | `.alignContent()` | flags → FlexAlign | Android: `app:alignContent="space_evenly"`<br/>HarmonyOS: `Flex({ alignContent: FlexAlign.SpaceEvenly })` |

**换行属性**

| Android XML | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|---------|---------|
| `app:flexWrap` | `.wrap()` | enum → FlexWrap | Android: `app:flexWrap="nowrap"`<br/>HarmonyOS: `Flex({ wrap: FlexWrap.NoWrap })` |
| `app:flexWrap="wrap"` | `.wrap()` | enum → FlexWrap | Android: `app:flexWrap="wrap"`<br/>HarmonyOS: `Flex({ wrap: FlexWrap.Wrap })` |
| `app:flexWrap="wrap_reverse"` | `.wrap()` | enum → FlexWrap | Android: `app:flexWrap="wrap_reverse"`<br/>HarmonyOS: `Flex({ wrap: FlexWrap.WrapReverse })` |

---

#### 2.6.2 FlexboxLayout 子组件布局属性映射

**Flex Item 属性**

| Android XML | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|---------|---------|
| `app:layout_flexGrow` | `.flexGrow()` | float → number | Android: `app:layout_flexGrow="1"`<br/>HarmonyOS: `.flexGrow(1)` |
| `app:layout_flexShrink` | `.flexShrink()` | float → number | Android: `app:layout_flexShrink="1"`<br/>HarmonyOS: `.flexShrink(1)` |
| `app:layout_flexBasisPercent` | `.flexBasis()` | float → 百分比 | Android: `app:layout_flexBasisPercent="50%"`<br/>HarmonyOS: `.flexBasis('50%')` |
| `app:layout_flexBasis` | dimension | 固定大小 | Android: `app:layout_flexBasis="100dp"`<br/>HarmonyOS: `.flexBasis(100)` |

**对齐属性**

| Android XML | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|---------|---------|---------|
| `app:layout_alignSelf` | `.alignSelf()` | enum → ItemAlign | Android: `app:layout_alignSelf="auto"`<br/>HarmonyOS: `.alignSelf(ItemAlign.Auto)` |
| `app:layout_alignSelf="flex_start"` | `.alignSelf()` | enum → ItemAlign | Android: `app:layout_alignSelf="flex_start"`<br/>HarmonyOS: `.alignSelf(ItemAlign.Start)` |
| `app:layout_alignSelf="flex_end"` | `.alignSelf()` | enum → ItemAlign | Android: `app:layout_alignSelf="flex_end"`<br/>HarmonyOS: `.alignSelf(ItemAlign.End)` |
| `app:layout_alignSelf="center"` | `.alignSelf()` | enum → ItemAlign | Android: `app:layout_alignSelf="center"`<br/>HarmonyOS: `.alignSelf(ItemAlign.Center)` |
| `app:layout_alignSelf="baseline"` | `.alignSelf()` | enum → ItemAlign | Android: `app:layout_alignSelf="baseline"`<br/>HarmonyOS: `.alignSelf(ItemAlign.Baseline)` |
| `app:layout_alignSelf="stretch"` | `.alignSelf()` | enum → ItemAlign | Android: `app:layout_alignSelf="stretch"`<br/>HarmonyOS: `.alignSelf(ItemAlign.Stretch)` |

**重力属性**

| Android XML | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|---------|---------|---------|
| `android:layout_gravity` | `.align()` / `.justify()` | flags → Alignment | Android: `android:layout_gravity="center"`<br/>HarmonyOS: `.align(Alignment.Center)`<br/>Android: `android:layout_gravity="center_horizontal"`<br/>HarmonyOS: `.alignItems(HorizontalAlign.Center)`<br/>Android: `android:layout_gravity="center_vertical"`<br/>HarmonyOS: `.justifyContent(FlexAlign.Center)`<br/>Android: `android:layout_gravity="left"`<br/>HarmonyOS: `.alignItems(VerticalAlign.Top)`<br/>Android: `android:layout_gravity="right"``<br/>HarmonyOS: `.alignItems(VerticalAlign.Bottom)`<br/>Android: `android:layout_gravity="center_horizontal"`<br/>HarmonyOS: `.alignItems(HorizontalAlign.Center)`<br/>Android: `android:layout_gravity="start"`<br/>HarmonyOS: `.alignItems(HorizontalAlign.Start)`<br/>Android: `android:layout_gravity="end"`<br/>HarmonyOS: `.alignItems(HorizontalAlign.End)`<br/>Android: `android:layout_gravity="center_vertical"`<br/>HarmonyOS: `.justifyContent(FlexAlign.Center)`<br/>Android: `android:layout_gravity="left"`<br/>HarmonyOS: `.alignItems(VerticalAlign.Top)`<br/>Android: `android:layout_gravity="right"`<br/>HarmonyOS: `.alignItems(VerticalAlign.Bottom)`<br/>Android: `android:layout_gravity="center_horizontal"`<br/>HarmonyOS: `.alignItems(HorizontalAlign.Center)`<br/>Android: `android:layout_gravity="start"`<br/>HarmonyOS: `.alignItems(HorizontalAlign.Start)`<br/>Android: `android:layout_gravity="end"`<br/>HarmonyOS: `.alignItems(VerticalAlign.Bottom)`<br/>Android: `android:layout_gravity="center_vertical"`<br/>HarmonyOS: `.align(Alignment.Center)`<br/>Android: `android:layout_gravity="left"`<br/>HarmonyOS: `.alignItems(VerticalAlign.Top)`<br/>Android: `android:layout_gravity="right"`<br/>HarmonyOS: `.alignItems(VerticalAlign.End)`<br/>Android: `android:layout_gravity="start"`<br/>HarmonyOS: `.alignItems(VerticalAlign.Start)`<br/>Android: `android:layout_gravity="end"`<br/>HarmonyOS: `.alignItems(VerticalAlign.End)`<br/>Android: `android:layout_gravity="center_vertical"`<br/>HarmonyOS: `.align(Alignment.Center)`<```

---

#### 2.6.3 FlexboxLayout 程序化方法映射

| Android 方法 | HarmonyOS 属性 | 类型转换 | 代码示例 |
|-------------|---------------|---------|---------|---------|---------|
| `setFlexDirection(int)` | 无直接对应 | int → 组件选择 | Android: `flexboxLayout.setFlexDirection(LinearLayout.VERTICAL)`<br/>HarmonyOS: 使用 `Column` 或 `Row` 组件 |
| `getFlexDirection()` | 无直接对应 | void → 组件判断 | Android: `int orientation = flexboxLayout.getFlexDirection()`<br/>HarmonyOS: 根据组件类型判断 |
| `setGravity(int)` | `.justifyContent()` / `.alignItems()` | int → FlexAlign | Android: `flexboxLayout.setGravity(Gravity.CENTER)`<br/>HarmonyOS: `Flex().justifyContent(FlexAlign.Center).alignItems(HorizontalAlign.Center)` |

---

#### 2.6.4 FlexboxLayout 属性映射统计

| 映射类型 | 数量 | 占比 |
|---------|------|------|------|
| 直接映射 | 6 | ~15% |
| 需类型转换 | 4 | ~25% |
| 需组合实现 | 8 | ~50% |
| 无直接对应 | 5 | ~14% |
| **总计** | **23** | **100%** |

---

### 2.7 协调布局

| Android 组件 | 类名 | HarmonyOS 组件 | 替代方案 | 说明 |
|-------------|------|---------------|---------|------|
| CoordinatorLayout | `androidx.coordinatorlayout.widget.CoordinatorLayout` | 自定义组合 | 需业务实现 | 协调布局 |
| AppBarLayout | `com.google.android.material.appbar.AppBarLayout` | 自定义组合 | Column + 手势 | 应用栏布局 |
| CollapsingToolbarLayout | `com.google.android.material.appbar.CollapsingToolbarLayout` | 自定义组合 | Column + 动画 | 折叠工具栏布局 |

### 2.8 抽屉布局

| Android 组件 | 类名 | HarmonyOS 组件 | 替代方案 | 说明 |
|-------------|------|---------------|---------|------|
| DrawerLayout | `androidx.drawerlayout.widget.DrawerLayout` | `Sheet` / 自定义 | 侧滑抽屉 | 抽屉布局 |
| SlidingPaneLayout | `androidx.slidingpanelayout.widget.SlidingPaneLayout` | 自定义组合 | Panel + 动画 | 滑动面板布局 |

### 2.9 刷新布局

| Android 组件 | 类名 | HarmonyOS 组件 | 替代方案 | 说明 |
|-------------|------|---------------|---------|------|
| SwipeRefreshLayout | `androidx.swiperefreshlayout.widget.SwipeRefreshLayout` | `Refresh` | 直接映射 | 下拉刷新布局 |

---

## 三、列表与适配器组件映射

### 3.1 列表视图

| Android 组件 | 类名 | HarmonyOS 组件 | 替代方案 | 说明 |
|-------------|------|---------------|---------|------|
| ListView | `android.widget.ListView` | `List` | 高性能列表 | 列表视图（已废弃） |
| ExpandableListView | `android.widget.ExpandableListView` | `List` + `ListItemGroup` | 配合展开逻辑 | 可展开列表视图 |
| ListPopupWindow | `android.widget.ListPopupWindow` | `Popup` + `List` | 组合实现 | 列表弹出窗口 |

### 3.2 RecyclerView 系列

| Android 组件 | 类名 | HarmonyOS 组件 | 替代方案 | 说明 |
|-------------|------|---------------|---------|------|
| RecyclerView | `androidx.recyclerview.widget.RecyclerView` | `List` | 配合 LazyForEach | 高性能列表视图 |
| RecyclerView.Adapter | `androidx.recyclerview.widget.RecyclerView.Adapter` | `LazyForEach` | 数据源管理 | 列表适配器 |
| RecyclerView.ViewHolder | `androidx.recyclerview.widget.RecyclerView.ViewHolder` | `ListItem` | 列表项组件 | 列表项持有者 |
| LinearLayoutManager | `androidx.recyclerview.widget.LinearLayoutManager` | `List` | listDirection 配置 | 线性布局管理器 |
| GridLayoutManager | `androidx.recyclerview.widget.GridLayoutManager` | `Grid` | 网格布局 | 网格布局管理器 |
| StaggeredGridLayoutManager | `androidx.recyclerview.widget.StaggeredGridLayoutManager` | `WaterFlow` | 瀑布流布局 | 瀑布流布局管理器 |
| ItemTouchHelper | `androidx.recyclerview.widget.ItemTouchHelper` | 拖拽 API | Drag + Drop | 列表项触摸辅助 |
| SnapHelper | `androidx.recyclerview.widget.SnapHelper` | 自定义对齐逻辑 | 手势实现 | 对齐辅助 |
| LinearSnapHelper | `androidx.recyclerview.widget.LinearSnapHelper` | 自定义对齐逻辑 | Swiper 配合 | 线性对齐辅助 |
| PagerSnapHelper | `androidx.recyclerview.widget.PagerSnapHelper` | `Swiper` | 轮播容器 | 分页对齐辅助 |

### 3.3 适配器视图基类

| Android 组件 | 类名 | HarmonyOS 组件 | 替代方案 | 说明 |
|-------------|------|---------------|---------|------|
| AdapterView | `android.widget.AdapterView` | 基础架构概念 | 适配器视图基类 | 适配器视图基类 |
| AdapterViewAnimator | `android.widget.AdapterViewAnimator` | 自定义动画组件 | transition | 适配器视图动画器 |
| AdapterViewFlipper | `android.widget.AdapterViewFlipper` | `Swiper` | 轮播切换 | 适配器视图翻转器 |
| StackView | `android.widget.StackView` | `Stack` | 堆叠布局 | 堆栈视图 |

---

## 四、切换与翻页组件映射

| Android 组件 | 类名 | HarmonyOS 组件 | 替代方案 | 说明 |
|-------------|------|---------------|---------|------|
| ViewPager | `androidx.viewpager.widget.ViewPager` | `Swiper` | 轮播容器 | 页面切换器（已废弃） |
| ViewPager2 | `androidx.viewpager2.widget.ViewPager2` | `Swiper` | 轮播容器 | 页面切换器 |
| TabHost | `android.widget.TabHost` | `Tabs` + `TabContent` | 已废弃 | 标签页主机（已废弃） |
| TabWidget | `android.widget.TabWidget` | `Tabs` | 已废弃 | 标签页组件（已废弃） |
| ViewFlipper | `android.widget.ViewFlipper` | `Swiper` | 轮播切换 | 视图翻转器 |
| ViewSwitcher | `android.widget.ViewSwitcher` | `Swiper` | 轮播切换 | 视图切换器 |
| ImageSwitcher | `android.widget.ImageSwitcher` | `Swiper` + `Image` | 配合 Image | 图片切换器 |
| TextSwitcher | `android.widget.TextSwitcher` | `Swiper` + `Text` | 配合 Text | 文本切换器 |

---

## 五、Material Design 组件映射

### 5.1 Material 按钮

| Android 组件 | 类名 | HarmonyOS 组件 | 替代方案 | 说明 |
|-------------|------|---------------|---------|------|
| MaterialButton | `com.google.android.material.button.MaterialButton` | `Button` | 配置样式 | Material 按钮 |
| IconButton | `com.google.android.material.button.MaterialButton` | `Button` + 图标 | 组合实现 | 图标按钮 |
| SplitButton | `com.google.android.material.button.MaterialButtonGroup` | `Row` + 2个 `Button` | 组合实现 | 分割按钮 |
| ToggleButton | `com.google.android.material.button.MaterialButtonToggleGroup` | `RadioContainer` | 配合 Radio | 切换按钮组 |

### 5.2 Material 文本输入

| Android 组件 | 类名 | HarmonyOS 组件 | 替代方案 | 说明 |
|-------------|------|---------------|---------|------|
| TextInputLayout | `com.google.android.material.textfield.TextInputLayout` | `Column` + `TextInput` + 样式 | 组合实现 | 文本输入布局 |
| TextInputEditText | `com.google.android.material.textfield.TextInputEditText` | `TextInput` | 配置样式 | 文本输入框 |
| ExposedDropdownMenu | `com.google.android.material.textfield.MaterialAutoCompleteTextView` | `Select` | 下拉选择 | 暴露下拉菜单 |

### 5.3 Material 卡片

| Android 组件 | 类名 | HarmonyOS 组件 | 替代方案 | 说明 |
|-------------|------|---------------|---------|------|
| CardView | `androidx.cardview.widget.CardView` | `Column` + 样式 | borderRadius + shadow | 卡片视图 |
| MaterialCardView | `com.google.android.material.card.MaterialCardView` | `Column` + 样式 | borderRadius + shadow | Material 卡片 |

### 5.4 Material 底部组件

| Android 组件 | 类名 | HarmonyOS 组件 | 替代方案 | 说明 |
|-------------|------|---------------|---------|------|
| BottomNavigationView | `com.google.android.material.bottomnavigation.BottomNavigationView` | `Tabs` | 配合路由 | 底部导航 |
| BottomSheetDialog | `com.google.android.material.bottomsheet.BottomSheetDialog` | `Sheet` | 底部抽屉 | 底部抽屉对话框 |
| BottomSheetDialogFragment | `com.google.android.material.bottomsheet.BottomSheetDialogFragment` | `Sheet` | 配合路由 | 底部抽屉片段 |
| BottomSheetBehavior | `com.google.android.material.bottomsheet.BottomSheetBehavior` | `Sheet` | 配置行为 | 底部抽屉行为 |

### 5.5 Material 导航组件

| Android 组件 | 类名 | HarmonyOS 组件 | 替代方案 | 说明 |
|-------------|------|---------------|---------|------|
| NavigationView | `com.google.android.material.navigation.NavigationView` | 自定义组合 | Column + 列表 | 导航视图 |
| NavigationRailView | `com.google.android.material.navigationrail.NavigationRailView` | 自定义组合 | Column + 垂直列表 | 导航栏 |
| TabLayout | `com.google.android.material.tabs.TabLayout` | `Tabs` | 直接映射 | 标签页布局 |
| TabItem | `com.google.android.material.tabs.TabItem` | `TabContent` | 配合 Tabs | 标签页项 |

### 5.6 Material 浮动组件

| Android 组件 | 类名 | HarmonyOS 组件 | 替代方案 | 说明 |
|-------------|------|---------------|---------|------|
| FloatingActionButton | `com.google.android.material.floatingactionbutton.FloatingActionButton` | `Button` + 样式 | 圆形 + 阴影 | 浮动操作按钮 |
| ExtendedFloatingActionButton | `com.google.android.material.floatingactionbutton.ExtendedFloatingActionButton` | `Button` + 样式 | 长按钮 | 扩展浮动按钮 |
| SpeedDial | `com.google.android.material.floatingactionbutton.FloatingActionButton` | 自定义组合 | 多个 FAB | 快捷拨号（组合实现） |

### 5.7 Material 对话框

| Android 组件 | 类名 | HarmonyOS 组件 | 替代方案 | 说明 |
|-------------|------|---------------|---------|------|
| AlertDialog | `androidx.appcompat.app.AlertDialog` | `AlertDialog` | 直接映射 | 警告对话框 |
| MaterialAlertDialogBuilder | `com.google.android.material.dialog.MaterialAlertDialogBuilder` | `AlertDialog` | 配置 Material 样式 | Material 对话框构建器 |
| DatePickerDialog | `android.app.DatePickerDialog` | `DatePickerDialog` | 直接映射 | 日期选择对话框 |
| TimePickerDialog | `android.app.TimePickerDialog` | `TimePickerDialog` | 直接映射 | 时间选择对话框 |
| ProgressDialog | `android.app.ProgressDialog` | `LoadingDialog` | 已废弃 | 进度对话框（已废弃） |

### 5.8 Material 提示组件

| Android 组件 | 类名 | HarmonyOS 组件 | 替代方案 | 说明 |
|-------------|------|---------------|---------|------|
| Snackbar | `com.google.android.material.snackbar.Snackbar` | 自定义组合 | Toast + 样式 | 快速提示条 |
| Toast | `android.widget.Toast` | `prompt.showToast()` | API 调用 | 吐司提示 |
| Tooltip | `com.google.android.material.tooltip.TooltipDrawable` | 暂无直接对应 | 自定义 Popup | 工具提示 |

### 5.9 Material 菜单组件

| Android 组件 | 类名 | HarmonyOS 组件 | 替代方案 | 说明 |
|-------------|------|---------------|---------|------|
| PopupMenu | `android.widget.PopupMenu` | `Menu` / `BindMenu` | 直接映射 | 弹出菜单 |
| PopupWindow | `android.widget.PopupWindow` | `Popup` | 直接映射 | 弹出窗口 |
| DropdownMenu | `com.google.android.material.menu.MaterialMenuView` | `Select` | 下拉选择 | 下拉菜单 |

### 5.10 Material 进度指示器

| Android 组件 | 类名 | HarmonyOS 组件 | 替代方案 | 说明 |
|-------------|------|---------------|---------|------|
| CircularProgressIndicator | `com.google.android.material.progressindicator.CircularProgressIndicator` | `Progress` (type: CircularProgressType) | 配置类型 | 圆形进度指示器 |
| LinearProgressIndicator | `com.google.android.material.progressindicator.LinearProgressIndicator` | `Progress` | 配置类型 | 线性进度指示器 |

### 5.11 Material 滑块与范围

| Android 组件 | 类名 | HarmonyOS 组件 | 替代方案 | 说明 |
|-------------|------|---------------|---------|------|
| Slider | `com.google.android.material.slider.Slider` | `Slider` | 直接映射 | 滑块 |
| RangeSlider | `com.google.android.material.slider.RangeSlider` | 暂无直接对应 | 自定义双 Slider | 范围滑块 |

### 5.12 Material Chips

| Android 组件 | 类名 | HarmonyOS 组件 | 替代方案 | 说明 |
|-------------|------|---------------|---------|------|
| Chip | `com.google.android.material.chip.Chip` | 自定义组合 | Row + 样式 | 芯片标签 |
| ChipGroup | `com.google.android.material.chip.ChipGroup` | `CheckboxGroup` / `Flex` | 配合 Chip | 芯片组 |
| ChipDrawable | `com.google.android.material.chip.ChipDrawable` | 自定义样式 | @Styles | 芯片绘制 |

### 5.13 Material 顶部应用栏

| Android 组件 | 类名 | HarmonyOS 组件 | 替代方案 | 说明 |
|-------------|------|---------------|---------|------|
| Toolbar | `androidx.appcompat.widget.Toolbar` | 自定义组合 | Row + 按钮 | 工具栏 |
| MaterialToolbar | `com.google.android.material.appbar.MaterialToolbar` | 自定义组合 | Row + 样式 | Material 工具栏 |
| SearchBar | `com.google.android.material.search.SearchBar` | `Search` | 配置样式 | 搜索栏 |
| SearchView | `com.google.android.material.search.SearchView` | `Search` | 配置样式 | 搜索视图 |

### 5.14 Material 骨架屏

| Android 组件 | 类名 | HarmonyOS 组件 | 替代方案 | 说明 |
|-------------|------|---------------|---------|------|
| ShimmerFrameLayout | `com.facebook.shimmer.ShimmerFrameLayout` | 暂无直接对应 | 自定义动画 | 骨架屏动画（Facebook） |
| SkeletonLayout | 第三方库 | 暂无直接对应 | 自定义加载占位 | 骨架屏布局 |

---

## 六、Jetpack Compose 组件映射

### 6.1 Compose 基础组件

| Android Compose | 函数名 | HarmonyOS 组件 | 替代方案 | 说明 |
|----------------|--------|---------------|---------|------|
| Text | `Text()` | `Text` | 直接映射 | 文本显示 |
| TextField | `TextField()` / `OutlinedTextField()` | `TextInput` | 配置样式 | 文本输入框 |
| BasicTextField | `BasicTextField()` | `TextInput` | 基础配置 | 基础文本输入 |
| Button | `Button()` | `Button` | 直接映射 | 按钮 |
| IconButton | `IconButton()` | `Button` + 图标 | 组合实现 | 图标按钮 |
| Icon | `Icon()` | `SymbolGlyph` / `Image` | 系统图标或图片 | 图标 |
| Image | `Image()` | `Image` | 直接映射 | 图片 |
| Checkbox | `Checkbox()` | `Checkbox` | 直接映射 | 复选框 |
| RadioButton | `RadioButton()` | `Radio` | 配合容器 | 单选按钮 |
| Switch | `Switch()` | `Toggle` (Switch) | 直接映射 | 开关 |
| Slider | `Slider()` | `Slider` | 直接映射 | 滑块 |
| RangeSlider | `RangeSlider()` | 暂无直接对应 | 自定义双 Slider | 范围滑块 |

### 6.2 Compose 布局组件

| Android Compose | 函数名 | HarmonyOS 组件 | 替代方案 | 说明 |
|----------------|--------|---------------|---------|------|
| Column | `Column()` | `Column` | 直接映射 | 垂直线性布局 |
| Row | `Row()` | `Row` | 直接映射 | 水平线性布局 |
| Box | `Box()` | `Stack` | 直接映射 | 堆叠布局 |
| ConstraintLayout | `ConstraintLayout()` | `RelativeContainer` | 部分对应 | 约束布局 |
| FlowRow | `FlowRow()` | `Flex` (direction: Row) | 流式行布局 | 流式行布局 |
| FlowColumn | `FlowColumn()` | `Flex` (direction: Column) | 流式列布局 | 流式列布局 |
| LazyColumn | `LazyColumn()` | `List` (listDirection: Axis.Vertical) | 配合 LazyForEach | 懒加载垂直列表 |
| LazyRow | `LazyRow()` | `List` (listDirection: Axis.Horizontal) | 配合 LazyForEach | 懒加载水平列表 |
| LazyVerticalGrid | `LazyVerticalGrid()` | `Grid` + LazyForEach | 网格懒加载 | 懒加载垂直网格 |
| LazyHorizontalGrid | `LazyHorizontalGrid()` | `Grid` + LazyForEach | 网格懒加载 | 懒加载水平网格 |
| GridLayout | `GridLayout()` | `GridRow` + `GridCol` | 栅格系统 | 网格布局 |

### 6.3 Compose Material 3 组件

| Android Compose | 函数名 | HarmonyOS 组件 | 替代方案 | 说明 |
|----------------|--------|---------------|---------|------|
| Card | `Card()` / `ElevatedCard()` / `OutlinedCard()` | `Column` + 样式 | 卡片 |
| FloatingActionButton | `FloatingActionButton()` / `ExtendedFloatingActionButton()` | `Button` + 样式 | 浮动按钮 |
| Chip | `Chip()` / `InputChip()` / `FilterChip()` / `SuggestionChip()` | 自定义组合 | Row + 样式 | 芯片 |
| NavigationBar | `NavigationBar()` | `Tabs` | 配合路由 | 底部导航栏 |
| NavigationRail | `NavigationRail()` | 自定义组合 | 垂直导航 | 侧边导航栏 |
| NavigationDrawer | `ModalNavigationDrawer()` | `Sheet` / 自定义 | 导航抽屉 | 模态导航抽屉 |
| TabRow | `TabRow()` / `ScrollableTabRow()` | `Tabs` | 直接映射 | 标签页行 |
| BottomSheet | `BottomSheetScaffold()` | `Sheet` | 直接映射 | 底部抽屉 |
| Snackbar | `Snackbar()` / `SnackbarHost()` | 自定义组合 | Toast + 样式 | 快速提示 |
| TopAppBar | `TopAppBar()` / `CenterAlignedTopAppBar()` / `MediumTopAppBar()` / `LargeTopAppBar()` | 自定义组合 | Row + 样式 | 顶部应用栏 |
| AlertDialog | `AlertDialog()` | `AlertDialog` | 直接映射 | 警告对话框 |
| DatePicker | `DatePicker()` | `DatePicker` | 直接映射 | 日期选择器 |
| ProgressIndicator | `CircularProgressIndicator()` / `LinearProgressIndicator()` | `Progress` | 配置类型 | 进度指示器 |
| PullRefresh | `PullRefreshIndicator()` | `Refresh` | 直接映射 | 下拉刷新 |
| SwipeToDismiss | `SwipeToDismiss()` | 暂无直接对应 | 拖拽 API + 状态 | 滑动删除 |

### 6.4 Compose 动画组件

| Android Compose | 函数名 | HarmonyOS 组件 | 替代方案 | 说明 |
|----------------|--------|---------------|---------|------|
| AnimatedVisibility | `AnimatedVisibility()` | `transition` + `animateTo` | 动画可见性 |
| AnimatedContent | `AnimatedContent()` | `transition` + `animateTo` | 动画内容切换 |
| Crossfade | `Crossfade()` | `animateTo` (opacity) | 淡入淡出 |
| animateAsState | `animate*AsState()` | `animateTo` | 状态动画 |
| AnimatedValue | `animateFloatAsState()` 等 | `animateTo` | 值动画 |

---

## 七、特殊视图组件映射

### 7.1 网页视图

| Android 组件 | 类名 | HarmonyOS 组件 | 替代方案 | 说明 |
|-------------|------|---------------|---------|------|
| WebView | `android.webkit.WebView` | `Web` | 直接映射 | 网页视图 |

### 7.2 表面视图

| Android 组件 | 类名 | HarmonyOS 组件 | 替代方案 | 说明 |
|-------------|------|---------------|---------|------|
| SurfaceView | `android.view.SurfaceView` | `XComponent` | OpenGL 渲染 | 表面视图（独立绘图线程） |
| TextureView | `android.view.TextureView` | `XComponent` | 原生渲染 | 纹理视图（支持动画变换） |
| GLSurfaceView | `android.opengl.GLSurfaceView` | `XComponent` | OpenGL 渲染 | OpenGL 表面视图 |

### 7.3 自定义组件

| Android 组件 | 类名 | HarmonyOS 组件 | 替代方案 | 说明 |
|-------------|------|---------------|---------|------|
| View | `android.view.View` | `@ComponentV2`（V2）/ `@Component`（V1） | 自定义组件 | 视图基类 |
| ViewGroup | `android.view.ViewGroup` | 容器组件 | Row/Column/Stack 等 | 视图组基类 |

### 7.4 通知组件

| Android 组件 | 类名 | HarmonyOS 组件 | 替代方案 | 说明 |
|-------------|------|---------------|---------|------|
| RemoteViews | `android.widget.RemoteViews` | 暂无直接对应 | 通知 API | 远程视图（用于通知、桌面小部件） |
| AppWidgetHostView | `android.appwidget.AppWidgetHostView` | 暂无直接对应 | 桌面小部件 API | 应用小部件宿主视图 |

---

## 八、辅助组件映射

### 8.1 视图辅助

| Android 组件 | 类名 | HarmonyOS 组件 | 替代方案 | 说明 |
|-------------|------|---------------|---------|------|
| ViewStub | `android.view.ViewStub` | 暂无直接对应 | 条件渲染 + Lazy | 延迟加载视图 |
| Space | `android.widget.Space` | `Row`/`Column` 空子项 | 布局技巧 | 空白占位 |
| ViewOutlineProvider | `android.view.ViewOutlineProvider` | 暂无直接对应 | clipShape API | 视图轮廓提供者 |

### 8.2 手势组件

| Android 组件 | 类名 | HarmonyOS 组件 | 替代方案 | 说明 |
|-------------|------|---------------|---------|------|
| GestureDetector | `android.view.GestureDetector` | 手势 API 组合 | TapGesture/PanGesture 等 | 手势检测器 |
| ScaleGestureDetector | `android.view.ScaleGestureDetector` | `PinchGesture` | 直接映射 | 缩放手势检测器 |

---

## 九、布局属性映射（API 20/21）

### 9.1 尺寸属性

| Android XML | HarmonyOS | 说明 | 代码示例对比 |
|-------------|-----------|------|-------------|
| layout_width | width | 宽度 | Android: `android:layout_width="100dp"`<br/>HarmonyOS: `Component().width(100)` |
| layout_height | height | 高度 | Android: `android:layout_height="match_parent"`<br/>HarmonyOS: `Component().height('100%')` |
| minWidth | constraintSize({ minWidth: value }) | 最小宽度 | Android: `android:minWidth="100dp"`<br/>HarmonyOS: `Component().constraintSize({ minWidth: 100 })` |
| maxWidth | constraintSize({ maxWidth: value }) | 最大宽度 | Android: `android:maxWidth="200dp"`<br/>HarmonyOS: `Component().constraintSize({ maxWidth: 200 })` |
| minHeight | constraintSize({ minHeight: value }) | 最小高度 | Android: `android:minHeight="50dp"`<br/>HarmonyOS: `Component().constraintSize({ minHeight: 50 })` |
| maxHeight | constraintSize({ maxHeight: value }) | 最大高度 | Android: `android:maxHeight="300dp"`<br/>HarmonyOS: `Component().constraintSize({ maxHeight: 300 })` |
| layout_weight | layoutWeight | 布局权重 | Android: `android:layout_weight="1"`<br/>HarmonyOS: `Component().layoutWeight(1)` |

### 9.2 边距与内边距

| Android XML | HarmonyOS | 说明 | 代码示例对比 |
|-------------|-----------|------|-------------|
| layout_margin | margin | 外边距 | Android: `android:layout_margin="10dp"`<br/>HarmonyOS: `Component().margin(10)` |
| layout_marginTop | margin({ top: value }) | 上边距 | Android: `android:layout_marginTop="10dp"`<br/>HarmonyOS: `Component().margin({ top: 10 })` |
| layout_marginBottom | margin({ bottom: value }) | 下边距 | Android: `android:layout_marginBottom="10dp"`<br/>HarmonyOS: `Component().margin({ bottom: 10 })` |
| layout_marginLeft | margin({ left: value }) | 左边距 | Android: `android:layout_marginLeft="10dp"`<br/>HarmonyOS: `Component().margin({ left: 10 })` |
| layout_marginRight | margin({ right: value }) | 右边距 | Android: `android:layout_marginRight="10dp"`<br/>HarmonyOS: `Component().margin({ right: 10 })` |
| layout_marginStart | margin({ start: value }) | 起始边距 | Android: `android:layout_marginStart="10dp"`<br/>HarmonyOS: `Component().margin({ start: 10 })` |
| layout_marginEnd | margin({ end: value }) | 结束边距 | Android: `android:layout_marginEnd="10dp"`<br/>HarmonyOS: `Component().margin({ end: 10 })` |
| padding | padding | 内边距 | Android: `android:padding="10dp"`<br/>HarmonyOS: `Component().padding(10)` |
| paddingTop | padding({ top: value }) | 上内边距 | Android: `android:paddingTop="10dp"`<br/>HarmonyOS: `Component().padding({ top: 10 })` |
| paddingBottom | padding({ bottom: value }) | 下内边距 | Android: `android:paddingBottom="10dp"`<br/>HarmonyOS: `Component().padding({ bottom: 10 })` |

### 9.3 对齐与权重

| Android XML | HarmonyOS | 说明 | 代码示例对比 |
|-------------|-----------|------|-------------|
| layout_gravity | align / alignSelf | 对齐方式 | Android: `android:layout_gravity="center"`<br/>HarmonyOS: `Component().align(Alignment.Center)` |
| gravity | textAlign | 文本对齐 | Android: `android:gravity="center"`<br/>HarmonyOS: `Text().textAlign(TextAlign.Center)` |
| layout_weight | layoutWeight | 权重 | Android: `android:layout_weight="1"`<br/>HarmonyOS: `Component().layoutWeight(1)` |

### 9.4 显示属性

| Android XML | HarmonyOS | 说明 | 代码示例对比 |
|-------------|-----------|------|-------------|
| visibility | visibility | 可见性 | Android: `android:visibility="gone"`<br/>HarmonyOS: `Component().visibility(Visibility.None)` |
| alpha | opacity | 透明度 | Android: `android:alpha="0.5"`<br/>HarmonyOS: `Component().opacity(0.5)` |
| background | backgroundColor | 背景色 | Android: `android:background="#FF0000FF"`<br/>HarmonyOS: `Component().backgroundColor('#FF0000FF')` |
| background | backgroundImage | 背景图 | Android: `android:background="@drawable/bg"`<br/>HarmonyOS: `Component().backgroundImage($r('app.media.bg'))` |
| foreground | 无直接对应 | 前景图 | Android: `android:foreground`<br/>HarmonyOS: 无直接对应，需组合实现 |

### 9.5 边框与圆角

| Android XML | HarmonyOS | 说明 | 代码示例对比 |
|-------------|-----------|------|-------------|
| elevation | shadow | 阴影效果 | Android: `android:elevation="10dp"`<br/>HarmonyOS: `Component().shadow({ radius: 10, color: '#80000000', offsetX: 0, offsetY: 5 })` |
| cardElevation | shadow | 卡片阴影 | Android: Material 卡片属性<br/>HarmonyOS: `Column().shadow({ radius: 8, color: '#30000000' })` |

### 9.6 变换属性

| Android XML | HarmonyOS | 说明 | 代码示例对比 |
|-------------|-----------|------|-------------|
| rotation | rotate | 旋转角度 | Android: `android:rotation="90"`<br/>HarmonyOS: `Component().rotate({ angle: 90 })` |
| scaleX / scaleY | scale({ x, y }) | 缩放 | Android: `android:scaleX="1.5"`<br/>HarmonyOS: `Component().scale({ x: 1.5, y: 1 })` |
| translationX / translationY | translate({ x, y }) | 平移 | Android: `android:translationX="100"`<br/>HarmonyOS: `Component().translate({ x: 100 })` |
| pivotX / pivotY | 无直接对应 | 旋转中心点 | Android: `android:pivotX="0.5"`<br/>HarmonyOS: 无直接对应 |

### 9.7 交互属性

| Android XML | HarmonyOS | 说明 | 代码示例对比 |
|-------------|-----------|------|-------------|
| clickable | enabled / enabled | 是否可点击 | Android: `android:clickable="true"`<br/>HarmonyOS: `Component().enabled(true)` |
| focusable | focusable | 是否可获取焦点 | Android: `android:focusable="true"`<br/>HarmonyOS: `Component().focusable(true)` |
| clickable | enabled / enabled | 是否可交互 | Android: `android:clickable="true"`<br/>HarmonyOS: `Component().enabled(true)` |

### 9.8 单位换算（API 20/21）

| Android | HarmonyOS | 换算关系 | 说明 |
|---------|-----------|---------|------|
| dp | vp | 密度无关像素 | Android: `16dp` ≈ HarmonyOS: `16vp` |
| sp | fp | 字体像素 | Android: `16sp` ≈ HarmonyOS: `16fp` |
| px | px | 像素 | Android: `16px` = HarmonyOS: `16px` |

---

## 十、未找到直接对应方案的 Android 组件

以下 Android 组件在 HarmonyOS ArkUI 中暂无直接对应组件，需要通过组合实现、自定义开发或使用特定 Kit 替代：

| Android 组件 | 类名 | HarmonyOS 替代方案 | 难度等级 | 说明 |
|-------------|------|------------------|---------|------|
| **ConstraintLayout 辅助组件** |  |  |  |  |
| Guideline | `androidx.constraintlayout.widget.Guideline` | 借助 Absolute 定位 | 中等 | 需手动计算和约束 |
| Barrier | `androidx.constraintlayout.widget.Barrier` | 手动计算位置 | 中等 | 需监听子组件尺寸变化 |
| Group | `androidx.constraintlayout.widget.Group` | 批量操作逻辑 | 简单 | 需要手动管理引用 |
| Placeholder | `androidx.constraintlayout.widget.Placeholder` | 动态替换 | 中等 | 需要状态管理 |
| **Material 3 特殊组件** |  |  |  |  |
| RangeSlider | `com.google.android.material.slider.RangeSlider` | 自定义双 Slider | 中等 | 需同步两个 Slider 状态 |
| ShimmerFrameLayout | `com.facebook.shimmer.ShimmerFrameLayout` | 自定义动画 | 简单 | 使用 animateTo + opacity |
| Tooltip | `com.google.android.material.tooltip.TooltipDrawable` | 自定义 Popup | 中等 | 长按触发 Popup |
| Chip | `com.google.android.material.chip.Chip` | 自定义组合 | 简单 | Row + 样式 + 点击逻辑 |
| **协调布局组件** |  |  |  |  |
| CoordinatorLayout | `androidx.coordinatorlayout.widget.CoordinatorLayout` | 自定义组合 | 困难 | 需要复杂的嵌套滚动协调 |
| AppBarLayout | `com.google.android.material.appbar.AppBarLayout` | 自定义组合 | 中等 | 需要滚动联动逻辑 |
| CollapsingToolbarLayout | `com.google.android.material.appbar.CollapsingToolbarLayout` | 自定义组合 | 困难 | 需要滚动高度计算 + 动画 |
| **抽屉布局** |  |  |  |  |
| DrawerLayout | `androidx.drawerlayout.widget.DrawerLayout` | Sheet / 自定义 | 中等 | 侧滑手势需要自定义 |
| SlidingPaneLayout | `androidx.slidingpanelayout.widget.SlidingPaneLayout` | 自定义组合 | 中等 | Panel + 动画 + 滑动手势 |
| **通知与小部件** |  |  |  |  |
| RemoteViews | `android.widget.RemoteViews` | 通知 Kit | 困难 | 桌面小部件暂不支持 |
| AppWidgetHostView | `android.appwidget.AppWidgetHostView` | 暂不支持 | 不可行 | HarmonyOS 没有桌面小部件系统 |
| **Jetpack Compose 特有** |  |  |  |  |
| SwipeToDismiss | `SwipeToDismiss()` | 拖拽 API + 状态 | 中等 | 需要配合 PanGesture + 状态管理 |
| **其他特殊组件** |  |  |  |  |
| DialerFilter | `android.widget.DialerFilter` | 自定义业务组件 | 中等 | 需要具体的拨号逻辑 |
| ViewStub | `android.view.ViewStub` | 条件渲染 + Lazy | 简单 | 使用 if/else + LazyForEach |
| ViewOutlineProvider | `android.view.ViewOutlineProvider` | clipShape API | 中等 | 使用通用属性中的裁剪 |
| MotionLayout | `androidx.constraintlayout.motion.widget.MotionLayout` | 动画 API 组合 | 困难 | animateTo + transition + 状态管理 |

---

## 十、映射方案总结

### 10.1 完全直接映射的组件（70+）

可以直接一对一替换的组件：
- 基础组件：Text、Button、Image、Checkbox、Radio、Slider、Rating 等
- 布局组件：Row、Column、Flex、Stack、Grid、List 等
- 选择器：DatePicker、TimePicker、CalendarPicker、Select 等
- 弹窗：AlertDialog、ActionSheet、LoadingDialog 等
- 功能组件：Web、Video、Search、Divider 等

### 10.2 需要组合实现的组件（50+）

需要通过多个 HarmonyOS 组件组合实现的 Android 组件：
- ImageButton → Button + Image
- ImageView 带文本 → Row + Image + Text
- Material 组件 → 容器组件 + 样式配置
- 复杂列表 → List + ListItemGroup + LazyForEach

### 10.3 需要自定义实现的组件（20+）

需要编写自定义逻辑或组件的 Android 组件：
- CoordinatorLayout 及相关 → 复杂滚动协调逻辑
- Material 特效组件 → 动画 API + 状态管理
- 通知/小部件 → 暂不支持，需替代方案
- ConstraintLayout 高级辅助 → 手动计算和约束

### 10.4 完全不支持的组件（5+）

在 HarmonyOS 中无法实现的 Android 组件：
- 桌面小部件系统 → HarmonyOS 架构不同
- 部分通知交互 → 通知 Kit 能力有限
- Material MotionLayout 部分功能 → 需要手动实现

---

## 十一、迁移建议

### 11.1 优先级排序

1. **高优先级**（完全支持）：基础 UI 组件、布局容器、列表组件
2. **中优先级**（部分支持）：Material 组件、复杂动画、自定义布局
3. **低优先级**（暂不支持）：小部件、高级动画、特殊交互

### 11.2 迁移策略

1. **渐进式迁移**：先迁移基础功能，再处理复杂交互
2. **组件降级**：Material 组件可降级为基础组件 + 样式
3. **功能替代**：无直接对应的组件用功能相似的组合替代
4. **自定义开发**：关键但缺失的组件需要自定义实现

### 11.3 注意事项

1. HarmonyOS 声明式 UI 与 Android 命令式 UI 有本质区别
2. 状态管理是 HarmonyOS 的核心，需熟练掌握 V2 装饰器（`@Local / @Param + @Once / @Event / @Provider() / @Consumer() / @ObservedV2 + @Trace / @Monitor / AppStorageV2 / PersistenceV2`，API 12+ 推荐）；老项目使用 V1 装饰器（`@State / @Prop / @Link / @Provide / @Consume / @Observed + @ObjectLink / @Watch / @StorageLink / PersistentStorage`）
3. 布局参数从 XML 属性改为链式调用，语法差异较大
4. 事件处理从监听器改为回调函数，编程范式不同
5. 部分高级功能（如 MotionLayout、小部件）需要重新设计架构

---

## 参考链接

1. **Android UI 组件全量清单**: `/docs/android-ui-components-full-list.md`
2. **HarmonyOS ArkUI 组件全量清单**: `/docs/harmonyos-arkui-components-full-list.md`
3. **HarmonyOS 开发者文档**: https://developer.huawei.com/consumer/cn/doc/harmonyos-guides/
4. **Android UI 组件总览**: https://developer.android.com/develop/ui
5. **Material Design 3 规范**: https://m3.material.io/components

---

*本文档基于 Android 14 / Material Design 3 和 HarmonyOS NEXT API 20/21 (6.0.0/6.0.1) 整理，具体 API 以官方最新文档为准。*
