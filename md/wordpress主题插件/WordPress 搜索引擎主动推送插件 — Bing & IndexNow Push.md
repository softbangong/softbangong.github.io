---
标题: "WordPress 搜索引擎主动推送插件 — Bing & IndexNow Push"
日期: 2026-07-12
修改日期: 2026-07-13
作者: "softbangong"
状态: publish
分类: ["wordpress主题插件"]
标签: ["Bing推送", "IndexNow", "SEO优化", "URL主动提交", "WordPress", "搜索引擎推送", "搜索引擎收录", "网站索引"]
---
# WordPress 搜索引擎主动推送插件 — Bing & IndexNow Push   

> 自动将 WordPress 文章与页面的 URL 提交至 Bing Webmaster API 和 IndexNow 协议，帮助搜索引擎即时发现并收录网站内容，提升搜索索引速度与覆盖率。
   

**版本**：v1.0.0  
**适配**：WordPress 5.8+  
**PHP**：>= 7.2  
**作者**：softbangong  
**授权**：不限制网站数量，下载安装后永久免费使用   

## 插件简介   

![](https://www.softbangong.com/wp-content/uploads/2026/07/4110675e-9490-403f-bd4f-7b3e5ce0a2e6.png)   

本插件用于将 WordPress 网站的文章和页面 URL 主动推送至搜索引擎，支持两条推送通道：   

- Bing 通道：通过 Bing Webmaster Tools API 提交 URL，让 Bing 搜索引擎第一时间发现新内容；  
- IndexNow 通道：通过 IndexNow 协议提交 URL，同时被 Bing、Yandex、Seznam 等多个搜索引擎接收。   

![](https://www.softbangong.com/wp-content/uploads/2026/07/38e77840-da19-4544-bc65-09eb53fc147d.png)   

插件在后台提供集中化的配置管理界面，Bing 和 IndexNow 两个通道独立设置、独立统计，支持自动推送、手动推送、发布即推送三种触发方式，并记录每次推送的详细日志方便排查。   

## 功能特性   

### 双通道独立推送   

插件提供 Bing 和 IndexNow 两条推送通道，各自拥有独立的 API Key、推送间隔、批量上限和启用开关，可按需单独启用或同时开启，互不干扰。   

### 三种推送触发方式   

- 发布即推送：文章或页面发布、更新时自动触发推送，无需等待定时任务；  
- 定时批量推送：前端页面被访问时按配置的间隔自动检查并推送未提交的 URL，对已推送过的 URL 自动去重避免重复提交；  
- 手动立即推送：后台点击推送按钮即时执行，适用于批量补推或紧急发布场景。   

### 智能去重与轮次管理   

插件通过文章自定义字段记录每条 URL 的推送状态，已推送的 URL 不会重复提交。当所有文章均已推送一轮后，自动清除标记重新开始新一轮推送，确保新增或修改的文章不会遗漏。   

### 外部 API 远程调用   

配置外部调用密钥后，可通过 HTTP GET 请求远程触发 Bing 推送：   

- 调用地址：`https://your-site.com/wp-content/plugins/bing_push/bing_api.php?key=YOUR_KEY`   

适用于第三方监控系统、外部定时任务或 CI/CD 流水线集成。   

### IndexNow Key 自动管理   

- 支持一键随机生成 IndexNow Key（基于浏览器 Crypto API 生成 32 位十六进制字符串）；  
- 保存配置后自动在网站根目录创建 Key 验证文件（如 `your-key.txt`），满足 IndexNow 协议的域名验证要求；  
- 更换 Key 时自动清理旧的验证文件，保持网站根目录整洁。   

### 全量推送日志   

后台提供按通道独立过滤的推送日志面板：   

- 记录每次推送的时间、触发类型（手动 / 自动 / 发布触发）、URL 数量、成功/失败状态、API 响应详情；  
- 保留最近 50 条日志记录，支持按通道单独清除或全部清除。   

### 中英双语界面   

插件内置中文、英文及自动（跟随系统语言）三种语言模式，后台顶部提供语言切换选择器即时生效。   

## 使用说明   

### 第一步：安装插件   

将 `bing_push` 文件夹上传至网站 `wp-content/plugins/` 目录，进入 WordPress 后台「插件」页面，找到「Bing & IndexNow Push」并点击启用。   

![](https://www.softbangong.com/wp-content/uploads/2026/07/image-22.png)   

### 第二步：配置 Bing 推送   

进入后台「Bing/IndexNow」菜单，在「Bing 推送」Tab 下：   

- 填入从 Bing Webmaster Tools 获取的 API Key；  
- 设置自动推送间隔（默认 5 分钟，范围 1-1440 分钟）和每批推送上限（默认 10 条）；  
- 设置外部调用密钥（可选），用于远程触发推送；  
- 勾选「启用自动推送」以开启定时提交；  
- 点击「保存设置」。   

确认配置无误后，可点击「立即推送」按钮手动触发一次推送以验证通道是否通畅。   

### 第三步：配置 IndexNow 推送   

切换到「IndexNow」Tab：   

- 生成或手动输入 IndexNow Key（建议使用随机生成按钮一键创建）；  
- 保存后插件会自动在网站根目录创建 `{key}.txt` 验证文件；  
- 设置推送间隔和批量上限，勾选「启用自动推送」；  
- 点击「保存设置」。   

### 第四步：验证生效   

- 发布一篇新文章或页面，推送日志中应出现「发布触发」类型的记录；  
- 访问网站前台任意页面，等待推送间隔到期后检查日志是否出现「自动」类型的推送记录；  
- 使用外部调用地址测试远程触发功能。   

## 注意事项   

- 使用 Bing 推送前需先在 Bing Webmaster Tools 中完成网站所有权验证并获取 API Key；  
- IndexNow 推送依赖网站根目录的 Key 验证文件，请确保 Web 服务器允许写入 WordPress 根目录；如果写入失败需手动创建；  
- 自动推送依赖前端页面访问触发，纯后台操作不会触发定时推送；如需更强的定时可靠性，建议配合系统 Cron 调用外部 API 地址；  
- 推送日志仅保留最近 50 条，重要数据请定期备份；  
- Bing 推送和 IndexNow 推送均有 API 调用频率限制，请根据网站文章量合理设置推送间隔。      

   

## 反馈与支持   

- 作者：softbangong  
- 作者网站：softbangong.com  
- 作者网站：softbangong.top  
- 邮箱：[yunjuliangpin@163.com](mailto:yunjuliangpin@163.com)  
- 邮箱：[softbangong@gmail.com](mailto:softbangong@gmail.com)   

## 更新日志   

### v1.0.0（2026-06）   

- 首发版本，支持 Bing Webmaster API 和 IndexNow 协议双通道 URL 推送；  
- 发布/更新自动触发推送，定时批量推送，手动立即推送三种触发方式；  
- 基于文章自定义字段的推送去重与轮次自动重置机制；  
- 外部 API 远程调用接口，支持密钥鉴权；  
- IndexNow Key 随机生成与验证文件自动管理；  
- 双通道独立统计数据面板（累计推送量、上次状态、上次数量）；  
- 推送日志记录与按通道清除功能；  
- 中英双语界面（中文 / English / 自动跟随系统语言）。

---

**程序下载链接：** <https://www.softbangong.com/3014.html>
