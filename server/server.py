# server/server.py
import grpc
from concurrent import futures
import time
import logging
import rfcontrol_pb2
import rfcontrol_pb2_grpc

class RFControllerServicer(rfcontrol_pb2_grpc.RFControllerServicer):
    def __init__(self):
        # Initialize mock device state
        self.device_state = {
            "frequency": 0.0,
            "gain": 0.0,
            "device_id": "none",
            "status": "disconnected"
        }
    
    def _mock_uhd_set_rf(self, frequency, gain, device_id):
        """Mock UHD implementation for testing without hardware"""
        # Simulate hardware delay
        time.sleep(0.2) 
        
        # Validate inputs
        if frequency <= 0:
            return False, "Frequency must be positive"
        if not (-20 <= gain <= 30):
            return False, "Gain must be between -20 and 30 dB"
        
        # Update mock device state
        self.device_state.update({
            "frequency": frequency,
            "gain": gain,
            "device_id": device_id,
            "status": "configured"
        })
        
        return True, f"Configured {device_id}: {frequency/1e6:.2f} MHz, {gain} dB"

    def SetRFSettings(self, request, context):
        """gRPC method implementation using mock UHD"""
        try:
            # Call mock UHD function
            success, message = self._mock_uhd_set_rf(
                request.frequency,
                request.gain,
                request.device_id
            )
            
            return rfcontrol_pb2.RFResponse(
                success=success,
                message=message,
                device_status=self.device_state["status"]
            )
            
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            return rfcontrol_pb2.RFResponse(
                success=False,
                message=f"Error: {str(e)}",
                device_status="error"
            )

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    rfcontrol_pb2_grpc.add_RFControllerServicer_to_server(
        RFControllerServicer(), server)
    server.add_insecure_port('[::]:50051')
    logging.info("Server started on port 50051")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    serve()