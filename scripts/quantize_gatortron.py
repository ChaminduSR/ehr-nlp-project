"""
INT8 Dynamic Quantization for GatorTron-Rheum Model

Applies PyTorch dynamic quantization to reduce model size and improve CPU inference speed.
Works on ANY CPU (no AVX-512 required).

Expected Results:
- Model size: 1.4GB → ~350MB (4x reduction)
- Inference speed: 1.5-2x faster on CPU
- Accuracy: <1% F1 drop (typically maintains 85%+ F1)

Usage:
    python scripts/quantize_gatortron.py
    python scripts/quantize_gatortron.py --input data/models/gatortron-rheum --output data/models/gatortron-rheum-int8
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

import torch
from transformers import AutoModelForTokenClassification, AutoTokenizer

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def quantize_model(input_path: str, output_path: str) -> dict:
    """
    Apply INT8 dynamic quantization to GatorTron model.

    Args:
        input_path: Path to original model directory
        output_path: Path to save quantized model

    Returns:
        Dictionary with quantization metrics
    """
    logger.info(f"Loading model from: {input_path}")

    # Load model and tokenizer
    model = AutoModelForTokenClassification.from_pretrained(input_path)
    tokenizer = AutoTokenizer.from_pretrained(input_path)

    # Get original model size
    original_size = sum(p.numel() * p.element_size() for p in model.parameters())
    original_size_mb = original_size / (1024 * 1024)
    logger.info(f"Original model size: {original_size_mb:.1f} MB")
    logger.info(f"Original parameters: {sum(p.numel() for p in model.parameters()) / 1e6:.1f}M")

    # Set model to evaluation mode
    model.eval()

    # Apply dynamic quantization
    # Only quantize Linear layers (most compute-intensive)
    logger.info("Applying INT8 dynamic quantization...")
    start_time = time.time()

    quantized_model = torch.quantization.quantize_dynamic(
        model,
        {torch.nn.Linear},  # Quantize all Linear layers
        dtype=torch.qint8
    )

    quantization_time = time.time() - start_time
    logger.info(f"Quantization completed in {quantization_time:.1f}s")

    # Create output directory
    os.makedirs(output_path, exist_ok=True)

    # Save quantized model
    logger.info(f"Saving quantized model to: {output_path}")

    # Save the state dict (quantized weights)
    torch.save(quantized_model.state_dict(), os.path.join(output_path, 'pytorch_model.bin'))

    # Copy config and tokenizer files
    model.config.save_pretrained(output_path)
    tokenizer.save_pretrained(output_path)

    # Calculate quantized model size (approximate from saved file)
    saved_model_path = os.path.join(output_path, 'pytorch_model.bin')
    quantized_size_mb = os.path.getsize(saved_model_path) / (1024 * 1024)

    # Benchmark inference speed
    logger.info("Benchmarking inference speed...")
    test_text = "Patient presents with joint swelling and morning stiffness. Currently on methotrexate 15mg weekly."

    # Tokenize
    inputs = tokenizer(
        test_text,
        return_tensors='pt',
        truncation=True,
        max_length=512,
        padding='max_length'
    )

    # Warm-up runs
    for _ in range(3):
        with torch.no_grad():
            _ = quantized_model(**inputs)

    # Timed runs
    num_runs = 10
    start_time = time.time()
    for _ in range(num_runs):
        with torch.no_grad():
            _ = quantized_model(**inputs)
    avg_inference_time = (time.time() - start_time) / num_runs * 1000  # ms

    logger.info(f"Average inference time: {avg_inference_time:.1f}ms")

    # Results summary
    results = {
        'original_size_mb': original_size_mb,
        'quantized_size_mb': quantized_size_mb,
        'size_reduction': f"{original_size_mb / quantized_size_mb:.1f}x",
        'quantization_time_s': quantization_time,
        'avg_inference_time_ms': avg_inference_time,
        'output_path': output_path
    }

    logger.info("=" * 50)
    logger.info("QUANTIZATION RESULTS")
    logger.info("=" * 50)
    logger.info(f"Original size:    {original_size_mb:.1f} MB")
    logger.info(f"Quantized size:   {quantized_size_mb:.1f} MB")
    logger.info(f"Size reduction:   {results['size_reduction']}")
    logger.info(f"Inference time:   {avg_inference_time:.1f} ms")
    logger.info(f"Output path:      {output_path}")
    logger.info("=" * 50)

    return results


def validate_quantized_model(model_path: str) -> bool:
    """
    Validate that quantized model loads and runs correctly.

    Args:
        model_path: Path to quantized model

    Returns:
        True if validation passes
    """
    logger.info(f"Validating quantized model at: {model_path}")

    try:
        # Load tokenizer (should work normally)
        tokenizer = AutoTokenizer.from_pretrained(model_path)

        # Load original model structure
        model = AutoModelForTokenClassification.from_pretrained(model_path)
        model.eval()

        # Re-apply quantization (state dict has quantized weights)
        quantized_model = torch.quantization.quantize_dynamic(
            model,
            {torch.nn.Linear},
            dtype=torch.qint8
        )

        # Load quantized weights
        state_dict = torch.load(os.path.join(model_path, 'pytorch_model.bin'))
        quantized_model.load_state_dict(state_dict)

        # Test inference
        test_text = "Patient on adalimumab for rheumatoid arthritis."
        inputs = tokenizer(test_text, return_tensors='pt', truncation=True, max_length=512)

        with torch.no_grad():
            outputs = quantized_model(**inputs)

        # Check outputs
        assert outputs.logits is not None
        assert outputs.logits.shape[0] == 1  # Batch size
        assert outputs.logits.shape[2] == model.config.num_labels  # Num labels

        logger.info("Validation PASSED: Model loads and produces valid outputs")
        return True

    except Exception as e:
        logger.error(f"Validation FAILED: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description='Quantize GatorTron-Rheum model to INT8')
    parser.add_argument(
        '--input',
        type=str,
        default='data/models/gatortron-rheum',
        help='Path to original model directory'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='data/models/gatortron-rheum-int8',
        help='Path to save quantized model'
    )
    parser.add_argument(
        '--validate',
        action='store_true',
        help='Validate quantized model after creation'
    )

    args = parser.parse_args()

    # Convert to absolute paths
    input_path = str(project_root / args.input)
    output_path = str(project_root / args.output)

    # Check input exists
    if not os.path.exists(input_path):
        logger.error(f"Input model not found: {input_path}")
        sys.exit(1)

    # Quantize
    results = quantize_model(input_path, output_path)

    # Validate if requested
    if args.validate:
        if not validate_quantized_model(output_path):
            logger.error("Quantized model validation failed!")
            sys.exit(1)

    logger.info("Quantization complete!")
    return results


if __name__ == '__main__':
    main()
