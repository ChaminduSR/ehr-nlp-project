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

**What it is**: Load heavy models only when first needed, not on app startup.

**Models using lazy loading**:
| Model | Size | First Load | Subsequent |
|-------|------|------------|------------|
| VOSK | 50MB | 2-3s | <50ms |
| spaCy (en_core_sci_md) | 100MB | 5-8s | <100ms |
| GatorTron-Rheum | 345M params | 5-10s | <800ms |
| BioLinkBERT-base | 110M params | 3-5s | <500ms |
| SapBERT | 110M params | 3-5s | <300ms |

**Why it matters**:
*   App starts instantly (<1 second).
*   Doctor only waits on first NLP use.
*   Subsequent uses meet <800ms target for transformers.

**Implementation Pattern**:
```python
# backend/services/mtl_entity_extractor.py
class MTLEntityExtractor:
    _model = None
    _tokenizer = None

    def _load_model(self):
        if self._model is None:
            from transformers import AutoModelForTokenClassification, AutoTokenizer
            self._tokenizer = AutoTokenizer.from_pretrained(self.model_path)
            self._model = AutoModelForTokenClassification.from_pretrained(self.model_path)
        return self._model, self._tokenizer
```

**Rule**: Never import transformers/torch at the top of a file. Use class-level caching.

---

### 2.4 Async Support ✅

Flask 3.0+ enables native async endpoints.
Old sync code continues working unchanged.
New endpoints can use async/await for I/O ops.

**Implementation**:
```python
# Example: backend/routes/patients.py
@patients_bp.route('/api/v1/patients/bulk-load', methods=['POST'])
async def load_multiple():
    # Async database or API calls
    results = await some_async_service()
    return jsonify(results)
```

**Rule**: Use `async def` for I/O bound operations (external APIs, heavy DB queries).

---

### 2.5 Parallel Ensemble Execution ✅

**What it is**: Version D (Ensemble) runs multiple extractors in parallel using ThreadPoolExecutor.

**Why it matters**:
*   4 extractors (A + C + BioLinkBERT + inference) run simultaneously
*   Total time ≈ slowest extractor, not sum of all
*   Graceful degradation if one extractor times out

**Implementation**:
```python
# backend/services/ensemble_extractor.py
from concurrent.futures import ThreadPoolExecutor, as_completed

def extract(self, text: str) -> dict:
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {
            executor.submit(ext.extract, text): name
            for name, ext in self.extractors.items()
        }
        for future in as_completed(futures, timeout=self.timeout_ms/1000):
            # Merge results with weighted confidence
```

**Timeout handling**: Each extractor has individual timeout (default 2s). Failed extractors are skipped, results merged from successful ones.

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
| Lazy Load Transformers | ✅ Done | ~5-10s first use, <800ms after |
| Parallel Ensemble | ✅ Done | Version D runs 4 extractors in parallel |
| CPU-Optimized Inference | ✅ Done | No GPU required |
| Connection Pooling | ⬜ Future | High-traffic scenarios |
| Response Compression | ⬜ Future | Slow networks |

---

## 5. Reference

*   `master_project_complete_v3-1.md` - Full project documentation
*   `utils/database.py` - Database utilities with WAL mode
*   `services/nlp_engine.py` - spaCy NLP service with lazy loading
*   `services/mtl_entity_extractor.py` - GatorTron with lazy loading
*   `services/ensemble_extractor.py` - Parallel ensemble execution
*   `nlp_config/nlp_config.py` - Version selection and factory
