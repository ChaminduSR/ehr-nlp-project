"""
BioLinkBERT Entity Extractor with Contextual Inference

This extractor uses BioLinkBERT (michiyasunaga/BioLinkBERT-base) for:
1. Entity extraction using semantic similarity
2. Contextual reasoning to infer diagnoses from symptom clusters
3. Entity linking to establish relationships between entities

Unique capability: Infers missing diagnoses from symptom/lab patterns.

Example:
    Input: "Patient has joint pain, morning stiffness, elevated ESR, positive RF"
    Output: Infers "Rheumatoid Arthritis" from the symptom cluster
"""

import time
import re
from typing import List, Dict, Any, Optional, Tuple

from .base_extractor import BaseEntityExtractor, Entity, ExtractionResult

# Check for numpy (optional, only for embeddings)
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    np = None
    NUMPY_AVAILABLE = False

# Check for transformer dependencies (optional, only for model inference)
try:
    import torch
    from transformers import AutoTokenizer, AutoModel
    BIOLINKBERT_DEPS_AVAILABLE = True
except ImportError:
    BIOLINKBERT_DEPS_AVAILABLE = False
    torch = None
    AutoTokenizer = None
    AutoModel = None


class BioLinkBERTExtractor(BaseEntityExtractor):
    """
    BioLinkBERT-based entity extractor with contextual reasoning.

    Uses BioLinkBERT embeddings to:
    - Extract medical entities via semantic similarity
    - Infer diagnoses from symptom/lab clusters
    - Link entities with relationship types

    Model: michiyasunaga/BioLinkBERT-base
    """

    MODEL_NAME = "michiyasunaga/BioLinkBERT-base"
    VERSION = "BioLink"

    # Similarity threshold for entity matching
    SIMILARITY_THRESHOLD = 0.70

    # =========================================
    # INFERENCE RULES (Rheumatology Focus)
    # =========================================
    INFERENCE_RULES = {
        'rheumatoid_arthritis': {
            'display_name': 'Rheumatoid Arthritis',
            'symptoms': [
                'joint pain', 'morning stiffness', 'joint swelling',
                'symmetric arthritis', 'hand stiffness', 'fatigue',
                'swollen joints', 'tender joints', 'stiff joints'
            ],
            'labs': ['ESR', 'CRP', 'RF', 'anti-CCP', 'rheumatoid factor',
                     'erythrocyte sedimentation rate', 'C-reactive protein'],
            'imaging': ['joint erosion', 'synovitis'],
            'min_match': 3,
            'required_categories': ['symptoms'],
            'confidence_boost_markers': ['RF', 'anti-CCP', 'rheumatoid factor'],
            'confidence_boost': 0.1,
            'suggested_actions': [
                'Confirm with anti-CCP antibody test',
                'Consider rheumatology referral',
                'X-ray hands and feet for erosions',
            ],
        },

        'systemic_lupus_erythematosus': {
            'display_name': 'Systemic Lupus Erythematosus',
            'symptoms': [
                'fatigue', 'fever', 'joint pain', 'butterfly rash',
                'malar rash', 'photosensitivity', 'oral ulcers',
                'hair loss', 'Raynaud phenomenon', 'rash'
            ],
            'labs': ['ANA', 'anti-dsDNA', 'anti-Smith', 'low complement',
                     'C3', 'C4', 'proteinuria', 'leukopenia',
                     'antinuclear antibody'],
            'min_match': 4,
            'required_categories': ['labs'],
            'confidence_boost_markers': ['ANA', 'anti-dsDNA'],
            'confidence_boost': 0.15,
            'suggested_actions': [
                'Check ANA and anti-dsDNA titers',
                'Monitor complement levels (C3, C4)',
                'Assess for renal involvement',
            ],
        },

        'psoriatic_arthritis': {
            'display_name': 'Psoriatic Arthritis',
            'symptoms': [
                'joint pain', 'psoriasis', 'nail changes', 'dactylitis',
                'sausage digit', 'enthesitis', 'back pain', 'skin plaques'
            ],
            'labs': ['ESR', 'CRP'],
            'imaging': ['pencil-in-cup', 'new bone formation'],
            'min_match': 2,
            'required_categories': [],
            'required_markers': ['psoriasis'],
            'rf_negative_boost': 0.1,
            'suggested_actions': [
                'Dermatology referral for skin assessment',
                'X-ray affected joints',
                'Consider biologic therapy if severe',
            ],
        },

        'ankylosing_spondylitis': {
            'display_name': 'Ankylosing Spondylitis',
            'symptoms': [
                'back pain', 'morning stiffness', 'sacroiliac pain',
                'reduced spinal mobility', 'chest pain', 'uveitis',
                'lower back pain', 'inflammatory back pain'
            ],
            'labs': ['HLA-B27', 'ESR', 'CRP'],
            'imaging': ['sacroiliitis', 'bamboo spine', 'syndesmophytes'],
            'min_match': 3,
            'required_categories': ['symptoms'],
            'confidence_boost_markers': ['HLA-B27'],
            'confidence_boost': 0.2,
            'suggested_actions': [
                'Check HLA-B27 status',
                'MRI sacroiliac joints',
                'Refer to rheumatology',
            ],
        },

        'gout': {
            'display_name': 'Gout',
            'symptoms': [
                'acute joint pain', 'red joint', 'swollen joint',
                'first MTP', 'podagra', 'tophi', 'big toe pain',
                'sudden joint pain'
            ],
            'labs': ['uric acid', 'hyperuricemia', 'urate crystals'],
            'min_match': 2,
            'required_categories': [],
            'confidence_boost_markers': ['urate crystals'],
            'confidence_boost': 0.25,
            'suggested_actions': [
                'Check serum uric acid level',
                'Consider joint aspiration for crystal analysis',
                'Initiate anti-inflammatory therapy',
            ],
        },

        'osteoarthritis': {
            'display_name': 'Osteoarthritis',
            'symptoms': [
                'joint pain', 'stiffness', 'crepitus', 'reduced ROM',
                'Heberden nodes', 'Bouchard nodes', 'knee pain',
                'hip pain', 'limited range of motion'
            ],
            'labs': [],
            'imaging': ['osteophytes', 'joint space narrowing', 'subchondral sclerosis'],
            'min_match': 2,
            'required_categories': ['symptoms'],
            'age_factor': True,
            'rf_negative_boost': 0.1,
            'suggested_actions': [
                'X-ray affected joints',
                'Physical therapy referral',
                'Weight management counseling',
            ],
        },

        'fibromyalgia': {
            'display_name': 'Fibromyalgia',
            'symptoms': [
                'widespread pain', 'fatigue', 'sleep disturbance',
                'cognitive dysfunction', 'tender points', 'headache',
                'chronic pain', 'diffuse pain', 'brain fog'
            ],
            'labs': [],
            'min_match': 3,
            'required_categories': ['symptoms'],
            'required_markers': ['widespread pain', 'chronic pain', 'diffuse pain'],
            'normal_labs_boost': 0.15,
            'suggested_actions': [
                'Rule out other rheumatic conditions',
                'Sleep study if indicated',
                'Multidisciplinary pain management',
            ],
        },

        'sjogren_syndrome': {
            'display_name': "Sjogren's Syndrome",
            'symptoms': [
                'dry eyes', 'dry mouth', 'fatigue', 'joint pain',
                'sicca symptoms', 'parotid swelling', 'xerostomia',
                'keratoconjunctivitis sicca'
            ],
            'labs': ['ANA', 'anti-SSA', 'anti-SSB', 'RF', 'anti-Ro', 'anti-La'],
            'min_match': 3,
            'required_categories': ['symptoms'],
            'required_markers': ['dry'],
            'suggested_actions': [
                'Schirmer test for dry eyes',
                'Check anti-SSA/SSB antibodies',
                'Ophthalmology referral',
            ],
        },

        'polymyalgia_rheumatica': {
            'display_name': 'Polymyalgia Rheumatica',
            'symptoms': [
                'shoulder pain', 'hip pain', 'morning stiffness',
                'bilateral symptoms', 'difficulty rising',
                'proximal muscle pain', 'neck stiffness'
            ],
            'labs': ['ESR', 'CRP'],
            'min_match': 3,
            'required_categories': ['symptoms', 'labs'],
            'age_factor': True,
            'suggested_actions': [
                'Check ESR and CRP (typically markedly elevated)',
                'Rule out giant cell arteritis',
                'Consider low-dose prednisone trial',
            ],
        },
    }

    # Relationship types for entity linking
    RELATIONSHIP_TYPES = {
        ('MEDICATION', 'DISEASE'): 'TREATS',
        ('MEDICATION', 'INFERRED_DIAGNOSIS'): 'TREATS',
        ('SYMPTOM', 'DISEASE'): 'SYMPTOM_OF',
        ('SYMPTOM', 'INFERRED_DIAGNOSIS'): 'SYMPTOM_OF',
        ('LAB_TEST', 'DISEASE'): 'INDICATES',
        ('LAB_TEST', 'INFERRED_DIAGNOSIS'): 'INDICATES',
        ('MEDICATION', 'SYMPTOM'): 'ALLEVIATES',
        ('LAB_TEST', 'SYMPTOM'): 'CORRELATES_WITH',
    }

    # Reference embeddings for common medical terms (lazy loaded)
    _reference_embeddings = None
    _model = None
    _tokenizer = None

    def __init__(self, model_path: Optional[str] = None, load_model: bool = True):
        """
        Initialize BioLinkBERT extractor.

        Args:
            model_path: Optional path to local model cache
            load_model: If False, only use rule-based inference (no model loading)
        """
        # Try to use local cached model first
        if model_path is None:
            local_path = self._get_local_model_path()
            self.model_path = local_path if local_path else self.MODEL_NAME
        else:
            self.model_path = model_path
        self._initialized = False
        self._skip_model = not load_model

    @staticmethod
    def _get_local_model_path() -> Optional[str]:
        """Check for locally cached model from model_downloader."""
        from pathlib import Path
        # Project root is 3 levels up: services -> backend -> root
        project_root = Path(__file__).parent.parent.parent
        local_model = project_root / 'data' / 'models' / 'biolinkbert'
        if local_model.exists() and (local_model / 'config.json').exists():
            return str(local_model)
        return None

    def _ensure_initialized(self) -> bool:
        """Lazy initialization of model and tokenizer."""
        if self._initialized:
            return True

        if self._skip_model:
            return False

        if not BIOLINKBERT_DEPS_AVAILABLE:
            return False

        try:
            if BioLinkBERTExtractor._tokenizer is None:
                BioLinkBERTExtractor._tokenizer = AutoTokenizer.from_pretrained(
                    self.model_path
                )
            if BioLinkBERTExtractor._model is None:
                BioLinkBERTExtractor._model = AutoModel.from_pretrained(
                    self.model_path
                )
                BioLinkBERTExtractor._model.eval()

            self._initialized = True
            return True
        except Exception as e:
            print(f"Failed to load BioLinkBERT model: {e}")
            return False

    def _get_embedding(self, text: str) -> Optional[Any]:
        """Get BioLinkBERT embedding for text."""
        if not NUMPY_AVAILABLE:
            return None

        if not self._ensure_initialized():
            return None

        try:
            inputs = self._tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=512,
                padding=True
            )

            with torch.no_grad():
                outputs = self._model(**inputs)

            # Use [CLS] token embedding (first token)
            embedding = outputs.last_hidden_state[:, 0, :].numpy()
            return embedding.flatten()
        except Exception:
            return None

    def _calculate_similarity(self, emb1: Any, emb2: Any) -> float:
        """Calculate cosine similarity between embeddings."""
        if not NUMPY_AVAILABLE or emb1 is None or emb2 is None:
            return 0.0

        norm1 = np.linalg.norm(emb1)
        norm2 = np.linalg.norm(emb2)
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return float(np.dot(emb1, emb2) / (norm1 * norm2))

    def _find_entity_mentions(self, text: str, entities_from_other_extractors: List[Entity]) -> List[Entity]:
        """
        Find entity mentions in text using semantic similarity.

        Uses entities already found by other extractors (A, B, C) as anchors,
        then uses BioLinkBERT to validate and potentially find additional entities.
        """
        entities = []
        text_lower = text.lower()

        # Get embedding for full text
        text_embedding = self._get_embedding(text)
        if text_embedding is None:
            return entities

        # Validate entities from other extractors using BioLinkBERT similarity
        for entity in entities_from_other_extractors:
            entity_embedding = self._get_embedding(entity.get('text', ''))
            if entity_embedding is not None:
                similarity = self._calculate_similarity(text_embedding, entity_embedding)
                # Add BioLinkBERT confidence score
                entity_copy = dict(entity)
                entity_copy['biolinkbert_similarity'] = similarity
                entity_copy['source'] = 'biolinkbert_validated'
                entities.append(entity_copy)

        return entities

    def _match_inference_rules(
        self,
        entities: List[Entity],
        text: str
    ) -> List[Dict[str, Any]]:
        """
        Match entities against inference rules to infer diagnoses.

        Args:
            entities: List of extracted entities
            text: Original text (for context)

        Returns:
            List of inferred diagnoses
        """
        inferred = []
        text_lower = text.lower()

        # Collect entity texts by type
        symptoms_found = set()
        labs_found = set()
        imaging_found = set()

        for entity in entities:
            entity_text = entity.get('text', '').lower()
            entity_type = entity.get('type', '')

            if entity_type in ['SYMPTOM', 'CONDITION']:
                symptoms_found.add(entity_text)
            elif entity_type in ['LAB_TEST', 'LAB_RESULT']:
                labs_found.add(entity_text)

        # Also scan text directly for rule markers
        for rule_name, rule in self.INFERENCE_RULES.items():
            matches = []
            matched_symptoms = []
            matched_labs = []
            matched_imaging = []

            # Check symptoms
            for symptom in rule.get('symptoms', []):
                symptom_lower = symptom.lower()
                if symptom_lower in text_lower or any(
                    symptom_lower in s for s in symptoms_found
                ):
                    matches.append(('symptom', symptom))
                    matched_symptoms.append(symptom)

            # Check labs
            for lab in rule.get('labs', []):
                lab_lower = lab.lower()
                if lab_lower in text_lower or any(
                    lab_lower in l for l in labs_found
                ):
                    matches.append(('lab', lab))
                    matched_labs.append(lab)

            # Check imaging
            for imaging in rule.get('imaging', []):
                if imaging.lower() in text_lower:
                    matches.append(('imaging', imaging))
                    matched_imaging.append(imaging)

            # Check if minimum matches met
            if len(matches) >= rule.get('min_match', 3):
                # Check required categories
                required_cats = rule.get('required_categories', [])
                cats_met = True
                for cat in required_cats:
                    if cat == 'symptoms' and not matched_symptoms:
                        cats_met = False
                    elif cat == 'labs' and not matched_labs:
                        cats_met = False

                # Check required markers
                required_markers = rule.get('required_markers', [])
                markers_met = True
                if required_markers:
                    markers_met = any(
                        marker.lower() in text_lower
                        for marker in required_markers
                    )

                if cats_met and markers_met:
                    # Calculate confidence
                    base_confidence = 0.60 + (len(matches) * 0.05)
                    base_confidence = min(base_confidence, 0.95)

                    # Apply confidence boosts
                    boost_markers = rule.get('confidence_boost_markers', [])
                    for marker in boost_markers:
                        if marker.lower() in text_lower:
                            base_confidence += rule.get('confidence_boost', 0.1)
                            break

                    base_confidence = min(base_confidence, 0.98)

                    # Build linked_from list
                    linked_from = []
                    total_contributors = len(matches)
                    contribution = 1.0 / total_contributors if total_contributors > 0 else 0

                    for match_type, match_text in matches:
                        linked_from.append({
                            'text': match_text,
                            'type': match_type.upper(),
                            'contribution': round(contribution, 3),
                        })

                    inferred.append({
                        'text': rule['display_name'],
                        'type': 'INFERRED_DIAGNOSIS',
                        'start': None,
                        'end': None,
                        'confidence': round(base_confidence, 3),
                        'source': 'biolinkbert_inference',
                        'inference_type': 'symptom_cluster',
                        'linked_from': linked_from,
                        'matched_rule': rule_name,
                        'rule_match_count': len(matches),
                        'rule_min_required': rule.get('min_match', 3),
                        'suggested_actions': rule.get('suggested_actions', []),
                    })

        return inferred

    def _create_entity_links(
        self,
        entities: List[Entity],
        inferred: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Create relationship links between entities.

        Args:
            entities: Extracted entities
            inferred: Inferred diagnoses

        Returns:
            List of entity links
        """
        links = []
        all_entities = entities + inferred

        for i, e1 in enumerate(all_entities):
            for e2 in all_entities[i + 1:]:
                type1 = e1.get('type', '')
                type2 = e2.get('type', '')

                # Check for known relationship types
                relationship = self.RELATIONSHIP_TYPES.get((type1, type2))
                if not relationship:
                    relationship = self.RELATIONSHIP_TYPES.get((type2, type1))
                    if relationship:
                        # Swap order for correct directionality
                        e1, e2 = e2, e1

                if relationship:
                    # Calculate link confidence based on entity confidences
                    conf1 = e1.get('confidence', 0.5)
                    conf2 = e2.get('confidence', 0.5)
                    link_confidence = (conf1 + conf2) / 2

                    links.append({
                        'source': e1.get('text', ''),
                        'target': e2.get('text', ''),
                        'relationship': relationship,
                        'confidence': round(link_confidence, 3),
                    })

        return links

    def extract(self, text: str, entities_from_others: Optional[List[Entity]] = None) -> ExtractionResult:
        """
        Extract entities and infer diagnoses from clinical text.

        Args:
            text: Clinical note text
            entities_from_others: Entities already found by other extractors (A, B, C)

        Returns:
            ExtractionResult with entities, inferred diagnoses, and links
        """
        start_time = time.time()

        entities = entities_from_others or []
        inferred = []
        links = []

        # Try to initialize model
        if self._ensure_initialized():
            # Validate entities with BioLinkBERT
            if entities:
                entities = self._find_entity_mentions(text, entities)

            # Apply inference rules
            inferred = self._match_inference_rules(entities, text)

            # Create entity links
            if entities or inferred:
                links = self._create_entity_links(entities, inferred)
        else:
            # Fallback: just apply rule-based inference without model
            inferred = self._match_inference_rules(entities, text)

        processing_time = (time.time() - start_time) * 1000

        return {
            'entities': entities,
            'inferred': inferred,
            'links': links,
            'version': self.VERSION,
            'model_name': self.get_model_name(),
            'processing_time_ms': round(processing_time, 2),
            'model_loaded': self._initialized,
        }

    def get_version(self) -> str:
        """Return version identifier."""
        return self.VERSION

    def get_model_name(self) -> str:
        """Return model name."""
        return 'biolinkbert-contextual-inference'


def is_biolinkbert_available() -> bool:
    """Check if BioLinkBERT dependencies are available."""
    return BIOLINKBERT_DEPS_AVAILABLE
