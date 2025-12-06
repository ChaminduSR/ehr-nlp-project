"""
Visit management endpoints
"""
from flask import Blueprint, request, jsonify
from utils.database import get_db

visits_bp = Blueprint('visits', __name__)

@visits_bp.route('', methods=['POST'])
def create_visit():
    """Create new visit for a patient"""
    data = request.get_json()
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO visits (patient_id, visit_date, visit_type)
        VALUES (?, ?, ?)
    ''', (data['patient_id'], data['visit_date'], data.get('visit_type', 'Follow-up')))

    conn.commit()
    visit_id = cursor.lastrowid
    conn.close()

    return jsonify({
        'id': visit_id,
        'patient_id': data['patient_id'],
        'visit_date': data['visit_date'],
        'message': 'Visit created'
    }), 201
