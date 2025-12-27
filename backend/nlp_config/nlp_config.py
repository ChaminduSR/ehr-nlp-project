"""
NLP Configuration and Extractor Factory

This module handles:
- Loading NLP configuration from environment variables
- Factory pattern for creating appropriate extractor based on version
- Version selection logic

Environment Variables:
- NLP_VERSION: Which extractor version to use ('A', 'B', 'C', or 'D')
- NLP_MODEL_PATH: Path to store downloaded models (default: 'data/models')
- NLP_FALLBACK_ENABLED: Enable fallback chain for Version C (default: True)
- NLP_TIMEOUT_MS: Timeout for model inference in milliseconds (default: 2000)
"""

import os
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
        try:
            from services.mtl_entity_extractor import MTLEntityExtractor
            return MTLEntityExtractor(model_path=config.model_path)
        except ImportError as e:
            print(f"Error: Cannot load Version B - transformers not installed")
            print(f"Run: pip install transformers torch sentencepiece")
            print(f"Falling back to Version A (regex)")
            from services.regex_entity_extractor import RegexEntityExtractor
            return RegexEntityExtractor()

    elif target_version == 'C':
        try:
            from services.fallback_manager import FallbackManager
            return FallbackManager()
        except ImportError:
            print(f"Error: Version C not yet implemented")
            print(f"Falling back to Version B or A")
            return get_extractor('B')

    elif target_version == 'D':
        try:
            from services.ensemble_extractor import EnsembleExtractor
            return EnsembleExtractor()
        except ImportError:
            print(f"Error: Version D not yet implemented")
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
        List of version strings that are implemented and have dependencies installed

    Example:
        >>> get_available_versions()
        ['A', 'B']  # C and D not yet implemented
    """
    available = ['A']  # Regex always available

    # Check if transformers is installed for Version B
    try:
        import transformers
        import torch
        available.append('B')
    except ImportError:
        pass

    # Check if Version C is implemented
    try:
        from services.fallback_manager import FallbackManager
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
    print("NLP Configuration:")
    print(config)
    print(f"\nAvailable versions: {get_available_versions()}")
    print(f"\nCurrent extractor: {get_extractor()}")
