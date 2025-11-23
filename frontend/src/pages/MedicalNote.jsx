import React, { useEffect, useRef, useState } from 'react'
import Card from '../components/Card'

export default function MedicalNote() {
  const [fragmentHtml, setFragmentHtml] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let mounted = true
    fetch('/api/v1/medical_notes/fragment')
      .then(r => r.text())
      .then(html => {
        if (!mounted) return
        setFragmentHtml(html)
      })
      .catch(() => { })
      .finally(() => mounted && setLoading(false))

    return () => { mounted = false }
  }, [])

  return (
    <div className="page medical-note">
      <h1>Medical Note</h1>
      <Card title="Patient Info">
        <div className="muted">Select a patient to begin</div>
      </Card>
      <Card title="Note">
        <div>
          {loading && <div className="muted">Loading note editor...</div>}
          {!loading && fragmentHtml && (
            <div id="medical-note-fragment" dangerouslySetInnerHTML={{ __html: fragmentHtml }} />
          )}
        </div>
      </Card>
    </div>
  )
}
