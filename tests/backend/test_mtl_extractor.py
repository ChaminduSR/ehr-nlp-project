"""
Tests for Version B: MTL Entity Extractor (GatorTron-Rheum)

Tests the transformer-based medical entity extraction using custom-trained
GatorTron model for rheumatology clinical notes.

Run with: pytest tests/backend/test_mtl_extractor.py -v
Run only Version B: pytest -m version_b -v
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'backend'))

from tests.helpers import (
    assert_entity_found,
    assert_entity_not_found,
    assert_entity_count_gte,
    assert_negated,
    assert_not_negated,
    assert_confidence_above,
    assert_valid_extraction_result,
    assert_processing_time_under,
    find_entity,
    get_entities_by_type,
)


@pytest.mark.version_b
class TestMTLEntityExtractorInitialization:
    """Tests for MTLEntityExtractor initialization and configuration."""

    # ==================== FIXTURES ====================

    @pytest.fixture(scope="class")
    def extractor(self):
        """Class-scoped: Load model once for all tests in class."""
        from services.mtl_entity_extractor import MTLEntityExtractor
        return MTLEntityExtractor()

    # ==================== INITIALIZATION TESTS ====================

    def test_initialization_succeeds(self, extractor):
        """Test extractor initializes without errors."""
        # Arrange - done by fixture

        # Act - initialization happens in fixture

        # Assert
        assert extractor is not None

    def test_version_is_b(self, extractor):
        """Test extractor reports correct version."""
        # Arrange - done by fixture

        # Act
        version = extractor.get_version()

        # Assert
        assert version == 'B'

    def test_model_name_is_gatortron_rheum(self, extractor):
        """Test extractor reports correct model name."""
        # Arrange - done by fixture

        # Act
        model_name = extractor.get_model_name()

        # Assert
        assert model_name == 'gatortron-rheum'

    def test_model_loaded_on_device(self, extractor):
        """Test model is loaded on correct device."""
        # Arrange - done by fixture

        # Act
        device = extractor.device

        # Assert
        assert device is not None
        assert str(device) in ['cpu', 'cuda', 'cuda:0']

    def test_tokenizer_loaded(self, extractor):
        """Test tokenizer is available."""
        # Arrange - done by fixture

        # Act
        tokenizer = extractor.tokenizer

        # Assert
        assert tokenizer is not None


@pytest.mark.version_b
class TestMTLEntityExtractorExtraction:
    """Tests for entity extraction functionality."""

    # ==================== FIXTURES ====================

    @pytest.fixture(scope="class")
    def extractor(self):
        """Class-scoped extractor for extraction tests."""
        from services.mtl_entity_extractor import MTLEntityExtractor
        return MTLEntityExtractor()

    @pytest.fixture
    def sample_note(self):
        """Simple sample note for basic tests."""
        return "Patient with RA on methotrexate 15mg weekly. Denies fever."

    # ==================== BASIC EXTRACTION TESTS ====================

    def test_extract_returns_valid_result(self, extractor, sample_note):
        """Test extraction returns properly structured result."""
        # Arrange - done by fixtures

        # Act
        result = extractor.extract(sample_note)

        # Assert
        assert_valid_extraction_result(result, expected_version='B')

    def test_extract_empty_text_returns_empty_entities(self, extractor):
        """Test extraction of empty text returns empty entity list."""
        # Arrange
        empty_text = ""

        # Act
        result = extractor.extract(empty_text)

        # Assert
        assert result['entities'] == []
        assert result['version'] == 'B'

    def test_extract_no_entities_text(self, extractor):
        """Test extraction of text with no medical entities."""
        # Arrange
        text = "The weather is nice today. Patient arrived on time."

        # Act
        result = extractor.extract(text)

        # Assert
        assert_valid_extraction_result(result, expected_version='B')
        # May have some false positives, but should be minimal
        assert len(result['entities']) <= 2

    # ==================== MEDICATION EXTRACTION TESTS ====================

    @pytest.mark.parametrize("text,expected_medication", [
        ("methotrexate 15mg weekly", "methotrexate"),
        ("hydroxychloroquine 200mg twice daily", "hydroxychloroquine"),
        ("prednisone 10mg daily", "prednisone"),
        ("adalimumab 40mg injection", "adalimumab"),
        ("etanercept 50mg subcutaneous weekly", "etanercept"),
        ("sulfasalazine 500mg twice daily", "sulfasalazine"),
        ("leflunomide 20mg daily", "leflunomide"),
        ("Patient on MTX", "MTX"),
        ("Started on HCQ", "HCQ"),
    ])
    def test_extract_medication(self, extractor, text, expected_medication):
        """Test extraction of various medications."""
        # Arrange - via parametrize

        # Act
        result = extractor.extract(text)

        # Assert
        assert_entity_found(
            result['entities'],
            'MEDICATION',
            expected_medication,
            f"Should find medication '{expected_medication}' in: {text}"
        )

    def test_extract_multiple_medications(self, extractor):
        """Test extraction of multiple medications in one note."""
        # Arrange
        text = (
            "Patient on methotrexate 15mg weekly, "
            "hydroxychloroquine 200mg daily, "
            "and prednisone 5mg daily."
        )

        # Act
        result = extractor.extract(text)

        # Assert
        assert_entity_count_gte(result['entities'], 'MEDICATION', 3)

    # ==================== DOSAGE EXTRACTION TESTS ====================

    @pytest.mark.parametrize("text,expected_dosage", [
        ("methotrexate 15mg", "15mg"),
        ("prednisone 10 mg daily", "10 mg"),
        ("hydroxychloroquine 200mg", "200mg"),
        ("adalimumab 40mg injection", "40mg"),
    ])
    def test_extract_dosage(self, extractor, text, expected_dosage):
        """Test extraction of dosage information."""
        # Arrange - via parametrize

        # Act
        result = extractor.extract(text)

        # Assert
        dosages = get_entities_by_type(result['entities'], 'DOSAGE')
        # Dosage might be part of medication entity, so check both
        found = any(
            expected_dosage.replace(' ', '') in e['text'].replace(' ', '')
            for e in result['entities']
        )
        assert found, f"Should find dosage '{expected_dosage}' in: {text}"

    # ==================== FREQUENCY EXTRACTION TESTS ====================

    @pytest.mark.parametrize("text,expected_freq", [
        ("methotrexate weekly", "weekly"),
        ("prednisone daily", "daily"),
        ("hydroxychloroquine twice daily", "twice daily"),
        ("adalimumab every 2 weeks", "every 2 weeks"),
        ("etanercept once weekly", "once weekly"),
    ])
    def test_extract_frequency(self, extractor, text, expected_freq):
        """Test extraction of medication frequency."""
        # Arrange - via parametrize

        # Act
        result = extractor.extract(text)

        # Assert
        # Frequency might be standalone or part of another entity
        found = any(
            expected_freq.lower() in e['text'].lower()
            for e in result['entities']
        )
        assert found, f"Should find frequency '{expected_freq}' in: {text}"

    # ==================== SYMPTOM EXTRACTION TESTS ====================

    @pytest.mark.parametrize("text,expected_symptom", [
        ("Patient reports joint pain", "pain"),
        ("Morning stiffness for 2 hours", "stiffness"),
        ("Fatigue and malaise", "fatigue"),
        ("Joint swelling in hands", "swelling"),
        ("Reports fever and chills", "fever"),
    ])
    def test_extract_symptom(self, extractor, text, expected_symptom):
        """Test extraction of symptoms."""
        # Arrange - via parametrize

        # Act
        result = extractor.extract(text)

        # Assert
        assert_entity_found(
            result['entities'],
            'SYMPTOM',
            expected_symptom,
            f"Should find symptom '{expected_symptom}' in: {text}"
        )

    # ==================== DISEASE EXTRACTION TESTS ====================

    @pytest.mark.parametrize("text,expected_disease", [
        ("Patient with rheumatoid arthritis", "rheumatoid arthritis"),
        ("History of lupus", "lupus"),
        ("Diagnosed with RA", "RA"),
        ("Presents with psoriatic arthritis", "psoriatic arthritis"),
        ("Known Sjogren syndrome", "Sjogren"),
    ])
    def test_extract_disease(self, extractor, text, expected_disease):
        """Test extraction of diseases/conditions."""
        # Arrange - via parametrize

        # Act
        result = extractor.extract(text)

        # Assert
        assert_entity_found(
            result['entities'],
            'DISEASE',
            expected_disease,
            f"Should find disease '{expected_disease}' in: {text}"
        )


@pytest.mark.version_b
class TestMTLEntityExtractorNegation:
    """Tests for negation detection functionality."""

    # ==================== FIXTURES ====================

    @pytest.fixture(scope="class")
    def extractor(self):
        """Class-scoped extractor for negation tests."""
        from services.mtl_entity_extractor import MTLEntityExtractor
        return MTLEntityExtractor()

    # ==================== NEGATION DETECTION TESTS ====================

    @pytest.mark.parametrize("text,entity_text", [
        ("Patient denies fever", "fever"),
        ("No joint swelling observed", "swelling"),
        ("Denies chest pain", "pain"),
        ("Without morning stiffness", "stiffness"),
        ("Rules out lupus", "lupus"),
        ("Negative for rash", "rash"),
    ])
    def test_negation_detected(self, extractor, text, entity_text):
        """Test that negated symptoms are marked as negated."""
        # Arrange - via parametrize

        # Act
        result = extractor.extract(text)

        # Assert
        entity = find_entity(result['entities'], entity_text)
        assert entity is not None, f"Entity '{entity_text}' not found in: {text}"
        assert_negated(entity)

    @pytest.mark.parametrize("text,entity_text", [
        ("Patient has fever", "fever"),
        ("Joint swelling present", "swelling"),
        ("Reports chest pain", "pain"),
        ("Morning stiffness for 2 hours", "stiffness"),
        ("Diagnosed with lupus", "lupus"),
    ])
    def test_positive_not_negated(self, extractor, text, entity_text):
        """Test that positive findings are NOT marked as negated."""
        # Arrange - via parametrize

        # Act
        result = extractor.extract(text)

        # Assert
        entity = find_entity(result['entities'], entity_text)
        assert entity is not None, f"Entity '{entity_text}' not found in: {text}"
        assert_not_negated(entity)

    def test_mixed_negation_in_note(self, extractor):
        """Test handling of both negated and positive in same note."""
        # Arrange
        text = (
            "Patient has joint pain and morning stiffness. "
            "Denies fever, chills, or weight loss."
        )

        # Act
        result = extractor.extract(text)

        # Assert
        pain = find_entity(result['entities'], 'pain')
        if pain:
            assert_not_negated(pain)

        fever = find_entity(result['entities'], 'fever')
        if fever:
            assert_negated(fever)


@pytest.mark.version_b
class TestMTLEntityExtractorLabTests:
    """Tests for LAB_TEST extraction (regex fallback)."""

    # ==================== FIXTURES ====================

    @pytest.fixture(scope="class")
    def extractor(self):
        """Class-scoped extractor for lab tests."""
        from services.mtl_entity_extractor import MTLEntityExtractor
        return MTLEntityExtractor()

    # ==================== LAB TEST EXTRACTION TESTS ====================

    @pytest.mark.parametrize("text,expected_lab", [
        ("ESR 45 mm/hr", "ESR"),
        ("CRP 12 mg/dL", "CRP"),
        ("ANA positive", "ANA"),
        ("RF 85 IU/mL", "RF"),
        ("anti-CCP 250 units", "anti-CCP"),
        ("hemoglobin 12.5 g/dL", "hemoglobin"),
        ("WBC 8.2", "WBC"),
        ("platelet count normal", "platelet"),
    ])
    def test_extract_lab_test(self, extractor, text, expected_lab):
        """Test extraction of lab tests via regex fallback."""
        # Arrange - via parametrize

        # Act
        result = extractor.extract(text)

        # Assert
        assert_entity_found(
            result['entities'],
            'LAB_TEST',
            expected_lab,
            f"Should find lab test '{expected_lab}' in: {text}"
        )

    def test_lab_test_with_value(self, extractor):
        """Test lab test extraction includes numeric values."""
        # Arrange
        text = "Labs: ESR 45 mm/hr, CRP 2.8 mg/dL"

        # Act
        result = extractor.extract(text)

        # Assert
        labs = get_entities_by_type(result['entities'], 'LAB_TEST')
        assert len(labs) >= 2, "Should extract at least 2 lab tests"


@pytest.mark.version_b
class TestMTLEntityExtractorConfidence:
    """Tests for confidence scoring."""

    # ==================== FIXTURES ====================

    @pytest.fixture(scope="class")
    def extractor(self):
        """Class-scoped extractor for confidence tests."""
        from services.mtl_entity_extractor import MTLEntityExtractor
        return MTLEntityExtractor()

    # ==================== CONFIDENCE TESTS ====================

    def test_entities_have_confidence_scores(self, extractor):
        """Test all entities have confidence scores."""
        # Arrange
        text = "Patient on methotrexate for rheumatoid arthritis"

        # Act
        result = extractor.extract(text)

        # Assert
        for entity in result['entities']:
            assert 'confidence' in entity
            assert 0.0 <= entity['confidence'] <= 1.0

    def test_high_confidence_for_common_entities(self, extractor):
        """Test common medications have high confidence."""
        # Arrange
        text = "methotrexate 15mg weekly"

        # Act
        result = extractor.extract(text)

        # Assert
        med = find_entity(result['entities'], 'methotrexate')
        if med:
            assert_confidence_above(med, threshold=0.5)


@pytest.mark.version_b
@pytest.mark.slow
class TestMTLEntityExtractorPerformance:
    """Performance tests for Version B extractor."""

    # ==================== FIXTURES ====================

    @pytest.fixture(scope="class")
    def extractor(self):
        """Class-scoped extractor for performance tests."""
        from services.mtl_entity_extractor import MTLEntityExtractor
        return MTLEntityExtractor()

    # ==================== PERFORMANCE TESTS ====================

    def test_short_note_under_500ms(self, extractor):
        """Test short note extraction completes under 5000ms (CPU threshold)."""
        # Arrange
        text = "Patient on methotrexate 15mg weekly for RA."

        # Act
        result = extractor.extract(text)

        # Assert - increased threshold for CPU execution (GPU would be ~500ms)
        assert_processing_time_under(result, max_ms=5000)

    def test_medium_note_under_800ms(self, extractor):
        """Test medium note extraction completes under 8000ms (CPU threshold)."""
        # Arrange
        text = """
        Patient with rheumatoid arthritis on methotrexate 15mg weekly
        and hydroxychloroquine 200mg twice daily. Labs show ESR 45,
        CRP 2.8. Reports morning stiffness lasting 2 hours. Denies
        fever or weight loss. Joint exam shows tender and swollen
        MCPs bilaterally.
        """

        # Act
        result = extractor.extract(text)

        # Assert - increased threshold for CPU execution (GPU would be ~800ms)
        assert_processing_time_under(result, max_ms=8000)

    def test_long_note_under_2000ms(self, extractor, sample_rheumatology_full):
        """Test long clinical note completes under 15000ms (CPU threshold)."""
        # Arrange - done by fixture

        # Act
        result = extractor.extract(sample_rheumatology_full)

        # Assert - increased threshold for CPU execution (GPU would be ~2000ms)
        assert_processing_time_under(result, max_ms=15000)

    def test_repeated_extraction_consistent(self, extractor):
        """Test repeated extractions give consistent results."""
        # Arrange
        text = "Patient on methotrexate 15mg weekly"

        # Act
        results = [extractor.extract(text) for _ in range(3)]

        # Assert
        entity_counts = [len(r['entities']) for r in results]
        assert len(set(entity_counts)) == 1, "Entity counts should be consistent"


@pytest.mark.version_b
class TestMTLEntityExtractorEdgeCases:
    """Edge case tests for Version B extractor."""

    # ==================== FIXTURES ====================

    @pytest.fixture(scope="class")
    def extractor(self):
        """Class-scoped extractor for edge case tests."""
        from services.mtl_entity_extractor import MTLEntityExtractor
        return MTLEntityExtractor()

    # ==================== EDGE CASE TESTS ====================

    def test_special_characters(self, extractor):
        """Test handling of special characters."""
        # Arrange
        text = "Patient on anti-TNF therapy (adalimumab) for RA."

        # Act
        result = extractor.extract(text)

        # Assert
        assert_valid_extraction_result(result)

    def test_unicode_characters(self, extractor):
        """Test handling of unicode characters."""
        # Arrange
        text = "Patient reports pain level 8/10. Temperature 37.5°C."

        # Act
        result = extractor.extract(text)

        # Assert
        assert_valid_extraction_result(result)

    def test_very_long_text_truncation(self, extractor):
        """Test handling of text longer than max_length."""
        # Arrange
        base_text = "Patient on methotrexate for rheumatoid arthritis. "
        long_text = base_text * 200  # ~10,000 characters

        # Act
        result = extractor.extract(long_text)

        # Assert
        assert_valid_extraction_result(result)
        # Should still extract some entities from truncated text
        assert len(result['entities']) > 0

    def test_mixed_case_entities(self, extractor):
        """Test case-insensitive entity extraction."""
        # Arrange
        texts = [
            "METHOTREXATE 15mg",
            "Methotrexate 15mg",
            "methotrexate 15mg",
        ]

        # Act
        results = [extractor.extract(text) for text in texts]

        # Assert
        for result in results:
            assert_entity_found(result['entities'], 'MEDICATION', 'methotrexate')

    def test_abbreviations(self, extractor):
        """Test handling of medical abbreviations."""
        # Arrange
        text = "Pt on MTX and HCQ for RA. ESR elevated."

        # Act
        result = extractor.extract(text)

        # Assert
        # Should recognize common abbreviations
        assert len(result['entities']) >= 2
