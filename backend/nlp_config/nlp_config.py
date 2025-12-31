"""
NLP Configuration and Extractor Factory

This module handles:
- Loading NLP configuration from environment variables
- Factory pattern for creating appropriate extractor based on version
- Version selection logic
- Model availability checking

Environment Variables:
- NLP_VERSION: Which extractor version to use ('A', 'B', 'C', or 'D')
- NLP_MODEL_PATH: Path to store downloaded models (default: 'data/models')
- NLP_FALLBACK_ENABLED: Enable fallback chain for Version C (default: True)
- NLP_TIMEOUT_MS: Timeout for model inference in milliseconds (default: 2000)
"""

import os
from pathlib import Path
from typing import Optional
from services.base_extractor import BaseEntityExtractor


# Configuration defaults
DEFAULT_VERSION = 'A'  # Start with regex (no dependencies)
DEFAULT_MODEL_PATH = 'data/models'
DEFAULT_TIMEOUT_MS = 2000


class NLPConfig:
    """NLP system configuration"""

    def __init__(self):
        """Initialize configuration from environment variables"""
        self.version: str = os.getenv('NLP_VERSION', DEFAULT_VERSION).upper()
        self.model_path: str = os.getenv('NLP_MODEL_PATH', DEFAULT_MODEL_PATH)
        self.fallback_enabled: bool = os.getenv('NLP_FALLBACK_ENABLED', 'true').lower() == 'true'
        self.timeout_ms: int = int(os.getenv('NLP_TIMEOUT_MS', str(DEFAULT_TIMEOUT_MS)))

        # Validate version
        if self.version not in ['A', 'B', 'C', 'D']:
            print(f"Warning: Invalid NLP_VERSION '{self.version}', defaulting to '{DEFAULT_VERSION}'")
            self.version = DEFAULT_VERSION

    def __repr__(self) -> str:
        return (
            f"NLPConfig(version={self.version}, model_path={self.model_path}, "
            f"fallback_enabled={self.fallback_enabled}, timeout_ms={self.timeout_ms})"
        )


# Global configuration instance
config = NLPConfig()


def get_version_b_model_path() -> Path:
    """
    Get the expected path for the Version B (gatortron-rheum) model.

    Returns:
        Path to the model directory

    Example:
        >>> get_version_b_model_path()
        PosixPath('/path/to/project/data/models/gatortron-rheum')
    """
    # Get project root (3 levels up from this file: nlp_config -> backend -> root)
    project_root = Path(__file__).parent.parent.parent

    # Build model path
    model_path = Path(config.model_path)
    if not model_path.is_absolute():
        model_path = project_root / model_path

    return model_path / 'gatortron-rheum'


def is_version_b_model_available() -> bool:
    """
    Check if the Version B (gatortron-rheum) model is available.

    Checks for required files:
    - config.json (model configuration)
    - vocab.txt (tokenizer vocabulary)
    - pytorch_model.bin OR model.safetensors (model weights)

    Returns:
        True if model is ready to use, False otherwise

    Example:
        >>> if is_version_b_model_available():
        ...     extractor = get_extractor('B')
        ... else:
        ...     print("Model not ready, using Version A")
    """
    model_path = get_version_b_model_path()

    if not model_path.exists():
        return False

    # Check for required files
    has_config = (model_path / 'config.json').exists()
    has_vocab = (model_path / 'vocab.txt').exists()
    has_weights = (
        (model_path / 'pytorch_model.bin').exists() or
        (model_path / 'model.safetensors').exists()
    )

    return has_config and has_vocab and has_weights


def get_extractor(version: Optional[str] = None) -> BaseEntityExtractor:
    """
    Factory function to get appropriate extractor based on version.

    Args:
        version: Override version ('A', 'B', 'C', 'D'). If None, uses config.version

    Returns:
        BaseEntityExtractor instance for requested version

    Raises:
        ValueError: If version is invalid
        ImportError: If required dependencies for version are not installed

    Examples:
        >>> extractor = get_extractor()  # Uses NLP_VERSION from .env
        >>> extractor = get_extractor('A')  # Force Version A (regex)
        >>> extractor = get_extractor('B')  # Force Version B (transformers)
    """
    target_version = (version or config.version).upper()

    if target_version == 'A':
        from services.regex_entity_extractor import RegexEntityExtractor
        return RegexEntityExtractor()

    elif target_version == 'B':
        # Check if model exists before trying to load
        if not is_version_b_model_available():
            print(f"Warning: Version B model (gatortron-rheum) not found")
            print(f"Expected at: {get_version_b_model_path()}")
            print(f"Copy your trained model or use Version A for now")
            print(f"Falling back to Version A (regex)")
            from services.regex_entity_extractor import RegexEntityExtractor
            return RegexEntityExtractor()

        try:
            from services.mtl_entity_extractor import MTLEntityExtractor
            return MTLEntityExtractor(model_path=config.model_path)
        except ImportError as e:
            print(f"Error: Cannot load Version B - transformers not installed")
            print(f"Run: pip install transformers torch sentencepiece")
            print(f"Falling back to Version A (regex)")
            from services.regex_entity_extractor import RegexEntityExtractor
            return RegexEntityExtractor()
        except FileNotFoundError as e:
            print(f"Error: Version B model not found: {e}")
            print(f"Falling back to Version A (regex)")
            from services.regex_entity_extractor import RegexEntityExtractor
            return RegexEntityExtractor()

    elif target_version == 'C':
        try:
            from services.two_tier_extractor import TwoTierExtractor
            return TwoTierExtractor(
                model_path=config.model_path,
                timeout_ms=config.timeout_ms,
                fallback_enabled=config.fallback_enabled
            )
        except ImportError as e:
            print(f"Error: Version C not available - {e}")
            print(f"Falling back to Version B or A")
            return get_extractor('B')

    elif target_version == 'D':
        try:
            from services.ensemble_extractor import EnsembleExtractor
            extractor = EnsembleExtractor(timeout_ms=config.timeout_ms)
            available = extractor.get_available_extractors()
            print(f"Version D initialized with extractors: {available}")
            return extractor
        except ImportError as e:
            print(f"Error: Version D not available - {e}")
            print(f"Falling back to Version C or B or A")
            return get_extractor('C')
        except Exception as e:
            print(f"Error initializing Version D: {e}")
            print(f"Falling back to Version C or B or A")
            return get_extractor('C')

    else:
        raise ValueError(
            f"Invalid NLP version: {target_version}. Must be 'A', 'B', 'C', or 'D'"
        )


def get_available_versions() -> list[str]:
    """
    Get list of currently available extractor versions.

    Returns:
        List of version strings that are implemented, have dependencies installed,
        AND have required models available.

    Example:
        >>> get_available_versions()
        ['A']  # B requires model, C and D not yet implemented
    """
    available = ['A']  # Regex always available

    # Check if transformers is installed AND model is available for Version B
    try:
        import transformers
        import torch
        if is_version_b_model_available():
            available.append('B')
    except ImportError:
        pass

    # Check if Version C (Two-Tier) is implemented
    try:
        from services.two_tier_extractor import TwoTierExtractor
        available.append('C')
    except ImportError:
        pass

    # Check if Version D is implemented
    try:
        from services.ensemble_extractor import EnsembleExtractor
        available.append('D')
    except ImportError:
        pass

    return available


def get_version_status() -> dict:
    """
    Get detailed status of all extractor versions.

    Returns:
        Dictionary with status info for each version

    Example:
        >>> status = get_version_status()
        >>> print(status['B'])
        {'available': False, 'reason': 'Model not found', 'model_path': '...'}
    """
    status = {}

    # Version A - always available
    status['A'] = {
        'available': True,
        'reason': 'Regex-based (no dependencies)',
        'accuracy': '85% F1'
    }

    # Version B - check transformers AND model
    try:
        import transformers
        import torch
        transformers_ok = True
    except ImportError:
        transformers_ok = False

    model_available = is_version_b_model_available()
    model_path = str(get_version_b_model_path())

    if transformers_ok and model_available:
        status['B'] = {
            'available': True,
            'reason': 'GatorTron-Rheum model ready',
            'model_path': model_path,
            'accuracy': '85-90% F1'
        }
    elif not transformers_ok:
        status['B'] = {
            'available': False,
            'reason': 'transformers/torch not installed',
            'fix': 'pip install transformers torch sentencepiece'
        }
    else:
        status['B'] = {
            'available': False,
            'reason': 'Model not found',
            'model_path': model_path,
            'fix': f'Copy trained model to: {model_path}'
        }

    # Version C - Two-Tier extraction with UMLS normalization
    try:
        from services.two_tier_extractor import TwoTierExtractor
        extractor = TwoTierExtractor(model_path=config.model_path)
        extractor_status = extractor.get_status()
        status['C'] = {
            'available': True,
            'reason': 'Two-Tier extractor ready',
            'tier1': extractor_status.get('tier1_model', 'unknown'),
            'tier2': extractor_status.get('tier2_model', 'unknown'),
            'accuracy': '90-91% F1 (with UMLS normalization)'
        }
    except ImportError:
        status['C'] = {'available': False, 'reason': 'Two-Tier extractor not installed'}

    # Version D - Ensemble extractor
    try:
        from services.ensemble_extractor import EnsembleExtractor, is_ensemble_available
        if is_ensemble_available():
            extractor = EnsembleExtractor()
            available_extractors = extractor.get_available_extractors()
            status['D'] = {
                'available': True,
                'reason': 'Ensemble extractor ready',
                'extractors': available_extractors,
                'accuracy': '93-95% F1 (weighted ensemble with inference)'
            }
        else:
            status['D'] = {
                'available': False,
                'reason': 'Ensemble requires at least 2 extractors'
            }
    except ImportError:
        status['D'] = {'available': False, 'reason': 'Ensemble extractor not installed'}

    return status


# Convenience function for quick extractor access
def extract_entities(text: str, version: Optional[str] = None) -> dict:
    """
    Convenience function to extract entities in one line.

    Args:
        text: Medical note text
        version: Optional version override

    Returns:
        ExtractionResult dict

    Example:
        >>> result = extract_entities("Patient takes methotrexate 15mg weekly")
        >>> print(result['entities'])
    """
    extractor = get_extractor(version)
    return extractor.extract(text)


if __name__ == "__main__":
    # Test configuration
    print("=" * 60)
    print("NLP Configuration Status")
    print("=" * 60)
    print(f"\nConfig: {config}")
    print(f"\nAvailable versions: {get_available_versions()}")

    print("\n" + "-" * 60)
    print("Version Details:")
    print("-" * 60)
    for version, info in get_version_status().items():
        status_icon = "[OK]" if info['available'] else "[--]"
        print(f"\n  {status_icon} Version {version}:")
        for key, value in info.items():
            if key != 'available':
                print(f"      {key}: {value}")

    print("\n" + "-" * 60)
    print(f"Current extractor (NLP_VERSION={config.version}):")
    print("-" * 60)
    try:
        extractor = get_extractor()
        print(f"  Loaded: {extractor.get_model_name()} (Version {extractor.get_version()})")
    except Exception as e:
        print(f"  Error: {e}")

    print("\n" + "=" * 60)
