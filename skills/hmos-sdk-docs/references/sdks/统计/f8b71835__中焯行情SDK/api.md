# **中焯行情SDK数据接口说明-HarmonyOS NEXT** 

## **版本更新说明** 

## **目的** 

## **形式说明** 

# **快速接入指南** 

##### **环境配置** 

// == SDK配置 == // 

- SseSdk.setDebug(true);//调试开关,输出log,生产环境需注释掉 let sseConfig = new  SSeConfig() 

config.setAppkey(appKey)//appkey传入与包名对应的key 

- .setContext(this.context) 

SseSdk.setConfig(sseConfig); 

// ==权限配置(备注: 以上配置信息可放在Application里,若不配置权限,港股默认为沪港1档与深港1 档,其他市场默认为 level1)== // 

SseSdk.permission().setLevel\(ZZPermission.LEVEL_2) //配置沪深境内权限 .addHkPermission\ 

(ZZPermission.HKA1,ZZPermission.HKD1,ZZPermission.SZHK5,ZZPermission.SHHK5,ZZPermission.HK 10,ZZPermission.HKAZ)//添加港股/港股指数权限 

- .addHKOverseaPermission\(ZZPermission.OL_HK10)//添加港股境外10档权限 

- .addHKOverseaPermission\(ZZPermission.OL_HKA1) //添加港股境外实时1档权限 

- .addShSzOverseaPermission\(ZZPermission.OL_LEVEL_1) //添加沪深境外权限 沪深Level1 

- .setSseLevel\(ZZPermission.LEVEL_1) //统一设置大商所、郑商所、全球、外汇市场的level 

- //单独设置沪深权限,设置后setLevel方法不起效果,不单独设置则setlevel继续有效 

- .addShSzPermission\(ZZPermission.SH_LEVEL_2) //添加l2默认会有level1,可以不添加level1 

- .addShSzPermission\(ZZPermission.SZ_LEVEL_2)//否则想要level1则要添加level1 

- .addShSzPermission\(ZZPermission.SH_LEVEL_1) 

- .addShSzPermission\(ZZPermission.SZ_LEVEL_1) 

- //注意:初始化时,配置权限禁止调用submit,后续操作权限才能调用submit方法 .submit();        //权限设置完,统一调用该方法, 更新港股境外权限,切换推送连接 

##### **所需应用权限** 

"requestPermissions": [ {"name":"ohos.permission.INTERNET"}, {"name": "ohos.permission.GET_NETWORK_INFO"}, {"name": "ohos.permission.GET_WIFI_INFO"} ] 

##### **注册认证** 

应用程序接口说明: 每次注册需要重新创建新的实体,每次启动APP只需要注册一次,之后SDK会处理 

```arkts
let registerReq = new ZZRegisterReq() registerReq.send({ onSuccess: (resp: RegisterResp) => { //注册成功 }, onFail: (err: ErrorInfo) => { //注册失败 } }); 
```

##### **行情Level切换监听** 

如果使用L2行情,需要监听通知, setIpAndLevelChangedListener ,监听行情级别的切换,使前端UI界面做调整 注意:该监听方法需放在注册代码之后执行,不是注册回调之后 行情切换回调详情参考LevelInstruction 

SseSDK.setIpAndLevelChangedListener({ ipChanged:(ipOwn: string)=>{ console.info("ipChanged => ipOwn :" + ipOwn) }, onLevelChanged:(market: string, status: string) =>{ console.info("onLevelChanged => market :" + market + " , status: " + status) } }) 

##### **调用示例(获取股票快照信息)** 

```arkts
let request = new QuoteDetailReq() request.code = "600000.sh" request.send({ onSuccess: (resp: ZZQuoteResp) => { //请求成功 }, onFail: (err: ErrorInfo) => { //请求失败 } }); 
```

### **市场** 

##### **市场列表** 

|**市场**|**名称**|**代码后缀**|**备注**|
|---|---|---|---|
|上海|ZZMarketType.SH|sh||
|深圳|ZZMarketType.SZ|sz||
|香港|ZZMarketType.HK|hk||
|新三板|ZZMarketType.BJ|bj||
|中金所|ZZMarketType.CFF|cff||
|大商所|ZZMarketType.DCE|dce||
|郑商所|ZZMarketType.CZCE|czce||
|上期所|ZZMarketType.SHFE|shfe||
|上期所原油|ZZMarketType.INE|ine||
|海外市场|ZZMarketType.GB|gb|收盘行情|
|沪伦通|ZZMarketType.UK|uk||
|板块指数|ZZMarketType.BK|bk||
|中证指数|ZZMarketType.CSI|csi||
|北交所|ZZMarketType.BZ|bz||

**市场分类** 

|**市场**|**备注**|
|---|---|
|指数分类代码||
|沪深分类代码||
|股转系统(新三板)||
|中金所||
|大商所||
|郑商所||
|上期所||
|上期所原油||
|港股市场||
|海外市场||
|全球指数||
|外汇||
|中证指数||
|北交所||
|沪深京分类||

|**指数分类代码**|||
|---|---|---|
|**名称**|**说明**|**备注**|
|指数代码(000001.sh)|指数成分股||

###### **沪深分类代码** 

|**名称**|**说明**|**备注**|**名称**|**说明**|**备注**|**名称**|**说明**|**备注**|
|---|---|---|---|---|---|---|---|---|
|~~SH1000~~|~~上证优先股~~|~~废~~ ~~弃~~|~~SZ1000~~|~~深证优先股~~|~~废~~ ~~弃~~||||
|SH1001|上证A股||SZ1001|深证A股||SHSZ1001|沪深A股||
|SH1002|上证B股||SZ1002|深证B股|||||
||||SZ1004|创业板|||||
|SH1005|主板A股||SZ1005|主板A股|||||
|SH1006|科创板||||||||
|SH1011|上证新股||SZ1011|深证新股|||||
|||~~废~~|||~~废~~||||

|~~SH1012~~|~~上证配股~~|~~弃~~|~~SZ1012~~|~~深证配股~~|~~弃~~|||
|---|---|---|---|---|---|---|---|
|SH1100|上证基金||SZ1100|深证基金||SHSZ1100|沪深基金|
|SH1110|上证LOF||SZ1110|深证LOF||SHSZ1110|LOF基金|
|SH1120|上证ETF||SZ1120|深证ETF||SHSZ1120|ETF基金|
|SH1140|上海封闭式基金||SZ1140|深圳封闭式基金||||
|SH1300|上证债券||SZ1300|深证债券||SHSZ1300|沪深债券|
|SH1310|债券现货(沪)||SZ1310|债券现货(深)||||
|SH1311|国债逆回购(沪)||SZ1311|国债逆回购(深)||SHSZ1311|沪深国债逆回购股票|
|SH1312|上证可转债||SZ1312|深证可转债||SHSZ1312|沪深可转债|
|SH1313|上证国债||SZ1313|深圳国债||SHSZ1313|国债|
|SH1314|上证企业债||SZ1314|深圳企业债||SHSZ1314|企业债|
|~~SH1321~~|~~债券合格投资者~~|~~废~~ ~~弃~~|~~SZ1321~~|~~债券合格投资者~~|~~废~~ ~~弃~~|||
|~~SH1322~~|~~债券合格机构投资者~~|~~废~~ ~~弃~~|~~SZ1322~~|~~债券合格机构投资者~~|~~废~~ ~~弃~~|||
|SH1400|上海指数||SZ1400|深证指数||SHSZ1400|沪深指数|
|SH1500|创新企业股票&存托凭 证||SZ1500|创新企业股票&存托凭证||SHSZ1500|创新企业股票&存托凭 证|
|SH1510|创新企业股票||SZ1510|创新企业股票||SHSZ1510|创新企业股票|
|SH1520|CDR(存托凭证)||SZ1520|CDR(存托凭证)||SHSZ1520|CDR(创新企业)|
|~~SH1530~~|~~CDR(沪伦通)~~||~~UK1530~~|~~CDR基础证券(沪伦~~ ~~通)~~||||
|SH1540|GDR基础证券(沪伦通)||UK1540|GDR(沪伦通)||||
||||~~SZ1600~~|~~权证~~|~~废~~ ~~弃~~|||
|SH3002|上证期权||SZ3002|深圳期权||||
|SHS|上证风险(包含退市整 理)||SZS|深证风险(包含退市整理)||SHSZS|风险警示(包含退市整 理)|
|SHP|上证退市||SZZ|深证退市||SHSZP|退市整理|
|~~Risk~~|~~风险警示~~|~~废~~ ~~弃~~||||||
|~~Delist~~|~~退市整理~~|~~废~~ ~~弃~~||||||
|~~SH9001~~|~~上证非交易~~|~~废~~ ~~弃~~|~~SZ9001~~|~~深圳非交易~~|~~废~~ ~~弃~~|||
|~~SH9800~~|~~已退市~~|~~废~~ ~~弃~~|~~SZ9800~~|~~已退市~~|~~废~~ ~~弃~~|||
|~~SH9900~~|~~名称变更~~|~~废~~ ~~弃~~|~~SZ9900~~|~~名称变更~~|~~废~~ ~~弃~~|||

###### **股转系统(新三板)** 

**名称 说明 备注** 

|BJ1000|新三板|除指数|
|---|---|---|
|BJ1400|三板指数|证券代码前三位899|
|BJ1001|两网及退市||
|BJ100101|两网及退市A股|证券代码前三位为400|
|BJ100102|两网及退市B股|证券代码前三位为420|
|BJ1002|优先股|证券代码前三位为820|
|BJ1003|首日挂牌|证券代码前两位为43或83、87,并且交易转让状态为Y|
|BJ1004|增发挂牌|证券代码前两位为43或83、87,并且交易转让状态为D|
|BJ1005|创新层||
|BJ100501|创新层集合竞价转让||
|BJ100502|创新层做市转让||
|BJ100503|创新层挂牌公司连续竞价股票||
|BJ1006|基础层||
|BJ100601|基础层集合竞价转让||
|BJ100602|基础层做市转让||
|BJ100603|基础层挂牌公司连续竞价股票||
|BJ1007|集合竞价转让|转让交易类型为C|
|BJ100701|集合竞价转让基础层||
|BJ100702|集合竞价转让创新层||
|BJ100703|集合竞价转让精选层||
|BJ1008|做市转让|交易转让类型为M|
|BJ100801|做市转让基础层||
|BJ100802|做市转让创新层||
|BJ100803|做市转让精选层||
|BJ1009|协议转让|交易转让类型为T|
|BJ1010|连续竞价转让|交易转让类型为B|
|BJ101001|连续竞价转让基础层||
|BJ101002|连续竞价转让创新层||

|BJ101003|连续竞价转让精选层||
|---|---|---|
|BJ1011|股权激励期权|证券代码前三位为850|
|BJ1012|挂牌公司|证券代码前两位为43或83、87|
|BJ1013|要约回收购|证券代码前两位为84|
|BJ101301|要约收购|证券代码前三位为840|
|BJ101302|要约回购|证券代码前三位为841|
|BJ1312|可转债||
|BJ131201|基础层可转债||
|BJ1312|创新层可转债||

###### **港股市场** 

|**名称**|**说明**|**备注**|
|---|---|---|
|HK1000|港股主板||
|HK1010|港股||
|HK1004|创业板||
|HK1100|基金||
|HK1300|债券||
|HK1400|香港指数||
|HK1500|牛熊证||
|HK1600|涡轮||
|HKAHG|AH股||
|HKGQ|国企股||
|HKHC|红筹股||
|HKHGT|沪股通||
|HKSGT|深股通||
|HKLC|蓝筹股||
|HSI|恒指成分股||
|HKTong|港股通(沪深)||
|HKUA2301|港股通(沪)||
|SZHK|港股通(深)||
|SHHGT|沪港通(纯标的)||
|SZSGT|深港通(纯标的)||
|HKGGT|港股通(沪深纯标的)||
|~~HKRed~~|~~红筹股~~|~~废弃~~|
|~~HKAH~~|~~AH股~~|~~废弃~~|
|~~SHTone~~|~~沪股通~~|~~废弃~~|
|~~HKTone~~|~~港股通~~|~~废弃~~|

|**海外市场**|
|---|

|**名称**|**说明**|**备注**|
|---|---|---|
|GB1400|全球指数(收盘行情)|海外市场|
|GB1001|外汇(收盘行情)|海外市场|

|**中金所**|||
|---|---|---|
|**名称**|**说明**|**备注**|
|CFF_all|所有证券|老版本all|
|CFF_index_future|中证沪深上证的合约|老版本if|
|CFF_treasury_future|2年5年10年国债的合约|老版本tf|
|CFF_future|所有中金所期货合约||
|CFF_IC|中证||
|CFF_IF|沪深||
|CFF_IH|上证||
|CFF_T|10年国债||
|CFF_TF|5年国债||
|CFF_TS|2年国债||
|CFF_if_month|中证沪深上证的当月及下月合约||
|CFF_option|中金所所有期权标的||
|CFF_underlying|中金所期权(沪深300股指期权)连续合约标的||
|CFF _expiremonth_IO|中金所期权(沪深300股指期权)年月板块||
|CFF_T_IO2205|中金所期权(沪深300股指期权2205)的认沽认购合约||

**大商所** 

|**名称**|**说明**|**备注**|
|---|---|---|
|DCE_all|大商所所有合约||
|DCE_future|大商所所有期货||
|DCE_option|大商所所有期权合约||
|DCE_bb|胶合板||
|DCE_a|豆一||
|DCE_b|豆二||
|DCE_cs|玉米淀粉||
|DCE_c|玉米||
|DCE_l|聚乙烯||
|DCE_m|豆粕||
|DCE_pp|聚丙烯||
|DCE_p|棕榈油||
|DCE_v|聚氯乙烯||
|DCE_y|豆油||
|DCE_jd|鸡蛋||
|DCE_jm|焦煤||
|DCE_j|焦炭||
|DCE_i|铁矿石||
|DCE_fb|纤维板||
|DCE_eg|乙二醇||
|DCE_T_m1903|大商所期权豆粕1903的认沽认购合约, (其中m1903可以为 DCE_expiremohth返回的任一code)||
|DCE_underlying|大商所大豆标的及玉米标的的连续合约||
|DCE_expiremonth_m|大商所豆粕期权所属期货年月板块||
|DCE_expiremonth_c|大商所玉米期权所属期货年月板块||

|**郑商所**|
|---|

|**名称**|**说明**|**备注**|
|---|---|---|
|CZCE_all|郑商所所有合约||
|CZCE_future|郑商所所有期货||
|CZCE_option|郑商所所有期权合约||
|CZCE_AP|苹果||
|CZCE_RI|早籼稻||
|CZCE_LR|晚籼稻||
|CZCE_JR|粳稻||
|CZCE_OI|菜籽油||
|CZCE_TA|PTA||
|CZCE_PM|普麦||
|CZCE_MA|甲醇||
|CZCE_FG|玻璃||
|CZCE_RS|油菜籽||
|CZCE_RM|菜籽粕||
|CZCE_ZC|动力煤||
|CZCE_SF|硅铁||
|CZCE_SM|锰硅||
|CZCE_CY|棉纱||
|CZCE_SR|白糖||
|CZCE_WH|强麦||
|CZCE_CF|郑棉||
|CZCE_T_SR001|郑商所期权白糖001的认沽认购合约,(其中SR001可以为 CZCE_expiremohth返回的任一code)||
|CZCE_underlying|郑商所白糖标的及郑棉标的的连续合约||
|CZCE_expiremonth_SR|郑商所白糖期权所属期货年月板块||
|CZCE_expiremonth_CF|郑商所郑棉期权所属期货年月板块||

**上期所** 

|**名称**|**说明**|**备注**|
|---|---|---|
|SHFE_all|上期所所有合约||
|SHFE_future|上期所所有期货合约||
|SHFE_option|上期所所有期权合约||
|SHFE_index|上期所所有指数合约||
|SHFE_cu|沪铜||
|SHFE_al|沪铝||
|SHFE_fu|燃料油||
|SHFE_ru|天然橡胶||
|SHFE_zn|沪锌||
|SHFE_au|黄金||
|SHFE_rb|螺纹钢||
|SHFE_wr|线材||
|SHFE_pb|沪铅||
|SHFE_ag|白银||
|SHFE_bu|石油沥青||
|SHFE_hc|热轧卷板||
|SHFE_ni|沪镍||
|SHFE_sn|沪锡||
|SHFE_sp|纸浆||
|SHFE_IMCI|上期有色金属指数||
|SHFE_T_ru1905|上期所期权天然橡胶1905的认沽认购合约(其中ru1905可以为 SHFE_expiremohth返回的任一code)||
|SHFE_underlying|上期所沪铜标的及天然橡胶标的的连续合约||
|SHFE_expiremonth_cu|上期所沪铜期权所属期货年月板块||
|SHFE_expiremonth_ru|上期所天然橡胶期权所属期货年月板块||

|**上期所原油**|
|---|

|**名称**|**说明**|**备注**|
|---|---|---|
|INE_all|所有上期所原油市场合约||
|INE_future|所有上期所原油市场期货合约||
|INE_sc|原油||
|INE_nr|20号胶||

###### **全球指数** 

|**名称**|**说明**|**备注**|
|---|---|---|
|~~GI1400~~|~~全球指数~~|废弃|

###### 外汇 

|**名称**|**说明**|**备注**|
|---|---|---|
|~~FE1100~~|~~全球外汇~~|废弃|
|~~FE1000~~|~~外汇~~|废弃|
|~~FE1200~~|~~人⺠币中间价~~|废弃|
|**名称中证指数**|**说明**|**备注**|
|CSI1400|中证指数||

###### **北交所** 

|**名称**|**说明**||**备注**|
|---|---|---|---|
|BZ1001|北交所A股|||
|BZ10011|北交所首日挂牌|||
|BZ10012|北交所增发挂牌|||
|BZ1011|北交所发行信息|||
|BZ10111|北交所申购发行信息|||
|BZ10112|北交所询价发行信息|||
|BZ1300|北交所债券|||
|BZ1312|北交所可转债|||
|BZ1400 **沪深京分类**|北交所指数|||
|**名称**|**说明**|**备注**||
|SHSZBZ1001|沪深京A股|||
|SHSZBZ1300|沪深京债券|||
|SHSZBZ1312|沪深京可转债|||
|SHSZBZ1400|沪深京指数|||
|SHSZBZ1005|沪深主板,北证股票|SH1005,SZ1005,|BZ1001的合集|

##### **板块分类** 

|**名称**|**说明**|**ID属性前两位**|
|---|---|---|
|Notion|概念板块|E0|
|Area|地区板块|F1|
|Trade|证监会行业一级|A1|
|Trade|证监会行业二级|A2|
|Trade_sw1|申万一级行业|D1|
|Trade_sw|申万二级行业|D2|
|Notion_szyp|优品概念板块|(使用优品板块需要特别申请)J1|
|Area_szyp|优品地区板块|(使用优品板块需要特别申请)I1|
|Trade_szyp|优品行业板块|(使用优品板块需要特别申请)H1|
|Trade_fz|小方行业板块|G1|

### **行情接口列表** 

##### **使用需知** 

- 提供的接口必须在认证成功之后才能正常使用 

- 站点列表轮询时间 默认时间为10S 

- 设置用户权限不需要重新调用注册接口 

- 关于subtype,需要使用subtype的接口,请使用从行情接口返回的ZZQuoteItem.subtype,不要手动填写 推荐使用请求方式 TCP订阅,实时、高效 

   - 目前支持市场沪、深、京、港、中证指数 

   - 支持接口 证券行情列表、证券行情快照、分时走势数据、分笔明细、逐笔、千档 

   - 使用TCP订阅行情,成功以后再发送订阅(订阅的上限:单市场不超过400) 

###### 轮询模式 

- 轮询行情源下发行情快照,每3S一幅,所以如果使用定时刷新,最快刷新频率为3S 

- 自选接口单市场支持200条,其中期货市场50条 

- 自选、列表 使用自定义,节省流量、提高性能 

- 非交易阶段取消定时轮询 

- 调查发现非相关接口调用频繁,建议在当前页面,只请求相关接口 

##### **辅助接口** 

|**说明**|**类名**|**备注**|
|---|---|---|
|应用程序接口类|ZZRegisterReq|SDK初始化:注册认证|
|站点管理|SiteManagerUtils|获取、设置某市场站点|
|站点ping测速|PingReq|站点测速|

##### **Level-1接口** 

|**行情接口分类**|**接口名称**|**请求列表**|**备注**|
|---|---|---|---|
|在线搜索|股票搜索|ZZSearchReqV2||
|自选快照|证券行情列表|ZZQuoteReq|建议使用 TCP订阅|
|证券行情快照|证券行情快照|ZZQuoteDetailReq|建议使用 TCP订阅|
|UK市场快照详情|UK市场快照详情|ZZUKQuoteReq||
|联动请求|AH联动|ZZAHLinkReq||
||可转债与正股联动|ZZKZZLinkReq||
||GDR\CDR联动|ZZDRLinkReq||
||AB股联动接口|ZZABLinkReq||
|分时线图|走势数据|ZZChartReq|建议使用 TCP订阅|
||历史分时|HistoryChartReq||
||走势增值指标|ZZChartIndexReq|沪深|
||集合竞价走势|ZZBidChartReq||
|历史K线|历史K线数据|ZZOHLCReq||
||历史K线增值数据|ZZOHLCIndexReq||
|分笔|分笔明细|ZZTickReq|建议使用 TCP订阅|
|列表|分类涨跌幅排行|ZZCateSortingReq||
||板块类别个股列表|ZZCategoryCodeReq||
|联动列表行情|AH股列表|ZZAHListReq||
||GDR\CDR列表|ZZDRListReq||

||AB股列表接口|ZZABListReq||
|---|---|---|---|
||可转债行情列表|ZZKZZListReq||
|板块|板块排行|ZZSectionSortingReq|沪深|
||个股所属板块行情|ZZSectionQuoteReq|沪深京|
||个股所属行业板块列表|ZZSectionStockReq|沪深京|
|涨跌统计|沪深京当日涨跌统计数据|ZZMarketUpdownsReq||
||当日或30日复盘涨跌请求|ZZCompoundUpdownsReq||
|期权|期权-商品行情列表|ZZOptionReq||
||期权-T型报价|ZZOptionTReq||
||期权-标的行情|ZZUnderlyingStockReq||
||期权-交割月|ZZExpireMonthReq||
|港股市场行情|波动调节等讯息|ZZHKStockInfoReq||
|次新股|次新股|ZZSubnewStockReq||
|次新债|次新债|ZZSubnewBondReq||
|市场当年交易日接口|市场当年交易日接口|ZZTradeDateReq||
|涨停统计|涨停统计|ZZZTSortingReq||
|港股通额度统计(南北 交易)|港股通额度统计(南北交易)|ZZHSAmountAllReq||
|可转债静态信息接口|根据可转债代码查询可转债静态信 息接口|ZZKZZInfoReq||
|市场总览接口|市场总览接口|ZZMarketOverviewReq||

##### **Level-2接口** 

|**行情接口分类**|**接口名称**|**请求列表**|**备注**|
|---|---|---|---|
|分笔逐笔|分笔明细(L1分笔,L2逐笔)|ZZTickReq||
||L2分笔明细|ZZL2TickReq||
||L2逐笔明细|ZZL2TickDetailReq||
|分量|分量表|ZZVolumeReq|沪深|
|分价|分价量表|ZZPriceVolumeReq|沪深港(不包含指数)、期货|

##### **Level-2Plus接口** 

|**行情接口分类**|**接口名称**|**请求列表**|**备注**|
|---|---|---|---|
|逐笔委托|逐笔委托|ZZL2TickEntrustReq||
|逐笔还原|逐笔还原|ZZL2TickRestoreReq||

##### **F10接口** 

### **TCP订阅推送(MQTTManager)** 

###### 快照推送仅支持沪深港京市场 

|**说明**|**方法**|**备注**|
|---|---|---|
|订阅|subscribe(codes: string, type: SubscribeType)|多只股票逗号分割|
|解除订阅|unSubscribe(codes: string, type: SubscribeType)|多只股票逗号分割|
||unSubscribeAll(type: SubscribeType)|解除所有股票的某一类型的订阅|

##### **订阅类型枚举(SubscribeType)** 

|**枚举类型**|**备注**|
|---|---|
|SubscribeType.None|无|
|SubscribeType.Snap|快照(增值数据部分不支持推送)|
|SubscribeType.Line|分时走势|
|SubscribeType.Line5|五日分时走势|
|SubscribeType.Tick|分时明细|
|SubscribeType.TickDetail|逐笔明细|
|SubscribeType.Thousands|千档|
|SubscribeType.QX|全息队列:参数code需带价格,价格为千档 ZZThousandsItem里的原始价格。 如code$orginPrice1$orginPrice2,用$分割,最多两个价格|
|SubscribeType.TickEntrust|逐笔委托|
|SubscribeType.TickRestore|逐笔还原|
|SubscribeType.All|所有类型(此类型只适用于取消)|

##### **TCP推送数据监听接口列表(IPush)** 

|**说明**|**方法**|**参数**|
|---|---|---|
|接收数据接口|SseSDK.setIPush(new ZZIPush())|参考 ZZIPush|

##### **IPush:推送数据的类** 

|**属性名**|**形态**|**备注**|
|---|---|---|
|quotePush|push: (item: ZZQuoteItem) => void;|快照推送回调|
|chartPush|push: (code:string, resp: ZZChartResp) => void;|分时走势推送回调|
|chart5Push|push: (code:string, resp: ZZChartResp) => void;|五日走势推送回调|
|tickPush|push: (code:string, resp: ZZTickResp) => void;|分时明细推送回调|
|tickDetailPush|push: (code:string, resp: ZZL2TickDetailResp) => void;|逐笔明细推送回调|
|tickEntrustPush|push: (code:string, resp: ZZL2TickEntrustResp) => void;|逐笔委托推送回调|
|tickRestorePush|push: (code:string, resp: ZZL2TickRestoreResp) => void;|逐笔还原推送回调|
|thousandsPush|push: (code:string, data: ZZThousandsData)=> void;|千档推送回调|
|qxPush|push: (code:string, data: ZZQXData) => void;|全息推送回调|

##### **订阅推送示例** 

```arkts
let iPush: IPush = new IPush(); iPush.quotePush = {push:(item) => { this.message = this.getMsg(item, new ZZAddValueModel(\)); }}; iPush.chartPush = {push:(code,resp) => { this.message = resp.toString(); }}; iPush.tickPush = {push:(code,resp) => { this.message = resp.toString(); }}; iPush.tickDetailPush = {push:(code,resp) => { this.message = resp.toString(); }}; iPush.tickEntrustPush = {push:(code,resp) => { this.message = resp.toString(); }}; iPush.tickRestorePush = {push:(code,resp) => { this.message = resp.toString(); }}; iPush.thousandsPush = {push:(code,data) => { this.message = JSON.stringify(data); }}; iPush.qxPush = {push:(code,data) => { this.message = JSON.stringify(data); 
```

}}; SseSDK.setIPush(iPush); //订阅 MQTTManager.getInstance().subscribe("600000.sh",SubscribeType.Line); //解订阅 MQTTManager.getInstance().unSubscribe("600000.sh",SubscribeType.Line); //全息支持传两个价格,如下 MQTTManager.getInstance().subscribe("600000.sh$9310$9320",SubscribeType.QX); 

##### **APP进入后台取消推送问题** 

|**方法**|**说明**||
|---|---|---|
|SseSDK.onForeground()|当APP进入前台时,|调用此方法,SDK会自动恢复订阅|
|SseSDK.onBackground();|当APP进入后台时,|调用此方法,SDK会自动断线解除订阅推送|

##### **数据类型汇总** 

##### **行情数据模型列表** 

|**说明**|**类名**|**备注**|
|---|---|---|
|市场资讯模型|ZZMarketInfoItem||
|股票模型|ZZQuoteItem||
|买卖队列模型|ZZOrderQuantityItem||
|经济席位模型|ZZBrokerInfoItem||
|K线数据模型|ZZOHLCItem||
|港股其他模型|ZZHKStockInfoItem||
|可转债静态信息|ZZKZZInfoItem||
|板块排序模型|ZZSectionSortingItem||
|板块类别个股列表模型|ZZCategoryListItem||
|股票查询模型|ZZSearchItem||
|新股日历模型|ZZNewShareDates||
|新股列表模型|ZZNewShareList||
|新股详情模型|ZZNewShareDetail||
|板块类别个股模型|ZZCategoryItem||
|市场当年交易日模型|ZZTradeDateItem||

|uk市场快照|ZZUKItem|
|---|---|
|K沪深当日涨跌统计数模型|ZZMarketUpDownItem|
|集合竞价走势模型|ZZBidItem|
|CDR,GDR联动|ZZDRLinkItem|
|AH联动|ZZAHLinkItem|
|AB联动|ZZABLinkItem|
|可转债联动|ZZKZZLinkItem|
|CDR,GDR联动列表数据|ZZDRListItem|
|AH联动列表数据|ZZAHListItem|
|AB联动列表数据|ZZABListItem|
|可转债联动列表数据|ZZKZZListItem|
|次新股列表数据模型|ZZSubnewStockItem|
|次新债列表数据模型|ZZSubnewBondItem|
|市场总览数据模型|ZZMarketOverviewItem|

##### **行情应答数据列表** 

|**说明**|**类名**|**备注**|
|---|---|---|
|行情快照|ZZQuoteResp||
|走势数据|ZZChartResp||
|K线数据|ZZOHLCResp||
|分价|ZZPriceVolumeResp||
|证券行情列表|ZZQuoteResp||
|排行|ZZCatesortingResp||
|板块排行|ZZSectionSortingResp||
|个股所属板块行情|ZZSectionQuoteResp||
|个股所属板块列表|ZZSectionStockResp||
|股票查询|ZZSearchResp||
|期权标的证券|ZZUnderlyingStockResp||
|期权-交割月|ZZExpireMonthResp||
|期权-T型报价|ZZOptionResp||
|期权-商品行情|ZZOptionResp||
|L2单独分笔|ZZL2TickResp||
|L2单独逐笔|ZZL2TickDetailResp||
|走势副图增值指标|ZZChartIndexResp||
|历史K线增值数据|ZZOHLCIndexResp||
|历史分时|ZZHistoryZZChartResp||
|沪深当日涨跌统计数据|ZZMarketUpdownsResp||
|沪股通和深股通额度|ZZHSAmountAllResp||
|集合竞价走势接口|ZZBidZZChartResp||
|涨跌分布统计请求|ZZCompoundUpdownsResp||

**LevelAndIpChangedListener(行情切换监听)** 

**SseSDK(监听个市场行情站点变化)** 

**行情level切换回调说明** 

**走势型态(ZZChartType)** 

|**名称**|**说明**|**备注**|
|---|---|---|
|ChartTypeOneDay|当日走势||
|ChartTypeFiveDays|五日走势||

##### **走势指标副图数据类别(ZZChartIndexType)** 

|**名称**|**说明**|**备注**|||
|---|---|---|---|---|
|ChartIndexTypeDDX|大单净差|(支持:|走势,|个股K线)|
|ChartIndexTypeDDY|主力动向|(支持:|走势,|个股K线)|
|ChartIndexTypeDDZ|涨跌动因|(支持:|走势,|个股K线)|
|ChartIndexTypeBBD|大单差分|(支持:|走势,|个股K线)|
|ChartIndexTypeRatioBS|单数比|(支持:|走势,|个股K线)|
|ChartIndexTypeLargeMoneyInflow|超大单净流入|(支持:|走势,|个股K线,板块K线)|
|ChartIndexTypeBigMoneyInflow|大单净流入|(支持:|走势,|个股K线,板块K线)|
|ChartIndexTypeMidMoneyInflow|中单净流入|(支持:|走势,|个股K线,板块K线)|
|ChartIndexTypeSmallMoneyInflow|小单净流入|(支持:|走势,|个股K线,板块K线)|
|ChartIndexTypeLargeTradeNum|超大单成交单数|(支持:|走势,|个股K线)|
|ChartIndexTypeBigTradeNum|大单成交单数|(支持:|走势,|个股K线)|
|ChartIndexTypeMidTradeNum|中单成交单数|(支持:|走势,|个股K线)|
|ChartIndexTypeSmallTradeNum|小单成交单数|(支持:|走势,|个股K线)|
|ChartIndexTypeBigNetVolume|大单净量|(支持:|走势)||
|ChartIndexTypeMainforceMoneyInflow|主力资金流入|(支持:|板块K|线)|
|ChartIndexTypeMainforceMoneyOutflow|主力资金流出|(支持:|板块K|线)|

##### **K线周期(ZZOHLCPeriod)** 

|**名称**|**说明**|**备注**|
|---|---|---|
|OHLCPeriodDay|日K||
|OHLCPeriodWeek|周K||
|OHLCPeriodMonth|月K||
|OHLCPeriodQuarter|季K|沪深京、新三板|
|OHLCPeriodYear|年K||
|OHLCPeriodMin1|1分钟K||
|OHLCPeriodMin5|5分钟K||
|OHLCPeriodMin15|15分钟K||
|OHLCPeriodMin30|30分钟K||
|OHLCPeriodMin60|60分钟K||
|OHLCPeriodMin120|120分钟K||

##### **板块类别个股型态(ZZCateType)** 

|**名称**|**说明**|**备注**|
|---|---|---|
|指数代码(如 000001.sh)|指数成分股||
|上海市场|||
|SH1001|上证A股||
|SH1002|上证B股||
|SH1005|上证主板A股||
|SH1006|科创板||
|SH1100|上证基金||
|SH1110|上证LOF||
|SH1120|上证ETF||
|SH1140|上海封闭式基金||
|SH1150|上海REITs||
|SH1300|上证债券||
|SH1311|国债逆回购(沪)||
|SH1312|上海可转债||
|SH1321|债券合格投资者||

|SH1322|债券合格机构投资者|
|---|---|
|SH1400|上海指数|
|SH3002|上证证期权|
|SHS|上证风险警示(包括退市 整理)|
|SHP|上证退市整理|
|SH1011|上海未上市中一些无法识 别类型的标的|
|SH1012|上证配股|
|SH9001|上证非交易|
|SH1000|上证优先股|
|SH9900|最近一次变更前股名|
|SH9800|退市的股票|
|SH1500|创新企业股票&存托凭证|
|SH1510|创新企业股票|
|SH1520|(CDR)存托凭证|
|SH1521|科创板CDR|
|SH1313|上证国债|
|SH1314|上证企业债|
|SHCXG|上证次新股(6个月)|
|SH8100|上海b转h|
|SH10013|注册制--上证A股注册制|
|SH10014|审核制--上证A股核准制|
|SH10053|注册制--上证主板注册制|
|SH10054|审核制--上证主板核准制|
|中证指数||
|CSI1400|中证指数|
|深证市场||
|SZ1001|深证A股|
|SZ1002|深证B股|
|SZ1004|创业板|
|SZ10041|注册制创业板|

|SZ10042|审核制创业板||
|---|---|---|
|SZ1005|主板||
|SZ1100|深证基金||
|SZ1110|深证LOF||
|SZ1120|深证ETF||
|SZ1140|深证封闭式基金||
|SZ1150|深圳REITs||
|SZ1300|深证债券||
|SZ1311|国债逆回购(深)||
|SZ1312|深证可转债||
|SZ1321|债券合格投资者|深证市场|
|SZ1322|债券合格机构投资者|深证市场|
|SZ1400|深证指数||
|SZS|深证风险警示(包括退市 整理)||
|SZZ|深证退市整理||
|SZ1011|深证未上市中一些无法识 别类型的标的||
|SZ1012|深证配股||
|SZ9001|深证非交易||
|SZ1000|深证优先股||
|SZ9900|最近一次变更前股名||
|SZ9800|退市的股票||
|SZ1500|创新企业股票&存托凭证||
|SZ1510|创新企业股票||
|SZ1520|存托凭证||
|SZ1522|CDR(创业板)||
|SZ1523|CDR(主板、中小板)||
|SZ1313|深证国债||
|SZ1314|深证企业债||
|SZCXG|深证次新股(6个月)||
|SZ8100|深圳b转h||

|SZ10013|注册制--深证A股注册制||
|---|---|---|
|SZ10014|审核制--深证A股核准制||
|SZ10053|注册制--深证主板注册制||
|SZ10054|审核制--深证主板核准制||
|沪深市场|||
|SHSZ1001|沪深A股||
|SHSZ1100|沪深基金||
|SHSZ1110|LOF基金||
|SHSZ1120|ETF基金||
|SHSZ1150|沪深REITs||
|SHSZ1300|沪深债劵||
|SHSZ1400|沪深指数||
|SHSZS|沪深风险警示(包括退市 整理)||
|SHSZP|沪深退市整理||
|SHSZ1500|创新企业股票&存托凭证||
|SHSZ1510|创新企业股票||
|SHSZ1520|存托凭证||
|SHSZ1311|沪深国债逆回购||
|SHSZ1312|沪深可转债||
|SHSZ1313|沪深国债||
|SHSZ1314|沪深企业债||
|SHSZCXG|沪深次新股(6个月)||
|SHSZ1005|沪深主板A股||
|SHSZ1002|沪深B股||
|SHSZ10013|注册制--沪深A股注册制|SH10013|SZ10013合集|
|SHSZ10014|审核制-沪深A股核准制|SH10014|SZ10014合集|
|SHSZ10053|注册制--沪深主板注册制|SH10053|SZ10053合集|
|SHSZ10054|审核制-沪深主板核准制|SH10054|SZ10054合集|
|沪深京市场|||
|SHSZBZ1001|沪深京A股||
|SHSZBZ1300|沪深京债券||

|SHSZBZ1312|沪深京可转债|
|---|---|
|北交所市场||
|BZ1001|北交所A股|
|BZ10011|北交所首日挂牌|
|BZ10012|北交所增发挂牌|
|BZ1011|北交所发行信息|
|BZ10111|北交所申购发行信息|
|BZ10112|北交所询价发行信息|
|BZ1300|北交所债券|
|BZ1312|北交所可转债|
|股转系统(新三板)||
|BJ1000|新三板|
|BJ1001|两网及退市|
|BJ100101|两网及退市A股|
|BJ100102|两网及退市B股|
|BJ1002|优先股|
|BJ1003|首日挂牌|
|BJ1004|增发挂牌|
|BJ1005|创新层|
|BJ100501|创新层集合竞价转让|
|BJ100502|创新层做市转让|
|BJ1006|基础层|
|BJ100601|基础层集合竞价转让|
|BJ100602|基础层做市转让|
|BJ1007|集合竞价转让|
|BJ100701|集合竞价转让基础层|
|BJ100702|集合竞价转让创新层|
|BJ1008|做市转让|
|BJ100801|做市转让基础层|
|BJ100802|做市转让创新层|
|BJ1009|协议转让|

|BJ1010|连续竞价转让||
|---|---|---|
|BJ1011|股权激励期权||
|BJ1012|挂牌公司||
|BJ1400|三板指数||
|BJ1013|要约回收购||
|BJ101301|要约收购||
|BJ101302|要约回购||
|BJ1300|债券||
|BJ1312|可转债||
|BJ131201|基础层||
|BJ131202|创新层||
|沪深港股通|||
|HKUA2301|港股通(沪)|沪港通|
|SZHK|港股通(深)|深港通|
|HKTong|港股通||
|HKHGT|沪股通|沪港通|
|HKSGT|深股通|深港通|
|SHHGT|港股通沪(纯标的)||
|SZSGT|港股通深(纯标的)||
|HKGGT|港股通(沪深纯标的)||
|HKGGTEQTY|沪深港股通股票||
|HKGGTTRST|沪深港股通基金||
|SZSGTEQTY|深港通股票||
|SZSGTTRST|深港通基金||
|SHHGTEQTY|沪港通股票||
|SHHGTTRST|沪港通基金||
|港股市场|||
|HK1010|港股||
|HK1000|主板(港股)||
|HK1004|创业板(港股)||
|HK1100|基金(港股)||

|HK1300|债券(港股)||
|---|---|---|
|HK1400|香港指数||
|HK1500|牛熊证||
|HK1600|涡轮||
|HK1610|界内证||
|HK1620|认沽认购||
|HKAHG|AH股||
|HKGQ|国企股||
|HKLC|蓝筹股||
|HKHC|红筹股||
|HSI|恒指成分股||
|海外市场|||
|GB1400|全球指数|收盘行情|
|GB1001|外汇|收盘行情|
|中金所|||
|CFF_ALL|所有证券|中金所|
|CFF_FUTURE|所有中金所期货合约|中金所|
|CFF_IC|中证|中金所|
|CFF_IF|沪深|中金所|
|CFF_IH|上证|中金所|
|CFF_T|10年国债|中金所|
|CFF_TF|5年国债|中金所|
|CFF_TS|2年国债|中金所|
|CFF_INDEX_FUTURE|中证沪深上证的合约(股指 期货)|中金所|
|CFF_TREASURY_FUTURE|2年5年10年国债的合约 (国债期货)|中金所|
|CFF_IF_MONTH|中证沪深上证的当月及下 月合约|中金所|
|CFF_OPTION|中金所所有期权标的|中金所|
|CFF_UNDERLYING|中金所期权(沪深300股 指期权)连续合约标的|中金所|
|CFF_EXPIREMONTH_IO|中金所期权(沪深300股|中金所|

|CFF_T_IO2205|指期权)年月板块 中金所期权(沪深300股 指期权2205)的认沽认购 合约|中金所|
|---|---|---|
|大商所|||
|DCE_ALL|所有大商所的合约|大商所|
|DCE_FUTURE|所有大商所期货合约|大商所|
|DCE_OPTION|所有大商所期权合约|大商所|
|DCE_BB|胶合板|大商所|
|DCE_A|豆一|大商所|
|DCE_B|豆二|大商所|
|DCE_CS|玉米淀粉|大商所|
|DCE_C|玉米|大商所|
|DCE_L|聚乙烯|大商所|
|DCE_M|豆粕|大商所|
|DCE_PP|聚丙烯|大商所|
|DCE_P|棕榈油|大商所|
|DCE_V|聚氯乙烯|大商所|
|DCE_Y|豆油|大商所|
|DCE_JD|鸡蛋|大商所|
|DCE_JM|焦煤|大商所|
|DCE_J|焦炭|大商所|
|DCE_I|铁矿石|大商所|
|DCE_FB|纤维板|大商所|
|DCE_EG|乙二醇|大商所|
|DCE_M1903(具体值: dce_T_m1903)|大商所期权豆粕1903的认 沽认购合约|大商所(期权接口),大商所期权豆粕1903的认沽认购合约, (其中m1903可以为DCE_EXPIREMONTH_M返回的任一 code)|
|DCE_C1905(具体值: dce_T_c1905)|大商所期权玉米1905的认 沽认购合约|大商所(期权接口),大商所期权玉米1905的认沽认购合约, (其中c1905可以为DCE_EXPIREMONTH_C返回的任一code)|
|DCE_UNDERLYING|大商所大豆标的及玉米标 的的连续合约|大商所|
|DCE_EXPIREMONTH_M|大商所豆粕期权所属期货 年月板块|大商所|

|DCE_EXPIREMONTH_C|大商所玉米期权所属期货 年月板块|大商所|
|---|---|---|
|郑商所|||
|CZCE_ALL|所有郑商所的合约|郑商所|
|CZCE_FUTURE|所有郑商所期货合约|郑商所|
|CZCE_OPTION|所有郑商所期权合约|郑商所|
|CZCE_AP|苹果|郑商所|
|CZCE_CF|郑棉|郑商所|
|CZCE_RI|早籼稻|郑商所|
|CZCE_LR|晚籼稻|郑商所|
|CZCE_JR|粳稻|郑商所|
|CZCE_OI|菜籽油|郑商所|
|CZCE_TA|PTA|郑商所|
|CZCE_PM|普麦|郑商所|
|CZCE_MA|甲醇|郑商所|
|CZCE_FG|玻璃|郑商所|
|CZCE_RS|油菜籽|郑商所|
|CZCE_RM|菜籽粕|郑商所|
|CZCE_ZC|动力煤|郑商所|
|CZCE_SF|硅铁|郑商所|
|CZCE_SM|锰硅|郑商所|
|CZCE_CY|棉纱|郑商所|
|CZCE_SR|白糖|郑商所|
|CZCE_WH|强麦|郑商所|
|CZCE_SR001(具体值: czce_T_SR001)|郑商所期权白糖001的认 沽认购合约|郑商所(期权接口),郑商所期权白糖001的认沽认购合约, (其 中SR001可以为CZCE_EXPIREMONTH_SR返回的任一code)|
|CZCE_CF905(具体值: czce_T_CF905)|郑商所期权郑棉905的认 沽认购合约|郑商所(期权接口),郑商所期权郑棉905的认沽认购合约, (其 中CF905可以为CZCE_EXPIREMONTH_CF返回的任一code)|
|CZCE_UNDERLYING|郑商所白糖标的及郑棉标 的的连续合约|郑商所|
|CZCE_EXPIREMONTH_SR|郑商所白糖期权所属期货 年月板块|郑商所|
|CZCE_EXPIREMONTH_CF|郑商所郑棉期权所属期货|郑商所|

||年月板块||
|---|---|---|
|上期所|||
|SHFE_ALL|所有上期所的合约|上期所|
|SHFE_FUTURE|所有上期所期货合约|上期所|
|SHFE_OPTION|所有上期所期权合约|上期所|
|SHFE_INDEX|所有上期所指数合约|上期所|
|SHFE_CU|沪铜|上期所|
|SHFE_AL|沪铝|上期所|
|SHFE_FU|燃料油|上期所|
|SHFE_RU|天然橡胶|上期所|
|SHFE_ZN|沪锌|上期所|
|SHFE_AU|黄金|上期所|
|SHFE_RB|螺纹钢|上期所|
|SHFE_WR|线材|上期所|
|SHFE_PB|沪铅|上期所|
|SHFE_AG|白银|上期所|
|SHFE_BU|石油沥青|上期所|
|SHFE_HC|热轧卷板|上期所|
|SHFE_NI|沪镍|上期所|
|SHFE_SN|沪锡|上期所|
|SHFE_SP|纸浆|上期所|
|SHFE_IMCI|上期有色金属指数|上期所|
|SHFE_CU1903(具体值: shfe_T_cu1903)|上期所期权沪铜1903的认 沽认购合约|上期所(期权接口),上期所期权郑棉905的认沽认购合约, (其中cu1903可以为SHFE_EXPIREMONTH_CU返回的任一 code)|
|SHFE_RU1905(具体值: shfe_T_ru1905)|上期所期权天然橡胶1905 的认沽认购合约|上期所(期权接口),上期所期权郑棉905的认沽认购合约, (其中ru1905可以为SHFE_EXPIREMONTH_RU返回的任一 code)|
|SHFE_UNDERLYING|上期所沪铜标的及天然橡 胶标的的连续合约|上期所|
|SHFE_EXPIREMONTH_CU|上期所沪铜期权所属期货 年月板块|上期所|
|SHFE_EXPIREMONTH_RU|上期所天然橡胶期权所属 期货年月板块|上期所|

|上期所原油|||
|---|---|---|
|INE_ALL|所有上期所原油市场的合 约|上期所原油|
|INE_FUTURE|所有上期所原油市场期货 合约|上期所原油|
|INE_SC|原油|上期所原油|
|沪伦通|||
|SH1530|CDR|沪伦通|
|UK1530|CDR基础证券|沪伦通|
|SH1540|GDR基础证券|沪伦通|
|UK1540|GDR|沪伦通|

##### **排序分类代码(ZZSortType)** 

|**代码**|**说明**|
|---|---|
|快照||
|quote_STATE|交易状态|
|quote_ID|代码|
|quote_NAME|名称|
|quote_LAST_PRICE|最新价|
|quote_HIGH_PRICE|最高价|
|quote_LOW_PRICE|最低价|
|quote_OPEN_PRICE|今开价|
|quote_PRE_CLOSE_PRICE|昨收价|
|quote_CHANGE_RATE|涨跌比率|
|quote_VOLUME|总手|
|quote_NOW_VOLUME|当前成交量|
|quote_TURNOVER_RATE|换手率|
|quote_LIMIT_UP|涨停价(暂不支持)|
|quote_LIMIT_DOWN|跌停价(暂不支持)|
|quote_AVERAGE_VALUE|均价(暂不支持)|
|quote_CHANGE|涨跌|

|quote_AMOUNT|成交金额|
|---|---|
|quote_VOLUME_RATIO|量比|
|quote_BUY_PRICE|买一价(暂不支持)|
|quote_SELL_PRICE|卖一价(暂不支持)|
|quote_BUY_VOLUME|外盘量|
|quote_SELL_VOLUME|内盘量|
|quote_TOTAL_VALUE|总市值|
|quote_FLOW_VALUE|流通市值|
|quote_NET_ASSET|净资产|
|quote_STOCK_INFO|pe(动态市盈率)|
|quote_PB|市净率|
|quote_CAPITALIZATION|总股本|
|quote_CIRCULATING_SHARES|流通股|
|quote_AMPLITUDE_RATE|振幅比率|
|quote_RECEIPTS|动态每股收益|
|quote_ORDER_RATIO|沪深港委比|
|quote_ETRUST_DIFF|委差|
|quote_pe2_unit|静态市盈率|
|quote_AFTER_HOURS_VOLUME|盘后成交量|
|quote_AFTER_HOURS_AMOUNT|盘后成交额|
|quote_MONTH_CHANGE_RATE|本月涨跌幅|
|quote_YEAR_CHANGE_RATE|本年涨跌幅|
|quote_RECENT_MONTH_CHANGE_RATE|近一月涨跌幅|
|quote_RECENT_YEAR_CHANGE_RATE|近一年涨跌幅|
|quote_TTM|滚动市盈率|
|quote_ROE|年化净资产收益率|
|quote_BUY_VOL1|买一量|
|quote_SELL_VOL1|卖一量|

|quote_LISTING_DATE|上市日期|
|---|---|
|quote_CHANGERATE5|前5日涨跌幅|
|quote_CHANGERATE10|前10日涨跌幅|
|quote_CHANGERATE20|前20日涨跌幅|
|quote_TURNOVER_RATE5|前5日换手率|
|quote_TURNOVER_RATE10|前10日换手率|
|quote_TURNOVER_RATE20|前20日换手率|
|quote_FIVE_MINUTES_CHANGERATE|五分钟涨速|
|quote_THREE_MINUTES_CHANGERATE|三分钟涨速|
|quote_CHANGERATE3|前3日涨跌幅|
|quote_CHANGERATE60|前60日涨跌幅|
|quote_YESTERDAY_CHANGERATE|昨日涨跌幅|
|增值指标||
|AddValue_ULTRALARGENETINFLOW|超大单净流入|
|addValue_LARGENETINFLOW|大单净流入|
|addValue_MEDIUMNETINFLOW|中单净流入|
|addValue_SMALLNETINFLOW|小单净流入|
|addValue_BBD|大单净差|
|addValue_BBD5|五日大单净差|
|addValue_BBD10|十日大单净差|
|addValue_DDX|主力动向|
|addValue_DDX5|五日主力动向|
|addValue_DDX10|十日主力动向|
|addValue_DDY|涨跌动因|
|addValue_DDY5|五日涨跌动因|
|addValue_DDY10|十日涨跌动因|
|addValue_NET_CAPITAL_INFLOW|主力净流入|
|addValue_CHG5MINUTES|五分钟涨跌幅|
|addValue_MAINFORCEMONEYNETINFLOW5|5日主力资金净流入|

|addValue_MAINFORCEMONEYNETINFLOW10|10日主力资金净流入|
|---|---|
|addValue_MAINFORCEMONEYNETINFLOW20|20日主力资金净流入|
|addValue_RATIOMAINFORCEMONEYNETINFLOW5|5日主力资金净流入占比|
|addValue_RATIOMAINFORCEMONEYNETINFLOW10|10日主力资金净流入占比|
|addValue_RATIOMAINFORCEMONEYNETINFLOW20|20日主力资金净流入占比|
|大商,郑商,全球指数,外汇||
|SSE_LastPrice|最新价(大商,郑商,全球指数,外汇)|
|SSE_LowPrice|最低价(大商,郑商,全球指数,外汇)|
|SSE_Change|涨跌额(全球指数,外汇)|
|SSE_ChangeRate|涨跌幅(大商,郑商,全球指数,外汇)|
|SSE_Amount|成交额(大商,郑商,全球指数,外汇)|
|SSE_Name|名称(大商,郑商,全球指数,外汇)|
|SSE_Volume|成交量(暂不支持)|
|SSE_PreClosePrice|昨收价(大商,郑商,全球指数,外汇)|
|SSE_HighPrice|最高价(大商,郑商,全球指数,外汇)|
|沪伦通||
|quote_DR_CURRENT_SHARE|当前份额|
|quote_DR_PREVIOUS_CLOSING_SHARE|前收盘份额(上一交易日)|
|科创板/深交所创业板||
|quote_AFTER_HOURS_VOLUME|盘后成交量|
|quote_AFTER_HOURS_AMOUNT|盘后成交额|

##### **沪伦通列表排序(ZZDRSortType)** 

|**名称**|**说明**|
|---|---|
|CODE|证券代码|
|NAME|证券名称|
|LASTPRICE|最新价|
|PRE_CLOSE_PRICE|前收盘价|
|CHANGE_RATE|涨幅|
|DATETIME|行情时间|
|BASECODE|基础证券代码|
|BASENAME|基础证券名称|
|BASE_LASTPRICE|基础证券最新价|
|BASE_PRE_CLOSE_PRICE|基础证券前收盘价|
|BASE_CHANGERATE|基础证券涨幅|
|BASE_DATETIME|基础证券行情时间|
|PREMIUM|溢价|

##### **搜索子分类代码(ZZSubType)** 

只有主类别支持在线搜索 

|**代码**|**名称**|**备注**|
|---|---|---|
|sh|上海|市场|
|sz|深圳|市场|
|bj|股转|市场|
|sh|上海|市场|
|sz|深圳|市场|
|bj|股转|市场|
|hk|港股|市场|
|hh|港股通(沪)|市场|
|hz|港股通(深)|市场|
|gb|全球指数(收盘)&外汇(收盘)|市场|
|cff|中金所|市场|
|dce|大商所|市场|
|czce|郑商所|市场|
|shfe|上期所|市场|
|ine|上期所原油|市场|
|dce|大商所|市场|
|bk|板块|市场|
|bz|北证|市场|
|shbh|上海b转h|市场|
|szbh|深圳b转h|市场|

以下代码由市场与subtype组合:SH1001(send方法)或者SH_1001(sendV2方法) 

|**subtype**|**说明**|**可用市场别**|**备注**|
|---|---|---|---|
|1000|新三板|BJ|主类别|
|1000|主板|HK|主类别|
|1000|优先股|SH,SZ|主类别|
|1001|A股|SH,SZ,HK,BZ|主类别|
|1002|B股|SH, SZ|主类别|

|1004|创业版|SZ, HK|主类别|
|---|---|---|---|
|1400|大盘指数|SH,SZ,GB,HK|主类别|
|1100|基金|SH,SZ,HK|主类别|
|1110|上市型开放式基金(LOF)|SH, SZ||
|1120|交易型开放式指数基金(ETF)|SH, SZ||
|1140|封闭式基金(CEF)|SH, SZ||
|1300|债券|SH,SZ,HK|主类别|
|1311|国债逆回购|SH,SZ||
|3002|上证期权|SH|主类别|
|1500|牛熊证|HK|主类别|
|1600|涡轮|HK|主类别|
|1010|港股|HK|主类别|
|1012|配股(沪/深)|SH,SZ||
|1011|沪深未上市中无法识别类型的标的|SH,SZ||
|1006|科创板|SH||
|9001|非交易|SH,SZ|主类别|
|9002|非交易|SH,SZ|主类别|
|9003|非交易产品细分品种未具体定义|SH,SZ|主类别|
|9004|非交易产品细分品种未具体定义|SH,SZ|主类别|
|9800|退市股票类型|SH,SZ|主类别|
|9900|更名股票类型|SH,SZ|主类别|
|futureIC|中证|CFF|主类别|
|futureIF|沪深|CFF|主类别|
|futureIH|上证|CFF|主类别|
|futureT|10年国债|CFF|主类别|
|futureTF|5年国债|CFF|主类别|
|futureTS|2年国债|CFF|主类别|
|futurea|豆一|DCE|主类别|

|futureb|豆二|DCE|主类别|
|---|---|---|---|
|futurebb|胶合板|DCE|主类别|
|futurec|玉米|DCE|主类别|
|futurecs|玉米淀粉|DCE|主类别|
|futureeg|乙二醇|DCE|主类别|
|futurefb|纤维板|DCE|主类别|
|futurei|铁矿石|DCE|主类别|
|futurej|焦炭|DCE|主类别|
|futurejd|鸡蛋|DCE|主类别|
|futurejm|焦煤|DCE|主类别|
|futurel|聚乙烯|DCE|主类别|
|futurem|豆粕|DCE|主类别|
|futurep|棕榈油|DCE|主类别|
|futurepp|聚丙烯|DCE|主类别|
|futurev|聚氯乙烯|DCE|主类别|
|futurey|豆油|DCE|主类别|
|optionc|玉米期权|DCE|主类别|
|optionm|豆粕期权|DCE|主类别|
|futureAP|苹果|CZCE|主类别|
|futureCF|郑棉|CZCE|主类别|
|futureCY|棉纱|CZCE|主类别|
|futureFG|玻璃|CZCE|主类别|
|futureJR|粳稻|CZCE|主类别|
|futureLR|晚籼稻|CZCE|主类别|
|futureMA|甲醇|CZCE|主类别|
|futureOI|菜籽油|CZCE|主类别|
|futurePM|普麦|CZCE|主类别|
|futureRI|早籼稻|CZCE|主类别|
|futureRM|菜籽粕|CZCE|主类别|

|futureRS|油菜籽|CZCE|主类别|
|---|---|---|---|
|futureSF|硅铁|CZCE|主类别|
|futureSM|锰硅|CZCE|主类别|
|futureSR|白糖|CZCE|主类别|
|futureTA|PTA|CZCE|主类别|
|futureWH|强麦|CZCE|主类别|
|futureZC|动力煤|CZCE|主类别|
|optionCF|郑棉期权|CZCE|主类别|
|optionSR|白糖期权|CZCE|主类别|
|futureag|白银|SHFE|主类别|
|futureal|沪铝|SHFE|主类别|
|futureau|黄金|SHFE|主类别|
|futurebu|石油沥青|SHFE|主类别|
|futurecu|沪铜|SHFE|主类别|
|futurefu|燃料油|SHFE|主类别|
|futurehc|热轧卷板|SHFE|主类别|
|futureni|沪镍|SHFE|主类别|
|futurepb|沪铅|SHFE|主类别|
|futurerb|螺纹钢|SHFE|主类别|
|futureru|天然橡胶|SHFE|主类别|
|futuresn|沪锡|SHFE|主类别|
|futuresp|纸浆|SHFE|主类别|
|futurewr|线材|SHFE|主类别|
|futurezn|沪锌|SHFE|主类别|
|indexIMCI|上期有色金属指数|SHFE|主类别|
|optioncu|沪铜期权|SHFE|主类别|
|optionru|天然橡胶期权|SHFE|主类别|
|futuresc|原油|INE|主类别|

##### **板块排序种类(ZZSectionSortingField)** 

|**名称**|**说明**|**备注**|
|---|---|---|
|SectionSortingFieldCode|板块代码||
|SectionSortingFieldLastPrice|最新价||
|SectionSortingFieldOpenPrice|开盘价||
|SectionSortingFieldHighPrice|最高价||
|SectionSortingFieldLowPrice|最低价||
|SectionSortingFieldPreClosePrice|昨收价||
|SectionSortingFieldChange|涨跌额||
|SectionSortingFieldChangeRate|涨跌幅||
|SectionSortingFieldChangeRate5|5日涨跌幅||
|SectionSortingFieldChangeRate10|10日涨跌幅||
|SectionSortingFieldAmount|总成交额||
|SectionSortingFieldHot|优品热度值|只有优品板块有值|
|SectionSortingFieldNowVolume|现成交量|单位(手)|
|SectionSortingFieldVolume|总成交量|单位(手)|
|SectionSortingFieldWeightedChange|权涨幅||
|SectionSortingFieldAverageChange|均涨幅||
|SectionSortingFieldFlowValue|流通市值||
|SectionSortingFieldTotalValue|总市值||
|SectionSortingFieldOrderRatio|委比||
|SectionSortingFieldEntrustDiff|委差||
|SectionSortingFieldTurnoverRate|换手率||
|SectionSortingFieldAmplitudeRate|振幅||
|SectionSortingFieldRiseRate|涨股比||
|SectionSortingFieldAdvanceAndDeclineCount|涨跌家数||
|SectionSortingFieldLimitUpCount|涨停家数||
|SectionSortingFieldLimitDownCount|跌停家数||

|SectionSortingFieldCapitalInflow|主力资金流入|
|---|---|
|SectionSortingFieldCapitalOutflow|主力资金流出|
|SectionSortingFieldNetCapitalInflow|主力资金净流入|
|SectionSortingFieldNetCapitalInflow5|五日主力资金净流入|
|SectionSortingFieldNetCapitalInflow10|10日主力资金净流入|
|SectionSortingFieldStockCode|领涨股|
|SectionSortingFieldStockChange|个股涨幅|
|SectionSortingFieldStockChangeRate|个股涨幅比|
|SectionSortingFieldEntrustBuyVolume|委买|
|SectionSortingFieldEntrustSellVolume|委卖|

##### **板块型态(ZZCategoryType)** 

|**名称**|**说明**|**备注**|
|---|---|---|
|CATE_NOTION|概念板块||
|CATE_AREA|地区板块||
|CATE_TRADE|行业板块||
|TRADE_SW|申万二级行业板块||
|TRADE_SW1|申万一级行业板块||
|TRADE_FZ|小方行业板块||
|TRADE_SZYP|优品行业板块|如需使用,需要与信息公司提出申请|
|AREA_SZYP|优品地区板块|如需使用,需要与信息公司提出申请|
|NOTION_SZYP|优品概念板块|如需使用,需要与信息公司提出申请|

##### **市场权限(ZZPermission)** 

|**名称**|**说明**|**备注**|
|---|---|---|
|HK10|港股十档||
|HKA1|港股实时一档||
|HKD1|港股延时一档||
|SHHK1|沪港通一档||
|SHHK5|沪港通五档||
|SZHK1|深港通一档||
|SZHK5|深港通五档||
|HKAZ|港股指数实时||
|HKDZ|港股指数延时||
|LEVEL_1|沪深LEVEL1|沪深LEVEL1注册可传该值|
|LEVEL_2|沪深LEVEL2|沪深LEVEL2注册可传该值|
|OL_LEVEL_1|境外沪深LEVEL1||
|OL_SH_LEVEL_2|境外沪LEVEL2||
|OL_SZ_LEVEL_2|境外深LEVEL2||
|CFF_LEVEL_2|中金所L2权限||
|CFF_LEVEL_1|中金所L1权限||
|OL_HK10|港股境外10档权限||
|OL_HKA1|港股境外实时一档权限||

##### **板块自定义栏位(ZZPlateIndexCustomField)** 

|**名称**|**说明**|**备注**|
|---|---|---|
|datetime|当前快照日期||
|blockIndex|板块指数||
|blockChg|板块权涨幅||
|turnoverRate|换手率||
|ratioUpDown|0:涨1:跌2:平家数||
|indexChg|指数涨跌幅||
|indexChg5|5日指数涨跌幅||

|indexChg10|10日指数涨跌幅|
|---|---|
|largeMoneyNetInflow|超大单净流入|
|bigMoneyNetInflow|大单净流入|
|midMoneyNetInflow|中单净流入|
|smallMoneyNetInflow|小单净流入|
|mainforceMoneyInflow|主力资金流入|
|mainforceMoneyOutflow|主力资金流出|
|mainforceMoneyNetInflow|主力资金净流入|
|mainforceMoneyNetInflow5|5日主力资金净流入|
|mainforceMoneyNetInflow10|10日主力资金净流入|
|largeVolumeB|超大单买入成交量|
|largeVolumeS|超大单卖出成交量|
|largeMoneyB|超大单买入成交额|
|largeMoneyS|超大单卖出成交额|
|bigVolumeB|大单买入成交量|
|bigVolumeS|大单卖出成交量|
|bigMoneyB|大单买入成交额|
|bigMoneyS|大单卖出成交额|
|midVolumeB|中单买入成交量|
|midVolumeS|中单卖出成交量|
|midMoneyB|中单买入成交额|
|midMoneyS|中单卖出成交额|
|smallVolumeB|小单买入成交量|
|smallVolumeS|小单卖出成交量|
|smallMoneyB|小单买入成交额|
|smallMoneyS|小单卖出成交额|
|totalTrdMoney|总成交额|
|blockFAMC|板块流通市值|

|totalMarketValue|板块总市值|
|---|---|
|mainforceMoneyNetInflow20|20日主力资金净流入|
|ratioMainforceMoneyNetInflow5|5日主力资金净流入占比|
|ratioMainforceMoneyNetInflow10|10日主力资金净流入占比|
|ratioMainforceMoneyNetInflow20|20日主力资金净流入占比|
|totalTrdVolume|总成交量|
|openBlockIndex|开盘板块指数|
|highBlockIndex|最高板块指数|
|lowBlockIndex|最低板块指数|
|closeBlockIndex|收盘板块指数|
|committee|委比|
|deviation|委差|
|buyNum|委买|
|sellNum|委卖|
|ttm|动态市盈率|
|lyr|静态市盈率|
|marketRate|市净率|
|blockName|板块名称|
|blockID|板块代码|
|preCloseBlockIndex|前收盘指数|
|upsDowns|涨跌额|
|amplitude|振幅|

##### **市场类别(ZZMarketType)** 

|**后缀**|**市场**|
|---|---|
|SH|上海|
|SZ|深圳|
|HK|港股|
|BJ|新三板|
|GB|全球指数/外汇|
|DCE|大商所|
|CZCE|郑商所|
|UK|沪伦通市场|
|SHFE|上海期货市场代码为|
|INE|上海期货原油市场代码为|
|BK|板块市场|
|BZ|北交所|

##### **快照V3自定义类别(ZZQuoteCustomField)** 

###### 快照部分 

|**名称**|**说明**|**备注**|
|---|---|---|
|quote_STATUS|股票状态||
|quote_ID|代码||
|quote_NAME|名称||
|quote_DATETIME|交易时间||
|quote_LAST_PRICE|最新价||
|quote_HIGH_PRICE|最高价||
|quote_LOW_PRICE|最低价||
|quote_OPEN_PRICE|今开价||
|quote_PRE_CLOSE_PRICE|昨收价||
|quote_HK_PARAM_STATUS|港股外部参数状态揭示||
|quote_VOLUME|总量||
|quote_NOW_VOLUME|当前成交量||
|quote_LIMIT_UP|涨停价||
|quote_LIMIT_DOWN|跌停价||
|quote_AVERAGE_VALUE|均价||
|quote_AMOUNT|成交金额||
|quote_VOLUME_RATIO|量比||

|quote_BUY_PRICE|买一价|
|---|---|
|quote_SELL_PRICE|卖一价|
|quote_BUY_VOLUME|外盘量|
|quote_SELL_VOLUME|内盘量|
|quote_NET_ASSET|净资产|
|quote_STOCK_INFO|个股静态信息|
|quote_CAPITALIZATION|总股本|
|quote_CIRCULATING_SHARES|流通股|
|quote_BUY_PRICES|五档买价|
|quote_BUY_VOLUMES|五档买量|
|quote_SELL_PRICES|五档卖价|
|quote_SELL_VOLUMES|五档卖量|
|quote_RECEIPTS|收益|
|quote_JIA_QUAN_PING_JUN_JIA|加权平均价|
|quote_JIA_QUAN_PING_JUN_ZHANG_DIE_BP|加权平均涨跌BP|
|quote_ZUO_SHOU_PAN_JIA_QUAN_PING_JUN_JIA|昨收盘加权平均价|
|quote_pe2_unit|放静态市盈率的计算因子|
|quote_GANG_GU_ZUI_XIAO_JIAO_YI_DAN_WEI|港股最小交易单位|
|quote_UP_DOWN_FLAG|涨跌标识|
|quote_CHANGE|涨跌|
|quote_CHANGE_RATE|涨跌幅|
|quote_TURNOVER_RATE|换手率|
|quote_PE|市盈|
|quote_PB|市净率|
|quote_TOTAL_VALUE|总市值|
|quote_FLOW_VALUE|流值|
|quote_AMPLITUDE_RATE|振幅比率|
|quote_ORDER_RATIO|委比|
|quote_IOPV|基金净值|
|quote_PreIOPV|基金净值参考价|
|quote_ZH|深港通|
|quote_HH|沪港通|
|quote_ST|次类别|
|quote_BU|融资|
|quote_SU|融券|
|quote_TBU|当日可融资|
|quote_TSU|当日可融券|
|quote_RP|回购期限|
|quote_CD|实际占款天数|
|quote_HG|沪股通标识|

|quote_SG|深股通标识||
|---|---|---|
|quote_FX|风险警示标识||
|quote_TS|退市整理标识||
|quote_VCMFlag|港股vcm标识||
|quote_CASFlag|港股cas标识||
|quote_CQCX|除权除息标识||
|quote_ZRLX|转让类型||
|quote_ZRZT|转让状态||
|quote_ZQJB|证券级别||
|quote_CRP|资金可用日期||
|quote_CDD|资金可取日期||
|quote_ETRUST_DIFF|委差||
|quote_EARN_PER_SHARE|每股收益||
|quote_EARN_PER_SHARE_REPORT_PERIOD|每股收益所属报告期|格式: YYYYQ表示YYYY年 第Q季度|
|quote_JSFZD|较上一副涨跌||
|quote_AH|ah股标识||
|quote_AB|ab股标识||
|quote_VOTE|表决权标识||
|quote_UPF|盈利标识||
|quote_DR_CURRENT_SHARE|当前份额|沪伦通|
|quote_DR_PREVIOUS_CLOSING_SHARE|前收盘份额(上一交易日)|沪伦通|
|quote_DR_CONVERSION_BASE|转换基数(用于计算溢价)|沪伦通|
|quote_DR_DEPOSITORY_INSTITUTION_CODE|存托机构代码|沪伦通|
|quote_DR_DEPOSITORY_INSTITUTION_NAME|存托机构名称|沪伦通|
|quote_DR_SUBJECT_CLOSING_REFERENCE_PRICE|标的收盘参考价|沪伦通|
|quote_DR|沪伦通标识|沪伦通|
|quote_DR_STOCKCODE|基础证券代码|沪伦通|
|quote_DR_FLOW_START_DATE|cdr初始流动性生成起始日|沪伦通|
|quote_DR_FLOW_END_DATE|cdr初始流动性生成终止日|沪伦通|
|quote_DR_LISTING_DATE|上市日期(CDR或GDR)|沪伦通|
|quote_DR_STOCK_NAME|基础证券名称|沪伦通|
|quote_DR_SECURITIES_CONVERSION_BASE|基础证券转换基数|沪伦通|
|quote_PRESET_PRICE|期权昨结算|上证期权|
|quote_EXERCISE_WAY|行权方式|上证期权|
|quote_SUBSCRIBE_UPPER_LIMIT|市价申报数量上限|科创板|
|quote_SUBSCRIBE_LOWER_LIMIT|市价申报数量下限|科创板|
|quote_AFTER_HOURS_VOLUME|盘后成交量|科创板/深交所创业板|
|quote_AFTER_HOURS_AMOUNT|盘后成交额|科创板/深交所创业板|
|quote_AFTER_HOURS_TRANSACTION_NUMBER|盘后成交笔数|科创板|
|quote_AFTER_HOURS_WITH_DRAW_BUY_COUNT|盘后撤单买笔数|科创板|

|quote_AFTER_HOURS_WITH_DRAW_BUY_VOLUME|盘后撤单买数量|科创板|
|---|---|---|
|quote_AFTER_HOURS_WITH_DRAW_SELL_COUNT|盘后撤单卖笔数|科创板|
|quote_AFTER_HOURS_WITH_DRAW_SELL_VOLUME|盘后撤单卖数量|科创板|
|quote_AFTER_HOURS_BUY_VOLUME|盘后委托买入总量|科创板|
|quote_AFTER_HOURS_SELL_VOLUME|盘后委托卖出总量|科创板|
|quote_LONG_NAME|中文证券简称(长)||
|quote_LIMIT_PRICE_LOWER_LIMIT|限价申报数量下限||
|quote_LIMIT_PRICE_UPPER_LIMIT|限价申报数量上限||
|quote_ISSUED_CAPITAL|注册资本||
|quote_UPDOWN_LIMIT_TYPE|涨跌幅限制类型||
|quote_LISTINGTYPE|挂牌类型||
|quote_BUY_QTY_UPPER_LIMIT|限价买数量上限|深交所|
|quote_SELL_QTY_UPPER_LIMIT|限价卖数量上限|深交所|
|quote_MARKET_BUY_QTY_UPPER_LIMIT|市价买数量上限|深交所|
|quote_MARKET_SELL_QTY_UPPER_LIMIT|市价卖数量上限|深交所|
|quote_SECURITY_STATUS|证券状态|深交所|
|quote_BUY_SELL_AUCTION_RANGE|买卖有效竞价范围|深交所|
|quote_AFTER_HOURS_BUY_UPPER_LIMIT|盘后定价交易买数量上限|深交所创业板|
|quote_AFTER_HOURS_SELL_UPPER_LIMIT|盘后定价交易卖数量上限|深交所创业板|
|quote_STOCK_INFO|是否是注册制(reg字段.在同一栏位,传一次quote_STOCK_INFO即 可)|深交所创业板|
|quote_STOCK_INFO|是否具有协议控制架构标识(vie字段.在同一栏位,传一次 quote_STOCK_INFO即可)|深交所创业板|
|quote_MF|市场化转融通标识|深交所|
|quote_RSLF|限售股份出借标志|深交所|
|quote_MMF|做市商标志|深交所|
|quote_PRE_DELTA|昨虚实度|期货|
|quote_CUR_DELTA|今虚实度|期货|
|quote_UPDATE_MILLISECOND|最后修改毫秒|期货|
|quote_UNDERLYING_LAST_PRICE|标的现价(两位小数)|期货|
|quote_UNDERLYING_PRE_CLOSE|标的昨收(两位小数)|期货|
|quote_UNDERLYING_CHG|标的涨跌 (两位小数)|期货|
|quote_UNDERLYING_SYMBOL|标的名称|期货|
|quote_UNDERLYING_TYPE|标地品种|期货|
|quote_CHANGE1|涨跌1|期货|
|quote_POS_DIFF|仓差|期货、期权|
|quote_CUR_DIFF|期现差|期货|
|quote_CALL_OR_PUT|期权类型|期货|
|quote_EXERCISE_PRICE|行权价|期货|
|quote_PREMIUM_RATE|溢价率(长)|期货|
|quote_REMAINING_DAYS|剩余天数|期货|

|quote_IMPLIED_VOLATILITY|隐含波动率|期货|
|---|---|---|
|quote_RISK_FREE_INTEREST_RATE|无风险利率|期货|
|quote_RISK_INDICATOR|风险指标|期货|
|quote_LEVERAGE_RATIO|杠杆比率|期货|
|quote_INTERSECTION_NUM|交割点数|期货|
|quote_FINAL_TRADE_DATE|期权到期日|期货|
|quote_TRADE_DAY|交易日|期货|
|quote_SETTLEMENT_GROUP_ID|结算组代码|期货|
|quote_SETTLEMENT_ID|结算编号|期货|
|quote_PRE_OPEN_INTEREST|昨持仓量(无小数点)|期货|
|quote_OPT|持仓量(0位小数)|期货|
|quote_POSITION_CHG|日增(0位小数)|期货|
|quote_PRESENT_CLOSE|今收盘价|期货|
|quote_SETTLEMENT|今结算价|期货|
|quote_DELIVERY_DAY|交割日期|期货|
|quote_BID|委托买价和委托买量|期货|
|quote_OFFER|委托卖价和委托卖量|期货|
|quote_TOTAL_BID|委买|期货|
|quote_TOTAL_ASK|委卖|期货|
|quote_BID_VOL|买一量|期货|
|quote_ASK_VOL|卖一量|期货|
|quote_TIME_VALUE|时间价值|期货|
|quote_IN_VALUE|内在价值|期货|
|quote_AVERAGE_CHG|均涨幅|板块指数|
|quote_BLOCK_CHG|权涨幅|板块指数|
|quote_RATIO_UP_DOWN|涨跌平家数|板块指数|
|quote_CLOSE_INDEX|收盘指数|板块指数|
|quote_INDEX_CHG5|5日指数涨跌幅|板块指数|
|quote_INDEX_CHG10|10日指数涨跌幅|板块指数|
|quote_ROE|年化净资产收益率||
|quote_LAST_RECEIPTS|每股净利润|新三板|
|quote_UNDERLYING_SECURITY|基础证券标的券|新三板|
|quote_LIST_DATE|挂牌日期|新三板|
|quote_VALUE_DATE|起息日|新三板|
|quote_EXPIRING_DATE|到期日|新三板|
|quote_BUY_QTY_UNIT|买数量单位|新三板|
|quote_SELL_QTY_UNIT|卖数量单位|新三板|
|quote_MARKET_NUMBER|做市商数量|新三板|
|quote_SERVICE_STATUS|服务状态|新三板|

|quote_SUSPENDED_SYMBOL|停牌标识|新三板|
|---|---|---|
|quote_EX_DIVIDEND_RIGHT_SYMOBL|除权除息标识|新三板|
|quote_TRANSFER_STATUS|转让状态|新三板|
|quote_TRANSFER_TYPE|转让类型|新三板|
|quote_SECURITY_LEVEL|证券级别|新三板|
|quote_MARKET_MAKER_QTY|做市商数量|北证|
|quote_ISSUE_PE|发行市盈率|新三板|
|quote_UNRESTRICTED_SHARE_CAPITAL|非限售股本|新三板|
|quote_PAR_VALUE|每股面值|新三板|
|quote_CONVERT_RATE|折合比例|新三板|
|quote_CVT_PRICE|转股价格|新三板|
|quote_CPUTTRIGGER_PRICE|回售触发价|新三板|
|quote_SHARE_VALUE|每股面值|北证|
|quote_REDUCED_PROPORTION|折合比例|北证|
|quote_MONTH_CHANGE_RATE|本月涨跌幅|沪深京市场|
|quote_YEAR_CHANGE_RATE|本年涨跌幅|沪深京市场|
|quote_RECENT_MONTH_CHANGE_RATE|近一月涨跌幅|沪深京市场|
|quote_RECENT_YEAR_CHANGE_RATE|近一年涨跌幅|沪深京市场|
|quote_TTM|滚动市盈率|沪深|
|quote_BUY_VOL1|买一量|沪深|
|quote_SELL_VOL1|卖一量|沪深|
|quote_LISTING_DATE|上市日期|沪深|
|quote_CHANGERATE5|前5日涨跌幅|沪深京|
|quote_CHANGERATE10|前10日涨跌幅|沪深京|
|quote_CHANGERATE20|前20日涨跌幅|沪深京市场|
|quote_TURNOVER_RATE5|前5日换手率|沪深市场|
|quote_TURNOVER_RATE10|前10日换手率|沪深市场|
|quote_TURNOVER_RATE20|前20日换手率|沪深市场|
|quote_LIMITUP_CHANGERATE|沪深两市涨停板百分比|沪深市场|
|quote_LIMITDOWN_CHANGERATE|沪深两市跌停板百分比|沪深市场|
|quote_LAST_TRADE_DATE|预估最后交易日(用于退市整理股票展示)|沪深市场|
|quote_SECT|股票证券类别|沪深港|
|quote_MATCH_LAST_PRICE|匹配成交最新价|深圳债券|
|quote_MATCH_VOL|匹配成交成交量|深圳债券|
|quote_MATCH_AMOUNT|匹配成交成交额|深圳债券|
|quote_TRADE_PHASE1|交易方式所处阶段|深圳债券|
|quote_TRADE_TYPE|最新价成交方式|深圳债券|
|quote_FIVE_MINUTES_CHANGERATE|五分钟涨速||
|quote_THREE_MINUTES_CHANGERATE|三分钟涨速||
|quote_STOCK_INFO|货币种类(hbzl字段.在同一栏位,传一次quote_STOCK_INFO即可)||

|quote_HIGH_PRECISION_IOPV|高精度iopv|上海市场|
|---|---|---|
|quote_LONG_NAME|中文证券简称(长)||
|quote_TRANSACTION_NUM|现成交笔数||
|quote_STOCK_INFO|是否支持回转交易字段||
|quote_OPTION_BREAK_REFERFENCE_PRICE|期权熔断参考价|沪深市场|
|quote_CHANGERATE3|前3日涨跌幅|沪深京市场|
|quote_CHANGERATE60|前60日涨跌幅|沪深京市场|
|quote_YESTERDAY_CHANGERATE|昨日涨跌幅|沪深京市场|
|quote_BUY_CANCEL_COUNT|ETF申购笔数|沪L2,深L1、L2|
|quote_BUY_CANCEL_NUM|ETF申购数量|沪L2,深L1、L2|
|quote_BUY_CANCEL_AMOUNT|ETF申购金额|沪L2,深证无数据|
|quote_SELL_CANCEL_COUNT|ETF赎回笔数|沪L2,深L1、L2|
|quote_SELL_CANCEL_NUM|ETF赎回数量|沪L2,深L1、L2|
|quote_SELL_CANCEL_AMOUNT|ETF赎回金额|沪L2,深证无数据|

##### **增值指标部分V3自定义类别(ZZAddValueCustomField)** 

|**名称**|**说明**|**备注**|
|---|---|---|
|ALL_COLUMN|所有栏位|若查所有栏位,则自定义栏位数组里只 能有该栏位,不能添加其他栏位。|
|addValue_CODE|证券代码||
|addValue_DATE|当前快照日期|暂时关闭|
|addValue_TIME|当前快照时间|暂时关闭|
|addValue_ULTRALARGEBUYVOLUME|超大单主动买入成 交量||
|addValue_ULTRALARGESELLVOLUME|超大单主动卖出成 交量||
|addValue_ULTRALARGEBUYAMOUNT|超大单主动买入成 交额||
|addValue_ULTRALARGESELLAMOUNT|超大单主动卖出成 交额||
|addValue_LARGEBUYVOLUME|大单主动买入成交 量||
|addValue_LARGESELLVOLUME|大单主动卖出成交 量||
|addValue_LARGEBUYAMOUNT|大单主动买入成交 额||
|addValue_LARGESELLAMOUNT|大单主动卖出成交 额||

|addValue_MEDIUMBUYVOLUME|中单主动买入成交 量|
|---|---|
|addValue_MEDIUMSELLVOLUME|中单主动卖出成交 量|
|addValue_MEDIUMBUYAMOUNT|中单主动买入成交 额|
|addValue_MEDIUMSELLAMOUNT|中单主动卖出成交 额|
|addValue_SMALLBUYVOLUME|小单主动买入成交 量|
|addValue_SMALLSELLVOLUME|小单主动卖出成交 量|
|addValue_SMALLBUYAMOUNT|小单主动买入成交 额|
|addValue_SMALLSELLAMOUNT|小单主动卖出成交 额|
|addValue_ULTRALARGENETINFLOW|超大单净流入|
|addValue_LARGENETINFLOW|大单净流入|
|addValue_MEDIUMNETINFLOW|中单净流入|
|addValue_SMALLNETINFLOW|小单净流入|
|addValue_FUNDSINFLOW|主力资金流入|
|addValue_FUNDSOUTFLOW|主力资金流出|
|addValue_ULTRALARGEDIFFER|超大单差|
|addValue_LARGEDIFFER|大单差|
|addValue_MEDIUMDIFFER|中单差|
|addValue_SMALLDIFFER|小单差|
|addValue_LARGEBUYDEALCOUNT|每单大买单成交手 数(超大单+大 单)|
|addValue_LARGESELLDEALCOUNT|每单大卖单成交手 数(超大单+大 单)|
|addValue_DEALCOUNTMOVINGAVERAGE|每单成交手数移动 平均值|
|addValue_BUYCOUNT|买入单数|
|addValue_SELLCOUNT|卖出单数|
|addValue_BBD|大单净差|

|addValue_BBD5|五日大单净差|
|---|---|
|addValue_BBD10|十日大单净差|
|addValue_DDX|主力动向|
|addValue_DDX5|五日主力动向|
|addValue_DDX10|十日主力动向|
|addValue_DDY|涨跌动向|
|addValue_DDY5|五日涨跌动向|
|addValue_DDY10|十日涨跌动向|
|addValue_DDZ|大单差分|
|addValue_RATIOBS|单数比|
|addValue_OTHERSFUNDSINFLOW|散户资金流入|
|addValue_OTHERSFUNDSOUTFLOW|散户资金流出|
|addValue_NET_CAPITAL_INFLOW|主力资金净流入|
|addValue_FIVE_MINUTES_CHANGERATE|五分钟涨跌幅|
|addValue_DATES|当日与五日日期|
|addValue_LARGEORDERNUMB|超大单买入单数|
|addValue_LARGEORDERNUMS|超大单卖出单数|
|addValue_BIGORDERNUMB|大单买入单数|
|addValue_BIGORDERNUMS|大单卖出单数|
|addValue_MIDORDERNUMB|中单买入单数|
|addValue_MIDORDERNUMS|中单卖出单数|
|addValue_SMALLORDERNUMB|小单买入单数|
|addValue_SMALLORDERNUMS|小单卖出单数|
|addValue_MAINFORCEMONEYNETINFLOW5|5日主力资金净流 入|
|addValue_MAINFORCEMONEYNETINFLOW10|10日主力资金净流 入|
|addValue_MAINFORCEMONEYNETINFLOW20|20日主力资金净流 入|
|addValue_RATIOMAINFORCEMONEYNETINFLOW5|5日主力资金净流 入占比|
|addValue_RATIOMAINFORCEMONEYNETINFLOW10|10日主力资金净流 入占比|

|addValue_RATIOMAINFORCEMONEYNETINFLOW20|20日主力资金净流 入占比|
|---|---|
|addValue_LARGEINFLOW|超大单流入|
|addValue_BIGINFLOW|大单流入|
|addValue_MEDIUMINFLOW|中单流入|
|addValue_SMALLINFLOW|小单流入|
|addValue_LARGEOUTFLOW|超大单流出|
|addValue_BIGOUTFLOW|大单流出|
|addValue_MEDIUMOUTFLOW|中单流出|
|addValue_SMALLOUTFLOW|小单流出|

##### **期货自定义类别(ZZFuturesQuoteBaseField)** 

|**名称**|**说明**|**备注**|
|---|---|---|
|code|股票代码||
|name|代码||
|prev_close|昨收(3位小数)||
|open|开盘||
|high|最高||
|low|最低||
|last|最新||
|avg|均价||
|change|涨跌||
|chg_rate|涨跌幅||
|volume|成交量||
|amount|成交金额||
|now_vol|当前成交量||
|sell_vol|内盘||
|buy_vol|外盘||
|tradingDay|交易日||
|settlementGroupID|结算组代码||

|settlementID|结算编号||
|---|---|---|
|preSettlement|昨结算||
|preOpenInterest|昨持仓量|三位小数|
|opt|持仓量|三位小数|
|position_chg|日增|三位小数|
|close|今收盘价||
|settlement|今结算价||
|upperLimit|涨停价||
|downLimit|跌停价||
|preDelta|昨虚实度||
|currDelta|今虚实度||
|updateMillisec|最后修改毫秒||
|type|类型||
|underlyingLastPx|标的现价|股指期货 保留两位小数|
|underlyingPreClose|标的昨收|股指期货 保留两位小数|
|underlyingchg|标的涨跌|股指期货 保留两位小数|
|tradeStatus|交易状态|期货|
|change1|change1|期货|
|amp_rate|振幅|期货|
|posDiff|仓差|期货|
|期货期权|||
|callOrPut|期权类型||
|excercisePx|行权价||
|premiumRate|溢价率||
|remainingDays|剩余天数||
|impliedVolatility|隐含波动率||
|riskFreeInterestRate|无风险利率||
|riskIndicator|风险指标||
|leverageRatio|杠杆比率||

|intersectionNum|
|---|

|交割点数|
|---|

#### **期货自定义类别** **Error: You can't use 'macro parameter character #' in math ) mode** 

|**名称**|**说明**|**备注**|
|---|---|---|
|entrustDiff|委差||
|bid|买价与买量|买价对应 ZZQuoteItem属性buyPrices买量对应 ZZQuoteItem属 性buyVolumes|
|offer|卖价与卖量|卖价对应 ZZQuoteItem属性sellPrices卖量对应 ZZQuoteItem属 性sellVolumes|
|entrustRatio|委比|对应 ZZQuoteItem属性orderRatio|
|currDiff|期现差||
|underlyingType|标的品种||
|posDiff|仓差||
|deliveryDay|交割日期 YYYYMMDD||
|totalBid|委买||
|totalAsk|委卖||

##### **期货自定义类别(ZZFuturesQuoteField)父类信息参考ZZFuturesQuoteBaseField** 

|**名称**|**说明**|**备注**|
|---|---|---|
|bidpx1|买1价|买价对应 ZZQuoteItem属性buyPrices|
|bidvol1|买1量|买量对应 ZZQuoteItem属性buyVolumes|
|askpx1|卖1价|卖价对应 ZZQuoteItem属性sellPrices|
|askvol1|卖1量|卖量对应 ZZQuoteItem属性sellVolumes|

##### **分笔逐笔共同的父类模型(ZZBaseTickItem)** 

|**方法名称**|**说明**|**备注**|
|---|---|---|
|transactionStatus|买卖标识|买:B卖:S未知:N|
|transactionTime|交易时间|格式:09303030时分秒毫秒|
|singleVolume|交易量|单位:手|
|transactionPrice|成交价格||

##### **逐笔成交/逐笔还原模型(TickDetailItem),父类信息ZZBaseTickItem** 

|**index**|**索引**||
|---|---|---|
|bn|买委托序号|仅提供了L2Plus权限的用户才提供|
|on|卖委托序号|仅提供了L2Plus权限的用户才提供|
|bq|买委托量|仅提供了L2Plus权限的用户才提供|
|oq|卖委托量|仅提供了L2Plus权限的用户才提供|
|br|买方剩余量|仅提供了L2Plus权限的用户才提供|
|sr|卖方剩余量|仅提供了L2Plus权限的用户才提供|

##### **分笔模型(ZZTickItem),父类信息ZZBaseTickItem** 

|**AMSStatus**|**AMS状态(只有港股的AMS状态有值,非港股返回null)**|**string**||
|---|---|---|---|
|minValueOfIndexRange|索引范围的最小值|string||
|maxValueOfIndexRange|索引范围的最大值|string||
|type|成交性质:期货有 值|string|1、多头换手;2、空头换手;3、多 头开仓;4、多头平仓;5、空头开 仓;6、空头平仓;7、双开仓;8、 双平仓|
|openInterestDiff|仓差|string||
|openInterest|开仓量|string||
|closeInterest|平仓量|string||
|transactionNum|成交笔数|string||

##### **逐笔委托(ZZTickEntrustItem)** 

|**sn**|**委托序号**|
|---|---|
|price|委托价|
|volume|委托量|
|bs|买卖方|
|time|卖委时间|

##### **千档数据(ZZThousandsData)** 

|**属性名称**|**形态**|**说明**|
|---|---|---|
|code|string|股票代码|
|buyItems|ZZThousandsItem[]|千档行情(买)|
|sellItems|ZZThousandsItem[]|千档行情(卖)|

##### **千档数据(ZZThousandsItem)** 

|**属性名称**|**形态**|**说明**|
|---|---|---|
|originalPrice|string|原始价格代码(订阅全息时用)|
|price|string|委托价格|
|volume|string|委托量|
|count|string|笔数(委托单子数量)|
|bs|string|买卖方向|

##### **全息数据(ZZQXData)** 

|**属性名称**|**形态**|**说明**|
|---|---|---|
|code|string|股票代码|
|price|string|价格,和档位价格比较,判定档位|
|items|QXItem[]|全席数据|

##### **全息数据(QXItem)** 

|**属性名称**|**形态**|**说明**|
|---|---|---|
|sn|string|委托序号|
|bs|string|买卖方向|
|volume|string|委托量|

##### **分价模型(PriceVolumeItem)** 

|**price**|**价格**|**string**|
|---|---|---|
|volume|买卖总量|string|
|buyVolume|买量|string|
|sellVolume|卖量|string|
|unknownVolume|未知买卖方向量|string|
|tradeCount|买卖笔数|string|
|buyCount|买笔数|string|
|sellCount|卖笔数|string|
|unknownCount|未知买卖方向笔数|string|

##### **GetServerIpController ping站点** 

|**方法名**|**参数说明**|**功能**|
|---|---|---|
|pingIp()|无参 数|ping所有不通的市场对应的站点SDK内部根据轮询设置的时间 ( AppInfo.refreshTime)定时调用该方法|

##### **增值指标走势接口列表(ZZChartSubType)** 

|**参数**|**简称**|**名称**|**备注**|
|---|---|---|---|
|1|DDX|DDX指标(主力动 向)|依次返回时间、DDX|
|2|DDY|DDY指标(涨跌动 因)|依次返回时间、DDY|
|3|DDZ|DDZ指标(大单差 分)|依次返回时间、DDZ|
|4|BBD|BBD指标(大单净 差)|依次返回时间、BBD|
|5|ratioBS|ratioBS指标(单数 比)|依次返回时间、ratioBS|
|6|captialGame|资金博弈指标|依次时间、超大单净流入、大单净流入、中单净流入、 小单净流入|
|7|bigNetVolume|大单净量|依次时间、大单净量|

##### **沪深A股及指数涨跌平家数(ZZUpdownsItem)** 

|**属性名**|**类型**|**说明**|
|---|---|---|
|upCount|String|上涨家数|
|downCount|String|下跌家数|
|sameCount|String|平盘家数|

##### **沪股通和深股通额度(HSAmountItem)** 

|**属性名**|**说明**|**型态**|**备注**|
|---|---|---|---|
|hgtInitialQuotaS|南向港股通沪每日初始额度|string||
|hgtRemainingQuotaS|南向港股通沪日中剩余额度|string||
|hgtQuotaStatusS|南向港股通沪额度状态1:不可用,2:可用,0或者null:源没 有,3:充足|string||
|hgtTotalBuyAmountS|南向港股通沪总买入成交额|string||
|hgtTotalSellAmountS|南向港股通沪总卖出成交额|string||
|hgtBuySellTotalAmountS|南向港股通沪买卖总成交额|string||
|hgtInitialQuotaN|北向沪股通每日初始额度|string||
|hgtRemainingQuotaN|北向沪股通日中剩余额度|string||
|hgtTotalBuyAmountN|北向沪股通总买入成交额|string||
|hgtTotalSellAmountN|北向沪股通总卖出成交额|string||
|hgtBuySellTotalAmountN|北向沪股通买卖总成交额|string||
|sgtInitialQuotaS|南向港股通深每日初始额度|string||
|sgtRemainingQuotaS|南向港股通深日中剩余额度|string||
|sgtQuotaStatusS|南向港股通深额度状态1:不可用,2:可用,0或者null:源没 有,3:充足|string||
|sgtTotalBuyAmountS|南向港股通深总买入成交额|string||
|sgtTotalSellAmountS|南向港股通深总卖出成交额|string||
|sgtBuySellTotalAmountS|南向港股通深买卖总成交额|string||
|sgtInitialQuotaN|北向深股通每日初始额度|string||
|sgtRemainingQuotaN|北向深股通日中剩余额度|string||
|sgtTotalBuyAmountN|北向深股通总买入成交额|string||
|sgtTotalSellAmountN|北向深股通总卖出成交额|string||
|sgtBuySellTotalAmountN|北向深股通买卖总成交额|string||

##### **集合竞价走势模型(ZZBidItem)** 

|**属性名**|**说明**|**型态**|**备注**|
|---|---|---|---|
|lastPrice|最新价|string||
|referencePrice|参考价|string||
|datetime|时间,精确到秒|string||
|sellVolume1|卖一量|string||
|sellVolume2|卖二量|string||
|buyVolume1|买一量|string||
|buyVolume2|买二量|string||

##### **板块指数模型(ZZPlateIndex)** 

|**属性名**|**说明**|**型态**|**备注**|
|---|---|---|---|
|blockID|证券代码|String||
|subType|子类别|String||
|dateTime|当前快照日期|String||
|blockIndex|板块指数|String||
|blockChg|板块权涨幅|String||
|averageChg|板块均涨幅|String||
|turnoverRate|换手率|String||
|ratioUpDown|0:涨;1:跌;2:平家数|String||
|indexChg|指数涨跌幅|String||
|upDownFlag|指数涨跌幅标识正负号|String|值为"+"或者"-"|
|indexChg5|5日指数涨跌幅|String||
|indexChg10|10日指数涨跌幅|String||
|largeMoneyNetInflow|超大单净流入|String||
|bigMoneyNetInflow|大单净流入|String||
|midMoneyNetInflow|中单净流入|String||
|smallMoneyNetInflow|小单净流入|String||
|mainforceMoneyInflow|主力资金流入|String||
|mainforceMoneyOutflow|主力资金流出|String||

|mainforceMoneyNetInflow5|5日主力资金净流入|String|
|---|---|---|
|mainforceMoneyNetInflow10|10日主力资金净流入|String|
|largeVolumeB|超大单买入成交量|String|
|largeVolumeS|超大单卖出成交量|String|
|largeMoneyB|超大单买入成交额|String|
|largeMoneyS|超大单卖出成交额|String|
|bigVolumeB|大单买入成交量|String|
|bigVolumeS|大单卖出成交量|String|
|bigMoneyB|大单买入成交额|String|
|bigMoneyS|大单卖出成交额|String|
|midVolumeB|中单买入成交量|String|
|midVolumeS|中单卖出成交量|String|
|midMoneyB|中单买入成交额|String|
|midMoneyS|中单卖出成交额|String|
|smallVolumeB|小单买入成交量|String|
|smallVolumeS|小单卖出成交量|String|
|smallMoneyB|小单买入成交额|String|
|smallMoneyS|小单卖出成交额|String|
|totalTrdMoney|总成交额|String|
|blockFAMC|板块流通市值|String|
|totalMarketValue|板块总市值|String|
|mainforceMoneyNetInflow20|20日主力资金净流入|String|
|ratioMainforceMoneyNetInflow5|5日主力资金净流入占比|String|
|ratioMainforceMoneyNetInflow10|10日主力资金净流入占比|String|
|ratioMainforceMoneyNetInflow20|20日主力资金净流入占比|String|
|totalTrdVolume|总成交量|String|
|openBlockIndex|开盘板块指数|String|
|highBlockIndex|最高板块指数|String|

|lowBlockIndex|最低板块指数|String|
|---|---|---|
|closeBlockIndex|收盘板块指数|String|
|committee|委比|String|
|deviation|委差|String|
|buyNum|委买|String|
|sellNum|委卖|String|
|ttm|动态市盈率|String|
|lyr|静态市盈率|String|
|marketRate|市净率|String|
|blockName|板块名称|String|
|preCloseBlockIndex|前收盘指数|String|
|upsDowns|涨跌额|String|
|amplitude|振幅|String|

##### **CDR,GDR联动(ZZDRLinkItem)** 

|**属性名**|**说明**|**型态**|**备注**|
|---|---|---|---|
|code|代码|string||
|name|名称|string||
|datetime|时间|string||
|subtype|类别|string||
|lastPrice|最新价|string||
|preClosePrice|昨收价|string||
|changeRate|涨幅|string||
|change|涨跌|string||
|premiumRate|联动代码溢价率|string||

##### **KZZ联动(ZZKZZLinkItem)** 

|**属性名**|**说明**|**型态**|**备注**|
|---|---|---|---|
|code|代码|string||
|name|名称|string||
|market|市场|string||
|subtype|类别|string||
|lastPrice|最新价|string||
|preClosePrice|昨收价|string||
|changeRate|涨幅|string||
|change|涨跌|string||
|changeState|涨跌状态|string||
|premiumRate|联动代码溢价率|string||
|transferPrice|转股价|string||

##### **AH联动(ZZAHLinkItem)** 

|**属性名**|**说明**|**型态**|**备注**|
|---|---|---|---|
|code|代码|string||
|name|名称|string||
|lastPrice|最新价|string||
|preClosePrice|昨收价|string||
|changeRate|涨跌幅|string||
|premiumRate|联动代码AH溢价率|string||
|premiumRateHA|联动代码HA溢价率|string||

##### **AB联动(ZZABLinkItem)** 

|**属性名**|**说明**|**型态**|**备注**|
|---|---|---|---|
|code|代码|string||
|name|名称|string||
|market|市场|string||
|subtype|类别|string||
|lastPrice|最新价|string||
|preClosePrice|昨收价|string||
|change|涨跌|string||
|changeRate|涨幅|string||
|premiumRateAB|AB溢价率|string||
|premiumRateBA|BA溢价率|string||

##### **uk市场快照单独接口,可支持多商品(ZZUKItem)** 

|**属性名**|**说明**|**型态**|**备注**|
|---|---|---|---|
|code|代码|String||
|name|名称|String||
|subtype|次类别|String||
|lastPrice|最新价|String||
|openPrice|开盘价|String||
|datetime|日期|String||
|volume|成交量|String||
|amount|成交额|String||
|transactionNumber|成交笔数|String||
|buyPrice|收盘买一价|String||
|sellPrice|收盘卖一价|String||
|highPriceDayAuto|日内最高价(自动交易)|String||
|highPriceNonDayAuto|日内最高价(非自动交 易)|String||
|lowPriceDayAuto|日内最低价(自动交易)|String||

|lowPriceNonDayAuto|日内最低价(非自动交 易)|String||
|---|---|---|---|
|highPriceYearAuto|近一年来最高价(自动 交易)|String||
|highPriceNonYearAuto|近一年来最高价(非自 动交易)|String||
|lowPriceYearAuto|近一年来最低价(自动 交易),|String||
|lowPriceNonYearAuto|近一年来最低价(非自 动交易),|String||
|highPriceTimeYearAuto|近一年来最高价出现日 期(自动交易)|String||
|highPriceTimeYearNonAuto|近一年来最高价出现日 期(非自动交易)|String||
|lowPriceTimeYearAuto|近一年来最低价出现日 期(自动交易)|String||
|lowPriceTimeYearNonAuto|近一年来最低价出现日 期(非自动交易)|String||
|averagePrice|均价|String||
|currency|币种|String||
|listingDate|上市日期|String||
|conversionBase|转换基数|String||
|securitiesConversionBase|基础证券转换基数|String||
|GDR|GDR标识|String|沪伦通标识gdr为1时表示沪伦通 gdr,为2时表示gdr基础证券|
|DR|CDR标识|String|沪伦通标识cdr为1时表示沪伦通 cdr,为2时表示cdr基础证券|
|DRStockCode|GDR基础证券代码 或 者CDR代码|String||
|DRStockName|GDR基础证券名称 或 者CDR名称|String||
|DRSubtypes|GDR基础证券次类别 或者CDR次类别|String||
|subjectClosingReferencePrice|标的收盘参考价|String||

溢价 

premiumRate 

String 

### **行情接口使用说明** 

##### **注册认证** 

###### **请求类:ZZRegisterReq** 

|**说明**|**方法**|
|---|---|
|注册方法|send(callback: IResponseCallback)|

|**参数**|
|---|

###### **调用样例** 

new ZZRegisterReq().send({ onSuccess: (resp: RegisterResp) => { console.info("resgister success") }, onFail: (err) => { console.info("resgister onFail:" + err.getMsg(\)); } }); 

##### **站点测速** 

###### **请求类:ZZPingReq** 

|**属性名**|**说明**|**形态**|**备注**|
|---|---|---|---|
|ip|http站点地址|string|如: http://100.1.1.1:22016|

###### **应答类:ZZPingResp** 

|**属性名**|**说明**|**形态**|**备注**|
|---|---|---|---|
|pingIP|http站点地址|string|如: http://100.1.1.1:22016|
|costTime|请求耗时|number|单位毫秒|

###### **调用样例** 

```arkts
let pingReq = new PingReq(); pingReq.ip = "http://100.1.1.1:22016"; pingReq.send({ onSuccess: (resp: PingResp) => { console.info("ping success") }, onFail: (err) => { console.info("ping onFail:" + err.getMsg(\)); } }); 
```

##### **SDK站点设置获取类(ZZSiteManagerUtils)** 

- 前端可根据站点类型获取该类别的站点列表,并可对该列表测试排序后选择最优站点设置到SDK的某类站点 里面 

- 方法1说明:获取某类站点列表 

|**方法名**|**参数名**|**说明**|**型态**|**备注**|
|---|---|---|---|---|
|getIpByMarket()|marketSiteType|站点类别|string|参考ZZMarketSiteType,需小写|

- 方法2说明:根据站点类别设置排序后的ip列表,可调用ZZPingReq进行测速 

|**方法名**|**参数名**|**说明**|**型态**|**备注**|
|---|---|---|---|---|
|setIPByMarket()|ips|站点|string[]|如: ( http://123.218.114.56:22016/)">>]|
|market|站点类型|String|参考ZZMarketSiteType,需小写||

##### **SDK注册配置信息** 

###### **说明** 

SDK注册配置 

###### **SseSdk** 

方法说明: 

|**方法名称**|**参数说明**|**备注**|
|---|---|---|
|static setDebug(debug:boolean)|设置是否打开log日志输出|true:开启,false:关闭|
|static setConfig(config: SseConfig)|参数:SseConfig类|参数参考 SseConfig|
|static permission()|无|所有市场权限配置 返回MarketPermission对 象 具体配置方法参考 MarketPermission|
|static getHid()|获取行情源唯一吗,可用于 查询请求情况,排查问题|唯一吗以ohos@开头|
|static getVersion()|获取SDK版本号||
|static getEnv()|获取SDK行情环境|release:生产,dev:全真|

###### **SseConfig** 

- SDK注册配置信息:appKey、上下文 

- 方法说明: 

|**方法名称**|**备注**|
|---|---|
|setContext(context: Context)|传入上下联系文(必传)|
|setAppkey(appkey: string)|券商appkey(必传)|

##### **权限配置** 

###### **说明** 

- 沪深,港股,中金所权限配置 

- 境内沪深权限设置有两种方式:1、通过setLevel统一设置沪深权限,2、通过addShSzPermission单独分开 设置沪深权限。两种方式不可混用。 

###### **请求类:ZZMarketPermission** 

属性说明: 

|**方法名称**|**参数说明**|**功能**|
|---|---|---|
|setLevel(level: string)|统一设置沪深level状态|1表示沪深level1 2表示沪深level2可调用 Permissions.LEVEL_1 或 者 Permissions.LEVEL_2|
|addHkPermission(...marketPermisson: string[])|传入港股权限:单个或多个|可从 Permissions中取值|
|removeHkPermission(marketPermisson: string)|移除港股权限|可从 Permissions中取值|
|clearHkPermission()|清空港股权限||
|setSseLevel(level: string)|统一设置大商所,郑商 所,全球,外汇市场,中 金所,期货,上海原油的 level|可从 Permissions中取值 例如:Permissions.LEVEL_2|
|addShSzOverseaPermission(permission: string)|设置 沪深境外权限|可从 Permissions中取值 例如:Permissions.OL_LEVEL_1(境外沪深 level1) Permissions.OL_SH_LEVEL_2(境外上海level2) Permissions.OL_SZ_LEVEL_2(境外深圳level2)|
|removeShSzOverseaPermission(permission: string)|移除 沪深境外权限|可从 Permissions中取值 例如:Permissions.OL_LEVEL_1(境外沪深 level1) Permissions.OL_SH_LEVEL_2(境外上海level2) Permissions.OL_SZ_LEVEL_2(境外深圳level2)|
|addShSzPermission(permission: string)|单独分开添加沪深权限, 调用此方法后已调用 setLevel方法设置的权限将 失效|可从 Permissions中取值 例如:Permissions.SH_LEVEL_1(上海 level1) Permissions.SZ_LEVEL_1(深圳level1) Permissions.SH_LEVEL_2(上海level2) Permissions.SZ_LEVEL_2(深 圳level2)|
|removeShSzPermission(permission: string)|单独移除沪深权限|可从 Permissions中取值 例如:Permissions.SH_LEVEL_1(上海 level1) Permissions.SZ_LEVEL_1(深圳level1) Permissions.SH_LEVEL_2(上海level2) Permissions.SZ_LEVEL_2(深 圳level2)|
|addHKOverseaPermission(permission: string)|设置 港股境外权限|可从 Permissions中取值 例如:Permissions.OL_HK0(境外港股10 档) Permissions.OL_HKA1(境外港股实时一档)|
|removeHKOverseaPermission(permission: string)|移除 港股境外权限|可从 Permissions中取值 例如:Permissions.OL_HK0(境外港股10 档) Permissions.OL_HKA1(境外港股实时一档)|

##### **行情快照** 

###### **说明** 

通过设置股票代码可获取该股票的行情数据,例如:600000.sh。 

- 股票商品市场别,如下: 

   - 上证:sh 

   - 深证:sz 

   - 港股:hk 

###### **请求类:ZZQuoteDetailReq** 

参数说明 

|**参数名**|**说明**|**型态**|**备注**|
|---|---|---|---|
|code|股票代 码|string||
|quoteColumns|快照自 定义栏 位|number[]|1:自定义栏位请参考 ZZQuoteCustomField2:当该参数为为空 时,内部默认请求所有栏位3:外汇不支持自定义栏位,会默认请求 所有栏位|
|addValueColumns|增值指 标自定 义栏位|number[]|1:自定义栏位请参考 ZZAddValueCustomField 2:当该参数为为 空时,内部默认请求所有栏位3:新三板 、外汇、期货不返回增值 指标数据,此参数对该市场无效|
|**类:ZZQuoteResp属性名** 属性说明:|**说明**|**型态**|**备注**|
|ZZQuoteItems|资料列表|Sse|ArrayList<ZZQuoteItem> 请参考 ZZQuoteItem|
|addValueModels|增值指标列|表 Sse|ArrayList<addValueModel> 请参考 ZZAddValueModel|

###### **应答类:ZZQuoteResp** 

###### **调用样例** 

```arkts
let quoteDetailReq = new ZZQuoteDetailReq(); quoteDetailReq.code = '600000.sh'; quoteDetailReq.send({ 
```

onSuccess: (resp: ZZQuoteResp) => { 

if (resp && resp.ZZQuoteItems && resp.ZZQuoteItems.length > 0) { this.item = resp.ZZQuoteItems.at(0); 

} 

if (resp && resp.addValueModels && resp.addValueModels.length > 0) { this.addValueModel = resp.addValueModels.at(0); } }, onFail: (error: ErrorInfo) => { } }) 

##### **走势数据** 

###### **说明** 

可获得当日走势数据。 

###### **请求类:ZZChartReq** 

入参说明 

|**属性名**|**说明**|**型态**|**备注**|
|---|---|---|---|
|code|股票代码|string||
|ZZChartType|走势型态|enum: ZZChartType|ZZChartType|
|subtype|子类别|string||
|returnAFData|是否返回盘后数 据|boolean|默认不返回, false:不返回, true:返 回|

###### **应答类:ZZChartResp** 

###### 属性说明 

|**属性名**|**说明**|**型态**|**备注**|
|---|---|---|---|
|OHLCItems|资料列表|ArrayList<OHLCItems>|请參考 ZZOHLCItem|
|AFItems|盘后数据|ArrayList<OHLCItems>|请參考 ZZOHLCItem|
|systemDatetime|市场交易时间|String||
|tradeDates|日期列表|ArrayList<String>|分时走势取get(0)|
|tickCount|连续竞价总点数|number||
|afTickCount|盘后交易总点数|number||
|timezones|交易时间段|string[][][]||
|referencePrices|参考价|Map<string,string>||
|referenceIOPVPrices|基金净值参考价|Map<string,string>||

###### **调用样例** 

let chartReq: ZZChartReq = new ZZChartReq(); 

chartReq.code = '688054.sh'; 

chartReq.chartType = ZZChartType.ChartTypeOneDay; 

chartReq.subtype = '1001; 

chartReq.returnAFData = true; 

chartReq.send({ 

onSuccess: (resp: ZZChartResp) => { 

if (resp.OHLCItems) { 

} 

}, onFail: (errorInfo: ErrorInfo) => { 

} 

}); 

**历史K线** 

###### **说明** 

- 1:可通过设置__K线周期(period)来获取不同周期的日K K线数据,例如: period=ZZOHLCPeriod.OHLCPeriodDay。 

- 2:支持 沪深港(市场:sh、sz、hk)、期货(cff,dce,czce,ine,shfe)、中证指数(csi)。 全部k线支持, 可以获取直到上市日的所有K线 

- 3:海外市场(收盘 市场:gb)。只支持日、周、月K历史K线,不支持复权。 

- 4:各市场支持k线类型参考交易市场支持的线图类型 

- 5:复权支持的K线类型参考复权支持的线图类型 

###### **请求类:ZZOHLCReq** 

###### 参数说明: 

|**属性名**|**说明**|**型态**|**备注**|
|---|---|---|---|
|code|股 票 代 码|string||
|period|K 线 周 期|string|ZZOHLCPeriod|
|subtype|次 类 别|number||
|requestType|请 求 类 型|RequestType|1、默认类型为RequestTypeRecent,取最新的300根K线数据2、当类型为RequestTypeNewer时, 取date日期之后的300根K线数据(注:沪深京港CSI、GB市场股票时不支持count自定义条数,返 回所传日期到当日的数据)3、当类型为RequestTypeOlder时,取date日期之前的300根K线数据 4、当类型为RequestTypeInterval时,获取指定区间的K线数据,此时时间格式为 @"yyyyMMdd,yyyyMMdd"|
|date|日 期/ 时 间|String|获取指定日期对应的数据,与requestType配合使用1:日周月K的时间格式为yyyyMMdd 2:分钟 K的时间格式为yyyyMMddHHmmss 3:特殊情况(针对RequestTypeInterval):当传入时间格式为 @"yyyyMMdd,yyyyMMdd"或@"yyyyMMddHHmmss,yyyyMMddHHmmss"时获取该时间区间的 数据,当传入时间格式为@"yyyyMMdd,n"或@"yyyyMMddHHmmss,n"或@"n,yyyyMMdd"或 @"n,yyyyMMddHHmmss"时获取获取一个时间往前或往后的n根,其中n>0。|
|priceAdjustedMode|复 权 类 型|OHLCPriceAdjustedMode|1、OHLCPriceAdjustedModeNone :不复权2、OHLCPriceAdjustedModeForward :前复权3、 OHLCPriceAdjustedModeBackward :后复权|
|count|自 定 义 条 数|number|其值必须满足于:0 < count <= 300.不传,默认300|

###### **应答类:ZZOHLCResp** 

属性说明 

|**属性名**|**说明**|**型态**|**备注**|
|---|---|---|---|
|OHLCItems|K线资料列表|ArrayList<OHLCItems>|请參考 ZZOHLCItem|
|FQItems|复权资料列表|ArrayList<FQItem>|请參考 FQItem|
|GBItems|股本资料列表|ArrayList<GBItem>|请參考 CirculatingShareItem|
|total|总条数|number|RequestTypeOlder、RequestTypeInterval才会返回|

###### **调用样例:最新300根 + 给定日期历史300根** 

//refresh, 最新300根 let ohlcReq = new ZZOHLCReq() ohlcReq.code = '600000.sh' ohlcReq.subtype = '1001' ohlcReq.period = ZZOHLCPeriod.OHLCPeriodDay ohlcReq.priceAdjustedMode = OHLCPriceAdjustedMode.OHLCPriceAdjustedModeNone ohlcReq.requestType =  RequestType.RequestTypeRecent ohlcReq.send({ onSuccess:(resp:ZZOHLCResp)=>{ if (resp.OHLCItems && resp.OHLCItems.length > 0) { 

} }, onFail: (err: ErrorInfo) => { } }) 

======================================================================================== //loadleft ,给定日期历史300根 let ohlcReq = new ZZOHLCReq() ohlcReq.code = '600000.sh' ohlcReq.subtype = '1001' ohlcReq.period = ZZOHLCPeriod.OHLCPeriodDay ohlcReq.priceAdjustedMode = OHLCPriceAdjustedMode.OHLCPriceAdjustedModeNone ohlcReq.requestType =  RequestType.RequestTypeOlder ohlcReq.date = '20221012' ohlcReq.send({ onSuccess:(resp:ZZOHLCResp)=>{ if (resp.OHLCItems && resp.OHLCItems.length > 0) { } }, onFail: (err: ErrorInfo) => { } }) 

###### **调用样例:K线请求自定义条数 (不支持的市场:全球指数、外汇、海外市场)** 

//请求最新10根 let ohlcReq = new ZZOHLCReq() ohlcReq.code = '600000.sh' 

```arkts
ohlcReq.subtype = '1001' ohlcReq.period = ZZOHLCPeriod.OHLCPeriodDay ohlcReq.priceAdjustedMode = OHLCPriceAdjustedMode.OHLCPriceAdjustedModeNone ohlcReq.requestType =  RequestType.RequestTypeRecent ohlcReq.count = 10 ohlcReq.send({ onSuccess:(resp:ZZOHLCResp)=>{ if (resp.OHLCItems && resp.OHLCItems.length > 0) { } }, onFail: (err: ErrorInfo) => { } }) ================================================================ //给定日期历史10根 let ohlcReq = new ZZOHLCReq() ohlcReq.code = '600000.sh' ohlcReq.subtype = '1001' ohlcReq.period = ZZOHLCPeriod.OHLCPeriodDay ohlcReq.priceAdjustedMode = OHLCPriceAdjustedMode.OHLCPriceAdjustedModeNone ohlcReq.requestType =  RequestType.RequestTypeOlder ohlcReq.date = '20221012' ohlcReq.count = 10 ohlcReq.send({ onSuccess:(resp:ZZOHLCResp)=>{ if (resp.OHLCItems && resp.OHLCItems.length > 0) { } }, onFail: (err: ErrorInfo) => { } }) 
```

###### **调用样例:k线区间** 

```arkts
let ohlcReq = new ZZOHLCReq() ohlcReq.code = '600000.sh' ohlcReq.subtype = '1001' ohlcReq.period = ZZOHLCPeriod.OHLCPeriodDay ohlcReq.priceAdjustedMode = OHLCPriceAdjustedMode.OHLCPriceAdjustedModeNone ohlcReq.requestType =  RequestType.RequestTypeInterval ohlcReq.date = '20221012,20231012' ohlcReq.send({ onSuccess:(resp:ZZOHLCResp)=>{ if (resp.OHLCItems && resp.OHLCItems.length > 0) { } }, onFail: (err: ErrorInfo) => { } 
```

}) 

##### **明细详情接口** 

###### **说明** 

- 分时明细接口, 分笔数据,中金所只有分笔接口。 限制100条 

###### **请求类:ZZTickReq** 

属性说明: 

|**属性名**|**说明**|**型态**|**备注**|
|---|---|---|---|
|stockId|股 票 代 码|string||
|param|需 要 的 条 数|string|(1)比如“0,15,-1”,第一个代表从第几条开始(获取最新的用0,其他的 用头里返回的数据“headerParams”详细见返回里面的),第二个代 表,显示几条,第三个-1代表获取最新的,1是代表获取相对老的,0代 表获取相对新的。(2) param:n1,n2,n3新的组合n3=2(固定) ,n2=条 数,n1=时间。如param:931,20,2获取9:31分以后的20条分笔或逐笔数 据|
|subtype|次 类 别|string||

**应答类:ZZTickResp** 

属性说明 

|**属性名**|**说明**|**型态**|**备注**|
|---|---|---|---|
|tickItems|资 料 列 表|List<ZZTickItem> tickItems|参考 ZZTickItem|
|headerParams|头 里 返 回 的 数 据|String headerParams|headerParams用“,”分割“left,right”形式。判断left和 right的大小,当获取想对老的数据用小的(即下一页如传 入“1989109.0,15,1”),获取相对新的数据用大的(即 上一页如传入“1989208.0,15,0”)|

###### **调用样例** 

```arkts
let tickReq = new ZZTickReq(); tickReq.stockId = this.item.id; tickReq.param = "0,10,-1" tickReq.subtype = this.item.subtype tickReq.send({ onSuccess: (resp: ZZTickResp) => { if (resp && resp.tickItems && resp.tickItems.length > 0) { } }, onFail: (error: ErrorInfo) => { } }) 
```

##### **L2单独分笔接口** 

###### **说明** 

- L2单独分笔接口,返回l2分笔数据,仅支持上海和深圳市场的非指数类股票,港股使用ZZTickReq 限制100条 

**请求类:ZZL2TickReq** 

属性说明: 

|**属性名**|**说明**|**型态备注**||
|---|---|---|---|
|code|股 票 代 码|string||
|param|需 要 的 条 数|string (1)比如“0,15,- 头里返回的数 显示几条,第 取相对新的。 时间。如par|1”,第一个代表从第几条开始(获取最新的用0,其他的用 据“headerParams”详细见返回里面的),第二个代表, 三个-1代表获取最新的,1是代表获取相对老的,0代表获 (2) param:n1,n2,n3新的组合n3=2(固定) ,n2=条数,n1= am:931,20,2获取9:31分以后的20条分笔或逐笔数据|
|subtype|次 类 别|string||
|**类:ZZL2TickR属性名** 属性说明|**esp**|**说明型态**|**备注**|
|tickItems||资 料 列 List<ZZTickItem>|请参考ZZTickItem|
|||表||
|headerPara|ms|头 里 返 回 的 数 据 String headerParams|headerParams用","分割“left,right”形式,left和right都 是double形式的。判断left和right的大小,当获取想对老 的数据用小的(即下一页如传入“1989109.0,15,1”), 获取相对新的数据用大的数据即上一页如传入 “1989208.0,15,0”)|

###### **应答类:ZZL2TickResp** 

###### **调用样例** 

```arkts
let tickReq = new ZZL2TickReq() tickReq.code = this.item.id tickReq.param = this.oldestIndex + ',15,1' tickReq.subtype = this.item.subtype tickReq.send({ onSuccess: (resp: ZZL2TickResp) => { if (resp.tickItems) { }, onFail: (err: ErrorInfo) => { 
```

}) 

} 

##### **L2单独逐笔成交接口** 

###### **说明** 

- L2单独逐笔接口,根据索引或者索引范围返回l2某个分笔下的逐笔数据,仅支持上海和深圳市场的非指数类 股票。 

限制100条 

###### **#请求类:ZZL2TickDetailReq** 

属性说明: 

|**属性名**|**说明**|**型态**|**备注**|
|---|---|---|---|
|code|股 票 代 码|string||
|param|需 要 的 条 数|string|(1)比如“0,15,-1”,第一个代表从第几条开始(获取相对新的用0,其他的 用头里返回的数据“headerParams”详细见返回里面的或者单独分笔接 口返回的索引),第二个代表,显示几条,第三个-1代表获取最新的, 1是代表获取相对老的,0代表获取相对新的。(2) param:n1,n2,n3新 的组合n3=2(固定) ,n2=条数,n1=时间。如param:931,20,2获取9:31分 以后的20条分笔或逐笔数据|
|subtype|次 类 别|string||

###### **应答类:ZZL2TickDetailResp** 

属性说明 

|**属性名**|**说明**|**型态**|**备注**|
|---|---|---|---|
||资|||
|tickDetailItems|料 列 表|List<ZZTickDetailItem>|请参考TickDetailItem|
|headerParams|头 里 返 回 的 数 据|string headerParams|headerParams用“,”分割“left,right”形式,left和right都是 double形式的。判断left和right的大小,当获取想对老的数据 用小的(即下一页如传入“1989109.0,15,1”),获取相对新 的数据用大的(即上一页如传入“1989208.0,15,0”)|
|**用样例** let req = new Z req.code = req.param = req.subtype req.send({|ZL2T this thi = t|ickDetailReq() .item.id s.rNewestIndex + ',15 his.item.subtype|,0'|
|onSuccess|: (r|esp: ZZL2TickDetailRe|sp) => {|

###### **调用样例** 

if (resp.tickDetailItems && resp.tickDetailItems.length > 0) { } }, onFail: (err: ErrorInfo) => { } }) 

##### **市场当年交易日接口** 

###### **说明** 

提供交易日历下载,获取所传日期的交易日历功能 

###### **请求类:ZZTradeDateReq** 

属性说明 

|**属性名**|**说明**|**型态**|**备注**|
|---|---|---|---|
|market|可传 多个 市场, 逗号 分割|String|市场别:SH(沪市),SZ(深市),BJ(新三板),HK(港股),SHHK (沪港通南向),SZHK(深港通南向),CFF(中金所),CZCE(郑商 所),DCE(大商所),HKSH(沪港通北向),HKSZ(深港通北向)* 多市场用逗号(,)隔开|

###### **应答类:ZZTradeDateResp** 

###### 属性说明 

|**属性名**|**说明**|**型态**|**备注**|
|---|---|---|---|
|dates|资料列表|Record<string,ZZTradeDateItem[]>|市场交易日列表: ZZTradeDateItem相应市场的交易日|

###### **调用样例** 

```arkts
let req = new ZZTradeDateReq(); req.market = "HK"; req.send({ onSuccess: (resp: TradeDateResp) => { }, onFail: (err: ErrorInfo) => { } }) 
```

##### **集合竞价走势接口** 

###### **说明** 

仅限沪深交易商品,提供集合竞价9:15-9:25的数据 

###### **请求类:ZZBidChartReq** 

参数说明: 

|**参数名**|**说明**|**型态**|**备注**|
|---|---|---|---|
|code|股票代码|string||
|subtype|子类别|string||

###### **应答类:ZZBidZZChartResp** 

###### 属性说明 

|**属性名**|**说明**|**型态**|**备注**|
|---|---|---|---|
|bidItems|股票代码|ArrayList<ZZBidItem>|可参考 ZZBidItem|
|systemDatetime|指数交易时间|string||
|tickCount|总点数|number||

###### **调用样例** 

```arkts
let bidChartReq = new ZZBidChartReq(); bidChartReq.code = '600000.sh' bidChartReq.subtype = '1001' bidChartReq.send({ onSuccess: (resp: ZZChartIndexResp) => { if (resp.items && resp.items.length > 0) { } }, onFail: (err: ErrorInfo) => { } }); 
```

##### **港股通额度统计(南北交易)** 

###### **说明** 

港股通额度统计(南北交易) 

###### **请求类:ZZHSAmountAllReq** 

方法说明: 

|**参数名**|**说明**|**型态**|**备注**|
|---|---|---|---|
|无||||

###### **应答类:ZZHSAmountAllResp** 

属性说明 

|**属性名**|**说明**|**型态**|**备注**|
|---|---|---|---|
|amountItem|额度|ZZHSAmountItem|可参考 ZZHSAmountItem|

###### **调用样例** 

ZZHSAmountAllReq request = new ZZHSAmountAllReq(); request.send({ onSuccess: (resp: ZZHSAmountAllResp) => { }, onFail: (err: ErrorInfo) => { } }); 

##### **走势副图指标接口** 

###### **说明** 

###### 根据传参返回走势副图指标数据 

###### **请求类:ZZChartIndexReq** 

参数说明: 

|**属性名**|**说明**|**型态**|**备注**|
|---|---|---|---|
|code|股 票 代 码|string|特殊代码,K00001沪市A股、K00002深市A股、K00003沪市科 创板、K00004深市创业板、K00005沪深A股、K00006沪市A 股、K00007深市A股|
|subtype|子 类 别|String||
||数|||
|type|据 类 别|ZZChartIndexType[]|ZZChartIndexType|
|beginIndex|开 始 索 引|number|默认0,非必选|
||开|||
|endIndex|始 索 引|number|默认-1,非必选|

###### **应答类:ZZChartIndexResp** 

###### 属性说明 

|**属性名**|**说明**|**型态**|**备注**|
|---|---|---|---|
|beginIndex|开始下标0开始|number||
|endIndex|结束下标(大于0)|number||
|items|资料列表|ArrayList<IndexItem>|参考 IndexItem|

###### **调用样例** 

let chartIndexReq = new ZZChartIndexReq() chartIndexReq.code = this.item.id 

chartIndexReq.subtype = this.item.subtype chartIndexReq.type = [ZZChartIndexType.ChartIndexTypeDDX, ZZChartIndexType.ChartIndexTypeDDY, ZZChartIndexType.ChartIndexTypeDDZ, ZZChartIndexType.ChartIndexTypeBBD , ZZChartIndexType.ChartIndexTypeRatioBS, ZZChartIndexType.ChartIndexTypeLargeMoneyInflow, ZZChartIndexType.ChartIndexTypeBigMoneyInflow, ZZChartIndexType.ChartIndexTypeMidMoneyInflow , ZZChartIndexType.ChartIndexTypeSmallMoneyInflow, ZZChartIndexType.ChartIndexTypeBigNetVolume] chartIndexReq.send({ onSuccess: (resp: ZZChartIndexResp) => { if (resp.items && resp.items.length > 0) { } }, onFail: (err: ErrorInfo) => { } }) 

##### **历史K线增值数据** 

**说明** 

根据传参返回历史K线增值数据(沪深股票及板块) 

**请求类:ZZOHLCIndexReq** 

参数说明: 

|**属性名**|**说明**|**型态**|**备注**|
|---|---|---|---|
|code|股 票 代 码|string|特殊代码,K00001沪市A股、K00002深市A股、K00003沪市科创 板、K00004深市创业板、K00005沪深A股、K00006沪市A股、 K00007深市A股|
|period|K 线 周 期|string|参考 ZZOHLCPeriod|
|type|指 标 类 型|ZZChartIndexType[]|参考 ZZChartIndexType|
|requestType|请 求 类 型|RequestType|1、默认类型为RequestTypeRecent,取最新的300根K线数据2、当 类型为RequestTypeNewer时,取date日期之后的300根K线数据3、 当类型为RequestTypeOlder时,取date日期之前的300根K线数据|
|date|日 期/ 时 间|string|获取指定日期对应的数据,与requestType配合使用1:日周月K的时 间格式为yyyyMMdd 2:分钟K的时间格式为yyyyMMddHHmmss|
|count|自 定 义 条 数|number|其值必须满足于:0 < count <= 300.不传,默认300|

###### **应答类:ZZOHLCIndexResp** 

###### 属性说明 

|**属性名**|**说明**|**型态**|**备注**|
|---|---|---|---|
|items|资料列表|ArrayList|参考: IndexItem|

###### **调用样例** 

let ohlcIndexReq = new ZZOHLCIndexReq(); 

ohlcIndexReq.type = [ZZChartIndexType.ChartIndexTypeDDX, 

ZZChartIndexType.ChartIndexTypeDDY, ZZChartIndexType.ChartIndexTypeDDZ, ZZChartIndexType.ChartIndexTypeBBD 

, ZZChartIndexType.ChartIndexTypeRatioBS, ZZChartIndexType.ChartIndexTypeLargeMoneyInflow, ZZChartIndexType.ChartIndexTypeBigMoneyInflow, ZZChartIndexType.ChartIndexTypeMidMoneyInflow 

, ZZChartIndexType.ChartIndexTypeSmallMoneyInflow] ohlcIndexReq.code = '600000.sh' ohlcIndexReq.subtype = '1001' 

ohlcIndexReq.period = ZZOHLCPeriod.OHLCPeriodDay ohlcIndexReq.requestType =  RequestType.RequestTypeRecent ohlcIndexReq.send({ onSuccess: (resp: ZZOHLCIndexResp) => { if (resp.items && resp.items.length > 0) { } }, onFail: (err: ErrorInfo) => { } }) 

##### **分价** 

**说明** 

股票交易量按价格展示,支持沪深港(不包含指数且不支持L1,仅支持L2)、期货 

###### **请求类(ZZPriceVolumeReq)** 

参数说明: 

|**属性名**|**说明**|**型态**|**备注**|
|---|---|---|---|
|code|代码|string||
|subtype|次类别|string||
|param|分页参数(不 支持期货、新 三板),不传 默认返回全量 数据|string|格式:param:n1,n2,n3; 其中:n1为价格,可取值为0; n2为条数,取值为正整数,最大100;n3取值范围0,-1,1; 当:n3=-1表示取最大价格的n2条,此时n1赋值0;n3=0 表示取比n1价格大的n2条;n3=1表示取比n1价格小的n2 条|

###### **应答类(ZZPriceVolumeResp)** 

###### 属性说明 

|**属性名**|**说明**|**型态**|**备注**|
|---|---|---|---|
|items|搜寻结果数组|SseArrayList<ZZPriceVolumeItem>|参考 ZZPriceVolumeItem|
|startIndex|起始价格|string|配合param参数使用|
|endIndex|结束价格|string|配合param参数使用|

###### **调用样例(返回全部数据)** 

let req = new ZZPriceVolumeReq() req.code = this.item.id req.subtype = this.item.subtype req.send({ 

onSuccess: (resp: ZZPriceVolumeResp) => { if (resp.items && resp.items.length > 0) { 

} }, onFail: (err: ErrorInfo) => { 

} }) 

##### **分量** 

###### **说明** 

###### 获取股票分量行情数据 

###### **请求类(ZZVolumeReq)** 

参数说明: 

|**属性名**|**说明**|**型态**|**备注**|
|---|---|---|---|
|code|标的证券券代码|string||
|subtype|次类别|string||

###### **应答类(ZZVolumeResp)** 

###### 属性说明 

|**属性名**|**说明**|**型态**|**备注**|
|---|---|---|---|
|volumes|分量表数据|string[]||
|buyVolumes|买分量表数据|string[]||
|sellVolumes|卖分量表数据|string[]||

###### **调用样例(返回全部数据)** 

```arkts
let req = new ZZVolumeReq() req.code = this.item.id req.subtype = this.item.subtype req.send({ onSuccess: (resp: VolumeResp) => { }, onFail: (err: ErrorInfo) => { } }) 
```

##### **L2plus 逐笔委托** 

**说明** 

获取股票逐笔委托行情数据 **请求类(ZZL2TickEntrustReq)** 

参数说明: 

|**属性名**|**说明**|**型态**|**备注**|
|---|---|---|---|
|code|代 码|string||
|subtype|次 类 别|string||
|pageIndex|页 码|number||
|pageSize|每 页 笔 数|number||
|type|次 类 别|string|基于页码索引请求的类别-1表示最新一页数据,0表示比pageIndex更新 的一页数据,1表示比pageIndex更旧的一页数据|
|param||string|沪深港股票 新增param参数,此参数效果等同于index,pageSize,type 参数;当param有值时,优先使用param的值,此时 index,pageSize,type三个参数的值无效 说 明:param:num1,num2,num3 1,当num3=-1时,num1为任意数字(建议 给0),num2为条数,如0,20,-1表示获取最新的20条2,当num3=0 时,num1为下标,num2为条数,如2.22373434E8,20,0,表示获取分 笔下标为2.22373434E8之后的20条3,当num3=1时,num1为下标, num2为条数,如2.22373434E8,20,1,表示获取分笔下标为 2.22373434E8之前的20条 关于上述的下标num1,为response中的 startIndex和endIndex|

###### **应答类(ZZL2TickEntrustResp)** 

###### 属性说明 

|**属性名**|**说明**|**型态**|**备注**|
|---|---|---|---|
|items|逐笔委托数据|ZZTickEntrustItem[]||
|startIndex|起始引索|string||
|endIndex|结束引索|string||

###### **调用样例** 

```arkts
let req = new ZZL2TickEntrustReq() req.code = this.item.id req.subtype = this.item.subtype req.send({ onSuccess: (resp: ZZL2TickEntrustResp) => { }, onFail: (err: ErrorInfo) => { } }) 
```

##### **L2plus 逐笔还原** 

**说明** 

获取股票逐笔还原行情数据 **请求类(ZZL2TickRestoreReq)** 

参数说明: 

|**属性名**|**说明**|**型态**|**备注**|
|---|---|---|---|
|code|代 码|string||
|subtype|次 类 别|string||
|pageIndex|页 码|number||
|pageSize|每 页 笔 数|number||
|type|次 类 别|string|基于页码索引请求的类别-1表示最新一页数据,0表示比pageIndex更新 的一页数据,1表示比pageIndex更旧的一页数据|
|param||string|沪深港股票 新增param参数,此参数效果等同于index,pageSize,type 参数;当param有值时,优先使用param的值,此时 index,pageSize,type三个参数的值无效 说 明:param:num1,num2,num3 1,当num3=-1时,num1为任意数字(建议 给0),num2为条数,如0,20,-1表示获取最新的20条2,当num3=0 时,num1为下标,num2为条数,如2.22373434E8,20,0,表示获取分 笔下标为2.22373434E8之后的20条3,当num3=1时,num1为下标, num2为条数,如2.22373434E8,20,1,表示获取分笔下标为 2.22373434E8之前的20条 关于上述的下标num1,为response中的 startIndex和endIndex|

###### **应答类(ZZL2TickRestoreResp)** 

###### 属性说明 

|**属性名**|**说明**|**型态**|**备注**|
|---|---|---|---|
|items|逐笔还原数据|ZZTickDetailItem[]||
|startIndex|起始引索|string||
|endIndex|结束引索|string||

###### **调用样例** 

let req = new ZZL2TickRestoreReq() req.code = this.item.id req.subtype = this.item.subtype req.send({ onSuccess: (resp: ZZL2TickRestoreResp) => { 

}, onFail: (err: ErrorInfo) => { } }) 

##### **港股波动调节等信息** 

###### **说明** 

###### 获取港股碎股列表,市场波动调节VCM,收市集合竞价CAS。 

###### **请求类:ZZHKStockInfoReq** 

属性说明: 

|**属性名**|**说明**|**型态**|**备注**|
|---|---|---|---|
|code|股票代码|String||
|subype|股票子分类|String||

###### **应答类:ZZHKStockInfoResp** 

属性说明 

|**属性名**|**说明**|**型态**|**备注**|
|---|---|---|---|
|item|数据信息|ZZHKStockInfoItem|请參考 ZZHKStockInfoItem|

###### **调用样例** 

ZZHKStockInfoReq req = new ZZHKStockInfoReq(); req.code = "00700.hk"; req.subtype = "1010"; req.send({ onSuccess: (resp: HKStockInfoResp) => { }, onFail: (err: ErrorInfo) => { } }) 

##### **证券行情列表** 

###### **说明** 

- 通过设置股票代码可获取该股票的行情数据,股票代码支持多笔,若异查询多行股票行情,可用逗号隔开, 例如:600000.sh,600600.sh。 

- 期货单市场限制50只股票,其他市场限制200只股票 

股票商品市场别,如下: 

- 上证:sh 

- 深证:sz 

- 北证:bz 

- 港股:hk 

中证指数:csi 

###### **请求类:ZZQuoteReq** 

参数说明: 

|**属性名**|**说明**|**型态**|**备注**|
|---|---|---|---|
|codes|股票代码数组|String[]|可传入多市场股票,券商无需分市场调用|
|quoteColumns|快照自定义栏 位|int[]|1:自定义栏位请参考 ZZQuoteCustomField2:当该参数为空时, 内部默认请求栏位:股票代码、股票名称、市场、子类别、最新 价、昨收价、昨结价、涨跌、涨跌幅、涨跌标识3:外汇不支持 自定义栏位,总是全量请求,此时参数对该市场不起作用|
|addValueColumns|增值指标自定 义栏位|int[]|1:自定义栏位请参考 ZZAddValueCustomField 2:当该参数为 空时,表示不查询,此时不返回增值指标数据5:新三板 、外汇、 期货不返回增值指标数据,此参数对该市场无效|
|useTaskPool|数据处理是否 使用子线程 (仅沪深京港 csi、gb等市 场)|boolean|true:使用子线程处理数据,false :不使用。默认true|

##### **应答类:ZZQuoteResp** 

###### 属性说明 

|**属性名**|**说明**|**型态**|**备注**|
|---|---|---|---|
|ZZQuoteItems|资料列表|SseArrayList<ZZQuoteItem>|请参考 ZZQuoteItem|
|addValueModels|增值指标模型|SseArrayList<ZZAddValueModel>|请参考 ZZAddValueModel|

###### **调用样例** 

```arkts
let quoteReq = new ZZQuoteReq(); quoteReq.codes = ['600000.sh']; quoteReq.quoteColumns = [ZZQuoteCustomField.quote_STATUS, ZZQuoteCustomField.quote_NAME] quoteReq.send({ onSuccess: (resp: ZZQuoteResp) => { if (resp.ZZQuoteItems) { this.items = resp.ZZQuoteItems; } }, onFail: (err: ErrorInfo) => { } }); 
```

##### **排序接口** 

###### **说明** 

排序接口第二个参数是拼接的,依次为页码,笔数,排序栏位,正倒序,是否显示停牌股以逗号分开,如 “0,12,1,0,1”,新三板暂不支持市盈率排序 

###### **请求类:ZZCateSortingReq** 

###### 参数说明一: 

|**方法名**|**参数名**|**说明**|**型态**|**备注**|
|---|---|---|---|---|
|send()|cateId|分类代码|string|可以带入 ZZCateType 或者直接带 入沪深指数 ID(如: 000001.sh or 000002.sh or 399001.sz ....等)|
|param|'0,12,1,0,1'|string|CateSortingReqType.CateSortingReqTypePage:其 中第一个代表页码,0表示首页 第二个代表每页数量 (建议在50条以内) CateSortingReqType.CateSortingReqTypeSection: 其中第一个代表起始条数 第二个代表结束条数(每次 请求建议在50条以内)第三个代表排序字段, 期货使 用ZZFuturesQuoteField, 其他市场使用ZZSortType 第四个代表排序顺序,1倒序,0正序 第五个代表是否 显示停牌股,0不显示,1显示||
|quoteColumns|[ZZQuoteCustomField.ID, ZZQuoteCustomField.NAME,...]|number[]|1.快照自定义栏位请参考 ZZQuoteCustomField2.如 果该参数传空,则内部默认请求栏位:代码、名称、 市场、子类别、最新价、昨收价、昨结价、涨跌、涨 跌幅3.外汇不支持自定义,会全量请求,此时参数该 市场无效||
|addValueColumns|[ZZAddValueCustomField.CODE, ...]|number[]|1.增值指标自定义栏位请参考 ZZAddValueCustomField 2.如果该参数传空,则不返 回增值指标数据3.新三板 、外汇、期货不返回增值指 标数据,此时参数该市场无效||
|type|分页/区间请求(GB分类不支持区 间请求)|CateSortingReqType|CateSortingReqType.CateSortingReqTypePage:分 页功能,按照每页多少条请求 CateSortingReqType.CateSortingReqTypeSection: 区间请求,按照从哪一条开始到哪一条的方式请求||

###### **应答类:ZZCateSortingResp** 

###### 属性说明 

|**属性名**|**说明**|**型态**|**备注**|
|---|---|---|---|
|list|资料列表|SseArrayList<ZZQuoteItem>|请参考 ZZQuoteItem|
|addValueModel|增值指标|SseArrayList<ZZAddValueModel>|请参考 ZZAddValueModel|
|totalPage|总页数|string||
|totalNumber|总条数|string||

###### **调用样例** 

```arkts
let zfbReq = new ZZCateSortingReq(); zfbReq.cateId = ZZCateType.SHSZBZ1001; zfbReq.param = "0,10,12,1,1"; zfbReq.send({ onSuccess: (resp: ZZCateSortingResp) => { callback.success(); if (resp.list) { this.zfbItems = resp.list; } }, 
```

onFail: (err: ErrorInfo) => { callback.failed(); 

} 

}); 

##### **板块类别个股列表** 

###### **说明** 

获取某一分类的成分股代码 

###### **请求类:ZZCategoryCodeReq** 

属性说明: 

|**属性名**|**说明**|**型态**|**备注**|
|---|---|---|---|
|code|分类代码|string|ZZCateType|

###### **应答类:ZZCategoryCodeResp** 

属性说明 

|**属性名**|**说明**|**型态**|**备注**|
|---|---|---|---|
|codes|代码列表|string[]|/td>|

###### **调用样例** 

ZZCategoryCodeReq req = new ZZCategoryCodeReq(); req.code = "SH1001"; req.send({ onSuccess: (resp: ZZCategoryCodeResp) => { }, onFail: (err: ErrorInfo) => { } }) 

##### **个股所属板块行情** 

###### **说明** 

个股所属板块行情:仅支持沪深京市场,其他市场报参数错误 

**请求类:ZZSectionQuoteReq** 

属性说明: 

|**属性名**|**说明**|**型态**|**备注**|
|---|---|---|---|
|code|股票 代码|string|单只股票:如600000.sh|
|type|板块|string|备注:取值范围(trade,area,notion,trade_sw,trade_sw1,notion_szyp,area_szyp,trade_szyp,trade_fz)可任意组合,逗 号分隔。 不传,默认返回Notion,Area,Trade板块|

###### **应答类:ZZSectionQuoteResp** 

###### 属性说明 

|**属性名**|**说明**|**型态**|**备注**|
|---|---|---|---|
|items|板块列表|ArrayList<ZZSectionSortingItem>|请参考 ZZSectionSortingItem|

###### **调用样例** 

let sectionQuoteReq = new ZZSectionQuoteReq() sectionQuoteReq.code = “600000.sh” sectionQuoteReq.type = 

'trade,area,notion,trade_sw,trade_sw1,notion_szyp,area_szyp,trade_szyp,trade_fz' sectionQuoteReq.send({ 

onSuccess: (resp: ZZSectionQuoteResp) => { if (resp.items && resp.items.length > 0) { 

} }, onFail: (err: ErrorInfo) => { } }) 

##### **板块排序接口** 

###### **说明** 

###### 板块排序接口 

###### **请求类:ZZSectionSortingReq** 

参数说明: 

|**参数名**|**说明**|**型态**|**备注**|
|---|---|---|---|
|code|板块分类|string|参考 ZZCategoryType|
|beginIndex|起始位置|number||
|endIndex|结束位置|number||
|ascending|排列顺序|boolean|排列顺序:true升序,false降序|
|field|排序栏位|ZZSectionSortingField|参考 ZZSectionSortingField|

###### **应答类:SectionSortingResp** 

###### 属性说明 

|**属性名**|**说明**|**型态**|**备注**|
|---|---|---|---|
|items|板块排序|ArrayList<ZZSectionSortingItem>|请参考 ZZSectionSortingItem|
|totalCount|总条数|string||

###### **调用样例** 

let req = new ZZSectionSortingReq() req.code = ZZCategoryType.CATE_TRADE req.beginIndex = 0 req.endIndex = 2 req.ascending = false req.field = ZZSectionSortingField.SectionSortingFieldAverageChange req.send({ 

onSuccess: (resp: ZZSectionSortingResp) => { if (resp.items && resp.items.length > 0) { } }, onFail: (err: ErrorInfo) => { } }) 

##### **个股所属行业板块列表** 

###### **说明** 

个股所属行业板块列表:仅支持沪深京市场,支持多只股票,最多200只 

###### **请求类:ZZSectionStockReq** 

属性说明: 

|**属性名**|**说明**|**型态**|**备注**|
|---|---|---|---|
|codes|股 票 代 码|string[]|股票:如["600000.sh"," 0000001.sz"],最多200只|
|type|板 块 类 别|枚举类型: SectionType|申万二级行业:SectionType.Trade_sw优品行业: SectionType.Trade_szyp小方行业:SectionType.Trade_fz不传默认 为申万二级行业|

**应答类:ZZSectionStockResp** 

###### 属性说明 

|**属性名**|**说明**|**型态**|**备注**|
|---|---|---|---|
|sectionStocks|板块列表|Map<string,ZZSectionItem[]>|请参考[ZZSectionItem](#板块模型(ZZSectionItem)|

###### **调用样例** 

let sectionStockReq = new ZZSectionStockReq() sectionStockReq.codes = [“600000.sh”,"0000001.sz"] sectionStockReq.send({ 

onSuccess: (resp: ZZSectionStockResp) => { if (resp.sectionStocks && resp.sectionStocks.length > 0) { 

} }, onFail: (err: ErrorInfo) => { } }) 

##### **AB股列表行情** 

###### **说明** 

###### 获取所有AB股列表数据 

###### **请求类(ZZABListReq)** 

###### 参数说明 

|**参数名**|**说明**|**型态**|**备注**|
|---|---|---|---|
|pageIndex|页码|string||
|pageSize|每页条数|number||
|field|排序字段|ABListField||
|ascending|排序|boolean|备注|

###### **应答类(ZZABListResp)** 

属性说明 

|**属性名**|**说明**|**型态**|**备注**|
|---|---|---|---|
|items|数据列表|ZZABListItem[]||
|numberOfPages|总页数|string||
|totalNumber|总条数|string||

###### **调用样例** 

ZZABListReq req = new ZZABListReq(); req.pageIndex = 0; req.pageSize = 20; req.field = ABListField.ABListFieldChangeRateA; req.ascending = false; req.send({ onSuccess: (resp: ZZABListResp) => { 

}, onFail: (err: ErrorInfo) => { } }) 

###### **AB股列表排序枚举ZZABListField** 

|**枚举类型**|**数值**|**说明**|
|---|---|---|
|ABListFieldCodeA|0||
|ABListFieldNameA|1||
|ABListFieldLastPriceA|3||
|ABListFieldChangeRateA|4||
|ABListFieldCodeB|6||
|ABListFieldNameB|7||
|ABListFieldLastPriceB|9||
|ABListFieldChangeRateB|10||
|ABListFieldPremiumRateAB|12||
|ABListFieldPremiumRateBA|13||

##### **AH股列表行情** 

**说明** 

获取所有AH股列表数据 

###### **请求类(ZZAHListReq)** 

参数说明 

|**参数名**|**说明**|**型态**|**备注**|
|---|---|---|---|
|pageIndex|页码|number||
|pageSize|每页条数|number||
|field|排序字段|AHListField||
|ascending|排序|boolean|备注|

###### **应答类(ZZAHListResp)** 

###### 属性说明 

|**属性名**|**说明**|**型态**|**备注**|
|---|---|---|---|
|items|数据列表|ZZAHListItem[]||
|numberOfPages|总页数|string||
|totalNumber|总条数|string||

###### **调用样例** 

ZZAHListReq req = new ZZAHListReq(); req.pageIndex = 0; req.pageSize = 20; req.field = AHListField.AHListFieldChangeRateA; req.ascending = false; req.send({ onSuccess: (resp: ZZAHListResp) => { }, onFail: (err: ErrorInfo) => { } }) 

###### **AH股列表排序枚举ZZAHListField** 

|**枚举类型**|**数值**|**说明**|
|---|---|---|
|AHListFieldLastPriceA|2||
|AHListFieldChangeRateA|3||
|AHListFieldLastPriceH|6||
|AHListFieldChangeRateH|7||
|AHListFieldPremiumRate|9||

##### **CDR/GDR联动列表行情** 

###### **说明** 

###### CDR/GDR联动列表数据 

###### **请求类(ZZDRListReq)** 

###### 参数说明 

|**参数名**|**说明**|**型态**|**备注**|
|---|---|---|---|
|code|股票代码|string|传cdr或gdr|
|pageIndex|页码|number||
|pageSize|每页条数|number||
|field|排序字段|ZZDRListField||
|ascending|排序|boolean|备注|

###### **应答类(ZZDRListResp)** 

###### 属性说明 

|**属性名**|**说明**|**型态**|**备注**|
|---|---|---|---|
|items|数据列表|ZZDRListItem[]||
|numberOfPages|总页数|string||

###### **调用样例** 

ZZDRListReq req = new ZZDRListReq(); req.pageIndex = 0; req.pageSize = 20; req.field = ZZDRListField.DRListFieldChangeRate; req.ascending = false; req.send({ onSuccess: (resp: ZZDRListResp) => { 

}, 

onFail: (err: ErrorInfo) => { 

} }) 

###### **CDR/GDR股列表排序枚举ZZDRListField** 

|**枚举类型**|**数值**|**说明**|
|---|---|---|
|DRListFieldCode|0||
|DRListFieldName|1||
|DRListFieldLastPrice|3||
|DRListFieldPreClosePrice|4||
|DRListFieldChangeRate|5||
|DRListFieldDatetime|6||
|DRListFieldBaseStockCode|7||
|DRListFieldBaseStockName|8||
|DRListFieldBaseLastPrice|10||
|DRListFieldBasePreClosePrice|11||
|DRListFieldBaseChangeRate|12||
|DRListFieldBaseDatetime|13||
|DRListFieldPremiumRate|14||

##### **可转债联动股列表行情** 

**说明** 

###### 可转债列表数据 

###### **请求类(ZZKZZListReq)** 

参数说明 

|**参数名**|**说明**|**型态**|**备注**|
|---|---|---|---|
|pageIndex|页码|string||
|pageSize|每页条数|number||
|field|排序字段|ZZKZZListField||
|ascending|排序|boolean|备注|

###### **应答类(ZZKZZListResp)** 

属性说明 

|**属性名**|**说明**|**型态**|**备注**|
|---|---|---|---|
|items|数据列表|ZZKZZListItem[]||
|numberOfPages|总页数|string||

###### **调用样例** 

ZZKZZListReq req = new ZZKZZListReq(); req.pageIndex = 0; req.pageSize = 20; req.field = ZZKZZListField.KZZListFieldChangeRateKZZ; req.ascending = false; req.send({ onSuccess: (resp: ZZKZZListResp) => { }, onFail: (err: ErrorInfo) => { } }) 

###### **可转债联动股列表排序枚举ZZKZZListField** 

|**枚举类型**|**数值**|**说明**|
|---|---|---|
|KZZListFieldChangeRateKZZ|4||
|KZZListFieldChangeRateZG|11||
|KZZListFieldPremiumRate|14||
|KZZListFieldConversionPrice|15||
|KZZListFieldConversionValue|16||
|KZZListFieldBackPrice|17||
|KZZListFieldEansomPrice|18||
|KZZListFieldExpirePrice|19||

##### **次新债列表行情** 

###### **说明** 

###### 获取所有次新债 

###### **请求类(ZZSubnewBondReq)** 

###### 参数说明 

|**参数名**|**说明**|**型态**|**备注**|
|---|---|---|---|
|pageIndex|页码|number||
|pageSize|每页条数|number||
|field|排序字段|ZZSubnewBondField||
|ascending|排序|boolean|备注|
|**类(ZZSubnewDond属性名** 属性说明|**Resp)说明**|**型态**|**备注**|
|items|数据列表|ZZSubnewBondItem[]||

###### **应答类(ZZSubnewDondResp)** 

###### **调用样例** 

ZZSubnewBondReq req = new ZZSubnewBondReq(); req.pageIndex = 0; req.pageSize = 20; 

req.field = ZZSubnewBondField.SubnewBondFieldLastPrice; req.ascending = false; 

req.send({ onSuccess: (resp: ZZSubnewDondResp) => { }, onFail: (err: ErrorInfo) => { 

} }) 

###### **次新债列表排序枚举ZZSubnewBondField** 

|**枚举类型**|**数值**|**说明**|
|---|---|---|
|SubnewBondFieldCode|0||
|SubnewBondFieldIPOPrice|2||
|SubnewBondFieldLastPrice|3||
|SubnewBondFieldIPODate|4||
|SubnewBondFieldPreClosePrice|6||
|SubnewBondFieldTotalRate|7||
|SubnewBondFieldChange|8||
|SubnewBondFieldTurnoverRate|9||
|SubnewBondFieldAmount|10||
|SubnewBondFieldCapitalInflow|11||
|SubnewBondFieldPE|12||
|SubnewBondFieldTotalValue|13||
|SubnewBondFieldFlowValue|14||

##### **次新股** 

**说明** 

获取所有次新股 

###### **请求类(ZZSubnewStockReq)** 

参数说明 

|**参数名**|**说明**|**型态**|**备注**|
|---|---|---|---|
|pageIndex|页码|number||
|pageSize|每页条数|number||
|field|排序字段|ZZSubnewStockField||
|ascending|排序|boolean|备注|

###### **应答类(ZZSubnewStockResp)** 

属性说明 

|**属性名**|**说明**|**型态**|**备注**|
|---|---|---|---|
|items|数据列表|ZZSubnewStockItem[]||

###### **调用样例** 

ZZSubnewStockReq req = new ZZSubnewStockReq(); req.pageIndex = 0; req.pageSize = 20; req.field = ZZSubnewStockField.SubnewStockFieldLastPrice; req.ascending = false; req.send({ onSuccess: (resp: ZZSubnewStockResp) => { }, onFail: (err: ErrorInfo) => { } }) 

###### **次新股列表排序枚举ZZSubnewStockField** 

|**枚举类型**|**数值**|**说明**|
|---|---|---|
|SubnewStockFieldCode|0|股票代码|
|SubnewStockFieldIPOPrice|2|发行价|
|SubnewStockFieldLastPrice|3|最新价|
|SubnewStockFieldIPODate|4|发行日期|
|SubnewStockFieldContinuousLimitUpDays|5|连续涨停天数|
|SubnewStockFieldPreClosePrice|7|昨收价|
|SubnewStockFieldTotalRate|8|累计涨跌幅|
|SubnewStockFieldChange|9|涨跌幅|
|SubnewStockFieldTurnoverRate|10|换手率|
|SubnewStockFieldAmount|11|成交额|
|SubnewStockFieldCapitalInflow|12|主力资金流入|
|SubnewStockFieldPE|13|动态市盈率|
|SubnewStockFieldTotalValue|14|总市值|
|SubnewStockFieldFlowValue|15|流通股本|

##### **实时涨停行情统计接口** 

###### **说明** 

###### 获取所有涨停统计行情 

###### **请求类(ZZZTSortingReq)** 

###### 属性说明 

|**属性名**|**说明**|**型态**|**备注**|
|---|---|---|---|
|pageIndex|页码|number||
|pageSize|每页条数|number||
|field|排序栏位|string|0按时间排序,6按最新价排序,7涨跌幅排序|
|ascending|是否升序|boolean||
|ZTType|涨停类型|string|0所有涨停,1一字涨停,2自然涨停|

###### **应答类(ZZZTSortingResp)** 

属性说明 

|**属性名**|**说明**|**型态**|**备注**|
|---|---|---|---|
|items||ZZZTSortingItem[]||

###### **调用样例** 

let ZZZTSortingReq = new ZZZTSortingReq() amountReq.send({ 

onSuccess: (resp: ZZZTSortingResp) => { 

}, onFail: (err: ErrorInfo) => { 

} }); 

##### **可转债静态信息接口** 

###### **说明** 

###### 根据可转债代码查询可转债静态信息接口 

###### **请求类(ZZKZZInfoReq)** 

|属性说明||||
|---|---|---|---|
|**属性名**|**说明**|**型态**|**备注**|
|code|可转债代码|string||

###### **应答类(ZZKZZInfoResp)** 

###### 属性说明 

|**属性名**|**说明**|**型态**|**备注**|
|---|---|---|---|
|item|可转债静态信息|ZZKZZInfoItem||

**调用样例** 

```arkts
let req = new ZZKZZInfoReq(); req.code = "128143.sz"; req.send({ onSuccess: (resp: ZZKZZInfoResp) => { 
```

}, onFail: (err: ErrorInfo) => { } }) 

##### **- 期权 标的行情** 

###### **说明** 

###### 获得期权标的证券列表 

###### **请求类(ZZUnderlyingStockReq)** 

属性说明 

|**属性名**|**说明**|**型态**|**备注**|
|---|---|---|---|
|market|市 场|string|传入"sz"则获取深圳市场标的列表,传入"sh,sz"获取上海和深圳市场标的 列表,不传或者传入"sh"则获取上海市场标的列表|

###### **应答类(ZZUnderlyingStockResp)** 

属性说明 

|**属性名**|**说明**|**型态**|**备注**|
|---|---|---|---|
|ZZQuoteItems|资料列表|ArrayList<ZZQuoteItem>|请参考 ZZQuoteItem|

###### **调用样例** 

```arkts
let optionListRequest = new ZZUnderlyingStockReq(); optionListRequest.market = 'sh,sz' optionListRequest.send({ onSuccess: (resp: ZZUnderlyingStockResp) => { 
```

if (resp.ZZQuoteItems && resp.ZZQuoteItems.length > 0) { } }, onFail: (err: ErrorInfo) => { } }) 

##### **- 期权 交割月** 

##### **说明** 

获得期权交割月列表 

##### **请求类(ZZExpireMonthReq)** 

参数说明: 

**属性名 说明 型态 备注** code 标的证券代码 string 

##### **应答类(ZZExpireMonthResp)** 

属性说明 

**属性名 说明 型态 备注** expireMonths 资料列表 ArrayList<ExpireMonthItem> 参考ExpireMonthItem 

##### **调用样例** 

```arkts
let optionExpireReq = new ZZExpireMonthReq(); optionExpireReq.code = '510050.sh' optionExpireReq.send({ onSuccess: (resp: ZZExpireMonthResp) => { if (resp.expireMonths && resp.expireMonths.length > 0) { } }, onFail: (err: ErrorInfo) => { } }) 
```

##### **期权-T型报价** 

##### **说明** 

获得期权T型报价列表 

##### **请求类(ZZOptionTReq)** 

属性说明: 

|**属性名**|**说明**|**型态**|**备注**|
|---|---|---|---|
|code|标的 证券 代码|string||
|expireMonth|交割 年月|string|格式如下: 不带字母(2001),返回2001所有期权 带字母 M(2001M),返回2001未调整的期权 带字母A(2001A),返回2001 调整的期权|

##### **应答类(ZZOptionResp)** 

###### 属性说明 

|**属性名**|**说明**|**型态**|**备注**|
|---|---|---|---|
|optionTList|资 料 列 表|Map<String, string|ZZQuoteItem|undefined> []|Map中key/value介绍"put":认沽(数据类型:ZZQuoteItem)"call": 认购(数据类型:ZZQuoteItem)"exePrice":行权价(数据类 型:string)|
|stockQuote|标 的 证 券|ZZQuoteItem|请参考 ZZQuoteItem|

##### **调用样例** 

```arkts
let optionTQuoteReq = new ZZOptionTReq(); optionTQuoteReq.code = '510050.sh' optionTQuoteReq.expireMonth = '2312A' optionTQuoteReq.send({ onSuccess: (resp: ZZOptionResp) => { if (resp.optionTList && resp.optionTList.length > 0) { } }, onFail: (err: ErrorInfo) => { } }) 
```

##### **- 期权 商品行情** 

##### **说明** 

获得期权报价列表 

##### **请求类(ZZOptionReq)** 

###### 属性说明: 

|**属性名**|**说明**|**型态**|**备注**|
|---|---|---|---|
|code|标的证券代 码|string||
|pageIndex|页次|number||
|optionType|期权类型(认 沽/认购)|OptionType|1、OptionType.OptionTypeUnknown:全部2、 OptionType.OptionTypeCall:认购3、OptionType.OptionTypePut:认沽|

##### **应答类(ZZOptionResp)** 

###### 属性说明 

|**属性名**|**说明**|**型态**|**备注**|
|---|---|---|---|
|ZZQuoteItems|资料列表|SseArrayList<ZZQuoteItem>|请参考 ZZQuoteItem|
|totalPage|总页数|string||
|totalNumber|总条数|string||

##### **调用样例** 

let optionQuoteReq = new ZZOptionReq(); optionQuoteReq.code     ='510050.sh' optionQuoteReq.optionType = OptionType.OptionTypeCall optionQuoteReq.pageIndex = 0 optionQuoteReq.send({ 

onSuccess: (resp: ZZOptionResp) => { 

if (resp.ZZQuoteItems && resp.ZZQuoteItems.length > 0) { } }, onFail: (err: ErrorInfo) => { } }) 

##### **历史分时** 

##### **说明** 

根据某个日期获取历史分时,注:港股不支持获取当天的历史分时,沪深京港当日数据不完整,建议用当日 分时替代,沪深支持近一年 其它市场支持近两个月 

##### **请求类(ZZHistoryChartReq)** 

参数说明:传入单只股票代码 

|**属性名**|**说明**|**型态**|**备注**|
|---|---|---|---|
|code|股票代码|String||
|subtype|次类别|string||
|date|日期|String|格式:yyyymmdd如20181105|

##### **应答类(ZZHistoryZZChartResp)** 

属性说明 

|**属性名**|**说明**|**型态**|**备注**|
|---|---|---|---|
|OHLCItems|资料列表|ArrayList<OHLCItems>|请參考 ZZOHLCItem|
|timezone|交易时间段|string[][]||
|tickCount|总点数|number||

##### **调用样例** 

let req = new HistoryChartReq() req.code = this.ZZQuoteItem.id req.subtype = this.ZZQuoteItem.subtype req.date = this.queryOhlcItem.datetime req.send({ 

onSuccess: (resp: ZZHistoryZZChartResp) => { if (resp.OHLCItems && resp.OHLCItems.length > 0) { 

} }, onFail: (err: ErrorInfo) => { } }) 

##### **UK市场行情快照** 

##### **说明** 

获取UK市场快照行情 

##### **请求类:ZZUKQuoteReq** 

参数说明: 

|**参数名**|**说明**|**型态**|**备注**|
|---|---|---|---|
|code|股票代码|string||

##### **应答类:ZZUKQuoteResp** 

###### 属性说明 

|**属性名**|**说明**|**型态**|**备注**|
|---|---|---|---|
|items||ZZUKItem[]||

##### **调用样例** 

```arkts
let req = new ZZUKQuoteReq(); req.code = ' PRM.uk' req.send({ onSuccess: (resp: UKQuoteResp) => { }, onFail: (err: ErrorInfo) => { } }); 
```

##### **AH联动请求** 

##### **说明** 

AH联动请求 

##### **请求类:ZZAHLinkReq** 

方法说明: 

|**参数名**|**说明**|**型态**|**备注**|
|---|---|---|---|
|code|股票代码|string||

##### **应答类:AHLinkResp** 

属性说明 

|**属性名**|**说明**|**型态**|**备注**|
|---|---|---|---|
|items|联动数据|ZZAHLinkItem||

##### **调用样例** 

```arkts
let request= new ZZAHLinkReq(); request.code = "002490.sz"; request.send({ onSuccess: (resp: Response) => { }, onFail: (err) => { } }); 
```

##### **可转债溢价查询(根据可转债代码或正股代码)** 

##### **说明** 

可转债溢价查询(根据可转债代码或正股代码) 

##### **请求类:ZZKZZLinkReq** 

方法说明: 

|**参数名**|**说明**|**型态**|**备注**|
|---|---|---|---|
|code|股票代码|string||

##### **应答类:ZZKZZLinkResp** 

属性说明 

|**属性名**|**说明**|**型态**|**备注**|
|---|---|---|---|
|items||ArrayList<ZZKZZLinkItem>|ZZKZZLinkItem|

##### **调用样例** 

```arkts
let request= new ZZKZZLinkReq(); request.code = "300121.sz"; request.send({ onSuccess: (resp: ZZKZZLinkResp) => { }, onFail: (err) => { } }); 
```

##### **GDR\CDR联动** 

##### **说明** 

GDR\CDR联动,通过股票代码获取联动行情 

##### **请求类:ZZDRLinkReq** 

方法说明: 

|**参数名**|**说明**|**型态**|**备注**|
|---|---|---|---|
|code|股票代码|string||

##### **应答类:ZZDRLinkResp** 

|属性说明||||
|---|---|---|---|
|**属性名**|**说明**|**型态**|**备注**|
|item|联动数据|ZZDRLinkItem||

##### **调用样例** 

```arkts
let request= new ZZDRLinkReq(); request.code = "600900.sh"; request.send({ onSuccess: (resp: ZZDRLinkResp) => { }, onFail: (err) => { } }); 
```

##### **AB股联动** 

##### **说明** 

AB股联动,通过股票代码获取联动股票行情 

##### **请求类:ZZABLinkReq** 

方法说明: 

|**参数名**|**说明**|**型态**|**备注**|
|---|---|---|---|
|code|股票代码|string||

##### **应答类:ZZABLinkResp** 

属性说明 

|**属性名**|**说明**|**型态**|**备注**|
|---|---|---|---|
|items|联动数据|ZZABLinkItem||

##### **调用样例** 

```arkts
let request= new ZZABLinkReq(); request.code = "600610.sh"; request.send({ onSuccess: (resp: ZZABLinkResp) => { }, onFail: (err) => { } }); 
```

##### **涨跌分布请求接口** 

##### **说明** 

适用市场:全部/沪市/深市/创业 

##### **请求类:ZZCompoundUpdownsReq** 

参数说明: 

|**参数名**|**说明**|**型态**|**备注**|
|---|---|---|---|
|code|市 场|string|备注:市场 必传 如:sh(沪市),sz(深市),cy(创业板),bz(京市),all(全市场)只支持单市 场|
|time|时 间|string|当日; time不传或传当天之前的时间返回当天数据time="yyyyMMddHHmm"传入 当天某个时间点,返回这个时间点之后的数据(包含当前时间)近30日; time不传返回 近30日time="yyyyMMdd"传入近30天某个日期,返回该日期对应的数据|
|type|日 期 类 型|ZZCompoundUpdownsType|备注:此参数指获取当天的还是近30天的,传值请參考 ZZCompoundUpdownsType|

##### **应答类:ZZCompoundUpdownsResp** 

###### 属性说明 

|**属性名**|**说明**|**型态**|**备注**|
|---|---|---|---|
|items|涨跌分布数据列表|ArrayList< ZZUpdownsItem>||

##### **调用样例一(获取当某个时间的涨跌分布数据)** 

let req = new ZZCompoundUpdownsReq() req.code = 'all' req.type = ZZCompoundUpdownsType.CompoundUpdownsTypeOneDay req.send({ 

onSuccess: (resp: ZZCompoundUpdownsResp) => { 

if (resp && resp.items && resp.items.length > 0) { 

} }, onFail: (err: ErrorInfo) => { 

} }) 

##### **市场总览** 

##### **说明** 

###### 市场市场、挂牌量总览 

##### **请求类:ZZMarketOverviewReq** 

参数说明: 

|**参数名**|**说明**|**型态**|**备注**|
|---|---|---|---|
|无||||

##### **应答类:ZZMarketOverviewResp** 

属性说明 

|**属性名**|**说明**|**型态**|**备注**|
|---|---|---|---|
|items|资料列表|ZZMarketOverviewItem[]||

##### **调用样例** 

ZZMarketOverviewReq req = new ZZMarketOverviewReq(); req.send({ 

onSuccess: (resp: ZZMarketOverviewResp) => { 

}, onFail: (err: ErrorInfo) => { 

} }) 

##### **新股日历** 

##### **说明** 

新股(债)上市日期信息请求类 

##### **请求类:ZZIPODateReq** 

参数说明: 

|**参数名**|**说明**|**型态**|**备注**|
|---|---|---|---|
|type|IPO类型|ZZIPOType||
|**类:ZZIPODat属性名** 属性说明|**eResp说明**|**型态**|**备注**|
|items|资料列表|object[]|属性说明|

##### **应答类:ZZIPODateResp** 

##### **调用样例** 

ZZIPODateReq req = new ZZIPODateReq(); req.type = ZZIPOType.IPOTypeSHSZ req.send({ onSuccess: (resp: ZZIPODateResp) => { }, onFail: (err: ErrorInfo) => { } }) 

##### **某日的所有新股(债)信息** 

##### **说明** 

获取某日的所有新股(债)信息 

##### **请求类:ZZIPOCalendarReq** 

参数说明: 

|**参数名**|**说明**|**型态**|**备注**|
|---|---|---|---|
|date|查询日期YYYY-MM-DD|string||
|type|IPO类型|ZZIPOType||

##### **应答类:ZZIPOCalendarResp** 

属性说明 

|**属性名**|**说明**|**型态**|**备注**|
|---|---|---|---|
|item|资料列表|object|某日新股(债)信息属性说明|

##### **调用样例** 

IPOCalendarReq req = new IPOCalendarReq(); req.date = "2023-03-25" req.send({ onSuccess: (resp: ZZIPOCalendarResp) => { 

}, onFail: (err: ErrorInfo) => { } }) 

##### **新股(债)详情** 

##### **说明** 

###### 获取新股(债)详细信息 

##### **请求类:ZZIPODetailReq** 

参数说明: 

|**参数名**|**说明**|**型态**|**备注**|
|---|---|---|---|
|code|股票代码|string||

##### **应答类:ZZIPODetailResp** 

属性说明 

|**属性名**|**说明**|**型态**|**备注**|
|---|---|---|---|
|item|资料列表|object|新股(债)IPO详情属性说明|

##### **调用样例** 

ZZIPODetailReq req = new ZZIPODetailReq(); req.code = "301587.sz" req.send({ onSuccess: (resp: ZZIPODetailResp) => { }, onFail: (err: ErrorInfo) => { } }) 

##### **股票查询:在线搜索** 

##### **说明** 

###### 只支持在线搜索 

通过设置搜寻字串(keyword)可获得相关股票列表,搜寻字串可以是代码、股名或拼音字串。 

##### **请求类:ZZSearchReqV2** 

###### 参数说明: 

|**参数名**|**说明**|**类型**|**备注**|
|---|---|---|---|
|keyword|搜 索 关 键 字|string|(代码、首拼、名称,不能带市场后缀)|
|categories|市 场/ 分 类|string[]|可传空,根据需求决定是否需要传入该值。1,支持市场组合,如: ["sh","hk"] 2,支持分类代码组合,如: ["SH1001","SZ1001"] 3, 支持不同市场、分类代码混合组合,如: ["sz","SH1001"] 4,不支 持同市场、分类代码混合组合,如: ["sh","SH1001"]支持的分类 代码如下: HK1010(港股主板)SH1001(沪A),SZ1001 (深A),SH1006(沪科),SH1005(沪主),SZ1005(深 主),SZ1004(创业板),BZ1001(北证A)SH1002(沪B 股),SZ1002(深B股)SH1100(沪基金不包含Reits), SZ1100(深基),SH1150(沪Reits),SZ1150(深Reits), SH1110(沪LOF),SZ1110(深LOF),SH1120(沪ETF), SZ1120(深ETF),SH1140(沪封闭式基金),SZ1140(深封 闭式基金),SHSZ1150(沪深Reits)SH1300(沪债), SZ1300(深债),BZ1300(北证债券),SH1311(沪国 债),SZ1311(深国债),SH1312(沪可转债),SZ1312 (深可转债),BZ1312(北证可转债)HKHGT(沪股通), HKSGT(深股通)SH1400(沪指),SZ1400(深指), BZ1400(北证指数)SH1011(沪当日申购),SH1012(沪配|

|||股),SZ1011(深当日申购),SZ1012(深配股)SH9001, SH9002,SZ9001,SZ9002(行情下发非交易代码), BKA1(证监会行业一级),BKA2(证监会行业二级),BKD1(申万行 业一级),BKD2(申万行业二级) BKE0(概念),BKF1(地区), BKH1(优品行业),BKI1(优品地区),BKJ1(优品概念)支持的市场 如下:sh,sz,hk,csi,bz,bj,cff,ine,shfe,dce,gb, czce, bk, shbh, szbh|
|---|---|---|
|limit 限 制 条 数|number|必须大于0,最多400条,大于400则按400条返回|
|是 否|||
|returnRenamed 返 回 曾 用|boolean|默认false:不返回|
|名|||
|是 否|||
|returnDelisted 返 回 退 市 股|boolean|默认false:不返回|
|票|||
|**答类(ZZSearchResp)属性名说明** 属性说明|**型态**|**备注**|
|items 资料列表|Array|List<SearchItem> 请参考 ZZSearchItem|

##### **应答类(ZZSearchResp)** 

##### **调用样例** 

```arkts
let request: ZZSearchReqV2 = new ZZSearchReqV2() // new SearchReqV2 request.keyword = '600' request.categories = ["SH1001","SZ1001"] request.limit = 20 // request.searchLocal = true; request.return Renamed = false request.return Delisted = true request.send({ onSuccess: (resp: ZZSearchResp) => { 
```

if (resp.items!) { this.items = resp.items.convertToArray() } }, onFail: (err) => { console.info("SearchReq onFail:" + err.getMsg(\)); } }); 

##### **沪深京当日涨跌统计数据** 

##### **说明** 

沪深京当日涨跌统计数据 

##### **请求类:ZZMarketUpdownsReq** 

参数说明: 无 

##### **应答类:ZZMarketUpdownsResp** 

###### 属性说明 

|**属性名**|**说明**|**型态**|**备注**|
|---|---|---|---|
|datetime|时间|string||
|advanceCount|上涨 家数|string||
|declineCount|下跌 家数|string||
|equalCount|平盘 家数|string||
|limitUpCount|涨停 家数|string||
|limitDownCount|跌停 家数|string||
|preDatetime|昨日 统计 时间|string||
|preAdvanceCount|昨日 上涨 家数|string||

|preDeclineCount|昨日 下跌 家数|string||
|---|---|---|---|
|preEqualCount|昨日 平盘 家数|string||
|preLimitUpCount|昨日 涨停 家数|string||
|preLimitDownCount|昨日 跌停 家数|string||
||五日|||
|fiveAverageLimitCount|平均 涨停 家数|string||
|riseFallRange|区间 涨跌 家数|string[]|0到20依次表示(-∞,-9),[-9,-8),[-8,-7),[-7,-6),[-6,-5), [-5,-4),[-4,-3),[-3,-2),[-2,-1),[-1,0),[0],(0,1],(1,2],(2,3], (3,4],(4,5],(5,6],(6,7],(7,8],(8,9],(9,+∞]区间的数量|

##### **调用样例** 

```arkts
let req = new ZZMarketUpdownsReq() req.send({ onSuccess: (resp: ZZMarketUpdownsResp) => { if (resp) { this.marketUpdownsResp = resp } }, onFail: (err: ErrorInfo) => { } }) 
```

### **数据模型** 

##### **市场资讯(ZZMarketinfoItem)** 

|**属性名**|**说明**|**型态**|**备注**|
|---|---|---|---|
|key|类型|string||
|market|市场别|string|比如:sh|
|subType|次类别|string|比如:SH1001|
|driftLen|小数化整的倍数标记值(私用)|number|1.300化13或者1300后, driftLen标 记为3|
|suffixRetainLen|小数点后的规格长度|number||
|timezone|市场开收时间|string[] []||
|afterTrading|盘后交易时间段(科创板/深交所创 业板)|string[] []||
|callAuction|集合竞价时间段(沪深市场)|string[] []||
|unit|量转手计算的媒介值(私用)|number|手=量/unit|

##### **AH股列表(ZZAHZZQuoteItem)** 

|**属性名**|**说明**|**型态**|**备注**|
|---|---|---|---|
|name|名称|String||
|codeA|A股代码|String||
|lastPriceA|A股最新价|String||
|preClosePriceA|A股昨收价|String||
|datetimeA|A股行情时间|String||
|codeH|H股代码|String||
|nameH|H股名称|String||
|lastPriceH|H股最新价|String||
|preClosePriceH|H股昨收|String||
|datetimeH|H股行情时间|String||
|premiumAH|AH股溢价率|String||
|premiumHA|HA溢价率|String||
|changeRateA|A股涨跌幅|String||
|changeRateH|H股涨跌幅|String||

##### **股票模型(ZZQuoteItem)** 

**属性名 说明 型态 备注** 为两个字元组合(股票状态+交易状态)。 第一个字元(股票 状态): 正常交易=0 停牌=1 (此停牌状态通常发生在新股盘 中涨跌过大时) 停牌=2 (此停牌状态为开市前即知道此商品 为全天停牌) 退市=3 第二个字元(交易状态): 未开市=0 盘 前集合竞价=1 收盘集合竞价=2 连续竞价=3 临时停市=4 (无实际意义) 已收盘=5 休市=6 交易中=7(已停用) 盘 后交易=8 波动性中断=9(原揭示为停牌) 范例(目前几种 状态): 00 -->正常交易(0)与未开市(0):未开市 01 -->正 常交易(0)盘前集合竞价(1)开盘前集合竞价 02 -->正常交 status 股票状态 String 易(0)收盘集合竞价(2):收盘集合竞价 03 -->正常交易(0) 连续竞价(3):连续竞价 05 -->正常交易(0)已收盘 (5):收盘 06 -->正常交易(0)休市(6):休市 08 -->正常 交易(0)盘后交易(8):盘后交易, 当交易进入盘后交易, 状态为08,最后收盘恢复为05 20 -->停牌(2)与未开市 (0):停牌 10 -->停牌(1)与未开市(0):停牌暂停交易 30 -->退市(3)与未开市(0):已退市 备注说明: sh,sz,hk 市场状态通过获取交易所转发行情提供 bz,bj等市场该字段 由服务端控制有风险,不建议使用 id 代码 String name 名称 String datetime 交易时间 String market 市场别 String subtype 次类别 String 

|lastPrice|最新价|String||
|---|---|---|---|
|highPrice|最高价|String||
|lowPrice|最低价|String||
|openPrice|今开价|String||
|preClosePrice|昨收价|String||
|changeRate|涨跌比率|String|不带正负号,涨跌参考upDownFlag|
|volume|总量|String||
|nowVolume|当前成交量|String||
|turnoverRate|换手率|String|期货无值|
|upDownLimitType|涨跌幅限制类 型|String|‘N’表示交易规则(2013修订版)3.4.13规定的有涨跌幅限 制类型或者权证管理办法第22条规定‘R’表示交易规则 (2013修订版)3.4.15和3.4.16规定的无涨跌幅限制类型 ‘S’表示回购涨跌幅控制类型‘F’表示基于参考价格的涨跌幅控 制‘P’表示IPO上市首日的涨跌幅控制类型‘U’表示无任何价 格涨跌幅控制类型“F114”表示科创板ETF “F220”表示科创板 相关LOF注:按照业务方说明,科创板ETF、科创板LOF涨 跌限制20%|
||||注:其中深股商品如果回"1000000000.00"表示无涨停价格 限制;其他股票如返回"",表示无涨停价格限制 对于N类型 涨跌幅限制的产品,该字段当日不会更改,基于前收盘价 (已首日上市交易产品为发行价)计算。 对于R类型无涨跌 |
|limitUP|涨停价|String|幅限制的产品,该字段取开盘时基于参考价格计算的上限价 格,无实际控制意义。 对于P类型IPO上市首日产品,取连 续竞价期间基于参考价格计算最大范围的上限价格,针对科 创板产品,无实际控制意义。 新三板市场:对于要约业务, 存放其收购/回购价格。对于发行业务,如果交易状态为I-询 价,存放询价价格区间上限,如果交易状态为F-申购,存放 申购价格上限|
|limitDown|跌停价|String|注:其中深股商品如果回价格档位(如对于股票现货集中竞 价业务为1,经SDK处理之后送出值为0.01或者0.001具体 值由subtype决定)表示无跌停价格限制;其他股票如返 回"",表示无跌停价格限制 新三板市场:对于要约业务,存 放其收购/回购价格。对于发行业务,如果交易状态为I-询 价,存放询价价格区间下限,如果交易状态为F-申购,存放 申购价格下限|
|averageValue|均价|String||
|change|涨跌|String|涨跌带正负号|
|amount|成交金额|String||
|volumeRatio|量比|String|期货无值|
|buyPrice|买一价|String|期货无值|
|sellPrice|卖一价|String|期货无值|
|buyVolume|外盘量|String||
|sellVolume|内盘量|String||
|totalValue|总值|String|期货无值|
|HKTotalValue|总值|String|只有港股有值H股市值=H股股本*最新价|
|flowValue|流值|String|期货无值|
|netAsset|净资产|String|期货无值|
|pe|PE(市盈)|String|期货无值|
|pe2|静态市盈率|String|期货无值|
|pb|PB(市净率)|String|期货无值|
|capitalization|总股本|String|期货无值 单位:股 新三板市场:对于要约回购,该字段存放 本次要约收购/回购数量|

|circulatingShares|流通股|String|期货无值 单位:股|
|---|---|---|---|
|buyPrices|五档/十档 买价|SseArrayList<string>|undefined>|
|buySingleVolumes|五档/十档 委托 总笔数(买)|SseArrayList<string>|在lv2下显示十档,在lvl下显示5档 (委托总笔数(买)) 期货无值|
|buyVolumes|五档/十档 买量|SseArrayList<string | undefined>|在lv2下显示十档,在lvl下显示5档 买一下标为(size-1)|
|sellPrices|五档/十档 卖价|SseArrayList<string | undefined>|在lv2下显示十档,在lvl下显示5档 卖一下标为0|
|sellSingleVolumes|五档/十档 委托 总笔数(卖)|SseArrayList<string>|在lv2下显示十档,在lvl下显示5档 (委托总笔数(卖)) 期货无值|
|sellVolumes|五档/十档 卖量|SseArrayList<string | undefined>|在lv2下显示十档,在lvl下显示5档 卖一下标为0|
|amplitudeRate|振幅比率|String||
|receipts|收益|String|期货无值|
|upCount|上涨家数|String|沪深指数及板块指数|
|sameCount|平盘家数|String|沪深指数及板块指数|
|downCount|下跌家数|String|沪深指数及板块指数|
|optionType|期权类型|String|只有期权,才有值,认沽:P认购:C(P、C大写)|
|contractID|合约代码|String|只有期权才有值|
|objectID|标的证券代码|String|只有期权才有值|
|stockSymbol|标的证券简称|String|只有期权才有值|
|stockType|标的证券类型|String|只有期权才有值|
|stockUnit|合约单位|String|只有期权才有值|
|exePrice|执行价格|String|只有期权才有值|
|startDate|首交易日|String|只有期权才有值|
|endDate|最后交易日|String|只有期权才有值|
|exeDate|行权日|String|只有期权才有值|
|delDate|交割日|String|只有期权才有值|
|expDate|到期日|String|只有期权才有值|
|version|合约版号|String|只有期权才有值|
|presetPrice|前(昨)结算价|String|期权、期货有值|
|setPrice|当日结算价(今 结)|String|期权、期货有值|
|stockClose|标的证券昨收|String|只有期权才有值|
|stockLast|标的证券价格|String|只有期权才有值|
|isLimit|有无涨跌限制|String|只有期权才有值|
|marginUnit|合约保证金|String|只有期权才有值|
|roundLot|一手合约数|String|只有期权才有值|
|inValue|内涵价值|String|只有期权才有值|
|timeValue|时间价值|String|只有期权才有值|
|preInterest|昨日持仓量|String|仅期权,期货有值|
|openInterest|持仓量|String|仅期权,期货有值|
|tradePhase|交易时段|String|只有期权才有值|
|remainDate|剩余天数|String|只有期权才有值|
|leverageRatio|杠杆比率|String|只有期权才有值|
|premiumRate|溢价率|String(2位小数)|只有期权才有值|
|premiumRate4|溢价率|String(4位小数)|只有期权才有值|
|impliedVolatility|隐含波动率|String|只有期权才有值|

|delta|风险指标delta|String|只有期权才有值|
|---|---|---|---|
|gramma|风险指标 gramma|String|只有期权才有值|
|theta|风险指标theta|String|只有期权才有值|
|rho|风险指标rho|String|只有期权才有值|
|vega|风险指标vega|String|只有期权才有值|
|realLeverage|真实杠杆|String|只有期权才有值|
|theoreticalPrice|理论价|String|只有期权才有值|
|exerciseWay|行权方式|String|只有期权才有值,行权方式: E:欧式期权A:美式期权|
|orderRatio|委比|String|期权没有值|
|hk_paramStatus|港股外部参考 状态|String|只有港股才有值:cas集合竞价vcm市场波动调节odd有碎 股成交7 = 111 = cas,vcm,odd 6 = 110 = cas,vcm,none 5 = 101 = cas,none,odd 4 = 100 = cas,none,none 3 = 011 = none,vcm,odd 2 = 010 = none,vcm,none 1 = 001 = none,none,odd 0 = 000 = none,none,none null = 000 = none,none,none期货无值|
|fundType|基金种类|String|只有基金才有值|
|sumBuy|总买量|String|目前只有QuoteDetailReq才有值并且level2才有值 期货无 值|
|sumSell|总卖量|String|目前只有QuoteDetailReq才有值并且level2才有值 期货无 值|
|averageBuy|均买价|String|目前只有QuoteDetailReq才有值并且level2才有值 期货无 值|
|averageSell|均卖价|String|目前只有QuoteDetailReq才有值并且level2才有值 期货无 值|
|upDownFlag|涨跌标识|String|"!":尚未开盘,或没有开盘"+":涨"-":跌"*":涨停"/":跌停"=": 平盘|
|zh|深港通标识|String|返回结果说明1:是; 0:不是; null:未知; "":未返回 期货无值|
|hh|沪港通标志|String|返回结果说明1:是; 0:不是; null:未知; "":未返回 期货无值|
|st|同一只股票多 市场 次类别|String|可能有多项,例如: 1001,1004 ;更多分类参考 ZZCateType 期货无值|
|bu|融资|String|返回结果说明1:是; 0:不是; null:未知; "":未返回 期货无值|
|su|融券|String|返回结果说明1:是; 0:不是; null:未知; "":未返回 期货无值|
|tbu|当日可融资|String|返回结果说明1:是; 0:不是; null:未知; "":未返回 期货无值|
|tsu|当日可融券|String|返回结果说明1:是; 0:不是; null:未知; "":未返回 期货无值|
|hs|港股股本|String|期货无值|
|ac|法定股本|String|期货无值|
|qf|债券合格投资 者标识qf|String|返回结果说明1:要求; 0:不要求; null:未知; "":未返回 期货无 值|
|qc|债券合格投资 者标识qc|String|返回结果说明“0”表示适合所有投资者,“1”表示投资者适当 性要求,“2”表示机构投资者适当性要求;null:未知; "":未返 回 期货无值|
|ah|AH股标识|String|若不为空,则是AH股,可将该值作为参数请求 ZZAHLinkReq对应的A股或者H股|
|VCMFlag|个股是否参与 VCM静态状态 标识|String|返回结果说明“Y”表示参与,“N”表示不参与 ,"":未返回 港 股有值|
|CASFlag|个股是否参与 CAS静态状态标 识|String|返回结果说明“Y”表示参与,“N”表示不参与 ,"":未返回 港 股有值|
||个股是否参与|||

|POSFlag|POS静态状态 标识|String|返回结果说明“Y”表示参与,“N”表示不参与 ,"":未返回 港 股有值|
|---|---|---|---|
|rp|回购期限|String|国债有值|
|cd|实际占款天数|String|国债有值|
|hg|沪股通|String|返回结果说明1:是; 0:不是; null:未知; "":未返回 期货无值|
|sg|深股通 标识|String|返回结果说明1:是; 0:不是; null:未知; "":未返回 期货无值|
|fx|风险警示 标识|String|返回结果说明1:是; 0:不是; null:未知; "":未返回 期货无值|
|ts|退市整理 标识|String|返回结果说明1:是; 0:不是; null:未知; "":未返回 期货无值|
|add_option_avg_price|加权平均价|String|期货无值|
|add_option_avg_pb|加权平均涨跌 BP|String|期货无值|
|add_option_avg_close|昨收盘加权平 均价|String|期货无值|
|pe2_unit|静态市盈率的 计算因子|String|期货无值|
|hk_volum_for_every_hand|港股最小交易 单位|String|期货无值|
|buy_cancel_count|ETF申购笔数|string|沪L2,深L1、L2|
|buy_cancel_num|ETF申购数量|string|沪L2,深L1、L2|
|buy_cancel_amount|ETF申购金额|string|沪L2,深证无数据|
|sell_cancel_count|ETF赎回笔数|string|沪L2,深L1、L2|
|sell_cancel_num|ETF赎回数量|string|沪L2,深L1、L2|
|sell_cancel_amount|ETF赎回金额|string|沪L2,深证无数据|
|tradingDay|交易日|String|仅期货有值|
|settlementID|极端编号|String|仅期货有值|
|settlementGroupID|结算组代码|String|仅期货有值|
|position_chg|日增|String|仅期货有值|
|close|今收价|String|仅期货有值|
|preDelta|昨虚实度|String|仅期货有值|
|currDelta|今虚实度|String|仅期权有值|
|updateMillisec|最后修改毫秒|String|仅期货有值|
|entrustDiff|委差|String||
|posDiff|仓差|String|期货、期权有值|
|currDiff|期现差|String|仅期货有值|
|deliveryDay|交割日期 YYYYMMDD|String|仅期货有值|
|riskFreeInterestRate|无风险利率|String|仅期货有值|
|intersectionNum|交割点数|String|仅期货有值|
|change1|change1|String|仅期货有值|
|totalBid|委买|String|仅期货有值,郑商所L2是总量值,非五档盘口计算值|
|totalAsk|委卖|String|仅期货有值,郑商所L2是总量值,非五档盘口计算值|
|IOPV|基金净值|String|仅基金有值|
|preIOPV|基金前收盘|String|仅基金有值|
|profit|目前是否盈利|String|CDR|
|suffrageDiff|是否存在投票 权差异|String|CDR|

|stateOfTransfer|转让状态|String|仅新三板股票有值,'N’表示正常状态,‘Y’表示首日挂牌,‘D’ 表示新增股票挂牌转让,'I'表示询价,'F'表示申购|
|---|---|---|---|
|typeOfTransfer|转让类型|String|仅新三板股票有值,‘T’表示协议转让方式;‘M’表示做市转让 方式;‘B’表示集合竞价+连续竞价转让方式;‘C’表示集合竞价转 让方式; 'P'表示发行方式;‘O’表示其他类型|
|exRighitDividend|除权除息|String|仅新三板股票有值,‘N’表示正常状态,‘E’表示除权,‘D’表 示除息,‘A’表示除权除息。|
||||仅新三板股票有值,‘T’表示对应证券是挂牌公司股票/上市 公司股票(允许盘后支持协议转让的挂牌股票);‘B’表示对 应证券是两网公司及退市公司股票; ‘O’表示对应证券是仅提|
|securityLevel|证券级别|String|供行权功能的期权;‘P’表示对应证券是持有人数存在200人 限制的证券; R’表示对应证券是其他类型的业务;'F'发行业 务; ’C’表示对应证券是可转换公司债券; ‘D’表示对应证券是 退市公司可转换公司债券。|
|rpd|资金可用日期|String|针对国债逆回购品种,SH1311和SZ1311|
|cdd|资金可取日期|String|针对国债逆回购品种,SH1311和SZ1311|
|change2|较上一副涨跌|String||
|earningsPerShare|每股收益|String||
|earningsPerShareReportingPeriod|每股收益所属 报告期|String|如:20181|
|hkTExchangeFlag|港股通是否可 交易标识|String|0表示两市都不可交易,1表示上海可交易,2表示深圳可交 易,3表示两市均可交易;其他,无定义|
|zgConvertCodes|可转债对应正 股代码,或正 股对应可转债 代码|String|多个股票代码以逗号隔开|
||返回值"1"代表 拥有表决权, 代表存在投票|||
|vote|权差异,同股 同权(否)返回 值"0"代表无表 决权,不存在 差异,同股同 权(是)|String|上市时是否具有表决权(科创板/创业板股票、创新企业股 票、存托凭证及沪深A股)|
||返回值"1"代表 未盈利,返回 ""|||
|upf|值0代表盈 利,如果为null 则说明不存在 这个字段,前 端根据这个含 义,显示对应 的描述信息|String|上市时是否尚未盈利(仅注册制股票有意义)sh:上市时 尚未盈利的发行人的股票(含或存托凭证),发行人首次实 现盈利后,消该特别标识。该字段仅针对注册制股票(含存 托凭证)有效sz:无特别说明|
|DRCurrentShare|当前份额|String|(沪伦通)|
|DRPreviousClosingShare|前收盘份额(上 一交易日)|String|(沪伦通)|
|DRConversionBase|转换基数(用于 计算溢价)|String|(沪伦通)|
|DRDepositoryInstitutionCode|存托机构代码|String|(沪伦通)|
|DRDepositoryInstitutionName|存托机构名称|String|(沪伦通)|
|DRSubjectClosingReferencePrice|标的收盘参考 价|String|(沪伦通)当请求股票为GDR股票,此价格为基础证券昨收价 当请求股票为CDR基础证券,此价格为CDR昨收价。|
|DR|沪伦通标识/ CDR(创业板)|String|1表示沪伦通CDR,2表示沪伦通CDR基础证券代码(可能是 GDR股票), 3标识其他CDR|

|GDR|沪伦通标识|String|(沪伦通) 1表示GDR,2表示GDR基础证券代码(可能是CDR 股票)|
|---|---|---|---|
|DRStockCode|基础证券代码|String|(沪伦通)传入的沪伦通股票对应的基础证券代码|
|DRStockName|基础证券名称|String|(沪伦通)传入的沪伦通股票对应的基础证券名称|
|DRSecuritiesConversionBase|基础证券转换 基数|String|(沪伦通)传入的沪伦通股票对应的基础证券转换基数|
|DRListingDate|上市日期(CDR 或GDR)|String|(沪伦通)|
|DRFlowStartDate|cdr初始流动性 生成起始日|String|(沪伦通)如:20181010|
|DRFlowEndDate|cdr初始流动性 生成终止日|String|(沪伦通)如:20181010|
|changeBP|最新价涨跌PB|String|国债逆回购才有值|
|subscribeUpperLimit|市价申报数量 上限|String|科创板|
|subscribeLowerLimit|市价申报数量 下限|String|科创板|
|afterHoursVolume|盘后成交量|String|科创板/深交所创业板,支持L1,L2|
|afterHoursAmount|盘后成交额|String|科创板/深交所创业板,支持L1,L2|
|afterHoursTransactionNumber|盘后成交笔数|String|科创板,仅支持L2|
|afterHoursWithdrawBuyCount|盘后撤单买笔 数|String|科创板,仅支持L2|
|afterHoursWithdrawBuyVolume|盘后撤单买数 量|String|科创板,仅支持L2|
|afterHoursWithdrawSellCount|盘后撤单卖笔 数|String|科创板,仅支持L2|
|afterHoursWithdrawSellVolume|盘后撤单卖数 量|String|科创板,仅支持L2|
|afterHoursBuyVolume|盘后委托买入 总量|String|科创板,仅支持L2|
|afterHoursSellVolume|盘后委托卖出 总量|String|科创板,仅支持L2|
|issuedCapital|发行资本(注册 资本)|String|备注:单位是万元|
|limitPriceUpperLimit|限价申报数量 上限|String||
|limitPriceLowerLimit|限价申报数量 下限|String||
|longName|中文证券简称 长|String||
|blockChg|板块权涨幅|String|板块|
|averageChg|板块均涨幅|String|板块|
|indexChg5|5日指数涨跌幅|String|板块|
|indexChg10|10日指数涨跌 幅|String|板块|
|listingType|挂牌类型|String|备注:A=当日新挂,E=存续合约,1=品种新挂,2=到期加 挂,3=调整加挂,4=波动加挂|
|underlyingSecurity|基础证券(标的 证券)|String|新三板|
||沪深市场:上 市日期;新三 板/北交所:挂|||

|listDate|牌日期 CCYYMMDD如 果交易状态为I- 询价,则填 写‘99991231’; 如果交易状态 为F-申购,则填 写发行日期|String||
|---|---|---|---|
|valueDate|对于优先股, 该字段存放其 起息日;对于 要约业务,该 字段存放其要 约开始日期。 对于发行业 务,该字段存 放其询价开始 日期|String|新三板|
||到期日 对于要 约业务,该字 段存放其要约|||
|expiringDate|结束日期。对 于发行业务, 该字段存放其 询价结束日 期。|String|新三板|
|serviceStatus|其他业务状态|String|新三板,参考 字段说明|
||停牌标志‘F’表 示正常转让; ‘T’表示停牌不|||
|suspendedSymbol|, 接受转让申 报;‘H’表示停 牌,接受转让 申报。|String|新三板|
||每笔限量,如 果交易状态为I- 询价,则填写 最大询价数|||
|mbxl|量;如果交易 状态为F-申购, 则填写网上投 资者最大申购 数量|String|新三板|
||最小申报数量 存放除做市商 外其他投资者|||
|zxsbsl|在正常交易时 段的每笔最小 申报数量|String|新三板|
|en|期货品种|String|期货|
|monthChangeRate|本月涨跌幅|string|支持沪深京市场(其他市场暂无意义)|
|yearChangeRate|本年涨跌幅|string|支持沪深京市场(其他市场暂无意义)|
|recentMonthChangeRate|近一月涨跌幅|string|支持沪深京市场(其他市场暂无意义)|
|recentYearChangeRate|近一年涨跌幅|string|支持沪深京市场(其他市场暂无意义)|
||||转发深交所证券状态字段,具体含义参考深交所<深圳证券 交易所数据文件交换接口规范>中证券信息(securities) 的 证券状态字段定义 参考链接 http://www.szse.cn/marketS ervices/technicalservice/interface/摘选部分参考说明完|
|securityStatus|证券状态|String,多个状态以"|"线分割|, 整性參考交易所官网接口: 1-停牌2-除权3-除息4-ST 5-*ST 6-上市首日7-公司再融资8-恢复上市首日9-网络投票10-退|

||||市整理期12-增发股份上市13-合约调整14-暂停上市后协 议转让15-实施双转单调整16-特定债券转让17-上市初期 18-退市整理期首日|
|---|---|---|---|
|buyQtyUpperLimit|限价买数量上 限|String|仅深交所有值|
|sellQtyUpperLimit|限价卖数量上 限|String|仅深交所有值|
|marketBuyQtyUpperLimit|市价买数量上 限|String|仅深交所有值|
|marketSellQtyUpperLimit|市价卖数量上 限|String|仅深交所有值|
|reg|是否注册制|String|创业板股票、创新企业股票、存托凭证及沪深A股;"1": 是,"0":否|
|vie|是否具有协议 控制架构|String|创业板股票、创新企业股票、存托凭证及沪深A股;"1": 是,"0":否|
|mf|是否实施市场 化转融通标识|String|仅深交所有值;"Y":实施,"N":不实施|
|rslf|限售股份出借 标志|String|仅深交所有值;"Y":允许出借,"N":不允许出借|
|mmf|是否有做市商 标志|String|仅深交所有值;"Y":是,"N":否|
|dtrad|是否支持回转 交易字段|String|仅沪深交所有值;"Y":是,"N":否|
|buyAuctionRange|买有效竞价范 围|string[]|无意义:预留字段|
|sellAuctionRange|卖有效竞价范 围|string[]|无意义:预留字段|
|afterHoursBuyQtyUpperLimit|盘后定价交易 买数量上限|String|仅深交所有值;|
|afterHoursBuyQtyUpperLimit|盘后定价交易 卖数量上限|String|仅深交所有值;|
|marketMakerQty|做市商数量|String|新三板,北证|
|issuePE|发行市盈率|String|新三板|
|unRestrictedShareCapital|非限售股本|String|新三板|
|cvtPrice|转股价格|String|新三板|
|cPutTriggerPrice|回售触发价|String|新三板|
|abCode|A股或者B股代 码|String||
|ttm|滚动市盈率|String||
|roe|年化净资产收 益率|String||
|buyVol1|买一量|String||
|sellVol1|卖一量|String||
|changeRate5|前5日涨跌幅|string|支持沪深京市场(其他市场暂无意义)|
|changeRate10|前10日涨跌幅|string|支持沪深京市场(其他市场暂无意义)|
|changeRate20|前20日涨跌幅|string|支持沪深京市场(其他市场暂无意义)|
|turnoverRate5|前5日换手率|string|支持沪深京市场(其他市场暂无意义)|
|turnoverRate10|前10日换手率|string|支持沪深京市场(其他市场暂无意义)|
|turnoverRate20|前20日换手率|string|支持沪深京市场(其他市场暂无意义)|
|limitUPChangeRate|沪深两市涨停|String||

|limitDownChangeRate|板百分比 沪深两市跌停 板百分比|String||
|---|---|---|---|
|lastTradeDate|预估最后交易 日(用于退市 整理股票展 示)|String|沪深|
|sect|股票证券类别|String|沪深港,参考 股票证券类别|
|matchTradeLastPrice|匹配成交最新 价|String|深圳债券|
|matchTradeVol|匹配成交成交 量|String|深圳债券|
|matchTradeAmount|匹配成交成交 额|String|深圳债券|
|tradePhase1|交易方式所处 阶段|String|深圳债券:1=匹配成交;2=协商成交;3=点击成交;4=询价 成交;5=竞价成交|
|lastPriceTradeType|最新价交易方 式|String|深圳债券:1=匹配成交;2=协商成交;3=点击成交;4=询 价成交;5=竞价成交 北证证券:1=匹配成交;2=点击成 交;3=协商成交;4=询价成交5=竞买成交|
|fiveMinutesChangeRate|五分钟涨速|string|支持沪深京市场(其他市场暂无意义)|
|threeMinutesChangeRate|三分钟涨速|string|支持沪深京市场(其他市场暂无意义)|
|zhbl|折合比例|String|北交所,新三板 对于优先股,该字段存放其票面股息率(%); 对于可转债,该字段存放票面利率(%)。|
|mgmz|每股面值|String|北交所,新三板 对于股票,每股面值为1元;对于可转债,每张 面值为100元。|
|hbzl|货币种类|string|‘HKD’ –港币, ‘USD’ –美元, ‘CNY’ –人⺠币|
|hIOPV|高精度iopv|string|沪深市场(5位小数)|
|transactionNum|现成交笔数|String||
|optionBreakReferencePrice|期权熔断参考 价|String|沪深市场(排序接口暂不支持)|
|buyBrokerInfos|经济席位列表 (买)|SseArrayList<ZZBrokerInfoItem>|请参考 ZZBrokerInfoItem 商品为港股且权限为10档的情况 下才有值|
|sellBrokerInfos|经济席位列表 (卖)|SseArrayList<ZZBrokerInfoItem>|请参考 ZZBrokerInfoItem 商品为港股且权限为10档的情况 下才有值|
|buyQtys|买队列列表|SseArrayList<ZZOrderQuantityItem>|请参考 ZZOrderQuantityItem 沪深level2情况下才有值(值 是从买1到买10)|
|sellQtys|卖买卖队列|SseArrayList<ZZOrderQuantityItem>|请参考 ZZOrderQuantityItem 沪深level2的情况下才有值 (值是从卖10到卖1,卖如果少数据是补齐栏位的)|
|changeRate3|前3日涨跌幅|string|支持沪深京市场(其他市场暂无意义)|
|changeRate60|前60日涨跌幅|string|支持沪深京市场(其他市场暂无意义)|
|yesterdayChangeRate|昨日涨跌幅|string|支持沪深京市场(其他市场暂无意义)|

##### **股票证券类别** 

|**值**|**说明**|
|---|---|
|上海市场||
|GBF|国债|
|GBZ|无息国债|

|DST|国债分销(仅用于分销阶段)|
|---|---|
|DVP|公司债(地方债)分销|
|CBF|企业债券|
|CCF|可转换企业债券|
|CPF|公司债券(或地方债券)|
|FBF|金融机构发行债券|
|CRP|质押式国债回购|
|BRP|质押式企债回购|
|ORP|买断式债券回购|
|CBD|分离式可转债|
|OBD|其它债券|
|CEF|封闭式基金|
|OEF|开放式基金|
|EBS|交易所交易基金(买卖)|
|OFN|其它基金|
|ASH|以人⺠币交易的股票(主板)|
|BSH|以美元交易的股票|
|KSH|以人⺠币交易的股票(科创板)|
|OEQ|其它股票|
|AMP|集合资产管理计划|
|WIT|国债预发行|
|LOF|LOF基金|
|OPS|公开发行优先股|
|PPS|非公开发行优先股|
|QRP|报价回购|
|CMD|控制指令(中登身份认证密码服务产品复用CMD证券子类别)|
|TCB|定向可转债|
|RET|REITs|

|深圳市场||
|---|---|
|1|主板A股|
|3|创业板股票|
|4|主板B股|
|5|国债(含地方债)|
|6|企业债|
|7|公司债|
|8|可转债|
|9|私募债|
|10|可交换私募债|
|11|证券公司次级债|
|12|质押式回购|
|13|资产支持证券|
|14|本市场股票ETF|
|15|跨市场股票ETF|
|16|跨境ETF|
|17|本市场实物债券ETF|
|18|现金债券ETF|
|19|黄金ETF|
|20|货币ETF|
|21|杠杆ETF (预留)|
|22|商品期货ETF|
|23|标准LOF|
|24|分级子基金|
|25|封闭式基金|
|26|仅申赎基金|
|28|权证|
|29|个股期权|
|30|ETF期权|

|33|优先股|
|---|---|
|34|证券公司短期债|
|35|可交换公司债|
|36|主板存托凭证|
|37|创业板存托凭证|
|38|基础设施基金|
|39|定向可转债|
|港股市场||
|Equity||
|1|Equity – Ordinary Shares|
|2|Equity – Preference Shares|
|6|Equity – Rights|
|7|Equity – Depository Receipt (HDR) – Ordinary Shares|
|12|Equity – Depository Receipt (HDR) – Preference Shares|
|Warrant||
|3|Warrant – Derivative Warrant (DW)|
|11|Warrant – Callable Bull/Bear Contract(CBBC)|
|13|Warrant – Equity Warrant|
|14|Warrant – Equity Linked Instrument(ELI)|
|15|Warrant – Inline Warrant|
|Bond||
|4|Bond – Debt Security|
|Trust||
|8|Trust – Real Estate Investment Trust (REIT)|
|9|Trust – Other Unit Trusts|
|10|Trust – Leveraged and Inverse Product (LIP)|
|16|Trust – Equity ETF|
|17|Trust – Fixed Income and Money Market ETF|

|18|Trust – Commodities ETF|
|---|---|
|99|Others – None of the above|

##### **买卖队列模型(ZZOrderQuantityItem)** 

|**名称**|**说明**|**备注**|
|---|---|---|
|ids|ID|ArrayList<string>|
|quantities|买卖量|ArrayList<string>|

##### **增值指标模型(ZZAddValueModel)** 

|**名称**|**说明**|**备注**||
|---|---|---|---|
|code|证券代码|String||
|date|当前快照日期|String||
|time|当前快照时间|String||
|ultraLargeBuyVolume|超大单主动买入成 交量|String, 交量|单一订单主动买入成交量达到超大单标准的总成|
|ultraLargeSellVolume|超大单主动卖出成 交量|String, 交量|单一订单主动卖出成交量达到超大单标准的总成|
|ultraLargeBuyAmount|超大单主动买入成 交额|String, 交额|单一订单主动买入成交额达到超大单标准的总成|
|ultraLargeSellAmount|超大单主动卖出成 交额|String, 交额|单一订单主动卖出成交额达到超大单标准的总成|
|largeBuyVolume|大单主动买入成交 量|String, 量|单一订单主动买入成交量达到大单标准的总成交|
|largeSellVolume|大单主动卖出成交 量|String, 量|单一订单主动卖出成交量达到大单标准的总成交|
|largeBuyAmount|大单主动买入成交 额|String, 额|单一订单主动买入成交额达到大单标准的总成交|
|largeSellAmount|大单主动卖出成交 额|String, 额|单一订单主动卖出成交额达到大单标准的总成交|
|mediumBuyVolume|中单主动买入成交 量|String, 量|单一订单主动买入成交量达到中单标准的总成交|
|mediumSellVolume|中单主动卖出成交 量|String, 量|单一订单主动卖出成交量达到中单标准的总成交|
|mediumBuyAmount|中单主动买入成交 额|String, 额|单一订单主动买入成交额达到中单标准的总成交|
||中单主动卖出成交|String,|单一订单主动卖出成交额达到中单标准的总成交|

|mediumSellAmount|额|额|
|---|---|---|
|smallBuyVolume|小单主动买入成交 量|String,单一订单主动买入成交量达到小单标准的总成交 量|
|smallSellVolume|小单主动卖出成交 量|String,单一订单主动卖出成交量达到小单标准的总成交 量|
|smallBuyAmount|小单主动买入成交 额|String,单一订单主动买入成交额达到小单标准的总成交 额|
|smallSellAmount|小单主动卖出成交 额|String,单一订单主动卖出成交额达到小单标准的总成交 额|
|ultraLargeNetInflow|超大单净流入|String,超大单买入成交额-超大单卖出成交额|
|largeNetInflow|大单净流入|String,大单买入成交额-大单卖出成交额|
|netCapitalInflow|主力净流入|String,超大单净流入+大单净流入|
|mediumNetInflow|中单净流入|String,中单买入成交额-中单卖出成交额|
|smallNetInflow|小单净流入|String,小单买入成交额-小单卖出成交额|
|fundsInflows|主力资金流入|collections.Array<string>排序为倒序,最新的在最前。 备注:板块主力资金流入=fundsInflows[0]|
|fundsOutflows|主力资金流出|collections.Array<string>排序为倒序,最新的在最前面 备注:板块主力资金流出=fundsOutflows[0]|
|ultraLargeDiffer|超大单差|String,(超大主动买入成交量–超大主动卖出成交 量)/总成交量,乘以10000取整后的值|
|largeDiffer|大单差|String,同上|
|mediumDiffer|中单差|String,同上|
|smallDiffer|小单差|String,同上|
|largeBuyDealCount|每单大买单成交手 数(超大单+大单)|String,每单大买单成交手数=大买单成交量/大买单成交 单数; 大买单=超大单+大单;|
|largeSellDealCount|每单大卖单成交手 数(超大单+大单)|String,每单大卖单成交手数=大卖单成交量/大卖单成交 单数; 大卖单=超大单+大单;|
|dealCountMovingAverage|每单成交手数移动 平均值|String|
|buyCount|买入单数|String|
|sellCount|卖出单数|String|
|BBD|大单净差|String|
|BBD5|五日大单净差|String|
|BBD10|十日大单净差|String|
|DDX|主力动向|String|

|DDX5|五日主力动向|String|
|---|---|---|
|DDX10|十日主力动向|String|
|DDY|涨跌动因|String|
|DDY5|五日涨跌动因|String|
|DDY10|十日涨跌动因|String|
|DDZ|大单差分|String|
|RatioBS|单数比|String|
|othersFundsInflows|散户资金流入|collections.Array<string>排序为倒序,最新的在最前|
|othersFundsOutflows|散户资金流出|collections.Array<string>排序为倒序,最新的在最前|
|fiveMinutesChangeRate|五分钟涨跌幅|String|
|dates|当日与五日日期|collections.Array<string>|
|largeOrderNumB|超大单买入单数|String|
|largeOrderNumS|超大单卖出单数|String|
|bigOrderNumB|大单买入单数|String|
|bigOrderNumS|大单卖出单数|String|
|midOrderNumB|中单买入单数|String|
|midOrderNumS|中单卖出单数|String|
|smallOrderNumB|小单买入单数|String|
|smallOrderNumS|小单卖出单数|String|
|mainforceMoneyNetInflow5|5日主力资金净流入|String|
|mainforceMoneyNetInflow10|10日主力资金净流 入|String|
|mainforceMoneyNetInflow20|20日主力资金净流 入|String|
|ratioMainforceMoneyNetInflow5|5日主力资金净流入 占比|String|
|ratioMainforceMoneyNetInflow10|10日主力资金净流 入占比|String|
|ratioMainforceMoneyNetInflow20|20日主力资金净流 入占比|String|
|largeInflow|超大单流入|String|
|bigInflow|大单流入|String|
|middleInflow|中单流入|String|
|smallInflow|小单流入|String|

|largeOutflow|超大单流出|String|
|---|---|---|
|bigOutflow|大单流出|String|
|middleOutflow|中单流出|String|
|smallOutflow|小单流出|String|

##### **经纪席位模型(ZZBrokerInfoItem)** 

|**名称**|**说明**|**备注**|
|---|---|---|
|id|ID||
|corp|证券证券名称||
|corporation|证券全名||
|state|买卖方向:0卖1买||

##### **线图点数据模型(ZZOHLCItem)** 

|**属性名**|**说明**|**型态**|**走势与五日**|**K线**|**盘后走势(科创板/深交所创业板)**|**历史分时**|**备注**|
|---|---|---|---|---|---|---|---|
|datetime|交易时 间|string|√|√|√|√||
|openPrice|开盘价|string|√|√|×|√||
|highPrice|最高价|string|√|√|×|√||
|lowPrice|最低价|string|√|√|×|√||
|closePrice|收盘价|string|√|√|√|√||
|tradeVolume|交易量|string|√|√|√|√||
|averagePrice|均价|string|√|√|×|√||
|referencePrice|参考价/ 昨收价|string|√|√|√|√|(期货期权是昨结,其 他是前一根收盘价)|
|amount|成交额|string|√|√|×|√||
|rgbar|红绿柱 MD值|string|√(仅 指数)|×|×|×||
|openInterest|持仓量|string|√(中 金所)|√(大商所, 郑商所)|×|×||
|IOPV|基金净 值|string|√(基 金)|√(基金)|×|√(基 金)||
|referenceIOPVPrice|基金净 值参考 价|string|√(基 金)|x|×|×||
|afterHoursVolume|盘后成 交量|string|×|√(科创板/深 交所创业板)|×|×||
|afterHoursAmount|盘后成 交额|string|×|√(科创板/深 交所创业板)|×|×||
|volumeRatio|量比|string|√(仅 分 时)|×|×|×|沪深|
|entrustBuyVolume|总委买|string|√(仅 分 时)|×|×|×|沪深L2|
|entrustSellVolume|总委卖|string|√(仅 分 时)|×|×|×|沪深L2|
|entrustDiff|委差|string|√(仅 分 时)|×|×|×|沪深L2|

##### **走势指标副图数据模型(ZZIndexItem)** 

|**属性名**|**说明**|**型态**|**备注**|
|---|---|---|---|
|datetime|时间|string||
|ddx|大单净差|string||
|ddy|主力动向|string||
|ddz|涨跌动因|string||
|bbd|大单差分|string||
|ratioBS|单数比|string||
|largeMoneyInflow|超大单净流入|string||
|bigMoneyInflow|大单净流入|string||
|midMoneyInflow|中单净流入|string||
|smallMoneyInflow|小单净流入|string||
|largeTradeNum|超大单成交单数|string||
|bigTradeNum|大单成交单数|string||
|midTradeNum|中单成交单数|string||
|smallTradeNum|小单成交单数|string||
|bigNetVolume|大单净量(增值K线数据暂不提供)|string||
|mainforceMoneyInflow|主力资金流入(板块指数返回)|string||
|mainforceMoneyOutflow|主力资金流出(板块指数返回)|string||

##### **复权信息数据模型(ZZFQItem)** 

|**属性名**|**说明**|**型态**|**备注**|
|---|---|---|---|
|dateTime|除权息日|string||
|increasePrice|增发价|string||
|allotmentPrice|配股价|string||
|bonusAmount|每股分红(包含基金分红)|string||
|bonusProportion|送股比例(包含基金折算比例)|string||
|increaseProportion|转增比例|string||
|increaseVolume|增发股份|string||
|allotmentProportion|配股比例|string||
|warrantsDistributionRatio|红利权证派送比例|String||
|mergeSplitRatio|并股/拆细比例|string||

##### **股本数据模型(ZZGBItem)** 

|**属性名**|**说明**|**型态**|**备注**|
|---|---|---|---|
|dateTime|日期|string|8位,精确到日|
|circulatingShare|股本|string||

##### **涨停模型(ZZZTSortingItem)** 

|**属性名**|**说明**|**型态**|**备注**|
|---|---|---|---|
|ztdateTime|涨停时间|String||
|code|代码|String||
|name|名称|String||
|dateTime|行情时间|String||
|market|市场别|String||
|subtype|次类别|String||
|lastPrice|最新价|String||
|preClosePrice|昨收价|String||
|changeRate|涨跌幅|String||
|buyVolumes|五档委买量,买5 ->买1|string[]||
|bu|融资标识|String|1:是; 0:不是; undefined或者“”:未知|
|su|融券标识|String|1:是; 0:不是; undefined或者“”:未知|

##### **港股其他数据模型(ZZHKStockInfoItem)** 

|**属性名**|**说明**|**型态**|**备注**|
|---|---|---|---|
|oddInfoItems|碎股列表|ZZHKOddInfoItem[]||
|vcmDatetime|vcm时间|String||
|vcmStartTime|市场调节 机制起始 时间|String||
|vcmEndTime|市场调节 机制结束 时间|String||
|vcmRefPrice|市场调节 机制参考 价|String||
|vcmLowerPrice|市场调节 下限价|String||
|vcmUpperPrice|市场调节 上限价|String||
||集合竞价|||

|casDatetime|时间|String||
|---|---|---|---|
|casOrdImbDirection|未能配对 买卖盘的 方向|N =买卖盘量相等B =买盘比卖盘多S =卖盘比买盘多<空格> =不适用||
|casOrdImbQty|未能配对 买卖盘的 数量|String||
|casRefPrice|参考价格|String||
|callAuctionStatus|集合竞价 状态||40:收盘集合竞价CAS; 20:开盘集合竞价POS|
|virtualRefPrice|虚拟参考 价|String||
|virtualOrdImbQty|虚拟未匹 配|String||
|buyPriceRange|买盘上下 限价格区 间|String[]||
|sellPriceRange|卖盘上下 限价格区 间|String[]||

##### **港股碎股类型(ZZHKOddInfoItem)** 

|**属性名**|**说明**|**型态**|**备注**|
|---|---|---|---|
|datetime|时间|String||
|orderId|订单编号|String||
|price|价格|String||
|orderQty|订单数量|String||
|brokerId|经纪人编号|String||
|side|买卖方向|0=Bid 1=Offer||

##### **交易日历数据模型(ZZTradeDateItem)** 

|**属性名**|**说明**|**型态**|**备注**|
|---|---|---|---|
|date|时间|string||
|type|交易类型|string|0:非交易日,1:交易日(仅日盘),2:交易日(日盘+夜盘),3:仅上午交 易,4:仅下午交易|
|desc|非交易日 说明|string||

##### **涨跌分布数据模型(ZZUpdownsItem)** 

|**属性名**|**说明**|**型态**|**备注**|
|---|---|---|---|
|dateTime|计算 时间|string||
|riseCount|上涨 家数|string||
|fallCount|下跌 家数|string||
|flatCount|平盘 家数|string||
|stopCount|停牌 家数|string||
|riseLimitCount|string|涨停家 数||
|fallLimitCount|跌停 家数|string||
|riseFallRange|涨跌 幅区 间|string[]|备注:riseFallRange中每个元素与下面区间一一对应,即 数组第0位置的数据值代表涨跌在(-∞,-9)区间的数量,依次 类推。其中涨跌区间为: {(-∞,-9),[-9,-8),[-8,-7),[-7,-6), [-6,-5),[-5,-4),[-4,-3),[-3,-2),[-2,-1),[-1,0),[0],(0,1],(1,2],(2,3], (3,4],(4,5],(5,6],(6,7],(7,8],(8,9],(9,+∞]}|
|oneRiseLimitCount|string|一字涨 停家数||
|natureRiseFallCount|string|自然涨 停家数|备注:自然涨停家数=涨停家数-一字涨停家数(15:00,存 在一字涨停时计算)|
|fiveAverageLimitCount|string|五日平 均涨停 家数||

##### **涨跌分布数据请求传入的日期类型(ZZCompoundUpdownsType)** 

|**属性名**|**说明**|**型态**|**备注**|
|---|---|---|---|
|CompoundUpdownsTypeOneDay|当天|ZZCompoundUpdownsType|调用方式:CompoundUpdownsType.CompoundUpdownsTypeOneDay|
|CompoundUpdownsTypeThirtyDays|最近30 天|ZZCompoundUpdownsType|调用方式: CompoundUpdownsType.CompoundUpdownsTypeThirtyDays|

##### **市场总览数据模型(ZZMarketOverviewItem)** 

|**属性名**|**说明**|**型态**|**备注**|
|---|---|---|---|
|market|市场|String||
|type|证券类别|String|0103:主板A股0104:主板B股0106:创业板0107:科创板|
|listValue|挂牌量|String||
|totalValue|总市值|String||
|flowValue|流通市值|String||

##### **板块排序模型(ZZSectionSortingItem)** 

|**属性名**|**说明**|**型态**|**备注**|
|---|---|---|---|
|code|板块代码|string||
|name|板块名称|string||
|type|板块类型|string|板块类型:Notion概念板块,Area地区板 块,Trade行业板块|
|lastPrice|最新价|string||
|openPrice|开盘价|string||
|highPrice|最高价|string||
|lowPrice|最低价|string||
|preClosePrice|昨收价|string||
|change|涨跌额|string||
|upDownFlag|涨跌状态|string||
|changeRate|涨跌幅|string||
|changeRate5|5日涨跌幅|string||
|changeRate10|10日涨跌幅|string||
|volume|总成交量|string|单位(手)|

|amount|总成交额|string||
|---|---|---|---|
|nowVolume|现成交量|string|单位(手):0.0.37及以上版本,个股所属板 块接口不提供|
|weightedChange|权涨幅|string||
|averageChange|均涨幅|string||
|flowValue|流通市值总和|string||
|hot|优品热度值|string|只有优品板块有值0.0.37及以上版本,个股所 属板块接口不提供|
|totalValue|市值总和|string||
|entrustBuyVolume|委买|string||
|entrustSellVolume|委卖|string||
|orderRatio|委比|string||
|entrustDiff|委差|string||
|turnoverRate|换手率|string||
|PE|市盈 动|string||
|SPE|市盈 静|string||
|PB|市净率|string||
|amplitudeRate|振幅比率|string||
|riseRate|涨股比|string|0.0.37及以上版本,个股所属板块接口不提供|
|advanceAndDeclineCount|涨跌家数|string|0.0.37及以上版本,个股所属板块接口不提供|
|limitUpCount|涨停家数|string|0.0.37及以上版本,个股所属板块接口不提供|
|limitDownCount|跌停家数|string|0.0.37及以上版本,个股所属板块接口不提供|
|capitalInflow|主力资金流入|string||
|capitalOutflow|主力资金流出|string||
|netCapitalInflow|主力资金净流 入|string||
|netCapitalInflow5|5日资金净流入|string||
|netCapitalInflow10|10日主力资金 净流入|string||
|stockCode|领涨个股代码|string|0.0.37及以上版本,个股所属板块接口不提供|

|stockName|领涨个股名|string|0.0.37及以上版本,|个股所属板块接口不提供|
|---|---|---|---|---|
|stockChange|领涨个股涨幅|string|0.0.37及以上版本,|个股所属板块接口不提供|
|stockChangeRate|领涨个股涨幅 比|string|0.0.37及以上版本,|个股所属板块接口不提供|
|stockLastPrice|领涨个股最新 价|string|0.0.37及以上版本,|个股所属板块接口不提供|
|stockSubtype **板块模型(ZZSection**|领涨个股次类 别 **Item)**|string|0.0.37及以上版本,|个股所属板块接口不提供|
|**属性名**|**说明**||**型态**|**备注**|
|code|板块代码||string||
|name|板块名称||string||

##### **次新债模型(ZZSubnewBondItem)** 

|**属性名**|**说明**|**型态**|**备注**|
|---|---|---|---|
|code|代码|string||
|name|名称|string||
|IPOPrice|发行价|string||
|lastPrice|最新价|string||
|IPODate|上市日期|string||
|subtype|次类别|string||
|preClosePrice|昨收价|string||
|rate|涨跌幅|string||
|totalRate|累计涨跌幅|string||
|change|涨跌|string||
|changeState|涨跌状态|string|+:涨,-:跌,=:平|
|turnoverRate|换手率|string||
|amount|成交额|string||
|capitalInflow|主力资金流入|string||
|EPS|每股收益|string||
|capitalization|总股本|string||
|circulatingShare|流通股本|string||
|flowValue|流通市值|string||
|totalValue|总市值|string||
|PE|动态市盈|string||
|bu|1为融券标识0为否|string||
|su|1为融资标识0为否|string||

##### **次新股模型(ZZSubnewStockItem)** 

|**属性名**|**说明**|**型态**|**备注**|
|---|---|---|---|
|code|代码|string||
|name|名称|string||
|subtype|次类别|string||
|IPOPrice|发行价|string||
|lastPrice|最新价|string||
|IPODate|上市日期|string||
|continuousLimitUpDays|连续涨停天数|string||
|preClosePrice|昨收价|string||
|rate|涨跌幅|string||
|totalRate|累计涨跌幅|string||
|change|涨跌|string||
|changeState|涨跌状态|string|+:涨,-:跌,=:平|
|turnoverRate|换手率|string||
|amount|成交额|string||
|capitalInflow|主力资金流入|string||
|EPS|每股收益|string||
|capitalization|总股本|string||
|circulatingShare|流通股本|string||
|flowValue|流通市值|string||
|totalValue|总市值|string||
|PE|动态市盈|string||
|bu|1为融券标识0为否|string||
|su|1为融资标识0为否|string||

##### **AB股列表行情数据模型(ZZABListItem)** 

|**属性名**|**说明**|**型态**|**备注**|
|---|---|---|---|
|dateTimeA|A股行情时间|string||
|codeA|A股代码|string||
|nameA|A股名称|string||
|marketA|A股市场|string||
|subtypeA|A股次类别|string||
|lastPriceA|A股最新价|string||
|preClosePriceA|A股前收盘价|string||
|changeRateA|A股涨跌幅|string||
|dateTimeB|B股行情时间|string||
|codeB|B股代码|string||
|nameB|B股名称|string||
|marketB|B股市场别|string||
|subtypeB|B股类别|string||
|lastPriceB|B股最新价|string||
|preClosePriceB|B股前收盘价|string||
|changeRateB|B股涨幅|string||
|premiumRateAB|AB溢价率|string||
|premiumRateBA|BA溢价率|string||
|changeB|B股涨跌|string||
|changeA|A股涨跌|string||

##### **AH股列表行情数据模型(ZZAHListItem)** 

|**属性名**|**说明**|**型态**|**备注**|
|---|---|---|---|
|name|联动名称|string||
|codeA|A股代码|string||
|lastPriceA|A股最新价|string||
|preClosePriceA|A股前收盘价|string||
|changeRateA|A股涨跌幅|string||
|datetimeA|A股行情时间|string||
|codeH|H股代码|string||
|lastPriceH|H股最新价|string||
|preClosePriceH|H股前收盘价|string||
|changeRateH|H股涨跌幅|string||
|datetimeH|H股行情时间|string||
|nameH|H股名称|string||
|premiumRate|AH溢价率|string||
|premiumRateHA|HA溢价率|string||

##### **CDR/GDR联动列表行情数据模型(ZZDRListItem)** 

|**属性名**|**说明**|**型态**|**备注**|
|---|---|---|---|
|code|代码|string||
|name|名称|string||
|subtype|次类别|string||
|lastPrice|最新价|string||
|preClosePrice|前收盘价|string||
|changeRate|涨跌幅|string||
|change|涨跌|string||
|datetime|行情时间|string||
|baseStockCode|基础证券代码|string||
|baseStockName|基础证券名称|string||
|baseLastPrice|基础证券最新价|string||
|basePreClosePrice|基础证券前收盘价|string||
|baseChangeRate|基础证券涨幅|string||
|baseChange|基础证券涨跌|string||
|baseSubtype|基础证券次类别|string||
|baseDatetime|基础证券行情时间|string||
|premiumRate|溢价率|string||

##### **可转债联动列表行情数据模型(ZZKZZListItem)** 

|**属性名**|**说明**|**型态**|**备注**|
|---|---|---|---|
|nameKZZ|可转债名称|string||
|codeKZZ|可转债代码|string||
|marketKZZ|可转债市场|string||
|subtypeKZZ|可转债次类别|string||
|lastPriceKZZ|可转债最新价|string||
|preClosePriceKZZ|可转债昨收|string||
|changeRateKZZ|可转债涨跌幅|string||
|datetimeKZZ|可转债行情时间|string||
|nameZG|正股名称|string||
|codeZG|正股代码|string||
|marketZG|正股市场|string||
|subtypeZG|正股次类别|string||
|lastPriceZG|正股最新价|string||
|preClosePriceZG|正股昨收|string||
|changeRateZG|正股涨跌幅|string||
|datetimeZG|正股行情时间|string||
|premiumRate|溢价率|string||
|conversionPrice|转股价|string||
|conversionValue|转股价值|string||
|backPrice|回售触发价|string||
|ransomPrice|强赎触发价|string||
|expirePrice|到期赎回价|string||

##### **要约收购数据模型(ZZOfferQuoteBean)** 

|**属性名**|**说明**|**型态**|**备注**|
|---|---|---|---|
|code|证券代码|String||
|name|证券名称|String||
|offerId|收购编码|String||
|offerName|收购人名称|String||
|price|收购价格|String||
|startDate|收购起始日|String||
|endDate|收购截止日|String||

##### **要约收购排序栏位(ZZSortField)** 

|**属性名**|**说明**|**型态**|**备注**|
|---|---|---|---|
|CODE|证券代码|int|调用方式:ZZSortField.CODE|
|NAME|证券名称|int|调用方式:ZZSortField.NAME|
|OFFER_ID|收购编码|int|调用方式:ZZSortField.OFFER_ID|
|OFFER_NAME|收购人名称|int|调用方式:ZZSortField.OFFER_NAME|
|PRICE|收购价格|int|调用方式:ZZSortField.PRICE|
|START_DATE|收购起始日|int|调用方式:ZZSortField.START_DATE|
|END_DATE|收购截止日|int|调用方式:ZZSortField.END_DATE|

##### **要约收购排序类型(ZZSortType)** 

|**属性名**|**说明**|**型态**|**备注**|
|---|---|---|---|
|ASC|升序|String|调用方式:ZZSortType.ASC|
|DESC|降序|String|调用方式:ZZSortType.DESC|

##### **板块类别个股列表模型(ZZCategoryList)** 

|**属性名**|**说明**|**型态**|**备注**|
|---|---|---|---|
|name|分类名|String||
|list|板块类别个股|ArrayList< ZZCategoryItem>||

##### **板块类别个股模型(ZZCategoryItem)** 

|**属性名**|**说明**|**型态**|**备注**|
|---|---|---|---|
|code|分类代码|String||
|name|分类名|String||
|type|分类内容型态|String||
|group|组别|int||

##### **股票查询模型(ZZSearchItem)** 

|**属性名**|**说明**|**型态**|**备注**|
|---|---|---|---|
|code|股票代码|string||
|name|股票名称|string||
|subtype|次类别|string||
|pinYin|拼音|string||
|market|市场别|string||
|hh|沪港通标签|number|1:是, 0:否|
|hz|深港通标签|number|1:是, 0:否|
|st|个股、基金、债券所属 的分类版块类型|String|如:502000.sh属于基金(1100) ->分级基金(1130) - >分级母基(1133)更多分类参考 ZZCateType|
|longName|股票长名称|String|如:天能股份,长简称为:天能电池集团股份|
|longPinYin|股票长名称首字母|String|如:TNGF,长简称首字母为:TNDCJTGF|
|ID|股票代码(不含市场后 缀)|String||
|name2|股票名称(去除文字间 空格的股票名称)|String||

##### **港股通/沪深股通额度走势模型(ZZTongItem)** 

|**属性名**|**说明(港股通/沪深股通)**|**型态**|**备注**|
|---|---|---|---|
|datetime|日期|string|如:202002250930|
|SHInitialAmount|港股通(沪)/沪深股通(沪)初始额度|string||
|SHRemainingAmount|港股通(沪)/沪深股通(沪)剩余额度|string||
|SHInflowAmount|港股通(沪)/沪深股通(沪)净流入|string||
|SZInitialAmount|港股通(深)/沪深股通(深)初始额度|string||
|SZRemainingAmount|港股通(深)/沪深股通(深)剩余额度|string||
|SZInflowAmount|港股通(深)/沪深股通(深)净流入|string||
|SHSZInflowAmount|沪深合计净流入|string||

##### **港股通/沪深股通买入卖出走势模型(ZZHKTItem)** 

|**属性名**|**说明(港股通/沪深股通)**|**型态**|**备注**|
|---|---|---|---|
|datetime|日期|string|如:202002250930|
|SHBuyAmount|南北向资金沪买入成交额|string||
|SHSellAmount|南北向资金沪卖出成交额|string||
|SHInflowAmount|南北向资金沪净买入成交额|string||
|SZBuyAmount|南北向资金深买入成交额|String||
|SZSellAmount|南北向资金深卖出成交额|string||
|SZInflowAmount|南北向资金深净买入成交额|string||
|SHSZInflowAmount|沪深合计净买入|string||

##### **AB股联动模型** 

|**属性名**|**说明**|**型态**|**备注**|
|---|---|---|---|
|code|代码|String||
|name|名称|String||
|market|市场|String||
|subtype|次类别|String||
|lastPrice|最新价|String||
|preClosePrice|昨收价|String||
|change|涨跌|String||
|changeRate|涨跌幅|String||
|premiumRateAB|AB溢价率|String||
|premiumRateBA|BA溢价率|String||

##### **AB股列表模型** 

|**属性名**|**说明**|**型态**|**备注**|
|---|---|---|---|
|codeA|A股代码|String||
|nameA|A股名称|String||
|marketA|A股市场|String||
|subtypeA|A股次类别|String||
|lastPriceA|A股最新价|String||
|preClosePriceA|A股昨收价|String||
|changeA|A股涨跌|String||
|changeRateA|A股涨跌幅|String||
|datetimeA|A股行情时间|String||
|codeB|B股代码|String||
|nameB|B股名称|String||
|marketB|B股市场|String||
|subtypeB|B股次类别|String||
|lastPriceB|B股最新价|String||
|preClosePriceB|B股昨收价|String||
|changeB|B股涨跌|String||
|changeRateB|B股涨跌幅|String||
|datetimeB|B股行情时间|String||
|premiumRateAB|AB溢价率|String||
|premiumRateBA|BA溢价率|String||

##### **可转债静态信息模型** 

|**属性名**|**说明**|**型态**|**备注**|
|---|---|---|---|
|code|可转债代码|String||
|codeZG|正股代码|String||
|priceZG|转股价格(小数位4)|String||
|priceZZ|转债价格(小数位4)|String||
|marketZG|转股代码市场|String||
|backPrice|回售触发价(小数位4)|String||
|ransomPrice|强赎触发价(小数位4)|String||
|expirePrice|到期赎回价(小数位4)|String||
|expireDate|到期日|String||
|dateZG|转股日期|String||
|scaleSize|发行规模单位:亿元(小数位8)|String||
|remainSize|剩余规模单位:亿元(小数位8)|String||
|ZQRate|网上中签率%(小数位10)|String||
|PSRate|股东配售率%(小数位2)|String||
|isKZ|是否可转股0:否1:是|String||
|isHS|是否可回售0:否1:是|String||

##### **- 期权 交割月** 

|**属性名**|**说明**|**型态**|**备注**|
|---|---|---|---|
|time|交割月|string||
|dayCount|剩余天数|string||

##### **IPO类型** 

|**属性名**|**说明**|**备注**|
|---|---|---|
|IPOTypeSHSZ|沪深新股||
|IPOTypeBond|新债||
|IPOTypeBJ|新三板新股||
|IPOTypeBZ|北证新股||
|IPOTypeHK|港股新股||

##### **新股日历数据说明** 

|**属性名**|**说明**|**型态**|**备注**|
|---|---|---|---|
|sg|今日申购个数|string||
|jjsg|当日待申购个数|string||
|zq|今日中签个数|string||
|ss|今日上市个数|string||
|dss|当日待上市个数|string||
|jjfx|今日即将发行个数|string||
|wss|今日未上市个数|string||
|NORMALDAY|日期|string||

##### **某日新股(债)信息键值表** 

新股(沪深京) 

|**名称**|**说明**|**型态**|**备注**|
|---|---|---|---|
|sglist|今日申购|Array||
|zqlist|今日中签|Array||
|sslist|今日上市|Array||
|jjfxlist|即将发行|Array||
|wsslist|未上市|Array||
|APPLYCODE|申购代码|string||
|SECUABBR|股票简称|string||
|TRADINGCODE|申购代码|string||

|ISSUEPRICE|实际发行价格|string||
|---|---|---|---|
|ISSUEPRICEPLAN|预估发行价格|string|财汇返回|
|PEAISSUE|发行市盈率|string||
|SUCCRESULTNOTICEDATE|中签公告日|string||
|CAPPLYSHARE|申购上限|string|SETYPE是Y时,单位:万份;N时,单 位:万股|
|ALLOTRATEON|中签率|string||
|LISTINGDATE|上市日期|string||
|BOOKSTARTDATEON|申购日期|string||
|ISSUESHARE|实际发行总量|string|SETYPE是Y时,单位:万份;N时,单 位:万股|
|ISSUESHAREON|实际网上发行数量|string|SETYPE是Y时,单位:万份;N时,单 位:万股|
|CAPPLYPRICE|实际网上申购所需资 金|string|1、实际网上申购所需资金=申购上线* 实际发行价格2、单位:万元|
|CISSUESHAREPLAN|计划发行总量|string|SETYPE是Y时,单位:万份;N时,单 位:万股|
|ISSUESHAREONPLAN|计划网上发行量|string|SETYPE是Y时,单位:万份;N时,单 位:万股|
|CAPPLYPRICEPLAN|预估网上申购所需资 金|string|财汇返回|
|CAPPLYSHAREPLAN|顶格申购所需资金|string|财汇返回|
|KEYCODE|是否科创板|string|Y:是科创板N:不是科创板|
|ISPROFIT|上市时尚未盈利|string|1:是0:否null/-:未披露|
|ISDIFFVOTE|是否存在投票权差异|string|1:是0:否null/-:未披露|
|ISVIEFRAME|是否具有协议控制架 构|string|1:是0:否null/-:未披露|
|ISSSYSTEM|发行制度|string|1-注册制 ,2-核准制|
|SETYPE|是否是CDR类型|string|是-Y, 否-N|
|STOCKCBX|基础股票(X)与CDR(Y) 的转换比例_X|string|基础股票(X)与CDR(Y)的转换比例_X|
|CDRCBY|基础股票(X)与CDR(Y)|string|基础股票(X)与CDR(Y)的转换比例_Y|

的转换比例_Y 

###### 新股(港股) 

|**名称**|**说明**|**型态**|**备注**|
|---|---|---|---|
|sglist|今日申购|Array||
|sslist|今日上市|Array||
|PRICE|计划发行价区间|string||
|TRANSUNIT|买卖单位|string||
|LISTDATE|上市日期|string||
|OFFPLABEGDATE|法人网下配售申购日期起始日|string||
|OFFPLAENDDATE|法人网下配售申购日期截止日|string||
|TRADINGCODE|股票代码|string||

新债 

|**名称**|**说明**|**型态**|**备注**|
|---|---|---|---|
|sglist|当日申购列表|Array||
|jjsglist|当日待申购列表|Array||
|dsslist|当日待上市列表|Array||
|LISTINGDATE|上市日期|string||
|TRADINGCODE|债券代码|string||
|SECUABBR|可转债名称|string||
|ALLOTRATEON|中签率|string||
|CONVERTPRICE|转股价格|string||
|STOCKTRADINGCODE|对应正股代码|string||
|STOCKSECUABBR|对应正股名称|string||
|PREFERREDPLACINGCODE|原股东配售代码|string||
|APPLYCODE|可转债申购代码|string||
|BEGINDATE|申购日期|string||
|ISSUEVAL|债券发行总额|string||
|CAPPLYVOL|网上认购数量上限|string||
|OFFCAPPLYVOL|网下认购数量上限|string||
|ISSUEPRICE|发行价格|string||

##### **新股(债)IPO详情属性说明** 

新股 

|**名称**|**说明**|**型态**|**备注**|
|---|---|---|---|
|APPLYCODE|申购代码|string||
|SECUABBR|股票简称|string||
|TRADINGCODE|交易代码|string||
|ISSUEPRICE|实际发行价格|string||
|ISSUEPRICEPLAN|预估发行价格|string||
|PEAISSUE|发行市盈率|string||
|SUCCRESULTNOTICEDATE|中签公告日|string||

|CAPPLYSHARE|申购上限|string|SETYPE是Y时,单位:万份;N时,单 位:万股|
|---|---|---|---|
|ALLOTRATEON|中签率|string||
|LISTINGDATE|上市日期|string||
|BOOKSTARTDATEON|申购日期|string||
|ISSUESHARE|实际发行总量|string|SETYPE是Y时,单位:万份;N时,单 位:万股|
|ISSUESHAREON|实际网上发行数量|string|SETYPE是Y时,单位:万份;N时,单 位:万股|
|CAPPLYPRICE|实际网上申购所需资 金|string|1、实际网上申购所需资金=申购上线* 实际发行价格2、单位:万元|
|CISSUESHAREPLAN|计划发行总量|string|SETYPE是Y时,单位:万份;N时,单 位:万股|
|ISSUESHAREONPLAN|计划网上发行量|string|SETYPE是Y时,单位:万份;N时,单 位:万股|
|BOARDNAME|所属板块|string||
|COMPROFILE|公司简介|string||
|BUSINESSSCOPE|经营范围|string||
|ISSUEALLOTNOON|中签号|string||
|REFUNDDATEON|网上申购资金解冻日 期|string||
|LEADUNDERWRITER|主承销商|string||
|CAPPLYPRICEPLAN|预估网上申购所需资 金|string|财汇返回|
|CAPPLYSHAREPLAN|顶格申购所需资金|string|财汇返回|
|NEWTOTRAISEAMT|募集资金总额|string||
|NEWNETRAISEAMT|募集资金净额|string||
|KEYCODE|是否科创板|string|Y:是科创板N:不是科创板|
|TYPE|类型|string|1:新股|
|ISPROFIT|上市时尚未盈利|string|1:是0:否null/-:未披露|
|ISDIFFVOTE|是否存在投票权差异|string|1:是0:否null/-:未披露|

|ISVIEFRAME|是否具有协议控制架 构|string|1:是0:否null/-:未披露|
|---|---|---|---|
|ISSSYSTEM|发行制度|string|1-注册制 ,2-核准制|
|SETYPE|是否是CDR类型|string|是-Y, 否-N|
|STOCKCBX|基础股票(X)与CDR(Y) 的转换比例_X|string|基础股票(X)与CDR(Y)的转换比例_X|
|CDRCBY|基础股票(X)与CDR(Y) 的转换比例_Y|string|基础股票(X)与CDR(Y)的转换比例_Y|

新债 

|**名称**|**说明**|**型态**|**备注**|
|---|---|---|---|
|APPLYCODE|申购代码|string||
|TRADINGCODE|债券代码|string||
|SECUABBR|债券名称|string||
|STOCKTRADINGCODE|正股代码|string||
|STOCKSECUABBR|正股名称|string||
|ISSUEPRICE|发行价格|string||
|CONVERTPRICE|初始转股价格|string||
|PREFERREDPLACINGCODE|配售代码|string||
|PREFERREDPLACINGNAME|配售简称|string||
|ISSUERRATING|信用评级|string||
|ISSUEVAL|债券发行总额|string||
|INTERESTTERM|利率|string||
|CAPPLYVOL|申购上限|string||
|BOOKSTARTDATEON|申购日期|string||
|SUCCRESULTNOTICEDATE|中签公告日|string||
|LISTINGDATE|上市日期|string||
|ALLOTRATEON|中签率|string||
|MATURITYYEAR|债券年限(年)|string||
|BONDTYPE|债券类型|string||
|ONLINEGSINVLWINNUM|中签号|string||
|OFFCAPPLYVOL|网下认购数量上限|string||
|TYPE|类型|string|2:新股|

##### **交易市场支持的线图类型** 

||**分时**|**五日**|**日K**|**周K**|**月K**|**季K**|**年K**|**1分K**|**5分K**|**15分K**|**30分K**|**60分K**|**120分K**|**历史分时**|
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
|上海市场(sh)|√|√|√|√|√|√|√|√|√|√|√|√|√|√|
|深圳市场(sz)|√|√|√|√|√|√|√|√|√|√|√|√|√|√|
|港股市场(hk)|√|√|√|√|√|√|√|√|√|√|√|√|√|√|
|新三板(bj)|√|√|√|√|√|√|√|√|√|√|√|√|√|√|
|中金所(cff)|√|√|√|√|√|x|√|√|√|√|√|√|√|x|
|大商所(dce)|√|√|√|√|√|x|√|√|√|√|√|√|√|x|
|郑商所(czce)|√|√|√|√|√|x|√|√|√|√|√|√|√|x|
|上期所(shfe)|√|√|√|√|√|x|√|√|√|√|√|√|√|x|
|上期所原油(ine)|√|√|√|√|√|x|√|√|√|√|√|√|√|x|
|海外市场(gb)|x|x|√|√|√|x|x|x|x|x|x|x|x|x|
|板块指数(bk)|√|√|√|√|√|x|√|√|√|√|√|√|√|√|
|中证指数(csi)|√|√|√|√|√|√|√|√|√|√|√|√|√|√|
|北交所(bz)|√|√|√|√|√|√|√|√|√|√|√|√|√|√|

##### **复权支持的线图类型** 

||**上海市场(sh)**|**深圳市场(sz)**|**北交所(bz)**|**港股市场(hk)**|
|---|---|---|---|---|
|日k前后复权|支持(成交量复权)|支持(成交量复权)|支持|支持|
|周k前后复权|支持(成交量复权)|支持(成交量复权)|支持|支持|
|月k前后复权|支持(成交量复权)|支持(成交量复权)|支持|支持|
|季k前后复权|支持(成交量复权)|支持(成交量复权)|支持|支持|
|年k前后复权|支持(成交量复权)|支持(成交量复权)|支持|支持|

##### **沪深市场K线计算历史换手率(FormatUtility类)** 

|**方法名**|**参数**|**型态**|**备注**|
|---|---|---|---|
|calculateTurnoverRate|ohlcItem|ZZOHLCItem||
|GBItems|ArrayList<CirculatingShareItem>|从OHLCResp中的GBItems字段获取 GBItems||

##### **调用示例** 

String turnoverRate = 

FormatUtility.calculateTurnoverRate(ohlcItem,ohlcResponse.GBItems); 

##### **新三板serviceStatus字段说明** 

###### **说明** 

字段来源新三板市场,最新说明请参考全国中小企业股份转让系统官网交易支持平台 

|||||**可转** ||**退市公司** ||
|---|---|---|---|---|---|---|---|
|**XXQTYW**|**优先股**|**挂牌公司股票**|**要约收购/回购**|**换公司债务**|**发行证券**|**可转换公司债券**|**其他**|
||||为T表明处于 ||为"T"表 明采用 |||
|第一字节|预 留, 默认 为空 格|为T,表明处于要约期,为F表明不处 于要约期|要约收购/回 购截止期间, 禁止做撤回预 售要约申报, 为F表明处于 要约收购/回 购正常期间|预 留, 默认 为空 格|的是询 价发行 方式, 为"F”表 示末采 用询价 发行方 式|预 留, 默认 为空 格|预 留, 默认 为空 格|
||预|为T表明有差异化表决权安排,为F表 明没有差异化表决权安排 行情展示:||预|为"T"表 明采用 的是询 价发行|预|预|
|第二字节|留, 默认 为空|对于有差异化表决权安排的挂牌公司 股票,应按如下两种方法明确揭示1. 证券简称后缀'-W', 2.行情信息中通过|预留,默认为 空格|留, 默认 为空|方式, 为"F”表 |留, 默认 为空|留, 默认 为空|
||格|文字表述的方式揭示,建议同时采取 以上两种,可选一种||格|示末采 用询价 发行方 式|格|格|
||回售|||回售||回售||
||标|||标|为"T"表|标||
||志,|||志,|明采用|志,||
||该证|||该证|的是询|该证|预|
||券是|||券是|价发行|券是|留|
|第三字节|否处|预留默认为空格|预留,默认为|否处|方式,|否处|, 默认|
||于回|,|空格|于回|为"F”表|于回|为空|
||售|||售|示末采|售|格|
||期:|||期:|用询价|期:||
||F-|||F-|发行方|F-||
||否,|||否,|式|否,||
||T-是|||T-是||T-是||
||转股|||转售||转售||
||标|||标||标||
||志,|||志,||志,||
||该证 |||该证 ||该证 ||
||券是|||券是||券是|预|
||否允||留默认为|否允|预留,|否允|留,|
|第四字节|许转|预留,默认为空格|预, 空格|许转|默认为|许转|默认|
||股:|||股:|空格|股:|为空|
||F-禁|||F-禁||F-禁|格|
||止,|||止,||止,||
||T-允|||T-允||T-允||

许 

许 许
