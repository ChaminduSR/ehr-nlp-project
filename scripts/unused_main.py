"""
Main entry point for EHR-NLP backend application.

This module initializes and runs the backend server.
"""

import sys
from pathlib import Path
import spacy
from backend.config import get_config

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

def load_nlp_model():
    """
    Load spaCy NLP model.

    Returns:
        nlp: Loaded spaCy model
    """
    config = get_config()
    try:
        nlp = spacy.load(config.SPACY_MODEL)
        return nlp
    except OSError:
        print(f"Model {config.SPACY_MODEL} not found")
        print("Run: python -m spacy download en_core_sci_md")
        return None


def main():
    """Main application entry point."""
    config = get_config()

    print("EHR-NLP Backend Starting...")
    print(f"Environment: {config.ENVIRONMENT}")
    print(f"Debug mode: {config.DEBUG}")

    # Load NLP model
    nlp = load_nlp_model()
    if not nlp:
        print("Failed to start - NLP model not available")
        return

    print("Application initialized successfully!")
    print("Ready to process clinical text...")


if __name__ == "__main__":
    main()
