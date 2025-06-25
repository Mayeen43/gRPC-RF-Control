#!/usr/bin/env python3
"""
RF Control gRPC Server
Implements RF device control via gRPC with VISA API integration
"""

import grpc
from concurrent import futures
import threading
import time
import logging
import json
from datetime import datetime
from typing import Dict, Optional

# Generated gRPC modules (will be created by protoc)
try:
    import rfcontrol_pb2
    import rfcontrol_pb2_grpc
except ImportError:
    print("Error: gRPC generated files not found. Run 'make generate' first.")
    exit(1)

# VISA/Hardware integration
try:
    import pyvisa
    VISA_AVAILABLE = True
    print("✓ PyVISA available - real hardware control enabled")
except ImportError:
    VISA_AVAILABLE = False
    print("⚠ PyVISA not available - using mock mode")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MockRFDevice:
    """Mock RF device for testing when no hardware is available"""

    def __init__(self, device_id: str):
        self.device_id = device_id
        self.connected = False
        self.config = {
            'frequency': 1e9,  # 1 GHz
            'gain': 0.0,       # 0 dB
            'power': -10.0,    # -10 dBm
            'mode': 'RX'
        }
        self.manufacturer = "Mock Instruments"
        self.model = "RF-MOCK-001"
        self.serial_number = f"MOCK{device_id}001"
        self.firmware_version = "1.0.0"
        self.capabilities = ["FREQUENCY", "GAIN", "POWER", "TX", "RX"]

    def connect(self):
        """Simulate device connection"""
        logger.info(f"Connecting to mock device {self.device_id}")
        time.sleep(0.1)  # Simulate connection time
        self.connected = True
        return True

    def disconnect(self):
        """Simulate device disconnection"""
        logger.info(f"Disconnecting from mock device {self.device_id}")
        self.connected = False

    def query_idn(self):
        """Simulate *IDN? query"""
        if not self.connected:
            raise Exception("Device not connected")
        return f"{self.manufacturer},{self.model},{self.serial_number},{self.firmware_version}"

    def set_frequency(self, freq: float):
        """Simulate frequency setting"""
        if not self.connected:
            raise Exception("Device not connected")

        # Validate frequency range (mock: 100 MHz to 6 GHz)
        if freq < 100e6 or freq > 6e9:
            raise ValueError(f"Frequency {freq/1e6:.2f} MHz out of range (100-6000 MHz)")

        self.config['frequency'] = freq
        logger.info(f"Mock device {self.device_id}: Set frequency to {freq/1e6:.2f} MHz")

    def set_gain(self, gain: float):
        """Simulate gain setting"""
        if not self.connected:
            raise Exception("Device not connected")

        # Validate gain range (mock: -20 to +40 dB)
        if gain < -20 or gain > 40:
            raise ValueError(f"Gain {gain} dB out of range (-20 to +40 dB)")

        self.config['gain'] = gain
        logger.info(f"Mock device {self.device_id}: Set gain to {gain} dB")

    def set_power(self, power: float):
        """Simulate power setting"""
        if not self.connected:
            raise Exception("Device not connected")

        # Validate power range (mock: -30 to +20 dBm)
        if power < -30 or power > 20:
            raise ValueError(f"Power {power} dBm out of range (-30 to +20 dBm)")

        self.config['power'] = power
        logger.info(f"Mock device {self.device_id}: Set power to {power} dBm")

    def set_mode(self, mode: str):
        """Simulate mode setting"""
        if not self.connected:
            raise Exception("Device not connected")

        if mode not in ['TX', 'RX']:
            raise ValueError(f"Invalid mode '{mode}'. Must be 'TX' or 'RX'")

        self.config['mode'] = mode
        logger.info(f"Mock device {self.device_id}: Set mode to {mode}")

    def get_status(self):
        """Get device status"""
        if not self.connected:
            return "DISCONNECTED"
        return "CONNECTED"

class RealRFDevice:
    """Real RF device using VISA"""

    def __init__(self, device_id: str):
        self.device_id = device_id
        self.instrument = None
        self.rm = None
        self.config = {
            'frequency': 1e9,
            'gain': 0.0,
            'power': -10.0,
            'mode': 'RX'
        }

    def connect(self):
        """Connect to real VISA device"""
        try:
            self.rm = pyvisa.ResourceManager()
            self.instrument = self.rm.open_resource(self.device_id)
            logger.info(f"Connected to real device {self.device_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to device {self.device_id}: {e}")
            return False

    def disconnect(self):
        """Disconnect from VISA device"""
        if self.instrument:
            self.instrument.close()
        if self.rm:
            self.rm.close()
        logger.info(f"Disconnected from device {self.device_id}")

    def query_idn(self):
        """Query device identification"""
        if not self.instrument:
            raise Exception("Device not connected")
        return self.instrument.query("*IDN?").strip()

    def set_frequency(self, freq: float):
        """Set RF frequency"""
        if not self.instrument:
            raise Exception("Device not connected")

        # Example SCPI command (adjust for your specific instrument)
        self.instrument.write(f"FREQ {freq}")
        self.config['frequency'] = freq
        logger.info(f"Set frequency to {freq/1e6:.2f} MHz")

    def set_gain(self, gain: float):
        """Set RF gain"""
        if not self.instrument:
            raise Exception("Device not connected")

        # Example SCPI command (adjust for your specific instrument)
        self.instrument.write(f"GAIN {gain}")
        self.config['gain'] = gain
        logger.info(f"Set gain to {gain} dB")

    def set_power(self, power: float):
        """Set RF power"""
        if not self.instrument:
            raise Exception("Device not connected")

        # Example SCPI command (adjust for your specific instrument)
        self.instrument.write(f"POW {power}")
        self.config['power'] = power
        logger.info(f"Set power to {power} dBm")

    def set_mode(self, mode: str):
        """Set operating mode"""
        if not self.instrument:
            raise Exception("Device not connected")

        # Example SCPI command (adjust for your specific instrument)
        self.instrument.write(f"MODE {mode}")
        self.config['mode'] = mode
        logger.info(f"Set mode to {mode}")

    def get_status(self):
        """Get device status"""
        if not self.instrument:
            return "DISCONNECTED"
        try:
            # Example status query (adjust for your specific instrument)
            status = self.instrument.query("STAT?").strip()
            return status
        except:
            return "ERROR"

class RFControlServicer(rfcontrol_pb2_grpc.RFControlServiceServicer):
    """gRPC service implementation for RF control"""

    def __init__(self):
        self.devices: Dict[str, object] = {}
        self.lock = threading.Lock()

    def _get_or_create_device(self, device_id: str):
        """Get existing device or create new one"""
        with self.lock:
            if device_id not in self.devices:
                if VISA_AVAILABLE:
                    # Try to create real device first
                    device = RealRFDevice(device_id)
                    if device.connect():
                        self.devices[device_id] = device
                    else:
                        # Fall back to mock device
                        logger.warning(f"Failed to connect to real device {device_id}, using mock")
                        device = MockRFDevice(device_id)
                        device.connect()
                        self.devices[device_id] = device
                else:
                    # Use mock device
                    device = MockRFDevice(device_id)
                    device.connect()
                    self.devices[device_id] = device

            return self.devices[device_id]

    def SetRFSettings(self, request, context):
        """Set RF device parameters"""
        try:
            logger.info(f"SetRFSettings called for device {request.device_id}")

            # Get or create device
            device = self._get_or_create_device(request.device_id)

            # Apply settings
            if request.frequency > 0:
                device.set_frequency(request.frequency)

            if request.gain != 0:  # Allow negative gain
                device.set_gain(request.gain)

            if request.power != 0:  # Allow negative power
                device.set_power(request.power)

            if request.mode:
                device.set_mode(request.mode.upper())

            # Create response
            current_config = rfcontrol_pb2.RFConfig(
                device_id=request.device_id,
                frequency=device.config['frequency'],
                gain=device.config['gain'],
                power=device.config['power'],
                mode=device.config['mode']
            )

            response = rfcontrol_pb2.RFResponse(
                success=True,
                message="RF settings applied successfully",
                device_status=device.get_status(),
                current_config=current_config,
                timestamp=int(time.time())
            )

            logger.info(f"SetRFSettings completed successfully for device {request.device_id}")
            return response

        except Exception as e:
            logger.error(f"SetRFSettings failed: {e}")
            return rfcontrol_pb2.RFResponse(
                success=False,
                message=f"Error: {str(e)}",
                device_status="ERROR",
                timestamp=int(time.time())
            )

    def GetDeviceStatus(self, request, context):
        """Get device status"""
        try:
            logger.info(f"GetDeviceStatus called for device {request.device_id}")

            device = self._get_or_create_device(request.device_id)

            current_config = rfcontrol_pb2.RFConfig(
                device_id=request.device_id,
                frequency=device.config['frequency'],
                gain=device.config['gain'],
                power=device.config['power'],
                mode=device.config['mode']
            )

            response = rfcontrol_pb2.RFResponse(
                success=True,
                message="Device status retrieved successfully",
                device_status=device.get_status(),
                current_config=current_config,
                timestamp=int(time.time())
            )

            return response

        except Exception as e:
            logger.error(f"GetDeviceStatus failed: {e}")
            return rfcontrol_pb2.RFResponse(
                success=False,
                message=f"Error: {str(e)}",
                device_status="ERROR",
                timestamp=int(time.time())
            )

    def GetDeviceInfo(self, request, context):
        """Get device information"""
        try:
            logger.info(f"GetDeviceInfo called for device {request.device_id}")

            device = self._get_or_create_device(request.device_id)

            if hasattr(device, 'query_idn'):
                idn = device.query_idn()
                parts = idn.split(',')
                manufacturer = parts[0] if len(parts) > 0 else "Unknown"
                model = parts[1] if len(parts) > 1 else "Unknown"
                serial = parts[2] if len(parts) > 2 else "Unknown"
                firmware = parts[3] if len(parts) > 3 else "Unknown"
            else:
                manufacturer = "Unknown"
                model = "Unknown"
                serial = "Unknown"
                firmware = "Unknown"

            capabilities = getattr(device, 'capabilities', [])

            response = rfcontrol_pb2.DeviceInfoResponse(
                success=True,
                device_id=request.device_id,
                manufacturer=manufacturer,
                model=model,
                serial_number=serial,
                firmware_version=firmware,
                capabilities=capabilities
            )

            return response

        except Exception as e:
            logger.error(f"GetDeviceInfo failed: {e}")
            return rfcontrol_pb2.DeviceInfoResponse(
                success=False,
                device_id=request.device_id,
                manufacturer="Error",
                model=str(e),
                serial_number="",
                firmware_version="",
                capabilities=[]
            )

def serve():
    """Start the gRPC server"""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    rfcontrol_pb2_grpc.add_RFControlServiceServicer_to_server(
        RFControlServicer(), server
    )

    listen_addr = '[::]:50051'
    server.add_insecure_port(listen_addr)

    logger.info(f"Starting RF Control gRPC server on {listen_addr}")
    logger.info(f"VISA available: {VISA_AVAILABLE}")

    server.start()
    logger.info("Server started successfully")

    try:
        while True:
            time.sleep(86400)  # Sleep for a day
    except KeyboardInterrupt:
        logger.info("Shutting down server...")
        server.stop(0)

if __name__ == '__main__':
    serve()