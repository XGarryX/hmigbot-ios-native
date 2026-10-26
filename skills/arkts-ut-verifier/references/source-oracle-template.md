# F001 source oracle

```yaml
source_platform: ios
feature: F001
feature_file: <实际主 spec>
source_root: <实际源根>
source_sha256: <已核验源快照>
collection_complete: false
oracle_status: partial
```

| 稳定 AC | 前态/输入 | 事件 | 期望/后态/副作用 | 真值类型 | 源 path:line | 限制/批准差异 |
|---|---|---|---|---|---|---|

## 完整性与未知项
列具体集合、已读成员、未能闭合的调用/继承/动态行为、需要的证据。
只有全量核对后 collection_complete=true；full/partial 与是否执行测试是不同维度。
不从源 enum 声明顺序猜 raw value，不将缺字段、缺设备当空值或通过。
