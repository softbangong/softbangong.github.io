---
标题: "Python程序卡密授权验证系统-卡密加验证系统"
日期: 2026-07-24
修改日期: 2026-07-24
作者: "softbangong"
状态: publish
分类: ["zblog主题插件"]
标签: ["PyQt5", "python卡密系统", "python卡密验证", "tkinter", "Z-BlogPHP", "授权监控", "激活码", "设备绑定", "软件授权"]
---
为任意 Python 写的程序提供卡密授权解决方案，支持 tkinter 和 PyQt5 双框架，使用 Z-BlogPHP 卡密管理插件实现。不限制网站数量，python程序接入卡密验证仅需导入两行代码即可实现。   

注：只支持python程序，支持 tkinter 和 PyQt5 双框架   

![](https://www.softbangong.com/wp-content/uploads/2026/07/image-46.png)   

## 核心功能   

**— 卡密激活验证：**为 Python 桌面应用提供开箱即用的激活码授权系统，两行代码即可集成  
**— 到期时间显示：**底部状态栏实时显示授权到期时间，三色分级（绿色安全、黄色预警、红色到期）  
**— 设备 ID 管理：**自动生成设备唯一标识，支持掩码显示与一键复制，保障隐私安全  
**— 锁定蒙层保护：**授权到期或设备被封禁后，自动覆盖全屏蒙层锁定主窗口，防止未授权使用  
**— 后台实时监控：**每 30 至 60 秒自动轮询授权状态，封禁、到期、公告推送实时响应  
**— 远程公告推送：**管理后台一键推送公告到所有客户端，支持时间范围控制，精准触达用户  
**— 多程序隔离授权：**每个程序独立 APP ID 和签名密钥，卡密不互通；设备 ID 按程序掺盐，同一设备不同程序生成不同标识  
**— PHP 管理后台：**Z-BlogPHP 插件形态，提供卡密生成与导入导出、设备管理、封禁解封、统计仪表盘、系统配置等全套管理功能   

![](https://www.softbangong.com/wp-content/uploads/2026/07/image-47.png)   

**— 安全机制：**HMAC-SHA256 请求签名防伪造，Token 本地缓存支持离线使用，心跳监控线程防篡改   

### 卡密列表   

![](https://www.softbangong.com/wp-content/uploads/2026/07/image-48.png)   

### 设备列表   

![](https://www.softbangong.com/wp-content/uploads/2026/07/image-49.png)   

### 渠道管理   

![](https://www.softbangong.com/wp-content/uploads/2026/07/image-50.png)   

### 程序管理   

![](https://www.softbangong.com/wp-content/uploads/2026/07/image-51.png)   

### 系统配置   

![](https://www.softbangong.com/wp-content/uploads/2026/07/image-52.png)   

## 项目结构   

```
├── python程序.py  主程序（PyQt5版或tk版本）
│
├── kami_config.py  SDK 配置文件（API 地址、APP ID、签名密钥）
├── kami_sdk.py  SDK 通信层（HMAC 签名、API 请求、Token 缓存）
├── license_core.py  授权核心管理器（状态、激活、监控）
├── license_qt.py  PyQt5 授权 UI 集成（蒙层、公告、LicenseBar）
├── license_tk.py  tkinter 授权 UI 集成
├── activation_dialog.py  激活窗口与锁定蒙层组件
│
├── kamiPy  PHP 管理后台（Z-BlogPHP 插件）
│   ├── main.php  管理界面主入口（仪表盘、卡密管理、设备管理、系统配置）
│   ├── include.php  插件注册与路由
│   ├── plugin.xml  插件元信息
│   ├── config.php  插件配置定义
│   ├── function.php  公共函数库
│   ├── api.php  API 入口
│   ├── class/
│   │   ├── kamiapi.php  REST API（激活、状态查询、Token 刷新、公告）
│   │   ├── kamidb.php  数据库操作封装
│   │   └── kamisecurity.php  签名校验、速率限制、安全日志
│   ├── export/
│   │   └── excelexport.php  Excel 导出功能
│   ├── css/
│   │   └── admin.css  管理后台样式
│   ├── script/
│   │   └── admin.js  管理后台脚本
│   ├── language/
│   │   └── zh-cn.php  中文语言包
│   └── logo.png  插件图标
│
├── README.md  项目总览
├── INTEGRATION.md  Python 程序集成授权验证指南
```   

## 技术架构   

**框架支持：**  
- tkinter 版（Python 自带 GUI）  
- PyQt5 版（现代化 UI，蒙层、公告弹窗等丰富交互）   

**后端管理：**  
- Z-BlogPHP 插件，PHP 7.0 及以上，MySQL 5.6 及以上   

## 快速开始   

1. 部署管理后台  
将 kamiPy 目录内容放入 Z-BlogPHP 的 zb_users/plugin**/kamiPy/**，在后台插件管理中启用。   

### 2. 配置 Python 客户端   

运行主程序或使用两行代码集成到自己的 Python 项目  
修改 `kami_config.py` 中的 API 地址、APP ID、签名密钥  
修改 `kami_config.py`：   

```
PP_ID = "你的程序ID"           # 在后台「程序管理」中创建API_BASE_URL = "https://你的站点.top"SIGN_KEY = "从后台复制的签名密钥"
```   

## 后台管理功能   

| 模块 | 功能 |
| --- | --- |
| 仪表盘 | 卡密和设备统计数据，环形图和条形图可视化 |
| 卡密管理 | 卡密生成、导入导出、状态管理、批量操作 |
| 设备管理 | 设备列表、封禁和解封、批量操作 |
| 系统配置 | API签名、公告设置、客户端显示配置 |
| 系统配置 | API签名、公告设置、客户端显示配置 |
   

## 授权系统设计   

### 安全机制   

HMAC-SHA256 请求签名，防止伪造请求  
设备 ID 多因子生成（CPUID 加主板加 MAC），支持程序级盐值隔离  
Token 本地缓存和有效期管理，支持离线使用  
心跳监控线程，封禁和到期实时阻断   

### 多程序隔离   

每个程序独立 APP_ID，卡密不互通  
default模式根据配置的程序名称自动记录无需后台再次配置，可以更快的完成部署  
设备 ID 使用 program_key 掺盐，同一设备不同程序生成不同标识   

### 配置热更新   

客户端启动时自动从服务端拉取最新配置，无需重新打包分发。   

### 公告推送   

程序更新等情况，可以开启公告推送将新的信息推送到客户端。   

![](https://www.softbangong.com/wp-content/uploads/2026/07/image-53.png)   

**Python程序卡密授权验证系统-卡密加验证系统-获取方式**   

联系客服咨询

---

**程序下载链接：** <https://www.softbangong.com/3124.html>
