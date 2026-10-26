# Known Compile Error Patterns

> **This file is auto-maintained by `a2h-retrospect`.**
> Manual edits are allowed but may be overwritten when retrospect detects updated patterns.
> Last updated: 2026-03-27

---

## Pattern Index

| # | Error Code / Type | Frequency | Short Description |
|---|-------------------|-----------|-------------------|
| 1 | arkts-identifiers-as-prop-names | 85 | ValuesBucket computed property name |
| 2 | type mismatch (EventData) | 16 | EventData double type cast |
| 3 | arkts-no-untyped-obj-literals | 9 | Untyped object literal |
| 4 | type mismatch (promptAction) | 8 | promptAction button color type |
| 5 | type error (@Param / @Prop) | 3 | @Param (V2) / @Prop (V1) naming conflict |

---

## 1. ValuesBucket Computed Property Name

- **Date**: 2026-03-27
- **Error code**: `arkts-identifiers-as-prop-names`
- **Frequency**: 85 occurrences
- **Source**: AntennaPod V1 migration (a2h-retrospect-report-2026-03-27)

**Error code**:
```typescript
const bucket: ValuesBucket = {
  [ColumnName.TITLE]: title,   // ERROR: computed property name not allowed
  [ColumnName.URL]: url,
};
```

**Correct code**:
```typescript
const bucket: ValuesBucket = {};
bucket[ColumnName.TITLE] = title;
bucket[ColumnName.URL] = url;
```

**Rule**: ArkTS forbids computed property names (`[expr]: value`) in object literals. Build the object first, then assign properties via bracket notation.

---

## 2. EventData Double Type Cast

- **Date**: 2026-03-27
- **Error code**: type mismatch
- **Frequency**: 16 occurrences
- **Source**: AntennaPod V1 migration (a2h-retrospect-report-2026-03-27)

**Error code**:
```typescript
emitter.on({ eventId: 1 }, (data: emitter.EventData) => {
  const value = data.data?.['key'] as string;  // ERROR: data.data is optional Record, direct cast fails
});
```

**Correct code**:
```typescript
emitter.on({ eventId: 1 }, (data: emitter.EventData) => {
  const raw = data.data as Record<string, Object>;
  const value = raw['key'] as string;
});
```

**Rule**: `EventData.data` is typed `Record<string, Object> | undefined`. Access requires two steps: (1) cast to `Record<string, Object>`, (2) cast the extracted value to the target type.

---

## 3. Untyped Object Literal

- **Date**: 2026-03-27
- **Error code**: `arkts-no-untyped-obj-literals`
- **Frequency**: 9 occurrences
- **Source**: AntennaPod V1 migration (a2h-retrospect-report-2026-03-27)

**Error code**:
```typescript
const options = {
  title: 'Hello',
  message: 'World',
};  // ERROR: object literal without explicit type annotation
```

**Correct code**:
```typescript
interface DialogOptions {
  title: string;
  message: string;
}
const options: DialogOptions = {
  title: 'Hello',
  message: 'World',
};
```

**Rule**: ArkTS requires all object literals to have an explicit type. Define an `interface` or `class` and annotate the variable.

---

## 4. promptAction Button Color Type

- **Date**: 2026-03-27
- **Error code**: type mismatch
- **Frequency**: 8 occurrences
- **Source**: AntennaPod V1 migration (a2h-retrospect-report-2026-03-27)

**Error code**:
```typescript
promptAction.showDialog({
  buttons: [
    { text: 'OK', color: '#ff0000' }   // ERROR: color expects ResourceColor, not string
  ]
});
```

**Correct code**:
```typescript
promptAction.showDialog({
  buttons: [
    { text: 'OK', color: Color.Red }
  ]
});
// Or use $r('app.color.xxx') for resource reference
```

**Rule**: `promptAction.showDialog` button `color` property expects `ResourceColor` type (Color enum or `$r()` resource reference), not a raw hex string.

---

## 5. @Param / @Prop Naming Conflict

- **Date**: 2026-03-27
- **Error code**: type error
- **Frequency**: 3 occurrences
- **Source**: AntennaPod V1 migration (a2h-retrospect-report-2026-03-27)

**Error code** (V2 — project-locked V2):
```typescript
@ComponentV2
struct MyComponent {
  @Param @Once title: string = '';   // ERROR: 'title' conflicts with built-in component property
}
```

**Correct code** (V2):
```typescript
@ComponentV2
struct MyComponent {
  @Param @Once itemTitle: string = '';   // Renamed to avoid conflict
}
```

**Rule**: Certain property names (`title`, `content`, `action`, etc.) conflict with built-in component attributes. Prefix with a domain-specific qualifier (e.g., `itemTitle`, `feedTitle`). Same rule applies to V1 `@Prop` and V2 `@Param`/`@Local`/`@Event` (see also `arkts-component-builder/references/v2-prop-naming-rules.md`).
