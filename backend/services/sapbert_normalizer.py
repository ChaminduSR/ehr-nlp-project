"""
SapBERT Entity Normalizer for Version C

UMLS entity normalization using SapBERT embeddings.
Maps extracted entities to standardized UMLS concepts (CUI codes).

Model: cambridgeltl/SapBERT-from-PubMedBERT-fulltext
- Trained on UMLS 2020AA
- 110M parameters
- Acc@1 = 0.81 on entity linking benchmarks

Usage:
    normalizer = SapBERTNormalizer()
    normalized_entities = normalizer.normalize(entities)

Each entity will have added fields:
    - umls_cui: UMLS Concept Unique Identifier
    - umls_name: Preferred UMLS concept name
    - umls_confidence: Similarity score (0.0-1.0)
"""

import os
import logging
import numpy as np
from pathlib import Path
from typing import List, Dict, Optional, Tuple

logger = logging.getLogger(__name__)


class SapBERTNormalizer:
    """
    UMLS entity normalization using SapBERT embeddings.

    Maps medical entity text to standardized UMLS concepts by:
    1. Computing SapBERT embedding for entity text
    2. Finding nearest UMLS concept via cosine similarity
    3. Returning CUI code and preferred name

    Requires:
    - SapBERT model: cambridgeltl/SapBERT-from-PubMedBERT-fulltext
    - Pre-computed UMLS embeddings (optional, for faster lookup)
    """

    MODEL_NAME = 'sapbert'
    MODEL_HF_NAME = 'cambridgeltl/SapBERT-from-PubMedBERT-fulltext'
    MODEL_FOLDER = 'sapbert'
    SIMILARITY_THRESHOLD = 0.7  # Minimum similarity for UMLS match
    BATCH_SIZE = 32  # Batch size for embedding computation

    # Common rheumatology UMLS mappings (fallback/cache)
    # Format: {lowercase_term: (cui, preferred_name)}
    COMMON_UMLS_MAPPINGS = {
        # Medications
        'methotrexate': ('C0025677', 'Methotrexate'),
        'mtx': ('C0025677', 'Methotrexate'),
        'humira': ('C1171255', 'Adalimumab'),
        'adalimumab': ('C1171255', 'Adalimumab'),
        'enbrel': ('C0717758', 'Etanercept'),
        'etanercept': ('C0717758', 'Etanercept'),
        'remicade': ('C0666743', 'Infliximab'),
        'infliximab': ('C0666743', 'Infliximab'),
        'prednisone': ('C0032952', 'Prednisone'),
        'hydroxychloroquine': ('C0020336', 'Hydroxychloroquine'),
        'plaquenil': ('C0020336', 'Hydroxychloroquine'),
        'sulfasalazine': ('C0036078', 'Sulfasalazine'),
        'leflunomide': ('C0064881', 'Leflunomide'),
        'arava': ('C0064881', 'Leflunomide'),
        'rituximab': ('C0393022', 'Rituximab'),
        'rituxan': ('C0393022', 'Rituximab'),
        'tocilizumab': ('C1609165', 'Tocilizumab'),
        'actemra': ('C1609165', 'Tocilizumab'),
        'tofacitinib': ('C2930175', 'Tofacitinib'),
        'xeljanz': ('C2930175', 'Tofacitinib'),
        'baricitinib': ('C3252270', 'Baricitinib'),
        'olumiant': ('C3252270', 'Baricitinib'),
        'ibuprofen': ('C0020740', 'Ibuprofen'),
        'naproxen': ('C0027396', 'Naproxen'),
        'celecoxib': ('C0538927', 'Celecoxib'),
        'celebrex': ('C0538927', 'Celecoxib'),
        'meloxicam': ('C0071097', 'Meloxicam'),
        'mobic': ('C0071097', 'Meloxicam'),

        # Diseases/Conditions
        'rheumatoid arthritis': ('C0003873', 'Rheumatoid Arthritis'),
        'ra': ('C0003873', 'Rheumatoid Arthritis'),
        'lupus': ('C0024141', 'Systemic Lupus Erythematosus'),
        'sle': ('C0024141', 'Systemic Lupus Erythematosus'),
        'systemic lupus erythematosus': ('C0024141', 'Systemic Lupus Erythematosus'),
        'fibromyalgia': ('C0016053', 'Fibromyalgia'),
        'osteoarthritis': ('C0029408', 'Osteoarthritis'),
        'oa': ('C0029408', 'Osteoarthritis'),
        'gout': ('C0018099', 'Gout'),
        'psoriatic arthritis': ('C0003872', 'Psoriatic Arthritis'),
        'psa': ('C0003872', 'Psoriatic Arthritis'),
        'ankylosing spondylitis': ('C0038013', 'Ankylosing Spondylitis'),
        'as': ('C0038013', 'Ankylosing Spondylitis'),
        'sjogren syndrome': ('C0037231', "Sjogren's Syndrome"),
        'sjogrens': ('C0037231', "Sjogren's Syndrome"),
        'vasculitis': ('C0042384', 'Vasculitis'),
        'polymyalgia rheumatica': ('C0032533', 'Polymyalgia Rheumatica'),
        'pmr': ('C0032533', 'Polymyalgia Rheumatica'),

        # Symptoms
        'joint pain': ('C0003862', 'Arthralgia'),
        'arthralgia': ('C0003862', 'Arthralgia'),
        'joint swelling': ('C0152031', 'Joint Swelling'),
        'morning stiffness': ('C0457109', 'Morning Stiffness'),
        'fatigue': ('C0015672', 'Fatigue'),
        'fever': ('C0015967', 'Fever'),
        'rash': ('C0015230', 'Exanthema'),
        'pain': ('C0030193', 'Pain'),
        'inflammation': ('C0021368', 'Inflammation'),
        'swelling': ('C0013604', 'Edema'),
        'stiffness': ('C0162298', 'Stiffness'),
        'tenderness': ('C0234233', 'Tenderness'),
        'weakness': ('C0004093', 'Asthenia'),
        'myalgia': ('C0231528', 'Myalgia'),
        'muscle pain': ('C0231528', 'Myalgia'),

        # Lab Tests
        'esr': ('C0853056', 'Erythrocyte Sedimentation Rate'),
        'sed rate': ('C0853056', 'Erythrocyte Sedimentation Rate'),
        'crp': ('C0006560', 'C-Reactive Protein'),
        'c-reactive protein': ('C0006560', 'C-Reactive Protein'),
        'ana': ('C0003243', 'Antinuclear Antibodies'),
        'antinuclear antibody': ('C0003243', 'Antinuclear Antibodies'),
        'rf': ('C0035450', 'Rheumatoid Factor'),
        'rheumatoid factor': ('C0035450', 'Rheumatoid Factor'),
        'anti-ccp': ('C1318542', 'Anti-Cyclic Citrullinated Peptide Antibodies'),
        'ccp': ('C1318542', 'Anti-Cyclic Citrullinated Peptide Antibodies'),
        'hla-b27': ('C0019740', 'HLA-B27 Antigen'),
        'uric acid': ('C0041980', 'Uric Acid'),
        'complement': ('C0009498', 'Complement'),
        'c3': ('C0009512', 'Complement C3'),
        'c4': ('C0009519', 'Complement C4'),
    }

    def __init__(self, model_path: str = 'data/models', use_model: bool = True):
        """
        Initialize SapBERT normalizer.

        Args:
            model_path: Directory containing cached models
            use_model: If True, load SapBERT model for dynamic normalization.
                      If False, only use cached UMLS mappings (faster, less accurate).

        Note:
            If SapBERT model is not available, falls back to cached mappings only.
        """
        logger.info("Initializing SapBERTNormalizer")

        # Get project root
        project_root = Path(__file__).parent.parent.parent

        # Build model path
        if not Path(model_path).is_absolute():
            self.model_path = str(project_root / model_path)
        else:
            self.model_path = model_path

        self.model = None
        self.tokenizer = None
        self.use_model = use_model
        self.umls_embeddings = None
        self.umls_concepts = None

        if use_model:
            self._try_load_model()

        logger.info(f"SapBERTNormalizer initialized (model_loaded={self.model is not None})")

    def _try_load_model(self):
        """Try to load SapBERT model and tokenizer."""
        try:
            from transformers import AutoModel, AutoTokenizer
            import torch

            cache_path = os.path.join(self.model_path, self.MODEL_FOLDER)

            if os.path.exists(cache_path):
                logger.info(f"Loading SapBERT from cache: {cache_path}")
                self.model = AutoModel.from_pretrained(cache_path)
                self.tokenizer = AutoTokenizer.from_pretrained(cache_path)
            else:
                logger.info(f"Downloading SapBERT from HuggingFace: {self.MODEL_HF_NAME}")
                self.model = AutoModel.from_pretrained(self.MODEL_HF_NAME)
                self.tokenizer = AutoTokenizer.from_pretrained(self.MODEL_HF_NAME)

                # Cache for future use
                Path(cache_path).mkdir(parents=True, exist_ok=True)
                self.model.save_pretrained(cache_path)
                self.tokenizer.save_pretrained(cache_path)
                logger.info(f"SapBERT cached at: {cache_path}")

            # Set to evaluation mode
            self.model.eval()

            # Try to use GPU if available
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
            self.model.to(self.device)

            logger.info(f"SapBERT loaded successfully (device={self.device})")

        except ImportError as e:
            logger.warning(f"transformers not installed, using cached mappings only: {e}")
            self.model = None
        except Exception as e:
            logger.warning(f"Failed to load SapBERT model, using cached mappings only: {e}")
            self.model = None

    def normalize(self, entities: List[Dict]) -> List[Dict]:
        """
        Normalize entities by adding UMLS mappings.

        Args:
            entities: List of entity dictionaries from extractor

        Returns:
            Same entities with added UMLS fields:
            - umls_cui: UMLS Concept Unique Identifier
            - umls_name: Preferred UMLS concept name
            - umls_confidence: Similarity score (0.0-1.0)

        Example:
            >>> normalizer = SapBERTNormalizer()
            >>> entities = [{'text': 'methotrexate', 'type': 'MEDICATION', ...}]
            >>> normalized = normalizer.normalize(entities)
            >>> normalized[0]['umls_cui']
            'C0025677'
        """
        if not entities:
            return entities

        normalized = []
        for entity in entities:
            normalized_entity = entity.copy()

            # Try to find UMLS mapping
            cui, name, confidence = self._lookup_umls(entity['text'], entity.get('type'))

            if cui:
                normalized_entity['umls_cui'] = cui
                normalized_entity['umls_name'] = name
                normalized_entity['umls_confidence'] = confidence
            else:
                normalized_entity['umls_cui'] = None
                normalized_entity['umls_name'] = None
                normalized_entity['umls_confidence'] = 0.0

            normalized.append(normalized_entity)

        return normalized

    def _lookup_umls(
        self,
        text: str,
        entity_type: Optional[str] = None
    ) -> Tuple[Optional[str], Optional[str], float]:
        """
        Look up UMLS concept for entity text.

        Args:
            text: Entity text to normalize
            entity_type: Optional entity type for disambiguation

        Returns:
            Tuple of (cui, preferred_name, confidence) or (None, None, 0.0)
        """
        # Normalize text for lookup
        text_lower = text.lower().strip()

        # First try cached mappings (fast)
        if text_lower in self.COMMON_UMLS_MAPPINGS:
            cui, name = self.COMMON_UMLS_MAPPINGS[text_lower]
            return cui, name, 1.0  # High confidence for exact match

        # If model available, use SapBERT for dynamic lookup
        if self.model is not None:
            return self._sapbert_lookup(text)

        # No match found
        return None, None, 0.0

    def _sapbert_lookup(self, text: str) -> Tuple[Optional[str], Optional[str], float]:
        """
        Use SapBERT model for UMLS concept lookup.

        This computes the embedding for the input text and finds
        the nearest UMLS concept. Requires pre-computed UMLS embeddings.

        Args:
            text: Entity text to normalize

        Returns:
            Tuple of (cui, preferred_name, confidence)
        """
        try:
            import torch

            # Tokenize input
            inputs = self.tokenizer(
                text,
                return_tensors='pt',
                padding=True,
                truncation=True,
                max_length=64
            ).to(self.device)

            # Compute embedding
            with torch.no_grad():
                outputs = self.model(**inputs)
                # Use [CLS] token embedding
                embedding = outputs.last_hidden_state[:, 0, :].cpu().numpy()

            # If we have pre-computed UMLS embeddings, find nearest
            if self.umls_embeddings is not None:
                return self._find_nearest_concept(embedding)

            # Without UMLS embeddings, we can't do dynamic lookup
            # Fall back to semantic similarity with cached concepts
            return self._semantic_fallback(text, embedding)

        except Exception as e:
            logger.warning(f"SapBERT lookup failed for '{text}': {e}")
            return None, None, 0.0

    def _semantic_fallback(
        self,
        text: str,
        embedding: np.ndarray
    ) -> Tuple[Optional[str], Optional[str], float]:
        """
        Semantic similarity fallback when UMLS embeddings not available.

        Computes embeddings for cached concepts and finds nearest match.
        """
        try:
            import torch

            best_match = None
            best_score = 0.0

            # Compute embeddings for cached concepts and find nearest
            for term, (cui, name) in self.COMMON_UMLS_MAPPINGS.items():
                # Tokenize cached term
                inputs = self.tokenizer(
                    term,
                    return_tensors='pt',
                    padding=True,
                    truncation=True,
                    max_length=64
                ).to(self.device)

                with torch.no_grad():
                    outputs = self.model(**inputs)
                    term_embedding = outputs.last_hidden_state[:, 0, :].cpu().numpy()

                # Compute cosine similarity
                similarity = self._cosine_similarity(embedding, term_embedding)

                if similarity > best_score:
                    best_score = similarity
                    best_match = (cui, name)

            if best_score >= self.SIMILARITY_THRESHOLD and best_match:
                return best_match[0], best_match[1], float(best_score)

            return None, None, 0.0

        except Exception as e:
            logger.warning(f"Semantic fallback failed: {e}")
            return None, None, 0.0

    def _find_nearest_concept(
        self,
        embedding: np.ndarray
    ) -> Tuple[Optional[str], Optional[str], float]:
        """
        Find nearest UMLS concept from pre-computed embeddings.

        Args:
            embedding: SapBERT embedding for input text

        Returns:
            Tuple of (cui, preferred_name, similarity_score)
        """
        if self.umls_embeddings is None or self.umls_concepts is None:
            return None, None, 0.0

        # Compute cosine similarities
        similarities = self._cosine_similarity(
            embedding,
            self.umls_embeddings
        )

        # Find best match
        best_idx = np.argmax(similarities)
        best_score = similarities[best_idx]

        if best_score >= self.SIMILARITY_THRESHOLD:
            cui, name = self.umls_concepts[best_idx]
            return cui, name, float(best_score)

        return None, None, 0.0

    @staticmethod
    def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> np.ndarray:
        """Compute cosine similarity between vectors."""
        a_norm = a / (np.linalg.norm(a, axis=-1, keepdims=True) + 1e-8)
        b_norm = b / (np.linalg.norm(b, axis=-1, keepdims=True) + 1e-8)
        return np.sum(a_norm * b_norm, axis=-1)

    def load_umls_embeddings(self, embeddings_path: str):
        """
        Load pre-computed UMLS concept embeddings.

        Args:
            embeddings_path: Path to directory containing:
                - embeddings.npy: Numpy array of concept embeddings
                - concepts.txt: Tab-separated CUI and preferred name

        Note:
            Pre-computing UMLS embeddings is recommended for production.
            This significantly speeds up entity normalization.
        """
        try:
            embeddings_file = os.path.join(embeddings_path, 'embeddings.npy')
            concepts_file = os.path.join(embeddings_path, 'concepts.txt')

            if os.path.exists(embeddings_file) and os.path.exists(concepts_file):
                self.umls_embeddings = np.load(embeddings_file)

                self.umls_concepts = []
                with open(concepts_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        parts = line.strip().split('\t')
                        if len(parts) >= 2:
                            self.umls_concepts.append((parts[0], parts[1]))

                logger.info(f"Loaded {len(self.umls_concepts)} UMLS concept embeddings")
            else:
                logger.warning(f"UMLS embeddings not found at: {embeddings_path}")

        except Exception as e:
            logger.error(f"Failed to load UMLS embeddings: {e}")

    def is_available(self) -> bool:
        """Check if normalizer is ready to use."""
        return self.model is not None or len(self.COMMON_UMLS_MAPPINGS) > 0
