"""
analyze_ai_governance.py
Comparative analysis of AI governance frameworks with focus on the
Philippines' readiness and policy gaps.

Produces:
  - 7 publication-quality charts
  - Console policy brief with findings and recommendations
  - output/policy_brief.txt — formatted brief for policymakers

Usage:
    python generate_ai_governance_data.py   # (run first)
    python analyze_ai_governance.py
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.dates as mdates
import numpy as np
from datetime import datetime

DATA_DIR = "data"
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def load_data():
    readiness = pd.read_csv(os.path.join(DATA_DIR, "asean_ai_readiness.csv"))
    gaps = pd.read_csv(os.path.join(DATA_DIR, "ph_governance_gaps.csv"))
    timeline = pd.read_csv(os.path.join(DATA_DIR, "ph_ai_timeline.csv"), parse_dates=["date"])
    dimensions = pd.read_csv(os.path.join(DATA_DIR, "policy_dimensions.csv"))
    return readiness, gaps, timeline, dimensions


def set_plot_style():
    plt.rcParams.update({
        "figure.facecolor": "#fafafa",
        "axes.facecolor": "#ffffff",
        "axes.edgecolor": "#cccccc",
        "axes.labelcolor": "#333333",
        "text.color": "#333333",
        "xtick.color": "#555555",
        "ytick.color": "#555555",
        "grid.color": "#eeeeee",
        "font.size": 10,
        "font.family": "sans-serif",
    })


# ===========================================================================
# VISUALISATIONS
# ===========================================================================

def plot_asean_readiness_bar(readiness):
    """Horizontal bar chart of ASEAN AI readiness scores."""
    df = readiness.sort_values("readiness_score", ascending=True)
    fig, ax = plt.subplots(figsize=(10, 7))

    colors = ["#0052b4" if c == "Philippines" else "#2980b9" if s > 50
              else "#85c1e9" for c, s in zip(df["country"], df["readiness_score"])]

    bars = ax.barh(df["country"], df["readiness_score"], color=colors,
                   edgecolor="#1a5276", linewidth=0.3)

    # Highlight Philippines
    ph_idx = df[df["country"] == "Philippines"].index[0]
    for i, bar in enumerate(bars):
        if df.iloc[i]["country"] == "Philippines":
            bar.set_edgecolor("#c0392b")
            bar.set_linewidth(2.5)

    # Add rank labels
    for i, (_, row) in enumerate(df.iterrows()):
        ax.text(row["readiness_score"] + 0.5, i,
                f'#{int(row["global_rank"])}',
                va="center", fontsize=8, color="#555")

    ax.set_xlabel("AI Readiness Score (0-100)")
    ax.set_title("ASEAN Government AI Readiness Index 2025\nPhilippines Ranked 65th Globally",
                 fontweight="bold", fontsize=13)
    ax.set_xlim(0, 95)
    ax.grid(axis="x", alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "01_asean_readiness.png"), dpi=150)
    plt.close()


def plot_readiness_pillars(readiness):
    """Grouped bar chart of readiness pillars for top 6 ASEAN."""
    top6 = readiness.nlargest(6, "readiness_score")
    fig, ax = plt.subplots(figsize=(12, 6))

    x = np.arange(len(top6))
    width = 0.25

    ax.bar(x - width, top6["government_pillar"], width, label="Government",
           color="#2c3e50", edgecolor="#1a252f")
    ax.bar(x, top6["technology_pillar"], width, label="Technology",
           color="#2980b9", edgecolor="#1a5276")
    ax.bar(x + width, top6["data_infrastructure_pillar"], width,
           label="Data & Infrastructure", color="#27ae60", edgecolor="#1e8449")

    ax.set_xticks(x)
    ax.set_xticklabels(top6["country"], fontsize=10)
    ax.set_ylabel("Pillar Score (0-100)")
    ax.set_title("AI Readiness by Pillar — Top 6 ASEAN Countries",
                 fontweight="bold", fontsize=13)
    ax.legend(fontsize=9)
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "02_readiness_pillars.png"), dpi=150)
    plt.close()


def plot_governance_gap_severity(gaps):
    """Horizontal bar chart of Philippine governance gap severity."""
    df = gaps.sort_values("severity", ascending=True)
    fig, ax = plt.subplots(figsize=(11, 6))

    colors = ["#c0392b" if s == 5 else "#e67e22" if s == 4
              else "#f1c40f" for s in df["severity"]]

    ax.barh(df["dimension"], df["severity"], color=colors,
            edgecolor="#333", linewidth=0.3)
    ax.set_xlabel("Gap Severity (1-5)")
    ax.set_title("Philippine AI Governance Gaps by Severity",
                 fontweight="bold", fontsize=13)
    ax.set_xlim(0, 5.5)
    ax.grid(axis="x", alpha=0.3)

    legend_patches = [
        mpatches.Patch(color="#c0392b", label="Critical (5)"),
        mpatches.Patch(color="#e67e22", label="High (4)"),
        mpatches.Patch(color="#f1c40f", label="Moderate (3)"),
    ]
    ax.legend(handles=legend_patches, loc="lower right", fontsize=9)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "03_gap_severity.png"), dpi=150)
    plt.close()


def plot_radar_comparison(dimensions):
    """Radar chart comparing Philippines vs Singapore, NZ, and ASEAN average."""
    categories = dimensions["dimension"].tolist()
    N = len(categories)
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(9, 9), subplot_kw=dict(polar=True))
    ax.set_facecolor("#fafafa")

    comparisons = {
        "Philippines": ("#c0392b", dimensions["Philippines"].tolist()),
        "Singapore": ("#2980b9", dimensions["Singapore"].tolist()),
        "New Zealand": ("#27ae60", dimensions["New_Zealand"].tolist()),
        "ASEAN Average": ("#8e44ad", dimensions["ASEAN_Avg"].tolist()),
    }

    for label, (color, values) in comparisons.items():
        values_closed = values + values[:1]
        ax.plot(angles, values_closed, "o-", linewidth=2, label=label,
                color=color, markersize=5)
        ax.fill(angles, values_closed, alpha=0.05, color=color)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, fontsize=8)
    ax.set_ylim(0, 5.5)
    ax.set_yticks([1, 2, 3, 4, 5])
    ax.set_yticklabels(["1", "2", "3", "4", "5"], fontsize=7, color="#888")
    ax.set_title("AI Governance Maturity — Philippines vs Benchmarks",
                 fontweight="bold", fontsize=13, pad=25)
    ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1), fontsize=9)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "04_radar_comparison.png"), dpi=150,
                bbox_inches="tight")
    plt.close()


def plot_policy_timeline(timeline):
    """Vertical timeline of Philippine AI policy milestones."""
    fig, ax = plt.subplots(figsize=(14, 8))

    category_colors = {
        "Legislation": "#c0392b",
        "Strategy": "#2980b9",
        "International": "#27ae60",
        "Event": "#8e44ad",
        "Enforcement": "#e67e22",
        "Assessment": "#1abc9c",
    }

    for i, (_, row) in enumerate(timeline.iterrows()):
        color = category_colors.get(row["category"], "#999")
        side = 1 if i % 2 == 0 else -1
        ax.plot(row["date"], 0, "o", color=color, markersize=10, zorder=5)
        ax.annotate(
            row["event"],
            xy=(row["date"], 0),
            xytext=(0, side * (40 + (i % 3) * 20)),
            textcoords="offset points",
            fontsize=7, color="#333", ha="center",
            arrowprops=dict(arrowstyle="-", color="#999", lw=0.5),
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
                      edgecolor=color, alpha=0.9),
        )

    ax.axhline(y=0, color="#ccc", linewidth=1)
    ax.set_yticks([])
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
    plt.xticks(rotation=30)
    ax.set_title("Philippine AI Policy Timeline — 2012 to 2026",
                 fontweight="bold", fontsize=13)

    legend_patches = [mpatches.Patch(color=c, label=l)
                      for l, c in category_colors.items()]
    ax.legend(handles=legend_patches, loc="lower right", fontsize=8, ncol=3)
    ax.grid(axis="x", alpha=0.2)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "05_policy_timeline.png"), dpi=150)
    plt.close()


def plot_regulatory_readiness_matrix(readiness):
    """Matrix showing which ASEAN countries have key governance building blocks."""
    blocks = ["has_national_strategy", "has_binding_ai_law",
              "has_data_protection_law", "has_cybersecurity_law", "dedicated_ai_agency"]
    block_labels = ["National AI\nStrategy", "Binding\nAI Law",
                    "Data Protection\nLaw", "Cybersecurity\nLaw", "Dedicated\nAI Agency"]

    countries = readiness.sort_values("readiness_score", ascending=False)["country"].tolist()
    matrix = []
    for c in countries:
        row = readiness[readiness["country"] == c].iloc[0]
        matrix.append([1 if row[b] else 0 for b in blocks])

    matrix = np.array(matrix)

    fig, ax = plt.subplots(figsize=(10, 7))
    cmap = plt.cm.colors.ListedColormap(["#f5b7b1", "#82e0aa"])
    ax.imshow(matrix, cmap=cmap, aspect="auto")

    ax.set_xticks(range(len(block_labels)))
    ax.set_yticks(range(len(countries)))
    ax.set_xticklabels(block_labels, fontsize=9)
    ax.set_yticklabels(countries, fontsize=10)

    for i in range(len(countries)):
        for j in range(len(blocks)):
            symbol = "✓" if matrix[i, j] else "✗"
            color = "#1e8449" if matrix[i, j] else "#c0392b"
            ax.text(j, i, symbol, ha="center", va="center",
                    fontsize=14, fontweight="bold", color=color)

    ax.set_title("ASEAN AI Governance Building Blocks",
                 fontweight="bold", fontsize=13)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "06_regulatory_matrix.png"), dpi=150)
    plt.close()


def plot_oecd_digital_govt(readiness):
    """Bar chart of OECD Digital Government Index scores."""
    df = readiness.dropna(subset=["oecd_digital_govt_score"])
    df = df.sort_values("oecd_digital_govt_score", ascending=True)

    fig, ax = plt.subplots(figsize=(9, 5))
    colors = ["#0052b4" if c == "Philippines" else "#85c1e9"
              for c in df["country"]]

    bars = ax.barh(df["country"], df["oecd_digital_govt_score"],
                   color=colors, edgecolor="#1a5276", linewidth=0.3)

    # ASEAN average line
    avg = 0.37
    ax.axvline(x=avg, color="#e67e22", linewidth=2, linestyle="--", label=f"ASEAN Avg: {avg}")

    for i, bar in enumerate(bars):
        if df.iloc[i]["country"] == "Philippines":
            bar.set_edgecolor("#c0392b")
            bar.set_linewidth(2.5)

    ax.set_xlabel("OECD Digital Government Index Score (0-1)")
    ax.set_title("Digital Government Readiness — OECD 2025 Index\nPhilippines Scores 0.28 (Below ASEAN Average)",
                 fontweight="bold", fontsize=12)
    ax.legend(fontsize=9)
    ax.set_xlim(0, 0.85)
    ax.grid(axis="x", alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "07_oecd_digital_govt.png"), dpi=150)
    plt.close()


# ===========================================================================
# POLICY BRIEF (TEXT OUTPUT)
# ===========================================================================

def write_policy_brief(readiness, gaps, dimensions):
    ph = readiness[readiness["country"] == "Philippines"].iloc[0]
    sg = readiness[readiness["country"] == "Singapore"].iloc[0]

    filepath = os.path.join(OUTPUT_DIR, "policy_brief.txt")
    with open(filepath, "w") as f:
        f.write("=" * 72 + "\n")
        f.write("  POLICY BRIEF\n")
        f.write("  AI Governance Frameworks for the Philippines:\n")
        f.write("  Gaps, Benchmarks, and a Path Forward\n")
        f.write("=" * 72 + "\n\n")
        f.write("  Prepared for   : Philippine policymakers and legislative staff\n")
        f.write("  Date           : May 2026\n")
        f.write("  Author         : [Your Name]\n")
        f.write("  Affiliation    : Master's in Contemporary International Studies\n")
        f.write("                   Institute Pacific, New Zealand\n\n")
        f.write("-" * 72 + "\n\n")

        f.write("  EXECUTIVE SUMMARY\n\n")
        f.write("  The Philippines ranks 65th globally in AI readiness — behind\n")
        f.write("  Singapore (2nd), Malaysia (23rd), Thailand (37th), Indonesia\n")
        f.write("  (42nd), and Vietnam (59th) within ASEAN alone. While the\n")
        f.write("  government has adopted multiple AI roadmaps and strategies, the\n")
        f.write("  country lacks a binding legal framework for AI governance, a\n")
        f.write("  dedicated institutional authority, and a risk classification\n")
        f.write("  system for AI applications.\n\n")
        f.write("  As 2026 ASEAN Chair, the Philippines has both the opportunity\n")
        f.write("  and obligation to advance regional AI governance — but credible\n")
        f.write("  regional leadership requires domestic institutional readiness.\n\n")
        f.write("  This brief identifies 10 governance gaps, benchmarks them\n")
        f.write("  against ASEAN peers and global leaders, and proposes a phased\n")
        f.write("  policy roadmap for Philippine AI governance.\n\n")

        f.write("-" * 72 + "\n\n")
        f.write("  KEY DATA POINTS\n\n")
        f.write(f"  • Global AI Readiness Rank     : {int(ph['global_rank'])} / 193\n")
        f.write(f"  • Readiness Score              : {ph['readiness_score']} / 100\n")
        f.write(f"  • Government Pillar            : {ph['government_pillar']} / 100\n")
        f.write(f"  • OECD Digital Govt Index       : {ph['oecd_digital_govt_score']} / 1.0\n")
        f.write(f"  • ASEAN Digital Govt Average    : 0.37 / 1.0\n")
        f.write(f"  • Gap from Singapore            : {sg['readiness_score'] - ph['readiness_score']:.1f} points\n")
        f.write(f"  • Binding AI legislation        : None\n")
        f.write(f"  • Dedicated AI authority         : None\n\n")

        f.write("-" * 72 + "\n\n")
        f.write("  GOVERNANCE GAPS (10 DIMENSIONS)\n\n")
        for _, g in gaps.iterrows():
            severity_dots = "●" * g["severity"] + "○" * (5 - g["severity"])
            f.write(f"  {severity_dots}  {g['dimension']}\n")
            f.write(f"           Current: {g['current_state']}\n")
            f.write(f"           Gap:     {g['gap']}\n")
            f.write(f"           Bench:   {g['benchmark']}\n\n")

        f.write("-" * 72 + "\n\n")
        f.write("  POLICY RECOMMENDATIONS\n\n")

        f.write("  PHASE 1 — IMMEDIATE (2026)\n")
        f.write("  ──────────────────────────\n")
        f.write("  1. Finalize and publish the DEPDev AI Governance Framework\n")
        f.write("     as announced at the 2026 National Innovation Day.\n\n")
        f.write("  2. Designate a single coordinating authority for AI governance\n")
        f.write("     (recommended: DEPDev, with DICT as implementing agency).\n\n")
        f.write("  3. Issue an Executive Order requiring all government agencies\n")
        f.write("     to inventory existing and planned AI deployments.\n\n")

        f.write("  PHASE 2 — SHORT-TERM (2026-2027)\n")
        f.write("  ────────────────────────────────\n")
        f.write("  4. Draft a Philippine AI Governance Act adopting risk-based\n")
        f.write("     classification aligned with the ASEAN Guide and EU AI Act\n")
        f.write("     tiered model.\n\n")
        f.write("  5. Develop a Philippine Government Data Strategy to raise\n")
        f.write("     the OECD Digital Government score from 0.28 toward the\n")
        f.write("     ASEAN average of 0.37.\n\n")
        f.write("  6. Adopt a Philippine Algorithm Charter modeled on New\n")
        f.write("     Zealand's, requiring transparency for government AI.\n\n")
        f.write("  7. Mandate AI literacy modules in CSC career development\n")
        f.write("     programs for all senior government officials.\n\n")

        f.write("  PHASE 3 — MEDIUM-TERM (2027-2028)\n")
        f.write("  ─────────────────────────────────\n")
        f.write("  8. Establish a National AI Ethics Board with review authority\n")
        f.write("     over high-risk government AI applications.\n\n")
        f.write("  9. Issue DBM-GPPB procurement guidelines for AI solutions\n")
        f.write("     under RA 9184, including explainability and bias testing\n")
        f.write("     requirements.\n\n")
        f.write("  10. Amend RA 10175 (Cybercrime Prevention Act) to address\n")
        f.write("      AI-specific threats: adversarial attacks, deepfakes,\n")
        f.write("      and automated social engineering.\n\n")

        f.write("-" * 72 + "\n\n")
        f.write("  THE ASEAN CHAIR OPPORTUNITY\n\n")
        f.write("  The Philippines assumed the ASEAN Chairmanship on 1 January\n")
        f.write("  2026 under the theme \"Navigating Our Future Together.\" This\n")
        f.write("  provides a unique window to:\n\n")
        f.write("  • Champion the ASEAN Responsible AI Roadmap 2025-2030\n")
        f.write("  • Propose harmonized AI risk classification across ASEAN\n")
        f.write("  • Host an ASEAN AI Governance Summit (Cebu or Manila)\n")
        f.write("  • Demonstrate domestic implementation as credibility signal\n\n")
        f.write("  Regional leadership without domestic readiness produces\n")
        f.write("  declarations without implementation. The domestic framework\n")
        f.write("  must advance in parallel with ASEAN commitments.\n\n")

        f.write("-" * 72 + "\n\n")
        f.write("  COMPARATIVE NOTE: NEW ZEALAND\n\n")
        f.write("  New Zealand offers a relevant benchmark as a small democracy\n")
        f.write("  with strong institutional capacity. Its Algorithm Charter\n")
        f.write("  (voluntary, adopted by 30+ government agencies) demonstrates\n")
        f.write("  that transparency norms can be implemented without binding\n")
        f.write("  legislation — a pragmatic model for the Philippines, where\n")
        f.write("  legislative processes are slow and institutional capacity\n")
        f.write("  is uneven. However, binding legislation will ultimately be\n")
        f.write("  necessary as AI adoption deepens in government services.\n\n")

        f.write("=" * 72 + "\n")
        f.write("  This policy brief is produced as part of a Master's thesis\n")
        f.write("  portfolio at the Institute Pacific, New Zealand. It draws\n")
        f.write("  on publicly available data from the Oxford Insights AI\n")
        f.write("  Readiness Index, OECD, UNESCO, ASEAN Secretariat, and\n")
        f.write("  Philippine government publications.\n")
        f.write("=" * 72 + "\n")

    print(f"  ✓ Policy brief saved to {filepath}")


# ===========================================================================
# CONSOLE REPORT
# ===========================================================================

def print_report(readiness, gaps, dimensions):
    ph = readiness[readiness["country"] == "Philippines"].iloc[0]

    print("\n" + "=" * 70)
    print("  AI GOVERNANCE FRAMEWORKS FOR THE PHILIPPINES")
    print("  Comparative Analysis & Policy Recommendations")
    print("=" * 70)

    print(f"\n  PHILIPPINE AI READINESS SNAPSHOT")
    print(f"  {'─' * 50}")
    print(f"    Global Rank          : {int(ph['global_rank'])} / 193")
    print(f"    Readiness Score      : {ph['readiness_score']} / 100")
    print(f"    Government Pillar    : {ph['government_pillar']}")
    print(f"    Technology Pillar    : {ph['technology_pillar']}")
    print(f"    Data Infrastructure  : {ph['data_infrastructure_pillar']}")
    print(f"    OECD Digital Govt    : {ph['oecd_digital_govt_score']} / 1.0 (ASEAN avg: 0.37)")

    print(f"\n  ASEAN COMPARISON")
    print(f"  {'─' * 50}")
    for _, row in readiness.sort_values("global_rank").iterrows():
        marker = " ◄" if row["country"] == "Philippines" else ""
        print(f"    #{int(row['global_rank']):<5d} {row['country']:<15s}  "
              f"Score: {row['readiness_score']:>5.1f}{marker}")

    print(f"\n\n  TOP GOVERNANCE GAPS (SEVERITY 5/5)")
    print(f"  {'─' * 50}")
    critical = gaps[gaps["severity"] == 5]
    for _, g in critical.iterrows():
        print(f"    ●●●●●  {g['dimension']}")
        print(f"           {g['gap']}")
        print()

    print(f"\n  MATURITY COMPARISON (Philippines vs Benchmarks, 1-5 scale)")
    print(f"  {'─' * 60}")
    print(f"    {'Dimension':<28s} {'PH':>4s} {'SG':>4s} {'VN':>4s} {'NZ':>4s} {'EU':>4s}")
    print(f"    {'─' * 52}")
    for _, d in dimensions.iterrows():
        print(f"    {d['dimension']:<28s} {d['Philippines']:>4.0f} {d['Singapore']:>4.0f} "
              f"{d['Vietnam']:>4.0f} {d['New_Zealand']:>4.0f} {d['EU']:>4.0f}")

    ph_avg = dimensions["Philippines"].mean()
    sg_avg = dimensions["Singapore"].mean()
    nz_avg = dimensions["New_Zealand"].mean()
    print(f"    {'─' * 52}")
    print(f"    {'AVERAGE':<28s} {ph_avg:>4.1f} {sg_avg:>4.1f} "
          f"{dimensions['Vietnam'].mean():>4.1f} {nz_avg:>4.1f} {dimensions['EU'].mean():>4.1f}")

    print(f"\n\n  The Philippines scores an average of {ph_avg:.1f}/5 across all")
    print(f"  governance dimensions — compared to Singapore's {sg_avg:.1f} and")
    print(f"  New Zealand's {nz_avg:.1f}. The widest gaps are in Legal Framework,")
    print(f"  Risk Classification, and Algorithmic Transparency.")
    print()


# ===========================================================================
# MAIN
# ===========================================================================

def main():
    set_plot_style()

    print("\nLoading AI governance data...")
    readiness, gaps, timeline, dimensions = load_data()
    print(f"  ASEAN countries: {len(readiness)} | Gaps: {len(gaps)} | "
          f"Timeline events: {len(timeline)} | Dimensions: {len(dimensions)}")

    # Console report
    print_report(readiness, gaps, dimensions)

    # Charts
    print("Generating charts...")
    plot_asean_readiness_bar(readiness)
    plot_readiness_pillars(readiness)
    plot_governance_gap_severity(gaps)
    plot_radar_comparison(dimensions)
    plot_policy_timeline(timeline)
    plot_regulatory_readiness_matrix(readiness)
    plot_oecd_digital_govt(readiness)
    print(f"  ✓ 7 charts saved to {OUTPUT_DIR}/")

    # Policy brief
    write_policy_brief(readiness, gaps, dimensions)
    print()


if __name__ == "__main__":
    main()
