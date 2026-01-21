"""
Version B-Optimized: ONNX-Based GatorTron-Rheum Entity Extractor

Optimized entity extraction using ONNX Runtime for faster CPU inference.
Drop-in replacement for MTLEntityExtractor with same API.

Model: Custom-trained GatorTron-base (gatortron-rheum) converted to ONNX
- Base: UFNLP/gatortron-base (345M params)
- Format: ONNX with optional INT8 quantization
- Labels: 13 BIO labels (6 entity types + O)

Performance Targets:
- Speed: 1.5-2s per note on CPU (vs 5-8s PyTorch)
- Memory: <500MB peak (with INT8 quantization)
- Accuracy: 80%+ F1 (same as PyTorch model)

Requirements:
    pip install onnxruntime optimum[onnxruntime]

Usage:
    # Use ONNX model if available, fallback to PyTorch
    try:
        from backend.services.mtl_entity_extractor_optimized import ONNXEntityExtractor
        extractor = ONNXEntityExtractor()
    except ImportError:
        from backend.services.mtl_entity_extractor import MTLEntityExtractor
        extractor = MTLEntityExtractor()
"""

import os
import re
import time
import logging
import numpy as np
from typing import List, Dict, Tuple, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


# Check for ONNX Runtime availability
try:
    from optimum.onnxruntime import ORTModelForTokenClassification
    from transformers import AutoTokenizer
    ONNX_AVAILABLE = True
except ImportError:
    ONNX_AVAILABLE = False
    logger.warning("ONNX Runtime not available. Install with: pip install onnxruntime optimum[onnxruntime]")


class ONNXEntityExtractor:
    """
    Version B-Optimized: ONNX-based entity extractor.

    Uses ONNX Runtime for optimized CPU inference (1.5-2x faster than PyTorch).
    API-compatible with MTLEntityExtractor.
    """

    # Model configuration
    MODEL_NAME = 'gatortron-rheum-onnx'
    MODEL_FOLDER = 'gatortron-rheum-onnx'  # ONNX model folder
    FALLBACK_FOLDER = 'gatortron-rheum-onnx-int8'  # Quantized ONNX fallback
    QUANTIZED_MODEL_FILE = 'model_quantized.onnx'  # Quantized model filename
    MAX_LENGTH = 512
    CONFIDENCE_THRESHOLD = 0.5
    NEGATION_SCOPE = 50

    # Label mapping (same as MTLEntityExtractor)
    LABEL_MAP = {
        'DRUG': 'MEDICATION',
        'SYMPTOM': 'SYMPTOM',
        'DOSAGE': 'DOSAGE',
        'FREQUENCY': 'FREQUENCY',
        'CONDITION': 'DISEASE',
        'NEGATION': 'NEGATION',
    }

    # Regex patterns for LAB_TEST fallback
    LAB_TEST_PATTERN = re.compile(
        r'\b(ESR|CRP|ANA|RF|anti-CCP|sed\s*rate|hemoglobin|WBC|platelet|'
        r'creatinine|BUN|ALT|AST|uric\s*acid|C3|C4|dsDNA|Smith|RNP|'
        r'Scl-70|Jo-1|SSA|SSB|centromere)\b',
        re.IGNORECASE
    )

    LAB_VALUE_PATTERN = re.compile(
        r'\b(ESR|CRP|ANA|RF|anti-CCP|sed\s*rate|hemoglobin|WBC|platelet|'
        r'creatinine|BUN|ALT|AST|uric\s*acid)\s*[:\s]*(\d+(?:\.\d+)?)\s*(mm/hr|mg/[dL]|g/dL|%)?',
        re.IGNORECASE
    )

    def __init__(self, model_path: str = 'data/models'):
        """
        Initialize ONNX-based extractor.

        Args:
            model_path: Directory containing model folders

        Raises:
            ImportError: If onnxruntime/optimum not installed
            FileNotFoundError: If ONNX model not found
        """
        if not ONNX_AVAILABLE:
            raise ImportError(
                "ONNX Runtime not available. Install with: pip install onnxruntime optimum[onnxruntime]"
            )

        logger.info("Initializing ONNXEntityExtractor (Version B-Optimized)")

        # Get project root
        project_root = Path(__file__).parent.parent.parent

        # Convert to absolute path
        if not Path(model_path).is_absolute():
            self.model_path = str(project_root / model_path)
        else:
            self.model_path = model_path

        # Try to load ONNX model
        self.model, self.tokenizer, self.id2label = self._load_model()

        logger.info("ONNXEntityExtractor initialized successfully")

    def _load_model(self) -> Tuple[ORTModelForTokenClassification, AutoTokenizer, Dict]:
        """
        Load ONNX model and tokenizer.

        Tries main ONNX folder first, then quantized fallback.

        Returns:
            Tuple of (model, tokenizer, id2label mapping)
        """
        # Try main ONNX folder
        onnx_path = os.path.join(self.model_path, self.MODEL_FOLDER)
        fallback_path = os.path.join(self.model_path, self.FALLBACK_FOLDER)

        model_path = None
        is_quantized = False

        if os.path.exists(onnx_path):
            model_path = onnx_path
            logger.info(f"Loading ONNX model from: {onnx_path}")
        elif os.path.exists(fallback_path):
            model_path = fallback_path
            is_quantized = True
            logger.info(f"Loading quantized ONNX model from: {fallback_path}")
        else:
            raise FileNotFoundError(
                f"ONNX model not found. Expected at:\n"
                f"  - {onnx_path}\n"
                f"  - {fallback_path}\n"
                f"Run: python scripts/convert_to_onnx.py"
            )

        # Load model - use file_name parameter for quantized models
        if is_quantized:
            # Check if quantized model file exists
            quantized_file = os.path.join(model_path, self.QUANTIZED_MODEL_FILE)
            if os.path.exists(quantized_file):
                model = ORTModelForTokenClassification.from_pretrained(
                    model_path,
                    file_name=self.QUANTIZED_MODEL_FILE
                )
                logger.info(f"Loaded quantized model: {self.QUANTIZED_MODEL_FILE}")
            else:
                # Fallback to default model.onnx
                model = ORTModelForTokenClassification.from_pretrained(model_path)
        else:
            model = ORTModelForTokenClassification.from_pretrained(model_path)

        tokenizer = AutoTokenizer.from_pretrained(model_path)

        # Get label mapping from config
        id2label = model.config.id2label if hasattr(model.config, 'id2label') else {}

        logger.info(f"ONNX model loaded: {model.config.num_labels} labels")

        return model, tokenizer, id2label

    def extract(self, text: str) -> Dict:
        """
        Extract medical entities from text using ONNX model.

        Args:
            text: Medical note text to process

        Returns:
            ExtractionResult with entities, version, processing time, model name
        """
        start_time = time.time()

        try:
            # Tokenize
            inputs = self.tokenizer(
                text,
                return_tensors='pt',
                truncation=True,
                max_length=self.MAX_LENGTH,
                padding='max_length',
                return_offsets_mapping=True
            )

            offset_mapping = inputs.pop('offset_mapping')[0].tolist()

            # Run ONNX inference
            outputs = self.model(**inputs)

            # Process outputs
            logits = outputs.logits[0].numpy()  # Convert to numpy
            predictions = np.argmax(logits, axis=-1)
            scores = np.max(self._softmax(logits), axis=-1)

            # Convert to labels
            tokens = self.tokenizer.convert_ids_to_tokens(inputs['input_ids'][0])
            labels = [self.id2label.get(p, 'O') for p in predictions]

            # Convert BIO to entities
            raw_entities = self._bio_to_entities(tokens, labels, scores.tolist(), offset_mapping, text)

            # Separate NEGATION entities
            negation_spans = []
            regular_entities = []

            for entity_dict in raw_entities:
                if entity_dict['type'] == 'NEGATION':
                    negation_spans.append((entity_dict['start'], entity_dict['end']))
                else:
                    regular_entities.append(entity_dict)

            # Map labels and check negation
            entities = []
            for entity_dict in regular_entities:
                mapped_type = self.LABEL_MAP.get(entity_dict['type'], 'ENTITY')

                entity = self._create_entity(
                    text=entity_dict['text'],
                    entity_type=mapped_type,
                    start=entity_dict['start'],
                    end=entity_dict['end'],
                    confidence=entity_dict['confidence']
                )

                # Check negation
                is_negated, negation_cue = self._check_negation_with_cue(
                    entity_dict['start'], entity_dict['end'], negation_spans, text
                )
                entity['is_negated'] = is_negated
                if is_negated and negation_cue:
                    entity['negation_cue'] = negation_cue

                entities.append(entity)

            # Add LAB_TEST via regex
            lab_entities = self._extract_lab_tests(text, entities)
            entities.extend(lab_entities)

            processing_time_ms = (time.time() - start_time) * 1000

            return {
                'entities': entities,
                'version': self.get_version(),
                'processing_time_ms': processing_time_ms,
                'model_name': self.get_model_name()
            }

        except Exception as e:
            logger.error(f"Error during ONNX extraction: {e}")
            processing_time_ms = (time.time() - start_time) * 1000
            return {
                'entities': [],
                'version': self.get_version(),
                'processing_time_ms': processing_time_ms,
                'model_name': self.get_model_name()
            }

    def _softmax(self, x: np.ndarray) -> np.ndarray:
        """Compute softmax values for numpy array."""
        exp_x = np.exp(x - np.max(x, axis=-1, keepdims=True))
        return exp_x / np.sum(exp_x, axis=-1, keepdims=True)

    def _bio_to_entities(
        self,
        tokens: List[str],
        labels: List[str],
        scores: List[float],
        offset_mapping: List[Tuple[int, int]],
        text: str
    ) -> List[Dict]:
        """Convert BIO tags to entity spans."""
        entities = []
        current_entity = None

        for idx, (token, label, score, offset) in enumerate(
            zip(tokens, labels, scores, offset_mapping)
        ):
            if token in ['[CLS]', '[SEP]', '[PAD]', '<s>', '</s>']:
                continue

            if offset[0] == 0 and offset[1] == 0 and idx > 0:
                continue

            if label == 'O':
                if current_entity:
                    entity_text = text[current_entity['start']:current_entity['end']]
                    current_entity['text'] = entity_text.strip()

                    if current_entity['scores']:
                        current_entity['confidence'] = sum(current_entity['scores']) / len(current_entity['scores'])
                    else:
                        current_entity['confidence'] = 0.0

                    if current_entity['confidence'] >= self.CONFIDENCE_THRESHOLD:
                        entities.append(current_entity)

                    current_entity = None

            elif label.startswith('B-'):
                if current_entity:
                    entity_text = text[current_entity['start']:current_entity['end']]
                    current_entity['text'] = entity_text.strip()
                    current_entity['confidence'] = sum(current_entity['scores']) / len(current_entity['scores'])

                    if current_entity['confidence'] >= self.CONFIDENCE_THRESHOLD:
                        entities.append(current_entity)

                entity_type = label[2:]
                current_entity = {
                    'type': entity_type,
                    'start': offset[0],
                    'end': offset[1],
                    'scores': [score],
                    'text': ''
                }

            elif label.startswith('I-') and current_entity:
                current_entity['end'] = offset[1]
                current_entity['scores'].append(score)

        if current_entity:
            entity_text = text[current_entity['start']:current_entity['end']]
            current_entity['text'] = entity_text.strip()
            current_entity['confidence'] = sum(current_entity['scores']) / len(current_entity['scores'])

            if current_entity['confidence'] >= self.CONFIDENCE_THRESHOLD:
                entities.append(current_entity)

        return entities

    def _create_entity(
        self,
        text: str,
        entity_type: str,
        start: int,
        end: int,
        confidence: float
    ) -> Dict:
        """Create standardized entity dictionary."""
        return {
            'text': text,
            'type': entity_type,
            'start': start,
            'end': end,
            'confidence': round(confidence, 3),
            'source': 'onnx-model'
        }

    def _check_negation_with_cue(
        self,
        entity_start: int,
        entity_end: int,
        negation_spans: List[Tuple[int, int]],
        text: str
    ) -> Tuple[bool, Optional[str]]:
        """Check if entity is negated and return negation cue."""
        for neg_start, neg_end in negation_spans:
            if neg_end <= entity_start and (entity_start - neg_end) <= self.NEGATION_SCOPE:
                cue_text = text[neg_start:neg_end].strip()
                return True, cue_text

            if neg_start >= entity_end and (neg_start - entity_end) <= self.NEGATION_SCOPE:
                cue_text = text[neg_start:neg_end].strip()
                return True, cue_text

        return False, None

    def _extract_lab_tests(self, text: str, existing_entities: List[Dict]) -> List[Dict]:
        """Extract LAB_TEST entities using regex fallback."""
        lab_entities = []
        existing_spans = set()

        for entity in existing_entities:
            for pos in range(entity['start'], entity['end']):
                existing_spans.add(pos)

        for match in self.LAB_VALUE_PATTERN.finditer(text):
            start, end = match.start(), match.end()

            if any(pos in existing_spans for pos in range(start, end)):
                continue

            entity = self._create_entity(
                text=match.group(0).strip(),
                entity_type='LAB_TEST',
                start=start,
                end=end,
                confidence=0.9
            )
            entity['is_negated'] = False
            lab_entities.append(entity)

            for pos in range(start, end):
                existing_spans.add(pos)

        for match in self.LAB_TEST_PATTERN.finditer(text):
            start, end = match.start(), match.end()

            if any(pos in existing_spans for pos in range(start, end)):
                continue

            entity = self._create_entity(
                text=match.group(0).strip(),
                entity_type='LAB_TEST',
                start=start,
                end=end,
                confidence=0.85
            )
            entity['is_negated'] = False
            lab_entities.append(entity)

        return lab_entities

    def get_version(self) -> str:
        """Return version identifier."""
        return 'B-ONNX'

    def get_model_name(self) -> str:
        """Return model name."""
        return 'gatortron-rheum-onnx'


def get_best_extractor(model_path: str = 'data/models'):
    """
    Factory function to get the best available extractor.

    Tries ONNX first (fastest), falls back to PyTorch with torch.compile.

    Args:
        model_path: Directory containing model folders

    Returns:
        Best available extractor instance
    """
    # Try ONNX first
    if ONNX_AVAILABLE:
        try:
            extractor = ONNXEntityExtractor(model_path)
            logger.info("Using ONNX extractor (fastest)")
            return extractor
        except FileNotFoundError:
            logger.info("ONNX model not found, falling back to PyTorch")
        except Exception as e:
            logger.warning(f"ONNX extractor failed: {e}, falling back to PyTorch")

    # Fall back to PyTorch
    from backend.services.mtl_entity_extractor import MTLEntityExtractor
    logger.info("Using PyTorch extractor with torch.compile")
    return MTLEntityExtractor(model_path)
