import React, { useState, useEffect } from 'react';
import { UserProfile } from './types';
import { LoginScreen } from './components/LoginScreen';
import { AppShell } from './components/AppShell';
import { ExecutiveOverview } from './components/ExecutiveOverview';
import { StudentDirectory } from './components/StudentDirectory';
import { StudentDrawer } from './components/StudentDrawer';
import { RiskInterventions } from './components/RiskInterventions';
import { AcademicAnalytics } from './components/AcademicAnalytics';
import { AttendanceEngagement } from './components/AttendanceEngagement';
import { PlacementIntelligence } from './components/PlacementIntelligence';
import { StudentSegments } from './components/StudentSegments';
import { ReportsSettings } from './components/ReportsSettings';
import { FacultyDirectory } from './components/FacultyDirectory';
import { StudentGrowthPortal } from './components/StudentGrowthPortal';
import { StudentAcademicsAttendance } from './components/StudentAcademicsAttendance';
import { AskZoroWidget } from './components/AskZoroWidget';
import { VoiceCopilotModal } from './components/VoiceCopilotModal';

export const App: React.FC = () => {
  const [user, setUser] = useState<UserProfile | null>(() => {
    const saved = localStorage.getItem('dexa_user');
    if (saved) {
      try {
        return JSON.parse(saved);
      } catch (e) {
        return null;
      }
    }
    return null;
  });

  const [activeTab, setActiveTab] = useState<string>('overview');
  const [selectedYear, setSelectedYear] = useState<string>('all');
  const [selectedSemester, setSelectedSemester] = useState<string>('all');
  const [selectedStudentId, setSelectedStudentId] = useState<string | null>(null);
  const [showVoiceCopilot, setShowVoiceCopilot] = useState(false);

  const handleLoginSuccess = (profile: UserProfile) => {
    setUser(profile);
    localStorage.setItem('dexa_user', JSON.stringify(profile));
    setActiveTab(profile.role === 'Student Portal' ? 'growth-portal' : 'overview');
  };

  const handleLogout = () => {
    setUser(null);
    localStorage.removeItem('dexa_user');
    setSelectedStudentId(null);
  };

  // If unauthenticated, show new enterprise LoginScreen
  if (!user) {
    return <LoginScreen onLoginSuccess={handleLoginSuccess} />;
  }

  return (
    <AppShell
      user={user}
      activeTab={activeTab}
      onTabChange={setActiveTab}
      onLogout={handleLogout}
      onOpenVoiceCopilot={() => setShowVoiceCopilot(true)}
      selectedYear={selectedYear}
      onYearChange={setSelectedYear}
      selectedSemester={selectedSemester}
      onSemesterChange={setSelectedSemester}
    >
      {/* Tab Navigation Views */}
      {activeTab === 'overview' && (
        <ExecutiveOverview
          selectedYear={selectedYear}
          selectedSemester={selectedSemester}
          onSelectStudent={(id) => setSelectedStudentId(id)}
        />
      )}

      {activeTab === 'students' && (
        <StudentDirectory onSelectStudent={(id) => setSelectedStudentId(id)} />
      )}

      {activeTab === 'interventions' && (
        <RiskInterventions onSelectStudent={(id) => setSelectedStudentId(id)} />
      )}

      {activeTab === 'academic-analytics' && (
        <StudentAcademicsAttendance
          user={user}
          selectedYear={selectedYear}
          selectedSemester={selectedSemester}
          onYearChange={setSelectedYear}
          onSemesterChange={setSelectedSemester}
        />
      )}

      {activeTab === 'academics' && (
        user.role === 'Student Portal' ? (
          <StudentAcademicsAttendance
            user={user}
            selectedYear={selectedYear}
            selectedSemester={selectedSemester}
            onYearChange={setSelectedYear}
            onSemesterChange={setSelectedSemester}
          />
        ) : (
          <AcademicAnalytics />
        )
      )}

      {activeTab === 'attendance' && <AttendanceEngagement />}

      {activeTab === 'placement' && <PlacementIntelligence />}

      {activeTab === 'segments' && (
        <StudentSegments onSelectStudent={(id) => setSelectedStudentId(id)} />
      )}

      {activeTab === 'reports' || activeTab === 'settings' ? (
        <ReportsSettings />
      ) : null}

      {activeTab === 'faculty' && <FacultyDirectory />}

      {activeTab === 'growth-portal' && <StudentGrowthPortal user={user} />}

      {/* Slide-over Student Detail Drawer */}
      <StudentDrawer
        studentId={selectedStudentId}
        onClose={() => setSelectedStudentId(null)}
      />

      {/* Floating Ask Zoro AI Widget */}
      <AskZoroWidget />

      {/* Voice Copilot Modal */}
      {showVoiceCopilot && (
        <VoiceCopilotModal
          onClose={() => setShowVoiceCopilot(false)}
          onNavigateTab={(tab) => {
            setActiveTab(tab);
            setShowVoiceCopilot(false);
          }}
        />
      )}
    </AppShell>
  );
};

export default App;
