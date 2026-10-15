# Anchor Research

> **Anchor first. Automate second.**（先下锚，再自动化）

一个 **anchor-first 的自动化科研（Auto Research）Skill 框架系统**。

**[English README → README.md](README.md)**

传统的 auto research 是“先自动化，再说”——把方向丢给 agent，然后一路放任自动探索：
自动跑实验、自动堆 baseline、自动改写方案……**方向偏了都无人察觉**。等论文最终写出来才发现解决的根本不是当初想解决的问题，几个 GPU 月的算力就这样白白浪费。

**Anchor Research 反其道而行之：在每一个关键阶段都先下锚，再启动自动化。**
这里的“锚点（Anchor）”绝不仅是开局写下的一份初始文档，而是**贯穿全科研生命周期的一系列确定性人机对齐门控**——
每个阶段的核心产物（文献语境、证据图景、问题定义、方法方案、实验计划、每轮里程碑决策、论文故事线、定稿手稿、海报展示）都必须**先向研究者呈现、充分沟通确认、固化为带校验哈希的锚点**，后续阶段的自动化操作才允许启动。在整个执行链路中，系统会持续回读上游锚点回答同一个核心问题：*“我们是否仍然在解决最初那个正确的问题？”*

```text
传统 auto research:        idea ──► 一路无引导自动探索 ──► 论文（方向早已跑偏，无人知晓）

Anchor Research:
                         文献调研与深度综述
                            │  📌 锚点 0: 语料边界与证据图景（经人审核确认）
                            ▼
                         研究方案（Ideas）
                            │  📌 锚点 1: Problem Anchor（问题定义与底线约束，经人审核确认）
                            │  📌 锚点 2: 核心贡献与方法方案 FINAL_PROPOSAL（机制与界限，经人审核确认）
                            ▼
                         实验路线规划
                            │  📌 锚点 3: 核心 claims + 任务清单 + 决策门控（经人审核确认）
                            ▼
                         实验运行与监控
                            │  📌 锚点 4: 追踪记录与里程碑决策（偏离/失败 → 暂停，向人请示决策）
                            ▼
                         论文规划（Plan）
                            │  📌 锚点 5: 真实核验数据、图表与叙事大纲（经人审核确认）
                            ▼
                         论文写作（Writing）
                            │  📌 锚点 6: 完整编译手稿与事实数据追溯（经人审核确认）
                            ▼
                         海报与展示交付
                            │  📌 锚点 7: 海报视觉版式与演讲脚本（逐 checkpoint 确认）
                            ▼
                         最终交付完成
```

**每个阶段 = 一次锚定（人机对齐门控） + 一次受锚约束的自动化执行。**

---

## 什么是“锚点（Anchor）”

锚点是**在某个科研阶段结束前，与研究者沟通确认并以不可变文件形式固化下来的核心判断**。它具备三个根本属性：

1. **已确认（Confirmed）**：绝非 agent 单方面生成的乐观草稿或虚构进度，而是由人类研究者明确签署确认的结论（confirm-then-commit）。大模型的自评高分、执行脚本的零返回值、静默或超时，均不可替代人类确认。
2. **可校验（Verifiable）**：后续每一轮、每一个阶段都必须通过完整字节 SHA-256 和规范 JSON 摘要回读上游锚点（`anchor check`），严格检测是否存在目标漂移。
3. **有权威（Authoritative）**：锚点的权威级别高于 agent 的自主决策。当自动化执行与锚点发生冲突时，系统必须服从锚点，或者立即暂停并提请人类重新锚定。

### 全流程锚点链明细

| # | 阶段 | 锚点（实体产物） | 如何与研究者对齐 | 负责 Skill |
|---|---|---|---|---|
| 0a | 文献调研 | **语料范围**（`CORPUS_STATE.json`） | 呈现源检索覆盖、合并文献清单与证据等级；必须获得 `corpus_approval` 才能发起综述 | `research-literature-review` |
| 0b | 文献综述 | **证据图景**（`SUMMARY_STATE.json`） | 呈现跨论文演化图景、公开缺陷与局限；必须获得 `summary_approval` 才能进入方案设计 | `research-literature-summary` |
| 1 | 问题界定 | **问题锚点**（`PROBLEM_ANCHOR.md`） | 文献驱动时呈现 4–6 个候选供显式挑选；起草锚点并在方法展开前获得 `anchor_approval` | `research-ideas` |
| 2 | 方法方案 | **核心贡献方案**（`FINAL_PROPOSAL.md`） | 锁定单一主导机制增量；多轮独立审稿人评审；在正式替换当前方案前必须获得 `proposal_approval` | `research-ideas` |
| 3 | 实验规划 | **核心 claims 与任务清单**（`EXPERIMENT_PLAN.md` + `EXPERIMENT_PLAN_STATE.json`） | 锁定验证指标、里程碑决策门控、算力上限；必须获得 `plan_approval` 确认任务清单映射 | `research-experiment-plannning` |
| 4 | 实验执行 | **运行追踪记录**（`EXPERIMENT_TRACKER.md`） | 校验计划任务投影；里程碑决策门控暂停等待人类指示；异常漂移或失败暂停等待策略决策（无自动击杀或超时自动放行） | `research-run-experiment` |
| 5 | 论文规划 | **审计结果、图表与叙事**（`PAPER_PLAN.md` + `PAPER_BUNDLE.json`） | 用真实预测与标签核算指标；生成可运行绘图/表格；独立评审；经用户确认循环通过完整 Bundle | `research-paper-plan` |
| 6 | 论文写作 | **定稿编译手稿**（`main.tex` + `main.pdf` + `MANUSCRIPT_MANIFEST.json`） | 依会议模板展开完整章节；每项数据与图注追溯至结果 ID；真实 LaTeX 编译；评审后经用户确认手稿 | `research-paper-writing` |
| 7 | 展示交付 | **会议海报与演讲**（`main.pdf` + `poster.pptx` + `poster.svg` + `POSTER_SPEECH.md`） | 从定稿论文提取 60 秒视觉叙事；内容大纲与卡片布局 checkpoints 默认等待用户确认；视觉复核与独立评审 | `research-paper-poster` |

> **关于反向重新锚定（Re-anchoring）**：锚点不是死板的化石。当代码实现与最初方案出现实质分歧时，`research-retrofit` 会将代码作为“实现真相（Ground Truth）”，但**绝不赋予代码凌驾于研究者原始问题的权力**。它会诊断分歧，在 `docs/research-retrofit/` 下起草对齐方案，并**向研究者提问：是调整代码以符合原问题，还是确认重新锚定问题（Re-anchor）以适应当前实现？** 严防 agent 擅自篡改科研目标。

---

## 系统架构与数据流

每个 Skill 都是专注自身任务的“自动化执行器”；真正维持科研航向不偏航的，是镶嵌在它们之间的 **📌 锚点门控**。上游产物必须通过锚点检验，方能流向下游。

```text
 ┌─ 知识与文献层 ───────────────────────────────────────────────────────────────────┐
 │  wiki-pk-base（PKBase 知识库） / research-daily-ideas（每日预印本流入）           │
 │        │                                                                        │
 │        ▼                                                                        │
 │  research-literature-review ──📌 锚点 0a（语料范围确认）──►                     │
 │  research-literature-summary ──📌 锚点 0b（证据图景确认）──►                    │
 └──────────────────────────────────────────┬──────────────────────────────────────┘
                                            ▼
 ┌─ 方案层（Proposal Layer）───────────────────────────────────────────────────────┐
 │  research-ideas:                                                                │
 │    候选路线挑选 ──► 📌 锚点 1: PROBLEM_ANCHOR.md（确认问题定义）               │
 │    机制深度细化 ──► 独立评审打磨 ──► 📌 锚点 2: FINAL_PROPOSAL.md（确认方案）   │
 └──────────────────────────────────────────┬──────────────────────────────────────┘
                                            ▼
 ┌─ 实验层（Experiment Layer）─────────────────────────────────────────────────────┐
 │  research-experiment-plannning:                                                 │
 │    Claim 映射 ──► 里程碑决策门控 ──► 📌 锚点 3: EXPERIMENT_PLAN.md              │
 │    核准任务清单投影 approved_task_inventory（确认实验规划）                      │
 │        │                                                                        │
 │        ▼                                                                        │
 │  research-run-experiment:                                                       │
 │    部署授权任务 ──► 评估预测指标 vs 真实标签                                   │
 │    辅助工具 1: research-structured-codebase（模块化注册表训练框架骨架）         │
 │    辅助工具 2: research-training-check（无副作用的指标质量诊断建议）           │
 │    📌 锚点 4: 单一追踪器 EXPERIMENT_TRACKER.md + 里程碑人机决策                 │
 │    （出现未授权漂移 / 运行失败 / 预算耗尽 → 暂停新工作，等待人机沟通）          │
 └──────────────────────────────────────────┬──────────────────────────────────────┘
                                            ▼
 ┌─ 论文与交付层（Paper & Delivery Layer）─────────────────────────────────────────┐
 │  research-paper-plan:                                                           │
 │    审计归一化结果 + 运行工程脚本绘制真实图表/表格                               │
 │    谋划故事线 ──► 📌 锚点 5: PAPER_PLAN.md & PAPER_BUNDLE.json（大纲与数据确认）│
 │        │                                                                        │
 │        ▼                                                                        │
 │  research-paper-writing:                                                        │
 │    细化章节写作 ──► 真实 LaTeX 编译 ──► 独立审查                                │
 │    📌 锚点 6: MANUSCRIPT_MANIFEST.json & 完整手稿（确认定稿论文）               │
 │        │                                                                        │
 │        ▼                                                                        │
 │  research-paper-poster:                                                         │
 │    📌 锚点 7: 海报内容计划与卡片布局确认（逐 checkpoint 人机确认）              │
 │    A0/A1 打印级 PDF + 原生/组件式 PPTX + SVG + 演讲脚本                         │
 └─────────────────────────────────────────────────────────────────────────────────┘

 ↺ research-retrofit: 代码 ↔ 方案回填对齐。将现有代码作为实现真相，诊断缺口，
   提请研究者明确决策是否重新下锚更新 PROBLEM_ANCHOR.md，经批准后方更新正式文档。
```

---

## Skills 清单一览

全部 12 个 Skill 均位于 `skills/` 下，遵循宿主中立原则（全面兼容 Claude Code、VS Code Copilot 等主流 Agent 环境），无任何硬编码的专有 CLI 或云端绑定：

### 📚 文献与知识层

| Skill | 角色职责 | 触发词示例 |
|---|---|---|
| [`research-literature-review`](skills/research-literature-review/SKILL.md) | 从 Zotero、PKBase、Obsidian、网络多源收集、去重与规范化文献，输出 `research_foundation_review.json`。在 `CORPUS_STATE.json` 中需要 `corpus_approval` | "find papers", "literature review", "文献调研" |
| [`research-literature-summary`](skills/research-literature-summary/SKILL.md) | 两阶段文献深度综述：逐篇论文由子代理分析，全局演化图景深度综合（`overview_summary.md`, `aggregate_report.md`）。在 `SUMMARY_STATE.json` 中需要 `summary_approval` | "summarize literature", "analyze papers", "文献综述" |
| [`wiki-pk-base`](skills/wiki-pk-base/SKILL.md) | 按照 Karpathy LLM Wiki 范式构建的持久化个人知识库（PKBase）：Markdown 知识网络 + 静态浏览器可视化站点。由人挑选源头，由 Agent 维护索引 | "wiki", "knowledge base", "PKBase", "知识库" |
| [`research-daily-ideas`](skills/research-daily-ideas/SKILL.md) | 可选的每日预印本流入工具：根据主题或 Zotero 兴趣抓取最新 arXiv 论文，提取源码与插图，撰写深度分析并归档入库 | "今日论文", "daily ideas", "arxiv daily" |

### 🧠 方案层（Proposal Layer）

| Skill | 角色职责 | 触发词示例 |
|---|---|---|
| [`research-ideas`](skills/research-ideas/SKILL.md) | 基于文献证据设计研究方案。无用户 idea 时生成 4–6 个候选供显式挑选；锁定用户确认的 `PROBLEM_ANCHOR.md`；多轮独立审查打磨机制；经用户批准后定稿 `FINAL_PROPOSAL.md` | "research ideas", "提出研究方案", "打磨idea", "refine my approach" |
| [`research-retrofit`](skills/research-retrofit/SKILL.md) | 代码 ↔ 方案反向回填对齐。视代码为实现真相，在 `docs/research-retrofit/CODE_ANALYSIS.md` 中诊断缺口；若涉及问题目标漂移，必须经用户显式批准才能重新下锚 | "update proposal from code", "通过代码更新方案", "retrofit proposal" |

### 🧪 实验层（Experiment Layer）

| Skill | 角色职责 | 触发词示例 |
|---|---|---|
| [`research-experiment-plannning`](skills/research-experiment-plannning/SKILL.md) | 将方案转换为 claim 驱动的执行路线图（`EXPERIMENT_PLAN.md`），设定里程碑决策门控与算力上限。计算规范任务投影 `approved_task_inventory` 并初始化单追踪器 `EXPERIMENT_TRACKER.md`。需要人类 `plan_approval` | "experiment plan", "规划实验", "ablation matrix", "run order" |
| [`research-run-experiment`](skills/research-run-experiment/SKILL.md) | 统一维护 `EXPERIMENT_TRACKER.md` 生命周期。校验任务是否符合核准的计划投影；部署授权任务；监控运行；评估直接比对数据集 Ground Truth 标签；在里程碑或遇阻时暂停等待人类决策 | "run experiment", "跑实验", "launch training", "review log", "实验进度" |
| [`research-structured-codebase`](skills/research-structured-codebase/SKILL.md) | 模块化、注册表驱动的 PyTorch 训练代码框架骨架（受 Dassl 启发）。作为 `research-run-experiment` 的可选实现助手 | "structured codebase", "代码库架构", "训练框架骨架" |
| [`research-training-check`](skills/research-training-check/SKILL.md) | 训练质量诊断助手：在训练期间读取指标与日志，诊断学习健康状况（NaN、发散、停滞），向 `docs/research-training-check/` 输出不可变建议报告。绝不直接杀进程或改写追踪器 | "check training", "monitor metrics", "is training healthy", "训练诊断" |

### ✍️ 论文与展示层（Paper & Presentation Layer）

| Skill | 角色职责 | 触发词示例 |
|---|---|---|
| [`research-paper-plan`](skills/research-paper-plan/SKILL.md) | 结果整理与论文规划：对照预测值与真实标签审计数据，在 `docs/research-paper-plan/analysis/` 运行绘图脚本，输出真实图表与代码映射，经独立评审后由用户确认 `PAPER_BUNDLE.json` | "paper plan", "论文规划", "规划论文", "整理实验结果" |
| [`research-paper-writing`](skills/research-paper-writing/SKILL.md) | 细化手稿写作：依据会议模板展开完整章节，程序化核验 BibTeX 引用，将所有数值与图注追溯至结果 ID，真实编译 LaTeX，独立评审后经人类批准定稿手稿 | "write paper", "draft manuscript", "论文写作", "compile paper" |
| [`research-paper-poster`](skills/research-paper-poster/SKILL.md) | 会议展示生成：从定稿论文与底层数据提炼 60 秒视觉叙事，排版 A0/A1 展板，卡片布局多重检验，导出可编辑与分卡片 PPTX、SVG 及演讲脚本（`POSTER_SPEECH.md`）。关键节点人机确认 | "make poster", "conference poster", "海报制作", "论文海报" |

---

## 典型工作流程（Happy Path）

```text
1.  /research-literature-review  ──► 从 Zotero/网络收集论文至规范化 JSON
        📌 人类锚点: 确认语料覆盖范围、来源策略与证据边界
2.  /research-literature-summary ──► 生成逐篇深入分析与宏观学术图景
        📌 人类锚点: 确认演化图景总结与已识别的开放缺陷
3.  /research-ideas              ──► 文献驱动生成 4–6 个候选路线
        📌 人类锚点: 挑选具体候选路线
        📌 人类锚点: 确认生成的问题锚点（核心瓶颈 + 明确非目标）
        ├── 启动宿主原生独立子代理进行多轮对抗性审查与机制修订
        📌 人类锚点: 确认定稿的方法方案（FINAL_PROPOSAL.md）
4.  /research-experiment-plannning ──► 将 claims 转化为里程碑模块与任务清单
        📌 人类锚点: 确认实验规划、决策门控与算力预算上限
5.  /research-run-experiment     ──► 部署授权任务，比对真实标签评估效果
        ├── （可选）/research-structured-codebase 搭建注册表代码库
        ├── （可选）/research-training-check 执行训练指标质量诊断
        📌 人类锚点: 里程碑决策门控与失败恢复必须由人类决策
6.  [若代码产生分歧] /research-retrofit ──► 代码逆向分析与缺口诊断
        📌 人类锚点: 重新锚定决策（修改实现 vs 重新确定问题定义）
7.  /research-paper-plan         ──► 审计实际结果，运行绘图脚本，策划故事线
        ├── 可运行分析脚本，生成 CSV/LaTeX 表格与清晰矢量图
        ├── 独立复核“代码-结果-主张”映射与数据真实性
        📌 人类锚点: 用户确认循环（审核确认 PAPER_BUNDLE.json）
8.  /research-paper-writing      ──► 依据会议模板撰写完整章节
        ├── 校验引文元数据，建立数值主张可追溯账本
        ├── 真实 LaTeX 编译器构建与独立同行评审
        📌 人类锚点: 确认最终编译手稿与其完整 Manifest
9.  /research-paper-poster       ──► 制作 A0/A1 展板、PPTX/SVG 导出与问答脚本
        📌 人类锚点: 确认海报内容计划与卡片视觉布局
```

---

## 实体产物与状态文件权威层级

所有项目状态文件统一存储于项目根目录的 `docs/` 下，均具备明确定义的 Schema 与内容校验哈希，构成整个科研工程的实体锚点：

| 物理文件位置 | 锚点属性 | 产生 Skill | 主要消费方 |
|---|---|---|---|
| `docs/research-literature-review/CORPUS_STATE.json` | 语料范围锚点 | `research-literature-review` | `research-literature-summary` |
| `docs/research-literature-summary/SUMMARY_STATE.json` | 证据图景锚点 | `research-literature-summary` | `research-ideas` |
| `docs/research-ideas/PROBLEM_ANCHOR.md` | 问题定义最高锚点：不可变瓶颈、底线约束、非目标 | `research-ideas` / `research-retrofit` | 后续所有阶段（反漂移基准） |
| `docs/research-ideas/FINAL_PROPOSAL.md` | 方法方案锚点：核心机制增量与最小充分验证 | `research-ideas` / `research-retrofit` | 实验规划、实验执行、论文规划 |
| `docs/research-experiment-plannning/EXPERIMENT_PLAN.md` | 实验路线锚点：claims、成功标准、里程碑门控 | `research-experiment-plannning` | 执行、代码对齐、论文规划 |
| `docs/research-experiment-plannning/EXPERIMENT_TRACKER.md` | 执行记录锚点：单一追踪器、实际指标、文件变更 | `research-experiment-plannning` / `research-run-experiment` | 研究者 + 论文规划 |
| `docs/research-paper-plan/PAPER_PLAN.md` + `PAPER_BUNDLE.json` | 叙事与数据锚点：已审计结果、表格、图表、高层叙事 | `research-paper-plan` | `research-paper-writing` |
| `docs/research-paper-writing/MANUSCRIPT_MANIFEST.json` | 手稿定稿锚点：PDF、TeX 源文件清单、构建记录、评审结论 | `research-paper-writing` | `research-paper-poster` |
| `docs/research-paper-poster/POSTER_STATE.json` | 交付状态锚点：海报 PDF、PPTX、SVG、演讲脚本 | `research-paper-poster` | 研究者（现场宣讲展示） |

---

## 阶段衔接门控协议（Stage Handoff Protocol）

详见核心协议规范文档 [`research-shared-references/anchor-gates.md`](skills/research-shared-references/anchor-gates.md)（或触发 [`research-shared-references`](skills/research-shared-references/SKILL.md)）：

1. **单次仅提一个 Offer**：当且仅当一个阶段实质完成且对应人类锚点已确认批准，系统才会在对话上下文中抛出唯一的 `NEXT_SKILL_HANDOFF` JSON 对象，标记 `status: awaiting_confirmation`。
2. **密码学摘要强绑定**：Handoff 必须显式枚举下游所需的所有输入文件绝对路径与 SHA-256 字节摘要（结构化数据采用规范 JSON 摘要），拒绝任何模糊的全局扫描或目录推测。
3. **权限绝不穿透与级联**：用户的单次确认（如回复“继续”或“可以”）**仅授权进入当前被提议的那一个下游技能**。它绝不自动授权后续阶段、绝不自动启动代码运行或模型训练，更绝不授权自动投稿或打印。
4. **输入变动即刻失效（Stale）**：如果任何已被绑定的上游文件在下游启动前发生变更，旧有的 Offer 即刻标记为 `stale`，必须重新呈现差异并由研究者重新确认。
5. **严禁超时自动放行**：静默、等待超时或开启自主运行标志，**永远不能代替研究者的显式批准**。

---

## 仓库目录结构

```text
anchor-research/
├── README.md                          # 英文主文档
├── README.zh.md                       # 中文主文档
└── skills/
    ├── research-shared-references/    # 全局人机锚点门控与协议规范
    │   ├── SKILL.md                   # 规范 Skill 定义与索引
    │   └── anchor-gates.md            # 完整人机门控细则与阶段衔接协议
    ├── research-literature-review/    # 文献收集、去重与规范化
    ├── research-literature-summary/   # 逐篇论文分析与全局图景综述
    ├── wiki-pk-base/                  # 持久化 LLM Wiki 知识库（PKBase）
    ├── research-daily-ideas/          # 每日 arXiv 论文自动发现与入库助手
    ├── research-ideas/                # 问题锚定与迭代审稿方案设计
    ├── research-retrofit/             # 代码反向回填对齐与人机重新下锚
    ├── research-experiment-plannning/ # Claim 映射、里程碑门控与任务初始化
    ├── research-run-experiment/       # 授权实验部署、运行监控与结果评估
    ├── research-structured-codebase/  # 模块化注册表训练框架骨架
    ├── research-training-check/       # 训练质量无副作用诊断建议工具
    ├── research-paper-plan/           # 结果审计归一化、工程制图与故事线规划
    ├── research-paper-writing/        # 会议模板排版、引用检验、编译与手稿定稿
    └── research-paper-poster/         # 会议海报排版、多格式转换与演讲脚本
```

---

## 开源协议

MIT 许可证。作者：Zhihao Li。
