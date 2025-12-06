"""
Patient management endpoints
"""
from datetime import datetime, date
from flask import Blueprint, request, jsonify, render_template
from utils.database import get_db
try:
    from schemas import PatientResponse
except ImportError:
    from backend.schemas import PatientResponse

patients_bp = Blueprint('patients', __name__)

def calculate_age(dob_str):
    if not dob_str:
        return None
    try:
        born = datetime.strptime(dob_str, '%Y-%m-%d').date()
        today = date.today()
        return today.year - born.year - ((today.month, today.day) < (born.month, born.day))
    except ValueError:
        return None

@patients_bp.route('/search', methods=['GET'])
def search_patients():
    """Search patients by name or MRN"""
    query = request.args.get('q', '').strip()

    if not query:
        return jsonify([])

    conn = get_db()
    cursor = conn.cursor()

    # Search by first name, last name, or MRN (case-insensitive)
    search_pattern = f'%{query}%'
    cursor.execute('''
        SELECT * FROM patients
        WHERE first_name LIKE ? OR last_name LIKE ? OR mrn LIKE ?
        ORDER BY last_name, first_name
        LIMIT 20
    ''', (search_pattern, search_pattern, search_pattern))

    rows = cursor.fetchall()
    conn.close()

    patients = []
    for r in rows:
        patients.append({
            'id': r['id'],
            'mrn': r['mrn'],
            'first_name': r['first_name'],
            'last_name': r['last_name'],
            'date_of_birth': r['date_of_birth'],
            'full_name': f"{r['first_name']} {r['last_name']}"
        })

    return jsonify(patients)

@patients_bp.route('', methods=['GET'])
def get_patients():
    """Get all patients (JSON)"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM patients ORDER BY last_name, first_name')
    rows = cursor.fetchall()
    conn.close()

    patients = []
    for r in rows:
        # Get latest visit
        conn = get_db()
        v_cursor = conn.cursor()
        v_cursor.execute('SELECT id FROM visits WHERE patient_id = ? ORDER BY visit_date DESC LIMIT 1', (r['id'],))
        latest_visit = v_cursor.fetchone()
        v_cursor.close()
        conn.close()

        # Use Pydantic model for validation/serialization
        patient_data = {
            'id': r['id'],
            'mrn': r['mrn'],
            'first_name': r['first_name'],
            'last_name': r['last_name'],
            'date_of_birth': r['date_of_birth'],
            'latest_visit_id': latest_visit['id'] if latest_visit else None
        }
        patients.append(PatientResponse(**patient_data).model_dump())

    return jsonify(patients)

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

@patients_bp.route('/<int:patient_id>', methods=['PUT'])
def update_patient(patient_id):
    """Update patient details"""
    data = request.get_json()
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        UPDATE patients
        SET first_name = ?, last_name = ?, date_of_birth = ?
        WHERE id = ?
    ''', (data['first_name'], data['last_name'], data.get('date_of_birth'), patient_id))

    if cursor.rowcount == 0:
        conn.close()
        return jsonify({'error': 'Patient not found'}), 404

    conn.commit()
    conn.close()

    return jsonify({'message': 'Patient updated'}), 200
