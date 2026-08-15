var defaultOptions = {
  headings: 'h1, h2',
  scope: '.markdown-section',

  // To make work
  title: 'Contents',
  listType: 'ul',  
}

// Element builders
var tocHeading = function(Title) {
  return document.createElement('h2').appendChild(
    document.createTextNode(Title)
  )
}

var aTag = function(src) {
  var a = document.createElement('a');
  var content = src.firstChild.innerHTML;

  // Use this to clip text w/ HTML in it.
  // https://github.com/arendjr/text-clipper
  a.innerHTML = content;
  a.href = src.firstChild.href;
  a.onclick = tocClick

  // In order to remove this gotta fix the styles.
  a.setAttribute('class', 'anchor');

  return a
};

var tocClick = function(e) {
  // 阻止浏览器原生锚点跳转（Docsify 异步渲染时内容未就绪，原生滚动必然错位）
  e.preventDefault();

  var divs = document.querySelectorAll('.page_toc .active');

  // Remove the previous classes
  [].forEach.call(divs, function(div) {
    div.setAttribute('class', 'anchor')
  });

  // Make sure this is attached to the parent not itself
  e.currentTarget.setAttribute('class', 'active')

  // 手动设置 hash 触发 Docsify 路由（滚动由 doneEach 统一处理）
  var href = e.currentTarget.getAttribute('href');
  if (href) {
    var hashIdx = href.indexOf('#');
    if (hashIdx >= 0) {
      window.location.hash = href.substring(hashIdx + 1);
    }
  }
};

// 主动滚动到指定 ID 的标题（带重试，处理异步渲染）
// 仅在 doneEach 中调用，避免与 tocClick 双重触发
var scrollToHeadingById = function(targetId) {
  var attempts = 0;
  var maxAttempts = 15;
  var tryScroll = function() {
    var el = document.getElementById(targetId);
    if (el) {
      var top = el.getBoundingClientRect().top + (window.pageYOffset || document.documentElement.scrollTop) - 20;
      window.scrollTo({ top: top, behavior: 'smooth' });
    } else if (attempts < maxAttempts) {
      attempts++;
      setTimeout(tryScroll, 150);
    }
  };
  // 首次延时 300ms，确保 Docsify 异步渲染完成
  setTimeout(tryScroll, 300);
};

// ===== Scroll-spy: 目录导航跟随文章标题滚动高亮 =====
var setupScrollSpy = function() {
  // 清理旧的滚动监听
  if (window.__tocScrollTimer) {
    clearTimeout(window.__tocScrollTimer);
    window.__tocScrollTimer = null;
  }
  if (window.__tocScrollHandler) {
    window.removeEventListener('scroll', window.__tocScrollHandler);
    window.__tocScrollHandler = null;
  }

  var nav = document.querySelector('.page_toc');
  if (!nav) return;

  var headings = document.querySelectorAll('.markdown-section h1[id], .markdown-section h2[id], .markdown-section h3[id], .markdown-section h4[id], .markdown-section h5[id], .markdown-section h6[id]');
  if (headings.length === 0) return;

  // 建立 heading.id → TOC链接 的映射
  // aTag() 中 a.href = src.firstChild.href 得到的是绝对URL，
  // 如 http://host/#/md/page?id=heading-id，需要提取 ?id= 参数值
  var linksMap = {};
  var tocLinks = nav.querySelectorAll('a.anchor');
  [].forEach.call(tocLinks, function(link) {
    var href = link.getAttribute('href');
    if (href) {
      // 匹配 ?id=xxx 或 &id=xxx，提取 heading ID
      var m = href.match(/[?&]id=([^&#]+)/);
      if (m) {
        linksMap[decodeURIComponent(m[1])] = link;
      }
    }
  });

  // 如果 href 解析不完整（映射数 < 标题数），回退到按索引匹配（更可靠）
  var headingsArr = Array.prototype.slice.call(headings);
  if (Object.keys(linksMap).length < headingsArr.length) {
    linksMap = {};
    var linksArr = Array.prototype.slice.call(tocLinks);
    for (var i = 0; i < headingsArr.length && i < linksArr.length; i++) {
      linksMap[headingsArr[i].id] = linksArr[i];
    }
  }

  var onScroll = function() {
    // 节流：100ms 内不重复执行
    if (window.__tocScrollTimer) return;
    window.__tocScrollTimer = setTimeout(function() {
      window.__tocScrollTimer = null;

      var scrollTop = window.pageYOffset || document.documentElement.scrollTop;
      var activeId = null;

      // 从最后一个标题向前找，找到第一个在滚动位置上方（或附近）的标题
      for (var i = headings.length - 1; i >= 0; i--) {
        var rect = headings[i].getBoundingClientRect();
        // 标题顶部在视口顶部以上（已滚过）或距离顶部 80px 以内
        if (rect.top <= 80) {
          activeId = headings[i].id;
          break;
        }
      }

      // 如果页面在顶部，激活第一个标题
      if (!activeId && scrollTop < 100 && headings.length > 0) {
        activeId = headings[0].id;
      }

      // 应用高亮：先无条件清除所有旧高亮，再按条件添加新高亮
      var currentActive = nav.querySelector('a.active');
      var targetLink = activeId ? linksMap[activeId] : null;

      // 只有目标变化时才操作（避免重复 DOM 操作）
      if (targetLink !== currentActive) {
        // 1. 先清除所有旧 active（无论新目标是否存在，都必须清理）
        var allActive = nav.querySelectorAll('a.active');
        [].forEach.call(allActive, function(a) {
          a.classList.remove('active');
        });

        // 2. 如果找到了新目标，添加 active
        if (targetLink) {
          targetLink.classList.add('active');

          // 让 TOC 中高亮项保持可见（自动滚动 TOC 容器）
          var tocContainer = document.querySelector('.page_toc');
          if (tocContainer) {
            var linkTop = targetLink.offsetTop;
            var containerScrollTop = tocContainer.scrollTop;
            var containerHeight = tocContainer.clientHeight;
            if (linkTop < containerScrollTop || linkTop > containerScrollTop + containerHeight - 40) {
              targetLink.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
            }
          }
        }
      }
    }, 100);
  };

  window.__tocScrollHandler = onScroll;
  window.addEventListener('scroll', onScroll, { passive: true });

  // 页面加载后立即触发一次
  setTimeout(onScroll, 200);
};

var createList = function(wrapper, count) {
  while (count--) {
    if(wrapper){
	    wrapper = wrapper.appendChild(
	      document.createElement('ul')
	    );
    }
    if (count) {
      wrapper = wrapper.appendChild(
        document.createElement('li')
      );
    }
  }

  return wrapper;
};

//------------------------------------------------------------------------

var getHeaders = function(selector) {
  var headings2 = document.querySelectorAll(selector);
  var ret = [];

  [].forEach.call(headings2, function(heading) {
    ret = ret.concat(heading);
  });

  return ret;
};

var getLevel = function(header) {
  var decs = header.match(/\d/g);

  return decs ? Math.min.apply(null, decs) : 1;
};

var jumpBack = function(currentWrapper, offset) {
  while (offset--) {
    currentWrapper = currentWrapper.parentElement;
  }

  return currentWrapper;
};

var buildTOC = function(options) {
  var ret = document.createElement('ul');
  var wrapper = ret;
  var lastLi = null;
  var selector = options.scope + ' ' + options.headings
  var headers = getHeaders(selector).filter(h => h.id);

  headers.reduce(function(prev, curr, index) {
    var currentLevel = getLevel(curr.tagName);
    var offset = currentLevel - prev;

    wrapper = (offset > 0)
      ? createList(lastLi || ret, offset)
      : jumpBack(wrapper, -offset * 2)

    wrapper = wrapper || ret;

    var li = document.createElement('li');

    wrapper.appendChild(li).appendChild(aTag(curr));

    lastLi = li;

    return currentLevel;
  }, getLevel(options.headings));

  return ret;
};

// Docsify plugin functions
function plugin(hook, vm) {
  var userOptions = vm.config.toc;

  hook.mounted(function () {
    var content = window.Docsify.dom.find(".content");
    if (content) {
      var nav = window.Docsify.dom.create("aside", "");
      window.Docsify.dom.toggleClass(nav, "add", "nav");
      window.Docsify.dom.before(content, nav);
    }
  });

  hook.doneEach(function () {
    var nav = document.querySelectorAll('.nav')[0]
    var t = Array.from(document.querySelectorAll('.nav'))

    if (!nav) {
      return;
    }

  	const toc = buildTOC(userOptions);

    // Just unset it for now.
    if (!toc.innerHTML) {
      nav.innerHTML = null
      return;
    }

    // Fix me in the future
		var title = document.createElement('p');
		title.innerHTML = userOptions.title;
		title.setAttribute('class', 'title');

		var container = document.createElement('div');
		container.setAttribute('class', 'page_toc');
		
		container.appendChild(title);
		container.appendChild(toc);

    // Existing TOC
    var tocChild = document.querySelectorAll('.nav .page_toc');

    if (tocChild.length > 0) {
      tocChild[0].parentNode.removeChild(tocChild[0]);
    }

    nav.appendChild(container);

    // 启动滚动监听：目录导航标题跟随文章标题滚动高亮
    setTimeout(setupScrollSpy, 200);

    // 内容渲染完毕后，主动滚动到 URL 中指定的标题（修复首次点击错位）
    var hash = window.location.hash;
    var idMatch = hash.match(/[?&]id=([^&#]+)/);
    if (idMatch) {
      scrollToHeadingById(decodeURIComponent(idMatch[1]));
    }
  });
}

// Docsify plugin options
window.$docsify['toc'] = Object.assign(defaultOptions, window.$docsify['toc']);
window.$docsify.plugins = [].concat(plugin, window.$docsify.plugins);
