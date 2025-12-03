import React, { useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import axios from 'axios'
import Card from '../components/Card'
import VoiceInput from '../components/ehr/VoiceInput'

export default function MedicalNote() {
  const [searchParams] = useSearchParams()
  const visitId = searchParams.get('visit_id')

  const [fragmentHtml, setFragmentHtml] = useState(null)
  const [loading, setLoading] = useState(true)
  const [patient, setPatient] = useState(null)
  const [visit, setVisit] = useState(null)

  useEffect(() => {
    if (!visitId) {
      setLoading(false)
      return
    }

    const loadData = async () => {
      try {
        // 1. Fetch Visit
        const visitRes = await axios.get(`/api/v1/visits/${visitId}`)
        setVisit(visitRes.data)

        // 2. Fetch Patient
        if (visitRes.data.patient_id) {
          const patientRes = await axios.get(`/api/v1/patients/${visitRes.data.patient_id}`)
          setPatient(patientRes.data)
        }

        // 3. Fetch Note Fragment
        const fragmentRes = await fetch(`/api/v1/medical_notes/fragment?visit_id=${visitId}`)
        const html = await fragmentRes.text()
        setFragmentHtml(html)
      } catch (err) {
        console.error('Failed to load medical note data', err)
      } finally {
        setLoading(false)
      }
    }

    loadData()
  }, [visitId])

  // Execute scripts in the fragment
  useEffect(() => {
    if (fragmentHtml) {
      const container = document.getElementById('medical-note-fragment')
      if (container) {
        const scripts = container.getElementsByTagName('script')
        Array.from(scripts).forEach(script => {
          const newScript = document.createElement('script')
          Array.from(script.attributes).forEach(attr => newScript.setAttribute(attr.name, attr.value))
          newScript.appendChild(document.createTextNode(script.innerHTML))
          script.parentNode.replaceChild(newScript, script)
        })
      }
    }
  }, [fragmentHtml])

  const handleTranscription = (text) => {
    // Call the global function exposed by the fragment
    if (window.injectDictation) {
      window.injectDictation(text)
    } else {
      console.warn('injectDictation function not found in fragment')
    }
  }

  return (
    <div className="page medical-note">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h1>Medical Note</h1>
        {visitId && (
          <VoiceInput onTranscribe={handleTranscription} />
        )}
      </div>

      <Card title="Patient Info">
        {!visitId ? (
          <div className="muted">Select a patient from the Patients list to begin a visit.</div>
        ) : patient ? (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1rem' }}>
            <div>
              <label>Name</label>
              <div className="font-medium">{patient.last_name}, {patient.first_name}</div>
            </div>
            <div>
              <label>MRN</label>
              <div className="font-medium">{patient.mrn}</div>
            </div>
            <div>
              <label>DOB</label>
              <div className="font-medium">{patient.date_of_birth}</div>
            </div>
            <div>
              <label>Visit Date</label>
              <div className="font-medium">{visit?.visit_date}</div>
            </div>
          </div>
        ) : (
          <div>Loading patient info...</div>
        )}
      </Card>

      <Card title="Note">
        <div>
          {loading && <div className="muted">Loading note editor...</div>}
          {!loading && !visitId && <div className="muted">No visit selected.</div>}
          {!loading && visitId && fragmentHtml && (
            <div
              id="medical-note-fragment"
              dangerouslySetInnerHTML={{ __html: fragmentHtml }}
            />
          )}
        </div>
      </Card>
    </div>
  )
}
