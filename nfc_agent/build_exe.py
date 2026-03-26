import PyInstaller.__main__
import os

# Build instructions:
# python build_exe.py

PyInstaller.__main__.run([
    'nfc_agent.py',
    '--onefile',
    '--noconsole',
    '--icon=NONE', # Can add .ico here
    '--name=NFCAgent',
    '--hidden-import=pystray._win32',
    '--hidden-import=PIL._imagingtk',
    '--hidden-import=PIL._tkinter_finder',
    '--add-data=config.json;.'
])

print("Build complete. Check the 'dist' folder for NFCAgent.exe")
