"""
DEXA — Dynamic Student Success Intelligence Platform
Enterprise University Academic Portal Layout (Clean Light Theme, No Sidebars, Top Horizontal ERP Nav)
"""

import os
import io
import urllib.parse
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Load environment variables from .env if present
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Local modules
from styles import CUSTOM_CSS
from data_engine import (
    load_student_dataset,
    load_staff_dataset,
    authenticate_user,
    get_image_base64_or_fallback,
    validate_and_import_student_data,
    REQUIRED_STUDENT_COLUMNS
)
from scoring_engine import (
    calculate_student_success_score,
    batch_compute_success_scores,
    DEFAULT_WEIGHTS
)
from segmentation_engine import (
    apply_student_segmentation,
    generate_prioritized_intervention_queue,
    SEGMENT_DEFINITIONS,
    classify_student_segment
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
from copilot_engine import parse_voice_command, COPILOT_PRESETS
from chatbot_engine import (
    process_chatbot_query,
    analyze_campus_vibe_telemetry,
    SUGGESTED_VIBE_PROMPTS,
    SUGGESTED_STUDY_PROMPTS
)
from notifications_engine import (
    init_mock_notifications,
    init_mock_grievances,
    init_mock_interventions
)

# ---------------------------------------------------------
# PAGE CONFIGURATION (WIDE LAYOUT, COLLAPSED SIDEBAR)
# ---------------------------------------------------------
st.set_page_config(
    page_title="DEXA Academic Portal — Dynamic Student Success Intelligence",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Apply Light Institutional Theme CSS (Completely hides sidebar and dots)
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ---------------------------------------------------------
# HELPER: ENTERPRISE HIGH-CONTRAST PLOTLY THEME
# ---------------------------------------------------------
def apply_enterprise_chart_theme(fig, title=""):
    """Enforce legible slate fonts, subtle gridlines, and clean white card background."""
    fig.update_layout(
        title=dict(
            text=title,
            font=dict(color="#0F172A", size=13, family="Plus Jakarta Sans, sans-serif")
        ),
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        font=dict(color="#0F172A", family="Plus Jakarta Sans, sans-serif"),
        margin=dict(l=24, r=24, t=44, b=24),
        xaxis=dict(
            title_font=dict(color="#334155", size=11, family="Plus Jakarta Sans, sans-serif"),
            tickfont=dict(color="#334155", size=10, family="Plus Jakarta Sans, sans-serif"),
            gridcolor="#F1F5F9",
            linecolor="#CBD5E1"
        ),
        yaxis=dict(
            title_font=dict(color="#334155", size=11, family="Plus Jakarta Sans, sans-serif"),
            tickfont=dict(color="#334155", size=10, family="Plus Jakarta Sans, sans-serif"),
            gridcolor="#F1F5F9",
            linecolor="#CBD5E1"
        ),
        legend=dict(
            font=dict(color="#334155", size=10, family="Plus Jakarta Sans, sans-serif"),
            bgcolor="rgba(255,255,255,0.9)",
            bordercolor="#E2E8F0"
        )
    )
    return fig


# ---------------------------------------------------------
# SESSION STATE INITIALIZATION
# ---------------------------------------------------------
if 'dataset' not in st.session_state:
    st.session_state.dataset = load_student_dataset()

if 'staff_dataset' not in st.session_state:
    st.session_state.staff_dataset = load_staff_dataset()

if 'custom_weights' not in st.session_state:
    st.session_state.custom_weights = DEFAULT_WEIGHTS.copy()

if 'rf_model' not in st.session_state:
    model, metrics, importances = train_rf_model(st.session_state.dataset)
    st.session_state.rf_model = model
    st.session_state.model_metrics = metrics
    st.session_state.model_importances = importances

if 'notifications' not in st.session_state:
    st.session_state.notifications = init_mock_notifications(st.session_state.dataset)

if 'grievances' not in st.session_state:
    st.session_state.grievances = init_mock_grievances()

if 'interventions' not in st.session_state:
    st.session_state.interventions = init_mock_interventions(st.session_state.dataset)

if 'chat_messages' not in st.session_state:
    st.session_state.chat_messages = [
        {
            "role": "assistant",
            "content": "👋 **Hello! I am Zoro (DEXA Copilot)**. Ask me about campus sentiment telemetry or toggle Study Copilot for DSA & technical guidance!"
        }
    ]

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if 'user_role' not in st.session_state:
    st.session_state.user_role = "HOD / Admin"

if 'user_name' not in st.session_state:
    st.session_state.user_name = "Dr. N. Balasubramanian"

if 'user_id' not in st.session_state:
    st.session_state.user_id = "STF005"

if 'user_photo' not in st.session_state:
    st.session_state.user_photo = get_image_base64_or_fallback("staff_photos/STF005.jpg", "Dr. N. Balasubramanian")

if 'active_tab' not in st.session_state:
    st.session_state.active_tab = "📊 Overview"

if 'voice_modal_open' not in st.session_state:
    st.session_state.voice_modal_open = False

if 'zoro_open' not in st.session_state:
    st.session_state.zoro_open = False

if 'zoro_mode' not in st.session_state:
    st.session_state.zoro_mode = "vibe"

df = st.session_state.dataset
df_staff = st.session_state.staff_dataset
model = st.session_state.rf_model
metrics = st.session_state.model_metrics


# ---------------------------------------------------------
# PHASE 1 & 2: REFINED INSTITUTIONAL SIGN IN GATEWAY
# ---------------------------------------------------------
if not st.session_state.authenticated:
    st.markdown("""
    <div style="text-align: center; margin-top: 1.25rem; margin-bottom: 1.25rem;">
        <div style="display: inline-flex; align-items: center; justify-content: center; width: 62px; height: 62px; border-radius: 14px; background: #1E40AF; color: white; font-size: 2rem; margin-bottom: 0.6rem; box-shadow: 0 4px 12px rgba(30, 64, 175, 0.25);">
            🎓
        </div>
        <h1 style="margin: 0; font-size: 1.95rem; color: #0F172A; font-weight: 800; letter-spacing: -0.02em;">DEXA Academic Portal</h1>
        <div style="font-size: 0.9rem; color: #475569; margin-top: 0.25rem; font-weight: 500;">
            Department of Computer Science & Engineering • Dynamic Student Success Intelligence
        </div>
    </div>
    """, unsafe_allow_html=True)

    login_col1, login_col2, login_col3 = st.columns([1.1, 1.6, 1.1])
    with login_col2:
        st.markdown("""
        <div class="login-card-container">
            <h3 style="margin-top: 0; color: #0F172A; font-weight: 700; font-size: 1.25rem;">Institutional Sign In</h3>
            <p style="color: #64748B; font-size: 0.84rem; margin-bottom: 1rem; line-height: 1.4;">
                Enter your college credentials. The system automatically verifies your role against the master faculty and student directories.
            </p>
        """, unsafe_allow_html=True)

        with st.form("portal_login_form"):
            login_user = st.text_input("User ID / Roll Number / Staff ID", placeholder="e.g. admin, STF002, STU0031, 24CS013...", help="HOD: admin | Staff: STF001-STF015 | Student: STU0001-STU0500")
            login_pass = st.text_input("Password", type="password", placeholder="Enter your portal password...")
            submit_login = st.form_submit_button("🔐 Sign In to Academic Portal", type="primary", use_container_width=True)

            if submit_login:
                auth_result = authenticate_user(login_user, login_pass, df, df_staff)
                if auth_result['authenticated']:
                    st.session_state.authenticated = True
                    st.session_state.user_role = auth_result['role']
                    st.session_state.user_name = auth_result['name']
                    st.session_state.user_id = auth_result['user_id']
                    rec = auth_result['profile_record']
                    st.session_state.user_photo = rec.get('photo_url', get_image_base64_or_fallback(f"student_photos/{auth_result['user_id']}.jpg", auth_result['name']))
                    st.session_state.active_tab = "🌟 My Growth Portal" if auth_result['role'] == "Student Portal" else "📊 Overview"
                    st.rerun()
                else:
                    st.error(auth_result['error'])

        st.markdown("<hr style='margin: 1.15rem 0 0.85rem 0; border-color: #E2E8F0;'/>", unsafe_allow_html=True)
        st.markdown("<div style='font-size: 0.8rem; font-weight: 700; color: #475569; margin-bottom: 0.5rem;'>⚡ Quick Demo Access (Pre-authenticated Sandbox):</div>", unsafe_allow_html=True)
        
        demo_c1, demo_c2 = st.columns(2)
        with demo_c1:
            if st.button("👑 HOD (Dr. Balasubramanian)", use_container_width=True, help="Institutional Admin Role with complete departmental oversight"):
                auth_res = authenticate_user("admin", "admin123", df, df_staff)
                st.session_state.authenticated = True
                st.session_state.user_role = auth_res['role']
                st.session_state.user_name = auth_res['name']
                st.session_state.user_id = auth_res['user_id']
                st.session_state.user_photo = auth_res['profile_record'].get('photo_url', '')
                st.session_state.active_tab = "📊 Overview"
                st.rerun()

            if st.button("🎓 Student (Sowmiya V)", use_container_width=True, help="High-achieving student personal growth portal"):
                auth_res = authenticate_user("STU0031", "123", df, df_staff)
                st.session_state.authenticated = True
                st.session_state.user_role = auth_res['role']
                st.session_state.user_name = auth_res['name']
                st.session_state.user_id = auth_res['user_id']
                st.session_state.user_photo = auth_res['profile_record'].get('photo_url', '')
                st.session_state.active_tab = "🌟 My Growth Portal"
                st.rerun()

        with demo_c2:
            if st.button("👨‍🏫 Mentor (Dr. T. Ramesh)", use_container_width=True, help="Faculty mentor role scoped to assigned mentees"):
                auth_res = authenticate_user("STF002", "123", df, df_staff)
                st.session_state.authenticated = True
                st.session_state.user_role = auth_res['role']
                st.session_state.user_name = auth_res['name']
                st.session_state.user_id = auth_res['user_id']
                st.session_state.user_photo = auth_res['profile_record'].get('photo_url', '')
                st.session_state.active_tab = "📊 Overview"
                st.rerun()

            if st.button("⚠️ At-Risk (Mohan N)", use_container_width=True, help="Student requiring academic recovery interventions"):
                auth_res = authenticate_user("STU0005", "123", df, df_staff)
                st.session_state.authenticated = True
                st.session_state.user_role = auth_res['role']
                st.session_state.user_name = auth_res['name']
                st.session_state.user_id = auth_res['user_id']
                st.session_state.user_photo = auth_res['profile_record'].get('photo_url', '')
                st.session_state.active_tab = "🌟 My Growth Portal"
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()


# ---------------------------------------------------------
# PHASE 2: ENTERPRISE ERP APP SHELL & TOP BAR
# ---------------------------------------------------------
h_col1, h_col2, h_col3 = st.columns([3.5, 4, 2.5])

with h_col1:
    st.markdown("""
    <div class="erp-brand-title">
        <span style="background: #1E40AF; color: white; width: 34px; height: 34px; border-radius: 8px; display: inline-flex; align-items: center; justify-content: center; font-size: 1.15rem; box-shadow: 0 2px 6px rgba(30, 64, 175, 0.25);">🎓</span>
        <div>
            <div style="font-size: 1.25rem; font-weight: 800; color: #1E3A8A; line-height: 1.1;">DEXA ACADEMIC PORTAL</div>
            <div class="erp-brand-subtitle">Dept of Computer Science & Engineering</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with h_col2:
    role_pill_style = "pill-brand" if st.session_state.user_role == "HOD / Admin" else ("pill-medium" if st.session_state.user_role == "Staff / Mentor" else "pill-low")
    st.markdown(f"""
    <div style="display: flex; align-items: center; gap: 0.75rem; justify-content: center; padding-top: 0.15rem;">
        <img src="{st.session_state.user_photo}" style="width: 42px; height: 42px; border-radius: 50%; object-fit: cover; border: 2px solid #BFDBFE;"/>
        <div>
            <div style="font-size: 0.92rem; font-weight: 700; color: #0F172A;">{st.session_state.user_name}</div>
            <div style="font-size: 0.74rem; color: #64748B;">Role: <span class="pill {role_pill_style}">{st.session_state.user_role}</span> ({st.session_state.user_id})</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with h_col3:
    act_c1, act_c2 = st.columns([1.2, 1.2])
    with act_c1:
        if st.button("🎙️ Voice Copilot", key="header_copilot_trigger", use_container_width=True):
            st.session_state.voice_modal_open = not st.session_state.voice_modal_open

    with act_c2:
        if st.button("🔄 Switch Account", key="header_logout_trigger", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.user_role = "HOD / Admin"
            st.session_state.user_name = ""
            st.session_state.user_id = ""
            st.session_state.chat_messages = []
            st.rerun()


# ---------------------------------------------------------
# MULTILINGUAL VOICE COPILOT MODAL (ENGLISH, TAMIL, TANGLISH)
# ---------------------------------------------------------
if st.session_state.voice_modal_open:
    st.markdown("""
    <div class="dexa-card" style="border: 2px solid #1E40AF; background: #FFFFFF; padding: 1.15rem 1.35rem; margin-bottom: 1rem;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <span style="font-size: 1.35rem;">🎙️</span>
                <h3 style="margin: 0; color: #1E3A8A; font-size: 1.1rem;">Multilingual Voice Copilot</h3>
            </div>
            <span class="pill pill-brand">English • தமிழ் (Tamil) • Tanglish</span>
        </div>
        <p style="font-size: 0.8rem; color: #64748B; margin-bottom: 0.75rem;">
            Speak or choose presets to navigate tabs, filter high-risk cohorts, or search specific students.
        </p>
    """, unsafe_allow_html=True)

    vc_c1, vc_c2 = st.columns([1.4, 1])
    with vc_c1:
        st.markdown("<div style='font-size:0.8rem; font-weight:700; color:#334155; margin-bottom:0.25rem;'>⚡ Quick Command Presets:</div>", unsafe_allow_html=True)
        v_p_row = st.columns(3)
        with v_p_row[0]:
            if st.button("⚠️ Show at-risk students", key="v_p1", use_container_width=True):
                st.session_state['v_cmd_val'] = "show at-risk students"
        with v_p_row[1]:
            if st.button("⚠️ ஆபத்தில் உள்ள மாணவர்கள்", key="v_p2", use_container_width=True):
                st.session_state['v_cmd_val'] = "ஆபத்தில் உள்ள மாணவர்களைக் காட்டு"
        with v_p_row[2]:
            if st.button("🔍 Search STU0005 (Tanglish)", key="v_p3", use_container_width=True):
                st.session_state['v_cmd_val'] = "search STU0005"

        v_text = st.text_input("Spoken Speech or Text Command:", value=st.session_state.get('v_cmd_val', "show at-risk students"), key="v_input_box")
        run_v_btn = st.button("⚡ Execute Voice Command", type="primary", use_container_width=True)

    with vc_c2:
        parsed_v = parse_voice_command(v_text)
        st.markdown(f"""
        <div style="background: #F8FAFC; border: 1px solid #CBD5E1; border-radius: 8px; padding: 0.75rem; font-size: 0.82rem;">
            <div style="display:flex; justify-content:space-between; margin-bottom: 0.25rem;">
                <span class="pill pill-brand">Intent: {parsed_v['intent']}</span>
                <span class="pill pill-low">{parsed_v['lang']}</span>
            </div>
            <div style="font-weight: 700; color: #0F172A; font-size: 0.88rem; margin: 0.25rem 0;">{parsed_v['response_text']}</div>
            <div style="color: #64748B; font-size: 0.74rem;">Target: <b>{parsed_v['target_page']}</b></div>
        </div>
        """, unsafe_allow_html=True)

        sp_esc = parsed_v['speech_text'].replace('"', '\\"').replace("'", "\\'")
        sp_lang = "ta-IN" if parsed_v['lang'] == "Tamil" else "en-US"
        st.markdown(f"""
        <div style="margin-top: 0.5rem;">
            <button onclick="window.speechSynthesis.cancel(); const u = new SpeechSynthesisUtterance('{sp_esc}'); u.lang = '{sp_lang}'; window.speechSynthesis.speak(u);" 
                    style="width: 100%; background: #059669; color: white; border: none; padding: 7px 12px; border-radius: 6px; font-weight: 600; cursor: pointer; font-size: 0.82rem;">
                🔊 Listen Speech Response ({parsed_v['lang']})
            </button>
        </div>
        """, unsafe_allow_html=True)

        if run_v_btn:
            if parsed_v['intent'] == "show_at_risk":
                st.session_state.active_tab = "⚠️ Risk & Interventions"
            elif parsed_v['intent'] == "search_student":
                st.session_state.active_tab = "👥 Students"
            elif parsed_v['intent'] == "micro_audit":
                st.session_state.active_tab = "📄 Reports & Briefs"
            st.session_state.voice_modal_open = False
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------------------------------------
# PHASE 3: ROLE-BASED HORIZONTAL ERP NAVIGATION BAR
# ---------------------------------------------------------
if st.session_state.user_role == "Student Portal":
    erp_tabs = [
        "🌟 My Growth Portal",
        "📊 Academics & Attendance",
        "🕸️ 360° Competency Radar",
        "🔬 Diagnostic & Simulation",
        "🗳️ Anonymous Grievance Box",
        "🏆 Public Hall of Fame"
    ]
elif st.session_state.user_role == "Staff / Mentor":
    erp_tabs = [
        "📊 Overview",
        "👥 Students",
        "⚠️ Risk & Interventions",
        "🎓 Academic Performance",
        "📅 Attendance",
        "💻 LMS & Engagement",
        "💼 Placement Readiness",
        "🧩 Student Segments",
        "📄 Reports & Briefs",
        "🔔 Mentee Notifications",
        "💬 Communication & Grievances"
    ]
else:  # HOD / Admin
    erp_tabs = [
        "📊 Overview",
        "👥 Students",
        "⚠️ Risk & Interventions",
        "🎓 Academic Performance",
        "📅 Attendance",
        "💻 LMS & Engagement",
        "💼 Placement Readiness",
        "🧩 Student Segments",
        "📄 Reports & Briefs",
        "⚙️ Settings & Data Integration",
        "👥 Faculty Directory",
        "💬 Communication & Grievances"
    ]

curr_tab_idx = erp_tabs.index(st.session_state.active_tab) if st.session_state.active_tab in erp_tabs else 0
selected_nav_tab = st.radio(
    "Enterprise Navigation Tabs",
    erp_tabs,
    index=curr_tab_idx,
    horizontal=True,
    label_visibility="collapsed"
)
st.session_state.active_tab = selected_nav_tab


# ---------------------------------------------------------
# GLOBAL INTERACTIVE FILTER BAR (FOR HOD & STAFF)
# ---------------------------------------------------------
filtered_df = df.copy()

if st.session_state.user_role != "Student Portal":
    with st.container():
        st.markdown('<div class="filter-bar-container">', unsafe_allow_html=True)
        gf1, gf2, gf3, gf4, gf5 = st.columns(5)
        
        with gf1:
            year_opts = ["All Years"] + sorted([str(y) for y in df['year'].dropna().unique()])
            sel_year = st.selectbox("Academic Year", year_opts, key="gf_year")
        with gf2:
            sem_opts = ["All Semesters"] + [f"Sem {s}" for s in range(1, 9)]
            sel_sem = st.selectbox("Semester", sem_opts, key="gf_sem")
        with gf3:
            sec_opts = ["All Sections"] + sorted([str(s) for s in df['section'].dropna().unique()])
            sel_sec = st.selectbox("Section", sec_opts, key="gf_sec")
        with gf4:
            risk_opts = ["All Risk Tiers", "High", "Medium", "Low"]
            sel_risk = st.selectbox("Risk Tier", risk_opts, key="gf_risk")
        with gf5:
            mentor_opts = ["All Mentors"] + sorted(list(df['faculty_mentor'].dropna().unique()))
            default_mentor_idx = 0
            if st.session_state.user_role == "Staff / Mentor" and st.session_state.user_name in mentor_opts:
                default_mentor_idx = mentor_opts.index(st.session_state.user_name)
            sel_mentor = st.selectbox("Faculty Mentor", mentor_opts, index=default_mentor_idx, key="gf_mentor")
        
        # Apply filters reactively
        if sel_year != "All Years":
            filtered_df = filtered_df[filtered_df['year'].astype(str) == sel_year]
        if sel_sec != "All Sections":
            filtered_df = filtered_df[filtered_df['section'].astype(str) == sel_sec]
        if sel_risk != "All Risk Tiers":
            filtered_df = filtered_df[filtered_df['risk_level'] == sel_risk]
        if sel_mentor != "All Mentors":
            filtered_df = filtered_df[filtered_df['faculty_mentor'] == sel_mentor]

        st.markdown(f"""
        <div style="display:flex; justify-content:space-between; align-items:center; margin-top:0.35rem; font-size:0.75rem; color:#64748B;">
            <span>Filtered Scope: <b style="color:#0F172A;">{len(filtered_df)}</b> of {len(df)} Students</span>
            <span class="pill pill-low">Data Completeness: {filtered_df['data_completeness_pct'].mean() if 'data_completeness_pct' in filtered_df else 100:.1f}%</span>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)


# =========================================================
# TAB 1: 📊 OVERVIEW (EXECUTIVE DASHBOARD & PREDICTION)
# =========================================================
if st.session_state.active_tab == "📊 Overview":
    if filtered_df.empty:
        st.warning("No student records match the active filters. Broaden your filter selection above.")
    else:
        # Macro KPI Cards
        k1, k2, k3, k4, k5 = st.columns(5)
        with k1:
            st.markdown(f"""<div class="kpi-container"><div class="kpi-label">👥 Total Students</div><div class="kpi-value">{len(filtered_df)}</div><div class="kpi-sub">Cohort Size</div></div>""", unsafe_allow_html=True)
        with k2:
            st.markdown(f"""<div class="kpi-container"><div class="kpi-label">🎓 Average CGPA</div><div class="kpi-value">{filtered_df['cgpa'].mean():.2f}</div><div class="kpi-sub">Scale of 10.00</div></div>""", unsafe_allow_html=True)
        with k3:
            st.markdown(f"""<div class="kpi-container"><div class="kpi-label">📅 Avg Attendance</div><div class="kpi-value">{filtered_df['attendance_overall_pct'].mean():.1f}%</div><div class="kpi-sub">Cutoff: 75.0%</div></div>""", unsafe_allow_html=True)
        with k4:
            hr_c = (filtered_df['risk_level'] == 'High').sum()
            st.markdown(f"""<div class="kpi-container" style="border-left: 3px solid #DC2626;"><div class="kpi-label">🚨 High Risk Flagged</div><div class="kpi-value" style="color: #DC2626;">{hr_c}</div><div class="kpi-sub">Require Attention</div></div>""", unsafe_allow_html=True)
        with k5:
            avg_score = filtered_df['student_success_score'].mean()
            st.markdown(f"""<div class="kpi-container"><div class="kpi-label">⭐ Avg Success Score</div><div class="kpi-value" style="color: #1E40AF;">{avg_score:.1f}</div><div class="kpi-sub">Index: 0–100</div></div>""", unsafe_allow_html=True)

        st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)

        ov_c1, ov_c2 = st.columns([3, 2])
        with ov_c1:
            fig_hist = px.histogram(
                filtered_df,
                x="student_success_score",
                color="risk_level",
                color_discrete_map={"Low": "#059669", "Medium": "#D97706", "High": "#DC2626"},
                nbins=30,
                marginal="box",
                labels={"student_success_score": "Success Score (0-100)", "risk_level": "Risk Tier"}
            )
            fig_hist = apply_enterprise_chart_theme(fig_hist, "Student Success Score Distribution Across Risk Tiers")
            st.plotly_chart(fig_hist, use_container_width=True)

        with ov_c2:
            rc_df = filtered_df['risk_level'].value_counts().reset_index()
            rc_df.columns = ['Risk Tier', 'Count']
            fig_p = px.pie(
                rc_df,
                values='Count',
                names='Risk Tier',
                color='Risk Tier',
                color_discrete_map={"Low": "#059669", "Medium": "#D97706", "High": "#DC2626"},
                hole=0.55
            )
            fig_p = apply_enterprise_chart_theme(fig_p, "Cohort Risk Composition")
            st.plotly_chart(fig_p, use_container_width=True)

        # Machine Learning Early-Warning Architecture
        st.markdown("### 🧠 Random Forest Early-Warning Architecture")
        rf_c1, rf_c2 = st.columns([2, 3])
        with rf_c1:
            st.markdown(f"""
            <div class="dexa-card">
                <h4 style="margin-top: 0; color: #1E40AF; font-size: 1rem;">Supervised Classifier Telemetry</h4>
                <p style="font-size: 0.78rem; color: #64748B; margin-bottom: 0.6rem;">
                    Evaluated on 20% stratified holdout partition (100 students). Trained with class-balanced Random Forest.
                </p>
                <table style="width: 100%; border-collapse: collapse; font-size: 0.84rem;">
                    <tr style="border-bottom: 1px solid #E2E8F0;"><td style="padding: 5px 0; color: #64748B;">Testing Accuracy:</td><td style="font-weight: 700; color: #059669;">{metrics['accuracy']*100:.2f}%</td></tr>
                    <tr style="border-bottom: 1px solid #E2E8F0;"><td style="padding: 5px 0; color: #64748B;">ROC-AUC Score:</td><td style="font-weight: 700; color: #1E40AF;">{metrics['roc_auc']:.4f}</td></tr>
                    <tr style="border-bottom: 1px solid #E2E8F0;"><td style="padding: 5px 0; color: #64748B;">Macro Precision:</td><td style="font-weight: 700; color: #0F172A;">{metrics['precision']*100:.2f}%</td></tr>
                    <tr style="border-bottom: 1px solid #E2E8F0;"><td style="padding: 5px 0; color: #64748B;">Recall (Sensitivity):</td><td style="font-weight: 700; color: #0F172A;">{metrics['recall']*100:.2f}%</td></tr>
                    <tr style="border-bottom: 1px solid #E2E8F0;"><td style="padding: 5px 0; color: #64748B;">Macro F1 Score:</td><td style="font-weight: 700; color: #0F172A;">{metrics['f1']*100:.2f}%</td></tr>
                    <tr><td style="padding: 5px 0; color: #64748B;">Split Partition:</td><td style="font-weight: 700; color: #0F172A;">{metrics['train_samples']} Train / {metrics['test_samples']} Test</td></tr>
                </table>
            </div>
            """, unsafe_allow_html=True)
        with rf_c2:
            fi_df = pd.DataFrame(list(st.session_state.model_importances.items()), columns=['Feature', 'Importance'])
            fi_df['Feature'] = fi_df['Feature'].map({
                'cgpa': 'Cumulative GPA (cgpa)',
                'attendance_overall_pct': 'Overall Attendance %',
                'assignment_completion_pct': 'Assignment Completion %',
                'aptitude_score': 'Aptitude Test Score',
                'coding_score': 'Coding Assessment Score',
                'communication_score': 'Communication Score'
            })
            fig_fi = px.bar(fi_df, x='Importance', y='Feature', orientation='h', color='Importance', color_continuous_scale='Blues')
            fig_fi = apply_enterprise_chart_theme(fig_fi, 'Feature Importance Weights (Gini Impurity)')
            fig_fi.update_layout(coloraxis_showscale=False)
            st.plotly_chart(fig_fi, use_container_width=True)


# =========================================================
# TAB 2: 👥 STUDENTS (REGISTRY & 360° PROFILE DOSSIER)
# =========================================================
elif st.session_state.active_tab == "👥 Students":
    st.markdown("## 👥 Student Registry & 360° Profile Dossiers")

    stu_search = st.text_input("🔍 Search Student Registry (ID, Roll No, Name, Mentor, Segment):", placeholder="e.g. STU0031, Sowmiya, Ramesh, High Achiever...")
    s_view_df = filtered_df.copy()
    if stu_search.strip():
        q = stu_search.strip().lower()
        s_view_df = s_view_df[
            s_view_df['student_id'].str.lower().str.contains(q) |
            s_view_df['name'].str.lower().str.contains(q) |
            s_view_df['roll_number'].str.lower().str.contains(q) |
            s_view_df['faculty_mentor'].str.lower().str.contains(q) |
            s_view_df['student_segment'].str.lower().str.contains(q) |
            s_view_df['risk_level'].str.lower().str.contains(q)
        ]

    st.markdown(f"**Showing {len(s_view_df)} students in current view:**")
    st.dataframe(
        s_view_df[['student_id', 'roll_number', 'name', 'year', 'section', 'cgpa', 'attendance_overall_pct', 'backlogs', 'student_success_score', 'risk_level', 'student_segment', 'faculty_mentor']],
        use_container_width=True,
        height=280
    )

    st.markdown("---")
    st.markdown("### 🔍 Inspect Individual 360° Student Profile Dossier")
    
    if not s_view_df.empty:
        student_picker_opts = {r['student_id']: f"{r['student_id']} - {r['name']} ({r['risk_level']} Risk | Score: {r['student_success_score']:.1f})" for _, r in s_view_df.iterrows()}
        selected_stu_id = st.selectbox("Select Student to Inspect:", options=list(student_picker_opts.keys()), format_func=lambda x: student_picker_opts[x])
        s_rec = s_view_df[s_view_df['student_id'] == selected_stu_id].iloc[0]
        
        # Calculate full score details & drivers
        score_details = calculate_student_success_score(s_rec, st.session_state.custom_weights)
        root_causes, mitigations = analyze_root_causes(s_rec)

        p_col1, p_col2 = st.columns([1.1, 2.9])
        with p_col1:
            st.markdown(f"""
            <div class="dexa-card" style="text-align: center;">
                <img src="{s_rec['photo_url']}" style="width: 80px; height: 80px; border-radius: 50%; object-fit: cover; border: 3px solid #BFDBFE; margin-bottom: 0.5rem;"/>
                <h3 style="margin: 0; color: #0F172A; font-size: 1.15rem;">{s_rec['name']}</h3>
                <div style="font-size: 0.8rem; color: #64748B;">{s_rec['student_id']} • {s_rec['roll_number']}</div>
                <div style="margin: 0.4rem 0;">
                    <span class="pill {'pill-high' if s_rec['risk_level']=='High' else ('pill-medium' if s_rec['risk_level']=='Medium' else 'pill-low')}">{s_rec['risk_level']} Risk</span>
                    <span class="pill pill-brand">Yr {s_rec['year']} {s_rec['section']}</span>
                </div>
                <div style="font-size: 0.78rem; color: #475569; margin-top: 0.5rem;">
                    Mentor: <b>{s_rec['faculty_mentor']}</b><br/>
                    Segment: <b>{s_rec['student_segment']}</b>
                </div>
            </div>
            """, unsafe_allow_html=True)

            pdf_dos = generate_student_pdf(s_rec, root_causes, mitigations)
            st.download_button(
                f"📥 Download PDF Dossier",
                data=pdf_dos,
                file_name=f"DEXA_Dossier_{s_rec['student_id']}.pdf",
                mime="application/pdf",
                type="primary",
                use_container_width=True
            )

        with p_col2:
            st.markdown(f"""
            <div class="dexa-card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <h4 style="margin: 0; color: #1E3A8A;">Student Success Score: {score_details['total_score']:.1f} / 100</h4>
                    <span class="pill pill-brand">Data Completeness: {score_details['completeness_pct']}%</span>
                </div>
                <div style="display: flex; gap: 0.5rem; margin: 0.65rem 0; flex-wrap: wrap;">
                    <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 6px; padding: 6px 10px; font-size: 0.78rem;">
                        Academics (35%): <b>{score_details['category_scores'].get('academics', 0):.1f}</b>
                    </div>
                    <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 6px; padding: 6px 10px; font-size: 0.78rem;">
                        Attendance (20%): <b>{score_details['category_scores'].get('attendance', 0):.1f}</b>
                    </div>
                    <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 6px; padding: 6px 10px; font-size: 0.78rem;">
                        LMS (15%): <b>{score_details['category_scores'].get('lms_engagement', 0):.1f}</b>
                    </div>
                    <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 6px; padding: 6px 10px; font-size: 0.78rem;">
                        Placement (20%): <b>{score_details['category_scores'].get('placement_readiness', 0):.1f}</b>
                    </div>
                    <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 6px; padding: 6px 10px; font-size: 0.78rem;">
                        Skills (10%): <b>{score_details['category_scores'].get('skills_feedback', 0):.1f}</b>
                    </div>
                </div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem; margin-top: 0.5rem; font-size: 0.8rem;">
                    <div style="background: #ECFDF5; border: 1px solid #A7F3D0; border-radius: 6px; padding: 8px;">
                        <b style="color: #065F46;">✅ Positive Drivers:</b><br/>
                        {'<br/>'.join(['• ' + d for d in score_details['positive_drivers']])}
                    </div>
                    <div style="background: #FEF2F2; border: 1px solid #FECACA; border-radius: 6px; padding: 8px;">
                        <b style="color: #991B1B;">⚠️ Negative Drivers / Vulnerabilities:</b><br/>
                        {'<br/>'.join(['• ' + d for d in score_details['negative_drivers']])}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # 360 Radar Chart
            cats = ['Coding', 'Aptitude', 'Tech Skills', 'Comm', 'Soft Skills', 'Problem Solving', 'Academics', 'Attendance']
            s_vals = [
                float(s_rec['coding_score']), float(s_rec['aptitude_score']), float(s_rec['technical_skill_score']),
                float(s_rec['communication_score']), float(s_rec['soft_skill_score']), float(s_rec['problem_solving_score']),
                float(s_rec['cgpa'] * 10.0), float(s_rec['attendance_overall_pct'])
            ]
            b_vals = [
                float(df['coding_score'].mean()), float(df['aptitude_score'].mean()), float(df['technical_skill_score'].mean()),
                float(df['communication_score'].mean()), float(df['soft_skill_score'].mean()), float(df['problem_solving_score'].mean()),
                float(df['cgpa'].mean() * 10.0), float(df['attendance_overall_pct'].mean())
            ]
            fig_rad = go.Figure()
            fig_rad.add_trace(go.Scatterpolar(r=s_vals + [s_vals[0]], theta=cats + [cats[0]], fill='toself', name=s_rec['name'], line_color='#1E40AF', fillcolor='rgba(30, 64, 175, 0.2)'))
            fig_rad.add_trace(go.Scatterpolar(r=b_vals + [b_vals[0]], theta=cats + [cats[0]], fill='toself', name='Batch Mean', line_color='#0284C7', fillcolor='rgba(2, 132, 199, 0.1)', line=dict(dash='dash')))
            fig_rad.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100], color="#64748B"), bgcolor="#FFFFFF"), paper_bgcolor="#FFFFFF", font_color="#0F172A", margin=dict(l=30, r=30, t=30, b=30), height=300)
            st.plotly_chart(fig_rad, use_container_width=True)


# =========================================================
# TAB 3: ⚠️ RISK & INTERVENTIONS (PRIORITIZED QUEUE & SIM)
# =========================================================
elif st.session_state.active_tab == "⚠️ Risk & Interventions":
    st.markdown("## ⚠️ Prioritized Interventions & Explainable AI Diagnosis")

    tab_int1, tab_int2 = st.tabs(["📋 Prioritized Intervention Queue", "🔬 AI Diagnosis & Score Recovery Simulation"])

    with tab_int1:
        st.markdown("### 🚨 Prioritized Institutional Intervention Queue")
        st.markdown("Ranked by multi-criteria urgency score combining detention warnings, backlogs, and academic trend.")

        int_queue = generate_prioritized_intervention_queue(filtered_df)
        st.markdown(f"**{len(int_queue)} students requiring proactive intervention in current scope:**")
        st.dataframe(int_queue, use_container_width=True, height=280)

        st.markdown("---")
        st.markdown("### 📝 Log / Update Intervention Record")
        with st.form("log_intervention_form"):
            int_stu_opts = {r['student_id']: f"{r['student_id']} - {r['name']} ({r['risk_level']} Risk)" for _, r in filtered_df.iterrows()}
            c_int1, c_int2 = st.columns(2)
            with c_int1:
                sel_int_stu = st.selectbox("Student Identifier:", options=list(int_stu_opts.keys()), format_func=lambda x: int_stu_opts[x])
                int_type = st.selectbox("Intervention Category:", ["1-on-1 Academic Counseling", "Attendance Warning & Detention Contract", "Fast-Track Arrear Remediation", "Coding & Placement Practice Bootcamp", "Mental Well-being Consultation"])
            with c_int2:
                int_date = st.date_input("Follow-up Milestone Date:", datetime.now() + timedelta(days=7))
                int_status = st.selectbox("Intervention Status:", ["Pending Action", "In Progress", "Scheduled", "Resolved"])
            int_notes = st.text_area("Faculty Counselor Notes & Prescriptions:", placeholder="Describe the discussion, agreed recovery plan, and next review date...")
            submit_int = st.form_submit_button("💾 Save Intervention Record", type="primary")

            if submit_int:
                stu_obj = filtered_df[filtered_df['student_id'] == sel_int_stu].iloc[0]
                new_int = {
                    "id": f"INT-{len(st.session_state.interventions)+1:03d}",
                    "student_id": sel_int_stu,
                    "student_name": stu_obj['name'],
                    "mentor": stu_obj['faculty_mentor'],
                    "category": int_type,
                    "notes": int_notes,
                    "follow_up_date": int_date.strftime("%Y-%m-%d"),
                    "status": int_status,
                    "logged_at": datetime.now().strftime("%b %d, %Y")
                }
                st.session_state.interventions.insert(0, new_int)
                st.success(f"Intervention {new_int['id']} successfully recorded for {stu_obj['name']}!")

        st.markdown("<b>Recent Recorded Interventions:</b>", unsafe_allow_html=True)
        for it in st.session_state.interventions[:4]:
            st.markdown(f"""
            <div class="dexa-card" style="padding: 0.75rem 1rem; border-left: 3px solid #1E40AF;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <b>{it['student_name']} ({it['student_id']})</b>
                    <span class="pill pill-brand">{it['status']}</span>
                </div>
                <div style="font-size:0.78rem; color:#64748B;">Type: <b>{it['category']}</b> • Logged: {it['logged_at']} • Review: <b>{it['follow_up_date']}</b></div>
                <div style="font-size:0.8rem; color:#334155; margin-top:0.25rem;">{it['notes']}</div>
            </div>
            """, unsafe_allow_html=True)

    with tab_int2:
        st.markdown("### 🔬 Explainable AI Risk Diagnosis & Mitigation Engine")
        
        sim_stu_opts = {r['student_id']: f"{r['student_id']} - {r['name']} ({r['risk_level']} Risk)" for _, r in filtered_df.iterrows()}
        sim_stu_id = st.selectbox("Select Student for Root Cause Audit:", options=list(sim_stu_opts.keys()), format_func=lambda x: sim_stu_opts[x], key="sim_sel_box")
        s_target = filtered_df[filtered_df['student_id'] == sim_stu_id].iloc[0]
        
        root_causes, mitigations = analyze_root_causes(s_target)
        pred_flag, pred_prob = predict_student_risk(model, s_target.to_dict())

        sb1, sb2, sb3 = st.columns([2, 1, 1])
        with sb1:
            st.markdown(f"""
            <div class="dexa-card">
                <h3 style="margin: 0; color: #0F172A;">{s_target['name']} ({s_target['student_id']})</h3>
                <div style="color: #64748B; font-size: 0.84rem; margin: 0.2rem 0;">Yr {s_target['year']} {s_target['section']} | Mentor: <b>{s_target['faculty_mentor']}</b></div>
                <div style="font-size: 0.8rem; color: #334155;">CGPA: <b>{s_target['cgpa']:.2f}</b> • Attendance: <b>{s_target['attendance_overall_pct']:.1f}%</b> • Backlogs: <b>{s_target['backlogs']}</b></div>
            </div>
            """, unsafe_allow_html=True)
        with sb2:
            st.markdown(f"""
            <div class="dexa-card" style="text-align: center;">
                <div style="font-size: 0.72rem; color: #64748B; text-transform: uppercase;">AI Risk Probability</div>
                <div style="font-size: 1.75rem; font-weight: 800; color: {'#DC2626' if pred_prob > 0.5 else '#059669'};">{pred_prob*100:.1f}%</div>
                <span class="pill {'pill-high' if pred_prob > 0.5 else 'pill-low'}">{'AT RISK' if pred_prob > 0.5 else 'SAFE'}</span>
            </div>
            """, unsafe_allow_html=True)
        with sb3:
            st.markdown(f"""
            <div class="dexa-card" style="text-align: center;">
                <div style="font-size: 0.72rem; color: #64748B; text-transform: uppercase;">Success Score</div>
                <div style="font-size: 1.75rem; font-weight: 800; color: #1E40AF;">{s_target['student_success_score']:.1f}</div>
                <div style="font-size: 0.72rem; color: #64748B;">Cohort Mean: {df['student_success_score'].mean():.1f}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("#### ⚠️ Identified Root Cause Indicators")
        rc_cols = st.columns(len(root_causes) if len(root_causes) <= 3 else 3)
        for i, cause in enumerate(root_causes):
            with rc_cols[i % 3]:
                border_c = "#DC2626" if cause['severity'] == "CRITICAL" else ("#D97706" if cause['severity'] == "HIGH" else "#2563EB")
                st.markdown(f"""
                <div class="dexa-card" style="border-left: 4px solid {border_c};">
                    <div style="display:flex; justify-content:space-between; margin-bottom:0.25rem;">
                        <span style="font-weight:700; color:#0F172A; font-size:0.84rem;">{cause['indicator']}</span>
                        <span class="pill {'pill-high' if cause['severity']=='CRITICAL' else ('pill-medium' if cause['severity']=='HIGH' else 'pill-brand')}">{cause['severity']}</span>
                    </div>
                    <div style="font-size:0.8rem; color:#475569;">Observed: <b>{cause['current']}</b> (Threshold: {cause['threshold']})</div>
                    <div style="font-size:0.75rem; color:#64748B; margin-top:0.25rem;">{cause['description']}</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("#### 🛠️ Prescribed Remedial Interventions")
        m_cols = st.columns(len(mitigations) if len(mitigations) <= 3 else 3)
        for i, mit in enumerate(mitigations):
            with m_cols[i % 3]:
                st.markdown(f"""
                <div class="dexa-card" style="border-top: 3px solid #059669; height: 100%;">
                    <span class="pill pill-low">{mit['type']}</span>
                    <h4 style="margin: 0.3rem 0; color: #0F172A; font-size:0.92rem;">{mit['title']}</h4>
                    <p style="font-size: 0.78rem; color: #475569; line-height: 1.4;">{mit['action']}</p>
                    <div style="color: #059669; font-weight: 700; font-size: 0.75rem;">📈 {mit['impact']}</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("#### 🎛️ Interactive Score & Risk Recovery Simulator")
        sc1, sc2, sc3, sc4 = st.columns(4)
        with sc1:
            att_b = st.slider("Attendance Gain (+%)", 0, 30, 10, step=2)
        with sc2:
            asg_b = st.slider("Assignment Gain (+%)", 0, 40, 15, step=5)
        with sc3:
            cod_b = st.slider("Coding Gain (+pts)", 0, 40, 15, step=5)
        with sc4:
            apt_b = st.slider("Aptitude Gain (+pts)", 0, 40, 10, step=5)

        rec = simulate_recovery(model, s_target, delta_attendance=att_b, delta_assignment=asg_b, delta_coding=cod_b, delta_aptitude=apt_b)
        st.markdown(f"""
        <div class="dexa-card" style="background: #F0FDF4; border: 1px solid #BBF7D0; padding: 1.15rem;">
            <span class="pill pill-low">Projected Recovery Outcome</span>
            <div style="font-size: 0.95rem; font-weight: 700; color: #065F46; margin: 0.4rem 0;">{rec['summary']}</div>
        </div>
        """, unsafe_allow_html=True)


# =========================================================
# TAB 4: 🎓 ACADEMIC PERFORMANCE (MARKS & BACKLOGS)
# =========================================================
elif st.session_state.active_tab == "🎓 Academic Performance":
    st.markdown("## 🎓 Academic Performance & Continuous Evaluation Analytics")

    ac_k1, ac_k2, ac_k3, ac_k4 = st.columns(4)
    with ac_k1:
        st.markdown(f"""<div class="kpi-container"><div class="kpi-label">Cohort CGPA Range</div><div class="kpi-value">{filtered_df['cgpa'].min():.2f} - {filtered_df['cgpa'].max():.2f}</div><div class="kpi-sub">Mean: {filtered_df['cgpa'].mean():.2f}</div></div>""", unsafe_allow_html=True)
    with ac_k2:
        tot_b = filtered_df['backlogs'].sum()
        st.markdown(f"""<div class="kpi-container"><div class="kpi-label">Total Backlogs Load</div><div class="kpi-value" style="color: {'#DC2626' if tot_b>0 else '#059669'};">{tot_b}</div><div class="kpi-sub">{(filtered_df['backlogs']>0).sum()} Students Affected</div></div>""", unsafe_allow_html=True)
    with ac_k3:
        st.markdown(f"""<div class="kpi-container"><div class="kpi-label">Avg IA1 Marks</div><div class="kpi-value">{filtered_df['ia1_marks_50'].mean():.1f} / 50</div><div class="kpi-sub">IA2: {filtered_df['ia2_marks_50'].mean():.1f} | IA3: {filtered_df['ia3_marks_50'].mean():.1f}</div></div>""", unsafe_allow_html=True)
    with ac_k4:
        st.markdown(f"""<div class="kpi-container"><div class="kpi-label">Math Subject Mean</div><div class="kpi-value">{filtered_df['mathematics_marks'].mean():.1f} / 100</div><div class="kpi-sub">Core 1: {filtered_df['core_subject_1_marks'].mean():.1f} / 100</div></div>""", unsafe_allow_html=True)

    st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)

    fig_gpa = px.box(filtered_df, x="year", y="cgpa", color="year", points="all", labels={"year": "Year of Study", "cgpa": "Cumulative GPA"})
    fig_gpa = apply_enterprise_chart_theme(fig_gpa, "CGPA Distribution Across Academic Years")
    fig_gpa.update_layout(showlegend=False)
    st.plotly_chart(fig_gpa, use_container_width=True)

    st.markdown("### 📋 Student Marks & Assessment Registry")
    st.dataframe(filtered_df[['student_id', 'roll_number', 'name', 'year', 'cgpa', 'current_sem_gpa', 'backlogs', 'ia1_marks_50', 'ia2_marks_50', 'ia3_marks_50', 'mathematics_marks', 'core_subject_1_marks', 'faculty_mentor']], use_container_width=True, height=280)


# =========================================================
# TAB 5: 📅 ATTENDANCE (DETENTION WATCH & TRENDS)
# =========================================================
elif st.session_state.active_tab == "📅 Attendance":
    st.markdown("## 📅 Institutional Attendance Monitoring & Detention Watch")

    att_k1, att_k2, att_k3, att_k4 = st.columns(4)
    with att_k1:
        st.markdown(f"""<div class="kpi-container"><div class="kpi-label">Overall Attendance</div><div class="kpi-value">{filtered_df['attendance_overall_pct'].mean():.1f}%</div><div class="kpi-sub">Institutional Average</div></div>""", unsafe_allow_html=True)
    with att_k2:
        st.markdown(f"""<div class="kpi-container"><div class="kpi-label">Theory Attendance</div><div class="kpi-value">{filtered_df['attendance_theory_pct'].mean():.1f}%</div><div class="kpi-sub">Lecture Regularity</div></div>""", unsafe_allow_html=True)
    with att_k3:
        st.markdown(f"""<div class="kpi-container"><div class="kpi-label">Laboratory Attendance</div><div class="kpi-value">{filtered_df['attendance_lab_pct'].mean():.1f}%</div><div class="kpi-sub">Practical Sessions</div></div>""", unsafe_allow_html=True)
    with att_k4:
        low_att_cnt = (filtered_df['attendance_overall_pct'] < 75.0).sum()
        st.markdown(f"""<div class="kpi-container" style="border-left: 3px solid #DC2626;"><div class="kpi-label">Detention Warning (<75%)</div><div class="kpi-value" style="color:#DC2626;">{low_att_cnt}</div><div class="kpi-sub">{(low_att_cnt/len(filtered_df)*100) if len(filtered_df)>0 else 0:.1f}% of cohort</div></div>""", unsafe_allow_html=True)

    st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)

    fig_att = px.scatter(
        filtered_df,
        x="attendance_overall_pct",
        y="cgpa",
        color="risk_level",
        color_discrete_map={"Low": "#059669", "Medium": "#D97706", "High": "#DC2626"},
        hover_data=["student_id", "name", "backlogs", "faculty_mentor"],
        labels={"attendance_overall_pct": "Overall Attendance (%)", "cgpa": "CGPA"}
    )
    fig_att.add_vline(x=75, line_dash="dash", line_color="#DC2626", annotation_text="75% Cutoff")
    fig_att = apply_enterprise_chart_theme(fig_att, "Attendance vs Academic CGPA Correlation (with 75% Cutoff Line)")
    st.plotly_chart(fig_att, use_container_width=True)

    st.markdown("### 🚨 Detention Watchlist (Overall Attendance < 75.0%)")
    det_df = filtered_df[filtered_df['attendance_overall_pct'] < 75.0].sort_values(by="attendance_overall_pct", ascending=True)
    st.dataframe(det_df[['student_id', 'roll_number', 'name', 'year', 'attendance_overall_pct', 'attendance_theory_pct', 'attendance_lab_pct', 'cgpa', 'backlogs', 'faculty_mentor', 'parent_mobile']], use_container_width=True, height=220)


# =========================================================
# TAB 6: 💻 LMS & ENGAGEMENT (PORTAL ACTIVITY & QUIZZES)
# =========================================================
elif st.session_state.active_tab == "💻 LMS & Engagement":
    st.markdown("## 💻 Learning Management System (LMS) Engagement Telemetry")

    l1, l2, l3, l4 = st.columns(4)
    with l1:
        st.markdown(f"""<div class="kpi-container"><div class="kpi-label">Assignment Completion</div><div class="kpi-value">{filtered_df['assignment_completion_pct'].mean():.1f}%</div><div class="kpi-sub">Benchmark: >= 75%</div></div>""", unsafe_allow_html=True)
    with l2:
        st.markdown(f"""<div class="kpi-container"><div class="kpi-label">Avg Logins / Week</div><div class="kpi-value">{filtered_df['lms_logins_per_week'].mean():.1f}</div><div class="kpi-sub">Portal Frequency</div></div>""", unsafe_allow_html=True)
    with l3:
        st.markdown(f"""<div class="kpi-container"><div class="kpi-label">Hours / Week</div><div class="kpi-value">{filtered_df['lms_hours_per_week'].mean():.1f} hrs</div><div class="kpi-sub">Screen Time</div></div>""", unsafe_allow_html=True)
    with l4:
        st.markdown(f"""<div class="kpi-container"><div class="kpi-label">Quiz Avg Score</div><div class="kpi-value">{filtered_df['lms_quiz_avg_score'].mean():.1f} / 100</div><div class="kpi-sub">Weekly Assessments</div></div>""", unsafe_allow_html=True)

    st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)

    fig_lms = px.histogram(filtered_df, x="assignment_completion_pct", color="risk_level", color_discrete_map={"Low": "#059669", "Medium": "#D97706", "High": "#DC2626"}, nbins=25, labels={"assignment_completion_pct": "Assignment Completion %"})
    fig_lms = apply_enterprise_chart_theme(fig_lms, "Assignment Submission Rate Distribution")
    st.plotly_chart(fig_lms, use_container_width=True)

    st.markdown("### 📋 Student LMS Activity Logs")
    st.dataframe(filtered_df[['student_id', 'roll_number', 'name', 'assignment_completion_pct', 'lms_logins_per_week', 'lms_hours_per_week', 'days_since_last_lms_login', 'lms_quiz_avg_score', 'faculty_mentor']], use_container_width=True, height=280)


# =========================================================
# TAB 7: 💼 PLACEMENT READINESS (CODING, APTITUDE, PAT)
# =========================================================
elif st.session_state.active_tab == "💼 Placement Readiness":
    st.markdown("## 💼 Placement & Training (PAT) Readiness Hub")

    pl1, pl2, pl3, pl4 = st.columns(4)
    with pl1:
        st.markdown(f"""<div class="kpi-container"><div class="kpi-label">Avg Readiness Score</div><div class="kpi-value">{filtered_df['placement_readiness_score'].mean():.1f} / 100</div><div class="kpi-sub">Composite Metric</div></div>""", unsafe_allow_html=True)
    with pl2:
        st.markdown(f"""<div class="kpi-container"><div class="kpi-label">Avg Coding Score</div><div class="kpi-value">{filtered_df['coding_score'].mean():.1f} / 100</div><div class="kpi-sub">Assessment Mean</div></div>""", unsafe_allow_html=True)
    with pl3:
        st.markdown(f"""<div class="kpi-container"><div class="kpi-label">Avg Aptitude Score</div><div class="kpi-value">{filtered_df['aptitude_score'].mean():.1f} / 100</div><div class="kpi-sub">Quantitative & Logic</div></div>""", unsafe_allow_html=True)
    with pl4:
        st.markdown(f"""<div class="kpi-container"><div class="kpi-label">Mock Interview Score</div><div class="kpi-value">{filtered_df['mock_interview_score'].mean():.1f} / 100</div><div class="kpi-sub">Panel Rating</div></div>""", unsafe_allow_html=True)

    st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)

    fig_pat = px.histogram(filtered_df, x="placement_readiness_score", color="placement_status", barmode="group", labels={"placement_readiness_score": "Placement Readiness Score (0-100)"})
    fig_pat = apply_enterprise_chart_theme(fig_pat, "Placement Readiness Distribution by Status")
    st.plotly_chart(fig_pat, use_container_width=True)

    st.markdown("### 📋 Student Technical & Placement Metrics")
    st.dataframe(filtered_df[['student_id', 'roll_number', 'name', 'year', 'placement_status', 'placement_readiness_score', 'coding_score', 'aptitude_score', 'mock_interview_score', 'technical_skill_score', 'communication_score', 'hackathons_participated', 'certifications_completed']], use_container_width=True, height=280)


# =========================================================
# TAB 8: 🧩 STUDENT SEGMENTS (DATA-DRIVEN COHORTS)
# =========================================================
elif st.session_state.active_tab == "🧩 Student Segments":
    st.markdown("## 🧩 Data-Driven Student Segmentation Engine")
    st.markdown("Deterministic multi-dimensional clustering classifying students into actionable institutional cohorts.")

    seg_counts = filtered_df['student_segment'].value_counts()
    
    sc_row1 = st.columns(3)
    with sc_row1[0]:
        c_ha = seg_counts.get("High Academic — Low Placement Readiness", 0)
        st.markdown(f"""<div class="dexa-card" style="border-left:4px solid #D97706;"><span class="pill pill-medium">Medium Priority</span><h4 style="margin:0.25rem 0;">High Academic — Low Placement</h4><div style="font-size:1.5rem; font-weight:800; color:#0F172A;">{c_ha} Students</div><div style="font-size:0.75rem; color:#64748B;">Strong GPA (>=7.5) but struggling in coding (<50)</div></div>""", unsafe_allow_html=True)
    with sc_row1[1]:
        c_dis = seg_counts.get("Disengaged — Needs Urgent Intervention", 0)
        st.markdown(f"""<div class="dexa-card" style="border-left:4px solid #DC2626;"><span class="pill pill-high">Critical Priority</span><h4 style="margin:0.25rem 0;">Disengaged — Urgent Intervention</h4><div style="font-size:1.5rem; font-weight:800; color:#DC2626;">{c_dis} Students</div><div style="font-size:0.75rem; color:#64748B;">Attendance < 75% + Portal Inactivity (>=5 days)</div></div>""", unsafe_allow_html=True)
    with sc_row1[2]:
        c_la = seg_counts.get("Low Academic — High Engagement", 0)
        st.markdown(f"""<div class="dexa-card" style="border-left:4px solid #2563EB;"><span class="pill pill-brand">High Priority</span><h4 style="margin:0.25rem 0;">Low Academic — High Engagement</h4><div style="font-size:1.5rem; font-weight:800; color:#0F172A;">{c_la} Students</div><div style="font-size:0.75rem; color:#64748B;">Struggling with exams despite regular LMS logins</div></div>""", unsafe_allow_html=True)

    sc_row2 = st.columns(2)
    with sc_row2[0]:
        c_ach = seg_counts.get("High Achiever — Placement Ready", 0)
        st.markdown(f"""<div class="dexa-card" style="border-left:4px solid #059669;"><span class="pill pill-low">Honors Track</span><h4 style="margin:0.25rem 0;">High Achiever — Placement Ready</h4><div style="font-size:1.5rem; font-weight:800; color:#059669;">{c_ach} Students</div><div style="font-size:0.75rem; color:#64748B;">All-round excellence (GPA>=7.5, Att>=80%, Code>=65)</div></div>""", unsafe_allow_html=True)
    with sc_row2[1]:
        c_avg = seg_counts.get("Average — Steady", 0)
        st.markdown(f"""<div class="dexa-card" style="border-left:4px solid #64748B;"><span class="pill pill-brand">Standard Track</span><h4 style="margin:0.25rem 0;">Average — Steady</h4><div style="font-size:1.5rem; font-weight:800; color:#0F172A;">{c_avg} Students</div><div style="font-size:0.75rem; color:#64748B;">Tracking within standard institutional parameters</div></div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 🔍 Segment Drilldown & Recommended Action Plan")
    sel_seg = st.selectbox("Select Segment to Inspect Cohort Roster:", list(SEGMENT_DEFINITIONS.keys()))
    seg_info = SEGMENT_DEFINITIONS[sel_seg]
    
    st.markdown(f"""
    <div style="background:#F8FAFC; border:1px solid #CBD5E1; border-radius:8px; padding:0.85rem; margin-bottom:0.75rem; font-size:0.82rem;">
        <b>Cohort Definition:</b> {seg_info['description']}<br/>
        <b>Primary Recommended Intervention:</b> <span style="color:#1E40AF; font-weight:700;">{seg_info['primary_intervention']}</span>
    </div>
    """, unsafe_allow_html=True)

    seg_students = filtered_df[filtered_df['student_segment'] == sel_seg]
    st.markdown(f"**Found {len(seg_students)} students in '{sel_seg}':**")
    st.dataframe(seg_students[['student_id', 'roll_number', 'name', 'year', 'section', 'cgpa', 'attendance_overall_pct', 'coding_score', 'placement_readiness_score', 'backlogs', 'faculty_mentor']], use_container_width=True, height=280)


# =========================================================
# TAB 9: 📄 REPORTS & BRIEFS (PDF & CSV EXPORTS)
# =========================================================
elif st.session_state.active_tab == "📄 Reports & Briefs":
    st.markdown("## 📄 Institutional Reports, Micro-Audits & Data Exports")

    r_c1, r_c2 = st.columns(2)
    with r_c1:
        st.markdown("""
        <div class="dexa-card">
            <h3 style="margin-top:0; color:#0F172A; font-size:1.15rem;">🏛️ Department Executive Brief (PDF)</h3>
            <p style="color:#64748B; font-size:0.82rem; line-height:1.4;">
                Download printable executive report with institutional KPI tables, risk composition, and detention watch rosters generated via ReportLab.
            </p>
        """, unsafe_allow_html=True)
        pdf_dept = generate_department_pdf(filtered_df)
        st.download_button("📥 Download Executive Brief (PDF)", data=pdf_dept, file_name="DEXA_Department_Brief.pdf", mime="application/pdf", type="primary", use_container_width=True)
        st.download_button("📊 Export Filtered Cohort Dataset (CSV)", data=filtered_df.to_csv(index=False).encode('utf-8'), file_name="DEXA_Filtered_Cohort.csv", mime="text/csv", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with r_c2:
        st.markdown("""
        <div class="dexa-card">
            <h3 style="margin-top:0; color:#0F172A; font-size:1.15rem;">👤 Individual Student Dossier (PDF)</h3>
            <p style="color:#64748B; font-size:0.82rem; line-height:1.4;">
                Generate official student academic dossier with root cause telemetry, radar matrix, and personalized remedial plan.
            </p>
        """, unsafe_allow_html=True)
        rep_stu_opts = {r['student_id']: f"{r['student_id']} - {r['name']}" for _, r in filtered_df.iterrows()}
        if rep_stu_opts:
            sel_rep_id = st.selectbox("Select Student for PDF Export:", options=list(rep_stu_opts.keys()), format_func=lambda x: rep_stu_opts[x], key="rep_stu_sel")
            rep_stu = filtered_df[filtered_df['student_id'] == sel_rep_id].iloc[0]
            rep_rc, rep_mt = analyze_root_causes(rep_stu)
            pdf_stu = generate_student_pdf(rep_stu, rep_rc, rep_mt)
            st.download_button(f"📥 Download Dossier for {rep_stu['name']} (PDF)", data=pdf_stu, file_name=f"DEXA_Dossier_{rep_stu['student_id']}.pdf", mime="application/pdf", type="primary", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("### 📋 Prioritized Intervention Queue Export")
    q_exp = generate_prioritized_intervention_queue(filtered_df)
    st.download_button("📥 Export Prioritized Interventions Queue (CSV)", data=q_exp.to_csv(index=False).encode('utf-8'), file_name="DEXA_Intervention_Queue.csv", mime="text/csv", use_container_width=True)


# =========================================================
# TAB 10: ⚙️ SETTINGS & DATA INTEGRATION (IMPORT & WEIGHTS)
# =========================================================
elif st.session_state.active_tab == "⚙️ Settings & Data Integration":
    st.markdown("## ⚙️ Settings, Data Integration & Score Weight Configuration")

    set_t1, set_t2 = st.tabs(["📥 Data Integration & Import Pipeline", "⚖️ Student Success Score Weight Tuning"])

    with set_t1:
        st.markdown("### 📥 Import Student Dataset (CSV / Excel)")
        st.markdown("""
        Upload institutional academic records. The engine validates required columns (`student_id`, `name`, `cgpa`, `attendance_overall_pct`, etc.), eliminates duplicates, renormalizes missing values, and recomputes success scores.
        """)

        up_file = st.file_uploader("Choose CSV or Excel file", type=['csv', 'xlsx', 'xls'], key="dataset_uploader")
        if up_file is not None:
            import_res = validate_and_import_student_data(up_file, up_file.name)
            if import_res['success']:
                st.success(import_res['message'])
                imp_stats = import_res['stats']
                s_c1, s_c2, s_c3 = st.columns(3)
                with s_c1:
                    st.metric("Total Valid Records", imp_stats['total_rows'])
                with s_c2:
                    st.metric("Duplicates Dropped", imp_stats['duplicates_removed'])
                with s_c3:
                    st.metric("Data Completeness", f"{imp_stats['data_completeness_pct']}%")

                if st.button("🚀 Apply Imported Dataset to Active Portal Session", type="primary"):
                    st.session_state.dataset = import_res['imported_df']
                    st.success("Master dataset updated in session! Reloading dashboard...")
                    st.rerun()
            else:
                st.error(import_res['message'])
                for err in import_res.get('errors', []):
                    st.markdown(f"- ❌ {err}")

        st.markdown("---")
        st.markdown("<b>Download Reference CSV Template:</b>", unsafe_allow_html=True)
        template_df = pd.DataFrame([{
            "student_id": "STU9001",
            "roll_number": "24CS901",
            "name": "Sample Student",
            "department": "CSE",
            "year": 3,
            "section": "A",
            "faculty_mentor": "Dr. T. Ramesh",
            "cgpa": 7.85,
            "attendance_overall_pct": 82.5,
            "backlogs": 0,
            "coding_score": 65.0,
            "aptitude_score": 60.0,
            "assignment_completion_pct": 85.0
        }])
        st.download_button("📥 Download Standard Schema CSV Template", data=template_df.to_csv(index=False).encode('utf-8'), file_name="DEXA_Student_Schema_Template.csv", mime="text/csv")

    with set_t2:
        st.markdown("### ⚖️ Multi-Criteria Success Score Weight Tuning")
        st.markdown("""
        Configure weights for the transparent 0–100 Student Success Score. The model calculates composite indices per dimension and transparently renormalizes weights when individual indicators are unavailable.
        """)

        w_col1, w_col2 = st.columns(2)
        with w_col1:
            w_acad = st.slider("Academics Weight (CGPA, IA marks, Arrears)", 0.10, 0.50, float(st.session_state.custom_weights['academics']), step=0.05)
            w_att = st.slider("Attendance Weight (Overall & 30-Day Trend)", 0.10, 0.40, float(st.session_state.custom_weights['attendance']), step=0.05)
            w_lms = st.slider("LMS & Engagement Weight (Assignments, Logins)", 0.05, 0.30, float(st.session_state.custom_weights['lms_engagement']), step=0.05)
        with w_col2:
            w_pat = st.slider("Placement Readiness Weight (Coding, Aptitude, PAT)", 0.10, 0.40, float(st.session_state.custom_weights['placement_readiness']), step=0.05)
            w_skill = st.slider("Skills & Feedback Weight (Soft skills, Faculty rating)", 0.05, 0.20, float(st.session_state.custom_weights['skills_feedback']), step=0.05)

            raw_sum = w_acad + w_att + w_lms + w_pat + w_skill
            st.markdown(f"**Total Weight Sum:** `{raw_sum*100:.0f}%` {'(Optimal 100%)' if round(raw_sum, 2) == 1.0 else '(⚠️ Normalized automatically if != 100%)'}")

        if st.button("💾 Apply Weights & Recalculate Cohort Scores", type="primary"):
            st.session_state.custom_weights = {
                'academics': w_acad,
                'attendance': w_att,
                'lms_engagement': w_lms,
                'placement_readiness': w_pat,
                'skills_feedback': w_skill
            }
            st.session_state.dataset = batch_compute_success_scores(st.session_state.dataset, st.session_state.custom_weights)
            st.success("Successfully recalculated 0–100 Student Success Scores across all students with updated weights!")
            st.rerun()

        st.markdown("""
        <div style="background:#F8FAFC; border:1px solid #CBD5E1; border-radius:8px; padding:0.85rem; margin-top:1rem; font-size:0.78rem; color:#475569;">
            <b>Mathematical Transparency Notice:</b> The Student Success Score is an explainable weighted multi-criteria index, not an opaque black-box ML prediction. For predictive at-risk classification, refer to the Random Forest model under the Overview tab.
        </div>
        """, unsafe_allow_html=True)


# =========================================================
# TAB 11: 👥 FACULTY DIRECTORY (HOD LEADERSHIP VIEW)
# =========================================================
elif st.session_state.active_tab == "👥 Faculty Directory":
    st.markdown("## 👥 Faculty & Staff Directory (HOD Leadership Oversight)")
    st.markdown("Comprehensive directory of all 15 department faculty members with assigned mentoring loads and feedback ratings.")

    if not df_staff.empty:
        for _, staff_m in df_staff.iterrows():
            c1, c2, c3, c4 = st.columns([1.1, 3.5, 3.5, 2])
            with c1:
                st.markdown(f"<img src='{staff_m['photo_url']}' class='staff-avatar'/>", unsafe_allow_html=True)
            with c2:
                st.markdown(f"""
                <div style="font-weight:700; color:#0F172A; font-size:0.95rem;">{staff_m['name']}</div>
                <div style="font-size:0.8rem; color:#1E40AF; font-weight:600;">{staff_m['designation']} • {staff_m['role_in_department']}</div>
                <div style="font-size:0.75rem; color:#64748B;">Staff ID: <code>{staff_m['staff_id']}</code> | Emp ID: <code>{staff_m['employee_id']}</code></div>
                <div style="font-size:0.75rem; color:#64748B;">Specialization: <b>{staff_m['specialization']}</b></div>
                """, unsafe_allow_html=True)
            with c3:
                st.markdown(f"""
                <div style="font-size:0.8rem; color:#334155;">
                    Experience: <b>{staff_m['total_experience_years']} yrs</b> • Teaching: <b>{staff_m['total_teaching_hours_per_week']} hrs/wk</b><br/>
                    Mentees Assigned: <b>{staff_m['mentees_assigned']}</b> • High Risk: <b style="color:#DC2626;">{staff_m['mentees_high_risk']}</b><br/>
                    Feedback: <b>{staff_m['student_feedback_rating_5']} / 5.0</b> • Pass %: <b>{staff_m['subject_pass_percentage']}%</b>
                </div>
                """, unsafe_allow_html=True)
            with c4:
                st.markdown(f"""
                <div style="text-align:right;">
                    <span class="pill pill-brand">{staff_m['appraisal_category']}</span><br/>
                    <div style="font-size:0.72rem; color:#64748B; margin-top:0.25rem;">Performance Score</div>
                    <div style="font-size:1.35rem; font-weight:800; color:#0F172A;">{staff_m['staff_performance_score']}</div>
                </div>
                """, unsafe_allow_html=True)
            st.markdown("<hr style='margin:0.35rem 0; border-color:#E2E8F0;'/>", unsafe_allow_html=True)


# =========================================================
# TAB: 🔔 MENTEE NOTIFICATIONS (STAFF / MENTOR VIEW)
# =========================================================
elif st.session_state.active_tab == "🔔 Mentee Notifications":
    st.markdown("## 🔔 Automated Staff Notifications & Counseling Scheduler")
    st.markdown("Automated high-risk alerts triggered when students cross critical detention or academic thresholds.")

    mentors = ["All Mentors"] + sorted(list(df['faculty_mentor'].unique()))
    default_m_idx = 0
    if st.session_state.user_role == "Staff / Mentor" and st.session_state.user_name in mentors:
        default_m_idx = mentors.index(st.session_state.user_name)
    chosen_m = st.selectbox("Filter Alerts by Mentor", mentors, index=default_m_idx)
    notifs = st.session_state.notifications if chosen_m == "All Mentors" else [n for n in st.session_state.notifications if n['mentor'] == chosen_m]

    st.markdown(f"**Showing {len(notifs)} alert notifications:**")
    for n in notifs:
        st.markdown(f"""
        <div class="dexa-card" style="padding: 0.75rem 1rem; border-left: 3px solid #DC2626; margin-bottom: 0.5rem;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div>
                    <span style="font-weight:700; color:#0F172A; font-size:0.92rem;">{n['student_name']}</span>
                    <span style="font-size:0.78rem; color:#64748B;">({n['student_id']}) • Yr {n['year']} {n.get('section', '')}</span>
                </div>
                <span class="pill {'pill-high' if n['status']=='Pending Counseling' else 'pill-low'}">{n['status']}</span>
            </div>
            <div style="font-size:0.8rem; color:#334155; margin-top:0.25rem;">Trigger: <b style="color:#DC2626;">{n['reason']}</b> | Mentor: {n['mentor']}</div>
        </div>
        """, unsafe_allow_html=True)
        ac1, ac2, _ = st.columns([2, 2, 4])
        with ac1:
            with st.popover(f"📅 Schedule Counseling for {n['student_name']}", use_container_width=True):
                c_d = st.date_input("Date", datetime.now() + timedelta(days=2), key=f"d_nt_{n['id']}")
                c_nt = st.text_area("Notes", value="Remedial session on core subjects and attendance contract.", key=f"t_nt_{n['id']}")
                if st.button("Confirm Schedule", key=f"cf_nt_{n['id']}", type="primary"):
                    n['status'] = "Counseling Scheduled"
                    st.success("Counseling scheduled!")
                    st.rerun()
        with ac2:
            if n['status'] != "Resolved":
                if st.button("Mark Resolved", key=f"rs_nt_{n['id']}", use_container_width=True):
                    n['status'] = "Resolved"
                    st.rerun()


# =========================================================
# TAB 12: 💬 COMMUNICATION & GRIEVANCES (WHATSAPP & BOX)
# =========================================================
elif st.session_state.active_tab in ["💬 Communication & Grievances", "🗳️ Anonymous Grievance Box"]:
    st.markdown("## 💬 Guardian WhatsApp Gateway & Anonymous Grievances")

    gw1, gw2 = st.columns(2)
    with gw1:
        st.markdown("### 📱 Guardian WhatsApp Notification Gateway")
        all_stu_map = {r['student_id']: f"{r['student_id']} - {r['name']} (Parent: {r['parent_name']})" for _, r in filtered_df.iterrows()}
        s_id_w = st.selectbox("Select Student for Guardian Dispatch", options=list(all_stu_map.keys()), format_func=lambda x: all_stu_map[x], key="wa_s_sel")
        st_wa = filtered_df[filtered_df['student_id'] == s_id_w].iloc[0]

        lang_w = st.radio("Language Template", ["English", "Tamil (தமிழ்)"], key="wa_lang_rad")
        if lang_w == "English":
            tmpl_w = f"Respected {st_wa['parent_name']},\n\nUpdate regarding your ward {st_wa['name']} ({st_wa['roll_number']}, Year {st_wa['year']} CSE):\n- Attendance: {st_wa['attendance_overall_pct']:.1f}%\n- CGPA: {st_wa['cgpa']:.2f}\n- Backlogs: {st_wa['backlogs']}\n\n{'URGENT: Attendance is below 75% cutoff. Please contact mentor ' + str(st_wa['faculty_mentor']) if st_wa['attendance_overall_pct'] < 75 else 'Academic standing is steady.'}\n\nRegards,\nCSE Department"
        else:
            tmpl_w = f"வணக்கம் {st_wa['parent_name']} அவர்களே,\n\n{st_wa['name']} ({st_wa['roll_number']}, {st_wa['year']}-ஆம் ஆண்டு CSE) கல்வி முன்னேற்ற தகவல்:\n- வருகை: {st_wa['attendance_overall_pct']:.1f}%\n- CGPA: {st_wa['cgpa']:.2f}\n- நிலுவை பாடங்கள்: {st_wa['backlogs']}\n\n{('முக்கிய அறிவிப்பு: வருகை பதிவு 75%-க்கு குறைவாக உள்ளது. பேராசிரியர் ' + str(st_wa['faculty_mentor']) + ' அவர்களை தொடர்பு கொள்ளவும்.') if st_wa['attendance_overall_pct'] < 75 else 'கல்வி நிலை திருப்திகரமாக உள்ளது.'}\n\nநன்றி,\nCSE துறை"

        msg_payload = st.text_area("WhatsApp Payload Message:", value=tmpl_w, height=160, key="wa_body_txt")
        if st.button("🚀 Simulate WhatsApp Send", type="primary", use_container_width=True):
            st.success(f"Notification dispatched to Guardian mobile: +91 {st_wa['parent_mobile']}!")
        wa_link = f"https://wa.me/91{st_wa['parent_mobile']}?text={urllib.parse.quote(msg_payload)}"
        st.markdown(f"""<a href="{wa_link}" target="_blank" style="text-decoration:none;"><button style="width:100%; background:#25D366; color:white; border:none; padding:9px; border-radius:8px; font-weight:700; cursor:pointer; font-size:0.85rem;">🟢 Open Real WhatsApp Web</button></a>""", unsafe_allow_html=True)

    with gw2:
        st.markdown("### 🗳️ Anonymous Campus Grievance Box")
        with st.form("anon_g_form_tab"):
            g_cat = st.selectbox("Category", ["Lab Facilities", "Hostel & Dining", "Academic Support", "Mental Well-being", "Placements"])
            g_urg = st.select_slider("Urgency", options=["Low", "Medium", "Urgent"], value="Medium")
            g_desc = st.text_area("Description", placeholder="Describe your concern frankly...")
            if st.form_submit_button("Submit Anonymously", type="primary"):
                if g_desc.strip():
                    tok = f"GFB-{abs(hash(g_desc)) % 9000 + 1000}-2026"
                    st.session_state.grievances.insert(0, {"id": tok, "category": g_cat, "urgency": g_urg, "comment": g_desc, "status": "Under Review"})
                    st.success(f"Grievance recorded! Token: **{tok}**")
                else:
                    st.error("Please enter details.")

        st.markdown("<b>Recent Grievances:</b>", unsafe_allow_html=True)
        for g in st.session_state.grievances[:3]:
            st.markdown(f"""<div class="dexa-card" style="padding:0.75rem; border-left:3px solid #1E40AF;"><span style="font-size:0.72rem; color:#1E40AF; font-weight:700;">{g['id']}</span> • <span class="pill pill-brand">{g['category']}</span><div style="font-size:0.8rem; margin:0.25rem 0;">{g['comment']}</div></div>""", unsafe_allow_html=True)


# =========================================================
# TAB: STUDENT PORTAL VIEW (FOR AUTHENTICATED STUDENTS)
# =========================================================
elif st.session_state.active_tab == "🌟 My Growth Portal":
    st.markdown("## 🌟 Personalized Student Growth Portal")

    student = df[df['student_id'] == st.session_state.user_id].iloc[0] if not df[df['student_id'] == st.session_state.user_id].empty else df.iloc[0]

    st.markdown(f"""
    <div class="dexa-card" style="display: flex; gap: 1.25rem; align-items: center; flex-wrap: wrap;">
        <img src="{student['photo_url']}" class="student-avatar" alt="Avatar"/>
        <div style="flex-grow: 1;">
            <div style="display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap;">
                <h2 style="margin: 0; color: #0F172A; font-size: 1.5rem;">{student['name']}</h2>
                <span class="pill {'pill-low' if student['risk_level']=='Low' else ('pill-medium' if student['risk_level']=='Medium' else 'pill-high')}">{student['risk_level']} Risk</span>
                <span class="pill pill-brand">⭐ {student['level_title']}</span>
            </div>
            <div style="color: #475569; font-size: 0.85rem; margin-top: 0.25rem;">
                Roll: <b>{student['roll_number']}</b> | Dept: <b>{student['department']}</b> (Year {student['year']}) | Mentor: <b>{student['faculty_mentor']}</b>
            </div>
        </div>
        <div style="text-align: right;">
            <div style="font-size: 0.75rem; color: #64748B; text-transform: uppercase;">Total Gamified XP</div>
            <div style="font-size: 1.85rem; font-weight: 800; color: #D97706;">{student['xp_points']} XP</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="margin-bottom: 1rem;">
        <div style="display:flex; justify-content:space-between; font-size:0.75rem; color:#64748B; margin-bottom:0.2rem;">
            <span>Level Progression</span><span>{student['level_progress_pct']:.1f}% to Next Rank</span>
        </div>
        <div style="background:#E2E8F0; height:8px; border-radius:999px; overflow:hidden;">
            <div style="background:#1E40AF; width:{student['level_progress_pct']}%; height:100%;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 🏆 Achievement Badges")
    b_cols = st.columns(7)
    for i, b in enumerate(student['badges']):
        with b_cols[i]:
            card_class = "unlocked" if b['unlocked'] else "locked"
            st.markdown(f"""
            <div class="badge-card {card_class}">
                <div style="font-size: 1.5rem;">{b['icon']}</div>
                <div style="font-weight: 700; font-size: 0.75rem; color: #0F172A;">{b['title']}</div>
            </div>
            """, unsafe_allow_html=True)


# =========================================================
# TAB: STUDENT RADAR & PUBLIC HALL OF FAME
# =========================================================
elif st.session_state.active_tab == "🕸️ 360° Competency Radar":
    student = df[df['student_id'] == st.session_state.user_id].iloc[0] if not df[df['student_id'] == st.session_state.user_id].empty else df.iloc[0]
    st.markdown(f"## 🕸️ 360° Competency Radar — {student['name']}")
    
    categories = ['Coding', 'Aptitude', 'Tech Skills', 'Comm', 'Soft Skills', 'Problem Solving', 'Academics', 'Attendance']
    stu_vals = [
        float(student['coding_score']), float(student['aptitude_score']), float(student['technical_skill_score']),
        float(student['communication_score']), float(student['soft_skill_score']), float(student['problem_solving_score']),
        float(student['cgpa'] * 10.0), float(student['attendance_overall_pct'])
    ]
    batch_vals = [
        float(df['coding_score'].mean()), float(df['aptitude_score'].mean()), float(df['technical_skill_score'].mean()),
        float(df['communication_score'].mean()), float(df['soft_skill_score'].mean()), float(df['problem_solving_score'].mean()),
        float(df['cgpa'].mean() * 10.0), float(df['attendance_overall_pct'].mean())
    ]
    fig_r = go.Figure()
    fig_r.add_trace(go.Scatterpolar(r=stu_vals + [stu_vals[0]], theta=categories + [categories[0]], fill='toself', name=student['name'], line_color='#1E40AF', fillcolor='rgba(30, 64, 175, 0.2)'))
    fig_r.add_trace(go.Scatterpolar(r=batch_vals + [batch_vals[0]], theta=categories + [categories[0]], fill='toself', name='Batch Average', line_color='#0284C7', fillcolor='rgba(2, 132, 199, 0.1)', line=dict(dash='dash')))
    fig_r.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100], color="#64748B"), bgcolor="#FFFFFF"), paper_bgcolor="#FFFFFF", font_color="#0F172A", margin=dict(l=40, r=40, t=50, b=40))
    st.plotly_chart(fig_r, use_container_width=True)

elif st.session_state.active_tab == "🏆 Public Hall of Fame":
    st.markdown("## 🏆 Public Hall of Fame")
    hf1, hf2, hf3 = st.tabs(["🥇 Top 10 CGPA Titans", "💻 Coding Champions", "🌟 100% Attendance Champions"])
    with hf1:
        top_cgpa = df.sort_values(by='cgpa', ascending=False).head(10)
        c_g = st.columns(5)
        for i, (_, r) in enumerate(top_cgpa.iterrows()):
            with c_g[i % 5]:
                st.markdown(f"""
                <div class="dexa-card" style="text-align:center;">
                    <img src="{r['photo_url']}" style="width:50px; height:50px; border-radius:50%; object-fit:cover;"/>
                    <div style="font-weight:700; font-size:0.8rem; color:#0F172A; margin-top:0.25rem;">{r['name']}</div>
                    <div style="font-size:1.15rem; font-weight:800; color:#D97706;">{r['cgpa']:.2f} CGPA</div>
                    <span class="pill pill-brand">Rank #{i+1}</span>
                </div>
                """, unsafe_allow_html=True)
    with hf2:
        top_code = df.sort_values(by=['coding_score', 'hackathons_participated'], ascending=False).head(10)
        c_g2 = st.columns(5)
        for i, (_, r) in enumerate(top_code.iterrows()):
            with c_g2[i % 5]:
                st.markdown(f"""
                <div class="dexa-card" style="text-align:center;">
                    <img src="{r['photo_url']}" style="width:50px; height:50px; border-radius:50%; object-fit:cover;"/>
                    <div style="font-weight:700; font-size:0.8rem; color:#0F172A; margin-top:0.25rem;">{r['name']}</div>
                    <div style="font-size:0.8rem; color:#0284C7;">Coding: <b>{r['coding_score']:.1f}</b></div>
                    <span class="pill pill-brand">Coder #{i+1}</span>
                </div>
                """, unsafe_allow_html=True)
    with hf3:
        top_att = df[df['attendance_overall_pct'] >= 95.0].sort_values(by='attendance_overall_pct', ascending=False).head(10)
        c_g3 = st.columns(5)
        for i, (_, r) in enumerate(top_att.iterrows()):
            with c_g3[i % 5]:
                st.markdown(f"""
                <div class="dexa-card" style="text-align:center;">
                    <img src="{r['photo_url']}" style="width:50px; height:50px; border-radius:50%; object-fit:cover;"/>
                    <div style="font-weight:700; font-size:0.8rem; color:#0F172A; margin-top:0.25rem;">{r['name']}</div>
                    <div style="font-size:1.15rem; font-weight:800; color:#059669;">{r['attendance_overall_pct']:.1f}%</div>
                    <span class="pill pill-low">Century Club</span>
                </div>
                """, unsafe_allow_html=True)


# ---------------------------------------------------------
# DOCKED FLOATING "ASK ZORO" ASSISTANT WIDGET (BOTTOM RIGHT)
# ---------------------------------------------------------
st.markdown("<div style='height: 4rem;'></div>", unsafe_allow_html=True)

st.markdown("""
<div class="ask-zoro-dock">
""", unsafe_allow_html=True)

with st.expander(f"💬 Ask Zoro ({'📚 Study' if st.session_state.zoro_mode=='study' else '😊 Vibe'})", expanded=st.session_state.zoro_open):
    st.markdown("""
    <div style="font-size: 0.75rem; color: #64748B; margin-bottom: 0.35rem;">
        Dual-Mode AI Academic Assistant
    </div>
    """, unsafe_allow_html=True)

    zoro_mode_sel = st.radio(
        "Zoro Assistant Mode",
        ["😊 Vibe & Sentiment", "📚 Study Copilot"],
        horizontal=True,
        label_visibility="collapsed"
    )
    st.session_state.zoro_mode = "study" if "Study" in zoro_mode_sel else "vibe"

    z_chat_box = st.container(height=240)
    with z_chat_box:
        for m in st.session_state.chat_messages[-6:]:
            if m["role"] == "user":
                st.markdown(f'<div class="chat-bubble-user">{m["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-bubble-agent">{m["content"]}</div>', unsafe_allow_html=True)

    chips = SUGGESTED_STUDY_PROMPTS if st.session_state.zoro_mode == "study" else SUGGESTED_VIBE_PROMPTS
    ch_c1, ch_c2 = st.columns(2)
    with ch_c1:
        if st.button(f"👉 {chips[0][:24]}...", key="z_chip_1", use_container_width=True):
            st.session_state.chat_messages.append({"role": "user", "content": chips[0]})
            rep = process_chatbot_query(chips[0], df, mode=st.session_state.zoro_mode)
            st.session_state.chat_messages.append({"role": "assistant", "content": rep})
            st.rerun()
    with ch_c2:
        if st.button(f"👉 {chips[1][:24]}...", key="z_chip_2", use_container_width=True):
            st.session_state.chat_messages.append({"role": "user", "content": chips[1]})
            rep = process_chatbot_query(chips[1], df, mode=st.session_state.zoro_mode)
            st.session_state.chat_messages.append({"role": "assistant", "content": rep})
            st.rerun()

    z_input = st.text_input("Ask Zoro...", placeholder="Type question here...", key="zoro_chat_input", label_visibility="collapsed")
    if st.button("Send Message", key="zoro_send_btn", type="primary", use_container_width=True):
        if z_input.strip():
            st.session_state.chat_messages.append({"role": "user", "content": z_input})
            reply = process_chatbot_query(z_input, df, mode=st.session_state.zoro_mode)
            st.session_state.chat_messages.append({"role": "assistant", "content": reply})
            st.rerun()

st.markdown("</div>", unsafe_allow_html=True)
