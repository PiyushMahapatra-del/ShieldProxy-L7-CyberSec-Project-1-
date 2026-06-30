import requests
import threading
import time
import json
import os

# Load proxy port from config.json with fallback
def load_proxy_port():
    """Load PROXY_PORT from config.json, fallback to 5000"""
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'core', 'config.json')
    try:
        with open(config_path, 'r') as config_file:
            config = json.load(config_file)
            port = config.get("PROXY_PORT", 5000)
            print(f"[✓] Configuration loaded: PROXY_PORT={port}")
            return port
    except (FileNotFoundError, json.JSONDecodeError):
        print(f"[⚠️ WARNING] config.json not found or invalid, using default PROXY_PORT=5000")
        return 5000

PROXY_PORT = load_proxy_port()

# Directing our weapon at the PROXY server
URL = f"http://127.0.0.1:{PROXY_PORT}/"

def flood():
    while True:
        try:
            response = requests.get(URL)
            print(f"[💥 ATTACK] Sent Request. Server responded with Status Code: {response.status_code}")
        except Exception as e:
            print("Server down or unreachable.")
        time.sleep(0.1) # Deliberate rapid spamming

# Spin up 3 concurrent threads to completely flood the server instantly
print("=" * 80)
print("[!] Initiating malicious request flooding sequence...")
print(f"[🎯] Target: {URL}")
print("=" * 80)
for i in range(3):
    t = threading.Thread(target=flood)
    t.daemon = True
    t.start()

# Keep main script alive
while True:
    time.sleep(1)
