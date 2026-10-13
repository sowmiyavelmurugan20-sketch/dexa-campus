import React, { useState, useEffect } from 'react';
import { Search, Filter, ArrowUpDown, ChevronLeft, ChevronRight, FileDown, Eye } from 'lucide-react';
import { fetchStudents } from '../api';
import { Student } from '../types';

interface StudentDirectoryProps {
  onSelectStudent: (studentId: string) => void;
}

export const StudentDirectory: React.FC<StudentDirectoryProps> = ({ onSelectStudent }) => {
  const [students, setStudents] = useState<Student[]>([]);
  const [totalRecords, setTotalRecords] = useState(0);
  const [totalPages, setTotalPages] = useState(1);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);

  // Filters & Search
  const [search, setSearch] = useState('');
  const [year, setYear] = useState('all');
  const [section, setSection] = useState('all');
  const [riskTier, setRiskTier] = useState('all');
  const [segment, setSegment] = useState('all');
  const [sortBy, setSortBy] = useState('student_id');
  const [sortDesc, setSortDesc] = useState(false);

  const loadData = async () => {
    setLoading(true);
    try {
      const res = await fetchStudents({
        search: search.trim(),
        year: year,
        section: section,
        risk_tier: riskTier,
        segment: segment,
        page: page,
        limit: 15,
        sort_by: sortBy,
        sort_desc: sortDesc
      });
      setStudents(res.students);
      setTotalRecords(res.total_records);
      setTotalPages(res.total_pages);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [page, search, year, section, riskTier, segment, sortBy, sortDesc]);

  const handleSort = (col: string) => {
    if (sortBy === col) {
      setSortDesc(!sortDesc);
    } else {
      setSortBy(col);
      setSortDesc(false);
    }
    setPage(1);
  };

  return (
    <div>
      {/* Title & Actions */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.25rem', flexWrap: 'wrap', gap: '0.75rem' }}>
        <div>
          <h2 style={{ fontSize: '1.25rem', fontWeight: 800, color: '#0F172A', letterSpacing: '-0.02em', margin: 0 }}>
            Institutional Student Directory
          </h2>
          <p style={{ fontSize: '0.78rem', color: '#64748B', margin: '2px 0 0 0' }}>
            Searchable, sortable registry of all 500 engineering students with 360° dossiers and multi-criteria indicators.
          </p>
        </div>

        <a href="/api/reports/export-csv" download style={{ textDecoration: 'none' }}>
          <button className="btn-secondary" style={{ padding: '0.5rem 0.85rem', fontSize: '0.8rem' }}>
            <FileDown size={15} />
            <span>Export Registry (CSV)</span>
          </button>
        </a>
      </div>

      {/* Filter and Search Bar */}
      <div
        className="card-elevated"
        style={{
          padding: '1rem',
          marginBottom: '1.25rem',
          display: 'flex',
          flexWrap: 'wrap',
          gap: '0.75rem',
          alignItems: 'center',
          justifyContent: 'space-between'
        }}
      >
        <div style={{ position: 'relative', flex: '1 1 280px', minWidth: '240px' }}>
          <Search size={16} color="#64748B" style={{ position: 'absolute', left: '10px', top: '10px' }} />
          <input
            type="text"
            value={search}
            onChange={(e) => {
              setSearch(e.target.value);
              setPage(1);
            }}
            placeholder="Search by ID, Name, Roll No, Mentor..."
            style={{
              width: '100%',
              padding: '0.5rem 0.75rem 0.5rem 2.25rem',
              borderRadius: '8px',
              border: '1px solid #CBD5E1',
              fontSize: '0.84rem',
              outline: 'none'
            }}
          />
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flexWrap: 'wrap' }}>
          <select
            value={year}
            onChange={(e) => { setYear(e.target.value); setPage(1); }}
            style={{ padding: '0.45rem 0.65rem', borderRadius: '6px', border: '1px solid #CBD5E1', fontSize: '0.8rem' }}
          >
            <option value="all">All Years</option>
            <option value="1">Year 1</option>
            <option value="2">Year 2</option>
            <option value="3">Year 3</option>
            <option value="4">Year 4</option>
          </select>

          <select
            value={section}
            onChange={(e) => { setSection(e.target.value); setPage(1); }}
            style={{ padding: '0.45rem 0.65rem', borderRadius: '6px', border: '1px solid #CBD5E1', fontSize: '0.8rem' }}
          >
            <option value="all">All Sections</option>
            <option value="A">Section A</option>
            <option value="B">Section B</option>
          </select>

          <select
            value={riskTier}
            onChange={(e) => { setRiskTier(e.target.value); setPage(1); }}
            style={{ padding: '0.45rem 0.65rem', borderRadius: '6px', border: '1px solid #CBD5E1', fontSize: '0.8rem' }}
          >
            <option value="all">All Risk Tiers</option>
            <option value="high">High Risk (&lt; 50)</option>
            <option value="medium">Medium Risk (50–69)</option>
            <option value="low">Low Risk (≥ 70)</option>
          </select>
        </div>
      </div>

      {/* Student Registry Table */}
      <div className="card-elevated" style={{ overflow: 'hidden', marginBottom: '1.25rem' }}>
        <div style={{ overflowX: 'auto' }}>
          <table className="table-dense">
            <thead>
              <tr>
                <th onClick={() => handleSort('student_id')} style={{ cursor: 'pointer' }}>
                  Student ID {sortBy === 'student_id' && (sortDesc ? '▼' : '▲')}
                </th>
                <th onClick={() => handleSort('name')} style={{ cursor: 'pointer' }}>
                  Full Name {sortBy === 'name' && (sortDesc ? '▼' : '▲')}
                </th>
                <th>Year & Sec</th>
                <th onClick={() => handleSort('cgpa')} style={{ cursor: 'pointer' }}>
                  CGPA {sortBy === 'cgpa' && (sortDesc ? '▼' : '▲')}
                </th>
                <th onClick={() => handleSort('attendance_overall_pct')} style={{ cursor: 'pointer' }}>
                  Attendance % {sortBy === 'attendance_overall_pct' && (sortDesc ? '▼' : '▲')}
                </th>
                <th>Backlogs</th>
                <th onClick={() => handleSort('student_success_score')} style={{ cursor: 'pointer' }}>
                  Success Score {sortBy === 'student_success_score' && (sortDesc ? '▼' : '▲')}
                </th>
                <th>Risk Tier</th>
                <th>Assigned Mentor</th>
                <th style={{ textAlign: 'right' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan={10} style={{ textAlign: 'center', padding: '2.5rem', color: '#64748B' }}>
                    Loading student records...
                  </td>
                </tr>
              ) : students.length === 0 ? (
                <tr>
                  <td colSpan={10} style={{ textAlign: 'center', padding: '2.5rem', color: '#64748B' }}>
                    No students match the current filters or search query.
                  </td>
                </tr>
              ) : (
                students.map((s) => (
                  <tr key={s.student_id}>
                    <td>
                      <code style={{ fontSize: '0.78rem', color: '#1E40AF', fontWeight: 600 }}>{s.student_id}</code>
                      <div style={{ fontSize: '0.68rem', color: '#64748B' }}>{s.roll_number}</div>
                    </td>
                    <td>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
                        <img
                          src={s.photo_url || `https://api.dicebear.com/7.x/avataaars/svg?seed=${s.name}`}
                          alt={s.name}
                          style={{ width: '28px', height: '28px', borderRadius: '50%', objectFit: 'cover' }}
                        />
                        <span style={{ fontWeight: 700, color: '#0F172A' }}>{s.name}</span>
                      </div>
                    </td>
                    <td>Yr {s.year} {s.section}</td>
                    <td style={{ fontWeight: 700, color: '#0F172A' }}>{s.cgpa.toFixed(2)}</td>
                    <td>
                      <span style={{ color: s.attendance_overall_pct < 75 ? '#DC2626' : '#059669', fontWeight: 700 }}>
                        {s.attendance_overall_pct.toFixed(1)}%
                      </span>
                    </td>
                    <td>
                      <span className={`badge-pill ${s.backlogs > 0 ? 'badge-high' : 'badge-low'}`}>
                        {s.backlogs}
                      </span>
                    </td>
                    <td>
                      <b style={{ color: '#1E40AF' }}>{s.student_success_score.toFixed(1)}</b>
                    </td>
                    <td>
                      <span
                        className={`badge-pill ${
                          s.risk_level === 'High' ? 'badge-high' : s.risk_level === 'Medium' ? 'badge-med' : 'badge-low'
                        }`}
                      >
                        {s.risk_level}
                      </span>
                    </td>
                    <td style={{ color: '#334155' }}>{s.faculty_mentor}</td>
                    <td style={{ textAlign: 'right' }}>
                      <button
                        onClick={() => onSelectStudent(s.student_id)}
                        className="btn-secondary"
                        style={{ padding: '4px 8px', fontSize: '0.74rem' }}
                      >
                        <Eye size={13} />
                        <span>Inspect</span>
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination Footer */}
        <div
          style={{
            padding: '0.75rem 1rem',
            borderTop: '1px solid #E2E8F0',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            fontSize: '0.78rem',
            color: '#64748B'
          }}
        >
          <span>
            Showing <b>{students.length}</b> of <b>{totalRecords}</b> students (Page {page} of {totalPages})
          </span>

          <div style={{ display: 'flex', gap: '0.35rem' }}>
            <button
              onClick={() => setPage(Math.max(1, page - 1))}
              disabled={page <= 1}
              className="btn-secondary"
              style={{ padding: '4px 8px', fontSize: '0.75rem', opacity: page <= 1 ? 0.5 : 1 }}
            >
              <ChevronLeft size={14} />
              <span>Previous</span>
            </button>
            <button
              onClick={() => setPage(Math.min(totalPages, page + 1))}
              disabled={page >= totalPages}
              className="btn-secondary"
              style={{ padding: '4px 8px', fontSize: '0.75rem', opacity: page >= totalPages ? 0.5 : 1 }}
            >
              <span>Next</span>
              <ChevronRight size={14} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
