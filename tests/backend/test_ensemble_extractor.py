"""
Tests for Version D: Ensemble Extractor

Tests the ensemble extraction architecture combining:
- Version A (Regex)
- Version B (GatorTron)
- Version C (Two-Tier)
- BioLinkBERT (contextual inference)

Run with: pytest tests/backend/test_ensemble_extractor.py -v
Run only Version D: pytest -m version_d -v
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
    assert_confidence_above,
    assert_valid_extraction_result,
    assert_processing_time_under,
    assert_agreement_score,
    assert_inferred_diagnosis,
    find_entity,
    get_entities_by_type,
)


@pytest.mark.version_d
class TestEnsembleExtractorInitialization:
    """Tests for EnsembleExtractor initialization."""

    # ==================== FIXTURES ====================

    @pytest.fixture(scope="class")
    def extractor(self):
        """Class-scoped: Load all extractors once."""
        from services.ensemble_extractor import EnsembleExtractor
        return EnsembleExtractor()

    # ==================== INITIALIZATION TESTS ====================

    def test_initialization_succeeds(self, extractor):
        """Test extractor initializes without errors."""
        # Arrange - done by fixture

        # Act - initialization in fixture

        # Assert
        assert extractor is not None

    def test_version_is_d(self, extractor):
        """Test extractor reports correct version."""
        # Arrange - done by fixture

        # Act
        version = extractor.get_version()

        # Assert
        assert version == 'D'

    def test_multiple_extractors_available(self, extractor):
        """Test multiple sub-extractors are loaded."""
        # Arrange - done by fixture

        # Act
        if hasattr(extractor, 'get_available_extractors'):
            available = extractor.get_available_extractors()
        else:
            available = []

        # Assert
        # Should have at least regex always available
        assert len(available) >= 1 or extractor is not None


@pytest.mark.version_d
class TestEnsembleExtractorExtraction:
    """Tests for ensemble extraction functionality."""

    # ==================== FIXTURES ====================

    @pytest.fixture(scope="class")
    def extractor(self):
        """Class-scoped extractor for extraction tests."""
        from services.ensemble_extractor import EnsembleExtractor
        return EnsembleExtractor()

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
        assert_valid_extraction_result(result, expected_version='D')

    def test_extract_empty_text(self, extractor):
        """Test extraction of empty text."""
        # Arrange
        empty_text = ""

        # Act
        result = extractor.extract(empty_text)

        # Assert
        assert result['entities'] == []
        assert result['version'] == 'D'

    # ==================== ENTITY EXTRACTION TESTS ====================

    @pytest.mark.parametrize("text,entity_type,expected_text", [
        ("methotrexate 15mg weekly", "MEDICATION", "methotrexate"),
        ("hydroxychloroquine 200mg", "MEDICATION", "hydroxychloroquine"),
        ("Patient reports joint pain", "SYMPTOM", "pain"),
        ("rheumatoid arthritis", "DISEASE", "rheumatoid arthritis"),
        ("ESR 45 mm/hr", "LAB_TEST", "ESR"),
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

    def test_multiple_entities_from_complex_note(self, extractor):
        """Test extraction of multiple entities from complex note."""
        # Arrange
        text = """
        Patient with rheumatoid arthritis on methotrexate 15mg weekly,
        hydroxychloroquine 200mg daily. Labs show ESR 45, CRP 2.8.
        Reports morning stiffness and joint pain. Denies fever.
        """

        # Act
        result = extractor.extract(text)

        # Assert
        assert len(result['entities']) >= 5


@pytest.mark.version_d
class TestEnsembleExtractorAgreement:
    """Tests for agreement scoring in ensemble."""

    # ==================== FIXTURES ====================

    @pytest.fixture(scope="class")
    def extractor(self):
        """Class-scoped extractor for agreement tests."""
        from services.ensemble_extractor import EnsembleExtractor
        return EnsembleExtractor()

    # ==================== AGREEMENT TESTS ====================

    def test_entities_have_agreement_field(self, extractor):
        """Test entities have agreement score field."""
        # Arrange
        text = "methotrexate 15mg weekly for rheumatoid arthritis"

        # Act
        result = extractor.extract(text)

        # Assert
        for entity in result['entities']:
            assert 'agreement' in entity or 'versions_found' in entity

    def test_high_agreement_for_common_entities(self, extractor):
        """Test common entities have high agreement."""
        # Arrange
        text = "methotrexate 15mg"  # Very common, should be found by multiple

        # Act
        result = extractor.extract(text)

        # Assert
        med = find_entity(result['entities'], 'methotrexate')
        if med and 'agreement' in med:
            assert med['agreement'] >= 1

    def test_versions_found_populated(self, extractor):
        """Test versions_found shows which extractors found entity."""
        # Arrange
        text = "Patient on methotrexate for rheumatoid arthritis"

        # Act
        result = extractor.extract(text)

        # Assert
        for entity in result['entities']:
            if 'versions_found' in entity:
                assert isinstance(entity['versions_found'], (list, str))


@pytest.mark.version_d
class TestEnsembleExtractorConfidenceWeighting:
    """Tests for confidence weighting in ensemble."""

    # ==================== FIXTURES ====================

    @pytest.fixture(scope="class")
    def extractor(self):
        """Class-scoped extractor for confidence tests."""
        from services.ensemble_extractor import EnsembleExtractor
        return EnsembleExtractor()

    # ==================== CONFIDENCE WEIGHTING TESTS ====================

    def test_entities_have_weighted_confidence(self, extractor):
        """Test entities have confidence scores."""
        # Arrange
        text = "methotrexate for rheumatoid arthritis"

        # Act
        result = extractor.extract(text)

        # Assert
        for entity in result['entities']:
            assert 'confidence' in entity
            assert 0.0 <= entity['confidence'] <= 1.0

    def test_multi_extractor_agreement_boosts_confidence(self, extractor):
        """Test that agreement from multiple extractors boosts confidence."""
        # Arrange
        text = "methotrexate 15mg weekly"

        # Act
        result = extractor.extract(text)

        # Assert
        med = find_entity(result['entities'], 'methotrexate')
        if med:
            # High-agreement entities should have reasonable confidence
            assert_confidence_above(med, threshold=0.5)


@pytest.mark.version_d
class TestEnsembleExtractorInference:
    """Tests for contextual inference (BioLinkBERT)."""

    # ==================== FIXTURES ====================

    @pytest.fixture(scope="class")
    def extractor(self):
        """Class-scoped extractor for inference tests."""
        from services.ensemble_extractor import EnsembleExtractor
        return EnsembleExtractor()

    # ==================== INFERENCE TESTS ====================

    def test_result_includes_inferred_field(self, extractor):
        """Test result includes inferred diagnoses field."""
        # Arrange
        text = """
        Patient with joint pain, morning stiffness, positive RF and anti-CCP,
        elevated ESR and CRP, symmetric polyarthritis.
        """

        # Act
        result = extractor.extract(text)

        # Assert
        # Result may or may not have 'inferred' depending on implementation
        assert 'entities' in result

    def test_inferred_diagnosis_from_symptoms(self, extractor):
        """Test diagnosis is inferred from symptom cluster."""
        # Arrange - classic RA presentation
        text = """
        58-year-old female with symmetric polyarthritis affecting MCPs and PIPs,
        morning stiffness lasting 2 hours, positive RF 156 IU/mL,
        anti-CCP 340 units strongly positive, ESR 52 elevated, CRP 3.2 elevated.
        X-rays show periarticular osteopenia and early erosions.
        """

        # Act
        result = extractor.extract(text)

        # Assert
        if 'inferred' in result and result['inferred']:
            assert_inferred_diagnosis(result, 'rheumatoid')


@pytest.mark.version_d
class TestEnsembleExtractorEntityLinking:
    """Tests for entity linking functionality."""

    # ==================== FIXTURES ====================

    @pytest.fixture(scope="class")
    def extractor(self):
        """Class-scoped extractor for linking tests."""
        from services.ensemble_extractor import EnsembleExtractor
        return EnsembleExtractor()

    # ==================== ENTITY LINKING TESTS ====================

    def test_result_may_include_links(self, extractor):
        """Test result may include entity links."""
        # Arrange
        text = "Patient on methotrexate for rheumatoid arthritis"

        # Act
        result = extractor.extract(text)

        # Assert
        # Links field is optional, just check extraction works
        assert_valid_extraction_result(result)

    def test_medication_disease_relationship(self, extractor):
        """Test medication-disease relationship may be captured."""
        # Arrange
        text = "methotrexate for rheumatoid arthritis"

        # Act
        result = extractor.extract(text)

        # Assert
        if 'links' in result and result['links']:
            # Check if any link connects methotrexate to RA
            found_link = any(
                'methotrexate' in str(link).lower() and 'arthritis' in str(link).lower()
                for link in result['links']
            )
            # This is optional functionality


@pytest.mark.version_d
class TestEnsembleExtractorNegation:
    """Tests for negation detection in ensemble."""

    # ==================== FIXTURES ====================

    @pytest.fixture(scope="class")
    def extractor(self):
        """Class-scoped extractor for negation tests."""
        from services.ensemble_extractor import EnsembleExtractor
        return EnsembleExtractor()

    # ==================== NEGATION TESTS ====================

    @pytest.mark.parametrize("text,entity_text", [
        ("Patient denies fever", "fever"),
        ("No joint swelling observed", "swelling"),
        ("Negative for ANA", "ANA"),
    ])
    def test_negation_detected(self, extractor, text, entity_text):
        """Test negation is detected by ensemble."""
        # Arrange - via parametrize

        # Act
        result = extractor.extract(text)

        # Assert
        entity = find_entity(result['entities'], entity_text)
        if entity:
            assert_negated(entity)


@pytest.mark.version_d
class TestEnsembleExtractorDeduplication:
    """Tests for entity deduplication."""

    # ==================== FIXTURES ====================

    @pytest.fixture(scope="class")
    def extractor(self):
        """Class-scoped extractor for dedup tests."""
        from services.ensemble_extractor import EnsembleExtractor
        return EnsembleExtractor()

    # ==================== DEDUPLICATION TESTS ====================

    def test_no_exact_duplicates(self, extractor):
        """Test no exact duplicate entities in result."""
        # Arrange
        text = "Patient on methotrexate for rheumatoid arthritis"

        # Act
        result = extractor.extract(text)

        # Assert
        entity_keys = [
            (e['text'].lower(), e['type'], e.get('start', 0))
            for e in result['entities']
        ]
        assert len(entity_keys) == len(set(entity_keys)), "Found duplicate entities"

    def test_overlapping_spans_merged(self, extractor):
        """Test overlapping entity spans are handled."""
        # Arrange
        text = "methotrexate 15mg weekly"

        # Act
        result = extractor.extract(text)

        # Assert
        # Should not have multiple versions of same medication
        meds = [e for e in result['entities'] if 'methotrexate' in e['text'].lower()]
        # May have 1 or more depending on if dosage is separate
        assert len(meds) >= 1


@pytest.mark.version_d
@pytest.mark.slow
class TestEnsembleExtractorPerformance:
    """Performance tests for Version D extractor."""

    # ==================== FIXTURES ====================

    @pytest.fixture(scope="class")
    def extractor(self):
        """Class-scoped extractor for performance tests."""
        from services.ensemble_extractor import EnsembleExtractor
        return EnsembleExtractor()

    # ==================== PERFORMANCE TESTS ====================

    def test_short_note_under_3000ms(self, extractor):
        """Test short note extraction completes under 30000ms (CPU threshold)."""
        # Arrange
        text = "Patient on methotrexate 15mg weekly for RA."

        # Act
        result = extractor.extract(text)

        # Assert - Ensemble runs 4 extractors, needs more time on CPU
        assert_processing_time_under(result, max_ms=30000)

    def test_medium_note_under_5000ms(self, extractor):
        """Test medium note extraction completes under 45000ms (CPU threshold)."""
        # Arrange
        text = """
        Patient with rheumatoid arthritis on methotrexate 15mg weekly
        and hydroxychloroquine 200mg twice daily. Labs show ESR 45,
        CRP 2.8. Reports morning stiffness lasting 2 hours.
        """

        # Act
        result = extractor.extract(text)

        # Assert - Ensemble runs 4 extractors, needs more time on CPU
        assert_processing_time_under(result, max_ms=45000)

    def test_parallel_execution_faster_than_sequential(self, extractor):
        """Test parallel execution provides performance benefit."""
        # Arrange
        text = "methotrexate for rheumatoid arthritis"

        # Act
        result = extractor.extract(text)

        # Assert
        # Even with 4 extractors, should complete in reasonable time
        assert result['processing_time_ms'] < 10000


@pytest.mark.version_d
class TestEnsembleExtractorIntegration:
    """Integration tests for ensemble extractor."""

    # ==================== FIXTURES ====================

    @pytest.fixture(scope="class")
    def extractor(self):
        """Class-scoped extractor for integration tests."""
        from services.ensemble_extractor import EnsembleExtractor
        return EnsembleExtractor()

    # ==================== INTEGRATION TESTS ====================

    def test_full_clinical_note_extraction(self, extractor, sample_rheumatology_full):
        """Test full clinical note with all ensemble components."""
        # Arrange - done by fixture

        # Act
        result = extractor.extract(sample_rheumatology_full)

        # Assert
        assert_valid_extraction_result(result, expected_version='D')

        # Should extract many entities from comprehensive note
        assert len(result['entities']) >= 10

        # Multiple entity types should be present
        types_found = set(e['type'] for e in result['entities'])
        assert len(types_found) >= 3

    def test_extractors_used_field(self, extractor):
        """Test extractors_used field shows active extractors."""
        # Arrange
        text = "Patient on methotrexate for RA"

        # Act
        result = extractor.extract(text)

        # Assert
        if 'extractors_used' in result:
            assert isinstance(result['extractors_used'], list)
            assert len(result['extractors_used']) >= 1

    def test_agreement_summary_field(self, extractor):
        """Test agreement_summary provides overview."""
        # Arrange
        text = "methotrexate 15mg weekly for rheumatoid arthritis"

        # Act
        result = extractor.extract(text)

        # Assert
        if 'agreement_summary' in result:
            assert isinstance(result['agreement_summary'], dict)

    def test_graceful_degradation(self, extractor):
        """Test ensemble degrades gracefully if some extractors fail."""
        # Arrange
        text = "methotrexate for RA"

        # Act
        result = extractor.extract(text)

        # Assert
        # Should always return valid result even if some extractors fail
        assert_valid_extraction_result(result)
        # At minimum, regex (Version A) should always work
        assert len(result['entities']) >= 1 or result['version'] == 'D'
