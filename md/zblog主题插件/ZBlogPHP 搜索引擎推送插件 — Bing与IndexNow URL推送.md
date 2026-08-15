---
标题: "ZBlogPHP 搜索引擎推送插件 — Bing与IndexNow URL推送"
日期: 2026-07-11
修改日期: 2026-07-13
作者: "softbangong"
状态: publish
分类: ["zblog主题插件"]
标签: ["Bing推送", "IndexNow", "SEO优化", "URL提交", "Z-BlogPHP", "搜索引擎收录", "网站优化"]
---
# Bing与IndexNow URL推送 — Z-BlogPHP 搜索引擎推送插件   

> 发布新文章时自动提交 URL 到 Bing Webmaster API 和 IndexNow 协议搜索引擎，支持 Bing、Yandex、Seznam、Naver 等多引擎同时推送，内置双通道独立配置、定时推送与手动一键批量推送，帮助网站快速被搜索引擎收录。
   

**版本**：v1.0.0  
**适配**：Z-BlogPHP 1.7.0+  
**PHP**：>= 7.2  
**作者**：softbangong  
**授权**：不限制网站数量，下载安装后永久免费使用   

## 插件简介   

![](https://www.softbangong.com/wp-content/uploads/2026/07/image-7.png)   

本插件用于将 Z-BlogPHP 网站的新发布文章 URL 自动推送到搜索引擎，涵盖 Bing Webmaster Tools 的 URL 提交 API 和 IndexNow 协议（Bing、Yandex、Seznam、Naver），让搜索引擎第一时间知道网站内容更新，加速新文章的收录速度。   

插件在后台提供了双 Tab 管理界面（Bing 推送 / IndexNow 推送），两个推送通道完全独立配置，可同时启用或按需单独开启。每条新文章发布时立即触发推送，同时通过访客访问前台页面自动驱动定时任务，按配置间隔持续推送待提交的 URL，无需额外设置 Cron 计划任务。   

## 功能特性   

### 双通道独立推送   

插件同时支持两大推送通道，在后台通过 Tab 切换独立管理：   

| 通道 | 覆盖引擎 | API 端点 |
| --- | ---- | ------ |
| Bing 推送 | Bing | Bing Webmaster API (SubmitUrlbatch) |
| Bing 推送 | Bing | Bing Webmaster API (SubmitUrlbatch) |
   

两个通道各自独立配置 API Key、推送间隔、每次推送数量和自动推送开关，互不干扰，可按需灵活组合使用。   

### 新文章发布即时推送   

发布新文章时，插件通过 Z-BlogPHP 的 PostSucceed 钩子自动触发推送：   

— 文章保存成功后立即调用 API 提交该文章 URL；  
— Bing 和 IndexNow 两个通道各自独立响应，一条文章发布可同时推送到多个搜索引擎；  
— 推送过程异步执行，不影响文章发布流程和后台操作体验。   

### 访客驱动定时推送   

无需配置服务器 Cron 计划任务，插件利用访客访问前台页面时自动检查推送间隔：   

— 当有访客访问网站前台 HTML 页面时，插件检查距上次推送是否已超过配置的时间间隔；  
— 若已达间隔，自动从数据库中取出尚未推送的文章 URL 批量提交；  
— 后台请求（管理页面、AJAX、CMD）和静态资源请求自动排除，不触发推送任务，避免无意义的 API 调用。   

### 数据库标记防重复推送   

插件在 Z-BlogPHP 文章表中自动添加 `bingis` 和 `indexnowis` 两个标记字段：   

— 每次推送成功后标记对应文章为已推送，下次定时任务不再重复提交；  
— 文章全部推送完毕后自动重置标记，确保后续新文章可正常进入推送队列；  
— 手动推送和定时推送共享同一套标记机制，保证数据一致性。   

### Bing 剩余额度实时查询   

Bing 推送面板顶部展示当日剩余推送额度仪表盘：   

— 通过 Bing Webmaster API 实时查询 DailyQuota 和已用量，计算当日剩余可推送条数；  
— API 查询失败时自动回退到本地缓存数据，确保额度信息不间断展示；  
— 仪表盘同时显示累计推送总数和上次推送时间，推送状态一目了然。   

### 手动一键批量推送   

后台配置页面提供「立即推送」按钮，配置好 API Key 后可随时手动触发：   

— Bing 推送面板和 IndexNow 推送面板各自拥有独立的立即推送按钮；  
— 点击后立即从数据库取出所有未推送文章 URL，按配置的数量上限批量提交；  
— 推送完成后刷新仪表盘数据，显示本次推送数量和执行结果。   

### IndexNow 密钥文件自动管理   

![](https://www.softbangong.com/wp-content/uploads/2026/07/image-8.png)   

IndexNow 协议要求网站根目录存在一个以 API Key 命名的 `.txt` 验证文件：   

— 保存 IndexNow 配置时，插件自动在网站根目录创建或更新密钥文件，内容与配置中的 Key 保持一致；  
— 修改 API Key 时自动删除旧密钥文件并创建新文件，同时清理其他历史密钥文件避免冗余；  
— 每次推送前先通过 cURL 模拟搜索引擎自检密钥文件是否可公开访问（HTTP 200 且内容匹配），验证通过后才发起推送，提前发现配置问题。   

### 外部 API 调用端点   

插件内置独立 API 端点 `bing_api.php`，支持通过外部工具（如系统 Cron、第三方监控平台）远程触发 Bing 推送：   

— 调用地址：`zb_users/plugin/bing_indexnow/bing_api.php?key=你的密钥`；  
— 密钥在后台独立设置，与 Bing API Key 分离，安全隔离；  
— 验证通过后按配置的数量上限批量推送，返回纯文本执行结果，方便脚本集成和日志记录。   

### 推送日志记录   

每次推送的结果和状态均记录到 JSON 日志文件中：   

— Bing 推送记录保存至 `cache/logs/bing_push_state.json`，含推送时间、推送数量、剩余额度等；  
— IndexNow 推送记录保存至 `cache/logs/indexnow_push_state.json` 和 `indexnow_push_log.json`，包含 HTTP 状态码和失败原因；  
— 日志自动限制最新 200 条记录，防止文件无限增长。   

### 管理后台开关   

— 顶部菜单显示开关（show_menu）：控制是否在后台顶部导航栏显示插件入口，关闭后仍可通过直接 URL 访问管理页；  
— 卸载时清空数据开关（show_uninstall_clean）：开启后，卸载插件时会一并删除所有配置文件和缓存数据。   

## 使用说明   

### 第一步：安装插件   

将 `bing_indexnow` 文件夹上传至网站 `zb_users/plugin/` 目录，进入 Z-BlogPHP 后台「插件管理」页面，找到「Bing与IndexNow URL推送」并点击启用。   

### 第二步：配置 Bing 推送   

进入后台「Bing与IndexNow推送」页面，默认显示 Bing 推送 Tab：   

— 填入 Bing Webmaster Tools 的 API Key（获取方式：登录 Bing Webmaster Tools -> 设置 -> API 访问 -> 获取 API Key）；  
— 设置自动推送间隔（建议 5-30 分钟）和每次推送数量（建议 10-100 条）；  
— 确认「自动推送开关」已开启（默认开启），点击「保存设置」；  
— 保存后可看到仪表盘显示当日剩余额度和累计推送统计。   

### 第三步：配置 IndexNow 推送   

切换到 IndexNow 推送 Tab：   

— 手动输入或点击「随机生成」按钮创建一个 32 位十六进制 API Key；  
— 设置自动推送间隔和每次推送数量（默认与 Bing 一致，可独立调整）；  
— 确认「自动推送开关」已开启，点击「保存设置」；  
— 保存时插件自动在网站根目录创建密钥验证文件（`你的Key.txt`），推送前自动验证文件可访问性。   

### 第四步：验证推送效果   

— 发布一篇新文章，插件会自动向两个通道提交该文章 URL；  
— 进入后台插件页面查看仪表盘，确认累计推送数量增加；  
— 如需主动推送旧文章，点击「立即推送」按钮一次性批量提交所有未推送 URL；  
— 也可配置外部 Cron 任务调用 `bing_api.php?key=你的密钥` 定期触发推送。   

## 注意事项   

— 本插件依赖 PHP cURL 扩展与外部 API 通信，请确保服务器已启用 cURL 扩展；  
— Bing 推送每日有额度限制（通常为每日 10,000 条），超出额度后 API 会拒绝请求，插件会自动记录剩余额度；  
— IndexNow 推送无每日额度限制，但要求密钥验证文件可通过公网 HTTP 访问（搜索引擎需读取该文件验证域名所有权）；  
— 如果网站使用了 CDN 或缓存插件，请确保根目录的 `.txt` 密钥文件不被缓存或重定向，否则 IndexNow 推送会因验证失败而中断；  
— 访客触发型定时推送依赖于前台页面访问，日访问量极低的网站建议额外配置外部 Cron 调用 `bing_api.php` 以保证推送及时性；  
— 推送日志和状态文件存储在插件目录下的 `cache/` 子目录中，请确保 PHP 对该目录有写入权限。      

   

## 反馈与支持   

— 作者：softbangong  
— 作者网站：softbangong.com  
— 作者网站：softbangong.top  
— 邮箱：[yunjuliangpin@163.com](mailto:yunjuliangpin@163.com)   

## 更新日志   

### v1.0.0（2026-07-05）   

— 初始版本发布；  
— 支持 Bing Webmaster API URL 推送，含实时额度查询、手动推送和访客驱动定时推送；  
— 支持 IndexNow 协议推送，覆盖 Bing、Yandex、Seznam、Naver 搜索引擎；  
— 双通道独立配置，各自拥有独立的 API Key、推送间隔、推送数量和自动开关；  
— 新文章发布自动推送（PostSucceed 钩子），发布即提交；  
— 数据库标记防重复推送，推送状态跨定时/手动共享；  
— IndexNow 密钥文件自动创建、更新和清理，推送前自检验证；  
— 外部 API 端点（bing_api.php），支持第三方定时任务调用；  
— 顶部菜单显示开关和卸载数据清理开关。

---

**程序下载链接：** <https://www.softbangong.com/2975.html>
