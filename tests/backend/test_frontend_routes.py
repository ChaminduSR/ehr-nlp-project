"""
Frontend Route Tests for EHR-NLP System

Tests verify that all frontend routes exist and are accessible.
These tests catch missing routes that cause 404 errors.

Run with: pytest tests/backend/test_frontend_routes.py -v -m api
"""

import pytest
import sys
from pathlib import Path

# Add paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'backend'))


@pytest.mark.api
class TestFrontendRoutes:
    """
    Test that all frontend routes exist and return HTML.

    Bug #4: /visit/<int:visit_id> route didn't exist (returned 404).
    """

    @pytest.fixture(scope="class")
    def app(self):
        from app import app
        app.config['TESTING'] = True
        return app

    @pytest.fixture
    def client(self, app):
        return app.test_client()

    # ---------- Main Page Routes ----------

    def test_dashboard_route_exists(self, client):
        """Dashboard at / must return 200."""
        response = client.get('/')
        assert response.status_code == 200
        assert 'text/html' in response.content_type

    def test_patients_route_exists(self, client):
        """Patients page at /patients must return 200."""
        response = client.get('/patients')
        assert response.status_code == 200
        assert 'text/html' in response.content_type

    def test_medical_note_route_exists(self, client):
        """Medical note page at /medical-note must return 200."""
        response = client.get('/medical-note')
        assert response.status_code == 200
        assert 'text/html' in response.content_type

    def test_reports_route_exists(self, client):
        """Reports page at /reports must return 200."""
        response = client.get('/reports')
        assert response.status_code == 200
        assert 'text/html' in response.content_type

    # ---------- Visit Route (Bug #4) ----------

    def test_visit_route_exists(self, client):
        """
        /visit/<id> route must exist and redirect to medical-note.

        Bug #4: This route was missing, causing 404 when clicking
        visit links from patient list.
        """
        # Act - test with arbitrary visit ID
        response = client.get('/visit/1')

        # Assert - should redirect (302) or return 200
        # The route redirects to /medical-note with visit_id param
        assert response.status_code in [200, 302, 308]

    def test_visit_route_redirects_correctly(self, client):
        """Visit route should redirect to medical-note page."""
        # Act
        response = client.get('/visit/123', follow_redirects=False)

        # Assert
        if response.status_code in [302, 308]:
            location = response.headers.get('Location', '')
            assert 'medical-note' in location
            assert 'visit_id=123' in location

    def test_visit_route_requires_integer_id(self, client):
        """Visit route should reject non-integer IDs."""
        # Act
        response = client.get('/visit/abc')

        # Assert - should be 404 for invalid ID format
        assert response.status_code == 404

    def test_visit_route_with_various_ids(self, client):
        """Visit route should work with various integer IDs."""
        test_ids = [1, 42, 999, 100000]

        for visit_id in test_ids:
            response = client.get(f'/visit/{visit_id}')
            assert response.status_code in [200, 302, 308], f"Failed for visit_id={visit_id}"

    # ---------- HTMX Fragment Support ----------

    def test_dashboard_htmx_header_handled(self, client):
        """Dashboard should handle HX-Request header for HTMX."""
        response = client.get('/', headers={'HX-Request': 'true'})
        assert response.status_code == 200

    def test_patients_htmx_header_handled(self, client):
        """Patients page should handle HX-Request header."""
        response = client.get('/patients', headers={'HX-Request': 'true'})
        assert response.status_code == 200

    def test_medical_note_htmx_header_handled(self, client):
        """Medical note page should handle HX-Request header."""
        response = client.get('/medical-note', headers={'HX-Request': 'true'})
        assert response.status_code == 200

    def test_reports_htmx_header_handled(self, client):
        """Reports page should handle HX-Request header."""
        response = client.get('/reports', headers={'HX-Request': 'true'})
        assert response.status_code == 200

    # ---------- Static Assets ----------

    def test_favicon_accessible(self, client):
        """Favicon should be accessible (200 or 404 if not configured)."""
        response = client.get('/favicon.ico')
        # Should return 200 or 404 if not configured, but not 500
        assert response.status_code in [200, 404]

    def test_serviceworker_accessible(self, client):
        """Service worker JS should be accessible."""
        response = client.get('/serviceworker.js')
        # Should return 200 or 404 if not configured
        assert response.status_code in [200, 404]


@pytest.mark.api
class TestFrontendRouteQueryParams:
    """Test that frontend routes handle query parameters correctly."""

    @pytest.fixture(scope="class")
    def app(self):
        from app import app
        app.config['TESTING'] = True
        return app

    @pytest.fixture
    def client(self, app):
        return app.test_client()

    def test_medical_note_with_visit_id_param(self, client):
        """Medical note page should accept visit_id query param."""
        response = client.get('/medical-note?visit_id=123')
        assert response.status_code == 200

    def test_medical_note_with_patient_id_param(self, client):
        """Medical note page should accept patient_id query param."""
        response = client.get('/medical-note?patient_id=456')
        assert response.status_code == 200

    def test_medical_note_with_both_params(self, client):
        """Medical note page should accept both visit_id and patient_id."""
        response = client.get('/medical-note?visit_id=123&patient_id=456')
        assert response.status_code == 200


@pytest.mark.api
class TestAPIFragmentRoutes:
    """Test API fragment routes used by HTMX."""

    @pytest.fixture(scope="class")
    def app(self):
        from app import app
        app.config['TESTING'] = True
        return app

    @pytest.fixture
    def client(self, app):
        return app.test_client()

    def test_medical_notes_fragment_returns_html(self, client):
        """Medical notes fragment should return HTML."""
        response = client.get('/api/v1/medical_notes/fragment?visit_id=1')
        # May return 200 with HTML or 404 if visit doesn't exist
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            assert 'text/html' in response.content_type

    def test_joint_assessments_fragment_returns_html(self, client):
        """Joint assessments fragment should return HTML."""
        response = client.get('/api/v1/joint_assessments/fragment?visit_id=1')
        # May return 200 with HTML or 404 if visit doesn't exist
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            assert 'text/html' in response.content_type


@pytest.mark.api
class TestErrorRoutes:
    """Test that invalid routes return proper error codes."""

    @pytest.fixture(scope="class")
    def app(self):
        from app import app
        app.config['TESTING'] = True
        return app

    @pytest.fixture
    def client(self, app):
        return app.test_client()

    def test_nonexistent_route_returns_404(self, client):
        """Non-existent routes should return 404."""
        response = client.get('/this-route-does-not-exist')
        assert response.status_code == 404

    def test_nonexistent_api_route_returns_404(self, client):
        """Non-existent API routes should return 404."""
        response = client.get('/api/v1/nonexistent')
        assert response.status_code == 404

    def test_old_api_prefix_returns_404(self, client):
        """Old /api/ prefix (without v1) should return 404."""
        # These are the routes that were broken by Bug #1
        old_routes = [
            '/api/dashboard/stats',
            '/api/reports/generate',
            '/api/reports/preview',
        ]
        for route in old_routes:
            response = client.get(route)
            assert response.status_code == 404, f"Old route {route} should return 404"
