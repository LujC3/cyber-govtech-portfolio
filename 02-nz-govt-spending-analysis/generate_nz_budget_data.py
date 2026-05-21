"""
generate_nz_budget_data.py
Generates a structured dataset of New Zealand government expenditure
by Vote and sector, modeled on publicly available NZ Treasury data
from the Estimates of Appropriations (2019/20 – 2025/26).

The figures are synthetic but calibrated to real published totals from:
  - NZ Treasury Budget documents (2019–2025)
  - Budget at a Glance summaries
  - Financial Statements of the Government of NZ

This approach demonstrates data engineering skills while respecting
that the raw Treasury XLSX files require manual download.

Usage:
    python generate_nz_budget_data.py
    -> produces data/nz_govt_expenditure.csv
    -> produces data/nz_population.csv
"""

import csv
import os
import random

random.seed(42)

OUTPUT_DIR = "data"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ===================================================================
# NZ GOVERNMENT EXPENDITURE BY SECTOR (NZD Millions)
# Based on published Budget at a Glance and Treasury summary tables
# ===================================================================

SECTORS = {
    "Social Security and Welfare": {
        "2019/20": 29800, "2020/21": 37200, "2021/22": 33500,
        "2022/23": 30100, "2023/24": 28900, "2024/25": 27200,
        "2025/26": 25500,
        "minister": "Minister for Social Development",
    },
    "Health": {
        "2019/20": 20100, "2020/21": 22800, "2021/22": 25600,
        "2022/23": 27400, "2023/24": 28100, "2024/25": 28700,
        "2025/26": 29200,
        "minister": "Minister of Health",
    },
    "Education": {
        "2019/20": 16200, "2020/21": 17400, "2021/22": 18100,
        "2022/23": 18900, "2023/24": 19800, "2024/25": 20600,
        "2025/26": 21500,
        "minister": "Minister of Education",
    },
    "NZ Superannuation": {
        "2019/20": 15800, "2020/21": 16600, "2021/22": 17500,
        "2022/23": 18600, "2023/24": 20100, "2024/25": 22400,
        "2025/26": 24700,
        "minister": "Minister for Social Development",
    },
    "Core Government Services": {
        "2019/20": 10200, "2020/21": 11400, "2021/22": 12300,
        "2022/23": 12800, "2023/24": 13100, "2024/25": 12500,
        "2025/26": 11800,
        "minister": "Various",
    },
    "Law and Order": {
        "2019/20": 5400, "2020/21": 5700, "2021/22": 6100,
        "2022/23": 6400, "2023/24": 6700, "2024/25": 7000,
        "2025/26": 7300,
        "minister": "Minister of Justice",
    },
    "Transport and Communications": {
        "2019/20": 4800, "2020/21": 5100, "2021/22": 5400,
        "2022/23": 5900, "2023/24": 6200, "2024/25": 6800,
        "2025/26": 7200,
        "minister": "Minister of Transport",
    },
    "Defence": {
        "2019/20": 3100, "2020/21": 3300, "2021/22": 3500,
        "2022/23": 3700, "2023/24": 4000, "2024/25": 4500,
        "2025/26": 5100,
        "minister": "Minister of Defence",
    },
    "Economic and Industrial Services": {
        "2019/20": 4500, "2020/21": 7200, "2021/22": 6100,
        "2022/23": 5300, "2023/24": 5000, "2024/25": 4800,
        "2025/26": 4500,
        "minister": "Various",
    },
    "Environmental Protection": {
        "2019/20": 1800, "2020/21": 2100, "2021/22": 2300,
        "2022/23": 2500, "2023/24": 2200, "2024/25": 1900,
        "2025/26": 1700,
        "minister": "Minister for the Environment",
    },
    "Housing and Community Development": {
        "2019/20": 2800, "2020/21": 3200, "2021/22": 3600,
        "2022/23": 4100, "2023/24": 4400, "2024/25": 4000,
        "2025/26": 3800,
        "minister": "Minister of Housing",
    },
    "Heritage, Culture and Recreation": {
        "2019/20": 1600, "2020/21": 1900, "2021/22": 2000,
        "2022/23": 1800, "2023/24": 1700, "2024/25": 1500,
        "2025/26": 1400,
        "minister": "Minister for Arts, Culture and Heritage",
    },
    "Primary Services": {
        "2019/20": 1400, "2020/21": 1500, "2021/22": 1600,
        "2022/23": 1700, "2023/24": 1600, "2024/25": 1500,
        "2025/26": 1400,
        "minister": "Minister for Primary Industries",
    },
    "Finance Costs": {
        "2019/20": 4200, "2020/21": 3800, "2021/22": 4500,
        "2022/23": 6200, "2023/24": 7800, "2024/25": 8900,
        "2025/26": 9500,
        "minister": "Minister of Finance",
    },
}

FISCAL_YEARS = [
    "2019/20", "2020/21", "2021/22",
    "2022/23", "2023/24", "2024/25", "2025/26"
]

YEAR_TYPES = {
    "2019/20": "Actual", "2020/21": "Actual", "2021/22": "Actual",
    "2022/23": "Actual", "2023/24": "Actual",
    "2024/25": "Estimated Actual", "2025/26": "Budget",
}

# Sub-appropriation breakdown (proportional allocation within sectors)
SUB_ITEMS = {
    "Health": [
        ("Health Services Funding", 0.55),
        ("Public Health", 0.12),
        ("Disability Support Services", 0.15),
        ("Mental Health Services", 0.08),
        ("Health Workforce", 0.05),
        ("Health Infrastructure", 0.05),
    ],
    "Education": [
        ("Primary and Secondary Schooling", 0.52),
        ("Tertiary Education", 0.25),
        ("Early Childhood Education", 0.13),
        ("Special Education", 0.06),
        ("Education System Stewardship", 0.04),
    ],
    "Law and Order": [
        ("Police", 0.38),
        ("Corrections and Prisons", 0.30),
        ("Courts", 0.15),
        ("Serious Fraud Office and Crown Law", 0.07),
        ("Legal Aid", 0.10),
    ],
    "Defence": [
        ("NZDF Operations", 0.45),
        ("Defence Equipment and Capability", 0.30),
        ("Veteran Affairs", 0.10),
        ("Defence Estate", 0.15),
    ],
    "Transport and Communications": [
        ("State Highway Maintenance and Operations", 0.35),
        ("Public Transport", 0.25),
        ("Road Safety", 0.10),
        ("Rail Network", 0.15),
        ("Maritime and Aviation", 0.08),
        ("Digital Connectivity", 0.07),
    ],
}

# NZ population estimates (June, from Stats NZ)
NZ_POPULATION = {
    "2019/20": 5_002_100,
    "2020/21": 5_090_200,
    "2021/22": 5_127_200,
    "2022/23": 5_223_100,
    "2023/24": 5_346_500,
    "2024/25": 5_404_100,
    "2025/26": 5_460_000,
}


def generate_expenditure_csv():
    """Generate the main expenditure dataset."""
    rows = []
    for sector, data in SECTORS.items():
        minister = data["minister"]
        sub_items = SUB_ITEMS.get(sector, [(sector, 1.0)])

        for fy in FISCAL_YEARS:
            total = data[fy]
            year_type = YEAR_TYPES[fy]

            for item_name, proportion in sub_items:
                # Add slight variance to sub-items
                noise = random.uniform(-0.02, 0.02)
                amount = round(total * (proportion + noise), 1)

                rows.append({
                    "fiscal_year": fy,
                    "year_type": year_type,
                    "sector": sector,
                    "appropriation": item_name,
                    "responsible_minister": minister,
                    "amount_nzd_millions": amount,
                    "appropriation_type": "Departmental" if random.random() > 0.4 else "Non-Departmental",
                    "expense_type": random.choice([
                        "Output Expenses",
                        "Benefits or Related Expenses",
                        "Other Expenses",
                        "Capital Expenditure",
                    ]),
                })

    filepath = os.path.join(OUTPUT_DIR, "nz_govt_expenditure.csv")
    fieldnames = [
        "fiscal_year", "year_type", "sector", "appropriation",
        "responsible_minister", "amount_nzd_millions",
        "appropriation_type", "expense_type"
    ]
    with open(filepath, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Generated {len(rows)} records -> {filepath}")
    return rows


def generate_population_csv():
    """Generate population reference data."""
    filepath = os.path.join(OUTPUT_DIR, "nz_population.csv")
    with open(filepath, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["fiscal_year", "population"])
        writer.writeheader()
        for fy, pop in NZ_POPULATION.items():
            writer.writerow({"fiscal_year": fy, "population": pop})
    print(f"Generated population data -> {filepath}")


if __name__ == "__main__":
    generate_expenditure_csv()
    generate_population_csv()
