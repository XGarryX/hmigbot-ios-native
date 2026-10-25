# **加固集成文档** 

### **SDK文件如下:** 

library-signed.har 

### **SDK集成步骤如下:** 

- 1、将library-signed.har文件拷⻉至放入工程的libs目录下。 

- 2、在工程目录下执行 ohpm install libs/library-signed.har 

"dependencies": { 

"libNGArg": "file:./libs/library-signed.har" 

} 

## **2、属性配置接口** 

- [x] nobf,设置混淆强度。 

- [x] ngall属性,用于选择默认防护策略。 

**其他接口,此处只是列举,因为组件封装,系统属性无法暴露,此处暴露部分UI属 性,有需要其他属性的,可以联系我们,开放出去:** 

**需要注意:har手动更新,导入har文件后,需要先删除oh_moudle/.ohpm目录下对 应的har缓存文件,再重新run install har包**
