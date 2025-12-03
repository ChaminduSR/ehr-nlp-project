# Backend Architecture Guidelines

These guidelines define the structure and patterns for the Flask backend.

---

## 1. Project Structure

```
backend/
├── app.py                 # Application entry point
├── config.py              # Configuration management
├── main.py                # Alternative entry point
├── database/
│   ├── init_db.py         # Database initialization
│   └── init_schema.sql    # SQL schema
├── routes/
│   ├── __init__.py        # Blueprint exports
│   ├── patients.py        # Patient CRUD + fragments
│   ├── visits.py          # Visit management
│   ├── medical_notes.py   # Medical notes + auto-save
│   ├── joint_assessments.py # Joint assessment data
│   └── voice.py           # Voice transcription (VOSK)
├── services/
│   ├── __init__.py
│   └── nlp_engine.py      # spaCy NLP processing
├── utils/
│   ├── __init__.py
│   └── database.py        # Database connection utilities
├── templates/
│   ├── base.html
│   └── fragments/         # HTMX HTML fragments
├── static/
│   └── models/            # VOSK model files
└── guidelines/            # This folder
```

---

## 2. Blueprint Pattern

All routes MUST be organized into Flask Blueprints.

**Naming Convention**:
*   Blueprint name: `<resource>_bp` (e.g., `patients_bp`)
*   URL Prefix: `/api/v1/<resource>` (e.g., `/api/v1/patients`)

**Example**:
```python
# backend/routes/patients.py
from flask import Blueprint

patients_bp = Blueprint('patients', __name__)

@patients_bp.route('', methods=['POST'])
def create_patient():
    ...

@patients_bp.route('/<int:patient_id>', methods=['GET'])
def get_patient(patient_id):
    ...

@patients_bp.route('/fragment', methods=['GET'])
def patients_fragment():
    ...
```

**Registration** (in `app.py`):
```python
from routes import patients_bp
app.register_blueprint(patients_bp, url_prefix='/api/v1/patients')
```

---

## 3. Service Layer Pattern

**Rule**: Keep business logic OUT of routes. Routes should only handle HTTP concerns.

**Structure**:
```
Route (HTTP) → Service (Logic) → Database (Data)
```

**Example**:
```python
# backend/services/nlp_engine.py
def extract_entities(text):
    nlp = get_nlp()
    doc = nlp(text)
    return [{'text': ent.text, 'label': ent.label_} for ent in doc.ents]

# backend/routes/medical_notes.py
from services.nlp_engine import extract_entities

@medical_notes_bp.route('/<int:note_id>/analyze', methods=['POST'])
def analyze_note(note_id):
    # Route only handles HTTP
    note = get_note_from_db(note_id)
    entities = extract_entities(note.text)  # Service handles logic
    return jsonify(entities)
```

---

## 4. Database Access Rules

### 4.1 Always Use Utilities

```python
# ✅ Correct
from utils.database import get_db, get_db_context

# ❌ Wrong
import sqlite3
conn = sqlite3.connect('database/clinical_ehr.db')
```

### 4.2 Use Context Manager for Transactions

```python
# ✅ Correct: Auto-commit/rollback
from utils.database import get_db_context

with get_db_context() as conn:
    cursor = conn.cursor()
    cursor.execute('INSERT INTO ...')
    # Commits automatically on success
    # Rolls back automatically on exception
```

### 4.3 Close Connections

```python
# ✅ Correct: Manual close
conn = get_db()
try:
    cursor = conn.cursor()
    cursor.execute('SELECT ...')
    result = cursor.fetchall()
finally:
    conn.close()
```

---

## 5. Configuration Management

### 5.1 Environment Variables

Use `.env` file for local development:
```
ENVIRONMENT=development
API_PORT=8000
SPACY_MODEL=en_core_sci_md
```

### 5.2 Accessing Config

```python
from config import get_config

config = get_config()
print(config.API_PORT)  # 8000
print(config.DEBUG)     # True in development
```

---

## 6. Error Handling

### 6.1 Standard Error Response

```python
return jsonify({'error': 'Patient not found'}), 404
```

### 6.2 Error Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request (validation error) |
| 404 | Not Found |
| 500 | Internal Server Error |

---

## 7. Reuse Guidelines

*   **Reuse Existing Files**: Modify existing routes/services instead of creating new ones.
*   **Add to Structure**: New features should fit into existing folders (`routes/`, `services/`).
*   **Avoid Duplication**: Check if functionality already exists before implementing.

---

## 8. Reference

*   `app.py` - Blueprint registration example
*   `utils/database.py` - Database utilities
*   `config.py` - Configuration classes
