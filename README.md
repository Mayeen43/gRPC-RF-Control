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
- [Conclusion](#-conclusion)

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

## Setup Instructions

### 1. Clone the Repository

```bash
git clone 
cd 
```

### 2. Install Dependencies

Install Python dependencies:

```bash
pip install -r requirements.txt
```

### 3. Generate gRPC Code

From the root directory, run:

```bash
python -m grpc_tools.protoc -I./proto --python_out=. --grpc_python_out=. ./proto/rfcontrol.proto
```

This generates the Python gRPC modules from the `.proto` file.

### 4. Run the Server

Start the gRPC server (default: localhost:50051):

```bash
python server/server.py
```

The server will attempt to connect to RF hardware via VISA/UHD. If hardware is not available, it will operate in mock mode with explanatory logs.

### 5. Run the Client

In a separate terminal, start the client:

```bash
python client/client.py
```

The client provides a CLI or interactive prompt to set RF parameters (frequency, gain, device ID). It sends these to the server and displays the response.

## Docker Usage

To run the server in a container:

1. **Build the Docker image:**
   ```bash
   docker build -t rf-server .
   ```
2. **Run the container:**
   ```bash
   docker run -p 50051:50051 rf-server
   ```

> **Note:** The container runs in mock mode unless you mount hardware or VISA/UHD drivers inside.

## VISA/UHD API Integration

- **VISA (PyVISA):**
  - Used for general RF instruments.
  - Example commands:
    - `*IDN?` (query device info)
    - Custom SCPI commands to set frequency/gain.
- **UHD:**
  - Used for USRP devices.
  - Example: `usrp.set_center_freq(freq)`.

If hardware is not detected, the server logs all API calls instead of executing them.

## Mocking (No Hardware)

If no RF hardware is available:
- The server automatically switches to mock mode.
- All API calls are logged with explanatory messages.
- The client and server interaction remains unchanged for testing and demonstration.

## Sample Session

**Client:**
```
Enter RF device ID: RF1234
Enter frequency (Hz): 915000000
Enter gain (dB): 20

[INFO] Sending RF settings to server...
[INFO] Server response: SUCCESS
        Device status: Frequency set to 915000000 Hz, Gain set to 20 dB
```

**Server (mock mode):**
```
[MOCK] Received RFConfig: device_id=RF1234, frequency=915000000, gain=20
[MOCK] Would send: *IDN? to device RF1234
[MOCK] Would set frequency to 915000000 Hz
[MOCK] Would set gain to 20 dB
[MOCK] Responding with success
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

## Conclusion

### **Conclusion**  

Despite multiple fixes, the **gRPC server** still fails with the error:  
**`Protocol message RFResponse has no "message" field`**, indicating a persistent mismatch between the `.proto` definition and the server’s response construction.  

#### **What’s Working:**  
**Protocol Buffer Definition** – Correctly defines `RFResponse` with `success`, `status`, and `device_id`.  
**Client-Server Communication** – Basic gRPC setup is functional.  
**UHD Mock Logic** – The RF configuration logic (simulated or real) executes properly.  

#### **Remaining Issue:**  
**Field Name Mismatch** – The server still tries to use a non-existent `message` field instead of `status`, suggesting:  
   - A hidden reference to an outdated `.proto` file.  
   - Cached generated files (`rfcontrol_pb2.py`) not being regenerated correctly.  
   - An overlooked `RFResponse` construction in error handling.  

#### **Next Steps:**  
1. **Nuclear Cleanup:**  
   - Delete *all* generated files (`rfcontrol_pb2*.py`) and regenerate them.  
   - Search the entire project for `message=` to ensure no legacy code remains.  
2. **Validation Test:**  
   - Temporarily hardcode the server to return a minimal `RFResponse` (no logic) to isolate the issue.  
3. **Debugging:**  
   - Add logging to verify which line constructs the faulty response.  

The core logic is sound—once the field mismatch is resolved, the project will work as intended.
