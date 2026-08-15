// 搜索页面逻辑 — 兼容 VitePress SPA 路由
(function() {
  if (typeof window === 'undefined') return;

  var initialized = false;
  var allData = [];
  var dataLoaded = false;
  var dataLoading = false;

  // 动态获取 base 路径
  function getBase() {
    var baseEl = document.querySelector('meta[name="vitepress-base"]');
    if (baseEl) return baseEl.content;
    // 从当前路径推断（/doc/xxx → /doc/）
    var path = window.location.pathname;
    var m = path.match(/^(\/[^/]+\/)/);
    return m ? m[1] : '/';
  }

  // ========== 多时机触发初始化 ==========
  function tryInit() {
    if (initialized) return;
    // 兼容两种容器 ID
    var container = document.getElementById('search-page-app') || document.getElementById('search-page-container');
    if (!container) return;
    initialized = true;
    initSearch(container);
  }

  // 初次加载
  document.addEventListener('DOMContentLoaded', tryInit);
  // SPA 路由切换时通过 DOM 变化检测（避免劫持 pushState）
  var observer = new MutationObserver(function() {
    initialized = false;
    setTimeout(tryInit, 100);
    setTimeout(tryInit, 400);
  });
  // 观测 VitePress 内容区变化
  var contentEl = document.querySelector('.VPContent');
  if (contentEl) {
    observer.observe(contentEl, { childList: true, subtree: true });
  } else {
    observer.observe(document.body, { childList: true, subtree: true });
  }
  // 兜底轮询
  setTimeout(tryInit, 50);
  setTimeout(tryInit, 400);

  // ========== 搜索核心逻辑 ==========
  function initSearch(container) {
    // 加载数据（只加载一次）
    if (!dataLoading && !dataLoaded) {
      dataLoading = true;
      var base = getBase();
      fetch(base + 'search-data.json')
        .then(function(res) {
          if (!res.ok) throw new Error('HTTP ' + res.status);
          return res.json();
        })
        .then(function(data) {
          allData = data;
          dataLoaded = true;
          updateCount(data.length);
        })
        .catch(function(e) {
          console.error('搜索数据加载失败:', e);
          updateCount(-1);
        });
    }

    renderUI(container);

    // 返回搜索页时数据已缓存，直接更新计数
    if (dataLoaded) {
      updateCount(allData.length);
    }
  }

  function renderUI(container) {
    container.innerHTML = '';

    var html = '<div class="search-page">';
    html += '<div class="search-page-header">';
    html += '<h2>🔍 搜索文档</h2>';
    html += '<p class="search-page-desc" id="search-total-count">加载中…</p>';
    html += '</div>';
    html += '<div class="search-box">';
    html += '<span class="search-icon">🔍</span>';
    html += '<input type="text" id="search-page-query" placeholder="输入关键词，即时搜索..." class="search-page-input" autofocus />';
    html += '<span id="search-clear" class="search-clear" style="display:none">✕</span>';
    html += '</div>';
    html += '<div id="search-results-area"></div>';
    html += '</div>';
    container.innerHTML = html;

    var input = document.getElementById('search-page-query');
    var clearBtn = document.getElementById('search-clear');
    var resultsArea = document.getElementById('search-results-area');

    clearBtn.addEventListener('click', function() {
      input.value = '';
      input.dispatchEvent(new Event('input'));
      input.focus();
    });

    function doSearch(q) {
      if (!q) {
        resultsArea.innerHTML = '<div class="search-placeholder"><div class="search-placeholder-icon">📄</div><p>输入关键词开始搜索</p><p class="search-placeholder-hint">支持搜索文章标题和分类名称</p></div>';
        clearBtn.style.display = 'none';
        return;
      }
      clearBtn.style.display = '';

      if (!dataLoaded) {
        resultsArea.innerHTML = '<div class="search-placeholder"><p>数据加载中，请稍候…</p></div>';
        return;
      }

      var kw = q.toLowerCase();
      var results = allData.filter(function(item) {
        return item.t.toLowerCase().indexOf(kw) !== -1 || item.c.toLowerCase().indexOf(kw) !== -1;
      }).slice(0, 50);

      var rh = '<div class="search-results">';
      if (results.length) {
        rh += '<div class="search-count">找到 ' + results.length + ' 条结果</div>';
        rh += '<div class="search-list">';
        results.forEach(function(r) {
          rh += '<a href="' + r.l + '" class="search-item">';
          rh += '<div class="search-item-title">' + esc(r.t) + '</div>';
          rh += '<div class="search-item-cat">' + esc(r.c) + '</div>';
          rh += '</a>';
        });
        rh += '</div>';
      } else {
        rh += '<div class="search-count">未找到与 "' + esc(q) + '" 相关的结果</div>';
      }
      rh += '</div>';
      resultsArea.innerHTML = rh;
    }

    function esc(s) {
      var d = document.createElement('div');
      d.appendChild(document.createTextNode(s));
      return d.innerHTML;
    }

    doSearch('');

    var timer;
    input.addEventListener('input', function() {
      clearTimeout(timer);
      timer = setTimeout(function() { doSearch(input.value); }, 150);
    });
  }

  function updateCount(n) {
    var el = document.getElementById('search-total-count');
    if (el) {
      el.textContent = n > 0 ? '共收录 ' + n + ' 篇文章，输入关键词即时搜索' : '搜索数据暂不可用';
    }
  }
})();
