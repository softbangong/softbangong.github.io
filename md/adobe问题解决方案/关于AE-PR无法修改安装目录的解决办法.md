---
标题: "关于AE/PR无法修改安装目录的解决办法"
日期: 2026-04-13
修改日期: 2026-04-13
作者: "softbangong"
状态: publish
分类: ["adobe问题解决方案"]
标签: ["adobe安装问题", "无法修改安装目录", "无法安装问题"]
---
### 方案1：driver.xml文件修改   

进入安装包目录，进入到products文件夹  
编辑driver.xml文件  
将“InstallDir”修改为你需要安装的软件的目录，我这里是修改到D:\Adobe目录  
<DriverInfo>  
<ProductInfo>  
xxxxxxxxxxxxxxxxx  
</ProductInfo>  
拷贝RequestInfo这部分，粘贴到和ProductInfo并排的这个位置  
<RequestInfo>  
<InstallDir>D:\Adobe</InstallDir>  
</RequestInfo>  
</DriverInfo>  
保存driver.xml，然后重新安装  
   

![](https://www.softbangong.com/wp-content/uploads/2026/04/20250723001829175320110953896.jpg)   

### 方案2：通过Adobe Creative Cloud 修改   

找到该文件   

![](https://www.softbangong.com/wp-content/uploads/2026/04/20250723001545175320094513395.png)   

点击首选项   

![](https://www.softbangong.com/wp-content/uploads/2026/04/20250723001618175320097813180.jpg)   

修改位置   

![](https://www.softbangong.com/wp-content/uploads/2026/04/20250723001701175320102181254.png)   

### 方案3：关于兼容性猜测   

有些朋友讲说是兼容性引起的，只需按键盘上的制表定位键（TAB键），即键盘左侧的键，反复按，就可以切换到相应位置。在安装界面上根据自己的选择进行设置，然后再点击“继续”按钮，即可顺利完成安装过程。    

### 方案4：断网安装   

断开网络安装   

### 方案5：另辟蹊径   

将电脑中其他软件迁移到其他盘，adobe类软件安装到默认位置，一般来说单adobe软件并占用不了多少存储。   

如果C盘空间不足，可以使用相关工具扩展C盘，条件允许的情况下再挂着一块硬盘，C盘单独使用整块硬盘。

---

**程序下载链接：** <https://www.softbangong.com/1964.html>
