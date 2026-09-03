# Automated scientific literature review generation using large language model agents

## summary
利用大语言模型（LLM）智能体自动生成科学文献综述是当前人工智能与科研交叉领域的重要研究方向。该领域已从早期的基础文本分类和检索增强生成（RAG）方法，发展为包含多智能体协作、负样本学习、复杂工具调用和信任框架的系统化工程 [P1, P3, P6, P7]。自动化文献综述不仅涉及单一的文本生成，而是涵盖了从问题界定、广域检索、主题组织、证据压缩到引用核查的完整流水线 [P1, P4]。通过整合外部工具与内部知识，现代系统能够更高效地处理海量学术文献，为科研人员提供结构化的知识摘要与综述草稿 [P1, P6]。

## Background
随着大语言模型相关研究的呈指数级增长，研究人员难以全面跟进最新进展，这促使了自动化文献综述和分类方法的快速发展 [P3]。早期工作主要关注自然语言处理（NLP）技术在文献综述中的应用，并尝试通过图表示学习来理解综述论文的分类体系（Taxonomy），通过提取标题、作者、发布日期和论文ID等属性，有效缓解了传统文本分类的困难 [P3]。与此同时，基于大语言模型的自主智能体研究开始将智能体的动作明确划分为外部工具调用和内部知识利用，为后续的自动化文献检索和内容生成奠定了理论基础 [P6]。Agentic AI 的演变及其工作原理的梳理，也为理解智能体如何执行复杂的科研调研任务提供了宏观的背景框架 [P12]。

## System Architecture
现有的自动化文献综述系统通常摒弃了单次生成的模式，转而采用流水线架构，将流程拆分为预写作检索与大纲生成、带引用的长文写作以及结构化评估等阶段 [P1]。在系统架构层面，检索增强生成（RAG）栈的工程化设计至关重要，其综合架构涵盖了多智能体系统、可信 AI 以及模型对齐等核心组件，以确保生成内容的可靠性与准确性 [P7]。为了支持长周期的文献调研任务，智能体系统中的外化机制（如记忆、技能、协议和 Harness 工程）被统一纳入架构设计，使得系统能够在复杂的学术环境中保持上下文连贯与任务聚焦 [P9]。

## Technological Approaches
在技术方法层面，研究者提出了多种优化大语言模型智能体表现的策略。在模型微调方面，通过整合负样本（即失败经验）来微调作为智能体的 LLM，提出了一种区分正确与错误交互的训练范式，从而显著提升了智能体在环境中的决策能力 [P2]。在检索与推理方面，科学大语言模型及其在科学发现中的应用展示了工具集成推理智能体（如 Tora）的强大能力，使其能够处理复杂的学术逻辑 [P8]。此外，基于偏好和逆强化学习的方法被用于学习智能体的价值系统，确保其在文献筛选和综述生成中符合特定的学术标准与偏好 [P11]。同时，自回归检索增强生成（AR-RAG）等新兴技术也在不断扩展 RAG 在跨模态和复杂生成任务中的应用边界 [P10]。

## Notable Systems and Implementations
在系统实现方面，已有多种代表性工具被开发出来以辅助科研工作者。例如，“AI Literature Review Suite” 提供了一个交互式工作台，能够将参考文献自动分类到子文件夹以增强可读性，并包含用于交互式分析的 PDF Chat 模块，极大简化了后续的文献分析任务 [P4]。另一项研究则比较了多种使用 NLP 技术和基于 LLM 的 RAG 方法来自动生成文献综述的系统，展示了不同技术路线在实际应用中的效果与差异 [P1]。在更广泛的数据科学领域，基于 LLM 的智能体被用于自动化端到端的数据科学工作流，涵盖了从数据可视化到主题漂移检测的多个环节，体现了智能体系统在复杂科研流程中的落地能力 [P5]。

## Applications
这些自动化方法正在逐步融入真实的科研工作流，使文献调研过程变得更加高效、可扩展和易于访问 [P5]。在实际应用中，系统需要处理文献阅读过程中的主题漂移，并执行严格的验证检查以标记可疑的推断，这表明在缺乏可靠领域基础（domain grounding）的情况下，下游的建模和决策仍会受到根本性的限制 [P5]。Agentic AI 的采用因素和应用场景分析表明，这些自动化工具正逐渐从概念验证走向日常的科研文献管理和知识提取工作流中，成为研究人员不可或缺的辅助手段 [P12]。

## Evaluation and Benchmarking
在评估体系方面，研究者开始采用标准化的数据集和指标来衡量系统的性能。例如，在自动化文献综述的评估中，研究者使用了 SciTLDR 数据集，并采用 ROUGE 等指标来评估基于 NLP 和 LLM-based RAG 系统自动生成文献综述的效果 [P1]。评估不仅关注文本生成的覆盖率，还涉及引用质量和事实性的考量。然而，当前的评估体系仍需进一步区分概念性综述、系统实现和实验评估，并需要建立更严格的 claim-level 引用审计和 SOTA 表格化标准，以确保不同系统之间的可比性 [P1, P5]。

## Challenges and Limitations
尽管自动化系统能够提取文本、提取相关细节并创建结构化摘要，但在处理复杂学术逻辑时仍面临诸多挑战 [P1]。主要局限包括全文证据的覆盖率不足、引用质量难以保证以及缺乏可靠的领域基础（domain grounding） [P5]。此外，现有的分类体系（Taxonomy）和系统架构在处理跨章节一致性和长文本生成时，仍难以完全摆脱对人工审核的依赖 [P3, P7]。系统需要更强的 LLM 分节写作和 claim-level 判断能力，以弥补当前自动化流水线在深度逻辑推理上的不足 [P1]。

## Ethical and Legal Considerations
在构建自动化文献综述系统时，信任框架和可信 AI 是架构设计的核心组成部分，旨在确保生成内容的准确性并防止错误信息的传播 [P7]。通过基于偏好和逆强化学习来塑造智能体的价值系统，可以在一定程度上缓解模型在文献筛选和总结时可能产生的偏见或错误推断 [P11]。同时，系统必须内置明确的验证检查机制，以防止在科研决策中传播未经验证或存在逻辑缺陷的结论，从而维护学术研究的严谨性与伦理底线 [P5]。

## Future Directions
未来的研究需要进一步提高全文证据的覆盖率，并引入多视角规划（如 perspective-guided question asking）以主动发现遗漏的主题 [P1]。在系统实现上，需要加强分节写作与跨章节修订，并建立更严格的 claim-level 引用审计机制，以提升综述的学术可靠性 [P1, P5]。此外，针对近期进展（如 2024 年以后的新系统和新基准），需要建立动态的 SOTA 追踪和表格化评估体系，明确任务、数据集、指标和实验设置，从而推动该领域向更可验证、更可复现的方向发展 [P1, P8]。

## References
[P1] Nurshat Fateh Ali, Md. Mahdi Mohtasim, Shakil Mosharrof et al.. Automated Literature Review Using NLP Techniques and LLM-Based Retrieval-Augmented Generation. arXiv, 2024. http://arxiv.org/abs/2411.18583v1
[P2] Renxi Wang, Haonan Li, Xudong Han et al.. Learning From Failure: Integrating Negative Examples when Fine-tuning Large Language Models as Agents. arXiv, 2024. http://arxiv.org/abs/2402.11651v2
[P3] Jun Zhuang, Casey Kennington. Understanding Survey Paper Taxonomy about Large Language Models via Graph Representation Learning. arXiv, 2024. http://arxiv.org/abs/2402.10409v1
[P4] David A. Tovar. AI Literature Review Suite. arXiv, 2023. http://arxiv.org/abs/2308.02443v1
[P5] Mizanur Rahman, Amran Bhuiyan, Mohammed Saidul Islam et al.. LLM-Based Data Science Agents: A Survey of Capabilities, Challenges, and Future Directions. arXiv, 2025. http://arxiv.org/abs/2510.04023v1
[P6] Lei Wang, Chen Ma, Xueyang Feng et al.. A Survey on Large Language Model based Autonomous Agents. arXiv, 2023. http://arxiv.org/abs/2308.11432v7
[P7] Dean Wampler, Dave Nielson, Alireza Seddighi. Engineering the RAG Stack: A Comprehensive Review of the Architecture and Trust Frameworks for Retrieval-Augmented Generation Systems. arXiv, 2025. http://arxiv.org/abs/2601.05264v1
[P8] Yu Zhang, Xiusi Chen, Bowen Jin et al.. A Comprehensive Survey of Scientific Large Language Models and Their Applications in Scientific Discovery. arXiv, 2024. http://arxiv.org/abs/2406.10833v3
[P9] Chenyu Zhou, Huacan Chai, Wenteng Chen et al.. Externalization in LLM Agents: A Unified Review of Memory, Skills, Protocols and Harness Engineering. arXiv, 2026. http://arxiv.org/abs/2604.08224v1
[P10] Jingyuan Qi, Zhiyang Xu, Qifan Wang et al.. AR-RAG: Autoregressive Retrieval Augmentation for Image Generation. arXiv, 2025. http://arxiv.org/abs/2506.06962v3
[P11] Andrés Holgado-Sánchez, Holger Billhardt, Alberto Fernández et al.. Learning the Value Systems of Agents with Preference-based and Inverse Reinforcement Learning. arXiv, 2026. http://arxiv.org/abs/2602.04518v1
[P12] AKM Bahalul Haque, Al Amin Islam Ridoy, Mohammad Rayhan et al.. Emergence of Agentic AI: A Review on Evolution, Background, Working Principles, Applications, Adoption Factors, and Future Research Directions. arXiv, 2026. http://arxiv.org/abs/2608.18110v1
