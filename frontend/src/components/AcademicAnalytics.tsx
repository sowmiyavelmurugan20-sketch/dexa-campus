import React, { useState, useEffect } from 'react';
import { GraduationCap, BookOpen, AlertCircle, TrendingUp, BarChart2 } from 'lucide-react';
import { fetchAcademicAnalytics } from '../api';

export const AcademicAnalytics: React.FC = () => {
  const [data, setData] = useState<any | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAcademicAnalytics()
      .then(setData)
      .finally(() => setLoading(false));
  }, []);

  if (loading || !data) {
    return <div style={{ padding: '3rem', textAlign: 'center', color: '#64748B' }}>Loading Academic Analytics...</div>;
  }

  return (
    <div>
      <div style={{ marginBottom: '1.25rem' }}>
        <h2 style={{ fontSize: '1.25rem', fontWeight: 800, color: '#0F172A', letterSpacing: '-0.02em', margin: 0 }}>
          Academic Performance & Continuous Assessment Analytics
        </h2>
        <p style={{ fontSize: '0.78rem', color: '#64748B', margin: '2px 0 0 0' }}>
          Semester GPA distributions, internal assessment benchmarks, and backlog burden across cohorts.
        </p>
      </div>

      {/* KPI Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1rem', marginBottom: '1.5rem' }}>
        <div className="card-elevated" style={{ padding: '1.15rem' }}>
          <div style={{ fontSize: '0.72rem', fontWeight: 700, color: '#64748B', textTransform: 'uppercase' }}>Cohort CGPA Range</div>
          <div style={{ fontSize: '1.75rem', fontWeight: 800, color: '#0F172A', margin: '0.25rem 0' }}>
            {data.cgpa_min} - {data.cgpa_max}
          </div>
          <div style={{ fontSize: '0.75rem', color: '#64748B' }}>Cohort Mean: <b>{data.cgpa_mean}</b></div>
        </div>

        <div className="card-elevated" style={{ padding: '1.15rem', borderLeft: '4px solid #DC2626' }}>
          <div style={{ fontSize: '0.72rem', fontWeight: 700, color: '#DC2626', textTransform: 'uppercase' }}>Total Backlogs Burden</div>
          <div style={{ fontSize: '1.75rem', fontWeight: 800, color: '#DC2626', margin: '0.25rem 0' }}>
            {data.total_backlogs}
          </div>
          <div style={{ fontSize: '0.75rem', color: '#64748B' }}>{data.students_with_backlogs} Students Affected</div>
        </div>

        <div className="card-elevated" style={{ padding: '1.15rem' }}>
          <div style={{ fontSize: '0.72rem', fontWeight: 700, color: '#64748B', textTransform: 'uppercase' }}>Avg IA1 Evaluation</div>
          <div style={{ fontSize: '1.75rem', fontWeight: 800, color: '#1E40AF', margin: '0.25rem 0' }}>
            {data.ia_averages.ia1} <span style={{ fontSize: '0.85rem', color: '#64748B' }}>/ 50</span>
          </div>
          <div style={{ fontSize: '0.75rem', color: '#64748B' }}>IA2: {data.ia_averages.ia2} | IA3: {data.ia_averages.ia3}</div>
        </div>

        <div className="card-elevated" style={{ padding: '1.15rem' }}>
          <div style={{ fontSize: '0.72rem', fontWeight: 700, color: '#64748B', textTransform: 'uppercase' }}>Math Subject Mean</div>
          <div style={{ fontSize: '1.75rem', fontWeight: 800, color: '#059669', margin: '0.25rem 0' }}>
            {data.subject_averages.mathematics} <span style={{ fontSize: '0.85rem', color: '#64748B' }}>/ 100</span>
          </div>
          <div style={{ fontSize: '0.75rem', color: '#64748B' }}>Core 1: {data.subject_averages.core_subject_1}</div>
        </div>
      </div>

      {/* Grid: Year Comparison and Assessment Progression */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(460px, 1fr))', gap: '1.25rem' }}>
        {/* Year Comparison */}
        <div className="card-elevated" style={{ padding: '1.25rem' }}>
          <h3 style={{ fontSize: '0.92rem', fontWeight: 700, color: '#0F172A', marginBottom: '1rem' }}>
            Academic Performance by Year of Study
          </h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
            {data.year_cgpa_distribution.map((yd: any) => (
              <div key={yd.year} style={{ padding: '0.75rem', backgroundColor: '#F8FAFC', borderRadius: '8px', border: '1px solid #E2E8F0' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
                  <span style={{ fontWeight: 700, color: '#0F172A', fontSize: '0.84rem' }}>{yd.year}</span>
                  <span style={{ fontWeight: 800, color: '#1E40AF' }}>{yd.mean_cgpa} CGPA</span>
                </div>
                <div style={{ fontSize: '0.74rem', color: '#64748B', display: 'flex', justifyContent: 'space-between' }}>
                  <span>Cohort: {yd.count} Students</span>
                  <span style={{ color: yd.backlogs > 0 ? '#DC2626' : '#059669', fontWeight: 600 }}>
                    {yd.backlogs} Backlogs Load
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Continuous Internal Assessments */}
        <div className="card-elevated" style={{ padding: '1.25rem' }}>
          <h3 style={{ fontSize: '0.92rem', fontWeight: 700, color: '#0F172A', marginBottom: '1rem' }}>
            Continuous Internal Assessments (IA1, IA2, IA3)
          </h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.78rem', color: '#334155', marginBottom: '4px' }}>
                <span>IA 1 Assessment (Scale 50)</span>
                <b>{data.ia_averages.ia1} / 50</b>
              </div>
              <div style={{ width: '100%', height: '8px', backgroundColor: '#F1F5F9', borderRadius: '999px', overflow: 'hidden' }}>
                <div style={{ width: `${(data.ia_averages.ia1 / 50) * 100}%`, height: '100%', backgroundColor: '#2563EB', borderRadius: '999px' }} />
              </div>
            </div>

            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.78rem', color: '#334155', marginBottom: '4px' }}>
                <span>IA 2 Assessment (Scale 50)</span>
                <b>{data.ia_averages.ia2} / 50</b>
              </div>
              <div style={{ width: '100%', height: '8px', backgroundColor: '#F1F5F9', borderRadius: '999px', overflow: 'hidden' }}>
                <div style={{ width: `${(data.ia_averages.ia2 / 50) * 100}%`, height: '100%', backgroundColor: '#0284C7', borderRadius: '999px' }} />
              </div>
            </div>

            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.78rem', color: '#334155', marginBottom: '4px' }}>
                <span>IA 3 Assessment (Scale 50)</span>
                <b>{data.ia_averages.ia3} / 50</b>
              </div>
              <div style={{ width: '100%', height: '8px', backgroundColor: '#F1F5F9', borderRadius: '999px', overflow: 'hidden' }}>
                <div style={{ width: `${(data.ia_averages.ia3 / 50) * 100}%`, height: '100%', backgroundColor: '#059669', borderRadius: '999px' }} />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
