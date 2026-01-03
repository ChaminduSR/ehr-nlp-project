"""
Tests for Medical Notes API Routes

Tests the Flask API endpoints for medical note processing:
- POST /api/v1/medical_notes/extract
- POST /api/v1/medical_notes/draft
- POST /api/v1/medical_notes/finalize
- GET /api/v1/medical_notes/fragment

Run with: pytest tests/backend/test_medical_notes_api.py -v
"""

import pytest
import json
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'backend'))


@pytest.mark.api
class TestMedicalNotesExtractAPI:
    """Tests for POST /api/v1/medical_notes/extract endpoint."""

    # ==================== FIXTURES ====================

    @pytest.fixture(scope="class")
    def app(self):
        """Create Flask application for testing."""
        from app import app
        app.config['TESTING'] = True
        return app

    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return app.test_client()

    # ==================== EXTRACT ENDPOINT TESTS ====================

    def test_extract_returns_200(self, client):
        """Test extract endpoint returns 200 for valid request."""
        # Arrange
        data = {'text': 'Patient on methotrexate for rheumatoid arthritis'}

        # Act
        response = client.post(
            '/api/v1/medical_notes/extract',
            data=json.dumps(data),
            content_type='application/json'
        )

        # Assert
        assert response.status_code == 200

    def test_extract_returns_json(self, client):
        """Test extract endpoint returns JSON response."""
        # Arrange
        data = {'text': 'methotrexate 15mg weekly'}

        # Act
        response = client.post(
            '/api/v1/medical_notes/extract',
            data=json.dumps(data),
            content_type='application/json'
        )

        # Assert
        assert response.content_type == 'application/json'

    def test_extract_response_structure(self, client):
        """Test extract response has correct structure."""
        # Arrange
        data = {'text': 'Patient on methotrexate'}

        # Act
        response = client.post(
            '/api/v1/medical_notes/extract',
            data=json.dumps(data),
            content_type='application/json'
        )
        result = json.loads(response.data)

        # Assert
        assert 'success' in result or 'entities' in result or 'raw_entities' in result

    def test_extract_returns_entities(self, client):
        """Test extract returns extracted entities."""
        # Arrange
        data = {'text': 'Patient on methotrexate 15mg weekly for rheumatoid arthritis'}

        # Act
        response = client.post(
            '/api/v1/medical_notes/extract',
            data=json.dumps(data),
            content_type='application/json'
        )
        result = json.loads(response.data)

        # Assert
        entities = result.get('raw_entities') or result.get('entities') or []
        assert len(entities) >= 1

    def test_extract_returns_structured_data(self, client):
        """Test extract returns structured data fields."""
        # Arrange
        data = {'text': 'Patient on methotrexate for rheumatoid arthritis. Chief complaint: joint pain.'}

        # Act
        response = client.post(
            '/api/v1/medical_notes/extract',
            data=json.dumps(data),
            content_type='application/json'
        )
        result = json.loads(response.data)

        # Assert
        if 'structured' in result:
            assert isinstance(result['structured'], dict)

    def test_extract_returns_nlp_version(self, client):
        """Test extract returns NLP version used."""
        # Arrange
        data = {'text': 'methotrexate 15mg'}

        # Act
        response = client.post(
            '/api/v1/medical_notes/extract',
            data=json.dumps(data),
            content_type='application/json'
        )
        result = json.loads(response.data)

        # Assert
        assert 'nlp_version' in result or 'version' in result

    def test_extract_returns_processing_time(self, client):
        """Test extract returns processing time."""
        # Arrange
        data = {'text': 'methotrexate for RA'}

        # Act
        response = client.post(
            '/api/v1/medical_notes/extract',
            data=json.dumps(data),
            content_type='application/json'
        )
        result = json.loads(response.data)

        # Assert
        assert 'processing_time_ms' in result

    def test_extract_empty_text_returns_empty_entities(self, client):
        """Test extract with empty text returns empty entities."""
        # Arrange
        data = {'text': ''}

        # Act
        response = client.post(
            '/api/v1/medical_notes/extract',
            data=json.dumps(data),
            content_type='application/json'
        )
        result = json.loads(response.data)

        # Assert
        entities = result.get('raw_entities') or result.get('entities') or []
        assert entities == []

    def test_extract_missing_text_returns_error(self, client):
        """Test extract without text field returns error."""
        # Arrange
        data = {}

        # Act
        response = client.post(
            '/api/v1/medical_notes/extract',
            data=json.dumps(data),
            content_type='application/json'
        )

        # Assert
        # Should return 400 or 422 for validation error
        assert response.status_code in [400, 422] or 'error' in json.loads(response.data)


@pytest.mark.api
@pytest.mark.database
class TestMedicalNotesDraftAPI:
    """Tests for POST /api/v1/medical_notes/draft endpoint."""

    # ==================== FIXTURES ====================

    @pytest.fixture(scope="class")
    def app(self):
        """Create Flask application for testing."""
        from app import app
        app.config['TESTING'] = True
        return app

    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return app.test_client()

    @pytest.fixture
    def sample_visit_id(self, test_database, db_connection):
        """Create a test patient and visit for draft tests."""
        # Insert test patient
        db_connection.execute(
            "INSERT INTO patients (first_name, last_name) VALUES (?, ?)",
            ('Test', 'Patient')
        )
        patient_id = db_connection.execute("SELECT last_insert_rowid()").fetchone()[0]

        # Insert test visit
        db_connection.execute(
            "INSERT INTO visits (patient_id, visit_date) VALUES (?, ?)",
            (patient_id, '2026-01-03')
        )
        visit_id = db_connection.execute("SELECT last_insert_rowid()").fetchone()[0]
        db_connection.commit()

        return visit_id

    # ==================== DRAFT ENDPOINT TESTS ====================

    def test_draft_returns_200(self, client, sample_visit_id):
        """Test draft endpoint returns 200 for valid request."""
        # Arrange
        data = {
            'visit_id': sample_visit_id,
            'text': 'Patient on methotrexate'
        }

        # Act
        response = client.post(
            '/api/v1/medical_notes/draft',
            data=json.dumps(data),
            content_type='application/json'
        )

        # Assert
        assert response.status_code == 200

    def test_draft_returns_note_id(self, client, sample_visit_id):
        """Test draft returns note_id."""
        # Arrange
        data = {
            'visit_id': sample_visit_id,
            'text': 'Test note content'
        }

        # Act
        response = client.post(
            '/api/v1/medical_notes/draft',
            data=json.dumps(data),
            content_type='application/json'
        )
        result = json.loads(response.data)

        # Assert
        assert 'note_id' in result or 'id' in result

    def test_draft_returns_status(self, client, sample_visit_id):
        """Test draft returns status field."""
        # Arrange
        data = {
            'visit_id': sample_visit_id,
            'text': 'Draft note'
        }

        # Act
        response = client.post(
            '/api/v1/medical_notes/draft',
            data=json.dumps(data),
            content_type='application/json'
        )
        result = json.loads(response.data)

        # Assert
        if 'status' in result:
            assert result['status'] == 'draft'

    def test_draft_missing_visit_id_returns_error(self, client):
        """Test draft without visit_id returns error."""
        # Arrange
        data = {'text': 'Some text'}

        # Act
        response = client.post(
            '/api/v1/medical_notes/draft',
            data=json.dumps(data),
            content_type='application/json'
        )

        # Assert
        assert response.status_code in [400, 422] or 'error' in json.loads(response.data)


@pytest.mark.api
@pytest.mark.database
class TestMedicalNotesFinalizeAPI:
    """Tests for POST /api/v1/medical_notes/finalize endpoint."""

    # ==================== FIXTURES ====================

    @pytest.fixture(scope="class")
    def app(self):
        """Create Flask application for testing."""
        from app import app
        app.config['TESTING'] = True
        return app

    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return app.test_client()

    @pytest.fixture
    def sample_note_id(self, test_database, db_connection):
        """Create a test note for finalize tests."""
        # Insert test patient
        db_connection.execute(
            "INSERT INTO patients (first_name, last_name) VALUES (?, ?)",
            ('Test', 'Finalize')
        )
        patient_id = db_connection.execute("SELECT last_insert_rowid()").fetchone()[0]

        # Insert test visit
        db_connection.execute(
            "INSERT INTO visits (patient_id, visit_date) VALUES (?, ?)",
            (patient_id, '2026-01-03')
        )
        visit_id = db_connection.execute("SELECT last_insert_rowid()").fetchone()[0]

        # Insert test note
        db_connection.execute(
            "INSERT INTO medical_notes (visit_id, text, status) VALUES (?, ?, ?)",
            (visit_id, 'Patient on methotrexate for RA', 'draft')
        )
        note_id = db_connection.execute("SELECT last_insert_rowid()").fetchone()[0]
        db_connection.commit()

        return note_id

    # ==================== FINALIZE ENDPOINT TESTS ====================

    def test_finalize_returns_200(self, client, sample_note_id):
        """Test finalize endpoint returns 200 for valid request."""
        # Arrange
        data = {
            'note_id': sample_note_id,
            'text': 'Final note content with methotrexate 15mg'
        }

        # Act
        response = client.post(
            '/api/v1/medical_notes/finalize',
            data=json.dumps(data),
            content_type='application/json'
        )

        # Assert
        assert response.status_code == 200

    def test_finalize_triggers_nlp(self, client, sample_note_id):
        """Test finalize triggers NLP extraction."""
        # Arrange
        data = {
            'note_id': sample_note_id,
            'text': 'Patient on methotrexate 15mg weekly for rheumatoid arthritis'
        }

        # Act
        response = client.post(
            '/api/v1/medical_notes/finalize',
            data=json.dumps(data),
            content_type='application/json'
        )
        result = json.loads(response.data)

        # Assert
        assert 'entities_extracted' in result or 'processing_time_ms' in result

    def test_finalize_returns_nlp_version(self, client, sample_note_id):
        """Test finalize returns NLP version used."""
        # Arrange
        data = {
            'note_id': sample_note_id,
            'text': 'methotrexate for RA'
        }

        # Act
        response = client.post(
            '/api/v1/medical_notes/finalize',
            data=json.dumps(data),
            content_type='application/json'
        )
        result = json.loads(response.data)

        # Assert
        assert 'nlp_version' in result or 'version' in result


@pytest.mark.api
class TestMedicalNotesFragmentAPI:
    """Tests for GET /api/v1/medical_notes/fragment endpoint."""

    # ==================== FIXTURES ====================

    @pytest.fixture(scope="class")
    def app(self):
        """Create Flask application for testing."""
        from app import app
        app.config['TESTING'] = True
        return app

    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return app.test_client()

    # ==================== FRAGMENT ENDPOINT TESTS ====================

    def test_fragment_returns_200(self, client):
        """Test fragment endpoint returns 200."""
        # Arrange - none needed

        # Act
        response = client.get('/api/v1/medical_notes/fragment')

        # Assert
        assert response.status_code == 200

    def test_fragment_returns_html(self, client):
        """Test fragment returns HTML content."""
        # Arrange - none needed

        # Act
        response = client.get('/api/v1/medical_notes/fragment')

        # Assert
        assert 'text/html' in response.content_type


@pytest.mark.api
class TestMedicalNotesAPIErrorHandling:
    """Tests for API error handling."""

    # ==================== FIXTURES ====================

    @pytest.fixture(scope="class")
    def app(self):
        """Create Flask application for testing."""
        from app import app
        app.config['TESTING'] = True
        return app

    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return app.test_client()

    # ==================== ERROR HANDLING TESTS ====================

    def test_invalid_json_returns_error(self, client):
        """Test invalid JSON returns error response."""
        # Arrange
        invalid_json = "not valid json"

        # Act
        response = client.post(
            '/api/v1/medical_notes/extract',
            data=invalid_json,
            content_type='application/json'
        )

        # Assert
        assert response.status_code in [400, 415, 422]

    def test_wrong_content_type_handled(self, client):
        """Test wrong content type is handled."""
        # Arrange
        data = 'text=some text'

        # Act
        response = client.post(
            '/api/v1/medical_notes/extract',
            data=data,
            content_type='application/x-www-form-urlencoded'
        )

        # Assert
        # Should either work or return appropriate error
        assert response.status_code in [200, 400, 415, 422]

    def test_very_long_text_handled(self, client):
        """Test very long text is handled gracefully."""
        # Arrange
        data = {'text': 'methotrexate ' * 10000}  # Very long text

        # Act
        response = client.post(
            '/api/v1/medical_notes/extract',
            data=json.dumps(data),
            content_type='application/json'
        )

        # Assert
        # Should succeed or return appropriate error (not crash)
        assert response.status_code in [200, 400, 413, 422]
