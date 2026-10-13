import React, { useState, useEffect } from 'react';
import { CalendarCheck, AlertTriangle, MessageSquare, ExternalLink } from 'lucide-react';
import { fetchAttendanceAnalytics } from '../api';

export const AttendanceEngagement: React.FC = () => {
  const [data, setData] = useState<any | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAttendanceAnalytics()
      .then(setData)
      .finally(() => setLoading(false));
  }, []);

  if (loading || !data) {
    return <div style={{ padding: '3rem', textAlign: 'center', color: '#64748B' }}>Loading Attendance Analytics...</div>;
  }

  return (
    <div>
      <div style={{ marginBottom: '1.25rem' }}>
        <h2 style={{ fontSize: '1.25rem', fontWeight: 800, color: '#0F172A', letterSpacing: '-0.02em', margin: 0 }}>
          Institutional Attendance Monitoring & Detention Watch
        </h2>
        <p style={{ fontSize: '0.78rem', color: '#64748B', margin: '2px 0 0 0' }}>
          Real-time tracking of lecture and laboratory attendance with automated detention cutoff warnings (75.0%).
        </p>
      </div>

      {/* KPI Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1rem', marginBottom: '1.5rem' }}>
        <div className="card-elevated" style={{ padding: '1.15rem' }}>
          <div style={{ fontSize: '0.72rem', fontWeight: 700, color: '#64748B', textTransform: 'uppercase' }}>Overall Attendance</div>
          <div style={{ fontSize: '1.75rem', fontWeight: 800, color: '#0F172A', margin: '0.25rem 0' }}>
            {data.overall_mean}%
          </div>
          <div style={{ fontSize: '0.75rem', color: '#64748B' }}>Institutional Average</div>
        </div>

        <div className="card-elevated" style={{ padding: '1.15rem' }}>
          <div style={{ fontSize: '0.72rem', fontWeight: 700, color: '#64748B', textTransform: 'uppercase' }}>Theory Attendance</div>
          <div style={{ fontSize: '1.75rem', fontWeight: 800, color: '#1E40AF', margin: '0.25rem 0' }}>
            {data.theory_mean}%
          </div>
          <div style={{ fontSize: '0.75rem', color: '#64748B' }}>Lectures & Tutorials</div>
        </div>

        <div className="card-elevated" style={{ padding: '1.15rem' }}>
          <div style={{ fontSize: '0.72rem', fontWeight: 700, color: '#64748B', textTransform: 'uppercase' }}>Laboratory Attendance</div>
          <div style={{ fontSize: '1.75rem', fontWeight: 800, color: '#059669', margin: '0.25rem 0' }}>
            {data.lab_mean}%
          </div>
          <div style={{ fontSize: '0.75rem', color: '#64748B' }}>Practical Lab Sessions</div>
        </div>

        <div className="card-elevated" style={{ padding: '1.15rem', borderLeft: '4px solid #DC2626' }}>
          <div style={{ fontSize: '0.72rem', fontWeight: 700, color: '#DC2626', textTransform: 'uppercase' }}>Detention Warning (&lt; 75%)</div>
          <div style={{ fontSize: '1.75rem', fontWeight: 800, color: '#DC2626', margin: '0.25rem 0' }}>
            {data.detention_warning_count}
          </div>
          <div style={{ fontSize: '0.75rem', color: '#64748B' }}>{data.detention_percentage}% of cohort affected</div>
        </div>
      </div>

      {/* Detention Watchlist Table */}
      <div className="card-elevated" style={{ padding: '1.25rem', marginBottom: '1.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
          <div>
            <h3 style={{ fontSize: '0.95rem', fontWeight: 700, color: '#0F172A', margin: 0 }}>
              🚨 Official Detention Watchlist (Overall Attendance &lt; 75.0%)
            </h3>
            <p style={{ fontSize: '0.75rem', color: '#64748B', margin: '2px 0 0 0' }}>
              Students below university semester exam eligibility criteria requiring mandatory mentor counseling.
            </p>
          </div>
        </div>

        <div style={{ overflowX: 'auto' }}>
          <table className="table-dense">
            <thead>
              <tr>
                <th>Student</th>
                <th>Year & Class</th>
                <th>Overall Att %</th>
                <th>Theory Att %</th>
                <th>Lab Att %</th>
                <th>CGPA</th>
                <th>Backlogs</th>
                <th>Assigned Mentor</th>
                <th>Guardian Contact</th>
                <th style={{ textAlign: 'right' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {data.detention_watchlist.map((s: any) => {
                const waMsg = encodeURIComponent(
                  `Respected Guardian, Attendance update for your ward ${s.name} (${s.roll_number}): Current attendance is ${s.attendance_overall_pct}%, which is below the mandatory 75% cutoff. Please contact mentor ${s.faculty_mentor}.`
                );
                return (
                  <tr key={s.student_id}>
                    <td>
                      <div style={{ fontWeight: 700, color: '#0F172A' }}>{s.name}</div>
                      <div style={{ fontSize: '0.7rem', color: '#64748B' }}>{s.student_id} • {s.roll_number}</div>
                    </td>
                    <td>Yr {s.year} {s.section}</td>
                    <td>
                      <b style={{ color: '#DC2626' }}>{s.attendance_overall_pct.toFixed(1)}%</b>
                    </td>
                    <td>{s.attendance_theory_pct.toFixed(1)}%</td>
                    <td>{s.attendance_lab_pct.toFixed(1)}%</td>
                    <td>{s.cgpa.toFixed(2)}</td>
                    <td>
                      <span className={`badge-pill ${s.backlogs > 0 ? 'badge-high' : 'badge-low'}`}>
                        {s.backlogs}
                      </span>
                    </td>
                    <td>{s.faculty_mentor}</td>
                    <td>+91 {s.parent_mobile}</td>
                    <td style={{ textAlign: 'right' }}>
                      <a
                        href={`https://wa.me/91${s.parent_mobile}?text=${waMsg}`}
                        target="_blank"
                        rel="noreferrer"
                        style={{ textDecoration: 'none' }}
                      >
                        <button
                          className="btn-secondary"
                          style={{ padding: '4px 8px', fontSize: '0.74rem', color: '#16A34A', borderColor: '#BBF7D0' }}
                        >
                          <MessageSquare size={13} />
                          <span>WhatsApp</span>
                        </button>
                      </a>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
