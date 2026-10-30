require 'ollama'

# Connect to local Ollama
client = Ollama.new

# Generate an answer
response = client.generate(model: 'llama3', prompt: 'Summarize this index.')
puts response['response']
