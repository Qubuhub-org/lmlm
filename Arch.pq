tokenizer.model
tokenizer.json
tokenizer_config.json
special_tokens_map.json

LMLM Nano      300M
LMLM Mini      1B
LMLM Small     3B
LMLM Base      8B
LMLM Pro      14B
LMLM Ultra    32B
LMLM Titan    70B

<lmlm_system>
You are LMLM.

<lmlm_user>
Explain quantum computing.

<lmlm_assistant>
Quantum computing...

<lmlm_image>
<lmlm_audio>
<lmlm_video>
<lmlm_document>
<lmlm_table>
<lmlm_graph>

<lmlm_tool_call>

{
  "tool": "search",
  "query": "weather"
}

<lmlm_tool_result>
...

LMLM
├── lmlm-train
├── lmlm-infer
├── lmlm-chat
├── lmlm-api
├── lmlm-cli
├── lmlm-tokenizer
├── lmlm-hub
├── lmlm-eval
├── lmlm-bench
├── lmlm-datasets
└── lmlm-sdk
