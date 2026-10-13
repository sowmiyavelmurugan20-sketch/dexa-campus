"""
DEXA Custom Styles - Clean Light-Only Professional University ERP Portal Design System
(No Sidebars, Top Horizontal Navigation, Pure Light Institutional Theme)
"""

CUSTOM_CSS = """
<style>
/* Import Clean Professional Fonts */
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

/* Force Light Theme Variables */
:root {
    --bg-main: #F8FAFC;
    --bg-card: #FFFFFF;
    --bg-hover: #F1F5F9;
    --border-subtle: #E2E8F0;
    --border-strong: #CBD5E1;
    --brand-primary: #1E40AF;       /* Enterprise Royal Blue */
    --brand-secondary: #0284C7;     /* Sky Cyan */
    --brand-accent: #4F46E5;        /* Indigo */
    --text-primary: #0F172A;
    --text-secondary: #334155;
    --text-muted: #64748B;
    
    --risk-low: #059669;
    --risk-low-bg: #ECFDF5;
    --risk-low-border: #A7F3D0;
    
    --risk-medium: #D97706;
    --risk-medium-bg: #FFFBEB;
    --risk-medium-border: #FDE68A;
    
    --risk-high: #DC2626;
    --risk-high-bg: #FEF2F2;
    --risk-high-border: #FECACA;
}

/* Hide Sidebar Entirely */
section[data-testid="stSidebar"],
div[data-testid="collapsedControl"] {
    display: none !important;
}

/* Force Light Theme across Streamlit */
html, body, [class*="css"], .stApp {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
    color: var(--text-primary) !important;
    background-color: var(--bg-main) !important;
}

/* Streamlit Header Bar Adjustment (Prevent Cut-out) */
header[data-testid="stHeader"] {
    background: transparent !important;
    height: 0px !important;
}

/* Main Container - Zero Top Cutout */
.block-container {
    padding-top: 1rem !important;
    padding-bottom: 5rem !important;
    max-width: 98% !important;
}

/* Institutional Top Navigation Bar */
.erp-top-header {
    background: #FFFFFF;
    border: 1px solid var(--border-subtle);
    border-radius: 12px;
    padding: 0.85rem 1.25rem;
    margin-bottom: 0.75rem;
    box-shadow: 0 2px 6px rgba(15, 23, 42, 0.03);
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 0.75rem;
}

.erp-brand-title {
    font-size: 1.35rem;
    font-weight: 800;
    color: #1E3A8A;
    letter-spacing: -0.02em;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.erp-brand-subtitle {
    font-size: 0.76rem;
    color: #64748B;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.04em;
}

/* Institutional Cards */
.dexa-card {
    background: #FFFFFF !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: 12px !important;
    padding: 1.15rem 1.35rem !important;
    box-shadow: 0 2px 6px rgba(15, 23, 42, 0.02), 0 1px 3px rgba(15, 23, 42, 0.02) !important;
    margin-bottom: 1rem !important;
    transition: all 0.15s ease-in-out !important;
}
.dexa-card:hover {
    border-color: var(--border-strong) !important;
    box-shadow: 0 6px 16px rgba(15, 23, 42, 0.05) !important;
}

/* KPI Metric Cards */
.kpi-container {
    background: #FFFFFF !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: 10px !important;
    padding: 0.85rem 1rem !important;
    text-align: left !important;
    box-shadow: 0 1px 3px rgba(15, 23, 42, 0.02) !important;
    transition: transform 0.12s ease !important;
}
.kpi-container:hover {
    transform: translateY(-2px) !important;
    border-color: #93C5FD !important;
    box-shadow: 0 4px 12px rgba(30, 58, 138, 0.06) !important;
}
.kpi-label {
    font-size: 0.72rem !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
    color: var(--text-muted) !important;
    margin-bottom: 0.25rem !important;
}
.kpi-value {
    font-size: 1.65rem !important;
    font-weight: 800 !important;
    color: var(--text-primary) !important;
    letter-spacing: -0.02em !important;
}
.kpi-sub {
    font-size: 0.75rem !important;
    color: var(--text-muted) !important;
    font-weight: 500 !important;
}

/* Badges & Pills */
.pill {
    display: inline-flex !important;
    align-items: center !important;
    gap: 0.3rem !important;
    padding: 0.2rem 0.55rem !important;
    border-radius: 9999px !important;
    font-size: 0.72rem !important;
    font-weight: 700 !important;
}
.pill-low {
    background: var(--risk-low-bg) !important;
    color: var(--risk-low) !important;
    border: 1px solid var(--risk-low-border) !important;
}
.pill-medium {
    background: var(--risk-medium-bg) !important;
    color: var(--risk-medium) !important;
    border: 1px solid var(--risk-medium-border) !important;
}
.pill-high {
    background: var(--risk-high-bg) !important;
    color: var(--risk-high) !important;
    border: 1px solid var(--risk-high-border) !important;
}
.pill-brand {
    background: #EFF6FF !important;
    color: #1D4ED8 !important;
    border: 1px solid #BFDBFE !important;
}

/* Student & Staff Profile Avatars */
.student-avatar {
    width: 64px !important;
    height: 64px !important;
    border-radius: 50% !important;
    border: 2px solid #BFDBFE !important;
    background: #F8FAFC !important;
    object-fit: cover !important;
}
.staff-avatar {
    width: 70px !important;
    height: 70px !important;
    border-radius: 10px !important;
    border: 2px solid #BFDBFE !important;
    background: #F8FAFC !important;
    object-fit: cover !important;
}

/* Horizontal Radio / Nav Bar Styling - Zero Black Dots */
div[role="radiogroup"] {
    display: flex !important;
    flex-wrap: wrap !important;
    gap: 8px !important;
    background: #FFFFFF !important;
    padding: 6px !important;
    border-radius: 10px !important;
    border: 1px solid var(--border-subtle) !important;
    margin-bottom: 1rem !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.02) !important;
}
div[role="radiogroup"] > label {
    background: #F8FAFC !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: 8px !important;
    padding: 8px 16px !important;
    cursor: pointer !important;
    transition: all 0.15s ease !important;
    margin-right: 0 !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
}
/* Eliminate any radio circles, dots, SVGs or checkmarks inside the pill label */
div[role="radiogroup"] label div:first-child:not([data-testid="stMarkdownContainer"]),
div[role="radiogroup"] label input[type="radio"],
div[role="radiogroup"] label svg {
    display: none !important;
    width: 0 !important;
    height: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
}
div[role="radiogroup"] > label:hover {
    background: #EFF6FF !important;
    border-color: #93C5FD !important;
}
div[role="radiogroup"] > label[data-checked="true"],
div[role="radiogroup"] > label:has(input:checked) {
    background: #1E40AF !important;
    border-color: #1E40AF !important;
    box-shadow: 0 2px 6px rgba(30, 64, 175, 0.2) !important;
}
div[role="radiogroup"] > label:has(input:checked) span,
div[role="radiogroup"] > label:has(input:checked) div,
div[role="radiogroup"] > label:has(input:checked) p {
    color: #FFFFFF !important;
    font-weight: 700 !important;
}

/* Streamlit Inputs with Strong Contrast & Visible Placeholders */
div[data-baseweb="select"] > div,
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stNumberInput > div > div > input {
    background-color: #FFFFFF !important;
    border-color: var(--border-strong) !important;
    color: var(--text-primary) !important;
    border-radius: 8px !important;
    font-size: 0.9rem !important;
}
input::placeholder,
textarea::placeholder {
    color: #64748B !important;
    opacity: 1 !important;
    font-size: 0.88rem !important;
}

/* Filter Bar Container */
.filter-bar-container {
    background: #FFFFFF;
    border: 1px solid var(--border-subtle);
    border-radius: 10px;
    padding: 0.75rem 1rem;
    margin-bottom: 1.15rem;
    box-shadow: 0 1px 3px rgba(15, 23, 42, 0.02);
}

/* Primary Button Styling */
button[kind="primary"] {
    background: #1E40AF !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 700 !important;
    box-shadow: 0 2px 6px rgba(30, 64, 175, 0.2) !important;
}
button[kind="primary"]:hover {
    background: #1E3A8A !important;
}

/* Streamlit Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 6px !important;
    background-color: #F1F5F9 !important;
    padding: 4px !important;
    border-radius: 10px !important;
    border: 1px solid var(--border-subtle) !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 7px !important;
    font-weight: 600 !important;
    font-size: 0.82rem !important;
    color: var(--text-muted) !important;
    padding: 6px 14px !important;
    border: none !important;
}
.stTabs [aria-selected="true"] {
    background-color: #FFFFFF !important;
    color: #1E40AF !important;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05) !important;
}

/* Login Page Container */
.login-card-container {
    max-width: 480px;
    margin: 1rem auto 2rem auto;
    background: #FFFFFF;
    border: 1px solid var(--border-subtle);
    border-radius: 14px;
    padding: 1.75rem 2rem;
    box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.08), 0 8px 10px -6px rgba(15, 23, 42, 0.04);
    text-align: left;
}

/* "Ask Zoro" Docked Widget */
.ask-zoro-dock {
    position: fixed;
    bottom: 20px;
    right: 25px;
    z-index: 999999;
}
.ask-zoro-btn {
    background: linear-gradient(135deg, #1E40AF 0%, #0284C7 100%);
    color: white;
    padding: 10px 18px;
    border-radius: 9999px;
    box-shadow: 0 6px 20px rgba(30, 64, 175, 0.3);
    font-weight: 700;
    font-size: 0.88rem;
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    cursor: pointer;
    border: none;
}
</style>
"""
