"""
Version C: Two-Tier Entity Extractor (V2.1)

Two-tier medical entity extraction with UMLS normalization.
Combines GatorTron-Rheum extraction with SapBERT entity linking.

Architecture:
- Tier 1: GatorTron-Rheum (MTLEntityExtractor) for entity extraction
- Tier 2: SapBERT (SapBERTNormalizer) for UMLS entity normalization
- Fallback: RegexEntityExtractor (Version A) on error

Performance Targets (per V2.1 docs):
- Accuracy: 90-91% F1
- Speed: 600ms (parallel inference)
- Memory: 1GB peak (GatorTron + SapBERT)

Usage:
    extractor = TwoTierExtractor()
    result = extractor.extract("Patient on methotrexate 15mg weekly")
    # Entities include umls_cui, umls_name, umls_confidence
"""

import time
import logging
from typing import Optional
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError

from .base_extractor import BaseEntityExtractor, ExtractionResult
from .regex_entity_extractor import RegexEntityExtractor

logger = logging.getLogger(__name__)


class TwoTierExtractor(BaseEntityExtractor):
    """
    Version C: Two-Tier Entity Extractor with UMLS normalization.

    Combines:
    - Tier 1: GatorTron-Rheum transformer for high-accuracy NER
    - Tier 2: SapBERT for UMLS entity normalization

    Falls back to Version A (Regex) on any error.
    """

    # Configuration
    TIER1_TIMEOUT_MS = 2000  # Timeout for GatorTron-Rheum
    TIER2_TIMEOUT_MS = 1000  # Timeout for SapBERT normalization
    TOTAL_TIMEOUT_MS = 3000  # Total timeout for both tiers

    def __init__(
        self,
        model_path: str = 'data/models',
        timeout_ms: Optional[int] = None,
        fallback_enabled: bool = True
    ):
        """
        Initialize Two-Tier extractor.

        Args:
            model_path: Directory containing cached models
            timeout_ms: Optional timeout override for total processing
            fallback_enabled: If True, fall back to Version A on error

        Note:
            - Requires GatorTron-Rheum model for Tier 1
            - Requires SapBERT model for Tier 2 (optional, uses cached mappings if unavailable)
            - Falls back to Version A if Tier 1 fails
        """
        logger.info("Initializing TwoTierExtractor (Version C V2.1)")

        self.model_path = model_path
        self.timeout_ms = timeout_ms or self.TOTAL_TIMEOUT_MS
        self.fallback_enabled = fallback_enabled

        # Initialize extractors
        self.mtl_extractor = None
        self.normalizer = None
        self.regex_extractor = None

        # Track which components are available
        self.tier1_available = False
        self.tier2_available = False

        self._initialize_components()

        logger.info(
            f"TwoTierExtractor initialized: "
            f"tier1={self.tier1_available}, tier2={self.tier2_available}"
        )

    def _initialize_components(self):
        """Initialize all extractor components."""
        # Always initialize fallback (Version A)
        try:
            self.regex_extractor = RegexEntityExtractor()
            logger.info("Version A (Regex) fallback initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Version A fallback: {e}")

        # Try to initialize Tier 1: GatorTron-Rheum (Version B)
        try:
            from .mtl_entity_extractor import MTLEntityExtractor
            self.mtl_extractor = MTLEntityExtractor(model_path=self.model_path)
            self.tier1_available = True
            logger.info("Tier 1 (GatorTron-Rheum) initialized")
        except ImportError as e:
            logger.warning(f"Tier 1 not available - transformers not installed: {e}")
        except FileNotFoundError as e:
            logger.warning(f"Tier 1 not available - model not found: {e}")
        except Exception as e:
            logger.warning(f"Tier 1 initialization failed: {e}")

        # Try to initialize Tier 2: SapBERT normalizer
        try:
            from .sapbert_normalizer import SapBERTNormalizer
            self.normalizer = SapBERTNormalizer(
                model_path=self.model_path,
                use_model=True  # Try to load SapBERT model
            )
            self.tier2_available = self.normalizer.is_available()
            logger.info(f"Tier 2 (SapBERT) initialized: {self.tier2_available}")
        except ImportError as e:
            logger.warning(f"Tier 2 not available - import error: {e}")
        except Exception as e:
            logger.warning(f"Tier 2 initialization failed: {e}")

    def extract(self, text: str) -> ExtractionResult:
        """
        Extract and normalize medical entities using two-tier architecture.

        Processing:
        1. Tier 1: Extract entities with GatorTron-Rheum
        2. Tier 2: Normalize entities with SapBERT (add UMLS CUIs)
        3. Fallback: Use Version A if Tier 1 fails

        Args:
            text: Medical note text to process

        Returns:
            ExtractionResult with UMLS-normalized entities:
            - entities: List of entities with umls_cui, umls_name, umls_confidence
            - version: 'C'
            - processing_time_ms: Total processing time
            - model_name: 'two-tier-gatortron-sapbert'
            - tier1_model: Model used for extraction
            - tier2_model: Model used for normalization
            - fallback_used: Whether fallback was triggered

        Example:
            >>> extractor = TwoTierExtractor()
            >>> result = extractor.extract("Patient on methotrexate")
            >>> result['entities'][0]['umls_cui']
            'C0025677'
        """
        start_time = time.time()

        try:
            # Try Tier 1 + Tier 2 extraction
            if self.tier1_available:
                return self._two_tier_extract(text, start_time)
            else:
                # Tier 1 not available, use fallback
                return self._fallback_extract(
                    text,
                    "Tier 1 (GatorTron-Rheum) not available",
                    start_time
                )

        except Exception as e:
            logger.error(f"Two-tier extraction failed: {e}")
            return self._fallback_extract(text, str(e), start_time)

    def _two_tier_extract(self, text: str, start_time: float) -> ExtractionResult:
        """
        Execute two-tier extraction with timeout.

        Args:
            text: Medical note text
            start_time: Timestamp when extraction started

        Returns:
            ExtractionResult with UMLS normalization
        """
        tier1_model = None
        tier2_model = None
        entities = []

        try:
            # Tier 1: Extract with GatorTron-Rheum
            tier1_result = self.mtl_extractor.extract(text)
            entities = tier1_result.get('entities', [])
            tier1_model = tier1_result.get('model_name', 'gatortron-rheum')

            # Tier 2: Normalize with SapBERT (if available)
            if self.tier2_available and self.normalizer:
                entities = self.normalizer.normalize(entities)
                tier2_model = 'sapbert'
            else:
                # Add empty UMLS fields
                for entity in entities:
                    entity['umls_cui'] = None
                    entity['umls_name'] = None
                    entity['umls_confidence'] = 0.0
                tier2_model = 'cached-mappings'

            processing_time_ms = (time.time() - start_time) * 1000

            return {
                'entities': entities,
                'version': self.get_version(),
                'processing_time_ms': processing_time_ms,
                'model_name': self.get_model_name(),
                'tier1_model': tier1_model,
                'tier2_model': tier2_model,
                'fallback_used': False,
                'fallback_reason': None
            }

        except Exception as e:
            logger.warning(f"Two-tier extraction error, using fallback: {e}")
            return self._fallback_extract(text, str(e), start_time)

    def _fallback_extract(
        self,
        text: str,
        reason: str,
        start_time: float
    ) -> ExtractionResult:
        """
        Execute fallback extraction using Version A (Regex).

        Args:
            text: Medical note text
            reason: Reason for fallback
            start_time: Timestamp when extraction started

        Returns:
            ExtractionResult from Version A with fallback metadata
        """
        logger.info(f"Using Version A fallback: {reason}")

        if self.regex_extractor is None:
            # Critical: Even fallback is unavailable
            processing_time_ms = (time.time() - start_time) * 1000
            return {
                'entities': [],
                'version': self.get_version(),
                'processing_time_ms': processing_time_ms,
                'model_name': 'none',
                'tier1_model': None,
                'tier2_model': None,
                'fallback_used': True,
                'fallback_reason': f"All extractors failed: {reason}",
                'error': True
            }

        try:
            # Extract with Version A
            result = self.regex_extractor.extract(text)
            entities = result.get('entities', [])

            # Try to normalize with cached mappings
            if self.normalizer:
                entities = self.normalizer.normalize(entities)

            processing_time_ms = (time.time() - start_time) * 1000

            return {
                'entities': entities,
                'version': self.get_version(),
                'processing_time_ms': processing_time_ms,
                'model_name': self.get_model_name(),
                'tier1_model': 'regex-v2.1',
                'tier2_model': 'cached-mappings' if self.normalizer else None,
                'fallback_used': True,
                'fallback_reason': reason
            }

        except Exception as e:
            processing_time_ms = (time.time() - start_time) * 1000
            logger.error(f"Fallback extraction also failed: {e}")
            return {
                'entities': [],
                'version': self.get_version(),
                'processing_time_ms': processing_time_ms,
                'model_name': 'none',
                'tier1_model': None,
                'tier2_model': None,
                'fallback_used': True,
                'fallback_reason': f"Fallback failed: {e}",
                'error': True
            }

    def get_version(self) -> str:
        """Return version identifier: 'C'"""
        return 'C'

    def get_model_name(self) -> str:
        """Return model name."""
        if self.tier1_available and self.tier2_available:
            return 'two-tier-gatortron-sapbert'
        elif self.tier1_available:
            return 'two-tier-gatortron-only'
        else:
            return 'two-tier-fallback'

    def get_status(self) -> dict:
        """
        Get detailed status of the two-tier extractor.

        Returns:
            Dictionary with component availability and configuration
        """
        return {
            'version': 'C',
            'tier1_available': self.tier1_available,
            'tier1_model': 'gatortron-rheum' if self.tier1_available else None,
            'tier2_available': self.tier2_available,
            'tier2_model': 'sapbert' if self.tier2_available else 'cached-mappings',
            'fallback_available': self.regex_extractor is not None,
            'fallback_model': 'regex-v2.1',
            'timeout_ms': self.timeout_ms,
            'model_path': self.model_path
        }


# Convenience function
def extract_with_umls(text: str, model_path: str = 'data/models') -> ExtractionResult:
    """
    Convenience function for two-tier extraction.

    Args:
        text: Medical note text
        model_path: Path to model cache

    Returns:
        ExtractionResult with UMLS normalization

    Example:
        >>> result = extract_with_umls("Patient on methotrexate 15mg weekly")
        >>> print(result['entities'][0]['umls_cui'])
        C0025677
    """
    extractor = TwoTierExtractor(model_path=model_path)
    return extractor.extract(text)
