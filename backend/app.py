from flask import Flask, jsonify
from flask_cors import CORS
from config import get_config

# Import blueprints
from routes import patients_bp, visits_bp, medical_notes_bp,joint_assessments_bp, voice_bp
from routes.frontend import frontend_bp

app = Flask(__name__)
CORS(app)
config = get_config()

# Register blueprints
app.register_blueprint(frontend_bp, url_prefix='/')
app.register_blueprint(patients_bp, url_prefix='/api/v1/patients')
app.register_blueprint(visits_bp, url_prefix='/api/v1/visits')
app.register_blueprint(medical_notes_bp, url_prefix='/api/v1/medical_notes')
app.register_blueprint(joint_assessments_bp, url_prefix='/api/v1/joint_assessments')
app.register_blueprint(voice_bp, url_prefix='/api/v1/voice')

@app.route('/api/v1/health', methods=['GET'])
def health_check():
    """Verify server is running"""
    return jsonify({
        'status': 'healthy',
        'environment': config.ENVIRONMENT,
        'version': '3.1'
    })

if __name__ == '__main__':
    app.run(host=config.API_HOST, port=config.API_PORT, debug=config.DEBUG)
