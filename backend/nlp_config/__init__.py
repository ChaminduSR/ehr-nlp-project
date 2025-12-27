"""
NLP Configuration Package

Exports:
- get_extractor: Factory function for creating entity extractors
- NLPConfig: Configuration class
- extract_entities: Convenience function for one-line extraction
"""

from .nlp_config import get_extractor, NLPConfig, extract_entities, config

__all__ = ['get_extractor', 'NLPConfig', 'extract_entities', 'config']
