from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Scan
from .serializers import ScanSerializer
import threading

# Global flag to control the NFC listener thread
nfc_thread = None
stop_nfc = threading.Event()

class ScanViewSet(viewsets.ModelViewSet):
    queryset = Scan.objects.all().order_by('-timestamp')
    serializer_class = ScanSerializer

    def perform_create(self, serializer):
        scan = serializer.save()
        
        from .nfc_reader import broadcast_scan, broadcast_status
        
        # Broadcast the scan result
        broadcast_scan({
            "type": "scan_result",
            "id": scan.id,
            "uid": scan.uid,
            "atr": scan.atr,
            "timestamp": scan.timestamp.isoformat(),
            "status": "success"
        })
        
        # Also update status since we just got a successful scan from a device
        # Note: the payload has a 'device' field, but it's not in the model. Agent sends it.
        device_name = self.request.data.get("device", "Remote Agent")
        broadcast_status("connected", reader_name=device_name)

@api_view(['POST'])
def start_nfc(request):
    global nfc_thread
    if nfc_thread and nfc_thread.is_alive():
        return Response({"status": "Already running"}, status=status.HTTP_400_BAD_REQUEST)
    
    from .nfc_reader import run_listener
    stop_nfc.clear()
    nfc_thread = threading.Thread(target=run_listener, args=(stop_nfc,))
    nfc_thread.daemon = True
    nfc_thread.start()
    return Response({"status": "Started"})

@api_view(['POST'])
def stop_nfc_view(request):
    global nfc_thread
    if nfc_thread:
        stop_nfc.set()
        nfc_thread.join(timeout=2)
        nfc_thread = None
        return Response({"status": "Stopped"})
    return Response({"status": "Not running"}, status=status.HTTP_400_BAD_REQUEST)
