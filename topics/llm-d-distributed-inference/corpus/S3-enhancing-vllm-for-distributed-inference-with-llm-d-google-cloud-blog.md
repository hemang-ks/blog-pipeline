---
id: S3
title: Enhancing vllm for distributed inference with llm-d | Google Cloud Blog
origin: https://cloud.google.com/blog/products/ai-machine-learning/enhancing-vllm-for-distributed-inference-with-llm-d
author: Mark Lohmeyer; Gabe Monroy
published: '2025-05-20'
fetched: '2026-10-02'
words: 593
status: ok
---

# Introducing the next generation of AI inference, powered by llm-d

##### Mark Lohmeyer

VP and GM, AI and Computing Infrastructure

##### Gabe Monroy

VP & GM, Cloud Runtimes

As the world transitions from prototyping AI solutions to deploying AI at scale, efficient AI inference is becoming the gating factor. Two years ago, the challenge was the ever-growing size of AI models. Cloud infrastructure providers responded by supporting orders of magnitude more compute and data. Today, agentic AI workflows and reasoning models create highly variable demands and another exponential increase in processing, easily bogging down the inference process and degrading the user experience. Cloud infrastructure has to evolve again.

Open-source inference engines such as vLLM are a key part of the solution. At Google Cloud Next 25 in April, we announced full vLLM support for Cloud TPUs in Google Kubernetes Engine (GKE), Google Compute Engine, Vertex AI, and Cloud Run. Additionally, given the widespread adoption of Kubernetes for orchestrating inference workloads, we introduced the open-source Gateway API Inference Extension project to add AI-native routing to Kubernetes, and made it available in our GKE Inference Gateway. Customers like Samsung and BentoML are seeing great results from these solutions. And later this year, customers will be able to use these solutions with our seventh-generation Ironwood TPU, purpose-built to build and serve reasoning models by scaling to up to 9,216 liquid-cooled chips in a single pod linked with breakthrough Inter-Chip Interconnect (ICI). But, there’s opportunity for even more innovation and value.

Today, we’re making inference even easier and more cost-effective, by making vLLM fully scalable with Kubernetes-native distributed and disaggregated inference. This new project is called llm-d. Google Cloud is a founding contributor alongside Red Hat, IBM Research, NVIDIA, and CoreWeave, joined by other industry leaders AMD, Cisco, Hugging Face, Intel, Lambda, and Mistral AI. Google has a long history of founding and contributing to key open-source projects that have shaped the cloud, such as Kubernetes, JAX, and Istio, and is committed to being the best platform for AI development. We believe that making llm-d open-source, and community-led, is the best way to make it widely available, so you can run it everywhere and know that a strong community supports it.

llm-d builds upon vLLM’s highly efficient inference engine, adding Google’s proven technology and extensive experience in securely and cost-effectively serving AI at billion-user scale. llm-d includes three major innovations: First, instead of traditional round-robin load balancing, llm-d includes a vLLM-aware inference scheduler, which enables routing requests to instances with prefix-cache hits and low load, achieving latency SLOs with fewer hardware resources. Second, to serve longer requests with higher throughput and lower latency, llm-d supports disaggregated serving, which handles the prefill and decode stages of LLM inference with independent instances. Third, llm-d introduces a multi-tier KV cache for intermediate values (prefixes) to improve response time across different storage tiers and reduce storage costs. llm-d works across frameworks (PyTorch today, JAX later this year), and both GPU and TPU accelerators, to provide choice and flexibility.

We are excited to partner with the community to help you cost-effectively scale AI in your business. llm-d incorporates state-of-the-art distributed serving technologies into an easily deployed Kubernetes stack. Deploying llm-d on Google Cloud provides low-latency and high-performance inference by leveraging Google Cloud’s vast global network, GKE AI capabilities, and AI Hypercomputer integrations across software and hardware accelerators. Early tests by Google Cloud using llm-d show 2x improvements in time-to-first-token for use cases like code completion, enabling more responsive applications.

Visit the llm-d project to learn more, contribute, and get started today.
