# VS Code Setup Guide for EHR-NLP Project

This guide documents the complete setup process for the EHR-NLP project development environment.

## 1. Initial Setup

### Environment Setup
1. Install VS Code
2. Install Git
3. Install Node.js and npm
4. Set up Python virtual environment:
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate
   ```

### VS Code Extensions
Install the following extensions:
1. GitLens — Git supercharged
2. Better Comments
3. Python extension
4. Jupyter Notebooks
5. Ruff (charliermarsh.ruff) - For Python linting and formatting

## 2. Project Configuration

### Initialize Project
```powershell
# Create project directory and initialize git
mkdir ehr-nlp-project
cd ehr-nlp-project
git init

# Initialize npm project
npm init -y
```

### Configure Git and GitHub
1. Set up Git configuration:
   ```powershell
   git config --global user.name "Your Name"
   git config --global user.email "your.email@example.com"
   ```
2. Connect to GitHub repository
   ```powershell
   git remote add origin https://github.com/ChaminduSR/ehr-nlp-project.git
   ```

## 3. Commit Convention Setup

### Install and Configure Commitizen
```powershell
# Install Commitizen and conventional changelog adapter
npm install --save-dev commitizen cz-conventional-changelog

# Initialize Commitizen configuration
npx commitizen init cz-conventional-changelog --save-dev --save-exact
```

### Install and Configure Husky
```powershell
# Install Husky
npm install --save-dev husky

# Initialize Husky
npx husky init

# Add prepare script to package.json
npm pkg set scripts.prepare="husky install"
```

### Configure Git Hooks
1. Create prepare-commit-msg hook:
   ```powershell
   # Create the hook file
   New-Item -Path .husky/prepare-commit-msg -Type File -Force
   ```

2. Add the following content to `.husky/prepare-commit-msg`:
   ```bash
   #!/usr/bin/env sh
   . "$(dirname -- "$0")/_/husky.sh"

   # Run Commitizen instead of the regular commit message editor
   exec < /dev/tty && npx cz --hook || true
   ```

3. Make the hook executable:
   ```powershell
   # In PowerShell
   git update-index --add --chmod=+x .husky/prepare-commit-msg
   ```

## 4. Project Structure Setup

Create the following directory structure:
```
ehr-nlp-project/
├── .env.example
├── .git/
├── .gitignore
├── .husky/
├── .vscode/
├── backend/
│   ├── app/
│   ├── config.py
│   ├── main.py
│   ├── models/
│   ├── routes/
│   ├── services/
│   ├── utils/
│   └── __init__.py
├── data/
│   ├── annotations/
│   ├── models/
│   └── raw_clinical_notes/
├── docs/
├── frontend/
├── scripts/
├── tests/
│   ├── backend/
│   └── integration/
├── CONTRIBUTING.md
├── LICENSE
├── node_modules/
├── package-lock.json
├── package.json
├── README.md
├── requirements.txt
├── VSCODE_SETUP_GUIDE.md
└── venv/
```

## 5. Verification Steps

### Test Commitizen Integration
1. Make a test change:
   ```powershell
   echo "# Test file" > test-file.md
   git add test-file.md
   git commit
   ```
2. Verify that Commitizen prompt appears with:
   - Type of change
   - Scope of change
   - Description
   - Breaking changes
   - Affected issues

### Verify Dependencies
```powershell
# Verify installed packages
npm list commitizen
npm list cz-conventional-changelog
npm list husky

# Check Python environment
python --version
pip list

# Verify Ruff installation and configuration
ruff --version
cat ruff.toml  # Verify Ruff configuration
```

## 6. Daily Development Workflow

1. Start of day:
   ```powershell
   git pull
   git status
   .\venv\Scripts\Activate
   ```

2. Making commits:
   ```powershell
   git add .
   git commit  # This will automatically trigger Commitizen
   ```

3. Push changes:
   ```powershell
   git push origin main
   ```

## Troubleshooting

### If Commitizen Doesn't Open
1. Verify hook permissions:
   ```powershell
   git ls-files --stage .husky/prepare-commit-msg
   ```
2. Reinstall dependencies:
   ```powershell
   npm install
   ```
3. Manual Commitizen:
   ```powershell
   npx cz commit
   ```

### Bypass Husky (Emergency Only)
```powershell
git commit --no-verify -m "your message"
```

Last Updated: November 1, 2025
