import React, { useState, useEffect } from 'react';
import { Briefcase, Code, CheckCircle, Target, TrendingUp } from 'lucide-react';
import { fetchPlacementAnalytics } from '../api';

export const PlacementIntelligence: React.FC = () => {
  const [data, setData] = useState<any | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchPlacementAnalytics()
      .then(setData)
      .finally(() => setLoading(false));
  }, []);

  if (loading || !data) {
    return <div style={{ padding: '3rem', textAlign: 'center', color: '#64748B' }}>Loading Placement Intelligence...</div>;
  }

  return (
    <div>
      <div style={{ marginBottom: '1.25rem' }}>
        <h2 style={{ fontSize: '1.25rem', fontWeight: 800, color: '#0F172A', letterSpacing: '-0.02em', margin: 0 }}>
          Placement & Training (PAT) Intelligence Hub
        </h2>
        <p style={{ fontSize: '0.78rem', color: '#64748B', margin: '2px 0 0 0' }}>
          Assessment benchmarking across technical coding tests, quantitative aptitude, and mock interviews.
        </p>
      </div>

      {/* KPI Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1rem', marginBottom: '1.5rem' }}>
        <div className="card-elevated" style={{ padding: '1.15rem' }}>
          <div style={{ fontSize: '0.72rem', fontWeight: 700, color: '#64748B', textTransform: 'uppercase' }}>Avg PAT Readiness</div>
          <div style={{ fontSize: '1.75rem', fontWeight: 800, color: '#1E40AF', margin: '0.25rem 0' }}>
            {data.avg_readiness} <span style={{ fontSize: '0.85rem', color: '#64748B' }}>/ 100</span>
          </div>
          <div style={{ fontSize: '0.75rem', color: '#64748B' }}>Composite Index</div>
        </div>

        <div className="card-elevated" style={{ padding: '1.15rem' }}>
          <div style={{ fontSize: '0.72rem', fontWeight: 700, color: '#64748B', textTransform: 'uppercase' }}>Avg Coding Assessment</div>
          <div style={{ fontSize: '1.75rem', fontWeight: 800, color: '#0F172A', margin: '0.25rem 0' }}>
            {data.avg_coding} <span style={{ fontSize: '0.85rem', color: '#64748B' }}>/ 100</span>
          </div>
          <div style={{ fontSize: '0.75rem', color: '#64748B' }}>Data Structures & Algorithms</div>
        </div>

        <div className="card-elevated" style={{ padding: '1.15rem' }}>
          <div style={{ fontSize: '0.72rem', fontWeight: 700, color: '#64748B', textTransform: 'uppercase' }}>Avg Aptitude Score</div>
          <div style={{ fontSize: '1.75rem', fontWeight: 800, color: '#059669', margin: '0.25rem 0' }}>
            {data.avg_aptitude} <span style={{ fontSize: '0.85rem', color: '#64748B' }}>/ 100</span>
          </div>
          <div style={{ fontSize: '0.75rem', color: '#64748B' }}>Quantitative & Analytical</div>
        </div>

        <div className="card-elevated" style={{ padding: '1.15rem' }}>
          <div style={{ fontSize: '0.72rem', fontWeight: 700, color: '#64748B', textTransform: 'uppercase' }}>Mock Interview Rating</div>
          <div style={{ fontSize: '1.75rem', fontWeight: 800, color: '#D97706', margin: '0.25rem 0' }}>
            {data.avg_mock_interview} <span style={{ fontSize: '0.85rem', color: '#64748B' }}>/ 100</span>
          </div>
          <div style={{ fontSize: '0.75rem', color: '#64748B' }}>Faculty Panel Evaluation</div>
        </div>
      </div>

      {/* Breakdown Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(460px, 1fr))', gap: '1.25rem' }}>
        <div className="card-elevated" style={{ padding: '1.25rem' }}>
          <h3 style={{ fontSize: '0.92rem', fontWeight: 700, color: '#0F172A', marginBottom: '1rem' }}>
            Placement Status Cohort Distribution
          </h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '0.75rem' }}>
            {Object.entries(data.status_breakdown).map(([status, count]: [string, any]) => (
              <div
                key={status}
                style={{
                  padding: '1rem',
                  backgroundColor: '#F8FAFC',
                  borderRadius: '8px',
                  border: '1px solid #E2E8F0',
                  textAlign: 'center'
                }}
              >
                <div style={{ fontSize: '0.72rem', fontWeight: 700, color: '#64748B', textTransform: 'uppercase' }}>{status}</div>
                <div style={{ fontSize: '1.5rem', fontWeight: 800, color: '#0F172A', margin: '0.25rem 0' }}>{count}</div>
                <div style={{ fontSize: '0.72rem', color: '#64748B' }}>Students</div>
              </div>
            ))}
          </div>
        </div>

        <div className="card-elevated" style={{ padding: '1.25rem' }}>
          <h3 style={{ fontSize: '0.92rem', fontWeight: 700, color: '#0F172A', marginBottom: '0.5rem' }}>
            Skill Gap Telemetry & Bootcamps
          </h3>
          <p style={{ fontSize: '0.76rem', color: '#64748B', marginBottom: '1rem' }}>
            Targeted training cohorts identified for immediate remediation prior to campus recruitment drives.
          </p>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.65rem' }}>
            <div style={{ padding: '0.75rem', backgroundColor: '#FEF2F2', borderLeft: '3px solid #DC2626', borderRadius: '0 6px 6px 0' }}>
              <div style={{ fontWeight: 700, color: '#991B1B', fontSize: '0.82rem' }}>
                Technical Coding Deficit ({data.technical_gap_count} Students)
              </div>
              <div style={{ fontSize: '0.74rem', color: '#B91C1C' }}>
                Coding assessment score below 50. Prescribed Action: Fast-track Data Structures & LeetCode sprint.
              </div>
            </div>

            <div style={{ padding: '0.75rem', backgroundColor: '#ECFDF5', borderLeft: '3px solid #059669', borderRadius: '0 6px 6px 0' }}>
              <div style={{ fontWeight: 700, color: '#065F46', fontSize: '0.82rem' }}>
                Placement Ready Cohort ({data.placement_ready_count} Students)
              </div>
              <div style={{ fontSize: '0.74rem', color: '#047857' }}>
                Composite PAT readiness score ≥ 70. Recommended Action: Tier-1 product track mock interviews.
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
