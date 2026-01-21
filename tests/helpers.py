"""
Custom Test Assertions for EHR-NLP ML System

Domain-specific assertion helpers for medical entity extraction testing.
These provide clearer error messages and reduce boilerplate in tests.

Usage:
    from tests.helpers import assert_entity_found, assert_negated, assert_confidence_above
"""

from typing import List, Dict, Optional, Any


# ==============================================================================
# ENTITY ASSERTIONS
# ==============================================================================

def assert_entity_found(
    entities: List[Dict],
    entity_type: str,
    text_contains: str,
    msg: Optional[str] = None
) -> Dict:
    """
    Assert an entity of given type containing specified text exists.

    Args:
        entities: List of entity dictionaries from extraction result
        entity_type: Expected entity type (MEDICATION, SYMPTOM, etc.)
        text_contains: Text that should be in entity['text']
        msg: Optional custom message

    Returns:
        The matching entity dictionary

    Raises:
        AssertionError: If no matching entity found

    Example:
        # Arrange
        result = extractor.extract("Patient takes methotrexate")

        # Assert
        med = assert_entity_found(result['entities'], 'MEDICATION', 'methotrexate')
    """
    matching = [
        e for e in entities
        if e['type'] == entity_type and text_contains.lower() in e['text'].lower()
    ]

    if not matching:
        found_of_type = [e['text'] for e in entities if e['type'] == entity_type]
        all_types = list(set(e['type'] for e in entities))

        error_msg = (
            f"Expected entity type='{entity_type}' containing '{text_contains}'\n"
            f"  Found entities of type '{entity_type}': {found_of_type or 'None'}\n"
            f"  All entity types found: {all_types}"
        )
        if msg:
            error_msg = f"{msg}\n{error_msg}"
        raise AssertionError(error_msg)

    return matching[0]


def assert_entity_not_found(
    entities: List[Dict],
    entity_type: str,
    text_contains: str,
    msg: Optional[str] = None
) -> None:
    """
    Assert NO entity of given type containing specified text exists.

    Useful for testing that false positives are avoided.

    Example:
        result = extractor.extract("The weather is nice")
        assert_entity_not_found(result['entities'], 'MEDICATION', 'weather')
    """
    matching = [
        e for e in entities
        if e['type'] == entity_type and text_contains.lower() in e['text'].lower()
    ]

    if matching:
        error_msg = (
            f"Expected NO entity type='{entity_type}' containing '{text_contains}'\n"
            f"  But found: {[e['text'] for e in matching]}"
        )
        if msg:
            error_msg = f"{msg}\n{error_msg}"
        raise AssertionError(error_msg)


def assert_entity_count(
    entities: List[Dict],
    entity_type: str,
    expected_count: int,
    msg: Optional[str] = None
) -> None:
    """
    Assert exact count of entities of a given type.

    Example:
        result = extractor.extract("methotrexate 15mg and prednisone 10mg")
        assert_entity_count(result['entities'], 'MEDICATION', 2)
    """
    actual = [e for e in entities if e['type'] == entity_type]
    actual_count = len(actual)

    if actual_count != expected_count:
        error_msg = (
            f"Expected {expected_count} entities of type '{entity_type}', "
            f"found {actual_count}\n"
            f"  Found: {[e['text'] for e in actual]}"
        )
        if msg:
            error_msg = f"{msg}\n{error_msg}"
        raise AssertionError(error_msg)


def assert_entity_count_gte(
    entities: List[Dict],
    entity_type: str,
    min_count: int,
    msg: Optional[str] = None
) -> None:
    """
    Assert at least min_count entities of a given type.

    Example:
        result = extractor.extract(long_clinical_note)
        assert_entity_count_gte(result['entities'], 'MEDICATION', 3)
    """
    actual = [e for e in entities if e['type'] == entity_type]
    actual_count = len(actual)

    if actual_count < min_count:
        error_msg = (
            f"Expected at least {min_count} entities of type '{entity_type}', "
            f"found {actual_count}\n"
            f"  Found: {[e['text'] for e in actual]}"
        )
        if msg:
            error_msg = f"{msg}\n{error_msg}"
        raise AssertionError(error_msg)


# ==============================================================================
# NEGATION ASSERTIONS
# ==============================================================================

def assert_negated(entity: Dict, msg: Optional[str] = None) -> None:
    """
    Assert entity is marked as negated (is_negated=True).

    Example:
        result = extractor.extract("Patient denies fever")
        fever = find_entity(result['entities'], 'fever')
        assert_negated(fever)
    """
    is_negated = entity.get('is_negated', False)

    if not is_negated:
        error_msg = (
            f"Expected entity '{entity.get('text', 'unknown')}' to be negated "
            f"(is_negated=True), but is_negated={is_negated}"
        )
        if msg:
            error_msg = f"{msg}\n{error_msg}"
        raise AssertionError(error_msg)


def assert_not_negated(entity: Dict, msg: Optional[str] = None) -> None:
    """
    Assert entity is NOT marked as negated (is_negated=False).

    Example:
        result = extractor.extract("Patient has fever")
        fever = find_entity(result['entities'], 'fever')
        assert_not_negated(fever)
    """
    is_negated = entity.get('is_negated', False)

    if is_negated:
        error_msg = (
            f"Expected entity '{entity.get('text', 'unknown')}' to NOT be negated "
            f"(is_negated=False), but is_negated={is_negated}"
        )
        if msg:
            error_msg = f"{msg}\n{error_msg}"
        raise AssertionError(error_msg)


# ==============================================================================
# CONFIDENCE ASSERTIONS
# ==============================================================================

def assert_confidence_above(
    entity: Dict,
    threshold: float = 0.5,
    msg: Optional[str] = None
) -> None:
    """
    Assert entity confidence meets or exceeds threshold.

    Example:
        result = extractor.extract("methotrexate 15mg")
        med = find_entity(result['entities'], 'methotrexate')
        assert_confidence_above(med, 0.8)
    """
    confidence = entity.get('confidence', 0.0)

    if confidence < threshold:
        error_msg = (
            f"Entity '{entity.get('text', 'unknown')}' confidence {confidence:.3f} "
            f"is below threshold {threshold}"
        )
        if msg:
            error_msg = f"{msg}\n{error_msg}"
        raise AssertionError(error_msg)


def assert_confidence_below(
    entity: Dict,
    threshold: float = 0.5,
    msg: Optional[str] = None
) -> None:
    """
    Assert entity confidence is below threshold.

    Useful for testing uncertain extractions.
    """
    confidence = entity.get('confidence', 0.0)

    if confidence >= threshold:
        error_msg = (
            f"Entity '{entity.get('text', 'unknown')}' confidence {confidence:.3f} "
            f"should be below threshold {threshold}"
        )
        if msg:
            error_msg = f"{msg}\n{error_msg}"
        raise AssertionError(error_msg)


# ==============================================================================
# POSITION ASSERTIONS
# ==============================================================================

def assert_entity_position(
    entity: Dict,
    expected_start: int,
    expected_end: int,
    msg: Optional[str] = None
) -> None:
    """
    Assert entity has correct start/end positions.

    Example:
        text = "Patient takes methotrexate"
        result = extractor.extract(text)
        med = find_entity(result['entities'], 'methotrexate')
        assert_entity_position(med, 14, 26)
    """
    actual_start = entity.get('start', -1)
    actual_end = entity.get('end', -1)

    if actual_start != expected_start or actual_end != expected_end:
        error_msg = (
            f"Entity '{entity.get('text', 'unknown')}' position mismatch\n"
            f"  Expected: start={expected_start}, end={expected_end}\n"
            f"  Actual: start={actual_start}, end={actual_end}"
        )
        if msg:
            error_msg = f"{msg}\n{error_msg}"
        raise AssertionError(error_msg)


def assert_no_overlapping_entities(
    entities: List[Dict],
    msg: Optional[str] = None
) -> None:
    """
    Assert no entities have overlapping positions.

    Example:
        result = extractor.extract(text)
        assert_no_overlapping_entities(result['entities'])
    """
    sorted_entities = sorted(entities, key=lambda e: (e.get('start', 0), e.get('end', 0)))

    for i in range(len(sorted_entities) - 1):
        current = sorted_entities[i]
        next_entity = sorted_entities[i + 1]

        current_end = current.get('end', 0)
        next_start = next_entity.get('start', 0)

        if current_end > next_start:
            error_msg = (
                f"Overlapping entities detected:\n"
                f"  Entity 1: '{current.get('text')}' ({current.get('start')}-{current.get('end')})\n"
                f"  Entity 2: '{next_entity.get('text')}' ({next_entity.get('start')}-{next_entity.get('end')})"
            )
            if msg:
                error_msg = f"{msg}\n{error_msg}"
            raise AssertionError(error_msg)


# ==============================================================================
# EXTRACTION RESULT ASSERTIONS
# ==============================================================================

def assert_valid_extraction_result(
    result: Dict,
    expected_version: Optional[str] = None,
    msg: Optional[str] = None
) -> None:
    """
    Assert extraction result has all required fields and valid structure.

    Example:
        result = extractor.extract(text)
        assert_valid_extraction_result(result, expected_version='B')
    """
    required_fields = ['entities', 'version', 'processing_time_ms', 'model_name']

    for field in required_fields:
        if field not in result:
            error_msg = f"Missing required field '{field}' in extraction result"
            if msg:
                error_msg = f"{msg}\n{error_msg}"
            raise AssertionError(error_msg)

    if not isinstance(result['entities'], list):
        raise AssertionError(f"'entities' must be a list, got {type(result['entities'])}")

    if expected_version and result['version'] != expected_version:
        raise AssertionError(
            f"Expected version '{expected_version}', got '{result['version']}'"
        )

    if result['processing_time_ms'] < 0:
        raise AssertionError(
            f"processing_time_ms must be >= 0, got {result['processing_time_ms']}"
        )


def assert_processing_time_under(
    result: Dict,
    max_ms: float,
    msg: Optional[str] = None
) -> None:
    """
    Assert extraction completed within time limit.

    Example:
        result = extractor.extract(long_text)
        assert_processing_time_under(result, 800)  # 800ms max
    """
    actual_ms = result.get('processing_time_ms', float('inf'))

    if actual_ms > max_ms:
        error_msg = (
            f"Processing time {actual_ms:.1f}ms exceeds limit of {max_ms}ms"
        )
        if msg:
            error_msg = f"{msg}\n{error_msg}"
        raise AssertionError(error_msg)


# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================

def find_entity(
    entities: List[Dict],
    text_contains: str,
    entity_type: Optional[str] = None
) -> Optional[Dict]:
    """
    Find first entity containing specified text.

    Args:
        entities: List of entity dictionaries
        text_contains: Text to search for (case-insensitive)
        entity_type: Optional type filter

    Returns:
        First matching entity or None

    Example:
        entity = find_entity(result['entities'], 'methotrexate')
        if entity:
            assert entity['type'] == 'MEDICATION'
    """
    for e in entities:
        if text_contains.lower() in e.get('text', '').lower():
            if entity_type is None or e.get('type') == entity_type:
                return e
    return None


def find_entities(
    entities: List[Dict],
    text_contains: str,
    entity_type: Optional[str] = None
) -> List[Dict]:
    """
    Find all entities containing specified text.

    Returns:
        List of matching entities (may be empty)
    """
    matching = []
    for e in entities:
        if text_contains.lower() in e.get('text', '').lower():
            if entity_type is None or e.get('type') == entity_type:
                matching.append(e)
    return matching


def get_entities_by_type(entities: List[Dict], entity_type: str) -> List[Dict]:
    """
    Get all entities of a specific type.

    Example:
        medications = get_entities_by_type(result['entities'], 'MEDICATION')
        assert len(medications) >= 2
    """
    return [e for e in entities if e.get('type') == entity_type]


def get_entity_texts(entities: List[Dict], entity_type: Optional[str] = None) -> List[str]:
    """
    Get just the text values from entities.

    Example:
        med_names = get_entity_texts(result['entities'], 'MEDICATION')
        assert 'methotrexate' in [m.lower() for m in med_names]
    """
    filtered = entities if entity_type is None else get_entities_by_type(entities, entity_type)
    return [e.get('text', '') for e in filtered]


# ==============================================================================
# VERSION D SPECIFIC ASSERTIONS
# ==============================================================================

def assert_agreement_score(
    entity: Dict,
    min_agreement: int = 2,
    msg: Optional[str] = None
) -> None:
    """
    Assert entity has minimum agreement score (Version D).

    Example:
        result = ensemble_extractor.extract(text)
        for entity in result['entities']:
            assert_agreement_score(entity, min_agreement=2)
    """
    agreement = entity.get('agreement', 0)

    if agreement < min_agreement:
        error_msg = (
            f"Entity '{entity.get('text', 'unknown')}' agreement {agreement} "
            f"is below minimum {min_agreement}"
        )
        if msg:
            error_msg = f"{msg}\n{error_msg}"
        raise AssertionError(error_msg)


def assert_has_umls_mapping(
    entity: Dict,
    msg: Optional[str] = None
) -> None:
    """
    Assert entity has UMLS CUI mapping (Version C/D with SapBERT).

    Example:
        result = two_tier_extractor.extract(text)
        med = find_entity(result['entities'], 'methotrexate')
        assert_has_umls_mapping(med)
    """
    umls_cui = entity.get('umls_cui')

    if not umls_cui:
        error_msg = (
            f"Entity '{entity.get('text', 'unknown')}' is missing UMLS CUI mapping"
        )
        if msg:
            error_msg = f"{msg}\n{error_msg}"
        raise AssertionError(error_msg)


def assert_inferred_diagnosis(
    result: Dict,
    diagnosis_contains: str,
    msg: Optional[str] = None
) -> Dict:
    """
    Assert an inferred diagnosis exists (Version D).

    Example:
        result = ensemble_extractor.extract(ra_symptoms_text)
        assert_inferred_diagnosis(result, 'rheumatoid arthritis')
    """
    inferred = result.get('inferred', [])

    matching = [
        d for d in inferred
        if diagnosis_contains.lower() in d.get('diagnosis_text', '').lower()
    ]

    if not matching:
        error_msg = (
            f"Expected inferred diagnosis containing '{diagnosis_contains}'\n"
            f"  Found: {[d.get('diagnosis_text') for d in inferred]}"
        )
        if msg:
            error_msg = f"{msg}\n{error_msg}"
        raise AssertionError(error_msg)

    return matching[0]


# ==============================================================================
# API CONTRACT ASSERTIONS
# ==============================================================================

def assert_response_has_keys(
    response_json: Dict,
    required_keys: List[str],
    msg: Optional[str] = None
) -> None:
    """
    Assert that API response JSON contains all required keys.

    Example:
        result = json.loads(response.data)
        assert_response_has_keys(result, ['data', 'pagination'])
    """
    missing = [k for k in required_keys if k not in response_json]
    if missing:
        error_msg = (
            f"Response missing required keys: {missing}\n"
            f"Got keys: {list(response_json.keys())}"
        )
        if msg:
            error_msg = f"{msg}\n{error_msg}"
        raise AssertionError(error_msg)


def assert_is_list(value: Any, msg: Optional[str] = None) -> None:
    """
    Assert that value is a list (not wrapped in object).

    Catches Bug #2: Frontend expected array but got {data: []}
    """
    if not isinstance(value, list):
        error_msg = f"Expected list, got {type(value).__name__}: {repr(value)[:100]}"
        if msg:
            error_msg = f"{msg}\n{error_msg}"
        raise AssertionError(error_msg)


def assert_is_dict(value: Any, msg: Optional[str] = None) -> None:
    """
    Assert that value is a dictionary.
    """
    if not isinstance(value, dict):
        error_msg = f"Expected dict, got {type(value).__name__}: {repr(value)[:100]}"
        if msg:
            error_msg = f"{msg}\n{error_msg}"
        raise AssertionError(error_msg)


def assert_pagination_structure(
    pagination: Dict,
    msg: Optional[str] = None
) -> None:
    """
    Assert pagination object has standard structure.

    Expected: {page, per_page, total_count, total_pages, has_next, has_prev}
    """
    required = ['page', 'per_page', 'total_count', 'total_pages', 'has_next', 'has_prev']
    missing = [k for k in required if k not in pagination]
    if missing:
        error_msg = f"Pagination missing keys: {missing}\nGot: {pagination}"
        if msg:
            error_msg = f"{msg}\n{error_msg}"
        raise AssertionError(error_msg)
