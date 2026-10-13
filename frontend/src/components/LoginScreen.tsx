import React, { useState } from 'react';
import { Sparkles, Eye, EyeOff, ArrowRight, AlertCircle, ShieldCheck, Database, Award, Activity } from 'lucide-react';
import { loginApi } from '../api';
import { UserProfile } from '../types';

interface LoginScreenProps {
  onLoginSuccess: (user: UserProfile) => void;
}

export const LoginScreen: React.FC<LoginScreenProps> = ({ onLoginSuccess }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleLogin = async (u: string, p: string) => {
    setError(null);
    setLoading(true);
    try {
      const profile = await loginApi(u, p);
      onLoginSuccess(profile);
    } catch (err: any) {
      setError(err.message || 'Authentication failed. Please verify your institutional credentials.');
    } finally {
      setLoading(false);
    }
  };

  const onSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!username.trim()) {
      setError('Please enter your Institutional User ID, Roll Number, or Staff ID.');
      return;
    }
    handleLogin(username, password);
  };

  return (
    <div
      style={{
        minHeight: '100vh',
        backgroundColor: '#F8FAFC',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '2.5rem 1rem'
      }}
    >
      {/* SINGLE-COLUMN VERTICAL CONTAINER */}
      <div style={{ width: '100%', maxWidth: '580px', display: 'flex', flexDirection: 'column' }}>

        {/* 1. TOP SECTION: DEXA BRANDING & INTRODUCTION PANEL */}
        <div
          style={{
            backgroundColor: '#0B132B',
            color: '#FFFFFF',
            borderRadius: '16px',
            padding: '2rem 2.25rem',
            position: 'relative',
            overflow: 'hidden',
            border: '1px solid #1E293B',
            boxShadow: '0 12px 32px rgba(11, 19, 43, 0.25)'
          }}
        >
          {/* Subtle Ambient Radial Glow */}
          <div
            style={{
              position: 'absolute',
              top: '-30%',
              right: '-20%',
              width: '320px',
              height: '320px',
              background: 'radial-gradient(circle, rgba(30,64,175,0.45) 0%, rgba(11,19,43,0) 70%)',
              borderRadius: '50%',
              pointerEvents: 'none'
            }}
          />

          <div style={{ position: 'relative', zIndex: 2 }}>
            {/* Logo Mark & Wordmark */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem', marginBottom: '0.65rem' }}>
              <div
                style={{
                  width: '44px',
                  height: '44px',
                  borderRadius: '12px',
                  backgroundColor: '#1E40AF',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  boxShadow: '0 4px 16px rgba(30,64,175,0.5)',
                  flexShrink: 0
                }}
              >
                <Sparkles size={24} color="#FFFFFF" />
              </div>
              <div>
                <div style={{ fontSize: '1.65rem', fontWeight: 800, letterSpacing: '-0.03em', lineHeight: 1.1, color: '#FFFFFF' }}>
                  DEXA 2.0
                </div>
                <div style={{ fontSize: '0.74rem', textTransform: 'uppercase', letterSpacing: '0.08em', color: '#94A3B8', fontWeight: 700, marginTop: '2px' }}>
                  Dynamic Student Success Intelligence
                </div>
              </div>
            </div>

            {/* Tagline */}
            <div style={{ fontSize: '0.94rem', color: '#60A5FA', fontWeight: 600, marginBottom: '0.65rem' }}>
              Turn student data into timely, explainable action.
            </div>

            {/* Concise Mission Copy */}
            <p style={{ fontSize: '0.82rem', color: '#CBD5E1', lineHeight: 1.5, margin: '0 0 1.25rem 0' }}>
              Enterprise institutional analytics platform for academic leaders, faculty advisors, and students.
              Synthesizes academic grades, attendance trends, LMS engagement, and placement telemetry into transparent early-warning intelligence.
            </p>

            {/* Compact Metric Badges */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '0.6rem' }}>
              <div
                style={{
                  backgroundColor: 'rgba(255,255,255,0.06)',
                  border: '1px solid rgba(255,255,255,0.12)',
                  borderRadius: '8px',
                  padding: '0.55rem 0.65rem',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.45rem'
                }}
              >
                <Database size={15} color="#60A5FA" />
                <div>
                  <div style={{ fontSize: '0.85rem', fontWeight: 700, color: '#FFFFFF', lineHeight: 1.1 }}>500</div>
                  <div style={{ fontSize: '0.64rem', color: '#94A3B8' }}>Verified Students</div>
                </div>
              </div>

              <div
                style={{
                  backgroundColor: 'rgba(255,255,255,0.06)',
                  border: '1px solid rgba(255,255,255,0.12)',
                  borderRadius: '8px',
                  padding: '0.55rem 0.65rem',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.45rem'
                }}
              >
                <Activity size={15} color="#34D399" />
                <div>
                  <div style={{ fontSize: '0.85rem', fontWeight: 700, color: '#FFFFFF', lineHeight: 1.1 }}>96.0%</div>
                  <div style={{ fontSize: '0.64rem', color: '#94A3B8' }}>ML Test Accuracy</div>
                </div>
              </div>

              <div
                style={{
                  backgroundColor: 'rgba(255,255,255,0.06)',
                  border: '1px solid rgba(255,255,255,0.12)',
                  borderRadius: '8px',
                  padding: '0.55rem 0.65rem',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.45rem'
                }}
              >
                <Award size={15} color="#FBBF24" />
                <div>
                  <div style={{ fontSize: '0.85rem', fontWeight: 700, color: '#FFFFFF', lineHeight: 1.1 }}>0–100</div>
                  <div style={{ fontSize: '0.64rem', color: '#94A3B8' }}>Explainable Index</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* 2. SECOND SECTION: INSTITUTIONAL SIGN-IN CARD (BELOW BRANDING) */}
        <div
          style={{
            backgroundColor: '#FFFFFF',
            border: '1px solid #E2E8F0',
            borderRadius: '16px',
            padding: '2rem 2.25rem',
            marginTop: '1.25rem',
            boxShadow: '0 8px 24px rgba(15, 23, 42, 0.06)'
          }}
        >
          {/* Sign In Header */}
          <div style={{ marginBottom: '1.4rem' }}>
            <h2 style={{ fontSize: '1.35rem', fontWeight: 800, color: '#0F172A', letterSpacing: '-0.02em', margin: '0 0 0.25rem 0' }}>
              Institutional Sign In
            </h2>
            <p style={{ fontSize: '0.82rem', color: '#64748B', margin: 0, lineHeight: 1.45 }}>
              Enter your assigned campus credentials. DEXA auto-detects your role (HOD, Mentor, or Student) and scopes departmental telemetry accordingly.
            </p>
          </div>

          {/* Validation / Error Banner */}
          {error && (
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem',
                backgroundColor: '#FEF2F2',
                border: '1px solid #FECACA',
                color: '#DC2626',
                padding: '0.75rem 1rem',
                borderRadius: '8px',
                fontSize: '0.82rem',
                marginBottom: '1.25rem'
              }}
            >
              <AlertCircle size={16} style={{ flexShrink: 0 }} />
              <span>{error}</span>
            </div>
          )}

          {/* Sign In Form */}
          <form onSubmit={onSubmit}>
            {/* User ID Field */}
            <div style={{ marginBottom: '1.15rem' }}>
              <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 700, color: '#334155', marginBottom: '0.35rem', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                Institutional User ID / Roll Number / Staff ID
              </label>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="e.g. admin, STF002, STU0031"
                style={{
                  width: '100%',
                  padding: '0.68rem 0.85rem',
                  borderRadius: '8px',
                  border: '1px solid #CBD5E1',
                  fontSize: '0.9rem',
                  color: '#0F172A',
                  outline: 'none',
                  backgroundColor: '#FFFFFF',
                  boxSizing: 'border-box'
                }}
                disabled={loading}
              />
            </div>

            {/* Password Field */}
            <div style={{ marginBottom: '1.5rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.35rem' }}>
                <label style={{ fontSize: '0.75rem', fontWeight: 700, color: '#334155', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                  Password
                </label>
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  style={{
                    background: 'none',
                    border: 'none',
                    color: '#64748B',
                    cursor: 'pointer',
                    fontSize: '0.75rem',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.25rem',
                    padding: 0
                  }}
                >
                  {showPassword ? <EyeOff size={14} /> : <Eye size={14} />}
                  <span>{showPassword ? 'Hide' : 'Show'}</span>
                </button>
              </div>
              <input
                type={showPassword ? 'text' : 'password'}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter your security password..."
                style={{
                  width: '100%',
                  padding: '0.68rem 0.85rem',
                  borderRadius: '8px',
                  border: '1px solid #CBD5E1',
                  fontSize: '0.9rem',
                  color: '#0F172A',
                  outline: 'none',
                  backgroundColor: '#FFFFFF',
                  boxSizing: 'border-box'
                }}
                disabled={loading}
              />
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading}
              style={{
                width: '100%',
                padding: '0.78rem',
                borderRadius: '8px',
                backgroundColor: '#1E40AF',
                color: '#FFFFFF',
                fontWeight: 700,
                fontSize: '0.92rem',
                border: 'none',
                cursor: loading ? 'not-allowed' : 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '0.5rem',
                boxShadow: '0 2px 10px rgba(30,64,175,0.3)',
                transition: 'background-color 0.15s ease'
              }}
            >
              <span>{loading ? 'Authenticating Credentials...' : 'Sign In to Platform'}</span>
              {!loading && <ArrowRight size={16} />}
            </button>
          </form>

          {/* Quick Demo Sandbox Access */}
          <div style={{ marginTop: '1.75rem', borderTop: '1px solid #E2E8F0', paddingTop: '1.25rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.65rem' }}>
              <span style={{ fontSize: '0.74rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.04em', color: '#475569' }}>
                ⚡ Quick Demo Sandbox Access
              </span>
              <span style={{ fontSize: '0.66rem', backgroundColor: '#EFF6FF', color: '#1E40AF', padding: '2px 8px', borderRadius: '4px', fontWeight: 700 }}>
                1-Click Preset
              </span>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '0.6rem' }}>
              <button
                type="button"
                onClick={() => handleLogin('admin', '123')}
                style={{
                  background: '#F8FAFC',
                  border: '1px solid #CBD5E1',
                  borderRadius: '8px',
                  padding: '0.65rem 0.65rem',
                  textAlign: 'left',
                  cursor: 'pointer'
                }}
              >
                <div style={{ fontSize: '0.78rem', fontWeight: 700, color: '#0F172A' }}>👑 HOD Leadership</div>
                <div style={{ fontSize: '0.68rem', color: '#64748B' }}>Dr. Balasubramanian (`admin` / `123`)</div>
              </button>

              <button
                type="button"
                onClick={() => handleLogin('STF002', '123')}
                style={{
                  background: '#F8FAFC',
                  border: '1px solid #CBD5E1',
                  borderRadius: '8px',
                  padding: '0.65rem 0.65rem',
                  textAlign: 'left',
                  cursor: 'pointer'
                }}
              >
                <div style={{ fontSize: '0.78rem', fontWeight: 700, color: '#0F172A' }}>👨‍🏫 Faculty Mentor</div>
                <div style={{ fontSize: '0.68rem', color: '#64748B' }}>Dr. T. Ramesh (`STF002` / `123`)</div>
              </button>

              <button
                type="button"
                onClick={() => handleLogin('STU0031', '123')}
                style={{
                  background: '#F8FAFC',
                  border: '1px solid #CBD5E1',
                  borderRadius: '8px',
                  padding: '0.65rem 0.65rem',
                  textAlign: 'left',
                  cursor: 'pointer'
                }}
              >
                <div style={{ fontSize: '0.78rem', fontWeight: 700, color: '#0F172A' }}>🎓 High Achiever</div>
                <div style={{ fontSize: '0.68rem', color: '#64748B' }}>Sowmiya V (`STU0031` / `123`)</div>
              </button>

              <button
                type="button"
                onClick={() => handleLogin('STU0005', '123')}
                style={{
                  background: '#F8FAFC',
                  border: '1px solid #FECACA',
                  borderRadius: '8px',
                  padding: '0.65rem 0.65rem',
                  textAlign: 'left',
                  cursor: 'pointer'
                }}
              >
                <div style={{ fontSize: '0.78rem', fontWeight: 700, color: '#DC2626' }}>⚠️ At-Risk Student</div>
                <div style={{ fontSize: '0.68rem', color: '#64748B' }}>Mohan N (`STU0005` / `123`)</div>
              </button>
            </div>
          </div>
        </div>

        {/* Footer Security Badge */}
        <div style={{ textAlign: 'center', marginTop: '1.25rem', fontSize: '0.72rem', color: '#64748B', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.4rem' }}>
          <ShieldCheck size={14} color="#64748B" />
          <span>DEXA 2.0 • Protected by Institutional Role-Based Access Control (RBAC)</span>
        </div>
      </div>
    </div>
  );
};
