"""
DEXA 2.0 Development Account Seeder
Generates cryptographically random credentials using python's secrets module,
hashes them using Werkzeug scrypt, and stores hashed accounts in auth_store.json.

Plaintext credentials for local development testing are written strictly to
the git-ignored local file `.dev_test_credentials.local.json`.
"""

import os
import sys
import json
import secrets
import string
import argparse
from typing import Dict, Any

from auth_engine import (
    hash_password,
    load_account_store,
    save_account_store,
    AUTH_STORE_FILE
)

DEV_CREDS_FILE = os.path.join(os.path.dirname(__file__), ".dev_test_credentials.local.json")


def generate_secure_password(length: int = 16) -> str:
    """Generate a strong random password using Python's secrets module."""
    # Ensure uppercase, lowercase, digits, and special symbols
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*-_"
    while True:
        pwd = ''.join(secrets.choice(alphabet) for _ in range(length))
        has_upper = any(c.isupper() for c in pwd)
        has_lower = any(c.islower() for c in pwd)
        has_digit = any(c.isdigit() for c in pwd)
        has_special = any(c in "!@#$%^&*-_" for c in pwd)
        if has_upper and has_lower and has_digit and has_special:
            return pwd


# Definition of the Four Roles in DEXA 2.0 with their real linked personas
SEED_ROLES_CONFIG = [
    {
        "primary_id": "dexa_admin",
        "alias_id": "admin",
        "role": "HOD / Admin",
        "name": "Dr. N. Balasubramanian",
        "email": "hod.cse@college.example.com",
        "linked_id": "STF005",
        "department": "CSE",
        "description": "Institutional Administrator / HOD (Full institutional oversight)"
    },
    {
        "primary_id": "dexa_mentor",
        "alias_id": "stf002",
        "role": "Staff / Mentor",
        "name": "Dr. T. Ramesh",
        "email": "t.ramesh@college.example.com",
        "linked_id": "STF002",
        "department": "CSE",
        "description": "Faculty Mentor (Scoped to assigned student mentees)"
    },
    {
        "primary_id": "dexa_student",
        "alias_id": "stu0031",
        "role": "Student Portal",
        "name": "Sowmiya V",
        "email": "24cs031@college.example.com",
        "linked_id": "STU0031",
        "department": "CSE",
        "description": "Student Portal (Personal academic growth and official dossier)"
    },
    {
        "primary_id": "dexa_advisor",
        "alias_id": "stf004",
        "role": "Class Advisor",
        "name": "Prof. P. Vijayakumar",
        "email": "p.vijayakumar@college.example.com",
        "linked_id": "STF004",
        "department": "CSE",
        "description": "Class Advisor (Class cohort roster and early-warning queue)"
    },
    {
        "primary_id": "dexa_disabled",
        "alias_id": "disabled_user",
        "role": "Student Portal",
        "name": "Test Disabled Account",
        "email": "disabled@college.example.com",
        "linked_id": "STU0099",
        "department": "CSE",
        "is_active": False,
        "description": "Disabled account (Used to verify deactivated account rejection)"
    }
]


def seed_accounts(force_reset: bool = False) -> Dict[str, Any]:
    """
    Seed or verify the 4 role accounts.
    Idempotent: If accounts already exist, does not overwrite passwords unless force_reset=True.
    """
    existing_accounts = load_account_store()
    existing_dev_creds = {}
    if os.path.exists(DEV_CREDS_FILE):
        try:
            with open(DEV_CREDS_FILE, "r", encoding="utf-8") as f:
                existing_dev_creds = json.load(f).get("credentials", {})
        except Exception:
            existing_dev_creds = {}

    updated_accounts = dict(existing_accounts)
    output_creds = dict(existing_dev_creds)

    new_accounts_created = 0

    for cfg in SEED_ROLES_CONFIG:
        p_id = cfg["primary_id"].lower()
        alias = cfg.get("alias_id", "").lower()

        # Check if already seeded and not resetting
        already_exists = (p_id in updated_accounts) and not force_reset

        if already_exists:
            password = output_creds.get(p_id, {}).get("password")
            if not password:
                # Regenerate password if missing from dev creds
                password = generate_secure_password()
                output_creds[p_id] = {
                    "user_id": cfg["primary_id"],
                    "password": password,
                    "role": cfg["role"],
                    "name": cfg["name"],
                    "linked_id": cfg["linked_id"]
                }
                updated_accounts[p_id]["password_hash"] = hash_password(password)
                if alias:
                    updated_accounts[alias]["password_hash"] = updated_accounts[p_id]["password_hash"]
        else:
            # Generate new unique secure password
            password = generate_secure_password()
            pwd_hash = hash_password(password)
            is_active = cfg.get("is_active", True)

            acc_entry = {
                "display_user_id": cfg["primary_id"],
                "normalized_id": p_id,
                "password_hash": pwd_hash,
                "role": cfg["role"],
                "name": cfg["name"],
                "email": cfg["email"],
                "linked_id": cfg["linked_id"],
                "department": cfg["department"],
                "is_active": is_active,
                "description": cfg["description"]
            }

            updated_accounts[p_id] = acc_entry

            if alias:
                alias_entry = dict(acc_entry)
                alias_entry["display_user_id"] = cfg["alias_id"]
                alias_entry["normalized_id"] = alias
                updated_accounts[alias] = alias_entry

            output_creds[p_id] = {
                "user_id": cfg["primary_id"],
                "alias": cfg.get("alias_id"),
                "password": password,
                "role": cfg["role"],
                "name": cfg["name"],
                "linked_id": cfg["linked_id"],
                "is_active": is_active,
                "description": cfg["description"]
            }
            new_accounts_created += 1

    # Save to auth_store.json
    save_account_store(updated_accounts)

    # Save plaintext test credentials strictly to local excluded file
    with open(DEV_CREDS_FILE, "w", encoding="utf-8") as f:
        json.dump({
            "notice": "LOCAL DEVELOPMENT CREDENTIALS ONLY. DO NOT COMMIT TO VERSION CONTROL.",
            "generated_with": "python secrets module (scrypt hashed in auth_store.json)",
            "credentials": output_creds
        }, f, indent=2)

    return {
        "status": "success",
        "new_accounts_created": new_accounts_created,
        "total_accounts": len(updated_accounts),
        "credentials_path": DEV_CREDS_FILE,
        "auth_store_path": AUTH_STORE_FILE
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="DEXA 2.0 Account Seeder")
    parser.add_argument("--reset", action="store_true", help="Force regenerate all passwords")
    args = parser.parse_args()

    result = seed_accounts(force_reset=args.reset)
    print(f"[SUCCESS] Seeded DEXA 2.0 Authentication Store.")
    print(f"Total Accounts: {result['total_accounts']}")
    print(f"Auth Store: {result['auth_store_path']}")
    print(f"Dev Credentials Saved Locally: {result['credentials_path']}")
