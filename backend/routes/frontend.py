from flask import Blueprint, render_template, request, redirect, url_for

frontend_bp = Blueprint('frontend', __name__)

def get_layout():
    if request.headers.get('HX-Request'):
        return 'base_htmx.html'
    return 'base.html'

@frontend_bp.route('/')
def dashboard():
    return render_template('dashboard.html', layout=get_layout())

@frontend_bp.route('/medical-note')
def medical_note():
    return render_template('medical_note.html', layout=get_layout())

@frontend_bp.route('/visit/<int:visit_id>')
def visit(visit_id):
    """Shorthand route for accessing a visit's medical note"""
    return redirect(url_for('frontend.medical_note', visit_id=visit_id))

@frontend_bp.route('/patients')
def patients():
    return render_template('patients.html', layout=get_layout())

@frontend_bp.route('/reports')
def reports():
    return render_template('reports.html', layout=get_layout())
