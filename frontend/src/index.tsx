import htmx from 'htmx.org';
import Alpine from 'alpinejs';
import React from 'react';
import { createRoot } from 'react-dom/client';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import Konva from 'konva';
import PatientList from './components/PatientList';

// Import Modules
import { medicalNote } from './modules/medical_note_logic';
import { patientsManager } from './modules/patients_logic';
import { jointAssessment } from './modules/joint_assessment_logic';
import { jointAssessmentFragment } from './modules/joint_assessment_fragment';
import { initDashboard } from './modules/dashboard_logic';
import { initReports } from './modules/reports_logic';
import { JointDiagram } from './modules/joint_diagram';
import { VoiceRecorder } from './modules/voice_recorder';

// Expose globals for legacy support or inline scripts
window.Alpine = Alpine;
window.htmx = htmx;
window.JointDiagram = JointDiagram;
window.VoiceRecorder = VoiceRecorder;
window.Konva = Konva;

// Register Alpine Data Components
Alpine.data('medicalNote', medicalNote);
Alpine.data('patientsManager', patientsManager);
Alpine.data('jointAssessment', jointAssessment);
Alpine.data('jointAssessmentFragment', jointAssessmentFragment);

// Initialize Logic
initDashboard(Alpine);
initReports(Alpine);

// Start Alpine
Alpine.start();

// React Mount
const queryClient = new QueryClient();
const patientListRoot = document.getElementById('react-patient-list');
if (patientListRoot) {
  const root = createRoot(patientListRoot);
  root.render(
    <QueryClientProvider client={queryClient}>
      <PatientList />
    </QueryClientProvider>
  );
}
