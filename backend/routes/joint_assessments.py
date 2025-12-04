"""
Joint assessment endpoints - 3-parameter tracking (tenderness, pain, swelling)
"""
from flask import Blueprint, request, jsonify, render_template
from utils.database import get_db

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
    """Save multiple joint assessments for a visit"""
    data = request.get_json()
    visit_id = data.get('visit_id')
    joints = data.get('joints', [])

    if not visit_id or not joints:
        return jsonify({'error': 'visit_id and joints are required'}), 400

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
                joint['joint_id'],
                joint.get('has_tenderness', False),
                joint.get('has_pain', False),
                joint.get('swelling_grade', 0)
            ))
            saved_count += 1

        conn.commit()

        return jsonify({
            'success': True,
            'visit_id': visit_id,
            'joints_saved': saved_count,
            'message': f'✅ Saved {saved_count} joint assessments'
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
