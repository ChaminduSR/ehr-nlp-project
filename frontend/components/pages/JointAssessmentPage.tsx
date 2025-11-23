import { useState, useEffect } from 'react';
import { Button } from '../ehr/Button';
import { Input } from '../ehr/Input';
import { Card, CardHeader, CardTitle, CardContent } from '../ehr/Card';
import { JointAssessment } from '../ehr/JointAssessment';
import { DAS28Calculator } from '../ehr/DAS28Score';
import { api } from '../../services/api';
import { useApp } from '../../contexts/AppContext';
import type { JointAssessment as JointAssessmentType } from '../../types';

export function JointAssessmentPage() {
  const { currentPatient, currentVisit, setError, isLoading, setIsLoading } = useApp();
  const [esr, setEsr] = useState(25);
  const [patientGlobal, setPatientGlobal] = useState(50);
  const [tenderCount, setTenderCount] = useState(0);
  const [swollenCount, setSwollenCount] = useState(0);
  const [joints, setJoints] = useState<any[]>([]);
  const [savedAssessments, setSavedAssessments] = useState<JointAssessmentType[]>([]);

  // Load existing assessments if visit exists
  useEffect(() => {
    if (currentVisit) {
      loadExistingAssessments();
    }
  }, [currentVisit]);

  const loadExistingAssessments = async () => {
    if (!currentVisit) return;

    setIsLoading(true);
    try {
      const response = await api.getJointAssessmentsByVisit(currentVisit.id);
      setSavedAssessments(response.joints);

      // Calculate tender/swollen counts from loaded data
      const tender = response.joints.filter(j => j.has_tenderness).length;
      const swollen = response.joints.filter(j => j.swelling_grade > 0).length;
      setTenderCount(tender);
      setSwollenCount(swollen);
    } catch (err: any) {
      // It's okay if no assessments exist yet
      console.log('No existing assessments:', err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleJointsChange = (jointsData: any[]) => {
    setJoints(jointsData);
    const tender = jointsData.filter(j => j.tenderness).length;
    const swollen = jointsData.filter(j => j.swelling > 0).length;
    setTenderCount(tender);
    setSwollenCount(swollen);
  };

  const handleSaveAssessment = async () => {
    if (!currentVisit) {
      alert('No active visit. Please create a visit first.');
      return;
    }

    if (joints.length === 0) {
      alert('Please assess at least one joint before saving.');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      // Convert UI joint format to backend format
      const jointAssessments = joints.map(j => ({
        visit_id: currentVisit.id,
        joint_id: j.id,
        has_tenderness: j.tenderness || false,
        has_pain: j.tenderness || false, // Using tenderness as pain indicator
        swelling_grade: (j.swelling || 0) as 0 | 1 | 2 | 3,
      }));

      const response = await api.saveJointAssessment(currentVisit.id, jointAssessments);

      alert(`Joint assessment saved successfully!\n${response.joints_saved} joints recorded.`);

      // Reload to see saved data
      await loadExistingAssessments();
    } catch (err: any) {
      setError(err.message || 'Failed to save joint assessment');
      alert('Error saving assessment: ' + (err.message || 'Unknown error'));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1>Joint Assessment</h1>
        <p className="text-[#333333] mt-2">Interactive 28-joint assessment for rheumatoid arthritis</p>
      </div>

      {/* Patient Info */}
      {!currentPatient && (
        <div className="p-4 bg-yellow-50 border-2 border-yellow-300 rounded">
          <p className="text-yellow-800">No patient selected. Please select a patient from Patient Management first.</p>
        </div>
      )}

      {!currentVisit && currentPatient && (
        <div className="p-4 bg-yellow-50 border-2 border-yellow-300 rounded">
          <p className="text-yellow-800">No active visit. Please create a visit for this patient first.</p>
        </div>
      )}

      {currentPatient && currentVisit && (
        <>
          <Card>
            <CardHeader>
              <CardTitle>Patient Information</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div>
                  <div className="text-sm text-[#333333]">MRN</div>
                  <div className="font-medium">{currentPatient.mrn}</div>
                </div>
                <div>
                  <div className="text-sm text-[#333333]">Patient Name</div>
                  <div className="font-medium">{currentPatient.first_name} {currentPatient.last_name}</div>
                </div>
                <div>
                  <div className="text-sm text-[#333333]">Visit Date</div>
                  <div className="font-medium">{currentVisit.visit_date}</div>
                </div>
                <div>
                  <div className="text-sm text-[#333333]">Visit Type</div>
                  <div className="font-medium">{currentVisit.visit_type}</div>
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
            <Button
              variant="success"
              fullWidth
              onClick={handleSaveAssessment}
              disabled={isLoading || joints.length === 0}
            >
              {isLoading ? 'Saving...' : 'Save Assessment'}
            </Button>
          </div>

          {savedAssessments.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Previously Saved Assessments</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-[#666666]">
                  {savedAssessments.length} joint(s) previously assessed for this visit.
                </p>
              </CardContent>
            </Card>
          )}

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
                    <div className="font-medium">Remission: DAS28 &lt; 2.6</div>
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
                    <div className="font-medium">High Activity: DAS28 &gt; 5.1</div>
                    <div className="text-sm text-[#333333]">Severe disease activity</div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </>
      )}
    </div>
  );
}
