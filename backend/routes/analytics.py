"""
Analytics and Dashboard endpoints
"""
from flask import Blueprint, jsonify, render_template, request, send_file
from datetime import datetime, timedelta
import io

analytics_bp = Blueprint('analytics', __name__)

# --- Dashboard API ---

@analytics_bp.route('/dashboard/stats')
def dashboard_stats():
    """Get KPI statistics for dashboard (Mock Data)"""
    # In a real implementation, query the database
    return jsonify({
        'patientsToday': 12,
        'avgDAS28': 3.4,
        'remissionPercent': 35,
        'pendingReviews': 5
    })

@analytics_bp.route('/dashboard/distribution')
def dashboard_distribution():
    """Get disease activity distribution for pie chart (Mock Data)"""
    return jsonify({
        'remission': 35,
        'low_activity': 40,
        'moderate': 20,
        'high': 5
    })

@analytics_bp.route('/dashboard/trend')
def dashboard_trend():
    """Get 30-day DAS28 trend for line chart (Mock Data)"""
    dates = [(datetime.now() - timedelta(days=i)).strftime('%m/%d') for i in range(30, 0, -1)]
    scores = [3.2, 3.1, 3.0, 2.9, 2.8, 2.9, 3.0, 3.1, 3.3, 3.4,
              3.5, 3.4, 3.3, 3.2, 3.1, 3.0, 2.9, 2.8, 2.7, 2.6,
              2.5, 2.6, 2.7, 2.8, 2.9, 3.0, 3.1, 3.2, 3.3, 3.4]

    return jsonify({
        'dates': dates,
        'scores': scores
    })

@analytics_bp.route('/dashboard/recent-visits')
def dashboard_recent_visits():
    """Return recent visits table as HTML (Mock Data)"""
    # Mock visits
    visits = [
        {'patient_name': 'John Doe', 'date': '2023-10-24', 'das28': 2.1, 'tjc': 2, 'sjc': 1, 'id': 1},
        {'patient_name': 'Jane Smith', 'date': '2023-10-24', 'das28': 3.8, 'tjc': 5, 'sjc': 3, 'id': 2},
        {'patient_name': 'Robert Brown', 'date': '2023-10-23', 'das28': 5.2, 'tjc': 8, 'sjc': 6, 'id': 3},
        {'patient_name': 'Emily Davis', 'date': '2023-10-23', 'das28': 2.9, 'tjc': 3, 'sjc': 2, 'id': 4},
        {'patient_name': 'Michael Wilson', 'date': '2023-10-22', 'das28': 4.1, 'tjc': 6, 'sjc': 4, 'id': 5},
    ]

    return render_template('fragments/recent_visits_table.html', visits=visits)

# --- Reports API ---

@analytics_bp.route('/reports/generate', methods=['POST'])
def generate_report():
    """Generate report data (Mock)"""
    data = request.json
    report_type = data.get('report_type')

    # Simulate processing
    return jsonify({'status': 'ok', 'report_type': report_type})

@analytics_bp.route('/reports/preview')
def report_preview():
    """Render report preview (Mock)"""
    report_type = request.args.get('type', 'summary')
    patient_id = request.args.get('patient_id')

    # Mock data for preview
    patient = {
        'first_name': 'John', 'last_name': 'Doe', 'mrn': 'MRN-12345',
        'dob': datetime(1980, 1, 1), 'id': patient_id or 1
    }
    visits = [
        {'visit_date': datetime.now(), 'das28_score': 2.4, 'tjc': 1, 'sjc': 0, 'esr': 15, 'crp': 2.0},
        {'visit_date': datetime.now() - timedelta(days=30), 'das28_score': 3.1, 'tjc': 3, 'sjc': 1, 'esr': 20, 'crp': 5.0},
    ]
    medications = [
        {'name': 'Methotrexate', 'dose': '15mg', 'frequency': 'Weekly'},
        {'name': 'Folic Acid', 'dose': '5mg', 'frequency': 'Weekly'}
    ]

    return render_template('reports/patient_summary.html',
                           patient=patient,
                           visits=visits,
                           medications=medications,
                           now=datetime.now)

@analytics_bp.route('/reports/export-pdf')
def export_pdf():
    """Export report as PDF (Mock - returns text file for now)"""
    # In real implementation, use WeasyPrint
    dummy_pdf = b"%PDF-1.4 ... (Dummy PDF Content)"
    return send_file(
        io.BytesIO(dummy_pdf),
        mimetype='application/pdf',
        as_attachment=True,
        download_name='report.pdf'
    )

@analytics_bp.route('/reports/export-csv')
def export_csv():
    """Export report as CSV (Mock)"""
    csv_content = "Date,DAS28,TJC,SJC\n2023-10-24,2.4,1,0\n2023-09-24,3.1,3,1"
    return send_file(
        io.BytesIO(csv_content.encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name='report.csv'
    )
