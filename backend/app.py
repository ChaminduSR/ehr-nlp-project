from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from config import get_config
import asyncio
import warnings

# Suppress spaCy FutureWarning about regex patterns
warnings.filterwarnings("ignore", category=FutureWarning, module="spacy")

# Import blueprints
from routes import patients_bp, visits_bp, medical_notes_bp,joint_assessments_bp, voice_bp, analytics_bp
from routes.frontend import frontend_bp

app = Flask(__name__)
CORS(app)
config = get_config()

# Enable async support (Flask 3.0+ default, but explicit config helps)
app.config['ASYNC_SUPPORT'] = True

# Register blueprints
app.register_blueprint(frontend_bp, url_prefix='/')
app.register_blueprint(analytics_bp, url_prefix='/api/v1')
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

@app.route('/api/v1/async-test', methods=['GET'])
async def async_test():
    """Test async endpoint capability"""
    await asyncio.sleep(0.1)
    return jsonify({'status': 'async_working'})

@app.route('/serviceworker.js')
def service_worker():
    return send_from_directory(app.static_folder, 'serviceworker.js')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(app.static_folder, 'img/favicon.ico', mimetype='image/vnd.microsoft.icon')

if __name__ == '__main__':
    app.run(host=config.API_HOST, port=config.API_PORT, debug=config.DEBUG)
