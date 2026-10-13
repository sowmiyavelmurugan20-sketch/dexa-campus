import { UserProfile, OverviewData, Student, Intervention, SegmentInfo, StaffMember } from './types';

const API_BASE = '/api';

export async function loginApi(username: string, password: string): Promise<UserProfile> {
  const res = await fetch(`${API_BASE}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password })
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Authentication failed' }));
    throw new Error(err.detail || 'Invalid credentials');
  }
  return res.json();
}

export async function fetchOverview(filters: {
  year?: string;
  semester?: string;
  section?: string;
  risk_tier?: string;
  mentor?: string;
}): Promise<OverviewData> {
  const params = new URLSearchParams();
  if (filters.year) params.append('year', filters.year);
  if (filters.semester) params.append('semester', filters.semester);
  if (filters.section) params.append('section', filters.section);
  if (filters.risk_tier) params.append('risk_tier', filters.risk_tier);
  if (filters.mentor) params.append('mentor', filters.mentor);

  const res = await fetch(`${API_BASE}/overview?${params.toString()}`);
  if (!res.ok) throw new Error('Failed to fetch executive overview data');
  return res.json();
}

export async function fetchStudents(params: {
  search?: string;
  year?: string;
  section?: string;
  risk_tier?: string;
  mentor?: string;
  segment?: string;
  page?: number;
  limit?: number;
  sort_by?: string;
  sort_desc?: boolean;
}): Promise<{
  page: number;
  limit: number;
  total_records: number;
  total_pages: number;
  students: Student[];
}> {
  const q = new URLSearchParams();
  if (params.search) q.append('search', params.search);
  if (params.year) q.append('year', params.year);
  if (params.section) q.append('section', params.section);
  if (params.risk_tier) q.append('risk_tier', params.risk_tier);
  if (params.mentor) q.append('mentor', params.mentor);
  if (params.segment) q.append('segment', params.segment);
  if (params.page) q.append('page', params.page.toString());
  if (params.limit) q.append('limit', params.limit.toString());
  if (params.sort_by) q.append('sort_by', params.sort_by);
  if (params.sort_desc !== undefined) q.append('sort_desc', params.sort_desc.toString());

  const res = await fetch(`${API_BASE}/students?${q.toString()}`);
  if (!res.ok) throw new Error('Failed to fetch student records');
  return res.json();
}

export async function fetchStudentDetail(studentId: string): Promise<any> {
  const res = await fetch(`${API_BASE}/students/${encodeURIComponent(studentId)}`);
  if (!res.ok) throw new Error('Failed to fetch student details');
  return res.json();
}

export async function simulateRecoveryApi(studentId: string, payload: {
  delta_attendance: number;
  delta_assignment: number;
  delta_coding: number;
  delta_aptitude: number;
}): Promise<any> {
  const res = await fetch(`${API_BASE}/students/${encodeURIComponent(studentId)}/simulate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  if (!res.ok) throw new Error('Failed to run simulation');
  return res.json();
}

export async function fetchInterventions(status?: string): Promise<{ total: number; interventions: Intervention[] }> {
  const params = status ? `?status=${encodeURIComponent(status)}` : '';
  const res = await fetch(`${API_BASE}/interventions${params}`);
  if (!res.ok) throw new Error('Failed to fetch interventions');
  return res.json();
}

export async function createInterventionApi(data: {
  student_id: string;
  category: string;
  notes: string;
  follow_up_date: string;
  status: string;
}): Promise<any> {
  const res = await fetch(`${API_BASE}/interventions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
  if (!res.ok) throw new Error('Failed to log intervention');
  return res.json();
}

export async function fetchSegments(): Promise<SegmentInfo[]> {
  const res = await fetch(`${API_BASE}/segments`);
  if (!res.ok) throw new Error('Failed to fetch student segments');
  return res.json();
}

export async function fetchAcademicAnalytics(): Promise<any> {
  const res = await fetch(`${API_BASE}/academic-analytics`);
  if (!res.ok) throw new Error('Failed to fetch academic analytics');
  return res.json();
}

export async function fetchAttendanceAnalytics(): Promise<any> {
  const res = await fetch(`${API_BASE}/attendance-analytics`);
  if (!res.ok) throw new Error('Failed to fetch attendance analytics');
  return res.json();
}

export async function fetchPlacementAnalytics(): Promise<any> {
  const res = await fetch(`${API_BASE}/placement-analytics`);
  if (!res.ok) throw new Error('Failed to fetch placement analytics');
  return res.json();
}

export async function fetchStaffDirectory(): Promise<StaffMember[]> {
  const res = await fetch(`${API_BASE}/staff`);
  if (!res.ok) throw new Error('Failed to fetch faculty directory');
  return res.json();
}

export async function fetchSettings(): Promise<{ custom_weights: any; default_weights: any }> {
  const res = await fetch(`${API_BASE}/settings`);
  if (!res.ok) throw new Error('Failed to fetch settings');
  return res.json();
}

export async function updateWeightsApi(weights: {
  academics: number;
  attendance: number;
  lms_engagement: number;
  placement_readiness: number;
  skills_feedback: number;
}): Promise<any> {
  const res = await fetch(`${API_BASE}/settings/weights`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(weights)
  });
  if (!res.ok) throw new Error('Failed to update weights');
  return res.json();
}

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export interface ChatResponse {
  role: string;
  content: string;
  configured: boolean;
  model_used?: string | null;
  error?: string | null;
}

export async function fetchChatStatus(): Promise<{
  configured: boolean;
  sdk: string;
  preferred_model: string;
  fallback_model: string;
  api_key_set: boolean;
  status_message: string;
}> {
  const res = await fetch(`${API_BASE}/chat/status`);
  if (!res.ok) throw new Error('Failed to fetch Gemini status');
  return res.json();
}

export async function sendChatQuery(
  message: string,
  mode: 'vibe' | 'study',
  history: ChatMessage[] = [],
  role?: string,
  userId?: string
): Promise<ChatResponse> {
  const res = await fetch(`${API_BASE}/chat/query`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, mode, history, role, user_id: userId })
  });
  if (!res.ok) throw new Error('Failed to send chat message');
  return res.json();
}


export async function postGrievanceApi(data: { category: string; urgency: string; comment: string }): Promise<any> {
  const res = await fetch(`${API_BASE}/grievances`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
  if (!res.ok) throw new Error('Failed to submit grievance');
  return res.json();
}
