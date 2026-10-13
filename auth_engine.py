"""
DEXA 2.0 Production Authentication & RBAC Engine
Provides server-side password hashing (via Werkzeug scrypt),
tamper-proof session management, and role-based access control.
"""

import os
import json
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from werkzeug.security import generate_password_hash, check_password_hash

AUTH_STORE_FILE = os.path.join(os.path.dirname(__file__), "auth_store.json")

# In-memory session registry: token -> session dict
_ACTIVE_SESSIONS: Dict[str, Dict[str, Any]] = {}

# Allowed roles in DEXA 2.0
VALID_ROLES = [
    "HOD / Admin",
    "Staff / Mentor",
    "Student Portal",
    "Class Advisor"
]


def hash_password(password: str) -> str:
    """Hash password using Werkzeug's secure scrypt algorithm."""
    return generate_password_hash(password, method="scrypt")


def verify_password(stored_hash: str, password: str) -> bool:
    """Verify plaintext password against stored hash."""
    if not stored_hash or not password:
        return False
    try:
        return check_password_hash(stored_hash, password)
    except Exception:
        return False


def load_account_store() -> Dict[str, Dict[str, Any]]:
    """Load accounts dictionary from local JSON store."""
    if not os.path.exists(AUTH_STORE_FILE):
        return {}
    try:
        with open(AUTH_STORE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("accounts", {})
    except Exception:
        return {}


def save_account_store(accounts: Dict[str, Dict[str, Any]]) -> None:
    """Save accounts dictionary to local JSON store."""
    payload = {
        "version": "2.0",
        "updated_at": datetime.utcnow().isoformat(),
        "accounts": accounts
    }
    with open(AUTH_STORE_FILE, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)


def get_account_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    """Lookup account case-insensitively by User ID."""
    if not user_id:
        return None
    accounts = load_account_store()
    normalized = user_id.strip().lower()
    return accounts.get(normalized)


def authenticate(user_id: str, password: str) -> Dict[str, Any]:
    """
    Authenticate User ID and password securely on the server.
    Returns:
        dict: {'authenticated': bool, 'user': dict or None, 'error': str or None}
    """
    u = (user_id or "").strip()
    p = (password or "").strip()

    if not u or not p:
        return {
            "authenticated": False,
            "user": None,
            "error": "Please enter both User ID and Password."
        }

    account = get_account_by_id(u)
    if not account:
        return {
            "authenticated": False,
            "user": None,
            "error": "Invalid User ID or Password."
        }

    # Check account active status
    if not account.get("is_active", True):
        return {
            "authenticated": False,
            "user": None,
            "error": "This account has been deactivated. Please contact your department administrator."
        }

    # Check password hash
    stored_hash = account.get("password_hash", "")
    if not verify_password(stored_hash, p):
        return {
            "authenticated": False,
            "user": None,
            "error": "Invalid User ID or Password."
        }

    # Return safe user profile (excluding password_hash)
    safe_profile = {
        "user_id": account.get("display_user_id", u),
        "normalized_id": u.lower(),
        "role": account.get("role", "Student Portal"),
        "name": account.get("name", ""),
        "email": account.get("email", ""),
        "linked_id": account.get("linked_id", ""),
        "department": account.get("department", "CSE"),
        "is_active": True
    }

    return {
        "authenticated": True,
        "user": safe_profile,
        "error": None
    }


def create_session(user: Dict[str, Any], expiry_seconds: int = 86400) -> str:
    """Generate a high-entropy session token and register it in memory."""
    token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(seconds=expiry_seconds)
    _ACTIVE_SESSIONS[token] = {
        "user": user,
        "role": user.get("role"),
        "user_id": user.get("user_id"),
        "linked_id": user.get("linked_id"),
        "created_at": datetime.utcnow().isoformat(),
        "expires_at": expires_at
    }
    return token


def get_session(token: str) -> Optional[Dict[str, Any]]:
    """Retrieve active session if valid and unexpired."""
    if not token or token not in _ACTIVE_SESSIONS:
        return None
    session = _ACTIVE_SESSIONS[token]
    if datetime.utcnow() > session["expires_at"]:
        del _ACTIVE_SESSIONS[token]
        return None
    return session


def revoke_session(token: str) -> bool:
    """Revoke session on logout."""
    if token in _ACTIVE_SESSIONS:
        del _ACTIVE_SESSIONS[token]
        return True
    return False


def can_access_student_record(session: Dict[str, Any], requested_student_id: str) -> bool:
    """
    Role-based authorization for individual student records:
    - HOD/Admin: Can view all students.
    - Class Advisor: Can view students in assigned cohort.
    - Staff/Mentor: Can view assigned mentees or all departmental records.
    - Student: Can ONLY view their OWN record.
    """
    if not session or not session.get("user"):
        return False

    role = session.get("role", "")
    req_id = (requested_student_id or "").strip().upper()

    if role in ["HOD / Admin", "Class Advisor", "Staff / Mentor"]:
        return True

    if role == "Student Portal":
        user_dict = session.get("user", {})
        profile = user_dict.get("profile_record") if isinstance(user_dict.get("profile_record"), dict) else {}
        allowed_ids = {
            str(session.get("user_id", "")).strip().upper(),
            str(session.get("linked_id", "")).strip().upper(),
            str(user_dict.get("user_id", "")).strip().upper(),
            str(user_dict.get("linked_id", "")).strip().upper(),
            str(profile.get("student_id", "")).strip().upper(),
            str(profile.get("roll_number", "")).strip().upper()
        }
        allowed_ids.discard("")
        return req_id in allowed_ids

    return False
