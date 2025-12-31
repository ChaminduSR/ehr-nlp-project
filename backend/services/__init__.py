"""
Services Package

NLP Entity Extraction Services:
- BaseEntityExtractor: Abstract base class for all extractors
- RegexEntityExtractor: Version A - regex-based extraction (V2.2)
- MTLEntityExtractor: Version B - GatorTron transformer-based extraction
- TwoTierExtractor: Version C - Two-Tier (GatorTron + SapBERT)
- BioLinkBERTExtractor: BioLinkBERT for contextual inference
- EnsembleExtractor: Version D - Weighted ensemble of all extractors
- SapBERTNormalizer: UMLS entity normalization
"""

# Always available
from .base_extractor import BaseEntityExtractor, Entity, ExtractionResult
from .regex_entity_extractor import RegexEntityExtractor

# Conditionally import Version B (requires transformers)
try:
    from .mtl_entity_extractor import MTLEntityExtractor
    MTL_AVAILABLE = True
except ImportError:
    MTLEntityExtractor = None
    MTL_AVAILABLE = False

# Conditionally import Version C (requires Version B + SapBERT)
try:
    from .two_tier_extractor import TwoTierExtractor
    TWO_TIER_AVAILABLE = True
except ImportError:
    TwoTierExtractor = None
    TWO_TIER_AVAILABLE = False

# Conditionally import SapBERT normalizer
try:
    from .sapbert_normalizer import SapBERTNormalizer
    SAPBERT_AVAILABLE = True
except ImportError:
    SapBERTNormalizer = None
    SAPBERT_AVAILABLE = False

# Conditionally import BioLinkBERT extractor
try:
    from .biolinkbert_extractor import BioLinkBERTExtractor, is_biolinkbert_available
    BIOLINKBERT_AVAILABLE = is_biolinkbert_available()
except ImportError:
    BioLinkBERTExtractor = None
    BIOLINKBERT_AVAILABLE = False

# Conditionally import Version D Ensemble extractor
try:
    from .ensemble_extractor import EnsembleExtractor, is_ensemble_available
    ENSEMBLE_AVAILABLE = is_ensemble_available()
except ImportError:
    EnsembleExtractor = None
    ENSEMBLE_AVAILABLE = False

__all__ = [
    # Base
    'BaseEntityExtractor',
    'Entity',
    'ExtractionResult',
    # Version A
    'RegexEntityExtractor',
    # Version B (conditional)
    'MTLEntityExtractor',
    'MTL_AVAILABLE',
    # Version C (conditional)
    'TwoTierExtractor',
    'TWO_TIER_AVAILABLE',
    # BioLinkBERT (conditional)
    'BioLinkBERTExtractor',
    'BIOLINKBERT_AVAILABLE',
    # Version D Ensemble (conditional)
    'EnsembleExtractor',
    'ENSEMBLE_AVAILABLE',
    # Normalizer (conditional)
    'SapBERTNormalizer',
    'SAPBERT_AVAILABLE',
]
