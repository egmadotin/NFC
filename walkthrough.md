# NFC Reader System Walkthrough

The NFC Reader System is a full-stack application that integrates with an ACR122U USB NFC reader to provide real-time tag data on a modern web dashboard.

## Features Accomplished
- [x] **Real-time Synchronization**: Instant display of NFC UID/ATR via WebSockets.
- [x] **Hardware Integration**: Background listener for ACR122U using `pyscard`.
- [x] **Modern Dashboard**: Dark-themed UI with pulse animations and scan history.
- [x] **Control System**: Start/Stop listener buttons from the web interface.
- [x] **Database Logging**: Persistent storage of all successful scans.

## Project Structure
- `nfc_backend/`: Django (Python) project with Channels and DRF.
- `nfc_frontend/`: Next.js (React/TypeScript) project with Vanilla CSS.

## Setup Instructions

### 1. Backend Setup
1. Open a terminal in `nfc_backend/`.
2. Activate (Windows)
.\venv\Scripts\activate
3. Install dependencies:
   ```bash
   pip install django djangorestframework channels[daphne] pyscard django-cors-headers
   ```
3. Run migrations:
   ```bash
   python manage.py migrate
   ```
4. Start the server:
   ```bash
   python manage.py runserver
   ```

### 2. Frontend Setup
1. Open a terminal in `nfc_frontend/`.
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm run dev
   ```

## Usage
1. Open [http://localhost:3000](http://localhost:3000) in your browser.
2. Click **Start Reader** on the dashboard.
3. Tap an NFC tag on your ACR122U device.
4. The UID and ATR will instantly appear with a pulse animation and a beep!

---
## NFC Agent (Standalone EXE)
The project now includes a standalone Windows agent that runs in the background.

### Agent Features
- System Tray Icon: Green when connected, Red when disconnected.
- Auto-Config: Reads 
config.json
 for the server URL.
- Background Mode: No console window, minimal resource usage.
- Standalone: All dependencies included in the single EXE.

### How to Build the EXE
1. Navigate to the nfc_agent folder.
2. Install build dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the build script:
   ```bash
   python build_exe.py
   ```
4. Find your NFCAgent.exe in the dist/ folder.

> [!IMPORTANT]
> Ensure your ACR122U drivers are installed on Windows (PC/SC drivers) for the system to detect the reader.
