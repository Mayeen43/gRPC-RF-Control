import grpc
import rfcontrol_pb2
import rfcontrol_pb2_grpc

def run():
    # Create a secure channel (insecure for local testing)
    channel = grpc.insecure_channel('localhost:50051')
    
    try:
        # Create the stub (client)
        stub = rfcontrol_pb2_grpc.RFControllerStub(channel)
        
        # Prepare the request
        request = rfcontrol_pb2.RFConfig(
            frequency=2.4e9,  # 2.4 GHz
            gain=20.0,
            device_id="usrp1"
        )
        
        # Make the RPC call
        print(f"Sending request: {request}")
        response = stub.SetRFSettings(request)
        
        # Handle the response
        print("\nServer response:")
        print(f"Success: {response.success}")
        print(f"Status: {response.status}")
        print(f"Device ID: {response.device_id}")
        
    except grpc.RpcError as e:
        print(f"RPC failed: {e.code()}: {e.details()}")
    finally:
        # Clean up the channel
        channel.close()

if __name__ == '__main__':
    run()