import React, { useState, useMemo } from 'react';
import { 
  Users, 
  AlertTriangle, 
  CheckCircle2, 
  Search, 
  Filter, 
  Phone, 
  UserCheck, 
  Clock, 
  ArrowUpDown, 
  ChevronRight, 
  ShieldAlert, 
  Sparkles, 
  Calendar, 
  FileText, 
  Send, 
  X, 
  TrendingUp, 
  Award, 
  GraduationCap, 
  BookOpen, 
  Building2, 
  Download,
  AlertCircle
} from 'lucide-react';
import { initialAssignedStudents, AssignedStudent, staffAdvisorProfile, StudentInterventionRecord } from '../../data/staffViewData';
import { MoodMascotMini } from '../MoodMascot';

export const StaffDashboardView: React.FC = () => {
  const [students, setStudents] = useState<AssignedStudent[]>(initialAssignedStudents);
  const [activeSubTab, setActiveSubTab] = useState<'risk-queue' | 'roster' | 'analytics'>('risk-queue');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [riskFilter, setRiskFilter] = useState<'ALL' | 'HIGH' | 'MEDIUM' | 'SAFE'>('ALL');
  const [sectionFilter, setSectionFilter] = useState<'ALL' | 'A' | 'B'>('ALL');
  const [sortField, setSortField] = useState<'risk' | 'attendance' | 'cgpa' | 'name'>('risk');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');

  // Modal states
  const [selectedStudentForIntervene, setSelectedStudentForIntervene] = useState<AssignedStudent | null>(null);
  const [selectedStudentForDetail, setSelectedStudentForDetail] = useState<AssignedStudent | null>(null);
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  // Intervention form state
  const [interventionType, setInterventionType] = useState<string>('Remedial Coaching Class');
  const [interventionNotes, setInterventionNotes] = useState<string>('');
  const [actionDueDate, setActionDueDate] = useState<string>('2026-04-18');
  const [outcomeStatus, setOutcomeStatus] = useState<StudentInterventionRecord['outcomeStatus']>('In Progress');

  // Stats computation
  const stats = useMemo(() => {
    const total = students.length;
    const high = students.filter(s => s.riskLevel === 'HIGH').length;
    const medium = students.filter(s => s.riskLevel === 'MEDIUM').length;
    const safe = students.filter(s => s.riskLevel === 'SAFE').length;
    const avgAtt = (students.reduce((acc, s) => acc + s.attendancePercentage, 0) / total).toFixed(1);
    const avgCg = (students.reduce((acc, s) => acc + s.cgpa, 0) / total).toFixed(2);
    const totalInterventions = students.reduce((acc, s) => acc + s.interventions.length, 0);
    return { total, high, medium, safe, avgAtt, avgCg, totalInterventions };
  }, [students]);

  // Filtered students for Roster
  const filteredStudents = useMemo(() => {
    return students
      .filter(s => {
        const matchesSearch = 
          s.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
          s.rollNo.toLowerCase().includes(searchQuery.toLowerCase()) ||
          s.registerNo.toLowerCase().includes(searchQuery.toLowerCase());
        const matchesRisk = riskFilter === 'ALL' || s.riskLevel === riskFilter;
        const matchesSection = sectionFilter === 'ALL' || s.section === sectionFilter;
        return matchesSearch && matchesRisk && matchesSection;
      })
      .sort((a, b) => {
        if (sortField === 'risk') {
          const priority = { HIGH: 1, MEDIUM: 2, SAFE: 3 };
          return (priority[a.riskLevel] - priority[b.riskLevel]) * (sortOrder === 'asc' ? 1 : -1);
        }
        if (sortField === 'attendance') {
          return (a.attendancePercentage - b.attendancePercentage) * (sortOrder === 'asc' ? 1 : -1);
        }
        if (sortField === 'cgpa') {
          return (a.cgpa - b.cgpa) * (sortOrder === 'asc' ? 1 : -1);
        }
        return a.name.localeCompare(b.name) * (sortOrder === 'asc' ? 1 : -1);
      });
  }, [students, searchQuery, riskFilter, sectionFilter, sortField, sortOrder]);

  // High & Medium Risk Students for Early Warning Queue
  const riskQueueStudents = useMemo(() => {
    return students.filter(s => s.riskLevel === 'HIGH' || s.riskLevel === 'MEDIUM');
  }, [students]);

  const handleOpenIntervene = (student: AssignedStudent, e?: React.MouseEvent) => {
    e?.stopPropagation();
    setSelectedStudentForIntervene(student);
    setInterventionType(student.riskLevel === 'HIGH' ? 'Parent Alert & Remedial Notice' : '1-on-1 Mentoring Meeting');
    setInterventionNotes('');
  };

  const handleSaveIntervention = (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedStudentForIntervene) return;

    const newRecord: StudentInterventionRecord = {
      id: `int-${Date.now()}`,
      date: new Date().toISOString().split('T')[0],
      type: interventionType,
      notes: interventionNotes || `Action initiated by ${staffAdvisorProfile.name}`,
      facultyName: staffAdvisorProfile.name,
      outcomeStatus: outcomeStatus
    };

    setStudents(prev => prev.map(st => {
      if (st.id === selectedStudentForIntervene.id) {
        return {
          ...st,
          lastInterventionDate: newRecord.date,
          lastInterventionType: newRecord.type,
          interventionNotes: newRecord.notes,
          interventions: [newRecord, ...st.interventions]
        };
      }
      return st;
    }));

    setToastMessage(`Intervention successfully logged for ${selectedStudentForIntervene.name}`);
    setTimeout(() => setToastMessage(null), 4000);
    setSelectedStudentForIntervene(null);
  };

  const handleExportCSV = () => {
    const headers = ['Roll No', 'Name', 'Section', 'Attendance %', 'CGPA', 'Arrears', 'Risk Level', 'Parent Contact'];
    const rows = filteredStudents.map(s => [
      s.rollNo,
      `"${s.name}"`,
      s.section,
      s.attendancePercentage,
      s.cgpa,
      s.arrearsCount,
      s.riskLevel,
      `"${s.parentPhone}"`
    ]);
    const csvContent = 'data:text/csv;charset=utf-8,' + [headers.join(','), ...rows.map(e => e.join(','))].join('\n');
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `Staff_Class_Roster_60_Students.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="space-y-6">
      {/* Toast Notification */}
      {toastMessage && (
        <div className="fixed top-20 right-6 z-50 bg-emerald-700 text-white px-4 py-3 rounded-xl shadow-lg border border-emerald-600 flex items-center gap-3 animate-in fade-in slide-in-from-top-4">
          <CheckCircle2 className="w-5 h-5 text-emerald-200" />
          <span className="text-sm font-semibold">{toastMessage}</span>
          <button onClick={() => setToastMessage(null)} className="text-emerald-200 hover:text-white ml-2">
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* Staff View Title & Advisor Identity Banner */}
      <div className="bg-white rounded-2xl border border-slate-200/80 p-5 sm:p-6 shadow-xs">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
          <div className="flex items-start gap-4">
            <div className="w-14 h-14 rounded-xl bg-blue-700 text-white flex items-center justify-center font-bold text-xl shadow-md shrink-0 border border-blue-800">
              KV
            </div>
            <div>
              <div className="flex flex-wrap items-center gap-2 mb-1">
                <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-blue-50 text-blue-700 border border-blue-200">
                  Class Advisor Portal
                </span>
                <span className="text-xs font-mono text-slate-500">
                  EMP-ID: {staffAdvisorProfile.employeeId}
                </span>
                <span className="text-xs font-medium text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200 flex items-center gap-1">
                  <CheckCircle2 className="w-3 h-3" /> Active Academic Advisor
                </span>
              </div>
              <h1 className="text-xl sm:text-2xl font-bold text-slate-900 tracking-tight">
                {staffAdvisorProfile.name}
              </h1>
              <p className="text-xs sm:text-sm text-slate-600 mt-0.5">
                {staffAdvisorProfile.designation} · {staffAdvisorProfile.assignedSection} · {staffAdvisorProfile.cabinLocation}
              </p>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-2 shrink-0">
            <button
              onClick={handleExportCSV}
              className="inline-flex items-center gap-1.5 px-3 py-2 text-xs font-semibold text-slate-700 bg-slate-100 hover:bg-slate-200 rounded-lg border border-slate-300 transition-colors"
            >
              <Download className="w-3.5 h-3.5" />
              Export Roster (CSV)
            </button>
            <div className="text-right pl-3 border-l border-slate-200 hidden sm:block">
              <div className="text-[11px] font-mono text-slate-500 uppercase tracking-wider">Office Hours</div>
              <div className="text-xs font-bold text-slate-800">{staffAdvisorProfile.officeHours}</div>
            </div>
          </div>
        </div>

        {/* 5 Enterprise Metric Cards */}
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3 mt-6 pt-5 border-t border-slate-100">
          <div className="p-3.5 bg-blue-50/60 rounded-xl border border-blue-100">
            <div className="flex items-center justify-between text-blue-700 mb-1">
              <span className="text-xs font-semibold">Assigned Cohort</span>
              <Users className="w-4 h-4" />
            </div>
            <div className="text-2xl font-extrabold text-blue-900">{stats.total}</div>
            <div className="text-[11px] text-blue-700 mt-0.5">Students (Sec A & B)</div>
          </div>

          <div className="p-3.5 bg-rose-50/70 rounded-xl border border-rose-200/80">
            <div className="flex items-center justify-between text-rose-700 mb-1">
              <span className="text-xs font-semibold">High Risk Queue</span>
              <AlertTriangle className="w-4 h-4 text-rose-600" />
            </div>
            <div className="text-2xl font-extrabold text-rose-700">{stats.high}</div>
            <div className="text-[11px] text-rose-600 mt-0.5">Critical Early Warnings</div>
          </div>

          <div className="p-3.5 bg-amber-50/70 rounded-xl border border-amber-200">
            <div className="flex items-center justify-between text-amber-800 mb-1">
              <span className="text-xs font-semibold">Medium Risk</span>
              <Clock className="w-4 h-4 text-amber-600" />
            </div>
            <div className="text-2xl font-extrabold text-amber-800">{stats.medium}</div>
            <div className="text-[11px] text-amber-700 mt-0.5">Borderline / Arrear (1)</div>
          </div>

          <div className="p-3.5 bg-emerald-50/60 rounded-xl border border-emerald-100">
            <div className="flex items-center justify-between text-emerald-700 mb-1">
              <span className="text-xs font-semibold">Avg Attendance</span>
              <UserCheck className="w-4 h-4 text-emerald-600" />
            </div>
            <div className="text-2xl font-extrabold text-emerald-800">{stats.avgAtt}%</div>
            <div className="text-[11px] text-emerald-700 mt-0.5">Threshold: 75.0%</div>
          </div>

          <div className="p-3.5 bg-slate-50 rounded-xl border border-slate-200">
            <div className="flex items-center justify-between text-slate-700 mb-1">
              <span className="text-xs font-semibold">Class Avg CGPA</span>
              <Award className="w-4 h-4 text-slate-600" />
            </div>
            <div className="text-2xl font-extrabold text-slate-900">{stats.avgCg}</div>
            <div className="text-[11px] text-slate-500 mt-0.5">Safe Mentees: {stats.safe}</div>
          </div>
        </div>
      </div>

      {/* Sub-Navigation Tabs */}
      <div className="flex items-center justify-between border-b border-slate-200 pb-2">
        <div className="flex items-center gap-2">
          <button
            onClick={() => setActiveSubTab('risk-queue')}
            className={`px-4 py-2 text-xs sm:text-sm font-bold rounded-lg transition-all flex items-center gap-2 ${
              activeSubTab === 'risk-queue'
                ? 'bg-blue-700 text-white shadow-xs'
                : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
            }`}
          >
            <ShieldAlert className="w-4 h-4" />
            AI Early Warning Risk Queue
            <span className={`px-1.5 py-0.2 rounded-full text-[11px] ${
              activeSubTab === 'risk-queue' ? 'bg-white/20 text-white' : 'bg-rose-100 text-rose-700'
            }`}>
              {stats.high + stats.medium}
            </span>
          </button>

          <button
            onClick={() => setActiveSubTab('roster')}
            className={`px-4 py-2 text-xs sm:text-sm font-bold rounded-lg transition-all flex items-center gap-2 ${
              activeSubTab === 'roster'
                ? 'bg-blue-700 text-white shadow-xs'
                : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
            }`}
          >
            <Users className="w-4 h-4" />
            All 60 Assigned Students Roster
          </button>

          <button
            onClick={() => setActiveSubTab('analytics')}
            className={`px-4 py-2 text-xs sm:text-sm font-bold rounded-lg transition-all hidden md:flex items-center gap-2 ${
              activeSubTab === 'analytics'
                ? 'bg-blue-700 text-white shadow-xs'
                : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
            }`}
          >
            <TrendingUp className="w-4 h-4" />
            Mentorship & Interventions ({stats.totalInterventions})
          </button>
        </div>
      </div>

      {/* TAB 1: AI Early Warning Risk Queue */}
      {activeSubTab === 'risk-queue' && (
        <div className="space-y-4">
          <div className="bg-amber-50/70 border border-amber-200/90 rounded-xl p-4 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
            <div className="flex items-start gap-3">
              <div className="p-2 bg-amber-100 text-amber-800 rounded-lg shrink-0 mt-0.5 sm:mt-0">
                <Sparkles className="w-5 h-5 text-amber-700" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-amber-900">
                  AI Early Warning Detection Engine (Active Model: NAAC/NBA Retention Rule)
                </h3>
                <p className="text-xs text-amber-800 mt-0.5">
                  Identified <strong>{stats.high} High-Risk</strong> and <strong>{stats.medium} Medium-Risk</strong> students based on attendance deficit (&lt;75%), internal mark failure (&lt;50%), standing arrears, and incomplete lab assessments.
                </p>
              </div>
            </div>
            <div className="text-xs font-mono font-bold text-amber-900 bg-amber-100/80 px-3 py-1.5 rounded-lg border border-amber-300 shrink-0">
              {stats.high + stats.medium} Cases Pending Attention
            </div>
          </div>

          {/* Risk Queue Table */}
          <div className="bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs text-slate-700">
                <thead className="bg-slate-50/80 text-slate-600 font-bold border-b border-slate-200 uppercase tracking-wider text-[11px]">
                  <tr>
                    <th className="px-4 py-3">Student & Roll No</th>
                    <th className="px-3 py-3">Section</th>
                    <th className="px-3 py-3">Risk Level</th>
                    <th className="px-3 py-3">Attendance</th>
                    <th className="px-3 py-3">CGPA / Arrears</th>
                    <th className="px-4 py-3 min-w-[260px]">AI Predictive Risk Signals</th>
                    <th className="px-3 py-3">Last Intervention</th>
                    <th className="px-4 py-3 text-right">Intervene Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {riskQueueStudents.map((st) => {
                    const isHigh = st.riskLevel === 'HIGH';
                    return (
                      <tr 
                        key={st.id} 
                        onClick={() => setSelectedStudentForDetail(st)}
                        className={`hover:bg-blue-50/30 transition-colors cursor-pointer ${
                          isHigh ? 'bg-rose-50/20' : ''
                        }`}
                      >
                        <td className="px-4 py-3">
                          <div className="flex items-center gap-3">
                            <img
                              src={st.avatarUrl}
                              alt={st.name}
                              className="w-9 h-9 rounded-full object-cover border border-slate-200 shrink-0"
                            />
                            <div>
                              <div className="font-bold text-slate-900 text-xs sm:text-sm">
                                {st.name}
                              </div>
                              <div className="text-[11px] font-mono text-slate-500">
                                {st.rollNo}
                              </div>
                            </div>
                          </div>
                        </td>
                        <td className="px-3 py-3 font-semibold text-slate-800">
                          Sec {st.section}
                        </td>
                        <td className="px-3 py-3">
                          {isHigh ? (
                            <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-rose-100 text-rose-800 border border-rose-300">
                              <AlertTriangle className="w-3 h-3 text-rose-600" />
                              High Risk
                            </span>
                          ) : (
                            <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-amber-100 text-amber-800 border border-amber-300">
                              <Clock className="w-3 h-3 text-amber-600" />
                              Medium Risk
                            </span>
                          )}
                        </td>
                        <td className="px-3 py-3">
                          <div className="flex items-center gap-1.5">
                            <MoodMascotMini attendance={st.attendancePercentage} cgpa={st.cgpa} />
                            <span className={`font-mono font-bold ${
                              st.attendancePercentage < 70 
                                ? 'text-rose-600' 
                                : st.attendancePercentage < 75 
                                  ? 'text-amber-600' 
                                  : 'text-slate-800'
                            }`}>
                              {st.attendancePercentage}%
                            </span>
                            {st.attendancePercentage < 75 && (
                              <span className="text-[10px] text-rose-700 bg-rose-50 px-1 rounded font-bold">
                                &lt;75%
                              </span>
                            )}
                          </div>
                        </td>
                        <td className="px-3 py-3">
                          <div>
                            <span className="font-mono font-bold text-slate-800">{st.cgpa}</span>
                            <span className="text-[11px] text-slate-500 ml-1">CGPA</span>
                          </div>
                          {st.arrearsCount > 0 ? (
                            <span className="inline-block text-[10px] font-semibold text-rose-700">
                              {st.arrearsCount} Arrear{st.arrearsCount > 1 ? 's' : ''}
                            </span>
                          ) : (
                            <span className="text-[10px] text-emerald-600">0 Arrears</span>
                          )}
                        </td>
                        <td className="px-4 py-3">
                          <p className="text-[11px] text-slate-700 leading-tight">
                            {st.aiPredictiveAnalysis}
                          </p>
                          <div className="flex flex-wrap gap-1 mt-1">
                            {st.riskFactors.map((rf, idx) => (
                              <span key={idx} className="text-[10px] px-1.5 py-0.2 bg-slate-100 text-slate-600 rounded">
                                {rf}
                              </span>
                            ))}
                          </div>
                        </td>
                        <td className="px-3 py-3">
                          {st.lastInterventionDate ? (
                            <div>
                              <div className="font-medium text-slate-800 text-[11px]">{st.lastInterventionType}</div>
                              <div className="text-[10px] font-mono text-slate-500">{st.lastInterventionDate}</div>
                            </div>
                          ) : (
                            <span className="text-[11px] text-slate-400 italic">None logged</span>
                          )}
                        </td>
                        <td className="px-4 py-3 text-right">
                          <button
                            onClick={(e) => handleOpenIntervene(st, e)}
                            className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-bold text-white bg-blue-700 hover:bg-blue-800 rounded-lg shadow-2xs hover:shadow-xs transition-colors whitespace-nowrap"
                          >
                            <Send className="w-3 h-3" />
                            Intervene
                          </button>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* TAB 2: All 60 Assigned Students Roster */}
      {activeSubTab === 'roster' && (
        <div className="space-y-4">
          {/* Controls: Search, Filters, Sorting */}
          <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs flex flex-col md:flex-row items-stretch md:items-center justify-between gap-3">
            <div className="relative flex-1 max-w-md">
              <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                placeholder="Search across 60 assigned students (name, roll no)..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-9 pr-3 py-2 text-xs border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600"
              />
              {searchQuery && (
                <button onClick={() => setSearchQuery('')} className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600">
                  <X className="w-3.5 h-3.5" />
                </button>
              )}
            </div>

            <div className="flex flex-wrap items-center gap-2 text-xs">
              {/* Risk Filter */}
              <div className="flex items-center gap-1 bg-slate-100 p-1 rounded-lg">
                <span className="text-[11px] font-bold text-slate-500 px-1">Risk:</span>
                {(['ALL', 'HIGH', 'MEDIUM', 'SAFE'] as const).map(lvl => (
                  <button
                    key={lvl}
                    onClick={() => setRiskFilter(lvl)}
                    className={`px-2 py-1 rounded-md font-semibold transition-colors ${
                      riskFilter === lvl
                        ? 'bg-white text-slate-900 shadow-2xs'
                        : 'text-slate-600 hover:text-slate-900'
                    }`}
                  >
                    {lvl}
                  </button>
                ))}
              </div>

              {/* Section Filter */}
              <div className="flex items-center gap-1 bg-slate-100 p-1 rounded-lg">
                <span className="text-[11px] font-bold text-slate-500 px-1">Sec:</span>
                {(['ALL', 'A', 'B'] as const).map(sec => (
                  <button
                    key={sec}
                    onClick={() => setSectionFilter(sec)}
                    className={`px-2 py-1 rounded-md font-semibold transition-colors ${
                      sectionFilter === sec
                        ? 'bg-white text-slate-900 shadow-2xs'
                        : 'text-slate-600 hover:text-slate-900'
                    }`}
                  >
                    {sec}
                  </button>
                ))}
              </div>

              {/* Sort Order Toggle */}
              <button
                onClick={() => setSortOrder(prev => prev === 'asc' ? 'desc' : 'asc')}
                className="p-1.5 border border-slate-300 rounded-lg hover:bg-slate-50 text-slate-600"
                title={`Sort ${sortOrder === 'asc' ? 'Descending' : 'Ascending'}`}
              >
                <ArrowUpDown className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Roster Table */}
          <div className="bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs text-slate-700">
                <thead className="bg-slate-50/90 text-slate-600 font-bold border-b border-slate-200 uppercase tracking-wider text-[11px]">
                  <tr>
                    <th className="px-4 py-3">#</th>
                    <th className="px-4 py-3">Student Name & Roll No</th>
                    <th className="px-3 py-3">Section</th>
                    <th 
                      onClick={() => setSortField('cgpa')}
                      className="px-3 py-3 cursor-pointer hover:text-blue-700"
                    >
                      CGPA {sortField === 'cgpa' && (sortOrder === 'asc' ? '↑' : '↓')}
                    </th>
                    <th 
                      onClick={() => setSortField('attendance')}
                      className="px-3 py-3 cursor-pointer hover:text-blue-700"
                    >
                      Attendance % {sortField === 'attendance' && (sortOrder === 'asc' ? '↑' : '↓')}
                    </th>
                    <th className="px-3 py-3">Arrears</th>
                    <th className="px-3 py-3">Status</th>
                    <th className="px-4 py-3">Parent Phone</th>
                    <th className="px-4 py-3 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {filteredStudents.map((st, index) => (
                    <tr
                      key={st.id}
                      onClick={() => setSelectedStudentForDetail(st)}
                      className="hover:bg-blue-50/30 transition-colors cursor-pointer"
                    >
                      <td className="px-4 py-3 font-mono text-slate-400">{index + 1}</td>
                      <td className="px-4 py-3">
                        <div className="flex items-center gap-3">
                          <img
                            src={st.avatarUrl}
                            alt={st.name}
                            className="w-8 h-8 rounded-full object-cover border border-slate-200 shrink-0"
                          />
                          <div>
                            <div className="font-bold text-slate-900 text-xs sm:text-sm flex items-center gap-1.5">
                              {st.name}
                              {st.rollNo === '7376222CB132' && (
                                <span className="text-[10px] bg-blue-100 text-blue-800 px-1 rounded font-bold">
                                  Current Student
                                </span>
                              )}
                            </div>
                            <div className="text-[11px] font-mono text-slate-500">
                              {st.rollNo} · Reg: {st.registerNo}
                            </div>
                          </div>
                        </div>
                      </td>
                      <td className="px-3 py-3 font-semibold text-slate-800">
                        Sec {st.section}
                      </td>
                      <td className="px-3 py-3 font-mono font-bold text-slate-900">
                        {st.cgpa}
                      </td>
                      <td className="px-3 py-3">
                        <span className={`font-mono font-bold ${
                          st.attendancePercentage < 75 ? 'text-rose-600' : 'text-slate-800'
                        }`}>
                          {st.attendancePercentage}%
                        </span>
                      </td>
                      <td className="px-3 py-3 font-mono">
                        {st.arrearsCount > 0 ? (
                          <span className="text-rose-600 font-bold">{st.arrearsCount}</span>
                        ) : (
                          <span className="text-emerald-600">0</span>
                        )}
                      </td>
                      <td className="px-3 py-3">
                        {st.riskLevel === 'HIGH' && (
                          <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-rose-100 text-rose-800">
                            High Risk
                          </span>
                        )}
                        {st.riskLevel === 'MEDIUM' && (
                          <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-100 text-amber-800">
                            Medium Risk
                          </span>
                        )}
                        {st.riskLevel === 'SAFE' && (
                          <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-100 text-emerald-800">
                            On Track
                          </span>
                        )}
                      </td>
                      <td className="px-4 py-3 font-mono text-slate-600">
                        {st.parentPhone}
                      </td>
                      <td className="px-4 py-3 text-right">
                        <div className="flex items-center justify-end gap-1.5" onClick={(e) => e.stopPropagation()}>
                          <button
                            onClick={() => handleOpenIntervene(st)}
                            className="px-2.5 py-1 text-xs font-semibold text-blue-700 bg-blue-50 hover:bg-blue-100 border border-blue-200 rounded-md transition-colors"
                          >
                            Intervene
                          </button>
                          <button
                            onClick={() => setSelectedStudentForDetail(st)}
                            className="p-1 text-slate-400 hover:text-slate-700 rounded hover:bg-slate-100"
                            title="View Full Profile"
                          >
                            <ChevronRight className="w-4 h-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* TAB 3: Mentorship & Intervention History */}
      {activeSubTab === 'analytics' && (
        <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs space-y-5">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-base font-bold text-slate-900">
                Official Mentorship & Early Warning Action Register
              </h3>
              <p className="text-xs text-slate-500">
                Compliant with NAAC Criteria 2.2.1 (Student Mentoring & Remedial Interventions)
              </p>
            </div>
            <span className="text-xs font-mono font-bold text-blue-700 bg-blue-50 px-2.5 py-1 rounded border border-blue-200">
              60 Total Mentees
            </span>
          </div>

          <div className="space-y-3">
            {students.filter(s => s.interventions.length > 0).map(st => (
              <div key={st.id} className="p-4 rounded-xl border border-slate-200 bg-slate-50/50 space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-slate-900 text-sm">{st.name}</span>
                    <span className="text-xs font-mono text-slate-500">({st.rollNo})</span>
                    <span className="text-[10px] px-2 py-0.5 rounded font-bold bg-blue-100 text-blue-800">
                      Sec {st.section}
                    </span>
                  </div>
                  <span className="text-xs font-mono font-semibold text-slate-600">
                    Attendance: {st.attendancePercentage}% · CGPA: {st.cgpa}
                  </span>
                </div>

                {st.interventions.map(int => (
                  <div key={int.id} className="p-3 bg-white rounded-lg border border-slate-200 text-xs space-y-1">
                    <div className="flex items-center justify-between">
                      <span className="font-semibold text-blue-800">{int.type}</span>
                      <span className="text-[11px] text-slate-500 font-mono">{int.date}</span>
                    </div>
                    <p className="text-slate-700">{int.notes}</p>
                    <div className="flex items-center justify-between pt-1 text-[11px] text-slate-500">
                      <span>Logged by: {int.facultyName}</span>
                      <span className="font-semibold text-emerald-700 bg-emerald-50 px-1.5 py-0.2 rounded">
                        Status: {int.outcomeStatus}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* INTERVENTION ACTION MODAL */}
      {selectedStudentForIntervene && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-lg w-full shadow-2xl border border-slate-200 overflow-hidden animate-in fade-in zoom-in-95">
            <div className="px-6 py-4 bg-blue-700 text-white flex items-center justify-between">
              <div>
                <h3 className="font-bold text-base flex items-center gap-2">
                  <ShieldAlert className="w-5 h-5 text-blue-200" />
                  Initiate Faculty Intervention
                </h3>
                <p className="text-xs text-blue-100 mt-0.5">
                  Target Student: <strong>{selectedStudentForIntervene.name}</strong> ({selectedStudentForIntervene.rollNo})
                </p>
              </div>
              <button 
                onClick={() => setSelectedStudentForIntervene(null)}
                className="text-blue-200 hover:text-white p-1 rounded-lg"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleSaveIntervention} className="p-6 space-y-4">
              {/* Student Summary Chips */}
              <div className="p-3 bg-slate-50 rounded-xl border border-slate-200 flex items-center justify-between text-xs">
                <div>
                  <div className="text-slate-500 text-[11px]">Current Attendance</div>
                  <div className={`font-mono font-bold ${
                    selectedStudentForIntervene.attendancePercentage < 75 ? 'text-rose-600' : 'text-slate-800'
                  }`}>
                    {selectedStudentForIntervene.attendancePercentage}%
                  </div>
                </div>
                <div>
                  <div className="text-slate-500 text-[11px]">Current CGPA</div>
                  <div className="font-mono font-bold text-slate-800">
                    {selectedStudentForIntervene.cgpa} / 10
                  </div>
                </div>
                <div>
                  <div className="text-slate-500 text-[11px]">Standing Arrears</div>
                  <div className="font-mono font-bold text-rose-600">
                    {selectedStudentForIntervene.arrearsCount} Course(s)
                  </div>
                </div>
                <div>
                  <div className="text-slate-500 text-[11px]">Section</div>
                  <div className="font-bold text-slate-800">
                    Sec {selectedStudentForIntervene.section}
                  </div>
                </div>
              </div>

              {/* Intervention Type Selector */}
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1.5">
                  Intervention Action Type
                </label>
                <select
                  value={interventionType}
                  onChange={(e) => setInterventionType(e.target.value)}
                  className="w-full text-xs p-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:outline-none"
                >
                  <option value="Remedial Coaching Class">📘 Remedial / Special Coaching Class (Post-College)</option>
                  <option value="Parent Alert & Telephonic Counseling">📞 Parent Telephonic Alert & Counseling Log</option>
                  <option value="1-on-1 Faculty Mentoring Meeting">🤝 1-on-1 Personal Mentoring Session</option>
                  <option value="Formal Academic Warning Notice">⚠️ Issue Formal Autonomous Academic Warning</option>
                  <option value="Peer Tutor Assignment (Top Performer Pairing)">🧑‍🤝‍🧑 Peer Tutor Pairing with Class Distinction Holder</option>
                  <option value="Medical Waiver & OD Regularization">🩺 Medical Certificate Review & OD Regularization</option>
                  <option value="HOD Escalation & Disciplinary Panel">🏛️ Escalate Case to HOD & Academic Council</option>
                </select>
              </div>

              {/* Action Plan Notes */}
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1.5">
                  Faculty Action Plan & Advisory Notes
                </label>
                <textarea
                  rows={3}
                  value={interventionNotes}
                  onChange={(e) => setInterventionNotes(e.target.value)}
                  placeholder="Detail specific tasks, assignments to clear, or parent commitments discussed..."
                  className="w-full text-xs p-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:outline-none"
                  required
                />
              </div>

              {/* Follow-up Date and Initial Status */}
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1.5">
                    Follow-Up Review Date
                  </label>
                  <input
                    type="date"
                    value={actionDueDate}
                    onChange={(e) => setActionDueDate(e.target.value)}
                    className="w-full text-xs p-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:outline-none"
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1.5">
                    Initial Case Status
                  </label>
                  <select
                    value={outcomeStatus}
                    onChange={(e) => setOutcomeStatus(e.target.value as any)}
                    className="w-full text-xs p-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:outline-none"
                  >
                    <option value="In Progress">In Progress</option>
                    <option value="Pending Review">Pending Review</option>
                    <option value="Resolved">Resolved</option>
                    <option value="Escalated to HOD">Escalated to HOD</option>
                  </select>
                </div>
              </div>

              {/* Parent Contact Quick Reference */}
              <div className="text-[11px] text-slate-500 bg-slate-50 p-2.5 rounded-lg flex items-center justify-between border border-slate-100">
                <span className="flex items-center gap-1.5">
                  <Phone className="w-3.5 h-3.5 text-blue-600" />
                  Parent: <strong>{selectedStudentForIntervene.parentName}</strong>
                </span>
                <span className="font-mono font-bold text-slate-800">{selectedStudentForIntervene.parentPhone}</span>
              </div>

              <div className="flex items-center justify-end gap-2 pt-2 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setSelectedStudentForIntervene(null)}
                  className="px-4 py-2 text-xs font-semibold text-slate-600 hover:bg-slate-100 rounded-lg"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 text-xs font-bold text-white bg-blue-700 hover:bg-blue-800 rounded-lg shadow-xs flex items-center gap-1.5"
                >
                  <CheckCircle2 className="w-4 h-4" />
                  Save & Log Intervention
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* STUDENT DETAIL DRAWER / MODAL */}
      {selectedStudentForDetail && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-xl w-full shadow-2xl border border-slate-200 overflow-hidden max-h-[90vh] flex flex-col">
            <div className="p-5 bg-gradient-to-r from-blue-700 to-blue-800 text-white flex items-center justify-between shrink-0">
              <div className="flex items-center gap-3">
                <img
                  src={selectedStudentForDetail.avatarUrl}
                  alt={selectedStudentForDetail.name}
                  className="w-12 h-12 rounded-full object-cover border-2 border-white shadow-sm"
                />
                <div>
                  <h3 className="font-bold text-base">{selectedStudentForDetail.name}</h3>
                  <p className="text-xs text-blue-100 font-mono">
                    Roll: {selectedStudentForDetail.rollNo} · Sec {selectedStudentForDetail.section}
                  </p>
                </div>
              </div>
              <button 
                onClick={() => setSelectedStudentForDetail(null)}
                className="text-blue-100 hover:text-white p-1 rounded-lg"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="p-6 overflow-y-auto space-y-4 text-xs">
              <div className="grid grid-cols-3 gap-3">
                <div className="p-3 bg-slate-50 rounded-xl border border-slate-200 text-center">
                  <div className="text-[11px] text-slate-500">Attendance</div>
                  <div className="text-base font-bold text-slate-900 mt-0.5 font-mono">
                    {selectedStudentForDetail.attendancePercentage}%
                  </div>
                </div>
                <div className="p-3 bg-slate-50 rounded-xl border border-slate-200 text-center">
                  <div className="text-[11px] text-slate-500">Cumulative CGPA</div>
                  <div className="text-base font-bold text-slate-900 mt-0.5 font-mono">
                    {selectedStudentForDetail.cgpa}
                  </div>
                </div>
                <div className="p-3 bg-slate-50 rounded-xl border border-slate-200 text-center">
                  <div className="text-[11px] text-slate-500">Active Arrears</div>
                  <div className="text-base font-bold text-rose-600 mt-0.5 font-mono">
                    {selectedStudentForDetail.arrearsCount}
                  </div>
                </div>
              </div>

              <div>
                <h4 className="font-bold text-slate-900 mb-1">AI Predictive Profile Analysis</h4>
                <div className="p-3 bg-blue-50/60 rounded-xl border border-blue-200 text-slate-700 leading-relaxed">
                  {selectedStudentForDetail.aiPredictiveAnalysis}
                </div>
              </div>

              {selectedStudentForDetail.riskFactors.length > 0 && (
                <div>
                  <h4 className="font-bold text-slate-900 mb-1">Identified Risk Signals</h4>
                  <ul className="space-y-1">
                    {selectedStudentForDetail.riskFactors.map((rf, i) => (
                      <li key={i} className="flex items-center gap-2 text-rose-700 bg-rose-50 px-2.5 py-1 rounded">
                        <AlertTriangle className="w-3.5 h-3.5 shrink-0" />
                        <span>{rf}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              <div>
                <h4 className="font-bold text-slate-900 mb-1">Parent & Guardian Contact</h4>
                <div className="p-3 bg-slate-50 rounded-xl border border-slate-200 space-y-1 text-slate-700">
                  <div>Parent Name: <strong>{selectedStudentForDetail.parentName}</strong></div>
                  <div>Primary Phone: <strong className="font-mono">{selectedStudentForDetail.parentPhone}</strong></div>
                </div>
              </div>

              <div>
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-bold text-slate-900">Intervention History ({selectedStudentForDetail.interventions.length})</h4>
                  <button
                    onClick={() => {
                      setSelectedStudentForDetail(null);
                      handleOpenIntervene(selectedStudentForDetail);
                    }}
                    className="text-xs font-bold text-blue-700 hover:underline"
                  >
                    + Add New Action
                  </button>
                </div>

                {selectedStudentForDetail.interventions.length > 0 ? (
                  <div className="space-y-2">
                    {selectedStudentForDetail.interventions.map((int) => (
                      <div key={int.id} className="p-2.5 border border-slate-200 rounded-lg bg-white space-y-1">
                        <div className="flex items-center justify-between font-semibold text-slate-900">
                          <span>{int.type}</span>
                          <span className="text-[10px] text-slate-400 font-mono">{int.date}</span>
                        </div>
                        <p className="text-slate-600">{int.notes}</p>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-slate-400 italic">No formal interventions logged yet.</div>
                )}
              </div>
            </div>

            <div className="p-4 bg-slate-50 border-t border-slate-200 flex items-center justify-end gap-2 shrink-0">
              <button
                onClick={() => setSelectedStudentForDetail(null)}
                className="px-4 py-2 text-xs font-semibold text-slate-600 hover:bg-slate-200 rounded-lg"
              >
                Close
              </button>
              <button
                onClick={() => {
                  const s = selectedStudentForDetail;
                  setSelectedStudentForDetail(null);
                  handleOpenIntervene(s);
                }}
                className="px-4 py-2 text-xs font-bold text-white bg-blue-700 hover:bg-blue-800 rounded-lg"
              >
                Log Intervention
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
