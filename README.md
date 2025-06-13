# gRPC-RF-Control
Here's the complete **README.md** in polished Markdown format, structured for clarity and visual appeal:

```markdown
# 📡 RF Device Control System with gRPC

[![Python](https://img.shields.io/badge/Python-3.9+-blue?logo=python)](https://www.python.org/)
[![gRPC](https://img.shields.io/badge/gRPC-1.48+-brightgreen?logo=grpc)](https://grpc.io/)
[![Protocol Buffers](https://img.shields.io/badge/Protobuf-3.20+-red)](https://protobuf.dev/)

A hardware-agnostic control system for configuring RF devices via gRPC with mock UHD integration.

---

## 📌 Table of Contents
- [Features](#-features)
- [Quick Start](#-quick-start)
- [Project Structure](#-project-structure)
- [Core Components](#-core-components)
- [Usage Examples](#-usage-examples)
- [Development](#-development)
- [License](#-license)

---

## ✨ Features
- **Remote Configuration** via gRPC:
  - Set frequency (Hz)
  - Adjust gain (dB)
  - Assign device IDs
- **Mock UHD** Hardware Simulation
- **Input Validation**:
  ```python
  assert -20 <= gain <= 30  # dB range check
  ```
- **CLI Client** with intuitive commands

---

## 🚀 Quick Start

### Prerequisites
```bash
pip install grpcio grpcio-tools
```

### 1. Generate gRPC Code
```bash
python -m grpc_tools.protoc -Iproto --python_out=. --grpc_python_out=. proto/rfcontrol.proto
cp rfcontrol_pb2*.py server/ client/
```

### 2. Run the System
| Component | Command | Expected Output |
|-----------|---------|-----------------|
| **Server** | `cd server && python server.py` | `INFO: Server listening on port 50051` |
| **Client** | `cd client && python client.py --frequency 2.4e9 --gain 20` | Success confirmation |

---

## 🏗️ Project Structure
```
.
├── proto/
│   └── rfcontrol.proto    # Service definition
├── server/
│   ├── server.py          # gRPC server
│   └── rfcontrol_pb2*.py  # Generated code
└── client/
    ├── client.py          # CLI interface
    └── rfcontrol_pb2*.py
```

---

## ⚙️ Core Components

### Protocol Buffer Service
```protobuf
service RFController {
  rpc SetRFSettings(RFConfig) returns (RFResponse);
}

message RFConfig {
  double frequency = 1;  // Hz
  double gain = 2;       // dB
  string device_id = 3;
}
```

### Mock UHD Implementation
```python
# server/server.py
def _set_rf_params(freq, gain):
    """Simulates hardware with 200ms delay"""
    time.sleep(0.2)
    if freq <= 0:
        raise ValueError("Frequency must be positive")
    return f"Set {freq/1e6:.2f} MHz at {gain} dB"
```

---

## 💻 Usage Examples

### Valid Configuration
```bash
python client.py --frequency 3.5e9 --gain 25 --device-id bs1
```
**Output**:
```
✅ Success: Configured bs1 at 3500.00 MHz (25 dB)
```

### Error Case
```bash
python client.py --frequency -1 --gain 10
```
**Output**:
```
❌ Error: Frequency must be positive
```

---

## 🛠️ Development

### Future Enhancements
1. [ ] Docker containerization
2. [ ] Real UHD hardware support
3. [ ] Web interface

### Testing
```bash
# Validate proto file syntax
protoc --proto_path=proto --validate_out=lang=python:. proto/rfcontrol.proto
```

---

## 📜 License
MIT License © 2023 - See [LICENSE](LICENSE) for details.

---

> **Pro Tip**: Use `--device-id` to manage multiple virtual radios simultaneously!
```