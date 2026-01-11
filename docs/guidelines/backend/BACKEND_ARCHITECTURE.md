# Backend Architecture Guidelines

These guidelines define the structure and patterns for the Flask backend.

---

## 1. Project Structure

```
backend/
├── app.py                 # Application entry point
├── config.py              # Configuration management
├── schemas.py             # Pydantic models
├── database/
│   ├── init_db.py         # Database initialization
│   └── init_schema.sql    # SQL schema
├── routes/
│   ├── __init__.py        # Blueprint exports
│   ├── patients.py        # Patient CRUD
│   ├── visits.py          # Visit management
│   ├── medical_notes.py   # Medical notes + NLP extraction
│   ├── joint_assessments.py # Joint assessment data
│   └── voice.py           # Voice transcription (VOSK)
├── nlp_config/
│   └── nlp_config.py      # NLP version selection & factory
├── services/
│   ├── __init__.py
│   ├── nlp_engine.py      # spaCy NLP processing (legacy)
│   ├── base_extractor.py  # Abstract base class for extractors
│   ├── regex_entity_extractor.py  # Version A (regex, no dependencies)
│   ├── mtl_entity_extractor.py    # Version B (GatorTron transformer)
│   ├── two_tier_extractor.py      # Version C (GatorTron + SapBERT)
│   ├── ensemble_extractor.py      # Version D (weighted ensemble)
│   ├── biolinkbert_extractor.py   # Contextual inference engine
│   └── abbreviation_utils.py      # Medical abbreviation expansion
├── utils/
│   ├── __init__.py
│   └── database.py        # Database connection utilities
├── templates/
│   ├── base.html
│   └── fragments/         # HTMX HTML fragments
├── static/
│   └── models/            # VOSK model files
├── data/
│   └── models/            # ML model files (GatorTron, BioLinkBERT)
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

## 4. ML Entity Extraction

The project uses a 4-tier entity extraction architecture with progressive complexity.

### 4.1 Version Comparison

| Version | Model | Accuracy | Dependencies | Use Case |
|---------|-------|----------|--------------|----------|
| A | Regex V2.2 | ~85% F1 | None | Fast fallback, always available |
| B | GatorTron-Rheum | 85-90% F1 | transformers, torch | Balanced accuracy/speed |
| C | Two-Tier (B + SapBERT) | 90-91% F1 | + sapbert | UMLS entity linking |
| D | Ensemble (A+C+BioLinkBERT) | 93-95% F1 | All | Production (weighted voting) |

### 4.2 Entity Types

All extractors produce these entity types:
- `MEDICATION` - Drug names (methotrexate, prednisone)
- `DOSAGE` - Amounts (15mg, 10mg/week)
- `FREQUENCY` - Timing (weekly, twice daily)
- `SYMPTOM` - Clinical symptoms (joint pain, fatigue)
- `DISEASE` - Conditions (rheumatoid arthritis, lupus)
- `LAB_TEST` - Lab values (ESR, CRP, RF)

### 4.3 Factory Pattern

Use `get_extractor()` to obtain the appropriate extractor:

```python
from nlp_config import get_extractor

# Uses NLP_VERSION from environment (default: 'A')
extractor = get_extractor()
result = extractor.extract("Patient takes methotrexate 15mg weekly")

# Force specific version
extractor_d = get_extractor('D')
```

### 4.4 BaseEntityExtractor Interface

All extractors implement this interface:

```python
class BaseEntityExtractor:
    def extract(self, text: str) -> dict:
        """Returns {entities, version, model_name, processing_time_ms}"""

    def get_version(self) -> str:
        """Returns 'A', 'B', 'C', or 'D'"""

    def get_model_name(self) -> str:
        """Returns human-readable model name"""
```

---

## 5. Database Access Rules

### 5.1 Always Use Utilities

```python
# ✅ Correct
from utils.database import get_db, get_db_context

# ❌ Wrong
import sqlite3
conn = sqlite3.connect('database/clinical_ehr.db')
```

### 5.2 Use Context Manager for Transactions

```python
# ✅ Correct: Auto-commit/rollback
from utils.database import get_db_context

with get_db_context() as conn:
    cursor = conn.cursor()
    cursor.execute('INSERT INTO ...')
    # Commits automatically on success
    # Rolls back automatically on exception
```

### 5.3 Close Connections

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

## 6. Configuration Management

### 6.1 Environment Variables

Use `.env` file for local development:
```
ENVIRONMENT=development
API_PORT=8000
SPACY_MODEL=en_core_sci_md
```

### 6.2 ML Configuration Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `NLP_VERSION` | A | Extractor version (A, B, C, or D) |
| `NLP_MODEL_PATH` | data/models | Path to ML model files |
| `NLP_TIMEOUT_MS` | 2000 | Inference timeout in milliseconds |
| `NLP_FALLBACK_ENABLED` | true | Enable fallback chain on errors |

### 6.3 Accessing Config

```python
from config import get_config

config = get_config()
print(config.API_PORT)  # 8000
print(config.DEBUG)     # True in development
```

---

## 7. Error Handling

### 7.1 Standard Error Response

```python
return jsonify({'error': 'Patient not found'}), 404
```

### 7.2 Error Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request (validation error) |
| 404 | Not Found |
| 500 | Internal Server Error |

---

## 8. Reuse Guidelines

*   **Reuse Existing Files**: Modify existing routes/services instead of creating new ones.
*   **Add to Structure**: New features should fit into existing folders (`routes/`, `services/`).
*   **Avoid Duplication**: Check if functionality already exists before implementing.

---

## 9. Reference

*   `app.py` - Blueprint registration example
*   `utils/database.py` - Database utilities
*   `config.py` - Configuration classes
*   `nlp_config/nlp_config.py` - ML version selection and factory
*   `services/*_extractor.py` - Entity extraction implementations
