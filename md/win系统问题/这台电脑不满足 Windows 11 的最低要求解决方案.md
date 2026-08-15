---
标题: "这台电脑不满足 Windows 11 的最低要求解决方案"
日期: 2026-04-13
修改日期: 2026-04-13
作者: "softbangong"
状态: publish
分类: ["win系统问题"]
标签: ["win11", "win11安装", "这台电脑不满足Windows 11 的最低要求"]
---
要安装 Windows 11，请从官方网站 microsoft.com 下载 ISO 镜像。   

安装此操作系统，已引入了一些额外的要求，这在某些情况下可能会阻止安装，本教程解决这台电脑不满足 Windows 11 的最低要求解决方案，可以在任意电脑中正常进行安装win11。   

在本指南中，我们将向您展示如何在使用官方分发版和文档的情况下禁用这些要求。   

### 跳过微软登录验证   

安装win11时不要联网即可跳过   

![](https://www.softbangong.com/wp-content/uploads/2026/04/20251031232953176192459380899.png)   

### 进入安装界面后，点击疫情版本的安装程序   

如下图所示：   

### ![](https://www.softbangong.com/wp-content/uploads/2026/04/20251101150234176198055419605.jpg) 看到这一步后，执行下一步 ![](https://www.softbangong.com/wp-content/uploads/2026/04/20251031233810176192509032706.jpg) 看到这一步后执行下方步骤 ![](https://www.softbangong.com/wp-content/uploads/2026/04/20251031233859176192513915826.jpg) 1. 打开注册表

1、按下 Shift + F10 打开控制台并启动注册表编辑器   

2、在打开的控制台中，输入 **regedit**，然后按 **Enter**   

3、找到并展开** HKEY_LOCAL_MACHINE\SYSTEM\Setup**   

鼠标右键在**Setup**上点击，然后点击新建项，命名为**labConfig**    

![](https://www.softbangong.com/wp-content/uploads/2026/04/20251101150536176198073631636.jpg)   

### 2.创建必要的参数以解除限制   

**添加值为 1 的 DWORD 参数如下所示：**   

BypassCPUCheck – 针对不兼容的处理器；   

BypassTPMCheck – 无 TPM 2.0 芯片；   

BypassRAMCheck – 不检查最低 RAM 要求；   

BypassSecureBootCheck – 使用 Legacy BIOS（或禁用 Secure Boot 的 UEFI）；   

BypassStorageCheck – 不检查系统盘大小。   

**选择我们创建的 labConfig 分支文件夹，在右侧空白处鼠标右键点击创建DWORD参数和值**   

![](https://www.softbangong.com/wp-content/uploads/2026/04/20251101150729176198084941512.jpg)   

对上边添加的每一个** DWORD（32位）**的值进行修改，选中后鼠标右键点击修改，将数值数据修改为1   

![](https://www.softbangong.com/wp-content/uploads/2026/04/20251101151010176198101047912.jpg)   

**然后关闭注册表窗口和命令行窗口，如下所示的两个窗口全部关闭，**   

### 保持主安装窗口打开。   

![](https://www.softbangong.com/wp-content/uploads/2026/04/20251101151234176198115463379.jpg)   

### 看到这个界面   

点击现在安装   

![](https://www.softbangong.com/wp-content/uploads/2026/04/20251031233859176192513915826.jpg)   

执行下一步   

![](https://www.softbangong.com/wp-content/uploads/2026/04/20251101151439176198127988929.jpg)   

### 看到这个界面   

选择如图所示：   

### ![](https://www.softbangong.com/wp-content/uploads/2026/04/20251101151511176198131189700.jpg) 选择要安装win11系统到哪里

这里，如果是安装到一个新的硬盘，则直接选择即可   

——————————————   

如果需要对硬盘进行分区，点击新建，按照硬盘大小进行分配即可   

![](https://www.softbangong.com/wp-content/uploads/2026/04/20251101151625176198138599033.jpg)   

### 之后会进入到系统自动安装界面   

这部分走完后，系统会重启，进入到系统配置界面   

![](https://www.softbangong.com/wp-content/uploads/2026/04/20251101151828176198150885371.jpg)   

### 进入系统配置界面   

![](https://www.softbangong.com/wp-content/uploads/2026/04/20251101151955176198159511981.jpg)   

### ![](https://www.softbangong.com/wp-content/uploads/2026/04/20251101152020176198162039015.jpg) ![](https://www.softbangong.com/wp-content/uploads/2026/04/20251101152048176198164833897.jpg)

**设置相关名称**   

![](https://www.softbangong.com/wp-content/uploads/2026/04/20251101152109176198166914650.jpg)   

**进行相关安全设置**   

![](https://www.softbangong.com/wp-content/uploads/2026/04/20251101152156176198171625913.jpg)   

### 全部选择否   

![](https://www.softbangong.com/wp-content/uploads/2026/04/20251101152223176198174371255.jpg)   

### 进入系统   

![](https://www.softbangong.com/wp-content/uploads/2026/04/20251101152309176198178973042.png)   

### 进入系统后，激活win11,然后在能在个性化里的主题部分，桌面图片添加到桌面   

![](https://www.softbangong.com/wp-content/uploads/2026/04/20251101152431176198187131921.jpg)

---

**程序下载链接：** <https://www.softbangong.com/2130.html>
