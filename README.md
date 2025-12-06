# Rheumatology EHR with NLP & Voice Recognition 🏥

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![React 18+](https://img.shields.io/badge/react-18+-61DAFB.svg)](https://react.dev/)

A production-ready Electronic Health Record system designed for rheumatology clinics in rural and low-resource settings, featuring:
- 🎤 **Offline Voice Recognition** (VOSK) - No internet required
- 🧠 **Medical NLP** (spaCy + scispaCy) - Automated entity extraction
- 🖐️ **Interactive Joint Assessment** - Canvas-based 28-joint tracking
- 💾 **Auto-save** - Epic-style real-time saving
- ♿ **WCAG AAA Accessible** - Works on 10+ year old PCs (Modern Browser)
- 📡 **Offline-First** - Full functionality without connectivity

---

## 📋 Table of Contents
- [Tech Stack](#-tech-stack)
- [Features](#-key-features)
- [Quick Start](#-quick-start)
- [Architecture](#-architecture)
- [API Documentation](#-api-endpoints)
- [Development](#-development)
- [Deployment](#-deployment)
- [Project Structure](#-project-structure)

---

## 🛠️ Tech Stack

### Backend & Frontend (Unified)
- **Framework**: Flask 3.0.3 (Python 3.11+) + Async Support
- **Database**: SQLite3 with WAL mode (ACID compliance)
- **NLP**: spaCy 3.7.5 + scispaCy 0.5.5 (`en_core_sci_md`)
- **Speech**: VOSK 0.3.45 (offline voice recognition)
- **Frontend Logic**: React 19 + Alpine.js + TypeScript
- **State Management**: TanStack Query (for complex data)
- **Validation**: Zod (Frontend) + Pydantic (Backend)
- **Styling**: Pico.css + Tailwind CSS (Utility)
- **Canvas**: Konva.js (Lazy-loaded)
- **Build Tool**: Vite (Dev) + Webpack (Prod)
- **Bundle**: <150KB total (ES2020 Target, Modern Browsers)

### Development
- **Testing**: pytest + pytest-flask
- **Linting**: Ruff + Black + mypy
- **Editor**: VS Code with Python extensions

---

## ✨ Key Features

### 1. Voice-to-Text Medical Notes
- **VOSK offline speech recognition** (50MB model)
- Works on 2GB RAM, Pentium 4, Windows 7+
- Lazy loading or central server deployment
- 70-80% documentation time savings
- USB microphone support ($20-60)

### 2. NLP-Powered Entity Extraction
- Automatic extraction from finalized notes
- Identifies: symptoms, diagnoses, medications, lab values
- Medical vocabulary via scispaCy
- Processing time: <2 seconds per note

### 3. Interactive Joint Assessment
- Canvas-based 28-joint diagram (shoulders, elbows, wrists, hands, knees)
- 3-parameter tracking: Tenderness, Pain, Swelling (0-3 grades)
- Left-click: Cycle swelling grades
- Right-click: Toggle tenderness
- Real-time joint counts

### 4. DAS28-ESR Calculator
- Automatic calculation from joint assessment
- Color-coded disease activity:
  - 🟢 Remission (<2.6)
  - 🟡 Low (2.6-3.2)
  - 🟠 Moderate (3.2-5.1)
  - 🔴 High (>5.1)

### 5. Auto-Save System
- Drafts save every 30 seconds
- Visual indicator (saving/saved/error)
- Finalize workflow triggers NLP processing
- Zero data loss

### 6. Accessibility (WCAG AAA)
- 7:1 contrast ratio minimum
- Full keyboard navigation
- Screen reader compatible
- 48px touch targets
- Modern Browser support (Chrome, Firefox, Edge)

---

## 🚀 Quick Start

### Prerequisites
```bash
# Python 3.11 or higher
python --version

# Git
git --version
```

### 1. Clone Repository
```powershell
git clone https://github.com/ChaminduSR/ehr-nlp-project.git
cd ehr-nlp-project
```

### 2. Setup & Run

#### Install Dependencies
```powershell
# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate

# Install packages
pip install -r requirements.txt

# Download spaCy model (150MB)
python -m spacy download en_core_sci_md
```

#### Download VOSK Model (Optional - for voice recognition)
```powershell
# Download from: https://alphacephei.com/vosk/models
# Recommended: vosk-model-small-en-us-0.15.zip (50MB)

# Extract to:
mkdir backend\static\models
# Unzip to: backend\static\models\vosk-model-small-en-us-0.15\
```

#### Initialize Database
```powershell
cd backend
python -c "from utils.database import get_db; conn = get_db(); conn.executescript(open('database/init_schema.sql').read())"
```

#### Run Application
```powershell
cd backend
python app.py

# Application starts at: http://localhost:5000
```

### 3. Verify Installation
```powershell
# Open browser to:
http://localhost:5000
```

---

## 🏗️ Architecture

### System Overview
```
┌───────────────────────────────────────────┐
│              Flask Backend                │
│  (Serves HTML + API + NLP + Voice Logic)  │
└─────────────────────┬─────────────────────┘
                      │
          ┌───────────▼───────────┐
          │   Browser (Client)    │
          │  HTMX + Alpine.js     │
          └───────────────────────┘
                      │
          ┌───────────▼───────────┐
          │   Offline Services    │
          │  (SQLite, spaCy, VOSK)│
          └───────────────────────┘
```

### Backend Architecture
```
backend/
├── app.py                    # Flask application entry point
├── config.py                 # Environment configuration
├── routes/                   # API endpoints (blueprints)
│   ├── patients.py           # Patient CRUD
│   ├── visits.py             # Visit management
│   ├── medical_notes.py      # Auto-save + finalize + NLP
│   ├── joint_assessments.py  # Joint data persistence
│   └── voice.py              # VOSK transcription
├── services/
│   └── nlp_engine.py         # spaCy medical entity extraction
├── utils/
│   └── database.py           # SQLite connection with WAL mode
├── database/
│   ├── init_schema.sql       # Database schema (patients, visits, notes, joints)
│   └── clinical_ehr.db       # SQLite database file (auto-created)
└── static/
    └── models/               # VOSK models (downloaded separately)
```

### Database Schema (v3.0)
```sql
-- Core tables
patients (id, mrn, name, dob, gender, phone, diagnosis, created_at)
visits (id, patient_id, visit_date, visit_type, provider_name)
medical_notes (id, visit_id, note_text, status, finalized_at, nlp_processed)

-- Clinical data
joint_assessments (id, visit_id, joint_id, has_tenderness, has_pain, swelling_grade)
voice_transcriptions (id, medical_note_id, audio_duration, transcribed_text, confidence_score)

-- NLP output
medical_entities (id, medical_note_id, entity_text, entity_type, start_pos, end_pos)
```

---

## 📡 API Endpoints

### Base URL
```
http://localhost:8000/api/v1
```

### Patients
```http
POST   /patients              # Create patient
GET    /patients/{id}         # Get patient by ID
```

### Visits
```http
POST   /visits                # Create visit
GET    /visits/{id}           # Get visit details
```

### Medical Notes
```http
POST   /medical_notes/draft           # Auto-save draft (every 30s)
POST   /medical_notes/finalize        # Finalize note (triggers NLP)
GET    /medical_notes/{id}            # Get note + entities
```

### Joint Assessments
```http
POST   /joint_assessments             # Save joint array (28 joints)
GET    /joint_assessments/visit/{id}  # Get joints by visit
```

### Voice Transcription
```http
POST   /voice/transcribe      # VOSK voice-to-text (audio file → text)
```

### Health Check
```http
GET    /health                # Server status
```

### Example Request
```bash
# Create patient
curl -X POST http://localhost:8000/api/v1/patients \
  -H "Content-Type: application/json" \
  -d '{
    "mrn": "MRN-2025-001",
    "name": "Rajesh Kumar",
    "dob": "1975-06-15",
    "gender": "M",
    "phone": "+91-9876543210",
    "diagnosis": "Rheumatoid Arthritis"
  }'
```

---

## 💻 Development

### Run Tests
```powershell
# Activate virtual environment
.\venv\Scripts\Activate

# Run all tests
pytest

# With coverage
pytest --cov=backend --cov-report=html

# Test specific file
pytest tests/backend/test_patients.py
```

### Code Quality
```powershell
# Lint with Ruff
ruff check backend/

# Format with Black
black backend/

# Type check with mypy
mypy backend/
```

### Git workflow
```powershell
# Make changes
git add .

# Commit with a short descriptive message
git commit -m "feat: add new feature"

# Follow your project's branching and PR process (e.g. open a PR, select reviewers)
```

### Project Status
✅ **Backend**: Fully implemented (Flask + NLP + VOSK + SQLite)
🚧 **Frontend**: Components built, API integration in progress
📝 **Documentation**: Complete (master_project_complete_v3-1.md)

---

## 🚀 Deployment

### Requirements
- **Server**: 4GB RAM, 2 CPU cores (for central deployment)
- **Old PCs**: 2GB RAM, Pentium 4+ (client machines)
- **Network**: Local LAN (no internet required)
- **OS**: Windows 7+, Linux, macOS

### Production Deployment
```powershell
# 1. Set production environment
# Edit .env: ENVIRONMENT=production

# 2. Install production server
pip install gunicorn

# 3. Run with gunicorn (Linux/Mac)
gunicorn -w 4 -b 0.0.0.0:8000 backend.app:app

# 4. Or use waitress (Windows)
pip install waitress
waitress-serve --host=0.0.0.0 --port=8000 backend.app:app
```

### Clinic Server Setup (Recommended)
See `docs/master_project_complete_v3-1.md` for:
- Central VOSK server configuration
- Old PC client setup
- USB microphone installation
- Performance optimization
- Troubleshooting guide

---

## 📂 Project Structure

```
ehr-nlp-project/
├── backend/              # Flask API server
│   ├── app.py           # Main application
│   ├── routes/          # API endpoints
│   ├── services/        # NLP engine
│   ├── utils/           # Database helpers
│   ├── database/        # SQLite schema & DB file
│   └── static/          # VOSK models
├── frontend/            # React TypeScript app
│   ├── components/      # UI components
│   │   ├── ehr/        # Custom EHR components
│   │   ├── pages/      # Page components
│   │   └── ui/         # shadcn/ui components
│   └── styles/         # Tailwind CSS
├── data/               # Clinical data & annotations
├── docs/               # Project documentation
├── learning/           # NLP learning scripts
├── scripts/            # Utility scripts
├── tests/              # Test suites
├── requirements.txt    # Python dependencies
├── package.json        # Node.js dependencies
├── .env.example        # Environment template
└── README.md          # This file
```

---

## 📖 Documentation

- **[Master Project Guide v3.1](docs/master_project_complete_v3-1.md)** - Complete technical documentation
- **[Project Update Summary v3.1](docs/project-update-summary-v3-1.md)** - What's new in v3.1
- **[VS Code Setup Guide](VSCODE_SETUP_GUIDE.md)** - Development environment setup
- **[Design Specifications](frontend/DESIGN_SPECIFICATIONS.md)** - UI/UX design system
- **[Accessibility Checklist](frontend/ACCESSIBILITY_CHECKLIST.md)** - WCAG compliance

---

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file.

---

## 👤 Author

**ChaminduSR**
- GitHub: [@ChaminduSR](https://github.com/ChaminduSR)

---

## 🙏 Acknowledgments

- **spaCy & scispaCy** - Medical NLP
- **VOSK** - Offline speech recognition
- **shadcn/ui** - UI component library
- **Tailwind CSS** - Utility-first CSS

---

**Version 3.1** | Master's Capstone Project | November 2025
