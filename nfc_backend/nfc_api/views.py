from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Scan
from .serializers import ScanSerializer
import threading

# Global flag to control the NFC listener thread
nfc_thread = None
stop_nfc = threading.Event()

class ScanViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Scan.objects.all().order_by('-timestamp')
    serializer_class = ScanSerializer

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
