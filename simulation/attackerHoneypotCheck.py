import requests
import time
import json
import os
from datetime import datetime

# Load proxy port from config.json with fallback
def load_config():
    """Load configuration from config.json, fallback to defaults"""
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'core', 'config.json')
    try:
        with open(config_path, 'r') as config_file:
            config = json.load(config_file)
            print(f"[✓] Configuration loaded from: {config_path}")
            return config
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"[⚠️ WARNING] config.json not found or invalid, using defaults")
        return {"PROXY_PORT": 5000, "TARPIT_DELAY": 2.5}

# Load configuration
config = load_config()
PROXY_PORT = config.get("PROXY_PORT", 5000)
TARPIT_DELAY = config.get("TARPIT_DELAY", 2.5)

# Honeypot endpoint URL
HONEYPOT_URL = f"http://127.0.0.1:{PROXY_PORT}/admin_backup_secret"

print("=" * 80)
print("🍯 HONEYPOT TRAP TESTER")
print("=" * 80)
print(f"[🎯] Target Honeypot: {HONEYPOT_URL}")
print(f"[⏱️] Expected Tarpit Delay: {TARPIT_DELAY} seconds")
print("=" * 80)

# Send single honeypot probe
print(f"\n[📡] Dispatching probe to honeypot endpoint...")
print(f"[🕐] Request sent at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}")

start_time = time.time()

try:
    response = requests.get(HONEYPOT_URL, timeout=10)
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
    print(f"[❌] Request timed out after 10 seconds")
except requests.ConnectionError:
    print(f"[❌] Connection failed - is the proxy running on port {PROXY_PORT}?")
except Exception as e:
    print(f"[❌] Error: {e}")
