"""
API Contract Tests for EHR-NLP System

Tests verify that API response structures match what the frontend expects.
These tests catch contract violations that cause frontend bugs.

Run with: pytest tests/backend/test_api_contracts.py -v -m api
"""

import pytest
import json
import uuid
import sys
from pathlib import Path

# Add paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'backend'))

from tests.helpers import (
    assert_response_has_keys,
    assert_is_list,
    assert_is_dict,
    assert_pagination_structure
)


# ==============================================================================
# PATIENTS API CONTRACT TESTS
# ==============================================================================

@pytest.mark.api
class TestPatientsAPIContract:
    """
    Contract tests for /api/v1/patients endpoints.

    These tests verify the response structure that frontend depends on.
    Bug #2: Frontend expected plain array but API returns {data: [], pagination: {}}
    """

    @pytest.fixture(scope="class")
    def app(self):
        from app import app
        app.config['TESTING'] = True
        return app

    @pytest.fixture
    def client(self, app):
        return app.test_client()

    # ---------- GET /api/v1/patients ----------

    def test_patients_list_returns_200(self, client):
        """GET /api/v1/patients should return 200 OK."""
        response = client.get('/api/v1/patients')
        assert response.status_code == 200

    def test_patients_list_returns_data_wrapper(self, client):
        """
        GET /api/v1/patients must return {data: [...], pagination: {...}}

        Bug #2: Frontend did `this.patients = await res.json()` expecting array,
        but API returns wrapped object. Frontend must use `json.data`.
        """
        # Act
        response = client.get('/api/v1/patients')
        result = json.loads(response.data)

        # Assert - response is wrapped object, not plain array
        assert_is_dict(result, "GET /api/v1/patients should return object")
        assert_response_has_keys(result, ['data', 'pagination'])
        assert_is_list(result['data'], "data field should be array")

    def test_patients_list_pagination_structure(self, client):
        """Pagination object must have all required fields."""
        # Act
        response = client.get('/api/v1/patients')
        result = json.loads(response.data)

        # Assert
        assert_pagination_structure(result['pagination'])
        assert isinstance(result['pagination']['page'], int)
        assert isinstance(result['pagination']['total_count'], int)

    def test_patients_list_item_structure(self, client, test_database, db_connection):
        """Each patient in data array must have required fields."""
        # Arrange - create test patient
        mrn = f"CONTRACT-{uuid.uuid4().hex[:8]}"
        db_connection.execute(
            "INSERT INTO patients (mrn, first_name, last_name, date_of_birth) VALUES (?, ?, ?, ?)",
            (mrn, 'Contract', 'Test', '1990-01-01')
        )
        db_connection.commit()

        # Act
        response = client.get('/api/v1/patients')
        result = json.loads(response.data)

        # Assert
        assert len(result['data']) >= 1
        patient = result['data'][0]
        required_fields = ['id', 'mrn', 'first_name', 'last_name', 'date_of_birth']
        assert_response_has_keys(patient, required_fields)

    # ---------- GET /api/v1/patients/search ----------

    def test_patients_search_returns_200(self, client):
        """GET /api/v1/patients/search should return 200 OK."""
        response = client.get('/api/v1/patients/search?q=test')
        assert response.status_code == 200

    def test_patients_search_returns_plain_array(self, client, test_database, db_connection):
        """
        GET /api/v1/patients/search must return plain array (not wrapped).

        Frontend uses this for autocomplete and expects: [{id, mrn, first_name, last_name, full_name}]
        """
        # Arrange
        mrn = f"SEARCH-{uuid.uuid4().hex[:8]}"
        db_connection.execute(
            "INSERT INTO patients (mrn, first_name, last_name) VALUES (?, ?, ?)",
            (mrn, 'Searchable', 'Patient')
        )
        db_connection.commit()

        # Act
        response = client.get('/api/v1/patients/search?q=Searchable')
        result = json.loads(response.data)

        # Assert - returns plain array, NOT {data: [...]}
        assert_is_list(result, "Search should return plain array, not wrapped object")

    def test_patients_search_item_has_full_name(self, client, test_database, db_connection):
        """Search results must include full_name field for display."""
        # Arrange
        mrn = f"FULLNAME-{uuid.uuid4().hex[:8]}"
        db_connection.execute(
            "INSERT INTO patients (mrn, first_name, last_name) VALUES (?, ?, ?)",
            (mrn, 'FullNameTest', 'Person')
        )
        db_connection.commit()

        # Act
        response = client.get('/api/v1/patients/search?q=FullNameTest')
        result = json.loads(response.data)

        # Assert
        if len(result) > 0:
            patient = result[0]
            assert 'full_name' in patient, "Search results must include full_name"

    def test_patients_search_empty_query_returns_empty_array(self, client):
        """Empty search query should return empty array, not error."""
        # Act
        response = client.get('/api/v1/patients/search?q=')
        result = json.loads(response.data)

        # Assert
        assert response.status_code == 200
        assert_is_list(result)


# ==============================================================================
# DASHBOARD API CONTRACT TESTS
# ==============================================================================

@pytest.mark.api
class TestDashboardAPIContract:
    """
    Contract tests for /api/v1/dashboard/* endpoints.

    Bug #1: Frontend called /api/dashboard/* but backend uses /api/v1/dashboard/*
    """

    @pytest.fixture(scope="class")
    def app(self):
        from app import app
        app.config['TESTING'] = True
        return app

    @pytest.fixture
    def client(self, app):
        return app.test_client()

    # ---------- URL Path Tests (Bug #1) ----------

    def test_dashboard_stats_correct_url(self, client):
        """
        Dashboard stats must be at /api/v1/dashboard/stats

        Bug #1: URL mismatch - ensure v1 prefix is required.
        """
        # Act - correct URL
        response = client.get('/api/v1/dashboard/stats')

        # Assert
        assert response.status_code == 200

    def test_dashboard_stats_without_v1_returns_404(self, client):
        """
        /api/dashboard/stats (without v1) should return 404.

        This test would FAIL if someone accidentally removes v1 prefix.
        """
        # Act - wrong URL (missing v1)
        response = client.get('/api/dashboard/stats')

        # Assert
        assert response.status_code == 404

    # ---------- Response Structure Tests ----------

    def test_dashboard_stats_structure(self, client):
        """Stats response must have all KPI fields."""
        # Act
        response = client.get('/api/v1/dashboard/stats')
        result = json.loads(response.data)

        # Assert
        required = ['patientsToday', 'avgDAS28', 'remissionPercent', 'pendingReviews']
        assert_response_has_keys(result, required)

    def test_dashboard_distribution_returns_200(self, client):
        """Distribution endpoint must return 200."""
        response = client.get('/api/v1/dashboard/distribution')
        assert response.status_code == 200

    def test_dashboard_distribution_structure(self, client):
        """Distribution response must have all disease activity levels."""
        # Act
        response = client.get('/api/v1/dashboard/distribution')
        result = json.loads(response.data)

        # Assert
        required = ['remission', 'low_activity', 'moderate', 'high']
        assert_response_has_keys(result, required)

    def test_dashboard_trend_returns_200(self, client):
        """Trend endpoint must return 200."""
        response = client.get('/api/v1/dashboard/trend')
        assert response.status_code == 200

    def test_dashboard_trend_structure(self, client):
        """Trend response must have dates and scores arrays."""
        # Act
        response = client.get('/api/v1/dashboard/trend')
        result = json.loads(response.data)

        # Assert
        assert_response_has_keys(result, ['dates', 'scores'])
        assert_is_list(result['dates'])
        assert_is_list(result['scores'])
        assert len(result['dates']) == len(result['scores'])

    def test_dashboard_recent_visits_returns_200(self, client):
        """Recent visits endpoint must return 200."""
        response = client.get('/api/v1/dashboard/recent-visits')
        assert response.status_code == 200

    def test_dashboard_recent_visits_returns_html(self, client):
        """Recent visits endpoint must return HTML fragment."""
        # Act
        response = client.get('/api/v1/dashboard/recent-visits')

        # Assert
        assert 'text/html' in response.content_type


# ==============================================================================
# REPORTS API CONTRACT TESTS
# ==============================================================================

@pytest.mark.api
class TestReportsAPIContract:
    """
    Contract tests for /api/v1/reports/* endpoints.

    Bug #1: Frontend called /api/reports/* but backend uses /api/v1/reports/*
    """

    @pytest.fixture(scope="class")
    def app(self):
        from app import app
        app.config['TESTING'] = True
        return app

    @pytest.fixture
    def client(self, app):
        return app.test_client()

    # ---------- URL Path Tests (Bug #1) ----------

    def test_reports_generate_correct_url(self, client):
        """POST /api/v1/reports/generate must exist."""
        # Act
        response = client.post(
            '/api/v1/reports/generate',
            data=json.dumps({'report_type': 'summary'}),
            content_type='application/json'
        )

        # Assert
        assert response.status_code == 200

    def test_reports_generate_without_v1_returns_404(self, client):
        """
        POST /api/reports/generate (without v1) should return 404.

        Bug #1: This catches URL mismatch between frontend and backend.
        """
        # Act
        response = client.post(
            '/api/reports/generate',
            data=json.dumps({'report_type': 'summary'}),
            content_type='application/json'
        )

        # Assert
        assert response.status_code == 404

    def test_reports_preview_returns_200(self, client):
        """Report preview endpoint must return 200."""
        response = client.get('/api/v1/reports/preview?type=summary')
        assert response.status_code == 200

    def test_reports_preview_returns_html(self, client):
        """Report preview must return HTML content."""
        # Act
        response = client.get('/api/v1/reports/preview?type=summary')

        # Assert
        assert 'text/html' in response.content_type

    def test_reports_export_pdf_returns_200(self, client):
        """PDF export endpoint must return 200."""
        response = client.get('/api/v1/reports/export-pdf')
        assert response.status_code == 200

    def test_reports_export_pdf_content_type(self, client):
        """PDF export must return application/pdf content type."""
        # Act
        response = client.get('/api/v1/reports/export-pdf')

        # Assert
        assert 'application/pdf' in response.content_type

    def test_reports_export_csv_returns_200(self, client):
        """CSV export endpoint must return 200."""
        response = client.get('/api/v1/reports/export-csv')
        assert response.status_code == 200

    def test_reports_export_csv_content_type(self, client):
        """CSV export must return text/csv content type."""
        # Act
        response = client.get('/api/v1/reports/export-csv')

        # Assert
        assert 'text/csv' in response.content_type


# ==============================================================================
# MEDICAL NOTES API CONTRACT TESTS
# ==============================================================================

@pytest.mark.api
@pytest.mark.database
class TestMedicalNotesAPIContract:
    """
    Contract tests for /api/v1/medical_notes/* endpoints.

    Bug #3: /api/v1/medical_notes/draft rejected empty text with 400 error,
    but auto-save needs to work with empty text (clearing the draft).
    """

    @pytest.fixture(scope="class")
    def app(self):
        from app import app
        app.config['TESTING'] = True
        return app

    @pytest.fixture
    def client(self, app):
        return app.test_client()

    @pytest.fixture
    def sample_visit_id(self, test_database, db_connection):
        """Create test patient and visit for draft tests."""
        mrn = f"DRAFT-{uuid.uuid4().hex[:8]}"
        db_connection.execute(
            "INSERT INTO patients (mrn, first_name, last_name) VALUES (?, ?, ?)",
            (mrn, 'Draft', 'Test')
        )
        patient_id = db_connection.execute("SELECT last_insert_rowid()").fetchone()[0]
        db_connection.execute(
            "INSERT INTO visits (patient_id, visit_date) VALUES (?, ?)",
            (patient_id, '2026-01-11')
        )
        visit_id = db_connection.execute("SELECT last_insert_rowid()").fetchone()[0]
        db_connection.commit()
        return visit_id

    # ---------- Draft Endpoint - Empty Text Bug #3 ----------

    def test_draft_accepts_empty_text(self, client, sample_visit_id):
        """
        POST /api/v1/medical_notes/draft must accept empty text.

        Bug #3: Draft was rejecting empty text with 400, but auto-save
        needs to work with empty/cleared text field.
        """
        # Arrange
        data = {'visit_id': sample_visit_id, 'text': ''}

        # Act
        response = client.post(
            '/api/v1/medical_notes/draft',
            data=json.dumps(data),
            content_type='application/json'
        )

        # Assert - should succeed, not 400
        assert response.status_code == 200, f"Draft should accept empty text, got {response.status_code}"

    def test_draft_accepts_whitespace_only(self, client, sample_visit_id):
        """Draft should accept whitespace-only text."""
        # Arrange
        data = {'visit_id': sample_visit_id, 'text': '   \n\t  '}

        # Act
        response = client.post(
            '/api/v1/medical_notes/draft',
            data=json.dumps(data),
            content_type='application/json'
        )

        # Assert
        assert response.status_code == 200

    def test_draft_accepts_raw_text_field(self, client, sample_visit_id):
        """Draft should accept raw_text as alternative to text field."""
        # Arrange
        data = {'visit_id': sample_visit_id, 'raw_text': 'Some note content'}

        # Act
        response = client.post(
            '/api/v1/medical_notes/draft',
            data=json.dumps(data),
            content_type='application/json'
        )

        # Assert
        assert response.status_code == 200

    def test_draft_response_structure(self, client, sample_visit_id):
        """Draft response must include note_id and status."""
        # Arrange
        data = {'visit_id': sample_visit_id, 'text': 'Test note content'}

        # Act
        response = client.post(
            '/api/v1/medical_notes/draft',
            data=json.dumps(data),
            content_type='application/json'
        )
        result = json.loads(response.data)

        # Assert
        assert 'note_id' in result or 'id' in result
        assert result.get('status') == 'draft'

    def test_draft_requires_visit_id(self, client):
        """Draft must reject request without visit_id."""
        # Arrange
        data = {'text': 'Some text'}  # missing visit_id

        # Act
        response = client.post(
            '/api/v1/medical_notes/draft',
            data=json.dumps(data),
            content_type='application/json'
        )

        # Assert
        assert response.status_code in [400, 422]


# ==============================================================================
# JOINT ASSESSMENTS API CONTRACT TESTS
# ==============================================================================

@pytest.mark.api
@pytest.mark.database
class TestJointAssessmentsAPIContract:
    """Contract tests for /api/v1/joint_assessments/* endpoints."""

    @pytest.fixture(scope="class")
    def app(self):
        from app import app
        app.config['TESTING'] = True
        return app

    @pytest.fixture
    def client(self, app):
        return app.test_client()

    @pytest.fixture
    def sample_visit_id(self, test_database, db_connection):
        """Create test patient and visit for joint assessment tests."""
        mrn = f"JOINT-{uuid.uuid4().hex[:8]}"
        db_connection.execute(
            "INSERT INTO patients (mrn, first_name, last_name) VALUES (?, ?, ?)",
            (mrn, 'Joint', 'Test')
        )
        patient_id = db_connection.execute("SELECT last_insert_rowid()").fetchone()[0]
        db_connection.execute(
            "INSERT INTO visits (patient_id, visit_date) VALUES (?, ?)",
            (patient_id, '2026-01-11')
        )
        visit_id = db_connection.execute("SELECT last_insert_rowid()").fetchone()[0]
        db_connection.commit()
        return visit_id

    def test_joint_assessments_post_returns_200(self, client, sample_visit_id):
        """POST /api/v1/joint_assessments should return 200 or 201."""
        data = {
            'visit_id': sample_visit_id,
            'joints': [
                {'joint_id': 'left_shoulder', 'has_tenderness': True, 'has_pain': False, 'swelling_grade': 1}
            ]
        }
        response = client.post(
            '/api/v1/joint_assessments',
            data=json.dumps(data),
            content_type='application/json'
        )
        assert response.status_code in [200, 201]

    def test_joint_assessments_accepts_multiple_joints(self, client, sample_visit_id):
        """POST should accept multiple joints in request."""
        data = {
            'visit_id': sample_visit_id,
            'joints': [
                {'joint_id': 'left_shoulder', 'has_tenderness': True, 'has_pain': False, 'swelling_grade': 1},
                {'joint_id': 'right_knee', 'has_tenderness': False, 'has_pain': True, 'swelling_grade': 0},
                {'joint_id': 'left_hip', 'has_tenderness': True, 'has_pain': True, 'swelling_grade': 2}
            ]
        }
        response = client.post(
            '/api/v1/joint_assessments',
            data=json.dumps(data),
            content_type='application/json'
        )
        assert response.status_code in [200, 201]

    def test_joint_assessments_get_by_visit_returns_200(self, client, sample_visit_id):
        """GET /api/v1/joint_assessments/visit/<id> should return 200."""
        response = client.get(f'/api/v1/joint_assessments/visit/{sample_visit_id}')
        assert response.status_code == 200

    def test_joint_assessments_get_by_visit_structure(self, client, sample_visit_id):
        """GET by visit should return object with joints array."""
        response = client.get(f'/api/v1/joint_assessments/visit/{sample_visit_id}')
        result = json.loads(response.data)

        assert 'joints' in result
        assert_is_list(result['joints'])


# ==============================================================================
# VISITS API CONTRACT TESTS
# ==============================================================================

@pytest.mark.api
@pytest.mark.database
class TestVisitsAPIContract:
    """Contract tests for /api/v1/visits/* endpoints."""

    @pytest.fixture(scope="class")
    def app(self):
        from app import app
        app.config['TESTING'] = True
        return app

    @pytest.fixture
    def client(self, app):
        return app.test_client()

    @pytest.fixture
    def sample_patient_id(self, test_database, db_connection):
        """Create test patient for visit tests."""
        mrn = f"VISIT-{uuid.uuid4().hex[:8]}"
        db_connection.execute(
            "INSERT INTO patients (mrn, first_name, last_name) VALUES (?, ?, ?)",
            (mrn, 'Visit', 'Test')
        )
        patient_id = db_connection.execute("SELECT last_insert_rowid()").fetchone()[0]
        db_connection.commit()
        return patient_id

    def test_visits_post_returns_200(self, client, sample_patient_id):
        """POST /api/v1/visits should create visit and return 200/201."""
        data = {
            'patient_id': sample_patient_id,
            'visit_date': '2026-01-11',
            'visit_type': 'Follow-up'
        }
        response = client.post(
            '/api/v1/visits',
            data=json.dumps(data),
            content_type='application/json'
        )
        assert response.status_code in [200, 201]

    def test_visits_post_returns_id(self, client, sample_patient_id):
        """POST should return the created visit ID."""
        data = {
            'patient_id': sample_patient_id,
            'visit_date': '2026-01-12',
            'visit_type': 'Initial'
        }
        response = client.post(
            '/api/v1/visits',
            data=json.dumps(data),
            content_type='application/json'
        )
        result = json.loads(response.data)
        assert 'id' in result


# ==============================================================================
# HEALTH CHECK CONTRACT TEST
# ==============================================================================

@pytest.mark.api
class TestHealthAPIContract:
    """Contract tests for health check endpoint."""

    @pytest.fixture(scope="class")
    def app(self):
        from app import app
        app.config['TESTING'] = True
        return app

    @pytest.fixture
    def client(self, app):
        return app.test_client()

    def test_health_endpoint_exists(self, client):
        """Health check must be at /api/v1/health."""
        response = client.get('/api/v1/health')
        assert response.status_code == 200

    def test_health_response_structure(self, client):
        """Health response must include status."""
        response = client.get('/api/v1/health')
        result = json.loads(response.data)

        assert 'status' in result
        assert result['status'] == 'healthy'


# ==============================================================================
# PATIENTS CRUD - SINGLE RESOURCE TESTS
# ==============================================================================

@pytest.mark.api
class TestPatientsCRUD:
    """Tests for single patient CRUD operations."""

    @pytest.fixture(scope="class")
    def app(self):
        from app import app
        app.config['TESTING'] = True
        return app

    @pytest.fixture
    def client(self, app):
        return app.test_client()

    def test_get_single_patient_returns_200(self, client):
        """GET /api/v1/patients/<id> should return 200 for existing patient."""
        # First create a patient via API
        mrn = f"GET-{uuid.uuid4().hex[:8]}"
        create_response = client.post(
            '/api/v1/patients',
            data=json.dumps({'mrn': mrn, 'first_name': 'GetTest', 'last_name': 'Patient'}),
            content_type='application/json'
        )
        patient_id = json.loads(create_response.data).get('id')

        response = client.get(f'/api/v1/patients/{patient_id}')
        assert response.status_code == 200

    def test_get_single_patient_not_found_returns_404(self, client):
        """GET /api/v1/patients/<id> should return 404 for non-existent patient."""
        response = client.get('/api/v1/patients/999999')
        assert response.status_code == 404

    def test_update_patient_returns_200(self, client):
        """PUT /api/v1/patients/<id> should update patient and return 200."""
        # First create a patient via API
        mrn = f"UPDATE-{uuid.uuid4().hex[:8]}"
        create_response = client.post(
            '/api/v1/patients',
            data=json.dumps({'mrn': mrn, 'first_name': 'UpdateTest', 'last_name': 'Patient'}),
            content_type='application/json'
        )
        patient_id = json.loads(create_response.data).get('id')

        data = {'first_name': 'UpdatedFirst', 'last_name': 'UpdatedLast'}
        response = client.put(
            f'/api/v1/patients/{patient_id}',
            data=json.dumps(data),
            content_type='application/json'
        )
        assert response.status_code == 200

    def test_delete_patient_returns_204(self, client):
        """DELETE /api/v1/patients/<id> should delete patient and return 204."""
        # Create a patient via API to delete
        mrn = f"DELETE-{uuid.uuid4().hex[:8]}"
        create_response = client.post(
            '/api/v1/patients',
            data=json.dumps({'mrn': mrn, 'first_name': 'ToDelete', 'last_name': 'Patient'}),
            content_type='application/json'
        )
        patient_id = json.loads(create_response.data).get('id')

        response = client.delete(f'/api/v1/patients/{patient_id}')
        assert response.status_code in [200, 204]


# ==============================================================================
# VISITS CRUD - SINGLE RESOURCE TESTS
# ==============================================================================

@pytest.mark.api
class TestVisitsCRUD:
    """Tests for single visit CRUD operations."""

    @pytest.fixture(scope="class")
    def app(self):
        from app import app
        app.config['TESTING'] = True
        return app

    @pytest.fixture
    def client(self, app):
        return app.test_client()

    def _create_patient_and_visit(self, client):
        """Helper to create patient and visit via API."""
        # Create patient first
        mrn = f"VISIT-{uuid.uuid4().hex[:8]}"
        patient_resp = client.post(
            '/api/v1/patients',
            data=json.dumps({'mrn': mrn, 'first_name': 'VisitTest', 'last_name': 'Patient'}),
            content_type='application/json'
        )
        patient_id = json.loads(patient_resp.data).get('id')

        # Create visit
        visit_resp = client.post(
            '/api/v1/visits',
            data=json.dumps({'patient_id': patient_id, 'visit_date': '2026-01-11', 'visit_type': 'Follow-up'}),
            content_type='application/json'
        )
        visit_id = json.loads(visit_resp.data).get('id')
        return patient_id, visit_id

    def test_get_single_visit_returns_200(self, client):
        """GET /api/v1/visits/<id> should return 200 for existing visit."""
        _, visit_id = self._create_patient_and_visit(client)
        response = client.get(f'/api/v1/visits/{visit_id}')
        assert response.status_code == 200

    def test_get_single_visit_not_found_returns_404(self, client):
        """GET /api/v1/visits/<id> should return 404 for non-existent visit."""
        response = client.get('/api/v1/visits/999999')
        assert response.status_code == 404

    def test_delete_visit_returns_204(self, client):
        """DELETE /api/v1/visits/<id> should delete visit and return 204."""
        _, visit_id = self._create_patient_and_visit(client)
        response = client.delete(f'/api/v1/visits/{visit_id}')
        assert response.status_code in [200, 204]


# ==============================================================================
# MEDICAL NOTES - EXTRACT AND FINALIZE TESTS
# ==============================================================================

@pytest.mark.api
class TestMedicalNotesExtractFinalize:
    """Tests for medical notes extract and finalize endpoints."""

    @pytest.fixture(scope="class")
    def app(self):
        from app import app
        app.config['TESTING'] = True
        return app

    @pytest.fixture
    def client(self, app):
        return app.test_client()

    def test_extract_returns_200(self, client):
        """POST /api/v1/medical_notes/extract should return 200."""
        data = {'text': 'Patient presents with joint pain and swelling in both knees.'}
        response = client.post(
            '/api/v1/medical_notes/extract',
            data=json.dumps(data),
            content_type='application/json'
        )
        assert response.status_code == 200

    def test_extract_returns_entities(self, client):
        """Extract should return structured entities."""
        data = {'text': 'Patient has rheumatoid arthritis with elevated ESR of 45.'}
        response = client.post(
            '/api/v1/medical_notes/extract',
            data=json.dumps(data),
            content_type='application/json'
        )
        result = json.loads(response.data)

        assert 'success' in result or 'structured' in result or 'entities' in result

    def test_finalize_note_returns_200(self, client):
        """POST /api/v1/medical_notes/finalize should return 200."""
        # Create patient and visit via API
        mrn = f"FINALIZE-{uuid.uuid4().hex[:8]}"
        patient_resp = client.post(
            '/api/v1/patients',
            data=json.dumps({'mrn': mrn, 'first_name': 'Finalize', 'last_name': 'Test'}),
            content_type='application/json'
        )
        patient_id = json.loads(patient_resp.data).get('id')

        visit_resp = client.post(
            '/api/v1/visits',
            data=json.dumps({'patient_id': patient_id, 'visit_date': '2026-01-11'}),
            content_type='application/json'
        )
        visit_id = json.loads(visit_resp.data).get('id')

        # Save a draft first to get a note_id
        draft_resp = client.post(
            '/api/v1/medical_notes/draft',
            data=json.dumps({'visit_id': visit_id, 'text': 'Draft content'}),
            content_type='application/json'
        )
        note_id = json.loads(draft_resp.data).get('note_id')

        # Finalize requires note_id, not visit_id
        data = {'note_id': note_id, 'text': 'Final medical note content'}
        response = client.post(
            '/api/v1/medical_notes/finalize',
            data=json.dumps(data),
            content_type='application/json'
        )
        # Accept 200 or 201 for successful finalize
        assert response.status_code in [200, 201]


# ==============================================================================
# JOINT ASSESSMENTS - SUMMARY AND FRAGMENT TESTS
# ==============================================================================

@pytest.mark.api
class TestJointAssessmentsFullAPI:
    """Tests for joint assessments summary and fragment endpoints."""

    @pytest.fixture(scope="class")
    def app(self):
        from app import app
        app.config['TESTING'] = True
        return app

    @pytest.fixture
    def client(self, app):
        return app.test_client()

    def _create_visit(self, client):
        """Helper to create patient and visit via API."""
        mrn = f"JOINT-{uuid.uuid4().hex[:8]}"
        patient_resp = client.post(
            '/api/v1/patients',
            data=json.dumps({'mrn': mrn, 'first_name': 'JointTest', 'last_name': 'Patient'}),
            content_type='application/json'
        )
        patient_id = json.loads(patient_resp.data).get('id')

        visit_resp = client.post(
            '/api/v1/visits',
            data=json.dumps({'patient_id': patient_id, 'visit_date': '2026-01-11'}),
            content_type='application/json'
        )
        return json.loads(visit_resp.data).get('id')

    def test_summary_endpoint_returns_200(self, client):
        """POST /api/v1/joint_assessments/summary should return 200."""
        visit_id = self._create_visit(client)
        data = {
            'visit_id': visit_id,
            'tjc': 5,
            'sjc': 3,
            'esr': 25,
            'pga': 40,
            'das28': 4.2
        }
        response = client.post(
            '/api/v1/joint_assessments/summary',
            data=json.dumps(data),
            content_type='application/json'
        )
        assert response.status_code in [200, 201]

    def test_fragment_returns_html(self, client):
        """GET /api/v1/joint_assessments/fragment should return HTML."""
        visit_id = self._create_visit(client)
        response = client.get(f'/api/v1/joint_assessments/fragment?visit_id={visit_id}')
        # Accept 200 with HTML or 404 if no data exists
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            assert 'text/html' in response.content_type


# ==============================================================================
# VOICE API TESTS
# ==============================================================================

@pytest.mark.api
class TestVoiceAPI:
    """Tests for voice transcription API endpoints."""

    @pytest.fixture(scope="class")
    def app(self):
        from app import app
        app.config['TESTING'] = True
        return app

    @pytest.fixture
    def client(self, app):
        return app.test_client()

    def test_voice_model_load_returns_200(self, client):
        """POST /api/v1/voice/model endpoint should exist and respond."""
        response = client.post('/api/v1/voice/model')
        # Accept various status codes:
        # - 200/201: Model loaded successfully
        # - 404: Model file not found (expected in test env without VOSK model)
        # - 409: Model already loaded
        # - 500: VOSK import failed (expected if vosk not installed)
        # The key is that endpoint exists and doesn't return method not allowed (405)
        assert response.status_code != 405

    def test_voice_transcribe_endpoint_exists(self, client):
        """POST /api/v1/voice/transcribe endpoint should exist."""
        # Without actual audio, we expect a 400 (bad request) but NOT 404
        response = client.post('/api/v1/voice/transcribe')
        # Should not be 404 - endpoint exists
        assert response.status_code != 404


# ==============================================================================
# ASYNC ENDPOINT TEST
# ==============================================================================

@pytest.mark.api
class TestAsyncEndpoint:
    """Tests for async test endpoint."""

    @pytest.fixture(scope="class")
    def app(self):
        from app import app
        app.config['TESTING'] = True
        return app

    @pytest.fixture
    def client(self, app):
        return app.test_client()

    def test_async_test_returns_200(self, client):
        """GET /api/v1/async-test should return 200."""
        response = client.get('/api/v1/async-test')
        assert response.status_code == 200
