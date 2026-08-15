// ===== 返回顶部按钮配置 =====
docsifyBackTop = {
    logo: '<svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="#fff" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="18 15 12 9 6 15"/></svg>',
    size: 44,
    bottom: 30,
    right: 5,
    bgColor: '#2096ff'
};

// ===== 独立搜索页面逻辑 =====
function initSearchPage() {
    var input = document.getElementById('search-page-input');
    var results = document.getElementById('search-page-results');
    var countEl = document.getElementById('search-page-count');

    if (!input || !results) {
        return;
    }

    // 从 localStorage 读取搜索索引
    function getIndexS() {
        try {
            var data = localStorage.getItem('docsify.search.index');
            return data ? JSON.parse(data) : {};
        } catch (e) {
            return {};
        }
    }

    // 转义 HTML
    function escapeHtml(str) {
        var map = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' };
        return String(str).replace(/[&<>"']/g, function (s) { return map[s]; });
    }

    // 去除变音符号
    function ignoreDiacriticalMarks(keyword) {
        if (keyword && keyword.normalize) {
            return keyword.normalize('NFD').replace(/[\u0300-\u036f]/g, '');
        }
        return keyword;
    }

    // 搜索
    function doSearch(query) {
        var indexData = getIndexS();
        var data = [];

        // 清洗预览文本：去掉markdown链接和路径，保留纯文本
        function cleanPreview(text) {
            var t = text
                .replace(/!\[.*?\]\(.*?\)/g, '')       // 去掉图片 ![alt](url)
                .replace(/\n?\[([^\]]*)\]\([^)]*\)/g, '') // 去掉markdown链接
                .replace(/[^\s]*\.md[^\s]*/g, '')       // 去掉.md文件路径
                .replace(/https?:\/\/\S+/g, '')          // 去掉裸URL
                .replace(/#\/[\w%\/\-.@]+/g, '')        // 去掉hash路由路径
                .replace(/\*\*(.+?)\*\*/g, '$1')         // 去掉粗体 **text**
                .replace(/__(.+?)__/g, '$1')             // 去掉粗体 __text__
                .replace(/~~(.+?)~~/g, '$1')             // 去掉删除线
                .replace(/`(.+?)`/g, '$1')               // 去掉行内代码
                .replace(/\n{2,}/g, '\n')                // 合并多余换行
                .replace(/\s{2,}/g, ' ');                // 合并多余空白
            // 解码 URL 编码的中文字符
            if (/%[0-9A-F]{2}/i.test(t)) {
                try { t = decodeURIComponent(t); } catch (e) {}
            }
            return t.trim();
        }

        Object.keys(indexData).forEach(function (key) {
            var pages = indexData[key];
            Object.keys(pages).forEach(function (page) {
                data.push(pages[page]);
            });
        });

        query = query.trim();
        if (!query) {
            results.innerHTML = '<div class="search-page-empty">😊 输入关键词开始搜索</div>';
            countEl.style.display = 'none';
            return;
        }

        var keywords = query.split(/[\s\-，\\/]+/);
        if (keywords.length !== 1) {
            keywords = [].concat(query, keywords);
        }

        // ===== 第一步：按文档 baseUrl 分组收集匹配信息 =====
        var docMap = {};      // { baseUrl: { mainTitle, titleScore, bestMatch } }
        var docTitles = {};   // { baseUrl: decodedMainTitle }

        for (var i = 0; i < data.length; i++) {
            var post = data[i];
            var postTitle = post.title && post.title.trim();
            var postContent = post.body && post.body.trim();
            var postUrl = post.slug || '';

            if (!postTitle) continue;
            // 仅保留文档文章（#/md/ 路径），排除首页、侧边栏等非文档页面
            if (postUrl.indexOf('/md/') === -1) continue;

            var baseUrl = postUrl.replace(/\?id=.*$/, '');
            var isMain = postUrl.indexOf('?id=') === -1;

            // 解码 URL 编码的标题
            var decodedTitle = postTitle;
            if (/%[0-9A-F]{2}/i.test(postTitle)) {
                try { decodedTitle = decodeURIComponent(postTitle); } catch (e) {}
            }
            var handleTitle = escapeHtml(ignoreDiacriticalMarks(decodedTitle));
            var handleContentRaw = postContent ? escapeHtml(ignoreDiacriticalMarks(postContent)) : '';
            // 屏蔽 URL 用于关键词匹配：将 URL 字符替换为等长空格，避免 "doc" 误匹配 kdocs.cn 等
            var handleContentForMatch = handleContentRaw.replace(/https?:\/\/\S+/g, function(m) { return m.replace(/./g, ' '); });

            // 记录主标题（优先使用无 ?id= 的主条目标题）
            if (isMain) {
                docTitles[baseUrl] = handleTitle;
            } else if (!docTitles[baseUrl]) {
                docTitles[baseUrl] = handleTitle;
            }

            // 检查关键词匹配
            var entryTitleMatched = false;
            var entryBestMatch = null;  // { index, keyword, escapedKw }

            for (var k = 0; k < keywords.length; k++) {
                var keyword = keywords[k];
                var escapedKw = escapeHtml(ignoreDiacriticalMarks(keyword)).replace(/[|\\{}()[\]^$+*?.]/g, '\\$&');
                var regEx = new RegExp(escapedKw, 'gi');

                var idxTitle = handleTitle.search(regEx);
                var idxContent = postContent ? handleContentForMatch.search(regEx) : -1;

                if (idxTitle >= 0) entryTitleMatched = true;
                if (idxContent >= 0 && (!entryBestMatch || idxContent < entryBestMatch.index)) {
                    entryBestMatch = { index: idxContent, keyword: keyword, escapedKw: escapedKw };
                }
            }

            if (entryTitleMatched || entryBestMatch) {
                if (!docMap[baseUrl]) {
                    docMap[baseUrl] = { titleScore: 0, contentScore: 0, bestMatch: null, contentRaw: '' };
                }
                if (entryTitleMatched) docMap[baseUrl].titleScore += 3;
                docMap[baseUrl].contentScore += (entryBestMatch ? 2 : 0);
                // 保留最早（最靠前）的内容匹配位置，同时保存对应的原始内容
                if (entryBestMatch && (!docMap[baseUrl].bestMatch || entryBestMatch.index < docMap[baseUrl].bestMatch.index)) {
                    docMap[baseUrl].bestMatch = entryBestMatch;
                    docMap[baseUrl].contentRaw = handleContentRaw;
                }
            }
        }

        // ===== 第二步：每个文档只生成一条结果 =====
        var matchingResults = [];
        Object.keys(docMap).forEach(function (baseUrl) {
            var doc = docMap[baseUrl];
            var displayTitle = docTitles[baseUrl] || baseUrl;

            // 构建内容预览片段
            var contentHtml = '';
            if (doc.bestMatch) {
                var m = doc.bestMatch;
                var start = m.index < 21 ? 0 : m.index - 20;
                var end = start === 0 ? 150 : m.index + m.keyword.length + 140;
                // 需要从原始数据中获取对应内容来截取
                // 这里使用缓存的内容原始文本（在分组循环中已处理）
                var regExHighlight = new RegExp(m.escapedKw, 'gi');
                // 从分组时缓存的原始文本中读取片段
                if (doc.contentRaw) {
                    if (end > doc.contentRaw.length) end = doc.contentRaw.length;
                    var snippetRaw = doc.contentRaw.substring(start, end);
                    var snippetClean = cleanPreview(snippetRaw);
                    contentHtml = '...' + snippetClean.replace(regExHighlight, function (word) {
                        return '<em class="search-keyword">' + word + '</em>';
                    }) + '...';
                }
            }

            matchingResults.push({
                title: displayTitle,
                content: contentHtml,
                url: baseUrl,
                score: doc.titleScore + doc.contentScore
            });
        });

        // 按分数排序
        matchingResults.sort(function (a, b) { return b.score - a.score; });

        // 渲染结果
        if (matchingResults.length === 0) {
            results.innerHTML = '<div class="search-page-empty">😞 没有找到相关结果</div>';
            countEl.style.display = 'none';
        } else {
            countEl.textContent = '共找到 ' + matchingResults.length + ' 条结果';
            countEl.style.display = 'inline';

            var html = '';
            for (var j = 0; j < matchingResults.length; j++) {
                var r = matchingResults[j];
                // 标题高亮关键词
                var hlTitle = r.title;
                for (var kw = 0; kw < keywords.length; kw++) {
                    var kwEscaped = keywords[kw].replace(/[|\\{}()[\]^$+*?.]/g, '\\$&');
                    var kwReg = new RegExp('(' + kwEscaped + ')', 'gi');
                    hlTitle = hlTitle.replace(kwReg, '<em class="search-keyword">$1</em>');
                }
                html += '<div class="search-page-result">' +
                    '<h3><a href="' + r.url + '" target="_blank">' + hlTitle + '</a></h3>' +
                    '<p>' + r.content + '</p>' +
                    '</div>';
            }
            results.innerHTML = html;
        }
    }

    // 显示等待索引的提示
    var indexData = getIndexS();
    if (Object.keys(indexData).length === 0) {
        results.innerHTML = '<div class="search-page-loading">⏳ 正在建立搜索索引，请稍候...</div>';

        // 轮询等待索引建立（搜索插件异步构建，最长等30秒）
        var attempts = 0;
        var checkInterval = setInterval(function () {
            attempts++;
            var data = getIndexS();
            if (Object.keys(data).length > 0) {
                clearInterval(checkInterval);
                results.innerHTML = '<div class="search-page-empty">😊 输入关键词开始搜索</div>';
            } else if (attempts >= 60) {
                clearInterval(checkInterval);
                results.innerHTML = '<div class="search-page-loading">⚠️ 索引建立超时，请刷新页面后重试</div>';
            }
        }, 500);
    } else {
        results.innerHTML = '<div class="search-page-empty">😊 输入关键词开始搜索</div>';
    }

    // 绑定输入事件（防抖）
    var timer;
    input.addEventListener('input', function () {
        clearTimeout(timer);
        timer = setTimeout(function () {
            doSearch(input.value);
        }, 200);
    });

    // 从 URL 参数读取预设关键词
    var hash = window.location.hash;
    var queryMatch = hash.match(/[?&]s=([^&]*)/);
    if (queryMatch) {
        var q = decodeURIComponent(queryMatch[1]);
        input.value = q;
        // 等待索引就绪再搜索
        var retryCount = 0;
        var searchInterval = setInterval(function () {
            retryCount++;
            var data = getIndexS();
            if (Object.keys(data).length > 0) {
                clearInterval(searchInterval);
                doSearch(q);
            } else if (retryCount >= 30) {
                clearInterval(searchInterval);
            }
        }, 500);
    }
}

// 分类页和搜索页隐藏目录导航（独立于 docsify 回调，确保可靠触发）
(function () {
    function toggleNoToc() {
        var hash = window.location.hash;
        if (hash.indexOf('/sidebar/') !== -1 || hash.indexOf('/md/search') !== -1) {
            document.body.classList.add('no-toc');
        } else {
            document.body.classList.remove('no-toc');
        }
    }
    toggleNoToc();
    window.addEventListener('hashchange', toggleNoToc);
})();

// 小屏幕侧边栏交互修复
// 【关键发现】移动端 vue.css 中 body.close 语义与桌面端完全相反：
//   桌面端: body.close → 侧边栏隐藏（translateX: -300px）
//   移动端: body.close → 侧边栏显示（translateX: 300px，因 sidebar 自身 left: -300px）
// Docsify body click 处理器：body.close 不存在时 toggle 添加它 → 移动端侧边栏意外弹出！
(function () {
    var allowToggle = false;

    // 捕获切换按钮点击（唯一合法的侧边栏开关来源）
    document.addEventListener('click', function (e) {
        var toggleBtn = document.querySelector('.sidebar-toggle');
        if (toggleBtn && toggleBtn.contains(e.target)) {
            allowToggle = true;
            setTimeout(function () { allowToggle = false; }, 150);
        }
    }, true);

    // MutationObserver：仅拦截 body.close 被【添加】（移动端添加 close = 侧边栏意外打开）
    // 不拦截 close 被移除，因为移动端 Docsify body 处理器在 close 存在时会自然移除它（= 关闭）
    var observer = new MutationObserver(function (mutations) {
        if (window.innerWidth > 768) return;
        mutations.forEach(function (mutation) {
            if (mutation.type === 'attributes' && mutation.attributeName === 'class') {
                var oldHad = mutation.oldValue && mutation.oldValue.indexOf('close') !== -1;
                var nowHas = document.body.classList.contains('close');
                // close 被【添加】（侧边栏从隐藏→显示）且非切换按钮触发 → 撤销
                if (!oldHad && nowHas && !allowToggle) {
                    document.body.classList.remove('close');
                }
            }
        });
    });
    observer.observe(document.body, {
        attributes: true,
        attributeFilter: ['class'],
        attributeOldValue: true
    });
})();

// 小屏点击收起侧边栏（docsify 内置 body 点击处理仅在宽度 ≤600px 时绑定，
// 而 vue.css 移动端样式断点是 768px，导致 601~768px 区间：菜单能打开但点击文章区不会收回）
(function () {
    document.addEventListener('click', function (e) {
        if (window.innerWidth > 768) return;
        var t = e.target;
        // 切换按钮负责开关、分类折叠箭头点击时不干预，其余点击（内容区/侧边栏链接）均收起菜单
        if (t.closest && (t.closest('.sidebar-toggle') || t.closest('.sidebar-catalog-toggle'))) return;
        if (document.body.classList.contains('close')) {
            document.body.classList.remove('close');
        }
    }, true);
})();

// 自启动：监听 hash 变化和页面加载，轮询初始化搜索页
(function() {
    function tryInit() {
        if (window.location.hash.indexOf('/md/search') === -1) return true;
        var input = document.getElementById('search-page-input');
        var results = document.getElementById('search-page-results');
        if (input && results) {
            initSearchPage();
            return true;
        }
        return false;
    }

    function waitAndInit() {
        var retries = 0;
        var timer = setInterval(function() {
            retries++;
            if (tryInit() || retries >= 60) clearInterval(timer);
        }, 100);
    }

    // 页面加载时检查
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            setTimeout(waitAndInit, 200);
        });
    } else {
        setTimeout(waitAndInit, 200);
    }

    // hash 变化时检查
    window.addEventListener('hashchange', function() {
        setTimeout(waitAndInit, 200);
    });
})();

// 侧边栏「📁 项目目录」折叠/展开（事件委托，不受 DOM 替换影响）
document.addEventListener('click', function (e) {
    var toggle = e.target.closest('.sidebar-catalog-toggle');
    if (toggle) {
        e.preventDefault();
        toggle.parentElement.classList.toggle('sidebar-catalog-collapsed');
    }
});

function initCatalogToggle() {
    if (document.querySelector('.sidebar-catalog-toggle')) return;
    var topLis = document.querySelectorAll('.sidebar-nav > ul > li');
    for (var i = 0; i < topLis.length; i++) {
        var li = topLis[i];
        var txt = li.childNodes[0];
        if (txt && txt.nodeType === 3 && txt.textContent.indexOf('项目目录') !== -1) {
            var span = document.createElement('span');
            span.textContent = txt.textContent;
            span.className = 'sidebar-catalog-toggle';
            li.replaceChild(span, txt);
            li.classList.add('sidebar-catalog-item');
            break;
        }
    }
}
setTimeout(initCatalogToggle, 400);
window.addEventListener('DOMContentLoaded', function () {
    setTimeout(initCatalogToggle, 400);
});
window.addEventListener('hashchange', function () {
    setTimeout(initCatalogToggle, 400);
});
