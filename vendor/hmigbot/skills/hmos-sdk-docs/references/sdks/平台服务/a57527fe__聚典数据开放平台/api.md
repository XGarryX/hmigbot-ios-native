# # 聚典 SDK 使用对接说明 

## 约束: 

本模块首批接口从 OpenHarmony SDK API version 11 开始支持。 

## 引入 方法一 : 项目级 oh-package.json5 引入 ``` 

"dependencies": { // 建议使用最新版本 "judian_search": "^1.0.0" }, ``` 

方法二 : 打开项目, Terminal 终端输入 ``` ohpm install @cishu/judian_search ``` 

## 代码开发 ### 开启权限 

``` 

ohos.permission.INTERNET // 申请网络权限 

ohos.permission.GET_BUNDLE_INFO // 申请应用信息权限 

``` 

### 获取 token 

获取 APP 对应的唯一 ID appIdentifier 

``` 

import { bundleManager } from '@kit.AbilityKit'; 

let info = await 

let appIdentifier = info.signatureInfo.appIdentifier as string ; 

``` 

请到 https://www.jdapi.com/ 官网注册并联系服务提供商,提供 appIdentifier 信息获取对应功能的 token 

### 编写代码 

使用 token 创建服务 client 

``` 

const judianApi = creatJuDianSdkClient(token) // 创建默认搜索服 务客服端 

# 根据设计需求调用不用功能 

judianApi?.getContent("","",true,"body").then((result: AxiosResponse<ContentResponse | GetContent200ResponseOneOf>) => { 

// 编写对应代码 

...... 

}).catch((error: WordSearchError) => { 

// 异常处理 

...... 

}) 

使用 token 创建诗词服务 client (非必要,可根据需求初始化) 

const judianPoetryApi = creatJuDianPoetrySdkClient(token) // token 是和默认的搜索服务共用一个 token 

# // 诗词和诗人相关标签 

// 编写对应代码 

...... 

}).catch((error: WordSearchError) => { 

# // 异常处理 

...... 

}) 

``` 

# ### 提供基础 xml 数据解析模板 

详情可查看 entry/src/main/ets/xml/xmlParse.ets 可根据开发设计实际需求进行修改 

## 方法与请求参数说明 

``` 

/** 

# * 开放接口 

*/ 

declare class DefaultApi extends BaseAPI { 

/** 

* 

- @summary 纪年换算 

- @param {string} q 关键字 

- @param {*} [options] Override http request option. 

- @throws {RequiredError} 

- @memberof DefaultApi 

*/ 

conversionEpoch(q: string, options?: RawAxiosRequestConfig): Promise<axios.AxiosResponse<EpochConversionResponse, 

any>>; 

/** 

# * 获取书籍分类列表支持分页查询 

# * @summary 获取书籍分类列表 

- @param {string} [name] 分类名字 

- @param {Set<number>} [parentId] 父分类 ID ,如果只想获取第 

- 一层分类请传 0 

- @param {number} [size] 数量 , 最大值 200 ,如果超过会自动变为 200 

- @param {number} [page] 页码 

- @param {*} [options] Override http request option. 

- @throws {RequiredError} 

- @memberof DefaultApi 

*/ 

findBookCategories(name?: string, parentId?: Set<number>, size?: number, page?: number, options?: RawAxiosRequestConfig): Promise<axios.AxiosResponse<PageBookCategoryResponse, any>>; 

/** 

- 该模糊搜索会同时搜索词头和释文,通过 headword 再调用内容 / 释 

- 文接口。高亮里面包含 text 、 headword 、 simplified 

- @summary 全文模糊搜索 

- @param {string} [q] 要搜索的字 / 词 

- @param {number} [textLength] text 最大长度,超出会截取掉 

- @param {number} [size] 页的大小 

- @param {number} [page] 页码 

- @param {Array<number>} [bookId] 需要搜索的书籍,为空搜索 全部有权限的书籍 

- @param {*} [options] Override http request option. 

- @throws {RequiredError} 

- @memberof DefaultApi 

*/ 

fuzzySearchBookExplain(q?: string, textLength?: number, size?: number, page?: number, bookId?: Array<number>, options?: RawAxiosRequestConfig): 

any>>; 

/** 

- 根据关键字搜索古今地名列表 , 最多 100 条数据 

- @summary 古今地名 

- @param {string} q 地名关键字 

- @param {GetAncientAndModernPlaceNameFontInEnum} [fontIn] 字体信息是否在响应体中 

- @param {*} [options] Override http request option. 

- @throws {RequiredError} 

- @memberof DefaultApi 

*/ 

getAncientAndModernPlaceName(q: string, fontIn?: GetAncientAndModernPlaceNameFontInEnum, options?: RawAxiosRequestConfig): 

any>>; 

/** 

* 
 1. 精确查询英语的释文 2. 接口返回的部分内容是乱码需要 下载对应的字体包才能显示 3. 获取字体令牌和字体名字默认是在响 应头中,需要传入在请求的参数加上 `fontIn=body` 才会在响应体 中,加了这个参数会导致返回的 json 会变为以下 内容 ```json { \"data\": { // 源数据 }, \"font\": { \"id\":\" 字体的 ID, 通过这个 ID 可以 直接下载字体包 \", \"name\":\" 字体的名字 \", \"token\":\" 字体的令牌 \", } } ``` 4. 如果没有在书籍权限里面添加英汉相关的书籍会返回 `search-book-not-found` 5. 接口有限流所以不能调用太快 

- @summary 查询英语的释文数据 

- @param {string} q 要搜索的字 / 词 

- @param {Array<number>} [bookId] 需要搜索的书籍,为空搜索 全部有权限的书籍 

- @param {number} [maxSize] 结果的最大大小 , 最多支持 100 条数据 

- @param {GetBookEnglishExplainFontInEnum} [fontIn] 字体信息 是否在响应体中 

- @param {*} [options] Override http request option. 

- @throws {RequiredError} 

- @memberof DefaultApi 

*/ 

getBookEnglishExplain(q: string, bookId?: Array<number>, maxSize?: number, fontIn?: GetBookEnglishExplainFontInEnum, options?: RawAxiosRequestConfig): Promise<axios.AxiosResponse<GetBookEnglishExplain200Response, any>>; 

/** 

* 
 1. 精确匹配查的字词,支持多本书的书籍 ID 传入,如果不 传书籍 ID 会查询该客户端所有的书籍释文 2. 接口返回的部分内容是 乱码需要下载对应的字体包才能显示 

3. 获取字体令牌和字体名字默认是在响应头中,需要传入在请求的参 数加上 `fontIn=body` 才会在响应体中,加了这个参数会导致返回的 json 会变为以下内容 ```json { \"data\": { // 源数据 }, \"font\": { \"id\":\" 字体的 ID, 通过这个 ID 可以直接下载字体包 \", \"name\":\" 字 体的名字 \", \"token\":\" 字体的令牌 \", } } ``` 4. 接口有限流所以不能 调用太快 

# * @summary 查询字词的书籍的释文数据 

- @param {string} q 要搜索的字 / 词 

- @param {boolean} [simplified] 是否同时搜索简体 , false 不搜 

- 索 ,true 搜索 

- @param {boolean} [qualitative] 是否同时定性语 , false 不搜 

索 ,true 搜索 

- @param {number} [maxSize] 结果的最大大小 , 最多支持 100 条数据 

- @param {Array<number>} [bookId] 需要搜索的书籍,为空搜索 全部有权限的书籍 

- @param {boolean} [synonym] 是否同时包含近义词搜索 false 不搜 索 ,true 搜索 

- @param {GetBookExplainFontInEnum} [fontIn] 字体信息是否在 响应体中 

- @param {*} [options] Override http request option. 

- @throws {RequiredError} 

- @memberof DefaultApi 

*/ 

getBookExplain(q: string, simplified?: boolean, qualitative?: boolean, maxSize?: number, bookId?: Array<number>, synonym?: boolean, fontIn?: GetBookExplainFontInEnum, options?: RawAxiosRequestConfig): 

Promise<axios.AxiosResponse<GetBookExplain200Response, any>>; 

/** 

* 
 1. 精确查询汉字的英语释文 2. 接口返回的部分内容是乱码 需要下载对应的字体包才能显示 3. 获取字体令牌和字体名字默认是 在响应头中,需要传入在请求的参数加上 `fontIn=body` 才会在响应 体中,加了这个参数会导致返回的 json 会变为以下内容 ```json { \"data\": { // 源数据 }, \"font\": { \"id\":\" 字体的 ID, 通过这个 ID 可以 直接下载字体包 \", \"name\":\" 字体的名字 \", \"token\":\" 字体的令牌 \", } } ``` 4. 如果没有在书籍权限里面添加汉英相关的书籍会返回 `search-book-not-found` 5. 接口有限流所以不能调用太快 

- @summary 查询汉语的英文翻译 

- @param {string} q 要搜索的字 / 词 

- @param {Array<number>} [bookId] 需要搜索的书籍,为空搜索 全部有权限的书籍 

- @param {number} [maxSize] 结果的最大大小 , 最多支持 100 条数据 

- @param {GetChineseEnglishExplainFontInEnum} [fontIn] 字体信 息是否在响应体中 

- @param {*} [options] Override http request option. 

- @throws {RequiredError} 

- @memberof DefaultApi 

*/ 

getChineseEnglishExplain(q: string, bookId?: Array<number>, maxSize?: number, fontIn?: GetChineseEnglishExplainFontInEnum, options?: RawAxiosRequestConfig): 

Promise<axios.AxiosResponse<GetBookEnglishExplain200Response, 

any>>; 

/** 

# * 获取客户端书籍详细列表支持分页查询 

- @summary 获取客户端书籍详细列表 

- @param {string} [name] 书名 

- @param {Set<number>} [categoryId] 书籍分类,支持多个分类 ID ,比如想把父分类的同时查询可以传分类对象里面的 path 数组 

- @param {number} [size] 页的大小 

- @param {number} [page] 页码 

- @param {*} [options] Override http request option. 

- @throws {RequiredError} 

- @memberof DefaultApi 

*/ 

getClientBooks(name?: string, categoryId?: Set<number>, size?: number, page?: number, options?: RawAxiosRequestConfig): Promise<axios.AxiosResponse<PageBookResponse, any>>; 

/** 

* 

- @summary 获取当前客户端信息 

- @param {*} [options] Override http request option. 

- @throws {RequiredError} 

- @memberof DefaultApi 

*/ 

getClientInfo(options?: RawAxiosRequestConfig): Promise<axios.AxiosResponse<ClientResponse, any>>; 

/** 

* 
 1. 接口返回的部分内容是乱码需要下载对应的字体包才能 显示 2. 获取字体令牌和字体名字默认是在响应头中,需要传入在请 求的参数加上 `fontIn=body` 才会在响应体中,加了这个参数会导致 返回的 json 会变为以下内容 ```json { \"data\": { // 源数据 }, \"font\": { \"id\":\" 字体的 ID, 通过这个 ID 可以直接下载字体包 \", \"name\":\" 字 体的名字 \", \"token\":\" 字体的令牌 \", } } ``` 3. 如果没有返回 field 字 段的话 json 对象是直接没有这个 key 而不是会返回 null 4. 默认使用错 词纠错,如果不需要使用纠错请传入 `useCorrect=false` 5. 如果纠错 成功会返回 correctWord 字段,如果没有纠错则不会返回 6. 如果不 传 fields 默认只查询释文和基本信息 , 但是如果没有释文则会从其它索 引中获取 7. 如果不想只加载释文信息需要查询所有功能数据,请直 接指定 fields ,但是这样可能会影响接口的性能,因为如果传入所有 的会导致接口变慢 8. 接口有限流所以不能调用太快 

- @summary 查询字词的内容数据 

- @param {string} q 要查询的文字 

- @param {Set<string>} [fields] 要查询的功能,逗号分隔 eg: shiwen.danzi,shiwen.baike,shici 

- @param {boolean} [useCorrect] 是否使用自动纠错 ,true 使用 ,false 不使用 

- @param {GetContentFontInEnum} [fontIn] 字体信息是否在响应 体中 

- @param {*} [options] Override http request option. 

- @throws {RequiredError} 

- @memberof DefaultApi 

*/ 

getContent(q: string, fields?: Set<string>, useCorrect?: boolean, 

fontIn?: GetContentFontInEnum, options?: RawAxiosRequestConfig): 

Promise<axios.AxiosResponse<GetContent200Response, any>>; 

/** 

* 

- @summary 获取字词的定性语列表 

- @param {string} q 

- @param {*} [options] Override http request option. 

- @throws {RequiredError} 

# * @memberof DefaultApi 

*/ 

getQualitatives(q: string, options?: RawAxiosRequestConfig): Promise<axios.AxiosResponse<Qualitative[], any>>; 

/** 

* 

- @summary 单字详情 

- @param {string} q 

- @param {Set<string>} [strokeFilter] 笔顺过滤器 

- @param {*} [options] Override http request option. 

- @throws {RequiredError} 

- @memberof DefaultApi 

*/ 

getSingleWord(q: string, strokeFilter?: Set<string>, options?: RawAxiosRequestConfig): 

Promise<axios.AxiosResponse<SingleWordBasicResponse, any>>; 

/** 

- 诗词搜索 -- 1.0.3 版本已弃用 

- @param {string} q 要查询的字 / 词 

- @param {number} [page] 页码 

- @param {number} [size] 页的大小 

- @param {*} [options] Override http request option. 

- @throws {RequiredError} 

- @memberof DefaultApi 

*/ 

poetry(q: string, page?: number, size?: number, options?: RawAxiosRequestConfig): 

any>>; 

/** 

- 根据释文模糊搜索得到列表,通过 headword 再调用内容 / 释文接 

- 口。高亮里面包含 text 

# * @summary 模糊搜索释文 

- @param {string} [q] 要搜索的字 / 词 

- @param {number} [textLength] text 最大长度,超出会截取掉 

- @param {number} [size] 页的大小 

- @param {number} [page] 页码 

* @param {Array<number>} [bookId] 需要搜索的书籍,为空搜索 全部有权限的书籍 

- @param {*} [options] Override http request option. 

- @throws {RequiredError} 

- @memberof DefaultApi 

*/ 

searchBookExplain(q?: string, textLength?: number, size?: number, page?: number, bookId?: Array<number>, options?: RawAxiosRequestConfig): 

any>>; 

/** 

- 根据词头模糊搜索得到列表,通过 headword 再调用内容 / 释文接 

- 口。高亮里面包含 headword 、 simplified 

- @summary 根据词头模糊搜索 

- @param {string} [q] 要搜索的字 / 词 

- @param {number} [textLength] text 最大长度,超出会截取掉 

- @param {number} [size] 页的大小 

- @param {number} [page] 页码 

- @param {Array<number>} [bookId] 需要搜索的书籍,为空搜索 全部有权限的书籍 

- @param {*} [options] Override http request option. 

- @throws {RequiredError} 

- @memberof DefaultApi 

*/ 

searchBookExplainByHeadword(q?: string, textLength?: number, size?: number, page?: number, bookId?: Array<number>, options?: RawAxiosRequestConfig): 

any>>; 

/** 

* 

- @summary 历史纪年搜索支持分页 

- @param {string} q 关键字 

- @param {number} [size] 页的大小 

- @param {number} [page] 页码 

- @param {*} [options] Override http request option. 

- @throws {RequiredError} 

- @memberof DefaultApi 

*/ 

searchEpoch(q: string, size?: number, page?: number, options?: RawAxiosRequestConfig): Promise<axios.AxiosResponse<PageEpoch, any>>; 

/** 

* 

- @summary 获取干支下年份 

- @param {string} ganzhi 干支 

- @param {*} [options] Override http request option. 

- @throws {RequiredError} 

- @memberof DefaultApi 

*/ 

searchEpochAdLunarYear(ganzhi: string, options?: RawAxiosRequestConfig): Promise<axios.AxiosResponse<Set<string>, any>>; 

/** 

* 

# * @summary 根据时期获取朝代 

- @param {string} period 时期 

- @param {*} [options] Override http request option. 

- @throws {RequiredError} 

- @memberof DefaultApi 

*/ 

searchEpochDynasty(period: string, options?: RawAxiosRequestConfig): 

Promise<axios.AxiosResponse<EpochDynastyResponse, any>>; 

/** 

* 

# * @summary 根据时期和朝代搜索皇帝 

- @param {string} period 时期 

- @param {string} dynasty 朝代 

- @param {*} [options] Override http request option. 

- @throws {RequiredError} 

- @memberof DefaultApi 

*/ 

searchEpochEmperor(period: string, dynasty: string, options?: RawAxiosRequestConfig): 

Promise<axios.AxiosResponse<EpochEmperorResponse, any>>; 

/** 

* 

# * @summary 部首搜索 

- @param {Array<string>} radical 

- @param {*} [options] Override http request option. 

- @throws {RequiredError} 

# * @memberof DefaultApi 

*/ 

searchSingleWordByRadical(radical: Array<string>, options?: RawAxiosRequestConfig): Promise<axios.AxiosResponse<SingleWordRadicalSearchResponse[], any>>; 

/** 

* 

# * @summary 拼音搜索 

- @param {Array<string>} spell 

- @param {*} [options] Override http request option. 

- @throws {RequiredError} 

# * @memberof DefaultApi 

*/ 

searchSingleWordBySpell(spell: Array<string>, options?: RawAxiosRequestConfig): Promise<axios.AxiosResponse<SingleWordSpellSearchResponse, any>>; 

/** 

* 

# * @summary 根据笔顺搜索 

- @param {string} [stroke] 

- @param {number} [page] Zero-based page index (0..N) 

- @param {number} [size] The size of the page to be return ed 

* @param {Array<string>} [sort] Sorting criteria in the format: property,(asc|desc). Default sort order is ascending. Multiple sort criteria are supported. 

- @param {*} [options] Override http request option. 

- @throws {RequiredError} 

# * @memberof DefaultApi 

*/ 

searchSingleWordByStroke(stroke?: string, page?: number, size?: number, sort?: Array<string>, options?: RawAxiosRequestConfig): Promise<axios.AxiosResponse<PageSingleWord, any>>; 

} 

/** 

# * 诗词模块开放接口 

*/ 

export class PoetryDefaultApi extends BaseAPI { 

/** 

- 通过诗人 id 获取诗人详情信息, id 参数通过搜索诗人获取 

- @summary 诗人详情 

- @param {string} id 诗人 id 

- @param {*} [options] Override http request option. 

- @throws {RequiredError} 

- @memberof DefaultApi 

*/ 

public getPoet(id: string, options?: RawAxiosRequestConfig) { 

return PoetryDefaultApiFp(this.configuration).getPoet(id, options).then((request) => request(this.axios, this.basePath)); 

} 

/** 

- 通过诗词 id 获取诗词详情信息, id 参数通过搜索诗词获取 

- @summary 诗词详情 

- @param {string} id 诗词 id 

- @param {*} [options] Override http request option. 

- @throws {RequiredError} 

- @memberof DefaultApi 

*/ 

public getPoetry(id: string, options?: RawAxiosRequestConfig) { 

return PoetryDefaultApiFp(this.configuration).getPoetry(id, options).then((request) => request(this.axios, this.basePath)); 

} 

/** 

- 通过诗词 id 获取诗词鉴赏信息,诗词 id 参数通过诗词详情获取 

- @summary 诗词鉴赏 

- @param {string} id 诗词 id 

* @param {GetPoetryAppreciationFontInEnum} [fontIn] 字体信息 是否在响应体中 

- @param {*} [options] Override http request option. 

- @throws {RequiredError} 

- @memberof DefaultApi 

*/ 

public getPoetryAppreciation(id: string,fontIn?: GetPoetryAppreciationFontInEnum, options?: RawAxiosRequestConfig) { 

# return 

PoetryDefaultApiFp(this.configuration).getPoetryAppreciation(id,fontIn, options).then((request) => request(this.axios, this.basePath)); 

} 

/** 

- 通过诗词 id 获取诗词译文信息,诗词 id 参数通过诗词详情获取 

- @summary 诗词译文 

- @param {string} id 诗词 id 

- @param {GetPoetryExplainFontInEnum} [fontIn] 字体信息是否在 响应体中 

- @param {*} [options] Override http request option. 

- @throws {RequiredError} 

- @memberof DefaultApi 

*/ 

public getPoetryExplain(id: string,fontIn?: GetPoetryExplainFontInEnum, options?: RawAxiosRequestConfig) { 

return 

PoetryDefaultApiFp(this.configuration).getPoetryExplain(id,fontIn, options).then((request) => request(this.axios, this.basePath)); 

} 

/** 

- 支持通过多个父标签 Id 搜索标签,不传则搜索所有标签 

- @summary 诗词和诗人相关标签 

- @param {Set<number>} [parentIds] 父标签 Id 

- @param {*} [options] Override http request option. 

- @throws {RequiredError} 

- @memberof DefaultApi 

*/ 

public getPoetryTags(parentIds?: Set<number>, options?: RawAxiosRequestConfig) { 

# return 

PoetryDefaultApiFp(this.configuration).getPoetryTags(parentIds, options).then((request) => request(this.axios, this.basePath)); 

} 

/** 

- 支持诗人名字,朝代,标签检索。默认使用 `spell` 拼音正序排序, 

- 同时还支持 `viewTimes` 浏览次数排序 

- @summary 诗人搜索 

- @param {Set<string>} [dynasty] 朝代 

- @param {string} [name] 搜索诗人姓名 

- @param {string} [tags] 多标签搜索 

- @param {number} [page] 页码 

- @param {number} [size] 页面的大小 

- @param {Array<string>} [sort] 排序标准的格式为: property, (asc|desc) 。默认排序顺序为升序。支持多种排序标准 

- @param {*} [options] Override http request option. 

- @throws {RequiredError} 

- @memberof DefaultApi 

*/ 

public searchPoet(dynasty?: Set<string>, name?: string, tags?: string, page?: number|string, size?: number|string, sort?: Array<string>, options?: RawAxiosRequestConfig) { 

return PoetryDefaultApiFp(this.configuration).searchPoet(dynasty, name, tags, page, size, sort, options).then((request) => request(this.axios, this.basePath)); 

} 

/** 

* 
 1. 支持标签需要搜索的标签,支持多个大的标签,每个大 的标签就是一个数组,里面的小标签使用逗号分割,格式为 `tags=tag1,tag2&tags=tag3,tag4`, 2. 诗人 Id, 3. 赏析作者 Id, 4. 根据 关键字全文搜索诗词,支持传入 fields 参数搜索条件,不传则检索所 有字段。 支持字段 : 1. `name` 诗词名字 2. `brandName` 词牌 3. `poetry` 诗文正文 4. `explain` 译文 5. `appreciation` 赏析 5 、默认使 用 `spell` 拼音正序排序,同时还支持 `viewTimes` 浏览次数排序 

- @summary 诗词作品搜索 

- @param {string} [tags] 多标签搜索 

- @param {Set<string>} [appreciationAuthorId] 鉴赏作者 Id 

- @param {Set<string>} [poetryAuthorId] 诗人 Id 

- @param {string} [q] 搜索词 

- @param {Set<SearchPoetryFieldsEnum>} [fields] 指定字段检索 

- @param {number} [page] 页码 

- @param {number} [size] 页面的大小 

- @param {Array<string>} [sort] 排序标准的格式为: property, (asc|desc) 。默认排序顺序为升序。支持多种排序标准 

- @param {*} [options] Override http request option. 

- @throws {RequiredError} 

- @memberof DefaultApi 

*/ 

public searchPoetry(tags?: string, appreciationAuthorId?: Set<string>, poetryAuthorId?: Set<string>, q?: string, fields?: Set<SearchPoetryFieldsEnum>, page?: number|string, size?: number|string, sort?: Array<string>, options?: RawAxiosRequestConfig) { 

return PoetryDefaultApiFp(this.configuration).searchPoetry(tags, appreciationAuthorId, poetryAuthorId, q, fields, page, size, sort, options).then((request) => request(this.axios, this.basePath)); 

} 

} 

``` 

# ## 方法返回对象参数字段说明 

``` 

/** 

- 古今地名 

- @export 

- @interface AncientModernPlaceNameBasicResponse 

*/ 

interface AncientModernPlaceNameBasicResponse { 

/** 

- 古今地名数据列表 

* @type {Array<PlaceName>} 

* @memberof AncientModernPlaceNameBasicResponse 

*/ 

'placeNames'?: Array<PlaceName>; 

} 

/** 

# * 包含后续授权使用的 code 

- @export 

- @interface AuthCodeResponse 

*/ 

interface AuthCodeResponse { 

/** 

# * 授权码 

- @type {string} 

- @memberof AuthCodeResponse 

*/ 

'code'?: string; 

} 

/** 

# * 作者小传 

- @export 

* @interface Author 

*/ 

# interface Author { 

/** 

# * 作者姓名 

- @type {string} 

- @memberof Author 

*/ 

'name'?: string; 

/** 

# * 小传内容 

- @type {string} 

- @memberof Author 

*/ 

'brief'?: string; 

} 

/** 

# * 书籍分类 

- @export 

- @interface BookCategoryResponse 

*/ 

interface BookCategoryResponse { 

/** 

# * 分类 ID 

# * @type {number} 

- @memberof BookCategoryResponse 

*/ 

'id'?: number; 

/** 

# * 分类名字 

- @type {string} 

- @memberof BookCategoryResponse 

*/ 

'name'?: string; 

/** 

# * 分类路径 

- @type {Array<number>} 

- @memberof BookCategoryResponse 

*/ 

'path'?: Array<number>; 

/** 

- 是否有子分类 

- @type {boolean} 

- @memberof BookCategoryResponse 

*/ 

'hasChildren'?: boolean; 

} 

/** 

* 

# * @export 

* @interface BookExplainEnglishResponse 

*/ 

interface BookExplainEnglishResponse { 

/** 

* 

- @type {Array<BookExplainXmlResponse>} 

- @memberof BookExplainEnglishResponse 

*/ 

'entries'?: Array<BookExplainXmlResponse>; 

} 

/** 

* 

# * @export 

* @interface BookExplainExactResponse 

*/ 

interface BookExplainExactResponse { 

/** 

# * 释文列表 

- @type {Array<BookExplainXmlResponse>} 

* @memberof BookExplainExactResponse 

*/ 

'entries'?: Array<BookExplainXmlResponse>; 

/** 

# * 定性语列表 

- @type {Array<Qualitative>} 

- @memberof BookExplainExactResponse 

*/ 

'qualitatives'?: Array<Qualitative>; 

} 

/** 

# * 词条 xml 数据 

- @export 

- @interface BookExplainXmlResponse 

*/ 

interface BookExplainXmlResponse { 

/** 

* 

- @type {number} 

* @memberof BookExplainXmlResponse 

*/ 

'id'?: number; 

/** 

- 词头 

- @type {string} 

- @memberof BookExplainXmlResponse 

*/ 

'headword'?: string; 

/** 

* 释文 xml 

- @type {string} 

- @memberof BookExplainXmlResponse 

*/ 

'xml'?: string; 

/** 

# * 书籍名字 

- @type {string} 

- @memberof BookExplainXmlResponse 

*/ 

'bookName'?: string; 

/** 

* 简体 

* @type {string} 

# * @memberof BookExplainXmlResponse 

*/ 

'simplified'?: string; 

} 

/** 

# * 书籍数据 

- @export 

- @interface BookResponse 

*/ 

interface BookResponse { 

/** 

* 

- @type {number} 

- @memberof BookResponse 

*/ 

'id'?: number; 

/** 

# * 书籍名 

- @type {string} 

- @memberof BookResponse 

*/ 

'name'?: string; 

/** 

# * 图片地址 

- @type {string} 

- @memberof BookResponse 

*/ 

'picture'?: string; 

/** 

- 作者 

- @type {string} 

* @memberof BookResponse 

*/ 

'author'?: string; 

/** 

* ISBN 

- @type {string} 

- @memberof BookResponse 

*/ 

'isbn'?: string; 

/** 

# * 出版社 

* @type {string} 

* @memberof BookResponse 

*/ 

'publishHouse'?: string; 

/** 

# * 出版时间 

- @type {string} 

- @memberof BookResponse 

*/ 

'publishTime'?: string; 

/** 

* 字数 

- @type {number} 

- @memberof BookResponse 

*/ 

'wordNum'?: number; 

} 

/** 

* 

* @export 

* @interface CalligraphyResponseItem 

*/ 

interface CalligraphyResponseItem { 

/** 

# * 作者 

* @type {string} 

* @memberof CalligraphyResponseItem 

*/ 

'author'?: string; 

/** 

# * 朝代 

- @type {string} 

- @memberof CalligraphyResponseItem 

*/ 

'dynasty'?: string; 

/** 

# * 书法组名称 

- @type {string} 

- @memberof CalligraphyResponseItem 

*/ 

'groupName'?: CalligraphyResponseItemGroupNameEnum; 

/** 

- 出处 

- @type {string} 

* @memberof CalligraphyResponseItem 

*/ 

'source'?: string; 

/** 

# * 书法分类 

- @type {string} 

* @memberof CalligraphyResponseItem 

*/ 

'classification'?: string; 

/** 

* 字体 

- @type {string} 

* @memberof CalligraphyResponseItem 

*/ 

'font'?: string; 

/** 

# * 图片路径 

* @type {string} 

# * @memberof CalligraphyResponseItem 

*/ 

'img'?: string; 

} 

declare const CalligraphyResponseItemGroupNameEnum: { 

readonly 1: " 篆书 "; 

readonly 2: " 隶书 "; 

readonly 3: " 楷书 "; 

readonly 4: " 草书 "; 

readonly 5: " 行书 "; 

}; 

type CalligraphyResponseItemGroupNameEnum = typeof CalligraphyResponseItemGroupNameEnum[keyof typeof CalligraphyResponseItemGroupNameEnum]; 

/** 

# * 书籍数据 

- @export 

- @interface ClientBookResponse 

*/ 

interface ClientBookResponse { 

/** 

- 书籍 ID ,可以在搜索的时候限定该书 

- @type {number} 

- @memberof ClientBookResponse 

*/ 

'id'?: number; 

/** 

- 书籍名 

# * @type {string} 

# * @memberof ClientBookResponse 

*/ 

'name'?: string; 

} 

/** 

# * 客户端配置 

# * @export 

- @interface ClientResponse 

*/ 

interface ClientResponse { 

/** 

# * 功能 

- @type {{ [key: string]: string; }} 

- @memberof ClientResponse 

*/ 

'fields'?: { 

[key: string]: string; 

}; 

/** 

# * 书籍 

* @type {Array<ClientBookResponse>} 

# * @memberof ClientResponse 

*/ 

'books'?: Array<ClientBookResponse>; 

} 

/** 

* 

* @export 

- @interface ContentCalligraphyResponse 

*/ 

interface ContentCalligraphyResponse { 

/** 

* 

- @type {ContentCalligraphyResponseFields} 

- @memberof ContentCalligraphyResponse 

*/ 

'fields'?: ContentCalligraphyResponseFields; 

/** 

* 

- @type {Array<CalligraphyResponseItem>} 

- @memberof ContentCalligraphyResponse 

*/ 

'zhuanshu'?: Array<CalligraphyResponseItem>; 

/** 

* 

* @type {Array<CalligraphyResponseItem>} 

- @memberof ContentCalligraphyResponse 

*/ 

'lishu'?: Array<CalligraphyResponseItem>; 

/** 

* 

- @type {Array<CalligraphyResponseItem>} 

- @memberof ContentCalligraphyResponse 

*/ 

'kaishu'?: Array<CalligraphyResponseItem>; 

/** 

* 

- @type {Array<CalligraphyResponseItem>} 

- @memberof ContentCalligraphyResponse 

*/ 

'caoshu'?: Array<CalligraphyResponseItem>; 

/** 

* 

- @type {Array<CalligraphyResponseItem>} 

- @memberof ContentCalligraphyResponse 

*/ 

'xingshu'?: Array<CalligraphyResponseItem>; 

} 

/** 

# * 字段信息 

# * @export 

* @interface ContentCalligraphyResponseFields 

*/ 

interface ContentCalligraphyResponseFields { 

/** 

* 

# * @type {string} 

- @memberof ContentCalligraphyResponseFields 

*/ 

'zhuanshu'?: string; 

/** 

* 

* @type {string} 

* @memberof ContentCalligraphyResponseFields 

*/ 

'lishu'?: string; 

/** 

* 

# * @type {string} 

# * @memberof ContentCalligraphyResponseFields 

*/ 

'kaishu'?: string; 

/** 

* 

* @type {string} 

- @memberof ContentCalligraphyResponseFields 

*/ 

'caoshu'?: string; 

/** 

* 

* @type {string} 

* @memberof ContentCalligraphyResponseFields 

*/ 

'xingshu'?: string; 

} 

/** 

# * 释文详情 

- @export 

* @interface ContentExplainResponse 

*/ 

interface ContentExplainResponse { 

/** 

* 单字 

- @type {string} 

- @memberof ContentExplainResponse 

*/ 

'danzi'?: string; 

/** 

- 语词 

- @type {string} 

- @memberof ContentExplainResponse 

*/ 

'yuci'?: string; 

/** 

# * 百科 

- @type {string} 

- @memberof ContentExplainResponse 

*/ 

'baike'?: string; 

/** 

# * 字段信息 

# * @type {{ [key: string]: string; }} 

# * @memberof ContentExplainResponse 

*/ 

'fields'?: { 

[key: string]: string; 

}; 

} 

/** 

# * 基本信息 

- @export 

- @interface ContentInfoResponse 

*/ 

interface ContentInfoResponse { 

/** 

# * 字段信息 

- @type {{ [key: string]: string; }} 

# * @memberof ContentInfoResponse 

*/ 

'fields'?: { 

[key: string]: string; 

}; 

/** 

* 

# * @type {InfoDanzi} 

# * @memberof ContentInfoResponse 

*/ 

'danzi'?: InfoDanzi; 

} 

/** 

* 

# * @export 

- @interface ContentOriginResponse 

*/ 

interface ContentOriginResponse { 

/** 

* 

- @type {ContentOriginResponseFields} 

- @memberof ContentOriginResponse 

*/ 

'fields'?: ContentOriginResponseFields; 

/** 

# * 说文 

- @type {Array<OriginResponseItem>} 

- @memberof ContentOriginResponse 

*/ 

'shuowen'?: Array<OriginResponseItem>; 

/** 

# * 殷商 

- @type {Array<OriginResponseItem>} 

- @memberof ContentOriginResponse 

*/ 

'yinshang'?: Array<OriginResponseItem>; 

/** 

# * 西周 

- @type {Array<OriginResponseItem>} 

- @memberof ContentOriginResponse 

*/ 

'xizhou'?: Array<OriginResponseItem>; 

/** 

# * 春秋 

- @type {Array<OriginResponseItem>} 

- @memberof ContentOriginResponse 

*/ 

'chunqiu'?: Array<OriginResponseItem>; 

/** 

- 战国 

* @type {Array<OriginResponseItem>} 

* @memberof ContentOriginResponse 

*/ 

'zhanguo'?: Array<OriginResponseItem>; 

} 

/** 

# * 字段信息 

* @export 

- @interface ContentOriginResponseFields 

*/ 

interface ContentOriginResponseFields { 

/** 

* 

- @type {string} 

- @memberof ContentOriginResponseFields 

*/ 

'yinshang'?: string; 

/** 

* 

- @type {string} 

- @memberof ContentOriginResponseFields 

*/ 

'xizhou'?: string; 

/** 

* 

* @type {string} 

* @memberof ContentOriginResponseFields 

*/ 

'chunqiu'?: string; 

/** 

* 

* @type {string} 

* @memberof ContentOriginResponseFields 

*/ 

'zhanguo'?: string; 

} 

/** 

* 

* @export 

* @interface ContentProtectResponse 

*/ 

interface ContentProtectResponse { 

/** 

* 字体的 ID, 通过这个 ID 可以直接下载字体包 

* @type {string} 

# * @memberof ContentProtectResponse 

*/ 

'id'?: string; 

/** 

# * 字体的名字 

- @type {string} 

- @memberof ContentProtectResponse 

*/ 

'name'?: string; 

/** 

# * 字体的令牌 

- @type {string} 

- @memberof ContentProtectResponse 

*/ 

'token'?: string; 

} 

/** 

# * 数据详情 

- @export 

- @interface ContentResponse 

*/ 

interface ContentResponse { 

/** 

# * 字段信息 

- @type {{ [key: string]: string; }} 

- @memberof ContentResponse 

*/ 

'fields'?: { 

[key: string]: string; 

}; 

/** 

# * 搜索的原始文字 

- @type {string} 

- @memberof ContentResponse 

*/ 

'query'?: string; 

/** 

# * 纠错后的文字 

- @type {string} 

- @memberof ContentResponse 

*/ 

- 'correctWord'?: string; 

/** 

* 

# * @type {ContentInfoResponse} 

* @memberof ContentResponse 

*/ 

'info'?: ContentInfoResponse; 

/** 

# * 懒加载字段 

- @type {Array<string>} 

- @memberof ContentResponse 

*/ 

'lazyFields'?: Array<string>; 

/** 

* 

- @type {ContentExplainResponse} 

- @memberof ContentResponse 

*/ 

'shiwen'?: ContentExplainResponse; 

/** 

* 

- @type {ContentCalligraphyResponse} 

- @memberof ContentResponse 

*/ 

'shufa'?: ContentCalligraphyResponse; 

/** 

* 

# * @type {ContentOriginResponse} 

- @memberof ContentResponse 

*/ 

'yuanliu'?: ContentOriginResponse; 

/** 

# * 唐诗宋词 

- @type {Array<Poetry>} 

- @memberof ContentResponse 

*/ 

'shici'?: Array<Poetry>; 

/** 

# * 同义词 

- @type {Array<string>} 

# * @memberof ContentResponse 

*/ 

'tongyici'?: Array<string>; 

/** 

# * 近义词 

- @type {Array<string>} 

# * @memberof ContentResponse 

*/ 

'jinyici'?: Array<string>; 

/** 

# * 反义词 

- @type {Array<string>} 

- @memberof ContentResponse 

*/ 

'fanyici'?: Array<string>; 

} 

/** 

* 

# * @export 

- @interface CustomSearchHitSearchPageableResponse 

*/ 

interface CustomSearchHitSearchPageableResponse { 

/** 

* 

- @type {SearchPageableResponse} 

- @memberof CustomSearchHitSearchPageableResponse 

*/ 

'content'?: SearchPageableResponse; 

/** 

# * 高亮 

- @type {{ [key: string]: Array<string>; }} 

- @memberof CustomSearchHitSearchPageableResponse 

*/ 

- 'highlights'?: { 

[key: string]: Array<string>; 

}; 

} 

/** 

* 

# * @export 

- @interface CustomSearchHitSearchPoetryResponse 

*/ 

interface CustomSearchHitSearchPoetryResponse { 

/** 

* 

- @type {SearchPoetryResponse} 

- @memberof CustomSearchHitSearchPoetryResponse 

*/ 

'content'?: SearchPoetryResponse; 

/** 

# * 高亮 

- @type {{ [key: string]: Array<string>; }} 

- @memberof CustomSearchHitSearchPoetryResponse 

*/ 

'highlights'?: { 

[key: string]: Array<string>; 

}; 

} 

/** 

# * 单字数据 

- @export 

- @interface Data 

*/ 

interface Data { 

/** 

* 

- @type {number} 

- @memberof Data 

*/ 

'id'?: number; 

/** 

* 文字 

* @type {string} 

* @memberof Data 

*/ 

'word'?: string; 

/** 

# * 部首 

- @type {string} 

- @memberof Data 

*/ 

'radical'?: string; 

/** 

- 笔画 

- @type {number} 

- @memberof Data 

*/ 

'periodNum'?: number; 

/** 

* 

- @type {string} 

- @memberof Data 

*/ 

'wordNum'?: string; 

/** 

# * 拼音 

- @type {string} 

- @memberof Data 

*/ 

'spell'?: string; 

/** 

# * 笔顺 

- @type {string} 

- @memberof Data 

*/ 

'chapterOrder'?: string; 

/** 

# * 结构 

- @type {string} 

- @memberof Data 

*/ 

'structure'?: string; 

} 

/** 

# * 朝代数据 

* @export 

# * @interface Dynasty 

*/ 

interface Dynasty { 

/** 

# * 朝代 

- @type {string} 

- @memberof Dynasty 

*/ 

'dynasty'?: string; 

/** 

- 公元年 

- @type {string} 

- @memberof Dynasty 

*/ 

'adLunarYear'?: string; 

} 

/** 

- 皇帝数据 

- @export 

- @interface Emperor 

*/ 

interface Emperor { 

/** 

* 帝号 

- @type {string} 

* @memberof Emperor 

*/ 

'diHao'?: string; 

/** 

# * 皇帝名称 

- @type {string} 

* @memberof Emperor 

*/ 

'emperor'?: string; 

} 

/** 

* 

* @export 

- @interface Epoch 

*/ 

interface Epoch { 

/** 

* 

* @type {string} 

* @memberof Epoch 

*/ 

'adLunarYear'?: string; 

/** 

* 

* @type {string} 

* @memberof Epoch 

*/ 

'ganzhi'?: string; 

/** 

* 

* @type {string} 

* @memberof Epoch 

*/ 

'period'?: string; 

/** 

* 

* @type {string} 

* @memberof Epoch 

*/ 

'dynasty'?: string; 

/** 

* 

* @type {string} 

* @memberof Epoch 

*/ 

'diHao'?: string; 

/** 

* 

- @type {string} 

* @memberof Epoch 

*/ 

'emperor'?: string; 

/** 

* 

* @type {string} 

* @memberof Epoch 

*/ 

'years'?: string; 

/** 

* 

* @type {string} 

* @memberof Epoch 

*/ 

'country'?: string; 

/** 

* 

* @type {string} 

* @memberof Epoch 

*/ 

'nianHao'?: string; 

/** 

* 

* @type {string} 

* @memberof Epoch 

*/ 

'nianHao1'?: string; 

/** 

* 

* @type {string} 

* @memberof Epoch 

*/ 

'nianHao2'?: string; 

/** 

* 

* @type {number} 

# * @memberof Epoch 

*/ 

'sort'?: number; 

/** 

* 

* @type {number} 

* @memberof Epoch 

*/ 

'id'?: number; 

} 

/** 

# * 历史纪年换算 

* @export 

* @interface EpochConversionResponse 

*/ 

interface EpochConversionResponse { 

/** 

# * 历史纪年数据 

- @type {Array<Epoch>} 

- @memberof EpochConversionResponse 

*/ 

'epochs'?: Array<Epoch>; 

} 

/** 

* 

# * @export 

* @interface EpochDynastyResponse 

*/ 

interface EpochDynastyResponse { 

/** 

# * 朝代数据 

- @type {Array<Dynasty>} 

- @memberof EpochDynastyResponse 

*/ 

'dynasties'?: Array<Dynasty>; 

} 

/** 

* 

# * @export 

* @interface EpochEmperorResponse 

*/ 

interface EpochEmperorResponse { 

/** 

# * 皇帝数据 

* @type {Array<Emperor>} 

# * @memberof EpochEmperorResponse 

*/ 

'emperors'?: Array<Emperor>; 

} 

/** 

- @type GetAncientAndModernPlaceName200Response 

* @export 

*/ 

type GetAncientAndModernPlaceName200Response = AncientModernPlaceNameBasicResponse | GetAncientAndModernPlaceName200ResponseOneOf; 

/** 

* 

- @export 

- @interface GetAncientAndModernPlaceName200ResponseOneOf 

*/ 

interface GetAncientAndModernPlaceName200ResponseOneOf { 

/** 

* 

- @type {AncientModernPlaceNameBasicResponse} 

- @memberof GetAncientAndModernPlaceName200ResponseOneOf 

*/ 

'data'?: AncientModernPlaceNameBasicResponse; 

/** 

* 

# * @type {ContentProtectResponse} 

* @memberof GetAncientAndModernPlaceName200ResponseOneOf 

*/ 

'font'?: ContentProtectResponse; 

} 

/** 

- @type GetBookEnglishExplain200Response 

- @export 

*/ 

type GetBookEnglishExplain200Response = BookExplainEnglishResponse | GetBookEnglishExplain200ResponseOneOf; 

/** 

* 

# * @export 

- @interface GetBookEnglishExplain200ResponseOneOf 

*/ 

interface GetBookEnglishExplain200ResponseOneOf { 

/** 

* 

- @type {BookExplainEnglishResponse} 

- @memberof GetBookEnglishExplain200ResponseOneOf 

*/ 

'data'?: BookExplainEnglishResponse; 

/** 

* 

- @type {ContentProtectResponse} 

- @memberof GetBookEnglishExplain200ResponseOneOf 

*/ 

'font'?: ContentProtectResponse; 

} 

/** 

- @type GetBookExplain200Response 

- @export 

*/ 

type GetBookExplain200Response = BookExplainExactResponse | GetBookExplain200ResponseOneOf; 

/** 

* 

* @export 

- @interface GetBookExplain200ResponseOneOf 

*/ 

interface GetBookExplain200ResponseOneOf { 

/** 

* 

* @type {BookExplainExactResponse} 

* @memberof GetBookExplain200ResponseOneOf 

*/ 

'data'?: BookExplainExactResponse; 

/** 

* 

- @type {ContentProtectResponse} 

- @memberof GetBookExplain200ResponseOneOf 

*/ 

'font'?: ContentProtectResponse; 

} 

/** 

* @type GetContent200Response 

- @export 

*/ 

type GetContent200Response = ContentResponse | GetContent200ResponseOneOf; 

/** 

* 

# * @export 

* @interface GetContent200ResponseOneOf 

*/ 

interface GetContent200ResponseOneOf { 

/** 

* 

- @type {ContentResponse} 

- @memberof GetContent200ResponseOneOf 

*/ 

'data'?: ContentResponse; 

/** 

* 

- @type {ContentProtectResponse} 

- @memberof GetContent200ResponseOneOf 

*/ 

'font'?: ContentProtectResponse; 

} 

/** 

* 单字 

- @export 

* @interface InfoDanzi 

*/ 

interface InfoDanzi { 

/** 

# * 部首 

- @type {string} 

- @memberof InfoDanzi 

*/ 

'radical'?: string; 

/** 

# * 笔画数 

- @type {number} 

- @memberof InfoDanzi 

*/ 

'strokes'?: number; 

/** 

* 

* @type {StrokeGif} 

* @memberof InfoDanzi 

*/ 

'strokeGif'?: StrokeGif; 

} 

/** 

* 

# * @export 

* @interface OriginResponseItem 

*/ 

interface OriginResponseItem { 

/** 

# * 字体类型 

- @type {string} 

- @memberof OriginResponseItem 

*/ 

'fontType'?: string; 

/** 

# * 类型分类 

- @type {string} 

- @memberof OriginResponseItem 

*/ 

'typeClassification'?: OriginResponseItemTypeClassificationEnum; 

/** 

- 文字类型 

- @type {string} 

- @memberof OriginResponseItem 

*/ 

'textType'?: string; 

/** 

* 出处 

- @type {string} 

* @memberof OriginResponseItem 

*/ 

'source'?: string; 

/** 

* 时代 

- @type {string} 

* @memberof OriginResponseItem 

*/ 

'era'?: string; 

/** 

# * 提供者 

* @type {string} 

* @memberof OriginResponseItem 

*/ 

'provider'?: string; 

/** 

# * 字编码 

* @type {string} 

# * @memberof OriginResponseItem 

*/ 

'wordCode'?: string; 

/** 

# * 字形 

* @type {string} 

* @memberof OriginResponseItem 

*/ 

'font'?: string; 

/** 

# * 图片路径 

* @type {string} 

* @memberof OriginResponseItem 

*/ 

'img'?: string; 

} 

declare const OriginResponseItemTypeClassificationEnum: { 

readonly 1: " 说文 "; 

readonly 2: " 殷商 "; 

readonly 3: " 西周 "; 

readonly 4: " 春秋 "; readonly 5: " 战国 "; 

}; 

type OriginResponseItemTypeClassificationEnum = typeof OriginResponseItemTypeClassificationEnum[keyof typeof OriginResponseItemTypeClassificationEnum]; 

/** 

* 

* @export 

- @interface PageBookCategoryResponse 

*/ 

interface PageBookCategoryResponse { 

/** 

* 

- @type {number} 

- @memberof PageBookCategoryResponse 

*/ 

'totalElements'?: number; 

/** 

* 

* @type {number} 

- @memberof PageBookCategoryResponse 

*/ 

'totalPages'?: number; 

/** 

* 

# * @type {number} 

* @memberof PageBookCategoryResponse 

*/ 

'size'?: number; 

/** 

* 

- @type {Array<BookCategoryResponse>} 

* @memberof PageBookCategoryResponse 

*/ 

'content'?: Array<BookCategoryResponse>; 

/** 

* 

* @type {number} 

- @memberof PageBookCategoryResponse 

*/ 

'number'?: number; 

/** 

* 

* @type {SortObject} 

* @memberof PageBookCategoryResponse 

*/ 

'sort'?: SortObject; 

/** 

* 

* @type {boolean} 

* @memberof PageBookCategoryResponse 

*/ 

'first'?: boolean; 

/** 

* 

* @type {boolean} 

* @memberof PageBookCategoryResponse 

*/ 

'last'?: boolean; 

/** 

* 

* @type {number} 

* @memberof PageBookCategoryResponse 

*/ 

'numberOfElements'?: number; 

/** 

* 

* @type {PageableObject} 

# * @memberof PageBookCategoryResponse 

*/ 

'pageable'?: PageableObject; 

/** 

* 

* @type {boolean} 

* @memberof PageBookCategoryResponse 

*/ 

'empty'?: boolean; 

} 

/** 

* 

# * @export 

* @interface PageBookResponse 

*/ 

interface PageBookResponse { 

/** 

* 

* @type {number} 

* @memberof PageBookResponse 

*/ 

# 'totalElements'?: number; 

/** 

* 

* @type {number} 

* @memberof PageBookResponse 

*/ 

'totalPages'?: number; 

/** 

* 

* @type {number} 

* @memberof PageBookResponse 

*/ 

'size'?: number; 

/** 

* 

* @type {Array<BookResponse>} 

* @memberof PageBookResponse 

*/ 

'content'?: Array<BookResponse>; 

/** 

* 

* @type {number} 

* @memberof PageBookResponse 

*/ 

'number'?: number; 

/** 

* 

* @type {SortObject} 

* @memberof PageBookResponse 

*/ 

'sort'?: SortObject; 

/** 

* 

* @type {boolean} 

* @memberof PageBookResponse 

*/ 

'first'?: boolean; 

/** 

* 

* @type {boolean} 

* @memberof PageBookResponse 

*/ 

'last'?: boolean; 

/** 

* 

# * @type {number} 

* @memberof PageBookResponse 

*/ 

'numberOfElements'?: number; 

/** 

* 

- @type {PageableObject} 

- @memberof PageBookResponse 

*/ 

'pageable'?: PageableObject; 

/** 

* 

- @type {boolean} 

- @memberof PageBookResponse 

*/ 

'empty'?: boolean; 

} 

/** 

* 

- @export 

* @interface PageCustomSearchHitSearchPageableResponse 

*/ 

interface PageCustomSearchHitSearchPageableResponse { 

/** 

* 

* @type {number} 

- @memberof PageCustomSearchHitSearchPageableResponse 

*/ 

'totalElements'?: number; 

/** 

* 

- @type {number} 

- @memberof PageCustomSearchHitSearchPageableResponse 

*/ 

'totalPages'?: number; 

/** 

* 

- @type {number} 

- @memberof PageCustomSearchHitSearchPageableResponse 

*/ 

'size'?: number; 

/** 

* 

- @type {Array<CustomSearchHitSearchPageableResponse>} 

- @memberof PageCustomSearchHitSearchPageableResponse 

*/ 

'content'?: Array<CustomSearchHitSearchPageableResponse>; 

/** 

* 

- @type {number} 

- @memberof PageCustomSearchHitSearchPageableResponse 

*/ 

'number'?: number; 

/** 

* 

- @type {SortObject} 

- @memberof PageCustomSearchHitSearchPageableResponse 

*/ 

'sort'?: SortObject; 

/** 

* 

- @type {boolean} 

- @memberof PageCustomSearchHitSearchPageableResponse 

*/ 

'first'?: boolean; 

/** 

* 

* @type {boolean} 

* @memberof PageCustomSearchHitSearchPageableResponse 

*/ 

'last'?: boolean; 

/** 

* 

- @type {number} 

- @memberof PageCustomSearchHitSearchPageableResponse 

*/ 

'numberOfElements'?: number; 

/** 

* 

* @type {PageableObject} 

- @memberof PageCustomSearchHitSearchPageableResponse 

*/ 

'pageable'?: PageableObject; 

/** 

* 

* @type {boolean} 

* @memberof PageCustomSearchHitSearchPageableResponse 

*/ 

'empty'?: boolean; 

} 

/** 

* 

* @export 

* @interface PageCustomSearchHitSearchPoetryResponse 

*/ 

interface PageCustomSearchHitSearchPoetryResponse { /** 

* 

* @type {number} 

* @memberof PageCustomSearchHitSearchPoetryResponse 

*/ 

'totalElements'?: number; 

/** 

* 

* @type {number} 

* @memberof PageCustomSearchHitSearchPoetryResponse 

*/ 

'totalPages'?: number; 

/** 

* 

# * @type {number} 

* @memberof PageCustomSearchHitSearchPoetryResponse 

*/ 

'size'?: number; 

/** 

* 

- @type {Array<CustomSearchHitSearchPoetryResponse>} 

- @memberof PageCustomSearchHitSearchPoetryResponse 

*/ 

'content'?: Array<CustomSearchHitSearchPoetryResponse>; 

/** 

* 

# * @type {number} 

- @memberof PageCustomSearchHitSearchPoetryResponse 

*/ 

'number'?: number; 

/** 

* 

* @type {SortObject} 

* @memberof PageCustomSearchHitSearchPoetryResponse 

*/ 

'sort'?: SortObject; 

/** 

* 

* @type {boolean} 

* @memberof PageCustomSearchHitSearchPoetryResponse 

*/ 

'first'?: boolean; 

/** 

* 

- @type {boolean} 

- @memberof PageCustomSearchHitSearchPoetryResponse 

*/ 

'last'?: boolean; 

/** 

* 

- @type {number} 

- @memberof PageCustomSearchHitSearchPoetryResponse 

*/ 

'numberOfElements'?: number; 

/** 

* 

* @type {PageableObject} 

* @memberof PageCustomSearchHitSearchPoetryResponse 

*/ 

'pageable'?: PageableObject; 

/** 

* 

* @type {boolean} 

* @memberof PageCustomSearchHitSearchPoetryResponse 

*/ 

'empty'?: boolean; 

} 

/** 

* 

* @export 

* @interface PageEpoch 

*/ 

interface PageEpoch { 

/** 

* 

* @type {number} 

* @memberof PageEpoch 

*/ 

'totalElements'?: number; 

/** 

* 

* @type {number} 

* @memberof PageEpoch 

*/ 

'totalPages'?: number; 

/** 

* 

* @type {number} 

* @memberof PageEpoch 

*/ 

'size'?: number; 

/** 

* 

* @type {Array<Epoch>} 

* @memberof PageEpoch 

*/ 

'content'?: Array<Epoch>; 

/** 

* 

* @type {number} 

* @memberof PageEpoch 

*/ 

'number'?: number; 

/** 

* 

* @type {SortObject} 

* @memberof PageEpoch 

*/ 

'sort'?: SortObject; 

/** 

* 

* @type {boolean} 

* @memberof PageEpoch 

*/ 

'first'?: boolean; 

/** 

* 

* @type {boolean} 

* @memberof PageEpoch 

*/ 

'last'?: boolean; 

/** 

* 

* @type {number} 

# * @memberof PageEpoch 

*/ 

'numberOfElements'?: number; 

/** 

* 

- @type {PageableObject} 

- @memberof PageEpoch 

*/ 

'pageable'?: PageableObject; 

/** 

* 

- @type {boolean} 

- @memberof PageEpoch 

*/ 

'empty'?: boolean; 

} 

/** 

* 

- @export 

* @interface PageSingleWord 

*/ 

interface PageSingleWord { 

/** 

* 

* @type {number} 

* @memberof PageSingleWord 

*/ 

'totalElements'?: number; 

/** 

* 

- @type {number} 

* @memberof PageSingleWord 

*/ 

'totalPages'?: number; 

/** 

* 

* @type {number} 

* @memberof PageSingleWord 

*/ 

'size'?: number; 

/** 

* 

* @type {Array<SingleWord>} 

* @memberof PageSingleWord 

*/ 

'content'?: Array<SingleWord>; 

/** 

* 

* @type {number} 

* @memberof PageSingleWord 

*/ 

'number'?: number; 

/** 

* 

* @type {SortObject} 

* @memberof PageSingleWord 

*/ 

'sort'?: SortObject; 

/** 

* 

* @type {boolean} 

* @memberof PageSingleWord 

*/ 

'first'?: boolean; 

/** 

* 

# * @type {boolean} 

* @memberof PageSingleWord 

*/ 

'last'?: boolean; 

/** 

* 

* @type {number} 

* @memberof PageSingleWord 

*/ 

'numberOfElements'?: number; 

/** 

* 

* @type {PageableObject} 

* @memberof PageSingleWord 

*/ 

'pageable'?: PageableObject; 

/** 

* 

* @type {boolean} 

* @memberof PageSingleWord 

*/ 

'empty'?: boolean; 

} 

/** 

* 

* @export 

- @interface PageableObject 

*/ 

interface PageableObject { 

/** 

* 

- @type {number} 

- @memberof PageableObject 

*/ 

'offset'?: number; 

/** 

* 

* @type {SortObject} 

* @memberof PageableObject 

*/ 

'sort'?: SortObject; 

/** 

* 

* @type {number} 

* @memberof PageableObject 

*/ 

'pageSize'?: number; 

/** 

* 

* @type {number} 

* @memberof PageableObject 

*/ 

'pageNumber'?: number; 

/** 

* 

- @type {boolean} 

* @memberof PageableObject 

*/ 

'unpaged'?: boolean; 

/** 

* 

- @type {boolean} 

* @memberof PageableObject 

*/ 

'paged'?: boolean; 

} 

/** 

# * 古今地名数据列表 

- @export 

- @interface PlaceName 

*/ 

interface PlaceName { 

/** 

- 古地名 

- @type {string} 

- @memberof PlaceName 

*/ 

'ancientName'?: string; 

/** 

- 年代 

- @type {string} 

- @memberof PlaceName 

*/ 

'era'?: string; 

/** 

- 历史变迁 

- @type {string} 

* @memberof PlaceName 

*/ 

'evolutionChange'?: string; 

/** 

# * 废弃记录 

- @type {string} 

- @memberof PlaceName 

*/ 

'abandonName'?: string; 

/** 

* 地区 

- @type {string} 

* @memberof PlaceName 

*/ 

'area'?: string; 

/** 

# * 现用名 

- @type {string} 

- @memberof PlaceName 

*/ 

'todayName'?: string; 

/** 

* 现用名 1 

- @type {string} 

- @memberof PlaceName 

*/ 

'todayName1'?: string; 

/** 

# * 现治所 

- @type {string} 

- @memberof PlaceName 

*/ 

'todayAdministrative'?: string; 

} 

/** 

# * 唐诗宋词详情 

- @export 

- @interface Poetry 

*/ 

interface Poetry { 

/** 

# * 唐诗宋词名 

- @type {string} 

* @memberof Poetry 

*/ 

'name'?: string; 

/** 

# * 词牌说明 

- @type {string} 

- @memberof Poetry 

*/ 

'brandName'?: string; 

/** 

# * 宋词词序 

- @type {string} 

- @memberof Poetry 

*/ 

'wordOrder'?: string; 

/** 

- 诗文词文 

- @type {string} 

- @memberof Poetry 

*/ 

'content'?: string; 

/** 

* 注释 

* @type {string} 

* @memberof Poetry 

*/ 

'annotation'?: string; 

/** 

* 赏析 

- @type {string} 

* @memberof Poetry 

*/ 

'appreciation'?: string; 

/** 

- 赏析作者 

- @type {string} 

- @memberof Poetry 

*/ 

'appreciationAuthor'?: string; 

/** 

* 

- @type {Author} 

- @memberof Poetry 

*/ 

'author'?: Author; 

} 

/** 

* 

# * @export 

- @interface Qualitative 

*/ 

interface Qualitative { 

/** 

- 词头 

- @type {string} 

- @memberof Qualitative 

*/ 

'headword'?: string; 

/** 

# * 定性语名字 

- @type {string} 

- @memberof Qualitative 

*/ 

'name'?: string; 

/** 

# * 定性语 

- @type {number} 

* @memberof Qualitative 

*/ 

'qualitative'?: number; 

/** 

# * 词头类型 

- @type {string} 

- @memberof Qualitative 

*/ 

'entryType'?: QualitativeEntryTypeEnum; 

/** 

* 拼音 

* @type {string} 

* @memberof Qualitative 

*/ 

'spell'?: string; 

} 

declare const QualitativeEntryTypeEnum: { 

readonly Words: "WORDS"; 

readonly Encyclopedia: "ENCYCLOPEDIA"; 

readonly Epoch: "EPOCH"; 

readonly PlaceName: "PLACE_NAME"; 

readonly English: "ENGLISH"; 

readonly Synonym: "Synonym"; 

readonly ChineseEnglish: "CHINESE_ENGLISH"; 

}; 

type QualitativeEntryTypeEnum = typeof QualitativeEntryTypeEnum[keyof typeof QualitativeEntryTypeEnum]; 

/** 

# * 搜索结果 

- @export 

- @interface SearchPageableResponse 

*/ 

interface SearchPageableResponse { 

/** 

- 词头 

- @type {string} 

- @memberof SearchPageableResponse 

*/ 

'headword'?: string; 

/** 

- 书名 

- @type {string} 

- @memberof SearchPageableResponse 

*/ 

'bookName'?: string; 

/** 

# * 书籍 id 

- @type {number} 

- @memberof SearchPageableResponse 

*/ 

'bookId'?: number; 

/** 

# * 简体 

- @type {string} 

- @memberof SearchPageableResponse 

*/ 

- 'simplified'?: string; 

/** 

# * 简单释文 

- @type {string} 

- @memberof SearchPageableResponse 

*/ 

'text'?: string; 

} 

/** 

* 内容 

- @export 

# * @interface SearchPoetryResponse 

*/ 

interface SearchPoetryResponse { 

/** 

# * 唐诗宋词名 

- @type {string} 

- @memberof SearchPoetryResponse 

*/ 

'name'?: string; 

/** 

# * 词牌说明 

- @type {string} 

- @memberof SearchPoetryResponse 

*/ 

'brandName'?: string; 

/** 

# * 宋词词序 

- @type {string} 

- @memberof SearchPoetryResponse 

*/ 

'wordOrder'?: string; 

/** 

# * 作者 

* @type {string} 

* @memberof SearchPoetryResponse 

*/ 

'authorName'?: string; 

/** 

# * 诗文词文 

- @type {string} 

* @memberof SearchPoetryResponse 

*/ 

'content'?: string; 

/** 

# * 注释 

- @type {string} 

- @memberof SearchPoetryResponse 

*/ 

'annotation'?: string; 

/** 

* 赏析 

- @type {string} 

* @memberof SearchPoetryResponse 

*/ 

'appreciation'?: string; 

/** 

# * 赏析作者 

* @type {string} 

* @memberof SearchPoetryResponse 

*/ 

'appreciationAuthor'?: string; 

} 

/** 

* 

* @export 

* @interface SingleWord 

*/ 

interface SingleWord { 

/** 

* 

* @type {number} 

* @memberof SingleWord 

*/ 

'id'?: number; 

/** 

* 

# * @type {string} 

# * @memberof SingleWord 

*/ 

'word'?: string; 

/** 

* 

* @type {string} 

* @memberof SingleWord 

*/ 

'radical'?: string; 

/** 

* 

* @type {string} 

* @memberof SingleWord 

*/ 

'level'?: string; 

/** 

* 

* @type {number} 

* @memberof SingleWord 

*/ 

'periodNum'?: number; 

/** 

* 

* @type {string} 

* @memberof SingleWord 

*/ 

'wordNum'?: string; 

/** 

* 

* @type {string} 

* @memberof SingleWord 

*/ 

'spell'?: string; 

/** 

* 

* @type {string} 

* @memberof SingleWord 

*/ 

'chapterOrder'?: string; 

/** 

* 

* @type {string} 

* @memberof SingleWord 

*/ 

'category'?: string; 

/** 

* 

- @type {string} 

- @memberof SingleWord 

*/ 

'structure'?: string; 

/** 

* 

- @type {{ [key: string]: string; }} 

* @memberof SingleWord 

*/ 

'strokeGif'?: { 

[key: string]: string; 

}; 

} 

/** 

# * 单字详情 

- @export 

- @interface SingleWordBasicResponse 

*/ 

interface SingleWordBasicResponse { 

/** 

* 

* @type {number} 

* @memberof SingleWordBasicResponse 

*/ 

'id'?: number; 

/** 

* 文字 

- @type {string} 

* @memberof SingleWordBasicResponse 

*/ 

'word'?: string; 

/** 

* 部首 

- @type {string} 

- @memberof SingleWordBasicResponse 

*/ 

'radical'?: string; 

/** 

* 字级 

# * @type {string} 

# * @memberof SingleWordBasicResponse 

*/ 

'level'?: string; 

/** 

# * 笔画 

- @type {number} 

- @memberof SingleWordBasicResponse 

*/ 

'periodNum'?: number; 

/** 

* 

- @type {string} 

- @memberof SingleWordBasicResponse 

*/ 

'wordNum'?: string; 

/** 

# * 拼音 

- @type {string} 

- @memberof SingleWordBasicResponse 

*/ 

'spell'?: string; 

/** 

# * 笔顺 

* @type {string} 

* @memberof SingleWordBasicResponse 

*/ 

'chapterOrder'?: string; 

/** 

* 

- @type {string} 

- @memberof SingleWordBasicResponse 

*/ 

'category'?: string; 

/** 

# * 结构 

- @type {string} 

- @memberof SingleWordBasicResponse 

*/ 

'structure'?: string; 

/** 

* 

- @type {{ [key: string]: string; }} 

* @memberof SingleWordBasicResponse 

*/ 

'strokeSrc'?: { 

[key: string]: string; 

}; 

} 

/** 

# * 单字部首搜索结果 

# * @export 

- @interface SingleWordRadicalSearchResponse 

*/ 

interface SingleWordRadicalSearchResponse { 

/** 

* 

* @type {number} 

- @memberof SingleWordRadicalSearchResponse 

*/ 

'id'?: number; 

/** 

- 文字 

- @type {string} 

- @memberof SingleWordRadicalSearchResponse 

*/ 

'word'?: string; 

/** 

# * 部首 

- @type {string} 

* @memberof SingleWordRadicalSearchResponse 

*/ 

'radical'?: string; 

/** 

# * 笔画 

- @type {number} 

- @memberof SingleWordRadicalSearchResponse 

*/ 

'periodNum'?: number; 

/** 

* 

* @type {string} 

- @memberof SingleWordRadicalSearchResponse 

*/ 

'wordNum'?: string; 

/** 

* 拼音 

* @type {string} 

# * @memberof SingleWordRadicalSearchResponse 

*/ 

'spell'?: string; 

/** 

# * 笔顺 

# * @type {string} 

* @memberof SingleWordRadicalSearchResponse 

*/ 

'chapterOrder'?: string; 

/** 

# * 结构 

- @type {string} 

- @memberof SingleWordRadicalSearchResponse 

*/ 

'structure'?: string; 

} 

/** 

# * 单字拼音搜索结果 

- @export 

- @interface SingleWordSpellSearchResponse 

*/ 

interface SingleWordSpellSearchResponse { 

/** 

# * 根据拼音分组后的单字数据 

- @type {{ [key: string]: Array<Data>; }} 

* @memberof SingleWordSpellSearchResponse 

*/ 

'data'?: { 

[key: string]: Array<Data>; 

}; 

} 

/** 

* 

# * @export 

* @interface SortObject 

*/ 

interface SortObject { 

/** 

* 

* @type {boolean} 

* @memberof SortObject 

*/ 

'empty'?: boolean; 

/** 

* 

# * @type {boolean} 

* @memberof SortObject 

*/ 

'sorted'?: boolean; 

/** 

* 

* @type {boolean} 

* @memberof SortObject 

*/ 

'unsorted'?: boolean; 

} 

/** 

* 

* @export 

* @interface StrokeGif 

*/ 

interface StrokeGif { 

/** 

- 标准笔顺 gif 

- @type {string} 

* @memberof StrokeGif 

*/ 

'white'?: string; 

/** 

* 反色笔顺 gif 

- @type {string} 

- @memberof StrokeGif 

*/ 

'black'?: string; 

} ``` 

```

## response 返回 code 说明 

errorCode: -1001 请求接口超时 

errorCode: -1002 网络异常 errorCode: -1003 证书异常,检查本地系统时间 

errorCode: -1004 权限不正确,请检查 SDK token 是否正确 errorCode: -1009 其他错误
