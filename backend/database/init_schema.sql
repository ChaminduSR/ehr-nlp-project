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
