"""
DEXA ML Engine - Random Forest Classifier, Explainable Root Cause Analyzer & Recovery Simulator
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, roc_auc_score, precision_score, recall_score, f1_score

KEY_FEATURES = [
    'cgpa',
    'attendance_overall_pct',
    'coding_score',
    'aptitude_score',
    'assignment_completion_pct',
    'communication_score'
]

def train_rf_model(df: pd.DataFrame):
    """
    Train Random Forest Classifier to predict academic_risk_flag.
    Returns:
        model: Trained RandomForestClassifier
        metrics: dict of evaluation metrics (accuracy, roc_auc, precision, recall, f1)
        feature_importances: dict mapping feature name to importance score
    """
    X = df[KEY_FEATURES].copy()
    y = df['academic_risk_flag'].copy()

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    model = RandomForestClassifier(
        n_estimators=120,
        max_depth=6,
        min_samples_split=4,
        random_state=42,
        class_weight="balanced"
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]

    metrics = {
        'accuracy': float(accuracy_score(y_test, y_pred)),
        'roc_auc': float(roc_auc_score(y_test, y_prob)),
        'precision': float(precision_score(y_test, y_pred, zero_division=0)),
        'recall': float(recall_score(y_test, y_pred, zero_division=0)),
        'f1': float(f1_score(y_test, y_pred, zero_division=0)),
        'train_samples': len(X_train),
        'test_samples': len(X_test)
    }

    importances = dict(zip(KEY_FEATURES, model.feature_importances_))
    sorted_importances = dict(sorted(importances.items(), key=lambda x: x[1], reverse=True))

    return model, metrics, sorted_importances

def predict_student_risk(model, student_features: dict):
    """Predict risk probability (0.0 to 1.0) and boolean flag for a student."""
    row_dict = {
        'cgpa': float(student_features.get('cgpa', 6.0)),
        'attendance_overall_pct': float(student_features.get('attendance_overall_pct', 75.0)),
        'coding_score': float(student_features.get('coding_score', 50.0)),
        'aptitude_score': float(student_features.get('aptitude_score', 50.0)),
        'assignment_completion_pct': float(student_features.get('assignment_completion_pct', 75.0)),
        'communication_score': float(student_features.get('communication_score', 50.0))
    }
    feat_df = pd.DataFrame([row_dict])[KEY_FEATURES]

    prob = float(model.predict_proba(feat_df)[0][1])
    flag = int(model.predict(feat_df)[0])
    return flag, prob

def analyze_root_causes(student_row):
    """
    Examine failing indicators against institutional academic thresholds.
    Returns:
        root_causes: list of failing indicators with severity and evidence
        mitigations: list of targeted remedial actions
    """
    root_causes = []
    mitigations = []

    cgpa = float(student_row.get('cgpa', 0))
    attendance = float(student_row.get('attendance_overall_pct', 0))
    att_30d = float(student_row.get('attendance_last30days_pct', 0))
    coding = float(student_row.get('coding_score', 0))
    aptitude = float(student_row.get('aptitude_score', 0))
    assignments = float(student_row.get('assignment_completion_pct', 0))
    backlogs = int(student_row.get('backlogs', 0))
    lms_inactive = int(student_row.get('days_since_last_lms_login', 0))
    mentor = str(student_row.get('faculty_mentor', 'Assigned Mentor'))

    # 1. Attendance Check
    if attendance < 75.0:
        severity = "CRITICAL" if attendance < 65.0 else "HIGH"
        root_causes.append({
            "indicator": "Overall Attendance Deficit",
            "current": f"{attendance:.1f}%",
            "threshold": ">= 75.0%",
            "severity": severity,
            "description": f"Overall attendance is critically depressed at {attendance:.1f}%, jeopardizing semester exam eligibility."
        })
        mitigations.append({
            "type": "Attendance Counseling",
            "title": "Mandatory Faculty Counseling",
            "action": f"Immediate 1-on-1 counseling with {mentor} and bi-weekly attendance audit check-ins.",
            "impact": "+10-15% Projected Attendance Recovery"
        })

    # 2. 30-Day Attendance Sudden Drop
    if att_30d < (attendance - 10.0) and att_30d < 75.0:
        root_causes.append({
            "indicator": "Recent 30-Day Attendance Shock",
            "current": f"{att_30d:.1f}%",
            "threshold": f">= {attendance:.1f}%",
            "severity": "CRITICAL",
            "description": f"Last 30 days attendance plummeted to {att_30d:.1f}% compared to {attendance:.1f}% overall average."
        })

    # 3. CGPA Deficit
    if cgpa < 6.50:
        severity = "CRITICAL" if cgpa < 5.50 else "HIGH"
        root_causes.append({
            "indicator": "Cumulative GPA Deficiency",
            "current": f"{cgpa:.2f}",
            "threshold": ">= 6.50",
            "severity": severity,
            "description": f"Current CGPA of {cgpa:.2f} is significantly below standard graduation & placement cutoffs."
        })
        mitigations.append({
            "type": "Academic Tutoring",
            "title": "Targeted Core Subject Coaching",
            "action": "Enroll in department remedial tutorial sessions on IA question banks and foundational concepts.",
            "impact": "+0.8 to +1.2 Projected GPA Boost"
        })

    # 4. Backlog Load
    if backlogs > 0:
        root_causes.append({
            "indicator": "Active Course Arrears",
            "current": f"{backlogs} Backlog(s)",
            "threshold": "0 Backlogs",
            "severity": "CRITICAL",
            "description": f"Carrying {backlogs} active backlog(s), which creates severe cognitive load and prevents placement drives."
        })
        mitigations.append({
            "type": "Arrear Remediation",
            "title": "Fast-Track Arrear Clearance Plan",
            "action": "Special weekend doubt clearance with subject faculty prior to supplementary university exams.",
            "impact": "100% Backlog Clearance Pathway"
        })

    # 5. Coding Score Threshold
    if coding < 50.0:
        root_causes.append({
            "indicator": "Programming Competency Gap",
            "current": f"{coding:.1f} / 100",
            "threshold": ">= 50.0",
            "severity": "HIGH",
            "description": f"Coding assessment score of {coding:.1f} demonstrates vulnerability in technical problem-solving."
        })
        mitigations.append({
            "type": "Skill Building",
            "title": "Weekend Code Bootcamp & Peer Pair",
            "action": "Pair with a Hall of Fame Student Mentor for weekly LeetCode/HackerRank foundational sprints.",
            "impact": "+20 to +25 Points Coding Index"
        })

    # 6. Assignment Completion
    if assignments < 75.0:
        root_causes.append({
            "indicator": "Assignment Submission Lag",
            "current": f"{assignments:.1f}%",
            "threshold": ">= 75.0%",
            "severity": "MEDIUM",
            "description": f"Low assignment completion at {assignments:.1f}% reflects disengagement with continuous evaluations."
        })
        mitigations.append({
            "type": "Continuous Assessment",
            "title": "Lab Assistant Catch-Up Clinic",
            "action": "Supervised lab hours on Tuesday & Thursday afternoons to submit overdue problem sets.",
            "impact": "Elevate to 90%+ Submission Rate"
        })

    # 7. LMS Inactivity
    if lms_inactive >= 5:
        root_causes.append({
            "indicator": "Portal Disengagement",
            "current": f"{lms_inactive} Days Inactive",
            "threshold": "<= 3 Days",
            "severity": "MEDIUM",
            "description": f"Student has not accessed the college LMS portal in {lms_inactive} days."
        })
        mitigations.append({
            "type": "Digital Engagement",
            "title": "LMS Active Sync Alert",
            "action": "Send automated push notification and SMS nudge to resume weekly quiz participation.",
            "impact": "Active Daily Platform Engagement"
        })

    # Default healthy message if no major causes
    if not root_causes:
        root_causes.append({
            "indicator": "Optimal Academic Stability",
            "current": "Benchmark Met",
            "threshold": "Standard",
            "severity": "LOW",
            "description": "Student is currently maintaining healthy attendance, grades, and core skill assessments."
        })
        mitigations.append({
            "type": "Growth Enhancement",
            "title": "Honor Track & Leadership",
            "action": "Encourage participation in inter-college competitive hackathons, research publications, or club mentorship.",
            "impact": "Top Tier Placement Readiness"
        })

    return root_causes, mitigations

def simulate_recovery(model, student_row, delta_attendance=10.0, delta_assignment=15.0, delta_coding=15.0, delta_aptitude=10.0):
    """
    Project risk score and success recovery based on remedial interventions.
    """
    # Baseline
    base_features = {
        'cgpa': float(student_row.get('cgpa', 6.0)),
        'attendance_overall_pct': float(student_row.get('attendance_overall_pct', 70.0)),
        'coding_score': float(student_row.get('coding_score', 45.0)),
        'aptitude_score': float(student_row.get('aptitude_score', 45.0)),
        'assignment_completion_pct': float(student_row.get('assignment_completion_pct', 65.0)),
        'communication_score': float(student_row.get('communication_score', 50.0))
    }
    _, base_prob = predict_student_risk(model, base_features)
    base_success = float(student_row.get('student_success_score', 55.0))

    # Simulated New Values
    sim_attendance = min(100.0, base_features['attendance_overall_pct'] + delta_attendance)
    sim_assignment = min(100.0, base_features['assignment_completion_pct'] + delta_assignment)
    sim_coding = min(100.0, base_features['coding_score'] + delta_coding)
    sim_aptitude = min(100.0, base_features['aptitude_score'] + delta_aptitude)

    # Estimate potential CGPA rebound from attendance and assignment completion
    cgpa_bump = min(1.0, (delta_attendance * 0.02) + (delta_assignment * 0.015))
    sim_cgpa = min(10.0, base_features['cgpa'] + cgpa_bump)

    sim_features = {
        'cgpa': sim_cgpa,
        'attendance_overall_pct': sim_attendance,
        'coding_score': sim_coding,
        'aptitude_score': sim_aptitude,
        'assignment_completion_pct': sim_assignment,
        'communication_score': base_features['communication_score']
    }

    sim_flag, sim_prob = predict_student_risk(model, sim_features)

    # Rebound in Success Score
    prob_drop = base_prob - sim_prob
    pct_risk_reduction = (prob_drop / max(0.001, base_prob)) * 100.0 if base_prob > 0 else 0.0
    projected_success = min(100.0, base_success + (prob_drop * 25.0) + (delta_coding * 0.15) + (delta_attendance * 0.12))
    success_delta = projected_success - base_success

    return {
        'base_prob': base_prob,
        'sim_prob': sim_prob,
        'prob_drop': max(0.0, prob_drop),
        'pct_risk_reduction': max(0.0, pct_risk_reduction),
        'base_success': base_success,
        'projected_success': projected_success,
        'success_delta': max(0.0, success_delta),
        'sim_features': sim_features,
        'sim_flag': sim_flag,
        'summary': (
            f"Improving attendance by +{delta_attendance:.0f}% (to {sim_attendance:.1f}%) "
            f"and assignment completion by +{delta_assignment:.0f}% (to {sim_assignment:.1f}%) "
            f"reduces academic risk probability from {base_prob*100:.1f}% to {sim_prob*100:.1f}% "
            f"({pct_risk_reduction:.1f}% relative risk drop) and raises Student Success Score from "
            f"{base_success:.1f} to {projected_success:.1f} (+{success_delta:.1f} pts)."
        )
    }
