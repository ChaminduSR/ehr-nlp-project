import htmx from 'htmx.org';
import Alpine from 'alpinejs';

// Import Modules
import { medicalNote } from './modules/medical_note_logic';
import { patientsManager } from './modules/patients_logic';
import { jointAssessment } from './modules/joint_assessment_logic';
import { jointAssessmentFragment } from './modules/joint_assessment_fragment';
import { initDashboard } from './modules/dashboard_logic';
import { initReports } from './modules/reports_logic';
import { VoiceRecorder } from './modules/voice_recorder';

// Expose globals for legacy support or inline scripts
window.Alpine = Alpine;
window.htmx = htmx;
window.VoiceRecorder = VoiceRecorder;

// Lazy-load JointDiagram (includes Konva) - only loaded when needed
window.loadJointDiagram = async () => {
  if (!window.JointDiagram) {
    const { JointDiagram } = await import(/* webpackChunkName: "joint-diagram" */ './modules/joint_diagram');
    window.JointDiagram = JointDiagram;
  }
  return window.JointDiagram;
};

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

// HTMX + Alpine Integration: Initialize Alpine on new HTMX content
document.body.addEventListener('htmx:afterSwap', (event: Event) => {
  const target = (event as CustomEvent).detail?.target;
  if (target) {
    Alpine.initTree(target);
  }
});
