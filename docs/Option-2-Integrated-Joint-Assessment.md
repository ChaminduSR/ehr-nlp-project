# 🏥 INTEGRATED JOINT ASSESSMENT + MEDICAL NOTES UX
## Option 2: Collapsible Side Panel Implementation Guide

**Version:** 1.0  
**Date:** December 6, 2025  
**For:** Rural Rheumatology EHR v3.2  
**Status:** Ready for Implementation

---

## 📋 OVERVIEW

This document details **Option 2: Collapsible Side Panel** - the recommended layout for integrating joint assessment into the medical notes page.

### Why Option 2?

| Criteria | Rating | Why |
|----------|--------|-----|
| **Speed** | ⭐⭐⭐⭐⭐ | No tab clicks; glance + click workflow |
| **Accessibility** | ⭐⭐⭐⭐ | Keyboard shortcuts available |
| **Rural Clinic Friendly** | ⭐⭐⭐⭐⭐ | Works on 10-year-old PCs with 2GB RAM |
| **Mobile/Tablet Support** | ⭐⭐⭐⭐ | Responsive collapse on tablets |
| **Clinical Workflow** | ⭐⭐⭐⭐⭐ | Matches real doctor behavior |
| **Screen Real Estate** | ⭐⭐⭐⭐ | 70% content : 30% assessment panel |

---

## 🎨 VISUAL LAYOUT

```
┌──────────────────────────────────────────────────────────┐
│ Medical Note                          [≡ Collapse/Expand] │
├──────────────────────────┬────────────────────────────────┤
│                          │                                 │
│  DICTATION SECTION       │  JOINT ASSESSMENT PANEL        │
│  (70% width)             │  (30% width - Sticky)          │
│                          │                                 │
│  Patient Info Card       │  ┌────────────────────────┐   │
│  ▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔   │  │ Joint Assessment       │   │
│  MRN: 001                │  │                        │   │
│  Name: Ramesh K          │  │ Mode Selection:        │   │
│  Age: 45M                │  │ □ Tenderness          │   │
│  ────────────────────    │  │ ☑ Swelling             │   │
│                          │  │ □ Pain                │   │
│  Dictation Input Area:   │  │                        │   │
│  ┌────────────────────┐  │  │ ┌──────────────────┐  │   │
│  │ "Patient presents  │  │  │ │                  │  │   │
│  │ with swelling in   │  │  │ │   [Joint Map]    │  │   │
│  │ hands and knees,   │  │  │ │   (Konva Canvas) │  │   │
│  │ ESR 20, patient    │  │  │ │   300x400px      │  │   │
│  │ global 50/100      │  │  │ │                  │  │   │
│  │                    │  │  │ └──────────────────┘  │   │
│  │ [Record]  [Extract]│  │  │                        │   │
│  │                    │  │  │ Summary Stats:        │   │
│  │ [Auto-save: 12:45] │  │  │ TJC: 6   SJC: 2      │   │
│  │                    │  │  │ ESR: 20  PG: 50      │   │
│  └────────────────────┘  │  │                        │   │
│                          │  │ DAS28: 4.56            │   │
│  Assessment Section:     │  │ Moderate Activity ⚠️   │   │
│  ▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔   │  │                        │   │
│  - Chief Complaint       │  │ [✓ Save Assessment]   │   │
│  - History              │  │                        │   │
│  - Physical Exam        │  │ [← Collapse Panel]     │   │
│  - Assessment           │  │                        │   │
│  - Plan                 │  │                        │   │
│                          │  └────────────────────────┘   │
│  [Save Draft] [Finalize] │                                 │
│                          │                                 │
└──────────────────────────┴────────────────────────────────┘
```

---

## 🔧 IMPLEMENTATION STRUCTURE

### HTML Structure

```html
<!-- Main Medical Note Container -->
<div class="medical-note-wrapper" id="medicalNoteWrapper">
  
  <!-- LEFT SIDE: Dictation & Medical Note Content (70%) -->
  <div class="dictation-section">
    
    <!-- Patient Header -->
    <div class="patient-header card">
      <div class="header-row">
        <span class="label">MRN:</span>
        <span class="value" id="mrn">001</span>
      </div>
      <div class="header-row">
        <span class="label">Name:</span>
        <span class="value" id="patientName">Ramesh K</span>
      </div>
      <div class="header-row">
        <span class="label">Age:</span>
        <span class="value" id="age">45</span>
      </div>
    </div>

    <!-- Dictation Area -->
    <div class="form-group">
      <label for="dictationInput" class="form-label">Clinical Note</label>
      <textarea 
        id="dictationInput" 
        class="form-control" 
        placeholder="Dictate or type clinical note here... Start recording to use microphone"
        rows="12"
      ></textarea>
      
      <div class="dictation-controls">
        <button id="recordBtn" class="btn btn--primary" title="Start voice recording">
          🎤 Record
        </button>
        <button id="stopRecordBtn" class="btn btn--secondary" style="display: none;" title="Stop recording">
          ⏹️ Stop
        </button>
        <button id="extractBtn" class="btn btn--secondary" title="Extract structured entities">
          ✨ Extract Entities
        </button>
        <span class="auto-save-indicator" id="autoSaveIndicator">
          Auto-saved at 12:45
        </span>
      </div>
    </div>

    <!-- Medical Note Sections (Collapsible) -->
    <div class="medical-sections">
      
      <div class="section-group">
        <h3 class="section-title">
          <span class="toggle-icon">▼</span>
          Chief Complaint
        </h3>
        <div class="section-content">
          <textarea class="form-control" placeholder="Chief complaint..." rows="2"></textarea>
        </div>
      </div>

      <div class="section-group">
        <h3 class="section-title">
          <span class="toggle-icon">▼</span>
          History of Present Illness
        </h3>
        <div class="section-content">
          <textarea class="form-control" placeholder="HPI..." rows="3"></textarea>
        </div>
      </div>

      <div class="section-group">
        <h3 class="section-title">
          <span class="toggle-icon">▼</span>
          Physical Examination
        </h3>
        <div class="section-content">
          <textarea class="form-control" placeholder="Examination findings..." rows="3"></textarea>
          <a href="#" class="link-assessment">→ Link to Joint Assessment</a>
        </div>
      </div>

      <div class="section-group">
        <h3 class="section-title">
          <span class="toggle-icon">▼</span>
          Assessment
        </h3>
        <div class="section-content">
          <textarea class="form-control" placeholder="Assessment..." rows="2"></textarea>
        </div>
      </div>

      <div class="section-group">
        <h3 class="section-title">
          <span class="toggle-icon">▼</span>
          Plan
        </h3>
        <div class="section-content">
          <textarea class="form-control" placeholder="Treatment plan..." rows="2"></textarea>
        </div>
      </div>

    </div>

    <!-- Action Buttons -->
    <div class="action-buttons">
      <button id="saveDraftBtn" class="btn btn--secondary" title="Save as draft">
        Save Draft
      </button>
      <button id="finalizeBtn" class="btn btn--primary" title="Finalize and submit">
        Finalize Note
      </button>
    </div>

  </div>

  <!-- RIGHT SIDE: Joint Assessment Panel (30%) - Sticky -->
  <aside class="joint-assessment-panel" id="jointPanel">
    
    <!-- Header with Toggle -->
    <div class="panel-header">
      <h3>Joint Assessment</h3>
      <button id="collapseBtn" class="btn-icon" title="Collapse panel">
        →
      </button>
    </div>

    <!-- Mode Selection -->
    <div class="mode-selector">
      <label class="checkbox-label">
        <input type="checkbox" id="tendernessMode" class="mode-toggle">
        <span>Tenderness</span>
      </label>
      <label class="checkbox-label">
        <input type="checkbox" id="swellingMode" class="mode-toggle" checked>
        <span>Swelling</span>
      </label>
      <label class="checkbox-label">
        <input type="checkbox" id="painMode" class="mode-toggle">
        <span>Pain</span>
      </label>
    </div>

    <!-- Joint Assessment Canvas (Konva) -->
    <div class="canvas-container">
      <canvas 
        id="jointCanvas" 
        width="280" 
        height="400"
        title="Click joints to mark assessment. Left: Swelling, Right: Tenderness"
      ></canvas>
      <div class="canvas-legend">
        <div class="legend-item">
          <span class="legend-dot" style="background: #ccc;"></span> Normal
        </div>
        <div class="legend-item">
          <span class="legend-dot" style="background: #FFC107;"></span> Tender
        </div>
        <div class="legend-item">
          <span class="legend-dot" style="background: #FF5252;"></span> Swollen
        </div>
        <div class="legend-item">
          <span class="legend-dot" style="background: #FF9800;"></span> Both
        </div>
      </div>
    </div>

    <!-- Summary Statistics -->
    <div class="assessment-summary">
      
      <div class="stat-row">
        <label for="tjcInput">Tender Joints (TJC)</label>
        <input 
          type="number" 
          id="tjcInput" 
          class="stat-input" 
          value="0" 
          min="0" 
          max="28"
          readonly
        >
      </div>

      <div class="stat-row">
        <label for="sjcInput">Swollen Joints (SJC)</label>
        <input 
          type="number" 
          id="sjcInput" 
          class="stat-input" 
          value="0" 
          min="0" 
          max="28"
          readonly
        >
      </div>

      <div class="stat-row">
        <label for="esrInput">ESR (mm/h)</label>
        <input 
          type="number" 
          id="esrInput" 
          class="stat-input" 
          value="20" 
          min="0"
        >
      </div>

      <div class="stat-row">
        <label for="pgInput">Patient Global (0-100)</label>
        <input 
          type="number" 
          id="pgInput" 
          class="stat-input" 
          value="50" 
          min="0" 
          max="100"
        >
      </div>

    </div>

    <!-- DAS28 Score Display -->
    <div class="das28-score-box">
      <div class="score-value" id="das28Score">4.56</div>
      <div class="score-category" id="das28Category">Moderate Activity</div>
      <div class="score-bar">
        <div class="bar-fill" id="das28Bar" style="width: 45%;"></div>
      </div>
      <div class="score-range">
        <span class="range-label">0</span>
        <span class="range-label">2.6</span>
        <span class="range-label">3.2</span>
        <span class="range-label">5.1</span>
      </div>
    </div>

    <!-- Save Button -->
    <button id="saveAssessmentBtn" class="btn btn--success btn--full">
      ✓ Save Assessment
    </button>

  </aside>

</div>
```

---

## 🎨 CSS STYLING

### Desktop Layout (1200px+)

```css
.medical-note-wrapper {
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: 16px;
  padding: 20px;
  max-width: 1600px;
  margin: 0 auto;
}

.dictation-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.joint-assessment-panel {
  position: sticky;
  top: 20px;
  height: fit-content;
  max-height: calc(100vh - 40px);
  overflow-y: auto;
  
  background: white;
  border: 2px solid #ddd;
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.patient-header.card {
  background: #f5f5f5;
  border: 2px solid #ddd;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 16px;
}

.header-row {
  display: flex;
  justify-content: space-between;
  padding: 4px 0;
  font-size: 14px;
}

.header-row .label {
  font-weight: 600;
  color: #333;
}

.header-row .value {
  color: #666;
}

.dictation-input, 
.form-control {
  width: 100%;
  padding: 12px;
  font-size: 14px;
  border: 2px solid #ddd;
  border-radius: 8px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  line-height: 1.6;
  resize: vertical;
}

.dictation-input:focus,
.form-control:focus {
  outline: none;
  border-color: #0066cc;
  box-shadow: 0 0 0 3px rgba(0, 102, 204, 0.1);
}

.dictation-controls {
  display: flex;
  gap: 8px;
  margin-top: 8px;
  align-items: center;
  flex-wrap: wrap;
}

.auto-save-indicator {
  margin-left: auto;
  font-size: 12px;
  color: #999;
}

.medical-sections {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.section-group {
  border: 1px solid #ddd;
  border-radius: 8px;
  overflow: hidden;
}

.section-title {
  margin: 0;
  padding: 12px 16px;
  background: #f9f9f9;
  border-bottom: 1px solid #ddd;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: background 0.2s;
}

.section-title:hover {
  background: #f0f0f0;
}

.toggle-icon {
  display: inline-block;
  transition: transform 0.2s;
}

.section-group.collapsed .toggle-icon {
  transform: rotate(-90deg);
}

.section-content {
  padding: 12px 16px;
  display: none;
}

.section-group.open .section-content {
  display: block;
}

.action-buttons {
  display: flex;
  gap: 8px;
  margin-top: 16px;
}

/* PANEL STYLING */
.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 2px solid #ddd;
}

.panel-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.btn-icon {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: #666;
  transition: color 0.2s;
}

.btn-icon:hover {
  color: #0066cc;
}

.mode-selector {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #ddd;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-size: 14px;
  user-select: none;
}

.checkbox-label input[type="checkbox"] {
  cursor: pointer;
  width: 16px;
  height: 16px;
}

.canvas-container {
  margin-bottom: 16px;
  text-align: center;
}

#jointCanvas {
  border: 1px solid #ddd;
  border-radius: 4px;
  display: block;
  margin: 0 auto 8px;
  background: white;
  cursor: crosshair;
}

.canvas-legend {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 4px;
  font-size: 12px;
  margin-bottom: 12px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.legend-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.assessment-summary {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #ddd;
}

.stat-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 13px;
}

.stat-row label {
  font-weight: 500;
  color: #666;
}

.stat-input {
  width: 60px;
  padding: 4px 8px;
  font-size: 13px;
  border: 1px solid #ddd;
  border-radius: 4px;
  text-align: right;
  background: #f9f9f9;
}

.stat-input:focus {
  outline: none;
  border-color: #0066cc;
  background: white;
}

.das28-score-box {
  background: linear-gradient(135deg, #f0f0f0 0%, #fafafa 100%);
  border: 2px solid #ddd;
  border-radius: 8px;
  padding: 12px;
  margin-bottom: 16px;
  text-align: center;
}

.score-value {
  font-size: 32px;
  font-weight: 700;
  color: #0066cc;
  margin-bottom: 4px;
}

.score-category {
  font-size: 14px;
  font-weight: 600;
  color: #666;
  margin-bottom: 8px;
}

.score-bar {
  height: 6px;
  background: #ddd;
  border-radius: 3px;
  overflow: hidden;
  margin-bottom: 8px;
}

.bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #4CAF50 0%, #FFC107 50%, #FF5252 100%);
  transition: width 0.3s ease;
}

.score-range {
  display: flex;
  justify-content: space-between;
  font-size: 11px;
  color: #999;
}

.btn--full {
  width: 100%;
}

.btn--success {
  background: #4CAF50;
  color: white;
}

.btn--success:hover {
  background: #45a049;
}
```

### Tablet Layout (768px - 1199px)

```css
@media (max-width: 1199px) {
  .medical-note-wrapper {
    display: flex;
    flex-direction: column;
    grid-template-columns: none;
  }

  .joint-assessment-panel {
    position: relative;
    top: auto;
    max-height: none;
    margin-top: 20px;
  }

  .medical-sections {
    max-height: 400px;
    overflow-y: auto;
  }
}
```

### Mobile Layout (< 768px)

```css
@media (max-width: 768px) {
  .medical-note-wrapper {
    padding: 12px;
  }

  .joint-assessment-panel {
    display: none;  /* Hidden by default on mobile */
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    height: 60vh;
    z-index: 1000;
    background: white;
    border-radius: 16px 16px 0 0;
    border: none;
    border-top: 2px solid #ddd;
    padding: 16px;
    max-height: none;
    overflow-y: auto;
    box-shadow: 0 -4px 12px rgba(0,0,0,0.15);
  }

  .joint-assessment-panel.visible {
    display: flex;
    flex-direction: column;
  }

  .dictation-input {
    min-height: 120px;
  }

  .action-buttons {
    flex-direction: column;
  }

  .action-buttons button {
    width: 100%;
  }

  .dictation-controls {
    flex-direction: column;
  }

  .dictation-controls button {
    width: 100%;
  }
}
```

---

## 💻 JAVASCRIPT FUNCTIONALITY

### Core State Management

```javascript
// Global state
const assessmentState = {
  mode: {
    tenderness: false,
    swelling: true,
    pain: false
  },
  joints: {
    // Will be populated with 28 joints
    // Each joint: { name, side, tenderness, swelling, pain }
  },
  tjc: 0,
  sjc: 0,
  esr: 20,
  pg: 50,
  das28: 0,
  lastSaved: null
};

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
  initializeJointCanvas();
  attachEventListeners();
  loadPreviousAssessment();
  autoSaveEnabled = true;
});
```

### Joint Canvas (Konva.js)

```javascript
const stage = new Konva.Stage({
  container: 'jointCanvas',
  width: 280,
  height: 400,
});

const layer = new Konva.Layer();
stage.add(layer);

// Define 28 joints (simplified example)
const JOINTS = [
  // Hands
  { id: 'h1', name: 'RH MCP 1', x: 200, y: 100, side: 'right' },
  { id: 'h2', name: 'RH MCP 2', x: 220, y: 100, side: 'right' },
  // ... continue for all 28 joints
];

function initializeJointCanvas() {
  JOINTS.forEach(joint => {
    const circle = new Konva.Circle({
      x: joint.x,
      y: joint.y,
      radius: 12,
      fill: '#cccccc',  // Default color
      stroke: '#999',
      strokeWidth: 1,
      id: joint.id,
      listening: true,
      cursor: 'pointer'
    });

    // Click handler
    circle.on('click', () => toggleJoint(joint.id));
    
    // Right-click handler
    circle.on('contextmenu', (e) => {
      e.evt.preventDefault();
      toggleTenderness(joint.id);
    });

    layer.add(circle);
  });

  layer.draw();
}

function toggleJoint(jointId) {
  if (!assessmentState.mode.swelling) return;
  
  const circle = layer.findOne(`#${jointId}`);
  assessmentState.joints[jointId] = assessmentState.joints[jointId] || {};
  assessmentState.joints[jointId].swelling = !assessmentState.joints[jointId].swelling;
  
  updateJointColor(circle, jointId);
  updateStats();
  updateDAS28();
  autoSave();
}

function toggleTenderness(jointId) {
  if (!assessmentState.mode.tenderness) return;
  
  const circle = layer.findOne(`#${jointId}`);
  assessmentState.joints[jointId] = assessmentState.joints[jointId] || {};
  assessmentState.joints[jointId].tenderness = !assessmentState.joints[jointId].tenderness;
  
  updateJointColor(circle, jointId);
  updateStats();
  updateDAS28();
  autoSave();
}

function updateJointColor(circle, jointId) {
  const joint = assessmentState.joints[jointId];
  let color = '#cccccc';  // Normal

  if (joint.swelling && joint.tenderness) {
    color = '#FF9800';  // Both
  } else if (joint.swelling) {
    color = '#FF5252';  // Swollen
  } else if (joint.tenderness) {
    color = '#FFC107';  // Tender
  }

  circle.fill(color);
  layer.draw();
}
```

### Statistics & DAS28 Calculation

```javascript
function updateStats() {
  let tjc = 0, sjc = 0;

  Object.values(assessmentState.joints).forEach(joint => {
    if (joint.tenderness) tjc++;
    if (joint.swelling) sjc++;
  });

  assessmentState.tjc = tjc;
  assessmentState.sjc = sjc;

  document.getElementById('tjcInput').value = tjc;
  document.getElementById('sjcInput').value = sjc;
}

function updateDAS28() {
  const { tjc, sjc, esr, pg } = assessmentState;

  // DAS28 Formula (simplified)
  const das28 = 0.56 * Math.sqrt(tjc) + 
                0.28 * Math.sqrt(sjc) + 
                0.7 * Math.log(esr) + 
                0.014 * pg;

  assessmentState.das28 = Math.round(das28 * 100) / 100;

  document.getElementById('das28Score').textContent = das28.toFixed(2);
  
  let category = 'Low Activity';
  let barWidth = 20;

  if (das28 < 2.6) {
    category = 'Remission';
    barWidth = 10;
  } else if (das28 < 3.2) {
    category = 'Low Activity';
    barWidth = 25;
  } else if (das28 < 5.1) {
    category = 'Moderate Activity';
    barWidth = 50;
  } else {
    category = 'High Activity';
    barWidth = 90;
  }

  document.getElementById('das28Category').textContent = category;
  document.getElementById('das28Bar').style.width = barWidth + '%';
}
```

### Event Listeners

```javascript
function attachEventListeners() {
  // Mode toggles
  document.getElementById('tendernessMode').addEventListener('change', (e) => {
    assessmentState.mode.tenderness = e.target.checked;
  });

  document.getElementById('swellingMode').addEventListener('change', (e) => {
    assessmentState.mode.swelling = e.target.checked;
  });

  document.getElementById('painMode').addEventListener('change', (e) => {
    assessmentState.mode.pain = e.target.checked;
  });

  // Stats inputs
  document.getElementById('esrInput').addEventListener('change', (e) => {
    assessmentState.esr = parseInt(e.target.value) || 0;
    updateDAS28();
    autoSave();
  });

  document.getElementById('pgInput').addEventListener('change', (e) => {
    assessmentState.pg = parseInt(e.target.value) || 0;
    updateDAS28();
    autoSave();
  });

  // Save button
  document.getElementById('saveAssessmentBtn').addEventListener('click', saveAssessment);

  // Collapse button
  document.getElementById('collapseBtn').addEventListener('click', togglePanelCollapse);

  // Medical note sections (collapsible)
  document.querySelectorAll('.section-title').forEach(title => {
    title.addEventListener('click', (e) => {
      e.currentTarget.parentElement.classList.toggle('open');
    });
  });

  // Voice recording
  document.getElementById('recordBtn').addEventListener('click', startRecording);
  document.getElementById('stopRecordBtn').addEventListener('click', stopRecording);
  document.getElementById('extractBtn').addEventListener('click', extractEntities);

  // Draft & Finalize
  document.getElementById('saveDraftBtn').addEventListener('click', saveDraft);
  document.getElementById('finalizeBtn').addEventListener('click', finalizeNote);
}

function togglePanelCollapse() {
  const panel = document.getElementById('jointPanel');
  panel.classList.toggle('collapsed');
}

function autoSave() {
  clearTimeout(window.autoSaveTimeout);
  window.autoSaveTimeout = setTimeout(() => {
    // Save to localStorage or backend
    localStorage.setItem('assessmentDraft', JSON.stringify(assessmentState));
    document.getElementById('autoSaveIndicator').textContent = 
      `Auto-saved at ${new Date().toLocaleTimeString()}`;
  }, 1000);
}

function saveAssessment() {
  // POST to backend
  fetch('/api/joint-assessment', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(assessmentState)
  })
  .then(r => r.json())
  .then(data => {
    assessmentState.lastSaved = new Date();
    showNotification('✓ Assessment saved successfully', 'success');
  })
  .catch(err => {
    showNotification('Error saving assessment', 'error');
    console.error(err);
  });
}

function saveDraft() {
  const noteData = {
    assessment: assessmentState,
    clinical_note: document.getElementById('dictationInput').value,
    status: 'draft'
  };

  fetch('/api/medical-note', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(noteData)
  })
  .then(r => r.json())
  .then(data => {
    showNotification('✓ Draft saved', 'success');
  });
}

function finalizeNote() {
  const noteData = {
    assessment: assessmentState,
    clinical_note: document.getElementById('dictationInput').value,
    status: 'finalized'
  };

  fetch('/api/medical-note', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(noteData)
  })
  .then(r => r.json())
  .then(data => {
    showNotification('✓ Note finalized and saved', 'success');
    // Redirect or reset form
    setTimeout(() => window.location.href = '/dashboard', 1000);
  });
}
```

### Keyboard Shortcuts

```javascript
function setupKeyboardShortcuts() {
  document.addEventListener('keydown', (e) => {
    // Alt + T: Toggle Tenderness mode
    if (e.altKey && e.key === 't') {
      e.preventDefault();
      const checkbox = document.getElementById('tendernessMode');
      checkbox.checked = !checkbox.checked;
      checkbox.dispatchEvent(new Event('change'));
    }

    // Alt + S: Toggle Swelling mode
    if (e.altKey && e.key === 's') {
      e.preventDefault();
      const checkbox = document.getElementById('swellingMode');
      checkbox.checked = !checkbox.checked;
      checkbox.dispatchEvent(new Event('change'));
    }

    // Alt + P: Toggle Pain mode
    if (e.altKey && e.key === 'p') {
      e.preventDefault();
      const checkbox = document.getElementById('painMode');
      checkbox.checked = !checkbox.checked;
      checkbox.dispatchEvent(new Event('change'));
    }

    // Ctrl + S: Save assessment
    if (e.ctrlKey && e.key === 's') {
      e.preventDefault();
      saveAssessment();
    }

    // Ctrl + D: Focus dictation
    if (e.ctrlKey && e.key === 'd') {
      e.preventDefault();
      document.getElementById('dictationInput').focus();
    }

    // Escape: Collapse panel on mobile
    if (e.key === 'Escape') {
      document.getElementById('jointPanel').classList.remove('visible');
    }
  });
}
```

---

## 🎯 CLINICAL WORKFLOW

### Typical Doctor Interaction (< 2 minutes)

```
Timeline                    Action                          System Response
────────────────────────────────────────────────────────────────────────────
0:00  Doctor opens note    Load page                       Show patient info + panel
      Patient is ready     
      
0:05  Doctor starts voice  Click [🎤 Record]              Mic starts listening
      examination          "Patient has swelling in..."    Auto-transcribe
      
0:15  Doctor examines      Glance at right panel          Canvas ready
      left hand            See tenderness/swelling modes  
      
0:20  Mark joints          Left-click joint (swollen)     Canvas updates color
      Left hand swollen    Right-click joint (tender)     Stats update: SJC = 5
      
0:45  Mark joints          Continue marking as exam       Stats update: TJC = 6
      Right hand & knees   progresses                     DAS28 updates: 4.56
      
1:00  Doctor stops voice   Click [⏹️ Stop]               Transcription stops
      completes exam       Auto-save triggered            Note saved to draft
      
1:10  Review numbers       Look at summary stats          Numbers visible:
                           TJC: 6, SJC: 2                TJC: 6  SJC: 2
                           ESR: 20, PG: 50               ESR: 20  PG: 50
                                                          Score: 4.56
      
1:20  Save assessment      Click [✓ Save Assessment]     Confirmation message
                                                          Panel highlights (green)
      
1:35  Finalize note        Click [Finalize Note]         Redirect to dashboard
                           
1:50  DONE                 Note saved in system          Patient record updated

Total elapsed time: ~1m 50s
```

---

## 🔄 DATA FLOW

```
User Input
    ↓
JavaScript State Update
    ↓
Canvas Redraws
    ↓
Statistics Calculate
    ↓
DAS28 Recalculates
    ↓
Auto-save to localStorage (1s debounce)
    ↓
User clicks [Save Assessment]
    ↓
POST to /api/joint-assessment
    ↓
Backend saves to database
    ↓
Return success
    ↓
Clear draft
    ↓
Show confirmation
```

---

## 📱 RESPONSIVE BEHAVIOR SUMMARY

| Breakpoint | Layout | Behavior |
|----------|--------|----------|
| **1200px+** | Side by side | Sticky panel, always visible |
| **768-1199px** | Stacked | Panel below main content, collapsible |
| **< 768px** | Mobile | Panel as bottom sheet, hidden by default, show with button |

---

## 🎯 SUCCESS METRICS

After implementation, measure:

1. **Time to complete assessment** - Target: < 2 minutes
2. **Accuracy of joint marking** - Target: 100% correct marks
3. **Doctor satisfaction** - Target: 4.5/5 rating
4. **System lag** - Target: < 100ms response time
5. **Auto-save frequency** - Target: Every 30 seconds

---

## 🚀 IMPLEMENTATION PHASES

### Phase 1: HTML & CSS (1 day)
- [ ] Create HTML structure
- [ ] Style desktop layout
- [ ] Style tablet layout
- [ ] Style mobile layout

### Phase 2: JavaScript Basics (2 days)
- [ ] Initialize state management
- [ ] Set up Konva canvas
- [ ] Implement click handlers
- [ ] Add mode toggles

### Phase 3: Logic & Calculation (2 days)
- [ ] Build DAS28 calculator
- [ ] Update statistics in real-time
- [ ] Add form validation
- [ ] Implement keyboard shortcuts

### Phase 4: Integration & Polish (2 days)
- [ ] Connect to backend API
- [ ] Add voice recording integration
- [ ] Implement auto-save
- [ ] Add notifications/feedback

### Phase 5: Testing & Optimization (1 day)
- [ ] Test on various devices
- [ ] Performance optimization
- [ ] Accessibility audit
- [ ] User testing

**Total: 8 days for full implementation**

---

## 📋 REQUIREMENTS CHECKLIST

### Functional Requirements
- [ ] Joint canvas displays 28 joints
- [ ] Click toggles swelling status
- [ ] Right-click toggles tenderness status
- [ ] Joint colors update immediately
- [ ] TJC/SJC counts update automatically
- [ ] DAS28 score calculates in real-time
- [ ] ESR and PG inputs accept manual entry
- [ ] Auto-save triggers every 30 seconds
- [ ] Save Assessment button saves to backend
- [ ] Mode toggles (Tenderness/Swelling/Pain) work
- [ ] Panel collapses on mobile
- [ ] Keyboard shortcuts functional

### Non-Functional Requirements
- [ ] Response time < 100ms
- [ ] Works on 10-year-old PCs (2GB RAM)
- [ ] Mobile-responsive
- [ ] WCAG AA accessibility
- [ ] No external fonts (system fonts only)
- [ ] Bundle size < 150KB

### User Experience
- [ ] Doctor can assess in < 2 minutes
- [ ] Zero tab switching required
- [ ] All controls visible at once
- [ ] Clear visual feedback
- [ ] Keyboard accessible
- [ ] Mobile-friendly (touch targets 48px+)

---

## 🎨 COLOR SCHEME

```css
/* Mapping to Design System */
--color-primary: #0066CC        /* Links, active states */
--color-success: #4CAF50        /* Save buttons, confirmation */
--color-warning: #FFC107        /* Tenderness indicator */
--color-error: #FF5252          /* Swelling indicator */
--color-info: #FF9800           /* Both tenderness & swelling */
--color-border: #CCCCCC         /* Borders, dividers */
--color-bg-light: #F5F5F5       /* Section backgrounds */
--color-text-primary: #000000   /* Main text */
--color-text-secondary: #666666 /* Labels, helpers */
```

---

**Document Status:** Ready for implementation  
**Version:** 1.0  
**Last Updated:** December 6, 2025  
**Next Step:** Begin Phase 1 (HTML & CSS)
