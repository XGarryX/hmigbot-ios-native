# Stage 1 源数据预检

执行 `python3 <runtime>/scripts/a2h_ios.py execution-contract --project <target> --apply`。
从 `spec/execution/source-ui/manifest.json` 按 page_id 取 snapshot_dir。
读取该目录的 meta.json、view.xml、原 page_spec、git facts/semantics 和当前源锚点。
这是真实源锚点与官方词项的静态投影；bounds 为空、状态 unknown，不是运行层级。
Phase A 用同一源证据补充语义；enrich 仅写该执行目录并记录补充来源，保留未知值。
发现新增页面、源变更或影响 AC 的状态缺失，回 a2h-spec/plan 受审更新，不能就地改冻结 baseline。
源读取统一使用 hmigbot_ios.execution_source.Source，不重跑 Garry 的另一套源解析器。
返回 page_id、source_root、page_spec、ui_info、target、owning_slice、wiring_ownership_map、registered_placeholders 和 owned_files。
禁止运行历史 ios-ui-graph-builder 合成命令代写 baseline；当前执行合同已提供所需 meta/outline。
页面未完成分析不得根据类名创建已转换空壳；源/计划失败保持 blocked。
