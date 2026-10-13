"""
DEXA Data Engine - Unified Pipeline, Data Validation, Import & RBAC Authentication
"""

import os
import base64
import urllib.parse
import pandas as pd
import numpy as np

from scoring_engine import calculate_student_success_score, batch_compute_success_scores
from segmentation_engine import apply_student_segmentation

REQUIRED_STUDENT_COLUMNS = [
    'student_id', 'roll_number', 'name', 'department', 'year', 'section',
    'faculty_mentor', 'cgpa', 'attendance_overall_pct'
]

def get_image_base64_or_fallback(filepath: str, fallback_seed: str, style: str = "avataaars") -> str:
    """Return local image as base64 data URI if file exists, else return DiceBear URL."""
    if filepath and os.path.exists(filepath):
        try:
            with open(filepath, 'rb') as f:
                encoded = base64.b64encode(f.read()).decode('utf-8')
                ext = 'jpeg' if filepath.lower().endswith(('.jpg', '.jpeg')) else 'png'
                return f"data:image/{ext};base64,{encoded}"
        except Exception:
            pass

    clean_seed = urllib.parse.quote(str(fallback_seed).strip().replace(" ", "-"))
    return f"https://api.dicebear.com/7.x/{style}/svg?seed={clean_seed}&backgroundColor=e2e8f0,cbd5e1,bfdbfe"

def calculate_xp_and_level(row):
    """Compute gamified XP points and progression levels for students."""
    cgpa = float(row.get('cgpa', 6.0))
    coding = float(row.get('coding_score', 50.0))
    aptitude = float(row.get('aptitude_score', 50.0))
    assignments = float(row.get('assignment_completion_pct', 70.0))
    hackathons = int(row.get('hackathons_participated', 0))
    certifications = int(row.get('certifications_completed', 0))
    backlogs = int(row.get('backlogs', 0))
    attendance = float(row.get('attendance_overall_pct', 75.0))

    base_xp = (cgpa * 110) + (coding * 3.5) + (aptitude * 2.5) + (assignments * 2.0)
    achievement_xp = (hackathons * 120) + (certifications * 90)
    attendance_xp = 150 if attendance >= 90 else (75 if attendance >= 80 else 0)
    backlog_penalty = backlogs * 120
    clean_bonus = 200 if backlogs == 0 else 0

    total_xp = max(250, int(base_xp + achievement_xp + attendance_xp + clean_bonus - backlog_penalty))

    levels = [
        (500, "Level 1: Novice Cadet"),
        (900, "Level 2: Academic Explorer"),
        (1300, "Level 3: Skill Builder"),
        (1700, "Level 4: Tech Practitioner"),
        (2100, "Level 5: Code Pioneer"),
        (2500, "Level 6: Campus Vanguard"),
        (2900, "Level 7: Research Specialist"),
        (3300, "Level 8: Lead Innovator"),
        (3700, "Level 9: Elite Scholar"),
        (99999, "Level 10: Grandmaster Prodigy")
    ]

    level_num = 1
    level_title = levels[0][1]
    prev_threshold = 0
    next_threshold = 500

    for i, (threshold, title) in enumerate(levels):
        if total_xp <= threshold:
            level_num = i + 1
            level_title = title
            prev_threshold = levels[i-1][0] if i > 0 else 0
            next_threshold = threshold
            break

    progress_pct = min(100.0, max(0.0, (total_xp - prev_threshold) / max(1, (next_threshold - prev_threshold)) * 100.0))

    badges = [
        {"id": "code_wizard", "title": "Code Wizard", "icon": "💻", "desc": "Coding >= 75", "unlocked": coding >= 75},
        {"id": "aptitude_ace", "title": "Aptitude Ace", "icon": "🎯", "desc": "Aptitude >= 70", "unlocked": aptitude >= 70},
        {"id": "hack_hero", "title": "Hackathon Hero", "icon": "⚡", "desc": "1+ Hackathon", "unlocked": hackathons >= 1},
        {"id": "certified_pro", "title": "Certified Pro", "icon": "📜", "desc": "2+ Certs", "unlocked": certifications >= 2},
        {"id": "century_att", "title": "Century Club", "icon": "🌟", "desc": "Attendance >= 90%", "unlocked": attendance >= 90},
        {"id": "deans_honor", "title": "Dean's Honor", "icon": "🎓", "desc": "CGPA >= 8.5", "unlocked": cgpa >= 8.5},
        {"id": "zero_arrears", "title": "Zero Arrears", "icon": "🛡️", "desc": "0 Backlogs", "unlocked": backlogs == 0}
    ]

    return total_xp, level_num, level_title, progress_pct, badges, next_threshold

def load_student_dataset(csv_path: str = "student_dataset_500-1 (1).csv") -> pd.DataFrame:
    """Load master student dataset, resolve avatars, compute scores & segmentations."""
    if not os.path.exists(csv_path):
        if os.path.exists("student_dataset.csv"):
            csv_path = "student_dataset.csv"
        else:
            raise FileNotFoundError(f"Cannot find student dataset at {csv_path}")

    df = pd.read_csv(csv_path)

    # Clean string fields
    df['name'] = df['name'].fillna('Student')
    df['student_id'] = df['student_id'].astype(str)
    df['department'] = df['department'].fillna('CSE')
    df['faculty_mentor'] = df['faculty_mentor'].fillna('Unassigned')
    df['risk_level'] = df['risk_level'].fillna('Low')

    # Apply deterministic student segmentation
    df = apply_student_segmentation(df)

    # Apply student success scores
    df = batch_compute_success_scores(df)

    avatar_urls = []
    xp_list = []
    level_list = []
    title_list = []
    progress_list = []
    badges_list = []
    next_xp_list = []

    for _, row in df.iterrows():
        stu_id = str(row['student_id']).strip()
        photo_path = f"student_photos/{stu_id}.jpg"
        photo_src = get_image_base64_or_fallback(photo_path, row['name'], style="avataaars")
        avatar_urls.append(photo_src)

        xp, lvl, title, prog, badges, next_xp = calculate_xp_and_level(row)
        xp_list.append(xp)
        level_list.append(lvl)
        title_list.append(title)
        progress_list.append(prog)
        badges_list.append(badges)
        next_xp_list.append(next_xp)

    df['photo_url'] = avatar_urls
    df['xp_points'] = xp_list
    df['student_level'] = level_list
    df['level_title'] = title_list
    df['level_progress_pct'] = progress_list
    df['badges'] = badges_list
    df['next_level_xp'] = next_xp_list

    return df

def load_staff_dataset(csv_path: str = "staff_dataset.csv") -> pd.DataFrame:
    """Load staff dataset, resolve photos into robust data URIs."""
    if not os.path.exists(csv_path):
        return pd.DataFrame()

    df = pd.read_csv(csv_path)
    df['name'] = df['name'].fillna('Faculty Member')
    df['staff_id'] = df['staff_id'].astype(str)

    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].fillna("")
        else:
            df[col] = df[col].fillna(0)

    photo_srcs = []
    for _, row in df.iterrows():
        stf_id = str(row['staff_id']).strip()
        photo_path = f"staff_photos/{stf_id}.jpg"
        photo_src = get_image_base64_or_fallback(photo_path, row['name'], style="lorelei" if str(row.get('gender')).lower() == 'female' else 'avataaars')
        photo_srcs.append(photo_src)

    df['photo_url'] = photo_srcs
    return df


def validate_and_import_student_data(file_obj, filename: str) -> dict:
    """
    Validate uploaded CSV or Excel file against required student schema.
    Returns:
        dict: {
            'success': bool,
            'message': str,
            'imported_df': pd.DataFrame or None,
            'stats': dict,
            'errors': list
        }
    """
    errors = []
    try:
        if filename.lower().endswith('.csv'):
            df_new = pd.read_csv(file_obj)
        elif filename.lower().endswith(('.xls', '.xlsx')):
            df_new = pd.read_excel(file_obj)
        else:
            return {'success': False, 'message': 'Unsupported file type. Please upload a CSV or Excel (.xlsx) file.', 'errors': ['Invalid extension']}

        # Check required columns
        missing_cols = [c for c in REQUIRED_STUDENT_COLUMNS if c not in df_new.columns]
        if missing_cols:
            return {
                'success': False,
                'message': f"Validation Failed: Missing required columns: {', '.join(missing_cols)}",
                'errors': [f"Missing column: {c}" for c in missing_cols]
            }

        initial_rows = len(df_new)
        # Drop duplicates by student_id
        df_new = df_new.drop_duplicates(subset=['student_id'], keep='last')
        dedup_count = initial_rows - len(df_new)

        # Standardize and clean
        df_new['student_id'] = df_new['student_id'].astype(str).str.strip().str.upper()
        df_new['name'] = df_new['name'].fillna('Student')
        df_new['cgpa'] = pd.to_numeric(df_new['cgpa'], errors='coerce').fillna(6.0)
        df_new['attendance_overall_pct'] = pd.to_numeric(df_new['attendance_overall_pct'], errors='coerce').fillna(75.0)

        # Apply segmentation and scoring
        df_new = apply_student_segmentation(df_new)
        df_new = batch_compute_success_scores(df_new)

        # Generate avatars
        avatars = []
        for _, row in df_new.iterrows():
            stu_id = str(row['student_id'])
            photo_path = f"student_photos/{stu_id}.jpg"
            avatars.append(get_image_base64_or_fallback(photo_path, row['name']))
        df_new['photo_url'] = avatars

        # Data quality telemetry
        null_counts = df_new[REQUIRED_STUDENT_COLUMNS].isnull().sum().to_dict()
        overall_completeness = round((1.0 - (sum(null_counts.values()) / (len(df_new) * len(REQUIRED_STUDENT_COLUMNS)))) * 100.0, 1)

        stats = {
            'total_rows': len(df_new),
            'duplicates_removed': dedup_count,
            'data_completeness_pct': overall_completeness,
            'columns_present': len(df_new.columns),
            'year_breakdown': df_new['year'].value_counts().to_dict() if 'year' in df_new.columns else {}
        }

        return {
            'success': True,
            'message': f"Successfully imported and validated {len(df_new)} student records (Data Quality: {overall_completeness}%).",
            'imported_df': df_new,
            'stats': stats,
            'errors': []
        }

    except Exception as e:
        return {'success': False, 'message': f"File processing exception: {str(e)}", 'errors': [str(e)]}

def sanitize_dict(d: dict) -> dict:
    if not isinstance(d, dict):
        return {}
    cleaned = {}
    for k, v in d.items():
        if v is None:
            cleaned[k] = ""
        elif isinstance(v, (list, tuple)):
            cleaned[k] = [sanitize_dict(x) if isinstance(x, dict) else x for x in v]
        elif isinstance(v, np.ndarray):
            cleaned[k] = [sanitize_dict(x) if isinstance(x, dict) else x for x in v.tolist()]
        elif isinstance(v, dict):
            cleaned[k] = sanitize_dict(v)
        elif isinstance(v, (bool, np.bool_)):
            cleaned[k] = bool(v)
        elif isinstance(v, (np.floating, float)):
            cleaned[k] = 0.0 if (np.isnan(v) or np.isinf(v)) else round(float(v), 4)
        elif isinstance(v, (np.integer, int)):
            cleaned[k] = int(v)
        elif pd.isna(v):
            cleaned[k] = ""
        else:
            cleaned[k] = v
    return cleaned



def authenticate_user(username: str, password: str, df_students: pd.DataFrame, df_staff: pd.DataFrame):
    """Authenticate user with scrypt password verification and role resolution."""
    from auth_engine import get_account_by_id, verify_password

    u = (username or "").strip()
    p = (password or "").strip()
    if not u or not p:
        return {'authenticated': False, 'error': 'Please enter both User ID and Password.'}

    # 1. Lookup in secure auth store
    acc = get_account_by_id(u)
    if not acc:
        return {'authenticated': False, 'error': 'Invalid User ID or Password.'}

    # 2. Check active status
    if not acc.get('is_active', True):
        return {
            'authenticated': False,
            'error': 'This account has been deactivated. Please contact your department administrator.'
        }

    # 3. Verify password hash
    stored_hash = acc.get('password_hash', '')
    if not verify_password(stored_hash, p):
        return {'authenticated': False, 'error': 'Invalid User ID or Password.'}

    # 4. Resolve enriched profile record from dataset
    linked_id = str(acc.get('linked_id', '')).strip().upper()
    role = acc.get('role', 'Student Portal')
    rec = {}

    if role in ['HOD / Admin', 'Staff / Mentor', 'Class Advisor'] and not df_staff.empty:
        m = df_staff[df_staff['staff_id'].str.upper() == linked_id]
        if not m.empty:
            rec = sanitize_dict(m.iloc[0].to_dict())

    if role == 'Student Portal' and not df_students.empty:
        s = df_students[df_students['student_id'].str.upper() == linked_id]
        if not s.empty:
            rec = sanitize_dict(s.iloc[0].to_dict())

    if not rec:
        rec = {
            'user_id': acc.get('display_user_id', u),
            'name': acc.get('name', ''),
            'email': acc.get('email', ''),
            'role': role
        }

    return {
        'authenticated': True,
        'role': role,
        'user_id': acc.get('display_user_id', u),
        'linked_id': linked_id,
        'name': acc.get('name', ''),
        'email': acc.get('email', ''),
        'profile_record': rec,
        'error': None
    }

