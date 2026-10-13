import React, { useState, useEffect } from 'react';
import {
  X,
  Award,
  AlertTriangle,
  GraduationCap,
  CalendarCheck,
  Briefcase,
  FileText,
  User,
  Phone,
  Mail,
  CheckCircle2,
  TrendingDown
} from 'lucide-react';
import { fetchStudentDetail } from '../api';

interface StudentDrawerProps {
  studentId: string | null;
  onClose: () => void;
}

export const StudentDrawer: React.FC<StudentDrawerProps> = ({ studentId, onClose }) => {
  const [data, setData] = useState<any | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!studentId) {
      setData(null);
      return;
    }
    const loadDetail = async () => {
      setLoading(true);
      setError(null);
      try {
        const res = await fetchStudentDetail(studentId);
        setData(res);
      } catch (err: any) {
        setError(err.message || 'Failed to load student details');
      } finally {
        setLoading(false);
      }
    };
    loadDetail();
  }, [studentId]);

  if (!studentId) return null;

  return (
    <div className="drawer-backdrop" onClick={onClose}>
      <div className="drawer-panel" onClick={(e) => e.stopPropagation()}>
        {/* Drawer Header */}
        <div
          style={{
            padding: '1.25rem 1.5rem',
            borderBottom: '1px solid #E2E8F0',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            backgroundColor: '#FFFFFF',
            position: 'sticky',
            top: 0,
            zIndex: 10
          }}
        >
          <div>
            <div style={{ fontSize: '0.72rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.04em', color: '#64748B' }}>
              360° Student Intelligence Profile
            </div>
            <div style={{ fontSize: '1.15rem', fontWeight: 800, color: '#0F172A', letterSpacing: '-0.02em' }}>
              {data ? `${data.student.name} (${data.student.student_id})` : 'Loading student profile...'}
            </div>
          </div>
          <button
            onClick={onClose}
            style={{
              background: '#F1F5F9',
              border: 'none',
              borderRadius: '6px',
              padding: '6px',
              color: '#475569',
              cursor: 'pointer'
            }}
          >
            <X size={18} />
          </button>
        </div>

        {/* Drawer Content */}
        <div style={{ padding: '1.5rem', overflowY: 'auto', flex: '1 1 0%' }}>
          {loading && (
            <div style={{ textAlign: 'center', padding: '3rem 0', color: '#64748B' }}>
              Loading comprehensive student dossier...
            </div>
          )}

          {error && (
            <div style={{ padding: '1rem', backgroundColor: '#FEF2F2', border: '1px solid #FECACA', borderRadius: '8px', color: '#DC2626' }}>
              {error}
            </div>
          )}

          {data && (
            <div>
              {/* Profile Header Card */}
              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '1.25rem',
                  padding: '1.25rem',
                  backgroundColor: '#F8FAFC',
                  border: '1px solid #E2E8F0',
                  borderRadius: '10px',
                  marginBottom: '1.25rem'
                }}
              >
                <img
                  src={data.student.photo_url || `https://api.dicebear.com/7.x/avataaars/svg?seed=${data.student.name}`}
                  alt={data.student.name}
                  style={{
                    width: '64px',
                    height: '64px',
                    borderRadius: '50%',
                    objectFit: 'cover',
                    border: '2px solid #BFDBFE'
                  }}
                />
                <div style={{ flex: 1 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.25rem' }}>
                    <span style={{ fontSize: '1.2rem', fontWeight: 800, color: '#0F172A' }}>{data.student.name}</span>
                    <span
                      className={`badge-pill ${
                        data.student.risk_level === 'High' ? 'badge-high' : data.student.risk_level === 'Medium' ? 'badge-med' : 'badge-low'
                      }`}
                    >
                      {data.student.risk_level} Risk
                    </span>
                  </div>
                  <div style={{ fontSize: '0.78rem', color: '#64748B' }}>
                    Roll: <b>{data.student.roll_number}</b> | Dept: <b>{data.student.department}</b> (Yr {data.student.year} {data.student.section})
                  </div>
                  <div style={{ fontSize: '0.78rem', color: '#334155', marginTop: '0.2rem' }}>
                    Mentor: <b>{data.student.faculty_mentor}</b> | Segment: <b>{data.student.student_segment}</b>
                  </div>
                </div>
              </div>

              {/* Success Score & Breakdown */}
              <div
                style={{
                  backgroundColor: '#FFFFFF',
                  border: '1px solid #E2E8F0',
                  borderRadius: '10px',
                  padding: '1.25rem',
                  marginBottom: '1.25rem'
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
                  <div>
                    <div style={{ fontSize: '0.74rem', textTransform: 'uppercase', color: '#64748B', fontWeight: 700 }}>
                      Student Success Score
                    </div>
                    <div style={{ fontSize: '1.85rem', fontWeight: 800, color: '#1E40AF', letterSpacing: '-0.02em' }}>
                      {data.score_details.total_score.toFixed(1)} <span style={{ fontSize: '0.9rem', color: '#64748B' }}>/ 100</span>
                    </div>
                  </div>
                  <span className="badge-pill badge-brand">Data Completeness: {data.score_details.completeness_pct}%</span>
                </div>

                {/* Categories Breakdown */}
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: '0.5rem', marginBottom: '1rem' }}>
                  <div style={{ backgroundColor: '#F8FAFC', padding: '8px', borderRadius: '6px', textAlign: 'center', border: '1px solid #E2E8F0' }}>
                    <div style={{ fontSize: '0.65rem', color: '#64748B', fontWeight: 700 }}>Academics (35%)</div>
                    <div style={{ fontSize: '0.95rem', fontWeight: 800, color: '#0F172A' }}>
                      {data.score_details.category_scores.academics?.toFixed(1) || '-'}
                    </div>
                  </div>
                  <div style={{ backgroundColor: '#F8FAFC', padding: '8px', borderRadius: '6px', textAlign: 'center', border: '1px solid #E2E8F0' }}>
                    <div style={{ fontSize: '0.65rem', color: '#64748B', fontWeight: 700 }}>Attendance (20%)</div>
                    <div style={{ fontSize: '0.95rem', fontWeight: 800, color: '#0F172A' }}>
                      {data.score_details.category_scores.attendance?.toFixed(1) || '-'}
                    </div>
                  </div>
                  <div style={{ backgroundColor: '#F8FAFC', padding: '8px', borderRadius: '6px', textAlign: 'center', border: '1px solid #E2E8F0' }}>
                    <div style={{ fontSize: '0.65rem', color: '#64748B', fontWeight: 700 }}>LMS (15%)</div>
                    <div style={{ fontSize: '0.95rem', fontWeight: 800, color: '#0F172A' }}>
                      {data.score_details.category_scores.lms_engagement?.toFixed(1) || '-'}
                    </div>
                  </div>
                  <div style={{ backgroundColor: '#F8FAFC', padding: '8px', borderRadius: '6px', textAlign: 'center', border: '1px solid #E2E8F0' }}>
                    <div style={{ fontSize: '0.65rem', color: '#64748B', fontWeight: 700 }}>Placement (20%)</div>
                    <div style={{ fontSize: '0.95rem', fontWeight: 800, color: '#0F172A' }}>
                      {data.score_details.category_scores.placement_readiness?.toFixed(1) || '-'}
                    </div>
                  </div>
                  <div style={{ backgroundColor: '#F8FAFC', padding: '8px', borderRadius: '6px', textAlign: 'center', border: '1px solid #E2E8F0' }}>
                    <div style={{ fontSize: '0.65rem', color: '#64748B', fontWeight: 700 }}>Skills (10%)</div>
                    <div style={{ fontSize: '0.95rem', fontWeight: 800, color: '#0F172A' }}>
                      {data.score_details.category_scores.skills_feedback?.toFixed(1) || '-'}
                    </div>
                  </div>
                </div>

                {/* Positive & Negative Drivers */}
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem', fontSize: '0.78rem' }}>
                  <div style={{ backgroundColor: '#ECFDF5', border: '1px solid #A7F3D0', padding: '8px 10px', borderRadius: '6px' }}>
                    <div style={{ fontWeight: 700, color: '#065F46', marginBottom: '4px' }}>✅ Positive Drivers:</div>
                    {data.score_details.positive_drivers.map((d: string, idx: number) => (
                      <div key={idx} style={{ color: '#047857' }}>• {d}</div>
                    ))}
                  </div>
                  <div style={{ backgroundColor: '#FEF2F2', border: '1px solid #FECACA', padding: '8px 10px', borderRadius: '6px' }}>
                    <div style={{ fontWeight: 700, color: '#991B1B', marginBottom: '4px' }}>⚠️ Risk Drivers:</div>
                    {data.score_details.negative_drivers.map((d: string, idx: number) => (
                      <div key={idx} style={{ color: '#B91C1C' }}>• {d}</div>
                    ))}
                  </div>
                </div>
              </div>

              {/* 360 Competency Radar Comparison */}
              <div
                style={{
                  backgroundColor: '#FFFFFF',
                  border: '1px solid #E2E8F0',
                  borderRadius: '10px',
                  padding: '1.25rem',
                  marginBottom: '1.25rem'
                }}
              >
                <div style={{ fontSize: '0.86rem', fontWeight: 700, color: '#0F172A', marginBottom: '0.75rem' }}>
                  📊 Competency Benchmarking vs Batch Mean
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                  {data.radar_data.map((r: any) => {
                    const diff = r.student - r.batch_average;
                    return (
                      <div key={r.dimension}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.76rem', color: '#334155', marginBottom: '2px' }}>
                          <span>{r.dimension}</span>
                          <span style={{ fontWeight: 700 }}>
                            {r.student} <span style={{ color: '#64748B', fontWeight: 400 }}>(Batch: {r.batch_average})</span>
                            <span style={{ color: diff >= 0 ? '#059669' : '#DC2626', marginLeft: '6px' }}>
                              {diff >= 0 ? `+${diff.toFixed(1)}` : diff.toFixed(1)}
                            </span>
                          </span>
                        </div>
                        <div style={{ width: '100%', height: '5px', backgroundColor: '#F1F5F9', borderRadius: '999px', position: 'relative' }}>
                          <div style={{ width: `${r.student}%`, height: '100%', backgroundColor: '#1E40AF', borderRadius: '999px' }} />
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Root Causes & Prescribed Mitigations */}
              <div
                style={{
                  backgroundColor: '#FFFFFF',
                  border: '1px solid #E2E8F0',
                  borderRadius: '10px',
                  padding: '1.25rem',
                  marginBottom: '1.25rem'
                }}
              >
                <div style={{ fontSize: '0.86rem', fontWeight: 700, color: '#0F172A', marginBottom: '0.75rem' }}>
                  ⚠️ Diagnostic Root Causes & Recommended Actions
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.65rem' }}>
                  {data.root_causes.map((cause: any, idx: number) => (
                    <div
                      key={idx}
                      style={{
                        padding: '0.75rem',
                        backgroundColor: '#F8FAFC',
                        borderLeft: `3px solid ${cause.severity === 'CRITICAL' ? '#DC2626' : cause.severity === 'HIGH' ? '#D97706' : '#2563EB'}`,
                        borderRadius: '0 6px 6px 0',
                        fontSize: '0.78rem'
                      }}
                    >
                      <div style={{ display: 'flex', justifyContent: 'space-between', fontWeight: 700, color: '#0F172A', marginBottom: '2px' }}>
                        <span>{cause.indicator}</span>
                        <span className={`badge-pill ${cause.severity === 'CRITICAL' ? 'badge-high' : 'badge-med'}`}>{cause.severity}</span>
                      </div>
                      <div style={{ color: '#64748B', fontSize: '0.74rem' }}>{cause.description}</div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Action Buttons */}
              <div style={{ display: 'flex', gap: '0.75rem', marginTop: '1rem' }}>
                <a
                  href={`/api/reports/student-pdf/${encodeURIComponent(data.student.student_id)}`}
                  target="_blank"
                  rel="noreferrer"
                  style={{ textDecoration: 'none', flex: 1 }}
                >
                  <button className="btn-primary" style={{ width: '100%', padding: '0.75rem' }}>
                    <FileText size={16} />
                    <span>Download Official PDF Dossier</span>
                  </button>
                </a>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
