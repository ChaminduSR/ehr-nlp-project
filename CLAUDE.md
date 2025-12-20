# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Rheumatology Electronic Health Record system for rural clinics, featuring offline voice recognition (VOSK), medical NLP (spaCy/scispaCy), and interactive 28-joint assessment with DAS28-ESR calculation.

## Requirements

- **Node.js**: >=24.0.0 (uses native ESM, type stripping, test runner)
- **Python**: 3.11+
- **Vite**: 7.3.0 (baseline-widely-available target, LightningCSS)

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

### Frontend (Node.js 24+)
```powershell
npm install

# Development
npm run dev        # Vite 7 dev server at :5173 (proxies to Flask)
npm run sass:dev   # SCSS with source maps

# Production build
npm run build      # Builds SCSS + Vite bundle to backend/static/dist
npm run sass:build # SCSS only (compressed)
npm run build:js   # Vite build only

# Type checking & Testing
npm run typecheck  # TypeScript type check (no emit)
npm test           # Node.js native test runner

# Node 24 features - run TypeScript directly
node script.ts     # Native type stripping (no build needed)
```

## Architecture

### Stack
- **Backend**: Flask 3.0 (async) + SQLite (WAL mode) + Pydantic validation
- **NLP**: spaCy 3.7 + scispaCy (`en_core_sci_md`) - lazy loaded
- **Speech**: VOSK offline recognition (50MB model)
- **Frontend**: Jinja2 templates + HTMX + Alpine.js + TypeScript/React components
- **Build**: Vite 7.3 (baseline-widely-available, LightningCSS) → `backend/static/dist`
- **Styling**: Pico.css (via SCSS) + Tailwind utilities
- **Runtime**: Node.js 24 (ESM-only, native test runner, type stripping)

### Build Configuration

**Vite 7.3** (`vite.config.js`):
- `target: 'baseline-widely-available'` - chrome107, edge107, firefox104, safari16
- `cssMinify: 'lightningcss'` - faster CSS minification
- Warmup enabled for faster HMR
- Rolldown bundler available experimentally (4-16x faster builds)

**TypeScript** (`tsconfig.json`):
- `target: ES2023` / `lib: ES2023` - full Node 24 support
- `moduleResolution: bundler` - optimized for Vite
- `noEmit: true` - Vite handles transpilation

**Package** (`package.json`):
- `type: module` - native ESM
- `engines.node: >=24.0.0` - enforces Node 24+
- Native test runner via `node --test`

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

**Node 24 tip**: Use `node --env-file=.env` to load env vars natively (no dotenv needed).

## API Endpoints

- `GET/POST /api/v1/patients` - Patient CRUD
- `GET/POST /api/v1/visits` - Visit management
- `POST /api/v1/medical_notes/draft` - Auto-save draft
- `POST /api/v1/medical_notes/finalize` - Finalize + NLP extraction
- `POST /api/v1/joint_assessments` - Save joint data
- `POST /api/v1/voice/transcribe` - VOSK transcription
- `GET /api/v1/health` - Health check

## Node.js 24 Native Features Available

These features are available without external dependencies:
- **Type stripping**: Run `.ts` files directly with `node script.ts`
- **Native test runner**: `node --test` replaces Jest/Mocha
- **Native watch mode**: `node --watch` replaces nodemon
- **Native env loading**: `node --env-file=.env` replaces dotenv
- **Native WebSocket**: `new WebSocket()` for client connections
- **Native SQLite**: `node:sqlite` for lightweight database needs
- **require(esm)**: CJS can require ESM modules without flags

## Performance Optimization (Optional)

To try Rolldown bundler (experimental, 4-16x faster builds):
```json
{
  "devDependencies": {
    "vite": "npm:rolldown-vite@latest"
  }
}
```
