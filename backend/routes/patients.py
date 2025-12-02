"""
Patient management endpoints
"""
from datetime import datetime, date
from flask import Blueprint, request, jsonify, render_template
from utils.database import get_db

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


@patients_bp.route('/fragment', methods=['GET'])
def patients_fragment():
    """Return an HTML fragment with a short patient list for HTMX or server-side includes."""
    conn = get_db()
    cursor = conn.cursor()

    q = request.args.get('q', '')
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1

    per_page = 15
    offset = (page - 1) * per_page

    if q:
        # Get total count
        cursor.execute('SELECT COUNT(*) FROM patients WHERE mrn LIKE ? OR first_name LIKE ? OR last_name LIKE ?', (f"%{q}%", f"%{q}%", f"%{q}%"))
        total_count = cursor.fetchone()[0]

        cursor.execute('''
            SELECT id, mrn, first_name, last_name, date_of_birth, created_at
            FROM patients
            WHERE mrn LIKE ? OR first_name LIKE ? OR last_name LIKE ?
            ORDER BY last_name, first_name
            LIMIT ? OFFSET ?
        ''', (f"%{q}%", f"%{q}%", f"%{q}%", per_page, offset))
    else:
        # Get total count
        cursor.execute('SELECT COUNT(*) FROM patients')
        total_count = cursor.fetchone()[0]

        cursor.execute('''
            SELECT id, mrn, first_name, last_name, date_of_birth, created_at
            FROM patients
            ORDER BY last_name, first_name
            LIMIT ? OFFSET ?
        ''', (per_page, offset))

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
            'age': calculate_age(r['date_of_birth']),
            'created_at': r['created_at']
        })

    total_pages = (total_count + per_page - 1) // per_page
    has_next = page < total_pages
    has_prev = page > 1

    return render_template('fragments/patients_list.html',
                           patients=patients,
                           total_count=total_count,
                           page=page,
                           total_pages=total_pages,
                           has_next=has_next,
                           has_prev=has_prev,
                           q=q)
