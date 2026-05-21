"""
analyze_lgu_risks.py
Analyzes the cybersecurity risk register for a Philippine LGU and
produces a risk assessment report with visualizations.

Outputs:
  - Console: risk summary, top risks, compliance gaps, recommendations
  - output/: seven charts (risk matrix, heatmap, department breakdown, etc.)
  - output/: executive_summary.txt (text-based executive brief)

Frameworks referenced:
  - NIST Cybersecurity Framework (CSF) 2.0
  - Philippine Data Privacy Act of 2012 (RA 10173)
  - NPC Circular 2016-01 (Security of Personal Data)
  - ISO/IEC 27001:2022 (Information Security Management)

Usage:
    python generate_lgu_risk_data.py   # (run first)
    python analyze_lgu_risks.py
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

INPUT_RISKS = "data/lgu_risk_register.csv"
INPUT_ASSETS = "data/lgu_asset_inventory.csv"
INPUT_THREATS = "data/lgu_threat_scenarios.csv"
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)


# ===========================================================================
# 1. LOAD
# ===========================================================================

def load_data():
    risks = pd.read_csv(INPUT_RISKS)
    assets = pd.read_csv(INPUT_ASSETS)
    threats = pd.read_csv(INPUT_THREATS)
    return risks, assets, threats


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


LEVEL_COLORS = {
    "Critical": "#c0392b",
    "High": "#e67e22",
    "Medium": "#f1c40f",
    "Low": "#27ae60",
}


# ===========================================================================
# 2. ANALYSIS
# ===========================================================================

def risk_summary(risks):
    """Count risks by level."""
    return risks["risk_level"].value_counts().reindex(
        ["Critical", "High", "Medium", "Low"], fill_value=0
    )


def top_risks(risks, n=10):
    """Top N risks by score."""
    return risks.nlargest(n, "risk_score")[
        ["risk_id", "threat_name", "asset_name", "department",
         "likelihood", "impact", "risk_score", "risk_level",
         "existing_controls"]
    ]


def risks_by_department(risks):
    """Risk score aggregated by department."""
    return (
        risks.groupby("department")
        .agg(
            total_risk_score=("risk_score", "sum"),
            count=("risk_id", "count"),
            avg_score=("risk_score", "mean"),
            critical_count=("risk_level", lambda x: (x == "Critical").sum()),
        )
        .sort_values("total_risk_score", ascending=False)
        .reset_index()
    )


def risks_by_nist_function(risks):
    """Risk distribution across NIST CSF functions."""
    # Explode multi-function entries
    exploded = risks.copy()
    exploded["nist_csf_function"] = exploded["nist_csf_function"].str.split(" / ")
    exploded = exploded.explode("nist_csf_function")
    exploded["nist_csf_function"] = exploded["nist_csf_function"].str.strip()
    return exploded.groupby("nist_csf_function")["risk_score"].agg(["sum", "count", "mean"]).reset_index()


def dpa_compliance_analysis(risks):
    """Identify DPA 2012 compliance risks."""
    dpa_risks = risks[risks["threat_name"] == "Non-Compliance with DPA 2012"]
    return dpa_risks


def personal_data_exposure(risks):
    """Count risks affecting assets with personal data."""
    personal = risks[risks["dpa_sensitivity"] != "N/A"]
    return personal.groupby("dpa_sensitivity")["risk_score"].agg(["count", "sum", "mean"]).reset_index()


# ===========================================================================
# 3. PRINT REPORT
# ===========================================================================

def print_report(risks, summary, top, by_dept, by_nist, dpa_risks, pd_exposure):
    print("\n" + "=" * 70)
    print("  CYBERSECURITY RISK ASSESSMENT REPORT")
    print("  Philippine Component City — Local Government Unit")
    print("=" * 70)

    print("\n  RISK SUMMARY")
    print("  " + "-" * 50)
    total = len(risks)
    for level in ["Critical", "High", "Medium", "Low"]:
        count = summary.get(level, 0)
        pct = count / total * 100
        bar = "█" * int(pct / 2)
        print(f"    {level:<10s}:  {count:>3d}  ({pct:>5.1f}%)  {bar}")
    print(f"    {'TOTAL':<10s}:  {total:>3d}")

    avg = risks["risk_score"].mean()
    print(f"\n    Average risk score : {avg:.1f} / 25")
    print(f"    Median risk score  : {risks['risk_score'].median():.0f} / 25")

    print(f"\n\n  TOP 10 HIGHEST RISKS")
    print("  " + "-" * 50)
    for _, r in top.iterrows():
        print(f"    [{r['risk_id']}] {r['threat_name']}")
        print(f"           Asset: {r['asset_name']}")
        print(f"           Dept:  {r['department']}")
        print(f"           Score: {r['risk_score']} ({r['risk_level']})  "
              f"L={r['likelihood']} × I={r['impact']}")
        print(f"           Controls: {r['existing_controls']}")
        print()

    print(f"\n  RISK BY DEPARTMENT")
    print("  " + "-" * 50)
    for _, d in by_dept.iterrows():
        print(f"    {d['department']:<40s}  Score: {d['total_risk_score']:>4.0f}  "
              f"Risks: {d['count']:>2.0f}  Critical: {d['critical_count']:>1.0f}")

    print(f"\n\n  DPA 2012 COMPLIANCE STATUS")
    print("  " + "-" * 50)
    if len(dpa_risks):
        print(f"    ⚠  {len(dpa_risks)} DPA compliance risks identified")
        print(f"    ⚠  {len(dpa_risks[dpa_risks['risk_level'] == 'Critical'])} rated CRITICAL")
        print(f"\n    Affected systems with sensitive personal information:")
        for _, r in dpa_risks.iterrows():
            print(f"      • {r['asset_name']} ({r['department']}) — {r['existing_controls']}")

    print(f"\n\n  PERSONAL DATA EXPOSURE ANALYSIS")
    print("  " + "-" * 50)
    for _, row in pd_exposure.iterrows():
        print(f"    {row['dpa_sensitivity']:<35s}  "
              f"Risks: {row['count']:>2.0f}  "
              f"Total Score: {row['sum']:>4.0f}  "
              f"Avg: {row['mean']:.1f}")

    print("\n\n" + "=" * 70)
    print("  PRIORITY RECOMMENDATIONS")
    print("=" * 70)
    print("""
  IMMEDIATE (0-30 days)
  ─────────────────────
  1. Appoint a Data Protection Officer (DPO) as required under RA 10173.
     Register processing systems with the National Privacy Commission.

  2. Deploy email filtering and conduct a phishing simulation exercise
     for all city employees. Phishing is the #1 attack vector.

  3. Change all default credentials on CCTV cameras and network devices.
     Implement a password policy (12+ chars, no sharing).

  SHORT-TERM (30-90 days)
  ───────────────────────
  4. Implement endpoint protection with centralized management.
     Replace Windows Defender default configs with managed antivirus.

  5. Establish a patch management schedule — monthly for workstations,
     weekly for internet-facing systems.

  6. Create offsite backup copies for all critical databases.
     Current single-NAS setup is a catastrophic single point of failure.

  MEDIUM-TERM (90-180 days)
  ─────────────────────────
  7. Draft and adopt a City Cybersecurity Policy via Sanggunian ordinance.
     Include incident response procedures and acceptable use policy.

  8. Conduct privacy impact assessments (PIA) for systems processing
     sensitive personal information (Civil Registry, Health, Social Welfare).

  9. Implement network segmentation to isolate critical databases
     from general-purpose endpoints.

  10. Engage DICT for a vulnerability assessment and subscribe to
      the National CERT (CERT-PH) threat intelligence feeds.
""")


# ===========================================================================
# 4. VISUALISATION
# ===========================================================================

def plot_risk_matrix(risks):
    """5x5 risk matrix scatter plot."""
    fig, ax = plt.subplots(figsize=(8, 8))

    # Background grid colors
    for l in range(1, 6):
        for i in range(1, 6):
            score = l * i
            if score >= 20:
                color = "#f5b7b1"
            elif score >= 12:
                color = "#fdebd0"
            elif score >= 6:
                color = "#fef9e7"
            else:
                color = "#d5f5e3"
            ax.add_patch(plt.Rectangle((l - 0.5, i - 0.5), 1, 1,
                                       facecolor=color, edgecolor="#cccccc"))

    # Jitter to avoid overlap
    jitter = lambda: random.uniform(-0.15, 0.15)
    import random
    random.seed(99)

    for _, r in risks.iterrows():
        ax.scatter(
            r["likelihood"] + jitter(), r["impact"] + jitter(),
            s=80, c=LEVEL_COLORS[r["risk_level"]],
            edgecolors="#333333", linewidths=0.5, zorder=5, alpha=0.8
        )

    ax.set_xlim(0.5, 5.5)
    ax.set_ylim(0.5, 5.5)
    ax.set_xticks(range(1, 6))
    ax.set_yticks(range(1, 6))
    ax.set_xticklabels(["Rare", "Unlikely", "Possible", "Likely", "Almost\nCertain"])
    ax.set_yticklabels(["Insignificant", "Minor", "Moderate", "Major", "Catastrophic"])
    ax.set_xlabel("Likelihood", fontweight="bold")
    ax.set_ylabel("Impact", fontweight="bold")
    ax.set_title("Risk Matrix — 5×5 Heat Map\nAll Identified Risks", fontweight="bold", fontsize=13)

    legend_patches = [mpatches.Patch(color=c, label=l) for l, c in LEVEL_COLORS.items()]
    ax.legend(handles=legend_patches, loc="lower right", fontsize=9)

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "01_risk_matrix.png"), dpi=150)
    plt.close()


def plot_risk_level_distribution(summary):
    """Donut chart of risk level distribution."""
    fig, ax = plt.subplots(figsize=(7, 7))
    colors = [LEVEL_COLORS[l] for l in summary.index]
    wedges, texts, autotexts = ax.pie(
        summary.values, labels=summary.index, autopct="%1.0f%%",
        colors=colors, startangle=90, pctdistance=0.75,
        wedgeprops={"edgecolor": "white", "linewidth": 2, "width": 0.4},
        textprops={"fontsize": 11}
    )
    for t in autotexts:
        t.set_fontsize(10)
        t.set_fontweight("bold")
    ax.set_title("Risk Level Distribution", fontweight="bold", fontsize=13)
    centre = plt.Circle((0, 0), 0.60, fc="white")
    ax.add_patch(centre)
    ax.text(0, 0, f"{summary.sum()}\nRisks", ha="center", va="center",
            fontsize=16, fontweight="bold", color="#333")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "02_risk_distribution.png"), dpi=150)
    plt.close()


def plot_department_risk_bar(by_dept):
    """Horizontal bar chart of risk by department."""
    fig, ax = plt.subplots(figsize=(10, 7))
    dept_sorted = by_dept.sort_values("total_risk_score", ascending=True)
    colors = ["#c0392b" if c > 0 else "#e67e22"
              for c in dept_sorted["critical_count"]]
    ax.barh(dept_sorted["department"], dept_sorted["total_risk_score"],
            color=colors, edgecolor="#333", linewidth=0.3)
    ax.set_xlabel("Cumulative Risk Score")
    ax.set_title("Risk Exposure by Department", fontweight="bold", fontsize=13)
    ax.grid(axis="x", alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "03_department_risk.png"), dpi=150)
    plt.close()


def plot_threat_category_breakdown(risks):
    """Bar chart by threat category."""
    cat_scores = (
        risks.groupby("threat_name")["risk_score"]
        .agg(["sum", "count"])
        .sort_values("sum", ascending=True)
        .reset_index()
    )
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.barh(cat_scores["threat_name"], cat_scores["sum"],
            color="#2980b9", edgecolor="#1a5276", linewidth=0.3)
    ax.set_xlabel("Total Risk Score")
    ax.set_title("Risk Score by Threat Type", fontweight="bold", fontsize=13)
    ax.grid(axis="x", alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "04_threat_breakdown.png"), dpi=150)
    plt.close()


def plot_nist_csf_coverage(by_nist):
    """Radar/bar chart showing NIST CSF function coverage."""
    nist_order = ["Govern", "Identify", "Protect", "Detect", "Respond", "Recover"]
    by_nist_ordered = by_nist.set_index("nist_csf_function").reindex(nist_order).fillna(0)

    fig, ax = plt.subplots(figsize=(9, 5))
    x = range(len(by_nist_ordered))
    ax.bar(x, by_nist_ordered["sum"], color="#8e44ad", edgecolor="#6c3483",
           width=0.6, alpha=0.85)
    ax.set_xticks(x)
    ax.set_xticklabels(by_nist_ordered.index, fontweight="bold")
    ax.set_ylabel("Total Risk Score in Function Area")
    ax.set_title("Risk Distribution Across NIST CSF Functions",
                 fontweight="bold", fontsize=13)
    ax.grid(axis="y", alpha=0.3)

    # Annotate counts
    for i, (_, row) in enumerate(by_nist_ordered.iterrows()):
        if row["count"] > 0:
            ax.text(i, row["sum"] + 3, f'{int(row["count"])} risks',
                    ha="center", fontsize=8, color="#555")

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "05_nist_csf_coverage.png"), dpi=150)
    plt.close()


def plot_dpa_compliance_heatmap(risks):
    """Heatmap: assets with personal data vs threat types."""
    personal_risks = risks[risks["dpa_sensitivity"] != "N/A"]
    pivot = personal_risks.pivot_table(
        index="asset_name", columns="threat_name",
        values="risk_score", aggfunc="sum", fill_value=0
    )
    # Keep only columns with data
    pivot = pivot.loc[:, (pivot != 0).any()]

    fig, ax = plt.subplots(figsize=(14, 7))
    im = ax.imshow(pivot.values, cmap="YlOrRd", aspect="auto")
    ax.set_xticks(range(len(pivot.columns)))
    ax.set_yticks(range(len(pivot.index)))
    ax.set_xticklabels(pivot.columns, rotation=45, ha="right", fontsize=8)
    ax.set_yticklabels(pivot.index, fontsize=9)
    ax.set_title("Personal Data Assets × Threats — Risk Score Heatmap",
                 fontweight="bold", fontsize=13)

    # Annotate cells
    for i in range(len(pivot.index)):
        for j in range(len(pivot.columns)):
            val = pivot.values[i, j]
            if val > 0:
                ax.text(j, i, f"{val:.0f}", ha="center", va="center",
                        fontsize=8, color="white" if val > 15 else "black")

    plt.colorbar(im, ax=ax, label="Risk Score", shrink=0.8)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "06_dpa_heatmap.png"), dpi=150)
    plt.close()


def plot_controls_gap(risks):
    """Show proportion of risks with adequate vs inadequate controls."""
    weak_keywords = ["none", "no ", "default", "partial", "outdated",
                     "incomplete", "basic", "manual", "single"]
    risks_copy = risks.copy()
    risks_copy["existing_controls"] = risks_copy["existing_controls"].fillna("None")
    risks_copy["control_strength"] = risks_copy["existing_controls"].apply(
        lambda c: "Weak / None" if any(k in str(c).lower() for k in weak_keywords)
        else "Some Controls"
    )

    by_strength = risks_copy.groupby(["risk_level", "control_strength"]).size().unstack(fill_value=0)
    level_order = ["Critical", "High", "Medium", "Low"]
    by_strength = by_strength.reindex(level_order).fillna(0)

    fig, ax = plt.subplots(figsize=(9, 5))
    by_strength.plot(kind="bar", stacked=True, ax=ax,
                     color=["#e74c3c", "#3498db"],
                     edgecolor="#333", linewidth=0.3, width=0.65)
    ax.set_ylabel("Number of Risks")
    ax.set_title("Control Gap Analysis — Existing Controls by Risk Level",
                 fontweight="bold", fontsize=13)
    ax.set_xticklabels(level_order, rotation=0)
    ax.legend(fontsize=9)
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "07_controls_gap.png"), dpi=150)
    plt.close()


# ===========================================================================
# 5. EXECUTIVE SUMMARY EXPORT
# ===========================================================================

def write_executive_summary(risks, summary, by_dept, dpa_risks):
    filepath = os.path.join(OUTPUT_DIR, "executive_summary.txt")
    total = len(risks)
    critical = summary.get("Critical", 0)
    high = summary.get("High", 0)

    with open(filepath, "w") as f:
        f.write("=" * 70 + "\n")
        f.write("  EXECUTIVE SUMMARY\n")
        f.write("  Cybersecurity Risk Assessment\n")
        f.write("  Philippine Component City — Local Government Unit\n")
        f.write("=" * 70 + "\n\n")
        f.write(f"Date Prepared   : May 2026\n")
        f.write(f"Prepared For    : Office of the City Mayor / City Administrator\n")
        f.write(f"Classification  : CONFIDENTIAL\n\n")
        f.write(f"SCOPE\n")
        f.write(f"  This assessment covers {total} identified cybersecurity risks\n")
        f.write(f"  across 15 information assets spanning 11 city departments.\n\n")
        f.write(f"HEADLINE FINDINGS\n")
        f.write(f"  • {critical} risks rated CRITICAL requiring immediate action\n")
        f.write(f"  • {high} risks rated HIGH requiring short-term remediation\n")
        f.write(f"  • {len(dpa_risks)} risks directly tied to Data Privacy Act compliance\n")
        f.write(f"  • Average risk score: {risks['risk_score'].mean():.1f} out of 25\n\n")
        f.write(f"MOST EXPOSED DEPARTMENT\n")
        top_dept = by_dept.iloc[0]
        f.write(f"  {top_dept['department']} — cumulative score {top_dept['total_risk_score']:.0f}\n\n")
        f.write(f"PRIMARY RISK DRIVERS\n")
        f.write(f"  1. No Data Protection Officer appointed (DPA violation)\n")
        f.write(f"  2. No security awareness training for employees\n")
        f.write(f"  3. Outdated/unpatched systems across all departments\n")
        f.write(f"  4. Single point of failure in backup infrastructure\n")
        f.write(f"  5. Default credentials on network and IoT devices\n\n")
        f.write(f"RECOMMENDED BUDGET PRIORITY\n")
        f.write(f"  Allocate cybersecurity line item in next Annual Investment\n")
        f.write(f"  Programme (AIP). Estimated minimum: PHP 2-5M for immediate\n")
        f.write(f"  controls (email security, endpoint protection, backup).\n")

    print(f"  ✓ Executive summary saved to {filepath}")


# ===========================================================================
# 6. MAIN
# ===========================================================================

def main():
    set_plot_style()

    print("\nLoading risk assessment data...")
    risks, assets, threats = load_data()
    print(f"  Assets: {len(assets)} | Threats: {len(threats)} | Risks: {len(risks)}")

    # Analysis
    summary = risk_summary(risks)
    top = top_risks(risks)
    by_dept = risks_by_department(risks)
    by_nist = risks_by_nist_function(risks)
    dpa_risks = dpa_compliance_analysis(risks)
    pd_exposure = personal_data_exposure(risks)

    # Report
    print_report(risks, summary, top, by_dept, by_nist, dpa_risks, pd_exposure)

    # Charts
    print("Generating charts...")
    plot_risk_matrix(risks)
    plot_risk_level_distribution(summary)
    plot_department_risk_bar(by_dept)
    plot_threat_category_breakdown(risks)
    plot_nist_csf_coverage(by_nist)
    plot_dpa_compliance_heatmap(risks)
    plot_controls_gap(risks)
    print(f"  ✓ 7 charts saved to {OUTPUT_DIR}/")

    # Executive summary
    write_executive_summary(risks, summary, by_dept, dpa_risks)
    print()


if __name__ == "__main__":
    main()
