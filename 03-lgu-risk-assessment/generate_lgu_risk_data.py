"""
generate_lgu_risk_data.py
Generates a cybersecurity risk assessment dataset for a typical
Philippine Local Government Unit (LGU) — specifically a Component City.

Models real LGU information assets, threat scenarios, and vulnerability
profiles based on:
  - Philippine Data Privacy Act of 2012 (RA 10173)
  - DICT Cybersecurity guidelines for government agencies
  - NIST Cybersecurity Framework (CSF) 2.0
  - Common LGU IT environments observed in practice

The scenario simulates a mid-size Component City with:
  - ~200 employees across multiple departments
  - Mix of legacy and modern systems
  - Limited dedicated IT security staff
  - Compliance obligations under DPA 2012

Usage:
    python generate_lgu_risk_data.py
    -> produces data/lgu_asset_inventory.csv
    -> produces data/lgu_threat_scenarios.csv
    -> produces data/lgu_risk_register.csv
"""

import csv
import os
import random

random.seed(42)

OUTPUT_DIR = "data"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ===================================================================
# ASSET INVENTORY
# Reflects what you'd actually find in a Philippine Component City
# ===================================================================

ASSETS = [
    {
        "asset_id": "A001",
        "asset_name": "Real Property Tax System (RPTS)",
        "department": "City Treasurer's Office",
        "asset_type": "Application",
        "data_classification": "Confidential",
        "contains_personal_data": True,
        "dpa_sensitivity": "Sensitive Personal Information",
        "users": 15,
        "description": "Manages property tax assessment, collection, and delinquency tracking for all real properties within the city.",
    },
    {
        "asset_id": "A002",
        "asset_name": "Business Permit and Licensing System (BPLS)",
        "department": "Business Permits Office",
        "asset_type": "Application",
        "data_classification": "Confidential",
        "contains_personal_data": True,
        "dpa_sensitivity": "Personal Information",
        "users": 20,
        "description": "Processes business permit applications, renewals, and compliance records including taxpayer identification.",
    },
    {
        "asset_id": "A003",
        "asset_name": "Civil Registry Database",
        "department": "City Civil Registrar",
        "asset_type": "Database",
        "data_classification": "Highly Confidential",
        "contains_personal_data": True,
        "dpa_sensitivity": "Sensitive Personal Information",
        "users": 8,
        "description": "Birth, death, and marriage records of all registered civil events within the city jurisdiction.",
    },
    {
        "asset_id": "A004",
        "asset_name": "Human Resource Information System (HRIS)",
        "department": "Human Resource Office",
        "asset_type": "Application",
        "data_classification": "Confidential",
        "contains_personal_data": True,
        "dpa_sensitivity": "Sensitive Personal Information",
        "users": 10,
        "description": "Employee records including 201 files, payroll data, leave management, and performance evaluations.",
    },
    {
        "asset_id": "A005",
        "asset_name": "Bids and Awards Committee (BAC) Records",
        "department": "BAC Secretariat",
        "asset_type": "File Server",
        "data_classification": "Confidential",
        "contains_personal_data": False,
        "dpa_sensitivity": "N/A",
        "users": 12,
        "description": "Procurement documents including bid evaluation reports, abstracts, purchase orders, and contract records under RA 9184.",
    },
    {
        "asset_id": "A006",
        "asset_name": "City Legal Case Management",
        "department": "City Legal Office",
        "asset_type": "Application",
        "data_classification": "Privileged",
        "contains_personal_data": True,
        "dpa_sensitivity": "Sensitive Personal Information",
        "users": 6,
        "description": "Tracks active litigation, legal opinions, ordinance drafts, and attorney-client privileged communications.",
    },
    {
        "asset_id": "A007",
        "asset_name": "City Website and Public Portal",
        "department": "City Information Office",
        "asset_type": "Web Application",
        "data_classification": "Public",
        "contains_personal_data": False,
        "dpa_sensitivity": "N/A",
        "users": 5,
        "description": "Public-facing website with transparency seal, bid notices, and service delivery information.",
    },
    {
        "asset_id": "A008",
        "asset_name": "Email Server (On-Premise)",
        "department": "MIS Division",
        "asset_type": "Infrastructure",
        "data_classification": "Internal",
        "contains_personal_data": True,
        "dpa_sensitivity": "Personal Information",
        "users": 180,
        "description": "On-premise email server handling all internal and external communications for city employees.",
    },
    {
        "asset_id": "A009",
        "asset_name": "Network Infrastructure (LAN/WAN)",
        "department": "MIS Division",
        "asset_type": "Infrastructure",
        "data_classification": "Internal",
        "contains_personal_data": False,
        "dpa_sensitivity": "N/A",
        "users": 200,
        "description": "Local and wide-area network connecting City Hall, annexes, and satellite offices.",
    },
    {
        "asset_id": "A010",
        "asset_name": "CCTV and Security System",
        "department": "General Services Office",
        "asset_type": "IoT/Physical",
        "data_classification": "Internal",
        "contains_personal_data": True,
        "dpa_sensitivity": "Personal Information",
        "users": 3,
        "description": "IP-based CCTV cameras across city hall premises with 30-day local storage.",
    },
    {
        "asset_id": "A011",
        "asset_name": "Social Welfare Beneficiary Database",
        "department": "City Social Welfare Office",
        "asset_type": "Database",
        "data_classification": "Highly Confidential",
        "contains_personal_data": True,
        "dpa_sensitivity": "Sensitive Personal Information",
        "users": 12,
        "description": "Records of indigent beneficiaries, PWD registrants, solo parents, and senior citizens receiving city assistance.",
    },
    {
        "asset_id": "A012",
        "asset_name": "City Health Information System",
        "department": "City Health Office",
        "asset_type": "Application",
        "data_classification": "Highly Confidential",
        "contains_personal_data": True,
        "dpa_sensitivity": "Sensitive Personal Information",
        "users": 25,
        "description": "Patient records from city health centers, immunization logs, TB-DOTS tracking, and maternal care data.",
    },
    {
        "asset_id": "A013",
        "asset_name": "Accounting and Budget System (eBudget/eNGAS)",
        "department": "City Accounting Office",
        "asset_type": "Application",
        "data_classification": "Confidential",
        "contains_personal_data": False,
        "dpa_sensitivity": "N/A",
        "users": 10,
        "description": "COA-prescribed accounting system for obligation tracking, journal entries, and financial reporting.",
    },
    {
        "asset_id": "A014",
        "asset_name": "Backup Storage (NAS)",
        "department": "MIS Division",
        "asset_type": "Infrastructure",
        "data_classification": "Confidential",
        "contains_personal_data": True,
        "dpa_sensitivity": "Mixed",
        "users": 3,
        "description": "Network-attached storage containing nightly backups of critical databases and file shares.",
    },
    {
        "asset_id": "A015",
        "asset_name": "Employee Workstations (Desktops/Laptops)",
        "department": "All Departments",
        "asset_type": "Endpoint",
        "data_classification": "Internal",
        "contains_personal_data": True,
        "dpa_sensitivity": "Personal Information",
        "users": 180,
        "description": "Windows-based workstations used by city employees, many running legacy OS versions.",
    },
]

# ===================================================================
# THREAT SCENARIOS
# Common threats mapped to NIST CSF and Philippine context
# ===================================================================

THREATS = [
    {
        "threat_id": "T001",
        "threat_name": "Ransomware Attack",
        "threat_category": "Malware",
        "nist_csf_function": "Protect / Detect",
        "attack_vector": "Phishing email with malicious attachment",
        "threat_actor": "Cybercriminal (opportunistic)",
        "applicable_assets": ["A008", "A015", "A014", "A001", "A004"],
    },
    {
        "threat_id": "T002",
        "threat_name": "Phishing / Social Engineering",
        "threat_category": "Social Engineering",
        "nist_csf_function": "Protect",
        "attack_vector": "Spoofed email impersonating government agency",
        "threat_actor": "Cybercriminal",
        "applicable_assets": ["A008", "A015", "A002", "A013"],
    },
    {
        "threat_id": "T003",
        "threat_name": "SQL Injection on Public Portal",
        "threat_category": "Web Application Attack",
        "nist_csf_function": "Protect / Detect",
        "attack_vector": "Malformed input on web forms",
        "threat_actor": "External attacker",
        "applicable_assets": ["A007", "A002"],
    },
    {
        "threat_id": "T004",
        "threat_name": "Insider Data Theft",
        "threat_category": "Insider Threat",
        "nist_csf_function": "Protect / Detect",
        "attack_vector": "Unauthorized USB copy or cloud upload",
        "threat_actor": "Disgruntled or negligent employee",
        "applicable_assets": ["A003", "A011", "A012", "A004", "A006"],
    },
    {
        "threat_id": "T005",
        "threat_name": "Unpatched System Exploitation",
        "threat_category": "Vulnerability Exploitation",
        "nist_csf_function": "Identify / Protect",
        "attack_vector": "Known CVE on unpatched Windows or application",
        "threat_actor": "External attacker (automated scanning)",
        "applicable_assets": ["A015", "A008", "A009", "A007"],
    },
    {
        "threat_id": "T006",
        "threat_name": "Data Breach via Lost/Stolen Device",
        "threat_category": "Physical",
        "nist_csf_function": "Protect",
        "attack_vector": "Laptop or USB drive lost or stolen",
        "threat_actor": "Opportunistic thief",
        "applicable_assets": ["A015", "A014"],
    },
    {
        "threat_id": "T007",
        "threat_name": "DDoS on City Website",
        "threat_category": "Availability Attack",
        "nist_csf_function": "Protect / Respond",
        "attack_vector": "Volumetric traffic flood",
        "threat_actor": "Hacktivist or competitor",
        "applicable_assets": ["A007", "A009"],
    },
    {
        "threat_id": "T008",
        "threat_name": "Unauthorized Access to CCTV Feeds",
        "threat_category": "Unauthorized Access",
        "nist_csf_function": "Protect",
        "attack_vector": "Default credentials on IP cameras",
        "threat_actor": "External attacker or insider",
        "applicable_assets": ["A010"],
    },
    {
        "threat_id": "T009",
        "threat_name": "Backup Failure / Data Loss",
        "threat_category": "Operational",
        "nist_csf_function": "Recover",
        "attack_vector": "NAS hardware failure or misconfiguration",
        "threat_actor": "N/A (system failure)",
        "applicable_assets": ["A014"],
    },
    {
        "threat_id": "T010",
        "threat_name": "Non-Compliance with DPA 2012",
        "threat_category": "Regulatory / Legal",
        "nist_csf_function": "Govern",
        "attack_vector": "Failure to register, lack of privacy notices, no DPO",
        "threat_actor": "N/A (compliance gap)",
        "applicable_assets": ["A001", "A002", "A003", "A004", "A011", "A012"],
    },
    {
        "threat_id": "T011",
        "threat_name": "Privilege Escalation via Shared Admin Accounts",
        "threat_category": "Access Control",
        "nist_csf_function": "Protect",
        "attack_vector": "Shared local admin credentials across workstations",
        "threat_actor": "Insider or lateral movement attacker",
        "applicable_assets": ["A015", "A009", "A008"],
    },
    {
        "threat_id": "T012",
        "threat_name": "Supply Chain Compromise (Vendor Access)",
        "threat_category": "Supply Chain",
        "nist_csf_function": "Govern / Protect",
        "attack_vector": "Third-party vendor with remote access to systems",
        "threat_actor": "Compromised vendor",
        "applicable_assets": ["A001", "A002", "A013", "A012"],
    },
]

# ===================================================================
# RISK SCORING
# ===================================================================

# Likelihood: 1=Rare, 2=Unlikely, 3=Possible, 4=Likely, 5=Almost Certain
# Impact: 1=Insignificant, 2=Minor, 3=Moderate, 4=Major, 5=Catastrophic

RISK_SCORES = {
    ("T001", "A008"): {"likelihood": 4, "impact": 5, "existing_controls": "Antivirus (outdated signatures)"},
    ("T001", "A015"): {"likelihood": 4, "impact": 4, "existing_controls": "Windows Defender (default config)"},
    ("T001", "A014"): {"likelihood": 3, "impact": 5, "existing_controls": "Network segmentation (partial)"},
    ("T001", "A001"): {"likelihood": 3, "impact": 5, "existing_controls": "Daily backup (local only)"},
    ("T001", "A004"): {"likelihood": 3, "impact": 4, "existing_controls": "Password-protected access"},
    ("T002", "A008"): {"likelihood": 5, "impact": 3, "existing_controls": "No email filtering or training"},
    ("T002", "A015"): {"likelihood": 5, "impact": 3, "existing_controls": "No security awareness program"},
    ("T002", "A002"): {"likelihood": 4, "impact": 3, "existing_controls": "None"},
    ("T002", "A013"): {"likelihood": 3, "impact": 4, "existing_controls": "Role-based access (basic)"},
    ("T003", "A007"): {"likelihood": 3, "impact": 3, "existing_controls": "Basic input validation"},
    ("T003", "A002"): {"likelihood": 3, "impact": 4, "existing_controls": "Firewall (perimeter only)"},
    ("T004", "A003"): {"likelihood": 3, "impact": 5, "existing_controls": "Physical access log only"},
    ("T004", "A011"): {"likelihood": 3, "impact": 5, "existing_controls": "Password protection"},
    ("T004", "A012"): {"likelihood": 3, "impact": 5, "existing_controls": "User authentication"},
    ("T004", "A004"): {"likelihood": 3, "impact": 4, "existing_controls": "HR department access only"},
    ("T004", "A006"): {"likelihood": 2, "impact": 5, "existing_controls": "Attorney-client privilege awareness"},
    ("T005", "A015"): {"likelihood": 5, "impact": 3, "existing_controls": "No patch management policy"},
    ("T005", "A008"): {"likelihood": 4, "impact": 4, "existing_controls": "Manual updates (irregular)"},
    ("T005", "A009"): {"likelihood": 4, "impact": 4, "existing_controls": "Vendor-managed (intermittent)"},
    ("T005", "A007"): {"likelihood": 3, "impact": 3, "existing_controls": "Hosted externally"},
    ("T006", "A015"): {"likelihood": 3, "impact": 3, "existing_controls": "No disk encryption"},
    ("T006", "A014"): {"likelihood": 2, "impact": 5, "existing_controls": "Server room lock"},
    ("T007", "A007"): {"likelihood": 2, "impact": 2, "existing_controls": "ISP-level basic protection"},
    ("T007", "A009"): {"likelihood": 2, "impact": 3, "existing_controls": "Firewall"},
    ("T008", "A010"): {"likelihood": 4, "impact": 3, "existing_controls": "Default passwords unchanged"},
    ("T009", "A014"): {"likelihood": 3, "impact": 5, "existing_controls": "Single NAS, no offsite backup"},
    ("T010", "A001"): {"likelihood": 5, "impact": 4, "existing_controls": "Partial privacy notices"},
    ("T010", "A002"): {"likelihood": 5, "impact": 4, "existing_controls": "None"},
    ("T010", "A003"): {"likelihood": 5, "impact": 5, "existing_controls": "None"},
    ("T010", "A004"): {"likelihood": 4, "impact": 4, "existing_controls": "Consent forms (incomplete)"},
    ("T010", "A011"): {"likelihood": 5, "impact": 5, "existing_controls": "None"},
    ("T010", "A012"): {"likelihood": 5, "impact": 5, "existing_controls": "None"},
    ("T011", "A015"): {"likelihood": 4, "impact": 4, "existing_controls": "Shared admin password known to MIS"},
    ("T011", "A009"): {"likelihood": 3, "impact": 4, "existing_controls": "Router password changed yearly"},
    ("T011", "A008"): {"likelihood": 3, "impact": 4, "existing_controls": "Single admin account"},
    ("T012", "A001"): {"likelihood": 2, "impact": 4, "existing_controls": "Vendor NDA signed"},
    ("T012", "A002"): {"likelihood": 2, "impact": 4, "existing_controls": "Vendor NDA signed"},
    ("T012", "A013"): {"likelihood": 2, "impact": 4, "existing_controls": "COA audit trail"},
    ("T012", "A012"): {"likelihood": 2, "impact": 5, "existing_controls": "No vendor access review"},
}


def risk_level(score):
    if score >= 20:
        return "Critical"
    elif score >= 12:
        return "High"
    elif score >= 6:
        return "Medium"
    else:
        return "Low"


def generate_asset_inventory():
    filepath = os.path.join(OUTPUT_DIR, "lgu_asset_inventory.csv")
    fieldnames = [
        "asset_id", "asset_name", "department", "asset_type",
        "data_classification", "contains_personal_data",
        "dpa_sensitivity", "users", "description"
    ]
    with open(filepath, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(ASSETS)
    print(f"Generated {len(ASSETS)} assets -> {filepath}")


def generate_threat_scenarios():
    filepath = os.path.join(OUTPUT_DIR, "lgu_threat_scenarios.csv")
    fieldnames = [
        "threat_id", "threat_name", "threat_category",
        "nist_csf_function", "attack_vector", "threat_actor",
        "applicable_assets"
    ]
    rows = []
    for t in THREATS:
        row = dict(t)
        row["applicable_assets"] = "; ".join(row["applicable_assets"])
        rows.append(row)
    with open(filepath, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Generated {len(THREATS)} threat scenarios -> {filepath}")


def generate_risk_register():
    filepath = os.path.join(OUTPUT_DIR, "lgu_risk_register.csv")
    fieldnames = [
        "risk_id", "threat_id", "threat_name", "asset_id", "asset_name",
        "department", "data_classification", "dpa_sensitivity",
        "likelihood", "impact", "risk_score", "risk_level",
        "existing_controls", "nist_csf_function"
    ]

    asset_lookup = {a["asset_id"]: a for a in ASSETS}
    threat_lookup = {t["threat_id"]: t for t in THREATS}

    rows = []
    risk_counter = 1
    for (tid, aid), scores in RISK_SCORES.items():
        threat = threat_lookup[tid]
        asset = asset_lookup[aid]
        risk_score = scores["likelihood"] * scores["impact"]

        rows.append({
            "risk_id": f"R{risk_counter:03d}",
            "threat_id": tid,
            "threat_name": threat["threat_name"],
            "asset_id": aid,
            "asset_name": asset["asset_name"],
            "department": asset["department"],
            "data_classification": asset["data_classification"],
            "dpa_sensitivity": asset["dpa_sensitivity"],
            "likelihood": scores["likelihood"],
            "impact": scores["impact"],
            "risk_score": risk_score,
            "risk_level": risk_level(risk_score),
            "existing_controls": scores["existing_controls"],
            "nist_csf_function": threat["nist_csf_function"],
        })
        risk_counter += 1

    rows.sort(key=lambda r: r["risk_score"], reverse=True)

    with open(filepath, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    critical = sum(1 for r in rows if r["risk_level"] == "Critical")
    high = sum(1 for r in rows if r["risk_level"] == "High")
    print(f"Generated {len(rows)} risks -> {filepath}")
    print(f"  Critical: {critical}  |  High: {high}  |  Medium+Low: {len(rows) - critical - high}")


if __name__ == "__main__":
    generate_asset_inventory()
    generate_threat_scenarios()
    generate_risk_register()
