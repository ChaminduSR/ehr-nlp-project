import React, { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../ehr/Card';
import { Select } from '../ehr/Input';
import { Button } from '../ehr/Button';

export function Reports() {
  const [reportType, setReportType] = useState('patient-summary');
  const [dateRange, setDateRange] = useState('month');
  
  const reportTypes = [
    { value: 'patient-summary', label: 'Patient Summary Report' },
    { value: 'disease-activity', label: 'Disease Activity Trends' },
    { value: 'medication', label: 'Medication Report' },
    { value: 'visit-summary', label: 'Visit Summary' },
    { value: 'lab-results', label: 'Laboratory Results' },
  ];
  
  const dateRanges = [
    { value: 'week', label: 'Last Week' },
    { value: 'month', label: 'Last Month' },
    { value: 'quarter', label: 'Last Quarter' },
    { value: 'year', label: 'Last Year' },
    { value: 'custom', label: 'Custom Range' },
  ];
  
  // Mock data for demonstration
  const summaryStats = [
    { label: 'Total Patients', value: '156', change: '+12' },
    { label: 'Active Patients', value: '142', change: '+8' },
    { label: 'Average DAS28', value: '3.4', change: '-0.3' },
    { label: 'Remission Rate', value: '28%', change: '+5%' },
  ];
  
  const recentVisits = [
    { date: '2025-11-15', patients: 24, avgDAS28: 3.2 },
    { date: '2025-11-14', patients: 22, avgDAS28: 3.5 },
    { date: '2025-11-13', patients: 26, avgDAS28: 3.1 },
    { date: '2025-11-12', patients: 20, avgDAS28: 3.6 },
    { date: '2025-11-11', patients: 23, avgDAS28: 3.4 },
  ];
  
  const diseaseDistribution = [
    { diagnosis: 'Rheumatoid Arthritis', count: 98, percentage: 63 },
    { diagnosis: 'Psoriatic Arthritis', count: 28, percentage: 18 },
    { diagnosis: 'Ankylosing Spondylitis', count: 18, percentage: 12 },
    { diagnosis: 'Other', count: 12, percentage: 7 },
  ];
  
  return (
    <div className="space-y-6">
      <div>
        <h1>Reports & Analytics</h1>
        <p className="text-[#333333] mt-2">View clinic performance and patient outcomes</p>
      </div>
      
      {/* Report Filters */}
      <Card>
        <CardHeader>
          <CardTitle>Generate Report</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Select
              label="Report Type"
              id="report-type"
              options={reportTypes}
              value={reportType}
              onChange={(e) => setReportType(e.target.value)}
            />
            <Select
              label="Date Range"
              id="date-range"
              options={dateRanges}
              value={dateRange}
              onChange={(e) => setDateRange(e.target.value)}
            />
          </div>
          <div className="flex gap-4 mt-4">
            <Button variant="primary">Generate Report</Button>
            <Button variant="secondary">Export to PDF</Button>
          </div>
        </CardContent>
      </Card>
      
      {/* Summary Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {summaryStats.map((stat, idx) => (
          <Card key={idx}>
            <CardContent>
              <div className="space-y-2">
                <div className="text-sm text-[#333333]">{stat.label}</div>
                <div className="flex items-baseline gap-2">
                  <div className="text-3xl font-medium">{stat.value}</div>
                  <div className={`text-sm ${stat.change.startsWith('+') ? 'text-[#00AA00]' : 'text-[#CC0000]'}`}>
                    {stat.change}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
      
      {/* Recent Visits */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Visit Statistics</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b-2 border-[#CCCCCC]">
                  <th className="text-left py-3 px-4">Date</th>
                  <th className="text-left py-3 px-4">Patients Seen</th>
                  <th className="text-left py-3 px-4">Average DAS28</th>
                </tr>
              </thead>
              <tbody>
                {recentVisits.map((visit, idx) => (
                  <tr key={idx} className="border-b border-[#CCCCCC]">
                    <td className="py-3 px-4">{visit.date}</td>
                    <td className="py-3 px-4">{visit.patients}</td>
                    <td className="py-3 px-4">{visit.avgDAS28.toFixed(1)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
      
      {/* Disease Distribution */}
      <Card>
        <CardHeader>
          <CardTitle>Patient Distribution by Diagnosis</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {diseaseDistribution.map((disease, idx) => (
              <div key={idx}>
                <div className="flex items-center justify-between mb-2">
                  <span className="font-medium">{disease.diagnosis}</span>
                  <span className="text-[#333333]">{disease.count} patients ({disease.percentage}%)</span>
                </div>
                <div className="w-full h-8 bg-[#F5F5F5] border-2 border-[#CCCCCC] rounded overflow-hidden">
                  <div
                    className="h-full bg-[#0066CC]"
                    style={{ width: `${disease.percentage}%` }}
                  ></div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
      
      {/* DAS28 Distribution */}
      <Card>
        <CardHeader>
          <CardTitle>Disease Activity Distribution</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="font-medium">Remission (<2.6)</span>
                <span className="text-[#00AA00]">44 patients (28%)</span>
              </div>
              <div className="w-full h-8 bg-[#F5F5F5] border-2 border-[#CCCCCC] rounded overflow-hidden">
                <div className="h-full bg-[#00AA00]" style={{ width: '28%' }}></div>
              </div>
            </div>
            
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="font-medium">Low Activity (2.6-3.2)</span>
                <span className="text-[#FFCC00]">39 patients (25%)</span>
              </div>
              <div className="w-full h-8 bg-[#F5F5F5] border-2 border-[#CCCCCC] rounded overflow-hidden">
                <div className="h-full bg-[#FFCC00]" style={{ width: '25%' }}></div>
              </div>
            </div>
            
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="font-medium">Moderate Activity (3.2-5.1)</span>
                <span className="text-[#FF9900]">55 patients (35%)</span>
              </div>
              <div className="w-full h-8 bg-[#F5F5F5] border-2 border-[#CCCCCC] rounded overflow-hidden">
                <div className="h-full bg-[#FF9900]" style={{ width: '35%' }}></div>
              </div>
            </div>
            
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="font-medium">High Activity (>5.1)</span>
                <span className="text-[#CC0000]">18 patients (12%)</span>
              </div>
              <div className="w-full h-8 bg-[#F5F5F5] border-2 border-[#CCCCCC] rounded overflow-hidden">
                <div className="h-full bg-[#CC0000]" style={{ width: '12%' }}></div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
      
      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Quick Export Options</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Button variant="secondary" fullWidth>Export Patient List</Button>
            <Button variant="secondary" fullWidth>Export Visit Data</Button>
            <Button variant="secondary" fullWidth>Export Lab Results</Button>
            <Button variant="secondary" fullWidth>Export Medication Report</Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
