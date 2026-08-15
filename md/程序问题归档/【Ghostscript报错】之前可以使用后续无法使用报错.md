---
标题: "【Ghostscript报错】之前可以使用后续无法使用报错"
日期: 2026-05-07
修改日期: 2026-05-07
作者: "softbangong"
状态: publish
分类: ["程序问题归档"]
标签: ["Ghostscript", "pdf调用出错", "程序使用问题", "程序错误", "解决方案"]
---
如果之前可以使用，但是过了一段时间使用时报错   

![](https://www.softbangong.com/wp-content/uploads/2026/05/image-4.png)   

### 报错如下所示   

处理文件时发生错误: D:\ceshi000000000\333.pdf, 错误信息: Command '['C:\\apitool\\gxpswin64\\bin\\gswin64c.exe', '-sDEVICE=pdfwrite', '-dCompatibilityLevel=1.7', '-dPDFSETTINGS=/prepress', '-dNOPAUSE', '-dBATCH', '-sOutputFile=D:\\ceshi000000000\\333_standard.pdf', 'D:\\ceshi000000000\\333.pdf']' returned non-zero exit status 1.。继续处理下一个文件。   

该问题为电脑权限发生了变化   

需要以管理员身份取得软件的管理权限，之后再运行就可以了   

出现这种问题情况原因为：误操作导致电脑原本的权限丢失，特别是使用了“获取管理员权限”这个插件的用户。

---

**程序下载链接：** <https://www.softbangong.com/2779.html>
