import React, { useState, useEffect } from 'react';
import { Table } from '../ehr/Table';
import { Button } from '../ehr/Button';
import { Input } from '../ehr/Input';
import { Modal } from '../ehr/Modal';
import { api } from '../../services/api';
import { useApp } from '../../contexts/AppContext';
// Removed unused type import `Patient` to avoid TS6133; re-add when used.

// Display patient with combined name for UI
interface DisplayPatient {
  id: number;
  name: string;
  mrn: string;
  age: number;
  date_of_birth: string;
  created_at: string;
}

export function PatientManagement() {
  const { setCurrentPatient, isLoading, setIsLoading, error, setError } = useApp();
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedPatient, setSelectedPatient] = useState<DisplayPatient | null>(null);
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [patients, setPatients] = useState<DisplayPatient[]>([]);
  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    mrn: '',
    dateOfBirth: '',
  });

  // Note: Backend doesn't have GET /patients endpoint yet
  // For now, patients array will be populated when we create new patients
  useEffect(() => {
    // You can add api.healthCheck() here to verify backend is running
    api.healthCheck().catch(err => setError('Backend not reachable: ' + err.message));
  }, []);

  const calculateAge = (dob: string) => {
    const birthDate = new Date(dob);
    const today = new Date();
    let age = today.getFullYear() - birthDate.getFullYear();
    const monthDiff = today.getMonth() - birthDate.getMonth();
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
      age--;
    }
    return age;
  };

  const handleAddPatient = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      const response = await api.createPatient({
        mrn: formData.mrn,
        first_name: formData.firstName,
        last_name: formData.lastName,
        date_of_birth: formData.dateOfBirth,
      });

      // Fetch the created patient
      const createdPatient = await api.getPatient(response.id);

      // Add to local state
      const displayPatient: DisplayPatient = {
        ...createdPatient,
        name: `${createdPatient.first_name} ${createdPatient.last_name}`,
        age: calculateAge(createdPatient.date_of_birth),
      };

      setPatients(prev => [...prev, displayPatient]);
      setCurrentPatient(createdPatient);

      // Reset form
      setFormData({ firstName: '', lastName: '', mrn: '', dateOfBirth: '' });
      setIsAddModalOpen(false);

      alert(`Patient ${displayPatient.name} created successfully!`);
    } catch (err: any) {
      setError(err.message || 'Failed to create patient');
      alert('Error creating patient: ' + (err.message || 'Unknown error'));
    } finally {
      setIsLoading(false);
    }
  };

  const filteredPatients = patients.filter(patient =>
    patient.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    patient.mrn.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const columns = [
    { header: 'MRN', accessor: 'mrn' as keyof DisplayPatient, width: '20%' },
    { header: 'Name', accessor: 'name' as keyof DisplayPatient, width: '25%' },
    { header: 'Age', accessor: 'age' as keyof DisplayPatient, width: '15%' },
    { header: 'Date of Birth', accessor: 'date_of_birth' as keyof DisplayPatient, width: '20%' },
    { header: 'Created', accessor: (row: DisplayPatient) => new Date(row.created_at).toLocaleDateString(), width: '20%' },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1>Patient Management</h1>
        <p className="text-[#333333] mt-2">Search and manage patient records</p>
      </div>

      {/* Search and Actions */}
      <div className="flex flex-col md:flex-row gap-4">
        <div className="flex-1">
          <Input
            placeholder="Search by name, MRN, or phone number..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            id="patient-search"
          />
        </div>
        <Button onClick={() => setIsAddModalOpen(true)}>
          Add New Patient
        </Button>
      </div>

      {/* Results Count */}
      <div className="text-[#333333]">
        Found {filteredPatients.length} patient{filteredPatients.length !== 1 ? 's' : ''}
      </div>

      {/* Patients Table */}
      <Table
        columns={columns}
        data={filteredPatients}
        onRowClick={(patient) => setSelectedPatient(patient)}
        emptyMessage="No patients found. Try a different search term."
      />

      {/* Patient Details Modal */}
      {selectedPatient && (
        <Modal
          isOpen={!!selectedPatient}
          onClose={() => setSelectedPatient(null)}
          title="Patient Details"
          size="large"
        >
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <div className="text-sm text-[#333333]">MRN</div>
                <div className="font-medium">{selectedPatient.mrn}</div>
              </div>
              <div>
                <div className="text-sm text-[#333333]">Name</div>
                <div className="font-medium">{selectedPatient.name}</div>
              </div>
              <div>
                <div className="text-sm text-[#333333]">Age</div>
                <div className="font-medium">{selectedPatient.age} years</div>
              </div>
              <div>
                <div className="text-sm text-[#333333]">Date of Birth</div>
                <div className="font-medium">{selectedPatient.date_of_birth}</div>
              </div>
              <div className="col-span-2">
                <div className="text-sm text-[#333333]">Created At</div>
                <div className="font-medium">{new Date(selectedPatient.created_at).toLocaleString()}</div>
              </div>
            </div>

            <div className="flex gap-4 pt-4 border-t-2 border-[#CCCCCC]">
              <Button variant="primary" fullWidth>
                Create Visit
              </Button>
              <Button variant="secondary" fullWidth onClick={() => setSelectedPatient(null)}>
                Close
              </Button>
            </div>
          </div>
        </Modal>
      )}

      {/* Add Patient Modal */}
      <Modal
        isOpen={isAddModalOpen}
        onClose={() => setIsAddModalOpen(false)}
        title="Add New Patient"
        size="large"
      >
        <form className="space-y-4" onSubmit={handleAddPatient}>
          {error && (
            <div className="p-4 bg-red-50 border-2 border-red-300 rounded text-red-800">
              {error}
            </div>
          )}

          <div className="grid grid-cols-2 gap-4">
            <Input
              label="First Name"
              id="first-name"
              required
              value={formData.firstName}
              onChange={(e) => setFormData(prev => ({ ...prev, firstName: e.target.value }))}
              disabled={isLoading}
            />
            <Input
              label="Last Name"
              id="last-name"
              required
              value={formData.lastName}
              onChange={(e) => setFormData(prev => ({ ...prev, lastName: e.target.value }))}
              disabled={isLoading}
            />
            <Input
              label="MRN (Medical Record Number)"
              id="mrn"
              required
              placeholder="MRN-2025-001"
              value={formData.mrn}
              onChange={(e) => setFormData(prev => ({ ...prev, mrn: e.target.value }))}
              disabled={isLoading}
            />
            <Input
              label="Date of Birth"
              type="date"
              id="dob"
              required
              value={formData.dateOfBirth}
              onChange={(e) => setFormData(prev => ({ ...prev, dateOfBirth: e.target.value }))}
              disabled={isLoading}
            />
          </div>

          <div className="flex gap-4 pt-4 border-t-2 border-[#CCCCCC]">
            <Button type="submit" variant="primary" fullWidth disabled={isLoading}>
              {isLoading ? 'Creating...' : 'Create Patient'}
            </Button>
            <Button
              type="button"
              variant="secondary"
              fullWidth
              onClick={() => {
                setIsAddModalOpen(false);
                setError(null);
              }}
              disabled={isLoading}
            >
              Cancel
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
