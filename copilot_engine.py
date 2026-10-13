"""
DEXA Voice Copilot Engine - Multilingual (English, Tamil, Tanglish) Natural Language Command Parser
"""

import re

# Presets for quick execution in UI
COPILOT_PRESETS = [
    {"label": "⚠️ Show at-risk students (English)", "cmd": "show at-risk students", "lang": "English"},
    {"label": "🔍 Search STU0005 (English)", "cmd": "search STU0005", "lang": "English"},
    {"label": "👨‍🏫 Filter Dr. T. Ramesh mentees (English)", "cmd": "show students of Dr. T. Ramesh", "lang": "English"},
    {"label": "🚨 Open daily micro audit (English)", "cmd": "open micro audit", "lang": "English"},
    {"label": "🏆 Open Hall of Fame (English)", "cmd": "open hall of fame", "lang": "English"},
    {"label": "📊 Campus mood telemetry (Tanglish)", "cmd": "campus vibe epdi irukku", "lang": "Tanglish"},
    {"label": "⚠️ ஆபத்தில் உள்ள மாணவர்கள் (Tamil)", "cmd": "ஆபத்தில் உள்ள மாணவர்களைக் காட்டு", "lang": "Tamil"},
    {"label": "🔍 STU0001 ஐத் தேடு (Tamil)", "cmd": "STU0001 ஐத் தேடு", "lang": "Tamil"},
    {"label": "📑 அறிக்கையைப் பதிவிறக்கு (Tamil)", "cmd": "அறிக்கையைப் பதிவிறக்கு", "lang": "Tamil"}
]

def parse_voice_command(command: str):
    """
    Parse a voice/text command across English, Tamil, and Tanglish.
    Returns:
        dict with:
            intent: str (e.g. 'show_at_risk', 'search_student', 'filter_mentor', 'micro_audit', 'campus_vibe', 'hall_of_fame', 'export_report')
            target_value: str or None (e.g. 'STU0005', 'Dr. T. Ramesh')
            response_text: str (human-readable response)
            speech_text: str (text for speech synthesizer)
            target_page: str (suggested page to display)
            lang: str ('English', 'Tamil', 'Tanglish')
    """
    cmd = command.strip().lower()

    # Detect language
    has_tamil = bool(re.search(r'[\u0B80-\u0BFF]', command))

    # 1. Search Student ID or Name
    stu_match = re.search(r'\b(stu\d{4}|2[2-4]cs\d{3})\b', cmd, re.IGNORECASE)
    if stu_match:
        stu_id = stu_match.group(1).upper()
        if has_tamil:
            resp = f"மாணவர் {stu_id} வெற்றிகரமாக கண்டுபிடிக்கப்பட்டார். விவரங்களை இப்போது காட்டுகிறேன்."
        elif any(w in cmd for w in ['thedu', 'pannu', 'kaattu']):
            resp = f"Student {stu_id} kandupidichachu! Opening profile details now."
        else:
            resp = f"Student {stu_id} identified. Opening comprehensive 360° profile now."
        return {
            "intent": "search_student",
            "target_value": stu_id,
            "response_text": resp,
            "speech_text": resp,
            "target_page": "Smart Global Search",
            "lang": "Tamil" if has_tamil else "English"
        }

    # 2. At-Risk Students
    risk_keywords = [
        'at-risk', 'at risk', 'risk', 'struggling', 'danger',
        'ஆபத்தில்', 'ரிஸ்க்',
        'risk student', 'risk students', 'kaattu'
    ]
    if any(k in cmd for k in risk_keywords) and not ('hall of fame' in cmd or 'fame' in cmd):
        if has_tamil:
            resp = "ஆபத்து நிலையில் உள்ள மாணவர்களின் பட்டியல் வடிகட்டப்பட்டு தயாராக உள்ளது."
        elif 'kaattu' in cmd or 'paaru' in cmd:
            resp = "At-risk students list filter panniyachu! Checking failing indicators and interventions."
        else:
            resp = "Filtering cohort to High and Moderate Risk students with failing indicators."
        return {
            "intent": "show_at_risk",
            "target_value": "High",
            "response_text": resp,
            "speech_text": resp,
            "target_page": "AI Success Predictor",
            "lang": "Tamil" if has_tamil else ("Tanglish" if 'kaattu' in cmd else "English")
        }

    # 3. Mentor Mentee Filter
    mentor_names = ["ramesh", "kalaivani", "suresh", "meenakshi", "anand", "priyadarshini"]
    for m in mentor_names:
        if m in cmd:
            full_mentor_map = {
                "ramesh": "Dr. T. Ramesh",
                "kalaivani": "Prof. V. Kalaivani",
                "suresh": "Prof. M. Suresh",
                "meenakshi": "Prof. S. Meenakshi",
                "anand": "Dr. R. Anand",
                "priyadarshini": "Dr. K. Priyadarshini"
            }
            mentor_full = full_mentor_map[m]
            if has_tamil:
                resp = f"{mentor_full} அவர்களின் வழிகாட்டலில் உள்ள மாணவர்கள் தேர்ந்தெடுக்கப்பட்டனர்."
            elif 'kaattu' in cmd or 'mentees' in cmd:
                resp = f"{mentor_full} oda mentees list load aayiduchu! Showing assigned students."
            else:
                resp = f"Filtered view to students assigned to {mentor_full}."
            return {
                "intent": "filter_mentor",
                "target_value": mentor_full,
                "response_text": resp,
                "speech_text": resp,
                "target_page": "Mentor Interventions",
                "lang": "Tamil" if has_tamil else ("Tanglish" if 'mentees' in cmd else "English")
            }

    # 4. Micro Audit
    if any(k in cmd for k in ['audit', 'anomaly', 'anomalies', 'ஆடிட்', 'முரண்பாடு']):
        if has_tamil:
            resp = "தினசரி மைக்ரோ-ஆடிட் இயந்திரம் திறக்கப்பட்டது. சமீபத்திய முரண்பாடுகள் பகுப்பாய்வு செய்யப்படுகின்றன."
        elif 'kaattu' in cmd or 'open pannu' in cmd:
            resp = "Daily micro-audit open panniyachu! Detecting attendance dips and anomalies."
        else:
            resp = "Opening Daily Micro-Audit Engine. Scanning 500 students for attendance and LMS anomalies."
        return {
            "intent": "micro_audit",
            "target_value": None,
            "response_text": resp,
            "speech_text": resp,
            "target_page": "Daily Micro-Audit",
            "lang": "Tamil" if has_tamil else "English"
        }

    # 5. Export Report
    if any(k in cmd for k in ['export', 'report', 'download', 'pdf', 'csv', 'அறிக்கை', 'பதிவிறக்கு']):
        if has_tamil:
            resp = "அறிக்கை தயாரிக்கும் பிரிவு தயாராக உள்ளது. நீங்கள் PDF அல்லது CSV வடிவங்களில் பதிவிறக்கலாம்."
        elif 'download pannu' in cmd:
            resp = "Report download section ready! Voice-to-PDF and CSV options available."
        else:
            resp = "Report generation engine active. Download Department Summary or Student Dossier in PDF/CSV."
        return {
            "intent": "export_report",
            "target_value": None,
            "response_text": resp,
            "speech_text": resp,
            "target_page": "Voice-to-PDF Reports",
            "lang": "Tamil" if has_tamil else "English"
        }

    # 6. Campus Mood / Vibe
    if any(k in cmd for k in ['vibe', 'mood', 'sentiment', 'mental', 'stress', 'மனநிலை', 'epdi irukku']):
        if has_tamil:
            resp = "வளாக மாணவர் திருப்தி விகிதம் 3.8/5 ஆகவும், ஒட்டுமொத்த மகிழ்ச்சி நிலை சீராகவும் உள்ளது."
        elif 'epdi irukku' in cmd or 'vibe' in cmd:
            resp = "Campus vibe super-ah irukku! Average satisfaction 3.8/5, and stress index is well monitored."
        else:
            resp = "Campus vibe index is at 78.4% healthy sentiment. Average student satisfaction is 3.82/5.0."
        return {
            "intent": "campus_vibe",
            "target_value": None,
            "response_text": resp,
            "speech_text": resp,
            "target_page": "Campus Vibe & Chatbot",
            "lang": "Tamil" if has_tamil else "English"
        }

    # 7. Hall of Fame
    if any(k in cmd for k in ['hall of fame', 'fame', 'topper', 'toppers', 'achiever', 'வெற்றியாளர்']):
        if has_tamil:
            resp = "வெற்றியாளர்கள் அரங்கம் திறக்கப்பட்டது! முதலிடம் பிடித்த மாணவர்களின் சாதனைகளை பார்வையிடவும்."
        elif 'kaattu' in cmd:
            resp = "Hall of Fame open panniyachu! Checking top CGPA and coding champions."
        else:
            resp = "Navigating to Public Hall of Fame. Celebrating Top CGPA, Coding Champions, and 100% Attendance stars."
        return {
            "intent": "hall_of_fame",
            "target_value": None,
            "response_text": resp,
            "speech_text": resp,
            "target_page": "Public Hall of Fame",
            "lang": "Tamil" if has_tamil else "English"
        }

    # Fallback General Copilot Response
    if has_tamil:
        resp = f"உங்கள் கட்டளை: '{command}'. டெக்சா உதவியாளர் தயார் நிலையில் உள்ளார்."
    else:
        resp = f"Command recognized: '{command}'. Navigating to AI Copilot insights."

    return {
        "intent": "general_help",
        "target_value": None,
        "response_text": resp,
        "speech_text": resp,
        "target_page": "AI Success Predictor",
        "lang": "Tamil" if has_tamil else "English"
    }
