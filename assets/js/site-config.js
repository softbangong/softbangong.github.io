// ==================== 🎨 自定义文案（集中管理，修改这里即可） ====================
var SITE = {
    brandName: 'softbangong.com',               // 网站标题
    footerCopy: '极致办公softbangong - 解放你的双手',         // 页脚标语
    footerAuth: 'by：www.softbangong.top / www.softbangong.com',                   // 页脚署名
    tocTitle:   '【目录导航】',                   // 右侧目录标题
    searchPlaceholder: '🔍 输入关键词搜索本站内容 ',
    searchNoData: '😞 暂无结果 ',
    prevText:   '上一篇',
    nextText:   '下一篇'
};
// ==================== 🎨 自定义文案结束 ====================

// ==================== 🍞 面包屑导航：首页 / 分类 / md 文档名称 ====================
// 文章页显示「首页/分类/文档名」，分类页显示「首页/分类」；
// 首页(#/)、README、搜索页(md/search)不显示。分类链接指向 sidebar/<分类名>.md（与 md 目录一一对应）。
function initBreadcrumb() {
    var sec = document.querySelector('.markdown-section');
    if (!sec) return;
    var hash = window.location.hash || '';
    var raw = hash.replace(/^#\//, '');
    // 首页 / 搜索页不显示面包屑
    if (!raw || raw === '/' || raw.indexOf('README') === 0 || raw.indexOf('md/search') === 0) return;
    var isSidebar = raw.indexOf('sidebar/') === 0;
    var isArticle = raw.indexOf('md/') === 0;
    if (!isSidebar && !isArticle) return;

    // URL 中的文件名经过百分号编码（如空格为 %20），解码后展示；解码失败则原样返回
    function safeDecode(s) {
        try { return decodeURIComponent(s); } catch (e) { return s; }
    }
    // 文件名/分类名来自 URL hash，插入前转义防 XSS
    function esc(s) {
        return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;')
            .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
    }

    var crumbs = [{ text: '首页', href: '#/' }];
    var parts = raw.split('/').filter(Boolean);

    if (isSidebar) {
        // 分类页：首页 / 分类
        if (parts.length > 1) {
            var cat = parts[1];
            crumbs.push({ text: safeDecode(cat), href: '#/sidebar/' + cat });
        }
    } else if (isArticle) {
        // 文章页：首页 / 分类 / 文档名
        parts.shift(); // 去掉 'md'
        var fileName = parts.pop() || '';
        if (parts.length > 0) {
            var catDir = parts[0];
            var catName = safeDecode(parts.join('/'));
            crumbs.push({ text: catName, href: '#/sidebar/' + catDir });
        }
        var docTitle = safeDecode(fileName).replace(/\.md$/i, '');
        // 文章标题可点击：href 为当前完整 URL（同 URL 点击不会自动刷新，需下方事件委托手动 reload）
        if (docTitle) crumbs.push({ text: docTitle, href: window.location.href, reload: true });
    }

    var div = document.createElement('div');
    div.className = 'breadcrumb';
    var html = '';
    for (var i = 0; i < crumbs.length; i++) {
        if (i > 0) html += '<span class="breadcrumb-sep">/</span>';
        if (crumbs[i].reload) {
            // 当前文章标题：可点击、点击后刷新页面
            html += '<a class="breadcrumb-title" href="' + esc(crumbs[i].href) + '">' + esc(crumbs[i].text) + '</a>';
        } else if (crumbs[i].href) {
            html += '<a href="' + esc(crumbs[i].href) + '">' + esc(crumbs[i].text) + '</a>';
        } else {
            html += '<span class="breadcrumb-current">' + esc(crumbs[i].text) + '</span>';
        }
    }
    div.innerHTML = html;
    // 事件委托：点击文章标题 → 刷新页面（阻止 docsify 的同 URL 路由拦截，stopPropagation 避免其误处理）
    div.addEventListener('click', function (e) {
        var link = e.target.closest ? e.target.closest('.breadcrumb-title') : null;
        if (link) {
            e.preventDefault();
            e.stopPropagation();
            window.location.reload();
        }
    });
    sec.insertBefore(div, sec.firstChild);
}
// ==================== 🍞 面包屑导航结束 ====================

window.$docsify = {
    name: SITE.brandName,
    nameLink: '/#/README',
    repo: 'http://doc.softbangong.top',
    auto2top: true,  // 切换页面后是否自动回到顶部
    coverpage: false,
    onlyCover: true,  // 首页只显示封面
    loadSidebar: true, // 启用侧边栏
    maxLevel: 0,  // 最大显示层级
    subMaxLevel:0,
    mergeNavbar: true,  // 导航栏在小屏幕上合并
    nativeEmoji: true,
    notFoundPage: false, //显示默认的 "404 - 未找到" 消息：

    // 别名：所有子路径下的 _sidebar.md 重定向到根目录
    alias: {
        '/(.+)/_sidebar.md': '/_sidebar.md',
    },
    
    toc: {
        scope: '.markdown-section',
        headings: 'h1, h2, h3, h4, h5, h6',
        title: SITE.tocTitle,
    },
    search: {
        paths: 'auto',
        placeholder: SITE.searchPlaceholder,
        noData: SITE.searchNoData,
        depth: 6
    },
    pagination: {
        previousText: SITE.prevText,
        nextText: SITE.nextText,
        crossChapter: true
    },
    basePath: '.',
    footer: {
        copy: '<span>' + SITE.footerCopy + '</span>',
        auth: SITE.footerAuth,
        pre: '<hr/>',
        style: 'text-align: center;',
    },
	
    // 渲染前剥离 WordPress 导出的 YAML frontmatter（--- 包裹的头部元数据），
    // 避免 标题/日期/标签 等键值对文本被当作正文显示在页面顶部（即页面顶部的“伪列表”乱行）
    plugins: [
        // ==================== 🍞 面包屑导航插件 ====================
        // docsify 4.x 已废弃顶层 $docsify.doneEach 配置（v3 遗留语法），
        // 页面渲染完成钩子必须经插件 hook.doneEach 注册，否则不会执行。
        // 正文链接的 target=_blank 由 docsify 内置 externalLinkTarget 处理，
        // 本插件动态插入的面包屑链接不受其影响（天然同页跳转）。
        function (hook) {
            hook.doneEach(function () {
                if (typeof initBreadcrumb === 'function') initBreadcrumb();
            });
        },
        // ==================== 🍞 面包屑导航插件结束 ====================
        
        function (hook) {
            // ==================== 🔍 SEO 插件：解析 frontmatter 元数据 → 动态更新每页 SEO ====================
            // 原理：docsify 是 SPA，所有页面共用一套静态 title/description；
            // 本插件在渲染前解析 md 顶部的 YAML frontmatter（标题/日期/作者/分类/标签），
            // 渲染后动态改写 <title>、meta description/keywords、Open Graph 与 JSON-LD，
            // 使每篇文章拥有独立的 SEO 信息（无 frontmatter 的页面自动回退到站点默认值）。
            var SEO_DEFAULT = {
                title: document.title,
                desc: (document.querySelector('meta[name="description"]') || {}).content || '',
                keywords: (document.querySelector('meta[name="keywords"]') || {}).content || ''
            };
            var SITE_URL = 'https://doc.softbangong.top/';
            var FM_RE = /^---\r?\n([\s\S]*?)\r?\n---\s*(?:\r?\n|$)/;

            // 解析 frontmatter 键值对（兼容中英文键名）
            function parseFrontMatter(md) {
                var m = md.match(FM_RE);
                if (!m) return null;
                var fm = {};
                var keyMap = {
                    'title': 'title', '标题': 'title',
                    'description': 'description', '描述': 'description', '摘要': 'description', '简介': 'description',
                    'keywords': 'keywords', '关键词': 'keywords',
                    'tags': 'tags', '标签': 'tags',
                    'categories': 'categories', '分类': 'categories',
                    'date': 'date', '日期': 'date',
                    'modified': 'modified', '修改日期': 'modified',
                    'author': 'author', '作者': 'author',
                    'status': 'status', '状态': 'status'
                };
                m[1].split(/\r?\n/).forEach(function (line) {
                    var idx = line.indexOf(':');
                    if (idx <= 0) return;
                    var key = line.slice(0, idx).trim();
                    var val = line.slice(idx + 1).trim().replace(/^["'“”]+|["'“”]+$/g, '').trim();
                    var norm = keyMap[key] || keyMap[key.toLowerCase()];
                    if (norm) fm[norm] = val;
                });
                return fm;
            }

            // YAML 数组/字符串 → 逗号分隔关键词串（["a","b"]、[a, b]、a,b 均可）
            function toListStr(val) {
                if (!val) return '';
                var s = String(val).trim();
                if (s.charAt(0) === '[') {
                    return s.replace(/[\[\]]/g, '').split(',')
                        .map(function (x) { return x.replace(/["'“”]/g, '').trim(); })
                        .filter(Boolean).join(',');
                }
                return s.replace(/["'“”]/g, '').trim();
            }

            // 从正文提取摘要（去除 Markdown 符号，截取前 maxLen 字）
            function extractSummary(md, maxLen) {
                var s = String(md || '')
                    .replace(/```[\s\S]*?```/g, ' ')
                    .replace(/`[^`]*`/g, ' ')
                    .replace(/!\[[^\]]*\]\([^)]*\)/g, ' ')
                    .replace(/\[[^\]]*\]\([^)]*\)/g, '$1')
                    .replace(/^#{1,6}\s+/gm, '')
                    .replace(/^>\s?/gm, '')
                    .replace(/^[-*+]\s+/gm, '')
                    .replace(/[*_~]/g, '')
                    .replace(/<[^>]+>/g, ' ')
                    .replace(/\s+/g, ' ').trim();
                return s.length > maxLen ? s.slice(0, maxLen) + '…' : s;
            }

            function setMeta(name, content) {
                var el = document.querySelector('meta[name="' + name + '"]');
                if (el) { el.setAttribute('content', content); return; }
                el = document.createElement('meta');
                el.setAttribute('name', name);
                el.setAttribute('content', content);
                document.head.appendChild(el);
            }
            function setMetaProp(prop, content) {
                var el = document.querySelector('meta[property="' + prop + '"]');
                if (el) { el.setAttribute('content', content); return; }
                el = document.createElement('meta');
                el.setAttribute('property', prop);
                el.setAttribute('content', content);
                document.head.appendChild(el);
            }

            // 注入/移除文章级 JSON-LD（Article 结构化数据，利于搜索引擎识别文章标题/日期/作者）
            function applyArticleJsonLd(seo) {
                var id = 'seo-article-jsonld';
                var old = document.getElementById(id);
                if (old) old.parentNode.removeChild(old);
                if (!seo || !seo.title) return;
                var obj = {
                    '@context': 'https://schema.org',
                    '@type': 'Article',
                    'headline': seo.title,
                    'mainEntityOfPage': { '@type': 'WebPage', '@id': window.location.href },
                    'author': { '@type': 'Person', 'name': seo.author || 'softbangong' },
                    'publisher': { '@type': 'Organization', 'name': '极致办公softbangong', 'url': SITE_URL },
                    'inLanguage': 'zh-CN'
                };
                if (seo.date) obj.datePublished = seo.date;
                if (seo.modified) obj.dateModified = seo.modified;
                if (seo.description) obj.description = seo.description;
                if (seo.categories) obj.articleSection = toListStr(seo.categories).split(',')[0];
                var sc = document.createElement('script');
                sc.type = 'application/ld+json';
                sc.id = id;
                sc.textContent = JSON.stringify(obj);
                document.head.appendChild(sc);
            }

            // 渲染后统一改写 head 中的 SEO 标签
            function applySEO() {
                var seo = window.__pageSEO || null;
                var hash = window.location.hash || '';
                var isArticle = !!(seo && seo.title) &&
                    hash.indexOf('/sidebar/') === -1 && hash.indexOf('/md/search') === -1;
                var title, desc, kws;
                if (isArticle) {
                    title = seo.title + ' - 极致办公softbangong';
                    desc = seo.description || extractSummary(seo.body, 120) || SEO_DEFAULT.desc;
                    kws = seo.keywords || toListStr(seo.tags) || SEO_DEFAULT.keywords;
                } else {
                    title = SEO_DEFAULT.title;
                    desc = SEO_DEFAULT.desc;
                    kws = SEO_DEFAULT.keywords;
                }
                document.title = title;
                setMeta('description', desc);
                setMeta('keywords', kws);
                if (seo && seo.author) setMeta('author', seo.author);
                setMetaProp('og:type', isArticle ? 'article' : 'website');
                setMetaProp('og:title', title);
                setMetaProp('og:description', desc);
                setMetaProp('og:url', window.location.href);
                setMeta('twitter:title', title);
                setMeta('twitter:description', desc);
                var canon = document.querySelector('link[rel="canonical"]');
                if (canon) canon.setAttribute('href', SITE_URL + window.location.hash);
                applyArticleJsonLd(isArticle ? seo : null);
            }

            // docsify 4.x hook API：beforeEach 接收原始 markdown 并返回处理后的内容
            hook.beforeEach(function (markdown) {
                // 解析 frontmatter 保存 SEO 数据，同时剥离避免 标题/日期/标签 等键值对文本显示在正文顶部
                var fm = parseFrontMatter(markdown);
                window.__pageSEO = fm ? {
                    title: fm.title,
                    description: fm.description,
                    keywords: fm.keywords || toListStr(fm.tags),
                    author: fm.author,
                    date: fm.date,
                    modified: fm.modified,
                    categories: fm.categories,
                    body: markdown.replace(FM_RE, '')
                } : null;
                return markdown.replace(FM_RE, '');
            });

            hook.doneEach(function () {
                applySEO();
            });
            // ==================== 🔍 SEO 插件结束 ====================
        }
    ]
};
