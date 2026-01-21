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
    """Get patients with pagination (JSON)

    Query params:
        page: Page number (default: 1)
        per_page: Items per page (default: 15, max: 100)
        q: Search query (optional)
    """
    # Pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 15, type=int), 100)
    q = request.args.get('q', '').strip()

    offset = (page - 1) * per_page

    conn = get_db()
    cursor = conn.cursor()

    # Build query with optional search
    if q:
        search_pattern = f'%{q}%'
        cursor.execute('SELECT COUNT(*) as total FROM patients WHERE first_name LIKE ? OR last_name LIKE ? OR mrn LIKE ?',
                      (search_pattern, search_pattern, search_pattern))
        total_count = cursor.fetchone()['total']

        cursor.execute('''
            SELECT * FROM patients
            WHERE first_name LIKE ? OR last_name LIKE ? OR mrn LIKE ?
            ORDER BY id DESC
            LIMIT ? OFFSET ?
        ''', (search_pattern, search_pattern, search_pattern, per_page, offset))
    else:
        cursor.execute('SELECT COUNT(*) as total FROM patients')
        total_count = cursor.fetchone()['total']

        cursor.execute('SELECT * FROM patients ORDER BY id DESC LIMIT ? OFFSET ?', (per_page, offset))

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

    total_pages = (total_count + per_page - 1) // per_page

    return jsonify({
        'data': patients,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total_count': total_count,
            'total_pages': total_pages,
            'has_next': page < total_pages,
            'has_prev': page > 1
        }
    })

@patients_bp.route('', methods=['POST'])
def create_patient():
    """Create new patient"""
    data = request.get_json()

    # Validate with Pydantic
    try:
        patient_data = PatientCreate(**data)
    except ValidationError as e:
        errors = e.errors()
        msg = '; '.join(f"{err['loc'][0]}: {err['msg']}" for err in errors)
        return jsonify({'error': msg}), 400

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
        errors = e.errors()
        msg = '; '.join(f"{err['loc'][0]}: {err['msg']}" for err in errors)
        return jsonify({'error': msg}), 400

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


@patients_bp.route('/<int:patient_id>', methods=['DELETE'])
def delete_patient(patient_id):
    """Delete patient by ID (soft delete - marks as inactive)"""
    conn = get_db()
    cursor = conn.cursor()

    # Check if patient exists
    cursor.execute('SELECT id FROM patients WHERE id = ?', (patient_id,))
    patient = cursor.fetchone()

    if not patient:
        conn.close()
        return jsonify({'error': 'Patient not found'}), 404

    # Soft delete: mark as inactive (or hard delete if no is_active column)
    # For now, doing hard delete since schema doesn't have is_active
    cursor.execute('DELETE FROM patients WHERE id = ?', (patient_id,))
    conn.commit()
    conn.close()

    return '', 204
