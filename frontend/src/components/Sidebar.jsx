import React from 'react'
import { NavLink } from 'react-router-dom'

export default function Sidebar() {
  return (
    <aside className="sidebar" style={{ width: 220, padding: 16, background: '#fff', borderRight: '1px solid #e6e9ef' }}>
      <div style={{ fontWeight: 700, marginBottom: 12 }}>Menu</div>
      <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'grid', gap: 8 }}>
        <li><NavLink to="/" end style={({ isActive }) => ({ textDecoration: 'none', color: isActive ? '#111' : '#6b7280' })}>Dashboard</NavLink></li>
        <li><NavLink to="/patients" style={({ isActive }) => ({ textDecoration: 'none', color: isActive ? '#111' : '#6b7280' })}>Patients</NavLink></li>
        <li><NavLink to="/medical-note" style={({ isActive }) => ({ textDecoration: 'none', color: isActive ? '#111' : '#6b7280' })}>Medical Note</NavLink></li>
        <li><NavLink to="/joint-assessment" style={({ isActive }) => ({ textDecoration: 'none', color: isActive ? '#111' : '#6b7280' })}>Joint Assessment</NavLink></li>
      </ul>
    </aside>
  )
}
