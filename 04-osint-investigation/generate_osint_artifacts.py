"""
generate_osint_artifacts.py
Generates simulated OSINT artifacts for a CTF-style investigation
scenario: verifying a suspicious government contractor.

SCENARIO
────────
"PacificBridge Solutions Inc." has submitted a bid to a Philippine
Component City for a PHP 45M IT Infrastructure Modernization Project
under RA 9184. The BAC Secretariat receives an anonymous tip alleging
the company is a shell entity with fabricated credentials. A due
diligence investigation using open-source intelligence is initiated.

The investigator must piece together publicly available information
to determine whether the company is legitimate.

ALL DATA IS ENTIRELY FICTITIOUS. No real persons, companies, or
government records are referenced.

Usage:
    python generate_osint_artifacts.py
    -> produces data/*.json (simulated OSINT artifacts)
    -> produces data/osint_timeline.csv
    -> produces data/entity_network.csv
"""

import json
import csv
import os

OUTPUT_DIR = "data"
os.makedirs(OUTPUT_DIR, exist_ok=True)


# ===================================================================
# ARTIFACT 1: COMPANY REGISTRATION (simulated SEC/DTI record)
# ===================================================================

SEC_RECORD = {
    "source": "SEC Company Registration Search (simulated)",
    "query_date": "2026-04-15",
    "company_name": "PacificBridge Solutions Inc.",
    "sec_registration_no": "CS-2023-07812",
    "date_registered": "2023-06-12",
    "registered_address": "Unit 1205, Pacific Century Tower, Osmeña Blvd, Cebu City 6000",
    "status": "Active",
    "primary_purpose": "Information Technology Consulting, Systems Integration, Network Infrastructure",
    "authorized_capital_stock": "PHP 5,000,000.00",
    "paid_up_capital": "PHP 1,250,000.00",
    "incorporators": [
        {"name": "Ricardo M. Villanueva", "nationality": "Filipino", "shares": 5000},
        {"name": "Angela S. Tan", "nationality": "Filipino", "shares": 3000},
        {"name": "Mark Joseph D. Reyes", "nationality": "Filipino", "shares": 2000},
    ],
    "directors": [
        {"name": "Ricardo M. Villanueva", "position": "President/CEO"},
        {"name": "Angela S. Tan", "position": "Treasurer"},
        {"name": "Mark Joseph D. Reyes", "position": "Corporate Secretary"},
    ],
    "red_flags": [
        "Company registered only 10 months before bid submission",
        "Paid-up capital (PHP 1.25M) is far below project value (PHP 45M)",
        "Only 3 incorporators — minimum required under Corporation Code",
    ],
}


# ===================================================================
# ARTIFACT 2: WHOIS DOMAIN LOOKUP
# ===================================================================

WHOIS_RECORD = {
    "source": "WHOIS Lookup (simulated)",
    "query_date": "2026-04-15",
    "domain": "pacificbridgesolutions.com.ph",
    "registrar": "dotPH (Philippine domain registry)",
    "registration_date": "2023-07-20",
    "expiry_date": "2025-07-20",
    "status": "EXPIRED — not renewed",
    "registrant_name": "Ricardo Villanueva",
    "registrant_org": "PacificBridge Solutions",
    "registrant_email": "r.villanueva@gmail.com",
    "registrant_phone": "+63.9171234567",
    "name_servers": ["ns1.cheaphost.ph", "ns2.cheaphost.ph"],
    "red_flags": [
        "Domain registered on free/personal email, not corporate email",
        "Domain expired and not renewed — suggests inactive business",
        "Hosted on budget shared hosting, not enterprise infrastructure",
        "Domain registered 38 days after SEC incorporation",
    ],
}


# ===================================================================
# ARTIFACT 3: WEBSITE SNAPSHOT (Wayback Machine simulation)
# ===================================================================

WAYBACK_RECORD = {
    "source": "Wayback Machine / Web Archive (simulated)",
    "query_date": "2026-04-16",
    "domain": "pacificbridgesolutions.com.ph",
    "snapshots_found": 3,
    "snapshots": [
        {
            "date": "2023-08-15",
            "description": "Single-page website with company logo, generic 'About Us' text, and stock photos. No client list, no project portfolio, no team photos.",
            "technology": "WordPress with default theme (flavor flavor flavor flavor flavor flavor flavor flavor flavor flavor flavor flavor flavor flavor flavor flavor flavor flavor flavor flavor flavor flavor flavor flavor flavor flavor flavor flavor flavor flavor flavor flavor flavor flavor flavor flavor flavor flavor flavor flavor Twenty Twenty-Three)",
            "contact_info": "Contact form only — no office phone, no physical address shown",
        },
        {
            "date": "2024-01-10",
            "description": "Same content as August 2023. No updates. Blog section exists but empty.",
            "technology": "WordPress (unchanged)",
            "contact_info": "Same contact form",
        },
        {
            "date": "2024-06-22",
            "description": "Site now shows 'Under Construction' page. Previous content removed.",
            "technology": "Static HTML placeholder",
            "contact_info": "Email: info@pacificbridgesolutions.com.ph (likely non-functional due to expired domain)",
        },
    ],
    "red_flags": [
        "Website used stock photos — no original content showing real projects",
        "No project portfolio despite claiming IT infrastructure experience",
        "Site went 'Under Construction' before domain expiry — possible abandonment",
        "Only 3 snapshots over 10 months — very low activity",
    ],
}


# ===================================================================
# ARTIFACT 4: SOCIAL MEDIA FOOTPRINT
# ===================================================================

SOCIAL_MEDIA = {
    "source": "Social Media OSINT (simulated search across platforms)",
    "query_date": "2026-04-16",
    "searches_performed": [
        "PacificBridge Solutions Inc",
        "PacificBridge Solutions Cebu",
        "Ricardo Villanueva IT Cebu",
        "pacificbridgesolutions",
    ],
    "findings": {
        "linkedin": {
            "company_page": False,
            "employee_profiles": 0,
            "ceo_profile": {
                "name": "Ricardo M. Villanueva",
                "headline": "Entrepreneur | IT Consultant",
                "connections": 87,
                "experience": [
                    {"role": "CEO", "company": "PacificBridge Solutions Inc.", "period": "Jun 2023 – Present"},
                    {"role": "Sales Associate", "company": "MegaTech Computer Sales", "period": "2018 – 2023"},
                ],
                "education": "BS Information Technology — University of the Visayas (2017)",
                "endorsements": 2,
                "posts": 0,
            },
            "notes": "No company page. CEO's only prior role was retail computer sales — no infrastructure project experience.",
        },
        "facebook": {
            "company_page": True,
            "page_created": "2023-07-25",
            "followers": 43,
            "posts": 5,
            "last_post": "2023-11-02",
            "content_type": "Generic motivational quotes and stock photos of server rooms",
            "reviews": 0,
            "check_ins": 0,
            "notes": "Page appears manufactured. No customer engagement, no project photos, no employee tagging.",
        },
        "twitter_x": {"account_found": False},
        "instagram": {"account_found": False},
        "github": {"account_found": False},
    },
    "red_flags": [
        "No LinkedIn company page — unusual for a legitimate IT firm",
        "CEO has 87 connections and zero posts — minimal professional network",
        "CEO's prior experience is retail computer sales, not infrastructure",
        "Facebook page has 43 followers and has been inactive since Nov 2023",
        "No employee profiles found on any platform",
        "No technical presence (GitHub, Stack Overflow, tech blogs)",
    ],
}


# ===================================================================
# ARTIFACT 5: PHILGEPS (Gov't E-Procurement) SEARCH
# ===================================================================

PHILGEPS_RECORD = {
    "source": "PhilGEPS (Philippine Government Electronic Procurement System) — simulated",
    "query_date": "2026-04-17",
    "searches": [
        {"query": "PacificBridge Solutions", "results": 1},
        {"query": "Ricardo Villanueva", "results": 0},
    ],
    "registration": {
        "philgeps_id": "PGR-2024-00456781",
        "company_name": "PacificBridge Solutions Inc.",
        "registration_date": "2024-01-15",
        "category": "Information and Communication Technology",
        "platinum_member": False,
        "business_size": "Micro",
    },
    "bid_history": [],
    "awards_received": [],
    "red_flags": [
        "Registered on PhilGEPS only in Jan 2024 — 7 months after SEC incorporation",
        "Zero bid participation history before current submission",
        "Zero contract awards — no government project track record",
        "Classified as 'Micro' enterprise bidding on a PHP 45M project",
        "Not a Platinum member — limited verification",
    ],
}


# ===================================================================
# ARTIFACT 6: PHYSICAL ADDRESS VERIFICATION
# ===================================================================

ADDRESS_VERIFICATION = {
    "source": "Google Maps / Street View / Building Directory (simulated)",
    "query_date": "2026-04-17",
    "registered_address": "Unit 1205, Pacific Century Tower, Osmeña Blvd, Cebu City 6000",
    "findings": {
        "building_exists": True,
        "building_type": "Mixed-use office/residential condominium",
        "unit_1205": {
            "status": "Virtual office / co-working space",
            "provider": "FlexSpace Cebu",
            "description": "Shared address service — PHP 2,500/month. Includes mail forwarding and occasional meeting room access. No permanent office.",
        },
        "signage": "No PacificBridge Solutions signage visible",
        "reception": "Building reception has no record of PacificBridge as a regular tenant",
    },
    "red_flags": [
        "Registered address is a virtual office, not a real business premises",
        "No physical signage or permanent presence",
        "Virtual office costs PHP 2,500/month — suggests minimal operational overhead",
        "Building reception does not recognize the company name",
    ],
}


# ===================================================================
# ARTIFACT 7: CROSS-REFERENCE — RELATED ENTITIES
# ===================================================================

ENTITY_CONNECTIONS = {
    "source": "Cross-reference analysis (SEC, DTI, PhilGEPS, social media)",
    "query_date": "2026-04-18",
    "primary_entity": "PacificBridge Solutions Inc.",
    "related_entities": [
        {
            "entity": "CebuTech Builders Corp.",
            "connection": "Angela S. Tan listed as Treasurer in both companies",
            "sec_reg": "CS-2022-04231",
            "status": "Revoked (non-filing of GIS for 2 consecutive years)",
            "notes": "Previous company of same incorporator — dissolved for non-compliance",
        },
        {
            "entity": "MegaTech Computer Sales",
            "connection": "Ricardo Villanueva's previous employer (retail)",
            "dti_reg": "DTI-07-2018-22134",
            "status": "Active (sole proprietorship)",
            "notes": "Computer retail shop in Colon St, Cebu. Not an IT infrastructure firm.",
        },
        {
            "entity": "Villanueva, Ricardo M. (Personal)",
            "connection": "CEO / Primary incorporator",
            "findings": [
                "No professional certifications found (no PRC, no IT certs)",
                "No published papers or conference appearances",
                "Personal Facebook shows lifestyle posts, no professional content",
                "No court records found (civil/criminal) — clean on this front",
            ],
        },
    ],
    "red_flags": [
        "Co-incorporator (Tan) was officer in a previously revoked company",
        "CEO's professional background is retail, not infrastructure",
        "No professional certifications held by any incorporator",
        "Pattern: incorporators appear to register companies for bidding purposes",
    ],
}


# ===================================================================
# TIMELINE & NETWORK DATA FOR ANALYSIS
# ===================================================================

TIMELINE_EVENTS = [
    ("2017-05-01", "Ricardo Villanueva graduates BS IT — UV", "Education", "Ricardo Villanueva"),
    ("2018-03-15", "MegaTech Computer Sales registered (DTI)", "Business Registration", "Ricardo Villanueva"),
    ("2022-02-10", "CebuTech Builders Corp. registered (SEC)", "Business Registration", "Angela Tan"),
    ("2023-06-12", "PacificBridge Solutions Inc. registered (SEC)", "Business Registration", "All Incorporators"),
    ("2023-07-20", "pacificbridgesolutions.com.ph domain registered", "Digital Footprint", "Ricardo Villanueva"),
    ("2023-07-25", "Facebook page created", "Digital Footprint", "PacificBridge"),
    ("2023-08-15", "Website first snapshot — single page with stock photos", "Digital Footprint", "PacificBridge"),
    ("2023-11-02", "Last Facebook post", "Digital Footprint", "PacificBridge"),
    ("2024-01-10", "Website snapshot — no updates since launch", "Digital Footprint", "PacificBridge"),
    ("2024-01-15", "PhilGEPS registration", "Procurement", "PacificBridge"),
    ("2024-03-01", "CebuTech Builders Corp. SEC registration REVOKED", "Business Registration", "Angela Tan"),
    ("2024-06-22", "Website changed to 'Under Construction'", "Digital Footprint", "PacificBridge"),
    ("2025-07-20", "Domain expired — not renewed", "Digital Footprint", "PacificBridge"),
    ("2026-03-01", "Bid submitted for PHP 45M IT Infrastructure Project", "Procurement", "PacificBridge"),
    ("2026-03-15", "Anonymous tip received by BAC Secretariat", "Investigation", "Anonymous"),
    ("2026-04-15", "OSINT investigation initiated", "Investigation", "Investigator"),
]

ENTITY_NETWORK = [
    ("PacificBridge Solutions Inc.", "Ricardo M. Villanueva", "CEO / President", "Corporate Officer"),
    ("PacificBridge Solutions Inc.", "Angela S. Tan", "Treasurer", "Corporate Officer"),
    ("PacificBridge Solutions Inc.", "Mark Joseph D. Reyes", "Corporate Secretary", "Corporate Officer"),
    ("CebuTech Builders Corp.", "Angela S. Tan", "Treasurer", "Corporate Officer"),
    ("MegaTech Computer Sales", "Ricardo M. Villanueva", "Employee (former)", "Employment"),
    ("PacificBridge Solutions Inc.", "pacificbridgesolutions.com.ph", "Company Website", "Digital Asset"),
    ("PacificBridge Solutions Inc.", "FlexSpace Cebu (Virtual Office)", "Registered Address", "Address"),
    ("PacificBridge Solutions Inc.", "Facebook Page (43 followers)", "Social Media", "Digital Asset"),
    ("PacificBridge Solutions Inc.", "PhilGEPS PGR-2024-00456781", "Procurement Registration", "Government Record"),
    ("PacificBridge Solutions Inc.", "PHP 45M IT Infrastructure Bid", "Bid Submission", "Procurement"),
    ("CebuTech Builders Corp.", "SEC — REVOKED", "Registration Status", "Government Record"),
    ("Ricardo M. Villanueva", "r.villanueva@gmail.com", "Personal Email (used for domain)", "Digital Asset"),
    ("Ricardo M. Villanueva", "LinkedIn (87 connections)", "Social Media", "Digital Asset"),
]


def save_json(data, filename):
    filepath = os.path.join(OUTPUT_DIR, filename)
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)
    print(f"  ✓ {filepath}")


def save_timeline():
    filepath = os.path.join(OUTPUT_DIR, "osint_timeline.csv")
    with open(filepath, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["date", "event", "category", "actor"])
        writer.writerows(TIMELINE_EVENTS)
    print(f"  ✓ {filepath}")


def save_entity_network():
    filepath = os.path.join(OUTPUT_DIR, "entity_network.csv")
    with open(filepath, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["source_entity", "target_entity", "relationship", "type"])
        writer.writerows(ENTITY_NETWORK)
    print(f"  ✓ {filepath}")


def main():
    print("Generating OSINT artifacts...")
    save_json(SEC_RECORD, "artifact_01_sec_registration.json")
    save_json(WHOIS_RECORD, "artifact_02_whois.json")
    save_json(WAYBACK_RECORD, "artifact_03_wayback.json")
    save_json(SOCIAL_MEDIA, "artifact_04_social_media.json")
    save_json(PHILGEPS_RECORD, "artifact_05_philgeps.json")
    save_json(ADDRESS_VERIFICATION, "artifact_06_address.json")
    save_json(ENTITY_CONNECTIONS, "artifact_07_entity_links.json")
    save_timeline()
    save_entity_network()
    print(f"\nGenerated 7 artifacts + 2 analysis datasets")


if __name__ == "__main__":
    main()
