"""
Patient management endpoints
"""
from flask import Blueprint, request, jsonify, render_template
from utils.database import get_db

patients_bp = Blueprint('patients', __name__)

@patients_bp.route('', methods=['POST'])
def create_patient():
    """Create new patient"""
    data = request.get_json()
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO patients (mrn, first_name, last_name, date_of_birth)
        VALUES (?, ?, ?, ?)
    ''', (data['mrn'], data['first_name'], data['last_name'], data.get('date_of_birth')))

    conn.commit()
    patient_id = cursor.lastrowid
    conn.close()

    return jsonify({
        'id': patient_id,
        'message': 'Patient created'
    }), 201

@patients_bp.route('/<int:patient_id>', methods=['GET'])
def get_patient(patient_id):
    """Retrieve patient by ID"""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM patients WHERE id = ?', (patient_id,))
    patient = cursor.fetchone()
    conn.close()

    if not patient:
        return jsonify({'error': 'Patient not found'}), 404

    return jsonify({
        'id': patient['id'],
        'mrn': patient['mrn'],
        'first_name': patient['first_name'],
        'last_name': patient['last_name'],
        'date_of_birth': patient['date_of_birth'],
        'created_at': patient['created_at']
    }), 200


@patients_bp.route('/fragment', methods=['GET'])
def patients_fragment():
    """Return an HTML fragment with a short patient list for HTMX or server-side includes."""
    conn = get_db()
    cursor = conn.cursor()

    q = request.args.get('q', '')
    if q:
        cursor.execute('''
            SELECT id, mrn, first_name, last_name, date_of_birth
            FROM patients
            WHERE mrn LIKE ? OR first_name LIKE ? OR last_name LIKE ?
            ORDER BY last_name, first_name
            LIMIT 50
        ''', (f"%{q}%", f"%{q}%", f"%{q}%"))
    else:
        cursor.execute('''
            SELECT id, mrn, first_name, last_name, date_of_birth
            FROM patients
            ORDER BY last_name, first_name
            LIMIT 50
        ''')

    rows = cursor.fetchall()
    conn.close()

    patients = [dict(id=r['id'], mrn=r['mrn'], first_name=r['first_name'], last_name=r['last_name'], date_of_birth=r['date_of_birth']) for r in rows]

    return render_template('fragments/patients_list.html', patients=patients)
