import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../ehr/Card';

export function Dashboard() {
  const stats = [
    { label: 'Patients Today', value: '24', color: 'text-[#0066CC]' },
    { label: 'Pending Notes', value: '7', color: 'text-[#FF9900]' },
    { label: 'Active Patients', value: '156', color: 'text-[#00AA00]' },
    { label: 'Follow-ups Due', value: '12', color: 'text-[#CC0000]' },
  ];
  
  const recentPatients = [
    { id: 1, name: 'Rajesh Kumar', mrn: 'MRN-2025-001', lastVisit: '2025-11-15', das28: 3.5 },
    { id: 2, name: 'Priya Sharma', mrn: 'MRN-2025-002', lastVisit: '2025-11-15', das28: 2.4 },
    { id: 3, name: 'Amit Patel', mrn: 'MRN-2025-003', lastVisit: '2025-11-14', das28: 5.8 },
    { id: 4, name: 'Sunita Devi', mrn: 'MRN-2025-004', lastVisit: '2025-11-14', das28: 3.9 },
  ];
  
  const getDAS28Color = (score: number) => {
    if (score < 2.6) return 'text-[#00AA00]';
    if (score < 3.2) return 'text-[#FFCC00]';
    if (score <= 5.1) return 'text-[#FF9900]';
    return 'text-[#CC0000]';
  };
  
  return (
    <div className="space-y-6">
      <div>
        <h1>Dashboard</h1>
        <p className="text-[#333333] mt-2">Welcome back, Dr. Singh</p>
      </div>
      
      {/* Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((stat, idx) => (
          <Card key={idx}>
            <CardContent>
              <div className="space-y-2">
                <div className="text-sm text-[#333333]">{stat.label}</div>
                <div className={`text-3xl font-medium ${stat.color}`}>{stat.value}</div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
      
      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <button className="h-16 px-6 border-2 border-[#0066CC] bg-[#0066CC] text-white rounded hover:bg-[#004C99]">
              New Patient Visit
            </button>
            <button className="h-16 px-6 border-2 border-[#CCCCCC] bg-white text-black rounded hover:bg-[#F5F5F5]">
              Search Patient
            </button>
            <button className="h-16 px-6 border-2 border-[#CCCCCC] bg-white text-black rounded hover:bg-[#F5F5F5]">
              View Reports
            </button>
            <button className="h-16 px-6 border-2 border-[#CCCCCC] bg-white text-black rounded hover:bg-[#F5F5F5]">
              Clinic Schedule
            </button>
          </div>
        </CardContent>
      </Card>
      
      {/* Recent Patients */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Patients</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {recentPatients.map(patient => (
              <div
                key={patient.id}
                className="p-4 border-2 border-[#CCCCCC] rounded hover:bg-[#F5F5F5] cursor-pointer"
              >
                <div className="flex justify-between items-start">
                  <div>
                    <div className="font-medium">{patient.name}</div>
                    <div className="text-sm text-[#333333]">{patient.mrn}</div>
                    <div className="text-sm text-[#333333]">Last visit: {patient.lastVisit}</div>
                  </div>
                  <div className="text-right">
                    <div className="text-sm text-[#333333]">DAS28</div>
                    <div className={`text-xl font-medium ${getDAS28Color(patient.das28)}`}>
                      {patient.das28.toFixed(1)}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
      
      {/* System Status */}
      <Card>
        <CardHeader>
          <CardTitle>System Status</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span>Offline Mode</span>
              <span className="px-3 py-1 bg-[#00AA00] text-white rounded">Active</span>
            </div>
            <div className="flex items-center justify-between">
              <span>Data Sync</span>
              <span className="px-3 py-1 bg-[#00AA00] text-white rounded">Up to date</span>
            </div>
            <div className="flex items-center justify-between">
              <span>Last Backup</span>
              <span className="text-[#333333]">15 Nov 2025, 09:30</span>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
