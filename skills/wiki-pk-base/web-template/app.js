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
      'raw.title': '原始材料',
      'raw.desc': 'raw/ 目录清单 — 按 材料类型 / 领域 / 主题 三级组织，点击文件名可打开原始文件。',
      'raw.empty': 'raw/ 目录还是空的<br>用 add 捕获素材，用 ingest 编译成 wiki',
      'raw.col.file': '文件', 'raw.col.domain': '领域', 'raw.col.topic': '主题', 'raw.col.desc': '说明',
      'log.title': '操作日志',
      'log.desc': 'log.md 时间线 — 最近的操作记录（add / ingest / query / lint …）。',
      'log.empty': '还没有操作记录',
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
      'raw.title': 'Raw Material',
      'raw.desc': 'Inventory of raw/ — organized by material type / domain / topic; click a file name to open the original.',
      'raw.empty': 'raw/ is still empty.<br>Use add to capture material, ingest to compile it into the wiki.',
      'raw.col.file': 'File', 'raw.col.domain': 'Domain', 'raw.col.topic': 'Topic', 'raw.col.desc': 'Notes',
      'log.title': 'Operation Log',
      'log.desc': 'log.md timeline — recent operations (add / ingest / query / lint …).',
      'log.empty': 'No log entries yet',
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
  var ACT_ICON = { add: 'fa-plus', ingest: 'fa-file-import', query: 'fa-magnifying-glass', lint: 'fa-stethoscope', create: 'fa-seedling', update: 'fa-pen', archive: 'fa-box-archive', delete: 'fa-trash' };

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
    var p0 = String(path || '').replace(/\.md$/, '').trim();
    for (var i = 0; i < TYPE_ORDER.length; i++) {
      var list = DATA.pages[TYPE_ORDER[i]] || [];
      // accept both "<type>/<domain>/<topic>/<slug>" (wikilink form)
      // and "<domain>/<topic>/<slug>" (route/file form)
      var rel = p0;
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
    return row.replace(/^\|/, '').replace(/\|$/, '').split('|').map(function (s) { return s.trim(); });
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
    s = s.replace(/!\[([^\]]*)\]\(([^)\s]+)[^)]*\)/g, function (_, alt, url) {
      return '<img src="' + url + '" alt="' + alt + '">';
    });
    // [[path|label]] / [[path]]  →  clickable wikilink (resolved by click handler)
    s = s.replace(/\[\[([^\]|]+)(?:\|([^\]]+))?\]\]/g, function (_, path, label) {
      var p = path.trim().replace(/\.md$/, '');
      var l = (label || path).trim().replace(/\.md$/, '');
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

  function pubItem(type, p) {
    var title = L(p, 'title'), desc = L(p, 'description');
    var meta = '<span class="pk-badge b-' + typeClass(type) + '">' + t('type.' + typeClass(type)) + '</span>' +
      (p.domain ? '<i class="fa-solid fa-diagram-project"></i> ' + esc(p.domain) : '') +
      (p.topic ? '<i class="fa-solid fa-folder"></i> ' + esc(p.topic) : '') +
      (p.updated ? '<i class="fa-regular fa-calendar"></i> ' + esc(p.updated) : '');
    return '<div class="pub-item" data-go="#/page/' + type + '/' + encodeURIComponent(p.file) + '">' +
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

    var html = '<div class="pk-card pad-lg">';
    html += '<h2 class="profile-name">' + esc(name) + '</h2>';
    if (desc) html += '<div class="profile-desc">' + esc(desc) + '</div>';
    html += '<hr>' + statRow(DATA.counts);
    html += '<hr>';
    html += '<div class="section-title" style="margin-top:0"><i class="fa-solid fa-magnifying-glass"></i> ' + t('search.title') + '</div>';
    html += '<input class="pk-search" id="pk-search" type="text" placeholder="' + esc(t('search.placeholder')) + '" autocomplete="off">';
    html += '<div id="pk-search-results" style="margin-top:1rem"></div>';
    html += '</div>';

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

  function viewWiki() {
    renderNav('wiki');
    setPageTitle(t('nav.wiki'));

    var html = '<div class="pk-card pad-lg">';
    html += '<h2 class="profile-name">' + t('wiki.title') + '</h2>';
    html += '<div class="profile-desc">' + t('wiki.desc') + '</div>';
    if (state.wikiDomain) {
      html += '<div style="margin-top:0.75rem"><span class="pk-badge b-source">' + t('wiki.domain') + esc(state.wikiDomain) + '</span> ' +
        '<a href="#/wiki" data-clear-domain="1" style="font-size:14px">' + t('wiki.clear') + '</a></div>';
    }
    html += '</div>';

    var any = false;
    TYPE_ORDER.forEach(function (type) {
      var pages = (DATA.pages[type] || []).filter(function (p) {
        return !state.wikiDomain || p.domain === state.wikiDomain;
      });
      if (!pages.length) return;
      any = true;
      html += sectionTitle(TYPE_ICON[type], t('type.' + typeClass(type)), pages.length);
      html += '<div class="pk-card"><div class="pub-list">';

      // group domain → topic
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
    });

    if (!any) html += '<div class="empty-state big">' + t('wiki.empty') + '</div>';
    html += footer();
    app.innerHTML = html;
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
    }

    function rawName(r) {
      // original file name first; the translation is shown alongside when present
      var base = r.title || r.file.split('/').pop();
      var alt = r['title_' + lang];
      return alt && alt !== base ? base + ' · ' + alt : base;
    }

    var types = {};
    raws.forEach(function (r) { (types[r.materialType || 'misc'] = types[r.materialType || 'misc'] || []).push(r); });
    Object.keys(types).sort(function (a, b) { return rawSortKey(a) - rawSortKey(b) || a.localeCompare(b); }).forEach(function (mt) {
      var list = types[mt];
      html += sectionTitle(RAW_ICON[mt] || 'fa-file', t('raw.' + mt), list.length);
      html += '<div class="pk-card pk-table-wrap"><table class="pk-table"><thead><tr>' +
        '<th>' + t('raw.col.file') + '</th><th>' + t('raw.col.domain') + '</th><th>' + t('raw.col.topic') + '</th><th>' + t('raw.col.desc') + '</th></tr></thead><tbody>';
      list.forEach(function (r) {
        var name = rawName(r);
        var rd = L(r, 'description');
        html += '<tr><td><a href="../raw/' + esc(r.file) + '">' + esc(name) + '</a>' +
          '<div class="file-path">' + esc(r.file) + '</div></td>' +
          '<td>' + esc(r.domain || '—') + '</td>' +
          '<td>' + esc(r.topic || '—') + '</td>' +
          '<td>' + esc(rd) + '</td></tr>';
      });
      html += '</tbody></table></div>';
    });

    html += footer();
    app.innerHTML = html;
  }

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
      html += '<div class="pk-card"><ul class="news-list">';
      logs.forEach(function (l) {
        var actCls = 'b-' + (l.action || 'log').replace(/^query$/, 'query-act');
        if (!/^b-(add|ingest|query-act|lint|create|update|archive|delete|log)$/.test(actCls)) actCls = 'b-log';
        var icon = ACT_ICON[l.action] || 'fa-gear';
        var lt = L(l, 'title'), ld = L(l, 'detail');
        html += '<li class="news-item"><span class="news-date">' + esc(l.date) + (l.time ? ' ' + esc(l.time) : '') + '</span>' +
          '<div class="news-body"><span class="pk-badge ' + actCls + '"><i class="fa-solid ' + icon + '"></i> ' + esc(l.action) + '</span> ' +
          '<span class="news-title">' + esc(lt) + '</span>' +
          (ld ? '<div class="news-detail">' + esc(ld) + '</div>' : '') + '</div></li>';
      });
      html += '</ul></div>';
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

  /* ---------------- router ---------------- */

  function route() {
    var h = location.hash || '#/';
    if (h === '#' || h === '#/') { viewHome(); return; }
    if (h === '#/wiki') { viewWiki(); return; }
    if (h === '#/raw') { viewRaw(); return; }
    if (h === '#/log') { viewLog(); return; }
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

  window.addEventListener('hashchange', route);

  if (!DATA) {
    applyLang();
    app.innerHTML = '<div class="pk-card"><div class="empty-state big">PKBASE_DATA not found (data.js)<br>请先用 wiki-pk-base 技能初始化或重建站点 / Run the wiki-pk-base skill to initialize or rebuild the site.</div></div>';
    return;
  }
  applyLang();
  route();
})();
