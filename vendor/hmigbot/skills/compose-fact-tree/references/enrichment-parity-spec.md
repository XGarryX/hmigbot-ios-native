# Enrichment-Parity Spec — making a Compose fact-tree byte-identical (in enrichment fields) to a traditional `app-relationship-tree`-enriched `toolkit-fact-tree.json`

> **Goal**: emit the SAME enrichment fields that `app-relationship-tree` writes, so `arkts-visual-verify` runs a Compose tree through the EXACT SAME code path with ZERO changes.
>
> **Scope**: research + field spec only. This document does not modify any skill.
>
> **Method**: cross-referenced `app-relationship-tree` producer scripts, a ground-truth traditional `toolkit-fact-tree.json` (160 records), the `arkts-visual-verify` consumers (`build_batches.py`, `build_page_queue.py`, `walk_to.py`, `sub-agent-batch-prompt.md`, `android-navigation-playbook.md`), and the current Compose tree (`habicat-main/.compose-fact-run/spec/toolkit-fact-tree.json`, 37 pages / 4 dialogs).

---

## 0. Critical finding up front — what arkts-visual-verify ACTUALLY consumes

I grepped every script + reference in `arkts-visual-verify` for each enrichment field. The **only** enrichment fields that any code path branches on are:

| Field / sub-key | Consumer | Decision it drives |
|---|---|---|
| `preconditions[].kind` ∈ {`login_required`,`vip_required`,`nav_redirect_target`} | `build_batches.py:99-105` (`classify_trip`) | which **trip** (logged_out vs logged_in_vip) a page lands in |
| `preconditions[].evidence` (substring `未登录`/`login`/`logged_out`) | `build_batches.py:103-105` | only when kind==`nav_redirect_target` → forces logged_in_vip |
| `preconditions[].kind` ∈ {`state_required`,`vip_required`} | `sub-agent-batch-prompt.md:247-256` | data injection / SKIPPED at capture time |
| `navigation_contract.trigger_actions[0].{type,label,resource_id,label_dynamic,fallback_am_start}` | `build_batches.py:168-188` (`edge_to_test_spec`); `walk_to.py:146-189` | the actual tap to perform when walking an edge / reach_path |
| `navigation_contract.verify_signal.text_contains` | `build_batches.py:174,195`; `walk_to.py:74,189,402`; `sub-agent-batch-prompt.md:261,288,305` | the on-screen anchor that confirms "we arrived at page X" |
| `navigation_contract.contract_uncertain` | `build_batches.py:187`; `sub-agent-batch-prompt.md:281` | skip testing this edge if true |
| `reach_path` (alternating `[page, token, page, …]`) | `walk_to.py:124-189` (`reach_path_walkable`, `walk_real_click`) | Mode A real-click traversal vs am-start fallback |
| `is_start_destination` | `build_batches.py:430-435` | Compose single-Activity BFS seed (already added) |
| `inbound_triggers[].{from_page,trigger_label,trigger_view_id,evidence_file,evidence_line}` | `android-navigation-playbook.md:105-119` (LLM decision in Phase 0 walk) | which button to tap when navigating from launcher — **prompt-level (LLM reads it), not script-branching** |

**Fields that NO code branches on** (carried but unused by `arkts-visual-verify`):
- `reach_actions`, `reach_path_clean`, `reach_path_orphan` — written by producer, never read by any visual-verify script/prompt. COSMETIC.
- `wizard_steps` — read only by `compute_navigation_contract.py` itself (the producer) to pre-seed `relationship_kind`; **no `arkts-visual-verify` consumer**. COSMETIC for visual-verify.
- `construction_mode` — consumed by **a2h-spec Phase B** (page-structure template choice), NOT by `arkts-visual-verify`. Safe to hardcode `"code_only"` for visual-verify's purposes.
- `truly_isolated` — described in the producer (`compute_reach_paths.py:319-326`) as "downstream sees this → go straight to am_start", but **no current `arkts-visual-verify` script reads it**. `walk_to.py` decides am-start vs real-click purely from `reach_path` length + contract labels. COSMETIC (defensive only).
- `parent_in_nav` — read only by the producer `compute_navigation_contract.py:632` to find the host record. `build_page_queue.py` derives host from `navigation.inbound[0].from` instead. COSMETIC for visual-verify.
- `relationship_kind`, `wizard_index`, `from_state`, `exit_action_to_next`, `generated_from` inside `navigation_contract` — **not read by any visual-verify script**; only `trigger_actions` + `verify_signal` + `contract_uncertain` are. COSMETIC sub-keys (but cheap to fill for shape parity).

> **Implication**: the must-have set is small. `preconditions` (login/vip), `navigation_contract.{trigger_actions, verify_signal, contract_uncertain}`, `reach_path`, and `inbound_triggers` are the load-bearing fields. Everything else can be stubbed for byte-shape parity with near-zero correctness risk.

---

## 1. `inbound_triggers`

### (A) Exact JSON schema
Array of objects on the record's top level. Required keys per entry: `from_page`, `trigger_label`, `evidence_file`, `evidence_line`, `source`. Optional: `trigger_method`, `trigger_view_id` (may be `null`).

Real example (traditional, `AIChangeClothesActivity`):
```jsonc
"inbound_triggers": [
  {
    "from_page": "VideoDanceTempActivity",
    "trigger_method": "openChangeClothesPage",
    "trigger_view_id": null,
    "trigger_label": "一键换衣模板项",
    "evidence_file": "aivideo/src/main/java/.../VideoDanceTempActivity.kt",
    "evidence_line": 103,
    "source": "llm_source_read"
  }
]
```
Launcher special case: `[{ "from_page": null, "trigger": "boot", "source": "launcher" }]`.

### (B) Consumers
- **`android-navigation-playbook.md:105-119`** — LOAD-BEARING (prompt-level). The Phase 0 walk LLM reads `inbound_triggers` to decide the next tap. Priority order it uses: `trigger_view_id` exact match in dump → `trigger_label` exact text → `trigger_label` substring → walk to `from_page` parent first.
  - `from_page` — LOAD-BEARING (identifies the host screen to be on before tapping).
  - `trigger_label` — LOAD-BEARING (the text to find+tap).
  - `trigger_view_id` — LOAD-BEARING when present (on-device resource-id match); may be `null`.
  - `trigger_method` / `evidence_file` / `evidence_line` — COSMETIC for runtime navigation (traceability only); `evidence_file` is HARD-validated to exist by the producer's self-check but no consumer reads it.
- No `arkts-visual-verify` **script** branches on this field — it is purely an LLM-prompt input.

### (C) Compose-source derivation rule
Compose has no `startActivity(X)` / `findViewById(R.id.X)` / layout XML. But the Compose tree already carries the inverse data: every navigating component has `navigation.to_page`, and the page-level `navigation.inbound[]` / `flow_graph.edges` already record `{from, to, via_component, trigger}`.

Build `inbound_triggers[target]` by inverting `flow_graph.edges` (or `navigation.inbound[]`):

```
FOR each edge e in flow_graph.edges:                # e = {from, to, via_component, trigger, is_dynamic}
  src_page  = record[e.from]
  comp      = component in src_page with id == e.via_component
  target    = record[e.to]
  append to target.inbound_triggers:
    from_page       = e.from
    trigger_method  = e.via_component                 # the Composable component id is the closest analogue to onClick method
    trigger_view_id = comp.testTag if present else null    # Compose has no R.id; use testTag/null
    trigger_label   = comp.text or comp.content_desc        # component label (Chinese on-device)
    evidence_file   = comp.source_anchor.file
    evidence_line   = comp.source_anchor.line
    source          = "compose_nav_edge_invert"
```

Launcher (`is_start_destination` page reached at cold start): emit the boot entry `[{from_page:null, trigger:"boot", source:"launcher"}]`. For the launcher shell (`MainActivity`/`MainScreen`) use boot; for tab children whose only inbound is the tab host, `from_page = MainScreen`, `trigger_label = <tab label>`.

`trigger_view_id` mapping: Compose has no `R.id`. Use the component's `testTag` if the extractor captured one, else `null`. The playbook's priority (2)/(3) (label match) then carries navigation — which is exactly the realistic Compose case.

### (D) Criticality — **CRITICAL**
Without `inbound_triggers`, the Phase 0 launcher walk has no button-targeting hints and falls back to blind dump-scanning. For login/onboarding pages reached by tapping Chinese labels, this is the field that tells the walker "tap 登录 / 同意 / 下一步". The data is already 100% present in the Compose tree (edge inversion) so cost is near zero.

---

## 2. `navigation_contract`

### (A) Exact JSON schema
Object on record top level. Keys: `relationship_kind` (required, enum), `from_state` (required, human string), `trigger_actions[]` (required), `verify_signal{text_contains}` (required), `contract_uncertain` (required bool), `generated_from[]` (required, may be empty), `wizard_index` (optional int, wizard only), `exit_action_to_next` (optional, wizard only), `notes` (optional).

`trigger_actions[i]` keys: `type` (enum: `am_start_launcher`|`auto_default`|`tap_text`|`tap_resource_id`|`back`|`swipe`), `label` (str|null), `label_dynamic` (bool), `verify_after_tap` (bool), `fallback_am_start` (bool, Activity-jump only), `resource_id` (str|null).

Real example A (Activity-jump, `AIChangeClothesActivity`):
```jsonc
"navigation_contract": {
  "relationship_kind": "activity_jump",
  "from_state": "cold_start",
  "trigger_actions": [
    { "type": "tap_text", "label": "一键换衣", "label_dynamic": false,
      "verify_after_tap": true, "fallback_am_start": true }
  ],
  "verify_signal": { "text_contains": "一键换衣" },
  "contract_uncertain": false,
  "generated_from": ["aivideo/src/main/res/layout/activity_change_clothes.xml"]
}
```
Real example B (wizard step, `AIDressCoatFragment`):
```jsonc
"navigation_contract": {
  "relationship_kind": "wizard_step",
  "from_state": "AIDressActivity_default",
  "trigger_actions": [
    { "type": "auto_default", "label": null, "verify_after_tap": false, "fallback_am_start": false }
  ],
  "verify_signal": { "text_contains": "选择上衣" },
  "contract_uncertain": false,
  "wizard_index": 0,
  "generated_from": ["AIDressCoatFragment.kt:41", "fragment_dress_coat.xml:120"]
}
```

### (B) Consumers
- **`build_batches.py:168-188` `edge_to_test_spec`** — reads `trigger_actions[0].{type,label,resource_id,label_dynamic}`, `verify_signal.text_contains`, `trigger_actions[0].fallback_am_start`, `contract_uncertain`. ALL LOAD-BEARING.
- **`build_batches.py:195` `record_to_page_spec`** — reads `verify_signal.text_contains` as the page's arrival anchor. LOAD-BEARING.
- **`walk_to.py:74,124-160,186-189,402`** — `reach_path_walkable` requires each intermediate page's `trigger_actions[0].label` non-null OR `type=="auto_default"`; `walk_real_click` taps `trigger_actions[0].label` and verifies via `verify_signal.text_contains`. LOAD-BEARING.
- **`sub-agent-batch-prompt.md:261,288,305`** — `verify_signal.text_contains` used as the "am I on the right page" check + per-edge verify. LOAD-BEARING.

Sub-key criticality:
- `trigger_actions[0].type` — LOAD-BEARING (`auto_default` vs `tap_text` changes walk behavior).
- `trigger_actions[0].label` — LOAD-BEARING (the tap text). **Must match on-device text** (see §locale, Decision 3).
- `trigger_actions[0].label_dynamic` — LOAD-BEARING (true → downstream tolerates label miss / uses first-button fallback).
- `trigger_actions[0].fallback_am_start` — LOAD-BEARING (lets walker am-start an Activity when tap fails).
- `trigger_actions[0].resource_id` — LOAD-BEARING when present (else null; Compose → null).
- `verify_signal.text_contains` — LOAD-BEARING (arrival anchor). **Must match on-device text.**
- `contract_uncertain` — LOAD-BEARING (true → edge skipped).
- `relationship_kind`, `from_state`, `wizard_index`, `exit_action_to_next`, `generated_from`, `notes` — COSMETIC for visual-verify (no script reads them). Fill for shape parity but correctness is not enforced downstream.

### (C) Compose-source derivation rule
Per record:
- **`relationship_kind`** (cosmetic, but pick a sensible value for shape):
  - `is_start_destination` page → `activity_root`.
  - page reached via a component `navigation.to_page` (has inbound edges) → `activity_jump`.
  - tab child (in launcher `contains[]` with `page_signature.kind=="tab_host"` parent) → `tab`.
  - dialog (in `dialogs[]`, appears in some page's `shows_dialogs[]`) → `dialog_trigger`; if shown from a lifecycle effect → `lifecycle_modal`.
  - NavHost-overlay onboarding steps consumed by `popUpTo(inclusive)` → `wizard_step`.
- **`from_state`**: `cold_start` for launcher-reachable (`is_start_destination` or directly reached from start dest); else `<host_id>_default` where host = the `from_page` of the primary inbound edge.
- **`trigger_actions[0]`**:
  - `activity_root` → `{type:"am_start_launcher", label:null}`.
  - `activity_jump`/`tab`/`dialog_trigger` → `{type:"tap_text", label:<inbound edge's via_component.text/content_desc>, label_dynamic:<true if navigation.is_dynamic or component text came from a state variable>, verify_after_tap:true, fallback_am_start:<true only for full-screen route pages, false for tabs/dialogs>}`.
  - `auto_default` for `host_default`, `lifecycle_modal`, and the first `wizard_step`.
- **`verify_signal.text_contains`**: derive from the **target page's `page_signature.positive[]`** — pick the most stable anchor (longest stable on-screen string; prefer a title/header). If `positive[]` is empty, fall back to the page `label` (only if that label is rendered on-screen) or the longest static `Text` component on the page. This is the single most important derived value (drives every arrival check). If no stable anchor can be found → set `text_contains:null` AND `contract_uncertain:true`.
- **`contract_uncertain`**: `true` when (a) `trigger_actions[0].label` is null for a non-`auto_default`/non-`am_start_launcher` action, OR (b) `verify_signal.text_contains` is null, OR (c) the label/anchor is dynamic and unresolved. Otherwise `false`.
- `generated_from`: list the Composable source anchor(s) (`<file>:<line>`). Cosmetic.

### (D) Criticality — **CRITICAL**
`verify_signal.text_contains` and `trigger_actions[0].label` are the two values the entire walk + capture loop pivots on. Derivable today from `page_signature.positive[]` (verify) and component `text` (label), both already in the Compose tree.

---

## 3. `preconditions`

### (A) Exact JSON schema
Array of objects on record top level. Per entry: `kind` (required), `evidence` (required string), `evidence_file` (optional), `evidence_line` (optional), `source` (required). Some kinds add `required_params`/`logic`.

Real examples (traditional):
```jsonc
"preconditions": [
  { "kind": "login_required", "evidence": "UserData.isBinding() check",
    "evidence_file": ".../AIChangeClothesActivity.kt", "evidence_line": 281,
    "source": "preconditions_enhancer" },
  { "kind": "login_conditional", "evidence": "interceptAuth==1 global flag",
    "evidence_file": ".../AIChangeClothesActivity.kt", "evidence_line": 281,
    "source": "preconditions_enhancer" }
]
```
Kinds seen in ground truth: `login_required` (26), `login_conditional` (24), `vip_required` (4), `param_required` (2). Producer can also emit `nav_redirect_target`, `state_required`, `credits_required_amount`, `feature_flag`.

### (B) Consumers
- **`build_batches.py:98-108` `classify_trip`** — LOAD-BEARING. Branches ONLY on:
  - `kind == "login_required"` → forces `["logged_in_vip"]`.
  - `kind == "vip_required"` → forces `["logged_in_vip"]`.
  - `kind == "nav_redirect_target"` AND `evidence` contains `未登录`/`login`/`logged_out` → forces `["logged_in_vip"]`.
  - Any other kind (incl. `login_conditional`, `param_required`, `state_required`, `credits_required_amount`, `feature_flag`) → **ignored by classify_trip** → page stays ambiguous (both trips).
- **`sub-agent-batch-prompt.md:247-256`** — LOAD-BEARING at capture time: `kind=="state_required"` → walk real creation or SKIPPED; `kind=="vip_required"` → assumed satisfied by trip_2 scenario. `login_required`/`nav_redirect_target`/`credits_required_amount` → "satisfied by scenario_chain" (no action).
- `evidence_file`/`evidence_line`/`source` — COSMETIC (never read by a branch).

> Note: `empirical_trip` (build_batches.py:54-69) overrides preconditions if a Phase-0 baseline screenshot already exists. So preconditions matter most on the FIRST run before any baseline is captured.

### (C) Compose-source derivation rule
The 3 load-bearing kinds map cleanly from Compose gating:
- **(a) AUTH-gated pages** — a route guarded by `isLogin` / `requiresLogin` / a NavHost that redirects to `LoginScreen` when not authenticated → emit `{kind:"login_required", evidence:"<guard expr>", evidence_file, evidence_line, source:"compose_gating_scan"}`. This is the ONE precondition Compose must extract from source (the guard predicate is not already in the current tree).
- **VIP-gated** — guard on a `vip`/`isVip`/`subscription` predicate → `{kind:"vip_required", ...}`.
- **conditional redirect** — `navigate(Login){ popUpTo… }` only when a predicate is false → `{kind:"nav_redirect_target", evidence:"未登录 → LoginScreen", source:"compose_gating_scan"}` (include `未登录` so classify_trip's substring check fires).

- **(b) ONBOARDING / first-run pages** (overlay NavHost gated on `!agreePrivacy` / `!setupComplete`, steps consumed by `popUpTo(inclusive)` — e.g. `PrivacyScreen → OnboardScreen → LoginScreen → CharacterScreen → …`): **emit NO precondition kind.**

  **Definitive answer**: `arkts-visual-verify` has **no first-run/onboarding precondition handling**. Onboarding is reached automatically by the default `pm clear` cold-launch walk:
  - `android-navigation-playbook.md:27` — trip_1 always `pm clear` cold launches "隐私协议会重弹" (privacy re-pops).
  - `sub-agent-batch-prompt.md:76-78` — reset = `pm clear` (kill + wipe data + wipe prefs), explicitly so splash/guide/agreement first-run paths replay.
  - `dismiss_popups.py` (playbook §2) clicks `agree/同意/跳过/下一步/我知道了` by keyword.

  So onboarding pages need only: `navigation_contract.from_state:"cold_start"` + correct `inbound_triggers` (Agree → Next → Skip labels) + a `verify_signal.text_contains` anchor. The cold-launch walk drives them with no precondition. They should also be name-classified into `logged_out` trip — which `build_batches.py:44-47` `LOGGED_OUT_NAME_PATTERN` already does for ids matching `Login|Splash|Guide|Welcome|Onboard|Agreement|Privacy|LaunchAd` (Habicat's `OnboardScreen`/`PrivacyScreen`/`LoginScreen` all match). **No new precondition kind is required for onboarding.**

### (D) Criticality — **CRITICAL** (for the auth/login kinds only)
`login_required`/`vip_required`/`nav_redirect_target` are the sole signals that route a gated page into trip_2 (logged_in_vip) so the login scenario runs first. Onboarding handling is FREE (cold-launch + name pattern). The only NEW source extraction required anywhere in this spec is the login/vip guard predicate (see Decision 2).

---

## 4. `reach_path` (+ `reach_actions`, `reach_path_clean`, `reach_path_orphan`)

### (A) Exact JSON schema
`reach_path`: flat array alternating `[page_id, transition_token, page_id, …]`, ending on the record itself. Length 1 (`[self]`) = orphan/unreached. Companion fields:
- `reach_actions`: array of coarse action tokens (`["am_start"]`, `["am_start","fragment_attach"]`).
- `reach_path_clean`: page-ids only (transitions stripped).
- `reach_path_orphan`: bool.

Real examples:
```jsonc
"reach_path": ["AIChangeClothesActivity"],            // orphan
"reach_actions": ["am_start"], "reach_path_clean": ["AIChangeClothesActivity"], "reach_path_orphan": false
```
```jsonc
"reach_path": ["AIChangeClothesActivity","goto","VFXDetailsActivity","goto",
               "AiPaintChatActivity","show_fragment_AiPaintChatFragment","AiPaintChatFragment"],
"reach_actions": ["am_start","fragment_attach"],
"reach_path_clean": ["AiPaintChatActivity","AiPaintChatFragment"], "reach_path_orphan": false
```

> Note: traditional records ALSO carry `reach_paths` (plural, `[{display:"A > B > C", depth, source, ref}]`) — that is the toolkit-indexer field consumed by `build_page_queue.py:68-75`. The Compose tree already emits `reach_paths`. The singular `reach_path` is the app-relationship-tree field consumed by `walk_to.py`.

### (B) Consumers
- **`walk_to.py:124-189`** — LOAD-BEARING. `reach_path_walkable` needs length ≥ 3 and every page after index 0 to have a contract label (or auto_default). `walk_real_click` iterates `reach_path[0,2,4,…]` tapping each transition. Drives Mode A (real-click) vs am-start fallback.
- **`build_page_queue.py:68-75`** — reads `reach_paths` (PLURAL, `.display`), NOT singular `reach_path`. So the singular field is consumed only by `walk_to.py`.
- `reach_actions`, `reach_path_clean`, `reach_path_orphan` — COSMETIC. Grepped all scripts/refs: never read.

### (C) Compose-source derivation rule
Run the existing producer logic against the Compose graph — it already speaks the new schema (`navigation.outbound[].to`, `inbound[].from`, `contains[]`, `shows_dialogs[]`). `compute_reach_paths.py` does multi-source BFS from `app.launcher_short` + every page as fallback entry, plus `contains[] → show_fragment_X` and `shows_dialogs[] → trigger_X` implicit edges. The Compose tree provides all of these:
- launcher = `MainActivity` shell; but its outbound is 0 → BFS must seed from `is_start_destination` page (`MainScreen`). The producer's launcher-first BFS plus all-pages fallback already covers this, and `build_batches.py:430-435` independently re-seeds from `is_start_destination`.
- `contains[]` (e.g. `MainScreen.contains=[OverviewScreen,TaskScreen,…]`) → tab children get `show_fragment_X` edges.
- `shows_dialogs[]` → dialog reach edges.

Then synthesize companions deterministically: `reach_path_clean` = `reach_path[0::2]`; `reach_path_orphan` = `len(reach_path) <= 1`; `reach_actions` = coarse tokens (`am_start` for first hop, `tab_select`/`dialog_show` per transition prefix). These are pure post-processing, no new source data.

### (D) Criticality — **USEFUL** (not strictly required)
`walk_to.py` is the only consumer and it gracefully falls back to am-start when `reach_path` is too short or labels are missing. A correct multi-hop `reach_path` makes real-click traversal possible (better fidelity); without it the walker still works via am-start / the Phase-0 LLM launcher walk. Companions are COSMETIC. Recommendation: emit `reach_path` (cheap, reuses producer script) but treat companions as pure shape stubs.

---

## 5. `wizard_steps`

### (A) Exact JSON schema
Array on the **host** record. Per entry: `step_index` (int), `fragment_id` (str), `relationship_kind` (str, usually `wizard_step`).
```jsonc
"wizard_steps": [
  { "step_index": 0, "fragment_id": "AIDressCoatFragment", "relationship_kind": "wizard_step" },
  { "step_index": 1, "fragment_id": "AIDressSuitFragment", "relationship_kind": "wizard_step" }
]
```

### (B) Consumers
- **Producer-only**: `compute_navigation_contract.py:246-262` reads a host's `wizard_steps` to pre-seed a child's `relationship_kind`. No `arkts-visual-verify` script or prompt reads `wizard_steps`. COSMETIC for visual-verify.

### (C) Compose-source derivation rule
If you choose to emit it for shape parity: for an onboarding NavHost (`SetupCharacterNavHost`: Privacy → Onboard → Login → Character → TaskPromote → PickTask), list each step as `{step_index:i, fragment_id:<screenId>, relationship_kind:"wizard_step"}` on the host record. Derivable from the `popUpTo`-inclusive sequential route order. But since nothing downstream reads it, this is optional.

### (D) Criticality — **COSMETIC / SKIP** for arkts-visual-verify.

---

## 6. `construction_mode`

### (A) Exact JSON schema
Top-level string, one of `"layout_xml"` | `"code_only"` | `null`. (Ground truth: 12 layout_xml, 4 code_only, 144 null.)

### (B) Consumers
- Consumed by **a2h-spec Phase B** (page-structure template selection), per `app-relationship-tree` SKILL.md §Phase 1.6. **No `arkts-visual-verify` consumer** (grepped: 0 hits). Safe to hardcode for visual-verify.

### (C) Compose-source derivation rule
Every Compose page is `code_only` (no per-page `setContentView(R.layout.*)`; UI is a `@Composable`). Hardcode `"code_only"` on every record. Matches reality and satisfies any a2h-spec consumer.

### (D) Criticality — **COSMETIC** for arkts-visual-verify (USEFUL only if a2h-spec also consumes the Compose tree — then hardcode `"code_only"`).

---

## 7. `truly_isolated`

### (A) Exact JSON schema
Top-level bool. (Ground truth: 90 true, 70 false.) Set `true` when `reach_path` length ≤ 1 and the record is not the launcher.

### (B) Consumers
- Documented intent (`compute_reach_paths.py:319-326`): downstream should go straight to am-start for isolated nodes. **But no current `arkts-visual-verify` script reads it** — `walk_to.py` decides am-start vs real-click from `reach_path` length + contract labels directly. COSMETIC.

### (C) Compose-source derivation rule
Pure function of `reach_path`: `truly_isolated = (len(reach_path) <= 1) and id != launcher_short`. Free byproduct of running `compute_reach_paths.py`.

### (D) Criticality — **COSMETIC** (defensive shape only).

---

## 8. `parent_in_nav`

### (A) Exact JSON schema
Top-level string (host record id) or `null`. Example: `"parent_in_nav": "AiPaintChatActivity"` on `AiPaintChatFragment`.

### (B) Consumers
- Read only by producer `compute_navigation_contract.py:632` (host lookup for contract). `build_page_queue.py:78-85` derives host from `navigation.inbound[0].from` instead. No `arkts-visual-verify` branch reads `parent_in_nav`. COSMETIC.

### (C) Compose-source derivation rule
For a tab child or dialog, set `parent_in_nav` = the page whose `contains[]`/`shows_dialogs[]` lists it (e.g. tab children → `MainScreen`). Derivable from existing `contains[]`/`shows_dialogs[]` with no new source data. Only needed if you run `compute_navigation_contract.py` and want it to resolve hosts; otherwise optional.

### (D) Criticality — **COSMETIC** for visual-verify (USEFUL if you reuse the producer's contract script, since it reads `parent_in_nav` to find the host).

---

## Decision answers

### Decision 1 — MINIMUM field set for onboarding + login-gating + launcher-navigation parity
Must-have (load-bearing in `arkts-visual-verify`):
1. **`navigation_contract`** with correct `trigger_actions[0].{type,label,label_dynamic,fallback_am_start}` + `verify_signal.text_contains` + `contract_uncertain`. (Drives every walk + capture + edge test.)
2. **`preconditions`** with `login_required` / `vip_required` / `nav_redirect_target` for auth/VIP-gated pages. (Drives trip classification.)
3. **`inbound_triggers`** with `from_page` + `trigger_label` (+ `trigger_view_id` if a testTag exists). (Drives the Phase-0 launcher walk LLM.)
4. **`reach_path`** (singular, alternating array). (USEFUL — enables `walk_to.py` Mode A real-click; degrades gracefully if absent.)

Explicitly EXCLUDE from must-have (cosmetic for arkts-visual-verify): `wizard_steps`, `construction_mode` (hardcode `"code_only"` only if a2h-spec consumes the tree), `truly_isolated`, `parent_in_nav`, `reach_actions`, `reach_path_clean`, `reach_path_orphan`, and the `navigation_contract` sub-keys `relationship_kind`/`from_state`/`wizard_index`/`exit_action_to_next`/`generated_from`. Emit them only as cheap shape stubs (derivable for free) if byte-shape identity is desired; their correctness is never enforced downstream.

**Onboarding needs NO precondition kind.** It is captured by the default `pm clear` cold-launch walk + `dismiss_popups.py` keyword clicking + name-pattern trip classification. Provide only `from_state:"cold_start"`, `inbound_triggers` for Agree/Next/Skip, and a `verify_signal` anchor.

### Decision 2 — Derivable from current tree, or needs NEW source extraction?
| Must-have field | Source |
|---|---|
| `inbound_triggers` | **Already in tree.** Invert `flow_graph.edges` / `navigation.inbound[]` + component `text`/`content_desc`/`source_anchor`. No new extraction. |
| `navigation_contract.trigger_actions[0].label` | **Already in tree.** From the inbound edge's `via_component.text`. No new extraction. |
| `navigation_contract.verify_signal.text_contains` | **Already in tree.** From target page `page_signature.positive[]` (present on Compose pages, e.g. MainScreen). Fallback to page `label`/longest static Text. No new extraction. |
| `navigation_contract.contract_uncertain` | **Derived** from label/anchor nullness. No new extraction. |
| `reach_path` | **Already in tree.** Reuse `compute_reach_paths.py` over `outbound/inbound/contains/shows_dialogs`. No new extraction. |
| `preconditions` (`login_required`/`vip_required`/`nav_redirect_target`) | **NEW SOURCE EXTRACTION REQUIRED.** The auth/VIP guard predicate (`isLogin`/`requiresLogin`/`isVip`/redirect-to-LoginScreen) is NOT in the current tree. compose-fact-tree must scan composable/NavHost source for these guards and emit the precondition. This is the single new extractor needed. |

**Summary of new extraction work**: exactly ONE — a login/VIP gating scanner that reads the composable + NavHost source to find auth guards and redirect-to-login navigation, emitting `login_required` / `vip_required` / `nav_redirect_target` preconditions. Everything else is synthesis from data the tree already holds.

### Decision 3 — Language / locale (labels & verify_signal must match the on-device baseline)
Problem: `trigger_actions[0].label` and `verify_signal.text_contains` are matched against on-device text. Habicat source strings are Chinese; if the emulator runs en-US they will not match.

How traditional apps handle it: `app-relationship-tree`'s `_trace_button_label_from_inbound` (`compute_navigation_contract.py:422-505`) resolves labels from `@string/foo` references via `_resolve_string_resource`, which reads `res/values*/strings.xml` — **the default (unqualified) `values/strings.xml`**, i.e. the app's default locale. It does NOT target a specific emulator locale; it relies on the baseline device running the app's default locale.

Recommendation for compose-fact-tree (in priority order):
1. **Run the baseline Android device in the app's default locale.** Habicat's default `stringResource` literals are Chinese; the Phase-0 `pm clear` baseline must run with the device locale set to zh (or at least the app's default), so on-screen text matches the extracted Chinese labels. This is the lowest-risk fix and mirrors how the traditional path implicitly works (default `values/strings.xml`). The HMOS side must be verified in the same locale (both emulators same locale — visual-verify already assumes a matched pair).
2. **Resolve `stringResource(R.string.x)` to the DEFAULT `values/strings.xml`** when the component label is a resource reference, exactly like the traditional `_resolve_string_resource`. Emit that literal as `label`/`text_contains`. For hardcoded Compose string literals (Habicat uses Chinese literals directly), use the literal as-is.
3. **For runtime/dynamic text** (label comes from a state variable / formatted string): set `label_dynamic:true` and rely on `trigger_view_id` (testTag) — `build_batches.py`/walk tolerate dynamic labels by falling back to first-button / resource-id. Do NOT guess the runtime string.

Do NOT translate to en-US in the fact-tree: the tree must carry whatever the on-device baseline will actually render. The clean rule is **fact-tree labels = app default-locale strings; baseline device runs that same default locale**.

---

## Must-have vs skip summary table

| Field | Load-bearing in arkts-visual-verify? | Compose-derivable from current tree? | New extraction? | Verdict |
|---|---|---|---|---|
| `navigation_contract.trigger_actions[0]` | YES (build_batches, walk_to) | YES (inbound edge component text) | No | **MUST-HAVE** |
| `navigation_contract.verify_signal.text_contains` | YES (walk_to, sub-agent, build_batches) | YES (page_signature.positive) | No | **MUST-HAVE** |
| `navigation_contract.contract_uncertain` | YES (edge skip) | YES (derived) | No | **MUST-HAVE** |
| `preconditions` login/vip/nav_redirect | YES (classify_trip) | NO | **YES — guard scanner** | **MUST-HAVE** |
| `inbound_triggers` (from_page,label,view_id) | YES (Phase-0 walk prompt) | YES (edge inversion) | No | **MUST-HAVE** |
| `reach_path` (singular) | YES (walk_to Mode A) | YES (compute_reach_paths) | No | **USEFUL (emit; degrades gracefully)** |
| `navigation_contract.relationship_kind/from_state/wizard_index/exit_action_to_next/generated_from` | No | YES | No | SHAPE STUB (optional) |
| `wizard_steps` | No (producer-only) | YES | No | SKIP / optional stub |
| `construction_mode` | No (a2h-spec only) | YES (`"code_only"`) | No | SKIP for VV; hardcode if a2h-spec consumes |
| `truly_isolated` | No | YES (reach_path len) | No | SKIP / free stub |
| `parent_in_nav` | No (producer-only) | YES (contains/shows_dialogs) | No | SKIP / stub if reusing contract script |
| `reach_actions` / `reach_path_clean` / `reach_path_orphan` | No | YES (post-process) | No | SKIP / free stub |
| `preconditions` for onboarding/first-run | N/A (no VV handling) | N/A | No | **NONE NEEDED** — cold-launch walk handles it |
