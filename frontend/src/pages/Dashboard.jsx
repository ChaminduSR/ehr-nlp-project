import React from 'react'
import Card from '../components/Card'

export default function Dashboard() {
  return (
    <div className="page dashboard">
      <h1>Overview</h1>
      <div className="grid cards">
        <Card title="Bundle Size">
          <div>150KB</div>
          <div className="muted">Optimized</div>
        </Card>
        <Card title="Contrast Ratio">
          <div>7:1</div>
          <div className="muted">WCAG AAA</div>
        </Card>
        <Card title="Touch Target">
          <div>48px</div>
        </Card>
        <Card title="Load Time">
          <div>&lt;1s</div>
        </Card>
      </div>
    </div>
  )
}
