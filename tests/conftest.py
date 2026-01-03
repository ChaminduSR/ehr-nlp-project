"""
Pytest Configuration and Shared Fixtures for EHR-NLP ML System Tests

This module provides:
- Test database setup (backend/database/test.db)
- Extractor fixtures (Version A, B, C, D)
- Sample clinical notes for testing
- Flask test client
- Custom markers registration

Usage:
    Fixtures are automatically available to all tests.
    Use markers to categorize tests: @pytest.mark.version_b
"""

import os
import sys
import sqlite3
from pathlib import Path
from typing import Generator, Dict, Any

import pytest

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / 'backend'))


# ==============================================================================
# PYTEST CONFIGURATION
# ==============================================================================

def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line("markers", "unit: Fast unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "slow: Slow tests requiring ML models")
    config.addinivalue_line("markers", "version_a: Version A (Regex) tests")
    config.addinivalue_line("markers", "version_b: Version B (GatorTron) tests")
    config.addinivalue_line("markers", "version_c: Version C (Two-Tier) tests")
    config.addinivalue_line("markers", "version_d: Version D (Ensemble) tests")
    config.addinivalue_line("markers", "api: API route tests")
    config.addinivalue_line("markers", "database: Database tests")


# ==============================================================================
# DATABASE FIXTURES
# ==============================================================================

TEST_DB_PATH = PROJECT_ROOT / 'backend' / 'database' / 'test.db'


@pytest.fixture(scope="session")
def test_database() -> Generator[Path, None, None]:
    """
    Session-scoped fixture: Create test database once for all tests.

    Creates backend/database/test.db with full schema.
    Database persists for inspection after tests.
    """
    # Ensure directory exists
    TEST_DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Read schema from init_schema.sql
    schema_path = PROJECT_ROOT / 'backend' / 'database' / 'init_schema.sql'

    # Create fresh database
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()

    conn = sqlite3.connect(str(TEST_DB_PATH))

    if schema_path.exists():
        with open(schema_path, 'r') as f:
            conn.executescript(f.read())
    else:
        # Minimal schema if init_schema.sql not found
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS patients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                date_of_birth TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS visits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER NOT NULL,
                visit_date TEXT NOT NULL,
                chief_complaint TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (patient_id) REFERENCES patients(id)
            );

            CREATE TABLE IF NOT EXISTS medical_notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                visit_id INTEGER NOT NULL,
                text TEXT,
                status TEXT DEFAULT 'draft',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (visit_id) REFERENCES visits(id)
            );

            CREATE TABLE IF NOT EXISTS extracted_entities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                medical_note_id INTEGER NOT NULL,
                text TEXT NOT NULL,
                entity_type TEXT NOT NULL,
                start_pos INTEGER,
                end_pos INTEGER,
                confidence REAL,
                is_negated BOOLEAN DEFAULT 0,
                umls_cui TEXT,
                umls_name TEXT,
                agreement INTEGER,
                versions_found TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (medical_note_id) REFERENCES medical_notes(id)
            );

            CREATE TABLE IF NOT EXISTS inferred_diagnoses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                medical_note_id INTEGER NOT NULL,
                diagnosis_text TEXT NOT NULL,
                confidence REAL,
                matched_rule TEXT,
                rule_match_count INTEGER,
                rule_min_required INTEGER,
                linked_from TEXT,
                suggested_actions TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (medical_note_id) REFERENCES medical_notes(id)
            );

            CREATE TABLE IF NOT EXISTS entity_links (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                medical_note_id INTEGER NOT NULL,
                source_entity TEXT NOT NULL,
                target_entity TEXT NOT NULL,
                relationship TEXT,
                confidence REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (medical_note_id) REFERENCES medical_notes(id)
            );
        """)

    conn.commit()
    conn.close()

    yield TEST_DB_PATH

    # Optional: cleanup after all tests (commented out for inspection)
    # TEST_DB_PATH.unlink()


@pytest.fixture(scope="function")
def db_connection(test_database) -> Generator[sqlite3.Connection, None, None]:
    """
    Function-scoped fixture: Fresh database connection per test.

    Provides a connection with Row factory.
    Rolls back changes after each test for isolation.
    """
    conn = sqlite3.connect(str(test_database))
    conn.row_factory = sqlite3.Row

    yield conn

    conn.rollback()
    conn.close()


# ==============================================================================
# EXTRACTOR FIXTURES
# ==============================================================================

@pytest.fixture(scope="module")
def extractor_a():
    """
    Module-scoped fixture: Version A (Regex) extractor.

    Loaded once per test module for performance.
    No ML models required.
    """
    from services.regex_entity_extractor import RegexEntityExtractor
    return RegexEntityExtractor()


@pytest.fixture(scope="module")
def extractor_b():
    """
    Module-scoped fixture: Version B (GatorTron-Rheum) extractor.

    Requires model at data/models/gatortron-rheum/
    Will fail if model not available.
    """
    from services.mtl_entity_extractor import MTLEntityExtractor
    return MTLEntityExtractor()


@pytest.fixture(scope="module")
def extractor_c():
    """
    Module-scoped fixture: Version C (Two-Tier) extractor.

    Requires GatorTron + SapBERT models.
    Will fail if models not available.
    """
    from services.two_tier_extractor import TwoTierExtractor
    return TwoTierExtractor()


@pytest.fixture(scope="module")
def extractor_d():
    """
    Module-scoped fixture: Version D (Ensemble) extractor.

    Requires all models (GatorTron, SapBERT, BioLinkBERT).
    Will fail if models not available.
    """
    from services.ensemble_extractor import EnsembleExtractor
    return EnsembleExtractor()


@pytest.fixture(scope="module")
def biolinkbert_extractor():
    """
    Module-scoped fixture: BioLinkBERT extractor.

    Requires model at data/models/biolinkbert/
    """
    from services.biolinkbert_extractor import BioLinkBERTExtractor
    return BioLinkBERTExtractor()


@pytest.fixture(scope="module")
def sapbert_normalizer():
    """
    Module-scoped fixture: SapBERT normalizer.

    Requires model at data/models/sapbert/
    """
    from services.sapbert_normalizer import SapBERTNormalizer
    return SapBERTNormalizer()


# ==============================================================================
# FLASK TEST CLIENT
# ==============================================================================

@pytest.fixture(scope="module")
def app():
    """
    Module-scoped fixture: Flask application.

    Configured for testing with test database.
    """
    from app import app as flask_app

    flask_app.config.update({
        'TESTING': True,
        'DATABASE_PATH': str(TEST_DB_PATH),
    })

    return flask_app


@pytest.fixture(scope="function")
def client(app):
    """
    Function-scoped fixture: Flask test client.

    Fresh client per test for isolation.
    """
    return app.test_client()


# ==============================================================================
# SAMPLE CLINICAL NOTES
# ==============================================================================

@pytest.fixture
def sample_note_simple() -> str:
    """Simple clinical note with basic entities."""
    return "Patient takes methotrexate 15mg weekly for rheumatoid arthritis."


@pytest.fixture
def sample_note_negation() -> str:
    """Clinical note with negated symptoms."""
    return (
        "Patient with RA on methotrexate 15mg weekly. "
        "Denies fever, chills, or night sweats. "
        "No joint swelling observed today."
    )


@pytest.fixture
def sample_note_complex() -> str:
    """Complex clinical note with multiple entity types."""
    return """
    Chief Complaint: Joint pain and morning stiffness

    HPI: 58-year-old female with known rheumatoid arthritis presents with
    increased joint pain in bilateral hands and wrists over the past 2 weeks.
    Morning stiffness lasting approximately 2 hours. Currently on methotrexate
    15mg weekly and hydroxychloroquine 200mg twice daily.

    Labs: ESR 45 mm/hr (elevated), CRP 2.8 mg/dL, RF positive, anti-CCP positive.

    Physical Exam: Tender and swollen MCP joints bilaterally. No warmth or
    erythema. DIP joints without tenderness.

    Assessment: Rheumatoid arthritis flare
    Plan:
    - Increase methotrexate to 20mg weekly
    - Add prednisone taper: 20mg x 5 days, then 10mg x 5 days
    - Recheck labs in 4 weeks
    - Consider adding biologic if no improvement
    """


@pytest.fixture
def sample_note_labs() -> str:
    """Clinical note focused on lab results."""
    return (
        "Labs reviewed: ESR 45 mm/hr, CRP 12 mg/dL elevated, "
        "ANA positive 1:320 speckled pattern, anti-dsDNA negative, "
        "C3 and C4 within normal limits, RF 85 IU/mL positive, "
        "anti-CCP 250 units positive."
    )


@pytest.fixture
def sample_note_medications() -> str:
    """Clinical note with multiple medications."""
    return (
        "Current medications: "
        "methotrexate 15mg weekly, "
        "folic acid 1mg daily, "
        "hydroxychloroquine 200mg twice daily, "
        "prednisone 5mg daily, "
        "adalimumab 40mg subcutaneous every 2 weeks, "
        "calcium 600mg with vitamin D daily, "
        "omeprazole 20mg daily for GI protection."
    )


@pytest.fixture
def sample_note_symptoms() -> str:
    """Clinical note with various symptoms."""
    return (
        "Patient reports morning stiffness lasting 2 hours, "
        "bilateral hand pain worse in the morning, "
        "fatigue and malaise, "
        "joint swelling in MCPs and PIPs, "
        "no fever or weight loss."
    )


@pytest.fixture
def sample_note_empty() -> str:
    """Empty note for edge case testing."""
    return ""


@pytest.fixture
def sample_note_no_entities() -> str:
    """Note with no medical entities."""
    return "The weather today is nice. Patient arrived on time for appointment."


@pytest.fixture
def sample_rheumatology_full() -> str:
    """Full rheumatology consultation note."""
    return """
    RHEUMATOLOGY CONSULTATION

    Patient: Jane Doe
    DOB: 01/15/1965
    Date: 01/03/2026

    CHIEF COMPLAINT:
    Joint pain and swelling for 3 months

    HISTORY OF PRESENT ILLNESS:
    58-year-old female presents with progressive polyarticular joint pain
    affecting small joints of hands, wrists, and feet bilaterally. Symptoms
    started insidiously 3 months ago. Morning stiffness lasts 2-3 hours daily.
    Pain is worse in the morning and improves with activity. She reports
    fatigue and 5-pound unintentional weight loss.

    PAST MEDICAL HISTORY:
    - Hypertension
    - Type 2 diabetes mellitus
    - Hypothyroidism

    CURRENT MEDICATIONS:
    1. Metoprolol 50mg daily
    2. Metformin 1000mg twice daily
    3. Levothyroxine 75mcg daily
    4. Ibuprofen 400mg as needed (taking daily for past month)

    ALLERGIES: Sulfa (rash)

    FAMILY HISTORY:
    Mother with rheumatoid arthritis
    Sister with lupus

    SOCIAL HISTORY:
    Non-smoker, occasional alcohol, works as teacher

    REVIEW OF SYSTEMS:
    - Constitutional: Fatigue, weight loss, no fever
    - Musculoskeletal: Joint pain, stiffness, swelling as above
    - Skin: No rashes, no nodules
    - Eyes: No dryness, no redness
    - Neurological: No numbness or tingling
    - Denies oral ulcers, hair loss, photosensitivity

    PHYSICAL EXAMINATION:
    Vitals: BP 132/78, HR 72, Temp 98.4F, Weight 145 lbs

    General: Well-appearing female in no acute distress
    HEENT: No oral ulcers, no alopecia
    Cardiovascular: Regular rhythm, no murmurs
    Pulmonary: Clear to auscultation bilaterally
    Abdomen: Soft, non-tender
    Skin: No rashes, no subcutaneous nodules

    Musculoskeletal:
    - Hands: Tender and swollen MCPs 2-5 bilaterally, PIPs 2-4 bilaterally
    - Wrists: Bilateral tenderness and mild swelling
    - Feet: Tender MTPs 2-5 bilaterally
    - Knees: No effusion, full ROM
    - No warmth or erythema noted

    LABORATORY DATA:
    - ESR: 52 mm/hr (elevated)
    - CRP: 3.2 mg/dL (elevated)
    - RF: 156 IU/mL (positive)
    - Anti-CCP: 340 units (strongly positive)
    - ANA: Negative
    - CBC: WBC 8.2, Hgb 12.1, Plt 298
    - CMP: Creatinine 0.9, normal LFTs
    - HbA1c: 7.2%

    IMAGING:
    X-rays hands: Periarticular osteopenia, early erosions at MCP 2-3 bilaterally

    ASSESSMENT:
    1. Seropositive rheumatoid arthritis - new diagnosis
       - ACR/EULAR criteria met (>6 points)
       - Poor prognostic factors: high RF/anti-CCP, early erosions
    2. NSAID gastropathy risk - on daily ibuprofen

    PLAN:
    1. Start methotrexate 15mg weekly with folic acid 1mg daily
    2. Prednisone bridge: 15mg daily x 2 weeks, then taper
    3. Stop ibuprofen, start omeprazole 20mg daily
    4. Labs in 4 weeks: CBC, CMP, LFTs
    5. Hepatitis B and C screening before biologics
    6. Consider adding biologic (adalimumab or etanercept) if inadequate response
    7. Physical therapy referral
    8. Return in 6 weeks

    DAS28-ESR: 5.8 (High disease activity)
    """


# ==============================================================================
# PARAMETRIZE DATA
# ==============================================================================

# Common medications for parametrized tests
MEDICATION_TEST_CASES = [
    ("methotrexate 15mg weekly", "MEDICATION", "methotrexate"),
    ("hydroxychloroquine 200mg", "MEDICATION", "hydroxychloroquine"),
    ("prednisone 10mg daily", "MEDICATION", "prednisone"),
    ("adalimumab 40mg injection", "MEDICATION", "adalimumab"),
    ("etanercept 50mg weekly", "MEDICATION", "etanercept"),
    ("sulfasalazine 500mg", "MEDICATION", "sulfasalazine"),
    ("leflunomide 20mg", "MEDICATION", "leflunomide"),
    ("rituximab infusion", "MEDICATION", "rituximab"),
    ("tofacitinib 5mg", "MEDICATION", "tofacitinib"),
    ("abatacept injection", "MEDICATION", "abatacept"),
]

# Common negation patterns
NEGATION_TEST_CASES = [
    ("Patient denies fever", "fever"),
    ("No joint swelling", "swelling"),
    ("Negative for ANA", "ANA"),
    ("Rules out lupus", "lupus"),
    ("Without morning stiffness", "stiffness"),
    ("Denies chest pain", "pain"),
    ("No evidence of erosions", "erosions"),
    ("Absence of rash", "rash"),
]

# Lab tests for parametrized tests
LAB_TEST_CASES = [
    ("ESR 45 mm/hr", "LAB_TEST", "ESR"),
    ("CRP 12 mg/dL", "LAB_TEST", "CRP"),
    ("RF positive", "LAB_TEST", "RF"),
    ("anti-CCP 250 units", "LAB_TEST", "anti-CCP"),
    ("ANA 1:320", "LAB_TEST", "ANA"),
    ("anti-dsDNA negative", "LAB_TEST", "anti-dsDNA"),
    ("C3 normal", "LAB_TEST", "C3"),
    ("hemoglobin 12.5", "LAB_TEST", "hemoglobin"),
]

# Symptoms for parametrized tests
SYMPTOM_TEST_CASES = [
    ("morning stiffness lasting 2 hours", "SYMPTOM", "stiffness"),
    ("joint pain in hands", "SYMPTOM", "pain"),
    ("fatigue and malaise", "SYMPTOM", "fatigue"),
    ("joint swelling", "SYMPTOM", "swelling"),
    ("fever and chills", "SYMPTOM", "fever"),
]


@pytest.fixture
def medication_test_data():
    """Fixture providing medication test cases for parametrized tests."""
    return MEDICATION_TEST_CASES


@pytest.fixture
def negation_test_data():
    """Fixture providing negation test cases."""
    return NEGATION_TEST_CASES


@pytest.fixture
def lab_test_data():
    """Fixture providing lab test cases."""
    return LAB_TEST_CASES


# ==============================================================================
# UTILITY FIXTURES
# ==============================================================================

@pytest.fixture
def project_root() -> Path:
    """Return project root path."""
    return PROJECT_ROOT


@pytest.fixture
def models_path() -> Path:
    """Return path to models directory."""
    return PROJECT_ROOT / 'data' / 'models'


@pytest.fixture
def assert_model_exists(models_path):
    """
    Factory fixture to assert a model exists.

    Usage:
        def test_something(assert_model_exists):
            assert_model_exists('gatortron-rheum')
    """
    def _assert_model_exists(model_name: str):
        model_path = models_path / model_name
        assert model_path.exists(), f"Model not found: {model_path}"
        assert (model_path / 'config.json').exists(), f"config.json not found in {model_path}"
    return _assert_model_exists
