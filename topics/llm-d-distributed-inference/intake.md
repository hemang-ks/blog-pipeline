# Intake — What llm-d changes about distributed inference on Kubernetes

Mode: technical
Audience: platform engineering leads running vLLM on Kubernetes/OpenShift who are hitting scaling limits
Reader walks away with: when llm-d's disaggregated, cache-aware serving is worth the added complexity over plain vLLM replicas
My angle (optional): most teams scale inference by adding replicas when their real problem is KV-cache reuse and routing
Position to use (optional):
Stories I could use (optional, anonymized):
- 
Must include:
- prefill/decode disaggregation, KV-cache-aware routing
Must avoid:
- vendor pitch tone; any client names
Length override (optional):
Publish target: substack