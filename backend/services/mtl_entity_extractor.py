"""
Version B: GatorTron-Rheum Entity Extractor (V2.2 - Optimized)

Transformer-based medical entity extraction using custom-trained GatorTron model.
Designed for rheumatology clinical notes with model-based negation detection.

Model: Custom-trained GatorTron-base (gatortron-rheum)
- Base: UFNLP/gatortron-base (345M params)
- Training: Sequential layer training on clinical NER datasets
- Fine-tuning: Stage Final cumulative training (F1=0.806)
- Labels: 13 BIO labels (6 entity types + O)

Entity Types (from model):
- DRUG → MEDICATION: Drugs, biologics, NSAIDs, steroids
- DOSAGE → DOSAGE: Numeric doses with units
- FREQUENCY → FREQUENCY: Administration schedules
- SYMPTOM → SYMPTOM: Clinical symptoms
- CONDITION → DISEASE: Medical conditions
- NEGATION → (marks nearby entities as negated)

Additional (regex fallback):
- LAB_TEST: ESR, CRP, ANA, RF, anti-CCP, etc.

Performance Targets:
- Speed: <2000ms per note on CPU (with torch.compile)
- Memory: <1GB peak
- Accuracy: 80%+ F1
- Negation: Model-based detection

Optimizations (V2.2):
- torch.compile: JIT compilation for 1.3-1.7x speedup
- Warm-up inference on initialization
"""

import os
import re
import time
import torch
import logging
from typing import List, Dict, Tuple, Optional
from transformers import AutoModelForTokenClassification, AutoTokenizer

from .base_extractor import BaseEntityExtractor, Entity, ExtractionResult

logger = logging.getLogger(__name__)


class MTLEntityExtractor(BaseEntityExtractor):
    """
    Version B: GatorTron-Rheum entity extractor (V2.2 - Optimized).

    Uses custom-trained GatorTron-base model for medical NER.
    Direct label mapping from model output + regex fallback for LAB_TEST.

    Optimizations:
    - torch.compile for JIT compilation (1.3-1.7x speedup)
    - Warm-up inference to pre-compile model
    """

    # Model configuration
    MODEL_NAME = 'gatortron-rheum'  # Custom trained model
    MODEL_FOLDER = 'gatortron-rheum'  # Folder in data/models/
    MAX_LENGTH = 512  # Maximum tokens for GatorTron
    CONFIDENCE_THRESHOLD = 0.5  # Lower threshold - model is well-trained
    NEGATION_SCOPE = 50  # Characters to check around NEGATION entities

    # Optimization settings
    # Note: torch.compile requires C++ compiler (Visual Studio on Windows)
    # For Windows without VS, set to False and use ONNX instead
    USE_TORCH_COMPILE = False  # Disabled - use ONNX for CPU optimization
    TORCH_COMPILE_MODE = "reduce-overhead"  # Best for older CPUs (2013-2018)

    # Direct label mapping from trained model to application types
    LABEL_MAP = {
        'DRUG': 'MEDICATION',
        'SYMPTOM': 'SYMPTOM',
        'DOSAGE': 'DOSAGE',
        'FREQUENCY': 'FREQUENCY',
        'CONDITION': 'DISEASE',
        'NEGATION': 'NEGATION',  # Special handling
    }

    # Regex pattern for LAB_TEST detection (not in training data)
    LAB_TEST_PATTERN = re.compile(
        r'\b(ESR|CRP|ANA|RF|anti-CCP|sed\s*rate|hemoglobin|WBC|platelet|'
        r'creatinine|BUN|ALT|AST|uric\s*acid|C3|C4|dsDNA|Smith|RNP|'
        r'Scl-70|Jo-1|SSA|SSB|centromere)\b',
        re.IGNORECASE
    )

    # Pattern to match lab values (e.g., "ESR 45", "CRP: 12")
    LAB_VALUE_PATTERN = re.compile(
        r'\b(ESR|CRP|ANA|RF|anti-CCP|sed\s*rate|hemoglobin|WBC|platelet|'
        r'creatinine|BUN|ALT|AST|uric\s*acid)\s*[:\s]*(\d+(?:\.\d+)?)\s*(mm/hr|mg/[dL]|g/dL|%)?',
        re.IGNORECASE
    )

    def __init__(self, model_path: str = 'data/models'):
        """
        Initialize GatorTron-Rheum extractor.

        Args:
            model_path: Directory containing cached models (relative to project root)

        Raises:
            ImportError: If transformers/torch not installed
            FileNotFoundError: If model not found in cache
        """
        logger.info(f"Initializing MTLEntityExtractor (Version B V2.1)")
        logger.info(f"Model: {self.MODEL_NAME}")

        # Get project root (2 levels up from this file: backend/services -> backend -> root)
        from pathlib import Path
        project_root = Path(__file__).parent.parent.parent

        # Convert to absolute path if relative path provided
        if not Path(model_path).is_absolute():
            self.model_path = str(project_root / model_path)
        else:
            self.model_path = model_path

        logger.info(f"Model cache path: {self.model_path}")

        self.device = self._setup_device()

        # Load custom-trained model and tokenizer
        self.model, self.tokenizer = self._load_model(self.model_path)

        # Store negation entity spans for post-processing
        self.negation_spans = []

        logger.info(f"MTLEntityExtractor initialized successfully")
        logger.info(f"Device: {self.device}")

    def _setup_device(self) -> torch.device:
        """
        Setup computation device (CPU/GPU).

        Returns:
            torch.device for model inference

        Note:
            Currently optimized for CPU inference.
            GPU support can be added by checking torch.cuda.is_available()
        """
        # For now, use CPU for maximum compatibility
        # GPU can be enabled with: torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        device = torch.device('cpu')
        logger.info(f"Using device: {device}")
        return device

    def _load_model(
        self,
        model_path: str
    ) -> Tuple[AutoModelForTokenClassification, AutoTokenizer]:
        """
        Load custom-trained GatorTron model and tokenizer from cache.

        Args:
            model_path: Base directory for model cache

        Returns:
            Tuple of (model, tokenizer)

        Raises:
            FileNotFoundError: If model not found in cache
            ImportError: If transformers not installed
        """
        cache_path = os.path.join(model_path, self.MODEL_FOLDER)

        try:
            if os.path.exists(cache_path):
                logger.info(f"Loading GatorTron-Rheum from cache: {cache_path}")
                model = AutoModelForTokenClassification.from_pretrained(cache_path)
                tokenizer = AutoTokenizer.from_pretrained(cache_path)
            else:
                # Custom model must be in cache - no HuggingFace download
                raise FileNotFoundError(
                    f"Model not found at: {cache_path}\n"
                    f"Please copy your trained model to: {cache_path}\n"
                    f"Expected files: pytorch_model.bin, config.json, vocab.txt"
                )

        except ImportError as e:
            logger.error(f"transformers library not installed: {e}")
            raise ImportError(
                "transformers library required for Version B. "
                "Install with: pip install transformers torch sentencepiece"
            )

        # Move model to device and set to evaluation mode
        model.to(self.device)
        model.eval()

        logger.info(f"Model loaded: {model.config.num_labels} labels, "
                   f"{sum(p.numel() for p in model.parameters())/1e6:.0f}M parameters")

        # Log label mapping from model config
        if hasattr(model.config, 'id2label'):
            logger.info(f"Model labels: {model.config.id2label}")

        # Apply torch.compile optimization (PyTorch 2.0+)
        if self.USE_TORCH_COMPILE and hasattr(torch, 'compile'):
            try:
                logger.info(f"Applying torch.compile (mode={self.TORCH_COMPILE_MODE})...")
                model = torch.compile(model, mode=self.TORCH_COMPILE_MODE)
                logger.info("torch.compile applied successfully")

                # Warm-up inference to trigger JIT compilation
                logger.info("Running warm-up inference to pre-compile model...")
                self._warmup_model(model, tokenizer)
                logger.info("Warm-up complete")

            except Exception as e:
                logger.warning(f"torch.compile failed, using uncompiled model: {e}")
        else:
            if self.USE_TORCH_COMPILE:
                logger.info("torch.compile not available (requires PyTorch 2.0+)")

        return model, tokenizer

    def _warmup_model(self, model, tokenizer):
        """
        Run warm-up inference to trigger JIT compilation.

        This reduces latency on the first real request by pre-compiling
        the model's computation graph.

        Args:
            model: The model to warm up
            tokenizer: Tokenizer for creating dummy input
        """
        # Create dummy input
        dummy_text = "Patient presents with joint pain."
        inputs = tokenizer(
            dummy_text,
            return_tensors='pt',
            truncation=True,
            max_length=self.MAX_LENGTH,
            padding='max_length'
        )

        # Move to device
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        # Run inference (triggers compilation)
        with torch.no_grad():
            _ = model(**inputs)

    def extract(self, text: str) -> ExtractionResult:
        """
        Extract medical entities from text using GatorTron-Rheum.

        Args:
            text: Medical note text to process

        Returns:
            ExtractionResult with entities, version, processing time, model name

        Example:
            >>> extractor = MTLEntityExtractor()
            >>> text = "Patient with RA on methotrexate 15mg weekly. Denies fever."
            >>> result = extractor.extract(text)
            >>> len(result['entities'])  # Multiple entities extracted
            >>> result['version']  # 'B'
            >>> result['model_name']  # 'gatortron-rheum'
        """
        start_time = time.time()

        try:
            # Step 1: Tokenize and predict with GatorTron
            tokens, labels, scores, offset_mapping = self._tokenize_and_predict(text)

            # Step 2: Convert BIO tags to entity spans (includes NEGATION entities)
            raw_entities = self._bio_to_entities(tokens, labels, scores, offset_mapping, text)

            # Step 3: Separate NEGATION entities from regular entities
            negation_spans = []
            regular_entities = []

            for entity_dict in raw_entities:
                if entity_dict['type'] == 'NEGATION':
                    negation_spans.append((entity_dict['start'], entity_dict['end']))
                else:
                    regular_entities.append(entity_dict)

            # Step 4: Map model labels to application types and check negation
            entities = []
            for entity_dict in regular_entities:
                # Direct label mapping
                mapped_type = self._map_entity_type(entity_dict['type'])

                # Create standardized entity
                entity = self._create_entity(
                    text=entity_dict['text'],
                    entity_type=mapped_type,
                    start=entity_dict['start'],
                    end=entity_dict['end'],
                    confidence=entity_dict['confidence']
                )

                # Check if entity is within scope of any NEGATION span
                is_negated, negation_cue = self._check_negation_with_cue(
                    entity_dict['start'], entity_dict['end'], negation_spans, text
                )
                entity['is_negated'] = is_negated
                if is_negated and negation_cue:
                    entity['negation_cue'] = negation_cue

                entities.append(entity)

            # Step 5: Add LAB_TEST entities via regex fallback
            lab_entities = self._extract_lab_tests(text, entities)
            entities.extend(lab_entities)

            # Calculate processing time
            processing_time_ms = (time.time() - start_time) * 1000

            return {
                'entities': entities,
                'version': self.get_version(),
                'processing_time_ms': processing_time_ms,
                'model_name': self.get_model_name()
            }

        except Exception as e:
            logger.error(f"Error during extraction: {e}")
            # Return empty result on error (graceful degradation)
            processing_time_ms = (time.time() - start_time) * 1000
            return {
                'entities': [],
                'version': self.get_version(),
                'processing_time_ms': processing_time_ms,
                'model_name': self.get_model_name()
            }

    def _tokenize_and_predict(
        self,
        text: str
    ) -> Tuple[List[str], List[str], List[float], List[Tuple[int, int]]]:
        """
        Tokenize text and run GatorTronS inference.

        Args:
            text: Medical note text

        Returns:
            Tuple of (tokens, labels, confidence_scores, offset_mapping)

        Note:
            Uses transformers tokenizer with return_offsets_mapping to
            maintain alignment with original text positions.
        """
        # Tokenize input text
        inputs = self.tokenizer(
            text,
            return_tensors='pt',
            truncation=True,
            max_length=self.MAX_LENGTH,
            padding='max_length',
            return_offsets_mapping=True
        )

        # Extract offset mapping before inference
        offset_mapping = inputs.pop('offset_mapping')[0].tolist()

        # Move inputs to device
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        # Run inference (no gradient computation needed)
        with torch.no_grad():
            outputs = self.model(**inputs)

        # Extract logits and convert to predictions
        logits = outputs.logits[0]  # [seq_len, num_labels]
        predictions = torch.argmax(logits, dim=-1)
        scores = torch.softmax(logits, dim=-1).max(dim=-1).values

        # Convert to labels
        tokens = self.tokenizer.convert_ids_to_tokens(inputs['input_ids'][0])
        labels = [self.model.config.id2label.get(p.item(), 'O') for p in predictions]
        confidence_scores = scores.cpu().tolist()

        return tokens, labels, confidence_scores, offset_mapping

    def _bio_to_entities(
        self,
        tokens: List[str],
        labels: List[str],
        scores: List[float],
        offset_mapping: List[Tuple[int, int]],
        text: str
    ) -> List[Dict]:
        """
        Convert BIO tags to entity spans.

        Args:
            tokens: Tokenized text
            labels: BIO labels (B-PER, I-PER, O, etc.)
            scores: Confidence scores for each token
            offset_mapping: Character positions in original text
            text: Original text

        Returns:
            List of entity dictionaries with text, type, start, end, confidence

        Example BIO sequence:
            tokens: ['Patient', 'has', 'fever']
            labels: ['O', 'O', 'B-SYMPTOM']
            → entity: {'text': 'fever', 'type': 'SYMPTOM', ...}
        """
        entities = []
        current_entity = None

        for idx, (token, label, score, offset) in enumerate(
            zip(tokens, labels, scores, offset_mapping)
        ):
            # Skip special tokens ([CLS], [SEP], [PAD])
            if token in ['[CLS]', '[SEP]', '[PAD]', '<s>', '</s>']:
                continue

            # Skip tokens with zero offset (padding)
            if offset[0] == 0 and offset[1] == 0 and idx > 0:
                continue

            if label == 'O':
                # Not an entity - save current entity if exists
                if current_entity:
                    # Extract full text from original using offsets
                    entity_text = text[current_entity['start']:current_entity['end']]
                    current_entity['text'] = entity_text.strip()

                    # Calculate average confidence
                    if current_entity['scores']:
                        current_entity['confidence'] = sum(current_entity['scores']) / len(current_entity['scores'])
                    else:
                        current_entity['confidence'] = 0.0

                    # Only include if meets confidence threshold
                    if current_entity['confidence'] >= self.CONFIDENCE_THRESHOLD:
                        entities.append(current_entity)

                    current_entity = None

            elif label.startswith('B-'):
                # Beginning of new entity
                if current_entity:
                    # Save previous entity
                    entity_text = text[current_entity['start']:current_entity['end']]
                    current_entity['text'] = entity_text.strip()
                    current_entity['confidence'] = sum(current_entity['scores']) / len(current_entity['scores'])

                    if current_entity['confidence'] >= self.CONFIDENCE_THRESHOLD:
                        entities.append(current_entity)

                # Start new entity
                entity_type = label[2:]  # Remove 'B-' prefix
                current_entity = {
                    'type': entity_type,
                    'start': offset[0],
                    'end': offset[1],
                    'scores': [score],
                    'text': ''  # Will be filled from original text
                }

            elif label.startswith('I-') and current_entity:
                # Inside existing entity - extend it
                current_entity['end'] = offset[1]
                current_entity['scores'].append(score)

        # Don't forget last entity
        if current_entity:
            entity_text = text[current_entity['start']:current_entity['end']]
            current_entity['text'] = entity_text.strip()
            current_entity['confidence'] = sum(current_entity['scores']) / len(current_entity['scores'])

            if current_entity['confidence'] >= self.CONFIDENCE_THRESHOLD:
                entities.append(current_entity)

        return entities

    def _map_entity_type(self, model_label: str) -> str:
        """
        Map model NER labels to application entity types.

        Uses direct mapping from LABEL_MAP since model is trained
        on the correct entity types.

        Args:
            model_label: Model entity type (DRUG, SYMPTOM, DOSAGE, etc.)

        Returns:
            Application entity type (MEDICATION, SYMPTOM, DISEASE, etc.)

        Example:
            >>> self._map_entity_type('DRUG')
            'MEDICATION'
            >>> self._map_entity_type('CONDITION')
            'DISEASE'
        """
        return self.LABEL_MAP.get(model_label, 'ENTITY')

    def _check_negation_from_spans(
        self,
        entity_start: int,
        entity_end: int,
        negation_spans: List[Tuple[int, int]]
    ) -> bool:
        """
        Check if entity is within scope of any NEGATION span from model.

        An entity is considered negated if:
        - A NEGATION span exists within NEGATION_SCOPE characters before it
        - A NEGATION span exists within NEGATION_SCOPE characters after it

        Args:
            entity_start: Starting position of entity
            entity_end: Ending position of entity
            negation_spans: List of (start, end) tuples for NEGATION entities

        Returns:
            True if entity is negated, False otherwise

        Example:
            >>> # "Patient denies fever" where "denies" is NEGATION
            >>> self._check_negation_from_spans(16, 21, [(8, 14)])
            True
        """
        for neg_start, neg_end in negation_spans:
            # Check if negation is before entity (within scope)
            if neg_end <= entity_start and (entity_start - neg_end) <= self.NEGATION_SCOPE:
                return True

            # Check if negation is after entity (within scope)
            if neg_start >= entity_end and (neg_start - entity_end) <= self.NEGATION_SCOPE:
                return True

        return False

    def _check_negation_with_cue(
        self,
        entity_start: int,
        entity_end: int,
        negation_spans: List[Tuple[int, int]],
        text: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Check if entity is negated and return the negation cue text.

        Args:
            entity_start: Starting position of entity
            entity_end: Ending position of entity
            negation_spans: List of (start, end) tuples for NEGATION entities
            text: Original text to extract cue from

        Returns:
            Tuple of (is_negated, negation_cue_text)
        """
        for neg_start, neg_end in negation_spans:
            # Check if negation is before entity (within scope)
            if neg_end <= entity_start and (entity_start - neg_end) <= self.NEGATION_SCOPE:
                cue_text = text[neg_start:neg_end].strip()
                return True, cue_text

            # Check if negation is after entity (within scope)
            if neg_start >= entity_end and (neg_start - entity_end) <= self.NEGATION_SCOPE:
                cue_text = text[neg_start:neg_end].strip()
                return True, cue_text

        return False, None

    def _extract_lab_tests(
        self,
        text: str,
        existing_entities: List[Dict]
    ) -> List[Dict]:
        """
        Extract LAB_TEST entities using regex fallback.

        Model doesn't include LAB_TEST in training data, so we use
        regex patterns to detect common lab tests (ESR, CRP, ANA, etc.).

        Args:
            text: Full medical note text
            existing_entities: Entities already extracted by model

        Returns:
            List of LAB_TEST entity dictionaries

        Example:
            >>> text = "Labs show ESR 45 and CRP 12"
            >>> self._extract_lab_tests(text, [])
            [{'text': 'ESR 45', 'type': 'LAB_TEST', ...}, ...]
        """
        lab_entities = []
        existing_spans = set()

        # Build set of existing entity spans to avoid duplicates
        for entity in existing_entities:
            for pos in range(entity['start'], entity['end']):
                existing_spans.add(pos)

        # Find lab values with numbers (e.g., "ESR 45", "CRP: 12")
        for match in self.LAB_VALUE_PATTERN.finditer(text):
            start, end = match.start(), match.end()

            # Skip if overlaps with existing entity
            if any(pos in existing_spans for pos in range(start, end)):
                continue

            entity = self._create_entity(
                text=match.group(0).strip(),
                entity_type='LAB_TEST',
                start=start,
                end=end,
                confidence=0.9  # High confidence for regex match
            )
            entity['is_negated'] = False
            lab_entities.append(entity)

            # Add to existing spans
            for pos in range(start, end):
                existing_spans.add(pos)

        # Also find standalone lab test names (without values)
        for match in self.LAB_TEST_PATTERN.finditer(text):
            start, end = match.start(), match.end()

            # Skip if overlaps with existing entity or lab value
            if any(pos in existing_spans for pos in range(start, end)):
                continue

            entity = self._create_entity(
                text=match.group(0).strip(),
                entity_type='LAB_TEST',
                start=start,
                end=end,
                confidence=0.85  # Slightly lower for name-only
            )
            entity['is_negated'] = False
            lab_entities.append(entity)

        return lab_entities

    def get_version(self) -> str:
        """Return version identifier: 'B'"""
        return 'B'

    def get_model_name(self) -> str:
        """Return model name: 'gatortron-rheum'"""
        return 'gatortron-rheum'
