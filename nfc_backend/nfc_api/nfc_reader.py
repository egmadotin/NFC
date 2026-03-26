import time
import logging
from smartcard.System import readers
from smartcard.util import toHexString
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import Scan

logger = logging.getLogger(__name__)

def get_reader():
    try:
        r = readers()
        logger.debug(f"Detected readers: {[reader.name for reader in r]}")
        if len(r) > 0:
            return r[0]
        return None
    except Exception as e:
        logger.error(f"Error enumerating readers: {e}")
        return None

def read_tag(reader_obj):
    try:
        connection = reader_obj.createConnection()
        connection.connect()
        
        # Get UID (Get Data command)
        GET_UID = [0xFF, 0xCA, 0x00, 0x00, 0x00]
        data, sw1, sw2 = connection.transmit(GET_UID)
        uid = toHexString(data)
        
        atr = toHexString(connection.getATR())
        
        return {
            "uid": uid,
            "atr": atr,
            "status": "success"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

def broadcast_scan(data):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "nfc_scans",
        {
            "type": "nfc_scan_message",
            "data": data
        }
    )

def broadcast_status(status, reader_name=None):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "nfc_scans",
        {
            "type": "reader_status_message",
            "data": {
                "type": "reader_status",
                "status": status,
                "reader_name": reader_name
            }
        }
    )

def run_listener(stop_event):
    logger.info("NFC Listener started")
    last_uid = None
    last_status = None
    
    while not stop_event.is_set():
        reader = get_reader()
        current_status = "connected" if reader else "disconnected"
        
        if current_status != last_status:
            broadcast_status(current_status, reader.name if reader else None)
            last_status = current_status

        if not reader:
            time.sleep(1)
            continue
            
        try:
            result = read_tag(reader)
            if result["status"] == "success":
                uid = result["uid"]
                if uid != last_uid:
                    # New tag detected
                    scan = Scan.objects.create(
                        uid=uid,
                        atr=result["atr"],
                    )
                    data = {
                        "type": "scan_result",
                        "id": scan.id,
                        "uid": scan.uid,
                        "atr": scan.atr,
                        "timestamp": scan.timestamp.isoformat(),
                        "status": "success"
                    }
                    broadcast_scan(data)
                    last_uid = uid
            else:
                last_uid = None 
        except Exception as e:
            logger.error(f"Error in listener: {e}")
            last_uid = None
            
        time.sleep(0.5)
    
    broadcast_status("disconnected")
    logger.info("NFC Listener stopped")
