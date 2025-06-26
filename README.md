# RF Device gRPC Control System

This project implements a client-server system for controlling an RF device via gRPC, using either VISA (PyVISA) or UHD APIs for hardware integration. The system supports both real hardware and mock operation for environments without RF instruments.

## Table of Contents

- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Setup Instructions](#setup-instructions)
  - [1. Clone the Repository](#1-clone-the-repository)
  - [2. Install Dependencies](#2-install-dependencies)
  - [3. Generate gRPC Code](#3-generate-grpc-code)
  - [4. Run the Server](#4-run-the-server)
  - [5. Run the Client](#5-run-the-client)
- [Docker Usage](#docker-usage)
- [VISA/UHD API Integration](#visa-uhd-api-integration)
- [Mocking (No Hardware)](#mocking-no-hardware)
- [Sample Session](#sample-session)
- [Troubleshooting](#troubleshooting)

## Project Structure

```
repo-root/
├── proto/
│   └── rfcontrol.proto          # gRPC service and message definitions
├── server/
│   └── server.py                # gRPC server and VISA/UHD integration
├── client/
│   └── client.py                # CLI/interactive gRPC client
├── Dockerfile                   # (Optional) Containerizes the server
└── README.md                    # This file
```

## Prerequisites

- Python 3.8+
- pip
- [gRPC tools for Python](https://grpc.io/docs/languages/python/quickstart/)
- For VISA integration: [PyVISA](https://pyvisa.readthedocs.io/en/latest/)
- For UHD integration: [UHD Python API](https://github.com/EttusResearch/uhd)
- (Optional) Docker (for containerized server)
- (Optional) RF hardware, or use mock mode

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
   docker compose version
   ```
   

> **Note:** Docker cannot be implemented as I was unable to start docker enginein my windows environment.

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

## Troubleshooting

- **gRPC import errors:** Ensure you generated the Python modules from `.proto` and installed `grpcio` and `grpcio-tools`.
- **VISA/UHD errors:** Check that hardware is connected and drivers are installed. Otherwise, use mock mode.
- **Docker issues:** If `docker-compose` is not recognized, use `docker compose` (with a space) instead of `docker-compose` (with a hyphen).
# RF Device gRPC Control System

This project implements a client-server system for controlling an RF device via gRPC, using either VISA (PyVISA) or UHD APIs for hardware integration. The system supports both real hardware and mock operation for environments without RF instruments.

## Table of Contents

- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Setup Instructions](#setup-instructions)
  - [1. Clone the Repository](#1-clone-the-repository)
  - [2. Install Dependencies](#2-install-dependencies)
  - [3. Generate gRPC Code](#3-generate-grpc-code)
  - [4. Run the Server](#4-run-the-server)
  - [5. Run the Client](#5-run-the-client)
- [Docker Usage](#docker-usage)
- [UHD API Integration](#uhd-api-integration)
- [Mocking (No Hardware)](#mocking-no-hardware)
- [Sample Session](#sample-session)
- [Troubleshooting](#troubleshooting)
- [References](#references)

## Project Structure

```
repo-root/
├── proto/
│   └── rfcontrol.proto          # gRPC service and message definitions
├── server/
│   └── server.py                # gRPC server and VISA/UHD integration
├── client/
│   └── client.py                # CLI/interactive gRPC client
└── README.md                    # This file
```

## Prerequisites

- Python 3.8+
- pip
- [gRPC tools for Python](https://grpc.io/docs/languages/python/quickstart/)
- For VISA integration: [PyVISA](https://pyvisa.readthedocs.io/en/latest/)
- For UHD integration: [UHD Python API](https://github.com/EttusResearch/uhd)
- (Optional) Docker (for containerized server)
- (Optional) RF hardware, or use mock mode

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

## Troubleshooting

- **gRPC import errors:** Ensure you generated the Python modules from `.proto` and installed `grpcio` and `grpcio-tools`.
