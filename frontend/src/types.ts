export interface UserProfile {
  authenticated: boolean;
  role: 'HOD / Admin' | 'Staff / Mentor' | 'Student Portal' | 'Class Advisor';
  user_id: string;
  name: string;
  email: string;
  photo_url: string;
  profile?: any;
}

export interface Student {
  student_id: string;
  roll_number: string;
  name: string;
  photo_url?: string;
  department: string;
  year: number;
  section: string;
  cgpa: number;
  current_sem_gpa?: number;
  attendance_overall_pct: number;
  backlogs: number;
  student_success_score: number;
  risk_level: 'Low' | 'Medium' | 'High';
  student_segment: string;
  faculty_mentor: string;
  coding_score?: number;
  aptitude_score?: number;
  placement_readiness_score?: number;
  placement_status?: string;
  parent_name?: string;
  parent_mobile?: string;
  [key: string]: any;
}

export interface ScoreCategoryBreakdown {
  academics?: number;
  attendance?: number;
  lms_engagement?: number;
  placement_readiness?: number;
  skills_feedback?: number;
  [key: string]: number | undefined;
}

export interface ScoreDetails {
  total_score: number;
  risk_tier: 'Low' | 'Medium' | 'High';
  category_scores: ScoreCategoryBreakdown;
  normalized_weights: ScoreCategoryBreakdown;
  completeness_pct: number;
  positive_drivers: string[];
  negative_drivers: string[];
  indicator_values?: Record<string, any>;
}

export interface RootCause {
  indicator: string;
  current: string;
  threshold: string;
  severity: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  description: string;
}

export interface Mitigation {
  type: string;
  title: string;
  action: string;
  impact: string;
}

export interface Intervention {
  id: string;
  student_id: string;
  student_name: string;
  mentor: string;
  category: string;
  notes: string;
  follow_up_date: string;
  status: string;
  logged_at: string;
}

export interface RadarPoint {
  dimension: string;
  student: number;
  batch_average: number;
}

export interface OverviewData {
  total_students: number;
  avg_cgpa: number;
  avg_attendance: number;
  high_risk_count: number;
  avg_success_score: number;
  data_completeness: number;
  risk_distribution: {
    Low: number;
    Medium: number;
    High: number;
  };
  score_histogram: Array<{ range: string; count: number }>;
  attendance_scatter: Array<{
    student_id: string;
    name: string;
    cgpa: number;
    attendance: number;
    risk_level: string;
    backlogs: number;
    mentor: string;
  }>;
  ml_metrics: {
    accuracy: number;
    roc_auc: number;
    precision: number;
    recall: number;
    f1: number;
    train_samples: number;
    test_samples: number;
    importances: Record<string, number>;
  };
  top_urgent: Array<{
    student_id: string;
    roll_number: string;
    name: string;
    year: number;
    section: string;
    risk_level: string;
    urgency_score: number;
    segment: string;
    cgpa: number;
    attendance_pct: number;
    backlogs: number;
    faculty_mentor: string;
    recommended_action: string;
    status: string;
  }>;
}

export interface SegmentInfo {
  name: string;
  count: number;
  percentage: number;
  priority: string;
  description: string;
  primary_intervention: string;
  students: Student[];
}

export interface StaffMember {
  staff_id: string;
  employee_id: string;
  name: string;
  photo_url: string;
  designation: string;
  role_in_department: string;
  specialization: string;
  total_experience_years: number;
  total_teaching_hours_per_week: number;
  mentees_assigned: number;
  mentees_high_risk: number;
  student_feedback_rating_5: number;
  subject_pass_percentage: number;
  appraisal_category: string;
  staff_performance_score: number;
}
