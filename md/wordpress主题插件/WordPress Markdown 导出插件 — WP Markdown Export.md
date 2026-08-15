---
标题: "WordPress Markdown 导出插件 — WP Markdown Export"
日期: 2026-07-12
修改日期: 2026-07-13
作者: "softbangong"
状态: publish
分类: ["wordpress主题插件"]
标签: ["Front Matter", "Hexo", "Hugo", "Jekyll", "markdown", "WordPress", "内容导出", "文章备份", "网站迁移", "静态站点"]
---
# WordPress Markdown 导出插件 — WP Markdown Export   

> 将 WordPress 文章和页面导出为 Markdown 格式文件，支持 YAML Front Matter 元数据头。零外部依赖，开箱即用。单篇导出和批量 ZIP 导出均可，兼容 Hugo、Jekyll、Hexo 等主流静态站点生成器。
   

**版本**：v1.0.0  
**适配**：WordPress 5.8+  
**PHP**：≥ 7.2  
**作者**：softbangong  
**授权**：不限制网站数量，下载安装后永久免费使用   

## 插件简介   

![](https://www.softbangong.com/wp-content/uploads/2026/07/image-31.png)   

本插件用于将 WordPress 中的文章和页面内容导出为标准的 Markdown 文件。导出的 Markdown 文件可直接导入 Hugo、Jekyll、Hexo 等静态站点生成器使用，也可用于网站内容迁移、本地备份存档或跨平台内容分发。   

插件采用自实现的 DOMDocument 驱动的 HTML 转 Markdown 引擎，无需任何第三方依赖库，安装即用。导出时自动处理 WordPress 特有的内容格式，包括 Gutenberg 代码块、图文混排（figure/caption）、嵌入内容（oEmbed）和短代码等，确保转换结果干净、规范。   

管理界面提供文章筛选、批量选择、导出选项配置和语言切换功能，所有设置可持久化保存。同时，每篇文章和页面的行操作菜单中均提供「导出 Markdown」快捷入口，方便单篇快速导出。   

## 功能特性   

### 自实现 HTML 转 Markdown 引擎，零依赖   

插件内置完整的 HTML 转 Markdown 转换器，基于 PHP DOMDocument 递归解析 HTML 节点，无需 Parsedown、League/HTMLToMarkdown 等第三方库：   

- 标题（H1-H6）转换为对应级别的 `#` 语法；  
- 粗体、斜体、删除线等行内格式完整保留；  
- 行内代码和围栏代码块正确转换，代码块自动识别语言标注（如 `php`、`javascript`）；  
- 有序列表和无序列表支持嵌套缩进；  
- HTML 表格转换为 GFM 格式的 Markdown 表格；  
- 引用块转换为 `>` 前缀格式；  
- 图片和链接的 alt、title 属性完整保留。   

### YAML Front Matter 元数据头   

导出时可在文件顶部自动生成 YAML 格式的 Front Matter 元数据头，字段可精细控制：   

- 标题（title）：文章标题，自动转义 YAML 特殊字符；  
- 日期（date）：文章发布日期，格式为 YYYY-MM-DD；  
- 修改日期（modified）：最后修改日期；  
- 作者（author）：文章作者显示名称；  
- 别名（slug）：文章 URL 别名；  
- 状态（status）：文章发布状态（publish/draft/pending/private）；  
- 分类（categories）：文章所属分类列表，YAML 数组格式；  
- 标签（tags）：文章标签列表，YAML 数组格式；  
- 特色图片（featured_image）：文章特色图片完整 URL；  
- 摘要（excerpt）：文章摘要内容。   

以上每个字段均可独立开启或关闭。开启 Front Matter 总开关后，默认可视化展开所有字段选项。Front Matter 的字段名（key）跟随插件界面语言设置，中文模式下显示中文键名，英文模式下显示英文键名。   

### WordPress 特有内容智能预处理   

导出引擎在转换前会对 WordPress 内容进行专项预处理，确保转换结果准确规范：   

- **图文混排（figure）**：自动提取 `<figure>` 中的图片和 `<figcaption>` 说明文字，生成 `![alt](url)` 格式；  
- **Caption 短代码**：识别 `...` 旧版短代码，提取图片和标题文字；  
- **Gutenberg 代码块**：处理 `wp-block-code` 样式块，自动识别并保留语言标注；  
- **嵌入内容（oEmbed）**：将 YouTube、Twitter 等嵌入块转为 HTML 注释形式（`<!-- embed: url -->`），保留原始链接；  
- **短代码保留**：可选保留或移除文章中的 WordPress 短代码，保留模式下原样输出 `[gallery]`、`[contact-form-7]` 等标记；  
- **more 标签**：`<!--more-->` 标签在导出内容中原样保留。   

### 单篇导出与批量导出   

- **单篇导出**：在文章列表页面，每篇文章和页面的行操作菜单中增加「导出 Markdown」链接，点击后直接下载该篇的 `.md` 文件；  
- **批量导出**：进入「工具 → Markdown 导出」管理页面，可多选文章后一键导出为 ZIP 压缩包。ZIP 包内按日期组织文件夹（如 `wp-markdown-export-2026-07-12/`），每篇文章以标题命名 `.md` 文件。   

### 文章筛选与批量选择   

管理界面提供便捷的筛选和选择工具：   

- 按分类筛选：下拉选择任意分类，仅显示该分类下的文章；  
- 按状态筛选：可选已发布、草稿、待审核、私密等状态；  
- 日期范围筛选：设定起止日期，精确查找时间段内的文章；  
- 全选/取消全选：表头复选框一键勾选当前页全部文章；  
- 分页浏览：每页显示 20 篇文章，支持翻页导航。   

### 导出选项灵活配置   

导出选项中以下功能均可独立开关，配置可保存持久化：   

- **Front Matter 元数据**：总开关 + 9 个字段独立子开关，精细控制导出内容；  
- **图片处理**：两种模式可选 —— 保留原始 URL（在线查看，不增加体积）或下载到本地并以相对路径引用（可离线查看，适合完整归档迁移）；  
- **包含文章摘要**：在 Front Matter 中添加 excerpt 字段；  
- **保留短代码**：原样保留 WordPress 短代码，便于后续手动替换；  
- **包含原文链接**：在导出文件末尾追加原文永久链接，格式为 `**文章原文链接：** <url>`，方便追溯来源。   

### 中英文双语界面   

插件内置完整的中英文双语系统，支持三种语言模式：   

- **自动**：根据 WordPress 站点语言自动选择中文或英文界面；  
- **中文**：强制使用中文界面，Front Matter 字段名同步显示中文键名；  
- **英文**：强制使用英文界面，Front Matter 字段名显示英文键名。   

语言切换通过管理页面顶部的下拉选择器即时生效，无需保存或刷新。   

### 导出配置持久化   

所有导出选项（Front Matter 字段开关、图片处理模式、摘要开关、短代码开关、原文链接开关）均可通过「保存配置」按钮持久化到 WordPress 的 options 表中。下次进入管理页面时自动恢复上次的配置状态，无需重复设置。   

## 使用说明   

### 第一步：安装插件   

将 `wp-markdown` 文件夹上传至网站 `wp-content/plugins/` 目录，进入 WordPress 后台「插件」页面，找到「WP Markdown Export」并点击启用。   

![](https://www.softbangong.com/wp-content/uploads/2026/07/image-32.png)   

### 第二步：单篇导出（快捷方式）   

在后台「文章 → 所有文章」或「页面 → 所有页面」列表中，将鼠标悬停在任意文章标题上，点击行操作菜单中的「导出 Markdown」链接，浏览器将自动下载该文章的 `.md` 文件。   

### 第三步：批量导出   

进入后台「工具 → Markdown 导出」页面：   

- 使用筛选条件（分类、状态、日期范围）缩小文章范围，点击「筛选」按钮；  
- 勾选需要导出的文章，或点击表头复选框全选当前页；  
- 在「导出选项」模块中按需开启或关闭各项功能；  
- 点击「导出选中文章」按钮，浏览器将下载包含所有选中文章 Markdown 文件的 ZIP 压缩包。   

如需保存当前配置以便下次复用，点击「保存配置」按钮即可。   

### 第四步：验证导出结果   

- 解压 ZIP 包，检查各 `.md` 文件的 Front Matter 头部是否包含预期字段；  
- 用任意 Markdown 编辑器（如 VS Code、Typora）打开文件，确认格式渲染正确；  
- 如需导入静态站点生成器，将 `.md` 文件放入对应内容目录即可。   

## 注意事项   

- 本插件导出的是 Markdown 文本文件，并非 WordPress 的 WXR 格式导入/导出文件。如需完整的 WordPress 数据迁移（含用户、设置等），请使用 WordPress 自带的「导出」工具；  
- 如果文章内容中包含大量依赖 WordPress 短代码渲染的功能（如表单、画廊），建议开启「保留短代码」选项，待迁移后手动替换；  
- 图片处理选择「下载到本地」模式时，导出过程会下载远程图片，处理时间与图片数量成正比，大量图片时建议分批导出；  
- 文章标题包含文件名非法字符（如 `/ \ : * ? " < > |`）时，插件会自动将其替换为连字符 `-`；  
- 文章标题超过 80 个字符时，文件名会自动截断，请留意同名文章可能导致的文件名冲突。      

   

## 反馈与支持   

- 作者：softbangong  
- 作者网站：softbangong.top  
- 作者网站：softbangong.com  
- 邮箱：[yunjuliangpin@163.com](mailto:yunjuliangpin@163.com)  
- 邮箱：[softbangong@gmail.com](mailto:softbangong@gmail.com)   

## 更新日志   

### v1.0.0（2026-07-12）   

- 初始版本发布；  
- 自实现零依赖 HTML 转 Markdown 转换引擎；  
- 支持 YAML Front Matter 元数据头，9 个字段独立开关；  
- 支持 WordPress 特有内容预处理（figure/caption/Gutenberg代码块/oEmbed/短代码）；  
- 单篇导出：文章/页面行操作菜单中一键导出；  
- 批量导出：多选文章打包为 ZIP 下载，按日期组织文件夹；  
- 管理界面：文章筛选（分类/状态/日期范围）、分页、全选；  
- 导出选项持久化保存；  
- 图片处理双模式（保留原始 URL / 下载本地引用）；  
- 中英文双语界面，Front Matter 字段名跟随语言切换。

---

**程序下载链接：** <https://www.softbangong.com/3055.html>
