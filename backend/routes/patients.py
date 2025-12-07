"""Patient management endpoints"""
from flask import Blueprint, request, jsonify
from pydantic import ValidationError
from utils.database import get_db
try:
    from schemas import PatientResponse, PatientCreate, PatientUpdate
except ImportError:
    from backend.schemas import PatientResponse, PatientCreate, PatientUpdate

patients_bp = Blueprint('patients', __name__)


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
    cursor.execute('SELECT * FROM patients')
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

    # Sort patients by MRN descending (try numeric inside MRN, otherwise string desc)
    def mrn_sort_key(p):
        mrn = p.get('mrn') or ''
        # Extract digits for numeric comparison
        digits = ''.join(ch for ch in str(mrn) if ch.isdigit())
        try:
            return (0, -int(digits)) if digits else (1, str(mrn))
        except Exception:
            return (1, str(mrn))

    patients_sorted = sorted(patients, key=mrn_sort_key)
    return jsonify(patients_sorted)

@patients_bp.route('', methods=['POST'])
def create_patient():
    """Create new patient"""
    data = request.get_json()

    # Validate with Pydantic
    try:
        patient_data = PatientCreate(**data)
    except ValidationError as e:
        return jsonify({'detail': e.errors()}), 422

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO patients (mrn, first_name, last_name, date_of_birth)
        VALUES (?, ?, ?, ?)
    ''', (patient_data.mrn, patient_data.first_name, patient_data.last_name, patient_data.date_of_birth))

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

    # Validate with Pydantic
    try:
        patient_data = PatientUpdate(**data)
    except ValidationError as e:
        return jsonify({'detail': e.errors()}), 422

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        UPDATE patients
        SET first_name = ?, last_name = ?, date_of_birth = ?
        WHERE id = ?
    ''', (patient_data.first_name, patient_data.last_name, patient_data.date_of_birth, patient_id))

    if cursor.rowcount == 0:
        conn.close()
        return jsonify({'error': 'Patient not found'}), 404

    conn.commit()
    conn.close()

    return jsonify({'message': 'Patient updated'}), 200
