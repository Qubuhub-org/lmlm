# Build the container image
docker build -t lmlm-engine:latest .

# Run the prompt engine inside the isolated network mapping
docker run --rm -it \
  -e HF_TOKEN="your_token_here" \
  --add-host=host.docker.internal:host-gateway \
  lmlm-engine:latest prompt "Write an optimized binary search function in Go"
