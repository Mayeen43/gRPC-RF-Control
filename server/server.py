import grpc
from concurrent import futures
import rf_settings_pb2
import rf_settings_pb2_grpc
import pyvisa as visa

class RFSettingsServicer(rf_settings_pb2_grpc.RFSettingsServiceServicer):
    def __init__(self):
        self.rm = visa.ResourceManager('@sim')
        self.devices = {}

    def SetRFSettings(self, request, context):
        try:
            if request.device_id not in self.devices:
                self.devices[request.device_id] = self.rm.open_resource(request.device_id)
            
            device = self.devices[request.device_id]
            device.write(f"FREQ {request.frequency} MHz")
            device.write(f"GAIN {request.gain} dB")
            
            return rf_settings_pb2.RFResponse(
                success=True,
                status=f"Frequency: {request.frequency} MHz, Gain: {request.gain} dB",
                device_id=request.device_id
            )
        except Exception as e:
            return rf_settings_pb2.RFResponse(
                success=False,
                status=str(e),
                device_id=request.device_id
            )

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    rf_settings_pb2_grpc.add_RFSettingsServiceServicer_to_server(
        RFSettingsServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("Server running on port 50051")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()