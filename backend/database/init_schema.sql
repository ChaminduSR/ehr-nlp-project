-- Core tables from your master document

CREATE TABLE patients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mrn TEXT UNIQUE NOT NULL,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    date_of_birth DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE visits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER NOT NULL,
    visit_date DATE NOT NULL,
    visit_type TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(id)
);

CREATE TABLE medical_notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    visit_id INTEGER NOT NULL,
    note_text TEXT NOT NULL,
    status TEXT DEFAULT 'draft' CHECK(status IN ('draft', 'finalized')),
    draft_saved_at TIMESTAMP,
    signed_by INTEGER,
    signed_at TIMESTAMP,
    entity_count INTEGER DEFAULT 0,
    processing_time_ms REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (visit_id) REFERENCES visits(id)
);

CREATE TABLE joint_assessments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    visit_id INTEGER NOT NULL,
    joint_id TEXT NOT NULL,
    has_tenderness BOOLEAN DEFAULT 0,
    has_pain BOOLEAN DEFAULT 0,
    swelling_grade INTEGER DEFAULT 0 CHECK(swelling_grade BETWEEN 0 AND 3),
    assessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (visit_id) REFERENCES visits(id)
);

CREATE TABLE voice_transcriptions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    medical_note_id INTEGER,
    audio_duration_seconds REAL,
    transcribed_text TEXT,
    model_used TEXT DEFAULT 'vosk-en-us',
    transcribed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (medical_note_id) REFERENCES medical_notes(id)
);

-- Joint assessment summary metrics (DAS28 + PGA 1-10)
CREATE TABLE IF NOT EXISTS joint_assessment_summaries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    visit_id INTEGER NOT NULL,
    tjc INTEGER,
    sjc INTEGER,
    esr REAL,
    pga REAL,
    pg_scale_1_10 INTEGER,
    das28_score REAL,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (visit_id) REFERENCES visits(id)
);

-- =============================================================================
-- NLP Entity Extraction Tables (Version D Ensemble Support)
-- =============================================================================

-- Store extracted entities for each medical note
CREATE TABLE IF NOT EXISTS extracted_entities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    medical_note_id INTEGER NOT NULL,
    text TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    start_pos INTEGER,
    end_pos INTEGER,
    confidence REAL,
    agreement INTEGER,
    versions_found TEXT,  -- JSON array: ["A", "C", "BioLink"]
    umls_cui TEXT,
    umls_name TEXT,
    is_negated BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (medical_note_id) REFERENCES medical_notes(id)
);

-- Store inferred diagnoses from Version D BioLinkBERT
CREATE TABLE IF NOT EXISTS inferred_diagnoses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    medical_note_id INTEGER NOT NULL,
    diagnosis_text TEXT NOT NULL,
    confidence REAL,
    matched_rule TEXT,
    rule_match_count INTEGER,
    rule_min_required INTEGER,
    linked_from TEXT,  -- JSON array of linked entities
    suggested_actions TEXT,  -- JSON array
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (medical_note_id) REFERENCES medical_notes(id)
);

-- Store entity relationships/links
CREATE TABLE IF NOT EXISTS entity_links (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    medical_note_id INTEGER NOT NULL,
    source_entity TEXT NOT NULL,
    target_entity TEXT NOT NULL,
    relationship TEXT NOT NULL,
    confidence REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (medical_note_id) REFERENCES medical_notes(id)
);

-- Indexes for faster lookups
CREATE INDEX IF NOT EXISTS idx_entities_note ON extracted_entities(medical_note_id);
CREATE INDEX IF NOT EXISTS idx_inferred_note ON inferred_diagnoses(medical_note_id);
CREATE INDEX IF NOT EXISTS idx_links_note ON entity_links(medical_note_id);
