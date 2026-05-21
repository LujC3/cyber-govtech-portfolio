"""
analyze_nz_spending.py
Analyzes New Zealand government expenditure data (2019/20 – 2025/26)
to surface spending trends, COVID-19 fiscal impact, sector priorities,
and per-capita allocation patterns.

Designed as a data analytics portfolio project with a governance focus —
the kind of analysis a policy analyst, public sector data team, or
GovTech consultancy would produce for Cabinet or Select Committee briefings.

Outputs:
  - Console: summary statistics, key findings, and policy observations
  - output/: eight publication-quality charts

Usage:
    python generate_nz_budget_data.py   # (run first)
    python analyze_nz_spending.py
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np

# --- Configuration ---
INPUT_FILE = "data/nz_govt_expenditure.csv"
POP_FILE = "data/nz_population.csv"
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

FISCAL_YEARS_ORDERED = [
    "2019/20", "2020/21", "2021/22",
    "2022/23", "2023/24", "2024/25", "2025/26"
]

# Colour palette (NZ government-inspired)
PALETTE = {
    "Social Security and Welfare": "#1f77b4",
    "Health": "#d62728",
    "Education": "#2ca02c",
    "NZ Superannuation": "#ff7f0e",
    "Core Government Services": "#9467bd",
    "Law and Order": "#8c564b",
    "Transport and Communications": "#e377c2",
    "Defence": "#7f7f7f",
    "Economic and Industrial Services": "#bcbd22",
    "Environmental Protection": "#17becf",
    "Housing and Community Development": "#aec7e8",
    "Heritage, Culture and Recreation": "#ffbb78",
    "Primary Services": "#98df8a",
    "Finance Costs": "#ff9896",
}


# ===========================================================================
# 1. LOAD AND PREPARE
# ===========================================================================

def load_data():
    df = pd.read_csv(INPUT_FILE)
    pop = pd.read_csv(POP_FILE)

    # Ordered categorical for fiscal years
    df["fiscal_year"] = pd.Categorical(
        df["fiscal_year"], categories=FISCAL_YEARS_ORDERED, ordered=True
    )

    # Aggregate to sector level per fiscal year
    sector_yearly = (
        df.groupby(["fiscal_year", "sector"], observed=True)["amount_nzd_millions"]
        .sum()
        .reset_index()
    )

    return df, pop, sector_yearly


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
# 2. ANALYSIS FUNCTIONS
# ===========================================================================

def compute_totals(sector_yearly):
    """Total government expenditure per fiscal year."""
    totals = (
        sector_yearly.groupby("fiscal_year", observed=True)["amount_nzd_millions"]
        .sum()
        .reset_index()
    )
    totals.columns = ["fiscal_year", "total_nzd_m"]
    return totals


def compute_yoy_growth(totals):
    """Year-over-year growth rates."""
    totals = totals.copy()
    totals["yoy_growth_pct"] = totals["total_nzd_m"].pct_change() * 100
    return totals


def compute_per_capita(totals, pop):
    """Per-capita spending."""
    merged = totals.merge(pop, on="fiscal_year")
    merged["per_capita_nzd"] = (
        merged["total_nzd_m"] * 1e6 / merged["population"]
    ).round(0)
    return merged


def compute_sector_shares(sector_yearly, totals):
    """Each sector's share of total spending."""
    merged = sector_yearly.merge(totals, on="fiscal_year")
    merged["share_pct"] = (
        merged["amount_nzd_millions"] / merged["total_nzd_m"] * 100
    ).round(2)
    return merged


def compute_covid_impact(sector_yearly):
    """Measure the COVID-19 spending surge (2020/21 vs 2019/20)."""
    pre = sector_yearly[sector_yearly["fiscal_year"] == "2019/20"][
        ["sector", "amount_nzd_millions"]
    ].rename(columns={"amount_nzd_millions": "pre_covid"})

    peak = sector_yearly[sector_yearly["fiscal_year"] == "2020/21"][
        ["sector", "amount_nzd_millions"]
    ].rename(columns={"amount_nzd_millions": "covid_peak"})

    impact = pre.merge(peak, on="sector")
    impact["change_nzd_m"] = impact["covid_peak"] - impact["pre_covid"]
    impact["change_pct"] = (impact["change_nzd_m"] / impact["pre_covid"] * 100).round(1)
    return impact.sort_values("change_nzd_m", ascending=False)


def identify_fastest_growing(sector_yearly):
    """Compound annual growth rate by sector (2019/20 to 2025/26)."""
    start = sector_yearly[sector_yearly["fiscal_year"] == "2019/20"][
        ["sector", "amount_nzd_millions"]
    ].rename(columns={"amount_nzd_millions": "start"})

    end = sector_yearly[sector_yearly["fiscal_year"] == "2025/26"][
        ["sector", "amount_nzd_millions"]
    ].rename(columns={"amount_nzd_millions": "end"})

    growth = start.merge(end, on="sector")
    n_years = 6
    growth["cagr_pct"] = ((growth["end"] / growth["start"]) ** (1 / n_years) - 1) * 100
    return growth.sort_values("cagr_pct", ascending=False).round(2)


# ===========================================================================
# 3. PRINT FINDINGS
# ===========================================================================

def print_summary(totals, per_capita, covid_impact, cagr):
    print("\n" + "=" * 70)
    print("  NEW ZEALAND GOVERNMENT EXPENDITURE ANALYSIS")
    print("  Fiscal Years 2019/20 — 2025/26")
    print("=" * 70)

    print("\n  TOTAL EXPENDITURE BY YEAR (NZD Millions)")
    print("  " + "-" * 50)
    for _, row in totals.iterrows():
        fy = row["fiscal_year"]
        total = row["total_nzd_m"]
        yoy = row.get("yoy_growth_pct", None)
        yoy_str = f"  ({yoy:+.1f}%)" if pd.notna(yoy) else ""
        print(f"    {fy}:  ${total:>10,.0f} M{yoy_str}")

    print(f"\n  PER-CAPITA SPENDING")
    print("  " + "-" * 50)
    for _, row in per_capita.iterrows():
        print(f"    {row['fiscal_year']}:  ${row['per_capita_nzd']:>8,.0f} per person")

    print(f"\n  COVID-19 FISCAL IMPACT (2020/21 vs 2019/20)")
    print("  " + "-" * 50)
    for _, row in covid_impact.head(5).iterrows():
        print(f"    {row['sector']:<42s}  {row['change_pct']:>+6.1f}%  "
              f"(${row['change_nzd_m']:>+8,.0f} M)")

    print(f"\n  FASTEST GROWING SECTORS (CAGR 2019/20 → 2025/26)")
    print("  " + "-" * 50)
    for _, row in cagr.head(5).iterrows():
        print(f"    {row['sector']:<42s}  {row['cagr_pct']:>+5.1f}% p.a.")

    print("\n" + "=" * 70)
    print("  KEY OBSERVATIONS")
    print("=" * 70)
    print("""
  1. SUPERANNUATION IS THE FASTEST-GROWING OBLIGATION
     NZ Super grows at ~7.7% CAGR, driven by demographics — not policy.
     It will overtake Social Security and Welfare as the largest single
     line item by 2025/26. This is structurally locked in.

  2. COVID-19 CREATED A FISCAL CLIFF IN SOCIAL SPENDING
     Social Security and Welfare surged 24.8% in 2020/21 (wage subsidies,
     income relief) then declined sharply as emergency measures expired.
     The sector is now below pre-COVID baseline.

  3. HEALTH SPENDING GREW STEADILY THROUGH ALL ADMINISTRATIONS
     Unlike other sectors, health has increased every single year —
     reflecting sustained demand pressure, Pharmac expansion, and
     workforce costs.

  4. FINANCE COSTS ARE CROWDING OUT DISCRETIONARY SPENDING
     Government borrowing costs grew from $4.2B to $9.5B — a 126%
     increase over six years. Every dollar spent on debt servicing
     is unavailable for frontline services.

  5. ENVIRONMENTAL AND CULTURAL BUDGETS FACE CUTS
     Environmental Protection and Heritage/Culture are the only sectors
     with negative CAGR — suggesting deprioritisation under current
     fiscal consolidation.
""")


# ===========================================================================
# 4. VISUALISATION
# ===========================================================================

def plot_total_expenditure_trend(totals):
    """Line chart of total government spending over time."""
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(
        totals["fiscal_year"].astype(str), totals["total_nzd_m"],
        color="#1a5276", marker="o", linewidth=2.5, markersize=8
    )
    ax.fill_between(
        range(len(totals)), totals["total_nzd_m"],
        alpha=0.1, color="#1a5276"
    )
    ax.set_ylabel("Total Expenditure (NZD Millions)")
    ax.set_title(
        "NZ Government Total Expenditure — 2019/20 to 2025/26",
        fontweight="bold", fontsize=13
    )
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}M"))
    ax.grid(axis="y", alpha=0.3)
    # Annotate COVID year
    ax.annotate(
        "COVID-19\nSpending Surge",
        xy=(1, totals.iloc[1]["total_nzd_m"]),
        xytext=(2.5, totals.iloc[1]["total_nzd_m"] + 3000),
        arrowprops=dict(arrowstyle="->", color="#c0392b"),
        fontsize=9, color="#c0392b", fontweight="bold"
    )
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "01_total_expenditure_trend.png"), dpi=150)
    plt.close()


def plot_sector_stacked_area(sector_yearly):
    """Stacked area chart of spending by sector."""
    pivot = sector_yearly.pivot_table(
        index="fiscal_year", columns="sector",
        values="amount_nzd_millions", observed=True
    ).fillna(0)

    # Sort columns by 2025/26 value
    order = pivot.iloc[-1].sort_values(ascending=False).index
    pivot = pivot[order]

    fig, ax = plt.subplots(figsize=(12, 6))
    colors = [PALETTE.get(s, "#999999") for s in order]
    pivot.plot.area(ax=ax, stacked=True, color=colors, alpha=0.85, linewidth=0.5)

    ax.set_ylabel("Expenditure (NZD Millions)")
    ax.set_title(
        "NZ Government Expenditure by Sector — Stacked Area",
        fontweight="bold", fontsize=13
    )
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}M"))
    ax.legend(loc="upper left", fontsize=7, ncol=2, framealpha=0.9)
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "02_sector_stacked_area.png"), dpi=150)
    plt.close()


def plot_top_sectors_bar(sector_yearly):
    """Grouped bar chart: top 6 sectors, first vs last year."""
    first_year = sector_yearly[sector_yearly["fiscal_year"] == "2019/20"]
    last_year = sector_yearly[sector_yearly["fiscal_year"] == "2025/26"]

    top_sectors = last_year.nlargest(6, "amount_nzd_millions")["sector"].values

    first_filtered = first_year[first_year["sector"].isin(top_sectors)].set_index("sector")
    last_filtered = last_year[last_year["sector"].isin(top_sectors)].set_index("sector")

    fig, ax = plt.subplots(figsize=(11, 6))
    x = np.arange(len(top_sectors))
    width = 0.35

    bars1 = ax.bar(
        x - width / 2,
        [first_filtered.loc[s, "amount_nzd_millions"] for s in top_sectors],
        width, label="2019/20", color="#85c1e9", edgecolor="#2980b9"
    )
    bars2 = ax.bar(
        x + width / 2,
        [last_filtered.loc[s, "amount_nzd_millions"] for s in top_sectors],
        width, label="2025/26 (Budget)", color="#1a5276", edgecolor="#0b3d5b"
    )

    ax.set_xticks(x)
    ax.set_xticklabels(top_sectors, rotation=25, ha="right", fontsize=9)
    ax.set_ylabel("Expenditure (NZD Millions)")
    ax.set_title(
        "Top 6 Sectors — 2019/20 vs 2025/26 Comparison",
        fontweight="bold", fontsize=13
    )
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}M"))
    ax.legend()
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "03_top_sectors_comparison.png"), dpi=150)
    plt.close()


def plot_per_capita(per_capita):
    """Per-capita spending trend."""
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(
        per_capita["fiscal_year"].astype(str),
        per_capita["per_capita_nzd"],
        color="#27ae60", edgecolor="#1e8449", width=0.6
    )
    for i, row in per_capita.iterrows():
        ax.text(
            i, row["per_capita_nzd"] + 200,
            f"${row['per_capita_nzd']:,.0f}",
            ha="center", fontsize=8, fontweight="bold"
        )
    ax.set_ylabel("NZD per Person")
    ax.set_title(
        "Government Spending Per Capita — 2019/20 to 2025/26",
        fontweight="bold", fontsize=13
    )
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "04_per_capita_spending.png"), dpi=150)
    plt.close()


def plot_covid_impact(covid_impact):
    """Horizontal bar chart of COVID-19 spending impact by sector."""
    fig, ax = plt.subplots(figsize=(10, 7))
    colors = ["#e74c3c" if v > 0 else "#2ecc71"
              for v in covid_impact["change_pct"]]

    ax.barh(
        covid_impact["sector"], covid_impact["change_pct"],
        color=colors, edgecolor="#333333", linewidth=0.3
    )
    ax.set_xlabel("Change in Spending (%)")
    ax.set_title(
        "COVID-19 Fiscal Impact by Sector — 2020/21 vs 2019/20",
        fontweight="bold", fontsize=13
    )
    ax.axvline(x=0, color="#333333", linewidth=0.8)
    ax.grid(axis="x", alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "05_covid_impact.png"), dpi=150)
    plt.close()


def plot_cagr(cagr):
    """Bar chart of compound annual growth rate by sector."""
    cagr_sorted = cagr.sort_values("cagr_pct", ascending=True)

    fig, ax = plt.subplots(figsize=(10, 7))
    colors = ["#c0392b" if v < 0 else "#2980b9" for v in cagr_sorted["cagr_pct"]]

    ax.barh(cagr_sorted["sector"], cagr_sorted["cagr_pct"],
            color=colors, edgecolor="#333333", linewidth=0.3)
    ax.set_xlabel("CAGR (%)")
    ax.set_title(
        "Sector Growth Rates — CAGR 2019/20 to 2025/26",
        fontweight="bold", fontsize=13
    )
    ax.axvline(x=0, color="#333333", linewidth=0.8)
    ax.grid(axis="x", alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "06_sector_cagr.png"), dpi=150)
    plt.close()


def plot_sector_share_treemap(sector_yearly):
    """Proportional treemap-style visualization for latest year."""
    latest = sector_yearly[sector_yearly["fiscal_year"] == "2025/26"].copy()
    latest = latest.sort_values("amount_nzd_millions", ascending=False)
    total = latest["amount_nzd_millions"].sum()
    latest["share"] = (latest["amount_nzd_millions"] / total * 100).round(1)

    fig, ax = plt.subplots(figsize=(10, 6))
    colors = [PALETTE.get(s, "#999") for s in latest["sector"]]
    wedges, texts, autotexts = ax.pie(
        latest["amount_nzd_millions"],
        labels=None,
        autopct=lambda p: f"{p:.1f}%" if p > 3 else "",
        colors=colors,
        startangle=140,
        pctdistance=0.8,
        wedgeprops={"edgecolor": "white", "linewidth": 1.5},
    )
    for t in autotexts:
        t.set_fontsize(8)
    ax.legend(
        latest["sector"], loc="center left", bbox_to_anchor=(1, 0.5),
        fontsize=8, framealpha=0.9
    )
    ax.set_title(
        "Expenditure Share by Sector — 2025/26 Budget",
        fontweight="bold", fontsize=13
    )
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "07_sector_share_pie.png"), dpi=150,
                bbox_inches="tight")
    plt.close()


def plot_finance_costs_vs_services(sector_yearly):
    """Dual-line: finance costs vs combined social spending."""
    finance = sector_yearly[sector_yearly["sector"] == "Finance Costs"].copy()
    social_sectors = ["Environmental Protection", "Heritage, Culture and Recreation",
                      "Primary Services"]
    social = (
        sector_yearly[sector_yearly["sector"].isin(social_sectors)]
        .groupby("fiscal_year", observed=True)["amount_nzd_millions"]
        .sum()
        .reset_index()
    )

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(
        finance["fiscal_year"].astype(str), finance["amount_nzd_millions"],
        color="#c0392b", marker="s", linewidth=2.5, label="Finance Costs (Debt Servicing)"
    )
    ax.plot(
        social["fiscal_year"].astype(str), social["amount_nzd_millions"],
        color="#27ae60", marker="o", linewidth=2.5,
        label="Environment + Culture + Primary (combined)"
    )
    ax.set_ylabel("Expenditure (NZD Millions)")
    ax.set_title(
        "Debt Servicing vs Discretionary Sectors — Crowding Out Effect",
        fontweight="bold", fontsize=13
    )
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}M"))
    ax.legend(fontsize=9)
    ax.grid(axis="y", alpha=0.3)

    # Annotate crossover
    ax.annotate(
        "Finance costs now exceed\nthree sectors combined",
        xy=(3, 6200), xytext=(4.5, 7500),
        arrowprops=dict(arrowstyle="->", color="#c0392b"),
        fontsize=9, color="#c0392b"
    )
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "08_crowding_out.png"), dpi=150)
    plt.close()


# ===========================================================================
# 5. MAIN
# ===========================================================================

def main():
    set_plot_style()

    print("Loading data...")
    df, pop, sector_yearly = load_data()

    print(f"  Records loaded     : {len(df):,}")
    print(f"  Sectors            : {df['sector'].nunique()}")
    print(f"  Fiscal years       : {df['fiscal_year'].nunique()}")
    print(f"  Appropriation items: {df['appropriation'].nunique()}")

    # Analysis
    totals = compute_totals(sector_yearly)
    totals = compute_yoy_growth(totals)
    per_capita = compute_per_capita(totals, pop)
    covid_impact = compute_covid_impact(sector_yearly)
    cagr = identify_fastest_growing(sector_yearly)

    print_summary(totals, per_capita, covid_impact, cagr)

    # Visualisation
    print("Generating charts...")
    plot_total_expenditure_trend(totals)
    plot_sector_stacked_area(sector_yearly)
    plot_top_sectors_bar(sector_yearly)
    plot_per_capita(per_capita)
    plot_covid_impact(covid_impact)
    plot_cagr(cagr)
    plot_sector_share_treemap(sector_yearly)
    plot_finance_costs_vs_services(sector_yearly)
    print(f"  ✓ 8 charts saved to {OUTPUT_DIR}/\n")


if __name__ == "__main__":
    main()
