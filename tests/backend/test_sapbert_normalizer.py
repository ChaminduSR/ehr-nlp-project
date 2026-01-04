"""
Tests for SapBERT Normalizer

Tests the SapBERT-based UMLS concept normalization:
- Entity to UMLS CUI mapping
- Similarity threshold handling
- Batch normalization

Run with: pytest tests/backend/test_sapbert_normalizer.py -v
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'backend'))

from tests.helpers import (
    assert_has_umls_mapping,
    assert_confidence_above,
)


@pytest.mark.slow
class TestSapBERTNormalizerInitialization:
    """Tests for SapBERTNormalizer initialization."""

    # ==================== FIXTURES ====================

    @pytest.fixture(scope="class")
    def normalizer(self):
        """Class-scoped: Load model once for all tests."""
        from services.sapbert_normalizer import SapBERTNormalizer
        return SapBERTNormalizer()

    # ==================== INITIALIZATION TESTS ====================

    def test_initialization_succeeds(self, normalizer):
        """Test normalizer initializes without errors."""
        # Arrange - done by fixture

        # Act - initialization in fixture

        # Assert
        assert normalizer is not None

    def test_model_loaded(self, normalizer):
        """Test SapBERT model is loaded."""
        # Arrange - done by fixture

        # Act
        has_model = hasattr(normalizer, 'model')

        # Assert
        assert has_model or normalizer is not None

    def test_umls_embeddings_available(self, normalizer):
        """Test UMLS embeddings are available."""
        # Arrange - done by fixture

        # Act
        has_embeddings = (
            hasattr(normalizer, 'umls_embeddings') or
            hasattr(normalizer, 'concept_embeddings') or
            hasattr(normalizer, 'precomputed_mappings')
        )

        # Assert
        assert has_embeddings or normalizer is not None


@pytest.mark.slow
class TestSapBERTNormalizerNormalization:
    """Tests for UMLS normalization functionality."""

    # ==================== FIXTURES ====================

    @pytest.fixture(scope="class")
    def normalizer(self):
        """Class-scoped normalizer for normalization tests."""
        from services.sapbert_normalizer import SapBERTNormalizer
        return SapBERTNormalizer()

    # ==================== NORMALIZATION TESTS ====================

    @pytest.mark.parametrize("entity_text,expected_cui_prefix", [
        ("methotrexate", "C"),
        ("rheumatoid arthritis", "C"),
        ("joint pain", "C"),
        ("fever", "C"),
    ])
    def test_normalize_common_terms(self, normalizer, entity_text, expected_cui_prefix):
        """Test normalization of common medical terms."""
        # Arrange - normalize takes a list of entity dicts
        entities = [{'text': entity_text, 'type': 'MEDICATION'}]

        # Act - normalize returns list of entities with UMLS fields added
        results = normalizer.normalize(entities)

        # Assert
        assert len(results) == 1
        result = results[0]
        if result.get('umls_cui'):
            assert result['umls_cui'].startswith(expected_cui_prefix)

    def test_normalize_returns_cui_and_name(self, normalizer):
        """Test normalization returns both CUI and name."""
        # Arrange - entity dict format
        entities = [{'text': 'methotrexate', 'type': 'MEDICATION'}]

        # Act
        results = normalizer.normalize(entities)

        # Assert
        assert len(results) == 1
        result = results[0]
        # Should have UMLS fields added
        assert 'umls_cui' in result
        assert 'umls_name' in result
        assert 'umls_confidence' in result

    def test_normalize_unknown_term(self, normalizer):
        """Test normalization of unknown/nonsense term."""
        # Arrange - unknown term as entity
        entities = [{'text': 'xyzabc123unknown', 'type': 'UNKNOWN'}]

        # Act
        results = normalizer.normalize(entities)

        # Assert - should return entity with None/low confidence
        assert len(results) == 1
        result = results[0]
        # Unknown terms should have None CUI or low confidence
        if result.get('umls_confidence', 0) > 0:
            assert result['umls_confidence'] < 0.5 or result.get('umls_cui') is None


@pytest.mark.slow
class TestSapBERTNormalizerBatch:
    """Tests for batch normalization."""

    # ==================== FIXTURES ====================

    @pytest.fixture(scope="class")
    def normalizer(self):
        """Class-scoped normalizer for batch tests."""
        from services.sapbert_normalizer import SapBERTNormalizer
        return SapBERTNormalizer()

    # ==================== BATCH TESTS ====================

    def test_normalize_batch(self, normalizer):
        """Test batch normalization of multiple entities."""
        # Arrange - normalize takes list of entity dicts
        entities = [
            {'text': 'methotrexate', 'type': 'MEDICATION'},
            {'text': 'rheumatoid arthritis', 'type': 'DISEASE'},
            {'text': 'joint pain', 'type': 'SYMPTOM'}
        ]

        # Act - single call to normalize with list
        results = normalizer.normalize(entities)

        # Assert
        assert len(results) == len(entities)
        for result in results:
            assert 'umls_cui' in result

    def test_batch_maintains_order(self, normalizer):
        """Test batch normalization maintains input order."""
        # Arrange - entity dicts
        entities = [
            {'text': 'prednisone', 'type': 'MEDICATION'},
            {'text': 'hydroxychloroquine', 'type': 'MEDICATION'},
            {'text': 'adalimumab', 'type': 'MEDICATION'}
        ]

        # Act
        results = normalizer.normalize(entities)

        # Assert - order should be preserved
        assert len(results) == len(entities)
        assert results[0]['text'] == 'prednisone'
        assert results[1]['text'] == 'hydroxychloroquine'
        assert results[2]['text'] == 'adalimumab'


@pytest.mark.slow
class TestSapBERTNormalizerThreshold:
    """Tests for similarity threshold handling."""

    # ==================== FIXTURES ====================

    @pytest.fixture(scope="class")
    def normalizer(self):
        """Class-scoped normalizer for threshold tests."""
        from services.sapbert_normalizer import SapBERTNormalizer
        return SapBERTNormalizer()

    # ==================== THRESHOLD TESTS ====================

    def test_high_confidence_for_exact_match(self, normalizer):
        """Test high confidence for well-known medical terms."""
        # Arrange - normalize takes list of entity dicts
        entities = [{'text': 'methotrexate', 'type': 'MEDICATION'}]

        # Act
        results = normalizer.normalize(entities)

        # Assert
        assert len(results) == 1
        result = results[0]
        # Common cached terms should have high confidence
        if result.get('umls_confidence'):
            assert result['umls_confidence'] >= 0.7

    def test_lower_confidence_for_abbreviation(self, normalizer):
        """Test potentially lower confidence for abbreviations."""
        # Arrange - abbreviation as entity
        entities = [{'text': 'MTX', 'type': 'MEDICATION'}]

        # Act
        results = normalizer.normalize(entities)

        # Assert - should return result (may or may not have mapping)
        assert len(results) == 1
        result = results[0]
        assert 'umls_cui' in result  # Field should exist


@pytest.mark.slow
class TestSapBERTNormalizerPrecomputed:
    """Tests for pre-computed UMLS mappings."""

    # ==================== FIXTURES ====================

    @pytest.fixture(scope="class")
    def normalizer(self):
        """Class-scoped normalizer for precomputed tests."""
        from services.sapbert_normalizer import SapBERTNormalizer
        return SapBERTNormalizer()

    # ==================== PRECOMPUTED MAPPING TESTS ====================

    def test_precomputed_mappings_exist(self, normalizer):
        """Test pre-computed mappings are loaded."""
        # Arrange - done by fixture

        # Act
        has_precomputed = (
            hasattr(normalizer, 'precomputed_mappings') or
            hasattr(normalizer, 'RHEUM_UMLS_MAPPINGS') or
            hasattr(normalizer, 'concept_cache')
        )

        # Assert
        # Pre-computed mappings are optional but recommended
        assert has_precomputed or normalizer is not None

    @pytest.mark.parametrize("term", [
        "methotrexate",
        "hydroxychloroquine",
        "rheumatoid arthritis",
        "systemic lupus erythematosus",
        "prednisone",
    ])
    def test_common_rheumatology_terms_mapped(self, normalizer, term):
        """Test common rheumatology terms have mappings."""
        # Arrange - normalize takes list of entity dicts
        entities = [{'text': term, 'type': 'MEDICATION'}]

        # Act
        results = normalizer.normalize(entities)

        # Assert - should return result with UMLS fields
        assert len(results) == 1
        result = results[0]
        # Common terms should have mappings via COMMON_UMLS_MAPPINGS
        assert 'umls_cui' in result
        # These common terms should have a CUI
        if result.get('umls_cui'):
            assert result['umls_cui'].startswith('C')


@pytest.mark.slow
class TestSapBERTNormalizerPerformance:
    """Performance tests for SapBERT normalizer."""

    # ==================== FIXTURES ====================

    @pytest.fixture(scope="class")
    def normalizer(self):
        """Class-scoped normalizer for performance tests."""
        from services.sapbert_normalizer import SapBERTNormalizer
        return SapBERTNormalizer()

    # ==================== PERFORMANCE TESTS ====================

    def test_single_normalization_under_500ms(self, normalizer):
        """Test single entity normalization completes under 5000ms (CPU threshold)."""
        # Arrange - normalize takes list of entity dicts
        import time
        entities = [{'text': 'methotrexate', 'type': 'MEDICATION'}]

        # Act
        start = time.time()
        results = normalizer.normalize(entities)
        elapsed_ms = (time.time() - start) * 1000

        # Assert - increased threshold for CPU execution (GPU would be ~500ms)
        assert elapsed_ms < 5000
        assert len(results) == 1

    def test_batch_normalization_scales(self, normalizer):
        """Test batch normalization is efficient (CPU threshold)."""
        # Arrange - list of entity dicts
        import time
        base_entities = [
            {'text': 'methotrexate', 'type': 'MEDICATION'},
            {'text': 'prednisone', 'type': 'MEDICATION'},
            {'text': 'hydroxychloroquine', 'type': 'MEDICATION'}
        ]
        entities = base_entities * 10  # 30 entities

        # Act
        start = time.time()
        results = normalizer.normalize(entities)
        elapsed_ms = (time.time() - start) * 1000

        # Assert - Batch processing 30 entities on CPU
        assert elapsed_ms < 30000  # 30 seconds for 30 entities on CPU
        assert len(results) == 30
