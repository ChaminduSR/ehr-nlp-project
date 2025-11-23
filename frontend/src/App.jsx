import React, { Suspense, lazy } from 'react'
import { Routes, Route } from 'react-router-dom'

const Dashboard = lazy(() => import('./pages/Dashboard'))
const Patients = lazy(() => import('./pages/Patients'))
const MedicalNote = lazy(() => import('./pages/MedicalNote'))
const JointAssessment = lazy(() => import('./pages/JointAssessment'))
const Reports = lazy(() => import('./pages/Reports'))
const DesignSystem = lazy(() => import('./pages/DesignSystem'))
const Header = lazy(() => import('./components/Header'))
const Sidebar = lazy(() => import('./components/Sidebar'))

export default function App() {
  return (
    <div className="app-root">
      <Suspense fallback={<div>Loading header...</div>}>
        <Header />
      </Suspense>
      <div className="layout">
        <Suspense fallback={<div style={{ width: 200 }}>Loading nav...</div>}>
          <Sidebar />
        </Suspense>
        <main className="main-content">
          <Suspense fallback={<div>Loading page...</div>}>
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/patients" element={<Patients />} />
              <Route path="/medical-note" element={<MedicalNote />} />
              <Route path="/joint-assessment" element={<JointAssessment />} />
              <Route path="/reports" element={<Reports />} />
              <Route path="/design-system" element={<DesignSystem />} />
            </Routes>
          </Suspense>
        </main>
      </div>
    </div>
  )
}
