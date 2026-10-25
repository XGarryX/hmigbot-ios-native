# iOS → HarmonyOS atomic component mapping

Use actual source types, actions, modifiers and resource evidence. The graph's class field must name a real declared/framework type or an explicit analysis marker; do not create SDK types by renaming another platform's widgets.

| Native source | Target candidate | Required semantic check |
|---|---|---|
| SwiftUI Text / UIKit UILabel | Text / Span | Localization, attributed runs, links, line limits, truncation, dynamic type and accessibility |
| TextField / SecureField; UITextField / UITextView | TextInput / TextArea | Binding, secure entry, keyboard/content type, submit, validation, selection, focus, multiline and error timing |
| SwiftUI Button / UIButton / UIAction | Button or interactive composed control | Real handler, enabled/loading state, repeat/cancel behavior and hit region |
| SwiftUI Image / UIImageView / SF Symbol usage | Image / SymbolGlyph or an explicit asset replacement | Asset scale, rendering mode, intrinsic/layout size, aspect policy, tint and variant. Symbol names are not portable identifiers |
| Toggle / UISwitch | Toggle | Binding owner, async rejection, persistence and disabled state |
| Picker / UISegmentedControl / UIPickerView | Select / Tabs / composed selector | Identity, selected value, options source, unavailable values, focus and callback timing |
| Slider / UISlider | Slider | Value range, step, tracking vs commit, formatting and side effects |
| ProgressView / UIProgressView / UIActivityIndicatorView | Progress / LoadingProgress | Determinate vs indeterminate, cancellation and actual completion |
| DatePicker / UIDatePicker | DatePicker / TimePicker candidate | Calendar, locale, time zone, range, optionality and commit/cancel |
| Menu / UIMenu / UIContextMenuInteraction | Menu / bindMenu / composed popup | Context, destructive/disabled states, actions and dismissal |
| Map / MKMapView; WKWebView; AVPlayer-backed view | A verified target Kit / Web / media implementation | Use platform domain skills and actual SDK contracts; a placeholder is not a completed capability |

## Attributes and state

Graph style/behavior/accessibility attributes are normalized evidence slots, not source API spelling. Keep font/attributed text, accessibility label/value/hint/traits/order, enabled/selected/hidden state and conditional absence distinct. Hidden and removed nodes have different layout, focus and lifecycle effects.

SwiftUI explicit .id, ForEach key, accessibilityIdentifier, restorationIdentifier and IB object ID have distinct semantics. Record their kind and anchors. Canonical analysis IDs are not runtime identities.

New target components follow the original V2-first policy in arkts-component-builder and arkts-state-manager. Do not change existing V1 components solely to satisfy this mapping. A generated component still requires the original compilation and behavior checks.

## Font size and scaling

Apple's [Fonts overview](https://developer.apple.com/documentation/technologyoverviews/fonts) distinguishes fixed `Font.system(size:)` / `UIFont.systemFont(ofSize:)` from semantic text styles. Preserve that distinction for text and SF Symbol uses. Inspect actual source values and modifiers: `@ScaledMetric`, `UIFontMetrics`, custom-font `fixedSize` / `relativeTo`, and source Dynamic Type settings can change the effective scaling; a numeric argument alone is not proof of fixed behavior.

ArkUI `Text.fontSize` and `SymbolGlyph.fontSize` use fp for bare numbers. When the source is fixed, retain its system-font scaling behavior with the supported local `minFontScale` / `maxFontScale` controls or an explicitly verified unit mapping; do not lock semantic fonts globally. Resource font values can remain fp: the consuming component's scaling contract still matters.

Source `minimumScaleFactor` describes shrink-to-fit behavior, which is separate from system font scaling. ArkUI `minFontSize` / `maxFontSize` are size bounds, not `minFontScale` / `maxFontScale`; verify both contracts independently against the actual component API. `Image` has no `fontSize` attribute: preserve image geometry through its supported size/aspect properties.
