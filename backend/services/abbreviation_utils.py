"""
Medical Abbreviation Expansion for UI Display

This module provides post-processing utilities to expand medical abbreviations
for improved UI readability. Stage 3 training with CASI dataset handles
abbreviation RECOGNITION - this utility adds expanded_text for DISPLAY.

Example:
    >>> entities = [{'text': 'MTX', 'type': 'MEDICATION', 'confidence': 0.9}]
    >>> expand_abbreviations(entities)
    >>> entities[0]['expanded_text']  # 'methotrexate'
    >>> entities[0]['is_abbreviation']  # True
"""

from typing import List, Dict, Any


# Medical abbreviation mapping from CASI dataset
# Matches abbreviations used in Stage 3 training data
ABBREVIATION_MAP = {
    # DMARDs (Disease-Modifying Antirheumatic Drugs)
    'MTX': 'methotrexate',
    'HCQ': 'hydroxychloroquine',
    'SSZ': 'sulfasalazine',
    'LEF': 'leflunomide',
    'AZA': 'azathioprine',

    # Biologics
    'TNF': 'tumor necrosis factor',
    'HUMIRA': 'adalimumab',
    'ENBREL': 'etanercept',
    'REMICADE': 'infliximab',

    # Rheumatic Diseases
    'RA': 'rheumatoid arthritis',
    'SLE': 'systemic lupus erythematosus',
    'OA': 'osteoarthritis',
    'PsA': 'psoriatic arthritis',
    'JIA': 'juvenile idiopathic arthritis',
    'AS': 'ankylosing spondylitis',
    'PMR': 'polymyalgia rheumatica',

    # Lab Tests
    'ESR': 'erythrocyte sedimentation rate',
    'CRP': 'C-reactive protein',
    'RF': 'rheumatoid factor',
    'ANA': 'antinuclear antibody',
    'CBC': 'complete blood count',
    'CMP': 'comprehensive metabolic panel',
    'BMP': 'basic metabolic panel',
    'LFT': 'liver function test',
    'TSH': 'thyroid-stimulating hormone',

    # Common Medical Terms
    'BP': 'blood pressure',
    'HR': 'heart rate',
    'RR': 'respiratory rate',
    'O2': 'oxygen',
    'IV': 'intravenous',
    'PO': 'by mouth',
    'PRN': 'as needed',
    'BID': 'twice daily',
    'TID': 'three times daily',
    'QID': 'four times daily',
    'QD': 'once daily',
}


def expand_abbreviations(entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Add expanded_text field to entities that are known abbreviations.

    This is for UI DISPLAY purposes - Stage 3 model handles recognition.
    After Stage 3 training, the model will extract "MTX" as a MEDICATION entity.
    This function adds expanded_text="methotrexate" for better UI readability.

    Args:
        entities: List of entity dictionaries from extraction

    Returns:
        Same list (modified in-place) with expanded_text added to abbreviations

    Example:
        >>> entities = [
        ...     {'text': 'MTX', 'type': 'MEDICATION'},
        ...     {'text': 'aspirin', 'type': 'MEDICATION'}
        ... ]
        >>> expand_abbreviations(entities)
        >>> entities[0]['expanded_text']
        'methotrexate'
        >>> 'expanded_text' in entities[1]
        False
    """
    for entity in entities:
        text = entity.get('text', '').strip()
        text_upper = text.upper()

        if text_upper in ABBREVIATION_MAP:
            entity['expanded_text'] = ABBREVIATION_MAP[text_upper]
            entity['is_abbreviation'] = True
            # Keep original text unchanged - "MTX" remains "MTX"

    return entities


def get_expansion(abbreviation: str) -> str:
    """
    Get the expanded form of a single abbreviation.

    Args:
        abbreviation: Medical abbreviation (case-insensitive)

    Returns:
        Expanded text, or original text if not found

    Example:
        >>> get_expansion('MTX')
        'methotrexate'
        >>> get_expansion('unknown')
        'unknown'
    """
    abbr_upper = abbreviation.strip().upper()
    return ABBREVIATION_MAP.get(abbr_upper, abbreviation)


def is_abbreviation(text: str) -> bool:
    """
    Check if text is a known medical abbreviation.

    Args:
        text: Text to check (case-insensitive)

    Returns:
        True if text is a known abbreviation

    Example:
        >>> is_abbreviation('MTX')
        True
        >>> is_abbreviation('methotrexate')
        False
    """
    return text.strip().upper() in ABBREVIATION_MAP
