import React, { useState, useEffect } from 'react';
import { PieChart, Users, ArrowRight, CheckCircle2, AlertTriangle, Sparkles } from 'lucide-react';
import { fetchSegments } from '../api';
import { SegmentInfo } from '../types';

interface StudentSegmentsProps {
  onSelectStudent: (studentId: string) => void;
}

export const StudentSegments: React.FC<StudentSegmentsProps> = ({ onSelectStudent }) => {
  const [segments, setSegments] = useState<SegmentInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedSegIndex, setSelectedSegIndex] = useState(0);

  useEffect(() => {
    fetchSegments()
      .then(setSegments)
      .finally(() => setLoading(false));
  }, []);

  if (loading || segments.length === 0) {
    return <div style={{ padding: '3rem', textAlign: 'center', color: '#64748B' }}>Loading Data-Driven Cohort Segments...</div>;
  }

  const activeSegment = segments[selectedSegIndex] || segments[0];

  return (
    <div>
      <div style={{ marginBottom: '1.25rem' }}>
        <h2 style={{ fontSize: '1.25rem', fontWeight: 800, color: '#0F172A', letterSpacing: '-0.02em', margin: 0 }}>
          Data-Driven Student Segmentation Engine
        </h2>
        <p style={{ fontSize: '0.78rem', color: '#64748B', margin: '2px 0 0 0' }}>
          Deterministic multi-criteria cohort clustering mapping students to precise remedial and enhancement workflows.
        </p>
      </div>

      {/* Cohort Cards Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '1rem', marginBottom: '1.5rem' }}>
        {segments.map((seg, i) => {
          const isSelected = selectedSegIndex === i;
          const priorityColor =
            seg.priority.toLowerCase().includes('critical') ? '#DC2626' :
            seg.priority.toLowerCase().includes('high') ? '#D97706' :
            seg.priority.toLowerCase().includes('honors') ? '#059669' : '#1E40AF';

          return (
            <div
              key={seg.name}
              onClick={() => setSelectedSegIndex(i)}
              className="card-elevated"
              style={{
                padding: '1.15rem',
                cursor: 'pointer',
                borderColor: isSelected ? '#1E40AF' : '#E2E8F0',
                backgroundColor: isSelected ? '#F8FAFC' : '#FFFFFF',
                boxShadow: isSelected ? '0 4px 14px rgba(30, 64, 175, 0.12)' : undefined,
                borderLeft: `4px solid ${priorityColor}`
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.35rem' }}>
                <span
                  style={{
                    fontSize: '0.68rem',
                    fontWeight: 700,
                    textTransform: 'uppercase',
                    color: priorityColor
                  }}
                >
                  {seg.priority}
                </span>
                <span style={{ fontSize: '0.74rem', color: '#64748B', fontWeight: 700 }}>{seg.percentage}%</span>
              </div>
              <h4 style={{ fontSize: '0.88rem', fontWeight: 700, color: '#0F172A', margin: '0 0 0.25rem 0' }}>{seg.name}</h4>
              <div style={{ fontSize: '1.45rem', fontWeight: 800, color: '#0F172A', margin: '0.2rem 0' }}>
                {seg.count} <span style={{ fontSize: '0.75rem', color: '#64748B', fontWeight: 400 }}>Students</span>
              </div>
              <p style={{ fontSize: '0.73rem', color: '#64748B', margin: 0, lineHeight: 1.4 }}>
                {seg.description.substring(0, 95)}...
              </p>
            </div>
          );
        })}
      </div>

      {/* Selected Segment Roster & Action Plan */}
      <div className="card-elevated" style={{ padding: '1.35rem' }}>
        <div style={{ borderBottom: '1px solid #E2E8F0', paddingBottom: '1rem', marginBottom: '1.25rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '0.5rem' }}>
            <div>
              <span className="badge-pill badge-brand">{activeSegment.priority}</span>
              <h3 style={{ fontSize: '1.15rem', fontWeight: 800, color: '#0F172A', margin: '0.35rem 0 0.25rem 0' }}>
                {activeSegment.name} ({activeSegment.count} Students)
              </h3>
              <p style={{ fontSize: '0.8rem', color: '#475569', margin: 0 }}>{activeSegment.description}</p>
            </div>
          </div>

          <div style={{ marginTop: '0.85rem', backgroundColor: '#EFF6FF', border: '1px solid #BFDBFE', borderRadius: '8px', padding: '0.75rem 1rem' }}>
            <span style={{ fontSize: '0.74rem', fontWeight: 700, textTransform: 'uppercase', color: '#1E40AF' }}>
              Primary Prescribed Institutional Intervention:
            </span>
            <div style={{ fontSize: '0.86rem', fontWeight: 700, color: '#1E3A8A', marginTop: '2px' }}>
              🎯 {activeSegment.primary_intervention}
            </div>
          </div>
        </div>

        {/* Student Roster Table */}
        <div style={{ overflowX: 'auto' }}>
          <table className="table-dense">
            <thead>
              <tr>
                <th>Student</th>
                <th>CGPA</th>
                <th>Attendance %</th>
                <th>Coding Score</th>
                <th>PAT Readiness</th>
                <th>Mentor</th>
                <th style={{ textAlign: 'right' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {activeSegment.students.map((s) => (
                <tr key={s.student_id}>
                  <td>
                    <div style={{ fontWeight: 700, color: '#0F172A' }}>{s.name}</div>
                    <div style={{ fontSize: '0.7rem', color: '#64748B' }}>{s.student_id} • {s.roll_number}</div>
                  </td>
                  <td style={{ fontWeight: 700 }}>{s.cgpa.toFixed(2)}</td>
                  <td>
                    <span style={{ color: s.attendance_overall_pct < 75 ? '#DC2626' : '#059669', fontWeight: 700 }}>
                      {s.attendance_overall_pct.toFixed(1)}%
                    </span>
                  </td>
                  <td>{s.coding_score || '-'}</td>
                  <td>
                    <b style={{ color: '#1E40AF' }}>{s.placement_readiness_score || '-'}</b>
                  </td>
                  <td>{s.faculty_mentor}</td>
                  <td style={{ textAlign: 'right' }}>
                    <button
                      onClick={() => onSelectStudent(s.student_id)}
                      className="btn-secondary"
                      style={{ padding: '4px 8px', fontSize: '0.74rem' }}
                    >
                      Inspect Profile
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
