# RF Control gRPC Project Makefile

# Variables
PROTO_DIR = proto
SERVER_DIR = server
CLIENT_DIR = client
PROTO_FILE = $(PROTO_DIR)/rfcontrol.proto
PYTHON = python3
PIP = pip3

# Default target
.PHONY: all
all: setup generate

# Setup virtual environment and install dependencies
.PHONY: setup
setup:
	@echo "Setting up project..."
	$(PIP) install -r requirements.txt
	@echo "Setup complete!"

# Generate gRPC Python files from proto
.PHONY: generate
generate: $(PROTO_FILE)
	@echo "Generating gRPC Python files..."
	mkdir -p $(PROTO_DIR)
	$(PYTHON) -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. rfcontrol.proto
	@echo "Generated rfcontrol_pb2.py and rfcontrol_pb2_grpc.py"

# Run the server
.PHONY: server
server: generate
	@echo "Starting RF Control gRPC server..."
	$(PYTHON) server.py

# Run the client in interactive mode
.PHONY: client
client: generate
	@echo "Starting RF Control client..."
	$(PYTHON) client.py --interactive

# Run client with specific parameters (example)
.PHONY: client-example
client-example: generate
	@echo "Running client example..."
	$(PYTHON) client.py --device "MOCK001" --frequency 2400 --gain 10 --power 5 --mode RX

# Clean generated files
.PHONY: clean
clean:
	@echo "Cleaning generated files..."
	rm -f rfcontrol_pb2.py rfcontrol_pb2_grpc.py
	rm -rf __pycache__
	rm -rf .pytest_cache
	@echo "Clean complete!"

# Build Docker image
.PHONY: docker-build
docker-build:
	@echo "Building Docker image..."
	docker build -t rf-control-server .

# Run Docker container
.PHONY: docker-run
docker-run: docker-build
	@echo "Running Docker container..."
	docker run -p 50051:50051 rf-control-server

# Run tests
.PHONY: test
test: generate
	@echo "Running tests..."
	$(PYTHON) -m pytest tests/ -v

# Install development dependencies
.PHONY: dev-setup
dev-setup: setup
	$(PIP) install pytest pytest-asyncio

# Format code
.PHONY: format
format:
	$(PYTHON) -m black server.py client.py
	$(PYTHON) -m isort server.py client.py

# Lint code
.PHONY: lint
lint:
	$(PYTHON) -m flake8 server.py client.py

# Show help
.PHONY: help
help:
	@echo "Available targets:"
	@echo "  all          - Setup and generate files (default)"
	@echo "  setup        - Install dependencies"
	@echo "  generate     - Generate gRPC files from proto"
	@echo "  server       - Run the gRPC server"
	@echo "  client       - Run the client in interactive mode"
	@echo "  client-example - Run client with example parameters"
	@echo "  docker-build - Build Docker image"
	@echo "  docker-run   - Run Docker container"
	@echo "  test         - Run tests"
	@echo "  clean        - Clean generated files"
	@echo "  help         - Show this help"
