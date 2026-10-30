> 来源: ohpm 中央仓 README(T1 信源) | 包: `hsmeeting_hmos_sdk` | ohpm 最新版: 1.0.7 | 抓取: 2026-07-16
> 注意: 版本可能比市场快照新,以此为准时核对 CHANGELOG

# 红杉会议SDK

本模块为红杉会议核心SDK模块,包含会议全部功能,并提供加会接口。

包含视频、语音、文字、共享白板与屏幕等各类视频会议常用功能。

## 特别提醒

此SDK为红杉会议专用SDK,红杉会议为私有化部署的软件视频会议系统,因此需要对应的红杉会议服务器才可使用,如果您没有测试环境, 请联系红杉云官方获取测试环境。

联系方式:frank.wang@hongshantong.com

## 安装方式

```cmd

ohpm install hsmeeting_hmos_sdk

```

## 接口说明

### joinConf 接口

功能描述:加入会议

#### 接口定义

```typescript

joinConf(funcName: string, userId: number, confId: string, confPwd: string, joinName: string, confType: number, role: number, siteUrl: string, InviteUrl?: string)

```

#### 输入参数说明

| 参数名 | 类型 | 必填 | 说明 |

| --- | --- | --- | --- |

| funcName | string | 是 | 加会方法: - joinConf: 参会者加入会议 - startConf: 主持人加入会议 |

| userId | number | 是 | 用户Id,如果空,传0 |

| confId | string | 是 | 会议号 |

| confPwd | string | 是 | 会议密码 |

| joinName | string | 是 | 参会昵称 |

| confType | number | 是 | 会议类型,目前仅有固定视频会议,默认为2 |

| role | number | 是 | 参会角色: - 0: 主持人 - 1: 参加者 |

| siteUrl | string | 是 | 会议服务器地址 |

| InviteUrl | string | 否 | 会议中展示外部邀请页面,如不传,不显示邀请按钮 |
