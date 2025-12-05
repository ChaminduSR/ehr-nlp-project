
## 1. Overall Goal

- Reduce rheumatologist documentation burden in **rural clinics with old PCs**.
- Let doctor **speak or type one free-form note** instead of filling 7 boxes.
- Use **offline speech recognition (VOSK)** + **NLP** + **joint assessment UI** to:
    - Capture data quickly
    - Auto-structure into the standard SOAP/DAS28 format
    - Compute DAS28 score
    - Store in a reliable, audit-friendly backend.

***

## 2. Single Free-Form Medical Note → Structured Report

### 2.1 Concept

- UI: One large text area (`medical_note`) + optional voice button 🎤.
- Workflow:

1. Doctor types or dictates entire visit note in natural language.
2. Backend NLP processes note → extracts:
        - Chief Complaint
        - HPI
        - Physical Exam
        - Assessment
        - Plan
        - Medications
        - DAS28 inputs (if present)
3. System auto-fills internal fields and generates a structured report.
4. Doctor reviews and edits only if needed.


### 2.2 Backend Endpoint (Flask + spaCy, lazy-loaded for performance)

```python
# app.py (or routes/medical_note.py)

from flask import Flask, request, jsonify
import spacy

app = Flask(__name__)
nlp = None  # Lazy-load spaCy model

def load_nlp():
    global nlp
    if nlp is None:
        nlp = spacy.load("en_core_web_sm")

@app.route('/api/v1/process-medical-note', methods=['POST'])
def process_medical_note():
    load_nlp()
    payload = request.get_json()
    note_text = payload.get('medical_note', '')

    doc = nlp(note_text)

    extraction = {
        "chief_complaint": extract_chief_complaint(doc),
        "hpi": extract_hpi(doc),
        "physical_exam": extract_exam(doc),
        "assessment": extract_assessment(doc),
        "plan": extract_plan(doc),
        "medications": extract_medications(doc),
        "follow_up": extract_follow_up(doc),
    }

    confidence_scores = calculate_confidence(doc, extraction)
    review_needed = [
        {"name": k, "confidence": confidence_scores[k]}
        for k, v in confidence_scores.items()
        if v < 0.8
    ]

    return jsonify({
        "structured_data": extraction,
        "confidence_scores": confidence_scores,
        "review_needed": review_needed
    })
```

*(You would implement `extract_*` + `calculate_confidence` using rule-based NLP + domain vocab.)*

### 2.3 Frontend Single Note Field (HTMX + Alpine.js)

```html
<div x-data="medicalNote()">
  <label for="medical_note">Medical Note</label>
  <textarea id="medical_note"
            class="form-control"
            rows="8"
            x-model="note"
            placeholder="Type or dictate full note here (CC, HPI, exam, assessment, plan)...">
  </textarea>

  <!-- Voice button (calls your VOSK endpoint) -->
  <button type="button" class="btn btn--secondary" @click="startDictation()">
    🎤 Dictate
  </button>

  <button type="button" class="btn btn--primary mt-8" @click="processNote()">
    Generate Structured Report
  </button>

  <!-- Structured report preview -->
  <div class="card mt-16" x-show="structured">
    <div class="card__header">
      <h3>Structured Report</h3>
      <span class="status" x-text="'Fields needing review: ' + reviewNeeded.length"></span>
    </div>
    <div class="card__body">
      <h4>Chief Complaint</h4>
      <p x-text="structured.chief_complaint"></p>

      <h4>HPI</h4>
      <p x-text="structured.hpi"></p>

      <h4>Physical Examination</h4>
      <p x-text="structured.physical_exam"></p>

      <h4>Assessment</h4>
      <p x-text="structured.assessment"></p>

      <h4>Plan</h4>
      <p x-text="structured.plan"></p>

      <h4>Medications</h4>
      <p x-text="structured.medications"></p>

      <h4>Follow-up</h4>
      <p x-text="structured.follow_up"></p>
    </div>

    <!-- Review-needed section -->
    <div class="card__footer" x-show="reviewNeeded.length > 0">
      <h4>Review Needed</h4>
      <ul>
        <template x-for="field in reviewNeeded" :key="field.name">
          <li x-text="field.name + ' (confidence ' + Math.round(field.confidence * 100) + '%)'"></li>
        </template>
      </ul>
    </div>
  </div>
</div>

<script>
function medicalNote() {
  return {
    note: '',
    structured: null,
    reviewNeeded: [],

    async startDictation() {
      // hook into your existing VOSK voice capture → transcribedText
      const text = await startVoskRecording(); // you already have this logic
      this.note += (this.note ? '\n' : '') + text;
    },

    async processNote() {
      const res = await fetch('/api/v1/process-medical-note', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ medical_note: this.note })
      });
      const data = await res.json();
      this.structured = data.structured_data;
      this.reviewNeeded = data.review_needed;
    }
  }
}
</script>
```


***

## 3. Voice Recognition in Rural Clinics (from your docs + this chat)

- Use **VOSK** for offline speech recognition.
- Two deployment modes (you already documented in `master_project_complete_v3-1.md`):

1. Lazy load on old PC.
2. Central server for multiple old PCs (recommended).

You already have this implemented, so just **reuse the voice button** with the new single-note endpoint.

***

## 4. Joint Assessment \& DAS28 – Performance-First Design

Original idea in your query was React + SVG. To stay aligned with your project, we pivot to:

- **Konva.js** for drawing joints (already in your stack).
- **Alpine.js** for state and popovers.
- **Flask** + **HTMX** for saving joint data and calculating DAS28.


### 4.1 Visual: 28 Joints via Konva.js

- Use Konva **Stage + Layer + Circles** for each DAS28 joint:
    - Shoulders (L/R)
    - Elbows (L/R)
    - Wrists (L/R)
    - MCP 1–5 (L/R)
    - PIP 2–5 (L/R)
    - Knees (L/R)

Each joint stored in `joints[jointId] = { shape, tenderness, pain, swelling }`.

### 4.2 Alpine Component Skeleton

```html
<div x-data="jointAssessment()" x-init="init()">
  <div id="joint-diagram-container" style="width: 400px; height: 600px;"></div>

  <!-- Popover -->
  <div x-show="selectedJoint"
       style="position:absolute; left: calc(popoverX + 20px); top: popoverY + 'px';"
       class="card">
    <div class="card__body">
      <h4 x-text="selectedJoint.name"></h4>

      <label>
        <input type="checkbox" @change="toggle('tenderness')" :checked="selectedJoint.tenderness">
        Tenderness
      </label>

      <label>
        <input type="checkbox" @change="toggle('pain')" :checked="selectedJoint.pain">
        Pain
      </label>

      <label>
        Swelling grade
        <select @change="updateSwelling($event)">
          <option value="0">0 – None</option>
          <option value="1">1 – Mild</option>
          <option value="2">2 – Moderate</option>
          <option value="3">3 – Severe</option>
        </select>
      </label>

      <button class="btn btn--primary mt-8" @click="saveJoint()">Save</button>
    </div>
  </div>

  <div id="das28-results" hx-target="this"></div>
</div>

<script>
function jointAssessment() {
  return {
    stage: null,
    layer: null,
    joints: {},
    selectedJoint: null,
    popoverX: 0,
    popoverY: 0,

    init() {
      this.initKonva();
      this.addJoints();
    },

    initKonva() {
      this.stage = new Konva.Stage({
        container: 'joint-diagram-container',
        width: 400,
        height: 600
      });
      this.layer = new Konva.Layer();
      this.stage.add(this.layer);
    },

    addJoints() {
      const positions = {
        l_shoulder: { x: 120, y: 80 },
        r_shoulder: { x: 280, y: 80 },
        l_elbow: { x: 100, y: 160 },
        r_elbow: { x: 300, y: 160 },
        l_wrist: { x: 90, y: 230 },
        r_wrist: { x: 310, y: 230 },
        l_knee: { x: 160, y: 430 },
        r_knee: { x: 240, y: 430 },
        // ... MCPs + PIPs etc.
      };

      for (const [id, pos] of Object.entries(positions)) {
        const circle = new Konva.Circle({
          x: pos.x,
          y: pos.y,
          radius: 12,
          fill: 'white',
          stroke: '#333',
          strokeWidth: 2,
          id
        });

        circle.on('click', () => this.openPopover(id, pos.x, pos.y));
        this.layer.add(circle);
        this.joints[id] = { shape: circle, tenderness: false, pain: false, swelling: 0 };
      }
      this.layer.draw();
    },

    openPopover(id, x, y) {
      const j = this.joints[id];
      this.selectedJoint = {
        id,
        name: id.replace('_', ' ').toUpperCase(),
        tenderness: j.tenderness,
        pain: j.pain,
        swelling: j.swelling
      };
      this.popoverX = x;
      this.popoverY = y;
    },

    toggle(prop) {
      this.selectedJoint[prop] = !this.selectedJoint[prop];
      this.updateColor(this.selectedJoint.id);
    },

    updateSwelling(e) {
      this.selectedJoint.swelling = parseInt(e.target.value);
      this.updateColor(this.selectedJoint.id);
    },

    updateColor(id) {
      const j = this.joints[id];
      const s = j.shape;
      const temp = this.selectedJoint && this.selectedJoint.id === id ? this.selectedJoint : j;

      let color = 'white';
      if (temp.tenderness && temp.swelling > 0) color = 'orange';
      else if (temp.tenderness) color = 'yellow';
      else if (temp.swelling > 0) color = '```

