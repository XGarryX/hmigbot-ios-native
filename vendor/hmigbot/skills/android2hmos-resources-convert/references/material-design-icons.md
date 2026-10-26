# Material Design Icon Download and Integration

When Android source code uses Material Design `imageVector` (such as `Icons.Outlined.Home`) to reference icons, you need to download the corresponding SVG from Google Fonts and integrate it into the HarmonyOS project.

---

## Complete Workflow

### 1. Identify Icon References in Android Source Code

Search for icon definition files in the Android source code (usually enum classes or sealed classes) to identify two types of icons:

| Reference Type | Example | Source |
|---------------|---------|--------|
| `imageVector = Icons.Outlined.Xxx` | `Icons.Outlined.Share` | Material Design icon library, download from Google Fonts |
| `iconResId = R.drawable.xxx` | `R.drawable.ic_touch_enabled` | Project custom drawable, extract from Android `res/drawable/` |

**Typical Source Code Example** (Kotlin sealed class):

```kotlin
data object Share : ToolbarAction(
    title = R.string.share,
    iconResId = R.drawable.ic_share,          // Custom icon
    imageVector = Icons.Outlined.Share,        // Material Design icon
)
```

When both `iconResId` and `imageVector` exist, **prefer the Material Design icon corresponding to `imageVector`** (more standardized, clearer).

### 2. Map Icon Names

Convert `Icons.Outlined.Xxx` camelCase names from Kotlin to snake_case used by Google Fonts:

| Kotlin Name | snake_case Name | Download File Name |
|-------------|-----------------|-------------------|
| `Icons.Outlined.Share` | `share` | `md_share.svg` |
| `Icons.Outlined.AddHome` | `add_home` | `md_add_home.svg` |
| `Icons.Outlined.EditNote` | `edit_note` | `md_edit_note.svg` |
| `Icons.Outlined.ChromeReaderMode` | `chrome_reader_mode` | `md_chrome_reader_mode.svg` |
| `Icons.Outlined.LibraryBooks` | `library_books` | `md_library_books.svg` |

**Conversion Rule**: camelCase → lowercase + underscore separation (`AddHome` → `add_home`).

### 3. Download SVG

**Download source**: https://fonts.google.com/icons?icon.size=24&icon.color=%231f1f1f

**Manual download method**:
1. Open the Google Fonts Icons webpage above
2. Search for icon name (e.g., `share`, `add_home`)
3. Select **Outlined** style (corresponds to `Icons.Outlined`)
4. Click to download SVG, choose 24px size, color `#1f1f1f` (dark black)

**Download URL pattern** (can be used for batch download scripts):
```
https://fonts.gstatic.com/s/i/short-term/release/materialsymbolsoutlined/{icon_name}/default/24px.svg
```

Example:
```
https://fonts.gstatic.com/s/i/short-term/release/materialsymbolsoutlined/share/default/24px.svg
https://fonts.gstatic.com/s/i/short-term/release/materialsymbolsoutlined/add_home/default/24px.svg
```

**Note**:
- The SVG downloaded from this URL has `fill="#000000"` (pure black)
- Downloaded SVG size is `viewBox="0 -960 960 960"` (Google standard Material Symbols coordinate system), renders correctly in HarmonyOS
- If an icon name doesn't exist in `materialsymbolsoutlined`, try `materialsymbolsrounded` or `materialsymbolssharp`

### 4. Rename and Store

**Naming rule**: Add `md_` prefix + snake_case name uniformly

```
Downloaded share.svg     → md_share.svg
Downloaded add_home.svg  → md_add_home.svg
```

**Storage location**: `entry/src/main/resources/base/media/`

**Key constraints**:
- `media/` directory **does not support subdirectories** (e.g., `media/icons/` will cause `CompileResource` error "invalid path, not a file")
- File names only allow lowercase letters, numbers, underscores
- All icon files must be placed directly at the root level of `media/` directory

### 5. Reference in ArkTS

```typescript
// Reference method: $r('app.media.filename_without_extension')
Image($r('app.media.md_share'))
Image($r('app.media.md_add_home'))
```

Typical icon mapping function pattern:

```typescript
private getIconResource(action: string): Resource {
  switch (action) {
    case 'share':
      return $r('app.media.md_share')
    case 'add_home':
      return $r('app.media.md_add_home')
    case 'settings':
      return $r('app.media.md_settings')
    default:
      return $r('app.media.icon_default')
  }
}
```

---

## Batch Download Script Example

Python script for batch downloading multiple icons:

```python
import urllib.request
import os

icons = [
    'share', 'add_home', 'edit_note', 'logout', 'bookmark_add',
    'add_link', 'apps', 'copy_all', 'library_books', 'pdf',
    'download', 'rule_settings', 'settings', 'chrome_reader_mode',
    'record_voice_over', 'invert_colors', 'format_size', 'view_column',
    'chat', 'cancel_presentation', 'cloud_upload', 'bookmarks'
]

output_dir = 'material_icons_svg'
os.makedirs(output_dir, exist_ok=True)

base_url = 'https://fonts.gstatic.com/s/i/short-term/release/materialsymbolsoutlined/{}/default/24px.svg'

for icon in icons:
    url = base_url.format(icon)
    out_path = os.path.join(output_dir, f'md_{icon}.svg')
    try:
        urllib.request.urlretrieve(url, out_path)
        print(f'OK: {icon}')
    except Exception as e:
        print(f'FAIL: {icon} - {e}')
```

---

## Common Icon Mapping Reference

Typical Material Design icon mappings for Android toolbar/menu items:

| Kotlin imageVector | snake_case Name | Download SVG | HarmonyOS Reference |
|-------------------|-----------------|-------------|---------------------|
| `Icons.Outlined.Share` | `share` | `md_share.svg` | `$r('app.media.md_share')` |
| `Icons.Outlined.Settings` | `settings` | `md_settings.svg` | `$r('app.media.md_settings')` |
| `Icons.Outlined.Home` | `home` | `md_home.svg` | `$r('app.media.md_home')` |
| `Icons.Outlined.Add` | `add` | `md_add.svg` | `$r('app.media.md_add')` |
| `Icons.Outlined.Edit` | `edit` | `md_edit.svg` | `$r('app.media.md_edit')` |
| `Icons.Outlined.Delete` | `delete` | `md_delete.svg` | `$r('app.media.md_delete')` |
| `Icons.Outlined.Search` | `search` | `md_search.svg` | `$r('app.media.md_search')` |
| `Icons.Outlined.ArrowBack` | `arrow_back` | `md_arrow_back.svg` | `$r('app.media.md_arrow_back')` |
| `Icons.Outlined.Bookmark` | `bookmark` | `md_bookmark.svg` | `$r('app.media.md_bookmark')` |
| `Icons.Outlined.BookmarkAdd` | `bookmark_add` | `md_bookmark_add.svg` | `$r('app.media.md_bookmark_add')` |
| `Icons.Outlined.Favorite` | `favorite` | `md_favorite.svg` | `$r('app.media.md_favorite')` |
| `Icons.Outlined.Share` | `share` | `md_share.svg` | `$r('app.media.md_share')` |
| `Icons.Outlined.Download` | `download` | `md_download.svg` | `$r('app.media.md_download')` |
| `Icons.Outlined.Upload` | `upload` | `md_upload.svg` | `$r('app.media.md_upload')` |
| `Icons.Outlined.Refresh` | `refresh` | `md_refresh.svg` | `$r('app.media.md_refresh')` |
| `Icons.Outlined.Menu` | `menu` | `md_menu.svg` | `$r('app.media.md_menu')` |
| `Icons.Outlined.MoreVert` | `more_vert` | `md_more_vert.svg` | `$r('app.media.md_more_vert')` |
| `Icons.Outlined.Close` | `close` | `md_close.svg` | `$r('app.media.md_close')` |
| `Icons.Outlined.Check` | `check` | `md_check.svg` | `$r('app.media.md_check')` |
| `Icons.Outlined.Visibility` | `visibility` | `md_visibility.svg` | `$r('app.media.md_visibility')` |

Note: `Icons.AutoMirrored.Outlined.*` variants use the same icon name as their non-mirrored counterparts (e.g., `Icons.AutoMirrored.Outlined.ArrowBack` → `arrow_back`).
