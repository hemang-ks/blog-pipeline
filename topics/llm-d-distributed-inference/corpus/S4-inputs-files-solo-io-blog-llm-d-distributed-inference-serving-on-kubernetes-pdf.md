---
id: S4
title: inputs/files/Solo.io Blog _ llm-d_ Distributed Inference Serving on Kubernetes
  .pdf
origin: inputs/files/Solo.io Blog _ llm-d_ Distributed Inference Serving on Kubernetes
  .pdf
author: null
published: null
fetched: '2026-10-02'
words: 1276
status: ok
---

Solo.io Blog | llm-d: Distributed Inference Serving on Kubernetes | Solo.io 

10/2/26, 12:22 AM 

Cloud Connectivity 

AI Agentic 

Get Started 

### Christian Posta 

# llm-d: Distributed Inference Serving on Kubernetes 



VP, Global Field CTO 

Christian Posta (@christianposta) is Global Field CTO at Solo.io supporting customers and end users in their adoption of cloud-native technologies. He is an author for Manning and O’Reilly publications, open source contributor, blogger and sought after speaker on Envoy Proxy and Kubernetes technologies. Prior to Solo.io, Chrisitian was a Speak now Chief Architect at Red Hat, FuseSource and Book a Meetingheld engineering positions at Ask a question…organizations like Wel ~~ls~~ Fargo, Apollo Group, This session and your communications may beIntel. monitored and recorded. View our Privacy <u>Policy</u> 

May 20, 2025 Christian Posta 

Today, Red Hat, Google, and IBM announced an exciting new open-source project called llm-d; a distributed inference platform built around vLLM. Personally, I’m very excited about this project as we know working with users and the community how difficult it is to build a cost-effective and performant inference platform. Organizations trying to run inference themselves have likely run into the main motivation for the llm-d project (quoted from the press release): 

https://www.solo.io/blog/llm-d-distributed-inference-serving-on-kubernetes 

1/8 

Solo.io Blog | llm-d: Distributed Inference Serving on Kubernetes | Solo.io 

10/2/26, 12:22 AM 

The escalating resource demands ~~of increasingly sophisticated and~~ larger reasoning models limits the viability of centralized inference and threatens to bottleneck AI innovation with prohibitive costs and crippling latency. 

AI Agentic Cloud Connectivity 

~~ADDITIONAL~~ RESOURCES 

#### Get Started 

Ambient Mesh Lab: Waypoints for Traffic management, Security and Observability 

Post 

Said another way (in my words): to get good inference results, you need larger models. Larger models are expensive, and inference is ultimately wasteful if not improved. Disaggregation, distribution, smart caching, and inference-aware routing can significantly improve inference. 

Introducing Solo Enterprise for agentgateway 

Post 

llm-d brings those improvements. 

llm-d focuses on two key areas that allow many optimizations: 

- Disaggregation of certain phases (prefill and decode) of inference, so they can be distributed 

- A powerful routing layer, to account for distribution and optimizations 

Establishing zero trust security for modern cloud architectures 



<!-- Start of picture text -->
Post<br><!-- End of picture text -->

The powerful routing layer used in the llm-d project is built on the Kubernetes Gateway API Inference Extension API and kgateway (with Istio also an option). Let’s take a closer look. 

This session and your communications may be monitored and recorded. View our Privacy <u>Policy</u> 

https://www.solo.io/blog/llm-d-distributed-inference-serving-on-kubernetes 

2/8 

Solo.io Blog | llm-d: Distributed Inference Serving on Kubernetes | Solo.io 

10/2/26, 12:22 AM 

AI Agentic Cloud Connectivity 

## Why is llm-d Needed? 

LLM inference poses unique challenges traditional infrastructures weren’t designed to handle. Unlike standard web services/APIs, LLM requests have dramatically different “shapes”. These different shapes cause inefficient usage of GPU compute and memory for inference. Inference begins with a “prefill” phase, which computes vectors for each token in the context and stores them into the KV cache/GPU memory. This is a very compute intensive phase and the GPUs are optimized for this. The second phase is “decode”, where the model generates new tokens using the KV cache from the previous phase. This phase is very memory bandwidth intensive, but leaves compute underutilized. The GPU cycles are essentially wasted. This is highly inefficient. 

Get Started 

Additionally, similar requests/prompts often share common prefixes that can be cached to avoid redundant computation. Standard load balancing approaches treat all replicas equally and distribute requests without considering these critical aspects, leading to suboptimal performance and wasted expensive GPU resources. 

## The Critical Role of Intelligent Routing 

At the heart of llm-d’s architecture is its intelligent routing layer, built on kgateway and the Inference Extension projects. kgateweay is a powerful AI 

This session and your communications may be monitored and recorded. View our Privacy <u>Policy</u> 

https://www.solo.io/blog/llm-d-distributed-inference-serving-on-kubernetes 

3/8 

Solo.io Blog | llm-d: Distributed Inference Serving on Kubernetes | Solo.io 

10/2/26, 12:22 AM 

gateway built on Envoy proxy. Traditional load balancers use simple algorithms like round-robin or least requests, but llm-d’s routing layer makes sophisticated decisions based on real-time metrics from the model servers themselves. It routes requests to servers with cached KV entries for similar prefixes, and balances load based on actual GPU memory utilization rather than just request count. The routing layer also implements filtering and scoring algorithms for making smart scheduling decisions, including supporting disaggregated serving where prefill and decode operations can run on separate specialized workers and infrastructure. In benchmark tests, this smart routing delivered up to 3x improvements in time-to-first-token and doubled throughput under SLO constraints. 

AI Agentic Cloud Connectivity 

Get Started 



## kgateway: The Enabler of Intelligent Inference 

kgateway provides the perfect foundation for llmd’s intelligent routing through its implementation of the Inference Extension. This extension introduces InferenceModel and InferencePool resources that enable AI-specific routing patterns. For out-of-thebox inference capabilities in kgateway, when a 

This session and your communications may be monitored and recorded. View our Privacy <u>Policy</u> 

https://www.solo.io/blog/llm-d-distributed-inference-serving-on-kubernetes 

4/8 

Solo.io Blog | llm-d: Distributed Inference Serving on Kubernetes | Solo.io 

10/2/26, 12:22 AM 

AI Agentic Cloud Connectivity 

request comes to the gateway, it flows through the Endpoint Selection Extension (following the Endpoint Picker Protocol) which examines the model name, LoRA adapter requirements, and request criticality; then selects the optimal backend based on queue depth, KV cache utilization, and adapter availability. 

Get Started 

This allows critical requests to be prioritized, while sheddable requests can be handled opportunistically or even dropped when the system is under pressure — all while maximizing GPU resource utilization. llm-d introduces its own scheduler that implements the EPP and brings more powerful selection decisioning. 

## A Complete Distributed Inference Solution 

As inference costs dominate AI deployment budgets, intelligent routing becomes an essential component in building efficient, scalable, and costeffective AI systems. 

Beyond intelligent routing, llm-d delivers a full distributed inference solution by extending vLLM to support disaggregated serving and enhanced prefix caching. The combination of kgateway’s sophisticated routing with these compute optimizations creates a system that dramatically improves both performance and cost-efficiency. You can explore this powerful combination on GitHub or try the quickstart guides to deploy it on your Kubernetes cluster. 

This session and your communications may be monitored and recorded. View our Privacy <u>Policy</u> 

5/8 

https://www.solo.io/blog/llm-d-distributed-inference-serving-on-kubernetes 

Solo.io Blog | llm-d: Distributed Inference Serving on Kubernetes | Solo.io 

10/2/26, 12:22 AM 

Cloud Connectivity 

AI Agentic 

Get Started 

FEATURED CONTENT 



Ambient Mesh Lab: Waypoints for Traffic management, Security and Observability 

Solo Lab | Waypoints in Ambient Mesh: For L4 and L7 Security,… 

Read Lab 

See More 





Introducing Solo Enterprise for agentgateway 

Establishing zero trust security for modern cloud architectures 

Secure, govern, and operationalize AI agent connectivity at… 

How your organization 

can ensure safer cloud architecture b… 

Read Datasheet 

Read Ebook 

This session and your communications may be monitored and recorded. View our Privacy <u><mark>Policy</mark></u> 

https://www.solo.io/blog/llm-d-distributed-inference-serving-on-kubernetes 

6/8 

Solo.io Blog | llm-d: Distributed Inference Serving on Kubernetes | Solo.io 

10/2/26, 12:22 AM 

AI Agentic Cloud Connectivity 



<!-- Start of picture text -->
Get Started<br><!-- End of picture text -->

Cloud connectivity done right 



<!-- Start of picture text -->
PRODUCTS LEARN TOPIC COMPANY CONTACT<br>SERIES SOLO<br>AGENTIC Docs Careers<br>INFRASTRUCTURE All Topic Contact<br>Customers About Us<br>Series Solo.io<br>agentregistry Resource Newsroom<br>AI Gateway Get Support<br>Library<br>kagent AI & Agentic Community Contact Sales<br>Blog Voices<br>agentgateway<br>API Gateway Pricing<br>Solo Partners<br>agentdesktop<br>Academy Service Mesh<br>Trust Center<br>Zero Trust<br>CLOUD<br>This session and your communications may be<br>CONNECTIVITY monitored and recorded. View our Privacy<br>Policy<br>Istio<br><!-- End of picture text -->

https://www.solo.io/blog/llm-d-distributed-inference-serving-on-kubernetes 

7/8 

Solo.io Blog | llm-d: Distributed Inference Serving on Kubernetes | Solo.io 

10/2/26, 12:22 AM 

kgateway 

Cloud Connectivity 

AI Agentic 

Get Started 

© 2026 Solo.io, inc. All Rights Reserved. Privacy Policy Security Terms of Use 

This session and your communications may be monitored and recorded. View our Privacy <u><mark>Policy</mark></u> 

https://www.solo.io/blog/llm-d-distributed-inference-serving-on-kubernetes 

8/8 


