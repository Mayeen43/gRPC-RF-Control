#!/usr/bin/env python3
"""
RF API Comparison: VISA vs UHD
Shows how to integrate both VISA and UHD APIs in the RF Control System
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Optional, Any

logger = logging.getLogger(__name__)

class RFDeviceInterface(ABC):
    """Abstract interface for RF devices"""

    @abstractmethod
    def connect(self) -> bool:
        """Connect to the device"""
        pass

    @abstractmethod
    def disconnect(self):
        """Disconnect from the device"""  
        pass

    @abstractmethod
    def set_frequency(self, freq: float):
        """Set RF frequency in Hz"""
        pass

    @abstractmethod
    def set_gain(self, gain: float):
        """Set RF gain in dB"""
        pass

    @abstractmethod
    def get_status(self) -> str:
        """Get device status"""
        pass

    @abstractmethod
    def get_device_info(self) -> Dict[str, Any]:
        """Get device information"""
        pass

class VISARFDevice(RFDeviceInterface):
    """VISA-based RF device implementation"""

    def __init__(self, resource_string: str):
        self.resource_string = resource_string
        self.instrument = None
        self.rm = None
        self.config = {'frequency': 1e9, 'gain': 0.0}

    def connect(self) -> bool:
        try:
            import pyvisa
            self.rm = pyvisa.ResourceManager()
            self.instrument = self.rm.open_resource(self.resource_string)
            logger.info(f"Connected to VISA device: {self.resource_string}")
            return True
        except Exception as e:
            logger.error(f"VISA connection failed: {e}")
            return False

    def disconnect(self):
        if self.instrument:
            self.instrument.close()
        if self.rm:
            self.rm.close()
        logger.info("VISA device disconnected")

    def set_frequency(self, freq: float):
        if not self.instrument:
            raise Exception("Device not connected")
        self.instrument.write(f"FREQ {freq}")
        self.config['frequency'] = freq
        logger.info(f"VISA: Set frequency to {freq/1e6:.2f} MHz")

    def set_gain(self, gain: float):
        if not self.instrument:
            raise Exception("Device not connected")
        self.instrument.write(f"GAIN {gain}")
        self.config['gain'] = gain
        logger.info(f"VISA: Set gain to {gain} dB")

    def get_status(self) -> str:
        if not self.instrument:
            return "DISCONNECTED"
        try:
            return self.instrument.query("STAT?").strip()
        except:
            return "ERROR"

    def get_device_info(self) -> Dict[str, Any]:
        if not self.instrument:
            raise Exception("Device not connected")

        idn = self.instrument.query("*IDN?").strip()
        parts = idn.split(',')

        return {
            'type': 'VISA',
            'resource': self.resource_string,
            'manufacturer': parts[0] if len(parts) > 0 else 'Unknown',
            'model': parts[1] if len(parts) > 1 else 'Unknown',
            'serial': parts[2] if len(parts) > 2 else 'Unknown',
            'firmware': parts[3] if len(parts) > 3 else 'Unknown'
        }

class UHDRFDevice(RFDeviceInterface):
    """UHD-based RF device implementation"""

    def __init__(self, device_args: str = ""):
        self.device_args = device_args
        self.usrp = None
        self.config = {'frequency': 1e9, 'gain': 0.0}

    def connect(self) -> bool:
        try:
            import uhd
            self.usrp = uhd.usrp.MultiUSRP(self.device_args)
            logger.info(f"Connected to USRP: {self.device_args}")
            return True
        except Exception as e:
            logger.error(f"UHD connection failed: {e}")
            return False

    def disconnect(self):
        self.usrp = None
        logger.info("UHD device disconnected")

    def set_frequency(self, freq: float):
        if not self.usrp:
            raise Exception("Device not connected")

        import uhd
        tune_req = uhd.types.TuneRequest(freq)
        result = self.usrp.set_rx_freq(tune_req, 0)
        self.config['frequency'] = result.actual_rf_freq
        logger.info(f"UHD: Set frequency to {result.actual_rf_freq/1e6:.2f} MHz")

    def set_gain(self, gain: float):
        if not self.usrp:
            raise Exception("Device not connected")

        self.usrp.set_rx_gain(gain, 0)
        actual_gain = self.usrp.get_rx_gain(0)
        self.config['gain'] = actual_gain
        logger.info(f"UHD: Set gain to {actual_gain} dB")

    def get_status(self) -> str:
        if not self.usrp:
            return "DISCONNECTED"
        try:
            self.usrp.get_mboard_name()
            return "CONNECTED"
        except:
            return "ERROR"

    def get_device_info(self) -> Dict[str, Any]:
        if not self.usrp:
            raise Exception("Device not connected")

        return {
            'type': 'UHD',
            'device_args': self.device_args,
            'mboard_name': self.usrp.get_mboard_name(),
            'pp_string': self.usrp.get_pp_string()
        }

class RFDeviceFactory:
    """Factory for creating RF devices based on identifier"""

    @staticmethod
    def create_device(device_id: str) -> RFDeviceInterface:
        """
        Create appropriate RF device based on identifier

        Examples:
        - "VISA:USB0::0x1234::0x5678::SERIAL::INSTR" -> VISA device
        - "UHD:type=b200" -> UHD device  
        - "UHD:addr=192.168.10.2" -> Network UHD device
        """

        if device_id.startswith("VISA:"):
            resource_string = device_id[5:]  # Remove "VISA:" prefix
            return VISARFDevice(resource_string)

        elif device_id.startswith("UHD:"):
            device_args = device_id[4:]  # Remove "UHD:" prefix
            return UHDRFDevice(device_args)

        else:
            # Default to mock device for testing
            from server import MockRFDevice
            return MockRFDevice(device_id)

# Example usage in gRPC server
def enhanced_get_or_create_device(device_id: str) -> RFDeviceInterface:
    """Enhanced device creation with API selection"""

    try:
        device = RFDeviceFactory.create_device(device_id)

        if device.connect():
            logger.info(f"Successfully connected to {device_id}")
            return device
        else:
            logger.warning(f"Failed to connect to {device_id}")
            # Fallback to mock device
            from server import MockRFDevice
            mock_device = MockRFDevice(device_id)
            mock_device.connect()
            return mock_device

    except Exception as e:
        logger.error(f"Device creation failed for {device_id}: {e}")
        # Fallback to mock device
        from server import MockRFDevice
        mock_device = MockRFDevice(device_id)
        mock_device.connect()
        return mock_device

def main():
    """Demonstrate both APIs"""
    print("RF API Comparison Demo")
    print("=====================")

    # Test device identifiers
    test_devices = [
        "MOCK001",  # Mock device
        "VISA:USB0::0x1234::0x5678::SERIAL::INSTR",  # VISA device
        "UHD:type=b200",  # UHD B200 device
        "UHD:addr=192.168.10.2"  # Network UHD device
    ]

    for device_id in test_devices:
        print(f"\nTesting device: {device_id}")
        try:
            device = RFDeviceFactory.create_device(device_id)
            print(f"Created device type: {type(device).__name__}")

            if device.connect():
                info = device.get_device_info()
                print(f"Device info: {info}")

                # Test basic operations
                device.set_frequency(2.4e9)
                device.set_gain(20)
                status = device.get_status()
                print(f"Status: {status}")

                device.disconnect()
            else:
                print("Connection failed")

        except Exception as e:
            print(f"Error: {e}")

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
