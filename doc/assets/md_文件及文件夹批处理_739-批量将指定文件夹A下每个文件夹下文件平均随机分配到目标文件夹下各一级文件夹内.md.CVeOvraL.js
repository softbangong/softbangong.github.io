import{_ as s,o as n,c as t,a5 as p}from"./chunks/framework.Cooo9kuv.js";const h=JSON.parse('{"title":"","description":"","frontmatter":{"标题":"739-批量将指定文件夹A下每个文件夹下文件平均随机分配到目标文件夹下各一级文件夹内","日期":"2026-04-12T00:00:00.000Z","修改日期":"2026-04-12T00:00:00.000Z","作者":"softbangong","状态":"publish","分类":["文件及文件夹批处理"],"标签":["分配文件到文件夹","分配文件夹内文件","批量文件分配"]},"headers":[],"relativePath":"md/文件及文件夹批处理/739-批量将指定文件夹A下每个文件夹下文件平均随机分配到目标文件夹下各一级文件夹内.md","filePath":"md/文件及文件夹批处理/739-批量将指定文件夹A下每个文件夹下文件平均随机分配到目标文件夹下各一级文件夹内.md"}'),e={name:"md/文件及文件夹批处理/739-批量将指定文件夹A下每个文件夹下文件平均随机分配到目标文件夹下各一级文件夹内.md"};function l(i,a,c,o,_,r){return n(),t("div",null,[...a[0]||(a[0]=[p(`<h3 id="程序介绍" tabindex="-1">程序介绍 <a class="header-anchor" href="#程序介绍" aria-label="Permalink to &quot;程序介绍&quot;">​</a></h3><p>批量将一个指定文件夹A下每个一级文件夹下的文件，以平均随机的方式分配到目标文件夹下各一级文件夹内</p><p>程序初始打开可能较慢，耐心等待即可</p><p><img src="https://www.softbangong.com/wp-content/uploads/2026/04/20250425002120174551168091268.jpg" alt=""></p><h3 id="程序演示示例" tabindex="-1">程序演示示例 <a class="header-anchor" href="#程序演示示例" aria-label="Permalink to &quot;程序演示示例&quot;">​</a></h3><p><strong>A 文件夹</strong>（源文件夹），路径为 <code>C:\\Data\\A</code>，其中有两个子文件夹：</p><div class="language- vp-adaptive-theme"><button title="Copy Code" class="copy"></button><span class="lang"></span><pre class="shiki shiki-themes github-light github-dark vp-code" tabindex="0"><code><span class="line"><span>C:\\Data\\A</span></span>
<span class="line"><span>├─ SubA1</span></span>
<span class="line"><span>│   ├─ a1_file1.txt</span></span>
<span class="line"><span>│   ├─ a1_file2.txt</span></span>
<span class="line"><span>│   └─ a1_file3.txt</span></span>
<span class="line"><span>└─ SubA2</span></span>
<span class="line"><span>    ├─ a2_file1.txt</span></span>
<span class="line"><span>    ├─ a2_file2.txt</span></span>
<span class="line"><span>    ├─ a2_file3.txt</span></span>
<span class="line"><span>    └─ a2_file4.txt</span></span></code></pre></div><p><strong>P 文件夹</strong>（目标文件夹），路径为 <code>C:\\Data\\P</code>，其中有两个一级子文件夹：</p><div class="language- vp-adaptive-theme"><button title="Copy Code" class="copy"></button><span class="lang"></span><pre class="shiki shiki-themes github-light github-dark vp-code" tabindex="0"><code><span class="line"><span>C:\\Data\\P</span></span>
<span class="line"><span>├─ Dest1</span></span>
<span class="line"><span>└─ Dest2</span></span></code></pre></div><p>在界面上我们选择：</p><ul><li>“A 文件夹路径” = <code>C:\\Data\\A</code></li><li>“P 文件夹路径” = <code>C:\\Data\\P</code></li><li>单选“移动文件”（也可以选“复制文件”）</li></ul><p>然后点击 <strong>“开始程序”</strong>。</p><h3 id="运行结果" tabindex="-1">运行结果 <a class="header-anchor" href="#运行结果" aria-label="Permalink to &quot;运行结果&quot;">​</a></h3><div class="language- vp-adaptive-theme"><button title="Copy Code" class="copy"></button><span class="lang"></span><pre class="shiki shiki-themes github-light github-dark vp-code" tabindex="0"><code><span class="line"><span>正在处理第 1 个子文件夹：C:\\Data\\A\\SubA1</span></span>
<span class="line"><span>  子文件夹 C:\\Data\\A\\SubA1 中共有 3 个文件。</span></span>
<span class="line"><span>  -&gt; 将 2 个文件分配到：C:\\Data\\P\\Dest1</span></span>
<span class="line"><span>      移动文件: C:\\Data\\A\\SubA1\\a1_file1.txt -&gt; C:\\Data\\P\\Dest1\\a1_file1.txt</span></span>
<span class="line"><span>      移动文件: C:\\Data\\A\\SubA1\\a1_file3.txt -&gt; C:\\Data\\P\\Dest1\\a1_file3.txt</span></span>
<span class="line"><span>  -&gt; 将 1 个文件分配到：C:\\Data\\P\\Dest2</span></span>
<span class="line"><span>      移动文件: C:\\Data\\A\\SubA1\\a1_file2.txt -&gt; C:\\Data\\P\\Dest2\\a1_file2.txt</span></span>
<span class="line"><span>  子文件夹 C:\\Data\\A\\SubA1 处理完成。</span></span>
<span class="line"><span></span></span>
<span class="line"><span>正在处理第 2 个子文件夹：C:\\Data\\A\\SubA2</span></span>
<span class="line"><span>  子文件夹 C:\\Data\\A\\SubA2 中共有 4 个文件。</span></span>
<span class="line"><span>  -&gt; 将 2 个文件分配到：C:\\Data\\P\\Dest1</span></span>
<span class="line"><span>      移动文件: C:\\Data\\A\\SubA2\\a2_file1.txt -&gt; C:\\Data\\P\\Dest1\\a2_file1.txt</span></span>
<span class="line"><span>      移动文件: C:\\Data\\A\\SubA2\\a2_file3.txt -&gt; C:\\Data\\P\\Dest1\\a2_file3.txt</span></span>
<span class="line"><span>  -&gt; 将 2 个文件分配到：C:\\Data\\P\\Dest2</span></span>
<span class="line"><span>      移动文件: C:\\Data\\A\\SubA2\\a2_file2.txt -&gt; C:\\Data\\P\\Dest2\\a2_file2.txt</span></span>
<span class="line"><span>      移动文件: C:\\Data\\A\\SubA2\\a2_file4.txt -&gt; C:\\Data\\P\\Dest2\\a2_file4.txt</span></span>
<span class="line"><span>  子文件夹 C:\\Data\\A\\SubA2 处理完成。</span></span>
<span class="line"><span></span></span>
<span class="line"><span>文件分配总结：</span></span>
<span class="line"><span>  C:\\Data\\P\\Dest1 分配了 4 个文件。</span></span>
<span class="line"><span>  C:\\Data\\P\\Dest2 分配了 3 个文件。</span></span>
<span class="line"><span>总共分配了 7 个文件。</span></span>
<span class="line"><span>操作结束。</span></span></code></pre></div><h3 id="程序适用环境" tabindex="-1">程序适用环境 <a class="header-anchor" href="#程序适用环境" aria-label="Permalink to &quot;程序适用环境&quot;">​</a></h3><p>win7及以上64位操作系统</p><h3 id="程序下载" tabindex="-1">程序下载 <a class="header-anchor" href="#程序下载" aria-label="Permalink to &quot;程序下载&quot;">​</a></h3><hr><p><strong>程序下载链接：</strong> <a href="https://www.softbangong.com/1770.html" target="_blank" rel="noreferrer">https://www.softbangong.com/1770.html</a></p>`,19)])])}const g=s(e,[["render",l]]);export{h as __pageData,g as default};
