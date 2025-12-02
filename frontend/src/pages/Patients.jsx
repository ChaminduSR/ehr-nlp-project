import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'
import Card from '../components/Card'
import Modal from '../components/Modal'
import Button from '../components/Button'
import Input from '../components/Input'
import PatientDetailModal from '../components/PatientDetailModal'

export default function Patients() {
  const navigate = useNavigate()
  const [fragmentHtml, setFragmentHtml] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [showAddModal, setShowAddModal] = useState(false)
  const [selectedPatientId, setSelectedPatientId] = useState(null)
  const [formData, setFormData] = useState({
    mrn: '',
    first_name: '',
    last_name: '',
    date_of_birth: ''
  })
  const [submitting, setSubmitting] = useState(false)

  const fetchPatients = (query = '', page = 1) => {
    setLoading(true)
    setError(null)
    let mounted = true

    const params = new URLSearchParams()
    if (query) params.append('q', query)
    if (page) params.append('page', page)

    const url = `/api/v1/patients/fragment?${params.toString()}`

    fetch(url)
      .then(r => r.text())
      .then(html => {
        if (!mounted) return
        setFragmentHtml(html)
      })
      .catch(err => {
        if (!mounted) return
        setError('Failed to load patients')
        console.error('Error fetching patients:', err)
      })
      .finally(() => mounted && setLoading(false))

    return () => { mounted = false }
  }

  useEffect(() => {
    fetchPatients()
  }, [])

  const handleSearch = (e) => {
    e.preventDefault()
    fetchPatients(searchQuery, 1)
  }

  const handleAddPatient = async (e) => {
    e.preventDefault()
    setSubmitting(true)

    try {
      await axios.post('/api/v1/patients', formData)
      setShowAddModal(false)
      setFormData({ mrn: '', first_name: '', last_name: '', date_of_birth: '' })
      fetchPatients(searchQuery, 1) // Refresh list
    } catch (err) {
      alert('Error creating patient: ' + (err.response?.data?.error || err.message))
    } finally {
      setSubmitting(false)
    }
  }

  const handlePatientClick = (patientId) => {
    setSelectedPatientId(patientId)
  }

  // Listen for custom event from the HTML fragment
  useEffect(() => {
    const handleOpenDetail = (e) => {
      if (e.detail && e.detail.id) {
        handlePatientClick(e.detail.id)
      }
    }

    const handleChangePage = (e) => {
      if (e.detail) {
        fetchPatients(e.detail.q, e.detail.page)
      }
    }

    window.addEventListener('open-patient-detail', handleOpenDetail)
    window.addEventListener('change-page', handleChangePage)

    return () => {
      window.removeEventListener('open-patient-detail', handleOpenDetail)
      window.removeEventListener('change-page', handleChangePage)
    }
  }, [])

  return (
    <div className="page patients">
      {selectedPatientId && (
        <PatientDetailModal
          patientId={selectedPatientId}
          onClose={() => setSelectedPatientId(null)}
        />
      )}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
        <h1>Patients</h1>
      </div>

      <Card title="Patient Management">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
          <form onSubmit={handleSearch} style={{ display: 'flex', gap: '0.5rem', flex: 1, maxWidth: '600px' }}>
            <Input
              placeholder="Search by name or MRN..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              style={{ flex: 1 }}
            />
            <Button type="submit">Search</Button>
            {searchQuery && (
              <Button
                onClick={() => { setSearchQuery(''); fetchPatients('') }}
                variant="secondary"
              >
                Clear
              </Button>
            )}
          </form>
          <Button onClick={() => setShowAddModal(true)}>+ Add Patient</Button>
        </div>

        {loading && <div className="muted">Loading patients...</div>}
        {error && <div style={{ color: '#dc3545', padding: '1rem' }}>{error}</div>}
        {!loading && !error && fragmentHtml && (
          <div id="patients-fragment" dangerouslySetInnerHTML={{ __html: fragmentHtml }} />
        )}
      </Card>

      {showAddModal && (
        <Modal title="Add New Patient" onClose={() => setShowAddModal(false)}>
          <form onSubmit={handleAddPatient} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <div>
              <label htmlFor="mrn">Medical Record Number (MRN) *</label>
              <Input
                id="mrn"
                required
                value={formData.mrn}
                onChange={(e) => setFormData({ ...formData, mrn: e.target.value })}
                placeholder="e.g., MRN123456"
              />
            </div>
            <div>
              <label htmlFor="first_name">First Name *</label>
              <Input
                id="first_name"
                required
                value={formData.first_name}
                onChange={(e) => setFormData({ ...formData, first_name: e.target.value })}
              />
            </div>
            <div>
              <label htmlFor="last_name">Last Name *</label>
              <Input
                id="last_name"
                required
                value={formData.last_name}
                onChange={(e) => setFormData({ ...formData, last_name: e.target.value })}
              />
            </div>
            <div>
              <label htmlFor="date_of_birth">Date of Birth</label>
              <Input
                id="date_of_birth"
                type="date"
                value={formData.date_of_birth}
                onChange={(e) => setFormData({ ...formData, date_of_birth: e.target.value })}
              />
            </div>
            <div style={{ display: 'flex', gap: '0.5rem', justifyContent: 'flex-end' }}>
              <Button type="button" onClick={() => setShowAddModal(false)} variant="secondary">
                Cancel
              </Button>
              <Button type="submit" disabled={submitting}>
                {submitting ? 'Creating...' : 'Create Patient'}
              </Button>
            </div>
          </form>
        </Modal>
      )}
    </div>
  )
}
