#!/usr/bin/env python3
"""
Simple test script to demonstrate RF Control system functionality
"""

import subprocess
import time
import threading
import sys
import os

def run_server():
    """Run the gRPC server in a separate process"""
    try:
        # Generate gRPC files first
        subprocess.run([
            sys.executable, '-m', 'grpc_tools.protoc', 
            '-I.', '--python_out=.', '--grpc_python_out=.', 
            'rfcontrol.proto'
        ], check=True)

        # Start server
        subprocess.run([sys.executable, 'server.py'], check=True)
    except KeyboardInterrupt:
        print("Server stopped")
    except Exception as e:
        print(f"Server error: {e}")

def test_client():
    """Test client functionality"""
    print("\n=== RF Control System Test ===\n")

    # Wait for server to start
    print("Waiting for server to start...")
    time.sleep(3)

    # Test commands
    test_commands = [
        # Test device info
        [sys.executable, 'client.py', '--device', 'TEST001', '--action', 'info'],

        # Test setting RF parameters
        [sys.executable, 'client.py', '--device', 'TEST001', 
         '--frequency', '2400', '--gain', '15', '--power', '10', '--mode', 'TX'],

        # Test getting status
        [sys.executable, 'client.py', '--device', 'TEST001', '--action', 'status'],

        # Test different device
        [sys.executable, 'client.py', '--device', 'TEST002', 
         '--frequency', '5800', '--gain', '20', '--power', '5', '--mode', 'RX'],
    ]

    for i, cmd in enumerate(test_commands, 1):
        print(f"\n--- Test {i}: {' '.join(cmd[2:])} ---")
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            print(result.stdout)
            if result.stderr:
                print(f"Error: {result.stderr}")
        except subprocess.TimeoutExpired:
            print("Command timed out")
        except Exception as e:
            print(f"Command failed: {e}")

        time.sleep(1)

    print("\n=== Test Complete ===")

def main():
    """Main test function"""
    print("RF Control System Test")
    print("This will start the server and run some test commands")
    print("Press Ctrl+C to stop\n")

    # Start server in background thread
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()

    try:
        # Run client tests
        test_client()
    except KeyboardInterrupt:
        print("\nTest interrupted")

    print("\nTest finished. Server may still be running in background.")

if __name__ == '__main__':
    main()
