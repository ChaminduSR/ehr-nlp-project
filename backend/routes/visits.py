"""
Visit management endpoints
"""
from flask import Blueprint, request, jsonify
from pydantic import ValidationError
from utils.database import get_db
try:
    from schemas import VisitCreate
except ImportError:
    from backend.schemas import VisitCreate

visits_bp = Blueprint('visits', __name__)

@visits_bp.route('', methods=['POST'])
def create_visit():
    """Create new visit for a patient"""
    data = request.get_json()

    # Validate with Pydantic
    try:
        visit_data = VisitCreate(**data)
    except ValidationError as e:
        return jsonify({'detail': e.errors()}), 422

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO visits (patient_id, visit_date, visit_type)
        VALUES (?, ?, ?)
    ''', (visit_data.patient_id, visit_data.visit_date, visit_data.visit_type or 'Follow-up'))

    conn.commit()
    visit_id = cursor.lastrowid
    conn.close()

    return jsonify({
        'id': visit_id,
        'patient_id': visit_data.patient_id,
        'visit_date': visit_data.visit_date,
        'message': 'Visit created'
    }), 201
