---
id: S1
title: What is llm-d?
origin: https://www.redhat.com/en/topics/ai/what-is-llm-d
author: null
published: '2026-02-18'
fetched: '2026-10-02'
words: 1612
status: ok
---

## What is llm-d?

llm-d is a Kubernetes-native, open source framework that speeds up distributed large language model (LLM) inference at scale.

This means when an AI model receives complicated queries with a lot of data, llm-d provides a framework that makes processing faster.

llm-d was created by Google, NVIDIA, IBM Research, and CoreWeave. Its open source community contributes updates to improve the technology.

## How does llm-d work?

LLM prompts can be complex and nonuniform. They typically require extensive computational resources and storage to process large amounts of data.

llm-d has a modular architecture that can support the increasing resource demands of sophisticated and larger reasoning models like LLMs.

A modular architecture allows all the different parts of the AI workload to work either together or separately, depending on the model's needs. This helps the model inference faster.

**Imagine llm-d is like a marathon race:** Each runner is in control of their own pace. You may cross the finish line at a different time than others, but everyone finishes when they’re ready. If everyone had to cross the finish line at the same time, you’d be tied to various unique needs of other runners, like endurance, water breaks, or time spent training. That would make things complicated. 

A modular architecture lets pieces of the inference process work at their own pace to reach the best result as quickly as possible. It makes it easier to fix or update specific processes independently, too.

This specific way of processing models allows llm-d to handle the demands of LLM inference at scale. It also empowers users to go beyond single-server deployments and use generative AI (gen AI) inference across the enterprise.

The llm-d modular architecture is made up of:

- **Kubernetes****:** an open source container-orchestration platform that automates many of the manual processes involved in deploying, managing, and scaling containerized applications.
- **vLLM****:** an open source inference server that speeds up the outputs of gen AI applications.
- **Inference Gateway (IGW):** a Kubernetes Gateway API extension that hosts features like model routing, serving priority, and “smart” load-balancing capabilities.

This accessible, modular architecture makes llm-d an ideal platform for distributed LLM inference at scale.

## 4 key considerations for implementing AI technology

## What are well-lit paths?

Well-lit paths refer to specific “blueprints” or strategies for building distributed inference at scale with llm-d. These well-lit paths are proven and replicable by the llm-d open source community. They’re defined as:

- **Intelligent inference scheduler:** Intelligent inference scheduling handles nuanced token-routing decisions. Its token-aware routing (also known as “smart” load-balancing) capabilities considers the model’s key value (KV) cache, latency, modular functionality, and observability to implement scoring and filtering algorithms that speed up inference.
- **Disaggregate prefill and decode services:** Prefill (prompt-processing) and decode (token-generation) services place different computational demands on inference servers. When the 2 operations are disaggregated (separated), each can work and be scaled independently. This keeps isolated issues, like latency bottlenecks, from affecting all the models at once.
- **Wide expert parallelism:** Mixture-of-experts (MoE) models break down into specifically skilled models that can handle prompts individually. Instead of a single, dense model relying on its entire database to answer each prompt, llm-d identifies 1 “expert” model that’s best suited to answer the prompt. It’s similar to using the “find” feature to locate a word in a document, rather than reading the whole text. This approach speeds up inference and uses GPUs more efficiently.

In addition to the well-lit paths, llm-d uses intelligent inference tools to boost inference efficiency:

- **Token-aware routing:** A token’s varying computational needs trigger its specific route during inference. Inference traffic is routed based on token length, queue depth, and cache hit predictions to reduce latency and avoid long disruptions.Using our race analogy, a slower runner (complex model) may take a path with fewer hills (smart load balancing) to cross the finish line (inference) as quickly as possible. **Why you should care about inference**
- **Shared KV cache and reuse:** Shared KV cache recognizes repeated tokens to decrease the time it takes to decode each key value.
For example, a prompt for the capital of Arizona will need to be decoded into 2 tokens: “What is the capital” and “of Arizona.” When the model is prompted for the capital of another state (“What is the capital of Alaska?”), it knows how to process the first token (“What is the capital”) because it has been previously calculated. This avoids redundant prefill computations, speeding up inference by using less GPU storage to answer each prompt.
- **Modular deployment and observability:** Monitor, scale, and update modular models independently from each other. Instead of a “black box” that limits visibility, modular flexibility provides insights into each part of the framework. This makes it easier to adjust models more quickly and align AI workloads with today’s typical DevOps and GitOps practices.

## Core components of llm-d

The open source community built llm-d, which is why its functionality depends on various moving parts and collaborations. Its core components include:

- **Kubernetes-native framework:** llm-d is designed to run within a Kubernetes platform and take advantage of all its benefits. To make the llm-d framework accessible, it’s built for Kubernetes-based distributed platforms (like Red Hat® OpenShift®). This Kubernetes-native approach provides the policy, security, and observability layer needed to apply gen AI inference across an organization.
- **Distributed LLM inference:** Distributed inference allocates a complex inference request across multiple servers and edge devices. From there, each function works in parallel to create an output, resulting in faster and more scalable AI-powered services. llm-d uses open source community projects―such as Envoy, vLLM, and Kserve―to achieve distributed inference.
- **Community-powered open source project:** Open source communities allow good ideas to come from anywhere and improve technologies that everyone can use. This open source project leans on ideas from industry leaders, such as Google, IBM, CoreWeave, NVIDIA, and Red Hat.

These components allow enterprises to use llm-d to scale gen AI use cases, without concerns of latency, complexities, or high costs.

## How is llm-d different from other methods of processing LLMs?

Typical AI model prompts follow a pattern: They’re often short and replicated. Therefore, each prompt gets the same support and resources, sometimes called “round-robin” load balancing.

But LLMs are different from traditional workloads. LLMs run long decode phases, rely on prefix cache reuse, and have different compute and memory needs. That’s why typical Kubernetes load balancing falls short of complicated LLM needs.

On top of that, most organizations deploy LLMs with little visibility, which limits control over their AI workloads. This leads to underused GPUs and latency, and inflexible architectures that don’t scale easily. Generic LLM-based inference systems may ignore prompt structure, token count, and cache states, which wastes resources.

For example, retrieval augmented generation (RAG) prompts require different load balancing than prompts that rely on thinking or reasoning. When the workloads get overwhelmed by different prompts that need unique load balancing, the inference process slows down.

**Think of it this way:** Your local bakery is really good at baking pies. It makes apple, blueberry, and pecan pies daily without error. But when the bakery receives orders for croissants, fudge, or wedding cakes, the bakers’ processes are inefficient. They fill fewer orders and tasks fall through the cracks. What your bakery needs is a head chef that can delegate tasks to fulfill orders for both the complicated baked goods and day-to-day pies. The head chef is able to orchestrate the complex scheduling of tasks to fulfill orders—pie or otherwise—in the most efficient way possible. 

When it comes to your AI technology configuration, llm-d is your head chef.

llm-d offers an AI inference platform that’s LLM aware, meaning it’s prepared for the high variance in LLM prompt request characteristics. The open source framework makes it possible to predictably monitor performance, optimize costs, and meet user expectations. llm-d transforms LLM inference into a Kubernetes-native architecture for a manageable inference framework, similarly to a microservice.

When users can’t easily inference at scale, time to market increases and gen AI use cases are more difficult to apply across the organization.

## Benefits of llm-d

llm-d makes scaling disaggregate models more accessible and helps teams reach bigger AI goals in less time with fewer resources.

- **Model quality and performance:** llm-d uses tools like intelligent load balancing to increase the speed of LLM inference response times. The llm-d framework removes typical LLM inference bottlenecks like repetitive inference tokens and black box disruptions. Removing these obstacles improves model performance and developer productivity.
- **Cost-effectiveness:** Because of its modularity, llm-d allows more users to access AI workloads at once and get results faster. This helps engineers and developers get the most out of their models and use GPUs more effectively. By increasing the accessibility and speed, teams can allocate time and resources elsewhere.
- **Control:** llm-d uses disaggregated serving, which introduces a new level of flexibility for LLM inference. By separating the different phases of inference―prefill and decode―the moving parts can work independently and simultaneously, speeding up inference.

## How Red Hat can help

Red Hat AI prioritizes improving access to scalable gen AI inference.

Our AI platform uses vLLM to fulfill the needs of increasingly complex inference and enterprise expectations.

Red Hat AI relies on llm-d to better support enterprise AI workloads at scale. Using the proven orchestration capabilities of Kubernetes, llm-d integrates advanced inference enablement into our existing enterprise AI infrastructure.

Along with becoming another open source success story, llm-d aligns with Red Hat’s vision: any model, any accelerator, any cloud.

### What is llm-d and why do we need it?

We're seeing a significant trend: more organizations are bringing their large language model (LLM) infrastructure in-house.
