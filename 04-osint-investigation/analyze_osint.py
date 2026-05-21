"""
analyze_osint.py
Processes OSINT artifacts collected during the investigation of
"PacificBridge Solutions Inc." and produces:

  1. Investigation timeline visualization
  2. Entity relationship network diagram
  3. Red flag severity matrix
  4. Digital footprint activity chart
  5. Investigation confidence scorecard
  6. Console investigation report

Designed as a CTF-style walkthrough demonstrating structured
OSINT methodology for cybersecurity portfolios.

Usage:
    python generate_osint_artifacts.py   # (run first)
    python analyze_osint.py
"""

import os
import json
import csv
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.dates as mdates
import numpy as np
from datetime import datetime

DATA_DIR = "data"
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)


# ===========================================================================
# 1. LOAD ARTIFACTS
# ===========================================================================

def load_json(filename):
    with open(os.path.join(DATA_DIR, filename)) as f:
        return json.load(f)


def load_all():
    artifacts = {
        "sec": load_json("artifact_01_sec_registration.json"),
        "whois": load_json("artifact_02_whois.json"),
        "wayback": load_json("artifact_03_wayback.json"),
        "social": load_json("artifact_04_social_media.json"),
        "philgeps": load_json("artifact_05_philgeps.json"),
        "address": load_json("artifact_06_address.json"),
        "entities": load_json("artifact_07_entity_links.json"),
    }
    timeline = pd.read_csv(os.path.join(DATA_DIR, "osint_timeline.csv"), parse_dates=["date"])
    network = pd.read_csv(os.path.join(DATA_DIR, "entity_network.csv"))
    return artifacts, timeline, network


def set_plot_style():
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


# ===========================================================================
# 2. RED FLAG ANALYSIS
# ===========================================================================

RED_FLAG_CATEGORIES = {
    "Corporate Registration": [
        ("Company registered only 10 months before bid", 4),
        ("Paid-up capital far below project value", 5),
        ("Minimum incorporators (3 — legal floor)", 2),
        ("Co-incorporator linked to revoked company", 5),
    ],
    "Digital Presence": [
        ("Domain registered on personal Gmail", 3),
        ("Domain expired and not renewed", 4),
        ("Website used stock photos only", 3),
        ("No project portfolio shown", 4),
        ("Website went Under Construction", 3),
    ],
    "Professional Credibility": [
        ("CEO's prior role was retail computer sales", 5),
        ("No LinkedIn company page", 3),
        ("Zero employee profiles on any platform", 4),
        ("No professional certifications", 4),
        ("43 Facebook followers, inactive since 2023", 3),
    ],
    "Procurement History": [
        ("Zero prior bids in PhilGEPS", 5),
        ("Zero government contract awards", 5),
        ("Classified as Micro enterprise for PHP 45M bid", 5),
        ("PhilGEPS registered 7 months after incorporation", 2),
    ],
    "Physical Presence": [
        ("Registered address is a virtual office", 5),
        ("No signage at registered address", 4),
        ("Building reception has no record of company", 4),
    ],
}


def compute_red_flag_scores():
    """Compute severity scores per category."""
    results = {}
    total_flags = 0
    total_score = 0
    for category, flags in RED_FLAG_CATEGORIES.items():
        cat_score = sum(s for _, s in flags)
        cat_count = len(flags)
        results[category] = {
            "count": cat_count,
            "total_severity": cat_score,
            "avg_severity": round(cat_score / cat_count, 1),
            "flags": flags,
        }
        total_flags += cat_count
        total_score += cat_score
    return results, total_flags, total_score


def compute_confidence_score(total_flags, total_score, max_possible_score):
    """
    Confidence that the entity is a shell/fraudulent company.
    Based on weighted red flag accumulation.
    """
    confidence = min(total_score / max_possible_score * 100, 99)
    return round(confidence, 1)


# ===========================================================================
# 3. PRINT INVESTIGATION REPORT
# ===========================================================================

def print_report(artifacts, flag_results, total_flags, total_score, confidence):
    print("\n" + "=" * 70)
    print("  ╔══════════════════════════════════════════════════════════╗")
    print("  ║        OSINT INVESTIGATION REPORT                      ║")
    print("  ║        Subject: PacificBridge Solutions Inc.            ║")
    print("  ║        Classification: CONFIDENTIAL                    ║")
    print("  ╚══════════════════════════════════════════════════════════╝")
    print("=" * 70)

    print(f"\n  INVESTIGATION METADATA")
    print(f"  {'─' * 50}")
    print(f"    Case initiated   : 2026-04-15")
    print(f"    Subject entity   : PacificBridge Solutions Inc.")
    print(f"    SEC Reg. No.     : CS-2023-07812")
    print(f"    Context          : PHP 45M IT Infrastructure Bid")
    print(f"    Trigger          : Anonymous tip to BAC Secretariat")
    print(f"    Methodology      : Open Source Intelligence (OSINT)")
    print(f"    Artifacts        : 7 sources analyzed")

    print(f"\n\n  EXECUTIVE FINDING")
    print(f"  {'─' * 50}")
    print(f"    Confidence Score : {confidence}% — SHELL ENTITY (PROBABLE)")
    print(f"    Red Flags Found  : {total_flags}")
    print(f"    Severity Score   : {total_score} / {5 * total_flags}")

    print(f"\n\n  RED FLAG ANALYSIS BY CATEGORY")
    print(f"  {'─' * 50}")
    for category, data in flag_results.items():
        severity_bar = "█" * data["total_severity"]
        print(f"\n    [{category}]  ({data['count']} flags, severity: {data['total_severity']})")
        for flag_text, severity in data["flags"]:
            dots = "●" * severity + "○" * (5 - severity)
            print(f"      {dots}  {flag_text}")

    # OSINT source breakdown
    print(f"\n\n  INTELLIGENCE SOURCES")
    print(f"  {'─' * 50}")
    sources = [
        ("SEC Company Registration", "Corporate records", "Government DB"),
        ("WHOIS Domain Lookup", "Domain ownership", "Public Registry"),
        ("Wayback Machine", "Historical web content", "Web Archive"),
        ("Social Media (LinkedIn, FB)", "Digital footprint", "Social Platforms"),
        ("PhilGEPS", "Procurement history", "Government DB"),
        ("Google Maps / Street View", "Physical verification", "Geospatial"),
        ("Cross-Reference Analysis", "Entity relationships", "Multi-Source"),
    ]
    for name, purpose, source_type in sources:
        print(f"    ✓ {name:<35s}  {purpose:<25s}  [{source_type}]")

    # Key findings per artifact
    print(f"\n\n  ARTIFACT-BY-ARTIFACT FINDINGS")
    print(f"  {'─' * 50}")

    print(f"\n    ARTIFACT 1 — SEC Registration")
    print(f"    Company exists on paper but was incorporated only 10 months")
    print(f"    before submitting a PHP 45M bid. Paid-up capital is PHP 1.25M")
    print(f"    — less than 3% of the project value.")

    print(f"\n    ARTIFACT 2 — WHOIS")
    print(f"    Domain registered to personal Gmail (not corporate email).")
    print(f"    Domain has EXPIRED and was not renewed — the company's own")
    print(f"    website no longer exists.")

    print(f"\n    ARTIFACT 3 — Web Archive")
    print(f"    Website consisted of a single page with stock photos. No")
    print(f"    project portfolio, no team information, no client testimonials.")
    print(f"    Site went 'Under Construction' before domain expiry.")

    print(f"\n    ARTIFACT 4 — Social Media")
    print(f"    No LinkedIn company page. CEO has 87 connections, zero posts,")
    print(f"    and prior experience limited to retail computer sales.")
    print(f"    Facebook page has 43 followers and has been dormant since 2023.")

    print(f"\n    ARTIFACT 5 — PhilGEPS")
    print(f"    Zero bid history. Zero contract awards. Registered as 'Micro'")
    print(f"    enterprise — bidding on a project 36x its paid-up capital.")

    print(f"\n    ARTIFACT 6 — Physical Address")
    print(f"    Registered address is a PHP 2,500/month virtual office.")
    print(f"    No signage. Building reception has no record of the company.")

    print(f"\n    ARTIFACT 7 — Entity Connections")
    print(f"    Co-incorporator Angela Tan was Treasurer of CebuTech Builders")
    print(f"    Corp., whose SEC registration was REVOKED for non-compliance.")
    print(f"    Pattern suggests serial company registration for bidding.")

    print(f"\n\n  {'=' * 70}")
    print(f"  CONCLUSION & RECOMMENDATION")
    print(f"  {'=' * 70}")
    print(f"""
    Based on {total_flags} red flags across 7 OSINT sources, this
    investigation finds with {confidence}% confidence that PacificBridge
    Solutions Inc. is a PROBABLE SHELL ENTITY established primarily
    for the purpose of participating in government procurement.

    RECOMMENDED ACTIONS:
    1. BAC to issue a Notice of Disqualification under Section 23.1(b)
       of RA 9184 IRR — failure to meet eligibility requirements.

    2. Refer findings to the City Legal Office for evaluation of
       potential violations under:
       - RA 3019 (Anti-Graft and Corrupt Practices Act)
       - RA 9184 Section 65 (Prohibited Acts in Procurement)

    3. Forward intelligence package to PhilGEPS for possible
       blacklisting proceedings.

    4. Recommend BAC adopt OSINT due diligence as standard practice
       for bidders on projects exceeding PHP 10M.
    """)


# ===========================================================================
# 4. VISUALISATION
# ===========================================================================

def plot_investigation_timeline(timeline):
    """Horizontal timeline of all events."""
    fig, ax = plt.subplots(figsize=(14, 7))

    category_colors = {
        "Education": "#3498db",
        "Business Registration": "#e67e22",
        "Digital Footprint": "#9b59b6",
        "Procurement": "#2ecc71",
        "Investigation": "#e74c3c",
    }

    y_positions = list(range(len(timeline)))
    colors = [category_colors.get(c, "#999") for c in timeline["category"]]

    ax.barh(y_positions, [1] * len(timeline), left=0, height=0.6,
            color=colors, alpha=0.0)

    for i, (_, row) in enumerate(timeline.iterrows()):
        color = category_colors.get(row["category"], "#999")
        ax.plot(row["date"], i, "o", color=color, markersize=10, zorder=5)
        ax.text(
            row["date"], i + 0.3,
            f"  {row['event']}",
            fontsize=7.5, va="center", color="#c9d1d9"
        )

    ax.set_yticks([])
    ax.set_xlabel("Date")
    ax.set_title("Investigation Timeline — PacificBridge Solutions Inc.",
                 fontweight="bold", fontsize=13)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    plt.xticks(rotation=30)

    legend_patches = [mpatches.Patch(color=c, label=l)
                      for l, c in category_colors.items()]
    ax.legend(handles=legend_patches, loc="lower right", fontsize=8)

    ax.grid(axis="x", alpha=0.2)
    ax.invert_yaxis()
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "01_investigation_timeline.png"), dpi=150)
    plt.close()


def plot_entity_network(network):
    """Node-link diagram of entity relationships."""
    fig, ax = plt.subplots(figsize=(14, 10))
    ax.set_xlim(-1.5, 1.5)
    ax.set_ylim(-1.5, 1.5)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("Entity Relationship Map — PacificBridge Solutions Inc.",
                 fontweight="bold", fontsize=14, pad=20)

    # Position nodes manually for clean layout
    positions = {
        "PacificBridge Solutions Inc.": (0, 0),
        "Ricardo M. Villanueva": (-0.8, 0.7),
        "Angela S. Tan": (0.8, 0.7),
        "Mark Joseph D. Reyes": (0, 1.1),
        "CebuTech Builders Corp.": (1.3, 0.2),
        "MegaTech Computer Sales": (-1.3, 0.2),
        "pacificbridgesolutions.com.ph": (-0.9, -0.6),
        "FlexSpace Cebu (Virtual Office)": (0.9, -0.6),
        "Facebook Page (43 followers)": (-0.4, -1.0),
        "PhilGEPS PGR-2024-00456781": (0.4, -1.0),
        "PHP 45M IT Infrastructure Bid": (0, -1.3),
        "SEC — REVOKED": (1.3, -0.3),
        "r.villanueva@gmail.com": (-1.3, -0.4),
        "LinkedIn (87 connections)": (-1.1, 1.1),
    }

    type_colors = {
        "Corporate Officer": "#e67e22",
        "Employment": "#3498db",
        "Digital Asset": "#9b59b6",
        "Address": "#2ecc71",
        "Government Record": "#e74c3c",
        "Procurement": "#f39c12",
    }

    # Draw edges
    for _, row in network.iterrows():
        src = row["source_entity"]
        tgt = row["target_entity"]
        if src in positions and tgt in positions:
            x1, y1 = positions[src]
            x2, y2 = positions[tgt]
            color = type_colors.get(row["type"], "#555")
            ax.plot([x1, x2], [y1, y2], "-", color=color, alpha=0.5, linewidth=1.5)

    # Draw nodes
    for node, (x, y) in positions.items():
        if node == "PacificBridge Solutions Inc.":
            ax.plot(x, y, "o", color="#e74c3c", markersize=22, zorder=10)
            ax.text(x, y - 0.15, node, fontsize=8, ha="center",
                    fontweight="bold", color="#e74c3c")
        elif node == "SEC — REVOKED":
            ax.plot(x, y, "X", color="#e74c3c", markersize=14, zorder=10)
            ax.text(x, y - 0.1, node, fontsize=7, ha="center", color="#e74c3c")
        else:
            ax.plot(x, y, "o", color="#58a6ff", markersize=10, zorder=10)
            # Wrap long names
            display = node if len(node) < 30 else node[:27] + "..."
            ax.text(x, y - 0.1, display, fontsize=7, ha="center", color="#c9d1d9")

    legend_patches = [mpatches.Patch(color=c, label=l)
                      for l, c in type_colors.items()]
    ax.legend(handles=legend_patches, loc="upper left", fontsize=8,
              framealpha=0.7, facecolor="#161b22")

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "02_entity_network.png"), dpi=150)
    plt.close()


def plot_red_flag_severity(flag_results):
    """Horizontal stacked bar of red flag severity by category."""
    fig, ax = plt.subplots(figsize=(10, 5))

    categories = list(flag_results.keys())
    scores = [flag_results[c]["total_severity"] for c in categories]
    counts = [flag_results[c]["count"] for c in categories]

    colors = ["#e74c3c", "#e67e22", "#9b59b6", "#3498db", "#2ecc71"]
    bars = ax.barh(categories, scores, color=colors[:len(categories)],
                   edgecolor="#0d1117", linewidth=0.5)

    for bar, count, score in zip(bars, counts, scores):
        ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height() / 2,
                f"{count} flags (severity: {score})",
                va="center", fontsize=9, color="#c9d1d9")

    ax.set_xlabel("Cumulative Severity Score")
    ax.set_title("Red Flag Analysis by Category",
                 fontweight="bold", fontsize=13)
    ax.grid(axis="x", alpha=0.2)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "03_red_flag_severity.png"), dpi=150)
    plt.close()


def plot_digital_activity(timeline):
    """Scatter plot showing digital activity (or lack thereof)."""
    digital = timeline[timeline["category"] == "Digital Footprint"].copy()

    fig, ax = plt.subplots(figsize=(12, 4))
    ax.scatter(digital["date"], [1] * len(digital),
               c="#9b59b6", s=120, zorder=5, edgecolors="#0d1117")

    for _, row in digital.iterrows():
        ax.annotate(
            row["event"], xy=(row["date"], 1),
            xytext=(0, 20), textcoords="offset points",
            fontsize=7, color="#c9d1d9", ha="center", rotation=25,
            arrowprops=dict(arrowstyle="-", color="#555", lw=0.5)
        )

    # Mark the gap
    ax.axvspan(datetime(2023, 11, 15), datetime(2026, 3, 1),
               alpha=0.1, color="#e74c3c")
    ax.text(datetime(2024, 10, 1), 1.15, "~28 months of\ndigital silence",
            fontsize=9, color="#e74c3c", ha="center", fontweight="bold")

    ax.set_yticks([])
    ax.set_title("Digital Footprint Activity — PacificBridge Solutions Inc.",
                 fontweight="bold", fontsize=13)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    ax.grid(axis="x", alpha=0.2)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "04_digital_activity.png"), dpi=150)
    plt.close()


def plot_confidence_scorecard(confidence, total_flags, total_score):
    """Visual scorecard showing overall investigation confidence."""
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis("off")

    # Background card
    card = mpatches.FancyBboxPatch(
        (0.5, 0.5), 9, 5, boxstyle="round,pad=0.3",
        facecolor="#161b22", edgecolor="#30363d", linewidth=2
    )
    ax.add_patch(card)

    ax.text(5, 5, "INVESTIGATION CONFIDENCE SCORE",
            fontsize=14, fontweight="bold", ha="center", va="center", color="#c9d1d9")

    # Confidence meter
    meter_width = 7
    meter_x = 1.5
    meter_y = 3.5
    ax.add_patch(mpatches.FancyBboxPatch(
        (meter_x, meter_y), meter_width, 0.6,
        boxstyle="round,pad=0.1", facecolor="#21262d", edgecolor="#30363d"
    ))
    fill_width = meter_width * (confidence / 100)
    fill_color = "#e74c3c" if confidence > 70 else "#e67e22" if confidence > 40 else "#2ecc71"
    ax.add_patch(mpatches.FancyBboxPatch(
        (meter_x, meter_y), fill_width, 0.6,
        boxstyle="round,pad=0.1", facecolor=fill_color, edgecolor="none"
    ))
    ax.text(meter_x + meter_width / 2, meter_y + 0.3,
            f"{confidence}%", fontsize=18, fontweight="bold",
            ha="center", va="center", color="white")

    ax.text(5, 2.7, "PROBABLE SHELL ENTITY",
            fontsize=16, fontweight="bold", ha="center", color="#e74c3c")

    ax.text(3, 1.8, f"Red Flags: {total_flags}", fontsize=11,
            ha="center", color="#8b949e")
    ax.text(7, 1.8, f"Severity: {total_score}", fontsize=11,
            ha="center", color="#8b949e")

    ax.text(5, 1.0, "Recommendation: DISQUALIFY from procurement process",
            fontsize=10, ha="center", color="#f0883e", style="italic")

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "05_confidence_scorecard.png"), dpi=150)
    plt.close()


# ===========================================================================
# 5. MAIN
# ===========================================================================

def main():
    set_plot_style()

    print("\nLoading OSINT artifacts...")
    artifacts, timeline, network = load_all()
    print(f"  Artifacts: {len(artifacts)} | Timeline events: {len(timeline)} | Network edges: {len(network)}")

    # Red flag analysis
    flag_results, total_flags, total_score = compute_red_flag_scores()
    max_possible = total_flags * 5
    confidence = compute_confidence_score(total_flags, total_score, max_possible)

    # Report
    print_report(artifacts, flag_results, total_flags, total_score, confidence)

    # Charts
    print("\nGenerating visualisations...")
    plot_investigation_timeline(timeline)
    plot_entity_network(network)
    plot_red_flag_severity(flag_results)
    plot_digital_activity(timeline)
    plot_confidence_scorecard(confidence, total_flags, total_score)
    print(f"  ✓ 5 charts saved to {OUTPUT_DIR}/\n")


if __name__ == "__main__":
    main()
