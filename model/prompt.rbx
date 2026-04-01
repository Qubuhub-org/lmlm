require 'ollama'

# Initialize the client (defaults to http://localhost:11434)
client = Ollama.new

# Generate a simple completion
response = client.generate(
  model: 'llama3',
  prompt: 'Why is the sky blue?'
)

puts response['response']

# Or use the Chat interface for conversation history
chat_response = client.chat(
  model: 'llama3',
  messages: [
    { role: 'user', content: 'Hello! Who are you?' }
  ]
)

puts chat_response['message']['content']
