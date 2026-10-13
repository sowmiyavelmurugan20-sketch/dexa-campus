"""
DEXA Scoring Engine - Trustworthy, Explainable Student Success Score (0-100)
Transparent Multi-Criteria Weighted Index with Missing Data Renormalization
"""

import numpy as np
import pandas as pd

# Default Configurable Weights
DEFAULT_WEIGHTS = {
    'academics': 0.35,
    'attendance': 0.20,
    'lms_engagement': 0.15,
    'placement_readiness': 0.20,
    'skills_feedback': 0.10
}

def calculate_student_success_score(row: pd.Series, custom_weights: dict = None) -> dict:
    """
    Compute a transparent, documented 0-100 Student Success Score.
    Categories:
      1. Academics (35%): CGPA (scale 10->100), current sem GPA, backlog penalty, IA marks.
      2. Attendance (20%): Overall attendance %, 30-day attendance trend.
      3. LMS & Engagement (15%): Assignment completion %, LMS logins/wk, quiz avg score.
      4. Placement Readiness (20%): Coding score, aptitude score, mock interview score, tech skills.
      5. Skills & Feedback (10%): Communication score, problem solving, faculty feedback.

    Handles missing data transparently by renormalizing weights across available categories.
    Returns:
      dict with total_score, category_scores, weighted_contributions, drivers, completeness_pct.
    """
    weights = custom_weights.copy() if custom_weights else DEFAULT_WEIGHTS.copy()
    available_weights = {}
    category_scores = {}
    indicator_values = {}

    # 1. ACADEMICS CATEGORY
    try:
        cgpa = float(row.get('cgpa', np.nan))
        current_gpa = float(row.get('current_sem_gpa', cgpa))
        backlogs = float(row.get('backlogs', 0))
        ia_avg = (float(row.get('ia1_marks_50', 25)) + float(row.get('ia2_marks_50', 25)) + float(row.get('ia3_marks_50', 25))) / 1.5

        # Normalize CGPA (0-10 -> 0-100)
        cgpa_score = np.clip(cgpa * 10.0, 0, 100)
        gpa_score = np.clip(current_gpa * 10.0, 0, 100)
        ia_score = np.clip(ia_avg, 0, 100)
        # Backlog deduction: -15 pts per active backlog
        backlog_factor = max(0, 100.0 - (backlogs * 18.0))

        acad_composite = (cgpa_score * 0.45) + (gpa_score * 0.25) + (ia_score * 0.15) + (backlog_factor * 0.15)
        category_scores['academics'] = float(np.clip(acad_composite, 0, 100))
        available_weights['academics'] = weights['academics']
        indicator_values['CGPA'] = cgpa
        indicator_values['Backlogs'] = int(backlogs)
    except Exception:
        pass

    # 2. ATTENDANCE CATEGORY
    try:
        att_overall = float(row.get('attendance_overall_pct', np.nan))
        att_30d = float(row.get('attendance_last30days_pct', att_overall))

        if not np.isnan(att_overall):
            # 70% overall attendance + 30% recent trend
            att_composite = (att_overall * 0.70) + (att_30d * 0.30)
            category_scores['attendance'] = float(np.clip(att_composite, 0, 100))
            available_weights['attendance'] = weights['attendance']
            indicator_values['Attendance Overall %'] = att_overall
            indicator_values['Attendance 30-Day %'] = att_30d
    except Exception:
        pass

    # 3. LMS & ENGAGEMENT CATEGORY
    try:
        assign_pct = float(row.get('assignment_completion_pct', np.nan))
        quiz_score = float(row.get('lms_quiz_avg_score', 60.0))
        logins = float(row.get('lms_logins_per_week', 3.0))
        login_score = np.clip(logins * 14.0, 0, 100) # 7 logins/wk ~ 98 pts

        if not np.isnan(assign_pct):
            lms_composite = (assign_pct * 0.50) + (quiz_score * 0.30) + (login_score * 0.20)
            category_scores['lms_engagement'] = float(np.clip(lms_composite, 0, 100))
            available_weights['lms_engagement'] = weights['lms_engagement']
            indicator_values['Assignment Completion %'] = assign_pct
            indicator_values['LMS Logins / Wk'] = logins
    except Exception:
        pass

    # 4. PLACEMENT READINESS CATEGORY
    try:
        coding = float(row.get('coding_score', np.nan))
        aptitude = float(row.get('aptitude_score', 50.0))
        mock_score = float(row.get('mock_interview_score', 50.0))
        tech_score = float(row.get('technical_skill_score', 50.0))

        if not np.isnan(coding):
            pat_composite = (coding * 0.35) + (aptitude * 0.25) + (tech_score * 0.20) + (mock_score * 0.20)
            category_scores['placement_readiness'] = float(np.clip(pat_composite, 0, 100))
            available_weights['placement_readiness'] = weights['placement_readiness']
            indicator_values['Coding Score'] = coding
            indicator_values['Aptitude Score'] = aptitude
    except Exception:
        pass

    # 5. SKILLS & FEEDBACK CATEGORY
    try:
        comm = float(row.get('communication_score', 50.0))
        ps = float(row.get('problem_solving_score', 50.0))
        faculty_fb = float(row.get('faculty_feedback_1to5', 3.5)) * 20.0 # scale to 100

        skills_composite = (comm * 0.40) + (ps * 0.40) + (faculty_fb * 0.20)
        category_scores['skills_feedback'] = float(np.clip(skills_composite, 0, 100))
        available_weights['skills_feedback'] = weights['skills_feedback']
        indicator_values['Communication Score'] = comm
        indicator_values['Problem Solving'] = ps
    except Exception:
        pass

    # RENORMALIZE WEIGHTS FOR MISSING DATA TRANSPARENCY
    total_avail_weight = sum(available_weights.values())
    if total_avail_weight > 0:
        normalized_weights = {k: v / total_avail_weight for k, v in available_weights.items()}
    else:
        normalized_weights = {k: 0.2 for k in DEFAULT_WEIGHTS}
        category_scores = {k: 50.0 for k in DEFAULT_WEIGHTS}

    total_score = sum(category_scores[k] * normalized_weights[k] for k in category_scores)
    total_score = float(np.clip(round(total_score, 1), 0, 100))

    # Calculate Data Completeness %
    total_categories = len(DEFAULT_WEIGHTS)
    available_categories = len(available_weights)
    completeness_pct = round((available_categories / total_categories) * 100.0, 1)

    # DRIVER ANALYSIS: Identify strongest positive and negative drivers
    drivers_positive = []
    drivers_negative = []

    # Benchmark comparisons
    if category_scores.get('academics', 0) >= 75:
        drivers_positive.append("Strong Academic Performance (CGPA & exam consistency)")
    elif category_scores.get('academics', 100) < 60:
        drivers_negative.append("Academic Disruption (Low GPA or active arrears)")

    if category_scores.get('attendance', 0) >= 85:
        drivers_positive.append("Excellent Attendance & Lecture Regularity (>= 85%)")
    elif category_scores.get('attendance', 100) < 75:
        drivers_negative.append("Attendance Shortage (< 75% detention threshold)")

    if category_scores.get('placement_readiness', 0) >= 70:
        drivers_positive.append("Advanced Placement Competency (Coding & Aptitude)")
    elif category_scores.get('placement_readiness', 100) < 50:
        drivers_negative.append("Placement Readiness Deficit (Needs technical practice)")

    if category_scores.get('lms_engagement', 0) >= 80:
        drivers_positive.append("High LMS Engagement & Prompt Assignment Submissions")
    elif category_scores.get('lms_engagement', 100) < 65:
        drivers_negative.append("LMS Submission Lag or Portal Inactivity")

    if not drivers_positive:
        drivers_positive.append("Consistent baseline performance across active modules")
    if not drivers_negative:
        drivers_negative.append("No critical negative drivers detected")

    # Risk Tier Assignment (Rule-Based Score Bands)
    if total_score < 50.0:
        risk_tier = "High"
    elif total_score < 70.0:
        risk_tier = "Medium"
    else:
        risk_tier = "Low"

    return {
        'total_score': total_score,
        'risk_tier': risk_tier,
        'category_scores': category_scores,
        'normalized_weights': normalized_weights,
        'completeness_pct': completeness_pct,
        'positive_drivers': drivers_positive[:2],
        'negative_drivers': drivers_negative[:2],
        'drivers_positive': drivers_positive[:2],
        'drivers_negative': drivers_negative[:2],
        'indicator_values': indicator_values
    }


def batch_compute_success_scores(df: pd.DataFrame, custom_weights: dict = None) -> pd.DataFrame:
    """
    Compute scores for an entire dataframe of students.
    Adds 'computed_success_score', 'computed_risk_tier', 'data_completeness_pct'.
    """
    scores = []
    tiers = []
    completeness = []

    for _, row in df.iterrows():
        res = calculate_student_success_score(row, custom_weights)
        scores.append(res['total_score'])
        tiers.append(res['risk_tier'])
        completeness.append(res['completeness_pct'])

    df_out = df.copy()
    df_out['computed_success_score'] = scores
    df_out['computed_risk_tier'] = tiers
    df_out['data_completeness_pct'] = completeness
    return df_out
