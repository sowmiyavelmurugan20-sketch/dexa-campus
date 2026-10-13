"""
DEXA Dual-Mode Assistant Engine - Powered by Real Google Gemini GenAI
Integrates Campus Vibe & Sentiment Telemetry with Dynamic Academic Study Intelligence.
"""

from typing import List, Dict, Any, Optional
import pandas as pd
from gemini_service import chat_with_gemini, is_gemini_configured, get_ai_service_status

SUGGESTED_VIBE_PROMPTS = [
    "What is the overall campus mood and satisfaction?",
    "Which students need immediate attendance follow-up?",
    "Why are students in 3rd year carrying backlogs?",
    "Who are the top performers by Student Success Score?",
    "Explain DEXA's Student Success Score formula and weights",
    "Tell me about student STU0005 and recommend interventions"
]

SUGGESTED_STUDY_PROMPTS = [
    "Explain Dijkstra's Algorithm and its time complexity",
    "How can a student improve their coding score from 40 to 80?",
    "Give me a 30-day revision schedule for campus placement interviews",
    "What is the difference between TCP and UDP in computer networks?",
    "Explain Overfitting vs Underfitting in Machine Learning",
    "What are the best strategies to clear backlogs in Operating Systems?"
]


def analyze_campus_vibe_telemetry(df: pd.DataFrame) -> dict:
    """Compute holistic campus mood, stress metrics, and satisfaction telemetry from actual dataset."""
    if df.empty:
        return {
            "vibe_score": 75.0,
            "vibe_status": "Neutral ⚖️",
            "vibe_sentiment": "No student records available.",
            "avg_satisfaction": 3.5,
            "avg_faculty_feedback": 3.5,
            "backlog_students": 0,
            "backlog_pct": 0.0,
            "att_stress_count": 0,
            "att_stress_pct": 0.0,
            "high_risk_count": 0
        }

    avg_satisfaction = float(df['student_satisfaction_1to5'].mean())
    avg_faculty_feedback = float(df['faculty_feedback_1to5'].mean())

    backlog_students = int((df['backlogs'] > 0).sum())
    backlog_pct = float(backlog_students / len(df) * 100.0)

    att_stress_count = int((df['attendance_overall_pct'] < 75.0).sum())
    att_stress_pct = float(att_stress_count / len(df) * 100.0)

    high_risk_count = int((df['risk_level'] == 'High').sum())

    vibe_score = (avg_satisfaction / 5.0 * 50.0) + (avg_faculty_feedback / 5.0 * 30.0) + ((100 - backlog_pct) * 0.1) + ((100 - att_stress_pct) * 0.1)
    vibe_score = max(0.0, min(100.0, vibe_score))

    if vibe_score >= 80:
        vibe_status = "Vibrant & Thriving 🚀"
        vibe_sentiment = "Strong positive sentiment across academic and peer engagement."
    elif vibe_score >= 65:
        vibe_status = "Balanced & Steady ⚖️"
        vibe_sentiment = "Moderate campus sentiment with localized pockets of exam & assignment pressure."
    else:
        vibe_status = "Elevated Stress Alert ⚠️"
        vibe_sentiment = "High collective anxiety noted around backlogs and attendance shortages."

    return {
        "vibe_score": vibe_score,
        "vibe_status": vibe_status,
        "vibe_sentiment": vibe_sentiment,
        "avg_satisfaction": avg_satisfaction,
        "avg_faculty_feedback": avg_faculty_feedback,
        "backlog_students": backlog_students,
        "backlog_pct": backlog_pct,
        "att_stress_count": att_stress_count,
        "att_stress_pct": att_stress_pct,
        "high_risk_count": high_risk_count
    }


def process_chatbot_query(
    query: str,
    df: pd.DataFrame,
    mode: str = "vibe",
    history: Optional[List[Dict[str, str]]] = None,
    df_staff: Optional[pd.DataFrame] = None,
    user_role: str = "HOD / Admin",
    user_id: str = "admin"
) -> Dict[str, Any]:
    """
    Route conversation to real Gemini AI service with verified dataset telemetry.
    Returns:
        dict: {"role": "assistant", "content": str, "configured": bool, "model_used": str, "error": Optional[str]}
    """
    if history is None:
        history = []
    if df_staff is None:
        df_staff = pd.DataFrame()

    return chat_with_gemini(
        message=query,
        history=history,
        df_students=df,
        df_staff=df_staff,
        user_role=user_role,
        user_id=user_id,
        mode=mode
    )
