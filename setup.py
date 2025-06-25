#!/usr/bin/env python3
"""
Setup script for RF Control System
"""

import subprocess
import sys
import os

def run_command(cmd, description):
    """Run a command and print results"""
    print(f"\n{description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, 
                              capture_output=True, text=True)
        print(f"✓ {description} completed successfully")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed:")
        print(e.stderr)
        return False

def main():
    """Main setup function"""
    print("=== RF Control System Setup ===\n")

    # Check Python version
    if sys.version_info < (3, 8):
        print("✗ Python 3.8 or higher is required")
        return 1

    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor} detected")

    # Install requirements
    if not run_command("pip install -r requirements.txt", "Installing Python dependencies"):
        return 1

    # Generate gRPC files
    if not run_command(
        "python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. rfcontrol.proto",
        "Generating gRPC Python files"
    ):
        return 1

    # Check if files were created
    required_files = ['rfcontrol_pb2.py', 'rfcontrol_pb2_grpc.py']
    for file in required_files:
        if os.path.exists(file):
            print(f"✓ Generated {file}")
        else:
            print(f"✗ Failed to generate {file}")
            return 1

    print("\n=== Setup Complete! ===")
    print("\nNext steps:")
    print("1. Start the server: python server.py")
    print("2. In another terminal, run the client: python client.py --interactive")
    print("3. Or run the test: python test_system.py")
    print("\nFor Docker deployment: docker-compose up --build")

    return 0

if __name__ == '__main__':
    sys.exit(main())
