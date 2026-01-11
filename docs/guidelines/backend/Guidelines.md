# Backend Development Guidelines

These guidelines are specific to the Rheumatology EHR project and derived from `master_project_complete_v3-1.md`.

---

## 📁 Guidelines Index

| File | Purpose |
|------|---------|
| `BACKEND_PERFORMANCE.md` | Performance optimizations (WAL, lazy loading, fragments) |
| `BACKEND_ARCHITECTURE.md` | Project structure, Blueprints, Service layer |
| `API_STANDARDS.md` | REST conventions, error handling, pagination |

---

## 🎯 Core Principles

1.  **Old PC Compatibility**: Target 2GB RAM, Pentium 4, Windows 7 (Requires Modern Browser).
2.  **Offline-First**: All features must work without internet.
3.  **Reuse Existing Files**: Modify existing code, don't duplicate.
4.  **Performance First**: Fast startup, minimal memory footprint.

---

## 📂 File Organization & Reuse

*   **Structure**: Follow the established Flask Blueprint pattern.
    *   **Routes**: `backend/routes/` (One file per domain, e.g., `patients.py`)
    *   **Services**: `backend/services/` (Business logic, e.g., `nlp_engine.py`, `*_extractor.py`)
    *   **NLP Config**: `backend/nlp_config/` (ML version selection and factory)
    *   **Models**: `backend/models/` (Database models)
    *   **Utils**: `backend/utils/` (Shared helpers)
*   **New Features**:
    *   **Do not create new top-level folders** in `backend/` without approval.
    *   Add new routes to existing Blueprints if they fit the domain.
    *   Create a new Blueprint in `backend/routes/` only for distinct new modules.

---

## ✅ Implemented Features

| Feature | Status | Location |
|---------|--------|----------|
| Flask Blueprints | ✅ Done | `routes/*.py` |
| SQLite WAL Mode | ✅ Done | `utils/database.py` |
| Jinja Fragments (HTMX) | ✅ Done | `templates/fragments/*.html` |
| Lazy Load spaCy | ✅ Done | `services/nlp_engine.py` |
| VOSK Voice Recognition | ✅ Done | `routes/voice.py` |
| Patient CRUD | ✅ Done | `routes/patients.py` |
| Visit Management | ✅ Done | `routes/visits.py` |
| Medical Notes | ✅ Done | `routes/medical_notes.py` |
| Joint Assessments | ✅ Done | `routes/joint_assessments.py` |
| Pico CSS + SASS Theme | ✅ Done | `static/scss/custom-theme.scss` |
| Reports & Dashboard | ✅ Done | `routes/analytics.py` |
| ML Entity Extraction (4-tier) | ✅ Done | `services/*_extractor.py`, `nlp_config/` |
| BioLinkBERT Inference | ✅ Done | `services/biolinkbert_extractor.py` |

---

## ⬜ To Be Implemented

| Feature | Priority | Notes |
|---------|----------|-------|
| Auto-Save (30 sec) | High | Epic-style drafts |
| Connection Pooling | Low | For high-traffic scenarios |
| Response Compression | Low | For slow networks |
| PDF Export | Medium | Using WeasyPrint |

---

## 📋 Quick Reference

### Database Access
```python
from utils.database import get_db, get_db_context

# For reads
conn = get_db()
cursor = conn.cursor()
cursor.execute('SELECT ...')
conn.close()

# For writes (auto-commit/rollback)
with get_db_context() as conn:
    cursor = conn.cursor()
    cursor.execute('INSERT ...')
```

### Lazy Load Pattern
```python
_model = None

def get_model():
    global _model
    if _model is None:
        _model = load_heavy_model()
    return _model
```

### HTMX Fragment
```python
@bp.route('/fragment', methods=['GET'])
def my_fragment():
    data = fetch_data()
    return render_template('fragments/my_template.html', data=data)
```

---

## 📚 Reference Documents

*   `master_project_complete_v3-1.md` - Full project spec
*   `project-update-summary-v3-1.md` - Version history
