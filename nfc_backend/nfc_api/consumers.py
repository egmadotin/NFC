import json
from channels.generic.websocket import AsyncWebsocketConsumer

class NFCConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("nfc_scans", self.channel_name)
        await self.accept()
        
        # Send initial reader status
        from .nfc_reader import get_reader
        reader = get_reader()
        await self.send(text_data=json.dumps({
            "type": "reader_status",
            "status": "connected" if reader else "disconnected",
            "reader_name": reader.name if reader else None
        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("nfc_scans", self.channel_name)

    async def nfc_scan_message(self, event):
        await self.send(text_data=json.dumps(event["data"]))

    async def reader_status_message(self, event):
        await self.send(text_data=json.dumps(event["data"]))
