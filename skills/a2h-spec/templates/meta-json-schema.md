<!-- when: Phase A 生成 / 扩展 meta.json 时加载 -->
<!-- topics: meta.json, schema, layout_sources, dynamic_menus, bottom_sheet_config, navigation_mode -->

# meta.json 完整 schema

Phase A 为每个页面扩展 / 生成 meta.json。确定性字段由 `synthesize_meta_json.py` 填，语义字段由 LLM 补。完整字段示例：

```json
{
  "page_id": "page_0001_MainView",
  "label": "从真实可见标题与页面行为提取，不以类型名代替规格",
  "activity": "MainView",
  "auto_generated": true,
  "confidence": "high | medium | low",
  "layout_sources": [
    "App/Views/MainView.swift",
    "App/Views/HomeView.swift"
  ],
  "style_sources": [
    "App/Theme.swift",
    "App/Appearance.swift",
    "App/Assets.xcassets/AccentColor.colorset/Contents.json"
  ],
  "click_path": [],
  "came_from": null,
  "trigger_element": null,
  "clickable_elements": [
    {
      "class": "SwiftUI.Button",
      "resource_id": "submitAction",
      "text": "Submit",
      "content_desc": "Submit button",
      "bounds": "unknown",
      "children_items": []
    }
  ],
  "navigation_targets": {
    "btn_settings": "SettingsView",
    "btn_profile": "ProfileView"
  },
  "menu_sources": ["App/Views/MainView.swift"],
  "fragment_tags": {},
  "dynamic_menus": {
    "bottom_nav": {
      "build_method": "MainView.toolbar",
      "max_visible_items": 4,
      "has_more_overflow": true,
      "more_popup_type": "Menu",
      "configurable": true
    }
  },
  "bottom_sheet_config": {
    "behavior_class": "presentationDetents",
    "peek_height_dimen": "source-defined-detent",
    "states": ["MEDIUM", "LARGE", "HIDDEN"],
    "lockable": true
  },
  "recycler_item_layouts": [
    {"adapter": "MainView.ForEach", "layouts": ["App/Views/RowView.swift"]}
  ],
  "navigation_mode": "MUTUALLY_EXCLUSIVE",
  "page_type": "full_screen_page",
  "needs_immersive_safearea": true
}
```

保留字段名不表示存在同名源控件。静态生成必须 synthesized=true；没有实际设备观测的 bounds=unknown，confidence 不得伪称运行结果。
