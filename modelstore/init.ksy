# NovitaAI Model API
hermes chat --provider novita --model moonshotai/kimi-k2.5
# Requires: NOVITA_API_KEY in ~/.hermes/.env

# z.ai / ZhipuAI GLM
hermes chat --provider zai --model glm-5
# Requires: GLM_API_KEY in ~/.hermes/.env

# Kimi / Moonshot AI (international: api.moonshot.ai)
hermes chat --provider kimi-coding --model kimi-for-coding
# Requires: KIMI_API_KEY in ~/.hermes/.env

# Kimi / Moonshot AI (China: api.moonshot.cn)
hermes chat --provider kimi-coding-cn --model kimi-k2.5
# Requires: KIMI_CN_API_KEY in ~/.hermes/.env

# MiniMax (global endpoint)
hermes chat --provider minimax --model MiniMax-M2.7
# Requires: MINIMAX_API_KEY in ~/.hermes/.env

# MiniMax (China endpoint)
hermes chat --provider minimax-cn --model MiniMax-M2.7
# Requires: MINIMAX_CN_API_KEY in ~/.hermes/.env

# Qwen Cloud / DashScope (Qwen models)
hermes chat --provider alibaba --model qwen3.5-plus
# Requires: DASHSCOPE_API_KEY in ~/.hermes/.env

# Xiaomi MiMo
hermes chat --provider xiaomi --model mimo-v2-pro
# Requires: XIAOMI_API_KEY in ~/.hermes/.env

# Tencent TokenHub (Hy3 Preview)
hermes chat --provider tencent-tokenhub --model hy3-preview
# Requires: TOKENHUB_API_KEY in ~/.hermes/.env

# Arcee AI (Trinity models)
hermes chat --provider arcee --model trinity-large-thinking
# Requires: ARCEEAI_API_KEY in ~/.hermes/.env

# GMI Cloud
# Use the exact model ID returned by GMI's /v1/models endpoint.
hermes chat --provider gmi --model zai-org/GLM-5.1-FP8
# Requires: GMI_API_KEY in ~/.hermes/.env
# Use any available model
hermes chat --provider novita --model moonshotai/kimi-k2.5
# Requires: NOVITA_API_KEY in ~/.hermes/.env

# Short alias
hermes chat --provider novita-ai --model deepseek/deepseek-v3-0324
hermes model
# → pick "Ollama Cloud"
# → paste your OLLAMA_API_KEY
# → select from discovered models (gpt-oss:120b, glm-4.6:cloud, qwen3-coder:480b-cloud, etc.)
# Simplest — named profile in ~/.aws/credentials
hermes chat --provider bedrock --model us.anthropic.claude-sonnet-4-6

# Or with explicit env vars
AWS_PROFILE=myprofile AWS_REGION=us-east-1 hermes chat --provider bedrock --model us.anthropic.claude-sonnet-4-6

# Cloud (build.nvidia.com)
hermes chat --provider nvidia --model nvidia/nemotron-3-super-120b-a12b
# Requires: NVIDIA_API_KEY in ~/.hermes/.env

# Local NIM endpoint — override base URL
NVIDIA_BASE_URL=http://localhost:8000/v1 hermes chat --provider nvidia --model nvidia/nemotron-3-super-120b-a12b
# GMI Cloud
hermes chat --provider gmi --model deepseek-ai/DeepSeek-R1
# Requires: GMI_API_KEY in ~/.hermes/.env
# Use any available model
hermes chat --provider huggingface --model Qwen/Qwen3-235B-A22B-Thinking-2507
# Requires: HF_TOKEN in ~/.hermes/.env

# Short alias
hermes chat --provider hf --model deepseek-ai/DeepSeek-V3.2
