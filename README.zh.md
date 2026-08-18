# Anchor Research

> **Anchor first. Automate second.**

一个 **anchor-first 的自动化科研（Auto Research）skill 系统**。

**[English README → README.md](README.md)**

传统的 auto research 是"先自动化，再说"——把方向丢给 agent，然后一路自动探索下去：
自动跑实验、自动堆 baseline、自动改写方案……**方向错了都不知道**，等论文写出来才发现解决的根本不是当初想解决的问题，
几个 GPU 月就白费了。

**Anchor Research 反过来：在每一个阶段都先下锚，再自动化。**
"锚点（anchor）"不只是开头的那份 Problem Anchor，而是**贯穿全流程的一系列对齐点**——
每个阶段的产物（问题定义、方法方案、实验 claim、run 成功标准、论文故事线）都必须**先与研究者沟通确认、固化为锚点**，
后续的所有自动化动作才允许展开，并且随时可以用锚点校验"我还走在正确的方向上吗"。

```
传统 auto research:        idea ──► 一路自动探索 ──► 论文（方向可能早已跑偏，无人察觉）

Anchor Research:           idea
                              │  📌 锚点 1: Problem Anchor（与人确认问题定义）
                              ▼
                            refine
                              │  📌 锚点 2: 核心贡献 / FINAL_PROPOSAL（与人确认方案）
                              ▼
                            experiment plan
                              │  📌 锚点 3: 核心 claim + 成功标准 + decision gate（与人确认）
                              ▼
                            run & monitor
                              │  📌 锚点 4: run 期望 vs 实际（偏离锚点 → 停下、回锚、再谈）
                              ▼
                            paper plan
                              │  📌 锚点 5: 论文故事线 / PAPER_PLAN（与人确认）
                              ▼
                            写作 / 海报
                              │  📌 锚点 6: 海报版式与 figure（逐 checkpoint 确认）
                              ▼
                            交付
```

**每个阶段 = 一次锚定（人 + agent 对齐） + 一次受锚约束的自动化执行。**

---

## 什么是"锚点"

锚点是**一个阶段结束前，与研究者沟通确认并固化下来的判断**，它具备三个性质：

1. **已确认**：不是 agent 单方面生成的产物，而是与用户对齐后写下的结论（confirm-then-commit）。
2. **可校验**：后续每一轮、每一个 run 都要回读锚点做 **anchor check**，检测是否漂移（drift warning）。
3. **有权威**：锚点之间的优先级高于 agent 的自主决策——自动化在冲突时必须服从锚点，或停下来请求人重新锚定。

### 全流程的锚点链

| # | 阶段 | 锚点（产物） | 与人的对齐方式 | 谁负责 |
|---|------|--------------|----------------|--------|
| 1 | 方案打磨 | **Problem Anchor**（`PROBLEM_ANCHOR.md`）——不可变的问题定义、瓶颈、底线约束 | Phase 0 从用户意图提取，每轮 verbatim 复制并做 anchor check | research-refine |
| 2 | 方案打磨 | **核心贡献 / 方法方案**（`FINAL_PROPOSAL.md`）——一句话主导贡献 + 最小充分机制 | 迭代 review 直到评分达标，方案定稿即锚定 | research-refine |
| 3 | 实验规划 | **核心 claim + 成功标准**（`EXPERIMENT_PLAN.md`）——最多 2 个主 claim、每个 run 的 success criterion、decision gate（stop/go） | plan 中的 decision gate 是显式的人机决策点；run 失败时向人报告并等待确认（超时才自动回锚调整） | experiment-plan / experiment-bridge |
| 4 | 实验执行 | **run 记录**（`EXPERIMENT_TRACKER.md`）——每个 run 的期望 vs 实际、代码变更清单 | 失败 run 的策略调整需人确认（auto-resume 只是超时兜底，且必须回写 plan/tracker 留痕） | run-experiment |
| 5 | 论文规划 | **论文故事线**（`PAPER_PLAN.md`）——one clear contribution 的 What / Why / So What | 显式的 **User Confirmation Loop**：大纲定稿前必须经用户确认 | research-paper-plan |
| 6 | 海报/交付 | **海报视觉锚点**（版式、figure 选择、60 秒故事） | 每个 checkpoint **默认等待用户显式确认**（`AUTO_PROCEED = false`） | research-paper-poster |

> 注意方向性：锚点不是"只读化石"。当代码与方案产生实质分歧时，`research-retrofit` 会以代码为 Ground Truth
> **重新锚定**（更新 `PROBLEM_ANCHOR.md` 与 `FINAL_PROPOSAL.md`）——重新下锚同样要走"沟通确认"这一步，
> 而不是让 agent 悄悄改方向。

---

## 系统架构

每个 skill 都是"自动化执行器"；真正保证方向正确的是夹在它们之间的 **📌 锚点**
（与研究者沟通确认后固化的对齐点）。自动化产物必须经过锚点确认，才能成为下一阶段的输入。

```
  知识库                文献层                    方案层
 ┌──────────┐        ┌────────────────────┐    ┌─────────────────────────┐
 │ wiki-pk- │        │ research-literature│    │ research-refine         │
 │ base     │───────►│ -review            │───►│  冻结 Problem Anchor    │
 │(PKBase)  │        │ research-literature│    │  迭代 review 打磨方案    │
 └──────────┘        │ -summary           │    └───────────┬─────────────┘
                     └────────────────────┘                │
                   📌 锚点 1+2: PROBLEM_ANCHOR.md          │ 📌 与人确认
                                  FINAL_PROPOSAL.md        │
                                                          ▼
  交付层            写作层                      实验层     ┌─────────────────────┐
 ┌──────────────────────┐  ┌────────────────────┐        │ experiment-plan     │
 │ research-paper-      │  │ research-paper-plan│◄───────│ claim→evidence→run  │
 │ poster               │◄─│ (PAPER_PLAN.md)    │        │ order + decision    │
 │(A0/A1 PDF + PPTX)    │  └────────────────────┘        │ gate                │
 └──────────────────────┘  📌 锚点 5: 论文故事线          └──────────┬──────────┘
        📌 锚点 6: 海报版式/figure（逐 checkpoint 等人确认）           │ 📌 锚点 3: claim+
                                                                    │  成功标准确认
  执行层                    ┌──────────────────┐   ┌─────────────────▼─────────┐
 ┌──────────────────────┐   │ structured-      │   │ experiment-bridge         │
 │ run-experiment       │◄──│ codebase         │   │ (plan → EXPERIMENT_       │
 │(实现/部署/评估)       │   │(注册表式训练框架) │   │  TRACKER.md)              │
 │ training-check       │   └──────────────────┘   └─────────────────┬─────────┘
 └──────────┬───────────┘                                            │
            │  📌 锚点 4: 每个 run 的期望 vs 实际（失败需人确认策略）    │
            └────── 偏离锚点 → 停下回锚 → 与人重新对齐 ────────────────┤
            │                                                        │
            └──────── research-retrofit（代码↔方案对齐，重新锚定）◄────┘
```

锚点的"回读"是常态而非例外：refine 每轮做 anchor check（drift warning）、
run-experiment 用 plan 里的 success criterion 对照实际结果、paper-plan 用 proposal 校验故事线——
任何一环发现漂移，流程就停在该锚点处等人重新下锚，而不是带病继续跑。

---

## Skills 一览

### 🧠 方案层（Proposal Layer）

| Skill | 作用 | 触发示例 |
|-------|------|----------|
| [`research-refine`](skills/research-refine/SKILL.md) | **系统核心。** 将模糊方向打磨为 problem-anchored、elegant、frontier-aware 的方法方案。Phase 0 冻结 `PROBLEM_ANCHOR.md`，每轮做 anchor check（drift warning），多轮隔离 reviewer 打分直到 ≥ 9 分 | "refine my approach" / "细化研究方案" |
| [`research-retrofit`](skills/research-retrofit/SKILL.md) | 代码 ↔ 方案对齐：以已实现代码为 Ground Truth 反向更新 proposal，并做 rebuttal 式投稿就绪度审查 | "通过代码更新方案" |

### 📚 文献层（Literature Layer）

| Skill | 作用 |
|-------|------|
| [`research-literature-review`](skills/research-literature-review/SKILL.md) | 从 Zotero / Obsidian / 网络多源收集、去重、归一化论文，输出统一的 `research_foundation_review.json` |
| [`research-literature-summary`](skills/research-literature-summary/SKILL.md) | 两阶段深度分析：全局研究图景综述（方法谱系、数据集、指标、open gaps）+ 逐篇 LLM 精读（调用 `summarize_review.py`，支持 OpenAI 兼容 API / Ollama） |
| [`wiki-pk-base`](skills/wiki-pk-base/SKILL.md) | 基于 Karpathy LLM Wiki 模式的持久化个人知识库（PKBase）：编译一次、持续维护、可查询、可 lint |

### 🧪 实验层（Experiment Layer）

| Skill | 作用 |
|-------|------|
| [`experiment-plan`](skills/experiment-plan/SKILL.md) | 把 proposal 转成 **claim → evidence → block → run-order** 的执行路线图（must-run vs nice-to-have、决策门、compute budget） |
| [`experiment-bridge`](skills/experiment-bridge/SKILL.md) | 解析 plan 的里程碑，初始化 `EXPERIMENT_TRACKER.md` 逐 run 追踪表 |
| [`structured-codebase`](skills/structured-codebase/SKILL.md) | 模块化、注册表驱动的训练框架（受 D2L/Dassl 启发），实验代码的标准落点 |
| [`run-experiment`](skills/run-experiment/SKILL.md) | 实现代码 → 记录文件变更 → GPU 校验 → 部署 → 评估 → 失败时自主策略调整闭环 |
| [`training-check`](skills/training-check/SKILL.md) | 周期性读取 WandB 指标，从"学习质量"（NaN、loss 发散、趋势）而非系统健康角度早期止损 |

### ✍️ 写作层（Writing Layer）

| Skill | 作用 |
|-------|------|
| [`research-paper-plan`](skills/research-paper-plan/SKILL.md) | 从项目材料生成 section-by-section 论文大纲（`PAPER_PLAN.md`），支持 ICLR / NeurIPS / ICML / ACL / AAAI / IEEE 等 venue 约束 |
| [`research-paper-hermes`](skills/research-paper-hermes/SKILL.md) | 端到端论文写作管线：实验分析、起草、自审、修订、投稿，覆盖 NeurIPS / ICML / ICLR / ACL / AAAI / COLM 模板，引用程序化校验（拒绝幻觉引用） |
| [`research-paper-poster`](skills/research-paper-poster/SKILL.md) | 从编译后的论文生成 A0/A1 会议海报（article + tcbposter → PDF / PPTX / SVG）+ 演讲脚本 |

---

## 典型工作流（Happy Path）

```
1. /wiki-pk-base              建立/维护领域知识库（PKBase）
2. /research-literature-review 收集文献 → artifacts/research_foundation_review.json
3. /research-literature-summary 文献深度综述 → Obsidian ResearchPapers/{topic}/
4. /research-refine           冻结 PROBLEM_ANCHOR.md，迭代打磨 → FINAL_PROPOSAL.md
       📌 锚点: 问题定义 + 核心贡献，与人确认
5. /experiment-plan           claim-driven 实验路线图 → EXPERIMENT_PLAN.md
       📌 锚点: 核心 claim + 成功标准 + decision gate，与人确认
6. /experiment-bridge         初始化追踪器 → EXPERIMENT_TRACKER.md
7. /structured-codebase       搭建/复用注册表式训练代码库
8. /run-experiment            逐 run 实现-部署-评估（配合 /training-check 监控）
       📌 锚点: run 失败时停下，与人确认策略调整后再继续
9. /research-retrofit         实验后期：代码反哺方案，重新锚定 PROBLEM_ANCHOR / FINAL_PROPOSAL
10. /research-paper-plan      生成论文大纲 PAPER_PLAN.md
       📌 锚点: 论文故事线（What/Why/So What），User Confirmation Loop
11. /research-paper-hermes    写作 → 自审 → 修订 → 投稿
12. /research-paper-poster    录用后：海报 + 演讲脚本（逐 checkpoint 确认）
```

关键状态文件（`docs/refine-logs/` 下）——**它们就是锚点的实体**，按权威级别从高到低排列：

| 文件 | 锚点性质 | 产生者 | 消费者 |
|------|----------|--------|--------|
| `PROBLEM_ANCHOR.md` | 最高权威：不可变问题定义，每轮 verbatim 复用 | research-refine / research-retrofit（重新锚定） | 全部（anchor check 基准） |
| `FINAL_PROPOSAL.md` | 方案锚点：核心贡献与机制定稿 | research-refine / research-retrofit | experiment-plan、run-experiment、paper-plan |
| `EXPERIMENT_PLAN.md` | 实验锚点：claim、成功标准、decision gate | experiment-plan / run-experiment（经人确认的策略更新） | experiment-bridge、run-experiment |
| `EXPERIMENT_TRACKER.md` | 执行记录：每个 run 的期望 vs 实际留痕 | experiment-bridge / run-experiment | 人 + 全部下游 |
| `PAPER_PLAN.md` | 叙事锚点：论文故事线（经 User Confirmation Loop） | research-paper-plan | research-paper-hermes |

---

## 使用方式

本仓库是一组 **agent skills**（每个 `skills/*/SKILL.md` 定义一个可触发技能，含工作流、常量与触发词），
可配合 Hermes / Claude Code / VS Code Copilot 等 agent 运行时使用：

- 将 `skills/` 目录接入你的 agent 的 skills 目录（如 `~/.agents/skills/` 或工作区 `.claude/skills/`）
- 通过触发词调用，例如：
  - `refine my approach: <问题描述>`
  - `run experiment`（自动选取下一个 PENDING run）
  - `check training <entity>/<project>/<run_id>`
- 部分 skill 依赖环境变量：
  - `PKBASE_PATH` — 知识库路径（wiki-pk-base）
  - `LLM_BASE_URL` / `LLM_API_KEY` / `LLM_MODEL` — 文献综述脚本的 OpenAI 兼容端点（缺省回退本地 Ollama）
  - `WANDB_ENTITY` / `WANDB_PROJECT` — 训练监控

## 目录结构

```
anchor-research/
└── skills/
    ├── research-refine/           # 方案层：方案打磨（核心，冻结 Problem Anchor）
    ├── research-retrofit/         # 方案层：代码↔方案对齐（重新锚定）
    ├── research-literature-review/
    ├── research-literature-summary/  # + summarize_review.py
    ├── wiki-pk-base/
    ├── experiment-plan/
    ├── experiment-bridge/
    ├── structured-codebase/          # + StructCodebase/ 训练框架骨架
    ├── run-experiment/
    ├── training-check/
    ├── research-paper-plan/          # + refer/ venue 清单与写作原则
    ├── research-paper-hermes/        # + references/ + templates/（ICLR/NeurIPS/ICML/ACL/AAAI/COLM）
    └── research-paper-poster/        # + templates/ + logos/
```

## License

MIT（各 skill 单独标注，作者：Zhihao Li；`research-paper-hermes` 基于 Orchestra Research 的工作改编）
