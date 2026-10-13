import React from 'react';
import { 
  Award, 
  Calendar, 
  Clock, 
  CheckCircle2, 
  AlertCircle, 
  TrendingUp, 
  Briefcase, 
  BookOpen, 
  ArrowRight,
  ShieldCheck,
  Zap,
  Target
} from 'lucide-react';
import { StudentProfile, SemesterRecord, AttendanceRecord, PlacementMetric } from '../types/student';
import { MoodMascotCard, STUDENT_CGPA } from './MoodMascot';

interface OverviewSectionProps {
  student: StudentProfile;
  academic: SemesterRecord[];
  attendance: AttendanceRecord;
  placement: PlacementMetric;
  onNavigateTab: (tab: string) => void;
  onOpenProfile: () => void;
}

export const OverviewSection: React.FC<OverviewSectionProps> = ({
  student,
  academic,
  attendance,
  placement,
  onNavigateTab,
  onOpenProfile
}) => {
  const currentSemester = academic.find(r => r.semester === student.semester) || academic[academic.length - 1];

  const todaySchedule = [
    { period: 1, time: '09:00 - 09:50 AM', code: 'CB301', subject: 'Discrete Mathematics', room: 'Hall 302', faculty: 'Dr. R. Murugesan' },
    { period: 2, time: '09:50 - 10:40 AM', code: 'CB302', subject: 'Design & Analysis of Algorithms', room: 'Hall 302', faculty: 'Prof. K. Saravanan' },
    { period: 3, time: '11:00 - 11:50 AM', code: 'CB303', subject: 'Operating Systems', room: 'Hall 302', faculty: 'Dr. M. Jayanthi' },
    { period: 4, time: '11:50 - 12:40 PM', code: 'CB304', subject: 'Fundamentals of Business Systems', room: 'Hall 302', faculty: 'Prof. S. Ramesh' },
    { period: 5, time: '01:30 - 03:10 PM', code: 'CB307', subject: 'Algorithms & OS Laboratory', room: 'Lab 4 (Autonomous Block)', faculty: 'Prof. K. Saravanan' },
  ];

  return (
    <div className="space-y-6">
      {/* Student Identity Card (Full White, Human-made, Camu Inspired) */}
      <div className="p-5 sm:p-6 bg-white rounded-xl border border-slate-200 shadow-2xs">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-5 border-b border-slate-100">
          <div className="flex items-center gap-4">
            <div className="w-16 h-20 rounded-lg overflow-hidden border border-slate-200 shadow-xs bg-slate-50 shrink-0">
              <img 
                src={student.avatarUrl} 
                alt={student.name} 
                className="w-full h-full object-cover"
                referrerPolicy="no-referrer"
              />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-lg sm:text-xl font-bold text-slate-900 tracking-tight">
                  {student.name}
                </h2>
                <span className="text-xs font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
                  {student.status}
                </span>
              </div>
              <p className="text-xs text-slate-600 font-medium mt-0.5">
                {student.courseName} · {student.degree}
              </p>
              <div className="flex flex-wrap items-center gap-2 text-xs text-slate-500 font-mono mt-1">
                <span>Roll: <strong className="text-slate-800">{student.rollNo}</strong></span>
                <span>·</span>
                <span>Adm: <strong className="text-slate-800">{student.admissionNo}</strong></span>
                <span>·</span>
                <span>{student.semester} - Section {student.section}</span>
              </div>
            </div>
          </div>

          <div className="flex sm:flex-col items-center sm:items-end justify-between w-full sm:w-auto gap-2">
            <button
              onClick={onOpenProfile}
              className="px-3.5 py-1.5 text-xs font-semibold text-blue-700 bg-blue-50 hover:bg-blue-100 rounded-lg border border-blue-200 transition-colors whitespace-nowrap"
            >
              View Full Camu Profile
            </button>
            <div className="text-[11px] text-slate-500 text-right">
              Proctor: <strong className="text-slate-700">Dr. K. Saravanan</strong>
            </div>
          </div>
        </div>

        {/* 4 Core Quantitative Pillars */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 pt-5">
          {/* CGPA */}
          <div 
            onClick={() => onNavigateTab('academic')}
            className="p-3.5 rounded-lg border border-slate-100 bg-slate-50/50 hover:bg-slate-50 transition-colors cursor-pointer group"
          >
            <div className="flex items-center justify-between text-xs text-slate-500 font-semibold uppercase">
              <span>Academic CGPA</span>
              <TrendingUp className="w-3.5 h-3.5 text-blue-600" />
            </div>
            <div className="mt-1 flex items-baseline gap-1.5 font-mono">
              <span className="text-2xl font-bold text-slate-900">8.72</span>
              <span className="text-xs text-slate-500">/ 10.0</span>
            </div>
            <div className="text-[11px] text-emerald-700 font-medium mt-1">
              Distinction · 0 Arrears
            </div>
          </div>

          {/* Attendance */}
          <div 
            onClick={() => onNavigateTab('attendance')}
            className="p-3.5 rounded-lg border border-slate-100 bg-slate-50/50 hover:bg-slate-50 transition-colors cursor-pointer group"
          >
            <div className="flex items-center justify-between text-xs text-slate-500 font-semibold uppercase">
              <span>Attendance</span>
              <Clock className="w-3.5 h-3.5 text-emerald-600" />
            </div>
            <div className="mt-1 flex items-baseline gap-1.5 font-mono">
              <span className="text-2xl font-bold text-slate-900">{attendance.overallPercentage}%</span>
              <span className="text-xs text-slate-500">/ 75% req</span>
            </div>
            <div className="text-[11px] text-emerald-700 font-medium mt-1">
              +78 Classes Safe Buffer
            </div>
          </div>

          {/* Placement */}
          <div 
            onClick={() => onNavigateTab('placement')}
            className="p-3.5 rounded-lg border border-slate-100 bg-slate-50/50 hover:bg-slate-50 transition-colors cursor-pointer group"
          >
            <div className="flex items-center justify-between text-xs text-slate-500 font-semibold uppercase">
              <span>Placement Readiness</span>
              <Briefcase className="w-3.5 h-3.5 text-purple-600" />
            </div>
            <div className="mt-1 flex items-baseline gap-1.5 font-mono">
              <span className="text-2xl font-bold text-blue-700">87.2%</span>
              <span className="text-xs text-slate-500">Score</span>
            </div>
            <div className="text-[11px] text-blue-700 font-medium mt-1">
              5 Dream Companies Eligible
            </div>
          </div>

          {/* Segmentation */}
          <div 
            onClick={() => onNavigateTab('segmentation')}
            className="p-3.5 rounded-lg border border-slate-100 bg-slate-50/50 hover:bg-slate-50 transition-colors cursor-pointer group"
          >
            <div className="flex items-center justify-between text-xs text-slate-500 font-semibold uppercase">
              <span>Cohort Segment</span>
              <Target className="w-3.5 h-3.5 text-amber-600" />
            </div>
            <div className="mt-1 font-bold text-base text-slate-900 truncate">
              Exemplar Cohort
            </div>
            <div className="text-[11px] text-slate-600 font-medium mt-1">
              High Academic · High Placement
            </div>
          </div>
        </div>
      </div>

      {/* Mood mascot: reacts to attendance + CGPA */}
      <MoodMascotCard
        firstName={student.firstName}
        attendance={attendance.overallPercentage}
        cgpa={STUDENT_CGPA}
      />

      {/* Main 2-Column Split: Timetable on Left, Action Items & Progress on Right */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Today's Academic Timetable */}
        <div className="lg:col-span-2 bg-white rounded-xl border border-slate-200 shadow-2xs overflow-hidden">
          <div className="px-5 py-4 border-b border-slate-200 bg-slate-50/60 flex items-center justify-between">
            <div>
              <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                <Calendar className="w-4 h-4 text-blue-600" />
                Today's Lecture & Laboratory Schedule
              </h3>
              <p className="text-xs text-slate-500">
                Odd Semester 2026-27 · Autonomous Regulation Block
              </p>
            </div>
            <span className="text-xs font-mono font-semibold px-2 py-1 bg-white rounded border border-slate-200 text-slate-700">
              Monday Schedule
            </span>
          </div>

          <div className="divide-y divide-slate-100 text-xs">
            {todaySchedule.map((item) => (
              <div key={item.period} className="p-4 hover:bg-slate-50/70 transition-colors flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                <div className="flex items-start gap-3">
                  <div className="w-8 h-8 rounded-lg bg-blue-50 border border-blue-100 flex items-center justify-center font-mono font-bold text-blue-700 shrink-0">
                    P{item.period}
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-mono font-bold text-slate-900">{item.code}</span>
                      <span className="text-slate-400">·</span>
                      <span className="font-bold text-slate-900">{item.subject}</span>
                    </div>
                    <div className="text-slate-500 mt-0.5">
                      {item.faculty} · <span className="font-medium text-slate-700">{item.room}</span>
                    </div>
                  </div>
                </div>

                <div className="sm:text-right shrink-0">
                  <div className="font-mono text-slate-700 font-semibold">{item.time}</div>
                  <div className="text-[11px] text-emerald-700 font-medium">Biometric Marked</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Priority Action Tasks & Deadlines */}
        <div className="space-y-4">
          <div className="bg-white rounded-xl border border-slate-200 shadow-2xs p-5 space-y-3 text-xs">
            <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
              <Zap className="w-4 h-4 text-amber-500" />
              Actionable Academic Alerts
            </h3>

            <div className="space-y-2.5">
              <div 
                onClick={() => onNavigateTab('lms')}
                className="p-3 bg-amber-50/70 rounded-lg border border-amber-200 hover:border-amber-300 transition-colors cursor-pointer space-y-1"
              >
                <div className="flex items-center justify-between font-bold text-amber-900">
                  <span>Assignment 3 Due Soon</span>
                  <span className="text-[11px] font-mono text-amber-800">In 6 Days</span>
                </div>
                <p className="text-amber-800 text-[11px]">
                  CB302: Dynamic Programming vs Greedy Strategy Knapsack report.
                </p>
              </div>

              <div 
                onClick={() => onNavigateTab('placement')}
                className="p-3 bg-blue-50/70 rounded-lg border border-blue-200 hover:border-blue-300 transition-colors cursor-pointer space-y-1"
              >
                <div className="flex items-center justify-between font-bold text-blue-900">
                  <span>PAT Mock Coding Sprint</span>
                  <span className="text-[11px] font-mono text-blue-800">Open</span>
                </div>
                <p className="text-blue-800 text-[11px]">
                  Internal LeetCode & Aptitude benchmark for Tier-1 company shortlist.
                </p>
              </div>

              <div 
                onClick={() => onNavigateTab('attendance')}
                className="p-3 bg-emerald-50/70 rounded-lg border border-emerald-200 hover:border-emerald-300 transition-colors cursor-pointer space-y-1"
              >
                <div className="flex items-center justify-between font-bold text-emerald-900">
                  <span>Exam Hall Ticket Status</span>
                  <span className="text-[11px] font-mono text-emerald-800">Clear</span>
                </div>
                <p className="text-emerald-800 text-[11px]">
                  Autonomous examination cell has verified 91.8% attendance.
                </p>
              </div>
            </div>
          </div>

          {/* Quick Shortcuts */}
          <div className="bg-white rounded-xl border border-slate-200 shadow-2xs p-4 text-xs space-y-2">
            <div className="font-bold text-slate-900 mb-1">Quick ERP Navigation</div>
            <button
              onClick={() => onNavigateTab('academic')}
              className="w-full text-left p-2 rounded hover:bg-slate-50 flex items-center justify-between text-slate-700 font-medium"
            >
              <span>Autonomous Grade Sheets</span>
              <ArrowRight className="w-3.5 h-3.5 text-slate-400" />
            </button>
            <button
              onClick={() => onNavigateTab('attendance')}
              className="w-full text-left p-2 rounded hover:bg-slate-50 flex items-center justify-between text-slate-700 font-medium"
            >
              <span>Class Attendance & Bunk Margin</span>
              <ArrowRight className="w-3.5 h-3.5 text-slate-400" />
            </button>
            <button
              onClick={() => onNavigateTab('segmentation')}
              className="w-full text-left p-2 rounded hover:bg-slate-50 flex items-center justify-between text-slate-700 font-medium"
            >
              <span>Student Segmentation Advisory</span>
              <ArrowRight className="w-3.5 h-3.5 text-slate-400" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
