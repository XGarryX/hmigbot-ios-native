---
name: ios-ui-graph-query
description: Query an iOS UI graph (produced by ios-ui-graph-builder) to retrieve migration context for iOS→HarmonyOS UI work. Given a screen, returns its full component tree, attributes, navigation edges, and resource inventory; given a component, returns its children, parent chain, siblings, and attributes — all sourced from the four JSON graph files (Screen.json, Component.json, Navigation_Edge.json, Containment_Edge.json). Use whenever the user asks to query, look up, inspect, or retrieve information from an iOS UI graph for migration ("迁移上下文", "查询界面/组件", "what does this screen contain", "what navigates to this screen"). This is the retrieval counterpart to ios-ui-graph-builder — run the builder first to create the graph; this skill only queries an existing one.
metadata:
  type: domain
  domain: migration
  tags:
  - migration
  - ios
  - ui-graph
  - query
---

> **iOS 源输入适配**：执行源分析/源设备操作前，读 [原生输入协议](../a2h-spec/references/native-input.md)。它仅替换平台输入；原阶段、模板、规则、门禁、模式和 target 侧执行保持 1.5.2。

# iOS UI Graph Query — Migration Context Retrieval

Query the original four-file graph without rewriting it. The native launcher adapts only the identity field at the original read-only engine boundary, then returns native keys. Unknown or incomplete source evidence stays unknown.

## Prerequisites

Locate Screen.json, Component.json, Navigation_Edge.json and Containment_Edge.json produced by ios-ui-graph-builder. Read the builder's schema_v2.md. Do not synthesize missing relationships to make a query look complete.

## Workflow

### Step 1: Read references

- references/ios-to-harmonyOS-ui-layout-mapping-reference.md
- references/ios-to-harmonyOS-ui-atomic-component-mapping-reference.md
- references/ios-to-harmonyOS-ui-interaction-mapping-reference.md
- references/ui-migration-pitfalls.md

### Step 2: Locate the graph

Use the actual project's spec/ios-ui-graph directory, or the explicitly supplied graph path. All four files are a single input set. Do not substitute another project's graph.

### Step 3: Get the big picture

`python scripts/query_graph.py GRAPH_DIR screen_list`

This lists screens and recorded relationships; it is not proof of runtime reachability or complete source coverage.

### Step 4: Query based on user intent

| Command | Lookup | Result |
|---|---|---|
| migration_context | Screen name or canonical ID | Screen, full recorded component tree, navigation, resources and normalized layout summary |
| migration_component | Canonical component ID or explicit ios_id | Component, children, parents, siblings, resources and triggered edges |
| screen | Screen name or ID | Metadata, roots and navigation summary |
| component | Canonical component ID or explicit ios_id | Attributes and direct context |
| screen_list | none | Screen inventory |
| component_list | Screen name or ID | Flat component inventory for that screen |
| tree | Screen name or ID | Indented hierarchy |
| navigation | Screen name or ID | Incoming/outgoing edges |
| search | Keyword | Matching recorded nodes |

For example: `python scripts/query_graph.py GRAPH_DIR migration_context LoginView` or `python scripts/query_graph.py GRAPH_DIR component login_button`.

`ios_id` is an explicit native lookup value with kind/anchor metadata, not necessarily SwiftUI identity. Prefer canonical IDs when the source value is none, unknown, repeated or dynamic. Preserve original ambiguous/not-found outcomes; do not invent a match.

### Step 5: Present context or feed migration

Summarize screen/container ownership, actions, state/Binding, navigation, resources and unknowns. Feed complete returned JSON to the converter together with the page specification and selected Release source anchors. Query output is evidence, not a replacement for reading the source or an approval marker. Historical host_activity / parent_activity result slots are screen associations only.

## Multiple screens

Use screen_list, inspect each screen's migration_context, and follow the original indexed UI plan. Do not choose a new execution order or omit child screens because a query has few components.

## Evidence and compatibility

The unchanged original engine performs the queries. A temporary four-file wire view maps the native identity key with exactly the same values; it is removed after each call. Formal graph files remain unchanged. Returned JSON maps identity keys back to ios_id without changing text values. Each invocation stores original stdout/stderr, native display, adapter identity and formal/wire hashes outside the graph. See the builder schema §5. Missing/dual/non-native identity keys are never silently repaired. No source build or target behavior is inferred from a successful query.
