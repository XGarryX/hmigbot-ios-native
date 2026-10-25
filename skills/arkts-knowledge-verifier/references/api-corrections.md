# API Corrections

> **This file is auto-maintained by `a2h-retrospect`.**
> Manual edits are allowed but may be overwritten when retrospect detects updated corrections.
> Last updated: 2026-03-27

---

## Correction Index

| # | Category | Error | Correction |
|---|----------|-------|------------|
| 1 | Import Path | `@ohos.*` imports | `@kit.XxxKit` imports |
| 2 | API Name | `ShowActionMenuSuccessResponse` | `ActionMenuSuccessResponse` |
| 3 | API Name | `DialogSuccessResponse` / `ShowDialogResponse` | `ShowDialogSuccessResponse` |

---

## 1. @ohos Import Path Deprecation

- **Date**: 2026-03-27
- **Category**: Import path
- **Source**: AntennaPod V1 migration (a2h-retrospect-report-2026-03-27)

**Error code**:
```typescript
import rdb from '@ohos.data.relationalStore';
import http from '@ohos.net.http';
import fileIo from '@ohos.file.fs';
```

**Correct code**:
```typescript
import { relationalStore } from '@kit.ArkData';
import { http } from '@kit.NetworkKit';
import { fileIo } from '@kit.CoreFileKit';
```

**Rule**: All `@ohos.*` import paths are deprecated since API 11. Use the corresponding `@kit.XxxKit` bundle import instead. Common mappings:

| Deprecated `@ohos.*` | Replacement `@kit.*` |
|----------------------|---------------------|
| `@ohos.data.relationalStore` | `@kit.ArkData` |
| `@ohos.data.preferences` | `@kit.ArkData` |
| `@ohos.net.http` | `@kit.NetworkKit` |
| `@ohos.file.fs` | `@kit.CoreFileKit` |
| `@ohos.promptAction` | `@kit.ArkUI` |
| `@ohos.router` | `@kit.ArkUI` |
| `@ohos.multimedia.media` | `@kit.MediaKit` |
| `@ohos.backgroundTaskManager` | `@kit.BackgroundTasksKit` |
| `@ohos.request` | `@kit.BasicServicesKit` |
| `@ohos.xml` | `@kit.ArkTS` |

---

## 2. promptAction API Name: ShowActionMenuSuccessResponse

- **Date**: 2026-03-27
- **Category**: API name
- **Source**: AntennaPod V1 migration (a2h-retrospect-report-2026-03-27)

**Error code**:
```typescript
import { promptAction } from '@kit.ArkUI';

promptAction.showActionMenu({...}).then((result: promptAction.ShowActionMenuSuccessResponse) => {
  // ERROR: ShowActionMenuSuccessResponse does not exist
});
```

**Correct code**:
```typescript
import { promptAction } from '@kit.ArkUI';

promptAction.showActionMenu({...}).then((result: promptAction.ActionMenuSuccessResponse) => {
  // Correct type name
});
```

**Rule**: The response type for `promptAction.showActionMenu()` is `ActionMenuSuccessResponse`, not `ShowActionMenuSuccessResponse` — for **this specific API** the `Show` prefix is dropped from the type name.

> ⚠️ **Do NOT over-generalize this to a "Show prefix is always dropped" rule.** The sibling API `promptAction.showDialog()` is the opposite: its response type **keeps** the prefix — `ShowDialogSuccessResponse`. So `showActionMenu → ActionMenuSuccessResponse` (no `Show`) but `showDialog → ShowDialogSuccessResponse` (with `Show`). The two `promptAction` APIs are **inconsistently named**; verify each one, never infer from the other. See §3.

---

## 3. promptAction API Name: ShowDialogSuccessResponse

- **Category**: API name
- **Source**: harmony-docs `@ohos.promptAction (弹窗).md` — `showDialog(options: ShowDialogOptions): Promise<ShowDialogSuccessResponse>`

**Correct code**:
```typescript
import { promptAction } from '@kit.ArkUI';

promptAction.showDialog({...}).then((result: promptAction.ShowDialogSuccessResponse) => {
  // result.index = index of the clicked button in the buttons[] array
});
```

**Rule**: The response type for `promptAction.showDialog()` is **`ShowDialogSuccessResponse`** — the `Show` prefix **is** part of the type name (it keeps `ShowDialog`). Do **not** shorten it to `DialogSuccessResponse` or `ShowDialogResponse`.

**Contrast with §2 — the two sibling APIs are named inconsistently, so decide per-API, never infer one from the other:**

| API | Correct response type | `Show` prefix? |
|-----|----------------------|----------------|
| `promptAction.showActionMenu()` | `ActionMenuSuccessResponse` | dropped (no `Show`) |
| `promptAction.showDialog()` | `ShowDialogSuccessResponse` | kept (`Show` present) |
