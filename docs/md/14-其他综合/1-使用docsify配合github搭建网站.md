# 使用docsify配合github搭建个人知识库

**安装 docsify-cli 工具：**

npm i docsify-cli -g

**初始化项目：**

docsify init ./docs

 **预览网站：**

docsify serve docs

**初始化之后其实有三个文件：**

index.html、README.md、.nojekyll。

**说明：**

index.html：入口文件，docsify 的各项配置都在此页面设置。

README.md：默认展示的首页就是 README.md 里的内容。

.nojekyll：用于阻止 GitHub Pages 会忽略掉下划线开头的文件。
