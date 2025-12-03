# Backend Performance Guidelines

These guidelines are derived from `master_project_complete_v3-1.md` and optimized for **rural clinic deployment** on old PCs (2GB RAM, Windows 7).

---

## 1. Core Performance Principles

*   **Target Hardware**: 2GB RAM, Pentium 4/Core 2 Duo, Windows 7.
*   **Offline-First**: All features must work without internet connectivity.
*   **Minimal Dependencies**: Avoid heavy libraries that increase memory footprint.

---

## 2. Implemented Optimizations

### 2.1 Jinja Fragments (HTMX Pattern) ✅

**What it is**: Render HTML on the server and send small HTML fragments instead of JSON.

**Why it matters**:
*   Reduces client-side JavaScript parsing (important for old CPUs).
*   Smaller payload size compared to full-page reloads.
*   Works seamlessly with HTMX on the frontend.

**Implementation**:
```python
# Example: backend/routes/patients.py
@patients_bp.route('/fragment', methods=['GET'])
def patients_fragment():
    # ... fetch data ...
    return render_template('fragments/patients_list.html', patients=patients)
```

**Rule**: Use `/fragment` suffix for HTMX endpoints. Return HTML, not JSON.

---

### 2.2 SQLite WAL Mode ✅

**What it is**: Write-Ahead Logging for SQLite, enabling concurrent reads during writes.

**Why it matters**:
*   Multiple doctors can access the system simultaneously.
*   Improves read performance significantly.
*   Reduces database lock contention.

**Implementation** (in `utils/database.py`):
```python
def get_db():
    conn = sqlite3.connect(DATABASE_PATH, timeout=10.0)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA journal_mode=WAL')  # <-- Critical!
    return conn
```

**Rule**: Always use `get_db()` or `get_db_context()`. Never create raw connections.

---

### 2.3 Lazy Loading for ML Models ✅

**What it is**: Load heavy models (VOSK, spaCy) only when first needed, not on app startup.

**Why it matters**:
*   App starts instantly (<1 second).
*   Doctor only waits (5-8 seconds) on first voice/NLP use.
*   Subsequent uses are instant (<100ms).

**Implementation Pattern**:
```python
# backend/services/nlp_engine.py
_nlp_model = None

def get_nlp():
    global _nlp_model
    if _nlp_model is None:
        import spacy
        _nlp_model = spacy.load("en_core_sci_md")
    return _nlp_model
```

**Rule**: Never import heavy models at the top of a file. Use a `get_*()` function.

---

## 3. To Be Implemented

### 3.1 Connection Pooling (Future)

For high-traffic scenarios (5-10 simultaneous doctors), consider connection pooling.

```python
# Example: Using a simple pool
from queue import Queue
db_pool = Queue(maxsize=5)
```

**Status**: Not critical for MVP. Implement if performance issues arise.

---

### 3.2 Response Compression (Future)

Enable gzip compression for large HTML fragments.

```python
from flask_compress import Compress
Compress(app)
```

**Status**: Bundle size is already small (120KB). Implement if network is slow.

---

## 4. Performance Checklist

| Optimization | Status | Impact |
|--------------|--------|--------|
| Jinja Fragments | ✅ Done | Reduced client JS, faster rendering |
| SQLite WAL Mode | ✅ Done | Better concurrency |
| Lazy Load VOSK | ✅ Done | Instant app startup |
| Lazy Load spaCy | ✅ Done | Instant app startup |
| Connection Pooling | ⬜ Future | High-traffic scenarios |
| Response Compression | ⬜ Future | Slow networks |

---

## 5. Reference

*   `master_project_complete_v3-1.md` - Full project documentation
*   `utils/database.py` - Database utilities with WAL mode
*   `services/nlp_engine.py` - NLP service with lazy loading
