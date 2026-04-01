ollama pull llama3.2
echo "FROM llama3.2" >> Modelfile
echo "SYSTEM You are a friendly assistant." >> Modelfile
ollama create -f Modelfile lmlm/Ollama.ai
ollama push lmlm/Ollama.ai
