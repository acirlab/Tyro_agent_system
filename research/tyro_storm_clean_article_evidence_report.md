# 研究综述：Automated scientific literature review generation using large language model agents

## 摘要

围绕“Automated scientific literature review generation using large language model agents”，本报告从 12 篇候选论文中梳理研究脉络。现有材料主要覆盖 基础方法与模型、系统与工具、评估与 Benchmark。高优先级阅读对象包括 [P1]、[P2]、[P3]、[P4]、[P5]。整体来看，较好的科研调研系统通常不是单次生成，而是将问题界定、广域检索、主题组织、证据压缩、分节写作和引用核查拆成流水线。

## 调研范围与方法

本报告面向“Automated scientific literature review generation using large language model agents”进行自动化学术调研，流程对齐 STORM 的“预写作检索与大纲生成 -> 带引用长文写作”范式，以及 AutoSurvey 的“检索增强、分节写作、结构化评估”范式。当前运行共保留 12 篇去重候选论文，正文中的 `[P#]` 均可在文末参考文献中追溯。本轮构建了 36 个 evidence chunks；若论文提供可访问 PDF，则优先使用全文，否则降级为摘要或元数据。

## STORM-style 运行轨迹

- 多视角角色数：5。
- 学术检索查询数：10。
- evidence chunks：36，其中全文 chunks：32。
- 流程：direct outline -> perspective-guided scholarly retrieval -> evidence-refined outline -> section-level evidence packing -> section-by-section writing -> citation audit。

## STORM-style 多视角问题

- **Field historian**：该领域的基础问题和早期脉络是什么？ 检索式：`automated scientific literature review generation using large language model agents foundational survey taxonomy`
- **System builder**：已有系统如何组织检索、规划、写作和验证？ 检索式：`automated scientific literature review generation using large language model agents system framework pipeline`
- **Evaluation critic**：现有工作如何评估覆盖、引用质量和可靠性？ 检索式：`automated scientific literature review generation using large language model agents evaluation benchmark citation quality`
- **Application researcher**：这些方法如何进入真实科研工作流？ 检索式：`automated scientific literature review generation using large language model agents applications case study workflow`
- **Recent-work tracker**：最近一到两年的新趋势是什么？ 检索式：`automated scientific literature review generation using large language model agents recent advances 2025 2026`

## STORM-style 多视角问答日志

### Field historian

- 角色关注：该领域的基础问题和早期脉络是什么？
- 追问：这个方向的代表性早期工作、综述和问题定义是什么？
- 检索式：`automated scientific literature review generation using large language model agents foundational survey taxonomy`; `automated scientific literature review generation using large language model agents foundational seminal`; `automated scientific literature review generation using large language model agents foundational seminal survey review`
- 证据引用：[P1], [P5], [P2], [P4]
- 回答摘要：该视角的候选证据主要来自 [P1]、[P5]、[P2]、[P4]。优先入口是《Automated Literature Review Using NLP Techniques and LLM-Based Retrieval-Augmented Generation》，其元数据/摘要显示该视角与This research presents and compares multiple approaches to automate the generation of literature reviews using several Natural Language P...相关。 最相关证据块来自 [P1] 的 `full_text`，内容指向：[page 1] Automated Literature Review Using NLP Techniques and LLM-Based Retrieval-Augmented Generation Nurshat Fateh Ali Department of Computer Science and E...

### System builder

- 角色关注：已有系统如何组织检索、规划、写作和验证？
- 追问：这些系统分别如何组织检索、规划、工具调用、写作和引用验证？
- 检索式：`automated scientific literature review generation using large language model agents system framework pipeline`; `automated scientific literature review generation using large language model agents system framework architecture retrieval augmented generation`; `automated scientific literature review generation using large language model agents system framework architecture retrieval augmented generation tool use agent citation grounding verification`
- 证据引用：[P1], [P7], [P5], [P6]
- 回答摘要：该视角的候选证据主要来自 [P1]、[P7]、[P5]、[P6]。优先入口是《Automated Literature Review Using NLP Techniques and LLM-Based Retrieval-Augmented Generation》，其元数据/摘要显示该视角与This research presents and compares multiple approaches to automate the generation of literature reviews using several Natural Language P...相关。 最相关证据块来自 [P1] 的 `full_text`，内容指向：[page 1] Automated Literature Review Using NLP Techniques and LLM-Based Retrieval-Augmented Generation Nurshat Fateh Ali Department of Computer Science and E...

### Evaluation critic

- 角色关注：现有工作如何评估覆盖、引用质量和可靠性？
- 追问：现有工作怎样评估覆盖率、事实性、引用质量和人工偏好？
- 检索式：`automated scientific literature review generation using large language model agents evaluation benchmark citation quality`; `automated scientific literature review generation using large language model agents citation grounding verification evaluation benchmark metric coverage recall`; `automated scientific literature review generation using large language model agents citation grounding verification evaluation benchmark metric coverage recall human expert preference`
- 证据引用：[P1], [P2], [P5], [P4]
- 回答摘要：该视角的候选证据主要来自 [P1]、[P2]、[P5]、[P4]。优先入口是《Automated Literature Review Using NLP Techniques and LLM-Based Retrieval-Augmented Generation》，其元数据/摘要显示该视角与This research presents and compares multiple approaches to automate the generation of literature reviews using several Natural Language P...相关。 最相关证据块来自 [P1] 的 `full_text`，内容指向：[page 1] Automated Literature Review Using NLP Techniques and LLM-Based Retrieval-Augmented Generation Nurshat Fateh Ali Department of Computer Science and E...

### Application researcher

- 角色关注：这些方法如何进入真实科研工作流？
- 追问：这些方法在哪些科研工作流中落地，用户如何介入和校正？
- 检索式：`automated scientific literature review generation using large language model agents applications case study workflow`; `automated scientific literature review generation using large language model agents workflow human in the loop`; `automated scientific literature review generation using large language model agents workflow human in the loop application case study`
- 证据引用：[P1], [P2], [P4], [P5]
- 回答摘要：该视角的候选证据主要来自 [P1]、[P2]、[P4]、[P5]。优先入口是《Automated Literature Review Using NLP Techniques and LLM-Based Retrieval-Augmented Generation》，其元数据/摘要显示该视角与This research presents and compares multiple approaches to automate the generation of literature reviews using several Natural Language P...相关。 最相关证据块来自 [P1] 的 `full_text`，内容指向：[page 1] Automated Literature Review Using NLP Techniques and LLM-Based Retrieval-Augmented Generation Nurshat Fateh Ali Department of Computer Science and E...

### Recent-work tracker

- 角色关注：最近一到两年的新趋势是什么？
- 追问：2024 年以后有哪些新系统、benchmark 或评测协议值得单独成节？
- 检索式：`automated scientific literature review generation using large language model agents recent advances 2025 2026`; `automated scientific literature review generation using large language model agents 最近一到两年的新趋势是什么？`; `automated scientific literature review generation using large language model agents system framework architecture 2024 2025 2026 recent`
- 证据引用：[P1], [P2], [P4], [P5]
- 回答摘要：该视角的候选证据主要来自 [P1]、[P2]、[P4]、[P5]。优先入口是《Automated Literature Review Using NLP Techniques and LLM-Based Retrieval-Augmented Generation》，其元数据/摘要显示该视角与This research presents and compares multiple approaches to automate the generation of literature reviews using several Natural Language P...相关。 最相关证据块来自 [P1] 的 `full_text`，内容指向：[page 1] Automated Literature Review Using NLP Techniques and LLM-Based Retrieval-Augmented Generation Nurshat Fateh Ali Department of Computer Science and E...


## 关键结论

- 候选文献显示，该方向需要同时关注系统架构、检索 grounding、评估基准和应用约束，而不是只比较单个模型 [P1]、[P2]、[P3]。
- 综述写作应先产出可审阅的大纲和 evidence pack，再进入正文生成；这比一次性长文生成更容易控制覆盖面和引用质量。
- `基础方法与模型` 当前以 [P3] 为主要证据入口，其中 2 个全文证据块。
- `系统与工具` 当前以 [P2]、[P4]、[P7] 为主要证据入口，其中 6 个全文证据块。
- `评估与 Benchmark` 当前以 [P1]、[P5]、[P6] 为主要证据入口，其中 8 个全文证据块。

## 代表论文

| 编号 | 年份 | 标题 | 来源 | 引用数 | 链接 |
| --- | --- | --- | --- | --- | --- |
| [P1] | 2024 | Automated Literature Review Using NLP Techniques and LLM-Based Retrieval-Augmented Generation | arxiv |  | http://arxiv.org/abs/2411.18583v1 |
| [P2] | 2024 | Learning From Failure: Integrating Negative Examples when Fine-tuning Large Language Models as Agents | arxiv |  | http://arxiv.org/abs/2402.11651v2 |
| [P3] | 2024 | Understanding Survey Paper Taxonomy about Large Language Models via Graph Representation Learning | arxiv |  | http://arxiv.org/abs/2402.10409v1 |
| [P4] | 2023 | AI Literature Review Suite | arxiv |  | http://arxiv.org/abs/2308.02443v1 |
| [P5] | 2025 | LLM-Based Data Science Agents: A Survey of Capabilities, Challenges, and Future Directions | arxiv |  | http://arxiv.org/abs/2510.04023v1 |
| [P6] | 2023 | A Survey on Large Language Model based Autonomous Agents | arxiv |  | http://arxiv.org/abs/2308.11432v7 |
| [P7] | 2025 | Engineering the RAG Stack: A Comprehensive Review of the Architecture and Trust Frameworks for Retrieval-Augmented Generation Systems | arxiv |  | http://arxiv.org/abs/2601.05264v1 |
| [P8] | 2024 | A Comprehensive Survey of Scientific Large Language Models and Their Applications in Scientific Discovery | arxiv |  | http://arxiv.org/abs/2406.10833v3 |
| [P9] | 2026 | Externalization in LLM Agents: A Unified Review of Memory, Skills, Protocols and Harness Engineering | arxiv |  | http://arxiv.org/abs/2604.08224v1 |
| [P10] | 2025 | AR-RAG: Autoregressive Retrieval Augmentation for Image Generation | arxiv |  | http://arxiv.org/abs/2506.06962v3 |
| [P11] | 2026 | Learning the Value Systems of Agents with Preference-based and Inverse Reinforcement Learning | arxiv |  | http://arxiv.org/abs/2602.04518v1 |
| [P12] | 2026 | Emergence of Agentic AI: A Review on Evolution, Background, Working Principles, Applications, Adoption Factors, and Future Research Directions | arxiv |  | http://arxiv.org/abs/2608.18110v1 |

## 建议综述大纲

### Direct outline

- 引言：Automated scientific literature review generation using large language model agents 的研究问题、应用背景和综述范围
- 背景：关键概念、技术前提和相关研究传统
- 方法分类：按模型、检索、agent 编排和验证方式组织已有工作
- 代表系统：梳理可复现系统、开源工具和端到端 pipeline
- 评估与 SOTA：总结 benchmark、指标、数据集和可比性风险
- 应用与工作流：讨论真实科研场景中的使用方式
- 局限与未来方向：覆盖可信度、引用质量、全文证据和人工审核

### Evidence-refined outline

- 引言：Automated scientific literature review generation using large language model agents 的研究问题、应用背景和综述范围
- 背景与研究脉络：从基础论文和近期综述中界定问题 [P3]
- 系统架构与 agent workflow：比较检索、规划、工具调用、写作和验证模块 [P2]、[P4]、[P7]、[P11]
- 评估协议与 SOTA 追踪：整理数据集、指标、人工偏好评测和 leaderboard 风险 [P1]、[P5]、[P6]、[P8]
- 证据缺口：应用与案例 仍需追加定向检索和全文获取
- 局限与未来方向：围绕全文 grounding、claim-level citation audit 和可复现 SOTA 表格展开

## 主题脉络

从时间线上看，较早工作可作为问题定义和基础方法入口，例如 [P4]、[P6]、[P3]。
近年的论文更集中在系统化、自动化和评估问题上，例如 [P9]、[P12]、[P11]、[P10]、[P5]。
因此，组会展示时可以把该领域讲成三段：早期基础方法形成、LLM/agent 系统化带来工作流自动化、近期重点转向可验证引用和 benchmark 化评估。

## 方法与系统分类

| 类别 | 关注问题 | 代表论文 | 当前证据强度 |
| --- | --- | --- | --- |
| 基础方法与模型 | 核心模型、算法思想、任务定义和理论基础 | [P3] | 低 |
| 系统与工具 | agent 编排、检索工具、pipeline、交互式工作台 | [P2]、[P4]、[P7]、[P11] | 中 |
| 评估与 Benchmark | 数据集、指标、leaderboard、实验协议和可比性 | [P1]、[P5]、[P6]、[P8] | 中 |
| 应用与案例 | 具体学科、行业或用户工作流中的落地方式 | 待补充 | 低 |

## 正文综述

### 1. 问题定义与基础方法

围绕“Automated scientific literature review generation using large language model agents”，`基础方法与模型` 方向的候选论文说明该主题已经形成可归纳的子问题。代表性材料包括 [P3]。其中，Understanding Survey Paper Taxonomy about Large Language Models via Graph Representation Learning 提供了一个优先阅读入口；其摘要显示，该方向关注的是As new research on Large Language Models (LLMs) continues, it is difficult to keep up with new research and models. T...。本节最相关证据来自 [P3] 的 `full_text` chunk，其内容摘要为：ficulty of text classification. Attributes Descriptions Taxonomy Proposed taxonomy Title Paper title Authors Lists of author’s name Relea...

### 2. Agent 系统与调研流水线

围绕“Automated scientific literature review generation using large language model agents”，`系统与工具` 方向的候选论文说明该主题已经形成可归纳的子问题。代表性材料包括 [P2]、[P4]、[P7]、[P11]。其中，Learning From Failure: Integrating Negative Examples when Fine-tuning Large Language Models as Agents 提供了一个优先阅读入口；其摘要显示，该方向关注的是Large language models (LLMs) have achieved success in acting as agents, which interact with environments through tool...。本节最相关证据来自 [P2] 的 `full_text` chunk，其内容摘要为：[page 1] Learning From Failure: Integrating Negative Examples when Fine-tuning Large Language Models as Agents Renxi Wang1,2 Haonan Li1,2...
从多篇论文的题名和摘要看，这一类工作需要进一步区分“概念性综述”“系统实现”和“实验评估”三种证据。后续写正式综述时，应把 [P4]、[P7]、[P11] 的贡献点拆成独立 claim，并为每个 claim 绑定原文段落。

### 3. 评估体系与 SOTA 追踪

围绕“Automated scientific literature review generation using large language model agents”，`评估与 Benchmark` 方向的候选论文说明该主题已经形成可归纳的子问题。代表性材料包括 [P1]、[P5]、[P6]、[P8]。其中，Automated Literature Review Using NLP Techniques and LLM-Based Retrieval-Augmented Generation 提供了一个优先阅读入口；其摘要显示，该方向关注的是This research presents and compares multiple approaches to automate the generation of literature reviews using severa...。本节最相关证据来自 [P1] 的 `full_text` chunk，其内容摘要为：[page 1] Automated Literature Review Using NLP Techniques and LLM-Based Retrieval-Augmented Generation Nurshat Fateh Ali Department of Co...
从多篇论文的题名和摘要看，这一类工作需要进一步区分“概念性综述”“系统实现”和“实验评估”三种证据。后续写正式综述时，应把 [P5]、[P6]、[P8] 的贡献点拆成独立 claim，并为每个 claim 绑定原文段落。

### 4. 应用场景与工作流融合

当前检索结果中该方向证据不足，需要追加定向检索。

### 5. 综合讨论

与普通搜索报告相比，高质量科研综述的关键不是列出更多论文，而是把论文组织成可审查的论证结构：先说明研究问题，再按方法谱系和系统组件分层，最后回到 benchmark、局限和未来方向。当前实现已经把候选论文、分类、大纲、正文、evidence chunks 和参考文献对齐到同一组 `[P#]` 证据编号；下一步应加入更强的 LLM 分节写作和 claim-level 判断。

## 综合对比

| 维度 | 当前观察 | 支撑文献 | 后续需要补强 |
| --- | --- | --- | --- |
| 覆盖面 | 是否覆盖基础、高被引和近期工作 | [P3] | 引入 citation graph 和最近一年时间过滤 |
| 系统性 | 是否能归纳 agent/pipeline/tool 的结构 | [P2]、[P4]、[P7] | 抽取系统组件和数据流图 |
| 评估性 | 是否有 benchmark、dataset、metric 或 leaderboard | [P1]、[P5]、[P6] | 接入 SOTA 表格抽取和可比性判断 |
| 落地性 | 是否说明真实研究工作流中的使用方式 | 待补充 | 补充 case study 和用户交互流程 |

## 研究空白与未来方向

- **全文证据化**：本轮已构建 36 个 evidence chunks，其中全文 chunk 为 32 个；后续应继续提高 PDF 覆盖率。
- **多视角规划**：参考 STORM，需要加入 perspective-guided question asking，用不同专家视角主动发现遗漏主题。
- **分节写作与修订**：参考 AutoSurvey，需要按 section 独立召回和写作，再做跨章节一致性修订。
- **新近论文覆盖**：当前候选集中 2024 年以后论文有 10 篇，后续应为近期进展单独建立章节 [P1]、[P2]、[P3]、[P5]。
- **SOTA 表格化**：涉及 benchmark 时，应输出 task/dataset/metric/setting，而不是只在正文中描述“性能更好”。

## Section Evidence Pack

### 基础方法与模型
- [P3] `full_text` score=0.600: ficulty of text classification. Attributes Descriptions Taxonomy Proposed taxonomy Title Paper title Authors Lists of author’s name Release Date First released date Links Links of papers Paper ID The arXiv paper ID Ca...
- [P3] `full_text` score=0.400: [page 1] Understanding Survey Paper Taxonomy about Large Language Models via Graph Representation Learning Jun Zhuang Department of Computer Science Boise State University junzhuang@boisestate.edu Casey Kennington Dep...

### 系统与工具
- [P2] `full_text` score=0.600: [page 1] Learning From Failure: Integrating Negative Examples when Fine-tuning Large Language Models as Agents Renxi Wang1,2 Haonan Li1,2 Xudong Han1,2 Yixuan Zhang1,2 Timothy Baldwin1,2,3 1LibrAI 2MBZUAI 3The Univers...
- [P4] `full_text` score=0.600: [page 1] AI LITERATURE REVIEW SUITE David A. Tovar Department of Psychology Vanderbilt University Nashville, TN david.tovar@vanderbilt.edu ABSTRACT The process of conducting literature reviews is often time-consuming ...
- [P4] `full_text` score=0.600: eferences into a subfolder. This classification enhances the accessibility and readability of the extracted data, which simplifies subsequent literature analysis tasks. 2.4 PDF Chat The PDF Chat module is an interacti...
- [P7] `full_text` score=0.600: [page 1] Engineering the RAG Stack: A Comprehensive Review of the Architecture and Trust Frameworks for Retrieval Augmented Generation Systems Dean Wampler, Ph.D. Head of Technology, The AI Alliance IBM Research dean@...
- [P7] `full_text` score=0.600: l-Augmented Generation (RAG), Large Language Models, Information Retrieval, Neural Language Models, Knowledge- Augmented Generation, AI System Architectures, Trustworthy AI, Model Alignment, Multi-agent Systems. 1 Int...
- [P2] `full_text` score=0.400: digm that explicitly tells the model to differentiate between correct and incorrect inter- actions by adding prefixes or suffixes. Our exper- iments demonstrate that NAT outperforms tradi- tional methods by solely usi...

### 评估与 Benchmark
- [P1] `full_text` score=0.800: [page 1] Automated Literature Review Using NLP Techniques and LLM-Based Retrieval-Augmented Generation Nurshat Fateh Ali Department of Computer Science and Engineering Military Institute of Science and Technology Dhak...
- [P1] `full_text` score=0.800: SciTLDR dataset is chosen for this research experiment and three distinct techniques are utilized to implement three different systems for auto-generating the literature reviews. The ROUGE scores are used for the eval...
- [P8] `full_text` score=0.800: ges 1212–1224. [page 14] Zhibin Gou, Zhihong Shao, Yeyun Gong, Yelong Shen, Yujiu Yang, Minlie Huang, Nan Duan, and Weizhu Chen. 2024. Tora: A tool-integrated reasoning agent for mathematical problem solving. In ICLR’...
- [P5] `full_text` score=0.700: efficient, scalable, and accessible approaches to executing this end-to-end process become increasingly critical. To address this need, research has focused on automating data science workflows using AI-driven tools. ...
- [P5] `full_text` score=0.600: ema drift, and validation checks that flag questionable inferences. Without reliable domain grounding at this stage, downstream modeling and decision-making remain fundamentally constrained. 5.2.2 Data Visualization. ...
- [P6] `full_text` score=0.600: divide these actions into two classes: (1) external tools and (2) inter- nal knowledge of the LLMs. In the following, we introduce these actions more in detail. • External Tools. While LLMs have been demonstrated to b...

### 应用与案例
- 暂无候选证据，后续需要追加检索。

## Citation Audit

| 引用 | 标题 | URL | 证据块 | 状态 |
| --- | --- | --- | --- | --- |
| [P1] | Automated Literature Review Using NLP Techniques and LLM-Based Retrieval-Augmented Generation | yes | 4 | full_text_grounded |
| [P2] | Learning From Failure: Integrating Negative Examples when Fine-tuning Large Language Models as Agents | yes | 4 | full_text_grounded |
| [P3] | Understanding Survey Paper Taxonomy about Large Language Models via Graph Representation Learning | yes | 4 | full_text_grounded |
| [P4] | AI Literature Review Suite | yes | 4 | full_text_grounded |
| [P5] | LLM-Based Data Science Agents: A Survey of Capabilities, Challenges, and Future Directions | yes | 4 | full_text_grounded |
| [P6] | A Survey on Large Language Model based Autonomous Agents | yes | 4 | full_text_grounded |
| [P7] | Engineering the RAG Stack: A Comprehensive Review of the Architecture and Trust Frameworks for Retrieval-Augmented Generation Systems | yes | 4 | full_text_grounded |
| [P8] | A Comprehensive Survey of Scientific Large Language Models and Their Applications in Scientific Discovery | yes | 4 | full_text_grounded |
| [P9] | Externalization in LLM Agents: A Unified Review of Memory, Skills, Protocols and Harness Engineering | yes | 1 | abstract_grounded |
| [P10] | AR-RAG: Autoregressive Retrieval Augmentation for Image Generation | yes | 1 | abstract_grounded |
| [P11] | Learning the Value Systems of Agents with Preference-based and Inverse Reinforcement Learning | yes | 1 | abstract_grounded |
| [P12] | Emergence of Agentic AI: A Review on Evolution, Background, Working Principles, Applications, Adoption Factors, and Future Research Directions | yes | 1 | abstract_grounded |

## OpenScholar-style 证据覆盖

- 证据块总数：36。
- 全文证据块：32；摘要证据块：4。
- Top evidence chunks：
  - [P1] `full_text` score=0.800: [page 1] Automated Literature Review Using NLP Techniques and LLM-Based Retrieval-Augmented Generation Nurshat Fateh Ali Department of Computer Science and Engineering Military ...
  - [P1] `full_text` score=0.800: SciTLDR dataset is chosen for this research experiment and three distinct techniques are utilized to implement three different systems for auto-generating the literature reviews...
  - [P1] `full_text` score=0.800: ancing the effectiveness and applicability of the developed system tool. More functionality can be added to the Graphical User Interface such as model options, output size, etc....
  - [P8] `full_text` score=0.800: ges 1212–1224. [page 14] Zhibin Gou, Zhihong Shao, Yeyun Gong, Yelong Shen, Yujiu Yang, Minlie Huang, Nan Duan, and Weizhu Chen. 2024. Tora: A tool-integrated reasoning agent fo...
  - [P1] `full_text` score=0.700: text, extract relevant details, and create structured summaries [2]. The primary objective of this research is to develop a system that can automatically generate the literature...
  - [P5] `full_text` score=0.700: efficient, scalable, and accessible approaches to executing this end-to-end process become increasingly critical. To address this need, research has focused on automating data s...
  - [P2] `full_text` score=0.600: [page 1] Learning From Failure: Integrating Negative Examples when Fine-tuning Large Language Models as Agents Renxi Wang1,2 Haonan Li1,2 Xudong Han1,2 Yixuan Zhang1,2 Timothy B...
  - [P3] `full_text` score=0.600: ficulty of text classification. Attributes Descriptions Taxonomy Proposed taxonomy Title Paper title Authors Lists of author’s name Release Date First released date Links Links ...
## 质量检查清单

- 覆盖性：当前综述依赖自动召回的 12 篇候选论文，仍需人工检查是否遗漏公认 seminal work。
- 新近性：建议追加最近 6-12 个月限定检索，单独审阅 arXiv/OpenReview/顶会 accepted paper。
- 引用可靠性：当前 `[P#]` 已连接到 evidence chunks；若 source_type 为 full_text，则比摘要级证据更可靠。
- 结构一致性：大纲、正文和 evidence pack 已对齐；taxonomy 仍需要后续 LLM/embedding 聚类继续增强。
- SOTA 可比性：如果综述涉及 benchmark，需要额外验证 dataset split、metric direction、训练数据和推理预算。

## 参考文献

- [P1] Nurshat Fateh Ali, Md. Mahdi Mohtasim, Shakil Mosharrof et al.. Automated Literature Review Using NLP Techniques and LLM-Based Retrieval-Augmented Generation. arXiv, 2024. http://arxiv.org/abs/2411.18583v1
- [P2] Renxi Wang, Haonan Li, Xudong Han et al.. Learning From Failure: Integrating Negative Examples when Fine-tuning Large Language Models as Agents. arXiv, 2024. http://arxiv.org/abs/2402.11651v2
- [P3] Jun Zhuang, Casey Kennington. Understanding Survey Paper Taxonomy about Large Language Models via Graph Representation Learning. arXiv, 2024. http://arxiv.org/abs/2402.10409v1
- [P4] David A. Tovar. AI Literature Review Suite. arXiv, 2023. http://arxiv.org/abs/2308.02443v1
- [P5] Mizanur Rahman, Amran Bhuiyan, Mohammed Saidul Islam et al.. LLM-Based Data Science Agents: A Survey of Capabilities, Challenges, and Future Directions. arXiv, 2025. http://arxiv.org/abs/2510.04023v1
- [P6] Lei Wang, Chen Ma, Xueyang Feng et al.. A Survey on Large Language Model based Autonomous Agents. arXiv, 2023. http://arxiv.org/abs/2308.11432v7
- [P7] Dean Wampler, Dave Nielson, Alireza Seddighi. Engineering the RAG Stack: A Comprehensive Review of the Architecture and Trust Frameworks for Retrieval-Augmented Generation Systems. arXiv, 2025. http://arxiv.org/abs/2601.05264v1
- [P8] Yu Zhang, Xiusi Chen, Bowen Jin et al.. A Comprehensive Survey of Scientific Large Language Models and Their Applications in Scientific Discovery. arXiv, 2024. http://arxiv.org/abs/2406.10833v3
- [P9] Chenyu Zhou, Huacan Chai, Wenteng Chen et al.. Externalization in LLM Agents: A Unified Review of Memory, Skills, Protocols and Harness Engineering. arXiv, 2026. http://arxiv.org/abs/2604.08224v1
- [P10] Jingyuan Qi, Zhiyang Xu, Qifan Wang et al.. AR-RAG: Autoregressive Retrieval Augmentation for Image Generation. arXiv, 2025. http://arxiv.org/abs/2506.06962v3
- [P11] Andrés Holgado-Sánchez, Holger Billhardt, Alberto Fernández et al.. Learning the Value Systems of Agents with Preference-based and Inverse Reinforcement Learning. arXiv, 2026. http://arxiv.org/abs/2602.04518v1
- [P12] AKM Bahalul Haque, Al Amin Islam Ridoy, Mohammad Rayhan et al.. Emergence of Agentic AI: A Review on Evolution, Background, Working Principles, Applications, Adoption Factors, and Future Research Directions. arXiv, 2026. http://arxiv.org/abs/2608.18110v1
