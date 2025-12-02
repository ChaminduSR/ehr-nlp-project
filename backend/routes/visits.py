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

@visits_bp.route('/patient/<int:patient_id>', methods=['GET'])
def get_patient_visits(patient_id):
    """Retrieve all visits for a patient"""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT * FROM visits
        WHERE patient_id = ?
        ORDER BY visit_date DESC, created_at DESC
    ''', (patient_id,))

    rows = cursor.fetchall()
    conn.close()

    visits = []
    for r in rows:
        visits.append({
            'id': r['id'],
            'patient_id': r['patient_id'],
            'visit_date': r['visit_date'],
            'visit_type': r['visit_type'],
            'created_at': r['created_at']
        })

    return jsonify(visits), 200
