## 蓝牙型智能密码钥匙集成说明 

### 一 . 集成 **SDK** 

1.1 导入 SDK 到 libs 目录 

(1)oh-package.json5 的"dependencies"修改如下,要求导入名必须和 har 同名、不区分大 

小写 

"standardhar": "file:./libs/StandardHar.har" 

(2)相应的导入语法改为如下 

import { Crypt, Standard } from 'standardhar'; 

import { IUKeyInterface, Consts, ErrorCodes } from 'standardhar'; 

(3)工程目录 build-profile.json5 添加如下项目,如果能正常编译也可以不加 

"app"."products" 

"buildOption": { 

"strictMode": { 

"useNormalizedOHMUrl": true 

} 

} 

# 二 **. SDK** 接口描述 

#### 2.1 签名流程 

接口调用顺序建议: 

蓝牙连接 

判断密码剩余次数(如果密码锁定,提示补发证书) 

判断是否默认密码(默认密码时,要提示设置密码) 

获取证书判断是否有证书(建议判断服务器上的证书状态是否正常,没有证书要提示失败, 

结束流程) 

弹出验证密码 

调用签名 

等待按键 

#### 2.1 盾管理流程 

建议调用流程: 

蓝牙连接 显示蓝牙 key 序列号 显示密码剩余次数 显示是否默认密码 

显示证书有效期(建议判断服务器上的证书有效期) 显示证书 CN(可以只显示签名证书)
