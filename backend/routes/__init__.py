"""API Routes"""
from .patients import patients_bp
from .visits import visits_bp
from .medical_notes import medical_notes_bp

__all__ = ['patients_bp', 'visits_bp', 'medical_notes_bp']
