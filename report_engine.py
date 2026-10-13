"""
DEXA Report Engine - Generate Institutional & Student Performance Reports (PDF / CSV)
"""

import io
from datetime import datetime
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def generate_department_pdf(df: pd.DataFrame, mentor_filter: str = None) -> bytes:
    """Generate high-fidelity Department Executive Summary PDF."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#0F172A'),
        spaceAfter=4
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#475569'),
        spaceAfter=15
    )
    section_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#1E293B'),
        spaceBefore=12,
        spaceAfter=6
    )
    table_cell = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor('#0F172A')
    )
    table_header = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.white
    )

    story = []

    # Title & Subtitle
    report_title = "DEXA Campus Analytics — Institutional Executive Brief"
    if mentor_filter and mentor_filter != "All Mentors":
        report_title += f" ({mentor_filter})"

    story.append(Paragraph(report_title, title_style))
    story.append(Paragraph(
        f"Generated on {datetime.now().strftime('%B %d, %Y - %H:%M')} | Department of Computer Science & Engineering",
        subtitle_style
    ))

    # Subset if filtered
    data = df if (not mentor_filter or mentor_filter == "All Mentors") else df[df['faculty_mentor'] == mentor_filter]

    # 1. Executive KPIs Table
    total_count = len(data)
    avg_cgpa = data['cgpa'].mean()
    avg_att = data['attendance_overall_pct'].mean()
    avg_success = data['student_success_score'].mean()
    high_risk_count = (data['risk_level'] == 'High').sum()
    med_risk_count = (data['risk_level'] == 'Medium').sum()
    low_risk_count = (data['risk_level'] == 'Low').sum()

    kpi_data = [
        [
            Paragraph("Total Students", table_header),
            Paragraph("Avg CGPA", table_header),
            Paragraph("Avg Attendance", table_header),
            Paragraph("Avg Success Score", table_header),
            Paragraph("High Risk Flagged", table_header)
        ],
        [
            Paragraph(f"<b>{total_count}</b>", table_cell),
            Paragraph(f"<b>{avg_cgpa:.2f}</b> / 10", table_cell),
            Paragraph(f"<b>{avg_att:.1f}%</b>", table_cell),
            Paragraph(f"<b>{avg_success:.1f}</b> / 100", table_cell),
            Paragraph(f"<b><font color='#DC2626'>{high_risk_count} Students</font></b>", table_cell)
        ]
    ]
    kpi_table = Table(kpi_data, colWidths=[105, 105, 110, 110, 110])
    kpi_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E293B')),
        ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#F8FAFC')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(kpi_table)
    story.append(Spacer(1, 14))

    # 2. Risk Distribution Breakdown
    story.append(Paragraph("Institutional Risk Distribution", section_style))
    risk_summary_data = [
        [Paragraph("Risk Tier", table_header), Paragraph("Count", table_header), Paragraph("Percentage", table_header), Paragraph("Protocol Status", table_header)],
        [Paragraph("<font color='#16A34A'><b>Low Risk (Safe)</b></font>", table_cell), Paragraph(f"{low_risk_count}", table_cell), Paragraph(f"{(low_risk_count/total_count*100):.1f}%", table_cell), Paragraph("Standard Academic Track", table_cell)],
        [Paragraph("<font color='#D97706'><b>Medium Risk (Moderate)</b></font>", table_cell), Paragraph(f"{med_risk_count}", table_cell), Paragraph(f"{(med_risk_count/total_count*100):.1f}%", table_cell), Paragraph("Targeted Remedial Support", table_cell)],
        [Paragraph("<font color='#DC2626'><b>High Risk (Critical)</b></font>", table_cell), Paragraph(f"{high_risk_count}", table_cell), Paragraph(f"{(high_risk_count/total_count*100):.1f}%", table_cell), Paragraph("Immediate Mentor Intervention", table_cell)]
    ]
    risk_table = Table(risk_summary_data, colWidths=[140, 90, 100, 210])
    risk_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#334155')),
        ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#F0FDF4')),
        ('BACKGROUND', (0, 2), (-1, 2), colors.HexColor('#FFFBEB')),
        ('BACKGROUND', (0, 3), (-1, 3), colors.HexColor('#FEF2F2')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(risk_table)
    story.append(Spacer(1, 14))

    # 3. High Risk Priority Action Cohort
    story.append(Paragraph("Critical Priority Cohort (Requiring Immediate Intervention)", section_style))
    high_risk_df = data[data['risk_level'] == 'High'].head(12)

    if not high_risk_df.empty:
        cohort_data = [[
            Paragraph("ID", table_header),
            Paragraph("Name", table_header),
            Paragraph("Year / Sec", table_header),
            Paragraph("CGPA", table_header),
            Paragraph("Att %", table_header),
            Paragraph("Backlogs", table_header),
            Paragraph("Mentor", table_header)
        ]]
        for _, r in high_risk_df.iterrows():
            cohort_data.append([
                Paragraph(str(r['student_id']), table_cell),
                Paragraph(str(r['name'])[:18], table_cell),
                Paragraph(f"Yr {r['year']} - {r['section']}", table_cell),
                Paragraph(f"{r['cgpa']:.2f}", table_cell),
                Paragraph(f"{r['attendance_overall_pct']:.1f}%", table_cell),
                Paragraph(f"<font color='#DC2626'><b>{r['backlogs']}</b></font>", table_cell),
                Paragraph(str(r['faculty_mentor'])[:18], table_cell)
            ])
        cohort_table = Table(cohort_data, colWidths=[65, 120, 65, 55, 55, 60, 120])
        cohort_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#475569')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')]),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#CBD5E1')),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(cohort_table)
    else:
        story.append(Paragraph("<i>No students currently flagged in High Risk category.</i>", subtitle_style))

    story.append(Spacer(1, 20))
    story.append(Paragraph(
        "Confidential document generated by DEXA — Dynamic Student Success Copilot. For internal faculty and leadership review only.",
        ParagraphStyle('Footer', parent=styles['Normal'], fontName='Helvetica-Oblique', fontSize=7.5, textColor=colors.HexColor('#94A3B8'))
    ))

    doc.build(story)
    return buffer.getvalue()

def generate_student_pdf(student_row, root_causes: list, mitigations: list) -> bytes:
    """Generate individual Comprehensive Student Performance & Intervention Dossier PDF."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#0F172A'),
        spaceAfter=2
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor('#475569'),
        spaceAfter=12
    )
    section_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=colors.HexColor('#1E293B'),
        spaceBefore=10,
        spaceAfter=4
    )
    table_cell = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor('#0F172A')
    )
    table_header = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.white
    )

    story = []

    # Student Header
    name = student_row['name']
    stu_id = student_row['student_id']
    roll = student_row['roll_number']
    dept = student_row['department']
    year = student_row['year']
    sec = student_row['section']
    mentor = student_row['faculty_mentor']
    risk = student_row['risk_level']

    story.append(Paragraph(f"DEXA 360° Student Performance Dossier", title_style))
    story.append(Paragraph(
        f"Student ID: <b>{stu_id}</b> | Roll No: <b>{roll}</b> | Name: <b>{name}</b> | Dept: {dept} (Year {year}, Sec {sec})",
        subtitle_style
    ))

    # Basic Info Table
    info_data = [
        [Paragraph("Mentor", table_header), Paragraph("Risk Status", table_header), Paragraph("Success Score", table_header), Paragraph("Career Goal", table_header)],
        [
            Paragraph(f"<b>{mentor}</b>", table_cell),
            Paragraph(f"<b>{risk} Risk</b>", table_cell),
            Paragraph(f"<b>{student_row.get('student_success_score', 0):.1f} / 100</b>", table_cell),
            Paragraph(f"{student_row.get('career_goal', 'Engineering')}", table_cell)
        ]
    ]
    info_table = Table(info_data, colWidths=[140, 110, 110, 180])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E293B')),
        ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#F8FAFC')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 10))

    # Academic & Skill Matrix
    story.append(Paragraph("Academic & Competency Breakdown", section_style))
    matrix_data = [
        [Paragraph("Metric", table_header), Paragraph("Score", table_header), Paragraph("Benchmark", table_header), Paragraph("Status", table_header)],
        [Paragraph("Cumulative GPA (CGPA)", table_cell), Paragraph(f"{student_row.get('cgpa', 0):.2f}", table_cell), Paragraph(">= 6.50", table_cell), Paragraph("Satisfactory" if student_row.get('cgpa', 0) >= 6.5 else "<font color='#DC2626'>Deficit</font>", table_cell)],
        [Paragraph("Overall Attendance", table_cell), Paragraph(f"{student_row.get('attendance_overall_pct', 0):.1f}%", table_cell), Paragraph(">= 75.0%", table_cell), Paragraph("Satisfactory" if student_row.get('attendance_overall_pct', 0) >= 75 else "<font color='#DC2626'>Deficit</font>", table_cell)],
        [Paragraph("Active Backlogs", table_cell), Paragraph(f"{student_row.get('backlogs', 0)}", table_cell), Paragraph("0 Arrears", table_cell), Paragraph("Clean" if student_row.get('backlogs', 0) == 0 else "<font color='#DC2626'>Action Needed</font>", table_cell)],
        [Paragraph("Coding Score", table_cell), Paragraph(f"{student_row.get('coding_score', 0):.1f} / 100", table_cell), Paragraph(">= 50.0", table_cell), Paragraph("Proficient" if student_row.get('coding_score', 0) >= 50 else "<font color='#D97706'>Needs Practice</font>", table_cell)],
        [Paragraph("Aptitude Score", table_cell), Paragraph(f"{student_row.get('aptitude_score', 0):.1f} / 100", table_cell), Paragraph(">= 50.0", table_cell), Paragraph("Proficient" if student_row.get('aptitude_score', 0) >= 50 else "<font color='#D97706'>Needs Practice</font>", table_cell)],
        [Paragraph("Communication Score", table_cell), Paragraph(f"{student_row.get('communication_score', 0):.1f} / 100", table_cell), Paragraph(">= 50.0", table_cell), Paragraph("Proficient" if student_row.get('communication_score', 0) >= 50 else "<font color='#D97706'>Needs Practice</font>", table_cell)],
        [Paragraph("Assignment Completion", table_cell), Paragraph(f"{student_row.get('assignment_completion_pct', 0):.1f}%", table_cell), Paragraph(">= 75.0%", table_cell), Paragraph("Consistent" if student_row.get('assignment_completion_pct', 0) >= 75 else "<font color='#D97706'>Lagging</font>", table_cell)]
    ]
    matrix_table = Table(matrix_data, colWidths=[170, 110, 110, 150])
    matrix_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#334155')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')]),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(matrix_table)
    story.append(Spacer(1, 10))

    # Root Cause Diagnostics
    story.append(Paragraph("AI Root Cause Analysis & Triggered Flags", section_style))
    causes_data = [
        [Paragraph("Indicator", table_header), Paragraph("Observed Value", table_header), Paragraph("Severity", table_header), Paragraph("Clinical Finding", table_header)]
    ]
    for c in root_causes:
        sev_color = '#DC2626' if c['severity'] == 'CRITICAL' else ('#D97706' if c['severity'] == 'HIGH' else '#16A34A')
        causes_data.append([
            Paragraph(f"<b>{c['indicator']}</b>", table_cell),
            Paragraph(str(c['current']), table_cell),
            Paragraph(f"<font color='{sev_color}'><b>{c['severity']}</b></font>", table_cell),
            Paragraph(c['description'], table_cell)
        ])
    causes_table = Table(causes_data, colWidths=[130, 90, 80, 240])
    causes_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E293B')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')]),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(causes_table)
    story.append(Spacer(1, 10))

    # Remedial Action Plan
    story.append(Paragraph("Tailored Remedial Action Plan", section_style))
    mitig_data = [
        [Paragraph("Type", table_header), Paragraph("Program Action", table_header), Paragraph("Projected Outcome", table_header)]
    ]
    for m in mitigations:
        mitig_data.append([
            Paragraph(f"<b>{m['type']}</b>", table_cell),
            Paragraph(f"<b>{m['title']}</b>: {m['action']}", table_cell),
            Paragraph(f"<font color='#16A34A'><b>{m['impact']}</b></font>", table_cell)
        ])
    mitig_table = Table(mitig_data, colWidths=[110, 290, 140])
    mitig_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#334155')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')]),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(mitig_table)
    story.append(Spacer(1, 15))

    # Signature Block
    sig_data = [
        [Paragraph(f"Faculty Mentor Signature: __________________<br/>({mentor})", table_cell),
         Paragraph("Head of Department Signature: __________________<br/>(Dr. HOD, Dept. of CSE)", table_cell)]
    ]
    sig_table = Table(sig_data, colWidths=[270, 270])
    sig_table.setStyle(TableStyle([
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))
    story.append(sig_table)

    doc.build(story)
    return buffer.getvalue()
