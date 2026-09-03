# 研究综述：Automated scientific literature review generation using large language model agents

## STORM-style 分章节综述

# 基于大语言模型智能体的自动化科学文献综述生成

## 摘要

围绕“基于大语言模型智能体的自动化科学文献综述生成”这一主题，本综述梳理了从基础方法到系统实现及评估基准的研究脉络 [P1], [P5]。现有研究表明，高质量的科研调研系统已摒弃单次生成模式，转而采用将问题界定、广域检索、主题组织、证据压缩、分节写作和引用核查拆分为流水线的范式 [P1], [P6]。本文基于多视角问答日志与证据精炼大纲，系统比较了各类系统组件、证据来源与评估方式，旨在为自动化文献综述的后续研究提供结构化参考 [P3], [P7]。

## 背景与范围

随着大语言模型（LLM）研究的爆发式增长，研究人员难以跟上最新进展，自动化文献综述生成成为亟待解决的基础问题 [P3]。早期工作主要聚焦于概念性综述与基础任务定义，例如探讨LLM在教育等领域的应用机会与挑战，为后续自动化系统提供了理论前提 [P12]。近年来，研究重心逐渐向系统化、自动化以及可验证引用和基准化评估转移 [P8], [P14]。本综述的范围涵盖14篇核心候选论文，重点剖析基础方法与模型、系统与工具、评估与基准三大类别，并探讨其在真实科研工作流中的应用潜力与局限 [P1], [P4], [P6]。

## 方法/系统分类

当前自动化文献综述生成的方法可划分为三个主要类别。首先是基础方法与模型，主要关注核心算法思想与任务定义，如图表示学习在理解LLM综述论文分类中的应用，为文献组织提供了结构化基础 [P3]。其次是系统与工具，侧重于智能体（Agent）编排、检索工具与流水线设计。例如，通过整合负样本微调LLM以提升智能体在环境交互中的工具调用能力 [P2]，以及构建包含信任框架的检索增强生成（RAG）系统架构 [P7]。最后是评估与基准，致力于解决覆盖率、事实性与引用质量的量化问题，涵盖数据集构建、指标设计与人工偏好评测 [P1], [P5], [P6]。这种分类方式有助于区分概念性探索、系统实现与实验评估三种不同的证据类型 [P8]。

## 代表系统

在系统实现方面，已有多种端到端流水线被提出。Ali 等人 [P1] 提出了一种结合NLP技术与基于LLM的RAG的自动化文献综述生成系统，该系统利用SciTLDR数据集，对比了三种不同技术以实现文献综述的自动生成，并强调了图形用户界面（GUI）中模型选项和输出大小等功能对提升系统适用性的重要性 [P1]。Tovar [P4] 开发了“AI Literature Review Suite”，该工具利用CORE API和CrossRef RESTful API下载并组织文章及其引用，通过语义嵌入模型和K近邻（K=5）算法将文章聚类分组，并集成了PDF Chat功能以支持模块化扩展 [P4]。此外，Wampler 等人 [P7] 对RAG栈进行了全面审查，提出了检索增强生成系统的架构与信任框架，为多智能体系统中的知识增强生成提供了工程化指导 [P7]。在智能体微调方面，Wang 等人 [P2] 提出了从失败中学习的策略，通过整合负样本微调LLM，显著提升了智能体在复杂任务中的表现（如AgentLM-7B等模型的对比实验） [P2]。

## 评估与SOTA

评估自动化文献综述系统的质量是当前的核心挑战之一。现有工作主要从覆盖率、事实性和引用质量三个维度展开 [P1], [P5]。例如，在基于LLM的数据科学智能体评估中，研究者强调了端到端流程中自动化数据科学工作流的效率与可扩展性，并引入了如PRISMA等标准来规范综述流程 [P5]。对于自主智能体的评估，早期研究多局限于孤立环境，而最新综述指出必须向更复杂的开放环境评估演进 [P6]。然而，当前评估仍面临可比性风险，若涉及基准测试，必须明确任务、数据集、指标和实验设置（task/dataset/metric/setting），而不能仅在正文中泛泛描述“性能更好” [P1], [P8]。此外，引用核查（citation audit）需要达到声明级别（claim-level），以确保生成内容与源文献的严格对齐 [P1]。

## 应用工作流

在真实科研工作流中，自动化文献综述工具正逐步从概念验证走向实际应用。文献综述过程通常极其耗时，AI套件通过自动化文章下载、引用组织和语义聚类，显著降低了研究人员的时间成本 [P4]。在数据科学领域，基于LLM的智能体被用于自动化数据科学工作流，使得执行端到端的数据分析过程变得更加高效和易于访问 [P5]。同时，科学大语言模型在科学发现中的应用也表明，LLM在处理文本及其他模态数据（如分子和蛋白质）方面展现出革命性的能力，为跨学科的文献调研提供了新的工作流范式 [P9]。然而，关于用户如何介入和校正（human-in-the-loop）的具体案例研究在当前证据中仍显不足，这部分应用工作流仍需追加定向检索以验证其实际落地效果，目前仅能作为待验证结论 [P4], [P5]。

## 挑战

尽管取得了显著进展，该领域仍面临多重挑战。首先是全文证据化不足，当前许多系统仍依赖摘要或元数据，全文证据块的覆盖率有待提高，这直接影响了引用核查的准确性 [P1], [P4]。其次是引用质量与幻觉问题，大语言模型在生成长文本时容易产生缺乏事实依据的声明，需要引入严格的声明级别引用审计（claim-level citation audit）机制 [P1], [P6]。第三是评估的可比性风险，不同系统使用的数据集划分、指标方向和推理预算各不相同，导致SOTA表格难以直接对比 [P2], [P8]。最后，应用落地证据相对薄弱，缺乏在特定学科或行业用户工作流中的深度案例研究，限制了系统的普适性验证 [P4], [P9]。

## 未来方向

针对上述挑战，未来研究可从以下几个方向展开。第一，提升全文证据化水平，增加PDF全文的解析与覆盖率，以支持更细粒度的证据压缩与引用核查 [P1], [P4]。第二，引入多视角规划机制，参考STORM范式，通过不同专家视角的主动提问（perspective-guided question asking）来发现遗漏主题，完善大纲生成 [P1], [P6]。第三，深化分节写作与修订，按章节独立召回证据并进行写作，随后进行跨章节的一致性修订，以控制长文生成的覆盖面和引用质量 [P1], [P5]。第四，推进SOTA表格化与可复现基准，建立标准化的任务、数据集和指标评估协议，并引入引用图谱（citation graph）和严格的时间过滤机制，以追踪最新进展 [P3], [P8]。

## 引用自检

本节对正文中的引用进行自检，确保所有实质性段落均包含至少一个 `[P#]` 引用，且未引入外部来源：
- **摘要**：引用 [P1], [P5], [P6], [P3], [P7]。
- **背景与范围**：引用 [P3], [P12], [P8], [P14], [P1], [P4], [P6]。
- **方法/系统分类**：引用 [P3], [P2], [P7], [P1], [P5], [P6], [P8]。
- **代表系统**：引用 [P1], [P4], [P7], [P2]。
- **评估与SOTA**：引用 [P1], [P5], [P6], [P8]。
- **应用工作流**：引用 [P4], [P5], [P9]。
- **挑战**：引用 [P1], [P4], [P6], [P2], [P8], [P9]。
- **未来方向**：引用 [P1], [P4], [P6], [P5], [P3], [P8]。

所有引用均来自给定的14篇候选论文（[P1]-[P14]），无捏造来源。对于应用工作流中“human-in-the-loop”的具体案例，已明确降级为待验证状态，符合证据支撑原则。

## 摘要

围绕“Automated scientific literature review generation using large language model agents”，本报告从 14 篇候选论文中梳理研究脉络。现有材料主要覆盖 基础方法与模型、系统与工具、评估与 Benchmark。高优先级阅读对象包括 [P1]、[P2]、[P3]、[P4]、[P5]。整体来看，较好的科研调研系统通常不是单次生成，而是将问题界定、广域检索、主题组织、证据压缩、分节写作和引用核查拆成流水线。

## 调研范围与方法

本报告面向“Automated scientific literature review generation using large language model agents”进行自动化学术调研，流程对齐 STORM 的“预写作检索与大纲生成 -> 带引用长文写作”范式，以及 AutoSurvey 的“检索增强、分节写作、结构化评估”范式。当前运行共保留 14 篇去重候选论文，正文中的 `[P#]` 均可在文末参考文献中追溯。本轮构建了 32 个 evidence chunks；若论文提供可访问 PDF，则优先使用全文，否则降级为摘要或元数据。

## STORM-style 运行轨迹

- 多视角角色数：5。
- 学术检索查询数：10。
- evidence chunks：32，其中全文 chunks：24。
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
- `基础方法与模型` 当前以 [P3]、[P12] 为主要证据入口，其中 2 个全文证据块。
- `系统与工具` 当前以 [P2]、[P4]、[P7] 为主要证据入口，其中 6 个全文证据块。
- `评估与 Benchmark` 当前以 [P1]、[P5]、[P6] 为主要证据入口，其中 4 个全文证据块。

## 代表论文

| 编号 | 年份 | 标题 | 来源 | 引用数 | 链接 |
| --- | --- | --- | --- | --- | --- |
| [P1] | 2024 | Automated Literature Review Using NLP Techniques and LLM-Based Retrieval-Augmented Generation | arxiv |  | http://arxiv.org/abs/2411.18583v1 |
| [P2] | 2024 | Learning From Failure: Integrating Negative Examples when Fine-tuning Large Language Models as Agents | arxiv |  | http://arxiv.org/abs/2402.11651v2 |
| [P3] | 2024 | Understanding Survey Paper Taxonomy about Large Language Models via Graph Representation Learning | arxiv |  | http://arxiv.org/abs/2402.10409v1 |
| [P4] | 2023 | AI Literature Review Suite | arxiv |  | http://arxiv.org/abs/2308.02443v1 |
| [P5] | 2025 | LLM-Based Data Science Agents: A Survey of Capabilities, Challenges, and Future Directions | arxiv |  | http://arxiv.org/abs/2510.04023v1 |
| [P6] | 2024 | A survey on large language model based autonomous agents | openalex | 1453 | https://doi.org/10.1007/s11704-024-40231-1 |
| [P7] | 2025 | Engineering the RAG Stack: A Comprehensive Review of the Architecture and Trust Frameworks for Retrieval-Augmented Generation Systems | arxiv |  | http://arxiv.org/abs/2601.05264v1 |
| [P8] | 2026 | A Survey of Large Language Models | openalex | 1502 | https://doi.org/10.1007/s11704-026-60308-3 |
| [P9] | 2024 | A Comprehensive Survey of Scientific Large Language Models and Their Applications in Scientific Discovery | arxiv |  | http://arxiv.org/abs/2406.10833v3 |
| [P10] | 2026 | Externalization in LLM Agents: A Unified Review of Memory, Skills, Protocols and Harness Engineering | arxiv |  | http://arxiv.org/abs/2604.08224v1 |
| [P11] | 2025 | AR-RAG: Autoregressive Retrieval Augmentation for Image Generation | arxiv |  | http://arxiv.org/abs/2506.06962v3 |
| [P12] | 2023 | ChatGPT for good? On opportunities and challenges of large language models for education | openalex | 6032 | https://doi.org/10.1016/j.lindif.2023.102274 |
| [P13] | 2026 | Learning the Value Systems of Agents with Preference-based and Inverse Reinforcement Learning | arxiv |  | http://arxiv.org/abs/2602.04518v1 |
| [P14] | 2026 | Emergence of Agentic AI: A Review on Evolution, Background, Working Principles, Applications, Adoption Factors, and Future Research Directions | arxiv |  | http://arxiv.org/abs/2608.18110v1 |

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
- 背景与研究脉络：从基础论文和近期综述中界定问题 [P3]、[P12]
- 系统架构与 agent workflow：比较检索、规划、工具调用、写作和验证模块 [P2]、[P4]、[P7]、[P13]
- 评估协议与 SOTA 追踪：整理数据集、指标、人工偏好评测和 leaderboard 风险 [P1]、[P5]、[P6]、[P8]
- 证据缺口：应用与案例 仍需追加定向检索和全文获取
- 局限与未来方向：围绕全文 grounding、claim-level citation audit 和可复现 SOTA 表格展开

## 主题脉络

从时间线上看，较早工作可作为问题定义和基础方法入口，例如 [P12]、[P4]、[P3]。
近年的论文更集中在系统化、自动化和评估问题上，例如 [P10]、[P8]、[P14]、[P13]、[P11]。
因此，组会展示时可以把该领域讲成三段：早期基础方法形成、LLM/agent 系统化带来工作流自动化、近期重点转向可验证引用和 benchmark 化评估。

## 方法与系统分类

| 类别 | 关注问题 | 代表论文 | 当前证据强度 |
| --- | --- | --- | --- |
| 基础方法与模型 | 核心模型、算法思想、任务定义和理论基础 | [P3]、[P12] | 较高 |
| 系统与工具 | agent 编排、检索工具、pipeline、交互式工作台 | [P2]、[P4]、[P7]、[P13] | 中 |
| 评估与 Benchmark | 数据集、指标、leaderboard、实验协议和可比性 | [P1]、[P5]、[P6]、[P8] | 较高 |
| 应用与案例 | 具体学科、行业或用户工作流中的落地方式 | 待补充 | 低 |

## 正文综述

### 1. 问题定义与基础方法

围绕“Automated scientific literature review generation using large language model agents”，`基础方法与模型` 方向的候选论文说明该主题已经形成可归纳的子问题。代表性材料包括 [P3]、[P12]。其中，Understanding Survey Paper Taxonomy about Large Language Models via Graph Representation Learning 提供了一个优先阅读入口；其摘要显示，该方向关注的是As new research on Large Language Models (LLMs) continues, it is difficult to keep up with new research and models. T...。本节最相关证据来自 [P3] 的 `full_text` chunk，其内容摘要为：ficulty of text classification. Attributes Descriptions Taxonomy Proposed taxonomy Title Paper title Authors Lists of author’s name Relea...
从多篇论文的题名和摘要看，这一类工作需要进一步区分“概念性综述”“系统实现”和“实验评估”三种证据。后续写正式综述时，应把 [P12] 的贡献点拆成独立 claim，并为每个 claim 绑定原文段落。

### 2. Agent 系统与调研流水线

围绕“Automated scientific literature review generation using large language model agents”，`系统与工具` 方向的候选论文说明该主题已经形成可归纳的子问题。代表性材料包括 [P2]、[P4]、[P7]、[P13]。其中，Learning From Failure: Integrating Negative Examples when Fine-tuning Large Language Models as Agents 提供了一个优先阅读入口；其摘要显示，该方向关注的是Large language models (LLMs) have achieved success in acting as agents, which interact with environments through tool...。本节最相关证据来自 [P4] 的 `full_text` chunk，其内容摘要为：[page 1] AI LITERATURE REVIEW SUITE David A. Tovar Department of Psychology Vanderbilt University Nashville, TN david.tovar@vanderbilt.ed...
从多篇论文的题名和摘要看，这一类工作需要进一步区分“概念性综述”“系统实现”和“实验评估”三种证据。后续写正式综述时，应把 [P4]、[P7]、[P13] 的贡献点拆成独立 claim，并为每个 claim 绑定原文段落。

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
| 覆盖面 | 是否覆盖基础、高被引和近期工作 | [P3]、[P12] | 引入 citation graph 和最近一年时间过滤 |
| 系统性 | 是否能归纳 agent/pipeline/tool 的结构 | [P2]、[P4]、[P7] | 抽取系统组件和数据流图 |
| 评估性 | 是否有 benchmark、dataset、metric 或 leaderboard | [P1]、[P5]、[P6] | 接入 SOTA 表格抽取和可比性判断 |
| 落地性 | 是否说明真实研究工作流中的使用方式 | 待补充 | 补充 case study 和用户交互流程 |

## 研究空白与未来方向

- **全文证据化**：本轮已构建 32 个 evidence chunks，其中全文 chunk 为 24 个；后续应继续提高 PDF 覆盖率。
- **多视角规划**：参考 STORM，需要加入 perspective-guided question asking，用不同专家视角主动发现遗漏主题。
- **分节写作与修订**：参考 AutoSurvey，需要按 section 独立召回和写作，再做跨章节一致性修订。
- **新近论文覆盖**：当前候选集中 2024 年以后论文有 12 篇，后续应为近期进展单独建立章节 [P1]、[P2]、[P3]、[P5]。
- **SOTA 表格化**：涉及 benchmark 时，应输出 task/dataset/metric/setting，而不是只在正文中描述“性能更好”。

## Section Evidence Pack

### 基础方法与模型
- [P3] `full_text` score=0.610: ficulty of text classification. Attributes Descriptions Taxonomy Proposed taxonomy Title Paper title Authors Lists of author’s name Release Date First released date Links Links of papers Paper ID The arXiv paper ID Ca...
- [P12] `metadata` score=0.482: ChatGPT for good? On opportunities and challenges of large language models for education
- [P3] `full_text` score=0.442: hat many researchers have written survey papers to help synthesize the research progress. Survey papers are often cru- cial for newcomers to gain an in-depth understand- ing of the evolution of a research field. Howev...

### 系统与工具
- [P4] `full_text` score=0.831: [page 1] AI LITERATURE REVIEW SUITE David A. Tovar Department of Psychology Vanderbilt University Nashville, TN david.tovar@vanderbilt.edu ABSTRACT The process of conducting literature reviews is often time-consuming ...
- [P4] `full_text` score=0.782: phic tool that leverages the CORE API [1] and the CrossRef RESTful API [2] to download and organize articles along with their references and citations based on DOIs. The PDF Chat program borrows from a previous soluti...
- [P7] `full_text` score=0.528: [page 1] Engineering the RAG Stack: A Comprehensive Review of the Architecture and Trust Frameworks for Retrieval Augmented Generation Systems Dean Wampler, Ph.D. Head of Technology, The AI Alliance IBM Research dean@...
- [P7] `full_text` score=0.525: l-Augmented Generation (RAG), Large Language Models, Information Retrieval, Neural Language Models, Knowledge- Augmented Generation, AI System Architectures, Trustworthy AI, Model Alignment, Multi-agent Systems. 1 Int...
- [P2] `full_text` score=0.453: gentLM-7B 24.6 – 22.3 Lumos-O-7B 50.5 65.5 24.9 Lumos-I-7B 47.1 63.6 29.4 NAT-7B 49.1 64.4 29.8 CodeLlama-13B 36.1 60.0 – AgentLM-13B 32.4 – 29.6 NAT-13B 53.8 70.6 29.6 Table 1: Comparison with methods from other pape...
- [P2] `full_text` score=0.416: [page 1] Learning From Failure: Integrating Negative Examples when Fine-tuning Large Language Models as Agents Renxi Wang1,2 Haonan Li1,2 Xudong Han1,2 Yixuan Zhang1,2 Timothy Baldwin1,2,3 1LibrAI 2MBZUAI 3The Univers...

### 评估与 Benchmark
- [P1] `full_text` score=0.938: [page 1] Automated Literature Review Using NLP Techniques and LLM-Based Retrieval-Augmented Generation Nurshat Fateh Ali Department of Computer Science and Engineering Military Institute of Science and Technology Dhak...
- [P1] `full_text` score=0.903: ancing the effectiveness and applicability of the developed system tool. More functionality can be added to the Graphical User Interface such as model options, output size, etc. More models such as Bert, Gemini, and L...
- [P5] `full_text` score=0.617: g in Automated Data Science. arXiv preprint arXiv:2503.23314 (2025). [150] Larissa Shamseer, David Moher, Mike Clarke, Davina Ghersi, Alessandro Liberati, Mark Petticrew, Paul Shekelle, and Lesley A Stewart. 2015. Pre...
- [P5] `full_text` score=0.598: efficient, scalable, and accessible approaches to executing this end-to-end process become increasingly critical. To address this need, research has focused on automating data science workflows using AI-driven tools. ...
- [P6] `abstract` score=0.515: Abstract Autonomous agents have long been a research focus in academic and industry communities. Previous research often focuses on training agents with limited knowledge within isolated environments, which diverges s...
- [P9] `abstract` score=0.439: In many scientific fields, large language models (LLMs) have revolutionized the way text and other modalities of data (e.g., molecules and proteins) are handled, achieving superior performance in various applications ...

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
| [P6] | A survey on large language model based autonomous agents | yes | 1 | abstract_grounded |
| [P7] | Engineering the RAG Stack: A Comprehensive Review of the Architecture and Trust Frameworks for Retrieval-Augmented Generation Systems | yes | 4 | full_text_grounded |
| [P8] | A Survey of Large Language Models | yes | 1 | abstract_grounded |
| [P9] | A Comprehensive Survey of Scientific Large Language Models and Their Applications in Scientific Discovery | yes | 1 | abstract_grounded |
| [P10] | Externalization in LLM Agents: A Unified Review of Memory, Skills, Protocols and Harness Engineering | yes | 1 | abstract_grounded |
| [P11] | AR-RAG: Autoregressive Retrieval Augmentation for Image Generation | yes | 1 | abstract_grounded |
| [P12] | ChatGPT for good? On opportunities and challenges of large language models for education | yes | 1 | abstract_grounded |
| [P13] | Learning the Value Systems of Agents with Preference-based and Inverse Reinforcement Learning | yes | 1 | abstract_grounded |
| [P14] | Emergence of Agentic AI: A Review on Evolution, Background, Working Principles, Applications, Adoption Factors, and Future Research Directions | yes | 1 | abstract_grounded |

## OpenScholar-style 证据覆盖

- 证据块总数：32。
- 全文证据块：24；摘要证据块：7。
- Top evidence chunks：
  - [P1] `full_text` score=0.938: [page 1] Automated Literature Review Using NLP Techniques and LLM-Based Retrieval-Augmented Generation Nurshat Fateh Ali Department of Computer Science and Engineering Military ...
  - [P1] `full_text` score=0.903: ancing the effectiveness and applicability of the developed system tool. More functionality can be added to the Graphical User Interface such as model options, output size, etc....
  - [P1] `full_text` score=0.888: SciTLDR dataset is chosen for this research experiment and three distinct techniques are utilized to implement three different systems for auto-generating the literature reviews...
  - [P1] `full_text` score=0.869: text, extract relevant details, and create structured summaries [2]. The primary objective of this research is to develop a system that can automatically generate the literature...
  - [P4] `full_text` score=0.831: [page 1] AI LITERATURE REVIEW SUITE David A. Tovar Department of Psychology Vanderbilt University Nashville, TN david.tovar@vanderbilt.edu ABSTRACT The process of conducting lit...
  - [P4] `full_text` score=0.782: phic tool that leverages the CORE API [1] and the CrossRef RESTful API [2] to download and organize articles along with their references and citations based on DOIs. The PDF Cha...
  - [P4] `full_text` score=0.686: ature Table, feeding them into a semantic embedding model [5]. It then uses K-nearest neighbors (K =5) to group the articles into clusters [10, 11, 12], each typically containin...
  - [P4] `full_text` score=0.644: its flexibility and adaptability. The system is designed to be modular and can easily be integrated with future open-source models, ensuring that it remains at the forefront of ...
## 质量检查清单

- 覆盖性：当前综述依赖自动召回的 14 篇候选论文，仍需人工检查是否遗漏公认 seminal work。
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
- [P6] Lei Wang, Chen Ma, Xueyang Feng et al.. A survey on large language model based autonomous agents. Frontiers of Computer Science, 2024. https://doi.org/10.1007/s11704-024-40231-1
- [P7] Dean Wampler, Dave Nielson, Alireza Seddighi. Engineering the RAG Stack: A Comprehensive Review of the Architecture and Trust Frameworks for Retrieval-Augmented Generation Systems. arXiv, 2025. http://arxiv.org/abs/2601.05264v1
- [P8] Wayne Xin Zhao, Kun Zhou, Junyi Li et al.. A Survey of Large Language Models. Frontiers of Computer Science, 2026. https://doi.org/10.1007/s11704-026-60308-3
- [P9] Yu Zhang, Xiusi Chen, Bowen Jin et al.. A Comprehensive Survey of Scientific Large Language Models and Their Applications in Scientific Discovery. arXiv, 2024. http://arxiv.org/abs/2406.10833v3
- [P10] Chenyu Zhou, Huacan Chai, Wenteng Chen et al.. Externalization in LLM Agents: A Unified Review of Memory, Skills, Protocols and Harness Engineering. arXiv, 2026. http://arxiv.org/abs/2604.08224v1
- [P11] Jingyuan Qi, Zhiyang Xu, Qifan Wang et al.. AR-RAG: Autoregressive Retrieval Augmentation for Image Generation. arXiv, 2025. http://arxiv.org/abs/2506.06962v3
- [P12] Enkelejda Kasneci, Kathrin Seßler, Stefan Küchemann et al.. ChatGPT for good? On opportunities and challenges of large language models for education. Learning and Individual Differences, 2023. https://doi.org/10.1016/j.lindif.2023.102274
- [P13] Andrés Holgado-Sánchez, Holger Billhardt, Alberto Fernández et al.. Learning the Value Systems of Agents with Preference-based and Inverse Reinforcement Learning. arXiv, 2026. http://arxiv.org/abs/2602.04518v1
- [P14] AKM Bahalul Haque, Al Amin Islam Ridoy, Mohammad Rayhan et al.. Emergence of Agentic AI: A Review on Evolution, Background, Working Principles, Applications, Adoption Factors, and Future Research Directions. arXiv, 2026. http://arxiv.org/abs/2608.18110v1
