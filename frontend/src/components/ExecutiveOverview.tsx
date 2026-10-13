import React, { useState, useEffect } from 'react';
import {
  Users,
  GraduationCap,
  CalendarCheck,
  AlertTriangle,
  Award,
  Database,
  ArrowUpRight,
  Filter,
  CheckCircle2,
  ChevronRight,
  TrendingUp,
  BrainCircuit
} from 'lucide-react';
import { OverviewData } from '../types';
import { fetchOverview } from '../api';

interface ExecutiveOverviewProps {
  selectedYear: string;
  selectedSemester: string;
  onSelectStudent: (studentId: string) => void;
}

export const ExecutiveOverview: React.FC<ExecutiveOverviewProps> = ({
  selectedYear,
  selectedSemester,
  onSelectStudent
}) => {
  const [data, setData] = useState<OverviewData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Local filter states
  const [section, setSection] = useState('all');
  const [riskTier, setRiskTier] = useState('all');
  const [mentor, setMentor] = useState('all');

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetchOverview({
        year: selectedYear,
        semester: selectedSemester,
        section: section,
        risk_tier: riskTier,
        mentor: mentor
      });
      setData(res);
    } catch (err: any) {
      setError(err.message || 'Failed to load executive overview data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [selectedYear, selectedSemester, section, riskTier, mentor]);

  if (loading && !data) {
    return (
      <div style={{ padding: '3rem', textAlign: 'center', color: '#64748B' }}>
        <div style={{ fontSize: '1rem', fontWeight: 600 }}>Loading Executive Overview telemetry...</div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div style={{ padding: '2rem', backgroundColor: '#FEF2F2', border: '1px solid #FECACA', borderRadius: '10px', color: '#DC2626' }}>
        <b>Error:</b> {error || 'No overview data available'}
      </div>
    );
  }

  return (
    <div>
      {/* 1. FILTER CONTROLS BAR */}
      <div
        style={{
          backgroundColor: '#FFFFFF',
          border: '1px solid #E2E8F0',
          borderRadius: '10px',
          padding: '0.85rem 1.25rem',
          marginBottom: '1.5rem',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: '1rem',
          boxShadow: '0 1px 3px rgba(15, 23, 42, 0.02)'
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#0F172A', fontWeight: 700, fontSize: '0.86rem' }}>
          <Filter size={16} color="#1E40AF" />
          <span>Active Analytical Filters</span>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem', flexWrap: 'wrap' }}>
          {/* Section Filter */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', fontSize: '0.8rem' }}>
            <span style={{ color: '#64748B', fontWeight: 600 }}>Section:</span>
            <select
              value={section}
              onChange={(e) => setSection(e.target.value)}
              style={{
                background: '#F8FAFC',
                border: '1px solid #CBD5E1',
                borderRadius: '6px',
                padding: '4px 8px',
                fontSize: '0.8rem',
                color: '#0F172A',
                cursor: 'pointer'
              }}
            >
              <option value="all">All Sections (A, B)</option>
              <option value="A">Section A</option>
              <option value="B">Section B</option>
            </select>
          </div>

          {/* Risk Tier Filter */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', fontSize: '0.8rem' }}>
            <span style={{ color: '#64748B', fontWeight: 600 }}>Risk Tier:</span>
            <select
              value={riskTier}
              onChange={(e) => setRiskTier(e.target.value)}
              style={{
                background: '#F8FAFC',
                border: '1px solid #CBD5E1',
                borderRadius: '6px',
                padding: '4px 8px',
                fontSize: '0.8rem',
                color: '#0F172A',
                cursor: 'pointer'
              }}
            >
              <option value="all">All Risk Tiers</option>
              <option value="high">High Risk Only</option>
              <option value="medium">Medium Risk</option>
              <option value="low">Low Risk</option>
            </select>
          </div>

          {/* Mentor Filter */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', fontSize: '0.8rem' }}>
            <span style={{ color: '#64748B', fontWeight: 600 }}>Mentor:</span>
            <select
              value={mentor}
              onChange={(e) => setMentor(e.target.value)}
              style={{
                background: '#F8FAFC',
                border: '1px solid #CBD5E1',
                borderRadius: '6px',
                padding: '4px 8px',
                fontSize: '0.8rem',
                color: '#0F172A',
                cursor: 'pointer'
              }}
            >
              <option value="all">All Mentors</option>
              <option value="Dr. T. Ramesh">Dr. T. Ramesh</option>
              <option value="Dr. R. Anand">Dr. R. Anand</option>
              <option value="Prof. S. Meenakshi">Prof. S. Meenakshi</option>
              <option value="Dr. N. Balasubramanian">Dr. N. Balasubramanian</option>
            </select>
          </div>
        </div>
      </div>

      {/* 2. EXECUTIVE KPI CARDS GRID */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginBottom: '1.5rem' }}>
        {/* KPI 1 */}
        <div className="card-elevated" style={{ padding: '1.15rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', color: '#64748B', fontSize: '0.72rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.04em' }}>
            <span>Total Students</span>
            <Users size={16} color="#1E40AF" />
          </div>
          <div style={{ fontSize: '1.75rem', fontWeight: 800, color: '#0F172A', margin: '0.35rem 0 0.15rem 0', letterSpacing: '-0.02em' }}>
            {data.total_students}
          </div>
          <div style={{ fontSize: '0.74rem', color: '#64748B' }}>Department of CSE</div>
        </div>

        {/* KPI 2 */}
        <div className="card-elevated" style={{ padding: '1.15rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', color: '#64748B', fontSize: '0.72rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.04em' }}>
            <span>Average CGPA</span>
            <GraduationCap size={16} color="#059669" />
          </div>
          <div style={{ fontSize: '1.75rem', fontWeight: 800, color: '#0F172A', margin: '0.35rem 0 0.15rem 0', letterSpacing: '-0.02em' }}>
            {data.avg_cgpa.toFixed(2)}
          </div>
          <div style={{ fontSize: '0.74rem', color: '#64748B' }}>Scale of 10.00 Max</div>
        </div>

        {/* KPI 3 */}
        <div className="card-elevated" style={{ padding: '1.15rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', color: '#64748B', fontSize: '0.72rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.04em' }}>
            <span>Avg Attendance</span>
            <CalendarCheck size={16} color="#2563EB" />
          </div>
          <div style={{ fontSize: '1.75rem', fontWeight: 800, color: '#0F172A', margin: '0.35rem 0 0.15rem 0', letterSpacing: '-0.02em' }}>
            {data.avg_attendance.toFixed(1)}%
          </div>
          <div style={{ fontSize: '0.74rem', color: '#64748B' }}>75.0% Mandatory Cutoff</div>
        </div>

        {/* KPI 4 */}
        <div className="card-elevated" style={{ padding: '1.15rem', borderLeft: '4px solid #DC2626' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', color: '#DC2626', fontSize: '0.72rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.04em' }}>
            <span>High Risk Flagged</span>
            <AlertTriangle size={16} color="#DC2626" />
          </div>
          <div style={{ fontSize: '1.75rem', fontWeight: 800, color: '#DC2626', margin: '0.35rem 0 0.15rem 0', letterSpacing: '-0.02em' }}>
            {data.high_risk_count}
          </div>
          <div style={{ fontSize: '0.74rem', color: '#64748B' }}>Priority Intervention</div>
        </div>

        {/* KPI 5 */}
        <div className="card-elevated" style={{ padding: '1.15rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', color: '#64748B', fontSize: '0.72rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.04em' }}>
            <span>Success Score</span>
            <Award size={16} color="#D97706" />
          </div>
          <div style={{ fontSize: '1.75rem', fontWeight: 800, color: '#1E40AF', margin: '0.35rem 0 0.15rem 0', letterSpacing: '-0.02em' }}>
            {data.avg_success_score.toFixed(1)}
          </div>
          <div style={{ fontSize: '0.74rem', color: '#64748B' }}>Composite Index (0–100)</div>
        </div>

        {/* KPI 6 */}
        <div className="card-elevated" style={{ padding: '1.15rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', color: '#64748B', fontSize: '0.72rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.04em' }}>
            <span>Data Completeness</span>
            <Database size={16} color="#059669" />
          </div>
          <div style={{ fontSize: '1.75rem', fontWeight: 800, color: '#059669', margin: '0.35rem 0 0.15rem 0', letterSpacing: '-0.02em' }}>
            {data.data_completeness}%
          </div>
          <div style={{ fontSize: '0.74rem', color: '#64748B' }}>5-Category Integration</div>
        </div>
      </div>

      {/* 3. CHARTS ROW */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(460px, 1fr))', gap: '1.25rem', marginBottom: '1.5rem' }}>
        {/* Score Distribution Chart */}
        <div className="card-elevated" style={{ padding: '1.35rem' }}>
          <h3 style={{ fontSize: '0.95rem', fontWeight: 700, color: '#0F172A', marginBottom: '0.25rem' }}>
            Student Success Score Distribution (0–100 Index)
          </h3>
          <p style={{ fontSize: '0.76rem', color: '#64748B', marginBottom: '1rem' }}>
            Transparent weighted aggregation across Academics (35%), Attendance (20%), LMS (15%), Placement (20%), and Skills (10%).
          </p>

          <div style={{ display: 'flex', alignItems: 'flex-end', gap: '0.5rem', height: '180px', paddingTop: '1.5rem' }}>
            {data.score_histogram.map((bar, i) => {
              const maxVal = Math.max(...data.score_histogram.map((b) => b.count), 1);
              const heightPct = (bar.count / maxVal) * 100;
              const color = i < 3 ? '#DC2626' : i < 5 ? '#D97706' : '#059669';
              return (
                <div key={bar.range} style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', height: '100%', justifyContent: 'flex-end' }}>
                  <div style={{ fontSize: '0.7rem', fontWeight: 700, color: '#475569', marginBottom: '4px' }}>{bar.count}</div>
                  <div
                    style={{
                      width: '100%',
                      height: `${Math.max(6, heightPct)}%`,
                      backgroundColor: color,
                      borderRadius: '4px 4px 0 0',
                      transition: 'height 0.3s ease'
                    }}
                    title={`${bar.range}: ${bar.count} students`}
                  />
                  <div style={{ fontSize: '0.66rem', color: '#64748B', marginTop: '6px', textAlign: 'center', whiteSpace: 'nowrap' }}>
                    {bar.range}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Risk Composition Donut / Breakdown */}
        <div className="card-elevated" style={{ padding: '1.35rem' }}>
          <h3 style={{ fontSize: '0.95rem', fontWeight: 700, color: '#0F172A', marginBottom: '0.25rem' }}>
            Institutional Risk Categorization
          </h3>
          <p style={{ fontSize: '0.76rem', color: '#64748B', marginBottom: '1rem' }}>
            Multi-tier population distribution driven by rule-based bands and supervised ML classification.
          </p>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem', marginTop: '1.25rem' }}>
            <div style={{ backgroundColor: '#ECFDF5', border: '1px solid #A7F3D0', borderRadius: '10px', padding: '1.25rem', textAlign: 'center' }}>
              <div style={{ fontSize: '0.74rem', fontWeight: 700, color: '#065F46', textTransform: 'uppercase' }}>Low Risk (≥ 70)</div>
              <div style={{ fontSize: '2rem', fontWeight: 800, color: '#059669', margin: '0.25rem 0' }}>{data.risk_distribution.Low}</div>
              <div style={{ fontSize: '0.75rem', color: '#047857' }}>
                {((data.risk_distribution.Low / Math.max(1, data.total_students)) * 100).toFixed(1)}% of cohort
              </div>
            </div>

            <div style={{ backgroundColor: '#FFFBEB', border: '1px solid #FDE68A', borderRadius: '10px', padding: '1.25rem', textAlign: 'center' }}>
              <div style={{ fontSize: '0.74rem', fontWeight: 700, color: '#92400E', textTransform: 'uppercase' }}>Medium Risk (50–69)</div>
              <div style={{ fontSize: '2rem', fontWeight: 800, color: '#D97706', margin: '0.25rem 0' }}>{data.risk_distribution.Medium}</div>
              <div style={{ fontSize: '0.75rem', color: '#B45309' }}>
                {((data.risk_distribution.Medium / Math.max(1, data.total_students)) * 100).toFixed(1)}% of cohort
              </div>
            </div>

            <div style={{ backgroundColor: '#FEF2F2', border: '1px solid #FECACA', borderRadius: '10px', padding: '1.25rem', textAlign: 'center' }}>
              <div style={{ fontSize: '0.74rem', fontWeight: 700, color: '#991B1B', textTransform: 'uppercase' }}>High Risk (&lt; 50)</div>
              <div style={{ fontSize: '2rem', fontWeight: 800, color: '#DC2626', margin: '0.25rem 0' }}>{data.risk_distribution.High}</div>
              <div style={{ fontSize: '0.75rem', color: '#B91C1C' }}>
                {((data.risk_distribution.High / Math.max(1, data.total_students)) * 100).toFixed(1)}% of cohort
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 4. SUPERVISED MACHINE LEARNING EARLY-WARNING ARCHITECTURE */}
      <div className="card-elevated" style={{ padding: '1.35rem', marginBottom: '1.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.35rem' }}>
          <BrainCircuit size={18} color="#1E40AF" />
          <h3 style={{ fontSize: '1rem', fontWeight: 700, color: '#0F172A' }}>
            Random Forest Supervised Early-Warning Architecture
          </h3>
          <span className="badge-pill badge-brand">KPMG Validated ML</span>
        </div>
        <p style={{ fontSize: '0.78rem', color: '#64748B', marginBottom: '1.25rem' }}>
          Trained on 80/20 stratified holdout partition (400 train, 100 test). Leakage-aware validation with class-balanced weights.
        </p>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1.25rem' }}>
          {/* Validation Metrics Table */}
          <div style={{ backgroundColor: '#F8FAFC', border: '1px solid #E2E8F0', borderRadius: '8px', padding: '1rem' }}>
            <div style={{ fontSize: '0.76rem', fontWeight: 700, color: '#334155', textTransform: 'uppercase', marginBottom: '0.75rem' }}>
              Test Partition Telemetry (N = 100)
            </div>
            <table style={{ width: '100%', fontSize: '0.82rem', borderCollapse: 'collapse' }}>
              <tbody>
                <tr style={{ borderBottom: '1px solid #E2E8F0' }}>
                  <td style={{ padding: '6px 0', color: '#64748B' }}>Testing Accuracy:</td>
                  <td style={{ textAlign: 'right', fontWeight: 700, color: '#059669' }}>{(data.ml_metrics.accuracy * 100).toFixed(2)}%</td>
                </tr>
                <tr style={{ borderBottom: '1px solid #E2E8F0' }}>
                  <td style={{ padding: '6px 0', color: '#64748B' }}>ROC-AUC Metric:</td>
                  <td style={{ textAlign: 'right', fontWeight: 700, color: '#1E40AF' }}>{data.ml_metrics.roc_auc.toFixed(4)}</td>
                </tr>
                <tr style={{ borderBottom: '1px solid #E2E8F0' }}>
                  <td style={{ padding: '6px 0', color: '#64748B' }}>Macro Precision:</td>
                  <td style={{ textAlign: 'right', fontWeight: 700, color: '#0F172A' }}>{(data.ml_metrics.precision * 100).toFixed(2)}%</td>
                </tr>
                <tr style={{ borderBottom: '1px solid #E2E8F0' }}>
                  <td style={{ padding: '6px 0', color: '#64748B' }}>Macro Recall (Sensitivity):</td>
                  <td style={{ textAlign: 'right', fontWeight: 700, color: '#0F172A' }}>{(data.ml_metrics.recall * 100).toFixed(2)}%</td>
                </tr>
                <tr>
                  <td style={{ padding: '6px 0', color: '#64748B' }}>Holdout Split:</td>
                  <td style={{ textAlign: 'right', fontWeight: 700, color: '#0F172A' }}>400 Train / 100 Test</td>
                </tr>
              </tbody>
            </table>
          </div>

          {/* Feature Importances Bar Chart */}
          <div style={{ backgroundColor: '#F8FAFC', border: '1px solid #E2E8F0', borderRadius: '8px', padding: '1rem' }}>
            <div style={{ fontSize: '0.76rem', fontWeight: 700, color: '#334155', textTransform: 'uppercase', marginBottom: '0.75rem' }}>
              Feature Importance Weights (Gini Impurity)
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              {Object.entries(data.ml_metrics.importances).map(([feat, imp]) => {
                const labelMap: Record<string, string> = {
                  cgpa: 'Cumulative GPA (cgpa)',
                  attendance_overall_pct: 'Overall Attendance %',
                  assignment_completion_pct: 'Assignment Completion %',
                  aptitude_score: 'Aptitude Test Score',
                  coding_score: 'Coding Assessment Score',
                  communication_score: 'Communication Score'
                };
                return (
                  <div key={feat}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.74rem', color: '#334155', marginBottom: '2px' }}>
                      <span>{labelMap[feat] || feat}</span>
                      <span style={{ fontWeight: 700 }}>{(imp * 100).toFixed(1)}%</span>
                    </div>
                    <div style={{ width: '100%', height: '6px', backgroundColor: '#E2E8F0', borderRadius: '999px', overflow: 'hidden' }}>
                      <div style={{ width: `${imp * 100 * 2}%`, height: '100%', backgroundColor: '#1E40AF', borderRadius: '999px' }} />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>

      {/* 5. TOP URGENT INTERVENTIONS SUMMARY TABLE */}
      <div className="card-elevated" style={{ padding: '1.35rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
          <div>
            <h3 style={{ fontSize: '0.95rem', fontWeight: 700, color: '#0F172A', margin: 0 }}>
              Students Requiring Urgent Review
            </h3>
            <p style={{ fontSize: '0.76rem', color: '#64748B', margin: '2px 0 0 0' }}>
              Multi-criteria urgency queue prioritizing detention risks, backlogs, and performance declines.
            </p>
          </div>
        </div>

        <div style={{ overflowX: 'auto' }}>
          <table className="table-dense">
            <thead>
              <tr>
                <th>Student</th>
                <th>Year & Class</th>
                <th>CGPA</th>
                <th>Attendance</th>
                <th>Backlogs</th>
                <th>Assigned Mentor</th>
                <th>Primary Action</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {data.top_urgent.map((s) => (
                <tr key={s.student_id}>
                  <td>
                    <div style={{ fontWeight: 700, color: '#0F172A' }}>{s.name}</div>
                    <div style={{ fontSize: '0.7rem', color: '#64748B' }}>{s.student_id} • {s.roll_number}</div>
                  </td>
                  <td>Yr {s.year} {s.section}</td>
                  <td style={{ fontWeight: 700 }}>{s.cgpa.toFixed(2)}</td>
                  <td>
                    <span style={{ color: s.attendance_pct < 75 ? '#DC2626' : '#059669', fontWeight: 700 }}>
                      {s.attendance_pct.toFixed(1)}%
                    </span>
                  </td>
                  <td>
                    <span className={`badge-pill ${s.backlogs > 0 ? 'badge-high' : 'badge-low'}`}>
                      {s.backlogs} Backlogs
                    </span>
                  </td>
                  <td>{s.faculty_mentor}</td>
                  <td style={{ maxWidth: '240px', color: '#334155', fontSize: '0.76rem' }}>
                    {s.recommended_action}
                  </td>
                  <td>
                    <button
                      onClick={() => onSelectStudent(s.student_id)}
                      className="btn-secondary"
                      style={{ padding: '4px 8px', fontSize: '0.75rem' }}
                    >
                      Inspect Dossier
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
