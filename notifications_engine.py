"""
DEXA Notifications, Interventions & Grievance State Engine
"""

from datetime import datetime, timedelta
import pandas as pd

def init_mock_notifications(df: pd.DataFrame) -> list:
    """
    Generate initial notifications for staff/mentors when high-risk students are detected.
    """
    notifications = []
    high_risk_df = df[df['risk_level'] == 'High'].head(15)

    for i, (_, row) in enumerate(high_risk_df.iterrows()):
        reasons = []
        if row['attendance_overall_pct'] < 75.0:
            reasons.append(f"Attendance critical ({row['attendance_overall_pct']:.1f}%)")
        if row['cgpa'] < 6.0:
            reasons.append(f"CGPA below cutoff ({row['cgpa']:.2f})")
        if row['backlogs'] > 0:
            reasons.append(f"{row['backlogs']} active backlog(s)")

        reason_str = ", ".join(reasons) if reasons else "Multiple composite risk thresholds triggered"

        created_time = (datetime.now() - timedelta(hours=i * 3 + 1)).strftime("%b %d, %H:%M")

        notifications.append({
            "id": f"NOTIF-{row['student_id']}-{100+i}",
            "student_id": row['student_id'],
            "student_name": row['name'],
            "mentor": row['faculty_mentor'],
            "year": row['year'],
            "section": row['section'],
            "cgpa": row['cgpa'],
            "attendance": row['attendance_overall_pct'],
            "backlogs": row['backlogs'],
            "reason": reason_str,
            "status": "Pending Counseling",  # 'Pending Counseling', 'Scheduled', 'Resolved'
            "counseling_date": None,
            "counseling_notes": None,
            "created_at": created_time,
            "severity": "CRITICAL"
        })

    return notifications

def init_mock_grievances() -> list:
    """Pre-seed sample anonymous grievances for Feature 9."""
    return [
        {
            "id": "GFB-A941-2026",
            "category": "Lab Facilities",
            "urgency": "High",
            "sentiment": "Neutral",
            "comment": "GPU computing lab machines in Block C have slow internet connectivity during practical deep learning sessions.",
            "status": "Under Review",
            "upvotes": 24,
            "created_at": "Oct 10, 14:30"
        },
        {
            "id": "GFB-B102-2026",
            "category": "Hostel & Dining",
            "urgency": "Medium",
            "sentiment": "Negative",
            "comment": "Night study room Wi-Fi access in Kaveri Hostel disconnects after midnight. Need 24x7 broadband for hackathon prep.",
            "status": "In Progress",
            "upvotes": 38,
            "created_at": "Oct 11, 09:15"
        },
        {
            "id": "GFB-C884-2026",
            "category": "Academic Support",
            "urgency": "Medium",
            "sentiment": "Positive",
            "comment": "Weekend coding bootcamp conducted by Dr. Ramesh was immensely helpful. Please organize similar tracks for Cloud DevOps.",
            "status": "Resolved",
            "upvotes": 42,
            "created_at": "Oct 09, 17:45"
        }
    ]

def init_mock_interventions(df: pd.DataFrame) -> list:
    """Pre-seed logged interventions for Feature 4."""
    return [
        {
            "id": "INT-001",
            "student_id": "STU0005",
            "student_name": "Mohan Nagarajan",
            "mentor": "Prof. S. Meenakshi",
            "category": "1-on-1 Academic Counseling",
            "notes": "Discussed 7 active backlogs and low attendance (60.5%). Prescribed weekend remedial coaching on IA question banks.",
            "follow_up_date": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
            "status": "In Progress",
            "logged_at": (datetime.now() - timedelta(days=2)).strftime("%b %d, %Y")
        },
        {
            "id": "INT-002",
            "student_id": "STU0009",
            "student_name": "Arun Sekar",
            "mentor": "Prof. S. Meenakshi",
            "category": "Peer Coding Buddy Assigned",
            "notes": "Paired with Hall of Fame coder Sathish Murugan for Data Structures problem sets. Weekly log required.",
            "follow_up_date": (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d"),
            "status": "Active",
            "logged_at": (datetime.now() - timedelta(days=4)).strftime("%b %d, %Y")
        }
    ]
