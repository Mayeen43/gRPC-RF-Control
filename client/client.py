#!/usr/bin/env python3
"""
RF Control gRPC Client
Interactive CLI for controlling RF devices via gRPC
"""

import grpc
import sys
import argparse
from typing import Optional
import json

# Generated gRPC modules (will be created by protoc)
try:
    import rfcontrol_pb2
    import rfcontrol_pb2_grpc
except ImportError:
    print("Error: gRPC generated files not found. Run 'make generate' first.")
    sys.exit(1)

class RFControlClient:
    """gRPC client for RF device control"""

    def __init__(self, server_address: str = 'localhost:50051'):
        """Initialize the client"""
        self.server_address = server_address
        self.channel = None
        self.stub = None

    def connect(self):
        """Connect to the gRPC server"""
        try:
            self.channel = grpc.insecure_channel(self.server_address)
            self.stub = rfcontrol_pb2_grpc.RFControlServiceStub(self.channel)

            # Test connection
            grpc.channel_ready_future(self.channel).result(timeout=5)
            print(f"✓ Connected to RF Control server at {self.server_address}")
            return True

        except grpc.FutureTimeoutError:
            print(f"✗ Failed to connect to server at {self.server_address} (timeout)")
            return False
        except Exception as e:
            print(f"✗ Connection failed: {e}")
            return False

    def disconnect(self):
        """Disconnect from the server"""
        if self.channel:
            self.channel.close()
            print("Disconnected from server")

    def set_rf_settings(self, device_id: str, frequency: Optional[float] = None,
                       gain: Optional[float] = None, power: Optional[float] = None,
                       mode: Optional[str] = None):
        """Set RF device parameters"""
        try:
            request = rfcontrol_pb2.RFConfig(
                device_id=device_id,
                frequency=frequency or 0,
                gain=gain if gain is not None else 0,
                power=power if power is not None else 0,
                mode=mode or ""
            )

            response = self.stub.SetRFSettings(request)

            if response.success:
                print("✓ RF settings applied successfully")
                print(f"  Message: {response.message}")
                print(f"  Device Status: {response.device_status}")
                print("  Current Configuration:")
                print(f"    Device ID: {response.current_config.device_id}")
                print(f"    Frequency: {response.current_config.frequency/1e6:.2f} MHz")
                print(f"    Gain: {response.current_config.gain} dB")
                print(f"    Power: {response.current_config.power} dBm")
                print(f"    Mode: {response.current_config.mode}")
            else:
                print(f"✗ Failed to set RF settings: {response.message}")

            return response.success

        except grpc.RpcError as e:
            print(f"✗ gRPC error: {e.details()}")
            return False
        except Exception as e:
            print(f"✗ Error: {e}")
            return False

    def get_device_status(self, device_id: str):
        """Get device status"""
        try:
            request = rfcontrol_pb2.DeviceRequest(device_id=device_id)
            response = self.stub.GetDeviceStatus(request)

            if response.success:
                print("✓ Device status retrieved successfully")
                print(f"  Device Status: {response.device_status}")
                print("  Current Configuration:")
                print(f"    Device ID: {response.current_config.device_id}")
                print(f"    Frequency: {response.current_config.frequency/1e6:.2f} MHz")
                print(f"    Gain: {response.current_config.gain} dB")
                print(f"    Power: {response.current_config.power} dBm")
                print(f"    Mode: {response.current_config.mode}")
            else:
                print(f"✗ Failed to get device status: {response.message}")

            return response.success

        except grpc.RpcError as e:
            print(f"✗ gRPC error: {e.details()}")
            return False
        except Exception as e:
            print(f"✗ Error: {e}")
            return False

    def get_device_info(self, device_id: str):
        """Get device information"""
        try:
            request = rfcontrol_pb2.DeviceRequest(device_id=device_id)
            response = self.stub.GetDeviceInfo(request)

            if response.success:
                print("✓ Device information retrieved successfully")
                print(f"  Device ID: {response.device_id}")
                print(f"  Manufacturer: {response.manufacturer}")
                print(f"  Model: {response.model}")
                print(f"  Serial Number: {response.serial_number}")
                print(f"  Firmware Version: {response.firmware_version}")
                print(f"  Capabilities: {', '.join(response.capabilities)}")
            else:
                print(f"✗ Failed to get device info: Device error")

            return response.success

        except grpc.RpcError as e:
            print(f"✗ gRPC error: {e.details()}")
            return False
        except Exception as e:
            print(f"✗ Error: {e}")
            return False

def interactive_mode(client: RFControlClient):
    """Interactive CLI mode"""
    print("\n=== RF Control Interactive Mode ===")
    print("Commands:")
    print("  set <device_id> - Set RF parameters for device")
    print("  status <device_id> - Get device status")
    print("  info <device_id> - Get device information")
    print("  help - Show this help")
    print("  quit - Exit")
    print()

    while True:
        try:
            command = input("rf-control> ").strip().lower()

            if command == "quit" or command == "exit":
                break
            elif command == "help":
                print("Commands:")
                print("  set <device_id> - Set RF parameters for device")
                print("  status <device_id> - Get device status")
                print("  info <device_id> - Get device information")
                print("  help - Show this help")
                print("  quit - Exit")
            elif command.startswith("set "):
                parts = command.split()
                if len(parts) < 2:
                    print("Usage: set <device_id>")
                    continue

                device_id = parts[1]

                # Get RF parameters interactively
                print(f"\nSetting RF parameters for device: {device_id}")

                freq_input = input("Frequency (MHz, press Enter to skip): ").strip()
                frequency = float(freq_input) * 1e6 if freq_input else None

                gain_input = input("Gain (dB, press Enter to skip): ").strip()
                gain = float(gain_input) if gain_input else None

                power_input = input("Power (dBm, press Enter to skip): ").strip()
                power = float(power_input) if power_input else None

                mode_input = input("Mode (TX/RX, press Enter to skip): ").strip().upper()
                mode = mode_input if mode_input in ['TX', 'RX'] else None

                print()
                client.set_rf_settings(device_id, frequency, gain, power, mode)

            elif command.startswith("status "):
                parts = command.split()
                if len(parts) < 2:
                    print("Usage: status <device_id>")
                    continue

                device_id = parts[1]
                client.get_device_status(device_id)

            elif command.startswith("info "):
                parts = command.split()
                if len(parts) < 2:
                    print("Usage: info <device_id>")
                    continue

                device_id = parts[1]
                client.get_device_info(device_id)

            elif command == "":
                continue
            else:
                print(f"Unknown command: {command}")
                print("Type 'help' for available commands")

            print()

        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except EOFError:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='RF Control gRPC Client')
    parser.add_argument('--server', default='localhost:50051',
                       help='Server address (default: localhost:50051)')
    parser.add_argument('--device', help='Device ID')
    parser.add_argument('--frequency', type=float, help='Frequency in MHz')
    parser.add_argument('--gain', type=float, help='Gain in dB')
    parser.add_argument('--power', type=float, help='Power in dBm')
    parser.add_argument('--mode', choices=['TX', 'RX'], help='Operating mode')
    parser.add_argument('--action', choices=['set', 'status', 'info'],
                       default='set', help='Action to perform')
    parser.add_argument('--interactive', '-i', action='store_true',
                       help='Start interactive mode')

    args = parser.parse_args()

    # Create client
    client = RFControlClient(args.server)

    # Connect to server
    if not client.connect():
        return 1

    try:
        if args.interactive:
            interactive_mode(client)
        else:
            if not args.device:
                print("Error: Device ID is required in non-interactive mode")
                return 1

            if args.action == 'set':
                frequency = args.frequency * 1e6 if args.frequency else None
                success = client.set_rf_settings(
                    args.device, frequency, args.gain, args.power, args.mode
                )
                return 0 if success else 1

            elif args.action == 'status':
                success = client.get_device_status(args.device)
                return 0 if success else 1

            elif args.action == 'info':
                success = client.get_device_info(args.device)
                return 0 if success else 1

    finally:
        client.disconnect()

    return 0

if __name__ == '__main__':
    sys.exit(main())