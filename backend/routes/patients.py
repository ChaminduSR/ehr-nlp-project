"""
Patient management endpoints
"""
from flask import Blueprint, request, jsonify
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
