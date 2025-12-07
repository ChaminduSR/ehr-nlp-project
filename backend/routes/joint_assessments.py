
"""Joint assessment endpoints - 3-parameter tracking (tenderness, pain, swelling)
"""
from flask import Blueprint, request, jsonify, render_template
from pydantic import ValidationError
from utils.database import get_db
try:
    from schemas import JointAssessmentCreate
except ImportError:
    from backend.schemas import JointAssessmentCreate

joint_assessments_bp = Blueprint('joint_assessments', __name__)

@joint_assessments_bp.route('/fragment', methods=['GET'])
def joint_assessment_fragment():
    """Return the Joint Assessment HTML fragment (HTMX)"""
    visit_id = request.args.get('visit_id')

    # Fetch existing data if any
    initial_data = {}
    if visit_id:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM joint_assessments WHERE visit_id = ?', (visit_id,))
        rows = cursor.fetchall()
        conn.close()

        for row in rows:
            initial_data[row['joint_id']] = {
                'tenderness': bool(row['has_tenderness']),
                'pain': bool(row['has_pain']),
                'swelling': row['swelling_grade']
            }

    return render_template('fragments/joint_assessment.html', visit_id=visit_id, initial_data=initial_data)

@joint_assessments_bp.route('', methods=['POST'])
def save_joint_assessment():
    """Save joint assessments and optional summary metrics in a single request.

    Accepts:
    - visit_id: required
    - joints: list of joint data
    - summary: optional dict with tjc, sjc, esr, pga, pg_scale, das28
    """
    data = request.get_json()

    # Validate with Pydantic
    try:
        assessment_data = JointAssessmentCreate(**data)
    except ValidationError as e:
        return jsonify({'detail': e.errors()}), 422

    visit_id = assessment_data.visit_id
    joints = assessment_data.joints
    summary = data.get('summary')  # Optional summary data

    conn = get_db()
    cursor = conn.cursor()

    try:
        # Delete existing assessments for this visit (replace with new)
        cursor.execute('DELETE FROM joint_assessments WHERE visit_id = ?', (visit_id,))

        # Insert new assessments
        saved_count = 0
        for joint in joints:
            cursor.execute('''
                INSERT INTO joint_assessments
                (visit_id, joint_id, has_tenderness, has_pain, swelling_grade)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                visit_id,
                joint.joint_id,
                joint.get_tenderness() > 0,
                joint.get_pain() > 0,
                joint.get_swelling()
            ))
            saved_count += 1

        # Save summary if provided (batched with joint data)
        summary_saved = False
        if summary:
            tjc = summary.get('tjc')
            sjc = summary.get('sjc')
            esr = summary.get('esr')
            pga = summary.get('pga')
            das28 = summary.get('das28')
            pg_scale = summary.get('pg_scale')

            cursor.execute('''
                INSERT INTO joint_assessment_summaries (visit_id, tjc, sjc, esr, pga, pg_scale_1_10, das28_score)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (visit_id, tjc, sjc, esr, pga, pg_scale, das28))
            summary_saved = True

        conn.commit()

        return jsonify({
            'success': True,
            'visit_id': visit_id,
            'joints_saved': saved_count,
            'summary_saved': summary_saved,
            'message': f'Saved {saved_count} joint assessments'
        }), 201

    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500

    finally:
        conn.close()

@joint_assessments_bp.route('/visit/<int:visit_id>', methods=['GET'])
def get_joint_assessment_by_visit(visit_id):
    """Get all joint assessments for a specific visit"""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT * FROM joint_assessments
        WHERE visit_id = ?
        ORDER BY assessed_at DESC
    ''', (visit_id,))

    assessments = cursor.fetchall()
    conn.close()

    if not assessments:
        return jsonify({
            'visit_id': visit_id,
            'joints': [],
            'message': 'No joint assessments found for this visit'
        }), 200

    joints_data = []
    for assessment in assessments:
        joints_data.append({
            'id': assessment['id'],
            'joint_id': assessment['joint_id'],
            'has_tenderness': bool(assessment['has_tenderness']),
            'has_pain': bool(assessment['has_pain']),
            'swelling_grade': assessment['swelling_grade'],
            'assessed_at': assessment['assessed_at']
        })

    return jsonify({
        'visit_id': visit_id,
        'joints': joints_data,
        'total_joints': len(joints_data)
    }), 200


@joint_assessments_bp.route('/summary', methods=['POST'])
def save_joint_summary():
    """Save joint summary metrics (TJC, SJC, ESR, PGA, DAS28) for a visit"""
    data = request.get_json() or {}
    visit_id = data.get('visit_id')
    if not visit_id:
        return jsonify({'error': 'visit_id required'}), 400

    tjc = data.get('tjc')
    sjc = data.get('sjc')
    esr = data.get('esr')
    pga = data.get('pga')
    das28 = data.get('das28')
    # Optional Patient Global (1-10)
    pg_scale = data.get('pg_scale')
    try:
        if pg_scale is not None:
            pg_scale = int(pg_scale)
            if pg_scale < 1 or pg_scale > 10:
                return jsonify({'error': 'pg_scale must be 1-10'}), 400
    except Exception:
        return jsonify({'error': 'pg_scale must be an integer between 1 and 10'}), 400

    conn = get_db()
    cursor = conn.cursor()
    try:
        # Ensure summary table exists
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS joint_assessment_summaries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                visit_id INTEGER NOT NULL,
                tjc INTEGER,
                sjc INTEGER,
                esr REAL,
                pga REAL,
                pg_scale_1_10 INTEGER,
                das28_score REAL,
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            INSERT INTO joint_assessment_summaries (visit_id, tjc, sjc, esr, pga, pg_scale_1_10, das28_score)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (visit_id, tjc, sjc, esr, pga, pg_scale, das28))
        conn.commit()
        return jsonify({'success': True, 'visit_id': visit_id}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()
