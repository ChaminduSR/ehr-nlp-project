import React, { useState, Suspense, lazy } from 'react'
import Card from '../components/Card'

const JointCanvas = lazy(() => import('../components/JointCanvas'))

function Das28Calculator() {
  const [tjc, setTjc] = useState(0)
  const [sjc, setSjc] = useState(0)
  const [esr, setEsr] = useState(10)
  const [gh, setGh] = useState(50)
  const [result, setResult] = useState(null)

  function calculate() {
    const safeEsr = esr <= 0 ? 1 : esr
    const das = 0.56 * Math.sqrt(Number(tjc)) + 0.28 * Math.sqrt(Number(sjc)) + 0.70 * Math.log(Number(safeEsr)) + 0.014 * Number(gh)
    setResult(Number.isFinite(das) ? das : null)
  }

  function interpret(d) {
    if (d === null) return ''
    if (d < 2.6) return 'Remission'
    if (d < 3.2) return 'Low disease activity'
    if (d <= 5.1) return 'Moderate disease activity'
    return 'High disease activity'
  }

  return (
    <div>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8 }}>
        <label>Tender joint count (0-28)
          <input type="number" value={tjc} min={0} max={28} onChange={e => setTjc(e.target.value)} />
        </label>
        <label>Swollen joint count (0-28)
          <input type="number" value={sjc} min={0} max={28} onChange={e => setSjc(e.target.value)} />
        </label>
        <label>ESR (mm/hr)
          <input type="number" value={esr} min={0} onChange={e => setEsr(e.target.value)} />
        </label>
        <label>Patient global health (0-100)
          <input type="number" value={gh} min={0} max={100} onChange={e => setGh(e.target.value)} />
        </label>
      </div>
      <div style={{ marginTop: 8, display: 'flex', gap: 8 }}>
        <button onClick={calculate}>Calculate DAS28</button>
        {result !== null && (
          <div>
            <strong>{result.toFixed(2)}</strong> — {interpret(result)}
          </div>
        )}
      </div>
    </div>
  )
}

export default function JointAssessment() {
  return (
    <div className="page joint-assessment">
      <h1>Joint Assessment</h1>
      <Card title="Joint Canvas">
        <Suspense fallback={<div>Loading canvas...</div>}>
          <JointCanvas />
        </Suspense>
      </Card>
      <Card title="DAS28 Calculator">
        <Das28Calculator />
      </Card>
    </div>
  )
}
