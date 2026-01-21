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
        errors = e.errors()
        msg = '; '.join(f"{err['loc'][0]}: {err['msg']}" for err in errors)
        return jsonify({'error': msg}), 400

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


@visits_bp.route('/<int:visit_id>', methods=['GET'])
def get_visit(visit_id):
    """Retrieve visit by ID"""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM visits WHERE id = ?', (visit_id,))
    visit = cursor.fetchone()
    conn.close()

    if not visit:
        return jsonify({'error': 'Visit not found'}), 404

    return jsonify({
        'id': visit['id'],
        'patient_id': visit['patient_id'],
        'visit_date': visit['visit_date'],
        'visit_type': visit['visit_type'],
        'created_at': visit['created_at']
    }), 200


@visits_bp.route('/<int:visit_id>', methods=['DELETE'])
def delete_visit(visit_id):
    """Delete visit by ID"""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('SELECT id FROM visits WHERE id = ?', (visit_id,))
    visit = cursor.fetchone()

    if not visit:
        conn.close()
        return jsonify({'error': 'Visit not found'}), 404

    cursor.execute('DELETE FROM visits WHERE id = ?', (visit_id,))
    conn.commit()
    conn.close()

    return '', 204
