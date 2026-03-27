import React, { useState } from 'react';
import { Table } from '../ehr/Table';
import { Button } from '../ehr/Button';
import { Input } from '../ehr/Input';
import { Modal } from '../ehr/Modal';

interface Patient {
  id: string;
  name: string;
  mrn: string;
  age: number;
  gender: string;
  phone: string;
  diagnosis: string;
  lastVisit: string;
  das28: number;
}

const MOCK_PATIENTS: Patient[] = [
  {
    id: '1',
    name: 'Rajesh Kumar',
    mrn: 'MRN-2025-001',
    age: 52,
    gender: 'Male',
    phone: '9876543210',
    diagnosis: 'Rheumatoid Arthritis',
    lastVisit: '2025-11-15',
    das28: 3.5,
  },
  {
    id: '2',
    name: 'Priya Sharma',
    mrn: 'MRN-2025-002',
    age: 45,
    gender: 'Female',
    phone: '9876543211',
    diagnosis: 'Rheumatoid Arthritis',
    lastVisit: '2025-11-15',
    das28: 2.4,
  },
  {
    id: '3',
    name: 'Amit Patel',
    mrn: 'MRN-2025-003',
    age: 58,
    gender: 'Male',
    phone: '9876543212',
    diagnosis: 'Psoriatic Arthritis',
    lastVisit: '2025-11-14',
    das28: 5.8,
  },
  {
    id: '4',
    name: 'Sunita Devi',
    mrn: 'MRN-2025-004',
    age: 48,
    gender: 'Female',
    phone: '9876543213',
    diagnosis: 'Rheumatoid Arthritis',
    lastVisit: '2025-11-14',
    das28: 3.9,
  },
  {
    id: '5',
    name: 'Mohammed Ali',
    mrn: 'MRN-2025-005',
    age: 61,
    gender: 'Male',
    phone: '9876543214',
    diagnosis: 'Ankylosing Spondylitis',
    lastVisit: '2025-11-13',
    das28: 2.1,
  },
];

export function PatientManagement() {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedPatient, setSelectedPatient] = useState<Patient | null>(null);
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  
  const getDAS28Badge = (score: number) => {
    if (score < 2.6) return <span className="px-2 py-1 bg-[#00AA00] text-white rounded text-sm">{score.toFixed(1)}</span>;
    if (score < 3.2) return <span className="px-2 py-1 bg-[#FFCC00] text-black rounded text-sm">{score.toFixed(1)}</span>;
    if (score <= 5.1) return <span className="px-2 py-1 bg-[#FF9900] text-white rounded text-sm">{score.toFixed(1)}</span>;
    return <span className="px-2 py-1 bg-[#CC0000] text-white rounded text-sm">{score.toFixed(1)}</span>;
  };
  
  const filteredPatients = MOCK_PATIENTS.filter(patient => 
    patient.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    patient.mrn.toLowerCase().includes(searchTerm.toLowerCase()) ||
    patient.phone.includes(searchTerm)
  );
  
  const columns = [
    { header: 'MRN', accessor: 'mrn' as keyof Patient, width: '15%' },
    { header: 'Name', accessor: 'name' as keyof Patient, width: '20%' },
    { header: 'Age/Gender', accessor: (row: Patient) => `${row.age} / ${row.gender}`, width: '15%' },
    { header: 'Phone', accessor: 'phone' as keyof Patient, width: '15%' },
    { header: 'Diagnosis', accessor: 'diagnosis' as keyof Patient, width: '20%' },
    { header: 'Last Visit', accessor: 'lastVisit' as keyof Patient, width: '10%' },
    { header: 'DAS28', accessor: (row: Patient) => getDAS28Badge(row.das28), width: '10%' },
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
                <div className="text-sm text-[#333333]">Gender</div>
                <div className="font-medium">{selectedPatient.gender}</div>
              </div>
              <div>
                <div className="text-sm text-[#333333]">Phone</div>
                <div className="font-medium">{selectedPatient.phone}</div>
              </div>
              <div>
                <div className="text-sm text-[#333333]">Last Visit</div>
                <div className="font-medium">{selectedPatient.lastVisit}</div>
              </div>
              <div className="col-span-2">
                <div className="text-sm text-[#333333]">Diagnosis</div>
                <div className="font-medium">{selectedPatient.diagnosis}</div>
              </div>
              <div className="col-span-2">
                <div className="text-sm text-[#333333]">Current DAS28 Score</div>
                <div className="mt-1">{getDAS28Badge(selectedPatient.das28)}</div>
              </div>
            </div>
            
            <div className="flex gap-4 pt-4 border-t-2 border-[#CCCCCC]">
              <Button variant="primary" fullWidth>
                Create Medical Note
              </Button>
              <Button variant="secondary" fullWidth>
                View History
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
        <form className="space-y-4" onSubmit={(e) => e.preventDefault()}>
          <div className="grid grid-cols-2 gap-4">
            <Input label="First Name" id="first-name" required />
            <Input label="Last Name" id="last-name" required />
            <Input label="Age" type="number" id="age" required />
            <Input label="Gender" id="gender" required />
            <Input label="Phone Number" type="tel" id="phone" required />
            <Input label="Email" type="email" id="email" />
            <div className="col-span-2">
              <Input label="Address" id="address" />
            </div>
            <div className="col-span-2">
              <Input label="Initial Diagnosis" id="diagnosis" />
            </div>
          </div>
          
          <div className="flex gap-4 pt-4 border-t-2 border-[#CCCCCC]">
            <Button type="submit" variant="primary" fullWidth>
              Save Patient
            </Button>
            <Button 
              type="button" 
              variant="secondary" 
              fullWidth
              onClick={() => setIsAddModalOpen(false)}
            >
              Cancel
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
