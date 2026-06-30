# 🛡️ ShieldProxy L7

**Enterprise-Grade Layer 7 DDoS Mitigation & Real-Time Threat Intelligence**

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-green)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow)]()

---

## 🎯 Overview

ShieldProxy L7 is a decentralized, Python-based application-layer firewall and reverse-proxy engineered to protect web servers from high-frequency flood attacks and automated scraping. It provides robust traffic filtering, machine-like precision bot detection, and a zero-dependency real-time observability console.

By decoupling security verification logic from the underlying application, ShieldProxy ensures target servers remain stable and unaware of active threat landscapes.

---

## 🛠️ System Architecture & Integration

### Decentralized Component Breakdown
*   **Proxy Boundary Engine (`core/proxy.py`):** Acts as the foundational stateful ingress controller. It manages traffic analysis, tracking calculations, dynamic IP blacklisting, and coordinates REST API exposition.
*   **Isolated Application Server (`core/website.py`):** The underlying targeted platform asset. It is intentionally decoupled from security verification logic and serves standard HTTP responses out-of-the-box.
*   **Telemetry Console Panel (`interface/dashboard.html`):** A zero-dependency, vanilla ECMAScript asynchronous graphical interface that aggregates threat signatures.

### Live Data Pipeline Flow
1. An adversarial agent floods the reverse proxy layer with high-frequency HTTP request packets.
2. The proxy gateway intersects incoming traffic, registers rolling sliding-window arrays, and checks timing distribution states.
3. Upon discovering an anomaly threshold breach, an inline runtime executor seals the client IP block status and commits an append-only payload entry into the local filesystem storage track (`alerts.log`).
4. The frontend tracking loop fires a non-blocking `fetch()` transaction toward the local proxy API boundary at a constant 1-second refresh cycle.
5. The REST endpoint opens the file buffer, decodes the line arrays sequentially into dictionary elements, and pipes a clean JSON response vector back down the channel.
6. The browser runtime loop recalculates the dynamic metric states, shifts visual alarms, and injects data arrays smoothly into the browser window DOM.

---

## 🛡️ Core Defense Mechanisms

### 1. Stateful Rate Limiting (Sliding Window)
Tracks requests per IP address using an accurate sliding-window algorithm. If a client exceeds the configurable threshold (e.g., 5 requests within 5 seconds), the IP is temporarily blacklisted.

### 2. Entropy-Based Behavioral Bot Detection
ShieldProxy utilizes advanced statistical analysis to distinguish between erratic human attackers and highly structured automated bots.
*   **The Math:** The system calculates the time deltas between consecutive requests and computes the statistical variance (standard deviation squared). 
*   **Execution:** Humans inherently possess irregular click patterns (higher variance). Automated bots operating on loops exhibit mechanical precision (variance `< 0.02s`). ShieldProxy mathematically proves automation, instantly doubling the penalty duration for detected bots.

### 3. Decoy Honeypot Trap
The protected application is injected with a hidden DOM node (`<a href="/admin_backup_secret" style="display:none;">`). Legitimate users cannot see or interact with this link. Automated directory scanners and scrapers parsing the DOM will hit this endpoint, triggering a zero-tolerance, instant IP ban while bypassing standard rate-limit counting entirely.

### 4. Stateful Tarpit Protocol
Instead of immediately returning a `429 Too Many Requests` code—which allows an attacker's script to close the socket and fire another thread—ShieldProxy traps the execution thread in a 2.5-second I/O Wait state (`time.sleep(2.5)`). This actively exhausts the attacker's outbound socket connection pool and chokes their threading engine.

---

## 🚀 Quick Start

### Prerequisites
```bash
pip install -r requirements.txt

```

### Start the System (Requires 3 Terminals)

**Terminal 1: Target Server**

```bash
cd core
python website.py

```

**Terminal 2: Proxy + Protection**

```bash
cd core
python proxy.py

```

**Terminal 3: Telemetry Dashboard**
Navigate your web browser to:

```text
http://localhost:5000/dashboard

```

### Simulate an Attack

To observe the mitigation engine in real-time, execute the included simulation tools:

```bash
cd simulation
python attacker.py               # Triggers standard DoS & Behavioral Bot detection
python attackerHoneypotCheck.py  # Triggers the Decoy Honeypot & Tarpit Protocol

```

---

## 📁 Project Structure

```text
ShieldProxy/
├── core/                           # Core application modules
│   ├── proxy.py                    # Main DDoS mitigation proxy server
│   ├── website.py                  # Target web server (protected asset)
│   └── config.json                 # System configuration definitions
│
├── interface/                      # User interface components
│   └── dashboard.html              # Real-time threat intelligence panel
│
├── simulation/                     # Attack simulation & testing tools
│   ├── attacker.py                 # Multi-threaded DDoS flood simulator
│   └── attackerHoneypotCheck.py    # Honeypot tarpit validation script
│
├── documentation/                  # Deep-dive architectural documentation
│   ├── ARCHITECTURE.txt            # Component mapping and traffic flow
│   ├── BEHAVIORAL_BOT_DETECTION.md # Statistical variance proofs
│   └── TROUBLESHOOTING.md          # Operational recovery and diagnostics
│
├── .gitignore                      # Prevents logging garbage leaks (*.log)
├── requirements.txt                # Python environment dependencies
└── README.md                       # This documentation

```

---

## ⚙️ Configuration (`core/config.json`)

System behavior is fully decoupled from the core logic. Edit `config.json` to tune the mitigation thresholds dynamically:

```json
{
  "PROXY_PORT": 5000,
  "TARGET_SERVER_PORT": 8080,
  "LIMIT_REQUESTS": 5,
  "TIME_WINDOW": 5,
  "BAN_DURATION": 10,
  "BOT_VARIANCE_THRESHOLD": 0.02,
  "TARPIT_DELAY": 2.5
}

```

*(Note: Core modules feature built-in fallback tolerances. If `config.json` is corrupted or missing, the system auto-reverts to safe default values without crashing).*

---

## 📡 API Specification & Logging

### Network Ingress Telemetry Stream

ShieldProxy uses a native, append-only JSON Lines format (`alerts.log`), making it immediately ingestible by enterprise SIEM pipelines (e.g., Splunk, ELK Stack) out-of-the-box.

* **Resource URL:** `GET http://localhost:5000/api/logs`
* **Payload Output Schema:**

```json
{
  "success": true,
  "count": 3,
  "logs": [
    {
      "timestamp": "2026-06-30T15:14:58.702287",
      "attacker_ip": "127.0.0.1",
      "status": "blocked",
      "total_requests": 6,
      "type": "behavioral_bot",
      "variance": 0.001956
    },
    {
      "timestamp": "2026-06-30T15:15:02.124555",
      "attacker_ip": "10.0.0.5",
      "status": "blocked",
      "total_requests": 1,
      "type": "honeypot_trap"
    }
  ]
}

```

---

*Developed for robust, decentralized application security.*

```

```