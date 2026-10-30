> 来源: ohpm 中央仓 README(T1 信源) | 包: `@wanshu/realauthsdk` | ohpm 最新版: 1.0.0 | 抓取: 2026-07-16
> 注意: 版本可能比市场快照新,以此为准时核对 CHANGELOG

# 实人SDK

## 简介与推荐
实人认证SDK,整合活体检测、身份证OCR、人像比对、身份证二要素比对四大要素。提高线上实人认证用户体验和移动端平台效率。

## 安装
> ohpm install @wanshu/realauthsdk

## 官方地址
[文档说明](https://doc.chuanglan.com/document/VTYS7IQDCLTFL3N4)

## demo下载地址
[示例Demo](https://doc.chuanglan.com/document/Q9V7D0MRTJG6C3VB)

## 合规说明
[实人认证SDK隐私政策](https://doc.chuanglan.com/document/ELA9JASF18PFUOZ7)

[实人认证SDK合规使用指南](https://doc.chuanglan.com/document/Z5352AJMKNBTQ4F0)

## 使用

### 1. 初始化

```typescript
 import {CLConfigureUtil,CLOCRManager,CLRealPersonManager } from '@wanshu/realauthsdk'

 // 设置token
 CLConfigureUtil.setToken("<#token#>")
```

### 2. 活体检测

```c
// 添加延时防止获取不到surfaceId
setTimeout( ()=>{
      // 配置相机视图
      CLRealPersonManager.getInstance().initWithRecordView(this.context,this.surfaceId)
      // 设置超时时间
      CLRealPersonManager.getInstance().setTimeoutInterval(30)
      // 设置检测动作个数及安全标准
      CLRealPersonManager.getInstance().setActionNumer(1,0)
      // 设置动作的检测时长,默认为2s
      CLRealPersonManager.getInstance().setActionDuration(2)
      // 启动活体检测
      CLRealPersonManager.getInstance().startLiveDetectWithActionsHandler((params:CLTypeParamObject,url?:string)=>{

      },(status:CLStatus,params:ESObject)=>{
      })
    },200)
```

### 3. OCR识别

#### 身份证双面识别

```c
/**
   * 身份证OCR接口    ⚠️ 先调用人像面(图片大小建议压缩为1M以内,超过会被SDK压缩)
   * @param image: 传入的身份证图片
   * @param isFront: true:人像面;false:国徽面
   * @return s Promise<Object> 返回结果:
   * @example
   * 国徽面数据 :{
                 "expire_date"       = "失效日期";
                 "issuing_authority" ="签发机关";
                 "issuing_date"      = "签发日期";
               };
   *人像面数据:{
                  "address"    = "地址";
                  "brith_day"  = "出生日期";
                  "id_card_no" = "身份证号";
                  "name"       = "姓名";
                  "nation"     = "民族";
                  "sex"        = "性别";
               };
   * */
  static async realPersonOCROfSignal(image: PixelMap, isFront: boolean): Promise<Object> 
```

#### 身份证单面识别

```c
/**
   * 身份证OCR接口    识别人像面和国徽面(单图片大小建议压缩为1M以内,超过会被SDK压缩)
   * @param frontImagePixMap 人像面照片
   * @param backImagePixMap  国徽面照片
   * @return s Promise<Object> 返回结果
   * @example {
              back = {
                       "expire_date"       = "失效日期";
                       "issuing_authority" = "签发机关";
                       "issuing_date"      = "签发日期";
                     };
             front =  {
                       "address"    = "地址";
                       "brith_day"  = "出生日期";
                       "id_card_no" = "身份证号";
                       "name"       = "姓名";
                       "nation"     = "民族";
                       "sex"        = "性别";
                      };
   * */
  static async realPersonOCR(frontImagePixMap: PixelMap, backImagePixMap: PixelMap): Promise<Object> 
```

#### 身份证认证

```c
/**
   * 身份证认证
   * @param name:姓名
   * @param idNumber:身份证号码
   * @return s Promise<Object> 返回结果:
   * @example {
                "order_no"  : "业务唯一流水号",
                "city"      : "城市",
                "country"   : "县区",
                "gender"    : "性别:1:男、2:女",
                "age"       : "年龄",
                "remark"    : "备注,例:一致",
                "birthday"  : "生日,格式是yyyyMMdd",
                "result"    : "返回结果: 01-认证一致(收费) 02-认证不一致(收费) 03-认证不确定(收费)   04-认证失败(不收费)",
                "handle_time" : "查询时间 例:2018-04-09 15:05:01",
                "province"  : "省份"
              }
   * */
  static async realPersonDetect(name: string, idNumber: string): Promise<Object>
```
