"""
Base Entity Extractor Interface

This module defines the abstract base class for all entity extractors in the NLP pipeline.
All extractor versions (A, B, C, D) must implement this interface.

Version History:
- Version A: Regex-based extraction
- Version B: DistilBERT/BioClinicalBERT transformer model
- Version C: Dual model with fallback chain (future)
- Version D: Ensemble voting system (future)
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, TypedDict


class Entity(TypedDict, total=False):
    """Type definition for extracted entity"""
    text: str
    type: str
    start: int
    end: int
    confidence: float
    version: str
    is_negated: bool
    is_uncertain: bool
    is_historical: bool
    section: str


class ExtractionResult(TypedDict):
    """Type definition for extraction result"""
    entities: List[Entity]
    version: str
    processing_time_ms: float
    model_name: str


class BaseEntityExtractor(ABC):
    """
    Abstract base class for all entity extractors.

    All extractors must implement:
    - extract(): Main extraction method
    - get_version(): Return version identifier
    - get_model_name(): Return model/method name
    """

    @abstractmethod
    def extract(self, text: str) -> ExtractionResult:
        """
        Extract medical entities from text.

        Args:
            text: Medical note text to process

        Returns:
            ExtractionResult containing:
                - entities: List of extracted entities
                - version: Extractor version ('A', 'B', 'C', or 'D')
                - processing_time_ms: Time taken in milliseconds
                - model_name: Name of model/method used

        Raises:
            NotImplementedError: If not implemented in subclass
        """
        raise NotImplementedError("Subclasses must implement extract()")

    @abstractmethod
    def get_version(self) -> str:
        """
        Get version identifier for this extractor.

        Returns:
            Version string: 'A', 'B', 'C', or 'D'
        """
        raise NotImplementedError("Subclasses must implement get_version()")

    @abstractmethod
    def get_model_name(self) -> str:
        """
        Get name of the model or method used.

        Returns:
            Model/method name (e.g., 'regex', 'distilbert', 'bio-clinical-bert')
        """
        raise NotImplementedError("Subclasses must implement get_model_name()")

    def _create_entity(
        self,
        text: str,
        entity_type: str,
        start: int,
        end: int,
        confidence: float,
        **kwargs
    ) -> Entity:
        """
        Helper method to create a standardized entity dict.

        Args:
            text: Entity text
            entity_type: Type of entity (e.g., 'MEDICATION', 'DOSAGE')
            start: Start position in original text
            end: End position in original text
            confidence: Confidence score (0.0 to 1.0)
            **kwargs: Additional optional fields (is_negated, section, etc.)

        Returns:
            Entity dict with standard structure
        """
        entity: Entity = {
            'text': text,
            'type': entity_type,
            'start': start,
            'end': end,
            'confidence': confidence,
            'version': self.get_version()
        }

        # Add optional fields if provided
        if 'is_negated' in kwargs:
            entity['is_negated'] = kwargs['is_negated']
        if 'is_uncertain' in kwargs:
            entity['is_uncertain'] = kwargs['is_uncertain']
        if 'is_historical' in kwargs:
            entity['is_historical'] = kwargs['is_historical']
        if 'section' in kwargs:
            entity['section'] = kwargs['section']

        return entity
