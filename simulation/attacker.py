import requests
import threading
import time
import json
import os

# Your live Render URL deployment endpoint
URL = "https://shieldproxy-l7-cybersec-project-1.onrender.com/"

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