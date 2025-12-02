import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'
import Modal from './Modal'
import Button from './Button'
import Input from './Input'

export default function PatientDetailModal({ patientId, onClose }) {
  const navigate = useNavigate()
  const [patient, setPatient] = useState(null)
  const [visits, setVisits] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [startingVisit, setStartingVisit] = useState(false)
  const [isEditing, setIsEditing] = useState(false)
  const [editForm, setEditForm] = useState({
    first_name: '',
    last_name: '',
    date_of_birth: ''
  })
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    if (!patientId) return

    setLoading(true)
    setError(null)

    Promise.all([
      axios.get(`/api/v1/patients/${patientId}`),
      axios.get(`/api/v1/visits/patient/${patientId}`)
    ])
      .then(([patientRes, visitsRes]) => {
        setPatient(patientRes.data)
        setVisits(visitsRes.data)
        setEditForm({
          first_name: patientRes.data.first_name,
          last_name: patientRes.data.last_name,
          date_of_birth: patientRes.data.date_of_birth || ''
        })
      })
      .catch(err => setError('Failed to load patient details'))
      .finally(() => setLoading(false))
  }, [patientId])

  const handleStartVisit = async () => {
    setStartingVisit(true)
    try {
      const today = new Date().toISOString().split('T')[0]
      const res = await axios.post('/api/v1/visits', {
        patient_id: patientId,
        visit_date: today,
        visit_type: 'Follow-up' // Default type
      })

      navigate(`/medical-note?visit_id=${res.data.id}`)
    } catch (err) {
      alert('Failed to start visit: ' + (err.response?.data?.error || err.message))
    } finally {
      setStartingVisit(false)
    }
  }

  const handleUpdatePatient = async (e) => {
    e.preventDefault()
    setSaving(true)
    try {
      await axios.put(`/api/v1/patients/${patientId}`, editForm)
      setPatient({ ...patient, ...editForm })
      setIsEditing(false)
    } catch (err) {
      alert('Failed to update patient: ' + (err.response?.data?.error || err.message))
    } finally {
      setSaving(false)
    }
  }

  if (!patientId) return null

  return (
    <Modal title={patient ? `${patient.last_name}, ${patient.first_name}` : 'Loading...'} onClose={onClose}>
      {loading && <div>Loading patient details...</div>}

      {error && <div style={{ color: 'var(--color-error)' }}>{error}</div>}

      {patient && !loading && !isEditing && (
        <div className="patient-detail-content">
          <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: 'var(--spacing-sm)' }}>
            <Button variant="secondary" onClick={() => setIsEditing(true)} className="btn-sm">Edit Details</Button>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--spacing-md)', marginBottom: 'var(--spacing-lg)' }}>
            <div>
              <label>MRN</label>
              <div>{patient.mrn}</div>
            </div>
            <div>
              <label>Date of Birth</label>
              <div>{patient.date_of_birth}</div>
            </div>
            <div>
              <label>Registered</label>
              <div>{patient.created_at ? new Date(patient.created_at).toLocaleDateString() : '-'}</div>
            </div>
          </div>

          <div style={{ borderTop: '1px solid var(--border-color)', paddingTop: 'var(--spacing-md)', marginBottom: 'var(--spacing-lg)' }}>
            <h3>Recent Visits</h3>
            {visits.length === 0 ? (
              <div className="muted">No visits recorded</div>
            ) : (
              <table className="patient-table" style={{ marginTop: 'var(--spacing-sm)' }}>
                <thead>
                  <tr>
                    <th>Date</th>
                    <th>Type</th>
                    <th>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {visits.map(visit => (
                    <tr key={visit.id}>
                      <td>{visit.visit_date}</td>
                      <td>{visit.visit_type}</td>
                      <td>
                        <button
                          className="btn btn-sm btn-secondary"
                          onClick={() => navigate(`/medical-note?visit_id=${visit.id}`)}
                        >
                          View
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>

          <div style={{ display: 'flex', gap: 'var(--spacing-sm)', justifyContent: 'flex-end', marginTop: 'var(--spacing-lg)' }}>
            <Button variant="secondary" onClick={onClose}>Close</Button>
            <Button onClick={handleStartVisit} disabled={startingVisit}>
              {startingVisit ? 'Starting...' : 'Start Visit'}
            </Button>
          </div>
        </div>
      )}

      {patient && !loading && isEditing && (
        <form onSubmit={handleUpdatePatient}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-md)', marginBottom: 'var(--spacing-lg)' }}>
            <div>
              <label>First Name</label>
              <Input
                value={editForm.first_name}
                onChange={e => setEditForm({ ...editForm, first_name: e.target.value })}
                required
              />
            </div>
            <div>
              <label>Last Name</label>
              <Input
                value={editForm.last_name}
                onChange={e => setEditForm({ ...editForm, last_name: e.target.value })}
                required
              />
            </div>
            <div>
              <label>Date of Birth</label>
              <Input
                type="date"
                value={editForm.date_of_birth}
                onChange={e => setEditForm({ ...editForm, date_of_birth: e.target.value })}
              />
            </div>
          </div>
          <div style={{ display: 'flex', gap: 'var(--spacing-sm)', justifyContent: 'flex-end' }}>
            <Button variant="secondary" type="button" onClick={() => setIsEditing(false)}>Cancel</Button>
            <Button type="submit" disabled={saving}>{saving ? 'Saving...' : 'Save Changes'}</Button>
          </div>
        </form>
      )}
    </Modal>
  )
}
