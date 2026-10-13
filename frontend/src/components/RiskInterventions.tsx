import React, { useState, useEffect } from 'react';
import { AlertTriangle, Plus, Sliders, CheckCircle, Clock, Calendar, ArrowRight, UserCheck } from 'lucide-react';
import { fetchInterventions, createInterventionApi, simulateRecoveryApi, fetchStudents } from '../api';
import { Intervention, Student } from '../types';

interface RiskInterventionsProps {
  onSelectStudent: (studentId: string) => void;
}

export const RiskInterventions: React.FC<RiskInterventionsProps> = ({ onSelectStudent }) => {
  const [interventions, setInterventions] = useState<Intervention[]>([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState('all');

  // Modal State
  const [showModal, setShowModal] = useState(false);
  const [studentIdInput, setStudentIdInput] = useState('');
  const [categoryInput, setCategoryInput] = useState('1-on-1 Academic Counseling');
  const [notesInput, setNotesInput] = useState('');
  const [followUpDateInput, setFollowUpDateInput] = useState(
    new Date(Date.now() + 7 * 86400000).toISOString().split('T')[0]
  );
  const [savingIntervention, setSavingIntervention] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);

  // Simulation State
  const [simStudentId, setSimStudentId] = useState('STU0005');
  const [simAttendance, setSimAttendance] = useState(10);
  const [simAssignment, setSimAssignment] = useState(15);
  const [simCoding, setSimCoding] = useState(15);
  const [simAptitude, setSimAptitude] = useState(10);
  const [simResult, setSimResult] = useState<any | null>(null);

  const loadData = async () => {
    setLoading(true);
    try {
      const res = await fetchInterventions(statusFilter);
      setInterventions(res.interventions);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const runSimulation = async () => {
    try {
      const res = await simulateRecoveryApi(simStudentId, {
        delta_attendance: simAttendance,
        delta_assignment: simAssignment,
        delta_coding: simCoding,
        delta_aptitude: simAptitude
      });
      setSimResult(res);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    loadData();
  }, [statusFilter]);

  useEffect(() => {
    runSimulation();
  }, [simStudentId, simAttendance, simAssignment, simCoding, simAptitude]);

  const handleCreateIntervention = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!studentIdInput.trim()) return;

    setSavingIntervention(true);
    try {
      await createInterventionApi({
        student_id: studentIdInput.trim(),
        category: categoryInput,
        notes: notesInput,
        follow_up_date: followUpDateInput,
        status: 'In Progress'
      });
      setSaveSuccess(true);
      setTimeout(() => {
        setSaveSuccess(false);
        setShowModal(false);
        setNotesInput('');
        loadData();
      }, 1000);
    } catch (err) {
      console.error(err);
    } finally {
      setSavingIntervention(false);
    }
  };

  return (
    <div>
      {/* Title & Actions */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.25rem', flexWrap: 'wrap', gap: '0.75rem' }}>
        <div>
          <h2 style={{ fontSize: '1.25rem', fontWeight: 800, color: '#0F172A', letterSpacing: '-0.02em', margin: 0 }}>
            Risk Management & Proactive Interventions Workbench
          </h2>
          <p style={{ fontSize: '0.78rem', color: '#64748B', margin: '2px 0 0 0' }}>
            Multi-criteria prioritization queue, clinical remedial tracking, and interactive score recovery simulation.
          </p>
        </div>

        <button onClick={() => setShowModal(true)} className="btn-primary" style={{ padding: '0.5rem 0.95rem', fontSize: '0.82rem' }}>
          <Plus size={16} />
          <span>Log New Intervention</span>
        </button>
      </div>

      {/* Grid: Left Queue, Right Recovery Simulator */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(460px, 1fr))', gap: '1.25rem', marginBottom: '1.5rem' }}>
        {/* Prioritized Intervention Queue */}
        <div className="card-elevated" style={{ padding: '1.25rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <AlertTriangle size={17} color="#DC2626" />
              <h3 style={{ fontSize: '0.92rem', fontWeight: 700, color: '#0F172A', margin: 0 }}>
                Active Intervention Queue ({interventions.length})
              </h3>
            </div>

            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              style={{ fontSize: '0.76rem', padding: '3px 8px', borderRadius: '6px', border: '1px solid #CBD5E1' }}
            >
              <option value="all">All Statuses</option>
              <option value="In Progress">In Progress</option>
              <option value="Pending Counseling">Pending Counseling</option>
              <option value="Resolved">Resolved</option>
            </select>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.65rem', maxHeight: '480px', overflowY: 'auto' }}>
            {interventions.map((it) => (
              <div
                key={it.id}
                style={{
                  padding: '0.85rem',
                  backgroundColor: '#F8FAFC',
                  border: '1px solid #E2E8F0',
                  borderRadius: '8px',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '0.25rem'
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div style={{ fontWeight: 700, color: '#0F172A', fontSize: '0.84rem' }}>
                    {it.student_name} <span style={{ color: '#1E40AF', fontSize: '0.76rem' }}>({it.student_id})</span>
                  </div>
                  <span className={`badge-pill ${it.status === 'Resolved' ? 'badge-low' : 'badge-med'}`}>
                    {it.status}
                  </span>
                </div>
                <div style={{ fontSize: '0.74rem', color: '#64748B' }}>
                  Category: <b>{it.category}</b> • Mentor: {it.mentor} • Review: <b>{it.follow_up_date}</b>
                </div>
                <div style={{ fontSize: '0.78rem', color: '#334155', marginTop: '2px', lineHeight: 1.4 }}>
                  {it.notes}
                </div>
                <div style={{ marginTop: '4px', textAlign: 'right' }}>
                  <button
                    onClick={() => onSelectStudent(it.student_id)}
                    style={{ background: 'none', border: 'none', color: '#1E40AF', fontSize: '0.72rem', fontWeight: 700, cursor: 'pointer' }}
                  >
                    View Dossier →
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* What-If Score & Risk Recovery Simulator */}
        <div className="card-elevated" style={{ padding: '1.25rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.35rem' }}>
            <Sliders size={17} color="#1E40AF" />
            <h3 style={{ fontSize: '0.92rem', fontWeight: 700, color: '#0F172A', margin: 0 }}>
              Interactive Score & Risk Recovery Simulator
            </h3>
          </div>
          <p style={{ fontSize: '0.75rem', color: '#64748B', marginBottom: '1rem' }}>
            Model projected outcomes based on targeted remedial interventions and behavioral improvements.
          </p>

          <div style={{ marginBottom: '1rem' }}>
            <label style={{ display: 'block', fontSize: '0.74rem', fontWeight: 700, color: '#334155', marginBottom: '4px' }}>
              Target Student Roll / ID:
            </label>
            <input
              type="text"
              value={simStudentId}
              onChange={(e) => setSimStudentId(e.target.value.toUpperCase())}
              placeholder="e.g. STU0005, STU0031"
              style={{ width: '100%', padding: '6px 10px', borderRadius: '6px', border: '1px solid #CBD5E1', fontSize: '0.82rem' }}
            />
          </div>

          {/* Sliders */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', marginBottom: '1.25rem' }}>
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: '#334155', marginBottom: '2px' }}>
                <span>Attendance Gain (+%)</span>
                <b>+{simAttendance}%</b>
              </div>
              <input
                type="range"
                min="0"
                max="30"
                step="2"
                value={simAttendance}
                onChange={(e) => setSimAttendance(Number(e.target.value))}
                style={{ width: '100%' }}
              />
            </div>

            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: '#334155', marginBottom: '2px' }}>
                <span>Assignment Completion Gain (+%)</span>
                <b>+{simAssignment}%</b>
              </div>
              <input
                type="range"
                min="0"
                max="40"
                step="5"
                value={simAssignment}
                onChange={(e) => setSimAssignment(Number(e.target.value))}
                style={{ width: '100%' }}
              />
            </div>

            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: '#334155', marginBottom: '2px' }}>
                <span>Coding Assessment Gain (+pts)</span>
                <b>+{simCoding} pts</b>
              </div>
              <input
                type="range"
                min="0"
                max="40"
                step="5"
                value={simCoding}
                onChange={(e) => setSimCoding(Number(e.target.value))}
                style={{ width: '100%' }}
              />
            </div>

            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: '#334155', marginBottom: '2px' }}>
                <span>Aptitude Assessment Gain (+pts)</span>
                <b>+{simAptitude} pts</b>
              </div>
              <input
                type="range"
                min="0"
                max="40"
                step="5"
                value={simAptitude}
                onChange={(e) => setSimAptitude(Number(e.target.value))}
                style={{ width: '100%' }}
              />
            </div>
          </div>

          {/* Projected Recovery Outcome Card */}
          {simResult && (
            <div
              style={{
                backgroundColor: '#F0FDF4',
                border: '1px solid #BBF7D0',
                borderRadius: '8px',
                padding: '1rem',
                fontSize: '0.8rem',
                color: '#065F46'
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.35rem' }}>
                <span className="badge-pill badge-low">Projected Recovery Outcome</span>
                <span style={{ fontWeight: 800 }}>-{(simResult.prob_drop * 100).toFixed(1)}% Risk Drop</span>
              </div>
              <div style={{ fontSize: '0.84rem', lineHeight: 1.5, fontWeight: 500 }}>
                {simResult.summary}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* CREATE INTERVENTION MODAL */}
      {showModal && (
        <div className="drawer-backdrop" onClick={() => setShowModal(false)}>
          <div
            onClick={(e) => e.stopPropagation()}
            style={{
              backgroundColor: '#FFFFFF',
              borderRadius: '12px',
              padding: '1.75rem',
              width: '100%',
              maxWidth: '500px',
              margin: 'auto',
              boxShadow: '0 20px 40px rgba(15, 23, 42, 0.15)'
            }}
          >
            <h3 style={{ fontSize: '1.15rem', fontWeight: 800, color: '#0F172A', marginBottom: '0.25rem' }}>
              Log Formal Student Intervention
            </h3>
            <p style={{ fontSize: '0.78rem', color: '#64748B', marginBottom: '1.25rem' }}>
              Record academic counseling, detention warnings, or remedial bootcamps into the official audit trail.
            </p>

            <form onSubmit={handleCreateIntervention}>
              <div style={{ marginBottom: '1rem' }}>
                <label style={{ display: 'block', fontSize: '0.76rem', fontWeight: 700, color: '#334155', marginBottom: '4px' }}>
                  Student ID:
                </label>
                <input
                  type="text"
                  required
                  value={studentIdInput}
                  onChange={(e) => setStudentIdInput(e.target.value.toUpperCase())}
                  placeholder="e.g. STU0005"
                  style={{ width: '100%', padding: '0.5rem', borderRadius: '6px', border: '1px solid #CBD5E1', fontSize: '0.84rem' }}
                />
              </div>

              <div style={{ marginBottom: '1rem' }}>
                <label style={{ display: 'block', fontSize: '0.76rem', fontWeight: 700, color: '#334155', marginBottom: '4px' }}>
                  Intervention Category:
                </label>
                <select
                  value={categoryInput}
                  onChange={(e) => setCategoryInput(e.target.value)}
                  style={{ width: '100%', padding: '0.5rem', borderRadius: '6px', border: '1px solid #CBD5E1', fontSize: '0.84rem' }}
                >
                  <option value="1-on-1 Academic Counseling">1-on-1 Academic Counseling</option>
                  <option value="Attendance Warning & Detention Contract">Attendance Warning & Detention Contract</option>
                  <option value="Fast-Track Arrear Remediation">Fast-Track Arrear Remediation</option>
                  <option value="Coding & Placement Practice Bootcamp">Coding & Placement Practice Bootcamp</option>
                  <option value="Mental Well-being Consultation">Mental Well-being Consultation</option>
                </select>
              </div>

              <div style={{ marginBottom: '1rem' }}>
                <label style={{ display: 'block', fontSize: '0.76rem', fontWeight: 700, color: '#334155', marginBottom: '4px' }}>
                  Follow-up Review Date:
                </label>
                <input
                  type="date"
                  required
                  value={followUpDateInput}
                  onChange={(e) => setFollowUpDateInput(e.target.value)}
                  style={{ width: '100%', padding: '0.5rem', borderRadius: '6px', border: '1px solid #CBD5E1', fontSize: '0.84rem' }}
                />
              </div>

              <div style={{ marginBottom: '1.25rem' }}>
                <label style={{ display: 'block', fontSize: '0.76rem', fontWeight: 700, color: '#334155', marginBottom: '4px' }}>
                  Faculty Counselor Notes:
                </label>
                <textarea
                  required
                  rows={3}
                  value={notesInput}
                  onChange={(e) => setNotesInput(e.target.value)}
                  placeholder="Details of the discussion, agreed recovery plan, and target milestones..."
                  style={{ width: '100%', padding: '0.5rem', borderRadius: '6px', border: '1px solid #CBD5E1', fontSize: '0.84rem' }}
                />
              </div>

              {saveSuccess && (
                <div style={{ color: '#059669', fontSize: '0.8rem', fontWeight: 700, marginBottom: '0.75rem' }}>
                  ✅ Intervention successfully logged!
                </div>
              )}

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.5rem' }}>
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="btn-secondary"
                  style={{ padding: '0.5rem 1rem' }}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={savingIntervention}
                  className="btn-primary"
                  style={{ padding: '0.5rem 1.25rem' }}
                >
                  {savingIntervention ? 'Saving...' : 'Save Intervention'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
