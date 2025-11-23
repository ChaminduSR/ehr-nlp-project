import spacy
import scispacy

print("="*80)
print("SCISPACY: BIOMEDICAL TEXT PROCESSING")
print("="*80)

print("\n\nPart 1: Environment Info")
print("-"*80)
print(f"Python Environment: Conda")
print(f"spaCy version: {spacy.__version__}")
print(f"scispaCy version: {scispacy.__version__}")

print("\n\nPart 2: Available scispaCy Models")
print("-"*80)

available_models = {
    "en_core_sci_sm": "Small biomedical model (12MB)",
    "en_core_sci_md": "Medium biomedical model (360MB)",
    "en_core_sci_lg": "Large biomedical model (361MB)",
}

for model_name, description in available_models.items():
    print(f"  {model_name:<20} - {description}")

print("\n\nPart 3: Download and Load Biomedical Model")
print("-"*80)

print("\nTo download the small model, run:")
print("  pip install https://s3-us-west-2.amazonaws.com/ai2-s2-scispacy/releases/v0.5.4/en_core_sci_sm-0.5.4.tar.gz")

try:
    print("\nAttempting to load biomedical model...")
    biomedical_nlp = spacy.load("en_core_sci_sm")
    print("✓ Biomedical model loaded successfully!")
    model_loaded = True
except OSError:
    print("✗ Biomedical model not found. Using general model as fallback.")
    biomedical_nlp = spacy.load("en_core_web_md")
    model_loaded = False

print("\n\nPart 4: Compare Models on Clinical Text")
print("-"*80)

clinical_text = "Patient with diabetes mellitus and hypertension presents with dyspnea and chest pain."

print(f"\nClinical text: {clinical_text}\n")

doc = biomedical_nlp(clinical_text)

if doc.ents:
    print("Entities found:")
    for ent in doc.ents:
        print(f"  {ent.text:<30} → {ent.label_}")
else:
    print("  No entities found")

print("\n\nPart 5: Process Clinical Abbreviations")
print("-"*80)

clinical_notes = [
    "HTN and DM2 noted on exam.",
    "Patient has CAD with recent MI.",
    "Presenting with SOB and chest discomfort.",
    "No evidence of CHF or arrhythmia.",
    "Labs show elevated HbA1c and BNP.",
]

print("\nProcessing clinical abbreviations:\n")

for note_num, note in enumerate(clinical_notes, 1):
    doc = biomedical_nlp(note)
    
    print(f"Note {note_num}: {note}")
    
    if doc.ents:
        print("  Entities:")
        for ent in doc.ents:
            print(f"    - {ent.text} ({ent.label_})")
    else:
        print("  No entities found")
    print()

print("="*80)
print("KEY ADVANTAGES OF SCISPACY:")
print("="*80)

advantages = """
1. BIOMEDICAL TRAINING DATA
   - Trained on PubMed (biomedical research articles)
   - Understands medical terminology
   - Better entity recognition for medical text

2. SPECIALIZED ENTITY TYPES
   - Recognizes: diseases, chemicals, genes, anatomy
   - Better with medical abbreviations (HTN, DM, CAD, MI)
   - Clinical context understanding

3. UMLS LINKING (Days 9-10)
   - Links entities to standardized medical concepts
   - Connects to medical knowledge bases
   - Normalizes terminology across different formats

4. ABBREVIATION DETECTION (Day 8)
   - Automatically detect medical abbreviations
   - Resolve abbreviations in context
   - Find what HTN, DM, CAD really mean

5. PRODUCTION READY
   - Industry standard for healthcare NLP
   - Used in real EHR systems
   - Well-maintained and documented
"""

print(advantages)

if not model_loaded:
    print("\n" + "="*80)
    print("NEXT STEP: Download biomedical model")
    print("="*80)
    print("\nRun this command to download the biomedical model:")
    print("  pip install https://s3-us-west-2.amazonaws.com/ai2-s2-scispacy/releases/v0.5.4/en_core_sci_sm-0.5.4.tar.gz")
    print("\nThen re-run this script to see the difference!")
