import React, { useState } from 'react';
import { Button } from '../ehr/Button';
import { Input } from '../ehr/Input';
import { Card, CardHeader, CardTitle, CardContent } from '../ehr/Card';
import { JointAssessment } from '../ehr/JointAssessment';
import { DAS28Calculator } from '../ehr/DAS28Score';

export function JointAssessmentPage() {
  const [esr, setEsr] = useState(25);
  const [patientGlobal, setPatientGlobal] = useState(50);
  const [tenderCount, setTenderCount] = useState(0);
  const [swollenCount, setSwollenCount] = useState(0);
  
  const handleJointsChange = (joints: any[]) => {
    const tender = joints.filter(j => j.tenderness).length;
    const swollen = joints.filter(j => j.swelling > 0).length;
    setTenderCount(tender);
    setSwollenCount(swollen);
  };
  
  return (
    <div className="space-y-6">
      <div>
        <h1>Joint Assessment</h1>
        <p className="text-[#333333] mt-2">Interactive 28-joint assessment for rheumatoid arthritis</p>
      </div>
      
      {/* Patient Info */}
      <Card>
        <CardHeader>
          <CardTitle>Patient Information</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <div className="text-sm text-[#333333]">MRN</div>
              <div className="font-medium">MRN-2025-001</div>
            </div>
            <div>
              <div className="text-sm text-[#333333]">Patient Name</div>
              <div className="font-medium">Rajesh Kumar</div>
            </div>
            <div>
              <div className="text-sm text-[#333333]">Date</div>
              <div className="font-medium">15 Nov 2025</div>
            </div>
            <div>
              <div className="text-sm text-[#333333]">Provider</div>
              <div className="font-medium">Dr. Singh</div>
            </div>
          </div>
        </CardContent>
      </Card>
      
      {/* Joint Assessment Canvas */}
      <Card>
        <CardContent>
          <JointAssessment onChange={handleJointsChange} />
        </CardContent>
      </Card>
      
      {/* Lab Values */}
      <Card>
        <CardHeader>
          <CardTitle>Additional Assessment Data</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Input
              label="ESR (mm/hr)"
              type="number"
              id="esr"
              value={esr}
              onChange={(e) => setEsr(Number(e.target.value))}
              helperText="Normal range: 0-20 mm/hr for men, 0-30 mm/hr for women"
            />
            <Input
              label="Patient Global Assessment (0-100)"
              type="number"
              id="patient-global"
              min="0"
              max="100"
              value={patientGlobal}
              onChange={(e) => setPatientGlobal(Number(e.target.value))}
              helperText="0 = Very well, 100 = Very poor"
            />
          </div>
        </CardContent>
      </Card>
      
      {/* DAS28 Calculation */}
      <Card>
        <CardHeader>
          <CardTitle>DAS28-ESR Calculation</CardTitle>
        </CardHeader>
        <CardContent>
          <DAS28Calculator
            tenderJointCount={tenderCount}
            swollenJointCount={swollenCount}
            esr={esr}
            patientGlobal={patientGlobal}
          />
        </CardContent>
      </Card>
      
      {/* Actions */}
      <div className="flex gap-4">
        <Button variant="success" fullWidth>
          Save Assessment
        </Button>
        <Button variant="secondary" fullWidth>
          Cancel
        </Button>
      </div>
      
      {/* Reference Information */}
      <Card>
        <CardHeader>
          <CardTitle>DAS28-ESR Reference</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <div className="flex items-center gap-3">
              <div className="w-16 h-8 bg-[#00AA00] rounded"></div>
              <div>
                <div className="font-medium">Remission: DAS28 < 2.6</div>
                <div className="text-sm text-[#333333]">Disease under control</div>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <div className="w-16 h-8 bg-[#FFCC00] rounded"></div>
              <div>
                <div className="font-medium">Low Activity: DAS28 2.6 - 3.2</div>
                <div className="text-sm text-[#333333]">Mild disease activity</div>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <div className="w-16 h-8 bg-[#FF9900] rounded"></div>
              <div>
                <div className="font-medium">Moderate Activity: DAS28 3.2 - 5.1</div>
                <div className="text-sm text-[#333333]">Moderate disease activity</div>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <div className="w-16 h-8 bg-[#CC0000] rounded"></div>
              <div>
                <div className="font-medium">High Activity: DAS28 > 5.1</div>
                <div className="text-sm text-[#333333]">Severe disease activity</div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
