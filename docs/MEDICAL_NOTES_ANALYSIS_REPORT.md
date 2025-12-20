# Medical Notes System Analysis Report

> **Purpose**: Comprehensive technical analysis for ML model training research
> **Generated**: December 2024
> **Scope**: Database schema, 3-tab UI system, NLP pipeline, data models

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Database Schema](#2-database-schema)
3. [Tab 1: Smart Detection](#3-tab-1-smart-detection)
4. [Tab 2: Joint Map (DAS28 Assessment)](#4-tab-2-joint-map-das28-assessment)
5. [Tab 3: Structured Note](#5-tab-3-structured-note)
6. [Backend API Endpoints](#6-backend-api-endpoints)
7. [NLP Engine & Entity Extraction](#7-nlp-engine--entity-extraction)
8. [Data Models & Validation](#8-data-models--validation)
9. [State Management & Auto-Save](#9-state-management--auto-save)
10. [Data Flow Architecture](#10-data-flow-architecture)
11. [ML Training Data Considerations](#11-ml-training-data-considerations)
12. [File Location Reference](#12-file-location-reference)

---

## 1. Executive Summary

The medical notes system is a multi-modal clinical documentation platform featuring:

- **Voice-to-text dictation** using VOSK offline recognition
- **NLP entity extraction** via spaCy/scispaCy (`en_core_sci_md`)
- **28-joint interactive assessment** with DAS28-ESR calculation
- **Structured clinical sections** following medical documentation standards
- **Auto-save with coordinated persistence** across all data types

### Key Data Assets for ML Training

| Data Type | Format | Volume | Use Case |
|-----------|--------|--------|----------|
| Clinical Notes | Free text + structured sections | Per visit | NER, section classification, clinical summarization |
| Entity Annotations | Labeled spans (DRUG, DISEASE, etc.) | Per extraction | Named entity recognition |
| Joint Assessments | 28 binary/ordinal values | Per visit | Multi-label classification |
| DAS28 Scores | Continuous 0-10 | Per assessment | Regression, severity prediction |
| Temporal Workflow | Draft → Finalized timestamps | Per note | Process modeling |

---

## 2. Database Schema

**Location**: `backend/database/init_schema.sql`
**Engine**: SQLite with WAL mode

### 2.1 Core Tables

#### `patients`
```sql
CREATE TABLE patients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mrn TEXT UNIQUE NOT NULL,           -- Medical Record Number
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    date_of_birth DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### `visits`
```sql
CREATE TABLE visits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER NOT NULL,         -- FK → patients.id
    visit_date DATE NOT NULL,
    visit_type TEXT,                      -- e.g., 'follow-up', 'new patient'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(id)
);
```

#### `medical_notes`
```sql
CREATE TABLE medical_notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    visit_id INTEGER NOT NULL,            -- FK → visits.id
    note_text TEXT NOT NULL,              -- Full clinical note (raw text blob)
    status TEXT DEFAULT 'draft',          -- CHECK IN ('draft', 'finalized')
    draft_saved_at TIMESTAMP,             -- Last auto-save timestamp
    signed_by INTEGER,                    -- User ID who finalized
    signed_at TIMESTAMP,                  -- Finalization timestamp
    entity_count INTEGER DEFAULT 0,       -- NLP entities extracted
    processing_time_ms REAL,              -- NLP processing duration
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (visit_id) REFERENCES visits(id)
);
```

**Key Fields for ML**:
- `note_text`: Primary training data for text models
- `entity_count`: Supervision signal for extraction quality
- `status`: Workflow state (draft notes may have different characteristics)

#### `joint_assessments`
```sql
CREATE TABLE joint_assessments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    visit_id INTEGER NOT NULL,            -- FK → visits.id
    joint_id TEXT NOT NULL,               -- e.g., 'l_shoulder', 'r_mcp3'
    has_tenderness BOOLEAN DEFAULT 0,     -- Binary tenderness flag
    has_pain BOOLEAN DEFAULT 0,           -- Binary pain indicator
    swelling_grade INTEGER DEFAULT 0,     -- 0=none, 1=mild, 2=moderate, 3=severe
    assessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (visit_id) REFERENCES visits(id),
    CHECK (swelling_grade BETWEEN 0 AND 3)
);
```

**Data Characteristics**:
- 28 rows per complete assessment (one per joint)
- Sparse representation (only affected joints may be stored)
- Ordinal swelling scale (0-3)

#### `joint_assessment_summaries`
```sql
CREATE TABLE joint_assessment_summaries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    visit_id INTEGER NOT NULL,            -- FK → visits.id
    tjc INTEGER,                          -- Tender Joint Count (0-28)
    sjc INTEGER,                          -- Swollen Joint Count (0-28)
    esr REAL,                             -- Erythrocyte Sedimentation Rate (mm/h)
    pga REAL,                             -- Patient Global Assessment (0-100)
    pg_scale_1_10 INTEGER,                -- VAS scale (1-10)
    das28_score REAL,                     -- Calculated DAS28-ESR
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (visit_id) REFERENCES visits(id)
);
```

**DAS28-ESR Formula**:
```
DAS28 = 0.56 × √(TJC) + 0.28 × √(SJC) + 0.70 × ln(ESR) + 0.014 × PGA
```

| Score Range | Disease Activity |
|-------------|------------------|
| < 2.6 | Remission |
| 2.6 - 3.2 | Low Activity |
| 3.2 - 5.1 | Moderate Activity |
| > 5.1 | High Activity |

#### `voice_transcriptions`
```sql
CREATE TABLE voice_transcriptions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    medical_note_id INTEGER,              -- FK → medical_notes.id
    audio_duration_seconds REAL,
    transcribed_text TEXT,
    model_used TEXT DEFAULT 'vosk-en-us',
    transcribed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (medical_note_id) REFERENCES medical_notes(id)
);
```

### 2.2 Entity Relationship Diagram

```
┌─────────────┐      ┌─────────────┐      ┌──────────────────┐
│  patients   │──1:N─│   visits    │──1:1─│  medical_notes   │
│             │      │             │      │                  │
│ • mrn       │      │ • visit_date│      │ • note_text      │
│ • first_name│      │ • visit_type│      │ • status         │
│ • last_name │      │             │      │ • entity_count   │
│ • dob       │      │             │      │ • processing_ms  │
└─────────────┘      └──────┬──────┘      └────────┬─────────┘
                            │                      │
                     ┌──────┴──────┐               │
                     │             │               │
              ┌──────▼─────┐ ┌─────▼──────────┐ ┌──▼─────────────────┐
              │  joint_    │ │ joint_assess-  │ │ voice_transcriptions│
              │ assessments│ │ ment_summaries │ │                     │
              │            │ │                │ │ • audio_duration    │
              │ • joint_id │ │ • tjc, sjc     │ │ • transcribed_text  │
              │ • tender   │ │ • esr, pga     │ │ • model_used        │
              │ • pain     │ │ • das28_score  │ └─────────────────────┘
              │ • swelling │ └────────────────┘
              └────────────┘
```

---

## 3. Tab 1: Smart Detection

**Location**: `backend/templates/fragments/medical_note_form.html`
**Logic**: `frontend/src/modules/medical_note_logic.js`

### 3.1 Purpose

Voice-powered dictation with intelligent NLP entity extraction for auto-populating structured sections.

### 3.2 UI Components

| Element | Type | Purpose |
|---------|------|---------|
| `#dictation-input` | Textarea (rows=6) | Main input for dictation/paste |
| Record Button 🎤 | Toggle | Start/stop VOSK recording |
| Extract Entities ✨ | Button | Trigger NLP extraction |
| Review Modal | Dialog | Display/edit extracted data |

### 3.3 Voice Recording Flow

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ Click Record│───▶│ VOSK Start  │───▶│ Audio Stream│───▶│ Transcribe  │
│     🎤      │    │             │    │ Processing  │    │ to Text     │
└─────────────┘    └─────────────┘    └─────────────┘    └──────┬──────┘
                                                                │
                                                         ┌──────▼──────┐
                                                         │ Append to   │
                                                         │ Textarea    │
                                                         └─────────────┘
```

**API**: Uses `window.VoiceRecorder.start()` / `.stop()` via VOSK offline model.

### 3.4 Entity Extraction Pipeline

```
Input Text                    NLP Processing                    Output
────────────────────────────────────────────────────────────────────────
"Patient presents with       ┌────────────────┐     ┌──────────────────┐
 joint pain and swelling.    │ spaCy Pipeline │     │ raw_entities: [  │
 Started on methotrexate     │ (en_core_sci_md)│    │   {text: "joint  │
 10mg weekly for RA.         │                │────▶│    pain",        │
 Plan: Continue current      │ Entity Detection│    │    type: DISEASE}│
 regimen, f/u 4 weeks."      │ + Heuristic    │     │   {text: "metho- │
                             │   Section Parse │     │    trexate",     │
                             └────────────────┘     │    type: DRUG}   │
                                                    │ ]                │
                                                    │ structured: {    │
                                                    │   medications:   │
                                                    │     ["methotrex- │
                                                    │      ate 10mg"]  │
                                                    │   conditions:    │
                                                    │     ["RA", "joint│
                                                    │      pain"]      │
                                                    │   plan: "Continue│
                                                    │     current..."  │
                                                    │ }                │
                                                    └──────────────────┘
```

### 3.5 State Variables

```javascript
{
  smartText: '',              // Current textarea content
  isRecording: false,         // VOSK recording active
  isExtracting: false,        // NLP request in-flight
  showReview: false,          // Review modal visible
  reviewData: {               // Extracted structured data
    chief_complaint: '',
    hpi: '',
    physical_exam: '',
    assessment: '',
    plan: '',
    medications: [],
    conditions: [],
    allergies: [],
    follow_up: ''
  },
  visitId: <number>,          // Current visit context
  lastSavedText: '',          // For dirty checking
  saveStatus: ''              // 'Saving...', 'Saved', 'Error'
}
```

### 3.6 Review Modal Fields

| Field | Type | Populated From |
|-------|------|----------------|
| Chief Complaint | Text | Heuristic: "complains of", "CC:" patterns |
| HPI | Textarea | First narrative paragraph |
| Assessment | Textarea | Entities: DISEASE, SYNDROME, DISORDER |
| Plan | Textarea | Heuristic: "plan:", "recommendation" |
| Medications | Array | Entities: DRUG, CHEMICAL |
| Conditions | Array | Entities: DISEASE, SYNDROME |
| Allergies | Array | Heuristic: "allergic to", "allergy" |
| Follow-up | Text | Heuristic: "follow-up", "f/u", "return" |

---

## 4. Tab 2: Joint Map (DAS28 Assessment)

**Location**: `backend/templates/fragments/joint_assessment.html`
**Logic**: `frontend/src/modules/joint_assessment_logic.js`
**Diagram**: `frontend/src/modules/joint_diagram.js` (Konva.js)

### 4.1 Purpose

Interactive 28-joint assessment diagram for rheumatoid arthritis disease activity scoring using the DAS28-ESR standard.

### 4.2 The 28 Joints

The DAS28 standard assesses exactly 28 joints:

```
┌─────────────────────────────────────────────────────────────────┐
│                        UPPER LIMBS (6)                          │
├─────────────────────────────────────────────────────────────────┤
│  Left Shoulder (l_shoulder)    │    Right Shoulder (r_shoulder) │
│  Left Elbow (l_elbow)          │    Right Elbow (r_elbow)       │
│  Left Wrist (l_wrist)          │    Right Wrist (r_wrist)       │
├─────────────────────────────────────────────────────────────────┤
│                        LOWER LIMBS (2)                          │
├─────────────────────────────────────────────────────────────────┤
│  Left Knee (l_knee)            │    Right Knee (r_knee)         │
├─────────────────────────────────────────────────────────────────┤
│                        LEFT HAND (10)                           │
├─────────────────────────────────────────────────────────────────┤
│  MCP Joints (5):  l_mcp1, l_mcp2, l_mcp3, l_mcp4, l_mcp5       │
│  PIP Joints (5):  l_pip1*, l_pip2, l_pip3, l_pip4, l_pip5      │
│                   *l_pip1 = IP joint for thumb                  │
├─────────────────────────────────────────────────────────────────┤
│                        RIGHT HAND (10)                          │
├─────────────────────────────────────────────────────────────────┤
│  MCP Joints (5):  r_mcp1, r_mcp2, r_mcp3, r_mcp4, r_mcp5       │
│  PIP Joints (5):  r_pip1*, r_pip2, r_pip3, r_pip4, r_pip5      │
│                   *r_pip1 = IP joint for thumb                  │
└─────────────────────────────────────────────────────────────────┘
```

### 4.3 Joint State Data Structure

Each joint has three assessment dimensions:

```javascript
joints: {
  'l_shoulder': {
    tenderness: boolean,    // Is joint tender to palpation?
    pain: boolean,          // Does patient report pain? (separate from tenderness)
    swelling: integer       // 0=none, 1=mild, 2=moderate, 3=severe
  },
  'l_elbow': { ... },
  // ... 28 total joints
}
```

### 4.4 Visual State Encoding

| State | Fill Color | Border | Meaning |
|-------|-----------|--------|---------|
| Normal | White (#FFFFFF) | Gray | No findings |
| Tenderness Only | Yellow (#FFEB3B) | Gray | Tender to palpation |
| Swelling Only | Red (#FF4444) | Gray | Visible swelling |
| Tenderness + Swelling | Orange (#FF8C00) | Gray | Both findings |
| +Pain | Any above | Blue (#2196F3) | Patient reports pain |

### 4.5 User Interactions

| Action | Trigger | Effect |
|--------|---------|--------|
| Left Click | Mouse click on joint | Cycles: Normal → Tender → Swelling → Both → Normal |
| Right Click | Context menu on joint | Toggles pain indicator (blue border) |
| Hover | Mouse over joint | Shows tooltip with joint label |

### 4.6 DAS28-ESR Calculation

#### Input Components

| Component | Source | Range | Description |
|-----------|--------|-------|-------------|
| TJC | Auto-counted | 0-28 | Number of tender joints |
| SJC | Auto-counted | 0-28 | Number of swollen joints |
| ESR | Manual input | 1-150+ mm/h | Lab value (erythrocyte sedimentation rate) |
| PGA | VAS input × 10 | 0-100 | Patient Global Assessment |

#### Formula

```
DAS28-ESR = 0.56 × √(TJC) + 0.28 × √(SJC) + 0.70 × ln(ESR) + 0.014 × PGA
```

#### Implementation

```javascript
calculateDAS28() {
  const tjc_component = 0.56 * Math.sqrt(this.tjc);
  const sjc_component = 0.28 * Math.sqrt(this.sjc);
  const esr_component = 0.70 * Math.log(Math.max(this.esr, 1)); // Avoid log(0)
  const pga_component = 0.014 * (this.pg_scale * 10);           // VAS 1-10 → 0-100

  this.score = tjc_component + sjc_component + esr_component + pga_component;
}
```

### 4.7 VAS 1-10 Scale UI

```
Patient Global Assessment (VAS 1-10):

[ 1 ] [ 2 ] [ 3 ] [ 4 ] [ 5 ] [ 6 ] [ 7 ] [ 8 ] [ 9 ] [10]
  ▲
  │
  └── Selected (highlighted)
```

- 10 radio-style buttons
- Keyboard navigation: Left/Right arrows, Home, End
- Value stored as `pg_scale` (1-10)
- Converted to 0-100 for formula: `pga = pg_scale * 10`

### 4.8 Disease Activity Categories

| DAS28 Score | Category | UI Color |
|-------------|----------|----------|
| < 2.6 | Remission | Green |
| 2.6 - 3.2 | Low Disease Activity | Yellow |
| 3.2 - 5.1 | Moderate Disease Activity | Blue |
| > 5.1 | High Disease Activity | Red |

### 4.9 Complete State Object

```javascript
{
  // Counts (auto-calculated)
  tjc: 0,                    // Tender Joint Count
  sjc: 0,                    // Swollen Joint Count

  // Manual inputs
  esr: 20,                   // ESR value (mm/h)
  pg_scale: 5,               // Patient Global 1-10

  // Calculated
  score: 0.0,                // DAS28-ESR result

  // Joint data (28 entries)
  joints: {
    'joint_id': { tenderness, pain, swelling }
  },

  // Save tracking
  lastSavedJson: '',
  saveStatus: '',

  // Tooltip
  hoveredJoint: null,
  tooltipX: 0,
  tooltipY: 0
}
```

---

## 5. Tab 3: Structured Note

**Location**: `backend/templates/fragments/medical_note_form.html`

### 5.1 Purpose

Standard clinical documentation sections for organizing medical notes according to healthcare documentation conventions.

### 5.2 Section Fields

| Section | Element Type | Rows | Placeholder | Data Section Attribute |
|---------|--------------|------|-------------|------------------------|
| Chief Complaint | Text input | 1 | "Main reason for visit..." | `CHIEF COMPLAINT` |
| History of Present Illness | Textarea | 4 | "Details of the complaint..." | `HISTORY OF PRESENT ILLNESS` |
| Physical Examination | Textarea | 4 | "Vital signs, general appearance..." | `PHYSICAL EXAMINATION` |
| Assessment | Textarea | 4 | "Diagnoses and clinical impressions..." | `ASSESSMENT` |
| Plan | Textarea | 4 | "Treatment plan, orders, referrals..." | `PLAN` |
| Medications | Textarea | 3 | "Current or new medications..." | `MEDICATIONS` |
| Follow-up | Text input | 1 | "Next appointment or instructions..." | `FOLLOW-UP` |

### 5.3 UI Layout

```
┌─────────────────────────────────────────────────────────────────┐
│ Chief Complaint: [_____________________________________]        │
├─────────────────────────────────────────────────────────────────┤
│ History of Present Illness:                                     │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │                                                             │ │
│ │                                                             │ │
│ │                                                             │ │
│ └─────────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│ Physical Examination:                                           │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │                                                             │ │
│ │                                                             │ │
│ └─────────────────────────────────────────────────────────────┘ │
├────────────────────────────┬────────────────────────────────────┤
│ Assessment:                │ Plan:                              │
│ ┌────────────────────────┐ │ ┌────────────────────────────────┐ │
│ │                        │ │ │                                │ │
│ │                        │ │ │                                │ │
│ └────────────────────────┘ │ └────────────────────────────────┘ │
├────────────────────────────┼────────────────────────────────────┤
│ Medications:               │ Follow-up:                         │
│ ┌────────────────────────┐ │ [______________________________]   │
│ │                        │ │                                    │
│ └────────────────────────┘ │                                    │
└────────────────────────────┴────────────────────────────────────┘
```

### 5.4 Text Serialization Format

Structured sections are serialized to/from a single text blob:

```
CHIEF COMPLAINT:
Joint pain and morning stiffness

HISTORY OF PRESENT ILLNESS:
45-year-old female presenting with progressive joint pain over 3 months.
Morning stiffness lasting >1 hour. Bilateral hand involvement.

PHYSICAL EXAMINATION:
Vitals stable. Bilateral MCP swelling noted. No rashes.

ASSESSMENT:
Rheumatoid arthritis, likely early stage

PLAN:
1. Start methotrexate 15mg weekly
2. Labs: CBC, LFTs, ESR, CRP
3. Rheumatology referral

MEDICATIONS:
Methotrexate 15mg PO weekly
Folic acid 1mg daily

FOLLOW-UP:
Return in 4 weeks for lab review
```

### 5.5 Smart Detection Integration

When user clicks "Accept & Apply" in review modal:

```javascript
// Mapping from extraction to structured sections
reviewData.chief_complaint  → Chief Complaint input
reviewData.hpi              → HPI textarea
reviewData.physical_exam    → Physical Exam textarea
reviewData.assessment       → Assessment textarea
reviewData.plan             → Plan textarea
reviewData.medications      → Medications textarea (array.join('\n'))
reviewData.follow_up        → Follow-up input
```

---

## 6. Backend API Endpoints

**Location**: `backend/routes/medical_notes.py`, `backend/routes/joint_assessments.py`

### 6.1 Medical Notes API

#### Extract Entities (NLP Processing)

```http
POST /api/v1/medical_notes/extract
Content-Type: application/json

Request:
{
  "text": "string (required, min_length=1)"
}

Response:
{
  "success": true,
  "raw_entities": [
    {
      "text": "methotrexate",
      "type": "DRUG",
      "start": 45,
      "end": 57,
      "is_negated": false
    }
  ],
  "structured": {
    "chief_complaint": "string",
    "hpi": "string",
    "physical_exam": "string",
    "assessment": "string",
    "plan": "string",
    "medications": ["array"],
    "conditions": ["array"],
    "allergies": ["array"],
    "follow_up": "string"
  }
}
```

#### Save Draft (Auto-save)

```http
POST /api/v1/medical_notes/draft
Content-Type: application/json

Request:
{
  "visit_id": 123,
  "text": "Full note text..."
}

Response:
{
  "success": true,
  "note_id": 456,
  "status": "draft",
  "draft_saved_at": "2024-01-15T10:30:00Z",
  "message": "✅ Draft auto-saved"
}
```

#### Finalize Note

```http
POST /api/v1/medical_notes/finalize
Content-Type: application/json

Request:
{
  "note_id": 456,
  "text": "Final note text..."
}

Response:
{
  "success": true,
  "note_id": 456,
  "status": "finalized",
  "signed_at": "2024-01-15T11:00:00Z",
  "entities_extracted": 12,
  "processing_time_ms": 234.5,
  "entities": [ /* first 5 entities */ ],
  "message": "✅ Note finalized and NLP processed"
}
```

### 6.2 Joint Assessments API

#### Save Joint Assessment

```http
POST /api/v1/joint_assessments
Content-Type: application/json

Request:
{
  "visit_id": 123,
  "joints": [
    {
      "joint_id": "l_shoulder",
      "has_tenderness": true,
      "has_pain": false,
      "swelling_grade": 2
    },
    {
      "joint_id": "r_mcp2",
      "tenderness": 1,
      "pain": 0,
      "swelling": 1
    }
  ],
  "summary": {
    "tjc": 5,
    "sjc": 3,
    "esr": 28.5,
    "pga": 60,
    "pg_scale": 6,
    "das28": 4.2
  }
}

Response:
{
  "success": true,
  "visit_id": 123,
  "joints_saved": 28,
  "summary_saved": true,
  "message": "Saved 28 joint assessments"
}
```

#### Get Joint Assessment

```http
GET /api/v1/joint_assessments/visit/123

Response:
{
  "visit_id": 123,
  "joints": [
    {
      "id": 1,
      "joint_id": "l_shoulder",
      "has_tenderness": true,
      "has_pain": false,
      "swelling_grade": 2,
      "assessed_at": "2024-01-15T10:30:00Z"
    }
  ],
  "total_joints": 28
}
```

---

## 7. NLP Engine & Entity Extraction

**Location**: `backend/services/nlp_engine.py`

### 7.1 Model Configuration

| Property | Value |
|----------|-------|
| Framework | spaCy 3.7 |
| Model | `en_core_sci_md` (scispaCy) |
| Loading | Lazy (on first extraction) |
| Instance | Singleton (`nlp_engine`) |

### 7.2 Entity Types

The `en_core_sci_md` model extracts the following entity types:

| Entity Type | Description | Example |
|-------------|-------------|---------|
| `CHEMICAL` | Chemical compounds | acetylsalicylic acid |
| `DRUG` | Medication names | methotrexate, prednisone |
| `DISEASE` | Disease names | rheumatoid arthritis, lupus |
| `SYNDROME` | Syndrome names | Sjogren's syndrome |
| `DISORDER` | Disorder names | anxiety disorder |
| `GENE` | Gene references | HLA-B27 |
| `PROTEIN` | Protein references | anti-CCP antibodies |

### 7.3 Processing Pipeline

```python
def process_note(note_text: str) -> dict:
    """
    1. Load model if not already loaded
    2. Run spaCy pipeline on text
    3. Extract entities with spans
    4. Return structured result
    """

    # Returns:
    return {
        "success": True,
        "entities": [
            {
                "text": "methotrexate",
                "type": "DRUG",
                "start": 45,      # Character offset
                "end": 57,
                "is_negated": False  # TODO: negation detection
            }
        ],
        "entity_count": 5,
        "processing_time_ms": 123.4,
        "model_version": "en_core_sci_md"
    }
```

### 7.4 Heuristic Section Extraction

The `/extract` endpoint applies regex-based heuristics to parse sections:

```python
SECTION_PATTERNS = {
    'chief_complaint': r'(?:patient\s+)?complains\s+of|cc:|chief\s+complaint',
    'assessment': r'(?:assessment|diagnosis|impression)',
    'plan': r'(?:plan|recommendation)',
    'allergies': r'(?:allergic\s+to|allergy|allergies)',
    'follow_up': r'(?:follow[\-\s]?up|f/u|return\s+in)'
}

ENTITY_TO_FIELD_MAPPING = {
    'CHEMICAL': 'medications',
    'DRUG': 'medications',
    'DISEASE': 'conditions',
    'SYNDROME': 'conditions',
    'DISORDER': 'conditions'
}
```

### 7.5 Performance Characteristics

| Metric | Typical Value |
|--------|---------------|
| Model load time | 2-5 seconds (first call only) |
| Processing time | 50-500ms per note |
| Memory usage | ~500MB (model in memory) |
| Throughput | 10-20 notes/second |

---

## 8. Data Models & Validation

**Location**: `backend/schemas.py`

### 8.1 Medical Note Schemas

```python
from pydantic import BaseModel, Field
from typing import Optional, List

class MedicalNoteExtractRequest(BaseModel):
    text: str = Field(..., min_length=1)

class MedicalNoteDraftRequest(BaseModel):
    visit_id: int
    text: Optional[str] = None
    raw_text: Optional[str] = None  # Alias

    def get_text(self) -> str:
        return self.text or self.raw_text or ''

class MedicalNoteFinalizeRequest(BaseModel):
    note_id: int
    text: Optional[str] = None
    final_text: Optional[str] = None  # Alias
```

### 8.2 Joint Assessment Schemas

```python
class JointAssessmentItem(BaseModel):
    joint_id: str = Field(..., min_length=1)

    # Boolean format (database columns)
    has_tenderness: Optional[bool] = None
    has_pain: Optional[bool] = None
    swelling_grade: Optional[int] = Field(None, ge=0, le=3)

    # Integer format (0-3 scale)
    tenderness: Optional[int] = Field(None, ge=0, le=3)
    pain: Optional[int] = Field(None, ge=0, le=3)
    swelling: Optional[int] = Field(None, ge=0, le=3)

    def get_tenderness(self) -> int:
        if self.tenderness is not None:
            return self.tenderness
        return 1 if self.has_tenderness else 0

    def get_pain(self) -> int:
        if self.pain is not None:
            return self.pain
        return 1 if self.has_pain else 0

    def get_swelling(self) -> int:
        if self.swelling is not None:
            return self.swelling
        return self.swelling_grade or 0

class JointAssessmentSummary(BaseModel):
    tjc: Optional[int] = Field(None, ge=0, le=28)
    sjc: Optional[int] = Field(None, ge=0, le=28)
    esr: Optional[float] = Field(None, ge=0)
    pga: Optional[float] = Field(None, ge=0, le=100)
    pg_scale: Optional[int] = Field(None, ge=1, le=10)
    das28: Optional[float] = Field(None, ge=0)

class JointAssessmentCreate(BaseModel):
    visit_id: int
    joints: List[JointAssessmentItem]
    summary: Optional[JointAssessmentSummary] = None
```

### 8.3 Validation Rules Summary

| Field | Validation |
|-------|------------|
| `text` (extraction) | Required, min_length=1 |
| `visit_id` | Required integer |
| `joint_id` | Required, non-empty string |
| `swelling_grade` | 0-3 inclusive |
| `pg_scale` | 1-10 inclusive |
| `pga` | 0-100 inclusive |
| `tjc`, `sjc` | 0-28 inclusive |

---

## 9. State Management & Auto-Save

**Location**: `backend/templates/fragments/medical_note_form.html`

### 9.1 Auto-Save Configuration

| Setting | Value |
|---------|-------|
| Interval | 30 seconds |
| Trigger | `isDirty` flag true |
| Scope | Note text + Joint data |
| Method | Coordinated batch save |

### 9.2 Coordinated Save Flow

```javascript
async function coordinatedSave() {
    // 1. Validate context
    if (!window.visitId) return;

    // 2. Emit start event
    document.dispatchEvent(new CustomEvent('coordinatedSaveStart'));

    // 3. Aggregate structured note sections
    const structured = aggregateStructuredInputs();

    // 4. Get dictation text
    const dictation = document.getElementById('dictation-input')?.value || '';

    // 5. Combine all text
    const fullText = dictation + '\n\n' + structured;

    // 6. Save medical note draft
    await fetch('/api/v1/medical_notes/draft', {
        method: 'POST',
        body: JSON.stringify({ visit_id: window.visitId, text: fullText })
    });

    // 7. Save joint assessment if available
    if (window.getJointData && window.getJointSummary) {
        const joints = window.getJointData();
        const summary = window.getJointSummary();

        await fetch('/api/v1/joint_assessments', {
            method: 'POST',
            body: JSON.stringify({ visit_id: window.visitId, joints, summary })
        });
    }

    // 8. Update UI and emit end event
    updateSaveStatus('Saved at ' + new Date().toLocaleTimeString());
    document.dispatchEvent(new CustomEvent('coordinatedSaveEnd', { detail: { success: true }}));
}
```

### 9.3 Dirty State Tracking

```javascript
// Sources that set isDirty = true:
- Structured section input change (x-on:input)
- Dictation textarea change
- Joint state change (via window._markDirty())
- VAS scale selection change

// Reset conditions:
- Successful save completes
- Note finalized
```

### 9.4 Event System

| Event | Trigger | Payload |
|-------|---------|---------|
| `coordinatedSaveStart` | Before save begins | None |
| `coordinatedSaveEnd` | After save completes | `{ success: boolean, error?: string }` |

---

## 10. Data Flow Architecture

### 10.1 Complete System Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              FRONTEND                                    │
├───────────────────┬───────────────────┬─────────────────────────────────┤
│   Smart Detection │     Joint Map     │       Structured Note           │
│                   │                   │                                 │
│ ┌───────────────┐ │ ┌───────────────┐ │ ┌─────────────────────────────┐ │
│ │ Dictation     │ │ │ Konva.js      │ │ │ Chief Complaint             │ │
│ │ Textarea      │ │ │ 28-Joint      │ │ │ HPI                         │ │
│ │               │ │ │ Diagram       │ │ │ Physical Exam               │ │
│ │ Voice Rec 🎤  │ │ │               │ │ │ Assessment / Plan           │ │
│ │ Extract ✨    │ │ │ TJC: [ ]      │ │ │ Medications / Follow-up     │ │
│ └───────┬───────┘ │ │ SJC: [ ]      │ │ └─────────────┬───────────────┘ │
│         │         │ │ ESR: [ ]      │ │               │                 │
│         │         │ │ VAS: 1-10     │ │               │                 │
│         │         │ │ DAS28: [    ] │ │               │                 │
│         │         │ └───────┬───────┘ │               │                 │
└─────────┼─────────┴─────────┼─────────┴───────────────┼─────────────────┘
          │                   │                         │
          │  ┌────────────────┴─────────────────────────┘
          │  │  Every 30s if dirty
          │  ▼
    ┌─────┴──────────────────────────────┐
    │      coordinatedSave()             │
    │  ┌───────────────────────────────┐ │
    │  │ 1. Aggregate all text         │ │
    │  │ 2. POST /api/v1/notes/draft   │ │
    │  │ 3. POST /api/v1/joints        │ │
    │  └───────────────────────────────┘ │
    └─────────────┬──────────────────────┘
                  │
┌─────────────────┼──────────────────────────────────────────────────────┐
│                 │                    BACKEND                            │
│                 ▼                                                       │
│    ┌───────────────────────────────────────────────────────────────┐   │
│    │                     Flask API Routes                          │   │
│    │  ┌─────────────────┐  ┌─────────────────┐  ┌───────────────┐  │   │
│    │  │ /notes/extract  │  │ /notes/draft    │  │ /joints       │  │   │
│    │  │ /notes/finalize │  │ /notes/fragment │  │ /joints/visit │  │   │
│    │  └────────┬────────┘  └────────┬────────┘  └───────┬───────┘  │   │
│    └───────────┼────────────────────┼───────────────────┼──────────┘   │
│                │                    │                   │              │
│    ┌───────────▼────────┐           │                   │              │
│    │   NLP Engine       │           │                   │              │
│    │   (spaCy)          │           │                   │              │
│    │   en_core_sci_md   │           │                   │              │
│    └────────────────────┘           │                   │              │
│                                     │                   │              │
│    ┌────────────────────────────────┴───────────────────┴──────────┐   │
│    │                        SQLite Database                         │   │
│    │  ┌───────────┐ ┌───────────┐ ┌─────────────┐ ┌──────────────┐ │   │
│    │  │ patients  │ │  visits   │ │medical_notes│ │joint_assess- │ │   │
│    │  │           │ │           │ │             │ │   ments      │ │   │
│    │  └───────────┘ └───────────┘ └─────────────┘ └──────────────┘ │   │
│    └───────────────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────────────────┘
```

### 10.2 Data Relationships

```
Patient (1) ──────┬──────── (*) Visit
                  │
                  └──── Visit (1) ──┬──── (1) Medical Note
                                    │
                                    ├──── (28) Joint Assessments
                                    │
                                    ├──── (1) Joint Assessment Summary
                                    │
                                    └──── (*) Voice Transcriptions
```

---

## 11. ML Training Data Considerations

### 11.1 Available Training Signals

| Data Type | Format | Cardinality | ML Use Case |
|-----------|--------|-------------|-------------|
| **Clinical Notes** | Free text | 1 per visit | NER, section classification, summarization |
| **NLP Entities** | Labeled spans | N per note | Named entity recognition |
| **Section Boundaries** | Formatted text | 7 sections/note | Section segmentation |
| **Joint States** | Multi-label binary | 28 × 3 per visit | Multi-label classification |
| **DAS28 Scores** | Continuous float | 1 per assessment | Regression |
| **Severity Categories** | 4 classes | 1 per assessment | Classification |
| **Temporal Pairs** | (draft, finalized) | 2 per note | Text completion/editing |

### 11.2 Entity Annotation Schema

```json
{
  "text": "Patient started on methotrexate 10mg weekly for RA.",
  "entities": [
    {"start": 19, "end": 31, "label": "DRUG", "text": "methotrexate"},
    {"start": 32, "end": 36, "label": "DOSAGE", "text": "10mg"},
    {"start": 37, "end": 43, "label": "FREQUENCY", "text": "weekly"},
    {"start": 48, "end": 50, "label": "DISEASE", "text": "RA"}
  ]
}
```

### 11.3 Joint Assessment Vector

For ML, each assessment can be vectorized as:

```python
# 28 joints × 3 features = 84-dimensional vector
joint_vector = [
    # l_shoulder
    tenderness_l_shoulder,  # 0 or 1
    pain_l_shoulder,        # 0 or 1
    swelling_l_shoulder,    # 0, 1, 2, or 3
    # l_elbow
    tenderness_l_elbow,
    pain_l_elbow,
    swelling_l_elbow,
    # ... 26 more joints
]

# Summary features
summary_vector = [
    tjc,          # 0-28
    sjc,          # 0-28
    esr,          # 0-150+ (continuous)
    pga,          # 0-100
    das28_score   # 0-10 (continuous)
]
```

### 11.4 Suggested Training Tasks

#### Task 1: Named Entity Recognition (NER)
- **Input**: Clinical note text
- **Output**: Entity spans with labels
- **Labels**: DRUG, DISEASE, DOSAGE, FREQUENCY, ANATOMY

#### Task 2: Section Classification
- **Input**: Paragraph or sentence
- **Output**: Section label
- **Labels**: CHIEF_COMPLAINT, HPI, PHYSICAL_EXAM, ASSESSMENT, PLAN, MEDICATIONS, FOLLOW_UP

#### Task 3: Disease Activity Prediction
- **Input**: Joint assessment vector (84-dim) + lab values
- **Output**: DAS28 score (regression) or severity class (classification)

#### Task 4: Clinical Summarization
- **Input**: Full clinical note
- **Output**: Structured sections (chief complaint, assessment, plan)

#### Task 5: Medication Extraction
- **Input**: Clinical note text
- **Output**: List of (drug, dose, frequency, route) tuples

### 11.5 Data Quality Considerations

| Aspect | Status | Notes |
|--------|--------|-------|
| Negation detection | TODO | Not implemented; entities may be negated |
| Temporal context | Partial | Timestamps available but not linked to entities |
| Inter-annotator agreement | N/A | Single-pass NLP extraction |
| Section boundaries | Heuristic | Regex-based, may miss edge cases |
| Swelling severity | Ordinal | 0-3 scale needs calibration |

---

## 12. File Location Reference

| Component | File Path |
|-----------|-----------|
| **Database Schema** | `backend/database/init_schema.sql` |
| **Medical Notes Routes** | `backend/routes/medical_notes.py` |
| **Joint Assessment Routes** | `backend/routes/joint_assessments.py` |
| **NLP Engine** | `backend/services/nlp_engine.py` |
| **Pydantic Schemas** | `backend/schemas.py` |
| **Database Utils** | `backend/utils/database.py` |
| **Medical Note Form (3 tabs)** | `backend/templates/fragments/medical_note_form.html` |
| **Joint Assessment Fragment** | `backend/templates/fragments/joint_assessment.html` |
| **Medical Note Logic (Alpine.js)** | `frontend/src/modules/medical_note_logic.js` |
| **Joint Assessment Logic (Alpine.js)** | `frontend/src/modules/joint_assessment_logic.js` |
| **Joint Diagram (Konva.js)** | `frontend/src/modules/joint_diagram.js` |
| **App Entry Point** | `backend/app.py` |

---

## Appendix A: Joint ID Reference

| Joint ID | Anatomical Name | Side |
|----------|-----------------|------|
| `l_shoulder` | Shoulder | Left |
| `r_shoulder` | Shoulder | Right |
| `l_elbow` | Elbow | Left |
| `r_elbow` | Elbow | Right |
| `l_wrist` | Wrist | Left |
| `r_wrist` | Wrist | Right |
| `l_knee` | Knee | Left |
| `r_knee` | Knee | Right |
| `l_mcp1` | 1st Metacarpophalangeal (thumb) | Left |
| `l_mcp2` | 2nd Metacarpophalangeal (index) | Left |
| `l_mcp3` | 3rd Metacarpophalangeal (middle) | Left |
| `l_mcp4` | 4th Metacarpophalangeal (ring) | Left |
| `l_mcp5` | 5th Metacarpophalangeal (pinky) | Left |
| `l_pip1` | Interphalangeal (thumb) | Left |
| `l_pip2` | 2nd Proximal Interphalangeal | Left |
| `l_pip3` | 3rd Proximal Interphalangeal | Left |
| `l_pip4` | 4th Proximal Interphalangeal | Left |
| `l_pip5` | 5th Proximal Interphalangeal | Left |
| `r_mcp1` | 1st Metacarpophalangeal (thumb) | Right |
| `r_mcp2` | 2nd Metacarpophalangeal (index) | Right |
| `r_mcp3` | 3rd Metacarpophalangeal (middle) | Right |
| `r_mcp4` | 4th Metacarpophalangeal (ring) | Right |
| `r_mcp5` | 5th Metacarpophalangeal (pinky) | Right |
| `r_pip1` | Interphalangeal (thumb) | Right |
| `r_pip2` | 2nd Proximal Interphalangeal | Right |
| `r_pip3` | 3rd Proximal Interphalangeal | Right |
| `r_pip4` | 4th Proximal Interphalangeal | Right |
| `r_pip5` | 5th Proximal Interphalangeal | Right |

---

## Appendix B: Entity Type Examples

| Type | Examples |
|------|----------|
| `DRUG` | methotrexate, prednisone, humira, enbrel, plaquenil |
| `DISEASE` | rheumatoid arthritis, lupus, psoriatic arthritis, gout |
| `SYNDROME` | Sjogren's syndrome, Raynaud's phenomenon |
| `DISORDER` | anxiety, depression, fibromyalgia |
| `CHEMICAL` | folic acid, vitamin D, calcium |
| `ANATOMY` | joints, hands, wrists, knees, shoulders |

---

*Report generated for ML model training research purposes.*
