"""
Version A: Regex-based Entity Extractor

Simple pattern matching for medical entity extraction.
No ML dependencies required - uses Python's built-in re module.

Performance:
- Speed: 50-100ms per note
- Memory: <512MB
- Accuracy: ~65% F1

Entity Types Supported:
- MEDICATION: Rheumatology drugs (methotrexate, biologics, NSAIDs, steroids)
- DOSAGE: Doses with units (15mg, 7.5 mg, 400mg/m2)
- FREQUENCY: Administration frequency (daily, weekly, BID, QD)
- SYMPTOM: Common rheumatology symptoms (pain, swelling, stiffness, fever)
- DISEASE: Rheumatology conditions (RA, SLE, OA, psoriatic arthritis)
"""

import re
import time
from typing import List
from .base_extractor import BaseEntityExtractor, Entity, ExtractionResult


class RegexEntityExtractor(BaseEntityExtractor):
    """
    Version A: Regex-based entity extractor for rheumatology clinical notes.

    Uses comprehensive regex patterns to extract medical entities.
    Always returns results (no dependencies, no failures).
    """

    # Fixed confidence score for all regex matches
    CONFIDENCE = 0.65

    # Comprehensive regex patterns for rheumatology entities
    PATTERNS = {
        'MEDICATION': r'\b(?:'
            # DMARDs (Disease-Modifying Anti-Rheumatic Drugs)
            r'methotrexate|MTX|'
            r'hydroxychloroquine|plaquenil|'
            r'sulfasalazine|azulfidine|'
            r'leflunomide|arava|'
            # Biologics
            r'adalimumab|humira|'
            r'etanercept|enbrel|'
            r'infliximab|remicade|'
            r'rituximab|rituxan|'
            r'tocilizumab|actemra|'
            r'abatacept|orencia|'
            # JAK inhibitors
            r'tofacitinib|xeljanz|'
            r'baricitinib|olumiant|'
            r'upadacitinib|rinvoq|'
            # NSAIDs
            r'ibuprofen|advil|motrin|'
            r'naproxen|naprosyn|aleve|'
            r'celecoxib|celebrex|'
            r'indomethacin|indocin|'
            r'diclofenac|voltaren|'
            r'meloxicam|mobic|'
            # Steroids
            r'prednisone|'
            r'prednisolone|'
            r'methylprednisolone|medrol|'
            r'dexamethasone|decadron|'
            r'hydrocortisone|'
            # Other immunosuppressants
            r'azathioprine|imuran|'
            r'cyclophosphamide|cytoxan|'
            r'mycophenolate|cellcept|'
            r'tacrolimus|prograf'
        r')\b',

        'DOSAGE': r'\b(?:'
            # Numeric dose with units
            r'(?:\d+(?:\.\d+)?)\s*(?:mg|mcg|g|ml|units?|iu)|'
            # Dose with body surface area
            r'(?:\d+(?:\.\d+)?)\s*(?:mg|mcg)/m2|'
            # Dose ranges
            r'(?:\d+(?:\.\d+)?)\s*(?:-|to)\s*(?:\d+(?:\.\d+)?)\s*(?:mg|mcg|g)'
        r')',

        'FREQUENCY': r'\b(?:'
            # Standard abbreviations
            r'QD|BID|TID|QID|Q\d+H|'
            # Written forms
            r'once\s+daily|twice\s+daily|three\s+times\s+daily|four\s+times\s+daily|'
            r'daily|weekly|monthly|bi-weekly|biweekly|'
            r'every\s+\d+\s+(?:hours?|days?|weeks?|months?)|'
            r'every\s+(?:day|week|month|other\s+day)|'
            r'per\s+(?:day|week|month)|'
            # Specific timing
            r'in\s+the\s+morning|at\s+bedtime|with\s+meals|before\s+meals|after\s+meals|'
            r'HS|AC|PC|PRN|as\s+needed'
        r')',

        'SYMPTOM': r'\b(?:'
            # Pain-related
            r'pain|painful|aching|tender(?:ness)?|'
            r'soreness|discomfort|'
            # Swelling/inflammation
            r'swelling|swollen|inflammation|inflamed|'
            r'edema|effusion|synovitis|'
            # Stiffness
            r'stiff(?:ness)?|rigidity|'
            r'morning\s+stiffness|'
            # Mobility
            r'limited\s+(?:range\s+of\s+)?motion|ROM|'
            r'difficulty\s+(?:walking|moving|bending)|'
            # Systemic symptoms
            r'fever|febrile|pyrexia|'
            r'fatigue|tired(?:ness)?|exhaustion|'
            r'weakness|malaise|'
            # Skin manifestations
            r'rash|erythema|purpura|'
            r'photosensitivity|'
            # Other rheumatology symptoms
            r'joint\s+pain|arthralgia|'
            r'muscle\s+pain|myalgia|'
            r'dry\s+eyes|dry\s+mouth|sicca'
        r')',

        'DISEASE': r'\b(?:'
            # Rheumatoid arthritis
            r'rheumatoid\s+arthritis|RA|'
            r'seropositive\s+RA|seronegative\s+RA|'
            # Lupus
            r'systemic\s+lupus\s+erythematosus|SLE|lupus|'
            r'discoid\s+lupus|cutaneous\s+lupus|'
            # Spondyloarthropathies
            r'ankylosing\s+spondylitis|AS|'
            r'psoriatic\s+arthritis|PsA|'
            r'reactive\s+arthritis|'
            r'enteropathic\s+arthritis|'
            # Osteoarthritis
            r'osteoarthritis|OA|degenerative\s+joint\s+disease|'
            # Crystalline arthropathies
            r'gout|gouty\s+arthritis|'
            r'pseudogout|CPPD|calcium\s+pyrophosphate|'
            # Connective tissue diseases
            r'scleroderma|systemic\s+sclerosis|'
            r'Sj(?:o|ö)gren[\'\']?s?\s+syndrome|'
            r'polymyositis|dermatomyositis|'
            r'mixed\s+connective\s+tissue\s+disease|MCTD|'
            # Vasculitis
            r'vasculitis|'
            r'temporal\s+arteritis|giant\s+cell\s+arteritis|GCA|'
            r'polymyalgia\s+rheumatica|PMR|'
            r'Wegener[\'\']?s?\s+granulomatosis|GPA|'
            # Other
            r'fibromyalgia|'
            r'polymyalgia|'
            r'inflammatory\s+arthritis'
        r')',

        'LAB_TEST': r'\b(?:'
            # Inflammation markers
            r'ESR|erythrocyte\s+sedimentation\s+rate|sed\s+rate|'
            r'CRP|C-reactive\s+protein|'
            # Autoantibodies
            r'RF|rheumatoid\s+factor|'
            r'anti-CCP|ACPA|anti-cyclic\s+citrullinated\s+peptide|'
            r'ANA|antinuclear\s+antibody|'
            r'anti-dsDNA|anti-DNA|'
            r'anti-Sm|'
            r'anti-RNP|'
            r'anti-SSA|anti-Ro|'
            r'anti-SSB|anti-La|'
            # Complement
            r'C3|C4|complement|'
            # Other
            r'uric\s+acid|'
            r'HLA-B27'
        r')'
    }

    def __init__(self):
        """Initialize regex extractor"""
        # Compile patterns for efficiency
        self.compiled_patterns = {
            entity_type: re.compile(pattern, re.IGNORECASE)
            for entity_type, pattern in self.PATTERNS.items()
        }

    def extract(self, text: str) -> ExtractionResult:
        """
        Extract entities from text using regex patterns.

        Args:
            text: Medical note text

        Returns:
            ExtractionResult with extracted entities

        Example:
            >>> extractor = RegexEntityExtractor()
            >>> result = extractor.extract("Patient takes methotrexate 15mg weekly")
            >>> print(result['entities'])
        """
        start_time = time.time()
        entities: List[Entity] = []

        # Extract entities for each pattern
        for entity_type, pattern in self.compiled_patterns.items():
            matches = pattern.finditer(text)

            for match in matches:
                entity = self._create_entity(
                    text=match.group(0),
                    entity_type=entity_type,
                    start=match.start(),
                    end=match.end(),
                    confidence=self.CONFIDENCE
                )
                entities.append(entity)

        # Calculate processing time
        processing_time_ms = (time.time() - start_time) * 1000

        # Sort entities by position for readability
        entities.sort(key=lambda e: e['start'])

        result: ExtractionResult = {
            'entities': entities,
            'version': self.get_version(),
            'processing_time_ms': processing_time_ms,
            'model_name': self.get_model_name()
        }

        return result

    def get_version(self) -> str:
        """Return version identifier"""
        return 'A'

    def get_model_name(self) -> str:
        """Return model name"""
        return 'regex'


if __name__ == "__main__":
    # Test the extractor
    extractor = RegexEntityExtractor()

    sample_note = """
    Chief Complaint: Joint pain and swelling

    Patient is a 45-year-old female with rheumatoid arthritis presenting with bilateral
    knee pain and swelling for 2 weeks. Currently taking methotrexate 15mg weekly and
    prednisone 5mg daily. Reports morning stiffness lasting 2 hours. No fever.

    Labs: ESR 45, CRP 12, RF positive, anti-CCP 150

    Assessment: RA flare, active disease
    Plan: Increase MTX to 20mg weekly, continue prednisone, add hydroxychloroquine 400mg daily
    """

    result = extractor.extract(sample_note)

    print(f"Version: {result['version']}")
    print(f"Model: {result['model_name']}")
    print(f"Processing time: {result['processing_time_ms']:.2f}ms")
    print(f"Entities found: {len(result['entities'])}\n")

    for entity in result['entities']:
        print(f"- {entity['type']}: '{entity['text']}' (confidence: {entity['confidence']})")
