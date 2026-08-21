/* ============================================================
   PKBase static site — data.js
   ----------------------------------------------------------
   THIS FILE IS GENERATED. Do not hand-edit after init:
   the wiki-pk-base skill regenerates it (rebuild) whenever
   init / add / ingest / lint changes the vault.

   Schema (all paths relative to the PKBase root, no .md kept
   is fine either way — the reader strips it):

   双语约定（bilingual vault）：
   - 每个条目可携带 <field>_zh / <field>_en 字段（翻译来自同目录的
     翻译文件 <slug>.en.md 等，见 SKILL.md），前端按当前 UI 语言
     优先取对应译文，缺译文时回退显示原文。
   - meta 支持 name_en / description_en；
     Page 支持 title_en / description_en / body_en；
     raw 条目支持 title_en / description_en；
     log 条目支持 title_en / detail_en。
   - 未提供 _en 字段的条目在 EN 界面下原样显示原文。

   window.PKBASE_DATA = {
     meta: {
       name: string,          // PKBase 名称（SCHEMA.md → name）
       description: string,   // 一句话描述
       name_en?: string,      // 英文名称（可选）
       description_en?: string, // 英文描述（可选）
       updated: string        // 最近一次重建时间，如 "2025-07-01 18:30"
     },
     counts: {                // 与下方数组长度一致
       sources: number, concepts: number,
       comparisons: number, queries: number,
       raw: number, log: number
     },
     pages: {
       sources:     [ Page ],  // wiki/sources/<domain>/<topic>/<slug>.md
       concepts:    [ Page ],  // wiki/concepts/<domain>/<topic>/<slug>.md
       comparisons: [ Page ],  // wiki/comparisons/<domain>/<topic>/<slug>.md
       queries:     [ Page ]   // wiki/queries/<domain>/<topic>/<slug>.md
     },
     raw: [                   // raw/ 清单（仅文件，含二进制素材）
       {
         file: string,        // 相对 raw/ 的路径，如 "papers/<domain>/<topic>/20250701-lee-hifi-umi.pdf"
         materialType: string,// papers | articles | transcripts | assets | misc
         domain: string, topic: string,
         title: string,       // 显示名（文件名或来源标题）
         description: string  // 一句话说明
       }
     ],
     log: [                   // log.md（+ log-*.md）最近条目，新的在前
       { date: string, time?: string, action: string, title?: string, detail?: string }
     }
   }

   Page = {
     file: string,        // 相对 wiki/<type>/ 的路径，如 "<domain>/<topic>/<slug>.md"
     title: string,       // frontmatter title
     description: string, // frontmatter description（可选）
     title_en?: string,       // 翻译文件 <slug>.en.md 的 title（可选）
     description_en?: string, // 翻译文件的 description（可选）
     body_en?: string,        // 翻译文件的正文（可选），同样保留 $..$ 与 [[wikilink]]
     domain: string,      // 路径第一级
     topic: string,       // 路径第二级
     tags: string[],      // frontmatter tags
     updated: string,     // frontmatter updated / last_reviewed（可选）
     source?: string,     // frontmatter source（source 页的来源文件，相对 PKBase 根）
     body: string         // 正文 markdown（不含 frontmatter），保留 $..$ 公式与 [[wikilink]]
   }

   约定：
   - body 里的 [[wikilink]] 路径用完整 wiki 相对路径：
     [[sources/<domain>/<topic>/<slug>]] 或带 |别名
   - body 里的 $...$ / $$...$$ 公式原样保留（前端只渲染样式，不做 LaTeX 计算）
   ============================================================ */
window.PKBASE_DATA = {
  meta: {
    name: "PKBase · 动作生成研究",
    description: "多模态交互动作生成（Interactive Motion）论文知识库",
    name_en: "PKBase · Motion Generation Research",
    description_en: "A literature knowledge base for multimodal interactive motion generation",
    updated: "2025-07-01 18:30"
  },
  counts: { sources: 2, concepts: 2, comparisons: 1, queries: 1, raw: 3, log: 3 },
  pages: {
    sources: [
      {
        file: "multimodal-learning/interactive-motion/hifi-umi.md",
        title: "HiFi-UMI: 高保真上肢运动生成",
        description: "基于流匹配的上肢运动生成模型，支持文本+参考条件控制。",
        title_en: "HiFi-UMI: High-Fidelity Upper-Body Motion Generation",
        description_en: "A flow-matching upper-body motion generation model with text + reference conditioning.",
        domain: "multimodal-learning",
        topic: "interactive-motion",
        tags: ["motion-generation", "flow-matching", "upper-body", "2025"],
        updated: "2025-07-01",
        source: "raw/papers/multimodal-learning/interactive-motion/20250701-lee-hifi-umi.pdf",
        body: "## 概要\n\nHiFi-UMI 提出了一种**流匹配**（flow matching）框架用于高保真上肢动作生成，核心贡献：\n\n1. 在 SMPL-X 参数空间中直接建模，避免关节空间插值的非刚性问题\n2. 支持文本 prompt 与参考动作片段的双重条件\n3. 引入时序一致性正则项 $\\mathcal{L}_{tc}$ 抑制帧间抖动\n\n> 关键假设：上肢动作的分布可以表示为从噪声到数据的常微分流（ODE flow）。\n\n## 方法\n\n给定条件 $c$（文本嵌入 + 参考动作），模型学习速度场 $v_\\theta(x_t, t, c)$ 求解\n\n$$x_{1:T} = [m_{\\text{root},1:T};\\, x_{\\text{body},1:T}] \\in \\mathbb{R}^{T \\times D}$$\n\n| 组件 | 配置 |\n| --- | --- |\n| 骨干 | DiT-XL/2 |\n| 条件注入 | AdaLN-Zero |\n| 训练步数 | 200k |\n\n## Sources\n\n详见来源文件 [[concepts/multimodal-learning/interactive-motion/flow-matching|流匹配]] 的综述。",
        body_en: "## Summary\n\nHiFi-UMI proposes a **flow matching** framework for high-fidelity upper-body motion generation. Key contributions:\n\n1. Models directly in SMPL-X parameter space, avoiding non-rigidity issues of joint-space interpolation\n2. Dual conditioning on text prompts and reference motion clips\n3. A temporal-consistency regularizer $\\mathcal{L}_{tc}$ that suppresses inter-frame jitter\n\n> Key hypothesis: the distribution of upper-body motion can be expressed as an ODE flow from noise to data.\n\n## Method\n\nGiven condition $c$ (text embedding + reference motion), the model learns a velocity field $v_\\theta(x_t, t, c)$ solving\n\n$$x_{1:T} = [m_{\\text{root},1:T};\\, x_{\\text{body},1:T}] \\in \\mathbb{R}^{T \\times D}$$\n\n| Component | Config |\n| --- | --- |\n| Backbone | DiT-XL/2 |\n| Condition injection | AdaLN-Zero |\n| Training steps | 200k |\n\n## Sources\n\nSee the source file and the [[concepts/multimodal-learning/interactive-motion/flow-matching|Flow Matching]] overview."
      },
      {
        file: "multimodal-learning/interactive-motion/mdm.md",
        title: "MDM: 基于扩散模型的动作生成",
        description: "Motion Diffusion Model，将 DDPM 应用于 3D 人体动作生成与补全。",
        domain: "multimodal-learning",
        topic: "interactive-motion",
        tags: ["motion-generation", "diffusion", "inpainting"],
        updated: "2025-06-20",
        source: "raw/papers/multimodal-learning/interactive-motion/20250620-teveter-mdm.pdf",
        body: "## 概要\n\nMDM 将去噪扩散概率模型迁移到 3D 人体动作序列，支持：\n\n- 无条件生成\n- 文本条件生成（CLIP 嵌入）\n- 动作补全（inpainting）：固定已知关节/帧，采样缺失部分\n\n## 与流匹配的关系\n\n扩散与 [[sources/multimodal-learning/interactive-motion/hifi-umi|HiFi-UMI]] 所用流匹配同属生成式序列建模；MDM 使用 DDPM 采样（步数多），流匹配使用 ODE（步数少、更稳定）。详见对比页 [[comparisons/multimodal-learning/interactive-motion/diffusion-vs-flow-matching]]。"
      }
    ],
    concepts: [
      {
        file: "multimodal-learning/interactive-motion/flow-matching.md",
        title: "流匹配 (Flow Matching)",
        description: "通过回归一个条件向量场学习连续归一化流，采样时解 ODE。",
        title_en: "Flow Matching",
        description_en: "Learns a continuous normalizing flow by regressing a conditional vector field; sampling solves an ODE.",
        domain: "multimodal-learning",
        topic: "interactive-motion",
        tags: ["generative-models", "flow-matching", "ode"],
        updated: "2025-07-01",
        body: "## 定义\n\n流匹配学习速度场 $v_\\theta(x_t, t)$，使得积分曲线 $x_0 \\to x_1$ 从噪声分布映射到数据分布。\n\n**条件流匹配 (CFM)** 用条件向量场 $u_t(x_t | x_1)$ 作为监督目标，避免对边缘分布的估计。\n\n## 与扩散模型对比\n\n| 维度 | 扩散 (DDPM) | 流匹配 |\n| --- | --- | --- |\n| 采样 | SDE/反向迭代，步数多 | ODE 积分，步数少 |\n| 目标 | 预测噪声 $\\epsilon$ | 预测速度场 $v$ |\n| 训练稳定性 | 较稳 | 更稳（线性插值路径） |\n\n## 相关\n\n- 应用示例：[[sources/multimodal-learning/interactive-motion/hifi-umi]]\n- 对比：[[comparisons/multimodal-learning/interactive-motion/diffusion-vs-flow-matching]]",
        body_en: "## Definition\n\nFlow matching learns a velocity field $v_\\theta(x_t, t)$ such that the integral curve $x_0 \\to x_1$ maps the noise distribution onto the data distribution.\n\n**Conditional flow matching (CFM)** uses the conditional vector field $u_t(x_t | x_1)$ as the regression target, avoiding estimation of the marginal distribution.\n\n## Comparison with diffusion\n\n| Dimension | Diffusion (DDPM) | Flow matching |\n| --- | --- | --- |\n| Sampling | SDE / reverse iteration, many steps | ODE integration, few steps |\n| Target | Predict noise $\\epsilon$ | Predict velocity field $v$ |\n| Training stability | Stable | More stable (linear interpolation path) |\n\n## Related\n\n- Application: [[sources/multimodal-learning/interactive-motion/hifi-umi]]\n- Comparison: [[comparisons/multimodal-learning/interactive-motion/diffusion-vs-flow-matching]]"
      },
      {
        file: "multimodal-learning/interactive-motion/smpl-x.md",
        title: "SMPL-X 人体模型",
        description: "统一的人体参数化模型：身体 + 表情 + 手部 + 眼睛。",
        domain: "multimodal-learning",
        topic: "interactive-motion",
        tags: ["body-model", "smpl", "parameters"],
        updated: "2025-06-18",
        body: "## 参数空间\n\nSMPL-X 由以下参数驱动：\n\n1. 形状参数 $\\beta \\in \\mathbb{R}^{10}$（PCA 体型）\n2. 姿态参数 $\\theta \\in \\mathbb{R}^{159}$（关节旋转，轴角表示）\n3. 表情参数（FLAME 部分）\n\n## 为什么动作生成在参数空间建模\n\n相比关节坐标，参数空间对非刚性形变更自然，且与渲染管线直接对接。"
      }
    ],
    comparisons: [
      {
        file: "multimodal-learning/interactive-motion/diffusion-vs-flow-matching.md",
        title: "对比：扩散 vs 流匹配（动作生成）",
        description: "两种序列生成框架在动作生成任务上的取舍。",
        domain: "multimodal-learning",
        topic: "interactive-motion",
        tags: ["comparison", "generative-models"],
        updated: "2025-07-01",
        body: "## 结论速览\n\n| 维度 | 扩散 (MDM) | 流匹配 (HiFi-UMI) |\n| --- | --- | --- |\n| 采样步数 | 100+ | 10–20 |\n| 推理速度 | 慢 | 快 |\n| 多样性 | 高 | 略低 |\n| 工程成熟度 | 高 | 上升中 |\n\n## 何时选哪个\n\n- **实时/交互场景** → 流匹配（采样快）\n- **离线高多样性数据集构建** → 扩散\n\n## 来源\n\n- [[sources/multimodal-learning/interactive-motion/mdm]]\n- [[sources/multimodal-learning/interactive-motion/hifi-umi]]"
      }
    ],
    queries: [
      {
        file: "multimodal-learning/interactive-motion/interactive-motion-survey-2025.md",
        title: "查询：2025 交互式动作生成方向综述",
        description: "回答「交互式动作生成目前的 SOTA 是什么」的查询记录。",
        domain: "multimodal-learning",
        topic: "interactive-motion",
        tags: ["query", "survey"],
        updated: "2025-07-01",
        body: "## 问题\n\n交互式动作生成（interactive motion generation）目前 SOTA 是什么？\n\n## 回答\n\n截至本库收录范围：\n\n1. 离线生成：[[sources/multimodal-learning/interactive-motion/hifi-umi|HiFi-UMI]] 在 FID/多样性上领先\n2. 条件控制：MDM 的 inpainting 仍是最通用的接口\n3. 生成框架选型参考 [[comparisons/multimodal-learning/interactive-motion/diffusion-vs-flow-matching]]\n\n## 未解决\n\n- 实时闭环交互（<50ms 响应）尚无公开 SOTA"
      }
    ]
  },
  raw: [
    {
      file: "papers/multimodal-learning/interactive-motion/20250701-lee-hifi-umi.pdf",
      materialType: "papers",
      domain: "multimodal-learning",
      topic: "interactive-motion",
      title: "HiFi-UMI (PDF 原文)",
      description: "Lee et al., 2025"
    },
    {
      file: "papers/multimodal-learning/interactive-motion/20250620-teveter-mdm.pdf",
      materialType: "papers",
      domain: "multimodal-learning",
      topic: "interactive-motion",
      title: "MDM (PDF 原文)",
      description: "Tevet et al., 2023"
    },
    {
      file: "assets/multimodal-learning/interactive-motion/smplx-diagram.png",
      materialType: "assets",
      domain: "multimodal-learning",
      topic: "interactive-motion",
      title: "SMPL-X 结构图",
      description: "用于 SMPL-X 概念页的插图",
      title_en: "SMPL-X structure diagram"
    }
  ],
  log: [
    { date: "2025-07-01", time: "18:30", action: "ingest", title: "HiFi-UMI", detail: "raw/papers/multimodal-learning/interactive-motion/20250701-lee-hifi-umi.pdf → wiki/sources/.../hifi-umi.md；新建概念页 flow-matching；更新对比页 diffusion-vs-flow-matching", title_en: "HiFi-UMI", detail_en: "raw/papers/.../20250701-lee-hifi-umi.pdf -> wiki/sources/.../hifi-umi.md; created concept page flow-matching; updated comparison page diffusion-vs-flow-matching" },
    { date: "2025-07-01", time: "17:42", action: "add", title: "MDM 论文 PDF", detail: "raw/papers/multimodal-learning/interactive-motion/20250620-teveter-mdm.pdf" },
    { date: "2025-06-30", time: "09:15", action: "query", title: "交互式动作生成 SOTA", detail: "生成 wiki/queries/.../interactive-motion-survey-2025.md" }
  ]
};
