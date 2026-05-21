"""
generate_traffic.py
Generates a synthetic network traffic log (CSV) that simulates
a small government office network over 24 hours.

Includes embedded anomalies:
  - Port scanning from an external IP
  - Data exfiltration (large outbound transfers at odd hours)
  - Brute-force SSH login attempts
  - DNS tunneling indicators (high-frequency DNS queries)

Usage:
    python generate_traffic.py
    -> produces data/network_traffic.csv
"""

import csv
import os
import random
from datetime import datetime, timedelta

random.seed(42)

# --- Configuration ---
OUTPUT_DIR = "data"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "network_traffic.csv")
NUM_NORMAL_RECORDS = 8000
START_TIME = datetime(2026, 5, 1, 0, 0, 0)

# Internal hosts (a small government LGU office)
INTERNAL_IPS = [
    "192.168.1.10",   # Workstation - Admin
    "192.168.1.11",   # Workstation - Legal
    "192.168.1.12",   # Workstation - Finance
    "192.168.1.13",   # Workstation - IT
    "192.168.1.14",   # Workstation - Records
    "192.168.1.100",  # File Server
    "192.168.1.101",  # Web Server (internal portal)
    "192.168.1.200",  # DNS Server
]

# Benign external IPs
EXTERNAL_IPS_BENIGN = [
    "203.0.113.5",    # Cloud provider
    "198.51.100.20",  # Software update server
    "198.51.100.45",  # Government portal
    "203.0.113.80",   # Email relay
    "198.51.100.100", # News/reference site
]

# Malicious external IPs
ATTACKER_IP = "45.33.32.156"
EXFIL_DEST_IP = "91.198.174.50"

PROTOCOLS = ["TCP", "UDP", "ICMP"]
NORMAL_PORTS = [80, 443, 53, 25, 110, 143, 993, 587, 8080, 3306]
ALL_SCAN_PORTS = list(range(1, 1025))

FIELDNAMES = [
    "timestamp", "src_ip", "dst_ip", "src_port", "dst_port",
    "protocol", "bytes_sent", "bytes_received", "packets",
    "duration_sec", "flag", "label"
]


def random_timestamp(base, window_hours=24):
    return base + timedelta(seconds=random.randint(0, window_hours * 3600))


def generate_normal_traffic(n):
    """Generate baseline legitimate traffic."""
    rows = []
    for _ in range(n):
        direction = random.choice(["outbound", "inbound", "internal"])
        if direction == "outbound":
            src = random.choice(INTERNAL_IPS[:5])
            dst = random.choice(EXTERNAL_IPS_BENIGN)
        elif direction == "inbound":
            src = random.choice(EXTERNAL_IPS_BENIGN)
            dst = random.choice(INTERNAL_IPS)
        else:
            src = random.choice(INTERNAL_IPS[:5])
            dst = random.choice(INTERNAL_IPS[5:])

        port = random.choice(NORMAL_PORTS)
        proto = "TCP" if port != 53 else random.choice(["TCP", "UDP"])
        ts = random_timestamp(START_TIME)

        # Business hours have heavier traffic
        hour = ts.hour
        if 8 <= hour <= 17:
            bytes_s = random.randint(200, 15000)
            bytes_r = random.randint(500, 50000)
        else:
            bytes_s = random.randint(50, 3000)
            bytes_r = random.randint(100, 5000)

        rows.append({
            "timestamp": ts.strftime("%Y-%m-%d %H:%M:%S"),
            "src_ip": src,
            "dst_ip": dst,
            "src_port": random.randint(49152, 65535),
            "dst_port": port,
            "protocol": proto,
            "bytes_sent": bytes_s,
            "bytes_received": bytes_r,
            "packets": random.randint(1, 80),
            "duration_sec": round(random.uniform(0.01, 120.0), 2),
            "flag": random.choice(["SYN-ACK", "ACK", "FIN", "PSH-ACK"]),
            "label": "normal"
        })
    return rows


def generate_port_scan(n=250):
    """Attacker scans internal web server across many ports."""
    rows = []
    scan_start = START_TIME + timedelta(hours=2, minutes=14)
    for i in range(n):
        ts = scan_start + timedelta(seconds=i * 0.3)
        rows.append({
            "timestamp": ts.strftime("%Y-%m-%d %H:%M:%S"),
            "src_ip": ATTACKER_IP,
            "dst_ip": "192.168.1.101",
            "src_port": random.randint(49152, 65535),
            "dst_port": ALL_SCAN_PORTS[i % len(ALL_SCAN_PORTS)],
            "protocol": "TCP",
            "bytes_sent": random.randint(40, 60),
            "bytes_received": random.randint(0, 44),
            "packets": 1,
            "duration_sec": round(random.uniform(0.001, 0.05), 4),
            "flag": random.choice(["SYN", "RST"]),
            "label": "port_scan"
        })
    return rows


def generate_brute_force(n=180):
    """Brute-force SSH attempts against IT workstation."""
    rows = []
    bf_start = START_TIME + timedelta(hours=3, minutes=45)
    for i in range(n):
        ts = bf_start + timedelta(seconds=i * 2)
        rows.append({
            "timestamp": ts.strftime("%Y-%m-%d %H:%M:%S"),
            "src_ip": ATTACKER_IP,
            "dst_ip": "192.168.1.13",
            "src_port": random.randint(49152, 65535),
            "dst_port": 22,
            "protocol": "TCP",
            "bytes_sent": random.randint(80, 200),
            "bytes_received": random.randint(40, 100),
            "packets": random.randint(3, 8),
            "duration_sec": round(random.uniform(0.5, 3.0), 2),
            "flag": "SYN-ACK",
            "label": "brute_force"
        })
    return rows


def generate_data_exfiltration(n=35):
    """Large outbound data transfers at 1-4 AM from file server."""
    rows = []
    for _ in range(n):
        hour = random.randint(1, 4)
        minute = random.randint(0, 59)
        ts = START_TIME.replace(hour=hour, minute=minute)
        rows.append({
            "timestamp": ts.strftime("%Y-%m-%d %H:%M:%S"),
            "src_ip": "192.168.1.100",
            "dst_ip": EXFIL_DEST_IP,
            "src_port": random.randint(49152, 65535),
            "dst_port": 443,
            "protocol": "TCP",
            "bytes_sent": random.randint(500000, 5000000),
            "bytes_received": random.randint(200, 1000),
            "packets": random.randint(300, 2000),
            "duration_sec": round(random.uniform(30.0, 300.0), 2),
            "flag": "PSH-ACK",
            "label": "exfiltration"
        })
    return rows


def generate_dns_tunneling(n=400):
    """High-frequency DNS queries indicating tunneling."""
    rows = []
    dns_start = START_TIME + timedelta(hours=13, minutes=20)
    for i in range(n):
        ts = dns_start + timedelta(seconds=i * 0.8)
        rows.append({
            "timestamp": ts.strftime("%Y-%m-%d %H:%M:%S"),
            "src_ip": "192.168.1.12",
            "dst_ip": "192.168.1.200",
            "src_port": random.randint(49152, 65535),
            "dst_port": 53,
            "protocol": "UDP",
            "bytes_sent": random.randint(150, 512),
            "bytes_received": random.randint(200, 512),
            "packets": 1,
            "duration_sec": round(random.uniform(0.001, 0.1), 4),
            "flag": "ACK",
            "label": "dns_tunneling"
        })
    return rows


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    all_rows = []
    all_rows.extend(generate_normal_traffic(NUM_NORMAL_RECORDS))
    all_rows.extend(generate_port_scan())
    all_rows.extend(generate_brute_force())
    all_rows.extend(generate_data_exfiltration())
    all_rows.extend(generate_dns_tunneling())

    # Sort by timestamp
    all_rows.sort(key=lambda r: r["timestamp"])

    with open(OUTPUT_FILE, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(all_rows)

    total = len(all_rows)
    anomalies = sum(1 for r in all_rows if r["label"] != "normal")
    print(f"Generated {total:,} records ({anomalies} anomalies) -> {OUTPUT_FILE}")
    print(f"  Port scans:      {sum(1 for r in all_rows if r['label'] == 'port_scan')}")
    print(f"  Brute force:     {sum(1 for r in all_rows if r['label'] == 'brute_force')}")
    print(f"  Exfiltration:    {sum(1 for r in all_rows if r['label'] == 'exfiltration')}")
    print(f"  DNS tunneling:   {sum(1 for r in all_rows if r['label'] == 'dns_tunneling')}")


if __name__ == "__main__":
    main()
