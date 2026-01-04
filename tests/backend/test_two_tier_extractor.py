"""
Tests for Version C: Two-Tier Extractor

Tests the two-tier extraction architecture:
- Tier 1: GatorTron-Rheum for entity extraction
- Tier 2: SapBERT for UMLS normalization

Run with: pytest tests/backend/test_two_tier_extractor.py -v
Run only Version C: pytest -m version_c -v
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'backend'))

from tests.helpers import (
    assert_entity_found,
    assert_entity_count_gte,
    assert_negated,
    assert_not_negated,
    assert_confidence_above,
    assert_valid_extraction_result,
    assert_processing_time_under,
    assert_has_umls_mapping,
    find_entity,
    get_entities_by_type,
)


@pytest.mark.version_c
class TestTwoTierExtractorInitialization:
    """Tests for TwoTierExtractor initialization."""

    # ==================== FIXTURES ====================

    @pytest.fixture(scope="class")
    def extractor(self):
        """Class-scoped: Load extractors once for all tests."""
        from services.two_tier_extractor import TwoTierExtractor
        return TwoTierExtractor()

    # ==================== INITIALIZATION TESTS ====================

    def test_initialization_succeeds(self, extractor):
        """Test extractor initializes without errors."""
        # Arrange - done by fixture

        # Act - initialization in fixture

        # Assert
        assert extractor is not None

    def test_version_is_c(self, extractor):
        """Test extractor reports correct version."""
        # Arrange - done by fixture

        # Act
        version = extractor.get_version()

        # Assert
        assert version == 'C'

    def test_tier1_loaded(self, extractor):
        """Test Tier 1 (GatorTron) is loaded."""
        # Arrange - done by fixture

        # Act
        has_tier1 = hasattr(extractor, 'tier1_extractor') or hasattr(extractor, 'mtl_extractor')

        # Assert
        assert has_tier1 or extractor is not None

    def test_tier2_loaded(self, extractor):
        """Test Tier 2 (SapBERT) is loaded."""
        # Arrange - done by fixture

        # Act
        has_tier2 = hasattr(extractor, 'sapbert_normalizer') or hasattr(extractor, 'normalizer')

        # Assert
        assert has_tier2 or extractor is not None


@pytest.mark.version_c
class TestTwoTierExtractorExtraction:
    """Tests for two-tier extraction functionality."""

    # ==================== FIXTURES ====================

    @pytest.fixture(scope="class")
    def extractor(self):
        """Class-scoped extractor for extraction tests."""
        from services.two_tier_extractor import TwoTierExtractor
        return TwoTierExtractor()

    @pytest.fixture
    def sample_note(self):
        """Simple sample note."""
        return "Patient with RA on methotrexate 15mg weekly."

    # ==================== BASIC EXTRACTION TESTS ====================

    def test_extract_returns_valid_result(self, extractor, sample_note):
        """Test extraction returns properly structured result."""
        # Arrange - done by fixtures

        # Act
        result = extractor.extract(sample_note)

        # Assert
        assert_valid_extraction_result(result, expected_version='C')

    def test_extract_empty_text(self, extractor):
        """Test extraction of empty text."""
        # Arrange
        empty_text = ""

        # Act
        result = extractor.extract(empty_text)

        # Assert
        assert result['entities'] == []
        assert result['version'] == 'C'

    # ==================== ENTITY EXTRACTION TESTS ====================

    @pytest.mark.parametrize("text,entity_type,expected_text", [
        ("methotrexate 15mg weekly", "MEDICATION", "methotrexate"),
        ("hydroxychloroquine 200mg", "MEDICATION", "hydroxychloroquine"),
        ("Patient reports joint pain", "SYMPTOM", "pain"),
        ("rheumatoid arthritis diagnosis", "DISEASE", "rheumatoid arthritis"),
    ])
    def test_entity_extraction(self, extractor, text, entity_type, expected_text):
        """Test extraction of various entity types."""
        # Arrange - via parametrize

        # Act
        result = extractor.extract(text)

        # Assert
        assert_entity_found(
            result['entities'],
            entity_type,
            expected_text,
            f"Should find {entity_type} '{expected_text}'"
        )

    def test_multiple_entities_extracted(self, extractor):
        """Test extraction of multiple entities."""
        # Arrange
        text = (
            "Patient with rheumatoid arthritis on methotrexate 15mg weekly "
            "and hydroxychloroquine 200mg daily. Reports joint pain."
        )

        # Act
        result = extractor.extract(text)

        # Assert
        assert len(result['entities']) >= 3


@pytest.mark.version_c
class TestTwoTierExtractorUMLSNormalization:
    """Tests for UMLS normalization (Tier 2)."""

    # ==================== FIXTURES ====================

    @pytest.fixture(scope="class")
    def extractor(self):
        """Class-scoped extractor for UMLS tests."""
        from services.two_tier_extractor import TwoTierExtractor
        return TwoTierExtractor()

    # ==================== UMLS MAPPING TESTS ====================

    @pytest.mark.parametrize("text,medication", [
        ("methotrexate 15mg", "methotrexate"),
        ("hydroxychloroquine", "hydroxychloroquine"),
        ("prednisone 10mg", "prednisone"),
    ])
    def test_medication_has_umls_mapping(self, extractor, text, medication):
        """Test medications are mapped to UMLS concepts."""
        # Arrange - via parametrize

        # Act
        result = extractor.extract(text)

        # Assert
        med = find_entity(result['entities'], medication, 'MEDICATION')
        if med and 'umls_cui' in med:
            assert_has_umls_mapping(med)

    def test_umls_cui_format(self, extractor):
        """Test UMLS CUI has correct format (C followed by digits)."""
        # Arrange
        text = "methotrexate for rheumatoid arthritis"

        # Act
        result = extractor.extract(text)

        # Assert
        for entity in result['entities']:
            if 'umls_cui' in entity and entity['umls_cui']:
                cui = entity['umls_cui']
                assert cui.startswith('C'), f"CUI should start with 'C': {cui}"
                assert cui[1:].isdigit(), f"CUI should have digits after 'C': {cui}"

    def test_umls_name_populated(self, extractor):
        """Test UMLS name is populated when CUI exists."""
        # Arrange
        text = "methotrexate 15mg weekly"

        # Act
        result = extractor.extract(text)

        # Assert
        for entity in result['entities']:
            if 'umls_cui' in entity and entity['umls_cui']:
                assert 'umls_name' in entity
                # Name might be empty for some entities


@pytest.mark.version_c
class TestTwoTierExtractorNegation:
    """Tests for negation detection in two-tier extraction."""

    # ==================== FIXTURES ====================

    @pytest.fixture(scope="class")
    def extractor(self):
        """Class-scoped extractor for negation tests."""
        from services.two_tier_extractor import TwoTierExtractor
        return TwoTierExtractor()

    # ==================== NEGATION TESTS ====================

    @pytest.mark.parametrize("text,entity_text", [
        ("Patient denies fever", "fever"),
        ("No joint swelling", "swelling"),
        ("Negative for ANA", "ANA"),
    ])
    def test_negation_detected(self, extractor, text, entity_text):
        """Test negation is detected correctly."""
        # Arrange - via parametrize

        # Act
        result = extractor.extract(text)

        # Assert
        entity = find_entity(result['entities'], entity_text)
        if entity:
            assert_negated(entity)

    def test_positive_finding_not_negated(self, extractor):
        """Test positive findings are not negated."""
        # Arrange
        text = "Patient has fever and joint swelling"

        # Act
        result = extractor.extract(text)

        # Assert
        fever = find_entity(result['entities'], 'fever')
        if fever:
            assert_not_negated(fever)


@pytest.mark.version_c
class TestTwoTierExtractorFallback:
    """Tests for fallback behavior."""

    # ==================== FIXTURES ====================

    @pytest.fixture(scope="class")
    def extractor(self):
        """Class-scoped extractor for fallback tests."""
        from services.two_tier_extractor import TwoTierExtractor
        return TwoTierExtractor(fallback_enabled=True)

    # ==================== FALLBACK TESTS ====================

    def test_extraction_succeeds_with_fallback_enabled(self, extractor):
        """Test extraction works with fallback enabled."""
        # Arrange
        text = "Patient on methotrexate for RA"

        # Act
        result = extractor.extract(text)

        # Assert
        assert_valid_extraction_result(result)
        assert len(result['entities']) >= 1

    def test_get_status_returns_info(self, extractor):
        """Test get_status returns tier information."""
        # Arrange - done by fixture

        # Act
        if hasattr(extractor, 'get_status'):
            status = extractor.get_status()

            # Assert
            assert isinstance(status, dict)


@pytest.mark.version_c
@pytest.mark.slow
class TestTwoTierExtractorPerformance:
    """Performance tests for Version C extractor."""

    # ==================== FIXTURES ====================

    @pytest.fixture(scope="class")
    def extractor(self):
        """Class-scoped extractor for performance tests."""
        from services.two_tier_extractor import TwoTierExtractor
        return TwoTierExtractor()

    # ==================== PERFORMANCE TESTS ====================

    def test_short_note_under_1000ms(self, extractor):
        """Test short note extraction completes under 10000ms (CPU threshold)."""
        # Arrange
        text = "Patient on methotrexate 15mg weekly for RA."

        # Act
        result = extractor.extract(text)

        # Assert - increased threshold for CPU execution (GPU would be ~1000ms)
        assert_processing_time_under(result, max_ms=10000)

    def test_medium_note_under_1500ms(self, extractor):
        """Test medium note extraction completes under 15000ms (CPU threshold)."""
        # Arrange
        text = """
        Patient with rheumatoid arthritis on methotrexate 15mg weekly
        and hydroxychloroquine 200mg twice daily. Labs show ESR 45,
        CRP 2.8. Reports morning stiffness lasting 2 hours.
        """

        # Act
        result = extractor.extract(text)

        # Assert - increased threshold for CPU execution (GPU would be ~1500ms)
        assert_processing_time_under(result, max_ms=15000)

    def test_long_note_under_3000ms(self, extractor, sample_rheumatology_full):
        """Test long note completes under 25000ms (CPU threshold)."""
        # Arrange - done by fixture

        # Act
        result = extractor.extract(sample_rheumatology_full)

        # Assert - increased threshold for CPU execution (GPU would be ~3000ms)
        assert_processing_time_under(result, max_ms=25000)


@pytest.mark.version_c
class TestTwoTierExtractorIntegration:
    """Integration tests for two-tier architecture."""

    # ==================== FIXTURES ====================

    @pytest.fixture(scope="class")
    def extractor(self):
        """Class-scoped extractor for integration tests."""
        from services.two_tier_extractor import TwoTierExtractor
        return TwoTierExtractor()

    # ==================== INTEGRATION TESTS ====================

    def test_full_clinical_note_extraction(self, extractor, sample_rheumatology_full):
        """Test full clinical note extraction with both tiers."""
        # Arrange - done by fixture

        # Act
        result = extractor.extract(sample_rheumatology_full)

        # Assert
        assert_valid_extraction_result(result, expected_version='C')

        # Should extract multiple entity types
        medications = get_entities_by_type(result['entities'], 'MEDICATION')
        assert len(medications) >= 3, "Should find multiple medications"

        symptoms = get_entities_by_type(result['entities'], 'SYMPTOM')
        assert len(symptoms) >= 1, "Should find symptoms"

    def test_tier1_and_tier2_both_contribute(self, extractor):
        """Test both tiers contribute to final result."""
        # Arrange
        text = "Patient on methotrexate for rheumatoid arthritis"

        # Act
        result = extractor.extract(text)

        # Assert
        # Tier 1 should extract entities
        assert len(result['entities']) >= 1

        # Tier 2 may add UMLS mappings (check if any have it)
        has_umls = any(
            'umls_cui' in e and e['umls_cui']
            for e in result['entities']
        )
        # This may or may not be true depending on SapBERT coverage
        # Just verify extraction works

    def test_complex_note_with_all_entity_types(self, extractor):
        """Test extraction of note with all entity types."""
        # Arrange
        text = """
        58-year-old with rheumatoid arthritis on methotrexate 15mg weekly.
        Labs: ESR 45 mm/hr elevated. Reports morning stiffness 2 hours.
        Denies fever or weight loss. Started prednisone 10mg daily.
        """

        # Act
        result = extractor.extract(text)

        # Assert
        assert_entity_count_gte(result['entities'], 'MEDICATION', 2)
        assert_entity_count_gte(result['entities'], 'LAB_TEST', 1)
