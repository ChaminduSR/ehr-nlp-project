"""
Model Downloader Utility for Version B

Downloads and caches pre-trained transformer models for NER.
Supports multiple model backends (BERT, DistilBERT, Bio_ClinicalBERT).
"""

import os
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class ModelDownloader:
    """Utility for downloading and caching transformer models"""

    # Supported pre-trained NER models
    MODELS = {
        'bert-base-ner': {
            'name': 'dslim/bert-base-NER',
            'description': 'General-purpose BERT NER model (PER, LOC, ORG, MISC)',
            'size': '438MB',
            'accuracy': 'High (CoNLL-2003 F1: 0.953)'
        },
        'bio-clinical-bert': {
            'name': 'emilyalsentzer/Bio_ClinicalBERT',
            'description': 'Clinical domain pre-trained BERT (needs NER fine-tuning)',
            'size': '420MB',
            'accuracy': 'Domain-specific (clinical text understanding)'
        },
        'distilbert-ner': {
            'name': 'Davlan/distilbert-base-multilingual-cased-ner-hrl',
            'description': 'Faster DistilBERT NER model',
            'size': '260MB',
            'accuracy': 'Good (faster inference, slightly lower accuracy)'
        },
        'gatortron-rheum': {
            'name': 'LOCAL',  # Custom trained, not from HuggingFace
            'description': 'Custom-trained GatorTron for rheumatology NER (345M params, V2.1)',
            'size': '~1.3GB',
            'accuracy': 'High (85-90% F1 on clinical NER)',
            'local_only': True,
            'labels': ['O', 'B-DRUG', 'I-DRUG', 'B-SYMPTOM', 'I-SYMPTOM', 'B-DOSAGE',
                      'I-DOSAGE', 'B-FREQUENCY', 'I-FREQUENCY', 'B-NEGATION',
                      'I-NEGATION', 'B-CONDITION', 'I-CONDITION']
        },
        'sapbert': {
            'name': 'cambridgeltl/SapBERT-from-PubMedBERT-fulltext',
            'description': 'Entity linking + UMLS normalization (Version C Tier 2)',
            'size': '~440MB',
            'accuracy': 'High (Acc@1=0.81 on entity linking)',
            'use_case': 'Maps medical terms to UMLS concept IDs'
        }
    }

    def __init__(self, cache_dir: str = 'data/models'):
        """
        Initialize model downloader.

        Args:
            cache_dir: Directory to cache downloaded models (relative to project root)
        """
        # Get project root (2 levels up from this file: backend/services -> backend -> root)
        project_root = Path(__file__).parent.parent.parent

        # Convert to absolute path if relative path provided
        if not Path(cache_dir).is_absolute():
            self.cache_dir = project_root / cache_dir
        else:
            self.cache_dir = Path(cache_dir)

        # Create directory if it doesn't exist
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Model cache directory: {self.cache_dir.absolute()}")

    def download_model(
        self,
        model_key: str = 'bert-base-ner',
        force_download: bool = False
    ) -> str:
        """
        Download and cache a pre-trained model.

        Args:
            model_key: Key from MODELS dict (e.g., 'bert-base-ner')
            force_download: Force re-download even if cached

        Returns:
            Path to cached model directory

        Raises:
            ValueError: If model_key not recognized
            ImportError: If transformers library not installed

        Example:
            >>> downloader = ModelDownloader()
            >>> model_path = downloader.download_model('bert-base-ner')
            >>> print(f"Model cached at: {model_path}")
        """
        if model_key not in self.MODELS:
            raise ValueError(
                f"Unknown model: {model_key}. "
                f"Available models: {', '.join(self.MODELS.keys())}"
            )

        try:
            from transformers import (
                AutoModel,
                AutoModelForTokenClassification,
                AutoTokenizer
            )
        except ImportError:
            raise ImportError(
                "transformers library not installed. "
                "Run: pip install transformers torch sentencepiece"
            )

        model_info = self.MODELS[model_key]
        model_name = model_info['name']
        save_path = self.cache_dir / model_key

        # Check if this is a local-only model (custom trained)
        if model_info.get('local_only', False):
            if save_path.exists():
                logger.info(f"Local model '{model_key}' found at {save_path}")
                return str(save_path)
            else:
                raise FileNotFoundError(
                    f"Local model '{model_key}' not found at: {save_path}\n"
                    f"This is a custom-trained model that must be copied manually.\n"
                    f"Copy your trained model to: {save_path}\n"
                    f"Expected files: pytorch_model.bin (or model.safetensors), config.json, vocab.txt"
                )

        # Check if model already cached
        if save_path.exists() and not force_download:
            logger.info(f"Model '{model_key}' already cached at {save_path}")
            return str(save_path)

        logger.info(f"Downloading {model_info['description']}...")
        logger.info(f"Model: {model_name}")
        logger.info(f"Size: {model_info['size']}")

        try:
            # Download model and tokenizer
            # Use AutoModel for embedding models (like SapBERT), AutoModelForTokenClassification for NER
            if model_info.get('use_case') == 'Maps medical terms to UMLS concept IDs':
                # SapBERT and other embedding models
                model = AutoModel.from_pretrained(model_name)
            else:
                # NER models
                model = AutoModelForTokenClassification.from_pretrained(model_name)

            tokenizer = AutoTokenizer.from_pretrained(model_name)

            # Save to cache directory
            save_path.mkdir(parents=True, exist_ok=True)
            model.save_pretrained(str(save_path))
            tokenizer.save_pretrained(str(save_path))

            logger.info(f"Model downloaded and cached at: {save_path}")
            return str(save_path)

        except Exception as e:
            logger.error(f"Failed to download model '{model_key}': {e}")
            raise

    def list_models(self) -> dict:
        """
        List all available models with descriptions.

        Returns:
            Dictionary of model info

        Example:
            >>> downloader = ModelDownloader()
            >>> models = downloader.list_models()
            >>> for key, info in models.items():
            ...     print(f"{key}: {info['description']}")
        """
        return self.MODELS.copy()

    def is_model_cached(self, model_key: str) -> bool:
        """
        Check if model is already cached locally.

        Args:
            model_key: Model identifier

        Returns:
            True if model is cached, False otherwise
        """
        if model_key not in self.MODELS:
            return False

        model_path = self.cache_dir / model_key
        return model_path.exists()

    def get_model_path(self, model_key: str) -> Optional[str]:
        """
        Get path to cached model.

        Args:
            model_key: Model identifier

        Returns:
            Path to cached model or None if not cached
        """
        if not self.is_model_cached(model_key):
            return None

        return str(self.cache_dir / model_key)


def download_default_model() -> str:
    """
    Convenience function to download default NER model (bert-base-ner).

    Returns:
        Path to cached model

    Example:
        >>> model_path = download_default_model()
        >>> print(f"Default model ready at: {model_path}")
    """
    downloader = ModelDownloader()
    return downloader.download_model('bert-base-ner')


if __name__ == "__main__":
    # CLI interface for downloading models
    import sys

    print("Model Downloader - Version B NER Models")
    print("=" * 50)

    downloader = ModelDownloader()

    # List available models
    print("\nAvailable Models:")
    for key, info in downloader.list_models().items():
        cached = "✓ CACHED" if downloader.is_model_cached(key) else "  (not downloaded)"
        print(f"\n  {key} {cached}")
        print(f"    Description: {info['description']}")
        print(f"    Size: {info['size']}")
        print(f"    Accuracy: {info['accuracy']}")

    # Download default model if requested
    if len(sys.argv) > 1 and sys.argv[1] == 'download':
        model_key = sys.argv[2] if len(sys.argv) > 2 else 'bert-base-ner'

        print(f"\n{'=' * 50}")
        print(f"Downloading model: {model_key}")
        print(f"{'=' * 50}\n")

        try:
            model_path = downloader.download_model(model_key)
            print(f"\n✓ Success! Model cached at: {model_path}")
        except Exception as e:
            print(f"\n✗ Error: {e}")
            sys.exit(1)
    else:
        print(f"\n{'=' * 50}")
        print("Usage:")
        print("  python model_downloader.py download [model_key]")
        print("\nExample:")
        print("  python model_downloader.py download bert-base-ner")
        print(f"{'=' * 50}\n")
