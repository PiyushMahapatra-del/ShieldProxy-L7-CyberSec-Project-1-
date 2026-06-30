# mimics our target website...

import http.server
import socketserver
import json
import os

# Load port from config.json with fallback
def load_port():
    """Load TARGET_SERVER_PORT from config.json, fallback to 8080"""
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    try:
        with open(config_path, 'r') as config_file:
            config = json.load(config_file)
            port = config.get("TARGET_SERVER_PORT", 8080)
            print(f"[✓] Configuration loaded: PORT={port}")
            return port
    except (FileNotFoundError, json.JSONDecodeError):
        print(f"[⚠️ WARNING] config.json not found or invalid, using default PORT=8080")
        return 8080

PORT = load_port()

class MyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        # The HTML page that displays when a user visits safely
        html_content = """
        <html>
        <head>
            <style>
                body { background-color: #0f172a; color: #38bdf8; font-family: sans-serif; text-align: center; padding-top: 100px; }
                .card { border: 2px solid #38bdf8; display: inline-block; padding: 30px; border-radius: 10px; background: #1e293b; }
            </style>
        </head>
        <body>
            <div class="card">
                <h1>✓ Target Web Server Online</h1>
                <p>Welcome! This is a secure server running behind our defense proxy.</p>
                <a href="/admin_backup_secret" style="display:none;">System Backup</a>
            </div>
        </body>
        </html>
        """
        self.wfile.write(bytes(html_content, "utf-8"))

with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
    print("=" * 80)
    print(f"[+] Target Web Server running on port {PORT}...")
    print(f"[🍯] Honeypot endpoint embedded: /admin_backup_secret (hidden)")
    print("=" * 80)
    httpd.serve_forever()
