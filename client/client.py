import grpc
import rfcontrol_pb2
import rfcontrol_pb2_grpc

def run():
    channel = grpc.insecure_channel('localhost:50051')
    stub = rfcontrol_pb2_grpc.RFSettingsServiceStub(channel)


    
    
    response = stub.SetRFSettings(rfcontrol_pb2.RFConfig(
        frequency=2.4e9,
        gain=20.0,
        device_id="usrp1"
    ))
    
    print(f"Response: {response.success}, {response.status}, {response.device_id}")

if __name__ == '__main__':
    run()