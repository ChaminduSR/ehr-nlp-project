"""
Medical notes endpoints - Auto-save and finalize pattern (async NLP)

Uses new NLP extractor system (Version A: Regex, Version B: Transformers)
Version selection via NLP_VERSION environment variable
"""
import re
import asyncio
from flask import Blueprint, request, jsonify, render_template
from datetime import datetime
from pydantic import ValidationError
from utils.database import get_db
try:
    from schemas import MedicalNoteExtractRequest, MedicalNoteDraftRequest, MedicalNoteFinalizeRequest
except ImportError:
    from backend.schemas import MedicalNoteExtractRequest, MedicalNoteDraftRequest, MedicalNoteFinalizeRequest

# Import new NLP config system
from nlp_config import get_extractor

medical_notes_bp = Blueprint('medical_notes', __name__)

# Get extractor instance (uses NLP_VERSION from environment)
# Version A (default): Regex-based, 0 dependencies
# Version B: Transformer-based, requires transformers library
extractor = get_extractor()


def _run_nlp_extraction(text, entity_extractor):
    """
    Synchronous NLP processing (runs in executor)

    Args:
        text: Medical note text
        entity_extractor: BaseEntityExtractor instance (Version A, B, C, or D)

    Returns:
        ExtractionResult dict with entities, version, processing_time_ms
    """
    return entity_extractor.extract(text)


@medical_notes_bp.route('/extract', methods=['POST'])
async def extract_entities():
    """Extract medical entities from text (async)"""
    data = request.get_json()

    # Validate with Pydantic
    try:
        extract_data = MedicalNoteExtractRequest(**data)
    except ValidationError as e:
        return jsonify({'detail': e.errors()}), 422

    text = extract_data.text

    try:
        # 1. Run NLP Entity Extraction in executor (CPU-bound)
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            _run_nlp_extraction,
            text,
            extractor
        )

        # 2. Initialize Structured Data
        structured = {
            'chief_complaint': '',
            'hpi': '',
            'physical_exam': '',
            'assessment': '',
            'plan': '',
            'medications': [],
            'conditions': [],
            'symptoms': [],
            'lab_tests': [],
            'allergies': [],
            'follow_up': ''
        }

        # 3. Heuristic Section Extraction (Regex)
        # Simple sentence-based extraction for the demo
        text_lower = text.lower()

        # Chief Complaint: "complains of X" or "cc: X"
        cc_match = re.search(r'(?:patient\s+)?complains\s+of\s+(.*?)(?:\.|$)|(?:cc|chief\s+complaint)[:\s]+(.*?)(?:\.|$)', text_lower, re.IGNORECASE)
        if cc_match:
            structured['chief_complaint'] = (cc_match.group(1) or cc_match.group(2)).strip()

        # Assessment: "assessment is X" or "diagnosis: X"
        assess_match = re.search(r'(?:assessment|diagnosis|impression)(?:\s+is)?[:\s]+(.*?)(?:\.|$)', text_lower, re.IGNORECASE)
        if assess_match:
            structured['assessment'] = assess_match.group(1).strip()

        # Plan: "plan is X" or "plan: X"
        plan_match = re.search(r'(?:plan|recommendation)(?:\s+is)?[:\s]+(.*?)(?:\.|$)', text_lower, re.IGNORECASE)
        if plan_match:
            structured['plan'] = plan_match.group(1).strip()

        # 4. Map NLP Entities to Fields (NEW: supports rheumatology entities)
        for ent in result['entities']:
            label = ent['type'].upper()

            # Medications (from new regex patterns)
            if label == 'MEDICATION':
                if ent['text'] not in structured['medications']:
                    structured['medications'].append(ent['text'])

            # Diseases/Conditions
            elif label == 'DISEASE':
                if ent['text'] not in structured['conditions']:
                    structured['conditions'].append(ent['text'])
                # Fallback: If assessment is empty, use the first condition found
                if not structured['assessment']:
                    structured['assessment'] = ent['text']

            # Symptoms
            elif label == 'SYMPTOM':
                if ent['text'] not in structured['symptoms']:
                    structured['symptoms'].append(ent['text'])

            # Lab Tests
            elif label == 'LAB_TEST':
                if ent['text'] not in structured['lab_tests']:
                    structured['lab_tests'].append(ent['text'])

            # Legacy support for old entity types (if Version B uses different labels)
            elif label in ['CHEMICAL', 'DRUG']:
                if ent['text'] not in structured['medications']:
                    structured['medications'].append(ent['text'])
            elif label in ['SYNDROME', 'DISORDER']:
                if ent['text'] not in structured['conditions']:
                    structured['conditions'].append(ent['text'])

        return jsonify({
            'success': True,
            'raw_entities': result['entities'],
            'structured': structured,
            'nlp_version': result['version'],
            'model_name': result['model_name'],
            'processing_time_ms': result['processing_time_ms'],
            'entity_count': len(result['entities'])
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e), 'nlp_version': extractor.get_version()}), 500

@medical_notes_bp.route('/draft', methods=['POST'])
def save_draft():
    """Auto-save draft note every 30 seconds"""
    data = request.get_json()

    # Validate with Pydantic
    try:
        draft_data = MedicalNoteDraftRequest(**data)
    except ValidationError as e:
        return jsonify({'detail': e.errors()}), 422

    raw_text = draft_data.get_text()
    if not raw_text:
        return jsonify({'detail': [{'loc': ['text'], 'msg': 'text or raw_text is required', 'type': 'value_error'}]}), 422

    conn = get_db()
    cursor = conn.cursor()

    # Check if draft already exists for this visit
    cursor.execute('''
        SELECT id FROM medical_notes
        WHERE visit_id = ? AND status = 'draft'
    ''', (draft_data.visit_id,))

    existing_draft = cursor.fetchone()

    if existing_draft:
        # Update existing draft
        cursor.execute('''
            UPDATE medical_notes
            SET note_text = ?, draft_saved_at = ?
            WHERE id = ?
        ''', (raw_text, datetime.utcnow().isoformat(), existing_draft['id']))
        note_id = existing_draft['id']
    else:
        # Create new draft
        cursor.execute('''
            INSERT INTO medical_notes (visit_id, note_text, status, draft_saved_at)
            VALUES (?, ?, 'draft', ?)
        ''', (draft_data.visit_id, raw_text, datetime.utcnow().isoformat()))
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

    # Validate with Pydantic
    try:
        finalize_data = MedicalNoteFinalizeRequest(**data)
    except ValidationError as e:
        return jsonify({'detail': e.errors()}), 422

    final_text = finalize_data.get_text()

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
        ''', (final_text, datetime.utcnow().isoformat(), finalize_data.note_id))

        conn.commit()

        # Trigger NLP processing with new extractor
        nlp_result = extractor.extract(final_text)

        # Store entities count and processing time
        cursor.execute('''
            UPDATE medical_notes
            SET entity_count = ?,
                processing_time_ms = ?
            WHERE id = ?
        ''', (len(nlp_result['entities']), nlp_result['processing_time_ms'], finalize_data.note_id))

        conn.commit()

        return jsonify({
            'success': True,
            'note_id': finalize_data.note_id,
            'status': 'finalized',
            'signed_at': datetime.utcnow().isoformat(),
            'entities_extracted': len(nlp_result['entities']),
            'processing_time_ms': nlp_result['processing_time_ms'],
            'nlp_version': nlp_result['version'],
            'model_name': nlp_result['model_name'],
            'entities': nlp_result['entities'][:10],  # Return first 10 entities as preview
            'message': f'✅ Note finalized and processed with NLP Version {nlp_result["version"]}'
        }), 200

    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500

    finally:
        conn.close()


@medical_notes_bp.route('/fragment', methods=['GET'])
def medical_note_fragment():
    """Return an HTML fragment containing a simple medical note form (for HTMX)."""
    visit_id = request.args.get('visit_id')

    conn = get_db()
    cursor = conn.cursor()

    note = None
    if visit_id:
        cursor.execute('SELECT * FROM medical_notes WHERE visit_id = ? ORDER BY created_at DESC LIMIT 1', (visit_id,))
        row = cursor.fetchone()
        if row:
            note = dict(id=row['id'], visit_id=row['visit_id'], note_text=row['note_text'], status=row['status'])

    conn.close()

    return render_template('fragments/medical_note_form.html', note=note, visit_id=visit_id)
