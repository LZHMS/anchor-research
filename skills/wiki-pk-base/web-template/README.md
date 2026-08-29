# web-template — PKBase 静态展示站点

`wiki-pk-base` 技能内置的静态站点模板。技能把本目录**复制**到 PKBase 内的 `site/`，之后每次状态变更（`add` / `ingest` / `lint`）都**只重新生成 `data.js`** 来重建站点 —— 其余文件永不手改。

## 文件清单

| 文件 | 职责 | 重建时是否改动 |
| --- | --- | --- |
| `index.html` | 页面骨架：加载 Lato、LXGW WenKai GB Screen 字体、Font Awesome 图标、KaTeX（公式）、`style.css`、`data.js`、`app.js` | ❌ 不变 |
| `style.css` | academic-homepage 学术主页风格（参考 https://huai-chang.github.io/ ）：浅灰底 `#f8f9fa`、白色圆角卡片、固定顶栏导航、蓝色链接、出版卡片式列表 | ❌ 不变 |
| `app.js` | 零依赖渲染器：hash 路由（总览 / Wiki / Wiki 单类型全量 `#/wiki/<type>` / 原始材料 / 日志 / 单页阅读器）、全文搜索、mini markdown（含 `[[wikilink]]`、`![[embed]]` 图片与 `$...$` 公式） | ❌ 不变 |
| `data.js` | **数据层**：`window.PKBASE_DATA`，由技能从 vault 状态生成 | ✅ 每次重建覆盖 |
| `README.md` | 本文件 | ❌ 不变 |

## 预览

直接双击 `site/index.html`（`file://` 协议可用，无构建步骤、无本地服务器）。
字体与图标经 CDN 加载（Google Fonts / jsDelivr / Cloudflare），离线时回退到系统字体并隐藏图标。

## 中英文切换

- 导航栏右侧有「中文 / EN」切换（`.pk-lang`），点击即时切换当前视图语言，选择存 `localStorage`（key `pkbase_lang`），首次访问默认跟随浏览器语言（`navigator.language` 以 `zh` 开头 → 中文）。
- 所有 UI 文案集中在 `app.js` 顶部的 `I18N` 字典（`zh` / `en` 两个 key 集合，一一对应），视图代码只通过 `t('key')` / `tf('key', {vars})` 取词 —— **不要在任何视图里硬编码中文或英文文案**，新增文案时两种语言都要加。
- 注意：data.js 的 `pages` 数组名是复数（`sources/concepts/comparisons/queries`），而 i18n key 与 CSS 类（`type.*`、`b-*`、`cov-*`）是单数，`app.js` 用 `typeClass()` 做映射 —— 新增页面类型时两边都要加。

## 双语内容（bilingual vault）

切换语言不仅切换 UI 框架，也切换 **vault 内容**（当 PKBase 的 `SCHEMA.md` 配置了 `bilingual: true` 时）：

- **翻译文件约定**：wiki 里每个 base 页 `<slug>.md`（用 `default_lang` 语言写，是 canonical 文件）可配一个**同目录**的翻译文件 `<slug>.en.md`（`default_lang: zh` 时）或 `<slug>.zh.md`（`default_lang: en` 时），例如 `wiki/concepts/multimodal-learning/interactive-motion/flow-matching.en.md`。翻译文件结构与 base 页一致（同样的 frontmatter 字段 + 同样的正文小节），**不单独进 index.md**。
- **重建时合并**：技能重建 `data.js` 时，把翻译文件的 frontmatter / 正文合并进 base 页**同一条目**的 `_en`（或 `_zh`）字段：Page 为 `title_en` / `description_en` / `body_en`，`meta` 为 `name_en` / `description_en`（来自 `SCHEMA.md`），`raw[]` 为 `title_en` / `description_en`（可选标注），`log[]` 为 `title_en` / `detail_en`（可选）。翻译文件**不得**作为独立条目出现 —— 否则站点会显示重复条目。
- **回退规则**：`app.js` 用 `metaField()` / `L()` 两个 helper 取词 —— 当前 UI 语言有对应 `_en`/`_zh` 字段就用，没有就原样显示 base 语言文本。所以**缺译文的条目在另一语言界面下显示原文**，不会出现空白。
- **永不即时翻译**：站点从不自己翻译内容；`_en` 字段只来自显式的翻译文件。
- **搜索**：全文搜索的 haystack 同时包含原文与 `_en` 字段，英文也能搜到中文标题的页面（反之亦然）。
- **缓存**：`index.html` 里 `data.js?v=` / `app.js?v=` / `style.css?v=` 的版本戳必须随重建/改模板递增，否则浏览器会用 file:// 缓存的旧脚本。

## Wiki 页布局（v5 起）

`#/wiki` 不再按类型纵向铺开全部页面，改为**短页 + 并排栏目**，避免页面过长：

- **每日论文看看**：独立栏目（图标 `fa-newspaper`）。识别规则：页面 slug 形如 `daily-YYYY-MM-DD-*`，或 tags 含 `daily*`（如 `daily-ideas`）。最多显示最近 3 篇；这类页面**不再**出现在查询记录栏目里。没有每日页面时显示空态文案。
- **四类页面并排卡片**（来源页 / 概念页 / 对比页 / 查询记录）：`.wiki-cols` 两列网格（≤900px 单列），每个类型一张紧凑卡片（`.col-card` + `.pub-list.compact`），**只显示按 `updated` 降序的最近 5 篇**。
- **全量列表**：每张卡片右上角「查看全部 N 项 →」链接到 `#/wiki/<type>`（`viewWikiAll`），保留旧的 领域→主题 分组长列表，带「返回 Wiki」。领域筛选（`state.wikiDomain`）对栏目卡片与全量视图同样生效。

## 原始材料页布局（与 Wiki 页一致）

`#/raw` 同样**不再纵向铺开全部文件**：按材料类型（论文 / 文章 / 转录 / 素材 / 其他）并排成 `.wiki-cols` 栏目卡，每栏只按文件名 `YYYYMMDD-` 日期前缀降序显示**最近 5 个**（紧凑行，文件名新标签打开原始文件）；「查看全部 N 项 →」链接到 `#/raw/<type>`（`viewRawAll`）查看该类型的完整表格，带「返回原始材料」。

## data.js 约定（重建时必须遵守）

完整 schema 见 `data.js` 文件头部注释。要点：

- `meta`：`name` / `description` 取自 `SCHEMA.md`；`updated` = 最近一次重建时间
- `counts`：与各数组长度一致（sources/concepts/comparisons/queries/raw/log）
- `pages.<type>[].file`：相对 `wiki/<type>/` 的路径（`<domain>/<topic>/<slug>.md`），`domain` / `topic` 从路径第一、二级解析
- `pages.<type>[].body`：正文 markdown（去掉 frontmatter），**原样保留** `[[wikilink]]` 与 `$...$` / `$$...$$` 公式；wikilink 用完整 wiki 相对路径 `[[sources/<domain>/<topic>/<slug>|别名]]`
- **双语字段（仅 `bilingual: true` 时）**：条目可带 `title_en` / `description_en` / `body_en`（Page）、`name_en` / `description_en`（meta）、`title_en` / `description_en`（raw）、`title_en` / `detail_en`（log）—— 全部来自同目录翻译文件 `<slug>.en.md`，合并进同一条目而非独立条目；无译文的条目**省略**该字段（不要写空字符串），站点自动回退原文
- `raw[].file`：相对 `raw/` 的路径；`materialType` ∈ papers / articles / transcripts / assets / misc
- `log[]`：取自 `log.md`（+ 全部 `log-*.md`），新的在前，建议保留最近 50 条
- 所有字符串里含 `</script>` 的内容必须转义（body 里出现 `</script>` 时写成 `<\/script>`）

## 设计规范（改 style.css 前必读）

参照 academic-homepage（huai-chang.github.io）的学术主页风格：

- 背景 `#f8f9fa`，正文 `#212529`，次要 `#6c757d`，边框 `#dee2e6`
- 链接 `#3f7fb7`，hover `#3e92db` + 下划线
- 卡片：白底、`0.8rem` 圆角、`0 2px 4px rgba(0,0,0,.075)` 阴影、无边框
- 导航：fixed-top 56px、浅灰半透明（0.95）、shadow-sm、brand 20px
- 区块标题：h5 20px bold + `1px solid #dee2e6` 下边框
- 字体：Lato（西文）+ LXGW WenKai GB Screen（中文，仅 400 字重）
- 图标：Font Awesome 6（fa-solid / fa-regular），不用 emoji
- 页面列表：出版卡片式（彩色封面方块 + 标题 + 描述 + meta 徽章行）
- 四类页面配色：source 蓝 `#2c5f8a` / concept 绿 `#2e7d32` / comparison 橙 `#e65100` / query 紫 `#7b1fa2`
