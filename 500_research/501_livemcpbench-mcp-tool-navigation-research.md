# LiveMCPBench: Can Agents Navigate an Ocean of MCP Tools?

<!-- MEMORY_CONTEXT: LOW - Research findings on MCP tool navigation and agent capabilities -->
<!-- CONTEXT_REFERENCE: 400_guides/400_system-overview.md -->

## 🔎 TL;DR {#tldr}

| what this file is | read when | do next |
|---|---|---|
| Research paper on MCP tool navigation benchmarking and agent capabilities | When researching MCP integration or agent tool navigation | Reference for MCP tool design decisions and agent evaluation approaches |

## 📋 Overview

This research paper presents LiveMCPBench, a comprehensive benchmark for evaluating LLM agents' capabilities in navigating large-scale MCP (Model Context Protocol) tool ecosystems. The paper addresses the gap in existing benchmarks that are limited to single-server settings with few tools, providing a framework for evaluating agents in realistic, tool-rich environments.

**Key Contributions:**
- LiveMCPBench: 95 real-world tasks across 6 domains
- LiveMCPTool: 70 MCP servers with 527 tools
- LiveMCPEval: LLM-as-a-Judge evaluation framework
- MCP Copilot Agent: Multi-step agent for dynamic tool navigation

**Research Context:** This paper is relevant for understanding how to design and evaluate agent systems that can effectively navigate large-scale tool ecosystems, particularly relevant for our DSPy-based agent development work.

---

## 📄 Research Paper Content

**Title:** LiveMCPBench: Can Agents Navigate an Ocean of MCP Tools?

**Authors:**
- Mo Guozhao¹,²
- Wenliang Zhong¹,²
- Jiawei Chen¹,²
- Xuanang Chen¹
- Yaojie Lu¹
- Hongyu Lin¹
- Ben He¹,²
- Xianpei Han¹
- Le Sun¹

**Affiliations:**
¹ Chinese Information Processing Laboratory, Institute of Software, Chinese Academy of Sciences  
² University of Chinese Academy of Sciences

**Contact:** {moguozhao2024,zhongwenliang2024,chenjiawei2024,xuanang2020,luyaojie,hongyu,xianpei,sunle}@iscas.ac.cn, benhe@ucas.ac.cn

## 📝 Abstract

With the rapid development of Model Context Protocol (MCP), the number of MCP servers has surpassed 10,000. However, existing MCP benchmarks are limited to single-server settings with only a few tools, hindering effective evaluation of agent capabilities in large-scale, real-world scenarios.

To address this limitation, we present **LiveMCPBench**, the first comprehensive benchmark comprising 95 real-world tasks grounded in the MCP ecosystem, designed to evaluate LLM agents at scale across diverse servers. To support a scalable and reproducible evaluation pipeline in large-scale MCP environments, we curate **LiveMCPTool**, a diverse and readily deployable collection of 70 MCP servers and 527 tools. Furthermore, we introduce **LiveMCPEval**, an LLM-as-a-Judge framework that enables automated and adaptive evaluation in dynamic, time-varying task environments, achieving 81% agreement with human reviewers. Finally, we propose the **MCP Copilot Agent**, a multi-step agent that routes tools for dynamic planning and executes tools for API interaction across the entire LiveMCPTool suite.

Our evaluation covers 10 leading models, with the best-performing model (Claude-Sonnet-4) reaching a 78.95% success rate. However, we observe large performance variance across models, and several widely-used models perform poorly in LiveMCPBench's complex, tool-rich environments. Overall, LiveMCPBench offers the first unified framework for benchmarking LLM agents in realistic, tool-rich, and dynamic MCP environments, laying a solid foundation for scalable and reproducible research on agent capabilities.

**Code and Data:** Available at https://icip-cas.github.io/LiveMCPBench

## 🎯 Introduction

Recent years have witnessed remarkable progress in tool-use agents powered by large language models (LLMs), demonstrating promising potential as a pathway towards artificial general intelligence. As model capabilities advance and application scenarios expand, enabling LLMs to effectively invoke external tools has emerged as a critical research direction for enhancing their generalization and real-world task execution abilities.

Notably, with the widespread adoption of the Model Context Protocol (MCP), an increasing number of real-world tools now expose their functionalities through standardized contextual interfaces, forming a vast ecosystem encompassing more than 10,000 MCP servers. Concurrently, certain pretrained models have begun to directly learn interaction patterns with MCP, further accelerating the evolution of tool-use agents.

However, existing tool-use benchmarks predominantly rely on simulated API interfaces, which suffer from a fundamental limitation. API interfaces exhibit high instability—for instance, 55.6% of APIs in ToolBench have become unavailable, forcing evaluation frameworks to resort to simplified simulated tools, significantly compromising task authenticity and challenge. The emergence of MCP provides a stable tool call interface. For the few MCP benchmarks, their experimental scales remain severely limited, typically involving only a small number of MCP servers (about 10), failing to reflect agents' generalization and decision-making capabilities in a large-scale toolset.

Consequently, two pivotal questions remain underexplored:
1. How can optimal planning and retrieval be achieved in large-scale MCP toolset to accomplish real-world tasks?
2. Can an LLM-driven agent, trained for tool invocation, exhibit meta-tool-learning capabilities—i.e., autonomously explore and compose tools from real-world toolset to complete tasks?

## 🔧 LiveMCPBench Framework

We present LiveMCPBench, a novel benchmark designed to evaluate the capability of agent systems in retrieving appropriate tools from a large-scale MCP toolset to accomplish general-purpose everyday tasks. The construction of such a benchmark necessitates addressing three fundamental challenges:

- **How to construct representative daily tasks requiring multi-step tool use?**
- **How to collect a large, redundant yet functionally complete MCP toolset?**
- **How to automatically evaluate performance on evolving online tasks?**

### Task Construction

To advance the development of practical agents for real-world applications, we create a diverse set of tasks grounded in everyday scenarios, spanning six key domains:

- **Office** (e.g., spreadsheet analysis)
- **Lifestyle** (e.g., news retrieval)
- **Leisure** (e.g., video game inquiries)
- **Finance** (e.g., stock price monitoring)
- **Travel** (e.g., ticket search)
- **Shopping** (e.g., product recommendations)

These scenarios were carefully selected to embody three critical characteristics:
1. **Time-varying**: Tasks exhibit time-sensitive outcomes
2. **Long-horizon**: Tasks require multiple tools to complete
3. **Genuine utility**: Tasks address authentic user needs

The annotation process employed a rigorous two-stage methodology involving two groups of computer science students serving as task **proposers** and **validators**. Proposers first generated scenario-specific tasks based on personal experience, with LLM-assisted ideation permitted but strictly vetted for authenticity. Each proposer then interacted with our toolset to complete their proposed task, meticulously annotating key points to preserve the task's compositional depth. Validators subsequently scrutinized both the task design and corresponding toolchain invocations, eliminating duplicates while enforcing quality standards. This iterative pipeline yielded 95 high-fidelity daily tasks.

### LiveMCPTool Collection

While prior study suggests the existence of over 10,000 MCP servers, curating a practical and accessible toolset remains nontrivial due to critical usability constraints. The predominant challenge stems from dependency fragmentation: the majority of MCP servers necessitate proprietary API keys or integrations with third-party services, rendering them impractical for a standardized toolset.

To address this, we introduce a rigorously validated methodology for constructing a high-quality, dependency-free MCP toolset—prioritizing reproducibility and broad applicability. Our approach first aggregates 5,588 server configurations from mcp.so, then systematically filters out key-dependent servers to eliminate access barriers.

Beyond accessibility, we ensure the toolset's representativeness through structured curation and expert annotation. Tools are taxonomically organized into five functional categories (Discovery, Visualization, File Access, Location, and Miscellaneous), followed by manual vetting to exclude low-quality implementations. This two-stage pipeline yields 70 MCP servers providing 527 tools, each verified for standalone functionality and categorical relevance.

### LiveMCPEval

Automated evaluation of trajectories generated by the agent is essential for benchmarking task performance. However, achieving robust automated evaluation remains challenging due to several factors:

1. **Time-varying nature** of daily tasks
2. **Inherent instability** of MCP tool outputs caused by its online dynamics
3. **Diversity of trajectories** resulting from different tool combinations that can accomplish the same task

To address these challenges, we employ an LLM-as-a-Judge system, leveraging the adaptability of LLMs to dynamically assess task completion based on tool usage patterns and feedback. While dynamic tasks may exhibit variability, they often share a set of critical subtasks or key points that must be fulfilled. Incorporating these key points—whether manually annotated or automatically extracted by LLM—improves the accuracy of the LLM-as-a-Judge system.

In our framework, all tasks are annotated with a verified set of key points to ensure a reliable evaluation. Specifically, given a task T, a set of key points P, agent's execution trajectory A with retrieval and tool-call sequences and descriptions of all tools used D, the evaluator performs binary classification to determine the outcome O as either "Success" or "Failure":

```
O = Evaluator(T, P, A, D)
```

Therefore, we use the success rate as the primary metric.

### MCP Copilot Agent

Due to the dynamic nature of daily tasks and the inherent uncertainty in retrieval systems, a fixed pipeline cannot be effectively employed for tool retrieval and invocation in LiveMCPTool. Instead, we require agents to dynamically adapt to environmental changes.

To model this dynamic tool retrieval and invocation process, we formulate it as a Partially Observable Markov Decision Process (POMDP), as the agent can only make decisions based on the textual descriptions of retrieved tools and feedback from tool execution.

We characterize the toolset environment using the following components:
1. **Hidden state space** S
2. **Observation space** O containing the descriptions of retrieved tools and feedback from tools
3. **Language action space** A, including three key actions—**route**, **execute**, and **response**—along with their associated descriptions
4. **State transition** T: S_t × A → S_{t+1}
5. **Terminal reward** R: S → ℝ quantifying task completion

Our agent implementation is based on the ReACT framework. For the **route** tool, we adopt a retrieval strategy inspired by MCP-Zero, where tool prioritization is determined by a weighted combination of server description similarity and tool description similarity.

## 🧪 Experiments and Results

### Setup

We evaluate 10 frontier models:
- Claude-Opus-4 and Claude-Sonnet-4
- GPT-4.1 and GPT-4.1-Mini
- Gemini-2.5-Pro
- Deepseek-V3 and Deepseek-R1
- Qwen3-235B-A22B and Qwen3-32B
- Qwen2.5-72B-Instruct

For assessment, we employ Deepseek-V3 as our primary evaluation model.

### Main Results

We show the task success rates for different models. Key findings include:

- **Meta-Tool-Learning Capabilities in Claude Models**: The Claude series demonstrates remarkable meta-tool-learning proficiency, with Claude-Sonnet-4 and Claude-Opus-4 achieving success rates of 78.95% and 70.53% respectively. These results indicate their superior ability to effectively explore and combine tools from a large-scale toolset to accomplish complex real-world tasks.

- **Performance Variance Among Models**: We observe substantial performance gap across frontier models. While most contemporary models achieve only 30%–50% task success rates, the Claude series shows significantly superior performance. This performance gap suggests fundamental limitations in the meta-tool-learning capabilities of other models.

- **Domain-Specific Superiority of Claude Models**: The Claude series exhibits particularly dominant performance in Office and Lifestyle scenarios, outperforming other models by more than 30%. This substantial advantage highlights Claude models' unique strengths and adaptability in these specific domains.

To validate the reliability of LiveMCPEval's automatic evaluation, we conducted human annotation of the execution trajectories for the top-performing models (Claude-Sonnet-4 and Claude-Opus-4). We systematically tested all models used in the baselines and calculated human agreement rates.

- **LiveMCPEval demonstrates high accuracy under appropriate model conditions**: Our experiments show that Deepseek-V3 achieves an average human agreement rate of 78.95%, validating the reliability of our evaluation framework. Additionally, GPT-4.1 Mini and Qwen2.5-72B-Instruct exhibit comparable performance, with human agreement rates around 75%, making them viable alternative models for accurate assessment.

- **Certain models prove less suitable for evaluation tasks**: Notably, advanced reasoning models such as Deepseek-R1, Claude-Opus-4, and Qwen3-32B exhibit lower human agreement rates (60%–70%). We hypothesize that this limitation stems from their reduced ability to process long trajectory inputs.

## 📊 Analysis

### Efficiency Analysis

To compare the behavioral characteristics of different models, we present the average number of dialogue turns, used tools, tool execution attempts, and retrieval calls. Based on these metrics, we draw the following conclusions:

- **Claude series models exhibit more proactive exploration and utilization behavior**: Their retrieval and execution frequencies are significantly higher than other models, accompanied by a greater number of used tools. This suggests that Claude models actively engage with and adapt to the tool-augmented environment, demonstrating a stronger tendency to explore and exploit available tools.

- **Most models suffer from severe underutilization of tools**: The average number of tools used by these models remains close to 1, indicating that once a model identifies and adopts a single tool, it tends to rely exclusively on it while neglecting other available tools. This behavior highlights a critical limitation in their ability to dynamically leverage multiple tools during task execution.

In practical applications, a trade-off between model performance and cost must be carefully considered. To provide actionable insights for model selection, we plotted the relationship between logarithmic cost and performance, along with the corresponding pareto frontier.

- **Near-Linear Trade-off on the Pareto Frontier**: The performance and logarithmic cost of models along the pareto frontier exhibit an approximately linear relationship. This observation presents a valuable opportunity for optimizing cost-performance balance in real-world tool-calling agent.

- **Optimal Cost-Performance Models**: The models positioned on the pareto frontier represent the most cost-effective choices for tool calling. These include Qwen3-32B, Qwen2.5-72B-Instruct, Deepseek-R1-0528, and Claude-Sonnet-4, each demonstrating distinct advantages in terms of cost-performance efficiency.

### Error Analysis

We conducted a detailed error analysis on the trajectories of current retrieval and invocation agents to provide insights for future development. Human annotators were employed to classify error types in the trajectories of Claude-Opus-4 and Claude-Sonnet-4. Based on the modules defined in the MCP Copilot Agent framework, we identified four distinct and easily distinguishable error categories. Each erroneous trajectory was uniquely classified into one error type without overlap.

**Query Error**: Query errors occur when the generated query either lacks semantic relevance to the required tools or exhibits a granularity mismatch with tool capabilities. For instance, in the task "summarize today's news and save as PDF," the agent might request a single omnipotent tool despite the availability of specialized tools for news retrieval and PDF generation. Such granularity mismatches prevent the retrieval system from providing appropriate tools, and agents often fail to refine queries based on retrieval feedback. Hallucinated queries for irrelevant tools further exacerbate this issue. These errors stem from limitations in LLMs' task decomposition and planning capabilities, suggesting room for improvement despite their generally competent performance.

**Retrieve Error**: Retrieve errors arise when semantically appropriate queries fail to match available tools due to retrieval system shortcomings. For example, in the task "Convert the YouTube video to MP3 format," the retrieval system may overlook the *youtube downloader* tool (which supports format conversion) due to unrecognized semantic equivalence between "convert to MP3" and the tool's documented "extract audio tracks" functionality. These errors highlight challenges in hierarchical retrieval (e.g., MCP server-tool structures) and semantic similarity computation. Dominating the error distribution, retrieve errors underscore the critical need for enhanced retrieval architectures and more robust similarity metrics.

**Tool Error**: Tool errors occur when the agent retrieves the correct tool but invokes it incorrectly—e.g., via error parameters or incomplete server/tool names. In the task "summarize news and save to specified path," the agent might supply "path name" instead of the required "path" parameter to the save tool. Such inaccuracies reflect limitations in contextual precision and memory retention. While modern LLMs exhibit strong contextual understanding, these errors indicate a need for more sophisticated memory mechanisms to ensure reliable tool usage.

**Other Error**: This category encompasses sporadic failures beyond the above types, including network timeouts or model invocation errors. For example, in "summarize today's news," a network timeout during news retrieval may cause the agent to abandon the task without retries or alternative solutions. Such behavior reveals deficiencies in framework design, particularly the absence of robust error-handling mechanisms (e.g., failure recovery, adaptive tool exploration). The prevalence of these errors suggests that while current frameworks support basic exploration, significant improvements in fault tolerance and proactive problem-solving are needed.

## 📚 Related Work

### Tool-Use Benchmarks

Most existing benchmarks for tool utilization rely on simulated APIs due to the inherent instability of real-world APIs. For instance, API-Bank and StableToolBench employ artificially constructed toolsets to ensure API stability. Other works, such as ToolAlpaca and Seal-Tools, collect real-world API interfaces but are unable to execute actual calls. A third category of tool-use benchmarks, including ToolBench and ShortcutsBench, attempts to integrate real-world APIs but faces challenges due to rapid API changes, leading to frequent tool unavailability.

Recent efforts, like StableToolBench-MirrorAPI, leverage fine-tuned LLMs to simulate API interfaces and calls. However, these prior tool-use benchmarks predominantly focus on API-based tools, which introduces instability and limits functionality—particularly in directly manipulating local user files or enabling complex operations (e.g., interacting with local software).

The emergence of MCP has shifted this paradigm by providing a stable, unified interface, enabling the development of general-purpose toolsets. In this work, we construct a practical MCP toolset, addressing both the instability of APIs and their functional constraints, thereby delivering a comprehensive and reliable real-world tool-use benchmark.

### MCP Benchmarks

The evaluation of MCP systems remains an emerging and rapidly evolving field. Among existing benchmarks, MCPBench stands as one of the earliest efforts, primarily focusing on comparative analyses between MCP tools and traditional API-based tools. Building upon this, MCP-RADAR extends the evaluation scope by introducing a multi-dimensional assessment framework that examines critical aspects such as efficiency, accuracy, and robustness. More recently, MCPEval has advanced the field further by proposing a fine-grained evaluation framework capable of automatically generating queries to assess the performance of MCP servers.

Despite these advancements, existing benchmarks suffer from a key limitation: their evaluations are predominantly conducted on small-scale MCP servers (typically around 10 servers), which inadequately reflects real-world scenarios where agents must operate in large-scale, dynamic environments. To bridge this gap, our work introduces a large-scale MCP toolset and systematically investigates agent capabilities in accomplishing everyday tasks through extensive tool utilization.

Recent efforts, such as RAG-MCP, MCPZero, and ScaleMCP, have explored retrieval methods over large-scale MCP toolsets. However, these approaches are constrained by rigid pipelines that lack dynamic adaptability in tool invocation and error feedback. Furthermore, ScaleMCP relies on a manually constructed toolset with limited functional diversity, restricting its applicability to broader, real-world use cases.

## 🎯 Conclusion

In this paper, we present LiveMCPBench, a benchmark designed to evaluate the capability of agents in accomplishing daily tasks using large-scale MCP toolset. We introduce LiveMCPTool, a comprehensive and readily deployable collection of MCP tools. We propose LiveMCPEval, an automated evaluation framework based on the LLM-as-a-Judge, which effectively assesses complex tool-usage tasks characterized by time-varying dynamics and diverse completion paths. Human evaluations confirm the reliability of LiveMCPEval.

Furthermore, we develop MCP Copilot Agent, an agent framework capable of autonomous exploration and dynamic decision-making in large-scale MCP environments. We conduct extensive evaluations on ten frontier models, revealing limitations in widely-used LLMs when applied to large-scale tool invocation tasks. Our in-depth analysis uncovers distinct behavioral patterns across different models and identifies the most cost-effective solutions.

Finally, through detailed error analysis, we highlight two critical shortcomings in current models:
1. Deficiencies in task decomposition and planning
2. Inadequate adaptation of tool retrieval systems in MCP environments

These findings provide clear directions for future improvements in the field.

## 📋 Limitations

While LiveMCPBench represents a comprehensive benchmarking framework, we acknowledge several limitations in its design and evaluation methodology:

**Dependence on LLM evaluation**: The LiveMCPEval component relies heavily on LLM-based assessment. Although we have validated the evaluation accuracy through human experiments, potential model biases may still influence the results. To mitigate this concern, we conducted extensive case studies analyzing model judgment failure cases, which helps improve the robustness of our evaluation framework.

**Evaluation Assumptions**: Our assessment framework operates under the assumption that agent behavior trajectories and tool descriptions sufficiently reflect task performance, without explicitly verifying the final environmental impact. While this assumption holds in most cases, expanding the toolset could introduce inconsistencies between actual tool effects and their descriptions, potentially compromising evaluation reliability. To address this, we rigorously inspect the quality of LiveMCPTool to minimize such discrepancies.

## 🤖 Ethical Considerations

The advent of large-scale multi-tool retrieving and calling agents promises to revolutionize traditional UI-based interaction paradigms by shifting from complex message retrieval or manual UI operations to automated tool invocation. This transition holds significant potential to reduce usability barriers, enhance operational efficiency, and accelerate progress toward Artificial General Intelligence (AGI). Furthermore, such systems can augment the capabilities of smaller models through automated tool construction by larger models. For instance, when faced with tasks beyond their native competence (e.g., complex code generation), smaller models can leverage tools dynamically encapsulated by larger models through MCP interfaces.

However, alongside these benefits, our framework introduces potential risks that warrant careful consideration. Malicious actors could exploit the system by disguising harmful or unsafe tools through misleading descriptions, potentially inducing models to execute dangerous operations. Such misuse may lead to information security breaches or financial losses. Additionally, erroneous tool invocation by the model—such as unintended deletion of local files—could cause significant losses, underscoring the need for robust safeguards in tool validation and execution monitoring.

## 📊 Task Statistics

LiveMCPBench comprises six categories of tasks, each designed to reflect common real-life scenarios:

- **Office**: This category represents typical office-related tasks, primarily involving reading and writing documents in Word, Excel, and PowerPoint.
- **Lifestyle**: These tasks pertain to daily routines, such as retrieving news updates or querying the latest arXiv papers.
- **Leisure**: This category encompasses entertainment-oriented tasks, including fetching gaming news, obtaining specific game-related information, or retrieving details about museums.
- **Finance**: Tasks in this category focus on personal financial management, such as checking stock prices, analyzing market trends, or obtaining cryptocurrency valuations.
- **Travel**: This category includes tasks related to personal travel, such as route planning, hotel searches, and ticket inquiries.
- **Shopping**: These tasks revolve around personal shopping activities, including product information retrieval and recommendations.

## 🔧 Implementation Details

### Computing Resources and Private Models

In our experiments, we deployed two models: Qwen2.5-72B-Instruct and Qwen3-Embedding-0.6B. The computational infrastructure consisted of a Linux server (Ubuntu 22.04) with 4 NVIDIA A800-80G GPUs and 1TB of memory.

We accessed the following proprietary models through their respective platforms:

- **OpenRouter**: GPT-4.1, GPT-4.1-Mini, DeepSeek-R1-0528, DeepSeek-V3-0324, Qwen3-235B-A22B and Qwen3-32B.
- **Anthropic Console**: Claude-Opus-4-20250514, Claude-Sonnet-4-20250514.
- **Google AI Studio**: Gemini-2.5-Pro.

To address suboptimal greedy decoding in certain reasoning models, we implemented a uniform temperature parameter of 0.7 across all experiments. This configuration introduces controlled stochasticity while maintaining result reliability for long-horizon tasks, as we observed that sporadic randomness has negligible cumulative impact on aggregate performance.

### Tool Retrieval Configuration

For consistent retrieval performance, we established a standardized framework using Qwen2.5-72B-Instruct for tool summarization and Qwen3-Embedding-0.6B for embedding generation. To control for potential variance in this component, we maintained identical retrieval module parameters across all experimental conditions. Given the inherent temporal variability in tool outputs, we conducted all experiments within a tightly controlled window (July 20–27, 2025) to minimize fluctuations attributable to temporal factors.

## 📝 Prompts

### MCP Copilot Agent Prompt

**Prompt for MCP Copilot Agent:**

You are an agent designed to assist users with daily tasks by using external tools. You have access to two tools: a retrieval tool and an execution tool. The retrieval tool allows you to search a large toolset for relevant tools, and the execution tool lets you invoke the tools you retrieved. Whenever possible, you should use these tools to get accurate, up-to-date information and to perform file operations.

Note that you can only response to user once, so you should try to provide a complete answer in your response.

**Task**: mcp-copilot (with *route* and *execute* tool)

**Prompt for route tool:**

This is a tool used to find MCP servers and tools that can solve user needs. When to use this tool:

- When faced with user needs, you (LLM) are unable to solve them on your own and do not have the tools to solve the problem.
- When a user proposes a new task and you (LLM) are unsure which specific tool to use to complete it.
- When the user's request is vague or complex, and feasible tool options need to be explored first.
- This is the first step in executing unknown tasks, known as the "discovery" phase, aimed at finding the correct tool.

**Parameter Description**

Query (string, required): The input query must contain a `<tool_assistant>` tag with server and tool descriptions, for example:

```
<tool_assistant>
server: ... # Platform/permission domain
tool: ... # Operation type + target
</tool_assistant>
```

**Prompt for execute tool:**

A tool for executing a specific tool on a specific server. Select tools only from the results obtained from the previous route each time.

When to use this tool:

- When using the route tool to route to a specific MCP server and tool
- When the 'execute-tool' fails to execute (up to 3 repetitions).
- When the user's needs and previous needs require the same tool.

Parameters explained:

- server_name: string, required. The name of the server where the target tool is located.
- tool_name: string, required. The name of the target tool to be executed.
- params: dictionary or None, optional. A dictionary containing all parameters that need to be passed to the target tool. This can be omitted if the target tool does not require parameters.

### LiveMCPEval Prompt

**Prompt for evaluation:**

You are an expert in evaluating the performance of a tool-use agent. The agent is designed to help a human user use multi-tools to complete a task. Given the user's task, the agent's final response, key points for task completion, and tool call history, your goal is to determine whether the agent has completed the task and achieved all requirements.

Your response must strictly follow the following evaluation criteria!

**Important Evaluation Criteria:**

1. You must carefully check whether the information (e.g. the coordinates of the addresses) comes from the tool call, if the agent get it from the internal knowledge, it should be considered failed.
2. Some tasks require to create files to be considered successful.

**IMPORTANT**

Format your response into two lines as shown below:

Thoughts: <your thoughts and reasoning process based on double-checking each key points and the evaluation criteria>

Status: "success" or "failure"

**Prompt for identify key points:**

You are an expert tasked with analyzing a given task to identify the key points explicitly stated in the task description.

**Objective**: Carefully analyze the task description and extract the critical elements explicitly mentioned in the task for achieving its goal.

**Instructions:**

1. Read the task description carefully.
2. Identify and extract **key points** directly stated in the task description.
   - A **key point** is a critical element, condition, or step explicitly mentioned in the task description.
   - Do not infer or add any unstated elements.

**Respond with:**

- **Key Points**: A numbered list of the explicit key points for completing this task, one per line, without explanations or additional details.

---

## 📚 References

This research paper provides valuable insights into MCP tool navigation and agent capabilities, serving as a reference for our own MCP integration work and agent evaluation approaches.
