# VS Code Setup Guide for EHR-NLP Project

This guide documents the complete setup process for the EHR-NLP project development environment.

## 📋 Table of Contents
1. [Prerequisites](#1-prerequisites)
2. [VS Code Extensions](#2-vs-code-extensions)
3. [Python Backend Setup](#3-python-backend-setup)
4. [React Frontend Setup](#4-react-frontend-setup)
5. [Git Configuration](#5-git-configuration)
6. [Project Structure](#6-project-structure)
7. [Debugging Configuration](#7-debugging-configuration)
8. [Daily Workflow](#8-daily-workflow)
9. [Troubleshooting](#9-troubleshooting)

---

## 1. Prerequisites

### Required Software
Install the following before starting:

1. **Python 3.11 or higher**
   ```powershell
   # Check version
   python --version

   # Download from: https://www.python.org/downloads/
   ```

2. **Node.js 18+ and npm**
   ```powershell
   # Check versions
   node --version
   npm --version

   # Download from: https://nodejs.org/
   ```

3. **Git**
   ```powershell
   # Check version
   git --version

   # Download from: https://git-scm.com/
   ```

4. **VS Code**
   - Download from: https://code.visualstudio.com/

---

## 2. VS Code Extensions

### Essential Extensions

Install these extensions from the VS Code marketplace:

#### Python Development
1. **Python** (ms-python.python)
   - IntelliSense, debugging, testing
   - Required for Flask backend

2. **Pylance** (ms-python.vscode-pylance)
   - Fast Python language server
   - Type checking and IntelliSense

3. **Ruff** (charliermarsh.ruff)
   - Python linting and formatting
   - Faster than flake8/black

4. **Python Test Explorer** (littlefoxteam.vscode-python-test-adapter)
   - Visual test runner for pytest

#### Frontend Development
5. **ES7+ React/Redux/React-Native snippets** (dsznajder.es7-react-js-snippets)
   - React component snippets

6. **TypeScript and JavaScript** (Built-in)
   - Already included in VS Code

7. **Tailwind CSS IntelliSense** (bradlc.vscode-tailwindcss)
   - Autocomplete for Tailwind classes

8. **ESLint** (dbaeumer.vscode-eslint)
   - JavaScript/TypeScript linting

#### Git & Collaboration
9. **GitLens** (eamodio.gitlens)
   - Git supercharged
   - Blame annotations, history

10. **Git Graph** (mhutchie.git-graph)
    - Visual git branch history

#### Utilities
11. **Better Comments** (aaron-bond.better-comments)
    - Color-coded comments

12. **Error Lens** (usernamehw.errorlens)
    - Inline error highlighting

13. **Auto Rename Tag** (formulahendry.auto-rename-tag)
    - Rename paired HTML/JSX tags

14. **Path Intellisense** (christian-kohler.path-intellisense)
    - Autocomplete file paths

15. **REST Client** (humao.rest-client)
    - Test API endpoints in VS Code

### Optional Extensions
16. **Thunder Client** (rangav.vscode-thunder-client)
    - Alternative to Postman

17. **Jupyter** (ms-toolsai.jupyter)
    - For data exploration notebooks

---

## 3. Python Backend Setup

### Create Virtual Environment
```powershell
# Navigate to project root
cd ehr-nlp-project

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate

# Upgrade pip
python -m pip install --upgrade pip
```

### Install Python Dependencies
```powershell
# Install all requirements
pip install -r requirements.txt

# Download spaCy medical model (150MB)
python -m spacy download en_core_sci_md

# Verify installation
python -c "import spacy; print(spacy.load('en_core_sci_md'))"
```

### Install VOSK Model (Optional - for voice recognition)
```powershell
# Download from: https://alphacephei.com/vosk/models
# Recommended: vosk-model-small-en-us-0.15.zip (50MB)

# Create models directory
mkdir backend\static\models

# Extract VOSK model to:
# backend\static\models\vosk-model-small-en-us-0.15\
```

### Initialize Database
```powershell
# Navigate to backend
cd backend

# Initialize SQLite database
python -c "from utils.database import get_db; conn = get_db(); conn.executescript(open('database/init_schema.sql').read())"

# Verify database created
ls database\  # Should see clinical_ehr.db
```

### Configure Environment Variables
```powershell
# Copy example environment file
cp .env.example .env

# Edit .env (optional - defaults work fine)
# ENVIRONMENT=development
# API_PORT=8000
# API_HOST=localhost
# SPACY_MODEL=en_core_sci_md
```

### Run Backend Server
```powershell
# From backend directory
cd backend
python app.py

# Server starts at: http://localhost:8000
# Test health endpoint: http://localhost:8000/api/v1/health
```

---

## 4. React Frontend Setup

### Install Node Dependencies
```powershell
# Navigate to project root (if in backend/)
cd ..

# Install root-level dependencies (Commitizen, Husky)
npm install

# Initialize Husky hooks
npx husky init

# Configure Commitizen
npm pkg set config.commitizen.path="./node_modules/cz-conventional-changelog"
```

### Frontend Dependencies (Future)
```powershell
# When frontend is ready for npm setup:
cd frontend
npm install

# Start dev server
npm run dev
```

---

## 5. Git Configuration

### Configure Git Identity
```powershell
# Set your name and email
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Verify configuration
git config --global --list
```

### Connect to GitHub
```powershell
# Add remote repository
git remote add origin https://github.com/ChaminduSR/ehr-nlp-project.git

# Verify remote
git remote -v

# Pull latest changes
git pull origin Dev
```

### Configure Commitizen Hooks
```powershell
# Create prepare-commit-msg hook
New-Item -Path .husky/prepare-commit-msg -Type File -Force

# Add content to .husky/prepare-commit-msg:
# #!/usr/bin/env sh
# . "$(dirname -- "$0")/_/husky.sh"
# exec < /dev/tty && npx cz --hook || true

# Make hook executable
git update-index --add --chmod=+x .husky/prepare-commit-msg
```

---

## 6. Project Structure

```
ehr-nlp-project/
├── .env.example               # Environment template
├── .gitignore                 # Git ignore patterns
├── .husky/                    # Git hooks (Commitizen)
├── .vscode/                   # VS Code settings
│   ├── settings.json          # Editor settings
│   ├── launch.json            # Debug configurations
│   └── extensions.json        # Recommended extensions
├── backend/                   # Flask Python API
│   ├── app.py                # Main application entry
│   ├── config.py             # Environment config
│   ├── routes/               # API blueprints
│   │   ├── __init__.py
│   │   ├── patients.py       # Patient endpoints
│   │   ├── visits.py         # Visit endpoints
│   │   ├── medical_notes.py  # Medical notes + NLP
│   │   ├── joint_assessments.py  # Joint data
│   │   └── voice.py          # VOSK transcription
│   ├── services/             # Business logic
│   │   ├── __init__.py
│   │   └── nlp_engine.py     # spaCy NLP processing
│   ├── utils/                # Utilities
│   │   ├── __init__.py
│   │   └── database.py       # SQLite connection
│   ├── database/             # Database files
│   │   ├── init_schema.sql   # Schema definition
│   │   └── clinical_ehr.db   # SQLite database
│   └── static/               # Static assets
│       └── models/           # VOSK models
├── frontend/                 # React TypeScript app
│   ├── components/
│   │   ├── ehr/             # Custom EHR components
│   │   ├── pages/           # Page components
│   │   └── ui/              # shadcn/ui components
│   ├── styles/              # Tailwind CSS
│   └── README.md            # Frontend docs
├── data/                    # Data files
│   ├── annotations/         # Training annotations
│   ├── models/             # Trained models
│   └── raw_clinical_notes/ # Sample notes
├── docs/                   # Documentation
│   └── master_project_complete_v3-1.md
├── learning/               # Learning scripts
├── scripts/               # Utility scripts
├── tests/                 # Test suites
│   └── backend/
├── package.json           # Node.js dependencies
├── requirements.txt       # Python dependencies
├── ruff.toml             # Ruff configuration
├── README.md             # Project overview
└── VSCODE_SETUP_GUIDE.md # This file
```

---

## 7. Debugging Configuration

### VS Code Settings (.vscode/settings.json)
```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/venv/Scripts/python.exe",
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": ["tests"],
  "python.linting.enabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff",
    "editor.codeActionsOnSave": {
      "source.fixAll": true,
      "source.organizeImports": true
    }
  },
  "[typescript]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  },
  "[typescriptreact]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  },
  "files.exclude": {
    "**/__pycache__": true,
    "**/*.pyc": true,
    "**/node_modules": true
  }
}
```

### Debug Configuration (.vscode/launch.json)
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: Flask Backend",
      "type": "python",
      "request": "launch",
      "module": "flask",
      "env": {
        "FLASK_APP": "backend/app.py",
        "FLASK_ENV": "development"
      },
      "args": ["run", "--no-debugger", "--no-reload"],
      "jinja": true,
      "justMyCode": true,
      "cwd": "${workspaceFolder}"
    },
    {
      "name": "Python: Current File",
      "type": "python",
      "request": "launch",
      "program": "${file}",
      "console": "integratedTerminal",
      "justMyCode": true
    },
    {
      "name": "Python: pytest",
      "type": "python",
      "request": "launch",
      "module": "pytest",
      "args": ["-v", "tests/"],
      "console": "integratedTerminal",
      "justMyCode": false
    }
  ]
}
```

### Extension Recommendations (.vscode/extensions.json)
```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.vscode-pylance",
    "charliermarsh.ruff",
    "dsznajder.es7-react-js-snippets",
    "bradlc.vscode-tailwindcss",
    "dbaeumer.vscode-eslint",
    "eamodio.gitlens",
    "mhutchie.git-graph",
    "aaron-bond.better-comments",
    "usernamehw.errorlens",
    "humao.rest-client"
  ]
}
```

---

## 8. Daily Workflow

### Morning Routine
```powershell
# Pull latest changes
git pull origin Dev

# Check branch
git branch

# Activate virtual environment
.\venv\Scripts\Activate

# Check status
git status
```

### Development Cycle

#### Backend Development
```powershell
# 1. Start backend server
cd backend
python app.py

# 2. Test API endpoints
# Use Thunder Client or REST Client extension
# Or curl: curl http://localhost:8000/api/v1/health

# 3. Run tests
pytest tests/backend/

# 4. Check code quality
ruff check backend/
black backend/ --check
mypy backend/
```

#### Frontend Development
```powershell
# 1. Start frontend dev server (when ready)
cd frontend
npm run dev

# 2. Open browser to http://localhost:3000

# 3. Run tests
npm test

# 4. Lint code
npm run lint
```

### Making Commits
```powershell
# 1. Stage changes
git add .

# 2. Commit (Commitizen opens automatically)
git commit

# 3. Follow Commitizen prompts:
#    - Type: feat, fix, docs, refactor, test, style, chore
#    - Scope: patients, nlp, voice, frontend, backend, etc.
#    - Description: Short summary (50 chars)
#    - Long description: Detailed explanation (optional)
#    - Breaking changes: Yes/No
#    - Issues: Reference issue numbers

# 4. Push to remote
git push origin Dev
```

### Example Commit Flow
```powershell
# Scenario: Adding voice transcription feature

git add backend/routes/voice.py
git commit

# Commitizen prompts:
# ? Select type: feat
# ? Scope: voice
# ? Short description: add VOSK offline transcription endpoint
# ? Long description: Implements POST /api/v1/voice/transcribe endpoint...
# ? Breaking changes: No
# ? Issues: #12

# Result:
# feat(voice): add VOSK offline transcription endpoint
#
# Implements POST /api/v1/voice/transcribe endpoint using VOSK model
# for offline speech-to-text conversion. Supports WAV audio files.
#
# Closes #12

git push origin Dev
```

---

## 9. Troubleshooting

### Python Issues

#### Virtual Environment Not Activating
```powershell
# PowerShell execution policy issue
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then retry
.\venv\Scripts\Activate
```

#### Module Not Found Errors
```powershell
# Ensure virtual environment is active
.\venv\Scripts\Activate

# Reinstall requirements
pip install -r requirements.txt

# Verify Python interpreter in VS Code
# Ctrl+Shift+P → "Python: Select Interpreter" → Choose venv
```

#### spaCy Model Not Found
```powershell
# Download model again
python -m spacy download en_core_sci_md

# Verify installation
python -m spacy info en_core_sci_md
```

### Git Issues

#### Commitizen Not Opening
```powershell
# Verify hook exists
ls .husky/prepare-commit-msg

# Reinstall Husky
npm install
npx husky init

# Manual commit with Commitizen
npx cz commit
```

#### Bypass Commitizen (Emergency)
```powershell
# Only use when necessary
git commit --no-verify -m "your message"
```

### Database Issues

#### Database Locked Error
```powershell
# Close all connections to database
# Restart Flask server
# Delete WAL files if needed
cd backend\database
del *.db-wal
del *.db-shm
```

#### Schema Changes Not Applied
```powershell
# Delete database and reinitialize
cd backend\database
del clinical_ehr.db

# Recreate from schema
cd ..
python -c "from utils.database import get_db; conn = get_db(); conn.executescript(open('database/init_schema.sql').read())"
```

### Port Already in Use
```powershell
# Find process using port 8000
netstat -ano | findstr :8000

# Kill process (replace PID with actual number)
taskkill /PID <PID> /F

# Or change port in .env
# API_PORT=8001
```

### VS Code IntelliSense Not Working

1. **Select Python Interpreter:**
   ```
   Ctrl+Shift+P → "Python: Select Interpreter"
   → Choose: .\venv\Scripts\python.exe
   ```

2. **Reload Window:**
   ```
   Ctrl+Shift+P → "Developer: Reload Window"
   ```

3. **Check Pylance Settings:**
   - Ensure Pylance extension is installed
   - Check `.vscode/settings.json` has correct paths

---

## 10. Testing Guide

### Run Backend Tests
```powershell
# Activate virtual environment
.\venv\Scripts\Activate

# Run all tests
pytest

# Run with coverage
pytest --cov=backend --cov-report=html

# Run specific test file
pytest tests/backend/test_patients.py

# Run specific test
pytest tests/backend/test_patients.py::test_create_patient

# Verbose output
pytest -v -s
```

### Run Frontend Tests (Future)
```powershell
cd frontend
npm test

# Watch mode
npm test -- --watch

# Coverage
npm test -- --coverage
```

---

## 11. Useful VS Code Shortcuts

### Navigation
- `Ctrl+P` - Quick open file
- `Ctrl+Shift+P` - Command palette
- `Ctrl+B` - Toggle sidebar
- `Ctrl+`` - Toggle terminal
- `Ctrl+\` - Split editor

### Editing
- `Alt+Up/Down` - Move line up/down
- `Shift+Alt+Up/Down` - Copy line up/down
- `Ctrl+/` - Toggle comment
- `Ctrl+D` - Select next occurrence
- `Ctrl+Shift+L` - Select all occurrences

### Python Specific
- `F5` - Start debugging
- `F9` - Toggle breakpoint
- `F10` - Step over
- `F11` - Step into
- `Shift+F5` - Stop debugging

### Testing
- `Ctrl+Shift+T` - Run tests (with test explorer)
- Test Explorer sidebar for visual test running

---

## 12. Additional Resources

### Documentation
- [Flask Documentation](https://flask.palletsprojects.com/)
- [spaCy Documentation](https://spacy.io/usage)
- [VOSK Documentation](https://alphacephei.com/vosk/)
- [React Documentation](https://react.dev/)
- [TypeScript Documentation](https://www.typescriptlang.org/)

### Project Docs
- `docs/master_project_complete_v3-1.md` - Complete technical guide
- `frontend/README.md` - Frontend documentation
- `frontend/DESIGN_SPECIFICATIONS.md` - Design system

### Tools
- [Postman Collection](postman_collection.json) - API testing
- [Thunder Client](https://www.thunderclient.com/) - VS Code API client

---

**Last Updated:** November 23, 2025
**Version:** 3.1
**Maintainer:** ChaminduSR

---

## Quick Reference Commands

```powershell
# Activate environment
.\venv\Scripts\Activate

# Run backend
cd backend; python app.py

# Run tests
pytest

# Commit changes
git add .; git commit; git push origin Dev

# Check code quality
ruff check backend/; black backend/ --check

# Update dependencies
pip install -r requirements.txt --upgrade
```
