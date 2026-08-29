/* ============================================================
   PKBase static site — app.js (academic-homepage style)
   Reads window.PKBASE_DATA (data.js) and renders a
   hash-routed, dependency-free SPA:
     #/                      overview (profile card, stats, search, domains)
     #/wiki                  all wiki pages grouped type/domain/topic
     #/page/<type>/<path>    single wiki page reader
     #/raw                   raw material inventory
     #/log                   operation log timeline
   Works from file:// (double-click index.html).

   i18n: UI chrome is bilingual (中文 / EN), toggle in the navbar,
   persisted in localStorage (key: pkbase_lang), defaulting to the
   browser language.
   Bilingual vault: entries in data.js may carry <field>_zh / <field>_en
   translations (title, description, body; raw + log: title, description,
   detail; meta: name, description). When present, the current language's
   translation is shown; otherwise the original text is shown as written
   (never machine-translated — translations are files the user/agent wrote).
   ============================================================ */
(function () {
  'use strict';

  /* ---------------- i18n ---------------- */

  var I18N = {
    zh: {
      'nav.home': '总览', 'nav.wiki': '知识 Wiki', 'nav.raw': '原始材料', 'nav.log': '操作日志',
      'stat.source': '来源页', 'stat.concept': '概念页', 'stat.comparison': '对比页', 'stat.query': '查询', 'stat.raw': '原始材料', 'stat.log': '日志',
      'search.title': '搜索知识库',
      'search.placeholder': '标题 / 标签 / 领域 / 说明…',
      'search.results': '搜索结果',
      'search.nofound': '没有匹配「{q}」的内容',
      'domains.title': '知识领域',
      'domains.view': '{n} 个 wiki 页面 · 点击查看',
      'recent.title': '最近更新',
      'footer.powered': '由 wiki-pk-base 技能生成',
      'footer.updated': '最后更新',
      'footer.stats': '{n} 个 wiki 页面 / {m} 份原始材料',
      'type.source': '来源页', 'type.concept': '概念页', 'type.comparison': '对比页', 'type.query': '查询记录',
      'raw.papers': '论文', 'raw.articles': '文章', 'raw.transcripts': '转录', 'raw.assets': '素材', 'raw.misc': '其他',
      'wiki.title': '知识 Wiki',
      'wiki.desc': '已编译的结构化知识 — 来源页 / 概念页 / 对比页 / 查询记录，按 领域 → 主题 组织。',
      'wiki.domain': '当前领域：',
      'wiki.clear': '清除筛选',
      'wiki.empty': '知识库还没有编译出 wiki 页面<br>对原始材料执行 ingest 后，这里会出现内容',
      'wiki.viewAll': '查看全部 {n} 项 →',
      'wiki.back': '返回 Wiki',
      'wiki.recent': '最近 {n} 篇',
      'daily.title': '每日论文看看',
      'daily.empty': '还没有每日论文栏目<br>对当日新论文执行一次 query 后，这里会出现内容',
      'raw.title': '原始材料',
      'raw.desc': 'raw/ 目录清单 — 按 材料类型 / 领域 / 主题 三级组织，点击文件名可打开原始文件。',
      'raw.empty': 'raw/ 目录还是空的<br>用 add 捕获素材，用 ingest 编译成 wiki',
      'raw.col.file': '文件', 'raw.col.domain': '领域', 'raw.col.topic': '主题', 'raw.col.desc': '说明',
      'raw.back': '返回原始材料', 'raw.recent': '最近 {n} 个',
      'log.title': '操作日志',
      'log.desc': 'log.md 时间线 — 最近的操作记录（add / ingest / query / lint …）。',
      'log.empty': '还没有操作记录',
      'log.viewAll': '查看全部 {n} 条 →',
      'log.back': '返回操作日志',
      'log.recent': '最近 {n} 条',
      'article.updated': '更新于',
      'article.back': '返回 Wiki 列表',
      'notfound.title': '页面不存在',
      'notfound.body': '「{q}」不在 data.js 中<br>可能是 data.js 过期了，重新运行技能的 lint 即可重建',
      'unclassified': '未分类',
      'badge.raw': '原始材料'
    },
    en: {
      'nav.home': 'Home', 'nav.wiki': 'Wiki', 'nav.raw': 'Raw', 'nav.log': 'Log',
      'stat.source': 'Sources', 'stat.concept': 'Concepts', 'stat.comparison': 'Comparisons', 'stat.query': 'Queries', 'stat.raw': 'Raw files', 'stat.log': 'Log entries',
      'search.title': 'Search',
      'search.placeholder': 'Title / tag / domain / description…',
      'search.results': 'Results',
      'search.nofound': 'No results matching "{q}"',
      'domains.title': 'Domains',
      'domains.view': '{n} pages · click to view',
      'recent.title': 'Recently updated',
      'footer.powered': 'Powered by the wiki-pk-base skill',
      'footer.updated': 'Last updated',
      'footer.stats': '{n} wiki pages / {m} raw files',
      'type.source': 'Source', 'type.concept': 'Concept', 'type.comparison': 'Comparison', 'type.query': 'Query',
      'raw.papers': 'Papers', 'raw.articles': 'Articles', 'raw.transcripts': 'Transcripts', 'raw.assets': 'Assets', 'raw.misc': 'Misc',
      'wiki.title': 'Knowledge Wiki',
      'wiki.desc': 'Compiled, structured knowledge — source summaries / concepts / comparisons / filed queries, organized by domain → topic.',
      'wiki.domain': 'Domain:',
      'wiki.clear': 'Clear filter',
      'wiki.empty': 'No wiki pages compiled yet.<br>Run ingest on raw material to populate this view.',
      'wiki.viewAll': 'View all {n} →',
      'wiki.back': 'Back to Wiki',
      'wiki.recent': 'latest {n}',
      'daily.title': 'Daily Papers',
      'daily.empty': 'No daily papers yet.<br>Run a daily-paper query to populate this section.',
      'raw.title': 'Raw Material',
      'raw.desc': 'Inventory of raw/ — organized by material type / domain / topic; click a file name to open the original.',
      'raw.empty': 'raw/ is still empty.<br>Use add to capture material, ingest to compile it into the wiki.',
      'raw.col.file': 'File', 'raw.col.domain': 'Domain', 'raw.col.topic': 'Topic', 'raw.col.desc': 'Notes',
      'raw.back': 'Back to Raw', 'raw.recent': 'latest {n}',
      'log.title': 'Operation Log',
      'log.desc': 'log.md timeline — recent operations (add / ingest / query / lint …).',
      'log.empty': 'No log entries yet',
      'log.viewAll': 'View all {n} →',
      'log.back': 'Back to Log',
      'log.recent': 'latest {n}',
      'article.updated': 'Updated',
      'article.back': 'Back to Wiki',
      'notfound.title': 'Page not found',
      'notfound.body': '"{q}" is not in data.js.<br>data.js may be stale — run the skill\'s lint to rebuild it.',
      'unclassified': 'Unclassified',
      'badge.raw': 'Raw'
    }
  };

  var lang = null;
  try { lang = localStorage.getItem('pkbase_lang'); } catch (e) { /* ignore */ }
  if (lang !== 'zh' && lang !== 'en') {
    lang = String(navigator.language || '').toLowerCase().indexOf('zh') === 0 ? 'zh' : 'en';
  }

  function t(key) {
    var d = I18N[lang] || I18N.zh;
    if (d[key] != null) return d[key];
    return I18N.zh[key] != null ? I18N.zh[key] : key;
  }
  function tf(key, vars) {
    var s = t(key);
    if (vars) for (var k in vars) s = s.replace('{' + k + '}', vars[k]);
    return s;
  }
  function applyLang() {
    document.documentElement.lang = lang === 'zh' ? 'zh-CN' : 'en';
  }
  function setLang(l) {
    if (l !== 'zh' && l !== 'en' || l === lang) return;
    lang = l;
    try { localStorage.setItem('pkbase_lang', l); } catch (e) { /* ignore */ }
    applyLang();
    route(); // re-render current view in the new language
  }

  /* ---------------- state ---------------- */

  var DATA = window.PKBASE_DATA || null;

  /* Obsidian embed support: wiki bodies use ![[filename]] embeds (resolved
     by filename across the vault in Obsidian). Map each vault asset filename
     to its raw/ path from the data.js raw inventory so the same pages render
     inline images in the browser too (files live under ../raw relative to
     site/). */
  var ASSET_BY_NAME = {};
  (function () {
    if (!DATA) return;
    (DATA.raw || []).forEach(function (r) {
      var name = (r.file || '').split('/').pop();
      if (name && !ASSET_BY_NAME[name]) ASSET_BY_NAME[name] = r.file;
    });
  })();
  var app = document.getElementById('app');
  var navEl = document.getElementById('pk-nav');
  var state = { wikiDomain: null };

  var NAV_ITEMS = [
    { id: 'home', hash: '#/', key: 'nav.home' },
    { id: 'wiki', hash: '#/wiki', key: 'nav.wiki' },
    { id: 'raw', hash: '#/raw', key: 'nav.raw' },
    { id: 'log', hash: '#/log', key: 'nav.log' }
  ];
  var TYPE_ORDER = ['sources', 'concepts', 'comparisons', 'queries'];
  var TYPE_ICON = { sources: 'fa-file-lines', concepts: 'fa-lightbulb', comparisons: 'fa-scale-balanced', queries: 'fa-magnifying-glass' };
  var RAW_ORDER = ['papers', 'articles', 'transcripts', 'assets', 'misc'];
  var RAW_ICON = { papers: 'fa-file-pdf', articles: 'fa-newspaper', transcripts: 'fa-wave-square', assets: 'fa-image', misc: 'fa-file' };
  var ACT_ICON = { add: 'fa-plus', ingest: 'fa-file-import', query: 'fa-magnifying-glass', lint: 'fa-stethoscope', create: 'fa-seedling', update: 'fa-pen', fix: 'fa-wrench', archive: 'fa-box-archive', delete: 'fa-trash' };

  function rawSortKey(mt) {
    var i = RAW_ORDER.indexOf(mt);
    return i === -1 ? RAW_ORDER.length : i;
  }

  /* ---------------- helpers ---------------- */

  function esc(s) {
    return String(s == null ? '' : s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  function go(hash) { location.hash = hash; }

  function findPage(path) {
    // tolerate a trailing backslash (table-escaped '\|' separator leaking in)
    var p0 = String(path || '').replace(/\.md$/, '').replace(/\\$/, '').trim();
    for (var i = 0; i < TYPE_ORDER.length; i++) {
      var list = DATA.pages[TYPE_ORDER[i]] || [];
      // accept "<type>/<domain>/<topic>/<slug>" (wikilink form),
      // "wiki/<type>/..." (PKBase-root form used in vault bodies)
      // and "<domain>/<topic>/<slug>" (route/file form)
      var rel = p0;
      if (rel.indexOf('wiki/') === 0) rel = rel.slice(5);
      if (rel.indexOf(TYPE_ORDER[i] + '/') === 0) rel = rel.slice(TYPE_ORDER[i].length + 1);
      for (var j = 0; j < list.length; j++) {
        if (list[j].file === rel || list[j].file.replace(/\.md$/, '') === rel) {
          return { type: TYPE_ORDER[i], page: list[j] };
        }
      }
    }
    return null;
  }

  function totalPages() {
    var n = 0;
    TYPE_ORDER.forEach(function (tp) { n += (DATA.pages[tp] || []).length; });
    return n;
  }

  function setPageTitle(text) {
    var base = (DATA && metaField(DATA.meta, 'name')) || 'PKBase';
    document.title = text ? text + ' · ' + base : base;
  }

  /* bilingual content: metaField()/L() pick the entry's translation when the
     current UI language has one, else fall back to the original text */
  function metaField(m, field) {
    if (!m) return '';
    var alt = m[field + '_' + lang];
    if (alt) return alt;
    return m[field] || '';
  }
  function L(p, field) {
    if (!p) return '';
    var alt = p[field + '_' + lang];
    if (alt) return alt;
    return p[field] || '';
  }

  function renderNav(active) {
    navEl.innerHTML = NAV_ITEMS.map(function (it) {
      return '<a href="' + it.hash + '" data-go="' + it.hash + '" data-nav="' + it.id + '"' +
        (it.id === active ? ' class="active"' : '') + '>' + t(it.key) + '</a>';
    }).join('') +
    '<span class="pk-lang">' +
    '<a href="#" data-lang="zh"' + (lang === 'zh' ? ' class="active"' : '') + '>中文</a>' +
    '<a href="#" data-lang="en"' + (lang === 'en' ? ' class="active"' : '') + '>EN</a>' +
    '</span>';
  }

  /* ---------------- tiny markdown renderer ---------------- */

  function splitRow(row) {
    // stash [[path|label]] wikilinks first: the '|' inside them (plain, or
    // escaped as '\|' inside table cells) must not split the row; the
    // escape backslash is dropped
    var stashed = [];
    row = row.replace(/\[\[([^\]|]+)\|([^\]]+)\]\]/g, function (_, p, l) {
      stashed.push('[[' + p.trim().replace(/\\$/, '') + '|' + l.trim() + ']]');
      return '\u0003' + (stashed.length - 1) + '\u0003';
    });
    // any remaining escaped pipes are literal '|' characters in cell text
    row = row.replace(/\\\|/g, '\u0004');
    return row.replace(/^\|/, '').replace(/\|$/, '').split('|').map(function (s) {
      return s.trim()
        .replace(/\u0003(\d+)\u0003/g, function (_, n) { return stashed[+n]; })
        .replace(/\u0004/g, '|');
    });
  }

  function inline(s) {
    // stash $...$ BEFORE escaping so backslashes survive; auto-render
    // (KaTeX) picks the delimiters up after the DOM is built
    var mathSpans = [];
    s = s.replace(/\$([^\n$]+?)\$/g, function (_, m) {
      mathSpans.push(m);
      return '\u0001M' + (mathSpans.length - 1) + '\u0001';
    });
    s = esc(s);
    var codeSpans = [];
    s = s.replace(/`([^`]+)`/g, function (_, c) {
      codeSpans.push('<code>' + c + '</code>');
      return '\u0001' + (codeSpans.length - 1) + '\u0001';
    });
    // Obsidian embed ![[name.png]] / ![[name.png|alt]] → raw/ asset image
    s = s.replace(/!\[\[([^\]]+)\]\]/g, function (_, name) {
      var n = name.split('|')[0].trim();
      var f = ASSET_BY_NAME[n];
      if (f) return '<img src="../raw/' + f + '" alt="' + n + '" loading="lazy">';
      return '<span class="embed-missing" title="Asset not found in raw/: ' + n + '"><i class="fa-solid fa-image-slash"></i> ' + n + '</span>';
    });
    s = s.replace(/!\[([^\]]*)\]\(([^)\s]+)[^)]*\)/g, function (_, alt, url) {
      return '<img src="' + url + '" alt="' + alt + '">';
    });
    // [[path|label]] / [[path]]  →  clickable wikilink (resolved by click handler).
    // Without an explicit alias the visible text is the target page's title
    // (looked up in data.js), not the raw path.
    s = s.replace(/\[\[([^\]|]+)(?:\|([^\]]+))?\]\]/g, function (_, path, label) {
      // a trailing backslash is the table-escape of the '|' separator — drop it
      var p = path.trim().replace(/\\$/, '').replace(/\.md$/, '');
      var l;
      if (label) {
        l = label.trim().replace(/\.md$/, ''); // already HTML-escaped by the earlier esc(s)
      } else {
        var f = findPage(p);
        var title = f ? L(f.page, 'title') : '';
        l = title ? esc(title) : p; // title is raw data → escape; p is pre-escaped
      }
      return '<a class="wikilink" data-wiki="' + esc(p) + '">' + l + '</a>';
    });
    s = s.replace(/\[([^\]]+)\]\(([^)\s]+)(?:\s+&quot;[^&]*&quot;)?\)/g, function (_, tt, u) {
      var ext = /^https?:|^mailto:/.test(u) ? ' target="_blank" rel="noopener"' : '';
      return '<a href="' + u + '"' + ext + '>' + tt + '</a>';
    });
    s = s.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
    s = s.replace(/(^|[^*])\*([^*\n]+)\*/g, '$1<em>$2</em>');
    s = s.replace(/\u0001M(\d+)\u0001/g, function (_, n) {
      return '<span class="math-inline">$' + mathSpans[+n] + '$</span>';
    });
    s = s.replace(/\u0001(\d+)\u0001/g, function (_, n) { return codeSpans[+n]; });
    return s;
  }

  function renderMath(root) {
    if (!window.katex) return; // CDN unavailable → raw TeX stays readable
    var blocks = root.querySelectorAll('.formula[data-tex]');
    for (var i = 0; i < blocks.length; i++) {
      try {
        window.katex.render(blocks[i].getAttribute('data-tex'), blocks[i], { displayMode: true, throwOnError: false });
      } catch (e) { /* keep raw text */ }
    }
    if (window.renderMathInElement) {
      try {
        window.renderMathInElement(root, {
          delimiters: [{ left: '$$', right: '$$', display: true }, { left: '$', right: '$', display: false }],
          throwOnError: false
        });
      } catch (e) { /* ignore */ }
    }
  }

  function mdToHtml(md) {
    if (!md) return '';
    var src = String(md).replace(/\r\n?/g, '\n');
    var stash = [];
    function put(html) { stash.push(html); return '\u0000' + (stash.length - 1) + '\u0000'; }

    src = src.replace(/```[^\n]*\n([\s\S]*?)(?:```|$)/g, function (_, code) {
      return put('<pre><code>' + esc(code.replace(/\n$/, '')) + '</code></pre>');
    });
    // autolink bare URLs: "项目主页：https://…" → clickable. Code fences and
    // (below) display math are stashed already; URLs inside [text](url) /
    // ![alt](url) are skipped by the guard characters; trailing sentence
    // punctuation stays outside the link
    src = src.replace(/(^|[^(\[>"'=])(https?:\/\/[^\s<>()\[\]]+)/g, function (_, pre, url) {
      var m2 = url.match(/^(.*?)[.,;:!?]+$/);
      var clean = m2 ? m2[1] : url;
      var tail = m2 ? url.slice(clean.length) : '';
      return pre + '[' + clean + '](' + clean + ')' + tail;
    });
    // stash raw TeX in a data attribute; KaTeX fills the block in renderMath()
    var displayMath = [];
    src = src.replace(/\$\$([\s\S]+?)\$\$/g, function (_, tex) {
      displayMath.push(tex.trim());
      return put('<div class="formula" data-midx="' + (displayMath.length - 1) + '"></div>');
    });

    var lines = src.split('\n');
    var out = [];
    var i = 0;
    while (i < lines.length) {
      var tt = lines[i].trim();

      if (tt === '') { i++; continue; }
      if (/^\u0000\d+\u0000$/.test(tt)) { out.push(tt); i++; continue; }

      var h = tt.match(/^(#{1,4})\s+(.*)$/);
      if (h) {
        out.push('<h' + h[1].length + '>' + inline(h[2]) + '</h' + h[1].length + '>');
        i++; continue;
      }
      if (/^(-{3,}|\*{3,})$/.test(tt)) { out.push('<hr>'); i++; continue; }

      if (/^>/.test(tt)) {
        var q = [];
        while (i < lines.length && /^>/.test(lines[i].trim())) {
          q.push(lines[i].trim().replace(/^>\s?/, ''));
          i++;
        }
        out.push('<blockquote>' + inline(q.join(' ')) + '</blockquote>');
        continue;
      }

      if (/^\|/.test(tt) && i + 1 < lines.length && /^\|[\s:|-]+\|$/.test(lines[i + 1].trim())) {
        var head = splitRow(tt);
        i += 2;
        var rows = [];
        while (i < lines.length && /^\|/.test(lines[i].trim())) { rows.push(splitRow(lines[i].trim())); i++; }
        var tbl = '<table><thead><tr>' +
          head.map(function (c) { return '<th>' + inline(c) + '</th>'; }).join('') +
          '</tr></thead><tbody>' +
          rows.map(function (r) {
            return '<tr>' + r.map(function (c) { return '<td>' + inline(c) + '</td>'; }).join('') + '</tr>';
          }).join('') +
          '</tbody></table>';
        out.push(tbl);
        continue;
      }

      if (/^([-*]|\d+\.)\s+/.test(tt)) {
        var ordered = /^\d+\./.test(tt);
        var items = [];
        while (i < lines.length && /^([-*]|\d+\.)\s+/.test(lines[i].trim())) {
          items.push(lines[i].trim().replace(/^([-*]|\d+\.)\s+/, ''));
          i++;
        }
        out.push((ordered ? '<ol>' : '<ul>') +
          items.map(function (x) { return '<li>' + inline(x) + '</li>'; }).join('') +
          (ordered ? '</ol>' : '</ul>'));
        continue;
      }

      var p = [tt];
      i++;
      while (i < lines.length) {
        var n = lines[i].trim();
        if (n === '' || /^(#{1,4}\s|>|\||[-*]\s|\d+\.\s)/.test(n) ||
            /^(-{3,}|\*{3,})$/.test(n) || /^\u0000\d+\u0000$/.test(n)) break;
        p.push(n); i++;
      }
      out.push('<p>' + p.map(inline).join('<br>') + '</p>');
    }

    return out.join('\n')
      .replace(/\u0000(\d+)\u0000/g, function (_, n) { return stash[+n]; })
      .replace(/data-midx="(\d+)"/g, function (_, n) {
        return 'data-tex="' + displayMath[+n].replace(/"/g, '&quot;') + '"';
      });
  }

  /* ---------------- shared chrome ---------------- */

  function sectionTitle(icon, text, count, extra) {
    return '<div class="section-title"><i class="fa-solid ' + icon + '"></i> ' + text +
      (count != null ? ' <span class="count">' + count + '</span>' : '') + (extra || '') + '</div>';
  }

  function statRow(c) {
    c = c || {};
    var cells = [
      { i: 'fa-file-lines', n: c.sources, label: t('stat.source') },
      { i: 'fa-lightbulb', n: c.concepts, label: t('stat.concept') },
      { i: 'fa-scale-balanced', n: c.comparisons, label: t('stat.comparison') },
      { i: 'fa-magnifying-glass', n: c.queries, label: t('stat.query') },
      { i: 'fa-folder-open', n: c.raw, label: t('stat.raw') },
      { i: 'fa-clock-rotate-left', n: c.log, label: t('stat.log') }
    ];
    return '<div class="stat-row">' + cells.map(function (x) {
      return '<span class="stat-item"><i class="fa-solid ' + x.i + '"></i><b>' + (x.n == null ? 0 : x.n) + '</b>' + x.label + '</span>';
    }).join('') + '</div>';
  }

  function footer() {
    var m = DATA.meta || {};
    return '<div class="pk-footer">' + t('footer.powered') +
      (m.updated ? '<span class="sep">·</span>' + t('footer.updated') + ' ' + esc(m.updated) : '') +
      '<span class="sep">·</span>' + tf('footer.stats', { n: totalPages(), m: (DATA.raw || []).length }) +
      '</div>';
  }

  function tagLimit(tags, n) {
    tags = tags || [];
    var shown = tags.slice(0, n).map(function (tg) { return '<span class="pk-badge b-log">' + esc(tg) + '</span>'; }).join('');
    if (tags.length > n) shown += '<span class="pk-badge b-log">+' + (tags.length - n) + '</span>';
    return shown;
  }

  var TYPE_SINGULAR = { sources: 'source', concepts: 'concept', comparisons: 'comparison', queries: 'query' };
  function typeClass(type) {
    // data.js arrays are plural (sources/concepts/comparisons/queries);
    // css classes (b-*, cov-*) & i18n keys (type.*) are singular
    return TYPE_SINGULAR[type] || type;
  }

  function pubItem(type, p, hidden) {
    var title = L(p, 'title'), desc = L(p, 'description');
    var meta = '<span class="pk-badge b-' + typeClass(type) + '">' + t('type.' + typeClass(type)) + '</span>' +
      (p.domain ? '<i class="fa-solid fa-diagram-project"></i> ' + esc(p.domain) : '') +
      (p.topic ? '<i class="fa-solid fa-folder"></i> ' + esc(p.topic) : '') +
      (p.updated ? '<i class="fa-regular fa-calendar"></i> ' + esc(p.updated) : '');
    return '<div class="pub-item"' + (hidden ? ' style="display:none"' : '') +
      ' data-go="#/page/' + type + '/' + encodeURIComponent(p.file) + '">' +
      '<div class="pub-cover cov-' + typeClass(type) + '"><i class="fa-solid ' + TYPE_ICON[type] + '"></i></div>' +
      '<div class="pub-body"><div class="pub-title">' + esc(title) + '</div>' +
      (desc ? '<div class="pub-desc">' + esc(desc) + '</div>' : '') +
      '<div class="pub-meta">' + meta + (p.tags ? ' ' + tagLimit(p.tags, 4) : '') + '</div></div></div>';
  }

  /* ---------------- views ---------------- */

  function viewHome() {
    var m = DATA.meta || {};
    renderNav('home');
    var name = metaField(m, 'name') || 'PKBase';
    var desc = metaField(m, 'description');
    setPageTitle('');
    if (navEl) navEl.parentNode.querySelector('.pk-brand').textContent = name;

    // header card: name / description / stats on the left, search on the right;
    // search results render full-width below the card
    var html = '<div class="pk-card pad-lg profile-card">';
    html += '<div class="profile-main">';
    html += '<h2 class="profile-name">' + esc(name) + '</h2>';
    if (desc) html += '<div class="profile-desc">' + esc(desc) + '</div>';
    html += '<hr>' + statRow(DATA.counts);
    html += '</div>';
    html += '<div class="profile-search">';
    html += '<div class="search-label"><i class="fa-solid fa-magnifying-glass"></i> ' + t('search.title') + '</div>';
    html += '<input class="pk-search" id="pk-search" type="text" placeholder="' + esc(t('search.placeholder')) + '" autocomplete="off">';
    html += '</div></div>';
    html += '<div id="pk-search-results"></div>';

    // domains grid
    var domains = {};
    TYPE_ORDER.forEach(function (type) {
      (DATA.pages[type] || []).forEach(function (p) {
        var d = p.domain || t('unclassified');
        domains[d] = (domains[d] || 0) + 1;
      });
    });
    var dKeys = Object.keys(domains);
    if (dKeys.length) {
      html += sectionTitle('fa-sitemap', t('domains.title'), dKeys.length);
      html += '<div class="domain-grid">';
      dKeys.sort().forEach(function (d) {
        html += '<div class="domain-card" data-domain="' + esc(d) + '">' +
          '<div class="d-name"><i class="fa-solid fa-diagram-project"></i>' + esc(d) + '</div>' +
          '<div class="d-count">' + tf('domains.view', { n: domains[d] }) + '</div></div>';
      });
      html += '</div>';
    }

    // recent additions
    var recent = [];
    TYPE_ORDER.forEach(function (type) {
      (DATA.pages[type] || []).forEach(function (p) {
        if (p.updated) recent.push({ type: type, p: p });
      });
    });
    recent.sort(function (a, b) { return a.p.updated < b.p.updated ? 1 : -1; });
    if (recent.length) {
      html += sectionTitle('fa-clock-rotate-left', t('recent.title'), recent.length);
      html += '<div class="pk-card"><div class="pub-list">';
      recent.slice(0, 5).forEach(function (r) { html += pubItem(r.type, r.p); });
      html += '</div></div>';
    }

    html += footer();
    app.innerHTML = html;

    var input = document.getElementById('pk-search');
    if (input) input.addEventListener('input', function () { renderSearch(input.value); });
  }

  function renderSearch(q) {
    var box = document.getElementById('pk-search-results');
    if (!box) return;
    q = (q || '').trim().toLowerCase();
    if (q.length < 2) { box.innerHTML = ''; return; }

    var results = [];
    TYPE_ORDER.forEach(function (type) {
      (DATA.pages[type] || []).forEach(function (p) {
        // search across both the primary language and the translation (_en) fields
        var hay = [p.title, p.title_en, p.description, p.description_en, p.body, p.body_en, p.domain, p.topic, (p.tags || []).join(' ')].filter(Boolean).join(' ').toLowerCase();
        if (hay.indexOf(q) !== -1) results.push({ kind: 'page', type: type, p: p });
      });
    });
    (DATA.raw || []).forEach(function (r) {
      var hay = [r.title, r.title_en, r.description, r.description_en, r.domain, r.topic].filter(Boolean).join(' ').toLowerCase();
      if (hay.indexOf(q) !== -1) results.push({ kind: 'raw', r: r });
    });

    if (!results.length) {
      box.innerHTML = '<div class="empty-state">' + tf('search.nofound', { q: esc(q) }) + '</div>';
      return;
    }
    var html = '<div class="section-title"><i class="fa-solid fa-list"></i> ' + t('search.results') + ' <span class="count">' + results.length + '</span></div><div class="pk-card"><div class="pub-list">';
    results.slice(0, 30).forEach(function (x) {
      if (x.kind === 'page') {
        html += pubItem(x.type, x.p);
      } else {
        var rt = L(x.r, 'title'), rd = L(x.r, 'description');
        html += '<div class="pub-item">' +
          '<div class="pub-cover cov-query"><i class="fa-solid fa-folder-open"></i></div>' +
          '<div class="pub-body"><div class="pub-title">' + esc(rt) + '</div>' +
          (rd ? '<div class="pub-desc">' + esc(rd) + '</div>' : '') +
          '<div class="pub-meta"><span class="pk-badge b-log">' + t('badge.raw') + '</span>' +
          '<span class="path">' + esc(x.r.file) + '</span></div></div></div>';
      }
    });
    html += '</div></div>';
    box.innerHTML = html;
  }

  /* daily-paper pages: slug "daily-YYYY-MM-DD-*" or a "daily*" tag —
     they get their own section on the wiki page instead of the type column */
  function isDaily(p) {
    var slug = String(p.file || '').split('/').pop().replace(/\.md$/, '');
    if (/^daily-\d{4}-\d{2}-\d{2}/.test(slug)) return true;
    return (p.tags || []).some(function (tg) { return /^daily/.test(tg); });
  }

  function sortPagesDesc(pages) {
    return pages.slice().sort(function (a, b) {
      var da = a.updated || '', db = b.updated || '';
      if (da !== db) return da < db ? 1 : -1;
      return String(a.file).localeCompare(String(b.file));
    });
  }

  function allDailyPages() {
    var out = [];
    TYPE_ORDER.forEach(function (type) {
      (DATA.pages[type] || []).forEach(function (p) {
        if (isDaily(p)) out.push({ type: type, p: p });
      });
    });
    out.sort(function (a, b) {
      var da = a.p.updated || '', db = b.p.updated || '';
      if (da !== db) return da < db ? 1 : -1;
      return String(a.p.file).localeCompare(String(b.p.file));
    });
    return out;
  }

  function wikiHeaderCard() {
    var html = '<div class="pk-card pad-lg">';
    html += '<h2 class="profile-name">' + t('wiki.title') + '</h2>';
    html += '<div class="profile-desc">' + t('wiki.desc') + '</div>';
    if (state.wikiDomain) {
      html += '<div style="margin-top:0.75rem"><span class="pk-badge b-source">' + t('wiki.domain') + esc(state.wikiDomain) + '</span> ' +
        '<a href="#/wiki" data-clear-domain="1" style="font-size:14px">' + t('wiki.clear') + '</a></div>';
    }
    html += '</div>';
    return html;
  }

  var WIKI_COLUMN_LIMIT = 5;

  function viewWiki() {
    renderNav('wiki');
    setPageTitle(t('nav.wiki'));

    var html = wikiHeaderCard();

    // standalone "daily papers" column
    var daily = allDailyPages().filter(function (d) {
      return !state.wikiDomain || d.p.domain === state.wikiDomain;
    });
    html += sectionTitle('fa-newspaper', t('daily.title'), daily.length);
    if (daily.length) {
      html += '<div class="pk-card"><div class="pub-list">';
      daily.slice(0, 3).forEach(function (d) { html += pubItem(d.type, d.p); });
      html += '</div></div>';
    } else {
      html += '<div class="pk-card"><div class="empty-state">' + t('daily.empty') + '</div></div>';
    }

    // one compact card per page type, recent pages only, laid out side by side
    var cols = [];
    TYPE_ORDER.forEach(function (type) {
      var pages = sortPagesDesc((DATA.pages[type] || []).filter(function (p) {
        return (!state.wikiDomain || p.domain === state.wikiDomain) && !isDaily(p);
      }));
      if (pages.length) cols.push({ type: type, pages: pages });
    });
    if (cols.length) {
      html += '<div class="wiki-cols">';
      cols.forEach(function (c) {
        html += '<div class="pk-card col-card">';
        html += '<div class="col-head"><i class="fa-solid ' + TYPE_ICON[c.type] + '"></i> ' +
          t('type.' + typeClass(c.type)) +
          ' <span class="count">' + c.pages.length + '</span>' +
          ' <span class="col-note">' + tf('wiki.recent', { n: Math.min(WIKI_COLUMN_LIMIT, c.pages.length) }) + '</span>' +
          '<a class="col-all" href="#/wiki/' + c.type + '" data-go="#/wiki/' + c.type + '">' + tf('wiki.viewAll', { n: c.pages.length }) + '</a></div>';
        // render every page; the ones beyond the base limit start hidden and
        // are revealed by fillColumns() to even out the card heights per row
        html += '<div class="pub-list compact" data-note-key="wiki.recent">';
        c.pages.forEach(function (p, idx) { html += pubItem(c.type, p, idx >= WIKI_COLUMN_LIMIT); });
        html += '</div></div>';
      });
      html += '</div>';
    }

    if (!cols.length && !daily.length) html += '<div class="empty-state big">' + t('wiki.empty') + '</div>';
    html += footer();
    app.innerHTML = html;
    fillColumns();
  }

  /* full-length list of one page type (the old long view), reachable via
     #/wiki/<type> from a column's "view all" link */
  function viewWikiAll(type) {
    if (TYPE_ORDER.indexOf(type) === -1) { viewWiki(); return; }
    renderNav('wiki');
    setPageTitle(t('type.' + typeClass(type)));

    var html = '<div class="pk-card pad-lg">';
    html += '<div style="display:flex;align-items:center;gap:14px;flex-wrap:wrap">' +
      '<a class="back-link" style="margin-top:0" href="#/wiki" data-go="#/wiki"><i class="fa-solid fa-arrow-left"></i> ' + t('wiki.back') + '</a>' +
      '<h2 class="profile-name" style="margin:0"><i class="fa-solid ' + TYPE_ICON[type] + '" style="color:var(--pk-link)"></i> ' +
      t('type.' + typeClass(type)) + '</h2></div>';
    if (state.wikiDomain) {
      html += '<div style="margin-top:0.75rem"><span class="pk-badge b-source">' + t('wiki.domain') + esc(state.wikiDomain) + '</span> ' +
        '<a href="#/wiki" data-clear-domain="1" style="font-size:14px">' + t('wiki.clear') + '</a></div>';
    }
    html += '</div>';

    var pages = sortPagesDesc((DATA.pages[type] || []).filter(function (p) {
      return !state.wikiDomain || p.domain === state.wikiDomain;
    }));
    if (!pages.length) {
      html += '<div class="empty-state big">' + t('wiki.empty') + '</div>';
    } else {
      html += '<div class="pk-card"><div class="pub-list">';
      var domains = {};
      pages.forEach(function (p) {
        var d = p.domain || t('unclassified'), tp = p.topic || t('unclassified');
        (domains[d] = domains[d] || {})[tp] = (domains[d][tp] || []).concat(p);
      });
      Object.keys(domains).sort().forEach(function (d) {
        html += '<div class="group-h"><i class="fa-solid fa-diagram-project"></i> ' + esc(d) + '</div>';
        Object.keys(domains[d]).sort().forEach(function (tp) {
          html += '<div class="group-h"><span class="topic"><i class="fa-solid fa-folder"></i> ' + esc(tp) + '</span></div>';
          domains[d][tp].forEach(function (p) { html += pubItem(type, p); });
        });
      });
      html += '</div></div>';
    }
    html += footer();
    app.innerHTML = html;
  }

  /* original file name first; the translation is shown alongside when present */
  function rawName(r) {
    var base = r.title || r.file.split('/').pop();
    var alt = r['title_' + lang];
    return alt && alt !== base ? base + ' · ' + alt : base;
  }

  /* "recency" for raw files: the YYYYMMDD- prefix of the file name */
  function rawDateKey(r) {
    var m = String(r.file || '').split('/').pop().match(/^(\d{8})-/);
    return m ? m[1] : '00000000';
  }

  function sortRawDesc(list) {
    return list.slice().sort(function (a, b) {
      var da = rawDateKey(a), db = rawDateKey(b);
      if (da !== db) return da < db ? 1 : -1;
      return String(a.file).localeCompare(String(b.file));
    });
  }

  var RAW_COLUMN_LIMIT = 5;

  function rawRow(mt, r, hidden) {
    var rd = L(r, 'description');
    return '<div class="pub-item"' + (hidden ? ' style="display:none"' : '') + '>' +
      '<div class="pub-cover cov-raw"><i class="fa-solid ' + (RAW_ICON[mt] || 'fa-file') + '"></i></div>' +
      '<div class="pub-body"><div class="pub-title">' +
      '<a href="../raw/' + esc(r.file) + '" target="_blank" rel="noopener">' + esc(rawName(r)) + '</a></div>' +
      (rd ? '<div class="pub-desc">' + esc(rd) + '</div>' : '') +
      '<div class="pub-meta">' +
      '<span class="pk-badge b-log">' + esc(r.domain || '—') + '</span>' +
      (r.topic ? '<span class="pk-badge b-log">' + esc(r.topic) + '</span>' : '') +
      '<span class="path">' + esc(r.file) + '</span></div></div></div>';
  }

  function rawTable(list) {
    var html = '<div class="pk-card pk-table-wrap"><table class="pk-table"><thead><tr>' +
      '<th>' + t('raw.col.file') + '</th><th>' + t('raw.col.domain') + '</th><th>' + t('raw.col.topic') + '</th><th>' + t('raw.col.desc') + '</th></tr></thead><tbody>';
    list.forEach(function (r) {
      html += '<tr><td><a href="../raw/' + esc(r.file) + '" target="_blank" rel="noopener">' + esc(rawName(r)) + '</a>' +
        '<div class="file-path">' + esc(r.file) + '</div></td>' +
        '<td>' + esc(r.domain || '—') + '</td>' +
        '<td>' + esc(r.topic || '—') + '</td>' +
        '<td>' + esc(L(r, 'description')) + '</td></tr>';
    });
    html += '</tbody></table></div>';
    return html;
  }

  function rawTypeList(mt) {
    return (DATA.raw || []).filter(function (r) { return (r.materialType || 'misc') === mt; });
  }

  function viewRaw() {
    renderNav('raw');
    setPageTitle(t('nav.raw'));

    var html = '<div class="pk-card pad-lg">';
    html += '<h2 class="profile-name">' + t('raw.title') + '</h2>';
    html += '<div class="profile-desc">' + t('raw.desc') + '</div>';
    html += '</div>';

    var raws = DATA.raw || [];
    if (!raws.length) {
      html += '<div class="empty-state big">' + t('raw.empty') + '</div>';
    } else {
      // one compact card per material type, recent files only, side by side
      var types = {};
      raws.forEach(function (r) { (types[r.materialType || 'misc'] = types[r.materialType || 'misc'] || []).push(r); });
      html += '<div class="wiki-cols">';
      Object.keys(types).sort(function (a, b) { return rawSortKey(a) - rawSortKey(b) || a.localeCompare(b); }).forEach(function (mt) {
        var list = sortRawDesc(types[mt]);
        html += '<div class="pk-card col-card">';
        html += '<div class="col-head"><i class="fa-solid ' + (RAW_ICON[mt] || 'fa-file') + '"></i> ' +
          t('raw.' + mt) +
          ' <span class="count">' + list.length + '</span>' +
          ' <span class="col-note">' + tf('raw.recent', { n: Math.min(RAW_COLUMN_LIMIT, list.length) }) + '</span>' +
          '<a class="col-all" href="#/raw/' + mt + '" data-go="#/raw/' + mt + '">' + tf('wiki.viewAll', { n: list.length }) + '</a></div>';
        // same fill-on-render strategy as the wiki columns
        html += '<div class="pub-list compact" data-note-key="raw.recent">';
        list.forEach(function (r, idx) { html += rawRow(mt, r, idx >= RAW_COLUMN_LIMIT); });
        html += '</div></div>';
      });
      html += '</div>';
    }

    html += footer();
    app.innerHTML = html;
    fillColumns();
  }

  /* full inventory table of one material type, reachable via #/raw/<type> */
  function viewRawAll(mt) {
    renderNav('raw');
    setPageTitle(t('raw.' + mt));

    var html = '<div class="pk-card pad-lg">';
    html += '<div style="display:flex;align-items:center;gap:14px;flex-wrap:wrap">' +
      '<a class="back-link" style="margin-top:0" href="#/raw" data-go="#/raw"><i class="fa-solid fa-arrow-left"></i> ' + t('raw.back') + '</a>' +
      '<h2 class="profile-name" style="margin:0"><i class="fa-solid ' + (RAW_ICON[mt] || 'fa-file') + '" style="color:var(--pk-link)"></i> ' +
      t('raw.' + mt) + '</h2></div>';
    html += '</div>';

    var list = sortRawDesc(rawTypeList(mt));
    if (!list.length) {
      html += '<div class="empty-state big">' + t('raw.empty') + '</div>';
    } else {
      html += rawTable(list);
    }
    html += footer();
    app.innerHTML = html;
  }

  var LOG_ACTION_LIMIT = 5;
  var ACT_ORDER = ['ingest', 'add', 'query', 'update', 'create', 'lint', 'fix', 'archive', 'delete'];

  function actOrderKey(a) {
    var i = ACT_ORDER.indexOf(a);
    return i === -1 ? ACT_ORDER.length : i;
  }

  function actBadge(a) {
    // normalize: real log data mixes cases ("Add" vs "add", "Fix" vs "fix")
    a = String(a || 'log').toLowerCase();
    var actCls = 'b-' + a.replace(/^query$/, 'query-act');
    if (!/^b-(add|ingest|query-act|lint|create|update|fix|archive|delete|log)$/.test(actCls)) actCls = 'b-log';
    return '<span class="pk-badge ' + actCls + '"><i class="fa-solid ' + (ACT_ICON[a] || 'fa-gear') + '"></i> ' + esc(a) + '</span>';
  }

  function logItem(l, hidden) {
    var lt = L(l, 'title'), ld = L(l, 'detail');
    return '<li class="news-item"' + (hidden ? ' style="display:none"' : '') + '><span class="news-date">' + esc(l.date) + (l.time ? ' ' + esc(l.time) : '') + '</span>' +
      '<div class="news-body">' + actBadge(l.action || 'log') + ' ' +
      '<span class="news-title">' + esc(lt) + '</span>' +
      (ld ? '<div class="news-detail">' + esc(ld) + '</div>' : '') + '</div></li>';
  }

  function logTimeline(logs, twoCol) {
    return '<div class="pk-card"><ul class="news-list' + (twoCol ? ' news-cols' : '') + '">' +
      logs.map(function (l) { return logItem(l); }).join('') + '</ul></div>';
  }

  /* one compact card per action type, recent entries only, side by side */
  function viewLog() {
    renderNav('log');
    setPageTitle(t('nav.log'));

    var html = '<div class="pk-card pad-lg">';
    html += '<h2 class="profile-name">' + t('log.title') + '</h2>';
    html += '<div class="profile-desc">' + t('log.desc') + '</div>';
    html += '</div>';

    var logs = DATA.log || [];
    if (!logs.length) {
      html += '<div class="empty-state big">' + t('log.empty') + '</div>';
    } else {
      var byAct = {};
      logs.forEach(function (l) {
        var a = String(l.action || 'log').toLowerCase();
        (byAct[a] = byAct[a] || []).push(l);
      });
      html += '<div class="wiki-cols">';
      Object.keys(byAct).sort(function (a, b) { return actOrderKey(a) - actOrderKey(b) || a.localeCompare(b); }).forEach(function (a) {
        var list = byAct[a]; // data.js is newest-first, keep that order
        html += '<div class="pk-card col-card">';
        html += '<div class="col-head">' + actBadge(a) +
          ' <span class="count">' + list.length + '</span>' +
          ' <span class="col-note">' + tf('log.recent', { n: Math.min(LOG_ACTION_LIMIT, list.length) }) + '</span>' +
          '<a class="col-all" href="#/log/action/' + a + '" data-go="#/log/action/' + a + '">' + tf('log.viewAll', { n: list.length }) + '</a></div>';
        html += '<ul class="news-list compact">';
        list.forEach(function (l, idx) { html += logItem(l, idx >= LOG_ACTION_LIMIT); });
        html += '</ul></div>';
      });
      html += '</div>';
    }
    html += footer();
    app.innerHTML = html;
  }

  /* the complete chronological timeline (two columns on wide screens),
     reachable via #/log/all */
  function viewLogAll() {
    renderNav('log');
    setPageTitle(t('nav.log'));

    var logs = DATA.log || [];
    var html = '<div class="pk-card pad-lg">';
    html += '<div style="display:flex;align-items:center;gap:14px;flex-wrap:wrap">' +
      '<a class="back-link" style="margin-top:0" href="#/log" data-go="#/log"><i class="fa-solid fa-arrow-left"></i> ' + t('log.back') + '</a>' +
      '<h2 class="profile-name" style="margin:0"><i class="fa-solid fa-clock-rotate-left" style="color:var(--pk-link)"></i> ' +
      t('log.title') + ' <span class="count" style="font-size:14px;font-weight:400;color:var(--pk-muted)">' + logs.length + '</span></h2></div>';
    html += '</div>';

    if (!logs.length) {
      html += '<div class="empty-state big">' + t('log.empty') + '</div>';
    } else {
      html += logTimeline(logs, true);
    }
    html += footer();
    app.innerHTML = html;
  }

  /* every entry of one action type, reachable via #/log/action/<action> */
  function viewLogAction(a) {
    renderNav('log');
    var logs = (DATA.log || []).filter(function (l) { return String(l.action || 'log').toLowerCase() === a; });
    setPageTitle(a);

    var html = '<div class="pk-card pad-lg">';
    html += '<div style="display:flex;align-items:center;gap:14px;flex-wrap:wrap">' +
      '<a class="back-link" style="margin-top:0" href="#/log" data-go="#/log"><i class="fa-solid fa-arrow-left"></i> ' + t('log.back') + '</a>' +
      '<h2 class="profile-name" style="margin:0">' + actBadge(a) +
      ' <span class="count" style="font-size:14px;font-weight:400;color:var(--pk-muted)">' + logs.length + '</span></h2></div>';
    html += '</div>';

    if (!logs.length) {
      html += '<div class="empty-state big">' + t('log.empty') + '</div>';
    } else {
      html += logTimeline(logs, logs.length > 12);
    }
    html += footer();
    app.innerHTML = html;
  }

  function viewArticle(type, filePath) {
    var found = findPage(filePath);
    if (!found || found.type !== type) {
      renderNav('wiki');
      setPageTitle(t('notfound.title'));
      app.innerHTML = '<div class="pk-card"><div class="empty-state big">' + tf('notfound.body', { q: esc(filePath) }) + '</div></div>' + footer();
      return;
    }
    var p = found.page;
    renderNav('wiki');
    var pTitle = L(p, 'title');
    var pBody = L(p, 'body');
    // the header above already shows the page title; per the SCHEMA the body
    // starts with the same H1 — drop that duplicate leading heading
    pBody = String(pBody || '').replace(/^\s{0,3}#[^\n]*\n+/, '');
    setPageTitle(pTitle);

    var html = '<div class="pk-card article-card">';
    html += '<h1>' + esc(pTitle) + '</h1>';
    html += '<div class="article-meta"><span class="pk-badge b-' + typeClass(type) + '">' + t('type.' + typeClass(type)) + '</span>' +
      (p.domain ? '<i class="fa-solid fa-diagram-project"></i> ' + esc(p.domain) : '') +
      (p.topic ? '<i class="fa-solid fa-folder"></i> ' + esc(p.topic) : '') +
      (p.updated ? '<i class="fa-regular fa-calendar"></i> ' + t('article.updated') + ' ' + esc(p.updated) : '') +
      (p.source ? '<i class="fa-solid fa-file-import"></i> ' + esc(p.source) : '') +
      (p.tags ? ' ' + tagLimit(p.tags, 10) : '') + '</div>';
    html += '<div class="article-body">' + mdToHtml(pBody) + '</div>';
    html += '<a class="back-link" data-go="#/wiki" href="#/wiki"><i class="fa-solid fa-arrow-left"></i> ' + t('article.back') + '</a>';
    html += '</div>' + footer();
    app.innerHTML = html;
    var body = app.querySelector('.article-body');
    if (body) renderMath(body);
  }

  /* Reveal hidden column items so that the cards of each grid row end up
     the same height: instead of leaving white space under the sparser
     card, it shows a few more entries (never re-hides, so it is safe to
     re-run on resize / re-render). */
  function fillColumns() {
    var grids = app.querySelectorAll('.wiki-cols');
    for (var g = 0; g < grids.length; g++) {
      var grid = grids[g];
      var cols = (getComputedStyle(grid).gridTemplateColumns.match(/px/g) || []).length || 1;
      if (cols < 2) continue; // single column: no side-by-side card to match
      var cards = grid.children;
      for (var r = 0; r + cols <= cards.length; r += cols) {
        var row = Array.prototype.slice.call(cards, r, r + cols);
        // grid stretch would already have equalized the card heights, hiding
        // the content-height difference — measure with align-self: start,
        // then restore stretch after filling
        row.forEach(function (c) { c.style.alignSelf = 'start'; });
        var target = 0;
        row.forEach(function (c) { if (c.offsetHeight > target) target = c.offsetHeight; });
        row.forEach(function (c) {
          var hidden = c.querySelectorAll('.pub-item[style*="display:none"]');
          while (hidden.length && c.offsetHeight < target) {
            hidden[0].style.display = '';
            hidden = c.querySelectorAll('.pub-item[style*="display:none"]');
          }
        });
        row.forEach(function (c) { c.style.alignSelf = ''; });
        row.forEach(function (c) {
          var list = c.querySelector('.pub-list[data-note-key]');
          if (!list) return;
          var n = c.querySelectorAll('.pub-item:not([style*="display:none"])').length;
          var note = c.querySelector('.col-note');
          if (note) note.textContent = tf(list.getAttribute('data-note-key'), { n: n });
        });
      }
    }
  }
  var fillTimer = null;
  window.addEventListener('resize', function () {
    clearTimeout(fillTimer);
    fillTimer = setTimeout(fillColumns, 100);
  });

  /* ---------------- router ---------------- */

  function route() {
    var h = location.hash || '#/';
    if (h === '#' || h === '#/') { viewHome(); return; }
    if (h === '#/wiki') { viewWiki(); return; }
    var wm = h.match(/^#\/wiki\/([a-z]+)$/);
    if (wm) { viewWikiAll(wm[1]); return; }
    if (h === '#/raw') { viewRaw(); return; }
    var rm = h.match(/^#\/raw\/([a-z-]+)$/);
    if (rm) { viewRawAll(rm[1]); return; }
    if (h === '#/log') { viewLog(); return; }
    if (h === '#/log/all') { viewLogAll(); return; }
    var lam = h.match(/^#\/log\/action\/([a-z-]+)$/);
    if (lam) { viewLogAction(lam[1]); return; }
    var pm = h.match(/^#\/page\/([a-z]+)\/(.+)$/);
    if (pm) { viewArticle(pm[1], decodeURIComponent(pm[2])); return; }
    viewHome();
  }

  app.addEventListener('click', function (e) {
    var tg = e.target.closest ? e.target.closest('[data-go]') : null;
    if (tg) { e.preventDefault(); go(tg.getAttribute('data-go')); return; }
    if (e.target.closest && e.target.closest('[data-clear-domain]')) {
      e.preventDefault(); state.wikiDomain = null; viewWiki(); return;
    }
    if (e.target.closest && e.target.closest('[data-domain]')) {
      e.preventDefault();
      state.wikiDomain = e.target.closest('[data-domain]').getAttribute('data-domain');
      go('#/wiki'); return;
    }
    var w = e.target.closest ? e.target.closest('a.wikilink') : null;
    if (w) {
      e.preventDefault();
      var f = findPage(w.getAttribute('data-wiki'));
      if (f) go('#/page/' + f.type + '/' + encodeURIComponent(f.page.file));
    }
  });

  // navbar: language toggle + nav links (rendered into #pk-nav by renderNav)
  if (navEl) {
    navEl.addEventListener('click', function (e) {
      var lg = e.target.closest ? e.target.closest('[data-lang]') : null;
      if (lg) {
        e.preventDefault();
        setLang(lg.getAttribute('data-lang'));
        return;
      }
      var g = e.target.closest ? e.target.closest('[data-go]') : null;
      if (g) { e.preventDefault(); go(g.getAttribute('data-go')); }
    });
  }

  // hashchange: re-render, then jump back to the top — the browser keeps the
  // old scroll offset when the new hash matches no element id, which would
  // otherwise land the reader in the middle of the new page
  window.addEventListener('hashchange', function () {
    route();
    window.scrollTo(0, 0);
  });

  if (!DATA) {
    applyLang();
    app.innerHTML = '<div class="pk-card"><div class="empty-state big">PKBASE_DATA not found (data.js)<br>请先用 wiki-pk-base 技能初始化或重建站点 / Run the wiki-pk-base skill to initialize or rebuild the site.</div></div>';
    return;
  }
  applyLang();
  route();
})();
