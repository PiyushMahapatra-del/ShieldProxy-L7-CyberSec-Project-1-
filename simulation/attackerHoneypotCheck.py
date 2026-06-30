import requests
import time
import json
import os
from datetime import datetime

# Define your production Render application base URL
RENDER_URL = "https://shieldproxy-l7-cybersec-project-1.onrender.com"

# Render environment configurations fallback
TARPIT_DELAY = 2.5

# Honeypot endpoint URL targeting the live Render setup
HONEYPOT_URL = f"{RENDER_URL}/admin_backup_secret"

print("=" * 80)
print("🍯 HONEYPOT TRAP TESTER (RENDER ENVIRONMENT)")
print("=" * 80)
print(f"[🎯] Target Honeypot: {HONEYPOT_URL}")
print(f"[⏱️] Expected Tarpit Delay: {TARPIT_DELAY} seconds")
print("=" * 80)

# Send single honeypot probe
print(f"\n[📡] Dispatching probe to honeypot endpoint...")
print(f"[🕐] Request sent at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}")

start_time = time.time()

try:
    response = requests.get(HONEYPOT_URL, timeout=15)
    end_time = time.time()
    
    elapsed_time = end_time - start_time
    
    print(f"[🕐] Response received at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}")
    print("=" * 80)
    print(f"[⏱️] Response Time: {elapsed_time:.3f} seconds")
    print(f"[📊] HTTP Status Code: {response.status_code}")
    print(f"[📝] Response Message: {response.text[:100]}")
    print("=" * 80)
    
    # Validate results
    if response.status_code == 429:
        print("✅ Status: Honeypot successfully triggered (429 Too Many Requests)")
    else:
        print(f"⚠️ Status: Unexpected status code {response.status_code}")
    
    if elapsed_time >= TARPIT_DELAY:
        print(f"✅ Tarpit: Successfully held for {elapsed_time:.3f}s (expected ~{TARPIT_DELAY}s)")
    else:
        print(f"⚠️ Tarpit: Response too fast ({elapsed_time:.3f}s), expected delay ~{TARPIT_DELAY}s")
    
    print("=" * 80)
    print("[🍯] HONEYPOT TRAP TEST COMPLETE")
    print(f"[🚨] Your IP should now be BLOCKED for accessing the honeypot!")
    print("=" * 80)
    
except requests.Timeout:
    print(f"[❌] Request timed out after 15 seconds")
except requests.ConnectionError:
    print(f"[❌] Connection failed - is the Render deployment active at {RENDER_URL}?")
except Exception as e:
    print(f"[❌] Error: {e}")