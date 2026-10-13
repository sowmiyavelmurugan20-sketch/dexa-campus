import React, { useState, useEffect } from 'react';
import { Award, Sparkles, Star, TrendingUp, CheckCircle, ShieldCheck } from 'lucide-react';
import { fetchStudentDetail } from '../api';
import { UserProfile } from '../types';

interface StudentGrowthPortalProps {
  user: UserProfile;
}

export const StudentGrowthPortal: React.FC<StudentGrowthPortalProps> = ({ user }) => {
  const [data, setData] = useState<any | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStudentDetail(user.user_id)
      .then(setData)
      .catch(() => {
        // Fallback to STU0031
        fetchStudentDetail('STU0031').then(setData);
      })
      .finally(() => setLoading(false));
  }, [user.user_id]);

  if (loading || !data) {
    return <div style={{ padding: '3rem', textAlign: 'center', color: '#64748B' }}>Loading Personalized Growth Portal...</div>;
  }

  const s = data.student;

  return (
    <div>
      {/* Student Banner */}
      <div
        className="card-elevated"
        style={{
          padding: '1.75rem',
          display: 'flex',
          gap: '1.5rem',
          alignItems: 'center',
          flexWrap: 'wrap',
          marginBottom: '1.5rem',
          backgroundColor: '#FFFFFF',
          borderLeft: '5px solid #1E40AF'
        }}
      >
        <img
          src={s.photo_url || `https://api.dicebear.com/7.x/avataaars/svg?seed=${s.name}`}
          alt={s.name}
          style={{ width: '80px', height: '80px', borderRadius: '50%', objectFit: 'cover', border: '3px solid #BFDBFE' }}
        />

        <div style={{ flex: '1 1 300px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem', marginBottom: '0.25rem', flexWrap: 'wrap' }}>
            <h2 style={{ fontSize: '1.5rem', fontWeight: 800, color: '#0F172A', margin: 0 }}>{s.name}</h2>
            <span className="badge-pill badge-brand">⭐ {s.level_title || 'Level 7: Tech Vanguard'}</span>
            <span className={`badge-pill ${s.risk_level === 'High' ? 'badge-high' : 'badge-low'}`}>{s.risk_level} Standing</span>
          </div>

          <div style={{ fontSize: '0.82rem', color: '#64748B' }}>
            Roll: <b>{s.roll_number}</b> | Dept: <b>{s.department}</b> (Year {s.year} {s.section}) | Mentor: <b>{s.faculty_mentor}</b>
          </div>
        </div>

        <div style={{ textAlign: 'right' }}>
          <div style={{ fontSize: '0.72rem', textTransform: 'uppercase', color: '#64748B', fontWeight: 700 }}>Total Gamified XP</div>
          <div style={{ fontSize: '2.1rem', fontWeight: 800, color: '#D97706', letterSpacing: '-0.02em' }}>
            {s.xp_points || 2840} <span style={{ fontSize: '1rem', color: '#64748B' }}>XP</span>
          </div>
        </div>
      </div>

      {/* Level Progression Progress Bar */}
      <div className="card-elevated" style={{ padding: '1.25rem', marginBottom: '1.5rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.78rem', color: '#64748B', marginBottom: '6px' }}>
          <span>Level Progression Tracker</span>
          <span style={{ fontWeight: 700, color: '#1E40AF' }}>{s.level_progress_pct?.toFixed(1) || '82.5'}% to Next Rank</span>
        </div>
        <div style={{ width: '100%', height: '10px', backgroundColor: '#E2E8F0', borderRadius: '999px', overflow: 'hidden' }}>
          <div style={{ width: `${s.level_progress_pct || 82.5}%`, height: '100%', backgroundColor: '#1E40AF', borderRadius: '999px' }} />
        </div>
      </div>

      {/* Badges Grid */}
      <div className="card-elevated" style={{ padding: '1.25rem' }}>
        <h3 style={{ fontSize: '0.95rem', fontWeight: 700, color: '#0F172A', marginBottom: '1rem' }}>
          🏆 Earned Achievement Badges & Milestones
        </h3>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))', gap: '0.85rem' }}>
          {Array.isArray(s.badges) && s.badges.length > 0 ? (
            s.badges.map((b: any) => (
              <div
                key={b.id}
                style={{
                  padding: '1rem',
                  backgroundColor: b.unlocked ? '#F8FAFC' : '#F1F5F9',
                  border: `1px solid ${b.unlocked ? '#CBD5E1' : '#E2E8F0'}`,
                  borderRadius: '10px',
                  textAlign: 'center',
                  opacity: b.unlocked ? 1 : 0.45
                }}
              >
                <div style={{ fontSize: '1.8rem', marginBottom: '4px' }}>{b.icon}</div>
                <div style={{ fontWeight: 700, fontSize: '0.78rem', color: '#0F172A' }}>{b.title}</div>
                <div style={{ fontSize: '0.68rem', color: '#64748B' }}>{b.desc}</div>
              </div>
            ))
          ) : (
            <div style={{ color: '#64748B' }}>No badges recorded yet.</div>
          )}
        </div>
      </div>
    </div>
  );
};
