> 来源: ohpm 中央仓 README(T1 信源) | 包: `@hnxaca/hnxacasdk` | ohpm 最新版: 1.0.3 | 抓取: 2026-07-16
> 注意: 版本可能比市场快照新,以此为准时核对 CHANGELOG

# 云签名SDK

## 简介与推荐
以国密核心专利算法为依托,为移动终端第三方应用提供密钥管理、密码运算和数据安全存储服务。

通过API调用为移动终端第三方应用开发者提供了完善的密钥管理和密码计算功能,可以有效保证密钥本身以及敏感数据的机密性和完整性。

### 应用领域主要包括:
(1)电子政务:可用于文件数据保护、用户身份认证、公文流转、网上办事大厅以及审批等环节,保证电子政务数据的完整、可信、和可用。

(2)企业办公信息化:可用于办公权限管理、工作流程确认、以及身份认证等环节,确保企业办公信息化系统安全可靠。

(3)电子商务:可用于各级网络电子商务服务系统提供用户订单交易确认、交易签名、身份认证等安全认证功能;

## 安装
> ohpm install @hnxaca/hnxacasdk

## 使用

### 请参考官方文档:http://125.46.86.254:8082/harmony/hnxacayqmsdk.html
 
### 1. 使用示例

#### 1.导入文件

```typescript
import { UserCertInfo,CertDetailInfo, HnXacaSdk, HnResponseObj,SoftKeySuppliers } from '@hnxaca/hnxacasdk'
```

#### 2. 初始化

```typescript
HnXacaSdk.getInstance().initSdk(getContext(), CommonConstants.APP_KEY, CommonConstants.TEST_PHONE, SoftKeySuppliers.ZY,(result:HnResponseObj)=>{})
```

**参数说明**

| 参数       | 类型 | 说明       | 是否必须 | 参数选项 |---------|---------|----------|----------|----------|
| context  | Context| 调用者的上下文环境 | 是 |
| thirdAppKey | string | App调用sdk的授权码 | 是 | 为开发者分配的业务授权码 | 
| thirdAppUserName | string | 调用者 App 用户唯一标识 | 是 | 调用者业务 APP用户唯一 标识 |
| keySupplier | SoftKeySuppliers | 证书类型 | 是 | SoftKeySuppliers.ZY |
| callBack | HnResponseObj | 结果回调 | 是 |  |

#### 3. 申请证书

```typescript
 HnXacaSdk.getInstance().applyCertNoPage("PIN码", userCertInfo,(result: HnResponseObj)=>{ })
```

**参数说明**

| 参数       | 类型 | 说明       | 是否必须 | 参数选项 |---------|---------|----------|----------|----------|
| pin  | string | 数字证书 pin 码 | 是 | |
| userCertInfo | UserCertInfo | 数字证书信息类 | 是 |  | 
| callBack | HnResponseObj | 结果回调 | 是 |  |

#### 4、P7签名

```typescript
HnXacaSdk.getInstance().initSdk(getContext(this),CommonConstants.APP_KEY,CommonConstants.TEST_PHONE,SoftKeySuppliers.ZY,(result: HnResponseObj)=>{ });
```

**参数说明**

| 参数       | 类型 | 说明       | 是否必须 | 参数选项 |---------|---------|----------|----------|----------|
| pin  | string | 数字证书 pin 码 | 是 | |
| businessNo | string | 事务代码 | 是 |  | 
| data | string | 原文 | 是 |  | 
| callBack | HnResponseObj | 结果回调 | 是 |  |
