import React, { useState, useEffect } from 'react';
import { FileText, Download, Sliders, Upload, CheckCircle2, AlertCircle, Save } from 'lucide-react';
import { fetchSettings, updateWeightsApi } from '../api';

export const ReportsSettings: React.FC = () => {
  const [weights, setWeights] = useState({
    academics: 0.35,
    attendance: 0.20,
    lms_engagement: 0.15,
    placement_readiness: 0.20,
    skills_feedback: 0.10
  });
  const [loading, setLoading] = useState(true);
  const [savedSuccess, setSavedSuccess] = useState(false);
  const [studentIdInput, setStudentIdInput] = useState('STU0031');

  useEffect(() => {
    fetchSettings()
      .then((res) => {
        if (res.custom_weights) setWeights(res.custom_weights);
      })
      .finally(() => setLoading(false));
  }, []);

  const handleSaveWeights = async () => {
    try {
      await updateWeightsApi(weights);
      setSavedSuccess(true);
      setTimeout(() => setSavedSuccess(false), 2500);
    } catch (err) {
      console.error(err);
    }
  };

  const totalSum = Math.round(
    (weights.academics + weights.attendance + weights.lms_engagement + weights.placement_readiness + weights.skills_feedback) * 100
  );

  return (
    <div>
      <div style={{ marginBottom: '1.25rem' }}>
        <h2 style={{ fontSize: '1.25rem', fontWeight: 800, color: '#0F172A', letterSpacing: '-0.02em', margin: 0 }}>
          Reports, Data Ingestion & Scoring Configuration
        </h2>
        <p style={{ fontSize: '0.78rem', color: '#64748B', margin: '2px 0 0 0' }}>
          Official ReportLab PDF generation, dataset exports, and multi-criteria success score weight customization.
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(460px, 1fr))', gap: '1.25rem', marginBottom: '1.5rem' }}>
        {/* PDF & Data Exports */}
        <div className="card-elevated" style={{ padding: '1.35rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.35rem' }}>
            <FileText size={18} color="#1E40AF" />
            <h3 style={{ fontSize: '0.95rem', fontWeight: 700, color: '#0F172A', margin: 0 }}>
              Institutional Document Exports (PDF & CSV)
            </h3>
          </div>
          <p style={{ fontSize: '0.76rem', color: '#64748B', marginBottom: '1.25rem' }}>
            Official printable documentation generated on the fly via ReportLab server engine.
          </p>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
            <div style={{ padding: '1rem', backgroundColor: '#F8FAFC', border: '1px solid #E2E8F0', borderRadius: '8px' }}>
              <div style={{ fontWeight: 700, fontSize: '0.86rem', color: '#0F172A', marginBottom: '2px' }}>
                🏛️ Department Executive Brief (PDF)
              </div>
              <p style={{ fontSize: '0.76rem', color: '#64748B', marginBottom: '0.65rem' }}>
                Official summary report including institutional KPIs, risk distribution, and detention watch rosters.
              </p>
              <a href="/api/reports/department-pdf" download style={{ textDecoration: 'none' }}>
                <button className="btn-primary" style={{ padding: '0.5rem 1rem', fontSize: '0.8rem' }}>
                  <Download size={14} />
                  <span>Download Executive Brief (PDF)</span>
                </button>
              </a>
            </div>

            <div style={{ padding: '1rem', backgroundColor: '#F8FAFC', border: '1px solid #E2E8F0', borderRadius: '8px' }}>
              <div style={{ fontWeight: 700, fontSize: '0.86rem', color: '#0F172A', marginBottom: '2px' }}>
                👤 Individual Student Dossier (PDF)
              </div>
              <p style={{ fontSize: '0.76rem', color: '#64748B', marginBottom: '0.65rem' }}>
                Printable performance dossier with root causes, radar benchmarking, and remedial prescriptions.
              </p>
              <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                <input
                  type="text"
                  value={studentIdInput}
                  onChange={(e) => setStudentIdInput(e.target.value.toUpperCase())}
                  placeholder="Student ID (e.g. STU0031)"
                  style={{ padding: '0.45rem 0.65rem', borderRadius: '6px', border: '1px solid #CBD5E1', fontSize: '0.8rem', width: '150px' }}
                />
                <a href={`/api/reports/student-pdf/${encodeURIComponent(studentIdInput)}`} download style={{ textDecoration: 'none' }}>
                  <button className="btn-secondary" style={{ padding: '0.5rem 0.85rem', fontSize: '0.8rem' }}>
                    <Download size={14} />
                    <span>Download Dossier</span>
                  </button>
                </a>
              </div>
            </div>

            <div style={{ padding: '1rem', backgroundColor: '#F8FAFC', border: '1px solid #E2E8F0', borderRadius: '8px' }}>
              <div style={{ fontWeight: 700, fontSize: '0.86rem', color: '#0F172A', marginBottom: '2px' }}>
                📊 Export Master Dataset (CSV)
              </div>
              <p style={{ fontSize: '0.76rem', color: '#64748B', marginBottom: '0.65rem' }}>
                Full cohort export containing all 500 records with computed scores and segment tags.
              </p>
              <a href="/api/reports/export-csv" download style={{ textDecoration: 'none' }}>
                <button className="btn-secondary" style={{ padding: '0.5rem 1rem', fontSize: '0.8rem' }}>
                  <Download size={14} />
                  <span>Export CSV</span>
                </button>
              </a>
            </div>
          </div>
        </div>

        {/* Multi-Criteria Success Score Weight Configuration */}
        <div className="card-elevated" style={{ padding: '1.35rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.35rem' }}>
            <Sliders size={18} color="#1E40AF" />
            <h3 style={{ fontSize: '0.95rem', fontWeight: 700, color: '#0F172A', margin: 0 }}>
              Transparent Success Score Weight Tuning
            </h3>
          </div>
          <p style={{ fontSize: '0.76rem', color: '#64748B', marginBottom: '1.25rem' }}>
            Configure the 0–100 index composition. Weights are normalized automatically across available indicators.
          </p>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', marginBottom: '1.25rem' }}>
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.78rem', color: '#334155', marginBottom: '2px' }}>
                <span>Academics Weight (CGPA, IA marks, Backlogs)</span>
                <b>{Math.round(weights.academics * 100)}%</b>
              </div>
              <input
                type="range"
                min="0.10"
                max="0.50"
                step="0.05"
                value={weights.academics}
                onChange={(e) => setWeights({ ...weights, academics: parseFloat(e.target.value) })}
                style={{ width: '100%' }}
              />
            </div>

            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.78rem', color: '#334155', marginBottom: '2px' }}>
                <span>Attendance Weight (Overall & 30-Day Trend)</span>
                <b>{Math.round(weights.attendance * 100)}%</b>
              </div>
              <input
                type="range"
                min="0.10"
                max="0.40"
                step="0.05"
                value={weights.attendance}
                onChange={(e) => setWeights({ ...weights, attendance: parseFloat(e.target.value) })}
                style={{ width: '100%' }}
              />
            </div>

            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.78rem', color: '#334155', marginBottom: '2px' }}>
                <span>LMS & Engagement Weight (Assignments, Logins)</span>
                <b>{Math.round(weights.lms_engagement * 100)}%</b>
              </div>
              <input
                type="range"
                min="0.05"
                max="0.30"
                step="0.05"
                value={weights.lms_engagement}
                onChange={(e) => setWeights({ ...weights, lms_engagement: parseFloat(e.target.value) })}
                style={{ width: '100%' }}
              />
            </div>

            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.78rem', color: '#334155', marginBottom: '2px' }}>
                <span>Placement Readiness Weight (Coding, Aptitude, PAT)</span>
                <b>{Math.round(weights.placement_readiness * 100)}%</b>
              </div>
              <input
                type="range"
                min="0.10"
                max="0.40"
                step="0.05"
                value={weights.placement_readiness}
                onChange={(e) => setWeights({ ...weights, placement_readiness: parseFloat(e.target.value) })}
                style={{ width: '100%' }}
              />
            </div>

            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.78rem', color: '#334155', marginBottom: '2px' }}>
                <span>Skills & Feedback Weight (Soft skills, Faculty rating)</span>
                <b>{Math.round(weights.skills_feedback * 100)}%</b>
              </div>
              <input
                type="range"
                min="0.05"
                max="0.20"
                step="0.05"
                value={weights.skills_feedback}
                onChange={(e) => setWeights({ ...weights, skills_feedback: parseFloat(e.target.value) })}
                style={{ width: '100%' }}
              />
            </div>
          </div>

          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingTop: '0.75rem', borderTop: '1px solid #E2E8F0' }}>
            <span style={{ fontSize: '0.8rem', color: '#64748B' }}>
              Sum Total: <b style={{ color: totalSum === 100 ? '#059669' : '#D97706' }}>{totalSum}%</b>
            </span>

            <button onClick={handleSaveWeights} className="btn-primary" style={{ padding: '0.5rem 1.15rem' }}>
              <Save size={14} />
              <span>{savedSuccess ? 'Weights Recalculated!' : 'Apply & Recalculate'}</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
