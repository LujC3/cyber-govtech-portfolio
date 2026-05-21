"""
analyze_traffic.py
Analyzes the synthetic network traffic log to detect and visualize
security anomalies relevant to a local government unit (LGU) network.

Detections:
  1. Port scanning        — single IP hitting many distinct ports rapidly
  2. Brute-force attacks  — repeated connections to SSH (port 22)
  3. Data exfiltration    — abnormally large outbound transfers at night
  4. DNS tunneling        — high-frequency DNS queries from one host

Outputs:
  - Console summary of findings
  - Six visualisation charts saved to output/

Usage:
    python generate_traffic.py   # (run first to create the dataset)
    python analyze_traffic.py
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
from datetime import datetime

# --- Configuration ---
INPUT_FILE = "data/network_traffic.csv"
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Detection thresholds
PORT_SCAN_THRESHOLD = 20         # unique ports per source IP per hour
BRUTE_FORCE_THRESHOLD = 15       # SSH connections per source IP per hour
EXFIL_BYTES_THRESHOLD = 100_000  # bytes sent in a single connection
EXFIL_HOUR_START = 0             # off-hours window start
EXFIL_HOUR_END = 5               # off-hours window end
DNS_QUERY_RATE_THRESHOLD = 50    # DNS queries per source IP per minute


# ===========================================================================
# 1. LOAD AND EXPLORE
# ===========================================================================

def load_data(filepath):
    """Load CSV and parse timestamps."""
    df = pd.read_csv(filepath, parse_dates=["timestamp"])
    df["hour"] = df["timestamp"].dt.hour
    df["minute"] = df["timestamp"].dt.minute
    return df


def print_overview(df):
    """Print basic dataset statistics."""
    print("=" * 65)
    print("  NETWORK TRAFFIC ANALYSIS — DATASET OVERVIEW")
    print("=" * 65)
    print(f"  Total records        : {len(df):,}")
    print(f"  Time range           : {df['timestamp'].min()} to {df['timestamp'].max()}")
    print(f"  Unique source IPs    : {df['src_ip'].nunique()}")
    print(f"  Unique dest IPs      : {df['dst_ip'].nunique()}")
    print(f"  Protocols            : {', '.join(df['protocol'].unique())}")
    print(f"  Total bytes sent     : {df['bytes_sent'].sum():,.0f}")
    print(f"  Total bytes received : {df['bytes_received'].sum():,.0f}")
    print("=" * 65)


# ===========================================================================
# 2. ANOMALY DETECTION
# ===========================================================================

def detect_port_scans(df):
    """Flag IPs contacting many unique destination ports per hour."""
    hourly = (
        df.groupby(["src_ip", "hour"])["dst_port"]
        .nunique()
        .reset_index(name="unique_ports")
    )
    scanners = hourly[hourly["unique_ports"] >= PORT_SCAN_THRESHOLD]
    return scanners


def detect_brute_force(df):
    """Flag IPs with repeated SSH (port 22) connections."""
    ssh = df[df["dst_port"] == 22]
    hourly = (
        ssh.groupby(["src_ip", "hour"])
        .size()
        .reset_index(name="ssh_attempts")
    )
    brute = hourly[hourly["ssh_attempts"] >= BRUTE_FORCE_THRESHOLD]
    return brute


def detect_exfiltration(df):
    """Flag large outbound transfers during off-hours."""
    off_hours = df[
        (df["hour"] >= EXFIL_HOUR_START) & (df["hour"] <= EXFIL_HOUR_END)
    ]
    large = off_hours[off_hours["bytes_sent"] >= EXFIL_BYTES_THRESHOLD]
    return large


def detect_dns_tunneling(df):
    """Flag hosts making abnormally frequent DNS queries."""
    dns = df[df["dst_port"] == 53].copy()
    dns["ts_minute"] = dns["timestamp"].dt.floor("min")
    per_min = (
        dns.groupby(["src_ip", "ts_minute"])
        .size()
        .reset_index(name="queries_per_min")
    )
    tunneling = per_min[per_min["queries_per_min"] >= DNS_QUERY_RATE_THRESHOLD]
    return tunneling


def print_detection_results(port_scans, brute_force, exfil, dns_tunnel):
    """Print a summary of all detections."""
    print("\n" + "=" * 65)
    print("  ANOMALY DETECTION RESULTS")
    print("=" * 65)

    print("\n  [1] PORT SCANNING")
    if len(port_scans):
        for _, row in port_scans.iterrows():
            print(f"      ⚠  {row['src_ip']}  →  {row['unique_ports']} unique ports "
                  f"(hour {int(row['hour']):02d}:00)")
    else:
        print("      ✓  No port scanning detected.")

    print("\n  [2] BRUTE-FORCE SSH ATTEMPTS")
    if len(brute_force):
        for _, row in brute_force.iterrows():
            print(f"      ⚠  {row['src_ip']}  →  {row['ssh_attempts']} SSH attempts "
                  f"(hour {int(row['hour']):02d}:00)")
    else:
        print("      ✓  No brute-force activity detected.")

    print("\n  [3] DATA EXFILTRATION (off-hours large transfers)")
    if len(exfil):
        total_bytes = exfil["bytes_sent"].sum()
        unique_src = exfil["src_ip"].unique()
        unique_dst = exfil["dst_ip"].unique()
        print(f"      ⚠  {len(exfil)} suspicious transfers detected")
        print(f"         Source(s)     : {', '.join(unique_src)}")
        print(f"         Destination(s): {', '.join(unique_dst)}")
        print(f"         Total bytes   : {total_bytes:,.0f} ({total_bytes / 1e6:.1f} MB)")
    else:
        print("      ✓  No exfiltration indicators found.")

    print("\n  [4] DNS TUNNELING")
    if len(dns_tunnel):
        sources = dns_tunnel["src_ip"].unique()
        peak = dns_tunnel["queries_per_min"].max()
        print(f"      ⚠  Suspicious DNS activity from: {', '.join(sources)}")
        print(f"         Peak query rate: {peak} queries/min")
    else:
        print("      ✓  No DNS tunneling indicators found.")

    print("\n" + "=" * 65)


# ===========================================================================
# 3. VISUALISATION
# ===========================================================================

def set_plot_style():
    """Set a consistent dark-themed plot style."""
    plt.rcParams.update({
        "figure.facecolor": "#0d1117",
        "axes.facecolor": "#161b22",
        "axes.edgecolor": "#30363d",
        "axes.labelcolor": "#c9d1d9",
        "text.color": "#c9d1d9",
        "xtick.color": "#8b949e",
        "ytick.color": "#8b949e",
        "grid.color": "#21262d",
        "font.size": 10,
    })


def plot_traffic_volume_by_hour(df):
    """Bar chart of total traffic volume per hour."""
    fig, ax = plt.subplots(figsize=(12, 5))
    hourly = df.groupby("hour")["bytes_sent"].sum() / 1e6
    colors = ["#f85149" if h < 6 else "#58a6ff" for h in hourly.index]
    ax.bar(hourly.index, hourly.values, color=colors, edgecolor="#30363d", width=0.8)
    ax.set_xlabel("Hour of Day")
    ax.set_ylabel("Total Bytes Sent (MB)")
    ax.set_title("Traffic Volume by Hour — Off-Hours Highlighted in Red", fontweight="bold")
    ax.set_xticks(range(24))
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "01_traffic_by_hour.png"), dpi=150)
    plt.close()


def plot_protocol_distribution(df):
    """Pie chart of protocol distribution."""
    fig, ax = plt.subplots(figsize=(7, 7))
    proto_counts = df["protocol"].value_counts()
    colors = ["#58a6ff", "#3fb950", "#f0883e"]
    ax.pie(
        proto_counts.values,
        labels=proto_counts.index,
        autopct="%1.1f%%",
        colors=colors[:len(proto_counts)],
        startangle=140,
        textprops={"color": "#c9d1d9", "fontsize": 12},
        wedgeprops={"edgecolor": "#0d1117", "linewidth": 2},
    )
    ax.set_title("Protocol Distribution", fontweight="bold", fontsize=14)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "02_protocol_distribution.png"), dpi=150)
    plt.close()


def plot_top_talkers(df):
    """Horizontal bar chart of top source IPs by bytes sent."""
    fig, ax = plt.subplots(figsize=(10, 6))
    top = df.groupby("src_ip")["bytes_sent"].sum().nlargest(10).sort_values()
    top_mb = top / 1e6
    bars = ax.barh(top_mb.index, top_mb.values, color="#58a6ff", edgecolor="#30363d")
    # Highlight known attacker / exfil IPs
    for bar, ip in zip(bars, top_mb.index):
        if ip in ["45.33.32.156", "192.168.1.100"]:
            bar.set_color("#f85149")
    ax.set_xlabel("Bytes Sent (MB)")
    ax.set_title("Top 10 Source IPs by Data Volume — Anomalous IPs in Red", fontweight="bold")
    ax.grid(axis="x", alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "03_top_talkers.png"), dpi=150)
    plt.close()


def plot_port_scan_activity(df):
    """Scatter plot showing port scan pattern."""
    scan_traffic = df[df["label"] == "port_scan"]
    if scan_traffic.empty:
        return
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.scatter(
        scan_traffic["timestamp"], scan_traffic["dst_port"],
        c="#f85149", s=8, alpha=0.6, edgecolors="none"
    )
    ax.set_xlabel("Time")
    ax.set_ylabel("Destination Port")
    ax.set_title(
        f"Port Scan Pattern — {scan_traffic['src_ip'].iloc[0]} → "
        f"{scan_traffic['dst_ip'].iloc[0]}",
        fontweight="bold"
    )
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    ax.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "04_port_scan_scatter.png"), dpi=150)
    plt.close()


def plot_exfiltration_timeline(df):
    """Timeline of exfiltration-size transfers during off-hours."""
    exfil = df[
        (df["bytes_sent"] >= EXFIL_BYTES_THRESHOLD) &
        (df["hour"] >= EXFIL_HOUR_START) &
        (df["hour"] <= EXFIL_HOUR_END)
    ]
    if exfil.empty:
        return
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.scatter(
        exfil["timestamp"], exfil["bytes_sent"] / 1e6,
        c="#f0883e", s=60, alpha=0.8, edgecolors="#0d1117", linewidths=0.5
    )
    ax.set_xlabel("Time")
    ax.set_ylabel("Bytes Sent (MB)")
    ax.set_title(
        "Suspected Data Exfiltration — Large Transfers During Off-Hours",
        fontweight="bold"
    )
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    ax.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "05_exfiltration_timeline.png"), dpi=150)
    plt.close()


def plot_anomaly_breakdown(df):
    """Stacked bar chart showing normal vs anomaly types per hour."""
    fig, ax = plt.subplots(figsize=(12, 5))
    pivot = pd.crosstab(df["hour"], df["label"])
    color_map = {
        "normal": "#238636",
        "port_scan": "#f85149",
        "brute_force": "#da3633",
        "exfiltration": "#f0883e",
        "dns_tunneling": "#d2a8ff",
    }
    cols_ordered = [c for c in color_map if c in pivot.columns]
    pivot[cols_ordered].plot(
        kind="bar", stacked=True, ax=ax, width=0.85,
        color=[color_map[c] for c in cols_ordered],
        edgecolor="#0d1117", linewidth=0.3
    )
    ax.set_xlabel("Hour of Day")
    ax.set_ylabel("Number of Connections")
    ax.set_title("Connections by Hour — Normal vs Anomalous Traffic", fontweight="bold")
    ax.legend(loc="upper right", fontsize=8, framealpha=0.7)
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "06_anomaly_breakdown.png"), dpi=150)
    plt.close()


# ===========================================================================
# 4. MAIN
# ===========================================================================

def main():
    set_plot_style()

    # Load
    print(f"\nLoading data from {INPUT_FILE}...")
    df = load_data(INPUT_FILE)
    print_overview(df)

    # Detect
    port_scans = detect_port_scans(df)
    brute_force = detect_brute_force(df)
    exfil = detect_exfiltration(df)
    dns_tunnel = detect_dns_tunneling(df)
    print_detection_results(port_scans, brute_force, exfil, dns_tunnel)

    # Visualise
    print("\nGenerating visualisations...")
    plot_traffic_volume_by_hour(df)
    plot_protocol_distribution(df)
    plot_top_talkers(df)
    plot_port_scan_activity(df)
    plot_exfiltration_timeline(df)
    plot_anomaly_breakdown(df)
    print(f"  ✓ 6 charts saved to {OUTPUT_DIR}/\n")

    # Summary
    total_anomalies = len(df[df["label"] != "normal"])
    print("=" * 65)
    print("  RECOMMENDATIONS")
    print("=" * 65)
    print(f"""
  Based on {total_anomalies} anomalous events detected:

  1. BLOCK {port_scans['src_ip'].unique()[0] if len(port_scans) else 'N/A'}
     at the perimeter firewall — confirmed port scanning activity.

  2. ENFORCE rate-limiting on SSH (port 22) and consider
     key-based authentication only. Disable password login.

  3. INVESTIGATE outbound traffic from 192.168.1.100 (File Server)
     to {df[df['label'] == 'exfiltration']['dst_ip'].unique()[0] if len(df[df['label'] == 'exfiltration']) else 'N/A'} 
     during hours {EXFIL_HOUR_START:02d}:00–{EXFIL_HOUR_END:02d}:00.
     Potential data exfiltration.

  4. AUDIT DNS query patterns from 192.168.1.12 (Finance workstation).
     Query frequency exceeds normal thresholds — possible DNS tunneling
     for covert data transfer.

  5. DEPLOY network segmentation to isolate the file server
     and restrict direct outbound internet access.
""")


if __name__ == "__main__":
    main()
