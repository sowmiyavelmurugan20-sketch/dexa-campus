"""
DEXA Student Segmentation & Prioritized Intervention Pipeline
Derives deterministic, explainable student cohorts from multi-dimensional data
"""

import pandas as pd
import numpy as np

SEGMENT_DEFINITIONS = {
    "High Academic — Low Placement Readiness": {
        "description": "Students with strong academic coursework (CGPA >= 7.50) but lagging behind in technical problem-solving or coding assessments (Coding < 50 or PAT Readiness < 50).",
        "action_priority": "Medium",
        "primary_intervention": "Fast-track Data Structures bootcamp & mock interview practice"
    },
    "Disengaged — Needs Urgent Intervention": {
        "description": "Students with acute attendance shortages (< 75%) combined with portal inactivity (>= 5 days idle) and low assignment submission rates (< 65%).",
        "action_priority": "Critical",
        "primary_intervention": "Mandatory faculty attendance counseling & daily check-in contract"
    },
    "Low Academic — High Engagement": {
        "description": "Students struggling academically (CGPA < 6.00 or active arrears) despite regular LMS logins and sincere assignment effort.",
        "action_priority": "High",
        "primary_intervention": "Core subject remedial coaching & IA question bank mentoring"
    },
    "High Achiever — Placement Ready": {
        "description": "Consistently strong performance across all dimensions (CGPA >= 7.5, Attendance >= 80%, Coding >= 65, PAT Readiness >= 65).",
        "action_priority": "Low (Honors Track)",
        "primary_intervention": "Peer leadership, research collaboration & tier-1 product hackathons"
    },
    "Average — Steady": {
        "description": "Balanced, consistent baseline performers tracking within healthy institutional parameters without acute deficits.",
        "action_priority": "Standard",
        "primary_intervention": "Routine semester mentoring review & career milestone checkpoints"
    }
}

def classify_student_segment(row: pd.Series) -> str:
    """Classify a single student record into an explainable segment."""
    cgpa = float(row.get('cgpa', 6.0))
    coding = float(row.get('coding_score', 50.0))
    pat_readiness = float(row.get('placement_readiness_score', 50.0))
    attendance = float(row.get('attendance_overall_pct', 75.0))
    lms_inactive = float(row.get('days_since_last_lms_login', 2.0))
    assignments = float(row.get('assignment_completion_pct', 75.0))
    logins_wk = float(row.get('lms_logins_per_week', 3.0))
    backlogs = float(row.get('backlogs', 0))

    # 1. High Academic - Low Placement
    if cgpa >= 7.50 and (coding < 50.0 or pat_readiness < 50.0):
        return "High Academic — Low Placement Readiness"

    # 2. Disengaged - Urgent
    if attendance < 75.0 and (lms_inactive >= 5.0 or assignments < 65.0):
        return "Disengaged — Needs Urgent Intervention"

    # 3. Low Academic - High Engagement
    if (cgpa < 6.00 or backlogs > 0) and (logins_wk >= 4.0 or assignments >= 75.0):
        return "Low Academic — High Engagement"

    # 4. High Achiever
    if cgpa >= 7.50 and pat_readiness >= 65.0 and attendance >= 80.0 and backlogs == 0:
        return "High Achiever — Placement Ready"

    # 5. Default
    return "Average — Steady"

def apply_student_segmentation(df: pd.DataFrame) -> pd.DataFrame:
    """Compute and assign 'student_segment' column across the dataframe."""
    df_out = df.copy()
    df_out['student_segment'] = df_out.apply(classify_student_segment, axis=1)
    return df_out

def generate_prioritized_intervention_queue(df: pd.DataFrame) -> pd.DataFrame:
    """
    Build prioritized list of student interventions based on risk level and segment.
    """
    queue = []
    for _, row in df.iterrows():
        segment = row.get('student_segment', classify_student_segment(row))
        seg_meta = SEGMENT_DEFINITIONS.get(segment, SEGMENT_DEFINITIONS["Average — Steady"])

        risk = str(row.get('risk_level', 'Low'))
        cgpa = float(row.get('cgpa', 6.0))
        att = float(row.get('attendance_overall_pct', 75.0))
        backlogs = int(row.get('backlogs', 0))

        # Severity score for sorting (higher = more urgent)
        urgency_score = 0
        if risk == "High":
            urgency_score += 50
        elif risk == "Medium":
            urgency_score += 25

        if att < 75.0:
            urgency_score += (75.0 - att) * 1.5
        if backlogs > 0:
            urgency_score += backlogs * 10
        if cgpa < 6.0:
            urgency_score += (6.0 - cgpa) * 15

        if urgency_score > 15: # Filter to students needing attention
            status = "Pending Action" if urgency_score > 35 else "Under Review"
            queue.append({
                "student_id": row['student_id'],
                "roll_number": row.get('roll_number', '-'),
                "name": row['name'],
                "year": row['year'],
                "section": row['section'],
                "risk_level": risk,
                "urgency_score": round(urgency_score, 1),
                "segment": segment,
                "cgpa": cgpa,
                "attendance_pct": att,
                "backlogs": backlogs,
                "faculty_mentor": row.get('faculty_mentor', 'Unassigned'),
                "recommended_action": seg_meta['primary_intervention'],
                "status": status
            })

    df_queue = pd.DataFrame(queue)
    if not df_queue.empty:
        df_queue = df_queue.sort_values(by="urgency_score", ascending=False).reset_index(drop=True)
    return df_queue
