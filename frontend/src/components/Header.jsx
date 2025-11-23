import React from 'react'
import { NavLink } from 'react-router-dom'

export default function Header() {
  return (
    <header className="site-header" style={{ padding: '12px 16px', background: '#fff', borderBottom: '1px solid #e6e9ef' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
        <div style={{ fontWeight: 700 }}>EHR NLP</div>
        <nav style={{ display: 'flex', gap: 12 }}>
          <NavLink to="/" end style={({ isActive }) => ({ textDecoration: 'none', color: isActive ? '#111' : '#6b7280' })}>Dashboard</NavLink>
          <NavLink to="/patients" style={({ isActive }) => ({ textDecoration: 'none', color: isActive ? '#111' : '#6b7280' })}>Patients</NavLink>
          <NavLink to="/medical-note" style={({ isActive }) => ({ textDecoration: 'none', color: isActive ? '#111' : '#6b7280' })}>Medical Note</NavLink>
          <NavLink to="/joint-assessment" style={({ isActive }) => ({ textDecoration: 'none', color: isActive ? '#111' : '#6b7280' })}>Joint Assessment</NavLink>
        </nav>
      </div>
    </header>
  )
}
