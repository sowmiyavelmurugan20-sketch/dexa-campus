import React, { useState, useEffect } from 'react';
import { BookOpen, Award, Users, Star, CheckCircle } from 'lucide-react';
import { fetchStaffDirectory } from '../api';
import { StaffMember } from '../types';

export const FacultyDirectory: React.FC = () => {
  const [staff, setStaff] = useState<StaffMember[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStaffDirectory()
      .then(setStaff)
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return <div style={{ padding: '3rem', textAlign: 'center', color: '#64748B' }}>Loading Department Faculty Directory...</div>;
  }

  return (
    <div>
      <div style={{ marginBottom: '1.25rem' }}>
        <h2 style={{ fontSize: '1.25rem', fontWeight: 800, color: '#0F172A', letterSpacing: '-0.02em', margin: 0 }}>
          Faculty & Staff Directory (HOD Leadership Oversight)
        </h2>
        <p style={{ fontSize: '0.78rem', color: '#64748B', margin: '2px 0 0 0' }}>
          Overview of all 15 department faculty members from master staff schema with mentoring loads, pass percentages, and appraisal scores.
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(360px, 1fr))', gap: '1rem' }}>
        {staff.map((m) => (
          <div key={m.staff_id} className="card-elevated" style={{ padding: '1.25rem', display: 'flex', gap: '1rem', alignItems: 'flex-start' }}>
            <img
              src={m.photo_url || `https://api.dicebear.com/7.x/avataaars/svg?seed=${m.name}`}
              alt={m.name}
              style={{
                width: '64px',
                height: '64px',
                borderRadius: '10px',
                objectFit: 'cover',
                border: '2px solid #BFDBFE'
              }}
            />

            <div style={{ flex: 1 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '2px' }}>
                <h4 style={{ fontSize: '0.92rem', fontWeight: 700, color: '#0F172A', margin: 0 }}>{m.name}</h4>
                <span className="badge-pill badge-brand">{m.appraisal_category}</span>
              </div>
              <div style={{ fontSize: '0.78rem', color: '#1E40AF', fontWeight: 600 }}>
                {m.designation} • {m.role_in_department}
              </div>
              <div style={{ fontSize: '0.72rem', color: '#64748B', margin: '0.2rem 0' }}>
                ID: <code>{m.staff_id}</code> | Spec: <b>{m.specialization}</b>
              </div>

              <div style={{ fontSize: '0.74rem', color: '#334155', borderTop: '1px solid #F1F5F9', paddingTop: '0.4rem', marginTop: '0.4rem' }}>
                <div>Experience: <b>{m.total_experience_years} yrs</b> • Teaching: <b>{m.total_teaching_hours_per_week} hrs/wk</b></div>
                <div>Mentees: <b>{m.mentees_assigned}</b> • High Risk: <b style={{ color: '#DC2626' }}>{m.mentees_high_risk}</b></div>
                <div>Pass Rate: <b>{m.subject_pass_percentage}%</b> • Rating: <b>{m.student_feedback_rating_5} / 5.0</b></div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
