curl https://localhost:0000/api/v1/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $LM_API_TOKEN" \
  -d '{
    "model": "lmlm/gpt-oss-20b",
    "input": "Who are you, and what can you do?"
  }'
