# hypium `aa test` 运行命令参考（第三步/执行用）

> 摘自官方 arkxtest README 的「专项能力 / 使用方式」段：`aa test` 的用例筛选(`-s class`/`-s notClass`)、
> 测试类型过滤、随机/压力/超时(`-s timeout`)、遇错即停(`-s breakOnError`)、空跑(`-s dryRun`)等参数。
> 完整 hypium API 见 [hypium.md](hypium.md)。

---

#### 专项能力

该项能力需通过在cmd窗口中输入aa test命令执行触发，并通过设置执行参数触发不同功能。另外，测试应用模型与编译方式不同，对应的aa test命令也不同，具体可参考[自动化测试框架使用指导](https://gitee.com/openharmony/docs/blob/master/zh-cn/application-dev/application-test/arkxtest-guidelines.md#cmd%E6%89%A7%E8%A1%8C)

- **筛选能力**

  1、按测试用例属性筛选

  可以利用框架提供的Level、Size、TestType 对象，对测试用例进行标记，以区分测试用例的级别、粒度、测试类型，各字段含义及代码如下：

  | Key      | 含义说明     | Value取值范围                                                                                                                                          |
  | -------- | ------------ |----------------------------------------------------------------------------------------------------------------------------------------------------|
  | level    | 用例级别     | "0","1","2","3","4", 例如：-s level 1                                                                                                                 |
  | size     | 用例粒度     | "small","medium","large", 例如：-s size small                                                                                                         |
  | testType | 用例测试类型 | "function","performance","power","reliability","security","global","compatibility","user","standard","safety","resilience", 例如：-s testType function |

  示例代码：

 ```javascript
 import { describe, it, expect, TestType, Size, Level } from '@ohos/hypium';

 export default function attributeTest() {
  describe('attributeTest', () => {
    it("testAttributeIt", TestType.FUNCTION | Size.SMALLTEST | Level.LEVEL0, () => {
      console.info('Hello Test');
    })
  })
}
 ```

  示例命令: 

  ```shell
  hdc shell aa test -b xxx -m xxx -s unittest OpenHarmonyTestRunner -s testType function -s size small -s level 0
  ```

  该命令作用是筛选测试应用中同时满足，用例测试类型是“function”、用例粒度是“small”、用例级别是“0”的三个条件用例执行。

  2、按测试套/测试用例名称筛选

  注意：测试套和测试用例的命名要符合框架规则，即以字母开头，后跟一个或多个字母、数字，不能包含特殊符号。

  框架可以通过指定测试套与测试用例名称，来指定特定用例的执行，测试套与用例名称用“#”号连接，多个用“,”英文逗号分隔

  | Key      | 含义说明                | Value取值范围                                                |
  | -------- | ----------------------- | ------------------------------------------------------------ |
  | class    | 指定要执行的测试套&用例 | ${describeName}#${itName}，${describeName} , 例如：-s class attributeTest#testAttributeIt |
  | notClass | 指定不执行的测试套&用例 | ${describeName}#${itName}，${describeName} , 例如：-s notClass attributeTest#testAttribut |

  示例代码：

  ```javascript
  import { describe, it, expect, TestType, Size, Level } from '@ohos/hypium';

  export default function attributeTest() {
  describe('describeTest_000',  () => {
    it("testIt_00", TestType.FUNCTION | Size.SMALLTEST | Level.LEVEL0,  () => {
      console.info('Hello Test');
    })

    it("testIt_01", TestType.FUNCTION | Size.SMALLTEST | Level.LEVEL0, () => {
      console.info('Hello Test');
    })
  })

  describe('describeTest_001',  () => {
    it("testIt_02", TestType.FUNCTION | Size.SMALLTEST | Level.LEVEL0, () => {
      console.info('Hello Test');
    })
  })
}
  ```

  示例命令1: 

  ```shell
  hdc shell aa test -b xxx -m xxx -s unittest OpenHarmonyTestRunner -s class describeTest_000#testIt_00,describeTest_001
  ```

  该命令作用是执行“describeTest_001”测试套中所有用例，以及“describeTest_000”测试套中的“testIt_00”用例。

  示例命令2：

  ```shell
  hdc shell aa test -b xxx -m xxx -s unittest OpenHarmonyTestRunner -s notClass describeTest_000#testIt_01
  ```

  该命令作用是不执行“describeTest_000”测试套中的“testIt_01”用例。

- **随机执行**

  使测试套与测试用例随机执行，用于稳定性测试。

  | Key    | 含义说明                             | Value取值范围                                  |
  | ------ | ------------------------------------ | ---------------------------------------------- |
  | random | @since1.0.3 测试套、测试用例随机执行 | true, 不传参默认为false， 例如：-s random true |

  示例命令：

  ```shell
  hdc shell aa test -b xxx -m xxx -s unittest OpenHarmonyTestRunner -s random true
  ```

- **压力测试**

  指定要执行用例的执行次数，用于压力测试。

  | Key    | 含义说明                             | Value取值范围                  |
  | ------ | ------------------------------------ | ------------------------------ |
  | stress | @since1.0.5 指定要执行用例的执行次数 | 正整数， 例如： -s stress 1000 |

  示例命令：

  ```shell
  hdc shell aa test -b xxx -m xxx -s unittest OpenHarmonyTestRunner -s stress 1000
  ```

- **用例超时时间设置**

  指定测试用例执行的超时时间，用例实际耗时如果大于超时时间，用例会抛出"timeout"异常，用例结果会显示“excute timeout XXX”

  | Key     | 含义说明                   | Value取值范围                                        |
  | ------- | -------------------------- | ---------------------------------------------------- |
  | timeout | 指定测试用例执行的超时时间 | 正整数(单位ms)，默认为 5000，例如： -s timeout 15000 |

  示例命令：

  ```shell
  hdc shell aa test -b xxx -m xxx -s unittest OpenHarmonyTestRunner -s timeout 15000
  ```

- **遇错即停模式**

  | Key          | 含义说明                                                     | Value取值范围                                        |
  | ------------ | ------------------------------------------------------------ | ---------------------------------------------------- |
  | breakOnError | @since1.0.6 遇错即停模式，当执行用例断言失败或者发生错误时，退出测试执行流程 | true, 不传参默认为false， 例如：-s breakOnError true |
  
  示例命令：

  ```shell
  hdc shell aa test -b xxx -m xxx -s unittest OpenHarmonyTestRunner -s breakOnError true
  ```
  
- **测试套中用例信息输出**

  输出测试应用中待执行的测试用例信息

  | Key    | 含义说明                     | Value取值范围                                  |
  | ------ | ---------------------------- | ---------------------------------------------- |
  | dryRun | 显示待执行的测试用例信息全集 | true, 不传参默认为false， 例如：-s dryRun true |

  示例命令：

  ```shell
  hdc shell aa test -b xxx -m xxx -s unittest OpenHarmonyTestRunner -s dryRun true
  ```

- **嵌套能力**

  1.示例代码
  ```javascript
  // Test1.test.ets
  import { describe, expect, it } from '@ohos/hypium';
  import test2 from './Test2.test';

  export default function test1() {
    describe('test1', () => {
      it('assertContain1', 0, () => {
        let a = true;
        let b = true;
        expect(a).assertEqual(b);
      })
      // 引入测试套test2
      test2();
    })
  }
  ```

  ```javascript
  //Test2.test.ets
  import { describe, expect, it } from '@ohos/hypium';

  export default function test2() {
    describe('test2', () => {
      it('assertContain1', 0, () => {
        let a = true;
        let b = true;
        expect(a).assertEqual(b);
      })
      it('assertContain2', 0, () => {
        let a = true;
        let b = true;
        expect(a).assertEqual(b);
      })
    })
  }
  ```

  ```javascript
  //List.test.ets
  import test1 from './nest/Test1.test';

  export default function testsuite() {
    test1();
  }
  ```

  2.示例筛选参数
    ```shell
    #执行test1的全部测试用例
    -s class test1 
    ```
    ```shell
    #执行test1的子测试用例
    -s class test1#assertContain1
    ```
    ```shell
    #执行test1的子测试套test2的测试用例
    -s class test1.test2#assertContain1
    ```

- **跳过能力**

    | Key          | 含义说明                                                     | Value取值范围                                        |
  | ------------ | ------------------------------------------------------------ | ---------------------------------------------------- |
  | skipMessage | @since1.0.17 显示待执行的测试用例信息全集中是否包含跳过测试套和跳过用例的信息 | true/false, 不传参默认为false， 例如：-s skipMessage true |
  | runSkipped | @since1.0.17 指定要执行的跳过测试套&跳过用例 | all，skipped，${describeName}#${itName}，${describeName}，不传参默认为空，例如：-s runSkipped all |

  1.示例代码
  
  ```javascript
  //Skip1.test.ets
  import { expect, xdescribe, xit } from '@ohos/hypium';
  
  export default function skip1() {
    xdescribe('skip1', () => {
      //注意：在xdescribe中不支持编写it用例
      xit('assertContain1', 0, () => {
        let a = true;
        let b = true;
        expect(a).assertEqual(b);
      })
    })
  }
  ```
  
    ```javascript
  //Skip2.test.ets
  import { describe, expect, xit, it } from '@ohos/hypium';
  
  export default function skip2() {
    describe('skip2', () => {
      //默认会跳过assertContain1
      xit('assertContain1', 0, () => {
        let a = true;
        let b = true;
        expect(a).assertEqual(b);
      })
      it('assertContain2', 0, () => {
        let a = true;
        let b = true;
        expect(a).assertEqual(b);
      })
    })
  }
    ```



### 使用方式

单元测试框架以ohpm包形式发布至[服务组件官网](https://ohpm.openharmony.cn/#/cn/detail/@ohos%2Fhypium)，开发者可以下载Deveco Studio后，在应用工程中配置依赖后使用框架能力，测试工程创建及测试脚本执行使用指南请参见[IDE指导文档](https://developer.harmonyos.com/cn/docs/documentation/doc-guides/ohos-openharmony-test-framework-0000001263160453)。
>**说明**
>
>1.0.8版本开始单元测试框架以HAR(Harmony Archive)格式发布
>
> 

