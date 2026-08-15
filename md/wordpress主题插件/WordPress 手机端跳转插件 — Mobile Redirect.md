---
标题: "WordPress 手机端跳转插件 — Mobile Redirect"
日期: 2026-07-12
修改日期: 2026-07-13
作者: "softbangong"
状态: publish
分类: ["wordpress主题插件"]
标签: ["301重定向", "UA匹配", "User-Agent", "WordPress", "微信浏览器", "手机跳转", "浏览器识别", "移动端", "设备跳转"]
---
# WordPress 手机端跳转插件 — Mobile Redirect   

> 基于 User-Agent 规则将手机、平板或指定 App 浏览器访问自动 301 重定向到指定地址。内置 20+ 条预置规则，支持自定义 UA 关键词匹配，管理后台、AJAX、REST API、登录、Cron 等请求自动跳过。
   

**版本**：v1.5.1  
**适配**：WordPress 5.8+  
**PHP**：≥ 7.2  
**作者**：softbangong  
**授权**：不限制网站数量，下载安装后永久免费使用   

## 插件简介   

![](https://www.softbangong.com/wp-content/uploads/2026/07/88791748-3872-400e-ad83-2dd63b9131f1.png)   

本插件根据访客浏览器的 User-Agent 字符串自动识别其设备类型和浏览器来源，当匹配到已启用的规则时，将访客 301 永久重定向到预设的目标地址。   

插件在后台提供了规则配置管理界面，支持每条规则独立开关、自定义 UA 关键词（支持管道符分隔和简单正则）、一键模块总开关控制。同时内置中英双语界面，语言切换即时生效无需保存。   

重定向逻辑运行于 WordPress 的 template_redirect 钩子（优先级 1），自动排除管理后台、AJAX 请求、REST API、登录页、Cron 任务和 XML-RPC 请求，确保网站管理功能不受影响。   

## 功能特性   

### 20+ 条预置浏览器规则   

插件内置了覆盖国内主流 App 和手机/平板浏览器的 21 条预置规则，每条规则均配有预设的 UA 关键词和独立的启用开关：   

- 微信内置浏览器：匹配 MicroMessenger 标识  
- QQ 内置浏览器 / QQ 浏览器（腾讯）：匹配 QQ/、MQQBrowser、QQBrowser 标识  
- 腾讯客户端 / QQ 空间客户端：匹配 TencentTraveler、Qzone/ 等腾讯系 UA 标识  
- UC 浏览器：匹配 UCBrowser、UCWEB、UC Browser 标识  
- 百度浏览器：匹配 baidubrowser、baiduboxapp 等标识  
- 搜狗浏览器：匹配 Sogou、MetaSr、SogouMobileBrowser 标识  
- 手机浏览器 / 平板设备：匹配 iPhone、Android、iPad、Tablet 等通用移动设备标识  
- Opera Mini/Mobile、Firefox 移动版、Edge 移动版  
- 360 浏览器、猎豹浏览器、夸克浏览器  
- 小米浏览器（Miui）、华为浏览器、Vivo 浏览器、OPPO 浏览器、三星浏览器   

### 自定义 UA 关键词   

每条规则的 UA 关键词均可在后台自由编辑，支持以下灵活配置：   

- 管道符（|）分隔多个关键词，命中任意一个即触发跳转  
- 支持简单正则表达式（如 Firefox.*Mobile 匹配 Firefox 移动版的多种变体）  
- 当正则语法无效时自动回退为大小写不敏感的纯文本子串匹配，确保规则鲁棒性   

### 模块总开关   

- 后台设置页提供模块总开关（Toggle Switch），一键启用或禁用全部跳转规则  
- 关闭总开关后配置表单自动折叠隐藏，界面简洁清晰  
- 总开关状态实时保存，无需额外操作   

### 自动排除管理请求   

插件在以下场景自动跳过重定向逻辑，无需手动配置：   

- WordPress 管理后台（is_admin）  
- AJAX 请求（wp_doing_ajax）  
- REST API 请求（REST_REQUEST 常量）  
- 登录页（wp-login.php）  
- Cron 任务（wp-cron.php）  
- XML-RPC 请求（xmlrpc.php）   

### 301 永久重定向   

匹配到规则后使用 wp_safe_redirect 执行 301 永久重定向，对搜索引擎友好，有利于 SEO 权重传递。   

### 传统 AntiBot 配置迁移   

插件激活时自动检测旧版 AntiBot 插件的配置数据（支持 WordPress 选项表和 config.json 文件两种存储格式），如果存在原有的手机设备跳转规则，自动导入到本插件中，实现无缝升级。   

### 中英双语界面   

- 后台界面支持中文（zh_CN）和英文（en_US）两种语言，也可选择「自动」跟随 WordPress 站点语言  
- 语言切换通过独立的 admin-post 表单即时生效，无需保存设置  
- 翻译通过 PHP 数组 + gettext 过滤器实现，不依赖 .po/.mo 文件   

## 使用说明   

### 第一步：安装插件   

将 mobile_tiaozhuan 文件夹上传至网站 wp-content/plugins/ 目录，进入 WordPress 后台「插件」页面，找到「Mobile Redirect」并点击启用。   

### 第二步：配置跳转规则   

启用后，后台左侧菜单会出现「Mobile Redirect」入口，点击进入配置页面：   

- 页面顶部提供界面语言切换下拉框，选择后即时生效  
- 「手机端跳转规则」模块卡片右上角为模块总开关，关闭后所有规则停止生效  
- 在规则表格中，勾选需要启用的规则对应的「启用」复选框  
- 在「跳转地址」列填入目标 URL（如 [https://m.example.com/）](https://m.example.com/%EF%BC%89)  
- 如需修改 UA 关键词，直接在「UA 关键词」文本框中编辑，多个关键词用 | 分隔  
- 点击页面底部「保存设置」按钮   

### 第三步：验证效果   

- 使用对应的浏览器或修改 User-Agent 模拟手机/平板设备访问网站前台  
- 确认匹配到规则时自动跳转到预设的目标地址  
- 访问 WordPress 后台确认不受影响   

## 注意事项   

- 跳转规则按表格顺序从上到下逐条匹配，命中第一条后立即跳转，后续规则不再检查。如有多条规则可能同时匹配同一浏览器，请通过调整规则顺序控制优先级  
- UA 关键词为空或跳转地址为空的规则不会被触发，即使已勾选启用  
- 插件使用 301 永久重定向，浏览器可能会缓存重定向结果，测试期间建议使用隐私/无痕模式  
- 与缓存插件共用时，建议将重定向逻辑排除在页面缓存之外，插件在 template_redirect 钩子优先级 1 执行，通常早于大多数缓存插件  
- 「严格」列目前为预留字段，暂不影响跳转行为      

   

## 反馈与支持   

- 作者：softbangong  
- 作者网站：softbangong.com  
- 作者网站：softbangong.top  
- 邮箱：[yunjuliangpin@163.com](mailto:yunjuliangpin@163.com)  
- 邮箱：[softbangong@gmail.com](mailto:softbangong@gmail.com)   

## 更新日志   

### v1.5.1（2026）   

- 新增中英双语界面支持，语言切换即时生效无需保存  
- 新增模块总开关（Toggle Switch），一键启用或禁用全部跳转规则  
- 新增模块卡片 UI，关闭总开关后配置表单自动折叠  
- 优化管理界面 CSS 样式，适配 WordPress 后台整体风格  
- 更新 textdomain 和标识符与插件 slug 对齐   

### v1.0.0   

- 初始版本发布  
- 内置 21 条预置手机/App 浏览器规则  
- 自定义 UA 关键词匹配，支持管道符分隔和简单正则  
- Settings API 配置注册与数据持久化  
- 传统 AntiBot 插件配置自动迁移  
- 自动排除管理后台、AJAX、REST API、登录、Cron、XML-RPC 请求

---

**程序下载链接：** <https://www.softbangong.com/3025.html>
