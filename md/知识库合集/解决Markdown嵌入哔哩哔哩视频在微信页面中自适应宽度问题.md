---
标题: "解决Markdown嵌入哔哩哔哩视频在微信页面中自适应宽度问题"
日期: 2026-04-07
修改日期: 2026-04-07
作者: "softbangong"
状态: publish
分类: ["知识库合集"]
标签: ["markdown", "哔哩哔哩"]
---
### Markdown嵌入哔哩哔哩视频在微信页面中自适应宽度   

代码如下：   

```
<div style="position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden;">
  <iframe src="//player.bilibili.com/player.html?bvid=BV1FQSUYTEq5&page=1" 
          style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;" 
          frameborder="0" allowfullscreen>
  </iframe>
</div>
```   

演示如下：   

//player.bilibili.com/player.html?bvid=BV1FQSUYTEq5&page=1

---

**程序下载链接：** <https://www.softbangong.com/281.html>
