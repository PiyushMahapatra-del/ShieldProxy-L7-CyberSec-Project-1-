from flask import Flask, request, Response, send_file, jsonify
import requests
import time
import json
import os
import math
from datetime import datetime

app = Flask(__name__)

# Load configuration from config.json with fallback to defaults
def load_config():
    """
    Load configuration from config.json file.
    Falls back to default values if file is missing or invalid.
    """
    default_config = {
        "PROXY_PORT": 5000,
        "TARGET_SERVER_PORT": 8080,
        "LIMIT_REQUESTS": 5,
        "TIME_WINDOW": 5,
        "BAN_DURATION": 10,
        "BOT_VARIANCE_THRESHOLD": 0.02,
        "TARPIT_DELAY": 2.5
    }
    
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    
    try:
        with open(config_path, 'r') as config_file:
            config = json.load(config_file)
            print(f"[✓] Configuration loaded from {config_path}")
            return config
    except FileNotFoundError:
        print(f"[⚠️ WARNING] config.json not found at {config_path}, using default configuration")
        return default_config
    except json.JSONDecodeError as e:
        print(f"[⚠️ WARNING] Invalid JSON in config.json: {e}, using default configuration")
        return default_config

# Load configuration
config = load_config()

# Extract configuration values
PROXY_PORT = config.get("PROXY_PORT", 5000)
TARGET_SERVER_PORT = config.get("TARGET_SERVER_PORT", 8080)
LIMIT_REQUESTS = config.get("LIMIT_REQUESTS", 5)
TIME_WINDOW = config.get("TIME_WINDOW", 5)
BAN_DURATION = config.get("BAN_DURATION", 10)
BOT_VARIANCE_THRESHOLD = config.get("BOT_VARIANCE_THRESHOLD", 0.02)
TARPIT_DELAY = config.get("TARPIT_DELAY", 2.5)

# TARGET WEBSITE ADDRESS
TARGET_URL = f"http://127.0.0.1:{TARGET_SERVER_PORT}"

# Tracker dictionary structure: { "IP_ADDRESS": [timestamp1, timestamp2, ...] }
request_tracker = {}

# Blocked IPs dictionary structure: { "IP_ADDRESS": unlock_timestamp }
blocked_ips = {}

def calculate_request_variance(timestamps):
    """
    Calculate the standard deviation of time deltas between consecutive requests.
    Returns the variance (std dev squared) to detect automated bot patterns.
    """
    if len(timestamps) < 2:
        return None
    
    # Calculate time deltas between consecutive requests
    deltas = []
    for i in range(1, len(timestamps)):
        deltas.append(timestamps[i] - timestamps[i-1])
    
    if len(deltas) < 2:
        return None
    
    # Calculate mean
    mean_delta = sum(deltas) / len(deltas)
    
    # Calculate variance (standard deviation squared)
    variance = sum((x - mean_delta) ** 2 for x in deltas) / len(deltas)
    
    return variance

def log_alert(attacker_ip, total_requests, attack_type="standard", variance=None):
    """
    Logs a structured JSON alert entry when an IP gets blocked
    """
    alert_entry = {
        "timestamp": datetime.now().isoformat(),
        "attacker_ip": attacker_ip,
        "status": "blocked",
        "total_requests": total_requests
    }
    
    # Add behavioral bot detection flag or honeypot trap flag
    if attack_type == "behavioral_bot":
        alert_entry["type"] = "behavioral_bot"
        alert_entry["variance"] = round(variance, 6) if variance is not None else None
    elif attack_type == "honeypot_trap":
        alert_entry["type"] = "honeypot_trap"
    
    # Write to alerts.log in project root (one level up from core/)
    log_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'alerts.log')
    
    try:
        with open(log_path, "a") as log_file:
            log_file.write(json.dumps(alert_entry) + "\n")
        print(f"[📝 LOGGED] Alert written to alerts.log for IP: {attacker_ip}")
    except Exception as e:
        print(f"[⚠️ WARNING] Failed to write to alerts.log: {e}")

@app.route('/dashboard')
def dashboard():
    """
    Serve the admin dashboard HTML interface from interface/ directory
    """
    try:
        dashboard_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'interface', 'dashboard.html')
        return send_file(dashboard_path)
    except Exception as e:
        return f"Dashboard not found: {e}", 404

@app.route('/api/logs')
def get_logs():
    """
    API endpoint to retrieve all logged alerts as JSON
    Reads alerts.log and returns parsed JSON array
    """
    logs = []
    
    # alerts.log is in project root (one level up from core/)
    log_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'alerts.log')
    
    try:
        # Check if alerts.log exists
        if os.path.exists(log_path):
            with open(log_path, 'r') as log_file:
                for line in log_file:
                    line = line.strip()
                    if line:  # Skip empty lines
                        try:
                            log_entry = json.loads(line)
                            logs.append(log_entry)
                        except json.JSONDecodeError:
                            # Skip malformed lines
                            continue
        
        return jsonify({
            'success': True,
            'count': len(logs),
            'logs': logs
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'logs': []
        }), 500

@app.route('/', defaults={'path': ''}, methods=['GET', 'POST', 'PUT', 'DELETE'])
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def proxy(path):
    user_ip = request.remote_addr
    current_time = time.time()

    # Check 0: Honeypot trap check - bypasses token count entirely
    if path == "admin_backup_secret" or request.path == "/admin_backup_secret" or "admin_backup_secret" in request.path:
        if user_ip not in request_tracker:
            request_tracker[user_ip] = []
        request_tracker[user_ip].append(current_time)
        total_requests = len(request_tracker[user_ip])
        blocked_ips[user_ip] = current_time + BAN_DURATION
        print(f"[🍯 HONEYPOT TRAP] Malicious bot accessed hidden honeypot /admin_backup_secret from IP: {user_ip}!")
        log_alert(user_ip, total_requests, attack_type="honeypot_trap")
        time.sleep(TARPIT_DELAY)
        return "Blocked for malicious threshold breach.", 429

    # Check 1: Is this IP currently banned?
    if user_ip in blocked_ips:
        if current_time < blocked_ips[user_ip]:
            remaining_ban = int(blocked_ips[user_ip] - current_time)
            # The Red Screen of Doom
            time.sleep(TARPIT_DELAY)
            return """
            <body style="background-color:#7f1d1d; color:white; font-family:sans-serif; text-align:center; padding-top:100px;">
                <h1>❌ 429: Too Many Requests</h1>
                <h2>DoS Attack Mitigated. Your IP has been temporarily blocked by the system.</h2>
                <p>Try again after absolute cooldown finishes.</p>
            </body>
            """, 429
        else:
            # Ban expired, remove them from the blacklist
            del blocked_ips[user_ip]
            request_tracker[user_ip] = []

    # Check 2: Rate limiting logic
    if user_ip not in request_tracker:
        request_tracker[user_ip] = []

    # Clean out timestamps older than our time window
    request_tracker[user_ip] = [t for t in request_tracker[user_ip] if current_time - t < TIME_WINDOW]

    # Add the current request timestamp
    request_tracker[user_ip].append(current_time)

    # If they hit more than LIMIT_REQUESTS in TIME_WINDOW seconds -> TRIGGER BLOCK
    if len(request_tracker[user_ip]) > LIMIT_REQUESTS:
        total_requests = len(request_tracker[user_ip])
        ban_duration = BAN_DURATION
        attack_type = "standard"
        
        # BEHAVIORAL BOT DETECTION: Analyze request timing pattern
        # Use last 5 requests for analysis (or all if less than 5)
        recent_requests = request_tracker[user_ip][-5:] if len(request_tracker[user_ip]) >= 5 else request_tracker[user_ip]
        
        if len(recent_requests) >= 2:
            variance = calculate_request_variance(recent_requests)
            
            # If variance is very low, it's a highly structured automated bot
            if variance is not None and variance < BOT_VARIANCE_THRESHOLD:
                ban_duration = BAN_DURATION * 2  # Double the ban duration
                attack_type = "behavioral_bot"
                print(f"[🤖 BOT DETECTED] Highly structured automated bot from IP: {user_ip}!")
                print(f"[📊 ANALYSIS] Request variance: {variance:.6f}s (threshold: {BOT_VARIANCE_THRESHOLD}s)")
                print(f"[⚡ ENHANCED BAN] Doubling ban duration to {ban_duration}s for behavioral bot.")
        
        blocked_ips[user_ip] = current_time + ban_duration
        print(f"[🚨 EMERGENCY] DoS Detected from IP: {user_ip}! Blocking for {ban_duration}s.")
        
        # LOG THE ALERT with attack type
        log_alert(user_ip, total_requests, attack_type, variance if attack_type == "behavioral_bot" else None)
        
        time.sleep(TARPIT_DELAY)
        return "Blocked for malicious threshold breach.", 429

    # If they are safe, route their traffic cleanly to the real website
    print(f"[✔ SAFE] Routing request from {user_ip} to target website.")
    resp = requests.request(
        method=request.method,
        url=f"{TARGET_URL}/{path}",
        headers={key: value for (key, value) in request.headers if key != 'Host'},
        data=request.get_data(),
        cookies=request.cookies,
        allow_redirects=False
    )
    
    return Response(resp.content, resp.status_code, resp.headers.items())

if __name__ == '__main__':
    print("=" * 80)
    print("[*] ShieldProxy L7 DDoS Mitigation System Starting...")
    print("=" * 80)
    print(f"[⚙️ CONFIG] Proxy Port: {PROXY_PORT}")
    print(f"[⚙️ CONFIG] Target Server Port: {TARGET_SERVER_PORT}")
    print(f"[⚙️ CONFIG] Rate Limit: {LIMIT_REQUESTS} requests per {TIME_WINDOW} seconds")
    print(f"[⚙️ CONFIG] Ban Duration: {BAN_DURATION} seconds")
    print(f"[⚙️ CONFIG] Bot Variance Threshold: {BOT_VARIANCE_THRESHOLD} seconds")
    print(f"[⚙️ CONFIG] Tarpit Delay: {TARPIT_DELAY} seconds")
    print("=" * 80)
    app.run(host='0.0.0.0', port=PROXY_PORT, debug=True, threaded=True)
