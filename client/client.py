import grpc
import rf_settings_pb2
import rf_settings_pb2_grpc
import argparse

def run():
    channel = grpc.insecure_channel('localhost:50051')
    stub = rf_settings_pb2_grpc.RFSettingsServiceStub(channel)
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--test', action='store_true', help='Run test configuration')
    args = parser.parse_args()
    
    if args.test:
        # Automated test
        response = stub.SetRFSettings(rf_settings_pb2.RFConfig(
            frequency=100.0,
            gain=20.0,
            device_id="TCPIP0::localhost::INSTR"
        ))
        print(f"Test Response: {response.status}")
    else:
        # Interactive mode
        while True:
            print("\nRF Settings Configuration")
            print("1. Set RF Parameters")
            print("2. Exit")
            choice = input("Select option: ")
            
            if choice == '2':
                break
                
            if choice == '1':
                try:
                    device_id = input("Device ID (e.g., 'TCPIP0::localhost::INSTR'): ")
                    frequency = float(input("Frequency (MHz): "))
                    gain = float(input("Gain (dB): "))
                    
                    response = stub.SetRFSettings(rf_settings_pb2.RFConfig(
                        frequency=frequency,
                        gain=gain,
                        device_id=device_id
                    ))
                    
                    print(f"\nStatus: {response.status}")
                    print(f"Success: {'Yes' if response.success else 'No'}")
                except Exception as e:
                    print(f"Error: {e}")

if __name__ == '__main__':
    run()