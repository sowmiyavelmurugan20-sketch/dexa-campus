"""
DEXA 2.0 Comprehensive Authentication, Security & RBAC Test Suite
Validates the four roles, password hashing, session tokens, endpoint authorization,
student record confidentiality, and logout revocation against the live server.
"""

import os
import json
import unittest
from starlette.testclient import TestClient

from auth_engine import (
    load_account_store,
    get_account_by_id,
    verify_password,
    authenticate,
    get_session,
    can_access_student_record,
    AUTH_STORE_FILE,
    VALID_ROLES
)
from seed_accounts import DEV_CREDS_FILE, seed_accounts
from server import app


class TestDexaAuthenticationSuite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Ensure accounts are seeded
        seed_accounts(force_reset=False)
        cls.client = TestClient(app)

        with open(DEV_CREDS_FILE, "r", encoding="utf-8") as f:
            cls.dev_creds = json.load(f)["credentials"]

        cls.admin_creds = cls.dev_creds["dexa_admin"]
        cls.mentor_creds = cls.dev_creds["dexa_mentor"]
        cls.student_creds = cls.dev_creds["dexa_student"]
        cls.advisor_creds = cls.dev_creds["dexa_advisor"]
        cls.disabled_creds = cls.dev_creds["dexa_disabled"]

    # 1. Verify each of the four test accounts exists
    def test_1_four_test_accounts_exist(self):
        store = load_account_store()
        self.assertIn("dexa_admin", store, "dexa_admin must exist in store")
        self.assertIn("dexa_mentor", store, "dexa_mentor must exist in store")
        self.assertIn("dexa_student", store, "dexa_student must exist in store")
        self.assertIn("dexa_advisor", store, "dexa_advisor must exist in store")

    # 2. Verify stored password hash verifies against generated test password
    def test_2_password_hashes_verify_correctly(self):
        for acc_key in ["dexa_admin", "dexa_mentor", "dexa_student", "dexa_advisor"]:
            creds = self.dev_creds[acc_key]
            acc = get_account_by_id(creds["user_id"])
            self.assertIsNotNone(acc)
            stored_hash = acc["password_hash"]
            self.assertTrue(stored_hash.startswith("scrypt:"), f"Hash must use scrypt: {stored_hash}")
            self.assertTrue(verify_password(stored_hash, creds["password"]))

    # 3. Verify each account resolves to the correct role
    def test_3_roles_resolve_accurately(self):
        acc_admin = get_account_by_id("dexa_admin")
        self.assertEqual(acc_admin["role"], "HOD / Admin")

        acc_mentor = get_account_by_id("dexa_mentor")
        self.assertEqual(acc_mentor["role"], "Staff / Mentor")

        acc_student = get_account_by_id("dexa_student")
        self.assertEqual(acc_student["role"], "Student Portal")

        acc_advisor = get_account_by_id("dexa_advisor")
        self.assertEqual(acc_advisor["role"], "Class Advisor")

    # 4. Verify correct credentials authenticate successfully via API
    def test_4_correct_credentials_authenticate_via_api(self):
        for acc_key in ["dexa_admin", "dexa_mentor", "dexa_student", "dexa_advisor"]:
            creds = self.dev_creds[acc_key]
            res = self.client.post("/api/auth/login", json={
                "user_id": creds["user_id"],
                "password": creds["password"]
            })
            self.assertEqual(res.status_code, 200, f"Failed for {creds['user_id']}: {res.text}")
            data = res.json()
            self.assertTrue(data["authenticated"])
            self.assertEqual(data["role"], creds["role"])
            self.assertIn("token", data)
            self.assertIn("dexa_session", res.cookies)

    # 5. Verify incorrect passwords are rejected
    def test_5_incorrect_passwords_rejected(self):
        res = self.client.post("/api/auth/login", json={
            "user_id": "dexa_admin",
            "password": "WrongPassword!999"
        })
        self.assertEqual(res.status_code, 401)
        self.assertIn("Invalid", res.json()["detail"])

    # 6. Verify unknown user IDs are rejected
    def test_6_unknown_user_ids_rejected(self):
        res = self.client.post("/api/auth/login", json={
            "user_id": "non_existent_user_999",
            "password": "SomePassword123!"
        })
        self.assertEqual(res.status_code, 401)
        self.assertIn("Invalid", res.json()["detail"])

    # 7. Verify disabled accounts cannot log in
    def test_7_disabled_account_cannot_login(self):
        res = self.client.post("/api/auth/login", json={
            "user_id": self.disabled_creds["user_id"],
            "password": self.disabled_creds["password"]
        })
        self.assertEqual(res.status_code, 401)
        self.assertIn("deactivated", res.json()["detail"].lower())

    # 8. Verify passwords are NOT stored in plaintext
    def test_8_passwords_not_stored_in_plaintext(self):
        store = load_account_store()
        for key, acc in store.items():
            self.assertNotIn("password", acc, "Plaintext password key must not exist in auth store")
            h = acc.get("password_hash", "")
            self.assertNotEqual(h, "")
            self.assertTrue(h.startswith("scrypt:"), "Stored password must be an scrypt hash")
            # Verify plaintext password from creds is nowhere in store JSON
            for c_key, c_val in self.dev_creds.items():
                self.assertNotIn(c_val["password"], json.dumps(acc))

    # 9. Verify no account has conflicting multiple roles
    def test_9_no_conflicting_multiple_roles(self):
        store = load_account_store()
        for key, acc in store.items():
            role = acc.get("role")
            self.assertIn(role, VALID_ROLES)
            self.assertIsInstance(role, str)
            self.assertFalse(isinstance(role, list), "Account must have exactly one role")

    # 10. Verify student account cannot access administrator-only endpoints
    def test_10_student_cannot_access_admin_endpoints(self):
        # Login as student
        stu_res = self.client.post("/api/auth/login", json={
            "user_id": self.student_creds["user_id"],
            "password": self.student_creds["password"]
        })
        self.assertEqual(stu_res.status_code, 200)
        stu_token = stu_res.json()["token"]

        headers = {"Authorization": f"Bearer {stu_token}"}

        # Attempt to modify institutional weights (Admin only)
        w_res = self.client.post(
            "/api/settings/weights",
            json={
                "academics": 0.4,
                "attendance": 0.2,
                "lms_engagement": 0.1,
                "placement_readiness": 0.2,
                "skills_feedback": 0.1
            },
            headers=headers
        )
        self.assertEqual(w_res.status_code, 403, "Student must receive 403 Forbidden on weights update")

        # Attempt to download department audit brief (Admin/Staff only)
        dept_res = self.client.get("/api/reports/department-pdf", headers=headers)
        self.assertEqual(dept_res.status_code, 403, "Student must receive 403 Forbidden on department PDF")

    # 11. Verify student cannot access unauthorized student records
    def test_11_student_cannot_access_unauthorized_records(self):
        # Login as student STU0031
        stu_res = self.client.post("/api/auth/login", json={
            "user_id": self.student_creds["user_id"],
            "password": self.student_creds["password"]
        })
        stu_token = stu_res.json()["token"]
        headers = {"Authorization": f"Bearer {stu_token}"}

        # Requesting self (STU0031) should be permitted
        own_res = self.client.get("/api/reports/student-pdf/STU0031", headers=headers)
        self.assertEqual(own_res.status_code, 200, "Student must be able to view their own dossier")

        # Requesting another student's dossier (STU0005) must be blocked
        other_res = self.client.get("/api/reports/student-pdf/STU0005", headers=headers)
        self.assertEqual(other_res.status_code, 403, "Student must receive 403 when requesting peer record")

    # 12. Verify session handling, /api/auth/me, and logout revocation
    def test_12_session_lifecycle_and_logout(self):
        # 1. Login
        login_res = self.client.post("/api/auth/login", json={
            "user_id": self.admin_creds["user_id"],
            "password": self.admin_creds["password"]
        })
        self.assertEqual(login_res.status_code, 200)
        token = login_res.json()["token"]

        # 2. Check /api/auth/me with Bearer token
        me_res = self.client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(me_res.status_code, 200)
        self.assertEqual(me_res.json()["role"], "HOD / Admin")

        # 3. Logout
        logout_res = self.client.post("/api/auth/logout", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(logout_res.status_code, 200)
        self.assertFalse(logout_res.json()["authenticated"])

        # 4. Verify session is revoked
        post_logout_me = self.client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(post_logout_me.status_code, 401, "Revoked session must be rejected with 401")


if __name__ == "__main__":
    unittest.main(verbosity=2)
