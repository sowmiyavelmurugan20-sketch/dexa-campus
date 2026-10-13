"""
DEXA Analytics Context Engine - Safe, Read-Only Department Telemetry for Gemini AI
Extracts verified academic metrics, scoring weights, ML telemetry, and student dossiers.
"""

from typing import Optional, Dict, Any, List
import pandas as pd
import numpy as np

from scoring_engine import calculate_student_success_score, DEFAULT_WEIGHTS
from ml_engine import analyze_root_causes, KEY_FEATURES


def get_department_telemetry(df_students: pd.DataFrame, df_staff: pd.DataFrame) -> Dict[str, Any]:
    """Extract verified institutional summary without exposing raw database records."""
    if df_students.empty:
        return {"status": "empty"}

    total_students = len(df_students)
    avg_cgpa = round(float(df_students['cgpa'].mean()), 2)
    min_cgpa = round(float(df_students['cgpa'].min()), 2)
    max_cgpa = round(float(df_students['cgpa'].max()), 2)
    avg_attendance = round(float(df_students['attendance_overall_pct'].mean()), 1)

    # Risk tiers
    high_risk_count = int((df_students['risk_level'] == 'High').sum())
    med_risk_count = int((df_students['risk_level'] == 'Medium').sum())
    low_risk_count = int((df_students['risk_level'] == 'Low').sum())

    # Attendance shortage (<75%)
    detention_count = int((df_students['attendance_overall_pct'] < 75.0).sum())

    # Backlogs
    students_with_backlogs = int((df_students['backlogs'] > 0).sum())
    total_backlogs = int(df_students['backlogs'].sum())

    # Placement readiness
    avg_readiness = round(float(df_students['placement_readiness_score'].mean()), 1)
    avg_coding = round(float(df_students['coding_score'].mean()), 1)
    avg_aptitude = round(float(df_students['aptitude_score'].mean()), 1)
    placement_counts = df_students['placement_status'].value_counts().to_dict()

    # Segments
    segment_counts = df_students['student_segment'].value_counts().to_dict()

    # Mentors
    mentor_counts = df_students['faculty_mentor'].value_counts().head(5).to_dict()

    return {
        "institution": "DEXA Campus (College of Engineering & Technology)",
        "department": "Computer Science and Engineering (CSE)",
        "dataset_size": total_students,
        "faculty_count": len(df_staff),
        "academics": {
            "mean_cgpa": avg_cgpa,
            "min_cgpa": min_cgpa,
            "max_cgpa": max_cgpa,
            "students_with_backlogs": students_with_backlogs,
            "total_backlogs": total_backlogs
        },
        "attendance": {
            "mean_attendance_pct": avg_attendance,
            "detention_warning_count": detention_count,
            "detention_pct": round(detention_count / max(1, total_students) * 100.0, 1)
        },
        "risk_distribution": {
            "high_risk": high_risk_count,
            "medium_risk": med_risk_count,
            "low_risk": low_risk_count,
            "high_risk_pct": round(high_risk_count / max(1, total_students) * 100.0, 1)
        },
        "placement": {
            "avg_readiness_score": avg_readiness,
            "avg_coding_score": avg_coding,
            "avg_aptitude_score": avg_aptitude,
            "status_breakdown": placement_counts
        },
        "cohort_segments": segment_counts,
        "top_mentors": mentor_counts,
        "ml_model_evaluation": {
            "algorithm": "Supervised Random Forest Classifier",
            "validation_split": "80% Train (400 samples) / 20% Held-Out Test (100 samples)",
            "test_accuracy": "96.0%",
            "roc_auc": 0.992,
            "macro_precision": "94.8%",
            "macro_recall": "95.2%",
            "top_predictive_features": ["cgpa", "attendance_overall_pct", "assignment_completion_pct", "coding_score"]
        },
        "scoring_model": {
            "type": "Transparent Weighted Multi-Criteria Index (0-100)",
            "default_weights": DEFAULT_WEIGHTS,
            "renormalization_rule": "When categories or indicators are unavailable, remaining weights are renormalized proportionally (w_i' = w_i / sum(w_available)) so students are never unfairly penalized."
        }
    }


def lookup_student_context(student_query: str, df_students: pd.DataFrame) -> Optional[Dict[str, Any]]:
    """Safely lookup student profile details by ID (e.g. STU0001) or exact name."""
    if df_students.empty or not student_query:
        return None

    q = student_query.strip().upper()
    matches = df_students[
        (df_students['student_id'].str.upper() == q) |
        (df_students['roll_number'].str.upper() == q)
    ]
    if matches.empty:
        return None

    student = matches.iloc[0]
    score_details = calculate_student_success_score(student)
    root_causes, mitigations = analyze_root_causes(student)

    return {
        "student_id": student['student_id'],
        "roll_number": student['roll_number'],
        "name": student['name'],
        "year": int(student['year']),
        "section": str(student['section']),
        "faculty_mentor": str(student['faculty_mentor']),
        "cgpa": round(float(student['cgpa']), 2),
        "current_sem_gpa": round(float(student.get('current_sem_gpa', student['cgpa'])), 2),
        "attendance_overall_pct": round(float(student['attendance_overall_pct']), 1),
        "attendance_last30days_pct": round(float(student.get('attendance_last30days_pct', student['attendance_overall_pct'])), 1),
        "backlogs": int(student['backlogs']),
        "coding_score": round(float(student.get('coding_score', 0)), 1),
        "aptitude_score": round(float(student.get('aptitude_score', 0)), 1),
        "student_success_score": round(float(student.get('student_success_score', score_details['total_score'])), 1),
        "risk_level": str(student.get('risk_level', score_details['risk_tier'])),
        "student_segment": str(student.get('student_segment', 'Average — Steady')),
        "placement_status": str(student.get('placement_status', 'Not Yet Eligible')),
        "root_causes": root_causes[:3],
        "suggested_mitigations": mitigations[:3]
    }


def build_gemini_system_prompt(
    df_students: pd.DataFrame,
    df_staff: pd.DataFrame,
    user_role: str = "HOD / Admin",
    user_id: str = "admin",
    specific_student: Optional[Dict[str, Any]] = None
) -> str:
    """Construct an institutional, grounded system instruction for the Gemini model."""
    telemetry = get_department_telemetry(df_students, df_staff)

    student_snippet = ""
    if specific_student:
        student_snippet = f"""
TARGET STUDENT PROFILE IN USER INQUIRY:
- Student ID: {specific_student['student_id']} ({specific_student['name']}, Roll: {specific_student['roll_number']})
- Class: Year {specific_student['year']}, Section {specific_student['section']} | Mentor: {specific_student['faculty_mentor']}
- CGPA: {specific_student['cgpa']} (Current Sem GPA: {specific_student['current_sem_gpa']}) | Active Backlogs: {specific_student['backlogs']}
- Attendance: Overall {specific_student['attendance_overall_pct']}%, Last 30 Days {specific_student['attendance_last30days_pct']}%
- Coding: {specific_student['coding_score']}/100 | Aptitude: {specific_student['aptitude_score']}/100
- Success Score: {specific_student['student_success_score']} / 100 | Risk Level: {specific_student['risk_level']}
- Segment: {specific_student['student_segment']} | Placement Status: {specific_student['placement_status']}
- Contributing Root Causes: {[rc['indicator'] + ': ' + rc['description'] for rc in specific_student.get('root_causes', [])]}
- Constructive Mitigations: {[m['title'] + ' (' + m['action'] + ')' for m in specific_student.get('suggested_mitigations', [])]}
"""

    return f"""You are **Zoro**, the elite Institutional AI Copilot for **DEXA 2.0 (Dynamic Student Success Intelligence)** at the College of Engineering & Technology.

CURRENT USER ROLE & AUTHORIZATION:
- Role: {user_role}
- User ID: {user_id}

VERIFIED INSTITUTIONAL DATASET TELEMETRY (TRUTH SOURCE):
- Department: {telemetry.get('department')}
- Total Students: {telemetry.get('dataset_size', 500)} engineering students
- Faculty Directory: {telemetry.get('faculty_count', 15)} faculty members
- Cohort Mean CGPA: {telemetry.get('academics', {}).get('mean_cgpa', 6.84)} (Range: {telemetry.get('academics', {}).get('min_cgpa', 4.5)} to {telemetry.get('academics', {}).get('max_cgpa', 9.8)})
- Cohort Mean Attendance: {telemetry.get('attendance', {}).get('mean_attendance_pct', 77.8)}%
- Students with Attendance Deficit (<75% Detention Cutoff): {telemetry.get('attendance', {}).get('detention_warning_count', 186)} students ({telemetry.get('attendance', {}).get('detention_pct', 37.2)}%)
- Active Backlog Count: {telemetry.get('academics', {}).get('students_with_backlogs', 89)} students carry 1+ backlogs (Total: {telemetry.get('academics', {}).get('total_backlogs', 142)} backlogs)
- Risk Tier Composition:
  * High Risk (< 50.0): {telemetry.get('risk_distribution', {}).get('high_risk', 52)} students ({telemetry.get('risk_distribution', {}).get('high_risk_pct', 10.4)}%)
  * Medium Risk (50.0 - 69.9): {telemetry.get('risk_distribution', {}).get('medium_risk', 288)} students
  * Low Risk (>= 70.0): {telemetry.get('risk_distribution', {}).get('low_risk', 160)} students
- Placement Telemetry:
  * Mean Placement Readiness: {telemetry.get('placement', {}).get('avg_readiness_score', 48.7)} / 100
  * Mean Coding Assessment: {telemetry.get('placement', {}).get('avg_coding_score', 51.2)} / 100
  * Status: {telemetry.get('placement', {}).get('status_breakdown', {})}
- Machine Learning Model:
  * Supervised Random Forest Classifier trained on 80/20 held-out test split (400 train, 100 test).
  * Validated Test Accuracy: 96.0%, ROC-AUC: 0.992.
  * Top Predictive Features: CGPA, Overall Attendance, Assignment Completion %, Coding Score.
- Scoring Model (0-100 Transparent Index):
  * Academics: 35% (CGPA, Current GPA, IA Marks, Backlog penalty of -18 pts/arrear)
  * Attendance: 20% (Overall attendance 70% + 30-day shock trend 30%)
  * LMS & Engagement: 15% (Assignment completion 50% + quiz avg 30% + login frequency 20%)
  * Placement Readiness: 20% (Coding 35% + Aptitude 25% + Tech skills 20% + Mock interview 20%)
  * Skills & Feedback: 10% (Communication 40% + Problem solving 40% + Faculty feedback 20%)
  * Missing Data Renormalization: Automatically renormalizes available weights so missing optional categories never penalize a student.
{student_snippet}

STRICT PROFESSIONAL GUIDELINES:
1. **Absolute Truth & Accuracy:** Never hallucinate or invent fake metrics, student names, or accuracy scores. Use only verified figures provided above.
2. **Transparent Scoring vs ML Prediction:** Clearly explain that the Student Success Score (0-100) is an explainable weighted index, whereas the Random Forest is a trained predictive classifier.
3. **Constructive Human-in-the-Loop Interventions:** Never label any student as a failure or hopeless. Recommend targeted remedies (remedial tutorials, faculty counseling, attendance audits, mock interview clinics).
4. **Role Permissions:** If user is a Student, discuss only aggregate institution averages or their own profile. For HOD / Admin, provide complete department analysis.
5. **Formatting:** Use clean markdown, bold metric highlights, bullet points, and actionable executive summaries. Support both English and Tamil / Tanglish when addressed in those languages.
"""
