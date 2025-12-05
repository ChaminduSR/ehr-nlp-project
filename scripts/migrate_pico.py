import os
import re

# Configuration
TEMPLATE_DIR = "backend/templates"
BACKUP_DIR = "backend/templates_backup"

# Replacement Rules (Regex Pattern -> Replacement)
MIGRATION_MAP = {
    # Containers
    r'class="container-fluid"': 'class="container-fluid"', # Keep same
    r'class="container"': 'class="container"',           # Keep same

    # Grid System (Bootstrap col-md-6 -> Pico grid is native)
    r'class="row"': 'class="grid"',
    r'class="col-md-\d+"': '', # Remove specific cols (let CSS Grid handle auto)

    # Buttons
    r'class="btn btn-primary"': 'role="button"',
    r'class="btn btn-secondary"': 'role="button" class="secondary"',
    r'class="btn btn-danger"': 'role="button" class="contrast"',
    r'class="btn btn-success"': 'role="button" class="outline"',
    r'class="btn-sm"': 'style="padding: 0.25rem 0.5rem; font-size: 0.875rem;"',

    # Forms
    r'class="form-control"': '', # Pico styles inputs automatically
    r'class="form-group"': 'class="mb-3"',
    r'class="form-label"': '',   # Pico styles labels automatically

    # Cards
    r'class="card"': 'class="article"', # Pico uses <article> for cards
    r'class="card-body"': '',          # Not needed in Pico
    r'class="card-header"': 'class="header"',
    r'class="card-footer"': 'class="footer"',

    # Typography
    r'class="text-center"': 'style="text-align: center;"',
    r'class="text-muted"': 'class="secondary"',
    r'class="display-4"': 'style="font-size: 2.5rem;"',

    # Tables
    r'class="table table-striped"': 'role="grid"',
    r'class="table-responsive"': 'style="overflow-x: auto;"',

    # Utilities
    r'class="d-flex"': 'style="display: flex;"',
    r'class="justify-content-between"': 'style="justify-content: space-between;"',
    r'class="align-items-center"': 'style="align-items: center;"',
    r'class="mt-3"': 'style="margin-top: 1rem;"',
    r'class="mb-3"': 'style="margin-bottom: 1rem;"',
}

def migrate_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Apply replacements
    for pattern, replacement in MIGRATION_MAP.items():
        content = re.sub(pattern, replacement, content)

    # Semantic HTML Upgrades
    content = content.replace('<div class="card">', '<article>')
    content = content.replace('</div><!-- card end -->', '</article>')

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Migrated: {filepath}")

def main():
    # Backup first
    if not os.path.exists(BACKUP_DIR):
        # Use shutil for recursive copy
        import shutil
        shutil.copytree(TEMPLATE_DIR, BACKUP_DIR)
        print(f"📦 Backup created at {BACKUP_DIR}")
    else:
        print(f"📦 Backup already exists at {BACKUP_DIR}")

    # Process all HTML files
    for root, dirs, files in os.walk(TEMPLATE_DIR):
        for file in files:
            if file.endswith(".html"):
                migrate_file(os.path.join(root, file))

if __name__ == "__main__":
    main()
