#!/usr/bin/env python3
"""
Example UHD API integration for RF Control System
This shows how to integrate with USRP devices using the UHD Python API
"""

import logging
from typing import Dict, Optional

# UHD API integration
try:
    import uhd
    UHD_AVAILABLE = True
    print("✓ UHD Python API available - USRP control enabled")
except ImportError:
    UHD_AVAILABLE = False
    print("⚠ UHD Python API not available - install with: pip install uhd")

logger = logging.getLogger(__name__)

class USRPDevice:
    """USRP device control using UHD API"""

    def __init__(self, device_args: str = ""):
        """
        Initialize USRP device
        Args:
            device_args: UHD device arguments (e.g., "type=b200", "addr=192.168.10.2")
        """
        self.device_args = device_args
        self.usrp = None
        self.connected = False
        self.config = {
            'frequency': 1e9,  # 1 GHz
            'gain': 0.0,       # 0 dB
            'power': -10.0,    # -10 dBm (not directly controllable)
            'mode': 'RX'       # RX or TX
        }

    def connect(self):
        """Connect to USRP device"""
        try:
            if not UHD_AVAILABLE:
                raise ImportError("UHD Python API not available")

            self.usrp = uhd.usrp.MultiUSRP(self.device_args)
            self.connected = True

            logger.info(f"Connected to USRP: {self.get_device_info()}")
            return True

        except Exception as e:
            logger.error(f"Failed to connect to USRP: {e}")
            self.connected = False
            return False

    def disconnect(self):
        """Disconnect from USRP device"""
        if self.usrp:
            self.usrp = None
        self.connected = False
        logger.info("Disconnected from USRP")

    def get_device_info(self):
        """Get USRP device information"""
        if not self.connected or not self.usrp:
            raise Exception("Device not connected")

        mboard_name = self.usrp.get_mboard_name()
        pp_string = self.usrp.get_pp_string()

        return {
            'mboard_name': mboard_name,
            'pp_string': pp_string
        }

    def set_frequency(self, freq: float, channel: int = 0):
        """Set center frequency"""
        if not self.connected or not self.usrp:
            raise Exception("Device not connected")

        # Set RX frequency
        tune_req = uhd.types.TuneRequest(freq)
        tune_result = self.usrp.set_rx_freq(tune_req, channel)

        # Set TX frequency  
        tune_result_tx = self.usrp.set_tx_freq(tune_req, channel)

        self.config['frequency'] = freq
        logger.info(f"Set frequency to {freq/1e6:.2f} MHz")
        logger.info(f"RX tune result: {tune_result.actual_rf_freq/1e6:.2f} MHz")
        logger.info(f"TX tune result: {tune_result_tx.actual_rf_freq/1e6:.2f} MHz")

    def set_gain(self, gain: float, channel: int = 0):
        """Set RF gain"""
        if not self.connected or not self.usrp:
            raise Exception("Device not connected")

        if self.config['mode'] == 'RX':
            self.usrp.set_rx_gain(gain, channel)
            actual_gain = self.usrp.get_rx_gain(channel)
        else:  # TX mode
            self.usrp.set_tx_gain(gain, channel)
            actual_gain = self.usrp.get_tx_gain(channel)

        self.config['gain'] = actual_gain
        logger.info(f"Set {self.config['mode']} gain to {actual_gain} dB")

    def set_sample_rate(self, rate: float, channel: int = 0):
        """Set sample rate"""
        if not self.connected or not self.usrp:
            raise Exception("Device not connected")

        self.usrp.set_rx_rate(rate, channel)
        self.usrp.set_tx_rate(rate, channel)

        actual_rx_rate = self.usrp.get_rx_rate(channel)
        actual_tx_rate = self.usrp.get_tx_rate(channel)

        logger.info(f"Set sample rate - RX: {actual_rx_rate/1e6:.2f} MS/s, TX: {actual_tx_rate/1e6:.2f} MS/s")

    def set_antenna(self, antenna: str, channel: int = 0):
        """Set antenna selection"""
        if not self.connected or not self.usrp:
            raise Exception("Device not connected")

        if self.config['mode'] == 'RX':
            self.usrp.set_rx_antenna(antenna, channel)
            actual_antenna = self.usrp.get_rx_antenna(channel)
        else:  # TX mode
            self.usrp.set_tx_antenna(antenna, channel)
            actual_antenna = self.usrp.get_tx_antenna(channel)

        logger.info(f"Set {self.config['mode']} antenna to {actual_antenna}")

    def get_frequency_range(self, channel: int = 0):
        """Get frequency range"""
        if not self.connected or not self.usrp:
            raise Exception("Device not connected")

        if self.config['mode'] == 'RX':
            freq_range = self.usrp.get_rx_freq_range(channel)
        else:
            freq_range = self.usrp.get_tx_freq_range(channel)

        return {
            'min': freq_range.start(),
            'max': freq_range.stop(),
            'step': freq_range.step()
        }

    def get_gain_range(self, channel: int = 0):
        """Get gain range"""
        if not self.connected or not self.usrp:
            raise Exception("Device not connected")

        if self.config['mode'] == 'RX':
            gain_range = self.usrp.get_rx_gain_range(channel)
        else:
            gain_range = self.usrp.get_tx_gain_range(channel)

        return {
            'min': gain_range.start(),
            'max': gain_range.stop(),
            'step': gain_range.step()
        }

    def get_status(self):
        """Get device status"""
        if not self.connected:
            return "DISCONNECTED"

        try:
            # Check if device is responsive
            self.usrp.get_mboard_name()
            return "CONNECTED"
        except:
            return "ERROR"

# Example usage
def main():
    """Example usage of USRP device control"""
    print("USRP Device Control Example")

    if not UHD_AVAILABLE:
        print("UHD Python API not available. Install with:")
        print("pip install uhd")
        return

    # Create USRP device
    # Common device args:
    # - "type=b200" for USRP B200 series
    # - "type=x300" for USRP X300 series  
    # - "addr=192.168.10.2" for network-connected USRPs
    device = USRPDevice("type=b200")

    try:
        # Connect to device
        if not device.connect():
            print("Failed to connect to USRP")
            return

        # Get device information
        info = device.get_device_info()
        print(f"Device: {info['mboard_name']}")

        # Set parameters
        device.set_frequency(2.4e9)  # 2.4 GHz
        device.set_gain(20)          # 20 dB
        device.set_sample_rate(10e6) # 10 MS/s
        device.set_antenna("TX/RX")  # Use TX/RX antenna

        # Get ranges
        freq_range = device.get_frequency_range()
        gain_range = device.get_gain_range()

        print(f"Frequency range: {freq_range['min']/1e6:.0f} - {freq_range['max']/1e6:.0f} MHz")
        print(f"Gain range: {gain_range['min']:.1f} - {gain_range['max']:.1f} dB")

        print("USRP configured successfully!")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        device.disconnect()

if __name__ == '__main__':
    main()
