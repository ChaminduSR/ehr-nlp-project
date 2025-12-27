"""
Services Package

NLP Entity Extraction Services:
- BaseEntityExtractor: Abstract base class for all extractors
- RegexEntityExtractor: Version A - regex-based extraction
- MTLEntityExtractor: Version B - transformer-based extraction (future)

Exports:
- BaseEntityExtractor
- RegexEntityExtractor
"""

from .base_extractor import BaseEntityExtractor, Entity, ExtractionResult
from .regex_entity_extractor import RegexEntityExtractor

__all__ = [
    'BaseEntityExtractor',
    'Entity',
    'ExtractionResult',
    'RegexEntityExtractor'
]
