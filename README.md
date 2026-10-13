# DEXA 2.0 — Dynamic Student Success Intelligence
### Enterprise Institutional Analytics & Real Gemini AI Platform (KPMG Hackathon Edition)

**DEXA 2.0** is an enterprise-grade institutional intelligence and early-warning student success platform designed for academic leadership (HODs, Deans), faculty mentors, and students. Built with an editorial midnight navy and clean working canvas design system, transparent multi-criteria student success scoring, explainable root-cause diagnosis, supervised machine learning risk prediction, and actionable remedial workflows.

---

## 🌟 Key Architecture & Capabilities

### 1. Vertical Single-Column Login Portal
- **Layout:** Centered single-column vertical orientation on both desktop and mobile.
- **Top Branding Section:** Deep Midnight Navy (`#0B132B`) hero card displaying DEXA 2.0 wordmark, product tagline (*"Turn student data into timely, explainable action."*), concise institutional description, and verified telemetry pills (500 Students, 96.0% ML Accuracy, 0–100 Explainable Index).
- **Institutional Sign-In Card (Below Branding):** High-contrast white card (`#FFFFFF`) with User ID and Password fields, Show/Hide password toggle, direct sign-in button, and 1-click sandbox presets for HOD (`admin` / `123`), Faculty Mentor (`STF002` / `123`), and Students (`STU0031` / `STU0005`).

### 2. Real Google Gemini AI Integration (Not Hardcoded Chat)
- **Official SDK:** Built with the official `google-genai` Python SDK (`from google import genai`, v2.29.0).
- **Model Hierarchy:** Primary target `gemini-2.5-flash` with automatic failover to `gemini-1.5-flash`.
- **Zero Predefined Text:** Removed old hardcoded keyword matching (`chatbot_engine.py`). All queries are sent dynamically to Gemini with multi-turn conversation context.
- **Verified Grounding (`analytics_context.py`):** System instructions inject real department figures (500 students, 6.84 mean CGPA, 77.8% attendance, 186 detention alerts, 52 high risk), formula explanations, and student dossiers (`STU0001`, `STU0005`, etc.) without hallucinations.
- **Security & Authorization:** Key is read exclusively from `GEMINI_API_KEY` environment variable or `.env`. Role-based access control restricts student users from accessing peer confidential records.

### 3. Professional Text & Voice Chat Interface (`AskZoroWidget.tsx`)
- **Text Chat:** Multi-turn session history, distinct user/assistant chat bubbles, loading state, error retry button, and clear conversation control.
- **Voice Input (Speech-to-Text):** Integrated microphone button using browser Web Speech Recognition (`SpeechRecognition` / `webkitSpeechRecognition`). Transcribes speech live into editable text in both **English (`en-US`)** and **தமிழ் / Tamil (`ta-IN`)**.
- **Voice Output (Text-to-Speech):** Integrated "Listen" button on every AI response powered by browser speech synthesis (`window.speechSynthesis`) with play, pause, and stop controls.

### 4. Transparent 0–100 Student Success Score
$$\text{Success Score} = \sum_{c \in \text{Categories}} w_c \cdot S_c$$

- **Academics (35%):** CGPA (45%), Current Semester GPA (25%), Internal Assessments (15%), Backlog penalty (-18 pts/arrear, 15%).
- **Attendance (20%):** Overall lecture attendance (70%) + 30-day shock trend (30%).
- **LMS & Engagement (15%):** Assignment completion rate (50%), LMS quiz average (30%), portal logins (20%).
- **Placement Readiness (20%):** Coding benchmark (35%), Quantitative aptitude (25%), Technical competency (20%), Mock interview (20%).
- **Skills & Feedback (10%):** Communication (40%), Problem solving (40%), Faculty feedback (20%).
- *Missing Data Renormalization:* Automatically renormalizes remaining weights proportionally so students without optional records are never unfairly penalized.

### 5. Supervised Machine Learning Telemetry
- **Model:** Supervised Random Forest Classifier (`ml_engine.py`).
- **Validation:** 80/20 held-out test split (400 train, 100 test).
- **Test Metrics:** Testing Accuracy: **96.0%**, ROC-AUC: **0.992**, Macro Precision: **94.8%**, Macro Recall: **95.2%**.
- **Key Features:** `cgpa`, `attendance_overall_pct`, `assignment_completion_pct`, `coding_score`.

---

## 🚀 Quick Launch & Configuration Instructions

### 1. Configure GEMINI_API_KEY on Windows
Obtain a free API key from [Google AI Studio](https://aistudio.google.com/app/apikey).

**Option A — Windows PowerShell:**
```powershell
$env:GEMINI_API_KEY="your_actual_gemini_api_key"
```

**Option B — Windows Command Prompt (CMD):**
```cmd
set GEMINI_API_KEY=your_actual_gemini_api_key
```

**Option C — Local `.env` File (Ignored by Git):**
Copy `.env.example` to `.env`:
```ini
GEMINI_API_KEY=your_actual_gemini_api_key
```

### 2. Launch the Application
Run the unified FastAPI server:
```bash
python server.py
```
Open your browser and navigate to:
```
http://localhost:8501
```

### 3. Rebuild Frontend (Optional, after code changes)
```bash
cd frontend
npm.cmd run build
```

---

## 🔑 Demo Access Credentials

| Role | Username / ID | Password | Persona & Scope |
| :--- | :--- | :--- | :--- |
| **HOD / Admin** | `admin` | `123` | Dr. N. Balasubramanian — Complete departmental oversight (500 students) |
| **Faculty Mentor** | `STF002` | `123` | Dr. T. Ramesh — Scoped to 33 assigned mentees |
| **Top Student** | `STU0031` | `123` | Sowmiya V — Level 7 Tech Vanguard (High Achiever, XP: 2035) |
| **At-Risk Student** | `STU0005` | `123` | Mohan N — High Risk (7 Backlogs, 60.5% Attendance) |

---

## 🧪 Automated Test Suite (25 Tests)

Run the comprehensive test suite:
```bash
python -m unittest test_dexa.py -v
```

**Summary of Verified Tests:**
- `TestDexaAnalyticsContext`: 4 tests (department telemetry, student lookup, invalid lookup, system prompt).
- `TestDexaGeminiService`: 4 tests (student ID regex extraction, AI status telemetry, missing key guidance, invalid key error handling).
- `TestDexaDataEngine`: 6 tests (RBAC authentication for HOD/Mentor/Student, CSV validation, missing columns).
- `TestDexaMLEngine`: 3 tests (Random Forest metrics >= 96%, risk prediction, recovery simulation).
- `TestDexaScoringEngine`: 5 tests (complete score, missing data renormalization, backlog penalty, risk boundaries at 49.9, 50, 69.9, 70).
- `TestDexaSegmentationEngine`: 3 tests (high academic low placement, disengaged, high achiever).

**Result:** `Ran 25 tests in 15.2s - OK`

---

## 📂 File Architecture

```
dexa-campus/
├── server.py                   # FastAPI REST server & SPA static host
├── gemini_service.py           # Official Google GenAI SDK client & multi-turn handler
├── analytics_context.py        # Verified telemetry & grounded system instruction builder
├── chatbot_engine.py           # Zoro dual-mode assistant router
├── data_engine.py              # Data pipeline, schema validation, CSV/Excel import & RBAC
├── scoring_engine.py           # Documented 0-100 Student Success Score & driver engine
├── segmentation_engine.py      # 5-cohort segmentation & prioritized intervention queue
├── ml_engine.py                # Random Forest classifier, root-cause diagnosis, recovery simulator
├── report_engine.py            # ReportLab PDF generator (Department Brief & Student Dossier)
├── copilot_engine.py           # Multilingual voice parser presets
├── notifications_engine.py     # Staff alerts, intervention tracking, anonymous grievances
├── test_dexa.py                # 25-point unit and integration test suite
├── .env.example                # Example configuration template
├── .gitignore                  # Git ignore rules protecting .env and build files
├── frontend/                   # Modern React 18 + TypeScript + Vite frontend
│   ├── src/components/
│   │   ├── LoginScreen.tsx     # Vertical single-column login experience
│   │   ├── AskZoroWidget.tsx   # Text and voice Gemini AI chat interface
│   │   ├── VoiceCopilotModal.tsx # Multilingual voice copilot dialog
│   │   └── ...                 # Other institutional dashboard screens
│   └── dist/                   # Production-compiled assets
├── student_dataset_500-1 (1).csv # Master dataset of 500 engineering students
└── staff_dataset.csv           # Master directory of 15 CSE faculty members
```
