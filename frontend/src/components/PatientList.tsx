import React from 'react';
import { usePatients } from '../queries';

const PatientList: React.FC = () => {
  const { data: patients, isLoading, error } = usePatients();

  if (isLoading) return <div className="p-4">Loading patients...</div>;
  if (error) return <div className="p-4 text-red-500">Error loading patients</div>;

  return (
    <div className="p-4 bg-white rounded shadow">
      <h2 className="text-2xl font-bold mb-4 text-gray-800">Patients (React + Tailwind)</h2>
      <div className="grid gap-4 grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
        {patients?.map((patient: any) => (
          <div key={patient.id} className="p-4 border rounded shadow-sm hover:bg-blue-50 transition-colors">
            <div className="font-bold text-lg">{patient.last_name}, {patient.first_name}</div>
            <div className="text-sm text-gray-600">MRN: {patient.mrn}</div>
            <div className="text-sm text-gray-600">DOB: {patient.date_of_birth}</div>
            {patient.latest_visit_id && (
                <div className="mt-2 text-xs bg-green-100 text-green-800 px-2 py-1 rounded inline-block">
                    Active
                </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default PatientList;
