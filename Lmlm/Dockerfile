# Start from a lightweight Python runtime base
FROM python:3.11-slim

# Install core cross-compilation tools and Ruby (for ollama-rb)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    ruby-full \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set up your internal application directory
WORKDIR /app

# Copy dependency manifests first to leverage Docker build cache layers
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Install the critical LMLM cross-compilation backend gem
RUN gem install ollama-rb

# Copy the rest of the toolkit repository files
COPY . .

# Set up defaults to point to the local network instance of Ollama
ENV OLLAMA_HOST=http://docker.internal

# Configure the entry script execution pipeline
ENTRYPOINT ["python", "Lmlm.py"]
CMD ["run"]
