# gRPC-RF-Control
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
| **Server** | `cd server && python server.py` | `INFO:root:Server started on port 50051` |
| **Client** | `cd client && python client.py --frequency 2.4e9 --gain 20` | Sending request: frequency: 2.4e+09
gain: 20
device_id: "usrp1" |

---

## 🏗️ Project Structure
```
.
├── proto/
    ├── rfcontrol.proto    # Service definition
    └── rfcontrol_pb2*.py  # Generated code
    └── rfcontrol_pb2_grpc*.py  # Generated code
├── server/
    ├── server.py          # gRPC server
    └── rfcontrol_pb2*.py  # Generated code
    └── rfcontrol_pb2_grpc*.py  # Generated code
├── client/
    ├── client.py          # CLI interface
    └── rfcontrol_pb2*.py
    └── rfcontrol_pb2_grpc*.py  # Generated code
└── README.md
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
def _mock_uhd_set_rf(self, frequency, gain, device_id):
        """Mock UHD implementation for testing without hardware"""
        # Simulate hardware delay
        time.sleep(0.2) 
        
        # Validate inputs
        if frequency <= 0:
            return False, "Frequency must be positive"
        if not (-20 <= gain <= 30):
            return False, "Gain must be between -20 and 30 dB"
        
        # Update mock device state
        self.device_state.update({
            "frequency": frequency,
            "gain": gain,
            "device_id": device_id,
            "status": "configured"
        })
```

---

## 💻 Usage Examples

### Valid Configuration
```bash
python client.py --frequency 3.5e9 --gain 25 --device-id bs1
```
**Output**:
```
Sending request: frequency: 2.4e+09
gain: 20
device_id: "usrp1"
```
```bash

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
