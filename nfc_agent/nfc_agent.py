import os
import sys
import time
import json
import logging
import threading
import requests
from datetime import datetime
from smartcard.System import readers
from smartcard.util import toHexString
from pystray import Icon, Menu, MenuItem
from PIL import Image, ImageDraw

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class NFCAgent:
    def __init__(self):
        self.config = self.load_config()
        self.server_url = self.config.get("server_url", "http://127.0.0.1:8000/api/scans/")
        self.reader_name_target = self.config.get("reader_name", "ACR122U")
        self.running = True
        self.reader_connected = False
        self.last_uid = None
        self.icon = None

    def load_config(self):
        try:
            if os.path.exists("config.json"):
                with open("config.json", "r") as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading config: {e}")
        return {}

    def create_image(self, color):
        width, height = 64, 64
        image = Image.new('RGB', (width, height), (30, 30, 30))
        dc = ImageDraw.Draw(image)
        dc.ellipse([8, 8, 56, 56], fill=color)
        return image

    def on_quit(self, icon, item):
        self.running = False
        icon.stop()
        os._exit(0)

    def run_tray(self):
        menu = Menu(MenuItem('Exit', self.on_quit))
        self.icon = Icon("NFC Agent", self.create_image('red'), "NFC Agent: Disconnected", menu)
        self.icon.run()

    def update_status(self, connected):
        if self.icon:
            self.reader_connected = connected
            color = 'green' if connected else 'red'
            status_text = f"NFC Agent: {'Connected' if connected else 'Disconnected'}"
            self.icon.icon = self.create_image(color)
            self.icon.title = status_text

    def get_reader(self):
        r = readers()
        for reader in r:
            if self.reader_name_target in reader.name:
                return reader
        return r[0] if r else None

    def send_to_server(self, data):
        try:
            resp = requests.post(self.server_url, json=data, timeout=5)
            if resp.status_code in [200, 201]:
                logger.info(f"Successfully sent data: {data['uid']}")
                return True
            else:
                logger.error(f"Server error: {resp.status_code}")
        except Exception as e:
            logger.error(f"Network error: {e}")
        return False

    def monitor_loop(self):
        logger.info("NFC Agent monitor loop started")
        while self.running:
            reader = self.get_reader()
            
            if not reader:
                if self.reader_connected:
                    logger.warning("Reader disconnected")
                    self.update_status(False)
                time.sleep(2)
                continue

            if not self.reader_connected:
                logger.info(f"Reader connected: {reader.name}")
                self.update_status(True)

            try:
                connection = reader.createConnection()
                connection.connect()
                
                # Get UID
                GET_UID = [0xFF, 0xCA, 0x00, 0x00, 0x00]
                data, sw1, sw2 = connection.transmit(GET_UID)
                uid = toHexString(data)
                
                if uid != self.last_uid:
                    atr = toHexString(connection.getATR())
                    payload = {
                        "uid": uid,
                        "atr": atr,
                        "raw_data": "", # Can add more read logic if needed
                        "device": reader.name,
                        "status": "success"
                    }
                    if self.send_to_server(payload):
                        self.last_uid = uid
                        # Simple beep (Windows only)
                        if sys.platform == "win32":
                            import winsound
                            winsound.Beep(1000, 100)
                
            except Exception as e:
                # Card removed or connection lost
                self.last_uid = None
                
            time.sleep(0.5)

if __name__ == "__main__":
    agent = NFCAgent()
    
    # Start monitor in background thread
    monitor_thread = threading.Thread(target=agent.monitor_loop, daemon=True)
    monitor_thread.start()
    
    # Run tray in main thread
    agent.run_tray()
