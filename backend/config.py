"""
Configuration management for EHR-NLP application.

Handles environment variables and app configuration.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Base configuration."""

    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    DEBUG = ENVIRONMENT == "development"

    # NLP Settings
    SPACY_MODEL = os.getenv("SPACY_MODEL", "en_core_sci_md")
    MIN_CONFIDENCE = float(os.getenv("MIN_CONFIDENCE", "0.7"))

    # API Settings
    API_PORT = int(os.getenv("API_PORT", "5000"))
    API_HOST = os.getenv("API_HOST", "localhost")

    # Frontend Settings
    USE_VITE = os.getenv("USE_VITE", "False").lower() == "true"


class DevelopmentConfig(Config):
    """Development environment configuration."""
    DEBUG = True


class ProductionConfig(Config):
    """Production environment configuration."""
    DEBUG = False


# Configuration dictionary
config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
}


def get_config():
    """Get configuration based on environment."""
    env = os.getenv("ENVIRONMENT", "development")
    return config.get(env, DevelopmentConfig)
