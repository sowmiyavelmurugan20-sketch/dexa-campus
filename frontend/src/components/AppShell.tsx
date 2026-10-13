import React, { useState } from 'react';
import {
  LayoutDashboard,
  Users,
  AlertTriangle,
  GraduationCap,
  CalendarCheck,
  Briefcase,
  PieChart,
  FileText,
  Sliders,
  LogOut,
  ChevronLeft,
  ChevronRight,
  Bell,
  Sparkles,
  Mic,
  Award,
  BookOpen
} from 'lucide-react';
import { UserProfile } from '../types';

interface AppShellProps {
  user: UserProfile;
  activeTab: string;
  onTabChange: (tabId: string) => void;
  onLogout: () => void;
  onOpenVoiceCopilot: () => void;
  selectedYear: string;
  onYearChange: (y: string) => void;
  selectedSemester: string;
  onSemesterChange: (s: string) => void;
  children: React.ReactNode;
}

export const AppShell: React.FC<AppShellProps> = ({
  user,
  activeTab,
  onTabChange,
  onLogout,
  onOpenVoiceCopilot,
  selectedYear,
  onYearChange,
  selectedSemester,
  onSemesterChange,
  children
}) => {
  const [collapsed, setCollapsed] = useState(false);
  const [showNotifications, setShowNotifications] = useState(false);

  // Define Navigation Items based on user role
  const isStudent = user.role === 'Student Portal';
  const isHOD = user.role === 'HOD / Admin';

  const navItems = isStudent
    ? [
        { id: 'growth-portal', label: 'My Growth Portal', icon: Award },
        { id: 'academic-analytics', label: 'Academics & Attendance', icon: GraduationCap },
        { id: 'interventions', label: 'Diagnostic & Action Plan', icon: AlertTriangle },
        { id: 'reports', label: 'My Official Dossier', icon: FileText }
      ]
    : [
        { id: 'overview', label: 'Executive Overview', icon: LayoutDashboard },
        { id: 'students', label: 'Student Directory', icon: Users },
        { id: 'interventions', label: 'Risk & Interventions', icon: AlertTriangle },
        { id: 'academics', label: 'Academic Analytics', icon: GraduationCap },
        { id: 'attendance', label: 'Attendance & Engagement', icon: CalendarCheck },
        { id: 'placement', label: 'Placement Intelligence', icon: Briefcase },
        { id: 'segments', label: 'Student Segments', icon: PieChart },
        { id: 'reports', label: 'Reports & Exports', icon: FileText },
        ...(isHOD ? [{ id: 'faculty', label: 'Faculty Directory', icon: BookOpen }] : []),
        { id: 'settings', label: 'Settings & Integration', icon: Sliders }
      ];

  return (
    <div style={{ display: 'flex', minHeight: '100vh', backgroundColor: '#F8FAFC' }}>
      {/* 1. PERSISTENT MIDNIGHT NAVY SIDEBAR */}
      <aside
        style={{
          width: collapsed ? '72px' : '260px',
          backgroundColor: '#0B132B',
          color: '#FFFFFF',
          transition: 'width 0.2s cubic-bezier(0.16, 1, 0.3, 1)',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'space-between',
          borderRight: '1px solid #1E293B',
          zIndex: 50,
          position: 'sticky',
          top: 0,
          height: '100vh'
        }}
      >
        {/* Top Branding Section */}
        <div>
          <div
            style={{
              padding: collapsed ? '1.25rem 0.75rem' : '1.25rem 1.25rem',
              borderBottom: '1px solid rgba(255, 255, 255, 0.08)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: collapsed ? 'center' : 'space-between'
            }}
          >
            {!collapsed ? (
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
                <div
                  style={{
                    width: '32px',
                    height: '32px',
                    borderRadius: '8px',
                    backgroundColor: '#1E40AF',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    boxShadow: '0 2px 8px rgba(30, 64, 175, 0.4)'
                  }}
                >
                  <Sparkles size={18} color="#FFFFFF" />
                </div>
                <div>
                  <div style={{ fontSize: '1.15rem', fontWeight: 800, letterSpacing: '-0.02em', color: '#FFFFFF', lineHeight: 1 }}>
                    DEXA 2.0
                  </div>
                  <div style={{ fontSize: '0.65rem', textTransform: 'uppercase', letterSpacing: '0.05em', color: '#94A3B8', fontWeight: 600 }}>
                    Student Intelligence
                  </div>
                </div>
              </div>
            ) : (
              <div
                style={{
                  width: '34px',
                  height: '34px',
                  borderRadius: '8px',
                  backgroundColor: '#1E40AF',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center'
                }}
              >
                <Sparkles size={18} color="#FFFFFF" />
              </div>
            )}

            <button
              onClick={() => setCollapsed(!collapsed)}
              style={{
                background: 'rgba(255,255,255,0.06)',
                border: 'none',
                borderRadius: '6px',
                color: '#94A3B8',
                cursor: 'pointer',
                padding: '4px',
                display: collapsed ? 'none' : 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}
              title={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
            >
              <ChevronLeft size={16} />
            </button>
          </div>

          {/* Navigation Links */}
          <nav style={{ padding: '0.85rem 0.65rem' }}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
              {navItems.map((item) => {
                const Icon = item.icon;
                const isActive = activeTab === item.id;
                return (
                  <button
                    key={item.id}
                    onClick={() => onTabChange(item.id)}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '0.75rem',
                      width: '100%',
                      padding: collapsed ? '0.65rem 0' : '0.65rem 0.85rem',
                      justifyContent: collapsed ? 'center' : 'flex-start',
                      borderRadius: '8px',
                      border: 'none',
                      cursor: 'pointer',
                      fontSize: '0.84rem',
                      fontWeight: isActive ? 700 : 500,
                      backgroundColor: isActive ? '#1E40AF' : 'transparent',
                      color: isActive ? '#FFFFFF' : '#94A3B8',
                      transition: 'all 0.12s ease',
                      boxShadow: isActive ? '0 2px 8px rgba(30, 64, 175, 0.3)' : 'none'
                    }}
                    onMouseOver={(e) => {
                      if (!isActive) {
                        e.currentTarget.style.backgroundColor = 'rgba(255, 255, 255, 0.05)';
                        e.currentTarget.style.color = '#FFFFFF';
                      }
                    }}
                    onMouseOut={(e) => {
                      if (!isActive) {
                        e.currentTarget.style.backgroundColor = 'transparent';
                        e.currentTarget.style.color = '#94A3B8';
                      }
                    }}
                    title={collapsed ? item.label : undefined}
                  >
                    <Icon size={18} color={isActive ? '#FFFFFF' : '#94A3B8'} />
                    {!collapsed && <span>{item.label}</span>}
                  </button>
                );
              })}
            </div>
          </nav>
        </div>

        {/* Bottom Sidebar User Info & Sign Out */}
        <div style={{ borderTop: '1px solid rgba(255, 255, 255, 0.08)', padding: '1rem 0.75rem' }}>
          {!collapsed ? (
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '0.5rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', overflow: 'hidden' }}>
                <img
                  src={user.photo_url || 'https://api.dicebear.com/7.x/avataaars/svg?seed=dexa'}
                  alt={user.name}
                  style={{ width: '34px', height: '34px', borderRadius: '50%', objectFit: 'cover', border: '1px solid rgba(255,255,255,0.2)' }}
                />
                <div style={{ overflow: 'hidden' }}>
                  <div style={{ fontSize: '0.82rem', fontWeight: 700, color: '#FFFFFF', whiteSpace: 'nowrap', textOverflow: 'ellipsis', overflow: 'hidden' }}>
                    {user.name}
                  </div>
                  <div style={{ fontSize: '0.68rem', color: '#94A3B8' }}>{user.role}</div>
                </div>
              </div>
              <button
                onClick={onLogout}
                style={{
                  background: 'transparent',
                  border: 'none',
                  color: '#EF4444',
                  cursor: 'pointer',
                  padding: '6px',
                  borderRadius: '6px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center'
                }}
                title="Sign out of DEXA"
              >
                <LogOut size={16} />
              </button>
            </div>
          ) : (
            <button
              onClick={onLogout}
              style={{
                width: '100%',
                background: 'transparent',
                border: 'none',
                color: '#EF4444',
                cursor: 'pointer',
                padding: '6px',
                display: 'flex',
                justifyContent: 'center'
              }}
              title="Sign Out"
            >
              <LogOut size={18} />
            </button>
          )}
        </div>
      </aside>

      {/* 2. MAIN APPLICATION CONTENT AREA */}
      <div style={{ flex: '1 1 0%', display: 'flex', flexDirection: 'column', minWidth: 0 }}>
        {/* TOP BAR */}
        <header
          style={{
            height: '62px',
            backgroundColor: '#FFFFFF',
            borderBottom: '1px solid #E2E8F0',
            padding: '0 1.75rem',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            position: 'sticky',
            top: 0,
            zIndex: 40,
            boxShadow: '0 1px 2px rgba(15, 23, 42, 0.02)'
          }}
        >
          {/* Breadcrumb & Scope */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <span style={{ fontSize: '0.78rem', color: '#64748B', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.04em' }}>
              DEXA Campus ERP
            </span>
            <span style={{ color: '#CBD5E1' }}>/</span>
            <span style={{ fontSize: '0.88rem', fontWeight: 700, color: '#0F172A' }}>
              {navItems.find((n) => n.id === activeTab)?.label || 'Intelligence Workspace'}
            </span>
          </div>

          {/* Right Action Controls */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            {/* Academic Year Selector */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', fontSize: '0.82rem' }}>
              <span style={{ color: '#64748B', fontWeight: 600 }}>Academic Year:</span>
              <select
                value={selectedYear}
                onChange={(e) => onYearChange(e.target.value)}
                style={{
                  background: '#F8FAFC',
                  border: '1px solid #CBD5E1',
                  borderRadius: '6px',
                  padding: '4px 8px',
                  fontSize: '0.82rem',
                  fontWeight: 600,
                  color: '#0F172A',
                  cursor: 'pointer'
                }}
              >
                <option value="all">All Years (1–4)</option>
                <option value="1">Year 1</option>
                <option value="2">Year 2</option>
                <option value="3">Year 3</option>
                <option value="4">Year 4</option>
              </select>
            </div>

            {/* Semester Selector */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', fontSize: '0.82rem' }}>
              <span style={{ color: '#64748B', fontWeight: 600 }}>Semester:</span>
              <select
                value={selectedSemester}
                onChange={(e) => onSemesterChange(e.target.value)}
                style={{
                  background: '#F8FAFC',
                  border: '1px solid #CBD5E1',
                  borderRadius: '6px',
                  padding: '4px 8px',
                  fontSize: '0.82rem',
                  fontWeight: 600,
                  color: '#0F172A',
                  cursor: 'pointer'
                }}
              >
                <option value="all">All Semesters</option>
                <option value="1">Semester 1</option>
                <option value="2">Semester 2</option>
                <option value="3">Semester 3</option>
                <option value="4">Semester 4</option>
                <option value="5">Semester 5</option>
                <option value="6">Semester 6</option>
                <option value="7">Semester 7</option>
                <option value="8">Semester 8</option>
              </select>
            </div>

            {/* Real-time sync badge */}
            <div
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '0.35rem',
                backgroundColor: '#ECFDF5',
                color: '#059669',
                padding: '3px 8px',
                borderRadius: '999px',
                fontSize: '0.72rem',
                fontWeight: 700,
                border: '1px solid #A7F3D0'
              }}
            >
              <span style={{ width: '6px', height: '6px', borderRadius: '50%', backgroundColor: '#059669', display: 'inline-block' }} />
              Live Sync (500 Students)
            </div>

            {/* Voice Copilot Button */}
            <button
              onClick={onOpenVoiceCopilot}
              style={{
                background: '#EFF6FF',
                color: '#1E40AF',
                border: '1px solid #BFDBFE',
                borderRadius: '8px',
                padding: '6px 12px',
                fontSize: '0.8rem',
                fontWeight: 700,
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '0.4rem',
                transition: 'all 0.15s ease'
              }}
              title="Launch Multilingual Voice Copilot"
            >
              <Mic size={15} />
              <span>Voice Copilot</span>
            </button>
          </div>
        </header>

        {/* WORKSPACE PAGE VIEW CONTAINER */}
        <main style={{ padding: '1.75rem', flex: '1 1 0%', maxWidth: '1600px', width: '100%', margin: '0 auto' }}>
          {children}
        </main>
      </div>
    </div>
  );
};
