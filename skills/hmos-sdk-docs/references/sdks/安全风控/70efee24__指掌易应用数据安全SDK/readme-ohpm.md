> 来源: ohpm 中央仓 README(T1 信源) | 包: `@zzy/uusafevsa` | ohpm 最新版: 1.0.0 | 抓取: 2026-07-16
> 注意: 版本可能比市场快照新,以此为准时核对 CHANGELOG

**K指掌易应用数据安全SDK**

**版权申明**

本文档版权归指掌易科技有限公司(以下简称“指掌易”)所有,并保留一切权利,非经本公司书面许可任何单位和个人不得擅自摘抄、复制本书内容的部分或者全 部,并不得以任何形式进行传播。对应本手册出现的其他公司的商标,产品标识和商品名称,由各自权利人拥有。除非另有约定,本手册仅作为使用指导,本手册中的所有陈述、信息和建议,不构成任何明示和暗示的担保。如需获取最新手册请联系指掌易科技有限公司产品部。

**免责声明**

本文档仅提供阶段性信息,所含内容可根据产品的实际情况随时更新,恕不另行通知。如因文档使用不当造成的直接或间接损失,本公司不承担任何责任

**联系我们**

网址:[www.zhizhangyi.com](http://www.zhizhangyi.com/)

服务电话:400 898 7798

地址:北京市朝阳区北苑路 58 号航空科技大厦 7 层

**下载安装**

    ohpm install @zzy/uusafevsa

# **1** API 文档说明

## **1** 基础配置

### **1.1.1** init

| 类名 | VsaSdk                                                 |

| ---- |--------------------------------------------------------|

| 方法 | static init(stage: AbilityStage, param?: VsaInitParam) |

| 描述 | 初始化 SDK 模块在 在AbilityStage的onCreate中调用。                 |

| 参数 | stage: AbilityStage对象, param: Vsa SDK 初始化参数,没有需要时可以不传  |

| 返回 | 无                                                      |

    示例

      import AbilityStage from '@ohos.app.ability.AbilityStage';

      import type Want from '@ohos.app.ability.Want';

      import { VsaSdk } from 'uusafevsa'

      

      export default class MyAbilityStage extends AbilityStage {

            onCreate(): void {

                  // 应用的HAP在首次加载的时,为该Module初始化操作

                  VsaSdk.init(this);

            }

            onAcceptWant(want: Want): string {

                  // 仅specified模式下触发

                  return 'MyAbilityStage';

            }

      }

### **1.1.2** 设置策略

| 类名 | VsaSdk                                                                                                                                                                                                                                                                                                                                                                                                                               |

| ---- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |

| 方法 | static setPermission(jsonStr: string): boolean                                                                                                                                                                                                                                                                                                                                                             |

| 描述 | 设置VSA安全策略 |

| 参数 | jsonStr: 策略json字符串                                                                                                                                                                                                                                                                           |

| 返回 | 设置策略是否成功                                                                                                                                                                                                                                                                                                                                                                                                                                  |
