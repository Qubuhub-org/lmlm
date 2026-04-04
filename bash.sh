``bafybeigdyrzt5sfp7udm7hu76uh7y26nf3efuylqabf3oclgtqy55fbzdi.llvms``
ollama pull llama3.2
echo "FROM llama3.2" >> Modelfile
echo "SYSTEM You are a friendly assistant." >> Modelfile
ollama create -f Modelfile lmlm/Lmkm
ollama push lmlm/Lmkm

ollama pull llama3.2
echo "FROM llama3.2" >> Modelfile
echo "SYSTEM You are a friendly assistant." >> Modelfile
ollama create -f Modelfile lmlm/Ollama.ai
ollama push lmlm/Ollama.ai
ollama run lmlm/Ollama.ai
cat << 'EOF' > Modelfile
FROM llama3.2

# Set parameters for technical precision
PARAMETER temperature 0.3
PARAMETER num_ctx 4096

# Define technical expertise in the System Prompt
SYSTEM """
You are a Senior Software Engineer and Data Scientist. 
- When writing code, prioritize security, readability, and modern best practices.
- For data analysis, explain your statistical reasoning and suggest Python (Pandas/NumPy) or SQL solutions.
- Format all code snippets in markdown blocks with the correct language tag.
- If a technical request is ambiguous, ask clarifying questions before providing a solution.
"""
EOFssh exe.dev new --name=myname



# Update and push
ollama create -f Modelfile lmlm/Ollama.ai
ollama push lmlm/Ollama.ai


# Example: Add this to your Modelfile to teach it about your specific database
MESSAGE user "What is the schema for our user table?"
MESSAGE assistant "The 'users' table has four columns: id (INT), username (VARCHAR), email (VARCHAR), and created_at (TIMESTAMP)."
