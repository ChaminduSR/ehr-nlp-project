import React, { useEffect, useRef, useState } from 'react'
import Card from '../components/Card'

export default function Patients() {
  const [fragmentHtml, setFragmentHtml] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let mounted = true
    // Try to fetch the server-side fragment (HTMX style)
    fetch('/api/v1/patients/fragment')
      .then(r => r.text())
      .then(html => {
        if (!mounted) return
        setFragmentHtml(html)
      })
      .catch(() => {
        if (!mounted) return
      })
      .finally(() => mounted && setLoading(false))

    return () => { mounted = false }
  }, [])

  return (
    <div className="page patients">
      <h1>Patients</h1>
      <Card title="Patient Search">
        <input placeholder="Search patients..." className="input" />
      </Card>
      <Card title="Patient List">
        <div>
          {loading && <div className="muted">Loading patients...</div>}
          {!loading && fragmentHtml && (
            <div id="patients-fragment" dangerouslySetInnerHTML={{ __html: fragmentHtml }} />
          )}
        </div>
      </Card>
    </div>
  )
}
