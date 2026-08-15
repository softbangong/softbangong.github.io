---
标题: "Windows10 启用长路径支持"
日期: 2026-04-09
修改日期: 2026-04-09
作者: "softbangong"
状态: publish
分类: ["win系统问题"]
标签: ["win系统长路径", "win长路径", "长路径启用"]
---
### Windows 启用长路径支持   

Windows 标准支持260个字符，超过可能会出现诸多错误资源管理器崩溃等问题   

### 下方为注册表修改方式：   

打开注册表编辑器：regedit  
找到如下路径：HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\FileSytem  
找到如下键值：LongPathsEnabled  
将值修改为1：默认是0，不启用。   

![](https://www.softbangong.com/wp-content/uploads/2026/04/202501081840409134031.png)   

### 下方为组策略修改方式   

win+r: 输入gpedit.msc  
打开文件（本地组策略编辑器）   

![](https://www.softbangong.com/wp-content/uploads/2026/04/202501081844396992355.png)   

依次点开 计算机配置>管理模板>系统>文件系统，找到“启用win32长路径”并双击打开   

![](https://www.softbangong.com/wp-content/uploads/2026/04/202501081845255041791.png)   

选择“启用”选项，然后单击“确定”  
退出，重启电脑   

![](https://www.softbangong.com/wp-content/uploads/2026/04/202501081845471161724.png)

---

**程序下载链接：** <https://www.softbangong.com/604.html>
