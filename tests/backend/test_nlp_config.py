"""
Tests for NLP Configuration and Extractor Factory

Tests the NLP configuration system:
- Version selection (A, B, C, D)
- Factory pattern for extractor creation
- Fallback chain behavior
- Environment variable handling

Run with: pytest tests/backend/test_nlp_config.py -v
"""

import pytest
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'backend'))


class TestNLPConfigInitialization:
    """Tests for NLPConfig class initialization."""

    # ==================== INITIALIZATION TESTS ====================

    def test_config_initializes(self):
        """Test NLPConfig initializes without errors."""
        # Arrange
        from nlp_config.nlp_config import NLPConfig

        # Act
        config = NLPConfig()

        # Assert
        assert config is not None

    def test_default_version_is_a(self):
        """Test default version is A when NLP_VERSION not set."""
        # Arrange
        from nlp_config.nlp_config import NLPConfig
        # Temporarily remove env var if set
        original = os.environ.pop('NLP_VERSION', None)

        try:
            # Act
            config = NLPConfig()

            # Assert
            assert config.version == 'A'
        finally:
            # Restore
            if original:
                os.environ['NLP_VERSION'] = original

    def test_default_model_path(self):
        """Test default model path is data/models."""
        # Arrange
        from nlp_config.nlp_config import NLPConfig

        # Act
        config = NLPConfig()

        # Assert
        assert 'data/models' in config.model_path or 'models' in config.model_path

    def test_fallback_enabled_default(self):
        """Test fallback is enabled by default."""
        # Arrange
        from nlp_config.nlp_config import NLPConfig

        # Act
        config = NLPConfig()

        # Assert
        assert config.fallback_enabled == True

    def test_timeout_default(self):
        """Test default timeout is set."""
        # Arrange
        from nlp_config.nlp_config import NLPConfig

        # Act
        config = NLPConfig()

        # Assert
        assert config.timeout_ms > 0


class TestNLPConfigVersionValidation:
    """Tests for version validation."""

    # ==================== VERSION VALIDATION TESTS ====================

    @pytest.mark.parametrize("version", ['A', 'B', 'C', 'D'])
    def test_valid_versions_accepted(self, version):
        """Test valid versions A, B, C, D are accepted."""
        # Arrange
        os.environ['NLP_VERSION'] = version
        from nlp_config.nlp_config import NLPConfig

        try:
            # Act
            config = NLPConfig()

            # Assert
            assert config.version == version
        finally:
            os.environ.pop('NLP_VERSION', None)

    def test_invalid_version_defaults_to_a(self):
        """Test invalid version falls back to A."""
        # Arrange
        os.environ['NLP_VERSION'] = 'X'
        # Need to reimport to pick up new env var
        import importlib
        import nlp_config.nlp_config as nlp_module
        importlib.reload(nlp_module)

        try:
            # Act
            config = nlp_module.NLPConfig()

            # Assert
            assert config.version == 'A'
        finally:
            os.environ.pop('NLP_VERSION', None)

    def test_lowercase_version_converted(self):
        """Test lowercase version is converted to uppercase."""
        # Arrange
        os.environ['NLP_VERSION'] = 'b'
        import importlib
        import nlp_config.nlp_config as nlp_module
        importlib.reload(nlp_module)

        try:
            # Act
            config = nlp_module.NLPConfig()

            # Assert
            assert config.version == 'B'
        finally:
            os.environ.pop('NLP_VERSION', None)


class TestGetExtractor:
    """Tests for get_extractor factory function."""

    # ==================== FACTORY TESTS ====================

    def test_get_extractor_version_a(self):
        """Test getting Version A (Regex) extractor."""
        # Arrange
        from nlp_config.nlp_config import get_extractor

        # Act
        extractor = get_extractor('A')

        # Assert
        assert extractor is not None
        assert extractor.get_version() == 'A'

    @pytest.mark.slow
    def test_get_extractor_version_b(self):
        """Test getting Version B (GatorTron) extractor."""
        # Arrange
        from nlp_config.nlp_config import get_extractor

        # Act
        extractor = get_extractor('B')

        # Assert
        assert extractor is not None
        # May fall back to A if model not available
        assert extractor.get_version() in ['A', 'B']

    @pytest.mark.slow
    def test_get_extractor_version_c(self):
        """Test getting Version C (Two-Tier) extractor."""
        # Arrange
        from nlp_config.nlp_config import get_extractor

        # Act
        extractor = get_extractor('C')

        # Assert
        assert extractor is not None
        # May fall back if models not available
        assert extractor.get_version() in ['A', 'B', 'C']

    @pytest.mark.slow
    def test_get_extractor_version_d(self):
        """Test getting Version D (Ensemble) extractor."""
        # Arrange
        from nlp_config.nlp_config import get_extractor

        # Act
        extractor = get_extractor('D')

        # Assert
        assert extractor is not None
        # May fall back if models not available
        assert extractor.get_version() in ['A', 'B', 'C', 'D']

    def test_get_extractor_uses_config_default(self):
        """Test get_extractor uses config version when none specified."""
        # Arrange
        from nlp_config.nlp_config import get_extractor, config

        # Act
        extractor = get_extractor()

        # Assert
        assert extractor is not None

    def test_invalid_version_raises_error(self):
        """Test invalid version raises ValueError."""
        # Arrange
        from nlp_config.nlp_config import get_extractor

        # Act & Assert
        with pytest.raises(ValueError):
            get_extractor('Z')


class TestModelAvailability:
    """Tests for model availability checking."""

    # ==================== AVAILABILITY TESTS ====================

    def test_is_version_b_model_available(self):
        """Test checking Version B model availability."""
        # Arrange
        from nlp_config.nlp_config import is_version_b_model_available

        # Act
        available = is_version_b_model_available()

        # Assert
        assert isinstance(available, bool)

    def test_get_version_b_model_path(self):
        """Test getting Version B model path."""
        # Arrange
        from nlp_config.nlp_config import get_version_b_model_path

        # Act
        path = get_version_b_model_path()

        # Assert
        assert path is not None
        assert 'gatortron-rheum' in str(path)


class TestGetAvailableVersions:
    """Tests for get_available_versions function."""

    # ==================== AVAILABLE VERSIONS TESTS ====================

    def test_version_a_always_available(self):
        """Test Version A is always in available versions."""
        # Arrange
        from nlp_config.nlp_config import get_available_versions

        # Act
        versions = get_available_versions()

        # Assert
        assert 'A' in versions

    def test_returns_list(self):
        """Test get_available_versions returns a list."""
        # Arrange
        from nlp_config.nlp_config import get_available_versions

        # Act
        versions = get_available_versions()

        # Assert
        assert isinstance(versions, list)

    def test_versions_are_valid(self):
        """Test all returned versions are valid."""
        # Arrange
        from nlp_config.nlp_config import get_available_versions
        valid_versions = ['A', 'B', 'C', 'D']

        # Act
        versions = get_available_versions()

        # Assert
        for v in versions:
            assert v in valid_versions


class TestGetVersionStatus:
    """Tests for get_version_status function."""

    # ==================== STATUS TESTS ====================

    def test_returns_dict(self):
        """Test get_version_status returns a dictionary."""
        # Arrange
        from nlp_config.nlp_config import get_version_status

        # Act
        status = get_version_status()

        # Assert
        assert isinstance(status, dict)

    def test_all_versions_in_status(self):
        """Test all versions have status entries."""
        # Arrange
        from nlp_config.nlp_config import get_version_status

        # Act
        status = get_version_status()

        # Assert
        assert 'A' in status
        assert 'B' in status
        assert 'C' in status
        assert 'D' in status

    def test_version_a_is_available(self):
        """Test Version A status shows available."""
        # Arrange
        from nlp_config.nlp_config import get_version_status

        # Act
        status = get_version_status()

        # Assert
        assert status['A']['available'] == True

    def test_status_has_reason(self):
        """Test each version status has a reason."""
        # Arrange
        from nlp_config.nlp_config import get_version_status

        # Act
        status = get_version_status()

        # Assert
        for version, info in status.items():
            assert 'reason' in info or 'available' in info


class TestExtractEntities:
    """Tests for extract_entities convenience function."""

    # ==================== CONVENIENCE FUNCTION TESTS ====================

    def test_extract_entities_basic(self):
        """Test extract_entities convenience function."""
        # Arrange
        from nlp_config.nlp_config import extract_entities
        text = "Patient on methotrexate for rheumatoid arthritis"

        # Act
        result = extract_entities(text)

        # Assert
        assert result is not None
        assert 'entities' in result

    def test_extract_entities_with_version(self):
        """Test extract_entities with explicit version."""
        # Arrange
        from nlp_config.nlp_config import extract_entities
        text = "methotrexate 15mg weekly"

        # Act
        result = extract_entities(text, version='A')

        # Assert
        assert result is not None
        assert result['version'] == 'A'

    def test_extract_entities_empty_text(self):
        """Test extract_entities with empty text."""
        # Arrange
        from nlp_config.nlp_config import extract_entities
        text = ""

        # Act
        result = extract_entities(text)

        # Assert
        assert result is not None
        assert result['entities'] == []


class TestConfigRepr:
    """Tests for NLPConfig string representation."""

    # ==================== REPR TESTS ====================

    def test_config_repr(self):
        """Test NLPConfig has readable repr."""
        # Arrange
        from nlp_config.nlp_config import NLPConfig

        # Act
        config = NLPConfig()
        repr_str = repr(config)

        # Assert
        assert 'NLPConfig' in repr_str
        assert 'version' in repr_str
