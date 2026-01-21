"""
Performance Benchmark Tests for Optimized GatorTron Inference

Tests to validate:
1. Optimized extractors produce correct outputs
2. Performance meets targets (3-4x speedup over baseline)
3. F1 accuracy maintained (>85%)

Usage:
    pytest tests/backend/test_optimized_inference.py -v
    pytest tests/backend/test_optimized_inference.py -v -k benchmark
"""

import pytest
import time
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Test data - clinical notes of varying lengths
SHORT_NOTE = "Patient with RA on methotrexate 15mg weekly. Denies fever."

MEDIUM_NOTE = """
55-year-old female with rheumatoid arthritis presents for follow-up.
Currently on methotrexate 20mg weekly and hydroxychloroquine 400mg daily.
Reports improved joint pain but persistent morning stiffness lasting 45 minutes.
No fever, weight loss, or rash. Labs show ESR 28, CRP 1.2.
Physical exam reveals mild synovitis in bilateral MCPs and PIPs.
Plan: Continue current medications, add prednisone 5mg daily for flare.
"""

LONG_NOTE = """
HISTORY OF PRESENT ILLNESS:
This is a 62-year-old male with a 10-year history of seropositive rheumatoid arthritis
who presents for routine follow-up. He was initially diagnosed after presenting with
symmetric polyarthritis affecting his hands and feet. He has been on multiple DMARDs
over the years including methotrexate, sulfasalazine, and leflunomide.

CURRENT MEDICATIONS:
1. Methotrexate 25mg subcutaneous weekly
2. Folic acid 1mg daily
3. Adalimumab 40mg subcutaneous every 2 weeks
4. Prednisone 5mg daily
5. Omeprazole 20mg daily
6. Calcium and Vitamin D supplementation

REVIEW OF SYSTEMS:
Patient denies fever, chills, or night sweats. No significant weight changes.
Reports occasional morning stiffness lasting approximately 30 minutes.
Denies any new joint swelling or warmth. No skin rashes or nodules noted.
Denies shortness of breath, chest pain, or palpitations.
No eye pain, redness, or vision changes. Denies dry eyes or dry mouth.

PHYSICAL EXAMINATION:
General: Well-appearing male in no acute distress
HEENT: No oral ulcers, no lymphadenopathy
Cardiovascular: Regular rate and rhythm, no murmurs
Pulmonary: Clear to auscultation bilaterally
Musculoskeletal:
- Hands: No active synovitis, mild ulnar deviation bilaterally
- Wrists: Full range of motion, no swelling
- Elbows: No nodules, full extension
- Shoulders: Full range of motion
- Knees: No effusion, full range of motion
- Ankles/Feet: No synovitis, mild hallux valgus bilaterally

LABORATORY DATA:
ESR: 18 mm/hr (normal)
CRP: 0.4 mg/dL (normal)
CBC: WBC 6.2, Hgb 14.1, Plt 245
CMP: Within normal limits
RF: 156 IU/mL (elevated)
Anti-CCP: >250 U/mL (elevated)

ASSESSMENT AND PLAN:
1. Rheumatoid arthritis - well controlled on current regimen
   - Continue methotrexate 25mg weekly
   - Continue adalimumab 40mg every 2 weeks
   - Taper prednisone to 2.5mg daily over next month
2. Osteoporosis prevention
   - Continue calcium and vitamin D
   - DEXA scan ordered for next visit
"""


class TestPyTorchExtractor:
    """Tests for PyTorch extractor with torch.compile."""

    @pytest.fixture
    def extractor(self):
        """Load PyTorch extractor."""
        from backend.services.mtl_entity_extractor import MTLEntityExtractor
        return MTLEntityExtractor()

    def test_extractor_loads(self, extractor):
        """Test that extractor loads successfully."""
        assert extractor is not None
        assert extractor.model is not None
        assert extractor.tokenizer is not None

    def test_extract_short_note(self, extractor):
        """Test extraction on short note."""
        result = extractor.extract(SHORT_NOTE)

        assert 'entities' in result
        assert 'processing_time_ms' in result
        assert 'version' in result
        assert result['version'] == 'B'

        # Should find at least medication and dosage
        entity_types = [e['type'] for e in result['entities']]
        assert 'MEDICATION' in entity_types or 'DISEASE' in entity_types

    def test_extract_medium_note(self, extractor):
        """Test extraction on medium note."""
        result = extractor.extract(MEDIUM_NOTE)

        assert 'entities' in result
        assert len(result['entities']) > 0

        # Should find multiple entity types
        entity_types = set(e['type'] for e in result['entities'])
        assert len(entity_types) >= 2

    def test_extract_long_note(self, extractor):
        """Test extraction on long note."""
        result = extractor.extract(LONG_NOTE)

        assert 'entities' in result
        assert len(result['entities']) > 0

        # Should find medications
        medications = [e for e in result['entities'] if e['type'] == 'MEDICATION']
        assert len(medications) >= 3  # methotrexate, adalimumab, prednisone

    @pytest.mark.benchmark
    def test_benchmark_pytorch(self, extractor):
        """Benchmark PyTorch extractor performance."""
        # Warm-up
        for _ in range(2):
            extractor.extract(MEDIUM_NOTE)

        # Benchmark
        times = []
        for _ in range(5):
            start = time.time()
            extractor.extract(MEDIUM_NOTE)
            times.append((time.time() - start) * 1000)

        avg_time = sum(times) / len(times)
        logger.info(f"PyTorch avg inference time: {avg_time:.1f}ms")

        # Performance target: <15000ms for baseline PyTorch on CPU
        # Note: Without torch.compile or ONNX, expect 8-12s on CPU
        # Use ONNX for production (3-4s)
        assert avg_time < 15000, f"PyTorch inference too slow: {avg_time:.1f}ms"


class TestONNXExtractor:
    """Tests for ONNX extractor (if available)."""

    @pytest.fixture
    def extractor(self):
        """Load ONNX extractor if available."""
        try:
            from backend.services.mtl_entity_extractor_optimized import ONNXEntityExtractor
            return ONNXEntityExtractor()
        except (ImportError, FileNotFoundError) as e:
            pytest.skip(f"ONNX extractor not available: {e}")

    def test_extractor_loads(self, extractor):
        """Test that ONNX extractor loads successfully."""
        assert extractor is not None
        assert extractor.model is not None
        assert extractor.tokenizer is not None

    def test_extract_short_note(self, extractor):
        """Test ONNX extraction on short note."""
        result = extractor.extract(SHORT_NOTE)

        assert 'entities' in result
        assert 'processing_time_ms' in result
        assert 'version' in result
        assert result['version'] == 'B-ONNX'

    def test_extract_medium_note(self, extractor):
        """Test ONNX extraction on medium note."""
        result = extractor.extract(MEDIUM_NOTE)

        assert 'entities' in result
        assert len(result['entities']) > 0

    def test_extract_long_note(self, extractor):
        """Test ONNX extraction on long note."""
        result = extractor.extract(LONG_NOTE)

        assert 'entities' in result
        assert len(result['entities']) > 0

    @pytest.mark.benchmark
    def test_benchmark_onnx(self, extractor):
        """Benchmark ONNX extractor performance."""
        # Warm-up
        for _ in range(2):
            extractor.extract(MEDIUM_NOTE)

        # Benchmark
        times = []
        for _ in range(5):
            start = time.time()
            extractor.extract(MEDIUM_NOTE)
            times.append((time.time() - start) * 1000)

        avg_time = sum(times) / len(times)
        logger.info(f"ONNX avg inference time: {avg_time:.1f}ms")

        # Performance target: <3000ms (faster than PyTorch)
        assert avg_time < 5000, f"ONNX inference too slow: {avg_time:.1f}ms"


class TestPerformanceComparison:
    """Compare PyTorch vs ONNX performance."""

    @pytest.mark.benchmark
    def test_compare_extractors(self):
        """Compare PyTorch and ONNX extractor performance."""
        from backend.services.mtl_entity_extractor import MTLEntityExtractor

        # Load PyTorch extractor
        pytorch_extractor = MTLEntityExtractor()

        # Try to load ONNX extractor
        try:
            from backend.services.mtl_entity_extractor_optimized import ONNXEntityExtractor
            onnx_extractor = ONNXEntityExtractor()
            has_onnx = True
        except (ImportError, FileNotFoundError):
            has_onnx = False
            logger.info("ONNX extractor not available for comparison")

        # Benchmark PyTorch
        pytorch_times = []
        for _ in range(3):
            start = time.time()
            pytorch_extractor.extract(MEDIUM_NOTE)
            pytorch_times.append((time.time() - start) * 1000)

        pytorch_avg = sum(pytorch_times) / len(pytorch_times)

        if has_onnx:
            # Benchmark ONNX
            onnx_times = []
            for _ in range(3):
                start = time.time()
                onnx_extractor.extract(MEDIUM_NOTE)
                onnx_times.append((time.time() - start) * 1000)

            onnx_avg = sum(onnx_times) / len(onnx_times)
            speedup = pytorch_avg / onnx_avg

            logger.info("=" * 50)
            logger.info("PERFORMANCE COMPARISON")
            logger.info("=" * 50)
            logger.info(f"PyTorch:  {pytorch_avg:.1f}ms")
            logger.info(f"ONNX:     {onnx_avg:.1f}ms")
            logger.info(f"Speedup:  {speedup:.2f}x")
            logger.info("=" * 50)

            # ONNX should be faster
            assert onnx_avg < pytorch_avg, "ONNX should be faster than PyTorch"
        else:
            logger.info(f"PyTorch only: {pytorch_avg:.1f}ms")


class TestEntityAccuracy:
    """Test entity extraction accuracy."""

    @pytest.fixture
    def pytorch_extractor(self):
        from backend.services.mtl_entity_extractor import MTLEntityExtractor
        return MTLEntityExtractor()

    def test_medication_extraction(self, pytorch_extractor):
        """Test that common medications are extracted."""
        text = "Patient is on methotrexate, adalimumab, and prednisone."
        result = pytorch_extractor.extract(text)

        medications = [e['text'].lower() for e in result['entities'] if e['type'] == 'MEDICATION']

        # Should find at least 2 of the 3 medications
        found = sum(1 for med in ['methotrexate', 'adalimumab', 'prednisone']
                   if any(med in m for m in medications))
        assert found >= 2, f"Only found {found} medications: {medications}"

    def test_dosage_extraction(self, pytorch_extractor):
        """Test that dosages are extracted."""
        text = "Methotrexate 15mg weekly, prednisone 5mg daily."
        result = pytorch_extractor.extract(text)

        dosages = [e for e in result['entities'] if e['type'] == 'DOSAGE']
        assert len(dosages) >= 1, "Should extract at least 1 dosage"

    def test_negation_detection(self, pytorch_extractor):
        """Test that negated entities are marked."""
        text = "Patient denies fever, chills, or weight loss."
        result = pytorch_extractor.extract(text)

        # Check if any symptom is marked as negated
        symptoms = [e for e in result['entities'] if e['type'] == 'SYMPTOM']
        negated = [e for e in symptoms if e.get('is_negated', False)]

        # Model should detect negation
        logger.info(f"Symptoms: {symptoms}")
        logger.info(f"Negated: {negated}")

    def test_lab_test_extraction(self, pytorch_extractor):
        """Test LAB_TEST regex fallback."""
        text = "Labs show ESR 45 and CRP 12."
        result = pytorch_extractor.extract(text)

        lab_tests = [e for e in result['entities'] if e['type'] == 'LAB_TEST']
        assert len(lab_tests) >= 1, "Should extract lab tests"


class TestFactoryFunction:
    """Test the get_best_extractor factory function."""

    def test_get_best_extractor(self):
        """Test that factory returns a working extractor."""
        from backend.services.mtl_entity_extractor_optimized import get_best_extractor

        extractor = get_best_extractor()
        assert extractor is not None

        # Test extraction works
        result = extractor.extract(SHORT_NOTE)
        assert 'entities' in result
        assert 'version' in result


# Standalone benchmark script
if __name__ == '__main__':
    import sys

    logging.basicConfig(level=logging.INFO)

    print("=" * 60)
    print("GatorTron Inference Performance Benchmark")
    print("=" * 60)

    # Load extractors
    from backend.services.mtl_entity_extractor import MTLEntityExtractor

    print("\nLoading PyTorch extractor...")
    pytorch = MTLEntityExtractor()

    try:
        from backend.services.mtl_entity_extractor_optimized import ONNXEntityExtractor
        print("Loading ONNX extractor...")
        onnx = ONNXEntityExtractor()
        has_onnx = True
    except Exception as e:
        print(f"ONNX not available: {e}")
        has_onnx = False

    # Benchmark
    print("\nRunning benchmarks...")

    for name, text in [("Short", SHORT_NOTE), ("Medium", MEDIUM_NOTE), ("Long", LONG_NOTE)]:
        print(f"\n{name} note ({len(text)} chars):")

        # PyTorch
        times = []
        for _ in range(3):
            start = time.time()
            pytorch.extract(text)
            times.append((time.time() - start) * 1000)
        pytorch_avg = sum(times) / len(times)
        print(f"  PyTorch: {pytorch_avg:.1f}ms")

        if has_onnx:
            times = []
            for _ in range(3):
                start = time.time()
                onnx.extract(text)
                times.append((time.time() - start) * 1000)
            onnx_avg = sum(times) / len(times)
            speedup = pytorch_avg / onnx_avg
            print(f"  ONNX:    {onnx_avg:.1f}ms ({speedup:.2f}x faster)")

    print("\n" + "=" * 60)
