# 0.9.5 · 以 hmigbot-ios-main 为交付基准

日期：2026-10-23。本轮代码、测试、文档与版本修改直接位于hmigbot-ios-main；临时目录仅存补丁传输材料、夹具和日志，不再维护独立的整包实现。

## 已核实的差异原因

修改前，0.9.4 ZIP的5088个交付文件与目录内同路径文件SHA-256逐项一致。源目录另有8个系统/字节码缓存文件未入ZIP。但旧打包器将顶层名固定改为hmigbot-ios，并将5006项0664改为0644、26项0775改为0755、38项0664改为0755；统一时间戳和README主标题仍标0.9.2也使比较和版本识别混乱。压缩体积492935708字节，而原始交付文件1286121387字节，压缩大小不能作为删减内容的依据。

## 当前目录中的修正

- scripts/package_plugin.py直接从自身所在源码目录构建，输出必须位于源目录外。
- scripts/package_tree.py枚举源树，保留目录名、文件字节、权限、修改时间（ZIP两秒精度）和空目录，新增根配置文件不被固定顶层白名单遗漏。
- 排除.git、Python缓存、测试缓存、虚拟环境、node_modules、build/dist/work、Swift构建缓存及已安装的本地状态目录；具体观察到的排除路径及原因写入ZIP旁的manifest，不静默遗漏。
- scripts/verify_package.py核对源目录、ZIP和旁置清单的逐项路径、SHA-256及元数据；检查源变化、包篡改和重复/越界路径。ZIP不承载文件系统所有者或扩展属性。
- scripts/smoke_package.py先验证ZIP清单，再从清单根名定位安装源。测试覆盖新根配置、二进制字节、空目录、权限/时间保留及源变化；原资源/OC回归继续在安装态运行。

0.9.3优化仍在原src/skills/scripts等目录；0.9.4修复仍在src/hmigbot_ios/source_scope.py、ios_harness.py和quality_views.py，回归位于tests/test_resource_preview_routing.py。Swift与OC源分析保留，plist元数据按二进制/XML解析，Preview专用扫描只解释Swift。没有通过删资源或删义务消除差异。

## 生产与核对

在本源目录运行：

```sh
python3 scripts/package_plugin.py --output ../releases/hmigbot-ios-main-0.9.5.zip
python3 scripts/verify_package.py --package ../releases/hmigbot-ios-main-0.9.5.zip --source .
python3 scripts/smoke_package.py --package ../releases/hmigbot-ios-main-0.9.5.zip --output ../releases/package-check.json
```

ZIP及两个sidecar保留在一起。旧归档不覆盖。版本与文档变化会使整包校验和自然改变，不能与旧ZIP哈希混用。真实测试结果及最终源目录核对见随交付发布目录的validation-summary.json、source-package-check.json和package-smoke.json；这些收据在包外产生，避免打包后回写源文件使清单过期。

本轮只处理工具目录及交付一致性，不修改当前迁移工程的安装副本、业务源码、spec或账本；macOS arm64安装验证不代表真实App HAP或双端行为通过，未上传服务器。
