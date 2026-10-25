# 原生网络源码定点取证

Phase 0.2 和 Phase 1 优先消费本轮 `api-inventory.json` 的 static/auth_model/data_flows；它们是同一选定 target/Release 的输入。补漏与反查复用 `Source.files/text/code`，不能对未过滤源码直接搜索后把两条条件分支都计入事实。以下只读示例在当前迁移工程根执行，使用本项目安装的运行时：

```python
from pathlib import Path
import json, re, sys
project = Path.cwd().resolve()
sys.path.insert(0, str(project / '.agents/hmigbot-runtime/src'))
from hmigbot_ios152.source import Source
cfg = json.loads((project / '.migbot/config.json').read_text(encoding='utf-8-sig'))
source = Source((project / cfg['ios']['source_root']).resolve(), project)
# 按当前小节缩小关键词；结果仅为候选，须沿真实调用链确认字段和次序。
query = re.compile(r'URLSession|URLRequest|Alamofire|Moya|CodingKeys|JSONDecoder|JSONSerialization|SecItem|UserDefaults|CryptoKit|CommonCrypto|httpBody|httpMethod|setValue')
for name in sorted(source.files):
    original = source.text(name).splitlines()
    for line_no, code in enumerate(source.code(name, strings=True).splitlines(), 1):
        if query.search(code):
            print(f'{name}:{line_no}: {original[line_no-1].strip()}')
```

| 对账维度 | 定点读取的真实来源 |
|---|---|
| URL/方法 | URLSession/URLRequest、实际 Alamofire/Moya 或自定义客户端；追踪 base URL、路由和动态拼接 |
| 请求字段 | Encodable/CodingKeys、自定义 encode、JSONSerialization、字典/表单/multipart 的实际组装；常量和类型均记录 |
| 响应 | Codable/CodingKeys、解码策略、自定义 init(from:)、实际映射库；保留先失败的字段、默认值及外层壳处理顺序 |
| 签名 | 实际 CryptoKit/CommonCrypto 或三方实现；追踪输入拼接、UTF-8、排序、摘要/HMAC、hex/base64；不能假定算法 |
| 鉴权 | 获取→Keychain/UserDefaults/实际存储→注入→失效→清除→界面状态；保持取消、重试和设备/账号身份边界 |
| 公参/构建配置 | 实际已绑定的 Release 设置、Info.plist/xcconfig、Bundle、业务配置；设备信息与权限按实际 API 读取 |

Objective-C 的消息/selector、category 与桥接调用同样沿真实 `.m/.mm/.h` 反查，不只查 Swift 声明。关键词未命中不能证明不存在网络或签名。符号、字段和示例路径必须替换为本轮 Source 中的实际值；源码静态事实不等于后端已接受、凭据有效或设备实测。
