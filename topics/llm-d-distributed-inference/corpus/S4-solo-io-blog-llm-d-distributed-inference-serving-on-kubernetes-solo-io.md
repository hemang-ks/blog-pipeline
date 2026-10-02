---
id: S4
title: 'Solo.io Blog | llm-d: Distributed Inference Serving on Kubernetes | Solo.io'
origin: https://www.solo.io/blog/llm-d-distributed-inference-serving-on-kubernetes
author: Solo Io
published: '2026-09-21'
fetched: '2026-10-02'
words: 723
status: ok
---

Today, Red Hat, Google, and IBM announced an exciting new open-source project called llm-d; a distributed inference platform built around vLLM. Personally, I’m very excited about this project as we know working with users and the community how difficult it is to build a cost-effective and performant inference platform. Organizations trying to run inference themselves have likely run into the main motivation for the llm-d project (quoted from the press release):

*The escalating resource demands of increasingly sophisticated and larger reasoning models limits the viability of centralized inference and threatens to bottleneck AI innovation with prohibitive costs and crippling latency.*

Said another way (in my words): to get good inference results, you need larger models. Larger models are expensive, and inference is ultimately wasteful if not improved. Disaggregation, distribution, smart caching, and inference-aware routing can significantly improve inference.

llm-d brings those improvements.

llm-d focuses on two key areas that allow many optimizations:

- Disaggregation of certain phases (prefill and decode) of inference, so they can be distributed
- A powerful routing layer, to account for distribution and optimizations

The powerful routing layer used in the llm-d project is built on the Kubernetes Gateway API Inference Extension API and kgateway (with Istio also an option). Let’s take a closer look.

## Why is llm-d Needed?

LLM inference poses unique challenges traditional infrastructures weren’t designed to handle. Unlike standard web services/APIs, LLM requests have dramatically different “shapes”. These different shapes cause inefficient usage of GPU compute and memory for inference. Inference begins with a “prefill” phase, which computes vectors for each token in the context and stores them into the KV cache/GPU memory. This is a very compute intensive phase and the GPUs are optimized for this. The second phase is “decode”, where the model generates new tokens using the KV cache from the previous phase. This phase is very memory bandwidth intensive, but leaves compute underutilized. The GPU cycles are essentially wasted. This is highly inefficient.

Additionally, similar requests/prompts often share common prefixes that can be cached to avoid redundant computation. Standard load balancing approaches treat all replicas equally and distribute requests without considering these critical aspects, leading to suboptimal performance and wasted expensive GPU resources.

## The Critical Role of Intelligent Routing

At the heart of llm-d’s architecture is its intelligent routing layer, built on kgateway and the Inference Extension projects. kgateweay is a powerful AI gateway built on Envoy proxy. Traditional load balancers use simple algorithms like round-robin or least requests, but llm-d’s routing layer makes sophisticated decisions based on real-time metrics from the model servers themselves. It routes requests to servers with cached KV entries for similar prefixes, and balances load based on actual GPU memory utilization rather than just request count. The routing layer also implements filtering and scoring algorithms for making smart scheduling decisions, including supporting disaggregated serving where prefill and decode operations can run on separate specialized workers and infrastructure. In benchmark tests, this smart routing delivered up to 3x improvements in time-to-first-token and doubled throughput under SLO constraints.

## kgateway: The Enabler of Intelligent Inference

kgateway provides the perfect foundation for llm-d’s intelligent routing through its implementation of the Inference Extension. This extension introduces InferenceModel and InferencePool resources that enable AI-specific routing patterns. For out-of-the-box inference capabilities in kgateway, when a request comes to the gateway, it flows through the Endpoint Selection Extension (following the Endpoint Picker Protocol) which examines the model name, LoRA adapter requirements, and request criticality; then selects the optimal backend based on queue depth, KV cache utilization, and adapter availability.

This allows critical requests to be prioritized, while sheddable requests can be handled opportunistically or even dropped when the system is under pressure — all while maximizing GPU resource utilization. llm-d introduces its own scheduler that implements the EPP and brings more powerful selection decisioning.

## A Complete Distributed Inference Solution

As inference costs dominate AI deployment budgets, intelligent routing becomes an essential component in building efficient, scalable, and cost-effective AI systems.

Beyond intelligent routing, llm-d delivers a full distributed inference solution by extending vLLM to support disaggregated serving and enhanced prefix caching. The combination of kgateway’s sophisticated routing with these compute optimizations creates a system that dramatically improves both performance and cost-efficiency. You can explore this powerful combination on GitHub or try the quickstart guides to deploy it on your Kubernetes cluster.
