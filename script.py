# Create a simple test script
test_content = '''#!/usr/bin/env python3
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
    print("\\n=== RF Control System Test ===\\n")
    
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
        print(f"\\n--- Test {i}: {' '.join(cmd[2:])} ---")
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
    
    print("\\n=== Test Complete ===")

def main():
    """Main test function"""
    print("RF Control System Test")
    print("This will start the server and run some test commands")
    print("Press Ctrl+C to stop\\n")
    
    # Start server in background thread
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    try:
        # Run client tests
        test_client()
    except KeyboardInterrupt:
        print("\\nTest interrupted")
    
    print("\\nTest finished. Server may still be running in background.")

if __name__ == '__main__':
    main()
'''

with open('test_system.py', 'w') as f:
    f.write(test_content)

print("✓ Created test_system.py")

# Create a simple setup script
setup_content = '''#!/usr/bin/env python3
"""
Setup script for RF Control System
"""

import subprocess
import sys
import os

def run_command(cmd, description):
    """Run a command and print results"""
    print(f"\\n{description}...")
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
    print("=== RF Control System Setup ===\\n")
    
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
    
    print("\\n=== Setup Complete! ===")
    print("\\nNext steps:")
    print("1. Start the server: python server.py")
    print("2. In another terminal, run the client: python client.py --interactive")
    print("3. Or run the test: python test_system.py")
    print("\\nFor Docker deployment: docker-compose up --build")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
'''

with open('setup.py', 'w') as f:
    f.write(setup_content)

print("✓ Created setup.py")