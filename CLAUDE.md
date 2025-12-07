# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Rheumatology Electronic Health Record system for rural clinics, featuring offline voice recognition (VOSK), medical NLP (spaCy/scispaCy), and interactive 28-joint assessment with DAS28-ESR calculation.

## Commands

### Backend (Flask)
```powershell
# Setup
python -m venv venv
.\venv\Scripts\Activate
pip install -r requirements.txt
python -m spacy download en_core_sci_md

# Run server
cd backend
python app.py  # Starts at http://localhost:5000

# Initialize database
python -c "from utils.database import get_db; conn = get_db(); conn.executescript(open('database/init_schema.sql').read())"

# Tests
pytest
pytest --cov=backend --cov-report=html
pytest tests/backend/test_patients.py  # Single file

# Linting
ruff check backend/
black backend/
mypy backend/
```

### Frontend (Node.js)
```powershell
npm install

# Development
npm run dev        # Vite dev server at :5173 (proxies to Flask)
npm run sass:dev   # SCSS with source maps

# Production build
npm run build      # Builds SCSS + Webpack bundle to backend/static/dist
npm run sass:build # SCSS only (compressed)
npm run build:js   # Webpack only
```

## Architecture

### Stack
- **Backend**: Flask 3.0 (async) + SQLite (WAL mode) + Pydantic validation
- **NLP**: spaCy 3.7 + scispaCy (`en_core_sci_md`) - lazy loaded
- **Speech**: VOSK offline recognition (50MB model)
- **Frontend**: Jinja2 templates + HTMX + Alpine.js + TypeScript/React components
- **Build**: Vite (dev) + Webpack (prod) → `backend/static/dist`
- **Styling**: Pico.css (via SCSS) + Tailwind utilities

### Key Patterns

**API Routes** (`backend/routes/`): Flask blueprints with Pydantic request/response validation. All routes prefixed `/api/v1/`.

**Database**: SQLite with `get_db()` returning Row-factory connections. Use `get_db_context()` for automatic commit/rollback.

**NLP Engine** (`backend/services/nlp_engine.py`): Global singleton `nlp_engine` with lazy model loading. Call `process_note(text)` to extract medical entities.

**Frontend Modules** (`frontend/src/modules/`): Alpine.js components (joint_assessment_logic.js, medical_note_logic.js) with auto-save every 30 seconds.

**Joint Assessment**: Konva.js canvas for 28-joint diagram. State stored in `joints` object with tenderness/pain/swelling per joint. DAS28-ESR calculated from TJC, SJC, ESR, PGA.

### Database Schema
Core tables: `patients`, `visits`, `medical_notes`, `joint_assessments`, `voice_transcriptions`, `joint_assessment_summaries`

## Configuration

Environment variables (`.env`):
- `ENVIRONMENT`: development/production
- `SPACY_MODEL`: NLP model (default: en_core_sci_md)
- `API_PORT`: Server port (default: 5000)
- `API_HOST`: Host binding (default: localhost)

## API Endpoints

- `GET/POST /api/v1/patients` - Patient CRUD
- `GET/POST /api/v1/visits` - Visit management
- `POST /api/v1/medical_notes/draft` - Auto-save draft
- `POST /api/v1/medical_notes/finalize` - Finalize + NLP extraction
- `POST /api/v1/joint_assessments` - Save joint data
- `POST /api/v1/voice/transcribe` - VOSK transcription
- `GET /api/v1/health` - Health check
