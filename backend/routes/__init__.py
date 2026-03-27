"""API Routes"""
from .patients import patients_bp
from .visits import visits_bp
from .medical_notes import medical_notes_bp
from .joint_assessments import joint_assessments_bp
from .voice import voice_bp

__all__ = ['patients_bp', 'visits_bp', 'medical_notes_bp', 'joint_assessments_bp', 'voice_bp']