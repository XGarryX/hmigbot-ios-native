# Unsupported Or High-Risk Patterns

Use this file when the batch includes Android patterns that are unsafe to translate mechanically.

## Patterns To Escalate

| Pattern | Why it is risky | What to do |
| --- | --- | --- |
| Jetpack Compose source UI | This skill is designed for View/XML projects. | Stop and switch to a Compose-specific migration workflow. |
| `View.onDraw`, custom canvas work, complex gesture math | ArkUI equivalent often needs a redesign, not a direct port. | Preserve the surrounding page and leave a focused TODO for the custom widget. |
| `CoordinatorLayout`, nested behaviors, collapsing toolbars | Behavior comes from Android-specific coordinator contracts. | Rebuild intent explicitly with page state instead of copying structure. |
| Programmatic `FragmentTransaction` with dynamic child injection | Dependencies are hidden in code, not in XML. | Extract a parent component and one child component per section or slot. |
| DataBinding expressions or XML logic | The source behavior is split between layout and code. | Move state and conditions into explicit ArkUI state and props. |
| Media3, ExoPlayer, video surfaces | UI and platform surface behavior are tightly coupled. | Port only shell UI first and leave playback surface behavior as a separate task. |
| `PreferenceFragment` or Android preference screens | Preference APIs do not map cleanly to ArkUI page components. | Rebuild the screen as a normal settings page instead of translating preference XML directly. |
| EventBus, WorkManager, services, broadcast-driven UI | The visual layer depends on platform events. | Stub the UI state and note the integration boundary in the batch report. |

## Response Rules

- Never claim full parity when one of these patterns is present.
- Keep the visible UI structure moving forward, but isolate risky behavior behind TODOs or placeholders.
- Call out exactly which source files were skipped or partially represented.
- Prefer a truthful partial migration over a confident but wrong screen.
