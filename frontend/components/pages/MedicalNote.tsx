import React, { useState, useEffect } from 'react';
import { Button } from '../ehr/Button';
import { Input, Textarea, Select } from '../ehr/Input';
import { AutoSaveIndicator } from '../ehr/AutoSaveIndicator';
import { Card, CardHeader, CardTitle, CardContent } from '../ehr/Card';

type SaveStatus = 'saving' | 'saved' | 'error';
type NoteStatus = 'draft' | 'finalized';

export function MedicalNote() {
  const [saveStatus, setSaveStatus] = useState<SaveStatus>('saved');
  const [lastSaved, setLastSaved] = useState<Date>(new Date());
  const [noteStatus, setNoteStatus] = useState<NoteStatus>('draft');
  const [formData, setFormData] = useState({
    patientMRN: 'MRN-2025-001',
    patientName: 'Rajesh Kumar',
    chiefComplaint: '',
    historyPresentIllness: '',
    physicalExam: '',
    assessment: '',
    plan: '',
    medications: '',
    followUp: '',
  });
  
  // Auto-save every 30 seconds
  useEffect(() => {
    if (noteStatus === 'draft') {
      const interval = setInterval(() => {
        handleAutoSave();
      }, 30000); // 30 seconds
      
      return () => clearInterval(interval);
    }
  }, [formData, noteStatus]);
  
  const handleAutoSave = () => {
    setSaveStatus('saving');
    
    // Simulate save operation
    setTimeout(() => {
      setSaveStatus('saved');
      setLastSaved(new Date());
      console.log('Auto-saved:', formData);
    }, 500);
  };
  
  const handleChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    
    // Trigger auto-save status
    if (saveStatus === 'saved') {
      setSaveStatus('saving');
      setTimeout(() => {
        setSaveStatus('saved');
        setLastSaved(new Date());
      }, 1000);
    }
  };
  
  const handleFinalize = () => {
    if (window.confirm('Are you sure you want to finalize this note? Finalized notes cannot be edited.')) {
      setSaveStatus('saving');
      setTimeout(() => {
        setNoteStatus('finalized');
        setSaveStatus('saved');
        setLastSaved(new Date());
        alert('Medical note has been finalized successfully.');
      }, 500);
    }
  };
  
  const handleSaveDraft = () => {
    handleAutoSave();
    alert('Draft saved successfully.');
  };
  
  const isFinalized = noteStatus === 'finalized';
  
  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between">
        <div>
          <h1>Medical Note</h1>
          <p className="text-[#333333] mt-2">Create comprehensive rheumatology assessment</p>
        </div>
        <AutoSaveIndicator status={saveStatus} lastSaved={lastSaved} />
      </div>
      
      {/* Patient Info */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Patient Information</CardTitle>
            {noteStatus === 'finalized' ? (
              <span className="px-4 py-2 bg-[#00AA00] text-white rounded">
                Finalized
              </span>
            ) : (
              <span className="px-4 py-2 bg-[#FF9900] text-white rounded">
                Draft
              </span>
            )}
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <div className="text-sm text-[#333333]">MRN</div>
              <div className="font-medium">{formData.patientMRN}</div>
            </div>
            <div>
              <div className="text-sm text-[#333333]">Patient Name</div>
              <div className="font-medium">{formData.patientName}</div>
            </div>
            <div>
              <div className="text-sm text-[#333333]">Date</div>
              <div className="font-medium">15 November 2025</div>
            </div>
            <div>
              <div className="text-sm text-[#333333]">Provider</div>
              <div className="font-medium">Dr. Singh</div>
            </div>
          </div>
        </CardContent>
      </Card>
      
      {/* Note Form */}
      <form className="space-y-6" onSubmit={(e) => e.preventDefault()}>
        <Card>
          <CardHeader>
            <CardTitle>Chief Complaint</CardTitle>
          </CardHeader>
          <CardContent>
            <Input
              id="chief-complaint"
              placeholder="Enter chief complaint..."
              value={formData.chiefComplaint}
              onChange={(e) => handleChange('chiefComplaint', e.target.value)}
              disabled={isFinalized}
            />
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader>
            <CardTitle>History of Present Illness</CardTitle>
          </CardHeader>
          <CardContent>
            <Textarea
              id="history-present-illness"
              placeholder="Document patient's history..."
              rows={6}
              value={formData.historyPresentIllness}
              onChange={(e) => handleChange('historyPresentIllness', e.target.value)}
              disabled={isFinalized}
            />
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader>
            <CardTitle>Physical Examination</CardTitle>
          </CardHeader>
          <CardContent>
            <Textarea
              id="physical-exam"
              placeholder="Document physical examination findings..."
              rows={6}
              value={formData.physicalExam}
              onChange={(e) => handleChange('physicalExam', e.target.value)}
              disabled={isFinalized}
            />
            <div className="mt-4 p-4 bg-[#F5F5F5] border-2 border-[#CCCCCC] rounded">
              <div className="flex items-center justify-between">
                <span>Joint assessment not completed</span>
                <Button variant="secondary" size="default" disabled={isFinalized}>
                  Open Joint Assessment
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader>
            <CardTitle>Assessment</CardTitle>
          </CardHeader>
          <CardContent>
            <Textarea
              id="assessment"
              placeholder="Clinical assessment and diagnosis..."
              rows={6}
              value={formData.assessment}
              onChange={(e) => handleChange('assessment', e.target.value)}
              disabled={isFinalized}
            />
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader>
            <CardTitle>Plan</CardTitle>
          </CardHeader>
          <CardContent>
            <Textarea
              id="plan"
              placeholder="Treatment plan and next steps..."
              rows={6}
              value={formData.plan}
              onChange={(e) => handleChange('plan', e.target.value)}
              disabled={isFinalized}
            />
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader>
            <CardTitle>Medications</CardTitle>
          </CardHeader>
          <CardContent>
            <Textarea
              id="medications"
              placeholder="List medications, dosages, and instructions..."
              rows={4}
              value={formData.medications}
              onChange={(e) => handleChange('medications', e.target.value)}
              disabled={isFinalized}
            />
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader>
            <CardTitle>Follow-up</CardTitle>
          </CardHeader>
          <CardContent>
            <Select
              id="follow-up"
              label="Follow-up Interval"
              options={[
                { value: '', label: 'Select follow-up period...' },
                { value: '1-week', label: '1 Week' },
                { value: '2-weeks', label: '2 Weeks' },
                { value: '1-month', label: '1 Month' },
                { value: '2-months', label: '2 Months' },
                { value: '3-months', label: '3 Months' },
                { value: '6-months', label: '6 Months' },
              ]}
              value={formData.followUp}
              onChange={(e) => handleChange('followUp', e.target.value)}
              disabled={isFinalized}
            />
          </CardContent>
        </Card>
        
        {/* Actions */}
        {!isFinalized && (
          <div className="flex gap-4">
            <Button type="button" variant="draft" fullWidth onClick={handleSaveDraft}>
              Save Draft
            </Button>
            <Button type="button" variant="success" fullWidth onClick={handleFinalize}>
              Finalize Note
            </Button>
          </div>
        )}
        
        {isFinalized && (
          <div className="p-4 bg-[#F5F5F5] border-2 border-[#CCCCCC] rounded">
            <p className="text-center">
              This note has been finalized and cannot be edited. 
              You can print or export this note for records.
            </p>
            <div className="flex gap-4 mt-4">
              <Button type="button" variant="secondary" fullWidth>
                Print Note
              </Button>
              <Button type="button" variant="secondary" fullWidth>
                Export as PDF
              </Button>
            </div>
          </div>
        )}
      </form>
    </div>
  );
}
