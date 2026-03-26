from smartcard.System import readers
try:
    r = readers()
    print(f"Total readers found: {len(r)}")
    if not r:
        print("No readers detected. Is the Smart Card service running?")
    for reader in r:
        print(f"Detected Reader: {reader.name}")
except Exception as e:
    print(f"Error: {e}")
