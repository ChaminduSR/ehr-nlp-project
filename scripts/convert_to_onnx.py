"""
ONNX Conversion Script for GatorTron-Rheum Model

Converts PyTorch model to ONNX format for optimized CPU inference.
Supports AVX2 optimization (works on Intel Core i3/i5/i7 2015+).

Expected Results:
- Inference speed: 1.5-1.8x faster than PyTorch on CPU
- Model size: Similar to original (~1.4GB) or quantized INT8 (~350MB)
- Portable: Copy .onnx file to any machine with onnxruntime

Usage:
    python scripts/convert_to_onnx.py
    python scripts/convert_to_onnx.py --input data/models/gatortron-rheum --output data/models/gatortron-rheum-onnx
    python scripts/convert_to_onnx.py --quantize  # Apply INT8 quantization to ONNX model

Requirements:
    pip install onnx onnxruntime optimum[onnxruntime]
"""

import os
import sys
import time
import argparse
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def check_dependencies():
    """Check if required packages are installed."""
    missing = []

    try:
        import onnx
    except ImportError:
        missing.append('onnx')

    try:
        import onnxruntime
    except ImportError:
        missing.append('onnxruntime')

    try:
        from optimum.onnxruntime import ORTModelForTokenClassification
    except ImportError:
        missing.append('optimum[onnxruntime]')

    if missing:
        logger.error(f"Missing dependencies: {', '.join(missing)}")
        logger.error(f"Install with: pip install {' '.join(missing)}")
        return False

    return True


def convert_to_onnx(input_path: str, output_path: str, quantize: bool = False) -> dict:
    """
    Convert GatorTron model to ONNX format.

    Args:
        input_path: Path to original PyTorch model
        output_path: Path to save ONNX model
        quantize: Apply INT8 quantization to ONNX model

    Returns:
        Dictionary with conversion metrics
    """
    from optimum.onnxruntime import ORTModelForTokenClassification
    from optimum.onnxruntime.configuration import AutoQuantizationConfig
    from transformers import AutoTokenizer

    logger.info(f"Loading model from: {input_path}")

    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(input_path)

    # Create output directory
    os.makedirs(output_path, exist_ok=True)

    # Convert to ONNX using Optimum
    logger.info("Converting to ONNX format...")
    start_time = time.time()

    # Export to ONNX
    ort_model = ORTModelForTokenClassification.from_pretrained(
        input_path,
        export=True  # Convert PyTorch to ONNX
    )

    conversion_time = time.time() - start_time
    logger.info(f"ONNX conversion completed in {conversion_time:.1f}s")

    # Save ONNX model
    ort_model.save_pretrained(output_path)
    tokenizer.save_pretrained(output_path)

    # Get model size
    onnx_model_path = os.path.join(output_path, 'model.onnx')
    if os.path.exists(onnx_model_path):
        model_size_mb = os.path.getsize(onnx_model_path) / (1024 * 1024)
    else:
        # Try alternative names
        for name in ['model.onnx', 'encoder_model.onnx', 'decoder_model.onnx']:
            path = os.path.join(output_path, name)
            if os.path.exists(path):
                model_size_mb = os.path.getsize(path) / (1024 * 1024)
                break
        else:
            model_size_mb = 0

    logger.info(f"ONNX model size: {model_size_mb:.1f} MB")

    # Apply quantization if requested
    if quantize:
        logger.info("Applying INT8 quantization to ONNX model...")
        quantized_output = output_path + "-int8"
        os.makedirs(quantized_output, exist_ok=True)

        from optimum.onnxruntime import ORTQuantizer

        quantizer = ORTQuantizer.from_pretrained(output_path)

        # Configure quantization for AVX2 CPUs
        qconfig = AutoQuantizationConfig.avx2(is_static=False)  # Dynamic quantization

        quantizer.quantize(
            save_dir=quantized_output,
            quantization_config=qconfig
        )

        # Copy tokenizer to quantized output
        tokenizer.save_pretrained(quantized_output)

        # Update output path to quantized version
        output_path = quantized_output

        # Get quantized model size
        for name in ['model.onnx', 'model_quantized.onnx']:
            path = os.path.join(quantized_output, name)
            if os.path.exists(path):
                model_size_mb = os.path.getsize(path) / (1024 * 1024)
                break

        logger.info(f"Quantized ONNX model size: {model_size_mb:.1f} MB")

    # Benchmark inference
    logger.info("Benchmarking ONNX inference...")

    # Load ONNX model for inference
    ort_model = ORTModelForTokenClassification.from_pretrained(output_path)

    test_text = "Patient presents with joint swelling and morning stiffness. Currently on methotrexate 15mg weekly."
    inputs = tokenizer(test_text, return_tensors='pt', truncation=True, max_length=512, padding='max_length')

    # Warm-up
    for _ in range(3):
        _ = ort_model(**inputs)

    # Timed runs
    num_runs = 10
    start_time = time.time()
    for _ in range(num_runs):
        _ = ort_model(**inputs)
    avg_inference_time = (time.time() - start_time) / num_runs * 1000

    results = {
        'model_size_mb': model_size_mb,
        'conversion_time_s': conversion_time,
        'avg_inference_time_ms': avg_inference_time,
        'quantized': quantize,
        'output_path': output_path
    }

    logger.info("=" * 50)
    logger.info("ONNX CONVERSION RESULTS")
    logger.info("=" * 50)
    logger.info(f"Model size:       {model_size_mb:.1f} MB")
    logger.info(f"Inference time:   {avg_inference_time:.1f} ms")
    logger.info(f"Quantized:        {quantize}")
    logger.info(f"Output path:      {output_path}")
    logger.info("=" * 50)

    return results


def validate_onnx_model(model_path: str) -> bool:
    """
    Validate ONNX model loads and produces valid outputs.

    Args:
        model_path: Path to ONNX model directory

    Returns:
        True if validation passes
    """
    from optimum.onnxruntime import ORTModelForTokenClassification
    from transformers import AutoTokenizer

    logger.info(f"Validating ONNX model at: {model_path}")

    try:
        # Load model and tokenizer
        model = ORTModelForTokenClassification.from_pretrained(model_path)
        tokenizer = AutoTokenizer.from_pretrained(model_path)

        # Test inference
        test_text = "Patient on adalimumab for rheumatoid arthritis."
        inputs = tokenizer(test_text, return_tensors='pt', truncation=True, max_length=512)

        outputs = model(**inputs)

        # Check outputs
        assert outputs.logits is not None
        assert outputs.logits.shape[0] == 1

        logger.info("Validation PASSED: ONNX model loads and produces valid outputs")
        return True

    except Exception as e:
        logger.error(f"Validation FAILED: {e}")
        return False


def compare_pytorch_onnx(pytorch_path: str, onnx_path: str) -> dict:
    """
    Compare PyTorch and ONNX model inference times.

    Args:
        pytorch_path: Path to PyTorch model
        onnx_path: Path to ONNX model

    Returns:
        Comparison metrics
    """
    import torch
    from transformers import AutoModelForTokenClassification, AutoTokenizer
    from optimum.onnxruntime import ORTModelForTokenClassification

    logger.info("Comparing PyTorch vs ONNX inference...")

    # Load models
    tokenizer = AutoTokenizer.from_pretrained(pytorch_path)
    pytorch_model = AutoModelForTokenClassification.from_pretrained(pytorch_path)
    pytorch_model.eval()

    onnx_model = ORTModelForTokenClassification.from_pretrained(onnx_path)

    # Test text
    test_text = "Patient presents with joint swelling and morning stiffness. Currently on methotrexate 15mg weekly. Denies fever or weight loss."
    inputs = tokenizer(test_text, return_tensors='pt', truncation=True, max_length=512, padding='max_length')

    # Benchmark PyTorch
    num_runs = 10

    # Warm-up
    for _ in range(3):
        with torch.no_grad():
            _ = pytorch_model(**inputs)

    start_time = time.time()
    for _ in range(num_runs):
        with torch.no_grad():
            _ = pytorch_model(**inputs)
    pytorch_time = (time.time() - start_time) / num_runs * 1000

    # Benchmark ONNX
    for _ in range(3):
        _ = onnx_model(**inputs)

    start_time = time.time()
    for _ in range(num_runs):
        _ = onnx_model(**inputs)
    onnx_time = (time.time() - start_time) / num_runs * 1000

    speedup = pytorch_time / onnx_time

    logger.info("=" * 50)
    logger.info("PYTORCH vs ONNX COMPARISON")
    logger.info("=" * 50)
    logger.info(f"PyTorch time:     {pytorch_time:.1f} ms")
    logger.info(f"ONNX time:        {onnx_time:.1f} ms")
    logger.info(f"Speedup:          {speedup:.2f}x")
    logger.info("=" * 50)

    return {
        'pytorch_time_ms': pytorch_time,
        'onnx_time_ms': onnx_time,
        'speedup': speedup
    }


def main():
    parser = argparse.ArgumentParser(description='Convert GatorTron-Rheum to ONNX format')
    parser.add_argument(
        '--input',
        type=str,
        default='data/models/gatortron-rheum',
        help='Path to original PyTorch model'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='data/models/gatortron-rheum-onnx',
        help='Path to save ONNX model'
    )
    parser.add_argument(
        '--quantize',
        action='store_true',
        help='Apply INT8 quantization to ONNX model (AVX2 optimized)'
    )
    parser.add_argument(
        '--validate',
        action='store_true',
        help='Validate ONNX model after conversion'
    )
    parser.add_argument(
        '--compare',
        action='store_true',
        help='Compare PyTorch vs ONNX inference speed'
    )

    args = parser.parse_args()

    # Check dependencies
    if not check_dependencies():
        logger.error("Please install missing dependencies first.")
        sys.exit(1)

    # Convert paths
    input_path = str(project_root / args.input)
    output_path = str(project_root / args.output)

    # Check input exists
    if not os.path.exists(input_path):
        logger.error(f"Input model not found: {input_path}")
        sys.exit(1)

    # Convert
    results = convert_to_onnx(input_path, output_path, quantize=args.quantize)

    # Validate if requested
    if args.validate:
        final_output = results['output_path']
        if not validate_onnx_model(final_output):
            logger.error("ONNX model validation failed!")
            sys.exit(1)

    # Compare if requested
    if args.compare:
        final_output = results['output_path']
        compare_pytorch_onnx(input_path, final_output)

    logger.info("ONNX conversion complete!")
    return results


if __name__ == '__main__':
    main()
