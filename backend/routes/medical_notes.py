"""
Medical notes endpoints - Auto-save and finalize pattern
"""
from flask import Blueprint, request, jsonify
from datetime import datetime
from utils.database import get_db

medical_notes_bp = Blueprint('medical_notes', __name__)

@medical_notes_bp.route('/draft', methods=['POST'])
def save_draft():
    """Auto-save draft note every 30 seconds"""
    data = request.get_json()
    conn = get_db()
    cursor = conn.cursor()
    
    # Check if draft already exists for this visit
    cursor.execute('''
        SELECT id FROM medical_notes 
        WHERE visit_id = ? AND status = 'draft'
    ''', (data['visit_id'],))
    
    existing_draft = cursor.fetchone()
    
    if existing_draft:
        # Update existing draft
        cursor.execute('''
            UPDATE medical_notes 
            SET note_text = ?, draft_saved_at = ?
            WHERE id = ?
        ''', (data['text'], datetime.utcnow().isoformat(), existing_draft['id']))
        note_id = existing_draft['id']
    else:
        # Create new draft
        cursor.execute('''
            INSERT INTO medical_notes (visit_id, note_text, status, draft_saved_at)
            VALUES (?, ?, 'draft', ?)
        ''', (data['visit_id'], data['text'], datetime.utcnow().isoformat()))
        note_id = cursor.lastrowid
    
    conn.commit()
    conn.close()
    
    return jsonify({
        'success': True,
        'note_id': note_id,
        'status': 'draft',
        'draft_saved_at': datetime.utcnow().isoformat(),
        'message': '✅ Draft auto-saved'
    }), 200

@medical_notes_bp.route('/finalize', methods=['POST'])
def finalize_note():
    """Finalize and sign note - triggers NLP"""
    data = request.get_json()
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # Update note status to finalized
        cursor.execute('''
            UPDATE medical_notes 
            SET status = 'finalized', 
                note_text = ?,
                signed_at = ?,
                signed_by = 1
            WHERE id = ?
        ''', (data['text'], datetime.utcnow().isoformat(), data['note_id']))
        
        conn.commit()
        
        # Trigger NLP processing
        from services.nlp_engine import nlp_engine
        nlp_result = nlp_engine.process_note(data['text'])
        
        if nlp_result['success']:
            # Store entities count and processing time
            cursor.execute('''
                UPDATE medical_notes 
                SET entity_count = ?,
                    processing_time_ms = ?
                WHERE id = ?
            ''', (nlp_result['entity_count'], nlp_result['processing_time_ms'], data['note_id']))
            
            conn.commit()
        
        return jsonify({
            'success': True,
            'note_id': data['note_id'],
            'status': 'finalized',
            'signed_at': datetime.utcnow().isoformat(),
            'entities_extracted': nlp_result['entity_count'],
            'processing_time_ms': nlp_result['processing_time_ms'],
            'entities': nlp_result['entities'][:5],  # Return first 5 entities as preview
            'message': '✅ Note finalized and NLP processed'
        }), 200
        
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
        
    finally:
        conn.close()

@medical_notes_bp.route('/<int:note_id>', methods=['GET'])
def get_note(note_id):
    """Retrieve medical note by ID"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM medical_notes WHERE id = ?', (note_id,))
    note = cursor.fetchone()
    conn.close()
    
    if not note:
        return jsonify({'error': 'Note not found'}), 404
    
    return jsonify({
        'id': note['id'],
        'visit_id': note['visit_id'],
        'note_text': note['note_text'],
        'status': note['status'],
        'draft_saved_at': note['draft_saved_at'],
        'signed_at': note['signed_at'],
        'signed_by': note['signed_by'],
        'created_at': note['created_at']
    }), 200
