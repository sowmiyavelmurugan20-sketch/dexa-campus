"""
DEXA 2.0 Enterprise Intelligence Server (FastAPI + Python Analytics Engine)
Serves REST API and modern enterprise React SPA at http://localhost:8501
"""

import os
import io
import math
import json
import urllib.parse
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

# Load environment variables from .env if present
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from fastapi import FastAPI, HTTPException, Query, UploadFile, File, Response, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse, StreamingResponse
from pydantic import BaseModel

# Local Data Science & Analytics Engines
from data_engine import (
    load_student_dataset,
    load_staff_dataset,
    authenticate_user,
    validate_and_import_student_data,
    get_image_base64_or_fallback,
    REQUIRED_STUDENT_COLUMNS
)
from auth_engine import (
    create_session,
    get_session,
    revoke_session,
    can_access_student_record,
    VALID_ROLES
)
from scoring_engine import (
    calculate_student_success_score,
    batch_compute_success_scores,
    DEFAULT_WEIGHTS
)
from segmentation_engine import (
    classify_student_segment,
    apply_student_segmentation,
    generate_prioritized_intervention_queue,
    SEGMENT_DEFINITIONS
)
from ml_engine import (
    train_rf_model,
    predict_student_risk,
    analyze_root_causes,
    simulate_recovery,
    KEY_FEATURES
)
from report_engine import (
    generate_department_pdf,
    generate_student_pdf
)
from chatbot_engine import (
    process_chatbot_query,
    analyze_campus_vibe_telemetry,
    SUGGESTED_VIBE_PROMPTS,
    SUGGESTED_STUDY_PROMPTS
)
from gemini_service import (
    get_ai_service_status,
    is_gemini_configured
)

from notifications_engine import (
    init_mock_notifications,
    init_mock_grievances,
    init_mock_interventions
)

# -------------------------------------------------------------------------
# JSON RESPONSE SANITIZATION (PREVENTS NaN/Inf CRASHES)
# -------------------------------------------------------------------------
def sanitize_for_json(val: Any) -> Any:
    if val is None:
        return None
    if isinstance(val, (float, np.floating)):
        f = float(val)
        if math.isnan(f) or math.isinf(f):
            return None
        return f
    if isinstance(val, (int, np.integer)):
        return int(val)
    if isinstance(val, (bool, np.bool_)):
        return bool(val)
    if isinstance(val, dict):
        return {str(k): sanitize_for_json(v) for k, v in val.items()}
    if isinstance(val, (list, tuple, set)):
        return [sanitize_for_json(x) for x in val]
    if isinstance(val, np.ndarray):
        return [sanitize_for_json(x) for x in val.tolist()]
    if pd.isna(val):
        return None
    return val

class SafeJSONResponse(JSONResponse):
    def render(self, content: Any) -> bytes:
        clean_content = sanitize_for_json(content)
        return json.dumps(
            clean_content,
            ensure_ascii=False,
            allow_nan=False,
            indent=None,
            separators=(",", ":"),
        ).encode("utf-8")

# -------------------------------------------------------------------------
# INITIALIZE MASTER IN-MEMORY STATE
# -------------------------------------------------------------------------
print("[INFO] Initializing DEXA 2.0 Analytics Engine...")
MASTER_STUDENTS_DF = load_student_dataset()
MASTER_STAFF_DF = load_staff_dataset()
CUSTOM_WEIGHTS = DEFAULT_WEIGHTS.copy()

RF_MODEL, MODEL_METRICS, MODEL_IMPORTANCES = train_rf_model(MASTER_STUDENTS_DF)
NOTIFICATIONS_STORE = init_mock_notifications(MASTER_STUDENTS_DF)
GRIEVANCES_STORE = init_mock_grievances()
INTERVENTIONS_STORE = init_mock_interventions(MASTER_STUDENTS_DF)

print(f"[INFO] DEXA Engine Ready: {len(MASTER_STUDENTS_DF)} students, {len(MASTER_STAFF_DF)} faculty members loaded.")


# -------------------------------------------------------------------------
# FASTAPI APP SETUP & CORS
# -------------------------------------------------------------------------
app = FastAPI(
    title="DEXA Dynamic Student Success Intelligence API",
    version="2.0.0",
    description="Enterprise Academic Analytics & Intervention Platform",
    default_response_class=SafeJSONResponse
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------------------------------------------------------------------------
# PYDANTIC SCHEMAS
# -------------------------------------------------------------------------
class LoginRequest(BaseModel):
    user_id: Optional[str] = None
    username: Optional[str] = None
    password: str

def get_current_session(request: Request) -> Optional[Dict[str, Any]]:
    """Extract and validate active session from HttpOnly cookie or Bearer token."""
    token = request.cookies.get("dexa_session")
    if not token:
        auth_hdr = request.headers.get("Authorization", "")
        if auth_hdr.startswith("Bearer "):
            token = auth_hdr.split(" ", 1)[1].strip()
    if token:
        return get_session(token)
    return None

class WeightsUpdateRequest(BaseModel):
    academics: float
    attendance: float
    lms_engagement: float
    placement_readiness: float
    skills_feedback: float

class InterventionCreateRequest(BaseModel):
    student_id: str
    category: str
    notes: str
    follow_up_date: str
    status: str

class InterventionUpdateRequest(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None
    follow_up_date: Optional[str] = None

class SimulationRequest(BaseModel):
    delta_attendance: float = 10.0
    delta_assignment: float = 15.0
    delta_coding: float = 15.0
    delta_aptitude: float = 10.0

class ChatRequest(BaseModel):
    message: str
    mode: str = "vibe"
    history: Optional[List[Dict[str, str]]] = None
    role: Optional[str] = "HOD / Admin"
    user_id: Optional[str] = "admin"


class GrievanceCreateRequest(BaseModel):
    category: str
    urgency: str
    comment: str


# -------------------------------------------------------------------------
# FILTERING HELPER
# -------------------------------------------------------------------------
def filter_dataframe(
    df: pd.DataFrame,
    year: Optional[str] = None,
    semester: Optional[str] = None,
    section: Optional[str] = None,
    risk_tier: Optional[str] = None,
    mentor: Optional[str] = None,
    segment: Optional[str] = None,
    search: Optional[str] = None
) -> pd.DataFrame:
    filtered = df.copy()
    if year and year != "all":
        filtered = filtered[filtered['year'].astype(str) == str(year)]
    if section and section != "all":
        filtered = filtered[filtered['section'].astype(str) == str(section)]
    if risk_tier and risk_tier != "all":
        filtered = filtered[filtered['risk_level'].str.lower() == risk_tier.lower()]
    if mentor and mentor != "all":
        filtered = filtered[filtered['faculty_mentor'].str.lower() == mentor.lower()]
    if segment and segment != "all":
        filtered = filtered[filtered['student_segment'] == segment]
    if search and search.strip():
        q = search.strip().lower()
        filtered = filtered[
            filtered['student_id'].str.lower().str.contains(q) |
            filtered['name'].str.lower().str.contains(q) |
            filtered['roll_number'].str.lower().str.contains(q) |
            filtered['faculty_mentor'].str.lower().str.contains(q) |
            filtered['student_segment'].str.lower().str.contains(q)
        ]
    return filtered


# -------------------------------------------------------------------------
# REST API ENDPOINTS
# -------------------------------------------------------------------------

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "total_students": len(MASTER_STUDENTS_DF),
        "total_staff": len(MASTER_STAFF_DF),
        "ml_accuracy": MODEL_METRICS["accuracy"],
        "ml_roc_auc": MODEL_METRICS["roc_auc"]
    }


@app.post("/api/auth/login")
def login(req: LoginRequest, response: Response):
    u_id = (req.user_id or req.username or "").strip()
    res = authenticate_user(u_id, req.password, MASTER_STUDENTS_DF, MASTER_STAFF_DF)
    if not res['authenticated']:
        raise HTTPException(status_code=401, detail=res['error'])

    # Create server-side session
    session_token = create_session(res, expiry_seconds=86400)
    response.set_cookie(
        key="dexa_session",
        value=session_token,
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=86400,
        path="/"
    )

    return {
        "authenticated": True,
        "token": session_token,
        "role": res['role'],
        "user_id": res['user_id'],
        "name": res['name'],
        "email": res.get('email', ''),
        "photo_url": res['profile_record'].get('photo_url', '') if isinstance(res['profile_record'], dict) else '',
        "profile": res['profile_record']
    }


@app.get("/api/auth/me")
def get_me(request: Request):
    session = get_current_session(request)
    if not session:
        raise HTTPException(status_code=401, detail="No active session. Please sign in.")
    u = session.get("user", {})
    return {
        "authenticated": True,
        "role": session.get("role"),
        "user_id": session.get("user_id"),
        "linked_id": session.get("linked_id"),
        "name": u.get("name"),
        "email": u.get("email"),
        "photo_url": u.get("profile_record", {}).get("photo_url", "") if isinstance(u.get("profile_record"), dict) else "",
        "profile": u.get("profile_record", {})
    }


@app.post("/api/auth/logout")
def logout(request: Request, response: Response):
    token = request.cookies.get("dexa_session")
    if not token:
        auth_hdr = request.headers.get("Authorization", "")
        if auth_hdr.startswith("Bearer "):
            token = auth_hdr.split(" ", 1)[1].strip()
    if token:
        revoke_session(token)
    response.delete_cookie(key="dexa_session", path="/")
    return {"authenticated": False, "message": "Successfully logged out."}


@app.get("/api/overview")
def get_overview(
    year: Optional[str] = "all",
    semester: Optional[str] = "all",
    section: Optional[str] = "all",
    risk_tier: Optional[str] = "all",
    mentor: Optional[str] = "all"
):
    df_sub = filter_dataframe(MASTER_STUDENTS_DF, year=year, semester=semester, section=section, risk_tier=risk_tier, mentor=mentor)
    
    total_count = len(df_sub)
    if total_count == 0:
        return {
            "total_students": 0,
            "avg_cgpa": 0,
            "avg_attendance": 0,
            "high_risk_count": 0,
            "avg_success_score": 0,
            "data_completeness": 0,
            "risk_distribution": {"Low": 0, "Medium": 0, "High": 0},
            "score_histogram": [],
            "attendance_scatter": [],
            "ml_metrics": MODEL_METRICS,
            "top_urgent": []
        }

    high_risk_count = int((df_sub['risk_level'] == 'High').sum())
    med_risk_count = int((df_sub['risk_level'] == 'Medium').sum())
    low_risk_count = int((df_sub['risk_level'] == 'Low').sum())

    # Score distribution histogram bins (0-10, 10-20, ... 90-100)
    bins = [0, 20, 40, 50, 60, 70, 80, 90, 100]
    labels = ["0-20", "20-40", "40-50", "50-60", "60-70", "70-80", "80-90", "90-100"]
    hist_series = pd.cut(df_sub['student_success_score'], bins=bins, labels=labels, include_lowest=True).value_counts()
    score_histogram = [{"range": k, "count": int(v)} for k, v in hist_series.items()]

    # Scatter points sample for Attendance vs CGPA
    scatter_pts = []
    for _, r in df_sub.head(150).iterrows():
        scatter_pts.append({
            "student_id": r['student_id'],
            "name": r['name'],
            "cgpa": round(float(r['cgpa']), 2),
            "attendance": round(float(r['attendance_overall_pct']), 1),
            "risk_level": r['risk_level'],
            "backlogs": int(r['backlogs']),
            "mentor": r['faculty_mentor']
        })

    # Top urgent students
    q = generate_prioritized_intervention_queue(df_sub)
    top_urgent = q.head(6).to_dict(orient="records") if not q.empty else []

    return {
        "total_students": total_count,
        "avg_cgpa": round(float(df_sub['cgpa'].mean()), 2),
        "avg_attendance": round(float(df_sub['attendance_overall_pct'].mean()), 1),
        "high_risk_count": high_risk_count,
        "avg_success_score": round(float(df_sub['student_success_score'].mean()), 1),
        "data_completeness": round(float(df_sub['data_completeness_pct'].mean() if 'data_completeness_pct' in df_sub else 100.0), 1),
        "risk_distribution": {
            "Low": low_risk_count,
            "Medium": med_risk_count,
            "High": high_risk_count
        },
        "score_histogram": score_histogram,
        "attendance_scatter": scatter_pts,
        "ml_metrics": {
            **MODEL_METRICS,
            "importances": MODEL_IMPORTANCES
        },
        "top_urgent": top_urgent
    }


@app.get("/api/students")
def get_students(
    search: Optional[str] = None,
    year: Optional[str] = "all",
    section: Optional[str] = "all",
    risk_tier: Optional[str] = "all",
    mentor: Optional[str] = "all",
    segment: Optional[str] = "all",
    page: int = 1,
    limit: int = 15,
    sort_by: str = "student_id",
    sort_desc: bool = False
):
    df_sub = filter_dataframe(MASTER_STUDENTS_DF, year=year, section=section, risk_tier=risk_tier, mentor=mentor, segment=segment, search=search)
    
    if sort_by in df_sub.columns:
        df_sub = df_sub.sort_values(by=sort_by, ascending=not sort_desc)

    total_records = len(df_sub)
    total_pages = max(1, (total_records + limit - 1) // limit)
    start_idx = (page - 1) * limit
    paged_df = df_sub.iloc[start_idx:start_idx + limit]

    columns_to_return = [
        'student_id', 'roll_number', 'name', 'photo_url', 'department', 'year', 'section',
        'cgpa', 'current_sem_gpa', 'attendance_overall_pct', 'backlogs',
        'student_success_score', 'risk_level', 'student_segment', 'faculty_mentor',
        'coding_score', 'aptitude_score', 'placement_readiness_score', 'placement_status'
    ]
    records = paged_df[[c for c in columns_to_return if c in paged_df.columns]].to_dict(orient="records")

    return {
        "page": page,
        "limit": limit,
        "total_records": total_records,
        "total_pages": total_pages,
        "students": records
    }


@app.get("/api/students/{student_id}")
def get_student_detail(student_id: str):
    matches = MASTER_STUDENTS_DF[MASTER_STUDENTS_DF['student_id'].str.upper() == student_id.strip().upper()]
    if matches.empty:
        raise HTTPException(status_code=404, detail=f"Student {student_id} not found")

    student = matches.iloc[0]
    score_details = calculate_student_success_score(student, CUSTOM_WEIGHTS)
    root_causes, mitigations = analyze_root_causes(student)
    pred_flag, pred_prob = predict_student_risk(RF_MODEL, student.to_dict())

    # 360 Radar Dimensions
    categories = ['Coding', 'Aptitude', 'Tech Skills', 'Communication', 'Soft Skills', 'Problem Solving', 'Academics', 'Attendance']
    stu_vals = [
        float(student['coding_score']), float(student['aptitude_score']), float(student['technical_skill_score']),
        float(student['communication_score']), float(student['soft_skill_score']), float(student['problem_solving_score']),
        float(student['cgpa'] * 10.0), float(student['attendance_overall_pct'])
    ]
    batch_vals = [
        float(MASTER_STUDENTS_DF['coding_score'].mean()), float(MASTER_STUDENTS_DF['aptitude_score'].mean()), float(MASTER_STUDENTS_DF['technical_skill_score'].mean()),
        float(MASTER_STUDENTS_DF['communication_score'].mean()), float(MASTER_STUDENTS_DF['soft_skill_score'].mean()), float(MASTER_STUDENTS_DF['problem_solving_score'].mean()),
        float(MASTER_STUDENTS_DF['cgpa'].mean() * 10.0), float(MASTER_STUDENTS_DF['attendance_overall_pct'].mean())
    ]
    radar_data = [{"dimension": cat, "student": round(s, 1), "batch_average": round(b, 1)} for cat, s, b in zip(categories, stu_vals, batch_vals)]

    # Interventions for this student
    student_interventions = [it for it in INTERVENTIONS_STORE if it['student_id'] == student['student_id']]

    return {
        "student": student.to_dict(),
        "score_details": score_details,
        "root_causes": root_causes,
        "mitigations": mitigations,
        "ai_risk_prediction": {
            "flag": int(pred_flag),
            "probability": round(float(pred_prob), 4),
            "label": "High Risk" if pred_prob > 0.5 else "Low/Normal Risk"
        },
        "radar_data": radar_data,
        "interventions": student_interventions
    }


@app.post("/api/students/{student_id}/simulate")
def run_simulation(student_id: str, req: SimulationRequest):
    matches = MASTER_STUDENTS_DF[MASTER_STUDENTS_DF['student_id'].str.upper() == student_id.strip().upper()]
    if matches.empty:
        raise HTTPException(status_code=404, detail=f"Student {student_id} not found")

    student = matches.iloc[0]
    res = simulate_recovery(
        RF_MODEL, student,
        delta_attendance=req.delta_attendance,
        delta_assignment=req.delta_assignment,
        delta_coding=req.delta_coding,
        delta_aptitude=req.delta_aptitude
    )
    return res


@app.get("/api/interventions")
def get_interventions(status: Optional[str] = None):
    items = INTERVENTIONS_STORE
    if status and status != "all":
        items = [it for it in items if it['status'].lower() == status.lower()]
    return {
        "total": len(items),
        "interventions": items
    }


@app.post("/api/interventions")
def create_intervention(req: InterventionCreateRequest):
    matches = MASTER_STUDENTS_DF[MASTER_STUDENTS_DF['student_id'].str.upper() == req.student_id.strip().upper()]
    stu_name = matches.iloc[0]['name'] if not matches.empty else "Student"
    mentor = matches.iloc[0]['faculty_mentor'] if not matches.empty else "Faculty Mentor"

    new_id = f"INT-{len(INTERVENTIONS_STORE) + 1:03d}"
    record = {
        "id": new_id,
        "student_id": req.student_id.strip().upper(),
        "student_name": stu_name,
        "mentor": mentor,
        "category": req.category,
        "notes": req.notes,
        "follow_up_date": req.follow_up_date,
        "status": req.status,
        "logged_at": datetime.now().strftime("%b %d, %Y")
    }
    INTERVENTIONS_STORE.insert(0, record)
    return {"success": True, "intervention": record}


@app.put("/api/interventions/{intervention_id}")
def update_intervention(intervention_id: str, req: InterventionUpdateRequest):
    for it in INTERVENTIONS_STORE:
        if it['id'] == intervention_id:
            if req.status is not None:
                it['status'] = req.status
            if req.notes is not None:
                it['notes'] = req.notes
            if req.follow_up_date is not None:
                it['follow_up_date'] = req.follow_up_date
            return {"success": True, "intervention": it}
    raise HTTPException(status_code=404, detail=f"Intervention {intervention_id} not found")


@app.get("/api/segments")
def get_segments():
    counts = MASTER_STUDENTS_DF['student_segment'].value_counts().to_dict()
    res = []
    for name, meta in SEGMENT_DEFINITIONS.items():
        count = counts.get(name, 0)
        # sample students
        sample_df = MASTER_STUDENTS_DF[MASTER_STUDENTS_DF['student_segment'] == name].head(12)
        samples = sample_df[['student_id', 'roll_number', 'name', 'photo_url', 'cgpa', 'attendance_overall_pct', 'coding_score', 'placement_readiness_score', 'faculty_mentor']].to_dict(orient="records")
        res.append({
            "name": name,
            "count": count,
            "percentage": round(count / max(1, len(MASTER_STUDENTS_DF)) * 100, 1),
            "priority": meta["action_priority"],
            "description": meta["description"],
            "primary_intervention": meta["primary_intervention"],
            "students": samples
        })
    return res


@app.get("/api/academic-analytics")
def get_academic_analytics():
    return {
        "cgpa_min": round(float(MASTER_STUDENTS_DF['cgpa'].min()), 2),
        "cgpa_max": round(float(MASTER_STUDENTS_DF['cgpa'].max()), 2),
        "cgpa_mean": round(float(MASTER_STUDENTS_DF['cgpa'].mean()), 2),
        "total_backlogs": int(MASTER_STUDENTS_DF['backlogs'].sum()),
        "students_with_backlogs": int((MASTER_STUDENTS_DF['backlogs'] > 0).sum()),
        "ia_averages": {
            "ia1": round(float(MASTER_STUDENTS_DF['ia1_marks_50'].mean()), 1),
            "ia2": round(float(MASTER_STUDENTS_DF['ia2_marks_50'].mean()), 1),
            "ia3": round(float(MASTER_STUDENTS_DF['ia3_marks_50'].mean()), 1),
        },
        "subject_averages": {
            "mathematics": round(float(MASTER_STUDENTS_DF['mathematics_marks'].mean()), 1),
            "core_subject_1": round(float(MASTER_STUDENTS_DF['core_subject_1_marks'].mean()), 1),
            "core_subject_2": round(float(MASTER_STUDENTS_DF['core_subject_2_marks'].mean()), 1),
        },
        "year_cgpa_distribution": [
            {
                "year": f"Year {y}",
                "mean_cgpa": round(float(sub['cgpa'].mean()), 2),
                "count": len(sub),
                "backlogs": int(sub['backlogs'].sum())
            }
            for y, sub in MASTER_STUDENTS_DF.groupby('year')
        ]
    }


@app.get("/api/attendance-analytics")
def get_attendance_analytics():
    detention_list = MASTER_STUDENTS_DF[MASTER_STUDENTS_DF['attendance_overall_pct'] < 75.0].sort_values(by="attendance_overall_pct")
    det_records = detention_list[['student_id', 'roll_number', 'name', 'year', 'section', 'attendance_overall_pct', 'attendance_theory_pct', 'attendance_lab_pct', 'cgpa', 'backlogs', 'faculty_mentor', 'parent_mobile']].to_dict(orient="records")

    return {
        "overall_mean": round(float(MASTER_STUDENTS_DF['attendance_overall_pct'].mean()), 1),
        "theory_mean": round(float(MASTER_STUDENTS_DF['attendance_theory_pct'].mean()), 1),
        "lab_mean": round(float(MASTER_STUDENTS_DF['attendance_lab_pct'].mean()), 1),
        "detention_warning_count": len(detention_list),
        "detention_percentage": round(len(detention_list) / max(1, len(MASTER_STUDENTS_DF)) * 100, 1),
        "detention_watchlist": det_records
    }


@app.get("/api/placement-analytics")
def get_placement_analytics():
    status_counts = MASTER_STUDENTS_DF['placement_status'].value_counts().to_dict()
    return {
        "avg_readiness": round(float(MASTER_STUDENTS_DF['placement_readiness_score'].mean()), 1),
        "avg_coding": round(float(MASTER_STUDENTS_DF['coding_score'].mean()), 1),
        "avg_aptitude": round(float(MASTER_STUDENTS_DF['aptitude_score'].mean()), 1),
        "avg_mock_interview": round(float(MASTER_STUDENTS_DF['mock_interview_score'].mean()), 1),
        "status_breakdown": status_counts,
        "placement_ready_count": int((MASTER_STUDENTS_DF['placement_readiness_score'] >= 70).sum()),
        "technical_gap_count": int((MASTER_STUDENTS_DF['coding_score'] < 50).sum())
    }


@app.get("/api/staff")
def get_staff_directory():
    return MASTER_STAFF_DF.to_dict(orient="records")


@app.get("/api/settings")
def get_settings():
    return {
        "custom_weights": CUSTOM_WEIGHTS,
        "default_weights": DEFAULT_WEIGHTS
    }


@app.post("/api/settings/weights")
def update_weights(req: WeightsUpdateRequest, request: Request):
    session = get_current_session(request)
    if session and session.get("role") != "HOD / Admin":
        raise HTTPException(
            status_code=403,
            detail="Access denied: Only Institutional Administrator / HOD can modify scoring weights."
        )

    global CUSTOM_WEIGHTS, MASTER_STUDENTS_DF
    CUSTOM_WEIGHTS = {
        'academics': req.academics,
        'attendance': req.attendance,
        'lms_engagement': req.lms_engagement,
        'placement_readiness': req.placement_readiness,
        'skills_feedback': req.skills_feedback
    }
    MASTER_STUDENTS_DF = batch_compute_success_scores(MASTER_STUDENTS_DF, CUSTOM_WEIGHTS)
    return {"success": True, "weights": CUSTOM_WEIGHTS}


@app.get("/api/reports/department-pdf")
def get_department_pdf(request: Request):
    session = get_current_session(request)
    if session and session.get("role") == "Student Portal":
        raise HTTPException(
            status_code=403,
            detail="Access denied: Students are not permitted to access departmental executive audits."
        )

    pdf_bytes = generate_department_pdf(MASTER_STUDENTS_DF)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=DEXA_Department_Brief.pdf"}
    )


@app.get("/api/reports/student-pdf/{student_id}")
def get_student_pdf(student_id: str, request: Request):
    session = get_current_session(request)
    if session and not can_access_student_record(session, student_id):
        raise HTTPException(
            status_code=403,
            detail=f"Access denied: You are not authorized to view student dossier '{student_id}'."
        )

    matches = MASTER_STUDENTS_DF[MASTER_STUDENTS_DF['student_id'].str.upper() == student_id.strip().upper()]
    if matches.empty:
        raise HTTPException(status_code=404, detail="Student not found")
    student = matches.iloc[0]
    rc, mt = analyze_root_causes(student)
    pdf_bytes = generate_student_pdf(student, rc, mt)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=DEXA_Dossier_{student['student_id']}.pdf"}
    )


@app.get("/api/reports/export-csv")
def export_csv():
    csv_str = MASTER_STUDENTS_DF.to_csv(index=False)
    return Response(
        content=csv_str,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=DEXA_Cohort_Dataset.csv"}
    )


@app.get("/api/chat/status")
def chat_status():
    return get_ai_service_status()


@app.post("/api/chat/query")
def chat_query(req: ChatRequest):
    res = process_chatbot_query(
        query=req.message,
        df=MASTER_STUDENTS_DF,
        mode=req.mode,
        history=req.history or [],
        df_staff=MASTER_STAFF_DF,
        user_role=req.role or "HOD / Admin",
        user_id=req.user_id or "admin"
    )
    return res


@app.get("/api/chat/telemetry")
def chat_telemetry():
    return analyze_campus_vibe_telemetry(MASTER_STUDENTS_DF)



@app.get("/api/grievances")
def get_grievances():
    return GRIEVANCES_STORE


@app.post("/api/grievances")
def post_grievance(req: GrievanceCreateRequest):
    tok = f"GFB-{abs(hash(req.comment)) % 9000 + 1000}-2026"
    record = {
        "id": tok,
        "category": req.category,
        "urgency": req.urgency,
        "comment": req.comment,
        "status": "Under Review",
        "created_at": datetime.now().strftime("%b %d, %H:%M")
    }
    GRIEVANCES_STORE.insert(0, record)
    return {"success": True, "token": tok, "grievance": record}


# -------------------------------------------------------------------------
# STATIC ASSET & SPA SERVING (MOUNT FRONTEND DIST IF PRESENT)
# -------------------------------------------------------------------------
FRONTEND_DIST = os.path.join(os.path.dirname(__file__), "frontend", "dist")

if os.path.exists(FRONTEND_DIST):
    app.mount("/assets", StaticFiles(directory=os.path.join(FRONTEND_DIST, "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        # Don't intercept API routes
        if full_path.startswith("api/"):
            raise HTTPException(status_code=404, detail="API route not found")
        file_path = os.path.join(FRONTEND_DIST, full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(FRONTEND_DIST, "index.html"))


if __name__ == "__main__":
    import uvicorn
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "8501"))
    print(f"[INFO] Starting DEXA 2.0 FastAPI Server on http://{host}:{port}...")
    uvicorn.run(app, host=host, port=port)
