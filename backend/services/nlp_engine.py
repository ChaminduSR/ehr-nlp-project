"""
NLP Engine - Medical entity extraction using spaCy
"""
import spacy
from datetime import datetime

class NLPEngine:
    def __init__(self):
        self.nlp = None
        self.model_version = "en_core_sci_md"

    def load_model(self):
        """Load spaCy model (lazy loading)"""
        if self.nlp is None:
            self.nlp = spacy.load(self.model_version)
        return self.nlp

    def process_note(self, note_text):
        """
        Extract medical entities from clinical note
        Returns: dict with entities and metadata
        """
        if self.nlp is None:
            self.load_model()

        start_time = datetime.now()
        doc = self.nlp(note_text)
        processing_time = (datetime.now() - start_time).total_seconds() * 1000

        entities = []
        for ent in doc.ents:
            entities.append({
                'text': ent.text,
                'type': ent.label_,
                'start': ent.start_char,
                'end': ent.end_char,
                'is_negated': False  # TODO: Add negation detection
            })

        return {
            'success': True,
            'entities': entities,
            'entity_count': len(entities),
            'processing_time_ms': processing_time,
            'model_version': self.model_version
        }

    def get_model_info(self):
        """Get current model information"""
        return {
            'model': self.model_version,
            'loaded': self.nlp is not None
        }

# Global NLP engine instance
nlp_engine = NLPEngine()
