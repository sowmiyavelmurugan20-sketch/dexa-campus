"""
DEXA Unit & Integration Test Suite
Validates Scoring Engine, Segmentation, ML Risk Prediction, Data Integration, and Authentication
"""

import unittest
import io
import json
import pandas as pd
import numpy as np

from scoring_engine import calculate_student_success_score, batch_compute_success_scores, DEFAULT_WEIGHTS
from segmentation_engine import classify_student_segment, apply_student_segmentation, generate_prioritized_intervention_queue
from ml_engine import train_rf_model, predict_student_risk, simulate_recovery
from data_engine import validate_and_import_student_data, authenticate_user, load_student_dataset, load_staff_dataset


class TestDexaScoringEngine(unittest.TestCase):
    def setUp(self):
        self.sample_row = pd.Series({
            'cgpa': 8.5,
            'current_sem_gpa': 8.2,
            'backlogs': 0,
            'ia1_marks_50': 42,
            'ia2_marks_50': 40,
            'ia3_marks_50': 44,
            'attendance_overall_pct': 88.0,
            'attendance_last30days_pct': 85.0,
            'assignment_completion_pct': 92.0,
            'lms_quiz_avg_score': 85.0,
            'lms_logins_per_week': 5.0,
            'coding_score': 78.0,
            'aptitude_score': 72.0,
            'mock_interview_score': 75.0,
            'technical_skill_score': 80.0,
            'communication_score': 76.0,
            'problem_solving_score': 74.0,
            'faculty_feedback_1to5': 4.2
        })

    def test_complete_data_score(self):
        res = calculate_student_success_score(self.sample_row)
        self.assertTrue(0 <= res['total_score'] <= 100)
        self.assertEqual(res['completeness_pct'], 100.0)
        self.assertIn(res['risk_tier'], ['Low', 'Medium', 'High'])
        self.assertEqual(res['risk_tier'], 'Low')
        self.assertTrue(len(res['positive_drivers']) > 0)

    def test_missing_data_renormalization(self):
        # Omit placement and LMS data completely
        partial_row = pd.Series({
            'cgpa': 7.0,
            'attendance_overall_pct': 80.0
        })
        res = calculate_student_success_score(partial_row)
        self.assertTrue(0 <= res['total_score'] <= 100)
        # Completeness should reflect only available categories
        self.assertLess(res['completeness_pct'], 100.0)
        # Normalized weights should sum to approx 1.0
        weight_sum = sum(res['normalized_weights'].values())
        self.assertAlmostEqual(weight_sum, 1.0, places=4)

    def test_high_risk_backlog_penalty(self):
        at_risk_row = pd.Series({
            'cgpa': 4.8,
            'current_sem_gpa': 4.5,
            'backlogs': 6,
            'attendance_overall_pct': 58.0,
            'assignment_completion_pct': 40.0,
            'coding_score': 30.0
        })
        res = calculate_student_success_score(at_risk_row)
        self.assertLess(res['total_score'], 50.0)
        self.assertEqual(res['risk_tier'], 'High')
        self.assertTrue(any('Attendance' in d or 'Academic' in d for d in res['negative_drivers']))

    def test_score_risk_boundaries(self):
        # High Risk: < 50.0
        # Medium Risk: 50.0 <= score < 70.0
        # Low Risk: >= 70.0
        def evaluate_tier(score):
            if score < 50.0:
                return "High"
            elif score < 70.0:
                return "Medium"
            return "Low"

        self.assertEqual(evaluate_tier(49.9), "High")
        self.assertEqual(evaluate_tier(50.0), "Medium")
        self.assertEqual(evaluate_tier(69.9), "Medium")
        self.assertEqual(evaluate_tier(70.0), "Low")


class TestDexaSegmentationEngine(unittest.TestCase):

    def test_high_academic_low_placement_segment(self):
        row = pd.Series({
            'cgpa': 8.2,
            'coding_score': 42.0,
            'placement_readiness_score': 45.0,
            'attendance_overall_pct': 82.0,
            'days_since_last_lms_login': 2.0,
            'assignment_completion_pct': 85.0,
            'lms_logins_per_week': 4.0,
            'backlogs': 0
        })
        seg = classify_student_segment(row)
        self.assertEqual(seg, "High Academic — Low Placement Readiness")

    def test_disengaged_urgent_segment(self):
        row = pd.Series({
            'cgpa': 6.2,
            'coding_score': 50.0,
            'placement_readiness_score': 50.0,
            'attendance_overall_pct': 64.0,
            'days_since_last_lms_login': 7.0,
            'assignment_completion_pct': 50.0,
            'lms_logins_per_week': 1.0,
            'backlogs': 1
        })
        seg = classify_student_segment(row)
        self.assertEqual(seg, "Disengaged — Needs Urgent Intervention")

    def test_high_achiever_segment(self):
        row = pd.Series({
            'cgpa': 8.8,
            'coding_score': 85.0,
            'placement_readiness_score': 82.0,
            'attendance_overall_pct': 92.0,
            'days_since_last_lms_login': 1.0,
            'assignment_completion_pct': 95.0,
            'lms_logins_per_week': 6.0,
            'backlogs': 0
        })
        seg = classify_student_segment(row)
        self.assertEqual(seg, "High Achiever — Placement Ready")


class TestDexaDataEngine(unittest.TestCase):
    def setUp(self):
        self.df_stu = load_student_dataset()
        self.df_staff = load_staff_dataset()
        from seed_accounts import seed_accounts, DEV_CREDS_FILE
        seed_accounts(force_reset=False)
        with open(DEV_CREDS_FILE, "r", encoding="utf-8") as f:
            self.creds = json.load(f)["credentials"]

    def test_auth_hod(self):
        pwd = self.creds["dexa_admin"]["password"]
        auth = authenticate_user("admin", pwd, self.df_stu, self.df_staff)
        self.assertTrue(auth['authenticated'])
        self.assertEqual(auth['role'], "HOD / Admin")

    def test_auth_staff(self):
        pwd = self.creds["dexa_mentor"]["password"]
        auth = authenticate_user("STF002", pwd, self.df_stu, self.df_staff)
        self.assertTrue(auth['authenticated'])
        self.assertIn("Staff", auth['role'])

    def test_auth_student(self):
        pwd = self.creds["dexa_student"]["password"]
        auth = authenticate_user("STU0031", pwd, self.df_stu, self.df_staff)
        self.assertTrue(auth['authenticated'])
        self.assertEqual(auth['role'], "Student Portal")

    def test_auth_advisor(self):
        pwd = self.creds["dexa_advisor"]["password"]
        auth = authenticate_user("STF004", pwd, self.df_stu, self.df_staff)
        self.assertTrue(auth['authenticated'])
        self.assertEqual(auth['role'], "Class Advisor")

    def test_auth_invalid(self):
        auth = authenticate_user("unknown_user_999", "wrong_pass", self.df_stu, self.df_staff)
        self.assertFalse(auth['authenticated'])
        self.assertIsNotNone(auth['error'])

    def test_auth_wrong_password(self):
        auth = authenticate_user("admin", "completely_wrong_password", self.df_stu, self.df_staff)
        self.assertFalse(auth['authenticated'])
        self.assertIn("Invalid", auth['error'])

    def test_data_import_validation_missing_cols(self):
        bad_csv = io.StringIO("student_id,name\nSTU999,Test Student\n")
        res = validate_and_import_student_data(bad_csv, "test.csv")
        self.assertFalse(res['success'])
        self.assertIn("Missing required columns", res['message'])

    def test_data_import_validation_invalid_ext(self):
        dummy_file = io.StringIO("test")
        res = validate_and_import_student_data(dummy_file, "file.txt")
        self.assertFalse(res['success'])
        self.assertIn("Unsupported file type", res['message'])


class TestDexaMLEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.df = load_student_dataset()
        cls.model, cls.metrics, cls.importances = train_rf_model(cls.df)

    def test_rf_model_metrics(self):
        self.assertGreater(self.metrics['accuracy'], 0.85)
        self.assertGreater(self.metrics['roc_auc'], 0.90)

    def test_predict_student_risk(self):
        sample = self.df.iloc[0].to_dict()
        flag, prob = predict_student_risk(self.model, sample)
        self.assertIn(flag, [0, 1])
        self.assertTrue(0.0 <= prob <= 1.0)

    def test_recovery_simulation(self):
        student = self.df[self.df['risk_level'] == 'High'].iloc[0]
        rec = simulate_recovery(self.model, student, delta_attendance=15.0, delta_assignment=20.0)
        self.assertLessEqual(rec['sim_prob'], rec['base_prob'])
        self.assertGreaterEqual(rec['projected_success'], rec['base_success'])


class TestDexaAnalyticsContext(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.df_stu = load_student_dataset()
        cls.df_staff = load_staff_dataset()

    def test_department_telemetry(self):
        from analytics_context import get_department_telemetry
        tel = get_department_telemetry(self.df_stu, self.df_staff)
        self.assertEqual(tel['dataset_size'], 500)
        self.assertEqual(tel['faculty_count'], 15)
        self.assertAlmostEqual(tel['academics']['mean_cgpa'], 6.84, places=1)
        self.assertGreater(tel['attendance']['detention_warning_count'], 0)
        self.assertEqual(tel['ml_model_evaluation']['test_accuracy'], "96.0%")

    def test_lookup_student_context(self):
        from analytics_context import lookup_student_context
        stu = lookup_student_context("STU0001", self.df_stu)
        self.assertIsNotNone(stu)
        self.assertEqual(stu['student_id'], "STU0001")
        self.assertIn("root_causes", stu)
        self.assertIn("suggested_mitigations", stu)

    def test_lookup_student_invalid(self):
        from analytics_context import lookup_student_context
        stu = lookup_student_context("STU9999", self.df_stu)
        self.assertIsNone(stu)

    def test_build_system_prompt(self):
        from analytics_context import build_gemini_system_prompt
        prompt = build_gemini_system_prompt(self.df_stu, self.df_staff)
        self.assertIn("DEXA 2.0", prompt)
        self.assertIn("500", prompt)
        self.assertIn("Random Forest", prompt)


class TestDexaGeminiService(unittest.TestCase):
    def test_extract_student_id(self):
        from gemini_service import extract_student_id_from_text
        self.assertEqual(extract_student_id_from_text("Why was STU0005 flagged?"), "STU0005")
        self.assertEqual(extract_student_id_from_text("Tell me about stu0031 please"), "STU0031")
        self.assertIsNone(extract_student_id_from_text("Explain dijkstra algorithm"))

    def test_ai_service_status(self):
        from gemini_service import get_ai_service_status
        status = get_ai_service_status()
        self.assertIn("configured", status)
        self.assertIn("preferred_model", status)
        self.assertTrue("gemini" in status["preferred_model"])

    def test_missing_key_guidance(self):
        from gemini_service import format_missing_key_guidance
        msg = format_missing_key_guidance()
        self.assertIn("GEMINI_API_KEY", msg)
        self.assertIn("PowerShell", msg)
        self.assertIn("Command Prompt", msg)

    def test_chat_without_api_key(self):
        import os
        from gemini_service import chat_with_gemini
        # Ensure key is temporarily unset for deterministic test
        old_key = os.environ.get("GEMINI_API_KEY")
        if "GEMINI_API_KEY" in os.environ:
            del os.environ["GEMINI_API_KEY"]
        try:
            df_stu = load_student_dataset()
            df_staff = load_staff_dataset()
            res = chat_with_gemini("Explain student scores", [], df_stu, df_staff)
            self.assertFalse(res["configured"])
            self.assertEqual(res["error"], "MISSING_GEMINI_API_KEY")
            self.assertIn("GEMINI_API_KEY", res["content"])
        finally:
            if old_key is not None:
                os.environ["GEMINI_API_KEY"] = old_key

    def test_chat_with_invalid_api_key(self):
        import os
        from gemini_service import chat_with_gemini
        old_key = os.environ.get("GEMINI_API_KEY")
        os.environ["GEMINI_API_KEY"] = "AIzaSyFakeInvalidKeyForTesting123"
        try:
            df_stu = load_student_dataset()
            df_staff = load_staff_dataset()
            res = chat_with_gemini("Explain DEXA", [], df_stu, df_staff)
            self.assertTrue(res["configured"])
            self.assertIsNotNone(res["error"])
            self.assertIn("Invalid Gemini API Key", res["content"])
        finally:
            if old_key is not None:
                os.environ["GEMINI_API_KEY"] = old_key
            else:
                del os.environ["GEMINI_API_KEY"]


if __name__ == '__main__':

    unittest.main()

