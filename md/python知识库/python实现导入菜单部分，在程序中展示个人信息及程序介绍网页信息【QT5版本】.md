---
标题: "python实现导入菜单部分，在程序中展示个人信息及程序介绍网页信息【QT5版本】"
日期: 2026-04-12
修改日期: 2026-04-12
作者: "softbangong"
状态: publish
分类: ["python知识库"]
---
![](https://www.softbangong.com/wp-content/uploads/2026/04/image-4.png)   

导入菜单信息，显示作者信息及程序介绍内容   

![](https://www.softbangong.com/wp-content/uploads/2026/04/20250309191618174151897817862.png)   

适用于：Qt5界面写出的python程序   

基础：适合零基础通过AI写python代码的人群。   

**实现方式：**   

先创建一个名为 menu_module_qt5.py 的文件，将代码复制到文件中。   

**需要复制的代码如下所示：**   

   

然后在使用qt5写好的程序代码中调用下方代码   

1、复制下方代码到头部区域   

```
# 导入菜单的函数
from menu_module_qt5 import create_menu
```   

插入截图，比如下图所示，直接复制 from menu_module_qt5 import create_menu 到该位置即可   

![](https://www.softbangong.com/wp-content/uploads/2026/04/20250309192649174151960958914.png)   

2、在 **def initUI(self):** 下方插入下方代码   

```
# 创建并设置菜单栏
menubar = create_menu(self)
self.setMenuBar(menubar)
self.show()
```   

插入后如下图所示   

![](https://www.softbangong.com/wp-content/uploads/2026/04/20250309193211174151993184256.png)

---

**程序下载链接：** <https://www.softbangong.com/1612.html>
